#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-12-05
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/

"""
RURO_estimate_FR.py
===================

Estimation script for a **RURO (Random Utility, Random Opportunity)** labor supply
model for France, based on an already prepared RURO-MNL long dataset.

This follows Stijn Van Houtven's Belgian RURO code and the Aaberge–Colombino
methodology (Aaberge & Colombino, 1998; Capeau & Decoster, 2014).

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
MEAN_DISPY_NORM = 2500.0  # normalization constant for consumption (Stijn uses 2500)
MEAN_LHW_NORM = 35.0      # normalization constant for leisure (Stijn uses 35)


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
    """
    # Core utility variables
    c: np.ndarray           # normalized consumption, shape (n,)
    l: np.ndarray           # normalized leisure, shape (n,)
    log_age: np.ndarray     # log(age)
    log_age2: np.ndarray    # log(age)^2
    
    # Children dummies
    children0_3: np.ndarray
    children4_6: np.ndarray
    children7_9: np.ndarray
    
    # Education dummies
    educL: np.ndarray
    educH: np.ndarray
    
    # Region dummies (NUTS1: 1=baseline, 2-9 estimated)
    reg2: np.ndarray
    reg3: np.ndarray
    reg4: np.ndarray
    reg5: np.ndarray
    reg6: np.ndarray
    reg7: np.ndarray
    reg8: np.ndarray
    reg9: np.ndarray
    
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
    yd1: np.ndarray
    yd2: np.ndarray
    
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
    """
    # Core utility variables (household-level)
    c: np.ndarray               # normalized household consumption, shape (n,)
    
    # Male partner leisure and demographics
    l_m: np.ndarray             # normalized leisure for male
    log_age_m: np.ndarray       # log(age) male
    log_age2_m: np.ndarray      # log(age)^2 male
    educL_m: np.ndarray         # low education male
    educH_m: np.ndarray         # high education male
    
    # Female partner leisure and demographics
    l_f: np.ndarray             # normalized leisure for female
    log_age_f: np.ndarray       # log(age) female
    log_age2_f: np.ndarray      # log(age)^2 female
    educL_f: np.ndarray         # low education female
    educH_f: np.ndarray         # high education female
    
    # Children dummies (household-level)
    children0_3: np.ndarray
    children4_6: np.ndarray
    children7_9: np.ndarray
    
    # Region dummies (household-level, NUTS1: 1=baseline, 2-9 estimated)
    reg2: np.ndarray
    reg3: np.ndarray
    reg4: np.ndarray
    reg5: np.ndarray
    reg6: np.ndarray
    reg7: np.ndarray
    reg8: np.ndarray
    reg9: np.ndarray
    
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
    
    # Year dummies (if needed for wage equation)
    yd1: np.ndarray
    yd2: np.ndarray
    
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
        return np.ascontiguousarray(arr, dtype=np.float64)
      # -------------------------------------------------------------------------
    # Consumption and leisure (normalized)
    # -------------------------------------------------------------------------
    # Check c_norm first, but only use if it has non-NaN values
    c = None
    if "c_norm" in df.columns and not df["c_norm"].isna().all():
        c = df["c_norm"].to_numpy(dtype=np.float64)
    if c is None and "dispy_util" in df.columns and not df["dispy_util"].isna().all():
        c = df["dispy_util"].to_numpy(dtype=np.float64)
    if c is None and "consumption" in df.columns:
        c = df["consumption"].to_numpy(dtype=np.float64) / MEAN_DISPY_NORM
    if c is None and "ils_dispy" in df.columns:
        c = df["ils_dispy"].to_numpy(dtype=np.float64) / MEAN_DISPY_NORM
    if c is None:
        c = np.ones(n, dtype=np.float64)
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
    # Age
    # -------------------------------------------------------------------------
    if "dag" in df.columns:
        age = pd.to_numeric(df["dag"], errors="coerce").fillna(40).to_numpy(dtype=np.float64)
        log_age = np.log(np.clip(age, 18, 65))
        log_age2 = log_age ** 2
    else:
        log_age = np.zeros(n, dtype=np.float64)
        log_age2 = np.zeros(n, dtype=np.float64)
    log_age = np.ascontiguousarray(log_age)
    log_age2 = np.ascontiguousarray(log_age2)
    
    # -------------------------------------------------------------------------
    # Children, education dummies
    # -------------------------------------------------------------------------
    children0_3 = safe_get("children0_3")
    children4_6 = safe_get("children4_6")
    children7_9 = safe_get("children7_9")
    educL = safe_get("educL")
    educH = safe_get("educH")
    
    # -------------------------------------------------------------------------
    # Region dummies (from drgn1 or pre-computed)
    # -------------------------------------------------------------------------
    if "drgn1" in df.columns:
        drgn1 = pd.to_numeric(df["drgn1"], errors="coerce").fillna(1).to_numpy()
        reg2 = np.ascontiguousarray((drgn1 == 2).astype(np.float64))
        reg3 = np.ascontiguousarray((drgn1 == 3).astype(np.float64))
        reg4 = np.ascontiguousarray((drgn1 == 4).astype(np.float64))
        reg5 = np.ascontiguousarray((drgn1 == 5).astype(np.float64))
        reg6 = np.ascontiguousarray((drgn1 == 6).astype(np.float64))
        reg7 = np.ascontiguousarray((drgn1 == 7).astype(np.float64))
        reg8 = np.ascontiguousarray((drgn1 == 8).astype(np.float64))
        reg9 = np.ascontiguousarray((drgn1 == 9).astype(np.float64))
    else:
        reg2 = safe_get("reg_nuts1_2")
        reg3 = safe_get("reg_nuts1_3")
        reg4 = safe_get("reg_nuts1_4")
        reg5 = safe_get("reg_nuts1_5")
        reg6 = safe_get("reg_nuts1_6")
        reg7 = safe_get("reg_nuts1_7")
        reg8 = safe_get("reg_nuts1_8")
        reg9 = safe_get("reg_nuts1_9")
    
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
    
    yd1 = safe_get("yd1")
    yd2 = safe_get("yd2")
    
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
        c=c, l=l, log_age=log_age, log_age2=log_age2,
        children0_3=children0_3, children4_6=children4_6, children7_9=children7_9,
        educL=educL, educH=educH,
        reg2=reg2, reg3=reg3, reg4=reg4, reg5=reg5, reg6=reg6, reg7=reg7, reg8=reg8, reg9=reg9,
        working=working, working_pt1=working_pt1, working_pt2=working_pt2, working_ft=working_ft,
        gsur=gsur, log_wage=log_wage, pexp=pexp, pexp2=pexp2, yd1=yd1, yd2=yd2,
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
    -------
    PrecomputedDataCouples
        All arrays needed for estimation, pre-extracted and contiguous
    """
    n = len(df)
    
    def safe_get(col: str, default: float = 0.0) -> np.ndarray:
        if col in df.columns:
            arr = pd.to_numeric(df[col], errors="coerce").fillna(default).to_numpy()
        else:
            arr = np.full(n, default)
        return np.ascontiguousarray(arr, dtype=np.float64)
    
    # Consumption (household-level, normalized)
    c = None
    if "c_norm" in df.columns and not df["c_norm"].isna().all():
        c = df["c_norm"].to_numpy(dtype=np.float64)
    if c is None and "consumption" in df.columns:
        c = df["consumption"].to_numpy(dtype=np.float64) / MEAN_DISPY_NORM
    if c is None:
        ils_m = pd.to_numeric(df.get("ils_dispy_m", 0), errors="coerce").fillna(0).to_numpy()
        ils_f = pd.to_numeric(df.get("ils_dispy_f", 0), errors="coerce").fillna(0).to_numpy()
        c = (ils_m + ils_f) / MEAN_DISPY_NORM
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
    
    # Age - male
    if "dag_m" in df.columns:
        age_m = pd.to_numeric(df["dag_m"], errors="coerce").fillna(40).to_numpy(dtype=np.float64)
        log_age_m = np.log(np.clip(age_m, 18, 65))
        log_age2_m = log_age_m ** 2
    else:
        log_age_m = np.zeros(n, dtype=np.float64)
        log_age2_m = np.zeros(n, dtype=np.float64)
    log_age_m = np.ascontiguousarray(log_age_m)
    log_age2_m = np.ascontiguousarray(log_age2_m)
    
    # Age - female
    if "dag_f" in df.columns:
        age_f = pd.to_numeric(df["dag_f"], errors="coerce").fillna(40).to_numpy(dtype=np.float64)
        log_age_f = np.log(np.clip(age_f, 18, 65))
        log_age2_f = log_age_f ** 2
    else:
        log_age_f = np.zeros(n, dtype=np.float64)
        log_age2_f = np.zeros(n, dtype=np.float64)
    log_age_f = np.ascontiguousarray(log_age_f)
    log_age2_f = np.ascontiguousarray(log_age2_f)
    
    # Education
    educL_m = safe_get("educL_m")
    educH_m = safe_get("educH_m")
    educL_f = safe_get("educL_f")
    educH_f = safe_get("educH_f")
    
    # Children (household-level)
    children0_3 = safe_get("children0_3")
    children4_6 = safe_get("children4_6")
    children7_9 = safe_get("children7_9")
    
    # Region dummies
    if "drgn1" in df.columns:
        drgn1 = pd.to_numeric(df["drgn1"], errors="coerce").fillna(1).to_numpy()
        reg2 = np.ascontiguousarray((drgn1 == 2).astype(np.float64))
        reg3 = np.ascontiguousarray((drgn1 == 3).astype(np.float64))
        reg4 = np.ascontiguousarray((drgn1 == 4).astype(np.float64))
        reg5 = np.ascontiguousarray((drgn1 == 5).astype(np.float64))
        reg6 = np.ascontiguousarray((drgn1 == 6).astype(np.float64))
        reg7 = np.ascontiguousarray((drgn1 == 7).astype(np.float64))
        reg8 = np.ascontiguousarray((drgn1 == 8).astype(np.float64))
        reg9 = np.ascontiguousarray((drgn1 == 9).astype(np.float64))
    else:
        reg2 = safe_get("reg2")
        reg3 = safe_get("reg3")
        reg4 = safe_get("reg4")
        reg5 = safe_get("reg5")
        reg6 = safe_get("reg6")
        reg7 = safe_get("reg7")
        reg8 = safe_get("reg8")
        reg9 = safe_get("reg9")
    
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
    
    # Year dummies
    yd1 = safe_get("yd1")
    yd2 = safe_get("yd2")
    
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
        c=c, l_m=l_m, log_age_m=log_age_m, log_age2_m=log_age2_m,
        educL_m=educL_m, educH_m=educH_m,
        l_f=l_f, log_age_f=log_age_f, log_age2_f=log_age2_f,
        educL_f=educL_f, educH_f=educH_f,
        children0_3=children0_3, children4_6=children4_6, children7_9=children7_9,
        reg2=reg2, reg3=reg3, reg4=reg4, reg5=reg5, reg6=reg6, reg7=reg7, reg8=reg8, reg9=reg9,
        working_m=working_m, working_pt1_m=working_pt1_m, working_pt2_m=working_pt2_m,
        working_ft_m=working_ft_m, gsur_m=gsur_m,
        working_f=working_f, working_pt1_f=working_pt1_f, working_pt2_f=working_pt2_f,
        working_ft_f=working_ft_f, gsur_f=gsur_f,
        log_wage_m=log_wage_m, pexp_m=pexp_m, pexp2_m=pexp2_m,
        log_wage_f=log_wage_f, pexp_f=pexp_f, pexp2_f=pexp2_f,
        yd1=yd1, yd2=yd2, log_prior=log_prior, group_idx=group_idx, n_groups=n_groups,
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
    
    Box-Cox utility structure (Stijn's `ff_calc_util` for singles):
        u = (β_leisure_terms) * (l^θ_l - 1)/θ_l + β_c * (c^θ_c - 1)/θ_c
    
    where β_leisure_terms = β_l0 + β_l_age*log(age) + β_l_age2*log(age)^2
                          + β_l_ch4_6*children4_6 + β_l_ch7_9*children7_9
                          + β_l_regW*regW + β_l_regB*regB (Belgium) or region dummies (France)
                          + β_l_educL*educL + β_l_educH*educH
    """
    # Leisure coefficients
    beta_l0: float = 1.0          # intercept for leisure term
    beta_l_log_age: float = 0.0   # coefficient on log(age)
    beta_l_log_age2: float = 0.0  # coefficient on log(age)^2
    beta_l_ch0_3: float = 0.0     # children 0-3 (females only in Stijn)
    beta_l_ch4_6: float = 0.0     # children 4-6
    beta_l_ch7_9: float = 0.0     # children 7-9
    beta_l_educL: float = 0.0     # low education
    beta_l_educH: float = 0.0     # high education
    # Region coefficients (France: 10 NUTS1 regions, region 1 = Île-de-France as baseline)
    # We'll use a simplified version with a few region dummies
    beta_l_reg2: float = 0.0      # placeholder for region effects
    
    # Consumption coefficient
    beta_c: float = 1.0           # coefficient on consumption utility
    
    # Box-Cox exponents
    theta_l: float = 0.5          # Box-Cox exponent on leisure
    theta_c: float = 0.5          # Box-Cox exponent on consumption


@dataclass
class PrefParamsCouples:
    """
    Preference parameters for couples (joint utility over male and female leisure).
    
    Box-Cox utility structure (Stijn's `ff_calc_util` for couples):
        u = (male leisure terms) * (l_m^θ_lm - 1)/θ_lm
          + (female leisure terms) * (l_f^θ_lf - 1)/θ_lf
          + β_c * ((c_m + c_f)^θ_c - 1)/θ_c
          + β_cross * transformed_leisure_m * transformed_leisure_f
    """
    # Male leisure coefficients
    beta_lm0: float = 1.0
    beta_lm_log_age: float = 0.0
    beta_lm_log_age2: float = 0.0
    beta_lm_ch0_3: float = 0.0
    beta_lm_ch4_6: float = 0.0
    beta_lm_ch7_9: float = 0.0
    beta_lm_educL: float = 0.0
    beta_lm_educH: float = 0.0
    beta_lm_reg2: float = 0.0
    
    # Female leisure coefficients
    beta_lf0: float = 1.0
    beta_lf_log_age: float = 0.0
    beta_lf_log_age2: float = 0.0
    beta_lf_ch0_3: float = 0.0
    beta_lf_ch4_6: float = 0.0
    beta_lf_ch7_9: float = 0.0
    beta_lf_educL: float = 0.0
    beta_lf_educH: float = 0.0
    beta_lf_reg2: float = 0.0
    
    # Consumption coefficient (joint)
    beta_c: float = 1.0
    
    # Cross-leisure interaction
    beta_cross: float = 0.0
    
    # Box-Cox exponents
    theta_lm: float = 0.5   # male leisure
    theta_lf: float = 0.5   # female leisure
    theta_c: float = 0.5    # consumption


@dataclass
class HoursOppParams:
    """
    Hours opportunity density parameters (Stijn's `ff_calc_hopp`).
    
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
                   + Σ_r β_work_region_r * region_r * 1{h>0}
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
    
    # Region interactions with working (France drgn1: 1=Île-de-France as baseline)
    # Stijn uses regW, regB for Belgium (Wallonia, Brussels)
    # For France we use drgn1 regions (10 total, 1 baseline → 9 dummies)
    beta_work_reg2: float = 0.0   # Region 2 (placeholder - expand as needed)
    beta_work_reg3: float = 0.0   # Region 3
    # TODO: Add remaining France regions (drgn1 = 4..10)


@dataclass
class WageOppParams:
    """
    Wage opportunity density parameters (Stijn's `ff_calc_wopp`).
    
    This captures the distribution of wage offers conditional on working.
    Wages are modeled as log-normal with mean depending on individual characteristics.
    
    **Log-wage equation** (Mincer-style):
        E[log(w)] = β0 + β_educL*educL + β_educH*educH
                      + β_pexp*pexp + β_pexp2*pexp²
                      + Σ_r β_region_r*region_r
                      + Σ_t β_year_t*year_t
    
    **Log-normal pdf** (log of density):
        For w > 0:
        log f(w | X) = -0.5 * ((log(w) - μ(X)) / σ)² - log(σ) - log(w) - 0.5*log(2π)
        
        For h = 0 (not working):
        log f(w | X) = 0  (wage is structurally 0, no density contribution)
    
    Note: The -log(w) term comes from the Jacobian of the log transformation.
    The constant -0.5*log(2π) cancels in the likelihood ratio and is omitted.
    
    In Stijn's R code:
        wopp = ifelse(working==0, 0, -0.5*((log(wage)-lw)/sigma)^2 - log(sigma*wage*sqrt(2*pi)))
    """
    # Intercept (baseline log wage for someone with educM, no experience, baseline region/year)
    beta0: float = 2.5        # log hourly wage ≈ exp(2.5) ≈ 12€/h
    
    # Education effects on log wage
    beta_educL: float = -0.1  # low education penalty (negative)
    beta_educH: float = 0.2   # high education premium (positive)
    
    # Experience effects (Mincer equation: concave in experience)
    # Note: Stijn uses pexp in "hundreds of years" (pexp = years/100)
    beta_pexp: float = 0.02   # linear experience term
    beta_pexp2: float = -0.001  # quadratic experience term (negative for concavity)
      # Region effects on log wage (France drgn1: 1=Île-de-France as baseline)
    # Île-de-France typically has wage premium relative to other regions
    # France NUTS1 regions:
    #   1 = Île-de-France (baseline)
    #   2 = Bassin Parisien
    #   3 = Nord-Pas-de-Calais
    #   4 = Est
    #   5 = Ouest
    #   6 = Sud-Ouest
    #   7 = Centre-Est
    #   8 = Méditerranée
    #   9 = Overseas (DOM)
    beta_reg2: float = 0.0    # Bassin Parisien
    beta_reg3: float = 0.0    # Nord-Pas-de-Calais
    beta_reg4: float = 0.0    # Est
    beta_reg5: float = 0.0    # Ouest
    beta_reg6: float = 0.0    # Sud-Ouest
    beta_reg7: float = 0.0    # Centre-Est
    beta_reg8: float = 0.0    # Méditerranée
    beta_reg9: float = 0.0    # Overseas (DOM)
    
    # Year dummies (to capture wage growth over time)
    beta_yd1: float = 0.0     # year dummy 1 (e.g., 2017 vs 2019)
    beta_yd2: float = 0.0     # year dummy 2 (e.g., 2015 vs 2019)
    
    # Standard deviation of log-wage residual
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
    
    Parameter order (total 30 for vw, 20 for fw):
    
    PREFERENCES (12 params):
      [0]  beta_l0          - leisure intercept
      [1]  beta_l_log_age   - log(age) effect on leisure
      [2]  beta_l_log_age2  - log(age)² effect
      [3]  beta_l_ch4_6     - children 4-6 effect
      [4]  beta_l_ch7_9     - children 7-9 effect
      [5]  beta_l_educL     - low education effect
      [6]  beta_l_educH     - high education effect
      [7]  beta_l_reg2      - region effect (placeholder)
      [8]  beta_c           - consumption coefficient
      [9]  theta_l          - Box-Cox exponent for leisure
      [10] theta_c          - Box-Cox exponent for consumption
      [11] beta_l_ch0_3     - children 0-3 effect (females mainly)
    
    HOURS OPPORTUNITY (9 params):
      [12] beta_work        - working indicator
      [13] beta_pt1         - 20h focal point
      [14] beta_pt2         - 30h focal point
      [15] beta_ft          - 40h focal point
      [16] beta_gsur        - group-specific unemployment rate
      [17] beta_work_educL  - low education × working
      [18] beta_work_educH  - high education × working
      [19] beta_work_reg2   - region 2 × working
      [20] beta_work_reg3   - region 3 × working
      WAGE OPPORTUNITY (16 params, used only for wage_spec="vw"):
      [21] beta0            - log-wage intercept
      [22] beta_educL       - low education wage penalty
      [23] beta_educH       - high education wage premium
      [24] beta_pexp        - experience (linear)
      [25] beta_pexp2       - experience (quadratic)
      [26] beta_reg2        - Bassin Parisien wage effect
      [27] beta_reg3        - Nord-Pas-de-Calais wage effect
      [28] beta_reg4        - Est wage effect
      [29] beta_reg5        - Ouest wage effect
      [30] beta_reg6        - Sud-Ouest wage effect
      [31] beta_reg7        - Centre-Est wage effect
      [32] beta_reg8        - Méditerranée wage effect
      [33] beta_reg9        - Overseas (DOM) wage effect
      [34] beta_yd1         - year dummy 1
      [35] beta_yd2         - year dummy 2
      [36] sigma            - std dev of log-wage
    """
    theta = np.array([
        # Preference parameters (12)
        pref.beta_l0,           # 0
        pref.beta_l_log_age,    # 1
        pref.beta_l_log_age2,   # 2
        pref.beta_l_ch4_6,      # 3
        pref.beta_l_ch7_9,      # 4
        pref.beta_l_educL,      # 5
        pref.beta_l_educH,      # 6
        pref.beta_l_reg2,       # 7
        pref.beta_c,            # 8
        pref.theta_l,           # 9
        pref.theta_c,           # 10
        pref.beta_l_ch0_3,      # 11
        # Hours opportunity parameters (9)
        hopp.beta_work,         # 12
        hopp.beta_pt1,          # 13
        hopp.beta_pt2,          # 14
        hopp.beta_ft,           # 15
        hopp.beta_gsur,         # 16
        hopp.beta_work_educL,   # 17
        hopp.beta_work_educH,   # 18
        hopp.beta_work_reg2,    # 19
        hopp.beta_work_reg3,    # 20
        # Wage opportunity parameters (16) - used only for vw
        wopp.beta0,             # 21
        wopp.beta_educL,        # 22
        wopp.beta_educH,        # 23
        wopp.beta_pexp,         # 24
        wopp.beta_pexp2,        # 25
        wopp.beta_reg2,         # 26
        wopp.beta_reg3,         # 27
        wopp.beta_reg4,         # 28
        wopp.beta_reg5,         # 29
        wopp.beta_reg6,         # 30
        wopp.beta_reg7,         # 31
        wopp.beta_reg8,         # 32
        wopp.beta_reg9,         # 33
        wopp.beta_yd1,          # 34
        wopp.beta_yd2,          # 35
        wopp.sigma,             # 36
    ])
    return theta


def unpack_theta_singles(theta: np.ndarray, wage_spec: str = "vw") -> Tuple[PrefParamsSingles, HoursOppParams, WageOppParams]:
    """
    Unpack flat parameter array into dataclasses.
    
    Parameters
    ----------
    theta : np.ndarray
        Parameter vector. Length 21 for fw (pref+hopp), 37 for vw (pref+hopp+wopp).
    wage_spec : str
        "fw" (fixed wages, 21 params) or "vw" (variable wages, 37 params)
    
    Returns
    -------
    pref, hopp, wopp : tuple of dataclasses
        For fw mode, wopp will have default values (not used).
    """
    pref = PrefParamsSingles(
        beta_l0=theta[0],
        beta_l_log_age=theta[1],
        beta_l_log_age2=theta[2],
        beta_l_ch4_6=theta[3],
        beta_l_ch7_9=theta[4],
        beta_l_educL=theta[5],
        beta_l_educH=theta[6],
        beta_l_reg2=theta[7],
        beta_c=theta[8],
        theta_l=theta[9],
        theta_c=theta[10],
        beta_l_ch0_3=theta[11],
    )
    hopp = HoursOppParams(
        beta_work=theta[12],
        beta_pt1=theta[13],
        beta_pt2=theta[14],
        beta_ft=theta[15],
        beta_gsur=theta[16],
        beta_work_educL=theta[17],
        beta_work_educH=theta[18],
        beta_work_reg2=theta[19],
        beta_work_reg3=theta[20],
    )
    
    # For fw mode, wage opp params are not used - return defaults
    if wage_spec == "fw" or len(theta) <= 21:
        wopp = WageOppParams()
    else:
        wopp = WageOppParams(
            beta0=theta[21],
            beta_educL=theta[22],
            beta_educH=theta[23],
            beta_pexp=theta[24],
            beta_pexp2=theta[25],
            beta_reg2=theta[26],
            beta_reg3=theta[27],
            beta_reg4=theta[28],
            beta_reg5=theta[29],
            beta_reg6=theta[30],
            beta_reg7=theta[31],
            beta_reg8=theta[32],
            beta_reg9=theta[33],
            beta_yd1=theta[34],
            beta_yd2=theta[35],
            sigma=theta[36],
        )
    return pref, hopp, wopp


def get_initial_theta_singles(is_male: bool = True) -> np.ndarray:
    """
    Get reasonable initial parameter values for singles estimation.
    
    Based loosely on Stijn's estimates for Belgium.
    """
    pref = PrefParamsSingles(
        beta_l0=1.0,
        beta_l_log_age=0.0,
        beta_l_log_age2=0.0,
        beta_l_ch4_6=0.0 if is_male else 0.1,
        beta_l_ch7_9=0.0,
        beta_l_educL=0.0,
        beta_l_educH=0.0,
        beta_l_reg2=0.0,
        beta_c=1.0,
        theta_l=0.5,
        theta_c=0.5,
        beta_l_ch0_3=0.0 if is_male else 0.2,
    )
    hopp = HoursOppParams(
        beta_work=0.5,
        beta_pt1=0.0,
        beta_pt2=0.0,
        beta_ft=0.0,
        beta_gsur=0.0,        beta_work_educL=0.0,
        beta_work_educH=0.0,
        beta_work_reg2=0.0,
        beta_work_reg3=0.0,
    )
    wopp = WageOppParams(
        beta0=2.5,
        beta_educL=-0.1,
        beta_educH=0.2,
        beta_pexp=0.02,
        beta_pexp2=-0.001,
        beta_reg2=-0.05,   # Bassin Parisien (slight Paris premium)
        beta_reg3=-0.05,   # Nord-Pas-de-Calais
        beta_reg4=-0.05,   # Est
        beta_reg5=-0.05,   # Ouest
        beta_reg6=-0.05,   # Sud-Ouest
        beta_reg7=-0.05,   # Centre-Est
        beta_reg8=-0.05,   # Méditerranée
        beta_reg9=-0.10,   # Overseas (DOM) - typically larger gap
        beta_yd1=0.0,
        beta_yd2=0.0,
        sigma=0.4,
    )
    return pack_theta_singles(pref, hopp, wopp)


def get_param_names_singles() -> List[str]:
    """
    Return list of parameter names for singles, aligned with pack_theta_singles order.
    
    This mirrors Stijn's parameter naming convention and is used for output display.
    """
    return [
        # Preference parameters (12)
        "pref.beta_l0",           # 0
        "pref.beta_l_log_age",    # 1
        "pref.beta_l_log_age2",   # 2
        "pref.beta_l_ch4_6",      # 3
        "pref.beta_l_ch7_9",      # 4
        "pref.beta_l_educL",      # 5
        "pref.beta_l_educH",      # 6
        "pref.beta_l_reg2",       # 7
        "pref.beta_c",            # 8
        "pref.theta_l",           # 9
        "pref.theta_c",           # 10
        "pref.beta_l_ch0_3",      # 11
        # Hours opportunity parameters (9)
        "hopp.beta_work",         # 12
        "hopp.beta_pt1",          # 13
        "hopp.beta_pt2",          # 14
        "hopp.beta_ft",           # 15
        "hopp.beta_gsur",         # 16
        "hopp.beta_work_educL",   # 17
        "hopp.beta_work_educH",   # 18
        "hopp.beta_work_reg2",    # 19
        "hopp.beta_work_reg3",    # 20
        # Wage opportunity parameters (16)
        "wopp.beta0",                      # 21
        "wopp.beta_educL",                 # 22
        "wopp.beta_educH",                 # 23
        "wopp.beta_pexp",                  # 24
        "wopp.beta_pexp2",                 # 25
        "wopp.beta_reg2_BassinParisien",   # 26
        "wopp.beta_reg3_NordPasDeCalais",  # 27
        "wopp.beta_reg4_Est",              # 28
        "wopp.beta_reg5_Ouest",            # 29
        "wopp.beta_reg6_SudOuest",         # 30
        "wopp.beta_reg7_CentreEst",        # 31
        "wopp.beta_reg8_Mediterranee",     # 32
        "wopp.beta_reg9_DOM",              # 33
        "wopp.beta_yd1",                   # 34
        "wopp.beta_yd2",                   # 35
        "wopp.sigma",                      # 36
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
        return result    @njit(cache=True, fastmath=True)
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
    
    Stijn's structure for singles:
        u = (β_l0 + β_l_log_age*log(age) + β_l_log_age2*log(age)^2
             + β_l_ch4_6*children4_6 + β_l_ch7_9*children7_9
             + β_l_educL*educL + β_l_educH*educH + region terms)
            * (l^θ_l - 1)/θ_l
          + β_c * (c^θ_c - 1)/θ_c
    
    Parameters
    ----------
    df : pd.DataFrame
        Long-format RURO-MNL dataset for singles.
    pref : PrefParamsSingles
        Preference parameters.
    is_male : bool
        If True, this is single males; if False, single females.
        (Affects which child variables matter, following Stijn.)
    
    Returns
    -------
    u : np.ndarray
        Utility values, shape (n_rows,).
    """
    n = len(df)
    
    # -------------------------------------------------------------------------
    # Normalized consumption and leisure
    # -------------------------------------------------------------------------
    # Try different column names that might be in the dataset
    # IMPORTANT: Check not just existence but also that values are valid (not all NaN)
    c = None
    if "c_norm" in df.columns and not df["c_norm"].isna().all():
        c = df["c_norm"].to_numpy()
    if c is None and "dispy_util" in df.columns and not df["dispy_util"].isna().all():
        c = df["dispy_util"].to_numpy()
    if c is None and "consumption" in df.columns and not df["consumption"].isna().all():
        # Normalize consumption by MEAN_DISPY_NORM
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
        # Normalize leisure: (TOTAL_LEISURE - hours) / (TOTAL_LEISURE - MEAN_LHW)
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
    # Covariates for leisure term
    # -------------------------------------------------------------------------
    # Age (log and log^2)
    if "dag" in df.columns:
        age = pd.to_numeric(df["dag"], errors="coerce").fillna(40).to_numpy()
        log_age = np.log(np.clip(age, 18, 65))
        log_age2 = log_age ** 2
    else:
        log_age = np.zeros(n)
        log_age2 = np.zeros(n)
    
    # Children variables (using helper to safely get columns)
    children0_3 = _get_col(df, "children0_3", 0.0)
    children4_6 = _get_col(df, "children4_6", 0.0)
    children7_9 = _get_col(df, "children7_9", 0.0)
    
    # Education dummies
    educL = _get_col(df, "educL", 0.0)
    educH = _get_col(df, "educH", 0.0)
    
    # Region dummy (placeholder - should be expanded for all France NUTS1 regions)
    # TODO: Add full region dummies (reg_nuts1_2, ..., reg_nuts1_10)
    reg2 = _get_col(df, "reg_nuts1_2", 0.0)
    
    # -------------------------------------------------------------------------
    # Build leisure coefficient (varies by covariates)
    # -------------------------------------------------------------------------
    beta_leisure = (
        pref.beta_l0
        + pref.beta_l_log_age * log_age
        + pref.beta_l_log_age2 * log_age2
        + pref.beta_l_ch4_6 * children4_6
        + pref.beta_l_ch7_9 * children7_9
        + pref.beta_l_educL * educL
        + pref.beta_l_educH * educH
        + pref.beta_l_reg2 * reg2
    )
    
    # For females, also include children 0-3 (Stijn does this)
    if not is_male:
        beta_leisure = beta_leisure + pref.beta_l_ch0_3 * children0_3
    
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
    
    Following Stijn's structure for couples (ff_calc_util with type=="cou"):
        u = (β_l0_m + β_l_log_age_m*log(dag_m) + β_l_log_age2_m*log(dag_m)^2
             + β_l_ch0_3_m*children0_3 + β_l_ch4_6_m*children4_6 + β_l_ch7_9_m*children7_9
             + β_l_reg2_m*regW + β_l_reg3_m*regB + β_l_educL_m*educL_m + β_l_educH_m*educH_m)
            * (l_m^θ_l_m - 1)/θ_l_m
          + (β_l0_f + ... female terms ...)
            * (l_f^θ_l_f - 1)/θ_l_f
          + β_c * ((c_m + c_f)^θ_c - 1)/θ_c
          + β_interaction * BC(l_m) * BC(l_f)
    
    The dataset should have _m and _f suffixes for male and female partner variables.
    
    Parameters
    ----------
    df : pd.DataFrame
        Long-format RURO-MNL dataset for couples. Must have columns with _m and _f
        suffixes for male and female partner characteristics.
    pref : PrefParamsCouples
        Couples preference parameters (25 total).
    
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
    # Covariates for male partner
    # -------------------------------------------------------------------------
    if "dag_m" in df.columns:
        age_m = pd.to_numeric(df["dag_m"], errors="coerce").fillna(40).to_numpy()
        log_age_m = np.log(np.clip(age_m, 18, 65))
        log_age2_m = log_age_m ** 2
    else:
        log_age_m = np.zeros(n)
        log_age2_m = np.zeros(n)
    
    educL_m = _get_col(df, "educL_m", 0.0)
    educH_m = _get_col(df, "educH_m", 0.0)
    
    # -------------------------------------------------------------------------
    # Covariates for female partner
    # -------------------------------------------------------------------------
    if "dag_f" in df.columns:
        age_f = pd.to_numeric(df["dag_f"], errors="coerce").fillna(40).to_numpy()
        log_age_f = np.log(np.clip(age_f, 18, 65))
        log_age2_f = log_age_f ** 2
    else:
        log_age_f = np.zeros(n)
        log_age2_f = np.zeros(n)
    
    educL_f = _get_col(df, "educL_f", 0.0)
    educH_f = _get_col(df, "educH_f", 0.0)
    
    # -------------------------------------------------------------------------
    # Household-level covariates (shared by both partners)
    # -------------------------------------------------------------------------
    children0_3 = _get_col(df, "children0_3", 0.0)
    children4_6 = _get_col(df, "children4_6", 0.0)
    children7_9 = _get_col(df, "children7_9", 0.0)
    
    # Region dummies (household-level, using regW/regB for Belgium or drgn1 for France)
    reg2 = _get_col(df, "regW", 0.0)
    if reg2.sum() == 0:
        reg2 = _get_col(df, "reg_nuts1_2", 0.0)
    reg3 = _get_col(df, "regB", 0.0)
    if reg3.sum() == 0:
        reg3 = _get_col(df, "reg_nuts1_3", 0.0)
    
    # -------------------------------------------------------------------------
    # Build male leisure coefficient
    # -------------------------------------------------------------------------
    beta_leisure_m = (
        pref.beta_l0_m
        + pref.beta_l_log_age_m * log_age_m
        + pref.beta_l_log_age2_m * log_age2_m
        + pref.beta_l_ch0_3_m * children0_3
        + pref.beta_l_ch4_6_m * children4_6
        + pref.beta_l_ch7_9_m * children7_9
        + pref.beta_l_reg2_m * reg2
        + pref.beta_l_reg3_m * reg3
        + pref.beta_l_educL_m * educL_m
        + pref.beta_l_educH_m * educH_m
    )
    
    # -------------------------------------------------------------------------
    # Build female leisure coefficient
    # -------------------------------------------------------------------------
    beta_leisure_f = (
        pref.beta_l0_f
        + pref.beta_l_log_age_f * log_age_f
        + pref.beta_l_log_age2_f * log_age2_f
        + pref.beta_l_ch0_3_f * children0_3
        + pref.beta_l_ch4_6_f * children4_6
        + pref.beta_l_ch7_9_f * children7_9
        + pref.beta_l_reg2_f * reg2
        + pref.beta_l_reg3_f * reg3
        + pref.beta_l_educL_f * educL_f
        + pref.beta_l_educH_f * educH_f
    )
    
    # -------------------------------------------------------------------------
    # Box-Cox transforms
    # -------------------------------------------------------------------------
    l_m_bc = boxcox_transform(l_m, pref.theta_l_m)
    l_f_bc = boxcox_transform(l_f, pref.theta_l_f)
    c_bc = boxcox_transform(c_total, pref.theta_c)
    
    # -------------------------------------------------------------------------
    # Utility: male leisure + female leisure + consumption + interaction
    # -------------------------------------------------------------------------
    u = (
        beta_leisure_m * l_m_bc          # Male leisure utility
        + beta_leisure_f * l_f_bc        # Female leisure utility
        + pref.beta_c * c_bc             # Joint consumption utility
        + pref.beta_interaction * l_m_bc * l_f_bc  # Leisure interaction
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
    
    Stijn's structure (log density):
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
    # Region dummies (France: drgn1, or NUTS1)
    # -------------------------------------------------------------------------
    # Try different region variable names
    if "drgn1" in df.columns:
        drgn1 = pd.to_numeric(df["drgn1"], errors="coerce").fillna(1).to_numpy()
        reg2 = (drgn1 == 2).astype(float)
        reg3 = (drgn1 == 3).astype(float)
    else:
        # Fall back to pre-computed dummies
        reg2 = _get_col(df, "reg_nuts1_2", 0.0)
        if reg2.sum() == 0:
            reg2 = _get_col(df, "regW", 0.0)
        reg3 = _get_col(df, "reg_nuts1_3", 0.0)
        if reg3.sum() == 0:
            reg3 = _get_col(df, "regB", 0.0)
    
    # -------------------------------------------------------------------------
    # Hours opportunity density (log)
    # -------------------------------------------------------------------------
    h_opp = (
        hopp.beta_work * working
        + hopp.beta_pt1 * working_pt1
        + hopp.beta_pt2 * working_pt2
        + hopp.beta_ft * working_ft
        + hopp.beta_gsur * working * gsur
        + hopp.beta_work_educL * working * educL
        + hopp.beta_work_educH * working * educH
        + hopp.beta_work_reg2 * working * reg2
        + hopp.beta_work_reg3 * working * reg3
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
    
    Stijn's R code:
        lw = β0 + β_educL*educL + β_educH*educH + β_pexp*pexp + β_pexp2*pexp² + β_yd1*yd1 + β_yd2*yd2
        wopp = ifelse(working==0, 0, -0.5*((log(wage)-lw)/σ)² - log(σ*wage*sqrt(2*π)))
    
    Parameters
    ----------
    df : pd.DataFrame
        Long-format RURO-MNL dataset.
    wopp : WageOppParams
        Wage opportunity parameters.
    is_male : bool
        Gender indicator (wage equation may differ by gender; Stijn estimates separate σ).
    
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
    # Stijn uses pexp in "hundreds of years" (pexp = years/100) for numerical stability
    if "pexp" in df.columns:
        pexp = pd.to_numeric(df["pexp"], errors="coerce").fillna(0).to_numpy()
    elif "pexp_years" in df.columns:
        pexp = pd.to_numeric(df["pexp_years"], errors="coerce").fillna(0).to_numpy() / 100.0
    else:
        # Estimate from age - years of schooling - 6
        pexp = np.zeros(n)
      # -------------------------------------------------------------------------
    # Region dummies (France: drgn1 NUTS1 regions)
    # 1 = Île-de-France (baseline), 2-9 = other regions
    # -------------------------------------------------------------------------
    if "drgn1" in df.columns:
        drgn1 = pd.to_numeric(df["drgn1"], errors="coerce").fillna(1).to_numpy()
        reg2 = (drgn1 == 2).astype(float)  # Bassin Parisien
        reg3 = (drgn1 == 3).astype(float)  # Nord-Pas-de-Calais
        reg4 = (drgn1 == 4).astype(float)  # Est
        reg5 = (drgn1 == 5).astype(float)  # Ouest
        reg6 = (drgn1 == 6).astype(float)  # Sud-Ouest
        reg7 = (drgn1 == 7).astype(float)  # Centre-Est
        reg8 = (drgn1 == 8).astype(float)  # Méditerranée
        reg9 = (drgn1 == 9).astype(float)  # Overseas (DOM)
    else:
        # Fall back to pre-computed dummies
        reg2 = _get_col(df, "reg_nuts1_2", 0.0)
        reg3 = _get_col(df, "reg_nuts1_3", 0.0)
        reg4 = _get_col(df, "reg_nuts1_4", 0.0)
        reg5 = _get_col(df, "reg_nuts1_5", 0.0)
        reg6 = _get_col(df, "reg_nuts1_6", 0.0)
        reg7 = _get_col(df, "reg_nuts1_7", 0.0)
        reg8 = _get_col(df, "reg_nuts1_8", 0.0)
        reg9 = _get_col(df, "reg_nuts1_9", 0.0)
    
    # -------------------------------------------------------------------------
    # Year dummies
    # -------------------------------------------------------------------------
    yd1 = _get_col(df, "yd1", 0.0)
    yd2 = _get_col(df, "yd2", 0.0)
    
    # -------------------------------------------------------------------------
    # Expected log-wage (Mincer equation with all regional effects)
    # -------------------------------------------------------------------------
    mean_logw = (
        wopp.beta0
        + wopp.beta_educL * educL
        + wopp.beta_educH * educH
        + wopp.beta_pexp * pexp
        + wopp.beta_pexp2 * (pexp ** 2)
        + wopp.beta_reg2 * reg2  # Bassin Parisien
        + wopp.beta_reg3 * reg3  # Nord-Pas-de-Calais
        + wopp.beta_reg4 * reg4  # Est
        + wopp.beta_reg5 * reg5  # Ouest
        + wopp.beta_reg6 * reg6  # Sud-Ouest
        + wopp.beta_reg7 * reg7  # Centre-Est
        + wopp.beta_reg8 * reg8  # Méditerranée
        + wopp.beta_reg9 * reg9  # Overseas (DOM)
        + wopp.beta_yd1 * yd1
        + wopp.beta_yd2 * yd2
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
    
    Following Stijn's structure:
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
    # Region dummies (household-level)
    # -------------------------------------------------------------------------
    reg2 = _get_col(df, "regW", 0.0)
    if reg2.sum() == 0:
        reg2 = _get_col(df, "reg_nuts1_2", 0.0)
    reg3 = _get_col(df, "regB", 0.0)
    if reg3.sum() == 0:
        reg3 = _get_col(df, "reg_nuts1_3", 0.0)
    
    # -------------------------------------------------------------------------
    # Hours opportunity: sum of male and female components
    # -------------------------------------------------------------------------
    h_opp_m = (
        hopp_m.beta_work * working_m
        + hopp_m.beta_pt1 * working_pt1_m
        + hopp_m.beta_pt2 * working_pt2_m
        + hopp_m.beta_ft * working_ft_m
        + hopp_m.beta_gsur * working_m * gsur_m
        + hopp_m.beta_work_educL * working_m * educL_m
        + hopp_m.beta_work_educH * working_m * educH_m
        + hopp_m.beta_work_reg2 * working_m * reg2
        + hopp_m.beta_work_reg3 * working_m * reg3
    )
    
    h_opp_f = (
        hopp_f.beta_work * working_f
        + hopp_f.beta_pt1 * working_pt1_f
        + hopp_f.beta_pt2 * working_pt2_f
        + hopp_f.beta_ft * working_ft_f
        + hopp_f.beta_gsur * working_f * gsur_f
        + hopp_f.beta_work_educL * working_f * educL_f
        + hopp_f.beta_work_educH * working_f * educH_f
        + hopp_f.beta_work_reg2 * working_f * reg2
        + hopp_f.beta_work_reg3 * working_f * reg3
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
    # Region and year dummies (household-level)
    # -------------------------------------------------------------------------
    # For France, extract from drgn1 or use pre-computed
    if "drgn1" in df.columns:
        drgn1 = pd.to_numeric(df["drgn1"], errors="coerce").fillna(1).to_numpy()
        reg2 = (drgn1 == 2).astype(float)
        reg3 = (drgn1 == 3).astype(float)
        reg4 = (drgn1 == 4).astype(float)
        reg5 = (drgn1 == 5).astype(float)
        reg6 = (drgn1 == 6).astype(float)
        reg7 = (drgn1 == 7).astype(float)
        reg8 = (drgn1 == 8).astype(float)
        reg9 = (drgn1 == 9).astype(float)
    else:
        reg2 = _get_col(df, "reg_nuts1_2", 0.0)
        reg3 = _get_col(df, "reg_nuts1_3", 0.0)
        reg4 = _get_col(df, "reg_nuts1_4", 0.0)
        reg5 = _get_col(df, "reg_nuts1_5", 0.0)
        reg6 = _get_col(df, "reg_nuts1_6", 0.0)
        reg7 = _get_col(df, "reg_nuts1_7", 0.0)
        reg8 = _get_col(df, "reg_nuts1_8", 0.0)
        reg9 = _get_col(df, "reg_nuts1_9", 0.0)
    
    yd1 = _get_col(df, "yd1", 0.0)
    yd2 = _get_col(df, "yd2", 0.0)
    
    # -------------------------------------------------------------------------
    # Mean log-wage for male (Mincer equation)
    # -------------------------------------------------------------------------
    mean_logw_m = (
        wopp_m.beta0
        + wopp_m.beta_educL * educL_m
        + wopp_m.beta_educH * educH_m
        + wopp_m.beta_pexp * pexp_m
        + wopp_m.beta_pexp2 * (pexp_m ** 2)
        + wopp_m.beta_reg2 * reg2
        + wopp_m.beta_reg3 * reg3
        + wopp_m.beta_reg4 * reg4
        + wopp_m.beta_reg5 * reg5
        + wopp_m.beta_reg6 * reg6
        + wopp_m.beta_reg7 * reg7
        + wopp_m.beta_reg8 * reg8
        + wopp_m.beta_reg9 * reg9
        + wopp_m.beta_yd1 * yd1
        + wopp_m.beta_yd2 * yd2
    )
    
    sigma_m = np.abs(wopp_m.sigma) + 1e-6
    z_m = (log_wage_m - mean_logw_m) / sigma_m
    w_opp_m = -0.5 * z_m**2 - np.log(sigma_m) - log_wage_m
    w_opp_m = np.where(working_m > 0, w_opp_m, 0.0)
    
    # -------------------------------------------------------------------------
    # Mean log-wage for female (Mincer equation)
    # -------------------------------------------------------------------------
    mean_logw_f = (
        wopp_f.beta0
        + wopp_f.beta_educL * educL_f
        + wopp_f.beta_educH * educH_f
        + wopp_f.beta_pexp * pexp_f
        + wopp_f.beta_pexp2 * (pexp_f ** 2)
        + wopp_f.beta_reg2 * reg2
        + wopp_f.beta_reg3 * reg3
        + wopp_f.beta_reg4 * reg4
        + wopp_f.beta_reg5 * reg5
        + wopp_f.beta_reg6 * reg6
        + wopp_f.beta_reg7 * reg7
        + wopp_f.beta_reg8 * reg8
        + wopp_f.beta_reg9 * reg9
        + wopp_f.beta_yd1 * yd1
        + wopp_f.beta_yd2 * yd2
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
    # Stijn uses idhh_true for all groups
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
    
    # Identify observed alternative: draw == 0 (Stijn's convention)
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
    
    Returns
    -------
    u : np.ndarray
        Utility values, shape (n_rows,)
    du_dtheta : np.ndarray
        Derivatives of u w.r.t. preference parameters, shape (n_rows, n_pref_params)
        Columns correspond to parameters [0:12] in theta (preference block)
    """
    n = len(df)
    pref, _, _ = unpack_theta_singles(theta)
    
    # Get normalized consumption and leisure (same as ff_calc_util_singles)
    # Check not just existence but also that values are valid (not all NaN)
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
    
    # Covariates
    if "dag" in df.columns:
        age = pd.to_numeric(df["dag"], errors="coerce").fillna(40).to_numpy()
        log_age = np.log(np.clip(age, 18, 65))
        log_age2 = log_age ** 2
    else:
        log_age = np.zeros(n)
        log_age2 = np.zeros(n)
    
    children0_3 = _get_col(df, "children0_3", 0.0)
    children4_6 = _get_col(df, "children4_6", 0.0)
    children7_9 = _get_col(df, "children7_9", 0.0)
    educL = _get_col(df, "educL", 0.0)
    educH = _get_col(df, "educH", 0.0)
    reg2 = _get_col(df, "reg_nuts1_2", 0.0)
    
    # Box-Cox transforms
    l_bc = boxcox_transform(l, pref.theta_l)
    c_bc = boxcox_transform(c, pref.theta_c)
    
    # Derivatives of Box-Cox w.r.t. theta_l and theta_c
    dl_bc_dtheta_l = d_boxcox_dtheta(l, pref.theta_l)
    dc_bc_dtheta_c = d_boxcox_dtheta(c, pref.theta_c)
    
    # Build beta_leisure coefficient
    beta_leisure = (
        pref.beta_l0
        + pref.beta_l_log_age * log_age
        + pref.beta_l_log_age2 * log_age2
        + pref.beta_l_ch4_6 * children4_6
        + pref.beta_l_ch7_9 * children7_9
        + pref.beta_l_educL * educL
        + pref.beta_l_educH * educH
        + pref.beta_l_reg2 * reg2
    )
    if not is_male:
        beta_leisure = beta_leisure + pref.beta_l_ch0_3 * children0_3
    
    # Utility
    u = beta_leisure * l_bc + pref.beta_c * c_bc
    
    # Derivatives w.r.t. preference parameters (12 params)
    # [0]  beta_l0, [1] beta_l_log_age, [2] beta_l_log_age2, [3] beta_l_ch4_6,
    # [4]  beta_l_ch7_9, [5] beta_l_educL, [6] beta_l_educH, [7] beta_l_reg2,
    # [8]  beta_c, [9] theta_l, [10] theta_c, [11] beta_l_ch0_3
    
    du_dtheta = np.zeros((n, 12), dtype=float)
    
    # ∂u/∂beta_l0 = l_bc
    du_dtheta[:, 0] = l_bc
    # ∂u/∂beta_l_log_age = log_age * l_bc
    du_dtheta[:, 1] = log_age * l_bc
    # ∂u/∂beta_l_log_age2 = log_age2 * l_bc
    du_dtheta[:, 2] = log_age2 * l_bc
    # ∂u/∂beta_l_ch4_6 = children4_6 * l_bc
    du_dtheta[:, 3] = children4_6 * l_bc
    # ∂u/∂beta_l_ch7_9 = children7_9 * l_bc
    du_dtheta[:, 4] = children7_9 * l_bc
    # ∂u/∂beta_l_educL = educL * l_bc
    du_dtheta[:, 5] = educL * l_bc
    # ∂u/∂beta_l_educH = educH * l_bc
    du_dtheta[:, 6] = educH * l_bc
    # ∂u/∂beta_l_reg2 = reg2 * l_bc
    du_dtheta[:, 7] = reg2 * l_bc
    # ∂u/∂beta_c = c_bc
    du_dtheta[:, 8] = c_bc
    # ∂u/∂theta_l = beta_leisure * ∂(l_bc)/∂theta_l
    du_dtheta[:, 9] = beta_leisure * dl_bc_dtheta_l
    # ∂u/∂theta_c = beta_c * ∂(c_bc)/∂theta_c
    du_dtheta[:, 10] = pref.beta_c * dc_bc_dtheta_c
    # ∂u/∂beta_l_ch0_3 = children0_3 * l_bc (only for females)
    if not is_male:
        du_dtheta[:, 11] = children0_3 * l_bc
    else:
        du_dtheta[:, 11] = 0.0
    
    return u, du_dtheta


def _compute_hopp_derivatives(
    df: pd.DataFrame,
    theta: np.ndarray,
    is_male: bool = True,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute hours opportunity density and its derivatives.
    
    Returns
    -------
    h_opp : np.ndarray
        Log hours opportunity density, shape (n_rows,)
    dh_dtheta : np.ndarray
        Derivatives w.r.t. hopp parameters, shape (n_rows, 9)
        Columns correspond to parameters [12:21] in theta
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
    
    if "drgn1" in df.columns:
        drgn1 = pd.to_numeric(df["drgn1"], errors="coerce").fillna(1).to_numpy()
        reg2 = (drgn1 == 2).astype(float)
        reg3 = (drgn1 == 3).astype(float)
    else:
        reg2 = _get_col(df, "reg_nuts1_2", 0.0)
        reg3 = _get_col(df, "reg_nuts1_3", 0.0)
    
    # h_opp value
    h_opp = (
        hopp.beta_work * working
        + hopp.beta_pt1 * working_pt1
        + hopp.beta_pt2 * working_pt2
        + hopp.beta_ft * working_ft
        + hopp.beta_gsur * working * gsur
        + hopp.beta_work_educL * working * educL
        + hopp.beta_work_educH * working * educH
        + hopp.beta_work_reg2 * working * reg2
        + hopp.beta_work_reg3 * working * reg3
    )
    
    # Derivatives (all linear, so derivatives are just the covariates)
    # [12] beta_work, [13] beta_pt1, [14] beta_pt2, [15] beta_ft,
    # [16] beta_gsur, [17] beta_work_educL, [18] beta_work_educH,
    # [19] beta_work_reg2, [20] beta_work_reg3
    
    dh_dtheta = np.zeros((n, 9), dtype=float)
    dh_dtheta[:, 0] = working
    dh_dtheta[:, 1] = working_pt1
    dh_dtheta[:, 2] = working_pt2
    dh_dtheta[:, 3] = working_ft
    dh_dtheta[:, 4] = working * gsur
    dh_dtheta[:, 5] = working * educL
    dh_dtheta[:, 6] = working * educH
    dh_dtheta[:, 7] = working * reg2
    dh_dtheta[:, 8] = working * reg3
    
    return h_opp, dh_dtheta


def _compute_wopp_derivatives(
    df: pd.DataFrame,
    theta: np.ndarray,
    is_male: bool = True,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute wage opportunity density and its derivatives.
    
    Returns
    -------
    w_opp : np.ndarray
        Log wage opportunity density, shape (n_rows,)
    dw_dtheta : np.ndarray
        Derivatives w.r.t. wopp parameters, shape (n_rows, 16)
        Columns correspond to parameters [21:37] in theta:
        [0] beta0, [1] beta_educL, [2] beta_educH, [3] beta_pexp, [4] beta_pexp2,
        [5] beta_reg2, [6] beta_reg3, [7] beta_reg4, [8] beta_reg5, [9] beta_reg6,
        [10] beta_reg7, [11] beta_reg8, [12] beta_reg9,
        [13] beta_yd1, [14] beta_yd2, [15] sigma
    """
    n = len(df)
    _, _, wopp = unpack_theta_singles(theta)
    
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
    
    # -------------------------------------------------------------------------
    # Region dummies (France: drgn1 NUTS1 regions)
    # 1 = Île-de-France (baseline), 2-9 = other regions
    # -------------------------------------------------------------------------
    if "drgn1" in df.columns:
        drgn1 = pd.to_numeric(df["drgn1"], errors="coerce").fillna(1).to_numpy()
        reg2 = (drgn1 == 2).astype(float)  # Bassin Parisien
        reg3 = (drgn1 == 3).astype(float)  # Nord-Pas-de-Calais
        reg4 = (drgn1 == 4).astype(float)  # Est
        reg5 = (drgn1 == 5).astype(float)  # Ouest
        reg6 = (drgn1 == 6).astype(float)  # Sud-Ouest
        reg7 = (drgn1 == 7).astype(float)  # Centre-Est
        reg8 = (drgn1 == 8).astype(float)  # Méditerranée
        reg9 = (drgn1 == 9).astype(float)  # Overseas (DOM)
    else:
        # Fall back to pre-computed dummies
        reg2 = _get_col(df, "reg_nuts1_2", 0.0)
        reg3 = _get_col(df, "reg_nuts1_3", 0.0)
        reg4 = _get_col(df, "reg_nuts1_4", 0.0)
        reg5 = _get_col(df, "reg_nuts1_5", 0.0)
        reg6 = _get_col(df, "reg_nuts1_6", 0.0)
        reg7 = _get_col(df, "reg_nuts1_7", 0.0)
        reg8 = _get_col(df, "reg_nuts1_8", 0.0)
        reg9 = _get_col(df, "reg_nuts1_9", 0.0)
    
    yd1 = _get_col(df, "yd1", 0.0)
    yd2 = _get_col(df, "yd2", 0.0)
    
    # Mean log-wage (Mincer equation with all regional effects)
    mean_logw = (
        wopp.beta0
        + wopp.beta_educL * educL
        + wopp.beta_educH * educH
        + wopp.beta_pexp * pexp
        + wopp.beta_pexp2 * (pexp ** 2)
        + wopp.beta_reg2 * reg2  # Bassin Parisien
        + wopp.beta_reg3 * reg3  # Nord-Pas-de-Calais
        + wopp.beta_reg4 * reg4  # Est
        + wopp.beta_reg5 * reg5  # Ouest
        + wopp.beta_reg6 * reg6  # Sud-Ouest
        + wopp.beta_reg7 * reg7  # Centre-Est
        + wopp.beta_reg8 * reg8  # Méditerranée
        + wopp.beta_reg9 * reg9  # Overseas (DOM)
        + wopp.beta_yd1 * yd1
        + wopp.beta_yd2 * yd2
    )
    
    sigma = np.abs(wopp.sigma) + 1e-6
    z = (log_wage - mean_logw) / sigma
    
    # w_opp = -0.5*z² - log(σ) - log(w)
    w_opp = -0.5 * z**2 - np.log(sigma) - log_wage
    w_opp = np.where(working > 0, w_opp, 0.0)
    
    # -------------------------------------------------------------------------
    # Derivatives of w_opp w.r.t. wopp parameters
    # w_opp = -0.5 * ((log_wage - μ)/σ)² - log(σ) - log(w)
    # 
    # For mean parameters (β0, β_educL, etc.): ∂w_opp/∂β_k = z/σ * (∂μ/∂β_k)
    # For σ: ∂w_opp/∂σ = z²/σ - 1/σ = (z² - 1)/σ
    # -------------------------------------------------------------------------
    
    dw_dtheta = np.zeros((n, 16), dtype=float)
    
    # Common factor for mean parameters: z/σ (positive gradient when z > 0)
    z_over_sigma = z / sigma
    
    # [21] beta0: ∂μ/∂β0 = 1
    dw_dtheta[:, 0] = z_over_sigma * 1.0
    # [22] beta_educL: ∂μ/∂β_educL = educL
    dw_dtheta[:, 1] = z_over_sigma * educL
    # [23] beta_educH: ∂μ/∂β_educH = educH
    dw_dtheta[:, 2] = z_over_sigma * educH
    # [24] beta_pexp: ∂μ/∂β_pexp = pexp
    dw_dtheta[:, 3] = z_over_sigma * pexp
    # [25] beta_pexp2: ∂μ/∂β_pexp2 = pexp²
    dw_dtheta[:, 4] = z_over_sigma * (pexp ** 2)
    # [26] beta_reg2: ∂μ/∂β_reg2 = reg2 (Bassin Parisien)
    dw_dtheta[:, 5] = z_over_sigma * reg2
    # [27] beta_reg3: ∂μ/∂β_reg3 = reg3 (Nord-Pas-de-Calais)
    dw_dtheta[:, 6] = z_over_sigma * reg3
    # [28] beta_reg4: ∂μ/∂β_reg4 = reg4 (Est)
    dw_dtheta[:, 7] = z_over_sigma * reg4
    # [29] beta_reg5: ∂μ/∂β_reg5 = reg5 (Ouest)
    dw_dtheta[:, 8] = z_over_sigma * reg5
    # [30] beta_reg6: ∂μ/∂β_reg6 = reg6 (Sud-Ouest)
    dw_dtheta[:, 9] = z_over_sigma * reg6
    # [31] beta_reg7: ∂μ/∂β_reg7 = reg7 (Centre-Est)
    dw_dtheta[:, 10] = z_over_sigma * reg7
    # [32] beta_reg8: ∂μ/∂β_reg8 = reg8 (Méditerranée)
    dw_dtheta[:, 11] = z_over_sigma * reg8
    # [33] beta_reg9: ∂μ/∂β_reg9 = reg9 (Overseas/DOM)
    dw_dtheta[:, 12] = z_over_sigma * reg9
    # [34] beta_yd1: ∂μ/∂β_yd1 = yd1
    dw_dtheta[:, 13] = z_over_sigma * yd1
    # [35] beta_yd2: ∂μ/∂β_yd2 = yd2
    dw_dtheta[:, 14] = z_over_sigma * yd2
    # [36] sigma: ∂w_opp/∂σ = (z² - 1)/σ
    dw_dtheta[:, 15] = (z**2 - 1.0) / sigma
    
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
    
    This is much faster than numerical differentiation.
    
    FULLY VECTORIZED implementation using numpy advanced indexing.
    No Python loops - uses np.bincount and broadcasting for speed.
    """
    n = len(df)
    n_params = 37 if wage_spec == "vw" else 21
    
    # Compute utilities and derivatives
    u, du_dtheta_pref = _compute_utility_derivatives_singles(df, theta, is_male)
    h_opp, dh_dtheta = _compute_hopp_derivatives(df, theta, is_male)
    
    if wage_spec == "vw":
        w_opp, dw_dtheta = _compute_wopp_derivatives(df, theta, is_male)
    else:
        w_opp = np.zeros(n)
        dw_dtheta = np.zeros((n, 16))  # 16 wage params
    
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
    dV_dtheta[:, 0:12] = du_dtheta_pref          # preference params
    dV_dtheta[:, 12:21] = dh_dtheta              # hours opp params
    if wage_spec == "vw":
        dV_dtheta[:, 21:37] = dw_dtheta          # wage opp params (16 total)
    
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
    
    Parameters
    ----------
    theta : np.ndarray
        Parameter vector (37 for vw, 21 for fw)
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
    # Preference params [0:12]
    beta_l0, beta_l_log_age, beta_l_log_age2 = theta[0], theta[1], theta[2]
    beta_l_ch4_6, beta_l_ch7_9 = theta[3], theta[4]
    beta_l_educL, beta_l_educH, beta_l_reg2 = theta[5], theta[6], theta[7]
    beta_c, theta_l, theta_c = theta[8], theta[9], theta[10]
    beta_l_ch0_3 = theta[11]
    
    # Hours opp params [12:21]
    beta_work, beta_pt1, beta_pt2, beta_ft = theta[12], theta[13], theta[14], theta[15]
    beta_gsur = theta[16]
    beta_work_educL, beta_work_educH = theta[17], theta[18]
    beta_work_reg2, beta_work_reg3 = theta[19], theta[20]
    
    # -------------------------------------------------------------------------
    # Utility computation (vectorized)
    # -------------------------------------------------------------------------
    # Box-Cox transforms
    l_bc = _fast_boxcox(data.l, theta_l)
    c_bc = _fast_boxcox(data.c, theta_c)
    
    # Beta_leisure coefficient
    beta_leisure = (
        beta_l0
        + beta_l_log_age * data.log_age
        + beta_l_log_age2 * data.log_age2
        + beta_l_ch4_6 * data.children4_6
        + beta_l_ch7_9 * data.children7_9
        + beta_l_educL * data.educL
        + beta_l_educH * data.educH
        + beta_l_reg2 * data.reg2
    )
    if not is_male:
        beta_leisure = beta_leisure + beta_l_ch0_3 * data.children0_3
    
    u = beta_leisure * l_bc + beta_c * c_bc
    
    # -------------------------------------------------------------------------
    # Hours opportunity density
    # -------------------------------------------------------------------------
    h_opp = (
        beta_work * data.working
        + beta_pt1 * data.working_pt1
        + beta_pt2 * data.working_pt2
        + beta_ft * data.working_ft
        + beta_gsur * data.working * data.gsur
        + beta_work_educL * data.working * data.educL
        + beta_work_educH * data.working * data.educH
        + beta_work_reg2 * data.working * data.reg2
        + beta_work_reg3 * data.working * data.reg3
    )
    
    # -------------------------------------------------------------------------
    # Wage opportunity density (only for vw)
    # -------------------------------------------------------------------------
    if wage_spec == "vw":
        # Wage params [21:37]
        w_beta0 = theta[21]
        w_educL, w_educH = theta[22], theta[23]
        w_pexp, w_pexp2 = theta[24], theta[25]
        w_reg2, w_reg3, w_reg4, w_reg5 = theta[26], theta[27], theta[28], theta[29]
        w_reg6, w_reg7, w_reg8, w_reg9 = theta[30], theta[31], theta[32], theta[33]
        w_yd1, w_yd2 = theta[34], theta[35]
        sigma = abs(theta[36]) + 1e-6
        
        # Mean log-wage (using pre-computed pexp2)
        mean_logw = (
            w_beta0
            + w_educL * data.educL + w_educH * data.educH
            + w_pexp * data.pexp + w_pexp2 * data.pexp2
            + w_reg2 * data.reg2 + w_reg3 * data.reg3
            + w_reg4 * data.reg4 + w_reg5 * data.reg5
            + w_reg6 * data.reg6 + w_reg7 * data.reg7
            + w_reg8 * data.reg8 + w_reg9 * data.reg9
            + w_yd1 * data.yd1 + w_yd2 * data.yd2
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
    
    Couples utility structure:
        U = β_lm(X_m) * BC(l_m; θ_lm) + β_lf(X_f) * BC(l_f; θ_lf) + β_c * BC(c; θ_c)
    
    where β_lm(X_m) and β_lf(X_f) are linear combinations of demographics.
    
    Parameters
    ----------
    theta : np.ndarray
        Parameter vector for couples (see below for layout)
    data : PrecomputedDataCouples  
        Pre-extracted arrays from precompute_data_couples()
    wage_spec : str
        "fw" (fixed wages) or "vw" (variable wages)
    
    Parameter layout (fw = 46 params, vw = 78 params):
    [0:11]   - Male leisure preferences (11 params)
    [11:22]  - Female leisure preferences (11 params)
    [22:25]  - Shared params: theta_lm, theta_lf, theta_c
    [25:26]  - beta_c (consumption)
    [26:35]  - Male hours opportunity (9 params)
    [35:44]  - Female hours opportunity (9 params)
    [44:46]  - Year dummies (if needed)
    [46:62]  - Male wage opportunity (16 params, vw only)
    [62:78]  - Female wage opportunity (16 params, vw only)
    
    Returns
    -------
    float
        Total log-likelihood
    """
    # -------------------------------------------------------------------------
    # Unpack theta - Male leisure preferences [0:11]
    # -------------------------------------------------------------------------
    beta_lm0 = theta[0]
    beta_lm_log_age = theta[1]
    beta_lm_log_age2 = theta[2]
    beta_lm_ch0_3 = theta[3]
    beta_lm_ch4_6 = theta[4]
    beta_lm_ch7_9 = theta[5]
    beta_lm_educL = theta[6]
    beta_lm_educH = theta[7]
    beta_lm_reg2 = theta[8]
    beta_lm_reg3 = theta[9]
    beta_lm_reg4 = theta[10]
    
    # Female leisure preferences [11:22]
    beta_lf0 = theta[11]
    beta_lf_log_age = theta[12]
    beta_lf_log_age2 = theta[13]
    beta_lf_ch0_3 = theta[14]
    beta_lf_ch4_6 = theta[15]
    beta_lf_ch7_9 = theta[16]
    beta_lf_educL = theta[17]
    beta_lf_educH = theta[18]
    beta_lf_reg2 = theta[19]
    beta_lf_reg3 = theta[20]
    beta_lf_reg4 = theta[21]
    
    # Shared Box-Cox and consumption [22:26]
    theta_lm = theta[22]
    theta_lf = theta[23]
    theta_c = theta[24]
    beta_c = theta[25]
    
    # Male hours opportunity [26:35]
    beta_work_m = theta[26]
    beta_pt1_m = theta[27]
    beta_pt2_m = theta[28]
    beta_ft_m = theta[29]
    beta_gsur_m = theta[30]
    beta_work_educL_m = theta[31]
    beta_work_educH_m = theta[32]
    beta_work_reg2_m = theta[33]
    beta_work_reg3_m = theta[34]
    
    # Female hours opportunity [35:44]
    beta_work_f = theta[35]
    beta_pt1_f = theta[36]
    beta_pt2_f = theta[37]
    beta_ft_f = theta[38]
    beta_gsur_f = theta[39]
    beta_work_educL_f = theta[40]
    beta_work_educH_f = theta[41]
    beta_work_reg2_f = theta[42]
    beta_work_reg3_f = theta[43]
    
    # -------------------------------------------------------------------------
    # Utility computation (vectorized)
    # -------------------------------------------------------------------------
    # Box-Cox transforms
    lm_bc = _fast_boxcox(data.l_m, theta_lm)
    lf_bc = _fast_boxcox(data.l_f, theta_lf)
    c_bc = _fast_boxcox(data.c, theta_c)
    
    # Male leisure coefficient
    beta_leisure_m = (
        beta_lm0
        + beta_lm_log_age * data.log_age_m
        + beta_lm_log_age2 * data.log_age2_m
        + beta_lm_ch0_3 * data.children0_3
        + beta_lm_ch4_6 * data.children4_6
        + beta_lm_ch7_9 * data.children7_9
        + beta_lm_educL * data.educL_m
        + beta_lm_educH * data.educH_m
        + beta_lm_reg2 * data.reg2
        + beta_lm_reg3 * data.reg3
        + beta_lm_reg4 * data.reg4
    )
    
    # Female leisure coefficient
    beta_leisure_f = (
        beta_lf0
        + beta_lf_log_age * data.log_age_f
        + beta_lf_log_age2 * data.log_age2_f
        + beta_lf_ch0_3 * data.children0_3
        + beta_lf_ch4_6 * data.children4_6
        + beta_lf_ch7_9 * data.children7_9
        + beta_lf_educL * data.educL_f
        + beta_lf_educH * data.educH_f
        + beta_lf_reg2 * data.reg2
        + beta_lf_reg3 * data.reg3
        + beta_lf_reg4 * data.reg4
    )
    
    # Total utility
    u = beta_leisure_m * lm_bc + beta_leisure_f * lf_bc + beta_c * c_bc
    
    # -------------------------------------------------------------------------
    # Hours opportunity density - male
    # -------------------------------------------------------------------------
    h_opp_m = (
        beta_work_m * data.working_m
        + beta_pt1_m * data.working_pt1_m
        + beta_pt2_m * data.working_pt2_m
        + beta_ft_m * data.working_ft_m
        + beta_gsur_m * data.working_m * data.gsur_m
        + beta_work_educL_m * data.working_m * data.educL_m
        + beta_work_educH_m * data.working_m * data.educH_m
        + beta_work_reg2_m * data.working_m * data.reg2
        + beta_work_reg3_m * data.working_m * data.reg3
    )
    
    # Hours opportunity density - female
    h_opp_f = (
        beta_work_f * data.working_f
        + beta_pt1_f * data.working_pt1_f
        + beta_pt2_f * data.working_pt2_f
        + beta_ft_f * data.working_ft_f
        + beta_gsur_f * data.working_f * data.gsur_f
        + beta_work_educL_f * data.working_f * data.educL_f
        + beta_work_educH_f * data.working_f * data.educH_f
        + beta_work_reg2_f * data.working_f * data.reg2
        + beta_work_reg3_f * data.working_f * data.reg3
    )
    
    h_opp = h_opp_m + h_opp_f
      # -------------------------------------------------------------------------
    # Wage opportunity density (only for vw)
    # -------------------------------------------------------------------------
    if wage_spec == "vw" and len(theta) > 44:
        # Male wage params [44:60]
        w_beta0_m = theta[44]
        w_educL_m, w_educH_m = theta[45], theta[46]
        w_pexp_m, w_pexp2_m = theta[47], theta[48]
        w_reg2_m, w_reg3_m, w_reg4_m, w_reg5_m = theta[49], theta[50], theta[51], theta[52]
        w_reg6_m, w_reg7_m, w_reg8_m, w_reg9_m = theta[53], theta[54], theta[55], theta[56]
        w_yd1_m, w_yd2_m = theta[57], theta[58]
        sigma_m = abs(theta[59]) + 1e-6
        
        mean_logw_m = (
            w_beta0_m
            + w_educL_m * data.educL_m + w_educH_m * data.educH_m
            + w_pexp_m * data.pexp_m + w_pexp2_m * data.pexp2_m
            + w_reg2_m * data.reg2 + w_reg3_m * data.reg3
            + w_reg4_m * data.reg4 + w_reg5_m * data.reg5
            + w_reg6_m * data.reg6 + w_reg7_m * data.reg7
            + w_reg8_m * data.reg8 + w_reg9_m * data.reg9            + w_yd1_m * data.yd1 + w_yd2_m * data.yd2
        )
        z_m = (data.log_wage_m - mean_logw_m) / sigma_m
        w_opp_m = np.where(data.working_m > 0, 
                          -0.5 * z_m * z_m - np.log(sigma_m) - data.log_wage_m, 0.0)
        
        # Female wage params [60:76]
        w_beta0_f = theta[60]
        w_educL_f, w_educH_f = theta[61], theta[62]
        w_pexp_f, w_pexp2_f = theta[63], theta[64]
        w_reg2_f, w_reg3_f, w_reg4_f, w_reg5_f = theta[65], theta[66], theta[67], theta[68]
        w_reg6_f, w_reg7_f, w_reg8_f, w_reg9_f = theta[69], theta[70], theta[71], theta[72]
        w_yd1_f, w_yd2_f = theta[73], theta[74]
        sigma_f = abs(theta[75]) + 1e-6
        
        mean_logw_f = (
            w_beta0_f
            + w_educL_f * data.educL_f + w_educH_f * data.educH_f
            + w_pexp_f * data.pexp_f + w_pexp2_f * data.pexp2_f
            + w_reg2_f * data.reg2 + w_reg3_f * data.reg3
            + w_reg4_f * data.reg4 + w_reg5_f * data.reg5
            + w_reg6_f * data.reg6 + w_reg7_f * data.reg7
            + w_reg8_f * data.reg8 + w_reg9_f * data.reg9
            + w_yd1_f * data.yd1 + w_yd2_f * data.yd2
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
    
    Parameter layout (44 for fw, 76 for vw):
    [0:11]   - Male leisure preferences
    [11:22]  - Female leisure preferences
    [22:25]  - Box-Cox exponents (theta_lm, theta_lf, theta_c)
    [25:26]  - beta_c (consumption)
    [26:35]  - Male hours opportunity (9 params)
    [35:44]  - Female hours opportunity (9 params)
    [44:60]  - Male wage opportunity (16 params, vw only)
    [60:76]  - Female wage opportunity (16 params, vw only)
    """
    theta = []
    
    # Male leisure preferences [0:11]
    theta += [
        1.0,   # beta_lm0
        0.0,   # beta_lm_log_age
        0.0,   # beta_lm_log_age2
        0.0,   # beta_lm_ch0_3 (may be zero for males)
        0.0,   # beta_lm_ch4_6
        0.0,   # beta_lm_ch7_9
        0.0,   # beta_lm_educL
        0.0,   # beta_lm_educH
        0.0,   # beta_lm_reg2
        0.0,   # beta_lm_reg3
        0.0,   # beta_lm_reg4
    ]
    
    # Female leisure preferences [11:22]
    theta += [
        1.0,   # beta_lf0
        0.0,   # beta_lf_log_age
        0.0,   # beta_lf_log_age2
        0.2,   # beta_lf_ch0_3 (positive for females - more leisure when young kids)
        0.1,   # beta_lf_ch4_6
        0.0,   # beta_lf_ch7_9
        0.0,   # beta_lf_educL
        0.0,   # beta_lf_educH
        0.0,   # beta_lf_reg2
        0.0,   # beta_lf_reg3
        0.0,   # beta_lf_reg4
    ]
    
    # Box-Cox exponents and consumption [22:26]
    theta += [
        0.5,   # theta_lm
        0.5,   # theta_lf
        0.5,   # theta_c
        1.0,   # beta_c
    ]
    
    # Male hours opportunity [26:35]
    theta += [
        0.5,   # beta_work_m
        0.0,   # beta_pt1_m
        0.0,   # beta_pt2_m
        0.0,   # beta_ft_m
        0.0,   # beta_gsur_m
        0.0,   # beta_work_educL_m
        0.0,   # beta_work_educH_m
        0.0,   # beta_work_reg2_m
        0.0,   # beta_work_reg3_m
    ]
    
    # Female hours opportunity [35:44]
    theta += [
        0.5,   # beta_work_f
        0.0,   # beta_pt1_f
        0.0,   # beta_pt2_f
        0.0,   # beta_ft_f
        0.0,   # beta_gsur_f
        0.0,   # beta_work_educL_f
        0.0,   # beta_work_educH_f
        0.0,   # beta_work_reg2_f
        0.0,   # beta_work_reg3_f
    ]
    
    if wage_spec == "vw":
        # Male wage opportunity [44:60]
        theta += [
            2.5,    # beta0
            -0.1,   # beta_educL
            0.2,    # beta_educH
            0.02,   # beta_pexp
            -0.001, # beta_pexp2
            -0.05, -0.05, -0.05, -0.05,  # reg2-5
            -0.05, -0.05, -0.05, -0.10,  # reg6-9
            0.0, 0.0,  # yd1, yd2
            0.4,    # sigma
        ]
        
        # Female wage opportunity [60:76]
        theta += [
            2.3,    # beta0 (typically lower)
            -0.1,   # beta_educL
            0.2,    # beta_educH
            0.02,   # beta_pexp
            -0.001, # beta_pexp2
            -0.05, -0.05, -0.05, -0.05,  # reg2-5
            -0.05, -0.05, -0.05, -0.10,  # reg6-9
            0.0, 0.0,  # yd1, yd2
            0.4,    # sigma
        ]
    
    return np.array(theta)


def get_param_names_couples(wage_spec: str = "fw") -> List[str]:
    """Return parameter names for couples, aligned with get_initial_theta_couples order."""
    names = []
    
    # Male leisure [0:11]
    names += [
        "cou.pref.beta_lm0", "cou.pref.beta_lm_log_age", "cou.pref.beta_lm_log_age2",
        "cou.pref.beta_lm_ch0_3", "cou.pref.beta_lm_ch4_6", "cou.pref.beta_lm_ch7_9",
        "cou.pref.beta_lm_educL", "cou.pref.beta_lm_educH",
        "cou.pref.beta_lm_reg2", "cou.pref.beta_lm_reg3", "cou.pref.beta_lm_reg4",
    ]
    
    # Female leisure [11:22]
    names += [
        "cou.pref.beta_lf0", "cou.pref.beta_lf_log_age", "cou.pref.beta_lf_log_age2",
        "cou.pref.beta_lf_ch0_3", "cou.pref.beta_lf_ch4_6", "cou.pref.beta_lf_ch7_9",
        "cou.pref.beta_lf_educL", "cou.pref.beta_lf_educH",
        "cou.pref.beta_lf_reg2", "cou.pref.beta_lf_reg3", "cou.pref.beta_lf_reg4",
    ]
    
    # Box-Cox and consumption [22:26]
    names += ["cou.pref.theta_lm", "cou.pref.theta_lf", "cou.pref.theta_c", "cou.pref.beta_c"]
    
    # Male hours opportunity [26:35]
    names += [
        "cou.hopp_m.beta_work", "cou.hopp_m.beta_pt1", "cou.hopp_m.beta_pt2",
        "cou.hopp_m.beta_ft", "cou.hopp_m.beta_gsur",
        "cou.hopp_m.beta_work_educL", "cou.hopp_m.beta_work_educH",
        "cou.hopp_m.beta_work_reg2", "cou.hopp_m.beta_work_reg3",
    ]
    
    # Female hours opportunity [35:44]
    names += [
        "cou.hopp_f.beta_work", "cou.hopp_f.beta_pt1", "cou.hopp_f.beta_pt2",
        "cou.hopp_f.beta_ft", "cou.hopp_f.beta_gsur",
        "cou.hopp_f.beta_work_educL", "cou.hopp_f.beta_work_educH",
        "cou.hopp_f.beta_work_reg2", "cou.hopp_f.beta_work_reg3",
    ]
    
    if wage_spec == "vw":
        # Male wage opportunity [44:60]
        names += [
            "cou.wopp_m.beta0", "cou.wopp_m.beta_educL", "cou.wopp_m.beta_educH",
            "cou.wopp_m.beta_pexp", "cou.wopp_m.beta_pexp2",
            "cou.wopp_m.beta_reg2", "cou.wopp_m.beta_reg3", "cou.wopp_m.beta_reg4", "cou.wopp_m.beta_reg5",
            "cou.wopp_m.beta_reg6", "cou.wopp_m.beta_reg7", "cou.wopp_m.beta_reg8", "cou.wopp_m.beta_reg9",
            "cou.wopp_m.beta_yd1", "cou.wopp_m.beta_yd2", "cou.wopp_m.sigma",
        ]
        
        # Female wage opportunity [60:76]
        names += [
            "cou.wopp_f.beta0", "cou.wopp_f.beta_educL", "cou.wopp_f.beta_educH",
            "cou.wopp_f.beta_pexp", "cou.wopp_f.beta_pexp2",
            "cou.wopp_f.beta_reg2", "cou.wopp_f.beta_reg3", "cou.wopp_f.beta_reg4", "cou.wopp_f.beta_reg5",
            "cou.wopp_f.beta_reg6", "cou.wopp_f.beta_reg7", "cou.wopp_f.beta_reg8", "cou.wopp_f.beta_reg9",
            "cou.wopp_f.beta_yd1", "cou.wopp_f.beta_yd2", "cou.wopp_f.sigma",
        ]
    
    return names


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
    
    Parameters
    ----------
    theta : np.ndarray
        Parameter vector
    data : PrecomputedDataSingles
        Pre-extracted arrays
    is_male : bool
        True for single males
    wage_spec : str
        "fw" or "vw"
    
    Returns
    -------
    np.ndarray
        Gradient of log-likelihood w.r.t. theta
    """
    n = len(data.c)
    n_params = 37 if wage_spec == "vw" else 21
    
    # Unpack theta
    beta_l0, beta_l_log_age, beta_l_log_age2 = theta[0], theta[1], theta[2]
    beta_l_ch4_6, beta_l_ch7_9 = theta[3], theta[4]
    beta_l_educL, beta_l_educH, beta_l_reg2 = theta[5], theta[6], theta[7]
    beta_c, theta_l, theta_c = theta[8], theta[9], theta[10]
    beta_l_ch0_3 = theta[11]
    
    beta_work, beta_pt1, beta_pt2, beta_ft = theta[12], theta[13], theta[14], theta[15]
    beta_gsur = theta[16]
    beta_work_educL, beta_work_educH = theta[17], theta[18]
    beta_work_reg2, beta_work_reg3 = theta[19], theta[20]
    
    # -------------------------------------------------------------------------
    # Utility and its derivatives
    # -------------------------------------------------------------------------
    l_bc = _fast_boxcox(data.l, theta_l)
    c_bc = _fast_boxcox(data.c, theta_c)
    dl_bc_dtheta_l = _fast_d_boxcox_dtheta(data.l, theta_l)
    dc_bc_dtheta_c = _fast_d_boxcox_dtheta(data.c, theta_c)
    
    beta_leisure = (
        beta_l0
        + beta_l_log_age * data.log_age
        + beta_l_log_age2 * data.log_age2
        + beta_l_ch4_6 * data.children4_6
        + beta_l_ch7_9 * data.children7_9
        + beta_l_educL * data.educL
        + beta_l_educH * data.educH
        + beta_l_reg2 * data.reg2
    )
    if not is_male:
        beta_leisure = beta_leisure + beta_l_ch0_3 * data.children0_3
    
    u = beta_leisure * l_bc + beta_c * c_bc
    
    # Preference derivatives (12 params)
    du_dtheta = np.zeros((n, 12), dtype=np.float64)
    du_dtheta[:, 0] = l_bc                           # beta_l0
    du_dtheta[:, 1] = data.log_age * l_bc            # beta_l_log_age
    du_dtheta[:, 2] = data.log_age2 * l_bc           # beta_l_log_age2
    du_dtheta[:, 3] = data.children4_6 * l_bc        # beta_l_ch4_6
    du_dtheta[:, 4] = data.children7_9 * l_bc        # beta_l_ch7_9
    du_dtheta[:, 5] = data.educL * l_bc              # beta_l_educL
    du_dtheta[:, 6] = data.educH * l_bc              # beta_l_educH
    du_dtheta[:, 7] = data.reg2 * l_bc               # beta_l_reg2
    du_dtheta[:, 8] = c_bc                           # beta_c
    du_dtheta[:, 9] = beta_leisure * dl_bc_dtheta_l  # theta_l
    du_dtheta[:, 10] = beta_c * dc_bc_dtheta_c       # theta_c
    if not is_male:
        du_dtheta[:, 11] = data.children0_3 * l_bc   # beta_l_ch0_3
    
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
        + beta_work_reg2 * data.working * data.reg2
        + beta_work_reg3 * data.working * data.reg3
    )
    
    # Hours opp derivatives (9 params)
    dh_dtheta = np.zeros((n, 9), dtype=np.float64)
    dh_dtheta[:, 0] = data.working
    dh_dtheta[:, 1] = data.working_pt1
    dh_dtheta[:, 2] = data.working_pt2
    dh_dtheta[:, 3] = data.working_ft
    dh_dtheta[:, 4] = data.working * data.gsur
    dh_dtheta[:, 5] = data.working * data.educL
    dh_dtheta[:, 6] = data.working * data.educH
    dh_dtheta[:, 7] = data.working * data.reg2
    dh_dtheta[:, 8] = data.working * data.reg3
    
    # -------------------------------------------------------------------------
    # Wage opportunity and its derivatives (if vw)
    # -------------------------------------------------------------------------
    if wage_spec == "vw":
        w_beta0 = theta[21]
        w_educL, w_educH = theta[22], theta[23]
        w_pexp, w_pexp2 = theta[24], theta[25]
        w_reg2, w_reg3, w_reg4, w_reg5 = theta[26], theta[27], theta[28], theta[29]
        w_reg6, w_reg7, w_reg8, w_reg9 = theta[30], theta[31], theta[32], theta[33]
        w_yd1, w_yd2 = theta[34], theta[35]
        sigma = abs(theta[36]) + 1e-6
        
        mean_logw = (
            w_beta0
            + w_educL * data.educL + w_educH * data.educH
            + w_pexp * data.pexp + w_pexp2 * data.pexp2
            + w_reg2 * data.reg2 + w_reg3 * data.reg3
            + w_reg4 * data.reg4 + w_reg5 * data.reg5
            + w_reg6 * data.reg6 + w_reg7 * data.reg7
            + w_reg8 * data.reg8 + w_reg9 * data.reg9
            + w_yd1 * data.yd1 + w_yd2 * data.yd2
        )
        
        z = (data.log_wage - mean_logw) / sigma
        w_opp = np.where(data.working > 0, -0.5 * z * z - np.log(sigma) - data.log_wage, 0.0)
        
        z_over_sigma = z / sigma
        dw_dtheta = np.zeros((n, 16), dtype=np.float64)
        dw_dtheta[:, 0] = z_over_sigma
        dw_dtheta[:, 1] = z_over_sigma * data.educL
        dw_dtheta[:, 2] = z_over_sigma * data.educH
        dw_dtheta[:, 3] = z_over_sigma * data.pexp
        dw_dtheta[:, 4] = z_over_sigma * data.pexp2
        dw_dtheta[:, 5] = z_over_sigma * data.reg2
        dw_dtheta[:, 6] = z_over_sigma * data.reg3
        dw_dtheta[:, 7] = z_over_sigma * data.reg4
        dw_dtheta[:, 8] = z_over_sigma * data.reg5
        dw_dtheta[:, 9] = z_over_sigma * data.reg6
        dw_dtheta[:, 10] = z_over_sigma * data.reg7
        dw_dtheta[:, 11] = z_over_sigma * data.reg8
        dw_dtheta[:, 12] = z_over_sigma * data.reg9
        dw_dtheta[:, 13] = z_over_sigma * data.yd1
        dw_dtheta[:, 14] = z_over_sigma * data.yd2
        dw_dtheta[:, 15] = (z * z - 1.0) / sigma
        dw_dtheta = np.where(data.working[:, None] > 0, dw_dtheta, 0.0)
    else:
        w_opp = 0.0
        dw_dtheta = np.zeros((n, 16), dtype=np.float64)
    
    # -------------------------------------------------------------------------
    # Composite V and dV/dtheta
    # -------------------------------------------------------------------------
    V = u + h_opp + w_opp - data.log_prior
    
    dV_dtheta = np.zeros((n, n_params), dtype=np.float64)
    dV_dtheta[:, 0:12] = du_dtheta
    dV_dtheta[:, 12:21] = dh_dtheta
    if wage_spec == "vw":
        dV_dtheta[:, 21:37] = dw_dtheta
    
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
    
    This is ~30-50% faster than calling LL and grad separately because:
    1. Box-Cox transforms computed once (not twice)
    2. V and softmax probabilities computed once (not twice)
    3. Better cache locality
    
    Use this with L-BFGS-B for maximum speed.
    """
    n = len(data.c)
    n_params = 37 if wage_spec == "vw" else 21
    
    # Unpack theta
    beta_l0, beta_l_log_age, beta_l_log_age2 = theta[0], theta[1], theta[2]
    beta_l_ch4_6, beta_l_ch7_9 = theta[3], theta[4]
    beta_l_educL, beta_l_educH, beta_l_reg2 = theta[5], theta[6], theta[7]
    beta_c, theta_l, theta_c = theta[8], theta[9], theta[10]
    beta_l_ch0_3 = theta[11]
    
    beta_work, beta_pt1, beta_pt2, beta_ft = theta[12], theta[13], theta[14], theta[15]
    beta_gsur = theta[16]
    beta_work_educL, beta_work_educH = theta[17], theta[18]
    beta_work_reg2, beta_work_reg3 = theta[19], theta[20]
    
    # Box-Cox transforms (computed ONCE)
    l_bc = _fast_boxcox(data.l, theta_l)
    c_bc = _fast_boxcox(data.c, theta_c)
    dl_bc_dtheta_l = _fast_d_boxcox_dtheta(data.l, theta_l)
    dc_bc_dtheta_c = _fast_d_boxcox_dtheta(data.c, theta_c)
    
    # Utility
    beta_leisure = (beta_l0 + beta_l_log_age * data.log_age + beta_l_log_age2 * data.log_age2
        + beta_l_ch4_6 * data.children4_6 + beta_l_ch7_9 * data.children7_9
        + beta_l_educL * data.educL + beta_l_educH * data.educH + beta_l_reg2 * data.reg2)
    if not is_male:
        beta_leisure = beta_leisure + beta_l_ch0_3 * data.children0_3
    
    u = beta_leisure * l_bc + beta_c * c_bc
    
    # Hours opportunity
    h_opp = (beta_work * data.working + beta_pt1 * data.working_pt1
        + beta_pt2 * data.working_pt2 + beta_ft * data.working_ft
        + beta_gsur * data.working * data.gsur
        + beta_work_educL * data.working * data.educL + beta_work_educH * data.working * data.educH
        + beta_work_reg2 * data.working * data.reg2 + beta_work_reg3 * data.working * data.reg3)
    
    # Wage opportunity (vw only)
    if wage_spec == "vw":
        sigma = abs(theta[36]) + 1e-6
        mean_logw = (theta[21] + theta[22] * data.educL + theta[23] * data.educH
            + theta[24] * data.pexp + theta[25] * data.pexp2
            + theta[26] * data.reg2 + theta[27] * data.reg3 + theta[28] * data.reg4 + theta[29] * data.reg5
            + theta[30] * data.reg6 + theta[31] * data.reg7 + theta[32] * data.reg8 + theta[33] * data.reg9
            + theta[34] * data.yd1 + theta[35] * data.yd2)
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
    
    # Preference derivatives [0:12]
    dV[:, 0] = l_bc
    dV[:, 1] = data.log_age * l_bc
    dV[:, 2] = data.log_age2 * l_bc
    dV[:, 3] = data.children4_6 * l_bc
    dV[:, 4] = data.children7_9 * l_bc
    dV[:, 5] = data.educL * l_bc
    dV[:, 6] = data.educH * l_bc
    dV[:, 7] = data.reg2 * l_bc
    dV[:, 8] = c_bc
    dV[:, 9] = beta_leisure * dl_bc_dtheta_l
    dV[:, 10] = beta_c * dc_bc_dtheta_c
    dV[:, 11] = data.children0_3 * l_bc if not is_male else 0.0
    
    # Hours opp derivatives [12:21]
    dV[:, 12] = data.working
    dV[:, 13] = data.working_pt1
    dV[:, 14] = data.working_pt2
    dV[:, 15] = data.working_ft
    dV[:, 16] = data.working * data.gsur
    dV[:, 17] = data.working * data.educL
    dV[:, 18] = data.working * data.educH
    dV[:, 19] = data.working * data.reg2
    dV[:, 20] = data.working * data.reg3
    
    # Wage derivatives (vw only)
    if wage_spec == "vw" and z is not None:
        z_s = z / sigma
        dV[:, 21] = np.where(data.working > 0, z_s, 0.0)
        dV[:, 22] = np.where(data.working > 0, z_s * data.educL, 0.0)
        dV[:, 23] = np.where(data.working > 0, z_s * data.educH, 0.0)
        dV[:, 24] = np.where(data.working > 0, z_s * data.pexp, 0.0)
        dV[:, 25] = np.where(data.working > 0, z_s * data.pexp2, 0.0)
        for i, r in enumerate([data.reg2, data.reg3, data.reg4, data.reg5, data.reg6, data.reg7, data.reg8, data.reg9]):
            dV[:, 26+i] = np.where(data.working > 0, z_s * r, 0.0)
        dV[:, 34] = np.where(data.working > 0, z_s * data.yd1, 0.0)
        dV[:, 35] = np.where(data.working > 0, z_s * data.yd2, 0.0)
        dV[:, 36] = np.where(data.working > 0, (z*z - 1.0)/sigma, 0.0)
    
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
    
    This is ~30-50% faster than calling LL and grad separately because:
    1. Box-Cox transforms computed once (not twice)
    2. V and softmax probabilities computed once (not twice)
    3. Better cache locality
    
    Use this with L-BFGS-B for maximum speed.
    
    Parameters
    ----------
    theta : np.ndarray
        Parameter vector (44 for fw, 76 for vw)
    data : PrecomputedDataCouples
        Pre-extracted arrays from precompute_data_couples()
    wage_spec : str
        "fw" (fixed wages) or "vw" (variable wages)
    
    Returns
    -------
    Tuple[float, np.ndarray]
        (-LL, -gradient) for minimization
    """
    n = len(data.c)
    n_params = 76 if wage_spec == "vw" else 44
    
    # -------------------------------------------------------------------------
    # Unpack theta once
    # -------------------------------------------------------------------------
    # Male leisure preferences [0:11]
    beta_lm0 = theta[0]
    beta_lm_log_age = theta[1]
    beta_lm_log_age2 = theta[2]
    beta_lm_ch0_3 = theta[3]
    beta_lm_ch4_6 = theta[4]
    beta_lm_ch7_9 = theta[5]
    beta_lm_educL = theta[6]
    beta_lm_educH = theta[7]
    beta_lm_reg2 = theta[8]
    beta_lm_reg3 = theta[9]
    beta_lm_reg4 = theta[10]
    
    # Female leisure preferences [11:22]
    beta_lf0 = theta[11]
    beta_lf_log_age = theta[12]
    beta_lf_log_age2 = theta[13]
    beta_lf_ch0_3 = theta[14]
    beta_lf_ch4_6 = theta[15]
    beta_lf_ch7_9 = theta[16]
    beta_lf_educL = theta[17]
    beta_lf_educH = theta[18]
    beta_lf_reg2 = theta[19]
    beta_lf_reg3 = theta[20]
    beta_lf_reg4 = theta[21]
    
    # Shared Box-Cox and consumption [22:26]
    theta_lm = theta[22]
    theta_lf = theta[23]
    theta_c = theta[24]
    beta_c = theta[25]
    
    # Male hours opportunity [26:35]
    beta_work_m = theta[26]
    beta_pt1_m = theta[27]
    beta_pt2_m = theta[28]
    beta_ft_m = theta[29]
    beta_gsur_m = theta[30]
    beta_work_educL_m = theta[31]
    beta_work_educH_m = theta[32]
    beta_work_reg2_m = theta[33]
    beta_work_reg3_m = theta[34]
    
    # Female hours opportunity [35:44]
    beta_work_f = theta[35]
    beta_pt1_f = theta[36]
    beta_pt2_f = theta[37]
    beta_ft_f = theta[38]
    beta_gsur_f = theta[39]
    beta_work_educL_f = theta[40]
    beta_work_educH_f = theta[41]
    beta_work_reg2_f = theta[42]
    beta_work_reg3_f = theta[43]
    
    # -------------------------------------------------------------------------
    # Box-Cox transforms (computed ONCE, used for both LL and gradient)
    # -------------------------------------------------------------------------
    lm_bc = _fast_boxcox(data.l_m, theta_lm)
    lf_bc = _fast_boxcox(data.l_f, theta_lf)
    c_bc = _fast_boxcox(data.c, theta_c)
    dlm_bc_dtheta = _fast_d_boxcox_dtheta(data.l_m, theta_lm)
    dlf_bc_dtheta = _fast_d_boxcox_dtheta(data.l_f, theta_lf)
    dc_bc_dtheta = _fast_d_boxcox_dtheta(data.c, theta_c)
    
    # -------------------------------------------------------------------------
    # Utility computation
    # -------------------------------------------------------------------------
    # Male leisure coefficient
    beta_leisure_m = (
        beta_lm0
        + beta_lm_log_age * data.log_age_m
        + beta_lm_log_age2 * data.log_age2_m
        + beta_lm_ch0_3 * data.children0_3
        + beta_lm_ch4_6 * data.children4_6
        + beta_lm_ch7_9 * data.children7_9
        + beta_lm_educL * data.educL_m
        + beta_lm_educH * data.educH_m
        + beta_lm_reg2 * data.reg2
        + beta_lm_reg3 * data.reg3
        + beta_lm_reg4 * data.reg4
    )
    
    # Female leisure coefficient
    beta_leisure_f = (
        beta_lf0
        + beta_lf_log_age * data.log_age_f
        + beta_lf_log_age2 * data.log_age2_f
        + beta_lf_ch0_3 * data.children0_3
        + beta_lf_ch4_6 * data.children4_6
        + beta_lf_ch7_9 * data.children7_9
        + beta_lf_educL * data.educL_f
        + beta_lf_educH * data.educH_f
        + beta_lf_reg2 * data.reg2
        + beta_lf_reg3 * data.reg3
        + beta_lf_reg4 * data.reg4
    )
    
    # Total utility
    u = beta_leisure_m * lm_bc + beta_leisure_f * lf_bc + beta_c * c_bc
    
    # -------------------------------------------------------------------------
    # Utility derivatives (26 params: male leisure 11 + female leisure 11 + shared 4)
    # -------------------------------------------------------------------------
    du_dtheta = np.empty((n, 26), dtype=np.float64)
    
    # Male leisure params [0:11]
    du_dtheta[:, 0] = lm_bc                                  # beta_lm0
    du_dtheta[:, 1] = data.log_age_m * lm_bc                 # beta_lm_log_age
    du_dtheta[:, 2] = data.log_age2_m * lm_bc                # beta_lm_log_age2
    du_dtheta[:, 3] = data.children0_3 * lm_bc               # beta_lm_ch0_3
    du_dtheta[:, 4] = data.children4_6 * lm_bc               # beta_lm_ch4_6
    du_dtheta[:, 5] = data.children7_9 * lm_bc               # beta_lm_ch7_9
    du_dtheta[:, 6] = data.educL_m * lm_bc                   # beta_lm_educL
    du_dtheta[:, 7] = data.educH_m * lm_bc                   # beta_lm_educH
    du_dtheta[:, 8] = data.reg2 * lm_bc                      # beta_lm_reg2
    du_dtheta[:, 9] = data.reg3 * lm_bc                      # beta_lm_reg3
    du_dtheta[:, 10] = data.reg4 * lm_bc                     # beta_lm_reg4
    
    # Female leisure params [11:22]
    du_dtheta[:, 11] = lf_bc                                 # beta_lf0
    du_dtheta[:, 12] = data.log_age_f * lf_bc                # beta_lf_log_age
    du_dtheta[:, 13] = data.log_age2_f * lf_bc               # beta_lf_log_age2
    du_dtheta[:, 14] = data.children0_3 * lf_bc              # beta_lf_ch0_3
    du_dtheta[:, 15] = data.children4_6 * lf_bc              # beta_lf_ch4_6
    du_dtheta[:, 16] = data.children7_9 * lf_bc              # beta_lf_ch7_9
    du_dtheta[:, 17] = data.educL_f * lf_bc                  # beta_lf_educL
    du_dtheta[:, 18] = data.educH_f * lf_bc                  # beta_lf_educH
    du_dtheta[:, 19] = data.reg2 * lf_bc                     # beta_lf_reg2
    du_dtheta[:, 20] = data.reg3 * lf_bc                     # beta_lf_reg3
    du_dtheta[:, 21] = data.reg4 * lf_bc                     # beta_lf_reg4
    
    # Box-Cox and consumption [22:26]
    du_dtheta[:, 22] = beta_leisure_m * dlm_bc_dtheta        # theta_lm
    du_dtheta[:, 23] = beta_leisure_f * dlf_bc_dtheta        # theta_lf
    du_dtheta[:, 24] = beta_c * dc_bc_dtheta                 # theta_c
    du_dtheta[:, 25] = c_bc                                  # beta_c
    
    # -------------------------------------------------------------------------
    # Hours opportunity density - male
    # -------------------------------------------------------------------------
    h_opp_m = (
        beta_work_m * data.working_m
        + beta_pt1_m * data.working_pt1_m
        + beta_pt2_m * data.working_pt2_m
        + beta_ft_m * data.working_ft_m
        + beta_gsur_m * data.working_m * data.gsur_m
        + beta_work_educL_m * data.working_m * data.educL_m
        + beta_work_educH_m * data.working_m * data.educH_m
        + beta_work_reg2_m * data.working_m * data.reg2
        + beta_work_reg3_m * data.working_m * data.reg3
    )
    
    # Hours opportunity density - female
    h_opp_f = (
        beta_work_f * data.working_f
        + beta_pt1_f * data.working_pt1_f
        + beta_pt2_f * data.working_pt2_f
        + beta_ft_f * data.working_ft_f
        + beta_gsur_f * data.working_f * data.gsur_f
        + beta_work_educL_f * data.working_f * data.educL_f
        + beta_work_educH_f * data.working_f * data.educH_f
        + beta_work_reg2_f * data.working_f * data.reg2
        + beta_work_reg3_f * data.working_f * data.reg3
    )
    
    h_opp = h_opp_m + h_opp_f
    
    # Hours opp derivatives (18 params: 9 male + 9 female)
    dh_dtheta = np.empty((n, 18), dtype=np.float64)
    # Male hopp [0:9]
    dh_dtheta[:, 0] = data.working_m
    dh_dtheta[:, 1] = data.working_pt1_m
    dh_dtheta[:, 2] = data.working_pt2_m
    dh_dtheta[:, 3] = data.working_ft_m
    dh_dtheta[:, 4] = data.working_m * data.gsur_m
    dh_dtheta[:, 5] = data.working_m * data.educL_m
    dh_dtheta[:, 6] = data.working_m * data.educH_m
    dh_dtheta[:, 7] = data.working_m * data.reg2
    dh_dtheta[:, 8] = data.working_m * data.reg3
    # Female hopp [9:18]
    dh_dtheta[:, 9] = data.working_f
    dh_dtheta[:, 10] = data.working_pt1_f
    dh_dtheta[:, 11] = data.working_pt2_f
    dh_dtheta[:, 12] = data.working_ft_f
    dh_dtheta[:, 13] = data.working_f * data.gsur_f
    dh_dtheta[:, 14] = data.working_f * data.educL_f
    dh_dtheta[:, 15] = data.working_f * data.educH_f
    dh_dtheta[:, 16] = data.working_f * data.reg2
    dh_dtheta[:, 17] = data.working_f * data.reg3
    
    # -------------------------------------------------------------------------
    # Wage opportunity density (only for vw)
    # -------------------------------------------------------------------------
    if wage_spec == "vw" and len(theta) > 44:
        # Male wage params [44:60]
        w_beta0_m = theta[44]
        w_educL_m, w_educH_m = theta[45], theta[46]
        w_pexp_m, w_pexp2_m = theta[47], theta[48]
        w_reg2_m, w_reg3_m, w_reg4_m, w_reg5_m = theta[49], theta[50], theta[51], theta[52]
        w_reg6_m, w_reg7_m, w_reg8_m, w_reg9_m = theta[53], theta[54], theta[55], theta[56]
        w_yd1_m, w_yd2_m = theta[57], theta[58]
        sigma_m = abs(theta[59]) + 1e-6
        
        mean_logw_m = (
            w_beta0_m
            + w_educL_m * data.educL_m + w_educH_m * data.educH_m
            + w_pexp_m * data.pexp_m + w_pexp2_m * data.pexp2_m
            + w_reg2_m * data.reg2 + w_reg3_m * data.reg3
            + w_reg4_m * data.reg4 + w_reg5_m * data.reg5
            + w_reg6_m * data.reg6 + w_reg7_m * data.reg7
            + w_reg8_m * data.reg8 + w_reg9_m * data.reg9
            + w_yd1_m * data.yd1 + w_yd2_m * data.yd2
        )
        z_m = (data.log_wage_m - mean_logw_m) / sigma_m
        w_opp_m = np.where(data.working_m > 0, 
                          -0.5 * z_m * z_m - np.log(sigma_m) - data.log_wage_m, 0.0)
        
        # Female wage params [60:76]
        w_beta0_f = theta[60]
        w_educL_f, w_educH_f = theta[61], theta[62]
        w_pexp_f, w_pexp2_f = theta[63], theta[64]
        w_reg2_f, w_reg3_f, w_reg4_f, w_reg5_f = theta[65], theta[66], theta[67], theta[68]
        w_reg6_f, w_reg7_f, w_reg8_f, w_reg9_f = theta[69], theta[70], theta[71], theta[72]
        w_yd1_f, w_yd2_f = theta[73], theta[74]
        sigma_f = abs(theta[75]) + 1e-6
        
        mean_logw_f = (
            w_beta0_f
            + w_educL_f * data.educL_f + w_educH_f * data.educH_f
            + w_pexp_f * data.pexp_f + w_pexp2_f * data.pexp2_f
            + w_reg2_f * data.reg2 + w_reg3_f * data.reg3
            + w_reg4_f * data.reg4 + w_reg5_f * data.reg5
            + w_reg6_f * data.reg6 + w_reg7_f * data.reg7
            + w_reg8_f * data.reg8 + w_reg9_f * data.reg9
            + w_yd1_f * data.yd1 + w_yd2_f * data.yd2
        )
        z_f = (data.log_wage_f - mean_logw_f) / sigma_f
        w_opp_f = np.where(data.working_f > 0,
                          -0.5 * z_f * z_f - np.log(sigma_f) - data.log_wage_f, 0.0)
        
        w_opp = w_opp_m + w_opp_f
          # Wage derivatives (32 params: 16 male + 16 female)
        z_over_sigma_m = z_m / sigma_m
        z_over_sigma_f = z_f / sigma_f
        
        dw_dtheta = np.empty((n, 32), dtype=np.float64)
        # Male wopp [0:16]
        dw_dtheta[:, 0] = np.where(data.working_m > 0, z_over_sigma_m, 0.0)
        dw_dtheta[:, 1] = np.where(data.working_m > 0, z_over_sigma_m * data.educL_m, 0.0)
        dw_dtheta[:, 2] = np.where(data.working_m > 0, z_over_sigma_m * data.educH_m, 0.0)
        dw_dtheta[:, 3] = np.where(data.working_m > 0, z_over_sigma_m * data.pexp_m, 0.0)
        dw_dtheta[:, 4] = np.where(data.working_m > 0, z_over_sigma_m * data.pexp2_m, 0.0)
        dw_dtheta[:, 5] = np.where(data.working_m > 0, z_over_sigma_m * data.reg2, 0.0)
        dw_dtheta[:, 6] = np.where(data.working_m > 0, z_over_sigma_m * data.reg3, 0.0)
        dw_dtheta[:, 7] = np.where(data.working_m > 0, z_over_sigma_m * data.reg4, 0.0)
        dw_dtheta[:, 8] = np.where(data.working_m > 0, z_over_sigma_m * data.reg5, 0.0)
        dw_dtheta[:, 9] = np.where(data.working_m > 0, z_over_sigma_m * data.reg6, 0.0)
        dw_dtheta[:, 10] = np.where(data.working_m > 0, z_over_sigma_m * data.reg7, 0.0)
        dw_dtheta[:, 11] = np.where(data.working_m > 0, z_over_sigma_m * data.reg8, 0.0)
        dw_dtheta[:, 12] = np.where(data.working_m > 0, z_over_sigma_m * data.reg9, 0.0)
        dw_dtheta[:, 13] = np.where(data.working_m > 0, z_over_sigma_m * data.yd1, 0.0)
        dw_dtheta[:, 14] = np.where(data.working_m > 0, z_over_sigma_m * data.yd2, 0.0)
        dw_dtheta[:, 15] = np.where(data.working_m > 0, (z_m * z_m - 1.0) / sigma_m, 0.0)
        
        # Female wopp [16:32]
        dw_dtheta[:, 16] = np.where(data.working_f > 0, z_over_sigma_f, 0.0)
        dw_dtheta[:, 17] = np.where(data.working_f > 0, z_over_sigma_f * data.educL_f, 0.0)
        dw_dtheta[:, 18] = np.where(data.working_f > 0, z_over_sigma_f * data.educH_f, 0.0)
        dw_dtheta[:, 19] = np.where(data.working_f > 0, z_over_sigma_f * data.pexp_f, 0.0)
        dw_dtheta[:, 20] = np.where(data.working_f > 0, z_over_sigma_f * data.pexp2_f, 0.0)
        dw_dtheta[:, 21] = np.where(data.working_f > 0, z_over_sigma_f * data.reg2, 0.0)
        dw_dtheta[:, 22] = np.where(data.working_f > 0, z_over_sigma_f * data.reg3, 0.0)
        dw_dtheta[:, 23] = np.where(data.working_f > 0, z_over_sigma_f * data.reg4, 0.0)
        dw_dtheta[:, 24] = np.where(data.working_f > 0, z_over_sigma_f * data.reg5, 0.0)
        dw_dtheta[:, 25] = np.where(data.working_f > 0, z_over_sigma_f * data.reg6, 0.0)
        dw_dtheta[:, 26] = np.where(data.working_f > 0, z_over_sigma_f * data.reg7, 0.0)
        dw_dtheta[:, 27] = np.where(data.working_f > 0, z_over_sigma_f * data.reg8, 0.0)
        dw_dtheta[:, 28] = np.where(data.working_f > 0, z_over_sigma_f * data.reg9, 0.0)
        dw_dtheta[:, 29] = np.where(data.working_f > 0, z_over_sigma_f * data.yd1, 0.0)
        dw_dtheta[:, 30] = np.where(data.working_f > 0, z_over_sigma_f * data.yd2, 0.0)
        dw_dtheta[:, 31] = np.where(data.working_f > 0, (z_f * z_f - 1.0) / sigma_f, 0.0)
    else:
        w_opp = 0.0
        dw_dtheta = None
        z_m = z_f = sigma_m = sigma_f = None
    
    # -------------------------------------------------------------------------
    # Composite V and dV/dtheta
    # -------------------------------------------------------------------------
    V = u + h_opp + w_opp - data.log_prior
    
    dV_dtheta = np.empty((n, n_params), dtype=np.float64)
    dV_dtheta[:, 0:26] = du_dtheta
    dV_dtheta[:, 26:44] = dh_dtheta
    if wage_spec == "vw" and dw_dtheta is not None:
        dV_dtheta[:, 44:76] = dw_dtheta
    
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
    
    # Bincount for E[dV] - this loop is the remaining bottleneck
    E_dV_per_group = np.zeros((data.n_groups, n_params), dtype=np.float64)
    for k in range(n_params):
        E_dV_per_group[:, k] = np.bincount(data.group_idx, weights=P_weighted_dV[:, k], minlength=data.n_groups)
    E_dV = E_dV_per_group[data.group_idx, :]
    
    grad = (dV_dtheta[data.is_obs, :] - E_dV[data.is_obs, :]).sum(axis=0)
    
    return -ll, -grad


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
    """
    if not NUMBA_AVAILABLE or _compute_softmax_gradient_numba is None:
        return fast_analytical_gradient_singles(theta, data, is_male, wage_spec)
    
    n = len(data.c)
    n_params = 37 if wage_spec == "vw" else 21
    
    # Unpack theta (same as fast_analytical_gradient_singles)
    beta_l0, beta_l_log_age, beta_l_log_age2 = theta[0], theta[1], theta[2]
    beta_l_ch4_6, beta_l_ch7_9 = theta[3], theta[4]
    beta_l_educL, beta_l_educH, beta_l_reg2 = theta[5], theta[6], theta[7]
    beta_c, theta_l, theta_c = theta[8], theta[9], theta[10]
    beta_l_ch0_3 = theta[11]
    
    beta_work, beta_pt1, beta_pt2, beta_ft = theta[12], theta[13], theta[14], theta[15]
    beta_gsur = theta[16]
    beta_work_educL, beta_work_educH = theta[17], theta[18]
    beta_work_reg2, beta_work_reg3 = theta[19], theta[20]
    
    # Box-Cox transforms
    l_bc = _fast_boxcox(data.l, theta_l)
    c_bc = _fast_boxcox(data.c, theta_c)
    dl_bc_dtheta_l = _fast_d_boxcox_dtheta(data.l, theta_l)
    dc_bc_dtheta_c = _fast_d_boxcox_dtheta(data.c, theta_c)
    
    beta_leisure = (
        beta_l0
        + beta_l_log_age * data.log_age
        + beta_l_log_age2 * data.log_age2
        + beta_l_ch4_6 * data.children4_6
        + beta_l_ch7_9 * data.children7_9
        + beta_l_educL * data.educL
        + beta_l_educH * data.educH
        + beta_l_reg2 * data.reg2
    )
    if not is_male:
        beta_leisure = beta_leisure + beta_l_ch0_3 * data.children0_3
    
    u = beta_leisure * l_bc + beta_c * c_bc
    
    # Preference derivatives
    du_dtheta = np.zeros((n, 12), dtype=np.float64)
    du_dtheta[:, 0] = l_bc
    du_dtheta[:, 1] = data.log_age * l_bc
    du_dtheta[:, 2] = data.log_age2 * l_bc
    du_dtheta[:, 3] = data.children4_6 * l_bc
    du_dtheta[:, 4] = data.children7_9 * l_bc
    du_dtheta[:, 5] = data.educL * l_bc
    du_dtheta[:, 6] = data.educH * l_bc
    du_dtheta[:, 7] = data.reg2 * l_bc
    du_dtheta[:, 8] = c_bc
    du_dtheta[:, 9] = beta_leisure * dl_bc_dtheta_l
    du_dtheta[:, 10] = beta_c * dc_bc_dtheta_c
    if not is_male:
        du_dtheta[:, 11] = data.children0_3 * l_bc
    
    # Hours opportunity
    h_opp = (
        beta_work * data.working
        + beta_pt1 * data.working_pt1
        + beta_pt2 * data.working_pt2
        + beta_ft * data.working_ft
        + beta_gsur * data.working * data.gsur
        + beta_work_educL * data.working * data.educL
        + beta_work_educH * data.working * data.educH
        + beta_work_reg2 * data.working * data.reg2
        + beta_work_reg3 * data.working * data.reg3
    )
    
    dh_dtheta = np.zeros((n, 9), dtype=np.float64)
    dh_dtheta[:, 0] = data.working
    dh_dtheta[:, 1] = data.working_pt1
    dh_dtheta[:, 2] = data.working_pt2
    dh_dtheta[:, 3] = data.working_ft
    dh_dtheta[:, 4] = data.working * data.gsur
    dh_dtheta[:, 5] = data.working * data.educL
    dh_dtheta[:, 6] = data.working * data.educH
    dh_dtheta[:, 7] = data.working * data.reg2
    dh_dtheta[:, 8] = data.working * data.reg3
    
    # Wage opportunity
    if wage_spec == "vw":
        w_beta0 = theta[21]
        w_educL, w_educH = theta[22], theta[23]
        w_pexp, w_pexp2 = theta[24], theta[25]
        w_reg2, w_reg3, w_reg4, w_reg5 = theta[26], theta[27], theta[28], theta[29]
        w_reg6, w_reg7, w_reg8, w_reg9 = theta[30], theta[31], theta[32], theta[33]
        w_yd1, w_yd2 = theta[34], theta[35]
        sigma = abs(theta[36]) + 1e-6
        
        mean_logw = (
            w_beta0
            + w_educL * data.educL + w_educH * data.educH
            + w_pexp * data.pexp + w_pexp2 * data.pexp2
            + w_reg2 * data.reg2 + w_reg3 * data.reg3
            + w_reg4 * data.reg4 + w_reg5 * data.reg5
            + w_reg6 * data.reg6 + w_reg7 * data.reg7
            + w_reg8 * data.reg8 + w_reg9 * data.reg9
            + w_yd1 * data.yd1 + w_yd2 * data.yd2
        )
        
        z = (data.log_wage - mean_logw) / sigma
        w_opp = np.where(data.working > 0, -0.5 * z * z - np.log(sigma) - data.log_wage, 0.0)
        
        z_over_sigma = z / sigma
        dw_dtheta = np.zeros((n, 16), dtype=np.float64)
        dw_dtheta[:, 0] = z_over_sigma
        dw_dtheta[:, 1] = z_over_sigma * data.educL
        dw_dtheta[:, 2] = z_over_sigma * data.educH
        dw_dtheta[:, 3] = z_over_sigma * data.pexp
        dw_dtheta[:, 4] = z_over_sigma * data.pexp2
        dw_dtheta[:, 5] = z_over_sigma * data.reg2
        dw_dtheta[:, 6] = z_over_sigma * data.reg3
        dw_dtheta[:, 7] = z_over_sigma * data.reg4
        dw_dtheta[:, 8] = z_over_sigma * data.reg5
        dw_dtheta[:, 9] = z_over_sigma * data.reg6
        dw_dtheta[:, 10] = z_over_sigma * data.reg7
        dw_dtheta[:, 11] = z_over_sigma * data.reg8
        dw_dtheta[:, 12] = z_over_sigma * data.reg9
        dw_dtheta[:, 13] = z_over_sigma * data.yd1
        dw_dtheta[:, 14] = z_over_sigma * data.yd2
        dw_dtheta[:, 15] = (z * z - 1.0) / sigma
        dw_dtheta = np.where(data.working[:, None] > 0, dw_dtheta, 0.0)
    else:
        w_opp = 0.0
        dw_dtheta = np.zeros((n, 16), dtype=np.float64)
    
    # Composite V and dV/dtheta
    V = u + h_opp + w_opp - data.log_prior
    
    dV_dtheta = np.zeros((n, n_params), dtype=np.float64)
    dV_dtheta[:, 0:12] = du_dtheta
    dV_dtheta[:, 12:21] = dh_dtheta
    if wage_spec == "vw":
        dV_dtheta[:, 21:37] = dw_dtheta
    
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
    """
    if NUMBA_AVAILABLE and _compute_log_likelihood_numba is not None:
        # Compute V once
        n = len(data.c)
        
        # Quick V computation (same as in gradient)
        beta_l0, beta_l_log_age, beta_l_log_age2 = theta[0], theta[1], theta[2]
        beta_l_ch4_6, beta_l_ch7_9 = theta[3], theta[4]
        beta_l_educL, beta_l_educH, beta_l_reg2 = theta[5], theta[6], theta[7]
        beta_c, theta_l, theta_c = theta[8], theta[9], theta[10]
        beta_l_ch0_3 = theta[11]
        
        l_bc = _fast_boxcox(data.l, theta_l)
        c_bc = _fast_boxcox(data.c, theta_c)
        
        beta_leisure = (
            beta_l0
            + beta_l_log_age * data.log_age
            + beta_l_log_age2 * data.log_age2
            + beta_l_ch4_6 * data.children4_6
            + beta_l_ch7_9 * data.children7_9
            + beta_l_educL * data.educL
            + beta_l_educH * data.educH
            + beta_l_reg2 * data.reg2
        )
        if not is_male:
            beta_leisure = beta_leisure + beta_l_ch0_3 * data.children0_3
        
        u = beta_leisure * l_bc + beta_c * c_bc
        
        # Hours opp
        beta_work, beta_pt1, beta_pt2, beta_ft = theta[12], theta[13], theta[14], theta[15]
        beta_gsur, beta_work_educL, beta_work_educH = theta[16], theta[17], theta[18]
        beta_work_reg2, beta_work_reg3 = theta[19], theta[20]
        
        h_opp = (
            beta_work * data.working
            + beta_pt1 * data.working_pt1
            + beta_pt2 * data.working_pt2
            + beta_ft * data.working_ft
            + beta_gsur * data.working * data.gsur
            + beta_work_educL * data.working * data.educL
            + beta_work_educH * data.working * data.educH
            + beta_work_reg2 * data.working * data.reg2
            + beta_work_reg3 * data.working * data.reg3
        )
        
        # Wage opp
        if wage_spec == "vw":
            w_beta0 = theta[21]
            w_educL, w_educH = theta[22], theta[23]
            w_pexp, w_pexp2 = theta[24], theta[25]
            w_reg2, w_reg3, w_reg4, w_reg5 = theta[26], theta[27], theta[28], theta[29]
            w_reg6, w_reg7, w_reg8, w_reg9 = theta[30], theta[31], theta[32], theta[33]
            w_yd1, w_yd2 = theta[34], theta[35]
            sigma = abs(theta[36]) + 1e-6
            
            mean_logw = (
                w_beta0
                + w_educL * data.educL + w_educH * data.educH
                + w_pexp * data.pexp + w_pexp2 * data.pexp2
                + w_reg2 * data.reg2 + w_reg3 * data.reg3
                + w_reg4 * data.reg4 + w_reg5 * data.reg5
                + w_reg6 * data.reg6 + w_reg7 * data.reg7
                + w_reg8 * data.reg8 + w_reg9 * data.reg9
                + w_yd1 * data.yd1 + w_yd2 * data.yd2
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
Joint estimation matches Stijn's approach where:

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


@dataclass
class PrefParamsCouples:
    """
    Preference parameters for couples (joint household utility).
    
    Following Stijn's structure:
    U = β_l_m(X_m) * BC(l_m; θ_l_m) + β_l_f(X_f) * BC(l_f; θ_l_f) 
        + β_c * BC(c_total; θ_c) + β_int * BC(l_m) * BC(l_f)
    
    Where X includes age, children, education, region for each partner.
    """
    # Male leisure preferences (10 params: [0-9])
    beta_l0_m: float = 1.0
    beta_l_log_age_m: float = 0.0
    beta_l_log_age2_m: float = 0.0
    beta_l_ch0_3_m: float = 0.0     # children 0-3 (relevant for males too in couples)
    beta_l_ch4_6_m: float = 0.0
    beta_l_ch7_9_m: float = 0.0
    beta_l_reg2_m: float = 0.0      # region (regW in Stijn)
    beta_l_reg3_m: float = 0.0      # region (regB in Stijn)
    beta_l_educL_m: float = 0.0
    beta_l_educH_m: float = 0.0
    
    # Female leisure preferences (10 params: [10-19])
    beta_l0_f: float = 1.0
    beta_l_log_age_f: float = 0.0
    beta_l_log_age2_f: float = 0.0
    beta_l_ch0_3_f: float = 0.2     # children 0-3 (typically larger for females)
    beta_l_ch4_6_f: float = 0.1
    beta_l_ch7_9_f: float = 0.0
    beta_l_reg2_f: float = 0.0
    beta_l_reg3_f: float = 0.0
    beta_l_educL_f: float = 0.0
    beta_l_educH_f: float = 0.0
    
    # Box-Cox exponents (3 params: [20-22])
    theta_l_m: float = 0.5          # male leisure Box-Cox
    theta_l_f: float = 0.5          # female leisure Box-Cox
    theta_c: float = 0.5            # consumption Box-Cox
    
    # Consumption and interaction (2 params: [23-24])
    beta_c: float = 1.0             # consumption coefficient
    beta_interaction: float = 0.0   # leisure interaction term l_m * l_f


def get_n_params_joint(wage_spec: str = "fw") -> Dict[str, int]:
    """
    Get parameter counts for joint estimation.
    
    Parameters are structured as:
    - Preferences (group-specific): sm(12) + sf(13) + couples(25) = 50
    - Hours opportunity (gender-specific): male(9) + female(9) = 18
    - Wage opportunity (gender-specific, vw only): male(16) + female(16) = 32
    
    Total: 50 + 18 = 68 (fw) or 50 + 18 + 32 = 100 (vw)
    """
    n_pref_sm = 12      # single males preferences
    n_pref_sf = 13      # single females preferences (includes ch0_3)
    n_pref_cou = 25     # couples preferences
    n_hopp_m = 9        # hours opportunity (males)
    n_hopp_f = 9        # hours opportunity (females)
    n_wopp_m = 16       # wage opportunity (males)
    n_wopp_f = 16       # wage opportunity (females)
    
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
    
    Parameter layout:
    [0:12]   - Single males preferences
    [12:25]  - Single females preferences (13 params, includes ch0_3)
    [25:50]  - Couples preferences (25 params)
    [50:59]  - Hours opportunity (males)
    [59:68]  - Hours opportunity (females)
    [68:84]  - Wage opportunity (males, vw only)
    [84:100] - Wage opportunity (females, vw only)
    """
    # Single males preferences (12)
    pref_sm = [
        1.0,   # beta_l0
        0.0,   # beta_l_log_age
        0.0,   # beta_l_log_age2
        0.0,   # beta_l_ch4_6
        0.0,   # beta_l_ch7_9
        0.0,   # beta_l_educL
        0.0,   # beta_l_educH
        0.0,   # beta_l_reg2
        1.0,   # beta_c
        0.5,   # theta_l
        0.5,   # theta_c
        0.0,   # beta_l_ch0_3 (placeholder for males)
    ]
    
    # Single females preferences (13 - with active ch0_3)
    pref_sf = [
        1.0,   # beta_l0
        0.0,   # beta_l_log_age
        0.0,   # beta_l_log_age2
        0.1,   # beta_l_ch4_6
        0.0,   # beta_l_ch7_9
        0.0,   # beta_l_educL
        0.0,   # beta_l_educH
        0.0,   # beta_l_reg2
        1.0,   # beta_c
        0.5,   # theta_l
        0.5,   # theta_c
        0.2,   # beta_l_ch0_3 (active for females)
        0.0,   # beta_l_reg3 (additional for females)
    ]
    
    # Couples preferences (25)
    pref_cou = [
        # Male leisure (10)
        1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        # Female leisure (10)
        1.0, 0.0, 0.0, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0,
        # Box-Cox exponents (3)
        0.5, 0.5, 0.5,
        # Consumption and interaction (2)
        1.0, 0.0,
    ]
    
    # Hours opportunity - males (9)
    hopp_m = [
        0.5,   # beta_work
        0.0,   # beta_pt1
        0.0,   # beta_pt2
        0.0,   # beta_ft
        0.0,   # beta_gsur
        0.0,   # beta_work_educL
        0.0,   # beta_work_educH
        0.0,   # beta_work_reg2
        0.0,   # beta_work_reg3
    ]
    
    # Hours opportunity - females (9, same structure)
    hopp_f = [
        0.5,   # beta_work
        0.0,   # beta_pt1
        0.0,   # beta_pt2
        0.0,   # beta_ft
        0.0,   # beta_gsur
        0.0,   # beta_work_educL
        0.0,   # beta_work_educH
        0.0,   # beta_work_reg2
        0.0,   # beta_work_reg3
    ]
    
    theta = pref_sm + pref_sf + pref_cou + hopp_m + hopp_f
    
    if wage_spec == "vw":
        # Wage opportunity - males (16)
        wopp_m = [
            2.5,    # beta0
            -0.1,   # beta_educL
            0.2,    # beta_educH
            0.02,   # beta_pexp
            -0.001, # beta_pexp2
            -0.05, -0.05, -0.05, -0.05, -0.05, -0.05, -0.05, -0.10,  # reg2-reg9
            0.0, 0.0,  # yd1, yd2
            0.4,    # sigma
        ]
        
        # Wage opportunity - females (16, same structure but different values)
        wopp_f = [
            2.3,    # beta0 (typically lower)
            -0.1,   # beta_educL
            0.2,    # beta_educH
            0.02,   # beta_pexp
            -0.001, # beta_pexp2
            -0.05, -0.05, -0.05, -0.05, -0.05, -0.05, -0.05, -0.10,  # reg2-reg9
            0.0, 0.0,  # yd1, yd2
            0.4,    # sigma
        ]
        
        theta = theta + wopp_m + wopp_f
    
    return np.array(theta)


def get_param_names_joint(wage_spec: str = "fw") -> List[str]:
    """Return parameter names for joint estimation."""
    names = []
    
    # Single males preferences (12)
    names += [
        "sm.pref.beta_l0", "sm.pref.beta_l_log_age", "sm.pref.beta_l_log_age2",
        "sm.pref.beta_l_ch4_6", "sm.pref.beta_l_ch7_9",
        "sm.pref.beta_l_educL", "sm.pref.beta_l_educH", "sm.pref.beta_l_reg2",
        "sm.pref.beta_c", "sm.pref.theta_l", "sm.pref.theta_c", "sm.pref.beta_l_ch0_3",
    ]
    
    # Single females preferences (13)
    names += [
        "sf.pref.beta_l0", "sf.pref.beta_l_log_age", "sf.pref.beta_l_log_age2",
        "sf.pref.beta_l_ch4_6", "sf.pref.beta_l_ch7_9",
        "sf.pref.beta_l_educL", "sf.pref.beta_l_educH", "sf.pref.beta_l_reg2",
        "sf.pref.beta_c", "sf.pref.theta_l", "sf.pref.theta_c", "sf.pref.beta_l_ch0_3",
        "sf.pref.beta_l_reg3",
    ]
    
    # Couples preferences (25)
    names += [
        # Male (10)
        "cou.pref.beta_l0_m", "cou.pref.beta_l_log_age_m", "cou.pref.beta_l_log_age2_m",
        "cou.pref.beta_l_ch0_3_m", "cou.pref.beta_l_ch4_6_m", "cou.pref.beta_l_ch7_9_m",
        "cou.pref.beta_l_reg2_m", "cou.pref.beta_l_reg3_m",
        "cou.pref.beta_l_educL_m", "cou.pref.beta_l_educH_m",
        # Female (10)
        "cou.pref.beta_l0_f", "cou.pref.beta_l_log_age_f", "cou.pref.beta_l_log_age2_f",
        "cou.pref.beta_l_ch0_3_f", "cou.pref.beta_l_ch4_6_f", "cou.pref.beta_l_ch7_9_f",
        "cou.pref.beta_l_reg2_f", "cou.pref.beta_l_reg3_f",
        "cou.pref.beta_l_educL_f", "cou.pref.beta_l_educH_f",
        # Box-Cox and shared (5)
        "cou.pref.theta_l_m", "cou.pref.theta_l_f", "cou.pref.theta_c",
        "cou.pref.beta_c", "cou.pref.beta_interaction",
    ]
    
    # Hours opportunity - males (9)
    names += [
        "hopp_m.beta_work", "hopp_m.beta_pt1", "hopp_m.beta_pt2", "hopp_m.beta_ft",
        "hopp_m.beta_gsur", "hopp_m.beta_work_educL", "hopp_m.beta_work_educH",
        "hopp_m.beta_work_reg2", "hopp_m.beta_work_reg3",
    ]
    
    # Hours opportunity - females (9)
    names += [
        "hopp_f.beta_work", "hopp_f.beta_pt1", "hopp_f.beta_pt2", "hopp_f.beta_ft",
        "hopp_f.beta_gsur", "hopp_f.beta_work_educL", "hopp_f.beta_work_educH",
        "hopp_f.beta_work_reg2", "hopp_f.beta_work_reg3",
    ]
    
    if wage_spec == "vw":
        # Wage opportunity - males (16)
        names += [
            "wopp_m.beta0", "wopp_m.beta_educL", "wopp_m.beta_educH",
            "wopp_m.beta_pexp", "wopp_m.beta_pexp2",
            "wopp_m.beta_reg2", "wopp_m.beta_reg3", "wopp_m.beta_reg4", "wopp_m.beta_reg5",
            "wopp_m.beta_reg6", "wopp_m.beta_reg7", "wopp_m.beta_reg8", "wopp_m.beta_reg9",
            "wopp_m.beta_yd1", "wopp_m.beta_yd2", "wopp_m.sigma",
        ]
        
        # Wage opportunity - females (16)
        names += [
            "wopp_f.beta0", "wopp_f.beta_educL", "wopp_f.beta_educH",
            "wopp_f.beta_pexp", "wopp_f.beta_pexp2",
            "wopp_f.beta_reg2", "wopp_f.beta_reg3", "wopp_f.beta_reg4", "wopp_f.beta_reg5",
            "wopp_f.beta_reg6", "wopp_f.beta_reg7", "wopp_f.beta_reg8", "wopp_f.beta_reg9",
            "wopp_f.beta_yd1", "wopp_f.beta_yd2", "wopp_f.sigma",
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
    
    Parameters
    ----------
    theta_joint : np.ndarray
        Full joint parameter vector
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
    counts = get_n_params_joint(wage_spec)
    
    # Index boundaries in joint theta
    idx_pref_sm_start = 0
    idx_pref_sm_end = 12
    idx_pref_sf_start = 12
    idx_pref_sf_end = 25
    idx_pref_cou_start = 25
    idx_pref_cou_end = 50
    idx_hopp_m_start = 50
    idx_hopp_m_end = 59
    idx_hopp_f_start = 59
    idx_hopp_f_end = 68
    
    if wage_spec == "vw":
        idx_wopp_m_start = 68
        idx_wopp_m_end = 84
        idx_wopp_f_start = 84
        idx_wopp_f_end = 100
    
    if group == "sm":
        # Single males: preferences(12) + hopp_m(9) + wopp_m(16 if vw)
        pref = theta_joint[idx_pref_sm_start:idx_pref_sm_end]
        hopp = theta_joint[idx_hopp_m_start:idx_hopp_m_end]
        result = np.concatenate([pref, hopp])
        if wage_spec == "vw":
            wopp = theta_joint[idx_wopp_m_start:idx_wopp_m_end]
            result = np.concatenate([result, wopp])
        return result
        
    elif group == "sf":
        # Single females: preferences(13) + hopp_f(9) + wopp_f(16 if vw)
        # Note: sf has 13 preference params in joint (includes extra reg3)
        # But our singles functions expect 12, so we need to handle this
        pref_sf = theta_joint[idx_pref_sf_start:idx_pref_sf_end]
        # Remap to standard 12-param layout (drop the extra reg3 or handle it)
        pref = pref_sf[:12]  # Take first 12 (standard layout)
        hopp = theta_joint[idx_hopp_f_start:idx_hopp_f_end]
        result = np.concatenate([pref, hopp])
        if wage_spec == "vw":
            wopp = theta_joint[idx_wopp_f_start:idx_wopp_f_end]
            result = np.concatenate([result, wopp])
        return result
        
    elif group == "cou":
        # Couples need all: preferences(25) + hopp_m(9) + hopp_f(9) + wopp_m(16) + wopp_f(16)
        # This is a different format - couples have their own likelihood function
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
    
    For couples, theta layout is:
    - Preferences: 25 params
    - Hours opp male: 9 params
    - Hours opp female: 9 params
    - Wage opp male: 16 params (vw only)
    - Wage opp female: 16 params (vw only)
    
    Returns
    -------
    pref : PrefParamsCouples
    hopp_m : HoursOppParams
    hopp_f : HoursOppParams
    wopp_m : WageOppParams (or None for fw)
    wopp_f : WageOppParams (or None for fw)
    """
    # Preferences (25 params)
    pref = PrefParamsCouples(
        # Male leisure (10)
        beta_l0_m=theta[0],
        beta_l_log_age_m=theta[1],
        beta_l_log_age2_m=theta[2],
        beta_l_ch0_3_m=theta[3],
        beta_l_ch4_6_m=theta[4],
        beta_l_ch7_9_m=theta[5],
        beta_l_reg2_m=theta[6],
        beta_l_reg3_m=theta[7],
        beta_l_educL_m=theta[8],
        beta_l_educH_m=theta[9],
        # Female leisure (10)
        beta_l0_f=theta[10],
        beta_l_log_age_f=theta[11],
        beta_l_log_age2_f=theta[12],
        beta_l_ch0_3_f=theta[13],
        beta_l_ch4_6_f=theta[14],
        beta_l_ch7_9_f=theta[15],
        beta_l_reg2_f=theta[16],
        beta_l_reg3_f=theta[17],
        beta_l_educL_f=theta[18],
        beta_l_educH_f=theta[19],
        # Box-Cox (3)
        theta_l_m=theta[20],
        theta_l_f=theta[21],
        theta_c=theta[22],
        # Consumption and interaction (2)
        beta_c=theta[23],
        beta_interaction=theta[24],
    )
    
    # Hours opportunity - male (9 params: indices 25-33)
    hopp_m = HoursOppParams(
        beta_work=theta[25],
        beta_pt1=theta[26],
        beta_pt2=theta[27],
        beta_ft=theta[28],
        beta_gsur=theta[29],
        beta_work_educL=theta[30],
        beta_work_educH=theta[31],
        beta_work_reg2=theta[32],
        beta_work_reg3=theta[33],
    )
    
    # Hours opportunity - female (9 params: indices 34-42)
    hopp_f = HoursOppParams(
        beta_work=theta[34],
        beta_pt1=theta[35],
        beta_pt2=theta[36],
        beta_ft=theta[37],
        beta_gsur=theta[38],
        beta_work_educL=theta[39],
        beta_work_educH=theta[40],
        beta_work_reg2=theta[41],
        beta_work_reg3=theta[42],
    )
    
    if wage_spec == "vw":
        # Wage opportunity - male (16 params: indices 43-58)
        wopp_m = WageOppParams(
            beta0=theta[43],
            beta_educL=theta[44],
            beta_educH=theta[45],
            beta_pexp=theta[46],
            beta_pexp2=theta[47],
            beta_reg2=theta[48],
            beta_reg3=theta[49],
            beta_reg4=theta[50],
            beta_reg5=theta[51],
            beta_reg6=theta[52],
            beta_reg7=theta[53],
            beta_reg8=theta[54],
            beta_reg9=theta[55],
            beta_yd1=theta[56],
            beta_yd2=theta[57],
            sigma=theta[58],
        )
        
        # Wage opportunity - female (16 params: indices 59-74)
        wopp_f = WageOppParams(
            beta0=theta[59],
            beta_educL=theta[60],
            beta_educH=theta[61],
            beta_pexp=theta[62],
            beta_pexp2=theta[63],
            beta_reg2=theta[64],
            beta_reg3=theta[65],
            beta_reg4=theta[66],
            beta_reg5=theta[67],
            beta_reg6=theta[68],
            beta_reg7=theta[69],
            beta_reg8=theta[70],
            beta_reg9=theta[71],
            beta_yd1=theta[72],
            beta_yd2=theta[73],
            sigma=theta[74],
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
    
    Parameters
    ----------
    theta : np.ndarray
        Flat parameter vector for couples:
        - fw: 43 params (25 pref + 9 hopp_m + 9 hopp_f)
        - vw: 75 params (25 pref + 9 hopp_m + 9 hopp_f + 16 wopp_m + 16 wopp_f)
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
    
    Similar structure to singles, but with joint utility over both partners.
    
    Parameters
    ----------
    theta : np.ndarray
        Couples parameter vector (43 for fw, 75 for vw)
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
        # Return zero gradient of appropriate size
        n_params = 43 if wage_spec == "fw" else 75
        return np.zeros(n_params)
    
    n_params = 43 if wage_spec == "fw" else 75
    
    # Unpack parameters
    pref, hopp_m, hopp_f, wopp_m, wopp_f = unpack_theta_couples(theta, wage_spec)
    
    # =========================================================================
    # Compute utility and derivatives for couples
    # This is more complex than singles due to joint utility
    # =========================================================================
    
    # Get normalized leisure and consumption
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
    l_m_bc = boxcox_transform(l_m, pref.theta_l_m)
    l_f_bc = boxcox_transform(l_f, pref.theta_l_f)
    c_bc = boxcox_transform(c_total, pref.theta_c)
    
    # Derivatives of Box-Cox w.r.t. theta
    dl_m_bc_dtheta = d_boxcox_dtheta(l_m, pref.theta_l_m)
    dl_f_bc_dtheta = d_boxcox_dtheta(l_f, pref.theta_l_f)
    dc_bc_dtheta = d_boxcox_dtheta(c_total, pref.theta_c)
    
    # Covariates
    if "dag_m" in df.columns:
        age_m = pd.to_numeric(df["dag_m"], errors="coerce").fillna(40).to_numpy()
        log_age_m = np.log(np.clip(age_m, 18, 65))
        log_age2_m = log_age_m ** 2
    else:
        log_age_m = np.zeros(n)
        log_age2_m = np.zeros(n)
    
    if "dag_f" in df.columns:
        age_f = pd.to_numeric(df["dag_f"], errors="coerce").fillna(40).to_numpy()
        log_age_f = np.log(np.clip(age_f, 18, 65))
        log_age2_f = log_age_f ** 2
    else:
        log_age_f = np.zeros(n)
        log_age2_f = np.zeros(n)
    
    children0_3 = _get_col(df, "children0_3", 0.0)
    children4_6 = _get_col(df, "children4_6", 0.0)
    children7_9 = _get_col(df, "children7_9", 0.0)
    educL_m = _get_col(df, "educL_m", 0.0)
    educH_m = _get_col(df, "educH_m", 0.0)
    educL_f = _get_col(df, "educL_f", 0.0)
    educH_f = _get_col(df, "educH_f", 0.0)
    reg2 = _get_col(df, "regW", 0.0)
    if reg2.sum() == 0:
        reg2 = _get_col(df, "reg_nuts1_2", 0.0)
    reg3 = _get_col(df, "regB", 0.0)
    if reg3.sum() == 0:
        reg3 = _get_col(df, "reg_nuts1_3", 0.0)
    
    # Beta leisure coefficients
    beta_leisure_m = (
        pref.beta_l0_m + pref.beta_l_log_age_m * log_age_m + pref.beta_l_log_age2_m * log_age2_m
        + pref.beta_l_ch0_3_m * children0_3 + pref.beta_l_ch4_6_m * children4_6
        + pref.beta_l_ch7_9_m * children7_9 + pref.beta_l_reg2_m * reg2 + pref.beta_l_reg3_m * reg3
        + pref.beta_l_educL_m * educL_m + pref.beta_l_educH_m * educH_m
    )
    beta_leisure_f = (
        pref.beta_l0_f + pref.beta_l_log_age_f * log_age_f + pref.beta_l_log_age2_f * log_age2_f
        + pref.beta_l_ch0_3_f * children0_3 + pref.beta_l_ch4_6_f * children4_6
        + pref.beta_l_ch7_9_f * children7_9 + pref.beta_l_reg2_f * reg2 + pref.beta_l_reg3_f * reg3
        + pref.beta_l_educL_f * educL_f + pref.beta_l_educH_f * educH_f
    )
    
    # Compute utility
    u = (beta_leisure_m * l_m_bc + beta_leisure_f * l_f_bc
         + pref.beta_c * c_bc + pref.beta_interaction * l_m_bc * l_f_bc)
    
    # =========================================================================
    # Preference derivatives (25 params)
    # =========================================================================
    du_dpref = np.zeros((n, 25), dtype=float)
    
    # Male leisure params [0-9]
    du_dpref[:, 0] = l_m_bc  # beta_l0_m
    du_dpref[:, 1] = log_age_m * l_m_bc  # beta_l_log_age_m
    du_dpref[:, 2] = log_age2_m * l_m_bc  # beta_l_log_age2_m
    du_dpref[:, 3] = children0_3 * l_m_bc  # beta_l_ch0_3_m
    du_dpref[:, 4] = children4_6 * l_m_bc  # beta_l_ch4_6_m
    du_dpref[:, 5] = children7_9 * l_m_bc  # beta_l_ch7_9_m
    du_dpref[:, 6] = reg2 * l_m_bc  # beta_l_reg2_m
    du_dpref[:, 7] = reg3 * l_m_bc  # beta_l_reg3_m
    du_dpref[:, 8] = educL_m * l_m_bc  # beta_l_educL_m
    du_dpref[:, 9] = educH_m * l_m_bc  # beta_l_educH_m
    
    # Female leisure params [10-19]
    du_dpref[:, 10] = l_f_bc  # beta_l0_f
    du_dpref[:, 11] = log_age_f * l_f_bc  # beta_l_log_age_f
    du_dpref[:, 12] = log_age2_f * l_f_bc  # beta_l_log_age2_f
    du_dpref[:, 13] = children0_3 * l_f_bc  # beta_l_ch0_3_f
    du_dpref[:, 14] = children4_6 * l_f_bc  # beta_l_ch4_6_f
    du_dpref[:, 15] = children7_9 * l_f_bc  # beta_l_ch7_9_f
    du_dpref[:, 16] = reg2 * l_f_bc  # beta_l_reg2_f
    du_dpref[:, 17] = reg3 * l_f_bc  # beta_l_reg3_f
    du_dpref[:, 18] = educL_f * l_f_bc  # beta_l_educL_f
    du_dpref[:, 19] = educH_f * l_f_bc  # beta_l_educH_f
    
    # Box-Cox and shared params [20-24]
    # theta_l_m: derivative of u w.r.t. theta_l_m (complex due to interaction)
    du_dpref[:, 20] = (beta_leisure_m + pref.beta_interaction * l_f_bc) * dl_m_bc_dtheta
    # theta_l_f
    du_dpref[:, 21] = (beta_leisure_f + pref.beta_interaction * l_m_bc) * dl_f_bc_dtheta
    # theta_c
    du_dpref[:, 22] = pref.beta_c * dc_bc_dtheta
    # beta_c
    du_dpref[:, 23] = c_bc
    # beta_interaction
    du_dpref[:, 24] = l_m_bc * l_f_bc
    
    # =========================================================================
    # Hours opportunity derivatives (18 params: 9 male + 9 female)
    # =========================================================================
    # Get working indicators for both partners
    working_m = _get_col(df, "working_m", 0.0)
    working_pt1_m = _get_col(df, "working_pt1_m", 0.0)
    working_pt2_m = _get_col(df, "working_pt2_m", 0.0)
    working_ft_m = _get_col(df, "working_ft_m", 0.0)
    gsur_m = _get_col(df, "gsur_m", 0.0)
    if gsur_m.sum() == 0:
        gsur_m = _get_col(df, "gsur", 0.0)
    
    working_f = _get_col(df, "working_f", 0.0)
    working_pt1_f = _get_col(df, "working_pt1_f", 0.0)
    working_pt2_f = _get_col(df, "working_pt2_f", 0.0)
    working_ft_f = _get_col(df, "working_ft_f", 0.0)
    gsur_f = _get_col(df, "gsur_f", 0.0)
    if gsur_f.sum() == 0:
        gsur_f = _get_col(df, "gsur", 0.0)
    
    dh_dtheta = np.zeros((n, 18), dtype=float)
    # Male hopp [0-8]
    dh_dtheta[:, 0] = working_m
    dh_dtheta[:, 1] = working_pt1_m
    dh_dtheta[:, 2] = working_pt2_m
    dh_dtheta[:, 3] = working_ft_m
    dh_dtheta[:, 4] = working_m * gsur_m
    dh_dtheta[:, 5] = working_m * educL_m
    dh_dtheta[:, 6] = working_m * educH_m
    dh_dtheta[:, 7] = working_m * reg2
    dh_dtheta[:, 8] = working_m * reg3
    # Female hopp [9-17]
    dh_dtheta[:, 9] = working_f
    dh_dtheta[:, 10] = working_pt1_f
    dh_dtheta[:, 11] = working_pt2_f
    dh_dtheta[:, 12] = working_ft_f
    dh_dtheta[:, 13] = working_f * gsur_f
    dh_dtheta[:, 14] = working_f * educL_f
    dh_dtheta[:, 15] = working_f * educH_f
    dh_dtheta[:, 16] = working_f * reg2
    dh_dtheta[:, 17] = working_f * reg3
    
    # Compute hopp values
    h_opp = ff_calc_hopp_couples(df, hopp_m, hopp_f)
    
    # =========================================================================
    # Wage opportunity derivatives (32 params if vw: 16 male + 16 female)
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
        yd1 = _get_col(df, "yd1", 0.0)
        yd2 = _get_col(df, "yd2", 0.0)
        
        # Region dummies for wage equation
        if "drgn1" in df.columns:
            drgn1 = pd.to_numeric(df["drgn1"], errors="coerce").fillna(1).to_numpy()
            wreg2 = (drgn1 == 2).astype(float)
            wreg3 = (drgn1 == 3).astype(float)
            wreg4 = (drgn1 == 4).astype(float)
            wreg5 = (drgn1 == 5).astype(float)
            wreg6 = (drgn1 == 6).astype(float)
            wreg7 = (drgn1 == 7).astype(float)
            wreg8 = (drgn1 == 8).astype(float)
            wreg9 = (drgn1 == 9).astype(float)
        else:
            wreg2 = _get_col(df, "reg_nuts1_2", 0.0)
            wreg3 = _get_col(df, "reg_nuts1_3", 0.0)
            wreg4 = _get_col(df, "reg_nuts1_4", 0.0)
            wreg5 = _get_col(df, "reg_nuts1_5", 0.0)
            wreg6 = _get_col(df, "reg_nuts1_6", 0.0)
            wreg7 = _get_col(df, "reg_nuts1_7", 0.0)
            wreg8 = _get_col(df, "reg_nuts1_8", 0.0)
            wreg9 = _get_col(df, "reg_nuts1_9", 0.0)
        
        # Mean log-wage
        mean_logw_m = (wopp_m.beta0 + wopp_m.beta_educL * educL_m + wopp_m.beta_educH * educH_m
                       + wopp_m.beta_pexp * pexp_m + wopp_m.beta_pexp2 * pexp_m**2
                       + wopp_m.beta_reg2 * wreg2 + wopp_m.beta_reg3 * wreg3 + wopp_m.beta_reg4 * wreg4
                       + wopp_m.beta_reg5 * wreg5 + wopp_m.beta_reg6 * wreg6 + wopp_m.beta_reg7 * wreg7
                       + wopp_m.beta_reg8 * wreg8 + wopp_m.beta_reg9 * wreg9
                       + wopp_m.beta_yd1 * yd1 + wopp_m.beta_yd2 * yd2)
        mean_logw_f = (wopp_f.beta0 + wopp_f.beta_educL * educL_f + wopp_f.beta_educH * educH_f
                       + wopp_f.beta_pexp * pexp_f + wopp_f.beta_pexp2 * pexp_f**2
                       + wopp_f.beta_reg2 * wreg2 + wopp_f.beta_reg3 * wreg3 + wopp_f.beta_reg4 * wreg4
                       + wopp_f.beta_reg5 * wreg5 + wopp_f.beta_reg6 * wreg6 + wopp_f.beta_reg7 * wreg7
                       + wopp_f.beta_reg8 * wreg8 + wopp_f.beta_reg9 * wreg9
                       + wopp_f.beta_yd1 * yd1 + wopp_f.beta_yd2 * yd2)
        
        sigma_m = np.abs(wopp_m.sigma) + 1e-6
        sigma_f = np.abs(wopp_f.sigma) + 1e-6
        z_m = (log_wage_m - mean_logw_m) / sigma_m
        z_f = (log_wage_f - mean_logw_f) / sigma_f
        z_over_sigma_m = z_m / sigma_m
        z_over_sigma_f = z_f / sigma_f
        
        dw_dtheta = np.zeros((n, 32), dtype=float)
        # Male wopp [0-15]
        dw_dtheta[:, 0] = np.where(working_m > 0, z_over_sigma_m, 0)
        dw_dtheta[:, 1] = np.where(working_m > 0, z_over_sigma_m * educL_m, 0)
        dw_dtheta[:, 2] = np.where(working_m > 0, z_over_sigma_m * educH_m, 0)
        dw_dtheta[:, 3] = np.where(working_m > 0, z_over_sigma_m * pexp_m, 0)
        dw_dtheta[:, 4] = np.where(working_m > 0, z_over_sigma_m * pexp_m**2, 0)
        dw_dtheta[:, 5] = np.where(working_m > 0, z_over_sigma_m * wreg2, 0)
        dw_dtheta[:, 6] = np.where(working_m > 0, z_over_sigma_m * wreg3, 0)
        dw_dtheta[:, 7] = np.where(working_m > 0, z_over_sigma_m * wreg4, 0)
        dw_dtheta[:, 8] = np.where(working_m > 0, z_over_sigma_m * wreg5, 0)
        dw_dtheta[:, 9] = np.where(working_m > 0, z_over_sigma_m * wreg6, 0)
        dw_dtheta[:, 10] = np.where(working_m > 0, z_over_sigma_m * wreg7, 0)
        dw_dtheta[:, 11] = np.where(working_m > 0, z_over_sigma_m * wreg8, 0)
        dw_dtheta[:, 12] = np.where(working_m > 0, z_over_sigma_m * wreg9, 0)
        dw_dtheta[:, 13] = np.where(working_m > 0, z_over_sigma_m * yd1, 0)
        dw_dtheta[:, 14] = np.where(working_m > 0, z_over_sigma_m * yd2, 0)
        dw_dtheta[:, 15] = np.where(working_m > 0, (z_m**2 - 1) / sigma_m, 0)
        # Female wopp [16-31]
        dw_dtheta[:, 16] = np.where(working_f > 0, z_over_sigma_f, 0)
        dw_dtheta[:, 17] = np.where(working_f > 0, z_over_sigma_f * educL_f, 0)
        dw_dtheta[:, 18] = np.where(working_f > 0, z_over_sigma_f * educH_f, 0)
        dw_dtheta[:, 19] = np.where(working_f > 0, z_over_sigma_f * pexp_f, 0)
        dw_dtheta[:, 20] = np.where(working_f > 0, z_over_sigma_f * pexp_f**2, 0)
        dw_dtheta[:, 21] = np.where(working_f > 0, z_over_sigma_f * wreg2, 0)
        dw_dtheta[:, 22] = np.where(working_f > 0, z_over_sigma_f * wreg3, 0)
        dw_dtheta[:, 23] = np.where(working_f > 0, z_over_sigma_f * wreg4, 0)
        dw_dtheta[:, 24] = np.where(working_f > 0, z_over_sigma_f * wreg5, 0)
        dw_dtheta[:, 25] = np.where(working_f > 0, z_over_sigma_f * wreg6, 0)
        dw_dtheta[:, 26] = np.where(working_f > 0, z_over_sigma_f * wreg7, 0)
        dw_dtheta[:, 27] = np.where(working_f > 0, z_over_sigma_f * wreg8, 0)
        dw_dtheta[:, 28] = np.where(working_f > 0, z_over_sigma_f * wreg9, 0)
        dw_dtheta[:, 29] = np.where(working_f > 0, z_over_sigma_f * yd1, 0)
        dw_dtheta[:, 30] = np.where(working_f > 0, z_over_sigma_f * yd2, 0)
        dw_dtheta[:, 31] = np.where(working_f > 0, (z_f**2 - 1) / sigma_f, 0)
    else:
        w_opp = np.zeros(n)
        dw_dtheta = np.zeros((n, 32))
    
    # =========================================================================
    # Stack all derivatives
    # =========================================================================
    dV_dtheta = np.zeros((n, n_params), dtype=float)
    dV_dtheta[:, 0:25] = du_dpref
    dV_dtheta[:, 25:43] = dh_dtheta
    if wage_spec == "vw":
        dV_dtheta[:, 43:75] = dw_dtheta
    
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
    FAST joint estimation using precomputed data.
    
    This is 2-5x faster than neg_log_likelihood_with_grad_joint because:
    1. Uses precomputed numpy arrays instead of DataFrames
    2. Computes LL and gradient in single pass for each group
    3. Avoids repeated DataFrame column access
    
    Parameters
    ----------
    theta : np.ndarray
        Joint parameter vector (68 for fw, 100 for vw)
    data_sm : PrecomputedDataSingles or None
        Precomputed data for single males
    data_sf : PrecomputedDataSingles or None
        Precomputed data for single females
    data_cou : PrecomputedDataCouples or None
        Precomputed data for couples
    wage_spec : str
        "fw" or "vw"
    
    Returns
    -------
    Tuple[float, np.ndarray]
        (-LL, -gradient) for minimization
    """
    counts = get_n_params_joint(wage_spec)
    n_params = counts["total"]
    
    ll_total = 0.0
    grad = np.zeros(n_params, dtype=np.float64)
    
    # Index boundaries
    idx_pref_sm = (0, 12)
    idx_pref_sf = (12, 25)
    idx_pref_cou = (25, 50)
    idx_hopp_m = (50, 59)
    idx_hopp_f = (59, 68)
    
    if wage_spec == "vw":
        idx_wopp_m = (68, 84)
        idx_wopp_f = (84, 100)
    
    # Single males
    if data_sm is not None:
        # Extract theta for single males: pref_sm(12) + hopp_m(9) + wopp_m(16 if vw)
        theta_sm = np.concatenate([
            theta[idx_pref_sm[0]:idx_pref_sm[1]],
            theta[idx_hopp_m[0]:idx_hopp_m[1]],
        ])
        if wage_spec == "vw":
            theta_sm = np.concatenate([theta_sm, theta[idx_wopp_m[0]:idx_wopp_m[1]]])
        
        neg_ll_sm, neg_grad_sm = fast_neg_ll_with_grad_singles(
            theta_sm, data_sm, is_male=True, wage_spec=wage_spec
        )
        ll_total -= neg_ll_sm  # Convert back to LL
        
        # Map gradient to joint theta
        grad[idx_pref_sm[0]:idx_pref_sm[1]] -= neg_grad_sm[0:12]
        grad[idx_hopp_m[0]:idx_hopp_m[1]] -= neg_grad_sm[12:21]
        if wage_spec == "vw":
            grad[idx_wopp_m[0]:idx_wopp_m[1]] -= neg_grad_sm[21:37]
    
    # Single females
    if data_sf is not None:
        # Extract theta for single females: pref_sf(12) + hopp_f(9) + wopp_f(16 if vw)
        # Note: pref_sf has 13 params in joint but singles expects 12
        theta_sf = np.concatenate([
            theta[idx_pref_sf[0]:idx_pref_sf[0]+12],  # First 12 params only
            theta[idx_hopp_f[0]:idx_hopp_f[1]],
        ])
        if wage_spec == "vw":
            theta_sf = np.concatenate([theta_sf, theta[idx_wopp_f[0]:idx_wopp_f[1]]])
        
        neg_ll_sf, neg_grad_sf = fast_neg_ll_with_grad_singles(
            theta_sf, data_sf, is_male=False, wage_spec=wage_spec
        )
        ll_total -= neg_ll_sf
        
        # Map gradient
        grad[idx_pref_sf[0]:idx_pref_sf[0]+12] -= neg_grad_sf[0:12]
        grad[idx_hopp_f[0]:idx_hopp_f[1]] -= neg_grad_sf[12:21]
        if wage_spec == "vw":
            grad[idx_wopp_f[0]:idx_wopp_f[1]] -= neg_grad_sf[21:37]    # Couples
    if data_cou is not None:
        # The standalone fast_neg_ll_with_grad_couples expects 44 params (fw) or 76 params (vw):
        # [0:11]  Male leisure: beta_lm0, log_age, log_age2, ch0_3, ch4_6, ch7_9, educL, educH, reg2, reg3, reg4
        # [11:22] Female leisure: same order
        # [22:26] Box-Cox: theta_lm, theta_lf, theta_c, beta_c (4)
        # [26:35] Male hopp (9)
        # [35:44] Female hopp (9)
        # [44:60] Male wopp (16, vw only)
        # [60:76] Female wopp (16, vw only)
        #
        # The joint theta has couples pref at [25:50] = 25 params with layout:
        # Male leisure (10): beta_l0, log_age, log_age2, ch0_3, ch4_6, ch7_9, reg2, reg3, educL, educH
        # Female leisure (10): same order
        # Box-Cox (3): theta_lm, theta_lf, theta_c
        # Consumption + interaction (2): beta_c, beta_interaction
        #
        # Key difference: Joint has reg2,reg3 at indices 6,7 and educL,educH at 8,9
        #                Standalone has educL,educH at indices 6,7 and reg2,reg3 at 8,9, plus reg4 at 10
        joint_cou_pref = theta[idx_pref_cou[0]:idx_pref_cou[1]]  # 25 params
        
        # Build standalone-compatible theta_cou (44 for fw)
        theta_cou = np.zeros(44 if wage_spec == "fw" else 76, dtype=np.float64)
        
        # Male leisure [0:11] with reordering
        # Joint order: [0]=beta_l0, [1]=log_age, [2]=log_age2, [3]=ch0_3, [4]=ch4_6, [5]=ch7_9, 
        #              [6]=reg2, [7]=reg3, [8]=educL, [9]=educH
        # Standalone order: [0]=beta_lm0, [1]=log_age, [2]=log_age2, [3]=ch0_3, [4]=ch4_6, [5]=ch7_9,
        #                   [6]=educL, [7]=educH, [8]=reg2, [9]=reg3, [10]=reg4
        theta_cou[0:6] = joint_cou_pref[0:6]   # first 6 same
        theta_cou[6] = joint_cou_pref[8]       # educL
        theta_cou[7] = joint_cou_pref[9]       # educH
        theta_cou[8] = joint_cou_pref[6]       # reg2
        theta_cou[9] = joint_cou_pref[7]       # reg3
        theta_cou[10] = 0.0                    # reg4 (not in joint)
        
        # Female leisure [11:22] with same reordering
        theta_cou[11:17] = joint_cou_pref[10:16]  # first 6 same
        theta_cou[17] = joint_cou_pref[18]        # educL
        theta_cou[18] = joint_cou_pref[19]        # educH
        theta_cou[19] = joint_cou_pref[16]        # reg2
        theta_cou[20] = joint_cou_pref[17]        # reg3
        theta_cou[21] = 0.0                       # reg4 (not in joint)
        
        # Box-Cox [22:25] - joint has 3 at [20:23]
        theta_cou[22:25] = joint_cou_pref[20:23]
        
        # beta_c [25] - joint has at [23]
        theta_cou[25] = joint_cou_pref[23]
        
        # Hours opportunity
        theta_cou[26:35] = theta[idx_hopp_m[0]:idx_hopp_m[1]]
        theta_cou[35:44] = theta[idx_hopp_f[0]:idx_hopp_f[1]]
        
        if wage_spec == "vw":
            theta_cou[44:60] = theta[idx_wopp_m[0]:idx_wopp_m[1]]
            theta_cou[60:76] = theta[idx_wopp_f[0]:idx_wopp_f[1]]
        
        neg_ll_cou, neg_grad_cou = fast_neg_ll_with_grad_couples(
            theta_cou, data_cou, wage_spec=wage_spec
        )
        ll_total -= neg_ll_cou
        
        # Map gradient back - reverse the parameter mapping (with reordering)
        # Male leisure: standalone -> joint with inverse reordering
        # Joint [0:6] <- standalone [0:6]
        grad[idx_pref_cou[0]:idx_pref_cou[0]+6] -= neg_grad_cou[0:6]
        # Joint [6] (reg2) <- standalone [8]
        grad[idx_pref_cou[0]+6] -= neg_grad_cou[8]
        # Joint [7] (reg3) <- standalone [9]
        grad[idx_pref_cou[0]+7] -= neg_grad_cou[9]
        # Joint [8] (educL) <- standalone [6]
        grad[idx_pref_cou[0]+8] -= neg_grad_cou[6]
        # Joint [9] (educH) <- standalone [7]
        grad[idx_pref_cou[0]+9] -= neg_grad_cou[7]
        # standalone [10] (reg4) is not mapped back (not in joint)
        
        # Female leisure: same inverse reordering
        grad[idx_pref_cou[0]+10:idx_pref_cou[0]+16] -= neg_grad_cou[11:17]
        grad[idx_pref_cou[0]+16] -= neg_grad_cou[19]  # reg2
        grad[idx_pref_cou[0]+17] -= neg_grad_cou[20]  # reg3
        grad[idx_pref_cou[0]+18] -= neg_grad_cou[17]  # educL
        grad[idx_pref_cou[0]+19] -= neg_grad_cou[18]  # educH
        # standalone [21] (reg4) is not mapped back
        
        # Box-Cox grad [22:25] -> joint [45:48]
        grad[idx_pref_cou[0]+20:idx_pref_cou[0]+23] -= neg_grad_cou[22:25]
        # beta_c grad [25] -> joint [48]
        grad[idx_pref_cou[0]+23] -= neg_grad_cou[25]
        # (skip joint interaction param [49] - no gradient from standalone)
          # Hours opportunity
        grad[idx_hopp_m[0]:idx_hopp_m[1]] -= neg_grad_cou[26:35]
        grad[idx_hopp_f[0]:idx_hopp_f[1]] -= neg_grad_cou[35:44]
        
        if wage_spec == "vw":
            grad[idx_wopp_m[0]:idx_wopp_m[1]] -= neg_grad_cou[44:60]
            grad[idx_wopp_f[0]:idx_wopp_f[1]] -= neg_grad_cou[60:76]
    
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
            "with SHARED opportunity parameters by gender. This matches Stijn's approach "
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
            "Following Stijn Van Houtven's R approach."
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
                return result
              # Bounds for Box-Cox parameters (loosened: 0.001 to 5.0 for Box-Cox, 0.01 to 10.0 for sigma)
            bounds = [(None, None)] * len(theta0)
            # SM Box-Cox: indices 9, 10
            bounds[9] = (0.001, 5.0)   # theta_l (SM leisure)
            bounds[10] = (0.001, 5.0)  # theta_c (SM consumption)
            # SF Box-Cox: indices 21, 22
            bounds[21] = (0.001, 5.0)  # theta_l (SF leisure)
            bounds[22] = (0.001, 5.0)  # theta_c (SF consumption)
            # Couples Box-Cox: indices 45, 46, 47
            bounds[45] = (0.001, 5.0)  # theta_lm (couples male leisure)
            bounds[46] = (0.001, 5.0)  # theta_lf (couples female leisure)
            bounds[47] = (0.001, 5.0)  # theta_c (couples consumption)
            # Sigma bounds (if vw)
            if args.wage_spec == "vw":
                bounds[83] = (0.01, 10.0)   # sigma_m (male wage error SD)
                bounds[99] = (0.01, 10.0)   # sigma_f (female wage error SD)
            
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
                "param_names": param_names,
                "wage_spec": args.wage_spec,
                "n_sm": int(n_sm),
                "n_sf": int(n_sf),
                "n_cou": int(n_cou),
                "n_individuals": int(n_sm + n_sf + n_cou),  # Total individuals for post-estimation
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
                
                LOGGER.info("")
                LOGGER.info("=" * 60)
                LOGGER.info("JOINT POST-ESTIMATION ANALYSIS")
                LOGGER.info("=" * 60)
                
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
                else:
                    LOGGER.warning("Could not compute SE (Hessian may be singular)")
                
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
        bounds[9] = (0.001, 5.0)   # theta_l (Box-Cox leisure)
        bounds[10] = (0.001, 5.0)  # theta_c (Box-Cox consumption)
        if args.wage_spec == "vw":
            bounds[36] = (0.01, 10.0)  # sigma (wage error SD)
        
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
        bounds[22] = (0.001, 5.0)  # theta_lm (Box-Cox male leisure)
        bounds[23] = (0.001, 5.0)  # theta_lf (Box-Cox female leisure)
        bounds[24] = (0.001, 5.0)  # theta_c (Box-Cox consumption)
        if args.wage_spec == "vw":
            bounds[59] = (0.01, 10.0)  # sigma_m (male wage error SD)
            bounds[75] = (0.01, 10.0)  # sigma_f (female wage error SD)
        
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
    LOGGER.info("")
      # Legacy display for singles (for backwards compatibility)
    if is_singles:
        # Pad theta to 37 params if fw mode (needed by unpack_theta_singles)
        theta_full = result.x if len(result.x) == 37 else np.concatenate([result.x, np.zeros(16)])
        pref, hopp, wopp = unpack_theta_singles(theta_full)
        LOGGER.info("Estimated preference parameters:")
        LOGGER.info(f"  beta_l0:        {pref.beta_l0:.4f}")
        LOGGER.info(f"  beta_l_log_age: {pref.beta_l_log_age:.4f}")
        LOGGER.info(f"  beta_l_educL:   {pref.beta_l_educL:.4f}")
        LOGGER.info(f"  beta_l_educH:   {pref.beta_l_educH:.4f}")
        LOGGER.info(f"  beta_c:         {pref.beta_c:.4f}")
        LOGGER.info(f"  theta_l:        {pref.theta_l:.4f}")
        LOGGER.info(f"  theta_c:        {pref.theta_c:.4f}")
        LOGGER.info("")
        
        LOGGER.info("Estimated hours opportunity parameters:")
        LOGGER.info(f"  beta_work:      {hopp.beta_work:.4f}")
        LOGGER.info(f"  beta_pt1:       {hopp.beta_pt1:.4f}")
        LOGGER.info(f"  beta_pt2:       {hopp.beta_pt2:.4f}")
        LOGGER.info(f"  beta_ft:        {hopp.beta_ft:.4f}")
        LOGGER.info("")
        
        if args.wage_spec == "vw":
            LOGGER.info("Estimated wage opportunity parameters:")
            LOGGER.info(f"  beta0:          {wopp.beta0:.4f}")
            LOGGER.info(f"  beta_educL:     {wopp.beta_educL:.4f}")
            LOGGER.info(f"  beta_educH:     {wopp.beta_educH:.4f}")
            LOGGER.info(f"  beta_pexp:      {wopp.beta_pexp:.4f}")
            LOGGER.info(f"  beta_pexp2:     {wopp.beta_pexp2:.6f}")
            LOGGER.info(f"  sigma:          {wopp.sigma:.4f}")
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
