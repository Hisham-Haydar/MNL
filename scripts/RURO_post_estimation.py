"""
RURO Post-Estimation Analysis - Refactored Version
===================================================

This module provides post-estimation analysis for RURO (Random Utility Random Opportunity)
labor supply models. It is designed to be **fully automatic** and dynamically adapt to
whatever parameters are passed from the estimation.

Key Design Principles:
1. **Parameter-Driven**: All computations derive from param_names and theta arrays
2. **No Hardcoding**: Parameter names are parsed dynamically, not hardcoded
3. **Flexible Utility**: Utility computation adapts to available covariates
4. **Single Source of Truth**: No duplicate functions

Author: RURO Team
"""

import logging
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))
from path_helpers import outputs_root  # noqa: E402

# Optional imports
try:
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

LOGGER = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES FOR STRUCTURED PARAMETER HANDLING
# =============================================================================

@dataclass
class ParsedParameters:
    """
    Container for parsed estimation parameters.
    
    This class automatically parses parameter names from the estimation results
    and organizes them by group and type for easy access.
    """
    # Raw inputs
    param_names: List[str]
    theta: np.ndarray
    std_errors: Optional[np.ndarray] = None
    
    # Parsed structure (populated by __post_init__)
    groups: List[str] = field(default_factory=list)
    param_types: List[str] = field(default_factory=list)
    params_by_group: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Identified model components
    preference_groups: List[str] = field(default_factory=list)  # Groups with utility params
    leisure_shifters: Dict[str, List[str]] = field(default_factory=dict)  # Leisure coefficient shifters per group
    
    def __post_init__(self):
        """Parse parameter names and organize by group."""
        self._parse_parameters()
        self._identify_model_structure()
    
    def _parse_parameters(self):
        """Parse parameter names into structured dict."""
        groups_set = set()
        types_set = set()
        
        for i, name in enumerate(self.param_names):
            parts = name.split('.')
            if len(parts) >= 2:
                group = parts[0]
                param_type = parts[1]
                param_name = '.'.join(parts[1:])  # Everything after group prefix
                
                groups_set.add(group)
                types_set.add(param_type)
                
                if group not in self.params_by_group:
                    self.params_by_group[group] = {}
                
                # Store both full name and short name
                self.params_by_group[group][param_name] = self.theta[i]
                self.params_by_group[group][name] = self.theta[i]  # Full name too
            else:
                # Single-part name - store at top level
                if '_global' not in self.params_by_group:
                    self.params_by_group['_global'] = {}
                self.params_by_group['_global'][name] = self.theta[i]
        
        self.groups = sorted(list(groups_set))
        self.param_types = sorted(list(types_set))
    
    def _identify_model_structure(self):
        """Identify which groups have preference parameters and what shifters they use."""
        for group, params in self.params_by_group.items():
            # Check if this group has preference parameters (has theta_l or beta_c)
            has_theta_l = any('theta_l' in k for k in params.keys())
            has_beta_c = any('beta_c' in k for k in params.keys())
            has_beta_l0 = any('beta_l0' in k for k in params.keys())
            
            if has_theta_l or has_beta_c or has_beta_l0:
                self.preference_groups.append(group)
                
                # Find leisure shifters (parameters starting with beta_l_ but not beta_l0)
                shifters = []
                for k in params.keys():
                    if k.startswith('pref.beta_l_') and 'beta_l0' not in k:
                        # Extract the shifter name (e.g., 'age_norm' from 'pref.beta_l_age_norm')
                        shifter = k.replace('pref.beta_l_', '')
                        # Remove _m or _f suffix for couples
                        if shifter.endswith('_m') or shifter.endswith('_f'):
                            shifter = shifter[:-2]
                        shifters.append(shifter)
                
                self.leisure_shifters[group] = list(set(shifters))
    
    def get_param(self, group: str, param_name: str, default: float = 0.0) -> float:
        """Get a parameter value by group and name."""
        if group not in self.params_by_group:
            return default
        
        params = self.params_by_group[group]
        
        # Try different name formats
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
            # Simplify key names (remove 'pref.' prefix if present)
            simple_key = key.replace('pref.', '') if key.startswith('pref.') else key
            result[simple_key] = val
        
        return result
    
    def get_leisure_coef_params(self, group: str, suffix: str = '') -> Dict[str, float]:
        """
        Get all leisure coefficient parameters for a group.
        
        For couples, suffix should be '_m' or '_f'.
        Returns dict like {'beta_l0': ..., 'beta_l_age_norm': ..., 'theta_l': ...}
        """
        params = self.params_by_group.get(group, {})
        result = {}
        
        # Build list of expected parameter names
        param_patterns = [
            f'pref.beta_l0{suffix}',
            f'pref.theta_l{suffix}',
        ]
        
        # Also add all beta_l_ shifters
        for key in params.keys():
            if f'pref.beta_l_' in key and key.endswith(suffix):
                param_patterns.append(key)
        
        # Extract values
        for pattern in param_patterns:
            for key, val in params.items():
                if key == pattern or key.endswith(pattern):
                    # Simplify name
                    simple = key.replace('pref.', '').replace(suffix, '')
                    result[simple] = val
        
        return result
    
    def get_consumption_params(self, group: str) -> Dict[str, float]:
        """Get consumption parameters (beta_c, theta_c) for a group."""
        params = self.params_by_group.get(group, {})
        result = {}
        
        for key, val in params.items():
            if 'beta_c' in key or 'theta_c' in key:
                simple = key.replace('pref.', '')
                result[simple] = val
        
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
            if self.std_errors is not None and not np.isnan(self.std_errors[i]):
                row['t_value'] = self.theta[i] / self.std_errors[i]
                row['p_value'] = 2 * (1 - norm.cdf(abs(row['t_value']))) if SCIPY_AVAILABLE else np.nan
            else:
                row['t_value'] = np.nan
                row['p_value'] = np.nan
            rows.append(row)
        
        return pd.DataFrame(rows)


# =============================================================================
# CORE MATHEMATICAL FUNCTIONS (Single Implementation)
# =============================================================================

def boxcox_transform(x: np.ndarray, theta: float, eps: float = 1e-10) -> np.ndarray:
    """
    Box-Cox transformation: (x^θ - 1) / θ
    
    For θ → 0, this approaches log(x).
    """
    x = np.asarray(x)
    x = np.clip(x, eps, None)  # Ensure positive values
    
    if abs(theta) < eps:
        return np.log(x)
    else:
        return (np.power(x, theta) - 1.0) / theta


def d_boxcox_dx(x: np.ndarray, theta: float, eps: float = 1e-10) -> np.ndarray:
    """
    Derivative of Box-Cox: d/dx [(x^θ - 1) / θ] = x^(θ-1)
    """
    x = np.asarray(x)
    x = np.clip(x, eps, None)
    return np.power(x, theta - 1.0)


# =============================================================================
# STANDARD ERROR COMPUTATION
# =============================================================================

def compute_standard_errors(
    theta: np.ndarray,
    grad_func: Callable[[np.ndarray], np.ndarray],
    param_names: List[str],
    eps: float = 1e-5,
) -> Dict[str, Any]:
    """
    Compute standard errors using numerical Hessian approximation.
    
    Parameters
    ----------
    theta : np.ndarray
        Parameter estimates
    grad_func : Callable
        Function that returns gradient of NEGATIVE log-likelihood
    param_names : List[str]
        Parameter names
    eps : float
        Step size for numerical differentiation
    
    Returns
    -------
    Dict with 'se', 'varcov', 't_values', 'p_values'
    """
    n_params = len(theta)
    
    # Compute Hessian numerically (central differences)
    LOGGER.info(f"Computing numerical Hessian ({n_params}x{n_params})...")
    H = np.zeros((n_params, n_params))
    
    for i in range(n_params):
        theta_plus = theta.copy()
        theta_minus = theta.copy()
        theta_plus[i] += eps
        theta_minus[i] -= eps
        
        g_plus = grad_func(theta_plus)
        g_minus = grad_func(theta_minus)
        
        # Second derivative: (g(x+h) - g(x-h)) / 2h
        H[:, i] = (g_plus - g_minus) / (2 * eps)
    
    # Symmetrize
    H = 0.5 * (H + H.T)
    
    # Compute variance-covariance matrix
    try:
        varcov = np.linalg.inv(H)
        se = np.sqrt(np.diag(varcov))
        
        # Check for negative variances
        neg_var = np.diag(varcov) < 0
        if np.any(neg_var):
            LOGGER.warning(f"Warning: {np.sum(neg_var)} parameters have negative variance")
            se[neg_var] = np.nan
        
        # Compute t-values and p-values
        t_values = theta / se
        p_values = 2 * (1 - norm.cdf(np.abs(t_values))) if SCIPY_AVAILABLE else np.full_like(se, np.nan)
        
        return {
            'se': se,
            'varcov': varcov,
            't_values': t_values,
            'p_values': p_values,
            'hessian': H,
        }
        
    except np.linalg.LinAlgError as e:
        LOGGER.error(f"Hessian inversion failed: {e}")
        return {
            'se': np.full(n_params, np.nan),
            'varcov': None,
            't_values': np.full(n_params, np.nan),
            'p_values': np.full(n_params, np.nan),
            'hessian': H,
        }


# =============================================================================
# BACKWARD COMPATIBILITY WRAPPERS
# =============================================================================

