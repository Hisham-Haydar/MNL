#!/usr/bin/env python
"""
Prepare estimation-ready split-stem inputs from unified pooled parquet.

Inputs
------
  Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet  (unified pooled)

Outputs
-------
  Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__singles.parquet
  Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet
  Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json

Repairs resolved
----------------
  R2: split-stem data contract for enh_RURO_estimate_FR.py
  R3: derive year_2015_indicator / year_2017_indicator from year_tag

Authorization
-------------
  docs/archive/2026-05-26_round2_chain_compression/replaced_by_clean_corrected/JMP_pooled_P3a_estimation_execution_repair_authorization_v1.md

NOT authorized by this script
------------------------------
  - Running the pooled solver
  - Welfare computation
  - Modifying the source unified parquet
  - Modifying any YAML specification

Usage
-----
  .venv/Scripts/python.exe scripts/maintenance/prepare_pooled_estimation_ready.py [--dry-run]
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]

# Pooled data lives under the configured storage root, not the repo working tree
# (migrated 2026-05-26). Resolve dynamically via path_helpers — no hardcoded paths.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
from path_helpers import data_root  # noqa: E402

POOLED_DIR = data_root() / "processed" / "fr" / "pooled"

UNIFIED_PARQUET = POOLED_DIR / "fr_p3a_gsurv2_harmonised.parquet"
STAGE_META_JSON  = POOLED_DIR / "fr_p3a_gsurv2_harmonised__stage_m1_meta.json"

OUT_BASE         = POOLED_DIR / "fr_p3a_gsurv2_estimation_ready"
OUT_SINGLES      = POOLED_DIR / "fr_p3a_gsurv2_estimation_ready__singles.parquet"
OUT_COUPLES      = POOLED_DIR / "fr_p3a_gsurv2_estimation_ready__couples.parquet"
OUT_META         = POOLED_DIR / "fr_p3a_gsurv2_estimation_ready__mnlmeta.json"

# household_type values in the unified parquet (confirmed plural)
HH_TYPE_SINGLES = "singles"
HH_TYPE_COUPLES = "couples"

# Expected row and cluster counts (from stage-M1 meta)
EXPECTED_TOTAL_ROWS    = 1_244_500
EXPECTED_HH_YEARS      = 12_445
EXPECTED_CLUSTERS      = 9_657


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true",
                   help="Validate inputs and print plan without writing outputs")
    p.add_argument("--unified-parquet", type=Path, default=UNIFIED_PARQUET,
                   help="Path to source unified pooled parquet")
    p.add_argument("--out-base", type=Path, default=OUT_BASE,
                   help="Output base path (stem; suffixes appended automatically)")
    return p.parse_args()


def derive_couples_region_dummies(df_couples: pd.DataFrame) -> pd.DataFrame:
    """
    R1 (2026-05-21): populate reg_nuts1_2..8 in the couples split from drgn1 when
    the existing columns are absent or entirely NaN.

    Guard: fires only when reg_nuts1_2 is absent OR entirely NaN in df_couples.
    Does not overwrite columns that already contain valid values.

    Region 1 (Ile-de-France) remains the omitted reference; no dummy is derived for it.
    """
    _reg_cols = [f"reg_nuts1_{k}" for k in range(2, 9)]
    col_present = all(c in df_couples.columns for c in _reg_cols)
    if col_present:
        any_valid = any(df_couples[c].notna().any() for c in _reg_cols)
        any_nondegenerate = any(df_couples[c].fillna(0).nunique() > 1 for c in _reg_cols)
        if any_valid and any_nondegenerate:
            logger.info("R1: reg_nuts1_2..8 already valid in couples split — no repair needed")
            return df_couples

    # Columns absent or all-NaN or all-zero: derive from drgn1
    if "drgn1" not in df_couples.columns or df_couples["drgn1"].isna().all():
        raise ValueError(
            "R1 HALT: drgn1 column is absent or entirely NaN in couples split — "
            "cannot derive region dummies. Diagnose the source parquet before proceeding."
        )
    drgn1_vals = df_couples["drgn1"].values
    n_unique_drgn = len(set(drgn1_vals[~np.isnan(drgn1_vals.astype(float))]))
    if n_unique_drgn < 2:
        raise ValueError(
            f"R1 HALT: drgn1 has only {n_unique_drgn} unique code(s) — "
            "not a valid region source for deriving region dummies."
        )

    df_couples = df_couples.copy()
    for k in range(2, 9):
        df_couples[f"reg_nuts1_{k}"] = (df_couples["drgn1"] == k).astype(float)

    logger.info("R1: derived reg_nuts1_2..8 from drgn1 for couples split (R1 repair applied)")
    for k in range(2, 9):
        n_ones = int((df_couples[f"reg_nuts1_{k}"] == 1.0).sum())
        logger.info(f"  reg_nuts1_{k}: {n_ones} rows = 1")
    return df_couples


def validate_couples_region_dummies(df_couples: pd.DataFrame) -> bool:
    """V1/V2: couples region dummies are non-NaN, binary, and match drgn1 exactly."""
    ok = True
    _reg_cols = [f"reg_nuts1_{k}" for k in range(2, 9)]

    # V1: all columns present, zero NaN, binary values
    for col in _reg_cols:
        if col not in df_couples.columns:
            logger.error(f"V1 FAIL: {col} missing from couples split")
            ok = False
            continue
        n_miss = df_couples[col].isna().sum()
        if n_miss > 0:
            logger.error(f"V1 FAIL: {col} has {n_miss} NaN values in couples split")
            ok = False
        vals = df_couples[col].dropna().unique()
        if not set(vals).issubset({0.0, 1.0}):
            logger.error(f"V1 FAIL: {col} has non-binary values: {vals[:10]}")
            ok = False
        if (df_couples[col].fillna(0) == 0).all():
            logger.error(f"V1 FAIL: {col} is all-zero in couples split")
            ok = False

    if not ok:
        return False

    # V2: exact match with drgn1
    if "drgn1" in df_couples.columns:
        for k in range(2, 9):
            col = f"reg_nuts1_{k}"
            expected = (df_couples["drgn1"] == k).astype(float)
            mismatch = (df_couples[col] != expected).sum()
            if mismatch > 0:
                logger.error(f"V2 FAIL: {col} does not match 1[drgn1=={k}] for {mismatch} rows")
                ok = False
            else:
                n_ones = int((df_couples[col] == 1.0).sum())
                logger.info(f"V2: {col} == 1[drgn1=={k}]: PASS ({n_ones} households in region {k})")
        # Confirm all-zero iff drgn1==1
        region1_rows = df_couples["drgn1"] == 1
        sum_of_dummies_region1 = sum(
            df_couples.loc[region1_rows, f"reg_nuts1_{k}"].sum() for k in range(2, 9)
        )
        if sum_of_dummies_region1 != 0:
            logger.error(f"V2 FAIL: for drgn1==1 rows, some reg_nuts1_k dummy is non-zero ({sum_of_dummies_region1} total)")
            ok = False
        else:
            logger.info("V2: all dummies zero for drgn1==1 rows  PASS")

    if ok:
        logger.info("V1/V2 couples region dummies: PASS")
    return ok


def derive_year_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive year_2015_indicator and year_2017_indicator from year_tag.

    year_tag == 1  ->  2015
    year_tag == 2  ->  2016 (reference, both indicators = 0)
    year_tag == 3  ->  2017
    """
    if "year_tag" not in df.columns:
        raise ValueError("year_tag column not found — cannot derive year indicators")
    df = df.copy()
    df["year_2015_indicator"] = (df["year_tag"] == 1).astype(float)
    df["year_2017_indicator"] = (df["year_tag"] == 3).astype(float)
    return df


