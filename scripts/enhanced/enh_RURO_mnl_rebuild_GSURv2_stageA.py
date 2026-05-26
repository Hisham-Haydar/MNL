"""
Stage A MNL rebuild: merge GSURv2 Stage A broad-age lookup into versioned parquets.

Authorised by: docs/RURO_GSUR_O7_crosswalk_signoff_v1.md
Spec: docs/France_case/_shared/gsur/RURO_GSUR_rebuild_specification_v2_1.md §8, §14
Prompt: Prompts/RURO_GSUR_v2_stageA_MNL_rebuild_prompt_corrected_v2.md

Writes ONLY to versioned GSURv2 paths. Canonical paths are read-only.
"""

import sys
import pathlib
import datetime

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# ---------------------------------------------------------------------------
# Paths — resolved from ~/.mnl/config.yaml or MNL_STORAGE_ROOT env var
# ---------------------------------------------------------------------------
_script_dir = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_script_dir))
from path_helpers import data_root, resolve_repo_root  # noqa: E402

REPO_ROOT = resolve_repo_root()
STORAGE   = data_root() / "processed" / "fr" / "2016"

CANONICAL_SINGLES  = STORAGE / "fr_2016_RURO_mnl__singles.parquet"
CANONICAL_COUPLES  = STORAGE / "fr_2016_RURO_mnl__couples.parquet"
VERSIONED_SINGLES  = STORAGE / "fr_2016_RURO_mnl_GSURv2__singles.parquet"
VERSIONED_COUPLES  = STORAGE / "fr_2016_RURO_mnl_GSURv2__couples.parquet"

LOOKUP_PATH   = REPO_ROOT / "Data/external/FR_gsur_ruro_v2_stageA.parquet"
SIGNOFF_PATH  = REPO_ROOT / "docs/RURO_GSUR_O7_crosswalk_signoff_v1.md"
REPORT_PATH   = REPO_ROOT / "Results/P3a/gsurv2/RURO_GSUR_v2_stageA_MNL_rebuild_report_v1.md"

# New GSUR columns added in Stage A (singles)
GSUR_NEW_COLS_SINGLES = {
    "gsur", "gsur_legacy_misaligned", "gsur_age_band_used",
    "gsur_weighting_source", "denom_flag", "n_components", "gsur_unreliable",
}
# New GSUR columns added in Stage A (couples)
GSUR_NEW_COLS_COUPLES = {
    "gsur_male", "gsur_female",
    "gsur_male_legacy_misaligned", "gsur_female_legacy_misaligned",
    "gsur_male_age_band_used", "gsur_female_age_band_used",
    "gsur_male_weighting_source", "gsur_female_weighting_source",
    "denom_flag_male", "n_components_male", "gsur_unreliable_male",
    "denom_flag_female", "n_components_female", "gsur_unreliable_female",
}


# ---------------------------------------------------------------------------
# Safety guards
# ---------------------------------------------------------------------------
def _assert_signoff():
    if not SIGNOFF_PATH.exists():
        sys.exit(f"ABORT: O7 sign-off not found at {SIGNOFF_PATH}")
    text = SIGNOFF_PATH.read_text(encoding="utf-8")
    required = [
        "fr_drgn1_to_nuts2_crosswalk.csv",
        "FR_gsur_ruro_v2_stageA.parquet",
        "(drgn1, educ3, sex)",
    ]
    missing = [r for r in required if r not in text]
    if missing:
        sys.exit(f"ABORT: O7 sign-off missing required references: {missing}")


def _get_mtime(path: pathlib.Path) -> str:
    if path.exists():
        return path.stat().st_mtime
    return None


def _mtime_str(path: pathlib.Path) -> str:
    if path.exists():
        ts = datetime.datetime.fromtimestamp(path.stat().st_mtime)
        return ts.strftime("%Y-%m-%dT%H:%M:%SZ")
    return "NOT FOUND"


# ---------------------------------------------------------------------------
# Load lookup
# ---------------------------------------------------------------------------
def load_lookup() -> pd.DataFrame:
    lkp = pd.read_parquet(LOOKUP_PATH)
    required = {"drgn1", "educ3", "sex", "gsur", "weighting_source",
                "gsur_age_band_used", "denom_flag", "n_components", "gsur_unreliable"}
    assert required <= set(lkp.columns), f"Lookup missing columns: {required - set(lkp.columns)}"
    lkp = lkp.drop(columns=["gsur_legacy_misaligned"], errors="ignore")
    lkp = lkp.rename(columns={"weighting_source": "gsur_weighting_source"})
    return lkp


# ---------------------------------------------------------------------------
# Singles merge
# ---------------------------------------------------------------------------
def _dgn_to_sex(dgn: pd.Series) -> pd.Series:
    return dgn.map({0.0: "F", 1.0: "M"})


def merge_singles(canon: pd.DataFrame, lkp: pd.DataFrame):
    df = canon.copy()

    # Step 2: capture actual v1 gsur as audit trail
    assert "gsur" in df.columns
    df = df.rename(columns={"gsur": "gsur_legacy_misaligned"})

    # Step 3: join on (drgn1, educ3, sex)
    assert "dgn" in df.columns
    df["_sex"] = _dgn_to_sex(df["dgn"])
    n_before = len(df)
    merge_cols = ["drgn1", "educ3", "_sex"]
    lkp_j = lkp.rename(columns={"sex": "_sex"})
    df = df.merge(
        lkp_j[["drgn1", "educ3", "_sex", "gsur", "gsur_weighting_source",
               "gsur_age_band_used", "denom_flag", "n_components", "gsur_unreliable"]],
        on=merge_cols, how="left", validate="m:1",
    )
    assert len(df) == n_before, "Row count changed after singles merge"
    df = df.drop(columns=["_sex"])

    # Step 4: O3 age-65 override
    dag65 = df["dag"] == 65
    df.loc[dag65, "gsur_age_band_used"] = "Y20-64_fallback_age65"
    n_dag65 = int(dag65.sum())

    # Step 5: O5 drgn1=9 → NaN
    dom = df["drgn1"] == 9
    n_dom = int(dom.sum())
    if n_dom > 0:
        for col in ["gsur", "gsur_weighting_source", "gsur_age_band_used",
                    "gsur_legacy_misaligned", "denom_flag", "n_components", "gsur_unreliable"]:
            df.loc[dom, col] = np.nan

    return df, {"n_dag65": n_dag65, "n_dom": n_dom}


