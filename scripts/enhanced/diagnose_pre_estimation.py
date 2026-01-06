"""
Pre-Estimation Diagnostic Checks for RURO Pipeline

This script performs comprehensive diagnostics on the RURO pipeline outputs
before proceeding to MNL estimation.

Diagnostics:
1. Decider identification quality (hh_IsHead/ruro_decider/lma fallback usage)
2. Worker status consistency (Step 1 is_worker vs Step 4 working draws)
3. EUROMOD input sanity (loc=-1 for non-workers, yem/bun/bsa values)
4. MNL dataset completeness (demographics, wages, GSUR unemployment rates)
5. LMA usage analysis (where lma was used and how it affected results)

Usage:
    python diagnose_pre_estimation.py \\
        --proc-dir "U:/EUROMOD-STORAGE/Data/processed/fr/2016" \\
        --euromod-output "U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016/combined_draws_em.parquet" \\
        --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \\
        --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/diagnostics"
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any

import numpy as np
import pandas as pd


# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],
)


# ============================================================================
# DIAGNOSTIC 1: DECIDER IDENTIFICATION QUALITY
# ============================================================================

def diagnose_decider_identification(
    singles_ruro: pd.DataFrame,
    couples_ruro: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Analyze how deciders were identified in RURO_prep outputs.

    Checks which method was used (priority order):
    1. hh_IsHead/hh_IsPartner (preferred)
    2. ruro_decider (standard)
    3. lma==1 (fallback - should be rare)
    """
    logging.info("=" * 80)
    logging.info("DIAGNOSTIC 1: DECIDER IDENTIFICATION QUALITY")
    logging.info("=" * 80)

    results = {"singles": {}, "couples": {}}

    # Analyze singles
    if singles_ruro is not None and not singles_ruro.empty:
        n_total = len(singles_ruro)

        # Check for hh_IsHead
        has_head = "hh_IsHead" in singles_ruro.columns
        n_heads = (singles_ruro["hh_IsHead"] == 1).sum() if has_head else 0

        # Check for ruro_decider
        has_ruro_decider = "ruro_decider" in singles_ruro.columns
        n_ruro_decider = (singles_ruro["ruro_decider"] == 1).sum() if has_ruro_decider else 0

        # Check for lma
        has_lma = "lma" in singles_ruro.columns
        n_lma = (singles_ruro["lma"] == 1).sum() if has_lma else 0

        results["singles"] = {
            "n_total": n_total,
            "has_hh_IsHead": has_head,
            "n_hh_IsHead": n_heads,
            "pct_hh_IsHead": 100.0 * n_heads / n_total if n_total > 0 else 0,
            "has_ruro_decider": has_ruro_decider,
            "n_ruro_decider": n_ruro_decider,
            "pct_ruro_decider": 100.0 * n_ruro_decider / n_total if n_total > 0 else 0,
            "has_lma": has_lma,
            "n_lma": n_lma,
            "pct_lma": 100.0 * n_lma / n_total if n_total > 0 else 0,
        }

        logging.info(f"Singles (n={n_total:,}):")
        logging.info(f"  hh_IsHead exists: {has_head}")
        if has_head:
            logging.info(f"    └─ {n_heads:,} ({100.0 * n_heads / n_total:.1f}%) flagged as heads")
        logging.info(f"  ruro_decider exists: {has_ruro_decider}")
        if has_ruro_decider:
            logging.info(f"    └─ {n_ruro_decider:,} ({100.0 * n_ruro_decider / n_total:.1f}%) flagged as deciders")
        logging.info(f"  lma exists: {has_lma}")
        if has_lma:
            logging.info(f"    └─ {n_lma:,} ({100.0 * n_lma / n_total:.1f}%) have lma==1")

    # Analyze couples
    if couples_ruro is not None and not couples_ruro.empty:
        n_total = len(couples_ruro)

        # Check for hh_IsHead/hh_IsPartner
        has_head = "hh_IsHead" in couples_ruro.columns
        has_partner = "hh_IsPartner" in couples_ruro.columns
        n_heads = (couples_ruro["hh_IsHead"] == 1).sum() if has_head else 0
        n_partners = (couples_ruro["hh_IsPartner"] == 1).sum() if has_partner else 0
        n_deciders = n_heads + n_partners

        # Check for ruro_decider
        has_ruro_decider = "ruro_decider" in couples_ruro.columns
        n_ruro_decider = (couples_ruro["ruro_decider"] == 1).sum() if has_ruro_decider else 0

        # Check for lma
        has_lma = "lma" in couples_ruro.columns
        n_lma = (couples_ruro["lma"] == 1).sum() if has_lma else 0

        results["couples"] = {
            "n_total": n_total,
            "has_hh_IsHead": has_head,
            "has_hh_IsPartner": has_partner,
            "n_hh_IsHead": n_heads,
            "n_hh_IsPartner": n_partners,
            "n_deciders": n_deciders,
            "pct_deciders": 100.0 * n_deciders / n_total if n_total > 0 else 0,
            "has_ruro_decider": has_ruro_decider,
            "n_ruro_decider": n_ruro_decider,
            "pct_ruro_decider": 100.0 * n_ruro_decider / n_total if n_total > 0 else 0,
            "has_lma": has_lma,
            "n_lma": n_lma,
            "pct_lma": 100.0 * n_lma / n_total if n_total > 0 else 0,
        }

        logging.info(f"\nCouples (n={n_total:,}):")
        logging.info(f"  hh_IsHead exists: {has_head}")
        logging.info(f"  hh_IsPartner exists: {has_partner}")
        if has_head and has_partner:
            logging.info(f"    └─ {n_heads:,} heads + {n_partners:,} partners = {n_deciders:,} ({100.0 * n_deciders / n_total:.1f}%) deciders")
        logging.info(f"  ruro_decider exists: {has_ruro_decider}")
        if has_ruro_decider:
            logging.info(f"    └─ {n_ruro_decider:,} ({100.0 * n_ruro_decider / n_total:.1f}%) flagged as deciders")
        logging.info(f"  lma exists: {has_lma}")
        if has_lma:
            logging.info(f"    └─ {n_lma:,} ({100.0 * n_lma / n_total:.1f}%) have lma==1")

    # Assessment
    logging.info("\n" + "=" * 80)
    logging.info("ASSESSMENT:")
    if results["singles"].get("has_hh_IsHead") or results["couples"].get("has_hh_IsHead"):
        logging.info("✅ hh_IsHead/hh_IsPartner used (PREFERRED method)")
    elif results["singles"].get("has_ruro_decider") or results["couples"].get("has_ruro_decider"):
        logging.info("✅ ruro_decider flag used (STANDARD method)")
    elif results["singles"].get("has_lma") or results["couples"].get("has_lma"):
        logging.warning("⚠️  lma used as fallback for decider identification (UNCOMMON)")
        logging.warning("    This means hh_IsHead/hh_IsPartner and ruro_decider were missing.")
    else:
        logging.error("❌ No decider identification method found!")

    return results