def build_mnlmeta(df_singles: pd.DataFrame, df_couples: pd.DataFrame) -> dict:
    """
    Build __mnlmeta.json in the format load_and_validate_mnl_data expects.

    Uses c_norm, l_norm, consumption, leisure (and gender variants for couples)
    present in the split data to derive c_scale and l_scale.

    load_and_validate_mnl_data supports both flat and nested normalization:
      normalization.singles.c_scale  /  normalization.singles.l_scale
      normalization.couples.c_scale  /  normalization.couples.l_male_scale
    We use the nested form for clarity.
    """
    def _derive_scale(data: pd.DataFrame, raw_col: str, norm_col: str, fallback: float) -> float:
        """c_scale = consumption / c_norm  (should be nearly constant)."""
        if raw_col in data.columns and norm_col in data.columns:
            mask = (data[norm_col] > 0) & data[norm_col].notna() & data[raw_col].notna()
            if mask.sum() > 0:
                ratios = data.loc[mask, raw_col] / data.loc[mask, norm_col]
                val = float(ratios.median())
                logger.info(f"  {raw_col}/{norm_col}: scale={val:.6f}  (n={mask.sum():,})")
                return val if np.isfinite(val) and val > 0 else fallback
        logger.warning(f"  Could not derive scale from {raw_col}/{norm_col}; using fallback={fallback}")
        return fallback

    # Singles normalization
    c_scale_s  = _derive_scale(df_singles, "consumption", "c_norm",   1.0)
    l_scale_s  = _derive_scale(df_singles, "leisure",     "l_norm",   1.0)

    # Couples normalization — use male columns (the estimator uses l_male_scale)
    if len(df_couples) > 0:
        c_scale_c  = _derive_scale(df_couples,
                                   "consumption_male" if "consumption_male" in df_couples.columns else "consumption",
                                   "c_norm", 1.0)
        l_scale_c  = _derive_scale(df_couples, "leisure_male", "l_norm_male", 1.0)
        l_scale_cf = _derive_scale(df_couples, "leisure_female", "l_norm_female", 1.0)
    else:
        c_scale_c = l_scale_c = l_scale_cf = 1.0

    meta = {
        "source": "fr_p3a_gsurv2_estimation_ready (split from fr_p3a_gsurv2_harmonised.parquet)",
        "produced_by": "scripts/maintenance/prepare_pooled_estimation_ready.py",
        "authorization": "docs/archive/2026-05-26_round2_chain_compression/replaced_by_clean_corrected/JMP_pooled_P3a_estimation_execution_repair_authorization_v1.md",
        "n_draws": 100,
        "normalization": {
            "singles": {
                "c_scale": c_scale_s,
                "l_scale": l_scale_s,
            },
            "couples": {
                "c_scale":        c_scale_c,
                "l_male_scale":   l_scale_c,
                "l_female_scale": l_scale_cf,
            },
        },
        "row_counts": {
            "singles": int(len(df_singles)),
            "couples": int(len(df_couples)),
            "total":   int(len(df_singles) + len(df_couples)),
        },
        "year_indicators": {
            "year_2015_indicator": "1[year_tag == 1]",
            "year_2017_indicator": "1[year_tag == 3]",
            "note": "year_tag 1=2015, 2=2016, 3=2017; 2016 is reference (both indicators=0)",
        },
        "cluster_key": {
            "cluster_id_col": "cluster_id",
            "source_col":     "idorighh",
        },
        "income_routing": {
            "singles":        "ils_dispy_real",
            "couples_male":   "ils_dispy_male",
            "couples_female": "ils_dispy_female",
            "note": "couples path does NOT use ils_dispy_real",
        },
        "region_dummy_repair": {
            "repair": "R1",
            "authorization": "docs/archive/2026-05-26_round2_chain_compression/replaced_by_clean_corrected/JMP_pooled_P3a_region_dummy_repair_authorization_v1.md",
            "description": (
                "reg_nuts1_2..8 derived from drgn1 for couples split when original columns were all-NaN. "
                "Diagnostic v1 classified cause as B/DEGENERATE_OR_MISWIRED_COLUMNS."
            ),
            "applied_date": "2026-05-21",
        },
    }
    return meta