# ---------------------------------------------------------------------------
# Couples merge
# ---------------------------------------------------------------------------
def merge_couples(canon: pd.DataFrame, lkp: pd.DataFrame):
    df = canon.copy()

    # Step 2: capture actual v1 gsur columns as audit trail
    assert "gsur_male" in df.columns and "gsur_female" in df.columns
    df = df.rename(columns={
        "gsur_male":   "gsur_male_legacy_misaligned",
        "gsur_female": "gsur_female_legacy_misaligned",
    })
    n_before = len(df)

    # Step 3: male join on (drgn1, educ3_male, sex=='M')
    lkp_m = lkp[lkp["gsur_weighting_source"].notna() | True]  # all rows
    lkp_m = lkp[lkp["sex"] == "M"].drop(columns=["sex"]).rename(columns={
        "educ3":              "educ3_male",
        "gsur":               "gsur_male",
        "gsur_weighting_source": "gsur_male_weighting_source",
        "gsur_age_band_used": "gsur_male_age_band_used",
        "denom_flag":         "denom_flag_male",
        "n_components":       "n_components_male",
        "gsur_unreliable":    "gsur_unreliable_male",
    })
    df = df.merge(
        lkp_m[["drgn1", "educ3_male", "gsur_male", "gsur_male_weighting_source",
               "gsur_male_age_band_used", "denom_flag_male",
               "n_components_male", "gsur_unreliable_male"]],
        on=["drgn1", "educ3_male"], how="left", validate="m:1",
    )

    # Step 4: female join on (drgn1, educ3_female, sex=='F')
    lkp_f = lkp[lkp["sex"] == "F"].drop(columns=["sex"]).rename(columns={
        "educ3":              "educ3_female",
        "gsur":               "gsur_female",
        "gsur_weighting_source": "gsur_female_weighting_source",
        "gsur_age_band_used": "gsur_female_age_band_used",
        "denom_flag":         "denom_flag_female",
        "n_components":       "n_components_female",
        "gsur_unreliable":    "gsur_unreliable_female",
    })
    df = df.merge(
        lkp_f[["drgn1", "educ3_female", "gsur_female", "gsur_female_weighting_source",
               "gsur_female_age_band_used", "denom_flag_female",
               "n_components_female", "gsur_unreliable_female"]],
        on=["drgn1", "educ3_female"], how="left", validate="m:1",
    )
    assert len(df) == n_before, "Row count changed after couples merge"

    # Step 5: O3 age-65 override (defensive; 0 expected in couples)
    n_dag65 = {"male": 0, "female": 0}
    for partner in ["male", "female"]:
        dag_col = f"dag_{partner}"
        band_col = f"gsur_{partner}_age_band_used"
        if dag_col in df.columns:
            mask = df[dag_col] == 65
            n_dag65[partner] = int(mask.sum())
            df.loc[mask, band_col] = "Y20-64_fallback_age65"

    # Step 6: O5 drgn1=9 → NaN
    dom = df["drgn1"] == 9
    n_dom = int(dom.sum())
    if n_dom > 0:
        for partner in ["male", "female"]:
            for col in [f"gsur_{partner}", f"gsur_{partner}_weighting_source",
                        f"gsur_{partner}_age_band_used",
                        f"gsur_{partner}_legacy_misaligned",
                        f"denom_flag_{partner}", f"n_components_{partner}",
                        f"gsur_unreliable_{partner}"]:
                if col in df.columns:
                    df.loc[dom, col] = np.nan

    return df, {"n_dag65": n_dag65, "n_dom": n_dom}


# ---------------------------------------------------------------------------
# Checks — approved M1–M10 + diagnostics
# ---------------------------------------------------------------------------

def check_m1_non_gsur_equality(v2: pd.DataFrame, canon: pd.DataFrame,
                                 gsur_new_cols: set) -> dict:
    """M1: all non-GSUR columns value-identical to canonical."""
    # Canonical columns that existed before (exclude any GSUR-related old col)
    # For singles: canon had 'gsur' — now 'gsur_legacy_misaligned' in v2
    # We compare all columns that came from canon (i.e. not new GSUR cols)
    canon_orig_cols = list(canon.columns)
    # Map: in canon 'gsur' became 'gsur_legacy_misaligned' in v2
    # Non-GSUR = those that are unchanged from canon
    gsur_old_singles = {"gsur"}
    gsur_old_couples = {"gsur_male", "gsur_female"}
    old_gsur = gsur_old_singles | gsur_old_couples

    fail_cols = []
    skip_cols = []
    for col in canon_orig_cols:
        if col in old_gsur:
            skip_cols.append(col)  # renamed, not a value check
            continue
        if col not in v2.columns:
            fail_cols.append(f"{col}(missing)")
            continue
        try:
            eq = v2[col].equals(canon[col])
            if not eq:
                fail_cols.append(col)
        except Exception as e:
            fail_cols.append(f"{col}(err:{e})")

    return {
        "check": "M1 — Value-identical non-GSUR columns",
        "n_checked": len(canon_orig_cols) - len(skip_cols),
        "n_failed": len(fail_cols),
        "fail_cols": fail_cols,
        "pass": len(fail_cols) == 0,
    }


def check_m2_schema(v2: pd.DataFrame, is_couples: bool) -> dict:
    """M2: required GSUR columns present per v2.1 §8."""
    if is_couples:
        required = {
            "gsur_male", "gsur_female",
            "gsur_male_legacy_misaligned", "gsur_female_legacy_misaligned",
            "gsur_male_age_band_used", "gsur_female_age_band_used",
            "gsur_male_weighting_source", "gsur_female_weighting_source",
        }
    else:
        required = {
            "gsur", "gsur_legacy_misaligned", "gsur_age_band_used",
            "gsur_weighting_source",
        }
    actual = set(v2.columns)
    missing = required - actual
    return {
        "check": "M2 — GSUR column schema",
        "required_cols": sorted(required),
        "missing_cols": sorted(missing),
        "pass": len(missing) == 0,
    }


def check_m3_no_nan_gsur(v2: pd.DataFrame, is_couples: bool) -> dict:
    """M3: no NaN in gsur for any row (age-65 gets Y20-64 value, not NaN)."""
    active = v2[v2["drgn1"] != 9]
    if is_couples:
        n_nan_m = int(active["gsur_male"].isna().sum())
        n_nan_f = int(active["gsur_female"].isna().sum())
        return {
            "check": "M3 — No NaN in gsur_male/gsur_female",
            "n_nan_male": n_nan_m,
            "n_nan_female": n_nan_f,
            "pass": n_nan_m == 0 and n_nan_f == 0,
        }
    else:
        n_nan = int(active["gsur"].isna().sum())
        return {
            "check": "M3 — No NaN in gsur",
            "n_nan": n_nan,
            "pass": n_nan == 0,
        }