def run_joint_post_estimation(
    theta: np.ndarray,
    param_names: List[str],
    log_likelihood: float,
    n_sm: int = 0,
    n_sf: int = 0,
    n_cou: int = 0,
    df_sm: pd.DataFrame = None,
    df_sf: pd.DataFrame = None,
    df_cou: pd.DataFrame = None,
    wage_spec: str = "fw",
    out_dir: Path = None,
    se: np.ndarray = None,
    std_errors: np.ndarray = None,
    varcov: np.ndarray = None,
    theta0: np.ndarray = None,
    bounds: List = None,
    estimation_time_seconds: float = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Backward-compatible wrapper for run_post_estimation.
    
    This function signature matches the old API from RURO_estimate_FR.py.
    
    Parameters
    ----------
    theta : np.ndarray
        Estimated parameter values
    param_names : List[str]
        Parameter names
    log_likelihood : float
        Log-likelihood at optimum
    n_sm, n_sf, n_cou : int
        Number of individuals in each group
    df_sm, df_sf, df_cou : pd.DataFrame
        MNL datasets for each group
    wage_spec : str
        "fw" or "vw" - affects output prefix
    out_dir : Path
        Output directory
    se : np.ndarray
        Standard errors (old API name)
    std_errors : np.ndarray
        Standard errors (new API name)
    varcov : np.ndarray
        Variance-covariance matrix
    theta0 : np.ndarray
        Initial parameter values (for reporting)
    bounds : List
        Parameter bounds (for reporting)
    estimation_time_seconds : float
        Time taken for estimation
    """
    # Handle se vs std_errors naming
    if std_errors is None and se is not None:
        std_errors = se
    
    # Compute n_individuals
    n_individuals = n_sm + n_sf + n_cou
    if n_individuals == 0:
        # Try to compute from dataframes
        n_individuals = sum([
            len(df_sm['idhh'].unique()) if df_sm is not None and 'idhh' in df_sm.columns else 0,
            len(df_sf['idhh'].unique()) if df_sf is not None and 'idhh' in df_sf.columns else 0,
            len(df_cou['idhh'].unique()) if df_cou is not None and 'idhh' in df_cou.columns else 0,
        ])
    
    # Set prefix based on wage_spec
    prefix = f"{wage_spec}_joint_" if wage_spec else ""
    
    # Build param_bounds dict for HTML report
    param_bounds = {}
    if bounds is not None:
        for i, name in enumerate(param_names):
            if i < len(bounds):
                param_bounds[name] = bounds[i]
    
    # Build initial_values dict for HTML report  
    initial_values = {}
    if theta0 is not None:
        for i, name in enumerate(param_names):
            if i < len(theta0):
                initial_values[name] = theta0[i]
    
    return run_post_estimation(
        theta=theta,
        param_names=param_names,
        log_likelihood=log_likelihood,
        df_sm=df_sm,
        df_sf=df_sf,
        df_cou=df_cou,
        out_dir=out_dir,
        std_errors=std_errors,
        prefix=prefix,
        n_individuals=n_individuals,
        param_bounds=param_bounds,
        initial_values=initial_values,
        **kwargs
    )


def run_full_post_estimation(
    result,  # scipy.optimize.OptimizeResult
    grad_func: Callable,
    param_names: List[str],
    n_individuals: int,
    df: pd.DataFrame = None,
    wage_spec: str = "fw",
    sex: str = "pooled",
    out_dir: Path = None,
    save_excel: bool = True,
    save_plots: bool = True,
    save_html: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Backward-compatible wrapper that computes SE then runs post-estimation.
    
    This function signature matches the old API.
    """
    # Extract theta from result
    theta = result.x
    log_likelihood = -result.fun if hasattr(result, 'fun') else 0.0
    
    # Compute standard errors
    se_result = compute_standard_errors(theta, grad_func, param_names)
    std_errors = se_result.get('se')
    varcov = se_result.get('varcov')
    
    # Determine which dataset to use based on sex
    df_sm = None
    df_sf = None
    df_cou = None
    
    if df is not None:
        if sex == "male":
            df_sm = df
        elif sex == "female":
            df_sf = df
        else:
            # Pooled or couples - check for couple columns
            if 'hours_m' in df.columns or 'hours_f' in df.columns:
                df_cou = df
            else:
                # Try to split by sex
                if 'sex' in df.columns:
                    df_sm = df[df['sex'] == 'm'].copy()
                    df_sf = df[df['sex'] == 'f'].copy()
                elif 'dsex' in df.columns:
                    df_sm = df[df['dsex'] == 1].copy()
                    df_sf = df[df['dsex'] == 0].copy()
    
    # Run post-estimation
    result = run_post_estimation(
        theta=theta,
        param_names=param_names,
        log_likelihood=log_likelihood,
        df_sm=df_sm,
        df_sf=df_sf,
        df_cou=df_cou,
        out_dir=out_dir,
        std_errors=std_errors,
        n_individuals=n_individuals,
        **kwargs
    )
    
    # Add SE results
    result['std_errors'] = std_errors
    result['varcov'] = varcov
    result['t_values'] = se_result.get('t_values')
    result['p_values'] = se_result.get('p_values')
    
    # Save Excel if requested
    if save_excel and out_dir is not None:
        try:
            excel_path = Path(out_dir) / 'post_estimation_results.xlsx'
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                result['parsed_params'].to_dataframe().to_excel(writer, sheet_name='Parameters', index=False)
                
                # Fit results
                if result.get('fit_results'):
                    fit_df = pd.DataFrame(result['fit_results']).T
                    fit_df.to_excel(writer, sheet_name='Fit')
                
                # MU results
                if result.get('mu_results'):
                    mu_df = pd.DataFrame(result['mu_results']).T
                    mu_df.to_excel(writer, sheet_name='MU_Diagnostics')
            
            LOGGER.info(f"Excel results saved to: {excel_path}")
            result['excel_path'] = excel_path
        except Exception as e:
            LOGGER.warning(f"Could not save Excel: {e}")
    
    return result


# =============================================================================
# DYNAMIC UTILITY COMPUTATION
# =============================================================================

class DynamicUtilityComputer:
    """
    Computes utility values dynamically based on available parameters and data columns.
    
    This class adapts to whatever parameters exist in the estimation results,
    without requiring hardcoded parameter names.
    """
    
    def __init__(self, parsed_params: ParsedParameters):
        self.params = parsed_params
    
    def compute_utility_singles(
        self, 
        df: pd.DataFrame, 
        group: str,
        consumption_col: str = 'consumption',
        leisure_col: str = 'leisure',
        normalize_c: float = 25000.0,
        normalize_l: float = 45.0,
    ) -> np.ndarray:
        """
        Compute systematic utility for singles.
        
        U = β_l(X) × BC(l; θ_l) + β_c × BC(c; θ_c)
        
        where β_l(X) = β_l0 + Σ β_l_k × X_k for all available shifters k.
        """
        n = len(df)
        
        # Get parameters
        group_params = self.params.get_all_params_for_group(group)
        
        theta_l = group_params.get('theta_l', 0.5)
        theta_c = group_params.get('theta_c', 0.5)
        beta_c = group_params.get('beta_c', 1.0)
        beta_l0 = group_params.get('beta_l0', 0.0)
        
        # Get consumption and leisure
        c = self._get_consumption(df, consumption_col, normalize_c)
        l = self._get_leisure(df, leisure_col, normalize_l)
        
        # Build leisure coefficient dynamically
        beta_l = np.full(n, beta_l0)
        
        # Add all available shifters
        for param_name, param_value in group_params.items():
            if param_name.startswith('beta_l_') and param_name != 'beta_l0':
                # Extract covariate name (e.g., 'age_norm' from 'beta_l_age_norm')
                cov_name = param_name.replace('beta_l_', '')
                
                # Try to find this covariate in the data
                cov_value = self._get_covariate(df, cov_name, n)
                if cov_value is not None:
                    beta_l += param_value * cov_value
        
        # Compute utility
        l_bc = boxcox_transform(l, theta_l)
        c_bc = boxcox_transform(c, theta_c)
        
        U = beta_l * l_bc + beta_c * c_bc
        
        return U
    
    def compute_utility_couples(
        self,
        df: pd.DataFrame,
        consumption_col: str = 'consumption',
        leisure_m_col: str = 'leisure_m',
        leisure_f_col: str = 'leisure_f',
        normalize_c: float = 25000.0,
        normalize_l: float = 45.0,
    ) -> np.ndarray:
        """
        Compute systematic utility for couples.
        
        U = β_lm(X_m) × BC(l_m; θ_lm) + β_lf(X_f) × BC(l_f; θ_lf) + β_c × BC(c; θ_c)
        """
        n = len(df)
        group_params = self.params.get_all_params_for_group('cou')
        
        # Shared parameters
        theta_c = group_params.get('theta_c', 0.5)
        beta_c = group_params.get('beta_c', 1.0)
        
        # Male leisure parameters
        theta_l_m = group_params.get('theta_l_m', 0.5)
        beta_l0_m = group_params.get('beta_l0_m', 0.0)
        
        # Female leisure parameters  
        theta_l_f = group_params.get('theta_l_f', 0.5)
        beta_l0_f = group_params.get('beta_l0_f', 0.0)
        
        # Get values
        c = self._get_consumption(df, consumption_col, normalize_c)
        l_m = self._get_leisure(df, leisure_m_col, normalize_l, suffix='_m')
        l_f = self._get_leisure(df, leisure_f_col, normalize_l, suffix='_f')
        
        # Build male leisure coefficient
        beta_l_m = np.full(n, beta_l0_m)
        for param_name, param_value in group_params.items():
            if param_name.startswith('beta_l_') and param_name.endswith('_m') and 'beta_l0' not in param_name:
                cov_name = param_name.replace('beta_l_', '').replace('_m', '')
                cov_value = self._get_covariate(df, cov_name, n, suffix='_m')
                if cov_value is not None:
                    beta_l_m += param_value * cov_value
        
        # Build female leisure coefficient
        beta_l_f = np.full(n, beta_l0_f)
        for param_name, param_value in group_params.items():
            if param_name.startswith('beta_l_') and param_name.endswith('_f') and 'beta_l0' not in param_name:
                cov_name = param_name.replace('beta_l_', '').replace('_f', '')
                cov_value = self._get_covariate(df, cov_name, n, suffix='_f')
                if cov_value is not None:
                    beta_l_f += param_value * cov_value
        
        # Compute utility
        l_m_bc = boxcox_transform(l_m, theta_l_m)
        l_f_bc = boxcox_transform(l_f, theta_l_f)
        c_bc = boxcox_transform(c, theta_c)
        
        U = beta_l_m * l_m_bc + beta_l_f * l_f_bc + beta_c * c_bc
        
        return U
    
    def _get_consumption(self, df: pd.DataFrame, col: str, normalize: float) -> np.ndarray:
        """Get consumption values from dataframe, trying multiple column names."""
        for candidate in [col, 'c_norm', 'consumption', 'ils_dispy', 'dispy_util']:
            if candidate in df.columns:
                c = df[candidate].values
                # Normalize if not already normalized
                if candidate in ['consumption', 'ils_dispy'] and normalize > 0:
                    c = c / normalize
                return np.clip(c, 1e-6, None)
        
        LOGGER.warning(f"No consumption column found, using 1.0")
        return np.ones(len(df))
    
    def _get_leisure(self, df: pd.DataFrame, col: str, normalize: float, suffix: str = '') -> np.ndarray:
        """Get leisure values from dataframe."""
        # Try direct column
        if col in df.columns:
            return np.clip(df[col].values / normalize if normalize > 0 else df[col].values, 1e-6, None)
        
        # Try computing from hours
        hours_cols = [
            f'hours{suffix}',
            f'lhw{suffix}',
            # common wide-format couple columns
            f'hours_male{suffix}',
            f'hours_female{suffix}',
            f'lhw_male{suffix}',
            f'lhw_female{suffix}',
            # generic fallbacks
            'hours_male',
            'hours_female',
            'lhw_male',
            'lhw_female',
            'hours_m',
            'hours_f',
            'lhw_m',
            'lhw_f',
            'hours',
            'lhw',
        ]
        for hcol in hours_cols:
            if hcol in df.columns:
                hours = df[hcol].values
                # Replace NaN/inf with zeros to avoid propagating NaNs into utilities
                hours = np.nan_to_num(hours, nan=0.0, posinf=0.0, neginf=0.0)
                leisure = 80.0 - hours  # Assume 80 hours total available
                return np.clip(leisure / normalize if normalize > 0 else leisure, 1e-6, None)
        
        LOGGER.warning(f"No leisure column found for suffix '{suffix}', using 1.0")
        return np.ones(len(df))
    
    def _get_covariate(self, df: pd.DataFrame, name: str, n: int, suffix: str = '') -> Optional[np.ndarray]:
        """
        Get a covariate from the dataframe.
        
        Tries multiple naming conventions to find the column.
        """
        # Build list of candidates to try
        candidates = [
            f'{name}{suffix}',
            name,
            f'{name}_norm{suffix}',
            f'{name}_norm',
        ]
        
        # Handle special cases
        if name == 'n_children':
            candidates.extend(['n_children', 'num_children_total', 'dch'])
        elif name == 'age_norm':
            candidates.extend(['age_norm', 'dag_norm', 'age_normalized'])
        elif name == 'age_norm2':
            candidates.extend(['age_norm2', 'age_norm_sq', 'dag_norm2'])
        elif name == 'educL':
            candidates.extend(['educL', 'educ_low', 'deduc1'])
        elif name == 'educH':
            candidates.extend(['educH', 'educ_high', 'deduc3'])
        
        for col in candidates:
            if col in df.columns:
                return df[col].values
        
        # If not found but it's a squared term, try computing it
        if '2' in name or 'sq' in name.lower():
            base_name = name.replace('2', '').replace('_sq', '').replace('sq', '')
            base_val = self._get_covariate(df, base_name, n, suffix)
            if base_val is not None:
                return base_val ** 2
        
        return None


# =============================================================================
# MARGINAL UTILITY COMPUTATIONS
# =============================================================================

def compute_marginal_utility_consumption(
    c: np.ndarray, 
    beta_c: float, 
    theta_c: float
) -> np.ndarray:
    """
    Marginal utility of consumption: ∂U/∂c = β_c × c^(θ_c - 1)
    """
    return beta_c * d_boxcox_dx(c, theta_c)


def compute_marginal_utility_leisure(
    l: np.ndarray,
    beta_l: np.ndarray,
    theta_l: float
) -> np.ndarray:
    """
    Marginal utility of leisure: ∂U/∂l = β_l(X) × l^(θ_l - 1)
    """
    return beta_l * d_boxcox_dx(l, theta_l)


def compute_mrs(
    c: np.ndarray,
    l: np.ndarray,
    beta_l: np.ndarray,
    beta_c: float,
    theta_l: float,
    theta_c: float
) -> np.ndarray:
    """
    Marginal rate of substitution: MRS = MUL / MUC
    """
    mul = compute_marginal_utility_leisure(l, beta_l, theta_l)
    muc = compute_marginal_utility_consumption(c, beta_c, theta_c)
    
    # Avoid division by zero
    muc = np.where(np.abs(muc) < 1e-10, 1e-10, muc)
    
    return mul / muc


def compute_beta_l_at_median(
    parsed_params: ParsedParameters,
    group: str,
    suffix: str = '',
    median_shifters: Dict[str, float] = None,
) -> float:
    """
    Compute the full leisure coefficient β_l(X) at median/mode shifter values.
    
    β_l(X) = β_l0 + Σ β_l_k * X_k
    
    where X_k are the shifter variables evaluated at their median (continuous)
    or mode (categorical) values.
    
    Parameters
    ----------
    parsed_params : ParsedParameters
        Parsed parameter structure
    group : str
        Group identifier (sm, sf, cou)
    suffix : str
        '_m' or '_f' for couples
    median_shifters : Dict[str, float], optional
        Pre-computed median/mode values for shifters.
        If None, uses default values (0 for normalized continuous, 0 for dummies)
        
    Returns
    -------
    float
        β_l evaluated at median characteristics
        
    Notes
    -----
    Default median values assume:
    - Normalized continuous variables (age_norm, age_norm2): 0 (centered at mean)
    - Dummy variables (educL, educH, region dummies): 0 (reference category)
    - Count variables (n_children): group-specific defaults
    
    For accurate results, pass actual median_shifters computed from the data.
    """
    params = parsed_params.get_all_params_for_group(group)
    
    # Get beta_l0
    beta_l0_key = f'beta_l0{suffix}' if suffix else 'beta_l0'
    beta_l = params.get(beta_l0_key, 0.0)
    
    # Default median values for common shifters
    # These assume normalized/centered variables
    default_medians = {
        'age_norm': 0.0,      # Normalized age (centered)
        'age_norm2': 0.0,     # Squared normalized age
        'n_children': 0.5,    # Typical median children
        'educL': 0.0,         # Low education dummy (reference = medium)
        'educH': 0.0,         # High education dummy (reference = medium)
        'married': 0.0,       # Married dummy
        'urban': 0.0,         # Urban dummy
        'region_1': 0.0,      # Region dummies
        'region_2': 0.0,
        'region_3': 0.0,
    }
    
    # Use provided medians or defaults
    shifter_values = median_shifters if median_shifters else default_medians
    
    # Find all beta_l_ shifter coefficients for this group
    for key, coef in params.items():
        # Match beta_l_* pattern (but not beta_l0)
        if 'beta_l_' in key and 'beta_l0' not in key:
            # Extract shifter name
            # Handle both 'beta_l_age_norm' and 'beta_l_age_norm_m' formats
            shifter_name = key.replace('beta_l_', '')
            if suffix and shifter_name.endswith(suffix):
                shifter_name = shifter_name[:-len(suffix)]
            
            # Get shifter value (median/mode)
            shifter_val = shifter_values.get(shifter_name, 0.0)
            
            # Add contribution: β_l_k * X_k
            beta_l += coef * shifter_val
    
    return beta_l


def get_default_median_shifters(group: str) -> Dict[str, float]:
    """
    Get default median/mode values for shifters by group.
    
    These are reasonable defaults for French data.
    For accurate analysis, compute actual medians from the estimation data.
    
    Parameters
    ----------
    group : str
        Group identifier (sm, sf, cou_m, cou_f)
        
    Returns
    -------
    Dict[str, float]
        Median/mode values for each shifter
    """
    # Base defaults (normalized variables centered at 0)
    defaults = {
        'age_norm': 0.0,      # Age normalized to mean
        'age_norm2': 0.0,     # Squared (at mean, this is ~variance)
        'educL': 0.0,         # Reference = medium education
        'educH': 0.0,         # Reference = medium education
        'n_children': 0.0,    # Median children (varies by group)
    }
    
    # Group-specific adjustments
    if group in ['sm', 'cou_m']:
        # Males: typically fewer children in household responsibility
        defaults['n_children'] = 0.3
    elif group in ['sf', 'cou_f']:
        # Females: slightly higher median for children
        defaults['n_children'] = 0.5
      # For couples, children effect is shared
    if group in ['cou_m', 'cou_f']:
        defaults['n_children'] = 0.8  # Couples more likely to have children
    
    return defaults


def compute_median_shifters_from_data(
    df: pd.DataFrame,
    shifter_names: List[str],
    suffix: str = '',
) -> Dict[str, float]:
    """
    Compute actual median/mode values for shifter variables from data.
    
    For continuous variables (age_norm, age_norm2, n_children), computes median.
    For binary/categorical variables (educL, educH, etc.), computes mode.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataset with shifter columns
    shifter_names : List[str]
        Names of shifter variables to compute medians for
    suffix : str
        Suffix for column names (e.g., '_m' for males in couples)
        
    Returns
    -------
    Dict[str, float]
        Median/mode values for each shifter
    """
    medians = {}
    
    # Binary/categorical variables (use mode)
    binary_vars = {'educL', 'educH', 'married', 'urban', 'region_1', 'region_2', 'region_3'}
    
    for shifter in shifter_names:
        # Try with and without suffix
        col_name = f"{shifter}{suffix}" if suffix else shifter
        if col_name not in df.columns:
            col_name = shifter  # Fall back to non-suffixed
        
        if col_name in df.columns:
            values = df[col_name].dropna()
            if len(values) > 0:
                # Use mode for binary, median for continuous
                if shifter in binary_vars:
                    medians[shifter] = float(values.mode().iloc[0]) if len(values.mode()) > 0 else 0.0
                else:
                    medians[shifter] = float(values.median())
            else:
                medians[shifter] = 0.0
        else:
            # Use default
            medians[shifter] = 0.0
    
    return medians


def compute_negative_mu_diagnostics(
    df: pd.DataFrame,
    utility_computer: DynamicUtilityComputer,
    group: str,
    consumption_col: str = 'consumption',
    leisure_col: str = 'leisure',
    is_couples: bool = False,
    suffix: str = '',
) -> Dict[str, Any]:
    """
    Compute diagnostics for negative marginal utilities at chosen alternatives.
    
    For the RURO Box-Cox utility specification:
    MUC = β_c * c^(θ_c - 1)
    MUL = β_l(X) * l^(θ_l - 1)
    
    MUC < 0 when β_c < 0 (since c^(θ_c-1) > 0 for positive c)
    MUL < 0 when β_l(X) < 0 for an individual's characteristics
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataset with individual observations
    utility_computer : DynamicUtilityComputer
        Utility computer with parsed parameters
    group : str
        Group identifier (sm, sf, cou)
    consumption_col : str
        Column name for consumption
    leisure_col : str
        Column name for leisure
    is_couples : bool
        Whether this is couples data
    suffix : str
        '_m' or '_f' for couples
        
    Returns
    -------
    Dict with MU statistics and negative MU counts
    """
    results = {
        "n_individuals": 0,
        "n_negative_muc": 0,
        "n_negative_mul": 0,
        "pct_negative_muc": np.nan,
        "pct_negative_mul": np.nan,
        "muc_mean": np.nan,
        "muc_median": np.nan,
        "muc_min": np.nan,
        "muc_max": np.nan,
        "mul_mean": np.nan,
        "mul_median": np.nan,
        "mul_min": np.nan,
        "mul_max": np.nan,
    }
    
    if df is None or len(df) == 0:
        return results
    
    # Get parameters
    params = utility_computer.params.get_all_params_for_group(group)
    
    # Get consumption parameters
    beta_c = params.get('beta_c', 1.0)
    theta_c = params.get('theta_c', 0.5)
    theta_l = params.get(f'theta_l{suffix}', params.get('theta_l', 0.5))
    beta_l0 = params.get(f'beta_l0{suffix}', params.get('beta_l0', 0.0))
    
    # Filter to observed/chosen alternatives
    obs_mask = None
    for col in ["is_chosen", "is_observed", "obs", "chosen"]:
        if col in df.columns:
            obs_mask = df[col] == 1
            break
    
    if obs_mask is None:
        LOGGER.warning(f"No observed choice indicator found for group {group}")
        return results
    
    obs_df = df[obs_mask].copy()
    
    if len(obs_df) == 0:
        return results
    
    results["n_individuals"] = len(obs_df)
    n = len(obs_df)
    
    # Get consumption values
    c = utility_computer._get_consumption(obs_df, consumption_col, normalize=1.0)  # Don't normalize for MU calc
    
    # Compute MUC
    muc = compute_marginal_utility_consumption(c, beta_c, theta_c)
    results["n_negative_muc"] = int(np.sum(muc < 0))
    results["pct_negative_muc"] = 100.0 * results["n_negative_muc"] / len(muc) if len(muc) > 0 else np.nan
    results["muc_mean"] = float(np.mean(muc))
    results["muc_median"] = float(np.median(muc))
    results["muc_min"] = float(np.min(muc))
    results["muc_max"] = float(np.max(muc))
    
    # Compute β_l(X) for each individual
    beta_l = np.full(n, beta_l0)
    group_params = params
    
    # Add shifters dynamically
    for param_name, param_value in group_params.items():
        # Match pattern: beta_l_{covariate}{suffix}
        if param_name.startswith('beta_l_') and 'beta_l0' not in param_name:
            if suffix and not param_name.endswith(suffix):
                continue
            
            cov_name = param_name.replace('beta_l_', '').replace(suffix, '')
            cov_value = utility_computer._get_covariate(obs_df, cov_name, n, suffix)
            if cov_value is not None:
                beta_l += param_value * cov_value
    
    # Get leisure values
    l = utility_computer._get_leisure(obs_df, leisure_col, normalize=1.0, suffix=suffix)
    
    # Compute MUL
    mul = compute_marginal_utility_leisure(l, beta_l, theta_l)
    results["n_negative_mul"] = int(np.sum(mul < 0))
    results["pct_negative_mul"] = 100.0 * results["n_negative_mul"] / len(mul) if len(mul) > 0 else np.nan
    results["mul_mean"] = float(np.mean(mul))
    results["mul_median"] = float(np.median(mul))
    results["mul_min"] = float(np.min(mul))
    results["mul_max"] = float(np.max(mul))
    
    return results


def compute_all_mu_diagnostics(
    df_sm: pd.DataFrame,
    df_sf: pd.DataFrame,
    df_cou: pd.DataFrame,
    utility_computer: DynamicUtilityComputer,
) -> Dict[str, Dict[str, Any]]:
    """
    Compute MU diagnostics for all demographic groups.
    """
    results = {}
    
    if df_sm is not None:
        results['sm'] = compute_negative_mu_diagnostics(
            df_sm, utility_computer, 'sm'
        )
    
    if df_sf is not None:
        results['sf'] = compute_negative_mu_diagnostics(
            df_sf, utility_computer, 'sf'
        )
    
    if df_cou is not None:
        results['cou_m'] = compute_negative_mu_diagnostics(
            df_cou, utility_computer, 'cou', suffix='_m'
        )
        results['cou_f'] = compute_negative_mu_diagnostics(
            df_cou, utility_computer, 'cou', suffix='_f'
        )
    
    return results


# =============================================================================
# FIT DIAGNOSTICS
# =============================================================================

def compute_fit_diagnostics(
    df: pd.DataFrame,
    utility_computer: DynamicUtilityComputer,
    group: str,
    hours_col: str = 'lhw',
    is_couples: bool = False,
) -> Dict[str, Any]:
    """
    Compute fit diagnostics comparing predicted vs observed outcomes.
    
    This function is fully automatic - it uses whatever utility function
    is defined by the parameters.
    """
    results = {
        'participation_rate_observed': np.nan,
        'participation_rate_predicted': np.nan,
        'mean_hours_observed': np.nan,
        'mean_hours_predicted': np.nan,
        'hours_distribution_observed': {},
        'hours_distribution_predicted': {},
    }
    
    # Find observed choice indicator
    obs_col = None
    for col in ['is_chosen', 'is_observed', 'obs', 'chosen']:
        if col in df.columns:
            obs_col = col
            break
    
    if obs_col is None:
        LOGGER.warning("No observed choice indicator found")
        return results
    
    # Find household/individual ID column
    id_col = None
    for col in ['idhh', 'idperson', 'hh_id', 'id']:
        if col in df.columns:
            id_col = col
            break
    
    if id_col is None:
        LOGGER.warning("No ID column found")
        return results
    
    if hours_col not in df.columns:
        LOGGER.warning(f"Hours column '{hours_col}' not found for group '{group}', predictions may be zero/NaN")
    
    # Get observed choices
    obs_mask = df[obs_col] == 1
    obs_df = df[obs_mask]
    
    if len(obs_df) == 0:
        return results
    
    # Observed statistics
    obs_hours = obs_df[hours_col].values if hours_col in obs_df.columns else np.zeros(len(obs_df))
    results['participation_rate_observed'] = float((obs_hours > 0).mean())
    results['mean_hours_observed'] = float(obs_hours[obs_hours > 0].mean()) if (obs_hours > 0).any() else 0.0
    
    # Hours distribution
    bins = [0, 5, 15, 25, 35, 45, 55, 65, 100]
    bin_labels = ['0', '1-10', '11-20', '21-30', '31-40', '41-50', '51-60', '60+']
    obs_binned = pd.cut(obs_hours, bins=bins, labels=bin_labels, include_lowest=True)
    obs_vc = obs_binned.value_counts()
    results['hours_distribution_observed'] = (obs_vc / obs_vc.sum()).to_dict()
    
    # Compute utilities for predicted statistics
    try:
        if is_couples:
            V = utility_computer.compute_utility_couples(df)
        else:
            V = utility_computer.compute_utility_singles(df, group)
        
        # Compute expected hours per individual
        unique_ids = df[id_col].unique()
        expected_hours = []
        participation_probs = []
        
        for uid in unique_ids:
            mask = df[id_col] == uid
            V_i = np.asarray(V[mask], dtype=float)
            h_raw = df.loc[mask, hours_col].values if hours_col in df.columns else np.zeros(mask.sum())
            # Coerce hours to float and replace non-finite with zero
            try:
                h_i = pd.to_numeric(h_raw, errors='coerce').to_numpy()
            except Exception:
                h_i = np.array(h_raw, dtype=float)
            h_i = np.nan_to_num(h_i, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Drop non-finite utilities; if none left, fall back to zeros
            finite_mask = np.isfinite(V_i)
            if not finite_mask.any():
                V_i = np.zeros_like(h_i, dtype=float)
            else:
                V_i = V_i[finite_mask]
                h_i = h_i[finite_mask]
            
            # Softmax probabilities
            if SCIPY_AVAILABLE:
                log_denom = logsumexp(V_i)
                probs = np.exp(V_i - log_denom)
            else:
                max_V = np.max(V_i)
                exp_shift = np.exp(V_i - max_V)
                sum_exp = np.sum(exp_shift)
                if sum_exp == 0 or not np.isfinite(sum_exp):
                    probs = np.full_like(V_i, 1.0 / len(V_i))
                else:
                    probs = exp_shift / sum_exp
            
            # Expected hours
            e_h = np.sum(probs * h_i)
            expected_hours.append(e_h)
            
            # Participation probability
            p_work = np.sum(probs[h_i > 0])
            participation_probs.append(p_work)
        
        if len(expected_hours) > 0:
            results['participation_rate_predicted'] = float(np.mean(participation_probs))
            expected_hours_arr = np.array(expected_hours)
            results['mean_hours_predicted'] = float(expected_hours_arr[expected_hours_arr > 0].mean()) \
                if (expected_hours_arr > 0).any() else 0.0
            
            # Predicted hours distribution
            pred_binned = pd.cut(expected_hours_arr, bins=bins, labels=bin_labels, include_lowest=True)
            pred_vc = pred_binned.value_counts()
            results['hours_distribution_predicted'] = (pred_vc / pred_vc.sum()).to_dict()
    
    except Exception as e:
        LOGGER.warning(f"Error computing predicted statistics: {e}")
    
    return results


# =============================================================================
# PLOTTING FUNCTIONS
# =============================================================================

def plot_fit_comparison(
    fit_results: Dict[str, Dict[str, Any]],
    output_dir: Path,
    prefix: str = '',
) -> Dict[str, Path]:
    """Generate fit comparison plots (participation rates, mean hours)."""
    if not MATPLOTLIB_AVAILABLE:
        LOGGER.warning("Matplotlib not available, skipping plots")
        return {}
    
    plot_paths = {}
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    group_labels = {
        'sm': 'SM', 'sf': 'SF', 'cou_m': 'CM', 'cou_f': 'CF'
    }
    
    groups = list(fit_results.keys())
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


def plot_marginal_utilities(
    parsed_params: ParsedParameters,
    output_dir: Path,
) -> Dict[str, Path]:
    """Plot marginal utility curves."""
    if not MATPLOTLIB_AVAILABLE:
        return {}
    
    output_dir = Path(output_dir)
    plot_paths = {}
    
    c_grid = np.linspace(0.1, 3.0, 200)
    l_grid = np.linspace(0.1, 2.5, 200)
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    colors = {'sm': '#1f77b4', 'sf': '#ff7f0e', 'cou': '#2ca02c'}
    
    # MUC plot
    ax = axes[0]
    for group in parsed_params.preference_groups:
        params = parsed_params.get_all_params_for_group(group)
        beta_c = params.get('beta_c', 1.0)
        theta_c = params.get('theta_c', 0.5)
        
        muc = compute_marginal_utility_consumption(c_grid, beta_c, theta_c)
        ax.plot(c_grid, muc, label=group, color=colors.get(group, 'gray'), linewidth=2)
    
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax.set_xlabel('Consumption (normalized)')
    ax.set_ylabel('MUC')
    ax.set_title('Marginal Utility of Consumption')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # MUL plot
    ax = axes[1]
    for group in parsed_params.preference_groups:
        params = parsed_params.get_all_params_for_group(group)
        theta_l = params.get('theta_l', params.get('theta_l_m', 0.5))
        beta_l0 = params.get('beta_l0', params.get('beta_l0_m', 0.0))
        
        beta_l = np.full_like(l_grid, beta_l0)
        mul = compute_marginal_utility_leisure(l_grid, beta_l, theta_l)
        ax.plot(l_grid, mul, label=group, color=colors.get(group, 'gray'), linewidth=2)
    
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax.set_xlabel('Leisure (normalized)')
    ax.set_ylabel('MUL')
    ax.set_title('Marginal Utility of Leisure (at median)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    path = output_dir / 'marginal_utilities.png'
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    plot_paths['marginal_utilities'] = path
    
    return plot_paths


def plot_mu_diagnostics(
    mu_results: Dict[str, Dict[str, Any]],
    output_dir: Path,
) -> Dict[str, Path]:
    """Plot marginal utility diagnostic summary."""
    if not MATPLOTLIB_AVAILABLE:
        return {}
    
    output_dir = Path(output_dir)
    plot_paths = {}
    
    groups = list(mu_results.keys())
    if not groups:
        return {}
    
    group_labels = {
        'sm': 'SM', 'sf': 'SF', 'cou_m': 'CM', 'cou_f': 'CF'
    }
    
    # Bar chart of negative MU percentages
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    x = np.arange(len(groups))
    width = 0.6
    
    # Negative MUC
    ax = axes[0]
    pct_neg_muc = [mu_results[g].get('pct_negative_muc', 0) or 0 for g in groups]
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
    pct_neg_mul = [mu_results[g].get('pct_negative_mul', 0) or 0 for g in groups]
    colors_mul = ['#d62728' if p > 5 else '#2ca02c' for p in pct_neg_mul]
    ax.bar(x, pct_neg_mul, width, color=colors_mul, edgecolor='white')
    ax.set_ylabel('% with Negative MUL')
    ax.set_title('Negative Marginal Utility of Leisure')
    ax.set_xticks(x)
    ax.set_xticklabels([group_labels.get(g, g) for g in groups])
    ax.axhline(y=5, color='k', linestyle='--', alpha=0.5, label='5% threshold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    path = output_dir / 'negative_mu_diagnostics.png'
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    plot_paths['negative_mu'] = path
    
    return plot_paths


def plot_mu_comparison(
    parsed_params: ParsedParameters,
    output_dir: Path,
    prefix: str = '',
    grid_points: int = 200,
    df_sm: pd.DataFrame = None,
    df_sf: pd.DataFrame = None,
    df_cou: pd.DataFrame = None,
) -> Dict[str, Path]:
    """
    Generate separate MUC and MUL comparison plots across all groups.
    
    Creates:
    1. muc_comparison.png - MUC curves for all groups on same axes
    2. mul_comparison.png - MUL curves for all groups on same axes
    3. Individual {group}_mu.png plots for each group
    
    Parameters
    ----------
    parsed_params : ParsedParameters
        Parsed parameter structure
    output_dir : Path
        Directory to save plots
    prefix : str
        Prefix for filenames (e.g., 'vw_')
    grid_points : int
        Resolution of grid
        
    Returns
    -------
    Dict[str, Path]
        Paths to generated plots
    """
    if not MATPLOTLIB_AVAILABLE:
        return {}
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_paths = {}
    
    c_grid = np.linspace(0.05, 2.5, grid_points)
    l_grid = np.linspace(0.1, 2.5, grid_points)
    
    # Define colors for each group
    colors = {
        'sm': '#1f77b4',        # blue
        'sf': '#ff7f0e',        # orange
        'cou_m': '#2ca02c',     # green
        'cou_f': '#d62728',     # red
        'cou': '#9467bd',       # purple (for shared couple params)
    }
    
    group_labels = {
        'sm': 'Single Males',
        'sf': 'Single Females',
        'cou_m': 'Males in Couples',
        'cou_f': 'Females in Couples',
        'cou': 'Couples (shared)',
    }
    
    # =========================================================================
    # 1. MUC Comparison Plot
    # =========================================================================
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Singles have their own beta_c, theta_c
    for group in ['sm', 'sf']:
        if group not in parsed_params.params_by_group:
            continue
        params = parsed_params.get_all_params_for_group(group)
        beta_c = params.get('beta_c', 1.0)
        theta_c = params.get('theta_c', 0.5)
        
        muc = compute_marginal_utility_consumption(c_grid, beta_c, theta_c)
        ax.plot(c_grid, muc, label=group_labels[group], color=colors[group], lw=2)
    
    # Couples share beta_c, theta_c
    if 'cou' in parsed_params.params_by_group:
        params_cou = parsed_params.get_all_params_for_group('cou')
        beta_c_cou = params_cou.get('beta_c', 1.0)
        theta_c_cou = params_cou.get('theta_c', 0.5)
        
        muc_cou = compute_marginal_utility_consumption(c_grid, beta_c_cou, theta_c_cou)
        ax.plot(c_grid, muc_cou, label='Couples (shared)', color=colors['cou'], lw=2, ls='--')
    
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
    
    # =========================================================================
    # 2. MUL Comparison Plot (using full β_l at median shifter values)
    # =========================================================================
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Track beta_l values for subtitle
    beta_l_info = []
    
    # Singles
    for group in ['sm', 'sf']:
        if group not in parsed_params.params_by_group:
            continue
        params = parsed_params.get_all_params_for_group(group)
        theta_l = params.get('theta_l', 0.5)
        
        # Get shifter names for this group
        shifter_names = parsed_params.leisure_shifters.get(group, [])
        
        # Compute median shifters from data if available, else use defaults
        df_group = df_sm if group == 'sm' else df_sf
        if df_group is not None and len(shifter_names) > 0:
            median_shifters = compute_median_shifters_from_data(df_group, shifter_names, '')
        else:
            median_shifters = get_default_median_shifters(group)
        
        beta_l_median = compute_beta_l_at_median(parsed_params, group, '', median_shifters)
        beta_l_info.append(f"{group}: β_l={beta_l_median:.3f}")
        
        beta_l = np.full_like(l_grid, beta_l_median)
        mul = compute_marginal_utility_leisure(l_grid, beta_l, theta_l)
        ax.plot(l_grid, mul, label=f"{group_labels[group]} (β_l={beta_l_median:.2f})", 
                color=colors[group], lw=2)
    
    # Couples - males and females separately
    if 'cou' in parsed_params.params_by_group:
        params_cou = parsed_params.get_all_params_for_group('cou')
        
        # Males in couples
        theta_l_m = params_cou.get('theta_l_m', params_cou.get('theta_l', 0.5))
        shifter_names_m = parsed_params.leisure_shifters.get('cou', [])
        if df_cou is not None and len(shifter_names_m) > 0:
            median_shifters_m = compute_median_shifters_from_data(df_cou, shifter_names_m, '_m')
        else:
            median_shifters_m = get_default_median_shifters('cou_m')
        beta_l_median_m = compute_beta_l_at_median(parsed_params, 'cou', '_m', median_shifters_m)
        beta_l_info.append(f"cou_m: β_l={beta_l_median_m:.3f}")
        
        beta_l_m = np.full_like(l_grid, beta_l_median_m)
        mul_m = compute_marginal_utility_leisure(l_grid, beta_l_m, theta_l_m)
        ax.plot(l_grid, mul_m, label=f"{group_labels['cou_m']} (β_l={beta_l_median_m:.2f})", 
                color=colors['cou_m'], lw=2)
        
        # Females in couples
        theta_l_f = params_cou.get('theta_l_f', params_cou.get('theta_l', 0.5))
        if df_cou is not None and len(shifter_names_m) > 0:
            median_shifters_f = compute_median_shifters_from_data(df_cou, shifter_names_m, '_f')
        else:
            median_shifters_f = get_default_median_shifters('cou_f')
        beta_l_median_f = compute_beta_l_at_median(parsed_params, 'cou', '_f', median_shifters_f)
        beta_l_info.append(f"cou_f: β_l={beta_l_median_f:.3f}")
        
        beta_l_f = np.full_like(l_grid, beta_l_median_f)
        mul_f = compute_marginal_utility_leisure(l_grid, beta_l_f, theta_l_f)
        ax.plot(l_grid, mul_f, label=f"{group_labels['cou_f']} (β_l={beta_l_median_f:.2f})", 
                color=colors['cou_f'], lw=2)
    
    ax.axhline(0, color='black', lw=1, ls='--', alpha=0.6)
    ax.set_xlabel('Normalized Leisure (l/l̄)')
    ax.set_ylabel('MUL = ∂U/∂l')
    ax.set_title('Marginal Utility of Leisure by Group\n(at median characteristics)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    mul_path = output_dir / f'{prefix}mul_comparison.png'
    fig.tight_layout()
    fig.savefig(mul_path, dpi=150)
    plt.close(fig)
    plot_paths['mul_comparison'] = mul_path
      # =========================================================================
    # 3. Individual Group Plots (MUC + MUL combined)
    # =========================================================================
    all_groups = []
    if 'sm' in parsed_params.params_by_group:
        all_groups.append(('sm', '', parsed_params.get_all_params_for_group('sm')))
    if 'sf' in parsed_params.params_by_group:
        all_groups.append(('sf', '', parsed_params.get_all_params_for_group('sf')))
    if 'cou' in parsed_params.params_by_group:
        params_cou = parsed_params.get_all_params_for_group('cou')
        # Add male and female in couples separately
        all_groups.append(('cou_m', '_m', {
            'beta_c': params_cou.get('beta_c', 1.0),
            'theta_c': params_cou.get('theta_c', 0.5),
            'theta_l': params_cou.get('theta_l_m', 0.5),
        }))
        all_groups.append(('cou_f', '_f', {
            'beta_c': params_cou.get('beta_c', 1.0),
            'theta_c': params_cou.get('theta_c', 0.5),
            'theta_l': params_cou.get('theta_l_f', 0.5),
        }))
    
    for group, suffix, params in all_groups:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        beta_c = params.get('beta_c', 1.0)
        theta_c = params.get('theta_c', 0.5)
        theta_l = params.get('theta_l', 0.5)
        
        # Compute full beta_l at median shifter values
        base_group = 'cou' if group.startswith('cou') else group
        shifter_names = parsed_params.leisure_shifters.get(base_group, [])
        
        # Get appropriate data frame and compute medians
        if group == 'sm' and df_sm is not None and len(shifter_names) > 0:
            median_shifters = compute_median_shifters_from_data(df_sm, shifter_names, suffix)
        elif group == 'sf' and df_sf is not None and len(shifter_names) > 0:
            median_shifters = compute_median_shifters_from_data(df_sf, shifter_names, suffix)
        elif group.startswith('cou') and df_cou is not None and len(shifter_names) > 0:
            median_shifters = compute_median_shifters_from_data(df_cou, shifter_names, suffix)
        else:
            median_shifters = get_default_median_shifters(group)
            
        beta_l_median = compute_beta_l_at_median(parsed_params, base_group, suffix, median_shifters)
        
        # MUC
        muc = compute_marginal_utility_consumption(c_grid, beta_c, theta_c)
        ax1.plot(c_grid, muc, color=colors.get(group, 'gray'), lw=2)
        ax1.axhline(0, color='black', lw=1, ls='--', alpha=0.6)
        ax1.fill_between(c_grid, muc, 0, where=(muc > 0), color='green', alpha=0.2)
        ax1.fill_between(c_grid, muc, 0, where=(muc < 0), color='red', alpha=0.2)
        ax1.set_xlabel('Normalized Consumption')
        ax1.set_ylabel('MUC (∂U/∂c)')
        ax1.set_title(f'Marginal Utility of Consumption\n(β_c={beta_c:.3f}, θ_c={theta_c:.3f})')
        ax1.grid(True, alpha=0.3)
        
        # MUL with full beta_l at median characteristics
        beta_l = np.full_like(l_grid, beta_l_median)
        mul = compute_marginal_utility_leisure(l_grid, beta_l, theta_l)
        ax2.plot(l_grid, mul, color=colors.get(group, 'gray'), lw=2)
        ax2.axhline(0, color='black', lw=1, ls='--', alpha=0.6)
        ax2.fill_between(l_grid, mul, 0, where=(mul > 0), color='green', alpha=0.2)
        ax2.fill_between(l_grid, mul, 0, where=(mul < 0), color='red', alpha=0.2)
        ax2.set_xlabel('Normalized Leisure')
        ax2.set_ylabel('MUL (∂U/∂l)')
        ax2.set_title(f'Marginal Utility of Leisure\n(β_l={beta_l_median:.3f} at median X, θ_l={theta_l:.3f})')
        ax2.grid(True, alpha=0.3)
        
        fig.suptitle(f'{group_labels.get(group, group)}', fontsize=12, fontweight='bold')
        
        group_path = output_dir / f'{prefix}{group}_mu.png'
        fig.tight_layout()
        fig.savefig(group_path, dpi=150)
        plt.close(fig)
        plot_paths[f'{group}_mu'] = group_path
    
    return plot_paths


def plot_utility_contours_all_groups(
    parsed_params: ParsedParameters,
    output_dir: Path,
    prefix: str = '',
    grid_points: int = 100,
    utility_percentiles: List[float] = [10, 25, 50, 75, 99],
) -> Dict[str, Path]:
    """
    Generate utility contour plots for all 4 demographic groups.
    
    Creates separate plots for:
    - Single Males (sm)
    - Single Females (sf)
    - Males in Couples (cou_m)
    - Females in Couples (cou_f)
    
    Parameters
    ----------
    parsed_params : ParsedParameters
        Parsed parameter structure
    output_dir : Path
        Directory to save plots
    prefix : str
        Prefix for filenames
    grid_points : int
        Resolution of grid
    utility_percentiles : List[float]
        Percentile levels for contour lines
        
    Returns
    -------
    Dict[str, Path]
        Paths to generated plots
    """
    if not MATPLOTLIB_AVAILABLE:
        return {}
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_paths = {}
    
    group_labels = {
        'sm': 'Single Males',
        'sf': 'Single Females',
        'cou_m': 'Males in Couples',
        'cou_f': 'Females in Couples',
    }
    
    c_range = (0.05, 2.5)
    l_range = (0.1, 2.5)
    
    c_grid = np.linspace(c_range[0], c_range[1], grid_points)
    l_grid = np.linspace(l_range[0], l_range[1], grid_points)
    C, L = np.meshgrid(c_grid, l_grid)
    
    # Build list of groups to process
    groups_to_plot = []
    
    # Singles
    for g in ['sm', 'sf']:
        if g in parsed_params.params_by_group:
            params = parsed_params.get_all_params_for_group(g)
            groups_to_plot.append((g, {
                'beta_c': params.get('beta_c', 1.0),
                'theta_c': params.get('theta_c', 0.5),
                'beta_l0': params.get('beta_l0', 0.0),
                'theta_l': params.get('theta_l', 0.5),
            }))
    
    # Couples - separate male and female
    if 'cou' in parsed_params.params_by_group:
        params_cou = parsed_params.get_all_params_for_group('cou')
        
        # Males in couples
        groups_to_plot.append(('cou_m', {
            'beta_c': params_cou.get('beta_c', 1.0),
            'theta_c': params_cou.get('theta_c', 0.5),
            'beta_l0': params_cou.get('beta_l0_m', 0.0),
            'theta_l': params_cou.get('theta_l_m', 0.5),
        }))
        
        # Females in couples
        groups_to_plot.append(('cou_f', {
            'beta_c': params_cou.get('beta_c', 1.0),
            'theta_c': params_cou.get('theta_c', 0.5),
            'beta_l0': params_cou.get('beta_l0_f', 0.0),
            'theta_l': params_cou.get('theta_l_f', 0.5),
        }))
    
    for group, params in groups_to_plot:
        try:
            theta_c = params['theta_c']
            theta_l = params['theta_l']
            beta_c = params['beta_c']
            beta_l0 = params['beta_l0']
            
            # Compute utility on grid
            c_bc = boxcox_transform(C, theta_c)
            l_bc = boxcox_transform(L, theta_l)
            U = beta_l0 * l_bc + beta_c * c_bc
            
            # Get finite values
            finite_mask = np.isfinite(U)
            if not finite_mask.any():
                LOGGER.warning(f"No finite utility values for {group}")
                continue
            
            # Compute percentile-based contour levels
            U_flat = U[finite_mask].flatten()
            levels = np.percentile(U_flat, utility_percentiles)
            levels = np.unique(levels)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Filled contours
            cf = ax.contourf(C, L, U, levels=20, cmap='RdYlGn', alpha=0.7)
            plt.colorbar(cf, ax=ax, label='Utility')
            
            # Contour lines at percentile levels
            cs = ax.contour(C, L, U, levels=levels, colors='black', linewidths=1.0)
            
            # Label contours with percentile info
            fmt_dict = {lev: f'{utility_percentiles[i]}%' 
                       for i, lev in enumerate(levels) if i < len(utility_percentiles)}
            ax.clabel(cs, inline=True, fontsize=9, fmt=fmt_dict)
            
            # Mark median point
            c_med = np.median(c_grid)
            l_med = np.median(l_grid)
            ax.scatter([c_med], [l_med], color='red', s=80, marker='x',
                      linewidths=2, zorder=5, label='Grid median')
            
            ax.set_xlabel('Normalized Consumption (c/c̄)')
            ax.set_ylabel('Normalized Leisure (l/l̄)')
            ax.set_title(f'Utility Indifference Curves\n{group_labels.get(group, group)}')
            ax.legend(loc='upper right')
            ax.grid(True, alpha=0.3)
            
            # Save
            output_path = output_dir / f'{prefix}{group}_contours.png'
            fig.tight_layout()
            fig.savefig(output_path, dpi=150)
            plt.close(fig)
            
            plot_paths[f'{group}_contours'] = output_path
            LOGGER.info(f"  Saved contour plot: {output_path.name}")
            
        except Exception as e:
            LOGGER.error(f"Error generating contour for {group}: {e}")
            import traceback
            traceback.print_exc()
    
    return plot_paths


# =============================================================================
# ELASTICITY COMPUTATION
# =============================================================================

def compute_structural_elasticities(parsed_params: ParsedParameters) -> pd.DataFrame:
    """
    Compute structural labor supply elasticities based on preference parameters.
    
    These are approximations using the Box-Cox utility structure:
    - Hicksian (compensated) elasticity ≈ 1 - θ_l
    - Marshallian (uncompensated) adds income effect
    """
    rows = []
    group_labels = {
        'sm': 'Single Males', 'sf': 'Single Females',
        'cou_m': 'Males in Couples', 'cou_f': 'Females in Couples'
    }
    
    for group in parsed_params.preference_groups:
        params = parsed_params.get_all_params_for_group(group)
        
        if group == 'cou':
            # Handle couples - male
            theta_l_m = params.get('theta_l_m', 0.5)
            theta_c = params.get('theta_c', 0.5)
            beta_l0_m = params.get('beta_l0_m', 0.0)
            beta_c = params.get('beta_c', 1.0)
            
            hicksian_m = 1 - theta_l_m
            marshallian_m = hicksian_m - 0.1  # Simplified income effect
            
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
            theta_l_f = params.get('theta_l_f', 0.5)
            beta_l0_f = params.get('beta_l0_f', 0.0)
            
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
            # Singles
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
        
        # MUC at median consumption (normalized to 1)
        muc_median = beta_c * (1.0 ** (theta_c - 1)) if beta_c > 0 else beta_c
        
        # C where MUC = 1 (if possible)
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
        
        group_name = 'Couples (shared)' if group == 'cou' else ('Single Males' if group == 'sm' else 'Single Females')
        
        rows.append({
            'Group': group_name,
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
# HTML REPORT GENERATION
# =============================================================================

def generate_html_report(
    parsed_params: ParsedParameters,
    fit_results: Dict[str, Dict[str, Any]],
    output_path: Path,
    fit_stats: Dict[str, float] = None,
    plot_paths: Dict[str, Path] = None,
    mu_results: Dict[str, Dict[str, Any]] = None,
    elasticities_df: pd.DataFrame = None,
    muc_analysis: List[Dict[str, Any]] = None,
    bounds_info: Dict[str, Any] = None,
    param_bounds: Dict[str, Tuple[float, float]] = None,
    initial_values: Dict[str, float] = None,
) -> Path:
    """
    Generate comprehensive HTML report with professional styling.
    
    Matches the aesthetics and detail level of the original vw_joint version.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    group_labels = {
        'sm': 'Single Males', 'sf': 'Single Females',
        'cou': 'Couples', 'cou_m': 'Males in Couples', 'cou_f': 'Females in Couples',
    }
    
    # Initialize defaults
    if fit_stats is None:
        fit_stats = {}
    if param_bounds is None:
        param_bounds = {}
    if initial_values is None:
        initial_values = {}
    
    # Compute elasticities if not provided
    if elasticities_df is None:
        elasticities_df = compute_structural_elasticities(parsed_params)
    
    # Compute MUC analysis if not provided
    if muc_analysis is None:
        muc_analysis = analyze_muc_behavior(parsed_params)
    
    # Calculate bounded parameter statistics
    n_bounded = 0
    n_hit_lower = 0
    n_hit_upper = 0
    for i, name in enumerate(parsed_params.param_names):
        if name in param_bounds:
            lb, ub = param_bounds[name]
            val = parsed_params.theta[i]
            n_bounded += 1
            if lb is not None and abs(val - lb) < 1e-6:
                n_hit_lower += 1
            if ub is not None and abs(val - ub) < 1e-6:
                n_hit_upper += 1
    
    # === BUILD HTML SECTIONS ===
    
    # CSS with professional styling matching old version
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
    h4 { margin-bottom: 0.5em; }
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
    .param-groups { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1em; }
    .param-group { background: var(--bg-light); padding: 1em; border-radius: 4px; }
    .contour-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5em; }
    .contour-item { text-align: center; }
    .header-info { background: var(--bg-light); padding: 1em; border-radius: 4px; margin-bottom: 2em; }
    .group-legend { display: flex; gap: 2em; margin: 1em 0; flex-wrap: wrap; }
    .legend-item { display: flex; align-items: center; gap: 0.5em; }
    .legend-color { width: 20px; height: 4px; border-radius: 2px; }
    .param-table .bounded-param { background-color: var(--bounded-row-color) !important; }
    .param-table .not-estimated { background-color: var(--not-estimated-color) !important; }
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
    
    # Build fit stats section with comprehensive info
    fit_stats_rows = ""
    # Add standard stats
    for k, v in fit_stats.items():
        if isinstance(v, float):
            if abs(v) < 0.01 or abs(v) > 10000:
                fit_stats_rows += f"<tr><th>{k}</th><td>{v:.4e}</td></tr>"
            else:
                fit_stats_rows += f"<tr><th>{k}</th><td>{v:.4f}</td></tr>"
        else:
            fit_stats_rows += f"<tr><th>{k}</th><td>{v}</td></tr>"
    
    # Add bounded params summary
    fit_stats_rows += f"<tr><th>n_bounded_params</th><td>{n_bounded}</td></tr>"
    fit_stats_rows += f"<tr><th>n_hit_lower_bound</th><td>{n_hit_lower}</td></tr>"
    fit_stats_rows += f"<tr><th>n_hit_upper_bound</th><td>{n_hit_upper}</td></tr>"
    
    # Add MU diagnostics summary
    total_neg_muc = sum(r.get('n_negative_muc', 0) for r in (mu_results or {}).values())
    total_neg_mul = sum(r.get('n_negative_mul', 0) for r in (mu_results or {}).values())
    total_n = sum(r.get('n_individuals', 0) for r in (mu_results or {}).values())
    pct_neg_muc = 100 * total_neg_muc / total_n if total_n > 0 else 0
    pct_neg_mul = 100 * total_neg_mul / total_n if total_n > 0 else 0
    fit_stats_rows += f"<tr><th>n_negative_muc_total</th><td>{total_neg_muc}</td></tr>"
    fit_stats_rows += f"<tr><th>n_negative_mul_total</th><td>{total_neg_mul}</td></tr>"
    fit_stats_rows += f"<tr><th>pct_negative_muc_total</th><td>{pct_neg_muc:.4f}</td></tr>"
    fit_stats_rows += f"<tr><th>pct_negative_mul_total</th><td>{pct_neg_mul:.4f}</td></tr>"
    
    # Bounded params explanation box
    bounds_explanation = f"""
    <div class="stats-box" style="margin-top:1.5em; border-left-color: var(--success-color);">
      <h4 style="margin-top:0;">📝 Understanding Bounded Parameters</h4>
      <ul style="margin-bottom:0; line-height:1.8;">
        <li><strong>n_bounded_params ({n_bounded})</strong>: Number of parameters with constraints defined (lower and/or upper bounds).</li>
        <li><strong>n_hit_lower_bound ({n_hit_lower})</strong>: Parameters stuck at lower bound. {'<span style="color:var(--success-color); font-weight:bold;">✓ Zero is good!</span>' if n_hit_lower == 0 else '<span style="color:var(--warning-color);">⚠ Check specification</span>'}</li>
        <li><strong>n_hit_upper_bound ({n_hit_upper})</strong>: Parameters stuck at upper bound. {'<span style="color:var(--success-color); font-weight:bold;">✓ Zero is good!</span>' if n_hit_upper == 0 else '<span style="color:var(--warning-color);">⚠ Check specification</span>'}</li>
        <li><strong>Interpretation</strong>: Zero hits means the optimizer found a solution <em>inside</em> the constraint region.</li>
      </ul>
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
            n_neg_muc = results.get('n_negative_muc', 0)
            pct_muc = results.get('pct_negative_muc', 0) or 0
            n_neg_mul = results.get('n_negative_mul', 0)
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
                <td {muc_cell_class}>{n_neg_muc}</td>
                <td {muc_cell_class}>{pct_muc:.4f}%</td>
                <td {mul_cell_class}>{n_neg_mul}</td>
                <td {mul_cell_class}>{pct_mul:.4f}%</td>
                <td>{muc_mean_str}</td>
                <td>{mul_mean_str}</td>
            </tr>
            """
    
    # Build group parameters section with separate males/females in couples
    group_params_html = ""
    for group in parsed_params.preference_groups:
        params = parsed_params.get_all_params_for_group(group)
        simple_params = {k: v for k, v in params.items() if '.' not in k}
        
        if group == 'cou':
            # Split couples into male/female/shared
            male_params = {k.replace('_m', ''): v for k, v in simple_params.items() if k.endswith('_m')}
            female_params = {k.replace('_f', ''): v for k, v in simple_params.items() if k.endswith('_f')}
            shared_params = {k: v for k, v in simple_params.items() if not k.endswith('_m') and not k.endswith('_f')}
            
            # Males in couples
            if male_params:
                param_rows = [f"<tr><td>{k}</td><td>{v:.4f}</td></tr>" for k, v in sorted(male_params.items())]
                group_params_html += f"""
                <div class="param-group">
                    <h4>Males in Couples</h4>
                    <table class="table table-sm">{''.join(param_rows)}</table>
                </div>
                """
            
            # Females in couples
            if female_params:
                param_rows = [f"<tr><td>{k}</td><td>{v:.4f}</td></tr>" for k, v in sorted(female_params.items())]
                group_params_html += f"""
                <div class="param-group">
                    <h4>Females in Couples</h4>
                    <table class="table table-sm">{''.join(param_rows)}</table>
                </div>
                """
            
            # Shared couple params
            if shared_params:
                param_rows = [f"<tr><td>{k}</td><td>{v:.4f}</td></tr>" for k, v in sorted(shared_params.items())]
                group_params_html += f"""
                <div class="param-group">
                    <h4>Couples (shared)</h4>aut
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
    
    # Build plots section with grid layout
    plots_section = ""
    if plot_paths:
        contour_plots = []
        mu_comparison_plots = []
        fit_plots = []
        other_plots = []
        
        for name, path in plot_paths.items():
            if path and Path(path).exists():
                img_tag = f'<img src="{Path(path).name}" alt="{name}" style="max-width:100%;">'
                if 'contour' in name.lower():
                    group_key = name.replace('_contours', '')
                    label = group_labels.get(group_key, group_key.upper())
                    contour_plots.append(f'<div class="contour-item"><h4>{label}</h4>{img_tag}</div>')
                elif 'muc_comparison' in name.lower() or 'mul_comparison' in name.lower():
                    title = 'Marginal Utility of Consumption' if 'muc' in name.lower() else 'Marginal Utility of Leisure'
                    mu_comparison_plots.append(f'<figure><figcaption>{title}</figcaption>{img_tag}</figure>')
                elif 'fit_' in name.lower() or 'participation' in name.lower() or 'mean_hours' in name.lower():
                    title = name.replace('fit_', '').replace('_', ' ').title()
                    fit_plots.append(f'<figure><figcaption>{title}</figcaption>{img_tag}</figure>')
                elif 'marginal_utilities' in name.lower():
                    fit_plots.append(f'<figure><figcaption>Marginal Utilities</figcaption>{img_tag}</figure>')
                else:
                    title = name.replace('_', ' ').title()
                    other_plots.append(f'<figure><figcaption>{title}</figcaption>{img_tag}</figure>')
        
        # MU comparison section
        if mu_comparison_plots:
            plots_section += f'<h3>Marginal Utility Comparison</h3><div class="two-col">{"".join(mu_comparison_plots)}</div>'
        
        # Contour plots section
        if contour_plots:
            plots_section += f'<h3>Utility Indifference Curves by Group</h3><p>Contour lines at utility levels</p><div class="contour-grid">{"".join(contour_plots)}</div>'
        
        # Fit plots
        if fit_plots:
            plots_section += f'<div class="two-col">{"".join(fit_plots)}</div>'
        
        # Other plots
        if other_plots:
            plots_section += f'<div class="two-col">{"".join(other_plots)}</div>'
    
    # Color legend for parameter table
    color_legend = """
    <div class="color-legend">
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--bounded-row-color);"></div>Bounded (has constraints)</div>
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--bound-hit-color);"></div>⚠️ Hit bound (stuck at constraint)</div>
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--not-estimated-color);"></div>Not estimated (fixed)</div>
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--pval-marginal);"></div>p ∈ [0.05, 0.1) Marginal</div>
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--pval-weak);"></div>p ∈ [0.1, 0.25) Weak</div>
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--pval-insig);"></div>p ≥ 0.25 Insignificant</div>
    </div>
    <p style="font-size:0.9em; color:#666; margin-top:0.5em;">
      <strong>Note:</strong> <span style="background-color: var(--bounded-row-color); padding:2px 4px;">Yellow rows</span> have bounds defined.
      <span style="background-color: var(--bound-hit-color); padding:2px 4px;">Red cells</span> indicate parameter at constraint.
    </p>
    """
    
    # Build full parameter table with SE, t-values, bounds
    param_df = parsed_params.to_dataframe()
    param_table_rows = ""
    for idx, row in param_df.iterrows():
        param_name = row.get('parameter', '')
        est = row.get('estimate', np.nan)
        se = row.get('std_error', np.nan)
        t_val = row.get('t_value', np.nan)
        p_val = row.get('p_value', np.nan)
        
        # Get bounds info
        lb, ub = param_bounds.get(param_name, (None, None))
        init_val = initial_values.get(param_name, None)
        
        # Determine row class
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
        
        # Format values
        est_str = f"{est:.4f}" if isinstance(est, float) and np.isfinite(est) else "N/A"
        se_str = f"{se:.4f}" if isinstance(se, float) and np.isfinite(se) else "N/A"
        t_str = f"{t_val:.2f}" if isinstance(t_val, float) and np.isfinite(t_val) else "N/A"
        lb_str = f"{lb:.4f}" if lb is not None else "—"
        ub_str = f"{ub:.4f}" if ub is not None else "—"
        init_str = f"{init_val:.4f}" if init_val is not None else "N/A"
        bounded_str = "Yes" if is_bounded else "No"
        estimated_str = "Yes" if isinstance(se, float) and np.isfinite(se) else "Unknown"
          # Significance
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
            <td>{bounded_str}</td>
            <td>{init_str}</td>
            <td>{estimated_str}</td>
        </tr>
        """
    
    # === ASSEMBLE FINAL HTML ===
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>RURO Joint Post-Estimation Analysis</title>
    <style>{css}</style>
</head>
<body>
    <h1>📊 RURO Joint Post-Estimation Analysis</h1>
    
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
        <p><small><em>Note: For exact elasticities, use simulation-based methods with tax-benefit integration.</em></small></p>
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
        <p>Analysis of marginal utilities at chosen alternatives. Negative values indicate potential specification issues.</p>
        
        <h3>Negative MUC/MUL at Chosen Alternatives by Group</h3>
        <table class="table table-striped">
            <thead>
                <tr><th>Group</th><th>N Individuals</th><th>N Neg MUC</th><th>% Neg MUC</th><th>N Neg MUL</th><th>% Neg MUL</th><th>MUC Mean</th><th>MUL Mean</th></tr>
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
                        <th>Bounded</th>
                        <th>Initial Value</th>
                        <th>Estimated</th>
                    </tr>
                </thead>
                <tbody>{param_table_rows}</tbody>
            </table>
        </div>
    </section>
    
    <footer>
        <p>Generated by RURO Post-Estimation v2 (Automatic) | {timestamp}</p>
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
# MAIN ENTRY POINT
# =============================================================================

def run_post_estimation(
    theta: np.ndarray,
    param_names: List[str],
    log_likelihood: float,
    df_sm: pd.DataFrame = None,
    df_sf: pd.DataFrame = None,
    df_cou: pd.DataFrame = None,
    out_dir: Path = None,
    std_errors: np.ndarray = None,
    prefix: str = '',
    n_individuals: int = None,
    param_bounds: Dict[str, Tuple[float, float]] = None,
    initial_values: Dict[str, float] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Run full post-estimation analysis.
    
    This is the main entry point. It automatically adapts to whatever
    parameters are passed from the estimation.
    
    Parameters
    ----------
    theta : np.ndarray
        Estimated parameter values
    param_names : List[str]
        Parameter names (determines model structure)
    log_likelihood : float
        Log-likelihood at optimum
    df_sm, df_sf, df_cou : pd.DataFrame
        MNL datasets for singles males, females, and couples
    out_dir : Path
        Output directory for reports and plots
    std_errors : np.ndarray
        Standard errors (optional)
    prefix : str
        Prefix for output filenames (e.g., 'vw_' for variable wage spec)
    n_individuals : int
        Total number of individuals (for BIC computation)
    param_bounds : Dict[str, Tuple[float, float]]
        Parameter bounds for HTML report
    initial_values : Dict[str, float]
        Initial parameter values for HTML report
    
    Returns
    -------
    Dict with all results
    """
    LOGGER.info("=" * 70)
    LOGGER.info("RURO POST-ESTIMATION ANALYSIS (v2 - Automatic)")
    LOGGER.info("=" * 70)
    
    if out_dir is None:
        out_dir = outputs_root() / "post_estimation"
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse parameters
    LOGGER.info("\n1. Parsing parameters...")
    parsed = ParsedParameters(
        param_names=param_names,
        theta=theta,
        std_errors=std_errors,
    )
    
    LOGGER.info(f"   Found {len(parsed.groups)} groups: {parsed.groups}")
    LOGGER.info(f"   Preference groups: {parsed.preference_groups}")
    for group in parsed.preference_groups:
        shifters = parsed.leisure_shifters.get(group, [])
        LOGGER.info(f"   {group} leisure shifters: {shifters}")
    
    # Create utility computer
    utility_computer = DynamicUtilityComputer(parsed)
    
    # Compute fit diagnostics
    LOGGER.info("\n2. Computing fit diagnostics...")
    fit_results = {}
    
    if df_sm is not None:
        LOGGER.info("   Single males...")
        fit_results['sm'] = compute_fit_diagnostics(
            df_sm, utility_computer, 'sm', hours_col='lhw'
        )
        LOGGER.info(f"      Obs: {fit_results['sm']['participation_rate_observed']:.1%}, "
                   f"Pred: {fit_results['sm']['participation_rate_predicted']:.1%}")
    
    if df_sf is not None:
        LOGGER.info("   Single females...")
        fit_results['sf'] = compute_fit_diagnostics(
            df_sf, utility_computer, 'sf', hours_col='lhw'
        )
        LOGGER.info(f"      Obs: {fit_results['sf']['participation_rate_observed']:.1%}, "
                   f"Pred: {fit_results['sf']['participation_rate_predicted']:.1%}")
    
    if df_cou is not None:
        LOGGER.info("   Couples (males)...")
        fit_results['cou_m'] = compute_fit_diagnostics(
            df_cou, utility_computer, 'cou', hours_col='hours_male', is_couples=True
        )
        LOGGER.info(f"      Obs: {fit_results['cou_m']['participation_rate_observed']:.1%}, "
                   f"Pred: {fit_results['cou_m']['participation_rate_predicted']:.1%}")

        LOGGER.info("   Couples (females)...")
        fit_results['cou_f'] = compute_fit_diagnostics(
            df_cou, utility_computer, 'cou', hours_col='hours_female', is_couples=True
        )
        LOGGER.info(f"      Obs: {fit_results['cou_f']['participation_rate_observed']:.1%}, "
                   f"Pred: {fit_results['cou_f']['participation_rate_predicted']:.1%}")
      # Model fit statistics
    if n_individuals is None:
        n_individuals = kwargs.get('n_individuals', 1000)

    # Compute null log-likelihood for rho-squared
    # Combine all available DataFrames
    dfs_available = []
    if df_sm is not None:
        dfs_available.append(df_sm)
    if df_sf is not None:
        dfs_available.append(df_sf)
    if df_cou is not None:
        dfs_available.append(df_cou)

    if dfs_available:
        df_combined = pd.concat(dfs_available, ignore_index=True)

        # Try multiple ID column names
        id_col = None
        for candidate in ['ruro_id', 'idhh', 'idperson', 'id']:
            if candidate in df_combined.columns:
                id_col = candidate
                break

        if id_col is not None:
            n_alts = df_combined.groupby(id_col).size()
            ll_null = -np.sum(np.log(n_alts))
            rho_squared = 1 - (log_likelihood / ll_null)
            rho_squared_adj = 1 - ((log_likelihood - len(theta)) / ll_null)
        else:
            LOGGER.warning("Could not compute rho-squared: ID column not found")
            ll_null = None
            rho_squared = None
            rho_squared_adj = None
    else:
        LOGGER.warning("Could not compute rho-squared: No DataFrames provided")
        ll_null = None
        rho_squared = None
        rho_squared_adj = None

    # Calculate total observations for AIC_per_obs
    n_obs = 0
    if dfs_available:
        n_obs = len(df_combined)

    fit_stats = {
        'log_likelihood': log_likelihood,
        'll_null': ll_null,
        'n_parameters': len(theta),
        'n_individuals': n_individuals,
        'rho_squared': rho_squared,
        'rho_squared_adj': rho_squared_adj,
        'AIC': -2 * log_likelihood + 2 * len(theta),
        'BIC': -2 * log_likelihood + np.log(n_individuals) * len(theta),
        'AIC_per_obs': (-2 * log_likelihood + 2 * len(theta)) / n_obs if n_obs > 0 else None,
    }
      # Compute MU diagnostics
    LOGGER.info("\n3. Computing marginal utility diagnostics...")
    mu_results = compute_all_mu_diagnostics(df_sm, df_sf, df_cou, utility_computer)
    for group, results in mu_results.items():
        pct_muc = results.get('pct_negative_muc', np.nan)
        pct_mul = results.get('pct_negative_mul', np.nan)
        LOGGER.info(f"   {group}: {pct_muc:.1f}% negative MUC, {pct_mul:.1f}% negative MUL")
    
    # Compute elasticities
    LOGGER.info("\n4. Computing elasticities...")
    elasticities_df = compute_structural_elasticities(parsed)
    
    # Generate plots
    LOGGER.info("\n5. Generating plots...")
    plot_paths = plot_fit_comparison(fit_results, out_dir, prefix=prefix)
    
    # Use the new unified contour function that generates separate plots for
    # sm, sf, cou_m, cou_f (all 4 demographic groups)
    plot_paths.update(plot_utility_contours_all_groups(parsed, out_dir, prefix=prefix))
    
    # MU comparison plots (muc_comparison.png, mul_comparison.png, individual group plots)
    plot_paths.update(plot_mu_comparison(
        parsed, out_dir, prefix=prefix,
        df_sm=df_sm, df_sf=df_sf, df_cou=df_cou
    ))
    
    # Additional MU diagnostic and marginal utility plots
    plot_paths.update(plot_marginal_utilities(parsed, out_dir))
    plot_paths.update(plot_mu_diagnostics(mu_results, out_dir))
      # Generate HTML report
    LOGGER.info("\n6. Generating HTML report...")
    html_path = out_dir / f'{prefix}post_estimation_report.html'
    generate_html_report(
        parsed_params=parsed,
        fit_results=fit_results,
        output_path=html_path,
        fit_stats=fit_stats,
        plot_paths=plot_paths,
        mu_results=mu_results,
        elasticities_df=elasticities_df,
        param_bounds=param_bounds,
        initial_values=initial_values,
    )
    
    # Save parameter CSV
    LOGGER.info("\n7. Saving output files...")
    param_csv = out_dir / f'{prefix}params.csv'
    parsed.to_dataframe().to_csv(param_csv, index=False)
    LOGGER.info(f"   Parameters: {param_csv}")
      # Save elasticities CSV
    elasticities_csv = out_dir / f'{prefix}elasticities.csv'
    elasticities_df.to_csv(elasticities_csv, index=False)
    LOGGER.info(f"   Elasticities: {elasticities_csv}")
    
    LOGGER.info("\n" + "=" * 70)
    LOGGER.info("POST-ESTIMATION COMPLETE")
    LOGGER.info("=" * 70)
    
    return {
        'parsed_params': parsed,
        'fit_results': fit_results,
        'fit_stats': fit_stats,
        'mu_results': mu_results,
        'elasticities': elasticities_df,
        'html_report': html_path,
        'param_csv': param_csv,
        'elasticities_csv': elasticities_csv,
        'plot_paths': plot_paths,
    }


# =============================================================================
# TEST
# =============================================================================

if __name__ == '__main__':
    import json
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    
    # Load test data
    with open(outputs_root() / "estimates/fr/2016/fr_2016_joint.json", 'r') as f:
        results = json.load(f)
    
    theta = np.array(results['theta'])
    param_names = results['param_names']
    
    # Test parameter parsing
    parsed = ParsedParameters(param_names=param_names, theta=theta)
    
    print("\n=== PARSED STRUCTURE ===")
    print(f"Groups: {parsed.groups}")
    print(f"Preference groups: {parsed.preference_groups}")
    print(f"Leisure shifters: {parsed.leisure_shifters}")
    
    print("\n=== SINGLE MALES PARAMS ===")
    for k, v in parsed.get_all_params_for_group('sm').items():
        print(f"  {k}: {v:.6f}")