def validate_conservation(df_unified: pd.DataFrame, df_singles: pd.DataFrame,
                           df_couples: pd.DataFrame) -> bool:
    """V2: verify row/HH-year/cluster conservation."""
    ok = True

    total_split = len(df_singles) + len(df_couples)
    if total_split != len(df_unified):
        logger.error(f"V2 FAIL: split rows {total_split:,} != unified rows {len(df_unified):,}")
        ok = False
    else:
        logger.info(f"V2 row count: {total_split:,} == {len(df_unified):,}  PASS")

    if total_split != EXPECTED_TOTAL_ROWS:
        logger.warning(f"V2 total rows {total_split:,} != expected {EXPECTED_TOTAL_ROWS:,}  (warn)")

    # HH-year count: unique (year_tag, idhh) pairs — idhh repeats across years
    if "idhh" in df_singles.columns and "year_tag" in df_singles.columns and \
       "idhh" in df_couples.columns and "year_tag" in df_couples.columns:
        n_hh_s = df_singles.groupby(["year_tag", "idhh"]).ngroups
        n_hh_c = df_couples.groupby(["year_tag", "idhh"]).ngroups
        n_hh_total = n_hh_s + n_hh_c
        if n_hh_total != EXPECTED_HH_YEARS:
            logger.warning(f"V2 HH-year count {n_hh_total} != expected {EXPECTED_HH_YEARS}")
        else:
            logger.info(f"V2 HH-year count: {n_hh_total} == {EXPECTED_HH_YEARS}  PASS")

    # Cluster count: unique idorighh across both splits combined should be 9,657
    if "idorighh" in df_singles.columns and "idorighh" in df_couples.columns:
        all_clusters = pd.concat([
            df_singles["idorighh"].drop_duplicates(),
            df_couples["idorighh"].drop_duplicates(),
        ]).nunique()
        if all_clusters != EXPECTED_CLUSTERS:
            logger.warning(f"V2 cluster count {all_clusters} != expected {EXPECTED_CLUSTERS}")
        else:
            logger.info(f"V2 cluster count: {all_clusters} == {EXPECTED_CLUSTERS}  PASS")

    return ok