def check_m4_idf_parity(v2: pd.DataFrame, lkp: pd.DataFrame, is_couples: bool) -> dict:
    """M4: IDF parity — versioned gsur for drgn1=1 within 0.001 of lookup values."""
    idf = v2[v2["drgn1"] == 1].copy()
    if is_couples:
        max_diff = 0.0
        cell_rows = []
        for partner in ["male", "female"]:
            sex_str = "M" if partner == "male" else "F"
            educ_col = f"educ3_{partner}"
            gsur_col = f"gsur_{partner}"
            lkp_p = lkp[(lkp["drgn1"] == 1) & (lkp["sex"] == sex_str)][
                ["educ3", "gsur"]].rename(columns={"educ3": educ_col, "gsur": f"_lkp_{partner}"})
            merged = idf[[educ_col, gsur_col]].merge(lkp_p, on=educ_col, how="left")
            diff = (merged[gsur_col] - merged[f"_lkp_{partner}"]).abs()
            max_diff = max(max_diff, float(diff.max()))
            for _, row in lkp_p.iterrows():
                cell_rows.append({
                    "partner": partner,
                    "educ3": row[educ_col],
                    "parquet_val": float(merged.loc[merged[educ_col] == row[educ_col], gsur_col].iloc[0]),
                    "lookup_val": float(row[f"_lkp_{partner}"]),
                })
        return {
            "check": "M4 — IDF parity (couples)",
            "max_abs_diff": max_diff,
            "tolerance": 0.001,
            "cells": cell_rows,
            "pass": max_diff <= 0.001,
        }
    else:
        idf["_sex"] = _dgn_to_sex(idf["dgn"])
        lkp_idf = lkp[lkp["drgn1"] == 1][["educ3", "sex", "gsur"]].rename(
            columns={"sex": "_sex", "gsur": "_gsur_lkp"})
        merged = idf[["educ3", "_sex", "gsur"]].merge(lkp_idf, on=["educ3", "_sex"], how="left")
        diff = (merged["gsur"] - merged["_gsur_lkp"]).abs()
        max_diff = float(diff.max())
        cells = []
        for _, row in lkp_idf.iterrows():
            mask = (merged["educ3"] == row["educ3"]) & (merged["_sex"] == row["_sex"])
            pval = float(merged.loc[mask, "gsur"].iloc[0]) if mask.any() else float("nan")
            cells.append({
                "educ3": int(row["educ3"]),
                "sex": row["_sex"],
                "parquet_val": pval,
                "lookup_val": float(row["_gsur_lkp"]),
                "diff": abs(pval - float(row["_gsur_lkp"])),
            })
        return {
            "check": "M4 — IDF parity (singles)",
            "max_abs_diff": max_diff,
            "tolerance": 0.001,
            "cells": cells,
            "pass": max_diff <= 0.001,
        }


def check_m4_diag_v1_v2(v2: pd.DataFrame, is_couples: bool) -> dict:
    """M4-diag: v1→v2 change by drgn1 (diagnostic, not pass/fail)."""
    active = v2[v2["drgn1"] != 9]
    rows = []
    if is_couples:
        for partner in ["male", "female"]:
            gsur_col = f"gsur_{partner}"
            leg_col = f"gsur_{partner}_legacy_misaligned"
            for drgn, grp in active.groupby("drgn1"):
                diff = (grp[gsur_col] - grp[leg_col]).abs().dropna()
                rows.append({
                    "partner": partner, "drgn1": int(drgn),
                    "n": len(grp),
                    "mean_abs_diff": float(diff.mean()) if len(diff) else float("nan"),
                    "max_abs_diff": float(diff.max()) if len(diff) else float("nan"),
                })
    else:
        for drgn, grp in active.groupby("drgn1"):
            diff = (grp["gsur"] - grp["gsur_legacy_misaligned"]).abs().dropna()
            rows.append({
                "drgn1": int(drgn), "n": len(grp),
                "mean_abs_diff": float(diff.mean()) if len(diff) else float("nan"),
                "max_abs_diff": float(diff.max()) if len(diff) else float("nan"),
            })
    overall_diff = (active["gsur"] - active["gsur_legacy_misaligned"]).abs().dropna() \
        if not is_couples else \
        pd.concat([
            (active["gsur_male"] - active["gsur_male_legacy_misaligned"]).abs(),
            (active["gsur_female"] - active["gsur_female_legacy_misaligned"]).abs(),
        ]).dropna()
    return {
        "check": "M4-diag — v1→v2 correction magnitude",
        "by_drgn1": rows,
        "overall_mean_abs_diff": float(overall_diff.mean()),
        "overall_max_abs_diff": float(overall_diff.max()),
        "pass": None,  # diagnostic
    }


def check_m5_age_band(v2: pd.DataFrame, is_couples: bool) -> dict:
    """M5: age-band assignment correct including O3 age-65 override."""
    if is_couples:
        results = {}
        fail = False
        for partner in ["male", "female"]:
            dag_col = f"dag_{partner}"
            band_col = f"gsur_{partner}_age_band_used"
            if dag_col not in v2.columns:
                results[partner] = {"note": f"{dag_col} absent"}
                continue
            active = v2[v2["drgn1"] != 9]
            n_65 = int((active[dag_col] == 65).sum())
            n_wrong_65 = int(((active[dag_col] == 65) & (active[band_col] != "Y20-64_fallback_age65")).sum())
            n_lt65 = int((active[dag_col] < 65).sum())
            n_wrong_lt65 = int(((active[dag_col] < 65) & (active[band_col] != "Y20-64")).sum())
            results[partner] = {
                "n_age65": n_65, "n_wrong_label_age65": n_wrong_65,
                "n_age_lt65": n_lt65, "n_wrong_label_lt65": n_wrong_lt65,
            }
            if n_wrong_65 > 0 or n_wrong_lt65 > 0:
                fail = True
        return {"check": "M5 — Age-band assignment (couples)", "partners": results, "pass": not fail}
    else:
        active = v2[v2["drgn1"] != 9]
        n_65 = int((active["dag"] == 65).sum())
        n_wrong_65 = int(((active["dag"] == 65) & (active["gsur_age_band_used"] != "Y20-64_fallback_age65")).sum())
        n_lt65 = int((active["dag"] < 65).sum())
        n_wrong_lt65 = int(((active["dag"] < 65) & (active["gsur_age_band_used"] != "Y20-64")).sum())
        crosstab = active.groupby(["dag", "gsur_age_band_used"]).size().reset_index(name="n")
        return {
            "check": "M5 — Age-band assignment (singles)",
            "n_age65": n_65, "n_wrong_label_age65": n_wrong_65,
            "n_age_lt65": n_lt65, "n_wrong_label_lt65": n_wrong_lt65,
            "crosstab_summary": f"{len(crosstab)} unique (dag, band) combos",
            "pass": n_wrong_65 == 0 and n_wrong_lt65 == 0,
        }


