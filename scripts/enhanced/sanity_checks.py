"""
Runtime Sanity Checks for RURO Pipeline

This module provides validation functions to catch structural issues at each
pipeline stage boundary before wasting time on downstream estimation.

These are NOT debug prints—they encode economic identification constraints
and structural assumptions required for valid RURO estimation.

Author: Research Software Engineering Team
Date: 2025-12-29
"""

import logging
import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any


# ============================================================================
# Core Assertion Utilities
# ============================================================================

def assert_no_missing(df: pd.DataFrame, cols: List[str], stage: str = "") -> None:
    """
    Assert that specified columns have no missing values.

    Args:
        df: DataFrame to check
        cols: List of column names that must be complete
        stage: Stage name for error messages

    Raises:
        ValueError: If any column has missing values
    """
    stage_prefix = f"[{stage}] " if stage else ""

    for col in cols:
        if col not in df.columns:
            raise ValueError(f"{stage_prefix}Required column '{col}' not found in DataFrame")

        n_missing = df[col].isna().sum()
        if n_missing > 0:
            missing_rate = n_missing / len(df)
            raise ValueError(
                f"{stage_prefix}Column '{col}' has {n_missing} missing values "
                f"({missing_rate:.1%} of {len(df)} rows). This column must be complete."
            )

    logging.info(f"{stage_prefix}✓ No missing values in {cols}")


def assert_dispy_variance(df: pd.DataFrame, dispy_col: str = "ils_dispy",
                         min_std: float = 1e-6, stage: str = "") -> None:
    """
    Assert that disposable income has meaningful variation.

    No variance in ils_dispy means EUROMOD outputs are degenerate and
    utility maximization will fail (all options have same income).

    Args:
        df: DataFrame with disposable income column
        dispy_col: Name of disposable income column
        min_std: Minimum acceptable standard deviation
        stage: Stage name for error messages

    Raises:
        ValueError: If variance is below threshold
    """
    stage_prefix = f"[{stage}] " if stage else ""

    if dispy_col not in df.columns:
        raise ValueError(f"{stage_prefix}Disposable income column '{dispy_col}' not found")

    # Check for missing values first
    n_missing = df[dispy_col].isna().sum()
    if n_missing > 0:
        missing_rate = n_missing / len(df)
        raise ValueError(
            f"{stage_prefix}Column '{dispy_col}' has {n_missing} missing values "
            f"({missing_rate:.1%}). Cannot compute variance with missing data."
        )

    # Compute variance
    dispy_std = df[dispy_col].std()
    dispy_mean = df[dispy_col].mean()

    if dispy_std < min_std:
        raise ValueError(
            f"{stage_prefix}Disposable income has insufficient variance: "
            f"std={dispy_std:.2e}, mean={dispy_mean:.2f}. "
            f"EUROMOD outputs appear degenerate (all same income)."
        )

    cv = dispy_std / abs(dispy_mean) if dispy_mean != 0 else float('inf')
    logging.info(
        f"{stage_prefix}✓ Disposable income variance OK: "
        f"std={dispy_std:.2f}, mean={dispy_mean:.2f}, CV={cv:.3f}"
    )


def assert_columns_exist(df: pd.DataFrame, cols: List[str], stage: str = "") -> None:
    """
    Assert that required columns exist in DataFrame.

    Args:
        df: DataFrame to check
        cols: List of required column names
        stage: Stage name for error messages

    Raises:
        ValueError: If any required column is missing
    """
    stage_prefix = f"[{stage}] " if stage else ""
    missing_cols = [c for c in cols if c not in df.columns]

    if missing_cols:
        available_cols = sorted(df.columns)
        raise ValueError(
            f"{stage_prefix}Missing required columns: {missing_cols}\n"
            f"Available columns: {available_cols[:20]}{'...' if len(available_cols) > 20 else ''}"
        )

    logging.info(f"{stage_prefix}✓ All required columns present: {cols}")