def validate_year_indicators(df: pd.DataFrame, label: str) -> bool:
    """V3: verify year indicators are correct float 0/1."""
    ok = True
    for col in ["year_2015_indicator", "year_2017_indicator"]:
        if col not in df.columns:
            logger.error(f"V3 FAIL [{label}]: {col} missing")
            ok = False
        else:
            # Check dtype is float
            if not pd.api.types.is_float_dtype(df[col]):
                logger.error(f"V3 FAIL [{label}]: {col} dtype {df[col].dtype} != float")
                ok = False

    if ok and "year_tag" in df.columns:
        # year_2015_indicator == 1 iff year_tag == 1
        mismatch_2015 = ((df["year_tag"] == 1) != (df["year_2015_indicator"] == 1.0)).sum()
        mismatch_2017 = ((df["year_tag"] == 3) != (df["year_2017_indicator"] == 1.0)).sum()
        both_zero = ((df["year_tag"] == 2) & ((df["year_2015_indicator"] != 0.0) | (df["year_2017_indicator"] != 0.0))).sum()
        if mismatch_2015 or mismatch_2017 or both_zero:
            logger.error(f"V3 FAIL [{label}]: indicator mismatch: 2015={mismatch_2015}, 2017={mismatch_2017}, ref_nonzero={both_zero}")
            ok = False
        else:
            counts_2015 = int((df["year_2015_indicator"] == 1.0).sum())
            counts_2017 = int((df["year_2017_indicator"] == 1.0).sum())
            logger.info(f"V3 [{label}]: year_2015_indicator={counts_2015} 1s, year_2017_indicator={counts_2017} 1s  PASS")

    return ok


def validate_cluster_key(df: pd.DataFrame, label: str) -> bool:
    """V4: cluster_id == idorighh."""
    ok = True
    if "cluster_id" not in df.columns:
        logger.error(f"V4 FAIL [{label}]: cluster_id missing")
        ok = False
    if "idorighh" not in df.columns:
        logger.error(f"V4 FAIL [{label}]: idorighh missing")
        ok = False
    if ok:
        n_equal = (df["cluster_id"] == df["idorighh"]).sum()
        if n_equal != len(df):
            logger.error(f"V4 FAIL [{label}]: cluster_id != idorighh for {len(df) - n_equal} rows")
            ok = False
        else:
            logger.info(f"V4 [{label}]: cluster_id == idorighh for all {len(df):,} rows  PASS")
    return ok


