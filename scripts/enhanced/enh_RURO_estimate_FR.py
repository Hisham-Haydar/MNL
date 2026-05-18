#!/usr/bin/env python
"""
==============================================================================
Enhanced RURO MNL Estimation - France
==============================================================================
Main estimation script for RURO labor supply model.

Features:
- Multiple wage specifications (fw, vw, loc_empirical)
- YAML-based configuration
- Parallel joint estimation (singles + couples)
- Strict metadata validation
- Comprehensive results export

Usage:
    python enh_RURO_estimate_FR.py \\
        --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \\
        --output-dir "outputs/estimation/FR_2016" \\
        --group joint \\
        --n-jobs 4

Author: Enhanced RURO Pipeline
Created: 2026-01-03
==============================================================================
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple

# CRITICAL: Disable Numba debug logging BEFORE importing any numba-accelerated code
# Numba's debug logging produces massive output that can hang the estimation
logging.getLogger('numba').setLevel(logging.WARNING)
logging.getLogger('numba.core').setLevel(logging.WARNING)
logging.getLogger('numba.core.byteflow').setLevel(logging.WARNING)
logging.getLogger('numba.core.interpreter').setLevel(logging.WARNING)
logging.getLogger('numba.core.ssa').setLevel(logging.WARNING)

import numpy as np
import pandas as pd

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from estimation_utils import (
    load_and_validate_mnl_data,
    precompute_data_singles,
    precompute_data_couples,
    validate_data_spec_compatibility
)
from estimation_spec_parser import (
    parse_specification,
    load_custom_initial_values,
    find_latest_results,
    load_warm_start_values
)
from parallel_estimation import (
    estimate_single_group,
    estimate_joint,
    format_estimation_results
)
from scipy.stats import norm


# ==============================================================================
# Logging Setup
# ==============================================================================

def setup_logging(output_dir: Path, verbose: bool = False) -> None:
    """
    Configure logging to file and console.

    Parameters
    ----------
    output_dir : Path
        Directory for log file
    verbose : bool
        If True, use DEBUG level; else INFO
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    log_file = output_dir / "estimation.log"

    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    # Remove any existing handlers to avoid duplicate logs
    if logger.handlers:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()

    # File handler
    fh = logging.FileHandler(log_file, mode='w')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)
    ch.setFormatter(logging.Formatter(
        '%(levelname)s - %(message)s'
    ))
    logger.addHandler(fh)
    logger.addHandler(ch)


# ==============================================================================
# Output Path Helpers
# ==============================================================================

def resolve_spec_path(spec_config_arg: str) -> Path:
    """
    Resolve specification file path from CLI argument.

    Tries the provided path first (relative to current working directory), then
    falls back to script-relative resolution.
    """
    spec_path = Path(spec_config_arg)
    if not spec_path.is_absolute() and not spec_path.exists():
        spec_path = Path(__file__).parent / spec_config_arg
    return spec_path.resolve()


def build_spec_folder_name(spec_config_path: Path) -> str:
    """
    Build a filesystem-safe folder name from a spec YAML filename.
    """
    base_name = spec_config_path.stem or spec_config_path.name or "unknown_spec"
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", base_name).strip("._")
    return safe_name or "unknown_spec"


# ==============================================================================
# GAMSPy Result Wrapper
# ==============================================================================

class GAMSPyOptimizeResult:
    """
    Wrapper for GAMSPy solver results to match scipy.optimize.OptimizeResult interface.

    This allows GAMSPy results to be used interchangeably with SciPy L-BFGS-B results
    in the estimation pipeline.
    """
    def __init__(self, gamspy_dict: Dict[str, Any]):
        self.x = gamspy_dict['theta']
        self.fun = -gamspy_dict['log_likelihood']  # Negative LL (minimization convention)
        self.success = ('Optimal' in gamspy_dict['solver_status'] or
                        'Normal' in gamspy_dict['solver_status'])
        self.message = f"{gamspy_dict['solver_status']} ({gamspy_dict['model_status']})"
        self.nit = gamspy_dict['n_iterations'] or 0
        self.nfev = self.nit  # Approximate (GAMSPy doesn't track function evals separately)
        self.jac = None  # GAMSPy uses automatic differentiation, doesn't return gradient


# ==============================================================================
# Standard Error Computation
# ==============================================================================

