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
import re
from html import escape
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime

# Diagnostics bundle: shared schema for HTML + Markdown rendering
try:
    from diagnostics_bundle import (
        build_diagnostics_bundle,
        write_bundle_artifacts,
        render_fit_stats_split_html,
        render_fit_stats_split_markdown,
        render_solver_section_markdown,
        render_gradient_section_markdown,
        render_inference_section_markdown,
        render_decision_summary_markdown,
        # Phase 2: per-block parameter table, identification, solver,
        # probability-fit renderers shared between HTML and Markdown.
        render_param_table_html,
        render_identification_html,
        render_solver_html,
        render_probability_fit_html,
        render_param_table_markdown,
        render_identification_markdown,
        render_probability_fit_markdown,
        PROFILE_CHOICES,
        DEFAULT_PROFILE,
    )
    HAS_DIAGNOSTICS_BUNDLE = True
except ImportError:  # pragma: no cover - defensive
    HAS_DIAGNOSTICS_BUNDLE = False
    PROFILE_CHOICES = ("decision", "standard", "full", "technical")
    DEFAULT_PROFILE = "standard"


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


def _format_signed_value(value: float, fmt: str = ".4f") -> str:
    """Format a signed numeric value with explicit +/− and spacing."""
    if value < 0:
        return f"- {abs(value):{fmt}}"
    return f"+ {value:{fmt}}"


def _format_signed_term(value: float, term: str, fmt: str = ".4f") -> str:
    """Format a signed coefficient with a term."""
    return f"{_format_signed_value(value, fmt)} · {term}"


def _join_signed_terms(terms: List[str]) -> str:
    """Join signed terms, removing a leading '+' if present."""
    if not terms:
        return ""
    cleaned = []
    for i, term in enumerate(terms):
        if i == 0 and term.startswith("+ "):
            cleaned.append(term[2:])
        else:
            cleaned.append(term)
    return " ".join(cleaned)


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
# MODULE-LEVEL CONSTANTS
# =============================================================================

GROUP_LABELS = {
    'sm': 'Single Males',
    'sf': 'Single Females',
    'm': 'Males in Couples',
    'f': 'Females in Couples',
    'cou': 'Couples',
    'cou_m': 'Males in Couples',
    'cou_f': 'Females in Couples',
    'singles_male': 'Single Males',
    'singles_female': 'Single Females',
    'couples': 'Couples',
    'couples_m': 'Males in Couples',
    'couples_f': 'Females in Couples',
    'joint': 'Joint (All Groups)'
}

GROUP_SUFFIX_HINTS = {
    'sm': '_sm',
    'sf': '_sf',
    'm': '_m',
    'f': '_f',
    'singles_male': '_sm',
    'singles_female': '_sf',
    'cou_m': '_m',
    'cou_f': '_f',
    'couples_m': '_m',
    'couples_f': '_f',
}


def _infer_group_suffix(group: str) -> str:
    """Best-effort mapping from group label to parameter suffix."""
    return GROUP_SUFFIX_HINTS.get(group, '')


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


def _resolve_couples_theta_c(
    params: Dict[str, Any],
    spec: Optional[Any] = None,
    fallback: float = 0.5,
) -> float:
    """Return couples theta_c: fixed constant if spec says so, else from params, else fallback."""
    _fixed = getattr(spec, "utility_consumption_theta_couples_fixed", None) if spec is not None else None
    if _fixed is not None:
        return float(_fixed)
    v = params.get("theta_c", None)
    return float(v) if v is not None else fallback


def d_boxcox_dx(x: np.ndarray, theta: float, eps: float = 1e-10) -> np.ndarray:
    """Derivative of Box-Cox: d/dx [(x^θ - 1) / θ] = x^(θ-1)"""
    x = np.asarray(x)
    x = np.clip(x, eps, None)
    return np.power(x, theta - 1.0)


