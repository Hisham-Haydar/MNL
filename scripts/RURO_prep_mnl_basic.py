#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-12-01 16:17:45
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)

TOTAL_LEISURE_HOURS = 80.0
WEEKS_PER_MONTH = 52.0 / 12.0
DCM_MIN_POSITIVE = 1e-6

# ---- Prior parameters (aligned with RURO_draws.py defaults) ----------------
DEFAULT_PI0_M = 0.10
DEFAULT_PI0_F = 0.10
DEFAULT_H_MIN = 1.0
DEFAULT_H_MAX = 70.0
DEFAULT_W_MIN = 1.0
DEFAULT_W_MAX = 120.0
DEFAULT_WAGE_SPEC = "vw"

# ---- GSUR (Group-Specific Unemployment Rate) --------------------------------
# Default path to GSUR lookup table (France)
DEFAULT_GSUR_PATH = Path(__file__).resolve().parent.parent / "Data" / "external" / "FR_gsur_ruro.parquet"


def _read_df(path: Path) -> pd.DataFrame:
    suf = path.suffix.lower()
    if suf == ".parquet":
        return pd.read_parquet(path)  # type: ignore[arg-type]
    if suf == ".csv":
        return pd.read_csv(path)
    if suf in {".pkl", ".pickle"}:
        return pd.read_pickle(path)
    raise ValueError(f"Unsupported format for {path}")


def _write_df(df: pd.DataFrame, base: Path) -> Dict[str, Path]:
    out_parquet = base.with_suffix(".parquet")
    out_csv = base.with_suffix(".csv")
    df.to_parquet(out_parquet, index=False)  # type: ignore[arg-type]
    df.to_csv(out_csv, index=False)
    return {"parquet": out_parquet, "csv": out_csv}


def _merge_euromod_outputs(long_df: pd.DataFrame, em_df: pd.DataFrame) -> pd.DataFrame:
    if "idperson" not in long_df.columns or "draw" not in long_df.columns:
        raise KeyError("long_df must contain 'idperson' and 'draw'.")
    if "idperson_true" not in em_df.columns or "draw" not in em_df.columns:
        raise KeyError("EUROMOD combined df must contain 'idperson_true' and 'draw'.")

    merged = long_df.merge(
        em_df,
        left_on=["idperson", "draw"],
        right_on=["idperson_true", "draw"],
        how="left",
        suffixes=("", "_em"),
    )

    if merged["ils_dispy"].isna().any():
        missing = merged[merged["ils_dispy"].isna()][["idperson", "draw"]].head()
        raise ValueError(
            "Missing ils_dispy after merge; EUROMOD outputs did not align. "
            f"Example missing pairs: {missing.to_dict(orient='records')}"
        )

    if "idhh_true" in merged.columns:
        merged["idhh"] = merged["idhh_true"]

    drop_cols = [c for c in ["idperson_true", "idhh_true"] if c in merged.columns]
    merged = merged.drop(columns=drop_cols)
    return merged


def _build_mnl_block(df: pd.DataFrame, sample_group: str) -> pd.DataFrame:
    df = df.copy()

    if "idperson" not in df.columns or "draw" not in df.columns or "is_chosen" not in df.columns:
        raise KeyError("Expected columns 'idperson', 'draw', 'is_chosen'.")
    if "ils_dispy" not in df.columns:
        raise KeyError("Expected EUROMOD disposable income 'ils_dispy' after merge.")

    hours = pd.to_numeric(df.get("hours", df.get("lhw")), errors="coerce").fillna(0.0)
    df["hours"] = hours

    leisure = TOTAL_LEISURE_HOURS - hours
    leisure = leisure.clip(lower=DCM_MIN_POSITIVE)
    df["leisure"] = leisure

    ils = pd.to_numeric(df["ils_dispy"], errors="coerce")
    other_raw = df["other_members_income"] if "other_members_income" in df.columns else pd.Series(0.0, index=df.index)
    other_inc = pd.to_numeric(other_raw, errors="coerce").fillna(0.0)
    ruro_group = pd.to_numeric(df.get("ruro_group", 0), errors="coerce").fillna(0)

    cons = ils.copy()

    singles_mask = ruro_group.eq(1)
    cons.loc[singles_mask] = ils.loc[singles_mask] + other_inc.loc[singles_mask]

    couples_mask = ruro_group.eq(10)
    if couples_mask.any() and "idhh" in df.columns:
        hh_total = (
            ils.groupby([df["idhh"], df["draw"]])
               .transform("sum")
        )
        cons.loc[couples_mask] = hh_total.loc[couples_mask]

    cons = cons.clip(lower=DCM_MIN_POSITIVE)
    df["consumption"] = cons

    df["log_c"] = np.log(cons)
    df["log_l"] = np.log(leisure)
    df["sample_group"] = sample_group

    # Education dummies from highest status (deh) if available
    if "deh" in df.columns:
        deh_num = pd.to_numeric(df["deh"], errors="coerce")
        df["educL"] = (deh_num.isin([0, 1, 2])).astype(int)
        df["educH"] = (deh_num == 5).astype(int)
        df["educM"] = (~df["educL"].astype(bool) & ~df["educH"].astype(bool)).astype(int)

    # Experience squared helper if not already present
    if "pexp_years" in df.columns and "pexp_years2" not in df.columns:
        pexp_num = pd.to_numeric(df["pexp_years"], errors="coerce").fillna(0.0)
        df["pexp_years2"] = pexp_num * pexp_num

    return df


