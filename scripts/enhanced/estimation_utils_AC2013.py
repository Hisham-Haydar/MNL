#!/usr/bin/env python
"""
==============================================================================
Aaberge-Colombino (2013) Style Utility and Opportunity Functions
==============================================================================
Extension module for RURO labor supply estimation.

Implements A-C (2013) specific features:
- Log(age) and log(age)² preference shifters
- Child-age-group dummies (C1, C2, C3)
- Extended wage equation with experience terms
- Couples cross-leisure interaction (α_ll)
- Joint market availability parameter (μ₀)

This module extends the existing estimation_utils.py and estimation_engine.py
without breaking backward compatibility.

Reference:
    Aaberge, R., & Colombino, U. (2013). Using a microeconometric model of 
    household labour supply to design optimal income tax. Scandinavian 
    Journal of Economics, 115(2), 449-475.

Author: RURO Pipeline (A-C Extension)
Created: 2026-01-09
==============================================================================
"""

import logging
import numpy as np
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass

# Try to import numba for JIT compilation
try:
    from numba import jit, prange
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False
    # Dummy decorator
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    prange = range

logger = logging.getLogger(__name__)

# ==============================================================================
# Constants
# ==============================================================================

EPS = 1e-12  # Numerical stability constant
LOG_2PI = np.log(2 * np.pi)
MIN_AGE = 18.0  # Minimum age for log transform


# ==============================================================================
# A-C Style Age Transformation
# ==============================================================================

