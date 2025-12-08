#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-12-06 16:52:34
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/



"""
RURO_estimate_FR.py
===================

Estimation script for a **RURO (Random Utility, Random Opportunity)** labor supply
model for France, based on an already prepared RURO-MNL long dataset.

RURO METHODOLOGY
----------------
The RURO model separates:

1. **PREFERENCES** (utility from consumption and leisure)
   - Deterministic utility U(c, l; X) depends on consumption c, leisure l, and
     individual characteristics X (age, children, education)
   - Box-Cox functional form: u = β_l(X) * BC(l; θ_l) + β_c * BC(c; θ_c)

2. **OPPORTUNITY DENSITIES** (to be estimated)
   These capture the probability that a job with certain (hours, wage) is offered
   to an individual with characteristics X. This is NOT the same as the prior!

   a) **Hours opportunity density** h(h | X):
      - Captures that certain hours are more likely to be offered (peaks at 20h, 30h, 40h)
      - Depends on individual characteristics (education, region, gsur)
      - Parameterized as: log h(h|X) = β_work*1{h>0} + β_pt1*1{h≈20} + β_pt2*1{h≈30}
                                      + β_ft*1{h≈40} + β_gsur*gsur*1{h>0}
                                      + (education × working) + (region × working)

   b) **Wage opportunity density** w(w | h, X) (if wage_spec="vw"):
      - Log-normal: log(w) ~ N(μ(X), σ²)
      - Mean depends on education, experience, region, year
      - μ(X) = β0 + β_educL*educL + β_educH*educH + β_exp*exp + β_exp2*exp²
              + β_region*region + β_year*year

3. **PRIOR** (proposal density, already computed in RURO_prep_mnl_basic.py)
   - This is how we *sampled* the opportunity set: uniform over hours × wages
   - NOT the true opportunity density
   - We subtract log(prior) to correct for importance sampling

LIKELIHOOD
----------
The probability of observing choice j=0 (the actual choice) for individual i:

    P(observed | θ) = exp(V_0) / Σ_j exp(V_j)

where:
    V_j = u(c_j, l_j; θ_pref) + log h(h_j | X; θ_hopp) + log w(w_j | X; θ_wopp) - log(prior_j)

The prior correction (-log prior) is essential: we sampled uniformly, but the true
opportunity density is non-uniform. This is importance sampling.

GROUP HANDLING (aligned with RURO_prep.py pipeline)
---------------------------------------------------
- ruro_group == 1:  Singles (ALL sexes pooled by default)
- ruro_group == 10: Couples

Use --sex to further filter singles:
- --sex m: single males only (dgn == 1)
- --sex f: single females only (dgn == 0)
- --sex pooled: both sexes (default)

Usage:
    # Estimate pooled singles with fixed wages
    python scripts/RURO_estimate_FR.py \\
        --mnl-file path/to/fr_2021_RURO_mnl.parquet \\
        --group 1 --sex pooled --wage-spec fw

    # Estimate single males with variable wages
    python scripts/RURO_estimate_FR.py \\
        --mnl-file path/to/fr_2021_RURO_mnl.parquet \\
        --group 1 --sex m --wage-spec vw

    # Estimate couples
    python scripts/RURO_estimate_FR.py \\
        --mnl-file path/to/fr_2021_RURO_mnl.parquet \\
        --group 10 --wage-spec fw

PERFORMANCE OPTIMIZATIONS
-------------------------
This script includes several speed optimizations:

1. **Pre-computed Data Arrays** (2-5x speedup - ENABLED BY DEFAULT)
   - All DataFrame columns are extracted ONCE before optimization
   - Uses contiguous numpy arrays for better cache locality
   - Avoids pandas overhead during iterations
   
2. **Numba JIT Compilation** (30x faster log-likelihood - OPTIONAL)
   - Install: pip install numba
   - Use with --use-numba flag
   - Accelerates log-likelihood computation significantly
   - NOTE: Gradient uses NumPy (faster than Numba for matrix operations)
   
3. **Joblib Parallelization** (for joint estimation)
   - Computes gradients for SM, SF, COU in parallel
   - Use: --n-jobs 32
   
4. **Analytical Gradients** (10-50x vs numerical)
   - L-BFGS-B uses exact gradients, not finite differences
   - Much faster convergence

PERFORMANCE TIPS
----------------
For maximum speed:

1. Install numba: pip install numba
2. Install Intel MKL numpy: pip install intel-numpy 
3. Use L-BFGS-B optimizer (default): --optimizer L-BFGS-B
4. Ensure data is sorted by household ID before loading
5. For joint estimation: --n-jobs 32 --joint
"""

from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.optimize import minimize

# Optional imports for parallelization and JIT compilation
try:
    from joblib import Parallel, delayed
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

try:
    from numba import njit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOGGER = logging.getLogger(__name__)

# Parallelization settings - adjust based on your system
# For 32 physical cores (64 logical), we use ~32 workers to avoid hyperthreading overhead
N_JOBS = int(os.environ.get("RURO_N_JOBS", min(32, os.cpu_count() or 1)))

# =============================================================================
# Constants (aligned with RURO_draws.py and RURO_prep_mnl_basic.py)
# =============================================================================

TOTAL_LEISURE_HOURS = 80.0
MEAN_DISPY_NORM = 2500.0  # normalization constant for consumption
MEAN_LHW_NORM = 35.0      # normalization constant for leisure


# =============================================================================
# PERFORMANCE OPTIMIZATION: Pre-computed data structure
# =============================================================================
# This avoids repeated DataFrame column access during optimization iterations.
# DataFrame access involves type checking, missing value handling, and is slow.
# By pre-extracting arrays ONCE before optimization, we can get 2-5x speedup.

@dataclass
class PrecomputedDataSingles:
    """
    Pre-extracted numpy arrays for fast singles estimation.
    
    All arrays are contiguous float64 for optimal vectorization.
    This structure is created ONCE before optimization starts.
    
    SIMPLIFIED SPECIFICATION:
    - age_norm = dag - mean(dag) (demeaned, not ratio)
    - age_norm2 = age_norm^2
    - Single n_children replaces ch0_3, ch4_6, ch7_9
    - No region effects (removed for identification)
    - No year dummies (single year)
    """
    # Core utility variables
    c: np.ndarray           # normalized consumption, shape (n,)
    l: np.ndarray           # normalized leisure, shape (n,)
    age_norm: np.ndarray    # demeaned age (dag - mean_dag)
    age_norm2: np.ndarray   # demeaned age squared
    
    # Children (single variable for all children)
    n_children: np.ndarray
    
    # Education dummies
    educL: np.ndarray
    educH: np.ndarray
    
    # Hours indicators
    working: np.ndarray
    working_pt1: np.ndarray
    working_pt2: np.ndarray
    working_ft: np.ndarray
    gsur: np.ndarray
    
    # Wage-related
    log_wage: np.ndarray
    pexp: np.ndarray
    pexp2: np.ndarray       # pre-computed pexp^2
    
    # Prior and grouping
    log_prior: np.ndarray
    group_idx: np.ndarray       # maps each row to group index
    n_groups: int               # number of individuals
    is_obs: np.ndarray          # boolean mask for observed choices
    
    # Group boundaries (for vectorized softmax)
    group_starts: np.ndarray    # start index per group
    group_ends: np.ndarray      # end index per group
    obs_indices: np.ndarray     # observed choice index per group


@dataclass
class PrecomputedDataCouples:
    """
    Pre-extracted numpy arrays for fast couples estimation.
    
    All arrays are contiguous float64 for optimal vectorization.
    This structure is created ONCE before optimization starts.
    
    Couples data is in wide format with _m and _f suffixes.
    Each row is a (household, draw) combination.
    
    SIMPLIFIED SPECIFICATION:
    - age_norm = dag - mean(dag) (demeaned, not ratio)
    - Single n_children replaces ch0_3, ch4_6, ch7_9
    - No region effects (removed for identification)
    - No year dummies (single year)
    """
    # Core utility variables (household-level)
    c: np.ndarray               # normalized household consumption, shape (n,)
    
    # Male partner leisure and demographics
    l_m: np.ndarray             # normalized leisure for male
    age_norm_m: np.ndarray      # demeaned age male
    age_norm2_m: np.ndarray     # demeaned age² male
    educL_m: np.ndarray         # low education male
    educH_m: np.ndarray         # high education male
    
    # Female partner leisure and demographics
    l_f: np.ndarray             # normalized leisure for female
    age_norm_f: np.ndarray      # demeaned age female
    age_norm2_f: np.ndarray     # demeaned age² female
    educL_f: np.ndarray         # low education female
    educH_f: np.ndarray         # high education female
    
    # Children (household-level, single variable)
    n_children: np.ndarray
    
    # Hours indicators - male
    working_m: np.ndarray
    working_pt1_m: np.ndarray
    working_pt2_m: np.ndarray
    working_ft_m: np.ndarray
    gsur_m: np.ndarray
    
    # Hours indicators - female
    working_f: np.ndarray
    working_pt1_f: np.ndarray
    working_pt2_f: np.ndarray
    working_ft_f: np.ndarray
    gsur_f: np.ndarray
    
    # Wage-related - male
    log_wage_m: np.ndarray
    pexp_m: np.ndarray
    pexp2_m: np.ndarray         # pre-computed pexp^2
    
    # Wage-related - female
    log_wage_f: np.ndarray
    pexp_f: np.ndarray
    pexp2_f: np.ndarray         # pre-computed pexp^2
    
    # Prior and grouping
    log_prior: np.ndarray
    group_idx: np.ndarray       # maps each row to group index
    n_groups: int               # number of households
    is_obs: np.ndarray          # boolean mask for observed choices
    
    # Group boundaries (for vectorized softmax)
    group_starts: np.ndarray    # start index per group
    group_ends: np.ndarray      # end index per group
    obs_indices: np.ndarray     # observed choice index per group


def precompute_data_singles(df: pd.DataFrame, is_male: bool = True) -> PrecomputedDataSingles:
    """
    Pre-extract all required arrays from DataFrame for singles estimation.
    
    Called ONCE before optimization. Returns PrecomputedDataSingles that is
    passed to all likelihood/gradient calls, avoiding DataFrame overhead.
    
    Parameters
    ----------
    df : pd.DataFrame
        Long-format RURO-MNL dataset for singles
    is_male : bool
        True for single males, False for single females
    
    Returns
    -------
    PrecomputedDataSingles
        All arrays needed for estimation, pre-extracted and contiguous
    """
    n = len(df)
    
    # Helper for safe column extraction
    def safe_get(col: str, default: float = 0.0) -> np.ndarray:
        if col in df.columns:
            arr = pd.to_numeric(df[col], errors="coerce").fillna(default).to_numpy()
        else:
            arr = np.full(n, default)
        return np.ascontiguousarray(arr, dtype=np.float64)      # -------------------------------------------------------------------------
    # Consumption and leisure (normalized)
    # -------------------------------------------------------------------------
    # CRITICAL FIX: Check if consumption varies within choice sets.
    # If ils_dispy is constant (EUROMOD not run for each draw), we need to
    # compute a synthetic consumption that varies with earnings.
    #
    # The standard approach is: c = non_labor_income + (1 - avg_tax_rate) * earnings
    # We approximate this as: c = base_dispy + 0.6 * (yem - base_yem)
    # where 0.6 approximates (1 - marginal_tax_rate) for typical workers
    
    c = None
    
    # First try normalized columns
    if "c_norm" in df.columns and not df["c_norm"].isna().all():
        c = df["c_norm"].to_numpy(dtype=np.float64)
    if c is None and "dispy_util" in df.columns and not df["dispy_util"].isna().all():
        c = df["dispy_util"].to_numpy(dtype=np.float64)
    
    # Check if consumption varies within choice sets
    if c is not None:
        # Group by person and check variation
        if "idperson_true" in df.columns:
            ids = df["idperson_true"].to_numpy()
        elif "idperson" in df.columns:
            ids = df["idperson"].to_numpy()
        else:
            ids = None
        
        if ids is not None:
            # Check variance within first 100 individuals
            unique_ids = np.unique(ids)[:100]
            c_varies = False
            for uid in unique_ids:
                mask = ids == uid
                if mask.sum() > 1 and np.std(c[mask]) > 1e-6:
                    c_varies = True
                    break
            
            if not c_varies:
                LOGGER.warning("Consumption does NOT vary within choice sets - will compute synthetic consumption")
                c = None  # Force recomputation
    
    # If no valid consumption, try to compute from ils_dispy + yem
    if c is None:
        ils_dispy = None
        yem = None
        
        if "ils_dispy" in df.columns:
            ils_dispy = pd.to_numeric(df["ils_dispy"], errors="coerce").fillna(0).to_numpy(dtype=np.float64)
        if "yem" in df.columns:
            yem = pd.to_numeric(df["yem"], errors="coerce").fillna(0).to_numpy(dtype=np.float64)
        
        if ils_dispy is not None and yem is not None:
            # Compute synthetic consumption that varies with earnings
            # c = base_non_labor_income + net_earnings
            # Approximate: c = ils_dispy_observed - 0.6*yem_observed + 0.6*yem_hypothetical
            # For each person, base = ils_dispy[draw=0] - 0.6*yem[draw=0]
            
            if "idperson_true" in df.columns:
                ids = df["idperson_true"].to_numpy()
            elif "idperson" in df.columns:
                ids = df["idperson"].to_numpy()
            else:
                ids = np.arange(n)
            
            draws = df["draw"].to_numpy() if "draw" in df.columns else np.zeros(n)
            
            # Get base (observed) values per person
            unique_ids, inverse = np.unique(ids, return_inverse=True)
            base_ils = np.zeros(len(unique_ids), dtype=np.float64)
            base_yem = np.zeros(len(unique_ids), dtype=np.float64)
            
            for i, uid in enumerate(unique_ids):
                mask = (ids == uid) & (draws == 0)
                if mask.any():
                    base_ils[i] = ils_dispy[mask][0]
                    base_yem[i] = yem[mask][0]
                else:
                    # Fallback: use first observation for this person
                    mask = ids == uid
                    base_ils[i] = ils_dispy[mask][0]
                    base_yem[i] = yem[mask][0]
            
            # Compute: c = base_non_labor + 0.6 * yem_hypothetical
            # where base_non_labor = base_ils - 0.6 * base_yem
            IMPLICIT_TAX_RATE = 0.40  # Approximate average marginal tax rate
            NET_OF_TAX = 1.0 - IMPLICIT_TAX_RATE
            
            base_non_labor = base_ils - NET_OF_TAX * base_yem
            c = base_non_labor[inverse] + NET_OF_TAX * yem
            c = c / MEAN_DISPY_NORM  # Normalize
            
            LOGGER.info(f"Computed synthetic consumption: mean={c.mean():.3f}, std={c.std():.3f}")
        
        elif "consumption" in df.columns:
            c = df["consumption"].to_numpy(dtype=np.float64) / MEAN_DISPY_NORM
        elif ils_dispy is not None:
            c = ils_dispy / MEAN_DISPY_NORM
        else:
            c = np.ones(n, dtype=np.float64)
            LOGGER.warning("No consumption data found - using constant consumption (β_c won't be identified)")
      # Check l_norm first, but only use if it has non-NaN values
    l = None
    if "l_norm" in df.columns and not df["l_norm"].isna().all():
        l = df["l_norm"].to_numpy(dtype=np.float64)
    if l is None and "leis_util" in df.columns and not df["leis_util"].isna().all():
        l = df["leis_util"].to_numpy(dtype=np.float64)
    if l is None and "leisure" in df.columns:
        l = df["leisure"].to_numpy(dtype=np.float64) / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    if l is None and "hours" in df.columns:
        hours = df["hours"].to_numpy(dtype=np.float64)
        l = (TOTAL_LEISURE_HOURS - hours) / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    if l is None:
        l = np.ones(n, dtype=np.float64)
    
    c = np.ascontiguousarray(np.clip(c, 1e-6, None), dtype=np.float64)
    l = np.ascontiguousarray(np.clip(l, 1e-6, None), dtype=np.float64)
      # -------------------------------------------------------------------------
    # Age (normalized) and children
    # -------------------------------------------------------------------------
    age_norm = safe_get("age_norm")   # demeaned age (dag - mean_dag)
    age_norm2 = safe_get("age_norm2") # demeaned age squared
    
    # Children: use total n_children
    n_children = safe_get("n_children")
    
    # Education dummies
    educL = safe_get("educL")
    educH = safe_get("educH")
      # -------------------------------------------------------------------------
    # Hours indicators
    # -------------------------------------------------------------------------
    working = safe_get("working")
    if working.sum() == 0 and "hours" in df.columns:
        hours = pd.to_numeric(df["hours"], errors="coerce").fillna(0).to_numpy()
        working = np.ascontiguousarray((hours > 0).astype(np.float64))
    
    working_pt1 = safe_get("working_pt1")
    working_pt2 = safe_get("working_pt2")
    working_ft = safe_get("working_ft")
    
    if working_pt1.sum() == 0 and "hours" in df.columns:
        hours = pd.to_numeric(df["hours"], errors="coerce").fillna(0).to_numpy()
        working_pt1 = np.ascontiguousarray(((hours >= 18.5) & (hours <= 21.5)).astype(np.float64))
        working_pt2 = np.ascontiguousarray(((hours >= 29.5) & (hours <= 30.5)).astype(np.float64))
        working_ft = np.ascontiguousarray(((hours >= 37.5) & (hours <= 40.5)).astype(np.float64))
    
    gsur = safe_get("gsur")
    
    # -------------------------------------------------------------------------
    # Wage-related (pre-compute pexp^2 for speed)
    # -------------------------------------------------------------------------
    # Priority: wage_final > yivwg > wage (wage may be 0 for observed choices)
    if "wage_final" in df.columns:
        wage = pd.to_numeric(df["wage_final"], errors="coerce").fillna(1).to_numpy(dtype=np.float64)
    elif "yivwg" in df.columns:
        wage = pd.to_numeric(df["yivwg"], errors="coerce").fillna(1).to_numpy(dtype=np.float64)
    elif "wage" in df.columns:
        wage = pd.to_numeric(df["wage"], errors="coerce").fillna(1).to_numpy(dtype=np.float64)
    else:
        wage = np.ones(n, dtype=np.float64)
    wage = np.clip(wage, 1e-6, None)
    log_wage = np.ascontiguousarray(np.log(wage))
    
    if "pexp" in df.columns:
        pexp = pd.to_numeric(df["pexp"], errors="coerce").fillna(0).to_numpy(dtype=np.float64)
    elif "pexp_years" in df.columns:
        pexp = pd.to_numeric(df["pexp_years"], errors="coerce").fillna(0).to_numpy(dtype=np.float64) / 100.0
    else:
        pexp = np.zeros(n, dtype=np.float64)
    pexp = np.ascontiguousarray(pexp)
    pexp2 = np.ascontiguousarray(pexp ** 2)  # Pre-compute!
    
    # -------------------------------------------------------------------------
    # Prior
    # -------------------------------------------------------------------------
    if "prior" in df.columns:
        log_prior = pd.to_numeric(df["prior"], errors="coerce").fillna(0).to_numpy(dtype=np.float64)
    else:
        log_prior = np.zeros(n, dtype=np.float64)
    log_prior = np.ascontiguousarray(log_prior)
    
    # -------------------------------------------------------------------------
    # Group structure (assumes data sorted by id!)
    # For SINGLES, we must group by PERSON (idperson), not household (idhh),
    # because multiple single persons can share a household.
    # -------------------------------------------------------------------------
    if "idperson_true" in df.columns:
        ids = df["idperson_true"].to_numpy()
    elif "idperson" in df.columns:
        ids = df["idperson"].to_numpy()
    elif "idhh_true" in df.columns:
        ids = df["idhh_true"].to_numpy()
    elif "idhh" in df.columns:
        ids = df["idhh"].to_numpy()
    else:
        raise KeyError("Need 'idperson_true', 'idperson', 'idhh_true', or 'idhh'")
    
    unique_ids, group_idx = np.unique(ids, return_inverse=True)
    n_groups = len(unique_ids)
    group_idx = np.ascontiguousarray(group_idx.astype(np.int64))
    
    # Observed choices
    draws = df["draw"].to_numpy()
    if "is_chosen" in df.columns:
        is_chosen = pd.to_numeric(df["is_chosen"], errors="coerce").fillna(0).to_numpy()
        is_obs = np.ascontiguousarray(((is_chosen == 1) | (draws == 0)).astype(bool))
    else:
        is_obs = np.ascontiguousarray((draws == 0).astype(bool))
    
    # Group boundaries
    id_changes = np.where(np.diff(ids) != 0)[0] + 1
    group_starts = np.ascontiguousarray(np.concatenate([[0], id_changes]).astype(np.int64))
    group_ends = np.ascontiguousarray(np.concatenate([id_changes, [n]]).astype(np.int64))
    
    # Observed index per group
    obs_indices = np.zeros(n_groups, dtype=np.int64)
    for g in range(n_groups):
        s, e = group_starts[g], group_ends[g]
        obs_in_group = np.where(is_obs[s:e])[0]
        obs_indices[g] = s + obs_in_group[0] if len(obs_in_group) > 0 else s
    obs_indices = np.ascontiguousarray(obs_indices)
    
    return PrecomputedDataSingles(
        c=c, l=l, age_norm=age_norm, age_norm2=age_norm2,
        n_children=n_children,
        educL=educL, educH=educH,
        working=working, working_pt1=working_pt1, working_pt2=working_pt2, working_ft=working_ft,
        gsur=gsur, log_wage=log_wage, pexp=pexp, pexp2=pexp2,
        log_prior=log_prior, group_idx=group_idx, n_groups=n_groups, is_obs=is_obs,
        group_starts=group_starts, group_ends=group_ends, obs_indices=obs_indices,
    )


def precompute_data_couples(df: pd.DataFrame) -> PrecomputedDataCouples:
    """
    Pre-extract all required arrays from DataFrame for couples estimation.
    
    Called ONCE before optimization. Returns PrecomputedDataCouples that is
    passed to all likelihood/gradient calls, avoiding DataFrame overhead.
    
    Parameters
    ----------
    df : pd.DataFrame
        Wide-format RURO-MNL dataset for couples (columns have _m and _f suffixes)
    
    Returns
    -------    PrecomputedDataCouples
        All arrays needed for estimation, pre-extracted and contiguous
    """
    n = len(df)
    
    def safe_get(col: str, default: float = 0.0) -> np.ndarray:
        if col in df.columns:
            arr = pd.to_numeric(df[col], errors="coerce").fillna(default).to_numpy()
        else:
            arr = np.full(n, default)
        return np.ascontiguousarray(arr, dtype=np.float64)
    
    # -------------------------------------------------------------------------
    # Consumption (household-level, normalized)
    # CRITICAL FIX: Check if consumption varies within choice sets.
    # If not, compute synthetic consumption from earnings.
    # -------------------------------------------------------------------------
    c = None
    
    if "c_norm" in df.columns and not df["c_norm"].isna().all():
        c = df["c_norm"].to_numpy(dtype=np.float64)
    
    # Check if consumption varies within choice sets
    if c is not None:
        if "idhh_true" in df.columns:
            ids = df["idhh_true"].to_numpy()
        elif "idhh" in df.columns:
            ids = df["idhh"].to_numpy()
        else:
            ids = None
        
        if ids is not None:
            unique_ids = np.unique(ids)[:100]
            c_varies = False
            for uid in unique_ids:
                mask = ids == uid
                if mask.sum() > 1 and np.std(c[mask]) > 1e-6:
                    c_varies = True
                    break
            
            if not c_varies:
                LOGGER.warning("Couples consumption does NOT vary within choice sets - will compute synthetic")
                c = None
      # If no valid consumption, compute from earnings
    if c is None:
        ils_m = safe_get("ils_dispy_m", 0.0)
        ils_f = safe_get("ils_dispy_f", 0.0)
        yem_m = safe_get("yem_m", 0.0)
        yem_f = safe_get("yem_f", 0.0)
        
        # Check if we have earnings data
        if np.any(yem_m > 0) or np.any(yem_f > 0):
            # Get base values per household
            if "idhh_true" in df.columns:
                ids = df["idhh_true"].to_numpy()
            elif "idhh" in df.columns:
                ids = df["idhh"].to_numpy()
            else:
                ids = np.arange(n)
            
            draws = df["draw"].to_numpy() if "draw" in df.columns else np.zeros(n)
            
            unique_ids, inverse = np.unique(ids, return_inverse=True)
            base_ils_m = np.zeros(len(unique_ids), dtype=np.float64)
            base_ils_f = np.zeros(len(unique_ids), dtype=np.float64)
            base_yem_m = np.zeros(len(unique_ids), dtype=np.float64)
            base_yem_f = np.zeros(len(unique_ids), dtype=np.float64)
            
            for i, uid in enumerate(unique_ids):
                mask = (ids == uid) & (draws == 0)
                if not mask.any():
                    mask = ids == uid
                base_ils_m[i] = ils_m[mask][0]
                base_ils_f[i] = ils_f[mask][0]
                base_yem_m[i] = yem_m[mask][0]
                base_yem_f[i] = yem_f[mask][0]
            
            NET_OF_TAX = 0.60
            base_non_labor = (base_ils_m + base_ils_f) - NET_OF_TAX * (base_yem_m + base_yem_f)
            c = base_non_labor[inverse] + NET_OF_TAX * (yem_m + yem_f)
            c = c / MEAN_DISPY_NORM
            
            LOGGER.info(f"Computed synthetic couples consumption: mean={c.mean():.3f}, std={c.std():.3f}")
        else:
            # Fallback to original ils_dispy
            c = (ils_m + ils_f) / MEAN_DISPY_NORM
            LOGGER.warning("No earnings data for couples - consumption won't vary")
    elif "consumption" in df.columns and c is None:
        c = df["consumption"].to_numpy(dtype=np.float64) / MEAN_DISPY_NORM
    
    c = np.ascontiguousarray(np.clip(c, 1e-6, None), dtype=np.float64)
    
    # Leisure - male
    l_m = None
    if "leis_util_m" in df.columns and not df["leis_util_m"].isna().all():
        l_m = df["leis_util_m"].to_numpy(dtype=np.float64)
    if l_m is None and "leisure_m" in df.columns:
        l_m = df["leisure_m"].to_numpy(dtype=np.float64) / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    if l_m is None and "hours_m" in df.columns:
        hours_m = df["hours_m"].to_numpy(dtype=np.float64)
        l_m = (TOTAL_LEISURE_HOURS - hours_m) / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    if l_m is None:
        l_m = np.ones(n, dtype=np.float64)
    l_m = np.ascontiguousarray(np.clip(l_m, 1e-6, None), dtype=np.float64)
    
    # Leisure - female
    l_f = None
    if "leis_util_f" in df.columns and not df["leis_util_f"].isna().all():
        l_f = df["leis_util_f"].to_numpy(dtype=np.float64)
    if l_f is None and "leisure_f" in df.columns:
        l_f = df["leisure_f"].to_numpy(dtype=np.float64) / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    if l_f is None and "hours_f" in df.columns:
        hours_f = df["hours_f"].to_numpy(dtype=np.float64)
        l_f = (TOTAL_LEISURE_HOURS - hours_f) / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    if l_f is None:
        l_f = np.ones(n, dtype=np.float64)
    l_f = np.ascontiguousarray(np.clip(l_f, 1e-6, None), dtype=np.float64)
      # Age (normalized) - male/female
    age_norm_m = safe_get("age_norm_m")
    age_norm2_m = safe_get("age_norm2_m")
    
    age_norm_f = safe_get("age_norm_f")
    age_norm2_f = safe_get("age_norm2_f")
    
    # Education
    educL_m = safe_get("educL_m")
    educH_m = safe_get("educH_m")
    educL_f = safe_get("educL_f")
    educH_f = safe_get("educH_f")
    
    # Children (household-level, use total n_children)
    n_children = safe_get("n_children")
    
    # Hours indicators - male
    working_m = safe_get("working_m")
    if working_m.sum() == 0 and "hours_m" in df.columns:
        hours_m = pd.to_numeric(df["hours_m"], errors="coerce").fillna(0).to_numpy()
        working_m = np.ascontiguousarray((hours_m > 0).astype(np.float64))
    working_pt1_m = safe_get("working_pt1_m")
    working_pt2_m = safe_get("working_pt2_m")
    working_ft_m = safe_get("working_ft_m")
    if working_pt1_m.sum() == 0 and "hours_m" in df.columns:
        hours_m = pd.to_numeric(df["hours_m"], errors="coerce").fillna(0).to_numpy()
        working_pt1_m = np.ascontiguousarray(((hours_m >= 18.5) & (hours_m <= 21.5)).astype(np.float64))
        working_pt2_m = np.ascontiguousarray(((hours_m >= 29.5) & (hours_m <= 30.5)).astype(np.float64))
        working_ft_m = np.ascontiguousarray(((hours_m >= 37.5) & (hours_m <= 40.5)).astype(np.float64))
    gsur_m = safe_get("gsur_m")
    if gsur_m.sum() == 0:
        gsur_m = safe_get("gsur")
    
    # Hours indicators - female
    working_f = safe_get("working_f")
    if working_f.sum() == 0 and "hours_f" in df.columns:
        hours_f = pd.to_numeric(df["hours_f"], errors="coerce").fillna(0).to_numpy()
        working_f = np.ascontiguousarray((hours_f > 0).astype(np.float64))
    working_pt1_f = safe_get("working_pt1_f")
    working_pt2_f = safe_get("working_pt2_f")
    working_ft_f = safe_get("working_ft_f")
    if working_pt1_f.sum() == 0 and "hours_f" in df.columns:
        hours_f = pd.to_numeric(df["hours_f"], errors="coerce").fillna(0).to_numpy()
        working_pt1_f = np.ascontiguousarray(((hours_f >= 18.5) & (hours_f <= 21.5)).astype(np.float64))
        working_pt2_f = np.ascontiguousarray(((hours_f >= 29.5) & (hours_f <= 30.5)).astype(np.float64))
        working_ft_f = np.ascontiguousarray(((hours_f >= 37.5) & (hours_f <= 40.5)).astype(np.float64))
    gsur_f = safe_get("gsur_f")
    if gsur_f.sum() == 0:
        gsur_f = safe_get("gsur")
    
    # Wages - male
    if "wage_m" in df.columns:
        wage_m = pd.to_numeric(df["wage_m"], errors="coerce").fillna(1).to_numpy(dtype=np.float64)
    elif "yivwg_m" in df.columns:
        wage_m = pd.to_numeric(df["yivwg_m"], errors="coerce").fillna(1).to_numpy(dtype=np.float64)
    else:
        wage_m = np.ones(n, dtype=np.float64)
    wage_m = np.clip(wage_m, 1e-6, None)
    log_wage_m = np.ascontiguousarray(np.log(wage_m))
    
    if "pexp_m" in df.columns:
        pexp_m = pd.to_numeric(df["pexp_m"], errors="coerce").fillna(0).to_numpy(dtype=np.float64)
    else:
        pexp_m = np.zeros(n, dtype=np.float64)
    pexp_m = np.ascontiguousarray(pexp_m)
    pexp2_m = np.ascontiguousarray(pexp_m ** 2)
    
    # Wages - female
    if "wage_f" in df.columns:
        wage_f = pd.to_numeric(df["wage_f"], errors="coerce").fillna(1).to_numpy(dtype=np.float64)
    elif "yivwg_f" in df.columns:
        wage_f = pd.to_numeric(df["yivwg_f"], errors="coerce").fillna(1).to_numpy(dtype=np.float64)
    else:
        wage_f = np.ones(n, dtype=np.float64)
    wage_f = np.clip(wage_f, 1e-6, None)
    log_wage_f = np.ascontiguousarray(np.log(wage_f))
    
    if "pexp_f" in df.columns:
        pexp_f = pd.to_numeric(df["pexp_f"], errors="coerce").fillna(0).to_numpy(dtype=np.float64)
    else:
        pexp_f = np.zeros(n, dtype=np.float64)
    pexp_f = np.ascontiguousarray(pexp_f)
    pexp2_f = np.ascontiguousarray(pexp_f ** 2)
    
    # Prior
    if "prior" in df.columns:
        log_prior = pd.to_numeric(df["prior"], errors="coerce").fillna(0).to_numpy(dtype=np.float64)
    else:
        log_prior = np.zeros(n, dtype=np.float64)
    log_prior = np.ascontiguousarray(log_prior)
    
    # Group structure (by household ID)
    if "idhh" in df.columns:
        ids = df["idhh"].to_numpy()
    else:
        raise KeyError("Couples data must have 'idhh' column")
    
    unique_ids, group_idx = np.unique(ids, return_inverse=True)
    n_groups = len(unique_ids)
    group_idx = np.ascontiguousarray(group_idx.astype(np.int64))
    
    # Observed choices (draw == 0)
    draws = df["draw"].to_numpy()
    is_obs = np.ascontiguousarray((draws == 0).astype(bool))
    
    # Group boundaries
    id_changes = np.where(np.diff(ids) != 0)[0] + 1
    group_starts = np.ascontiguousarray(np.concatenate([[0], id_changes]).astype(np.int64))
    group_ends = np.ascontiguousarray(np.concatenate([id_changes, [n]]).astype(np.int64))
    
    # Observed index per group
    obs_indices = np.zeros(n_groups, dtype=np.int64)
    for g in range(n_groups):
        s, e = group_starts[g], group_ends[g]
        obs_in_group = np.where(is_obs[s:e])[0]
        obs_indices[g] = s + obs_in_group[0] if len(obs_in_group) > 0 else s
    obs_indices = np.ascontiguousarray(obs_indices)
    
    return PrecomputedDataCouples(
        c=c, l_m=l_m, age_norm_m=age_norm_m, age_norm2_m=age_norm2_m,
        educL_m=educL_m, educH_m=educH_m,
        l_f=l_f, age_norm_f=age_norm_f, age_norm2_f=age_norm2_f,
        educL_f=educL_f, educH_f=educH_f,
        n_children=n_children,
        working_m=working_m, working_pt1_m=working_pt1_m, working_pt2_m=working_pt2_m,
        working_ft_m=working_ft_m, gsur_m=gsur_m,
        working_f=working_f, working_pt1_f=working_pt1_f, working_pt2_f=working_pt2_f,
        working_ft_f=working_ft_f, gsur_f=gsur_f,
        log_wage_m=log_wage_m, pexp_m=pexp_m, pexp2_m=pexp2_m,
        log_wage_f=log_wage_f, pexp_f=pexp_f, pexp2_f=pexp2_f,
        log_prior=log_prior, group_idx=group_idx, n_groups=n_groups,
        is_obs=is_obs, group_starts=group_starts, group_ends=group_ends, obs_indices=obs_indices,
    )