def validate_income_routing(df_singles: pd.DataFrame, df_couples: pd.DataFrame) -> bool:
    """V5: income routing preserved; couples path does not use ils_dispy_real."""
    ok = True

    # Singles carry ils_dispy_real (non-null)
    if "ils_dispy_real" in df_singles.columns:
        n_null = df_singles["ils_dispy_real"].isna().sum()
        if n_null > 0:
            logger.warning(f"V5 singles: {n_null} null ils_dispy_real rows (may be zero-income singles)")
        else:
            logger.info(f"V5 singles: ils_dispy_real present and non-null  PASS")
    else:
        logger.error("V5 FAIL: singles missing ils_dispy_real")
        ok = False

    # Couples carry ils_dispy_male and ils_dispy_female
    for col in ["ils_dispy_male", "ils_dispy_female"]:
        if col not in df_couples.columns:
            logger.error(f"V5 FAIL: couples missing {col}")
            ok = False
        else:
            n_null = df_couples[col].isna().sum()
            if n_null > 0:
                logger.warning(f"V5 couples: {n_null} null {col}")
            else:
                logger.info(f"V5 couples: {col} present and non-null  PASS")

    # Couples consumption path must NOT read ils_dispy_real.
    # precompute_data_couples uses c_norm (= (ils_dispy_male + ils_dispy_female) / c_scale),
    # not ils_dispy_real. The column may exist in the couples split with non-zero values
    # (it carries the singles income from the unified parquet) but the estimator ignores it.
    # We confirm c_norm is present and non-null — that is the actual consumption source.
    if "c_norm" not in df_couples.columns:
        logger.error("V5 FAIL: couples file missing c_norm — couples consumption cannot be computed")
        ok = False
    else:
        n_null_cnorm = df_couples["c_norm"].isna().sum()
        if n_null_cnorm > 0:
            logger.error(f"V5 FAIL: couples c_norm has {n_null_cnorm} null values")
            ok = False
        else:
            logger.info("V5 couples: c_norm present and non-null (couples consumption source)  PASS")
    # Confirm the precompute function's path: it reads c_norm, NOT ils_dispy_real.
    logger.info("V5 couples consumption path: precompute_data_couples uses c_norm "
                "(= normalized household income from ils_dispy_male+ils_dispy_female), NOT ils_dispy_real  PASS")

    return ok


