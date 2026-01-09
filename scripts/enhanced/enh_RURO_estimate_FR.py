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
import sys
from datetime import datetime
from pathlib import Path

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
    load_custom_initial_values
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
    ))    logger.addHandler(fh)
    logger.addHandler(ch)


# ==============================================================================
# Standard Error Computation
# ==============================================================================

def compute_standard_errors(
    theta: np.ndarray,
    grad_func,
    eps: float = 1e-5,
    logger: logging.Logger = None
) -> Dict[str, any]:
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
    logger.info(f"Computing numerical Hessian ({n_params}x{n_params})...")
    
    # Compute Hessian numerically (central differences on gradient)
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
        
        if (i + 1) % 10 == 0:
            logger.info(f"  Hessian column {i+1}/{n_params} computed")
    
    # Symmetrize
    H = 0.5 * (H + H.T)
    
    # Compute variance-covariance matrix
    try:
        varcov = np.linalg.inv(H)
        se = np.sqrt(np.abs(np.diag(varcov)))  # abs to handle numerical issues
        
        # Check for negative variances (indicates identification problems)
        neg_var = np.diag(varcov) < 0
        if np.any(neg_var):
            n_neg = np.sum(neg_var)
            logger.warning(f"Warning: {n_neg} parameters have negative variance (identification issue)")
            se[neg_var] = np.nan
        
        # Compute t-values and p-values
        with np.errstate(divide='ignore', invalid='ignore'):
            t_values = theta / se
            p_values = 2 * (1 - norm.cdf(np.abs(t_values)))
        
        logger.info(f"Standard errors computed successfully")
        
        return {
            'se': se,
            'varcov': varcov,
            't_values': t_values,
            'p_values': p_values,
            'hessian': H,
        }
        
    except np.linalg.LinAlgError as e:
        logger.error(f"Hessian inversion failed: {e}")
        logger.error("This typically indicates model identification problems")
        
        # Return NaN for all SE
        return {
            'se': np.full(n_params, np.nan),
            'varcov': None,
            't_values': np.full(n_params, np.nan),
            'p_values': np.full(n_params, np.nan),
            'hessian': H,
        }


# ==============================================================================
# Results Export
# ==============================================================================

def save_results_json(
    results: dict,
    spec,
    metadata: dict,
    output_dir: Path,
    args: argparse.Namespace
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
    for param_name in spec.all_param_names:
        if param_name in spec.bounds:
            lb, ub = spec.bounds[param_name]
            bounds_dict[param_name] = [lb, ub]
        initial_dict[param_name] = float(spec.initial_values.get(param_name, 0.0))    # Add group results - handle both separate groups and joint estimation
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
        'total_walltime_seconds': float(results['total_walltime'])
    }

    # Save
    json_path = output_dir / "estimation_results.json"
    with open(json_path, 'w') as f:
        json.dump(output, f, indent=2)

    logger.info(f"Saved results to: {json_path}")


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
    --spec-config estimation_spec_loc_empirical.yaml

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
    )

    # Specification
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
        help="CSV with custom initial values (overrides spec)"
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
    )

    # Optimization
    parser.add_argument(
        "--method",
        type=str,
        default=None,
        choices=["L-BFGS-B", "BFGS", "trust-constr"],
        help="Optimization method (overrides spec)"
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
        "--no-gradient",
        action="store_true",
        help="Disable analytical gradient (use numerical approximation)"
    )

    # Output
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Directory for estimation results"
    )

    # Validation
    parser.add_argument(
        "--no-strict-validation",
        action="store_true",
        help="Disable strict metadata validation (not recommended)"
    )

    # Logging
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging (DEBUG level)"
    )

    args = parser.parse_args()

    # Setup output directory and logging
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(output_dir, verbose=args.verbose)

    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info("Enhanced RURO MNL Estimation - France")
    logger.info("="*80)
    logger.info(f"Started: {datetime.now().isoformat()}")
    logger.info("")

    try:
        # ===== 1. LOAD SPECIFICATION =====
        logger.info("="*80)
        logger.info("Step 1: Loading Specification")
        logger.info("="*80)

        spec_path = Path(args.spec_config)
        if not spec_path.is_absolute():        # Relative to script directory
            spec_path = Path(__file__).parent / args.spec_config

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
                    include_loc_vars=include_loc_vars
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
                        include_loc_vars=include_loc_vars
                    )

                if len(df_sf) > 0:
                    logger.info("Precomputing singles (female) data...")
                    data_sf = precompute_data_singles(
                        df=df_sf,
                        metadata=metadata,
                        is_male=False,
                        include_wage_vars=include_wage_vars,
                        include_loc_vars=include_loc_vars
                    )

        if df_couples is not None:
            logger.info("Precomputing couples data...")
            data_cou = precompute_data_couples(
                df=df_couples,
                metadata=metadata,
                include_wage_vars=include_wage_vars,
                include_loc_vars=include_loc_vars
            )

        # ===== 6. GET INITIAL VALUES =====
        logger.info("")
        logger.info("="*80)
        logger.info("Step 6: Setting Initial Values")
        logger.info("="*80)

        theta_init = spec.get_initial_vector()

        if args.init_params:
            logger.info(f"Loading custom initial values from: {args.init_params}")
            custom_init = load_custom_initial_values(Path(args.init_params))

            for param_name, value in custom_init.items():
                if param_name in spec.initial_values:
                    idx = spec.get_param_index(param_name)
                    theta_init[idx] = value
                    logger.info(f"  {param_name} = {value}")
                else:
                    logger.warning(f"Unknown parameter in custom init: {param_name}")

        logger.info(f"Initial vector: {theta_init}")

        # ===== 7. RUN ESTIMATION =====
        logger.info("")
        logger.info("="*80)
        logger.info("Step 7: Running Estimation")
        logger.info("="*80)

        if args.group == "joint":
            # Parallel joint estimation
            results = estimate_joint(
                data_singles_male=data_sm,
                data_singles_female=data_sf,
                data_couples=data_cou,
                spec=spec,
                n_jobs=args.n_jobs,
                use_gradient=spec.opt_analytical_gradient
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

        # ===== 8. SAVE RESULTS =====
        logger.info("")
        logger.info("="*80)
        logger.info("Step 8: Saving Results")
        logger.info("="*80)

        save_results_json(results, spec, metadata, output_dir, args)
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