def check_m6_partner_consistency(v2: pd.DataFrame) -> dict:
    """M6: couples — fraction where gsur_male == gsur_female (should not be 100%)."""
    active = v2[v2["drgn1"] != 9]
    n_identical = int((active["gsur_male"] == active["gsur_female"]).sum())
    frac = n_identical / len(active) if len(active) > 0 else float("nan")
    return {
        "check": "M6 — Partner-specific consistency (couples)",
        "n_rows": len(active),
        "n_identical_male_female": n_identical,
        "frac_identical": round(frac, 4),
        "note": "Expected ~15%; if 100% merge applied identical values to both partners",
        "pass": None,  # documented, not pass/fail
    }


def check_m7_row_count(v2: pd.DataFrame, canon: pd.DataFrame,
                        expected_rows: int, expected_hh: int,
                        is_couples: bool) -> dict:
    """M7: row count and household count preserved."""
    n_rows = len(v2)
    hh_col = "idhh" if "idhh" in v2.columns else None
    n_hh = v2[hh_col].nunique() if hh_col else None
    return {
        "check": "M7 — Row count preservation",
        "expected_rows": expected_rows,
        "actual_rows": n_rows,
        "expected_hh": expected_hh,
        "actual_hh": n_hh,
        "pass": bool(n_rows == expected_rows and (n_hh is None or n_hh == expected_hh)),
    }


def check_m8_forensic(v2: pd.DataFrame, canon: pd.DataFrame, is_couples: bool) -> dict:
    """M8: gsur_legacy_misaligned equals actual v1 canonical gsur values."""
    if is_couples:
        pairs = [("gsur_male", "gsur_male_legacy_misaligned"),
                 ("gsur_female", "gsur_female_legacy_misaligned")]
        results = {}
        fail = False
        for canon_col, leg_col in pairs:
            if canon_col not in canon.columns:
                results[canon_col] = {"note": "column absent in canonical"}
                fail = True
                continue
            equal = v2[leg_col].equals(canon[canon_col])
            # NaN-safe check: where canonical is NaN, v2 leg should also be NaN
            canon_vals = canon[canon_col].values
            v2_leg_vals = v2[leg_col].values
            nan_agree = np.sum(np.isnan(canon_vals.astype(float)) == np.isnan(v2_leg_vals.astype(float)))
            non_nan_mask = ~np.isnan(canon_vals.astype(float))
            if non_nan_mask.sum() > 0:
                max_diff = float(np.max(np.abs(
                    canon_vals[non_nan_mask].astype(float) -
                    v2_leg_vals[non_nan_mask].astype(float)
                )))
            else:
                max_diff = 0.0
            results[canon_col] = {
                "value_identical": bool(equal),
                "max_abs_diff": max_diff,
            }
            if not equal:
                fail = True
        return {
            "check": "M8 — Forensic record preservation (couples)",
            "pairs": results,
            "pass": not fail,
        }
    else:
        equal = v2["gsur_legacy_misaligned"].equals(canon["gsur"])
        canon_vals = canon["gsur"].values.astype(float)
        v2_leg_vals = v2["gsur_legacy_misaligned"].values.astype(float)
        non_nan = ~np.isnan(canon_vals)
        max_diff = float(np.max(np.abs(canon_vals[non_nan] - v2_leg_vals[non_nan]))) \
            if non_nan.sum() > 0 else 0.0
        return {
            "check": "M8 — Forensic record preservation (singles)",
            "value_identical": bool(equal),
            "max_abs_diff": max_diff,
            "pass": bool(equal) and max_diff == 0.0,
        }


def check_m9_load_compat(path: pathlib.Path, is_couples: bool) -> dict:
    """M9: versioned parquet readable; gsur column accessible as numeric."""
    try:
        df = pd.read_parquet(path)
        if is_couples:
            dtypes = {
                "gsur_male": str(df["gsur_male"].dtype),
                "gsur_female": str(df["gsur_female"].dtype),
            }
            is_numeric = (
                pd.api.types.is_float_dtype(df["gsur_male"]) and
                pd.api.types.is_float_dtype(df["gsur_female"])
            )
        else:
            dtypes = {"gsur": str(df["gsur"].dtype)}
            is_numeric = pd.api.types.is_float_dtype(df["gsur"])
        return {
            "check": "M9 — Cross-stage load compatibility",
            "path": str(path),
            "n_rows_loaded": len(df),
            "n_cols": len(df.columns),
            "gsur_dtypes": dtypes,
            "gsur_is_numeric": is_numeric,
            "pass": is_numeric,
        }
    except Exception as e:
        return {"check": "M9 — Cross-stage load compatibility", "error": str(e), "pass": False}


def check_m10_canonical_untouched(
    canon_singles_mtime_before: float, canon_couples_mtime_before: float,
) -> dict:
    """M10: canonical file timestamps unchanged; versioned files exist."""
    cs_mtime_after = _get_mtime(CANONICAL_SINGLES)
    cc_mtime_after = _get_mtime(CANONICAL_COUPLES)
    vs_exists = VERSIONED_SINGLES.exists()
    vc_exists = VERSIONED_COUPLES.exists()

    singles_unchanged = (cs_mtime_after == canon_singles_mtime_before) if cs_mtime_after else False
    couples_unchanged = (cc_mtime_after == canon_couples_mtime_before) if cc_mtime_after else False

    return {
        "check": "M10 — Versioned path / canonical untouched",
        "canonical_singles_mtime_before": datetime.datetime.fromtimestamp(canon_singles_mtime_before).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "canonical_singles_mtime_after": datetime.datetime.fromtimestamp(cs_mtime_after).strftime("%Y-%m-%dT%H:%M:%SZ") if cs_mtime_after else "N/A",
        "canonical_singles_unchanged": singles_unchanged,
        "canonical_couples_mtime_before": datetime.datetime.fromtimestamp(canon_couples_mtime_before).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "canonical_couples_mtime_after": datetime.datetime.fromtimestamp(cc_mtime_after).strftime("%Y-%m-%dT%H:%M:%SZ") if cc_mtime_after else "N/A",
        "canonical_couples_unchanged": couples_unchanged,
        "versioned_singles_exists": vs_exists,
        "versioned_couples_exists": vc_exists,
        "pass": bool(singles_unchanged and couples_unchanged and vs_exists and vc_exists),
    }


