"""
==============================================================================
Occupation Choice Utilities and Opportunities
==============================================================================
Modular extension for occupation choice in RURO MNL estimation.

This module provides occupation-specific:
- Utility computations (preferences and leisure shifters)
- Wage opportunity densities (occupation-specific Mincer equations)
- Hours opportunity densities (occupation-specific clustering)
- Occupation availability (multinomial logit)

Design principles:
- Country/year/specification agnostic
- Only activated when spec.occupation_choice == True
- Works with any occupation coding (loc4_1/2/3/4, isco, etc.)
- Compatible with existing estimation engine

Author: Enhanced RURO Pipeline
Created: 2026-01-27
==============================================================================
"""

import logging
from typing import Dict, List, Optional

import numpy as np

from estimation_spec_parser import EstimationSpec


def add_occupation_preferences_to_utility(
    u: np.ndarray,
    params: Dict[str, float],
    spec: EstimationSpec,
    occupation_dummies: Dict[str, np.ndarray],
    demographic_vars: Dict[str, np.ndarray],
    gender_suffix: str
) -> np.ndarray:
    """
    Add occupation preferences and interactions to utility.

    Adds to utility:
    1. Direct occupation preferences: α_occ
    2. Occupation-demographic interactions: α_occ_var * occupation * demographic

    This is ADDITIVE to existing utility, so it preserves all other utility components.

    Parameters
    ----------
    u : np.ndarray, shape (n_obs,)
        Base utility (from consumption + leisure)
    params : dict
        Parameter dictionary
    spec : EstimationSpec
        Specification with occupation_preferences list
    occupation_dummies : dict
        Dictionary mapping occupation names (e.g., 'loc4_2') to dummy arrays
    demographic_vars : dict
        Dictionary of demographic variables (e.g., 'education_high', 'age')
    gender_suffix : str
        Gender suffix for parameters (_sm, _sf, _m, _f)

    Returns
    -------
    np.ndarray, shape (n_obs,)
        Utility with occupation preferences added

    Notes
    -----
    - Reference occupation (first in list) has preference = 0
    - Works with any occupation coding system specified in YAML
    - Completely agnostic to country/year/normalization
    """
    if not spec.occupation_choice or not spec.occupation_preferences:
        return u

    u_with_occ = u.copy()

    for occ_pref in spec.occupation_preferences:
        occ_var = occ_pref["occupation"]  # e.g., "loc4_2"

        # Check if this occupation is in the data
        if occ_var not in occupation_dummies:
            logging.warning(f"Occupation {occ_var} not found in data, skipping")
            continue

        occ_dummy = occupation_dummies[occ_var]

        # Add direct occupation preference
        alpha_occ_name = f"{occ_pref['coefficient']}{gender_suffix}"
        if alpha_occ_name in params:
            u_with_occ = u_with_occ + params[alpha_occ_name] * occ_dummy

        # Add occupation-demographic interactions
        if "interactions" in occ_pref:
            for interaction in occ_pref["interactions"]:
                var_name = interaction["variable"]
                coef_name = f"{interaction['coefficient']}{gender_suffix}"

                if var_name in demographic_vars and coef_name in params:
                    # α_occ_var * occupation * demographic
                    interaction_term = occ_dummy * demographic_vars[var_name]
                    u_with_occ = u_with_occ + params[coef_name] * interaction_term
                else:
                    if var_name not in demographic_vars:
                        logging.warning(f"Demographic variable {var_name} not found in data")

    return u_with_occ