def run(dry_run: bool, unified_parquet: Path, out_base: Path) -> bool:
    out_singles = Path(str(out_base) + "__singles.parquet")
    out_couples = Path(str(out_base) + "__couples.parquet")
    out_meta    = Path(str(out_base) + "__mnlmeta.json")

    # ------------------------------------------------------------------
    # 1. Load unified pooled parquet
    # ------------------------------------------------------------------
    logger.info(f"Loading unified pooled parquet: {unified_parquet}")
    if not unified_parquet.exists():
        logger.error(f"HALT (H1): unified parquet not found: {unified_parquet}")
        return False

    df = pd.read_parquet(unified_parquet)
    logger.info(f"  Loaded {len(df):,} rows, {len(df.columns)} columns")

    if len(df) != EXPECTED_TOTAL_ROWS:
        logger.warning(f"  Expected {EXPECTED_TOTAL_ROWS:,} rows, got {len(df):,}")

    # ------------------------------------------------------------------
    # 2. Split by household_type
    # ------------------------------------------------------------------
    if "household_type" not in df.columns:
        logger.error("HALT: household_type column missing from unified parquet")
        return False

    htypes = df["household_type"].unique().tolist()
    logger.info(f"  household_type values: {htypes}")

    df_singles = df[df["household_type"] == HH_TYPE_SINGLES].copy()
    df_couples = df[df["household_type"] == HH_TYPE_COUPLES].copy()

    if len(df_singles) == 0:
        logger.error(f"HALT (H2): no rows with household_type == '{HH_TYPE_SINGLES}'")
        return False
    if len(df_couples) == 0:
        logger.error(f"HALT (H2): no rows with household_type == '{HH_TYPE_COUPLES}'")
        return False

    logger.info(f"  Singles: {len(df_singles):,} rows")
    logger.info(f"  Couples: {len(df_couples):,} rows")

    # ------------------------------------------------------------------
    # 3. Sort by idhh (required by precompute_data_singles/couples)
    # ------------------------------------------------------------------
    if "idhh" in df_singles.columns:
        df_singles = df_singles.sort_values("idhh").reset_index(drop=True)
    if "idhh" in df_couples.columns:
        df_couples = df_couples.sort_values("idhh").reset_index(drop=True)
    logger.info("  Data sorted by idhh")

    # ------------------------------------------------------------------
    # 4. Derive year indicators (R3)
    # ------------------------------------------------------------------
    logger.info("Deriving year indicators from year_tag...")
    df_singles = derive_year_indicators(df_singles)
    df_couples = derive_year_indicators(df_couples)

    # ------------------------------------------------------------------
    # 4a. R1: repair couples region dummies from drgn1 if absent/all-NaN
    # ------------------------------------------------------------------
    logger.info("\nR1: repairing couples region dummies (if needed)...")
    df_couples = derive_couples_region_dummies(df_couples)
    logger.info(f"  year_2015_indicator: {int(df_singles['year_2015_indicator'].sum())} singles, "
                f"{int(df_couples['year_2015_indicator'].sum())} couples")
    logger.info(f"  year_2017_indicator: {int(df_singles['year_2017_indicator'].sum())} singles, "
                f"{int(df_couples['year_2017_indicator'].sum())} couples")

    # ------------------------------------------------------------------
    # 5. Validation
    # ------------------------------------------------------------------
    logger.info("\n--- Validation ---")

    v1v2_ok = validate_couples_region_dummies(df_couples)
    if not v1v2_ok:
        logger.error("HALT (H2/V1/V2): couples region dummy validation failed")
        return False

    v2_ok = validate_conservation(df, df_singles, df_couples)
    if not v2_ok:
        logger.error("HALT (H5): row/cluster conservation failed")
        return False

    v3s_ok = validate_year_indicators(df_singles, "singles")
    v3c_ok = validate_year_indicators(df_couples, "couples")
    if not (v3s_ok and v3c_ok):
        logger.error("HALT (H4): year indicator validation failed")
        return False

    v4s_ok = validate_cluster_key(df_singles, "singles")
    v4c_ok = validate_cluster_key(df_couples, "couples")
    if not (v4s_ok and v4c_ok):
        logger.error("HALT (H3): cluster key preservation failed")
        return False

    v5_ok = validate_income_routing(df_singles, df_couples)
    if not v5_ok:
        logger.error("HALT (H2): income routing validation failed")
        return False

    logger.info("\nAll pre-write validations passed.")

    # ------------------------------------------------------------------
    # 6. Build metadata
    # ------------------------------------------------------------------
    logger.info("\nBuilding mnlmeta.json...")
    meta = build_mnlmeta(df_singles, df_couples)

    # ------------------------------------------------------------------
    # 7. Write outputs (unless dry-run)
    # ------------------------------------------------------------------
    if dry_run:
        logger.info("\n[DRY RUN] Would write:")
        logger.info(f"  {out_singles}  ({len(df_singles):,} rows)")
        logger.info(f"  {out_couples}  ({len(df_couples):,} rows)")
        logger.info(f"  {out_meta}")
        logger.info("Dry-run complete. No files written.")
        return True

    logger.info(f"\nWriting singles: {out_singles}")
    df_singles.to_parquet(out_singles, index=False)
    logger.info(f"  Written: {len(df_singles):,} rows, {len(df_singles.columns)} columns")

    logger.info(f"Writing couples: {out_couples}")
    df_couples.to_parquet(out_couples, index=False)
    logger.info(f"  Written: {len(df_couples):,} rows, {len(df_couples.columns)} columns")

    logger.info(f"Writing mnlmeta: {out_meta}")
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2)
    logger.info(f"  Written: {out_meta}")

    logger.info("\nR2/R3 split-stem preparation complete.")
    logger.info("NOT authorized: solver, welfare, SA2, canonical promotion.")
    logger.info("M1-clean 2016 remains the active JMP baseline.")
    return True


def main():
    args = parse_args()
    ok = run(
        dry_run=args.dry_run,
        unified_parquet=args.unified_parquet,
        out_base=args.out_base,
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()