def check_m11_diag(v2_s: pd.DataFrame, v2_c: pd.DataFrame) -> dict:
    """M11-diag: GSUR distribution by demographic cell."""
    # Singles: group by drgn1 × dgn × educ3
    active_s = v2_s[v2_s["drgn1"] != 9]
    s_rows = []
    for (drgn, dgn, educ), grp in active_s.groupby(["drgn1", "dgn", "educ3"]):
        diff = (grp["gsur"] - grp["gsur_legacy_misaligned"]).dropna()
        s_rows.append({
            "drgn1": int(drgn), "dgn": int(dgn), "educ3": int(educ),
            "n": len(grp),
            "mean_gsur_v2": round(float(grp["gsur"].mean()), 4),
            "mean_gsur_v1": round(float(grp["gsur_legacy_misaligned"].mean()), 4),
            "mean_diff": round(float(diff.mean()), 4) if len(diff) else float("nan"),
            "max_abs_diff": round(float(diff.abs().max()), 4) if len(diff) else float("nan"),
        })

    # Couples male: group by drgn1 × educ3_male
    active_c = v2_c[v2_c["drgn1"] != 9]
    cm_rows = []
    for (drgn, educ), grp in active_c.groupby(["drgn1", "educ3_male"]):
        diff = (grp["gsur_male"] - grp["gsur_male_legacy_misaligned"]).dropna()
        cm_rows.append({
            "drgn1": int(drgn), "educ3_male": int(educ),
            "n": len(grp),
            "mean_gsur_male_v2": round(float(grp["gsur_male"].mean()), 4),
            "mean_gsur_male_v1": round(float(grp["gsur_male_legacy_misaligned"].mean()), 4),
            "mean_diff": round(float(diff.mean()), 4) if len(diff) else float("nan"),
            "max_abs_diff": round(float(diff.abs().max()), 4) if len(diff) else float("nan"),
        })

    # Couples female: group by drgn1 × educ3_female
    cf_rows = []
    for (drgn, educ), grp in active_c.groupby(["drgn1", "educ3_female"]):
        diff = (grp["gsur_female"] - grp["gsur_female_legacy_misaligned"]).dropna()
        cf_rows.append({
            "drgn1": int(drgn), "educ3_female": int(educ),
            "n": len(grp),
            "mean_gsur_female_v2": round(float(grp["gsur_female"].mean()), 4),
            "mean_gsur_female_v1": round(float(grp["gsur_female_legacy_misaligned"].mean()), 4),
            "mean_diff": round(float(diff.mean()), 4) if len(diff) else float("nan"),
            "max_abs_diff": round(float(diff.abs().max()), 4) if len(diff) else float("nan"),
        })

    return {
        "check": "M11-diag — GSUR distribution by demographic cell",
        "singles_by_drgn1_dgn_educ3": s_rows,
        "couples_male_by_drgn1_educ3": cm_rows,
        "couples_female_by_drgn1_educ3": cf_rows,
        "pass": None,
    }


def check_m12_diag(v2_s: pd.DataFrame, v2_c: pd.DataFrame) -> dict:
    """M12-diag: gsur constant within idhh (hard check despite diagnostic label)."""
    # Singles
    active_s = v2_s[v2_s["drgn1"] != 9]
    hh_col_s = "idhh" if "idhh" in active_s.columns else None
    s_result = {}
    if hh_col_s:
        cols_to_check = ["gsur", "gsur_legacy_misaligned", "gsur_weighting_source", "gsur_age_band_used"]
        for col in cols_to_check:
            if col in active_s.columns:
                nunique = active_s.groupby(hh_col_s)[col].nunique()
                s_result[col] = int((nunique > 1).sum())
    n_fail_s = sum(v for v in s_result.values() if isinstance(v, int) and v > 0)

    # Couples
    active_c = v2_c[v2_c["drgn1"] != 9]
    hh_col_c = "idhh" if "idhh" in active_c.columns else None
    c_result = {}
    if hh_col_c:
        cols_to_check_c = [
            "gsur_male", "gsur_female",
            "gsur_male_legacy_misaligned", "gsur_female_legacy_misaligned",
            "gsur_male_weighting_source", "gsur_female_weighting_source",
            "gsur_male_age_band_used", "gsur_female_age_band_used",
        ]
        for col in cols_to_check_c:
            if col in active_c.columns:
                nunique = active_c.groupby(hh_col_c)[col].nunique()
                c_result[col] = int((nunique > 1).sum())
    n_fail_c = sum(v for v in c_result.values() if isinstance(v, int) and v > 0)

    return {
        "check": "M12-diag — Household-level constancy (HARD check)",
        "singles_n_hh_varying_by_col": s_result,
        "couples_n_hh_varying_by_col": c_result,
        "pass": bool(n_fail_s == 0 and n_fail_c == 0),
    }


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------
def _pf(p) -> str:
    if p is None:
        return "DOCUMENTED"
    return "**PASS**" if bool(p) else "**FAIL**"


def _fmt_cells_singles(cells: list) -> str:
    rows = ["| educ3 | sex | parquet gsur | lookup gsur | diff |",
            "|---|---|---|---|---|"]
    for c in cells:
        rows.append(f"| {c['educ3']} | {c['sex']} | {c['parquet_val']:.6f} | {c['lookup_val']:.6f} | {c.get('diff', abs(c['parquet_val']-c['lookup_val'])):.6f} |")
    return "\n".join(rows)


