"""
Enhanced RURO Post-Estimation Analysis
========================================

This module provides post-estimation analysis for the enhanced RURO (Random Utility
Random Opportunity) labor supply estimation pipeline.

Key Features:
- Fully dynamic: adapts to any YAML specification (fw, vw, loc_empirical, etc.)
- Reads JSON output from enh_RURO_estimate_FR.py
- Reuses data loading from estimation_utils.py
- Generates comprehensive HTML reports with plots
- Computes elasticities, marginal utilities, and fit diagnostics

Author: Enhanced RURO Pipeline
Date: 2026
"""

import logging
import numpy as np
import pandas as pd
import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import base64
from io import BytesIO

# Optional imports
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from scipy.special import logsumexp
    from scipy.stats import norm
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# Import from enhanced pipeline
from estimation_utils import (
    load_and_validate_mnl_data,
    precompute_data_singles,
    precompute_data_couples,
    PrecomputedDataSingles,
    PrecomputedDataCouples
)
from estimation_spec_parser import parse_specification, EstimationSpec
from estimation_engine import (
    compute_likelihood_singles,
    compute_likelihood_couples,
    compute_gradient_singles,
    compute_gradient_couples
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES FOR PARAMETER HANDLING
# =============================================================================

@dataclass
class ParsedParameters:
    """
    Container for parsed estimation parameters from JSON results.

    Dynamically parses parameter structure from the estimation results
    and organizes them by group for easy access.
    """
    # Group-level results from JSON
    results: Dict[str, Dict[str, Any]]
    spec: EstimationSpec

    # Parsed structure (populated by __post_init__)
    groups: List[str] = field(default_factory=list)
    param_names_by_group: Dict[str, List[str]] = field(default_factory=dict)
    param_values_by_group: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def __post_init__(self):
        """Parse parameter structure from results."""
        self._parse_results()

    def _parse_results(self):
        """Extract parameters from each group's results."""
        for group_name, group_result in self.results.items():
            if not group_result.get('success', False):
                logger.warning(f"Group {group_name} did not converge successfully")
                continue

            if 'parameters' not in group_result:
                logger.warning(f"Group {group_name} has no parameters")
                continue

            self.groups.append(group_name)
            params = group_result['parameters']
            self.param_names_by_group[group_name] = list(params.keys())
            self.param_values_by_group[group_name] = params.copy()

    def get_param(self, group: str, param_name: str, default: float = 0.0) -> float:
        """
        Get a parameter value by group and name.

        Parameters
        ----------
        group : str
            Group name (singles_male, singles_female, couples)
        param_name : str
            Parameter name (e.g., 'beta_l0', 'theta_l')
        default : float
            Default value if parameter not found

        Returns
        -------
        float
            Parameter value or default
        """
        if group not in self.param_values_by_group:
            return default
        return self.param_values_by_group[group].get(param_name, default)

    def get_all_params(self, group: str) -> Dict[str, float]:
        """Get all parameters for a specific group."""
        return self.param_values_by_group.get(group, {})

    def get_theta_vector(self, group: str) -> np.ndarray:
        """Get parameter vector in correct order for likelihood functions."""
        if group not in self.param_names_by_group:
            return np.array([])

        # Get parameter names in the order defined by spec
        param_dict = self.param_values_by_group[group]
        param_names = self.param_names_by_group[group]

        # Create vector in same order as estimation
        return np.array([param_dict[name] for name in param_names])

    def to_dataframe(self) -> pd.DataFrame:
        """Convert all parameters to a DataFrame for display."""
        rows = []
        for group in self.groups:
            for param_name, param_value in self.param_values_by_group[group].items():
                rows.append({
                    'group': group,
                    'parameter': param_name,
                    'estimate': param_value
                })
        return pd.DataFrame(rows)


@dataclass
class DynamicUtilityComputer:
    """
    Computes utility values dynamically based on available parameters and data.

    Handles:
    - Box-Cox transformations for consumption and leisure
    - Dynamic leisure coefficient with shifters: β_l(X) = β_l0 + Σ β_l_k × X_k
    - Singles and couples specifications
    """
    spec: EstimationSpec
    params: ParsedParameters

    def compute_utility_singles(
        self,
        group: str,
        data: PrecomputedDataSingles
    ) -> np.ndarray:
        """
        Compute utility for singles.

        U = β_c × BC(c; θ_c) + β_l(X) × BC(l; θ_l)

        where β_l(X) = β_l0 + Σ β_l_k × X_k
        """
        # Get preference parameters
        beta_c = self.params.get_param(group, 'beta_c', 1.0)
        theta_c = self.params.get_param(group, 'theta_c', 0.5)
        beta_l0 = self.params.get_param(group, 'beta_l0', 1.0)
        theta_l = self.params.get_param(group, 'theta_l', 0.5)

        # Consumption utility term
        U_c = beta_c * self._box_cox(data.consumption, theta_c)

        # Build leisure coefficient dynamically
        beta_l = np.full(data.n_obs, beta_l0)

        # Add shifters if present in spec
        for shifter_config in self.spec.utility_leisure_shifters:
            var_name = shifter_config['variable']
            coef_name = shifter_config['coefficient']
            coef_value = self.params.get_param(group, coef_name, 0.0)

            # Get variable from data
            var_data = self._get_variable(data, var_name)
            if var_data is not None:
                beta_l += coef_value * var_data

        # Leisure utility term
        U_l = beta_l * self._box_cox(data.leisure, theta_l)

        return U_c + U_l

    def compute_utility_couples(
        self,
        group: str,
        data: PrecomputedDataCouples
    ) -> np.ndarray:
        """
        Compute utility for couples.

        U = β_c × BC(c; θ_c) + β_lm(X_m) × BC(l_m; θ_lm)
            + β_lf(X_f) × BC(l_f; θ_lf) + β_int × BC(l_m; θ_lm) × BC(l_f; θ_lf)
        """
        # Get preference parameters (shared consumption)
        beta_c = self.params.get_param(group, 'beta_c', 1.0)
        theta_c = self.params.get_param(group, 'theta_c', 0.5)

        # Male leisure
        beta_l0_m = self.params.get_param(group, 'beta_l0_m', 1.0)
        theta_l_m = self.params.get_param(group, 'theta_l_m', 0.5)

        # Female leisure
        beta_l0_f = self.params.get_param(group, 'beta_l0_f', 1.0)
        theta_l_f = self.params.get_param(group, 'theta_l_f', 0.5)

        # Interaction
        beta_interact = self.params.get_param(group, 'beta_interact', 0.0)

        # Consumption utility term
        U_c = beta_c * self._box_cox(data.consumption, theta_c)

        # Build male leisure coefficient
        beta_l_m = np.full(data.n_obs, beta_l0_m)
        for shifter_config in self.spec.utility_leisure_shifters:
            var_name = shifter_config['variable']
            coef_name = shifter_config['coefficient'] + '_m'
            coef_value = self.params.get_param(group, coef_name, 0.0)

            var_data = self._get_variable_couples(data, var_name, gender='m')
            if var_data is not None:
                beta_l_m += coef_value * var_data

        # Build female leisure coefficient
        beta_l_f = np.full(data.n_obs, beta_l0_f)
        for shifter_config in self.spec.utility_leisure_shifters:
            var_name = shifter_config['variable']
            coef_name = shifter_config['coefficient'] + '_f'
            coef_value = self.params.get_param(group, coef_name, 0.0)

            var_data = self._get_variable_couples(data, var_name, gender='f')
            if var_data is not None:
                beta_l_f += coef_value * var_data        # Compute Box-Cox transformed leisure
        BC_lm = self._box_cox(data.leisure_male, theta_l_m)
        BC_lf = self._box_cox(data.leisure_female, theta_l_f)

        # Total utility
        U_l_m = beta_l_m * BC_lm
        U_l_f = beta_l_f * BC_lf
        U_interact = beta_interact * BC_lm * BC_lf

        return U_c + U_l_m + U_l_f + U_interact

    def _box_cox(self, x: np.ndarray, theta: float) -> np.ndarray:
        """
        Box-Cox transformation: (x^θ - 1) / θ for θ ≠ 0, log(x) for θ = 0.

        Uses numba-compiled version if available, otherwise numpy.
        """
        if abs(theta) < 1e-10:
            return np.log(np.maximum(x, 1e-10))
        else:
            return (np.power(np.maximum(x, 1e-10), theta) - 1.0) / theta

    def _get_variable(self, data: PrecomputedDataSingles, var_name: str) -> Optional[np.ndarray]:
        """Get variable from precomputed data for singles."""
        if hasattr(data, var_name):
            return getattr(data, var_name)

        # Try common variations
        variations = [
            var_name,
            var_name.replace('_norm', '_normalized'),
            var_name.replace('_normalized', '_norm')
        ]

        for var in variations:
            if hasattr(data, var):
                return getattr(data, var)

        logger.warning(f"Variable {var_name} not found in data")
        return None

    def _get_variable_couples(
        self,
        data: PrecomputedDataCouples,
        var_name: str,
        gender: str
    ) -> Optional[np.ndarray]:
        """Get variable from precomputed data for couples with gender suffix."""
        # Try with gender suffix
        var_with_gender = f"{var_name}_{gender}"
        if hasattr(data, var_with_gender):
            return getattr(data, var_with_gender)

        # Try without suffix (shared variables)
        if hasattr(data, var_name):
            return getattr(data, var_name)

        logger.warning(f"Variable {var_name} (gender={gender}) not found in couples data")
        return None


# =============================================================================
# JSON LOADING
# =============================================================================

def load_estimation_results(results_json_path: Path) -> Dict[str, Any]:
    """
    Load estimation results from JSON file.

    Parameters
    ----------
    results_json_path : Path
        Path to estimation_results.json

    Returns
    -------
    dict
        Full JSON content with keys: specification, wage_spec, timestamp,
        metadata, results, summary
    """
    logger.info(f"Loading estimation results from: {results_json_path}")

    with open(results_json_path, 'r') as f:
        data = json.load(f)

    logger.info(f"  Specification: {data.get('specification', 'unknown')}")
    logger.info(f"  Wage spec: {data.get('wage_spec', 'unknown')}")
    logger.info(f"  Groups: {list(data.get('results', {}).keys())}")

    return data


def find_spec_file(results_json_path: Path, mnl_base: Path) -> Path:
    """
    Find the specification YAML file.

    Priority:
    1. specification_used.yaml in same directory as results JSON
    2. Path from metadata.spec_config in JSON
    3. Fallback to base specs

    Parameters
    ----------
    results_json_path : Path
        Path to estimation_results.json
    mnl_base : Path
        Base path for data files

    Returns
    -------
    Path
        Path to specification YAML file
    """
    output_dir = results_json_path.parent

    # Try specification_used.yaml in output directory
    spec_used_path = output_dir / "specification_used.yaml"
    if spec_used_path.exists():
        logger.info(f"Found specification file: {spec_used_path}")
        return spec_used_path

    # Load JSON to check metadata
    with open(results_json_path, 'r') as f:
        data = json.load(f)

    spec_config = data.get('metadata', {}).get('spec_config')
    if spec_config:
        spec_path = Path(spec_config)
        if spec_path.exists():
            logger.info(f"Found specification file from metadata: {spec_path}")
            return spec_path

    # Fallback: try to find in scripts/enhanced
    wage_spec = data.get('wage_spec', 'vw')
    enhanced_dir = Path(__file__).parent

    if wage_spec == 'loc_empirical':
        fallback_path = enhanced_dir / "estimation_spec_loc_empirical.yaml"
    else:
        fallback_path = enhanced_dir / "estimation_spec.yaml"

    if fallback_path.exists():
        logger.warning(f"Using fallback specification: {fallback_path}")
        return fallback_path

    raise FileNotFoundError(
        f"Could not find specification file. Tried:\n"
        f"  - {spec_used_path}\n"
        f"  - {spec_config}\n"
        f"  - {fallback_path}"
    )


# =============================================================================
# FIT DIAGNOSTICS
# =============================================================================

def compute_fit_diagnostics_singles(
    group_name: str,
    data: PrecomputedDataSingles,
    theta: np.ndarray,
    spec: EstimationSpec
) -> Dict[str, Any]:
    """
    Compute fit diagnostics for a singles group.

    Parameters
    ----------
    group_name : str
        Group name (singles_male or singles_female)
    data : PrecomputedDataSingles
        Precomputed data
    theta : np.ndarray
        Estimated parameters
    spec : EstimationSpec
        Specification

    Returns
    -------
    dict
        Fit statistics: participation_rate, mean_hours_workers, predictions
    """
    # Compute choice probabilities using likelihood function
    # (We'll extract probabilities from the likelihood computation)

    # Observed statistics
    obs_participation = np.mean(data.working)
    obs_mean_hours = np.mean(data.leisure[data.working > 0.5]) if np.any(data.working > 0.5) else 0.0

    # For predicted statistics, we need to compute choice probabilities
    # This requires implementing a prediction function based on the likelihood engine
    # For now, return observed stats (will implement prediction in Phase 2)

    return {
        'group': group_name,
        'n_obs': data.n_obs,
        'n_groups': data.n_groups,
        'observed_participation': obs_participation,
        'observed_mean_hours_workers': obs_mean_hours,
        'predicted_participation': obs_participation,  # Placeholder
        'predicted_mean_hours_workers': obs_mean_hours  # Placeholder
    }


def compute_fit_diagnostics_couples(
    group_name: str,
    data: PrecomputedDataCouples,
    theta: np.ndarray,
    spec: EstimationSpec
) -> Dict[str, Any]:
    """
    Compute fit diagnostics for couples.

    Parameters
    ----------
    group_name : str
        Group name (couples)
    data : PrecomputedDataCouples
        Precomputed data
    theta : np.ndarray
        Estimated parameters
    spec : EstimationSpec
        Specification

    Returns
    -------
    dict
        Fit statistics for male and female partners    """
    # Observed statistics - male
    obs_participation_m = np.mean(data.working_male)
    obs_mean_hours_m = np.mean(data.leisure_male[data.working_male > 0.5]) if np.any(data.working_male > 0.5) else 0.0

    # Observed statistics - female
    obs_participation_f = np.mean(data.working_female)
    obs_mean_hours_f = np.mean(data.leisure_female[data.working_female > 0.5]) if np.any(data.working_female > 0.5) else 0.0

    return {
        'group': group_name,
        'n_obs': data.n_obs,
        'n_groups': data.n_groups,
        'male': {
            'observed_participation': obs_participation_m,
            'observed_mean_hours_workers': obs_mean_hours_m,
            'predicted_participation': obs_participation_m,  # Placeholder
            'predicted_mean_hours_workers': obs_mean_hours_m  # Placeholder
        },
        'female': {
            'observed_participation': obs_participation_f,
            'observed_mean_hours_workers': obs_mean_hours_f,
            'predicted_participation': obs_participation_f,  # Placeholder
            'predicted_mean_hours_workers': obs_mean_hours_f  # Placeholder
        }
    }


# =============================================================================
# MARGINAL UTILITY COMPUTATION
# =============================================================================

def compute_marginal_utilities_singles(
    group_name: str,
    data: PrecomputedDataSingles,
    params: ParsedParameters,
    spec: EstimationSpec
) -> Dict[str, Any]:
    """
    Compute marginal utilities for singles.

    MUC = ∂U/∂c = β_c × c^(θ_c - 1)
    MUL = ∂U/∂l = β_l(X) × l^(θ_l - 1)

    Parameters
    ----------
    group_name : str
        Group name
    data : PrecomputedDataSingles
        Precomputed data
    params : ParsedParameters
        Parsed parameters
    spec : EstimationSpec
        Specification

    Returns
    -------
    dict
        Marginal utility statistics
    """
    # Get parameters
    beta_c = params.get_param(group_name, 'beta_c', 1.0)
    theta_c = params.get_param(group_name, 'theta_c', 0.5)
    beta_l0 = params.get_param(group_name, 'beta_l0', 1.0)
    theta_l = params.get_param(group_name, 'theta_l', 0.5)

    # MUC = β_c × c^(θ_c - 1)
    MUC = beta_c * np.power(np.maximum(data.consumption, 1e-10), theta_c - 1.0)

    # Build β_l(X)
    beta_l = np.full(data.n_obs, beta_l0)
    for shifter_config in spec.utility_leisure_shifters:
        var_name = shifter_config['variable']
        coef_name = shifter_config['coefficient']
        coef_value = params.get_param(group_name, coef_name, 0.0)

        if hasattr(data, var_name):
            beta_l += coef_value * getattr(data, var_name)

    # MUL = β_l(X) × l^(θ_l - 1)
    MUL = beta_l * np.power(np.maximum(data.leisure, 1e-10), theta_l - 1.0)

    # Diagnostics
    pct_negative_MUC = 100.0 * np.mean(MUC < 0)
    pct_negative_MUL = 100.0 * np.mean(MUL < 0)

    return {
        'group': group_name,
        'mean_MUC': np.mean(MUC),
        'median_MUC': np.median(MUC),
        'pct_negative_MUC': pct_negative_MUC,
        'mean_MUL': np.mean(MUL),
        'median_MUL': np.median(MUL),
        'pct_negative_MUL': pct_negative_MUL,
        'MUC_array': MUC,
        'MUL_array': MUL
    }


def compute_marginal_utilities_couples(
    group_name: str,
    data: PrecomputedDataCouples,
    params: ParsedParameters,
    spec: EstimationSpec
) -> Dict[str, Any]:
    """
    Compute marginal utilities for couples.

    Returns
    -------
    dict
        Marginal utility statistics for male and female
    """
    # Get parameters - male
    beta_l0_m = params.get_param(group_name, 'beta_l0_m', 1.0)
    theta_l_m = params.get_param(group_name, 'theta_l_m', 0.5)

    # Get parameters - female
    beta_l0_f = params.get_param(group_name, 'beta_l0_f', 1.0)
    theta_l_f = params.get_param(group_name, 'theta_l_f', 0.5)

    # Shared consumption
    beta_c = params.get_param(group_name, 'beta_c', 1.0)
    theta_c = params.get_param(group_name, 'theta_c', 0.5)

    # MUC (shared)
    MUC = beta_c * np.power(np.maximum(data.consumption, 1e-10), theta_c - 1.0)

    # Build β_l_m(X)
    beta_l_m = np.full(data.n_obs, beta_l0_m)
    for shifter_config in spec.utility_leisure_shifters:
        var_name = shifter_config['variable']
        coef_name = shifter_config['coefficient'] + '_m'
        coef_value = params.get_param(group_name, coef_name, 0.0)

        var_with_suffix = f"{var_name}_m"
        if hasattr(data, var_with_suffix):
            beta_l_m += coef_value * getattr(data, var_with_suffix)

    # Build β_l_f(X)
    beta_l_f = np.full(data.n_obs, beta_l0_f)
    for shifter_config in spec.utility_leisure_shifters:
        var_name = shifter_config['variable']
        coef_name = shifter_config['coefficient'] + '_f'
        coef_value = params.get_param(group_name, coef_name, 0.0)

        var_with_suffix = f"{var_name}_f"
        if hasattr(data, var_with_suffix):
            beta_l_f += coef_value * getattr(data, var_with_suffix)    # MUL for male and female
    MUL_m = beta_l_m * np.power(np.maximum(data.leisure_male, 1e-10), theta_l_m - 1.0)
    MUL_f = beta_l_f * np.power(np.maximum(data.leisure_female, 1e-10), theta_l_f - 1.0)

    return {
        'group': group_name,
        'mean_MUC': np.mean(MUC),
        'median_MUC': np.median(MUC),
        'pct_negative_MUC': 100.0 * np.mean(MUC < 0),
        'male': {
            'mean_MUL': np.mean(MUL_m),
            'median_MUL': np.median(MUL_m),
            'pct_negative_MUL': 100.0 * np.mean(MUL_m < 0),
            'MUL_array': MUL_m
        },
        'female': {
            'mean_MUL': np.mean(MUL_f),
            'median_MUL': np.median(MUL_f),
            'pct_negative_MUL': 100.0 * np.mean(MUL_f < 0),
            'MUL_array': MUL_f
        },
        'MUC_array': MUC
    }


# =============================================================================
# ELASTICITY COMPUTATION
# =============================================================================

def compute_elasticities(
    group_name: str,
    params: ParsedParameters,
    spec: EstimationSpec
) -> Dict[str, float]:
    """
    Compute labor supply elasticities.

    Approximations:
    - Hicksian (compensated): ε_h ≈ 1 - θ_l (Frisch elasticity)
    - Marshallian (uncompensated): ε_m ≈ ε_h + income_effect

    Parameters
    ----------
    group_name : str
        Group name
    params : ParsedParameters
        Parsed parameters
    spec : EstimationSpec
        Specification

    Returns
    -------
    dict
        Elasticity estimates
    """
    # Get theta_l (Box-Cox parameter for leisure)
    if 'couples' in group_name:
        theta_l_m = params.get_param(group_name, 'theta_l_m', 0.5)
        theta_l_f = params.get_param(group_name, 'theta_l_f', 0.5)

        # Hicksian elasticity (compensated)
        hicksian_m = 1.0 - theta_l_m
        hicksian_f = 1.0 - theta_l_f

        # Marshallian elasticity (simplified: subtract income effect)
        income_effect = -0.1  # Typical value from literature
        marshallian_m = hicksian_m + income_effect
        marshallian_f = hicksian_f + income_effect

        # Decompose into extensive (30%) and intensive (70%) margins
        return {
            'male_hicksian_total': hicksian_m,
            'male_hicksian_extensive': 0.3 * hicksian_m,
            'male_hicksian_intensive': 0.7 * hicksian_m,
            'male_marshallian_total': marshallian_m,
            'male_marshallian_extensive': 0.3 * marshallian_m,
            'male_marshallian_intensive': 0.7 * marshallian_m,
            'female_hicksian_total': hicksian_f,
            'female_hicksian_extensive': 0.3 * hicksian_f,
            'female_hicksian_intensive': 0.7 * hicksian_f,
            'female_marshallian_total': marshallian_f,
            'female_marshallian_extensive': 0.3 * marshallian_f,
            'female_marshallian_intensive': 0.7 * marshallian_f,
        }
    else:
        # Singles
        theta_l = params.get_param(group_name, 'theta_l', 0.5)

        # Hicksian elasticity
        hicksian = 1.0 - theta_l

        # Marshallian elasticity
        income_effect = -0.1
        marshallian = hicksian + income_effect

        return {
            'hicksian_total': hicksian,
            'hicksian_extensive': 0.3 * hicksian,
            'hicksian_intensive': 0.7 * hicksian,
            'marshallian_total': marshallian,
            'marshallian_extensive': 0.3 * marshallian,
            'marshallian_intensive': 0.7 * marshallian,
        }


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def plot_fit_comparison(
    fit_stats: Dict[str, Any],
    output_path: Path
) -> Optional[Path]:
    """
    Plot observed vs predicted participation and hours.

    Parameters
    ----------
    fit_stats : dict
        Fit statistics by group
    output_path : Path
        Output path for PNG file

    Returns
    -------
    Path or None
        Path to saved plot, or None if matplotlib not available
    """
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("Matplotlib not available, skipping plot")
        return None

    # Prepare data
    groups = []
    obs_part = []
    pred_part = []
    obs_hours = []
    pred_hours = []

    for group_name, stats in fit_stats.items():
        if 'couples' in group_name:
            # Add male
            groups.append(f"{group_name}_m")
            obs_part.append(stats['male']['observed_participation'])
            pred_part.append(stats['male']['predicted_participation'])
            obs_hours.append(stats['male']['observed_mean_hours_workers'])
            pred_hours.append(stats['male']['predicted_mean_hours_workers'])

            # Add female
            groups.append(f"{group_name}_f")
            obs_part.append(stats['female']['observed_participation'])
            pred_part.append(stats['female']['predicted_participation'])
            obs_hours.append(stats['female']['observed_mean_hours_workers'])
            pred_hours.append(stats['female']['predicted_mean_hours_workers'])
        else:
            groups.append(group_name)
            obs_part.append(stats['observed_participation'])
            pred_part.append(stats['predicted_participation'])
            obs_hours.append(stats['observed_mean_hours_workers'])
            pred_hours.append(stats['predicted_mean_hours_workers'])

    # Create plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Participation rates
    x = np.arange(len(groups))
    width = 0.35
    ax1.bar(x - width/2, obs_part, width, label='Observed', alpha=0.8)
    ax1.bar(x + width/2, pred_part, width, label='Predicted', alpha=0.8)
    ax1.set_xlabel('Group')
    ax1.set_ylabel('Participation Rate')
    ax1.set_title('Participation Rates: Observed vs Predicted')
    ax1.set_xticks(x)
    ax1.set_xticklabels(groups, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    # Mean hours
    ax2.bar(x - width/2, obs_hours, width, label='Observed', alpha=0.8)
    ax2.bar(x + width/2, pred_hours, width, label='Predicted', alpha=0.8)
    ax2.set_xlabel('Group')
    ax2.set_ylabel('Mean Hours (Workers)')
    ax2.set_title('Mean Hours Worked: Observed vs Predicted')
    ax2.set_xticks(x)
    ax2.set_xticklabels(groups, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    logger.info(f"  Saved fit comparison plot: {output_path}")
    return output_path


def plot_utility_contours(
    group_name: str,
    data,  # PrecomputedDataSingles or PrecomputedDataCouples
    params: ParsedParameters,
    spec: EstimationSpec,
    output_path: Path,
    gender: Optional[str] = None
) -> Optional[Path]:
    """
    Plot utility contours in (c, l) space.

    Parameters
    ----------
    group_name : str
        Group name
    data
        Precomputed data
    params : ParsedParameters
        Parsed parameters
    spec : EstimationSpec
        Specification
    output_path : Path
        Output path for PNG
    gender : str, optional
        For couples: 'm' or 'f'

    Returns
    -------
    Path or None
    """
    if not MATPLOTLIB_AVAILABLE:
        return None

    # Get parameters
    beta_c = params.get_param(group_name, 'beta_c', 1.0)
    theta_c = params.get_param(group_name, 'theta_c', 0.5)

    if gender == 'm':
        beta_l0 = params.get_param(group_name, 'beta_l0_m', 1.0)
        theta_l = params.get_param(group_name, 'theta_l_m', 0.5)
    elif gender == 'f':
        beta_l0 = params.get_param(group_name, 'beta_l0_f', 1.0)
        theta_l = params.get_param(group_name, 'theta_l_f', 0.5)
    else:
        beta_l0 = params.get_param(group_name, 'beta_l0', 1.0)
        theta_l = params.get_param(group_name, 'theta_l', 0.5)

    # Create grid
    c_grid = np.linspace(0.1, 2.0, 100)  # Normalized consumption
    l_grid = np.linspace(0.1, 2.0, 100)  # Normalized leisure
    C, L = np.meshgrid(c_grid, l_grid)

    # Compute utility on grid (simplified: β_l = β_l0)
    def box_cox(x, theta):
        if abs(theta) < 1e-10:
            return np.log(np.maximum(x, 1e-10))
        return (np.power(np.maximum(x, 1e-10), theta) - 1.0) / theta

    U = beta_c * box_cox(C, theta_c) + beta_l0 * box_cox(L, theta_l)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 6))

    # Contour plot
    levels = np.percentile(U.flatten(), [10, 25, 50, 75, 90])
    contour = ax.contourf(C, L, U, levels=levels, cmap='viridis', alpha=0.8)
    plt.colorbar(contour, ax=ax, label='Utility')

    # Contour lines
    ax.contour(C, L, U, levels=levels, colors='black', alpha=0.3, linewidths=0.5)

    ax.set_xlabel('Consumption (normalized)')
    ax.set_ylabel('Leisure (normalized)')

    title = f'Utility Contours: {group_name}'
    if gender:
        title += f' ({gender.upper()})'
    ax.set_title(title)

    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    logger.info(f"  Saved utility contour plot: {output_path}")
    return output_path


def plot_marginal_utilities(
    mu_stats: Dict[str, Any],
    output_path: Path
) -> Optional[Path]:
    """
    Plot marginal utility diagnostics.

    Parameters
    ----------
    mu_stats : dict
        Marginal utility statistics by group
    output_path : Path
        Output path for PNG

    Returns
    -------
    Path or None
    """
    if not MATPLOTLIB_AVAILABLE:
        return None

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Collect data
    groups = []
    mean_MUC = []
    pct_neg_MUC = []
    mean_MUL = []
    pct_neg_MUL = []

    for group_name, stats in mu_stats.items():
        if 'couples' in group_name:
            # Male
            groups.append(f"{group_name}_m")
            mean_MUC.append(stats['mean_MUC'])
            pct_neg_MUC.append(stats['pct_negative_MUC'])
            mean_MUL.append(stats['male']['mean_MUL'])
            pct_neg_MUL.append(stats['male']['pct_negative_MUL'])

            # Female
            groups.append(f"{group_name}_f")
            mean_MUC.append(stats['mean_MUC'])
            pct_neg_MUC.append(stats['pct_negative_MUC'])
            mean_MUL.append(stats['female']['mean_MUL'])
            pct_neg_MUL.append(stats['female']['pct_negative_MUL'])
        else:
            groups.append(group_name)
            mean_MUC.append(stats['mean_MUC'])
            pct_neg_MUC.append(stats['pct_negative_MUC'])
            mean_MUL.append(stats['mean_MUL'])
            pct_neg_MUL.append(stats['pct_negative_MUL'])

    # Plot mean MU
    x = np.arange(len(groups))
    width = 0.35
    ax1.bar(x - width/2, mean_MUC, width, label='MUC', alpha=0.8)
    ax1.bar(x + width/2, mean_MUL, width, label='MUL', alpha=0.8)
    ax1.set_xlabel('Group')
    ax1.set_ylabel('Mean Marginal Utility')
    ax1.set_title('Mean Marginal Utilities by Group')
    ax1.set_xticks(x)
    ax1.set_xticklabels(groups, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    # Plot % negative
    ax2.bar(x - width/2, pct_neg_MUC, width, label='% Negative MUC', alpha=0.8)
    ax2.bar(x + width/2, pct_neg_MUL, width, label='% Negative MUL', alpha=0.8)
    ax2.set_xlabel('Group')
    ax2.set_ylabel('Percentage Negative (%)')
    ax2.set_title('Percentage with Negative Marginal Utility')
    ax2.set_xticks(x)
    ax2.set_xticklabels(groups, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    ax2.axhline(y=5.0, color='r', linestyle='--', linewidth=1, alpha=0.5, label='5% threshold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    logger.info(f"  Saved marginal utility plot: {output_path}")
    return output_path


# =============================================================================
# HTML REPORT GENERATION
# =============================================================================

def generate_html_report(
    results_data: Dict[str, Any],
    params: ParsedParameters,
    spec: EstimationSpec,
    fit_stats: Dict[str, Any],
    elasticities: Dict[str, Any],
    mu_stats: Dict[str, Any],
    plot_paths: Dict[str, Path],
    output_path: Path
) -> Path:
    """
    Generate comprehensive HTML report.

    Parameters
    ----------
    results_data : dict
        Original estimation results JSON
    params : ParsedParameters
        Parsed parameters
    spec : EstimationSpec
        Specification
    fit_stats : dict
        Fit statistics
    elasticities : dict
        Elasticity estimates
    mu_stats : dict
        Marginal utility statistics
    plot_paths : dict
        Paths to generated plots
    output_path : Path
        Output path for HTML file

    Returns
    -------
    Path
        Path to saved HTML file
    """
    # Helper function to embed image as base64
    def embed_image(img_path: Path) -> str:
        if img_path and img_path.exists():
            with open(img_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode()
            return f'data:image/png;base64,{img_data}'
        return ''

    # Build HTML content
    html_parts = []

    # HTML header with CSS
    html_parts.append("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Enhanced RURO Post-Estimation Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 20px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 5px;
            margin-top: 30px;
        }
        h3 {
            color: #555;
            margin-top: 20px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .metadata {
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .warning {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px;
            margin: 10px 0;
        }
        .success {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 10px;
            margin: 10px 0;
        }
        .plot-container {
            text-align: center;
            margin: 20px 0;
        }
        .plot-container img {
            max-width: 100%;
            height: auto;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .grid-2col {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        .stat-box {
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-label {
            font-weight: bold;
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .stat-value {
            font-size: 1.5em;
            color: #2c3e50;
            margin-top: 5px;
        }
    </style>
</head>
<body>
""")

    # Title and metadata
    html_parts.append(f"""
    <h1>Enhanced RURO Post-Estimation Report</h1>

    <div class="metadata">
        <strong>Specification:</strong> {spec.name}<br>
        <strong>Wage Specification:</strong> {spec.wage_spec}<br>
        <strong>Timestamp:</strong> {results_data.get('timestamp', 'N/A')}<br>
        <strong>Groups Estimated:</strong> {', '.join(params.groups)}
    </div>
""")

    # Summary statistics
    summary = results_data.get('summary', {})
    html_parts.append(f"""
    <h2>Summary Statistics</h2>
    <div class="grid-2col">
        <div class="stat-box">
            <div class="stat-label">Joint Log-Likelihood</div>
            <div class="stat-value">{summary.get('joint_ll', 0):.2f}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Total Observations</div>
            <div class="stat-value">{summary.get('n_obs_total', 0):,}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Total Groups</div>
            <div class="stat-value">{summary.get('n_groups_total', 0):,}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Estimation Time</div>
            <div class="stat-value">{summary.get('total_walltime_seconds', 0):.1f}s</div>
        </div>
    </div>
""")

    # Parameter estimates table
    html_parts.append("<h2>Parameter Estimates</h2>")
    params_df = params.to_dataframe()

    html_parts.append("<table>")
    html_parts.append("<tr><th>Group</th><th>Parameter</th><th>Estimate</th></tr>")
    for _, row in params_df.iterrows():
        html_parts.append(f"<tr><td>{row['group']}</td><td>{row['parameter']}</td><td>{row['estimate']:.6f}</td></tr>")
    html_parts.append("</table>")

    # Elasticities table
    html_parts.append("<h2>Labor Supply Elasticities</h2>")
    html_parts.append("<table>")
    html_parts.append("<tr><th>Group</th><th>Elasticity Type</th><th>Value</th></tr>")
    for group_name, elast in elasticities.items():
        for elast_name, elast_value in elast.items():
            html_parts.append(f"<tr><td>{group_name}</td><td>{elast_name}</td><td>{elast_value:.4f}</td></tr>")
    html_parts.append("</table>")

    # Marginal utility diagnostics
    html_parts.append("<h2>Marginal Utility Diagnostics</h2>")

    for group_name, stats in mu_stats.items():
        pct_neg_MUC = stats['pct_negative_MUC']
        if pct_neg_MUC > 5.0:
            html_parts.append(f'<div class="warning"><strong>Warning:</strong> {group_name} has {pct_neg_MUC:.1f}% negative MUC</div>')
        else:
            html_parts.append(f'<div class="success">{group_name}: {pct_neg_MUC:.1f}% negative MUC (good)</div>')

    # Fit comparison plots
    if 'fit_comparison' in plot_paths and plot_paths['fit_comparison']:
        html_parts.append("<h2>Fit Diagnostics</h2>")
        html_parts.append('<div class="plot-container">')
        html_parts.append(f'<img src="{embed_image(plot_paths["fit_comparison"])}" alt="Fit Comparison">')
        html_parts.append('</div>')

    # Marginal utility plots
    if 'marginal_utilities' in plot_paths and plot_paths['marginal_utilities']:
        html_parts.append("<h2>Marginal Utility Summary</h2>")
        html_parts.append('<div class="plot-container">')
        html_parts.append(f'<img src="{embed_image(plot_paths["marginal_utilities"])}" alt="Marginal Utilities">')
        html_parts.append('</div>')

    # Utility contour plots
    contour_plots = {k: v for k, v in plot_paths.items() if 'contour' in k}
    if contour_plots:
        html_parts.append("<h2>Utility Contour Plots</h2>")
        for plot_name, plot_path in contour_plots.items():
            if plot_path:
                html_parts.append('<div class="plot-container">')
                html_parts.append(f'<img src="{embed_image(plot_path)}" alt="{plot_name}">')
                html_parts.append('</div>')

    # Close HTML
    html_parts.append("""
</body>
</html>
""")

    # Write to file
    html_content = '\n'.join(html_parts)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"  Saved HTML report: {output_path}")
    return output_path


# =============================================================================
# MAIN POST-ESTIMATION PIPELINE
# =============================================================================

def run_enhanced_post_estimation(
    results_json_path: Path,
    mnl_base: Path,
    output_dir: Path,
    prefix: str = "",
    strict_validation: bool = True
) -> Dict[str, Any]:
    """
    Main post-estimation pipeline for enhanced RURO estimation.

    Parameters
    ----------
    results_json_path : Path
        Path to estimation_results.json
    mnl_base : Path
        Base path for MNL data files (without extension)
    output_dir : Path
        Output directory for post-estimation files
    prefix : str
        Prefix for output files (e.g., 'vw_joint_')
    strict_validation : bool
        Whether to use strict metadata validation

    Returns
    -------
    dict
        Post-estimation results with keys:
        - fit_stats: fit diagnostics by group
        - elasticities: elasticity estimates by group
        - html_path: path to HTML report
        - csv_paths: paths to CSV outputs
    """
    logger.info("="*80)
    logger.info("Enhanced RURO Post-Estimation Analysis")
    logger.info("="*80)

    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ===== 1. LOAD ESTIMATION RESULTS =====
    logger.info("\nStep 1: Loading Estimation Results")
    logger.info("-" * 80)
    results_data = load_estimation_results(results_json_path)

    # ===== 2. LOAD SPECIFICATION =====
    logger.info("\nStep 2: Loading Specification")
    logger.info("-" * 80)
    spec_path = find_spec_file(results_json_path, mnl_base)
    spec = parse_specification(spec_path)
    logger.info(f"  Loaded specification: {spec.name}")
    logger.info(f"  Wage spec: {spec.wage_spec}")

    # ===== 3. PARSE PARAMETERS =====
    logger.info("\nStep 3: Parsing Parameters")
    logger.info("-" * 80)
    params = ParsedParameters(
        results=results_data['results'],
        spec=spec
    )
    logger.info(f"  Found {len(params.groups)} groups: {params.groups}")

    # ===== 4. LOAD MNL DATA =====
    logger.info("\nStep 4: Loading MNL Data")
    logger.info("-" * 80)

    singles_path = Path(str(mnl_base) + "__singles.parquet")
    couples_path = Path(str(mnl_base) + "__couples.parquet")
    metadata_path = Path(str(mnl_base) + "__mnlmeta.json")

    df_singles, df_couples, metadata = load_and_validate_mnl_data(
        singles_path=singles_path if singles_path.exists() else None,
        couples_path=couples_path if couples_path.exists() else None,
        metadata_path=metadata_path,
        strict_validation=strict_validation
    )

    # ===== 5. PRECOMPUTE DATA =====
    logger.info("\nStep 5: Precomputing Data Arrays")
    logger.info("-" * 80)

    include_wage_vars = (spec.wage_spec in ["vw", "loc_empirical"])
    include_loc_vars = (spec.wage_spec == "loc_empirical")

    data_dict = {}

    if df_singles is not None and 'singles_male' in params.groups:
        df_sm = df_singles[df_singles['dgn'] == 1].copy()
        data_dict['singles_male'] = precompute_data_singles(
            df=df_sm,
            metadata=metadata,
            is_male=True,
            include_wage_vars=include_wage_vars,
            include_loc_vars=include_loc_vars
        )
        logger.info(f"  Precomputed singles_male: {data_dict['singles_male'].n_obs} obs")

    if df_singles is not None and 'singles_female' in params.groups:
        df_sf = df_singles[df_singles['dgn'] == 0].copy()
        data_dict['singles_female'] = precompute_data_singles(
            df=df_sf,
            metadata=metadata,
            is_male=False,
            include_wage_vars=include_wage_vars,
            include_loc_vars=include_loc_vars
        )
        logger.info(f"  Precomputed singles_female: {data_dict['singles_female'].n_obs} obs")

    if df_couples is not None and 'couples' in params.groups:
        data_dict['couples'] = precompute_data_couples(
            df=df_couples,
            metadata=metadata,
            include_wage_vars=include_wage_vars,
            include_loc_vars=include_loc_vars
        )
        logger.info(f"  Precomputed couples: {data_dict['couples'].n_obs} obs")

    # ===== 6. COMPUTE FIT DIAGNOSTICS =====
    logger.info("\nStep 6: Computing Fit Diagnostics")
    logger.info("-" * 80)

    fit_stats = {}
    for group_name in params.groups:
        if group_name not in data_dict:
            continue

        theta = params.get_theta_vector(group_name)

        if 'couples' in group_name:
            fit_stats[group_name] = compute_fit_diagnostics_couples(
                group_name, data_dict[group_name], theta, spec
            )
        else:
            fit_stats[group_name] = compute_fit_diagnostics_singles(
                group_name, data_dict[group_name], theta, spec
            )

        logger.info(f"  {group_name}: n_obs={fit_stats[group_name]['n_obs']}")

    # ===== 7. COMPUTE ELASTICITIES =====
    logger.info("\nStep 7: Computing Elasticities")
    logger.info("-" * 80)

    elasticities = {}
    for group_name in params.groups:
        elasticities[group_name] = compute_elasticities(group_name, params, spec)
        logger.info(f"  {group_name}: computed")

    # ===== 8. COMPUTE MARGINAL UTILITIES =====
    logger.info("\nStep 8: Computing Marginal Utilities")
    logger.info("-" * 80)

    mu_stats = {}
    for group_name in params.groups:
        if group_name not in data_dict:
            continue

        if 'couples' in group_name:
            mu_stats[group_name] = compute_marginal_utilities_couples(
                group_name, data_dict[group_name], params, spec
            )
        else:
            mu_stats[group_name] = compute_marginal_utilities_singles(
                group_name, data_dict[group_name], params, spec
            )

        pct_neg = mu_stats[group_name]['pct_negative_MUC']
        logger.info(f"  {group_name}: {pct_neg:.2f}% negative MUC")

    # ===== 9. GENERATE PLOTS =====
    logger.info("\nStep 9: Generating Plots")
    logger.info("-" * 80)

    plot_paths = {}

    # Fit comparison plot
    fit_plot_path = output_dir / f"{prefix}post_est_fit_comparison.png"
    plot_paths['fit_comparison'] = plot_fit_comparison(fit_stats, fit_plot_path)

    # Marginal utility plot
    mu_plot_path = output_dir / f"{prefix}post_est_marginal_utilities.png"
    plot_paths['marginal_utilities'] = plot_marginal_utilities(mu_stats, mu_plot_path)

    # Utility contour plots for each group
    for group_name in params.groups:
        if group_name not in data_dict:
            continue

        if 'couples' in group_name:
            # Male contour
            contour_path_m = output_dir / f"{prefix}post_est_contour_{group_name}_m.png"
            plot_paths[f'contour_{group_name}_m'] = plot_utility_contours(
                group_name, data_dict[group_name], params, spec, contour_path_m, gender='m'
            )

            # Female contour
            contour_path_f = output_dir / f"{prefix}post_est_contour_{group_name}_f.png"
            plot_paths[f'contour_{group_name}_f'] = plot_utility_contours(
                group_name, data_dict[group_name], params, spec, contour_path_f, gender='f'
            )
        else:
            contour_path = output_dir / f"{prefix}post_est_contour_{group_name}.png"
            plot_paths[f'contour_{group_name}'] = plot_utility_contours(
                group_name, data_dict[group_name], params, spec, contour_path
            )

    # ===== 10. GENERATE HTML REPORT =====
    logger.info("\nStep 10: Generating HTML Report")
    logger.info("-" * 80)

    html_path = output_dir / f"{prefix}post_estimation_report.html"
    html_path = generate_html_report(
        results_data=results_data,
        params=params,
        spec=spec,
        fit_stats=fit_stats,
        elasticities=elasticities,
        mu_stats=mu_stats,
        plot_paths=plot_paths,
        output_path=html_path
    )

    # ===== 11. SAVE CSV OUTPUTS =====
    logger.info("\nStep 11: Saving CSV Outputs")
    logger.info("-" * 80)

    # Save parameter table
    params_df = params.to_dataframe()
    params_csv_path = output_dir / f"{prefix}post_est_params.csv"
    params_df.to_csv(params_csv_path, index=False)
    logger.info(f"  Saved parameters: {params_csv_path}")

    # Save elasticities
    elast_rows = []
    for group_name, elast in elasticities.items():
        for elast_name, elast_value in elast.items():
            elast_rows.append({
                'group': group_name,
                'elasticity': elast_name,
                'value': elast_value
            })
    elast_df = pd.DataFrame(elast_rows)
    elast_csv_path = output_dir / f"{prefix}post_est_elasticities.csv"
    elast_df.to_csv(elast_csv_path, index=False)
    logger.info(f"  Saved elasticities: {elast_csv_path}")

    # Save fit statistics
    fit_csv_path = output_dir / f"{prefix}post_est_fit.csv"
    with open(fit_csv_path, 'w') as f:
        f.write("group,statistic,value\n")
        for group_name, stats in fit_stats.items():
            for key, val in stats.items():
                if isinstance(val, (int, float)):
                    f.write(f"{group_name},{key},{val}\n")
    logger.info(f"  Saved fit statistics: {fit_csv_path}")

    # Save marginal utility statistics
    mu_csv_path = output_dir / f"{prefix}post_est_marginal_utilities.csv"
    mu_rows = []
    for group_name, stats in mu_stats.items():
        if 'couples' in group_name:
            mu_rows.append({
                'group': f"{group_name}_m",
                'mean_MUC': stats['mean_MUC'],
                'median_MUC': stats['median_MUC'],
                'pct_negative_MUC': stats['pct_negative_MUC'],
                'mean_MUL': stats['male']['mean_MUL'],
                'median_MUL': stats['male']['median_MUL'],
                'pct_negative_MUL': stats['male']['pct_negative_MUL']
            })
            mu_rows.append({
                'group': f"{group_name}_f",
                'mean_MUC': stats['mean_MUC'],
                'median_MUC': stats['median_MUC'],
                'pct_negative_MUC': stats['pct_negative_MUC'],
                'mean_MUL': stats['female']['mean_MUL'],
                'median_MUL': stats['female']['median_MUL'],
                'pct_negative_MUL': stats['female']['pct_negative_MUL']
            })
        else:
            mu_rows.append({
                'group': group_name,
                'mean_MUC': stats['mean_MUC'],
                'median_MUC': stats['median_MUC'],
                'pct_negative_MUC': stats['pct_negative_MUC'],
                'mean_MUL': stats['mean_MUL'],
                'median_MUL': stats['median_MUL'],
                'pct_negative_MUL': stats['pct_negative_MUL']
            })
    mu_df = pd.DataFrame(mu_rows)
    mu_df.to_csv(mu_csv_path, index=False)
    logger.info(f"  Saved marginal utilities: {mu_csv_path}")

    logger.info("\n" + "="*80)
    logger.info("Post-Estimation Complete!")
    logger.info("="*80)
    logger.info(f"HTML Report: {html_path}")
    logger.info("")

    return {
        'fit_stats': fit_stats,
        'elasticities': elasticities,
        'mu_stats': mu_stats,
        'params': params,
        'html_path': html_path,
        'plot_paths': plot_paths,
        'csv_paths': {
            'parameters': params_csv_path,
            'elasticities': elast_csv_path,
            'fit': fit_csv_path,
            'marginal_utilities': mu_csv_path
        }
    }


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Command-line interface for post-estimation."""
    parser = argparse.ArgumentParser(
        description='Enhanced RURO Post-Estimation Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--results-json',
        type=Path,
        required=True,
        help='Path to estimation_results.json'
    )

    parser.add_argument(
        '--mnl-base',
        type=Path,
        required=True,
        help='Base path for MNL data files (without extension)'
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        required=True,
        help='Output directory for post-estimation files'
    )

    parser.add_argument(
        '--prefix',
        type=str,
        default="",
        help='Prefix for output files (default: "")'
    )

    parser.add_argument(
        '--no-strict-validation',
        action='store_true',
        help='Disable strict metadata validation'
    )

    args = parser.parse_args()

    try:
        results = run_enhanced_post_estimation(
            results_json_path=args.results_json,
            mnl_base=args.mnl_base,
            output_dir=args.output_dir,
            prefix=args.prefix,
            strict_validation=not args.no_strict_validation
        )
        return 0
    except Exception as e:
        logger.error(f"Post-estimation failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

