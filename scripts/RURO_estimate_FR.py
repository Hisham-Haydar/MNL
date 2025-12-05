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
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.optimize import minimize

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOGGER = logging.getLogger(__name__)

# =============================================================================
# Constants (aligned with RURO_draws.py and RURO_prep_mnl_basic.py)
# =============================================================================

TOTAL_LEISURE_HOURS = 80.0
MEAN_DISPY_NORM = 2500.0  # normalization constant for consumption (Stijn uses 2500)
MEAN_LHW_NORM = 35.0      # normalization constant for leisure (Stijn uses 35)


# =============================================================================
# Helper functions
# =============================================================================

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


def unpack_theta_singles(theta: np.ndarray) -> Tuple[PrefParamsSingles, HoursOppParams, WageOppParams]:
    """
    Unpack flat parameter array into dataclasses.
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
        beta_gsur=theta[16],        beta_work_educL=theta[17],
        beta_work_educH=theta[18],
        beta_work_reg2=theta[19],
        beta_work_reg3=theta[20],
    )
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
    if "c_norm" in df.columns:
        c = df["c_norm"].to_numpy()
    elif "dispy_util" in df.columns:
        c = df["dispy_util"].to_numpy()
    elif "consumption" in df.columns:
        # Normalize consumption by MEAN_DISPY_NORM
        c = df["consumption"].to_numpy() / MEAN_DISPY_NORM
    elif "ils_dispy" in df.columns:
        c = df["ils_dispy"].to_numpy() / MEAN_DISPY_NORM
    else:
        LOGGER.warning("No consumption column found; using 1.0 as placeholder.")
        c = np.ones(n)
    
    if "l_norm" in df.columns:
        l = df["l_norm"].to_numpy()
    elif "leis_util" in df.columns:
        l = df["leis_util"].to_numpy()
    elif "leisure" in df.columns:
        # Normalize leisure: (TOTAL_LEISURE - hours) / (TOTAL_LEISURE - MEAN_LHW)
        l = df["leisure"].to_numpy() / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    elif "hours" in df.columns:
        hours = df["hours"].to_numpy()
        l = (TOTAL_LEISURE_HOURS - hours) / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    else:
        LOGGER.warning("No leisure column found; using 1.0 as placeholder.")
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
    
    Stijn's structure for couples:
        u = (male leisure terms) * (l_m^θ_lm - 1)/θ_lm
          + (female leisure terms) * (l_f^θ_lf - 1)/θ_lf
          + β_c * ((c_m + c_f)^θ_c - 1)/θ_c
          + β_cross * (l_m^θ_lm - 1)/θ_lm * (l_f^θ_lf - 1)/θ_lf
    
    NOTE: This is a skeleton. The couples dataset should have _m and _f suffixes
    for male and female variables, or be pivoted to wide format.
    
    TODO: Implement full couples utility once data structure is confirmed.
    """
    n = len(df)
    
    # Placeholder: return zeros
    LOGGER.warning("Couples utility not fully implemented; returning zeros.")
    return np.zeros(n)


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
    
    # log f(w|X) = -0.5*z² - log(σ) - log(w) - 0.5*log(2π)
    # We omit -0.5*log(2π) as it cancels in the likelihood ratio
    w_opp = -0.5 * z**2 - np.log(sigma) - log_wage
    
    # For non-working alternatives (h=0), wage is structurally 0 → no density contribution
    w_opp = np.where(working > 0, w_opp, 0.0)
    
    return w_opp


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
    pref, hopp, wopp = unpack_theta_singles(theta)
    
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
    if "c_norm" in df.columns:
        c = df["c_norm"].to_numpy()
    elif "consumption" in df.columns:
        c = df["consumption"].to_numpy() / MEAN_DISPY_NORM
    else:
        c = np.ones(n)
    
    if "l_norm" in df.columns:
        l = df["l_norm"].to_numpy()
    elif "leisure" in df.columns:
        l = df["leisure"].to_numpy() / (TOTAL_LEISURE_HOURS - MEAN_LHW_NORM)
    elif "hours" in df.columns:
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
    # w_opp = -0.5 * ((log_wage - μ)/σ)² - log(σ) - log(wage)
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
    # FULLY VECTORIZED gradient computation using numpy
    # =========================================================================
    
    # Get unique IDs and build index mapping
    unique_ids, inverse_idx = np.unique(ids, return_inverse=True)
    n_individuals = len(unique_ids)
    
    # Group start/end indices (assumes data is sorted by id)
    # Use numpy to find group boundaries
    id_changes = np.where(np.diff(ids) != 0)[0] + 1
    group_starts = np.concatenate([[0], id_changes])
    group_ends = np.concatenate([id_changes, [n]])
    
    # Compute log-sum-exp per individual for numerical stability
    # First, find max V per group
    V_max = np.zeros(n)
    for i in range(n_individuals):
        s, e = group_starts[i], group_ends[i]
        V_max[s:e] = V[s:e].max()
    
    # Softmax probabilities
    exp_V_shifted = np.exp(V - V_max)
    
    # Sum exp(V) per individual
    sum_exp_V = np.zeros(n)
    for i in range(n_individuals):
        s, e = group_starts[i], group_ends[i]
        sum_exp_V[s:e] = exp_V_shifted[s:e].sum()
    
    P = exp_V_shifted / sum_exp_V  # Choice probabilities (n,)
    
    # Compute E[dV/dθ] for each individual (vectorized over all params)
    # E_dV[row, k] = sum over alternatives j in same group of P[j] * dV[j, k]
    # Use einsum: for each group, E_dV = P @ dV_dtheta
    
    E_dV = np.zeros((n, n_params), dtype=float)
    for i in range(n_individuals):
        s, e = group_starts[i], group_ends[i]
        # P[s:e] @ dV_dtheta[s:e, :] gives (n_params,) expected derivatives
        E_dV[s:e, :] = P[s:e] @ dV_dtheta[s:e, :]  # broadcast to all rows in group
    
    # Gradient: sum over observed alternatives of (dV_obs - E[dV])
    # is_obs is a boolean array
    obs_mask = is_obs.astype(bool)
    grad = (dV_dtheta[obs_mask, :] - E_dV[obs_mask, :]).sum(axis=0)
    
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    
    LOGGER.info("=" * 60)
    LOGGER.info("RURO Estimation for France")
    LOGGER.info("=" * 60)
    LOGGER.info(f"MNL file: {args.mnl_file}")
    LOGGER.info(f"Group: {args.group} ({'singles' if args.group == 1 else 'couples'})")
    if args.group == 1:
        LOGGER.info(f"Sex filter: {args.sex}")
    LOGGER.info(f"Wage spec: {args.wage_spec}")
    LOGGER.info("")
    
    # -------------------------------------------------------------------------
    # Load data
    # -------------------------------------------------------------------------
    if not args.mnl_file.exists():
        raise FileNotFoundError(f"MNL file not found: {args.mnl_file}")
    
    df = pd.read_parquet(args.mnl_file)
    LOGGER.info(f"Loaded {len(df)} rows from MNL dataset.")
    
    # -------------------------------------------------------------------------
    # Filter to requested group (ruro_group: 1=singles, 10=couples)
    # -------------------------------------------------------------------------
    if "ruro_group" in df.columns:
        df = df[df["ruro_group"] == args.group].copy()
        LOGGER.info(f"Filtered to ruro_group={args.group}: {len(df)} rows.")
    else:
        LOGGER.warning("No 'ruro_group' column found; using full dataset.")
    
    if len(df) == 0:
        raise ValueError(f"No data for group {args.group}.")
    
    # -------------------------------------------------------------------------
    # For singles, optionally filter by sex (dgn: 1=male, 0=female)
    # -------------------------------------------------------------------------
    is_male = True  # default for singles
    
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
            raise ValueError(f"No data for singles with sex={args.sex}.")
    else:
        # Couples
        is_male = True  # placeholder for couples
        LOGGER.info("Estimating couples (skeleton only).")
    
    # -------------------------------------------------------------------------
    # Initial parameters
    # -------------------------------------------------------------------------
    theta0 = get_initial_theta_singles(is_male=is_male)
    LOGGER.info(f"Number of parameters: {len(theta0)}")
    LOGGER.info(f"Initial theta: {theta0[:5]}... (truncated)")
    
    # -------------------------------------------------------------------------
    # Check initial log-likelihood
    # -------------------------------------------------------------------------
    ll0 = log_likelihood_singles(theta0, df, is_male=is_male, wage_spec=args.wage_spec)
    LOGGER.info(f"Initial log-likelihood: {ll0:.4f}")
    
    # -------------------------------------------------------------------------
    # Validate gradient (optional)
    # -------------------------------------------------------------------------
    if args.validate_gradient:
        LOGGER.info("")
        LOGGER.info("Validating analytical gradient against numerical gradient...")
        grad_analytical = analytical_gradient_singles(theta0, df, is_male=is_male, wage_spec=args.wage_spec)
        grad_numerical = numerical_gradient(
            lambda t: -log_likelihood_singles(t, df, is_male=is_male, wage_spec=args.wage_spec),
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
    # Optimization
    # -------------------------------------------------------------------------
    LOGGER.info("")
    LOGGER.info("Starting optimization...")
    LOGGER.info(f"Optimizer: {args.optimizer}")
    LOGGER.info("-" * 40)
    
    def objective(theta):
        return neg_log_likelihood_singles(theta, df, is_male=is_male, wage_spec=args.wage_spec)
    
    if args.optimizer == "L-BFGS-B":
        # Use analytical gradient with L-BFGS-B
        def objective_and_grad(theta):
            return neg_log_likelihood_with_grad_singles(theta, df, is_male=is_male, wage_spec=args.wage_spec)
        
        # Set up bounds for Box-Cox parameters (theta_l, theta_c should be bounded)
        bounds = [(None, None)] * len(theta0)
        bounds[9] = (0.01, 2.0)   # theta_l: avoid extreme values
        bounds[10] = (0.01, 2.0)  # theta_c: avoid extreme values
        if args.wage_spec == "vw":
            bounds[29] = (0.01, 2.0)  # sigma: must be positive
        
        result = minimize(
            objective_and_grad,
            theta0,
            method="L-BFGS-B",
            jac=True,  # objective_and_grad returns (f, grad)
            bounds=bounds,
            options={"disp": True, "maxiter": args.maxiter, "ftol": 1e-9, "gtol": 1e-5},
        )
    else:
        # Use BFGS with numerical gradient (original behavior)
        result = minimize(
            objective,
            theta0,
            method="BFGS",
            options={"disp": True, "maxiter": args.maxiter},
        )
    
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
    
    # Unpack and display estimated parameters
    pref, hopp, wopp = unpack_theta_singles(result.x)
      # Parameter names table (aligned with Stijn's structure)
    param_names = get_param_names_singles()
    
    LOGGER.info("=" * 70)
    LOGGER.info("ESTIMATED PARAMETERS")
    LOGGER.info("=" * 70)
    LOGGER.info(f"{'Index':<6} {'Name':<35} {'Value':>12}")
    LOGGER.info("-" * 55)
    for i, (name, val) in enumerate(zip(param_names, result.x)):
        # Only show wage params if wage_spec == "vw"
        if args.wage_spec == "fw" and i >= 21:
            continue
        LOGGER.info(f"{i:<6} {name:<35} {val:>12.4f}")
    LOGGER.info("")
    
    # Legacy display (for backwards compatibility)
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
        LOGGER.info("  Regional wage effects (vs Île-de-France baseline):")
        LOGGER.info(f"    reg2 (Bassin Parisien):   {wopp.beta_reg2:.4f}")
        LOGGER.info(f"    reg3 (Nord-Pas-de-Calais):{wopp.beta_reg3:.4f}")
        LOGGER.info(f"    reg4 (Est):               {wopp.beta_reg4:.4f}")
        LOGGER.info(f"    reg5 (Ouest):             {wopp.beta_reg5:.4f}")
        LOGGER.info(f"    reg6 (Sud-Ouest):         {wopp.beta_reg6:.4f}")
        LOGGER.info(f"    reg7 (Centre-Est):        {wopp.beta_reg7:.4f}")
        LOGGER.info(f"    reg8 (Méditerranée):      {wopp.beta_reg8:.4f}")
        LOGGER.info(f"    reg9 (DOM):               {wopp.beta_reg9:.4f}")
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
    
    LOGGER.info("=" * 60)
    LOGGER.info("Done.")


if __name__ == "__main__":
    main()