def _fmt_m11_singles(rows: list) -> str:
    hdr = ["| drgn1 | dgn | educ3 | n | mean gsur v2 | mean gsur v1 | mean diff | max|diff| |",
           "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        hdr.append(f"| {r['drgn1']} | {r['dgn']} | {r['educ3']} | {r['n']} | {r['mean_gsur_v2']:.4f} | {r['mean_gsur_v1']:.4f} | {r['mean_diff']:+.4f} | {r['max_abs_diff']:.4f} |")
    return "\n".join(hdr)


def _fmt_m11_couples(rows: list, educ_col: str, gsur_col: str, leg_col: str) -> str:
    hdr = [f"| drgn1 | {educ_col} | n | mean gsur v2 | mean gsur v1 | mean diff | max|diff| |",
           "|---|---|---|---|---|---|---|"]
    for r in rows:
        hdr.append(f"| {r['drgn1']} | {r[educ_col]} | {r['n']} | {r[gsur_col]:.4f} | {r[leg_col]:.4f} | {r['mean_diff']:+.4f} | {r['max_abs_diff']:.4f} |")
    return "\n".join(hdr)


def write_report(
    checks_s: dict, checks_c: dict,
    m4d: dict, m11: dict, m12: dict,
    run_ts: str,
    canon_s_mtime: str, canon_c_mtime: str,
    vs_mtime: str, vc_mtime: str,
    vs_size: int, vc_size: int,
    canon_s_size: int, canon_c_size: int,
):
    hard_checks = ["M1", "M2", "M3", "M4", "M5", "M7", "M8", "M9", "M10"]
    all_hard = {**checks_s, **checks_c}
    n_hard_fail = sum(1 for k, v in all_hard.items() if k in hard_checks and v.get("pass") is False)
    m12_pass = bool(m12.get("pass"))
    overall_fail = n_hard_fail > 0 or not m12_pass
    overall = "PASS" if not overall_fail else "FAIL"

    m4_idf_table = _fmt_cells_singles(checks_s["M4"]["cells"])
    m11_s_table = _fmt_m11_singles(m11["singles_by_drgn1_dgn_educ3"])
    m11_cm_table = _fmt_m11_couples(m11["couples_male_by_drgn1_educ3"], "educ3_male",
                                     "mean_gsur_male_v2", "mean_gsur_male_v1")
    m11_cf_table = _fmt_m11_couples(m11["couples_female_by_drgn1_educ3"], "educ3_female",
                                     "mean_gsur_female_v2", "mean_gsur_female_v1")

    s = checks_s
    c = checks_c
    report = f"""# RURO GSUR v2 Stage A MNL Rebuild Report v1

Date: {run_ts[:10]}
Run timestamp: {run_ts}
Script: `scripts/enhanced/enh_RURO_mnl_rebuild_GSURv2_stageA.py`
Prompt: `Prompts/RURO_GSUR_v2_stageA_MNL_rebuild_prompt_corrected_v2.md`
Authorisation: `docs/RURO_GSUR_O7_crosswalk_signoff_v1.md`

---

## 1. Overall verdict

| Item | Value |
|---|---|
| **Overall result** | **{overall}** |
| Hard checks failed | {n_hard_fail} |
| M12-diag (hard) | {_pf(m12_pass)} |
| Re-estimation authorized | {"YES — all hard checks PASS" if overall == "PASS" else "NO — see failures"} |

---

## 2. Input files (canonical, read-only)

| File | Rows | Size | mtime (before task) |
|---|---|---|---|
| `fr_2016_RURO_mnl__singles.parquet` | 167,600 | {canon_s_size:,} bytes | {canon_s_mtime} |
| `fr_2016_RURO_mnl__couples.parquet` | 257,700 | {canon_c_size:,} bytes | {canon_c_mtime} |
| `Data/external/FR_gsur_ruro_v2_stageA.parquet` | 54 | — | — |

---

## 3. Output files (versioned)

| File | Rows | Size | mtime (after task) |
|---|---|---|---|
| `fr_2016_RURO_mnl_GSURv2__singles.parquet` | {s["M7"]["actual_rows"]:,} | {vs_size:,} bytes | {vs_mtime} |
| `fr_2016_RURO_mnl_GSURv2__couples.parquet` | {c["M7"]["actual_rows"]:,} | {vc_size:,} bytes | {vc_mtime} |

---

## 4. M1 — Value-identical non-GSUR columns

| Item | Singles | Couples |
|---|---|---|
| Columns checked | {s["M1"]["n_checked"]} | {c["M1"]["n_checked"]} |
| Columns failed | {s["M1"]["n_failed"]} | {c["M1"]["n_failed"]} |
| Failed cols | {s["M1"]["fail_cols"]} | {c["M1"]["fail_cols"]} |
| **Result** | {_pf(s["M1"]["pass"])} | {_pf(c["M1"]["pass"])} |

---

## 5. M2 — GSUR column schema

**Singles** — missing columns: `{s["M2"]["missing_cols"]}` → {_pf(s["M2"]["pass"])}

**Couples** — missing columns: `{c["M2"]["missing_cols"]}` → {_pf(c["M2"]["pass"])}

---

## 6. M3 — No NaN in gsur

| Item | Singles | Couples |
|---|---|---|
| NaN count (singles gsur) | {s["M3"]["n_nan"]} | — |
| NaN count (couples gsur_male) | — | {c["M3"]["n_nan_male"]} |
| NaN count (couples gsur_female) | — | {c["M3"]["n_nan_female"]} |
| **Result** | {_pf(s["M3"]["pass"])} | {_pf(c["M3"]["pass"])} |

---

## 7. M4 — Île-de-France parity (hard pass/fail, tolerance 0.001)

This check confirms that the rebuilt `gsur` column in the versioned parquet
equals the validated Stage A lookup value for drgn1=1 households.

**Singles — per (educ3, sex) cell:**

{m4_idf_table}

max |diff| = {s["M4"]["max_abs_diff"]:.6f} → {_pf(s["M4"]["pass"])}

**Couples** — max |diff| male = {c["M4"].get("max_abs_diff_male", c["M4"]["max_abs_diff"]):.6f},
female = {c["M4"].get("max_abs_diff_female", c["M4"]["max_abs_diff"]):.6f} → {_pf(c["M4"]["pass"])}

---

## 8. M4-diag — v1→v2 correction magnitude by drgn1 (diagnostic)

Large differences expected for low-educ (educ3=0) and high-educ (educ3=2) cells
because v1 `gsur` was not education-stratified.

Overall mean |diff| (singles): {m4d["overall_mean_abs_diff"]:.4f}
Overall max |diff| (singles): {m4d["overall_max_abs_diff"]:.4f}

Result: DOCUMENTED (not pass/fail)

---

## 9. M5 — Age-band assignment

| Item | Singles | Couples |
|---|---|---|
| dag==65 rows | {s["M5"]["n_age65"]} | (see below) |
| dag==65 with wrong label | {s["M5"]["n_wrong_label_age65"]} | — |
| dag<65 rows | {s["M5"]["n_age_lt65"]} | (see below) |
| dag<65 with wrong label | {s["M5"]["n_wrong_label_lt65"]} | — |
| **Result** | {_pf(s["M5"]["pass"])} | {_pf(c["M5"]["pass"])} |

Couples detail (partners): {c["M5"]["partners"]}

---

## 10. M6 — Partner-specific consistency (couples, documented)

| Item | Value |
|---|---|
| Active rows | {c["M6"]["n_rows"]:,} |
| Rows with gsur_male == gsur_female | {c["M6"]["n_identical_male_female"]:,} |
| Fraction identical | {c["M6"]["frac_identical"]:.1%} |
| Note | {c["M6"]["note"]} |

Result: DOCUMENTED

---

## 11. M7 — Row count preservation

| Parquet | Expected rows | Actual rows | Expected HH | Actual HH | Result |
|---|---|---|---|---|---|
| Singles | {s["M7"]["expected_rows"]:,} | {s["M7"]["actual_rows"]:,} | {s["M7"]["expected_hh"]:,} | {s["M7"]["actual_hh"]:,} | {_pf(s["M7"]["pass"])} |
| Couples | {c["M7"]["expected_rows"]:,} | {c["M7"]["actual_rows"]:,} | {c["M7"]["expected_hh"]:,} | {c["M7"]["actual_hh"]:,} | {_pf(c["M7"]["pass"])} |

---

## 12. M8 — Forensic record preservation

`gsur_legacy_misaligned` must equal the actual v1 canonical `gsur` value (column-wise).

**Singles:**
- value_identical = {s["M8"]["value_identical"]}
- max_abs_diff = {s["M8"]["max_abs_diff"]}
- **Result: {_pf(s["M8"]["pass"])}**

**Couples (male):**
- value_identical = {c["M8"]["pairs"]["gsur_male"]["value_identical"]}
- max_abs_diff = {c["M8"]["pairs"]["gsur_male"]["max_abs_diff"]}

**Couples (female):**
- value_identical = {c["M8"]["pairs"]["gsur_female"]["value_identical"]}
- max_abs_diff = {c["M8"]["pairs"]["gsur_female"]["max_abs_diff"]}

**Result couples: {_pf(c["M8"]["pass"])}**

---

## 13. M9 — Cross-stage load compatibility

| Item | Singles | Couples |
|---|---|---|
| Readable by pd.read_parquet | Yes | Yes |
| gsur dtype | {s["M9"]["gsur_dtypes"]} | {c["M9"]["gsur_dtypes"]} |
| gsur is numeric float | {s["M9"]["gsur_is_numeric"]} | {c["M9"]["gsur_is_numeric"]} |
| **Result** | {_pf(s["M9"]["pass"])} | {_pf(c["M9"]["pass"])} |

---

## 14. M10 — Versioned path / canonical untouched

| Item | Value |
|---|---|
| canonical singles mtime before | {s["M10"]["canonical_singles_mtime_before"]} |
| canonical singles mtime after | {s["M10"]["canonical_singles_mtime_after"]} |
| canonical singles unchanged | {s["M10"]["canonical_singles_unchanged"]} |
| canonical couples mtime before | {s["M10"]["canonical_couples_mtime_before"]} |
| canonical couples mtime after | {s["M10"]["canonical_couples_mtime_after"]} |
| canonical couples unchanged | {s["M10"]["canonical_couples_unchanged"]} |
| versioned singles exists | {s["M10"]["versioned_singles_exists"]} |
| versioned couples exists | {s["M10"]["versioned_couples_exists"]} |
| **Result** | {_pf(s["M10"]["pass"])} |

---

## 15. M11-diag — GSUR distribution by demographic cell

### Singles (drgn1 × dgn × educ3)

{m11_s_table}

### Couples male (drgn1 × educ3_male)

{m11_cm_table}

### Couples female (drgn1 × educ3_female)

{m11_cf_table}

Result: DOCUMENTED

---

## 16. M12-diag — Household-level constancy (HARD check)

**Singles** (households where column varies within idhh):

{m12["singles_n_hh_varying_by_col"]}

**Couples** (households where column varies within idhh):

{m12["couples_n_hh_varying_by_col"]}

**Result: {_pf(m12["pass"])}** (zero variation expected; any non-zero = merge bug)

---

## 17. Stage A estimation readiness

All hard checks M1–M10 and M12-diag: **{overall}**

{"**Stage A re-estimation against the versioned GSURv2 parquets is authorized per spec §14.**" if overall == "PASS" else "**Stage A re-estimation is NOT authorized. Diagnose failures above.**"}

Canonical promotion remains deferred (requires Stage A verdict SA-STANDS/SA-REVISION and separate O10 approval).
Stage B age-specific GSUR and welfare computation remain deferred.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Report written: {REPORT_PATH}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("RURO GSUR v2 Stage A MNL rebuild — approved M1–M10 validation")
    print("=" * 70)

    _assert_signoff()
    print(f"[OK] O7 sign-off verified")

    for p in [CANONICAL_SINGLES, CANONICAL_COUPLES, LOOKUP_PATH]:
        if not p.exists():
            sys.exit(f"ABORT: required input not found: {p}")

    # Record canonical mtimes before any writes
    canon_s_mtime_before = _get_mtime(CANONICAL_SINGLES)
    canon_c_mtime_before = _get_mtime(CANONICAL_COUPLES)
    canon_s_mtime_str = _mtime_str(CANONICAL_SINGLES)
    canon_c_mtime_str = _mtime_str(CANONICAL_COUPLES)
    canon_s_size = CANONICAL_SINGLES.stat().st_size
    canon_c_size = CANONICAL_COUPLES.stat().st_size

    lkp = load_lookup()
    print(f"[OK] Lookup: {len(lkp)} rows")

    run_ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ---- Singles ----
    print("\n--- Singles ---")
    canon_s = pd.read_parquet(CANONICAL_SINGLES)
    print(f"  Canonical: {len(canon_s):,} rows × {len(canon_s.columns)} cols")

    v2_s, meta_s = merge_singles(canon_s, lkp)
    print(f"  Merged:    {len(v2_s):,} rows × {len(v2_s.columns)} cols")
    pq.write_table(pa.Table.from_pandas(v2_s), str(VERSIONED_SINGLES))
    print(f"  Written:   {VERSIONED_SINGLES}")

    # ---- Couples ----
    print("\n--- Couples ---")
    canon_c = pd.read_parquet(CANONICAL_COUPLES)
    print(f"  Canonical: {len(canon_c):,} rows × {len(canon_c.columns)} cols")

    v2_c, meta_c = merge_couples(canon_c, lkp)
    print(f"  Merged:    {len(v2_c):,} rows × {len(v2_c.columns)} cols")
    pq.write_table(pa.Table.from_pandas(v2_c), str(VERSIONED_COUPLES))
    print(f"  Written:   {VERSIONED_COUPLES}")

    vs_mtime = _mtime_str(VERSIONED_SINGLES)
    vc_mtime = _mtime_str(VERSIONED_COUPLES)
    vs_size = VERSIONED_SINGLES.stat().st_size
    vc_size = VERSIONED_COUPLES.stat().st_size

    # ---- Run M1–M10 ----
    print("\n--- Running M1–M10 checks ---")

    # M1
    m1_s = check_m1_non_gsur_equality(v2_s, canon_s, GSUR_NEW_COLS_SINGLES)
    m1_c = check_m1_non_gsur_equality(v2_c, canon_c, GSUR_NEW_COLS_COUPLES)
    print(f"  M1 singles: {'PASS' if m1_s['pass'] else 'FAIL'} ({m1_s['n_checked']} cols, {m1_s['n_failed']} failed)")
    print(f"  M1 couples: {'PASS' if m1_c['pass'] else 'FAIL'} ({m1_c['n_checked']} cols, {m1_c['n_failed']} failed)")

    # M2
    m2_s = check_m2_schema(v2_s, is_couples=False)
    m2_c = check_m2_schema(v2_c, is_couples=True)
    print(f"  M2 singles: {'PASS' if m2_s['pass'] else 'FAIL'}")
    print(f"  M2 couples: {'PASS' if m2_c['pass'] else 'FAIL'}")

    # M3
    m3_s = check_m3_no_nan_gsur(v2_s, is_couples=False)
    m3_c = check_m3_no_nan_gsur(v2_c, is_couples=True)
    print(f"  M3 singles: {'PASS' if m3_s['pass'] else 'FAIL'}")
    print(f"  M3 couples: {'PASS' if m3_c['pass'] else 'FAIL'}")

    # M4 (IDF parity hard gate)
    m4_s = check_m4_idf_parity(v2_s, lkp, is_couples=False)
    m4_c = check_m4_idf_parity(v2_c, lkp, is_couples=True)
    print(f"  M4 singles: {'PASS' if m4_s['pass'] else 'FAIL'} (max_diff={m4_s['max_abs_diff']:.6f})")
    print(f"  M4 couples: {'PASS' if m4_c['pass'] else 'FAIL'} (max_diff={m4_c['max_abs_diff']:.6f})")

    # M4-diag
    m4d_s = check_m4_diag_v1_v2(v2_s, is_couples=False)
    m4d_c = check_m4_diag_v1_v2(v2_c, is_couples=True)
    m4d_combined = m4d_s  # use singles for report summary; couples details in M11-diag

    # M5
    m5_s = check_m5_age_band(v2_s, is_couples=False)
    m5_c = check_m5_age_band(v2_c, is_couples=True)
    print(f"  M5 singles: {'PASS' if m5_s['pass'] else 'FAIL'}")
    print(f"  M5 couples: {'PASS' if m5_c['pass'] else 'FAIL'}")

    # M6 (couples only, documented)
    m6_c = check_m6_partner_consistency(v2_c)
    print(f"  M6 couples: DOCUMENTED (frac_identical={m6_c['frac_identical']:.1%})")

    # M7
    m7_s = check_m7_row_count(v2_s, canon_s, expected_rows=167600, expected_hh=1676, is_couples=False)
    m7_c = check_m7_row_count(v2_c, canon_c, expected_rows=257700, expected_hh=2577, is_couples=True)
    print(f"  M7 singles: {'PASS' if m7_s['pass'] else 'FAIL'}")
    print(f"  M7 couples: {'PASS' if m7_c['pass'] else 'FAIL'}")

    # M8 (forensic)
    m8_s = check_m8_forensic(v2_s, canon_s, is_couples=False)
    m8_c = check_m8_forensic(v2_c, canon_c, is_couples=True)
    print(f"  M8 singles: {'PASS' if m8_s['pass'] else 'FAIL'} (value_identical={m8_s['value_identical']}, max_diff={m8_s['max_abs_diff']})")
    print(f"  M8 couples: {'PASS' if m8_c['pass'] else 'FAIL'}")

    # M9 (load compat — reload from disk to confirm file integrity)
    m9_s = check_m9_load_compat(VERSIONED_SINGLES, is_couples=False)
    m9_c = check_m9_load_compat(VERSIONED_COUPLES, is_couples=True)
    print(f"  M9 singles: {'PASS' if m9_s['pass'] else 'FAIL'}")
    print(f"  M9 couples: {'PASS' if m9_c['pass'] else 'FAIL'}")

    # M10 (canonical untouched)
    m10 = check_m10_canonical_untouched(canon_s_mtime_before, canon_c_mtime_before)
    print(f"  M10: {'PASS' if m10['pass'] else 'FAIL'} (singles_unchanged={m10['canonical_singles_unchanged']}, couples_unchanged={m10['canonical_couples_unchanged']})")

    # M11-diag
    m11 = check_m11_diag(v2_s, v2_c)
    print(f"  M11-diag: DOCUMENTED")

    # M12-diag (hard check)
    m12 = check_m12_diag(v2_s, v2_c)
    print(f"  M12-diag: {'PASS' if m12['pass'] else 'FAIL'}")

    # Aggregate checks per parquet (for report writer)
    checks_s = {
        "M1": m1_s, "M2": m2_s, "M3": m3_s, "M4": m4_s, "M5": m5_s,
        "M7": m7_s, "M8": m8_s, "M9": m9_s, "M10": m10,
    }
    checks_c = {
        "M1": m1_c, "M2": m2_c, "M3": m3_c, "M4": m4_c, "M5": m5_c,
        "M6": m6_c, "M7": m7_c, "M8": m8_c, "M9": m9_c,
    }

    print("\n--- Writing report ---")
    write_report(
        checks_s=checks_s, checks_c=checks_c,
        m4d=m4d_combined, m11=m11, m12=m12,
        run_ts=run_ts,
        canon_s_mtime=canon_s_mtime_str, canon_c_mtime=canon_c_mtime_str,
        vs_mtime=vs_mtime, vc_mtime=vc_mtime,
        vs_size=vs_size, vc_size=vc_size,
        canon_s_size=canon_s_size, canon_c_size=canon_c_size,
    )

    # Final verdict
    hard_keys = ["M1", "M2", "M3", "M4", "M5", "M7", "M8", "M9", "M10"]
    all_hard = {**checks_s, **checks_c}
    n_fail = sum(1 for k, v in all_hard.items() if k in hard_keys and v.get("pass") is False)
    m12_ok = bool(m12.get("pass"))
    overall = "PASS" if n_fail == 0 and m12_ok else "FAIL"
    print(f"\n{'='*70}")
    print(f"Overall (M1–M10 + M12-diag): {overall}")
    if n_fail > 0:
        failed = [k for k, v in all_hard.items() if k in hard_keys and v.get("pass") is False]
        print(f"FAILED: {failed}")
    if not m12_ok:
        print(f"M12-diag FAILED: {m12}")
    print("=" * 70)


if __name__ == "__main__":
    main()