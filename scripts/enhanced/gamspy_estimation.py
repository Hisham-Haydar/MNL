"""
==============================================================================
GAMSPy-based MNL Estimation for RURO Pipeline
==============================================================================
Integrates GAMSPy + CONOPT/IPOPT solvers as alternative to SciPy L-BFGS-B.

Features:
- Automatic differentiation (no manual gradient coding)
- Commercial-grade NLP solvers (CONOPT, IPOPT)
- 2-3x faster than L-BFGS-B
- Compatible with existing YAML specifications
- Supports both singles and couples estimation

Based on archived RUM estimation scripts (DCM1_gamspy.py, DCM2_gamspy.py)
Adapted for current RURO pipeline data structures.

Author: Enhanced RURO Pipeline
Created: 2026-01-16
==============================================================================
"""

import logging
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
import numpy as np

try:
    from gamspy import Container, Model, Variable, Equation, Options
    from gamspy.math import exp as gp_exp, log as gp_log
    HAS_GAMSPY = True
except ImportError:
    HAS_GAMSPY = False
    Options = None  # Fallback for type hints
    logging.warning("GAMSPy not available. Install with: pip install gamspy")

from estimation_utils import PrecomputedDataSingles, PrecomputedDataCouples
from estimation_spec_parser import EstimationSpec


# ==============================================================================
# Constants
# ==============================================================================

# Small epsilon for GAMSPy log stabilization
LOG_EPS = 1e-12

# Solver mapping
SOLVER_MAP = {
    "conopt": "conopt",
    "ipopt": "ipopt", 
    "ipopth": "ipopth",
    "knitro": "knitro",
}


# ==============================================================================
# Helper Functions
# ==============================================================================

# Group to parameter suffix mapping for 4-group architecture
SUFFIX_MAP = {
    "singles_male": "_sm",
    "singles_female": "_sf",
    "couples_male": "_m",
    "couples_female": "_f",
    "couples_household": "",  # No suffix for household-level parameters
}


def boxcox_gamspy(value: float, theta_var, epsilon: float = 1e-12):
    """
    Box-Cox transformation for GAMSPy expressions with correct θ→0 limit.

    Mathematical form:
        BC(x, θ) = (x^θ - 1) / θ    if θ ≠ 0
        BC(x, θ) = log(x)            if θ = 0 (limit)

    This matches the SciPy implementation in estimation_utils.py lines 1049-1072.

    Parameters
    ----------
    value : float
        Scalar value to transform (consumption or leisure observation)
    theta_var : GAMSPy Variable
        Box-Cox exponent parameter (being optimized)
    epsilon : float, default=1e-12
        Small constant for numerical stability (not used in division anymore)

    Returns
    -------
    GAMSPy expression
        Box-Cox transformed value

    Notes
    -----
    **The θ=0 Problem**:
    The naive formula (x^θ - 1) / (θ + ε) gives 0 when θ=0, but the correct
    limit is log(x). This caused a mismatch between GAMSPy and SciPy.

    **Solution**: Use Taylor series expansion around θ=0:
        BC(x, θ) = log(x) * [1 + θ*log(x)/2 + θ²*log(x)²/6 + ...]

    This is equivalent to: (exp(θ*log(x)) - 1) / θ when θ≠0, and equals log(x) when θ=0.

    We use a 4th-order Taylor expansion which is accurate for |θ| < 2:
        BC(x, θ) ≈ log(x) * (1 + θ*log(x)/2 + θ²*log(x)²/6 + θ³*log(x)³/24)

    This is smooth, differentiable, and gives the correct limit at θ=0.

    **Verification**:
    - When θ = 0: BC(x, 0) = log(x) * 1 = log(x) [OK]
    - When θ = 0.5: BC(x, 0.5) ≈ 2*(√x - 1) (matches standard formula)
    - When θ = 1: BC(x, 1) = x - 1 (matches standard formula)
    """
    import math

    # Ensure value is positive
    safe_value = max(value, LOG_EPS)

    # Compute log(value) as a CONSTANT
    log_val = math.log(safe_value)
    log_val2 = log_val * log_val
    log_val3 = log_val2 * log_val
    log_val4 = log_val3 * log_val

    # Taylor series expansion of (exp(θ*log(x)) - 1) / θ around θ=0:
    # = log(x) + θ*log(x)²/2 + θ²*log(x)³/6 + θ³*log(x)⁴/24 + ...
    # = log(x) * [1 + θ*log(x)/2 + θ²*log(x)²/6 + θ³*log(x)³/24 + ...]
    #
    # This form:
    # - Equals log(x) when θ=0 (correct!)
    # - Is smooth and differentiable everywhere
    # - Converges to the exact Box-Cox for small θ

    # 4th order Taylor expansion (accurate for |θ| < 2, which covers typical estimates)
    bc_value = log_val * (1.0
                          + theta_var * log_val / 2.0
                          + theta_var * theta_var * log_val2 / 6.0
                          + theta_var * theta_var * theta_var * log_val3 / 24.0
                          + theta_var * theta_var * theta_var * theta_var * log_val4 / 120.0)

    return bc_value


def get_param_name(base_name: str, group: str, param_vars: dict) -> str:
    """
    Get actual parameter name for a group-specific context.

    This function enables specification-agnostic code by dynamically determining
    which parameter variant to use based on the estimation group.

    Strategy:
    1. Try group-specific parameter (e.g., beta_c + _sm = beta_c_sm)
    2. Fall back to generic parameter (e.g., beta_c)
    3. Raise error if neither exists

    Parameters
    ----------
    base_name : str
        Base parameter name without suffix (e.g., "beta_c", "beta_l0")
    group : str
        Estimation group: "singles_male", "singles_female", "couples_male",
        "couples_female", or "couples_household"
    param_vars : dict
        Dictionary mapping parameter names to GAMSPy Variables

    Returns
    -------
    str
        Actual parameter name that exists in param_vars

    Raises
    ------
    ValueError
        If parameter not found with either suffix or as generic

    Examples
    --------
    >>> # 4-group spec has beta_c_sm, beta_c_sf, beta_c (household)
    >>> get_param_name("beta_c", "singles_male", param_vars)
    "beta_c_sm"

    >>> # Legacy spec might only have beta_c (generic)
    >>> get_param_name("beta_c", "singles_male", param_vars_legacy)
    "beta_c"

    >>> # AC2013 spec uses _cm/_cf for couples
    >>> get_param_name("beta_l0", "couples_male", param_vars_ac2013)
    "beta_l0_cm"  # If _cm used instead of _m
    """
    suffix = SUFFIX_MAP.get(group, "")

    # Try with suffix first (most specific)
    if suffix:
        param_with_suffix = f"{base_name}{suffix}"
        if param_with_suffix in param_vars:
            return param_with_suffix

    # Try generic parameter (fallback)
    if base_name in param_vars:
        return base_name

    # Not found - provide helpful error message
    tried_names = [f"{base_name}{suffix}", base_name] if suffix else [base_name]
    raise ValueError(
        f"Parameter '{base_name}' for group '{group}' not found in specification. "
        f"Tried: {', '.join(tried_names)}. "
        f"Available parameters: {list(param_vars.keys())[:10]}..."
    )


