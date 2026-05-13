#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-12-04 23:11:01
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/


"""
france_data_prep.py - Standalone French Data Preparation Script

Filters French EUROMOD data for any specified year via CLI.
Usage: python france_data_prep.py --year 2021 [--raw-dir PATH] [--out-dir PATH]

The script automatically:
  - Uses input file: FR_{year}.txt
  - Uses EUROMOD system year: year - 1
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")  # headless plotting for batch runs

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Ensure pythonnet uses CoreCLR runtime for Euromod
os.environ.setdefault("PYTHONNET_RUNTIME", "coreclr")

try:
    import euromod as em
except ImportError:
    em = None
    print("Warning: euromod package not found. EUROMOD simulation will not be available.")

# Import centralized path helpers
try:
    from path_helpers import (
        data_root,
        euromod_root,
        euromod_raw_root,
        outputs_root,
        ensure_dir,
    )
except ImportError:
    # Fallback if path_helpers not available - define minimal versions
    def get_project_root() -> Path:
        """Get project root directory."""
        try:
            script_dir = Path(__file__).resolve().parent
        except NameError:
            script_dir = Path.cwd()
        return script_dir.parent if script_dir.name == "scripts" else script_dir

    def data_root() -> Path:
        """Return the base data directory."""
        candidates = [
            Path(r"U:\EUROMOD-STORAGE\Data"),
            Path(r"\\crc\users\hisham\Desktop\Nizam_Hisham\MNL\data"),
            get_project_root() / "data",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return get_project_root() / "data"

    def euromod_root() -> Path:
        """Return the EUROMOD model directory."""
        candidates = [
            Path(r"U:\EUROMOD-STORAGE\EUROMOD_RELEASES_I6\EM3"),
            Path(r"U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+"),
            Path(r"\\crc\users\hisham\Desktop\Nizam_Hisham\MNL\EUROMOD"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return get_project_root() / "EUROMOD"

    def euromod_raw_root() -> Path:
        """Return the raw EUROMOD data directory."""
        candidates = [
            Path(r"U:\EUROMOD-STORAGE\Data\raw"),
            data_root() / "raw",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return data_root() / "raw"

    def outputs_root() -> Path:
        """Return the outputs directory."""
        return get_project_root() / "outputs"

    def ensure_dir(path: Path) -> Path:
        """Create directory if it doesn't exist and return it."""
        path.mkdir(parents=True, exist_ok=True)
        return path

# =============================================================================
# CONSTANTS
# =============================================================================

WPM = 52 / 12  # weeks-per-month factor for wage reconstruction (~4.3333)

DEFAULT_CONFIG = {
    "age_range": (16, 65),
    "allowed_les": [3, 5, 7],
    "extreme_wage_diff": 500,
    "wage_bounds": (2, 170),
    "hour_bounds": (10, 70),
    "export_format": "parquet",
    "plot_bins": 40,
}

PLOT_VARIABLES = {
    "lhw": {"label": "Weekly hours worked (lhw)", "discrete": False},
    "yivwg": {"label": "Gross wage (yivwg)", "discrete": False},
    "ils_disp": {"label": "Disposable income (ils_disp)", "discrete": False},
    "yem": {"label": "Employment income (yem)", "discrete": False},
    "les": {"label": "Labour status code (les)", "discrete": True},
    "loc": {"label": "Occupation class (loc)", "discrete": True},
    "lindi": {"label": "Industry class (lindi)", "discrete": True},
    "dag": {"label": "Age (dag)", "discrete": False},
    "dehde": {"label": "Highest education (dehde)", "discrete": True},
    "num_children_total": {"label": "Number of children", "discrete": True},
}

# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the data preparation pipeline."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_household_integrity(df: pd.DataFrame) -> bool:
    """Check household data integrity."""
    if "idhh" not in df.columns:
        logging.warning("Column 'idhh' not found for household integrity check.")
        return True
    
    # Check for duplicate person IDs within households
    if "idperson" in df.columns:
        duplicates = df.groupby(["idhh", "idperson"]).size()
        if (duplicates > 1).any():
            logging.warning("Found duplicate person IDs within households.")
            return False
    return True

def check_data_quality(df: pd.DataFrame) -> List[str]:
    """Check data quality and return list of issues."""
    issues = []
    
    # Check for high missing values
    for col in df.columns:
        missing_pct = df[col].isna().mean() * 100
        if missing_pct > 50:
            issues.append(f"Column '{col}' has {missing_pct:.1f}% missing values")
    
    # Check for negative values in income columns
    income_cols = [c for c in df.columns if c.startswith(("y", "ils_"))]
    for col in income_cols:
        if col in df.columns and (df[col] < 0).any():
            neg_count = (df[col] < 0).sum()
            issues.append(f"Column '{col}' has {neg_count} negative values")
    
    return issues

# =============================================================================
# INCOME CREATION FUNCTIONS
# =============================================================================