def _get_col(df: pd.DataFrame, col: str, default: float = 0.0) -> np.ndarray:
    """
    Safely get a column from a DataFrame, returning default if not present.
    
    This avoids the issue where df.get(col, 0) returns an int when col is missing,
    which breaks pd.to_numeric().
    """
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce").fillna(default).to_numpy()
    else:
        return np.full(len(df), default, dtype=float)


# =============================================================================
# Parameter dataclasses
# =============================================================================

@dataclass
class PrefParamsSingles:
    """
    Preference parameters for single men or single women.
    
    Box-Cox utility structure:
        u = (β_leisure_terms) * (l^θ_l - 1)/θ_l + β_c * (c^θ_c - 1)/θ_c
    
    where β_leisure_terms = β_l0 + β_l_age_norm*age_norm + β_l_age_norm2*age_norm^2
                          + β_l_n_children*n_children
                          + β_l_educL*educL + β_l_educH*educH
    
    SIMPLIFIED SPECIFICATION (vs original):
    - age_norm = dag - mean(dag) (demeaned, not log)
    - age_norm2 = age_norm^2
    - Single n_children replaces ch0_3, ch4_6, ch7_9
    - No region effects on preferences (moved to opportunity)
    """
    # Leisure coefficients
    beta_l0: float = 1.0             # intercept for leisure term
    beta_l_age_norm: float = 0.0     # coefficient on demeaned age
    beta_l_age_norm2: float = 0.0    # coefficient on demeaned age squared
    beta_l_n_children: float = 0.0   # single coefficient for total children count
    beta_l_educL: float = 0.0        # low education
    beta_l_educH: float = 0.0        # high education
    
    # Consumption coefficient
    beta_c: float = 1.0              # coefficient on consumption utility
    
    # Box-Cox exponents (bounds: 0.1-3.0)
    theta_l: float = 0.5             # Box-Cox exponent on leisure
    theta_c: float = 0.5             # Box-Cox exponent on consumption


@dataclass
class PrefParamsCouples:
    """
    Preference parameters for couples (joint utility over male and female leisure).
    
    SIMPLIFIED SPECIFICATION:
    - age_norm = dag - mean(dag) (demeaned, not log)
    - Single n_children replaces ch0_3, ch4_6, ch7_9
    - No region effects on preferences
    - No cross-leisure interaction (unidentified)
    
    Box-Cox utility structure:
        u = (male leisure terms) * (l_m^θ_lm - 1)/θ_lm
          + (female leisure terms) * (l_f^θ_lf - 1)/θ_lf
          + β_c * ((c_m + c_f)^θ_c - 1)/θ_c
    """
    # Male leisure coefficients
    beta_lm0: float = 1.0
    beta_lm_age_norm: float = 0.0
    beta_lm_age_norm2: float = 0.0
    beta_lm_n_children: float = 0.0
    beta_lm_educL: float = 0.0
    beta_lm_educH: float = 0.0
    
    # Female leisure coefficients
    beta_lf0: float = 1.0
    beta_lf_age_norm: float = 0.0
    beta_lf_age_norm2: float = 0.0
    beta_lf_n_children: float = 0.0
    beta_lf_educL: float = 0.0
    beta_lf_educH: float = 0.0
    
    # Consumption coefficient (joint, bounds: -15, 15)
    beta_c: float = 1.0
    
    # Box-Cox exponents (bounds: 0.1-3.0)
    theta_lm: float = 0.5   # male leisure
    theta_lf: float = 0.5   # female leisure
    theta_c: float = 0.5    # consumption


@dataclass
class HoursOppParams:
    """
    Hours opportunity density parameters.
    
    This captures the probability that a job offer with certain hours is available
    to an individual with characteristics X. Key features:
    
    1. **Hours focal points**: Certain hours (20h, 30h, 40h) are more likely due to
       institutional constraints (part-time contracts, full-time norm)
       - working_pt1: 1{h ∈ [18.5, 21.5]} (20h part-time peak)
       - working_pt2: 1{h ∈ [29.5, 30.5]} (30h part-time peak)  
       - working_ft:  1{h ∈ [37.5, 40.5]} (40h full-time peak)
    
    2. **Group-specific unemployment rate (gsur)**: Higher unemployment → lower
       opportunity to find *any* job (negative β_gsur expected)
    
    3. **Education × working**: Higher education → better job market access
    
    4. **Region × working**: Regional labor market differences (France: drgn1)
    
    Structure (log opportunity density):
        log h(h|X) = β_work * 1{h>0}
                   + β_pt1 * 1{h≈20} + β_pt2 * 1{h≈30} + β_ft * 1{h≈40}
                   + β_gsur * gsur * 1{h>0}
                   + β_work_educL * educL * 1{h>0}
                   + β_work_educH * educH * 1{h>0}
    
    SIMPLIFIED: No region interactions (moved to wage equation or removed)
    """
    # Base working effect (intercept for h > 0)
    beta_work: float = 0.0
    
    # Hours focal points (peaks in the hours distribution)
    beta_pt1: float = 0.0   # ~20 hours (half-time)
    beta_pt2: float = 0.0   # ~30 hours (3/4 time)
    beta_ft: float = 0.0    # ~40 hours (full-time)
    
    # Group-specific unemployment rate interaction
    beta_gsur: float = 0.0  # expect negative: higher gsur → fewer opportunities
    
    # Education interactions with working
    beta_work_educL: float = 0.0  # low education × working
    beta_work_educH: float = 0.0  # high education × working


@dataclass
class WageOppParams:
    """
    Wage opportunity density parameters
    
    SIMPLIFIED SPECIFICATION:
    - No region effects (unidentified with single year/region)
    - No year dummies (single year)
    
    Log-wage equation (Mincer-style):
        E[log(w)] = β0 + β_educL*educL + β_educH*educH
                      + β_pexp*pexp + β_pexp2*pexp²
    
    Log-normal pdf (log of density):
        For w > 0:
        log f(w | X) = -0.5 * ((log(w) - μ(X)) / σ)² - log(σ) - log(w) - 0.5*log(2π)
        
        For h = 0 (not working):
        log f(w | X) = 0  (wage is structurally 0, no density contribution)
    """
    # Intercept (baseline log wage for someone with educM, no experience)
    beta0: float = 2.5        # log hourly wage ≈ exp(2.5) ≈ 12€/h
    
    # Education effects on log wage
    beta_educL: float = -0.1  # low education penalty (negative)
    beta_educH: float = 0.2   # high education premium (positive)
    
    # Experience effects (Mincer equation: concave in experience)
    beta_pexp: float = 0.02   # linear experience term
    beta_pexp2: float = -0.001  # quadratic experience term (negative for concavity)
    
    # Standard deviation of log-wage residual (bounds: 0.1-20.0)
    sigma: float = 0.4        # σ > 0; typical values 0.3-0.5


# =============================================================================
# Parameter packing/unpacking
# =============================================================================

def pack_theta_singles(
    pref: PrefParamsSingles,
    hopp: HoursOppParams,
    wopp: WageOppParams,
) -> np.ndarray:
    """
    Pack parameter dataclasses into a flat numpy array for optimization.
    
    SIMPLIFIED PARAMETER STRUCTURE:
    
    PREFERENCES (9 params):
      [0]  beta_l0          - leisure intercept
      [1]  beta_l_age_norm  - demeaned age effect on leisure
      [2]  beta_l_age_norm2 - demeaned age² effect
      [3]  beta_l_n_children- total children effect
      [4]  beta_l_educL     - low education effect
      [5]  beta_l_educH     - high education effect
      [6]  beta_c           - consumption coefficient (bounds: -15, 15)
      [7]  theta_l          - Box-Cox exponent for leisure (bounds: 0.1-3.0)
      [8]  theta_c          - Box-Cox exponent for consumption (bounds: 0.1-3.0)
    
    HOURS OPPORTUNITY (7 params):
      [9]  beta_work        - working indicator (bounds: -15, 15)
      [10] beta_pt1         - 20h focal point (bounds: -15, 15)
      [11] beta_pt2         - 30h focal point (bounds: -15, 15)
      [12] beta_ft          - 40h focal point (bounds: -15, 15)
      [13] beta_gsur        - group-specific unemployment rate (bounds: -15, 15)
      [14] beta_work_educL  - low education × working (bounds: -15, 15)
      [15] beta_work_educH  - high education × working (bounds: -15, 15)

    WAGE OPPORTUNITY (6 params, used only for wage_spec="vw"):
      [16] beta0            - log-wage intercept
      [17] beta_educL       - low education wage penalty
      [18] beta_educH       - high education wage premium
      [19] beta_pexp        - experience (linear)
      [20] beta_pexp2       - experience (quadratic)
      [21] sigma            - std dev of log-wage (bounds: 0.1-20.0)
    
    TOTAL: 16 params for fw, 22 params for vw
    """
    theta = np.array([
        # Preference parameters (9)
        pref.beta_l0,           # 0
        pref.beta_l_age_norm,   # 1
        pref.beta_l_age_norm2,  # 2
        pref.beta_l_n_children, # 3
        pref.beta_l_educL,      # 4
        pref.beta_l_educH,      # 5
        pref.beta_c,            # 6
        pref.theta_l,           # 7
        pref.theta_c,           # 8
        # Hours opportunity parameters (7)
        hopp.beta_work,         # 9
        hopp.beta_pt1,          # 10
        hopp.beta_pt2,          # 11
        hopp.beta_ft,           # 12
        hopp.beta_gsur,         # 13
        hopp.beta_work_educL,   # 14
        hopp.beta_work_educH,   # 15
        # Wage opportunity parameters (6) - used only for vw
        wopp.beta0,             # 16
        wopp.beta_educL,        # 17
        wopp.beta_educH,        # 18
        wopp.beta_pexp,         # 19
        wopp.beta_pexp2,        # 20
        wopp.sigma,             # 21
    ])
    return theta


def unpack_theta_singles(theta: np.ndarray, wage_spec: str = "vw") -> Tuple[PrefParamsSingles, HoursOppParams, WageOppParams]:
    """
    Unpack flat parameter array into dataclasses.
    
    Parameters
    ----------
    theta : np.ndarray
        Parameter vector. Length 16 for fw (pref+hopp), 22 for vw (pref+hopp+wopp).
    wage_spec : str
        "fw" (fixed wages, 16 params) or "vw" (variable wages, 22 params)
    
    Returns
    -------
    pref, hopp, wopp : tuple of dataclasses
        For fw mode, wopp will have default values (not used).
    """
    pref = PrefParamsSingles(
        beta_l0=theta[0],
        beta_l_age_norm=theta[1],
        beta_l_age_norm2=theta[2],
        beta_l_n_children=theta[3],
        beta_l_educL=theta[4],
        beta_l_educH=theta[5],
        beta_c=theta[6],
        theta_l=theta[7],
        theta_c=theta[8],
    )
    hopp = HoursOppParams(
        beta_work=theta[9],
        beta_pt1=theta[10],
        beta_pt2=theta[11],
        beta_ft=theta[12],
        beta_gsur=theta[13],
        beta_work_educL=theta[14],
        beta_work_educH=theta[15],
    )
    
    # For fw mode, wage opp params are not used - return defaults
    if wage_spec == "fw" or len(theta) <= 16:
        wopp = WageOppParams()
    else:
        wopp = WageOppParams(
            beta0=theta[16],
            beta_educL=theta[17],
            beta_educH=theta[18],
            beta_pexp=theta[19],
            beta_pexp2=theta[20],
            sigma=theta[21],
        )
    return pref, hopp, wopp


def get_initial_theta_singles(is_male: bool = True) -> np.ndarray:
    """
    Get reasonable initial parameter values for singles estimation.
    """
    pref = PrefParamsSingles(
        beta_l0=1.0,
        beta_l_age_norm=0.0,
        beta_l_age_norm2=0.0,
        beta_l_n_children=0.0 if is_male else 0.1,
        beta_l_educL=0.0,
        beta_l_educH=0.0,
        beta_c=1.0,
        theta_l=0.5,
        theta_c=0.5,
    )
    hopp = HoursOppParams(
        beta_work=0.5,
        beta_pt1=0.0,
        beta_pt2=0.0,
        beta_ft=0.0,
        beta_gsur=0.0,
        beta_work_educL=0.0,
        beta_work_educH=0.0,
    )
    wopp = WageOppParams(
        beta0=2.5,
        beta_educL=-0.1,
        beta_educH=0.2,
        beta_pexp=0.02,
        beta_pexp2=-0.001,
        sigma=0.4,
    )
    return pack_theta_singles(pref, hopp, wopp)


def get_param_names_singles() -> List[str]:
    """
    Return list of parameter names for singles, aligned with pack_theta_singles order.
    """
    return [
        # Preference parameters (9)
        "pref.beta_l0",           # 0
        "pref.beta_l_age_norm",   # 1
        "pref.beta_l_age_norm2",  # 2
        "pref.beta_l_n_children", # 3
        "pref.beta_l_educL",      # 4
        "pref.beta_l_educH",      # 5
        "pref.beta_c",            # 6
        "pref.theta_l",           # 7
        "pref.theta_c",           # 8
        # Hours opportunity parameters (7)
        "hopp.beta_work",         # 9
        "hopp.beta_pt1",          # 10
        "hopp.beta_pt2",          # 11
        "hopp.beta_ft",           # 12
        "hopp.beta_gsur",         # 13
        "hopp.beta_work_educL",   # 14
        "hopp.beta_work_educH",   # 15
        # Wage opportunity parameters (6)
        "wopp.beta0",             # 16
        "wopp.beta_educL",        # 17
        "wopp.beta_educH",        # 18
        "wopp.beta_pexp",         # 19
        "wopp.beta_pexp2",        # 20
        "wopp.sigma",             # 21
    ]


# =============================================================================
# Box-Cox transformation
# =============================================================================

def boxcox_transform(x: np.ndarray, theta: float) -> np.ndarray:
    """
    Box-Cox transformation: (x^θ - 1) / θ
    
    When θ → 0, this converges to log(x).
    We handle this case explicitly for numerical stability.
    """
    eps = 1e-6
    x = np.clip(x, eps, None)  # ensure positivity
    
    if abs(theta) < eps:
        return np.log(x)
    else:
        return (np.power(x, theta) - 1.0) / theta


def d_boxcox_dtheta(x: np.ndarray, theta: float) -> np.ndarray:
    """
    Derivative of Box-Cox transform w.r.t. theta (the exponent parameter).
    
    ∂BC/∂θ = (θ * x^θ * ln(x) - (x^θ - 1)) / θ²
    
    At θ → 0, this converges to 0.5 * ln(x)²
    
    This is needed for computing the gradient w.r.t. theta_l and theta_c.
    """
    eps = 1e-6
    x = np.clip(x, eps, None)
    ln_x = np.log(x)
    
    if abs(theta) < eps:
        return 0.5 * ln_x * ln_x
    
    x_theta = np.power(x, theta)
    num = theta * x_theta * ln_x - (x_theta - 1.0)
    den = theta * theta
    return num / den


def d_boxcox_dx(x: np.ndarray, theta: float) -> np.ndarray:
    """
    Derivative of Box-Cox transform w.r.t. its argument x.
    
    ∂BC/∂x = x^(θ-1)
    
    At θ → 0, this is 1/x
    
    This is the marginal utility scaling factor.
    """
    eps = 1e-6
    x = np.clip(x, eps, None)
    
    if abs(theta) < eps:
        return 1.0 / x
    return np.power(x, theta - 1.0)


# =============================================================================
# Numba-accelerated core functions (when available)
# =============================================================================

if NUMBA_AVAILABLE:
    @njit(cache=True, fastmath=True)
    def _boxcox_transform_numba(x: np.ndarray, theta: float) -> np.ndarray:
        """Numba-accelerated Box-Cox transformation."""
        eps = 1e-6
        n = len(x)
        result = np.empty(n, dtype=np.float64)
        
        if abs(theta) < eps:
            for i in range(n):
                xi = max(x[i], eps)
                result[i] = np.log(xi)
        else:
            for i in range(n):
                xi = max(x[i], eps)
                result[i] = (xi ** theta - 1.0) / theta
        return result
    
    @njit(cache=True, fastmath=True)
    def _d_boxcox_dtheta_numba(x: np.ndarray, theta: float) -> np.ndarray:
        """Numba-accelerated derivative of Box-Cox w.r.t. theta."""
        eps = 1e-6
        n = len(x)
        result = np.empty(n, dtype=np.float64)
        
        if abs(theta) < eps:
            for i in range(n):
                xi = max(x[i], eps)
                ln_xi = np.log(xi)
                result[i] = 0.5 * ln_xi * ln_xi
        else:
            for i in range(n):
                xi = max(x[i], eps)
                ln_xi = np.log(xi)
                x_theta = xi ** theta
                result[i] = (theta * x_theta * ln_xi - (x_theta - 1.0)) / (theta * theta)
        return result
    
    @njit(cache=True, fastmath=True)
    def _compute_softmax_gradient_numba(
        V: np.ndarray,
        dV_dtheta: np.ndarray,
        group_starts: np.ndarray,
        group_ends: np.ndarray,
        obs_indices: np.ndarray,
    ) -> np.ndarray:
        """
        Numba-accelerated softmax gradient computation.
        
        Computes: ∂LL/∂θ = Σ_i [∂V_i*/∂θ - Σ_j P_ij * ∂V_ij/∂θ]
        
        NOTE: This is slower than the vectorized NumPy version for the gradient
        because NumPy's matrix operations are highly optimized. We keep this
        for reference but recommend using the NumPy version for gradients.
        """
        n_groups = len(group_starts)
        n_params = dV_dtheta.shape[1]
        grad = np.zeros(n_params, dtype=np.float64)
        
        for g in range(n_groups):
            s = group_starts[g]
            e = group_ends[g]
            n_alts = e - s
            obs_idx = obs_indices[g]
            
            # Find max V
            V_max = V[s]
            for j in range(s + 1, e):
                if V[j] > V_max:
                    V_max = V[j]
            
            # Compute probabilities (store them to avoid recomputing)
            probs = np.empty(n_alts, dtype=np.float64)
            sum_exp = 0.0
            for j in range(n_alts):
                probs[j] = np.exp(V[s + j] - V_max)
                sum_exp += probs[j]
            for j in range(n_alts):
                probs[j] /= sum_exp
            
            # Compute gradient: dV_obs - P @ dV
            # Loop order optimized for cache: j (rows), then k (cols)
            for j in range(n_alts):
                P_j = probs[j]
                for k in range(n_params):
                    grad[k] -= P_j * dV_dtheta[s + j, k]
            
            # Add observed contribution
            for k in range(n_params):
                grad[k] += dV_dtheta[obs_idx, k]
        
        return grad
    
    @njit(cache=True, fastmath=True)
    def _compute_log_likelihood_numba(
        V: np.ndarray,
        group_starts: np.ndarray,
        group_ends: np.ndarray,
        obs_indices: np.ndarray,
    ) -> float:
        """
        Numba-accelerated log-likelihood computation.
        
        LL = Σ_i log(P_i*) = Σ_i [V_i* - log(Σ_j exp(V_ij))]
        """
        n_groups = len(group_starts)
        ll = 0.0
        
        for g in range(n_groups):
            s = group_starts[g]
            e = group_ends[g]
            obs_idx = obs_indices[g]
            
            # Find max V in group
            V_max = V[s]
            for j in range(s, e):
                if V[j] > V_max:
                    V_max = V[j]
            
            # Log-sum-exp
            sum_exp = 0.0
            for j in range(s, e):
                sum_exp += np.exp(V[j] - V_max)
            
            log_sum_exp = V_max + np.log(sum_exp)
            ll += V[obs_idx] - log_sum_exp
        
        return ll

else:
    # Fallback implementations when numba is not available
    _boxcox_transform_numba = None
    _d_boxcox_dtheta_numba = None
    _compute_softmax_gradient_numba = None
    _compute_log_likelihood_numba = None


# =============================================================================
# Utility function: ff_calc_util
# =============================================================================

def ff_calc_util_singles(
    df: pd.DataFrame,
    pref: PrefParamsSingles,
    is_male: bool = True,
) -> np.ndarray:
    """
    Compute systematic utility u_ij for each alternative j of each single individual i.
    
    SIMPLIFIED SPECIFICATION:
       u = (β_l0 + β_l_age_norm*age_norm + β_l_age_norm2*age_norm²
             + β_l_n_children*n_children
             + β_l_educL*educL + β_l_educH*educH)
            * (l^θ_l - 1)/θ_l
          + β_c * (c^θ_c - 1)/θ_c
    
    where age_norm = dag - mean(dag) (demeaned)
    
    Parameters
    ----------
    df : pd.DataFrame
        Long-format RURO-MNL dataset for singles.
    pref : PrefParamsSingles
        Preference parameters (simplified: 9 params).
    is_male : bool
        Gender indicator (unused in simplified spec, kept for API compatibility).
    
    Returns
    -------
    u : np.ndarray
        Utility values, shape (n_rows,).
    """
    n = len(df)
    
    # -------------------------------------------------------------------------
    # Normalized consumption and leisure
    # -------------------------------------------------------------------------
    c = None
    if "c_norm" in df.columns and not df["c_norm"].isna().all():
        c = df["c_norm"].to_numpy()
    if c is None and "dispy_util" in df.columns and not df["dispy_util"].isna().all():
        c = df["dispy_util"].to_numpy()
    if c is None and "consumption" in df.columns and not df["consumption"].isna().all():
        c = df["consumption"].to_numpy() / MEAN_DISPY_NORM
    if c is None and "ils_dispy" in df.columns and not df["ils_dispy"].isna().all():
        c = df["ils_dispy"].to_numpy() / MEAN_DISPY_NORM
    if c is None:
        LOGGER.warning("No valid consumption column found; using 1.0 as placeholder.")
        c = np.ones(n)
    
    l = None
    if "l_norm" in df.columns and not df["l_norm"].isna().all():
        l = df["l_norm"].to_numpy()
    if l is None and "leis_util" in df.columns and not df["leis_util"].isna().all():
        l = df["leis_util"].to_numpy()
    if l is None and "leisure" in df.columns and not df["leisure"].isna().all():
        l = df["leisure"].to_numpy() / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    if l is None and "hours" in df.columns:
        hours = df["hours"].to_numpy()
        l = (TOTAL_LEISURE_HOURS - hours) / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    if l is None:
        LOGGER.warning("No valid leisure column found; using 1.0 as placeholder.")
        l = np.ones(n)
    
    # Clip to avoid numerical issues
    c = np.clip(c, 1e-6, None)
    l = np.clip(l, 1e-6, None)
    
    # -------------------------------------------------------------------------
    # Covariates for leisure term (simplified)
    # -------------------------------------------------------------------------
    age_norm = _get_col(df, "age_norm", 0.0)
    age_norm2 = _get_col(df, "age_norm2", 0.0)
    if age_norm2.sum() == 0:
        age_norm2 = age_norm ** 2
    
    n_children = _get_col(df, "n_children", 0.0)
    educL = _get_col(df, "educL", 0.0)
    educH = _get_col(df, "educH", 0.0)
    
    # -------------------------------------------------------------------------
    # Build leisure coefficient (simplified: no region, single children var)
    # -------------------------------------------------------------------------
    beta_leisure = (
        pref.beta_l0
        + pref.beta_l_age_norm * age_norm
        + pref.beta_l_age_norm2 * age_norm2
        + pref.beta_l_n_children * n_children
        + pref.beta_l_educL * educL
        + pref.beta_l_educH * educH
    )
    
    # -------------------------------------------------------------------------
    # Box-Cox transforms
    # -------------------------------------------------------------------------
    l_bc = boxcox_transform(l, pref.theta_l)
    c_bc = boxcox_transform(c, pref.theta_c)
    
    # -------------------------------------------------------------------------
    # Utility
    # -------------------------------------------------------------------------
    u = beta_leisure * l_bc + pref.beta_c * c_bc
    
    return u


def ff_calc_util_couples(
    df: pd.DataFrame,
    pref: PrefParamsCouples,
) -> np.ndarray:
    """
    Compute systematic utility u_ij for each alternative j of each couple.

    SIMPLIFIED SPECIFICATION:
        u = (β_lm0 + β_lm_age_norm*age_norm_m + β_lm_age_norm2*age_norm²_m
             + β_lm_n_children*n_children
             + β_lm_educL*educL_m + β_lm_educH*educH_m)
            * (l_m^θ_lm - 1)/θ_lm
          + (β_lf0 + ... female terms ...)
            * (l_f^θ_lf - 1)/θ_lf
          + β_c * ((c_m + c_f)^θ_c - 1)/θ_c
    
    The dataset should have _m and _f suffixes for male and female partner variables.
    
    Parameters
    ----------
    df : pd.DataFrame
        Long-format RURO-MNL dataset for couples. Must have columns with _m and _f
        suffixes for male and female partner characteristics.
    pref : PrefParamsCouples
        Couples preference parameters (simplified: 16 params).
    
    Returns
    -------
    u : np.ndarray
        Utility values, shape (n_rows,).
    """
    n = len(df)
    
    # -------------------------------------------------------------------------
    # Normalized consumption and leisure for both partners
    # -------------------------------------------------------------------------
    # Male partner leisure
    if "leis_util_m" in df.columns:
        l_m = df["leis_util_m"].to_numpy()
    elif "l_norm_m" in df.columns:
        l_m = df["l_norm_m"].to_numpy()
    elif "hours_m" in df.columns:
        hours_m = pd.to_numeric(df["hours_m"], errors="coerce").fillna(0).to_numpy()
        l_m = (TOTAL_LEISURE_HOURS - hours_m) / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    else:
        l_m = np.ones(n)
    
    # Female partner leisure
    if "leis_util_f" in df.columns:
        l_f = df["leis_util_f"].to_numpy()
    elif "l_norm_f" in df.columns:
        l_f = df["l_norm_f"].to_numpy()
    elif "hours_f" in df.columns:
        hours_f = pd.to_numeric(df["hours_f"], errors="coerce").fillna(0).to_numpy()
        l_f = (TOTAL_LEISURE_HOURS - hours_f) / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    else:
        l_f = np.ones(n)
    
    # Joint household consumption (sum of individual consumption)
    if "dispy_util_m" in df.columns and "dispy_util_f" in df.columns:
        c_m = df["dispy_util_m"].to_numpy()
        c_f = df["dispy_util_f"].to_numpy()
        c_total = c_m + c_f
    elif "c_norm" in df.columns:
        c_total = df["c_norm"].to_numpy()
    elif "consumption" in df.columns:
        c_total = df["consumption"].to_numpy() / MEAN_DISPY_NORM
    else:
        c_total = np.ones(n)
    
    # Clip for numerical stability
    l_m = np.clip(l_m, 1e-6, None)
    l_f = np.clip(l_f, 1e-6, None)
    c_total = np.clip(c_total, 1e-6, None)
    
    # -------------------------------------------------------------------------
    # Covariates for male partner (simplified: demeaned age)
    # -------------------------------------------------------------------------
    age_norm_m = _get_col(df, "age_norm_m", 0.0)
    age_norm2_m = _get_col(df, "age_norm2_m", 0.0)
    if age_norm2_m.sum() == 0:
        age_norm2_m = age_norm_m ** 2
    
    educL_m = _get_col(df, "educL_m", 0.0)
    educH_m = _get_col(df, "educH_m", 0.0)
    
    # -------------------------------------------------------------------------
    # Covariates for female partner (simplified: demeaned age)
    # -------------------------------------------------------------------------
    age_norm_f = _get_col(df, "age_norm_f", 0.0)
    age_norm2_f = _get_col(df, "age_norm2_f", 0.0)
    if age_norm2_f.sum() == 0:
        age_norm2_f = age_norm_f ** 2
    
    educL_f = _get_col(df, "educL_f", 0.0)
    educH_f = _get_col(df, "educH_f", 0.0)
    
    # -------------------------------------------------------------------------
    # Household-level covariates (single n_children variable)
    # -------------------------------------------------------------------------
    n_children = _get_col(df, "n_children", 0.0)
    
    # -------------------------------------------------------------------------
    # Build male leisure coefficient (simplified)
    # -------------------------------------------------------------------------
    beta_leisure_m = (
        pref.beta_lm0
        + pref.beta_lm_age_norm * age_norm_m
        + pref.beta_lm_age_norm2 * age_norm2_m
        + pref.beta_lm_n_children * n_children
        + pref.beta_lm_educL * educL_m
        + pref.beta_lm_educH * educH_m
    )
    
    # -------------------------------------------------------------------------
    # Build female leisure coefficient (simplified)
    # -------------------------------------------------------------------------
    beta_leisure_f = (
        pref.beta_lf0
        + pref.beta_lf_age_norm * age_norm_f
        + pref.beta_lf_age_norm2 * age_norm2_f
        + pref.beta_lf_n_children * n_children
        + pref.beta_lf_educL * educL_f
        + pref.beta_lf_educH * educH_f
    )
    
    # -------------------------------------------------------------------------
    # Box-Cox transforms
    # -------------------------------------------------------------------------
    l_m_bc = boxcox_transform(l_m, pref.theta_lm)
    l_f_bc = boxcox_transform(l_f, pref.theta_lf)
    c_bc = boxcox_transform(c_total, pref.theta_c)
      # -------------------------------------------------------------------------
    # Utility: male leisure + female leisure + consumption (no interaction)
    # -------------------------------------------------------------------------
    u = (
        beta_leisure_m * l_m_bc          # Male leisure utility
        + beta_leisure_f * l_f_bc        # Female leisure utility
        + pref.beta_c * c_bc             # Joint consumption utility
    )
    
    return u


# =============================================================================
# Hours opportunity density: ff_calc_hopp
# =============================================================================

