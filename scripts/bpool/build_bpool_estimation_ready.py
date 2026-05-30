"""
Build B-pool estimation-ready parquets from the d1w1 draws files + priced long files.

Layout (already collapsed in d1w1):
  singles : one row per (stacked_hh_uid, draw)        — 101 alts/HH (100 draws + chosen)
  couples : one row per (stacked_hh_uid, draw_joint, is_chosen_joint) — 901 alts/HH
            (900 simulated Cartesian cells + 1 chosen; draw_joint=0 collides with the
             chosen row, disambiguated by is_chosen_joint)

The d1w1 file already carries every demographic / opportunity covariate and the
male/female suffixing. The ONLY things we add here:
  1. ils_dispy_real  — joined from the per-year priced long files:
       singles : decider-row value, keyed (uid, draw, data_year)
       couples : JOINT household disposable income = sum of per-person ils_dispy_real
                 over the tax unit, keyed (uid, draw_joint, is_chosen_joint, data_year)
  2. wage columns      — nominal values retained as *_nominal; estimator-facing
                         wage / wage_male / wage_female converted to 2016-real
  3. reg2..reg8        = reg_nuts1_2..reg_nuts1_8 (reg_nuts1_1 is the omitted base)
  4. loc4 one-hots     loc4_2/3/4 (singles) ; loc4_{2,3,4}_{male,female} (couples)

Read-only on all sources. Writes:
  fr_p3a_bpool_estimation_ready__singles.parquet
  fr_p3a_bpool_estimation_ready__couples.parquet
  fr_p3a_bpool_estimation_ready__meta.json   (sidecar)

NO estimation. Reports PASS/FAIL on hard gate + 5 checks.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from _bpool_paths import bpool_dir, FR_PARQUETS  # noqa: E402

_BP = bpool_dir()

# Age-banded child counts, computed per parent from the EUROMOD input microdata via
# idmother/idfather. Bands are LEFT-INCLUSIVE [a, b). "total" has NO age restriction
# (sum of all bands incl. adult offspring still in the household) and equals the count
# of all in-household persons linking to that parent.
_CHILD_BANDS = {
    "n_children_0_3":   (0, 3),
    "n_children_3_6":   (3, 6),
    "n_children_6_9":   (6, 9),
    "n_children_9_12":  (9, 12),
    "n_children_12_18": (12, 18),
    "n_children_18plus": (18, 10_000),
}
_SPEC = Path(__file__).resolve().parent / "specs" / "estimation_spec_bpool_p3a_v1.yaml"
_YEARS = (2015, 2016, 2017)
_CPI = {2015: 1.0031, 2016: 1.0000, 2017: 0.9886}
_WAGE_COLUMNS = ("wage", "wage_male", "wage_female")
_OUT_S = _BP / "fr_p3a_bpool_estimation_ready__singles.parquet"
_OUT_C = _BP / "fr_p3a_bpool_estimation_ready__couples.parquet"
_META  = _BP / "fr_p3a_bpool_estimation_ready__meta.json"

# Optional couples-grid variant suffix (e.g. "_20x20"). When set, the couples
# input d1w1 file and the couples output file carry this suffix, so a coarse-grid
# variant build does NOT overwrite the production 901-alt files. Singles are
# unaffected (always 101 alts). Set via --couples-suffix.
_COUPLES_SUFFIX = ""


# ---------------------------------------------------------------------------
# Spec variable extraction (for the hard gate)
# ---------------------------------------------------------------------------
def spec_required_variables() -> list[str]:
    """Every input variable referenced anywhere in the spec's blocks."""
    spec = yaml.safe_load(_SPEC.read_text())
    vars_: set[str] = set()

    def add_shifters(block):
        for sh in block.get("shifters", []):
            v = sh.get("variable")
            if v and v != "intercept":
                vars_.add(v)
            for iv in sh.get("interaction", []) or []:
                vars_.add(iv)

    # consumption — uses ils_dispy_real (the "consumption" variable in estimation)
    vars_.add("ils_dispy_real")
    # leisure block
    add_shifters(spec.get("utility", {}).get("leisure", {}))
    # hours / wage / market / occupation
    add_shifters(spec.get("hours_opportunity", {}))
    for sh in spec.get("wage_opportunity", {}).get("mean_shifters", []):
        v = sh.get("variable")
        if v and v != "intercept":
            vars_.add(v)
    mkt = spec.get("market_opportunity", {})
    if mkt.get("gsur_variable"):
        vars_.add(mkt["gsur_variable"])
    add_shifters(mkt)
    occ = spec.get("occupation_opportunity", {})
    if occ.get("variable"):
        vars_.add(occ["variable"])  # loc4 base
    add_shifters(occ)
    # employment indicator
    if mkt.get("employment_indicator"):
        vars_.add(mkt["employment_indicator"])
    return sorted(vars_)