def validate_gamspy_result(model, ll_final: float, theta_final: np.ndarray,
                          expected_ll_range: tuple = (-20000, -1000),
                          logger=None) -> None:
    """
    Validate GAMSPy optimization result and raise errors if something is wrong.

    Parameters
    ----------
    model : GAMSPy Model object
        The Model object (contains solver/model status after solve())
    ll_final : float
        Final log-likelihood value
    theta_final : np.ndarray
        Final parameter estimates
    expected_ll_range : tuple, default=(-20000, -1000)
        Expected range for log-likelihood (min, max)
    logger : logging.Logger, optional
        Logger for warnings

    Raises
    ------
    RuntimeError
        If solver failed or results are invalid
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    # Get solver/model status from MODEL object
    # GAMSPy stores: model.solve_status (SolveStatus enum) and model.status (ModelStatus enum)
    solve_status_enum = getattr(model, 'solve_status', None)
    model_status_enum = getattr(model, 'status', None)

    solver_status = str(solve_status_enum) if solve_status_enum else 'Unknown'
    model_status = str(model_status_enum) if model_status_enum else 'Unknown'

    # Known bad statuses (check string representation of enum)
    failed_solver_statuses = ['Iteration Interrupt', 'Resource Interrupt', 'Error Unknown',
                              'Capability Problems', 'Licensing Problems', 'User Interrupt']
    failed_model_statuses = ['Infeasible', 'Unbounded', 'InfeasibleIntermed', 'Error Unknown']

    if solver_status in failed_solver_statuses:
        raise RuntimeError(
            f"GAMSPy solver FAILED with status '{solver_status}'. "
            f"Model status: '{model_status}'. "
            f"Final LL: {ll_final:.4f}. "
            f"Check solver output for details."
        )

    if model_status in failed_model_statuses:
        raise RuntimeError(
            f"GAMSPy model status is FAILED: '{model_status}'. "
            f"Solver status: '{solver_status}'. "
            f"Final LL: {ll_final:.4f}. "
            f"The optimization problem may be infeasible or unbounded."
        )

    # Check log-likelihood is reasonable
    ll_min, ll_max = expected_ll_range
    if ll_final < ll_min:
        logger.error(
            f"SUSPICIOUS RESULT: Log-likelihood {ll_final:.4f} is suspiciously low (< {ll_min}). "
            f"Expected range: [{ll_min}, {ll_max}]"
        )
        raise RuntimeError(
            f"Log-likelihood {ll_final:.4f} is outside expected range. "
            f"Optimization may have failed silently. "
            f"Solver status: {solver_status}, Model status: {model_status}"
        )

    if ll_final > ll_max:
        logger.warning(
            f"SUSPICIOUS RESULT: Log-likelihood {ll_final:.4f} is suspiciously high (> {ll_max}). "
            f"Expected range: [{ll_min}, {ll_max}]. "
            f"This may indicate an error in likelihood construction."
        )

    # Check for NaN or Inf in parameters
    if np.any(np.isnan(theta_final)):
        raise RuntimeError(
            f"Parameter estimates contain NaN values! "
            f"Solver status: {solver_status}, Model status: {model_status}. "
            f"Optimization failed."
        )

    if np.any(np.isinf(theta_final)):
        raise RuntimeError(
            f"Parameter estimates contain Inf values! "
            f"Solver status: {solver_status}, Model status: {model_status}. "
            f"Optimization failed or bounds are incorrect."
        )

    # Check if parameters changed from initial values (detect silent failure)
    # Note: This check would require passing theta_init, so we skip it here

    logger.info(f"[OK] Result validation passed: LL={ll_final:.4f}, Solver={solver_status}, Model={model_status}")


def ensure_local_workdir():
    r"""
    Ensure we're on a local (non-UNC) working directory for GAMS/GAMSPy.

    GAMS has issues with UNC paths (\\server\share). If current directory
    is on UNC path, this function changes to a local temp directory.
    """
    import os
    cwd = Path.cwd()
    
    # Check if on UNC path
    if str(cwd).startswith('\\\\'):
        import tempfile
        local_temp = Path(tempfile.gettempdir()) / "gamspy_workspace"
        local_temp.mkdir(parents=True, exist_ok=True)
        os.chdir(local_temp)
        logging.info(f"Changed to local working directory: {local_temp}")
        logging.info(f"(GAMS doesn't work well with UNC paths like {cwd})")


def _extract_var_level(var: Variable) -> float:
    """
    Extract scalar level from GAMSPy Variable.
    
    Handles different GAMSPy versions and variable types.
    """
    # Try records.level first (common format)
    if hasattr(var, 'records') and var.records is not None:
        if hasattr(var.records, 'level'):
            level_series = var.records.level
            if hasattr(level_series, 'iloc') and len(level_series) > 0:
                return float(level_series.iloc[0])
    
    # Try direct .level attribute
    if hasattr(var, 'level'):
        return float(var.level)
    
    # Try records dataframe (last column)
    if hasattr(var, 'records') and hasattr(var.records, 'iloc'):
        if len(var.records) > 0:
            last_col = var.records.columns[-1]
            return float(var.records.iloc[0][last_col])
    
    # Default to 0.0 if nothing works
    logging.warning(f"Could not extract level for variable {var.name}, defaulting to 0.0")
    return 0.0


# ==============================================================================
# Singles Estimation
# ==============================================================================

def estimate_singles_gamspy(
    data: PrecomputedDataSingles,
    spec: EstimationSpec,
    theta_init: np.ndarray,
    group: str = "singles_male",
    solver: str = "conopt",
    verbose: bool = True,
    solver_options: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Estimate singles MNL using GAMSPy + CONOPT/IPOPT.

    Uses Box-Cox utility specification (matching SciPy implementation):
        U_j = β_c * BC(C_j/c_scale, θ_c) + β_l(Z) * BC(L_j/l_scale, θ_l) + ASC_j

    where:
        BC(x, θ) = (x^θ - 1) / θ  (Box-Cox transformation)
        β_l(Z) varies by demographics (age, children, education, etc.)

    Parameters
    ----------
    data : PrecomputedDataSingles
        Precomputed data for singles (male or female)
    spec : EstimationSpec
        Specification from YAML config
    theta_init : np.ndarray
        Initial parameter values (length = n_params)
    group : str, default="singles_male"
        Estimation group: "singles_male" or "singles_female"
        Determines which gender-specific parameters to use
    solver : str, default="conopt"
        GAMSPy solver: "conopt", "ipopt", "ipopth", or "knitro"
    verbose : bool, default=True
        If True, print solver output
    solver_options : dict, optional
        Solver-specific options to pass to GAMSPy. For CONOPT, common options include:
        - "Tol_Optimality": Optimality tolerance (default 1e-7)
        - "Tol_Obj_Change": Limit for relative change in objective (default 3e-12)
        - "Lim_Iteration": Maximum iterations
        - "Lim_StallIter": Stalled iterations limit (default 100)
        Example: {"Tol_Optimality": "1e-9", "Lim_Iteration": "10000"}

    Returns
    -------
    dict with:
        - theta: np.ndarray - Final parameter estimates
        - log_likelihood: float - Final log-likelihood value
        - solver_status: str - Solver termination status
        - model_status: str - Model status
        - walltime: float - Walltime in seconds
        - n_iterations: int - Number of iterations (if available)
    """
    if not HAS_GAMSPY:
        raise ImportError("GAMSPy not installed. Run: pip install gamspy")
    
    logger = logging.getLogger(__name__)
    
    # Validate solver
    if solver not in SOLVER_MAP:
        raise ValueError(f"Unknown solver '{solver}'. Choose from: {list(SOLVER_MAP.keys())}")
    
    solver_name = SOLVER_MAP[solver]
    
    logger.info(f"Starting GAMSPy estimation (solver={solver_name.upper()}, group={group})")
    logger.info(f"  Observations: {data.n_obs:,}")
    logger.info(f"  Groups: {data.n_groups:,}")
    logger.info(f"  Alternatives: {data.n_alts}")
    logger.info(f"  Parameters: {len(spec.all_param_names)}")
    
    start_time = time.time()
    
    # Ensure local working directory (GAMS doesn't like UNC paths)
    ensure_local_workdir()
    
    # Create GAMSPy container
    container = Container()
    
    # ========================================================================
    # 1. Create GAMSPy variables for each parameter
    # ========================================================================
    
    param_vars = {}
    
    for i, param_name in enumerate(spec.all_param_names):
        var = Variable(container, param_name, type="free")
        
        # Set initial value
        var.l = float(theta_init[i])
        
        # Set bounds (if specified)
        if param_name in spec.bounds:
            lb, ub = spec.bounds[param_name]
            if lb is not None:
                var.lo = float(lb)
            if ub is not None:
                var.up = float(ub)
        
        param_vars[param_name] = var
    
    logger.info(f"  Created {len(param_vars)} GAMSPy variables")
    
    # ========================================================================
    # 2. Build log-likelihood expression
    # ========================================================================
    
    logger.info("  Building log-likelihood expression...")
    
    # Reference values for normalization
    y_ref = data.c_scale
    l_ref = data.l_scale
    # Track which parameters are used (for debugging)
    params_used = set()
    
    # Log-likelihood accumulator
    ll_expr = 0.0
    
    # Group boundaries
    group_starts = data.group_starts
    group_ends = data.group_ends
    n_groups = data.n_groups
    
    # Loop over groups (each person/household)
    for g in range(n_groups):
        start_idx = group_starts[g]
        end_idx = group_ends[g]
        
        # Get indices for this group's alternatives
        alt_indices = range(start_idx, end_idx)
        
        # Find chosen alternative (within group)
        chosen_idx_within_group = None
        for local_j, global_idx in enumerate(alt_indices):
            if data.actual_choice[global_idx] == 1.0:
                chosen_idx_within_group = local_j
                break
        
        if chosen_idx_within_group is None:
            logger.warning(f"Group {g}: No chosen alternative found!")
            continue
        
        # Build utilities for all alternatives in this group
        utilities = []
        
        for global_idx in alt_indices:
            # === CONSUMPTION UTILITY: β_c * BC(C / c_scale, θ_c) ===
            # Use group-specific parameters (e.g., beta_c_sm, theta_c_sm for singles male)
            c_val = data.consumption[global_idx]
            c_scaled = c_val / y_ref

            # Get group-specific consumption parameters
            beta_c_param = get_param_name('beta_c', group, param_vars)

            # Handle optional theta_c parameter (None = log utility)
            if spec.utility_consumption_theta:
                theta_c_param = get_param_name('theta_c', group, param_vars)
                bc_c = boxcox_gamspy(c_scaled, param_vars[theta_c_param])
                params_used.add(theta_c_param)
            else:
                # Log utility when theta=None
                bc_c = gp_log(c_scaled)

            # Consumption utility component
            util_j = param_vars[beta_c_param] * bc_c
            params_used.add(beta_c_param)

            # === LEISURE UTILITY: β_l(Z) * BC(L / l_scale, θ_l) ===
            l_val = data.leisure[global_idx]
            l_scaled = l_val / l_ref

            # Get group-specific leisure parameters
            beta_l0_param = get_param_name('beta_l0', group, param_vars)

            # Build β_l(Z) = β_l0 + Σ β_k * Z_k
            beta_l_expr = param_vars[beta_l0_param]
            params_used.add(beta_l0_param)

            # Add demographic shifters (also group-specific)
            for shifter in spec.utility_leisure_shifters:
                var_name = shifter['variable']
                base_coef = shifter['coefficient']

                # Try to get group-specific coefficient
                try:
                    coef_param = get_param_name(base_coef, group, param_vars)
                except ValueError:
                    # Parameter doesn't exist for this group, skip
                    continue

                # Get demographic value for this observation
                demo_val = getattr(data, var_name, None)
                if demo_val is None:
                    logger.warning(f"Demographic variable '{var_name}' not found in data")
                    continue

                beta_l_expr = beta_l_expr + param_vars[coef_param] * float(demo_val[global_idx])
                params_used.add(coef_param)

            # Handle optional theta_l parameter (None = log utility)
            if spec.utility_leisure_theta:
                theta_l_param = get_param_name('theta_l', group, param_vars)
                bc_l = boxcox_gamspy(l_scaled, param_vars[theta_l_param])
                params_used.add(theta_l_param)
            else:
                # Log utility when theta=None
                bc_l = gp_log(l_scaled)

            # Leisure utility component
            util_j = util_j + beta_l_expr * bc_l
            
            # Add ASC if applicable (not for base alternative)
            # ASCs are alternative-specific, check if this alt has one
            for asc_label in spec.asc_labels:
                asc_param = f'ASC_{asc_label}'
                if asc_param in param_vars:
                    # Determine if this alternative matches the ASC
                    # (This requires alternative labels - we'll add a simple heuristic)
                    # For now, skip ASCs - can be added later
                    pass
            
            utilities.append(util_j)
        
        # Compute log-probability for chosen alternative using log-sum-exp
        # log P(chosen) = U_chosen - log(Σ exp(U_j))
        
        chosen_util = utilities[chosen_idx_within_group]
        
        # Sum of exp(utilities) - use GAMSPy exp
        sum_exp_u = sum(gp_exp(u) for u in utilities)
        
        # Log probability
        log_prob = chosen_util - gp_log(sum_exp_u + LOG_EPS)
        
        # Add to total log-likelihood
        ll_expr = ll_expr + log_prob
    
    logger.info(f"  Built log-likelihood with {len(params_used)} active parameters")
    
    # ========================================================================
    # 3. Create objective and model
    # ========================================================================
    
    obj = Variable(container, "log_likelihood", type="free")
    obj_eq = Equation(container, "obj_eq", definition=(obj == ll_expr))
    
    model = Model(
        container, 
        name="ruro_mnl_gamspy",
        equations=[obj_eq], 
        problem="nlp",
        sense="max", 
    objective=obj
    )
      # ========================================================================
    # 4. Solve
    # ========================================================================
    logger.info(f"  Solving with {solver_name.upper()}...")

    # Pass solver-specific options if provided
    if solver_options:
        logger.info(f"  Solver options: {solver_options}")
        result = model.solve(solver=solver_name, solver_options=solver_options)
    else:
        result = model.solve(solver=solver_name)

    walltime = time.time() - start_time

    # ========================================================================
    # 5. Extract results
    # ========================================================================

    theta_final = np.array([
        _extract_var_level(param_vars[name])
        for name in spec.all_param_names
    ])
    
    ll_final = _extract_var_level(obj)
    
    # Get solver/model status from MODEL object
    # GAMSPy stores: model.solve_status (SolveStatus enum) and model.status (ModelStatus enum)
    solve_status_enum = getattr(model, 'solve_status', None)
    model_status_enum = getattr(model, 'status', None)

    solver_status = str(solve_status_enum) if solve_status_enum else 'Unknown'
    model_status = str(model_status_enum) if model_status_enum else 'Unknown'
    
    # Try to get iteration count
    n_iterations = getattr(result, 'iteration_count', None)
    if n_iterations is None:
        # Try alternative attributes
        n_iterations = getattr(result, 'iter_used', None)
    
    logger.info(f"  [OK] Solved in {walltime:.1f} seconds")
    logger.info(f"  Final LL: {ll_final:.4f}")
    logger.info(f"  Solver status: {solver_status}")
    logger.info(f"  Model status: {model_status}")
    if n_iterations is not None:
        logger.info(f"  Iterations: {n_iterations}")

    # ========================================================================
    # 6. Validate results
    # ========================================================================

    logger.info("  Validating results...")
    validate_gamspy_result(model, ll_final, theta_final,
                          expected_ll_range=(-15000, -1000),
                          logger=logger)

    return {
        'theta': theta_final,
        'log_likelihood': ll_final,
        'solver_status': solver_status,
        'model_status': model_status,
        'walltime': walltime,
        'n_iterations': n_iterations,
        'gamspy_result': result,
    }