def create_income_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create standardized income aggregate columns.
    
    EUROMOD DRD mapping used here:
        bun = unemployment benefit
        bsa = social assistance
        pdi = disability pension
        poa = old-age pension
        psu = survivor's pension
        byr = early retirement benefit (if present)
    
    Key aggregates created:
        - benefit_retire_disab: Retirement/survivor/early-retirement/disability benefits
          Used to EXCLUDE households (RURO benefit-exclusion logic: byr + pdi + poa + psu == 0)
        - benefit_ub_sa: Unemployment benefits + social assistance
          These do NOT trigger exclusion; kept in sample as out-of-labour income in RURO model
        - replacement_income_total: Legacy aggregate for descriptive purposes only
    """
    df = df.copy()
    
    # Employment income aggregates
    if "yem" in df.columns:
        df["income_employment"] = df["yem"].fillna(0)
    
    # Self-employment income
    if "yse" in df.columns:
        df["income_self_employment"] = df["yse"].fillna(0)
    
    # Total market income
    market_cols = ["yem", "yse", "yiy", "ypt"]
    available_market = [c for c in market_cols if c in df.columns]
    if available_market:
        df["income_market"] = df[available_market].fillna(0).sum(axis=1)
    
    # =========================================================================
    # BENEFIT AGGREGATES (RURO DRD mapping)
    # =========================================================================
    
    # Retirement/survivor/early-retirement/disability benefits
    # These trigger household exclusion (analogous to byr + pdi + poa + psu == 0)
    retire_cols = [c for c in ["byr", "pdi", "poa", "psu"] if c in df.columns]
    if retire_cols:
        df["benefit_retire_disab"] = df[retire_cols].fillna(0).sum(axis=1)
    else:
        df["benefit_retire_disab"] = 0
    
    # Unemployment benefits + social assistance
    # These do NOT trigger exclusion; they are part of out-of-labour income in RURO
    ub_cols = [c for c in ["bun", "bsa"] if c in df.columns]
    if ub_cols:
        df["benefit_ub_sa"] = df[ub_cols].fillna(0).sum(axis=1)
    else:
        df["benefit_ub_sa"] = 0
    
    # Legacy aggregate for descriptive purposes only (NOT used as hard filter anymore)
    replacement_cols = ["bun", "bsa", "poa", "pdi"]
    available_replacement = [c for c in replacement_cols if c in df.columns]
    if available_replacement:
        df["replacement_income_total"] = df[available_replacement].fillna(0).sum(axis=1)
    else:
        df["replacement_income_total"] = 0
    
    # Total income / Disposable income
    # Check for various EUROMOD disposable income column names
    disp_candidates = ["ils_disp", "ils_dispy", "ils_disp_s"]
    disp_col = next((c for c in disp_candidates if c in df.columns), None)
    
    if disp_col:
        df["ils_disp"] = df[disp_col].fillna(0)  # Standardize column name
        df["income_total_overall"] = df["ils_disp"]
    elif "income_market" in df.columns:
        df["income_total_overall"] = df["income_market"]
    
    return df

# =============================================================================
# LABOR STATUS CORRECTION
# =============================================================================

def correct_labor_status(
    df: pd.DataFrame,
    *,
    emp_threshold: float = 100.0,
    yse_threshold: float = 300.0,
    hrs_min: float = 10.0,
    ratio_high: float = 4.0,
) -> pd.DataFrame:
    """
    Correct labor status based on income and hours worked.
    
    Labor status codes:
        1 = Farmer
        2 = Self-employed
        3 = Employee
        4 = Pensioner
        5 = Unemployed
        6 = Student
        7 = Inactive/other
    """
    df = df.copy()
    
    yem = df["yem"].fillna(0) if "yem" in df.columns else pd.Series(0, index=df.index)
    yse = df["yse"].fillna(0) if "yse" in df.columns else pd.Series(0, index=df.index)
    lhw = df["lhw"].fillna(0) if "lhw" in df.columns else pd.Series(0, index=df.index)
    les_orig = df["les"].fillna(7) if "les" in df.columns else pd.Series(7, index=df.index)
    
    les_new = les_orig.copy()
    
    # Dominance logic: classify based on primary income source
    has_emp_income = yem > emp_threshold
    has_se_income = yse > yse_threshold
    working_hours = lhw >= hrs_min
    
    # Self-employed dominates if yse/yem >= ratio_high
    se_dominates = (yse > 0) & (yem > 0) & (yse / yem.replace(0, np.nan) >= ratio_high)
    se_only = has_se_income & ~has_emp_income
    
    # Employee if has employee income and not dominated by self-employment
    emp_condition = has_emp_income & ~se_dominates & working_hours
    les_new = np.where(emp_condition, 3, les_new)
    
    # Self-employed if SE income dominates or only SE income
    se_condition = (se_dominates | se_only) & working_hours
    les_new = np.where(se_condition, 2, les_new)
    
    # Inactive if no significant income and not working
    inactive_condition = ~has_emp_income & ~has_se_income & ~working_hours
    les_new = np.where(inactive_condition & (les_new == 3), 7, les_new)
    
    df["les_enforced"] = les_new.astype(int)
    
    return df

# =============================================================================
# WAGE RECONSTRUCTION
# =============================================================================

def compute_wage_recon(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute reconstructed hourly wage for employees.
    
    Creates:
        - w_emp_strict: hourly wage = yem / (lhw * WPM)
        - yem_recon: reconstructed monthly earnings
    """
    df = df.copy()
    
    yem = df["yem"].fillna(0) if "yem" in df.columns else pd.Series(0, index=df.index)
    lhw = df["lhw"].fillna(0) if "lhw" in df.columns else pd.Series(0, index=df.index)
    
    # Valid employees: les_enforced == 3 and positive hours
    is_employee = df.get("les_enforced", df.get("les", pd.Series(0, index=df.index))) == 3
    valid_hours = lhw > 0
    
    # Compute hourly wage
    monthly_hours = lhw * WPM
    df["w_emp_strict"] = np.where(
        is_employee & valid_hours,
        yem / monthly_hours.replace(0, np.nan),
        np.nan
    )
    
    # Reconstructed monthly earnings
    df["yem_recon"] = np.where(
        is_employee & valid_hours,
        df["w_emp_strict"] * monthly_hours,
        np.nan
    )
    
    return df

# =============================================================================
# EXTREME HOUSEHOLD IDENTIFICATION
# =============================================================================

def identify_extreme_households(df: pd.DataFrame, config: Optional[Dict] = None) -> np.ndarray:
    """
    Identify households with extreme wage differences for removal.
    """
    if config is None:
        config = DEFAULT_CONFIG
    
    diff_col = config.get("extreme_diff_column", "diff_yem_final")
    threshold = config.get("extreme_wage_diff", 500)
    
    if diff_col not in df.columns:
        return np.array([])
    
    # Identify households with extreme positive or negative differences
    extreme_mask = df[diff_col].abs() >= threshold
    extreme_households = df.loc[extreme_mask, "idhh"].unique()
    
    return extreme_households

# =============================================================================
# FILTERING FUNCTIONS
# =============================================================================

def log_filtering_step(step_name: str, before_count: int, after_count: int) -> None:
    """Log a filtering step with counts."""
    dropped = before_count - after_count
    pct = (dropped / before_count * 100) if before_count > 0 else 0
    logging.info(f"{step_name}: {before_count} -> {after_count} (dropped {dropped}, {pct:.1f}%)")

def apply_other_members_filter(df: pd.DataFrame, config: Optional[Dict] = None) -> pd.DataFrame:
    """
    Filter out households where non-head/non-partner members have significant income or work capacity.
    """
    if config is None:
        config = DEFAULT_CONFIG
    
    df_work = df.copy()
    
    # Condition: non-head, non-partner members in working age with no disability, 
    # not in education, or with employment/self-employment income
    cond = (
        (df_work["hh_IsHead"] == 0)
        & (df_work.get("hh_IsPartner", 0) == 0)
        & (
            (
                df_work["dag"].between(*config["age_range"])
                & (df_work.get("ddi", 0) == 0)
                & (df_work.get("dec", 0) == 0)
            )
            | ((df_work.get("yem", 0) > 50) | (df_work.get("yse", 0) != 0))
        )
    )
    
    households_to_drop = df_work.loc[cond, "idhh"].unique()
    df_work = df_work[~df_work["idhh"].isin(households_to_drop)]
    
    return df_work

# =============================================================================
# STEPWISE FILTERING
# =============================================================================