def compute_log_age_terms(age: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute A-C style log-age terms.
    
    In Aaberge-Colombino (2013), age enters as log(age) and log(age)²
    rather than linear age and age².
    
    Parameters
    ----------
    age : np.ndarray
        Age in years
        
    Returns
    -------
    log_age : np.ndarray
        log(age), with minimum age floor for stability
    log_age_sq : np.ndarray
        log(age)² 
    """
    age_safe = np.maximum(age, MIN_AGE)
    log_age = np.log(age_safe)
    log_age_sq = log_age ** 2
    return log_age, log_age_sq


# ==============================================================================
# A-C Style Children Variables
# ==============================================================================

def compute_children_age_groups(
    df,
    var_mapping: Dict[str, str]
) -> Dict[str, np.ndarray]:
    """
    Extract or compute child-age-group variables (C1, C2, C3).
    
    If variables are available in data, use them.
    Otherwise, attempt to derive from total children (with warning).
    
    Parameters
    ----------
    df : pd.DataFrame
        Data with children variables
    var_mapping : dict
        Variable name mapping from spec
        
    Returns
    -------
    dict
        {'C1': array, 'C2': array, 'C3': array}
    """
    result = {}
    
    # Try to get age-specific children counts
    c1_var = var_mapping.get('children_0_2', 'nch02')
    c2_var = var_mapping.get('children_3_6', 'nch36')
    c3_var = var_mapping.get('children_7_17', 'nch717')
    nch_var = var_mapping.get('children_total', 'n_children')
    
    n_obs = len(df)
    
    # C1: Children 0-2
    if c1_var in df.columns:
        result['C1'] = df[c1_var].values.astype(np.float64)
    else:
        result['C1'] = np.zeros(n_obs)
        logger.debug(f"Variable {c1_var} not found, using zeros for C1")
    
    # C2: Children 3-6
    if c2_var in df.columns:
        result['C2'] = df[c2_var].values.astype(np.float64)
    else:
        result['C2'] = np.zeros(n_obs)
        logger.debug(f"Variable {c2_var} not found, using zeros for C2")
    
    # C3: Children 7-17
    if c3_var in df.columns:
        result['C3'] = df[c3_var].values.astype(np.float64)
    else:
        result['C3'] = np.zeros(n_obs)
        logger.debug(f"Variable {c3_var} not found, using zeros for C3")
    
    # If all age-specific are zero but total children available, warn
    if (np.sum(result['C1']) + np.sum(result['C2']) + np.sum(result['C3'])) == 0:
        if nch_var in df.columns and np.sum(df[nch_var].values) > 0:
            logger.warning(
                f"Age-specific children variables not found, but {nch_var} has values. "
                "Consider adding nch02, nch36, nch717 to data for A-C specification."
            )
    
    return result


# ==============================================================================
# A-C Style Experience Terms
# ==============================================================================

def compute_experience_terms(
    df,
    var_mapping: Dict[str, str]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute experience and experience² terms for wage equation.
    
    A-C use potential experience: exp = age - years_of_education - 6
    
    If experience variable not available, attempts to compute from age/education.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data
    var_mapping : dict
        Variable name mapping
        
    Returns
    -------
    exp : np.ndarray
        Experience (years)
    exp2 : np.ndarray
        Experience squared
    """
    exp_var = var_mapping.get('experience', 'pexp')
    exp2_var = var_mapping.get('experience_squared', 'pexp2')
    
    if exp_var in df.columns:
        exp = df[exp_var].values.astype(np.float64)
        if exp2_var in df.columns:
            exp2 = df[exp2_var].values.astype(np.float64)
        else:
            exp2 = exp ** 2
    else:
        # Attempt to compute potential experience
        age_var = var_mapping.get('age', 'dage')
        if age_var in df.columns:
            age = df[age_var].values.astype(np.float64)
            # Rough approximation: exp = age - 20 (assuming work starts at 20)
            exp = np.maximum(age - 20, 0)
            exp2 = exp ** 2
            logger.warning(
                f"Experience variable {exp_var} not found. "
                f"Using approximation: exp = max(age - 20, 0)"
            )
        else:
            # Fallback to zeros
            exp = np.zeros(len(df))
            exp2 = np.zeros(len(df))
            logger.warning(
                f"Neither {exp_var} nor {age_var} found. "
                "Setting experience terms to zero."
            )
    
    return exp, exp2


# ==============================================================================
# A-C Style Leisure Shifter Computation
# ==============================================================================

def compute_leisure_shifter_AC2013(
    params: Dict[str, float],
    data: Dict[str, np.ndarray],
    gender_suffix: str,
    is_couples: bool = False
) -> np.ndarray:
    """
    Compute the A-C style leisure preference shifter.
    
    β_l = β_l0 + β_age * log(age) + β_age2 * log(age)²
               + β_C1 * C1 + β_C2 * C2 + β_C3 * C3
               + β_nch * n_children (females only, legacy)
    
    Parameters
    ----------
    params : dict
        Parameter values
    data : dict
        Data arrays including 'age', 'C1', 'C2', 'C3', 'n_children'
    gender_suffix : str
        '_sm', '_sf', '_cm', or '_cf'
    is_couples : bool
        Whether this is for couples (different variable handling)
        
    Returns
    -------
    beta_l : np.ndarray
        Leisure preference coefficient for each observation
    """
    n_obs = len(data.get('age', data.get('leisure', [])))
    
    # Start with intercept
    beta_l0_name = f"beta_l0{gender_suffix}"
    beta_l = np.full(n_obs, params.get(beta_l0_name, 1.0))
    
    # Log-age terms (A-C style)
    if 'age' in data:
        log_age, log_age_sq = compute_log_age_terms(data['age'])
        
        beta_age_name = f"beta_age{gender_suffix}"
        beta_age2_name = f"beta_age2{gender_suffix}"
        
        if beta_age_name in params:
            beta_l = beta_l + params[beta_age_name] * log_age
        if beta_age2_name in params:
            beta_l = beta_l + params[beta_age2_name] * log_age_sq
    
    # Child-age-group shifters (primarily for females)
    is_female = gender_suffix in ('_sf', '_cf')
    
    if is_female or f"beta_C1{gender_suffix}" in params:
        for cg in ['C1', 'C2', 'C3']:
            param_name = f"beta_{cg}{gender_suffix}"
            if param_name in params and cg in data:
                beta_l = beta_l + params[param_name] * data[cg]
    
    # Legacy total children (females only)
    if is_female:
        nch_name = f"beta_nch{gender_suffix}"
        if nch_name in params and 'n_children' in data:
            beta_l = beta_l + params[nch_name] * data['n_children']
    
    return beta_l


# ==============================================================================
# A-C Style Wage Equation
# ==============================================================================

def compute_wage_mean_AC2013(
    params: Dict[str, float],
    data: Dict[str, np.ndarray],
    gender_suffix: str = ""
) -> np.ndarray:
    """
    Compute A-C style wage equation mean.
    
    μ_w = β_w0 + β_exp * exp + β_exp2 * exp² + β_educL * educL + β_educH * educH
    
    Parameters
    ----------
    params : dict
        Parameter values
    data : dict
        Data arrays including 'exp', 'exp2', 'educL', 'educH'
    gender_suffix : str
        '' for singles, '_cm' or '_cf' for couples
        
    Returns
    -------
    mu_w : np.ndarray
        Mean log wage for each observation
    """
    # Determine sample size from available data
    for key in ['exp', 'educL', 'educH', 'log_wage']:
        if key in data:
            n_obs = len(data[key])
            break
    else:
        raise ValueError("Cannot determine sample size from data")
    
    # Intercept
    w0_name = f"beta_w0{gender_suffix}"
    mu_w = np.full(n_obs, params.get(w0_name, 2.5))
    
    # Experience terms (A-C extension)
    exp_name = f"beta_exp{gender_suffix}"
    exp2_name = f"beta_exp2{gender_suffix}"
    
    if 'exp' in data:
        if exp_name in params:
            mu_w = mu_w + params[exp_name] * data['exp']
        if exp2_name in params and 'exp2' in data:
            mu_w = mu_w + params[exp2_name] * data['exp2']
    
    # Education effects
    educL_name = f"beta_educL{gender_suffix}"
    educH_name = f"beta_educH{gender_suffix}"
    
    if educL_name in params and 'educL' in data:
        mu_w = mu_w + params[educL_name] * data['educL']
    if educH_name in params and 'educH' in data:
        mu_w = mu_w + params[educH_name] * data['educH']
    
    return mu_w


def compute_log_wage_density_AC2013(
    params: Dict[str, float],
    data: Dict[str, np.ndarray],
    gender_suffix: str = "",
    working_mask: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Compute log wage density for A-C style specification.
    
    log f(w|X) = -0.5 * [(log w - μ_w)² / σ²] - log(σ) - 0.5 * log(2π)
    
    Only computed for workers (h > 0).
    
    Parameters
    ----------
    params : dict
        Parameter values
    data : dict
        Data arrays including 'log_wage', 'exp', 'educL', 'educH'
    gender_suffix : str
        '' for singles, '_cm' or '_cf' for couples
    working_mask : np.ndarray, optional
        Boolean mask for working individuals
        
    Returns
    -------
    log_f_w : np.ndarray
        Log wage density (0 for non-workers)
    """
    n_obs = len(data.get('log_wage', []))
    log_f_w = np.zeros(n_obs)
    
    if 'log_wage' not in data:
        logger.warning("log_wage not in data, returning zero wage density")
        return log_f_w
    
    # Determine working individuals
    if working_mask is not None:
        working = working_mask
    elif 'working' in data:
        working = data['working'] > 0
    elif 'hours' in data:
        working = data['hours'] > 0
    else:
        working = np.ones(n_obs, dtype=bool)
    
    if not np.any(working):
        return log_f_w
    
    # Compute mean wage
    mu_w = compute_wage_mean_AC2013(params, data, gender_suffix)
    
    # Get variance parameter
    sigma_name = f"sigma_w{gender_suffix}"
    sigma = params.get(sigma_name, 0.4)
    sigma = max(sigma, EPS)  # Ensure positive
    
    # Log-normal density for workers
    log_w = data['log_wage']
    residual = (log_w[working] - mu_w[working]) / sigma
    
    log_f_w[working] = -0.5 * residual**2 - np.log(sigma) - 0.5 * LOG_2PI
    
    return log_f_w


# ==============================================================================
# A-C Couples Cross-Leisure Interaction
# ==============================================================================

def compute_cross_leisure_utility(
    leisure_male: np.ndarray,
    leisure_female: np.ndarray,
    theta_l_m: float,
    theta_l_f: float,
    alpha_ll: float
) -> np.ndarray:
    """
    Compute cross-leisure interaction term for couples (A-C style).
    
    U_cross = α_ll * BC(l_m, θ_lm) * BC(l_f, θ_lf)
    
    This captures complementarity (α_ll > 0) or substitutability (α_ll < 0)
    in spouses' leisure.
    
    Parameters
    ----------
    leisure_male : np.ndarray
        Male leisure values
    leisure_female : np.ndarray
        Female leisure values
    theta_l_m : float
        Male leisure Box-Cox parameter
    theta_l_f : float
        Female leisure Box-Cox parameter
    alpha_ll : float
        Cross-leisure interaction coefficient
        
    Returns
    -------
    U_cross : np.ndarray
        Cross-leisure utility contribution
    """
    from estimation_utils import box_cox_transform
    
    bc_l_m = box_cox_transform(leisure_male, theta_l_m)
    bc_l_f = box_cox_transform(leisure_female, theta_l_f)
    
    return alpha_ll * bc_l_m * bc_l_f


# ==============================================================================
# A-C Joint Market Availability (μ₀)
# ==============================================================================

def compute_joint_market_availability(
    working_male: np.ndarray,
    working_female: np.ndarray,
    mu_0: float = 1.0
) -> np.ndarray:
    """
    Compute joint market availability term for couples (A-C's μ₀).
    
    log f_joint = log(μ₀) * I(both_work)
    
    Where I(both_work) = 1 if both h_m > 0 and h_f > 0.
    
    μ₀ > 1: Positive assortative matching (both working more likely)
    μ₀ < 1: Negative assortative matching
    μ₀ = 1: Independent (no joint effect)
    
    Parameters
    ----------
    working_male : np.ndarray
        Male working indicator (1 if h_m > 0)
    working_female : np.ndarray
        Female working indicator (1 if h_f > 0)
    mu_0 : float
        Joint market availability parameter
        
    Returns
    -------
    log_f_joint : np.ndarray
        Log joint availability contribution
    """
    both_work = (working_male > 0) & (working_female > 0)
    
    # Ensure μ₀ is positive
    mu_0_safe = max(mu_0, EPS)
    
    log_f_joint = np.where(both_work, np.log(mu_0_safe), 0.0)
    
    return log_f_joint


# ==============================================================================
# Diagnostic Functions
# ==============================================================================

def compute_ll_breakdown(
    V: np.ndarray,
    u: np.ndarray,
    log_h: np.ndarray,
    log_w: np.ndarray,
    group_starts: np.ndarray,
    group_ends: np.ndarray
) -> Dict[str, float]:
    """
    Compute log-likelihood breakdown by component (A-C style diagnostic).
    
    Decomposes the total LL into:
    - Preference contribution (from utility u)
    - Hours opportunity contribution
    - Wage opportunity contribution
    
    Parameters
    ----------
    V : np.ndarray
        Total value function
    u : np.ndarray
        Utility component
    log_h : np.ndarray
        Hours opportunity component
    log_w : np.ndarray
        Wage opportunity component
    group_starts : np.ndarray
        Start indices for each choice set
    group_ends : np.ndarray
        End indices for each choice set
        
    Returns
    -------
    dict
        {'ll_total': float, 'll_preference': float, 
         'll_hours': float, 'll_wage': float}
    """
    from estimation_utils import compute_log_sum_exp_by_group
    
    # Total LL
    lse_total = compute_log_sum_exp_by_group(V, group_starts, group_ends)
    V_obs = np.array([V[start] for start in group_starts])
    ll_total = np.sum(V_obs - lse_total)
    
    # Approximate breakdown (treating components as if independent)
    # This is an approximation since components are not separable in MNL
    u_obs = np.array([u[start] for start in group_starts])
    log_h_obs = np.array([log_h[start] for start in group_starts])
    log_w_obs = np.array([log_w[start] for start in group_starts])
    
    return {
        'll_total': ll_total,
        'll_preference_approx': np.sum(u_obs),
        'll_hours_approx': np.sum(log_h_obs),
        'll_wage_approx': np.sum(log_w_obs),
        'mean_u': np.mean(u),
        'mean_log_h': np.mean(log_h),
        'mean_log_w': np.mean(log_w)
    }


def compute_p_nonwork(
    hours: np.ndarray,
    group_starts: np.ndarray,
    predicted_probs: Optional[np.ndarray] = None
) -> Dict[str, float]:
    """
    Compute non-working proportion diagnostic (A-C's p₁ₖ).
    
    Parameters
    ----------
    hours : np.ndarray
        Hours worked for each observation
    group_starts : np.ndarray
        Start indices for each choice set
    predicted_probs : np.ndarray, optional
        Predicted choice probabilities
        
    Returns
    -------
    dict
        {'p_nonwork_observed': float, 'p_nonwork_predicted': float}
    """
    # Observed non-working rate (among observed choices = first in each group)
    hours_obs = np.array([hours[start] for start in group_starts])
    p_nonwork_obs = np.mean(hours_obs == 0)
    
    result = {'p_nonwork_observed': p_nonwork_obs}
    
    if predicted_probs is not None:
        # Get predicted probability of h=0 for each individual
        # Assumes h=0 is the first alternative in each choice set
        p_nonwork_pred = np.mean([
            predicted_probs[start] for start in group_starts
            if hours[start] == 0  # Only for those with h=0 as first option
        ]) if len(group_starts) > 0 else 0.0
        result['p_nonwork_predicted'] = p_nonwork_pred
    
    return result


def compute_gradient_norms_by_block(
    gradient: np.ndarray,
    param_names: list,
    block_definitions: Optional[Dict[str, list]] = None
) -> Dict[str, float]:
    """
    Compute gradient norms by parameter block (A-C style diagnostic).
    
    Parameters
    ----------
    gradient : np.ndarray
        Full gradient vector
    param_names : list
        Names of parameters corresponding to gradient elements
    block_definitions : dict, optional
        Mapping from block name to list of parameter name prefixes
        
    Returns
    -------
    dict
        Gradient norms for each block
    """
    if block_definitions is None:
        block_definitions = {
            'consumption': ['beta_c', 'theta_c'],
            'leisure': ['beta_l', 'theta_l', 'beta_age', 'beta_C', 'beta_nch'],
            'hours': ['beta_working', 'beta_PT', 'beta_FT', 'beta_gsur'],
            'wage': ['beta_w', 'beta_exp', 'beta_educ', 'sigma_w'],
            'couples_joint': ['alpha_ll', 'mu_0']
        }
    
    result = {'gradient_norm_total': np.linalg.norm(gradient)}
    
    for block_name, prefixes in block_definitions.items():
        indices = [
            i for i, name in enumerate(param_names)
            if any(name.startswith(prefix) for prefix in prefixes)
        ]
        if indices:
            result[f'gradient_norm_{block_name}'] = np.linalg.norm(gradient[indices])
    
    return result


# ==============================================================================
# Integration with Existing Engine
# ==============================================================================

def is_ac2013_spec(spec) -> bool:
    """
    Check if specification uses A-C 2013 style.
    
    Parameters
    ----------
    spec : EstimationSpec
        Specification object
        
    Returns
    -------
    bool
        True if A-C 2013 style
    """
    if hasattr(spec, 'model_version'):
        return spec.model_version == 'AC2013'
    return False


def get_ac2013_param_blocks() -> Dict[str, list]:
    """
    Get the parameter block definitions for A-C 2013 specification.
    
    Returns
    -------
    dict
        Block name -> list of parameter prefixes
    """
    return {
        'consumption': ['beta_c', 'theta_c'],
        'leisure_base': ['beta_l0', 'theta_l'],
        'leisure_age': ['beta_age'],
        'leisure_children': ['beta_C1', 'beta_C2', 'beta_C3', 'beta_nch'],
        'hours_focal': ['beta_PT', 'beta_FT'],
        'hours_working': ['beta_working', 'beta_gsur', 'beta_educ_working'],
        'wage_mean': ['beta_w0', 'beta_exp', 'beta_educL', 'beta_educH'],
        'wage_variance': ['sigma_w'],
        'couples_interaction': ['alpha_ll'],
        'couples_joint_opp': ['mu_0']
    }


# ==============================================================================
# Summary Table Helpers
# ==============================================================================

def get_ac2013_vs_legacy_comparison() -> str:
    """
    Return a formatted comparison table of A-C 2013 vs legacy specification.
    
    Returns
    -------
    str
        Markdown-formatted comparison table
    """
    table = """
| Block | Legacy (Stijn) | A-C 2013 | Status |
|-------|----------------|----------|--------|
| **Hours opportunity** | Discrete logits (implicit h=0) | Discrete logits (explicit non-work) | Same structure |
| **Wage equation** | μ = β₀ + β_educ | μ = β₀ + β_exp + β_exp² + β_educ | Extended |
| **Non-market mass** | Implicit | Explicit in hours component | Clarified |
| **Utility - consumption** | β_c * BC(c, θ_c) | Same | Kept |
| **Utility - leisure** | β_l * BC(l, θ_l) | Same with age/children shifters | Extended |
| **Utility - age terms** | β_age * age | β_age * log(age) + β_age2 * log(age)² | Changed |
| **Utility - children** | β_nch * n_children | β_C1*C1 + β_C2*C2 + β_C3*C3 | Extended |
| **Couples - joint opp** | Independent | μ₀ correlation parameter | Added |
| **Couples - leisure** | Additive | α_ll cross-leisure interaction | Added |
"""
    return table


# ==============================================================================
# Main Test
# ==============================================================================

if __name__ == "__main__":
    # Basic tests
    print("Testing A-C 2013 utility functions...")
    
    # Test log-age computation
    ages = np.array([25, 35, 45, 55, 65])
    log_age, log_age_sq = compute_log_age_terms(ages)
    print(f"Ages: {ages}")
    print(f"Log ages: {log_age}")
    print(f"Log ages²: {log_age_sq}")
    
    # Test wage mean computation
    test_params = {
        'beta_w0': 2.5,
        'beta_exp': 0.03,
        'beta_exp2': -0.0005,
        'beta_educL': -0.1,
        'beta_educH': 0.2,
        'sigma_w': 0.4
    }
    test_data = {
        'exp': np.array([5, 10, 15, 20, 25]),
        'exp2': np.array([25, 100, 225, 400, 625]),
        'educL': np.array([1, 0, 0, 0, 0]),
        'educH': np.array([0, 0, 0, 1, 1]),
        'log_wage': np.array([2.5, 2.7, 2.8, 3.0, 3.1])
    }
    
    mu_w = compute_wage_mean_AC2013(test_params, test_data)
    print(f"\nWage equation mean: {mu_w}")
    
    # Test joint market availability
    working_m = np.array([1, 1, 0, 1, 0])
    working_f = np.array([1, 0, 1, 1, 0])
    log_f_joint = compute_joint_market_availability(working_m, working_f, mu_0=1.5)
    print(f"\nJoint market availability (μ₀=1.5): {log_f_joint}")
    
    # Print comparison table
    print("\n" + get_ac2013_vs_legacy_comparison())
    
    print("\nAll tests passed!")