def ff_calc_hopp(
    df: pd.DataFrame,
    hopp: HoursOppParams,
    is_male: bool = True,
) -> np.ndarray:
    """
    Compute log hours-opportunity density h(h | X) (up to additive constant).
    
    This is the **true opportunity density** for being offered a job with given hours,
    conditional on individual characteristics X. This is NOT the proposal/prior density.
    
    The hours opportunity captures:
    1. **Employment probability**: Higher-educated individuals have better job access
    2. **Hours focal points**: Institutional peaks at 20h, 30h, 40h (contracts)
    3. **Regional labor markets**: Different regions have different employment rates
    4. **Cyclical conditions**: Group-specific unemployment rate (gsur)

    The structure (log density):
        log h(h|X) = β_work * 1{h>0}
                   + β_pt1 * 1{h ∈ [18.5, 21.5]}   (20h peak)
                   + β_pt2 * 1{h ∈ [29.5, 30.5]}   (30h peak)
                   + β_ft  * 1{h ∈ [37.5, 40.5]}   (40h peak)
                   + β_gsur * gsur * 1{h>0}
                   + β_work_educL * educL * 1{h>0}
                   + β_work_educH * educH * 1{h>0}
                   + β_work_reg2 * region2 * 1{h>0}
                   + β_work_reg3 * region3 * 1{h>0}
    
    Parameters
    ----------
    df : pd.DataFrame
        Long-format RURO-MNL dataset.
    hopp : HoursOppParams
        Hours opportunity parameters.
    is_male : bool
        Gender indicator (for potential gender-specific parameters).
    
    Returns
    -------
    h_opp : np.ndarray
        Log hours opportunity density, shape (n_rows,).
    """
    n = len(df)
    
    # -------------------------------------------------------------------------
    # Working indicators and focal points
    # -------------------------------------------------------------------------
    working = _get_col(df, "working", 0.0)
    working_pt1 = _get_col(df, "working_pt1", 0.0)
    working_pt2 = _get_col(df, "working_pt2", 0.0)
    working_ft = _get_col(df, "working_ft", 0.0)
    
    # If working indicators not present, derive from hours
    if "working" not in df.columns and "hours" in df.columns:
        hours = pd.to_numeric(df["hours"], errors="coerce").fillna(0).to_numpy()
        working = (hours > 0).astype(float)
        # Focal points: allow some slack around the peak values
        working_pt1 = ((hours >= 18.5) & (hours <= 21.5)).astype(float)  # ~20h
        working_pt2 = ((hours >= 29.5) & (hours <= 30.5)).astype(float)  # ~30h
        working_ft = ((hours >= 37.5) & (hours <= 40.5)).astype(float)   # ~40h
    
    # -------------------------------------------------------------------------
    # Group-specific unemployment rate (gsur)
    # -------------------------------------------------------------------------
    # This captures cyclical conditions for the individual's demographic group
    # Higher gsur → fewer opportunities (expect negative coefficient)
    gsur = _get_col(df, "gsur", 0.0)
      # -------------------------------------------------------------------------
    # Education dummies
    # -------------------------------------------------------------------------
    educL = _get_col(df, "educL", 0.0)
    educH = _get_col(df, "educH", 0.0)
    
    # -------------------------------------------------------------------------
    # Hours opportunity density (log)
    # SIMPLIFIED: No region interactions (removed for identification)
    # -------------------------------------------------------------------------
    h_opp = (
        hopp.beta_work * working
        + hopp.beta_pt1 * working_pt1
        + hopp.beta_pt2 * working_pt2
        + hopp.beta_ft * working_ft
        + hopp.beta_gsur * working * gsur
        + hopp.beta_work_educL * working * educL
        + hopp.beta_work_educH * working * educH
    )
    
    return h_opp


# =============================================================================
# Wage opportunity density: ff_calc_wopp
# =============================================================================

def ff_calc_wopp(
    df: pd.DataFrame,
    wopp: WageOppParams,
    is_male: bool = True,
) -> np.ndarray:
    """
    Compute log wage-opportunity density w(w | h, X) for working individuals.
    
    This is the **true opportunity density** for being offered a wage w, conditional
    on working (h > 0) and individual characteristics X. This is NOT the proposal density.
    
    Wages are modeled as **log-normal**:
        log(w) | X ~ N(μ(X), σ²)
    
    where the mean μ(X) follows a Mincer-style equation:
        μ(X) = β0 + β_educL*educL + β_educH*educH
                 + β_pexp*exp + β_pexp2*exp²
                 + β_reg2*region2
                 + β_yd1*year1 + β_yd2*year2
    
    The log-pdf of a log-normal distribution for w is:
        log f(w|X) = -0.5 * ((log w - μ(X)) / σ)² - log(σ) - log(w) - 0.5*log(2π)
    
    The -log(w) term is the **Jacobian** from the change of variables log(w) → w.
    The constant -0.5*log(2π) cancels in the likelihood ratio and is omitted.
    
    For non-working alternatives (h = 0), we set w_opp = 0 because wage is
    structurally zero and there's no wage density contribution.

    Parameters
    ----------
    df : pd.DataFrame
        Long-format RURO-MNL dataset.
    wopp : WageOppParams
        Wage opportunity parameters.
    is_male : bool
        Gender indicator (wage equation may differ by gender).
    
    Returns
    -------
    w_opp : np.ndarray
        Log wage opportunity density, shape (n_rows,).
    """
    n = len(df)
    
    # -------------------------------------------------------------------------
    # Working indicator
    # -------------------------------------------------------------------------
    working = _get_col(df, "working", 0.0)
    if working.sum() == 0 and "hours" in df.columns:
        hours = pd.to_numeric(df["hours"], errors="coerce").fillna(0).to_numpy()
        working = (hours > 0).astype(float)
    
    # -------------------------------------------------------------------------
    # Wage (hourly wage rate)
    # -------------------------------------------------------------------------
    if "wage" in df.columns:
        wage = pd.to_numeric(df["wage"], errors="coerce").fillna(1).to_numpy()
    elif "yivwg" in df.columns:
        wage = pd.to_numeric(df["yivwg"], errors="coerce").fillna(1).to_numpy()
    else:
        wage = np.ones(n)
    wage = np.clip(wage, 1e-6, None)  # avoid log(0)
    log_wage = np.log(wage)
    
    # -------------------------------------------------------------------------
    # Education dummies
    # -------------------------------------------------------------------------
    educL = _get_col(df, "educL", 0.0)
    educH = _get_col(df, "educH", 0.0)
      # -------------------------------------------------------------------------
    # Potential experience (Mincer equation)
    # -------------------------------------------------------------------------
    if "pexp" in df.columns:
        pexp = pd.to_numeric(df["pexp"], errors="coerce").fillna(0).to_numpy()
    elif "pexp_years" in df.columns:
        pexp = pd.to_numeric(df["pexp_years"], errors="coerce").fillna(0).to_numpy() / 100.0
    else:
        # Estimate from age - years of schooling - 6
        pexp = np.zeros(n)
    
    # -------------------------------------------------------------------------
    # Expected log-wage (Mincer equation - simplified)
    # SIMPLIFIED: No region effects, no year dummies (removed for identification)
    # -------------------------------------------------------------------------
    mean_logw = (
        wopp.beta0
        + wopp.beta_educL * educL
        + wopp.beta_educH * educH
        + wopp.beta_pexp * pexp
        + wopp.beta_pexp2 * (pexp ** 2)
    )
    
    # -------------------------------------------------------------------------
    # Log-normal pdf (log of density)
    # -------------------------------------------------------------------------
    sigma = np.abs(wopp.sigma) + 1e-6  # enforce positivity
    z = (log_wage - mean_logw) / sigma
    
    # log f(w|X) = -0.5*z² - log(σ) - log(w)
    # We omit -0.5*log(2π) as it cancels in the likelihood ratio
    w_opp = -0.5 * z**2 - np.log(sigma) - log_wage
    
    # For non-working alternatives (h=0), wage is structurally 0 → no density contribution
    w_opp = np.where(working > 0, w_opp, 0.0)
    
    return w_opp


# =============================================================================
# Couples opportunity densities
# =============================================================================

def ff_calc_hopp_couples(
    df: pd.DataFrame,
    hopp_m: HoursOppParams,
    hopp_f: HoursOppParams,
) -> np.ndarray:
    """
    Compute log hours-opportunity density for couples (both partners).
    
    For couples, the opportunity density is the sum of male and female components:
        log h(h_m, h_f | X) = log h_m(h_m | X_m) + log h_f(h_f | X_f)
        hopp = (hopp_male_terms using working_m, educL_m, gsur_m, etc.)
             + (hopp_female_terms using working_f, educL_f, gsur_f, etc.)
    
    Parameters
    ----------
    df : pd.DataFrame
        Couples dataset with _m and _f suffixed columns.
    hopp_m : HoursOppParams
        Male hours opportunity parameters.
    hopp_f : HoursOppParams
        Female hours opportunity parameters.
    
    Returns
    -------
    h_opp : np.ndarray
        Log hours opportunity density (sum of male and female), shape (n_rows,).
    """
    n = len(df)
    
    # -------------------------------------------------------------------------
    # Male partner working indicators
    # -------------------------------------------------------------------------
    working_m = _get_col(df, "working_m", 0.0)
    working_pt1_m = _get_col(df, "working_pt1_m", 0.0)
    working_pt2_m = _get_col(df, "working_pt2_m", 0.0)
    working_ft_m = _get_col(df, "working_ft_m", 0.0)
    
    # If not present, derive from hours_m
    if "working_m" not in df.columns and "hours_m" in df.columns:
        hours_m = pd.to_numeric(df["hours_m"], errors="coerce").fillna(0).to_numpy()
        working_m = (hours_m > 0).astype(float)
        working_pt1_m = ((hours_m >= 18.5) & (hours_m <= 21.5)).astype(float)
        working_pt2_m = ((hours_m >= 29.5) & (hours_m <= 30.5)).astype(float)
        working_ft_m = ((hours_m >= 37.5) & (hours_m <= 40.5)).astype(float)
    
    gsur_m = _get_col(df, "gsur_m", 0.0)
    if gsur_m.sum() == 0:
        gsur_m = _get_col(df, "gsur", 0.0)  # Fallback to household gsur
    educL_m = _get_col(df, "educL_m", 0.0)
    educH_m = _get_col(df, "educH_m", 0.0)
    
    # -------------------------------------------------------------------------
    # Female partner working indicators
    # -------------------------------------------------------------------------
    working_f = _get_col(df, "working_f", 0.0)
    working_pt1_f = _get_col(df, "working_pt1_f", 0.0)
    working_pt2_f = _get_col(df, "working_pt2_f", 0.0)
    working_ft_f = _get_col(df, "working_ft_f", 0.0)
    
    if "working_f" not in df.columns and "hours_f" in df.columns:
        hours_f = pd.to_numeric(df["hours_f"], errors="coerce").fillna(0).to_numpy()
        working_f = (hours_f > 0).astype(float)
        working_pt1_f = ((hours_f >= 18.5) & (hours_f <= 21.5)).astype(float)
        working_pt2_f = ((hours_f >= 29.5) & (hours_f <= 30.5)).astype(float)
        working_ft_f = ((hours_f >= 37.5) & (hours_f <= 40.5)).astype(float)
    
    gsur_f = _get_col(df, "gsur_f", 0.0)
    if gsur_f.sum() == 0:
        gsur_f = _get_col(df, "gsur", 0.0)
    educL_f = _get_col(df, "educL_f", 0.0)
    educH_f = _get_col(df, "educH_f", 0.0)
    
    # -------------------------------------------------------------------------
    # Hours opportunity: sum of male and female components
    # SIMPLIFIED: No region interactions (removed for identification)
    # -------------------------------------------------------------------------
    h_opp_m = (
        hopp_m.beta_work * working_m
        + hopp_m.beta_pt1 * working_pt1_m
        + hopp_m.beta_pt2 * working_pt2_m
        + hopp_m.beta_ft * working_ft_m
        + hopp_m.beta_gsur * working_m * gsur_m
        + hopp_m.beta_work_educL * working_m * educL_m
        + hopp_m.beta_work_educH * working_m * educH_m
    )
    
    h_opp_f = (
        hopp_f.beta_work * working_f
        + hopp_f.beta_pt1 * working_pt1_f
        + hopp_f.beta_pt2 * working_pt2_f
        + hopp_f.beta_ft * working_ft_f
        + hopp_f.beta_gsur * working_f * gsur_f
        + hopp_f.beta_work_educL * working_f * educL_f
        + hopp_f.beta_work_educH * working_f * educH_f
    )
    
    return h_opp_m + h_opp_f


def ff_calc_wopp_couples(
    df: pd.DataFrame,
    wopp_m: WageOppParams,
    wopp_f: WageOppParams,
) -> np.ndarray:
    """
    Compute log wage-opportunity density for couples (both partners).
    
    For couples, the wage opportunity is the sum of male and female log-normal densities:
        log w(w_m, w_f | X) = log w_m(w_m | X_m) + log w_f(w_f | X_f)
    
    Each partner's wage follows a log-normal distribution with gender-specific parameters.
    
    Parameters
    ----------
    df : pd.DataFrame
        Couples dataset with _m and _f suffixed columns.
    wopp_m : WageOppParams
        Male wage opportunity parameters.
    wopp_f : WageOppParams
        Female wage opportunity parameters.
    
    Returns
    -------
    w_opp : np.ndarray
        Log wage opportunity density (sum of male and female), shape (n_rows,).
    """
    n = len(df)
    
    # -------------------------------------------------------------------------
    # Male partner wage equation
    # -------------------------------------------------------------------------
    working_m = _get_col(df, "working_m", 0.0)
    if "working_m" not in df.columns and "hours_m" in df.columns:
        hours_m = pd.to_numeric(df["hours_m"], errors="coerce").fillna(0).to_numpy()
        working_m = (hours_m > 0).astype(float)
    
    if "wage_m" in df.columns:
        wage_m = pd.to_numeric(df["wage_m"], errors="coerce").fillna(1).to_numpy()
    elif "yivwg_m" in df.columns:
        wage_m = pd.to_numeric(df["yivwg_m"], errors="coerce").fillna(1).to_numpy()
    else:
        wage_m = np.ones(n)
    wage_m = np.clip(wage_m, 1e-6, None)
    log_wage_m = np.log(wage_m)
    
    educL_m = _get_col(df, "educL_m", 0.0)
    educH_m = _get_col(df, "educH_m", 0.0)
    pexp_m = _get_col(df, "pexp_m", 0.0)
    
    # -------------------------------------------------------------------------
    # Female partner wage equation
    # -------------------------------------------------------------------------
    working_f = _get_col(df, "working_f", 0.0)
    if "working_f" not in df.columns and "hours_f" in df.columns:
        hours_f = pd.to_numeric(df["hours_f"], errors="coerce").fillna(0).to_numpy()
        working_f = (hours_f > 0).astype(float)
    
    if "wage_f" in df.columns:
        wage_f = pd.to_numeric(df["wage_f"], errors="coerce").fillna(1).to_numpy()
    elif "yivwg_f" in df.columns:
        wage_f = pd.to_numeric(df["yivwg_f"], errors="coerce").fillna(1).to_numpy()
    else:
        wage_f = np.ones(n)
    wage_f = np.clip(wage_f, 1e-6, None)
    log_wage_f = np.log(wage_f)
    
    educL_f = _get_col(df, "educL_f", 0.0)
    educH_f = _get_col(df, "educH_f", 0.0)
    pexp_f = _get_col(df, "pexp_f", 0.0)
    
    # -------------------------------------------------------------------------
    # Mean log-wage for male (Mincer equation - simplified)
    # SIMPLIFIED: No region effects, no year dummies
    # -------------------------------------------------------------------------
    mean_logw_m = (
        wopp_m.beta0
        + wopp_m.beta_educL * educL_m
        + wopp_m.beta_educH * educH_m
        + wopp_m.beta_pexp * pexp_m
        + wopp_m.beta_pexp2 * (pexp_m ** 2)
    )
    
    sigma_m = np.abs(wopp_m.sigma) + 1e-6
    z_m = (log_wage_m - mean_logw_m) / sigma_m
    w_opp_m = -0.5 * z_m**2 - np.log(sigma_m) - log_wage_m
    w_opp_m = np.where(working_m > 0, w_opp_m, 0.0)
    
    # -------------------------------------------------------------------------
    # Mean log-wage for female (Mincer equation - simplified)
    # -------------------------------------------------------------------------
    mean_logw_f = (
        wopp_f.beta0
        + wopp_f.beta_educL * educL_f
        + wopp_f.beta_educH * educH_f
        + wopp_f.beta_pexp * pexp_f
        + wopp_f.beta_pexp2 * (pexp_f ** 2)
    )
    
    sigma_f = np.abs(wopp_f.sigma) + 1e-6
    z_f = (log_wage_f - mean_logw_f) / sigma_f
    w_opp_f = -0.5 * z_f**2 - np.log(sigma_f) - log_wage_f
    w_opp_f = np.where(working_f > 0, w_opp_f, 0.0)
    
    return w_opp_m + w_opp_f


# =============================================================================
# Log-likelihood function
# =============================================================================

def log_likelihood_singles(
    theta: np.ndarray,
    df: pd.DataFrame,
    is_male: bool = True,
    wage_spec: str = "fw",
) -> float:
    """
    Compute total log-likelihood for singles (single males or single females).
    
    Parameters
    ----------
    theta : np.ndarray
        Flat parameter vector.
    df : pd.DataFrame
        Long-format RURO-MNL dataset, filtered to singles.
    is_male : bool
        True for single males, False for single females.
    wage_spec : str
        "fw" for fixed wages (no wage density), "vw" for variable wages.
    
    Returns
    -------
    ll : float
        Total log-likelihood.
    """
    # Unpack parameters
    pref, hopp, wopp = unpack_theta_singles(theta, wage_spec=wage_spec)
    
    # Building blocks
    u = ff_calc_util_singles(df, pref, is_male=is_male)
    h_opp = ff_calc_hopp(df, hopp, is_male=is_male)
    
    if wage_spec == "vw":
        w_opp = ff_calc_wopp(df, wopp, is_male=is_male)
    else:
        w_opp = np.zeros(len(df))
      # Prior (already in log form in the dataset)
    prior_col = df.get("prior", None)
    if prior_col is not None:
        log_prior = pd.to_numeric(prior_col, errors="coerce").fillna(0).to_numpy()
    else:
        LOGGER.warning("No 'prior' column found; using 0 as placeholder.")
        log_prior = np.zeros(len(df))
    
    # Composite index: V = u + h_opp + w_opp - log_prior
    # (prior enters as subtraction because it's the proposal density)
    V = u + h_opp + w_opp - log_prior
    
    # -------------------------------------------------------------------------
    # Aggregate log-likelihood across decision units
    # -------------------------------------------------------------------------
    # Group by decision unit (idhh_true for singles, idhh for couples)
    
    if "idhh_true" in df.columns:
        ids = df["idhh_true"].to_numpy()
    elif "idhh" in df.columns:
        ids = df["idhh"].to_numpy()
    elif "idperson_true" in df.columns:
        ids = df["idperson_true"].to_numpy()
    elif "idperson" in df.columns:
        ids = df["idperson"].to_numpy()
    else:
        raise KeyError("Dataset must contain 'idhh_true', 'idhh', 'idperson_true', or 'idperson'.")
    
    draws = df["draw"].to_numpy()
    
    # Identify observed alternative: draw == 0
    # Also support is_chosen == 1 as fallback
    if "is_chosen" in df.columns:
        is_chosen = pd.to_numeric(df["is_chosen"], errors="coerce").fillna(0).to_numpy()
        is_obs = (is_chosen == 1) | (draws == 0)
    else:
        is_obs = (draws == 0)
    
    # -------------------------------------------------------------------------
    # Vectorized log-likelihood computation using pandas groupby
    # This is much faster than looping over individuals
    # -------------------------------------------------------------------------
    # Create a temporary DataFrame for groupby operations
    tmp = pd.DataFrame({
        "id": ids,
        "V": V,
        "is_obs": is_obs,
    })
    
    # For numerical stability, compute V - V_max within each group
    tmp["V_max"] = tmp.groupby("id")["V"].transform("max")
    tmp["exp_V_shifted"] = np.exp(tmp["V"] - tmp["V_max"])
    
    # Sum of exp(V - V_max) within each group (denominator in softmax)
    tmp["sum_exp_V"] = tmp.groupby("id")["exp_V_shifted"].transform("sum")
    
    # Log-sum-exp = V_max + log(sum(exp(V - V_max)))
    tmp["log_sum_exp"] = tmp["V_max"] + np.log(tmp["sum_exp_V"])
    
    # Log probability of observed choice: V_obs - log_sum_exp
    tmp["log_prob"] = tmp["V"] - tmp["log_sum_exp"]
    
    # Filter to observed alternatives and sum
    ll = tmp.loc[tmp["is_obs"], "log_prob"].sum()
    
    return ll


def neg_log_likelihood_singles(
    theta: np.ndarray,
    df: pd.DataFrame,
    is_male: bool = True,
    wage_spec: str = "fw",
) -> float:
    """
    Negative log-likelihood for minimization.
    """
    ll = log_likelihood_singles(theta, df, is_male=is_male, wage_spec=wage_spec)
    return -ll


# =============================================================================
# Gradient (numerical, for now)
# =============================================================================

def numerical_gradient(
    f,
    theta: np.ndarray,
    eps: float = 1e-6,
    **kwargs,
) -> np.ndarray:
    """
    Compute numerical gradient of f at theta using central differences.
    """
    grad = np.zeros_like(theta)
    for i in range(len(theta)):
        theta_plus = theta.copy()
        theta_plus[i] += eps
        theta_minus = theta.copy()
        theta_minus[i] -= eps
        grad[i] = (f(theta_plus, **kwargs) - f(theta_minus, **kwargs)) / (2 * eps)
    return grad


# =============================================================================
# Analytical gradient computation (vectorized)
# =============================================================================