def gate_columns(mode: str, required: list[str]) -> dict:
    """
    For each spec variable, decide which concrete column(s) must exist in `mode`.
    Returns {spec_var: [concrete cols]} expansion map for the coverage check.
    """
    # Variables that are person-specific become _male/_female on couples.
    person_specific = {
        "age_norm", "age_norm2", "educL", "educH",
        "pexp_years", "pexp_years2", "working", "working_pt1", "working_pt2",
        "working_ft", "working_lh", "loc4", "loc4_2", "loc4_3", "loc4_4", "gsur",
    }
    # Variables that are household-shared (same on both partners / single row).
    # n_children stays UNSUFFIXED on couples: the engine reads a plain `n_children`
    # column (estimation_utils.py:679,1017) and applies the beta_l_nkids shifter
    # female-only internally (estimation_engine.py via data.is_male). Confirmed against
    # estimation_spec_parser.py — males skip the n_children parameter, not the column.
    household = {
        "ils_dispy_real", "reg2", "reg3", "reg4", "reg5", "reg6", "reg7", "reg8",
        "year_2015_indicator", "year_2017_indicator", "n_children",
    }
    out: dict[str, list[str]] = {}
    for v in required:
        if mode == "couples" and v in person_specific:
            out[v] = [f"{v}_male", f"{v}_female"]
        elif v in household or mode == "singles":
            out[v] = [v]
        else:
            out[v] = [v]
    return out


# ---------------------------------------------------------------------------
# Age-banded per-parent child counts (from microdata)
# ---------------------------------------------------------------------------
def per_parent_child_bands(year: int) -> pd.DataFrame:
    """
    Compute, per parent idperson, the count of in-household children in each age band
    (left-inclusive) plus n_children_total (no age restriction). A 'child' is any HH
    member that links to the parent via idfather/idmother — any age.
    Returns DataFrame indexed by idperson with columns = bands + n_children_total.
    """
    df = pd.read_parquet(FR_PARQUETS[year],
                         columns=["idperson", "idmother", "idfather", "dag"])
    dag = pd.to_numeric(df["dag"], errors="coerce")
    # everyone who has a parent link in-HH (any age) is a 'child' of that parent
    base = df[["idmother", "idfather"]].copy()
    base["dag"] = dag
    # band membership flags
    for col, (lo, hi) in _CHILD_BANDS.items():
        base[col] = ((dag >= lo) & (dag < hi)).astype("int64")
    # father links
    f = base.loc[(base["idfather"].notna()) & (base["idfather"] != 0),
                 ["idfather"] + list(_CHILD_BANDS)].rename(columns={"idfather": "parent_id"})
    # mother links
    m = base.loc[(base["idmother"].notna()) & (base["idmother"] != 0),
                 ["idmother"] + list(_CHILD_BANDS)].rename(columns={"idmother": "parent_id"})
    counts = (pd.concat([f, m], ignore_index=True)
              .groupby("parent_id")[list(_CHILD_BANDS)].sum())
    counts["n_children_total"] = counts[list(_CHILD_BANDS)].sum(axis=1)
    counts.index.name = "idperson"
    return counts