def compute_marginal_utility_consumption(
    c: np.ndarray,
    beta_c: float,
    theta_c: float,
    beta_cl: float = 0.0,
    bc_l: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Marginal utility of consumption.

    Separable case:
        MUC = β_c * dBC(c, θ_c)/dc

    With consumption-leisure interaction:
        U += β_cl * BC(c, θ_c) * BC(l, θ_l)
        MUC = [β_c + β_cl * BC(l, θ_l)] * dBC(c, θ_c)/dc
    """
    if bc_l is None:
        return beta_c * d_boxcox_dx(c, theta_c)
    return (beta_c + beta_cl * bc_l) * d_boxcox_dx(c, theta_c)


def compute_marginal_utility_leisure(
    l: np.ndarray,
    beta_l: np.ndarray,
    theta_l: float,
    beta_cl: float = 0.0,
    bc_c: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Marginal utility of leisure.

    Separable case:
        MUL = β_l(X) * dBC(l, θ_l)/dl

    With consumption-leisure interaction:
        U += β_cl * BC(c, θ_c) * BC(l, θ_l)
        MUL = [β_l(X) + β_cl * BC(c, θ_c)] * dBC(l, θ_l)/dl
    """
    if bc_c is None:
        return beta_l * d_boxcox_dx(l, theta_l)
    return (beta_l + beta_cl * bc_c) * d_boxcox_dx(l, theta_l)


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

def analyze_muc_behavior(parsed_params: ParsedParameters, spec: Optional[Any] = None) -> List[Dict[str, Any]]:
    """Analyze MUC behavior for well-behavedness checks."""
    rows = []

    for group in parsed_params.preference_groups:
        params = parsed_params.get_all_params_for_group(group)
        suffix = _infer_group_suffix(group)
        beta_c = _get_param_value(params, 'beta_c', (suffix,)) if suffix else _get_param_value(params, 'beta_c')
        theta_c = _get_param_value(params, 'theta_c', (suffix,)) if suffix else _get_param_value(params, 'theta_c')
        theta_l = _get_param_value(params, 'theta_l', (suffix,)) if suffix else _get_param_value(params, 'theta_l')
        beta_cl = _get_param_value(params, 'beta_cl', (suffix,)) if suffix else _get_param_value(params, 'beta_cl')

        beta_c = 1.0 if beta_c is None else beta_c
        # Use fixed couples theta_c when available (M0c_b); falls back to 0.5 for singles if absent.
        _is_couples = group not in ('sm', 'sf', 'singles_male', 'singles_female')
        theta_c = _resolve_couples_theta_c(params, spec) if (theta_c is None and _is_couples) else (0.5 if theta_c is None else theta_c)
        theta_l = 0.5 if theta_l is None else theta_l
        beta_cl = 0.0 if beta_cl is None else beta_cl

        # With interaction, MUC sign depends on leisure via (beta_c + beta_cl * BC(l)).
        l_grid = np.linspace(0.1, 2.5, 200)
        beta_c_eff = beta_c + beta_cl * boxcox_transform(l_grid, theta_l)
        muc_positive = bool(np.all(beta_c_eff > 0.0))
        muc_diminishing = theta_c < 1
        well_behaved = muc_positive and muc_diminishing

        # At normalized medians c=1,l=1, BC(1,theta)=0 so interaction drops out.
        muc_median = beta_c * (1.0 ** (theta_c - 1)) if beta_c > 0 else beta_c

        c_muc_1 = None
        if beta_c > 0 and theta_c != 1:
            try:
                c_muc_1 = (1.0 / beta_c) ** (1.0 / (theta_c - 1))
            except:
                pass

        notes = []
        if not muc_positive:
            notes.append("WARNING: β_c + β_cl·BC(l) ≤ 0 for some l, MUC can be non-positive")
        elif not muc_diminishing:
            notes.append(f"MUC is increasing (θ_c = {theta_c:.2f} > 1)")
        if abs(beta_cl) > 1e-12:
            notes.append("MUC varies with leisure due to β_cl interaction")

        group_label = GROUP_LABELS.get(group, group)

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

def compute_structural_elasticities(parsed_params: ParsedParameters, spec: Optional[Any] = None) -> pd.DataFrame:
    """Compute structural labor supply elasticities."""
    rows = []
    group_labels = GROUP_LABELS

    for group in parsed_params.preference_groups:
        params = parsed_params.get_all_params_for_group(group)

        if group in ['cou', 'couples']:
            # Handle couples - male
            theta_l_m = params.get('theta_l_m', params.get('theta_l', 0.5))
            theta_c = _resolve_couples_theta_c(params, spec)
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
    group_labels = GROUP_LABELS

    c_grid = np.linspace(0.05, 2.5, 100)
    l_grid = np.linspace(0.1, 2.5, 100)
    C, L = np.meshgrid(c_grid, l_grid)

    groups_to_plot = []

    for g in ['sm', 'sf', 'singles_male', 'singles_female']:
        if g in parsed_params.params_by_group:
            params = parsed_params.get_all_params_for_group(g)
            suffix = _infer_group_suffix(g)
            groups_to_plot.append((g, {
                'beta_c': _get_param_value(params, 'beta_c', (suffix,)) if suffix else params.get('beta_c', 1.0),
                'theta_c': _get_param_value(params, 'theta_c', (suffix,)) if suffix else params.get('theta_c', 0.5),
                'beta_l0': _get_param_value(params, 'beta_l0', (suffix,)) if suffix else params.get('beta_l0', 0.0),
                'theta_l': _get_param_value(params, 'theta_l', (suffix,)) if suffix else params.get('theta_l', 0.5),
                'beta_cl': _get_param_value(params, 'beta_cl', (suffix,)) if suffix else params.get('beta_cl', 0.0),
            }))
    for g in ['cou', 'couples']:
        if g in parsed_params.params_by_group:
            params = parsed_params.get_all_params_for_group(g)
            groups_to_plot.append((f'{g}_m', {
                'beta_c': params.get('beta_c', 1.0),
                'theta_c': params.get('theta_c', 0.5),
                'beta_l0': params.get('beta_l0_m', params.get('beta_l0', 0.0)),
                'theta_l': params.get('theta_l_m', params.get('theta_l', 0.5)),
                'beta_cl': params.get('beta_cl_m', params.get('beta_cl', 0.0)),
            }))
            groups_to_plot.append((f'{g}_f', {
                'beta_c': params.get('beta_c', 1.0),
                'theta_c': params.get('theta_c', 0.5),
                'beta_l0': params.get('beta_l0_f', params.get('beta_l0', 0.0)),
                'theta_l': params.get('theta_l_f', params.get('theta_l', 0.5)),
                'beta_cl': params.get('beta_cl_f', params.get('beta_cl', 0.0)),
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
                'beta_cl': params.get('beta_cl', 0.0),
            }))
        if 'f' in parsed_params.params_by_group:
            params = parsed_params.get_all_params_for_group('f')
            groups_to_plot.append(('cou_f', {
                'beta_c': params.get('beta_c', 1.0),
                'theta_c': params.get('theta_c', 0.5),
                'beta_l0': params.get('beta_l0', 0.0),
                'theta_l': params.get('theta_l', 0.5),
                'beta_cl': params.get('beta_cl', 0.0),
            }))

    for group, params in groups_to_plot:
        try:
            theta_c = params['theta_c']
            theta_l = params['theta_l']
            beta_c = params['beta_c']
            beta_l0 = params['beta_l0']
            beta_cl = params.get('beta_cl', 0.0) or 0.0
            theta_c = 0.5 if theta_c is None else theta_c
            theta_l = 0.5 if theta_l is None else theta_l
            beta_c = 1.0 if beta_c is None else beta_c
            beta_l0 = 0.0 if beta_l0 is None else beta_l0

            c_bc = boxcox_transform(C, theta_c)
            l_bc = boxcox_transform(L, theta_l)
            U = beta_l0 * l_bc + beta_c * c_bc + beta_cl * c_bc * l_bc

            finite_mask = np.isfinite(U)
            if not finite_mask.any():
                continue

            U_flat = U[finite_mask].flatten()
            levels = np.percentile(U_flat, [10, 25, 50, 75, 99])
            levels = np.unique(levels)

            fig, ax = plt.subplots(figsize=(8, 6))
            cf = ax.contourf(L, C, U.T, levels=20, cmap='RdYlGn', alpha=0.7)
            plt.colorbar(cf, ax=ax, label='Utility')
            cs = ax.contour(L, C, U.T, levels=levels, colors='black', linewidths=1.0)
            ax.clabel(cs, inline=True, fontsize=9)

            ax.set_xlabel('Normalized Leisure (l/l̄)')
            ax.set_ylabel('Normalized Consumption (c/c̄)')
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
    group_labels = GROUP_LABELS

    # MUC comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    # Reference point for interaction slices.
    l_ref = float(np.median(l_grid))
    for group in parsed_params.preference_groups:
        params = parsed_params.get_all_params_for_group(group)
        suffix = _infer_group_suffix(group)
        beta_c = _get_param_value(params, 'beta_c', (suffix,)) if suffix else params.get('beta_c', 1.0)
        theta_c = _get_param_value(params, 'theta_c', (suffix,)) if suffix else params.get('theta_c', 0.5)
        theta_l = _get_param_value(params, 'theta_l', (suffix,)) if suffix else params.get('theta_l', 0.5)
        beta_cl = _get_param_value(params, 'beta_cl', (suffix,)) if suffix else params.get('beta_cl', 0.0)

        beta_c = 1.0 if beta_c is None else beta_c
        theta_c = 0.5 if theta_c is None else theta_c
        theta_l = 0.5 if theta_l is None else theta_l
        beta_cl = 0.0 if beta_cl is None else beta_cl

        bc_l_ref = boxcox_transform(np.array([l_ref]), theta_l)[0]
        muc = compute_marginal_utility_consumption(
            c_grid,
            beta_c,
            theta_c,
            beta_cl=beta_cl,
            bc_l=np.full_like(c_grid, bc_l_ref),
        )
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
    c_ref = float(np.median(c_grid))
    for group in parsed_params.preference_groups:
        params = parsed_params.get_all_params_for_group(group)
        suffix = _infer_group_suffix(group)
        theta_l = _get_param_value(params, 'theta_l', (suffix,)) if suffix else params.get('theta_l', params.get('theta_l_m', 0.5))
        theta_c = _get_param_value(params, 'theta_c', (suffix,)) if suffix else params.get('theta_c', 0.5)
        beta_l0 = _get_param_value(params, 'beta_l0', (suffix,)) if suffix else params.get('beta_l0', params.get('beta_l0_m', 0.0))
        beta_cl = _get_param_value(params, 'beta_cl', (suffix,)) if suffix else params.get('beta_cl', 0.0)

        theta_l = 0.5 if theta_l is None else theta_l
        theta_c = 0.5 if theta_c is None else theta_c
        beta_l0 = 0.0 if beta_l0 is None else beta_l0
        beta_cl = 0.0 if beta_cl is None else beta_cl

        beta_l = np.full_like(l_grid, beta_l0)
        bc_c_ref = boxcox_transform(np.array([c_ref]), theta_c)[0]
        mul = compute_marginal_utility_leisure(
            l_grid,
            beta_l,
            theta_l,
            beta_cl=beta_cl,
            bc_c=np.full_like(l_grid, bc_c_ref),
        )
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
    group_labels = GROUP_LABELS

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
        beta_cl = params.get(f'beta_cl{suffix}', params.get('beta_cl', 0.0))
        beta_c = 1.0 if beta_c is None else beta_c
        theta_c = 0.5 if theta_c is None else theta_c
        theta_l = 0.5 if theta_l is None else theta_l
        beta_cl = 0.0 if beta_cl is None else beta_cl

        # Compute beta_l at median characteristics
        beta_l0 = params.get(f'beta_l0{suffix}', params.get('beta_l0', 0.0))
        beta_l0 = 0.0 if beta_l0 is None else beta_l0
        beta_l_median = beta_l0  # Start with intercept
        
        # Add median shifter contributions (approximate with 0 for normalized vars)
        for key, value in params.items():
            if key.startswith('beta_l_') and 'beta_l0' not in key:
                # Normalized continuous vars have median ~0, dummies ~0 (reference)
                pass  # Contribution is ~0 for normalized/centered variables
        
        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        l_ref = float(np.median(l_grid))
        c_ref = float(np.median(c_grid))
        bc_l_ref = boxcox_transform(np.array([l_ref]), theta_l)[0]
        bc_c_ref = boxcox_transform(np.array([c_ref]), theta_c)[0]

        # MUC curve
        muc = compute_marginal_utility_consumption(
            c_grid,
            beta_c,
            theta_c,
            beta_cl=beta_cl,
            bc_l=np.full_like(c_grid, bc_l_ref),
        )
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
        mul = compute_marginal_utility_leisure(
            l_grid,
            beta_l,
            theta_l,
            beta_cl=beta_cl,
            bc_c=np.full_like(l_grid, bc_c_ref),
        )
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
        beta_cl = params.get(f'beta_cl{suffix}', params.get('beta_cl', None))

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
                    U = β<sub>c</sub> · BC(C, θ<sub>c</sub>) + β<sub>l</sub>(X) · BC(L, θ<sub>l</sub>)"""

        if beta_cl is not None:
            symbolic_html += """
                    + β<sub>cl</sub> · BC(C, θ<sub>c</sub>) · BC(L, θ<sub>l</sub>)"""

        symbolic_html += """
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

        # Handle optional theta parameters (can be None for log utility)
        theta_c_str = f"{theta_c:.4f}" if theta_c is not None else "0 (log)"
        theta_l_str = f"{theta_l:.4f}" if theta_l is not None else "0 (log)"

        utility_terms = [f"{beta_c:.4f} · BC(C, {theta_c_str})"]
        if beta_cl is not None:
            utility_terms.append(
                _format_signed_term(
                    beta_cl,
                    f"BC(C, {theta_c_str}) · BC(L, {theta_l_str})",
                    ".4f",
                )
            )

        symbolic_html += f"U = {_join_signed_terms(utility_terms)} + ("
        inner_terms = [f"{beta_l0:.4f}"]
        for s, v in zip(shifters, shifter_vals):
            inner_terms.append(f"{_format_signed_term(v, s, '.4f')}")
        symbolic_html += f"{_join_signed_terms(inner_terms)}) · BC(L, {theta_l_str})"

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

    cond_display = "N/A"
    cond_suffix = ""

    # Fallback: if kappa is unavailable (e.g., non-positive min eigenvalue), use |eigenvalue| ratio.
    if condition_number is None and eigenvalues:
        finite_abs = [
            abs(v) for v in eigenvalues
            if v is not None and np.isfinite(v) and abs(v) > 1e-14
        ]
        if len(finite_abs) >= 2:
            condition_number = max(finite_abs) / min(finite_abs)
            cond_suffix = " (|eigenvalue| fallback)"

    # Color-code condition number
    if condition_number is None:
        cond_color = "var(--warning-color)"
        cond_status = "⚠ Condition Number Unavailable"
        cond_interpretation = (
            "Could not compute κ using the standard formula. "
            "This usually happens when Hessian eigenvalues are non-positive or near-zero "
            "(indicating weak identification or non-concavity)."
        )
    elif condition_number < 100:
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
    if condition_number is not None:
        cond_display = f"{condition_number:.2e}{cond_suffix}"

    min_ev_text = f"{min_eigenvalue:.2e}" if min_eigenvalue is not None and np.isfinite(min_eigenvalue) else "N/A"
    max_ev_text = f"{max_eigenvalue:.2e}" if max_eigenvalue is not None and np.isfinite(max_eigenvalue) else "N/A"

    # Build eigenvalue info
    eigenvalue_html = f"""
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1em; margin-top: 1em;">
            <div class="stats-box" style="border-left-color: #3498db;">
                <h4 style="margin-top:0;">Minimum Eigenvalue</h4>
                <p style="font-size: 1.5em; margin: 0;">{min_ev_text}</p>
            </div>
            <div class="stats-box" style="border-left-color: #3498db;">
                <h4 style="margin-top:0;">Maximum Eigenvalue</h4>
                <p style="font-size: 1.5em; margin: 0;">{max_ev_text}</p>
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
            <h3 style="margin-top:0;">Condition Number: {cond_display}</h3>
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


# ============================================================================
# Spec-driven opportunity-block rendering
# ----------------------------------------------------------------------------
# These helpers consume the raw YAML spec to render symbolic and numerical
# equations for the hours, market, wage, and occupation opportunity blocks.
# They are intentionally country/year/spec agnostic: they iterate over
# whichever shifters the YAML declares and bind them to estimated parameter
# values from `ParsedParameters`. Group suffixes (`_sm`, `_sf`, `_cm`, `_cf`,
# `_m`, `_f`) are tolerated when looking up estimates for a shared coefficient.
# Falls back gracefully if the YAML cannot be read; in that case the legacy
# hard-coded renderers below are used.
# ============================================================================

_GROUP_SUFFIXES: Tuple[str, ...] = (
    "_sm", "_sf", "_cm", "_cf", "_m", "_f",
    "_singles_male", "_singles_female", "_couples_male", "_couples_female",
    "_couples", "_joint",
)


def _load_yaml_spec_blocks(spec_path: Optional[Union[str, Path]]) -> Dict[str, Any]:
    """
    Re-parse the YAML spec to recover the four opportunity blocks distinctly.

    ``estimation_spec_parser.parse_specification`` appends occupation shifters
    into ``market_opportunity_shifters`` for engine convenience; we read the
    raw YAML directly so the renderer can keep the blocks separate.
    """
    if not spec_path:
        return {}
    try:
        import yaml
        with open(spec_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning(
            f"   Spec-driven rendering disabled: could not load YAML at "
            f"{spec_path}: {exc}"
        )
        return {}

    hours = (raw.get("hours_opportunity") or {}).get("shifters", []) or []
    market = (raw.get("market_opportunity") or {}).get("shifters", []) or []
    wage_opp = raw.get("wage_opportunity") or {}
    wage_mean = wage_opp.get("mean_shifters", []) or []
    wage_var = wage_opp.get("variance") or {}
    wage_sigma = wage_var.get("parameter") if isinstance(wage_var, dict) else None
    occ_opp = raw.get("occupation_opportunity") or {}
    occupation = occ_opp.get("shifters", []) or []
    occ_var = occ_opp.get("variable")
    occ_ref = occ_opp.get("reference")
    utility = raw.get("utility") or {}
    return {
        "hours": hours,
        "market": market,
        "wage_mean": wage_mean,
        "wage_sigma": wage_sigma,
        "wage_form": wage_opp.get("specification"),
        "occupation": occupation,
        "occ_var": occ_var,
        "occ_ref": occ_ref,
        "utility_leisure": (utility.get("leisure") or {}),
        "utility_consumption": (utility.get("consumption") or {}),
    }


def _strip_group_suffix(name: str) -> str:
    """Return ``name`` with any known group suffix removed."""
    for suf in _GROUP_SUFFIXES:
        if name.endswith(suf):
            return name[: -len(suf)]
    return name


def _coef_to_block_map(blocks: Dict[str, Any]) -> Dict[str, str]:
    """Map each declared coefficient to its block category."""
    out: Dict[str, str] = {}
    for sh in blocks.get("hours", []) or []:
        coef = (sh or {}).get("coefficient")
        if coef:
            out[coef] = "hours"
    for sh in blocks.get("market", []) or []:
        coef = (sh or {}).get("coefficient")
        if coef:
            out[coef] = "market"
    for sh in blocks.get("wage_mean", []) or []:
        coef = (sh or {}).get("coefficient")
        if coef:
            out[coef] = "wage"
    sigma = blocks.get("wage_sigma")
    if sigma:
        out[sigma] = "wage"
    for sh in blocks.get("occupation", []) or []:
        coef = (sh or {}).get("coefficient")
        if coef:
            out[coef] = "occupation"
    util_leisure = blocks.get("utility_leisure") or {}
    for key in ("intercept", "coefficient", "box_cox_exponent"):
        c = util_leisure.get(key)
        if c:
            out[c] = "preference"
    for sh in (util_leisure.get("shifters") or []):
        coef = (sh or {}).get("coefficient")
        if coef:
            out[coef] = "preference"
    util_cons = blocks.get("utility_consumption") or {}
    for key in ("coefficient", "box_cox_exponent"):
        c = util_cons.get(key)
        if c:
            out[c] = "preference"
    return out


_GROUP_PREFIXES: Tuple[str, ...] = (
    "joint.", "pref.", "sm.", "sf.", "cm.", "cf.", "m.", "f.",
    "singles_male.", "singles_female.", "couples_male.", "couples_female.",
    "couples.",
)


def _strip_group_prefix(name: str) -> str:
    """Return ``name`` with any known group prefix removed (e.g. joint.beta_E -> beta_E)."""
    for pref in _GROUP_PREFIXES:
        if name.startswith(pref):
            return name[len(pref):]
    return name


def _classify_param_via_blocks(name: str, coef_map: Dict[str, str]) -> Optional[str]:
    """Try exact match, then prefix-stripped, then suffix-stripped, then both."""
    if not coef_map:
        return None
    if name in coef_map:
        return coef_map[name]
    no_prefix = _strip_group_prefix(name)
    if no_prefix in coef_map:
        return coef_map[no_prefix]
    no_suffix = _strip_group_suffix(name)
    if no_suffix in coef_map:
        return coef_map[no_suffix]
    no_both = _strip_group_suffix(no_prefix)
    if no_both in coef_map:
        return coef_map[no_both]
    return None


def _format_coef_value(value: Any, fmt: str = ".4f") -> str:
    """Compact numeric formatting tolerant of NaN/None."""
    if value is None:
        return "?"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "?"
    if np.isnan(v):
        return "?"
    return format(v, fmt)


def _shifter_symbolic_term(shifter: Dict[str, Any]) -> str:
    coef = (shifter or {}).get("coefficient", "?")
    var = (shifter or {}).get("variable", "?")
    parts = [coef, var]
    for ix in (shifter.get("interaction") or []):
        if ix:
            parts.append(str(ix))
    return " * ".join(parts)


def _shifter_numerical_term(shifter: Dict[str, Any], value: Any) -> str:
    coef_str = _format_coef_value(value)
    var = (shifter or {}).get("variable", "?")
    parts = [coef_str, var]
    for ix in (shifter.get("interaction") or []):
        if ix:
            parts.append(str(ix))
    return " * ".join(parts)


def _pick_value_for_group(
    coef: str,
    group_label: str,
    parsed_params: "ParsedParameters",
) -> Optional[float]:
    """Resolve a coefficient's value for one group, with suffix fallback."""
    gp = parsed_params.get_all_params_for_group(group_label) if group_label else {}
    if not gp:
        return None
    if coef in gp:
        return gp[coef]
    for suf in _GROUP_SUFFIXES:
        cand = coef + suf
        if cand in gp:
            return gp[cand]
    alias_map = {
        "singles_male": "_sm",
        "singles_female": "_sf",
        "couples_male": "_cm",
        "couples_female": "_cf",
    }
    alias = alias_map.get(group_label)
    if alias and (coef + alias) in gp:
        return gp[coef + alias]
    return None


def _pick_value_for_coef(
    coef: str,
    parsed_params: "ParsedParameters",
    group_priority: Optional[List[str]] = None,
) -> Tuple[Optional[float], Optional[str]]:
    """Search for the first group that has a value (shared or suffixed)."""
    if group_priority is None:
        group_priority = list(getattr(parsed_params, "groups", []) or []) + [
            "joint", "sm", "sf", "cm", "cf", "m", "f",
            "couples_male", "couples_female", "couples",
        ]
    seen = set()
    for grp in group_priority:
        if grp in seen:
            continue
        seen.add(grp)
        val = _pick_value_for_group(coef, grp, parsed_params)
        if val is not None:
            return val, grp
    return None, None


def build_model_index_equation_html(blocks: Dict[str, Any]) -> str:
    """Render the top-level model-index equation, adapted to declared blocks."""
    has_hours = bool(blocks.get("hours") or blocks.get("market"))
    has_wage = bool(blocks.get("wage_mean") or blocks.get("wage_sigma"))
    has_occ = bool(blocks.get("occupation"))

    rhs_terms = ["U<sub>ij</sub>"]
    if has_hours:
        rhs_terms.append("O<sup>E</sup><sub>ij</sub> + O<sup>H</sup><sub>ij</sub>")
    if has_wage:
        rhs_terms.append("O<sup>W</sup><sub>ij</sub>")
    if has_occ:
        rhs_terms.append("O<sup>Occ</sup><sub>ij</sub>")
    rhs_terms.append("&minus; log&nbsp;prior<sub>ij</sub>")

    rhs = " &nbsp;+&nbsp; ".join(rhs_terms)
    return f"""
    <section>
        <h2>📐 Model Index</h2>
        <div class="stats-box">
            <div class="math-block symbolic">
                V<sub>ij</sub> = {rhs}
            </div>
            <div class="math-block symbolic" style="margin-top: 0.6em;">
                P<sub>ij</sub> = exp(V<sub>ij</sub>) / &Sigma;<sub>k&isin;C<sub>i</sub></sub> exp(V<sub>ik</sub>)
            </div>
            <p style="margin: 0.6em 0 0 0; font-size: 0.9em;">
                U is the utility of consumption and leisure; the O<sup>·</sup> terms
                are opportunity-density contributions (employment/hours, wage,
                occupation); <code>log&nbsp;prior</code> rescales each alternative
                to the data-generating measure. The terms displayed reflect the
                opportunity blocks declared in the active YAML specification.
            </p>
        </div>
    </section>
    """


def build_employment_hours_opportunity_html_specdriven(
    blocks: Dict[str, Any],
    parsed_params: "ParsedParameters",
    group_labels: Optional[Dict[str, str]] = None,
) -> str:
    """Render O^E + O^H from hours_opportunity + market_opportunity shifters."""
    hours_shifters = list(blocks.get("hours") or [])
    market_shifters = list(blocks.get("market") or [])
    all_shifters = hours_shifters + market_shifters
    if not all_shifters:
        return ""

    symb_parts = [_shifter_symbolic_term(sh) for sh in all_shifters]
    symbolic_html = "<br>&nbsp;&nbsp;&nbsp;&nbsp;+ ".join(symb_parts)

    groups = list(getattr(parsed_params, "groups", []) or []) or ["joint"]
    numerical_blocks: List[str] = []
    for grp in groups:
        terms: List[str] = []
        for sh in all_shifters:
            coef = (sh or {}).get("coefficient")
            if not coef:
                continue
            val = _pick_value_for_group(coef, grp, parsed_params)
            if val is None:
                val, _ = _pick_value_for_coef(coef, parsed_params, [grp] + groups)
            terms.append(_shifter_numerical_term(sh, val))
        if terms:
            label = (group_labels or {}).get(grp, grp)
            numerical_blocks.append(
                f"<div style='margin-top: 0.4em;'><strong>{escape(str(label))}:</strong> "
                + " &nbsp;+&nbsp; ".join(terms) + "</div>"
            )
    numerical_html = "\n".join(numerical_blocks) or "(no estimated values resolved)"

    return f"""
    <section>
        <h2>⏰ Employment and Hours Opportunity Parameters</h2>
        <p>Working-gated employment and hours intercepts. Combines
        <code>hours_opportunity.shifters</code> (base employment intercept and
        PT/FT focal-point indicators) with
        <code>market_opportunity.shifters</code> (working-gated residual market
        access terms like gsur, education).</p>
        <div class="stats-box">
            <h4 style="margin-top:0;">Symbolic form</h4>
            <div class="math-block symbolic">
                O<sup>E</sup> + O<sup>H</sup> =<br>
                &nbsp;&nbsp;&nbsp;&nbsp;{symbolic_html}
            </div>
            <h4 style="margin-top:1em;">Numerical form (by group)</h4>
            <div class="math-block numerical">{numerical_html}</div>
        </div>
    </section>
    """


def build_wage_opportunity_html_specdriven(
    blocks: Dict[str, Any],
    parsed_params: "ParsedParameters",
    group_labels: Optional[Dict[str, str]] = None,
) -> str:
    """Render the Mincer μ_w equation from wage_opportunity.mean_shifters."""
    mean_shifters = list(blocks.get("wage_mean") or [])
    if not mean_shifters and not blocks.get("wage_sigma"):
        return ""

    parts: List[str] = []
    for sh in mean_shifters:
        var = (sh or {}).get("variable")
        coef = (sh or {}).get("coefficient", "?")
        if var == "intercept":
            parts.append(coef)
        else:
            term_parts = [coef, str(var)]
            for ix in (sh.get("interaction") or []):
                if ix:
                    term_parts.append(str(ix))
            parts.append(" · ".join(term_parts))
    symbolic_mu = "<br>&nbsp;&nbsp;&nbsp;&nbsp;+ ".join(parts) if parts else "(no mean shifters)"
    sigma_name = blocks.get("wage_sigma") or "σ"

    groups = list(getattr(parsed_params, "groups", []) or []) or ["joint"]
    numerical_blocks: List[str] = []
    for grp in groups:
        terms: List[str] = []
        for sh in mean_shifters:
            coef = (sh or {}).get("coefficient")
            if not coef:
                continue
            val = _pick_value_for_group(coef, grp, parsed_params)
            if val is None:
                val, _ = _pick_value_for_coef(coef, parsed_params, [grp] + groups)
            var = (sh or {}).get("variable")
            if var == "intercept":
                terms.append(_format_coef_value(val))
            else:
                terms.append(_shifter_numerical_term(sh, val))
        if terms:
            sigma_val = None
            if blocks.get("wage_sigma"):
                sigma_val = _pick_value_for_group(blocks["wage_sigma"], grp, parsed_params)
                if sigma_val is None:
                    sigma_val, _ = _pick_value_for_coef(blocks["wage_sigma"], parsed_params, [grp] + groups)
            label = (group_labels or {}).get(grp, grp)
            sigma_html = (
                f"<br><span style='font-family: monospace;'>{escape(str(sigma_name))} = "
                f"{_format_coef_value(sigma_val)}</span>"
                if sigma_val is not None else ""
            )
            numerical_blocks.append(
                f"<div style='margin-top: 0.4em;'><strong>{escape(str(label))}:</strong> "
                f"μ<sub>w</sub> = " + " &nbsp;+&nbsp; ".join(terms)
                + sigma_html + "</div>"
            )

    numerical_html = "\n".join(numerical_blocks) or "(no estimated values resolved)"

    return f"""
    <section>
        <h2>💰 Wage Opportunity / Mincer Parameters</h2>
        <p>Log-normal wage opportunity:
        <code>log(wage) = μ<sub>w</sub>(X) + ε</code>,
        <code>ε ~ N(0, σ²)</code>. The mean μ<sub>w</sub> is built from
        <code>wage_opportunity.mean_shifters</code>.</p>
        <div class="stats-box">
            <h4 style="margin-top:0;">Symbolic form</h4>
            <div class="math-block symbolic">
                μ<sub>w</sub> =<br>
                &nbsp;&nbsp;&nbsp;&nbsp;{symbolic_mu}
                <br><br>
                log(wage) = μ<sub>w</sub> + ε,&nbsp;&nbsp; ε ~ N(0, {escape(str(sigma_name))}²)
            </div>
            <h4 style="margin-top:1em;">Numerical form (by group)</h4>
            <div class="math-block numerical">{numerical_html}</div>
        </div>
    </section>
    """


def build_occupation_opportunity_html_specdriven(
    blocks: Dict[str, Any],
    parsed_params: "ParsedParameters",
    group_labels: Optional[Dict[str, str]] = None,
) -> str:
    """Render occupation_opportunity grouped by ``applies_to``."""
    occ_shifters = list(blocks.get("occupation") or [])
    if not occ_shifters:
        return ""

    occ_var = blocks.get("occ_var") or "occ"
    occ_ref = blocks.get("occ_ref")

    by_group: Dict[str, List[Dict[str, Any]]] = {}
    for sh in occ_shifters:
        applies = (sh or {}).get("applies_to") or "both"
        by_group.setdefault(applies, []).append(sh)

    group_aliases = {
        "sm": "singles_male", "sf": "singles_female",
        "cm": "couples_male", "cf": "couples_female",
    }

    sections_html: List[str] = []
    for applies, sh_list in by_group.items():
        symb_parts = [_shifter_symbolic_term(sh) for sh in sh_list]
        symb_html = "<br>&nbsp;&nbsp;&nbsp;&nbsp;+ ".join(symb_parts)

        target_group = group_aliases.get(applies, applies)
        num_terms: List[str] = []
        groups = list(getattr(parsed_params, "groups", []) or []) or ["joint"]
        for sh in sh_list:
            coef = (sh or {}).get("coefficient")
            if not coef:
                continue
            val = _pick_value_for_group(coef, target_group, parsed_params)
            if val is None:
                val, _ = _pick_value_for_coef(coef, parsed_params, [target_group] + groups)
            num_terms.append(_shifter_numerical_term(sh, val))
        num_html = " &nbsp;+&nbsp; ".join(num_terms) if num_terms else "(no values)"
        label = (group_labels or {}).get(target_group, target_group)

        sections_html.append(f"""
        <div class="stats-box" style="margin-top: 0.6em;">
            <h4 style="margin-top:0;">{escape(str(label))} &nbsp;(<code>applies_to = {escape(str(applies))}</code>)</h4>
            <div class="math-block symbolic">
                O<sup>Occ</sup><sub>{escape(str(applies))}</sub> =<br>
                &nbsp;&nbsp;&nbsp;&nbsp;{symb_html}
            </div>
            <div class="math-block numerical" style="margin-top: 0.5em;">
                {num_html}
            </div>
        </div>
        """)

    ref_note = (
        f" Reference category: <code>{escape(str(occ_var))} = {escape(str(occ_ref))}</code>."
        if occ_ref is not None else ""
    )

    return f"""
    <section>
        <h2>🧭 Occupation Opportunity Parameters</h2>
        <p>Working-gated occupation shifters. Each <code>applies_to</code>
        group has its own coefficient set on the non-reference categories of
        <code>{escape(str(occ_var))}</code>.{ref_note}</p>
        {''.join(sections_html)}
    </section>
    """


# ============================================================================
# Legacy hard-coded renderers (used as fallback when YAML is unavailable)
# ============================================================================


def build_wage_equation_html_dynamic(wage_params: Dict[str, float]) -> str:
    """
    Build wage equation HTML dynamically based on actual parameters in wage_params.
    Only includes parameters that exist in the dictionary.
    """
    if not wage_params:
        return ""

    # Core wage parameters (always include if present)
    core_params = ['beta_w0', 'beta_w_educL', 'beta_w_educH', 'beta_pexp', 'beta_pexp2']

    # Additional demographic shifters
    demographic_params = ['beta_w_female', 'beta_w_couple', 'beta_w_age',
                         'beta_w_age2', 'beta_w_nc', 'beta_w_idf']

    # Build symbolic equation
    symbolic_parts = []
    if 'beta_w0' in wage_params:
        symbolic_parts.append('β<sub>w0</sub>')
    if 'beta_w_educL' in wage_params:
        symbolic_parts.append('β<sub>w,educL</sub> · educL')
    if 'beta_w_educH' in wage_params:
        symbolic_parts.append('β<sub>w,educH</sub> · educH')
    if 'beta_pexp' in wage_params:
        symbolic_parts.append('β<sub>pexp</sub> · experience')
    if 'beta_pexp2' in wage_params:
        symbolic_parts.append('β<sub>pexp²</sub> · experience²')

    # Add demographic shifters
    for param in demographic_params:
        if param in wage_params:
            var_name = param.replace('beta_w_', '')
            symbolic_parts.append(f'β<sub>w,{var_name}</sub> · {var_name}')

    symbolic_eq = ' + '.join(symbolic_parts) if symbolic_parts else '(no wage parameters)'

    # Build numerical equation
    numerical_parts = []
    if 'beta_w0' in wage_params:
        numerical_parts.append(f"{wage_params['beta_w0']:.4f}")
    if 'beta_w_educL' in wage_params:
        numerical_parts.append(_format_signed_term(wage_params['beta_w_educL'], "educL", ".4f"))
    if 'beta_w_educH' in wage_params:
        numerical_parts.append(_format_signed_term(wage_params['beta_w_educH'], "educH", ".4f"))
    if 'beta_pexp' in wage_params:
        numerical_parts.append(_format_signed_term(wage_params['beta_pexp'], "experience", ".4f"))
    if 'beta_pexp2' in wage_params:
        numerical_parts.append(_format_signed_term(wage_params['beta_pexp2'], "experience²", ".6f"))

    # Add demographic shifters
    for param in demographic_params:
        if param in wage_params:
            var_name = param.replace('beta_w_', '')
            numerical_parts.append(_format_signed_term(wage_params[param], var_name, ".4f"))

    numerical_eq = _join_signed_terms(numerical_parts) if numerical_parts else '(no wage parameters)'

    # Sigma
    sigma_html = ""
    if 'sigma' in wage_params:
        sigma_html = f"<br><br>σ = {wage_params['sigma']:.4f}"

    return f"""
    <div class="stats-box" style="margin-top: 1em;">
        <h4>Log-Wage Equation (Mincer Style)</h4>
        <div class="math-block symbolic">
            log(wage) = {symbolic_eq} + ε
            <br><br>
            where ε ~ N(0, σ²)
        </div>
        <div class="math-block numerical" style="margin-top: 1em;">
            log(wage) = {numerical_eq} + ε
            {sigma_html}
        </div>
    </div>
    """


def build_hours_opportunity_html_dynamic(wage_params: Dict[str, float]) -> str:
    """
    Build hours opportunity function HTML dynamically based on actual parameters.
    Only includes parameters that exist in wage_params dictionary.
    """
    if not wage_params:
        return ""

    # Core hours parameters (focal peaks)
    core_params = ['beta_work', 'beta_pt1', 'beta_pt2', 'beta_ft']

    # Additional shifters
    shifter_params = ['beta_gsur', 'beta_work_educL', 'beta_work_educH',
                     'beta_work_female', 'beta_work_couple', 'beta_work_idf',
                     'beta_work_age', 'beta_work_age2', 'beta_work_nc']

    # Build symbolic equation
    symbolic_parts = []
    if 'beta_work' in wage_params:
        symbolic_parts.append('β<sub>work</sub> · I(h>0)')
    if 'beta_pt1' in wage_params:
        symbolic_parts.append('β<sub>pt1</sub> · I(h∈[18.5,20.5])')
    if 'beta_pt2' in wage_params:
        symbolic_parts.append('β<sub>pt2</sub> · I(h∈[29.5,30.5])')
    if 'beta_ft' in wage_params:
        symbolic_parts.append('β<sub>ft</sub> · I(h∈[37.5,40.5])')

    # Add shifters
    if 'beta_gsur' in wage_params:
        symbolic_parts.append('β<sub>gsur</sub> · gsur')
    if 'beta_work_educL' in wage_params:
        symbolic_parts.append('β<sub>work,educL</sub> · educL')
    if 'beta_work_educH' in wage_params:
        symbolic_parts.append('β<sub>work,educH</sub> · educH')

    for param in ['beta_work_female', 'beta_work_couple', 'beta_work_idf',
                  'beta_work_age', 'beta_work_age2', 'beta_work_nc']:
        if param in wage_params:
            var_name = param.replace('beta_work_', '')
            symbolic_parts.append(f'β<sub>work,{var_name}</sub> · {var_name}')

    symbolic_eq = ' + '.join(symbolic_parts) if symbolic_parts else '(no hours parameters)'

    # Build numerical equation - split into lines for readability
    numerical_lines = []

    # Line 1: Core parameters
    line1_parts = []
    if 'beta_work' in wage_params:
        line1_parts.append(_format_signed_term(wage_params['beta_work'], "I(h>0)", ".4f"))
    if 'beta_pt1' in wage_params:
        line1_parts.append(_format_signed_term(wage_params['beta_pt1'], "I(h∈[18.5,20.5])", ".4f"))
    if 'beta_pt2' in wage_params:
        line1_parts.append(_format_signed_term(wage_params['beta_pt2'], "I(h∈[29.5,30.5])", ".4f"))
    if 'beta_ft' in wage_params:
        line1_parts.append(_format_signed_term(wage_params['beta_ft'], "I(h∈[37.5,40.5])", ".4f"))

    if line1_parts:
        numerical_lines.append(_join_signed_terms(line1_parts))

    # Line 2: Shifters
    line2_parts = []
    if 'beta_gsur' in wage_params:
        line2_parts.append(_format_signed_term(wage_params['beta_gsur'], "gsur", ".4f"))
    if 'beta_work_educL' in wage_params:
        line2_parts.append(_format_signed_term(wage_params['beta_work_educL'], "educL", ".4f"))
    if 'beta_work_educH' in wage_params:
        line2_parts.append(_format_signed_term(wage_params['beta_work_educH'], "educH", ".4f"))
    if 'beta_work_female' in wage_params:
        line2_parts.append(_format_signed_term(wage_params['beta_work_female'], "female", ".4f"))
    if 'beta_work_couple' in wage_params:
        line2_parts.append(_format_signed_term(wage_params['beta_work_couple'], "couple", ".4f"))
    if 'beta_work_idf' in wage_params:
        line2_parts.append(_format_signed_term(wage_params['beta_work_idf'], "idf", ".4f"))

    for param in ['beta_work_age', 'beta_work_age2', 'beta_work_nc']:
        if param in wage_params:
            var_name = param.replace('beta_work_', '')
            line2_parts.append(_format_signed_term(wage_params[param], var_name, ".4f"))

    if line2_parts:
        numerical_lines.append(_join_signed_terms(line2_parts))

    numerical_eq = '<br>                           + '.join(numerical_lines) if numerical_lines else '(no hours parameters)'

    return f"""
    <div class="stats-box" style="margin-top: 1em;">
        <h4>Hours Opportunity Function</h4>
        <div class="math-block symbolic">
            log h(h|X) = {symbolic_eq}
        </div>
        <div class="math-block numerical" style="margin-top: 1em;">
            log h(h|X) = {numerical_eq}
        </div>
    </div>
    """


def _extract_market_opportunity_params(parsed_params: ParsedParameters) -> Dict[str, float]:
    """
    Extract market-opportunity parameters (beta_offer_*) from parsed parameters.

    Returns the first non-empty block found across groups.
    """
    search_groups = list(parsed_params.groups) + ["joint", "sm", "sf", "m", "f", "cou", "couples"]
    seen = set()
    for group in search_groups:
        if group in seen:
            continue
        seen.add(group)
        params = parsed_params.get_all_params_for_group(group)
        offer_params = {k: v for k, v in params.items() if k.startswith("beta_offer_")}
        if offer_params:
            return offer_params
    return {}


def build_job_market_opportunity_html_dynamic(opportunity_params: Dict[str, float]) -> str:
    """
    Build job-market opportunity equation HTML dynamically for job-choice models.
    """
    if not opportunity_params:
        return ""

    label_map = {
        "working": "I(job > 0)",
        "hours_bin": "hours_bin",
        "wage_bin": "wage_bin",
        "isco1": "isco1",
        "gsur": "gsur",
        "educL": "educL",
        "educH": "educH",
        "age_norm": "age_norm",
        "age_norm2": "age_norm2",
        "pexp": "pexp_years",
        "pexp2": "pexp_years2",
        "reg2": "reg2",
        "reg3": "reg3",
        "reg4": "reg4",
        "reg5": "reg5",
        "reg6": "reg6",
        "reg7": "reg7",
        "reg8": "reg8",
    }
    ordered_bases = [
        "working", "hours_bin", "wage_bin", "isco1", "gsur",
        "educL", "educH", "age_norm", "age_norm2", "pexp", "pexp2",
        "reg2", "reg3", "reg4", "reg5", "reg6", "reg7", "reg8",
    ]

    ordered_keys = []
    for base in ordered_bases:
        key = f"beta_offer_{base}"
        if key in opportunity_params:
            ordered_keys.append(key)
    for key in sorted(opportunity_params.keys()):
        if key.startswith("beta_offer_") and key not in ordered_keys:
            ordered_keys.append(key)

    symbolic_terms = []
    numerical_terms = []
    for key in ordered_keys:
        base = key.replace("beta_offer_", "")
        var_label = label_map.get(base, base)
        symbolic_terms.append(f"beta_offer,{base} * {var_label}")
        numerical_terms.append(_format_signed_term(opportunity_params[key], var_label, ".4f"))

    symbolic_eq = " + ".join(symbolic_terms) if symbolic_terms else "(no market opportunity parameters)"
    numerical_eq = _join_signed_terms(numerical_terms) if numerical_terms else "(no market opportunity parameters)"

    return f"""
    <div class="stats-box" style="margin-top: 1em;">
        <h4>Job Market Opportunity Function</h4>
        <div class="math-block symbolic">
            log a(j|X) = {symbolic_eq}
        </div>
        <div class="math-block numerical" style="margin-top: 1em;">
            log a(j|X) = {numerical_eq}
        </div>
        <p style="margin-top: 0.75em; font-size: 0.9em;">
            This opportunity index is added to utility through +log a(j|X).
        </p>
    </div>
    """


def _get_param_value(params: Dict[str, float], base: str, suffixes: Tuple[str, ...] = ()) -> Optional[float]:
    """Fetch parameter value with optional suffix fallbacks."""
    for suf in suffixes:
        key = f"{base}{suf}"
        if key in params:
            return params[key]
    if base in params:
        return params[base]
    return None


def _resolve_column(df: pd.DataFrame, base: str, gender: Optional[str] = None) -> Optional[np.ndarray]:
    """Resolve a covariate column for a base name with optional gender suffix."""
    alias_map = {
        'age': ['age_norm'],
        'age2': ['age_norm2'],
        'age_norm': ['age_norm'],
        'age_norm2': ['age_norm2'],
        'n_children': ['n_children'],
        'nc': ['n_children'],
        'educL': ['educL'],
        'educH': ['educH'],
        'educM': ['educM'],
        'pexp': ['pexp_years'],
        'pexp2': ['pexp_years2'],
        'pexp_years': ['pexp_years'],
        'pexp_years2': ['pexp_years2'],
        'gsur': ['gsur', 'u_rate'],
    }

    bases = alias_map.get(base, [base])
    candidates = []
    for b in bases:
        if gender:
            candidates.extend([f"{b}_{gender}", f"{b}_{gender[0]}"])
        candidates.append(b)

    for col in candidates:
        if col in df.columns:
            return df[col].values

    if base.startswith('reg') and len(base) == 4 and base[3].isdigit():
        idx = int(base[3])
        reg_col = f"reg_nuts1_{idx}"
        if reg_col in df.columns:
            return df[reg_col].values
        if 'drgn1' in df.columns:
            return (df['drgn1'].values == idx).astype(float)

    if base in ('idf', 'reg1'):
        if 'reg_nuts1_1' in df.columns:
            return df['reg_nuts1_1'].values
        if 'drgn1' in df.columns:
            return (df['drgn1'].values == 1).astype(float)

    return None


def _compute_log_h(
    df: pd.DataFrame,
    params: Dict[str, float],
    hours_col: str,
    gender: Optional[str] = None,
    group_suffix: str = '',
    is_couple: bool = False,
    spec: Optional['EstimationSpec'] = None,
) -> np.ndarray:
    """Compute hours opportunity log-density using spec when available."""
    hours = df[hours_col].values
    working = (hours > 0).astype(float)
    pt1 = ((hours >= 18.5) & (hours <= 20.5)).astype(float)
    pt2 = ((hours >= 29.5) & (hours <= 30.5)).astype(float)
    ft = ((hours >= 37.5) & (hours <= 40.5)).astype(float)

    log_h = np.zeros(len(df))

    if spec is not None and spec.hours_shifters:
        suffixes = []
        if group_suffix:
            suffixes.append(group_suffix)
        if gender:
            suffixes.extend([f"_{gender}", f"_{gender[0]}"])

        for shifter in spec.hours_shifters:
            var_name = shifter.get('variable')
            coef_name = shifter.get('coefficient')
            interaction = shifter.get('interaction')
            if not var_name or not coef_name:
                continue
            coef_val = _get_param_value(params, coef_name, tuple(suffixes))
            if coef_val is None:
                continue

            if var_name == 'working':
                var = working
            elif var_name == 'working_pt1':
                var = pt1
            elif var_name == 'working_pt2':
                var = pt2
            elif var_name == 'working_ft':
                var = ft
            else:
                var = _resolve_column(df, var_name, gender=gender)
                if var is None:
                    continue

            if interaction == 'working':
                var = var * working

            log_h += coef_val * var

        return log_h

    beta_work = _get_param_value(params, 'beta_work', (group_suffix,))
    if beta_work is not None:
        log_h += beta_work * working

    beta_pt1 = _get_param_value(params, 'beta_pt1', (group_suffix,))
    if beta_pt1 is not None:
        log_h += beta_pt1 * pt1

    beta_pt2 = _get_param_value(params, 'beta_pt2', (group_suffix,))
    if beta_pt2 is not None:
        log_h += beta_pt2 * pt2

    beta_ft = _get_param_value(params, 'beta_ft', (group_suffix,))
    if beta_ft is not None:
        log_h += beta_ft * ft

    beta_gsur = _get_param_value(params, 'beta_gsur', (group_suffix,))
    if beta_gsur is not None:
        gsur = _resolve_column(df, 'gsur', gender=gender)
        if gsur is not None:
            log_h += beta_gsur * gsur * working

    female_flag = 1.0 if gender == 'female' else 0.0
    couple_flag = 1.0 if is_couple else 0.0

    for name, val in params.items():
        if not name.startswith('beta_work_'):
            continue
        base = name.replace('beta_work_', '')
        if base in ('work', 'pt1', 'pt2', 'ft'):
            continue

        if base in ('female', 'f'):
            var = female_flag
        elif base in ('couple', 'in_couple'):
            var = couple_flag
        else:
            var = _resolve_column(df, base, gender=gender)

        if var is not None:
            log_h += val * var * working

    return log_h


def _compute_log_w(
    df: pd.DataFrame,
    params: Dict[str, float],
    wage_col: str,
    hours_col: str,
    gender: Optional[str] = None,
    group_suffix: str = '',
    is_couple: bool = False,
    spec: Optional['EstimationSpec'] = None,
) -> np.ndarray:
    """Compute wage log-density using spec when available."""
    if wage_col not in df.columns:
        return np.zeros(len(df))

    if spec is not None and spec.wage_spec not in ('vw', 'vw_occupation', 'loc_empirical'):
        return np.zeros(len(df))

    sigma = _get_param_value(params, 'sigma', (group_suffix,))
    if sigma is None:
        return np.zeros(len(df))

    sigma = float(abs(sigma)) if abs(sigma) > 1e-12 else 1e-12
    wage = np.maximum(df[wage_col].values, 1e-12)
    log_wage = np.log(wage)
    working = (df[hours_col].values > 0).astype(float)

    mu_w = np.zeros(len(df))
    female_flag = 1.0 if gender == 'female' else 0.0
    couple_flag = 1.0 if is_couple else 0.0

    if spec is not None:
        suffixes = []
        if group_suffix:
            suffixes.append(group_suffix)
        if gender:
            suffixes.extend([f"_{gender}", f"_{gender[0]}"])

        for shifter in spec.wage_mean_shifters:
            var_name = shifter.get('variable')
            coef_name = shifter.get('coefficient')
            if not var_name or not coef_name:
                continue
            coef_val = _get_param_value(params, coef_name, tuple(suffixes))
            if coef_val is None:
                continue
            if var_name == 'intercept':
                mu_w += coef_val
                continue
            if var_name in ('female', 'f'):
                var = female_flag
            elif var_name in ('couple', 'in_couple'):
                var = couple_flag
            else:
                var = _resolve_column(df, var_name, gender=gender)
            if var is None:
                continue
            mu_w += coef_val * var
    else:
        beta_w0 = _get_param_value(params, 'beta_w0', (group_suffix,))
        if beta_w0 is not None:
            mu_w += beta_w0

        for name, val in params.items():
            if not name.startswith('beta_w_'):
                continue
            if name == 'beta_w0':
                continue
            base = name.replace('beta_w_', '')
            if base in ('female', 'f'):
                var = female_flag
            elif base in ('couple', 'in_couple'):
                var = couple_flag
            else:
                var = _resolve_column(df, base, gender=gender)
            if var is not None:
                mu_w += val * var

        beta_pexp = _get_param_value(params, 'beta_pexp', (group_suffix,))
        if beta_pexp is not None:
            pexp = _resolve_column(df, 'pexp', gender=gender)
            if pexp is not None:
                mu_w += beta_pexp * pexp

        beta_pexp2 = _get_param_value(params, 'beta_pexp2', (group_suffix,))
        if beta_pexp2 is not None:
            pexp2 = _resolve_column(df, 'pexp2', gender=gender)
            if pexp2 is not None:
                mu_w += beta_pexp2 * pexp2

    residual = log_wage - mu_w
    log_w_density = (
        -0.5 * (residual * residual) / (sigma * sigma)
        - np.log(sigma)
        - 0.5 * np.log(2.0 * np.pi)
    )

    return working * log_w_density


def _compute_opportunity_from_spec(
    df: pd.DataFrame,
    params: Dict[str, float],
    spec: 'EstimationSpec',
    applies_key: str,
    partner: Optional[str] = None,
) -> np.ndarray:
    """Reconstruct O = O_E + O_H + O_market + O_W + O_Occ from the spec.

    Mirrors ``Results/_participation_diag_ruro_occ_M0a_clean.py``'s V
    decomposition so the fit diagnostic matches the structural diagnostic.

    Parameters
    ----------
    applies_key : 'sm' | 'sf' | 'cm' | 'cf'
        Used to filter occupation shifters whose ``applies_to`` matches.
    partner : 'male' | 'female' | None
        For couples (``cm``/``cf``) selects the partner-specific columns
        (``working_male``, ``hours_male``, ``wage_male``, ``loc4_male``, …).
        For singles (``sm``/``sf``) pass ``None`` — bare column names are
        used (``working``, ``hours``, ``wage``, ``loc4``).
    """
    n = len(df)
    O = np.zeros(n)

    def col(name: str) -> Optional[np.ndarray]:
        # Resolve a column preferring the partner-suffixed variant.
        if partner is not None:
            for c in (f"{name}_{partner}", name):
                if c in df.columns:
                    return df[c].to_numpy(dtype=float)
        elif name in df.columns:
            return df[name].to_numpy(dtype=float)
        return None

    working = col('working')
    if working is None:
        hours = col('hours')
        working = (hours > 0).astype(float) if hours is not None else np.zeros(n)

    # --- O_E + O_H -- hours_opportunity shifters (working / working_pt1/2/ft).
    for shifter in (getattr(spec, 'hours_shifters', []) or []):
        coef_name = shifter.get('coefficient')
        var_name = shifter.get('variable')
        if not coef_name or not var_name or coef_name not in params:
            continue
        x = col(var_name)
        if x is None:
            continue
        O = O + float(params[coef_name]) * x

    # --- O_market AND O_Occ -- both live on spec.market_opportunity_shifters
    # (occupation shifters were appended by the spec parser).
    var_scales = getattr(spec, 'market_opportunity_variable_scales', {}) or {}
    for shifter in (getattr(spec, 'market_opportunity_shifters', []) or []):
        coef_name = shifter.get('coefficient')
        var_name = shifter.get('variable')
        if not coef_name or not var_name or coef_name not in params:
            continue
        applies_to = shifter.get('applies_to')
        if applies_to in ('sm', 'sf', 'cm', 'cf') and applies_to != applies_key:
            continue
        if var_name and var_name.startswith(('loc4_', 'loc_')):
            # Occupation indicator: loc4_k -> (loc4 == k).
            base, _, k_str = var_name.partition('_')
            try:
                k = int(k_str)
            except ValueError:
                continue
            loc = col(base)
            if loc is None:
                continue
            x = (loc.astype(int) == k).astype(float)
            scale = 1.0
        else:
            x = col(var_name)
            if x is None:
                continue
            scale = float(var_scales.get(var_name, 1.0)) if var_scales else 1.0
        contrib = float(params[coef_name]) * (x / scale)
        for ix in (shifter.get('interaction', []) or []):
            ix_arr = col(ix)
            if ix_arr is not None:
                contrib = contrib * ix_arr
        O = O + contrib

    # --- O_W -- log-normal wage density (zero on non-work rows).
    sigma_name = 'sigma'
    if getattr(spec, 'wage_mean_shifters', None) is not None:
        try:
            sigma_name = (spec.__dict__.get('wage_sigma_parameter') or 'sigma')
        except Exception:
            sigma_name = 'sigma'
    sigma_val = params.get(sigma_name, params.get('sigma'))
    if sigma_val is not None:
        sigma = float(abs(sigma_val)) if abs(float(sigma_val)) > 1e-12 else 1e-12
        mu = np.zeros(n)
        for shifter in (getattr(spec, 'wage_mean_shifters', []) or []):
            coef_name = shifter.get('coefficient')
            var_name = shifter.get('variable')
            if not coef_name or coef_name not in params:
                continue
            if var_name == 'intercept':
                mu = mu + float(params[coef_name])
                continue
            x = col(var_name)
            if x is None:
                continue
            mu = mu + float(params[coef_name]) * x
        wage = col('wage')
        if wage is not None:
            w_safe = np.clip(wage, 1e-12, None)
            log_w = (
                -np.log(w_safe)
                - np.log(sigma)
                - 0.5 * np.log(2.0 * np.pi)
                - 0.5 * ((np.log(w_safe) - mu) / sigma) ** 2
            )
            O = O + np.where(working > 0.5, log_w, 0.0)

    return O


def _add_predicted_probabilities(
    df: pd.DataFrame,
    params: Dict[str, float],
    spec: Optional['EstimationSpec'] = None,
    is_couples: bool = False,
    group_suffix: str = '',
) -> pd.DataFrame:
    """
    Compute predicted choice probabilities for a DataFrame and add 'pred_prob'.
    """
    df = df.copy()

    beta_c = params.get(f'beta_c{group_suffix}', params.get('beta_c', 1.0))

    # Resolve theta_c via the spec helper when available so M0a-clean's shared
    # singles curvature `theta_c_singles` is preferred for singles groups
    # instead of silently falling back to couples' `theta_c`.
    theta_c = None
    if spec is not None and group_suffix in ('_sm', '_sf') and hasattr(spec, 'theta_c_param_name'):
        group_key = 'singles_male' if group_suffix == '_sm' else 'singles_female'
        theta_name = spec.theta_c_param_name(group_key)
        if theta_name and theta_name in params:
            theta_c = params[theta_name]
    if theta_c is None:
        # M0c-b: when couples theta_c is structurally fixed, use the constant directly.
        _fixed = getattr(spec, "utility_consumption_theta_couples_fixed", None) if spec is not None else None
        if _fixed is not None and group_suffix not in ('_sm', '_sf'):
            theta_c = float(_fixed)
        else:
            theta_c = params.get(f'theta_c{group_suffix}', params.get('theta_c', 0.5))

    # Use RAW consumption/leisure to match the estimator (gamspy_estimation_vectorized
    # applies the Box-Cox to data.consumption / data.leisure, not the c_norm/l_norm
    # rescaled views in the parquet). The structural participation diagnostic uses
    # the same raw columns.
    c = df['consumption'].values
    c_bc = boxcox_transform(c, theta_c)
    V = beta_c * c_bc

    if is_couples:
        theta_l_m = params.get('theta_l_m', params.get('theta_l', 0.5))
        theta_l_f = params.get('theta_l_f', params.get('theta_l', 0.5))
        l_m = df['leisure_male'].values
        l_f = df['leisure_female'].values
        beta_l_m = compute_beta_l_full(df, params, '_m', spec=spec)
        beta_l_f = compute_beta_l_full(df, params, '_f', spec=spec)
        l_bc_m = boxcox_transform(l_m, theta_l_m)
        l_bc_f = boxcox_transform(l_f, theta_l_f)
        V += beta_l_m * l_bc_m
        V += beta_l_f * l_bc_f

        beta_cl_m = params.get('beta_cl_m', params.get('beta_cl', 0.0))
        beta_cl_f = params.get('beta_cl_f', params.get('beta_cl', 0.0))
        if beta_cl_m is None:
            beta_cl_m = 0.0
        if beta_cl_f is None:
            beta_cl_f = 0.0
        V += beta_cl_m * c_bc * l_bc_m
        V += beta_cl_f * c_bc * l_bc_f

        # Leisure-leisure interaction (M0b+): beta_ll * BC(L_m) * BC(L_f).
        # Zero contribution for M0a-clean (couples_interaction_coef is None).
        if spec is not None and hasattr(spec, 'couples_interaction_coef') \
                and spec.couples_interaction_coef \
                and spec.couples_interaction_coef in params:
            beta_ll = params[spec.couples_interaction_coef]
            V += beta_ll * l_bc_m * l_bc_f

        opp_added = False
        for col in ['log_opp_male', 'log_opp_female', 'log_opp']:
            if col in df.columns:
                V += df[col].values
                opp_added = True

        if not opp_added:
            if spec is not None:
                V += _compute_opportunity_from_spec(df, params, spec, applies_key='cm', partner='male')
                V += _compute_opportunity_from_spec(df, params, spec, applies_key='cf', partner='female')
            else:
                log_h_m = _compute_log_h(df, params, 'hours_male', gender='male', is_couple=True, spec=spec)
                log_h_f = _compute_log_h(df, params, 'hours_female', gender='female', is_couple=True, spec=spec)
                log_w_m = _compute_log_w(df, params, 'wage_male', 'hours_male', gender='male', is_couple=True, spec=spec)
                log_w_f = _compute_log_w(df, params, 'wage_female', 'hours_female', gender='female', is_couple=True, spec=spec)
                V += log_h_m + log_h_f + log_w_m + log_w_f
    else:
        theta_l = params.get(f'theta_l{group_suffix}', params.get('theta_l', 0.5))
        l = df['leisure'].values
        beta_l = compute_beta_l_full(df, params, group_suffix, spec=spec)
        l_bc = boxcox_transform(l, theta_l)
        V += beta_l * l_bc

        beta_cl = params.get(f'beta_cl{group_suffix}', params.get('beta_cl', 0.0))
        if beta_cl is None:
            beta_cl = 0.0
        V += beta_cl * c_bc * l_bc

        opp_added = False
        for col in ['log_opp']:
            if col in df.columns:
                V += df[col].values
                opp_added = True
                break

        if not opp_added:
            if spec is not None:
                applies_key = 'sf' if group_suffix in ('_sf', '_f') else 'sm'
                V += _compute_opportunity_from_spec(df, params, spec, applies_key=applies_key, partner=None)
            else:
                gender = 'female' if group_suffix in ('_sf', '_f') else 'male'
                log_h = _compute_log_h(df, params, 'hours', gender=gender, group_suffix=group_suffix, spec=spec)
                log_w = _compute_log_w(df, params, 'wage', 'hours', gender=gender, group_suffix=group_suffix, spec=spec)
                V += log_h + log_w

    # Correct for sampling/proposal density: subtract log(prior).
    if 'log_prior' in df.columns:
        V -= df['log_prior'].values
    elif 'prior' in df.columns:
        V -= np.log(np.maximum(df['prior'].values, 1e-300))

    df['V'] = V
    df['pred_prob'] = 0.0

    for idhh, grp in df.groupby('idhh'):
        V_grp = grp['V'].values
        V_shifted = V_grp - V_grp.max()
        exp_V = np.exp(V_shifted)
        probs = exp_V / exp_V.sum()
        df.loc[grp.index, 'pred_prob'] = probs

    return df


def plot_hours_distribution_comparison(
    parsed_params: ParsedParameters,
    mnl_base: Path,
    output_dir: Path,
    prefix: str = '',
    spec: Optional['EstimationSpec'] = None,
) -> Dict[str, Path]:
    """
    Generate histograms comparing observed vs predicted hours distributions.
    Returns dict mapping plot keys to file paths.
    """
    if not MATPLOTLIB_AVAILABLE:
        LOGGER.warning("Matplotlib not available, skipping hours distribution plots")
        return {}

    plot_paths = {}

    # Define bins for hours (0, 10, 18.5, 20.5, 29.5, 30.5, 37.5, 40.5, 50, 60+)
    bins = [0, 10, 18.5, 20.5, 29.5, 30.5, 37.5, 40.5, 50, 60, 100]
    bin_labels = ['0', '0-10', '10-18.5', 'PT1\n(18.5-20.5)', '20.5-29.5', 'PT2\n(29.5-30.5)', '30.5-37.5', 'FT\n(37.5-40.5)', '40.5-50', '50+']

    try:
        # Load data
        singles_path = Path(str(mnl_base) + '__singles.parquet')
        couples_path = Path(str(mnl_base) + '__couples.parquet')

        df_all_parts = []
        group_defs = []

        if singles_path.exists():
            df_singles = pd.read_parquet(singles_path)
            gender_col = 'dgn' if 'dgn' in df_singles.columns else 'gender'
            for gender_code, group_key in [(1, 'sm'), (0, 'sf')]:
                df_g = df_singles[df_singles[gender_col] == gender_code].copy()
                if len(df_g) == 0:
                    continue
                params = None
                for try_key in [group_key, group_key.upper()]:
                    if try_key in parsed_params.params_by_group:
                        params = parsed_params.get_all_params_for_group(try_key)
                        break
                if not params:
                    continue
                df_g = _add_predicted_probabilities(
                    df_g,
                    params,
                    spec=spec,
                    is_couples=False,
                    group_suffix=f'_{group_key}'
                )
                df_g['group'] = group_key
                df_all_parts.append(df_g)
                group_defs.append((f'singles_{"male" if group_key == "sm" else "female"}', df_g, 'hours'))

        if couples_path.exists():
            df_couples = pd.read_parquet(couples_path)
            params = None
            for try_key in ['joint', 'cou', 'couples', 'm']:
                if try_key in parsed_params.params_by_group:
                    params = parsed_params.get_all_params_for_group(try_key)
                    break
            if params:
                df_c = _add_predicted_probabilities(
                    df_couples,
                    params,
                    spec=spec,
                    is_couples=True
                )
                df_c['group'] = 'couples'
                df_all_parts.append(df_c)
                group_defs.append(('couples_male', df_c, 'hours_male'))
                group_defs.append(('couples_female', df_c, 'hours_female'))

        if not df_all_parts:
            LOGGER.warning("No MNL data files found for hours distribution plot")
            return {}

        df_all = pd.concat(df_all_parts, ignore_index=True)
        chosen_col = 'chosen' if 'chosen' in df_all.columns else 'is_chosen'

        def _build_obs_pred(df: pd.DataFrame, hours_col: str) -> Tuple[np.ndarray, np.ndarray]:
            obs_counts, _ = np.histogram(df.loc[df[chosen_col] == 1, hours_col].values, bins=bins)
            obs_freq = obs_counts / obs_counts.sum() * 100 if obs_counts.sum() > 0 else obs_counts
            pred_counts = np.zeros(len(bins) - 1)
            for i in range(len(bins) - 1):
                mask = (df[hours_col] >= bins[i]) & (df[hours_col] < bins[i+1])
                pred_counts[i] = df.loc[mask, 'pred_prob'].sum()
            pred_freq = pred_counts / pred_counts.sum() * 100 if pred_counts.sum() > 0 else pred_counts
            return obs_freq, pred_freq

        def _plot_dist(obs_freq: np.ndarray, pred_freq: np.ndarray, title: str, out_key: str) -> None:
            fig, ax = plt.subplots(figsize=(10, 6))
            x = np.arange(len(bin_labels))
            width = 0.35

            ax.bar(x - width/2, obs_freq, width, label='Observed', alpha=0.8, color='steelblue')
            ax.bar(x + width/2, pred_freq, width, label='Predicted', alpha=0.8, color='coral')

            ax.set_xlabel('Weekly Hours')
            ax.set_ylabel('Percentage (%)')
            ax.set_title(title)
            ax.set_xticks(x)
            ax.set_xticklabels(bin_labels, rotation=45, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')

            fig.tight_layout()
            output_path = output_dir / f'{prefix}{out_key}.png'
            fig.savefig(output_path, dpi=150)
            plt.close(fig)
            plot_paths[out_key] = output_path

        total_parts = []
        for _, df_src, hours_col in group_defs:
            total_parts.append(df_src[[hours_col, 'pred_prob', chosen_col]].rename(columns={hours_col: 'hours'}))
        df_total = pd.concat(total_parts, ignore_index=True)
        obs_total, pred_total = _build_obs_pred(df_total, 'hours')
        _plot_dist(obs_total, pred_total, 'Hours Distribution: Observed vs Predicted (Total)', 'hours_distribution_total')

        label_map = {
            'singles_male': 'Singles Male',
            'singles_female': 'Singles Female',
            'couples_male': 'Couples Male',
            'couples_female': 'Couples Female',
        }
        for key, df_src, hours_col in group_defs:
            obs_freq_g, pred_freq_g = _build_obs_pred(df_src, hours_col)
            _plot_dist(
                obs_freq_g,
                pred_freq_g,
                f'Hours Distribution: Observed vs Predicted ({label_map.get(key, key)})',
                f'hours_distribution_{key}'
            )

        LOGGER.info(f"   Generated {len(plot_paths)} hours distribution plots")

    except Exception as e:
        LOGGER.error(f"Error generating hours distribution plots: {e}")
        import traceback
        traceback.print_exc()

    return plot_paths


def plot_wage_distribution_comparison(
    parsed_params: ParsedParameters,
    mnl_base: Path,
    output_dir: Path,
    prefix: str = '',
    spec: Optional['EstimationSpec'] = None,
) -> Dict[str, Path]:
    """
    Generate smooth density curves comparing observed vs predicted wage distributions.
    Returns dict mapping plot keys to file paths.
    """
    if not MATPLOTLIB_AVAILABLE:
        LOGGER.warning("Matplotlib not available, skipping wage distribution plots")
        return {}

    try:
        from scipy.stats import gaussian_kde
    except ImportError:
        LOGGER.warning("scipy.stats not available, skipping wage distribution plots")
        return {}

    plot_paths = {}

    try:
        singles_path = Path(str(mnl_base) + '__singles.parquet')
        couples_path = Path(str(mnl_base) + '__couples.parquet')

        group_defs = []

        if singles_path.exists():
            df_singles = pd.read_parquet(singles_path)
            gender_col = 'dgn' if 'dgn' in df_singles.columns else 'gender'
            for gender_code, group_key in [(1, 'sm'), (0, 'sf')]:
                df_g = df_singles[df_singles[gender_col] == gender_code].copy()
                if len(df_g) == 0:
                    continue
                params = None
                for try_key in [group_key, group_key.upper()]:
                    if try_key in parsed_params.params_by_group:
                        params = parsed_params.get_all_params_for_group(try_key)
                        break
                if not params and 'joint' in parsed_params.params_by_group:
                    params = parsed_params.get_all_params_for_group('joint')
                if not params:
                    continue
                df_g = _add_predicted_probabilities(
                    df_g,
                    params,
                    spec=spec,
                    is_couples=False,
                    group_suffix=f'_{group_key}'
                )
                df_g['group'] = group_key
                group_defs.append((f'singles_{"male" if group_key == "sm" else "female"}', df_g, 'wage', 'hours'))

        if couples_path.exists():
            df_couples = pd.read_parquet(couples_path)
            params = None
            for try_key in ['joint', 'cou', 'couples', 'm']:
                if try_key in parsed_params.params_by_group:
                    params = parsed_params.get_all_params_for_group(try_key)
                    break
            if params:
                df_c = _add_predicted_probabilities(
                    df_couples,
                    params,
                    spec=spec,
                    is_couples=True
                )
                df_c['group'] = 'couples'
                group_defs.append(('couples_male', df_c, 'wage_male', 'hours_male'))
                group_defs.append(('couples_female', df_c, 'wage_female', 'hours_female'))

        if not group_defs:
            LOGGER.warning("No MNL data files found for wage distribution plot")
            return {}

        def _extract_obs_pred(df: pd.DataFrame, wage_col: str, hours_col: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
            chosen_col = 'chosen' if 'chosen' in df.columns else 'is_chosen'
            if hours_col not in df.columns or wage_col not in df.columns:
                return np.array([]), np.array([]), np.array([])
            df_working = df[df[hours_col] > 0].copy()
            obs_wages = df_working[df_working[chosen_col] == 1][wage_col].values
            obs_wages = obs_wages[np.isfinite(obs_wages)]
            pred_wages = df_working[wage_col].values
            pred_probs = df_working['pred_prob'].values
            mask = np.isfinite(pred_wages) & (pred_probs > 0)
            return obs_wages, pred_wages[mask], pred_probs[mask]

        def _plot_kde(obs_wages: np.ndarray, pred_wages: np.ndarray, pred_probs: np.ndarray,
                      title: str, out_key: str) -> None:
            fig, ax = plt.subplots(figsize=(10, 6))

            wage_min = None
            wage_max = None
            if obs_wages.size > 0:
                wage_min = obs_wages.min()
                wage_max = obs_wages.max()
            if pred_wages.size > 0:
                wage_min = pred_wages.min() if wage_min is None else min(wage_min, pred_wages.min())
                wage_max = pred_wages.max() if wage_max is None else max(wage_max, pred_wages.max())

            if obs_wages.size > 10:
                kde_obs = gaussian_kde(obs_wages)
                wage_range = np.linspace(obs_wages.min(), obs_wages.max(), 200)
                density_obs = kde_obs(wage_range)
                ax.plot(wage_range, density_obs, label='Observed', color='steelblue', linewidth=2)

            if pred_wages.size > 10 and pred_probs.sum() > 0:
                sample_size = min(10000, len(pred_wages))
                idx_sample = np.random.choice(len(pred_wages), size=sample_size, p=pred_probs / pred_probs.sum())
                pred_wages_sampled = pred_wages[idx_sample]
                kde_pred = gaussian_kde(pred_wages_sampled)
                wage_range_pred = np.linspace(pred_wages_sampled.min(), pred_wages_sampled.max(), 200)
                density_pred = kde_pred(wage_range_pred)
                ax.plot(wage_range_pred, density_pred, label='Predicted', color='coral', linewidth=2)

            if wage_min is not None and wage_max is not None and wage_min != wage_max:
                ax.set_xlim(wage_min, wage_max)

            ax.set_xlabel('Hourly Wage')
            ax.set_ylabel('Density')
            ax.set_title(title)
            ax.legend()
            ax.grid(True, alpha=0.3)

            fig.tight_layout()
            output_path = output_dir / f'{prefix}{out_key}.png'
            fig.savefig(output_path, dpi=150)
            plt.close(fig)
            plot_paths[out_key] = output_path

        obs_total_parts = []
        pred_w_total_parts = []
        pred_p_total_parts = []
        for _, df_src, wage_col, hours_col in group_defs:
            obs_w, pred_w, pred_p = _extract_obs_pred(df_src, wage_col, hours_col)
            if obs_w.size > 0:
                obs_total_parts.append(obs_w)
            if pred_w.size > 0:
                pred_w_total_parts.append(pred_w)
                pred_p_total_parts.append(pred_p)

        obs_total = np.concatenate(obs_total_parts) if obs_total_parts else np.array([])
        pred_w_total = np.concatenate(pred_w_total_parts) if pred_w_total_parts else np.array([])
        pred_p_total = np.concatenate(pred_p_total_parts) if pred_p_total_parts else np.array([])
        _plot_kde(
            obs_total,
            pred_w_total,
            pred_p_total,
            'Wage Distribution: Observed vs Predicted (Total, Working Only)',
            'wage_distribution_total',
        )

        label_map = {
            'singles_male': 'Singles Male',
            'singles_female': 'Singles Female',
            'couples_male': 'Couples Male',
            'couples_female': 'Couples Female',
        }
        for key, df_src, wage_col, hours_col in group_defs:
            obs_w, pred_w, pred_p = _extract_obs_pred(df_src, wage_col, hours_col)
            _plot_kde(
                obs_w,
                pred_w,
                pred_p,
                f'Wage Distribution: Observed vs Predicted ({label_map.get(key, key)}, Working Only)',
                f'wage_distribution_{key}',
            )

        LOGGER.info(f"   Generated {len(plot_paths)} wage distribution plots")

    except Exception as e:
        LOGGER.error(f"Error generating wage distribution plots: {e}")
        import traceback
        traceback.print_exc()

    return plot_paths


def plot_job_distribution_comparison(
    parsed_params: ParsedParameters,
    mnl_base: Path,
    output_dir: Path,
    prefix: str = '',
    spec: Optional['EstimationSpec'] = None,
    top_n: int = 20,
) -> Dict[str, Path]:
    """
    Generate observed vs predicted job-share plots (top-N job IDs).
    """
    if not MATPLOTLIB_AVAILABLE:
        LOGGER.warning("Matplotlib not available, skipping job distribution plots")
        return {}

    plot_paths: Dict[str, Path] = {}

    try:
        singles_path = Path(str(mnl_base) + '__singles.parquet')
        couples_path = Path(str(mnl_base) + '__couples.parquet')

        group_defs: List[Tuple[str, pd.DataFrame, str]] = []

        if singles_path.exists():
            df_singles = pd.read_parquet(singles_path)
            gender_col = 'dgn' if 'dgn' in df_singles.columns else 'gender'
            for gender_code, group_key in [(1, 'sm'), (0, 'sf')]:
                df_g = df_singles[df_singles[gender_col] == gender_code].copy()
                if len(df_g) == 0:
                    continue
                params = None
                for try_key in [group_key, group_key.upper(), 'joint']:
                    if try_key in parsed_params.params_by_group:
                        params = parsed_params.get_all_params_for_group(try_key)
                        break
                if not params:
                    continue
                df_g = _add_predicted_probabilities(
                    df_g, params, spec=spec, is_couples=False, group_suffix=f'_{group_key}'
                )
                if 'job_id' in df_g.columns:
                    group_defs.append((f'singles_{"male" if group_key == "sm" else "female"}', df_g, 'job_id'))

        if couples_path.exists():
            df_couples = pd.read_parquet(couples_path)
            params = None
            for try_key in ['joint', 'cou', 'couples', 'm']:
                if try_key in parsed_params.params_by_group:
                    params = parsed_params.get_all_params_for_group(try_key)
                    break
            if params:
                df_c = _add_predicted_probabilities(df_couples, params, spec=spec, is_couples=True)
                if 'job_id_male' in df_c.columns:
                    group_defs.append(('couples_male', df_c, 'job_id_male'))
                if 'job_id_female' in df_c.columns:
                    group_defs.append(('couples_female', df_c, 'job_id_female'))

        if not group_defs:
            LOGGER.warning("No job_id columns found for job distribution plots")
            return {}

        def _obs_pred_shares(df: pd.DataFrame, cat_col: str) -> Tuple[pd.Series, pd.Series]:
            chosen_col = 'chosen' if 'chosen' in df.columns else 'is_chosen'
            obs = df.loc[df[chosen_col] == 1, cat_col].value_counts(dropna=False).sort_index()
            pred = df.groupby(cat_col)['pred_prob'].sum().sort_index()
            obs = (obs / obs.sum() * 100.0) if obs.sum() > 0 else obs.astype(float)
            pred = (pred / pred.sum() * 100.0) if pred.sum() > 0 else pred.astype(float)
            return obs, pred

        def _plot_topn(obs: pd.Series, pred: pd.Series, title: str, out_key: str) -> None:
            combined = obs.add(pred, fill_value=0.0).sort_values(ascending=False)
            top_idx = list(combined.head(top_n).index)

            obs_top = obs.reindex(top_idx, fill_value=0.0)
            pred_top = pred.reindex(top_idx, fill_value=0.0)

            other_obs = obs.loc[~obs.index.isin(top_idx)].sum()
            other_pred = pred.loc[~pred.index.isin(top_idx)].sum()
            if other_obs > 0 or other_pred > 0:
                obs_top.loc['Other'] = other_obs
                pred_top.loc['Other'] = other_pred

            labels = [str(x) for x in obs_top.index]
            x = np.arange(len(labels))

            fig, ax = plt.subplots(figsize=(12, 6))
            width = 0.40
            ax.bar(x - width / 2, obs_top.values, width, label='Observed', alpha=0.85, color='steelblue')
            ax.bar(x + width / 2, pred_top.values, width, label='Predicted', alpha=0.85, color='coral')
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=60, ha='right')
            ax.set_ylabel('Share (%)')
            ax.set_xlabel('Job ID')
            ax.set_title(title)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            fig.tight_layout()

            output_path = output_dir / f'{prefix}{out_key}.png'
            fig.savefig(output_path, dpi=150)
            plt.close(fig)
            plot_paths[out_key] = output_path

        # Total
        total_parts = []
        for _, df_src, cat_col in group_defs:
            chosen_col = 'chosen' if 'chosen' in df_src.columns else 'is_chosen'
            total_parts.append(df_src[[cat_col, 'pred_prob', chosen_col]].rename(columns={cat_col: 'job_id', chosen_col: 'is_chosen'}))
        df_total = pd.concat(total_parts, ignore_index=True)
        obs_total, pred_total = _obs_pred_shares(df_total, 'job_id')
        _plot_topn(obs_total, pred_total, 'Job Distribution: Observed vs Predicted (Total, Top IDs)', 'job_distribution_total')

        # By group
        label_map = {
            'singles_male': 'Singles Male',
            'singles_female': 'Singles Female',
            'couples_male': 'Couples Male',
            'couples_female': 'Couples Female',
        }
        for key, df_src, cat_col in group_defs:
            obs_g, pred_g = _obs_pred_shares(df_src, cat_col)
            _plot_topn(
                obs_g,
                pred_g,
                f'Job Distribution: Observed vs Predicted ({label_map.get(key, key)}, Top IDs)',
                f'job_distribution_{key}',
            )

        LOGGER.info(f"   Generated {len(plot_paths)} job distribution plots")

    except Exception as e:
        LOGGER.error(f"Error generating job distribution plots: {e}")
        import traceback
        traceback.print_exc()

    return plot_paths


def plot_loc_distribution_comparison(
    parsed_params: ParsedParameters,
    mnl_base: Path,
    output_dir: Path,
    prefix: str = '',
    spec: Optional['EstimationSpec'] = None,
) -> Dict[str, Path]:
    """
    Generate observed vs predicted occupation (LOC/ISCO1) distribution plots.
    """
    if not MATPLOTLIB_AVAILABLE:
        LOGGER.warning("Matplotlib not available, skipping LOC distribution plots")
        return {}

    plot_paths: Dict[str, Path] = {}

    try:
        singles_path = Path(str(mnl_base) + '__singles.parquet')
        couples_path = Path(str(mnl_base) + '__couples.parquet')

        group_defs: List[Tuple[str, pd.DataFrame, str]] = []

        if singles_path.exists():
            df_singles = pd.read_parquet(singles_path)
            gender_col = 'dgn' if 'dgn' in df_singles.columns else 'gender'
            for gender_code, group_key in [(1, 'sm'), (0, 'sf')]:
                df_g = df_singles[df_singles[gender_col] == gender_code].copy()
                if len(df_g) == 0:
                    continue
                params = None
                for try_key in [group_key, group_key.upper(), 'joint']:
                    if try_key in parsed_params.params_by_group:
                        params = parsed_params.get_all_params_for_group(try_key)
                        break
                if not params:
                    continue
                df_g = _add_predicted_probabilities(
                    df_g, params, spec=spec, is_couples=False, group_suffix=f'_{group_key}'
                )
                if 'isco1' in df_g.columns:
                    group_defs.append((f'singles_{"male" if group_key == "sm" else "female"}', df_g, 'isco1'))

        if couples_path.exists():
            df_couples = pd.read_parquet(couples_path)
            params = None
            for try_key in ['joint', 'cou', 'couples', 'm']:
                if try_key in parsed_params.params_by_group:
                    params = parsed_params.get_all_params_for_group(try_key)
                    break
            if params:
                df_c = _add_predicted_probabilities(df_couples, params, spec=spec, is_couples=True)
                if 'isco1_male' in df_c.columns:
                    group_defs.append(('couples_male', df_c, 'isco1_male'))
                if 'isco1_female' in df_c.columns:
                    group_defs.append(('couples_female', df_c, 'isco1_female'))

        if not group_defs:
            LOGGER.warning("No LOC/ISCO columns found for LOC distribution plots")
            return {}

        def _obs_pred_shares(df: pd.DataFrame, cat_col: str) -> Tuple[pd.Series, pd.Series]:
            chosen_col = 'chosen' if 'chosen' in df.columns else 'is_chosen'
            obs = df.loc[df[chosen_col] == 1, cat_col].value_counts(dropna=False).sort_index()
            pred = df.groupby(cat_col)['pred_prob'].sum().sort_index()
            obs = (obs / obs.sum() * 100.0) if obs.sum() > 0 else obs.astype(float)
            pred = (pred / pred.sum() * 100.0) if pred.sum() > 0 else pred.astype(float)
            return obs, pred

        def _plot(obs: pd.Series, pred: pd.Series, title: str, out_key: str) -> None:
            idx = sorted(set(obs.index).union(set(pred.index)))
            obs_aligned = obs.reindex(idx, fill_value=0.0)
            pred_aligned = pred.reindex(idx, fill_value=0.0)
            labels = [str(x) for x in idx]
            x = np.arange(len(labels))

            fig, ax = plt.subplots(figsize=(10, 6))
            width = 0.40
            ax.bar(x - width / 2, obs_aligned.values, width, label='Observed', alpha=0.85, color='steelblue')
            ax.bar(x + width / 2, pred_aligned.values, width, label='Predicted', alpha=0.85, color='coral')
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.set_ylabel('Share (%)')
            ax.set_xlabel('LOC / ISCO1 Category')
            ax.set_title(title)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            fig.tight_layout()

            output_path = output_dir / f'{prefix}{out_key}.png'
            fig.savefig(output_path, dpi=150)
            plt.close(fig)
            plot_paths[out_key] = output_path

        # Total
        total_parts = []
        for _, df_src, cat_col in group_defs:
            chosen_col = 'chosen' if 'chosen' in df_src.columns else 'is_chosen'
            total_parts.append(df_src[[cat_col, 'pred_prob', chosen_col]].rename(columns={cat_col: 'isco1', chosen_col: 'is_chosen'}))
        df_total = pd.concat(total_parts, ignore_index=True)
        obs_total, pred_total = _obs_pred_shares(df_total, 'isco1')
        _plot(obs_total, pred_total, 'LOC / ISCO Distribution: Observed vs Predicted (Total)', 'loc_distribution_total')

        # By group
        label_map = {
            'singles_male': 'Singles Male',
            'singles_female': 'Singles Female',
            'couples_male': 'Couples Male',
            'couples_female': 'Couples Female',
        }
        for key, df_src, cat_col in group_defs:
            obs_g, pred_g = _obs_pred_shares(df_src, cat_col)
            _plot(
                obs_g,
                pred_g,
                f'LOC / ISCO Distribution: Observed vs Predicted ({label_map.get(key, key)})',
                f'loc_distribution_{key}',
            )

        LOGGER.info(f"   Generated {len(plot_paths)} LOC distribution plots")

    except Exception as e:
        LOGGER.error(f"Error generating LOC distribution plots: {e}")
        import traceback
        traceback.print_exc()

    return plot_paths


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
    n_iterations: int = None,
    prob_diagnostics: Dict[str, Any] = None,
    bound_diagnostics: List[Dict[str, Any]] = None,
    hessian_diagnostics: Dict[str, Any] = None,
    estimation_results_path: Optional[Path] = None,
    run_metadata: Optional[Dict[str, Any]] = None,
    diagnostics_bundle: Optional[Any] = None,
    report_profile: str = DEFAULT_PROFILE,
) -> Path:
    """
    Generate comprehensive HTML report with professional styling.

    Matches the aesthetics of vw_pooled_post_estimation_report.html

    If ``diagnostics_bundle`` is supplied, the report renders the four
    reorganized fit-statistics sections (A/B/C/D) from the shared bundle
    *before* the legacy combined "Model Fit Statistics" table, which is
    preserved inside a collapsed <details> appendix for backward
    compatibility (and is the only fit-stats view rendered under the
    'technical' profile's appendix mode).
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    group_labels = GROUP_LABELS

    if fit_stats is None:
        fit_stats = {}
    if elasticities_df is None:
        elasticities_df = compute_structural_elasticities(parsed_params)
    if muc_analysis is None:
        muc_analysis = analyze_muc_behavior(parsed_params)

    estimation_results_info = ""
    if estimation_results_path is not None:
        estimation_results_info = (
            f"<p><strong>Estimation Results Source:</strong> "
            f"<code>{escape(str(estimation_results_path))}</code></p>"
        )

    run_metadata = run_metadata or {}
    run_meta_items = []
    if run_metadata.get("spec_name"):
        run_meta_items.append(("Specification", run_metadata.get("spec_name")))
    if run_metadata.get("spec_config_path"):
        run_meta_items.append(("Specification File", f"<code>{escape(str(run_metadata.get('spec_config_path')))}</code>"))
    if run_metadata.get("model_family"):
        run_meta_items.append(("Model Family", run_metadata.get("model_family")))
    if run_metadata.get("market_opportunity_tier"):
        run_meta_items.append(("Opportunity Tier", run_metadata.get("market_opportunity_tier")))

    if run_metadata.get("prior_correction_applied") is not None:
        run_meta_items.append((
            "Proposal Correction",
            "Enabled" if bool(run_metadata.get("prior_correction_applied")) else "Disabled"
        ))
    if run_metadata.get("prior_correction_form"):
        run_meta_items.append(("Proposal Correction Form", run_metadata.get("prior_correction_form")))
    if run_metadata.get("market_centering_applied") is not None:
        run_meta_items.append((
            "Opportunity Centering",
            "Enabled" if bool(run_metadata.get("market_centering_applied")) else "Disabled"
        ))

    run_metadata_html = ""
    if run_meta_items:
        run_rows = "".join(
            f"<tr><th>{escape(str(k))}</th><td>{v}</td></tr>"
            for k, v in run_meta_items
        )
        run_metadata_html = f"""
        <div class="stats-box" style="margin-top: 1em;">
            <h4 style="margin-top:0;">Estimation Configuration</h4>
            <table class="table table-sm" style="width:auto; margin-bottom:0;">
                {run_rows}
            </table>
        </div>
        """

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
    .param-table .degenerate-se-row { background-color: #fff3cd !important; }
    .param-table .degenerate-se-cell { background-color: #ffe69c !important; font-weight: 600; }
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
    # Bundle-driven split sections (A/B/C/D) + Phase-2 sections (solver,
    # identification, probability-fit, parameter table). All fall back to
    # empty string if diagnostics_bundle was not supplied or the bundle
    # module is unavailable.
    fit_stats_split_html = ""
    solver_bundle_html = ""
    identification_bundle_html = ""
    probability_fit_bundle_html = ""
    param_table_bundle_html = ""
    if diagnostics_bundle is not None and HAS_DIAGNOSTICS_BUNDLE:
        try:
            fit_stats_split_html = render_fit_stats_split_html(diagnostics_bundle)
        except Exception as e:
            LOGGER.warning(f"Could not render split fit-stats sections: {e}")
            fit_stats_split_html = ""
        try:
            solver_bundle_html = render_solver_html(diagnostics_bundle)
        except Exception as e:
            LOGGER.warning(f"Could not render bundle solver section: {e}")
            solver_bundle_html = ""
        try:
            identification_bundle_html = render_identification_html(diagnostics_bundle)
        except Exception as e:
            LOGGER.warning(f"Could not render bundle identification section: {e}")
            identification_bundle_html = ""
        try:
            probability_fit_bundle_html = render_probability_fit_html(diagnostics_bundle)
        except Exception as e:
            LOGGER.warning(f"Could not render bundle probability-fit section: {e}")
            probability_fit_bundle_html = ""
        try:
            param_table_bundle_html = render_param_table_html(diagnostics_bundle)
        except Exception as e:
            LOGGER.warning(f"Could not render bundle parameter table: {e}")
            param_table_bundle_html = ""

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
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1em; text-align: center;">
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
        <div>
          <div style="font-size: 0.9em; opacity: 0.8;">Iterations</div>
          <div class="time-value">{n_iterations if n_iterations is not None else 'N/A'}</div>
        </div>
      </div>
    </div>
    """    # Build elasticities table
    elasticities_html = ""
    if elasticities_df is not None and len(elasticities_df) > 0:
        elasticities_html = elasticities_df.to_html(classes='table table-striped', border=0, index=False)

    # Build model-specific specification blocks.
    # Spec-driven path: re-load the YAML and render the four opportunity blocks
    # generically. Falls back to legacy hard-coded renderers if YAML unavailable.
    _spec_path_for_blocks = run_metadata.get("spec_config_path") if run_metadata else None
    _spec_blocks = _load_yaml_spec_blocks(_spec_path_for_blocks)

    model_specific_sections_html = ""
    if _spec_blocks:
        # Top-of-section model index equation
        model_specific_sections_html += build_model_index_equation_html(_spec_blocks)

        # Employment / Hours Opportunity (hours + market shifters together)
        emp_hours_html = build_employment_hours_opportunity_html_specdriven(
            _spec_blocks, parsed_params, group_labels
        )
        # Wage Opportunity / Mincer
        wage_html_spec = build_wage_opportunity_html_specdriven(
            _spec_blocks, parsed_params, group_labels
        )
        # Occupation Opportunity
        occ_html_spec = build_occupation_opportunity_html_specdriven(
            _spec_blocks, parsed_params, group_labels
        )
        model_specific_sections_html += emp_hours_html + wage_html_spec + occ_html_spec

    # Always also resolve the legacy path for job-choice models / fallback.
    wage_params = {}
    for group in parsed_params.groups:
        params = parsed_params.get_all_params_for_group(group)
        if any(k.startswith('beta_w') for k in params.keys()):
            wage_params = params
            break
    if not wage_params and parsed_params.groups:
        wage_params = parsed_params.get_all_params_for_group(parsed_params.groups[0])

    market_opportunity_params = _extract_market_opportunity_params(parsed_params)
    is_job_choice_model = len(market_opportunity_params) > 0

    if is_job_choice_model:
        market_opportunity_html = build_job_market_opportunity_html_dynamic(market_opportunity_params)
        model_specific_sections_html += f"""
        <h3>Job Market Opportunity Equation (All Groups)</h3>
        {market_opportunity_html}
        """
    elif not _spec_blocks:
        # YAML unavailable AND not a job-choice model -> legacy renderers
        wage_equation_html = build_wage_equation_html_dynamic(wage_params)
        hours_opportunity_html = build_hours_opportunity_html_dynamic(wage_params)
        model_specific_sections_html += f"""
        <h3>Hours Opportunity Function (All Groups)</h3>
        {hours_opportunity_html}

        <h3>Wage Equation - Mincer (All Groups)</h3>
        {wage_equation_html}
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

        # Hours distribution plots
        hours_dist_plots = []
        hours_plot_order = [
            ('hours_distribution_total', 'Total'),
            ('hours_distribution_singles_male', 'Singles Male'),
            ('hours_distribution_singles_female', 'Singles Female'),
            ('hours_distribution_couples_male', 'Couples Male'),
            ('hours_distribution_couples_female', 'Couples Female'),
        ]
        for key, label in hours_plot_order:
            if key in plot_paths:
                hours_dist_plots.append(
                    f'<div class="plot-box"><img src="{plot_paths[key].name}" alt="Hours Distribution ({label})"></div>'
                )
        if hours_dist_plots:
            plots_section += f'<h3>?? Hours Distribution: Observed vs Predicted</h3><div class="contour-grid">{"".join(hours_dist_plots)}</div>'

        # Wage distribution plots
        wage_dist_plots = []
        wage_plot_order = [
            ('wage_distribution_total', 'Total'),
            ('wage_distribution_singles_male', 'Singles Male'),
            ('wage_distribution_singles_female', 'Singles Female'),
            ('wage_distribution_couples_male', 'Couples Male'),
            ('wage_distribution_couples_female', 'Couples Female'),
        ]
        for key, label in wage_plot_order:
            if key in plot_paths:
                wage_dist_plots.append(
                    f'<div class="plot-box"><img src="{plot_paths[key].name}" alt="Wage Distribution ({label})"></div>'
                )
        if wage_dist_plots:
            plots_section += f'<h3>?? Wage Distribution: Observed vs Predicted (Working Only)</h3><div class="contour-grid">{"".join(wage_dist_plots)}</div>'

        # Job distribution plots
        job_dist_plots = []
        job_plot_order = [
            ('job_distribution_total', 'Total'),
            ('job_distribution_singles_male', 'Singles Male'),
            ('job_distribution_singles_female', 'Singles Female'),
            ('job_distribution_couples_male', 'Couples Male'),
            ('job_distribution_couples_female', 'Couples Female'),
        ]
        for key, label in job_plot_order:
            if key in plot_paths:
                job_dist_plots.append(
                    f'<div class="plot-box"><img src="{plot_paths[key].name}" alt="Job Distribution ({label})"></div>'
                )
        if job_dist_plots:
            plots_section += f'<h3>?? Job Distribution: Observed vs Predicted</h3><div class="contour-grid">{"".join(job_dist_plots)}</div>'

        # LOC / ISCO distribution plots
        loc_dist_plots = []
        loc_plot_order = [
            ('loc_distribution_total', 'Total'),
            ('loc_distribution_singles_male', 'Singles Male'),
            ('loc_distribution_singles_female', 'Singles Female'),
            ('loc_distribution_couples_male', 'Couples Male'),
            ('loc_distribution_couples_female', 'Couples Female'),
        ]
        for key, label in loc_plot_order:
            if key in plot_paths:
                loc_dist_plots.append(
                    f'<div class="plot-box"><img src="{plot_paths[key].name}" alt="LOC Distribution ({label})"></div>'
                )
        if loc_dist_plots:
            plots_section += f'<h3>?? LOC / ISCO Distribution: Observed vs Predicted</h3><div class="contour-grid">{"".join(loc_dist_plots)}</div>'

    # Color legend
    color_legend = """
    <div class="color-legend">
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--bounded-row-color);"></div>Bounded (has constraints)</div>
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--bound-hit-color);"></div>⚠️ Hit bound</div>
      <div class="color-legend-item"><div class="color-box" style="background-color: #ffe69c;"></div>Warning: degenerate SE (near zero)</div>
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

    # Build YAML-driven coefficient -> block-category map (spec-driven, generic).
    # Falls back to substring heuristics for legacy specs or when the YAML is unavailable.
    _spec_blocks_for_class = _spec_blocks if isinstance(_spec_blocks, dict) else {}
    _coef_map_for_class = _coef_to_block_map(_spec_blocks_for_class)
    _block_to_category = {
        "hours": "hours_opp",
        "market": "hours_opp",       # market shifters are working-gated, shown together with hours
        "wage": "wage_opp",
        "occupation": "occupation_opp",
        "preference": "preference",
    }

    def classify_param(name):
        """Classify parameter via YAML spec, then by name conventions."""
        block = _classify_param_via_blocks(name, _coef_map_for_class)
        if block is not None:
            return _block_to_category.get(block, "other")
        name_lower = name.lower()
        if 'beta_offer_' in name_lower:
            return 'market_opp'
        if 'beta_occ_' in name_lower:
            return 'occupation_opp'
        if any(x in name_lower for x in ['beta_l', 'beta_c', 'theta_l', 'theta_c', 'beta_interact']):
            return 'preference'
        if any(x in name_lower for x in ['beta_work', 'beta_pt', 'beta_ft', 'beta_gsur',
                                          'beta_e_', 'beta_e ', 'beta_h_']):
            return 'hours_opp'
        if name_lower in ('beta_e',):
            return 'hours_opp'
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

            row_classes = []
            is_bounded = lb is not None or ub is not None
            hit_bound = False
            if is_bounded and is_num(est):
                if lb is not None and abs(float(est) - lb) < 1e-6:
                    hit_bound = True
                if ub is not None and abs(float(est) - ub) < 1e-6:
                    hit_bound = True

            if hit_bound:
                row_classes.append("bound-hit")
            elif is_bounded:
                row_classes.append("bounded-param")

            est_str = safe_format(est, ".4f", "N/A")
            se_str = safe_format(se, ".4f", "N/A")
            t_str = safe_format(t_val, ".2f", "N/A")
            lb_str = safe_format(lb, ".4f", "—")
            ub_str = safe_format(ub, ".4f", "—")
            init_str = safe_format(init_val, ".4f", "N/A")
            se_cell_class = ""

            degenerate_se = is_num(se) and abs(float(se)) <= 1e-12
            if degenerate_se:
                row_classes.append("degenerate-se-row")
                se_cell_class = 'class="degenerate-se-cell"'
                se_str = f"{se_str} [degenerate]"
                t_str = "N/A"

            sig = ""
            p_str = "N/A"
            p_class = ""
            if degenerate_se:
                p_class = 'class="warning-cell"'
                p_str = "N/A"
            elif is_num(p_val):
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

            row_class = ""
            if row_classes:
                row_class = f'class="{" ".join(row_classes)}"'

            rows_html += f"""
            <tr {row_class}>
                <td>{param_name}</td>
                <td>{est_str}</td>
                <td {se_cell_class}>{se_str}</td>
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

    market_opp_table = build_param_table_html(
        param_df[param_df['category'] == 'market_opp'],
        "Job Market Opportunity Parameters",
        "Parameters entering the market-opportunity index log a(j|X) for job-choice models."
    )

    hours_opp_table = build_param_table_html(
        param_df[param_df['category'] == 'hours_opp'],
        "⏰ Employment and Hours Opportunity Parameters",
        ("Working-gated employment intercept and hours focal-point indicators, "
         "plus residual market-access shifters (gsur, education) declared in "
         "<code>market_opportunity.shifters</code>.")
    )

    wage_opp_table = build_param_table_html(
        param_df[param_df['category'] == 'wage_opp'],
        "💰 Wage Opportunity / Mincer Parameters",
        ("Log-normal wage opportunity: μ<sub>w</sub>(X) intercept, education, "
         "experience, and residual standard deviation σ.")
    )

    occupation_opp_table = build_param_table_html(
        param_df[param_df['category'] == 'occupation_opp'],
        "🧭 Occupation Opportunity Parameters",
        ("Working-gated occupation shifters declared in "
         "<code>occupation_opportunity.shifters</code>; routed by "
         "<code>applies_to</code> group (sm/sf/cm/cf). Reference category is "
         "the YAML's <code>occupation_opportunity.reference</code>.")
    )

    other_table = build_param_table_html(
        param_df[param_df['category'] == 'other'],
        "📋 Other Parameters",
        ""
    )

    param_table_rows = (
        pref_table + market_opp_table + hours_opp_table + wage_opp_table
        + occupation_opp_table + other_table
    )

    # Generate specification HTML
    specification_html = generate_specification_html(parsed_params)

    # Generate identification diagnostics HTML
    identification_html = generate_identification_diagnostics_html(hessian_diagnostics, parsed_params)

    # Optionally include persisted identification diagnostics from estimation stage
    identification_file_html = ""
    id_diag_text = run_metadata.get("identification_diagnostics_text")
    if isinstance(id_diag_text, str) and id_diag_text.strip():
        id_diag_path = run_metadata.get("identification_diagnostics_path")
        id_source_html = (
            f"<p><strong>Source:</strong> <code>{escape(str(id_diag_path))}</code></p>"
            if id_diag_path else ""
        )
        identification_file_html = f"""
    <section>
        <h2>🧪 Identification Diagnostics (Estimation Stage)</h2>
        {id_source_html}
        <pre style="white-space: pre-wrap; background: #f8f9fa; padding: 1em; border-radius: 6px; border: 1px solid #ddd; max-height: 500px; overflow-y: auto;">{escape(id_diag_text)}</pre>
    </section>
    """

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
        {estimation_results_info}
        {run_metadata_html}
        <div class="group-legend">
            <div class="legend-item"><div class="legend-color" style="background:var(--sm-color)"></div>Single Males</div>
            <div class="legend-item"><div class="legend-color" style="background:var(--sf-color)"></div>Single Females</div>
            <div class="legend-item"><div class="legend-color" style="background:var(--cm-color)"></div>Males in Couples</div>
            <div class="legend-item"><div class="legend-color" style="background:var(--cf-color)"></div>Females in Couples</div>
        </div>
    </div>

    {time_section}

    {solver_bundle_html}

    {fit_stats_split_html}

    <section>
        <details>
          <summary><strong>📈 Legacy combined fit-statistics dump (technical appendix)</strong></summary>
          <p style="margin-top:0.5em;"><em>This is the legacy "kitchen-sink" table preserved for backward compatibility. The four reorganized sections above (A–D) are the canonical view. This table mixes core fit, null-model, bound and economic-sanity values; prefer the sections above for adoption decisions.</em></p>
          <table class="table" style="width:auto;">
            {fit_stats_rows}
          </table>
          {bounds_explanation}
        </details>
    </section>

    {identification_bundle_html}

    {identification_html}
    {identification_file_html}

    <section>
        <h2>📐 Model Specification</h2>
        <p>Utility and opportunity functions for each demographic group, shown in both symbolic and numerical form.</p>
        {specification_html}

        {model_specific_sections_html}
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

        {probability_fit_bundle_html}

        {bound_diag_html}
    </section>

    <section>
        <h2>🗺️ Utility Contours & Plots</h2>
        {plots_section}
    </section>

    {group_params_section}

    {param_table_bundle_html}

    <section>
        <h2>📋 Parameter Estimates by Category (legacy view)</h2>
        <p><em>Significance: *** p&lt;0.001, ** p&lt;0.01, * p&lt;0.05. The
        bundle-driven block view above is the canonical Phase-2 source.</em></p>
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


def compute_null_log_likelihood_prior_corrected(
    df: pd.DataFrame,
    choice_id_col: str = 'idhh',
    prior_col: str = 'prior',
    chosen_col: str = 'is_chosen',
) -> Optional[float]:
    """
    Compute prior-corrected null LL for sampled-alternative estimators.

    Uses index V_ij = -log(prior_ij), i.e.:
      P_ij = (1/prior_ij) / sum_k (1/prior_ik)
    and LL0 = sum_i log(P_i,chosen).
    """
    if prior_col not in df.columns:
        return None

    # Prefer explicit chosen flags; fallback to "chosen".
    effective_chosen_col = chosen_col if chosen_col in df.columns else ("chosen" if "chosen" in df.columns else None)
    if effective_chosen_col is None:
        return None

    ll0 = 0.0
    n_groups_used = 0

    for _, g in df.groupby(choice_id_col, sort=False):
        prior = pd.to_numeric(g[prior_col], errors='coerce').to_numpy(dtype=float)
        if prior.size == 0 or np.any(~np.isfinite(prior)) or np.any(prior <= 0):
            continue

        chosen = (pd.to_numeric(g[effective_chosen_col], errors='coerce').fillna(0.0).to_numpy(dtype=float) > 0.5)
        if chosen.sum() != 1:
            continue

        chosen_prior = prior[np.argmax(chosen)]
        inv_prior_sum = np.sum(1.0 / prior)
        if not np.isfinite(inv_prior_sum) or inv_prior_sum <= 0:
            continue

        ll0 += -np.log(chosen_prior) - np.log(inv_prior_sum)
        n_groups_used += 1

    if n_groups_used == 0:
        return None

    return float(ll0)


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
    
    # Process singles. In the MNL parquets the convention is dgn=1 → male,
    # dgn=0 → female (verified against sample sizes 766 male / 910 female).
    for gender_code, gender_name, group_key in [(1, 'male', 'sm'), (0, 'female', 'sf')]:
        if df_singles is None:
            continue

        # Try 'dgn' first (dataset convention), then 'gender'
        gender_col = 'dgn' if 'dgn' in df_singles.columns else 'gender'
        df_g = df_singles[df_singles[gender_col] == gender_code].copy()
        if len(df_g) == 0:
            continue
        # Get the FULL joint param vector (so theta_c_singles is visible to
        # the spec-driven theta_c resolver inside _add_predicted_probabilities).
        params = None
        if 'joint' in parsed_params.params_by_group:
            params = parsed_params.get_all_params_for_group('joint')
        if params is None:
            for try_key in [group_key, f'singles_{gender_name}', group_key.upper()]:
                if try_key in parsed_params.params_by_group:
                    params = parsed_params.get_all_params_for_group(try_key)
                    break

        group_suffix = f'_{group_key}'  # '_sm' or '_sf'
        has_beta_c = (
            params is not None
            and (f'beta_c{group_suffix}' in params or 'beta_c' in params)
        )
        if not has_beta_c:
            LOGGER.warning(f"No parameters found for {group_key}, skipping fit diagnostics")
            continue

        try:
            # Compute observed moments
            chosen_col = 'is_chosen' if 'is_chosen' in df_g.columns else 'chosen'
            chosen = df_g[df_g[chosen_col] == 1].copy()
            obs_participation = (chosen['hours'] > 0).mean()
            obs_hours = chosen.loc[chosen['hours'] > 0, 'hours'].mean() if (chosen['hours'] > 0).any() else 0.0
            df_g = _add_predicted_probabilities(
                df_g, params, spec=spec, is_couples=False, group_suffix=group_suffix,
            )
            df_g['prob'] = df_g['pred_prob']
            
            # Predicted participation
            pred_participation = (df_g.groupby('idhh').apply(
                lambda x: (x['prob'] * (x['hours'] > 0).astype(float)).sum(),
                include_groups=False
            )).mean()
            
            # Predicted mean hours among workers
            def household_pred_hours(x):
                working_mask = (x['hours'] > 0).values
                if not working_mask.any():
                    return 0.0
                numerator = (x['prob'].values * x['hours'].values * working_mask).sum()
                denominator = (x['prob'].values * working_mask).sum()
                return numerator / denominator if denominator > 0 else 0.0
            
            pred_hours = df_g.groupby('idhh').apply(
                household_pred_hours,
                include_groups=False
            ).mean()
            
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
        
        # Prefer the full joint param vector so theta_l_m / theta_l_f and all
        # leisure-shifter coefficients are visible regardless of grouping.
        if 'joint' in parsed_params.params_by_group:
            params = parsed_params.get_all_params_for_group('joint')

        if params is not None:
            try:
                df_cou = df_couples.copy()
                df_cou = _add_predicted_probabilities(
                    df_cou, params, spec=spec, is_couples=True, group_suffix='',
                )
                df_cou['prob'] = df_cou['pred_prob']
                
                # Now compute predicted moments for each gender
                for gender, suffix in [('male', '_m'), ('female', '_f')]:
                    group_key = f'cou{suffix}'
                    hours_col = f'hours_{gender}'
                    
                    chosen = df_cou[df_cou[chosen_col] == 1].copy()
                    obs_participation = (chosen[hours_col] > 0).mean()
                    obs_hours = chosen.loc[chosen[hours_col] > 0, hours_col].mean() if (chosen[hours_col] > 0).any() else 0.0
                    
                    # Predicted participation
                    pred_participation = (df_cou.groupby('idhh').apply(
                        lambda x: (x['prob'] * (x[hours_col] > 0).astype(float)).sum(),
                        include_groups=False
                    )).mean()
                    
                    # Predicted hours among workers
                    def household_pred_hours(x):
                        working_mask = (x[hours_col] > 0).values
                        if not working_mask.any():
                            return 0.0
                        numerator = (x['prob'].values * x[hours_col].values * working_mask).sum()
                        denominator = (x['prob'].values * working_mask).sum()
                        return numerator / denominator if denominator > 0 else 0.0
                    
                    pred_hours = df_cou.groupby('idhh').apply(
                        household_pred_hours,
                        include_groups=False
                    ).mean()
                    
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


def compute_beta_l_full(
    df: pd.DataFrame,
    params: Dict[str, float],
    suffix: str = '',
    spec: Optional['EstimationSpec'] = None,
) -> np.ndarray:
    """
    Compute full beta_l(X) = beta_l0 + sum(beta_l_k * X_k) for each observation.

    When `spec` is provided the YAML's utility_leisure_shifters list drives the
    mapping from coefficient names to data column names (the only authoritative
    source — earlier heuristic stripping of `beta_l_` silently lost shifters
    whose coefficient base did not match a data column).
    """
    n = len(df)
    beta_l0_key = f'beta_l0{suffix}' if suffix else 'beta_l0'
    beta_l = np.full(n, params.get(beta_l0_key, params.get('beta_l0', 0.0)))

    gender = None
    if suffix in ('_m', '_sm'):
        gender = 'male'
    elif suffix in ('_f', '_sf'):
        gender = 'female'

    def _resolve(col_base: str) -> Optional[str]:
        # Prefer gender-specific column when available (couples data), else base.
        if gender is not None:
            for c in (f'{col_base}_{gender}', f'{col_base}{suffix}'):
                if c in df.columns:
                    return c
        if col_base in df.columns:
            return col_base
        return None

    if spec is not None and getattr(spec, 'utility_leisure_shifters', None):
        for shifter in spec.utility_leisure_shifters:
            coef = shifter.get('coefficient')
            var_name = shifter.get('variable')
            gender_specific = shifter.get('gender_specific', False)
            if not coef or not var_name:
                continue
            # Resolve parameter value via suffixed lookup.
            param_keys = []
            if suffix:
                param_keys.append(f'{coef}{suffix}')
            param_keys.append(coef)
            val = None
            for k in param_keys:
                if k in params and params[k] is not None:
                    val = params[k]
                    break
            if val is None:
                continue
            if gender_specific and gender == 'male':
                # `gender_specific: true` on YAML means female-only.
                continue
            col = _resolve(var_name)
            if col is None:
                continue
            beta_l = beta_l + val * df[col].values
        return beta_l

    # Legacy fallback: heuristic strip of `beta_l_` prefix.
    covariate_mapping = {
        'age_norm': ['age_norm', 'age_normalized'],
        'age_norm2': ['age_norm2', 'age_normalized2', 'age_norm_sq'],
        'n_children': ['n_children', 'nch', 'num_children'],
        'educL': ['educL', 'educ_low', 'low_education'],
        'educH': ['educH', 'educ_high', 'high_education'],
        'age': ['age_norm', 'age_normalized'],
        'age2': ['age_norm2', 'age_normalized2', 'age_norm_sq'],
        'nkids': ['n_children', 'nch', 'num_children'],
    }

    for param_name, param_value in params.items():
        if not param_name.startswith('beta_l_'):
            continue
        if 'beta_l0' in param_name:
            continue
        cov_base = param_name.replace('beta_l_', '').replace(suffix, '')
        col_found = None
        possible_cols = covariate_mapping.get(cov_base, [cov_base])
        if suffix:
            for c in [f'{cov_base}_{gender}' if gender else None, f'{cov_base}{suffix}']:
                if c and c in df.columns:
                    col_found = c
                    break
        if col_found is None:
            for col in possible_cols:
                if col in df.columns:
                    col_found = col
                    break
        if col_found is not None:
            beta_l = beta_l + param_value * df[col_found].values

    return beta_l


def compute_marginal_utilities_at_chosen(
    parsed_params: ParsedParameters,
    mnl_base: Path,
) -> Dict[str, Any]:
    """
    Compute marginal utilities (MUC, MUL) at chosen alternatives.
    
    Separable specification:
        MUC = beta_c * c^(theta_c - 1)
        MUL = beta_l(X) * l^(theta_l - 1)

    With interaction U += beta_cl * BC(c, theta_c) * BC(l, theta_l):
        MUC = (beta_c + beta_cl * BC(l, theta_l)) * c^(theta_c - 1)
        MUL = (beta_l(X) + beta_cl * BC(c, theta_c)) * l^(theta_l - 1)
    
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
        beta_cl = params.get('beta_cl', 0.0)
        if beta_cl is None:
            beta_cl = 0.0

        c = df_g['consumption'].values
        l = df_g['leisure'].values

        # Compute Box-Cox terms used by interaction-aware derivatives.
        bc_c = boxcox_transform(c, theta_c)
        bc_l = boxcox_transform(l, theta_l)

        # Compute MUC
        muc = compute_marginal_utility_consumption(
            c,
            beta_c,
            theta_c,
            beta_cl=beta_cl,
            bc_l=bc_l,
        )
        
        # Compute full beta_l(X) for each observation
        beta_l = compute_beta_l_full(df_g, params, suffix='')
        
        # Compute MUL = [beta_l(X) + beta_cl * BC(c)] * l^(theta_l - 1)
        mul = compute_marginal_utility_leisure(
            l,
            beta_l,
            theta_l,
            beta_cl=beta_cl,
            bc_c=bc_c,
        )
        
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

        # If virtual groups are absent, fall back to coupled group params.
        if params_m is None:
            for try_key in ['cou', 'couples']:
                if try_key in parsed_params.params_by_group:
                    params_m = parsed_params.get_all_params_for_group(try_key)
                    break
        if params_f is None:
            params_f = params_m

        if params_m is not None:
            # Get consumption parameters (shared between M and F in couples)
            beta_c = params_m.get('beta_c', 1.0)
            theta_c = params_m.get('theta_c', 0.5)
            beta_cl_m = params_m.get('beta_cl_m', params_m.get('beta_cl', 0.0))
            params_female = params_f if params_f is not None else params_m
            beta_cl_f = params_female.get('beta_cl_f', params_female.get('beta_cl', 0.0))
            if beta_cl_m is None:
                beta_cl_m = 0.0
            if beta_cl_f is None:
                beta_cl_f = 0.0

            c = df_chosen['consumption'].values
            bc_c = boxcox_transform(c, theta_c)

            # MUC for household consumption includes both male and female interactions.
            theta_l_m = params_m.get('theta_l_m', params_m.get('theta_l', 0.5))
            l_m = df_chosen['leisure_male'].values
            bc_l_m = boxcox_transform(l_m, theta_l_m)
            theta_l_f = params_female.get('theta_l_f', params_female.get('theta_l', 0.5))
            l_f = df_chosen['leisure_female'].values
            bc_l_f = boxcox_transform(l_f, theta_l_f)
            muc = (beta_c + beta_cl_m * bc_l_m + beta_cl_f * bc_l_f) * d_boxcox_dx(c, theta_c)

            # Add MUC for couples to total.
            all_muc.extend(muc)

            # Males in couples
            beta_l_m = compute_beta_l_full(df_chosen, params_m, suffix='_m')
            mul_m = compute_marginal_utility_leisure(
                l_m,
                beta_l_m,
                theta_l_m,
                beta_cl=beta_cl_m,
                bc_c=bc_c,
            )
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
            beta_l_f = compute_beta_l_full(df_chosen, params_female, suffix='_f')
            mul_f = compute_marginal_utility_leisure(
                l_f,
                beta_l_f,
                theta_l_f,
                beta_cl=beta_cl_f,
                bc_c=bc_c,
            )
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
    spec: Optional['EstimationSpec'] = None,
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
    
    # Helper to compute logit probabilities using shared routine
    def compute_probs_for_df(df, params, is_couples=False, group_suffix=''):
        df = _add_predicted_probabilities(
            df,
            params,
            spec=spec,
            is_couples=is_couples,
            group_suffix=group_suffix,
        )
        df['prob'] = df['pred_prob']
        return df

    # Process singles
    if df_singles is not None and len(df_singles) > 0:
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
            if params is None and 'joint' in parsed_params.params_by_group:
                params = parsed_params.get_all_params_for_group('joint')
            
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
        for try_key in ['joint', 'm', 'cou', 'couples']:
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

    # Extract spec-driven extra precompute variables (market opportunity shifters)
    extra_precompute_vars_set = set()
    for shifter in getattr(spec, "market_opportunity_shifters", []):
        if not isinstance(shifter, dict):
            continue
        var_name = shifter.get("variable")
        if isinstance(var_name, str) and var_name.strip():
            extra_precompute_vars_set.add(var_name.strip())
        interaction_cfg = shifter.get("interaction")
        if interaction_cfg is None:
            continue
        if isinstance(interaction_cfg, (list, tuple, set)):
            interaction_names = [str(v).strip() for v in interaction_cfg if str(v).strip()]
        else:
            interaction_names = [str(interaction_cfg).strip()]
        for interaction_name in interaction_names:
            if interaction_name and interaction_name != "working":
                extra_precompute_vars_set.add(interaction_name)
    extra_precompute_vars = sorted(extra_precompute_vars_set) if extra_precompute_vars_set else None
    if extra_precompute_vars:
        LOGGER.info(f"   Extra precompute variables for SE: {extra_precompute_vars}")

    data_sm = None
    data_sf = None
    data_cou = None

    if df_singles is not None:
        df_sm = df_singles[df_singles["dgn"] == 1]
        df_sf = df_singles[df_singles["dgn"] == 0]

        if len(df_sm) > 0:
            data_sm = precompute_data_singles(
                df=df_sm, metadata=metadata, is_male=True,
                include_wage_vars=include_wage_vars, include_loc_vars=include_loc_vars,
                include_extra_vars=extra_precompute_vars
            )
        if len(df_sf) > 0:
            data_sf = precompute_data_singles(
                df=df_sf, metadata=metadata, is_male=False,
                include_wage_vars=include_wage_vars, include_loc_vars=include_loc_vars,
                include_extra_vars=extra_precompute_vars
            )

    if df_couples is not None:
        data_cou = precompute_data_couples(
            df=df_couples, metadata=metadata,
            include_wage_vars=include_wage_vars, include_loc_vars=include_loc_vars,
            include_extra_vars=extra_precompute_vars
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
# LOW-TOKEN MARKDOWN SUMMARY EXPORT
# =============================================================================

def _md_clean(value: Any) -> str:
    """Render a value for a Markdown table cell."""
    if value is None:
        return "NA"
    if isinstance(value, (float, np.floating)):
        if not np.isfinite(value):
            return "NA"
        return f"{float(value):.6g}"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    text = str(value).replace("\n", " ").replace("\r", " ").strip()
    replacements = {
        "β": "beta",
        "θ": "theta",
        "σ": "sigma",
        "κ": "kappa",
        "μ": "mu",
        "ε": "eps",
        "Σ": "sum",
        "·": "*",
        "✓": "yes",
        "✗": "no",
        "≤": "<=",
        "≥": ">=",
        "−": "-",
        "—": "-",
        "→": "->",
        "Δ": "delta",
        "β": "beta",
        "θ": "theta",
        "σ": "sigma",
        "✓": "yes",
        "✗": "no",
        "Î²": "beta",
        "Î¸": "theta",
        "Ïƒ": "sigma",
        "Îº": "kappa",
        "Î¼": "mu",
        "Îµ": "eps",
        "Î£": "sum",
        "Â·": "*",
        "Â·": "*",
        "âœ“": "yes",
        "âœ—": "no",
        "â‰¤": "<=",
        "â‰¥": ">=",
        "âˆ’": "-",
        "â€”": "-",
        "â†’": "->",
        "Î”": "delta",
        "â‰¤": "<=",
        "â‰¥": ">=",
        "âˆ’": "-",
        "â€”": "-",
        "ðŸŽ¯": "",
        "ðŸ’°": "",
        "ðŸ§­": "",
        "â°": "",
        "ðŸ“‹": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.replace("|", "\\|") if text else "NA"


def _md_table(headers: List[str], rows: List[List[Any]]) -> str:
    """Build a compact GitHub-flavored Markdown table."""
    if not rows:
        return "_None._\n"
    header = "| " + " | ".join(_md_clean(h) for h in headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = [
        "| " + " | ".join(_md_clean(cell) for cell in row) + " |"
        for row in rows
    ]
    return "\n".join([header, sep] + body) + "\n"


# =============================================================================
# Low-token Markdown summary — enrichment helpers
# Country/year/specification agnostic: each helper degrades gracefully when
# inputs are absent (empty list / "_None._").
# =============================================================================


def _git_revision_info() -> Dict[str, Any]:
    """Compact git rev + dirty + branch info; empty dict on any failure."""
    import subprocess  # local import to keep top-level light
    out: Dict[str, Any] = {}
    for label, args in [
        ("git_sha", ["git", "rev-parse", "--short=12", "HEAD"]),
        ("git_branch", ["git", "rev-parse", "--abbrev-ref", "HEAD"]),
    ]:
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=5, check=False)
            if r.returncode == 0 and r.stdout.strip():
                out[label] = r.stdout.strip()
        except Exception:  # noqa: BLE001
            pass
    try:
        s = subprocess.run(["git", "status", "--porcelain"],
                           capture_output=True, text=True, timeout=5, check=False)
        if s.returncode == 0:
            out["git_dirty"] = bool(s.stdout.strip())
    except Exception:  # noqa: BLE001
        pass
    return out


def _read_mnl_dataframes_for_summary(
    mnl_base: Optional[Union[str, Path]],
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """Best-effort load of MNL singles/couples parquets. Returns (None, None) silently on failure."""
    if mnl_base is None:
        return None, None
    try:
        base = str(mnl_base)
        sp = Path(base + "__singles.parquet")
        cp = Path(base + "__couples.parquet")
        s = pd.read_parquet(sp) if sp.exists() else None
        c = pd.read_parquet(cp) if cp.exists() else None
        return s, c
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning(f"   _read_mnl_dataframes_for_summary: {exc}")
        return None, None


def _sample_size_rows(
    df_singles: Optional[pd.DataFrame],
    df_couples: Optional[pd.DataFrame],
) -> List[List[Any]]:
    """Per-group n_obs, n_households, n_chosen, n_working."""
    rows: List[List[Any]] = []

    def _stat(df, label, dgn_value, work_col, hours_col):
        if df is None or "idhh" not in df.columns:
            return
        sub = df
        if dgn_value is not None and "dgn" in df.columns:
            sub = df[df["dgn"] == dgn_value]
        if len(sub) == 0:
            return
        chosen_col = "is_chosen" if "is_chosen" in sub.columns else ("chosen" if "chosen" in sub.columns else None)
        n_obs = len(sub)
        n_hh = int(sub["idhh"].nunique())
        n_chosen = int((sub[chosen_col] == 1).sum()) if chosen_col else None
        n_working: Optional[int] = None
        if work_col in sub.columns:
            n_working = int((sub[work_col] == 1).sum())
        elif hours_col in sub.columns:
            n_working = int((pd.to_numeric(sub[hours_col], errors="coerce") > 0).sum())
        alts_per_hh = (n_obs / n_hh) if n_hh else None
        rows.append([label, n_obs, n_hh,
                     round(alts_per_hh, 2) if alts_per_hh is not None else None,
                     n_chosen, n_working])

    _stat(df_singles, "singles_male", 1, "working", "hours")
    _stat(df_singles, "singles_female", 0, "working", "hours")
    _stat(df_couples, "couples_male", None, "working_male", "hours_male")
    _stat(df_couples, "couples_female", None, "working_female", "hours_female")
    return rows


def _x_descriptives_rows(
    df_singles: Optional[pd.DataFrame],
    df_couples: Optional[pd.DataFrame],
) -> List[List[Any]]:
    """Means on chosen-alt rows for canonical X variables, per group."""
    rows: List[List[Any]] = []
    base_vars = ["age_norm", "age_norm2", "educL", "educM", "educH",
                 "pexp_years", "n_children", "gsur"]

    def _emit(df, label, dgn_value, suffix=""):
        if df is None:
            return
        chosen = df
        if "is_chosen" in chosen.columns:
            chosen = chosen[chosen["is_chosen"] == 1]
        elif "chosen" in chosen.columns:
            chosen = chosen[chosen["chosen"] == 1]
        if dgn_value is not None and "dgn" in chosen.columns:
            chosen = chosen[chosen["dgn"] == dgn_value]
        if len(chosen) == 0:
            return
        for v in base_vars:
            col = v + suffix
            if col in chosen.columns:
                series = pd.to_numeric(chosen[col], errors="coerce").dropna()
                if len(series):
                    rows.append([label, v, round(float(series.mean()), 4),
                                 round(float(series.std()), 4),
                                 round(float(series.min()), 4),
                                 round(float(series.max()), 4),
                                 int(len(series))])

    _emit(df_singles, "singles_male", 1)
    _emit(df_singles, "singles_female", 0)
    _emit(df_couples, "couples_male", None, "_male")
    _emit(df_couples, "couples_female", None, "_female")
    return rows


def _observed_log_wage_rows(
    df_singles: Optional[pd.DataFrame],
    df_couples: Optional[pd.DataFrame],
    implied_sigma: Optional[float],
) -> List[List[Any]]:
    """Observed log-wage mean & std on chosen working rows, with implied σ comparison."""
    rows: List[List[Any]] = []

    def _row(df, label, wage_col, work_col, hours_col, dgn_value=None):
        if df is None or wage_col not in df.columns:
            return
        sub = df
        if "is_chosen" in df.columns:
            sub = sub[sub["is_chosen"] == 1]
        elif "chosen" in df.columns:
            sub = sub[sub["chosen"] == 1]
        if dgn_value is not None and "dgn" in sub.columns:
            sub = sub[sub["dgn"] == dgn_value]
        if work_col in sub.columns:
            sub = sub[sub[work_col] == 1]
        elif hours_col in sub.columns:
            sub = sub[pd.to_numeric(sub[hours_col], errors="coerce") > 0]
        wage = pd.to_numeric(sub[wage_col], errors="coerce")
        wage = wage[(wage > 0) & wage.notna()]
        if len(wage) < 2:
            return
        logw = np.log(wage.to_numpy())
        rows.append([label, int(len(logw)),
                     round(float(np.mean(logw)), 4),
                     round(float(np.std(logw, ddof=1)), 4),
                     _md_clean(implied_sigma)])

    _row(df_singles, "singles_male", "wage", "working", "hours", 1)
    _row(df_singles, "singles_female", "wage", "working", "hours", 0)
    _row(df_couples, "couples_male", "wage_male", "working_male", "hours_male")
    _row(df_couples, "couples_female", "wage_female", "working_female", "hours_female")
    return rows


def _hours_quantile_rows(
    df_singles: Optional[pd.DataFrame],
    df_couples: Optional[pd.DataFrame],
) -> List[List[Any]]:
    """Observed hours quantiles on chosen working alternatives."""
    quants = [0.10, 0.25, 0.50, 0.75, 0.90]
    rows: List[List[Any]] = []

    def _emit(df, label, hours_col, work_col, dgn_value=None):
        if df is None or hours_col not in df.columns:
            return
        sub = df
        if "is_chosen" in sub.columns:
            sub = sub[sub["is_chosen"] == 1]
        elif "chosen" in sub.columns:
            sub = sub[sub["chosen"] == 1]
        if dgn_value is not None and "dgn" in sub.columns:
            sub = sub[sub["dgn"] == dgn_value]
        if work_col in sub.columns:
            sub = sub[sub[work_col] == 1]
        else:
            sub = sub[pd.to_numeric(sub[hours_col], errors="coerce") > 0]
        h = pd.to_numeric(sub[hours_col], errors="coerce").dropna()
        if not len(h):
            return
        qs = h.quantile(quants).to_dict()
        rows.append([label, int(len(h)),
                     round(float(qs[0.10]), 2), round(float(qs[0.25]), 2),
                     round(float(qs[0.50]), 2), round(float(qs[0.75]), 2),
                     round(float(qs[0.90]), 2)])

    _emit(df_singles, "singles_male", "hours", "working", 1)
    _emit(df_singles, "singles_female", "hours", "working", 0)
    _emit(df_couples, "couples_male", "hours_male", "working_male")
    _emit(df_couples, "couples_female", "hours_female", "working_female")
    return rows


def _distribution_fit_l1_rows(fit_results: Dict[str, Dict[str, Any]]) -> List[List[Any]]:
    """L1 and L2 distance between observed and predicted hours-bin shares per group."""
    rows: List[List[Any]] = []
    for group, vals in sorted((fit_results or {}).items()):
        obs = vals.get("hours_distribution_observed") or {}
        pred = vals.get("hours_distribution_predicted") or {}
        if not obs and not pred:
            continue
        keys = sorted(set(obs) | set(pred), key=str)
        diffs = [abs(float(obs.get(k, 0.0)) - float(pred.get(k, 0.0))) for k in keys]
        l1 = sum(diffs)
        l2 = float(np.sqrt(sum(d * d for d in diffs)))
        rows.append([group, "hours_bins", len(keys),
                     round(l1, 4), round(l2, 4)])
    return rows


def _bound_proximity_rows(param_df: pd.DataFrame, pct: float = 0.05) -> List[List[Any]]:
    """Estimates within `pct` of a bound but not exactly at it."""
    rows: List[List[Any]] = []
    for _, row in param_df.iterrows():
        est = row.get("estimate")
        lb = row.get("lower_bound")
        ub = row.get("upper_bound")
        if not isinstance(est, (int, float)) or (np.isnan(est) if hasattr(np, "isnan") else False):
            continue
        if not (isinstance(lb, (int, float)) or isinstance(ub, (int, float))):
            continue
        if isinstance(lb, (int, float)) and isinstance(ub, (int, float)):
            width = float(ub) - float(lb)
        else:
            width = max(abs(float(est)), 1.0)
        if width <= 0:
            continue
        tol = pct * abs(width)
        flags = []
        if isinstance(lb, (int, float)):
            d = abs(float(est) - float(lb))
            if 1e-6 < d <= tol:
                flags.append(f"near_lower(Δ={d:.3g})")
        if isinstance(ub, (int, float)):
            d = abs(float(est) - float(ub))
            if 1e-6 < d <= tol:
                flags.append(f"near_upper(Δ={d:.3g})")
        if flags:
            rows.append([row.get("block"), row.get("parameter"),
                         _md_clean(est), _md_clean(lb), _md_clean(ub),
                         "; ".join(flags)])
    return rows


def _convergence_warning_rows(
    param_df: pd.DataFrame,
    hessian_diagnostics: Optional[Dict[str, Any]],
    prob_diagnostics: Optional[Dict[str, Any]],
    bound_diagnostics: Optional[List[Dict[str, Any]]],
    fit_stats: Optional[Dict[str, Any]],
) -> List[List[Any]]:
    """Aggregated convergence/health summary for fast LLM review."""
    rows: List[List[Any]] = []
    n = len(param_df)
    p_vals = pd.to_numeric(param_df.get("p_value"), errors="coerce")
    se = pd.to_numeric(param_df.get("std_error"), errors="coerce")
    t_vals = pd.to_numeric(param_df.get("t_value"), errors="coerce").abs()
    n_degen = int((se.abs() < 1e-12).sum()) if se is not None else 0
    n_sig_05 = int((p_vals < 0.05).sum())
    n_t_under_1 = int((t_vals < 1.0).sum())
    pct_sig = (n_sig_05 / n * 100) if n else 0.0
    pct_noise = (n_t_under_1 / n * 100) if n else 0.0
    n_at_bound = len(bound_diagnostics or [])
    p_min = ((prob_diagnostics or {}).get("p_chosen_dist") or {}).get("min")
    p_q10 = ((prob_diagnostics or {}).get("p_chosen_dist") or {}).get("q10")
    cond = (hessian_diagnostics or {}).get("condition_number")
    n_neg = (hessian_diagnostics or {}).get("n_negative_eigenvalues") or 0
    ll = (fit_stats or {}).get("log_likelihood")
    aic = (fit_stats or {}).get("AIC")
    bic = (fit_stats or {}).get("BIC")
    rho2 = (fit_stats or {}).get("rho_squared")

    rows.append(["n_estimated_params", n])
    rows.append(["log_likelihood", ll])
    rows.append(["AIC", aic])
    rows.append(["BIC", bic])
    rows.append(["rho_squared", rho2])
    rows.append(["n_significant_p<0.05", n_sig_05])
    rows.append(["pct_significant_p<0.05", f"{pct_sig:.1f}%" if n else "NA"])
    rows.append(["n_low_t<1.0", n_t_under_1])
    rows.append(["pct_low_t<1.0", f"{pct_noise:.1f}%" if n else "NA"])
    rows.append(["n_degenerate_se", n_degen])
    rows.append(["n_at_bound_strict", n_at_bound])
    rows.append(["hessian_condition_number", cond])
    rows.append(["n_negative_eigenvalues", n_neg])
    rows.append(["p_chosen_min", p_min])
    rows.append(["p_chosen_q10", p_q10])

    verdicts: List[str] = []
    if isinstance(cond, (int, float)) and cond > 1e10:
        verdicts.append("ill_conditioned_hessian")
    if n_neg and int(n_neg) > 0:
        verdicts.append("negative_eigenvalues_present")
    if n_degen > 0:
        verdicts.append("degenerate_standard_errors")
    if n_at_bound > 0:
        verdicts.append("parameters_at_bounds")
    if isinstance(p_min, (int, float)) and p_min < 1e-6:
        verdicts.append("very_small_p_chosen_min")
    if pct_noise > 25.0:
        verdicts.append("over_25pct_low_t")
    rows.append(["review_priority_flags", ", ".join(verdicts) if verdicts else "none"])
    return rows


def _top_significant_rows(param_df: pd.DataFrame, n: int = 15) -> List[List[Any]]:
    """Top-n estimated coefficients by |t-value|."""
    df = param_df.copy()
    df["abs_t"] = pd.to_numeric(df.get("t_value"), errors="coerce").abs()
    df = df.dropna(subset=["abs_t"])
    df = df.sort_values("abs_t", ascending=False).head(n)
    out: List[List[Any]] = []
    for _, r in df.iterrows():
        out.append([r.get("block"), r.get("parameter"),
                    r.get("estimate"), r.get("std_error"),
                    r.get("t_value"), r.get("p_value")])
    return out


def _utility_leisure_inventory(blocks: Dict[str, Any]) -> List[List[Any]]:
    """Inventory rows for the utility.leisure block (intercept, theta, shifters)."""
    u_leis = (blocks.get("utility_leisure") or {}) if isinstance(blocks, dict) else {}
    if not u_leis:
        return []
    out: List[List[Any]] = []
    intercept = u_leis.get("intercept")
    theta = u_leis.get("box_cox_exponent")
    if intercept:
        out.append(["utility.leisure.intercept", "leisure intercept", 1, "—", intercept])
    if theta:
        out.append(["utility.leisure.box_cox_exponent", "leisure θ_l", 1, "—", theta])
    shifters = u_leis.get("shifters") or []
    if shifters:
        coefs = ", ".join(sh.get("coefficient", "?") for sh in shifters)
        vars_set = ", ".join(sorted({(sh or {}).get("variable", "?") for sh in shifters}))
        out.append(["utility.leisure.shifters", "Utility-leisure shifters",
                    len(shifters), vars_set, coefs])
    return out


def _utility_consumption_inventory(blocks: Dict[str, Any]) -> List[List[Any]]:
    """Inventory rows for the utility.consumption block."""
    u_c = (blocks.get("utility_consumption") or {}) if isinstance(blocks, dict) else {}
    if not u_c:
        return []
    out: List[List[Any]] = []
    coef = u_c.get("coefficient")
    theta = u_c.get("box_cox_exponent")
    if coef:
        out.append(["utility.consumption.coefficient", "consumption scale", 1, "—", coef])
    if theta:
        out.append(["utility.consumption.box_cox_exponent", "consumption θ_c", 1, "—", theta])
    return out


def _parameter_block_for_markdown(
    name: str,
    coef_map: Dict[str, str],
) -> str:
    """Classify a parameter into a compact reporting block."""
    block = _classify_param_via_blocks(name, coef_map)
    if block:
        labels = {
            "preference": "preference",
            "hours": "employment_hours_opportunity",
            "market": "market_residual_opportunity",
            "wage": "wage_opportunity",
            "occupation": "occupation_opportunity",
        }
        return labels.get(block, block)

    lower = name.lower()
    if "beta_occ_" in lower:
        return "occupation_opportunity"
    if lower.endswith(".beta_e") or lower == "beta_e" or "beta_h_" in lower:
        return "employment_hours_opportunity"
    if "beta_e_" in lower:
        return "market_residual_opportunity"
    if "beta_w" in lower or "sigma" in lower:
        return "wage_opportunity"
    if any(x in lower for x in ["beta_l", "beta_c", "theta_l", "theta_c"]):
        return "preference"
    return "other"


def _fit_moment_rows(fit_results: Dict[str, Dict[str, Any]]) -> List[List[Any]]:
    rows = []
    for group, vals in sorted((fit_results or {}).items()):
        rows.append([
            group,
            vals.get("participation_observed"),
            vals.get("participation_predicted"),
            vals.get("mean_hours_observed"),
            vals.get("mean_hours_predicted"),
        ])
    return rows


def _hours_distribution_rows(fit_results: Dict[str, Dict[str, Any]]) -> List[List[Any]]:
    rows = []
    for group, vals in sorted((fit_results or {}).items()):
        obs = vals.get("hours_distribution_observed") or {}
        pred = vals.get("hours_distribution_predicted") or {}
        for bin_label in sorted(set(obs) | set(pred), key=str):
            rows.append([group, bin_label, obs.get(bin_label), pred.get(bin_label)])
    return rows


def _row_get_suffix(row: Dict[str, Any], suffix: str, default: Any = None) -> Any:
    """Get a dict value by exact key or by ASCII-safe suffix match."""
    if suffix in row:
        return row.get(suffix)
    for key, value in row.items():
        if str(key).endswith(suffix):
            return value
    return default


def _muc_beta_theta_values(row: Dict[str, Any]) -> Tuple[Any, Any]:
    """Resolve beta_c/theta_c from MUC rows without depending on Greek glyphs."""
    beta_c = row.get("beta_c")
    theta_c = row.get("theta_c")
    if beta_c is not None and theta_c is not None:
        return beta_c, theta_c

    c_like_values = [
        value for key, value in row.items()
        if str(key).endswith("_c") and str(key) not in {"MUC at Median C"}
    ]
    if beta_c is None and c_like_values:
        beta_c = c_like_values[0]
    if theta_c is None and len(c_like_values) > 1:
        theta_c = c_like_values[1]
    return beta_c, theta_c


def _utility_parameter_rows(parsed_params: ParsedParameters) -> List[List[Any]]:
    """Compact numerical summary of utility/preference equations by group."""
    rows = []
    for group in sorted(set(parsed_params.preference_groups or [])):
        params = parsed_params.get_all_params_for_group(group)
        beta_l_terms = []
        for key, value in sorted(params.items()):
            if not key.startswith("beta_l"):
                continue
            if key == "beta_l0" or "." in key:
                continue
            beta_l_terms.append(f"{key}={_md_clean(value)}")
        rows.append([
            group,
            params.get("beta_c"),
            params.get("theta_c"),
            params.get("beta_l0"),
            "; ".join(beta_l_terms) if beta_l_terms else "none",
            params.get("theta_l"),
            params.get("beta_cl"),
        ])
    return rows


def _safe_read_parquet(path: Path) -> Optional[pd.DataFrame]:
    """Read a parquet file, returning None if it is absent or unreadable."""
    try:
        return pd.read_parquet(path) if path.exists() else None
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning(f"Could not read {path}: {exc}")
        return None


def _working_mask_for_cols(df: pd.DataFrame, work_col: str, hours_col: str) -> pd.Series:
    """Prefer an explicit working indicator, fallback to hours > 0."""
    if work_col in df.columns:
        return pd.to_numeric(df[work_col], errors="coerce").fillna(0) > 0
    if hours_col in df.columns:
        return pd.to_numeric(df[hours_col], errors="coerce").fillna(0) > 0
    return pd.Series(False, index=df.index)


def _choice_data_footprint_rows(mnl_base: Optional[Path]) -> List[List[Any]]:
    """Summarize rows, groups, alternatives, chosen rows, and working rows."""
    if mnl_base is None:
        return []
    base = Path(mnl_base)
    rows = []
    for dataset, path in [
        ("singles", Path(str(base) + "__singles.parquet")),
        ("couples", Path(str(base) + "__couples.parquet")),
    ]:
        df = _safe_read_parquet(path)
        if df is None or len(df) == 0:
            continue
        alt_counts = df.groupby("idhh").size() if "idhh" in df.columns else pd.Series(dtype=float)
        chosen_col = "is_chosen" if "is_chosen" in df.columns else ("chosen" if "chosen" in df.columns else None)
        chosen_rows = int(pd.to_numeric(df[chosen_col], errors="coerce").fillna(0).sum()) if chosen_col else None
        if dataset == "singles":
            working = int(_working_mask_for_cols(df, "working", "hours").sum())
        else:
            wm = int(_working_mask_for_cols(df, "working_male", "hours_male").sum())
            wf = int(_working_mask_for_cols(df, "working_female", "hours_female").sum())
            working = f"male={wm}; female={wf}"
        rows.append([
            dataset,
            len(df),
            df["idhh"].nunique() if "idhh" in df.columns else None,
            alt_counts.min() if len(alt_counts) else None,
            alt_counts.median() if len(alt_counts) else None,
            alt_counts.max() if len(alt_counts) else None,
            chosen_rows,
            working,
            len(df.columns),
        ])
    return rows


def _proposal_prior_diagnostic_rows(mnl_base: Optional[Path]) -> List[List[Any]]:
    """Check proposal aliases, prior positivity, and prior reconstruction."""
    if mnl_base is None:
        return []
    base = Path(mnl_base)
    rows = []
    forbidden = {"lindi", "industry", "nace", "job_id", "type_id", "log_q_job", "log_q_total", "log_q_state"}

    def _max_abs(series: pd.Series) -> Optional[float]:
        if series is None or len(series) == 0:
            return None
        return float(pd.to_numeric(series, errors="coerce").abs().max())

    for dataset, path in [
        ("singles", Path(str(base) + "__singles.parquet")),
        ("couples", Path(str(base) + "__couples.parquet")),
    ]:
        df = _safe_read_parquet(path)
        if df is None or len(df) == 0:
            continue
        present_forbidden = ", ".join(sorted(forbidden & set(df.columns))) or "none"
        prior_min = float(pd.to_numeric(df["prior"], errors="coerce").min()) if "prior" in df.columns else None
        log_prior_diff = None
        if "prior" in df.columns and "log_prior" in df.columns:
            log_prior_diff = _max_abs(df["log_prior"] - np.log(np.maximum(pd.to_numeric(df["prior"], errors="coerce"), 1e-300)))

        recon_diff = None
        missing_aliases: List[str] = []
        if dataset == "singles":
            needed = ["log_q_E", "log_q_H", "log_q_W", "log_q_Occ"]
            missing_aliases = [c for c in needed if c not in df.columns]
            if not missing_aliases and "log_prior" in df.columns:
                working = _working_mask_for_cols(df, "working", "hours").astype(float)
                recon = df["log_q_E"] + working * (df["log_q_H"] + df["log_q_W"] + df["log_q_Occ"])
                recon_diff = _max_abs(df["log_prior"] - recon)
        else:
            needed = [
                "log_q_E_male", "log_q_H_male", "log_q_W_male", "log_q_Occ_male",
                "log_q_E_female", "log_q_H_female", "log_q_W_female", "log_q_Occ_female",
            ]
            missing_aliases = [c for c in needed if c not in df.columns]
            if not missing_aliases and "log_prior" in df.columns:
                wm = _working_mask_for_cols(df, "working_male", "hours_male").astype(float)
                wf = _working_mask_for_cols(df, "working_female", "hours_female").astype(float)
                recon = (
                    df["log_q_E_male"] + wm * (df["log_q_H_male"] + df["log_q_W_male"] + df["log_q_Occ_male"])
                    + df["log_q_E_female"] + wf * (df["log_q_H_female"] + df["log_q_W_female"] + df["log_q_Occ_female"])
                )
                recon_diff = _max_abs(df["log_prior"] - recon)
        rows.append([
            dataset,
            prior_min,
            log_prior_diff,
            recon_diff,
            ", ".join(missing_aliases) if missing_aliases else "none",
            present_forbidden,
        ])
    return rows


def _weighted_quantile(values: np.ndarray, weights: np.ndarray, qs: List[float]) -> List[Optional[float]]:
    """Compute weighted quantiles for finite values and positive weights."""
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not mask.any():
        return [None for _ in qs]
    values = values[mask]
    weights = weights[mask]
    order = np.argsort(values)
    values = values[order]
    weights = weights[order]
    cdf = np.cumsum(weights) / np.sum(weights)
    return [float(np.interp(q, cdf, values)) for q in qs]


def _weighted_mean(values: np.ndarray, weights: np.ndarray) -> Optional[float]:
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not mask.any():
        return None
    return float(np.average(values[mask], weights=weights[mask]))


def _prediction_frames(
    parsed_params: ParsedParameters,
    mnl_base: Optional[Path],
    spec: Optional[Any],
) -> List[Tuple[str, pd.DataFrame, str, str, Optional[str]]]:
    """Build group-level frames with predicted probabilities for summaries."""
    if mnl_base is None:
        return []
    base = Path(mnl_base)
    out: List[Tuple[str, pd.DataFrame, str, str, Optional[str]]] = []
    singles = _safe_read_parquet(Path(str(base) + "__singles.parquet"))
    couples = _safe_read_parquet(Path(str(base) + "__couples.parquet"))

    if singles is not None and len(singles):
        gender_col = "dgn" if "dgn" in singles.columns else "gender"
        for gender_code, group_key, label in [(1, "sm", "singles_male"), (0, "sf", "singles_female")]:
            df_g = singles[singles[gender_col] == gender_code].copy()
            if len(df_g) == 0:
                continue
            params = None
            for try_key in [group_key, group_key.upper(), "joint"]:
                if try_key in parsed_params.params_by_group:
                    params = parsed_params.get_all_params_for_group(try_key)
                    break
            if params:
                df_g = _add_predicted_probabilities(df_g, params, spec=spec, is_couples=False, group_suffix=f"_{group_key}")
                out.append((label, df_g, "wage", "hours", "loc4" if "loc4" in df_g.columns else None))

    if couples is not None and len(couples):
        params = None
        for try_key in ["joint", "cou", "couples", "m"]:
            if try_key in parsed_params.params_by_group:
                params = parsed_params.get_all_params_for_group(try_key)
                break
        if params:
            df_c = _add_predicted_probabilities(couples, params, spec=spec, is_couples=True)
            out.append(("couples_male", df_c, "wage_male", "hours_male", "loc4_male" if "loc4_male" in df_c.columns else None))
            out.append(("couples_female", df_c, "wage_female", "hours_female", "loc4_female" if "loc4_female" in df_c.columns else None))
    return out


def _wage_distribution_summary_rows(
    parsed_params: ParsedParameters,
    mnl_base: Optional[Path],
    spec: Optional[Any],
) -> List[List[Any]]:
    """Observed and predicted wage quantiles by group, text-only."""
    rows = []
    for label, df, wage_col, hours_col, _ in _prediction_frames(parsed_params, mnl_base, spec):
        if wage_col not in df.columns or hours_col not in df.columns:
            continue
        chosen_col = "is_chosen" if "is_chosen" in df.columns else ("chosen" if "chosen" in df.columns else None)
        if not chosen_col:
            continue
        work = pd.to_numeric(df[hours_col], errors="coerce").fillna(0) > 0
        obs = pd.to_numeric(df.loc[work & (df[chosen_col] == 1), wage_col], errors="coerce").dropna().to_numpy()
        pred_values = pd.to_numeric(df.loc[work, wage_col], errors="coerce").to_numpy()
        pred_weights = pd.to_numeric(df.loc[work, "pred_prob"], errors="coerce").fillna(0).to_numpy()
        pred_q10, pred_q50, pred_q90 = _weighted_quantile(pred_values, pred_weights, [0.10, 0.50, 0.90])
        obs_q10, obs_q50, obs_q90 = (
            [float(np.nanquantile(obs, q)) for q in [0.10, 0.50, 0.90]]
            if obs.size else [None, None, None]
        )
        rows.append([
            label,
            int(obs.size),
            float(np.sum(pred_weights)) if pred_weights.size else None,
            float(np.nanmean(obs)) if obs.size else None,
            _weighted_mean(pred_values, pred_weights),
            obs_q10,
            obs_q50,
            obs_q90,
            pred_q10,
            pred_q50,
            pred_q90,
        ])
    return rows


def _loc4_label(value: Any) -> str:
    mapping = {
        -2: "unknown_observed_working",
        -1: "nonwork",
        1: "routine_manual_ref",
        2: "nonroutine_manual",
        3: "routine_cognitive",
        4: "nonroutine_cognitive",
    }
    try:
        key = int(value)
    except (TypeError, ValueError):
        return str(value)
    return mapping.get(key, str(key))


def _occupation_share_rows(
    parsed_params: ParsedParameters,
    mnl_base: Optional[Path],
    spec: Optional[Any],
) -> List[List[Any]]:
    """Observed vs predicted occupation shares when loc4-style columns exist."""
    rows = []
    for label, df, _, hours_col, occ_col in _prediction_frames(parsed_params, mnl_base, spec):
        if not occ_col or occ_col not in df.columns or hours_col not in df.columns:
            continue
        chosen_col = "is_chosen" if "is_chosen" in df.columns else ("chosen" if "chosen" in df.columns else None)
        if not chosen_col:
            continue
        work = pd.to_numeric(df[hours_col], errors="coerce").fillna(0) > 0
        obs_counts = df.loc[work & (df[chosen_col] == 1), occ_col].value_counts(dropna=False)
        pred_weights = df.loc[work].groupby(occ_col)["pred_prob"].sum()
        obs_total = float(obs_counts.sum())
        pred_total = float(pred_weights.sum())
        categories = sorted(
            set(obs_counts.index.tolist()) | set(pred_weights.index.tolist()),
            key=lambda x: (pd.isna(x), str(x)),
        )
        for cat in categories:
            obs_count = float(obs_counts.get(cat, 0.0))
            pred_weight = float(pred_weights.get(cat, 0.0))
            rows.append([
                label,
                occ_col,
                cat,
                _loc4_label(cat),
                obs_count / obs_total if obs_total else None,
                pred_weight / pred_total if pred_total else None,
                obs_count,
                pred_weight,
            ])
    return rows


def _marginal_utility_distribution_rows(mu_results: Dict[str, Any]) -> List[List[Any]]:
    """Summarize negative and mean MUC/MUL by group."""
    rows = []
    for group, vals in sorted((mu_results or {}).get("by_group", {}).items()):
        rows.append([
            group,
            vals.get("N"),
            vals.get("n_neg_muc"),
            vals.get("pct_neg_muc"),
            vals.get("mean_muc"),
            vals.get("n_neg_mul"),
            vals.get("pct_neg_mul"),
            vals.get("mean_mul"),
        ])
    totals = (mu_results or {}).get("totals") or {}
    if totals:
        rows.append([
            "total",
            None,
            totals.get("n_negative_muc_total"),
            totals.get("pct_negative_muc_total"),
            None,
            totals.get("n_negative_mul_total"),
            totals.get("pct_negative_mul_total"),
            None,
        ])
    return rows


def _warning_rows(
    fit_results: Dict[str, Dict[str, Any]],
    hessian_interp: Optional[str],
    hessian_diagnostics: Optional[Dict[str, Any]],
    probability_rows: List[List[Any]],
    prior_rows: List[List[Any]],
) -> List[List[Any]]:
    """Collect compact warnings that are useful in an LLM memory artifact."""
    rows: List[List[Any]] = []
    if hessian_interp:
        rows.append(["identification", hessian_interp])
    for group, vals in sorted((fit_results or {}).items()):
        pred_part = vals.get("participation_predicted")
        if pred_part is not None and np.isfinite(pred_part) and float(pred_part) >= 0.99:
            rows.append(["fit", f"{group}: predicted participation is very high ({float(pred_part):.4f})"])
    p_min = None
    for key, value in probability_rows:
        if key == "p_chosen_min":
            p_min = value
    if p_min is not None and float(p_min) < 1e-6:
        rows.append(["probability", f"minimum chosen probability is very small ({float(p_min):.3e})"])
    for dataset, _, log_diff, recon_diff, missing, forbidden in prior_rows:
        if missing != "none":
            rows.append(["proposal", f"{dataset}: missing aliases {missing}"])
        if forbidden != "none":
            rows.append(["proposal", f"{dataset}: forbidden diagnostic columns present: {forbidden}"])
        if log_diff is not None and float(log_diff) > 1e-8:
            rows.append(["proposal", f"{dataset}: log_prior != log(prior), max diff {float(log_diff):.3e}"])
        if recon_diff is not None and float(recon_diff) > 1e-8:
            rows.append(["proposal", f"{dataset}: prior alias reconstruction max diff {float(recon_diff):.3e}"])
    if hessian_diagnostics and hessian_diagnostics.get("n_negative_eigenvalues"):
        if int(hessian_diagnostics.get("n_negative_eigenvalues") or 0) > 0:
            rows.append(["hessian", "negative eigenvalues present; inspect SE and local optimum diagnostics"])
    return rows


def generate_llm_markdown_summary(
    parsed_params: ParsedParameters,
    data: Dict[str, Any],
    fit_stats: Dict[str, Any],
    fit_results: Dict[str, Dict[str, Any]],
    elasticities_df: pd.DataFrame,
    muc_analysis: List[Dict[str, Any]],
    prob_diagnostics: Dict[str, Any],
    bound_diagnostics: List[Dict[str, Any]],
    hessian_diagnostics: Optional[Dict[str, Any]],
    run_metadata: Dict[str, Any],
    output_path: Path,
    estimation_results_path: Path,
    html_report_path: Optional[Path] = None,
    param_csv_path: Optional[Path] = None,
    elasticities_csv_path: Optional[Path] = None,
    post_output_dir: Optional[Path] = None,
    mnl_base: Optional[Path] = None,
    spec_config: Optional[Path] = None,
    mu_results: Optional[Dict[str, Any]] = None,
    spec: Optional[Any] = None,
    diagnostics_bundle: Optional[Any] = None,
    report_profile: str = DEFAULT_PROFILE,
) -> Path:
    """
    Write a compact, graph-free Markdown report for LLM/paper workflows.

    This is intentionally text/table only. Large plots, HTML, and household-
    level dumps stay in the post-estimation output folder.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    blocks = _load_yaml_spec_blocks(spec_config)
    coef_map = _coef_to_block_map(blocks)
    param_df = parsed_params.to_dataframe().copy()
    param_df["block"] = param_df["parameter"].apply(
        lambda x: _parameter_block_for_markdown(str(x), coef_map)
    )

    summary = data.get("summary", {}) if isinstance(data.get("summary"), dict) else {}
    result_groups = data.get("results", {}) if isinstance(data.get("results"), dict) else {}
    group_rows = []
    for group, group_data in sorted(result_groups.items()):
        group_rows.append([
            group,
            group_data.get("success"),
            group_data.get("message"),
            group_data.get("n_iterations"),
            group_data.get("n_function_evaluations"),
            group_data.get("gradient_norm"),
            group_data.get("final_ll") or group_data.get("log_likelihood"),
            group_data.get("walltime_seconds"),
        ])

    param_rows = []
    for _, row in param_df.sort_values(["block", "parameter"]).iterrows():
        param_rows.append([
            row.get("block"),
            row.get("parameter"),
            row.get("estimate"),
            row.get("std_error"),
            row.get("t_value"),
            row.get("p_value"),
            row.get("lower_bound"),
            row.get("upper_bound"),
            row.get("initial_value"),
        ])

    # ----- Spec-block inventory ------------------------------------------------
    def _shifter_inventory_row(block_name: str, label: str, shifters: List[Dict[str, Any]]) -> List[Any]:
        n = len(shifters or [])
        coefs = ", ".join(
            (sh or {}).get("coefficient", "?") for sh in (shifters or [])
        ) if shifters else ""
        variables = ", ".join(sorted({(sh or {}).get("variable", "?") for sh in (shifters or [])}))
        return [block_name, label, n, variables, coefs]

    spec_inventory_rows: List[List[Any]] = []
    if isinstance(blocks, dict) and blocks:
        spec_inventory_rows.extend(_utility_consumption_inventory(blocks))
        spec_inventory_rows.extend(_utility_leisure_inventory(blocks))
        spec_inventory_rows.append(_shifter_inventory_row("hours_opportunity", "Employment/Hours", blocks.get("hours") or []))
        spec_inventory_rows.append(_shifter_inventory_row("market_opportunity", "Market residual", blocks.get("market") or []))
        spec_inventory_rows.append(_shifter_inventory_row("wage_opportunity.mean_shifters", "Mincer mean", blocks.get("wage_mean") or []))
        if blocks.get("wage_sigma"):
            spec_inventory_rows.append(["wage_opportunity.variance", "Mincer sigma", 1, "-", blocks["wage_sigma"]])
        spec_inventory_rows.append(_shifter_inventory_row("occupation_opportunity", "Occupation", blocks.get("occupation") or []))

    # ----- Symbolic + numerical opportunity equations --------------------------
    symbolic_equations_lines: List[str] = []
    if isinstance(blocks, dict) and blocks:
        # Hours + market
        emp_shifters = list(blocks.get("hours") or []) + list(blocks.get("market") or [])
        if emp_shifters:
            symbolic_equations_lines.append("O^E + O^H =")
            for sh in emp_shifters:
                symbolic_equations_lines.append(f"  + {_shifter_symbolic_term(sh)}")
            symbolic_equations_lines.append("")
        # Wage
        wage_mean = list(blocks.get("wage_mean") or [])
        if wage_mean or blocks.get("wage_sigma"):
            symbolic_equations_lines.append("mu_w =")
            for sh in wage_mean:
                var = (sh or {}).get("variable")
                coef = (sh or {}).get("coefficient", "?")
                if var == "intercept":
                    symbolic_equations_lines.append(f"  + {coef}")
                else:
                    symbolic_equations_lines.append(f"  + {_shifter_symbolic_term(sh)}")
            sigma_name = blocks.get("wage_sigma") or "σ"
            symbolic_equations_lines.append(f"log(wage) = mu_w + eps,  eps ~ N(0, {sigma_name}^2)")
            symbolic_equations_lines.append("")
        # Occupation
        occ_shifters = list(blocks.get("occupation") or [])
        if occ_shifters:
            occ_var = blocks.get("occ_var") or "occ"
            occ_ref = blocks.get("occ_ref")
            symbolic_equations_lines.append(f"O^Occ (reference {occ_var}={occ_ref}):")
            by_grp: Dict[str, List[Dict[str, Any]]] = {}
            for sh in occ_shifters:
                by_grp.setdefault((sh or {}).get("applies_to") or "both", []).append(sh)
            for applies, sh_list in by_grp.items():
                symbolic_equations_lines.append(f"  applies_to={applies}:")
                for sh in sh_list:
                    symbolic_equations_lines.append(f"    + {_shifter_symbolic_term(sh)}")
            symbolic_equations_lines.append("")

    # Numerical equations: one row per (block_group, term, coefficient_value)
    numerical_eq_rows: List[List[Any]] = []
    if isinstance(blocks, dict) and blocks:
        groups_pri = list(getattr(parsed_params, "groups", []) or []) or ["joint"]
        # Employment / hours
        for sh in (blocks.get("hours") or []) + (blocks.get("market") or []):
            coef = (sh or {}).get("coefficient")
            if not coef:
                continue
            val, src = _pick_value_for_coef(coef, parsed_params, groups_pri)
            numerical_eq_rows.append([
                "employment_hours", _shifter_symbolic_term(sh),
                coef, src or "-", _md_clean(val),
            ])
        for sh in (blocks.get("wage_mean") or []):
            coef = (sh or {}).get("coefficient")
            if not coef:
                continue
            val, src = _pick_value_for_coef(coef, parsed_params, groups_pri)
            numerical_eq_rows.append([
                "wage_mean", _shifter_symbolic_term(sh),
                coef, src or "-", _md_clean(val),
            ])
        if blocks.get("wage_sigma"):
            coef = blocks["wage_sigma"]
            val, src = _pick_value_for_coef(coef, parsed_params, groups_pri)
            numerical_eq_rows.append(["wage_sigma", coef, coef, src or "-", _md_clean(val)])
        for sh in (blocks.get("occupation") or []):
            coef = (sh or {}).get("coefficient")
            if not coef:
                continue
            applies = (sh or {}).get("applies_to") or "both"
            # Prefer the matching group when applies_to is sm/sf/cm/cf
            group_aliases = {"sm": "singles_male", "sf": "singles_female",
                             "cm": "couples_male", "cf": "couples_female"}
            target = group_aliases.get(applies, applies)
            val = _pick_value_for_group(coef, target, parsed_params)
            src = target if val is not None else None
            if val is None:
                val, src = _pick_value_for_coef(coef, parsed_params, [target] + groups_pri)
            numerical_eq_rows.append([
                f"occupation:{applies}", _shifter_symbolic_term(sh),
                coef, src or "-", _md_clean(val),
            ])

    # ----- Per-block parameter counts and significance summary -----------------
    block_count_rows: List[List[Any]] = []
    def _count_block(block_name: str) -> List[Any]:
        sub = param_df[param_df["block"] == block_name]
        n_total = len(sub)
        if n_total == 0:
            return []
        n_estim = int(sub.apply(
            lambda r: not (
                isinstance(r.get("lower_bound"), (int, float))
                and isinstance(r.get("upper_bound"), (int, float))
                and (float(r["upper_bound"]) - float(r["lower_bound"])) <= 1e-6
            ),
            axis=1,
        ).sum())
        p_vals = pd.to_numeric(sub["p_value"], errors="coerce")
        n_sig_001 = int((p_vals < 0.001).sum())
        n_sig_01 = int((p_vals < 0.01).sum())
        n_sig_05 = int((p_vals < 0.05).sum())
        n_sig_10 = int((p_vals < 0.10).sum())
        return [block_name, n_total, n_estim, n_sig_001, n_sig_01, n_sig_05, n_sig_10]

    for blk_name in [
        "preference", "employment_hours_opportunity", "market_residual_opportunity",
        "wage_opportunity", "occupation_opportunity", "other",
    ]:
        row = _count_block(blk_name)
        if row:
            block_count_rows.append(row)

    # ----- Top movers (initial -> final) ---------------------------------------
    mover_rows: List[List[Any]] = []
    if "initial_value" in param_df.columns:
        df_m = param_df.copy()
        df_m["initial_value"] = pd.to_numeric(df_m["initial_value"], errors="coerce")
        df_m["estimate"] = pd.to_numeric(df_m["estimate"], errors="coerce")
        df_m["delta"] = (df_m["estimate"] - df_m["initial_value"]).abs()
        df_m = df_m.dropna(subset=["delta"])
        df_m = df_m.sort_values("delta", ascending=False).head(15)
        for _, row in df_m.iterrows():
            init = row.get("initial_value")
            est = row.get("estimate")
            mover_rows.append([
                row.get("block"),
                row.get("parameter"),
                init,
                est,
                float(est) - float(init) if pd.notna(init) and pd.notna(est) else None,
            ])

    # ----- Hessian condition interpretation ------------------------------------
    hessian_interp: Optional[str] = None
    if hessian_diagnostics and isinstance(hessian_diagnostics, dict):
        cond = hessian_diagnostics.get("condition_number")
        n_neg = hessian_diagnostics.get("n_negative_eigenvalues")
        try:
            cond_f = float(cond) if cond is not None else None
        except (TypeError, ValueError):
            cond_f = None
        labels: List[str] = []
        if cond_f is not None:
            if cond_f < 1e3:
                labels.append("well-conditioned (κ < 1e3)")
            elif cond_f < 1e6:
                labels.append("moderately conditioned (κ < 1e6)")
            elif cond_f < 1e10:
                labels.append("weakly conditioned (1e6 ≤ κ < 1e10)")
            else:
                labels.append("ill-conditioned (κ ≥ 1e10)")
        if n_neg and int(n_neg) > 0:
            labels.append(f"{int(n_neg)} negative eigenvalue(s) — not at a local maximum or numerically singular")
        hessian_interp = "; ".join(labels) if labels else None

    footprint_rows = _choice_data_footprint_rows(mnl_base)
    prior_rows = _proposal_prior_diagnostic_rows(mnl_base)
    utility_rows = _utility_parameter_rows(parsed_params)
    mu_distribution_rows = _marginal_utility_distribution_rows(mu_results or {})
    wage_distribution_rows = _wage_distribution_summary_rows(parsed_params, mnl_base, spec)
    occupation_share_rows = _occupation_share_rows(parsed_params, mnl_base, spec)

    # Enrichments: load MNL data once for per-group breakdowns and observed stats.
    _mnl_singles_df, _mnl_couples_df = _read_mnl_dataframes_for_summary(mnl_base)
    sample_size_rows = _sample_size_rows(_mnl_singles_df, _mnl_couples_df)
    x_descriptive_rows = _x_descriptives_rows(_mnl_singles_df, _mnl_couples_df)
    # Implied sigma from estimated parameters (works across joint/per-group runs)
    implied_sigma_val: Optional[float] = None
    if isinstance(blocks, dict) and blocks.get("wage_sigma"):
        sig_val, _ = _pick_value_for_coef(
            blocks["wage_sigma"], parsed_params,
            list(getattr(parsed_params, "groups", []) or []) or ["joint"],
        )
        if sig_val is not None:
            try:
                implied_sigma_val = float(sig_val)
            except (TypeError, ValueError):
                implied_sigma_val = None
    observed_log_wage_rows_list = _observed_log_wage_rows(
        _mnl_singles_df, _mnl_couples_df, implied_sigma_val,
    )
    hours_quantile_rows = _hours_quantile_rows(_mnl_singles_df, _mnl_couples_df)
    distribution_fit_rows = _distribution_fit_l1_rows(fit_results)
    bound_proximity_rows = _bound_proximity_rows(param_df, pct=0.05)
    convergence_warning_rows = _convergence_warning_rows(
        param_df, hessian_diagnostics, prob_diagnostics, bound_diagnostics, fit_stats,
    )
    top_significant_rows = _top_significant_rows(param_df, n=15)
    git_info = _git_revision_info()

    # Bundle-driven reorganized fit-stats sections (A/B/C/D). Falls back
    # to a placeholder note if the bundle is unavailable.
    _bundle_param_table_md_block = ""
    _bundle_solver_md_block = ""
    _bundle_identification_md_block = ""
    _bundle_probability_md_block = ""
    if diagnostics_bundle is not None and HAS_DIAGNOSTICS_BUNDLE:
        try:
            _bundle_fit_lines = render_fit_stats_split_markdown(diagnostics_bundle)
            _bundle_fit_split_md_block = "\n".join(_bundle_fit_lines)
        except Exception as _e:
            LOGGER.warning(f"Could not render bundle Markdown fit sections: {_e}")
            _bundle_fit_split_md_block = ""
        # Phase-2 bundle renderers (same data as HTML).
        try:
            _bundle_param_table_md_block = "\n".join(
                render_param_table_markdown(diagnostics_bundle)
            )
        except Exception as _e:
            LOGGER.warning(f"Could not render bundle param-table Markdown: {_e}")
        try:
            _bundle_solver_md_block = "\n".join(
                render_solver_section_markdown(diagnostics_bundle)
            )
        except Exception as _e:
            LOGGER.warning(f"Could not render bundle solver Markdown: {_e}")
        try:
            _bundle_identification_md_block = "\n".join(
                render_identification_markdown(diagnostics_bundle)
            )
        except Exception as _e:
            LOGGER.warning(f"Could not render bundle identification Markdown: {_e}")
        try:
            _bundle_probability_md_block = "\n".join(
                render_probability_fit_markdown(diagnostics_bundle)
            )
        except Exception as _e:
            LOGGER.warning(f"Could not render bundle probability Markdown: {_e}")
    else:
        _bundle_fit_split_md_block = (
            "## Fit Statistics (reorganized)\n\n"
            "_Diagnostics bundle unavailable; see legacy combined table below._\n"
        )

    fit_rows = [
        ["log_likelihood", fit_stats.get("log_likelihood")],
        ["ll_null_uniform", fit_stats.get("ll_null_uniform")],
        ["ll_null_prior_corrected", fit_stats.get("ll_null_prior_corrected")],
        ["rho_squared", fit_stats.get("rho_squared")],
        ["rho_squared_adj", fit_stats.get("rho_squared_adj")],
        ["rho_squared_uniform", fit_stats.get("rho_squared_uniform")],
        ["rho_squared_prior_corrected", fit_stats.get("rho_squared_prior_corrected")],
        ["AIC", fit_stats.get("AIC")],
        ["BIC", fit_stats.get("BIC")],
        ["AIC_per_obs", fit_stats.get("AIC_per_obs")],
        ["n_observations", fit_stats.get("n_observations")],
        ["n_groups", fit_stats.get("n_groups")],
        ["n_parameters", fit_stats.get("n_parameters")],
        ["n_obs_long", fit_stats.get("n_obs_long")],
    ]

    probability_rows = []
    for key, value in (prob_diagnostics.get("prob_sum_errors") or {}).items():
        probability_rows.append([f"prob_sum_{key}", value])
    for key, value in (prob_diagnostics.get("p_chosen_dist") or {}).items():
        probability_rows.append([f"p_chosen_{key}", value])

    warning_rows = _warning_rows(
        fit_results,
        hessian_interp,
        hessian_diagnostics,
        probability_rows,
        prior_rows,
    )

    worst_rows = [
        [i + 1, row.get("idhh"), row.get("group"), row.get("p_chosen"), row.get("ll_i")]
        for i, row in enumerate((prob_diagnostics.get("worst_fit_households") or [])[:10])
    ]

    hessian_rows = []
    for key in [
        "condition_number",
        "min_eigenvalue",
        "max_eigenvalue",
        "n_negative_eigenvalues",
    ]:
        if hessian_diagnostics and key in hessian_diagnostics:
            hessian_rows.append([key, hessian_diagnostics.get(key)])
    top_corr_rows = [
        [row.get("param_i"), row.get("param_j"), row.get("corr")]
        for row in ((hessian_diagnostics or {}).get("top_correlations") or [])[:10]
    ]
    eig_rows = []
    for idx, row in enumerate(((hessian_diagnostics or {}).get("eigenvector_diagnostics") or [])[:3], 1):
        loads = "; ".join(
            f"{x.get('param')}={_md_clean(x.get('loading'))}"
            for x in row.get("top_loadings", [])[:5]
        )
        eig_rows.append([idx, row.get("eigenvalue"), loads])

    bound_rows = [
        [row.get("parameter"), row.get("estimate"), row.get("bound"), row.get("side")]
        for row in (bound_diagnostics or [])
    ]

    lines = [
        "# RURO Low-Token Post-Estimation Summary",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Purpose",
        "",
        "Compact text-only report for Git, paper drafting, and LLM review.",
        "Figures and large HTML output are intentionally omitted.",
        "",
        "## Sources",
        "",
        _md_table(
            ["item", "path_or_value"],
            [
                ["estimation_results_json", estimation_results_path],
                ["html_report", html_report_path],
                ["post_output_dir", post_output_dir],
                ["params_csv", param_csv_path],
                ["elasticities_csv", elasticities_csv_path],
                ["mnl_base", mnl_base],
                ["spec_config", spec_config],
            ],
        ),
        "## Run Metadata",
        "",
        _md_table(
            ["field", "value"],
            [
                ["specification", run_metadata.get("spec_name") or data.get("specification")],
                ["model_family", run_metadata.get("model_family")],
                ["market_opportunity_tier", run_metadata.get("market_opportunity_tier")],
                ["prior_correction_applied", run_metadata.get("prior_correction_applied")],
                ["prior_correction_form", run_metadata.get("prior_correction_form")],
                ["market_centering_applied", run_metadata.get("market_centering_applied")],
                ["wage_spec", data.get("wage_spec")],
                ["estimation_walltime_seconds", summary.get("total_walltime_seconds")],
            ],
        ),
        "## Source Environment",
        "",
        _md_table(
            ["field", "value"],
            [
                ["git_sha", git_info.get("git_sha")],
                ["git_branch", git_info.get("git_branch")],
                ["git_dirty", git_info.get("git_dirty")],
            ],
        ) if git_info else "_Git info unavailable._\n",
        "## Choice Data Footprint",
        "",
        _md_table(
            ["dataset", "rows", "groups", "alt_min", "alt_median", "alt_max", "chosen_rows", "working_rows", "n_columns"],
            footprint_rows,
        ) if footprint_rows else "_MNL base not provided or not readable._\n",
        "## Per-Group Sample Sizes",
        "",
        _md_table(
            ["group", "n_obs", "n_households", "alts_per_hh", "n_chosen", "n_working"],
            sample_size_rows,
        ) if sample_size_rows else "_MNL data not loaded._\n",
        "## Sample Descriptives (chosen alternatives, by group)",
        "",
        _md_table(
            ["group", "variable", "mean", "std", "min", "max", "n"],
            x_descriptive_rows,
        ) if x_descriptive_rows else "_No X-variable descriptives available._\n",
        "## Proposal And Prior Diagnostics",
        "",
        _md_table(
            ["dataset", "min_prior", "max_abs_log_prior_minus_log_density", "max_abs_prior_alias_reconstruction", "missing_aliases", "forbidden_columns_present"],
            prior_rows,
        ) if prior_rows else "_MNL base not provided or not readable._\n",
        "## Warnings And Review Flags",
        "",
        _md_table(["type", "message"], warning_rows) if warning_rows else "_No automatic warnings raised._\n",
        "## Convergence Health Summary",
        "",
        _md_table(["metric", "value"], convergence_warning_rows)
            if convergence_warning_rows else "_Convergence summary unavailable._\n",
        "## Model Index Equation",
        "",
        (
            "V_ij = U_ij"
            + (" + O^E_ij + O^H_ij" if (blocks.get("hours") or blocks.get("market")) else "")
            + (" + O^W_ij" if (blocks.get("wage_mean") or blocks.get("wage_sigma")) else "")
            + (" + O^Occ_ij" if blocks.get("occupation") else "")
            + " - log_prior_ij"
        ) if isinstance(blocks, dict) and blocks else "_Spec YAML not loaded; equation omitted._",
        "",
        "P_ij = exp(V_ij) / sum_k exp(V_ik)",
        "",
        "## Utility / Preference Parameters By Group",
        "",
        "Utility uses Box-Cox consumption and leisure. This table gives the",
        "group-level consumption and leisure parameters resolved from the",
        "estimated parameter vector.",
        "",
        _md_table(
            ["group", "beta_c", "theta_c", "beta_l0", "beta_l_shifters", "theta_l", "beta_cl"],
            utility_rows,
        ) if utility_rows else "_No group-level preference parameters resolved._\n",
        "## Specification Block Inventory",
        "",
        _md_table(
            ["yaml_block", "label", "n_shifters", "variables", "coefficients"],
            spec_inventory_rows,
        ) if spec_inventory_rows else "_Spec YAML not loaded._\n",
        "## Opportunity Equations — Symbolic",
        "",
        "```text",
        "\n".join(
            _md_clean(line) if str(line).strip() else ""
            for line in symbolic_equations_lines
        ).rstrip(),
        "```",
        "" if symbolic_equations_lines else "_Spec YAML not loaded; symbolic equations omitted._",
        "## Opportunity Equations — Numerical (estimated coefficients bound)",
        "",
        _md_table(
            ["block", "term", "coefficient", "source_group", "value"],
            numerical_eq_rows,
        ) if numerical_eq_rows else "_Spec YAML not loaded; numerical equations omitted._\n",
        "## Per-Block Parameter Counts and Significance",
        "",
        _md_table(
            ["block", "n_params", "n_estimable", "n_sig_p<0.001", "n_sig_p<0.01", "n_sig_p<0.05", "n_sig_p<0.10"],
            block_count_rows,
        ) if block_count_rows else "_No estimated parameters classified._\n",
        "## Convergence By Result Block",
        "",
        _md_table(
            ["group", "success", "message", "iterations", "n_function_evaluations", "gradient_norm", "log_likelihood", "walltime_seconds"],
            group_rows,
        ),
        _bundle_solver_md_block,
        _bundle_fit_split_md_block,
        _bundle_param_table_md_block,
        _bundle_identification_md_block,
        _bundle_probability_md_block,
        "## Fit Statistics (legacy combined table — kept for backward compatibility)",
        "",
        _md_table(["metric", "value"], fit_rows),
        "## Fit Moments",
        "",
        _md_table(
            ["group", "participation_observed", "participation_predicted", "mean_hours_observed", "mean_hours_predicted"],
            _fit_moment_rows(fit_results),
        ),
        "## Observed Hours Quantiles (chosen working alts)",
        "",
        _md_table(
            ["group", "n", "q10", "q25", "q50", "q75", "q90"],
            hours_quantile_rows,
        ) if hours_quantile_rows else "_Observed hours quantiles unavailable._\n",
        "## Distribution Fit Summary (observed vs predicted hours bins)",
        "",
        _md_table(
            ["group", "dimension", "n_bins", "L1_distance", "L2_distance"],
            distribution_fit_rows,
        ) if distribution_fit_rows else "_Distribution fit summary unavailable._\n",
        "## Observed vs Implied Log-Wage σ (chosen working alts)",
        "",
        _md_table(
            ["group", "n", "observed_mean_log_wage", "observed_std_log_wage", "implied_sigma"],
            observed_log_wage_rows_list,
        ) if observed_log_wage_rows_list else "_Observed wage stats unavailable._\n",
        "## Structural Elasticity Heuristics",
        "",
        "These are curvature-based heuristics from the post-estimation script, not",
        "policy-counterfactual elasticities.",
        "",
        _md_table(
            list(elasticities_df.columns),
            elasticities_df.values.tolist(),
        ) if elasticities_df is not None and len(elasticities_df) else "_None._\n",
        "## Marginal Utility Diagnostics",
        "",
        _md_table(
            ["Group", "beta_c", "theta_c", "MUC Positive?", "MUC Diminishing?", "Well-Behaved?", "MUC at Median C", "C where MUC=1", "Notes"],
            [
                [
                    row.get("Group"),
                    _muc_beta_theta_values(row)[0],
                    _muc_beta_theta_values(row)[1],
                    row.get("MUC Positive?"),
                    row.get("MUC Diminishing?"),
                    row.get("Well-Behaved?"),
                    row.get("MUC at Median C"),
                    row.get("C where MUC=1"),
                    row.get("Notes"),
                ]
                for row in (muc_analysis or [])
            ],
        ),
        "## Marginal Utility Distribution Summary",
        "",
        _md_table(
            ["group", "N", "n_neg_muc", "pct_neg_muc", "mean_muc", "n_neg_mul", "pct_neg_mul", "mean_mul"],
            mu_distribution_rows,
        ) if mu_distribution_rows else "_Marginal utility arrays not available._\n",
        "## Probability Diagnostics",
        "",
        _md_table(["metric", "value"], probability_rows),
        "## Worst-Fit Households",
        "",
        _md_table(["rank", "idhh", "group", "p_chosen", "ll_i"], worst_rows),
        "## Identification Diagnostics",
        "",
        _md_table(["metric", "value"], hessian_rows),
        f"_Interpretation: {_md_clean(hessian_interp)}._\n" if hessian_interp else "",
        "## Initial → Final Movement (top 15 by |Δ|)",
        "",
        _md_table(
            ["block", "parameter", "initial_value", "final_estimate", "delta"],
            mover_rows,
        ) if mover_rows else "_No initial values available._\n",
        "## Top High-Correlation Parameter Pairs",
        "",
        _md_table(["param_i", "param_j", "correlation"], top_corr_rows),
        "## Weakest Eigenvector Diagnostics",
        "",
        _md_table(["rank", "eigenvalue", "top_loadings"], eig_rows),
        "## Parameters At Bounds",
        "",
        _md_table(["parameter", "estimate", "bound", "side"], bound_rows),
        "## Parameters Near Bounds (within 5% of bound width)",
        "",
        _md_table(
            ["block", "parameter", "estimate", "lower_bound", "upper_bound", "flags"],
            bound_proximity_rows,
        ) if bound_proximity_rows else "_No parameters within 5% of a bound._\n",
        "## Top Significant Coefficients (top 15 by |t|)",
        "",
        _md_table(
            ["block", "parameter", "estimate", "std_error", "t_value", "p_value"],
            top_significant_rows,
        ) if top_significant_rows else "_No t-values available._\n",
        "## Parameter Estimates By Block",
        "",
        _md_table(
            ["block", "parameter", "estimate", "std_error", "t_value", "p_value", "lower_bound", "upper_bound", "initial_value"],
            param_rows,
        ),
        "## Hours Distribution Shares",
        "",
        _md_table(
            ["group", "hours_bin", "observed_share", "predicted_share"],
            _hours_distribution_rows(fit_results),
        ),
        "## Wage Distribution Summary",
        "",
        "Observed values use chosen working alternatives. Predicted values use",
        "choice-probability weights over working alternatives.",
        "",
        _md_table(
            ["group", "n_observed_working", "predicted_worker_weight", "obs_mean", "pred_mean", "obs_q10", "obs_q50", "obs_q90", "pred_q10", "pred_q50", "pred_q90"],
            wage_distribution_rows,
        ) if wage_distribution_rows else "_No wage columns available for this run._\n",
        "## Occupation Distribution Shares",
        "",
        "Observed shares use chosen working alternatives. Predicted shares use",
        "choice-probability weights over working alternatives. Category labels",
        "are reported for loc4-style variables when available.",
        "",
        _md_table(
            ["group", "occupation_column", "category", "label", "observed_share", "predicted_share", "observed_count", "predicted_weight"],
            occupation_share_rows,
        ) if occupation_share_rows else "_No loc4-style occupation columns available for this run._\n",
        "## Notes For Use",
        "",
        "- This Markdown file is the preferred low-token artifact for LLM review.",
        "- Use the HTML report only when plots or visual diagnostics are needed.",
        "- Generated output folders remain local unless explicitly added to Git.",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")
    LOGGER.info(f"   Low-token Markdown summary: {output_path}")
    return output_path


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
    llm_summary_dir: Optional[Path] = Path("reports"),
    report_title: Optional[str] = None,
    report_profile: str = DEFAULT_PROFILE,
    cluster_se_path: Optional[Path] = None,
    solver_log_path: Optional[Path] = None,
    listing_file_path: Optional[Path] = None,
    gradient_diag_inputs: Optional[Dict[str, Any]] = None,
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
    llm_summary_dir : Path, optional
        Directory for compact Markdown summaries. If None, skip this artifact.
    report_title : str, optional
        Custom title for the HTML report header. Defaults to spec-derived title.

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

    def _first_non_null(*values):
        for value in values:
            if value is not None:
                return value
        return None

    # Load estimation results
    LOGGER.info("\n1. Loading estimation results...")    # Try enhanced format first, then legacy
    try:
        parsed, data = load_estimation_results_from_json(results_json_path)
    except (KeyError, TypeError):
        LOGGER.info("  Trying legacy JSON format...")
        parsed, data = load_estimation_results_legacy(results_json_path)
    
    LOGGER.info(f"   Found {len(parsed.groups)} groups: {parsed.groups}")
    LOGGER.info(f"   Preference groups: {parsed.preference_groups}")

    spec = None
    if spec_config is not None:
        try:
            spec = parse_specification(spec_config)
            LOGGER.info(f"   Loaded specification for diagnostics: {spec.name}")
        except Exception as e:
            LOGGER.warning(f"   Failed to parse spec config ({spec_config}): {e}")

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
    n_iterations = None
    if 'summary' in data:
        estimation_time = data['summary'].get('total_walltime_seconds')
        n_iterations = data['summary'].get('n_iterations')
    elif 'estimation_time_seconds' in data:
        estimation_time = data['estimation_time_seconds']

    # Fallback: Try to extract from results groups
    if n_iterations is None and 'results' in data:
        for group_data in data['results'].values():
            if 'n_iterations' in group_data:
                n_iterations = group_data['n_iterations']
                break

    # Build run metadata for report header (model-aware context)
    summary_data = data.get('summary', {}) if isinstance(data.get('summary'), dict) else {}
    result_groups = data.get('results', {}) if isinstance(data.get('results'), dict) else {}
    first_group_data = next(iter(result_groups.values()), {}) if result_groups else {}
    metadata_data = data.get('metadata', {}) if isinstance(data.get('metadata'), dict) else {}

    prior_correction_applied = _first_non_null(
        summary_data.get('prior_correction_applied'),
        data.get('prior_correction_applied'),
        first_group_data.get('prior_correction_applied'),
    )
    prior_correction_form = _first_non_null(
        summary_data.get('prior_correction_form'),
        data.get('prior_correction_form'),
        first_group_data.get('prior_correction_form'),
    )
    market_centering_applied = _first_non_null(
        summary_data.get('market_centering_applied'),
        data.get('market_centering_applied'),
        first_group_data.get('market_centering_applied'),
    )

    # Fallback: infer proposal correction metadata from MNL sidecar when absent.
    if (
        prior_correction_applied is None or prior_correction_form is None
    ) and mnl_base is not None:
        try:
            mnl_meta_path = Path(str(mnl_base) + "__mnlmeta.json")
            if mnl_meta_path.exists():
                with open(mnl_meta_path, 'r') as f:
                    mnl_meta = json.load(f)
                prior_meta = mnl_meta.get('prior_parameters', {})
                eff_single = prior_meta.get('effective_prior_source_singles')
                eff_couples = prior_meta.get('effective_prior_source_couples')
                if prior_correction_applied is None and (eff_single or eff_couples):
                    prior_correction_applied = True
                if prior_correction_form is None and (eff_single or eff_couples):
                    prior_correction_form = "-log(prior)"
        except Exception:
            # Keep report generation resilient if metadata sidecar is missing or malformed.
            pass

    if market_centering_applied is None and spec is not None:
        market_centering_applied = bool(
            getattr(spec, 'market_opportunity_center_within_choice_set', False)
        )

    run_metadata = {
        'spec_name': _first_non_null(
            getattr(spec, 'name', None),
            data.get('specification'),
        ),
        'spec_config_path': _first_non_null(
            str(spec_config) if spec_config is not None else None,
            metadata_data.get('spec_config'),
        ),
        'model_family': _first_non_null(
            getattr(spec, 'model_family', None),
            summary_data.get('model_family'),
            first_group_data.get('model_family'),
        ),
        'market_opportunity_tier': _first_non_null(
            getattr(spec, 'market_opportunity_tier', None),
            summary_data.get('market_opportunity_tier'),
            first_group_data.get('market_opportunity_tier'),
        ),
        'prior_correction_applied': (
            bool(prior_correction_applied)
            if prior_correction_applied is not None else None
        ),
        'prior_correction_form': prior_correction_form,
        'market_centering_applied': (
            bool(market_centering_applied)
            if market_centering_applied is not None else None
        ),
    }

    id_diag_path = results_json_path.parent / "identification_diagnostics.txt"
    if id_diag_path.exists():
        try:
            run_metadata['identification_diagnostics_text'] = id_diag_path.read_text(
                encoding='utf-8',
                errors='replace',
            )
            run_metadata['identification_diagnostics_path'] = str(id_diag_path)
        except Exception as e:
            LOGGER.warning(f"Could not read identification diagnostics file: {e}")

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
    elasticities_df = compute_structural_elasticities(parsed, spec=spec)

    # MUC behavior analysis
    LOGGER.info("\n3. Analyzing MUC behavior...")
    muc_analysis = analyze_muc_behavior(parsed, spec=spec)

    # Compute fit diagnostics from data
    LOGGER.info("\n4. Computing fit diagnostics from MNL data...")
    fit_results = {}
    mu_results = {}
    ll_null_uniform = None
    ll_null_prior_corrected = None
    n_obs_long = None
    n_individuals = None
    
    if mnl_base is not None:
        try:
            fit_results = compute_fit_diagnostics_from_data(parsed, mnl_base, spec=spec)
            mu_results = compute_marginal_utilities_at_chosen(parsed, mnl_base)
            
            # Compute LL0 diagnostics if not in JSON
            if 'll_null' not in fit_stats or fit_stats['ll_null'] is None:
                try:
                    singles_path = Path(str(mnl_base) + '__singles.parquet')
                    if singles_path.exists():
                        df_temp = pd.read_parquet(singles_path)
                        ll_null_uniform = compute_null_log_likelihood(df_temp, 'idhh')
                        ll_null_prior_corrected = compute_null_log_likelihood_prior_corrected(df_temp, 'idhh')
                        n_obs_long = len(df_temp)
                        n_individuals = df_temp['idhh'].nunique()
                        
                        couples_path = Path(str(mnl_base) + '__couples.parquet')
                        if couples_path.exists():
                            df_temp_c = pd.read_parquet(couples_path)
                            ll_null_uniform += compute_null_log_likelihood(df_temp_c, 'idhh')
                            ll0p_c = compute_null_log_likelihood_prior_corrected(df_temp_c, 'idhh')
                            if ll_null_prior_corrected is None:
                                ll_null_prior_corrected = ll0p_c
                            elif ll0p_c is not None:
                                ll_null_prior_corrected += ll0p_c
                            n_obs_long += len(df_temp_c)
                            n_individuals += df_temp_c['idhh'].nunique()

                        # Keep legacy keys and expose both null variants.
                        fit_stats['ll_null'] = ll_null_uniform
                        fit_stats['ll_null_uniform'] = ll_null_uniform
                        fit_stats['ll_null_prior_corrected'] = ll_null_prior_corrected
                        fit_stats['n_obs_long'] = n_obs_long
                        LOGGER.info(f"  Computed LL0 (uniform) = {ll_null_uniform:.2f}")
                        if ll_null_prior_corrected is not None:
                            LOGGER.info(f"  Computed LL0 (prior-corrected) = {ll_null_prior_corrected:.2f}")
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
    ll_null_uniform_val = fit_stats.get('ll_null_uniform')
    ll_null_prior_val = fit_stats.get('ll_null_prior_corrected')
    n_params = fit_stats.get('n_parameters', 0)
    n_obs = fit_stats.get('n_observations', 0)

    # Uniform null metrics (legacy McFadden rho²)
    if ll_null_uniform_val is not None and ll_null_uniform_val != 0:
        fit_stats['rho_squared_uniform'] = 1 - (ll / ll_null_uniform_val)
        fit_stats['rho_squared_adj_uniform'] = 1 - ((ll - n_params) / ll_null_uniform_val)
    else:
        fit_stats['rho_squared_uniform'] = None
        fit_stats['rho_squared_adj_uniform'] = None

    # Prior-corrected null metrics (recommended for sampled-alternative/job-choice runs)
    if ll_null_prior_val is not None and ll_null_prior_val != 0:
        fit_stats['rho_squared_prior_corrected'] = 1 - (ll / ll_null_prior_val)
        fit_stats['rho_squared_adj_prior_corrected'] = 1 - ((ll - n_params) / ll_null_prior_val)
    else:
        fit_stats['rho_squared_prior_corrected'] = None
        fit_stats['rho_squared_adj_prior_corrected'] = None

    # Backward-compatible headline rho²:
    # use prior-corrected when available; otherwise fall back to legacy uniform.
    if fit_stats['rho_squared_prior_corrected'] is not None:
        fit_stats['rho_squared'] = fit_stats['rho_squared_prior_corrected']
        fit_stats['rho_squared_adj'] = fit_stats['rho_squared_adj_prior_corrected']
        LOGGER.info(f"  Rho-squared (prior-corrected): {fit_stats['rho_squared']:.4f}")
        LOGGER.info(f"  Adjusted Rho-squared (prior-corrected): {fit_stats['rho_squared_adj']:.4f}")
    elif ll_null_val is not None and ll_null_val != 0:
        fit_stats['rho_squared'] = 1 - (ll / ll_null_val)
        fit_stats['rho_squared_adj'] = 1 - ((ll - n_params) / ll_null_val)
        LOGGER.info(f"  Rho-squared (uniform): {fit_stats['rho_squared']:.4f}")
        LOGGER.info(f"  Adjusted Rho-squared (uniform): {fit_stats['rho_squared_adj']:.4f}")
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
            prob_diagnostics = compute_probability_diagnostics(parsed, mnl_base, spec=spec)
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

    # NEW: Hours and Wage distribution comparisons
    if mnl_base is not None:
        LOGGER.info("  Generating hours distribution plots...")
        plot_paths.update(plot_hours_distribution_comparison(parsed, mnl_base, output_dir, prefix, spec=spec))
        LOGGER.info("  Generating wage distribution plots...")
        plot_paths.update(plot_wage_distribution_comparison(parsed, mnl_base, output_dir, prefix, spec=spec))
        LOGGER.info("  Generating job distribution plots...")
        plot_paths.update(plot_job_distribution_comparison(parsed, mnl_base, output_dir, prefix, spec=spec))
        LOGGER.info("  Generating LOC distribution plots...")
        plot_paths.update(plot_loc_distribution_comparison(parsed, mnl_base, output_dir, prefix, spec=spec))

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

    # Build the diagnostics bundle BEFORE rendering HTML so the HTML can
    # render the four reorganized fit-statistics sections (A/B/C/D) and the
    # Phase-2 bundle-driven sections (parameter table by block, identification,
    # solver, probability-fit) from the shared bundle. Solver-log / cluster-SE
    # / gradient artifacts are supplied later by run_extended_diagnostics,
    # which rebuilds the bundle with those inputs and rewrites the JSON.
    diagnostics_bundle = None
    # Build YAML-driven block map (specification-agnostic; falls back to
    # name heuristics inside the bundle when this map is empty).
    _spec_blocks_for_bundle = (run_metadata or {}).get("spec_blocks") or {}
    if not _spec_blocks_for_bundle:
        _spec_path_for_bundle = (run_metadata or {}).get("spec_config_path")
        try:
            _spec_blocks_for_bundle = _load_yaml_spec_blocks(_spec_path_for_bundle) or {}
        except Exception:
            _spec_blocks_for_bundle = {}
    try:
        _block_map_for_bundle = _coef_to_block_map(_spec_blocks_for_bundle) if _spec_blocks_for_bundle else {}
    except Exception:
        _block_map_for_bundle = {}

    # Pre-load extended inputs (cluster SE / solver log / listing) so the
    # styled HTML render can use the enriched bundle directly. These same
    # inputs are also consumed by run_extended_diagnostics for its
    # extended_diagnostics.md / .json artifacts.
    _pre_cluster_se_data: Optional[Dict[str, Any]] = None
    if cluster_se_path is not None:
        try:
            _pre_cluster_se_data = _load_cluster_se_json(cluster_se_path)
            LOGGER.info(f"   pre-loaded cluster SE JSON for HTML bundle: {cluster_se_path}")
        except Exception as _e:
            LOGGER.warning(f"   Could not pre-load cluster SE JSON: {_e}")
    _pre_solver_diag: Optional[Dict[str, Any]] = None
    if (solver_log_path is not None) or (listing_file_path is not None):
        try:
            _pre_solver_diag = _extract_solver_convergence_diagnostics(
                data,
                solver_log_path=solver_log_path,
                listing_file_path=listing_file_path,
            )
            LOGGER.info("   pre-built solver convergence diagnostics for HTML bundle")
        except Exception as _e:
            LOGGER.warning(f"   Could not pre-build solver diagnostics: {_e}")

    if HAS_DIAGNOSTICS_BUNDLE:
        try:
            diagnostics_bundle = build_diagnostics_bundle(
                profile=report_profile,
                results_data=data,
                parsed_params=parsed,
                fit_stats=fit_stats,
                bound_diagnostics=bound_diagnostics,
                mu_results=mu_results,
                prob_diagnostics=prob_diagnostics,
                hessian_diagnostics=hessian_diagnostics,
                cluster_se_data=_pre_cluster_se_data,
                solver_diag=_pre_solver_diag,
                gradient_diag=gradient_diag_inputs,
                repro_meta=None,
                run_metadata=run_metadata,
                block_map=_block_map_for_bundle,
            )
        except Exception as e:
            LOGGER.warning(f"Diagnostics bundle build failed (pre-HTML): {e}", exc_info=True)
            diagnostics_bundle = None

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
        n_iterations=n_iterations,
        prob_diagnostics=prob_diagnostics,
        bound_diagnostics=bound_diagnostics,
        hessian_diagnostics=hessian_diagnostics,
        estimation_results_path=results_json_path,
        run_metadata=run_metadata,
        diagnostics_bundle=diagnostics_bundle,
        report_profile=report_profile,
    )

    # Save CSV outputs
    LOGGER.info("\n7. Saving CSV outputs...")

    param_csv = output_dir / f'{prefix}params.csv'
    parsed.to_dataframe().to_csv(param_csv, index=False)
    LOGGER.info(f"   Parameters: {param_csv}")

    elast_csv = output_dir / f'{prefix}elasticities.csv'
    elasticities_df.to_csv(elast_csv, index=False)
    LOGGER.info(f"   Elasticities: {elast_csv}")

    llm_summary_path = None
    if llm_summary_dir is not None:
        safe_prefix = prefix or ""
        llm_summary_path = (
            Path(llm_summary_dir)
            / f"{safe_prefix}llm_summary_{report_timestamp}.md"
        )
        generate_llm_markdown_summary(
            parsed_params=parsed,
            data=data,
            fit_stats=fit_stats,
            fit_results=fit_results,
            elasticities_df=elasticities_df,
            muc_analysis=muc_analysis,
            prob_diagnostics=prob_diagnostics,
            bound_diagnostics=bound_diagnostics,
            hessian_diagnostics=hessian_diagnostics,
            run_metadata=run_metadata,
            output_path=llm_summary_path,
            estimation_results_path=results_json_path,
            html_report_path=html_path,
            param_csv_path=param_csv,
            elasticities_csv_path=elast_csv,
            post_output_dir=output_dir,
            mnl_base=mnl_base,
            spec_config=spec_config,
            mu_results=mu_results,
            spec=spec,
            diagnostics_bundle=diagnostics_bundle,
            report_profile=report_profile,
        )

    LOGGER.info("\n" + "=" * 70)
    LOGGER.info("POST-ESTIMATION COMPLETE")
    LOGGER.info("=" * 70)
    LOGGER.info(f"  HTML Report: {html_path}")
    if llm_summary_path is not None:
        LOGGER.info(f"  Low-token Summary: {llm_summary_path}")
    LOGGER.info(f"  Total Time: {post_estimation_time:.1f}s")

    # ------------------------------------------------------------------
    # Diagnostics bundle: write canonical artifact files. The bundle was
    # built above (before HTML render); here we serialize it. Solver-log /
    # cluster-SE / gradient artifacts are added later from
    # run_extended_diagnostics, which rewrites the JSON if those inputs
    # are supplied in the same invocation.
    # ------------------------------------------------------------------
    bundle_paths: Dict[str, Path] = {}
    if HAS_DIAGNOSTICS_BUNDLE and diagnostics_bundle is not None:
        try:
            bundle_paths = write_bundle_artifacts(diagnostics_bundle, output_dir, prefix=prefix)
            for label, p in bundle_paths.items():
                LOGGER.info(f"   {label}: {p}")
        except Exception as e:
            LOGGER.warning(f"Diagnostics bundle write failed: {e}", exc_info=True)

    return {
        'parsed_params': parsed,
        'fit_stats': fit_stats,
        'elasticities': elasticities_df,
        'muc_analysis': muc_analysis,
        'html_report': html_path,
        'param_csv': param_csv,
        'elasticities_csv': elast_csv,
        'llm_summary': llm_summary_path,
        'plot_paths': plot_paths,
        'prob_diagnostics': prob_diagnostics,
        'bound_diagnostics': bound_diagnostics,
        'report_profile': report_profile,
        'diagnostics_bundle_json': bundle_paths.get("diagnostics_bundle"),
        'enhanced_parameter_table_csv': bundle_paths.get("enhanced_parameter_table"),
        'solver_diagnostics_json': bundle_paths.get("solver_diagnostics"),
        'inference_diagnostics_json': bundle_paths.get("inference_diagnostics"),
    }


# =============================================================================
# EXTENDED DIAGNOSTICS — general-purpose inference & convergence reporting
# =============================================================================

_DIAG_NA = "Not available in supplied solver artifacts"


def _load_cluster_se_json(path: Path) -> Dict[str, Any]:
    """Load and return a cluster-robust SE JSON artifact. Raises on failure."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _parse_listing_file(listing_path: Path) -> Dict[str, Any]:
    """Parse a GAMS .lst listing file for solver/CONOPT diagnostics.

    All fields are optional; missing ones are omitted from the returned dict.
    """
    out: Dict[str, Any] = {}

    if not listing_path.exists():
        out["_parse_error"] = f"Listing file not found: {listing_path}"
        return out

    try:
        text = listing_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        out["_parse_error"] = str(exc)
        return out

    lines = text.splitlines()

    # Solver / model status lines
    for line in lines:
        ls = line.strip()
        if re.search(r"SOLVER STATUS|Solver Status", ls, re.IGNORECASE):
            m = re.search(r"(\d+)\s+(.+)$", ls)
            if m:
                out["solver_status"] = m.group(2).strip()
        elif re.search(r"MODEL STATUS|Model Status", ls, re.IGNORECASE):
            m = re.search(r"(\d+)\s+(.+)$", ls)
            if m:
                out["model_status"] = m.group(2).strip()

    # Model statistics block: equations, variables, nonzeros
    for line in lines:
        ls = line.strip()
        m = re.match(r"Equations\s+(\d+)", ls, re.IGNORECASE)
        if m:
            out["equations"] = int(m.group(1))
        m = re.match(r"Variables\s+(\d+)", ls, re.IGNORECASE)
        if m:
            out["variables"] = int(m.group(1))
        m = re.match(r"Non(?:zeros?|linear elements?)\s+(\d+)", ls, re.IGNORECASE)
        if m:
            out["nonzeros"] = int(m.group(1))

    # Resource / solve time
    for line in lines:
        ls = line.strip()
        m = re.match(r"Resource\s+usage.*?([\d.]+)", ls, re.IGNORECASE)
        if m:
            try:
                out["solve_time_s"] = float(m.group(1))
            except ValueError:
                pass
        m = re.match(r"Generation\s+time\s+([\d.]+)", ls, re.IGNORECASE)
        if m:
            try:
                out["generation_time_s"] = float(m.group(1))
            except ValueError:
                pass

    # Max infeasibility
    for line in lines:
        m = re.search(r"[Mm]ax(?:imum)?\s+infeasib[a-z]*\s*[=:\s]*([\d.eE+\-]+)", line)
        if m:
            try:
                out["max_infeasibility"] = float(m.group(1))
            except ValueError:
                pass

    # CONOPT RGmax (reduced gradient norm, solver-internal)
    for line in lines:
        m = re.search(r"RGmax\s*[=:]\s*([\d.eE+\-]+)", line, re.IGNORECASE)
        if m:
            try:
                out["rgmax"] = float(m.group(1))
                break
            except ValueError:
                pass
    if "rgmax" not in out:
        for line in lines:
            m = re.search(r"Reduced gradient\s+norm\s*[=:]\s*([\d.eE+\-]+)", line, re.IGNORECASE)
            if m:
                try:
                    out["rgmax"] = float(m.group(1))
                    break
                except ValueError:
                    pass

    # CONOPT iteration-log RGmax (terminal value from tabular iteration log).
    # The CONOPT iteration log uses a fixed-column tabular format that the
    # explicit "RGmax = value" / "Reduced gradient norm = value" patterns
    # above do not capture. Fall back to the bundle helper for that format.
    if "rgmax" not in out and HAS_DIAGNOSTICS_BUNDLE:
        try:
            from diagnostics_bundle import (
                parse_conopt_rgmax_from_text,
                parse_conopt_termination_text,
            )
            rgmax_val = parse_conopt_rgmax_from_text(text)
            if rgmax_val is not None:
                out["rgmax"] = rgmax_val
            term = parse_conopt_termination_text(text)
            if term and "termination_text" not in out:
                out["termination_text"] = term
        except Exception as _e:
            LOGGER.debug(f"CONOPT iteration-log parse failed in listing parser: {_e}")

    # CONOPT tolerances
    for line in lines:
        m = re.search(r"\bRTOL\b\s*[=:]\s*([\d.eE+\-]+)", line, re.IGNORECASE)
        if m:
            try:
                out["conopt_rtol"] = float(m.group(1))
            except ValueError:
                pass
        m = re.search(r"\bFTOL\b\s*[=:]\s*([\d.eE+\-]+)", line, re.IGNORECASE)
        if m:
            try:
                out["conopt_ftol"] = float(m.group(1))
            except ValueError:
                pass

    if "rgmax" in out and "conopt_rtol" in out:
        out["rgmax_below_tol"] = out["rgmax"] <= out["conopt_rtol"]

    # Active bounds
    active_bound_count = sum(
        1 for line in lines
        if re.search(r"(active|binding)\s+(lower|upper)\s+bound", line, re.IGNORECASE)
    )
    if active_bound_count:
        out["active_bounds"] = active_bound_count

    # Solver warnings (*** WARNING lines)
    warnings_found = [
        line.strip() for line in lines
        if re.search(r"^\*\*\*\s*warning", line.strip(), re.IGNORECASE)
    ]
    if warnings_found:
        out["solver_warnings"] = warnings_found[:10]

    # Solver name from header
    for line in lines[:30]:
        m = re.search(r"Using\s+solver\s+([A-Za-z0-9_]+)", line, re.IGNORECASE)
        if m:
            out["gams_solver"] = m.group(1).upper()
            break
        m = re.search(r"Solver\s*:\s*([A-Za-z0-9_]+)", line, re.IGNORECASE)
        if m:
            out.setdefault("gams_solver", m.group(1).upper())

    return out


def _parse_solver_log_file(log_path: Path) -> Dict[str, Any]:
    """Parse a plain-text solver log for convergence information. Degrades gracefully."""
    out: Dict[str, Any] = {}

    if not log_path.exists():
        out["_parse_error"] = f"Solver log not found: {log_path}"
        return out

    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        out["_parse_error"] = str(exc)
        return out

    lines = text.splitlines()

    for line in lines:
        m = re.search(r"objective\s*[=:]\s*([\-\d.eE+]+)", line, re.IGNORECASE)
        if m:
            try:
                out["log_objective"] = float(m.group(1))
            except ValueError:
                pass
        m = re.search(r"iterations?\s*[=:]\s*(\d+)", line, re.IGNORECASE)
        if m:
            try:
                out.setdefault("log_iterations", int(m.group(1)))
            except ValueError:
                pass

    meaningful = [l.strip() for l in lines if l.strip() and not l.startswith("#")]
    if meaningful:
        out["log_last_lines"] = meaningful[-3:]

    # CONOPT iteration-log RGmax (terminal reduced-gradient norm).
    # Uses the diagnostics_bundle helper to handle the tabular CONOPT format.
    if HAS_DIAGNOSTICS_BUNDLE:
        try:
            from diagnostics_bundle import (
                parse_conopt_rgmax_from_text,
                parse_conopt_termination_text,
            )
            rgmax_val = parse_conopt_rgmax_from_text(text)
            if rgmax_val is not None and "rgmax" not in out:
                out["rgmax"] = rgmax_val
            term = parse_conopt_termination_text(text)
            if term and "termination_text" not in out:
                out["termination_text"] = term
        except Exception as _e:
            LOGGER.debug(f"CONOPT iteration-log parse failed: {_e}")

    return out


def _extract_solver_convergence_diagnostics(
    results_data: Dict[str, Any],
    solver_log_path: Optional[Path] = None,
    listing_file_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Combine results JSON metadata + optional GAMS artifacts into a diagnostics dict.

    Missing values use the sentinel _DIAG_NA so callers can test for absence.
    """
    out: Dict[str, Any] = {}
    metadata = results_data.get("metadata", {}) or {}
    out["gamspy_version"] = metadata.get("gamspy_version", _DIAG_NA)
    out["solver"] = metadata.get("solver", _DIAG_NA)

    groups_info = []
    for grp_name, grp_data in (results_data.get("results", {}) or {}).items():
        if not isinstance(grp_data, dict):
            continue
        info: Dict[str, Any] = {"group": grp_name}
        info["final_ll"] = grp_data.get("final_ll", _DIAG_NA)
        info["n_iterations"] = grp_data.get("n_iterations", _DIAG_NA)
        info["n_function_evals"] = grp_data.get("n_function_evals", _DIAG_NA)
        info["walltime_s"] = grp_data.get("walltime_seconds", _DIAG_NA)
        info["success"] = grp_data.get("success", _DIAG_NA)
        msg = grp_data.get("message", _DIAG_NA)
        info["message"] = msg
        if isinstance(msg, str):
            m = re.search(r"SolveStatus[.:\s]+([A-Za-z]+)", msg)
            if m:
                info["solve_status_parsed"] = m.group(1)
            m = re.search(r"ModelStatus[.:\s]+([A-Za-z]+)", msg)
            if m:
                info["model_status_parsed"] = m.group(1)
        groups_info.append(info)
    out["groups"] = groups_info

    out["listing_diagnostics"] = (
        _parse_listing_file(listing_file_path)
        if listing_file_path is not None
        else {"_note": _DIAG_NA}
    )
    out["solver_log_diagnostics"] = (
        _parse_solver_log_file(solver_log_path)
        if solver_log_path is not None
        else {"_note": _DIAG_NA}
    )
    return out


def _compute_gradient_diagnostics(
    results_json_path: Path,
    mnl_base: Optional[Path],
    spec_config: Optional[Path],
) -> Dict[str, Any]:
    """Compute the Python likelihood gradient (score vector) at the converged theta.

    This is the RURO Python-side gradient of log L, computed via central-difference
    numerical differentiation.  It is DISTINCT from CONOPT RGmax (solver-internal
    reduced gradient).  Both should be near zero at a local optimum but are produced
    by entirely different computations.

    Returns available=False with a descriptive note when data/spec are unavailable.
    """
    result: Dict[str, Any] = {
        "available": False,
        "note": _DIAG_NA,
        "distinction_note": (
            "Python likelihood gradient (score at convergence) — "
            "computed by the RURO Python engine via central-difference numerical "
            "differentiation of the log-likelihood function.  "
            "DISTINCT from CONOPT RGmax / reduced gradient, "
            "which is an internal solver quantity produced by GAMS/CONOPT."
        ),
    }

    if mnl_base is None or spec_config is None:
        result["note"] = (
            "Gradient computation requires --mnl-base and --spec-config. "
            "Both must be supplied and point to accessible files."
        )
        return result

    try:
        import sys as _sys
        _script_dir = Path(__file__).parent
        if str(_script_dir) not in _sys.path:
            _sys.path.insert(0, str(_script_dir))

        from estimation_engine import compute_gradient_joint  # type: ignore
        from estimation_spec_parser import load_spec           # type: ignore
        from estimation_utils import precompute_mnl_arrays     # type: ignore

        spec = load_spec(spec_config)

        base = str(mnl_base)
        singles_path = Path(base + "__singles.parquet")
        couples_path = Path(base + "__couples.parquet")

        if not singles_path.exists() or not couples_path.exists():
            result["note"] = (
                f"MNL data files not found at {base}__singles.parquet / "
                f"{base}__couples.parquet — cannot compute gradient."
            )
            return result

        df_singles = pd.read_parquet(singles_path)
        df_couples = pd.read_parquet(couples_path)
        data_sm, data_sf, data_cou = precompute_mnl_arrays(df_singles, df_couples, spec)

        with open(results_json_path, "r", encoding="utf-8") as fh:
            res_data = json.load(fh)

        theta = None
        param_names: List[str] = []
        for grp_data in (res_data.get("results", {}) or {}).values():
            if isinstance(grp_data, dict) and "parameters" in grp_data:
                params = grp_data["parameters"]
                if isinstance(params, dict) and params:
                    param_names = list(params.keys())
                    theta = np.array(list(params.values()), dtype=float)
                    break

        if theta is None:
            result["note"] = "Could not extract converged parameter vector from results JSON."
            return result

        grad = np.asarray(
            compute_gradient_joint(theta, data_sm, data_sf, data_cou, spec), dtype=float
        )
        max_abs_idx = int(np.argmax(np.abs(grad)))
        top10_idx = np.argsort(np.abs(grad))[-10:][::-1]

        result.update({
            "available": True,
            "note": "Computed successfully via central-difference numerical differentiation.",
            "gradient_norm_l2": float(np.linalg.norm(grad)),
            "gradient_norm_inf": float(np.max(np.abs(grad))),
            "max_abs_param": param_names[max_abs_idx] if param_names else None,
            "n_params": len(grad),
            "top10_by_magnitude": {
                (param_names[i] if i < len(param_names) else f"param_{i}"): float(grad[i])
                for i in top10_idx
            },
        })
    except ImportError as exc:
        result["note"] = f"estimation_engine not importable ({exc}); gradient unavailable."
    except Exception as exc:
        result["note"] = f"Gradient computation failed: {exc}"

    return result


def _extract_extended_hessian_diagnostics(
    results_data: Dict[str, Any],
    cluster_se_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Extract Hessian / VCV diagnostics, preferring cluster-SE JSON over results JSON."""
    out: Dict[str, Any] = {
        "condition_number": _DIAG_NA,
        "eigenvalue_min": _DIAG_NA,
        "eigenvalue_max": _DIAG_NA,
        "n_free": _DIAG_NA,
        "near_singular_warning": False,
        "source": _DIAG_NA,
    }

    if cluster_se_data is not None:
        art = cluster_se_data.get("cluster_robust_se_artifacts", {}) or {}
        checks = cluster_se_data.get("checks", {}) or {}
        pe6 = checks.get("PE6_true_hessian", {}) or {}

        cond = pe6.get("condition_number")
        if cond is not None:
            out["condition_number"] = float(cond)
            out["near_singular_warning"] = float(cond) > 1e12
            out["source"] = "cluster_robust_se_json (PE6_true_hessian)"

        n_free = art.get("n_free")
        if n_free is not None:
            out["n_free"] = int(n_free)

        hess_shape = pe6.get("hessian_shape_free")
        if hess_shape:
            out["hessian_shape_free"] = hess_shape

        se_h = art.get("se_hessian_vector")
        se_r = art.get("se_robust_vector")
        if se_h is not None:
            arr = np.array(se_h, dtype=float)
            pos = arr[arr > 1e-15]
            if len(pos):
                out["se_hessian_min"] = float(pos.min())
                out["se_hessian_max"] = float(pos.max())
        if se_r is not None:
            arr = np.array(se_r, dtype=float)
            pos = arr[arr > 1e-15]
            if len(pos):
                out["se_robust_min"] = float(pos.min())
                out["se_robust_max"] = float(pos.max())

        t5 = checks.get("T5_robust_vs_hessian")
        if t5:
            out["t5_robust_vs_hessian"] = t5
        return out

    # Fallback: results JSON
    metadata = results_data.get("metadata", {}) or {}
    se_block = metadata.get("standard_errors", {}) or {}
    cond = se_block.get("hessian_condition_number")
    if cond is not None:
        out["condition_number"] = float(cond)
        out["near_singular_warning"] = float(cond) > 1e12
        out["source"] = "estimation_results.json metadata"

    return out


def _build_reproducibility_metadata(
    results_json_path: Path,
    spec_config: Optional[Path],
    mnl_base: Optional[Path],
    output_dir: Optional[Path],
) -> Dict[str, Any]:
    """Assemble reproducibility metadata: git state, Python version, key packages, hashes."""
    import sys as _sys
    import platform
    import hashlib
    import importlib

    out: Dict[str, Any] = {
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "python_version": _sys.version,
        "platform": platform.platform(),
    }
    out["git"] = _git_revision_info()

    pkg_versions: Dict[str, str] = {}
    for pkg in ("numpy", "pandas", "scipy", "gamspy", "pyarrow", "yaml"):
        try:
            mod = importlib.import_module(pkg)
            pkg_versions[pkg] = getattr(mod, "__version__", "unknown")
        except ImportError:
            pkg_versions[pkg] = "not installed"
    out["package_versions"] = pkg_versions

    hashes: Dict[str, str] = {}
    file_targets = [
        ("results_json", results_json_path),
        ("spec_config", spec_config),
        ("mnl_base_singles", Path(str(mnl_base) + "__singles.parquet") if mnl_base else None),
        ("mnl_base_couples", Path(str(mnl_base) + "__couples.parquet") if mnl_base else None),
    ]
    import hashlib as _hl
    for label, path in file_targets:
        if path is not None and Path(path).exists():
            try:
                h = _hl.sha256()
                with open(path, "rb") as fh:
                    for chunk in iter(lambda: fh.read(65536), b""):
                        h.update(chunk)
                hashes[label] = h.hexdigest()[:16]
            except Exception:
                hashes[label] = "hash_error"
        else:
            hashes[label] = "not_available"
    out["file_hashes_sha256_prefix16"] = hashes

    try:
        with open(results_json_path, "r", encoding="utf-8") as fh:
            res_data = json.load(fh)
        meta = res_data.get("metadata", {}) or {}
        for key in ("run_timestamp", "spec_name", "specification", "solver",
                    "gamspy_version", "command_line"):
            if key in meta:
                out[f"results_json_{key}"] = meta[key]
    except Exception:
        pass

    return out


def _build_comparison_diagnostics(
    main_results_path: Path,
    comp_results_path: Path,
    comp_label: str = "Comparison",
    main_cluster_se_path: Optional[Path] = None,
    comp_cluster_se_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Compute L-infinity parameter differences between two estimation runs."""
    out: Dict[str, Any] = {"available": False}

    def _theta_from_cluster_se(se_path: Path) -> Tuple[List[str], Optional[np.ndarray]]:
        with open(se_path, "r", encoding="utf-8") as fh:
            d = json.load(fh)
        art = d.get("cluster_robust_se_artifacts", {}) or {}
        if "converged_theta" in art:
            names = art.get("param_names", [])
            return names, np.array(art["converged_theta"], dtype=float)
        return [], None

    def _theta_from_results(path: Path) -> Tuple[List[str], Optional[np.ndarray]]:
        with open(path, "r", encoding="utf-8") as fh:
            d = json.load(fh)
        for grp_data in (d.get("results", {}) or {}).values():
            if isinstance(grp_data, dict) and "parameters" in grp_data:
                params = grp_data["parameters"]
                if isinstance(params, dict) and params:
                    return list(params.keys()), np.array(list(params.values()), dtype=float)
        return [], None

    def _get_theta(se_path: Optional[Path], res_path: Path) -> Tuple[List[str], Optional[np.ndarray]]:
        if se_path is not None and se_path.exists():
            names, theta = _theta_from_cluster_se(se_path)
            if theta is not None:
                return names, theta
        return _theta_from_results(res_path)

    try:
        main_names, main_theta = _get_theta(main_cluster_se_path, main_results_path)
        comp_names, comp_theta = _get_theta(comp_cluster_se_path, comp_results_path)

        if main_theta is None or comp_theta is None or len(main_theta) == 0 or len(comp_theta) == 0:
            out["note"] = "Could not extract parameter vectors from one or both result files."
            return out

        if len(main_theta) != len(comp_theta):
            out["note"] = (
                f"Parameter vector length mismatch: main={len(main_theta)}, "
                f"comparison={len(comp_theta)}."
            )
            return out

        diff = np.abs(main_theta - comp_theta)
        linf = float(diff.max())
        linf_idx = int(diff.argmax())
        names = main_names if main_names else [f"param_{i}" for i in range(len(main_theta))]

        top5_idx = list(np.argsort(diff)[-5:][::-1])
        top5 = [
            {
                "param": names[i] if i < len(names) else f"param_{i}",
                "theta_main": float(main_theta[i]),
                "theta_comp": float(comp_theta[i]),
                "abs_diff": float(diff[i]),
            }
            for i in top5_idx
        ]

        comp_key = f"theta_{comp_label.lower().replace(' ', '_')}"
        param_diff_table = [
            {
                "param": names[i] if i < len(names) else f"param_{i}",
                "theta_main": float(main_theta[i]),
                comp_key: float(comp_theta[i]),
                "abs_diff": float(diff[i]),
            }
            for i in range(len(main_theta))
        ]

        out.update({
            "available": True,
            "comp_label": comp_label,
            "n_params": len(main_theta),
            "linf_distance": linf,
            "linf_param": names[linf_idx] if linf_idx < len(names) else f"param_{linf_idx}",
            "top5_diffs": top5,
            "param_diff_table": param_diff_table,
            "agreement_note": f"L∞ = {linf:.2e} between main and {comp_label}.",
        })
    except Exception as exc:
        out["note"] = f"Comparison diagnostics failed: {exc}"

    return out


def _build_enhanced_param_df(
    parsed_results: Dict[str, Any],
    cluster_se_data: Optional[Dict[str, Any]] = None,
    bound_diag: Optional[Any] = None,
) -> pd.DataFrame:
    """Build a comprehensive parameter DataFrame with SE, t-ratios, and bound status."""
    from scipy.stats import norm as _norm

    # Collect parameter names and theta from parsed results blocks
    param_data: Dict[str, float] = {}
    for grp_data in parsed_results.values():
        if not isinstance(grp_data, dict):
            continue
        params = grp_data.get("parameters", {})
        if isinstance(params, dict):
            for pname, pval in params.items():
                if pname not in param_data:
                    param_data[pname] = float(pval) if is_num(pval) else float("nan")

    if not param_data:
        return pd.DataFrame()

    param_names_list = list(param_data.keys())

    # Overlay cluster SE vectors
    se_hessian_map: Dict[str, float] = {}
    se_robust_map: Dict[str, float] = {}
    free_mask_map: Dict[str, bool] = {}

    if cluster_se_data is not None:
        art = cluster_se_data.get("cluster_robust_se_artifacts", {}) or {}
        cnames: List[str] = art.get("param_names") or param_names_list
        name_to_idx = {n: i for i, n in enumerate(cnames)}
        se_h = art.get("se_hessian_vector", [])
        se_r = art.get("se_robust_vector", [])
        fm = art.get("free_mask", [])
        theta_c = art.get("converged_theta", [])

        for pname in param_names_list:
            idx = name_to_idx.get(pname)
            if idx is not None:
                se_hessian_map[pname] = float(se_h[idx]) if idx < len(se_h) else float("nan")
                se_robust_map[pname] = float(se_r[idx]) if idx < len(se_r) else float("nan")
                free_mask_map[pname] = bool(fm[idx]) if idx < len(fm) else True
                if idx < len(theta_c):
                    param_data[pname] = float(theta_c[idx])
            else:
                se_hessian_map[pname] = float("nan")
                se_robust_map[pname] = float("nan")
                free_mask_map[pname] = True

    # Bound diagnostics
    at_lower: Dict[str, bool] = {}
    at_upper: Dict[str, bool] = {}
    if bound_diag is not None:
        for p in getattr(bound_diag, "at_lower_bound", []):
            at_lower[str(p)] = True
        for p in getattr(bound_diag, "at_upper_bound", []):
            at_upper[str(p)] = True

    records = []
    for pname in param_names_list:
        theta_val = param_data[pname]
        se_h = se_hessian_map.get(pname, float("nan"))
        se_r = se_robust_map.get(pname, float("nan"))
        in_free = free_mask_map.get(pname, True)

        if is_num(se_r) and se_r > 0 and is_num(theta_val):
            t_rob = theta_val / se_r
            p_rob = float(2.0 * _norm.sf(abs(t_rob)))
        else:
            t_rob = float("nan")
            p_rob = float("nan")

        records.append({
            "param": pname,
            "theta": theta_val,
            "se_hessian": se_h,
            "se_robust": se_r,
            "t_robust": t_rob,
            "p_robust": p_rob,
            "at_lower_bound": at_lower.get(pname, False),
            "at_upper_bound": at_upper.get(pname, False),
            "in_free_mask": in_free,
        })

    return pd.DataFrame(records)


def _fmt_solver_diag_md(solver_diag: Dict[str, Any]) -> str:
    """Render solver convergence diagnostics as Markdown (internal helper)."""
    lines = []
    lines.append(f"**GAMSPy version**: {solver_diag.get('gamspy_version', _DIAG_NA)}")
    lines.append(f"**Solver**: {solver_diag.get('solver', _DIAG_NA)}")
    lines.append("")

    groups = solver_diag.get("groups", [])
    if groups:
        lines.append("**Per-group convergence:**")
        lines.append("")
        lines.append("| Group | Final LL | Iterations | Fn Evals | Wall (s) | Success | Solve Status | Model Status |")
        lines.append("|-------|----------|------------|----------|----------|---------|--------------|--------------|")
        for g in groups:
            ll = g.get("final_ll", _DIAG_NA)
            ll_s = f"{ll:.6f}" if is_num(ll) else str(ll)
            lines.append(
                f"| {g['group']} | {ll_s} | {g.get('n_iterations', _DIAG_NA)} | "
                f"{g.get('n_function_evals', _DIAG_NA)} | {g.get('walltime_s', _DIAG_NA)} | "
                f"{g.get('success', _DIAG_NA)} | {g.get('solve_status_parsed', _DIAG_NA)} | "
                f"{g.get('model_status_parsed', _DIAG_NA)} |"
            )
        lines.append("")

    listing = solver_diag.get("listing_diagnostics", {}) or {}
    note = listing.get("_note", "")
    parse_err = listing.get("_parse_error", "")

    lines.append("**GAMS listing file diagnostics** (from `--listing-file`):")
    lines.append("")
    if note == _DIAG_NA or parse_err:
        lines.append(f"*{parse_err if parse_err else _DIAG_NA}*")
    else:
        rows = [
            ("GAMS solver", listing.get("gams_solver", _DIAG_NA)),
            ("Solver status", listing.get("solver_status", _DIAG_NA)),
            ("Model status", listing.get("model_status", _DIAG_NA)),
            ("Equations", listing.get("equations", _DIAG_NA)),
            ("Variables", listing.get("variables", _DIAG_NA)),
            ("Nonzeros", listing.get("nonzeros", _DIAG_NA)),
            ("Max infeasibility", listing.get("max_infeasibility", _DIAG_NA)),
            ("Solve time (s)", listing.get("solve_time_s", _DIAG_NA)),
            ("Generation time (s)", listing.get("generation_time_s", _DIAG_NA)),
            ("Active bounds count", listing.get("active_bounds", _DIAG_NA)),
        ]
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        for k, v in rows:
            lines.append(f"| {k} | {v} |")
        warnings = listing.get("solver_warnings", [])
        if warnings:
            lines.append("")
            lines.append(f"**Solver warnings ({len(warnings)}):**")
            for w in warnings[:5]:
                lines.append(f"- `{w}`")
    lines.append("")
    return "\n".join(lines)


def _fmt_conopt_md(listing: Dict[str, Any]) -> str:
    """Render CONOPT-specific fields as Markdown (internal helper)."""
    lines = []
    note = listing.get("_note", "")
    parse_err = listing.get("_parse_error", "")

    if note == _DIAG_NA or parse_err:
        msg = parse_err if parse_err else _DIAG_NA
        lines.append(f"*{msg}*")
    else:
        rgmax = listing.get("rgmax", _DIAG_NA)
        rtol = listing.get("conopt_rtol", _DIAG_NA)
        rows = [
            ("RGmax (solver-internal reduced gradient norm)", rgmax),
            ("CONOPT RTOL (optimality tolerance)", rtol),
            ("CONOPT FTOL (feasibility tolerance)", listing.get("conopt_ftol", _DIAG_NA)),
            ("RGmax ≤ RTOL", listing.get("rgmax_below_tol", _DIAG_NA)),
        ]
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        for k, v in rows:
            lines.append(f"| {k} | {v} |")
        lines.append("")
        lines.append(
            "> **Note**: CONOPT RGmax is the solver-internal reduced gradient norm from GAMS/CONOPT. "
            "It is **not** the Python likelihood gradient (score) shown in the next section."
        )
    lines.append("")
    return "\n".join(lines)


def _fmt_gradient_md(grad_diag: Dict[str, Any]) -> str:
    """Render Python likelihood gradient diagnostics as Markdown (internal helper)."""
    lines = []
    lines.append(
        "> **Scope**: This section reports the *Python-side* likelihood gradient — "
        "the score vector ∂ log L / ∂ θ at the converged parameter vector, "
        "computed via central-difference numerical differentiation by the RURO Python engine.  "
        "It is **distinct** from the CONOPT solver’s reduced gradient (RGmax)."
    )
    lines.append("")
    if not grad_diag.get("available", False):
        lines.append(f"*{grad_diag.get('note', _DIAG_NA)}*")
        return "\n".join(lines)

    lines.append(f"**Status**: {grad_diag['note']}")
    lines.append("")
    rows = [
        ("‖∇‖₂ (Euclidean norm)", f"{grad_diag['gradient_norm_l2']:.4e}"),
        ("‖∇‖∞ (max-abs component)", f"{grad_diag['gradient_norm_inf']:.4e}"),
        ("Param with largest |∂LL/∂θ|", grad_diag.get("max_abs_param", _DIAG_NA)),
        ("n_params", grad_diag.get("n_params", _DIAG_NA)),
    ]
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    for k, v in rows:
        lines.append(f"| {k} | {v} |")

    top10 = grad_diag.get("top10_by_magnitude", {})
    if top10:
        lines.append("")
        lines.append("**Top-10 gradient components by magnitude:**")
        lines.append("")
        lines.append("| Param | ∂LL/∂θ |")
        lines.append("|-------|--------|")
        for pname, gval in list(top10.items())[:10]:
            lines.append(f"| {pname} | {gval:.4e} |")
    lines.append("")
    return "\n".join(lines)


def _fmt_hessian_md(hess_diag: Dict[str, Any]) -> str:
    """Render Hessian / VCV diagnostics as Markdown (internal helper)."""
    lines = []
    rows = [
        ("Source", hess_diag.get("source", _DIAG_NA)),
        ("n_free (identified block)", hess_diag.get("n_free", _DIAG_NA)),
        ("Hessian shape (free × free)", hess_diag.get("hessian_shape_free", _DIAG_NA)),
        ("VCV condition number", hess_diag.get("condition_number", _DIAG_NA)),
        ("Near-singular warning (cond > 1e12)", hess_diag.get("near_singular_warning", _DIAG_NA)),
        ("SE Hessian range (positive SEs)", f"{hess_diag.get('se_hessian_min', _DIAG_NA)} – {hess_diag.get('se_hessian_max', _DIAG_NA)}"),
        ("SE Robust range (positive SEs)", f"{hess_diag.get('se_robust_min', _DIAG_NA)} – {hess_diag.get('se_robust_max', _DIAG_NA)}"),
    ]
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    for k, v in rows:
        lines.append(f"| {k} | {v} |")
    t5 = hess_diag.get("t5_robust_vs_hessian")
    if t5:
        lines.append("")
        lines.append(f"**T5 robust-vs-hessian**: {t5}")
    lines.append("")
    return "\n".join(lines)


def _fmt_comparison_md(comp_diag: Dict[str, Any]) -> str:
    """Render comparison-run L-inf diagnostics as Markdown (internal helper)."""
    lines = []
    if not comp_diag.get("available", False):
        lines.append(f"*{comp_diag.get('note', _DIAG_NA)}*")
        return "\n".join(lines)

    lines.append(f"**Comparison label**: {comp_diag.get('comp_label', 'Comparison')}")
    lines.append(f"**n_params**: {comp_diag.get('n_params', _DIAG_NA)}")
    linf = comp_diag.get("linf_distance")
    lines.append(f"**L∞ distance**: {linf:.4e}" if is_num(linf) else f"**L∞ distance**: {_DIAG_NA}")
    lines.append(f"**L∞ at param**: `{comp_diag.get('linf_param', _DIAG_NA)}`")
    lines.append(f"**Summary**: {comp_diag.get('agreement_note', '')}")
    lines.append("")

    top5 = comp_diag.get("top5_diffs", [])
    if top5:
        comp_lbl = comp_diag.get("comp_label", "comp")
        lines.append("**Top-5 parameter differences:**")
        lines.append("")
        lines.append(f"| Param | θ (main) | θ ({comp_lbl}) | |Δ| |")
        lines.append("|-------|----------|---------|------|")
        for row in top5:
            lines.append(
                f"| {row['param']} | {row['theta_main']:.6f} | "
                f"{row['theta_comp']:.6f} | {row['abs_diff']:.2e} |"
            )
    lines.append("")
    return "\n".join(lines)


def run_extended_diagnostics(
    results_json_path: Path,
    output_dir: Path,
    prefix: str = "",
    cluster_se_json: Optional[Path] = None,
    solver_log: Optional[Path] = None,
    listing_file: Optional[Path] = None,
    gamspy_diagnostics: bool = False,
    comparison_results_json: Optional[Path] = None,
    comparison_label: str = "Comparison",
    gradient_diagnostics: bool = False,
    mnl_base: Optional[Path] = None,
    spec_config: Optional[Path] = None,
    strict_report: bool = False,
    cluster_col: Optional[str] = None,
    report_title: Optional[str] = None,
    report_profile: str = DEFAULT_PROFILE,
) -> Dict[str, Any]:
    """Orchestrate all extended post-estimation diagnostics and write artifacts.

    Produces:
      - ``{prefix}extended_diagnostics.md``   Markdown report
      - ``{prefix}extended_diagnostics.json`` Machine-readable diagnostics bundle

    Parameters
    ----------
    results_json_path : Path
        Required. Path to ``estimation_results.json``.
    output_dir : Path
        Directory for output artifacts (created if absent).
    prefix : str
        Filename prefix for output files.
    cluster_se_json : Path, optional
        Cluster-robust SE artifact from ``cluster_robust_se.py``.
    solver_log : Path, optional
        Plain-text GAMS/CONOPT solver log file.
    listing_file : Path, optional
        GAMS ``.lst`` listing file (enables CONOPT RGmax, tolerances, etc.).
    gamspy_diagnostics : bool
        If True, include a GAMSPy/CONOPT diagnostics section even when no
        listing file is supplied (high-level info from results JSON only).
    comparison_results_json : Path, optional
        Second ``estimation_results.json`` for parameter L-inf comparison.
    comparison_label : str
        Label for the comparison run.
    gradient_diagnostics : bool
        If True, compute the Python likelihood gradient at convergence.
        Requires ``--mnl-base`` and ``--spec-config``.
    mnl_base : Path, optional
        MNL data base path (required for gradient diagnostics).
    spec_config : Path, optional
        YAML specification path (required for gradient diagnostics).
    strict_report : bool
        If True, raise RuntimeError when critical diagnostics are unavailable.
    cluster_col : str, optional
        Cluster column name (informational, for report header).
    report_title : str, optional
        Custom Markdown report title.

    Returns
    -------
    dict
        All computed diagnostics plus ``extended_diagnostics_md`` and
        ``extended_diagnostics_json`` artifact paths.

    Notes
    -----
    If ``--listing-file`` / ``--solver-log`` were not saved during estimation,
    GAMS/CONOPT fields (RGmax, tolerances, equations/variables/nonzeros, active
    bounds) will be reported as *Not available in supplied solver artifacts*.
    The recommended practice is to configure the estimator to save the GAMS
    listing file and solver log for every run so these fields are always
    populated.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    LOGGER.info("run_extended_diagnostics: loading results JSON")
    with open(results_json_path, "r", encoding="utf-8") as fh:
        results_data = json.load(fh)

    # 1. Cluster SE JSON
    cluster_se_data = None
    if cluster_se_json is not None:
        try:
            cluster_se_data = _load_cluster_se_json(cluster_se_json)
            LOGGER.info(f"  Loaded cluster SE JSON: {cluster_se_json}")
        except Exception as exc:
            LOGGER.warning(f"  Could not load cluster SE JSON: {exc}")

    # 2. Solver convergence diagnostics
    include_solver = gamspy_diagnostics or (solver_log is not None) or (listing_file is not None)
    if include_solver:
        LOGGER.info("  Building solver convergence diagnostics")
    solver_diag = _extract_solver_convergence_diagnostics(
        results_data,
        solver_log_path=solver_log,
        listing_file_path=listing_file,
    )

    # 3. Python likelihood gradient (distinct from CONOPT RGmax)
    grad_diag: Dict[str, Any] = {
        "available": False,
        "note": _DIAG_NA,
        "distinction_note": (
            "Python likelihood gradient (score at convergence) — "
            "computed via central-difference numerical differentiation. "
            "DISTINCT from CONOPT RGmax / reduced gradient."
        ),
    }
    if gradient_diagnostics:
        LOGGER.info("  Computing Python likelihood gradient (score)")
        grad_diag = _compute_gradient_diagnostics(results_json_path, mnl_base, spec_config)

    # 4. Hessian / VCV diagnostics
    LOGGER.info("  Extracting Hessian diagnostics")
    hess_diag = _extract_extended_hessian_diagnostics(results_data, cluster_se_data)

    # 5. Reproducibility metadata
    LOGGER.info("  Building reproducibility metadata")
    repro_meta = _build_reproducibility_metadata(results_json_path, spec_config, mnl_base, output_dir)

    # 6. Comparison diagnostics
    comp_diag: Dict[str, Any] = {"available": False, "note": _DIAG_NA}
    if comparison_results_json is not None:
        LOGGER.info(f"  Building comparison diagnostics vs {comparison_results_json}")
        comp_diag = _build_comparison_diagnostics(
            main_results_path=results_json_path,
            comp_results_path=comparison_results_json,
            comp_label=comparison_label,
            main_cluster_se_path=cluster_se_json,
        )

    # 7. Enhanced parameter table
    LOGGER.info("  Building enhanced parameter table")
    parsed_for_param: Dict[str, Any] = {
        k: v for k, v in (results_data.get("results", {}) or {}).items()
        if isinstance(v, dict) and "parameters" in v
    }
    param_df = _build_enhanced_param_df(parsed_for_param, cluster_se_data)

    # 8. Data diagnostics (from cluster SE JSON checks block)
    data_diag: Dict[str, Any] = {}
    if cluster_se_data is not None:
        checks = cluster_se_data.get("checks", {}) or {}
        data_diag = {
            "T3_cluster_count": checks.get("T3_cluster_count", _DIAG_NA),
            "T4_se_positivity": checks.get("T4_se_positivity", _DIAG_NA),
            "T5_robust_vs_hessian": checks.get("T5_robust_vs_hessian", _DIAG_NA),
            "PE3_data_loaded": checks.get("PE3_data_loaded", _DIAG_NA),
            "cluster_col": cluster_col or _DIAG_NA,
        }

    # ------------------------------------------------------------------
    # Compose Markdown report
    # ------------------------------------------------------------------
    title = report_title or "Extended Post-Estimation Diagnostics"
    ts = repro_meta.get("timestamp_utc", "")
    results_json_name = results_json_path.name
    spec_name = (
        repro_meta.get("results_json_specification")
        or repro_meta.get("results_json_spec_name")
        or _DIAG_NA
    )

    md: List[str] = [
        f"# {title}",
        "",
        f"**Results JSON**: `{results_json_name}`  ",
        f"**Specification**: {spec_name}  ",
        f"**Generated**: {ts}  ",
        f"**Cluster column**: {cluster_col or _DIAG_NA}",
        "",
        "---",
        "",
        "## 1. Inference Table",
        "",
        ("Full parameter table with Hessian SE, cluster-robust SE, t-ratios, and bound status. "
         "Supply `--cluster-se-json` to populate `se_robust` and `t_robust` columns."),
        "",
    ]

    if not param_df.empty:
        cols = [c for c in ["param", "theta", "se_hessian", "se_robust", "t_robust", "p_robust",
                             "at_lower_bound", "at_upper_bound", "in_free_mask"]
                if c in param_df.columns]
        md.append("| " + " | ".join(cols) + " |")
        md.append("|" + "|".join(["---"] * len(cols)) + "|")
        for _, row in param_df.iterrows():
            cells = []
            for c in cols:
                v = row[c]
                if c in ("theta", "se_hessian", "se_robust"):
                    cells.append(f"{v:.6f}" if is_num(v) and not np.isnan(float(v)) else str(v))
                elif c == "t_robust":
                    cells.append(f"{v:.3f}" if is_num(v) and not np.isnan(float(v)) else str(v))
                elif c == "p_robust":
                    cells.append(f"{v:.4f}" if is_num(v) and not np.isnan(float(v)) else str(v))
                else:
                    cells.append(str(v))
            md.append("| " + " | ".join(cells) + " |")
        md.append("")
    else:
        md.append("*Parameter table could not be constructed from the supplied artifacts.*")
    md.append("")

    md += [
        "## 2. Solver Convergence Diagnostics",
        "",
        _fmt_solver_diag_md(solver_diag),
        "",
        "## 3. CONOPT / GAMS Solver Diagnostics",
        "",
        ("> CONOPT-specific fields (RGmax, tolerances, equations/variables/nonzeros) are parsed "
         "from the GAMS listing file supplied via `--listing-file`.  "
         "If not supplied all fields report «Not available in supplied solver artifacts».  "
         "**Best practice**: configure the estimator to save the GAMS listing file and solver log "
         "for every run so these fields are always populated."),
        "",
        _fmt_conopt_md(solver_diag.get("listing_diagnostics", {"_note": _DIAG_NA})),
        "",
        "## 4. Python Likelihood Gradient Diagnostics",
        "",
        _fmt_gradient_md(grad_diag),
        "",
        "## 5. Hessian Diagnostics",
        "",
        _fmt_hessian_md(hess_diag),
        "",
        "## 6. Data Diagnostics",
        "",
    ]

    if data_diag:
        md += [
            f"**Cluster column**: `{data_diag.get('cluster_col', _DIAG_NA)}`",
            "",
            f"**T3 cluster count**: {data_diag.get('T3_cluster_count', _DIAG_NA)}",
            f"**T4 SE positivity**: {data_diag.get('T4_se_positivity', _DIAG_NA)}",
            f"**T5 robust-vs-hessian**: {data_diag.get('T5_robust_vs_hessian', _DIAG_NA)}",
            f"**PE3 data loaded**: {data_diag.get('PE3_data_loaded', _DIAG_NA)}",
            "",
        ]
    else:
        md.append(
            "*Data diagnostics require `--cluster-se-json`. "
            "Provide a cluster-robust SE artifact to populate T3/T4/T5/PE3.*"
        )
    md.append("")

    md += [
        "## 7. Comparison Run",
        "",
        _fmt_comparison_md(comp_diag),
        "",
        "## 8. Reproducibility Metadata",
        "",
        f"**Timestamp (UTC)**: {repro_meta.get('timestamp_utc', _DIAG_NA)}  ",
        f"**Python**: {repro_meta.get('python_version', _DIAG_NA)}  ",
        f"**Platform**: {repro_meta.get('platform', _DIAG_NA)}  ",
        f"**Git SHA**: {repro_meta.get('git', {}).get('git_sha', _DIAG_NA)}  ",
        f"**Git branch**: {repro_meta.get('git', {}).get('git_branch', _DIAG_NA)}  ",
        f"**Git dirty**: {repro_meta.get('git', {}).get('git_dirty', _DIAG_NA)}  ",
        "",
        "**Package versions:**",
        "",
        "| Package | Version |",
        "|---------|---------|",
    ]
    for pkg, ver in (repro_meta.get("package_versions", {}) or {}).items():
        md.append(f"| {pkg} | {ver} |")

    md += [
        "",
        "**File hashes (SHA-256, first 16 hex digits):**",
        "",
        "| Artifact | Hash |",
        "|----------|------|",
    ]
    for label, h in (repro_meta.get("file_hashes_sha256_prefix16", {}) or {}).items():
        md.append(f"| {label} | `{h}` |")
    md.append("")

    # ------------------------------------------------------------------
    # Write artifacts
    # ------------------------------------------------------------------
    md_content = "\n".join(md)
    md_path = output_dir / f"{prefix}extended_diagnostics.md"
    md_path.write_text(md_content, encoding="utf-8")
    LOGGER.info(f"  Wrote: {md_path}")

    diag_bundle: Dict[str, Any] = {
        "solver_diagnostics": solver_diag,
        "gradient_diagnostics": grad_diag,
        "hessian_diagnostics": hess_diag,
        "comparison_diagnostics": comp_diag,
        "data_diagnostics": data_diag,
        "reproducibility": repro_meta,
    }
    json_path = output_dir / f"{prefix}extended_diagnostics.json"
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(diag_bundle, fh, indent=2, default=str)
    LOGGER.info(f"  Wrote: {json_path}")

    if strict_report:
        issues = []
        if hess_diag.get("condition_number") == _DIAG_NA:
            issues.append("Hessian condition number unavailable (supply --cluster-se-json).")
        if not data_diag:
            issues.append("Data diagnostics unavailable (supply --cluster-se-json).")
        if issues:
            raise RuntimeError(
                f"--strict-report: {len(issues)} required diagnostic(s) missing:\n"
                + "\n".join(f"  - {i}" for i in issues)
            )

    # ------------------------------------------------------------------
    # Enriched diagnostics bundle: now that extended inputs (solver log,
    # cluster SE, gradient) are loaded, rebuild the bundle so the JSON
    # artifact includes them. This overwrites the base bundle written
    # by run_styled_post_estimation when both run in the same invocation.
    # ------------------------------------------------------------------
    enriched_bundle_paths: Dict[str, Path] = {}
    if HAS_DIAGNOSTICS_BUNDLE:
        try:
            # Best-effort: load parsed params from results_data via the existing
            # _build_enhanced_param_df route + the raw arrays. The bundle
            # builder degrades gracefully when parsed_params is minimal.
            class _MinimalParsed:
                pass
            mp = _MinimalParsed()
            mp.param_names = []
            mp.theta = []
            mp.bounds = None
            # Pull names/theta/bounds out of results JSON if available
            for gd in (results_data.get("results", {}) or {}).values():
                if isinstance(gd, dict) and "parameters" in gd:
                    params_dict = gd["parameters"] or {}
                    mp.param_names = list(params_dict.keys())
                    mp.theta = list(params_dict.values())
                    raw_bounds = gd.get("bounds")
                    if isinstance(raw_bounds, dict):
                        mp.bounds = [raw_bounds.get(n, (None, None)) for n in mp.param_names]
                    elif isinstance(raw_bounds, list):
                        mp.bounds = raw_bounds
                    break
            # Block map for parameter classification: derived from the YAML
            # spec if available. Falls back to bundle-side heuristics.
            _ext_block_map = {}
            try:
                _ext_blocks = _load_yaml_spec_blocks(spec_config) if spec_config else {}
                if _ext_blocks:
                    _ext_block_map = _coef_to_block_map(_ext_blocks) or {}
            except Exception:
                _ext_block_map = {}
            bundle = build_diagnostics_bundle(
                profile=report_profile,
                results_data=results_data,
                parsed_params=mp,
                fit_stats={
                    "log_likelihood": (results_data.get("summary") or {}).get("joint_ll"),
                    "n_observations": (results_data.get("summary") or {}).get("n_obs_total"),
                    "n_groups": (results_data.get("summary") or {}).get("n_groups_total"),
                    "n_parameters": len(mp.param_names),
                },
                bound_diagnostics=[],
                mu_results=None,
                prob_diagnostics=None,
                hessian_diagnostics=None,
                cluster_se_data=cluster_se_data,
                solver_diag=solver_diag,
                gradient_diag=grad_diag,
                repro_meta=repro_meta,
                block_map=_ext_block_map,
            )
            enriched_bundle_paths = write_bundle_artifacts(bundle, output_dir, prefix=prefix)
            for label, p in enriched_bundle_paths.items():
                LOGGER.info(f"   (extended) {label}: {p}")
        except Exception as e:
            LOGGER.warning(f"Enriched diagnostics bundle build failed: {e}", exc_info=True)

    return {
        "extended_diagnostics_md": md_path,
        "extended_diagnostics_json": json_path,
        "param_df": param_df,
        "solver_diagnostics": solver_diag,
        "gradient_diagnostics": grad_diag,
        "hessian_diagnostics": hess_diag,
        "comparison_diagnostics": comp_diag,
        "data_diagnostics": data_diag,
        "reproducibility": repro_meta,
        "report_profile": report_profile,
        "diagnostics_bundle_json": enriched_bundle_paths.get("diagnostics_bundle"),
        "enhanced_parameter_table_csv": enriched_bundle_paths.get("enhanced_parameter_table"),
        "solver_diagnostics_json": enriched_bundle_paths.get("solver_diagnostics"),
        "inference_diagnostics_json": enriched_bundle_paths.get("inference_diagnostics"),
    }


# =============================================================================
# CLI INTERFACE
# =============================================================================

def _build_spec_folder_name(spec_config_path: Union[str, Path]) -> str:
    """Build a filesystem-safe folder name from a spec YAML path."""
    path_obj = Path(str(spec_config_path))
    base_name = path_obj.stem or path_obj.name or "unknown_spec"
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", base_name).strip("._")
    return safe_name or "unknown_spec"


def _extract_spec_config_from_results_json(results_json_path: Path) -> Optional[str]:
    """Extract spec config path from estimation_results.json metadata when available."""
    try:
        with open(results_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None

    metadata = data.get("metadata")
    if isinstance(metadata, dict):
        spec_config = metadata.get("spec_config")
        if isinstance(spec_config, str) and spec_config.strip():
            return spec_config

    # Legacy fallback: try command line capture if metadata key is absent
    command_line = data.get("command_line")
    if isinstance(command_line, str):
        match = re.search(r"--spec-config\s+([^\s]+)", command_line)
        if match:
            return match.group(1).strip().strip('"').strip("'")

    return None


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
        help='Base output directory (default: same as results-json parent)'
    )

    parser.add_argument(
        '--no-spec-subdir',
        action='store_true',
        help='Do not create a specification-named subfolder under --output-dir'
    )
    
    parser.add_argument(
        '--auto-timestamp',
        action='store_true',
        help='Automatically create timestamped run folder under the selected output directory'
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

    parser.add_argument(
        '--llm-summary-dir',
        type=Path,
        default=Path("reports"),
        help=(
            'Directory for compact Markdown summaries designed for Git/LLM use '
            '(default: reports)'
        )
    )

    parser.add_argument(
        '--no-llm-summary',
        action='store_true',
        help='Do not write the compact Markdown summary artifact'
    )

    # ------------------------------------------------------------------
    # Extended diagnostics options
    # ------------------------------------------------------------------
    parser.add_argument(
        '--cluster-se-json',
        type=Path,
        default=None,
        metavar='PATH',
        help=(
            'Path to cluster-robust SE JSON artifact produced by cluster_robust_se.py. '
            'Enables inference table (se_robust, t-ratios), Hessian diagnostics, '
            'and data-quality checks (T3/T4/T5).'
        )
    )

    parser.add_argument(
        '--solver-log',
        type=Path,
        default=None,
        metavar='PATH',
        help=(
            'Path to plain-text GAMS/CONOPT solver log file. '
            'Parsed for convergence information (objective, iterations, termination). '
            'Best practice: configure the estimator to save this file for every run.'
        )
    )

    parser.add_argument(
        '--listing-file',
        type=Path,
        default=None,
        metavar='PATH',
        help=(
            'Path to GAMS .lst listing file. '
            'Parsed for CONOPT diagnostics: RGmax, RTOL/FTOL tolerances, '
            'equations/variables/nonzeros counts, max infeasibility, active bounds. '
            'If not supplied, all CONOPT fields report "Not available". '
            'Best practice: configure the estimator to save this file for every run.'
        )
    )

    parser.add_argument(
        '--gamspy-diagnostics',
        action='store_true',
        help=(
            'Include a GAMSPy/CONOPT diagnostics section in the extended report. '
            'Automatically enabled when --listing-file or --solver-log are supplied. '
            'Without those files only the high-level status from estimation_results.json '
            'is available; CONOPT fields (RGmax, tolerances) will be reported as '
            '"Not available in supplied solver artifacts".'
        )
    )

    parser.add_argument(
        '--gradient-diagnostics',
        action='store_true',
        help=(
            'Compute the Python likelihood gradient (score vector) at the converged '
            'parameter vector via central-difference numerical differentiation. '
            'Requires --mnl-base and --spec-config. '
            'NOTE: this is the RURO Python-side gradient of log L and is DISTINCT '
            'from the CONOPT solver-internal reduced gradient (RGmax).'
        )
    )

    parser.add_argument(
        '--comparison-results-json',
        type=Path,
        default=None,
        metavar='PATH',
        help=(
            'Path to a second estimation_results.json for parameter comparison. '
            'Produces an L-infinity distance table between the two runs.'
        )
    )

    parser.add_argument(
        '--comparison-label',
        type=str,
        default='Comparison',
        metavar='LABEL',
        help='Label for the comparison run in the extended report (default: "Comparison")'
    )

    parser.add_argument(
        '--cluster-col',
        type=str,
        default=None,
        metavar='COL',
        help='Name of the cluster column used for sandwich SE computation (informational)'
    )

    parser.add_argument(
        '--report-title',
        type=str,
        default=None,
        metavar='TITLE',
        help='Custom title for the extended diagnostics Markdown report'
    )

    parser.add_argument(
        '--strict-report',
        action='store_true',
        help=(
            'Raise an error if critical diagnostics are unavailable '
            '(Hessian condition number, data checks). '
            'Use to enforce complete diagnostic coverage in automated pipelines.'
        )
    )

    parser.add_argument(
        '--report-profile',
        type=str,
        choices=list(PROFILE_CHOICES),
        default=DEFAULT_PROFILE,
        metavar='PROFILE',
        help=(
            'Report depth: decision (adoption-relevant only), '
            'standard (default), full (all useful diagnostics), '
            'technical (debugging + legacy combined fit-stats appendix).'
        )
    )

    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed is not None:
        np.random.seed(args.seed)
        LOGGER.info(f"Set random seed to {args.seed}")
    
    # Build output directory (base + optional spec folder + optional timestamp)
    if args.output_dir is None:
        output_dir_base = args.results_json.parent / 'post_estimation'
    else:
        output_dir_base = Path(args.output_dir)

    spec_for_grouping = args.spec_config
    if spec_for_grouping is None:
        extracted_spec = _extract_spec_config_from_results_json(args.results_json)
        if extracted_spec:
            spec_for_grouping = Path(extracted_spec)
            LOGGER.info(f"Detected specification from results JSON: {extracted_spec}")

    if not args.no_spec_subdir and spec_for_grouping is not None:
        spec_folder_name = _build_spec_folder_name(spec_for_grouping)
        output_dir_base = output_dir_base / spec_folder_name
        LOGGER.info(f"Using specification folder: {spec_folder_name}")

    output_dir = output_dir_base
    if args.auto_timestamp:
        from datetime import datetime
        timestamp = datetime.now().strftime("run_%Y-%m-%d_%H-%M-%S")
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
            llm_summary_dir=None if args.no_llm_summary else args.llm_summary_dir,
            report_title=args.report_title,
            report_profile=args.report_profile,
            # Phase 2: pre-load extended inputs so styled HTML uses enriched bundle
            cluster_se_path=args.cluster_se_json,
            solver_log_path=args.solver_log,
            listing_file_path=args.listing_file,
            # bootstrap=args.bootstrap,  # Future: pass to function when implemented
        )
    except Exception as e:
        LOGGER.error(f"Post-estimation failed: {e}", exc_info=True)
        return 1

    # Run extended diagnostics when any extended option is requested
    _run_ext = any([
        args.cluster_se_json is not None,
        args.solver_log is not None,
        args.listing_file is not None,
        args.gamspy_diagnostics,
        args.gradient_diagnostics,
        args.comparison_results_json is not None,
        args.strict_report,
    ])
    if _run_ext:
        try:
            run_extended_diagnostics(
                results_json_path=args.results_json,
                output_dir=output_dir,
                prefix=args.prefix,
                cluster_se_json=args.cluster_se_json,
                solver_log=args.solver_log,
                listing_file=args.listing_file,
                gamspy_diagnostics=args.gamspy_diagnostics,
                comparison_results_json=args.comparison_results_json,
                comparison_label=args.comparison_label,
                gradient_diagnostics=args.gradient_diagnostics,
                mnl_base=args.mnl_base,
                spec_config=args.spec_config,
                strict_report=args.strict_report,
                cluster_col=args.cluster_col,
                report_title=args.report_title,
                report_profile=args.report_profile,
            )
        except RuntimeError as e:
            # --strict-report failures surface as RuntimeError
            LOGGER.error(f"Extended diagnostics strict-report failure: {e}")
            return 1
        except Exception as e:
            LOGGER.error(f"Extended diagnostics failed: {e}", exc_info=True)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
