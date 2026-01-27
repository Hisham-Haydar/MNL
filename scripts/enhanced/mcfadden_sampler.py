"""
==============================================================================
McFadden Sampler for Occupation Choice
==============================================================================
Implements occupation-stratified sampling for expanding choice sets during
estimation, following McFadden (1978).

For each individual, samples alternatives from occupation-specific (hours, wage)
distributions to create a choice set of 400 alternatives (100 per occupation).

Author: Enhanced RURO Pipeline
Created: 2026-01-27
==============================================================================
"""

import logging
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


def sample_occupation_alternatives(
    individual_data: pd.Series,
    spec: 'EstimationSpec',
    n_per_occ: int = 100,
    random_state: np.random.RandomState = None
) -> pd.DataFrame:
    """
    Sample alternatives from occupation-specific distributions.

    Creates a choice set of n_per_occ * 4 alternatives (one per occupation).
    Each alternative is sampled from:
    - Occupation-specific hours distribution g1_occ(h)
    - Occupation-specific wage distribution g2_occ(w | experience, education)

    Parameters
    ----------
    individual_data : pd.Series
        Individual characteristics with fields:
        - experience: years of experience
        - education: education level
        - gender: 'male' or 'female'
        - observed_hours: actual hours worked
        - observed_wage: actual hourly wage
        - observed_occupation: loc4_1, loc4_2, loc4_3, or loc4_4
    spec : EstimationSpec
        Parsed specification with occupation configurations
    n_per_occ : int
        Number of alternatives to sample per occupation (default: 100)
    random_state : np.random.RandomState
        Random state for reproducibility

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - hours: sampled hours
        - wage: sampled wage
        - loc4_1: occupation dummy (Managers)
        - loc4_2: occupation dummy (Professionals)
        - loc4_3: occupation dummy (Technicians)
        - loc4_4: occupation dummy (Service)
        - is_observed: True for the observed alternative
    """
    if random_state is None:
        random_state = np.random.RandomState()

    occupations = ['loc4_1', 'loc4_2', 'loc4_3', 'loc4_4']
    alternatives = []

    # Determine gender suffix for parameter lookup
    gender_suffix = '_sm' if individual_data['gender'] == 'male' else '_sf'

    for occ in occupations:
        # Sample hours from occupation-specific distribution
        hours = sample_hours_for_occupation(
            occupation=occ,
            n_samples=n_per_occ,
            spec=spec,
            random_state=random_state
        )

        # Sample wages from occupation-specific Mincer equation
        wages = sample_wages_for_occupation(
            occupation=occ,
            experience=individual_data['experience'],
            education=individual_data['education'],
            gender_suffix=gender_suffix,
            n_samples=n_per_occ,
            spec=spec,
            random_state=random_state
        )

        # Create occupation dummies
        occ_dummies = {o: (1 if o == occ else 0) for o in occupations}

        # Build alternatives dataframe
        occ_alternatives = pd.DataFrame({
            'hours': hours,
            'wage': wages,
            **occ_dummies,
            'is_observed': False
        })

        alternatives.append(occ_alternatives)

    # Concatenate all alternatives
    all_alternatives = pd.concat(alternatives, ignore_index=True)

    # Replace one alternative with the observed choice
    # Find the alternative in the observed occupation that is closest to observed (h, w)
    obs_occ = individual_data['observed_occupation']
    obs_mask = all_alternatives[obs_occ] == 1
    obs_alternatives = all_alternatives[obs_mask].copy()

    # Compute distance to observed point
    obs_h = individual_data['observed_hours']
    obs_w = individual_data['observed_wage']
    distances = np.sqrt(
        ((obs_alternatives['hours'] - obs_h) / obs_h) ** 2 +
        ((obs_alternatives['wage'] - obs_w) / obs_w) ** 2
    )

    # Replace the closest alternative with the exact observed choice
    closest_idx = obs_alternatives.index[distances.argmin()]
    all_alternatives.loc[closest_idx, 'hours'] = obs_h
    all_alternatives.loc[closest_idx, 'wage'] = obs_w
    all_alternatives.loc[closest_idx, 'is_observed'] = True

    return all_alternatives