def _compute_utility_derivatives_singles(
    df: pd.DataFrame,
    theta: np.ndarray,
    is_male: bool = True,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute utility values and their derivatives w.r.t. preference parameters.
    
    SIMPLIFIED SPECIFICATION (9 preference params):
    - Uses age_norm (demeaned age) instead of log(age)
    - Single n_children instead of separate age groups
    - No region effects
    
    Returns
    -------
    u : np.ndarray
        Utility values, shape (n_rows,)
    du_dtheta : np.ndarray
        Derivatives of u w.r.t. preference parameters, shape (n_rows, 9)
    """
    n = len(df)
    pref, _, _ = unpack_theta_singles(theta)
    
    # Get normalized consumption and leisure
    c = None
    if "c_norm" in df.columns and not df["c_norm"].isna().all():
        c = df["c_norm"].to_numpy()
    if c is None and "consumption" in df.columns and not df["consumption"].isna().all():
        c = df["consumption"].to_numpy() / MEAN_DISPY_NORM
    if c is None and "ils_dispy" in df.columns and not df["ils_dispy"].isna().all():
        c = df["ils_dispy"].to_numpy() / MEAN_DISPY_NORM
    if c is None:
        c = np.ones(n)
    
    l = None
    if "l_norm" in df.columns and not df["l_norm"].isna().all():
        l = df["l_norm"].to_numpy()
    if l is None and "leisure" in df.columns and not df["leisure"].isna().all():
        l = df["leisure"].to_numpy() / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    if l is None and "hours" in df.columns:
        hours = df["hours"].to_numpy()
        l = (TOTAL_LEISURE_HOURS - hours) / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    else:
        l = np.ones(n)
    
    c = np.clip(c, 1e-6, None)
    l = np.clip(l, 1e-6, None)
    
    # Covariates - SIMPLIFIED: use demeaned age
    age_norm = _get_col(df, "age_norm", 0.0)
    if age_norm.sum() == 0 and "dag" in df.columns:
        # Fall back to computing age_norm from dag
        age = pd.to_numeric(df["dag"], errors="coerce").fillna(40).to_numpy()
        mean_age = 40.0  # Approximate mean
        age_norm = age - mean_age
    age_norm2 = age_norm ** 2
    
    n_children = _get_col(df, "n_children", 0.0)
    educL = _get_col(df, "educL", 0.0)
    educH = _get_col(df, "educH", 0.0)
    
    # Box-Cox transforms
    l_bc = boxcox_transform(l, pref.theta_l)
    c_bc = boxcox_transform(c, pref.theta_c)
    
    # Derivatives of Box-Cox w.r.t. theta_l and theta_c
    dl_bc_dtheta_l = d_boxcox_dtheta(l, pref.theta_l)
    dc_bc_dtheta_c = d_boxcox_dtheta(c, pref.theta_c)
    
    # Build beta_leisure coefficient - SIMPLIFIED
    beta_leisure = (
        pref.beta_l0
        + pref.beta_l_age_norm * age_norm
        + pref.beta_l_age_norm2 * age_norm2
        + pref.beta_l_n_children * n_children
        + pref.beta_l_educL * educL
        + pref.beta_l_educH * educH
    )
    
    # Utility
    u = beta_leisure * l_bc + pref.beta_c * c_bc
    
    # Derivatives w.r.t. preference parameters (9 params)
    # [0] beta_l0, [1] beta_l_age_norm, [2] beta_l_age_norm2, [3] beta_l_n_children,
    # [4] beta_l_educL, [5] beta_l_educH, [6] beta_c, [7] theta_l, [8] theta_c
    
    du_dtheta = np.zeros((n, 9), dtype=float)
    
    du_dtheta[:, 0] = l_bc                           # beta_l0
    du_dtheta[:, 1] = age_norm * l_bc                # beta_l_age_norm
    du_dtheta[:, 2] = age_norm2 * l_bc               # beta_l_age_norm2
    du_dtheta[:, 3] = n_children * l_bc              # beta_l_n_children
    du_dtheta[:, 4] = educL * l_bc                   # beta_l_educL
    du_dtheta[:, 5] = educH * l_bc                   # beta_l_educH
    du_dtheta[:, 6] = c_bc                           # beta_c
    du_dtheta[:, 7] = beta_leisure * dl_bc_dtheta_l  # theta_l
    du_dtheta[:, 8] = pref.beta_c * dc_bc_dtheta_c   # theta_c
    
    return u, du_dtheta


def _compute_hopp_derivatives(
    df: pd.DataFrame,
    theta: np.ndarray,
    is_male: bool = True,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute hours opportunity density and its derivatives.
    
    SIMPLIFIED SPECIFICATION (7 params, no region interactions):
    
    Returns
    -------
    h_opp : np.ndarray
        Log hours opportunity density, shape (n_rows,)
    dh_dtheta : np.ndarray
        Derivatives w.r.t. hopp parameters, shape (n_rows, 7)
        Columns correspond to parameters [9:16] in theta
    """
    n = len(df)
    _, hopp, _ = unpack_theta_singles(theta)
    
    # Get working indicators
    working = _get_col(df, "working", 0.0)
    working_pt1 = _get_col(df, "working_pt1", 0.0)
    working_pt2 = _get_col(df, "working_pt2", 0.0)
    working_ft = _get_col(df, "working_ft", 0.0)
    
    if "working" not in df.columns and "hours" in df.columns:
        hours = pd.to_numeric(df["hours"], errors="coerce").fillna(0).to_numpy()
        working = (hours > 0).astype(float)
        working_pt1 = ((hours >= 18.5) & (hours <= 21.5)).astype(float)
        working_pt2 = ((hours >= 29.5) & (hours <= 30.5)).astype(float)
        working_ft = ((hours >= 37.5) & (hours <= 40.5)).astype(float)
    
    gsur = _get_col(df, "gsur", 0.0)
    educL = _get_col(df, "educL", 0.0)
    educH = _get_col(df, "educH", 0.0)
    
    # h_opp value - SIMPLIFIED (no region interactions)
    h_opp = (
        hopp.beta_work * working
        + hopp.beta_pt1 * working_pt1
        + hopp.beta_pt2 * working_pt2
        + hopp.beta_ft * working_ft
        + hopp.beta_gsur * working * gsur
        + hopp.beta_work_educL * working * educL
        + hopp.beta_work_educH * working * educH
    )
    
    # Derivatives (7 params)
    # [9] beta_work, [10] beta_pt1, [11] beta_pt2, [12] beta_ft,
    # [13] beta_gsur, [14] beta_work_educL, [15] beta_work_educH
    
    dh_dtheta = np.zeros((n, 7), dtype=float)
    dh_dtheta[:, 0] = working
    dh_dtheta[:, 1] = working_pt1
    dh_dtheta[:, 2] = working_pt2
    dh_dtheta[:, 3] = working_ft
    dh_dtheta[:, 4] = working * gsur
    dh_dtheta[:, 5] = working * educL
    dh_dtheta[:, 6] = working * educH
    
    return h_opp, dh_dtheta


def _compute_wopp_derivatives(
    df: pd.DataFrame,
    theta: np.ndarray,
    is_male: bool = True,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute wage opportunity density and its derivatives.
    
    SIMPLIFIED SPECIFICATION (6 params, no region/year dummies):
    
    Returns
    -------
    w_opp : np.ndarray
        Log wage opportunity density, shape (n_rows,)
    dw_dtheta : np.ndarray
        Derivatives w.r.t. wopp parameters, shape (n_rows, 6)
        Columns correspond to parameters [16:22] in theta:
        [0] beta0, [1] beta_educL, [2] beta_educH, [3] beta_pexp, [4] beta_pexp2, [5] sigma
    """
    n = len(df)
    _, _, wopp = unpack_theta_singles(theta, wage_spec="vw")
    
    working = _get_col(df, "working", 0.0)
    if working.sum() == 0 and "hours" in df.columns:
        hours = pd.to_numeric(df["hours"], errors="coerce").fillna(0).to_numpy()
        working = (hours > 0).astype(float)
    
    if "wage" in df.columns:
        wage = pd.to_numeric(df["wage"], errors="coerce").fillna(1).to_numpy()
    elif "yivwg" in df.columns:
        wage = pd.to_numeric(df["yivwg"], errors="coerce").fillna(1).to_numpy()
    else:
        wage = np.ones(n)
    wage = np.clip(wage, 1e-6, None)
    log_wage = np.log(wage)
    
    educL = _get_col(df, "educL", 0.0)
    educH = _get_col(df, "educH", 0.0)
    
    if "pexp" in df.columns:
        pexp = pd.to_numeric(df["pexp"], errors="coerce").fillna(0).to_numpy()
    elif "pexp_years" in df.columns:
        pexp = pd.to_numeric(df["pexp_years"], errors="coerce").fillna(0).to_numpy() / 100.0
    else:
        pexp = np.zeros(n)
    
    # Mean log-wage (Mincer equation - SIMPLIFIED, no region/year)
    mean_logw = (
        wopp.beta0
        + wopp.beta_educL * educL
        + wopp.beta_educH * educH
        + wopp.beta_pexp * pexp
        + wopp.beta_pexp2 * (pexp ** 2)
    )
    
    sigma = np.abs(wopp.sigma) + 1e-6
    z = (log_wage - mean_logw) / sigma
    
    # w_opp = -0.5*z² - log(σ) - log(w)
    w_opp = -0.5 * z**2 - np.log(sigma) - log_wage
    w_opp = np.where(working > 0, w_opp, 0.0)
    
    # Derivatives of w_opp (6 params)
    dw_dtheta = np.zeros((n, 6), dtype=float)
    
    z_over_sigma = z / sigma
    
    dw_dtheta[:, 0] = z_over_sigma * 1.0           # beta0
    dw_dtheta[:, 1] = z_over_sigma * educL         # beta_educL
    dw_dtheta[:, 2] = z_over_sigma * educH         # beta_educH
    dw_dtheta[:, 3] = z_over_sigma * pexp          # beta_pexp
    dw_dtheta[:, 4] = z_over_sigma * (pexp ** 2)   # beta_pexp2
    dw_dtheta[:, 5] = (z**2 - 1.0) / sigma         # sigma
    
    # Zero out for non-working
    dw_dtheta = np.where(working[:, None] > 0, dw_dtheta, 0.0)
    
    return w_opp, dw_dtheta


def analytical_gradient_singles(
    theta: np.ndarray,
    df: pd.DataFrame,
    is_male: bool = True,
    wage_spec: str = "fw",
) -> np.ndarray:
    """
    Compute analytical gradient of log-likelihood for singles.
    
    The gradient of the log-likelihood for MNL is:
        ∂LL/∂θ = Σ_i [∂V_i*/∂θ - Σ_j P_ij * ∂V_ij/∂θ]
    
    where i* is the chosen alternative for individual i.
    
    SIMPLIFIED PARAMETER STRUCTURE:
    - Preferences (9): [0:9]
    - Hours opp (7): [9:16]  
    - Wage opp (6): [16:22] (vw only)
    
    Total: 16 (fw) or 22 (vw)
    """
    n = len(df)
    n_params = 22 if wage_spec == "vw" else 16
    
    # Compute utilities and derivatives
    u, du_dtheta_pref = _compute_utility_derivatives_singles(df, theta, is_male)
    h_opp, dh_dtheta = _compute_hopp_derivatives(df, theta, is_male)
    
    if wage_spec == "vw":
        w_opp, dw_dtheta = _compute_wopp_derivatives(df, theta, is_male)
    else:
        w_opp = np.zeros(n)
        dw_dtheta = np.zeros((n, 6))
    
    # Prior
    prior_col = df.get("prior", None)
    if prior_col is not None:
        log_prior = pd.to_numeric(prior_col, errors="coerce").fillna(0).to_numpy()
    else:
        log_prior = np.zeros(n)
    
    # Total utility V = u + h_opp + w_opp - log_prior
    V = u + h_opp + w_opp - log_prior
    
    # Stack derivatives into full dV/dtheta matrix (n_rows x n_params)
    dV_dtheta = np.zeros((n, n_params), dtype=float)
    dV_dtheta[:, 0:9] = du_dtheta_pref           # preference params (9)
    dV_dtheta[:, 9:16] = dh_dtheta               # hours opp params (7)
    if wage_spec == "vw":
        dV_dtheta[:, 16:22] = dw_dtheta          # wage opp params (6)
    
    # Get individual IDs and choice indicators
    if "idhh_true" in df.columns:
        ids = df["idhh_true"].to_numpy()
    elif "idhh" in df.columns:
        ids = df["idhh"].to_numpy()
    elif "idperson_true" in df.columns:
        ids = df["idperson_true"].to_numpy()
    elif "idperson" in df.columns:
        ids = df["idperson"].to_numpy()
    else:
        raise KeyError("No ID column found")
    
    draws = df["draw"].to_numpy()
    if "is_chosen" in df.columns:
        is_chosen = pd.to_numeric(df["is_chosen"], errors="coerce").fillna(0).to_numpy()
        is_obs = (is_chosen == 1) | (draws == 0)
    else:
        is_obs = (draws == 0)
    
    # =========================================================================
    # FULLY VECTORIZED gradient computation - NO PYTHON LOOPS
    # Uses np.bincount for group aggregations (much faster than loops)
    # =========================================================================
    
    # Map IDs to consecutive indices 0, 1, 2, ...
    unique_ids, group_idx = np.unique(ids, return_inverse=True)
    n_individuals = len(unique_ids)
    
    # ----- Step 1: Log-sum-exp with numerical stability -----
    # Find max V per individual using bincount-like approach
    # We use a trick: set V_shifted = V - V_max_per_group
    
    # Get max V per group (vectorized using np.maximum.reduceat or sorting)
    # First, find group boundaries (data should be sorted by id)
    id_changes = np.concatenate([[0], np.where(np.diff(ids) != 0)[0] + 1, [n]])
    
    # Compute max V per group using reduceat
    V_max_per_group = np.maximum.reduceat(V, id_changes[:-1])
    
    # Broadcast max back to each row
    V_max = V_max_per_group[group_idx]
    
    # ----- Step 2: Softmax probabilities -----
    exp_V_shifted = np.exp(V - V_max)
    
    # Sum exp(V) per individual using bincount
    sum_exp_V_per_group = np.bincount(group_idx, weights=exp_V_shifted, minlength=n_individuals)
    
    # Broadcast sum back to each row
    sum_exp_V = sum_exp_V_per_group[group_idx]
    
    # Choice probabilities
    P = exp_V_shifted / sum_exp_V
    
    # ----- Step 3: Expected derivatives E[dV/dθ] per individual -----
    # E_dV[g, k] = Σ_j∈g P[j] * dV[j, k]
    # We compute this using matrix multiplication with bincount
    
    # For each parameter k, compute: E_dV_per_group[:, k] = bincount(group_idx, P * dV[:, k])
    # This is equivalent to: E_dV_per_group = (sparse group matrix).T @ (P[:, None] * dV_dtheta)
    
    P_weighted_dV = P[:, None] * dV_dtheta  # (n, n_params)
    
    # Sum P-weighted derivatives per group for each parameter
    # Use numba-accelerated version if available, otherwise fall back to loop
    E_dV_per_group = np.zeros((n_individuals, n_params), dtype=float)
    for k in range(n_params):
        E_dV_per_group[:, k] = np.bincount(group_idx, weights=P_weighted_dV[:, k], minlength=n_individuals)
    
    # Broadcast E[dV] back to each row
    E_dV = E_dV_per_group[group_idx, :]
    
    # ----- Step 4: Gradient = sum over observed of (dV_obs - E[dV]) -----
    obs_mask = is_obs.astype(bool)
    grad = (dV_dtheta[obs_mask, :] - E_dV[obs_mask, :]).sum(axis=0)
    
    return grad


def analytical_gradient_singles_numba(
    theta: np.ndarray,
    df: pd.DataFrame,
    is_male: bool = True,
    wage_spec: str = "fw",
) -> np.ndarray:
    """
    Compute analytical gradient using numba-accelerated core computation.
    
    This version uses the numba JIT-compiled _compute_softmax_gradient_numba
    function for the inner loop, which can provide significant speedup
    on multi-core systems.
    
    Falls back to regular analytical_gradient_singles if numba is not available.
    """
    if not NUMBA_AVAILABLE or _compute_softmax_gradient_numba is None:
        return analytical_gradient_singles(theta, df, is_male, wage_spec)
    
    n = len(df)
    n_params = 37 if wage_spec == "vw" else 21
    
    # Compute utilities and derivatives (same as regular version)
    u, du_dtheta_pref = _compute_utility_derivatives_singles(df, theta, is_male)
    h_opp, dh_dtheta = _compute_hopp_derivatives(df, theta, is_male)
    
    if wage_spec == "vw":
        w_opp, dw_dtheta = _compute_wopp_derivatives(df, theta, is_male)
    else:
        w_opp = np.zeros(n)
        dw_dtheta = np.zeros((n, 16))
    
    # Prior
    prior_col = df.get("prior", None)
    if prior_col is not None:
        log_prior = pd.to_numeric(prior_col, errors="coerce").fillna(0).to_numpy()
    else:
        log_prior = np.zeros(n)
    
    # Total utility V
    V = u + h_opp + w_opp - log_prior
    
    # Stack derivatives
    dV_dtheta = np.zeros((n, n_params), dtype=np.float64)
    dV_dtheta[:, 0:12] = du_dtheta_pref
    dV_dtheta[:, 12:21] = dh_dtheta
    if wage_spec == "vw":
        dV_dtheta[:, 21:37] = dw_dtheta
    
    # Get IDs and choice indicators
    if "idhh_true" in df.columns:
        ids = df["idhh_true"].to_numpy()
    elif "idhh" in df.columns:
        ids = df["idhh"].to_numpy()
    elif "idperson_true" in df.columns:
        ids = df["idperson_true"].to_numpy()
    else:
        ids = df["idperson"].to_numpy()
    
    draws = df["draw"].to_numpy()
    if "is_chosen" in df.columns:
        is_chosen = pd.to_numeric(df["is_chosen"], errors="coerce").fillna(0).to_numpy()
        is_obs = (is_chosen == 1) | (draws == 0)
    else:
        is_obs = (draws == 0)
    
    # Prepare data for numba function
    # Find group boundaries and observed indices
    id_changes = np.where(np.diff(ids) != 0)[0] + 1
    group_starts = np.concatenate([[0], id_changes]).astype(np.int64)
    group_ends = np.concatenate([id_changes, [n]]).astype(np.int64)
    
    # Find observed index for each group
    obs_indices = np.zeros(len(group_starts), dtype=np.int64)
    for g in range(len(group_starts)):
        s, e = group_starts[g], group_ends[g]
        obs_in_group = np.where(is_obs[s:e])[0]
        if len(obs_in_group) > 0:
            obs_indices[g] = s + obs_in_group[0]
        else:
            obs_indices[g] = s  # fallback
    
    # Call numba function
    grad = _compute_softmax_gradient_numba(
        V.astype(np.float64),
        dV_dtheta.astype(np.float64),
        group_starts,
        group_ends,
        obs_indices,
    )
    
    return grad


def neg_log_likelihood_with_grad_singles(
    theta: np.ndarray,
    df: pd.DataFrame,
    is_male: bool = True,
    wage_spec: str = "fw",
) -> Tuple[float, np.ndarray]:
    """
    Compute negative log-likelihood and its gradient simultaneously.
    
    This is more efficient when both are needed (e.g., L-BFGS-B optimization).
    """
    ll = log_likelihood_singles(theta, df, is_male=is_male, wage_spec=wage_spec)
    grad = analytical_gradient_singles(theta, df, is_male=is_male, wage_spec=wage_spec)
    return -ll, -grad


# =============================================================================
# FAST VERSIONS using PrecomputedData (2-5x speedup)
# =============================================================================
# These functions avoid DataFrame overhead by using pre-extracted numpy arrays.
# Call precompute_data_singles() ONCE before optimization, then use these.

def _fast_boxcox(x: np.ndarray, theta: float) -> np.ndarray:
    """Fast Box-Cox transform on contiguous array."""
    if abs(theta) < 1e-6:
        return np.log(x)
    return (np.power(x, theta) - 1.0) / theta


def _fast_d_boxcox_dtheta(x: np.ndarray, theta: float) -> np.ndarray:
    """Fast derivative of Box-Cox w.r.t. theta."""
    ln_x = np.log(x)
    if abs(theta) < 1e-6:
        return 0.5 * ln_x * ln_x
    x_theta = np.power(x, theta)
    return (theta * x_theta * ln_x - (x_theta - 1.0)) / (theta * theta)


def fast_log_likelihood_singles(
    theta: np.ndarray,
    data: PrecomputedDataSingles,
    is_male: bool = True,
    wage_spec: str = "fw",
) -> float:
    """
    FAST log-likelihood using precomputed data arrays.
    
    This avoids all DataFrame overhead - typically 2-5x faster than
    log_likelihood_singles() which accesses DataFrame columns repeatedly.
    
    SIMPLIFIED PARAMETER STRUCTURE (22 params for vw, 16 for fw):
    
    PREFERENCES (9 params):
      [0]  beta_l0          - leisure intercept
      [1]  beta_l_age_norm  - demeaned age effect
      [2]  beta_l_age_norm2 - demeaned age² effect
      [3]  beta_l_n_children- total children effect
      [4]  beta_l_educL     - low education effect
      [5]  beta_l_educH     - high education effect
      [6]  beta_c           - consumption coefficient
      [7]  theta_l          - Box-Cox for leisure
      [8]  theta_c          - Box-Cox for consumption
    
    HOURS OPPORTUNITY (7 params):
      [9]  beta_work        - working indicator
      [10] beta_pt1         - 20h focal point
      [11] beta_pt2         - 30h focal point
      [12] beta_ft          - 40h focal point
      [13] beta_gsur        - unemployment rate
      [14] beta_work_educL  - low education × working
      [15] beta_work_educH  - high education × working
    
    WAGE OPPORTUNITY (6 params, vw only):
      [16] beta0            - log-wage intercept
      [17] beta_educL       - low education wage penalty
      [18] beta_educH       - high education wage premium
      [19] beta_pexp        - experience (linear)
      [20] beta_pexp2       - experience (quadratic)
      [21] sigma            - std dev of log-wage
    
    Parameters
    ----------
    theta : np.ndarray
        Parameter vector (22 for vw, 16 for fw)
    data : PrecomputedDataSingles  
        Pre-extracted arrays from precompute_data_singles()
    is_male : bool
        True for single males
    wage_spec : str
        "fw" or "vw"
    
    Returns
    -------
    float
        Total log-likelihood
    """
    # Unpack theta manually (faster than calling unpack_theta_singles)
    # Preference params [0:9]
    beta_l0 = theta[0]
    beta_l_age_norm = theta[1]
    beta_l_age_norm2 = theta[2]
    beta_l_n_children = theta[3]
    beta_l_educL = theta[4]
    beta_l_educH = theta[5]
    beta_c = theta[6]
    theta_l = theta[7]
    theta_c = theta[8]
    
    # Hours opp params [9:16]
    beta_work = theta[9]
    beta_pt1 = theta[10]
    beta_pt2 = theta[11]
    beta_ft = theta[12]
    beta_gsur = theta[13]
    beta_work_educL = theta[14]
    beta_work_educH = theta[15]
    
    # -------------------------------------------------------------------------
    # Utility computation (vectorized)
    # -------------------------------------------------------------------------
    # Box-Cox transforms
    l_bc = _fast_boxcox(data.l, theta_l)
    c_bc = _fast_boxcox(data.c, theta_c)
    
    # Beta_leisure coefficient (simplified: demeaned age + single children variable)
    beta_leisure = (
        beta_l0
        + beta_l_age_norm * data.age_norm
        + beta_l_age_norm2 * data.age_norm2
        + beta_l_n_children * data.n_children
        + beta_l_educL * data.educL
        + beta_l_educH * data.educH    )
    
    u = beta_leisure * l_bc + beta_c * c_bc
    
    # -------------------------------------------------------------------------
    # Hours opportunity density (simplified: no region interactions)
    # -------------------------------------------------------------------------
    h_opp = (
        beta_work * data.working
        + beta_pt1 * data.working_pt1
        + beta_pt2 * data.working_pt2
        + beta_ft * data.working_ft
        + beta_gsur * data.working * data.gsur
        + beta_work_educL * data.working * data.educL
        + beta_work_educH * data.working * data.educH
    )
    
    # -------------------------------------------------------------------------
    # Wage opportunity density (only for vw, simplified: no region/year)
    # -------------------------------------------------------------------------
    if wage_spec == "vw":
        # Wage params [16:22]
        w_beta0 = theta[16]
        w_educL = theta[17]
        w_educH = theta[18]
        w_pexp = theta[19]
        w_pexp2 = theta[20]
        sigma = abs(theta[21]) + 1e-6
        
        # Mean log-wage (simplified Mincer equation)
        mean_logw = (
            w_beta0
            + w_educL * data.educL + w_educH * data.educH
            + w_pexp * data.pexp + w_pexp2 * data.pexp2
        )
        
        z = (data.log_wage - mean_logw) / sigma
        w_opp = -0.5 * z * z - np.log(sigma) - data.log_wage
        w_opp = np.where(data.working > 0, w_opp, 0.0)
    else:
        w_opp = 0.0
    
    # -------------------------------------------------------------------------
    # Composite utility V
    # -------------------------------------------------------------------------
    V = u + h_opp + w_opp - data.log_prior
    
    # -------------------------------------------------------------------------
    # Log-likelihood (vectorized log-sum-exp)
    # -------------------------------------------------------------------------
    # Use pre-computed group boundaries
    V_max_per_group = np.maximum.reduceat(V, data.group_starts)
    V_max = V_max_per_group[data.group_idx]
    
    exp_V_shifted = np.exp(V - V_max)
    sum_exp_per_group = np.bincount(data.group_idx, weights=exp_V_shifted, minlength=data.n_groups)
    log_sum_exp_per_group = V_max_per_group + np.log(sum_exp_per_group)
      # LL = sum over observed of (V_obs - log_sum_exp)
    V_obs = V[data.obs_indices]
    ll = np.sum(V_obs - log_sum_exp_per_group)
    
    return ll


def fast_log_likelihood_couples(
    theta: np.ndarray,
    data: PrecomputedDataCouples,
    wage_spec: str = "fw",
) -> float:
    """
    FAST log-likelihood for couples using precomputed data arrays.
    
    SIMPLIFIED SPECIFICATION:
    - Uses demeaned age (age_norm) instead of log(age)
    - Single n_children variable instead of ch0_3, ch4_6, ch7_9
    - No region effects on preferences or hours opportunity
    - No year dummies on wages
    
    Parameter layout (fw = 28 params, vw = 40 params):
    
    MALE PREFERENCES (6 params):
      [0]  beta_lm0          - male leisure intercept
      [1]  beta_lm_age_norm  - male demeaned age effect
      [2]  beta_lm_age_norm2 - male demeaned age² effect
      [3]  beta_lm_n_children- male children effect
      [4]  beta_lm_educL     - male low education
      [5]  beta_lm_educH     - male high education
    
    FEMALE PREFERENCES (6 params):
      [6]  beta_lf0          - female leisure intercept
      [7]  beta_lf_age_norm  - female demeaned age effect
      [8]  beta_lf_age_norm2 - female demeaned age² effect
      [9]  beta_lf_n_children- female children effect
      [10] beta_lf_educL     - female low education
      [11] beta_lf_educH     - female high education
    
    SHARED (4 params):
      [12] beta_c    - consumption coefficient
      [13] theta_lm  - Box-Cox male leisure
      [14] theta_lf  - Box-Cox female leisure
      [15] theta_c   - Box-Cox consumption
    
    MALE HOURS OPP (7 params):
      [16] beta_work_m       - male working indicator
      [17] beta_pt1_m        - male 20h focal point
      [18] beta_pt2_m        - male 30h focal point
      [19] beta_ft_m         - male 40h focal point
      [20] beta_gsur_m       - male unemployment rate
      [21] beta_work_educL_m - male low education × working
      [22] beta_work_educH_m - male high education × working
    
    FEMALE HOURS OPP (7 params):
      [23] beta_work_f       - female working indicator
      [24] beta_pt1_f        - female 20h focal point
      [25] beta_pt2_f        - female 30h focal point
      [26] beta_ft_f         - female 40h focal point
      [27] beta_gsur_f       - female unemployment rate
      [28] beta_work_educL_f - female low education × working
      [29] beta_work_educH_f - female high education × working
    
    MALE WAGE OPP (6 params, vw only):
      [30] w_beta0_m   - male log-wage intercept
      [31] w_educL_m   - male low education wage penalty
      [32] w_educH_m   - male high education wage premium
      [33] w_pexp_m    - male experience (linear)
      [34] w_pexp2_m   - male experience (quadratic)
      [35] sigma_m     - male std dev of log-wage
    
    FEMALE WAGE OPP (6 params, vw only):
      [36] w_beta0_f   - female log-wage intercept
      [37] w_educL_f   - female low education wage penalty
      [38] w_educH_f   - female high education wage premium
      [39] w_pexp_f    - female experience (linear)
      [40] w_pexp2_f   - female experience (quadratic)
      [41] sigma_f     - female std dev of log-wage
    
    TOTAL: 30 params for fw, 42 params for vw
    
    Returns
    -------
    float
        Total log-likelihood
    """
    # -------------------------------------------------------------------------
    # Unpack theta - Male leisure preferences [0:6]
    # -------------------------------------------------------------------------
    beta_lm0 = theta[0]
    beta_lm_age_norm = theta[1]
    beta_lm_age_norm2 = theta[2]
    beta_lm_n_children = theta[3]
    beta_lm_educL = theta[4]
    beta_lm_educH = theta[5]
    
    # Female leisure preferences [6:12]
    beta_lf0 = theta[6]
    beta_lf_age_norm = theta[7]
    beta_lf_age_norm2 = theta[8]
    beta_lf_n_children = theta[9]
    beta_lf_educL = theta[10]
    beta_lf_educH = theta[11]
    
    # Shared params [12:16]
    beta_c = theta[12]
    theta_lm = theta[13]
    theta_lf = theta[14]
    theta_c = theta[15]
    
    # Male hours opportunity [16:23]
    beta_work_m = theta[16]
    beta_pt1_m = theta[17]
    beta_pt2_m = theta[18]
    beta_ft_m = theta[19]
    beta_gsur_m = theta[20]
    beta_work_educL_m = theta[21]
    beta_work_educH_m = theta[22]
    
    # Female hours opportunity [23:30]
    beta_work_f = theta[23]
    beta_pt1_f = theta[24]
    beta_pt2_f = theta[25]
    beta_ft_f = theta[26]
    beta_gsur_f = theta[27]
    beta_work_educL_f = theta[28]
    beta_work_educH_f = theta[29]
    
    # -------------------------------------------------------------------------
    # Utility computation (vectorized)
    # -------------------------------------------------------------------------
    # Box-Cox transforms
    lm_bc = _fast_boxcox(data.l_m, theta_lm)
    lf_bc = _fast_boxcox(data.l_f, theta_lf)
    c_bc = _fast_boxcox(data.c, theta_c)
    
    # Male leisure coefficient (simplified)
    beta_leisure_m = (
        beta_lm0
        + beta_lm_age_norm * data.age_norm_m
        + beta_lm_age_norm2 * data.age_norm2_m
        + beta_lm_n_children * data.n_children
        + beta_lm_educL * data.educL_m
        + beta_lm_educH * data.educH_m
    )
    
    # Female leisure coefficient (simplified)
    beta_leisure_f = (
        beta_lf0
        + beta_lf_age_norm * data.age_norm_f
        + beta_lf_age_norm2 * data.age_norm2_f
        + beta_lf_n_children * data.n_children
        + beta_lf_educL * data.educL_f
        + beta_lf_educH * data.educH_f
    )
    
    # Total utility
    u = beta_leisure_m * lm_bc + beta_leisure_f * lf_bc + beta_c * c_bc
    
    # -------------------------------------------------------------------------
    # Hours opportunity density - male (simplified: no region)
    # -------------------------------------------------------------------------
    h_opp_m = (
        beta_work_m * data.working_m
        + beta_pt1_m * data.working_pt1_m
        + beta_pt2_m * data.working_pt2_m
        + beta_ft_m * data.working_ft_m
        + beta_gsur_m * data.working_m * data.gsur_m
        + beta_work_educL_m * data.working_m * data.educL_m
        + beta_work_educH_m * data.working_m * data.educH_m
    )
    
    # Hours opportunity density - female (simplified: no region)
    h_opp_f = (
        beta_work_f * data.working_f
        + beta_pt1_f * data.working_pt1_f
        + beta_pt2_f * data.working_pt2_f
        + beta_ft_f * data.working_ft_f
        + beta_gsur_f * data.working_f * data.gsur_f
        + beta_work_educL_f * data.working_f * data.educL_f
        + beta_work_educH_f * data.working_f * data.educH_f
    )
    
    h_opp = h_opp_m + h_opp_f
    
    # -------------------------------------------------------------------------
    # Wage opportunity density (only for vw, simplified: no region/year)
    # -------------------------------------------------------------------------
    if wage_spec == "vw" and len(theta) > 30:
        # Male wage params [30:36]
        w_beta0_m = theta[30]
        w_educL_m = theta[31]
        w_educH_m = theta[32]
        w_pexp_m = theta[33]
        w_pexp2_m = theta[34]
        sigma_m = abs(theta[35]) + 1e-6
        
        mean_logw_m = (
            w_beta0_m
            + w_educL_m * data.educL_m + w_educH_m * data.educH_m
            + w_pexp_m * data.pexp_m + w_pexp2_m * data.pexp2_m
        )
        z_m = (data.log_wage_m - mean_logw_m) / sigma_m
        w_opp_m = np.where(data.working_m > 0, 
                          -0.5 * z_m * z_m - np.log(sigma_m) - data.log_wage_m, 0.0)
        
        # Female wage params [36:42]
        w_beta0_f = theta[36]
        w_educL_f = theta[37]
        w_educH_f = theta[38]
        w_pexp_f = theta[39]
        w_pexp2_f = theta[40]
        sigma_f = abs(theta[41]) + 1e-6
        
        mean_logw_f = (
            w_beta0_f
            + w_educL_f * data.educL_f + w_educH_f * data.educH_f
            + w_pexp_f * data.pexp_f + w_pexp2_f * data.pexp2_f
        )
        z_f = (data.log_wage_f - mean_logw_f) / sigma_f
        w_opp_f = np.where(data.working_f > 0,
                          -0.5 * z_f * z_f - np.log(sigma_f) - data.log_wage_f, 0.0)
        
        w_opp = w_opp_m + w_opp_f
    else:
        w_opp = 0.0
    
    # -------------------------------------------------------------------------
    # Composite utility V
    # -------------------------------------------------------------------------
    V = u + h_opp + w_opp - data.log_prior
    
    # -------------------------------------------------------------------------
    # Log-likelihood (vectorized log-sum-exp)
    # -------------------------------------------------------------------------
    V_max_per_group = np.maximum.reduceat(V, data.group_starts)
    V_max = V_max_per_group[data.group_idx]
    
    exp_V_shifted = np.exp(V - V_max)
    sum_exp_per_group = np.bincount(data.group_idx, weights=exp_V_shifted, minlength=data.n_groups)
    log_sum_exp_per_group = V_max_per_group + np.log(sum_exp_per_group)
    
    # LL = sum over observed of (V_obs - log_sum_exp)
    V_obs = V[data.obs_indices]
    ll = np.sum(V_obs - log_sum_exp_per_group)
    
    return ll


def get_initial_theta_couples(wage_spec: str = "fw") -> np.ndarray:
    """
    Get initial parameter values for couples estimation.
    
    SIMPLIFIED Parameter layout (30 for fw, 42 for vw):
    [0:6]    - Male leisure preferences (6 params)
    [6:12]   - Female leisure preferences (6 params)
    [12:16]  - Shared: beta_c, theta_lm, theta_lf, theta_c
    [16:23]  - Male hours opportunity (7 params)
    [23:30]  - Female hours opportunity (7 params)
    [30:36]  - Male wage opportunity (6 params, vw only)
    [36:42]  - Female wage opportunity (6 params, vw only)
    """
    theta = []
    
    # Male leisure preferences [0:6]
    theta += [
        1.0,   # beta_lm0
        0.0,   # beta_lm_age_norm
        0.0,   # beta_lm_age_norm2
        0.0,   # beta_lm_n_children (may be zero for males)
        0.0,   # beta_lm_educL
        0.0,   # beta_lm_educH
    ]
    
    # Female leisure preferences [6:12]
    theta += [
        1.0,   # beta_lf0
        0.0,   # beta_lf_age_norm
        0.0,   # beta_lf_age_norm2
        0.1,   # beta_lf_n_children (positive for females - more leisure when kids)
        0.0,   # beta_lf_educL
        0.0,   # beta_lf_educH
    ]
    
    # Shared params [12:16]
    theta += [
        1.0,   # beta_c
        0.5,   # theta_lm
        0.5,   # theta_lf
        0.5,   # theta_c
    ]
    
    # Male hours opportunity [16:23]
    theta += [
        0.5,   # beta_work_m
        0.0,   # beta_pt1_m
        0.0,   # beta_pt2_m
        0.0,   # beta_ft_m
        0.0,   # beta_gsur_m
        0.0,   # beta_work_educL_m
        0.0,   # beta_work_educH_m
    ]
    
    # Female hours opportunity [23:30]
    theta += [
        0.5,   # beta_work_f
        0.0,   # beta_pt1_f
        0.0,   # beta_pt2_f
        0.0,   # beta_ft_f
        0.0,   # beta_gsur_f
        0.0,   # beta_work_educL_f
        0.0,   # beta_work_educH_f
    ]
    
    if wage_spec == "vw":
        # Male wage opportunity [30:36]
        theta += [
            2.5,    # w_beta0_m
            -0.1,   # w_educL_m
            0.2,    # w_educH_m
            0.02,   # w_pexp_m
            -0.001, # w_pexp2_m
            0.4,    # sigma_m
        ]
        
        # Female wage opportunity [36:42]
        theta += [
            2.3,    # w_beta0_f (typically lower)
            -0.1,   # w_educL_f
            0.2,    # w_educH_f
            0.02,   # w_pexp_f
            -0.001, # w_pexp2_f
            0.4,    # sigma_f
        ]
    
    return np.array(theta)


def get_param_names_couples(wage_spec: str = "fw") -> List[str]:
    """Return parameter names for couples, aligned with get_initial_theta_couples order."""
    names = []
    
    # Male leisure [0:6]
    names += [
        "cou.pref.beta_lm0", "cou.pref.beta_lm_age_norm", "cou.pref.beta_lm_age_norm2",
        "cou.pref.beta_lm_n_children",
        "cou.pref.beta_lm_educL", "cou.pref.beta_lm_educH",
    ]
    
    # Female leisure [6:12]
    names += [
        "cou.pref.beta_lf0", "cou.pref.beta_lf_age_norm", "cou.pref.beta_lf_age_norm2",
        "cou.pref.beta_lf_n_children",
        "cou.pref.beta_lf_educL", "cou.pref.beta_lf_educH",
    ]
    
    # Shared params [12:16]
    names += ["cou.pref.beta_c", "cou.pref.theta_lm", "cou.pref.theta_lf", "cou.pref.theta_c"]
    
    # Male hours opportunity [16:23]
    names += [
        "cou.hopp_m.beta_work", "cou.hopp_m.beta_pt1", "cou.hopp_m.beta_pt2",
        "cou.hopp_m.beta_ft", "cou.hopp_m.beta_gsur",
        "cou.hopp_m.beta_work_educL", "cou.hopp_m.beta_work_educH",
    ]
    
    # Female hours opportunity [23:30]
    names += [
        "cou.hopp_f.beta_work", "cou.hopp_f.beta_pt1", "cou.hopp_f.beta_pt2",
        "cou.hopp_f.beta_ft", "cou.hopp_f.beta_gsur",
        "cou.hopp_f.beta_work_educL", "cou.hopp_f.beta_work_educH",
    ]
    
    if wage_spec == "vw":
        # Male wage opportunity [30:36]
        names += [
            "cou.wopp_m.beta0", "cou.wopp_m.beta_educL", "cou.wopp_m.beta_educH",
            "cou.wopp_m.beta_pexp", "cou.wopp_m.beta_pexp2", "cou.wopp_m.sigma",
        ]
          # Female wage opportunity [36:42]
        names += [
            "cou.wopp_f.beta0", "cou.wopp_f.beta_educL", "cou.wopp_f.beta_educH",
            "cou.wopp_f.beta_pexp", "cou.wopp_f.beta_pexp2", "cou.wopp_f.sigma",
        ]
    
    return names


def pack_theta_couples(
    pref: PrefParamsCouples,
    hopp_m: HoursOppParams,
    hopp_f: HoursOppParams,
    wopp_m: WageOppParams = None,
    wopp_f: WageOppParams = None,
) -> np.ndarray:
    """
    Pack couples parameter dataclasses into flat vector.
    
    SIMPLIFIED Parameter layout (30 for fw, 42 for vw):
    [0:6]    - Male leisure preferences (6 params)
    [6:12]   - Female leisure preferences (6 params)
    [12:16]  - Shared: beta_c, theta_lm, theta_lf, theta_c
    [16:23]  - Male hours opportunity (7 params)
    [23:30]  - Female hours opportunity (7 params)
    [30:36]  - Male wage opportunity (6 params, vw only)
    [36:42]  - Female wage opportunity (6 params, vw only)
    """
    theta = [
        # Male leisure preferences [0:6]
        pref.beta_lm0, pref.beta_lm_age_norm, pref.beta_lm_age_norm2,
        pref.beta_lm_n_children, pref.beta_lm_educL, pref.beta_lm_educH,
        # Female leisure preferences [6:12]
        pref.beta_lf0, pref.beta_lf_age_norm, pref.beta_lf_age_norm2,
        pref.beta_lf_n_children, pref.beta_lf_educL, pref.beta_lf_educH,
        # Shared params [12:16]
        pref.beta_c, pref.theta_lm, pref.theta_lf, pref.theta_c,
        # Male hours opportunity [16:23]
        hopp_m.beta_work, hopp_m.beta_pt1, hopp_m.beta_pt2, hopp_m.beta_ft,
        hopp_m.beta_gsur, hopp_m.beta_work_educL, hopp_m.beta_work_educH,
        # Female hours opportunity [23:30]
        hopp_f.beta_work, hopp_f.beta_pt1, hopp_f.beta_pt2, hopp_f.beta_ft,
        hopp_f.beta_gsur, hopp_f.beta_work_educL, hopp_f.beta_work_educH,
    ]
    
    # Add wage opportunity params if provided
    if wopp_m is not None and wopp_f is not None:
        theta += [
            # Male wage opportunity [30:36]
            wopp_m.beta0, wopp_m.beta_educL, wopp_m.beta_educH,
            wopp_m.beta_pexp, wopp_m.beta_pexp2, wopp_m.sigma,
            # Female wage opportunity [36:42]
            wopp_f.beta0, wopp_f.beta_educL, wopp_f.beta_educH,
            wopp_f.beta_pexp, wopp_f.beta_pexp2, wopp_f.sigma,
        ]
    
    return np.array(theta)


def fast_analytical_gradient_singles(
    theta: np.ndarray,
    data: PrecomputedDataSingles,
    is_male: bool = True,
    wage_spec: str = "fw",
) -> np.ndarray:
    """
    FAST analytical gradient using precomputed data arrays.
    
    Computes gradient without any DataFrame access - typically 2-5x faster.
    Uses vectorized operations throughout.
    
    SIMPLIFIED PARAMETER STRUCTURE:
    - Preferences (9 params): [0-8] beta_l0, beta_l_age_norm, beta_l_age_norm2, 
      beta_l_n_children, beta_l_educL, beta_l_educH, beta_c, theta_l, theta_c
    - Hours opp (7 params): [9-15] beta_work, beta_pt1, beta_pt2, beta_ft, 
      beta_gsur, beta_work_educL, beta_work_educH
    - Wage opp (6 params): [16-21] beta0, beta_educL, beta_educH, beta_pexp, 
      beta_pexp2, sigma
    
    Total: 16 params for fw, 22 params for vw
    
    Parameters
    ----------
    theta : np.ndarray
        Parameter vector (length 16 for fw, 22 for vw)
    data : PrecomputedDataSingles
        Pre-extracted arrays (uses age_norm, age_norm2, n_children)
    is_male : bool
        True for single males (unused in simplified spec, kept for compatibility)
    wage_spec : str
        "fw" or "vw"
    
    Returns
    -------
    np.ndarray
        Gradient of log-likelihood w.r.t. theta
    """
    n = len(data.c)
    n_params = 22 if wage_spec == "vw" else 16
    
    # Unpack theta - SIMPLIFIED STRUCTURE
    # Preferences (9 params)
    beta_l0 = theta[0]
    beta_l_age_norm = theta[1]
    beta_l_age_norm2 = theta[2]
    beta_l_n_children = theta[3]
    beta_l_educL = theta[4]
    beta_l_educH = theta[5]
    beta_c = theta[6]
    theta_l = theta[7]
    theta_c = theta[8]
    
    # Hours opportunity (7 params)
    beta_work = theta[9]
    beta_pt1 = theta[10]
    beta_pt2 = theta[11]
    beta_ft = theta[12]
    beta_gsur = theta[13]
    beta_work_educL = theta[14]
    beta_work_educH = theta[15]
    
    # -------------------------------------------------------------------------
    # Utility and its derivatives
    # -------------------------------------------------------------------------
    l_bc = _fast_boxcox(data.l, theta_l)
    c_bc = _fast_boxcox(data.c, theta_c)
    dl_bc_dtheta_l = _fast_d_boxcox_dtheta(data.l, theta_l)
    dc_bc_dtheta_c = _fast_d_boxcox_dtheta(data.c, theta_c)
    
    beta_leisure = (
        beta_l0
        + beta_l_age_norm * data.age_norm
        + beta_l_age_norm2 * data.age_norm2
        + beta_l_n_children * data.n_children
        + beta_l_educL * data.educL
        + beta_l_educH * data.educH
    )
    
    u = beta_leisure * l_bc + beta_c * c_bc
    
    # Preference derivatives (9 params)
    du_dtheta = np.zeros((n, 9), dtype=np.float64)
    du_dtheta[:, 0] = l_bc                           # beta_l0
    du_dtheta[:, 1] = data.age_norm * l_bc           # beta_l_age_norm
    du_dtheta[:, 2] = data.age_norm2 * l_bc          # beta_l_age_norm2
    du_dtheta[:, 3] = data.n_children * l_bc         # beta_l_n_children
    du_dtheta[:, 4] = data.educL * l_bc              # beta_l_educL
    du_dtheta[:, 5] = data.educH * l_bc              # beta_l_educH
    du_dtheta[:, 6] = c_bc                           # beta_c
    du_dtheta[:, 7] = beta_leisure * dl_bc_dtheta_l  # theta_l
    du_dtheta[:, 8] = beta_c * dc_bc_dtheta_c        # theta_c
    
    # -------------------------------------------------------------------------
    # Hours opportunity and its derivatives
    # -------------------------------------------------------------------------
    h_opp = (
        beta_work * data.working
        + beta_pt1 * data.working_pt1
        + beta_pt2 * data.working_pt2
        + beta_ft * data.working_ft
        + beta_gsur * data.working * data.gsur
        + beta_work_educL * data.working * data.educL
        + beta_work_educH * data.working * data.educH
    )
    
    # Hours opp derivatives (7 params)
    dh_dtheta = np.zeros((n, 7), dtype=np.float64)
    dh_dtheta[:, 0] = data.working                   # beta_work
    dh_dtheta[:, 1] = data.working_pt1               # beta_pt1
    dh_dtheta[:, 2] = data.working_pt2               # beta_pt2
    dh_dtheta[:, 3] = data.working_ft                # beta_ft
    dh_dtheta[:, 4] = data.working * data.gsur       # beta_gsur
    dh_dtheta[:, 5] = data.working * data.educL      # beta_work_educL
    dh_dtheta[:, 6] = data.working * data.educH      # beta_work_educH
    
    # -------------------------------------------------------------------------
    # Wage opportunity and its derivatives (if vw)
    # -------------------------------------------------------------------------
    if wage_spec == "vw":
        w_beta0 = theta[16]
        w_educL = theta[17]
        w_educH = theta[18]
        w_pexp = theta[19]
        w_pexp2 = theta[20]
        sigma = abs(theta[21]) + 1e-6
        
        mean_logw = (
            w_beta0
            + w_educL * data.educL
            + w_educH * data.educH
            + w_pexp * data.pexp
            + w_pexp2 * data.pexp2
        )
        
        z = (data.log_wage - mean_logw) / sigma
        w_opp = np.where(data.working > 0, -0.5 * z * z - np.log(sigma) - data.log_wage, 0.0)
        
        z_over_sigma = z / sigma
        dw_dtheta = np.zeros((n, 6), dtype=np.float64)
        dw_dtheta[:, 0] = z_over_sigma               # w_beta0
        dw_dtheta[:, 1] = z_over_sigma * data.educL  # w_educL
        dw_dtheta[:, 2] = z_over_sigma * data.educH  # w_educH
        dw_dtheta[:, 3] = z_over_sigma * data.pexp   # w_pexp
        dw_dtheta[:, 4] = z_over_sigma * data.pexp2  # w_pexp2
        dw_dtheta[:, 5] = (z * z - 1.0) / sigma      # sigma
        dw_dtheta = np.where(data.working[:, None] > 0, dw_dtheta, 0.0)
    else:
        w_opp = 0.0
        dw_dtheta = np.zeros((n, 6), dtype=np.float64)
    
    # -------------------------------------------------------------------------
    # Composite V and dV/dtheta
    # -------------------------------------------------------------------------
    V = u + h_opp + w_opp - data.log_prior
    
    dV_dtheta = np.zeros((n, n_params), dtype=np.float64)
    dV_dtheta[:, 0:9] = du_dtheta         # Preferences (9 params)
    dV_dtheta[:, 9:16] = dh_dtheta        # Hours opp (7 params)
    if wage_spec == "vw":
        dV_dtheta[:, 16:22] = dw_dtheta   # Wage opp (6 params)
    
    # -------------------------------------------------------------------------
    # Softmax gradient computation (vectorized)
    # -------------------------------------------------------------------------
    V_max_per_group = np.maximum.reduceat(V, data.group_starts)
    V_max = V_max_per_group[data.group_idx]
    
    exp_V_shifted = np.exp(V - V_max)
    sum_exp_per_group = np.bincount(data.group_idx, weights=exp_V_shifted, minlength=data.n_groups)
    sum_exp = sum_exp_per_group[data.group_idx]
    
    P = exp_V_shifted / sum_exp
    P_weighted_dV = P[:, None] * dV_dtheta
    
    # Expected derivatives per group (bincount loop - consider numba for more speed)
    E_dV_per_group = np.zeros((data.n_groups, n_params), dtype=np.float64)
    for k in range(n_params):
        E_dV_per_group[:, k] = np.bincount(data.group_idx, weights=P_weighted_dV[:, k], minlength=data.n_groups)
    
    E_dV = E_dV_per_group[data.group_idx, :]
    
    # Gradient = sum over observed of (dV_obs - E[dV])
    grad = (dV_dtheta[data.is_obs, :] - E_dV[data.is_obs, :]).sum(axis=0)
    
    return grad


def fast_neg_ll_with_grad_singles(
    theta: np.ndarray,
    data: PrecomputedDataSingles,
    is_male: bool = True,
    wage_spec: str = "fw",
) -> Tuple[float, np.ndarray]:
    """
    OPTIMIZED: Compute LL and gradient in single pass for singles.
    
    SIMPLIFIED PARAMETER STRUCTURE (22 params for vw, 16 for fw):
    
    PREFERENCES (9 params): [0:9]
    HOURS OPPORTUNITY (7 params): [9:16]
    WAGE OPPORTUNITY (6 params, vw only): [16:22]
    
    This is ~30-50% faster than calling LL and grad separately because:
    1. Box-Cox transforms computed once (not twice)
    2. V and softmax probabilities computed once (not twice)
    3. Better cache locality
    
    Use this with L-BFGS-B for maximum speed.
    """
    n = len(data.c)
    n_params = 22 if wage_spec == "vw" else 16
    
    # Unpack theta - Preferences [0:9]
    beta_l0 = theta[0]
    beta_l_age_norm = theta[1]
    beta_l_age_norm2 = theta[2]
    beta_l_n_children = theta[3]
    beta_l_educL = theta[4]
    beta_l_educH = theta[5]
    beta_c = theta[6]
    theta_l = theta[7]
    theta_c = theta[8]
    
    # Hours opp [9:16]
    beta_work = theta[9]
    beta_pt1 = theta[10]
    beta_pt2 = theta[11]
    beta_ft = theta[12]
    beta_gsur = theta[13]
    beta_work_educL = theta[14]
    beta_work_educH = theta[15]
    
    # Box-Cox transforms (computed ONCE)
    l_bc = _fast_boxcox(data.l, theta_l)
    c_bc = _fast_boxcox(data.c, theta_c)
    dl_bc_dtheta_l = _fast_d_boxcox_dtheta(data.l, theta_l)
    dc_bc_dtheta_c = _fast_d_boxcox_dtheta(data.c, theta_c)
    
    # Utility (simplified)
    beta_leisure = (
        beta_l0 
        + beta_l_age_norm * data.age_norm 
        + beta_l_age_norm2 * data.age_norm2
        + beta_l_n_children * data.n_children
        + beta_l_educL * data.educL 
        + beta_l_educH * data.educH
    )
    
    u = beta_leisure * l_bc + beta_c * c_bc
    
    # Hours opportunity (simplified: no region interactions)
    h_opp = (
        beta_work * data.working 
        + beta_pt1 * data.working_pt1
        + beta_pt2 * data.working_pt2 
        + beta_ft * data.working_ft
        + beta_gsur * data.working * data.gsur
        + beta_work_educL * data.working * data.educL 
        + beta_work_educH * data.working * data.educH
    )
    
    # Wage opportunity (vw only, simplified)
    if wage_spec == "vw":
        sigma = abs(theta[21]) + 1e-6
        mean_logw = (
            theta[16] 
            + theta[17] * data.educL 
            + theta[18] * data.educH
            + theta[19] * data.pexp 
            + theta[20] * data.pexp2
        )
        z = (data.log_wage - mean_logw) / sigma
        w_opp = np.where(data.working > 0, -0.5*z*z - np.log(sigma) - data.log_wage, 0.0)
    else:
        w_opp = 0.0
        z = sigma = None
    
    # V and softmax (computed ONCE)
    V = u + h_opp + w_opp - data.log_prior
    V_max_per_group = np.maximum.reduceat(V, data.group_starts)
    V_max = V_max_per_group[data.group_idx]
    exp_V = np.exp(V - V_max)
    sum_exp = np.bincount(data.group_idx, weights=exp_V, minlength=data.n_groups)
    
    # LL
    ll = np.sum(V[data.obs_indices] - V_max_per_group - np.log(sum_exp))
    
    # Build dV/dtheta
    dV = np.zeros((n, n_params), dtype=np.float64)
    
    # Preference derivatives [0:9]
    dV[:, 0] = l_bc                        # beta_l0
    dV[:, 1] = data.age_norm * l_bc        # beta_l_age_norm
    dV[:, 2] = data.age_norm2 * l_bc       # beta_l_age_norm2
    dV[:, 3] = data.n_children * l_bc      # beta_l_n_children
    dV[:, 4] = data.educL * l_bc           # beta_l_educL
    dV[:, 5] = data.educH * l_bc           # beta_l_educH
    dV[:, 6] = c_bc                        # beta_c
    dV[:, 7] = beta_leisure * dl_bc_dtheta_l  # theta_l
    dV[:, 8] = beta_c * dc_bc_dtheta_c     # theta_c
    
    # Hours opp derivatives [9:16]
    dV[:, 9] = data.working               # beta_work
    dV[:, 10] = data.working_pt1          # beta_pt1
    dV[:, 11] = data.working_pt2          # beta_pt2
    dV[:, 12] = data.working_ft           # beta_ft
    dV[:, 13] = data.working * data.gsur  # beta_gsur
    dV[:, 14] = data.working * data.educL # beta_work_educL
    dV[:, 15] = data.working * data.educH # beta_work_educH
    
    # Wage derivatives (vw only) [16:22]
    if wage_spec == "vw" and z is not None:
        z_s = z / sigma
        dV[:, 16] = np.where(data.working > 0, z_s, 0.0)                 # beta0
        dV[:, 17] = np.where(data.working > 0, z_s * data.educL, 0.0)    # beta_educL
        dV[:, 18] = np.where(data.working > 0, z_s * data.educH, 0.0)    # beta_educH
        dV[:, 19] = np.where(data.working > 0, z_s * data.pexp, 0.0)     # beta_pexp
        dV[:, 20] = np.where(data.working > 0, z_s * data.pexp2, 0.0)    # beta_pexp2
        dV[:, 21] = np.where(data.working > 0, (z*z - 1.0)/sigma, 0.0)   # sigma
    
    # Softmax gradient
    P = exp_V / sum_exp[data.group_idx]
    P_dV = P[:, None] * dV
    E_dV = np.zeros((data.n_groups, n_params), dtype=np.float64)
    for k in range(n_params):
        E_dV[:, k] = np.bincount(data.group_idx, weights=P_dV[:, k], minlength=data.n_groups)
    
    grad = (dV[data.is_obs, :] - E_dV[data.group_idx[data.is_obs], :]).sum(axis=0)
    
    return -ll, -grad


def fast_neg_ll_with_grad_couples(
    theta: np.ndarray,
    data: PrecomputedDataCouples,
    wage_spec: str = "fw",
) -> Tuple[float, np.ndarray]:
    """
    OPTIMIZED: Compute LL and gradient for couples in single pass.
    
    SIMPLIFIED SPECIFICATION (matching fast_log_likelihood_couples):
    - Uses demeaned age (age_norm) instead of log(age)
    - Single n_children variable instead of ch0_3, ch4_6, ch7_9
    - No region effects on preferences or hours opportunity
    - No year dummies on wages
    
    Parameter layout (30 for fw, 42 for vw):
    [0:6]    - Male leisure preferences
    [6:12]   - Female leisure preferences
    [12:16]  - Shared: beta_c, theta_lm, theta_lf, theta_c
    [16:23]  - Male hours opportunity (7 params)
    [23:30]  - Female hours opportunity (7 params)
    [30:36]  - Male wage opportunity (6 params, vw only)
    [36:42]  - Female wage opportunity (6 params, vw only)
    
    Parameters
    ----------
    theta : np.ndarray
        Parameter vector (30 for fw, 42 for vw)
    data : PrecomputedDataCouples
        Pre-extracted arrays
    wage_spec : str
        "fw" or "vw"
    
    Returns
    -------
    Tuple[float, np.ndarray]
        (-LL, -gradient) for minimization
    """
    n = len(data.c)
    n_params = 42 if wage_spec == "vw" else 30
    
    # -------------------------------------------------------------------------
    # Unpack theta - SIMPLIFIED STRUCTURE
    # -------------------------------------------------------------------------
    # Male leisure preferences [0:6]
    beta_lm0 = theta[0]
    beta_lm_age_norm = theta[1]
    beta_lm_age_norm2 = theta[2]
    beta_lm_n_children = theta[3]
    beta_lm_educL = theta[4]
    beta_lm_educH = theta[5]
    
    # Female leisure preferences [6:12]
    beta_lf0 = theta[6]
    beta_lf_age_norm = theta[7]
    beta_lf_age_norm2 = theta[8]
    beta_lf_n_children = theta[9]
    beta_lf_educL = theta[10]
    beta_lf_educH = theta[11]
    
    # Shared params [12:16]
    beta_c = theta[12]
    theta_lm = theta[13]
    theta_lf = theta[14]
    theta_c = theta[15]
    
    # Male hours opportunity [16:23]
    beta_work_m = theta[16]
    beta_pt1_m = theta[17]
    beta_pt2_m = theta[18]
    beta_ft_m = theta[19]
    beta_gsur_m = theta[20]
    beta_work_educL_m = theta[21]
    beta_work_educH_m = theta[22]
    
    # Female hours opportunity [23:30]
    beta_work_f = theta[23]
    beta_pt1_f = theta[24]
    beta_pt2_f = theta[25]
    beta_ft_f = theta[26]
    beta_gsur_f = theta[27]
    beta_work_educL_f = theta[28]
    beta_work_educH_f = theta[29]
    
    # -------------------------------------------------------------------------
    # Box-Cox transforms (computed ONCE)
    # -------------------------------------------------------------------------
    lm_bc = _fast_boxcox(data.l_m, theta_lm)
    lf_bc = _fast_boxcox(data.l_f, theta_lf)
    c_bc = _fast_boxcox(data.c, theta_c)
    dlm_bc_dtheta = _fast_d_boxcox_dtheta(data.l_m, theta_lm)
    dlf_bc_dtheta = _fast_d_boxcox_dtheta(data.l_f, theta_lf)
    dc_bc_dtheta = _fast_d_boxcox_dtheta(data.c, theta_c)
    
    # -------------------------------------------------------------------------
    # Utility computation (SIMPLIFIED)
    # -------------------------------------------------------------------------
    beta_leisure_m = (
        beta_lm0
        + beta_lm_age_norm * data.age_norm_m
        + beta_lm_age_norm2 * data.age_norm2_m
        + beta_lm_n_children * data.n_children
        + beta_lm_educL * data.educL_m
        + beta_lm_educH * data.educH_m
    )
    
    beta_leisure_f = (
        beta_lf0
        + beta_lf_age_norm * data.age_norm_f
        + beta_lf_age_norm2 * data.age_norm2_f
        + beta_lf_n_children * data.n_children
        + beta_lf_educL * data.educL_f
        + beta_lf_educH * data.educH_f
    )
    
    u = beta_leisure_m * lm_bc + beta_leisure_f * lf_bc + beta_c * c_bc
    
    # -------------------------------------------------------------------------
    # Utility derivatives (16 params)
    # -------------------------------------------------------------------------
    du_dtheta = np.empty((n, 16), dtype=np.float64)
    
    # Male leisure params [0:6]
    du_dtheta[:, 0] = lm_bc                          # beta_lm0
    du_dtheta[:, 1] = data.age_norm_m * lm_bc        # beta_lm_age_norm
    du_dtheta[:, 2] = data.age_norm2_m * lm_bc       # beta_lm_age_norm2
    du_dtheta[:, 3] = data.n_children * lm_bc        # beta_lm_n_children
    du_dtheta[:, 4] = data.educL_m * lm_bc           # beta_lm_educL
    du_dtheta[:, 5] = data.educH_m * lm_bc           # beta_lm_educH
    
    # Female leisure params [6:12]
    du_dtheta[:, 6] = lf_bc                          # beta_lf0
    du_dtheta[:, 7] = data.age_norm_f * lf_bc        # beta_lf_age_norm
    du_dtheta[:, 8] = data.age_norm2_f * lf_bc       # beta_lf_age_norm2
    du_dtheta[:, 9] = data.n_children * lf_bc        # beta_lf_n_children
    du_dtheta[:, 10] = data.educL_f * lf_bc          # beta_lf_educL
    du_dtheta[:, 11] = data.educH_f * lf_bc          # beta_lf_educH
    
    # Shared params [12:16]
    du_dtheta[:, 12] = c_bc                          # beta_c
    du_dtheta[:, 13] = beta_leisure_m * dlm_bc_dtheta  # theta_lm
    du_dtheta[:, 14] = beta_leisure_f * dlf_bc_dtheta  # theta_lf
    du_dtheta[:, 15] = beta_c * dc_bc_dtheta           # theta_c
    
    # -------------------------------------------------------------------------
    # Hours opportunity density (SIMPLIFIED - no region)
    # -------------------------------------------------------------------------
    h_opp_m = (
        beta_work_m * data.working_m
        + beta_pt1_m * data.working_pt1_m
        + beta_pt2_m * data.working_pt2_m
        + beta_ft_m * data.working_ft_m
        + beta_gsur_m * data.working_m * data.gsur_m
        + beta_work_educL_m * data.working_m * data.educL_m
        + beta_work_educH_m * data.working_m * data.educH_m
    )
    
    h_opp_f = (
        beta_work_f * data.working_f
        + beta_pt1_f * data.working_pt1_f
        + beta_pt2_f * data.working_pt2_f
        + beta_ft_f * data.working_ft_f
        + beta_gsur_f * data.working_f * data.gsur_f
        + beta_work_educL_f * data.working_f * data.educL_f
        + beta_work_educH_f * data.working_f * data.educH_f
    )
    
    h_opp = h_opp_m + h_opp_f
    
    # Hours opp derivatives (14 params: 7 male + 7 female)
    dh_dtheta = np.empty((n, 14), dtype=np.float64)
    # Male hopp [0:7]
    dh_dtheta[:, 0] = data.working_m
    dh_dtheta[:, 1] = data.working_pt1_m
    dh_dtheta[:, 2] = data.working_pt2_m
    dh_dtheta[:, 3] = data.working_ft_m
    dh_dtheta[:, 4] = data.working_m * data.gsur_m
    dh_dtheta[:, 5] = data.working_m * data.educL_m
    dh_dtheta[:, 6] = data.working_m * data.educH_m
    # Female hopp [7:14]
    dh_dtheta[:, 7] = data.working_f
    dh_dtheta[:, 8] = data.working_pt1_f
    dh_dtheta[:, 9] = data.working_pt2_f
    dh_dtheta[:, 10] = data.working_ft_f
    dh_dtheta[:, 11] = data.working_f * data.gsur_f
    dh_dtheta[:, 12] = data.working_f * data.educL_f
    dh_dtheta[:, 13] = data.working_f * data.educH_f
    
    # -------------------------------------------------------------------------
    # Wage opportunity density (SIMPLIFIED - no region/year)
    # -------------------------------------------------------------------------
    if wage_spec == "vw" and len(theta) > 30:
        # Male wage params [30:36]
        w_beta0_m = theta[30]
        w_educL_m = theta[31]
        w_educH_m = theta[32]
        w_pexp_m = theta[33]
        w_pexp2_m = theta[34]
        sigma_m = abs(theta[35]) + 1e-6
        
        mean_logw_m = (
            w_beta0_m
            + w_educL_m * data.educL_m
            + w_educH_m * data.educH_m
            + w_pexp_m * data.pexp_m
            + w_pexp2_m * data.pexp2_m
        )
        z_m = (data.log_wage_m - mean_logw_m) / sigma_m
        w_opp_m = np.where(data.working_m > 0, 
                          -0.5 * z_m * z_m - np.log(sigma_m) - data.log_wage_m, 0.0)
        
        # Female wage params [36:42]
        w_beta0_f = theta[36]
        w_educL_f = theta[37]
        w_educH_f = theta[38]
        w_pexp_f = theta[39]
        w_pexp2_f = theta[40]
        sigma_f = abs(theta[41]) + 1e-6
        
        mean_logw_f = (
            w_beta0_f
            + w_educL_f * data.educL_f
            + w_educH_f * data.educH_f
            + w_pexp_f * data.pexp_f
            + w_pexp2_f * data.pexp2_f
        )
        z_f = (data.log_wage_f - mean_logw_f) / sigma_f
        w_opp_f = np.where(data.working_f > 0,
                          -0.5 * z_f * z_f - np.log(sigma_f) - data.log_wage_f, 0.0)
        
        w_opp = w_opp_m + w_opp_f
        
        # Wage derivatives (12 params: 6 male + 6 female)
        z_over_sigma_m = z_m / sigma_m
        z_over_sigma_f = z_f / sigma_f
        
        dw_dtheta = np.empty((n, 12), dtype=np.float64)
        # Male wopp [0:6]
        dw_dtheta[:, 0] = np.where(data.working_m > 0, z_over_sigma_m, 0.0)
        dw_dtheta[:, 1] = np.where(data.working_m > 0, z_over_sigma_m * data.educL_m, 0.0)
        dw_dtheta[:, 2] = np.where(data.working_m > 0, z_over_sigma_m * data.educH_m, 0.0)
        dw_dtheta[:, 3] = np.where(data.working_m > 0, z_over_sigma_m * data.pexp_m, 0.0)
        dw_dtheta[:, 4] = np.where(data.working_m > 0, z_over_sigma_m * data.pexp2_m, 0.0)
        dw_dtheta[:, 5] = np.where(data.working_m > 0, (z_m * z_m - 1.0) / sigma_m, 0.0)
        # Female wopp [6:12]
        dw_dtheta[:, 6] = np.where(data.working_f > 0, z_over_sigma_f, 0.0)
        dw_dtheta[:, 7] = np.where(data.working_f > 0, z_over_sigma_f * data.educL_f, 0.0)
        dw_dtheta[:, 8] = np.where(data.working_f > 0, z_over_sigma_f * data.educH_f, 0.0)
        dw_dtheta[:, 9] = np.where(data.working_f > 0, z_over_sigma_f * data.pexp_f, 0.0)
        dw_dtheta[:, 10] = np.where(data.working_f > 0, z_over_sigma_f * data.pexp2_f, 0.0)
        dw_dtheta[:, 11] = np.where(data.working_f > 0, (z_f * z_f - 1.0) / sigma_f, 0.0)
    else:
        w_opp = 0.0
        dw_dtheta = None
    
    # -------------------------------------------------------------------------
    # Composite V and dV/dtheta
    # -------------------------------------------------------------------------
    V = u + h_opp + w_opp - data.log_prior
    
    dV_dtheta = np.empty((n, n_params), dtype=np.float64)
    dV_dtheta[:, 0:16] = du_dtheta
    dV_dtheta[:, 16:30] = dh_dtheta
    if wage_spec == "vw" and dw_dtheta is not None:
        dV_dtheta[:, 30:42] = dw_dtheta
    
    # -------------------------------------------------------------------------
    # Softmax computation (ONCE for both LL and gradient)
    # -------------------------------------------------------------------------
    V_max_per_group = np.maximum.reduceat(V, data.group_starts)
    V_max = V_max_per_group[data.group_idx]
    
    exp_V_shifted = np.exp(V - V_max)
    sum_exp_per_group = np.bincount(data.group_idx, weights=exp_V_shifted, minlength=data.n_groups)
    
    # -------------------------------------------------------------------------
    # Log-likelihood
    # -------------------------------------------------------------------------
    log_sum_exp_per_group = V_max_per_group + np.log(sum_exp_per_group)
    V_obs = V[data.obs_indices]
    ll = np.sum(V_obs - log_sum_exp_per_group)
      # -------------------------------------------------------------------------
    # Gradient (reuses exp_V_shifted and sum_exp_per_group)
    # -------------------------------------------------------------------------
    sum_exp = sum_exp_per_group[data.group_idx]
    P = exp_V_shifted / sum_exp
    P_weighted_dV = P[:, None] * dV_dtheta
    
    E_dV_per_group = np.zeros((data.n_groups, n_params), dtype=np.float64)
    for k in range(n_params):
        E_dV_per_group[:, k] = np.bincount(data.group_idx, weights=P_weighted_dV[:, k], minlength=data.n_groups)
    E_dV = E_dV_per_group[data.group_idx, :]
    
    grad = (dV_dtheta[data.is_obs, :] - E_dV[data.is_obs, :]).sum(axis=0)
    
    return -ll, -grad


def fast_analytical_gradient_couples(
    theta: np.ndarray,
    data: PrecomputedDataCouples,
    wage_spec: str = "fw",
) -> np.ndarray:
    """
    FAST analytical gradient for couples using precomputed data.
    
    This is a convenience wrapper around fast_neg_ll_with_grad_couples
    that returns just the gradient (not negated).
    
    Parameters
    ----------
    theta : np.ndarray
        Parameter vector (30 for fw, 42 for vw)
    data : PrecomputedDataCouples
        Pre-extracted arrays
    wage_spec : str
        "fw" or "vw"
    
    Returns
    -------
    grad : np.ndarray
        Gradient of log-likelihood (positive for maximization)
    """
    _, neg_grad = fast_neg_ll_with_grad_couples(theta, data, wage_spec)
    return -neg_grad  # Return positive gradient for maximization


def fast_analytical_gradient_numba(
    theta: np.ndarray,
    data: PrecomputedDataSingles,
    is_male: bool = True,
    wage_spec: str = "fw",
) -> np.ndarray:
    """
    FASTEST gradient using Numba JIT-compiled softmax computation.
    
    Uses _compute_softmax_gradient_numba for the final aggregation step,
    which runs in parallel across all CPU cores.
    
    Falls back to fast_analytical_gradient_singles if Numba not available.
    
    SIMPLIFIED PARAMETER STRUCTURE (22 params for vw, 16 for fw):
    - Preferences (9): beta_l0, beta_l_age_norm, beta_l_age_norm2, 
      beta_l_n_children, beta_l_educL, beta_l_educH, beta_c, theta_l, theta_c
    - Hours opp (7): beta_work, beta_pt1, beta_pt2, beta_ft, 
      beta_gsur, beta_work_educL, beta_work_educH
    - Wage opp (6, vw only): beta0, beta_educL, beta_educH, beta_pexp, 
      beta_pexp2, sigma
    """
    if not NUMBA_AVAILABLE or _compute_softmax_gradient_numba is None:
        return fast_analytical_gradient_singles(theta, data, is_male, wage_spec)
    
    n = len(data.c)
    n_params = 22 if wage_spec == "vw" else 16
    
    # Unpack theta - SIMPLIFIED STRUCTURE
    # Preferences (9 params)
    beta_l0 = theta[0]
    beta_l_age_norm = theta[1]
    beta_l_age_norm2 = theta[2]
    beta_l_n_children = theta[3]
    beta_l_educL = theta[4]
    beta_l_educH = theta[5]
    beta_c = theta[6]
    theta_l = theta[7]
    theta_c = theta[8]
    
    # Hours opportunity (7 params)
    beta_work = theta[9]
    beta_pt1 = theta[10]
    beta_pt2 = theta[11]
    beta_ft = theta[12]
    beta_gsur = theta[13]
    beta_work_educL = theta[14]
    beta_work_educH = theta[15]
    
    # Box-Cox transforms
    l_bc = _fast_boxcox(data.l, theta_l)
    c_bc = _fast_boxcox(data.c, theta_c)
    dl_bc_dtheta_l = _fast_d_boxcox_dtheta(data.l, theta_l)
    dc_bc_dtheta_c = _fast_d_boxcox_dtheta(data.c, theta_c)
    
    beta_leisure = (
        beta_l0
        + beta_l_age_norm * data.age_norm
        + beta_l_age_norm2 * data.age_norm2
        + beta_l_n_children * data.n_children
        + beta_l_educL * data.educL
        + beta_l_educH * data.educH
    )
    
    u = beta_leisure * l_bc + beta_c * c_bc
    
    # Preference derivatives (9 params)
    du_dtheta = np.zeros((n, 9), dtype=np.float64)
    du_dtheta[:, 0] = l_bc                           # beta_l0
    du_dtheta[:, 1] = data.age_norm * l_bc           # beta_l_age_norm
    du_dtheta[:, 2] = data.age_norm2 * l_bc          # beta_l_age_norm2
    du_dtheta[:, 3] = data.n_children * l_bc         # beta_l_n_children
    du_dtheta[:, 4] = data.educL * l_bc              # beta_l_educL
    du_dtheta[:, 5] = data.educH * l_bc              # beta_l_educH
    du_dtheta[:, 6] = c_bc                           # beta_c
    du_dtheta[:, 7] = beta_leisure * dl_bc_dtheta_l  # theta_l
    du_dtheta[:, 8] = beta_c * dc_bc_dtheta_c        # theta_c
    
    # Hours opportunity (7 params, no region interactions)
    h_opp = (
        beta_work * data.working
        + beta_pt1 * data.working_pt1
        + beta_pt2 * data.working_pt2
        + beta_ft * data.working_ft
        + beta_gsur * data.working * data.gsur
        + beta_work_educL * data.working * data.educL
        + beta_work_educH * data.working * data.educH
    )
    
    dh_dtheta = np.zeros((n, 7), dtype=np.float64)
    dh_dtheta[:, 0] = data.working                   # beta_work
    dh_dtheta[:, 1] = data.working_pt1               # beta_pt1
    dh_dtheta[:, 2] = data.working_pt2               # beta_pt2
    dh_dtheta[:, 3] = data.working_ft                # beta_ft
    dh_dtheta[:, 4] = data.working * data.gsur       # beta_gsur
    dh_dtheta[:, 5] = data.working * data.educL      # beta_work_educL
    dh_dtheta[:, 6] = data.working * data.educH      # beta_work_educH
    
    # Wage opportunity (6 params, vw only - no region/year)
    if wage_spec == "vw":
        w_beta0 = theta[16]
        w_educL = theta[17]
        w_educH = theta[18]
        w_pexp = theta[19]
        w_pexp2 = theta[20]
        sigma = abs(theta[21]) + 1e-6
        
        mean_logw = (
            w_beta0
            + w_educL * data.educL
            + w_educH * data.educH
            + w_pexp * data.pexp
            + w_pexp2 * data.pexp2
        )
        
        z = (data.log_wage - mean_logw) / sigma
        w_opp = np.where(data.working > 0, -0.5 * z * z - np.log(sigma) - data.log_wage, 0.0)
        
        z_over_sigma = z / sigma
        dw_dtheta = np.zeros((n, 6), dtype=np.float64)
        dw_dtheta[:, 0] = z_over_sigma               # w_beta0
        dw_dtheta[:, 1] = z_over_sigma * data.educL  # w_educL
        dw_dtheta[:, 2] = z_over_sigma * data.educH  # w_educH
        dw_dtheta[:, 3] = z_over_sigma * data.pexp   # w_pexp
        dw_dtheta[:, 4] = z_over_sigma * data.pexp2  # w_pexp2
        dw_dtheta[:, 5] = (z * z - 1.0) / sigma      # sigma
        dw_dtheta = np.where(data.working[:, None] > 0, dw_dtheta, 0.0)
    else:
        w_opp = 0.0
        dw_dtheta = np.zeros((n, 6), dtype=np.float64)
    
    # Composite V and dV/dtheta
    V = u + h_opp + w_opp - data.log_prior
    
    dV_dtheta = np.zeros((n, n_params), dtype=np.float64)
    dV_dtheta[:, 0:9] = du_dtheta         # Preferences (9 params)
    dV_dtheta[:, 9:16] = dh_dtheta        # Hours opp (7 params)
    if wage_spec == "vw":
        dV_dtheta[:, 16:22] = dw_dtheta   # Wage opp (6 params)
    
    # Use Numba-accelerated softmax gradient (parallel across groups)
    grad = _compute_softmax_gradient_numba(
        np.ascontiguousarray(V),
        np.ascontiguousarray(dV_dtheta),
        data.group_starts,
        data.group_ends,
        data.obs_indices,
    )
    
    return grad


def fast_neg_ll_with_grad_numba(
    theta: np.ndarray,
    data: PrecomputedDataSingles,
    is_male: bool = True,
    wage_spec: str = "fw",
) -> Tuple[float, np.ndarray]:
    """
    Fast negative log-likelihood and gradient with Numba acceleration.
    
    Uses Numba JIT for log-likelihood computation (30x faster than Python loops).
    Uses NumPy vectorized operations for gradient (faster than Numba for matrix ops).
    
    Falls back to pure NumPy version if Numba not available.
    
    SIMPLIFIED PARAMETER STRUCTURE (22 params for vw, 16 for fw):
    - Preferences (9): beta_l0, beta_l_age_norm, beta_l_age_norm2, 
      beta_l_n_children, beta_l_educL, beta_l_educH, beta_c, theta_l, theta_c
    - Hours opp (7): beta_work, beta_pt1, beta_pt2, beta_ft, 
      beta_gsur, beta_work_educL, beta_work_educH
    - Wage opp (6, vw only): beta0, beta_educL, beta_educH, beta_pexp, 
      beta_pexp2, sigma
    """
    if NUMBA_AVAILABLE and _compute_log_likelihood_numba is not None:
        # Compute V once - SIMPLIFIED STRUCTURE
        n = len(data.c)
        
        # Preferences (9 params)
        beta_l0 = theta[0]
        beta_l_age_norm = theta[1]
        beta_l_age_norm2 = theta[2]
        beta_l_n_children = theta[3]
        beta_l_educL = theta[4]
        beta_l_educH = theta[5]
        beta_c = theta[6]
        theta_l = theta[7]
        theta_c = theta[8]
        
        l_bc = _fast_boxcox(data.l, theta_l)
        c_bc = _fast_boxcox(data.c, theta_c)
        
        beta_leisure = (
            beta_l0
            + beta_l_age_norm * data.age_norm
            + beta_l_age_norm2 * data.age_norm2
            + beta_l_n_children * data.n_children
            + beta_l_educL * data.educL
            + beta_l_educH * data.educH
        )
        
        u = beta_leisure * l_bc + beta_c * c_bc
        
        # Hours opp (7 params)
        beta_work = theta[9]
        beta_pt1 = theta[10]
        beta_pt2 = theta[11]
        beta_ft = theta[12]
        beta_gsur = theta[13]
        beta_work_educL = theta[14]
        beta_work_educH = theta[15]
        
        h_opp = (
            beta_work * data.working
            + beta_pt1 * data.working_pt1
            + beta_pt2 * data.working_pt2
            + beta_ft * data.working_ft
            + beta_gsur * data.working * data.gsur
            + beta_work_educL * data.working * data.educL
            + beta_work_educH * data.working * data.educH
        )
        
        # Wage opp (6 params, vw only)
        if wage_spec == "vw":
            w_beta0 = theta[16]
            w_educL = theta[17]
            w_educH = theta[18]
            w_pexp = theta[19]
            w_pexp2 = theta[20]
            sigma = abs(theta[21]) + 1e-6
            
            mean_logw = (
                w_beta0
                + w_educL * data.educL
                + w_educH * data.educH
                + w_pexp * data.pexp
                + w_pexp2 * data.pexp2
            )
            z = (data.log_wage - mean_logw) / sigma
            w_opp = np.where(data.working > 0, -0.5 * z * z - np.log(sigma) - data.log_wage, 0.0)
        else:
            w_opp = 0.0
        
        V = np.ascontiguousarray(u + h_opp + w_opp - data.log_prior)
        
        # Use Numba for LL (30x faster than Python loops)
        ll = _compute_log_likelihood_numba(V, data.group_starts, data.group_ends, data.obs_indices)
        
        # Use NumPy for gradient (faster than Numba for matrix ops)
        grad = fast_analytical_gradient_singles(theta, data, is_male, wage_spec)
        
        return -ll, -grad
    else:
        return fast_neg_ll_with_grad_singles(theta, data, is_male, wage_spec)


# =============================================================================
# JOINT ESTIMATION (all groups with shared opportunity parameters)
# =============================================================================
"""
1. PREFERENCES are GROUP-SPECIFIC:
   - Single males: 12 preference parameters
   - Single females: 12 preference parameters (13 with children0_3)
   - Couples: 25 preference parameters (male leisure, female leisure, consumption, interaction)

2. OPPORTUNITY DENSITIES are SHARED BY GENDER:
   - Hours opportunity for males: Used by single males AND male partners in couples
   - Hours opportunity for females: Used by single females AND female partners in couples
   - Wage opportunity for males: Shared across single males and male partners
   - Wage opportunity for females: Shared across single females and female partners

This makes economic sense: the labor market doesn't care if you're single or married.
"""

# NOTE: PrefParamsCouples is defined at line ~868 with the SIMPLIFIED structure
# (age_norm, n_children, no regions). Do NOT duplicate it here.


def get_n_params_joint(wage_spec: str = "fw") -> Dict[str, int]:
    """
    Get parameter counts for joint estimation.
    
    SIMPLIFIED Parameters are structured as:
    - Preferences (group-specific): sm(9) + sf(9) + couples(16) = 34
    - Hours opportunity (gender-specific): male(7) + female(7) = 14
    - Wage opportunity (gender-specific, vw only): male(6) + female(6) = 12
    
    Total: 34 + 14 = 48 (fw) or 34 + 14 + 12 = 60 (vw)
    
    NOTE: Joint estimation may need further work to properly share parameters
    across groups. For now, use standalone estimation for singles/couples.
    """
    n_pref_sm = 9       # single males preferences (simplified)
    n_pref_sf = 9       # single females preferences (simplified, same as males)
    n_pref_cou = 16     # couples preferences (simplified)
    n_hopp_m = 7        # hours opportunity (males, no region)
    n_hopp_f = 7        # hours opportunity (females, no region)
    n_wopp_m = 6        # wage opportunity (males, no region/year)
    n_wopp_f = 6        # wage opportunity (females, no region/year)
    
    n_pref = n_pref_sm + n_pref_sf + n_pref_cou
    n_hopp = n_hopp_m + n_hopp_f
    n_wopp = n_wopp_m + n_wopp_f if wage_spec == "vw" else 0
    
    return {
        "n_pref_sm": n_pref_sm,
        "n_pref_sf": n_pref_sf,
        "n_pref_cou": n_pref_cou,
        "n_pref": n_pref,
        "n_hopp_m": n_hopp_m,
        "n_hopp_f": n_hopp_f,
        "n_hopp": n_hopp,
        "n_wopp_m": n_wopp_m,
        "n_wopp_f": n_wopp_f,
        "n_wopp": n_wopp,
        "total": n_pref + n_hopp + n_wopp,
    }


def get_initial_theta_joint(wage_spec: str = "fw") -> np.ndarray:
    """
    Get initial parameter values for joint estimation.
    
    SIMPLIFIED Parameter layout:
    [0:9]    - Single males preferences (9)
    [9:18]   - Single females preferences (9)
    [18:34]  - Couples preferences (16)
    [34:41]  - Hours opportunity (males, 7)
    [41:48]  - Hours opportunity (females, 7)
    [48:54]  - Wage opportunity (males, 6, vw only)
    [54:60]  - Wage opportunity (females, 6, vw only)
    
    Total: 48 (fw) or 60 (vw)
    """
    # Single males preferences (9) - SIMPLIFIED
    pref_sm = [
        1.0,   # beta_l0
        0.0,   # beta_l_age_norm
        0.0,   # beta_l_age_norm2
        0.0,   # beta_l_n_children
        0.0,   # beta_l_educL
        0.0,   # beta_l_educH
        1.0,   # beta_c
        0.5,   # theta_l
        0.5,   # theta_c
    ]
    
    # Single females preferences (9) - SIMPLIFIED (same structure as males)
    pref_sf = [
        1.0,   # beta_l0
        0.0,   # beta_l_age_norm
        0.0,   # beta_l_age_norm2
        0.2,   # beta_l_n_children (stronger for females)
        0.0,   # beta_l_educL
        0.0,   # beta_l_educH
        1.0,   # beta_c
        0.5,   # theta_l
        0.5,   # theta_c
    ]
    
    # Couples preferences (16) - SIMPLIFIED
    pref_cou = [
        # Male leisure (6)
        1.0,   # beta_l0_m
        0.0,   # beta_l_age_norm_m
        0.0,   # beta_l_age_norm2_m
        0.0,   # beta_l_n_children_m
        0.0,   # beta_l_educL_m
        0.0,   # beta_l_educH_m
        # Female leisure (6)
        1.0,   # beta_l0_f
        0.0,   # beta_l_age_norm_f
        0.0,   # beta_l_age_norm2_f
        0.2,   # beta_l_n_children_f
        0.0,   # beta_l_educL_f
        0.0,   # beta_l_educH_f
        # Shared (4)
        1.0,   # beta_c
        0.5,   # theta_l_m
        0.5,   # theta_l_f
        0.5,   # theta_c
    ]
    
    # Hours opportunity - males (7) - SIMPLIFIED (no region)
    hopp_m = [
        0.5,   # beta_work
        0.0,   # beta_pt1
        0.0,   # beta_pt2
        0.0,   # beta_ft
        0.0,   # beta_gsur
        0.0,   # beta_work_educL
        0.0,   # beta_work_educH
    ]
    
    # Hours opportunity - females (7) - SIMPLIFIED (no region)
    hopp_f = [
        0.5,   # beta_work
        0.0,   # beta_pt1
        0.0,   # beta_pt2
        0.0,   # beta_ft
        0.0,   # beta_gsur
        0.0,   # beta_work_educL
        0.0,   # beta_work_educH
    ]
    
    theta = pref_sm + pref_sf + pref_cou + hopp_m + hopp_f
    
    if wage_spec == "vw":
        # Wage opportunity - males (6) - SIMPLIFIED (no region/year)
        wopp_m = [
            2.5,    # beta0
            -0.1,   # beta_educL
            0.2,    # beta_educH
            0.02,   # beta_pexp
            -0.001, # beta_pexp2
            0.4,    # sigma
        ]
        
        # Wage opportunity - females (6) - SIMPLIFIED (no region/year)
        wopp_f = [
            2.3,    # beta0 (typically lower)
            -0.1,   # beta_educL
            0.2,    # beta_educH
            0.02,   # beta_pexp
            -0.001, # beta_pexp2
            0.4,    # sigma
        ]
        
        theta = theta + wopp_m + wopp_f
    
    return np.array(theta)


def get_param_names_joint(wage_spec: str = "fw") -> List[str]:
    """Return parameter names for joint estimation - SIMPLIFIED."""
    names = []
    
    # Single males preferences (9)
    names += [
        "sm.pref.beta_l0", "sm.pref.beta_l_age_norm", "sm.pref.beta_l_age_norm2",
        "sm.pref.beta_l_n_children",
        "sm.pref.beta_l_educL", "sm.pref.beta_l_educH",
        "sm.pref.beta_c", "sm.pref.theta_l", "sm.pref.theta_c",
    ]
    
    # Single females preferences (9)
    names += [
        "sf.pref.beta_l0", "sf.pref.beta_l_age_norm", "sf.pref.beta_l_age_norm2",
        "sf.pref.beta_l_n_children",
        "sf.pref.beta_l_educL", "sf.pref.beta_l_educH",
        "sf.pref.beta_c", "sf.pref.theta_l", "sf.pref.theta_c",
    ]
    
    # Couples preferences (16)
    names += [
        # Male (6)
        "cou.pref.beta_l0_m", "cou.pref.beta_l_age_norm_m", "cou.pref.beta_l_age_norm2_m",
        "cou.pref.beta_l_n_children_m", "cou.pref.beta_l_educL_m", "cou.pref.beta_l_educH_m",
        # Female (6)
        "cou.pref.beta_l0_f", "cou.pref.beta_l_age_norm_f", "cou.pref.beta_l_age_norm2_f",
        "cou.pref.beta_l_n_children_f", "cou.pref.beta_l_educL_f", "cou.pref.beta_l_educH_f",
        # Shared (4)
        "cou.pref.beta_c", "cou.pref.theta_l_m", "cou.pref.theta_l_f", "cou.pref.theta_c",
    ]
    
    # Hours opportunity - males (7)
    names += [
        "hopp_m.beta_work", "hopp_m.beta_pt1", "hopp_m.beta_pt2", "hopp_m.beta_ft",
        "hopp_m.beta_gsur", "hopp_m.beta_work_educL", "hopp_m.beta_work_educH",
    ]
    
    # Hours opportunity - females (7)
    names += [
        "hopp_f.beta_work", "hopp_f.beta_pt1", "hopp_f.beta_pt2", "hopp_f.beta_ft",
        "hopp_f.beta_gsur", "hopp_f.beta_work_educL", "hopp_f.beta_work_educH",
    ]
    
    if wage_spec == "vw":
        # Wage opportunity - males (6)
        names += [
            "wopp_m.beta0", "wopp_m.beta_educL", "wopp_m.beta_educH",
            "wopp_m.beta_pexp", "wopp_m.beta_pexp2", "wopp_m.sigma",
        ]
        
        # Wage opportunity - females (6)
        names += [
            "wopp_f.beta0", "wopp_f.beta_educL", "wopp_f.beta_educH",
            "wopp_f.beta_pexp", "wopp_f.beta_pexp2", "wopp_f.sigma",
        ]
    
    return names


def _extract_group_params_from_joint(
    theta_joint: np.ndarray,
    group: str,
    wage_spec: str = "fw",
) -> np.ndarray:
    """
    Extract parameters for a specific group from the joint theta vector.
    
    For singles, this returns the preference + gender-specific opportunity params.
    For couples, returns couples preferences + both genders' opportunity params.
    
    SIMPLIFIED Parameter layout in theta_joint:
    [0:9]    - Single males preferences (9)
    [9:18]   - Single females preferences (9)
    [18:34]  - Couples preferences (16)
    [34:41]  - Hours opportunity (males, 7)
    [41:48]  - Hours opportunity (females, 7)
    [48:54]  - Wage opportunity (males, 6, vw only)
    [54:60]  - Wage opportunity (females, 6, vw only)
    
    Parameters
    ----------
    theta_joint : np.ndarray
        Full joint parameter vector (48 fw, 60 vw)
    group : str
        One of "sm" (single males), "sf" (single females), "cou" (couples)
    wage_spec : str
        "fw" or "vw"
    
    Returns
    -------
    theta_group : np.ndarray
        Parameters for the specified group in the format expected by
        the singles/couples likelihood functions.
    """
    # Index boundaries in joint theta - SIMPLIFIED
    idx_pref_sm_start = 0
    idx_pref_sm_end = 9
    idx_pref_sf_start = 9
    idx_pref_sf_end = 18
    idx_pref_cou_start = 18
    idx_pref_cou_end = 34
    idx_hopp_m_start = 34
    idx_hopp_m_end = 41
    idx_hopp_f_start = 41
    idx_hopp_f_end = 48
    
    if wage_spec == "vw":
        idx_wopp_m_start = 48
        idx_wopp_m_end = 54
        idx_wopp_f_start = 54
        idx_wopp_f_end = 60
    
    if group == "sm":
        # Single males: preferences(9) + hopp_m(7) + wopp_m(6 if vw)
        pref = theta_joint[idx_pref_sm_start:idx_pref_sm_end]
        hopp = theta_joint[idx_hopp_m_start:idx_hopp_m_end]
        result = np.concatenate([pref, hopp])
        if wage_spec == "vw":
            wopp = theta_joint[idx_wopp_m_start:idx_wopp_m_end]
            result = np.concatenate([result, wopp])
        return result
        
    elif group == "sf":
        # Single females: preferences(9) + hopp_f(7) + wopp_f(6 if vw)
        pref = theta_joint[idx_pref_sf_start:idx_pref_sf_end]
        hopp = theta_joint[idx_hopp_f_start:idx_hopp_f_end]
        result = np.concatenate([pref, hopp])
        if wage_spec == "vw":
            wopp = theta_joint[idx_wopp_f_start:idx_wopp_f_end]
            result = np.concatenate([result, wopp])
        return result
        
    elif group == "cou":
        # Couples need all: preferences(16) + hopp_m(7) + hopp_f(7) + wopp_m(6) + wopp_f(6)
        pref = theta_joint[idx_pref_cou_start:idx_pref_cou_end]
        hopp_m = theta_joint[idx_hopp_m_start:idx_hopp_m_end]
        hopp_f = theta_joint[idx_hopp_f_start:idx_hopp_f_end]
        result = np.concatenate([pref, hopp_m, hopp_f])
        if wage_spec == "vw":
            wopp_m = theta_joint[idx_wopp_m_start:idx_wopp_m_end]
            wopp_f = theta_joint[idx_wopp_f_start:idx_wopp_f_end]
            result = np.concatenate([result, wopp_m, wopp_f])
        return result
    
    else:
        raise ValueError(f"Unknown group: {group}")


def unpack_theta_couples(theta: np.ndarray, wage_spec: str = "fw") -> Tuple:
    """
    Unpack couples parameter vector into component dataclasses.
    
    SIMPLIFIED Parameter layout (30 for fw, 42 for vw):
    [0:6]    - Male leisure preferences (6 params)
    [6:12]   - Female leisure preferences (6 params)
    [12:16]  - Shared: beta_c, theta_lm, theta_lf, theta_c
    [16:23]  - Male hours opportunity (7 params)
    [23:30]  - Female hours opportunity (7 params)
    [30:36]  - Male wage opportunity (6 params, vw only)
    [36:42]  - Female wage opportunity (6 params, vw only)
    
    Returns
    -------
    pref : PrefParamsCouples
    hopp_m : HoursOppParams
    hopp_f : HoursOppParams
    wopp_m : WageOppParams (or default for fw)
    wopp_f : WageOppParams (or default for fw)
    """
    # Preferences (16 params total)
    pref = PrefParamsCouples(
        # Male leisure (6) [0:6]
        beta_lm0=theta[0],
        beta_lm_age_norm=theta[1],
        beta_lm_age_norm2=theta[2],
        beta_lm_n_children=theta[3],
        beta_lm_educL=theta[4],
        beta_lm_educH=theta[5],
        # Female leisure (6) [6:12]
        beta_lf0=theta[6],
        beta_lf_age_norm=theta[7],
        beta_lf_age_norm2=theta[8],
        beta_lf_n_children=theta[9],
        beta_lf_educL=theta[10],
        beta_lf_educH=theta[11],
        # Shared (4) [12:16]
        beta_c=theta[12],
        theta_lm=theta[13],
        theta_lf=theta[14],
        theta_c=theta[15],
    )
    
    # Hours opportunity - male (7 params: indices 16-22)
    hopp_m = HoursOppParams(
        beta_work=theta[16],
        beta_pt1=theta[17],
        beta_pt2=theta[18],
        beta_ft=theta[19],
        beta_gsur=theta[20],
        beta_work_educL=theta[21],
        beta_work_educH=theta[22],
    )
    
    # Hours opportunity - female (7 params: indices 23-29)
    hopp_f = HoursOppParams(
        beta_work=theta[23],
        beta_pt1=theta[24],
        beta_pt2=theta[25],
        beta_ft=theta[26],
        beta_gsur=theta[27],
        beta_work_educL=theta[28],
        beta_work_educH=theta[29],
    )
    
    if wage_spec == "vw":
        # Wage opportunity - male (6 params: indices 30-35)
        wopp_m = WageOppParams(
            beta0=theta[30],
            beta_educL=theta[31],
            beta_educH=theta[32],
            beta_pexp=theta[33],
            beta_pexp2=theta[34],
            sigma=theta[35],
        )
        
        # Wage opportunity - female (6 params: indices 36-41)
        wopp_f = WageOppParams(
            beta0=theta[36],
            beta_educL=theta[37],
            beta_educH=theta[38],
            beta_pexp=theta[39],
            beta_pexp2=theta[40],
            sigma=theta[41],
        )
    else:
        wopp_m = WageOppParams()
        wopp_f = WageOppParams()
    
    return pref, hopp_m, hopp_f, wopp_m, wopp_f


def log_likelihood_couples(
    theta: np.ndarray,
    df: pd.DataFrame,
    wage_spec: str = "fw",
) -> float:
    """
    Compute total log-likelihood for couples.
    
    The likelihood for couples follows the same MNL structure as singles,
    but with joint utility over both partners' labor supply.
    
    SIMPLIFIED Parameter layout (30 for fw, 42 for vw):
    [0:6]    - Male leisure preferences (6 params)
    [6:12]   - Female leisure preferences (6 params)
    [12:16]  - Shared: beta_c, theta_lm, theta_lf, theta_c
    [16:23]  - Male hours opportunity (7 params)
    [23:30]  - Female hours opportunity (7 params)
    [30:36]  - Male wage opportunity (6 params, vw only)
    [36:42]  - Female wage opportunity (6 params, vw only)
    
    Parameters
    ----------
    theta : np.ndarray
        Flat parameter vector for couples (30 for fw, 42 for vw)
    df : pd.DataFrame
        Long-format RURO-MNL dataset for couples.
    wage_spec : str
        "fw" or "vw"
    
    Returns
    -------
    ll : float
        Total log-likelihood.
    """
    n = len(df)
    if n == 0:
        return 0.0
    
    # Unpack parameters
    pref, hopp_m, hopp_f, wopp_m, wopp_f = unpack_theta_couples(theta, wage_spec)
    
    # Building blocks
    u = ff_calc_util_couples(df, pref)
    h_opp = ff_calc_hopp_couples(df, hopp_m, hopp_f)
    
    if wage_spec == "vw":
        w_opp = ff_calc_wopp_couples(df, wopp_m, wopp_f)
    else:
        w_opp = np.zeros(n)
    
    # Prior
    prior_col = df.get("prior", None)
    if prior_col is not None:
        log_prior = pd.to_numeric(prior_col, errors="coerce").fillna(0).to_numpy()
    else:
        log_prior = np.zeros(n)
    
    # Composite index: V = u + h_opp + w_opp - log_prior
    V = u + h_opp + w_opp - log_prior
    
    # Get individual/household IDs
    if "idhh_true" in df.columns:
        ids = df["idhh_true"].to_numpy()
    elif "idhh" in df.columns:
        ids = df["idhh"].to_numpy()
    else:
        raise KeyError("Dataset must contain 'idhh_true' or 'idhh'.")
    
    draws = df["draw"].to_numpy()
    if "is_chosen" in df.columns:
        is_chosen = pd.to_numeric(df["is_chosen"], errors="coerce").fillna(0).to_numpy()
        is_obs = (is_chosen == 1) | (draws == 0)
    else:
        is_obs = (draws == 0)
    
    # Vectorized log-likelihood
    tmp = pd.DataFrame({"id": ids, "V": V, "is_obs": is_obs})
    tmp["V_max"] = tmp.groupby("id")["V"].transform("max")
    tmp["exp_V_shifted"] = np.exp(tmp["V"] - tmp["V_max"])
    tmp["sum_exp_V"] = tmp.groupby("id")["exp_V_shifted"].transform("sum")
    tmp["log_sum_exp"] = tmp["V_max"] + np.log(tmp["sum_exp_V"])
    tmp["log_prob"] = tmp["V"] - tmp["log_sum_exp"]
    
    ll = tmp.loc[tmp["is_obs"], "log_prob"].sum()
    
    return ll


def log_likelihood_joint(
    theta: np.ndarray,
    df_sm: pd.DataFrame,
    df_sf: pd.DataFrame,
    df_cou: pd.DataFrame,
    wage_spec: str = "fw",
) -> float:
    """
    Compute joint log-likelihood over all groups.
    
    LL_total = LL_sm + LL_sf + LL_cou
    
    Each group uses its own preference parameters but SHARES opportunity
    parameters by gender:
    - Single males share hopp_m and wopp_m with male partners in couples
    - Single females share hopp_f and wopp_f with female partners in couples
    """
    ll_total = 0.0
    
    # Single males
    if len(df_sm) > 0:
        theta_sm = _extract_group_params_from_joint(theta, "sm", wage_spec)
        ll_sm = log_likelihood_singles(theta_sm, df_sm, is_male=True, wage_spec=wage_spec)
        ll_total += ll_sm
    
    # Single females
    if len(df_sf) > 0:
        theta_sf = _extract_group_params_from_joint(theta, "sf", wage_spec)
        ll_sf = log_likelihood_singles(theta_sf, df_sf, is_male=False, wage_spec=wage_spec)
        ll_total += ll_sf
    
    # Couples - now properly implemented with joint utility
    if len(df_cou) > 0:
        theta_cou = _extract_group_params_from_joint(theta, "cou", wage_spec)
        ll_cou = log_likelihood_couples(theta_cou, df_cou, wage_spec=wage_spec)
        ll_total += ll_cou
    
    return ll_total


def neg_log_likelihood_joint(
    theta: np.ndarray,
    df_sm: pd.DataFrame,
    df_sf: pd.DataFrame,
    df_cou: pd.DataFrame,
    wage_spec: str = "fw",
) -> float:
    """Negative log-likelihood for joint estimation (for minimization)."""
    return -log_likelihood_joint(theta, df_sm, df_sf, df_cou, wage_spec)


def analytical_gradient_joint(
    theta: np.ndarray,
    df_sm: pd.DataFrame,
    df_sf: pd.DataFrame,
    df_cou: pd.DataFrame,
    wage_spec: str = "fw",
    use_parallel: bool = True,
    n_jobs: int = N_JOBS,
) -> np.ndarray:
    """
    Compute analytical gradient for joint estimation.
    
    The gradient has contributions from each group, with the opportunity
    parameters receiving gradients from multiple groups (shared by gender).
    
    Parameters
    ----------
    theta : np.ndarray
        Joint parameter vector
    df_sm, df_sf, df_cou : pd.DataFrame
        DataFrames for single males, single females, and couples
    wage_spec : str
        "fw" or "vw"
    use_parallel : bool
        If True and joblib is available, compute group gradients in parallel
    n_jobs : int
        Number of parallel jobs (default: N_JOBS based on CPU count)
    
    Returns
    -------
    grad : np.ndarray
        Gradient of log-likelihood w.r.t. joint theta
    """
    counts = get_n_params_joint(wage_spec)
    n_params = counts["total"]
    grad = np.zeros(n_params)
    
    # Index boundaries
    idx_pref_sm = (0, 12)
    idx_pref_sf = (12, 25)
    idx_pref_cou = (25, 50)
    idx_hopp_m = (50, 59)
    idx_hopp_f = (59, 68)
    
    if wage_spec == "vw":
        idx_wopp_m = (68, 84)
        idx_wopp_f = (84, 100)
    
    # Define helper functions for each group's gradient
    def compute_grad_sm():
        if len(df_sm) == 0:
            return None
        theta_sm = _extract_group_params_from_joint(theta, "sm", wage_spec)
        return analytical_gradient_singles(theta_sm, df_sm, is_male=True, wage_spec=wage_spec)
    
    def compute_grad_sf():
        if len(df_sf) == 0:
            return None
        theta_sf = _extract_group_params_from_joint(theta, "sf", wage_spec)
        return analytical_gradient_singles(theta_sf, df_sf, is_male=False, wage_spec=wage_spec)
    
    def compute_grad_cou():
        if len(df_cou) == 0:
            return None
        theta_cou = _extract_group_params_from_joint(theta, "cou", wage_spec)
        return analytical_gradient_couples(theta_cou, df_cou, wage_spec=wage_spec)
    
    # Compute gradients - parallel or sequential
    if use_parallel and JOBLIB_AVAILABLE and n_jobs > 1:
        # Parallel computation across groups
        results = Parallel(n_jobs=min(3, n_jobs), prefer="threads")(
            delayed(fn)() for fn in [compute_grad_sm, compute_grad_sf, compute_grad_cou]
        )
        grad_sm, grad_sf, grad_cou = results
    else:
        # Sequential computation
        grad_sm = compute_grad_sm()
        grad_sf = compute_grad_sf()
        grad_cou = compute_grad_cou()
    
    # Map single males gradient
    if grad_sm is not None:
        grad[idx_pref_sm[0]:idx_pref_sm[1]] += grad_sm[0:12]
        grad[idx_hopp_m[0]:idx_hopp_m[1]] += grad_sm[12:21]
        if wage_spec == "vw":
            grad[idx_wopp_m[0]:idx_wopp_m[1]] += grad_sm[21:37]
    
    # Map single females gradient
    if grad_sf is not None:
        grad[idx_pref_sf[0]:idx_pref_sf[0]+12] += grad_sf[0:12]
        grad[idx_hopp_f[0]:idx_hopp_f[1]] += grad_sf[12:21]
        if wage_spec == "vw":
            grad[idx_wopp_f[0]:idx_wopp_f[1]] += grad_sf[21:37]
    
    # Map couples gradient
    if grad_cou is not None:
        # Couples preferences: 25 params
        grad[idx_pref_cou[0]:idx_pref_cou[1]] += grad_cou[0:25]
        # Couples hopp_m: params 25-33 in grad_cou → indices 50-59 in grad
        grad[idx_hopp_m[0]:idx_hopp_m[1]] += grad_cou[25:34]
        # Couples hopp_f: params 34-42 in grad_cou → indices 59-68 in grad
        grad[idx_hopp_f[0]:idx_hopp_f[1]] += grad_cou[34:43]
        if wage_spec == "vw":
            # Couples wopp_m: params 43-58 in grad_cou → indices 68-84 in grad
            grad[idx_wopp_m[0]:idx_wopp_m[1]] += grad_cou[43:59]
            # Couples wopp_f: params 59-74 in grad_cou → indices 84-100 in grad
            grad[idx_wopp_f[0]:idx_wopp_f[1]] += grad_cou[59:75]
    
    return grad


def analytical_gradient_couples(
    theta: np.ndarray,
    df: pd.DataFrame,
    wage_spec: str = "fw",
) -> np.ndarray:
    """
    Compute analytical gradient of log-likelihood for couples.
    
    SIMPLIFIED Parameter layout (30 for fw, 42 for vw):
    [0:6]    - Male leisure preferences (6 params)
    [6:12]   - Female leisure preferences (6 params)
    [12:16]  - Shared: beta_c, theta_lm, theta_lf, theta_c
    [16:23]  - Male hours opportunity (7 params)
    [23:30]  - Female hours opportunity (7 params)
    [30:36]  - Male wage opportunity (6 params, vw only)
    [36:42]  - Female wage opportunity (6 params, vw only)
    
    Parameters
    ----------
    theta : np.ndarray
        Couples parameter vector (30 for fw, 42 for vw)
    df : pd.DataFrame
        Couples dataset
    wage_spec : str
        "fw" or "vw"
    
    Returns
    -------
    grad : np.ndarray
        Gradient of log-likelihood
    """
    n = len(df)
    if n == 0:
        n_params = 30 if wage_spec == "fw" else 42
        return np.zeros(n_params)
    
    n_params = 30 if wage_spec == "fw" else 42
    
    # Unpack parameters
    pref, hopp_m, hopp_f, wopp_m, wopp_f = unpack_theta_couples(theta, wage_spec)
    
    # =========================================================================
    # Get data arrays
    # =========================================================================
    # Leisure
    if "leis_util_m" in df.columns:
        l_m = df["leis_util_m"].to_numpy()
    elif "hours_m" in df.columns:
        hours_m = pd.to_numeric(df["hours_m"], errors="coerce").fillna(0).to_numpy()
        l_m = (TOTAL_LEISURE_HOURS - hours_m) / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    else:
        l_m = np.ones(n)
    
    if "leis_util_f" in df.columns:
        l_f = df["leis_util_f"].to_numpy()
    elif "hours_f" in df.columns:
        hours_f = pd.to_numeric(df["hours_f"], errors="coerce").fillna(0).to_numpy()
        l_f = (TOTAL_LEISURE_HOURS - hours_f) / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    else:
        l_f = np.ones(n)
    
    # Consumption
    if "dispy_util_m" in df.columns and "dispy_util_f" in df.columns:
        c_total = df["dispy_util_m"].to_numpy() + df["dispy_util_f"].to_numpy()
    elif "c_norm" in df.columns:
        c_total = df["c_norm"].to_numpy()
    else:
        c_total = np.ones(n)
    
    l_m = np.clip(l_m, 1e-6, None)
    l_f = np.clip(l_f, 1e-6, None)
    c_total = np.clip(c_total, 1e-6, None)
    
    # Box-Cox transforms
    l_m_bc = boxcox_transform(l_m, pref.theta_lm)
    l_f_bc = boxcox_transform(l_f, pref.theta_lf)
    c_bc = boxcox_transform(c_total, pref.theta_c)
    
    # Derivatives of Box-Cox w.r.t. theta
    dl_m_bc_dtheta = d_boxcox_dtheta(l_m, pref.theta_lm)
    dl_f_bc_dtheta = d_boxcox_dtheta(l_f, pref.theta_lf)
    dc_bc_dtheta = d_boxcox_dtheta(c_total, pref.theta_c)
    
    # Covariates
    age_norm_m = _get_col(df, "age_norm_m", 0.0)
    age_norm2_m = _get_col(df, "age_norm2_m", age_norm_m ** 2)
    age_norm_f = _get_col(df, "age_norm_f", 0.0)
    age_norm2_f = _get_col(df, "age_norm2_f", age_norm_f ** 2)
    n_children = _get_col(df, "n_children", 0.0)
    educL_m = _get_col(df, "educL_m", 0.0)
    educH_m = _get_col(df, "educH_m", 0.0)
    educL_f = _get_col(df, "educL_f", 0.0)
    educH_f = _get_col(df, "educH_f", 0.0)
    
    # Beta leisure coefficients
    beta_leisure_m = (
        pref.beta_lm0
        + pref.beta_lm_age_norm * age_norm_m
        + pref.beta_lm_age_norm2 * age_norm2_m
        + pref.beta_lm_n_children * n_children
        + pref.beta_lm_educL * educL_m
        + pref.beta_lm_educH * educH_m
    )
    beta_leisure_f = (
        pref.beta_lf0
        + pref.beta_lf_age_norm * age_norm_f
        + pref.beta_lf_age_norm2 * age_norm2_f
        + pref.beta_lf_n_children * n_children
        + pref.beta_lf_educL * educL_f
        + pref.beta_lf_educH * educH_f
    )
    
    # Compute utility (no interaction term in simplified spec)
    u = beta_leisure_m * l_m_bc + beta_leisure_f * l_f_bc + pref.beta_c * c_bc
    
    # =========================================================================
    # Preference derivatives (16 params)
    # =========================================================================
    du_dpref = np.zeros((n, 16), dtype=float)
    
    # Male leisure params [0:6]
    du_dpref[:, 0] = l_m_bc                   # beta_lm0
    du_dpref[:, 1] = age_norm_m * l_m_bc      # beta_lm_age_norm
    du_dpref[:, 2] = age_norm2_m * l_m_bc     # beta_lm_age_norm2
    du_dpref[:, 3] = n_children * l_m_bc      # beta_lm_n_children
    du_dpref[:, 4] = educL_m * l_m_bc         # beta_lm_educL
    du_dpref[:, 5] = educH_m * l_m_bc         # beta_lm_educH
    
    # Female leisure params [6:12]
    du_dpref[:, 6] = l_f_bc                   # beta_lf0
    du_dpref[:, 7] = age_norm_f * l_f_bc      # beta_lf_age_norm
    du_dpref[:, 8] = age_norm2_f * l_f_bc     # beta_lf_age_norm2
    du_dpref[:, 9] = n_children * l_f_bc      # beta_lf_n_children
    du_dpref[:, 10] = educL_f * l_f_bc        # beta_lf_educL
    du_dpref[:, 11] = educH_f * l_f_bc        # beta_lf_educH
    
    # Shared params [12:16]
    du_dpref[:, 12] = c_bc                              # beta_c
    du_dpref[:, 13] = beta_leisure_m * dl_m_bc_dtheta   # theta_lm
    du_dpref[:, 14] = beta_leisure_f * dl_f_bc_dtheta   # theta_lf
    du_dpref[:, 15] = pref.beta_c * dc_bc_dtheta        # theta_c
    
    # =========================================================================
    # Hours opportunity derivatives (14 params: 7 male + 7 female)
    # =========================================================================
    working_m = _get_col(df, "working_m", 0.0)
    working_pt1_m = _get_col(df, "working_pt1_m", 0.0)
    working_pt2_m = _get_col(df, "working_pt2_m", 0.0)
    working_ft_m = _get_col(df, "working_ft_m", 0.0)
    gsur_m = _get_col(df, "gsur_m", _get_col(df, "gsur", 0.0))
    
    working_f = _get_col(df, "working_f", 0.0)
    working_pt1_f = _get_col(df, "working_pt1_f", 0.0)
    working_pt2_f = _get_col(df, "working_pt2_f", 0.0)
    working_ft_f = _get_col(df, "working_ft_f", 0.0)
    gsur_f = _get_col(df, "gsur_f", _get_col(df, "gsur", 0.0))
    
    dh_dtheta = np.zeros((n, 14), dtype=float)
    # Male hopp [0:7]
    dh_dtheta[:, 0] = working_m
    dh_dtheta[:, 1] = working_pt1_m
    dh_dtheta[:, 2] = working_pt2_m
    dh_dtheta[:, 3] = working_ft_m
    dh_dtheta[:, 4] = working_m * gsur_m
    dh_dtheta[:, 5] = working_m * educL_m
    dh_dtheta[:, 6] = working_m * educH_m
    # Female hopp [7:14]
    dh_dtheta[:, 7] = working_f
    dh_dtheta[:, 8] = working_pt1_f
    dh_dtheta[:, 9] = working_pt2_f
    dh_dtheta[:, 10] = working_ft_f
    dh_dtheta[:, 11] = working_f * gsur_f
    dh_dtheta[:, 12] = working_f * educL_f
    dh_dtheta[:, 13] = working_f * educH_f
    
    # Compute hopp values
    h_opp = ff_calc_hopp_couples(df, hopp_m, hopp_f)
    
    # =========================================================================
    # Wage opportunity derivatives (12 params if vw: 6 male + 6 female)
    # =========================================================================
    if wage_spec == "vw":
        w_opp = ff_calc_wopp_couples(df, wopp_m, wopp_f)
        
        # Get wage-related variables
        if "wage_m" in df.columns:
            wage_m = pd.to_numeric(df["wage_m"], errors="coerce").fillna(1).to_numpy()
        else:
            wage_m = np.ones(n)
        wage_m = np.clip(wage_m, 1e-6, None)
        log_wage_m = np.log(wage_m)
        
        if "wage_f" in df.columns:
            wage_f = pd.to_numeric(df["wage_f"], errors="coerce").fillna(1).to_numpy()
        else:
            wage_f = np.ones(n)
        wage_f = np.clip(wage_f, 1e-6, None)
        log_wage_f = np.log(wage_f)
        
        pexp_m = _get_col(df, "pexp_m", 0.0)
        pexp_f = _get_col(df, "pexp_f", 0.0)
        
        # Simplified mean log-wage (no regions, no year dummies)
        mean_logw_m = (
            wopp_m.beta0
            + wopp_m.beta_educL * educL_m
            + wopp_m.beta_educH * educH_m
            + wopp_m.beta_pexp * pexp_m
            + wopp_m.beta_pexp2 * pexp_m**2
        )
        mean_logw_f = (
            wopp_f.beta0
            + wopp_f.beta_educL * educL_f
            + wopp_f.beta_educH * educH_f
            + wopp_f.beta_pexp * pexp_f
            + wopp_f.beta_pexp2 * pexp_f**2
        )
        
        sigma_m = np.abs(wopp_m.sigma) + 1e-6
        sigma_f = np.abs(wopp_f.sigma) + 1e-6
        z_m = (log_wage_m - mean_logw_m) / sigma_m
        z_f = (log_wage_f - mean_logw_f) / sigma_f
        z_over_sigma_m = z_m / sigma_m
        z_over_sigma_f = z_f / sigma_f
        
        dw_dtheta = np.zeros((n, 12), dtype=float)
        # Male wopp [0:6]
        dw_dtheta[:, 0] = np.where(working_m > 0, z_over_sigma_m, 0)
        dw_dtheta[:, 1] = np.where(working_m > 0, z_over_sigma_m * educL_m, 0)
        dw_dtheta[:, 2] = np.where(working_m > 0, z_over_sigma_m * educH_m, 0)
        dw_dtheta[:, 3] = np.where(working_m > 0, z_over_sigma_m * pexp_m, 0)
        dw_dtheta[:, 4] = np.where(working_m > 0, z_over_sigma_m * pexp_m**2, 0)
        dw_dtheta[:, 5] = np.where(working_m > 0, (z_m**2 - 1) / sigma_m, 0)
        # Female wopp [6:12]
        dw_dtheta[:, 6] = np.where(working_f > 0, z_over_sigma_f, 0)
        dw_dtheta[:, 7] = np.where(working_f > 0, z_over_sigma_f * educL_f, 0)
        dw_dtheta[:, 8] = np.where(working_f > 0, z_over_sigma_f * educH_f, 0)
        dw_dtheta[:, 9] = np.where(working_f > 0, z_over_sigma_f * pexp_f, 0)
        dw_dtheta[:, 10] = np.where(working_f > 0, z_over_sigma_f * pexp_f**2, 0)
        dw_dtheta[:, 11] = np.where(working_f > 0, (z_f**2 - 1) / sigma_f, 0)
    else:
        w_opp = np.zeros(n)
        dw_dtheta = np.zeros((n, 12))
    
    # =========================================================================
    # Stack all derivatives
    # =========================================================================
    dV_dtheta = np.zeros((n, n_params), dtype=float)
    dV_dtheta[:, 0:16] = du_dpref
    dV_dtheta[:, 16:30] = dh_dtheta
    if wage_spec == "vw":
        dV_dtheta[:, 30:42] = dw_dtheta
    
    # Prior
    prior_col = df.get("prior", None)
    if prior_col is not None:
        log_prior = pd.to_numeric(prior_col, errors="coerce").fillna(0).to_numpy()
    else:
        log_prior = np.zeros(n)
    
    # Total V
    V = u + h_opp + w_opp - log_prior
    
    # Get IDs and observed indicators
    if "idhh_true" in df.columns:
        ids = df["idhh_true"].to_numpy()
    else:
        ids = df["idhh"].to_numpy()
    
    draws = df["draw"].to_numpy()
    if "is_chosen" in df.columns:
        is_chosen = pd.to_numeric(df["is_chosen"], errors="coerce").fillna(0).to_numpy()
        is_obs = (is_chosen == 1) | (draws == 0)
    else:
        is_obs = (draws == 0)
    
    # =========================================================================
    # Vectorized gradient computation (same as singles)
    # =========================================================================
    unique_ids, group_idx = np.unique(ids, return_inverse=True)
    n_individuals = len(unique_ids)
    
    id_changes = np.concatenate([[0], np.where(np.diff(ids) != 0)[0] + 1, [n]])
    V_max_per_group = np.maximum.reduceat(V, id_changes[:-1])
    V_max = V_max_per_group[group_idx]
    
    exp_V_shifted = np.exp(V - V_max)
    sum_exp_V_per_group = np.bincount(group_idx, weights=exp_V_shifted, minlength=n_individuals)
    sum_exp_V = sum_exp_V_per_group[group_idx]
    P = exp_V_shifted / sum_exp_V
    
    P_weighted_dV = P[:, None] * dV_dtheta
    E_dV_per_group = np.zeros((n_individuals, n_params), dtype=float)
    for k in range(n_params):
        E_dV_per_group[:, k] = np.bincount(group_idx, weights=P_weighted_dV[:, k], minlength=n_individuals)
    E_dV = E_dV_per_group[group_idx, :]
    
    obs_mask = is_obs.astype(bool)
    grad = (dV_dtheta[obs_mask, :] - E_dV[obs_mask, :]).sum(axis=0)
    
    return grad


def neg_log_likelihood_with_grad_joint(
    theta: np.ndarray,
    df_sm: pd.DataFrame,
    df_sf: pd.DataFrame,
    df_cou: pd.DataFrame,
    wage_spec: str = "fw",
) -> Tuple[float, np.ndarray]:
    """Compute negative log-likelihood and gradient for joint estimation."""
    ll = log_likelihood_joint(theta, df_sm, df_sf, df_cou, wage_spec)
    grad = analytical_gradient_joint(theta, df_sm, df_sf, df_cou, wage_spec)
    return -ll, -grad


def fast_neg_ll_with_grad_joint(
    theta: np.ndarray,
    data_sm: Optional[PrecomputedDataSingles],
    data_sf: Optional[PrecomputedDataSingles],
    data_cou: Optional[PrecomputedDataCouples],
    wage_spec: str = "fw",
) -> Tuple[float, np.ndarray]:
    """
    FAST joint estimation using precomputed data (SIMPLIFIED SPEC).
    
    SIMPLIFIED Parameter layout (48 fw, 60 vw):
    [0:9]    - Single males preferences (9)
    [9:18]   - Single females preferences (9)
    [18:34]  - Couples preferences (16)
    [34:41]  - Hours opportunity (males, 7)
    [41:48]  - Hours opportunity (females, 7)
    [48:54]  - Wage opportunity (males, 6, vw only)
    [54:60]  - Wage opportunity (females, 6, vw only)
    
    Singles standalone expects (16 fw, 22 vw):
    - Preferences: 9 (beta_l0, age_norm, age_norm2, n_children, educL, educH, beta_c, theta_l, theta_c)
    - Hours opp: 7 (const, age_norm, age_norm2, n_children, educL, educH, gsur)
    - Wage opp: 6 (const, age_norm, age_norm2, educL, educH, pexp, vw only)
    
    Couples standalone expects (30 fw, 42 vw):
    - Male prefs: 6 (beta_lm0, age_norm, age_norm2, n_children, educL, educH)
    - Female prefs: 6 (beta_lf0, age_norm, age_norm2, n_children, educL, educH)
    - Shared prefs: 4 (beta_c, theta_lm, theta_lf, theta_c)
    - Male hopp: 7
    - Female hopp: 7
    - Male wopp: 6 (vw only)
    - Female wopp: 6 (vw only)
    
    Returns
    -------
    Tuple[float, np.ndarray]
        (-LL, -gradient) for minimization
    """
    counts = get_n_params_joint(wage_spec)
    n_params = counts["total"]
    
    ll_total = 0.0
    grad = np.zeros(n_params, dtype=np.float64)
    
    # SIMPLIFIED Index boundaries
    idx_pref_sm = (0, 9)       # 9 params
    idx_pref_sf = (9, 18)      # 9 params
    idx_pref_cou = (18, 34)    # 16 params
    idx_hopp_m = (34, 41)      # 7 params
    idx_hopp_f = (41, 48)      # 7 params
    
    if wage_spec == "vw":
        idx_wopp_m = (48, 54)  # 6 params
        idx_wopp_f = (54, 60)  # 6 params
    
    # Single males
    if data_sm is not None:
        # Standalone singles expects: pref(9) + hopp(7) + wopp(6 if vw) = 16 or 22
        theta_sm = np.concatenate([
            theta[idx_pref_sm[0]:idx_pref_sm[1]],  # 9 pref params
            theta[idx_hopp_m[0]:idx_hopp_m[1]],    # 7 hopp params
        ])
        if wage_spec == "vw":
            theta_sm = np.concatenate([theta_sm, theta[idx_wopp_m[0]:idx_wopp_m[1]]])  # 6 wopp
        
        neg_ll_sm, neg_grad_sm = fast_neg_ll_with_grad_singles(
            theta_sm, data_sm, is_male=True, wage_spec=wage_spec
        )
        ll_total -= neg_ll_sm
        
        # Map gradient to joint theta
        grad[idx_pref_sm[0]:idx_pref_sm[1]] -= neg_grad_sm[0:9]
        grad[idx_hopp_m[0]:idx_hopp_m[1]] -= neg_grad_sm[9:16]
        if wage_spec == "vw":
            grad[idx_wopp_m[0]:idx_wopp_m[1]] -= neg_grad_sm[16:22]
    
    # Single females
    if data_sf is not None:
        # Standalone singles expects: pref(9) + hopp(7) + wopp(6 if vw) = 16 or 22
        theta_sf = np.concatenate([
            theta[idx_pref_sf[0]:idx_pref_sf[1]],  # 9 pref params
            theta[idx_hopp_f[0]:idx_hopp_f[1]],    # 7 hopp params
        ])
        if wage_spec == "vw":
            theta_sf = np.concatenate([theta_sf, theta[idx_wopp_f[0]:idx_wopp_f[1]]])  # 6 wopp
        
        neg_ll_sf, neg_grad_sf = fast_neg_ll_with_grad_singles(
            theta_sf, data_sf, is_male=False, wage_spec=wage_spec
        )
        ll_total -= neg_ll_sf
        
        # Map gradient
        grad[idx_pref_sf[0]:idx_pref_sf[1]] -= neg_grad_sf[0:9]
        grad[idx_hopp_f[0]:idx_hopp_f[1]] -= neg_grad_sf[9:16]
        if wage_spec == "vw":
            grad[idx_wopp_f[0]:idx_wopp_f[1]] -= neg_grad_sf[16:22]
    
    # Couples
    if data_cou is not None:
        # Standalone couples expects (30 fw, 42 vw):
        # [0:6]   Male prefs: beta_lm0, age_norm, age_norm2, n_children, educL, educH
        # [6:12]  Female prefs: beta_lf0, age_norm, age_norm2, n_children, educL, educH
        # [12:16] Shared prefs: beta_c, theta_lm, theta_lf, theta_c
        # [16:23] Male hopp (7)
        # [23:30] Female hopp (7)
        # [30:36] Male wopp (6, vw only)
        # [36:42] Female wopp (6, vw only)
        #
        # Joint couples pref [18:34] has 16 params with same layout:
        # [0:6]   Male prefs
        # [6:12]  Female prefs
        # [12:16] Shared prefs
        
        joint_cou_pref = theta[idx_pref_cou[0]:idx_pref_cou[1]]  # 16 params
        
        # Build standalone-compatible theta_cou (30 for fw, 42 for vw)
        n_cou_params = 30 if wage_spec == "fw" else 42
        theta_cou = np.zeros(n_cou_params, dtype=np.float64)
        
        # Preferences map directly (same order)
        theta_cou[0:16] = joint_cou_pref
        
        # Hours opportunity
        theta_cou[16:23] = theta[idx_hopp_m[0]:idx_hopp_m[1]]
        theta_cou[23:30] = theta[idx_hopp_f[0]:idx_hopp_f[1]]
        
        if wage_spec == "vw":
            theta_cou[30:36] = theta[idx_wopp_m[0]:idx_wopp_m[1]]
            theta_cou[36:42] = theta[idx_wopp_f[0]:idx_wopp_f[1]]
        
        neg_ll_cou, neg_grad_cou = fast_neg_ll_with_grad_couples(
            theta_cou, data_cou, wage_spec=wage_spec
        )
        ll_total -= neg_ll_cou
        
        # Map gradient back (same layout, no reordering needed)
        grad[idx_pref_cou[0]:idx_pref_cou[1]] -= neg_grad_cou[0:16]
        grad[idx_hopp_m[0]:idx_hopp_m[1]] -= neg_grad_cou[16:23]
        grad[idx_hopp_f[0]:idx_hopp_f[1]] -= neg_grad_cou[23:30]
        
        if wage_spec == "vw":
            grad[idx_wopp_m[0]:idx_wopp_m[1]] -= neg_grad_cou[30:36]
            grad[idx_wopp_f[0]:idx_wopp_f[1]] -= neg_grad_cou[36:42]
    
    return -ll_total, -grad


# =============================================================================
# CSV Initial Parameters Loader
# =============================================================================

def _load_init_params_from_csv(
    csv_path: Path,
    param_names: List[str],
    default_theta: np.ndarray,
) -> np.ndarray:
    """
    Load initial parameter values from a CSV file.
    
    Parameters
    ----------
    csv_path : Path
        Path to CSV file with columns 'parameter' and 'value'
    param_names : List[str]
        List of parameter names (defines order)
    default_theta : np.ndarray
        Default values to use for parameters not found in CSV
    
    Returns
    -------
    np.ndarray
        Initial parameter values
    """
    import pandas as pd
    
    LOGGER.info(f"Loading initial parameters from: {csv_path}")
    
    if not csv_path.exists():
        LOGGER.warning(f"CSV file not found: {csv_path}. Using defaults.")
        return default_theta
    
    df = pd.read_csv(csv_path)
    
    # Check required columns
    if "parameter" not in df.columns or "value" not in df.columns:
        LOGGER.warning("CSV must have 'parameter' and 'value' columns. Using defaults.")
        return default_theta
    
    # Create mapping from CSV
    param_map = dict(zip(df["parameter"], df["value"]))
    
    # Build initial values array
    theta0 = default_theta.copy()
    loaded = 0
    missing = []
    
    for i, name in enumerate(param_names):
        if name in param_map:
            theta0[i] = float(param_map[name])
            loaded += 1
        else:
            missing.append(name)
    
    LOGGER.info(f"  Loaded {loaded}/{len(param_names)} parameters from CSV")
    if missing:
        LOGGER.info(f"  Using defaults for: {missing[:5]}{'...' if len(missing) > 5 else ''}")
    
    return theta0


# =============================================================================
# CLI and main
# =============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "RURO estimation for France (preferences + opportunity densities).\n\n"
            "Group definitions (aligned with RURO_prep.py pipeline):\n"
            "  - group=1:  ALL singles (both sexes pooled)\n"
            "  - group=10: couples\n\n"
            "Use --sex to further filter singles by gender:\n"
            "  - --sex m: single males only\n"
            "  - --sex f: single females only\n"
            "  - --sex pooled: both sexes (default)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mnl-file",
        type=Path,
        required=True,
        help="Path to the RURO-MNL long dataset produced by RURO_prep_mnl_basic.py",
    )
    parser.add_argument(
        "--group",
        type=int,
        default=1,
        choices=[1, 10],
        help="RURO group to estimate: 1=singles (all sexes), 10=couples.",
    )
    parser.add_argument(
        "--sex",
        type=str,
        default="pooled",
        choices=["m", "f", "pooled"],
        help=(
            "For singles (group=1): filter by sex. "
            "'m'=males only (dgn==1), 'f'=females only (dgn==0), "
            "'pooled'=both sexes (default). Ignored for couples."
        ),
    )
    parser.add_argument(
        "--wage-spec",
        type=str,
        default="fw",
        choices=["fw", "vw"],
        help="Wage specification: 'fw' for fixed wages, 'vw' for variable wages.",
    )
    parser.add_argument(
        "--maxiter",
        type=int,
        default=200,
        help="Maximum number of optimizer iterations.",
    )
    parser.add_argument(
        "--optimizer",
        type=str,
        default="L-BFGS-B",
        choices=["BFGS", "L-BFGS-B"],
        help="Optimization method: 'BFGS' (numerical grad) or 'L-BFGS-B' (analytical grad).",
    )
    parser.add_argument(
        "--validate-gradient",
        action="store_true",
        help="Compare analytical and numerical gradients at initial point.",
    )
    parser.add_argument(
        "--out-file",
        type=Path,
        default=None,
        help="Optional path to save estimation results (JSON or pickle).",
    )
    parser.add_argument(
        "--joint",
        action="store_true",
        help=(
            "Joint estimation of all groups (single males, single females, couples) "
            "with SHARED opportunity parameters by gender "
            "where hours/wage opportunity densities are the same for single males and "
            "male partners in couples (and similarly for females)."
        ),
    )
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=N_JOBS,
        help=(
            f"Number of parallel jobs for gradient computation (default: {N_JOBS}). "
            "Set to 1 to disable parallelization. Requires joblib."
        ),
    )
    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel computation even if joblib is available.",
    )
    parser.add_argument(
        "--use-numba",
        action="store_true",
        help="Use numba-accelerated gradient computation if available.",
    )
    parser.add_argument(
        "--post-estimation",
        action="store_true",
        help=(
            "Run post-estimation analysis (standard errors, t-values, model fit). "
            "Computes Hessian, variance-covariance matrix, and saves to Excel. "
        ),
    )
    parser.add_argument(
        "--init-params",
        type=Path,
        default=None,
        help=(
            "Path to CSV file with initial parameter values. "
            "CSV should have columns 'parameter' and 'value'. "
            "Use this to start from previous estimates or custom values. "
            "Parameters not found in CSV will use defaults."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    
    LOGGER.info("=" * 60)
    LOGGER.info("RURO Estimation for France")
    LOGGER.info("=" * 60)
    LOGGER.info(f"MNL file: {args.mnl_file}")
    
    # -------------------------------------------------------------------------
    # Report available optimizations
    # -------------------------------------------------------------------------
    LOGGER.info("")
    LOGGER.info("Performance optimizations:")
    if NUMBA_AVAILABLE:
        LOGGER.info(f"  ✓ Numba JIT compilation available (use --use-numba to enable)")
    else:
        LOGGER.info(f"  ✗ Numba not available (install with: pip install numba)")
    
    if JOBLIB_AVAILABLE:
        n_jobs_effective = 1 if args.no_parallel else args.n_jobs
        LOGGER.info(f"  ✓ Joblib parallelization available (n_jobs={n_jobs_effective})")
    else:
        LOGGER.info(f"  ✗ Joblib not available (install with: pip install joblib)")
    
    LOGGER.info(f"  CPU cores: {os.cpu_count()} logical, N_JOBS={N_JOBS}")
    LOGGER.info("")
    
    # -------------------------------------------------------------------------
    # Load data
    # -------------------------------------------------------------------------
    if not args.mnl_file.exists():
        raise FileNotFoundError(f"MNL file not found: {args.mnl_file}")
    
    df_full = pd.read_parquet(args.mnl_file)
    LOGGER.info(f"Loaded {len(df_full)} rows from MNL dataset.")
    
    # =========================================================================
    # JOINT ESTIMATION MODE
    # =========================================================================
    if args.joint:
        LOGGER.info("")
        LOGGER.info("=" * 60)
        LOGGER.info("JOINT ESTIMATION MODE")
        LOGGER.info("Estimating all groups with SHARED opportunity parameters")
        LOGGER.info("=" * 60)
        LOGGER.info(f"Wage spec: {args.wage_spec}")
        LOGGER.info("")
        
        # Split data into groups
        if "ruro_group" in df_full.columns and "dgn" in df_full.columns:
            df_sm = df_full[(df_full["ruro_group"] == 1) & (df_full["dgn"] == 1)].copy()
            df_sf = df_full[(df_full["ruro_group"] == 1) & (df_full["dgn"] == 0)].copy()
            df_cou = df_full[df_full["ruro_group"] == 10].copy()
        else:
            raise ValueError("Need 'ruro_group' and 'dgn' columns for joint estimation.")
        
        LOGGER.info(f"Single males:   {len(df_sm)} rows")
        LOGGER.info(f"Single females: {len(df_sf)} rows")
        LOGGER.info(f"Couples:        {len(df_cou)} rows")
        LOGGER.info("")
        
        # Count unique individuals
        n_sm = df_sm["idhh"].nunique() if "idhh" in df_sm.columns else len(df_sm) // 50
        n_sf = df_sf["idhh"].nunique() if "idhh" in df_sf.columns else len(df_sf) // 50
        n_cou = df_cou["idhh"].nunique() if "idhh" in df_cou.columns else len(df_cou) // 50
        LOGGER.info(f"Unique individuals: SM={n_sm}, SF={n_sf}, COU={n_cou}")
        LOGGER.info("")
        
        # Precompute data for fast optimization
        LOGGER.info("Pre-computing data arrays for fast optimization...")
        import time
        t0 = time.perf_counter()
        data_sm = precompute_data_singles(df_sm, is_male=True) if len(df_sm) > 0 else None
        data_sf = precompute_data_singles(df_sf, is_male=False) if len(df_sf) > 0 else None
        data_cou = precompute_data_couples(df_cou) if len(df_cou) > 0 else None
        t1 = time.perf_counter()
        LOGGER.info(f"Pre-computation done in {t1-t0:.3f}s")
        LOGGER.info("")
        
        # Initial parameters for joint estimation
        theta0 = get_initial_theta_joint(wage_spec=args.wage_spec)
        param_names = get_param_names_joint(wage_spec=args.wage_spec)
        counts = get_n_params_joint(wage_spec=args.wage_spec)
        
        LOGGER.info(f"Total parameters: {len(theta0)}")
        LOGGER.info(f"  - Preferences (group-specific): {counts['n_pref']}")
        LOGGER.info(f"    - Single males:   {counts['n_pref_sm']}")
        LOGGER.info(f"    - Single females: {counts['n_pref_sf']}")
        LOGGER.info(f"    - Couples:        {counts['n_pref_cou']}")
        LOGGER.info(f"  - Hours opportunity (gender-shared): {counts['n_hopp']}")
        LOGGER.info(f"    - Males:   {counts['n_hopp_m']}")
        LOGGER.info(f"    - Females: {counts['n_hopp_f']}")
        if args.wage_spec == "vw":
            LOGGER.info(f"  - Wage opportunity (gender-shared): {counts['n_wopp']}")
            LOGGER.info(f"    - Males:   {counts['n_wopp_m']}")
            LOGGER.info(f"    - Females: {counts['n_wopp_f']}")
        LOGGER.info("")
        
        # Initial log-likelihood
        ll0 = log_likelihood_joint(theta0, df_sm, df_sf, df_cou, wage_spec=args.wage_spec)
        LOGGER.info(f"Initial log-likelihood: {ll0:.4f}")
        LOGGER.info("")
        
        # Validate gradient (optional)
        if args.validate_gradient:
            LOGGER.info("Validating analytical gradient against numerical gradient...")
            LOGGER.info("(This may take a minute for joint estimation)")
            
            # Get analytical gradient from fast function
            _, neg_grad_analytical = fast_neg_ll_with_grad_joint(
                theta0, data_sm, data_sf, data_cou, wage_spec=args.wage_spec
            )
            
            # Numerical gradient (central differences)
            def neg_ll_only(theta):
                neg_ll, _ = fast_neg_ll_with_grad_joint(
                    theta, data_sm, data_sf, data_cou, wage_spec=args.wage_spec
                )
                return neg_ll
            
            grad_numerical = numerical_gradient(neg_ll_only, theta0, eps=1e-5)
            
            # Compare
            grad_diff = np.abs(neg_grad_analytical - grad_numerical)
            rel_diff = np.abs(grad_diff / (np.abs(grad_numerical) + 1e-10))
            max_diff = np.max(grad_diff)
            max_rel_diff = np.max(rel_diff)
            mean_diff = np.mean(grad_diff)
            
            LOGGER.info(f"Max absolute gradient difference: {max_diff:.8f}")
            LOGGER.info(f"Max relative gradient difference: {max_rel_diff:.8f}")
            LOGGER.info(f"Mean absolute gradient difference: {mean_diff:.8f}")
            
            if max_rel_diff > 0.01:  # 1% relative tolerance
                LOGGER.warning("Large gradient discrepancy detected!")
                # Show worst parameters
                worst_idx = np.argsort(rel_diff)[-10:][::-1]
                LOGGER.warning("Top 10 parameters with largest relative gradient difference:")
                for idx in worst_idx:
                    LOGGER.warning(f"  [{idx}] {param_names[idx]}: "
                                 f"analytical={neg_grad_analytical[idx]:.6f}, "
                                 f"numerical={grad_numerical[idx]:.6f}, "
                                 f"rel_diff={rel_diff[idx]:.4f}")
            else:
                LOGGER.info("Gradient validation passed!")
            LOGGER.info("")
        
        # Optimization
        LOGGER.info("Starting joint optimization...")
        LOGGER.info(f"Optimizer: {args.optimizer}")
        LOGGER.info("-" * 40)
        
        # Track timing
        iteration_times = []
        import time as time_module
        start_time_joint = time_module.perf_counter()
        
        if args.optimizer == "L-BFGS-B":
            # Use FAST precomputed-data function (2-5x faster)
            LOGGER.info("Using FAST precomputed-data objective function")
            
            def objective_and_grad(theta):
                t_start = time_module.perf_counter()
                result = fast_neg_ll_with_grad_joint(
                    theta, data_sm, data_sf, data_cou, wage_spec=args.wage_spec
                )
                iteration_times.append(time_module.perf_counter() - t_start)
                return result            # Bounds for Box-Cox parameters (loosened further to avoid singular Hessian)
            # Box-Cox: (-10, 20.0), Sigma: (-10, 50.0)
            # SIMPLIFIED Parameter layout (60 params for vw, 48 for fw):
            # [0:9]   SM prefs: theta_l=7, theta_c=8
            # [9:18]  SF prefs: theta_l=16, theta_c=17
            # [18:34] COU prefs: theta_l_m=31, theta_l_f=32, theta_c=33
            # [34:41] HOPP males
            # [41:48] HOPP females
            # [48:54] WOPP males: sigma=53
            # [54:60] WOPP females: sigma=59
            bounds = [(None, None)] * len(theta0)
            # SM Box-Cox: indices 7, 8
            bounds[7] = (-10, 20.0)   # theta_l (SM leisure)
            bounds[8] = (-10, 20.0)   # theta_c (SM consumption)
            # SF Box-Cox: indices 16, 17
            bounds[16] = (-10, 20.0)  # theta_l (SF leisure)
            bounds[17] = (-10, 20.0)  # theta_c (SF consumption)
            # Couples Box-Cox: indices 31, 32, 33
            bounds[31] = (-10, 20.0)  # theta_lm (couples male leisure)
            bounds[32] = (-10, 20.0)  # theta_lf (couples female leisure)
            bounds[33] = (-10, 20.0)  # theta_c (couples consumption)
            # Sigma bounds (if vw)
            if args.wage_spec == "vw":
                bounds[53] = (-10, 50.0)   # sigma_m (male wage error SD)
                bounds[59] = (-10, 50.0)   # sigma_f (female wage error SD)
            
            result = minimize(
                objective_and_grad,
                theta0,
                method="L-BFGS-B",
                jac=True,
                bounds=bounds,
                options={"disp": True, "maxiter": args.maxiter, "ftol": 1e-9, "gtol": 1e-5},
            )
        else:
            # Use FAST precomputed-data function for BFGS too
            LOGGER.info("Using FAST precomputed-data objective function")
            
            def objective(theta):
                t_start = time_module.perf_counter()
                neg_ll, _ = fast_neg_ll_with_grad_joint(
                    theta, data_sm, data_sf, data_cou, wage_spec=args.wage_spec
                )
                iteration_times.append(time_module.perf_counter() - t_start)
                return neg_ll
            
            result = minimize(
                objective,
                theta0,
                method="BFGS",
                options={"disp": True, "maxiter": args.maxiter},
            )
        
        total_time_joint = time_module.perf_counter() - start_time_joint
        
        # Results
        LOGGER.info("-" * 40)
        LOGGER.info("Joint optimization completed.")
        LOGGER.info(f"Success: {result.success}")
        LOGGER.info(f"Message: {result.message}")
        LOGGER.info(f"Final log-likelihood: {-result.fun:.4f}")
        LOGGER.info(f"Number of iterations: {result.nit}")
        LOGGER.info(f"Number of function evaluations: {result.nfev}")
        LOGGER.info("")
        LOGGER.info(f"Performance:")
        LOGGER.info(f"  Total optimization time: {total_time_joint:.2f}s")
        if iteration_times:
            LOGGER.info(f"  Avg time per evaluation: {np.mean(iteration_times)*1000:.2f}ms")
            LOGGER.info(f"  Min/Max per evaluation: {np.min(iteration_times)*1000:.2f}ms / {np.max(iteration_times)*1000:.2f}ms")
        LOGGER.info("")
        
        # Display parameters by group
        LOGGER.info("=" * 70)
        LOGGER.info("ESTIMATED PARAMETERS (JOINT)")
        LOGGER.info("=" * 70)
        
        # Show all parameters
        LOGGER.info(f"{'Index':<6} {'Name':<40} {'Value':>12}")
        LOGGER.info("-" * 60)
        for i, (name, val) in enumerate(zip(param_names, result.x)):
            LOGGER.info(f"{i:<6} {name:<40} {val:>12.4f}")
        LOGGER.info("")
        
        # Convert bounds to serializable format
        bounds_serializable = []
        for b in bounds:
            if b == (None, None):
                bounds_serializable.append([None, None])
            else:
                bounds_serializable.append([b[0], b[1]])
        
        # Save results
        if args.out_file:
            import json
            results_dict = {
                "mode": "joint",
                "success": result.success,
                "message": result.message,
                "log_likelihood": float(-result.fun),
                "n_iterations": int(result.nit),
                "n_fev": int(result.nfev),
                "theta": result.x.tolist(),
                "theta0": theta0.tolist(),  # Initial values
                "bounds": bounds_serializable,  # Bounds for each parameter
                "param_names": param_names,
                "wage_spec": args.wage_spec,
                "n_sm": int(n_sm),
                "n_sf": int(n_sf),
                "n_cou": int(n_cou),
                "n_individuals": int(n_sm + n_sf + n_cou),  # Total individuals for post-estimation
                "estimation_time_seconds": total_time_joint,  # Estimation time
            }
            
            out_path = Path(args.out_file)
            if out_path.suffix == ".json":
                with open(out_path, "w") as f:
                    json.dump(results_dict, f, indent=2)
            else:
                import pickle
                with open(out_path, "wb") as f:
                    pickle.dump(results_dict, f)
            
            LOGGER.info(f"Results saved to: {out_path}")
        
        # -------------------------------------------------------------------------
        # Run joint post-estimation analysis (SE, t-values, plots)
        # -------------------------------------------------------------------------
        if args.post_estimation:
            try:
                from RURO_post_estimation import run_joint_post_estimation, compute_standard_errors
                import sys
                
                # Flush output to ensure previous messages are captured
                sys.stdout.flush()
                sys.stderr.flush()
                
                LOGGER.info("")
                LOGGER.info("=" * 60)
                LOGGER.info("JOINT POST-ESTIMATION ANALYSIS")
                LOGGER.info("=" * 60)
                sys.stdout.flush()
                
                out_dir = Path(args.out_file).parent if args.out_file else Path("outputs/estimates/fr")
                
                # Compute standard errors using the joint gradient function
                # We need to build a gradient function that returns gradient of NLL
                def joint_grad_func(theta):
                    _, neg_grad = fast_neg_ll_with_grad_joint(
                        theta,
                        data_sm, data_sf, data_cou,
                        args.wage_spec
                    )
                    return neg_grad  # Already gradient of NLL
                
                LOGGER.info("Computing standard errors via numerical Hessian...")
                se_result = compute_standard_errors(
                    theta=result.x,
                    grad_func=joint_grad_func,
                    param_names=param_names,
                )
                
                se = se_result.get("se")
                varcov = se_result.get("varcov")
                
                if se is not None:
                    LOGGER.info(f"SE computed successfully for {len(se)} parameters")
                    # Update JSON file with SE if it exists
                    if args.out_file:
                        out_path = Path(args.out_file)
                        if out_path.suffix == ".json" and out_path.exists():
                            import json
                            with open(out_path, "r") as f:
                                results_dict = json.load(f)
                            results_dict["std_errors"] = se.tolist()
                            results_dict["t_values"] = (result.x / se).tolist()
                            with open(out_path, "w") as f:
                                json.dump(results_dict, f, indent=2)
                            LOGGER.info(f"SE added to: {out_path}")
                else:
                    LOGGER.warning("Could not compute SE (Hessian may be singular)")
                
                # Flush output to ensure capture
                import sys
                sys.stdout.flush()
                sys.stderr.flush()
                
                # Run full joint post-estimation
                post_results = run_joint_post_estimation(
                    theta=result.x,
                    param_names=param_names,
                    log_likelihood=float(-result.fun),
                    n_sm=n_sm,
                    n_sf=n_sf,
                    n_cou=n_cou,
                    df_sm=df_sm,
                    df_sf=df_sf,
                    df_cou=df_cou,
                    wage_spec=args.wage_spec,
                    out_dir=out_dir,
                    se=se,
                    varcov=varcov,
                    theta0=theta0,
                    bounds=bounds,
                    estimation_time_seconds=total_time_joint,
                )
                
                LOGGER.info("Joint post-estimation analysis complete.")
                
            except ImportError as e:
                LOGGER.warning(f"Could not run post-estimation: {e}")
            except Exception as e:
                LOGGER.error(f"Joint post-estimation failed: {e}")
                import traceback
                traceback.print_exc()
        
        LOGGER.info("=" * 60)
        LOGGER.info("Done (joint estimation).")
        return
    
    # =========================================================================
    # SINGLE GROUP ESTIMATION MODE (original behavior)
    # =========================================================================
    LOGGER.info(f"Group: {args.group} ({'singles' if args.group == 1 else 'couples'})")
    if args.group == 1:
        LOGGER.info(f"Sex filter: {args.sex}")
    LOGGER.info(f"Wage spec: {args.wage_spec}")
    LOGGER.info("")
    
    # Filter to requested group
    df = df_full.copy()
    if "ruro_group" in df.columns:
        df = df[df["ruro_group"] == args.group].copy()
        LOGGER.info(f"Filtered to ruro_group={args.group}: {len(df)} rows.")
    else:
        LOGGER.warning("No 'ruro_group' column found; using full dataset.")
    
    if len(df) == 0:
        raise ValueError(f"No data for group {args.group}.")
    
    # -------------------------------------------------------------------------
    # For singles, optionally filter by sex (dgn: 1=male, 0=female)
    # -------------------------------------------------------------------------    is_male = True  # default for singles
    
    if args.group == 1:
        if args.sex == "m":
            if "dgn" in df.columns:
                df = df[df["dgn"] == 1].copy()
                LOGGER.info(f"Filtered to single males (dgn==1): {len(df)} rows.")
            else:
                LOGGER.warning("No 'dgn' column found; cannot filter by sex.")
            is_male = True
        elif args.sex == "f":
            if "dgn" in df.columns:
                df = df[df["dgn"] == 0].copy()
                LOGGER.info(f"Filtered to single females (dgn==0): {len(df)} rows.")
            else:
                LOGGER.warning("No 'dgn' column found; cannot filter by sex.")
            is_male = False
        else:  # pooled
            LOGGER.info("Using pooled singles (both sexes).")
            # For pooled, we use male parameters as default (can be extended)
            is_male = True
        
        if len(df) == 0:
            raise ValueError(f"No data for singles with sex={args.sex}.")        # Get initial parameters and precompute data for singles
        param_names = get_param_names_singles()
        theta0 = get_initial_theta_singles(is_male=is_male)
        # For fixed wages, only use first 21 parameters (no wage equation)
        if args.wage_spec == "fw":
            theta0 = theta0[:21]
            param_names = param_names[:21]
        
        # Load initial parameters from CSV if provided
        if args.init_params is not None:
            theta0 = _load_init_params_from_csv(
                csv_path=args.init_params,
                param_names=param_names,
                default_theta=theta0,
            )
        
        LOGGER.info(f"Number of parameters: {len(theta0)}")
        LOGGER.info(f"Initial theta: {theta0[:5]}... (truncated)")
        
        LOGGER.info("")
        LOGGER.info("Pre-computing data arrays for fast optimization...")
        import time
        t0 = time.perf_counter()
        precomputed_data = precompute_data_singles(df, is_male=is_male)
        t1 = time.perf_counter()
        LOGGER.info(f"Pre-computation done in {t1-t0:.3f}s")
        LOGGER.info(f"  - {precomputed_data.n_groups} individuals")
        LOGGER.info(f"  - {len(precomputed_data.c)} rows")
        LOGGER.info("")
          # Initial log-likelihood
        ll0 = fast_log_likelihood_singles(theta0, precomputed_data, is_male=is_male, wage_spec=args.wage_spec)
        LOGGER.info(f"Initial log-likelihood: {ll0:.4f}")
        
        # Set up estimation functions
        ll_func = lambda t: fast_log_likelihood_singles(t, precomputed_data, is_male=is_male, wage_spec=args.wage_spec)
        grad_func = lambda t: fast_analytical_gradient_singles(t, precomputed_data, is_male=is_male, wage_spec=args.wage_spec)
        
    else:
        # =====================================================================
        # COUPLES ESTIMATION
        # =====================================================================
        LOGGER.info("=" * 60)
        LOGGER.info("COUPLES ESTIMATION")
        LOGGER.info("=" * 60)
        
        # Verify couples data has wide format columns
        required_cols = ["hours_m", "hours_f", "idhh", "draw"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Couples data missing required columns: {missing}. "
                           "Ensure RURO_prep_mnl_basic.py created wide-format data.")
        
        LOGGER.info(f"Couples data: {len(df)} rows, {df['idhh'].nunique()} households")
          # Get initial parameters and precompute data for couples
        param_names = get_param_names_couples(wage_spec=args.wage_spec)
        theta0 = get_initial_theta_couples(wage_spec=args.wage_spec)
        
        # Load initial parameters from CSV if provided
        if args.init_params is not None:
            theta0 = _load_init_params_from_csv(
                csv_path=args.init_params,
                param_names=param_names,
                default_theta=theta0,
            )
        
        LOGGER.info(f"Number of parameters: {len(theta0)}")
        LOGGER.info(f"Initial theta: {theta0[:5]}... (truncated)")
        
        LOGGER.info("")
        LOGGER.info("Pre-computing data arrays for fast optimization...")
        import time
        t0 = time.perf_counter()
        precomputed_data = precompute_data_couples(df)
        t1 = time.perf_counter()
        LOGGER.info(f"Pre-computation done in {t1-t0:.3f}s")
        LOGGER.info(f"  - {precomputed_data.n_groups} households")
        LOGGER.info(f"  - {len(precomputed_data.c)} rows")
        LOGGER.info("")
        
        # Initial log-likelihood
        ll0 = fast_log_likelihood_couples(theta0, precomputed_data, wage_spec=args.wage_spec)
        LOGGER.info(f"Initial log-likelihood: {ll0:.4f}")
        
        # Set up estimation functions
        ll_func = lambda t: fast_log_likelihood_couples(t, precomputed_data, wage_spec=args.wage_spec)
        # Note: analytical gradient for couples not yet implemented, use numerical
        grad_func = None
        is_male = None  # Not applicable for couples
    
    # -------------------------------------------------------------------------
    # Validate gradient (optional) - only for singles with analytical gradient
    # -------------------------------------------------------------------------
    if args.validate_gradient and grad_func is not None:
        LOGGER.info("")
        LOGGER.info("Validating analytical gradient against numerical gradient...")
        grad_analytical = fast_analytical_gradient_singles(theta0, precomputed_data, is_male=is_male, wage_spec=args.wage_spec)
        grad_numerical = numerical_gradient(
            lambda t: -fast_log_likelihood_singles(t, precomputed_data, is_male=is_male, wage_spec=args.wage_spec),
            theta0,
            eps=1e-6,
        )
        
        grad_diff = np.abs(grad_analytical - (-grad_numerical))  # Note: analytical is for LL, numerical is for -LL
        max_diff = np.max(grad_diff)
        mean_diff = np.mean(grad_diff)
        
        LOGGER.info(f"Max gradient difference: {max_diff:.8f}")
        LOGGER.info(f"Mean gradient difference: {mean_diff:.8f}")
        
        if max_diff > 1e-3:
            LOGGER.warning("Large gradient discrepancy detected!")
            # Show worst parameters
            param_names = get_param_names_singles()
            worst_idx = np.argsort(grad_diff)[-5:]
            for idx in worst_idx:
                LOGGER.warning(f"  {param_names[idx]}: analytical={grad_analytical[idx]:.6f}, "
                             f"numerical={-grad_numerical[idx]:.6f}, diff={grad_diff[idx]:.8f}")
        else:
            LOGGER.info("Gradient validation passed!")
        LOGGER.info("")
      # -------------------------------------------------------------------------
    # Optimization (using FAST functions with precomputed data)
    # -------------------------------------------------------------------------
    LOGGER.info("")
    LOGGER.info("Starting optimization (using FAST precomputed-data functions)...")
    LOGGER.info(f"Optimizer: {args.optimizer}")
    
    # Track timing
    iteration_times = []
    start_time = time.perf_counter()
    
    # Determine if we're doing singles or couples
    is_singles = args.group == 1
    
    if is_singles and args.optimizer == "L-BFGS-B":
        # Singles with analytical gradient - use fast objective with gradient
        use_numba_opt = args.use_numba and NUMBA_AVAILABLE and _compute_log_likelihood_numba is not None
        if use_numba_opt:
            LOGGER.info("Using Numba-accelerated objective function")
            obj_func = fast_neg_ll_with_grad_numba
        else:
            LOGGER.info("Using NumPy-based objective function")
            obj_func = fast_neg_ll_with_grad_singles
        
        def objective_and_grad(theta):
            t_start = time.perf_counter()
            result = obj_func(theta, precomputed_data, is_male=is_male, wage_spec=args.wage_spec)
            iteration_times.append(time.perf_counter() - t_start)
            return result        # Set up bounds for Box-Cox parameters (loosened: 0.001 to 5.0)
        bounds = [(None, None)] * len(theta0)
        bounds[9] = (-5, 20)   # theta_l (Box-Cox leisure)
        bounds[10] = (-5, 20)  # theta_c (Box-Cox consumption)
        if args.wage_spec == "vw":
            bounds[36] = (-10, 30.0)  # sigma (wage error SD)
        
        LOGGER.info("-" * 40)
        result = minimize(
            objective_and_grad,
            theta0,
            method="L-BFGS-B",
            jac=True,
            bounds=bounds,
            options={"disp": True, "maxiter": args.maxiter, "ftol": 1e-9, "gtol": 1e-5},
        )
    elif not is_singles:
        # Couples - USE ANALYTICAL GRADIENT (available via fast_neg_ll_with_grad_couples)
        LOGGER.info("Using FAST analytical gradient for couples (single-pass LL+grad)")
        
        def objective_and_grad(theta):
            t_start = time.perf_counter()
            neg_ll, neg_grad = fast_neg_ll_with_grad_couples(
                theta, precomputed_data, wage_spec=args.wage_spec
            )
            iteration_times.append(time.perf_counter() - t_start)
            return neg_ll, neg_grad
          # Set up bounds for Box-Cox parameters (loosened: 0.001 to 5.0 for Box-Cox, 0.01 to 10.0 for sigma)
        bounds = [(None, None)] * len(theta0)
        bounds[22] = (-10, 20.0)  # theta_lm (Box-Cox male leisure)
        bounds[23] = (-10, 20.0)  # theta_lf (Box-Cox female leisure)
        bounds[24] = (-10, 20.0)  # theta_c (Box-Cox consumption)
        if args.wage_spec == "vw":
            bounds[59] = (-10, 30.0)  # sigma_m (male wage error SD)
            bounds[75] = (-10, 30.0)  # sigma_f (female wage error SD)
        
        LOGGER.info("-" * 40)
        result = minimize(
            objective_and_grad,
            theta0,
            method="L-BFGS-B",
            jac=True,  # CRITICAL: Tell optimizer we're providing gradient
            bounds=bounds,
            options={"disp": True, "maxiter": args.maxiter, "ftol": 1e-9, "gtol": 1e-5},
        )
    else:
        # Singles with BFGS (numerical gradient)
        LOGGER.info("Using NumPy-based objective function with numerical gradient")
        
        def objective(theta):
            t_start = time.perf_counter()
            ll = fast_log_likelihood_singles(theta, precomputed_data, is_male=is_male, wage_spec=args.wage_spec)
            iteration_times.append(time.perf_counter() - t_start)
            return -ll
        
        LOGGER.info("-" * 40)
        result = minimize(
            objective,
            theta0,
            method="BFGS",
            options={"disp": True, "maxiter": args.maxiter},
        )
    
    total_time = time.perf_counter() - start_time
    
    # -------------------------------------------------------------------------
    # Results
    # -------------------------------------------------------------------------
    LOGGER.info("-" * 40)
    LOGGER.info("Optimization completed.")
    LOGGER.info(f"Success: {result.success}")
    LOGGER.info(f"Message: {result.message}")
    LOGGER.info(f"Final log-likelihood: {-result.fun:.4f}")
    LOGGER.info(f"Number of iterations: {result.nit}")
    LOGGER.info(f"Number of function evaluations: {result.nfev}")
    LOGGER.info("")
    LOGGER.info(f"Performance:")
    LOGGER.info(f"  Total optimization time: {total_time:.2f}s")
    if iteration_times:
        LOGGER.info(f"  Avg time per evaluation: {np.mean(iteration_times)*1000:.2f}ms")
        LOGGER.info(f"  Min/Max per evaluation: {np.min(iteration_times)*1000:.2f}ms / {np.max(iteration_times)*1000:.2f}ms")
    LOGGER.info("")
    
    # Display estimated parameters
    LOGGER.info("=" * 70)
    LOGGER.info("ESTIMATED PARAMETERS")
    LOGGER.info("=" * 70)
    LOGGER.info(f"{'Index':<6} {'Name':<40} {'Value':>12}")
    LOGGER.info("-" * 60)
    
    n_params_to_show = len(result.x)
    if args.wage_spec == "fw":
        # Don't show wage params if fixed wages
        n_params_to_show = 21 if is_singles else 44
    
    for i, (name, val) in enumerate(zip(param_names, result.x)):
        if i >= n_params_to_show:
            break
        LOGGER.info(f"{i:<6} {name:<40} {val:>12.4f}")
    LOGGER.info("")    # Legacy display for singles (for backwards compatibility)
    if is_singles:
        # Unpack theta using simplified structure (16 fw, 22 vw)
        pref, hopp, wopp = unpack_theta_singles(result.x, wage_spec=args.wage_spec)
        LOGGER.info("Estimated preference parameters:")
        LOGGER.info(f"  beta_l0:         {pref.beta_l0:.4f}")
        LOGGER.info(f"  beta_l_age_norm: {pref.beta_l_age_norm:.4f}")
        LOGGER.info(f"  beta_l_age_norm2:{pref.beta_l_age_norm2:.4f}")
        LOGGER.info(f"  beta_l_n_children:{pref.beta_l_n_children:.4f}")
        LOGGER.info(f"  beta_l_educL:    {pref.beta_l_educL:.4f}")
        LOGGER.info(f"  beta_l_educH:    {pref.beta_l_educH:.4f}")
        LOGGER.info(f"  beta_c:          {pref.beta_c:.4f}")
        LOGGER.info(f"  theta_l:         {pref.theta_l:.4f}")
        LOGGER.info(f"  theta_c:         {pref.theta_c:.4f}")
        LOGGER.info("")
        
        LOGGER.info("Estimated hours opportunity parameters:")
        LOGGER.info(f"  beta_work:       {hopp.beta_work:.4f}")
        LOGGER.info(f"  beta_pt1:        {hopp.beta_pt1:.4f}")
        LOGGER.info(f"  beta_pt2:        {hopp.beta_pt2:.4f}")
        LOGGER.info(f"  beta_ft:         {hopp.beta_ft:.4f}")
        LOGGER.info(f"  beta_gsur:       {hopp.beta_gsur:.4f}")
        LOGGER.info(f"  beta_work_educL: {hopp.beta_work_educL:.4f}")
        LOGGER.info(f"  beta_work_educH: {hopp.beta_work_educH:.4f}")
        LOGGER.info("")
        
        if args.wage_spec == "vw":
            LOGGER.info("Estimated wage opportunity parameters:")
            LOGGER.info(f"  beta0:           {wopp.beta0:.4f}")
            LOGGER.info(f"  beta_educL:      {wopp.beta_educL:.4f}")
            LOGGER.info(f"  beta_educH:      {wopp.beta_educH:.4f}")
            LOGGER.info(f"  beta_pexp:       {wopp.beta_pexp:.4f}")
            LOGGER.info(f"  beta_pexp2:      {wopp.beta_pexp2:.6f}")
            LOGGER.info(f"  sigma:           {wopp.sigma:.4f}")
            LOGGER.info("")
    else:
        # Couples summary
        LOGGER.info("Couples model - key parameters:")
        LOGGER.info(f"  Male leisure intercept (beta_lm0):     {result.x[0]:.4f}")
        LOGGER.info(f"  Female leisure intercept (beta_lf0):   {result.x[11]:.4f}")
        LOGGER.info(f"  Consumption coefficient (beta_c):      {result.x[25]:.4f}")
        LOGGER.info(f"  Male Box-Cox leisure (theta_lm):       {result.x[22]:.4f}")
        LOGGER.info(f"  Female Box-Cox leisure (theta_lf):     {result.x[23]:.4f}")
        LOGGER.info(f"  Box-Cox consumption (theta_c):         {result.x[24]:.4f}")
        LOGGER.info(f"  Male work coefficient:                 {result.x[26]:.4f}")
        LOGGER.info(f"  Female work coefficient:               {result.x[35]:.4f}")
        LOGGER.info("")
      # -------------------------------------------------------------------------
    # Save results (optional)
    # -------------------------------------------------------------------------
    if args.out_file:
        import json
        results_dict = {
            "success": result.success,
            "message": result.message,
            "log_likelihood": float(-result.fun),
            "n_iterations": int(result.nit),
            "n_fev": int(result.nfev),
            "theta": result.x.tolist(),
            "param_names": param_names,
            "group": args.group,
            "sex": args.sex if args.group == 1 else None,
            "wage_spec": args.wage_spec,
            "n_individuals": int(precomputed_data.n_groups),  # Number of individuals/households
        }
        out_path = Path(args.out_file)
        if out_path.suffix == ".json":
            with open(out_path, "w") as f:
                json.dump(results_dict, f, indent=2)
        else:
            import pickle
            with open(out_path, "wb") as f:
                pickle.dump(results_dict, f)
        
        LOGGER.info(f"Results saved to: {out_path}")
      # -------------------------------------------------------------------------
    # Run post-estimation analysis (standard errors, t-values, plots)
    # -------------------------------------------------------------------------
    if args.post_estimation:
        try:
            from RURO_post_estimation import run_full_post_estimation
            
            # Get the number of individuals from precomputed data
            n_individuals = precomputed_data.n_groups
              # Get gradient function for SE computation
            # IMPORTANT: compute_standard_errors expects gradient of NEGATIVE log-likelihood
            # (i.e., gradient pointing to minimum, not maximum). This ensures the Hessian
            # is positive definite and varcov = inv(Hessian) has positive diagonal.
            if is_singles:
                # Singles: return NEGATIVE of analytical gradient (grad of NLL)
                def grad_func(theta):
                    grad_ll = fast_analytical_gradient_singles(
                        theta, precomputed_data, is_male=is_male, wage_spec=args.wage_spec
                    )
                    return -grad_ll  # Convert to gradient of NLL
            else:
                # Couples: fast_neg_ll_with_grad_couples already returns gradient of NLL
                def grad_func(theta):
                    _, neg_grad = fast_neg_ll_with_grad_couples(
                        theta, precomputed_data, wage_spec=args.wage_spec
                    )
                    return neg_grad  # Already gradient of NLL (don't negate!)
            
            out_dir = Path(args.out_file).parent if args.out_file else Path("outputs/estimates/fr")
            
            # Determine sex label
            sex_label = "pooled"
            if args.sex == "m":
                sex_label = "male"
            elif args.sex == "f":
                sex_label = "female"
            
            post_results = run_full_post_estimation(
                result=result,
                grad_func=grad_func,
                param_names=param_names,
                n_individuals=n_individuals,
                df=df,  # Use df which is the filtered DataFrame in scope
                wage_spec=args.wage_spec,
                sex=sex_label,
                out_dir=out_dir,
                save_excel=True,
                save_plots=True,
                save_html=True,
            )
            
            LOGGER.info("Post-estimation analysis complete.")
            
        except ImportError as e:
            LOGGER.warning(f"Could not run post-estimation: {e}")
        except Exception as e:
            LOGGER.error(f"Post-estimation failed: {e}")
            import traceback
            traceback.print_exc()
    
    LOGGER.info("=" * 60)
    LOGGER.info("Done.")


if __name__ == "__main__":
    main()
