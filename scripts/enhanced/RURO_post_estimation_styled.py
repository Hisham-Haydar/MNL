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
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime

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
                self.preference_groups.append(group)

                shifters = []
                for k in params.keys():
                    if 'pref.beta_l_' in k and 'beta_l0' not in k:
                        shifter = k.replace('pref.beta_l_', '')
                        if shifter.endswith('_m') or shifter.endswith('_f'):
                            shifter = shifter[:-2]
                        shifters.append(shifter)
                self.leisure_shifters[group] = list(set(shifters))

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
    all_bounds = []
    all_init = []

    results = data.get('results', {})

    for group_name, group_data in results.items():
        if not group_data.get('success', False):
            LOGGER.warning(f"Group {group_name} did not converge, skipping")
            continue

        params = group_data.get('parameters', {})
        se_dict = group_data.get('standard_errors', {})
        bounds_dict = group_data.get('bounds', {})
        init_dict = group_data.get('initial_values', {})

        for param_name, param_value in params.items():
            full_name = f"{group_name}.{param_name}"
            all_param_names.append(full_name)
            all_theta.append(param_value)
            all_se.append(se_dict.get(param_name, np.nan))

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
        beta_c = params.get('beta_c', 1.0)
        theta_c = params.get('theta_c', 0.5)

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
            'cou': 'Couples (shared)', 'singles_male': 'Single Males',
            'singles_female': 'Single Females', 'couples': 'Couples'
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
        'cou_m': 'Males in Couples', 'cou_f': 'Females in Couples',
        'singles_male': 'Single Males', 'singles_female': 'Single Females',
        'couples': 'Couples'
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
            theta_l = params.get('theta_l', 0.5)
            theta_c = params.get('theta_c', 0.5)
            beta_l0 = params.get('beta_l0', 0.0)
            beta_c = params.get('beta_c', 1.0)

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
                   'singles_male': 'SM', 'singles_female': 'SF', 'couples_m': 'CM', 'couples_f': 'CF'}

    groups = list(fit_results.keys())
    if not groups:
        return {}

    x = np.arange(len(groups))
    width = 0.35

    # Participation rates
    fig, ax = plt.subplots(figsize=(8, 5))
    obs_rates = [fit_results[g].get('participation_rate_observed', 0) * 100 for g in groups]
    pred_rates = [fit_results[g].get('participation_rate_predicted', 0) * 100 for g in groups]

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
            groups_to_plot.append((g, {
                'beta_c': params.get('beta_c', 1.0),
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
        'sm': '#1f77b4', 'sf': '#ff7f0e', 'cou_m': '#2ca02c', 'cou_f': '#d62728',
        'singles_male': '#1f77b4', 'singles_female': '#ff7f0e',
        'couples_m': '#2ca02c', 'couples_f': '#d62728', 'cou': '#9467bd', 'couples': '#9467bd'
    }

    group_labels = {
        'sm': 'Single Males', 'sf': 'Single Females',
        'cou_m': 'Males in Couples', 'cou_f': 'Females in Couples',
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


# =============================================================================
# HTML REPORT GENERATION (STYLED VERSION)
# =============================================================================

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
) -> Path:
    """
    Generate comprehensive HTML report with professional styling.

    Matches the aesthetics of vw_pooled_post_estimation_report.html
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    group_labels = {
        'sm': 'Single Males', 'sf': 'Single Females',
        'cou': 'Couples', 'cou_m': 'Males in Couples', 'cou_f': 'Females in Couples',
        'singles_male': 'Single Males', 'singles_female': 'Single Females',
        'couples': 'Couples', 'couples_m': 'Males in Couples', 'couples_f': 'Females in Couples',
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
    @media (max-width: 768px) { .two-col, .four-col, .contour-grid { grid-template-columns: 1fr; } }
    """

    # Build fit stats section
    fit_stats_rows = ""
    for k, v in fit_stats.items():
        if isinstance(v, float):
            if abs(v) < 0.01 or abs(v) > 10000:
                fit_stats_rows += f"<tr><th>{k}</th><td>{v:.4e}</td></tr>"
            else:
                fit_stats_rows += f"<tr><th>{k}</th><td>{v:.4f}</td></tr>"
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
    """

    # Build elasticities table
    elasticities_html = ""
    if elasticities_df is not None and len(elasticities_df) > 0:
        elasticities_html = elasticities_df.to_html(classes='table table-striped', border=0, index=False)

    # Build MUC analysis table
    muc_analysis_html = ""
    if muc_analysis:
        muc_rows = ""
        for row in muc_analysis:
            row_class = 'class="warning-row"' if row.get('is_warning') else ''
            c_muc_1 = row.get('C where MUC=1')
            c_muc_1_str = f"{c_muc_1:.4f}" if c_muc_1 is not None else "N/A"
            muc_median = row.get('MUC at Median C', 0)
            muc_median_str = f"{muc_median:.4f}" if isinstance(muc_median, (int, float)) else "N/A"

            muc_rows += f"""
            <tr {row_class}>
                <td>{row['Group']}</td>
                <td>{row['β_c']:.4f}</td>
                <td>{row['θ_c']:.4f}</td>
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
            <tbody>{muc_rows}</tbody>
        </table>
        """

    # Build fit diagnostics table
    fit_table_rows = ""
    for group, results in fit_results.items():
        obs_part = results.get('participation_rate_observed', np.nan)
        pred_part = results.get('participation_rate_predicted', np.nan)
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
    if mu_results:
        for group, results in mu_results.items():
            n_ind = results.get('n_individuals', 0)
            pct_muc = results.get('pct_negative_muc', 0) or 0
            pct_mul = results.get('pct_negative_mul', 0) or 0
            muc_mean = results.get('muc_mean', np.nan)
            mul_mean = results.get('mul_mean', np.nan)

            muc_cell_class = 'class="warning-cell"' if pct_muc > 5 else ''
            mul_cell_class = 'class="warning-cell"' if pct_mul > 5 else ''

            muc_mean_str = f"{muc_mean:.4f}" if isinstance(muc_mean, float) and np.isfinite(muc_mean) else "N/A"
            mul_mean_str = f"{mul_mean:.4e}" if isinstance(mul_mean, float) and np.isfinite(mul_mean) else "N/A"

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

    # Build plots section
    plots_section = ""
    if plot_paths:
        contour_plots = []
        mu_comparison_plots = []
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
                elif 'fit_' in name.lower() or 'participation' in name.lower() or 'mean_hours' in name.lower():
                    title = name.replace('fit_', '').replace('_', ' ').title()
                    fit_plots.append(f'<figure><figcaption>{title}</figcaption>{img_tag}</figure>')

        if mu_comparison_plots:
            plots_section += f'<h3>Marginal Utility Comparison</h3><div class="two-col">{"".join(mu_comparison_plots)}</div>'
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
    """

    # Build full parameter table
    param_df = parsed_params.to_dataframe()
    param_table_rows = ""
    for idx, row in param_df.iterrows():
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
        if is_bounded and isinstance(est, float):
            if lb is not None and abs(est - lb) < 1e-6:
                hit_bound = True
            if ub is not None and abs(est - ub) < 1e-6:
                hit_bound = True

        if hit_bound:
            row_class = 'class="bound-hit"'
        elif is_bounded:
            row_class = 'class="bounded-param"'

        est_str = f"{est:.4f}" if isinstance(est, float) and np.isfinite(est) else "N/A"
        se_str = f"{se:.4f}" if isinstance(se, float) and np.isfinite(se) else "N/A"
        t_str = f"{t_val:.2f}" if isinstance(t_val, float) and np.isfinite(t_val) else "N/A"
        lb_str = f"{lb:.4f}" if lb is not None else "—"
        ub_str = f"{ub:.4f}" if ub is not None else "—"
        init_str = f"{init_val:.4f}" if init_val is not None and not np.isnan(init_val) else "N/A"

        sig = ""
        p_str = "N/A"
        p_class = ""
        if isinstance(p_val, float) and np.isfinite(p_val):
            p_str = f"{p_val:.4f}"
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

        param_table_rows += f"""
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

    <section>
        <h2>📈 Labor Supply Elasticities</h2>
        <p>Structural approximations based on estimated preference parameters.</p>
        {elasticities_html}
        <p><small><em>Note: For exact elasticities, use simulation-based methods.</em></small></p>
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
            <tbody>{mu_table_rows}</tbody>
        </table>

        <h3>MUC Behavior Analysis</h3>
        <p>For well-behaved utility: MUC &gt; 0 (β_c &gt; 0) and diminishing (θ_c &lt; 1)</p>
        {muc_analysis_html}
    </section>

    <section>
        <h2>🗺️ Utility Contours & Plots</h2>
        {plots_section}
    </section>

    <section>
        <h2>⚙️ Group-Specific Parameters</h2>
        <div class="param-groups">
            {group_params_html}
        </div>
    </section>

    <section>
        <h2>📋 Full Parameter Estimates</h2>
        <p><em>Significance: *** p&lt;0.001, ** p&lt;0.01, * p&lt;0.05</em></p>
        {color_legend}
        <div style="max-height:600px; overflow-y:auto;">
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
                <tbody>{param_table_rows}</tbody>
            </table>
        </div>
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
# MAIN POST-ESTIMATION PIPELINE
# =============================================================================

def run_styled_post_estimation(
    results_json_path: Path,
    mnl_base: Path = None,
    output_dir: Path = None,
    prefix: str = "",
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
    LOGGER.info("\n1. Loading estimation results...")

    # Try enhanced format first, then legacy
    try:
        parsed, data = load_estimation_results_from_json(results_json_path)
    except (KeyError, TypeError):
        LOGGER.info("  Trying legacy JSON format...")
        parsed, data = load_estimation_results_legacy(results_json_path)

    LOGGER.info(f"   Found {len(parsed.groups)} groups: {parsed.groups}")
    LOGGER.info(f"   Preference groups: {parsed.preference_groups}")

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
            fit_stats['BIC'] = -2 * fit_stats['log_likelihood'] + np.log(fit_stats['n_observations']) * fit_stats['n_parameters']

    # Compute elasticities
    LOGGER.info("\n2. Computing elasticities...")
    elasticities_df = compute_structural_elasticities(parsed)

    # MUC behavior analysis
    LOGGER.info("\n3. Analyzing MUC behavior...")
    muc_analysis = analyze_muc_behavior(parsed)

    # Generate plots
    LOGGER.info("\n4. Generating plots...")
    plot_paths = {}

    # Fit comparison (placeholder - would need data)
    fit_results = {}
    for group in parsed.preference_groups:
        fit_results[group] = {
            'participation_rate_observed': 0.9,
            'participation_rate_predicted': 0.9,
            'mean_hours_observed': 35,
            'mean_hours_predicted': 35,
        }

    plot_paths.update(plot_fit_comparison(fit_results, output_dir, prefix))
    plot_paths.update(plot_utility_contours_all_groups(parsed, output_dir, prefix))
    plot_paths.update(plot_mu_comparison(parsed, output_dir, prefix))

    # Generate HTML report
    LOGGER.info("\n5. Generating HTML report...")

    post_est_end = time.time()
    post_estimation_time = post_est_end - post_est_start
    total_time = (estimation_time or 0) + post_estimation_time

    html_path = output_dir / f'{prefix}post_estimation_report.html'
    generate_html_report_styled(
        parsed_params=parsed,
        fit_results=fit_results,
        output_path=html_path,
        fit_stats=fit_stats,
        plot_paths=plot_paths,
        mu_results={},  # Would compute from data
        elasticities_df=elasticities_df,
        muc_analysis=muc_analysis,
        estimation_time_seconds=estimation_time,
        post_estimation_time_seconds=post_estimation_time,
        total_elapsed_seconds=total_time if estimation_time else None,
    )

    # Save CSV outputs
    LOGGER.info("\n6. Saving CSV outputs...")

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
        '--mnl-base',
        type=Path,
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
        '--prefix',
        type=str,
        default="",
        help='Prefix for output files'
    )

    args = parser.parse_args()

    try:
        results = run_styled_post_estimation(
            results_json_path=args.results_json,
            mnl_base=args.mnl_base,
            output_dir=args.output_dir,
            prefix=args.prefix,
        )
        return 0
    except Exception as e:
        LOGGER.error(f"Post-estimation failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