def _hh_partner_ids(mode: str, year: int) -> pd.DataFrame:
    """
    Bridge stacked_hh_uid -> decider idperson_true, with dgn, from the priced long file.
    Singles: one decider per HH. Couples: male (dgn=1) and female (dgn=0) deciders.
    """
    pr = pd.read_parquet(
        _BP / f"fr_p3a_bpool_priced__{year}__{mode}.parquet",
        columns=["stacked_hh_uid", "dgn", "idperson_true", "ruro_decider"],
    )
    dec = pr[pr["ruro_decider"] == 1][["stacked_hh_uid", "dgn", "idperson_true"]]
    return dec.drop_duplicates()


def child_band_columns(mode: str) -> pd.DataFrame:
    """
    Build the per-HH (stacked_hh_uid, data_year) -> child-band columns table.
    Singles: unsuffixed bands for the single decider.
    Couples: _male / _female suffixed bands for each partner.
    """
    band_cols = list(_CHILD_BANDS) + ["n_children_total"]
    parts = []
    for y in _YEARS:
        counts = per_parent_child_bands(y)             # idperson -> bands
        bridge = _hh_partner_ids(mode, y)              # uid, dgn, idperson_true
        bridge = bridge.merge(counts, left_on="idperson_true", right_index=True, how="left")
        bridge[band_cols] = bridge[band_cols].fillna(0).astype("int64")
        bridge["data_year"] = y

        if mode == "singles":
            out = bridge[["stacked_hh_uid", "data_year"] + band_cols].drop_duplicates("stacked_hh_uid")
        else:
            # pivot male (dgn=1) / female (dgn=0) into suffixed columns
            mal = bridge[bridge["dgn"] == 1][["stacked_hh_uid"] + band_cols].rename(
                columns={c: f"{c}_male" for c in band_cols})
            fem = bridge[bridge["dgn"] == 0][["stacked_hh_uid"] + band_cols].rename(
                columns={c: f"{c}_female" for c in band_cols})
            out = mal.merge(fem, on="stacked_hh_uid", how="outer")
            out["data_year"] = y
        parts.append(out)
    res = pd.concat(parts, ignore_index=True)
    # fill any partner with no parent link as 0
    fillcols = [c for c in res.columns if c.startswith("n_children")]
    res[fillcols] = res[fillcols].fillna(0).astype("int64")
    return res


# ---------------------------------------------------------------------------
# ils_dispy_real lookups
# ---------------------------------------------------------------------------
def singles_dispy_lookup() -> pd.DataFrame:
    parts = []
    for y in _YEARS:
        pr = pd.read_parquet(
            _BP / f"fr_p3a_bpool_priced__{y}__singles.parquet",
            columns=["stacked_hh_uid", "draw", "ruro_decider", "ils_dispy_real", "data_year"],
        )
        dec = pr[pr["ruro_decider"] == 1][["stacked_hh_uid", "draw", "data_year", "ils_dispy_real"]]
        parts.append(dec)
    return pd.concat(parts, ignore_index=True)


def couples_dispy_lookup() -> pd.DataFrame:
    parts = []
    for y in _YEARS:
        pr = pd.read_parquet(
            _BP / f"fr_p3a_bpool_priced__{y}__couples.parquet",
            columns=["stacked_hh_uid", "draw_joint", "is_chosen_joint", "ils_dispy_real", "data_year"],
        )
        # JOINT household disposable income = sum of per-person ils_dispy_real
        joint = pr.groupby(
            ["stacked_hh_uid", "draw_joint", "is_chosen_joint", "data_year"], as_index=False
        )["ils_dispy_real"].sum()
        parts.append(joint)
    return pd.concat(parts, ignore_index=True)


# ---------------------------------------------------------------------------
# Urbanisation lookup (household-level; carried from priced files — d1w1 dropped it)
# ---------------------------------------------------------------------------
def urbanisation_lookup(mode: str) -> pd.DataFrame:
    """
    (stacked_hh_uid, data_year) -> drgur/drgmd/drgru, from the priced long files.
    Household-constant (verified at source); take one row per (uid, data_year).
    drgur=urban (db100==1), drgmd=middle (db100==2), drgru=rural (db100==3);
    mutually exclusive, sum to 1. Rural is the reference category in the spec.
    """
    parts = []
    for y in _YEARS:
        pr = pd.read_parquet(
            _BP / f"fr_p3a_bpool_priced__{y}__{mode}.parquet",
            columns=["stacked_hh_uid", "drgur", "drgmd", "drgru"],
        )
        pr = pr.drop_duplicates("stacked_hh_uid")
        pr["data_year"] = y
        parts.append(pr)
    return pd.concat(parts, ignore_index=True)