def stepwise_filter_households(
    df: pd.DataFrame, household_type: str = "couples", config: Optional[Dict] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Perform stepwise filtering on households.
    
    Steps: Baseline, Age, Education, Retirement/Disability (HH level), Allowed LES,
           Other Members, Wage/Labor Time.
    """
    if config is None:
        config = DEFAULT_CONFIG
    
    stats = []
    df_work = df.copy()
    initial_households = df_work["idhh"].nunique()
    
    # Guard against empty dataframe
    if initial_households == 0:
        logging.warning(f"No {household_type} households to filter. Returning empty results.")
        empty_stats = pd.DataFrame([{
            "Step": "Baseline",
            "Total Households": 0,
            "Female Heads": 0,
            "Male Heads": 0,
            "% Remaining": 0.0,
        }])
        return df_work, empty_stats
    
    # Baseline
    heads = df_work[df_work["hh_IsHead"] == 1]
    total = heads["idhh"].nunique()
    female = heads[heads["dgn"] == 0]["idhh"].nunique() if "dgn" in heads.columns else 0
    male = heads[heads["dgn"] == 1]["idhh"].nunique() if "dgn" in heads.columns else 0
    stats.append({
        "Step": "Baseline",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": 100.0,
    })
    
    # Step 1: Age (Head)
    age_mask = (df_work["hh_IsHead"] == 1) & df_work["dag"].between(*config["age_range"])
    keep_idhh = df_work.loc[age_mask, "idhh"].unique()
    df_work = df_work[df_work["idhh"].isin(keep_idhh)]
    heads = df_work[df_work["hh_IsHead"] == 1]
    total = heads["idhh"].nunique()
    female = heads[heads["dgn"] == 0]["idhh"].nunique() if "dgn" in heads.columns else 0
    male = heads[heads["dgn"] == 1]["idhh"].nunique() if "dgn" in heads.columns else 0
    stats.append({
        "Step": "Age (Head)",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    })
      # Step 2: Education (Head) - dec == 0 means not currently in education
    if "dec" in df_work.columns:
        edu_mask = (df_work["hh_IsHead"] == 1) & (df_work["dec"] == 0)
        keep_idhh = df_work.loc[edu_mask, "idhh"].unique()
        df_work = df_work[df_work["idhh"].isin(keep_idhh)]
    heads = df_work[df_work["hh_IsHead"] == 1]
    total = heads["idhh"].nunique()
    female = heads[heads["dgn"] == 0]["idhh"].nunique() if "dgn" in heads.columns else 0
    male = heads[heads["dgn"] == 1]["idhh"].nunique() if "dgn" in heads.columns else 0
    stats.append({
        "Step": "Education (Head)",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    })
    
    # =========================================================================
    # Step 3: Retirement/Disability Benefits (Household level)
    # =========================================================================
    # Exclude households where ANY member receives retirement/survivor/early-retirement/
    # disability benefits, using RURO exclusion logic: byr + pdi + poa + psu == 0
    # 
    # NOTE: Unemployment benefits (bun) and social assistance (bsa) do NOT trigger
    # exclusion. They are kept in the sample as out-of-labour income in the RURO model.
    # =========================================================================
    if "benefit_retire_disab" in df_work.columns:
        # Sum retirement/disability benefits at household level
        hh_retire_sum = df_work.groupby("idhh")["benefit_retire_disab"].sum()
        # Flag households with any such benefits (sum > 0)
        hh_retire_flag = hh_retire_sum.gt(0)
        # Keep only households where sum == 0 (no retirement/disability benefits)
        hh_to_keep = hh_retire_flag[~hh_retire_flag].index
    else:
        # If column doesn't exist, keep all households
        hh_to_keep = df_work["idhh"].unique()
    
    before_count = df_work["idhh"].nunique()
    df_work = df_work[df_work["idhh"].isin(hh_to_keep)]
    after_count = df_work["idhh"].nunique()
    log_filtering_step("Retirement/Disability Benefits (Any Member)", before_count, after_count)
    
    heads = df_work[df_work["hh_IsHead"] == 1]
    total = heads["idhh"].nunique()
    female = heads[heads["dgn"] == 0]["idhh"].nunique() if "dgn" in heads.columns else 0
    male = heads[heads["dgn"] == 1]["idhh"].nunique() if "dgn" in heads.columns else 0
    stats.append({
        "Step": "Retirement/Disability (HH level)",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    })
    
    # =========================================================================
    # Step 4: Allowed LES (Head)
    # =========================================================================
    # NOTE: We no longer filter out les == 5 (unemployed) explicitly.
    # Unemployed heads are kept as long as their household passes age, education,
    # retirement/disability filters and les is in allowed_les (which includes 5).
    # =========================================================================
    les_col = "les_enforced" if "les_enforced" in df_work.columns else "les"
    if les_col in df_work.columns:
        allowed_mask = (df_work["hh_IsHead"] == 1) & (df_work[les_col].isin(config["allowed_les"]))
        keep_idhh = df_work.loc[allowed_mask, "idhh"].unique()
        df_work = df_work[df_work["idhh"].isin(keep_idhh)]
    heads = df_work[df_work["hh_IsHead"] == 1]
    total = heads["idhh"].nunique()
    female = heads[heads["dgn"] == 0]["idhh"].nunique() if "dgn" in heads.columns else 0
    male = heads[heads["dgn"] == 1]["idhh"].nunique() if "dgn" in heads.columns else 0
    stats.append({
        "Step": "Allowed LES (Head)",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    })
    
    # Partner steps (for couples only)
    if household_type == "couples":
        # Age (Partner)
        if "hh_IsPartner" in df_work.columns:
            partner_age_mask = (
                (df_work["hh_IsPartner"] == 1) 
                & df_work["dag"].between(*config["age_range"])
            )
            keep_idhh = df_work.loc[partner_age_mask, "idhh"].unique()
            df_work = df_work[df_work["idhh"].isin(keep_idhh)]
        
        heads = df_work[df_work["hh_IsHead"] == 1]
        total = heads["idhh"].nunique()
        female = heads[heads["dgn"] == 0]["idhh"].nunique() if "dgn" in heads.columns else 0
        male = heads[heads["dgn"] == 1]["idhh"].nunique() if "dgn" in heads.columns else 0
        stats.append({
            "Step": "Age (Partner)",
            "Total Households": total,
            "Female Heads": female,
            "Male Heads": male,
            "% Remaining": round(100 * total / initial_households, 2),
        })
        
        # Education (Partner)
        if "hh_IsPartner" in df_work.columns and "dec" in df_work.columns:
            partner_edu_mask = (df_work["hh_IsPartner"] == 1) & (df_work["dec"] == 0)
            keep_idhh = df_work.loc[partner_edu_mask, "idhh"].unique()
            df_work = df_work[df_work["idhh"].isin(keep_idhh)]
        
        heads = df_work[df_work["hh_IsHead"] == 1]
        total = heads["idhh"].nunique()
        female = heads[heads["dgn"] == 0]["idhh"].nunique() if "dgn" in heads.columns else 0
        male = heads[heads["dgn"] == 1]["idhh"].nunique() if "dgn" in heads.columns else 0
        stats.append({
            "Step": "Education (Partner)",
            "Total Households": total,
            "Female Heads": female,
            "Male Heads": male,
            "% Remaining": round(100 * total / initial_households, 2),
        })
    
    # Step: Other Household Members
    df_work = apply_other_members_filter(df_work, config)
    heads = df_work[df_work["hh_IsHead"] == 1]
    total = heads["idhh"].nunique()
    female = heads[heads["dgn"] == 0]["idhh"].nunique() if "dgn" in heads.columns else 0
    male = heads[heads["dgn"] == 1]["idhh"].nunique() if "dgn" in heads.columns else 0
    stats.append({
        "Step": "Other Household Members",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    })    # Step: Hours Capping & Wage Filter
    # For employees (les == 3) who are heads/partners, cap hours instead of filtering:
    #   - lhw > 70: cap to 70
    #   - 5 < lhw <= 10: cap to 10 (floor)
    #   - lhw <= 5: set lhw=0 and les=7 (inactive) if les in [3,5,7], else filter out
    # Wage bounds still filter out households
    
    role_mask = df_work["hh_IsHead"] == 1
    if household_type == "couples" and "hh_IsPartner" in df_work.columns:
        role_mask = role_mask | (df_work["hh_IsPartner"] == 1)
    
    wage_col = "wage_final" if "wage_final" in df_work.columns else "w_emp_strict"
    les_col = "les_enforced" if "les_enforced" in df_work.columns else "les"
    
    # Only apply hour capping to employees (les == 3) who are heads/partners
    emp_role_mask = (df_work[les_col] == 3) & role_mask
    
    # Cap hours > 70 to 70
    high_hours_mask = emp_role_mask & (df_work["lhw"] > 70)
    n_capped_high = high_hours_mask.sum()
    df_work.loc[high_hours_mask, "lhw"] = 70
    
    # Cap hours in (5, 10] to 10 (floor from below)
    low_hours_floor_mask = emp_role_mask & (df_work["lhw"] > 5) & (df_work["lhw"] <= 10)
    n_capped_low = low_hours_floor_mask.sum()
    df_work.loc[low_hours_floor_mask, "lhw"] = 10
    
    # Handle very low hours (lhw <= 5): set to 0 and make inactive if les in [3,5,7]
    very_low_hours_mask = emp_role_mask & (df_work["lhw"] <= 5)
    allowed_les_for_inactive = [3, 5, 7]
    can_become_inactive = very_low_hours_mask & df_work[les_col].isin(allowed_les_for_inactive)
    must_filter_out = very_low_hours_mask & ~df_work[les_col].isin(allowed_les_for_inactive)
    
    n_made_inactive = can_become_inactive.sum()
    
    # Set lhw=0 and les=7 for those who can become inactive
    df_work.loc[can_become_inactive, "lhw"] = 0
    df_work.loc[can_become_inactive, les_col] = 7
    
    # Filter out households where member has very low hours but cannot become inactive
    households_to_drop_hours = df_work.loc[must_filter_out, "idhh"].unique()
    n_filtered_hours = len(households_to_drop_hours)
    df_work = df_work[~df_work["idhh"].isin(households_to_drop_hours)]
    
    # Log hour capping results
    logging.info(f"Hours capping [{household_type}]: capped high (>70)->70: {n_capped_high}, "
                 f"capped low (5-10]->10: {n_capped_low}, made inactive (<=5): {n_made_inactive}, "
                 f"filtered out: {n_filtered_hours} households")
    
    # Still filter by wage bounds (abnormal wages)
    wage_abnormal_mask = (
        (df_work[les_col] == 3)  # Only employees
        & role_mask
        & (
            (df_work.get(wage_col, 0) < config["wage_bounds"][0])
            | (df_work.get(wage_col, 0) > config["wage_bounds"][1])
        )
    )
    households_to_drop_wage = df_work.loc[wage_abnormal_mask, "idhh"].unique()
    n_filtered_wage = len(households_to_drop_wage)
    df_work = df_work[~df_work["idhh"].isin(households_to_drop_wage)]
    
    logging.info(f"Wage filter [{household_type}]: filtered {n_filtered_wage} households with abnormal wages")
    
    heads = df_work[df_work["hh_IsHead"] == 1]
    total = heads["idhh"].nunique()
    female = heads[heads["dgn"] == 0]["idhh"].nunique() if "dgn" in heads.columns else 0
    male = heads[heads["dgn"] == 1]["idhh"].nunique() if "dgn" in heads.columns else 0
    stats.append({
        "Step": "Hours Capping & Wage Filter",
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": round(100 * total / initial_households, 2),
    })
    
    stats_df = pd.DataFrame(stats)
    return df_work, stats_df

# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

def _write_dataframe(df: pd.DataFrame, base_path: Path, export_format: str = "parquet") -> Path:
    """Write dataframe to file in specified format."""
    if export_format == "parquet":
        output_path = base_path.with_suffix(".parquet")
        df.to_parquet(output_path, index=False)
    elif export_format == "csv":
        output_path = base_path.with_suffix(".csv")
        df.to_csv(output_path, index=False)
    elif export_format == "pickle":
        output_path = base_path.with_suffix(".pkl")
        df.to_pickle(output_path)
    else:
        raise ValueError(f"Unsupported export format: {export_format}")
    
    return output_path

def export_household_data(
    df: pd.DataFrame,
    stats_df: pd.DataFrame,
    output_prefix: str,
    output_dir: Path,
    processed_dir: Path,
    export_format: str = "parquet",
) -> Dict[str, Any]:
    """Export filtered household data and statistics."""
    ensure_dir(output_dir)
    ensure_dir(processed_dir)
    
    # Export main data
    data_path = _write_dataframe(df, processed_dir / output_prefix, export_format)
    
    # Export statistics
    stats_path = output_dir / f"{output_prefix}_stats.csv"
    stats_df.to_csv(stats_path, index=False)
    
    # Export LaTeX table
    latex_path = output_dir / f"{output_prefix}_stats.tex"
    latex_table = stats_df.to_latex(
        index=False,
        caption=f"Filtering steps for {output_prefix}",
        label=f"tab:{output_prefix}",
        column_format="l" + "r" * (len(stats_df.columns) - 1),
    )
    with open(latex_path, "w") as f:
        f.write(latex_table)
    
    return {
        "data_path": data_path,
        "stats_path": stats_path,
        "latex_path": latex_path,
        "final_households": df["idhh"].nunique(),
        "final_records": len(df),
    }

# =============================================================================
# PLOTTING FUNCTIONS
# =============================================================================

def _plot_distribution(
    series: pd.Series, title: str, output_path: Path, *, discrete: bool, bins: int
) -> None:
    """Save a histogram/bar plot for a series."""
    clean = series.dropna()
    if clean.empty:
        return
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    if discrete or (pd.api.types.is_integer_dtype(clean) and clean.nunique() <= bins / 2):
        value_counts = clean.value_counts().sort_index()
        ax.bar(value_counts.index.astype(str), value_counts.values)
    else:
        ax.hist(clean, bins=bins, edgecolor="black", alpha=0.7)
    
    ax.set_title(title)
    ax.set_xlabel(title.split(" - ")[0])
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

def _generate_group_plots(
    df: pd.DataFrame, *, group_name: str, prefix: str, bins: int, plots_dir: Path
) -> Dict[str, Path]:
    """Create plots for a dataframe group."""
    saved_paths: Dict[str, Path] = {}
    skipped_cols: List[str] = []
    
    for column, info in PLOT_VARIABLES.items():
        if column not in df.columns:
            skipped_cols.append(column)
            continue
        
        output_path = plots_dir / f"{prefix}_{column}.png"
        title = f"{info['label']} - {group_name}"
        _plot_distribution(
            df[column], title, output_path, discrete=info["discrete"], bins=bins
        )
        saved_paths[column] = output_path
    
    if saved_paths:
        logging.info(f"Generated {len(saved_paths)} plots for {group_name}: {list(saved_paths.keys())}")
    if skipped_cols:
        logging.debug(f"Skipped plots (columns not in data): {skipped_cols}")
    
    return saved_paths

# =============================================================================
# MAIN DATA LOADING AND CLEANING (FRANCE)
# =============================================================================

def load_fr_txt(raw_path: Path) -> pd.DataFrame:
    """Load French micro-data stored as tab-delimited text."""
    return pd.read_csv(raw_path, sep="\t")

def clean_harmonize_fr(
    df: pd.DataFrame,
    *,
    country: str = "FR",
    year: int,
    system_year: int,
    model_dir: Path,
    config: Optional[Dict] = None,
) -> pd.DataFrame:
    """
    Run the EUROMOD simulation and cleaning pipeline for French data.
    """
    if config is None:
        config = DEFAULT_CONFIG
    
    setup_logging("INFO")
    
    if em is None:
        raise ImportError("euromod package is required for EUROMOD simulation")
    
    # Run EUROMOD model
    mod = em.Model(str(model_dir))
    
    target_system = f"FR_{system_year}"
    target_dataset = f"FR_{year}_a1"  # Adjust pattern as needed
    
    country_mod = mod["FR"]
    
    # Get system
    try:
        system = country_mod[target_system]
    except KeyError:
        # Try to find closest system
        available_systems = list(country_mod.keys()) if hasattr(country_mod, "keys") else []
        logging.warning(f"System {target_system} not found. Available: {available_systems}")
        raise KeyError(f"EUROMOD system {target_system} not found")
    
    # Get dataset
    dataset = None
    if hasattr(system, "datasets"):
        for ds in system.datasets:
            ds_name = getattr(ds, "name", str(ds))
            if str(year) in ds_name:
                dataset = ds
                break
    
    if dataset is None:
        logging.warning(f"Dataset for year {year} not found. Using default.")
        dataset = system.datasets[0] if hasattr(system, "datasets") and system.datasets else None
    
    system_name = getattr(system, "name", target_system)
    dataset_name = getattr(dataset, "name", target_dataset) if dataset else target_dataset
    logging.info(f"Running EUROMOD system {system_name} with dataset {dataset_name}")
    
    # Run simulation
    sim = system.run(df, dataset_name if dataset else target_dataset)
    df_sim = sim.outputs[0]
    
    logging.info(f"Simulation complete. Output shape: {df_sim.shape}")
    
    # Log available columns for debugging partner/head identification
    tu_cols = [c for c in df_sim.columns if c.startswith("tu_")]
    id_cols = [c for c in df_sim.columns if "id" in c.lower() or "partner" in c.lower()]
    logging.debug(f"Available tu_ columns: {tu_cols[:20]}...")  # Limit output
    logging.debug(f"Available id/partner columns: {id_cols}")
    
    # Household head identification
    # Adjust column names for French data structure
    # Note: EUROMOD French data uses "tu_household_fr_HeadID" (not tu_hh_fr)
    head_id_col = None
    head_col_candidates = [
        "tu_household_fr_HeadID",  # French household head ID
        "tu_hh_fr_HeadID", 
        "tu_hh_HeadID",
        "tu_household_HeadID",
    ]
    for col in head_col_candidates:
        if col in df_sim.columns:
            head_id_col = col
            logging.info(f"Found head ID column: {col}")
            break
    
    if head_id_col and "idperson" in df_sim.columns:
        df_sim["hh_IsHead"] = (df_sim[head_id_col] == df_sim["idperson"]).astype(int)
        logging.info(f"Head identification: {df_sim['hh_IsHead'].sum()} heads identified")
    else:
        # Fallback: assume first person in household is head
        logging.warning("No head ID column found. Using first person in household as head.")
        df_sim["hh_IsHead"] = df_sim.groupby("idhh").cumcount() == 0
        df_sim["hh_IsHead"] = df_sim["hh_IsHead"].astype(int)
    
    # Partner identification - check multiple possible column names
    partner_col = None
    partner_candidates = [
        "tu_hh_fr_IsPartner", "tu_hh_fr_ispartner",
        "tu_hh_IsPartner", "tu_hh_ispartner",
        "IsPartner", "ispartner",
    ]
    for col in partner_candidates:
        if col in df_sim.columns:
            partner_col = col
            logging.info(f"Found partner column: {col}")
            break
    
    if partner_col:
        df_sim["hh_IsPartner"] = (df_sim[partner_col] == 1).astype(int)
        logging.info(f"Partner flag set from column '{partner_col}': {df_sim['hh_IsPartner'].sum()} partners identified")
    elif "idpartner" in df_sim.columns:
        # Derive partner from idpartner column
        logging.info("Deriving partner flag from 'idpartner' column")
        
        # Log idpartner statistics for debugging
        idpartner_stats = df_sim["idpartner"].describe()
        logging.debug(f"idpartner stats: min={df_sim['idpartner'].min()}, max={df_sim['idpartner'].max()}, "
                     f"non-zero count={(df_sim['idpartner'] > 0).sum()}")
        
        # Method 1: A person is a partner if they have a valid idpartner (mutual partner relationship)
        # In EUROMOD data, if person A has idpartner = B, then B should have idpartner = A
        # The partner (non-head) is the one whose idpartner points to the head
        
        if head_id_col and head_id_col in df_sim.columns:
            # Get head info per household
            head_info = df_sim[df_sim["hh_IsHead"] == 1][["idhh", "idperson", "idpartner"]].copy()
            head_info.rename(columns={"idperson": "head_id", "idpartner": "head_partner_id"}, inplace=True)
            
            # Merge back to identify partners
            df_sim = df_sim.merge(head_info[["idhh", "head_id", "head_partner_id"]], on="idhh", how="left")
            
            # A person is a partner if:
            # 1. Their idperson matches the head's idpartner, OR
            # 2. Their idpartner matches the head's idperson (they point to the head as their partner)
            df_sim["hh_IsPartner"] = (
                (
                    (df_sim["idperson"] == df_sim["head_partner_id"]) 
                    | (df_sim["idpartner"] == df_sim["head_id"])
                )
                & (df_sim["hh_IsHead"] != 1)  # Not the head themselves
            ).astype(int)
            
            df_sim.drop(columns=["head_id", "head_partner_id"], inplace=True)
        else:
            # Fallback: anyone with idpartner > 0 who is not a head is potentially a partner
            df_sim["hh_IsPartner"] = (
                (df_sim["idpartner"] > 0) 
                & (df_sim["hh_IsHead"] != 1)
            ).astype(int)
        
        logging.info(f"Partner flag derived from idpartner: {df_sim['hh_IsPartner'].sum()} partners identified")
        
        # If still no partners found, try alternative: use household composition
        if df_sim["hh_IsPartner"].sum() == 0:
            logging.warning("No partners found via idpartner. Trying household composition fallback.")
            # Identify potential partners: adults (age >= 18) who are not head, in same household
            # This is a heuristic: in 2-adult households, the non-head adult is likely the partner
            adults_mask = df_sim["dag"] >= 18 if "dag" in df_sim.columns else pd.Series(True, index=df_sim.index)
            hh_adult_count = df_sim[adults_mask].groupby("idhh").size()
            
            # Households with exactly 2 adults might be couples
            two_adult_hh = hh_adult_count[hh_adult_count == 2].index
            
            # In these households, mark the non-head adult as partner
            df_sim["hh_IsPartner"] = (
                df_sim["idhh"].isin(two_adult_hh)
                & adults_mask
                & (df_sim["hh_IsHead"] != 1)
            ).astype(int)
            
            logging.info(f"Partner flag via household composition fallback: {df_sim['hh_IsPartner'].sum()} partners identified")
    else:
        logging.warning("No partner identification column found. All households will be classified as singles.")
        df_sim["hh_IsPartner"] = 0
    
    # =========================================================================
    # RURO DECIDER FLAG: head + partner are "deciders" for RURO estimation
    # =========================================================================
    # All other household members (children, other adults) are kept in the data
    # for EUROMOD tax-benefit calculations, but will NOT enter RURO estimation.
    df_sim["ruro_decider"] = (
        (df_sim["hh_IsHead"] == 1) | (df_sim["hh_IsPartner"] == 1)
    ).astype(int)
    
    logging.info(
        f"RURO deciders identified: {df_sim['ruro_decider'].sum()} persons "
        f"(heads + partners) out of {len(df_sim)} total"
    )
    
    # Log household structure
    is_single_head = df_sim.groupby("idhh")["hh_IsHead"].sum().eq(1)
    logging.info(f"Households with single head: {is_single_head.sum()}")
    multi_head_count = df_sim.groupby("idhh")["hh_IsHead"].sum().gt(1).sum()
    logging.info(f"Households with multiple heads: {multi_head_count}")
    logging.info(f"Unique households: {df_sim['idhh'].nunique()}")
    
    # Create income aggregates
    df_sim = create_income_columns(df_sim)
    
    # Merge with original data
    if "idperson" in df.columns and "idperson" in df_sim.columns:
        # CRITICAL FIX: Prioritize EUROMOD simulation outputs over input data
        # The old logic kept input values if columns existed in both - this is wrong!
        # EUROMOD outputs (ils_*, lma, lun, lmc, etc.) should REPLACE input values

        # Strategy: Take ALL columns from df_sim, merge with df, keep df_sim versions
        # Step 1: Get columns unique to original df (not in simulation)
        df_only_cols = [c for c in df.columns if c not in df_sim.columns and c != "idperson"]

        # Step 2: Merge simulation output with original data's unique columns
        # Use how="outer" to keep all records from both
        final_df = df_sim.merge(
            df[["idperson"] + df_only_cols],
            on="idperson",
            how="left",
            suffixes=("", "_original")  # Keep df_sim version when conflicts
        )

        logging.info(f"Merged EUROMOD output: {len(df_sim.columns)} sim columns + {len(df_only_cols)} original-only columns")

        # Remove duplicate columns (keep first occurrence, which is from df_sim)
        dup_cols = final_df.columns[final_df.columns.duplicated()].tolist()
        if dup_cols:
            logging.warning(f"Found {len(dup_cols)} duplicate columns, removing: {dup_cols[:10]}...")
            final_df = final_df.loc[:, ~final_df.columns.duplicated()]
            logging.info(f"After de-duplication: {final_df.shape[1]} columns")

        # Log which EUROMOD labor market variables were included
        labor_vars = ["lma", "lun", "lmc", "lhw_a", "lhw_a1", "lhw_a_9", "lhw_a_20"]
        for var in labor_vars:
            if var in final_df.columns:
                std_val = final_df[var].std() if final_df[var].notna().any() else 0
                logging.info(f"  EUROMOD labor variable '{var}': present (std={std_val:.4f})")
            else:
                logging.warning(f"  EUROMOD labor variable '{var}': MISSING from output")
    else:
        final_df = df_sim
    
    # Validate
    required_columns = ["idperson", "idhh", "dag", "dgn", "les"]
    available_required = [c for c in required_columns if c in final_df.columns]
    if len(available_required) < len(required_columns):
        missing = set(required_columns) - set(available_required)
        logging.warning(f"Missing some required columns: {missing}")
    
    validate_household_integrity(final_df)
    
    quality_issues = check_data_quality(final_df)
    if quality_issues:
        for issue in quality_issues[:5]:
            logging.warning(issue)
    
    # Labor status correction
    final_df["les_orig"] = final_df["les"]
    final_df = correct_labor_status(final_df, emp_threshold=100)
    
    # Log reclassifications
    if "les_enforced" in final_df.columns:
        chg = final_df["les_enforced"] != final_df["les_orig"]
        logging.info(f"Labor status changes: {chg.sum()}")
    
    # Wage reconstruction
    final_df = compute_wage_recon(final_df)
    
    # Final wage metrics
    les_col = "les_enforced" if "les_enforced" in final_df.columns else "les"
    valid_emp = final_df[les_col].eq(3) & final_df["lhw"].ge(config["hour_bounds"][0])
    
    final_df["wage_final"] = final_df["w_emp_strict"]
    final_df["yem2_final"] = np.where(
        valid_emp, final_df["wage_final"] * final_df["lhw"] * WPM, np.nan
    )
    
    yem_col = "yem"
    final_df["diff_yem_final"] = np.where(
        valid_emp, final_df["yem2_final"] - final_df[yem_col], np.nan
    )
    
    config["extreme_diff_column"] = "diff_yem_final"
    
    # =========================================================================
    # PERIODICITY DETECTION AND CORRECTION (matching data_prep2.py)
    # =========================================================================
    # Recompute monthly-from-hours (strict)
    yem_from_hours = final_df["w_emp_strict"] * final_df["lhw"] * WPM
    
    # Periodicity tests:
    #  - div12: observed yem looks like annual/12 vs recon monthly
    #  - liwmy: observed yem matches recon scaled by months-worked / 12
    m_div12 = np.isclose(final_df["yem"], yem_from_hours / 12, rtol=0.05, atol=5)
    
    if "liwmy" in final_df.columns:
        m_liwmy = np.isclose(
            final_df["yem"],
            yem_from_hours * (final_df["liwmy"].clip(lower=0, upper=12).fillna(0) / 12),
            rtol=0.10,
            atol=5,
        )
    else:
        m_liwmy = pd.Series(False, index=final_df.index)
    
    final_df["flag_periodicity"] = valid_emp & (m_div12 | m_liwmy)
    
    # Describe which rule triggered the fix (purely informational)
    final_df["periodicity_type"] = np.select(
        [valid_emp & m_div12, valid_emp & m_liwmy],
        ["div12", "liwmy"],
        default=""
    )
    
    # Correct yem for periodicity; otherwise keep observed
    final_df["yem_corrected"] = np.where(final_df["flag_periodicity"], yem_from_hours, final_df["yem"])
    
    # Update diff_yem_final to use corrected yem
    final_df["diff_yem_final"] = np.where(
        valid_emp, final_df["yem2_final"] - final_df["yem_corrected"], np.nan
    )
    
    logging.info(f"Periodicity corrections applied: {final_df['flag_periodicity'].sum()} records flagged")
    
    # =========================================================================
    # EXTREME HOUSEHOLD IDENTIFICATION (matching data_prep2.py)
    # =========================================================================
    # Adult-only screening (exclude minors from outlier test)
    adults = final_df["dag"].fillna(0).ge(18)
    screen_idx = adults & valid_emp & ~final_df["flag_periodicity"].fillna(False)
    
    households_to_remove = identify_extreme_households(final_df.loc[screen_idx], config)
    logging.info(f"Extreme-screened population: {int(screen_idx.sum())} records")
    logging.info(f"Households to remove due to extreme wages: {len(households_to_remove)}")
    
    # =========================================================================
    # ELIGIBILITY FLAGS (matching data_prep2.py)
    # =========================================================================
    is_emp = final_df[les_col].eq(3)
    
    ready_allowed_les = final_df[les_col].isin(config["allowed_les"])
    ready_age = final_df["dag"].between(*config["age_range"])
    
    # Hours bounds apply only to employees; non-employees pass this check
    ready_hours = (~is_emp) | final_df["lhw"].between(*config["hour_bounds"])
    
    # Wage bounds apply only to employees; for non-employees or missing wages, pass
    ready_wage = (
        (~is_emp)
        | final_df["wage_final"].between(*config["wage_bounds"])
        | final_df["wage_final"].isna()
    )
    
    ready_no_unresolved_extreme = ~final_df["idhh"].isin(households_to_remove)
    
    final_df["keep_for_analysis"] = (
        ready_allowed_les & ready_age & ready_hours & ready_wage & ready_no_unresolved_extreme
    )
    
    logging.info(
        f"keep_for_analysis: {int(final_df['keep_for_analysis'].sum())} / {len(final_df)} "
        "rows meet eligibility criteria"
    )
    
    # =========================================================================
    # CHILD COUNTS BY AGE BAND (matching data_prep2.py)
    # =========================================================================
    # Check if parent ID columns exist
    has_parent_cols = "idfather" in final_df.columns and "idmother" in final_df.columns
    
    if has_parent_cols:
        child_bands = {
            "num_children_0_3": final_df["dag"].ge(0) & final_df["dag"].le(3),
            "num_children_3_6": final_df["dag"].gt(3) & final_df["dag"].le(6),
            "num_children_6_11": final_df["dag"].gt(6) & final_df["dag"].le(11),
            "num_children_11_17": final_df["dag"].gt(11) & final_df["dag"].le(17),
        }
        child_flags = pd.DataFrame(child_bands, index=final_df.index)
        
        # Build long table linking each child to each available parent id
        parent_links = pd.concat(
            [child_flags, final_df[["idfather", "idmother"]]],
            axis=1,
        )
        parent_links = parent_links.melt(
            id_vars=list(child_bands.keys()),
            value_vars=["idfather", "idmother"],
            var_name="parent_role",
            value_name="parent_id",
        )
        
        # Keep valid parent ids (non-missing, non-zero)
        valid_parent = parent_links["parent_id"].notna() & parent_links["parent_id"].ne(0)
        
        # Aggregate child-band indicators to the parent_id level
        parent_counts = (
            parent_links.loc[valid_parent]
            .groupby("parent_id")[list(child_bands.keys())]
            .sum()
        )
        
        # Add a total children column
        parent_counts["num_children_total"] = parent_counts.sum(axis=1)
        parent_counts = parent_counts[
            [
                "num_children_total",
                "num_children_0_3",
                "num_children_3_6",
                "num_children_6_11",
                "num_children_11_17",
            ]
        ]
        
        # Merge parent-level child counts back to the person file
        final_df = final_df.merge(
            parent_counts,
            how="left",
            left_on="idperson",
            right_index=True,
        )
        
        # Fill missing counts with 0 and cast to int
        child_cols = parent_counts.columns.tolist()
        final_df[child_cols] = final_df[child_cols].fillna(0).astype(int)
        
        logging.info(f"Child counts created: {child_cols}")
    else:
        logging.warning("Parent ID columns (idfather, idmother) not found. Child counts not created.")
        # Create placeholder columns
        for col in ["num_children_total", "num_children_0_3", "num_children_3_6", 
                    "num_children_6_11", "num_children_11_17"]:
            final_df[col] = 0
    
    # From this point on, use the enforced labour status as canonical
    final_df["les"] = final_df[les_col]
    
    return final_df

# =============================================================================
# HOUSEHOLD TYPE SEPARATION
# =============================================================================

def separate_household_types(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Separate households into couples and singles based on presence of partner.
    
    Returns:
        Tuple of (couples_df, singles_df)
    """
    # Identify households with partners
    if "hh_IsPartner" in df.columns:
        hh_has_partner = df.groupby("idhh")["hh_IsPartner"].max()
        couple_idhh = hh_has_partner[hh_has_partner == 1].index
        single_idhh = hh_has_partner[hh_has_partner == 0].index
    else:
        # Fallback: count adults per household
        head_count = df.groupby("idhh")["hh_IsHead"].sum()
        # Assume single if only one head and no partner column
        single_idhh = head_count[head_count == 1].index
        couple_idhh = head_count[head_count > 1].index
    
    couples_df = df[df["idhh"].isin(couple_idhh)].copy()
    singles_df = df[df["idhh"].isin(single_idhh)].copy()
    
    return couples_df, singles_df


def filter_singles_by_gender(df: pd.DataFrame, gender: int) -> pd.DataFrame:
    """
    Filter singles dataframe to only include households where the head is of specified gender.
    
    Args:
        df: Singles dataframe
        gender: 0 for female, 1 for male
    
    Returns:
        Filtered dataframe with only households where head matches gender
    """
    # Get households where head has the specified gender
    heads = df[df["hh_IsHead"] == 1]
    matching_idhh = heads[heads["dgn"] == gender]["idhh"].unique()
    
    return df[df["idhh"].isin(matching_idhh)].copy()


# =============================================================================
# MAIN PREPARATION FUNCTION
# =============================================================================

def prepare_one_year(
    *,
    country: str,
    year: int,
    raw_filename: str,
    system_year: Optional[int] = None,
    raw_dir: Optional[Path] = None,
    out_dir: Optional[Path] = None,
    config: Optional[Dict] = None,
) -> Tuple[Path, Dict[str, Any]]:
    """
    Prepare data for one country-year combination.
    
    Args:
        country: Country code (e.g., "FR")
        year: Data year
        raw_filename: Input filename (e.g., "FR_2021.txt")
        system_year: EUROMOD system year (defaults to year - 1)
        raw_dir: Directory containing raw data
        out_dir: Output directory (defaults to processed/{country.lower()}/{year})
        config: Configuration dictionary
    
    Returns:
        Tuple of (output_directory, metadata_dict)
    """
    if config is None:
        config = DEFAULT_CONFIG.copy()
    
    country = country.upper()
    
    if system_year is None:
        system_year = year - 1
    
    if raw_dir is None:
        raw_dir = euromod_raw_root()
    
    if out_dir is None:
        out_dir = ensure_dir(data_root() / "processed" / country.lower() / str(year))
    else:
        out_dir = ensure_dir(Path(out_dir))
    
    outputs_dir = ensure_dir(outputs_root() / "prep" / country.lower() / str(year))
    plots_dir = ensure_dir(outputs_dir / "plots")
    
    raw_path = raw_dir / raw_filename
    
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw data file not found: {raw_path}")
    
    logging.info(f"Loading raw data from: {raw_path}")
    
    # Load data
    if country == "FR":
        df_raw = load_fr_txt(raw_path)
    else:
        df_raw = pd.read_csv(raw_path, sep="\t")
    
    logging.info(f"Loaded {len(df_raw)} records")
    
    # Clean and harmonize
    model_dir = euromod_root()
    
    if country == "FR":
        df_clean = clean_harmonize_fr(
            df_raw,
            country=country,
            year=year,
            system_year=system_year,
            model_dir=model_dir,
            config=config,
        )
    else:
        raise NotImplementedError(f"Country {country} not implemented")
    
    logging.info(f"Cleaned data: {len(df_clean)} records, {df_clean['idhh'].nunique()} households")
    
    # =========================================================================
    # SEPARATE COUPLES AND SINGLES BEFORE FILTERING
    # =========================================================================
    couples_raw, singles_raw = separate_household_types(df_clean)
    
    logging.info(
        f"Separated household types: "
        f"{couples_raw['idhh'].nunique()} couple households, "
        f"{singles_raw['idhh'].nunique()} single households"
    )
    
    # =========================================================================
    # APPLY FILTERING PIPELINE TO COUPLES ONLY
    # =========================================================================
    df_filtered_couples, stats_df_couples = stepwise_filter_households(
        couples_raw, household_type="couples", config=config
    )
    logging.info(
        f"Filtered couples data: {len(df_filtered_couples)} records, "
        f"{df_filtered_couples['idhh'].nunique()} households"
    )
    
    # =========================================================================
    # APPLY FILTERING PIPELINE TO SINGLES ONLY
    # =========================================================================
    df_filtered_singles, stats_df_singles = stepwise_filter_households(
        singles_raw, household_type="singles", config=config
    )
    logging.info(
        f"Filtered singles data: {len(df_filtered_singles)} records, "
        f"{df_filtered_singles['idhh'].nunique()} households"
    )
    
    # =========================================================================
    # COMBINE FILTERED COUPLES AND SINGLES INTO FULL FILTERED DATASET
    # =========================================================================
    df_filtered = pd.concat([df_filtered_couples, df_filtered_singles], ignore_index=True)
    
    logging.info(
        f"Combined filtered data: {len(df_filtered)} records, "
        f"{df_filtered['idhh'].nunique()} households"
    )
    
    # Export results - full dataset
    output_prefix = f"{country.lower()}_{year}"
    
    export_result = export_household_data(
        df_filtered,
        stats_df_couples,  # Use couples stats for main export
        output_prefix,
        outputs_dir,
        out_dir,
        export_format=config.get("export_format", "parquet"),
    )
    
    # =========================================================================
    # EXPORT BY HOUSEHOLD TYPE (from already filtered data)
    # =========================================================================
    # Export couples (already filtered)
    ensure_dir(out_dir)
    household_type_results = {}
    
    if len(df_filtered_couples) > 0:
        couples_path = _write_dataframe(
            df_filtered_couples,
            out_dir / f"{output_prefix}_couples",
            config.get("export_format", "parquet"),
        )
        household_type_results["couples"] = {
            "path": couples_path,
            "households": df_filtered_couples["idhh"].nunique(),
            "records": len(df_filtered_couples),
        }
        logging.info(
            f"Exported couples: {df_filtered_couples['idhh'].nunique()} households, "
            f"{len(df_filtered_couples)} records"
        )
    else:
        logging.warning("No couple households found to export")
        household_type_results["couples"] = {"path": None, "households": 0, "records": 0}
    
    # Export all singles (already filtered)
    if len(df_filtered_singles) > 0:
        singles_path = _write_dataframe(
            df_filtered_singles,
            out_dir / f"{output_prefix}_singles",
            config.get("export_format", "parquet"),
        )
        household_type_results["singles"] = {
            "path": singles_path,
            "households": df_filtered_singles["idhh"].nunique(),
            "records": len(df_filtered_singles),
        }
        logging.info(
            f"Exported singles: {df_filtered_singles['idhh'].nunique()} households, "
            f"{len(df_filtered_singles)} records"
        )
        
        # Export singles by gender
        for gender_code, gender_label in [(0, "female"), (1, "male")]:
            gender_df = filter_singles_by_gender(df_filtered_singles, gender_code)
            
            if len(gender_df) > 0:
                gender_path = _write_dataframe(
                    gender_df,
                    out_dir / f"{output_prefix}_singles_{gender_label}",
                    config.get("export_format", "parquet"),
                )
                household_type_results[f"singles_{gender_label}"] = {
                    "path": gender_path,
                    "households": gender_df["idhh"].nunique(),
                    "records": len(gender_df),
                }
                logging.info(
                    f"Exported singles ({gender_label}): "
                    f"{gender_df['idhh'].nunique()} households, {len(gender_df)} records"
                )
            else:
                logging.warning(f"No single {gender_label} households found")
                household_type_results[f"singles_{gender_label}"] = {
                    "path": None, "households": 0, "records": 0
                }
    else:
        logging.warning("No single households found to export")
        household_type_results["singles"] = {"path": None, "households": 0, "records": 0}
        household_type_results["singles_female"] = {"path": None, "households": 0, "records": 0}
        household_type_results["singles_male"] = {"path": None, "households": 0, "records": 0}
    
    # =========================================================================
    # EXPORT FILTERING STATISTICS FOR SINGLES (CSV + LaTeX)
    # =========================================================================
    singles_stats_path = outputs_dir / f"{output_prefix}_singles_stats.csv"
    stats_df_singles.to_csv(singles_stats_path, index=False)
      # Export LaTeX table for singles statistics
    singles_latex_path = outputs_dir / f"{output_prefix}_singles_stats.tex"
    singles_latex_table = stats_df_singles.to_latex(
        index=False,
        caption=f"Filtering steps for {output_prefix} singles",
        label=f"tab:{output_prefix}_singles",
        column_format="l" + "r" * (len(stats_df_singles.columns) - 1),
    )
    with open(singles_latex_path, "w") as f:
        f.write(singles_latex_table)
    
    logging.info(f"Exported singles statistics: {singles_stats_path}, {singles_latex_path}")
    
    # =========================================================================
    # GENERATE PLOTS FOR EACH GROUP
    # =========================================================================
    plot_bins = config.get("plot_bins", 40)
    
    # Overall combined plots
    _generate_group_plots(
        df_filtered,
        group_name=f"{country} {year} (All)",
        prefix=f"{output_prefix}_all",
        bins=plot_bins,
        plots_dir=plots_dir,
    )
    
    # Couples plots
    if len(df_filtered_couples) > 0:
        _generate_group_plots(
            df_filtered_couples,
            group_name=f"{country} {year} Couples",
            prefix=f"{output_prefix}_couples",
            bins=plot_bins,
            plots_dir=plots_dir,
        )
    
    # Singles plots
    if len(df_filtered_singles) > 0:
        _generate_group_plots(
            df_filtered_singles,
            group_name=f"{country} {year} Singles",
            prefix=f"{output_prefix}_singles",
            bins=plot_bins,
            plots_dir=plots_dir,
        )
        
        # Singles female plots
        singles_female_df = filter_singles_by_gender(df_filtered_singles, 0)
        if len(singles_female_df) > 0:
            _generate_group_plots(
                singles_female_df,
                group_name=f"{country} {year} Singles (Female)",
                prefix=f"{output_prefix}_singles_female",
                bins=plot_bins,
                plots_dir=plots_dir,
            )
        
        # Singles male plots
        singles_male_df = filter_singles_by_gender(df_filtered_singles, 1)
        if len(singles_male_df) > 0:
            _generate_group_plots(
                singles_male_df,
                group_name=f"{country} {year} Singles (Male)",
                prefix=f"{output_prefix}_singles_male",
                bins=plot_bins,
                plots_dir=plots_dir,
            )
    
    meta = {
        "country": country,
        "year": year,
        "system_year": system_year,
        "raw_file": str(raw_path),
        "output_dir": str(out_dir),
        "final_households": df_filtered["idhh"].nunique(),
        "final_records": len(df_filtered),
        "couples_households_raw": couples_raw["idhh"].nunique(),
        "singles_households_raw": singles_raw["idhh"].nunique(),
        "couples_households_filtered": df_filtered_couples["idhh"].nunique(),
        "singles_households_filtered": df_filtered_singles["idhh"].nunique(),
        "export_result": export_result,
        "household_type_results": household_type_results,
        "couples_stats": stats_df_couples.to_dict(),
        "singles_stats": stats_df_singles.to_dict(),
    }
    
    return out_dir, meta

# =============================================================================
# CLI INTERFACE
# =============================================================================

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Prepare French EUROMOD data for analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python france_data_prep.py --year 2021
  python france_data_prep.py --year 2015 --raw-dir /path/to/data
  python france_data_prep.py --year 2021 --out-dir ./output
        """,
    )
    
    parser.add_argument(
        "--year", "-y",
        type=int,
        required=True,
        help="Data year to process (e.g., 2021)",
    )
    
    parser.add_argument(
        "--raw-dir",
        type=str,
        default=None,
        help="Directory containing raw data files (default: auto-detect)",
    )
    
    parser.add_argument(
        "--out-dir",
        type=str,
        default=None,
        help="Output directory for processed data (default: processed/fr/{year})",
    )
    
    parser.add_argument(
        "--raw-filename",
        type=str,
        default=None,
        help="Override input filename (default: FR_{year}.txt)",
    )
    
    parser.add_argument(
        "--system-year",
        type=int,
        default=None,
        help="EUROMOD system year (default: year - 1)",
    )
    
    parser.add_argument(
        "--export-format",
        type=str,
        choices=["parquet", "csv", "pickle"],
        default="parquet",
        help="Output file format (default: parquet)",
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )
    
    return parser.parse_args()

def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    setup_logging(args.log_level)
    
    country = "FR"
    year = args.year
    system_year = args.system_year if args.system_year else year - 1
    
    # Determine raw filename
    if args.raw_filename:
        raw_filename = args.raw_filename
    else:
        raw_filename = f"FR_{year}.txt"
    
    # Parse directories
    raw_dir = Path(args.raw_dir) if args.raw_dir else None
    out_dir = Path(args.out_dir) if args.out_dir else None
    
    # Build config
    config = DEFAULT_CONFIG.copy()
    config["export_format"] = args.export_format
    
    logging.info(f"Processing {country} {year}")
    logging.info(f"EUROMOD system year: {system_year}")
    logging.info(f"Raw filename: {raw_filename}")
    
    try:
        out_dir, meta = prepare_one_year(
            country=country,
            year=year,
            raw_filename=raw_filename,
            system_year=system_year,
            raw_dir=raw_dir,
            out_dir=out_dir,
            config=config,
        )
        
        logging.info(f"Processing complete!")
        logging.info(f"Output directory: {out_dir}")
        logging.info(f"Final households: {meta['final_households']}")
        logging.info(f"Final records: {meta['final_records']}")
        
        print("\n" + "=" * 60)
        print(f"FR {year} prepared with system-year {system_year}")
        print(f"Output dir: {out_dir}")
        print(f"Households: {meta['final_households']}")
        print(f"Records: {meta['final_records']}")
        print("=" * 60)
        
    except Exception as e:
        logging.error(f"Error processing data: {e}")
        raise

if __name__ == "__main__":
    main()