def _transform_couples_to_wide(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform couples data from long format (one row per person) to wide format
    (one row per household with _m and _f suffixes).
    
    This follows Stijn Van Houtven's approach in f_preparedata_est():
    - Common household variables stay as single columns
    - Person-specific variables get _m (male) and _f (female) suffixes
    
    Parameters
    ----------
    df : pd.DataFrame
        Long-format couples data with columns: idhh, draw, dgn, hours, wage, etc.
        Each household has 2 rows per draw (one for male, one for female partner).
    
    Returns
    -------
    pd.DataFrame
        Wide-format data with one row per (household, draw) combination.
        Columns like hours_m, hours_f, wage_m, wage_f, etc.
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    # -------------------------------------------------------------------------
    # Step 1: Filter to only decider couples (exclude children, other HH members)
    # -------------------------------------------------------------------------
    if "ruro_decider" in df.columns:
        n_before = len(df)
        df = df[df["ruro_decider"] == 1].copy()
        n_after = len(df)
        if n_before != n_after:
            LOGGER.info(f"  Filtered to ruro_decider==1: {n_before} -> {n_after} rows")
    
    # Ensure dgn exists
    if "dgn" not in df.columns:
        raise KeyError("Couples data must contain 'dgn' (gender) column for wide transformation.")
    
    dgn = pd.to_numeric(df["dgn"], errors="coerce").fillna(1).astype(int)
    df["_gender"] = np.where(dgn == 1, "m", "f")
    
    # -------------------------------------------------------------------------
    # Step 2: Identify and exclude same-sex couples
    # -------------------------------------------------------------------------
    index_cols = ["idhh", "draw"]
    if "idhh_true" in df.columns:
        index_cols = ["idhh", "idhh_true", "draw"]
    
    gender_counts = df.groupby(index_cols)["_gender"].nunique()
    same_sex_mask = gender_counts == 1
    different_sex_mask = gender_counts == 2
    
    n_same_sex = same_sex_mask.sum()
    n_different_sex = different_sex_mask.sum()
    
    if n_same_sex > 0:
        # Get unique households with same-sex couples
        same_sex_hh = same_sex_mask[same_sex_mask].index.get_level_values("idhh").unique()
        LOGGER.warning(f"  Excluding {len(same_sex_hh)} same-sex couple households "
                      f"({n_same_sex} household-draw combinations). "
                      f"These require separate handling with different column naming.")
        
        # Keep only different-sex couples
        complete_idx = different_sex_mask[different_sex_mask].index
        df = df.set_index(index_cols).loc[complete_idx].reset_index()
    
    LOGGER.info(f"Transforming couples to wide format...")
    LOGGER.info(f"  {n_different_sex} different-sex couple household-draw combinations")
    
    # -------------------------------------------------------------------------
    # Step 3: Verify exactly 2 persons per household-draw
    # -------------------------------------------------------------------------
    person_counts = df.groupby(index_cols).size()
    not_two = person_counts[person_counts != 2]
    if len(not_two) > 0:
        LOGGER.warning(f"  {len(not_two)} (household, draw) combinations don't have exactly 2 persons.")
        # Keep only pairs with exactly 2 persons
        valid_idx = person_counts[person_counts == 2].index
        df = df.set_index(index_cols).loc[valid_idx].reset_index()
    
    # Define common (household-level) variables that should NOT be pivoted
    # These stay as single columns in the wide format
    common_vars = [
        # IDs
        "idhh", "idhh_true", "idorighh",
        # Draw and choice info
        "draw", "is_chosen",
        # Group identifiers
        "ruro_group", "group", "groupy", "sample_group",
        # Household characteristics (same for both partners)
        "children0_3", "children4_6", "children7_9", "children",
        "hh_size", "hhlma",
        # Region (household-level)
        "drgn1", "drgn2", "regW", "regB", "reg2", "reg3",
        # Year dummies
        "year", "yd1", "yd2", "yd3",
        # Weights
        "dwt",
        # Prior (will be recomputed for wide format)
        "prior",
        # Other household-level
        "other_members_income",
    ]
    
    # Get all columns in the dataframe
    all_cols = list(df.columns)
    
    # Determine which columns to pivot (person-specific)
    # Exclude common vars and the gender column we just created
    exclude_cols = set(common_vars + ["_gender", "dgn", "ruro_decider"])
    pivot_cols = [c for c in all_cols if c not in exclude_cols]
    
    # Keep only common vars that actually exist in the data
    existing_common = [c for c in common_vars if c in all_cols]
    
    LOGGER.info(f"  Common (household) vars: {len(existing_common)}")
    LOGGER.info(f"  Person-specific vars to pivot: {len(pivot_cols)}")
    
    # -------------------------------------------------------------------------
    # Step 4: Pivot the data
    # -------------------------------------------------------------------------
    # First, get the common vars from the male partner (arbitrary choice, should be same)
    common_df = df[df["_gender"] == "m"][index_cols + [c for c in existing_common if c not in index_cols]].copy()
    
    # Now pivot the person-specific columns
    pivot_df = df.pivot(
        index=index_cols,
        columns="_gender",
        values=pivot_cols
    )
    
    # Flatten multi-level column names: (hours, m) -> hours_m
    pivot_df.columns = [f"{col}_{gender}" for col, gender in pivot_df.columns]
    pivot_df = pivot_df.reset_index()
    
    # Merge common vars back
    wide_df = pivot_df.merge(common_df, on=index_cols, how="left")
    
    LOGGER.info(f"  Result: {len(wide_df)} rows, {len(wide_df.columns)} columns")
    
    return wide_df


def _build_couples_mnl_block(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build MNL block for couples after wide transformation.
    
    This computes couple-specific utility variables:
    - leisure_m, leisure_f: leisure for each partner
    - consumption: household total disposable income
    - working_m, working_f: employment indicators
    - working_pt1_m, working_pt2_m, working_ft_m: hours category dummies
    - etc.
    
    Parameters
    ----------
    df : pd.DataFrame
        Wide-format couples data from _transform_couples_to_wide()
    
    Returns
    -------
    pd.DataFrame
        MNL-ready couples dataset with all required variables
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    # -------------------------------------------------------------------------
    # Hours and leisure for each partner
    # -------------------------------------------------------------------------
    hours_m = pd.to_numeric(df.get("hours_m", df.get("lhw_m", 0)), errors="coerce").fillna(0.0)
    hours_f = pd.to_numeric(df.get("hours_f", df.get("lhw_f", 0)), errors="coerce").fillna(0.0)
    
    df["hours_m"] = hours_m
    df["hours_f"] = hours_f
    
    df["leisure_m"] = (TOTAL_LEISURE_HOURS - hours_m).clip(lower=DCM_MIN_POSITIVE)
    df["leisure_f"] = (TOTAL_LEISURE_HOURS - hours_f).clip(lower=DCM_MIN_POSITIVE)
    
    # Normalized leisure (following Stijn: (168-hours)/(168-mean_lhw))
    # Using 35 as mean hours (approx full-time)
    MEAN_LHW = 35.0
    df["leis_util_m"] = (168 - hours_m) / (168 - MEAN_LHW)
    df["leis_util_f"] = (168 - hours_f) / (168 - MEAN_LHW)
    
    # -------------------------------------------------------------------------
    # Consumption (household total disposable income)
    # -------------------------------------------------------------------------
    # Sum of both partners' ils_dispy
    ils_m = pd.to_numeric(df.get("ils_dispy_m", 0), errors="coerce").fillna(0.0)
    ils_f = pd.to_numeric(df.get("ils_dispy_f", 0), errors="coerce").fillna(0.0)
    
    consumption = (ils_m + ils_f).clip(lower=DCM_MIN_POSITIVE)
    df["consumption"] = consumption
    
    # Normalized consumption (following Stijn)
    MEAN_DISPY = 2500.0  # approximate monthly household disposable income
    df["dispy_util_m"] = ils_m / MEAN_DISPY
    df["dispy_util_f"] = ils_f / MEAN_DISPY
    df["c_norm"] = consumption / MEAN_DISPY
    
    df["log_c"] = np.log(consumption)
    df["log_l_m"] = np.log(df["leisure_m"])
    df["log_l_f"] = np.log(df["leisure_f"])
    
    # -------------------------------------------------------------------------
    # Working indicators
    # -------------------------------------------------------------------------
    df["working_m"] = (hours_m > 0).astype(int)
    df["working_f"] = (hours_f > 0).astype(int)
    
    # Part-time and full-time dummies (following Stijn's thresholds)
    df["working_pt1_m"] = ((hours_m >= 18.5) & (hours_m <= 20.5)).astype(int)
    df["working_pt2_m"] = ((hours_m >= 29.5) & (hours_m <= 30.5)).astype(int)
    df["working_ft_m"] = ((hours_m >= 37.5) & (hours_m <= 40.5)).astype(int)
    
    df["working_pt1_f"] = ((hours_f >= 18.5) & (hours_f <= 20.5)).astype(int)
    df["working_pt2_f"] = ((hours_f >= 29.5) & (hours_f <= 30.5)).astype(int)
    df["working_ft_f"] = ((hours_f >= 37.5) & (hours_f <= 40.5)).astype(int)
    
    # -------------------------------------------------------------------------
    # Wages
    # -------------------------------------------------------------------------
    wage_m = pd.to_numeric(df.get("wage_m", df.get("yivwg_m", 0)), errors="coerce").fillna(0.0)
    wage_f = pd.to_numeric(df.get("wage_f", df.get("yivwg_f", 0)), errors="coerce").fillna(0.0)
    df["wage_m"] = wage_m
    df["wage_f"] = wage_f
    
    # -------------------------------------------------------------------------
    # Age variables
    # -------------------------------------------------------------------------
    dag_m = pd.to_numeric(df.get("dag_m", 40), errors="coerce").fillna(40)
    dag_f = pd.to_numeric(df.get("dag_f", 40), errors="coerce").fillna(40)
    df["dag_m"] = dag_m
    df["dag_f"] = dag_f
    df["log_age_m"] = np.log(dag_m.clip(lower=18))
    df["log_age_f"] = np.log(dag_f.clip(lower=18))
    
    # -------------------------------------------------------------------------
    # Education variables
    # -------------------------------------------------------------------------
    if "deh_m" in df.columns:
        deh_m = pd.to_numeric(df["deh_m"], errors="coerce").fillna(3)
        df["educL_m"] = deh_m.isin([0, 1, 2]).astype(int)
        df["educH_m"] = (deh_m == 5).astype(int)
    else:
        # Try to get from existing educL/educH if already computed
        df["educL_m"] = pd.to_numeric(df.get("educL_m", 0), errors="coerce").fillna(0).astype(int)
        df["educH_m"] = pd.to_numeric(df.get("educH_m", 0), errors="coerce").fillna(0).astype(int)
    
    if "deh_f" in df.columns:
        deh_f = pd.to_numeric(df["deh_f"], errors="coerce").fillna(3)
        df["educL_f"] = deh_f.isin([0, 1, 2]).astype(int)
        df["educH_f"] = (deh_f == 5).astype(int)
    else:
        df["educL_f"] = pd.to_numeric(df.get("educL_f", 0), errors="coerce").fillna(0).astype(int)
        df["educH_f"] = pd.to_numeric(df.get("educH_f", 0), errors="coerce").fillna(0).astype(int)
    
    # -------------------------------------------------------------------------
    # Experience (potential experience based on age and education)
    # -------------------------------------------------------------------------
    if "pexp_m" not in df.columns:
        deh_m = pd.to_numeric(df.get("deh_m", 3), errors="coerce").fillna(3)
        pexp_m = np.maximum(0, np.where(
            deh_m.isin([0, 1, 2]), dag_m - 15,
            np.where(deh_m.isin([3, 4]), dag_m - 19, dag_m - 23)
        )) / 100.0
        df["pexp_m"] = pexp_m
    
    if "pexp_f" not in df.columns:
        deh_f = pd.to_numeric(df.get("deh_f", 3), errors="coerce").fillna(3)
        pexp_f = np.maximum(0, np.where(
            deh_f.isin([0, 1, 2]), dag_f - 15,
            np.where(deh_f.isin([3, 4]), dag_f - 19, dag_f - 23)
        )) / 100.0
        df["pexp_f"] = pexp_f
    
    # -------------------------------------------------------------------------
    # Region dummies (use household-level region)
    # -------------------------------------------------------------------------
    if "drgn1" in df.columns:
        drgn1 = pd.to_numeric(df["drgn1"], errors="coerce").fillna(1)
        df["reg2"] = (drgn1 == 2).astype(int)
        df["reg3"] = (drgn1 == 3).astype(int)
    
    # -------------------------------------------------------------------------
    # GSUR for both partners (if available)
    # -------------------------------------------------------------------------
    if "gsur_m" not in df.columns and "gsur" in df.columns:
        df["gsur_m"] = df["gsur"]
        df["gsur_f"] = df["gsur"]
    
    df["sample_group"] = "couples"
    
    return df


def _compute_prior_couples(
    df: pd.DataFrame,
    *,
    wage_spec: str = DEFAULT_WAGE_SPEC,
    pi0_m: float = DEFAULT_PI0_M,
    pi0_f: float = DEFAULT_PI0_F,
    h_min: float = DEFAULT_H_MIN,
    h_max: float = DEFAULT_H_MAX,
    w_min: float = DEFAULT_W_MIN,
    w_max: float = DEFAULT_W_MAX,
) -> pd.DataFrame:
    """
    Compute prior (proposal density) for couples in wide format.
    
    For couples, the prior is the PRODUCT of both partners' priors
    (since draws are independent for male and female):
    
        prior = p(h_m, w_m) * p(h_f, w_f)
    
    Following Stijn's R code:
        prior = log(ifelse(hours_m==0, pi0_m, (1-pi0_m)*(1/(h_max-h_min)))
                    *ifelse(wage_m==0, 1, 1/(w_max-w_min))
                    *ifelse(hours_f==0, pi0_f, (1-pi0_f)*(1/(h_max-h_min)))
                    *ifelse(wage_f==0, 1, 1/(w_max-w_min)))
    
    Parameters
    ----------
    df : pd.DataFrame
        Wide-format couples data with hours_m, hours_f, wage_m, wage_f columns.
    wage_spec : str
        'fw' for fixed wages, 'vw' for variable wages.
    pi0_m, pi0_f : float
        Mass at zero hours for active men/women.
    h_min, h_max, w_min, w_max : float
        Support bounds for hours and wages.
    
    Returns
    -------
    pd.DataFrame
        Input dataframe with 'prior' column added (log prior density).
    """
    df = df.copy()
    
    # Get hours for both partners
    hours_m = pd.to_numeric(df.get("hours_m", 0), errors="coerce").fillna(0.0).to_numpy()
    hours_f = pd.to_numeric(df.get("hours_f", 0), errors="coerce").fillna(0.0).to_numpy()
    
    h_support = max(h_max - h_min, DCM_MIN_POSITIVE)
    w_support = max(w_max - w_min, DCM_MIN_POSITIVE)
    
    # Male partner prior
    prior_m = np.where(
        hours_m <= 0,
        pi0_m,  # Zero hours
        (1.0 - pi0_m) * (1.0 / h_support)  # Positive hours
    )
    
    # Female partner prior
    prior_f = np.where(
        hours_f <= 0,
        pi0_f,  # Zero hours
        (1.0 - pi0_f) * (1.0 / h_support)  # Positive hours
    )
    
    if wage_spec == "vw":
        # Variable wages: multiply by wage density for working partners
        wage_m = pd.to_numeric(df.get("wage_m", 0), errors="coerce").fillna(0.0).to_numpy()
        wage_f = pd.to_numeric(df.get("wage_f", 0), errors="coerce").fillna(0.0).to_numpy()
        
        # Wage density is 1/(w_max - w_min) for positive wages, 1 for zero wages
        wage_dens_m = np.where(wage_m > 0, 1.0 / w_support, 1.0)
        wage_dens_f = np.where(wage_f > 0, 1.0 / w_support, 1.0)
        
        prior_m = prior_m * wage_dens_m
        prior_f = prior_f * wage_dens_f
    
    # Joint prior is product of both partners' priors
    prior_density = prior_m * prior_f
    prior_density = np.clip(prior_density, 1e-16, None)
    
    df["prior"] = np.log(prior_density)
    
    LOGGER.info(f"Couples prior computed: mean={df['prior'].mean():.4f}, range=[{df['prior'].min():.4f}, {df['prior'].max():.4f}]")
    
    return df


def _compute_prior(
    df: pd.DataFrame,
    *,
    wage_spec: str = DEFAULT_WAGE_SPEC,
    pi0_m: float = DEFAULT_PI0_M,
    pi0_f: float = DEFAULT_PI0_F,
    h_min: float = DEFAULT_H_MIN,
    h_max: float = DEFAULT_H_MAX,
    w_min: float = DEFAULT_W_MIN,
    w_max: float = DEFAULT_W_MAX,
) -> pd.DataFrame:
    df = df.copy()

    for col in ("lma", "dgn", "hours", "loc"):
        if col not in df.columns:
            raise KeyError(f"RURO dataset must contain '{col}' before computing the prior.")

    if "wage" in df.columns:
        wage = pd.to_numeric(df["wage"], errors="coerce")
    elif "wage_ruro" in df.columns:
        wage = pd.to_numeric(df["wage_ruro"], errors="coerce")
    elif "yivwg" in df.columns:
        wage = pd.to_numeric(df["yivwg"], errors="coerce")
    else:
        raise KeyError("RURO dataset must contain 'wage', 'wage_ruro' or 'yivwg'.")
    df["wage"] = wage

    lma = pd.to_numeric(df["lma"], errors="coerce").fillna(0).astype(int)
    dgn = pd.to_numeric(df["dgn"], errors="coerce").fillna(1).astype(int)
    hours = pd.to_numeric(df["hours"], errors="coerce").fillna(0.0)

    pi0 = np.zeros(len(df), dtype=float)
    active = lma > 0
    mask_m = active & (dgn == 1)
    mask_f = active & (dgn == 0)

    pi0[mask_m.to_numpy()] = pi0_m
    pi0[mask_f.to_numpy()] = pi0_f
    df["pi0"] = pi0

    h_support = max(h_max - h_min, DCM_MIN_POSITIVE)
    w_support = max(w_max - w_min, DCM_MIN_POSITIVE)

    hours_zero = hours <= 0
    hours_pos = ~hours_zero

    loc_pos = pd.to_numeric(df.loc[hours_pos, "loc"], errors="coerce").dropna().unique()
    loc_support = float(len(loc_pos))
    if loc_support <= 0:
        loc_support = 1.0
        LOGGER.warning(
            "No non-missing loc values among positive-hour jobs; "
            "treating loc_support as 1."
        )

    prior_density = np.empty(len(df), dtype=float)

    if wage_spec == "fw":
        prior_density[hours_zero.to_numpy()] = pi0[hours_zero.to_numpy()]
        prior_density[hours_pos.to_numpy()] = (
            (1.0 - pi0[hours_pos.to_numpy()])
            * (1.0 / h_support)
            * (1.0 / loc_support)
        )
    elif wage_spec == "vw":
        prior_density[hours_zero.to_numpy()] = pi0[hours_zero.to_numpy()]
        prior_density[hours_pos.to_numpy()] = (
            (1.0 - pi0[hours_pos.to_numpy()])
            * (1.0 / h_support)
            * (1.0 / w_support)
            * (1.0 / loc_support)
        )
    else:
        raise ValueError("wage_spec must be 'fw' or 'vw'.")

    prior_density = np.clip(prior_density, 1e-16, None)
    df["prior"] = np.log(prior_density)

    return df


def merge_gsur(
    df: pd.DataFrame,
    gsur_path: Optional[Path] = None,
    year: Optional[int] = None,
) -> pd.DataFrame:
    """
    Merge group-specific unemployment rate (GSUR) onto individuals.
    
    GSUR is used as a regressor in the hours opportunity density to capture
    labor market conditions for each demographic group. It does NOT affect draws.
    
    Matching is done on: (year, drgn1, dgn, education_level)
    
    Following Stijn Van Houtven's approach:
    - GSUR varies by sex (dgn), age group, education level, region, and year
    - In the hours opportunity: hopp = ... + β_gsur * working * gsur + ...
    
    Parameters
    ----------
    df : pd.DataFrame
        MNL dataset with columns: dgn, deh (or educL/educH), drgn1, year (optional)
    gsur_path : Path, optional
        Path to GSUR lookup table (parquet). Defaults to FR_gsur_ruro.parquet.
    year : int, optional
        Data year for filtering GSUR. If None, tries to extract from df['year'].
    
    Returns
    -------
    pd.DataFrame
        Input dataframe with added 'gsur' column (unemployment rate as proportion).
    """
    if gsur_path is None:
        gsur_path = DEFAULT_GSUR_PATH
    
    gsur_path = Path(gsur_path)
    if not gsur_path.exists():
        LOGGER.warning(f"GSUR file not found at {gsur_path}; gsur will be set to 0.")
        df = df.copy()
        df["gsur"] = 0.0
        return df
    
    # Load GSUR lookup
    gsur_df = pd.read_parquet(gsur_path)
    LOGGER.info(f"Loaded GSUR lookup with {len(gsur_df)} rows from {gsur_path.name}")
    
    # Determine year
    if year is None:
        if "year" in df.columns:
            year = int(df["year"].mode().iloc[0])
        else:
            # Default to most recent year in GSUR data
            year = int(gsur_df["year"].max())
            LOGGER.warning(f"No year specified; using most recent GSUR year: {year}")
    
    # Filter GSUR to relevant year
    gsur_year = gsur_df[gsur_df["year"] == year].copy()
    if gsur_year.empty:
        # Try closest year
        available_years = sorted(gsur_df["year"].unique())
        closest_year = min(available_years, key=lambda y: abs(y - year))
        LOGGER.warning(f"No GSUR data for year {year}; using {closest_year}")
        gsur_year = gsur_df[gsur_df["year"] == closest_year].copy()
    
    df = df.copy()
    
    # Create education category in main df
    # educL = ED0-2 (low), educM = ED3_4 (medium), educH = ED5-8 (high)
    if "educL" in df.columns and "educH" in df.columns:
        educL = pd.to_numeric(df["educL"], errors="coerce").fillna(0)
        educH = pd.to_numeric(df["educH"], errors="coerce").fillna(0)
        df["_educ_cat"] = np.where(
            educL == 1, "ED0-2",
            np.where(educH == 1, "ED5-8", "ED3_4")
        )
    elif "deh" in df.columns:
        deh = pd.to_numeric(df["deh"], errors="coerce").fillna(3)
        df["_educ_cat"] = np.where(
            deh.isin([0, 1, 2]), "ED0-2",
            np.where(deh == 5, "ED5-8", "ED3_4")
        )
    else:
        LOGGER.warning("No education variable (educL/educH or deh); using TOTAL gsur.")
        df["_educ_cat"] = "TOTAL"
    
    # Ensure dgn exists
    if "dgn" not in df.columns:
        LOGGER.warning("No 'dgn' column; assuming all males (dgn=1).")
        df["dgn"] = 1
    
    # Ensure drgn1 exists (region)
    if "drgn1" not in df.columns:
        LOGGER.warning("No 'drgn1' column; using national average (drgn1=0).")
        df["drgn1"] = 0
    
    dgn = pd.to_numeric(df["dgn"], errors="coerce").fillna(1).astype(int)
    drgn1 = pd.to_numeric(df["drgn1"], errors="coerce").fillna(0).astype(int)
    
    # Prepare GSUR for merging (exclude TOTAL education for now)
    gsur_merge = gsur_year[gsur_year["education"] != "TOTAL"][
        ["drgn1", "dgn", "education", "gsur"]
    ].copy()
    
    # Merge GSUR onto df
    n_before = len(df)
    df = df.merge(
        gsur_merge,
        left_on=["drgn1", "dgn", "_educ_cat"],
        right_on=["drgn1", "dgn", "education"],
        how="left",
        suffixes=("", "_gsur")
    )
    
    # Fill missing gsur with national average for same sex/education
    missing_mask = df["gsur"].isna()
    if missing_mask.any():
        n_missing = missing_mask.sum()
        LOGGER.info(f"Filling {n_missing} missing gsur values with national average...")
        
        # Get national averages (drgn1 == 0)
        national_gsur = gsur_year[
            (gsur_year["drgn1"] == 0) & (gsur_year["education"] != "TOTAL")
        ].set_index(["dgn", "education"])["gsur"].to_dict()
        
        # Fill missing values
        for idx in df[missing_mask].index:
            key = (int(df.loc[idx, "dgn"]), df.loc[idx, "_educ_cat"])
            if key in national_gsur:
                df.loc[idx, "gsur"] = national_gsur[key]
            else:
                # Ultimate fallback: overall average
                df.loc[idx, "gsur"] = gsur_year["gsur"].mean()
    
    # Clean up temporary columns
    df = df.drop(columns=["_educ_cat", "education"], errors="ignore")
    
    # Ensure gsur is float and fill any remaining NaN
    df["gsur"] = pd.to_numeric(df["gsur"], errors="coerce").fillna(0.0)
    
    LOGGER.info(f"GSUR merged: mean={df['gsur'].mean():.4f}, range=[{df['gsur'].min():.4f}, {df['gsur'].max():.4f}]")
    
    return df


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Prepare RURO MNL estimation dataset by merging draws with EUROMOD outputs."
    )
    ap.add_argument(
        "--singles-draws",
        type=str,
        required=True,
        help="Path to singles_RURO_ready_RURO_draws.parquet (or .csv, .pkl).",
    )
    ap.add_argument(
        "--couples-draws",
        type=str,
        required=False,
        help="Path to couples_RURO_ready_RURO_draws.parquet (optional).",
    )
    ap.add_argument(
        "--euromod-combined",
        type=str,
        required=True,
        help="Path to combined_draws_em.parquet (from RURO_euromod.py).",
    )
    ap.add_argument(
        "--out-base",
        type=str,
        required=True,
        help="Base path for output (without extension), e.g. fr_2021_RURO_mnl",
    )
    ap.add_argument(
        "--wage-spec",
        type=str,
        choices=["fw", "vw"],
        default=DEFAULT_WAGE_SPEC,
        help="Wage opportunity specification used for the prior: 'fw' fixed or 'vw' variable.",
    )
    ap.add_argument(
        "--pi0-m",
        type=float,
        default=DEFAULT_PI0_M,
        help="Mass at zero hours for active men.",
    )
    ap.add_argument(
        "--pi0-f",
        type=float,
        default=DEFAULT_PI0_F,
        help="Mass at zero hours for active women.",
    )
    ap.add_argument(
        "--h-min",
        type=float,
        default=DEFAULT_H_MIN,
        help="Lower bound of hour support for opportunities.",
    )
    ap.add_argument(
        "--h-max",
        type=float,
        default=DEFAULT_H_MAX,
        help="Upper bound of hour support for opportunities.",
    )
    ap.add_argument(
        "--w-min",
        type=float,
        default=DEFAULT_W_MIN,
        help="Lower bound of wage support for opportunities.",
    )
    ap.add_argument(
        "--w-max",
        type=float,
        default=DEFAULT_W_MAX,
        help="Upper bound of wage support for opportunities.",
    )
    ap.add_argument(
        "--gsur-file",
        type=str,
        default=None,
        help="Path to GSUR lookup table (parquet). If not provided, uses default FR_gsur_ruro.parquet.",
    )
    ap.add_argument(
        "--year",
        type=int,
        default=None,
        help="Data year for GSUR lookup. If not provided, extracted from data or uses most recent.",
    )
    ap.add_argument(
        "--no-gsur",
        action="store_true",
        help="Skip GSUR merge (gsur column will be 0).",
    )
    return ap.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    args = parse_args()

    em_path = Path(args.euromod_combined).resolve()
    if not em_path.exists():
        raise FileNotFoundError(f"EUROMOD combined file not found: {em_path}")
    em_df = _read_df(em_path)

    prior_kwargs = dict(
        wage_spec=args.wage_spec,
        pi0_m=args.pi0_m,
        pi0_f=args.pi0_f,
        h_min=args.h_min,
        h_max=args.h_max,
        w_min=args.w_min,
        w_max=args.w_max,
    )

    # -------------------------------------------------------------------------
    # Process singles (long format)
    # -------------------------------------------------------------------------
    singles_path = Path(args.singles_draws).resolve()
    if not singles_path.exists():
        raise FileNotFoundError(f"Singles draws file not found: {singles_path}")
    singles_long = _read_df(singles_path)
    singles_long = _merge_euromod_outputs(singles_long, em_df)
    singles_mnl = _build_mnl_block(singles_long, sample_group="singles")
    
    # Compute prior for singles (long format with dgn, lma, hours, loc columns)
    LOGGER.info("Computing prior for singles...")
    singles_mnl = _compute_prior(singles_mnl, **prior_kwargs)

    frames = [singles_mnl]

    # -------------------------------------------------------------------------
    # Process couples (transform to wide format)
    # -------------------------------------------------------------------------
    if args.couples_draws:
        couples_path = Path(args.couples_draws).resolve()
        if not couples_path.exists():
            raise FileNotFoundError(f"Couples draws file not found: {couples_path}")
        couples_long = _read_df(couples_path)
        couples_long = _merge_euromod_outputs(couples_long, em_df)
        
        # Transform to wide format (one row per household-draw)
        couples_wide = _transform_couples_to_wide(couples_long)
        couples_mnl = _build_couples_mnl_block(couples_wide)
        
        # Compute prior for couples (wide format with hours_m, hours_f columns)
        LOGGER.info("Computing prior for couples...")
        couples_mnl = _compute_prior_couples(couples_mnl, **prior_kwargs)
        
        frames.append(couples_mnl)

    full_mnl = pd.concat(frames, axis=0, ignore_index=True)

    # Check for NaN in key columns - handle separately for singles vs couples
    # Singles have 'idperson', couples have 'idperson_m' and 'idperson_f'
    singles_mask = full_mnl["sample_group"] == "singles"
    if singles_mask.any():
        singles_df = full_mnl[singles_mask]
        if singles_df[["idperson", "draw"]].isna().any().any():
            raise ValueError("Found NaNs in singles idperson/draw after merge; check EUROMOD alignment.")
    
    couples_mask = full_mnl["sample_group"] == "couples"
    if couples_mask.any():
        couples_df = full_mnl[couples_mask]
        # Couples may have idperson_m, idperson_f instead of idperson
        if "idperson_m" in couples_df.columns:
            if couples_df[["idperson_m", "idperson_f", "draw"]].isna().any().any():
                raise ValueError("Found NaNs in couples idperson_m/idperson_f/draw after merge.")
        elif "idhh" in couples_df.columns:
            if couples_df[["idhh", "draw"]].isna().any().any():
                raise ValueError("Found NaNs in couples idhh/draw after merge.")

    # Merge GSUR (group-specific unemployment rate) for estimation
    # GSUR is used as a regressor in hours opportunity density, NOT in draws/prior
    # Note: For couples in wide format, we need GSUR for both partners
    if not args.no_gsur:
        gsur_path = Path(args.gsur_file) if args.gsur_file else None
        # Merge GSUR only for singles (long format) - couples need separate handling
        if singles_mask.any():
            singles_with_gsur = merge_gsur(full_mnl[singles_mask].copy(), gsur_path=gsur_path, year=args.year)
            full_mnl.loc[singles_mask, "gsur"] = singles_with_gsur["gsur"].values
        # For couples, set gsur to 0 for now (would need gsur_m and gsur_f columns)
        if couples_mask.any():
            if "gsur_m" not in full_mnl.columns:
                full_mnl.loc[couples_mask, "gsur"] = 0.0
                LOGGER.info("Couples gsur set to 0 (would need separate gsur_m/gsur_f columns).")
    else:
        full_mnl["gsur"] = 0.0
        LOGGER.info("GSUR merge skipped (--no-gsur flag); gsur set to 0.")

    out_base = Path(args.out_base).resolve()
    outputs = _write_df(full_mnl, out_base)
    print("MNL dataset written to:")
    for k, v in outputs.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