def sample_hours_for_occupation(
    occupation: str,
    n_samples: int,
    spec: 'EstimationSpec',
    random_state: np.random.RandomState
) -> np.ndarray:
    """
    Sample hours from occupation-specific distribution.

    The distribution has peaks at part-time (18-20 hrs/week) and full-time
    (37-40 hrs/week) with occupation-specific clustering parameters.

    Distribution:
    g1_occ(h) = γ_occ                          if h in [52, 910]
              = γ_occ * exp(π_pt_occ * s_pt)   if h in (910, 1066]   (part-time peak)
              = γ_occ                          if h in (1066, 1898]
              = γ_occ * exp(π_ft_occ * s_ft)   if h in (1898, 2106]  (full-time peak)
              = γ_occ                          if h in (2106, 3640]

    Parameters
    ----------
    occupation : str
        Occupation code (loc4_1, loc4_2, loc4_3, loc4_4)
    n_samples : int
        Number of hours to sample
    spec : EstimationSpec
        Parsed specification
    random_state : np.random.RandomState
        Random state

    Returns
    -------
    np.ndarray
        Sampled hours (annual)
    """
    # Map occupation to parameter suffix
    occ_map = {
        'loc4_1': 'mgr',
        'loc4_2': 'prof',
        'loc4_3': 'tech',
        'loc4_4': 'service'
    }
    occ_suffix = occ_map[occupation]

    # Get clustering parameters from spec initial values
    pi_pt = spec.initial_values.get(f'pi_pt_{occ_suffix}', 1.0)
    pi_ft = spec.initial_values.get(f'pi_ft_{occ_suffix}', 1.5)

    # Define hour ranges and their weights
    ranges = [
        (52, 910, 1.0),           # Low hours
        (911, 1066, np.exp(pi_pt)),  # Part-time peak (18-20 hrs/week)
        (1067, 1898, 1.0),        # Medium hours
        (1899, 2106, np.exp(pi_ft)), # Full-time peak (37-40 hrs/week)
        (2107, 3640, 1.0)         # High hours
    ]

    # Compute total mass for each range
    range_masses = []
    for low, high, weight in ranges:
        mass = (high - low + 1) * weight
        range_masses.append(mass)

    total_mass = sum(range_masses)
    range_probs = [m / total_mass for m in range_masses]

    # Sample which range each observation comes from
    range_indices = random_state.choice(
        len(ranges),
        size=n_samples,
        p=range_probs
    )

    # Sample hours within each range
    hours = np.zeros(n_samples)
    for i, (low, high, weight) in enumerate(ranges):
        mask = range_indices == i
        n_in_range = mask.sum()
        if n_in_range > 0:
            hours[mask] = random_state.randint(low, high + 1, size=n_in_range)

    return hours