def assert_positive_values(df: pd.DataFrame, cols: List[str], stage: str = "") -> None:
    """
    Assert that specified columns contain only positive values (> 0).

    Args:
        df: DataFrame to check
        cols: List of column names that must be positive
        stage: Stage name for error messages

    Raises:
        ValueError: If any column has non-positive values
    """
    stage_prefix = f"[{stage}] " if stage else ""

    for col in cols:
        if col not in df.columns:
            raise ValueError(f"{stage_prefix}Column '{col}' not found")

        # Skip missing values for this check
        non_missing = df[col].dropna()
        n_non_positive = (non_missing <= 0).sum()

        if n_non_positive > 0:
            violation_rate = n_non_positive / len(non_missing)
            sample_violations = df[df[col] <= 0][[col]].head(5)
            raise ValueError(
                f"{stage_prefix}Column '{col}' has {n_non_positive} non-positive values "
                f"({violation_rate:.1%}). Examples:\n{sample_violations}"
            )

    logging.info(f"{stage_prefix}✓ All values positive in {cols}")


# ============================================================================
# Stage-Specific Sanity Reports
# ============================================================================

def sanity_report_ruro_prep(df: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    Sanity checks for Stage 2: enh_RURO_prep.py output

    Validates:
    - Required columns exist (idhh, idperson, drgn1, dgn, les, ruro_sample)
    - No missing values in critical identifiers
    - Region codes (drgn1) are valid (1-10 for France)
    - Gender codes (dgn) are valid (0 or 1)
    - ruro_sample flag is boolean (adult deciders)
    - Decider counts per household type

    Args:
        df: Output DataFrame from enh_RURO_prep.py
        metadata: Optional metadata dict with household type info
    """
    stage = "RURO_prep"
    logging.info(f"\n{'='*60}")
    logging.info(f"Sanity Check: {stage}")
    logging.info(f"{'='*60}")

    # Check required columns
    required_cols = ["idhh", "idperson", "drgn1", "dgn", "les", "ruro_sample"]
    assert_columns_exist(df, required_cols, stage)

    # Check no missing in identifiers
    assert_no_missing(df, ["idhh", "idperson", "drgn1", "dgn"], stage)

    # Validate drgn1 range (France NUTS1: 1-10)
    drgn1_values = df["drgn1"].unique()
    invalid_regions = [r for r in drgn1_values if r < 1 or r > 10]
    if invalid_regions:
        raise ValueError(
            f"[{stage}] Invalid drgn1 values found: {invalid_regions}. "
            f"France NUTS1 regions must be in [1, 10]."
        )
    logging.info(f"[{stage}] ✓ drgn1 values valid: {sorted(drgn1_values)}")

    # Validate dgn values (0=female, 1=male)
    dgn_values = df["dgn"].unique()
    invalid_gender = [g for g in dgn_values if g not in [0, 1]]
    if invalid_gender:
        raise ValueError(
            f"[{stage}] Invalid dgn values found: {invalid_gender}. "
            f"Gender must be 0 (female) or 1 (male)."
        )
    logging.info(f"[{stage}] ✓ dgn values valid: {sorted(dgn_values)}")

    # Validate ruro_sample is boolean
    ruro_sample_values = df["ruro_sample"].unique()
    invalid_sample = [v for v in ruro_sample_values if v not in [0, 1, True, False]]
    if invalid_sample:
        raise ValueError(
            f"[{stage}] Invalid ruro_sample values found: {invalid_sample}. "
            f"RURO sample flag (adult deciders) must be boolean."
        )

    n_sample = df["ruro_sample"].sum()
    sample_rate = n_sample / len(df)
    logging.info(
        f"[{stage}] ✓ ruro_sample valid: {n_sample} adult deciders ({sample_rate:.1%}) "
        f"of {len(df)} persons"
    )

    # Check decider counts if metadata available
    if metadata and "household_types" in metadata:
        for hh_type, expected_deciders in [("singles", 1), ("couples", 2)]:
            if hh_type in metadata["household_types"]:
                hh_ids = metadata["household_types"][hh_type]
                decider_counts = (
                    df[df["idhh"].isin(hh_ids)]
                    .groupby("idhh")["ruro_sample"]
                    .sum()
                )

                violations = decider_counts[decider_counts != expected_deciders]
                if len(violations) > 0:
                    raise ValueError(
                        f"[{stage}] Decider count validation failed for {hh_type}: "
                        f"{len(violations)} households do not have {expected_deciders} decider(s). "
                        f"Sample: {violations.head()}"
                    )

                logging.info(
                    f"[{stage}] ✓ Decider counts valid for {hh_type}: "
                    f"all {len(decider_counts)} households have {expected_deciders} decider(s)"
                )

    logging.info(f"[{stage}] ✓ All sanity checks passed\n")


def sanity_report_draws(df: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None,
                       n_draws: int = 1000) -> None:
    """
    Sanity checks for Stage 3: enh_RURO_draws.py output

    Validates:
    - Each decider has exactly n_draws copies
    - Draw IDs are in expected range [0, n_draws-1]
    - No missing values in key columns (idhh, idperson, draw, lhw, yivwg)
    - Baseline references (lhw_base, yivwg_base) are preserved
    - Hours and wages are non-negative

    Args:
        df: Output DataFrame from enh_RURO_draws.py
        metadata: Optional metadata dict
        n_draws: Expected number of draws per decider
    """
    stage = "RURO_draws"
    logging.info(f"\n{'='*60}")
    logging.info(f"Sanity Check: {stage}")
    logging.info(f"{'='*60}")

    # Check required columns
    required_cols = ["idhh", "idperson", "draw", "lhw", "yivwg"]
    assert_columns_exist(df, required_cols, stage)

    # Check no missing in identifiers
    assert_no_missing(df, ["idhh", "idperson", "draw"], stage)

    # Validate draw counts per person
    # IMPORTANT: Deciders have n_draws+1 draws (0 to n_draws-1 = n_draws total, plus draw 0 = n_draws+1? NO!)
    # Actually: draw 0, 1, 2, ..., n_draws-1 = exactly n_draws total
    # Non-deciders only have draw 0 (1 draw total)

    # Separate deciders from non-deciders
    if "is_decider" in df.columns:
        deciders = df[df["is_decider"] == 1]
        non_deciders = df[df["is_decider"] == 0]

        # Deciders should have exactly n_draws+1 unique draws (0, 1, ..., n_draws)
        decider_draw_counts = deciders.groupby("idperson")["draw"].nunique()
        expected_decider_draws = n_draws + 1  # draw 0 through n_draws = n_draws+1 total

        decider_violations = decider_draw_counts[decider_draw_counts != expected_decider_draws]
        if len(decider_violations) > 0:
            raise ValueError(
                f"[{stage}] Draw count validation failed for deciders: {len(decider_violations)} deciders "
                f"do not have exactly {expected_decider_draws} draws (0 through {n_draws}). Found:\n"
                f"{decider_violations.value_counts().head()}"
            )

        # Non-deciders should have exactly 1 draw (draw=0)
        if len(non_deciders) > 0:
            non_decider_draw_counts = non_deciders.groupby("idperson")["draw"].nunique()
            non_decider_violations = non_decider_draw_counts[non_decider_draw_counts != 1]
            if len(non_decider_violations) > 0:
                raise ValueError(
                    f"[{stage}] Draw count validation failed for non-deciders: {len(non_decider_violations)} non-deciders "
                    f"have more than 1 draw. Non-deciders should only have draw=0. Found:\n"
                    f"{non_decider_violations.value_counts().head()}"
                )

            logging.info(
                f"[{stage}] ✓ Draw counts valid: {len(decider_draw_counts)} deciders have {expected_decider_draws} draws, "
                f"{len(non_decider_draw_counts)} non-deciders have 1 draw (draw=0)"
            )
        else:
            logging.info(
                f"[{stage}] ✓ Draw counts valid: all {len(decider_draw_counts)} deciders "
                f"have {expected_decider_draws} draws (0 through {n_draws})"
            )
    else:
        # Fallback: assume all persons are deciders (backward compatibility)
        draw_counts = df.groupby("idperson")["draw"].nunique()
        expected_draws = n_draws + 1

        violations = draw_counts[draw_counts != expected_draws]
        if len(violations) > 0:
            raise ValueError(
                f"[{stage}] Draw count validation failed: {len(violations)} persons "
                f"do not have exactly {expected_draws} draws (0 through {n_draws}). Found:\n"
                f"{violations.value_counts().head()}"
            )

        logging.info(
            f"[{stage}] ✓ Draw counts valid: all {len(draw_counts)} persons "
            f"have {expected_draws} draws (0 through {n_draws})"
        )

    # Validate draw IDs are in range
    draw_min = df["draw"].min()
    draw_max = df["draw"].max()

    if draw_min < 0 or draw_max > n_draws:
        raise ValueError(
            f"[{stage}] Draw IDs out of range: expected [0, {n_draws}], "
            f"found [{draw_min}, {draw_max}]"
        )

    logging.info(f"[{stage}] ✓ Draw IDs valid: [{draw_min}, {draw_max}]")

    # Check baseline references if they exist
    if "lhw_base" in df.columns and "yivwg_base" in df.columns:
        # Each person should have same baseline across all draws
        baseline_var = df.groupby("idperson")[["lhw_base", "yivwg_base"]].std()

        if (baseline_var > 1e-6).any().any():
            violators = baseline_var[(baseline_var > 1e-6).any(axis=1)]
            raise ValueError(
                f"[{stage}] Baseline references vary across draws for {len(violators)} persons. "
                f"Baselines must be constant per person. Sample:\n{violators.head()}"
            )

        logging.info(f"[{stage}] ✓ Baseline references constant across draws")

    # Check hours and wages are non-negative
    if (df["lhw"] < 0).any():
        n_negative = (df["lhw"] < 0).sum()
        raise ValueError(
            f"[{stage}] Found {n_negative} negative hours (lhw). "
            f"Hours must be non-negative."
        )

    if (df["yivwg"] < 0).any():
        n_negative = (df["yivwg"] < 0).sum()
        raise ValueError(
            f"[{stage}] Found {n_negative} negative wages (yivwg). "
            f"Wages must be non-negative."
        )

    logging.info(f"[{stage}] ✓ Hours and wages are non-negative")

    logging.info(f"[{stage}] ✓ All sanity checks passed\n")


def sanity_report_euromod(df: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    Sanity checks for Stage 4: enh_RURO_euromod.py output

    Validates:
    - Disposable income (ils_dispy) has meaningful variance
    - No missing values in ils_dispy
    - Income values are reasonable (not all zero, not all identical)
    - Row count matches expected (deciders × n_draws + non-deciders replicated)

    Args:
        df: Output DataFrame from EUROMOD simulation
        metadata: Optional metadata dict with expected row counts
    """
    stage = "RURO_euromod"
    logging.info(f"\n{'='*60}")
    logging.info(f"Sanity Check: {stage}")
    logging.info(f"{'='*60}")

    # Check ils_dispy exists and has no missing
    assert_columns_exist(df, ["ils_dispy"], stage)
    assert_no_missing(df, ["ils_dispy"], stage)

    # Check for variance in disposable income
    assert_dispy_variance(df, dispy_col="ils_dispy", stage=stage)

    # Check for all-zero income (degenerate case)
    n_zero = (df["ils_dispy"] == 0).sum()
    if n_zero == len(df):
        raise ValueError(
            f"[{stage}] All {len(df)} rows have ils_dispy=0. "
            f"EUROMOD outputs are degenerate."
        )

    if n_zero > len(df) * 0.1:  # More than 10% zeros
        zero_rate = n_zero / len(df)
        logging.warning(
            f"[{stage}] {n_zero} rows ({zero_rate:.1%}) have ils_dispy=0. "
            f"This is unusually high and may indicate issues."
        )

    # Check row count if metadata available
    if metadata and "expected_rows" in metadata:
        expected = metadata["expected_rows"]
        actual = len(df)

        if actual != expected:
            raise ValueError(
                f"[{stage}] Row count mismatch: expected {expected}, got {actual}. "
                f"Check that non-deciders were properly replicated across draws."
            )

        logging.info(f"[{stage}] ✓ Row count matches expected: {actual}")

    # Check income range is reasonable
    dispy_min = df["ils_dispy"].min()
    dispy_max = df["ils_dispy"].max()
    dispy_median = df["ils_dispy"].median()

    logging.info(
        f"[{stage}] ✓ Income range: [{dispy_min:.2f}, {dispy_max:.2f}], "
        f"median={dispy_median:.2f}"
    )

    logging.info(f"[{stage}] ✓ All sanity checks passed\n")


def sanity_report_couples_gender_balance(df: pd.DataFrame, stage: str = "MNL_prep") -> None:
    """
    Sanity check for couples gender composition.

    Validates that each (idhh, draw) pair has exactly 1 male and 1 female.
    This is CRITICAL for couples reshape—invalid composition causes silent data corruption.

    Args:
        df: DataFrame with couples data (must have idhh, draw, dgn columns)
        stage: Stage name for error messages

    Raises:
        ValueError: If any household-draw has invalid gender composition
    """
    logging.info(f"\n{'='*60}")
    logging.info(f"Sanity Check: {stage} - Couples Gender Balance")
    logging.info(f"{'='*60}")

    # Check required columns
    assert_columns_exist(df, ["idhh", "draw", "dgn"], stage)

    # Count males and females per (idhh, draw)
    gender_counts = df.groupby(["idhh", "draw"])["dgn"].apply(
        lambda x: pd.Series({
            "n_male": (x == 1).sum(),
            "n_female": (x == 0).sum(),
            "n_total": len(x)
        })
    ).unstack()

    # Check for violations
    violations = gender_counts[
        (gender_counts["n_male"] != 1) |
        (gender_counts["n_female"] != 1) |
        (gender_counts["n_total"] != 2)
    ]

    if len(violations) > 0:
        sample = violations.head(10)
        raise ValueError(
            f"[{stage}] Gender composition validation FAILED: "
            f"{len(violations)} household-draws have invalid composition.\n"
            f"Each couple must have exactly 1 male (dgn=1) and 1 female (dgn=0).\n"
            f"Sample violations:\n{sample}"
        )

    logging.info(
        f"[{stage}] ✓ Gender composition valid: all {len(gender_counts)} "
        f"household-draws have 1 male + 1 female"
    )
    logging.info(f"[{stage}] ✓ Couples gender balance check passed\n")


def sanity_report_mnl_dataset(df: pd.DataFrame, household_type: str,
                              metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    Sanity checks for Stage 6: enh_RURO_prep_mnl_basic.py output

    Validates:
    - Required MNL variables exist (idhh, draw, consumption, leisure, etc.)
    - No missing values in estimation variables
    - Consumption and leisure are positive
    - If couples: gender-specific variables have been properly reshaped
    - Draw counts match expected n_draws per household

    Args:
        df: Output MNL dataset
        household_type: "singles" or "couples"
        metadata: Optional metadata dict
    """
    stage = f"MNL_prep_{household_type}"
    logging.info(f"\n{'='*60}")
    logging.info(f"Sanity Check: {stage}")
    logging.info(f"{'='*60}")

    # Check required base columns
    required_cols = ["idhh", "draw"]
    assert_columns_exist(df, required_cols, stage)

    # Type-specific validations
    if household_type == "singles":
        # Singles should have consumption, leisure, baseline variables
        required_cols.extend(["consumption", "leisure"])
        assert_columns_exist(df, required_cols, stage)
        assert_no_missing(df, required_cols, stage)
        assert_positive_values(df, ["consumption", "leisure"], stage)

    elif household_type == "couples":
        # Couples: leisure is individual (male/female), consumption is household-level
        # Check for gender-specific leisure (required)
        required_cols.extend(["leisure_male", "leisure_female"])
        assert_columns_exist(df, required_cols, stage)
        assert_no_missing(df, required_cols, stage)
        assert_positive_values(df, ["leisure_male", "leisure_female"], stage)

        # Consumption can be either:
        # 1. Household-level: "consumption" (standard in household labor supply models)
        # 2. Individual-level: "consumption_m" and "consumption_f" (if tracked separately)
        has_household_consumption = "consumption" in df.columns
        has_individual_consumption = ("consumption_m" in df.columns and "consumption_f" in df.columns)

        if has_household_consumption:
            # Standard: household-level consumption
            assert_no_missing(df, ["consumption"], stage)
            assert_positive_values(df, ["consumption"], stage)
        elif has_individual_consumption:
            # Alternative: individual consumption (for compatibility)
            assert_no_missing(df, ["consumption_m", "consumption_f"], stage)
            assert_positive_values(df, ["consumption_m", "consumption_f"], stage)
        else:
            raise ValueError(
                f"[{stage}] Couples data must have either household 'consumption' or "
                f"individual 'consumption_m'/'consumption_f' columns"
            )

    else:
        raise ValueError(f"Unknown household_type: {household_type}")

    # Check draw counts per household
    if "draw" in df.columns:
        draw_counts = df.groupby("idhh")["draw"].nunique()

        # All households should have same number of draws
        unique_counts = draw_counts.unique()
        if len(unique_counts) > 1:
            raise ValueError(
                f"[{stage}] Inconsistent draw counts across households: "
                f"found {unique_counts}. All households must have same n_draws."
            )

        n_draws = unique_counts[0]
        logging.info(
            f"[{stage}] ✓ Draw counts valid: all {len(draw_counts)} households "
            f"have {n_draws} draws"
        )

    # Check for consumption/leisure variance
    if household_type == "singles":
        consumption_std = df["consumption"].std()
        leisure_std = df["leisure"].std()
    else:
        # Couples: check consumption variance (household or individual)
        if "consumption" in df.columns:
            consumption_std = df["consumption"].std()
        else:
            consumption_std = df[["consumption_m", "consumption_f"]].std().mean()

        # Couples: check leisure variance (always individual male/female)
        leisure_std = df[["leisure_male", "leisure_female"]].std().mean()

    if consumption_std < 1e-6:
        raise ValueError(
            f"[{stage}] Consumption has no variance (std={consumption_std:.2e}). "
            f"MNL estimation will fail."
        )

    if leisure_std < 1e-6:
        raise ValueError(
            f"[{stage}] Leisure has no variance (std={leisure_std:.2e}). "
            f"MNL estimation will fail."
        )

    logging.info(
        f"[{stage}] ✓ Consumption variance: std={consumption_std:.2f}"
    )
    logging.info(
        f"[{stage}] ✓ Leisure variance: std={leisure_std:.2f}"
    )

    logging.info(f"[{stage}] ✓ All sanity checks passed\n")


# ============================================================================
# Summary Report
# ============================================================================

def print_sanity_summary(checks_passed: List[str], checks_failed: List[str]) -> None:
    """
    Print a summary of all sanity checks run during pipeline execution.

    Args:
        checks_passed: List of stage names that passed all checks
        checks_failed: List of stage names that failed checks
    """
    print("\n" + "="*60)
    print("PIPELINE SANITY CHECK SUMMARY")
    print("="*60)

    if checks_passed:
        print(f"\n✓ PASSED ({len(checks_passed)} stages):")
        for stage in checks_passed:
            print(f"  - {stage}")

    if checks_failed:
        print(f"\n✗ FAILED ({len(checks_failed)} stages):")
        for stage in checks_failed:
            print(f"  - {stage}")
    else:
        print("\n✓ ALL SANITY CHECKS PASSED")

    print("="*60 + "\n")