# ============================================================================
# DIAGNOSTIC 2: WORKER STATUS CONSISTENCY
# ============================================================================

def diagnose_worker_consistency(
    singles_ruro: pd.DataFrame,
    couples_ruro: pd.DataFrame,
    singles_draws: pd.DataFrame,
    couples_draws: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Compare baseline is_worker (from Step 1) with actual working draws (Step 4).

    Checks:
    - How many baseline workers (is_worker==1) have hours>0 in their draw==0 (baseline)?
    - How worker status varies across draws
    """
    logging.info("\n" + "=" * 80)
    logging.info("DIAGNOSTIC 2: WORKER STATUS CONSISTENCY")
    logging.info("=" * 80)

    results = {"singles": {}, "couples": {}}

    # Analyze singles
    if singles_ruro is not None and singles_draws is not None:
        # Get baseline is_worker from RURO_ready
        baseline = singles_ruro[["idperson", "is_worker", "lhw"]].copy()
        baseline["is_worker"] = pd.to_numeric(baseline["is_worker"], errors="coerce").fillna(0).astype(int)
        baseline["lhw_baseline"] = pd.to_numeric(baseline["lhw"], errors="coerce").fillna(0.0)

        # Get draw==0 (baseline draw) from draws
        draw0 = singles_draws[singles_draws["draw"] == 0][["idperson", "hours"]].copy()
        draw0["hours_draw0"] = pd.to_numeric(draw0["hours"], errors="coerce").fillna(0.0)

        # Merge
        merged = baseline.merge(draw0, on="idperson", how="inner")

        n_total = len(merged)
        n_is_worker = (merged["is_worker"] == 1).sum()
        n_has_hours = (merged["hours_draw0"] > 0).sum()

        # Consistency check: is_worker==1 should have hours>0 in draw==0
        consistent = (merged["is_worker"] == 1) & (merged["hours_draw0"] > 0)
        n_consistent = consistent.sum()

        # Mismatches
        worker_no_hours = (merged["is_worker"] == 1) & (merged["hours_draw0"] <= 0)
        n_worker_no_hours = worker_no_hours.sum()

        nonworker_has_hours = (merged["is_worker"] == 0) & (merged["hours_draw0"] > 0)
        n_nonworker_has_hours = nonworker_has_hours.sum()

        results["singles"] = {
            "n_total": n_total,
            "n_is_worker": n_is_worker,
            "n_has_hours_draw0": n_has_hours,
            "n_consistent": n_consistent,
            "n_worker_no_hours": n_worker_no_hours,
            "n_nonworker_has_hours": n_nonworker_has_hours,
        }

        logging.info(f"Singles (n={n_total:,}):")
        logging.info(f"  Baseline is_worker==1: {n_is_worker:,} ({100.0 * n_is_worker / n_total:.1f}%)")
        logging.info(f"  Draw==0 hours>0: {n_has_hours:,} ({100.0 * n_has_hours / n_total:.1f}%)")
        logging.info(f"  Consistent (is_worker==1 & hours>0): {n_consistent:,} ({100.0 * n_consistent / n_total:.1f}%)")
        if n_worker_no_hours > 0:
            logging.warning(f"  ⚠️  Workers with hours<=0 in draw==0: {n_worker_no_hours:,} ({100.0 * n_worker_no_hours / n_total:.1f}%)")
        if n_nonworker_has_hours > 0:
            logging.info(f"  Non-workers with hours>0 in draw==0: {n_nonworker_has_hours:,} ({100.0 * n_nonworker_has_hours / n_total:.1f}%)")
            logging.info("    (This is OK - RURO offers hypothetical jobs to non-workers)")

    # Analyze couples (similar logic)
    if couples_ruro is not None and couples_draws is not None:
        # For couples, check deciders only
        baseline = couples_ruro[couples_ruro["ruro_decider"] == 1][["idperson", "is_worker", "lhw"]].copy()
        baseline["is_worker"] = pd.to_numeric(baseline["is_worker"], errors="coerce").fillna(0).astype(int)
        baseline["lhw_baseline"] = pd.to_numeric(baseline["lhw"], errors="coerce").fillna(0.0)

        draw0 = couples_draws[couples_draws["draw"] == 0][["idperson", "hours"]].copy()
        draw0["hours_draw0"] = pd.to_numeric(draw0["hours"], errors="coerce").fillna(0.0)

        merged = baseline.merge(draw0, on="idperson", how="inner")

        n_total = len(merged)
        n_is_worker = (merged["is_worker"] == 1).sum()
        n_has_hours = (merged["hours_draw0"] > 0).sum()

        consistent = (merged["is_worker"] == 1) & (merged["hours_draw0"] > 0)
        n_consistent = consistent.sum()

        worker_no_hours = (merged["is_worker"] == 1) & (merged["hours_draw0"] <= 0)
        n_worker_no_hours = worker_no_hours.sum()

        nonworker_has_hours = (merged["is_worker"] == 0) & (merged["hours_draw0"] > 0)
        n_nonworker_has_hours = nonworker_has_hours.sum()

        results["couples"] = {
            "n_total": n_total,
            "n_is_worker": n_is_worker,
            "n_has_hours_draw0": n_has_hours,
            "n_consistent": n_consistent,
            "n_worker_no_hours": n_worker_no_hours,
            "n_nonworker_has_hours": n_nonworker_has_hours,
        }

        logging.info(f"\nCouples deciders (n={n_total:,}):")
        logging.info(f"  Baseline is_worker==1: {n_is_worker:,} ({100.0 * n_is_worker / n_total:.1f}%)")
        logging.info(f"  Draw==0 hours>0: {n_has_hours:,} ({100.0 * n_has_hours / n_total:.1f}%)")
        logging.info(f"  Consistent (is_worker==1 & hours>0): {n_consistent:,} ({100.0 * n_consistent / n_total:.1f}%)")
        if n_worker_no_hours > 0:
            logging.warning(f"  ⚠️  Workers with hours<=0 in draw==0: {n_worker_no_hours:,} ({100.0 * n_worker_no_hours / n_total:.1f}%)")
        if n_nonworker_has_hours > 0:
            logging.info(f"  Non-workers with hours>0 in draw==0: {n_nonworker_has_hours:,} ({100.0 * n_nonworker_has_hours / n_total:.1f}%)")

    logging.info("\n" + "=" * 80)
    logging.info("ASSESSMENT:")
    singles_ok = results["singles"].get("n_worker_no_hours", 0) == 0
    couples_ok = results["couples"].get("n_worker_no_hours", 0) == 0
    if singles_ok and couples_ok:
        logging.info("✅ All baseline workers (is_worker==1) have hours>0 in draw==0")
    else:
        logging.warning("⚠️  Some baseline workers have hours<=0 in draw==0")
        logging.warning("    This may indicate issues with worker identification or draw generation")

    return results


# ============================================================================
# DIAGNOSTIC 3: EUROMOD INPUT SANITY
# ============================================================================

def diagnose_euromod_inputs(euromod_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Verify EUROMOD input consistency:
    - loc=-1 for non-workers (hours<=0)
    - yem, bun, bsa values are sensible
    """
    logging.info("\n" + "=" * 80)
    logging.info("DIAGNOSTIC 3: EUROMOD INPUT SANITY")
    logging.info("=" * 80)

    results = {}

    # Check loc (occupation) for non-workers
    if "loc" in euromod_df.columns and "hours" in euromod_df.columns:
        hours = pd.to_numeric(euromod_df["hours"], errors="coerce").fillna(0.0)
        loc = pd.to_numeric(euromod_df["loc"], errors="coerce").fillna(np.nan)

        non_workers = hours <= 0
        n_non_workers = non_workers.sum()

        # For non-workers, loc should be -1
        loc_minus1 = loc[non_workers] == -1
        n_loc_correct = loc_minus1.sum()

        results["loc_non_workers"] = {
            "n_non_workers": n_non_workers,
            "n_loc_minus1": n_loc_correct,
            "pct_correct": 100.0 * n_loc_correct / n_non_workers if n_non_workers > 0 else 0,
        }

        logging.info(f"Occupation (loc) for non-workers (hours<=0):")
        logging.info(f"  Non-workers: {n_non_workers:,}")
        logging.info(f"  loc==-1: {n_loc_correct:,} ({100.0 * n_loc_correct / n_non_workers:.1f}%)")

        if n_loc_correct < n_non_workers:
            logging.warning(f"  ⚠️  {n_non_workers - n_loc_correct:,} non-workers have loc!=-1")

    # Check yem (employment income) for workers
    if "yem" in euromod_df.columns and "hours" in euromod_df.columns:
        hours = pd.to_numeric(euromod_df["hours"], errors="coerce").fillna(0.0)
        yem = pd.to_numeric(euromod_df["yem"], errors="coerce").fillna(0.0)

        workers = hours > 0
        n_workers = workers.sum()

        # Workers should have yem > 0
        yem_positive = yem[workers] > 0
        n_yem_positive = yem_positive.sum()

        results["yem_workers"] = {
            "n_workers": n_workers,
            "n_yem_positive": n_yem_positive,
            "pct_positive": 100.0 * n_yem_positive / n_workers if n_workers > 0 else 0,
            "yem_mean": yem[workers].mean(),
            "yem_median": yem[workers].median(),
        }

        logging.info(f"\nEmployment income (yem) for workers (hours>0):")
        logging.info(f"  Workers: {n_workers:,}")
        logging.info(f"  yem>0: {n_yem_positive:,} ({100.0 * n_yem_positive / n_workers:.1f}%)")
        logging.info(f"  yem mean: {yem[workers].mean():.2f}")
        logging.info(f"  yem median: {yem[workers].median():.2f}")

        if n_yem_positive < n_workers:
            logging.warning(f"  ⚠️  {n_workers - n_yem_positive:,} workers have yem<=0")

    # Check bun (unemployment benefits) - should be 0 for workers
    if "bun" in euromod_df.columns and "hours" in euromod_df.columns:
        hours = pd.to_numeric(euromod_df["hours"], errors="coerce").fillna(0.0)
        bun = pd.to_numeric(euromod_df["bun"], errors="coerce").fillna(0.0)

        workers = hours > 0
        n_workers = workers.sum()

        bun_zero = bun[workers] == 0
        n_bun_zero = bun_zero.sum()

        results["bun_workers"] = {
            "n_workers": n_workers,
            "n_bun_zero": n_bun_zero,
            "pct_zero": 100.0 * n_bun_zero / n_workers if n_workers > 0 else 0,
        }

        logging.info(f"\nUnemployment benefits (bun) for workers (hours>0):")
        logging.info(f"  Workers: {n_workers:,}")
        logging.info(f"  bun==0: {n_bun_zero:,} ({100.0 * n_bun_zero / n_workers:.1f}%)")

        if n_bun_zero < n_workers:
            logging.warning(f"  ⚠️  {n_workers - n_bun_zero:,} workers have bun>0 (should be 0)")

    logging.info("\n" + "=" * 80)
    logging.info("ASSESSMENT:")
    all_ok = True
    if results.get("loc_non_workers", {}).get("pct_correct", 0) < 99:
        logging.warning("⚠️  Some non-workers have loc!=-1")
        all_ok = False
    if results.get("yem_workers", {}).get("pct_positive", 0) < 95:
        logging.warning("⚠️  Some workers have yem<=0")
        all_ok = False
    if results.get("bun_workers", {}).get("pct_zero", 0) < 95:
        logging.warning("⚠️  Some workers have bun>0")
        all_ok = False

    if all_ok:
        logging.info("✅ EUROMOD inputs look consistent")

    return results


# ============================================================================
# DIAGNOSTIC 4: MNL DATASET COMPLETENESS
# ============================================================================

def diagnose_mnl_completeness(
    mnl_singles: pd.DataFrame,
    mnl_couples: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Check MNL dataset completeness:
    - Required columns present
    - No missing values in key columns
    - GSUR unemployment rates present
    - Reasonable value ranges
    """
    logging.info("\n" + "=" * 80)
    logging.info("DIAGNOSTIC 4: MNL DATASET COMPLETENESS")
    logging.info("=" * 80)

    results = {"singles": {}, "couples": {}}

    # Required columns
    required_singles = ["idhh", "draw", "consumption", "leisure", "hours", "wage"]
    required_couples = ["idhh", "draw", "consumption", "leisure_male", "leisure_female", "hours_male", "hours_female"]

    # Check singles
    if mnl_singles is not None:
        n_total = len(mnl_singles)
        missing_cols = [col for col in required_singles if col not in mnl_singles.columns]

        # Check for missing values
        missing_counts = {}
        for col in required_singles:
            if col in mnl_singles.columns:
                missing_counts[col] = mnl_singles[col].isna().sum()

        # Check for GSUR (column name is 'gsur', not 'u_rate')
        has_gsur = "gsur" in mnl_singles.columns or "u_rate" in mnl_singles.columns
        gsur_col = "gsur" if "gsur" in mnl_singles.columns else ("u_rate" if "u_rate" in mnl_singles.columns else None)
        if has_gsur and gsur_col:
            n_missing_gsur = mnl_singles[gsur_col].isna().sum()
        else:
            n_missing_gsur = n_total

        results["singles"] = {
            "n_total": n_total,
            "missing_cols": missing_cols,
            "missing_counts": missing_counts,
            "has_gsur": has_gsur,
            "n_missing_gsur": n_missing_gsur,
        }

        logging.info(f"Singles (n={n_total:,}):")
        if missing_cols:
            logging.error(f"  ❌ Missing columns: {missing_cols}")
        else:
            logging.info(f"  ✅ All required columns present")

        for col, count in missing_counts.items():
            if count > 0:
                logging.warning(f"  ⚠️  {col}: {count:,} missing ({100.0 * count / n_total:.1f}%)")
            else:
                logging.info(f"  ✅ {col}: no missing values")

        if has_gsur:
            col_name = gsur_col if gsur_col else "gsur/u_rate"
            if n_missing_gsur > 0:
                logging.warning(f"  ⚠️  GSUR {col_name}: {n_missing_gsur:,} missing ({100.0 * n_missing_gsur / n_total:.1f}%)")
            else:
                logging.info(f"  ✅ GSUR {col_name}: no missing values")
        else:
            logging.error("  ❌ GSUR column (gsur or u_rate) not found!")

    # Check couples
    if mnl_couples is not None:
        n_total = len(mnl_couples)
        missing_cols = [col for col in required_couples if col not in mnl_couples.columns]

        missing_counts = {}
        for col in required_couples:
            if col in mnl_couples.columns:
                missing_counts[col] = mnl_couples[col].isna().sum()

        # Check for GSUR (column names are 'gsur_male'/'gsur_female', not 'u_rate_*')
        has_gsur_new = "gsur_male" in mnl_couples.columns and "gsur_female" in mnl_couples.columns
        has_gsur_old = "u_rate_male" in mnl_couples.columns and "u_rate_female" in mnl_couples.columns
        has_gsur = has_gsur_new or has_gsur_old

        if has_gsur_new:
            n_missing_gsur_male = mnl_couples["gsur_male"].isna().sum()
            n_missing_gsur_female = mnl_couples["gsur_female"].isna().sum()
            gsur_suffix = "gsur"
        elif has_gsur_old:
            n_missing_gsur_male = mnl_couples["u_rate_male"].isna().sum()
            n_missing_gsur_female = mnl_couples["u_rate_female"].isna().sum()
            gsur_suffix = "u_rate"
        else:
            n_missing_gsur_male = n_total
            n_missing_gsur_female = n_total
            gsur_suffix = "gsur"

        results["couples"] = {
            "n_total": n_total,
            "missing_cols": missing_cols,
            "missing_counts": missing_counts,
            "has_gsur": has_gsur,
            "n_missing_gsur_male": n_missing_gsur_male,
            "n_missing_gsur_female": n_missing_gsur_female,
        }

        logging.info(f"\nCouples (n={n_total:,}):")
        if missing_cols:
            logging.error(f"  ❌ Missing columns: {missing_cols}")
        else:
            logging.info(f"  ✅ All required columns present")

        for col, count in missing_counts.items():
            if count > 0:
                logging.warning(f"  ⚠️  {col}: {count:,} missing ({100.0 * count / n_total:.1f}%)")
            else:
                logging.info(f"  ✅ {col}: no missing values")

        if has_gsur:
            if n_missing_gsur_male > 0:
                logging.warning(f"  ⚠️  GSUR {gsur_suffix}_male: {n_missing_gsur_male:,} missing ({100.0 * n_missing_gsur_male / n_total:.1f}%)")
            else:
                logging.info(f"  ✅ GSUR {gsur_suffix}_male: no missing values")

            if n_missing_gsur_female > 0:
                logging.warning(f"  ⚠️  GSUR {gsur_suffix}_female: {n_missing_gsur_female:,} missing ({100.0 * n_missing_gsur_female / n_total:.1f}%)")
            else:
                logging.info(f"  ✅ GSUR {gsur_suffix}_female: no missing values")
        else:
            logging.error("  ❌ GSUR columns (gsur_* or u_rate_*) not found!")

    logging.info("\n" + "=" * 80)
    logging.info("ASSESSMENT:")
    singles_ok = not results["singles"].get("missing_cols") and results["singles"].get("has_gsur", False)
    couples_ok = not results["couples"].get("missing_cols") and results["couples"].get("has_gsur", False)

    if singles_ok and couples_ok:
        logging.info("✅ MNL datasets are complete and ready for estimation")
    else:
        logging.error("❌ MNL datasets have missing columns or GSUR data")

    return results


# ============================================================================
# DIAGNOSTIC 5: LMA USAGE ANALYSIS
# ============================================================================

def diagnose_lma_usage(
    singles_ruro: pd.DataFrame,
    couples_ruro: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Analyze how lma was used in the pipeline.
    """
    logging.info("\n" + "=" * 80)
    logging.info("DIAGNOSTIC 5: LMA USAGE ANALYSIS")
    logging.info("=" * 80)

    results = {"singles": {}, "couples": {}}

    # Analyze singles
    if singles_ruro is not None and "lma" in singles_ruro.columns:
        lma = pd.to_numeric(singles_ruro["lma"], errors="coerce").fillna(0)

        n_total = len(singles_ruro)
        n_lma_1 = (lma == 1).sum()
        n_lma_0 = (lma == 0).sum()
        n_lma_other = n_total - n_lma_1 - n_lma_0

        # Check if lma is informative (has variation + some 1s)
        is_informative = (lma == 1).any() and lma.nunique(dropna=True) > 1

        results["singles"] = {
            "has_lma": True,
            "n_total": n_total,
            "n_lma_1": n_lma_1,
            "n_lma_0": n_lma_0,
            "n_lma_other": n_lma_other,
            "pct_lma_1": 100.0 * n_lma_1 / n_total,
            "is_informative": is_informative,
        }

        logging.info(f"Singles (n={n_total:,}):")
        logging.info(f"  lma column exists: YES")
        logging.info(f"  lma==1: {n_lma_1:,} ({100.0 * n_lma_1 / n_total:.1f}%)")
        logging.info(f"  lma==0: {n_lma_0:,} ({100.0 * n_lma_0 / n_total:.1f}%)")
        if n_lma_other > 0:
            logging.info(f"  lma other: {n_lma_other:,} ({100.0 * n_lma_other / n_total:.1f}%)")
        logging.info(f"  Informative: {is_informative} (has variation + some 1s)")

        if is_informative:
            logging.info("  ℹ️  lma was USED for worker identification in Step 1")
        else:
            logging.info("  ℹ️  lma was NOT USED (uninformative) - fell back to les==3")
    else:
        results["singles"] = {"has_lma": False}
        logging.info("Singles: lma column NOT FOUND")

    # Analyze couples
    if couples_ruro is not None and "lma" in couples_ruro.columns:
        lma = pd.to_numeric(couples_ruro["lma"], errors="coerce").fillna(0)

        n_total = len(couples_ruro)
        n_lma_1 = (lma == 1).sum()
        n_lma_0 = (lma == 0).sum()
        n_lma_other = n_total - n_lma_1 - n_lma_0

        is_informative = (lma == 1).any() and lma.nunique(dropna=True) > 1

        results["couples"] = {
            "has_lma": True,
            "n_total": n_total,
            "n_lma_1": n_lma_1,
            "n_lma_0": n_lma_0,
            "n_lma_other": n_lma_other,
            "pct_lma_1": 100.0 * n_lma_1 / n_total,
            "is_informative": is_informative,
        }

        logging.info(f"\nCouples (n={n_total:,}):")
        logging.info(f"  lma column exists: YES")
        logging.info(f"  lma==1: {n_lma_1:,} ({100.0 * n_lma_1 / n_total:.1f}%)")
        logging.info(f"  lma==0: {n_lma_0:,} ({100.0 * n_lma_0 / n_total:.1f}%)")
        if n_lma_other > 0:
            logging.info(f"  lma other: {n_lma_other:,} ({100.0 * n_lma_other / n_total:.1f}%)")
        logging.info(f"  Informative: {is_informative} (has variation + some 1s)")

        if is_informative:
            logging.info("  ℹ️  lma was USED for worker identification in Step 1")
        else:
            logging.info("  ℹ️  lma was NOT USED (uninformative) - fell back to les==3")
    else:
        results["couples"] = {"has_lma": False}
        logging.info("\nCouples: lma column NOT FOUND")

    logging.info("\n" + "=" * 80)
    logging.info("ASSESSMENT:")
    if results["singles"].get("has_lma") or results["couples"].get("has_lma"):
        logging.info("ℹ️  lma is present in the data (from SILC/EUROMOD)")
        logging.info("   It was used for worker identification ONLY IF informative")
        logging.info("   Working status in RURO draws uses hours>0 regardless of lma")
    else:
        logging.info("ℹ️  lma not found - worker identification used les==3 & lhw>0")

    return results


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Pre-estimation diagnostic checks for RURO pipeline"
    )
    parser.add_argument(
        "--proc-dir",
        type=str,
        required=True,
        help="Directory with processed RURO files"
    )
    parser.add_argument(
        "--euromod-output",
        type=str,
        required=True,
        help="Path to EUROMOD combined output parquet"
    )
    parser.add_argument(
        "--mnl-base",
        type=str,
        required=True,
        help="Base path for MNL datasets (without __singles.parquet suffix)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save diagnostic report JSON (optional)"
    )

    args = parser.parse_args()

    proc_dir = Path(args.proc_dir)
    euromod_path = Path(args.euromod_output)
    mnl_base = Path(args.mnl_base)
    output_dir = Path(args.output_dir) if args.output_dir else None

    # -------------------------------------------------------------------------
    # Load data
    # -------------------------------------------------------------------------
    logging.info("=" * 80)
    logging.info("LOADING DATA")
    logging.info("=" * 80)

    singles_ruro_path = proc_dir / "singles_RURO_ready.parquet"
    couples_ruro_path = proc_dir / "couples_RURO_ready.parquet"
    singles_draws_path = proc_dir / "singles_RURO_ready_RURO_draws.parquet"
    couples_draws_path = proc_dir / "couples_RURO_ready_RURO_draws.parquet"
    mnl_singles_path = Path(str(mnl_base) + "__singles.parquet")
    mnl_couples_path = Path(str(mnl_base) + "__couples.parquet")

    singles_ruro = pd.read_parquet(singles_ruro_path) if singles_ruro_path.exists() else None
    couples_ruro = pd.read_parquet(couples_ruro_path) if couples_ruro_path.exists() else None
    singles_draws = pd.read_parquet(singles_draws_path) if singles_draws_path.exists() else None
    couples_draws = pd.read_parquet(couples_draws_path) if couples_draws_path.exists() else None
    euromod_df = pd.read_parquet(euromod_path) if euromod_path.exists() else None
    mnl_singles = pd.read_parquet(mnl_singles_path) if mnl_singles_path.exists() else None
    mnl_couples = pd.read_parquet(mnl_couples_path) if mnl_couples_path.exists() else None

    logging.info(f"Loaded singles RURO: {len(singles_ruro):,} rows" if singles_ruro is not None else "Singles RURO not found")
    logging.info(f"Loaded couples RURO: {len(couples_ruro):,} rows" if couples_ruro is not None else "Couples RURO not found")
    logging.info(f"Loaded singles draws: {len(singles_draws):,} rows" if singles_draws is not None else "Singles draws not found")
    logging.info(f"Loaded couples draws: {len(couples_draws):,} rows" if couples_draws is not None else "Couples draws not found")
    logging.info(f"Loaded EUROMOD output: {len(euromod_df):,} rows" if euromod_df is not None else "EUROMOD output not found")
    logging.info(f"Loaded MNL singles: {len(mnl_singles):,} rows" if mnl_singles is not None else "MNL singles not found")
    logging.info(f"Loaded MNL couples: {len(mnl_couples):,} rows" if mnl_couples is not None else "MNL couples not found")

    # -------------------------------------------------------------------------
    # Run diagnostics
    # -------------------------------------------------------------------------
    all_results = {}

    all_results["decider_identification"] = diagnose_decider_identification(
        singles_ruro, couples_ruro
    )

    all_results["worker_consistency"] = diagnose_worker_consistency(
        singles_ruro, couples_ruro, singles_draws, couples_draws
    )

    if euromod_df is not None:
        all_results["euromod_inputs"] = diagnose_euromod_inputs(euromod_df)

    if mnl_singles is not None or mnl_couples is not None:
        all_results["mnl_completeness"] = diagnose_mnl_completeness(
            mnl_singles, mnl_couples
        )

    all_results["lma_usage"] = diagnose_lma_usage(singles_ruro, couples_ruro)

    # -------------------------------------------------------------------------
    # Save results
    # -------------------------------------------------------------------------
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "pre_estimation_diagnostics.json"

        with open(output_path, "w") as f:
            json.dump(all_results, f, indent=2, default=str)

        logging.info("\n" + "=" * 80)
        logging.info(f"Diagnostic report saved to: {output_path}")

    # -------------------------------------------------------------------------
    # Final summary
    # -------------------------------------------------------------------------
    logging.info("\n" + "=" * 80)
    logging.info("DIAGNOSTIC SUMMARY")
    logging.info("=" * 80)
    logging.info("✅ Diagnostics complete - review warnings above before estimation")
    logging.info("=" * 80)


if __name__ == "__main__":
    main()