def compute_occupation_specific_wage_density(
    log_wage: np.ndarray,
    occupation_dummies: Dict[str, np.ndarray],
    experience: Optional[np.ndarray],
    education: Optional[np.ndarray],
    working: np.ndarray,
    params: Dict[str, float],
    spec: EstimationSpec,
    gender_suffix: str
) -> np.ndarray:
    """
    Compute occupation-specific wage opportunity density.

    For each occupation occ:
        log w ~ N(μ_occ(X), σ_occ²)
        μ_occ(X) = β0_occ + β_exp_occ * (exp/10) + β_exp2_occ * (exp/10)² + β_ed_occ * ed

    Total density:
        log w(w|X, occ) = Σ_occ 1{occ} * log N(log w; μ_occ, σ_occ²)

    Parameters
    ----------
    log_wage : np.ndarray, shape (n_obs,)
        Log hourly wage
    occupation_dummies : dict
        Dictionary mapping occupation names to dummy arrays
    experience : np.ndarray or None, shape (n_obs,)
        Years of experience (can be None if not in spec)
    education : np.ndarray or None, shape (n_obs,)
        Education level (can be None if not in spec)
    working : np.ndarray, shape (n_obs,)
        Working indicator (1 if hours > 0)
    params : dict
        Parameter dictionary
    spec : EstimationSpec
        Specification with occupation_wage_configs
    gender_suffix : str
        Gender suffix for parameters (_sm, _sf)

    Returns
    -------
    np.ndarray, shape (n_obs,)
        Log wage opportunity density (zero for non-workers)

    Notes
    -----
    - Returns zero for non-workers (hours == 0)
    - Experience is scaled by 10 (decades)
    - Works with any occupation coding system
    - Gracefully handles missing variables (logs warning)
    """
    if not spec.occupation_specific_wages or not spec.occupation_wage_configs:
        raise ValueError("Occupation-specific wages not configured in specification")

    n_obs = len(log_wage)
    log_w = np.zeros(n_obs)

    for occ_config in spec.occupation_wage_configs:
        occ_var = occ_config["occupation"]  # e.g., "loc4_1"

        # Check if this occupation is in the data
        if occ_var not in occupation_dummies:
            logging.warning(f"Occupation {occ_var} not found in data, skipping")
            continue

        occ_indicator = occupation_dummies[occ_var]

        # Get parameter names with gender suffix
        beta_0_name = f"{occ_config['intercept']}{gender_suffix}"
        beta_exp_name = f"{occ_config['experience']}{gender_suffix}"
        beta_exp2_name = f"{occ_config['experience_squared']}{gender_suffix}"
        beta_ed_name = f"{occ_config['education']}{gender_suffix}"
        sigma_name = f"{occ_config['variance']}{gender_suffix}"

        # Check if parameters exist
        if not all(p in params for p in [beta_0_name, sigma_name]):
            logging.warning(f"Parameters for {occ_var} not found, skipping")
            continue

        # Compute mean log-wage for this occupation
        mu_occ = params[beta_0_name] + np.zeros(n_obs)

        # Add experience terms (if available)
        if experience is not None and beta_exp_name in params:
            exp_scaled = experience / 10.0  # Scale to decades
            mu_occ = mu_occ + params[beta_exp_name] * exp_scaled

            if beta_exp2_name in params:
                mu_occ = mu_occ + params[beta_exp2_name] * (exp_scaled ** 2)

        # Add education term (if available)
        if education is not None and beta_ed_name in params:
            mu_occ = mu_occ + params[beta_ed_name] * education

        # Compute log-normal density for this occupation
        sigma_occ = params[sigma_name]
        residual = (log_wage - mu_occ) / sigma_occ
        log_density_occ = -0.5 * residual**2 - np.log(sigma_occ) - 0.5 * np.log(2 * np.pi)

        # Add this occupation's contribution (weighted by occupation indicator)
        log_w = log_w + occ_indicator * log_density_occ

    # Zero for non-workers
    log_w = np.where(working > 0, log_w, 0.0)

    return log_w


