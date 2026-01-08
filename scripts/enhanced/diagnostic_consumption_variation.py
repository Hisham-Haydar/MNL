"""
==============================================================================
Diagnostic: Check Consumption Variation Across Draws
==============================================================================
CRITICAL CHECK: If consumption doesn't vary within households across draws,
then beta_c and theta_c are NOT IDENTIFIED!

This script checks:
1. Within-household consumption variation (std dev across draws)
2. Whether consumption is constant for some/all households
3. Correlation between hours/wages and consumption (EUROMOD working?)

Author: RURO Diagnostic Suite
Created: 2026-01-07
==============================================================================
"""

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def check_consumption_variation(mnl_data_path: Path, household_type: str):
    """
    Check if consumption varies across draws within households.

    Critical for identification of beta_c and theta_c!
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"DIAGNOSTIC: Consumption Variation Check ({household_type})")
    logger.info(f"{'='*80}\n")

    # Load MNL dataset
    df = pd.read_parquet(mnl_data_path)
    logger.info(f"Loaded: {mnl_data_path}")
    logger.info(f"  Rows: {len(df):,}")
    logger.info(f"  Unique households: {df['idhh'].nunique():,}")

    # Determine consumption column
    if household_type == "couples" and "consumption" not in df.columns:
        # Couples may have consumption_m and consumption_f
        if "consumption_m" in df.columns:
            logger.warning("Couples data has individual consumption (consumption_m, consumption_f)")
            logger.warning("Using consumption_m for variation check")
            c_col = "consumption_m"
        else:
            raise ValueError("Cannot find consumption column")
    else:
        c_col = "consumption"

    # Compute within-household statistics
    logger.info(f"\n{'='*60}")
    logger.info("Within-Household Consumption Variation")
    logger.info(f"{'='*60}")

    household_stats = df.groupby('idhh')[c_col].agg([
        ('mean', 'mean'),
        ('std', 'std'),
        ('min', 'min'),
        ('max', 'max'),
        ('range', lambda x: x.max() - x.min()),
        ('cv', lambda x: x.std() / x.mean() if x.mean() > 0 else 0)  # Coefficient of variation
    ]).reset_index()

    # Overall statistics
    logger.info(f"\nOVERALL STATISTICS:")
    logger.info(f"  Mean consumption: {df[c_col].mean():.2f}")
    logger.info(f"  Std dev consumption (overall): {df[c_col].std():.2f}")

    # Within-household variation
    logger.info(f"\nWITHIN-HOUSEHOLD VARIATION:")
    logger.info(f"  Mean std dev: {household_stats['std'].mean():.2f}")
    logger.info(f"  Median std dev: {household_stats['std'].median():.2f}")
    logger.info(f"  Mean CV: {household_stats['cv'].mean():.4f}")

    # CRITICAL: Check for zero variation
    zero_var = household_stats['std'] < 1e-6
    n_zero_var = zero_var.sum()
    pct_zero_var = 100 * n_zero_var / len(household_stats)

    logger.info(f"\n🚨 CRITICAL CHECK:")
    logger.info(f"  Households with ZERO consumption variation: {n_zero_var:,} / {len(household_stats):,} ({pct_zero_var:.1f}%)")

    if pct_zero_var > 50:
        logger.error("  ❌ SEVERE ISSUE: >50% of households have no consumption variation!")
        logger.error("  → beta_c and theta_c are NOT IDENTIFIED")
        logger.error("  → Check EUROMOD simulation (Step 4)")
    elif pct_zero_var > 10:
        logger.warning("  ⚠️  WARNING: >10% of households have no consumption variation")
        logger.warning("  → Weak identification of beta_c and theta_c")
    else:
        logger.info(f"  ✓ Good: Only {pct_zero_var:.1f}% have zero variation")

    # Check correlation with hours and wages (if available)
    if 'hours' in df.columns and 'wage' in df.columns:
        logger.info(f"\n{'='*60}")
        logger.info("Correlation with Hours/Wages (EUROMOD Check)")
        logger.info(f"{'='*60}")

        corr_hours = df[c_col].corr(df['hours'])
        corr_wage = df[c_col].corr(df['wage'])

        logger.info(f"  Consumption vs Hours: {corr_hours:.4f}")
        logger.info(f"  Consumption vs Wage: {corr_wage:.4f}")

        if abs(corr_hours) < 0.1 and abs(corr_wage) < 0.1:
            logger.error("  ❌ SEVERE: Consumption uncorrelated with hours/wages")
            logger.error("  → EUROMOD simulation may have failed!")
        else:
            logger.info(f"  ✓ Consumption responds to hours/wages")

    # Sample households with zero variation
    if n_zero_var > 0:
        logger.info(f"\n{'='*60}")
        logger.info("Sample Households with ZERO Variation")
        logger.info(f"{'='*60}")

        zero_var_hh = household_stats[zero_var].head(5)['idhh'].values
        for idhh in zero_var_hh:
            hh_data = df[df['idhh'] == idhh][[c_col, 'hours', 'wage', 'draw']].head(10)
            logger.info(f"\nHousehold {idhh}:")
            logger.info(f"{hh_data.to_string(index=False)}")

    # Distribution of within-household std dev
    logger.info(f"\n{'='*60}")
    logger.info("Distribution of Within-Household Std Dev")
    logger.info(f"{'='*60}")

    percentiles = [0, 10, 25, 50, 75, 90, 100]
    pct_values = np.percentile(household_stats['std'], percentiles)
    for p, v in zip(percentiles, pct_values):
        logger.info(f"  P{p:3d}: {v:8.2f}")

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("SUMMARY")
    logger.info(f"{'='*60}")

    if pct_zero_var > 50:
        logger.error("❌ FAILED: Consumption does not vary within households")
        logger.error("   → beta_c, theta_c NOT IDENTIFIED")
        logger.error("   → Check EUROMOD output (Step 4: enh_RURO_euromod.py)")
        return False
    elif pct_zero_var > 10:
        logger.warning("⚠️  WARNING: Weak consumption variation")
        logger.warning("   → beta_c, theta_c weakly identified")
        return True
    else:
        logger.info("✓ PASSED: Consumption varies across draws")
        logger.info("  → beta_c, theta_c should be identified")
        return True


def main():
    parser = argparse.ArgumentParser(description="Check consumption variation across draws")
    parser.add_argument("--mnl-base", type=str, required=True,
                        help="Base path to MNL datasets (e.g., fr_2016_RURO_mnl)")
    parser.add_argument("--household-type", type=str, choices=["singles", "couples", "both"],
                        default="both", help="Which household type to check")

    args = parser.parse_args()
    mnl_base = Path(args.mnl_base)

    # Check singles
    if args.household_type in ["singles", "both"]:
        singles_path = mnl_base.parent / f"{mnl_base.name}__singles.parquet"
        if singles_path.exists():
            result_singles = check_consumption_variation(singles_path, "singles")
        else:
            logger.error(f"Singles data not found: {singles_path}")
            result_singles = False

    # Check couples
    if args.household_type in ["couples", "both"]:
        couples_path = mnl_base.parent / f"{mnl_base.name}__couples.parquet"
        if couples_path.exists():
            result_couples = check_consumption_variation(couples_path, "couples")
        else:
            logger.error(f"Couples data not found: {couples_path}")
            result_couples = False

    # Overall result
    logger.info(f"\n{'='*80}")
    logger.info("FINAL RESULT")
    logger.info(f"{'='*80}")

    if args.household_type == "both":
        if result_singles and result_couples:
            logger.info("✓ Both singles and couples have sufficient consumption variation")
        else:
            logger.error("❌ Consumption variation issues detected")
            logger.error("   → This explains why beta_c and theta_c are stuck at initial values!")
    else:
        if args.household_type == "singles" and result_singles:
            logger.info("✓ Singles have sufficient consumption variation")
        elif args.household_type == "couples" and result_couples:
            logger.info("✓ Couples have sufficient consumption variation")
        else:
            logger.error("❌ Consumption variation issues detected")


if __name__ == "__main__":
    main()
