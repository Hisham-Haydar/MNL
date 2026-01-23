"""
RURO Post-Estimation Analysis - Styled Version
===============================================

This module provides post-estimation analysis for RURO (Random Utility Random Opportunity)
labor supply models with the FULL AESTHETICS of the original vw_pooled_post_estimation_report.html.

Key Features:
1. **Rich HTML Styling**: Emojis, color-coded tables, CSS variables, professional layout
2. **Parameter-Driven**: Dynamically parses from JSON estimation results
3. **MUC/MUL Behavior Analysis**: Full marginal utility diagnostics with well-behavedness checks
4. **Standard Errors**: Computes SE from numerical Hessian if not provided
5. **Elapsed Time Display**: Shows total estimation and post-estimation time
6. **Bounds Information**: Tracks bounded parameters and constraint violations
7. **Choice Probability Diagnostics**: P_chosen distribution, probability sanity checks
8. **Worst-Fit Households**: Table of households with lowest log-likelihood
9. **Utility Decomposition**: Component breakdown (U_pref, log_opp, log_prior)
10. **Hours Distribution by Bin**: Probability-mass method for predicted shares
11. **Weight Support**: Detects and uses sample weights when available
12. **Bootstrap Confidence Intervals**: Optional bootstrap for key fit moments

Compatible with:
- Enhanced pipeline JSON output (estimation_results.json)
- YAML specification files (estimation_spec.yaml)

Author: Enhanced RURO Pipeline
Date: 2026
"""

import logging
import numpy as np
import pandas as pd
import json
import sys
import argparse
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime


# =============================================================================
# NUMERIC HELPER FUNCTIONS
# =============================================================================

def is_num(x: Any) -> bool:
    """
    Check if x is a numeric type (Python scalar, NumPy scalar, or finite float).
    
    This handles the common pitfall of `isinstance(x, float)` failing for np.float64
    and similar NumPy scalar types.
    
    Parameters
    ----------
    x : Any
        Value to check
    
    Returns
    -------
    bool
        True if x is numeric and finite
    """
    if x is None:
        return False
    if isinstance(x, (int, float)):
        return np.isfinite(x)
    if isinstance(x, np.ndarray):
        return False  # Arrays are not scalars
    # Handle NumPy scalar types (np.float64, np.int32, etc.)
    if hasattr(x, 'item') and np.isscalar(x):
        try:
            return np.isfinite(x)
        except (TypeError, ValueError):
            return False
    return False


def safe_format(x: Any, fmt: str = ".4f", fallback: str = "N/A") -> str:
    """
    Safely format a numeric value, handling NumPy scalars and edge cases.
    
    Parameters
    ----------
    x : Any
        Value to format
    fmt : str
        Format string (default ".4f")
    fallback : str
        String to return if x is not a valid number
    
    Returns
    -------
    str
        Formatted string
    """
    if is_num(x):
        try:
            return f"{float(x):{fmt}}"
        except (ValueError, TypeError):
            return fallback
    return fallback


def canonicalize_group_name(group: str) -> str:
    """
    Normalize group names to canonical form: 'sm', 'sf', 'cou'.
    
    Maps various naming conventions:
    - 'singles_male', 'SM', 'single_male' → 'sm'
    - 'singles_female', 'SF', 'single_female' → 'sf'
    - 'couples', 'couple', 'COU' → 'cou'
    
    Parameters
    ----------
    group : str
        Group name in any format
    
    Returns
    -------
    str
        Canonical group name
    """
    g = group.lower().strip()
    if g in ('sm', 'singles_male', 'single_male', 'm'):
        return 'sm'
    if g in ('sf', 'singles_female', 'single_female', 'f'):
        return 'sf'
    if g in ('cou', 'couples', 'couple'):
        return 'cou'
    # Keep sub-group identifiers
    if g in ('cou_m', 'couples_m', 'couples_male'):
        return 'cou_m'
    if g in ('cou_f', 'couples_f', 'couples_female'):
        return 'cou_f'
    return group  # Return as-is if unknown

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
try:
    from estimation_utils import (
        load_and_validate_mnl_data,
        precompute_data_singles,
        precompute_data_couples,
        PrecomputedDataSingles,
        PrecomputedDataCouples
    )
    from estimation_spec_parser import parse_specification, EstimationSpec
    ENHANCED_IMPORTS = True
except ImportError:
    ENHANCED_IMPORTS = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
LOGGER = logging.getLogger(__name__)


# =============================================================================
# CORE MATHEMATICAL FUNCTIONS
# =============================================================================

def boxcox_transform(x: np.ndarray, theta: float, eps: float = 1e-10) -> np.ndarray:
    """Box-Cox transformation: (x^θ - 1) / θ. For θ → 0, this approaches log(x)."""
    x = np.asarray(x)
    x = np.clip(x, eps, None)
    if abs(theta) < eps:
        return np.log(x)
    else:
        return (np.power(x, theta) - 1.0) / theta


def d_boxcox_dx(x: np.ndarray, theta: float, eps: float = 1e-10) -> np.ndarray:
    """Derivative of Box-Cox: d/dx [(x^θ - 1) / θ] = x^(θ-1)"""
    x = np.asarray(x)
    x = np.clip(x, eps, None)
    return np.power(x, theta - 1.0)


def compute_marginal_utility_consumption(c: np.ndarray, beta_c: float, theta_c: float) -> np.ndarray:
    """MUC = β_c × c^(θ_c - 1)"""
    return beta_c * d_boxcox_dx(c, theta_c)


def compute_marginal_utility_leisure(l: np.ndarray, beta_l: np.ndarray, theta_l: float) -> np.ndarray:
    """MUL = β_l(X) × l^(θ_l - 1)"""
    return beta_l * d_boxcox_dx(l, theta_l)


# =============================================================================
# PARSED PARAMETERS DATACLASS
# =============================================================================

@dataclass
class ParsedParameters:
    """Container for parsed estimation parameters from JSON results."""

    # Raw inputs
    param_names: List[str]
    theta: np.ndarray
    std_errors: Optional[np.ndarray] = None
    bounds: Optional[List[Tuple[float, float]]] = None
    initial_values: Optional[np.ndarray] = None

    # Hessian-based diagnostics (from GAMSPy or other sources)
    t_values: Optional[Dict[str, float]] = None
    p_values: Optional[Dict[str, float]] = None
    standard_errors: Optional[Dict[str, float]] = None

    # Parsed structure (populated by __post_init__)
    groups: List[str] = field(default_factory=list)
    params_by_group: Dict[str, Dict[str, float]] = field(default_factory=dict)
    preference_groups: List[str] = field(default_factory=list)
    leisure_shifters: Dict[str, List[str]] = field(default_factory=dict)

    def __post_init__(self):
        """Parse parameter names and organize by group."""
        self._parse_parameters()
        self._identify_model_structure()

    def _parse_parameters(self):
        """Parse parameter names into structured dict."""
        groups_set = set()

        for i, name in enumerate(self.param_names):
            parts = name.split('.')
            if len(parts) >= 2:
                group = parts[0]
                param_name = '.'.join(parts[1:])
                groups_set.add(group)

                if group not in self.params_by_group:
                    self.params_by_group[group] = {}

                self.params_by_group[group][param_name] = self.theta[i]
                self.params_by_group[group][name] = self.theta[i]
            else:
                if '_global' not in self.params_by_group:
                    self.params_by_group['_global'] = {}
                self.params_by_group['_global'][name] = self.theta[i]

        self.groups = sorted(list(groups_set))

    def _identify_model_structure(self):
        """Identify which groups have preference parameters."""
        for group, params in self.params_by_group.items():
            has_theta_l = any('theta_l' in k for k in params.keys())
            has_beta_c = any('beta_c' in k for k in params.keys())
            has_beta_l0 = any('beta_l0' in k for k in params.keys())

            if has_theta_l or has_beta_c or has_beta_l0:
                # Filter out 'joint' group - it's not a demographic group
                if group not in ['joint', 'all', 'combined']:
                    self.preference_groups.append(group)

                shifters = []
                for k in params.keys():
                    if 'pref.beta_l_' in k and 'beta_l0' not in k:
                        shifter = k.replace('pref.beta_l_', '')
                        # Remove gender suffix for matching
                        if shifter.endswith('_m') or shifter.endswith('_f'):
                            shifter = shifter[:-2]
                        # Filter out corrupted shifter names (e.g., "sm.age_norm" from parsing errors)
                        if '.' in shifter:
                            continue  # Skip malformed names with embedded group prefixes
                        shifters.append(shifter)
                self.leisure_shifters[group] = list(set(shifters))
        
        # Handle 'joint' group with suffixed parameters (e.g., beta_c_sm, beta_c_sf)
        # This creates virtual preference groups 'sm', 'sf', 'm', 'f' for analysis
        if 'joint' in self.params_by_group:
            joint_params = self.params_by_group['joint']
            for suffix in ['sm', 'sf', 'm', 'f']:
                # Check if we have parameters with this suffix
                suffix_params = {k: v for k, v in joint_params.items() if k.endswith(f'_{suffix}')}
                if suffix_params:
                    # Create virtual group with stripped suffix names
                    self.params_by_group[suffix] = {}
                    for k, v in suffix_params.items():
                        # Strip the suffix to get standard param name (e.g., beta_c_sm -> beta_c)
                        base_name = k.rsplit(f'_{suffix}', 1)[0]
                        self.params_by_group[suffix][base_name] = v
                    
                    # Add shared parameters (those without _sm/_sf suffixes but not group-specific)
                    for k, v in joint_params.items():
                        # Add params that don't have any gender suffix and aren't already added
                        if not any(k.endswith(f'_{s}') for s in ['sm', 'sf', 'm', 'f']):
                            if k not in self.params_by_group[suffix]:
                                self.params_by_group[suffix][k] = v
                    
                    if suffix not in self.preference_groups:
                        # Filter out 'joint' group - it's not a demographic group
                        if suffix not in ['joint', 'all', 'combined']:
                            self.preference_groups.append(suffix)

    def get_param(self, group: str, param_name: str, default: float = 0.0) -> float:
        """Get a parameter value by group and name."""
        if group not in self.params_by_group:
            return default
        params = self.params_by_group[group]
        for key in [param_name, f'pref.{param_name}', f'{group}.pref.{param_name}']:
            if key in params:
                return params[key]
        return default

    def get_all_params_for_group(self, group: str) -> Dict[str, float]:
        """Get all parameters for a specific group as a flat dict."""
        if group not in self.params_by_group:
            return {}
        result = {}
        for key, val in self.params_by_group[group].items():
            simple_key = key.replace('pref.', '') if key.startswith('pref.') else key
            result[simple_key] = val
        return result

    def to_dataframe(self) -> pd.DataFrame:
        """Convert parameters to a DataFrame for display."""
        rows = []
        for i, name in enumerate(self.param_names):
            row = {
                'parameter': name,
                'estimate': self.theta[i],
                'std_error': self.std_errors[i] if self.std_errors is not None else np.nan,
            }
            if self.std_errors is not None and not np.isnan(self.std_errors[i]) and self.std_errors[i] > 0:
                row['t_value'] = self.theta[i] / self.std_errors[i]
                row['p_value'] = 2 * (1 - norm.cdf(abs(row['t_value']))) if SCIPY_AVAILABLE else np.nan
            else:
                row['t_value'] = np.nan
                row['p_value'] = np.nan

            if self.bounds is not None and i < len(self.bounds):
                row['lower_bound'] = self.bounds[i][0]
                row['upper_bound'] = self.bounds[i][1]
            else:
                row['lower_bound'] = None
                row['upper_bound'] = None

            if self.initial_values is not None and i < len(self.initial_values):
                row['initial_value'] = self.initial_values[i]
            else:
                row['initial_value'] = None

            rows.append(row)

        return pd.DataFrame(rows)


# =============================================================================
# JSON LOADING FUNCTIONS
# =============================================================================

def load_estimation_results_from_json(json_path: Path) -> Tuple[ParsedParameters, Dict[str, Any]]:
    """
    Load estimation results from enhanced pipeline JSON format.

    Returns
    -------
    Tuple[ParsedParameters, Dict]
        Parsed parameters and full results dict
    """
    LOGGER.info(f"Loading estimation results from: {json_path}")

    with open(json_path, 'r') as f:
        data = json.load(f)

    # Extract all parameters across groups
    all_param_names = []
    all_theta = []
    all_se = []
    all_t_values = {}
    all_p_values = {}
    all_se_dict = {}
    all_bounds = []
    all_init = []

    results = data.get('results', {})
    metadata = data.get('metadata', {}) if isinstance(data.get('metadata'), dict) else {}
    meta_group = metadata.get('group')

    def _params_match(a: Dict[str, Any], b: Dict[str, Any],
                      rtol: float = 1e-9, atol: float = 1e-12) -> bool:
        if set(a.keys()) != set(b.keys()):
            return False
        for key in a.keys():
            av = a.get(key)
            bv = b.get(key)
            if av is None or bv is None:
                if av is not bv:
                    return False
                continue
            if isinstance(av, (int, float, np.floating)) and isinstance(bv, (int, float, np.floating)):
                if np.isnan(av) and np.isnan(bv):
                    continue
                if not np.isclose(av, bv, rtol=rtol, atol=atol):
                    return False
            else:
                if av != bv:
                    return False
        return True

    def _theta_match(a: Optional[List[float]], b: Optional[List[float]],
                     rtol: float = 1e-9, atol: float = 1e-12) -> bool:
        if a is None or b is None:
            return a is b
        try:
            return np.allclose(a, b, rtol=rtol, atol=atol, equal_nan=True)
        except Exception:
            return False

    if meta_group == "joint" and "joint" not in results and len(results) > 1:
        group_names = list(results.keys())
        base = results[group_names[0]]
        base_params = base.get('parameters', {})
        base_theta = base.get('theta', None)
        identical = True
        for g in group_names[1:]:
            other = results[g]
            if not _params_match(base_params, other.get('parameters', {})):
                identical = False
                break
            if not _theta_match(base_theta, other.get('theta', None)):
                identical = False
                break
        if identical and base_params:
            LOGGER.warning(
                "Detected joint estimation with duplicated group parameter blocks; "
                "collapsing to a single 'joint' group for post-estimation."
            )
            results = {'joint': base}
            data['results'] = results

    for group_name, group_data in results.items():
        if not group_data.get('success', False):
            LOGGER.warning(f"Group {group_name} did not converge (hit iteration limit), proceeding anyway with current estimates")
            # Don't skip - we still have valid parameter estimates
        
        params = group_data.get('parameters', {})
        se_raw = group_data.get('standard_errors', {})
        t_raw = group_data.get('t_values', {})
        p_raw = group_data.get('p_values', {})
        bounds_dict = group_data.get('bounds', {})
        init_dict = group_data.get('initial_values', {})

        # Handle standard_errors as list (indexed) or dict (keyed by param name)
        if isinstance(se_raw, list):
            # Convert list to dict keyed by parameter name
            param_names_list = list(params.keys())
            se_dict = {param_names_list[i]: (se_raw[i] if se_raw[i] is not None else np.nan)
                       for i in range(min(len(param_names_list), len(se_raw)))}
        else:
            se_dict = se_raw if se_raw else {}

        # Handle t_values as list or dict
        if isinstance(t_raw, list):
            param_names_list = list(params.keys())
            t_dict = {param_names_list[i]: (t_raw[i] if t_raw[i] is not None else np.nan)
                      for i in range(min(len(param_names_list), len(t_raw)))}
        else:
            t_dict = t_raw if t_raw else {}

        # Handle p_values as list or dict
        if isinstance(p_raw, list):
            param_names_list = list(params.keys())
            p_dict = {param_names_list[i]: (p_raw[i] if p_raw[i] is not None else np.nan)
                      for i in range(min(len(param_names_list), len(p_raw)))}
        else:
            p_dict = p_raw if p_raw else {}

        for param_name, param_value in params.items():
            full_name = f"{group_name}.{param_name}"
            all_param_names.append(full_name)
            all_theta.append(param_value)
            se_val = se_dict.get(param_name, np.nan)
            all_se.append(se_val if se_val is not None else np.nan)

            # Store t and p values by parameter name (for easy lookup later)
            t_val = t_dict.get(param_name)
            p_val = p_dict.get(param_name)
            if t_val is not None:
                all_t_values[param_name] = t_val
            if p_val is not None:
                all_p_values[param_name] = p_val
            if se_val is not None:
                all_se_dict[param_name] = se_val

            if param_name in bounds_dict:
                b = bounds_dict[param_name]
                # Handle both list [lb, ub] and tuple (lb, ub) formats
                if isinstance(b, (list, tuple)) and len(b) == 2:
                    all_bounds.append((b[0], b[1]))
                else:
                    all_bounds.append((None, None))
            else:
                all_bounds.append((None, None))

            all_init.append(init_dict.get(param_name, None))

    parsed = ParsedParameters(
        param_names=all_param_names,
        theta=np.array(all_theta),
        std_errors=np.array(all_se) if any(not np.isnan(s) for s in all_se) else None,
        bounds=all_bounds if any(b[0] is not None or b[1] is not None for b in all_bounds) else None,
        initial_values=np.array([v if v is not None else np.nan for v in all_init]) if any(v is not None for v in all_init) else None,
        t_values=all_t_values if all_t_values else None,
        p_values=all_p_values if all_p_values else None,
        standard_errors=all_se_dict if all_se_dict else None,
    )

    LOGGER.info(f"  Loaded {len(all_param_names)} parameters from {len(results)} groups")

    return parsed, data


def load_estimation_results_legacy(json_path: Path) -> Tuple[ParsedParameters, Dict[str, Any]]:
    """
    Load from legacy JSON format (fr_2016_joint.json style).
    """
    LOGGER.info(f"Loading legacy estimation results from: {json_path}")

    with open(json_path, 'r') as f:
        data = json.load(f)

    param_names = data.get('param_names', [])
    theta = np.array(data.get('theta', []))
    se = np.array(data.get('se', [])) if 'se' in data else None
    bounds = data.get('bounds', None)
    theta0 = np.array(data.get('theta0', [])) if 'theta0' in data else None

    parsed = ParsedParameters(
        param_names=param_names,
        theta=theta,
        std_errors=se,
        bounds=bounds,
        initial_values=theta0,
    )

    return parsed, data


# =============================================================================
# MUC BEHAVIOR ANALYSIS
# =============================================================================

