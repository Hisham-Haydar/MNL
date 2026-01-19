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

# Standard library
import argparse
import datetime
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import copy
# Third-party
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
        ensure_dir,
        euromod_raw_root,
        euromod_root,
        outputs_root,
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
    "age_range": (18, 65),
    "allowed_les": [3, 5, 7],
    "extreme_wage_diff": 500,
    "wage_bounds": (2, 170),
    "hours_cap_high": 70,
    "hours_floor_low": 10,
    "hours_inactive_threshold": 5,
    "export_format": "parquet",
    "plot_bins": 40,
}

PLOT_VARIABLES = {
    "lhw": {"label": "Weekly hours worked (lhw)", "discrete": False},
    "yivwg": {"label": "Gross wage (yivwg)", "discrete": False},
    "ils_disp": {"label": "Disposable income (ils_disp)", "discrete": False},
    "yem": {"label": "TOTAL Employment income (yem)", "discrete": False},
    "yem00": {"label": "Employment income regular (yem00)", "discrete": False},
    "yemxp": {"label": "Employment income overtime (yemxp)", "discrete": False},
    "yem_emp_annual": {"label": "Employment income annual (canonical)", "discrete": False},
    "yem_emp_monthly": {"label": "Employment income monthly (RURO)", "discrete": False},
    "wage_final": {"label": "Hourly wage (wage_final)", "discrete": False},
    "les": {"label": "Labour status code (les)", "discrete": True},
    "loc": {"label": "Occupation class (loc)", "discrete": True},
    "lindi": {"label": "Industry class (lindi)", "discrete": True},
    "dag": {"label": "Age (dag)", "discrete": False},
    "dehde": {"label": "Highest education (dehde)", "discrete": True},
    "deh": {"label": "Highest education simplified (deh)", "discrete": True},
    "num_children_total": {"label": "Number of children", "discrete": True},
    # Discrete regional identifiers (plot if available)
    "drgn1": {"label": "Regional NUTS 1 (drgn1)", "discrete": True},
    "drgn2": {"label": "Regional NUTS 2 (drgn2)", "discrete": True},
    "liwftmy": {"label": "Full time months per year", "discrete": False},
    "liwptmy": {"label": "Part time months per year", "discrete": False},
    "liwmy": {"label": "worked months per year", "discrete": False},
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

def _stamp_years(df: pd.DataFrame, *, data_year: int, system_year: int) -> pd.DataFrame:
    """
    Stamp stable year columns into df:
      - data_year: integer data year (e.g., 2016)
      - system_year: integer EUROMOD system year (e.g., 2015)
      - input_year: alias to data_year for backward compatibility
    """
    df = df.copy()
    df["data_year"] = np.int16(data_year)
    df["system_year"] = np.int16(system_year)
    df["input_year"] = np.int16(data_year)
    return df

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

# -----------------------------------------------------------------------------
# Utility: ensure required columns exist (normalisation layer)
# -----------------------------------------------------------------------------

def ensure_columns(df: pd.DataFrame, defaults: Dict[str, Any]) -> pd.DataFrame:
    """
    Ensure columns exist in df; if missing create them with default values.
    Defaults can be scalars, Series, or callables f(df) -> scalar/Series.
    Created values are aligned to df.index as Series.
    """
    df = df.copy()
    for col, default in defaults.items():
        if col in df.columns:
            continue
        if callable(default):
            val = default(df)
        else:
            val = default
        # Align to index: if not a Series, make a Series broadcasted to index
        if not isinstance(val, pd.Series):
            # Use pandas API to detect scalar values and broadcast them explicitly.
            # This avoids ambiguous overload resolution for pd.Series when static code checkers
            # cannot determine if `val` is scalar or an iterable/map.
            try:
                from pandas.api.types import is_scalar  # local import to avoid polluting module-level namespace
                if is_scalar(val):
                    # Broadcast scalar to full index
                    val = pd.Series([val] * len(df), index=df.index)
                else:
                    # val is iterable-like or mapping; construct Series aligned to index
                    val = pd.Series(val, index=df.index)
            except Exception:
                # Fallback conservative construction
                val = pd.Series(val, index=df.index)
        else:
            # ensure index alignment
            val = val.reindex(df.index).fillna(val.iat[0] if len(val) else np.nan)
        df[col] = val
        logging.debug(f"ensure_columns: added missing column '{col}' with default")
    return df


# -----------------------------------------------------------------------------
# Utility: collect head statistics (deduplicate repeated code)
# -----------------------------------------------------------------------------

# Test compilation of the suspect functions
def get_head_stats(df_work: pd.DataFrame, step: str, initial_households: int) -> Dict[str, Any]:
    """
    Compute head-level statistics used in stepwise_filter_households.
    """
    if "hh_IsHead" in df_work.columns:
        head_mask = df_work["hh_IsHead"].eq(1)
        heads = df_work.loc[head_mask]
        
        if "idhh" in heads.columns:
            total = int(heads["idhh"].nunique())
        else:
            logging.warning("Column 'idhh' not found in heads DataFrame when computing total households.")
            total = 0

        if "dgn" in heads.columns:
            female = int(heads.loc[heads["dgn"] == 0, "idhh"].nunique())
            male = int(heads.loc[heads["dgn"] == 1, "idhh"].nunique())
        else:
            female = 0
            male = 0

        assert initial_households >= 0, "initial_households should not be negative"
        pct = round(100 * total / initial_households, 2) if initial_households > 0 else 0.0
    else:
        total = 0
        female = 0
        male = 0
        pct = 0.0

    return {
        "Step": step,
        "Total Households": total,
        "Female Heads": female,
        "Male Heads": male,
        "% Remaining": pct,
    }


# =============================================================================
# INCOME CREATION FUNCTIONS
# =============================================================================

def create_income_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Create standardized income aggregate columns."""
    df = df.copy()

    if ("yem00" in df.columns) and ("yemxp" in df.columns):
        df["income_employment"] = df["yem00"].fillna(0) + df["yemxp"].fillna(0)
    elif "yem" in df.columns:
        df["income_employment"] = df["yem"].fillna(0)
    else:
        df["income_employment"] = 0.0

    if "yse" in df.columns:
        df["income_self_employment"] = df["yse"].fillna(0)

    market_cols = ["yem", "yse", "yiy", "ypt"]
    available_market = [c for c in market_cols if c in df.columns]
    if available_market:
        df["income_market"] = df[available_market].fillna(0).sum(axis=1)

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
        7 = Inactive
        8 = Sick
        9 = Other
        10 = Family worker
    """
    df = df.copy()

    # Build yem: prefer yem00 + yemxp if at least one of those DRD components exists,
    # otherwise fall back to yem (if present), else zeros.
    if ("yem00" in df.columns) or ("yemxp" in df.columns):
        yem00 = df["yem00"].fillna(0) if "yem00" in df.columns else pd.Series(0, index=df.index)
        yemxp = df["yemxp"].fillna(0) if "yemxp" in df.columns else pd.Series(0, index=df.index)
        yem = yem00 + yemxp
    elif "yem" in df.columns:
        yem = df["yem"].fillna(0)
    else:
        yem = pd.Series(0, index=df.index)

    # Coerce to numeric floats to avoid type/operation issues with static checkers and ensure elementwise comparisons work
    yem = pd.to_numeric(yem, errors="coerce").fillna(0.0).astype(float)

    yse = df["yse"].fillna(0) if "yse" in df.columns else pd.Series(0, index=df.index)
    yse = pd.to_numeric(yse, errors="coerce").fillna(0.0).astype(float)

    lhw = df["lhw"].fillna(0) if "lhw" in df.columns else pd.Series(0.0, index=df.index)
    lhw = pd.to_numeric(lhw, errors="coerce").fillna(0.0).astype(float)

    les_orig = df["les"].fillna(7) if "les" in df.columns else pd.Series(7, index=df.index)
    les_orig = pd.to_numeric(les_orig, errors="coerce").fillna(7).astype(int)

    les_new = les_orig.copy()

    # Dominance logic: classify based on primary income source
    # Use pandas comparison methods (.gt/.ge) to make intent explicit and satisfy type checkers.
    has_emp_income = yem.gt(emp_threshold)
    has_se_income = yse.gt(yse_threshold)
    working_hours = lhw.ge(hrs_min)

    # Self-employed dominates if yse/yem >= ratio_high
    se_dominates = yse.gt(0) & yem.gt(0) & ((yse / yem.replace(0, np.nan)).ge(ratio_high))
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
def compute_wage_for_ruro(df: pd.DataFrame, config: Optional[Dict] = None) -> pd.DataFrame:
    """
    Build RURO-consistent earnings and hourly wages under the FR-DRD convention.

    DRD CONVENTION (FR 2016, as in your DRD tables):
      - yem, yem00, yemxp are "annualised monthly" amounts:
            yem* = (annual total earnings) / 12
        (equivalently: if someone worked m months, the DRD stores (total over worked months)/12)
      - therefore:
            annual total earnings      = yem* * 12
            monthly earnings (work months) = (yem* * 12) / months_worked

    Key outputs:
      - months_worked                  : months worked in [1,12] (prefer liwmy; fallback liwftmy+liwptmy; then yemmy; else 12)
      - yem_emp_am                     : DRD annualised-monthly employment income (yem00+yemxp if available else yem)
      - yem_emp_annual_total           : annual total employment income = yem_emp_am * 12
      - yem_emp_monthly                : monthly earnings during worked months = yem_emp_annual_total / months_worked
      - wage_final                     : hourly wage (prefer yivwg if plausible; else implied), clipped to [lb, ub] for stability
      - wage_ruro                      : alias of wage_final (downstream-friendly)
      - wage_source                    : 'yivwg' or 'implied_from_yem'
      - yem_recon_monthly              : wage_final * lhw * (52/12)
      - diff_yem_monthly               : yem_recon_monthly - yem_emp_monthly

    Extra diagnostics (non-breaking):
      - wage_implied                   : implied wage from (yem_emp_monthly / monthly_hours)
      - wage_unbounded                 : chosen wage before clipping
      - wage_clipped_flag              : True where chosen wage was outside [lb, ub] and clipped
      - yem00_monthly, yemxp_monthly   : monthly components during worked months (if yem00/yemxp exist)
      - wage_implied_regular/overtime  : purely diagnostic decomposition around REG_HOURS (if yem00/yemxp exist)
    """
    if config is None:
        config = DEFAULT_CONFIG

    df = df.copy()

    # --- Config / constants ---
    lb, ub = config.get("wage_bounds", (2.0, 170.0))
    WPM_local = float(config.get("weeks_per_month", WPM))
    REG_HOURS = float(config.get("regular_hours_weekly", 35.0))

    # ------------------------------------------------------------------
    # 1) Months worked (prefer liwmy; fallback liwftmy+liwptmy; then yemmy)
    # ------------------------------------------------------------------
    months = pd.Series(np.nan, index=df.index, dtype="float64")

    if "liwmy" in df.columns:
        months = pd.to_numeric(df["liwmy"], errors="coerce")

    # fallback: liwftmy + liwptmy if available
    if ("liwftmy" in df.columns) or ("liwptmy" in df.columns):
        liwftmy = pd.to_numeric(df.get("liwftmy", 0.0), errors="coerce").fillna(0.0)
        liwptmy = pd.to_numeric(df.get("liwptmy", 0.0), errors="coerce").fillna(0.0)
        months_fb = liwftmy + liwptmy
        months = months.where(months.notna() & (months > 0), months_fb)

    # optional fallback: yemmy (months in employment from income sheet)
    if "yemmy" in df.columns:
        months_yemmy = pd.to_numeric(df["yemmy"], errors="coerce")
        months = months.where(months.notna() & (months > 0), months_yemmy)

    months = months.fillna(12.0).clip(lower=1.0, upper=12.0).astype("float64")
    df["months_worked"] = months

    # ------------------------------------------------------------------
    # 2) Employment income in DRD "annualised monthly" units
    # ------------------------------------------------------------------
    has_yem00 = "yem00" in df.columns
    has_yemxp = "yemxp" in df.columns
    has_yem = "yem" in df.columns

    yem00 = pd.to_numeric(df["yem00"], errors="coerce") if has_yem00 else pd.Series(np.nan, index=df.index)
    yemxp = pd.to_numeric(df["yemxp"], errors="coerce") if has_yemxp else pd.Series(np.nan, index=df.index)
    yem = pd.to_numeric(df["yem"], errors="coerce") if has_yem else pd.Series(np.nan, index=df.index)

    if has_yem00 or has_yemxp:
        yem00_am = yem00.fillna(0.0) if has_yem00 else pd.Series(0.0, index=df.index)
        yemxp_am = yemxp.fillna(0.0) if has_yemxp else pd.Series(0.0, index=df.index)
        yem_emp_am = yem00_am + yemxp_am
    elif has_yem:
        yem00_am = yem.fillna(0.0)               # treat yem as the total annualised-monthly employment income
        yemxp_am = pd.Series(0.0, index=df.index)
        yem_emp_am = yem00_am
    else:
        yem00_am = pd.Series(0.0, index=df.index)
        yemxp_am = pd.Series(0.0, index=df.index)
        yem_emp_am = pd.Series(0.0, index=df.index)

    # Keep both a clear name and (optionally) a backward-compatible name
    df["yem_emp_am"] = yem_emp_am
    df["yem_emp_annual"] = yem_emp_am  # backward-compatible: this is DRD annualised-monthly, NOT annual total

    # Convert to annual total and then to monthly-in-work-months
    df["yem_emp_annual_total"] = yem_emp_am * 12.0
    df["yem_emp_monthly"] = df["yem_emp_annual_total"] / df["months_worked"]

    # Component monthly earnings during worked months (useful diagnostics)
    df["yem00_monthly"] = (yem00_am * 12.0) / df["months_worked"]
    df["yemxp_monthly"] = (yemxp_am * 12.0) / df["months_worked"]

    # ------------------------------------------------------------------
    # 3) Identify employees and valid hours
    # ------------------------------------------------------------------
    les_col = "les_enforced" if "les_enforced" in df.columns else "les"
    is_emp = df.get(les_col, 0).eq(3)

    lhw = pd.to_numeric(df["lhw"], errors="coerce") if "lhw" in df.columns else pd.Series(np.nan, index=df.index)
    valid_hours = is_emp & lhw.notna() & np.isfinite(lhw) & (lhw > 0.0)

    weekly_hours = lhw.where(valid_hours)
    monthly_hours = weekly_hours * WPM_local  # hours/month

    # ------------------------------------------------------------------
    # 4) Implied hourly wage
    # ------------------------------------------------------------------
    wage_implied = (df["yem_emp_monthly"] / monthly_hours.replace(0.0, np.nan)).where(valid_hours)
    df["wage_implied"] = wage_implied

    # Optional overtime diagnostics (purely diagnostic; does not change wage_final)
    reg_weekly_hours = weekly_hours.clip(upper=REG_HOURS)
    ot_weekly_hours = (weekly_hours - REG_HOURS).clip(lower=0.0)

    reg_monthly_hours = reg_weekly_hours * WPM_local
    ot_monthly_hours = ot_weekly_hours * WPM_local

    df["wage_implied_regular"] = (df["yem00_monthly"] / reg_monthly_hours.replace(0.0, np.nan)).where(valid_hours)
    df["wage_implied_overtime"] = (
        (df["yemxp_monthly"] / ot_monthly_hours.replace(0.0, np.nan)).where(valid_hours & (ot_weekly_hours > 0.0))
    )

    # ------------------------------------------------------------------
    # 5) Prefer yivwg if it behaves like an hourly wage; else use implied
    # ------------------------------------------------------------------
    if "yivwg" in df.columns:
        yivwg = pd.to_numeric(df["yivwg"], errors="coerce")
    else:
        yivwg = pd.Series(np.nan, index=df.index)

    use_yivwg_row = valid_hours & yivwg.notna() & np.isfinite(yivwg) & yivwg.between(lb, ub)
    df["wage_source"] = np.where(use_yivwg_row, "yivwg", "implied_from_yem")

    wage_unbounded = np.where(use_yivwg_row, yivwg, wage_implied)
    wage_unbounded = pd.Series(wage_unbounded, index=df.index, dtype="float64")
    df["wage_unbounded"] = wage_unbounded

    # Identify wages that will be clipped (only among valid employed-hours rows)
    df["wage_clipped_flag"] = valid_hours & wage_unbounded.notna() & ((wage_unbounded < lb) | (wage_unbounded > ub))

    # Enforce positivity + clip for stability in downstream logs/densities
    wage_unbounded = wage_unbounded.where(~valid_hours | (wage_unbounded > 0.0))
    wage_final = wage_unbounded.where(~valid_hours, wage_unbounded.clip(lower=lb, upper=ub))
    wage_final = wage_final.where(valid_hours)  # keep NaN for non-employed / invalid hours

    df["wage_final"] = wage_final
    df["wage_ruro"] = df["wage_final"]

    # ------------------------------------------------------------------
    # 6) Diagnostics: reconstructed earnings vs implied work-month earnings
    # ------------------------------------------------------------------
    df["yem_recon_monthly"] = (df["wage_final"] * monthly_hours).where(valid_hours)
    df["diff_yem_monthly"] = (df["yem_recon_monthly"] - df["yem_emp_monthly"]).where(valid_hours)

    return df

# =============================================================================
# EXTREME HOUSEHOLD IDENTIFICATION
# =============================================================================

def identify_extreme_households(
    df: pd.DataFrame,
    diff_col: str,
    threshold: float,
    hh_col: str = "idhh",
    *,
    use_household_max: bool = True,
    require_finite: bool = True,
) -> np.ndarray:
    """
    Identify households with extreme earnings differences (diagnostic screen).

    This is typically used after constructing:
        diff = yem_recon_monthly - yem_emp_monthly
    to drop households where implied/reconstructed earnings are wildly inconsistent.

    Parameters
    ----------
    df : pd.DataFrame
        Person-level (or alternative-level) dataframe containing household ids.
    diff_col : str
        Column with differences (e.g. "diff_yem_monthly").
    threshold : float
        Household is flagged if |diff| >= threshold (either row-wise or household-wise).
    hh_col : str, default "idhh"
        Household identifier column.
    use_household_max : bool, default True
        If True: compute max(|diff|) within each household and flag if that max >= threshold.
        If False: flag households if any row satisfies |diff| >= threshold (equivalent logic,
        but less explicit and slightly more fragile when data contain duplicates).
    require_finite : bool, default True
        If True: ignore NaN/+/-inf values when screening (only finite diffs count).

    Returns
    -------
    np.ndarray
        Unique household ids to remove.
    """
    # Basic guards
    if diff_col not in df.columns:
        return np.array([], dtype=df[hh_col].dtype if hh_col in df.columns else object)
    if hh_col not in df.columns:
        return np.array([], dtype=object)

    # Coerce diff to numeric robustly (strings -> NaN)
    diff = pd.to_numeric(df[diff_col], errors="coerce")

    if require_finite:
        finite_mask = np.isfinite(diff.to_numpy(dtype="float64", copy=False))
        # if nothing finite, nothing to flag
        if not finite_mask.any():
            return np.array([], dtype=df[hh_col].dtype)
        work = df.loc[finite_mask, [hh_col]].copy()
        work["_absdiff"] = diff.loc[finite_mask].abs().to_numpy()
    else:
        work = df[[hh_col]].copy()
        work["_absdiff"] = diff.abs().to_numpy()

    if use_household_max:
        # Household-level maximum absolute difference
        hh_max = work.groupby(hh_col, sort=False)["_absdiff"].max()
        extreme_hh = hh_max.index[hh_max >= float(threshold)].to_numpy()
    else:
        # Any-row logic
        extreme_hh = work.loc[work["_absdiff"] >= float(threshold), hh_col].unique()

    return extreme_hh

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
    Drop households where non-head/non-partner members have meaningful work capacity
    or meaningful labour income (employee or self-employment).

    This is a *sample selection* choice: it makes the RURO decision unit cleaner,
    but it can reduce representativeness (adult children, multi-family households).
    """
    if config is None:
        config = DEFAULT_CONFIG

    df_work = df.copy()

    if "idhh" not in df_work.columns or "hh_IsHead" not in df_work.columns or "dag" not in df_work.columns:
        # If the structural identifiers aren't there, do nothing safely.
        return df_work

    # Safe column fetchers (always return Series aligned with df_work.index)
    hh_is_partner = df_work["hh_IsPartner"] if "hh_IsPartner" in df_work.columns else pd.Series(0, index=df_work.index)
    ddi = df_work["ddi"] if "ddi" in df_work.columns else pd.Series(0, index=df_work.index)
    dec = df_work["dec"] if "dec" in df_work.columns else pd.Series(0, index=df_work.index)

    yem = pd.to_numeric(df_work["yem"], errors="coerce") if "yem" in df_work.columns else pd.Series(0.0, index=df_work.index)
    yse = pd.to_numeric(df_work["yse"], errors="coerce") if "yse" in df_work.columns else pd.Series(0.0, index=df_work.index)

    income_thr = float(config.get("other_member_income_threshold", 50.0))

    non_decider = (df_work["hh_IsHead"] == 0) & (hh_is_partner == 0)

    working_age_healthy_not_student = (
        df_work["dag"].between(*config["age_range"])
        & (ddi == 0)
        & (dec == 0)
    )

    has_meaningful_income = (yem > income_thr) | (yse.abs() > income_thr)

    cond = non_decider & (working_age_healthy_not_student | has_meaningful_income)

    households_to_drop = df_work.loc[cond, "idhh"].unique()
    return df_work.loc[~df_work["idhh"].isin(households_to_drop)].copy()


# =============================================================================
# stepwise_filter_households
# =============================================================================


def stepwise_filter_households(
    df: pd.DataFrame, household_type: str = "couples", config: Optional[Dict] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Perform stepwise filtering on households.

    Steps: Baseline, Age, Education, Retirement/Disability (HH level), Allowed LES,
           Age (Partner), Education (Partner), Opposite-Sex Couples (couples only),
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
        empty_stats = pd.DataFrame(
            [
                {
                    "Step": "Baseline",
                    "Total Households": 0,
                    "Female Heads": 0,
                    "Male Heads": 0,
                    "% Remaining": 0.0,
                }
            ]
        )
        return df_work, empty_stats

    # Baseline
    stats.append(get_head_stats(df_work, "Baseline", initial_households))

    # Step 1: Age (Head)
    age_mask = (df_work["hh_IsHead"] == 1) & df_work["dag"].between(*config["age_range"])
    keep_idhh = df_work.loc[age_mask, "idhh"].unique()
    df_work = df_work[df_work["idhh"].isin(keep_idhh)]
    stats.append(get_head_stats(df_work, "Age (Head)", initial_households))

    # Step 2: Education (Head) - dec == 0 means not currently in education
    if "dec" in df_work.columns:
        edu_mask = (df_work["hh_IsHead"] == 1) & (df_work["dec"] == 0)
        keep_idhh = df_work.loc[edu_mask, "idhh"].unique()
        df_work = df_work[df_work["idhh"].isin(keep_idhh)]
    stats.append(get_head_stats(df_work, "Education (Head)", initial_households))

    # =========================================================================
    # Step 3: Retirement/Disability Benefits (Household level)
    # =========================================================================
    if "benefit_retire_disab" in df_work.columns:
        hh_retire_sum = df_work.groupby("idhh")["benefit_retire_disab"].sum(min_count=1).fillna(0.0)
        hh_retire_flag = hh_retire_sum.gt(0)
        hh_to_keep = hh_retire_sum.index[hh_retire_sum.eq(0.0)]
    else:
        hh_to_keep = df_work["idhh"].unique()

    before_count = df_work["idhh"].nunique()
    df_work = df_work[df_work["idhh"].isin(hh_to_keep)]
    after_count = df_work["idhh"].nunique()
    log_filtering_step("Retirement/Disability Benefits (Any Member)", before_count, after_count)
    stats.append(get_head_stats(df_work, "Retirement/Disability (HH level)", initial_households))

    # =========================================================================
    # Step 4: Allowed LES (RURO deciders: Head + Partner)
    #   This enforces that ALL deciders (head + partner) have les in allowed_les = [3, 5, 7]
    #   Excluded: les=1 (Farmer, intentional for French data), les=2 (Self-employed)
    #   This household-level filter ensures all downstream deciders have valid LES status
    # =========================================================================
    les_col = "les_enforced" if "les_enforced" in df_work.columns else "les"

    if "ruro_decider" in df_work.columns:
        decider_mask = df_work["ruro_decider"].eq(1)
    else:
        # fallback if ruro_decider not present for some reason
        decider_mask = df_work["hh_IsHead"].eq(1)
        if household_type == "couples" and "hh_IsPartner" in df_work.columns:
            decider_mask = decider_mask | df_work["hh_IsPartner"].eq(1)

    bad_hh = df_work.loc[
        decider_mask & ~df_work[les_col].isin(config["allowed_les"]),
        "idhh",
    ].unique()

    before_count = df_work["idhh"].nunique()
    df_work = df_work[~df_work["idhh"].isin(bad_hh)]
    after_count = df_work["idhh"].nunique()
    log_filtering_step("Allowed LES (Deciders)", before_count, after_count)

    stats.append(get_head_stats(df_work, "Allowed LES (Deciders)", initial_households))

    # Partner steps (for couples only)
    if household_type == "couples":
        # Age (Partner)
        if "hh_IsPartner" in df_work.columns:
            partner_age_mask = (df_work["hh_IsPartner"] == 1) & df_work["dag"].between(
                *config["age_range"]
            )
            keep_idhh = df_work.loc[partner_age_mask, "idhh"].unique()
            df_work = df_work[df_work["idhh"].isin(keep_idhh)]
        stats.append(get_head_stats(df_work, "Age (Partner)", initial_households))

        # Education (Partner)
        if "hh_IsPartner" in df_work.columns and "dec" in df_work.columns:
            partner_edu_mask = (df_work["hh_IsPartner"] == 1) & (df_work["dec"] == 0)
            keep_idhh = df_work.loc[partner_edu_mask, "idhh"].unique()
            df_work = df_work[df_work["idhh"].isin(keep_idhh)]
        stats.append(get_head_stats(df_work, "Education (Partner)", initial_households))

        # Opposite-Sex Couples Only (RURO labor supply model assumes heterosexual couples)
        # Filter to keep only couples with 1 male + 1 female (dgn: 0=female, 1=male)
        if "dgn" in df_work.columns and "hh_IsHead" in df_work.columns and "hh_IsPartner" in df_work.columns:
            # Get gender composition per household (count males and females among deciders)
            deciders = df_work[(df_work["hh_IsHead"] == 1) | (df_work["hh_IsPartner"] == 1)].copy()
            deciders["dgn_numeric"] = pd.to_numeric(deciders["dgn"], errors="coerce")

            gender_comp = deciders.groupby("idhh")["dgn_numeric"].agg(
                n_female=lambda x: (x == 0).sum(),
                n_male=lambda x: (x == 1).sum()
            )

            # Keep only households with exactly 1 male and 1 female
            opposite_sex_hh = gender_comp[(gender_comp["n_female"] == 1) & (gender_comp["n_male"] == 1)].index

            before_count = df_work["idhh"].nunique()
            df_work = df_work[df_work["idhh"].isin(opposite_sex_hh)]
            after_count = df_work["idhh"].nunique()
            log_filtering_step("Opposite-Sex Couples Only", before_count, after_count)

        stats.append(get_head_stats(df_work, "Opposite-Sex Couples", initial_households))

    # Step: Other Household Members
    df_work = apply_other_members_filter(df_work, config)
    stats.append(get_head_stats(df_work, "Other Household Members", initial_households))

    # Step: Hours Capping & Wage Filter
    # For employees (les == 3) who are heads/partners, cap hours instead of filtering:
    #   - lhw > 70: cap to 70
    #   - 5 < lhw <= 10: cap to 10 (floor)
    #   - lhw <= 5: set lhw=0 and les=7 (inactive) if les in [3,5,7], else filter out
    # Wage bounds still filter out households

    role_mask = df_work["hh_IsHead"] == 1
    if household_type == "couples" and "hh_IsPartner" in df_work.columns:
        role_mask = role_mask | (df_work["hh_IsPartner"] == 1)

    # Use unbounded wage for meaningful screening
    wage_col = "wage_unbounded" if "wage_unbounded" in df_work.columns else (
        "yivwg" if "yivwg" in df_work.columns else None
    )
    les_col = "les_enforced" if "les_enforced" in df_work.columns else "les"

    emp_role_mask = (df_work[les_col] == 3) & role_mask

    cap = config.get("hours_cap_high", 70)
    floor = config.get("hours_floor_low", 10)
    inactive_thr = config.get("hours_inactive_threshold", 5)

    high_hours_mask = emp_role_mask & (df_work["lhw"] > cap)
    n_capped_high = high_hours_mask.sum()
    df_work.loc[high_hours_mask, "lhw"] = cap

    low_hours_floor_mask = emp_role_mask & (df_work["lhw"] > inactive_thr) & (df_work["lhw"] <= floor)
    n_capped_low = low_hours_floor_mask.sum()
    df_work.loc[low_hours_floor_mask, "lhw"] = floor
    very_low_hours_mask = emp_role_mask & (df_work["lhw"] <= inactive_thr)
    
    allowed_les_for_inactive = [3, 5, 7]
    can_become_inactive = very_low_hours_mask & df_work[les_col].isin(allowed_les_for_inactive)
    must_filter_out = very_low_hours_mask & ~df_work[les_col].isin(allowed_les_for_inactive)

    n_made_inactive = can_become_inactive.sum()

    # Transition to inactive: set hours=0 and les=7, but also zero employment income/wage fields
    # to avoid internal inconsistency (les=inactive but positive employment income).
    if can_become_inactive.any():
        df_work.loc[can_become_inactive, "lhw"] = 0
        df_work.loc[can_become_inactive, les_col] = 7

        # Zero common employment income / wage columns where present
        emp_zero_cols = [
            "yem", "yem00", "yemxp", "yse",
            "income_employment", "yem_emp_am", "yem_emp_annual_total",
            "yem_emp_monthly", "yem00_monthly", "yemxp_monthly",
        ]
        for c in emp_zero_cols:
            if c in df_work.columns:
                df_work.loc[can_become_inactive, c] = 0

        # Blank REALIZED wage columns only (preserve wage offers: yivwg, wage_draw)
        for c in ("wage_final", "wage_unbounded", "wage_ruro", "wage_emp_obs"):
            if c in df_work.columns:
                df_work.loc[can_become_inactive, c] = np.nan

    households_to_drop_hours = df_work.loc[must_filter_out, "idhh"].unique()
    n_filtered_hours = len(households_to_drop_hours)
    df_work = df_work[~df_work["idhh"].isin(households_to_drop_hours)]

    logging.info(
        f"Hours capping [{household_type}]: capped high (>70)->70: {n_capped_high}, "
        f"capped low (5-10]->10: {n_capped_low}, made inactive (<=5): {n_made_inactive}, "
        f"filtered out: {n_filtered_hours} households"
    )

    # IMPORTANT: hours were changed above; recompute wage/earnings diagnostics so
    # downstream wage filters and diff-based screens use consistent values.
    try:
        # Recompute RURO wage objects (wage_final, wage_implied, yem_recon_monthly, diff_yem_monthly, ...)
        # compute_wage_for_ruro expects a DataFrame and returns a DataFrame copy.
        df_work = compute_wage_for_ruro(df_work, config=config)
        logging.info(f"Recomputed wage diagnostics after hours capping ({household_type}).")
    except Exception as e:
        # Fail-safe: log warning and continue with existing wage columns (if any)
        logging.warning(f"Failed to recompute wages after hours capping: {e}")
    
    # Wage filter: screen on unbounded/raw wage (before clipping)
    if wage_col is not None and wage_col in df_work.columns:
        w = pd.to_numeric(df_work[wage_col], errors="coerce")
        wage_abnormal_mask = (
            (df_work[les_col] == 3)
            & role_mask
            & w.notna()
            & ((w < config["wage_bounds"][0]) | (w > config["wage_bounds"][1]))
        )
        households_to_drop_wage = df_work.loc[wage_abnormal_mask, "idhh"].unique()
        n_filtered_wage = len(households_to_drop_wage)
        df_work = df_work[~df_work["idhh"].isin(households_to_drop_wage)]

        logging.info(
            f"Wage filter [{household_type}]: filtered {n_filtered_wage} households with abnormal wages"
        )
    else:
        logging.warning(f"Wage filter [{household_type}]: skipped because no wage column present.")

    # Additional filter: remove households where yivwg is outside bounds for workers
    # This ensures RURO_draws (which uses yivwg directly) won't fail
    if "yivwg" in df_work.columns:
        yivwg = pd.to_numeric(df_work["yivwg"], errors="coerce")
        yivwg_abnormal_mask = (
            (df_work[les_col] == 3)
            & role_mask
            & yivwg.notna()
            & ((yivwg < config["wage_bounds"][0]) | (yivwg > config["wage_bounds"][1]))
        )
        households_to_drop_yivwg = df_work.loc[yivwg_abnormal_mask, "idhh"].unique()
        n_filtered_yivwg = len(households_to_drop_yivwg)
        df_work = df_work[~df_work["idhh"].isin(households_to_drop_yivwg)]
        
        if n_filtered_yivwg > 0:
            logging.info(
                f"yivwg bounds filter [{household_type}]: filtered {n_filtered_yivwg} households "
                f"with yivwg outside [{config['wage_bounds'][0]}, {config['wage_bounds'][1]}]"
            )

    stats.append(get_head_stats(df_work, "Hours Capping & Wage Filter", initial_households))

    stats_df = pd.DataFrame(stats)
    return df_work, stats_df


# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

def _write_dataframe(df: pd.DataFrame, base_path: Path, export_format: str = "parquet") -> Path:
    """Write dataframe to file in specified format."""
    base_path = Path(base_path)

    if export_format == "parquet":
        output_path = base_path.with_suffix(".parquet")
        # Prefer pyarrow if available; compression is usually beneficial.
        try:
            df.to_parquet(output_path, index=False, engine="pyarrow", compression="snappy")
        except Exception as e:
            logging.warning(f"to_parquet(pyarrow) failed ({e}); retrying with default engine.")
            df.to_parquet(output_path, index=False)  # fallback to whatever is installed
    elif export_format == "csv":
        output_path = base_path.with_suffix(".csv")
        df.to_csv(output_path, index=False, encoding="utf-8")
    elif export_format == "pickle":
        output_path = base_path.with_suffix(".pkl")
        df.to_pickle(output_path)
    else:
        raise ValueError(f"Unsupported export format: {export_format}")

    return output_path


def export_stats(stats_df: pd.DataFrame, outputs_dir: Path, prefix: str) -> Tuple[Path, Path]:
    """Export a stats DataFrame to CSV and LaTeX and return paths."""
    ensure_dir(outputs_dir)

    stats_path = outputs_dir / f"{prefix}.csv"
    stats_df.to_csv(stats_path, index=False, encoding="utf-8")

    latex_path = outputs_dir / f"{prefix}.tex"
    # escape=True is safer for LaTeX; if you *want* underscores etc. unescaped, set escape=False.
    latex_table = stats_df.to_latex(
        index=False,
        caption=f"Filtering steps for {prefix}",
        label=f"tab:{prefix}",
        column_format="l" + "r" * max(0, (len(stats_df.columns) - 1)),
        escape=True,
    )
    latex_path.write_text(latex_table, encoding="utf-8")

    logging.info(f"Exported stats: {stats_path}, {latex_path}")
    return stats_path, latex_path

def export_household_data(
    df: pd.DataFrame,
    stats_df: pd.DataFrame,
    output_prefix: str,
    output_dir: Path,
    processed_dir: Path,
    export_format: str = "parquet",
) -> Dict[str, Any]:
    """
    Export filtered household data and statistics.

    Notes:
      - returns *string paths* so the result dict can be JSON-serialized safely.
    """
    ensure_dir(output_dir)
    ensure_dir(processed_dir)

    data_path = _write_dataframe(df, processed_dir / output_prefix, export_format)
    stats_path, latex_path = export_stats(stats_df, output_dir, f"{output_prefix}_stats")

    return {
        "data_path": str(data_path),
        "stats_path": str(stats_path),
        "latex_path": str(latex_path),
        "final_households": int(df["idhh"].nunique()) if "idhh" in df.columns else None,
        "final_records": int(len(df)),
    }


def _generate_group_plots(df: pd.DataFrame, *, group_name: str, prefix: str, bins: int, plots_dir: Path) -> None:
    """
    Minimal placeholder for plotting.
    Creates plots_dir if missing and logs that plotting was requested.
    """
    ensure_dir(plots_dir)
    logging.info(f"Plot generation requested for {group_name} (prefix={prefix}), {len(df)} rows — stub invoked.")


def load_fr_txt(raw_path: Path) -> pd.DataFrame:
    """Load French micro-data stored as tab-delimited text. Try fast engine then fallback."""
    raw_path = Path(raw_path)
    logging.info(f"Reading raw file: {raw_path}")
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw file not found: {raw_path}")

    try:
        return pd.read_csv(raw_path, sep="\t", engine="c", low_memory=False)
    except Exception as e:
        logging.warning(f"C-engine read failed ({e}), retrying with engine='python' and encoding fallbacks")

    # Python engine + robust decoding
    try:
        return pd.read_csv(raw_path, sep="\t", engine="python", encoding="utf-8", encoding_errors="replace")
    except Exception:
        return pd.read_csv(raw_path, sep="\t", engine="python", encoding="latin1", encoding_errors="replace")


def clean_harmonize_fr(
    df: pd.DataFrame,
    *,
    country: str = "FR",
    year: int,
    system_year: int,
    model_dir: Path,
    config: Optional[Dict] = None,
    A_cols: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Run the EUROMOD simulation and cleaning pipeline for French data.

    Returns:
        Tuple of (cleaned_dataframe, column_groups_dict)
        where column_groups_dict contains:
            - A_cols: columns from raw EUROMOD template
            - B_cols: columns created before EUROMOD run
            - C_cols: columns created by EUROMOD simulation
            - euromod_system: EUROMOD system name
            - euromod_dataset: EUROMOD dataset name
    """
    if config is None:
        config = DEFAULT_CONFIG
    # Work on a local copy to avoid mutating caller's config (prevents side-effects
    # when running multiple countries/years in the same process)
    config = dict(config)

    # Track A_cols: columns from raw EUROMOD template at input
    if A_cols is None:
        A_cols = list(df.columns)

    # Track columns created before EUROMOD (B_cols will be computed later)
    initial_cols = set(df.columns)

    if em is None:
        raise ImportError("euromod package is required for EUROMOD simulation")

    # Run EUROMOD model
    logging.info(f"Loading EUROMOD model from: {model_dir}")
    logging.info("This may take several minutes if model is on network drive...")
    import time
    model_load_start = time.time()
    mod = em.Model(str(model_dir))
    model_load_elapsed = time.time() - model_load_start
    logging.info(f"EUROMOD model loaded in {model_load_elapsed:.1f} seconds")

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

    # =========================================================================
    # PRESERVE BASELINE LABOUR-INPUT REFERENCE (Goal 5)
    # =========================================================================
    # Create baseline copies of key labour inputs before EUROMOD simulation
    # This ensures downstream enh_RURO_draws.py can guarantee draw=0 reproduces baseline
    baseline_labor_cols = []

    # Core labour input columns
    if "lhw" in df.columns:
        df["lhw_base"] = df["lhw"].copy()
        baseline_labor_cols.append("lhw_base")

    if "yivwg" in df.columns:
        df["yivwg_base"] = df["yivwg"].copy()
        baseline_labor_cols.append("yivwg_base")

    # Additional EUROMOD employment/wage columns if present
    for col in ["yem00", "yemxp", "yem"]:
        if col in df.columns:
            baseline_col = f"{col}_base"
            df[baseline_col] = df[col].copy()
            baseline_labor_cols.append(baseline_col)

    if baseline_labor_cols:
        logging.info(f"Created baseline labour input columns: {baseline_labor_cols}")

    # =========================================================================
    # EUROMOD INPUT/OUTPUT BOUNDARY - Capture column groups
    # =========================================================================
    # Snapshot the dataframe before EUROMOD to compute B_cols and C_cols
    euromod_input_df = df
    B_cols = sorted(set(euromod_input_df.columns) - set(A_cols))

    # Sanity log: EUROMOD input
    logging.info(
        f"EUROMOD input: {len(euromod_input_df)} rows, {len(euromod_input_df.columns)} columns"
    )

    # Run simulation
    logging.info("Starting EUROMOD simulation (this may take several minutes)...")
    import time
    start_time = time.time()
    sim = system.run(euromod_input_df, dataset_name if dataset else target_dataset)
    elapsed = time.time() - start_time
    logging.info(f"EUROMOD simulation completed in {elapsed:.1f} seconds")

    euromod_output_df = sim.outputs[0]

    # Sanity log: EUROMOD output
    logging.info(
        f"EUROMOD output: {len(euromod_output_df)} rows, {len(euromod_output_df.columns)} columns"
    )

    # Compute C_cols: columns that appeared only after EUROMOD
    C_cols = sorted(set(euromod_output_df.columns) - set(euromod_input_df.columns))

    # Sanity log: C_cols preview
    C_cols_preview = C_cols[:20] if len(C_cols) > 20 else C_cols
    logging.info(
        f"EUROMOD created {len(C_cols)} new columns (C_cols). Preview: {C_cols_preview}"
    )

    # =========================================================================
    # STORE EUROMOD I/O COLUMN SIGNATURES (Goal 6)
    # =========================================================================
    # Capture full column lists for auditable ABC boundary enforcement
    euromod_input_cols = sorted(euromod_input_df.columns.tolist())
    euromod_output_cols = sorted(euromod_output_df.columns.tolist())

    # Continue with euromod_output_df (renamed from df_sim for clarity)
    df_sim = euromod_output_df

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
        "tu_hh_fr_IsPartner",
        "tu_hh_fr_ispartner",
        "tu_hh_IsPartner",
        "tu_hh_ispartner",
        "IsPartner",
        "ispartner",
    ]
    for col in partner_candidates:
        if col in df_sim.columns:
            partner_col = col
            logging.info(f"Found partner column: {col}")
            break

    if partner_col:
        df_sim["hh_IsPartner"] = (df_sim[partner_col] == 1).astype(int)
        logging.info(
            f"Partner flag set from column '{partner_col}': {df_sim['hh_IsPartner'].sum()} partners identified"
        )
    elif "idpartner" in df_sim.columns:
        # Derive partner from idpartner column
        logging.info("Deriving partner flag from 'idpartner' column")

        # Log idpartner statistics for debugging
        logging.debug(
            f"idpartner stats: min={df_sim['idpartner'].min()}, max={df_sim['idpartner'].max()}, "
            f"non-zero count={(df_sim['idpartner'] > 0).sum()}"
        )

        # Method 1: A person is a partner if they have a valid idpartner (mutual partner relationship)
        # In EUROMOD data, if person A has idpartner = B, then B should have idpartner = A
        # The partner (non-head) is the one whose idpartner points to the head

        if head_id_col and head_id_col in df_sim.columns:
            # Get head info per household
            head_info = df_sim[df_sim["hh_IsHead"] == 1][["idhh", "idperson", "idpartner"]].copy()
            # Ensure one head row per household (avoid duplicating the entire file if hh_IsHead has errors)
            head_info = (
                head_info.sort_values(["idhh", "idperson"]).groupby("idhh", as_index=False).first()
            )
            head_info.rename(
                columns={"idperson": "head_id", "idpartner": "head_partner_id"}, inplace=True
            )

            # Merge back to identify partners
            df_sim = df_sim.merge(
                head_info[["idhh", "head_id", "head_partner_id"]], on="idhh", how="left"
            )

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
                (df_sim["idpartner"] > 0) & (df_sim["hh_IsHead"] != 1)
            ).astype(int)

        logging.info(
            f"Partner flag derived from idpartner: {df_sim['hh_IsPartner'].sum()} partners identified"
        )

        # If still no partners found, try alternative: use household composition
        if df_sim["hh_IsPartner"].sum() == 0:
            logging.warning(
                "No partners found via idpartner. Trying household composition fallback."
            )
            # Identify potential partners: adults (age >= 18) who are not head, in same household
            # This is a heuristic: in 2-adult households, the non-head adult is likely the partner
            adults_mask = (
                df_sim["dag"] >= 18
                if "dag" in df_sim.columns
                else pd.Series(True, index=df_sim.index)
            )
            hh_adult_count = df_sim[adults_mask].groupby("idhh").size()

            # Households with exactly 2 adults might be couples
            two_adult_hh = hh_adult_count[hh_adult_count == 2].index

            # In these households, mark the non-head adult as partner
            df_sim["hh_IsPartner"] = (
                df_sim["idhh"].isin(two_adult_hh) & adults_mask & (df_sim["hh_IsHead"] != 1)
            ).astype(int)

            logging.info(
                f"Partner flag via household composition fallback: {df_sim['hh_IsPartner'].sum()} partners identified"
            )
    else:
        logging.warning(
            "No partner identification column found. All households will be classified as singles."
        )
        df_sim["hh_IsPartner"] = 0

    # =========================================================================
    # RURO DECIDER FLAG: head + partner are "deciders" for RURO estimation
    # =========================================================================
    # All other household members (children, other adults) are kept in the data
    # for EUROMOD tax-benefit calculations, but will NOT enter RURO estimation.
    df_sim["ruro_decider"] = ((df_sim["hh_IsHead"] == 1) | (df_sim["hh_IsPartner"] == 1)).astype(
        int
    )

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
        # Use a composite key (idhh, idperson) for a safe merge. If those keys are not
        # present or are non-unique, raise an error rather than silently producing
        # many-to-many merges that duplicate rows.
        key = ["idhh", "idperson"]
        if not set(key).issubset(df.columns) or not set(key).issubset(df_sim.columns):
            raise KeyError(
                "Expected 'idhh' and 'idperson' in both input and EUROMOD output for safe merge."
            )
        if df.duplicated(subset=key).any():
            raise ValueError("Input has duplicate (idhh,idperson) pairs; merge would be unsafe.")
        if df_sim.duplicated(subset=key).any():
            raise ValueError("EUROMOD output has duplicate (idhh,idperson) pairs; merge would be unsafe.")

        # Ensure composite key is explicit
        key = ["idhh", "idperson"]

        # Keep columns unique to original df (not in simulation) and not part of the key
        df_only_cols = [c for c in df.columns if c not in df_sim.columns and c not in key]

        # Also preserve overlapping raw columns by importing them with a suffix
        df_overlap_cols = [c for c in df.columns if c in df_sim.columns and c not in key]

        # Merge simulation output with original data's unique and overlapping columns on composite key.
        # Use suffixes so EUROMOD outputs keep canonical names and raw inputs are preserved as *_input.
        final_df = df_sim.merge(
            df[key + df_only_cols + df_overlap_cols],
            on=key,
            how="left",
            suffixes=("", "_input"),
        )

        # Sanity check: merge should be 1:1 on df_sim rows. If not, raise to avoid silent duplication.
        if len(final_df) != len(df_sim):
            raise RuntimeError(
                "Post-merge row count mismatch: merge did not preserve EUROMOD output row count. "
                "This likely indicates non-unique keys or unexpected duplicate matches."
            )
    else:
        final_df = df_sim

    # --- Normalise columns to safe defaults (avoid KeyError / boolean-scalar pitfalls) ----
    required = {"idperson", "idhh"}
    missing_req = required - set(final_df.columns)
    if missing_req:
        raise KeyError(f"Missing required identifiers in EUROMOD output: {missing_req}")

    final_df = ensure_columns(
        final_df,
        {
            # structural flags (series aligned to index)
            "hh_IsHead": 0,
            "hh_IsPartner": 0,
            # demographics
            "dag": lambda d: pd.Series(np.nan, index=d.index),
            "dgn": lambda d: pd.Series(np.nan, index=d.index),
            # labour market basic primitives
            "les": 7,
            "lhw": 0.0,
            "yem": 0.0,
            "yse": 0.0,
            "yivwg": lambda d: pd.Series(np.nan, index=d.index),
            "liwmy": lambda d: pd.Series(12.0, index=d.index),
            # benefits / aggregates used downstream
            "benefit_retire_disab": 0.0,
            # optional screening flag
            "flag_periodicity": lambda d: pd.Series(False, index=d.index),
        },
    )

    # Validate
    required_columns = ["idperson", "idhh", "dag", "dgn", "les"]
    available_required = [c for c in required_columns if c in final_df.columns]
    if len(available_required) < len(required_columns):
        missing = set(required_columns) - set(available_required)
        logging.warning(f"Missing some required columns: {missing}")
        if logging.getLogger().isEnabledFor(logging.DEBUG):
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
    # Wage + earnings objects for RURO (uses yem00+yemxp if present; prefers yivwg when plausible)
    final_df = compute_wage_for_ruro(final_df, config=config)
    # -------------------------------------------------------------------------
    # Wage cleaning for RURO draws (robust):
    #  - Keep yivwg as "wage offer" (predicted wage) for ALL individuals.
    #  - Build wage_draw used by RURO_draws: always finite & within bounds if possible.
    # -------------------------------------------------------------------------
    lb, ub = config.get("wage_bounds", (2, 170))

    # Preserve original (do not destroy it later)
    final_df["yivwg_raw"] = final_df["yivwg"] if "yivwg" in final_df.columns else np.nan

    # Numeric coercion (critical: prevents object dtype surprises)
    yivwg_num = pd.to_numeric(final_df.get("yivwg", np.nan), errors="coerce")
    wf_num = pd.to_numeric(final_df.get("wage_final", np.nan), errors="coerce")

    # Candidate wage offer:
    #  - prefer yivwg if finite
    #  - else fallback to wage_final
    wage_draw_raw = np.where(np.isfinite(yivwg_num), yivwg_num, wf_num)
    wage_draw_raw = pd.Series(wage_draw_raw, index=final_df.index, dtype="float64")

    final_df["wage_draw_raw"] = wage_draw_raw

    # Build a RURO-safe draw wage:
    #  - if raw wage exists, clip to [lb, ub]
    #  - else remain NaN (we will exclude those cases for estimation)
    final_df["wage_draw"] = wage_draw_raw.where(np.isfinite(wage_draw_raw)).clip(lower=lb, upper=ub)

    # Diagnostics: who got clipped?
    final_df["wage_draw_clipped_flag"] = (
        wage_draw_raw.notna() & np.isfinite(wage_draw_raw) & ((wage_draw_raw < lb) | (wage_draw_raw > ub))
    )

    # Defensive: ensure lhw exists
    final_df["lhw"] = pd.to_numeric(final_df.get("lhw", 0.0), errors="coerce").fillna(0.0)

    les_col = "les_enforced" if "les_enforced" in final_df.columns else "les"
    is_emp = final_df[les_col].eq(3)

    # Employees with positive hours MUST have a wage_draw for RURO estimation stability
    emp_needs_wage = is_emp & final_df["lhw"].gt(0) & final_df["ruro_decider"].eq(1)
    bad_emp_wage = emp_needs_wage & (final_df["wage_draw"].isna() | ~np.isfinite(final_df["wage_draw"]))

    bad_hh = final_df.loc[bad_emp_wage, "idhh"].unique()
    if len(bad_hh) > 0:
        logging.warning(
            f"{len(bad_hh)} households have employed deciders with hours>0 but missing/invalid wage_draw. "
            "They will be excluded from keep_for_analysis."
        )

    # Keep existing labels for downstream
    final_df["yem2_final"] = final_df.get("yem_recon_monthly", np.nan)
    final_df["diff_yem_final"] = final_df.get("diff_yem_monthly", np.nan)
    # Do NOT rely on config for which diff column to use; pass explicitly below.
    diff_column = "diff_yem_final"
    threshold = config.get("extreme_wage_diff", DEFAULT_CONFIG["extreme_wage_diff"])

    # =========================================================================
    # EXTREME HOUSEHOLD IDENTIFICATION (matching data_prep2.py)
    # =========================================================================
    # Adult-only screening (exclude minors from outlier test)
    adults = final_df["dag"].fillna(0).ge(18)
    # Recompute employee flag explicitly here (safer and clearer)
    is_emp = final_df[les_col].eq(3)
    # Ensure flag_periodicity is always an index-aligned boolean Series to avoid scalar bitwise issues
    if "flag_periodicity" in final_df.columns:
        flag_periodicity = final_df["flag_periodicity"].fillna(False).astype(bool)
    else:
        flag_periodicity = pd.Series(False, index=final_df.index)
    screen_idx = adults & is_emp & (~flag_periodicity)
    # Only screen extremes if we have a meaningful diff measure (typically when wage_source='yivwg')
    has_diff = diff_column in final_df.columns and final_df[diff_column].notna().any()

    if has_diff:
        households_to_remove = identify_extreme_households(
            final_df.loc[screen_idx], diff_column, threshold
        )
    else:
        households_to_remove = np.array([])
        logging.info("Extreme-screened population: no non-missing diff measure available.")

    logging.info(f"Extreme-screened population: {int(screen_idx.sum())} records")
    logging.info(f"Households to remove due to extreme wages: {len(households_to_remove)}")
    # =========================================================================
    # ELIGIBILITY FLAGS (matching data_prep2.py)
    # =========================================================================
    is_emp = final_df[les_col].eq(3)

    ready_allowed_les = final_df[les_col].isin(config["allowed_les"])
    ready_age = final_df["dag"].between(*config["age_range"])

    # Hours bounds apply only to employees; use new config keys for floor/cap
    hours_floor = config.get("hours_floor_low", 10)
    hours_cap = config.get("hours_cap_high", 70)

    # Employees pass if their weekly hours are within [hours_floor, hours_cap].
    # Non-employees automatically pass.
    ready_hours = (~is_emp) | final_df["lhw"].between(hours_floor, hours_cap)

    # Wage bounds apply only to employees; require finite wage_draw within bounds for employees
    ready_wage = (~is_emp) | (final_df["wage_draw"].between(lb, ub))
    
    #
    # bad_hh was computed earlier as households with employed deciders missing/invalid wage_draw
    if "bad_hh" in locals() and (isinstance(bad_hh, (list, np.ndarray)) and len(bad_hh) > 0):
        ready_no_missing_emp_wage = ~final_df["idhh"].isin(bad_hh)
    else:
        # If no bad_hh recorded, allow all households (Series of True)
        ready_no_missing_emp_wage = pd.Series(True, index=final_df.index)

    ready_no_unresolved_extreme = ~final_df["idhh"].isin(households_to_remove)

    final_df["keep_for_analysis"] = (
        ready_allowed_les
        & ready_age
        & ready_hours
        & ready_wage
        & ready_no_unresolved_extreme
        & ready_no_missing_emp_wage
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
        # Efficient approach: subset to children and aggregate father/mother separately.
        bands = {
            "num_children_0_3": (final_df["dag"].between(0, 3)),
            "num_children_3_6": (final_df["dag"].between(4, 6)),
            "num_children_6_11": (final_df["dag"].between(7, 11)),
            "num_children_11_17": (final_df["dag"].between(12, 17)),
        }

        # Subset to potential children (saves memory)
        children_mask = final_df["dag"].between(0, 17)
        children = final_df.loc[children_mask, ["idfather", "idmother", "dag"]].copy()

        # If no children, create zero columns and skip heavy work
        if children.empty:
            for col in [
                "num_children_total",
                "num_children_0_3",
                "num_children_3_6",
                "num_children_6_11",
                "num_children_11_17",
            ]:
                final_df[col] = 0
            logging.info("No children (0-17) found; child count placeholders created.")
        else:
            # Build band indicators (int8 to save memory)
            for name, cond in bands.items():
                children[name] = cond.loc[children.index].astype(np.int8)

            # Father links
            father = children.loc[
                children["idfather"].notna() & (children["idfather"] != 0),
                ["idfather"] + list(bands.keys()),
            ].copy()
            father = father.rename(columns={"idfather": "parent_id"})

            # Mother links
            mother = children.loc[
                children["idmother"].notna() & (children["idmother"] != 0),
                ["idmother"] + list(bands.keys()),
            ].copy()
            mother = mother.rename(columns={"idmother": "parent_id"})

            # Concatenate and aggregate by parent_id
            parent_counts = (
                pd.concat([father, mother], ignore_index=True)
                .groupby("parent_id")[list(bands.keys())]
                .sum()
            )
            parent_counts["num_children_total"] = parent_counts.sum(axis=1)

            # Reorder columns to match previous output
            parent_counts = parent_counts[
                [
                    "num_children_total",
                    "num_children_0_3",
                    "num_children_3_6",
                    "num_children_6_11",
                    "num_children_11_17",
                ]
            ]

            # Ensure parent index dtype matches idperson where possible
            try:
                parent_counts.index = parent_counts.index.astype(final_df["idperson"].dtype)
            except Exception:
                pass

            # Merge back to persons and fill missing with zeros
            final_df = final_df.merge(
                parent_counts,
                how="left",
                left_on="idperson",
                right_index=True,
            )

            child_cols = parent_counts.columns.tolist()
            final_df[child_cols] = final_df[child_cols].fillna(0).astype(int)

            logging.info(f"Child counts created: {child_cols}")
    else:
        logging.warning(
            "Parent ID columns (idfather, idmother) not found. Child counts not created."
        )
        # Create placeholder columns
        for col in [
            "num_children_total",
            "num_children_0_3",
            "num_children_3_6",
            "num_children_6_11",
            "num_children_11_17",
        ]:
            final_df[col] = 0

    # From this point on, use the enforced labour status as canonical
    final_df["les"] = final_df[les_col]
    # -------------------------------------------------------------------------
    # Enforce internal consistency: only employees carry positive hours/wage
    # -------------------------------------------------------------------------
    is_emp = final_df["les"].eq(3)

    # Non-employees carry zero working hours; preserve yivwg (wage offer) for all.
    final_df.loc[~is_emp, "lhw"] = 0.0
    # Only blank the observed/constructed employee wage; keep yivwg for draws/offer information.
    final_df.loc[~is_emp, "wage_final"] = np.nan
    final_df["wage_emp_obs"] = final_df["wage_draw"].where(is_emp & final_df["lhw"].gt(0))

    # Prepare column groups metadata to return
    colgroups = {
        "A_cols": A_cols,
        "B_cols": B_cols,
        "C_cols": C_cols,
        "euromod_system": system_name,
        "euromod_dataset": dataset_name,
        "euromod_input_cols": euromod_input_cols,
        "euromod_output_cols": euromod_output_cols,
    }

    return final_df, colgroups


# =============================================================================
# HOUSEHOLD TYPE SEPARATION
# =============================================================================

def separate_household_types(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Separate households into couples and singles using head/partner structure.

    Couples: exactly 1 head AND at least 1 partner (typically exactly 1).
    Singles: exactly 1 head AND 0 partners.

    Any household not matching these patterns is flagged (logged) and treated as single by default
    (conservative), but you can change that policy easily.
    """
    if "idhh" not in df.columns:
        raise KeyError("Expected 'idhh' in df.")
    if "hh_IsHead" not in df.columns:
        raise KeyError("Expected 'hh_IsHead' in df.")
    if "hh_IsPartner" not in df.columns:
        # In your pipeline, you usually ensure this exists. Create a safe default anyway.
        df = df.copy()
        df["hh_IsPartner"] = 0

    # Force clean numeric 0/1
    hh_head = pd.to_numeric(df["hh_IsHead"], errors="coerce").fillna(0).astype(int)
    hh_part = pd.to_numeric(df["hh_IsPartner"], errors="coerce").fillna(0).astype(int)

    hh_struct = (
        pd.DataFrame({"idhh": df["idhh"], "hh_IsHead": hh_head, "hh_IsPartner": hh_part})
        .groupby("idhh", as_index=True)
        .agg(n_head=("hh_IsHead", "sum"), n_partner=("hh_IsPartner", "sum"))
    )

    # Define household type
    is_single = (hh_struct["n_head"] == 1) & (hh_struct["n_partner"] == 0)
    is_couple = (hh_struct["n_head"] == 1) & (hh_struct["n_partner"] >= 1)

    # Diagnostics: households that violate structure assumptions
    weird = hh_struct.index[~(is_single | is_couple)]
    if len(weird) > 0:
        logging.warning(
            f"separate_household_types: {len(weird)} households have inconsistent structure "
            f"(not exactly 1 head and partner in {{0,>=1}}). Example idhh: {list(weird[:10])}"
        )
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug(hh_struct.loc[weird].value_counts().to_string())

    # Conservative: treat weird as singles to avoid sample loss
    single_idhh = hh_struct.index[is_single | hh_struct.index.isin(weird)]
    couple_idhh = hh_struct.index[is_couple]

    # Diagnostic: ensure no households lost
    n_all = df["idhh"].nunique()
    n_sum = len(couple_idhh) + len(single_idhh)
    if n_sum != n_all:
        raise RuntimeError(f"Household split mismatch: all={n_all}, couples+singles={n_sum}")

    couples_df = df[df["idhh"].isin(couple_idhh)].copy()
    singles_df = df[df["idhh"].isin(single_idhh)].copy()

    return couples_df, singles_df

def filter_singles_by_gender(df: pd.DataFrame, gender: int) -> pd.DataFrame:
    """
    Filter singles dataframe to include only households where the head has the specified gender.

    Parameters
    ----------
    df : pd.DataFrame
        Singles dataframe (all persons in those households).
    gender : int
        Gender code to keep (must match df['dgn'] coding).

    Returns
    -------
    pd.DataFrame
        Filtered dataframe containing all persons in households whose head matches `gender`.
    """
    if "hh_IsHead" not in df.columns:
        raise KeyError("Expected 'hh_IsHead' in df.")
    if "dgn" not in df.columns:
        raise KeyError("Expected 'dgn' in df.")
    if "idhh" not in df.columns:
        raise KeyError("Expected 'idhh' in df.")

    heads = df.loc[df["hh_IsHead"] == 1, ["idhh", "dgn"]].copy()
    heads["dgn"] = pd.to_numeric(heads["dgn"], errors="coerce")

    # Optional diagnostic: ensure exactly one head per household in the singles sample
    dup_heads = heads.groupby("idhh").size()
    bad = dup_heads[dup_heads != 1]
    if len(bad) > 0:
        logging.warning(
            f"{len(bad)} households do not have exactly 1 head in filter_singles_by_gender. "
            f"Example idhh (up to 10): {list(bad.index[:10])}"
        )

    # Keep only households with exactly one head to be strict
    valid_idhh = dup_heads[dup_heads == 1].index
    heads = heads[heads["idhh"].isin(valid_idhh)]

    matching_idhh = heads.loc[heads["dgn"] == float(gender), "idhh"].unique()
    return df[df["idhh"].isin(matching_idhh)].copy()

# =============================================================================
# FINALIZE POST-FILTER RURO CONSISTENCY
# =============================================================================

def finalize_post_filter_ruro_consistency(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Enforce internal consistency after filtering that may have changed lhw/les.

    Policy (RURO-consistent):
      - 'wage_draw' is a WAGE OFFER (opportunity object): keep it for everyone (clip to bounds if finite).
      - 'wage_final'/'wage_unbounded'/'wage_ruro' are REALIZED/EMPLOYEE wage objects: keep only for employees with lhw>0.
      - Non-employees must have lhw == 0.
    """
    df = df.copy()

    lb, ub = config.get("wage_bounds", (2, 170))
    WPM_local = float(config.get("weeks_per_month", WPM))

    # Canonicalize les
    les_col = "les_enforced" if "les_enforced" in df.columns else "les"
    if les_col != "les":
        df["les"] = pd.to_numeric(df[les_col], errors="coerce").fillna(7).astype(int)
    else:
        df["les"] = pd.to_numeric(df["les"], errors="coerce").fillna(7).astype(int)

    is_emp = df["les"].eq(3)

    # Hours: non-employees must have zero hours
    df["lhw"] = pd.to_numeric(df.get("lhw", 0.0), errors="coerce").fillna(0.0)
    df.loc[~is_emp, "lhw"] = 0.0

    # Blank REALIZED wage objects for non-employees (keep wage offers)
    for wcol in ("wage_final", "wage_unbounded", "wage_ruro", "wage_emp_obs",
                 "wage_implied", "wage_implied_regular", "wage_implied_overtime"):
        if wcol in df.columns:
            df.loc[~is_emp, wcol] = np.nan

    # Offer wage: keep for everyone, just coerce + bound it for numerical stability
    if "wage_draw" in df.columns:
        wd = pd.to_numeric(df["wage_draw"], errors="coerce")
        df["wage_draw"] = wd.where(np.isfinite(wd)).clip(lower=lb, upper=ub)

    # Realized employee wage: keep only if employee AND positive hours AND within bounds
    if "wage_final" in df.columns:
        wf = pd.to_numeric(df["wage_final"], errors="coerce")
        df["wage_final"] = wf.where(is_emp & df["lhw"].gt(0) & wf.between(lb, ub), np.nan)

    # Optional: define observed employee wage as the bounded offer wage on the employed-with-hours support
    if "wage_draw" in df.columns:
        df["wage_emp_obs"] = df["wage_draw"].where(is_emp & df["lhw"].gt(0))

    # Recompute reconstructed earnings diagnostics if possible
    if ("wage_final" in df.columns) and ("yem_emp_monthly" in df.columns):
        monthly_hours = df["lhw"] * WPM_local
        yem_emp_monthly = pd.to_numeric(df["yem_emp_monthly"], errors="coerce")

        yem_recon = (pd.to_numeric(df["wage_final"], errors="coerce") * monthly_hours).where(is_emp & df["lhw"].gt(0))
        df["yem_recon_monthly"] = yem_recon
        df["diff_yem_monthly"] = (yem_recon - yem_emp_monthly).where(is_emp & df["lhw"].gt(0))

        # Maintain aliases if downstream expects them
        df["yem2_final"] = df.get("yem_recon_monthly", np.nan)
        df["diff_yem_final"] = df.get("diff_yem_monthly", np.nan)

    return df

# =============================================================================
# PLOT GENERATION FUNCTION
# =============================================================================

def generate_plots(df: pd.DataFrame, title: str, prefix: str, out_dir: str) -> None:
    """Generate diagnostic plots for the processed data."""
    import logging
    logger = logging.getLogger(__name__)
    
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    
    plots_dir = out_dir
    os.makedirs(plots_dir, exist_ok=True)
    
    logger.info(f"Generating plots for {title} ({len(df)} rows) -> {plots_dir}")
    
    # Define columns to plot (adjust based on what's available)
    plot_cols = [
        ("lhw", "Weekly Hours"),
        ("lhw_base", "Baseline Weekly Hours"),
        ("yem", "Employment Income"),
        ("yem_base", "Baseline Employment Income"),
        ("age", "Age"),
        ("ils_dispy", "Disposable Income"),
        ("hourly_wage", "Hourly Wage"),
    ]
    
    for col, label in plot_cols:
        if col not in df.columns:
            continue
        try:
            fig, ax = plt.subplots(figsize=(8, 5))
            data = df[col].dropna()
            if len(data) == 0:
                plt.close(fig)
                continue
            
            ax.hist(data, bins=50, edgecolor="black", alpha=0.7)
            ax.set_xlabel(label)
            ax.set_ylabel("Count")
            ax.set_title(f"{title} — {label} Distribution")
            
            # Add summary stats
            stats_text = f"N={len(data):,}\nMean={data.mean():.2f}\nMedian={data.median():.2f}"
            ax.text(0.95, 0.95, stats_text, transform=ax.transAxes, 
                    verticalalignment='top', horizontalalignment='right',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            plt.tight_layout()
            out_path = os.path.join(plots_dir, f"{prefix}_{col}.png")
            plt.savefig(out_path, dpi=150)
            plt.close(fig)
            logger.debug(f"Saved plot: {out_path}")
        except Exception as e:
            logger.warning(f"Could not plot {col}: {e}")
            plt.close("all")
    
    # Hours distribution by gender (if dgn column exists)
    if "dgn" in df.columns and "lhw" in df.columns:
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            for gender, label in [(0, "Male"), (1, "Female")]:
                subset = df[df["dgn"] == gender]["lhw"].dropna()
                if len(subset) > 0:
                    ax.hist(subset, bins=30, alpha=0.5, label=label, edgecolor="black")
            ax.set_xlabel("Weekly Hours")
            ax.set_ylabel("Count")
            ax.set_title(f"{title} — Hours by Gender")
            ax.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(plots_dir, f"{prefix}_hours_by_gender.png"), dpi=150)
            plt.close(fig)
        except Exception as e:
            logger.warning(f"Could not plot hours by gender: {e}")
            plt.close("all")
    
    logger.info(f"Plots saved to {plots_dir}")

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
    model_dir: Optional[Path] = None,
    config: Optional[Dict] = None,
    data_year: Optional[int] = None,
    stamp_system_year: Optional[int] = None,
    no_plots: bool = False,
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
        model_dir: EUROMOD model directory (optional, can be detected automatically)
        config: Configuration dictionary
        data_year: Explicit data year to stamp (defaults to year)
        stamp_system_year: Explicit system year to stamp (defaults to system_year)
        no_plots: Skip plot generation to speed up processing

    Returns:
        Tuple of (output_directory, metadata_dict)

    Raises:
        FileNotFoundError: If the raw data file is not found.
        NotImplementedError: If the specified country is not implemented.
        ImportError: If required packages are missing.
        KeyError: If required columns are missing in the data.
        ValueError: If there are duplicate keys or invalid year stamps.
        RuntimeError: If merging data results in row count mismatch.
    """
    if config is None:
        config = copy.deepcopy(DEFAULT_CONFIG)
    else:
        # Work on local copy to avoid mutating caller-provided dict
        config = copy.deepcopy(config)

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

    # Capture A_cols: columns from raw EUROMOD template at load time
    A_cols = list(df_raw.columns)

    # Clean and harmonize
    # allow overriding detected model path from CLI
    model_dir = Path(model_dir) if model_dir else euromod_root()

    if country == "FR":
        df_clean, colgroups = clean_harmonize_fr(
            df_raw,
            country=country,
            year=year,
            system_year=system_year,
            model_dir=model_dir,
            config=config,
            A_cols=A_cols,
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
    # Ensure post-filter canonicalization so les/lhw/wages are internally consistent
    df_filtered_couples = finalize_post_filter_ruro_consistency(df_filtered_couples, config)
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
    df_filtered_singles = finalize_post_filter_ruro_consistency(df_filtered_singles, config)
    logging.info(
        f"Filtered singles data: {len(df_filtered_singles)} records, "
        f"{df_filtered_singles['idhh'].nunique()} households"
    )

    # =========================================================================
    # COMBINE FILTERED COUPLES AND SINGLES INTO FULL FILTERED DATASET
    # =========================================================================
    # Stamp year columns into outputs BEFORE exporting
    resolved_data_year = int(data_year if data_year is not None else year)
    resolved_system_year = int(stamp_system_year if stamp_system_year is not None else system_year)

    # Stamp filtered couples/singles (these are used below to export by household type)
    if len(df_filtered_couples) > 0:
        df_filtered_couples = _stamp_years(df_filtered_couples, data_year=resolved_data_year, system_year=resolved_system_year)
        if df_filtered_couples["data_year"].nunique() != 1 or not (1900 <= int(df_filtered_couples["data_year"].iat[0]) <= 2100):
            raise ValueError("Invalid data_year stamped on couples output; expected single plausible year between 1900 and 2100.")
        if df_filtered_couples["system_year"].nunique() != 1 or not (1900 <= int(df_filtered_couples["system_year"].iat[0]) <= 2100):
            raise ValueError("Invalid system_year stamped on couples output; expected single plausible year between 1900 and 2100.")

    if len(df_filtered_singles) > 0:
        df_filtered_singles = _stamp_years(df_filtered_singles, data_year=resolved_data_year, system_year=resolved_system_year)
        if df_filtered_singles["data_year"].nunique() != 1 or not (1900 <= int(df_filtered_singles["data_year"].iat[0]) <= 2100):
            raise ValueError("Invalid data_year stamped on singles output; expected single plausible year between 1900 and 2100.")
        if df_filtered_singles["system_year"].nunique() != 1 or not (1900 <= int(df_filtered_singles["system_year"].iat[0]) <= 2100):
            raise ValueError("Invalid system_year stamped on singles output; expected single plausible year between 1900 and 2100.")
    # Recreate combined filtered dataset (preserve earlier behavior)
    df_filtered = pd.concat([df_filtered_couples, df_filtered_singles], ignore_index=True)
    df_filtered = _stamp_years(df_filtered, data_year=resolved_data_year, system_year=resolved_system_year)

    logging.info(
        f"Combined filtered data: {len(df_filtered)} records, "
        f"{df_filtered['idhh'].nunique()} households"
    )

    # Export results - full dataset
    output_prefix = f"{country.lower()}_{year}"

    # Main export should not silently report couples-only stats.
    stats_all = pd.concat(
        [
            stats_df_couples.assign(Sample="couples"),
            stats_df_singles.assign(Sample="singles"),
        ],
        ignore_index=True,
    )

    # IMPORTANT (user choice): do not drop any columns at export.
    # Keep df_filtered as-is, including all EUROMOD outputs and *_input raw overlaps.

    export_result = export_household_data(
        df_filtered,
        stats_all,
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
                    "path": None,
                    "households": 0,
                    "records": 0,
                }
    else:
        logging.warning("No single households found to export")
        household_type_results["singles"] = {"path": None, "households": 0, "records": 0}
        household_type_results["singles_female"] = {"path": None, "households": 0, "records": 0}
        household_type_results["singles_male"] = {"path": None, "households": 0, "records": 0}

    # =========================================================================
    # EXPORT FILTERING STATISTICS FOR SINGLES (CSV + LaTeX)
    # =========================================================================
    # Reuse helper to export singles stats (CSV + LaTeX)
    export_stats(stats_df_singles, outputs_dir, f"{output_prefix}_singles_stats")

    # Build metadata dict BEFORE persisting (was below — caused NameError)
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

    # Persist metadata JSON for reproducibility
    try:
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        git_hash = None

    meta["run_utc"] = datetime.datetime.utcnow().isoformat() + "Z"
    if git_hash:
        meta["git_commit"] = git_hash
    
    meta_path = outputs_dir / f"{output_prefix}_meta.json"
    # JSON-safe serializer: convert Path and numpy scalar types to native Python
    def _json_safe(x):
        from pathlib import Path
        import numpy as _np
        if isinstance(x, Path):
            return str(x)
        if isinstance(x, (_np.integer, _np.floating)):
            return x.item()
        return x
    try:
        meta_path.write_text(json.dumps(meta, indent=2, default=_json_safe), encoding="utf-8")
        logging.info(f"Saved metadata to {meta_path}")
    except Exception as e:
        logging.warning(f"Failed to write metadata JSON: {e}")

    # =========================================================================
    # SAVE COLUMN GROUPS JSON SIDECAR
    # =========================================================================
    colgroups_json = {
        "A_cols": colgroups["A_cols"],
        "B_cols": colgroups["B_cols"],
        "C_cols": colgroups["C_cols"],
        "metadata": {
            "country": country,
            "year": year,
            "euromod_system": colgroups["euromod_system"],
            "euromod_dataset": colgroups["euromod_dataset"],
            "euromod_input_cols": colgroups["euromod_input_cols"],
            "euromod_output_cols": colgroups["euromod_output_cols"],
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        },
    }
    colgroups_path = out_dir / f"{output_prefix}__colgroups.json"
    try:
        colgroups_path.write_text(json.dumps(colgroups_json, indent=2), encoding="utf-8")
        logging.info(f"Saved column groups to {colgroups_path}")
    except Exception as e:
        logging.warning(f"Failed to write column groups JSON: {e}")

    # =========================================================================
    # EXPORT A+B ONLY (optional, if --export-ab-only flag is set)
    # =========================================================================
    # This supports the user's "drop C before 2nd EUROMOD run" workflow
    export_ab_only = config.get("export_ab_only")
    if export_ab_only:
        AB_cols = set(colgroups["A_cols"]) | set(colgroups["B_cols"])
        # Keep only columns that exist in df_filtered
        AB_cols_available = sorted([c for c in AB_cols if c in df_filtered.columns])
        df_ab_only = df_filtered[AB_cols_available].copy()

        # Determine output path
        if export_ab_only in ("true", "True", "1"):
            ab_output_path = out_dir / f"{output_prefix}_AB_only"
        else:
            ab_output_path = Path(export_ab_only)

        ab_file_path = _write_dataframe(
            df_ab_only,
            ab_output_path,
            config.get("export_format", "parquet"),
        )
        logging.info(
            f"Exported A+B columns only: {len(AB_cols_available)} columns, "
            f"{len(df_ab_only)} rows to {ab_file_path}"
        )

    # =========================================================================
    # GENERATE PLOTS FOR EACH GROUP
    # =========================================================================
    if not no_plots:
        plot_bins = config.get("plot_bins", 40)

        # Overall combined plots
        generate_plots(
            df_filtered,
            title=f"{country} {year} (All)",
            prefix=f"{output_prefix}_all",
            out_dir=plots_dir,
        )

        # Couples plots
        if len(df_filtered_couples) > 0:
            generate_plots(
                df_filtered_couples,
                title=f"{country} {year} Couples",
                prefix=f"{output_prefix}_couples",
                out_dir=plots_dir,
            )

        # Singles plots
        if len(df_filtered_singles) > 0:
            generate_plots(
                df_filtered_singles,
                title=f"{country} {year} Singles",
                prefix=f"{output_prefix}_singles",
                out_dir=plots_dir,
            )

            # Singles female plots
            singles_female_df = filter_singles_by_gender(df_filtered_singles, 0)
            if len(singles_female_df) > 0:
                generate_plots(
                    singles_female_df,
                    title=f"{country} {year} Singles (Female)",
                    prefix=f"{output_prefix}_singles_female",
                    out_dir=plots_dir,
                )

            # Singles male plots
            singles_male_df = filter_singles_by_gender(df_filtered_singles, 1)
            if len(singles_male_df) > 0:
                generate_plots(
                    singles_male_df,
                    title=f"{country} {year} Singles (Male)",
                    prefix=f"{output_prefix}_singles_male",
                    out_dir=plots_dir,
                )
    else:
        logging.info("Skipping plot generation (--no-plots flag set)")



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
  python france_data_prep.py --year 2015 --raw-dir /path/to/data
  python france_data_prep.py --year 2021 --out-dir ./output
        """,
    )

    parser.add_argument(
        "--year",
        "-y",
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
        help="Optional explicit EUROMOD system year to stamp into outputs (defaults to data_year or year-1)",
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

    parser.add_argument(
        "--model-dir",
        type=str,
        default=None,
        help="Path to EUROMOD model directory (overrides auto-detect)",
    )

    parser.add_argument(
        "--data-year",
        type=int,
        default=None,
        help="Optional explicit data year to stamp into outputs (defaults to --year)",
    )

    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Skip plot generation to speed up processing",
    )

    parser.add_argument(
        "--export-ab-only",
        type=str,
        default=None,
        help="Export additional parquet with only A_cols + B_cols (drops C_cols). "
             "Provide output path or 'true' to use default naming.",
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
    if hasattr(args, "export_ab_only") and args.export_ab_only:
        config["export_ab_only"] = args.export_ab_only

    logging.info(f"Processing {country} {year}")
    logging.info(f"EUROMOD system year: {system_year}")
    logging.info(f"Raw filename: {raw_filename}")
    if config.get("export_ab_only"):
        logging.info(f"Export A+B only enabled: {config['export_ab_only']}")

    try:
        out_dir, meta = prepare_one_year(
            country=country,
            year=year,
            raw_filename=raw_filename,
            system_year=system_year,
            raw_dir=raw_dir,
            out_dir=out_dir,
            model_dir=Path(args.model_dir) if args.model_dir else None,
            config=config,
            data_year=args.data_year if getattr(args, "data_year", None) is not None else None,
            stamp_system_year=args.system_year if getattr(args, "system_year", None) is not None else None,
            no_plots=getattr(args, "no_plots", False),
        )

        logging.info("Processing complete!")
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