def sample_wages_for_occupation(
    occupation: str,
    experience: float,
    education: float,
    gender_suffix: str,
    n_samples: int,
    spec: 'EstimationSpec',
    random_state: np.random.RandomState
) -> np.ndarray:
    """
    Sample wages from occupation-specific Mincer equation.

    Log-wage equation:
    log(w) = β0_occ + β_exp_occ * exp + β_exp2_occ * exp² + β_ed_occ * ed + σ_occ * ε

    where ε ~ N(0, 1)

    Parameters
    ----------
    occupation : str
        Occupation code (loc4_1, loc4_2, loc4_3, loc4_4)
    experience : float
        Years of experience
    education : float
        Education level
    gender_suffix : str
        Gender suffix (_sm or _sf)
    n_samples : int
        Number of wages to sample
    spec : EstimationSpec
        Parsed specification
    random_state : np.random.RandomState
        Random state

    Returns
    -------
    np.ndarray
        Sampled hourly wages
    """
    # Map occupation to parameter suffix
    occ_map = {
        'loc4_1': 'mgr',
        'loc4_2': 'prof',
        'loc4_3': 'tech',
        'loc4_4': 'service'
    }
    occ_suffix = occ_map[occupation]

    # Get wage equation parameters from spec
    beta_0 = spec.initial_values.get(f'beta_w0_{occ_suffix}{gender_suffix}', 3.0)
    beta_exp = spec.initial_values.get(f'beta_w_exp_{occ_suffix}{gender_suffix}', 2.5)
    beta_exp2 = spec.initial_values.get(f'beta_w_exp2_{occ_suffix}{gender_suffix}', -4.0)
    beta_ed = spec.initial_values.get(f'beta_w_ed_{occ_suffix}{gender_suffix}', 4.5)
    sigma = spec.initial_values.get(f'sigma_{occ_suffix}{gender_suffix}', 0.3)

    # Compute mean log-wage
    exp_scaled = experience / 10.0  # Scale to decades
    log_wage_mean = (
        beta_0 +
        beta_exp * exp_scaled +
        beta_exp2 * (exp_scaled ** 2) +
        beta_ed * education
    )

    # Sample log-wages
    log_wages = log_wage_mean + sigma * random_state.randn(n_samples)

    # Transform to wages
    wages = np.exp(log_wages)

    return wages


def compute_opportunity_density(
    alternative: pd.Series,
    individual_data: pd.Series,
    spec: 'EstimationSpec'
) -> float:
    """
    Compute opportunity density p(h, w, occ) for an alternative.

    Following Aaberge & Colombino (2011):
    p(h, w, occ) = p1k * g1_occ(h) * g2_occ(w) * g3(occ)

    where:
    - p1k = market opportunity proportion (assumed constant for all)
    - g1_occ(h) = occupation-specific hours density
    - g2_occ(w) = occupation-specific wage density
    - g3(occ) = occupation availability

    Parameters
    ----------
    alternative : pd.Series
        Alternative with fields: hours, wage, loc4_1, loc4_2, loc4_3, loc4_4
    individual_data : pd.Series
        Individual characteristics
    spec : EstimationSpec
        Parsed specification

    Returns
    -------
    float
        Opportunity density
    """
    # Identify occupation
    occ = None
    for o in ['loc4_1', 'loc4_2', 'loc4_3', 'loc4_4']:
        if alternative[o] == 1:
            occ = o
            break

    if occ is None:
        raise ValueError("Alternative must have exactly one occupation dummy = 1")

    # Compute hours density
    g_h = compute_hours_density(
        hours=alternative['hours'],
        occupation=occ,
        spec=spec
    )

    # Compute wage density
    g_w = compute_wage_density(
        wage=alternative['wage'],
        occupation=occ,
        experience=individual_data['experience'],
        education=individual_data['education'],
        gender_suffix='_sm' if individual_data['gender'] == 'male' else '_sf',
        spec=spec
    )

    # Compute occupation availability
    g_occ = compute_occupation_availability(
        occupation=occ,
        gender_suffix='_sm' if individual_data['gender'] == 'male' else '_sf',
        spec=spec
    )

    # Market proportion (assumed constant)
    p1k = 1.0

    return p1k * g_h * g_w * g_occ


def compute_hours_density(
    hours: float,
    occupation: str,
    spec: 'EstimationSpec'
) -> float:
    """
    Compute occupation-specific hours density g1_occ(h).

    Parameters
    ----------
    hours : float
        Annual hours
    occupation : str
        Occupation code
    spec : EstimationSpec
        Parsed specification

    Returns
    -------
    float
        Hours density
    """
    # Map occupation to parameter suffix
    occ_map = {
        'loc4_1': 'mgr',
        'loc4_2': 'prof',
        'loc4_3': 'tech',
        'loc4_4': 'service'
    }
    occ_suffix = occ_map[occupation]

    # Get clustering parameters
    pi_pt = spec.initial_values.get(f'pi_pt_{occ_suffix}', 1.0)
    pi_ft = spec.initial_values.get(f'pi_ft_{occ_suffix}', 1.5)

    # Base density
    gamma = 1.0

    # Check which range hours falls into
    if 52 <= hours <= 910:
        density = gamma
    elif 911 <= hours <= 1066:
        density = gamma * np.exp(pi_pt)
    elif 1067 <= hours <= 1898:
        density = gamma
    elif 1899 <= hours <= 2106:
        density = gamma * np.exp(pi_ft)
    elif 2107 <= hours <= 3640:
        density = gamma
    else:
        density = 0.0

    return density


