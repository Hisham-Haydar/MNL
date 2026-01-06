"""
==============================================================================
Parallel Joint Estimation
==============================================================================
Parallel estimation of singles (male/female) and couples using joblib.

Provides:
- estimate_joint() - Parallel execution of all three estimations
- estimate_single_group() - Worker function for one group
- Result aggregation and reporting

Author: Enhanced RURO Pipeline
Created: 2026-01-03
==============================================================================
"""

import logging
import time
from typing import Dict, Optional, Tuple

import numpy as np
import scipy.optimize

try:
    from joblib import Parallel, delayed
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False
    logging.warning("joblib not available - parallel estimation will run sequentially")

from estimation_utils import (
    PrecomputedDataSingles,
    PrecomputedDataCouples
)
from estimation_spec_parser import EstimationSpec
from estimation_engine import (
    compute_likelihood_singles,
    compute_gradient_singles,
    compute_likelihood_couples,
    compute_gradient_couples
)


def estimate_single_group(
    group_name: str,
    data: PrecomputedDataSingles | PrecomputedDataCouples,
    spec: EstimationSpec,
    theta_init: np.ndarray,
    use_gradient: bool = True
) -> Tuple[str, scipy.optimize.OptimizeResult, float]:
    """
    Worker function for estimating a single group (males, females, or couples).

    This function is designed to be called in parallel by joblib.

    Parameters
    ----------
    group_name : str
        Name of group: "singles_male", "singles_female", or "couples"
    data : PrecomputedDataSingles | PrecomputedDataCouples
        Precomputed data for this group
    spec : EstimationSpec
        Specification configuration
    theta_init : np.ndarray
        Initial parameter values
    use_gradient : bool, default=True
        Whether to use analytical gradient

    Returns
    -------
    group_name : str
        Name of group (echo back for identification)
    result : scipy.optimize.OptimizeResult
        Optimization result
    walltime : float
        Walltime in seconds
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting estimation for {group_name}...")
    logger.info(f"  Data: {data.n_groups:,} groups, {data.n_obs:,} observations")
    logger.info(f"  Parameters: {len(theta_init)}")
    logger.info(f"  Optimizer: {spec.opt_method}")

    start_time = time.time()

    # Determine likelihood and gradient functions
    if isinstance(data, PrecomputedDataSingles):
        fun = compute_likelihood_singles
        jac = compute_gradient_singles if use_gradient else None
    elif isinstance(data, PrecomputedDataCouples):
        fun = compute_likelihood_couples
        jac = compute_gradient_couples if use_gradient else None
    else:
        raise TypeError(f"Unknown data type: {type(data)}")

    # Run optimization
    result = scipy.optimize.minimize(
        fun=fun,
        x0=theta_init,
        args=(data, spec),
        jac=jac,
        method=spec.opt_method,
        bounds=spec.get_bounds_tuple(),
        options={
            'maxiter': spec.opt_max_iterations,
            'ftol': spec.opt_tolerance,
            'disp': False  # Don't print during optimization (for clean parallel output)
        }
    )

    walltime = time.time() - start_time

    logger.info(f"Completed estimation for {group_name}")
    logger.info(f"  Success: {result.success}")
    logger.info(f"  Iterations: {result.nit}")
    logger.info(f"  Final LL: {-result.fun:.2f}")
    logger.info(f"  Walltime: {walltime:.1f}s")

    return group_name, result, walltime


def estimate_joint(
    data_singles_male: Optional[PrecomputedDataSingles],
    data_singles_female: Optional[PrecomputedDataSingles],
    data_couples: Optional[PrecomputedDataCouples],
    spec: EstimationSpec,
    n_jobs: int = -1,
    use_gradient: bool = True
) -> Dict[str, any]:
    """
    Estimate singles (male/female) and couples in parallel.

    Parameters
    ----------
    data_singles_male : PrecomputedDataSingles | None
        Male singles data (None to skip)
    data_singles_female : PrecomputedDataSingles | None
        Female singles data (None to skip)
    data_couples : PrecomputedDataCouples | None
        Couples data (None to skip)
    spec : EstimationSpec
        Specification configuration
    n_jobs : int, default=-1
        Number of parallel jobs (-1 = all CPUs)
    use_gradient : bool, default=True
        Whether to use analytical gradient

    Returns
    -------
    dict
        Results dictionary with keys:
        - 'singles_male': OptimizeResult (if provided)
        - 'singles_female': OptimizeResult (if provided)
        - 'couples': OptimizeResult (if provided)
        - 'walltimes': dict mapping group_name -> walltime
        - 'joint_ll': float (sum of all LLs)
        - 'n_obs_total': int
        - 'n_groups_total': int
        - 'total_walltime': float
    """
    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info("Joint Parallel Estimation")
    logger.info("="*80)

    # Build task list
    tasks = []
    theta_init = spec.get_initial_vector()

    if data_singles_male is not None:
        tasks.append(("singles_male", data_singles_male, spec, theta_init, use_gradient))
        logger.info(f"Scheduled: singles_male ({data_singles_male.n_groups:,} groups)")

    if data_singles_female is not None:
        tasks.append(("singles_female", data_singles_female, spec, theta_init, use_gradient))
        logger.info(f"Scheduled: singles_female ({data_singles_female.n_groups:,} groups)")

    if data_couples is not None:
        tasks.append(("couples", data_couples, spec, theta_init, use_gradient))
        logger.info(f"Scheduled: couples ({data_couples.n_groups:,} groups)")

    if not tasks:
        raise ValueError("No data provided for estimation")

    logger.info(f"Total tasks: {len(tasks)}")
    logger.info(f"Parallel jobs: {n_jobs if n_jobs > 0 else 'all CPUs'}")
    logger.info("="*80)

    # Run in parallel or sequentially
    total_start = time.time()

    if HAS_JOBLIB and len(tasks) > 1 and n_jobs != 1:
        # Parallel execution
        logger.info("Running estimations in parallel...")
        results = Parallel(n_jobs=n_jobs)(
            delayed(estimate_single_group)(*task) for task in tasks
        )
    else:
        # Sequential execution
        if not HAS_JOBLIB:
            logger.warning("joblib not available - running sequentially")
        else:
            logger.info("Running estimations sequentially (n_jobs=1)")

        results = [estimate_single_group(*task) for task in tasks]

    total_walltime = time.time() - total_start

    # Aggregate results
    logger.info("="*80)
    logger.info("Aggregating results...")

    output = {
        'walltimes': {},
        'joint_ll': 0.0,
        'n_obs_total': 0,
        'n_groups_total': 0,
        'total_walltime': total_walltime
    }

    for group_name, result, walltime in results:
        output[group_name] = result
        output['walltimes'][group_name] = walltime
        output['joint_ll'] += -result.fun  # Convert back to positive LL

        # Count observations
        if group_name == "singles_male":
            output['n_obs_total'] += data_singles_male.n_obs
            output['n_groups_total'] += data_singles_male.n_groups
        elif group_name == "singles_female":
            output['n_obs_total'] += data_singles_female.n_obs
            output['n_groups_total'] += data_singles_female.n_groups
        elif group_name == "couples":
            output['n_obs_total'] += data_couples.n_obs
            output['n_groups_total'] += data_couples.n_groups

    # Summary
    logger.info("="*80)
    logger.info("Joint Estimation Complete")
    logger.info("="*80)
    logger.info(f"Total observations: {output['n_obs_total']:,}")
    logger.info(f"Total groups: {output['n_groups_total']:,}")
    logger.info(f"Joint log-likelihood: {output['joint_ll']:.2f}")
    logger.info(f"Total walltime: {total_walltime:.1f}s")
    logger.info("")

    for group_name in ['singles_male', 'singles_female', 'couples']:
        if group_name in output:
            result = output[group_name]
            wt = output['walltimes'][group_name]
            logger.info(f"{group_name}:")
            logger.info(f"  Success: {result.success}")
            logger.info(f"  Iterations: {result.nit}")
            logger.info(f"  LL: {-result.fun:.2f}")
            logger.info(f"  Walltime: {wt:.1f}s")

    logger.info("="*80)

    return output


def format_estimation_results(
    results: Dict[str, any],
    spec: EstimationSpec
) -> str:
    """
    Format estimation results as a human-readable string.

    Parameters
    ----------
    results : dict
        Results from estimate_joint()
    spec : EstimationSpec
        Specification used

    Returns
    -------
    str
        Formatted results string
    """
    lines = []
    lines.append("="*80)
    lines.append("ESTIMATION RESULTS SUMMARY")
    lines.append("="*80)
    lines.append(f"Specification: {spec.name}")
    lines.append(f"Wage specification: {spec.wage_spec}")
    lines.append(f"Optimization method: {spec.opt_method}")
    lines.append(f"Analytical gradient: {spec.opt_analytical_gradient}")
    lines.append("")
    lines.append(f"Total observations: {results['n_obs_total']:,}")
    lines.append(f"Total groups: {results['n_groups_total']:,}")
    lines.append(f"Joint log-likelihood: {results['joint_ll']:.2f}")
    lines.append(f"Total walltime: {results['total_walltime']:.1f}s")
    lines.append("")

    for group_name in ['singles_male', 'singles_female', 'couples']:
        if group_name not in results:
            continue

        result = results[group_name]
        walltime = results['walltimes'][group_name]

        lines.append("-"*80)
        lines.append(f"{group_name.upper()}")
        lines.append("-"*80)
        lines.append(f"Success: {result.success}")
        lines.append(f"Message: {result.message}")
        lines.append(f"Iterations: {result.nit}")
        lines.append(f"Function evaluations: {result.nfev}")
        lines.append(f"Final LL: {-result.fun:.4f}")
        lines.append(f"Gradient norm: {np.linalg.norm(result.jac):.6e}")
        lines.append(f"Walltime: {walltime:.1f}s")
        lines.append("")

        # Parameter estimates
        lines.append("Parameter estimates:")
        params_dict = spec.unpack_parameters(result.x)
        for param_name, value in params_dict.items():
            lines.append(f"  {param_name:<20} = {value:>12.6f}")

        lines.append("")

    lines.append("="*80)

    return "\n".join(lines)


# ==============================================================================
# End of parallel_estimation.py
# ==============================================================================