# ---------------------------------------------------------------------------
# Derivations
# ---------------------------------------------------------------------------
def add_region_dummies(df: pd.DataFrame) -> pd.DataFrame:
    # reg2..reg8 from reg_nuts1_2..reg_nuts1_8 (reg_nuts1_1 = omitted base)
    for k in range(2, 9):
        src = f"reg_nuts1_{k}"
        if src in df.columns:
            df[f"reg{k}"] = df[src].astype(float)
    return df


def add_loc4_onehots(df: pd.DataFrame, mode: str) -> pd.DataFrame:
    # Reference category is loc4==1 (spec occupation_opportunity.reference: 1).
    # Singles: loc4_2/3/4.  Couples: loc4_{2,3,4}_{male,female} (variable + partner suffix,
    # matching the spec's per-partner expansion of loc4_2/loc4_3/loc4_4).
    if mode == "singles":
        v = pd.to_numeric(df["loc4"], errors="coerce")
        for k in (2, 3, 4):
            df[f"loc4_{k}"] = (v == k).astype(float)
    else:
        for partner in ("male", "female"):
            v = pd.to_numeric(df[f"loc4_{partner}"], errors="coerce")
            for k in (2, 3, 4):
                df[f"loc4_{k}_{partner}"] = (v == k).astype(float)
    return df