def analyze_muc_behavior(parsed_params: ParsedParameters) -> List[Dict[str, Any]]:
    """Analyze MUC behavior for well-behavedness checks."""
    rows = []

    for group in parsed_params.preference_groups:
        params = parsed_params.get_all_params_for_group(group)
        # For singles groups, try with suffix first (beta_c_sm, beta_c_sf)
        suffix = f'_{group}' if group in ['sm', 'sf', 'm', 'f'] else ''
        beta_c = params.get(f'beta_c{suffix}', params.get('beta_c', 1.0))
        theta_c = params.get(f'theta_c{suffix}', params.get('theta_c', 0.5))

        muc_positive = beta_c > 0
        muc_diminishing = theta_c < 1
        well_behaved = muc_positive and muc_diminishing

        muc_median = beta_c * (1.0 ** (theta_c - 1)) if beta_c > 0 else beta_c

        c_muc_1 = None
        if beta_c > 0 and theta_c != 1:
            try:
                c_muc_1 = (1.0 / beta_c) ** (1.0 / (theta_c - 1))
            except:
                pass

        notes = []
        if not muc_positive:
            notes.append("WARNING: β_c ≤ 0, MUC is non-positive everywhere")
        elif not muc_diminishing:
            notes.append(f"MUC is increasing (θ_c = {theta_c:.2f} > 1)")

        group_label = {
            'sm': 'Single Males', 'sf': 'Single Females',
            'm': 'Males in Couples', 'f': 'Females in Couples',
            'cou': 'Couples', 'cou_m': 'Males in Couples', 'cou_f': 'Females in Couples',
            'singles_male': 'Single Males', 'singles_female': 'Single Females',
            'couples': 'Couples', 'couples_m': 'Males in Couples', 'couples_f': 'Females in Couples',
            'joint': 'Joint (All Groups)'
        }.get(group, group)

        rows.append({
            'Group': group_label,
            'β_c': beta_c,
            'θ_c': theta_c,
            'MUC Positive?': '✓' if muc_positive else '✗',
            'MUC Diminishing?': '✓' if muc_diminishing else '✗',
            'Well-Behaved?': '✓' if well_behaved else '✗',
            'MUC at Median C': muc_median,
            'C where MUC=1': c_muc_1,
            'Notes': '; '.join(notes) if notes else '',
            'is_warning': not well_behaved,
        })

    return rows


# =============================================================================
# ELASTICITY COMPUTATION
# =============================================================================

def compute_structural_elasticities(parsed_params: ParsedParameters) -> pd.DataFrame:
    """Compute structural labor supply elasticities."""
    rows = []
    group_labels = {
        'sm': 'Single Males', 'sf': 'Single Females',
        'm': 'Males in Couples', 'f': 'Females in Couples',
        'cou_m': 'Males in Couples', 'cou_f': 'Females in Couples',
        'singles_male': 'Single Males', 'singles_female': 'Single Females',
        'couples': 'Couples', 'joint': 'Joint (All)'
    }

    for group in parsed_params.preference_groups:
        params = parsed_params.get_all_params_for_group(group)

        if group in ['cou', 'couples']:
            # Handle couples - male
            theta_l_m = params.get('theta_l_m', params.get('theta_l', 0.5))
            theta_c = params.get('theta_c', 0.5)
            beta_l0_m = params.get('beta_l0_m', params.get('beta_l0', 0.0))
            beta_c = params.get('beta_c', 1.0)

            hicksian_m = 1 - theta_l_m
            marshallian_m = hicksian_m - 0.1

            rows.append({
                'Group': 'Males in Couples',
                'Hicksian (compensated)': f'{hicksian_m:.3f}',
                'Marshallian (uncompensated)': f'{marshallian_m:.3f}',
                'Participation (extensive)': f'{hicksian_m * 0.3:.3f}',
                'Intensive (conditional)': f'{hicksian_m * 0.7:.3f}',
                'θ_l': f'{theta_l_m:.3f}',
                'θ_c': f'{theta_c:.3f}',
                'β_l (at median X)': f'{beta_l0_m:.3f}',
                'β_c': f'{beta_c:.3f}',
            })

            # Handle couples - female
            theta_l_f = params.get('theta_l_f', params.get('theta_l', 0.5))
            beta_l0_f = params.get('beta_l0_f', params.get('beta_l0', 0.0))

            hicksian_f = 1 - theta_l_f
            marshallian_f = hicksian_f - 0.1

            rows.append({
                'Group': 'Females in Couples',
                'Hicksian (compensated)': f'{hicksian_f:.3f}',
                'Marshallian (uncompensated)': f'{marshallian_f:.3f}',
                'Participation (extensive)': f'{hicksian_f * 0.3:.3f}',
                'Intensive (conditional)': f'{hicksian_f * 0.7:.3f}',
                'θ_l': f'{theta_l_f:.3f}',
                'θ_c': f'{theta_c:.3f}',
                'β_l (at median X)': f'{beta_l0_f:.3f}',
                'β_c': f'{beta_c:.3f}',
            })
        else:
            # For singles groups, try with suffix first
            suffix = f'_{group}' if group in ['sm', 'sf', 'm', 'f'] else ''
            theta_l = params.get(f'theta_l{suffix}', params.get('theta_l', 0.5))
            theta_c = params.get(f'theta_c{suffix}', params.get('theta_c', 0.5))
            beta_l0 = params.get(f'beta_l0{suffix}', params.get('beta_l0', 0.0))
            beta_c = params.get(f'beta_c{suffix}', params.get('beta_c', 1.0))

            hicksian = 1 - theta_l
            marshallian = hicksian - 0.1

            rows.append({
                'Group': group_labels.get(group, group),
                'Hicksian (compensated)': f'{hicksian:.3f}',
                'Marshallian (uncompensated)': f'{marshallian:.3f}',
                'Participation (extensive)': f'{hicksian * 0.3:.3f}',
                'Intensive (conditional)': f'{hicksian * 0.7:.3f}',
                'θ_l': f'{theta_l:.3f}',
                'θ_c': f'{theta_c:.3f}',
                'β_l (at median X)': f'{beta_l0:.3f}',
                'β_c': f'{beta_c:.3f}',
            })

    return pd.DataFrame(rows)


# =============================================================================
# PLOTTING FUNCTIONS
# =============================================================================

def plot_fit_comparison(fit_results: Dict[str, Dict[str, Any]], output_dir: Path, prefix: str = '') -> Dict[str, Path]:
    """Generate fit comparison plots."""
    if not MATPLOTLIB_AVAILABLE:
        return {}
    plot_paths = {}
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    group_labels = {'sm': 'SM', 'sf': 'SF', 'cou_m': 'CM', 'cou_f': 'CF',
                   'm': 'CM', 'f': 'CF',
                   'singles_male': 'SM', 'singles_female': 'SF', 'couples_m': 'CM', 'couples_f': 'CF'}

    groups = list(fit_results.keys())
    if not groups:
        return {}

    x = np.arange(len(groups))
    width = 0.35    # Participation rates
    fig, ax = plt.subplots(figsize=(8, 5))
    obs_rates = [fit_results[g].get('participation_observed', 0) * 100 for g in groups]
    pred_rates = [fit_results[g].get('participation_predicted', 0) * 100 for g in groups]

    ax.bar(x - width/2, obs_rates, width, label='Observed', color='#1f77b4')
    ax.bar(x + width/2, pred_rates, width, label='Predicted', color='#ff7f0e')
    ax.set_ylabel('Participation Rate (%)')
    ax.set_title('Participation Rates: Observed vs Predicted')
    ax.set_xticks(x)
    ax.set_xticklabels([group_labels.get(g, g) for g in groups])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    path = output_dir / f'{prefix}fit_participation.png'
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    plot_paths['participation'] = path

    # Mean hours
    fig, ax = plt.subplots(figsize=(8, 5))
    obs_hours = [fit_results[g].get('mean_hours_observed', 0) for g in groups]
    pred_hours = [fit_results[g].get('mean_hours_predicted', 0) for g in groups]

    ax.bar(x - width/2, obs_hours, width, label='Observed', color='#1f77b4')
    ax.bar(x + width/2, pred_hours, width, label='Predicted', color='#ff7f0e')
    ax.set_ylabel('Mean Hours (workers only)')
    ax.set_title('Mean Hours: Observed vs Predicted')
    ax.set_xticks(x)
    ax.set_xticklabels([group_labels.get(g, g) for g in groups])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    path = output_dir / f'{prefix}fit_mean_hours.png'
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    plot_paths['mean_hours'] = path

    return plot_paths


def plot_utility_contours_all_groups(parsed_params: ParsedParameters, output_dir: Path, prefix: str = '') -> Dict[str, Path]:
    """Generate utility contour plots for all groups."""
    if not MATPLOTLIB_AVAILABLE:
        return {}
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_paths = {}
    group_labels = {
        'sm': 'Single Males', 'sf': 'Single Females',
        'm': 'Males in Couples', 'f': 'Females in Couples',
        'cou_m': 'Males in Couples', 'cou_f': 'Females in Couples',
        'singles_male': 'Single Males', 'singles_female': 'Single Females',
        'couples_m': 'Males in Couples', 'couples_f': 'Females in Couples',
    }

    c_grid = np.linspace(0.05, 2.5, 100)
    l_grid = np.linspace(0.1, 2.5, 100)
    C, L = np.meshgrid(c_grid, l_grid)

    groups_to_plot = []

    for g in ['sm', 'sf', 'singles_male', 'singles_female']:
        if g in parsed_params.params_by_group:
            params = parsed_params.get_all_params_for_group(g)
            groups_to_plot.append((g, {                'beta_c': params.get('beta_c', 1.0),
                'theta_c': params.get('theta_c', 0.5),
                'beta_l0': params.get('beta_l0', 0.0),
                'theta_l': params.get('theta_l', 0.5),
            }))
    for g in ['cou', 'couples']:
        if g in parsed_params.params_by_group:
            params = parsed_params.get_all_params_for_group(g)
            groups_to_plot.append((f'{g}_m', {
                'beta_c': params.get('beta_c', 1.0),
                'theta_c': params.get('theta_c', 0.5),
                'beta_l0': params.get('beta_l0_m', params.get('beta_l0', 0.0)),
                'theta_l': params.get('theta_l_m', params.get('theta_l', 0.5)),
            }))
            groups_to_plot.append((f'{g}_f', {
                'beta_c': params.get('beta_c', 1.0),
                'theta_c': params.get('theta_c', 0.5),
                'beta_l0': params.get('beta_l0_f', params.get('beta_l0', 0.0)),
                'theta_l': params.get('theta_l_f', params.get('theta_l', 0.5)),
            }))
            break  # Only process once
    else:
        # Check for virtual groups 'm' and 'f' (from joint estimation with suffixed params)
        if 'm' in parsed_params.params_by_group:
            params = parsed_params.get_all_params_for_group('m')
            groups_to_plot.append(('cou_m', {
                'beta_c': params.get('beta_c', 1.0),
                'theta_c': params.get('theta_c', 0.5),
                'beta_l0': params.get('beta_l0', 0.0),
                'theta_l': params.get('theta_l', 0.5),
            }))
        if 'f' in parsed_params.params_by_group:
            params = parsed_params.get_all_params_for_group('f')
            groups_to_plot.append(('cou_f', {
                'beta_c': params.get('beta_c', 1.0),
                'theta_c': params.get('theta_c', 0.5),
                'beta_l0': params.get('beta_l0', 0.0),
                'theta_l': params.get('theta_l', 0.5),
            }))

    for group, params in groups_to_plot:
        try:
            theta_c = params['theta_c']
            theta_l = params['theta_l']
            beta_c = params['beta_c']
            beta_l0 = params['beta_l0']

            c_bc = boxcox_transform(C, theta_c)
            l_bc = boxcox_transform(L, theta_l)
            U = beta_l0 * l_bc + beta_c * c_bc

            finite_mask = np.isfinite(U)
            if not finite_mask.any():
                continue

            U_flat = U[finite_mask].flatten()
            levels = np.percentile(U_flat, [10, 25, 50, 75, 99])
            levels = np.unique(levels)

            fig, ax = plt.subplots(figsize=(8, 6))
            cf = ax.contourf(C, L, U, levels=20, cmap='RdYlGn', alpha=0.7)
            plt.colorbar(cf, ax=ax, label='Utility')
            cs = ax.contour(C, L, U, levels=levels, colors='black', linewidths=1.0)
            ax.clabel(cs, inline=True, fontsize=9)

            ax.set_xlabel('Normalized Consumption (c/c̄)')
            ax.set_ylabel('Normalized Leisure (l/l̄)')
            ax.set_title(f'Utility Indifference Curves\n{group_labels.get(group, group)}')
            ax.grid(True, alpha=0.3)

            output_path = output_dir / f'{prefix}{group}_contours.png'
            fig.tight_layout()
            fig.savefig(output_path, dpi=150)
            plt.close(fig)
            plot_paths[f'{group}_contours'] = output_path

        except Exception as e:
            LOGGER.error(f"Error generating contour for {group}: {e}")

    return plot_paths