def compute_wage_density(
    wage: float,
    occupation: str,
    experience: float,
    education: float,
    gender_suffix: str,
    spec: 'EstimationSpec'
) -> float:
    """
    Compute occupation-specific wage density g2_occ(w).

    Log-normal density from Mincer equation.

    Parameters
    ----------
    wage : float
        Hourly wage
    occupation : str
        Occupation code
    experience : float
        Years of experience
    education : float
        Education level
    gender_suffix : str
        Gender suffix (_sm or _sf)
    spec : EstimationSpec
        Parsed specification

    Returns
    -------
    float
        Wage density
    """
    # Map occupation to parameter suffix
    occ_map = {
        'loc4_1': 'mgr',
        'loc4_2': 'prof',
        'loc4_3': 'tech',
        'loc4_4': 'service'
    }
    occ_suffix = occ_map[occupation]

    # Get wage equation parameters
    beta_0 = spec.initial_values.get(f'beta_w0_{occ_suffix}{gender_suffix}', 3.0)
    beta_exp = spec.initial_values.get(f'beta_w_exp_{occ_suffix}{gender_suffix}', 2.5)
    beta_exp2 = spec.initial_values.get(f'beta_w_exp2_{occ_suffix}{gender_suffix}', -4.0)
    beta_ed = spec.initial_values.get(f'beta_w_ed_{occ_suffix}{gender_suffix}', 4.5)
    sigma = spec.initial_values.get(f'sigma_{occ_suffix}{gender_suffix}', 0.3)

    # Compute mean log-wage
    exp_scaled = experience / 10.0
    log_wage_mean = (
        beta_0 +
        beta_exp * exp_scaled +
        beta_exp2 * (exp_scaled ** 2) +
        beta_ed * education
    )

    # Log-normal density
    log_wage = np.log(wage)
    z = (log_wage - log_wage_mean) / sigma
    density = (1 / (wage * sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * z ** 2)

    return density


def compute_occupation_availability(
    occupation: str,
    gender_suffix: str,
    spec: 'EstimationSpec'
) -> float:
    """
    Compute occupation availability g3(occ).

    Multinomial logit form:
    g3(occ) = exp(μ_occ) / Σ_k exp(μ_k)

    Service (loc4_4) is the reference category with μ_service = 0.

    Parameters
    ----------
    occupation : str
        Occupation code
    gender_suffix : str
        Gender suffix (_sm or _sf)
    spec : EstimationSpec
        Parsed specification

    Returns
    -------
    float
        Occupation availability probability
    """
    # Map occupation to parameter name
    occ_map = {
        'loc4_1': 'mu_mgr',
        'loc4_2': 'mu_prof',
        'loc4_3': 'mu_tech',
        'loc4_4': None  # Reference category
    }

    # Get all occupation availability parameters
    mu_values = []
    for occ in ['loc4_1', 'loc4_2', 'loc4_3', 'loc4_4']:
        param_name = occ_map[occ]
        if param_name is None:
            mu = 0.0  # Reference category
        else:
            mu = spec.initial_values.get(f'{param_name}{gender_suffix}', 0.0)
        mu_values.append(mu)

    # Compute softmax probabilities
    exp_mu = np.exp(mu_values)
    probs = exp_mu / exp_mu.sum()

    # Return probability for this occupation
    occ_idx = ['loc4_1', 'loc4_2', 'loc4_3', 'loc4_4'].index(occupation)
    return probs[occ_idx]


# ==============================================================================
# End of mcfadden_sampler.py
# ==============================================================================
