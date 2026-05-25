#!/usr/bin/env python
"""
NC pilot — Stages 3 + 4 driver: build 30x30 product alternatives for 2016
couples; write pilot parquet + metadata.

Authorized by: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_stage1_4_scope_amendment_v1.md (Stages 3-4).

Hard scope:
  - 2016 couples ONLY (year_tag == 2), product 30x30 = 900 alts/couple
  - Output: 2,577 * 900 = 2,319,300 rows
  - W1 wages applied to working alternatives (loc4 in {1..4}) using
    calibrated Mincer coefficients from
    scripts/pilot/config/pilot_mincer_coefficients_v1.json
  - occ_spec="fixed" retained: simulated loc4 = observed loc4 per partner
  - Singles parquet NOT touched
  - No EUROMOD, no GSUR, no MNL estimation-ready stack rebuild
  - Disposable-income columns (ils_dispy_*) are NOT populated for product
    alternatives at this stage; they will be set by EUROMOD in a later
    slice. The pilot parquet at this stage is a CHOICE-SET SCAFFOLD with
    regenerated wage draws.

Hard halts:
  HP3 — exactly one draw_joint==0 row per couple; is_chosen_male ==
        is_chosen_female on that row
  HP9 — row count must equal 2_577 * 900 = 2_319_300

This driver does NOT modify production files. The pilot wage draw is
imported from scripts/pilot/pilot_wage_draw.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
POOLED = REPO / "Data" / "processed" / "fr" / "pooled"
COUPLES_SRC = POOLED / "fr_p3a_gsurv2_estimation_ready__couples.parquet"
SINGLES_SRC = POOLED / "fr_p3a_gsurv2_estimation_ready__singles.parquet"
MINCER_CONFIG = REPO / "scripts" / "pilot" / "config" / "pilot_mincer_coefficients_v1.json"
PILOT_DATA_DIR = REPO / "Data" / "pilot" / "nc_2016_couples"
OUT_PARQUET = PILOT_DATA_DIR / "fr_pilot_nc_2016_couples_product.parquet"
OUT_META = PILOT_DATA_DIR / "fr_pilot_nc_2016_couples_product__mnlmeta.json"

# Import pilot wage module
sys.path.insert(0, str(REPO / "scripts" / "pilot"))
from pilot_wage_draw import draw_pilot_wages, lockstep_sanity_check  # noqa: E402

YEAR_TAG_2016 = 2
PRODUCT_SIZE = 30  # 30 male x 30 female = 900
N_DRAWS_JOINT = PRODUCT_SIZE * PRODUCT_SIZE
EXPECTED_COUPLES_2016 = 2577
EXPECTED_ROWS = EXPECTED_COUPLES_2016 * N_DRAWS_JOINT  # 2_319_300

PILOT_SEED = 20260522  # couples pilot seed (couples = singles + 1 if singles seed is 20260521)


def _load_couples_2016() -> pd.DataFrame:
    """Read 2016 couples from production parquet (read-only). All columns needed
    for the product scaffold (preserve partner-specific and household vars)."""
    df = pd.read_parquet(COUPLES_SRC)
    df = df[df["year_tag"] == YEAR_TAG_2016].copy()
    print(f"[stage-3] couples 2016 rows from production parquet: {len(df):,}")
    # Sanity: production data is wide; one row per (idhh, draw). draw in 0..99
    n_couples_obs = int(df.loc[df["draw"] == 0, "idhh"].nunique())
    print(f"[stage-3] 2016 unique couple households (idhh) at draw=0: {n_couples_obs:,}")
    if n_couples_obs != EXPECTED_COUPLES_2016:
        raise RuntimeError(
            f"HP9 pre-check: 2016 couples count {n_couples_obs} != "
            f"expected {EXPECTED_COUPLES_2016}"
        )
    return df


def _verify_singles_unchanged() -> int:
    """HP9: singles production parquet row count must be unchanged at 500,700."""
    import pyarrow.parquet as pq
    n = pq.read_metadata(SINGLES_SRC).num_rows
    if n != 500_700:
        raise RuntimeError(f"HP9: singles row count {n} != 500,700 (production drift!)")
    print(f"[stage-3] singles production parquet rows confirmed: {n:,} (unchanged)")
    return n


def _build_product(df_diag: pd.DataFrame) -> pd.DataFrame:
    """
    Stage 3: replace the diagonal pairing with a 30x30 product over the first 30
    male and 30 female marginal draws.

    Input df_diag: production diagonal wide couples 2016 — one row per (idhh,
    draw) with _male and _female columns side by side. draw in 0..99 (we use
    0..29).

    Construction:
      male_side   = df_diag[df_diag["draw"] < 30] keeping male-side columns
      female_side = df_diag[df_diag["draw"] < 30] keeping female-side columns
      product     = male_side.merge(female_side, on="idhh", how="inner")
                       producing draw_male in 0..29, draw_female in 0..29
      draw_joint  = 30 * draw_male + draw_female

    The chosen row is (draw_male==0 AND draw_female==0) <=> draw_joint == 0.
    The existing is_chosen column from production refers to (draw==0) and is
    NOT directly meaningful in the product. We construct is_chosen_male and
    is_chosen_female from draw_male / draw_female respectively.
    """
    # Restrict to first 30 marginal draws per partner
    df30 = df_diag[df_diag["draw"] < PRODUCT_SIZE].copy()
    if df30["draw"].nunique() != PRODUCT_SIZE:
        raise RuntimeError(
            f"[stage-3] expected {PRODUCT_SIZE} distinct draws 0..{PRODUCT_SIZE-1}; "
            f"got {df30['draw'].nunique()}"
        )

    # Separate male-side and female-side columns. The production parquet is
    # already wide (both _male and _female columns per row); we explode the
    # diagonal into independent male and female marginals first.

    # Columns ending in _male — male partner fields; ending in _female —
    # female partner fields; the rest are shared/household.
    all_cols = df30.columns.tolist()
    male_cols = [c for c in all_cols if c.endswith("_male")]
    female_cols = [c for c in all_cols if c.endswith("_female")]
    # Avoid colliding renamed columns (paranoia)
    shared_cols = [c for c in all_cols
                   if c not in male_cols and c not in female_cols
                   and c not in {"draw", "is_chosen", "chosen", "idhh"}]

    # MALE-side dataframe with draw_male and all shared (household) columns
    male_side = df30[["idhh", "draw"] + male_cols + shared_cols].rename(columns={"draw": "draw_male"})
    # FEMALE-side dataframe with draw_female (only female-side fields; shared
    # columns live on the male side to avoid duplicate columns after merge)
    female_side = df30[["idhh", "draw"] + female_cols].rename(columns={"draw": "draw_female"})

    print(f"[stage-3] male-side rows (draws 0..{PRODUCT_SIZE-1}): {len(male_side):,}")
    print(f"[stage-3] female-side rows (draws 0..{PRODUCT_SIZE-1}): {len(female_side):,}")

    # 30 x 30 cross-join on idhh
    product = male_side.merge(female_side, on="idhh", how="inner",
                              suffixes=("", "_F_DUP"))
    if any(c.endswith("_F_DUP") for c in product.columns):
        dup_cols = [c for c in product.columns if c.endswith("_F_DUP")]
        raise RuntimeError(f"[stage-3] unexpected duplicate columns after merge: {dup_cols}")
    product["draw_joint"] = PRODUCT_SIZE * product["draw_male"].astype(np.int32) \
                          + product["draw_female"].astype(np.int32)
    # Chosen flags from joint indices
    product["is_chosen_male"] = (product["draw_male"] == 0).astype(np.int8)
    product["is_chosen_female"] = (product["draw_female"] == 0).astype(np.int8)
    product["is_chosen_joint"] = ((product["draw_male"] == 0) & (product["draw_female"] == 0)).astype(np.int8)
    # Drop the legacy single-integer "draw" column to avoid confusion;
    # downstream code that needs a single index reads draw_joint.
    # (Listed in promotion-debt / re-pointing surface in the build report.)

    return product


def _apply_W1_wages(product: pd.DataFrame, mincer: dict, seed: int) -> dict[str, str | float | int]:
    """
    Stage 2 application: replace wage_male / wage_female on NON-CHOSEN working
    alternatives (draw_male > 0 or draw_female > 0) with W1 log-normal draws
    conditional on the partner's observed loc4. Chosen row (draw_joint==0)
    retains observed wages.

    occ_spec="fixed" is RESPECTED: each partner's simulated loc4 in this
    product equals the partner's OBSERVED loc4 (carried through the diagonal
    parquet from draw=0 by production code). We do not resample loc4.

    Also computes log_q_wage_male / log_q_wage_female via the matching
    log-normal density (HP2 lockstep). Existing log_q_wage_male/female columns
    from production (uniform proposal) are overwritten in the pilot parquet
    where the wage has been redrawn; on chosen rows we set log_q to 0 (the
    observed alternative is not sampled).
    """
    # Working alternatives = loc4 in {1,2,3,4} and wage > 0 in observed.
    # Under occ_spec=fixed and pilot wage draw, working status follows the
    # partner's observed working status (the production marginal builder
    # already encodes non-employment as wage=0/loc4=-1 in draws). For the
    # 2016 couples wide parquet, the carried partner loc4 IS the observed
    # loc4 in every draw row. We treat (loc4 in {1..4}) as working.

    # ---- Male wage redraw (skip chosen draw_male==0)
    male_mask = (product["loc4_male"].isin([1, 2, 3, 4])) & (product["draw_male"] > 0)
    n_male = int(male_mask.sum())
    if n_male:
        sub = product.loc[male_mask]
        out_m = draw_pilot_wages(
            n=n_male,
            educL=sub["educL_male"].to_numpy(dtype=float),
            educH=sub["educH_male"].to_numpy(dtype=float),
            pexp_years=sub["pexp_years_male"].to_numpy(dtype=float),
            pexp_years2=sub["pexp_years2_male"].to_numpy(dtype=float),
            loc4=sub["loc4_male"].to_numpy(dtype=np.int32),
            year_tag=sub["year_tag"].to_numpy(dtype=np.int32),
            mincer_payload=mincer, seed=seed, draw_method="halton",
        )
        product.loc[male_mask, "wage_male"] = out_m["wage"]
        product.loc[male_mask, "log_q_wage_male_pilot"] = out_m["log_q_wage"]
        method_male = out_m["method"]
    else:
        method_male = "n/a"

    # ---- Female wage redraw (skip chosen draw_female==0)
    female_mask = (product["loc4_female"].isin([1, 2, 3, 4])) & (product["draw_female"] > 0)
    n_female = int(female_mask.sum())
    if n_female:
        sub = product.loc[female_mask]
        out_f = draw_pilot_wages(
            n=n_female,
            educL=sub["educL_female"].to_numpy(dtype=float),
            educH=sub["educH_female"].to_numpy(dtype=float),
            pexp_years=sub["pexp_years_female"].to_numpy(dtype=float),
            pexp_years2=sub["pexp_years2_female"].to_numpy(dtype=float),
            loc4=sub["loc4_female"].to_numpy(dtype=np.int32),
            year_tag=sub["year_tag"].to_numpy(dtype=np.int32),
            mincer_payload=mincer, seed=seed + 1, draw_method="halton",
        )
        product.loc[female_mask, "wage_female"] = out_f["wage"]
        product.loc[female_mask, "log_q_wage_female_pilot"] = out_f["log_q_wage"]
        method_female = out_f["method"]
    else:
        method_female = "n/a"

    # Chosen rows: log_q_wage_*_pilot = 0 (observed; not sampled)
    product["log_q_wage_male_pilot"] = product["log_q_wage_male_pilot"].fillna(0.0)
    product["log_q_wage_female_pilot"] = product["log_q_wage_female_pilot"].fillna(0.0)

    return {
        "n_male_redrawn": n_male,
        "n_female_redrawn": n_female,
        "method_male": method_male,
        "method_female": method_female,
        "seed_male": seed,
        "seed_female": seed + 1,
        "sigma": float(mincer["wage_model_W1"]["sigma"]),
    }


def _stage4_invariants(product: pd.DataFrame) -> dict[str, int]:
    """HP3 + HP9 invariants on the pilot parquet."""
    rows = len(product)
    n_couples = product["idhh"].nunique()
    # Exactly one draw_joint==0 row per couple
    chosen = product[product["draw_joint"] == 0]
    n_chosen_rows = len(chosen)
    n_distinct_chosen_couples = chosen["idhh"].nunique()
    # is_chosen consistency on chosen row
    consistent_on_chosen = bool((chosen["is_chosen_male"] == chosen["is_chosen_female"]).all())

    # draw_male and draw_female value sets
    n_distinct_dm = product["draw_male"].nunique()
    n_distinct_df = product["draw_female"].nunique()
    n_distinct_dj = product["draw_joint"].nunique()

    halts = []
    if rows != EXPECTED_ROWS:
        halts.append(f"HP9: rows {rows:,} != expected {EXPECTED_ROWS:,}")
    if n_couples != EXPECTED_COUPLES_2016:
        halts.append(f"HP9: distinct couples {n_couples} != expected {EXPECTED_COUPLES_2016}")
    if n_distinct_chosen_couples != EXPECTED_COUPLES_2016:
        halts.append(f"HP3: chosen-row couples {n_distinct_chosen_couples} != {EXPECTED_COUPLES_2016}")
    if n_chosen_rows != EXPECTED_COUPLES_2016:
        halts.append(f"HP3: exactly one chosen row per couple expected; got {n_chosen_rows}")
    if not consistent_on_chosen:
        halts.append("HP3: is_chosen_male != is_chosen_female on chosen row")
    if n_distinct_dm != PRODUCT_SIZE or n_distinct_df != PRODUCT_SIZE:
        halts.append(f"HP3: draw_male/draw_female cardinalities ({n_distinct_dm},{n_distinct_df}) != "
                     f"({PRODUCT_SIZE},{PRODUCT_SIZE})")
    if n_distinct_dj != N_DRAWS_JOINT:
        halts.append(f"HP3: draw_joint cardinality {n_distinct_dj} != {N_DRAWS_JOINT}")

    return {
        "rows": rows,
        "n_couples": n_couples,
        "n_chosen_rows": n_chosen_rows,
        "n_distinct_chosen_couples": n_distinct_chosen_couples,
        "consistent_on_chosen": consistent_on_chosen,
        "n_distinct_draw_male": n_distinct_dm,
        "n_distinct_draw_female": n_distinct_df,
        "n_distinct_draw_joint": n_distinct_dj,
        "halts": halts,
    }


def main() -> int:
    if not MINCER_CONFIG.exists():
        print(f"[stage-3] ERROR: Stage-1 Mincer config not found at\n  {MINCER_CONFIG}",
              file=sys.stderr)
        return 2
    with MINCER_CONFIG.open("r", encoding="utf-8") as f:
        mincer = json.load(f)
    print(f"[stage-3] loaded Mincer config (sigma={mincer['wage_model_W1']['sigma']:.4f})")

    n_singles_prod = _verify_singles_unchanged()

    diag = _load_couples_2016()

    # Lockstep sanity (HP2) on a small slice of male partners (draw=0 observed)
    sample = diag.loc[diag["draw"] == 0].head(1024)
    ls = lockstep_sanity_check(
        educL=sample["educL_male"].to_numpy(dtype=float),
        educH=sample["educH_male"].to_numpy(dtype=float),
        pexp_years=sample["pexp_years_male"].to_numpy(dtype=float),
        pexp_years2=sample["pexp_years2_male"].to_numpy(dtype=float),
        loc4=np.where(sample["loc4_male"].isin([1, 2, 3, 4]),
                      sample["loc4_male"], 1).astype(np.int32),
        year_tag=sample["year_tag"].to_numpy(dtype=np.int32),
        mincer_payload=mincer,
    )
    print(f"[stage-2] HP2 lockstep sanity: n={ls['n']}, "
          f"max_abs_diff={ls['max_abs_diff']:.2e}, ok={ls['ok']}")
    if not ls["ok"]:
        raise RuntimeError("HP2 violated: pilot wage draw and log_q are not in lockstep")

    product = _build_product(diag)
    print(f"[stage-3] product rows: {len(product):,} (expected {EXPECTED_ROWS:,})")

    # Initialize pilot log_q columns so chosen rows can be filled to 0
    product["log_q_wage_male_pilot"] = np.nan
    product["log_q_wage_female_pilot"] = np.nan

    # Apply pilot W1 wages on non-chosen alternatives
    wage_report = _apply_W1_wages(product, mincer, seed=PILOT_SEED)
    print(f"[stage-2/3] W1 wages applied: male n={wage_report['n_male_redrawn']:,} "
          f"({wage_report['method_male']}); female n={wage_report['n_female_redrawn']:,} "
          f"({wage_report['method_female']})")

    inv = _stage4_invariants(product)
    print(f"[stage-4] invariants: {inv}")
    if inv["halts"]:
        for h in inv["halts"]:
            print(f"[stage-4] HALT: {h}", file=sys.stderr)
        raise RuntimeError("Stage-4 invariants failed; see HALT lines above")

    # ---- Stage 4: write parquet + metadata
    # Pilot scaffold: drop EUROMOD-dependent disposable income columns that
    # are NOT valid for product alternatives (only observed draw=0 had valid
    # income; the other 899 alts/couple have no EUROMOD output yet).
    income_cols_invalid = [c for c in product.columns
                           if c.startswith(("ils_dispy", "ils_dispy_em",
                                            "i_", "il_", "tu_"))]
    if income_cols_invalid:
        product = product.drop(columns=income_cols_invalid)
        print(f"[stage-4] dropped {len(income_cols_invalid)} EUROMOD-dependent income "
              f"columns (not valid for product alts pre-EUROMOD)")

    PILOT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[stage-4] writing pilot couples parquet:\n  {OUT_PARQUET}")
    product.to_parquet(OUT_PARQUET, index=False, engine="pyarrow", compression="snappy")
    bytes_ = OUT_PARQUET.stat().st_size
    print(f"[stage-4] wrote {bytes_:,} bytes")

    meta = {
        "schema_version": "nc_pilot_couples_product_v1",
        "produced_by": "scripts/pilot/build_pilot_couples_product.py",
        "produced_at_utc": datetime.now(timezone.utc).isoformat(),
        "authorization": "docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_stage1_4_scope_amendment_v1.md (Stages 3-4)",
        "year": 2016,
        "year_tag": YEAR_TAG_2016,
        "country": "FR",
        "household_type": "couples_only",
        "singles_production_rows_unchanged": n_singles_prod,
        "n_couples": EXPECTED_COUPLES_2016,
        "n_draws_per_couple": N_DRAWS_JOINT,
        "product_size": f"{PRODUCT_SIZE}x{PRODUCT_SIZE}",
        "row_count": int(inv["rows"]),
        "expected_row_count": EXPECTED_ROWS,
        "chosen_alternative_convention": {
            "rule": "draw_joint == 0 (equivalent to draw_male == 0 AND draw_female == 0)",
            "n_chosen_rows": int(inv["n_chosen_rows"]),
            "is_chosen_male_eq_female_on_chosen": bool(inv["consistent_on_chosen"]),
        },
        "wage_model": "W1 (occupation-conditioned log-normal); reference loc4 = 1",
        "wage_sigma": float(mincer["wage_model_W1"]["sigma"]),
        "wage_sigma_kind": "common (single scalar)",
        "calibrated_delta_occ": {
            "delta_occ2": mincer["wage_model_W1"]["coef"]["delta_occ2"],
            "delta_occ3": mincer["wage_model_W1"]["coef"]["delta_occ3"],
            "delta_occ4": mincer["wage_model_W1"]["coef"]["delta_occ4"],
            "status": "calibrated, fixed at draw time, NOT free structural parameters",
        },
        "occ_spec": "fixed (partner loc4 = observed loc4 across all 900 alternatives)",
        "partner_dependence_assumption": "conditional independence (product is the correct joint sample)",
        "draw_method": {
            "wage_male": wage_report["method_male"],
            "wage_female": wage_report["method_female"],
            "sequence_preferred": "Halton (scipy.stats.qmc.Halton, scrambled, seeded)",
            "fallback": "PCG64 (numpy.random.default_rng)",
            "seed_male": wage_report["seed_male"],
            "seed_female": wage_report["seed_female"],
            "scramble": True,
        },
        "stage_2_lockstep_HP2": {
            "checked": True,
            "n_sample": int(ls["n"]),
            "max_abs_diff": float(ls["max_abs_diff"]),
            "ok": bool(ls["ok"]),
        },
        "EUROMOD_status": "not_run",
        "GSUR_status": "not_run",
        "precompute_status": "not_run",
        "estimation_status": "not_run",
        "income_columns_dropped": income_cols_invalid,
        "income_columns_dropped_reason": (
            "EUROMOD-dependent disposable income and tax-benefit columns are "
            "NOT valid for product alternatives at the Stage-4 scaffold. They "
            "will be (re-)computed by EUROMOD in a later authorized slice."
        ),
        "downstream_draw_repointing_surface": (
            "Code that previously used `draw == 0` semantics in couples context "
            "must read `draw_joint == 0` (or equivalently draw_male == 0 AND "
            "draw_female == 0) on the pilot parquet. The single integer `draw` "
            "column from production is NOT present in the pilot parquet. "
            "Re-pointing of downstream consumers (precompute, estimation, "
            "post-estimation) is a LATER slice and is not performed here."
        ),
        "promotion_debt": [
            "EXPECTED_COUPLES_2016 = 2577 hard-coded (would parameterize for FR_2015/2017 or other countries)",
            "PRODUCT_SIZE = 30 hard-coded (would parameterize for 20x20 / 40x40 consistency builds)",
            "year_tag mapping {1:2015, 2:2016, 3:2017} consumed; no general year-set abstraction",
            "Mincer fitting set fixed (pooled 2015-2017 singles+couples) by the stage-1 driver",
        ],
    }
    OUT_META.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[stage-4] wrote metadata sidecar:\n  {OUT_META}")
    print(f"[stage-4] DONE.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    _ = ap.parse_args()
    sys.exit(main())