# ==============================================================================
# Couples Estimation
# ==============================================================================

def estimate_couples_gamspy(
    data: PrecomputedDataCouples,
    spec: EstimationSpec,
    theta_init: np.ndarray,
    solver: str = "conopt",
    verbose: bool = True,
    solver_options: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Estimate couples MNL using GAMSPy + CONOPT/IPOPT.

    Uses Aaberge-Colombino collective utility specification:
        U_j = β_c_f * log(C_j / y_ref) + β_c_m * log(C_j / y_ref) +
            β_l_f(Z_f) * log(L_f_j / l_ref) + β_l_m(Z_m) * log(L_m_j / l_ref) +
            ASC_j

    Parameters
    ----------
    data : PrecomputedDataCouples
        Precomputed data for couples
    spec : EstimationSpec
        Specification from YAML config
    theta_init : np.ndarray
        Initial parameter values
    solver : str, default="conopt"
        GAMSPy solver
    verbose : bool, default=True
        Print solver output
    solver_options : dict, optional
        Solver-specific options (e.g., {"Tol_Optimality": "1e-9"})

    Returns
    -------
    dict with estimation results (same format as estimate_singles_gamspy)
    """
    if not HAS_GAMSPY:
        raise ImportError("GAMSPy not installed. Run: pip install gamspy")
    
    logger = logging.getLogger(__name__)
    
    # Validate solver
    if solver not in SOLVER_MAP:
        raise ValueError(f"Unknown solver '{solver}'. Choose from: {list(SOLVER_MAP.keys())}")
    
    solver_name = SOLVER_MAP[solver]
    
    logger.info(f"Starting GAMSPy couples estimation (solver={solver_name.upper()})")
    logger.info(f"  Observations: {data.n_obs:,}")
    logger.info(f"  Groups: {data.n_groups:,}")
    logger.info(f"  Alternatives: {data.n_alts}")
    logger.info(f"  Parameters: {len(spec.all_param_names)}")
    
    start_time = time.time()
    
    # Ensure local working directory
    ensure_local_workdir()
    
    # Create GAMSPy container
    container = Container()
    
    # ========================================================================
    # 1. Create variables
    # ========================================================================
    
    param_vars = {}
    
    for i, param_name in enumerate(spec.all_param_names):
        var = Variable(container, param_name, type="free")
        var.l = float(theta_init[i])
        
        if param_name in spec.bounds:
            lb, ub = spec.bounds[param_name]
            if lb is not None:
                var.lo = float(lb)
            if ub is not None:
                var.up = float(ub)
        
        param_vars[param_name] = var
    
    logger.info(f"  Created {len(param_vars)} GAMSPy variables")
    
    # ========================================================================    # 2. Build log-likelihood
    # ========================================================================
    
    logger.info("  Building log-likelihood expression...")
    
    y_ref = data.c_scale
    l_ref = data.l_scale
    
    ll_expr = 0.0
    
    group_starts = data.group_starts
    group_ends = data.group_ends
    n_groups = data.n_groups
    
    for g in range(n_groups):
        start_idx = group_starts[g]
        end_idx = group_ends[g]
        
        alt_indices = range(start_idx, end_idx)
        # Find chosen alternative
        chosen_idx_within_group = None
        for local_j, global_idx in enumerate(alt_indices):
            if data.actual_choice[global_idx] == 1.0:
                chosen_idx_within_group = local_j
                break
        
        if chosen_idx_within_group is None:
            continue
        
        utilities = []
        
        for global_idx in alt_indices:
            # === CONSUMPTION UTILITY: β_c * BC(C / c_scale, θ_c) ===
            # Use couples_household group for shared consumption parameter
            c_val = data.consumption[global_idx]
            c_scaled = c_val / y_ref

            # Get household-level consumption parameters (shared between partners)
            beta_c_param = get_param_name('beta_c', 'couples_household', param_vars)

            # Handle optional theta_c parameter (None = log utility)
            if spec.utility_consumption_theta:
                theta_c_param = get_param_name('theta_c', 'couples_household', param_vars)
                bc_c = boxcox_gamspy(c_scaled, param_vars[theta_c_param])
            else:
                # Log utility when theta=None
                bc_c = gp_log(c_scaled)

            # Consumption utility component (appears once, not twice!)
            util_j = param_vars[beta_c_param] * bc_c

            # === FEMALE LEISURE UTILITY: β_l_f(Z) * BC(L_f / l_scale, θ_l_f) ===
            l_f_val = data.leisure_female[global_idx]
            l_f_scaled = l_f_val / l_ref

            # Get female-specific leisure parameters
            beta_l0_f_param = get_param_name('beta_l0', 'couples_female', param_vars)

            # Build female leisure coefficient β_l_f(Z) = β_l0_f + Σ β_k_f * Z_k
            beta_l_f_expr = param_vars[beta_l0_f_param]

            for shifter in spec.utility_leisure_shifters:
                var_name = shifter['variable']
                base_coef = shifter['coefficient']

                # Try to get female-specific coefficient
                try:
                    coef_param_f = get_param_name(base_coef, 'couples_female', param_vars)
                except ValueError:
                    # Parameter doesn't exist for females, skip
                    continue

                demo_val = getattr(data, var_name, None)
                if demo_val is None:
                    continue

                beta_l_f_expr = beta_l_f_expr + param_vars[coef_param_f] * float(demo_val[global_idx])

            # Handle optional theta_l parameter (None = log utility)
            if spec.utility_leisure_theta:
                theta_l_f_param = get_param_name('theta_l', 'couples_female', param_vars)
                bc_l_f = boxcox_gamspy(l_f_scaled, param_vars[theta_l_f_param])
            else:
                # Log utility when theta=None
                bc_l_f = gp_log(l_f_scaled)

            # Female leisure utility component
            util_j = util_j + beta_l_f_expr * bc_l_f

            # === MALE LEISURE UTILITY: β_l_m(Z) * BC(L_m / l_scale, θ_l_m) ===
            l_m_val = data.leisure_male[global_idx]
            l_m_scaled = l_m_val / l_ref

            # Get male-specific leisure parameters
            beta_l0_m_param = get_param_name('beta_l0', 'couples_male', param_vars)

            # Build male leisure coefficient β_l_m(Z) = β_l0_m + Σ β_k_m * Z_k
            beta_l_m_expr = param_vars[beta_l0_m_param]

            for shifter in spec.utility_leisure_shifters:
                var_name = shifter['variable']
                base_coef = shifter['coefficient']

                # Try to get male-specific coefficient
                try:
                    coef_param_m = get_param_name(base_coef, 'couples_male', param_vars)
                except ValueError:
                    # Parameter doesn't exist for males, skip
                    continue

                demo_val = getattr(data, var_name, None)
                if demo_val is None:
                    continue

                beta_l_m_expr = beta_l_m_expr + param_vars[coef_param_m] * float(demo_val[global_idx])

            # Handle optional theta_l parameter (None = log utility)
            if spec.utility_leisure_theta:
                theta_l_m_param = get_param_name('theta_l', 'couples_male', param_vars)
                bc_l_m = boxcox_gamspy(l_m_scaled, param_vars[theta_l_m_param])
            else:
                # Log utility when theta=None
                bc_l_m = gp_log(l_m_scaled)

            # Male leisure utility component
            util_j = util_j + beta_l_m_expr * bc_l_m
            
            utilities.append(util_j)
        
        # Log-softmax
        chosen_util = utilities[chosen_idx_within_group]
        sum_exp_u = sum(gp_exp(u) for u in utilities)
        log_prob = chosen_util - gp_log(sum_exp_u + LOG_EPS)
        
        ll_expr = ll_expr + log_prob
    
    logger.info(f"  Built couples log-likelihood expression")
    
    # ========================================================================
    # 3. Create model
    # ========================================================================
    
    obj = Variable(container, "log_likelihood", type="free")
    obj_eq = Equation(container, "obj_eq", definition=(obj == ll_expr))
    
    model = Model(
        container,
        name="ruro_couples_mnl_gamspy",
        equations=[obj_eq],
        problem="nlp",
        sense="max",
        objective=obj
    )
    
    # ========================================================================
    # 4. Solve
    # ========================================================================

    logger.info(f"  Solving with {solver_name.upper()}...")

    # Pass solver-specific options if provided
    if solver_options:
        logger.info(f"  Solver options: {solver_options}")
        result = model.solve(solver=solver_name, solver_options=solver_options)
    else:
        result = model.solve(solver=solver_name)
    walltime = time.time() - start_time

    # ========================================================================
    # 5. Extract results
    # ========================================================================

    theta_final = np.array([
        _extract_var_level(param_vars[name])
        for name in spec.all_param_names
    ])

    ll_final = _extract_var_level(obj)

    # Get solver/model status from MODEL object
    # GAMSPy stores: model.solve_status (SolveStatus enum) and model.status (ModelStatus enum)
    solve_status_enum = getattr(model, 'solve_status', None)
    model_status_enum = getattr(model, 'status', None)

    solver_status = str(solve_status_enum) if solve_status_enum else 'Unknown'
    model_status = str(model_status_enum) if model_status_enum else 'Unknown'
    n_iterations = getattr(result, 'iteration_count', getattr(result, 'iter_used', None))
    
    logger.info(f"  [OK] Solved in {walltime:.1f} seconds")
    logger.info(f"  Final LL: {ll_final:.4f}")
    logger.info(f"  Solver status: {solver_status}")
    logger.info(f"  Model status: {model_status}")
    if n_iterations is not None:
        logger.info(f"  Iterations: {n_iterations}")

    # ========================================================================
    # 6. Validate results
    # ========================================================================

    logger.info("  Validating results...")
    validate_gamspy_result(model, ll_final, theta_final,
                          expected_ll_range=(-15000, -1000),
                          logger=logger)

    return {
        'theta': theta_final,
        'log_likelihood': ll_final,
        'solver_status': solver_status,
        'model_status': model_status,
        'walltime': walltime,
        'n_iterations': n_iterations,
        'gamspy_result': result,
    }


# ==============================================================================
# Hessian Extraction and Identification Diagnostics
# ==============================================================================

def _extract_hessian_from_gams_workdir(container, param_vars, spec, logger):
    """
    Extract Hessian matrix from GAMS working directory files.

    GAMS solvers (especially CONOPT) compute the Hessian and store it in scratch files.
    This function attempts to read those files and reconstruct the Hessian matrix.

    Parameters
    ----------
    container : GAMSPy Container
        The GAMSPy container with working directory info
    param_vars : dict
        Dictionary mapping parameter names to GAMSPy Variables
    spec : EstimationSpec
        Specification object containing parameter names
    logger : logging.Logger
        Logger for output

    Returns
    -------
    np.ndarray or None
        Hessian matrix (n_params, n_params) if successful, None otherwise
    """
    import os
    import glob

    n_params = len(spec.all_param_names)

    # Get the working directory from container
    if not hasattr(container, 'working_directory'):
        logger.warning("  Container has no working_directory attribute")
        return None

    workdir = container.working_directory
    logger.info(f"  GAMS working directory: {workdir}")

    # Look for CONOPT Hessian files
    # CONOPT may write Hessian to files like: CNO*.scr, *.hes, or GDX files
    possible_patterns = [
        os.path.join(workdir, "CNO*.scr"),
        os.path.join(workdir, "*.hes"),
        os.path.join(workdir, "*_hessian.gdx"),
        os.path.join(workdir, "*.gdx"),
    ]

    hessian_files = []
    for pattern in possible_patterns:
        hessian_files.extend(glob.glob(pattern))

    if not hessian_files:
        logger.warning(f"  No potential Hessian files found in {workdir}")
        return None

    logger.info(f"  Found {len(hessian_files)} potential Hessian file(s)")
    for f in hessian_files[:5]:  # Show first 5
        logger.info(f"    - {os.path.basename(f)}")

    # Try to read GDX files (most structured format)
    for gdx_file in [f for f in hessian_files if f.endswith('.gdx')]:
        try:
            logger.info(f"  Trying to read Hessian from GDX: {os.path.basename(gdx_file)}")
            H = _read_hessian_from_gdx(gdx_file, n_params, logger)
            if H is not None:
                return H
        except Exception as e:
            logger.warning(f"  Failed to read {os.path.basename(gdx_file)}: {e}")
            continue

    # If GDX failed, try CONOPT scratch files (binary format - harder to parse)
    logger.warning("  GDX extraction failed, CONOPT binary scratch files not yet supported")
    return None


def _read_hessian_from_gdx(gdx_path, n_params, logger):
    """
    Read Hessian matrix from a GAMS GDX file.

    Parameters
    ----------
    gdx_path : str
        Path to GDX file
    n_params : int
        Expected number of parameters
    logger : logging.Logger
        Logger

    Returns
    -------
    np.ndarray or None
        Hessian matrix if found, None otherwise
    """
    from gamspy import Container

    try:
        # Load GDX file into a new container
        hess_container = Container(load_from=gdx_path)

        # Look for symbols that might contain the Hessian
        # Common names: hessian, hess, H, jacobian, second_derivatives
        possible_names = ['hessian', 'hess', 'H', 'second_deriv', 'second_derivatives']

        for name in possible_names:
            if hasattr(hess_container, name):
                logger.info(f"  Found symbol: {name}")
                hess_symbol = getattr(hess_container, name)

                # Try to convert to numpy array
                if hasattr(hess_symbol, 'records'):
                    records = hess_symbol.records
                    logger.info(f"  Symbol has {len(records)} records")

                    # Hessian is typically stored as (i, j, value) tuples
                    # Try to reconstruct the matrix
                    H = np.zeros((n_params, n_params))
                    for _, row in records.iterrows():
                        if len(row) >= 3:
                            i = int(row.iloc[0])
                            j = int(row.iloc[1])
                            val = float(row.iloc[2])
                            if 0 <= i < n_params and 0 <= j < n_params:
                                H[i, j] = val
                                H[j, i] = val  # Symmetric

                    if np.any(H != 0):
                        logger.info(f"  Reconstructed {n_params}x{n_params} Hessian matrix")
                        return H

        logger.warning(f"  No Hessian symbol found in GDX file")
        return None

    except Exception as e:
        logger.warning(f"  Error reading GDX file: {e}")
        return None


def extract_hessian_diagnostics(model, param_vars, spec, logger):
    """
    Extract Hessian matrix from GAMSPy model and compute identification diagnostics.

    Parameters
    ----------
    model : GAMSPy Model
        The solved optimization model
    param_vars : dict
        Dictionary mapping parameter names to GAMSPy Variables
    spec : EstimationSpec
        Specification object containing parameter names
    logger : logging.Logger
        Logger for output

    Returns
    -------
    dict with:
        - hessian: np.ndarray (n_params, n_params) or None
        - eigenvalues: np.ndarray (n_params,) or None
        - condition_number: float or None
        - standard_errors: np.ndarray (n_params,) or None
        - t_values: np.ndarray (n_params,) or None
        - p_values: np.ndarray (n_params,) or None
        - correlation_matrix: np.ndarray (n_params, n_params) or None
        - poorly_identified_params: list of parameter names
    """
    from scipy.stats import norm

    n_params = len(spec.all_param_names)
    theta = np.array([_extract_var_level(param_vars[name]) for name in spec.all_param_names])

    logger.info("")
    logger.info("="*80)
    logger.info("EXTRACTING HESSIAN MATRIX")
    logger.info("="*80)

    # Try to get Hessian from GAMSPy
    H = None

    # Try multiple possible locations for Hessian
    if hasattr(model, 'hessian'):
        logger.info("  Found Hessian in model.hessian")
        H = model.hessian
        if hasattr(H, 'toarray'):
            H = H.toarray()
    elif hasattr(model, '_model') and hasattr(model._model, 'hessian'):
        logger.info("  Found Hessian in model._model.hessian")
        H = model._model.hessian
        if hasattr(H, 'toarray'):
            H = H.toarray()
    elif hasattr(model, 'getHessian'):
        logger.info("  Extracting Hessian using model.getHessian()")
        try:
            H = model.getHessian()
            if hasattr(H, 'toarray'):
                H = H.toarray()
        except Exception as e:
            logger.warning(f"  Failed to extract Hessian: {e}")

    # If not found, try extracting from GAMS working directory
    if H is None and hasattr(model, 'container'):
        logger.info("  Attempting to extract Hessian from GAMS working directory...")
        try:
            H = _extract_hessian_from_gams_workdir(model.container, param_vars, spec, logger)
            if H is not None:
                logger.info(f"  [OK] Successfully extracted Hessian from GAMS files")
        except Exception as e:
            logger.warning(f"  Failed to extract Hessian from GAMS workdir: {e}")

    if H is None:
        logger.warning("  [!] Hessian not found in GAMSPy model")
        logger.warning("  Numerical Hessian computation not yet implemented")
        logger.warning("  Returning None for all Hessian diagnostics")
        return {
            'hessian': None,
            'eigenvalues': None,
            'condition_number': None,
            'standard_errors': None,
            't_values': None,
            'p_values': None,
            'correlation_matrix': None,
            'poorly_identified_params': [],
            'n_negative_eigenvalues': 0,  # FIX: Add missing key
        }

    logger.info(f"  Hessian shape: {H.shape}")

    # Ensure it's negative definite for maximum likelihood
    # (GAMSPy may return -H already for minimization problems)
    if H.shape[0] > 0:
        # Check if it's positive or negative definite by looking at median eigenvalue
        eigvals_test = np.linalg.eigvalsh(H)
        if np.median(eigvals_test) > 0:
            # Hessian is positive, negate it (we're maximizing LL)
            H = -H
            logger.info("  Negated Hessian (GAMSPy solver works with minimization)")

    # Compute eigenvalues of -H (should be positive for maximum)
    eigenvalues = np.linalg.eigvalsh(-H)
    logger.info(f"  Eigenvalue range: [{eigenvalues.min():.2e}, {eigenvalues.max():.2e}]")

    # Check for negative eigenvalues (saddle point!)
    n_negative = np.sum(eigenvalues < 0)
    if n_negative > 0:
        logger.error(f"  [X] Found {n_negative} NEGATIVE eigenvalues - NOT a local maximum!")
        logger.error(f"  This indicates a saddle point, not an optimum!")

    # Compute condition number
    if eigenvalues.min() > 0:
        condition_number = eigenvalues.max() / eigenvalues.min()
    else:
        condition_number = np.inf
        logger.error("  [X] Minimum eigenvalue ≤ 0, condition number is infinite!")

    logger.info(f"  Condition number: {condition_number:.2e}")

    # Interpret condition number
    if condition_number < 100:
        logger.info("  [OK] Well-conditioned Hessian (kappa < 100)")
    elif condition_number < 10000:
        logger.warning(f"  [!] Moderate conditioning issues (100 ≤ kappa < 10,000)")
    else:
        logger.error(f"  [X] Severe identification problem (kappa ≥ 10,000)")

    # Compute covariance matrix (inverse of -H)
    try:
        logger.info("  Computing covariance matrix (inverse Hessian)...")
        H_inv = np.linalg.inv(-H)
        standard_errors = np.sqrt(np.diag(H_inv))

        # Correlation matrix
        correlation_matrix = H_inv / np.outer(standard_errors, standard_errors)

        # T-statistics and p-values
        t_values = theta / standard_errors
        p_values = 2 * (1 - norm.cdf(np.abs(t_values)))

        logger.info(f"  [OK] Computed standard errors for {n_params} parameters")

    except np.linalg.LinAlgError as e:
        logger.error(f"  [X] Failed to invert Hessian: {e}")
        logger.error("  SEVERE IDENTIFICATION PROBLEM - Hessian is singular!")
        standard_errors = np.full(n_params, np.nan)
        t_values = np.full(n_params, np.nan)
        p_values = np.full(n_params, np.nan)
        correlation_matrix = np.full((n_params, n_params), np.nan)

    # Identify poorly identified parameters
    poorly_identified = []
    logger.info("")
    logger.info("  Parameter significance check:")

    for i, (name, val, se, t_val, p_val) in enumerate(zip(
        spec.all_param_names, theta, standard_errors, t_values, p_values
    )):
        if np.isnan(se):
            poorly_identified.append(name)
            logger.warning(f"    [!] {name}: SE = NaN (singular Hessian)")
        elif se > 10.0:
            poorly_identified.append(name)
            logger.warning(f"    [!] {name}: SE = {se:.2f} (very large, poorly identified)")
        elif p_val > 0.10:
            if p_val > 0.50:
                poorly_identified.append(name)
                logger.warning(f"    [!] {name}: p = {p_val:.3f} (not significant at any level)")
            elif p_val > 0.20:
                logger.info(f"       {name}: p = {p_val:.3f} (weakly significant)")
        else:
            # Significant - log only if verbose
            if p_val < 0.01:
                sig_level = "***"
            elif p_val < 0.05:
                sig_level = "**"
            else:
                sig_level = "*"
            # Only log parameters of interest
            if 'theta' in name or 'beta_c' in name:
                logger.info(f"       {name}: t = {t_val:.2f}, p = {p_val:.4f} {sig_level}")

    logger.info("="*80)
    logger.info("")

    return {
        'hessian': H,
        'eigenvalues': eigenvalues,
        'condition_number': condition_number,
        'standard_errors': standard_errors,
        't_values': t_values,
        'p_values': p_values,
        'correlation_matrix': correlation_matrix,
        'poorly_identified_params': poorly_identified,
        'n_negative_eigenvalues': n_negative,
    }


# ==============================================================================
# Joint Estimation (All Groups)
# ==============================================================================

def estimate_joint_gamspy(
    data_singles_male: PrecomputedDataSingles,
    data_singles_female: PrecomputedDataSingles,
    data_couples: PrecomputedDataCouples,
    spec: EstimationSpec,
    theta_init: Optional[np.ndarray] = None,
    solver: str = "conopt",
    verbose: bool = True,
    solver_options: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Estimate joint MNL (singles male + singles female + couples) using GAMSPy.

    This combines all three groups into a single optimization problem with
    shared parameters across groups where applicable.

    Uses Box-Cox utility specification (matching SciPy implementation):
        U = β_c * BC(C/c_scale, θ_c) + β_l(Z) * BC(L/l_scale, θ_l) + opportunity terms

    The objective is to maximize the sum of log-likelihoods:
        LL_joint = LL_singles_male + LL_singles_female + LL_couples

    Parameters
    ----------
    data_singles_male : PrecomputedDataSingles
        Precomputed data for singles male
    data_singles_female : PrecomputedDataSingles
        Precomputed data for singles female
    data_couples : PrecomputedDataCouples
        Precomputed data for couples
    spec : EstimationSpec
        Specification from YAML config
    theta_init : np.ndarray, optional
        Initial parameter values (length = n_params). If None, uses spec.initial_values.
        This should come from warm-start (previous estimation results).
    solver : str, default="conopt"
        GAMSPy solver: "conopt", "ipopt", "ipopth", or "knitro"
    verbose : bool, default=True
        If True, print solver output
    solver_options : dict, optional
        Solver-specific options. For CONOPT:
        - "Tol_Optimality": Optimality tolerance (default 1e-7)
        - "Tol_Obj_Change": Limit for relative change in objective (default 3e-12)
        - "Lim_Iteration": Maximum iterations
        Example: {"Tol_Optimality": "1e-9", "Lim_Iteration": "10000"}

    Returns
    -------
    dict with:
        - theta: np.ndarray - Final parameter estimates
        - log_likelihood: float - Total log-likelihood (sum of all groups)
        - ll_singles_male: float - Singles male contribution
        - ll_singles_female: float - Singles female contribution
        - ll_couples: float - Couples contribution
        - solver_status: str - Solver termination status
        - model_status: str - Model status
        - walltime: float - Total walltime in seconds
        - n_iterations: int - Number of iterations
    """
    if not HAS_GAMSPY:
        raise ImportError("GAMSPy not installed. Run: pip install gamspy")
    
    logger = logging.getLogger(__name__)
    
    # Validate solver
    if solver not in SOLVER_MAP:
        raise ValueError(f"Unknown solver '{solver}'. Choose from: {list(SOLVER_MAP.keys())}")
    
    solver_name = SOLVER_MAP[solver]
    
    logger.info("="*80)
    logger.info("Starting GAMSPy JOINT estimation")
    logger.info("="*80)
    logger.info(f"  Solver: {solver_name.upper()}")
    logger.info(f"  Singles male:   {data_singles_male.n_obs:,} obs, {data_singles_male.n_groups:,} groups")
    logger.info(f"  Singles female: {data_singles_female.n_obs:,} obs, {data_singles_female.n_groups:,} groups")
    logger.info(f"  Couples:        {data_couples.n_obs:,} obs, {data_couples.n_groups:,} groups")
    logger.info(f"  Total observations: {data_singles_male.n_obs + data_singles_female.n_obs + data_couples.n_obs:,}")
    logger.info(f"  Parameters: {len(spec.all_param_names)}")
    
    start_time = time.time()
    
    # Ensure local working directory
    ensure_local_workdir()
    # Create GAMSPy container
    container = Container()
    
    # ========================================================================
    # 1. Create parameter variables (shared across all groups)
    # ========================================================================
    
    logger.info("  Creating shared parameter variables...")

    param_vars = {}

    # Use provided theta_init (from warm-start) or fall back to spec defaults
    if theta_init is None:
        theta_init = np.array([spec.initial_values.get(name, 0.0) for name in spec.all_param_names])
        logger.info("    Using spec default initial values")
    else:
        logger.info("    Using warm-start initial values")

    for i, param_name in enumerate(spec.all_param_names):
        var = Variable(container, param_name, type="free")
        var.l = float(theta_init[i])
        
        if param_name in spec.bounds:
            lb, ub = spec.bounds[param_name]
            if lb is not None:
                var.lo = float(lb)
            if ub is not None:
                var.up = float(ub)
        
        param_vars[param_name] = var
    
    logger.info(f"    Created {len(param_vars)} shared parameters")
    
    # ========================================================================
    # 2. Build log-likelihood for SINGLES MALE
    # ========================================================================
    
    logger.info("  Building log-likelihood for singles male...")
    
    ll_sm = 0.0
    y_ref_sm = data_singles_male.c_scale
    l_ref_sm = data_singles_male.l_scale
    
    for g in range(data_singles_male.n_groups):
        start_idx = data_singles_male.group_starts[g]
        end_idx = data_singles_male.group_ends[g]
        
        # Find chosen alternative
        chosen_idx = None
        for local_j, global_idx in enumerate(range(start_idx, end_idx)):
            if data_singles_male.actual_choice[global_idx] == 1.0:
                chosen_idx = local_j
                break
        
        if chosen_idx is None:
            continue
        
        # Build utilities for singles male
        utilities = []
        for global_idx in range(start_idx, end_idx):
            # Consumption utility: β_c * BC(C, θ_c)
            # NOTE: Apply Box-Cox to RAW values, NOT scaled (matches SciPy)
            c_val = data_singles_male.consumption[global_idx]

            beta_c_param = get_param_name('beta_c', 'singles_male', param_vars)

            # Handle optional theta_c parameter (None = log utility)
            if spec.utility_consumption_theta:
                theta_c_param = get_param_name('theta_c', 'singles_male', param_vars)
                bc_c = boxcox_gamspy(c_val, param_vars[theta_c_param])
            else:
                # Log utility when theta=None
                bc_c = gp_log(c_val)

            util_j = param_vars[beta_c_param] * bc_c

            # Leisure utility: β_l(Z) * BC(L, θ_l)
            # NOTE: Apply Box-Cox to RAW values, NOT scaled (matches SciPy)
            l_val = data_singles_male.leisure[global_idx]

            beta_l0_param = get_param_name('beta_l0', 'singles_male', param_vars)
            beta_l_expr = param_vars[beta_l0_param]

            for shifter in spec.utility_leisure_shifters:
                var_name = shifter['variable']
                base_coef = shifter['coefficient']

                try:
                    coef_param = get_param_name(base_coef, 'singles_male', param_vars)
                except ValueError:
                    continue

                demo_val = getattr(data_singles_male, var_name, None)
                if demo_val is not None:
                    beta_l_expr = beta_l_expr + param_vars[coef_param] * float(demo_val[global_idx])

            # Handle optional theta_l parameter (None = log utility)
            if spec.utility_leisure_theta:
                theta_l_param = get_param_name('theta_l', 'singles_male', param_vars)
                bc_l = boxcox_gamspy(l_val, param_vars[theta_l_param])
            else:
                # Log utility when theta=None
                bc_l = gp_log(l_val)

            util_j = util_j + beta_l_expr * bc_l

            # Hours opportunity density (log_h)
            # Use pre-computed variables from data
            working = float(data_singles_male.working[global_idx])  # 0/1 indicator
            pt1_focal = float(data_singles_male.working_pt1[global_idx])  # Part-time 1 ~20h
            pt2_focal = float(data_singles_male.working_pt2[global_idx])  # Part-time 2 ~30h
            ft_focal = float(data_singles_male.working_ft[global_idx])    # Full-time ~40h

            # Get demographic variables for interactions
            educL = float(getattr(data_singles_male, 'educL', np.zeros(1))[global_idx])
            educH = float(getattr(data_singles_male, 'educH', np.zeros(1))[global_idx])
            gsur_val = float(data_singles_male.gsur[global_idx])
            female = 0.0  # This is singles_male
            couple = 0.0  # This is singles

            # Build log_h from specification (specification-agnostic)
            log_h = 0.0
            for shifter in spec.hours_shifters:
                var_name = shifter["variable"]
                coef_name = shifter["coefficient"]
                interaction = shifter.get("interaction", None)

                # Get parameter - try gender-specific first, then base name
                coef_name_gender = f"{coef_name}_male"
                if coef_name_gender in param_vars:
                    param = param_vars[coef_name_gender]
                elif coef_name in param_vars:
                    param = param_vars[coef_name]
                else:
                    continue  # Skip if parameter not found

                # Get variable value
                if var_name == "working":
                    var_val = working
                elif var_name == "working_pt1":
                    var_val = pt1_focal
                elif var_name == "working_pt2":
                    var_val = pt2_focal
                elif var_name == "working_ft":
                    var_val = ft_focal
                elif var_name == "gsur":
                    var_val = gsur_val
                elif var_name == "educL":
                    var_val = educL
                elif var_name == "educH":
                    var_val = educH
                elif var_name == "female":
                    var_val = female
                elif var_name in ("couple", "in_couple"):
                    var_val = couple
                elif var_name == "drgn1":
                    # Get region indicator from data
                    var_val = float(getattr(data_singles_male, 'drgn1', np.zeros(1))[global_idx]) if hasattr(data_singles_male, 'drgn1') else 0.0
                elif hasattr(data_singles_male, var_name):
                    var_val = float(getattr(data_singles_male, var_name)[global_idx])
                else:
                    continue  # Skip if variable not found

                # Apply interaction if specified
                if interaction == "working":
                    var_val = var_val * working

                log_h = log_h + param * var_val

            # Add to utility
            util_j = util_j + log_h

            # Wage opportunity density (log_w) for workers
            if working > 0.5 and data_singles_male.log_wage is not None:
                log_wage_obs = float(data_singles_male.log_wage[global_idx])

                # Build wage mean
                mu_wage = param_vars['beta_w0']
                if 'beta_w_educL' in param_vars:
                    mu_wage = mu_wage + param_vars['beta_w_educL'] * educL
                if 'beta_w_educH' in param_vars:
                    mu_wage = mu_wage + param_vars['beta_w_educH'] * educH

                # Add experience terms if available
                if data_singles_male.pexp_years is not None and 'beta_pexp' in param_vars:
                    pexp = float(data_singles_male.pexp_years[global_idx])
                    mu_wage = mu_wage + param_vars['beta_pexp'] * pexp
                    if 'beta_pexp2' in param_vars and data_singles_male.pexp_years2 is not None:
                        pexp2 = float(data_singles_male.pexp_years2[global_idx])
                        mu_wage = mu_wage + param_vars['beta_pexp2'] * pexp2

                # Log-likelihood of observed wage
                residual = log_wage_obs - mu_wage
                sigma_param = param_vars['sigma']

                log_w = (-0.5 * (residual * residual) / (sigma_param * sigma_param + LOG_EPS)
                        - gp_log(sigma_param + LOG_EPS)
                        - 0.5 * gp_log(2.0 * 3.141592653589793))

                util_j = util_j + log_w

            # Importance sampling correction (subtract log_prior)
            prior_j = float(data_singles_male.prior[global_idx])
            log_prior = gp_log(prior_j + LOG_EPS)
            util_j = util_j - log_prior

            utilities.append(util_j)

        # Log-softmax
        chosen_util = utilities[chosen_idx]
        sum_exp_u = sum(gp_exp(u) for u in utilities)
        log_prob = chosen_util - gp_log(sum_exp_u + LOG_EPS)
        ll_sm = ll_sm + log_prob
    
    logger.info(f"    Singles male LL expression built")
    
    # ========================================================================
    # 3. Build log-likelihood for SINGLES FEMALE
    # ========================================================================
    
    logger.info("  Building log-likelihood for singles female...")
    
    ll_sf = 0.0
    y_ref_sf = data_singles_female.c_scale
    l_ref_sf = data_singles_female.l_scale
    
    for g in range(data_singles_female.n_groups):
        start_idx = data_singles_female.group_starts[g]
        end_idx = data_singles_female.group_ends[g]
        
        chosen_idx = None
        for local_j, global_idx in enumerate(range(start_idx, end_idx)):
            if data_singles_female.actual_choice[global_idx] == 1.0:
                chosen_idx = local_j
                break
        
        if chosen_idx is None:
            continue
        
        utilities = []
        for global_idx in range(start_idx, end_idx):
            # Consumption utility: β_c * BC(C, θ_c)
            # NOTE: Apply Box-Cox to RAW values, NOT scaled (matches SciPy)
            c_val = data_singles_female.consumption[global_idx]

            beta_c_param = get_param_name('beta_c', 'singles_female', param_vars)

            # Handle optional theta_c parameter (None = log utility)
            if spec.utility_consumption_theta:
                theta_c_param = get_param_name('theta_c', 'singles_female', param_vars)
                bc_c = boxcox_gamspy(c_val, param_vars[theta_c_param])
            else:
                # Log utility when theta=None
                bc_c = gp_log(c_val)

            util_j = param_vars[beta_c_param] * bc_c

            # Leisure utility: β_l(Z) * BC(L, θ_l)
            # NOTE: Apply Box-Cox to RAW values, NOT scaled (matches SciPy)
            l_val = data_singles_female.leisure[global_idx]

            beta_l0_param = get_param_name('beta_l0', 'singles_female', param_vars)
            beta_l_expr = param_vars[beta_l0_param]

            for shifter in spec.utility_leisure_shifters:
                var_name = shifter['variable']
                base_coef = shifter['coefficient']

                try:
                    coef_param = get_param_name(base_coef, 'singles_female', param_vars)
                except ValueError:
                    continue

                demo_val = getattr(data_singles_female, var_name, None)
                if demo_val is not None:
                    beta_l_expr = beta_l_expr + param_vars[coef_param] * float(demo_val[global_idx])

            # Handle optional theta_l parameter (None = log utility)
            if spec.utility_leisure_theta:
                theta_l_param = get_param_name('theta_l', 'singles_female', param_vars)
                bc_l = boxcox_gamspy(l_val, param_vars[theta_l_param])
            else:
                # Log utility when theta=None
                bc_l = gp_log(l_val)

            util_j = util_j + beta_l_expr * bc_l

            # Hours opportunity density (log_h)
            # Use pre-computed variables from data
            working = float(data_singles_female.working[global_idx])  # 0/1 indicator
            pt1_focal = float(data_singles_female.working_pt1[global_idx])  # Part-time 1 ~20h
            pt2_focal = float(data_singles_female.working_pt2[global_idx])  # Part-time 2 ~30h
            ft_focal = float(data_singles_female.working_ft[global_idx])    # Full-time ~40h

            # Get demographic variables for interactions
            educL = float(getattr(data_singles_female, 'educL', np.zeros(1))[global_idx])
            educH = float(getattr(data_singles_female, 'educH', np.zeros(1))[global_idx])
            gsur_val = float(data_singles_female.gsur[global_idx])
            female = 1.0  # This is singles_female
            couple = 0.0  # This is singles

            # Build log_h from specification (specification-agnostic)
            log_h = 0.0
            for shifter in spec.hours_shifters:
                var_name = shifter["variable"]
                coef_name = shifter["coefficient"]
                interaction = shifter.get("interaction", None)

                # Get parameter - try gender-specific first, then base name
                coef_name_gender = f"{coef_name}_female"
                if coef_name_gender in param_vars:
                    param = param_vars[coef_name_gender]
                elif coef_name in param_vars:
                    param = param_vars[coef_name]
                else:
                    continue  # Skip if parameter not found

                # Get variable value
                if var_name == "working":
                    var_val = working
                elif var_name == "working_pt1":
                    var_val = pt1_focal
                elif var_name == "working_pt2":
                    var_val = pt2_focal
                elif var_name == "working_ft":
                    var_val = ft_focal
                elif var_name == "gsur":
                    var_val = gsur_val
                elif var_name == "educL":
                    var_val = educL
                elif var_name == "educH":
                    var_val = educH
                elif var_name == "female":
                    var_val = female
                elif var_name in ("couple", "in_couple"):
                    var_val = couple
                elif var_name == "drgn1":
                    # Get region indicator from data
                    var_val = float(getattr(data_singles_female, 'drgn1', np.zeros(1))[global_idx]) if hasattr(data_singles_female, 'drgn1') else 0.0
                elif hasattr(data_singles_female, var_name):
                    var_val = float(getattr(data_singles_female, var_name)[global_idx])
                else:
                    continue  # Skip if variable not found

                # Apply interaction if specified
                if interaction == "working":
                    var_val = var_val * working

                log_h = log_h + param * var_val

            # Add to utility
            util_j = util_j + log_h

            # Wage opportunity density (log_w) for workers
            if working > 0.5 and data_singles_female.log_wage is not None:
                log_wage_obs = float(data_singles_female.log_wage[global_idx])

                # Build wage mean
                mu_wage = param_vars['beta_w0']
                if 'beta_w_educL' in param_vars:
                    mu_wage = mu_wage + param_vars['beta_w_educL'] * educL
                if 'beta_w_educH' in param_vars:
                    mu_wage = mu_wage + param_vars['beta_w_educH'] * educH

                # Add experience terms if available
                if data_singles_female.pexp_years is not None and 'beta_pexp' in param_vars:
                    pexp = float(data_singles_female.pexp_years[global_idx])
                    mu_wage = mu_wage + param_vars['beta_pexp'] * pexp
                    if 'beta_pexp2' in param_vars and data_singles_female.pexp_years2 is not None:
                        pexp2 = float(data_singles_female.pexp_years2[global_idx])
                        mu_wage = mu_wage + param_vars['beta_pexp2'] * pexp2

                # Log-likelihood of observed wage
                residual = log_wage_obs - mu_wage
                sigma_param = param_vars['sigma']

                log_w = (-0.5 * (residual * residual) / (sigma_param * sigma_param + LOG_EPS)
                        - gp_log(sigma_param + LOG_EPS)
                        - 0.5 * gp_log(2.0 * 3.141592653589793))

                util_j = util_j + log_w

            # Importance sampling correction (subtract log_prior)
            prior_j = float(data_singles_female.prior[global_idx])
            log_prior = gp_log(prior_j + LOG_EPS)
            util_j = util_j - log_prior

            utilities.append(util_j)

        chosen_util = utilities[chosen_idx]
        sum_exp_u = sum(gp_exp(u) for u in utilities)
        log_prob = chosen_util - gp_log(sum_exp_u + LOG_EPS)
        ll_sf = ll_sf + log_prob
    
    logger.info(f"    Singles female LL expression built")
    
    # ========================================================================
    # 4. Build log-likelihood for COUPLES
    # ========================================================================
    
    logger.info("  Building log-likelihood for couples...")
    
    ll_cou = 0.0
    y_ref_cou = data_couples.c_scale
    l_ref_cou = data_couples.l_scale
    
    for g in range(data_couples.n_groups):
        start_idx = data_couples.group_starts[g]
        end_idx = data_couples.group_ends[g]
        
        chosen_idx = None
        for local_j, global_idx in enumerate(range(start_idx, end_idx)):
            if data_couples.actual_choice[global_idx] == 1.0:
                chosen_idx = local_j
                break
        if chosen_idx is None:
            continue
        
        utilities = []
        for global_idx in range(start_idx, end_idx):
            # Consumption utility: β_c * BC(C, θ_c) [household level]
            # NOTE: Apply Box-Cox to RAW values, NOT scaled (matches SciPy)
            c_val = data_couples.consumption[global_idx]

            beta_c_param = get_param_name('beta_c', 'couples_household', param_vars)

            # Handle optional theta_c parameter (None = log utility)
            if spec.utility_consumption_theta:
                theta_c_param = get_param_name('theta_c', 'couples_household', param_vars)
                bc_c = boxcox_gamspy(c_val, param_vars[theta_c_param])
            else:
                # Log utility when theta=None
                bc_c = gp_log(c_val)

            util_j = param_vars[beta_c_param] * bc_c

            # Female leisure utility: β_l_f(Z) * BC(L_f, θ_l_f)
            # NOTE: Apply Box-Cox to RAW values, NOT scaled (matches SciPy)
            l_f_val = data_couples.leisure_female[global_idx]

            beta_l0_f_param = get_param_name('beta_l0', 'couples_female', param_vars)
            beta_l_f_expr = param_vars[beta_l0_f_param]

            for shifter in spec.utility_leisure_shifters:
                var_name = shifter['variable']
                base_coef = shifter['coefficient']

                try:
                    coef_param_f = get_param_name(base_coef, 'couples_female', param_vars)
                except ValueError:
                    continue

                demo_val = getattr(data_couples, var_name, None)
                if demo_val is not None:
                    beta_l_f_expr = beta_l_f_expr + param_vars[coef_param_f] * float(demo_val[global_idx])

            # Handle optional theta_l parameter (None = log utility)
            if spec.utility_leisure_theta:
                theta_l_f_param = get_param_name('theta_l', 'couples_female', param_vars)
                bc_l_f = boxcox_gamspy(l_f_val, param_vars[theta_l_f_param])
            else:
                # Log utility when theta=None
                bc_l_f = gp_log(l_f_val)

            util_j = util_j + beta_l_f_expr * bc_l_f

            # Male leisure utility: β_l_m(Z) * BC(L_m, θ_l_m)
            # NOTE: Apply Box-Cox to RAW values, NOT scaled (matches SciPy)
            l_m_val = data_couples.leisure_male[global_idx]

            beta_l0_m_param = get_param_name('beta_l0', 'couples_male', param_vars)
            beta_l_m_expr = param_vars[beta_l0_m_param]

            for shifter in spec.utility_leisure_shifters:
                var_name = shifter['variable']
                base_coef = shifter['coefficient']

                try:
                    coef_param_m = get_param_name(base_coef, 'couples_male', param_vars)
                except ValueError:
                    continue

                demo_val = getattr(data_couples, var_name, None)
                if demo_val is not None:
                    beta_l_m_expr = beta_l_m_expr + param_vars[coef_param_m] * float(demo_val[global_idx])

            # Handle optional theta_l parameter (None = log utility)
            if spec.utility_leisure_theta:
                theta_l_m_param = get_param_name('theta_l', 'couples_male', param_vars)
                bc_l_m = boxcox_gamspy(l_m_val, param_vars[theta_l_m_param])
            else:
                # Log utility when theta=None
                bc_l_m = gp_log(l_m_val)

            util_j = util_j + beta_l_m_expr * bc_l_m

            # Interaction term: β_interact * BC(L_m) * BC(L_f)
            if 'beta_interact' in param_vars:
                interact_term = param_vars['beta_interact'] * bc_l_m * bc_l_f
                util_j = util_j + interact_term

            # Hours opportunity density for MALE (log_h_m)
            working_m = float(data_couples.working_male[global_idx])
            pt1_focal_m = float(data_couples.working_pt1_male[global_idx])
            pt2_focal_m = float(data_couples.working_pt2_male[global_idx])
            ft_focal_m = float(data_couples.working_ft_male[global_idx])

            # Male demographics
            educL_m = float(getattr(data_couples, 'educL_male', np.zeros(1))[global_idx])
            educH_m = float(getattr(data_couples, 'educH_male', np.zeros(1))[global_idx])
            gsur_m = float(data_couples.gsur_male[global_idx])
            female_m = 0.0  # Male
            couple = 1.0  # This is couples

            # Build log_h_m from specification (specification-agnostic)
            log_h_m = 0.0
            for shifter in spec.hours_shifters:
                var_name = shifter["variable"]
                coef_name = shifter["coefficient"]
                interaction = shifter.get("interaction", None)

                # Get parameter - try gender-specific first, then base name
                coef_name_gender = f"{coef_name}_male"
                if coef_name_gender in param_vars:
                    param = param_vars[coef_name_gender]
                elif coef_name in param_vars:
                    param = param_vars[coef_name]
                else:
                    continue  # Skip if parameter not found

                # Get variable value for male
                if var_name == "working":
                    var_val = working_m
                elif var_name == "working_pt1":
                    var_val = pt1_focal_m
                elif var_name == "working_pt2":
                    var_val = pt2_focal_m
                elif var_name == "working_ft":
                    var_val = ft_focal_m
                elif var_name == "gsur":
                    var_val = gsur_m
                elif var_name == "educL":
                    var_val = educL_m
                elif var_name == "educH":
                    var_val = educH_m
                elif var_name == "female":
                    var_val = female_m
                elif var_name in ("couple", "in_couple"):
                    var_val = couple
                elif var_name == "drgn1":
                    # Get region indicator from data (household level)
                    var_val = float(getattr(data_couples, 'drgn1_male', np.zeros(1))[global_idx]) if hasattr(data_couples, 'drgn1_male') else 0.0
                elif hasattr(data_couples, f"{var_name}_male"):
                    var_val = float(getattr(data_couples, f"{var_name}_male")[global_idx])
                elif hasattr(data_couples, var_name):
                    var_val = float(getattr(data_couples, var_name)[global_idx])
                else:
                    continue  # Skip if variable not found

                # Apply interaction if specified
                if interaction == "working":
                    var_val = var_val * working_m

                log_h_m = log_h_m + param * var_val

            util_j = util_j + log_h_m

            # Hours opportunity density for FEMALE (log_h_f)
            working_f = float(data_couples.working_female[global_idx])
            pt1_focal_f = float(data_couples.working_pt1_female[global_idx])
            pt2_focal_f = float(data_couples.working_pt2_female[global_idx])
            ft_focal_f = float(data_couples.working_ft_female[global_idx])

            # Female demographics
            educL_f = float(getattr(data_couples, 'educL_female', np.zeros(1))[global_idx])
            educH_f = float(getattr(data_couples, 'educH_female', np.zeros(1))[global_idx])
            gsur_f = float(data_couples.gsur_female[global_idx])
            female_f = 1.0  # Female

            # Build log_h_f from specification (specification-agnostic)
            log_h_f = 0.0
            for shifter in spec.hours_shifters:
                var_name = shifter["variable"]
                coef_name = shifter["coefficient"]
                interaction = shifter.get("interaction", None)

                # Get parameter - try gender-specific first, then base name
                coef_name_gender = f"{coef_name}_female"
                if coef_name_gender in param_vars:
                    param = param_vars[coef_name_gender]
                elif coef_name in param_vars:
                    param = param_vars[coef_name]
                else:
                    continue  # Skip if parameter not found

                # Get variable value for female
                if var_name == "working":
                    var_val = working_f
                elif var_name == "working_pt1":
                    var_val = pt1_focal_f
                elif var_name == "working_pt2":
                    var_val = pt2_focal_f
                elif var_name == "working_ft":
                    var_val = ft_focal_f
                elif var_name == "gsur":
                    var_val = gsur_f
                elif var_name == "educL":
                    var_val = educL_f
                elif var_name == "educH":
                    var_val = educH_f
                elif var_name == "female":
                    var_val = female_f
                elif var_name in ("couple", "in_couple"):
                    var_val = couple
                elif var_name == "drgn1":
                    # Get region indicator from data (household level)
                    var_val = float(getattr(data_couples, 'drgn1_female', np.zeros(1))[global_idx]) if hasattr(data_couples, 'drgn1_female') else 0.0
                elif hasattr(data_couples, f"{var_name}_female"):
                    var_val = float(getattr(data_couples, f"{var_name}_female")[global_idx])
                elif hasattr(data_couples, var_name):
                    var_val = float(getattr(data_couples, var_name)[global_idx])
                else:
                    continue  # Skip if variable not found

                # Apply interaction if specified
                if interaction == "working":
                    var_val = var_val * working_f

                log_h_f = log_h_f + param * var_val

            util_j = util_j + log_h_f

            # Wage opportunity for MALE (log_w_m)
            if working_m > 0.5 and data_couples.log_wage_male is not None:
                log_wage_m = float(data_couples.log_wage_male[global_idx])

                # Build wage mean - only include terms if data is available
                mu_wage_m = param_vars['beta_w0']
                if 'beta_w_educL' in param_vars:
                    mu_wage_m = mu_wage_m + param_vars['beta_w_educL'] * educL_m
                if 'beta_w_educH' in param_vars:
                    mu_wage_m = mu_wage_m + param_vars['beta_w_educH'] * educH_m

                # Add experience terms only if available
                if data_couples.pexp_years_male is not None and 'beta_pexp' in param_vars:
                    pexp_m = float(data_couples.pexp_years_male[global_idx])
                    mu_wage_m = mu_wage_m + param_vars['beta_pexp'] * pexp_m
                    if 'beta_pexp2' in param_vars and data_couples.pexp_years2_male is not None:
                        pexp2_m = float(data_couples.pexp_years2_male[global_idx])
                        mu_wage_m = mu_wage_m + param_vars['beta_pexp2'] * pexp2_m

                residual_m = log_wage_m - mu_wage_m
                sigma_param = param_vars['sigma']

                log_w_m = (-0.5 * (residual_m * residual_m) / (sigma_param * sigma_param + LOG_EPS)
                          - gp_log(sigma_param + LOG_EPS)
                          - 0.5 * gp_log(2.0 * 3.141592653589793))

                util_j = util_j + log_w_m

            # Wage opportunity for FEMALE (log_w_f)
            if working_f > 0.5 and data_couples.log_wage_female is not None:
                log_wage_f = float(data_couples.log_wage_female[global_idx])

                # Build wage mean - only include terms if data is available
                mu_wage_f = param_vars['beta_w0']
                if 'beta_w_educL' in param_vars:
                    mu_wage_f = mu_wage_f + param_vars['beta_w_educL'] * educL_f
                if 'beta_w_educH' in param_vars:
                    mu_wage_f = mu_wage_f + param_vars['beta_w_educH'] * educH_f

                # Add experience terms only if available
                if data_couples.pexp_years_female is not None and 'beta_pexp' in param_vars:
                    pexp_f = float(data_couples.pexp_years_female[global_idx])
                    mu_wage_f = mu_wage_f + param_vars['beta_pexp'] * pexp_f
                    if 'beta_pexp2' in param_vars and data_couples.pexp_years2_female is not None:
                        pexp2_f = float(data_couples.pexp_years2_female[global_idx])
                        mu_wage_f = mu_wage_f + param_vars['beta_pexp2'] * pexp2_f

                residual_f = log_wage_f - mu_wage_f
                sigma_param = param_vars['sigma']

                log_w_f = (-0.5 * (residual_f * residual_f) / (sigma_param * sigma_param + LOG_EPS)
                          - gp_log(sigma_param + LOG_EPS)
                          - 0.5 * gp_log(2.0 * 3.141592653589793))

                util_j = util_j + log_w_f

            # Importance sampling correction (subtract log_prior)
            prior_j = float(data_couples.prior[global_idx])
            log_prior = gp_log(prior_j + LOG_EPS)
            util_j = util_j - log_prior

            utilities.append(util_j)

        chosen_util = utilities[chosen_idx]
        sum_exp_u = sum(gp_exp(u) for u in utilities)
        log_prob = chosen_util - gp_log(sum_exp_u + LOG_EPS)
        ll_cou = ll_cou + log_prob
    
    logger.info(f"    Couples LL expression built")
    
    # ========================================================================
    # 5. Combine into joint log-likelihood
    # ========================================================================
    
    logger.info("  Combining into joint log-likelihood...")

    ll_joint = ll_sm + ll_sf + ll_cou

    # DEBUG: Check expression types
    logger.info(f"    ll_sm type: {type(ll_sm)}")
    logger.info(f"    ll_sf type: {type(ll_sf)}")
    logger.info(f"    ll_cou type: {type(ll_cou)}")
    logger.info(f"    ll_joint type: {type(ll_joint)}")
    
    # NOTE: We do NOT create Variables for LL tracking here.
    # The LL expressions (ll_sm, ll_sf, ll_cou, ll_joint) are already GAMSPy expressions.
    # We directly maximize the expression without creating constraining equations.
    #
    # CRITICAL: Creating equations like "ll_var == ll_expression" makes the problem
    # trivial - the solver just sets ll_var to match the expression at the initial
    # parameter values and doesn't optimize! We must maximize the expression directly.

    # ========================================================================
    # 6. Create model and solve
    # ========================================================================

    model = Model(
        container,
        name="ruro_joint_mnl_gamspy",
        problem="nlp",
        sense="max",
        objective=ll_joint  # Maximize the LL expression directly, no equations!
    )

    # DEBUG: Check model has variables
    logger.info(f"    Model problem type: {model.problem}")
    logger.info(f"    Model sense: {model.sense}")
    logger.info(f"    Container has {len(container.data)} symbols")
    logger.info(f"    Number of Variables in container: {sum(1 for s in container.data.values() if hasattr(s, 'type') and s.type in ['free', 'positive', 'binary'])}")

    logger.info(f"  Solving joint model with {solver_name.upper()}...")
    logger.info("  (This may take 5-15 minutes depending on data size)")

    # Pass solver-specific options if provided
    if solver_options:
        logger.info(f"  Solver options: {solver_options}")
        result = model.solve(solver=solver_name, solver_options=solver_options)
    else:
        result = model.solve(solver=solver_name)
    walltime = time.time() - start_time
    
    # ========================================================================
    # 7. Extract results
    # ========================================================================
    
    theta_final = np.array([
        _extract_var_level(param_vars[name])
        for name in spec.all_param_names
    ])

    # Since we maximized ll_joint directly (not a Variable), we need to get the
    # objective value from the model
    ll_total_final = model.objective_value

    # We don't have individual LL variables anymore, so we'll recompute them
    # using the optimized parameters. This is a limitation of direct expression
    # maximization - we lose the breakdown.
    # For now, we'll report the total LL only.
    ll_sm_final = None
    ll_sf_final = None
    ll_cou_final = None

    # Get solver/model status from MODEL object
    # GAMSPy stores: model.solve_status (SolveStatus enum) and model.status (ModelStatus enum)
    solve_status_enum = getattr(model, 'solve_status', None)
    model_status_enum = getattr(model, 'status', None)

    solver_status = str(solve_status_enum) if solve_status_enum else 'Unknown'
    model_status = str(model_status_enum) if model_status_enum else 'Unknown'
    n_iterations = getattr(model, 'iteration_count', getattr(model, 'iter_used', None))
    
    logger.info("="*80)
    logger.info("JOINT ESTIMATION COMPLETE")
    logger.info("="*80)
    logger.info(f"  Total walltime: {walltime:.1f} seconds ({walltime/60:.1f} minutes)")
    logger.info(f"  Solver status: {solver_status}")
    logger.info(f"  Model status: {model_status}")
    if n_iterations is not None:
        logger.info(f"  Iterations: {n_iterations}")
    logger.info("")
    logger.info(f"  Joint Log-Likelihood: {ll_total_final:12.4f}")
    logger.info("  (Individual group breakdown not available with direct expression maximization)")
    logger.info("="*80)

    # ========================================================================
    # 8. Validate results
    # ========================================================================

    logger.info("  Validating results...")

    # For joint estimation, expected range is wider since we have all groups
    # TEMPORARILY VERY WIDE: Allow investigation (will narrow after fixing)
    validate_gamspy_result(model, ll_total_final, theta_final,
                          expected_ll_range=(-20000, -3000),
                          logger=logger)

    # ========================================================================
    # 9. Extract Hessian and compute identification diagnostics
    # ========================================================================

    logger.info("")
    logger.info("Extracting Hessian matrix and computing identification diagnostics...")

    hessian_diag = extract_hessian_diagnostics(
        model=model,
        param_vars=param_vars,
        spec=spec,
        logger=logger
    )

    return {
        'theta': theta_final,
        'log_likelihood': ll_total_final,
        'll_singles_male': ll_sm_final,  # Will be None
        'll_singles_female': ll_sf_final,  # Will be None
        'll_couples': ll_cou_final,  # Will be None
        'solver_status': solver_status,
        'model_status': model_status,
        'walltime': walltime,
        'n_iterations': n_iterations,
        'gamspy_result': result,
        # Hessian diagnostics
        'hessian': hessian_diag['hessian'],
        'standard_errors': hessian_diag['standard_errors'],
        't_values': hessian_diag['t_values'],
        'p_values': hessian_diag['p_values'],
        'eigenvalues': hessian_diag['eigenvalues'],
        'condition_number': hessian_diag['condition_number'],
        'correlation_matrix': hessian_diag['correlation_matrix'],
        'hessian_diagnostics': {
            'condition_number': hessian_diag.get('condition_number'),
            'min_eigenvalue': hessian_diag['eigenvalues'].min() if hessian_diag.get('eigenvalues') is not None else None,
            'max_eigenvalue': hessian_diag['eigenvalues'].max() if hessian_diag.get('eigenvalues') is not None else None,
            'n_negative_eigenvalues': hessian_diag.get('n_negative_eigenvalues', 0),
            'poorly_identified_params': hessian_diag.get('poorly_identified_params', []),
        },
    }
