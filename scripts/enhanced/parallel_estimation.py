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


def verify_gradient_finite_difference(
    theta: np.ndarray,
    data,
    spec: EstimationSpec,
    likelihood_fn,
    gradient_fn,
) -> Dict[str, any]:
    """
    Verify analytical gradient using finite differences.

    Parameters
    ----------
    theta : np.ndarray
        Parameter vector to check
    data : PrecomputedDataSingles | PrecomputedDataCouples
        Data for evaluation
    spec : EstimationSpec
        Specification
    likelihood_fn : callable
        Likelihood function: f(theta, data, spec) -> float
    gradient_fn : callable
        Gradient function: g(theta, data, spec) -> np.ndarray

    Returns
    -------
    dict
        - max_rel_error: float
        - max_abs_error: float
        - param_errors: np.ndarray
        - passed: bool
        - details: str (formatted report)
    """
    logger = logging.getLogger(__name__)
    epsilon = spec.grad_verify_epsilon
    method = spec.grad_verify_method
    tol = spec.grad_verify_tolerance
    bounds = spec.get_bounds_tuple()

    # Compute analytical gradient
    grad_analytical = gradient_fn(theta, data, spec)

    # Compute numerical gradient with bounds checking
    grad_numerical = np.zeros_like(theta)
    n_params = len(theta)

    for i in range(n_params):
        lb, ub = bounds[i]

        if method == 'central':
            # Central difference: f'(x) ≈ [f(x+ε) - f(x-ε)] / 2ε
            theta_plus = theta.copy()
            theta_minus = theta.copy()

            # Check bounds before stepping
            step_plus = epsilon
            step_minus = epsilon

            if ub is not None and theta[i] + step_plus > ub:
                step_plus = ub - theta[i]  # Reduce step to stay in bounds
            if lb is not None and theta[i] - step_minus < lb:
                step_minus = theta[i] - lb  # Reduce step to stay in bounds

            theta_plus[i] = theta[i] + step_plus
            theta_minus[i] = theta[i] - step_minus

            f_plus = likelihood_fn(theta_plus, data, spec)
            f_minus = likelihood_fn(theta_minus, data, spec)
            grad_numerical[i] = (f_plus - f_minus) / (step_plus + step_minus)

        else:  # forward
            # Forward difference: f'(x) ≈ [f(x+ε) - f(x)] / ε
            theta_plus = theta.copy()
            step = epsilon

            if ub is not None and theta[i] + step > ub:
                step = ub - theta[i]

            theta_plus[i] = theta[i] + step
            f_plus = likelihood_fn(theta_plus, data, spec)
            f_0 = likelihood_fn(theta, data, spec)
            grad_numerical[i] = (f_plus - f_0) / step

    # Compute errors
    abs_errors = np.abs(grad_analytical - grad_numerical)
    rel_errors = abs_errors / (np.abs(grad_analytical) + 1e-12)

    max_abs_error = np.max(abs_errors)
    max_rel_error = np.max(rel_errors)
    passed = max_rel_error < tol

    # Build detailed report
    details = []
    details.append(f"Gradient Verification ({method} differences, ε={epsilon:.2e})")
    details.append("=" * 80)
    details.append(f"{'Parameter':<25} {'Analytical':>15} {'Numerical':>15} {'Abs Error':>15} {'Rel Error':>15}")
    details.append("-" * 80)

    for i in range(min(n_params, 20)):  # Show first 20 params
        param_name = spec.all_param_names[i] if i < len(spec.all_param_names) else f"param_{i}"
        details.append(
            f"{param_name:<25} {grad_analytical[i]:>15.6e} {grad_numerical[i]:>15.6e} "
            f"{abs_errors[i]:>15.6e} {rel_errors[i]:>15.6e}"
        )

    if n_params > 20:
        details.append(f"... ({n_params - 20} more parameters)")

    details.append("=" * 80)
    details.append(f"Max absolute error: {max_abs_error:.6e}")
    details.append(f"Max relative error: {max_rel_error:.6e}")
    details.append(f"Tolerance: {tol:.6e}")
    details.append(f"Status: {'✓ PASSED' if passed else '✗ FAILED'}")

    return {
        'max_rel_error': float(max_rel_error),
        'max_abs_error': float(max_abs_error),
        'param_errors': rel_errors,
        'passed': passed,
        'details': '\n'.join(details)
    }


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

    if getattr(spec, "expression_constraints_enabled", False) and use_gradient:
        logger.warning(
            f"[{group_name}] Expression constraints enabled: disabling analytical gradient "
            "for SciPy optimization to keep objective/gradient consistent."
        )
        use_gradient = False

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

    # ========================================================================
    # GRADIENT VERIFICATION (if enabled)
    # ========================================================================
    if spec.grad_verify_enabled and use_gradient:
        logger.info(f"[{group_name}] Running gradient verification...")

        # Check at initial values
        if spec.grad_verify_at_init:
            logger.info(f"[{group_name}] Checking gradient at initial values...")

            verify_result = verify_gradient_finite_difference(
                theta_init, data, spec, fun, jac
            )

            if spec.grad_verify_verbose:
                logger.info(f"\n{verify_result['details']}")

            if not verify_result['passed']:
                logger.error(
                    f"[{group_name}] Gradient verification FAILED at initial values!\n"
                    f"Max relative error: {verify_result['max_rel_error']:.6e} "
                    f"(tolerance: {spec.grad_verify_tolerance:.6e})\n"
                    f"This indicates a bug in the analytical gradient computation."
                )
                raise ValueError(f"Gradient verification failed for {group_name}")
            else:
                logger.info(
                    f"[{group_name}] ✓ Gradient verification PASSED "
                    f"(max rel error: {verify_result['max_rel_error']:.6e})"
                )

    # Build options dict with EXPLICIT tolerances
    options = {
        'maxiter': spec.opt_max_iterations,
        'ftol': spec.opt_tolerance,           # Function value tolerance
        'gtol': spec.opt_gradient_tolerance,  # Gradient norm tolerance - NEW!
        'disp': spec.opt_display_convergence,
        'maxfun': 15000,  # Explicit max function evaluations
    }

    # L-BFGS-B specific: control iteration printing
    if spec.opt_method == 'L-BFGS-B':
        options['iprint'] = spec.opt_iprint if hasattr(spec, 'opt_iprint') else -1

    logger.info(f"[{group_name}] Optimizer settings:")
    logger.info(f"  method: {spec.opt_method}")
    logger.info(f"  ftol: {options['ftol']:.2e}")
    logger.info(f"  gtol: {options['gtol']:.2e}")
    logger.info(f"  maxiter: {options['maxiter']}")

    # Run optimization
    result = scipy.optimize.minimize(
        fun=fun,
        x0=theta_init,
        args=(data, spec),
        jac=jac,
        method=spec.opt_method,
        bounds=spec.get_bounds_tuple(),
        options=options
    )

    walltime = time.time() - start_time

    # ========================================================================
    # KKT-AWARE CONVERGENCE DIAGNOSTICS
    # ========================================================================
    if result.success:
        grad = result.jac  # Full gradient from optimizer
        grad_norm_full = np.linalg.norm(grad)
        grad_inf_norm = np.linalg.norm(grad, ord=np.inf)

        # Compute projected gradient (accounting for bounds)
        grad_proj = grad.copy()
        bounds = spec.get_bounds_tuple()
        theta_final = result.x

        n_at_lower = 0
        n_at_upper = 0
        bound_tol = 1e-8
        params_at_bounds = []

        for i in range(len(theta_final)):
            lb, ub = bounds[i]
            param_name = spec.all_param_names[i] if i < len(spec.all_param_names) else f"param_{i}"

            # At lower bound: project out positive gradient components
            if lb is not None and abs(theta_final[i] - lb) < bound_tol:
                if grad[i] > 0:  # Gradient pointing into feasible region
                    grad_proj[i] = 0.0
                n_at_lower += 1
                params_at_bounds.append(f"{param_name} (at lower={lb:.6f}, grad={grad[i]:.3e})")

            # At upper bound: project out negative gradient components
            elif ub is not None and abs(theta_final[i] - ub) < bound_tol:
                if grad[i] < 0:  # Gradient pointing into feasible region
                    grad_proj[i] = 0.0
                n_at_upper += 1
                params_at_bounds.append(f"{param_name} (at upper={ub:.6f}, grad={grad[i]:.3e})")

        grad_norm_proj = np.linalg.norm(grad_proj)
        grad_inf_proj = np.linalg.norm(grad_proj, ord=np.inf)

        # Identify parameters with largest gradient components
        grad_abs = np.abs(grad)
        top_indices = np.argsort(grad_abs)[-10:][::-1]  # Top 10 by magnitude

        logger.info(f"[{group_name}] Convergence Diagnostics:")
        logger.info(f"  Optimizer message: {result.message}")
        logger.info(f"  Full gradient norm (L2):       {grad_norm_full:.6e}")
        logger.info(f"  Full gradient norm (L∞):       {grad_inf_norm:.6e}")
        logger.info(f"  Projected gradient norm (L2):  {grad_norm_proj:.6e}")
        logger.info(f"  Projected gradient norm (L∞):  {grad_inf_proj:.6e}")
        logger.info(f"  Parameters at lower bound: {n_at_lower}")
        logger.info(f"  Parameters at upper bound: {n_at_upper}")

        if params_at_bounds:
            logger.info(f"  Parameters at bounds:")
            for param_str in params_at_bounds:
                logger.info(f"    {param_str}")

        # Component-wise gradient report
        logger.info(f"  Top 10 gradient components:")
        for idx in top_indices:
            param_name = spec.all_param_names[idx] if idx < len(spec.all_param_names) else f"param_{idx}"
            at_bound = ""
            if bounds[idx][0] is not None and abs(theta_final[idx] - bounds[idx][0]) < bound_tol:
                at_bound = " (at lower bound)"
            elif bounds[idx][1] is not None and abs(theta_final[idx] - bounds[idx][1]) < bound_tol:
                at_bound = " (at upper bound)"

            logger.info(
                f"    {param_name:<25} grad={grad[idx]:>12.6e} "
                f"value={theta_final[idx]:>10.6f}{at_bound}"
            )

        # Convergence assessment
        if grad_norm_proj > 10.0:
            logger.warning(
                f"⚠️  [{group_name}] HIGH PROJECTED GRADIENT NORM: {grad_norm_proj:.2f}\n"
                f"    Convergence is questionable even after accounting for bounds.\n"
                f"    Recommendations:\n"
                f"    1. Tighten ftol/gtol in optimization settings\n"
                f"    2. Increase max_iterations to allow more steps\n"
                f"    3. Review bounds on parameters at constraints"
            )
        elif grad_norm_proj > 1.0:
            logger.warning(
                f"⚠️  [{group_name}] Moderate projected gradient norm: {grad_norm_proj:.2f}\n"
                f"    May not be fully converged. Consider tightening tolerances."
            )
        else:
            logger.info(f"✓ [{group_name}] Projected gradient norm acceptable: {grad_norm_proj:.6e}")

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
    theta_init: Optional[np.ndarray] = None,
    n_jobs: int = -1,
    use_gradient: bool = True
) -> Dict[str, any]:
    """
    Estimate all groups jointly using a single optimization.

    This function performs TRUE joint estimation by summing the likelihoods
    and gradients from all groups at each iteration. This is required for
    the 4-group architecture where parameters are shared across groups.

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
        IGNORED for joint estimation (kept for API compatibility)
    use_gradient : bool, default=True
        Whether to use analytical gradient

    Returns
    -------
    dict
        Results dictionary with keys:
        - 'joint': OptimizeResult from joint optimization
        - 'walltimes': dict with total walltime
        - 'joint_ll': float (final log-likelihood)
        - 'n_obs_total': int
        - 'n_groups_total': int
        - 'total_walltime': float
    """
    from estimation_engine import compute_likelihood_joint, compute_gradient_joint
    from scipy.optimize import minimize

    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info("Joint Estimation (4-Group Architecture)")
    logger.info("="*80)

    # Count observations
    n_obs_total = 0
    n_groups_total = 0

    if data_singles_male is not None:
        n_obs_total += data_singles_male.n_obs
        n_groups_total += data_singles_male.n_groups
        logger.info(f"Singles male: {data_singles_male.n_groups:,} groups, {data_singles_male.n_obs:,} obs")

    if data_singles_female is not None:
        n_obs_total += data_singles_female.n_obs
        n_groups_total += data_singles_female.n_groups
        logger.info(f"Singles female: {data_singles_female.n_groups:,} groups, {data_singles_female.n_obs:,} obs")

    if data_couples is not None:
        n_obs_total += data_couples.n_obs
        n_groups_total += data_couples.n_groups
        logger.info(f"Couples: {data_couples.n_groups:,} groups, {data_couples.n_obs:,} obs")

    logger.info(f"Total: {n_groups_total:,} groups, {n_obs_total:,} observations")
    logger.info(f"Parameters: {len(spec.all_param_names)}")
    logger.info("="*80)

    # Get initial values
    if theta_init is None:
        theta_init = spec.get_initial_vector()

    if getattr(spec, "expression_constraints_enabled", False) and use_gradient:
        logger.warning(
            "Expression constraints enabled: disabling analytical gradient for joint SciPy optimization."
        )
        use_gradient = False

    # Build objective function
    def objective(theta):
        return compute_likelihood_joint(
            theta, data_singles_male, data_singles_female, data_couples, spec
        )

    # Build gradient function
    jac = None
    if use_gradient:
        def jac(theta):
            return compute_gradient_joint(
                theta, data_singles_male, data_singles_female, data_couples, spec
            )

    # Build bounds
    bounds_list = []
    for param_name in spec.all_param_names:
        if param_name in spec.bounds:
            bounds_list.append(spec.bounds[param_name])
        else:
            bounds_list.append((None, None))    # Run optimization
    logger.info("Starting joint optimization...")
    logger.info(f"Method: {spec.opt_method}")
    logger.info(f"Max iterations: {spec.opt_max_iterations}")
    logger.info(f"Analytical gradient: {use_gradient}")
    logger.info("="*80)

    total_start = time.time()
    
    # Iteration counter and callback for progress logging
    iteration_state = {'count': 0, 'last_f': None}
    
    def iteration_callback(xk):
        """Callback function to log iteration progress."""
        iteration_state['count'] += 1
        iter_num = iteration_state['count']
          # Compute current objective value
        current_f = objective(xk)
        
        # Log every iteration or every 10 iterations based on verbosity
        if iter_num <= 10 or iter_num % 10 == 0:
            # Show a subset of key parameters
            param0_name = spec.all_param_names[0] if len(spec.all_param_names) > 0 else "param0"
            param1_name = spec.all_param_names[1] if len(spec.all_param_names) > 1 else "param1"
            param0_val = xk[0] if len(xk) > 0 else 0
            param1_val = xk[1] if len(xk) > 1 else 0
            logger.info(
                f"Iter {iter_num:4d}: neg_LL = {current_f:14.4f}, "
                f"LL = {-current_f:14.4f}, "
                f"{param0_name} = {param0_val:.4f}, {param1_name} = {param1_val:.4f}"
            )
        
        iteration_state['last_f'] = current_f

    result = minimize(
        objective,
        theta_init,
        method=spec.opt_method,
        jac=jac,
        bounds=bounds_list,
        callback=iteration_callback,
        options={
            'maxiter': spec.opt_max_iterations,
            'ftol': spec.opt_tolerance,
            'gtol': spec.opt_gradient_tolerance,
            'disp': spec.opt_display_convergence,
            'iprint': spec.opt_iprint
        }
    )

    total_walltime = time.time() - total_start

    # Summary
    logger.info("="*80)
    logger.info("Joint Estimation Complete")
    logger.info("="*80)
    logger.info(f"Success: {result.success}")
    logger.info(f"Message: {result.message}")
    logger.info(f"Iterations: {result.nit}")
    logger.info(f"Function evaluations: {result.nfev}")
    logger.info(f"Final negative LL: {result.fun:.6f}")
    logger.info(f"Final LL: {-result.fun:.6f}")
    logger.info(f"Walltime: {total_walltime:.1f}s")
    logger.info("="*80)

    # Package results
    output = {
        'joint': result,
        'walltimes': {'joint': total_walltime},
        'joint_ll': -result.fun,
        'n_obs_total': n_obs_total,
        'n_groups_total': n_groups_total,
        'total_walltime': total_walltime
    }

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

    Returns    -------
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
    if results.get("prior_correction_applied"):
        lines.append(
            f"Proposal correction: {results.get('prior_correction_form', '-log(prior)')} "
            "(applied once per alternative)"
        )
    if results.get("market_centering_applied"):
        lines.append("Opportunity centering: enabled within each choice set")
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
        
        # Gradient norm (only available for SciPy, not GAMSPY)
        if result.jac is not None:
            lines.append(f"Gradient norm: {np.linalg.norm(result.jac):.6e}")
        else:
            lines.append(f"Gradient norm: N/A (GAMSPY uses automatic differentiation)")
        
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