def deflate_wages_for_estimation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep EUROMOD earnings inputs nominal upstream, but expose estimator-facing wages
    in 2016-real euros. This is deliberately applied after pricing inputs are no
    longer used to construct yivwg/yem, preventing double deflation of ils_dispy_real.
    """
    phi = df["data_year"].map(_CPI)
    if phi.isna().any():
        bad_years = sorted(df.loc[phi.isna(), "data_year"].dropna().unique().tolist())
        raise ValueError(f"Missing CPI phi for data_year values: {bad_years}")

    for col in _WAGE_COLUMNS:
        if col not in df.columns:
            continue
        nominal_col = f"{col}_nominal"
        if nominal_col not in df.columns:
            df[nominal_col] = df[col]
        nominal = pd.to_numeric(df[nominal_col], errors="coerce")
        df[col] = nominal * phi
    return df


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
# Stale disposable-income columns carried on the d1w1 base. These predate the fresh
# EUROMOD pricing run; the priced long files are authoritative, so we DROP these and
# replace ils_dispy_real (and consumption) from the priced join.
_STALE_DISPY = ["ils_dispy_real", "consumption", "ils_dispy", "ils_dispy_em",
                "ils_dispy_male", "ils_dispy_female", "consumption_male", "consumption_female"]


def build_singles() -> pd.DataFrame:
    df = pd.read_parquet(_BP / "fr_p3a_bpool_d1w1__singles.parquet")
    df = deflate_wages_for_estimation(df)
    df = df.drop(columns=[c for c in _STALE_DISPY if c in df.columns])
    look = singles_dispy_lookup()
    df = df.merge(look, on=["stacked_hh_uid", "draw", "data_year"], how="left")
    df["consumption"] = df["ils_dispy_real"]   # estimation consumption = priced real disp income
    df = add_region_dummies(df)
    df = add_loc4_onehots(df, "singles")
    # Urbanisation (household access increment, D5): drgur/drgmd/drgru, rural=reference
    urb = urbanisation_lookup("singles")
    df = df.merge(urb, on=["stacked_hh_uid", "data_year"], how="left")
    # New age-banded per-parent child counts (additive; existing n_children kept as-is)
    bands = child_band_columns("singles")
    df = df.merge(bands, on=["stacked_hh_uid", "data_year"], how="left")
    bcols = [c for c in df.columns if c.startswith("n_children_")]
    df[bcols] = df[bcols].fillna(0)
    if "idorighh" in df.columns:
        df["cluster_id"] = df["idorighh"]
    return df


def build_couples() -> pd.DataFrame:
    in_path = _BP / f"fr_p3a_bpool_d1w1{_COUPLES_SUFFIX}__couples.parquet"
    print(f"  [build_couples] reading {in_path.name}")
    df = pd.read_parquet(in_path)
    df = deflate_wages_for_estimation(df)
    df = df.drop(columns=[c for c in _STALE_DISPY if c in df.columns])
    look = couples_dispy_lookup()
    df = df.merge(
        look, on=["stacked_hh_uid", "draw_joint", "is_chosen_joint", "data_year"], how="left"
    )
    df["consumption"] = df["ils_dispy_real"]   # joint household real disposable income
    df = add_region_dummies(df)
    df = add_loc4_onehots(df, "couples")
    # Urbanisation (household access increment, D5): drgur/drgmd/drgru, rural=reference
    urb = urbanisation_lookup("couples")
    df = df.merge(urb, on=["stacked_hh_uid", "data_year"], how="left")
    # New age-banded per-parent child counts, suffixed _male/_female (additive)
    bands = child_band_columns("couples")
    df = df.merge(bands, on=["stacked_hh_uid", "data_year"], how="left")
    bcols = [c for c in df.columns if c.startswith("n_children_")]
    df[bcols] = df[bcols].fillna(0)
    if "idorighh" in df.columns:
        df["cluster_id"] = df["idorighh"]
    return df


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
def run_checks(df: pd.DataFrame, mode: str) -> dict:
    r = {}
    chosen_flag = "is_chosen" if mode == "singles" else "is_chosen_joint"
    draw_col = "draw" if mode == "singles" else "draw_joint"
    n_hh = df["stacked_hh_uid"].nunique()

    # CHECK 1: consumption non-null on ALL alternatives (incl. non-working)
    n_null = int(df["ils_dispy_real"].isna().sum())
    r["check1_consumption_nonnull"] = {"n_null": n_null, "n_total": len(df), "pass": n_null == 0}

    # CHECK 2: row counts
    # Singles are fixed at 101. Couples depend on the product grid: 30x30 -> 901,
    # 20x20 -> 401. Infer the expected per-HH count from the modal row count so
    # the check is grid-agnostic, then verify every HH matches it.
    per_hh = df.groupby("stacked_hh_uid").size()
    if mode == "singles":
        expected = 101
    else:
        expected = int(per_hh.mode().iloc[0])  # modal alts/HH (e.g. 401 or 901)
    ok_counts = bool((per_hh == expected).all())
    r["check2_row_counts"] = {
        "n_hh": int(n_hh), "expected_per_hh": expected,
        "n_rows": len(df), "expected_rows": int(n_hh * expected),
        "all_hh_have_expected": ok_counts, "pass": ok_counts and len(df) == n_hh * expected,
    }

    # CHECK 3: chosen row present exactly once per HH
    chosen_sum = int(df[chosen_flag].sum())
    chosen_per_hh = df.groupby("stacked_hh_uid")[chosen_flag].sum()
    r["check3_chosen_once"] = {
        "chosen_sum": chosen_sum, "n_hh": int(n_hh),
        "all_hh_exactly_one": bool((chosen_per_hh == 1).all()),
        "pass": chosen_sum == n_hh and bool((chosen_per_hh == 1).all()),
    }

    # CHECK 4: dgn partition complete + non-overlapping; idpartner pairs resolve
    if mode == "singles":
        # singles: each HH has one decider; dgn in {0,1}; no partner
        dgn_vals = set(pd.to_numeric(df["dgn"], errors="coerce").dropna().unique().tolist())
        r["check4_dgn_partition"] = {
            "dgn_values": sorted(dgn_vals),
            "note": "singles — single decider per HH, no idpartner pairing required",
            "pass": dgn_vals.issubset({0.0, 1.0}),
        }
    else:
        # couples: male=dgn1, female=dgn0 carried as suffixed cols already.
        # Verify the suffixed working/hours/wage columns are both present (partition complete).
        need = ["working_male", "working_female", "hours_male", "hours_female",
                "wage_male", "wage_female", "loc4_male", "loc4_female"]
        present = {c: (c in df.columns) for c in need}
        r["check4_dgn_partition"] = {
            "suffixed_cols_present": present,
            "note": "couples — male/female already on one wide row via dgn suffixing in d1w1",
            "pass": all(present.values()),
        }

    # CHECK 5: log_prior identity post-collapse
    if mode == "singles":
        recon = df["log_q_E"] + df["working"] * (df["log_q_Occ"] + df["log_q_H"] + df["log_q_W"])
        d = (df["log_prior"] - recon).abs()
        r["check5_log_prior_identity"] = {
            "max_abs_diff": float(d.max()), "n_violations": int((d > 1e-6).sum()),
            "formula": "log_q_E + working*(log_q_Occ+log_q_H+log_q_W)",
            "pass": float(d.max()) <= 1e-6,
        }
    else:
        recon = df["log_prior_male"] + df["log_prior_female"]
        d = (df["log_prior"] - recon).abs()
        r["check5_log_prior_identity"] = {
            "max_abs_diff": float(d.max()), "n_violations": int((d > 1e-6).sum()),
            "formula": "log_prior_male + log_prior_female",
            "pass": float(d.max()) <= 1e-6,
        }

    # CHECK 6: child-band totals = sum of age bands (per parent / per partner)
    bands = list(_CHILD_BANDS)
    check6 = {}
    ok6 = True
    suffixes = [""] if mode == "singles" else ["_male", "_female"]
    for suf in suffixes:
        tcol = f"n_children_total{suf}"
        bcols = [f"{b}{suf}" for b in bands]
        if tcol in df.columns and all(b in df.columns for b in bcols):
            recon = df[bcols].sum(axis=1)
            d = (df[tcol] - recon).abs()
            viol = int((d > 0).sum())
            check6[tcol] = {"max_abs_diff": int(d.max()), "n_violations": viol,
                            "total_mean": round(float(df[tcol].mean()), 4)}
            if viol > 0:
                ok6 = False
        else:
            check6[tcol] = {"note": "columns absent"}
            ok6 = False
    check6["pass"] = ok6
    r["check6_child_band_total_identity"] = check6

    # CHECK 7: wage columns consumed by estimation are 2016-real; nominal copies retained.
    phi = df["data_year"].map(_CPI)
    check7 = {}
    for col in _WAGE_COLUMNS:
        if col not in df.columns:
            continue
        nominal_col = f"{col}_nominal"
        if nominal_col not in df.columns:
            check7[col] = {"pass": False, "missing_nominal_col": nominal_col}
            continue
        real = pd.to_numeric(df[col], errors="coerce")
        nominal = pd.to_numeric(df[nominal_col], errors="coerce")
        mask = real.notna() & nominal.notna()
        max_abs = float((real[mask] - nominal[mask] * phi[mask]).abs().max()) if mask.any() else 0.0
        check7[col] = {
            "nominal_col": nominal_col,
            "max_abs_diff": max_abs,
            "pass": max_abs <= 1e-9,
        }
    check7["pass"] = bool(check7) and all(v.get("pass") for k, v in check7.items() if k != "pass")
    r["check7_wage_2016_real"] = check7

    # CHECK 8: idorighh is the clustered-SE key, not stacked_hh_uid/restacked idhh.
    has_idorighh = "idorighh" in df.columns
    n_nonnull = int(df["idorighh"].notna().sum()) if has_idorighh else 0
    cluster_equal = bool((df["cluster_id"] == df["idorighh"]).all()) if has_idorighh and "cluster_id" in df.columns else False
    r["check8_idorighh_cluster_key"] = {
        "present": has_idorighh,
        "nonnull": n_nonnull,
        "n_rows": int(len(df)),
        "cluster_id_eq_idorighh": cluster_equal,
        "pass": has_idorighh and n_nonnull == len(df) and cluster_equal,
    }
    return r


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    import argparse
    global _COUPLES_SUFFIX, _OUT_C, _META
    ap = argparse.ArgumentParser(description="Build B-pool estimation-ready parquets.")
    ap.add_argument("--couples-suffix", default="",
                    help="Suffix for the couples d1w1 INPUT and estimation-ready OUTPUT "
                         "(e.g. '_20x20'). Keeps coarse-grid variants from overwriting the "
                         "production 901-alt files. Singles unaffected (always 101 alts). "
                         "When set, ONLY the couples file is rebuilt.")
    args = ap.parse_args()
    _COUPLES_SUFFIX = args.couples_suffix
    if _COUPLES_SUFFIX:
        _OUT_C = _BP / f"fr_p3a_bpool_estimation_ready{_COUPLES_SUFFIX}__couples.parquet"
        _META = _BP / f"fr_p3a_bpool_estimation_ready{_COUPLES_SUFFIX}__meta.json"
        print(f"[couples-variant] suffix={_COUPLES_SUFFIX!r}; "
              f"couples-only rebuild -> {_OUT_C.name}")

    required = spec_required_variables()
    print(f"Spec references {len(required)} input variables:")
    print("  " + ", ".join(required))

    summary = {
        "spec_required_variables": required,
        "wage_price_basis": {
            "estimator_columns": list(_WAGE_COLUMNS),
            "nominal_copies": [f"{c}_nominal" for c in _WAGE_COLUMNS],
            "cpi_phi": _CPI,
            "convention": "wage/wage_male/wage_female are 2016-real; *_nominal keeps the original drawn nominal wage",
        },
        "cluster_key": {"cluster_id_col": "cluster_id", "source_col": "idorighh"},
        "files": {},
    }
    hard_gate_ok = True
    all_checks_ok = True

    build_targets = [("singles", build_singles, _OUT_S),
                     ("couples", build_couples, _OUT_C)]
    if _COUPLES_SUFFIX:
        # Couples-only variant rebuild: singles are grid-independent (101 alts).
        build_targets = [t for t in build_targets if t[0] == "couples"]
    for mode, builder, out in build_targets:
        print(f"\n{'='*70}\nBUILD {mode}\n{'='*70}")
        df = builder()
        print(f"  shape: {df.shape}")

        # ---- HARD GATE: spec coverage ----
        expand = gate_columns(mode, required)
        missing = []
        coverage = {}
        for spec_var, concrete in expand.items():
            present = [c for c in concrete if c in df.columns]
            absent = [c for c in concrete if c not in df.columns]
            coverage[spec_var] = {"expected": concrete, "present": present, "missing": absent}
            missing.extend(absent)
        if missing:
            hard_gate_ok = False
            print(f"  HARD GATE FAIL — missing columns: {missing}")
        else:
            print(f"  HARD GATE PASS — all {len(expand)} spec variables covered.")

        # ---- CHECKS ----
        checks = run_checks(df, mode)
        for k, v in checks.items():
            status = "PASS" if v["pass"] else "FAIL"
            if not v["pass"]:
                all_checks_ok = False
            print(f"  {status} {k}: { {kk:vv for kk,vv in v.items() if kk!='pass'} }")

        # ---- WRITE (only if hard gate passes for this file) ----
        if not missing:
            df.to_parquet(out, index=False)
            print(f"  Written: {out}  shape={df.shape}")
        else:
            print(f"  NOT WRITTEN (hard gate failed).")

        summary["files"][mode] = {
            "n_rows": int(len(df)),
            "n_hh": int(df["stacked_hh_uid"].nunique()),
            "n_cols": int(df.shape[1]),
            "hard_gate_pass": not missing,
            "spec_coverage": coverage,
            "checks": checks,
            "output_path": str(out) if not missing else None,
        }

    summary["hard_gate_all_pass"] = hard_gate_ok
    summary["all_checks_pass"] = all_checks_ok
    summary["overall_pass"] = hard_gate_ok and all_checks_ok
    with open(_META, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nSidecar written: {_META}")
    print(f"\n{'='*70}")
    print(f"HARD GATE: {'PASS' if hard_gate_ok else 'FAIL'}")
    print(f"CHECKS:    {'PASS' if all_checks_ok else 'FAIL'}")
    print(f"OVERALL:   {'PASS' if summary['overall_pass'] else 'FAIL'}")
    print(f"{'='*70}")
    if not summary["overall_pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