def compute_occupation_specific_hours_density(
    hours: np.ndarray,
    occupation_dummies: Dict[str, np.ndarray],
    working: np.ndarray,
    params: Dict[str, float],
    spec: EstimationSpec
) -> np.ndarray:
    """
    Compute occupation-specific hours opportunity density.

    For each occupation, hours have different clustering at part-time and full-time:
        g1_occ(h) = γ_occ * exp(π_pt_occ * 1{h in PT range})
                           * exp(π_ft_occ * 1{h in FT range})

    Where:
    - PT range: (910, 1066] hours/year (18-20 hrs/week)
    - FT range: (1898, 2106] hours/year (37-40 hrs/week)

    Parameters
    ----------
    hours : np.ndarray, shape (n_obs,)
        Annual hours
    occupation_dummies : dict
        Dictionary mapping occupation names to dummy arrays
    working : np.ndarray, shape (n_obs,)
        Working indicator
    params : dict
        Parameter dictionary
    spec : EstimationSpec
        Specification with occupation_hour_configs

    Returns
    -------
    np.ndarray, shape (n_obs,)
        Log hours opportunity density contribution from occupation-specific clustering

    Notes
    -----
    - Returns additional contribution to log density (additive to base hours density)
    - Only applies to workers (hours > 0)
    - Hour ranges are hardcoded but parameters are flexible
    - Works with any occupation coding
    """
    if not spec.occupation_specific_hours or not spec.occupation_hour_configs:
        return np.zeros(len(hours))  # No occupation-specific hours

    log_h_occ = np.zeros(len(hours))

    # Define hour ranges (these are universal constants)
    PT_LOW, PT_HIGH = 910, 1066    # Part-time peak
    FT_LOW, FT_HIGH = 1898, 2106   # Full-time peak

    # Create indicators for hour ranges
    in_pt_range = (hours > PT_LOW) & (hours <= PT_HIGH)
    in_ft_range = (hours > FT_LOW) & (hours <= FT_HIGH)

    for occ_config in spec.occupation_hour_configs:
        occ_var = occ_config["occupation"]  # e.g., "loc4_1"

        # Check if this occupation is in the data
        if occ_var not in occupation_dummies:
            logging.warning(f"Occupation {occ_var} not found in data, skipping")
            continue

        occ_indicator = occupation_dummies[occ_var]

        # Get clustering parameters
        pi_pt_name = occ_config["part_time_peak"]
        pi_ft_name = occ_config["full_time_peak"]

        if pi_pt_name not in params or pi_ft_name not in params:
            logging.warning(f"Hour clustering parameters for {occ_var} not found, skipping")
            continue

        pi_pt = params[pi_pt_name]
        pi_ft = params[pi_ft_name]

        # Add occupation-specific clustering
        # log density += occupation_dummy * (π_pt * 1{PT} + π_ft * 1{FT})
        clustering_contribution = (
            pi_pt * in_pt_range.astype(float) +
            pi_ft * in_ft_range.astype(float)
        )

        log_h_occ = log_h_occ + occ_indicator * clustering_contribution

    # Only apply to workers
    log_h_occ = np.where(working > 0, log_h_occ, 0.0)

    return log_h_occ


def compute_occupation_availability(
    occupation_dummies: Dict[str, np.ndarray],
    params: Dict[str, float],
    spec: EstimationSpec,
    gender_suffix: str
) -> np.ndarray:
    """
    Compute occupation availability g3(occ).

    Multinomial logit form:
        g3(occ) = exp(μ_occ) / Σ_k exp(μ_k)

    Where μ for reference occupation = 0.

    Parameters
    ----------
    occupation_dummies : dict
        Dictionary mapping occupation names to dummy arrays
    params : dict
        Parameter dictionary
    spec : EstimationSpec
        Specification with occupation_availability list
    gender_suffix : str
        Gender suffix for parameters (_sm, _sf)

    Returns
    -------
    np.ndarray, shape (n_obs,)
        Log occupation availability density

    Notes
    -----
    - Reference occupation (parameter = None) has μ = 0
    - Returns log probability
    - Gender-specific availability (singles only)
    """
    if not spec.occupation_choice or not spec.occupation_availability:
        return np.zeros(len(next(iter(occupation_dummies.values()))))

    n_obs = len(next(iter(occupation_dummies.values())))

    # Collect all μ values for softmax
    mu_values = []
    occupations = []

    for occ_avail in spec.occupation_availability:
        occ_var = occ_avail["occupation"]
        param_name = occ_avail.get("parameter")

        if occ_var not in occupation_dummies:
            logging.warning(f"Occupation {occ_var} not found in data")
            continue

        occupations.append(occ_var)

        if param_name is None:
            # Reference category
            mu_values.append(0.0)
        else:
            # Get parameter value
            mu_name = f"{param_name}{gender_suffix}"
            if mu_name in params:
                mu_values.append(params[mu_name])
            else:
                logging.warning(f"Availability parameter {mu_name} not found")
                mu_values.append(0.0)

    # Compute softmax probabilities
    mu_array = np.array(mu_values)
    max_mu = np.max(mu_array)
    exp_mu = np.exp(mu_array - max_mu)  # Numerical stability
    sum_exp_mu = np.sum(exp_mu)

    # Compute log probability for each individual's occupation
    log_g3 = np.zeros(n_obs)

    for i, occ_var in enumerate(occupations):
        occ_indicator = occupation_dummies[occ_var]
        log_prob_occ = mu_array[i] - max_mu - np.log(sum_exp_mu)
        log_g3 = log_g3 + occ_indicator * log_prob_occ

    return log_g3