def compute_standard_errors(
    theta: np.ndarray,
    grad_func,
    eps: float = 1e-5,
    bounds: Optional[List[Tuple[Optional[float], Optional[float]]]] = None,
    bound_tol: float = 1e-6,
    bound_range_tol: float = 1e-6,
    logger: logging.Logger = None
) -> Dict[str, Any]:
    """
    Compute standard errors using numerical Hessian approximation.
    
    Uses central differences on the gradient to approximate the Hessian,
    then inverts to get variance-covariance matrix.
    
    Parameters
    ----------
    theta : np.ndarray
        Final parameter estimates
    grad_func : callable
        Function that returns gradient of NEGATIVE log-likelihood
    eps : float
        Step size for numerical differentiation
    bounds : list of tuple, optional
        Parameter bounds (lb, ub) aligned with theta; used to exclude parameters at bounds
    bound_tol : float
        Absolute tolerance to treat a parameter as "at bound"
    bound_range_tol : float
        Treat parameters with very tight bounds (ub - lb <= bound_range_tol) as fixed
    logger : logging.Logger
        Logger for progress messages
        
    Returns
    -------
    dict with keys:
        - 'se': np.ndarray of standard errors
        - 'varcov': variance-covariance matrix
        - 't_values': t-statistics (theta / se)
        - 'p_values': p-values (two-sided)
        - 'hessian': numerical Hessian matrix
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    n_params = len(theta)

    # Identify free parameters (exclude those at bounds)
    free_mask = np.ones(n_params, dtype=bool)
    if bounds is not None:
        if len(bounds) != n_params:
            logger.warning("Bounds length mismatch; ignoring bounds for SE computation")
        else:
            for i, (lb, ub) in enumerate(bounds):
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
        logger.info(f"Computing Hessian for {n_free}/{n_params} free parameters ({n_fixed} at bounds/fixed)")
    else:
        logger.info(f"Computing Hessian for all {n_params} parameters")

    if n_free == 0:
        logger.warning("No free parameters for SE computation; returning NaN standard errors")
        se_full = np.full(n_params, np.nan)
        return {
            'se': se_full,
            'varcov': None,
            't_values': np.full(n_params, np.nan),
            'p_values': np.full(n_params, np.nan),
            'hessian': None,
            'eigenvalues': None,
            'condition_number': None,
            'n_negative_eigenvalues': 0,
            'correlation_matrix': None,
        }

    logger.info(f"Computing numerical Hessian ({n_free}x{n_free})...")

    # Compute Hessian numerically (central differences on gradient) for free params
    H = np.zeros((n_free, n_free))

    for col_idx, i in enumerate(free_idx):
        theta_plus = theta.copy()
        theta_minus = theta.copy()
        theta_plus[i] += eps
        theta_minus[i] -= eps

        g_plus = grad_func(theta_plus)
        g_minus = grad_func(theta_minus)

        # Second derivative: (g(x+h) - g(x-h)) / 2h, restricted to free params
        H[:, col_idx] = (g_plus[free_idx] - g_minus[free_idx]) / (2 * eps)

        if (col_idx + 1) % 10 == 0:
            logger.info(f"  Hessian column {col_idx+1}/{n_free} computed")
    
    # Symmetrize
    H = 0.5 * (H + H.T)

    # Check condition number
    try:
        cond = np.linalg.cond(H)
        logger.info(f"Hessian condition number: {cond:.2e}")
        if cond > 1e10:
            logger.warning(f"Hessian is ill-conditioned (cond={cond:.2e})")
    except:
        cond = np.inf
        logger.warning("Could not compute condition number")

    # Eigenvalues (Hessian of negative log-likelihood)
    eigenvalues = None
    n_negative = 0
    try:
        eigenvalues = np.linalg.eigvalsh(H)
        n_negative = int(np.sum(eigenvalues < 0))
    except Exception as exc:
        logger.warning(f"Could not compute Hessian eigenvalues: {exc}")

    # Compute variance-covariance matrix with robust methods
    try:
        # First try regular inverse
        if cond < 1e10:
            varcov_free = np.linalg.inv(H)
        else:
            # Use pseudo-inverse for ill-conditioned matrices
            logger.info("Using Moore-Penrose pseudoinverse for robustness...")
            varcov_free = np.linalg.pinv(H, rcond=1e-10)

        se_free = np.sqrt(np.abs(np.diag(varcov_free)))  # abs to handle numerical issues

        # Embed into full-size arrays (fixed params -> NaN)
        varcov_full = np.full((n_params, n_params), np.nan)
        varcov_full[np.ix_(free_idx, free_idx)] = varcov_free
        se_full = np.full(n_params, np.nan)
        se_full[free_idx] = se_free

        # Correlation matrix (full)
        with np.errstate(divide='ignore', invalid='ignore'):
            denom = np.outer(se_full, se_full)
            corr_full = np.divide(varcov_full, denom, out=np.full_like(varcov_full, np.nan), where=denom != 0)
        if corr_full.size:
            np.fill_diagonal(corr_full, 1.0)

        # Check for negative variances (indicates identification problems)
        neg_var = np.diag(varcov_free) < 0
        if np.any(neg_var):
            n_neg = np.sum(neg_var)
            logger.warning(f"Warning: {n_neg} free parameters have negative variance (identification issue)")
            se_free[neg_var] = np.nan
            se_full[free_idx] = se_free

        # Flag parameters with very large SEs (likely poorly identified)
        large_se = se_full > 100 * np.abs(theta + 1e-10)
        if np.any(large_se & ~np.isnan(se_full)):
            n_large = np.sum(large_se & ~np.isnan(se_full))
            logger.warning(f"Warning: {n_large} parameters have very large SEs (poor identification)")

        # Compute t-values and p-values (free params only)
        t_values = np.full(n_params, np.nan)
        p_values = np.full(n_params, np.nan)
        with np.errstate(divide='ignore', invalid='ignore'):
            t_values[free_idx] = theta[free_idx] / se_free
            p_values[free_idx] = 2 * (1 - norm.cdf(np.abs(t_values[free_idx])))

        n_valid = np.sum(np.isfinite(se_full))
        logger.info(f"Standard errors computed: {n_valid}/{n_params} valid")

        return {
            'se': se_full,
            'varcov': varcov_full,
            't_values': t_values,
            'p_values': p_values,
            'hessian': H,
            'eigenvalues': eigenvalues,
            'condition_number': cond,
            'n_negative_eigenvalues': n_negative,
            'correlation_matrix': corr_full,
        }

    except np.linalg.LinAlgError as e:
        logger.error(f"Hessian inversion failed: {e}")
        logger.error("This typically indicates model identification problems")

        # Try pseudo-inverse as last resort
        try:
            logger.info("Attempting pseudo-inverse as fallback...")
            varcov_free = np.linalg.pinv(H, rcond=1e-8)
            se_free = np.sqrt(np.abs(np.diag(varcov_free)))
            neg_var = np.diag(varcov_free) < 0
            se_free[neg_var] = np.nan

            varcov_full = np.full((n_params, n_params), np.nan)
            varcov_full[np.ix_(free_idx, free_idx)] = varcov_free
            se_full = np.full(n_params, np.nan)
            se_full[free_idx] = se_free

            t_values = np.full(n_params, np.nan)
            p_values = np.full(n_params, np.nan)
            with np.errstate(divide='ignore', invalid='ignore'):
                t_values[free_idx] = theta[free_idx] / se_free
                p_values[free_idx] = 2 * (1 - norm.cdf(np.abs(t_values[free_idx])))

            n_valid = np.sum(np.isfinite(se_full))
            logger.info(f"Pseudo-inverse succeeded: {n_valid}/{n_params} valid SEs")

            return {
                'se': se_full,
                'varcov': varcov_full,
                't_values': t_values,
                'p_values': p_values,
                'hessian': H,
                'eigenvalues': eigenvalues,
                'condition_number': cond,
                'n_negative_eigenvalues': n_negative,
                'correlation_matrix': None,
            }
        except Exception as e2:
            logger.error(f"Pseudo-inverse also failed: {e2}")

        # Return NaN for all SE
        return {
            'se': np.full(n_params, np.nan),
            'varcov': None,
            't_values': np.full(n_params, np.nan),
            'p_values': np.full(n_params, np.nan),
            'hessian': H,
            'eigenvalues': eigenvalues,
            'condition_number': cond,
            'n_negative_eigenvalues': n_negative,
            'correlation_matrix': None,
        }


# ==============================================================================
# Results Export
# ==============================================================================

def save_results_json(
    results: dict,
    spec,
    metadata: dict,
    output_dir: Path,
    args: argparse.Namespace,
    theta_init: Optional[np.ndarray] = None
) -> None:
    """
    Save estimation results to JSON file.

    Parameters
    ----------
    results : dict
        Results from estimate_joint() or estimate_single_group()
    spec : EstimationSpec
        Specification used
    metadata : dict
        Pipeline metadata
    output_dir : Path
        Output directory
    args : Namespace
        CLI arguments
    theta_init : np.ndarray, optional
        Initial parameter vector actually used (warm-start or spec defaults)
    """
    logger = logging.getLogger(__name__)

    output = {
        'specification': spec.name,
        'wage_spec': spec.wage_spec,
        'timestamp': datetime.now().isoformat(),
        'command_line': ' '.join(sys.argv),

        'metadata': {
            'mnl_base': str(args.mnl_base),
            'spec_config': str(args.spec_config),
            'group': args.group,
            'n_jobs': args.n_jobs,
            'opt_method': spec.opt_method,
            'analytical_gradient': spec.opt_analytical_gradient,
            'strict_validation': not args.no_strict_validation
        },

        'results': {}
    }

    # Build bounds and initial values dicts for JSON
    bounds_dict = {}
    initial_dict = {}
    if theta_init is not None and len(theta_init) == len(spec.all_param_names):
        for i, param_name in enumerate(spec.all_param_names):
            if param_name in spec.bounds:
                lb, ub = spec.bounds[param_name]
                bounds_dict[param_name] = [lb, ub]
            initial_dict[param_name] = float(theta_init[i])
    else:
        if theta_init is not None:
            logger.warning("theta_init length mismatch; falling back to spec defaults for initial values")
        for param_name in spec.all_param_names:
            if param_name in spec.bounds:
                lb, ub = spec.bounds[param_name]
                bounds_dict[param_name] = [lb, ub]
            initial_dict[param_name] = float(spec.initial_values.get(param_name, 0.0))
    group_keys = ['singles_male', 'singles_female', 'couples', 'joint']
    for group_name in group_keys:
        if group_name in results:
            opt_result = results[group_name]

            # Add convergence diagnostics
            convergence_diag = {}
            if hasattr(opt_result, 'jac') and opt_result.jac is not None:
                grad = opt_result.jac
                bounds_tuple = spec.get_bounds_tuple()
                theta_final = opt_result.x

                # Compute projected gradient
                grad_proj = grad.copy()
                for i in range(len(theta_final)):
                    lb, ub = bounds_tuple[i]
                    if lb is not None and abs(theta_final[i] - lb) < 1e-8:
                        if grad[i] > 0:
                            grad_proj[i] = 0.0
                    elif ub is not None and abs(theta_final[i] - ub) < 1e-8:
                        if grad[i] < 0:
                            grad_proj[i] = 0.0

                convergence_diag = {
                    'gradient_norm_full': float(np.linalg.norm(grad)),
                    'gradient_norm_projected': float(np.linalg.norm(grad_proj)),
                    'gradient_inf_norm_full': float(np.linalg.norm(grad, ord=np.inf)),
                    'gradient_inf_norm_projected': float(np.linalg.norm(grad_proj, ord=np.inf))
                }

            # Get walltime - 'joint' uses 'joint' key in walltimes
            walltime_key = group_name
            walltime = results.get('walltimes', {}).get(walltime_key, results.get('total_walltime', 0.0))

            output['results'][group_name] = {
                'success': bool(opt_result.success),
                'message': opt_result.message,
                'n_iterations': int(opt_result.nit),
                'n_function_evaluations': int(opt_result.nfev),
                'final_ll': float(-opt_result.fun),
                'gradient_norm': float(np.linalg.norm(opt_result.jac)) if hasattr(opt_result, 'jac') and opt_result.jac is not None else None,
                'walltime_seconds': float(walltime),

                'parameters': spec.unpack_parameters(opt_result.x),
                'theta': opt_result.x.tolist(),  # Also save raw theta vector
                'bounds': bounds_dict,
                'initial_values': initial_dict,
                'convergence_diagnostics': convergence_diag
            }

    # Add summary
    output['summary'] = {
        'joint_ll': float(results.get('joint_ll', 0.0)),
        'n_obs_total': int(results['n_obs_total']),
        'n_groups_total': int(results['n_groups_total']),
        'total_walltime_seconds': float(results['total_walltime']),
        'prior_correction_applied': bool(results.get('prior_correction_applied', False)),
        'prior_correction_form': results.get('prior_correction_form'),
        'market_centering_applied': bool(results.get('market_centering_applied', False)),
    }

    # Add standard errors if available
    if 'standard_errors' in results and results['standard_errors'] is not None:
        se_results = results['standard_errors']

        # Convert NumPy arrays to serializable lists
        def convert_array(arr):
            """Convert NumPy array to list, handling NaN/Inf."""
            if arr is None:
                return None
            if isinstance(arr, np.ndarray):
                return [float(x) if np.isfinite(x) else None for x in arr.flatten()]
            elif isinstance(arr, list):
                return arr  # Already a list
            return arr

        output['standard_errors'] = {
            'se': convert_array(se_results.get('se')),
            't_values': convert_array(se_results.get('t_values')),
            'p_values': convert_array(se_results.get('p_values')),
            # Don't save varcov and hessian matrices (too large for JSON)
        }

        # Also add SEs to each group result
        for group_name in group_keys:
            if group_name in output['results']:
                output['results'][group_name]['standard_errors'] = output['standard_errors']['se']
                output['results'][group_name]['t_values'] = output['standard_errors']['t_values']
                output['results'][group_name]['p_values'] = output['standard_errors']['p_values']

    se_results_dict = results.get('standard_errors') if isinstance(results.get('standard_errors'), dict) else None

    # Add Hessian diagnostics if available (from GAMSPy estimation or numerical Hessian)
    hess_diag = results.get('hessian_diagnostics') if isinstance(results.get('hessian_diagnostics'), dict) else None
    if hess_diag is None and se_results_dict is not None:
        hess_diag = {}

    if hess_diag is not None:

        # Convert numpy arrays to lists, handling None values
        def to_serializable(val):
            if val is None:
                return None
            elif isinstance(val, np.ndarray):
                # Convert to list, replacing NaN/Inf with None
                return [float(x) if np.isfinite(x) else None for x in val.flatten()]
            elif isinstance(val, (np.integer, np.floating)):
                return float(val) if np.isfinite(val) else None
            elif isinstance(val, dict):
                return {k: to_serializable(v) for k, v in val.items()}
            elif isinstance(val, list):
                return [to_serializable(x) for x in val]
            else:
                return val

        def build_top_correlations(varcov, param_names, min_abs=0.9, max_pairs=20):
            if varcov is None or not isinstance(varcov, np.ndarray):
                return []
            n_params = len(param_names)
            if varcov.shape[0] != n_params or varcov.shape[1] != n_params:
                return []
            se = np.sqrt(np.abs(np.diag(varcov)))
            with np.errstate(divide='ignore', invalid='ignore'):
                denom = np.outer(se, se)
                corr = np.divide(varcov, denom, out=np.full_like(varcov, np.nan), where=denom != 0)
            pairs = []
            for i in range(n_params):
                for j in range(i + 1, n_params):
                    val = corr[i, j]
                    if not np.isfinite(val):
                        continue
                    if abs(val) >= min_abs:
                        pairs.append((abs(val), float(val), param_names[i], param_names[j]))
            pairs.sort(reverse=True)
            return [
                {'param_i': p_i, 'param_j': p_j, 'corr': corr_val}
                for _, corr_val, p_i, p_j in pairs[:max_pairs]
            ]

        eigenvalues = hess_diag.get('eigenvalues')
        if eigenvalues is None and se_results_dict is not None:
            eigenvalues = se_results_dict.get('eigenvalues')
        eigenvalues_arr = np.array(eigenvalues, dtype=float) if eigenvalues is not None else None

        condition_number = hess_diag.get('condition_number')
        if condition_number is None and se_results_dict is not None:
            condition_number = se_results_dict.get('condition_number')
        if condition_number is None and eigenvalues_arr is not None and eigenvalues_arr.size:
            finite_eigs = eigenvalues_arr[np.isfinite(eigenvalues_arr)]
            if finite_eigs.size:
                min_ev = np.nanmin(finite_eigs)
                max_ev = np.nanmax(finite_eigs)
                if min_ev > 0:
                    condition_number = max_ev / min_ev

        min_eigenvalue = hess_diag.get('min_eigenvalue')
        max_eigenvalue = hess_diag.get('max_eigenvalue')
        n_negative = hess_diag.get('n_negative_eigenvalues')
        if eigenvalues_arr is not None and eigenvalues_arr.size:
            if min_eigenvalue is None:
                min_eigenvalue = float(np.nanmin(eigenvalues_arr))
            if max_eigenvalue is None:
                max_eigenvalue = float(np.nanmax(eigenvalues_arr))
            n_negative = int(np.sum(eigenvalues_arr < 0))
        if n_negative is None:
            n_negative = 0

        poorly_identified = hess_diag.get('poorly_identified_params', [])
        top_correlations = hess_diag.get('top_correlations')
        if top_correlations is None and se_results_dict is not None:
            top_correlations = build_top_correlations(
                se_results_dict.get('varcov'),
                spec.all_param_names
            )

        # Build Hessian diagnostics output
        hessian_output = {
            'condition_number': to_serializable(condition_number),
            'min_eigenvalue': to_serializable(min_eigenvalue),
            'max_eigenvalue': to_serializable(max_eigenvalue),
            'n_negative_eigenvalues': int(n_negative),
            'poorly_identified_params': poorly_identified
        }
        if eigenvalues_arr is not None:
            hessian_output['eigenvalues'] = to_serializable(eigenvalues_arr)
        if top_correlations:
            hessian_output['top_correlations'] = to_serializable(top_correlations)

        output['hessian_diagnostics'] = hessian_output

        # Also add individual SEs, t-values, p-values to each group result
        # (These come from the Hessian-based computation in GAMSPy)
        se_arr = output.get('standard_errors', {}).get('se')
        t_arr = output.get('standard_errors', {}).get('t_values')
        p_arr = output.get('standard_errors', {}).get('p_values')

        # Add to each group
        for group_name in group_keys:
            if group_name in output['results']:
                if se_arr is not None:
                    output['results'][group_name]['standard_errors'] = se_arr
                if t_arr is not None:
                    output['results'][group_name]['t_values'] = t_arr
                if p_arr is not None:
                    output['results'][group_name]['p_values'] = p_arr

                # Add Hessian diagnostics to each group result
                output['results'][group_name]['hessian_diagnostics'] = hessian_output

    # Save - ensure directory exists first
    json_path = output_dir / "estimation_results.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = json_path.with_suffix(json_path.suffix + ".tmp")
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    tmp_path.replace(json_path)

    logger.info(f"Saved results JSON: {json_path}")


def save_results_csv(
    results: dict,
    spec,
    output_dir: Path
) -> None:
    """
    Save parameter estimates to CSV files (one per group).

    Parameters
    ----------
    results : dict
        Results from estimation
    spec : EstimationSpec
        Specification used
    output_dir : Path
        Output directory
    """
    logger = logging.getLogger(__name__)

    for group_name in ['singles_male', 'singles_female', 'couples']:
        if group_name not in results:
            continue

        opt_result = results[group_name]
        params_dict = spec.unpack_parameters(opt_result.x)

        # Create DataFrame
        df = pd.DataFrame([
            {
                'parameter': name,
                'value': value,
                'specification': spec.name
            }
            for name, value in params_dict.items()
        ])

        # Save
        csv_path = output_dir / f"estimation_results_{group_name}.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved {group_name} parameters to: {csv_path}")


def save_specification_copy(spec_path: Path, output_dir: Path) -> None:
    """
    Copy specification file to output directory for reproducibility.

    Parameters
    ----------
    spec_path : Path
        Original specification file
    output_dir : Path
        Output directory
    """
    import shutil

    dest_path = output_dir / "specification_used.yaml"
    shutil.copy(spec_path, dest_path)

    logger = logging.getLogger(__name__)
    logger.info(f"Copied specification to: {dest_path}")


def _get_primary_theta(results: Dict[str, Any]) -> Optional[np.ndarray]:
    """Extract final parameter vector from joint or first available group."""
    for key in ("joint", "singles_male", "singles_female", "couples"):
        obj = results.get(key)
        if obj is not None and hasattr(obj, "x"):
            try:
                return np.asarray(obj.x, dtype=float)
            except Exception:
                return None
    return None


def _load_previous_theta(results_path: Path, spec) -> Optional[np.ndarray]:
    """Load parameter vector from a previous estimation_results.json."""
    try:
        with open(results_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None

    params = {}
    for key in ("joint", "singles_male", "singles_female", "couples"):
        group_payload = data.get("results", {}).get(key, {})
        if isinstance(group_payload, dict) and isinstance(group_payload.get("parameters"), dict):
            params = group_payload["parameters"]
            break

    if not params:
        return None

    vec = []
    for name in spec.all_param_names:
        val = params.get(name, None)
        if val is None:
            vec.append(np.nan)
        else:
            try:
                vec.append(float(val))
            except Exception:
                vec.append(np.nan)
    return np.asarray(vec, dtype=float)


def write_identification_diagnostics(
    results: Dict[str, Any],
    spec,
    output_dir: Path,
    warm_start_results_path: Optional[Path],
    theta_init: Optional[np.ndarray],
) -> Path:
    """
    Write compact identification diagnostics next to estimation results JSON.
    """
    logger = logging.getLogger(__name__)
    out_path = output_dir / "identification_diagnostics.txt"

    theta_final = _get_primary_theta(results)
    if theta_final is None:
        text = "Identification diagnostics unavailable: no final parameter vector found.\n"
        out_path.write_text(text, encoding="utf-8")
        logger.info(f"Saved identification diagnostics: {out_path}")
        return out_path

    # Bounds diagnostics
    n_lower = 0
    n_upper = 0
    hit_params: List[str] = []
    tol = 1e-8
    for idx, pname in enumerate(spec.all_param_names):
        if pname not in spec.bounds:
            continue
        lb, ub = spec.bounds[pname]
        val = float(theta_final[idx])
        if lb is not None and abs(val - float(lb)) <= tol:
            n_lower += 1
            hit_params.append(f"{pname}: lower ({lb})")
        elif ub is not None and abs(val - float(ub)) <= tol:
            n_upper += 1
            hit_params.append(f"{pname}: upper ({ub})")

    # Hessian diagnostics
    hdiag = results.get("hessian_diagnostics") if isinstance(results.get("hessian_diagnostics"), dict) else {}
    se_payload = results.get("standard_errors") if isinstance(results.get("standard_errors"), dict) else {}
    eigvals = hdiag.get("eigenvalues", se_payload.get("eigenvalues"))
    eig = np.asarray(eigvals, dtype=float) if eigvals is not None else np.array([], dtype=float)
    eig = eig[np.isfinite(eig)]
    n_neg_eig = int(np.sum(eig < 0)) if eig.size else 0
    n_near_zero = int(np.sum(np.abs(eig) <= 1e-8)) if eig.size else 0

    cond_number = hdiag.get("condition_number", se_payload.get("condition_number"))
    if cond_number is None and eig.size:
        min_abs = np.min(np.abs(eig))
        max_abs = np.max(np.abs(eig))
        cond_number = float(max_abs / min_abs) if min_abs > 0 else np.inf

    neg_variances = 0
    varcov = se_payload.get("varcov")
    if isinstance(varcov, np.ndarray):
        diag = np.diag(varcov)
        neg_variances = int(np.sum(np.isfinite(diag) & (diag < 0)))

    # Stability vs warm start / initialization
    ref_label = "initial_vector"
    ref_theta = np.asarray(theta_init, dtype=float) if theta_init is not None else None
    if warm_start_results_path is not None and warm_start_results_path.exists():
        prev_theta = _load_previous_theta(warm_start_results_path, spec)
        if prev_theta is not None:
            ref_theta = prev_theta
            ref_label = f"warm_start:{warm_start_results_path}"

    stability_lines: List[str] = []
    if ref_theta is not None and ref_theta.shape[0] == theta_final.shape[0]:
        mask = np.isfinite(ref_theta) & np.isfinite(theta_final)
        if np.any(mask):
            delta = theta_final[mask] - ref_theta[mask]
            l2 = float(np.linalg.norm(delta))
            max_abs = float(np.max(np.abs(delta)))
            mean_abs = float(np.mean(np.abs(delta)))
            ref_norm = float(np.linalg.norm(ref_theta[mask]))
            rel_l2 = l2 / (ref_norm + 1e-12)
            stability_lines.extend([
                f"reference: {ref_label}",
                f"matched_params: {int(np.sum(mask))}/{len(theta_final)}",
                f"delta_l2: {l2:.6e}",
                f"delta_l2_relative: {rel_l2:.6e}",
                f"delta_max_abs: {max_abs:.6e}",
                f"delta_mean_abs: {mean_abs:.6e}",
            ])
        else:
            stability_lines.append("reference comparison unavailable: no matched finite parameters.")
    else:
        stability_lines.append("reference comparison unavailable: no compatible reference vector.")

    lines: List[str] = []
    lines.append("Identification Diagnostics")
    lines.append("=" * 80)
    lines.append(f"specification: {spec.name}")
    lines.append(f"n_parameters: {len(spec.all_param_names)}")
    lines.append(f"bounded_hits_total: {n_lower + n_upper}")
    lines.append(f"bounded_hits_lower: {n_lower}")
    lines.append(f"bounded_hits_upper: {n_upper}")
    lines.append(f"hessian_condition_number: {cond_number}")
    lines.append(f"hessian_negative_eigenvalues: {n_neg_eig}")
    lines.append(f"hessian_near_zero_eigenvalues(|eig|<=1e-8): {n_near_zero}")
    lines.append(f"negative_variances_from_varcov: {neg_variances}")
    lines.append("")
    lines.append("Parameter Stability")
    lines.append("-" * 80)
    lines.extend(stability_lines)
    lines.append("")
    lines.append("Bound Hits")
    lines.append("-" * 80)
    if hit_params:
        lines.extend(hit_params)
    else:
        lines.append("none")
    lines.append("")
    lines.append(
        "Interpretation hints: many bound hits, negative/near-zero Hessian eigenvalues, "
        "or unstable parameters indicate weak identification."
    )
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Saved identification diagnostics: {out_path}")
    return out_path


# ==============================================================================
# Main Function
# ==============================================================================

def main():
    """Main estimation routine"""

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Enhanced RURO MNL Estimation - France",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic joint estimation (singles + couples, default spec)
  python enh_RURO_estimate_FR.py \\
    --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \\
    --output-dir "outputs/estimation/FR_2016"

  # Custom specification (LOC empirical)
  python enh_RURO_estimate_FR.py \\
    --mnl-base "..." \\
    --output-dir "..." \\
    --spec-config scripts/enhanced/specifications/estimation_spec_loc_empirical.yaml

  # Singles only (males)
  python enh_RURO_estimate_FR.py \\
    --mnl-base "..." \\
    --output-dir "..." \\
    --group singles_male

  # Joint estimation with parallelization
  python enh_RURO_estimate_FR.py \\
    --mnl-base "..." \\
    --output-dir "..." \\
    --group joint \\
    --n-jobs 4
        """
    )

    # Data inputs
    parser.add_argument(
        "--mnl-base",
        type=str,
        required=True,
        help="Base path for MNL datasets (without __singles.parquet suffix)"
    )
    parser.add_argument(
        "--metadata",
        type=str,
        default=None,
        help="Path to metadata JSON (default: {mnl_base}__mnlmeta.json)"
    )    # Specification
    parser.add_argument(
        "--spec-config",
        type=str,
        default="estimation_spec.yaml",
        help="Path to YAML specification file (default: estimation_spec.yaml)"
    )
    parser.add_argument(
        "--init-params",
        type=str,
        default=None,
        help="CSV or JSON with custom initial values (overrides spec and warm-start)"
    )
    
    # Warm-start from previous results
    parser.add_argument(
        "--warm-start",
        type=str,
        default="auto",
        help="Warm-start from previous results: 'auto' (search output dir), "
             "'none' (use spec defaults), or path to results JSON file"
    )
    parser.add_argument(
        "--warm-start-search-dir",
        type=str,
        default=None,
        help="Additional directory to search for previous results (used with --warm-start auto)"
    )
    parser.add_argument(
        "--warm-start-default",
        type=float,
        default=0.0,
        help="Default value for new parameters not in previous results (default: 0.0)"
    )

    # Estimation group
    parser.add_argument(
        "--group",
        type=str,
        default="joint",
        choices=["singles_male", "singles_female", "singles_pooled", "couples", "joint"],
        help="Which group(s) to estimate (default: joint)"
    )

    # Parallelization
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=-1,
        help="Number of parallel jobs for joint estimation (-1 = all CPUs)"
    )    # Solver selection
    parser.add_argument(
        "--solver",
        type=str,
        default="scipy",
        choices=["scipy", "gamspy-conopt", "gamspy-ipopt", "gamspy-knitro"],
        help="Optimization solver: scipy (L-BFGS-B), gamspy-conopt (2-3x faster), "
             "gamspy-ipopt, or gamspy-knitro (default: scipy)"
    )
    parser.add_argument(
        "--vectorized",
        action="store_true",
        help="Use vectorized GAMSPy implementation (3-5x faster, only for GAMSPy solvers)"
    )

    # Optimization (SciPy-specific)
    parser.add_argument(
        "--method",
        type=str,
        default=None,
        choices=["L-BFGS-B", "BFGS", "trust-constr"],
        help="SciPy optimization method (overrides spec, ignored for GAMSPy)"
    )
    parser.add_argument(
        "--maxiter",
        type=int,
        default=None,
        help="Maximum iterations (overrides spec)"
    )
    parser.add_argument(
        "--ftol",
        type=float,
        default=None,
        help="Function tolerance (overrides spec)"
    )
    parser.add_argument(
        "--solver-options",
        type=str,
        default=None,
        help="CONOPT solver options as key=value pairs separated by commas. "
             "Example: --solver-options 'Tol_Optimality=1e-9,Lim_Iteration=10000'"
    )
    parser.add_argument(
        "--no-gradient",
        action="store_true",
        help="Disable analytical gradient - SciPy only (use numerical approximation)"
    )

    # Output
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Base directory for estimation results"
    )
    parser.add_argument(
        "--no-spec-subdir",
        action="store_true",
        help="Do not create a specification-named subfolder under --output-dir"
    )
    parser.add_argument(
        "--auto-timestamp",
        action="store_true",
        help="Automatically create timestamped run folder under the selected output directory"
    )

    # Validation
    parser.add_argument(
        "--no-strict-validation",
        action="store_true",
        help="Disable strict metadata validation (not recommended)"
    )

    # Standard errors
    parser.add_argument(
        "--skip-se",
        action="store_true",
        help="Skip standard error computation (faster, but no SEs)"
    )    # Logging
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging (DEBUG level)"
    )
    
    args = parser.parse_args()

    # Resolve spec path once so it can drive folder grouping and later parsing
    spec_path = resolve_spec_path(args.spec_config)
    spec_folder_name = build_spec_folder_name(spec_path)

    # Setup output directory and logging
    output_dir_base = Path(args.output_dir)
    if not args.no_spec_subdir:
        output_dir_base = output_dir_base / spec_folder_name

    if args.auto_timestamp:
        # Create timestamped subdirectory
        timestamp = datetime.now().strftime("run_%Y-%m-%d_%H-%M-%S")
        output_dir = output_dir_base / timestamp
        print(f"Auto-timestamp enabled: {output_dir}")
    else:
        output_dir = output_dir_base
    
    output_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(output_dir, verbose=args.verbose)

    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info("Enhanced RURO MNL Estimation - France")
    logger.info("="*80)
    logger.info(f"Started: {datetime.now().isoformat()}")
    logger.info(f"Output directory: {output_dir}")
    if not args.no_spec_subdir:
        logger.info(f"Specification folder: {spec_folder_name}")
    if args.auto_timestamp:
        logger.info(f"  (Timestamped run folder created automatically)")
    logger.info("")

    try:        # ===== 1. LOAD SPECIFICATION =====
        logger.info("="*80)
        logger.info("Step 1: Loading Specification")
        logger.info("="*80)

        spec = parse_specification(spec_path)
        
        # Override optimization settings if specified
        if args.method:
            spec.opt_method = args.method
            logger.info(f"Overriding optimization method: {args.method}")
        
        if args.maxiter:
            spec.opt_max_iterations = args.maxiter
            logger.info(f"Overriding max iterations: {args.maxiter}")
        
        if args.ftol:
            spec.opt_tolerance = float(args.ftol)
            logger.info(f"Overriding tolerance: {args.ftol}")

        if args.no_gradient:
            spec.opt_analytical_gradient = False
            logger.warning("Analytical gradient disabled - optimization will be slower")

        # ===== 2. LOAD AND VALIDATE DATA =====
        logger.info("")
        logger.info("="*80)
        logger.info("Step 2: Loading and Validating Data")
        logger.info("="*80)

        mnl_base = Path(args.mnl_base)
        singles_path = Path(str(mnl_base) + "__singles.parquet")
        couples_path = Path(str(mnl_base) + "__couples.parquet")

        if args.metadata:
            metadata_path = Path(args.metadata)
        else:
            metadata_path = Path(str(mnl_base) + "__mnlmeta.json")

        df_singles, df_couples, metadata = load_and_validate_mnl_data(
            singles_path=singles_path,
            couples_path=couples_path if couples_path.exists() else None,
            metadata_path=metadata_path,
            strict_validation=not args.no_strict_validation
        )

        # ===== 3. VALIDATE DATA-SPEC COMPATIBILITY =====
        logger.info("")
        logger.info("="*80)
        logger.info("Step 3: Validating Data-Specification Compatibility")
        logger.info("="*80)

        validate_data_spec_compatibility(df_singles, df_couples, spec.__dict__, metadata)

        # ===== 4. FILTER BY GROUP =====
        logger.info("")
        logger.info("="*80)
        logger.info("Step 4: Filtering by Group")
        logger.info("="*80)

        if args.group == "singles_male":
            df_singles = df_singles[df_singles["dgn"] == 1].copy()
            df_couples = None
            logger.info("Estimating singles (males only)")

        elif args.group == "singles_female":
            df_singles = df_singles[df_singles["dgn"] == 0].copy()
            df_couples = None
            logger.info("Estimating singles (females only)")

        elif args.group == "singles_pooled":
            df_couples = None
            logger.info("Estimating singles (pooled males + females)")

        elif args.group == "couples":
            df_singles = None
            logger.info("Estimating couples only")

        elif args.group == "joint":
            logger.info("Estimating joint (singles males + females + couples)")

        # ===== 5. PRECOMPUTE DATA =====
        logger.info("")
        logger.info("="*80)
        logger.info("Step 5: Precomputing Data")
        logger.info("="*80)

        include_wage_vars = (spec.wage_spec in ["vw", "loc_empirical"])
        include_loc_vars = (spec.wage_spec == "loc_empirical")
        extra_precompute_vars_set = set()

        # Extract variables from market opportunity shifters
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
                # 'working' is part of the base precompute structure.
                if interaction_name and interaction_name != "working":
                    extra_precompute_vars_set.add(interaction_name)

        # Extract variables from leisure shifters
        for shifter in getattr(spec, "utility_leisure_shifters", []):
            if not isinstance(shifter, dict):
                continue
            var_name = shifter.get("variable")
            if isinstance(var_name, str) and var_name.strip():
                extra_precompute_vars_set.add(var_name.strip())

        extra_precompute_vars = sorted(extra_precompute_vars_set)
        if extra_precompute_vars:
            logger.info(
                "Spec-driven extra precompute variables: %s",
                extra_precompute_vars,
            )

        data_sm = None
        data_sf = None
        data_cou = None

        if df_singles is not None:
            if args.group == "singles_pooled":
                # Single dataset (pooled)
                logger.info("Precomputing pooled singles data...")
                data_sm = precompute_data_singles(
                    df=df_singles,
                    metadata=metadata,
                    is_male=True,  # Treat as male for parameter convention
                    include_wage_vars=include_wage_vars,
                    include_loc_vars=include_loc_vars,
                    include_extra_vars=extra_precompute_vars,
                )
            else:
                # Separate male/female
                df_sm = df_singles[df_singles["dgn"] == 1]
                df_sf = df_singles[df_singles["dgn"] == 0]

                if len(df_sm) > 0:
                    logger.info("Precomputing singles (male) data...")
                    data_sm = precompute_data_singles(
                        df=df_sm,
                        metadata=metadata,
                        is_male=True,
                        include_wage_vars=include_wage_vars,
                        include_loc_vars=include_loc_vars,
                        include_extra_vars=extra_precompute_vars,
                    )

                if len(df_sf) > 0:
                    logger.info("Precomputing singles (female) data...")
                    data_sf = precompute_data_singles(
                        df=df_sf,
                        metadata=metadata,
                        is_male=False,
                        include_wage_vars=include_wage_vars,
                        include_loc_vars=include_loc_vars,
                        include_extra_vars=extra_precompute_vars,
                    )

        if df_couples is not None:
            logger.info("Precomputing couples data...")
            data_cou = precompute_data_couples(
                df=df_couples,
                metadata=metadata,
                include_wage_vars=include_wage_vars,
                include_loc_vars=include_loc_vars,
                include_extra_vars=extra_precompute_vars,
            )

        # ===== 5b. VALIDATE MARKET OPPORTUNITY VARIABLES =====
        market_shifters = getattr(spec, "market_opportunity_shifters", [])
        if market_shifters:
            logger.info("Validating market opportunity variables on precomputed data...")
            for shifter in market_shifters:
                var_name = shifter.get("variable", "")
                coef_name = shifter.get("coefficient", "")
                interactions = shifter.get("interaction", [])
                if isinstance(interactions, str):
                    interactions = [interactions]
                all_vars = [var_name] + [v for v in (interactions or []) if v != "working"]
                for vn in all_vars:
                    if not vn:
                        continue
                    # Check singles
                    for data_obj, label in [(data_sm, "singles_male"), (data_sf, "singles_female")]:
                        if data_obj is not None and not hasattr(data_obj, vn):
                            logger.error(
                                "MISSING variable '%s' on %s data — "
                                "gradient for '%s' will be ZERO, SE will be 0.0!",
                                vn, label, coef_name
                            )
                    # Check couples (gender-specific)
                    if data_cou is not None:
                        for gender in ("male", "female"):
                            attr = f"{vn}_{gender}"
                            if not hasattr(data_cou, attr) and not hasattr(data_cou, vn):
                                logger.error(
                                    "MISSING variable '%s' (or '%s') on couples data — "
                                    "gradient for '%s' will be ZERO, SE will be 0.0!",
                                    attr, vn, coef_name
                                )
            logger.info("Market opportunity variable validation complete.")

        # ===== 6. GET INITIAL VALUES =====
        logger.info("")
        logger.info("="*80)
        logger.info("Step 6: Setting Initial Values")
        logger.info("="*80)

        # Determine warm-start behavior
        warm_start_results_path_used: Optional[Path] = None
        if args.warm_start.lower() == "none":
            # Use spec defaults only
            logger.info("Warm-start disabled - using specification defaults")
            theta_init = spec.get_initial_vector()
            init_sources = {p: 'spec_default' for p in spec.all_param_names}
            
        elif args.warm_start.lower() == "auto":
            # Auto-find previous results
            search_dirs = [output_dir]
            
            # Add parent directory to search (for sibling estimation folders)
            if output_dir.parent.exists():
                search_dirs.append(output_dir.parent)
            
            # Add custom search directory if specified
            if args.warm_start_search_dir:
                search_dirs.append(Path(args.warm_start_search_dir))
            
            logger.info(f"Auto-searching for previous results in: {[str(d) for d in search_dirs]}")
            theta_init, init_sources = load_warm_start_values(
                spec=spec,
                search_dirs=search_dirs,
                default_value=args.warm_start_default
            )
            
        else:
            # Explicit path to previous results
            prev_results_path = Path(args.warm_start)
            if not prev_results_path.exists():
                logger.warning(f"Warm-start file not found: {prev_results_path}")
                logger.warning("Falling back to specification defaults")
                theta_init = spec.get_initial_vector()
                init_sources = {p: 'spec_default' for p in spec.all_param_names}
            else:
                logger.info(f"Loading warm-start values from: {prev_results_path}")
                theta_init, init_sources = load_warm_start_values(
                    spec=spec,
                    results_path=prev_results_path,
                    default_value=args.warm_start_default
                )
                warm_start_results_path_used = prev_results_path

        # Override with explicit init-params if provided (highest priority)
        if args.init_params:
            logger.info(f"Overriding with custom initial values from: {args.init_params}")
            custom_init = load_custom_initial_values(Path(args.init_params))

            for param_name, value in custom_init.items():
                if param_name in spec.initial_values:
                    idx = spec.get_param_index(param_name)
                    theta_init[idx] = value
                    init_sources[param_name] = 'init_params_override'
                    logger.info(f"  {param_name} = {value}")
                else:
                    logger.warning(f"Unknown parameter in custom init: {param_name}")

        # Log summary of initial values by source
        source_counts = {}
        for src in init_sources.values():
            source_counts[src] = source_counts.get(src, 0) + 1
        logger.info(f"Initial values by source: {source_counts}")
        
        # Log the initial vector (compact format for many params)
        if len(theta_init) <= 20:
            logger.info(f"Initial vector: {theta_init}")
        else:
            logger.info(f"Initial vector (first 10): {theta_init[:10]}")
            logger.info(f"Initial vector (last 10): {theta_init[-10:]}")        # ===== 7. RUN ESTIMATION =====
        logger.info("")
        logger.info("="*80)
        logger.info("Step 7: Running Estimation")
        logger.info("="*80)
        
        # Check if using GAMSPy solver
        use_gamspy = args.solver.startswith("gamspy-")
        
        if use_gamspy:
            # Extract GAMSPy solver name (conopt, ipopt, knitro)
            gamspy_solver = args.solver.split("-")[1]
            logger.info(f"Using GAMSPy solver: {gamspy_solver.upper()}")
            logger.info("Note: GAMSPy uses automatic differentiation (no manual gradient)")

            # Parse solver options if provided
            solver_options = None
            if args.solver_options:
                solver_options = {}
                for pair in args.solver_options.split(","):
                    if "=" in pair:
                        key, value = pair.strip().split("=", 1)
                        solver_options[key.strip()] = value.strip()
                logger.info(f"Solver options: {solver_options}")

            # Import GAMSPy estimation functions
            try:
                if args.vectorized:
                    logger.info("Using VECTORIZED GAMSPy implementation (3-5x faster)")
                    from gamspy_estimation_vectorized import (
                        estimate_singles_vectorized_gamspy as estimate_singles_gamspy,
                        estimate_couples_vectorized_gamspy as estimate_couples_gamspy,
                        estimate_joint_vectorized_gamspy as estimate_joint_gamspy
                    )
                else:
                    logger.info("Using standard GAMSPy implementation")
                    from gamspy_estimation import (
                        estimate_singles_gamspy,
                        estimate_couples_gamspy,
                        estimate_joint_gamspy
                    )
            except ImportError as e:
                logger.error(f"Failed to import GAMSPy estimation module: {e}")
                logger.error("Make sure gamspy_estimation.py (or gamspy_estimation_vectorized.py) is in scripts/enhanced/")
                raise
            
            # Run estimation with GAMSPy
            if args.group == "joint":
                # Joint estimation with GAMSPy
                logger.info("="*80)
                logger.info("JOINT ESTIMATION WITH GAMSPy")
                logger.info("="*80)
                logger.info("This will estimate all three groups simultaneously with shared parameters")
                logger.info("Expected runtime: 10-16 minutes (vs 30-40 min with SciPy)")
                logger.info("="*80)
                
                gamspy_result = estimate_joint_gamspy(
                    data_singles_male=data_sm,
                    data_singles_female=data_sf,
                    data_couples=data_cou,
                    spec=spec,
                    theta_init=theta_init,  # Pass warm-start initial values!
                    solver=gamspy_solver,
                    verbose=args.verbose,
                    solver_options=solver_options
                )
                
                # Convert to format compatible with downstream code
                opt_result = GAMSPyOptimizeResult(gamspy_result)
                walltime = gamspy_result['walltime']
                
                # Create results dict in joint format
                results = {
                    'singles_male': opt_result,  # Same params for all groups
                    'singles_female': opt_result,
                    'couples': opt_result,
                    'walltimes': {
                        'singles_male': walltime / 3,  # Approximate split
                        'singles_female': walltime / 3,
                        'couples': walltime / 3,
                    },
                    'joint_ll': gamspy_result['log_likelihood'],
                    'll_breakdown': {
                        'singles_male': gamspy_result['ll_singles_male'],
                        'singles_female': gamspy_result['ll_singles_female'],
                        'couples': gamspy_result['ll_couples'],
                    },
                    'n_obs_total': data_sm.n_obs + data_sf.n_obs + data_cou.n_obs,
                    'n_groups_total': data_sm.n_groups + data_sf.n_groups + data_cou.n_groups,
                    'total_walltime': walltime,
                    'gamspy_solver': gamspy_solver,
                    # Add Hessian diagnostics if available
                    'standard_errors': gamspy_result.get('standard_errors'),
                    't_values': gamspy_result.get('t_values'),
                    'p_values': gamspy_result.get('p_values'),
                    'hessian_diagnostics': gamspy_result.get('hessian_diagnostics'),
                    'prior_correction_applied': gamspy_result.get('prior_correction_applied'),
                    'prior_correction_form': gamspy_result.get('prior_correction_form'),
                    'market_centering_applied': gamspy_result.get('market_centering_applied'),
                }
            else:
                # Single group estimation with GAMSPy
                if args.group in ["singles_male", "singles_pooled"]:
                    data = data_sm
                    group_name = args.group
                    logger.info(f"Estimating {group_name} with GAMSPy...")
                    gamspy_result = estimate_singles_gamspy(
                        data=data, spec=spec, theta_init=theta_init,
                        solver=gamspy_solver, verbose=args.verbose,
                        solver_options=solver_options
                    )

                elif args.group == "singles_female":
                    data = data_sf
                    group_name = "singles_female"
                    logger.info(f"Estimating {group_name} with GAMSPy...")
                    gamspy_result = estimate_singles_gamspy(
                        data=data, spec=spec, theta_init=theta_init,
                        solver=gamspy_solver, verbose=args.verbose,
                        solver_options=solver_options
                    )

                elif args.group == "couples":
                    data = data_cou
                    group_name = "couples"
                    logger.info(f"Estimating {group_name} with GAMSPy...")
                    gamspy_result = estimate_couples_gamspy(
                        data=data, spec=spec, theta_init=theta_init,
                        solver=gamspy_solver, verbose=args.verbose,
                        solver_options=solver_options
                    )
                
                # Convert GAMSPy result to SciPy-like OptimizeResult format
                # (for compatibility with downstream code)
                opt_result = GAMSPyOptimizeResult(gamspy_result)
                walltime = gamspy_result['walltime']
                
                # Format results
                results = {
                    group_name: opt_result,
                    'walltimes': {group_name: walltime},
                    'joint_ll': gamspy_result['log_likelihood'],
                    'n_obs_total': data.n_obs,
                    'n_groups_total': data.n_groups,
                    'total_walltime': walltime,
                    'gamspy_solver': gamspy_solver,
                    # Add Hessian diagnostics if available
                    'standard_errors': gamspy_result.get('standard_errors'),
                    't_values': gamspy_result.get('t_values'),
                    'p_values': gamspy_result.get('p_values'),
                    'hessian_diagnostics': gamspy_result.get('hessian_diagnostics'),
                    'prior_correction_applied': gamspy_result.get('prior_correction_applied'),
                    'prior_correction_form': gamspy_result.get('prior_correction_form'),
                    'market_centering_applied': gamspy_result.get('market_centering_applied'),
                }
        
        else:
            # Use SciPy estimation (original path)
            if args.group == "joint":
                # Parallel joint estimation
                results = estimate_joint(
                    data_singles_male=data_sm,
                    data_singles_female=data_sf,
                    data_couples=data_cou,
                    spec=spec,
                    n_jobs=args.n_jobs,
                    use_gradient=spec.opt_analytical_gradient,
                    theta_init=theta_init
                )
            else:
                # Single group estimation
                if args.group in ["singles_male", "singles_pooled"]:
                    data = data_sm
                    group_name = args.group
                elif args.group == "singles_female":
                    data = data_sf
                    group_name = "singles_female"
                elif args.group == "couples":
                    data = data_cou
                    group_name = "couples"

                logger.info(f"Estimating {group_name}...")

                group_name, opt_result, walltime = estimate_single_group(
                    group_name=group_name,
                    data=data,
                    spec=spec,
                    theta_init=theta_init,
                    use_gradient=spec.opt_analytical_gradient
                )

                # Format results like estimate_joint output
                results = {
                    group_name: opt_result,
                    'walltimes': {group_name: walltime},
                    'joint_ll': -opt_result.fun,
                    'n_obs_total': data.n_obs,
                    'n_groups_total': data.n_groups,
                    'total_walltime': walltime
                }

        # ===== 7b. COMPUTE STANDARD ERRORS =====
        if not args.skip_se:
            # Check if GAMSPy already provided Hessian diagnostics
            has_gamspy_hessian = (
                results.get('hessian_diagnostics') is not None and
                results.get('standard_errors') is not None
            )

            if has_gamspy_hessian:
                logger.info("")
                logger.info("="*80)
                logger.info("Step 7b: Standard Errors from GAMSPy Hessian")
                logger.info("="*80)
                logger.info("GAMSPy solver already computed Hessian-based diagnostics")
                logger.info("Skipping numerical Hessian computation (already done by GAMSPy)")

                # Count valid SEs
                se_array = results.get('standard_errors')
                if isinstance(se_array, dict):
                    n_valid = sum(1 for v in se_array.values() if v is not None and not np.isnan(v))
                    n_total = len(se_array)
                elif isinstance(se_array, np.ndarray):
                    n_valid = np.sum(~np.isnan(se_array))
                    n_total = len(se_array)
                else:
                    n_valid, n_total = 0, 0

                logger.info(f"GAMSPy provided {n_valid} valid SEs out of {n_total} parameters")

            else:
                # Compute numerical Hessian (SciPy estimation or GAMSPy didn't provide one)
                logger.info("")
                logger.info("="*80)
                logger.info("Step 7b: Computing Standard Errors (Numerical Hessian)")
                logger.info("="*80)
                logger.info("Computing numerical Hessian using finite differences...")

                from estimation_engine import compute_gradient_joint

                # Get the final theta from results
                if 'joint' in results:
                    theta_final = results['joint'].x
                    group_key = 'joint'
                else:
                    # Single group estimation
                    for key in ['singles_male', 'singles_female', 'couples']:
                        if key in results:
                            theta_final = results[key].x
                            group_key = key
                            break

                # Build gradient function for SE computation
                def grad_func_for_se(theta):
                    return compute_gradient_joint(
                        theta, data_sm, data_sf, data_cou, spec
                    )

                # Compute SEs
                se_results = compute_standard_errors(
                    theta=theta_final,
                    grad_func=grad_func_for_se,
                    eps=1e-5,
                    bounds=spec.get_bounds_tuple(),
                    logger=logger
                )

                # Store in results
                results['standard_errors'] = se_results

                logger.info(f"SE computation complete. {np.sum(~np.isnan(se_results['se']))} valid SEs out of {len(se_results['se'])}")
        else:
            logger.info("Skipping standard error computation (--skip-se flag)")
            results['standard_errors'] = None

        # ===== 8. SAVE RESULTS =====
        logger.info("")
        logger.info("="*80)
        logger.info("Step 8: Saving Results")
        logger.info("="*80)

        save_results_json(results, spec, metadata, output_dir, args, theta_init=theta_init)
        save_results_csv(results, spec, output_dir)
        save_specification_copy(spec_path, output_dir)

        # ===== 9. PRINT SUMMARY =====
        logger.info("")
        summary = format_estimation_results(results, spec)
        logger.info(summary)

        # Save summary to text file
        summary_path = output_dir / "estimation_summary.txt"
        with open(summary_path, 'w') as f:
            f.write(summary)
        logger.info(f"Saved summary to: {summary_path}")

        write_identification_diagnostics(
            results=results,
            spec=spec,
            output_dir=output_dir,
            warm_start_results_path=warm_start_results_path_used,
            theta_init=theta_init,
        )

        logger.info("")
        logger.info("="*80)
        logger.info("Estimation Complete!")
        logger.info("="*80)
        logger.info(f"Results saved to: {output_dir}")
        logger.info("")

        return 0

    except Exception as e:
        logger.error("="*80)
        logger.error("ESTIMATION FAILED")
        logger.error("="*80)
        logger.error(f"Error: {e}", exc_info=True)
        logger.error("")
        return 1


if __name__ == "__main__":
    sys.exit(main())