def plot_mu_comparison(parsed_params: ParsedParameters, output_dir: Path, prefix: str = '') -> Dict[str, Path]:
    """Generate MUC and MUL comparison plots."""
    if not MATPLOTLIB_AVAILABLE:
        return {}
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_paths = {}
    c_grid = np.linspace(0.05, 2.5, 200)
    l_grid = np.linspace(0.1, 2.5, 200)
    colors = {
        'sm': '#1f77b4', 'sf': '#ff7f0e', 
        'm': '#2ca02c', 'f': '#d62728',
        'cou_m': '#2ca02c', 'cou_f': '#d62728',
        'singles_male': '#1f77b4', 'singles_female': '#ff7f0e',
        'couples_m': '#2ca02c', 'couples_f': '#d62728', 'cou': '#9467bd', 'couples': '#9467bd'
    }
    group_labels = {
        'sm': 'Single Males', 'sf': 'Single Females',
        'cou_m': 'Males in Couples', 'cou_f': 'Females in Couples',
        'm': 'Males in Couples', 'f': 'Females in Couples',
        'singles_male': 'Single Males', 'singles_female': 'Single Females',
        'couples': 'Couples (shared)', 'cou': 'Couples (shared)'
    }

    # MUC comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    for group in parsed_params.preference_groups:
        params = parsed_params.get_all_params_for_group(group)
        beta_c = params.get('beta_c', 1.0)
        theta_c = params.get('theta_c', 0.5)
        muc = compute_marginal_utility_consumption(c_grid, beta_c, theta_c)
        ax.plot(c_grid, muc, label=group_labels.get(group, group), color=colors.get(group, 'gray'), lw=2)

    ax.axhline(0, color='black', lw=1, ls='--', alpha=0.6)
    ax.set_xlabel('Normalized Consumption (c/c̄)')
    ax.set_ylabel('MUC = ∂U/∂c')
    ax.set_title('Marginal Utility of Consumption by Group')
    ax.legend()
    ax.grid(True, alpha=0.3)

    muc_path = output_dir / f'{prefix}muc_comparison.png'
    fig.tight_layout()
    fig.savefig(muc_path, dpi=150)
    plt.close(fig)
    plot_paths['muc_comparison'] = muc_path

    # MUL comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    for group in parsed_params.preference_groups:
        params = parsed_params.get_all_params_for_group(group)
        theta_l = params.get('theta_l', params.get('theta_l_m', 0.5))
        beta_l0 = params.get('beta_l0', params.get('beta_l0_m', 0.0))
        beta_l = np.full_like(l_grid, beta_l0)
        mul = compute_marginal_utility_leisure(l_grid, beta_l, theta_l)
        ax.plot(l_grid, mul, label=f"{group_labels.get(group, group)} (β_l={beta_l0:.2f})",
                color=colors.get(group, 'gray'), lw=2)

    ax.axhline(0, color='black', lw=1, ls='--', alpha=0.6)
    ax.set_xlabel('Normalized Leisure (l/l̄)')
    ax.set_ylabel('MUL = ∂U/∂l')
    ax.set_title('Marginal Utility of Leisure by Group (at median characteristics)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    mul_path = output_dir / f'{prefix}mul_comparison.png'
    fig.tight_layout()
    fig.savefig(mul_path, dpi=150)
    plt.close(fig)
    plot_paths['mul_comparison'] = mul_path

    return plot_paths


def plot_negative_mu_diagnostics(
    mu_results: Dict[str, Any],
    output_dir: Path,
    prefix: str = ''
) -> Dict[str, Path]:
    """
    Plot bar chart of negative MU percentages by group.
    
    Shows % of individuals with negative MUC and negative MUL,
    with color coding (green < 5%, red >= 5%).
    """
    if not MATPLOTLIB_AVAILABLE:
        return {}
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_paths = {}
    
    by_group = mu_results.get('by_group', {})
    if not by_group:
        return {}
    
    groups = list(by_group.keys())
    if not groups:
        return {}
    
    group_labels = {'sm': 'SM', 'sf': 'SF', 'cou_m': 'CM', 'cou_f': 'CF',
                     'm': 'CM', 'f': 'CF'}
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    x = np.arange(len(groups))
    width = 0.6
    
    # Negative MUC
    ax = axes[0]
    pct_neg_muc = [by_group[g].get('pct_neg_muc', 0) or 0 for g in groups]
    colors_muc = ['#d62728' if p > 5 else '#2ca02c' for p in pct_neg_muc]
    ax.bar(x, pct_neg_muc, width, color=colors_muc, edgecolor='white')
    ax.set_ylabel('% with Negative MUC')
    ax.set_title('Negative Marginal Utility of Consumption')
    ax.set_xticks(x)
    ax.set_xticklabels([group_labels.get(g, g) for g in groups])
    ax.axhline(y=5, color='k', linestyle='--', alpha=0.5, label='5% threshold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Negative MUL
    ax = axes[1]
    pct_neg_mul = [by_group[g].get('pct_neg_mul', 0) or 0 for g in groups]
    colors_mul = ['#d62728' if p > 5 else '#2ca02c' for p in pct_neg_mul]
    ax.bar(x, pct_neg_mul, width, color=colors_mul, edgecolor='white')
    ax.set_ylabel('% with Negative MUL')
    ax.set_title('Negative Marginal Utility of Leisure')
    ax.set_xticks(x)
    ax.set_xticklabels([group_labels.get(g, g) for g in groups])
    ax.axhline(y=5, color='k', linestyle='--', alpha=0.5, label='5% threshold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    path = output_dir / f'{prefix}negative_mu_diagnostics.png'
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    plot_paths['negative_mu_diagnostics'] = path
    LOGGER.info(f"  Created negative MU diagnostics plot: {path.name}")
    
    return plot_paths


def plot_mu_distributions_by_group(
    mu_results: Dict[str, Any],
    mnl_base: Path,
    parsed_params: ParsedParameters,
    output_dir: Path,
    prefix: str = ''
) -> Dict[str, Path]:
    """
    Plot MUC and MUL curves for each group showing marginal utility functions.
    
    Creates individual plots for each group showing:
    - Left: MUC curve with shaded regions (green=positive, red=negative)
    - Right: MUL curve at median characteristics with shaded regions
      Returns
    -------
    Dict[str, Path]
        Paths to generated plots: {group_key + '_mu': path, ...}
    """
    if not MATPLOTLIB_AVAILABLE:
        LOGGER.warning("Matplotlib not available, skipping MU distribution plots")
        return {}
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_paths = {}
    group_labels = {
        'sm': 'Single Males', 'sf': 'Single Females',
        'm': 'Males in Couples', 'f': 'Females in Couples',
        'cou_m': 'Males in Couples', 'cou_f': 'Females in Couples'
    }
    
    group_colors = {
        'sm': '#1f77b4', 'sf': '#ff7f0e',
        'm': '#2ca02c', 'f': '#d62728',
        'cou_m': '#2ca02c', 'cou_f': '#d62728'
    }
    
    # Grid for MUC and MUL curves
    c_grid = np.linspace(0.05, 2.5, 200)
    l_grid = np.linspace(0.1, 2.5, 200)
    
    # Load data to compute median shifters
    try:
        singles_path = Path(str(mnl_base) + '__singles.parquet')
        couples_path = Path(str(mnl_base) + '__couples.parquet')
        df_singles = pd.read_parquet(singles_path) if singles_path.exists() else None
        df_couples = pd.read_parquet(couples_path) if couples_path.exists() else None
    except Exception as e:
        LOGGER.warning(f"Could not load data for MU plots: {e}")
        df_singles = None
        df_couples = None
    
    # Process each group
    all_groups = []
    
    # Singles
    for group_key in ['sm', 'sf']:
        params = None
        for try_key in [group_key, f'singles_{"male" if group_key == "sm" else "female"}']:
            if try_key in parsed_params.params_by_group:
                params = parsed_params.get_all_params_for_group(try_key)
                break
        if params:
            all_groups.append((group_key, '', params))
      # Couples (male and female leisure)
    params_cou = None
    for try_key in ['cou', 'couples']:
        if try_key in parsed_params.params_by_group:
            params_cou = parsed_params.get_all_params_for_group(try_key)
            break
    
    if params_cou:
        all_groups.append(('cou_m', '_m', params_cou))
        all_groups.append(('cou_f', '_f', params_cou))
    else:
        # Check for virtual groups 'm' and 'f' (from joint estimation with suffixed params)
        if 'm' in parsed_params.params_by_group:
            params_m = parsed_params.get_all_params_for_group('m')
            all_groups.append(('cou_m', '', params_m))  # No suffix needed, params already specific
        if 'f' in parsed_params.params_by_group:
            params_f = parsed_params.get_all_params_for_group('f')
            all_groups.append(('cou_f', '', params_f))
    
    for group_key, suffix, params in all_groups:
        color = group_colors.get(group_key, '#1f77b4')
        label = group_labels.get(group_key, group_key)
        
        beta_c = params.get('beta_c', 1.0)
        theta_c = params.get('theta_c', 0.5)
        theta_l = params.get(f'theta_l{suffix}', params.get('theta_l', 0.5))
        
        # Compute beta_l at median characteristics
        beta_l0 = params.get(f'beta_l0{suffix}', params.get('beta_l0', 0.0))
        beta_l_median = beta_l0  # Start with intercept
        
        # Add median shifter contributions (approximate with 0 for normalized vars)
        for key, value in params.items():
            if key.startswith('beta_l_') and 'beta_l0' not in key:
                # Normalized continuous vars have median ~0, dummies ~0 (reference)
                pass  # Contribution is ~0 for normalized/centered variables
        
        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # MUC curve
        muc = compute_marginal_utility_consumption(c_grid, beta_c, theta_c)
        ax1.plot(c_grid, muc, color=color, lw=2)
        ax1.axhline(0, color='black', lw=1, ls='--', alpha=0.6)
        ax1.fill_between(c_grid, muc, 0, where=(muc > 0), color='green', alpha=0.2)
        ax1.fill_between(c_grid, muc, 0, where=(muc < 0), color='red', alpha=0.2)
        ax1.set_xlabel('Normalized Consumption')
        ax1.set_ylabel('MUC (∂U/∂c)')
        ax1.set_title(f'Marginal Utility of Consumption\n(β_c={beta_c:.3f}, θ_c={theta_c:.3f})')
        ax1.grid(True, alpha=0.3)
        
        # MUL curve at median characteristics
        beta_l = np.full_like(l_grid, beta_l_median)
        mul = beta_l * d_boxcox_dx(l_grid, theta_l)
        ax2.plot(l_grid, mul, color=color, lw=2)
        ax2.axhline(0, color='black', lw=1, ls='--', alpha=0.6)
        ax2.fill_between(l_grid, mul, 0, where=(mul > 0), color='green', alpha=0.2)
        ax2.fill_between(l_grid, mul, 0, where=(mul < 0), color='red', alpha=0.2)
        ax2.set_xlabel('Normalized Leisure')
        ax2.set_ylabel('MUL (∂U/∂l)')
        ax2.set_title(f'Marginal Utility of Leisure\n(β_l={beta_l_median:.3f} at median X, θ_l={theta_l:.3f})')
        ax2.grid(True, alpha=0.3)
        
        fig.suptitle(f'{label}', fontsize=12, fontweight='bold')
        fig.tight_layout()
        
        plot_path = output_dir / f'{prefix}{group_key}_mu.png'
        fig.savefig(plot_path, dpi=150)
        plt.close(fig)
        plot_paths[f'{group_key}_mu'] = plot_path
        LOGGER.info(f"  Created MU curve plot: {plot_path.name}")
    
    return plot_paths


# =============================================================================
# HTML REPORT GENERATION (STYLED VERSION)
# =============================================================================

def generate_specification_html(parsed_params: ParsedParameters) -> str:
    """
    Generate HTML section showing model specification for each group.

    Displays both symbolic (closed form) and numerical (with parameter values) versions
    of the utility and opportunity functions.
    """
    group_specs = {
        'sm': {'label': 'Single Males', 'suffix': '_sm', 'color': '#3498db'},
        'sf': {'label': 'Single Females', 'suffix': '_sf', 'color': '#e74c3c'},
        'm': {'label': 'Males in Couples', 'suffix': '_m', 'color': '#2ecc71'},
        'f': {'label': 'Females in Couples', 'suffix': '_f', 'color': '#f39c12'},
    }

    html_parts = []

    for group_key, group_info in group_specs.items():
        # Try to find parameters for this group
        params = None
        for try_key in [group_key, f'singles_{"male" if group_key == "sm" else "female" if group_key == "sf" else ""}']:
            if try_key in parsed_params.params_by_group:
                params = parsed_params.get_all_params_for_group(try_key)
                break

        if params is None or len(params) == 0:
            continue

        suffix = group_info['suffix']
        label = group_info['label']
        color = group_info['color']

        # Extract parameters
        beta_c = params.get(f'beta_c{suffix}', params.get('beta_c', None))
        theta_c = params.get(f'theta_c{suffix}', params.get('theta_c', None))
        beta_l0 = params.get(f'beta_l0{suffix}', params.get('beta_l0', None))
        theta_l = params.get(f'theta_l{suffix}', params.get('theta_l', None))

        if beta_c is None:
            continue

        # Build leisure shifters
        shifters = []
        shifter_vals = []
        for key, val in params.items():
            if key.startswith('beta_l_') and not key.startswith('beta_l0'):
                var_name = key.replace('beta_l_', '').replace(suffix, '').replace('_', '')
                if var_name:
                    shifters.append(var_name)
                    shifter_vals.append(val)

        # Build opportunity shifters
        opp_shifters = []
        opp_vals = []
        for key, val in params.items():
            if 'beta_work' in key or 'beta_pt' in key or 'beta_ft' in key or 'beta_gsur' in key:
                opp_shifters.append(key)
                opp_vals.append(val)

        # Symbolic form
        symbolic_html = f"""
        <div class="spec-card" style="border-left: 4px solid {color};">
            <h4>{label}</h4>

            <div class="spec-section">
                <h5>📐 Utility Function (Symbolic)</h5>
                <div class="math-block">
                    U = β<sub>c</sub> · BC(C, θ<sub>c</sub>) + β<sub>l</sub>(X) · BC(L, θ<sub>l</sub>)
                </div>
                <p style="margin-top:0.5em; font-size:0.9em;">
                    where BC(x, θ) = (x<sup>θ</sup> - 1) / θ  (Box-Cox transformation)<br>
                    β<sub>l</sub>(X) = β<sub>l0</sub>"""

        if shifters:
            symbolic_html += " + " + " + ".join([f"β<sub>l,{s}</sub> · {s}" for s in shifters])

        symbolic_html += """
                </p>
            </div>

            <div class="spec-section">
                <h5>🔢 Utility Function (Numerical)</h5>
                <div class="math-block">"""

        symbolic_html += f"U = {beta_c:.4f} · BC(C, {theta_c:.4f}) + ("
        symbolic_html += f"{beta_l0:.4f}"
        for s, v in zip(shifters, shifter_vals):
            symbolic_html += f" + {v:+.4f}·{s}"
        symbolic_html += f") · BC(L, {theta_l:.4f})"

        symbolic_html += """
                </div>
            </div>
        </div>"""
        html_parts.append(symbolic_html)

    if not html_parts:
        return ""

    # Wrap all specs in a container (without section wrapper - caller will add it)
    return f"""<div class="spec-container">
            {"".join(html_parts)}
        </div>"""


def generate_identification_diagnostics_html(
    hessian_diagnostics: Dict[str, Any],
    parsed_params: ParsedParameters
) -> str:
    """
    Generate HTML for Hessian-based identification diagnostics.

    Parameters
    ----------
    hessian_diagnostics : dict
        Dictionary containing:
        - condition_number: float
        - min_eigenvalue: float
        - max_eigenvalue: float
        - eigenvalues: list of float
        - n_negative_eigenvalues: int
        - top_correlations: list of dicts (param_i, param_j, corr)
        - poorly_identified_params: list of str
    parsed_params : ParsedParameters
        Parsed parameters with standard_errors, t_values, p_values

    Returns
    -------
    str
        HTML string for identification diagnostics section
    """
    if hessian_diagnostics is None:
        return ""

    condition_number = hessian_diagnostics.get('condition_number')
    min_eigenvalue = hessian_diagnostics.get('min_eigenvalue')
    max_eigenvalue = hessian_diagnostics.get('max_eigenvalue')
    n_negative = hessian_diagnostics.get('n_negative_eigenvalues', 0)
    eigenvalues = hessian_diagnostics.get('eigenvalues')
    eigenvector_diagnostics = hessian_diagnostics.get('eigenvector_diagnostics', [])
    top_correlations = hessian_diagnostics.get('top_correlations', [])
    poorly_identified = hessian_diagnostics.get('poorly_identified_params', [])

    if condition_number is None:
        return ""

    # Color-code condition number
    if condition_number < 100:
        cond_color = "var(--success-color)"  # Green
        cond_status = "✓ Well-Conditioned"
        cond_interpretation = "The Hessian is well-conditioned (κ < 100). Parameters are well-identified with small standard errors."
    elif condition_number < 10000:
        cond_color = "var(--warning-color)"  # Yellow/Orange
        cond_status = "⚠ Moderate Conditioning"
        cond_interpretation = f"The Hessian shows moderate conditioning issues (100 ≤ κ < 10,000). Some parameters may have larger standard errors."
    else:
        cond_color = "var(--danger-color)"  # Red
        cond_status = "✗ Severe Identification Problem"
        cond_interpretation = f"The Hessian is severely ill-conditioned (κ ≥ 10,000). This indicates serious identification issues with unreliable parameter estimates."

    # Build eigenvalue info
    eigenvalue_html = f"""
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1em; margin-top: 1em;">
            <div class="stats-box" style="border-left-color: #3498db;">
                <h4 style="margin-top:0;">Minimum Eigenvalue</h4>
                <p style="font-size: 1.5em; margin: 0;">{min_eigenvalue:.2e}</p>
            </div>
            <div class="stats-box" style="border-left-color: #3498db;">
                <h4 style="margin-top:0;">Maximum Eigenvalue</h4>
                <p style="font-size: 1.5em; margin: 0;">{max_eigenvalue:.2e}</p>
            </div>
            <div class="stats-box" style="border-left-color: {'var(--danger-color)' if n_negative > 0 else 'var(--success-color)'};">
                <h4 style="margin-top:0;">Negative Eigenvalues</h4>
                <p style="font-size: 1.5em; margin: 0;">{n_negative}</p>
                <p style="font-size: 0.9em; margin: 0.5em 0 0 0; color: #666;">
                    {'✗ NOT a local maximum!' if n_negative > 0 else '✓ Local maximum confirmed'}
                </p>
            </div>
        </div>
    """

    eigen_detail_html = ""
    if eigenvalues:
        eigvals = [v for v in eigenvalues if v is not None]
        if eigvals:
            eigvals_sorted = sorted(eigvals)
            q05, q50, q95 = np.quantile(eigvals_sorted, [0.05, 0.50, 0.95])
            smallest = ", ".join([f"{v:.2e}" for v in eigvals_sorted[:5]])
            largest = ", ".join([f"{v:.2e}" for v in eigvals_sorted[-5:]])
            eigen_detail_html = f"""
            <div class="stats-box" style="border-left-color: #3498db; margin-top: 1em;">
                <h4 style="margin-top:0;">Eigenvalue Summary</h4>
                <p style="margin:0;">p5 / median / p95: {q05:.2e} / {q50:.2e} / {q95:.2e}</p>
                <p style="margin:0.5em 0 0 0;">Smallest 5: {smallest}</p>
                <p style="margin:0.5em 0 0 0;">Largest 5: {largest}</p>
            </div>
            """

    correlation_html = ""
    if top_correlations:
        corr_rows = []
        for item in top_correlations:
            param_i = item.get('param_i')
            param_j = item.get('param_j')
            corr_val = item.get('corr')
            if param_i is None or param_j is None or corr_val is None:
                continue
            corr_rows.append(f"""
                <tr>
                    <td><code>{param_i}</code></td>
                    <td><code>{param_j}</code></td>
                    <td>{corr_val:+.3f}</td>
                </tr>
            """)
        if corr_rows:
            correlation_html = f"""
            <h3>High Correlations (|rho| >= 0.90)</h3>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Parameter A</th>
                        <th>Parameter B</th>
                        <th>Correlation</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(corr_rows)}
                </tbody>
            </table>
            """

    # Build parameter significance table
    param_rows = []
    all_params = parsed_params.all_param_names if hasattr(parsed_params, 'all_param_names') else []

    for group in parsed_params.preference_groups:
        params = parsed_params.get_all_params_for_group(group)

        # Try to get standard errors from parsed_params
        if hasattr(parsed_params, 'standard_errors') and parsed_params.standard_errors:
            se_dict = parsed_params.standard_errors
        else:
            se_dict = {}

        if hasattr(parsed_params, 't_values') and parsed_params.t_values:
            t_dict = parsed_params.t_values
        else:
            t_dict = {}

        if hasattr(parsed_params, 'p_values') and parsed_params.p_values:
            p_dict = parsed_params.p_values
        else:
            p_dict = {}

        for param_name, param_value in params.items():
            # Get SE, t, p for this parameter
            se = se_dict.get(param_name)
            t_val = t_dict.get(param_name)
            p_val = p_dict.get(param_name)

            if se is None or t_val is None or p_val is None:
                continue  # Skip if we don't have diagnostics

            # Determine significance stars
            if p_val < 0.01:
                sig_stars = "***"
                sig_color = "var(--success-color)"
            elif p_val < 0.05:
                sig_stars = "**"
                sig_color = "var(--warning-color)"
            elif p_val < 0.10:
                sig_stars = "*"
                sig_color = "#f39c12"
            else:
                sig_stars = ""
                sig_color = "#999"

            # Highlight poorly identified
            row_style = ""
            if param_name in poorly_identified:
                row_style = 'style="background-color: #fff3cd;"'  # Light yellow

            param_rows.append(f"""
                <tr {row_style}>
                    <td><code>{param_name}</code></td>
                    <td>{param_value:.6f}</td>
                    <td>{se:.6f}</td>
                    <td>{t_val:.3f}</td>
                    <td>{p_val:.4f}</td>
                    <td style="color: {sig_color}; font-weight: bold;">{sig_stars}</td>
                </tr>
            """)

    param_table_html = ""
    if param_rows:
        param_table_html = f"""
        <h3>Parameter Standard Errors and Significance</h3>
        <p style="font-size: 0.9em; color: #666; margin-bottom: 1em;">
            Significance levels: *** p&lt;0.01, ** p&lt;0.05, * p&lt;0.10.
            Highlighted rows indicate poorly identified parameters (large SE or p&gt;0.10).
        </p>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Parameter</th>
                    <th>Estimate</th>
                    <th>Std Error</th>
                    <th>t-value</th>
                    <th>p-value</th>
                    <th>Sig</th>
                </tr>
            </thead>
            <tbody>
                {"".join(param_rows)}
            </tbody>
        </table>
        """

    eigenvector_html = ""
    if eigenvector_diagnostics:
        rows = ""
        for item in eigenvector_diagnostics:
            ev = item.get('eigenvalue')
            ev_str = f"{ev:.2e}" if is_num(ev) else "N/A"
            loadings = item.get('top_loadings', [])
            loading_str = ", ".join([
                f"<code>{l.get('param')}</code> ({l.get('loading'):.3f})"
                for l in loadings
            ])
            rows += f"""
            <tr>
                <td>{ev_str}</td>
                <td>{loading_str}</td>
            </tr>
            """
        eigenvector_html = f"""
        <h3>Smallest-Eigenvalue Directions</h3>
        <p style="font-size: 0.9em; color: #666;">
            Dominant loadings for the smallest eigenvalues (flat directions in the likelihood).
        </p>
        <table class="table table-striped table-sm">
            <thead>
                <tr><th>Eigenvalue</th><th>Top Loadings</th></tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        """

    # Build poorly identified params list
    poorly_identified_html = ""
    if poorly_identified:
        poorly_list = ", ".join([f"<code>{p}</code>" for p in poorly_identified[:10]])
        if len(poorly_identified) > 10:
            poorly_list += f" (and {len(poorly_identified) - 10} more)"
        poorly_identified_html = f"""
        <div class="stats-box" style="border-left-color: var(--warning-color); margin-top: 1em;">
            <h4 style="margin-top:0;">⚠ Poorly Identified Parameters ({len(poorly_identified)})</h4>
            <p style="margin:0;">{poorly_list}</p>
        </div>
        """

    return f"""
    <section>
        <h2>🔍 Identification Diagnostics</h2>
        <p>Hessian-based diagnostics for parameter identification quality.</p>

        <div class="stats-box" style="border-left-color: {cond_color}; margin-bottom: 1em;">
            <h3 style="margin-top:0;">Condition Number: {condition_number:.2e}</h3>
            <p style="font-size: 1.1em; margin: 0.5em 0;"><strong>{cond_status}</strong></p>
            <p style="margin:0;">{cond_interpretation}</p>
        </div>

        <h3>Eigenvalue Analysis</h3>
        {eigenvalue_html}
        {eigen_detail_html}
        {eigenvector_html}

        {poorly_identified_html}

        {correlation_html}

        <div class="stats-box" style="border-left-color: #95a5a6; margin-top: 1.5em;">
            <h4 style="margin-top:0;">ℹ️ Technical Notes</h4>
            <p style="margin-bottom: 0.5em;">
                <strong>Condition Number (κ):</strong> Measures sensitivity of parameter estimates to small changes in data.
                κ = λ<sub>max</sub> / λ<sub>min</sub>, where λ are eigenvalues of -H (Hessian).
            </p>
            <p style="margin-bottom: 0.5em;">
                <strong>Eigenvalues:</strong> All eigenvalues of -H should be positive for a local maximum.
                Near-zero eigenvalues indicate flat directions (weak identification).
            </p>
            <p style="margin-bottom: 0.5em;">
                <strong>Sign convention:</strong> Eigenvalues shown come from the Hessian used to compute SEs. When SEs are
                computed numerically, this is the Hessian of the negative log-likelihood (H), so negative values indicate
                H is not positive semidefinite (ill-conditioning or non-optimum).
            </p>
            <p style="margin:0;">
                <strong>Standard Errors:</strong> Computed as SE = √diag((-H)⁻¹), where H is the Hessian at the optimum.
                Large SE indicates parameter is not precisely estimated.
            </p>
        </div>
    </section>
    """


def generate_html_report_styled(
    parsed_params: ParsedParameters,
    fit_results: Dict[str, Dict[str, Any]],
    output_path: Path,
    fit_stats: Dict[str, float] = None,
    plot_paths: Dict[str, Path] = None,
    mu_results: Dict[str, Dict[str, Any]] = None,
    elasticities_df: pd.DataFrame = None,
    muc_analysis: List[Dict[str, Any]] = None,
    estimation_time_seconds: float = None,
    post_estimation_time_seconds: float = None,
    total_elapsed_seconds: float = None,
    prob_diagnostics: Dict[str, Any] = None,
    bound_diagnostics: List[Dict[str, Any]] = None,
    hessian_diagnostics: Dict[str, Any] = None,
) -> Path:
    """
    Generate comprehensive HTML report with professional styling.

    Matches the aesthetics of vw_pooled_post_estimation_report.html
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    group_labels = {
        'sm': 'Single Males', 'sf': 'Single Females',
        'm': 'Males in Couples', 'f': 'Females in Couples',
        'cou': 'Couples', 'cou_m': 'Males in Couples', 'cou_f': 'Females in Couples',
        'singles_male': 'Single Males', 'singles_female': 'Single Females',
        'couples': 'Couples', 'couples_m': 'Males in Couples', 'couples_f': 'Females in Couples',
        'joint': 'Joint (All Groups)',
    }

    if fit_stats is None:
        fit_stats = {}
    if elasticities_df is None:
        elasticities_df = compute_structural_elasticities(parsed_params)
    if muc_analysis is None:
        muc_analysis = analyze_muc_behavior(parsed_params)

    # Calculate bounded parameter statistics
    param_bounds = {}
    initial_values = {}
    n_bounded = 0
    n_hit_lower = 0
    n_hit_upper = 0

    if parsed_params.bounds is not None:
        for i, name in enumerate(parsed_params.param_names):
            if i < len(parsed_params.bounds):
                lb, ub = parsed_params.bounds[i]
                param_bounds[name] = (lb, ub)
                val = parsed_params.theta[i]
                if lb is not None or ub is not None:
                    n_bounded += 1
                if lb is not None and abs(val - lb) < 1e-6:
                    n_hit_lower += 1
                if ub is not None and abs(val - ub) < 1e-6:
                    n_hit_upper += 1

    if parsed_params.initial_values is not None:
        for i, name in enumerate(parsed_params.param_names):
            if i < len(parsed_params.initial_values):
                initial_values[name] = parsed_params.initial_values[i]

    # Format elapsed time
    def format_time(seconds):
        if seconds is None:
            return "N/A"
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s"
        else:
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            return f"{hours}h {mins}m"

    # CSS
    css = """
    :root {
      --primary-color: #2c3e50;
      --success-color: #27ae60;
      --warning-color: #e74c3c;
      --bg-light: #f8f9fa;
      --sm-color: #1f77b4;
      --sf-color: #ff7f0e;
      --cm-color: #2ca02c;
      --cf-color: #d62728;
      --bound-hit-color: #ffcccc;
      --bounded-row-color: #fff3cd;
      --not-estimated-color: #f8d7da;
      --pval-marginal: #d4edda;
      --pval-weak: #fff3cd;
      --pval-insig: #f8d7da;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      margin: 0; padding: 2em; max-width: 1600px; margin: 0 auto;
      line-height: 1.6; color: #333;
    }
    h1 { color: var(--primary-color); border-bottom: 3px solid var(--primary-color); padding-bottom: 0.5em; }
    h2 { color: var(--primary-color); margin-top: 2em; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; }
    h3 { color: var(--primary-color); }
    .table { border-collapse: collapse; margin-bottom: 1.5em; width: 100%; }
    .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    .table th { background-color: var(--bg-light); font-weight: 600; }
    .table-striped tbody tr:nth-child(odd) { background-color: #f9f9f9; }
    .table-sm th, .table-sm td { padding: 5px 8px; font-size: 0.9em; }
    section { margin-bottom: 2.5em; padding: 1.5em; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    figure { margin: 1em 0; text-align: center; }
    figcaption { font-weight: bold; margin-bottom: 0.5em; color: var(--primary-color); }
    img { max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5em; }
    .four-col { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5em; }
    .stats-box { background: var(--bg-light); padding: 1em; border-radius: 4px; border-left: 4px solid var(--primary-color); }
    .time-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1em; border-radius: 8px; margin: 1em 0; }
    .time-box h4 { margin: 0 0 0.5em 0; }
    .time-box .time-value { font-size: 1.5em; font-weight: bold; }
    .param-groups { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1em; }
    .param-group { background: var(--bg-light); padding: 1em; border-radius: 4px; }
    .contour-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5em; }
    .header-info { background: var(--bg-light); padding: 1em; border-radius: 4px; margin-bottom: 2em; }
    .group-legend { display: flex; gap: 2em; margin: 1em 0; flex-wrap: wrap; }
    .legend-item { display: flex; align-items: center; gap: 0.5em; }
    .legend-color { width: 20px; height: 4px; border-radius: 2px; }
    .param-table .bounded-param { background-color: var(--bounded-row-color) !important; }
    .param-table .bound-hit { background-color: var(--bound-hit-color) !important; font-weight: bold; }
    .param-table .pval-marginal { background-color: var(--pval-marginal); }
    .param-table .pval-weak { background-color: var(--pval-weak); }
    .param-table .pval-insig { background-color: var(--pval-insig); }
    .warning-cell { background-color: #ffcccc !important; font-weight: bold; }
    .warning-row { background-color: #fff3cd !important; }
    .color-legend { display: flex; flex-wrap: wrap; gap: 1em; margin: 1em 0; padding: 0.5em; background: #f0f0f0; border-radius: 4px; }
    .color-legend-item { display: flex; align-items: center; gap: 0.5em; font-size: 0.85em; }
    .color-box { width: 16px; height: 16px; border: 1px solid #999; border-radius: 2px; }
    .spec-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1.5em; margin-top: 1.5em; }
    .spec-card { background: white; padding: 1.5em; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-top: 4px solid; }
    .spec-section { margin-bottom: 1.5em; }
    .spec-section h4 { margin: 0 0 0.75em 0; font-size: 1.1em; color: #333; border-bottom: 2px solid #eee; padding-bottom: 0.5em; }
    .math-block { background: #f8f9fa; padding: 1em; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 0.95em; line-height: 1.6; overflow-x: auto; white-space: pre-wrap; word-break: break-word; }
    .math-block.symbolic { background: #e8f4f8; border-left: 3px solid #3498db; }
    .math-block.numerical { background: #fef5e7; border-left: 3px solid #f39c12; }
    @media (max-width: 768px) { .two-col, .four-col, .contour-grid { grid-template-columns: 1fr; } }
    """    # Build fit stats section
    fit_stats_rows = ""
    for k, v in fit_stats.items():
        if is_num(v):
            fv = float(v)
            if abs(fv) < 0.01 or abs(fv) > 10000:
                fit_stats_rows += f"<tr><th>{k}</th><td>{fv:.4e}</td></tr>"
            else:
                fit_stats_rows += f"<tr><th>{k}</th><td>{fv:.4f}</td></tr>"
        elif v is not None:
            fit_stats_rows += f"<tr><th>{k}</th><td>{v}</td></tr>"

    fit_stats_rows += f"<tr><th>n_bounded_params</th><td>{n_bounded}</td></tr>"
    fit_stats_rows += f"<tr><th>n_hit_lower_bound</th><td>{n_hit_lower}</td></tr>"
    fit_stats_rows += f"<tr><th>n_hit_upper_bound</th><td>{n_hit_upper}</td></tr>"

    # Bounds explanation
    bounds_explanation = f"""
    <div class="stats-box" style="margin-top:1.5em; border-left-color: var(--success-color);">
      <h4 style="margin-top:0;">📝 Understanding Bounded Parameters</h4>
      <ul style="margin-bottom:0; line-height:1.8;">
        <li><strong>n_bounded_params ({n_bounded})</strong>: Parameters with constraints defined.</li>
        <li><strong>n_hit_lower_bound ({n_hit_lower})</strong>: Parameters at lower bound. {'<span style="color:var(--success-color);">✓ Good!</span>' if n_hit_lower == 0 else '<span style="color:var(--warning-color);">⚠ Check spec</span>'}</li>
        <li><strong>n_hit_upper_bound ({n_hit_upper})</strong>: Parameters at upper bound. {'<span style="color:var(--success-color);">✓ Good!</span>' if n_hit_upper == 0 else '<span style="color:var(--warning-color);">⚠ Check spec</span>'}</li>
      </ul>
    </div>
    """

    # Elapsed time section
    time_section = ""
    if estimation_time_seconds is not None or post_estimation_time_seconds is not None or total_elapsed_seconds is not None:
        time_section = f"""
    <div class="time-box">
      <h4>⏱️ Elapsed Time</h4>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1em; text-align: center;">
        <div>
          <div style="font-size: 0.9em; opacity: 0.8;">Estimation</div>
          <div class="time-value">{format_time(estimation_time_seconds)}</div>
        </div>
        <div>
          <div style="font-size: 0.9em; opacity: 0.8;">Post-Estimation</div>
          <div class="time-value">{format_time(post_estimation_time_seconds)}</div>
        </div>
        <div>
          <div style="font-size: 0.9em; opacity: 0.8;">Total</div>
          <div class="time-value">{format_time(total_elapsed_seconds)}</div>
        </div>
      </div>
    </div>
    """    # Build elasticities table
    elasticities_html = ""
    if elasticities_df is not None and len(elasticities_df) > 0:
        elasticities_html = elasticities_df.to_html(classes='table table-striped', border=0, index=False)

    # Build wage equation display
    wage_equation_html = ""
    # Extract wage parameters (they should be in the first group or 'joint')
    wage_params = {}
    for group in parsed_params.groups:
        params = parsed_params.get_all_params_for_group(group)
        if 'beta_w0' in params:
            wage_params = params
            break

    if wage_params:
        beta_w0 = wage_params.get('beta_w0', 0.0)
        beta_w_educL = wage_params.get('beta_w_educL', 0.0)
        beta_w_educH = wage_params.get('beta_w_educH', 0.0)
        beta_pexp = wage_params.get('beta_pexp', 0.0)
        beta_pexp2 = wage_params.get('beta_pexp2', 0.0)
        sigma = wage_params.get('sigma', 0.0)

        wage_equation_html = f"""
        <div class="stats-box" style="margin-top: 1em;">
            <h4>Log-Wage Equation (Mincer Style)</h4>
            <div class="math-block symbolic">
                log(wage) = β<sub>w0</sub> + β<sub>w,educL</sub> · educL + β<sub>w,educH</sub> · educH
                           + β<sub>pexp</sub> · experience + β<sub>pexp²</sub> · experience² + ε
                <br><br>
                where ε ~ N(0, σ²)
            </div>
            <div class="math-block numerical" style="margin-top: 1em;">
                log(wage) = {beta_w0:.4f} + {beta_w_educL:+.4f} · educL + {beta_w_educH:+.4f} · educH
                           + {beta_pexp:+.4f} · experience + {beta_pexp2:+.6f} · experience² + ε
                <br><br>
                σ = {sigma:.4f}
            </div>
        </div>
        """

    # Build hours opportunity HTML
    hours_opportunity_html = ""
    if wage_params:  # Same params dict contains opportunity parameters
        beta_work = wage_params.get('beta_work', 0.0)
        beta_pt1 = wage_params.get('beta_pt1', 0.0)
        beta_pt2 = wage_params.get('beta_pt2', 0.0)
        beta_ft = wage_params.get('beta_ft', 0.0)
        beta_gsur = wage_params.get('beta_gsur', 0.0)
        beta_work_educL = wage_params.get('beta_work_educL', 0.0)
        beta_work_educH = wage_params.get('beta_work_educH', 0.0)
        beta_work_female = wage_params.get('beta_work_female', 0.0)
        beta_work_couple = wage_params.get('beta_work_couple', 0.0)
        beta_work_idf = wage_params.get('beta_work_idf', 0.0)

        hours_opportunity_html = f"""
        <div class="stats-box" style="margin-top: 1em;">
            <h4>Hours Opportunity Function</h4>
            <div class="math-block symbolic">
                log h(h|X) = β<sub>work</sub> · I(h>0) + β<sub>pt1</sub> · I(h∈[18.5,20.5])
                           + β<sub>pt2</sub> · I(h∈[29.5,30.5]) + β<sub>ft</sub> · I(h∈[37.5,40.5])
                           + β<sub>gsur</sub> · gsur + β<sub>work,educL</sub> · educL + β<sub>work,educH</sub> · educH
                           + β<sub>work,female</sub> · female + β<sub>work,couple</sub> · couple + β<sub>work,idf</sub> · idf
            </div>
            <div class="math-block numerical" style="margin-top: 1em;">
                log h(h|X) = {beta_work:.4f} · I(h>0) + {beta_pt1:+.4f} · I(h∈[18.5,20.5])
                           + {beta_pt2:+.4f} · I(h∈[29.5,30.5]) + {beta_ft:+.4f} · I(h∈[37.5,40.5])
                <br>
                           + {beta_gsur:+.4f} · gsur + {beta_work_educL:+.4f} · educL + {beta_work_educH:+.4f} · educH
                <br>
                           + {beta_work_female:+.4f} · female + {beta_work_couple:+.4f} · couple + {beta_work_idf:+.4f} · idf
            </div>
        </div>
        """

    # Build MUC analysis table
    muc_analysis_html = ""
    if muc_analysis:
        muc_rows = ""
        for row in muc_analysis:
            row_class = 'class="warning-row"' if row.get('is_warning') else ''
            c_muc_1 = row.get('C where MUC=1')
            c_muc_1_str = safe_format(c_muc_1, ".4f", "N/A")
            muc_median = row.get('MUC at Median C', 0)
            muc_median_str = safe_format(muc_median, ".4f", "N/A")

            muc_rows += f"""
            <tr {row_class}>
                <td>{row['Group']}</td>
                <td>{safe_format(row['β_c'], '.4f')}</td>
                <td>{safe_format(row['θ_c'], '.4f')}</td>
                <td>{row['MUC Positive?']}</td>
                <td>{row['MUC Diminishing?']}</td>
                <td>{row['Well-Behaved?']}</td>
                <td>{muc_median_str}</td>
                <td>{c_muc_1_str}</td>
                <td style="font-size:0.85em;">{row.get('Notes', '')}</td>
            </tr>
            """
        muc_analysis_html = f"""
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Group</th><th>β_c</th><th>θ_c</th>
                    <th>MUC Positive?</th><th>MUC Diminishing?</th><th>Well-Behaved?</th>
                    <th>MUC at Median C</th><th>C where MUC=1</th><th>Notes</th>
                </tr>
            </thead>
            <tbody>{muc_rows}</tbody>        </table>
        """

    # Build fit diagnostics table
    fit_table_rows = ""
    for group, results in fit_results.items():
        obs_part = results.get('participation_observed', np.nan)
        pred_part = results.get('participation_predicted', np.nan)
        obs_hours = results.get('mean_hours_observed', np.nan)
        pred_hours = results.get('mean_hours_predicted', np.nan)

        obs_part_str = f"{obs_part*100:.1f}%" if not np.isnan(obs_part) else "N/A"
        pred_part_str = f"{pred_part*100:.1f}%" if not np.isnan(pred_part) else "N/A"
        obs_hours_str = f"{obs_hours:.1f}" if not np.isnan(obs_hours) else "N/A"
        pred_hours_str = f"{pred_hours:.1f}" if not np.isnan(pred_hours) else "N/A"

        fit_table_rows += f"""
        <tr>
            <td>{group_labels.get(group, group)}</td>
            <td>{obs_part_str}</td>
            <td>{pred_part_str}</td>
            <td>{obs_hours_str}</td>
            <td>{pred_hours_str}</td>
        </tr>
        """

    # Build MU diagnostics table
    mu_table_rows = ""
    if mu_results and 'by_group' in mu_results:
        for group, results in mu_results['by_group'].items():
            n_ind = results.get('N', 0)
            pct_muc = results.get('pct_neg_muc', 0) or 0
            pct_mul = results.get('pct_neg_mul', 0) or 0
            muc_mean = results.get('mean_muc', np.nan)
            mul_mean = results.get('mean_mul', np.nan)

            muc_cell_class = 'class="warning-cell"' if pct_muc > 5 else ''
            mul_cell_class = 'class="warning-cell"' if pct_mul > 5 else ''

            muc_mean_str = safe_format(muc_mean, ".4f", "N/A")
            mul_mean_str = safe_format(mul_mean, ".4e", "N/A")

            mu_table_rows += f"""
            <tr>
                <td>{group_labels.get(group, group)}</td>
                <td>{n_ind}</td>
                <td {muc_cell_class}>{pct_muc:.2f}%</td>
                <td {mul_cell_class}>{pct_mul:.2f}%</td>
                <td>{muc_mean_str}</td>
                <td>{mul_mean_str}</td>
            </tr>
            """

    # Build probability diagnostics section
    prob_diag_html = ""
    if prob_diagnostics:
        prob_sum = prob_diagnostics.get('prob_sum_errors', {})
        p_chosen = prob_diagnostics.get('p_chosen_dist', {})
        worst_fit = prob_diagnostics.get('worst_fit_households', [])
        
        if prob_sum or p_chosen:
            prob_diag_html = """
            <h3>📊 Choice Probability Diagnostics</h3>
            <div class="two-col">
            """
            
            if prob_sum:
                prob_diag_html += f"""
                <div class="stats-box">
                    <h4>Probability Sum Sanity Check</h4>
                    <table class="table table-sm">
                        <tr><td>Max |Σp - 1|</td><td>{prob_sum.get('max_error', 0):.6f}</td></tr>
                        <tr><td>Mean |Σp - 1|</td><td>{prob_sum.get('mean_error', 0):.6f}</td></tr>
                        <tr><td>% HH off by &gt;0.01</td><td>{prob_sum.get('pct_off_by_0.01', 0):.2f}%</td></tr>
                        <tr><td>% HH off by &gt;0.001</td><td>{prob_sum.get('pct_off_by_0.001', 0):.2f}%</td></tr>
                    </table>
                </div>
                """
            
            if p_chosen:
                prob_diag_html += f"""
                <div class="stats-box">
                    <h4>P(chosen) Distribution</h4>
                    <table class="table table-sm">
                        <tr><td>Min</td><td>{p_chosen.get('min', 0):.4f}</td></tr>
                        <tr><td>10th percentile</td><td>{p_chosen.get('q10', 0):.4f}</td></tr>
                        <tr><td>25th percentile</td><td>{p_chosen.get('q25', 0):.4f}</td></tr>
                        <tr><td>Median</td><td>{p_chosen.get('median', 0):.4f}</td></tr>
                        <tr><td>Mean</td><td>{p_chosen.get('mean', 0):.4f}</td></tr>
                        <tr><td>75th percentile</td><td>{p_chosen.get('q75', 0):.4f}</td></tr>
                        <tr><td>90th percentile</td><td>{p_chosen.get('q90', 0):.4f}</td></tr>
                        <tr><td>Max</td><td>{p_chosen.get('max', 0):.4f}</td></tr>                    </table>
                </div>
                """
            
            prob_diag_html += "</div>"
        
        # Worst-fit households table - COMMENTED OUT per user request
        # These diagnostics can be misleading and are not essential for model evaluation
        # if worst_fit:
        #     worst_rows = ""
        #     for i, hh in enumerate(worst_fit[:20], 1):
        #         worst_rows += f"""
        #         <tr>
        #             <td>{i}</td>
        #             <td>{hh.get('idhh', 'N/A')}</td>
        #             <td>{group_labels.get(hh.get('group', ''), hh.get('group', 'N/A'))}</td>
        #             <td>{hh.get('p_chosen', 0):.6f}</td>
        #             <td>{hh.get('ll_i', 0):.2f}</td>
        #         </tr>
        #         """
        #     
        #     prob_diag_html += f"""
        #     <h3>🔻 Worst-Fit Households (Bottom 20 by Log-Likelihood)</h3>
        #     <p><em>These households have the lowest P(chosen), indicating potential outliers or specification issues.</em></p>
        #     <table class="table table-striped table-sm">
        #         <thead>
        #             <tr><th>#</th><th>HH ID</th><th>Group</th><th>P(chosen)</th><th>log(P)</th></tr>
        #         </thead>
        #         <tbody>{worst_rows}</tbody>
        #     </table>
        #     """

    # Build bound diagnostics section
    bound_diag_html = ""
    if bound_diagnostics and len(bound_diagnostics) > 0:
        bound_rows = ""
        for bd in bound_diagnostics:
            side_icon = "⬇️" if bd.get('side') == 'lower' else "⬆️"
            bound_rows += f"""
            <tr>
                <td>{bd.get('parameter', 'N/A')}</td>
                <td>{bd.get('estimate', 0):.6f}</td>
                <td>{bd.get('bound', 0):.6f}</td>
                <td>{side_icon} {bd.get('side', 'N/A')}</td>
            </tr>
            """
        
        bound_diag_html = f"""
        <h3>⚠️ Parameters at Bounds (within 1e-6)</h3>
        <p><em>These parameters hit their constraints. Consider checking if bounds are too restrictive.</em></p>
        <table class="table table-striped table-sm">
            <thead>
                <tr><th>Parameter</th><th>Estimate</th><th>Bound</th><th>Side</th></tr>
            </thead>
            <tbody>{bound_rows}</tbody>
        </table>
        """

    # Build group parameters section
    group_params_html = ""
    for group in parsed_params.preference_groups:
        params = parsed_params.get_all_params_for_group(group)
        simple_params = {k: v for k, v in params.items() if '.' not in k}

        if group in ['cou', 'couples']:
            male_params = {k.replace('_m', ''): v for k, v in simple_params.items() if k.endswith('_m')}
            female_params = {k.replace('_f', ''): v for k, v in simple_params.items() if k.endswith('_f')}
            shared_params = {k: v for k, v in simple_params.items() if not k.endswith('_m') and not k.endswith('_f')}

            if male_params:
                param_rows = [f"<tr><td>{k}</td><td>{v:.4f}</td></tr>" for k, v in sorted(male_params.items())]
                group_params_html += f"""
                <div class="param-group">
                    <h4>Males in Couples</h4>
                    <table class="table table-sm">{''.join(param_rows)}</table>
                </div>
                """
            if female_params:
                param_rows = [f"<tr><td>{k}</td><td>{v:.4f}</td></tr>" for k, v in sorted(female_params.items())]
                group_params_html += f"""
                <div class="param-group">
                    <h4>Females in Couples</h4>
                    <table class="table table-sm">{''.join(param_rows)}</table>
                </div>
                """
            if shared_params:
                param_rows = [f"<tr><td>{k}</td><td>{v:.4f}</td></tr>" for k, v in sorted(shared_params.items())]
                group_params_html += f"""
                <div class="param-group">
                    <h4>Couples (shared)</h4>
                    <table class="table table-sm">{''.join(param_rows)}</table>
                </div>
                """
        else:
            param_rows = [f"<tr><td>{k}</td><td>{v:.4f}</td></tr>" for k, v in sorted(simple_params.items())]
            group_params_html += f"""
            <div class="param-group">
                <h4>{group_labels.get(group, group)}</h4>
                <table class="table table-sm">{''.join(param_rows)}</table>
            </div>
            """

    group_params_section = ""
    if group_params_html:
        group_params_section = f"""
    <section>
        <h2>Group-Specific Parameters</h2>
        <div class="param-groups">{group_params_html}</div>
    </section>
    """

    # Build plots section
    plots_section = ""
    if plot_paths:
        contour_plots = []
        mu_comparison_plots = []
        mu_distribution_plots = []
        fit_plots = []

        for name, path in plot_paths.items():
            if path and Path(path).exists():
                img_tag = f'<img src="{Path(path).name}" alt="{name}" style="max-width:100%;">'
                if 'contour' in name.lower():
                    label = group_labels.get(name.replace('_contours', ''), name)
                    contour_plots.append(f'<div class="contour-item"><h4>{label}</h4>{img_tag}</div>')
                elif 'muc_comparison' in name.lower() or 'mul_comparison' in name.lower():
                    title = 'Marginal Utility of Consumption' if 'muc' in name.lower() else 'Marginal Utility of Leisure'
                    mu_comparison_plots.append(f'<figure><figcaption>{title}</figcaption>{img_tag}</figure>')
                elif name.endswith('_mu'):
                    # Individual MU distribution plots per group (sm_mu, sf_mu, cou_m_mu, cou_f_mu)
                    group_key = name.replace('_mu', '')
                    label = group_labels.get(group_key, group_key)
                    mu_distribution_plots.append(f'<div class="contour-item"><h4>{label} - MUC & MUL Distributions</h4>{img_tag}</div>')
                elif 'fit_' in name.lower() or 'participation' in name.lower() or 'mean_hours' in name.lower():
                    title = name.replace('fit_', '').replace('_', ' ').title()
                    fit_plots.append(f'<figure><figcaption>{title}</figcaption>{img_tag}</figure>')

        if mu_comparison_plots:
            plots_section += f'<h3>Marginal Utility Comparison</h3><div class="two-col">{"".join(mu_comparison_plots)}</div>'
        if mu_distribution_plots:
            plots_section += f'<h3>📊 Marginal Utility Distributions by Group</h3><div class="contour-grid">{"".join(mu_distribution_plots)}</div>'
        if contour_plots:
            plots_section += f'<h3>Utility Indifference Curves by Group</h3><div class="contour-grid">{"".join(contour_plots)}</div>'
        if fit_plots:
            plots_section += f'<div class="two-col">{"".join(fit_plots)}</div>'

    # Color legend
    color_legend = """
    <div class="color-legend">
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--bounded-row-color);"></div>Bounded (has constraints)</div>
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--bound-hit-color);"></div>⚠️ Hit bound</div>
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--pval-marginal);"></div>p ∈ [0.05, 0.1)</div>
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--pval-weak);"></div>p ∈ [0.1, 0.25)</div>
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--pval-insig);"></div>p ≥ 0.25</div>
    </div>
    """    # Build full parameter table - SEPARATED by preference vs opportunity
    param_df = parsed_params.to_dataframe()

    bound_range_tol = 1e-6

    def is_estimable_param(row):
        lb = row.get('lower_bound')
        ub = row.get('upper_bound')
        if is_num(lb) and is_num(ub) and (float(ub) - float(lb)) <= bound_range_tol:
            return False
        return True

    param_df = param_df[param_df.apply(is_estimable_param, axis=1)].copy()
    
    # Classify parameters into preference vs opportunity
    def classify_param(name):
        """Classify parameter as 'preference', 'hours_opp', 'wage_opp', or 'other'."""
        name_lower = name.lower()
        # Preference parameters: beta_l*, beta_c*, theta_l*, theta_c*, beta_interact
        if any(x in name_lower for x in ['beta_l', 'beta_c', 'theta_l', 'theta_c', 'beta_interact']):
            return 'preference'
        # Hours opportunity: beta_work, beta_pt*, beta_ft, beta_gsur, beta_work_educ*
        if any(x in name_lower for x in ['beta_work', 'beta_pt', 'beta_ft', 'beta_gsur']):
            return 'hours_opp'
        # Wage opportunity: beta_w*, beta_pexp*, sigma
        if any(x in name_lower for x in ['beta_w', 'beta_pexp', 'sigma']):
            return 'wage_opp'
        return 'other'
    
    param_df['category'] = param_df['parameter'].apply(classify_param)
    
    def build_param_table_html(df_subset, title, description=""):
        """Build HTML table for a subset of parameters."""
        if len(df_subset) == 0:
            return ""
        
        rows_html = ""
        for idx, row in df_subset.iterrows():
            param_name = row.get('parameter', '')
            est = row.get('estimate', np.nan)
            se = row.get('std_error', np.nan)
            t_val = row.get('t_value', np.nan)
            p_val = row.get('p_value', np.nan)
            lb = row.get('lower_bound')
            ub = row.get('upper_bound')
            init_val = row.get('initial_value')

            row_class = ""
            is_bounded = lb is not None or ub is not None
            hit_bound = False
            if is_bounded and is_num(est):
                if lb is not None and abs(float(est) - lb) < 1e-6:
                    hit_bound = True
                if ub is not None and abs(float(est) - ub) < 1e-6:
                    hit_bound = True

            if hit_bound:
                row_class = 'class="bound-hit"'
            elif is_bounded:
                row_class = 'class="bounded-param"'

            est_str = safe_format(est, ".4f", "N/A")
            se_str = safe_format(se, ".4f", "N/A")
            t_str = safe_format(t_val, ".2f", "N/A")
            lb_str = safe_format(lb, ".4f", "—")
            ub_str = safe_format(ub, ".4f", "—")
            init_str = safe_format(init_val, ".4f", "N/A")

            sig = ""
            p_str = "N/A"
            p_class = ""
            if is_num(p_val):
                p_str = f"{float(p_val):.4f}"
                if p_val < 0.001:
                    sig = "***"
                elif p_val < 0.01:
                    sig = "**"
                elif p_val < 0.05:
                    sig = "*"
                elif p_val < 0.1:
                    p_class = 'class="pval-marginal"'
                elif p_val < 0.25:
                    p_class = 'class="pval-weak"'
                else:
                    p_class = 'class="pval-insig"'

            rows_html += f"""
            <tr {row_class}>
                <td>{param_name}</td>
                <td>{est_str}</td>
                <td>{se_str}</td>
                <td>{t_str}</td>
                <td {p_class}>{p_str} {sig}</td>
                <td>{lb_str}</td>
                <td>{ub_str}</td>
                <td>{init_str}</td>
            </tr>
            """
        
        desc_html = f"<p><em>{description}</em></p>" if description else ""
        return f"""
        <h3>{title}</h3>
        {desc_html}
        <div style="max-height:400px; overflow-y:auto;">
            <table class="table table-striped table-sm param-table">
                <thead>
                    <tr>
                        <th>Parameter</th>
                        <th>Estimate</th>
                        <th>Std Error</th>
                        <th>t-value</th>
                        <th>p-value</th>
                        <th>Lower Bound</th>
                        <th>Upper Bound</th>
                        <th>Initial Value</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        """
    
    # Build separate tables for each category
    pref_table = build_param_table_html(
        param_df[param_df['category'] == 'preference'],
        "🎯 Preference Parameters (Utility Function)",
        "Parameters determining the utility from consumption (β_c, θ_c) and leisure (β_l*, θ_l) by demographic group."
    )
    
    hours_opp_table = build_param_table_html(
        param_df[param_df['category'] == 'hours_opp'],
        "⏰ Hours Opportunity Parameters",
        "Parameters for the hours density: working indicator, focal hours (PT/FT), education interactions, unemployment rate effects."
    )
    
    wage_opp_table = build_param_table_html(
        param_df[param_df['category'] == 'wage_opp'],
        "💰 Wage Opportunity Parameters (Mincer Equation)",
        "Log-wage equation parameters: intercept, education effects, experience effects, and residual standard deviation (σ)."
    )
    
    other_table = build_param_table_html(
        param_df[param_df['category'] == 'other'],
        "📋 Other Parameters",
        ""
    )
    
    param_table_rows = pref_table + hours_opp_table + wage_opp_table + other_table

    # Generate specification HTML
    specification_html = generate_specification_html(parsed_params)

    # Generate identification diagnostics HTML
    identification_html = generate_identification_diagnostics_html(hessian_diagnostics, parsed_params)

    # Assemble HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>RURO Post-Estimation Analysis</title>
    <style>{css}</style>
</head>
<body>
    <h1>📊 RURO Post-Estimation Analysis</h1>

    <div class="header-info">
        <p><strong>Generated:</strong> {timestamp}</p>
        <p><strong>Total Parameters:</strong> {len(parsed_params.param_names)} | <strong>Groups:</strong> {', '.join(parsed_params.groups)}</p>
        <div class="group-legend">
            <div class="legend-item"><div class="legend-color" style="background:var(--sm-color)"></div>Single Males</div>
            <div class="legend-item"><div class="legend-color" style="background:var(--sf-color)"></div>Single Females</div>
            <div class="legend-item"><div class="legend-color" style="background:var(--cm-color)"></div>Males in Couples</div>
            <div class="legend-item"><div class="legend-color" style="background:var(--cf-color)"></div>Females in Couples</div>
        </div>
    </div>

    {time_section}

    <section>
        <h2>📈 Model Fit Statistics</h2>
        <table class="table" style="width:auto;">
            {fit_stats_rows}
        </table>
        {bounds_explanation}
    </section>

    {identification_html}

    <section>
        <h2>📐 Model Specification</h2>
        <p>Utility and opportunity functions for each demographic group, shown in both symbolic and numerical form.</p>
        {specification_html}

        <h3>⏰ Hours Opportunity Function (All Groups)</h3>
        {hours_opportunity_html}

        <h3>💰 Wage Equation - Mincer (All Groups)</h3>
        {wage_equation_html}
    </section>

    <section>
        <h2>📈 Curvature-Based Heuristics (Structural Elasticity Approximations)</h2>
        <div class="stats-box" style="margin-bottom: 1.5em; border-left-color: #3498db;">
            <h4 style="margin-top:0;">⚠️ Interpretation Note</h4>
            <p style="margin-bottom:0;">
                These are <strong>not</strong> true labor supply elasticities. They are heuristic approximations
                derived from the curvature parameters (θ) of the Box-Cox utility function. The Hicksian approximation
                is (1 - θ_l), which measures the curvature of preferences. For rigorous elasticity estimates,
                use simulation-based methods that account for the full discrete choice structure and budget constraints.
            </p>
        </div>

        <h3>📊 Labor Supply Elasticities</h3>
        {elasticities_html}
    </section>

    <section>
        <h2>🎯 Fit Diagnostics</h2>
        <h3>Observed vs Predicted</h3>
        <table class="table table-striped">
            <thead>
                <tr><th>Group</th><th>Obs. Participation</th><th>Pred. Participation</th><th>Obs. Mean Hours</th><th>Pred. Mean Hours</th></tr>
            </thead>
            <tbody>{fit_table_rows}</tbody>
        </table>
    </section>

    <section>
        <h2>⚠️ Marginal Utility Diagnostics</h2>
        <p>Analysis at chosen alternatives. Negative values indicate potential specification issues.</p>

        <h3>Negative MUC/MUL Summary</h3>
        <table class="table table-striped">
            <thead>
                <tr><th>Group</th><th>N Individuals</th><th>% Neg MUC</th><th>% Neg MUL</th><th>MUC Mean</th><th>MUL Mean</th></tr>
            </thead>
            <tbody>{mu_table_rows}</tbody>        <h3>MUC Behavior Analysis</h3>
        <p>For well-behaved utility: MUC &gt; 0 (β_c &gt; 0) and diminishing (θ_c &lt; 1)</p>
        {muc_analysis_html}
        
        {prob_diag_html}
        
        {bound_diag_html}
    </section>

    <section>
        <h2>🗺️ Utility Contours & Plots</h2>
        {plots_section}
    </section>

    {group_params_section}

    <section>
        <h2>📋 Parameter Estimates by Category</h2>
        <p><em>Significance: *** p&lt;0.001, ** p&lt;0.01, * p&lt;0.05</em></p>
        {color_legend}
        {param_table_rows}
    </section>

    <footer>
        <p>Generated by Enhanced RURO Post-Estimation (Styled) | {timestamp}</p>
    </footer>
</body>
</html>
"""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')
    LOGGER.info(f"HTML report saved to: {output_path}")

    return output_path


# =============================================================================
# FIT DIAGNOSTICS & MARGINAL UTILITY COMPUTATION
# =============================================================================

def compute_null_log_likelihood(df: pd.DataFrame, choice_id_col: str = 'idhh') -> float:
    """
    Compute null model log-likelihood: LL0 = -Σ_i log(J_i).
    
    Parameters
    ----------
    df : pd.DataFrame
        Long-format MNL data
    choice_id_col : str
        Column identifying choice units (households)
    
    Returns
    -------
    float
        Null model log-likelihood
    """
    choice_set_sizes = df.groupby(choice_id_col).size()
    ll_null = -np.sum(np.log(choice_set_sizes.values))
    return ll_null


def load_mnl_metadata(mnl_base: Path) -> Optional[Dict[str, Any]]:
    """
    Load metadata from __mnlmeta.json file.
    
    Parameters
    ----------
    mnl_base : Path
        Base path for MNL files (e.g., fr_2016_RURO_mnl)
    
    Returns
    -------
    Optional[Dict[str, Any]]
        Metadata dict or None if not found
    """
    metadata_path = Path(str(mnl_base) + '__mnlmeta.json')
    if not metadata_path.exists():
        LOGGER.warning(f"Metadata file not found: {metadata_path}")
        return None
    
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        LOGGER.info(f"Loaded MNL metadata from: {metadata_path.name}")
        return metadata
    except Exception as e:
        LOGGER.warning(f"Could not load metadata: {e}")
        return None


def get_column_name(metadata: Optional[Dict[str, Any]], dataset: str, preferred: str, fallbacks: List[str]) -> str:
    """
    Get the correct column name from metadata with fallbacks.
    
    Parameters
    ----------
    metadata : Optional[Dict[str, Any]]
        MNL metadata dict
    dataset : str
        'singles' or 'couples'
    preferred : str
        Preferred column name
    fallbacks : List[str]
        List of fallback column names to try
    
    Returns
    -------
    str
        Column name to use
    """
    # Check metadata first
    if metadata is not None:
        columns = metadata.get('columns', {}).get(dataset, [])
        if preferred in columns:
            return preferred
        for fb in fallbacks:
            if fb in columns:
                return fb
    
    # Return preferred if no metadata
    return preferred


def compute_fit_diagnostics_from_data(
    parsed_params: ParsedParameters,
    mnl_base: Path,
    spec: Optional[Any] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Compute observed vs predicted participation and hours by group.
    
    This computes probabilities using the same utility as estimation:
    V_ij = U_pref(c_ij, l_ij; θ) + log(f_opp_ij) - log(prior_ij)
    
    Returns
    -------
    Dict[str, Dict[str, float]]
        Nested dict: {group: {'participation_observed': ..., 'participation_predicted': ..., etc.}}
    """
    LOGGER.info("Computing fit diagnostics from MNL data...")
    
    mnl_base = Path(mnl_base)
    fit_results = {}
    
    # Load data files
    try:
        metadata_path = Path(str(mnl_base) + '__mnlmeta.json')
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        singles_path = Path(str(mnl_base) + '__singles.parquet')
        couples_path = Path(str(mnl_base) + '__couples.parquet')
        
        df_singles = pd.read_parquet(singles_path) if singles_path.exists() else None
        df_couples = pd.read_parquet(couples_path) if couples_path.exists() else None
    except Exception as e:
        LOGGER.warning(f"Could not load MNL data: {e}")
        return {}
    
    # Process singles (male=0, female=1)
    for gender_code, gender_name, group_key in [(0, 'male', 'sm'), (1, 'female', 'sf')]:
        if df_singles is None:
            continue
        
        # Try 'dgn' first (dataset convention), then 'gender'
        gender_col = 'dgn' if 'dgn' in df_singles.columns else 'gender'
        df_g = df_singles[df_singles[gender_col] == gender_code].copy()
        if len(df_g) == 0:
            continue
          # Get parameters for this group
        params = None
        for try_key in [group_key, f'singles_{gender_name}', group_key.upper()]:
            if try_key in parsed_params.params_by_group:
                params = parsed_params.get_all_params_for_group(try_key)
                break
        
        if params is None or 'beta_c' not in params:
            LOGGER.warning(f"No parameters found for {group_key}, skipping fit diagnostics")
            continue
        
        try:
            # Compute observed moments
            chosen_col = 'is_chosen' if 'is_chosen' in df_g.columns else 'chosen'
            chosen = df_g[df_g[chosen_col] == 1].copy()
            obs_participation = (chosen['hours'] > 0).mean()
            obs_hours = chosen.loc[chosen['hours'] > 0, 'hours'].mean() if (chosen['hours'] > 0).any() else 0.0
            
            # Compute predicted probabilities
            beta_c = params.get('beta_c', 1.0)
            theta_c = params.get('theta_c', 0.5)
            theta_l = params.get('theta_l', 0.5)
            
            # Utility from preferences
            c = df_g['consumption'].values
            l = df_g['leisure'].values
            
            # Compute full beta_l(X) for each observation (not just beta_l0)
            beta_l = compute_beta_l_full(df_g, params, suffix='')
            
            U_pref = beta_c * boxcox_transform(c, theta_c) + beta_l * boxcox_transform(l, theta_l)
            
            # Add opportunity terms if available
            if 'log_opp' in df_g.columns:
                V = U_pref + df_g['log_opp'].values
            else:
                V = U_pref
            
            # Subtract prior if available
            if 'log_prior' in df_g.columns:
                V = V - df_g['log_prior'].values
            
            # Compute choice probabilities within each household
            df_g['V'] = V
            df_g['prob'] = 0.0
            
            for idhh, group_df in df_g.groupby('idhh'):
                V_group = group_df['V'].values
                V_shifted = V_group - V_group.max()
                exp_V = np.exp(V_shifted)
                probs = exp_V / exp_V.sum()
                df_g.loc[group_df.index, 'prob'] = probs
            
            # Predicted participation
            pred_participation = (df_g.groupby('idhh').apply(
                lambda x: (x['prob'] * (x['hours'] > 0).astype(float)).sum()
            )).mean()
            
            # Predicted mean hours among workers
            def household_pred_hours(x):
                working_mask = (x['hours'] > 0).values
                if not working_mask.any():
                    return 0.0
                numerator = (x['prob'].values * x['hours'].values * working_mask).sum()
                denominator = (x['prob'].values * working_mask).sum()
                return numerator / denominator if denominator > 0 else 0.0
            
            pred_hours = df_g.groupby('idhh').apply(household_pred_hours).mean()
            
            # Hours distribution (binned) for observed
            bins = [0, 5, 15, 25, 35, 45, 55, 65, 100]
            bin_labels = ['0', '1-10', '11-20', '21-30', '31-40', '41-50', '51-60', '60+']
            obs_hours_array = chosen['hours'].values
            obs_binned = pd.cut(obs_hours_array, bins=bins, labels=bin_labels, include_lowest=True)
            obs_vc = obs_binned.value_counts()
            hours_dist_observed = (obs_vc / obs_vc.sum()).to_dict() if obs_vc.sum() > 0 else {}
            
            # Hours distribution for predicted (expected hours per household)
            expected_hours_list = []
            for idhh, group_df in df_g.groupby('idhh'):
                exp_h = (group_df['prob'] * group_df['hours']).sum()
                expected_hours_list.append(exp_h)
            expected_hours_arr = np.array(expected_hours_list)
            pred_binned = pd.cut(expected_hours_arr, bins=bins, labels=bin_labels, include_lowest=True)
            pred_vc = pred_binned.value_counts()
            hours_dist_predicted = (pred_vc / pred_vc.sum()).to_dict() if pred_vc.sum() > 0 else {}
            
            fit_results[group_key] = {
                'participation_observed': obs_participation,
                'participation_predicted': pred_participation,
                'mean_hours_observed': obs_hours,
                'mean_hours_predicted': pred_hours,
                'hours_distribution_observed': hours_dist_observed,
                'hours_distribution_predicted': hours_dist_predicted,
            }
            
            LOGGER.info(f"  {group_key}: obs_part={obs_participation:.3f}, pred_part={pred_participation:.3f}")
            
        except Exception as e:
            LOGGER.warning(f"Could not compute fit for {group_key}: {e}")
            continue      # Process couples - compute real predicted moments using joint utility
    if df_couples is not None and len(df_couples) > 0:
        chosen_col = 'is_chosen' if 'is_chosen' in df_couples.columns else 'chosen'
        
        # Get couples parameters - try multiple keys including the new 'm'/'f' virtual groups
        params_m = None
        params_f = None
        
        # First try to get from 'cou' or 'couples' groups
        for try_key in ['cou', 'couples']:
            if try_key in parsed_params.params_by_group:
                params_m = parsed_params.get_all_params_for_group(try_key)
                params_f = params_m  # Same group for both in old format
                break
        
        # If not found, try the new 'm' and 'f' virtual groups created from 'joint'
        if params_m is None and 'm' in parsed_params.params_by_group:
            params_m = parsed_params.get_all_params_for_group('m')
        if params_f is None and 'f' in parsed_params.params_by_group:
            params_f = parsed_params.get_all_params_for_group('f')
        
        # Use params_m as the main params dict for shared parameters
        params = params_m
        
        if params is not None:
            try:
                beta_c = params.get('beta_c', 1.0)
                theta_c = params.get('theta_c', 0.5)
                # Use sex-specific curvature when available (theta_l_m, theta_l_f)
                theta_l_m = params.get('theta_l_m', params.get('theta_l', 0.5))
                theta_l_f = params.get('theta_l_f', params.get('theta_l', 0.5))
                
                df_cou = df_couples.copy()
                
                # Compute joint utility V = U_pref + log_opp - log_prior
                c = df_cou['consumption'].values
                l_m = df_cou['leisure_male'].values
                l_f = df_cou['leisure_female'].values
                
                # Preference utility
                U_c = beta_c * boxcox_transform(c, theta_c)
                
                # Leisure for male and female (using full beta_l with shifters and sex-specific curvature)
                beta_l_m = compute_beta_l_full(df_cou, params, '_m')
                beta_l_f = compute_beta_l_full(df_cou, params, '_f')
                U_l_m = beta_l_m * boxcox_transform(l_m, theta_l_m)
                U_l_f = beta_l_f * boxcox_transform(l_f, theta_l_f)
                
                V = U_c + U_l_m + U_l_f
                
                # Add opportunity terms
                if 'log_opp_male' in df_cou.columns:
                    V = V + df_cou['log_opp_male'].values
                if 'log_opp_female' in df_cou.columns:
                    V = V + df_cou['log_opp_female'].values
                if 'log_opp' in df_cou.columns:
                    V = V + df_cou['log_opp'].values
                
                # Subtract prior
                if 'log_prior' in df_cou.columns:
                    V = V - df_cou['log_prior'].values
                
                df_cou['V'] = V
                df_cou['prob'] = 0.0
                
                # Compute probabilities within each household
                for idhh, group_df in df_cou.groupby('idhh'):
                    V_group = group_df['V'].values
                    V_shifted = V_group - V_group.max()
                    exp_V = np.exp(V_shifted)
                    probs = exp_V / exp_V.sum()
                    df_cou.loc[group_df.index, 'prob'] = probs
                
                # Now compute predicted moments for each gender
                for gender, suffix in [('male', '_m'), ('female', '_f')]:
                    group_key = f'cou{suffix}'
                    hours_col = f'hours_{gender}'
                    
                    chosen = df_cou[df_cou[chosen_col] == 1].copy()
                    obs_participation = (chosen[hours_col] > 0).mean()
                    obs_hours = chosen.loc[chosen[hours_col] > 0, hours_col].mean() if (chosen[hours_col] > 0).any() else 0.0
                    
                    # Predicted participation
                    pred_participation = (df_cou.groupby('idhh').apply(
                        lambda x: (x['prob'] * (x[hours_col] > 0).astype(float)).sum()
                    )).mean()
                    
                    # Predicted hours among workers
                    def household_pred_hours(x):
                        working_mask = (x[hours_col] > 0).values
                        if not working_mask.any():
                            return 0.0
                        numerator = (x['prob'].values * x[hours_col].values * working_mask).sum()
                        denominator = (x['prob'].values * working_mask).sum()
                        return numerator / denominator if denominator > 0 else 0.0
                    
                    pred_hours = df_cou.groupby('idhh').apply(household_pred_hours).mean()
                    
                    # Hours distribution (binned) for observed
                    bins = [0, 5, 15, 25, 35, 45, 55, 65, 100]
                    bin_labels = ['0', '1-10', '11-20', '21-30', '31-40', '41-50', '51-60', '60+']
                    obs_hours_array = chosen[hours_col].values
                    obs_binned = pd.cut(obs_hours_array, bins=bins, labels=bin_labels, include_lowest=True)
                    obs_vc = obs_binned.value_counts()
                    hours_dist_observed = (obs_vc / obs_vc.sum()).to_dict() if obs_vc.sum() > 0 else {}
                    
                    # Hours distribution for predicted
                    expected_hours_list = []
                    for idhh, group_df in df_cou.groupby('idhh'):
                        exp_h = (group_df['prob'] * group_df[hours_col]).sum()
                        expected_hours_list.append(exp_h)
                    expected_hours_arr = np.array(expected_hours_list)
                    pred_binned = pd.cut(expected_hours_arr, bins=bins, labels=bin_labels, include_lowest=True)
                    pred_vc = pred_binned.value_counts()
                    hours_dist_predicted = (pred_vc / pred_vc.sum()).to_dict() if pred_vc.sum() > 0 else {}
                    
                    fit_results[group_key] = {
                        'participation_observed': obs_participation,
                        'participation_predicted': pred_participation,
                        'mean_hours_observed': obs_hours,
                        'mean_hours_predicted': pred_hours,
                        'hours_distribution_observed': hours_dist_observed,
                        'hours_distribution_predicted': hours_dist_predicted,
                    }
                    
                    LOGGER.info(f"  {group_key}: obs_part={obs_participation:.3f}, pred_part={pred_participation:.3f}")
                    
            except Exception as e:
                LOGGER.warning(f"Could not compute fit for couples: {e}")
                # Fallback to observed as approximation
                for gender, suffix in [('male', '_m'), ('female', '_f')]:
                    group_key = f'cou{suffix}'
                    hours_col = f'hours_{gender}'
                    chosen = df_couples[df_couples[chosen_col] == 1].copy()
                    obs_participation = (chosen[hours_col] > 0).mean()
                    obs_hours = chosen.loc[chosen[hours_col] > 0, hours_col].mean() if (chosen[hours_col] > 0).any() else 0.0
                    fit_results[group_key] = {
                        'participation_observed': obs_participation,
                        'participation_predicted': np.nan,
                        'mean_hours_observed': obs_hours,
                        'mean_hours_predicted': np.nan,
                    }
    
    return fit_results


def compute_beta_l_full(df: pd.DataFrame, params: Dict[str, float], suffix: str = '') -> np.ndarray:
    """
    Compute full beta_l(X) = beta_l0 + sum(beta_l_k * X_k) for each observation.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data with demographic columns
    params : Dict[str, float]
        Parameter dictionary with beta_l0, beta_l_age_norm, etc.
    suffix : str
        Suffix for couples ('_m' or '_f')
    
    Returns
    -------
    np.ndarray
        beta_l value for each observation
    """
    n = len(df)
    beta_l0_key = f'beta_l0{suffix}' if suffix else 'beta_l0'
    beta_l = np.full(n, params.get(beta_l0_key, params.get('beta_l0', 0.0)))
    
    # Mapping of parameter suffixes to column names
    covariate_mapping = {
        'age_norm': ['age_norm', 'age_normalized'],
        'age_norm2': ['age_norm2', 'age_normalized2', 'age_norm_sq'],
        'n_children': ['n_children', 'nch', 'num_children'],
        'educL': ['educL', 'educ_low', 'low_education'],
        'educH': ['educH', 'educ_high', 'high_education'],
    }
    
    for param_name, param_value in params.items():
        # Match beta_l_* parameters (but not beta_l0)
        if not param_name.startswith('beta_l_'):
            continue
        if 'beta_l0' in param_name:
            continue
        
        # Extract covariate name (e.g., 'age_norm' from 'beta_l_age_norm')
        cov_base = param_name.replace('beta_l_', '').replace(suffix, '')
        
        # Try to find the column in the dataframe
        col_found = None
        possible_cols = covariate_mapping.get(cov_base, [cov_base])
        
        # For couples, try gender-specific columns first
        if suffix:
            gender = 'male' if suffix == '_m' else 'female'
            for col in [f'{cov_base}_{gender}', f'{cov_base}{suffix}']:
                if col in df.columns:
                    col_found = col
                    break
        
        # Then try general columns
        if col_found is None:
            for col in possible_cols:
                if col in df.columns:
                    col_found = col
                    break
        
        if col_found is not None:
            beta_l += param_value * df[col_found].values
    
    return beta_l


def compute_marginal_utilities_at_chosen(
    parsed_params: ParsedParameters,
    mnl_base: Path,
) -> Dict[str, Any]:
    """
    Compute marginal utilities (MUC, MUL) at chosen alternatives.
    
    MUC = beta_c * c^(theta_c - 1)
    MUL = beta_l(X) * l^(theta_l - 1)
    
    where beta_l(X) = beta_l0 + sum_k(beta_l_k * X_k) is the full leisure 
    coefficient evaluated at each individual's characteristics.
    
    Returns
    -------
    Dict with keys:
        - 'by_group': Dict[str, Dict] with N, n_neg_muc, pct_neg_muc, mean_muc, etc.
        - 'totals': Dict with aggregate stats
        - 'arrays': Dict[str, Dict] with actual muc/mul arrays for plotting
    """
    LOGGER.info("Computing marginal utilities at chosen alternatives...")
    
    mnl_base = Path(mnl_base)
    mu_results = {'by_group': {}, 'totals': {}, 'arrays': {}}
    
    # Load data
    try:
        singles_path = Path(str(mnl_base) + '__singles.parquet')
        couples_path = Path(str(mnl_base) + '__couples.parquet')
        
        df_singles = pd.read_parquet(singles_path) if singles_path.exists() else None
        df_couples = pd.read_parquet(couples_path) if couples_path.exists() else None
    except Exception as e:
        LOGGER.warning(f"Could not load data for MU computation: {e}")
        return mu_results
    
    all_muc = []
    all_mul = []
    
    # Process singles
    for gender_code, gender_name, group_key in [(0, 'male', 'sm'), (1, 'female', 'sf')]:
        if df_singles is None:
            continue
        
        # Try 'dgn' first (dataset convention), then 'gender'
        gender_col = 'dgn' if 'dgn' in df_singles.columns else 'gender'
        chosen_col = 'is_chosen' if 'is_chosen' in df_singles.columns else 'chosen'
        df_g = df_singles[(df_singles[gender_col] == gender_code) & (df_singles[chosen_col] == 1)].copy()
        if len(df_g) == 0:
            continue
        
        params = None
        for try_key in [group_key, f'singles_{gender_name}']:
            if try_key in parsed_params.params_by_group:
                params = parsed_params.get_all_params_for_group(try_key)
                break
        
        if params is None:
            continue
        
        beta_c = params.get('beta_c', 1.0)
        theta_c = params.get('theta_c', 0.5)
        theta_l = params.get('theta_l', 0.5)
        
        c = df_g['consumption'].values
        l = df_g['leisure'].values
        
        # Compute MUC
        muc = compute_marginal_utility_consumption(c, beta_c, theta_c)
        
        # Compute full beta_l(X) for each observation
        beta_l = compute_beta_l_full(df_g, params, suffix='')
        
        # Compute MUL = beta_l(X) * l^(theta_l - 1)
        mul = beta_l * d_boxcox_dx(l, theta_l)
        
        all_muc.extend(muc)
        all_mul.extend(mul)
        
        # Store arrays for plotting
        mu_results['arrays'][group_key] = {'muc': muc, 'mul': mul}
        
        mu_results['by_group'][group_key] = {
            'N': len(df_g),
            'n_neg_muc': int((muc < 0).sum()),
            'pct_neg_muc': float(100 * (muc < 0).mean()),
            'n_neg_mul': int((mul < 0).sum()),
            'pct_neg_mul': float(100 * (mul < 0).mean()),
            'mean_muc': float(muc.mean()),
            'mean_mul': float(mul.mean()),
        }
        
        LOGGER.info(f"  {group_key}: {len(df_g)} obs, {(muc<0).sum()} neg MUC ({100*(muc<0).mean():.1f}%), {(mul<0).sum()} neg MUL ({100*(mul<0).mean():.1f}%)")
      # Process couples
    if df_couples is not None:
        chosen_col = 'is_chosen' if 'is_chosen' in df_couples.columns else 'chosen'
        df_chosen = df_couples[df_couples[chosen_col] == 1].copy()
        
        # Try to find couples parameters - check multiple possible group names
        params_m = None
        params_f = None
        
        # First, try 'm' and 'f' virtual groups (from joint estimation)
        if 'm' in parsed_params.params_by_group:
            params_m = parsed_params.get_all_params_for_group('m')
        if 'f' in parsed_params.params_by_group:
            params_f = parsed_params.get_all_params_for_group('f')
          # If not found, try 'cou' or 'couples' group with suffixed params
        if params_m is not None:
            # Get consumption parameters (shared between M and F in couples)
            beta_c = params_m.get('beta_c', 1.0)
            theta_c = params_m.get('theta_c', 0.5)
            
            c = df_chosen['consumption'].values
            muc = compute_marginal_utility_consumption(c, beta_c, theta_c)
            
            # Add MUC for couples to total (was missing before!)
            all_muc.extend(muc)
            
            # Males in couples
            theta_l_m = params_m.get('theta_l_m', params_m.get('theta_l', 0.5))
            l_m = df_chosen['leisure_male'].values
            beta_l_m = compute_beta_l_full(df_chosen, params_m, suffix='_m')
            mul_m = beta_l_m * d_boxcox_dx(l_m, theta_l_m)
            all_mul.extend(mul_m)
            
            mu_results['arrays']['cou_m'] = {'muc': muc, 'mul': mul_m}
            
            mu_results['by_group']['cou_m'] = {
                'N': len(df_chosen),
                'n_neg_muc': int((muc < 0).sum()),
                'pct_neg_muc': float(100 * (muc < 0).mean()),
                'n_neg_mul': int((mul_m < 0).sum()),
                'pct_neg_mul': float(100 * (mul_m < 0).mean()),
                'mean_muc': float(muc.mean()),
                'mean_mul': float(mul_m.mean()),
            }
            
            LOGGER.info(f"  cou_m: {len(df_chosen)} obs, {(muc<0).sum()} neg MUC ({100*(muc<0).mean():.1f}%), {(mul_m<0).sum()} neg MUL ({100*(mul_m<0).mean():.1f}%)")
            
            # Females in couples - use params_f if available, else fallback to params_m
            params_female = params_f if params_f is not None else params_m
            theta_l_f = params_female.get('theta_l_f', params_female.get('theta_l', 0.5))
            l_f = df_chosen['leisure_female'].values
            beta_l_f = compute_beta_l_full(df_chosen, params_female, suffix='_f')
            mul_f = beta_l_f * d_boxcox_dx(l_f, theta_l_f)
            all_mul.extend(mul_f)
            
            mu_results['arrays']['cou_f'] = {'muc': muc, 'mul': mul_f}
            
            mu_results['by_group']['cou_f'] = {
                'N': len(df_chosen),
                'n_neg_muc': int((muc < 0).sum()),
                'pct_neg_muc': float(100 * (muc < 0).mean()),
                'n_neg_mul': int((mul_f < 0).sum()),
                'pct_neg_mul': float(100 * (mul_f < 0).mean()),
                'mean_muc': float(muc.mean()),
                'mean_mul': float(mul_f.mean()),
            }
            
            LOGGER.info(f"  cou_f: {len(df_chosen)} obs, {(muc<0).sum()} neg MUC ({100*(muc<0).mean():.1f}%), {(mul_f<0).sum()} neg MUL ({100*(mul_f<0).mean():.1f}%)")
    
    # Compute totals
    if all_muc:
        all_muc = np.array(all_muc)
        all_mul = np.array(all_mul)
        mu_results['totals'] = {
            'n_negative_muc_total': int((all_muc < 0).sum()),
            'n_negative_mul_total': int((all_mul < 0).sum()),
            'pct_negative_muc_total': float(100 * (all_muc < 0).mean()),            'pct_negative_mul_total': float(100 * (all_mul < 0).mean()),
        }
        LOGGER.info(f"  Totals: {len(all_muc)} obs, {(all_muc<0).sum()} neg MUC ({100*(all_muc<0).mean():.1f}%), {(all_mul<0).sum()} neg MUL ({100*(all_mul<0).mean():.1f}%)")
    
    return mu_results


# =============================================================================
# PROBABILITY SANITY AND WORST-FIT DIAGNOSTICS
# =============================================================================

def compute_probability_diagnostics(
    parsed_params: ParsedParameters,
    mnl_base: Path,
) -> Dict[str, Any]:
    """
    Compute probability sanity diagnostics and worst-fit households.
    
    Returns
    -------
    Dict with:
        - prob_sum_errors: {max_error, mean_error, pct_off_by_0.01}
        - p_chosen_dist: {min, max, mean, median, q10, q25, q75, q90}
        - worst_fit_households: List of 20 households with lowest ll_i
    """
    LOGGER.info("Computing probability diagnostics...")
    
    mnl_base = Path(mnl_base)
    results = {
        'prob_sum_errors': {},
        'p_chosen_dist': {},
        'worst_fit_households': [],
    }
    
    try:
        singles_path = Path(str(mnl_base) + '__singles.parquet')
        couples_path = Path(str(mnl_base) + '__couples.parquet')
        
        df_singles = pd.read_parquet(singles_path) if singles_path.exists() else None
        df_couples = pd.read_parquet(couples_path) if couples_path.exists() else None
    except Exception as e:
        LOGGER.warning(f"Could not load data for probability diagnostics: {e}")
        return results
    
    all_prob_sums = []
    all_p_chosen = []
    all_ll_i = []  # (ll_i, idhh, group, p_chosen)
    
    # Helper to compute logit probabilities
    def compute_probs_for_df(df, params, is_couples=False, group_suffix=''):
        """Compute choice probabilities for a DataFrame."""
        df = df.copy()

        # Try with suffix first (for sm, sf groups)
        beta_c = params.get(f'beta_c{group_suffix}', params.get('beta_c', 1.0))
        theta_c = params.get(f'theta_c{group_suffix}', params.get('theta_c', 0.5))
        
        c = df['consumption'].values
        V = beta_c * boxcox_transform(c, theta_c)
        
        if is_couples:
            theta_l_m = params.get('theta_l_m', params.get('theta_l', 0.5))
            theta_l_f = params.get('theta_l_f', params.get('theta_l', 0.5))
            l_m = df['leisure_male'].values
            l_f = df['leisure_female'].values
            beta_l_m = compute_beta_l_full(df, params, '_m')
            beta_l_f = compute_beta_l_full(df, params, '_f')
            V += beta_l_m * boxcox_transform(l_m, theta_l_m)
            V += beta_l_f * boxcox_transform(l_f, theta_l_f)
              # Add opportunity terms - check multiple possible column names
            for col in ['log_q_total_male', 'log_opp_male', 'log_q_total_female', 'log_opp_female', 'log_q_total', 'log_opp']:
                if col in df.columns:
                    V += df[col].values
        else:
            theta_l = params.get(f'theta_l{group_suffix}', params.get('theta_l', 0.5))
            l = df['leisure'].values
            beta_l = compute_beta_l_full(df, params, group_suffix)
            V += beta_l * boxcox_transform(l, theta_l)
            
            # Add opportunity terms - check multiple possible column names
            for col in ['log_q_total', 'log_opp']:
                if col in df.columns:
                    V += df[col].values
                    break
        
        # Subtract prior - check multiple possible column names
        for prior_col in ['prior', 'log_prior']:
            if prior_col in df.columns:
                # 'prior' is already log_prior in some datasets
                V -= df[prior_col].values
                break
        
        df['V'] = V
        df['prob'] = 0.0
        
        for idhh, grp in df.groupby('idhh'):
            V_grp = grp['V'].values
            V_shifted = V_grp - V_grp.max()
            exp_V = np.exp(V_shifted)
            probs = exp_V / exp_V.sum()
            df.loc[grp.index, 'prob'] = probs
        
        return df
    
    # Process singles    if df_singles is not None and len(df_singles) > 0:
        # dgn=1 means male, dgn=0 means female
        for gender_code, group_key in [(1, 'sm'), (0, 'sf')]:
            gender_col = 'dgn' if 'dgn' in df_singles.columns else 'gender'
            df_g = df_singles[df_singles[gender_col] == gender_code].copy()
            if len(df_g) == 0:
                continue
            
            params = None
            for try_key in [group_key, group_key.upper()]:
                if try_key in parsed_params.params_by_group:
                    params = parsed_params.get_all_params_for_group(try_key)
                    break
            
            if params is None:
                continue
            
            try:
                df_g = compute_probs_for_df(df_g, params, is_couples=False, group_suffix=f'_{group_key}')
                chosen_col = 'is_chosen' if 'is_chosen' in df_g.columns else 'chosen'
                
                # Probability sums by household
                prob_sums = df_g.groupby('idhh')['prob'].sum().values
                all_prob_sums.extend(prob_sums)
                
                # P_chosen
                p_chosen = df_g.loc[df_g[chosen_col] == 1, 'prob'].values
                all_p_chosen.extend(p_chosen)
                
                # ll_i per household
                for idhh, p_ch in zip(df_g.loc[df_g[chosen_col] == 1, 'idhh'].values, p_chosen):
                    ll_i = np.log(max(p_ch, 1e-20))
                    all_ll_i.append((ll_i, idhh, group_key, p_ch))
                    
            except Exception as e:
                LOGGER.warning(f"Error computing probs for {group_key}: {e}")
                import traceback
                LOGGER.warning(traceback.format_exc())
    
    # Process couples
    if df_couples is not None and len(df_couples) > 0:
        # Try to find couples parameters - check multiple possible group names
        params = None
        for try_key in ['m', 'cou', 'couples']:
            if try_key in parsed_params.params_by_group:
                params = parsed_params.get_all_params_for_group(try_key)
                break
        
        if params is not None:
            try:
                df_cou = compute_probs_for_df(df_couples, params, is_couples=True)
                chosen_col = 'is_chosen' if 'is_chosen' in df_cou.columns else 'chosen'
                
                # Probability sums
                prob_sums = df_cou.groupby('idhh')['prob'].sum().values
                all_prob_sums.extend(prob_sums)
                
                # P_chosen
                p_chosen = df_cou.loc[df_cou[chosen_col] == 1, 'prob'].values
                all_p_chosen.extend(p_chosen)
                
                # ll_i per household
                for idhh, p_ch in zip(df_cou.loc[df_cou[chosen_col] == 1, 'idhh'].values, p_chosen):
                    ll_i = np.log(max(p_ch, 1e-20))
                    all_ll_i.append((ll_i, idhh, 'cou', p_ch))
                    
            except Exception as e:
                LOGGER.warning(f"Error computing probs for couples: {e}")
    
    # Compute summary statistics
    if all_prob_sums:
        prob_sums = np.array(all_prob_sums)
        errors = np.abs(prob_sums - 1.0)
        results['prob_sum_errors'] = {
            'max_error': float(errors.max()),
            'mean_error': float(errors.mean()),
            'pct_off_by_0.01': float(100 * (errors > 0.01).mean()),
            'pct_off_by_0.001': float(100 * (errors > 0.001).mean()),
        }
        LOGGER.info(f"  Prob sum errors: max={errors.max():.6f}, mean={errors.mean():.6f}")
    
    if all_p_chosen:
        p_chosen = np.array(all_p_chosen)
        results['p_chosen_dist'] = {
            'min': float(p_chosen.min()),
            'max': float(p_chosen.max()),
            'mean': float(p_chosen.mean()),
            'median': float(np.median(p_chosen)),
            'q10': float(np.percentile(p_chosen, 10)),
            'q25': float(np.percentile(p_chosen, 25)),
            'q75': float(np.percentile(p_chosen, 75)),
            'q90': float(np.percentile(p_chosen, 90)),
        }
        LOGGER.info(f"  P_chosen: mean={p_chosen.mean():.4f}, median={np.median(p_chosen):.4f}")
    
    # Worst-fit households (lowest ll_i)
    if all_ll_i:
        sorted_ll = sorted(all_ll_i, key=lambda x: x[0])[:20]
        results['worst_fit_households'] = [
            {'ll_i': ll, 'idhh': int(idhh), 'group': grp, 'p_chosen': float(p)}
            for ll, idhh, grp, p in sorted_ll
        ]
        LOGGER.info(f"  Worst ll_i: {sorted_ll[0][0]:.2f} (idhh={sorted_ll[0][1]})")
    
    return results


def compute_bound_diagnostics(parsed_params: ParsedParameters, tol: float = 1e-6) -> List[Dict[str, Any]]:
    """
    Find parameters within `tol` of their bounds.
    
    Returns list of dicts with: {parameter, estimate, bound, side}
    """
    at_bounds = []
    
    if parsed_params.bounds is None:
        return at_bounds
    
    for i, name in enumerate(parsed_params.param_names):
        if i >= len(parsed_params.bounds):
            continue
        
        lb, ub = parsed_params.bounds[i]
        val = parsed_params.theta[i]
        
        if lb is not None and abs(val - lb) < tol:
            at_bounds.append({
                'parameter': name,
                'estimate': val,
                'bound': lb,
                'side': 'lower',
            })
        elif ub is not None and abs(val - ub) < tol:
            at_bounds.append({
                'parameter': name,
                'estimate': val,
                'bound': ub,
                'side': 'upper',
            })
    
    if at_bounds:
        LOGGER.info(f"  Found {len(at_bounds)} parameters at bounds")
    
    return at_bounds


def detect_weight_column(df: pd.DataFrame, metadata: Dict = None) -> Optional[str]:
    """
    Detect sample weight column from metadata or common naming conventions.
    
    Returns column name if found, else None.
    """
    # Check metadata first
    if metadata:
        weight_col = metadata.get('weight_column')
        if weight_col and weight_col in df.columns:
            return weight_col
    
    # Common weight column names
    candidates = ['weight', 'wgt', 'sample_weight', 'pweight', 'pw', 'dwgt', 'wt', 'weights']
    for col in candidates:
        if col in df.columns:
            return col
        # Case-insensitive
        for c in df.columns:
            if c.lower() == col:
                return c
    
    return None


# =============================================================================
# STANDARD ERROR COMPUTATION
# =============================================================================

def _compute_and_update_standard_errors(
    parsed: ParsedParameters,
    data: Dict[str, Any],
    mnl_base: Path,
    spec_config: Path,
    results_json_path: Path,
) -> Tuple[ParsedParameters, Dict[str, Any]]:
    """
    Compute standard errors and update parsed results and JSON file.
    
    Parameters
    ----------
    parsed : ParsedParameters
        Parsed estimation results
    data : dict
        Raw JSON data
    mnl_base : Path
        Base path for MNL data files
    spec_config : Path
        Path to YAML specification
    results_json_path : Path
        Path to results JSON (will be updated)
        
    Returns
    -------
    Tuple of (updated_parsed, updated_data)
    """
    from estimation_utils import (
        load_and_validate_mnl_data,
        precompute_data_singles,
        precompute_data_couples,
    )
    from estimation_spec_parser import parse_specification
    from estimation_engine import compute_gradient_joint
    from scipy.stats import norm
    
    # Load specification
    spec = parse_specification(spec_config)
    
    # Get theta from results
    if 'results' in data and 'joint' in data['results']:
        theta = np.array(data['results']['joint']['theta'])
    else:
        # Try to reconstruct from parsed
        theta = parsed.theta
    
    LOGGER.info(f"   Loaded {len(theta)} parameters")

    # Identify free parameters (exclude those at bounds)
    n_params = len(theta)
    bounds_list = spec.get_bounds_tuple()
    bound_tol = 1e-6
    bound_range_tol = 1e-6
    free_mask = np.ones(n_params, dtype=bool)
    if len(bounds_list) != n_params:
        LOGGER.warning("   Bounds length mismatch; ignoring bounds for SE computation")
    else:
        for i, (lb, ub) in enumerate(bounds_list):
            if lb is None and ub is None:
                continue
            if lb is not None and ub is not None and (ub - lb) <= bound_range_tol:
                free_mask[i] = False
                continue
            if lb is not None and abs(theta[i] - lb) <= bound_tol:
                free_mask[i] = False
            elif ub is not None and abs(theta[i] - ub) <= bound_tol:
                free_mask[i] = False

    free_idx = np.where(free_mask)[0]
    n_free = len(free_idx)
    n_fixed = n_params - n_free
    if n_fixed > 0:
        LOGGER.info(f"   Computing Hessian for {n_free}/{n_params} free parameters ({n_fixed} at bounds/fixed)")
    
    # Load data
    singles_path = Path(str(mnl_base) + "__singles.parquet")
    couples_path = Path(str(mnl_base) + "__couples.parquet")
    metadata_path = Path(str(mnl_base) + "__mnlmeta.json")
    
    df_singles, df_couples, metadata = load_and_validate_mnl_data(
        singles_path=singles_path,
        couples_path=couples_path if couples_path.exists() else None,
        metadata_path=metadata_path,
        strict_validation=False
    )
    
    # Precompute data
    include_wage_vars = (spec.wage_spec in ["vw", "loc_empirical"])
    include_loc_vars = (spec.wage_spec == "loc_empirical")
    
    data_sm = None
    data_sf = None
    data_cou = None
    
    if df_singles is not None:
        df_sm = df_singles[df_singles["dgn"] == 1]
        df_sf = df_singles[df_singles["dgn"] == 0]
        
        if len(df_sm) > 0:
            data_sm = precompute_data_singles(
                df=df_sm, metadata=metadata, is_male=True,
                include_wage_vars=include_wage_vars, include_loc_vars=include_loc_vars
            )
        if len(df_sf) > 0:
            data_sf = precompute_data_singles(
                df=df_sf, metadata=metadata, is_male=False,
                include_wage_vars=include_wage_vars, include_loc_vars=include_loc_vars
            )
    
    if df_couples is not None:
        data_cou = precompute_data_couples(
            df=df_couples, metadata=metadata,
            include_wage_vars=include_wage_vars, include_loc_vars=include_loc_vars
        )
    
    # Build gradient function
    def grad_func(theta_):
        return compute_gradient_joint(theta_, data_sm, data_sf, data_cou, spec)
    
    # Compute Hessian numerically (free parameters only)
    eps = 1e-5
    if n_free == 0:
        LOGGER.warning("   No free parameters for SE computation; returning NaN SEs")
        H = None
    else:
        H = np.zeros((n_free, n_free))

        for col_idx, i in enumerate(free_idx):
            theta_plus = theta.copy()
            theta_minus = theta.copy()
            theta_plus[i] += eps
            theta_minus[i] -= eps

            g_plus = grad_func(theta_plus)
            g_minus = grad_func(theta_minus)

            H[:, col_idx] = (g_plus[free_idx] - g_minus[free_idx]) / (2 * eps)

            if (col_idx + 1) % 10 == 0:
                LOGGER.info(f"   Hessian column {col_idx+1}/{n_free}")

        # Symmetrize
        H = 0.5 * (H + H.T)

    # Eigenvalues and condition number (Hessian of negative log-likelihood)
    eigenvalues = None
    eigenvector_diagnostics = []
    condition_number = None
    n_negative = 0
    if H is not None:
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(H)
            n_negative = int(np.sum(eigenvalues < 0))
            finite_eigs = eigenvalues[np.isfinite(eigenvalues)]
            if finite_eigs.size:
                min_ev = np.nanmin(finite_eigs)
                max_ev = np.nanmax(finite_eigs)
                if min_ev > 0:
                    condition_number = max_ev / min_ev
            if eigenvectors is not None and n_free > 0:
                param_names = [spec.all_param_names[i] for i in free_idx]
                k = min(3, n_free)
                for idx in range(k):
                    ev = float(eigenvalues[idx]) if np.isfinite(eigenvalues[idx]) else None
                    vec = eigenvectors[:, idx]
                    order = np.argsort(np.abs(vec))[::-1][:5]
                    top_loadings = [
                        {'param': param_names[j], 'loading': float(vec[j])}
                        for j in order
                    ]
                    eigenvector_diagnostics.append({
                        'eigenvalue': ev,
                        'top_loadings': top_loadings
                    })
        except Exception as exc:
            LOGGER.warning(f"   Failed to compute Hessian eigenvalues: {exc}")

    # Compute SEs using pseudoinverse (free params only)
    if H is not None:
        varcov_free = np.linalg.pinv(H, rcond=1e-10)
        se_free = np.sqrt(np.abs(np.diag(varcov_free)))

        # Handle negative variances
        neg_var = np.diag(varcov_free) < 0
        if np.any(neg_var):
            se_free[neg_var] = np.nan

        varcov_full = np.full((n_params, n_params), np.nan)
        varcov_full[np.ix_(free_idx, free_idx)] = varcov_free
        se_full = np.full(n_params, np.nan)
        se_full[free_idx] = se_free
    else:
        varcov_full = None
        se_full = np.full(n_params, np.nan)

    # Compute t-values and p-values (free params only)
    t_values = np.full(n_params, np.nan)
    p_values = np.full(n_params, np.nan)
    with np.errstate(divide='ignore', invalid='ignore'):
        t_values[free_idx] = theta[free_idx] / se_full[free_idx]
        p_values[free_idx] = 2 * (1 - norm.cdf(np.abs(t_values[free_idx])))

    # Build top correlations (avoid dumping full matrix)
    top_correlations = []
    if varcov_full is not None:
        try:
            denom = np.outer(se_full, se_full)
            corr = np.divide(varcov_full, denom, out=np.full_like(varcov_full, np.nan), where=denom != 0)
            n_params = len(spec.all_param_names)
            pairs = []
            for i in range(n_params):
                for j in range(i + 1, n_params):
                    val = corr[i, j]
                    if not np.isfinite(val):
                        continue
                    if abs(val) >= 0.90:
                        pairs.append((abs(val), float(val), spec.all_param_names[i], spec.all_param_names[j]))
            pairs.sort(reverse=True)
            top_correlations = [
                {'param_i': p_i, 'param_j': p_j, 'corr': corr_val}
                for _, corr_val, p_i, p_j in pairs[:20]
            ]
        except Exception as exc:
            LOGGER.warning(f"   Failed to compute correlation diagnostics: {exc}")
    
    # Update parsed
    parsed.std_errors = se_full
    
    # Update JSON data
    se_list = [float(x) if not np.isnan(x) else None for x in se_full]
    t_list = [float(x) if not np.isnan(x) else None for x in t_values]
    p_list = [float(x) if not np.isnan(x) else None for x in p_values]
    
    if 'results' in data and 'joint' in data['results']:
        data['results']['joint']['standard_errors'] = se_list
        data['results']['joint']['t_values'] = t_list
        data['results']['joint']['p_values'] = p_list

        data['results']['joint']['hessian_diagnostics'] = {
            'condition_number': float(condition_number) if condition_number is not None else None,
            'min_eigenvalue': float(np.nanmin(eigenvalues)) if eigenvalues is not None else None,
            'max_eigenvalue': float(np.nanmax(eigenvalues)) if eigenvalues is not None else None,
            'n_negative_eigenvalues': n_negative,
            'poorly_identified_params': [],
            'eigenvalues': [float(x) if np.isfinite(x) else None for x in eigenvalues] if eigenvalues is not None else None,
            'eigenvector_diagnostics': eigenvector_diagnostics,
            'top_correlations': top_correlations
        }
    
    data['standard_errors'] = {
        'se': se_list,
        't_values': t_list,
        'p_values': p_list,
    }

    data['hessian_diagnostics'] = {
        'condition_number': float(condition_number) if condition_number is not None else None,
        'min_eigenvalue': float(np.nanmin(eigenvalues)) if eigenvalues is not None else None,
        'max_eigenvalue': float(np.nanmax(eigenvalues)) if eigenvalues is not None else None,
        'n_negative_eigenvalues': n_negative,
        'poorly_identified_params': [],
        'eigenvalues': [float(x) if np.isfinite(x) else None for x in eigenvalues] if eigenvalues is not None else None,
        'eigenvector_diagnostics': eigenvector_diagnostics,
        'top_correlations': top_correlations
    }
    
    # Save updated JSON
    with open(results_json_path, 'w') as f:
        json.dump(data, f, indent=2)
    LOGGER.info(f"   Updated {results_json_path} with standard errors")
    
    # Also save CSV
    params_df = pd.DataFrame({
        'parameter': spec.all_param_names,
        'estimate': theta,
        'std_error': se_full,
        't_value': t_values,
        'p_value': p_values,
    })
    csv_path = results_json_path.parent / 'params_with_se.csv'
    params_df.to_csv(csv_path, index=False)
    LOGGER.info(f"   Saved {csv_path}")
    
    return parsed, data


# =============================================================================
# MAIN POST-ESTIMATION PIPELINE
# =============================================================================

def run_styled_post_estimation(
    results_json_path: Path,
    mnl_base: Path = None,
    output_dir: Path = None,
    prefix: str = "",
    compute_se: bool = False,
    spec_config: Path = None,
) -> Dict[str, Any]:
    """
    Main entry point for styled post-estimation.

    Parameters
    ----------
    results_json_path : Path
        Path to estimation_results.json or legacy fr_2016_joint.json
    mnl_base : Path, optional
        Base path for MNL data files
    output_dir : Path, optional
        Output directory (defaults to results_json_path parent)
    prefix : str
        Prefix for output files
    compute_se : bool
        If True, compute standard errors if not present
    spec_config : Path, optional
        Path to YAML specification file (required for compute_se)

    Returns
    -------
    Dict with all results
    """
    post_est_start = time.time()

    LOGGER.info("=" * 70)
    LOGGER.info("RURO POST-ESTIMATION ANALYSIS (Styled Version)")
    LOGGER.info("=" * 70)

    results_json_path = Path(results_json_path)

    if output_dir is None:
        output_dir = results_json_path.parent / 'post_estimation'
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load estimation results
    LOGGER.info("\n1. Loading estimation results...")    # Try enhanced format first, then legacy
    try:
        parsed, data = load_estimation_results_from_json(results_json_path)
    except (KeyError, TypeError):
        LOGGER.info("  Trying legacy JSON format...")
        parsed, data = load_estimation_results_legacy(results_json_path)
    
    LOGGER.info(f"   Found {len(parsed.groups)} groups: {parsed.groups}")
    LOGGER.info(f"   Preference groups: {parsed.preference_groups}")

    # Check if SEs or diagnostics are missing and compute if requested
    se_computed = False
    hess_diag = data.get('hessian_diagnostics')
    needs_diag = (
        hess_diag is None or
        hess_diag.get('eigenvalues') is None or
        hess_diag.get('top_correlations') is None
    )
    se_missing = parsed.std_errors is None or np.all(np.isnan(parsed.std_errors))

    if se_missing or needs_diag:
        if se_missing:
            LOGGER.info("   Standard errors not found in results")
        if needs_diag:
            LOGGER.info("   Identification diagnostics are incomplete or missing")
        if compute_se:
            if mnl_base is None:
                LOGGER.warning("   Cannot compute SEs: --mnl-base required")
            elif spec_config is None:
                LOGGER.warning("   Cannot compute SEs: --spec-config required")
            else:
                LOGGER.info("   Computing standard errors from numerical Hessian...")
                try:
                    parsed, data = _compute_and_update_standard_errors(
                        parsed, data, mnl_base, spec_config, results_json_path
                    )
                    se_computed = True
                    LOGGER.info("   Standard errors computed and saved")
                except Exception as e:
                    LOGGER.error(f"   Failed to compute SEs: {e}")
        else:
            LOGGER.info("   Use --compute-se flag to compute them")

    # Extract timing info from results
    estimation_time = None
    if 'summary' in data:
        estimation_time = data['summary'].get('total_walltime_seconds')
    elif 'estimation_time_seconds' in data:
        estimation_time = data['estimation_time_seconds']

    # Compute fit statistics
    fit_stats = {}
    if 'summary' in data:
        summary = data['summary']
        fit_stats['log_likelihood'] = summary.get('joint_ll', 0)
        fit_stats['n_observations'] = summary.get('n_obs_total', 0)
        fit_stats['n_groups'] = summary.get('n_groups_total', 0)
        fit_stats['n_parameters'] = len(parsed.param_names)
        if fit_stats['n_observations'] > 0:
            fit_stats['AIC'] = -2 * fit_stats['log_likelihood'] + 2 * fit_stats['n_parameters']
            fit_stats['BIC'] = -2 * fit_stats['log_likelihood'] + np.log(fit_stats['n_observations']) * fit_stats['n_parameters']    # Compute elasticities
    LOGGER.info("\n2. Computing elasticities...")
    elasticities_df = compute_structural_elasticities(parsed)

    # MUC behavior analysis
    LOGGER.info("\n3. Analyzing MUC behavior...")
    muc_analysis = analyze_muc_behavior(parsed)

    # Compute fit diagnostics from data
    LOGGER.info("\n4. Computing fit diagnostics from MNL data...")
    fit_results = {}
    mu_results = {}
    ll_null = None
    n_obs_long = None
    n_individuals = None
    
    if mnl_base is not None:
        try:
            fit_results = compute_fit_diagnostics_from_data(parsed, mnl_base)
            mu_results = compute_marginal_utilities_at_chosen(parsed, mnl_base)
            
            # Compute LL0 if not in JSON
            if 'll_null' not in fit_stats or fit_stats['ll_null'] is None:
                try:
                    singles_path = Path(str(mnl_base) + '__singles.parquet')
                    if singles_path.exists():
                        df_temp = pd.read_parquet(singles_path)
                        ll_null = compute_null_log_likelihood(df_temp, 'idhh')
                        n_obs_long = len(df_temp)
                        n_individuals = df_temp['idhh'].nunique()
                        
                        couples_path = Path(str(mnl_base) + '__couples.parquet')
                        if couples_path.exists():
                            df_temp_c = pd.read_parquet(couples_path)
                            ll_null += compute_null_log_likelihood(df_temp_c, 'idhh')
                            n_obs_long += len(df_temp_c)
                            n_individuals += df_temp_c['idhh'].nunique()
                        
                        fit_stats['ll_null'] = ll_null
                        fit_stats['n_obs_long'] = n_obs_long
                        LOGGER.info(f"  Computed LL0 = {ll_null:.2f}")
                except Exception as e:
                    LOGGER.warning(f"Could not compute LL0: {e}")
        except Exception as e:
            LOGGER.warning(f"Could not compute fit diagnostics: {e}")
            # Fallback to placeholders
            for group in parsed.preference_groups:
                fit_results[group] = {
                    'participation_observed': np.nan,
                    'participation_predicted': np.nan,
                    'mean_hours_observed': np.nan,
                    'mean_hours_predicted': np.nan,
                }
    else:
        LOGGER.warning("No mnl-base provided, skipping data-driven diagnostics")
        for group in parsed.preference_groups:
            fit_results[group] = {
                'participation_observed': np.nan,
                'participation_predicted': np.nan,
                'mean_hours_observed': np.nan,
                'mean_hours_predicted': np.nan,
            }    # Compute rho-squared and AIC_per_obs now that we have ll_null
    ll = fit_stats.get('log_likelihood', 0)
    ll_null_val = fit_stats.get('ll_null')
    n_params = fit_stats.get('n_parameters', 0)
    n_obs = fit_stats.get('n_observations', 0)
    
    if ll_null_val is not None and ll_null_val != 0:
        fit_stats['rho_squared'] = 1 - (ll / ll_null_val)
        fit_stats['rho_squared_adj'] = 1 - ((ll - n_params) / ll_null_val)
        LOGGER.info(f"  Rho-squared: {fit_stats['rho_squared']:.4f}")
        LOGGER.info(f"  Adjusted Rho-squared: {fit_stats['rho_squared_adj']:.4f}")
    else:
        fit_stats['rho_squared'] = None
        fit_stats['rho_squared_adj'] = None
    
    if n_obs > 0:
        fit_stats['AIC_per_obs'] = fit_stats.get('AIC', 0) / n_obs
    else:
        fit_stats['AIC_per_obs'] = None    # Update fit_stats with MU totals
    if mu_results and 'totals' in mu_results:
        fit_stats.update(mu_results['totals'])

    # Compute probability diagnostics and worst-fit households
    prob_diagnostics = {}
    if mnl_base is not None:
        LOGGER.info("\n4b. Computing probability diagnostics...")
        try:
            prob_diagnostics = compute_probability_diagnostics(parsed, mnl_base)
        except Exception as e:
            LOGGER.warning(f"Could not compute probability diagnostics: {e}")
    
    # Compute bound diagnostics
    LOGGER.info("\n4c. Computing bound diagnostics...")
    bound_diagnostics = compute_bound_diagnostics(parsed)

    # Generate plots
    LOGGER.info("\n5. Generating plots...")
    plot_paths = {}

    plot_paths.update(plot_fit_comparison(fit_results, output_dir, prefix))
    plot_paths.update(plot_utility_contours_all_groups(parsed, output_dir, prefix))
    plot_paths.update(plot_mu_comparison(parsed, output_dir, prefix))
    plot_paths.update(plot_mu_distributions_by_group(mu_results, mnl_base, parsed, output_dir, prefix))
    plot_paths.update(plot_negative_mu_diagnostics(mu_results, output_dir, prefix))

    # Generate HTML report
    LOGGER.info("\n6. Generating HTML report...")

    post_est_end = time.time()
    post_estimation_time = post_est_end - post_est_start
    total_time = (estimation_time or 0) + post_estimation_time

    # Extract Hessian diagnostics from data (if available from GAMSPy estimation)
    hessian_diagnostics = data.get('hessian_diagnostics')
    if hessian_diagnostics is None:
        # Try to get from first group result
        results = data.get('results', {})
        for group_data in results.values():
            if 'hessian_diagnostics' in group_data:
                hessian_diagnostics = group_data['hessian_diagnostics']
                break

    # Generate timestamped filename for report
    report_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    html_path = output_dir / f'{prefix}post_estimation_report_{report_timestamp}.html'
    generate_html_report_styled(
        parsed_params=parsed,
        fit_results=fit_results,
        output_path=html_path,
        fit_stats=fit_stats,
        plot_paths=plot_paths,
        mu_results=mu_results,  # Real MU results now
        elasticities_df=elasticities_df,
        muc_analysis=muc_analysis,
        estimation_time_seconds=estimation_time,
        post_estimation_time_seconds=post_estimation_time,
        total_elapsed_seconds=total_time if estimation_time else None,
        prob_diagnostics=prob_diagnostics,
        bound_diagnostics=bound_diagnostics,
        hessian_diagnostics=hessian_diagnostics,
    )

    # Save CSV outputs
    LOGGER.info("\n7. Saving CSV outputs...")

    param_csv = output_dir / f'{prefix}params.csv'
    parsed.to_dataframe().to_csv(param_csv, index=False)
    LOGGER.info(f"   Parameters: {param_csv}")

    elast_csv = output_dir / f'{prefix}elasticities.csv'
    elasticities_df.to_csv(elast_csv, index=False)
    LOGGER.info(f"   Elasticities: {elast_csv}")

    LOGGER.info("\n" + "=" * 70)
    LOGGER.info("POST-ESTIMATION COMPLETE")
    LOGGER.info("=" * 70)
    LOGGER.info(f"  HTML Report: {html_path}")
    LOGGER.info(f"  Total Time: {post_estimation_time:.1f}s")

    return {
        'parsed_params': parsed,
        'fit_stats': fit_stats,
        'elasticities': elasticities_df,
        'muc_analysis': muc_analysis,
        'html_report': html_path,
        'param_csv': param_csv,
        'elasticities_csv': elast_csv,
        'plot_paths': plot_paths,
        'prob_diagnostics': prob_diagnostics,
        'bound_diagnostics': bound_diagnostics,
    }


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='RURO Post-Estimation Analysis (Styled Version)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--results-json',
        type=Path,
        required=True,
        help='Path to estimation_results.json or legacy JSON file'
    )

    parser.add_argument(
        '--mnl-base',        type=Path,
        default=None,
        help='Base path for MNL data files (optional)'
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default=None,
        help='Output directory (default: same as results-json parent)'
    )
    
    parser.add_argument(
        '--auto-timestamp',
        action='store_true',
        help='Automatically create timestamped subfolder: {output-dir}/run_{YYYY-MM-DD}_{HH-MM-SS}/'
    )
    
    parser.add_argument(
        '--prefix',
        type=str,
        default="",
        help='Prefix for output files'
    )
    
    parser.add_argument(
        '--bootstrap',
        type=int,
        default=0,
        metavar='N',
        help='Number of bootstrap replications for confidence intervals (default: 0 = disabled)'
    )

    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        metavar='S',
        help='Random seed for bootstrap reproducibility'
    )

    parser.add_argument(
        '--compute-se',
        action='store_true',
        help='Compute standard errors if not present in results (requires --spec-config)'
    )

    parser.add_argument(
        '--spec-config',
        type=Path,        default=None,
        help='Path to YAML specification file (required for --compute-se)'
    )

    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed is not None:
        np.random.seed(args.seed)
        LOGGER.info(f"Set random seed to {args.seed}")
    
    # Handle timestamped output directory
    output_dir = args.output_dir
    if args.auto_timestamp:
        from datetime import datetime
        timestamp = datetime.now().strftime("run_%Y-%m-%d_%H-%M-%S")
        if output_dir is None:
            output_dir = args.results_json.parent / timestamp
        else:
            output_dir = Path(output_dir) / timestamp
        print(f"Auto-timestamp enabled: {output_dir}")
        LOGGER.info(f"Timestamped output directory: {output_dir}")
    
    try:
        results = run_styled_post_estimation(
            results_json_path=args.results_json,
            mnl_base=args.mnl_base,
            output_dir=output_dir,
            prefix=args.prefix,
            compute_se=args.compute_se,
            spec_config=args.spec_config,
            # bootstrap=args.bootstrap,  # Future: pass to function when implemented
        )
        return 0
    except Exception as e:
        LOGGER.error(f"Post-estimation failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