def extract_occupation_dummies_from_data(
    data,
    spec: EstimationSpec
) -> Dict[str, np.ndarray]:
    """
    Extract occupation dummy variables from precomputed data.

    Looks for occupation variables specified in the specification and extracts
    them as a dictionary for easy access.

    Parameters
    ----------
    data : PrecomputedDataSingles or PrecomputedDataCouples
        Precomputed data object
    spec : EstimationSpec
        Specification with occupation configurations

    Returns
    -------
    dict
        Dictionary mapping occupation variable names to arrays

    Notes
    -----
    - Agnostic to occupation coding system (loc4, isco, etc.)
    - Occupation variables must be present in data as dummy variables
    - Logs warning for missing occupations
    """
    if not spec.occupation_choice:
        return {}

    occupation_dummies = {}

    # Collect all occupation variables from different configs
    occ_vars = set()

    if spec.occupation_preferences:
        for occ_pref in spec.occupation_preferences:
            occ_vars.add(occ_pref["occupation"])

    if spec.occupation_wage_configs:
        for occ_cfg in spec.occupation_wage_configs:
            occ_vars.add(occ_cfg["occupation"])

    if spec.occupation_hour_configs:
        for occ_cfg in spec.occupation_hour_configs:
            occ_vars.add(occ_cfg["occupation"])

    if spec.occupation_availability:
        for occ_avail in spec.occupation_availability:
            occ_vars.add(occ_avail["occupation"])

    # Extract from data
    for occ_var in occ_vars:
        if hasattr(data, occ_var):
            occupation_dummies[occ_var] = getattr(data, occ_var)
        else:
            logging.warning(f"Occupation variable {occ_var} not found in data")

    return occupation_dummies


def extract_demographic_vars_from_data(
    data,
    spec: EstimationSpec
) -> Dict[str, np.ndarray]:
    """
    Extract demographic variables used in occupation interactions.

    Parameters
    ----------
    data : PrecomputedDataSingles or PrecomputedDataCouples
        Precomputed data object
    spec : EstimationSpec
        Specification with occupation_preferences

    Returns
    -------
    dict
        Dictionary mapping variable names to arrays

    Notes
    -----
    - Extracts variables mentioned in occupation-demographic interactions
    - Agnostic to normalization and scaling
    - Logs warning for missing variables
    """
    if not spec.occupation_choice or not spec.occupation_preferences:
        return {}

    demographic_vars = {}

    # Collect all demographic variables from interactions
    for occ_pref in spec.occupation_preferences:
        if "interactions" in occ_pref:
            for interaction in occ_pref["interactions"]:
                var_name = interaction["variable"]

                if hasattr(data, var_name):
                    demographic_vars[var_name] = getattr(data, var_name)
                else:
                    logging.warning(f"Demographic variable {var_name} not found in data")

    return demographic_vars


# ==============================================================================
# End of occupation_choice_utils.py
# ==============================================================================
