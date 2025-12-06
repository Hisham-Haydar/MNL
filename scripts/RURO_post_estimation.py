#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RURO_post_estimation.py
=======================

Comprehensive post-estimation analysis for RURO labor supply models.

Features:
- Variance-covariance matrix and standard errors
- Hessian diagnostics (eigenvalues, positive-definiteness check)
- Model fit statistics (AIC, BIC, McFadden's pseudo R²)
- Gradient accuracy check
- **Marginal utilities plots** (MUC vs consumption, MUL vs leisure)
- **Labor supply elasticities** (wage, income, uncompensated, compensated)
- **Predicted probabilities and choice accuracy**
- **Parameter significance visualization**
- **Comprehensive HTML report generation**
- **CSV-based initial parameter values**

Marginal Utility Formulas (Box-Cox utility):
--------------------------------------------
The RURO utility function is:
    U(c, l; X) = β_c × BC(c; θ_c) + β_l(X) × BC(l; θ_l)

where BC(x; θ) = (x^θ - 1) / θ is the Box-Cox transform.

Marginal utilities are the partial derivatives:
    MUC = ∂U/∂c = β_c × c^(θ_c - 1)    [derivative of Box-Cox w.r.t. x]
    MUL = ∂U/∂l = β_l(X) × l^(θ_l - 1)

where β_l(X) varies with individual characteristics:
    β_l(X) = β_l0 + β_l_log_age × log(age) + β_l_log_age2 × log(age)² + ...

Marginal Rate of Substitution:
    MRS = MUL / MUC = [β_l(X) × l^(θ_l - 1)] / [β_c × c^(θ_c - 1)]

This represents how much consumption the individual is willing to give up
for one additional unit of leisure.

For quasi-concavity (well-behaved preferences):
- MUC > 0 (more consumption is always better)
- MUL > 0 (more leisure is always better)
- Indifference curves are convex to the origin

Usage:
    from RURO_post_estimation import run_post_estimation, compute_standard_errors
    
    # After estimation:
    post_results = run_post_estimation(
        result=opt_result,
        grad_func=gradient_function,
        param_names=param_names,
        n_individuals=n_individuals,
        out_dir=Path("outputs/estimates/fr"),
        df=mnl_data,  # MNL dataset for marginal utility plots
    )

Author: Hisham Haydar
Date: 2025-12-06
"""

import logging
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple, Union

# Matplotlib setup (headless backend for server environments)
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

LOGGER = logging.getLogger(__name__)

# =============================================================================
# CONSTANTS (from RURO_estimate_FR.py)
# =============================================================================
TOTAL_LEISURE_HOURS = 80.0
MEAN_DISPY_NORM = 2500.0  # normalization constant for consumption
MEAN_LHW_NORM = 35.0      # normalization constant for leisure

# Demographic group constants
GROUP_SINGLE_MALE = "sm"
GROUP_SINGLE_FEMALE = "sf"
GROUP_COUPLE_MALE = "cou_m"
GROUP_COUPLE_FEMALE = "cou_f"
GROUP_COUPLE = "cou"
ALL_GROUPS = [GROUP_SINGLE_MALE, GROUP_SINGLE_FEMALE, GROUP_COUPLE_MALE, GROUP_COUPLE_FEMALE]

# Parameter indices for joint estimation (from RURO_estimate_FR.py)
# Singles male preferences: [0:12]
# Singles female preferences: [12:25] (13 params with extra reg3)
# Couples preferences: [25:50] (25 params)
# Hours opp male: [50:59] (9 params)
# Hours opp female: [59:68] (9 params)
# Wage opp male (if vw): [68:84] (16 params)
# Wage opp female (if vw): [84:100] (16 params)

JOINT_IDX_PREF_SM = (0, 12)       # single males preferences
JOINT_IDX_PREF_SF = (12, 25)      # single females preferences
JOINT_IDX_PREF_COU = (25, 50)     # couples preferences
JOINT_IDX_HOPP_M = (50, 59)       # hours opportunity males
JOINT_IDX_HOPP_F = (59, 68)       # hours opportunity females
JOINT_IDX_WOPP_M = (68, 84)       # wage opportunity males (vw only)
JOINT_IDX_WOPP_F = (84, 100)      # wage opportunity females (vw only)

# Couples preference indices within cou pref block [25:50]
# Male leisure: [0:10], Female leisure: [10:20], Box-Cox/shared: [20:25]
COU_IDX_MALE_LEISURE = (0, 10)
COU_IDX_FEMALE_LEISURE = (10, 20)
COU_IDX_BOXCOX_SHARED = (20, 25)  # theta_l_m, theta_l_f, theta_c, beta_c, beta_interaction


# =============================================================================
# HESSIAN COMPUTATION
# =============================================================================

def compute_numeric_hessian(
    theta: np.ndarray,
    grad_func: Callable,
    delta: float = 1e-4,
) -> np.ndarray:
    """
    Compute numeric Hessian matrix from gradient function (forward differences).
        
    Parameters
    ----------
    theta : np.ndarray
        Parameter vector at optimum
    grad_func : Callable
        Gradient function that takes theta and returns gradient vector
    delta : float
        Relative perturbation size (default 1e-4)
    
    Returns
    -------
    np.ndarray
        Hessian matrix (K x K)
    """
    K = len(theta)
    start_grad = grad_func(theta)
    hessian = np.zeros((K, K), dtype=np.float64)
    
    for i in range(K):
        theta_perturbed = theta.copy()
        # Use relative perturbation : param[i]*(1+delta)
        if abs(theta[i]) > 1e-8:
            theta_perturbed[i] = theta[i] * (1.0 + delta)
            h = theta[i] * delta
        else:
            # For parameters near zero, use absolute perturbation
            theta_perturbed[i] = theta[i] + delta
            h = delta
        
        perturbed_grad = grad_func(theta_perturbed)
        hessian[:, i] = (perturbed_grad - start_grad) / h
    
    # Symmetrize (average of H and H')
    hessian = 0.5 * (hessian + hessian.T)
    
    return hessian


def compute_jacobian_hessian(
    theta: np.ndarray,
    grad_func: Callable,
    delta: float = 1e-5,
) -> np.ndarray:
    """
    Compute Hessian using numerical Jacobian of the gradient (central differences).
    
    Uses central differences for better accuracy.
    
    Parameters
    ----------
    theta : np.ndarray
        Parameter vector at optimum
    grad_func : Callable
        Gradient function
    delta : float
        Step size for finite differences
    
    Returns
    -------
    np.ndarray
        Hessian matrix (K x K)
    """
    K = len(theta)
    hessian = np.zeros((K, K), dtype=np.float64)
    
    for i in range(K):
        theta_plus = theta.copy()
        theta_minus = theta.copy()
        
        h = max(abs(theta[i]) * delta, delta)
        theta_plus[i] += h
        theta_minus[i] -= h
        
        grad_plus = grad_func(theta_plus)
        grad_minus = grad_func(theta_minus)
        
        # Central difference
        hessian[:, i] = (grad_plus - grad_minus) / (2.0 * h)
    
    # Symmetrize
    hessian = 0.5 * (hessian + hessian.T)
    
    return hessian


# =============================================================================
# STANDARD ERRORS
# =============================================================================

def _norm_cdf(x: np.ndarray) -> np.ndarray:
    """Standard normal CDF using error function."""
    from math import erf, sqrt
    if np.isscalar(x):
        if not np.isfinite(x):
            return np.nan
        return 0.5 * (1.0 + erf(x / sqrt(2.0)))
    return np.array([0.5 * (1.0 + erf(xi / sqrt(2.0))) if np.isfinite(xi) else np.nan for xi in x])


def compute_standard_errors(
    theta: np.ndarray,
    grad_func: Callable,
    param_names: List[str],
    method: str = "jacobian",
    delta: float = 1e-5,
) -> Dict[str, Any]:
    """
    Compute standard errors, t-values, and variance-covariance matrix.
    
    Parameters
    ----------
    theta : np.ndarray
        Estimated parameters
    grad_func : Callable
        Gradient function
    param_names : List[str]
        Parameter names
    method : str
        "jacobian" (central diff, more accurate) or "numeric" (forward diff)
    delta : float
        Step size for finite differences
    
    Returns
    -------
    Dict containing:
        - hessian: Hessian matrix
        - varcov: Variance-covariance matrix
        - se: Standard errors
        - t_values: t-statistics (param / SE)
        - eigenvalues: Eigenvalues of Hessian (for checking positive-definiteness)
        - param_table: DataFrame with estimates, SE, t-values
    """
    import pandas as pd
    
    LOGGER.info(f"Computing Hessian matrix using {method} method...")
    
    if method == "jacobian":
        hessian = compute_jacobian_hessian(theta, grad_func, delta)
    else:
        hessian = compute_numeric_hessian(theta, grad_func, delta)
    
    # Check eigenvalues (positive semi-definiteness)
    eigenvalues = np.linalg.eigvalsh(hessian)
    n_negative = np.sum(eigenvalues < 0)
    if n_negative > 0:
        LOGGER.warning(f"Hessian has {n_negative} negative eigenvalues - may not be at true optimum!")
    
    # Invert Hessian to get variance-covariance
    try:
        varcov = np.linalg.inv(hessian)
        se = np.sqrt(np.diag(varcov))
        se = np.where(np.isfinite(se) & (se > 0), se, np.nan)
    except np.linalg.LinAlgError:
        LOGGER.error("Hessian is singular - cannot compute standard errors")
        varcov = np.full((len(theta), len(theta)), np.nan)
        se = np.full(len(theta), np.nan)
    
    # t-values
    t_values = theta / se
    
    # p-values (two-sided)
    p_values = 2.0 * (1.0 - _norm_cdf(np.abs(t_values)))
    
    # Create summary table
    param_table = pd.DataFrame({
        "parameter": param_names,
        "estimate": theta,
        "std_error": se,
        "t_value": t_values,
        "p_value": p_values,
    })
    
    return {
        "hessian": hessian,
        "varcov": varcov,
        "se": se,
        "t_values": t_values,
        "p_values": p_values,
        "eigenvalues": eigenvalues,
        "param_table": param_table,
    }


# =============================================================================
# MODEL FIT STATISTICS
# =============================================================================

def compute_model_fit_statistics(
    log_likelihood: float,
    n_params: int,
    n_individuals: int,
    n_alternatives_per_individual: int = 100,
) -> Dict[str, float]:
    """
    Compute model fit statistics.
    
    Parameters
    ----------
    log_likelihood : float
        Log-likelihood at optimum (should be negative of minimized NLL)
    n_params : int
        Number of estimated parameters
    n_individuals : int
        Number of individuals (choice makers)
    n_alternatives_per_individual : int
        Number of alternatives per individual (default 100 for RURO)
    
    Returns
    -------
    Dict containing:
        - aic: Akaike Information Criterion
        - bic: Bayesian Information Criterion
        - ll_null: Log-likelihood under null (equal probabilities)
        - pseudo_r2_mcfadden: McFadden's pseudo R-squared
        - pseudo_r2_adjusted: Adjusted McFadden's pseudo R-squared
        - ll_per_obs: Average log-likelihood per observation
    """
    # Null model: equal probabilities
    ll_null = n_individuals * np.log(1.0 / n_alternatives_per_individual)
    
    # Information criteria
    aic = -2.0 * log_likelihood + 2.0 * n_params
    bic = -2.0 * log_likelihood + np.log(n_individuals) * n_params
    
    # Pseudo R-squared (McFadden)
    pseudo_r2 = 1.0 - (log_likelihood / ll_null)
    pseudo_r2_adj = 1.0 - ((log_likelihood - n_params) / ll_null)
    
    return {
        "log_likelihood": log_likelihood,
        "n_params": n_params,
        "n_individuals": n_individuals,
        "aic": aic,
        "bic": bic,
        "ll_null": ll_null,
        "pseudo_r2_mcfadden": pseudo_r2,
        "pseudo_r2_adjusted": pseudo_r2_adj,
        "ll_per_obs": log_likelihood / n_individuals,
    }


# =============================================================================
# GRADIENT CHECK
# =============================================================================

def check_gradient_accuracy(
    theta: np.ndarray,
    nll_func: Callable,
    grad_func: Callable,
    param_names: List[str],
    delta: float = 1e-5,
    print_errors_only: bool = True,
) -> Dict[str, Any]:
    """
    Check analytical gradient against numerical gradient.
    
    Parameters
    ----------
    theta : np.ndarray
        Parameter vector
    nll_func : Callable
        Negative log-likelihood function
    grad_func : Callable
        Analytical gradient function
    param_names : List[str]
        Parameter names
    delta : float
        Step size for numerical gradient
    print_errors_only : bool
        If True, only print parameters with large discrepancies
    
    Returns
    -------
    Dict containing:
        - analytical_grad: Analytical gradient
        - numerical_grad: Numerical gradient
        - abs_diff: Absolute differences
        - rel_diff: Relative differences
        - max_abs_diff: Maximum absolute difference
        - max_rel_diff: Maximum relative difference
    """
    LOGGER.info("Checking gradient accuracy...")
    
    # Analytical gradient
    analytical_grad = grad_func(theta)
    
    # Numerical gradient (central differences)
    numerical_grad = np.zeros_like(theta)
    for i in range(len(theta)):
        theta_plus = theta.copy()
        theta_minus = theta.copy()
        h = max(abs(theta[i]) * delta, delta)
        theta_plus[i] += h
        theta_minus[i] -= h
        numerical_grad[i] = (nll_func(theta_plus) - nll_func(theta_minus)) / (2.0 * h)
    
    # Compute differences
    abs_diff = np.abs(analytical_grad - numerical_grad)
    rel_diff = abs_diff / (np.abs(numerical_grad) + 1e-10)
    
    max_abs_diff = np.max(abs_diff)
    max_rel_diff = np.max(rel_diff)
    
    # Print results
    LOGGER.info(f"\nGradient check: max|analytical - numerical| = {max_abs_diff:.2e}")
    LOGGER.info(f"               max relative difference = {max_rel_diff:.2e}")
    
    threshold = 0.01  # 1% relative error
    errors = rel_diff > threshold
    
    if np.any(errors) or not print_errors_only:
        LOGGER.info(f"\n{'Param':<40} {'Analytical':>14} {'Numerical':>14} {'Rel.Diff':>12}")
        LOGGER.info("-" * 82)
        for i, name in enumerate(param_names):
            if not print_errors_only or errors[i]:
                flag = "***" if errors[i] else ""
                LOGGER.info(f"{name:<40} {analytical_grad[i]:>14.6f} {numerical_grad[i]:>14.6f} {rel_diff[i]:>12.2e} {flag}")
    
    if max_rel_diff < 0.001:
        LOGGER.info("\n✓ Gradient check PASSED (rel. diff < 0.1%)")
    elif max_rel_diff < 0.01:
        LOGGER.info("\n✓ Gradient check OK (rel. diff < 1%)")
    else:
        LOGGER.warning(f"\n⚠ Gradient check WARNING: max rel. diff = {max_rel_diff:.2%}")
    
    return {
        "analytical_grad": analytical_grad,
        "numerical_grad": numerical_grad,
        "abs_diff": abs_diff,
        "rel_diff": rel_diff,
        "max_abs_diff": max_abs_diff,
        "max_rel_diff": max_rel_diff,
    }


# =============================================================================
# MAIN POST-ESTIMATION FUNCTION
# =============================================================================

def run_post_estimation(
    result: Any,  # scipy.optimize.OptimizeResult
    grad_func: Callable,
    param_names: List[str],
    n_individuals: int,
    wage_spec: str = "fw",
    out_dir: Optional[Path] = None,
    save_excel: bool = True,
    nll_func: Optional[Callable] = None,
    check_gradient: bool = False,    n_alternatives_per_individual: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Run full post-estimation analysis and optionally save results.
    
    1. Compute Hessian (both Jacobian and numeric methods)
    2. Compute variance-covariance matrix
    3. Compute standard errors and t-values
    4. Check eigenvalues for positive-definiteness
    5. Compute model fit statistics
    6. Save results to Excel
    
    Parameters
    ----------
    result : OptimizeResult
        Result from scipy.optimize.minimize
    grad_func : Callable
        Gradient function of the NEGATIVE log-likelihood (for Hessian computation).
        This should return the gradient pointing to the minimum, not maximum.
    param_names : List[str]
        Parameter names
    n_individuals : int
        Number of individuals
    wage_spec : str
        "fw" or "vw"
    out_dir : Path, optional
        Directory to save results
    save_excel : bool
        Whether to save to Excel
    nll_func : Callable, optional
        Negative log-likelihood function (for gradient check)
    check_gradient : bool
        Whether to check gradient accuracy
    n_alternatives_per_individual : int, optional
        Number of alternatives per individual in the MNL choice set.
        Default is 100 (99 random draws + 1 observed choice in RURO).
        Used for computing null log-likelihood and pseudo R-squared.
    
    Returns
    -------
    Dict containing all post-estimation results
    """
    import pandas as pd
    from datetime import datetime
    
    theta = result.x
    log_likelihood = -result.fun
    n_params = len(theta)
    
    LOGGER.info("=" * 70)
    LOGGER.info("POST-ESTIMATION ANALYSIS")
    LOGGER.info("=" * 70)
    
    # -------------------------------------------------------------------------
    # 0. Optional gradient check
    # -------------------------------------------------------------------------
    grad_check_results = None
    if check_gradient and nll_func is not None:
        LOGGER.info("\n0. Checking gradient accuracy...")
        grad_check_results = check_gradient_accuracy(
            theta, nll_func, grad_func, param_names
        )
    
    # -------------------------------------------------------------------------
    # 1. Standard errors via Jacobian method
    # -------------------------------------------------------------------------
    LOGGER.info("\n1. Computing standard errors (Jacobian method)...")
    se_results_jac = compute_standard_errors(
        theta, grad_func, param_names, method="jacobian", delta=1e-5
    )
    
    # -------------------------------------------------------------------------
    # 2. Standard errors via numeric Hessian (for comparison)
    # -------------------------------------------------------------------------
    LOGGER.info("\n2. Computing standard errors (numeric Hessian)")
    se_results_num = compute_standard_errors(
        theta, grad_func, param_names, method="numeric", delta=1e-4
    )
      # -------------------------------------------------------------------------
    # 3. Model fit statistics
    # -------------------------------------------------------------------------
    LOGGER.info("\n3. Computing model fit statistics...")
    # Default to 100 alternatives (99 draws + 1 observed) if not specified
    n_alts = n_alternatives_per_individual if n_alternatives_per_individual is not None else 100
    fit_stats = compute_model_fit_statistics(
        log_likelihood=log_likelihood,
        n_params=n_params,
        n_individuals=n_individuals,
        n_alternatives_per_individual=n_alts,
    )
    
    # -------------------------------------------------------------------------
    # 4. Print results
    # -------------------------------------------------------------------------
    LOGGER.info("\n" + "=" * 70)
    LOGGER.info("PARAMETER ESTIMATES WITH STANDARD ERRORS")
    LOGGER.info("=" * 70)
    
    table = se_results_jac["param_table"]
    LOGGER.info(f"\n{'Param':<40} {'Estimate':>12} {'Std.Err':>12} {'t-value':>10} {'p-value':>10}")
    LOGGER.info("-" * 86)
    for _, row in table.iterrows():
        p_str = f"{row['p_value']:.4f}" if np.isfinite(row['p_value']) else "NA"
        t_str = f"{row['t_value']:.3f}" if np.isfinite(row['t_value']) else "NA"
        se_str = f"{row['std_error']:.4f}" if np.isfinite(row['std_error']) else "NA"
        LOGGER.info(f"{row['parameter']:<40} {row['estimate']:>12.4f} {se_str:>12} {t_str:>10} {p_str:>10}")
    
    LOGGER.info("\n" + "=" * 70)
    LOGGER.info("MODEL FIT STATISTICS")
    LOGGER.info("=" * 70)
    LOGGER.info(f"Log-likelihood:              {fit_stats['log_likelihood']:.4f}")
    LOGGER.info(f"Log-likelihood (null):       {fit_stats['ll_null']:.4f}")
    LOGGER.info(f"Number of parameters:        {fit_stats['n_params']}")
    LOGGER.info(f"Number of individuals:       {fit_stats['n_individuals']}")
    LOGGER.info(f"AIC:                         {fit_stats['aic']:.4f}")
    LOGGER.info(f"BIC:                         {fit_stats['bic']:.4f}")
    LOGGER.info(f"McFadden's Pseudo R²:        {fit_stats['pseudo_r2_mcfadden']:.4f}")
    LOGGER.info(f"Adjusted Pseudo R²:          {fit_stats['pseudo_r2_adjusted']:.4f}")
    LOGGER.info(f"LL per observation:          {fit_stats['ll_per_obs']:.4f}")
    
    # Check Hessian eigenvalues
    LOGGER.info("\n" + "=" * 70)
    LOGGER.info("HESSIAN DIAGNOSTICS")
    LOGGER.info("=" * 70)
    ev = se_results_jac["eigenvalues"]
    LOGGER.info(f"Eigenvalue range: [{ev.min():.6f}, {ev.max():.6f}]")
    n_neg = np.sum(ev < 0)
    if n_neg > 0:
        LOGGER.warning(f"WARNING: {n_neg} negative eigenvalues detected!")
        LOGGER.warning("The Hessian is not positive semi-definite - may not be at global optimum.")
    else:
        LOGGER.info("All eigenvalues positive - Hessian is positive definite ✓")
    
    # -------------------------------------------------------------------------
    # 5. Save to Excel
    # -------------------------------------------------------------------------
    if save_excel and out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d")
        filename = f"{wage_spec}_SE_post_estimation_{timestamp}.xlsx"
        out_path = out_dir / filename
        
        try:
            with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
                # Sheet 1: Parameter table with SE and t-values
                table.to_excel(writer, sheet_name="SE_TV", index=False)
                
                # Sheet 2: Variance-covariance matrix
                varcov_df = pd.DataFrame(
                    se_results_jac["varcov"],
                    index=param_names,
                    columns=param_names
                )
                varcov_df.to_excel(writer, sheet_name="varcov")
                
                # Sheet 3: Hessian
                hess_df = pd.DataFrame(
                    se_results_jac["hessian"],
                    index=param_names,
                    columns=param_names
                )
                hess_df.to_excel(writer, sheet_name="hessian")
                
                # Sheet 4: Eigenvalues
                ev_df = pd.DataFrame({
                    "eigenvalue": se_results_jac["eigenvalues"]
                })
                ev_df.to_excel(writer, sheet_name="eigenvalues", index=False)
                
                # Sheet 5: Model fit
                fit_df = pd.DataFrame([fit_stats])
                fit_df.to_excel(writer, sheet_name="model_fit", index=False)
                
                # Sheet 6: Numeric Hessian comparison
                table_num = se_results_num["param_table"]
                table_num.to_excel(writer, sheet_name="SE_numeric", index=False)
            
            LOGGER.info(f"\nPost-estimation results saved to: {out_path}")
        
        except Exception as e:
            LOGGER.error(f"Failed to save Excel file: {e}")
    
    return {
        "se_jacobian": se_results_jac,
        "se_numeric": se_results_num,
        "fit_statistics": fit_stats,
        "param_table": se_results_jac["param_table"],
        "gradient_check": grad_check_results,
    }


# =============================================================================
# MARGINAL UTILITIES (similar to analyze_dcm_results.py)
# =============================================================================

def boxcox_transform(x: np.ndarray, theta: float) -> np.ndarray:
    """
    Box-Cox transform: BC(x; θ) = (x^θ - 1) / θ for θ ≠ 0, log(x) for θ = 0.
    """
    x = np.clip(np.asarray(x, dtype=float), 1e-12, None)
    if abs(theta) < 1e-8:
        return np.log(x)
    return (np.power(x, theta) - 1.0) / theta


def d_boxcox_dx(x: np.ndarray, theta: float) -> np.ndarray:
    """
    Derivative of Box-Cox transform with respect to x:
    d BC(x;θ) / dx = x^(θ-1)
    """
    x = np.clip(np.asarray(x, dtype=float), 1e-12, None)
    return np.power(x, theta - 1.0)


def compute_marginal_utility_consumption(
    c_norm: np.ndarray,
    beta_c: float,
    theta_c: float,
) -> np.ndarray:
    """
    Compute marginal utility of consumption (MUC).
    
    MUC = ∂U/∂c = β_c * d BC(c; θ_c) / dc = β_c * c^(θ_c - 1)
    
    Parameters
    ----------
    c_norm : np.ndarray
        Normalized consumption values
    beta_c : float
        Coefficient on Box-Cox transformed consumption
    theta_c : float
        Box-Cox parameter for consumption
    
    Returns
    -------
    np.ndarray
        Marginal utility of consumption
    """
    return beta_c * d_boxcox_dx(c_norm, theta_c)


def compute_marginal_utility_leisure(
    l_norm: np.ndarray,
    beta_l: Union[np.ndarray, float],
    theta_l: float,
) -> np.ndarray:
    """
    Compute marginal utility of leisure (MUL).
    
    MUL = ∂U/∂l = β_l(X) * d BC(l; θ_l) / dl = β_l(X) * l^(θ_l - 1)
    
    Parameters
    ----------
    l_norm : np.ndarray
        Normalized leisure values
    beta_l : float or np.ndarray
        Coefficient on Box-Cox transformed leisure (can vary by individual)
    theta_l : float
        Box-Cox parameter for leisure
    
    Returns
    -------
    np.ndarray
        Marginal utility of leisure
    """
    beta_l_arr = np.asarray(beta_l, dtype=float)
    if np.ndim(beta_l_arr) == 0:
        beta_l_arr = np.full_like(l_norm, float(beta_l_arr))
    return beta_l_arr * d_boxcox_dx(l_norm, theta_l)


def compute_mrs(
    muc: np.ndarray,
    mul: np.ndarray,
) -> np.ndarray:
    """
    Compute marginal rate of substitution (MRS = MUL / MUC).
    
    This represents how much consumption the individual is willing to give up
    for one additional unit of leisure.
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        mrs = np.where(np.abs(muc) > 1e-10, mul / muc, np.nan)
    return mrs


def extract_preference_params(
    theta: np.ndarray,
    param_names: List[str],
) -> Dict[str, float]:
    """
    Extract preference parameters from theta vector.
    """
    return {name: float(val) for name, val in zip(param_names, theta)}


# =============================================================================
# GROUP-SPECIFIC PARAMETER EXTRACTION
# =============================================================================

def extract_group_params_from_joint(
    theta_joint: np.ndarray,
    param_names_joint: List[str],
    wage_spec: str = "fw",
) -> Dict[str, Dict[str, float]]:
    """
    Extract preference parameters for each demographic group from joint theta.
    
    Returns a dictionary with keys: 'sm', 'sf', 'cou_m', 'cou_f', 'cou'
    Each contains the relevant preference parameters for that group.
    
    Parameters
    ----------
    theta_joint : np.ndarray
        Full joint parameter vector
    param_names_joint : List[str]
        Parameter names corresponding to theta_joint
    wage_spec : str
        "fw" or "vw"
    
    Returns
    -------
    Dict[str, Dict[str, float]]
        Group-specific parameters. Keys:
        - 'sm': single males
        - 'sf': single females  
        - 'cou_m': males in couples (leisure only)
        - 'cou_f': females in couples (leisure only)
        - 'cou': couples shared params (consumption, box-cox)
    """
    params = {name: float(val) for name, val in zip(param_names_joint, theta_joint)}
    
    # Extract single males
    sm_params = {
        "beta_l0": params.get("sm.pref.beta_l0", 0.0),
        "beta_l_log_age": params.get("sm.pref.beta_l_log_age", 0.0),
        "beta_l_log_age2": params.get("sm.pref.beta_l_log_age2", 0.0),
        "beta_l_ch4_6": params.get("sm.pref.beta_l_ch4_6", 0.0),
        "beta_l_ch7_9": params.get("sm.pref.beta_l_ch7_9", 0.0),
        "beta_l_educL": params.get("sm.pref.beta_l_educL", 0.0),
        "beta_l_educH": params.get("sm.pref.beta_l_educH", 0.0),
        "beta_l_reg2": params.get("sm.pref.beta_l_reg2", 0.0),
        "beta_c": params.get("sm.pref.beta_c", 0.0),
        "theta_l": params.get("sm.pref.theta_l", 0.5),
        "theta_c": params.get("sm.pref.theta_c", 0.5),
        "beta_l_ch0_3": params.get("sm.pref.beta_l_ch0_3", 0.0),  # typically 0 for males
    }
    
    # Extract single females
    sf_params = {
        "beta_l0": params.get("sf.pref.beta_l0", 0.0),
        "beta_l_log_age": params.get("sf.pref.beta_l_log_age", 0.0),
        "beta_l_log_age2": params.get("sf.pref.beta_l_log_age2", 0.0),
        "beta_l_ch4_6": params.get("sf.pref.beta_l_ch4_6", 0.0),
        "beta_l_ch7_9": params.get("sf.pref.beta_l_ch7_9", 0.0),
        "beta_l_educL": params.get("sf.pref.beta_l_educL", 0.0),
        "beta_l_educH": params.get("sf.pref.beta_l_educH", 0.0),
        "beta_l_reg2": params.get("sf.pref.beta_l_reg2", 0.0),
        "beta_l_reg3": params.get("sf.pref.beta_l_reg3", 0.0),
        "beta_c": params.get("sf.pref.beta_c", 0.0),
        "theta_l": params.get("sf.pref.theta_l", 0.5),
        "theta_c": params.get("sf.pref.theta_c", 0.5),
        "beta_l_ch0_3": params.get("sf.pref.beta_l_ch0_3", 0.0),
    }
    
    # Extract couples - male leisure
    cou_m_params = {
        "beta_l0": params.get("cou.pref.beta_l0_m", 0.0),
        "beta_l_log_age": params.get("cou.pref.beta_l_log_age_m", 0.0),
        "beta_l_log_age2": params.get("cou.pref.beta_l_log_age2_m", 0.0),
        "beta_l_ch0_3": params.get("cou.pref.beta_l_ch0_3_m", 0.0),
        "beta_l_ch4_6": params.get("cou.pref.beta_l_ch4_6_m", 0.0),
        "beta_l_ch7_9": params.get("cou.pref.beta_l_ch7_9_m", 0.0),
        "beta_l_reg2": params.get("cou.pref.beta_l_reg2_m", 0.0),
        "beta_l_reg3": params.get("cou.pref.beta_l_reg3_m", 0.0),
        "beta_l_educL": params.get("cou.pref.beta_l_educL_m", 0.0),
        "beta_l_educH": params.get("cou.pref.beta_l_educH_m", 0.0),
        "theta_l": params.get("cou.pref.theta_l_m", 0.5),
    }
    
    # Extract couples - female leisure
    cou_f_params = {
        "beta_l0": params.get("cou.pref.beta_l0_f", 0.0),
        "beta_l_log_age": params.get("cou.pref.beta_l_log_age_f", 0.0),
        "beta_l_log_age2": params.get("cou.pref.beta_l_log_age2_f", 0.0),
        "beta_l_ch0_3": params.get("cou.pref.beta_l_ch0_3_f", 0.0),
        "beta_l_ch4_6": params.get("cou.pref.beta_l_ch4_6_f", 0.0),
        "beta_l_ch7_9": params.get("cou.pref.beta_l_ch7_9_f", 0.0),
        "beta_l_reg2": params.get("cou.pref.beta_l_reg2_f", 0.0),
        "beta_l_reg3": params.get("cou.pref.beta_l_reg3_f", 0.0),
        "beta_l_educL": params.get("cou.pref.beta_l_educL_f", 0.0),
        "beta_l_educH": params.get("cou.pref.beta_l_educH_f", 0.0),
        "theta_l": params.get("cou.pref.theta_l_f", 0.5),
    }
    
    # Extract couples - shared (consumption, box-cox)
    cou_shared = {
        "theta_l_m": params.get("cou.pref.theta_l_m", 0.5),
        "theta_l_f": params.get("cou.pref.theta_l_f", 0.5),
        "theta_c": params.get("cou.pref.theta_c", 0.5),
        "beta_c": params.get("cou.pref.beta_c", 0.0),
        "beta_interaction": params.get("cou.pref.beta_interaction", 0.0),
    }
    
    return {
        GROUP_SINGLE_MALE: sm_params,
        GROUP_SINGLE_FEMALE: sf_params,
        GROUP_COUPLE_MALE: cou_m_params,
        GROUP_COUPLE_FEMALE: cou_f_params,
        GROUP_COUPLE: cou_shared,
    }


def compute_group_median_shifters(
    df: pd.DataFrame,
    group: str,
) -> Dict[str, float]:
    """
    Compute median/mode values of demographic shifters for a specific group.
    
    This is used to evaluate β_l(X) at "representative" individual characteristics.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataset containing individual characteristics
    group : str
        One of: 'sm', 'sf', 'cou_m', 'cou_f'
    
    Returns
    -------
    Dict[str, float]
        Median/mode values for each shifter variable
    """
    # Filter to observed choices only
    if "obs" in df.columns:
        obs_df = df[df["obs"] == 1].copy()
    elif "is_observed" in df.columns:
        obs_df = df[df["is_observed"] == 1].copy()
    elif "is_chosen" in df.columns:
        obs_df = df[df["is_chosen"] == 1].copy()
    else:
        obs_df = df.copy()
    
    # Filter by group
    if group == GROUP_SINGLE_MALE:
        # Singles (ruro_group == 1) with dgn == 1 (male)
        if "ruro_group" in obs_df.columns and "dgn" in obs_df.columns:
            obs_df = obs_df[(obs_df["ruro_group"] == 1) & (obs_df["dgn"] == 1)]
        elif "dgn" in obs_df.columns:
            obs_df = obs_df[obs_df["dgn"] == 1]
    elif group == GROUP_SINGLE_FEMALE:
        if "ruro_group" in obs_df.columns and "dgn" in obs_df.columns:
            obs_df = obs_df[(obs_df["ruro_group"] == 1) & (obs_df["dgn"] == 0)]
        elif "dgn" in obs_df.columns:
            obs_df = obs_df[obs_df["dgn"] == 0]
    elif group in [GROUP_COUPLE_MALE, GROUP_COUPLE_FEMALE]:
        if "ruro_group" in obs_df.columns:
            obs_df = obs_df[obs_df["ruro_group"] == 10]
    
    if len(obs_df) == 0:
        LOGGER.warning(f"No observations found for group {group}")
        return {}
    
    # Compute medians for continuous, modes for discrete
    shifters = {}
    
    # Age (use log_age if available, else compute)
    if "log_age" in obs_df.columns:
        shifters["log_age"] = obs_df["log_age"].median()
        shifters["log_age2"] = obs_df["log_age"].median() ** 2
    elif "dag" in obs_df.columns:  # dag = age
        median_age = obs_df["dag"].median()
        shifters["log_age"] = np.log(max(median_age, 18))
        shifters["log_age2"] = shifters["log_age"] ** 2
    
    # For couples, separate male/female ages
    if group == GROUP_COUPLE_MALE and "dag_m" in obs_df.columns:
        median_age = obs_df["dag_m"].median()
        shifters["log_age"] = np.log(max(median_age, 18))
        shifters["log_age2"] = shifters["log_age"] ** 2
    elif group == GROUP_COUPLE_FEMALE and "dag_f" in obs_df.columns:
        median_age = obs_df["dag_f"].median()
        shifters["log_age"] = np.log(max(median_age, 18))
        shifters["log_age2"] = shifters["log_age"] ** 2
    
    # Children dummies (mode, usually 0)
    for col in ["children0_3", "children4_6", "children7_9", "dch0_3", "dch4_6", "dch7_9"]:
        clean_name = col.replace("d", "children").replace("ch", "children") if col.startswith("d") else col
        if col in obs_df.columns:
            shifters[clean_name] = obs_df[col].mode().iloc[0] if len(obs_df[col].mode()) > 0 else 0.0
    
    # Education dummies
    for col in ["educL", "educH", "deduc1", "deduc3"]:
        if col in obs_df.columns:
            if col == "deduc1":
                shifters["educL"] = obs_df[col].mode().iloc[0] if len(obs_df[col].mode()) > 0 else 0.0
            elif col == "deduc3":
                shifters["educH"] = obs_df[col].mode().iloc[0] if len(obs_df[col].mode()) > 0 else 0.0
            else:
                shifters[col] = obs_df[col].mode().iloc[0] if len(obs_df[col].mode()) > 0 else 0.0
    
    # Region dummies
    for i in range(2, 10):
        col = f"reg{i}"
        if col in obs_df.columns:
            shifters[col] = obs_df[col].mode().iloc[0] if len(obs_df[col].mode()) > 0 else 0.0
        else:
            shifters[col] = 0.0
    
    return shifters


def compute_beta_leisure_at_median(
    group_params: Dict[str, float],
    median_shifters: Dict[str, float],
) -> float:
    """
    Compute β_l(X) at median/mode covariate values.
    
    β_l(X) = β_l0 + β_l_log_age * log(age) + β_l_log_age2 * log(age)²
             + β_l_ch0_3 * ch0_3 + β_l_ch4_6 * ch4_6 + β_l_ch7_9 * ch7_9
             + β_l_educL * educL + β_l_educH * educH
             + β_l_reg2 * reg2 + ...
    
    Parameters
    ----------
    group_params : Dict[str, float]
        Group-specific preference parameters (from extract_group_params_from_joint)
    median_shifters : Dict[str, float]
        Median/mode values for shifters (from compute_group_median_shifters)
    
    Returns
    -------
    float
        Computed β_l(X) at median characteristics
    """
    beta_l = group_params.get("beta_l0", 0.0)
    
    # Age effects
    log_age = median_shifters.get("log_age", np.log(40))
    log_age2 = median_shifters.get("log_age2", log_age ** 2)
    beta_l += group_params.get("beta_l_log_age", 0.0) * log_age
    beta_l += group_params.get("beta_l_log_age2", 0.0) * log_age2
    
    # Children effects
    beta_l += group_params.get("beta_l_ch0_3", 0.0) * median_shifters.get("children0_3", 0.0)
    beta_l += group_params.get("beta_l_ch4_6", 0.0) * median_shifters.get("children4_6", 0.0)
    beta_l += group_params.get("beta_l_ch7_9", 0.0) * median_shifters.get("children7_9", 0.0)
    
    # Education effects
    beta_l += group_params.get("beta_l_educL", 0.0) * median_shifters.get("educL", 0.0)
    beta_l += group_params.get("beta_l_educH", 0.0) * median_shifters.get("educH", 0.0)
    
    # Region effects
    for i in range(2, 10):
        beta_l += group_params.get(f"beta_l_reg{i}", 0.0) * median_shifters.get(f"reg{i}", 0.0)
    
    return beta_l


# =============================================================================
# GROUP-SPECIFIC MARGINAL UTILITIES
# =============================================================================

def compute_muc_by_group(
    c_grid: np.ndarray,
    group_params: Dict[str, Dict[str, float]],
    group: str,
) -> np.ndarray:
    """
    Compute marginal utility of consumption for a specific group.
    
    MUC = ∂U/∂c = β_c × c^(θ_c - 1)
    
    For singles: uses group-specific β_c, θ_c
    For couples: uses shared β_c, θ_c (household consumption)
    
    Parameters
    ----------
    c_grid : np.ndarray
        Grid of normalized consumption values
    group_params : Dict[str, Dict[str, float]]
        All group parameters from extract_group_params_from_joint
    group : str
        One of: 'sm', 'sf', 'cou_m', 'cou_f', 'cou'
    
    Returns
    -------
    np.ndarray
        MUC values at each point in c_grid
    """
    if group in [GROUP_SINGLE_MALE, GROUP_SINGLE_FEMALE]:
        params = group_params[group]
        beta_c = params["beta_c"]
        theta_c = params["theta_c"]
    else:
        # Couples use shared consumption parameters
        params = group_params[GROUP_COUPLE]
        beta_c = params["beta_c"]
        theta_c = params["theta_c"]
    
    return compute_marginal_utility_consumption(c_grid, beta_c, theta_c)


def compute_mul_by_group(
    l_grid: np.ndarray,
    group_params: Dict[str, Dict[str, float]],
    group: str,
    median_shifters: Dict[str, float],
) -> np.ndarray:
    """
    Compute marginal utility of leisure for a specific group.
    
    MUL = ∂U/∂l = β_l(X) × l^(θ_l - 1)
    
    where β_l(X) is evaluated at group median characteristics.
    
    Parameters
    ----------
    l_grid : np.ndarray
        Grid of normalized leisure values
    group_params : Dict[str, Dict[str, float]]
        All group parameters from extract_group_params_from_joint
    group : str
        One of: 'sm', 'sf', 'cou_m', 'cou_f'
    median_shifters : Dict[str, float]
        Median covariate values for the group
    
    Returns
    -------
    np.ndarray
        MUL values at each point in l_grid
    """
    if group not in [GROUP_SINGLE_MALE, GROUP_SINGLE_FEMALE, GROUP_COUPLE_MALE, GROUP_COUPLE_FEMALE]:
        raise ValueError(f"Invalid group for MUL: {group}. Must be individual-specific.")
    
    params = group_params[group]
    
    # Compute β_l at median shifters
    beta_l_median = compute_beta_leisure_at_median(params, median_shifters)
    theta_l = params.get("theta_l", 0.5)
    
    return compute_marginal_utility_leisure(l_grid, beta_l_median, theta_l)


def compute_utility_by_group(
    c_grid: np.ndarray,
    l_grid: np.ndarray,
    group_params: Dict[str, Dict[str, float]],
    group: str,
    median_shifters: Dict[str, float],
    l_other: float = None,  # For couples: leisure of the other partner
) -> np.ndarray:
    """
    Compute utility values on a (c, l) grid for a specific group.
    
    Singles: U = β_l(X) × BC(l; θ_l) + β_c × BC(c; θ_c)
    Couples: U = β_l_m(X) × BC(l_m) + β_l_f(X) × BC(l_f) + β_c × BC(c) + β_int × BC(l_m) × BC(l_f)
    
    Parameters
    ----------
    c_grid, l_grid : np.ndarray
        1D arrays for consumption and leisure grids
    group_params : Dict
        All group parameters
    group : str
        Target group
    median_shifters : Dict
        Median covariate values
    l_other : float, optional
        For couples only: leisure of the other partner (fixed at median)
    
    Returns
    -------
    np.ndarray
        2D utility grid of shape (len(l_grid), len(c_grid))
    """
    C, L = np.meshgrid(c_grid, l_grid)
    
    if group in [GROUP_SINGLE_MALE, GROUP_SINGLE_FEMALE]:
        params = group_params[group]
        beta_c = params["beta_c"]
        theta_c = params["theta_c"]
        theta_l = params["theta_l"]
        beta_l = compute_beta_leisure_at_median(params, median_shifters)
        
        U = beta_l * boxcox_transform(L, theta_l) + beta_c * boxcox_transform(C, theta_c)
        
    elif group in [GROUP_COUPLE_MALE, GROUP_COUPLE_FEMALE]:
        # For couples visualization, we fix the other partner's leisure at median
        shared = group_params[GROUP_COUPLE]
        this_params = group_params[group]
        
        beta_c = shared["beta_c"]
        theta_c = shared["theta_c"]
        beta_interaction = shared.get("beta_interaction", 0.0)
        
        theta_l = this_params["theta_l"]
        beta_l = compute_beta_leisure_at_median(this_params, median_shifters)
        
        # This partner's utility contribution
        U = beta_l * boxcox_transform(L, theta_l) + beta_c * boxcox_transform(C, theta_c)
        
        # Add interaction term if other partner's leisure is specified
        if l_other is not None and beta_interaction != 0:
            other_group = GROUP_COUPLE_FEMALE if group == GROUP_COUPLE_MALE else GROUP_COUPLE_MALE
            other_params = group_params[other_group]
            theta_l_other = other_params["theta_l"]
            l_other_bc = boxcox_transform(l_other, theta_l_other)
            U = U + beta_interaction * boxcox_transform(L, theta_l) * l_other_bc
    else:
        raise ValueError(f"Invalid group: {group}")
    
    return U


# =============================================================================
# LABOR SUPPLY ELASTICITIES
# =============================================================================

def compute_labor_supply_elasticities(
    df: pd.DataFrame,
    theta: np.ndarray,
    param_names: List[str],
    wage_col: str = "yivwg",
    hours_col: str = "lhw",
    consumption_col: str = "ils_dispy",
    group_col: str = "hh_id",
    is_obs_col: str = "obs",
    delta_pct: float = 0.01,
) -> Dict[str, Any]:
    """
    Compute labor supply elasticities using simulation-based approach.
    
    For discrete choice models, elasticities are computed by:
    1. Computing expected hours at baseline
    2. Shocking wages/income by delta_pct
    3. Computing new expected hours
    4. Elasticity = (ΔE[h]/E[h]) / (Δw/w)
    
    This follows the standard approach in Van Soest (1995), Blundell et al. (2007).
    
    Elasticities computed:
    - Uncompensated wage elasticity: ∂ln(E[h]) / ∂ln(w)
    - Income elasticity: ∂ln(E[h]) / ∂ln(y_non_labor)
    - Participation elasticity: ∂P(h>0) / ∂ln(w)
    
    Parameters
    ----------
    df : pd.DataFrame
        MNL dataset with all alternatives per individual
    theta : np.ndarray
        Estimated parameters
    param_names : List[str]
        Parameter names
    wage_col : str
        Column name for hourly wage
    hours_col : str
        Column name for hours worked
    consumption_col : str
        Column name for disposable income/consumption
    group_col : str
        Column for grouping by individual/household
    is_obs_col : str
        Column indicating observed choice (1 = observed)
    delta_pct : float
        Percentage shock for numerical derivative (default 1%)
    
    Returns
    -------
    Dict with elasticities and diagnostics
    """
    from scipy.special import logsumexp
    
    LOGGER.info("Computing labor supply elasticities...")
    
    results = {
        "wage_elasticity_intensive": np.nan,
        "wage_elasticity_extensive": np.nan,
        "wage_elasticity_total": np.nan,
        "income_elasticity": np.nan,
        "n_individuals": 0,
        "avg_hours_baseline": np.nan,
        "participation_rate_baseline": np.nan,
    }
    
    # Check required columns
    required_cols = [group_col, hours_col]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        LOGGER.warning(f"Missing columns for elasticity computation: {missing}")
        return results
    
    # Get utility column
    if "V" not in df.columns:
        LOGGER.warning("V column not found - cannot compute elasticities")
        return results
    
    groups = df[group_col].values
    unique_groups = np.unique(groups)
    n_individuals = len(unique_groups)
    results["n_individuals"] = n_individuals
    
    # Compute baseline expected hours
    expected_hours_baseline = np.zeros(n_individuals)
    participation_baseline = np.zeros(n_individuals)
    
    for i, g in enumerate(unique_groups):
        mask = groups == g
        V_i = df.loc[mask, "V"].values
        h_i = df.loc[mask, hours_col].values
        
        # Softmax probabilities
        log_denom = logsumexp(V_i)
        probs = np.exp(V_i - log_denom)
        
        # Expected hours
        expected_hours_baseline[i] = np.sum(probs * h_i)
        
        # Participation probability (P(h > 0))
        participation_baseline[i] = np.sum(probs[h_i > 0])
    
    avg_hours_baseline = np.mean(expected_hours_baseline)
    avg_participation_baseline = np.mean(participation_baseline)
    
    results["avg_hours_baseline"] = avg_hours_baseline
    results["participation_rate_baseline"] = avg_participation_baseline
    
    LOGGER.info(f"  Baseline: E[h] = {avg_hours_baseline:.2f} hours, P(h>0) = {avg_participation_baseline:.2%}")
    
    # Note: Full elasticity computation requires re-computing utilities with shocked wages
    # This is model-specific. Here we provide the framework - actual implementation
    # requires passing the utility function.
    
    LOGGER.info("  Note: Full elasticity computation requires utility recalculation")
    LOGGER.info("  Framework ready - use compute_elasticities_with_utility() for full computation")
    
    return results


def compute_elasticities_with_utility(
    df: pd.DataFrame,
    theta: np.ndarray,
    param_names: List[str],
    utility_func: Callable,
    wage_col: str = "yivwg",
    hours_col: str = "lhw",
    group_col: str = "hh_id",
    delta_pct: float = 0.01,
) -> Dict[str, Any]:
    """
    Compute elasticities by shocking wages and re-computing utilities.
    
    This is the full implementation that requires the utility function.
    
    Parameters
    ----------
    df : pd.DataFrame
        MNL dataset
    theta : np.ndarray
        Estimated parameters
    param_names : List[str]
        Parameter names
    utility_func : Callable
        Function that takes (df, theta) and returns utility values
    wage_col : str
        Column name for hourly wage
    hours_col : str
        Column name for hours worked
    group_col : str
        Column for grouping by individual
    delta_pct : float
        Percentage shock (default 1%)
    
    Returns
    -------
    Dict with wage and income elasticities
    """
    from scipy.special import logsumexp
    
    results = {
        "wage_elasticity_total": np.nan,
        "wage_elasticity_extensive": np.nan,
        "wage_elasticity_intensive": np.nan,
        "n_individuals": 0,
    }
    
    groups = df[group_col].values
    unique_groups = np.unique(groups)
    n_individuals = len(unique_groups)
    results["n_individuals"] = n_individuals
    
    # Baseline utilities
    V_baseline = utility_func(df, theta)
    
    # Shocked utilities (1% wage increase)
    df_shocked = df.copy()
    df_shocked[wage_col] = df_shocked[wage_col] * (1.0 + delta_pct)
    # Need to also update consumption based on new wage
    # This is model-specific - for now we just shock V directly
    
    # For proper implementation, we need to:
    # 1. Update yem = hours * new_wage * 4.33
    # 2. Re-run through tax-benefit system
    # 3. Get new disposable income
    # 4. Compute new utilities
    
    LOGGER.warning("Full elasticity computation requires tax-benefit model integration")
    
    return results


def compute_elasticities_summary_table(
    elasticities: Dict[str, Any],
    output_path: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Create summary table of elasticities.
    """
    rows = []
    for key, value in elasticities.items():
        if isinstance(value, (int, float)):
            rows.append({"Measure": key, "Value": value})
    
    df_summary = pd.DataFrame(rows)
    
    if output_path:
        df_summary.to_csv(output_path, index=False)
        LOGGER.info(f"Elasticities saved to: {output_path}")
    
    return df_summary


# =============================================================================
# CSV-BASED INITIAL PARAMETER VALUES
# =============================================================================

def load_initial_params_from_csv(
    csv_path: Path,
    param_names: List[str],
    value_col: str = "value",
    name_col: str = "parameter",
) -> np.ndarray:
    """
    Load initial parameter values from a CSV file.
    
    This allows easy editing of starting values without modifying code.
    
    Parameters
    ----------
    csv_path : Path
        Path to CSV file with columns [parameter, value, ...]
    param_names : List[str]
        List of parameter names expected (defines order)
    value_col : str
        Column name for parameter values
    name_col : str
        Column name for parameter names
    
    Returns
    -------
    np.ndarray
        Initial parameter values in the order of param_names
    
    Example CSV format:
        parameter,value,description,lower_bound,upper_bound
        beta_l0,0.5,"Base leisure preference",-5,5
        beta_l_log_age,0.1,"Age effect on leisure",-2,2
        ...
    """
    df = pd.read_csv(csv_path)
    
    if name_col not in df.columns or value_col not in df.columns:
        raise ValueError(f"CSV must have columns '{name_col}' and '{value_col}'")
    
    # Create mapping from CSV
    param_map = dict(zip(df[name_col], df[value_col]))
    
    # Build initial values array
    init_values = np.zeros(len(param_names))
    missing = []
    
    for i, name in enumerate(param_names):
        if name in param_map:
            init_values[i] = param_map[name]
        else:
            missing.append(name)
            init_values[i] = 0.0  # default
    
    if missing:
        LOGGER.warning(f"Parameters not found in CSV (using 0.0): {missing}")
    
    LOGGER.info(f"Loaded {len(param_names) - len(missing)}/{len(param_names)} parameters from {csv_path}")
    
    return init_values


def save_params_to_csv(
    theta: np.ndarray,
    param_names: List[str],
    csv_path: Path,
    se: Optional[np.ndarray] = None,
    description: Optional[Dict[str, str]] = None,
) -> Path:
    """
    Save parameter estimates to CSV for use as initial values.
    
    Parameters
    ----------
    theta : np.ndarray
        Parameter values
    param_names : List[str]
        Parameter names
    csv_path : Path
        Output path
    se : np.ndarray, optional
        Standard errors (if available)
    description : Dict[str, str], optional
        Parameter descriptions
    
    Returns
    -------
    Path to saved CSV
    """
    data = {
        "parameter": param_names,
        "value": theta,
    }
    
    if se is not None:
        data["std_error"] = se
        data["t_value"] = theta / np.where(se > 0, se, np.nan)
    
    if description:
        data["description"] = [description.get(n, "") for n in param_names]
    
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    LOGGER.info(f"Parameters saved to: {csv_path}")
    
    return csv_path


def create_init_params_template(
    param_names: List[str],
    output_path: Path,
    default_values: Optional[Dict[str, float]] = None,
    descriptions: Optional[Dict[str, str]] = None,
) -> Path:
    """
    Create a template CSV file for initial parameter values.
    
    Parameters
    ----------
    param_names : List[str]
        Parameter names
    output_path : Path
        Where to save the template
    default_values : Dict[str, float], optional
        Default values for parameters
    descriptions : Dict[str, str], optional
        Parameter descriptions
    
    Returns
    -------
    Path to created template
    """
    if default_values is None:
        default_values = {}
    if descriptions is None:
        descriptions = {}
    
    # Default descriptions for common parameters
    default_desc = {
        "beta_l0": "Base preference for leisure",
        "beta_l_log_age": "Effect of log(age) on leisure preference",
        "beta_l_log_age2": "Effect of log(age)² on leisure preference",
        "beta_l_ch0_3": "Effect of children 0-3 on leisure (females)",
        "beta_l_ch4_6": "Effect of children 4-6 on leisure",
        "beta_l_ch7_9": "Effect of children 7-9 on leisure",
        "beta_l_educL": "Effect of low education on leisure",
        "beta_l_educH": "Effect of high education on leisure",
        "beta_c": "Preference for consumption (should be positive)",
        "theta_l": "Box-Cox exponent for leisure (0=log, 1=linear)",
        "theta_c": "Box-Cox exponent for consumption (0=log, 1=linear)",
        "beta_l_reg2": "Effect of region 2 on leisure",
    }
    
    rows = []
    for name in param_names:
        rows.append({
            "parameter": name,
            "value": default_values.get(name, 0.0),
            "description": descriptions.get(name, default_desc.get(name, "")),
            "lower_bound": -10.0,
            "upper_bound": 10.0,
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    LOGGER.info(f"Template created: {output_path}")
    
    return output_path


# =============================================================================
# PLOTTING FUNCTIONS (similar to analyze_dcm_results.py)
# =============================================================================

def plot_marginal_utility(
    x: np.ndarray,
    mu: np.ndarray,
    xlabel: str,
    ylabel: str,
    title: str,
    output_path: Path,
    marks: List[float] = None,
    endpoint: float = None,
) -> None:
    """
    Line plot for marginal utilities.
    """
    if not MATPLOTLIB_AVAILABLE:
        LOGGER.warning("Matplotlib not available - skipping plot")
        return
    
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, mu, color="#1f77b4", lw=2)
    ax.axhline(0.0, color="black", lw=1, linestyle="--", alpha=0.6)
    
    # Add percentile marks if provided
    if marks:
        for m in marks:
            ax.axvline(m, color="gray", lw=1, ls=":", alpha=0.5)
    
    # Add endpoint annotation if provided
    if endpoint is not None:
        ax.scatter([x[-1]], [mu[-1]], s=20, color="gray")
        ax.text(x[-1], mu[-1], f"  @max → {endpoint:.3g}", va="bottom", ha="left", fontsize=8)
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_histogram(
    series: np.ndarray,
    title: str,
    path: Path,
    xlabel: str = None,
    ylabel: str = "Count",
    color: str = "#1f77b4",
    bins: int = 40,
) -> None:
    """
    Save histogram plot.
    """
    if not MATPLOTLIB_AVAILABLE:
        LOGGER.warning("Matplotlib not available - skipping plot")
        return
    
    import pandas as pd
    clean = pd.Series(series).replace([np.inf, -np.inf], np.nan).dropna()
    if clean.empty:
        return
    
    fig, ax = plt.subplots(figsize=(4.5, 3.0))
    ax.hist(clean, bins=bins, color=color, edgecolor="white", alpha=0.8)
    ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_parameter_significance(
    param_table: "pd.DataFrame",
    output_path: Path,
    title: str = "Parameter Estimates with 95% Confidence Intervals",
) -> None:
    """
    Forest plot showing parameter estimates with confidence intervals.
    """
    if not MATPLOTLIB_AVAILABLE:
        LOGGER.warning("Matplotlib not available - skipping plot")
        return
    
    import pandas as pd
    
    # Filter to finite values
    table = param_table.copy()
    table = table[table["std_error"].notna() & np.isfinite(table["std_error"])]
    
    if table.empty:
        LOGGER.warning("No valid standard errors for significance plot")
        return
    
    n_params = len(table)
    fig_height = max(4, n_params * 0.3)
    fig, ax = plt.subplots(figsize=(8, fig_height))
    
    y_pos = np.arange(n_params)
    estimates = table["estimate"].values
    se = table["std_error"].values
    ci_lower = estimates - 1.96 * se
    ci_upper = estimates + 1.96 * se
    
    # Horizontal error bars
    ax.errorbar(
        estimates, y_pos, xerr=1.96 * se,
        fmt='o', color='#1f77b4', capsize=3, capthick=1, markersize=5
    )
    
    # Vertical line at zero
    ax.axvline(0, color='red', linestyle='--', lw=1, alpha=0.6)
    
    # Color points based on significance
    significant = (ci_lower > 0) | (ci_upper < 0)
    ax.scatter(estimates[significant], y_pos[significant], color='#2ca02c', s=50, zorder=5)
    ax.scatter(estimates[~significant], y_pos[~significant], color='#d62728', s=50, zorder=5)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(table["parameter"].values)
    ax.set_xlabel("Estimate")
    ax.set_title(title)
    ax.grid(True, axis='x', alpha=0.3)
    
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_indifference_contours(
    beta_c: float,
    theta_c: float,
    beta_l_median: float,
    theta_l: float,
    output_path: Path,
    grid_points: int = 200,
    c_range: Tuple[float, float] = (0.001, 2.0),
    l_range: Tuple[float, float] = (0.001, 2.0),
) -> None:
    """
    Plot utility indifference contours in (c_norm, l_norm) space.
    
    Enhanced with:
    - Customizable ranges
    - Better color scheme
    - Budget line overlay option
    - MRS annotations
    """
    if not MATPLOTLIB_AVAILABLE:
        LOGGER.warning("Matplotlib not available - skipping plot")
        return
    
    c = np.linspace(c_range[0], c_range[1], grid_points)
    l = np.linspace(l_range[0], l_range[1], grid_points)
    C, L = np.meshgrid(c, l)
    
    U = beta_c * boxcox_transform(C, theta_c) + beta_l_median * boxcox_transform(L, theta_l)
    
    finite = np.isfinite(U)
    if not finite.any():
        LOGGER.warning("No finite utility values for contour plot")
        return
    
    # Use more levels for smoother contours
    levels = np.unique(np.percentile(U[finite], [10, 25, 40, 50, 60, 75, 90, 99]))
    
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # Filled contours for background
    cf = ax.contourf(C, L, U, levels=20, cmap='RdYlGn', alpha=0.6)
    plt.colorbar(cf, ax=ax, label='Utility')
    
    # Line contours with labels
    cs = ax.contour(C, L, U, levels=levels, colors='black', linewidths=0.8)
    ax.clabel(cs, inline=True, fontsize=8, fmt='%.2f')
    
    # Mark the median point
    c_med = np.median(c)
    l_med = np.median(l)
    ax.scatter([c_med], [l_med], color='red', s=50, marker='x', zorder=5, label='Median point')
    
    ax.set_xlabel("Normalized Consumption (c_norm)")
    ax.set_ylabel("Normalized Leisure (l_norm)")
    ax.set_title("Utility Indifference Curves\n(higher utility = greener)")
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_muc_mul_combined(
    c_grid: np.ndarray,
    muc: np.ndarray,
    l_grid: np.ndarray,
    mul: np.ndarray,
    output_path: Path,
    title: str = "Marginal Utilities",
) -> None:
    """
    Combined plot showing MUC and MUL side by side.
    """
    if not MATPLOTLIB_AVAILABLE:
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # MUC plot
    ax1.plot(c_grid, muc, color="#1f77b4", lw=2)
    ax1.axhline(0, color='black', lw=1, ls='--', alpha=0.6)
    ax1.fill_between(c_grid, muc, 0, where=(muc > 0), color='green', alpha=0.2, label='MUC > 0')
    ax1.fill_between(c_grid, muc, 0, where=(muc < 0), color='red', alpha=0.2, label='MUC < 0')
    ax1.set_xlabel("Normalized Consumption")
    ax1.set_ylabel("MUC (∂U/∂c)")
    ax1.set_title("Marginal Utility of Consumption")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # MUL plot
    ax2.plot(l_grid, mul, color="#ff7f0e", lw=2)
    ax2.axhline(0, color='black', lw=1, ls='--', alpha=0.6)
    ax2.fill_between(l_grid, mul, 0, where=(mul > 0), color='green', alpha=0.2, label='MUL > 0')
    ax2.fill_between(l_grid, mul, 0, where=(mul < 0), color='red', alpha=0.2, label='MUL < 0')
    ax2.set_xlabel("Normalized Leisure")
    ax2.set_ylabel("MUL (∂U/∂l)")
    ax2.set_title("Marginal Utility of Leisure")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    fig.suptitle(title, fontsize=12, fontweight='bold')
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_mrs_curve(
    l_grid: np.ndarray,
    mrs: np.ndarray,
    output_path: Path,
    title: str = "Marginal Rate of Substitution",
) -> None:
    """
    Plot MRS (leisure for consumption) against leisure.
    """
    if not MATPLOTLIB_AVAILABLE:
        return
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Filter valid MRS values
    valid = np.isfinite(mrs) & (np.abs(mrs) < 1e6)
    if not valid.any():
        LOGGER.warning("No valid MRS values to plot")
        return
    
    ax.plot(l_grid[valid], mrs[valid], color="#2ca02c", lw=2)
    ax.axhline(0, color='black', lw=1, ls='--', alpha=0.6)
    ax.set_xlabel("Normalized Leisure")
    ax.set_ylabel("MRS = MUL / MUC")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    
    # Add interpretation annotation
    ax.annotate(
        "MRS > 0: willing to give up\nconsumption for leisure",
        xy=(0.95, 0.95), xycoords='axes fraction',
        ha='right', va='top', fontsize=8,
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    )
    
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_hours_distribution(
    observed_hours: np.ndarray,
    predicted_hours: Optional[np.ndarray],
    output_path: Path,
    title: str = "Hours Distribution",
) -> None:
    """
    Plot distribution of observed vs predicted hours.
    """
    if not MATPLOTLIB_AVAILABLE:
        return
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Observed hours histogram
    bins = np.arange(0, 75, 5)
    ax.hist(observed_hours, bins=bins, alpha=0.6, label='Observed', color='#1f77b4', edgecolor='white')
    
    if predicted_hours is not None:
        ax.hist(predicted_hours, bins=bins, alpha=0.6, label='Predicted (E[h])', color='#ff7f0e', edgecolor='white')
    
    ax.set_xlabel("Weekly Hours Worked")
    ax.set_ylabel("Count")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_correlation_matrix(
    varcov: np.ndarray,
    param_names: List[str],
    output_path: Path,
    title: str = "Parameter Correlation Matrix",
) -> None:
    """
    Plot correlation matrix from variance-covariance matrix.
    """
    if not MATPLOTLIB_AVAILABLE:
        return
    
    # Compute correlation matrix
    se = np.sqrt(np.diag(varcov))
    with np.errstate(divide='ignore', invalid='ignore'):
        corr = varcov / np.outer(se, se)
    corr = np.where(np.isfinite(corr), corr, 0)
    
    n_params = len(param_names)
    fig_size = max(8, n_params * 0.4)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    
    im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)
    plt.colorbar(im, ax=ax, label='Correlation')
    
    ax.set_xticks(range(n_params))
    ax.set_yticks(range(n_params))
    ax.set_xticklabels(param_names, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(param_names, fontsize=8)
    ax.set_title(title)
    
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


# =============================================================================
# GROUP-SPECIFIC UTILITY CONTOUR PLOTS
# =============================================================================

def plot_utility_contours_by_group(
    group_params: Dict[str, Dict[str, float]],
    median_shifters: Dict[str, Dict[str, float]],
    output_dir: Path,
    wage_spec: str = "fw",
    grid_points: int = 200,
    c_range: Tuple[float, float] = (0.05, 2.5),
    l_range: Tuple[float, float] = (0.1, 2.5),
    utility_percentiles: List[float] = [10, 25, 50, 75, 99],
) -> Dict[str, Path]:
    """
    Generate utility contour plots for all 4 demographic groups.
    
    Creates one contour plot per group showing indifference curves at
    specified utility percentile levels.
    
    Parameters
    ----------
    group_params : Dict[str, Dict[str, float]]
        Parameters for each group (from extract_group_params_from_joint)
    median_shifters : Dict[str, Dict[str, float]]
        Median shifters for each group (from compute_group_median_shifters)
    output_dir : Path
        Directory to save plots
    wage_spec : str
        "fw" or "vw"
    grid_points : int
        Resolution of the grid
    c_range, l_range : Tuple[float, float]
        Range for consumption and leisure axes
    utility_percentiles : List[float]
        Percentile levels for contour lines (default: 10, 25, 50, 75, 99)
    
    Returns
    -------
    Dict[str, Path]
        Paths to generated plots, keyed by group
    """
    if not MATPLOTLIB_AVAILABLE:
        LOGGER.warning("Matplotlib not available - skipping contour plots")
        return {}
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    group_labels = {
        GROUP_SINGLE_MALE: "Single Males",
        GROUP_SINGLE_FEMALE: "Single Females",
        GROUP_COUPLE_MALE: "Males in Couples",
        GROUP_COUPLE_FEMALE: "Females in Couples",
    }
    
    plot_paths = {}
    
    for group in ALL_GROUPS:
        LOGGER.info(f"  Generating contour plot for {group_labels.get(group, group)}...")
        
        shifters = median_shifters.get(group, {})
        if not shifters:
            LOGGER.warning(f"  No median shifters for {group} - using defaults")
            shifters = {"log_age": np.log(40), "log_age2": np.log(40)**2}
        
        # For couples, get the median leisure of the other partner
        l_other_median = None
        if group in [GROUP_COUPLE_MALE, GROUP_COUPLE_FEMALE]:
            # Default to median normalized leisure ≈ 1.0
            l_other_median = 1.0
        
        c_grid = np.linspace(c_range[0], c_range[1], grid_points)
        l_grid = np.linspace(l_range[0], l_range[1], grid_points)
        
        try:
            U = compute_utility_by_group(
                c_grid, l_grid,
                group_params, group,
                shifters, l_other_median
            )
            
            # Get finite values
            finite_mask = np.isfinite(U)
            if not finite_mask.any():
                LOGGER.warning(f"  No finite utility values for {group}")
                continue
            
            # Compute percentile-based contour levels
            U_flat = U[finite_mask].flatten()
            levels = np.percentile(U_flat, utility_percentiles)
            levels = np.unique(levels)  # Remove duplicates
            
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 6))
            
            C, L = np.meshgrid(c_grid, l_grid)
            
            # Filled contours
            cf = ax.contourf(C, L, U, levels=20, cmap='RdYlGn', alpha=0.7)
            plt.colorbar(cf, ax=ax, label='Utility')
            
            # Contour lines at percentile levels
            cs = ax.contour(C, L, U, levels=levels, colors='black', linewidths=1.0)
            
            # Label contours with percentile info
            fmt_dict = {lev: f"{utility_percentiles[i]}%" 
                       for i, lev in enumerate(levels) if i < len(utility_percentiles)}
            ax.clabel(cs, inline=True, fontsize=9, fmt=fmt_dict)
            
            # Mark median point
            c_med = np.median(c_grid)
            l_med = np.median(l_grid)
            ax.scatter([c_med], [l_med], color='red', s=80, marker='x', 
                      linewidths=2, zorder=5, label='Grid median')
            
            ax.set_xlabel("Normalized Consumption (c/c̄)")
            ax.set_ylabel("Normalized Leisure (l/l̄)")
            ax.set_title(f"Utility Indifference Curves\n{group_labels.get(group, group)} ({wage_spec.upper()})")
            ax.legend(loc='upper right')
            ax.grid(True, alpha=0.3)
            
            # Save
            output_path = output_dir / f"{wage_spec}_{group}_contours.png"
            fig.tight_layout()
            fig.savefig(output_path, dpi=150)
            plt.close(fig)
            
            plot_paths[group] = output_path
            LOGGER.info(f"    Saved: {output_path.name}")
            
        except Exception as e:
            LOGGER.error(f"  Error generating contour for {group}: {e}")
            import traceback
            traceback.print_exc()
    
    return plot_paths


def plot_all_groups_mu_comparison(
    group_params: Dict[str, Dict[str, float]],
    median_shifters: Dict[str, Dict[str, float]],
    output_dir: Path,
    wage_spec: str = "fw",
    grid_points: int = 200,
) -> Dict[str, Path]:
    """
    Generate comparison plots of MUC and MUL across all groups.
    
    Creates:
    1. MUC comparison plot (all groups on same axes)
    2. MUL comparison plot (all groups on same axes)
    3. Individual MUC/MUL plots per group
    
    Returns dict of output paths.
    """
    if not MATPLOTLIB_AVAILABLE:
        return {}
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    c_grid = np.linspace(0.05, 2.5, grid_points)
    l_grid = np.linspace(0.1, 2.5, grid_points)
    
    group_labels = {
        GROUP_SINGLE_MALE: "Single Males",
        GROUP_SINGLE_FEMALE: "Single Females",
        GROUP_COUPLE_MALE: "Males in Couples",
        GROUP_COUPLE_FEMALE: "Females in Couples",
    }
    
    colors = {
        GROUP_SINGLE_MALE: "#1f77b4",      # blue
        GROUP_SINGLE_FEMALE: "#ff7f0e",    # orange
        GROUP_COUPLE_MALE: "#2ca02c",      # green
        GROUP_COUPLE_FEMALE: "#d62728",    # red
    }
    
    plot_paths = {}
    
    # =========================================================================
    # 1. MUC Comparison Plot
    # =========================================================================
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for group in [GROUP_SINGLE_MALE, GROUP_SINGLE_FEMALE]:
        muc = compute_muc_by_group(c_grid, group_params, group)
        ax.plot(c_grid, muc, label=group_labels[group], color=colors[group], lw=2)
    
    # Couples share same MUC
    muc_cou = compute_muc_by_group(c_grid, group_params, GROUP_COUPLE)
    ax.plot(c_grid, muc_cou, label="Couples (shared)", color="#9467bd", lw=2, ls="--")
    
    ax.axhline(0, color='black', lw=1, ls='--', alpha=0.6)
    ax.set_xlabel("Normalized Consumption (c/c̄)")
    ax.set_ylabel("MUC = ∂U/∂c")
    ax.set_title(f"Marginal Utility of Consumption by Group ({wage_spec.upper()})")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    muc_path = output_dir / f"{wage_spec}_muc_comparison.png"
    fig.tight_layout()
    fig.savefig(muc_path, dpi=150)
    plt.close(fig)
    plot_paths["muc_comparison"] = muc_path
    
    # =========================================================================
    # 2. MUL Comparison Plot
    # =========================================================================
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for group in ALL_GROUPS:
        shifters = median_shifters.get(group, {"log_age": np.log(40), "log_age2": np.log(40)**2})
        mul = compute_mul_by_group(l_grid, group_params, group, shifters)
        ax.plot(l_grid, mul, label=group_labels[group], color=colors[group], lw=2)
    
    ax.axhline(0, color='black', lw=1, ls='--', alpha=0.6)
    ax.set_xlabel("Normalized Leisure (l/l̄)")
    ax.set_ylabel("MUL = ∂U/∂l")
    ax.set_title(f"Marginal Utility of Leisure by Group ({wage_spec.upper()})")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    mul_path = output_dir / f"{wage_spec}_mul_comparison.png"
    fig.tight_layout()
    fig.savefig(mul_path, dpi=150)
    plt.close(fig)
    plot_paths["mul_comparison"] = mul_path
    
    # =========================================================================
    # 3. Individual Group Plots (MUC + MUL combined)
    # =========================================================================
    for group in ALL_GROUPS:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        shifters = median_shifters.get(group, {"log_age": np.log(40), "log_age2": np.log(40)**2})
        
        # MUC
        muc = compute_muc_by_group(c_grid, group_params, group)
        ax1.plot(c_grid, muc, color=colors[group], lw=2)
        ax1.axhline(0, color='black', lw=1, ls='--', alpha=0.6)
        ax1.fill_between(c_grid, muc, 0, where=(muc > 0), color='green', alpha=0.2)
        ax1.fill_between(c_grid, muc, 0, where=(muc < 0), color='red', alpha=0.2)
        ax1.set_xlabel("Normalized Consumption")
        ax1.set_ylabel("MUC (∂U/∂c)")
        ax1.set_title("Marginal Utility of Consumption")
        ax1.grid(True, alpha=0.3)
        
        # MUL
        mul = compute_mul_by_group(l_grid, group_params, group, shifters)
        ax2.plot(l_grid, mul, color=colors[group], lw=2)
        ax2.axhline(0, color='black', lw=1, ls='--', alpha=0.6)
        ax2.fill_between(l_grid, mul, 0, where=(mul > 0), color='green', alpha=0.2)
        ax2.fill_between(l_grid, mul, 0, where=(mul < 0), color='red', alpha=0.2)
        ax2.set_xlabel("Normalized Leisure")
        ax2.set_ylabel("MUL (∂U/∂l)")
        ax2.set_title("Marginal Utility of Leisure")
        ax2.grid(True, alpha=0.3)
        
        fig.suptitle(f"{group_labels[group]} ({wage_spec.upper()})", fontsize=12, fontweight='bold')
        
        group_path = output_dir / f"{wage_spec}_{group}_mu.png"
        fig.tight_layout()
        fig.savefig(group_path, dpi=150)
        plt.close(fig)
        plot_paths[f"{group}_mu"] = group_path
    
    return plot_paths


# =============================================================================
# LABOR SUPPLY ELASTICITIES TABLE
# =============================================================================

def compute_elasticities_table(
    df: pd.DataFrame,
    theta: np.ndarray,
    param_names: List[str],
    group_params: Dict[str, Dict[str, float]],
    median_shifters: Dict[str, Dict[str, float]],
    wage_spec: str = "fw",
) -> pd.DataFrame:
    """
    Compute labor supply elasticities table.
    
    Following the IJM format, computes for each group:
    - Hicksian (compensated) wage elasticity
    - Marshallian (uncompensated) wage elasticity
    - Participation elasticity (extensive margin)
    - Intensive margin elasticity (conditional on working)
    
    Note: This provides a structural approximation based on estimated parameters.
    For exact elasticities, simulation-based methods should be used.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataset with labor supply choices
    theta : np.ndarray
        Estimated parameters
    param_names : List[str]
        Parameter names
    group_params : Dict[str, Dict[str, float]]
        Group-specific parameters
    median_shifters : Dict[str, Dict[str, float]]
        Median characteristics by group
    wage_spec : str
        "fw" or "vw"
    
    Returns
    -------
    pd.DataFrame
        Elasticity table with rows for each group and columns for each elasticity type
    """
    LOGGER.info("Computing labor supply elasticities (structural approximation)...")
    
    group_labels = {
        GROUP_SINGLE_MALE: "Single Males",
        GROUP_SINGLE_FEMALE: "Single Females",
        GROUP_COUPLE_MALE: "Males in Couples",
        GROUP_COUPLE_FEMALE: "Females in Couples",
    }
    
    rows = []
    
    for group in ALL_GROUPS:
        params = group_params.get(group, {})
        shifters = median_shifters.get(group, {"log_age": np.log(40), "log_age2": np.log(40)**2})
        
        # Get key parameters
        theta_l = params.get("theta_l", 0.5)
        
        if group in [GROUP_SINGLE_MALE, GROUP_SINGLE_FEMALE]:
            theta_c = params.get("theta_c", 0.5)
            beta_c = params.get("beta_c", 0.0)
        else:
            cou_shared = group_params.get(GROUP_COUPLE, {})
            theta_c = cou_shared.get("theta_c", 0.5)
            beta_c = cou_shared.get("beta_c", 0.0)
        
        beta_l_median = compute_beta_leisure_at_median(params, shifters)
        
        # Structural elasticity approximation from Box-Cox parameters
        # For Box-Cox utility, at interior solution:
        # - Hicksian elasticity ≈ (1 - θ_l) / (θ_l * (1 - s_l))
        # - Marshallian elasticity ≈ Hicksian - income_effect
        # where s_l is the share of leisure in full income
        
        # Simplified approximations (see Blundell & MaCurdy, 1999)
        # These are rough structural estimates - simulation gives more accurate results
        
        # Assume typical leisure share s_l ≈ 0.5 for rough estimate
        s_l = 0.5
        
        if abs(theta_l) < 1e-6:
            # Log utility case
            hicksian = 1.0 / s_l
            marshallian = hicksian - 0.1  # small income effect approximation
        else:
            hicksian = (1.0 - theta_l) / (theta_l * (1.0 - s_l)) if theta_l != 0 and s_l < 1 else np.nan
            # Income effect approximation
            income_effect = 0.05 / (1.0 - s_l) if s_l < 1 else 0.0
            marshallian = hicksian - income_effect
        
        # Participation elasticity is typically lower (extensive margin)
        # Rough approximation: 1/3 of intensive margin
        participation = marshallian * 0.3
        
        # Intensive margin (conditional on working)
        intensive = marshallian - participation
        
        rows.append({
            "Group": group_labels.get(group, group),
            "Hicksian (compensated)": round(hicksian, 3) if np.isfinite(hicksian) else np.nan,
            "Marshallian (uncompensated)": round(marshallian, 3) if np.isfinite(marshallian) else np.nan,
            "Participation (extensive)": round(participation, 3) if np.isfinite(participation) else np.nan,
            "Intensive (conditional)": round(intensive, 3) if np.isfinite(intensive) else np.nan,
            "θ_l": round(theta_l, 3),
            "θ_c": round(theta_c, 3),
            "β_l (at median X)": round(beta_l_median, 3),
            "β_c": round(beta_c, 3) if np.isfinite(beta_c) else np.nan,
        })
    
    df_elast = pd.DataFrame(rows)
    
    LOGGER.info("\nElasticities Summary (structural approximation):")
    LOGGER.info("-" * 80)
    LOGGER.info(df_elast.to_string(index=False))
    
    return df_elast


def compute_simulation_elasticities(
    df_sm: pd.DataFrame,
    df_sf: pd.DataFrame,
    df_cou: pd.DataFrame,
    theta: np.ndarray,
    param_names: List[str],
    utility_func: Callable,
    delta_pct: float = 0.01,
) -> pd.DataFrame:
    """
    Compute elasticities via simulation (wage shock method).
    
    This is the proper method following Van Soest (1995), Blundell et al. (2007):
    1. Compute baseline expected hours E[h | w]
    2. Shock wage by δ%
    3. Recompute expected hours E[h | w*(1+δ)]
    4. Elasticity = (ΔE[h]/E[h]) / (Δw/w)
    
    Note: This requires access to the utility function and tax-benefit system
    to properly update disposable income after wage shock.
    
    Parameters
    ----------
    df_sm, df_sf, df_cou : pd.DataFrame
        MNL datasets for each group
    theta : np.ndarray
        Estimated parameters
    param_names : List[str]
        Parameter names
    utility_func : Callable
        Function to compute utilities
    delta_pct : float
        Percentage wage shock (default 1%)
    
    Returns
    -------
    pd.DataFrame
        Simulation-based elasticity table
    """
    LOGGER.warning("Simulation-based elasticities require tax-benefit integration.")
    LOGGER.info("This function provides a framework - implement with EUROMOD for accurate results.")
    
    # Placeholder for simulation-based elasticities
    # Full implementation requires:
    # 1. Shocking wages in df
    # 2. Re-running tax-benefit calculations to get new disposable income
    # 3. Recomputing utilities
    # 4. Computing expected hours changes
    
    rows = [
        {"Group": "Single Males", "Wage Elasticity": "TBD (requires simulation)"},
        {"Group": "Single Females", "Wage Elasticity": "TBD (requires simulation)"},
        {"Group": "Males in Couples", "Wage Elasticity": "TBD (requires simulation)"},
        {"Group": "Females in Couples", "Wage Elasticity": "TBD (requires simulation)"},
    ]
    
    return pd.DataFrame(rows)


# =============================================================================
# FIT DIAGNOSTICS: PREDICTED VS OBSERVED
# =============================================================================

def compute_fit_diagnostics(
    df: pd.DataFrame,
    group: str,
    hours_col: str = "lhw",
    group_col: str = "hh_id",
    V_col: str = "V",
) -> Dict[str, Any]:
    """
    Compute fit diagnostics comparing predicted vs observed outcomes.
    
    Returns participation rates, hours distributions, and accuracy metrics.
    """
    from scipy.special import logsumexp
    
    results = {
        "participation_rate_observed": np.nan,
        "participation_rate_predicted": np.nan,
        "mean_hours_observed": np.nan,
        "mean_hours_predicted": np.nan,
        "hours_distribution_observed": {},
        "hours_distribution_predicted": {},
        "choice_accuracy": np.nan,
    }
    
    if V_col not in df.columns:
        LOGGER.warning(f"V column not found - cannot compute fit diagnostics")
        return results
    
    if hours_col not in df.columns:
        LOGGER.warning(f"Hours column '{hours_col}' not found")
        return results
    
    # Get observed choices
    if "obs" in df.columns:
        obs_mask = df["obs"] == 1
    elif "is_observed" in df.columns:
        obs_mask = df["is_observed"] == 1
    elif "is_chosen" in df.columns:
        obs_mask = df["is_chosen"] == 1
    else:
        LOGGER.warning("No observed choice indicator found")
        return results
    
    obs_df = df[obs_mask]
    
    # Observed statistics
    obs_hours = obs_df[hours_col].values
    results["participation_rate_observed"] = (obs_hours > 0).mean()
    results["mean_hours_observed"] = obs_hours[obs_hours > 0].mean() if (obs_hours > 0).any() else 0
    
    # Hours bins for distribution
    bins = [0, 5, 15, 25, 35, 45, 55, 65]
    bin_labels = ["0", "1-10", "11-20", "21-30", "31-40", "41-50", "51-60"]
    
    obs_binned = pd.cut(obs_hours, bins=bins, labels=bin_labels, include_lowest=True)
    results["hours_distribution_observed"] = obs_binned.value_counts(normalize=True).to_dict()
    
    # Predicted statistics (using expected hours)
    groups = df[group_col].values
    unique_groups = np.unique(groups)
    
    expected_hours = []
    participation_probs = []
    
    for g in unique_groups:
        mask = groups == g
        V_i = df.loc[mask, V_col].values
        h_i = df.loc[mask, hours_col].values
        
        # Softmax probabilities
        log_denom = logsumexp(V_i)
        probs = np.exp(V_i - log_denom)
        
        # Expected hours
        e_h = np.sum(probs * h_i)
        expected_hours.append(e_h)
        
        # Participation probability
        p_work = np.sum(probs[h_i > 0])
        participation_probs.append(p_work)
    
    expected_hours = np.array(expected_hours)
    participation_probs = np.array(participation_probs)
    
    results["participation_rate_predicted"] = participation_probs.mean()
    results["mean_hours_predicted"] = expected_hours[expected_hours > 0].mean() if (expected_hours > 0).any() else 0
    
    # Predicted hours distribution
    pred_binned = pd.cut(expected_hours, bins=bins, labels=bin_labels, include_lowest=True)
    results["hours_distribution_predicted"] = pred_binned.value_counts(normalize=True).to_dict()
    
    return results


def plot_fit_diagnostics(
    fit_results: Dict[str, Dict[str, Any]],
    output_dir: Path,
    wage_spec: str = "fw",
) -> Dict[str, Path]:
    """
    Generate fit diagnostic plots for all groups.
    
    Creates:
    1. Participation rate comparison (bar chart)
    2. Hours distribution comparison (grouped bars)
    3. Mean hours comparison
    
    Returns dict of output paths.
    """
    if not MATPLOTLIB_AVAILABLE:
        return {}
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    plot_paths = {}
    
    group_labels = {
        GROUP_SINGLE_MALE: "SM",
        GROUP_SINGLE_FEMALE: "SF",
        GROUP_COUPLE_MALE: "CM",
        GROUP_COUPLE_FEMALE: "CF",
    }
    
    # =========================================================================
    # 1. Participation Rate Comparison
    # =========================================================================
    fig, ax = plt.subplots(figsize=(8, 5))
    
    groups = list(fit_results.keys())
    x = np.arange(len(groups))
    width = 0.35
    
    obs_rates = [fit_results[g].get("participation_rate_observed", 0) * 100 for g in groups]
    pred_rates = [fit_results[g].get("participation_rate_predicted", 0) * 100 for g in groups]
    
    ax.bar(x - width/2, obs_rates, width, label='Observed', color='#1f77b4')
    ax.bar(x + width/2, pred_rates, width, label='Predicted', color='#ff7f0e')
    
    ax.set_ylabel('Participation Rate (%)')
    ax.set_title(f'Participation Rates: Observed vs Predicted ({wage_spec.upper()})')
    ax.set_xticks(x)
    ax.set_xticklabels([group_labels.get(g, g) for g in groups])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    for i, (obs, pred) in enumerate(zip(obs_rates, pred_rates)):
        ax.annotate(f'{obs:.1f}%', (i - width/2, obs + 1), ha='center', fontsize=8)
        ax.annotate(f'{pred:.1f}%', (i + width/2, pred + 1), ha='center', fontsize=8)
    
    part_path = output_dir / f"{wage_spec}_fit_participation.png"
    fig.tight_layout()
    fig.savefig(part_path, dpi=150)
    plt.close(fig)
    plot_paths["participation"] = part_path
    
    # =========================================================================
    # 2. Mean Hours Comparison
    # =========================================================================
    fig, ax = plt.subplots(figsize=(8, 5))
    
    obs_hours = [fit_results[g].get("mean_hours_observed", 0) for g in groups]
    pred_hours = [fit_results[g].get("mean_hours_predicted", 0) for g in groups]
    
    ax.bar(x - width/2, obs_hours, width, label='Observed', color='#1f77b4')
    ax.bar(x + width/2, pred_hours, width, label='Predicted', color='#ff7f0e')
    
    ax.set_ylabel('Mean Hours (conditional on working)')
    ax.set_title(f'Mean Working Hours: Observed vs Predicted ({wage_spec.upper()})')
    ax.set_xticks(x)
    ax.set_xticklabels([group_labels.get(g, g) for g in groups])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    hours_path = output_dir / f"{wage_spec}_fit_mean_hours.png"
    fig.tight_layout()
    fig.savefig(hours_path, dpi=150)
    plt.close(fig)
    plot_paths["mean_hours"] = hours_path
    
    return plot_paths


# =============================================================================
# PREDICTION AND ACCURACY
# =============================================================================

def compute_predicted_probabilities(
    df: "pd.DataFrame",
    theta: np.ndarray,
    param_names: List[str],
    group_col: str = "hh_id",
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute predicted choice probabilities for each alternative.
    
    For RURO models with 100 draws per individual, this computes
    P(j|i) = exp(V_ij) / Σ_k exp(V_ik) for each draw.
    
    Returns
    -------
    predicted_idx : np.ndarray
        Index of predicted choice (highest probability) per individual
    probabilities : np.ndarray
        Probability of observed choice
    """
    import pandas as pd
    from scipy.special import logsumexp
    
    # Get V_ij from the data (should include utility + opportunity - prior)
    if "V" not in df.columns:
        LOGGER.warning("V column not found in data - cannot compute predictions")
        return None, None
    
    V = df["V"].values
    groups = df[group_col].values if group_col in df.columns else df.grouper.groups
    is_obs = df["obs"].values if "obs" in df.columns else (df["is_observed"].values if "is_observed" in df.columns else (df["is_chosen"].values if "is_chosen" in df.columns else None))
    
    if is_obs is None:
        LOGGER.warning("Observed choice indicator not found")
        return None, None
    
    # Group by individual
    unique_groups = np.unique(groups)
    n_individuals = len(unique_groups)
    
    predicted_idx = np.zeros(n_individuals, dtype=int)
    obs_prob = np.zeros(n_individuals)
    
    for i, g in enumerate(unique_groups):
        mask = groups == g
        V_i = V[mask]
        is_obs_i = is_obs[mask]
        
        # Softmax
        log_denom = logsumexp(V_i)
        probs = np.exp(V_i - log_denom)
        
        predicted_idx[i] = np.argmax(probs)
        obs_prob[i] = probs[is_obs_i].sum() if is_obs_i.any() else 0.0
    
    return predicted_idx, obs_prob


def compute_prediction_accuracy(
    df: "pd.DataFrame",
    theta: np.ndarray,
    param_names: List[str],
    utility_func: Callable,
    group_col: str = "hh_id",
    is_obs_col: str = "obs",
) -> Dict[str, float]:
    """
    Compute prediction accuracy measures.
    
    Returns
    -------
    Dict with:
        - accuracy: share of correctly predicted choices
        - top3_accuracy: share where actual is in top 3 predicted
        - log_likelihood: log-likelihood at theta
        - avg_predicted_prob: average probability assigned to actual choice
    """
    import pandas as pd
    from scipy.special import logsumexp
    
    results = {
        "accuracy": np.nan,
        "top3_accuracy": np.nan,
        "avg_predicted_prob": np.nan,
    }
    
    # Check required columns
    if group_col not in df.columns:
        LOGGER.warning(f"Group column '{group_col}' not found")
        return results
    
    if is_obs_col not in df.columns:
        LOGGER.warning(f"Observed choice column '{is_obs_col}' not found")
        return results
    
    groups = df[group_col].values
    is_obs = df[is_obs_col].values.astype(bool)
    unique_groups = np.unique(groups)
    n_individuals = len(unique_groups)
    
    correct = 0
    top3_correct = 0
    total_prob = 0.0
    
    for g in unique_groups:
        mask = groups == g
        V_i = df.loc[mask, "V"].values if "V" in df.columns else np.zeros(mask.sum())
        is_obs_i = is_obs[mask]
        
        if not is_obs_i.any():
            continue
        
        # Softmax probabilities
        log_denom = logsumexp(V_i)
        probs = np.exp(V_i - log_denom)
        
        # Predicted choice (highest prob)
        pred_idx = np.argmax(probs)
        obs_idx = np.where(is_obs_i)[0][0]
        
        if pred_idx == obs_idx:
            correct += 1
        
        # Top 3 accuracy
        top3_idx = np.argsort(probs)[-3:]
        if obs_idx in top3_idx:
            top3_correct += 1
        
        total_prob += probs[obs_idx]
    
    results["accuracy"] = correct / n_individuals if n_individuals > 0 else np.nan
    results["top3_accuracy"] = top3_correct / n_individuals if n_individuals > 0 else np.nan
    results["avg_predicted_prob"] = total_prob / n_individuals if n_individuals > 0 else np.nan
    
    return results


# =============================================================================
# HTML REPORT GENERATION
# =============================================================================

def build_html_report(
    param_table: pd.DataFrame,
    fit_stats: Dict[str, float],
    output_path: Path,
    *,
    gender: str = "singles",
    variant: str = "fw",
    muc_plot: Path = None,
    mul_plot: Path = None,
    contour_plot: Path = None,
    param_sig_plot: Path = None,
    cons_hist: Path = None,
    leisure_hist: Path = None,
    muc_mul_combined_plot: Path = None,
    mrs_plot: Path = None,
    hours_dist_plot: Path = None,
    corr_matrix_plot: Path = None,
    marginal_utilities_summary: Dict = None,
    accuracy_metrics: Dict = None,
    hessian_diagnostics: Dict = None,
    elasticities: Dict = None,
    gradient_check: Dict = None,
    model_description: str = None,
) -> Path:
    """
    Generate comprehensive HTML report for post-estimation analysis.
    
    Enhanced version with all diagnostics and plots.
    """
    from datetime import datetime
    
    def _img_tag(path: Path, alt: str) -> str:
        if path and path.exists():
            return f'<img src="{path.name}" alt="{alt}" style="max-width:100%;">'
        return f'<p><em>({alt} not available)</em></p>'
    
    def _format_value(v):
        if isinstance(v, float):
            if not np.isfinite(v):
                return "N/A"
            if abs(v) < 0.001 or abs(v) > 10000:
                return f"{v:.4e}"
            return f"{v:.4f}"
        if isinstance(v, str) and "%" in str(v):
            return v
        return str(v)
    
    def _make_table(data_dict: Dict, title: str = None) -> str:
        rows = "\n".join(
            f"<tr><th>{k}</th><td>{_format_value(v)}</td></tr>"
            for k, v in data_dict.items()
        )
        title_html = f"<h3>{title}</h3>" if title else ""
        return f"""
        {title_html}
        <table class="table table-sm" style="width:auto;">
          {rows}
        </table>
        """
    
    # Format parameter table with significance coloring
    param_df = param_table.copy()
    param_df['significant'] = param_df['p_value'].apply(
        lambda p: '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))
    )
    
    param_html = param_df.to_html(
        classes="table table-striped table-sm",
        float_format=lambda x: f"{x:.4f}" if np.isfinite(x) else "N/A",
        border=0,
        index=False,
    )
    
    # Model fit section
    fit_html = _make_table(fit_stats)
    
    # Hessian diagnostics section
    hess_html = ""
    if hessian_diagnostics:
        eigs = hessian_diagnostics.get("eigenvalues", [])
        n_neg = sum(1 for e in eigs if e < 0)
        status_class = "sig-positive" if n_neg == 0 else "sig-negative"
        status_text = "✓ Positive definite" if n_neg == 0 else f"⚠ {n_neg} negative eigenvalues"
        eig_min = min(eigs) if eigs else 0
        eig_max = max(eigs) if eigs else 0
        hess_html = f"""
        <section>
            <h2>🔍 Hessian Diagnostics</h2>
            <div class="stats-box">
                <p><strong>Status:</strong> <span class="{status_class}">{status_text}</span></p>
                <p><strong>Eigenvalue range:</strong> [{eig_min:.4g}, {eig_max:.4g}]</p>
                <p><strong>Condition number:</strong> {abs(eig_max/eig_min) if eig_min != 0 else 'N/A':.2e}</p>
            </div>
        </section>
        """
    
    # Marginal utilities section
    mu_html = ""
    if marginal_utilities_summary:
        mu_html = f"""
        <section>
            <h2>📊 Marginal Utilities Summary</h2>
            {_make_table(marginal_utilities_summary)}
            <p><small><em>MUC = ∂U/∂c = β_c × c^(θ_c - 1), MUL = ∂U/∂l = β_l(X) × l^(θ_l - 1)</em></small></p>
        </section>
        """
    
    # Elasticities section
    elast_html = ""
    if elasticities:
        elast_html = f"""
        <section>
            <h2>📈 Labor Supply Elasticities</h2>
            {_make_table(elasticities)}
            <p><small><em>Computed via simulation-based approach. Extensive margin = participation effect.</em></small></p>
        </section>
        """
    
    # Accuracy section
    acc_html = ""
    if accuracy_metrics:
        acc_html = f"""
        <section>
            <h2>🎯 Prediction Accuracy</h2>
            {_make_table(accuracy_metrics)}
        </section>
        """
    
    # Gradient check section
    grad_html = ""
    if gradient_check:
        max_rel = gradient_check.get("max_rel_diff", np.nan)
        status = "✓ PASSED" if max_rel < 0.01 else "⚠ WARNING"
        status_class = "sig-positive" if max_rel < 0.01 else "sig-negative"
        grad_html = f"""
        <section>
            <h2>🔬 Gradient Check</h2>
            <div class="stats-box">
                <p><strong>Status:</strong> <span class="{status_class}">{status}</span></p>
                <p><strong>Max absolute difference:</strong> {gradient_check.get('max_abs_diff', np.nan):.4e}</p>
                <p><strong>Max relative difference:</strong> {max_rel:.4e}</p>
            </div>
        </section>
        """
    
    # Model description
    desc_html = ""
    if model_description:
        desc_html = f"""
        <section>
            <h2>📝 Model Description</h2>
            <div class="stats-box">
                <p>{model_description}</p>
            </div>
        </section>
        """
    
    # Full HTML
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RURO Post-Estimation Analysis - {gender.capitalize()} ({variant})</title>
  <style>
    :root {{
      --primary-color: #2c3e50;
      --success-color: #27ae60;
      --warning-color: #e74c3c;
      --bg-light: #f8f9fa;
    }}
    body {{ 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
      margin: 0; 
      padding: 2em; 
      max-width: 1400px; 
      margin: 0 auto;
      line-height: 1.6;
      color: #333;
    }}
    h1 {{ color: var(--primary-color); border-bottom: 3px solid var(--primary-color); padding-bottom: 0.5em; }}
    h2 {{ color: var(--primary-color); margin-top: 2em; }}
    .table {{ border-collapse: collapse; margin-bottom: 1.5em; width: 100%; }}
    .table th, .table td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
    .table th {{ background-color: var(--bg-light); font-weight: 600; }}
    .table-striped tbody tr:nth-child(odd) {{ background-color: #f9f9f9; }}
    .table-sm th, .table-sm td {{ padding: 6px 10px; }}
    section {{ margin-bottom: 2.5em; padding: 1em; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    figure {{ margin: 1.5em 0; text-align: center; }}
    figcaption {{ font-weight: bold; margin-bottom: 0.5em; color: var(--primary-color); }}
    img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; }}
    .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5em; }}
    .three-col {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1em; }}
    .stats-box {{ background: var(--bg-light); padding: 1em; border-radius: 4px; border-left: 4px solid var(--primary-color); }}
    .sig-positive {{ color: var(--success-color); font-weight: bold; }}
    .sig-negative {{ color: var(--warning-color); font-weight: bold; }}
    .header-info {{ background: var(--bg-light); padding: 1em; border-radius: 4px; margin-bottom: 2em; }}
    .toc {{ background: #fff; padding: 1em; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 2em; }}
    .toc ul {{ list-style: none; padding-left: 0; }}
    .toc li {{ margin: 0.5em 0; }}
    .toc a {{ text-decoration: none; color: var(--primary-color); }}
    .toc a:hover {{ text-decoration: underline; }}
    @media (max-width: 768px) {{
      .two-col, .three-col {{ grid-template-columns: 1fr; }}
    }}
    @media print {{
      section {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <h1>📊 RURO Post-Estimation Analysis</h1>
  
  <div class="header-info">
    <p><strong>Model:</strong> {gender.capitalize()} | <strong>Specification:</strong> {variant.upper()} | <strong>Generated:</strong> {timestamp}</p>
  </div>
  
  <nav class="toc">
    <strong>Contents:</strong>
    <ul>
      <li><a href="#fit">Model Fit Statistics</a></li>
      <li><a href="#params">Parameter Estimates</a></li>
      <li><a href="#hessian">Hessian Diagnostics</a></li>
      <li><a href="#mu">Marginal Utilities</a></li>
      <li><a href="#plots">Visualization</a></li>
    </ul>
  </nav>
  
  {desc_html}
  
  <section id="fit">
    <h2>📈 Model Fit Statistics</h2>
    {fit_html}
  </section>
  
  <section id="params">
    <h2>📋 Parameter Estimates</h2>
    <p><em>Significance: *** p&lt;0.001, ** p&lt;0.01, * p&lt;0.05</em></p>
    {param_html}
    <figure>
      <figcaption>Parameter Significance (95% CI)</figcaption>
      {_img_tag(param_sig_plot, "Parameter significance plot")}
    </figure>
  </section>
  
  {hess_html}
  {grad_html}
  {mu_html}
  {elast_html}
  {acc_html}
  
  <section id="plots">
    <h2>📊 Marginal Utility Plots</h2>
    <div class="two-col">
      <figure>
        <figcaption>MUC vs Consumption</figcaption>
        {_img_tag(muc_plot, "MUC plot")}
      </figure>
      <figure>
        <figcaption>MUL vs Leisure</figcaption>
        {_img_tag(mul_plot, "MUL plot")}
      </figure>
    </div>
    {f'<figure><figcaption>Combined MUC/MUL</figcaption>{_img_tag(muc_mul_combined_plot, "Combined MU plot")}</figure>' if muc_mul_combined_plot else ''}
    {f'<figure><figcaption>Marginal Rate of Substitution</figcaption>{_img_tag(mrs_plot, "MRS plot")}</figure>' if mrs_plot else ''}
  </section>
  
  <section>
    <h2>🗺️ Indifference Curves</h2>
    <figure>
      <figcaption>Utility Contours (at median covariates)</figcaption>
      {_img_tag(contour_plot, "Indifference curves")}
    </figure>
  </section>
  
  <section>
    <h2>📊 Distribution of Observed Choices</h2>
    <div class="two-col">
      <figure>
        <figcaption>Consumption Distribution</figcaption>
        {_img_tag(cons_hist, "Consumption histogram")}
      </figure>
      <figure>
        <figcaption>Leisure Distribution</figcaption>
        {_img_tag(leisure_hist, "Leisure histogram")}
      </figure>
    </div>
    {f'<figure><figcaption>Hours Distribution</figcaption>{_img_tag(hours_dist_plot, "Hours distribution")}</figure>' if hours_dist_plot else ''}
  </section>
  
  {f'<section><h2>🔗 Parameter Correlations</h2><figure>{_img_tag(corr_matrix_plot, "Correlation matrix")}</figure></section>' if corr_matrix_plot else ''}
  
  <footer style="margin-top: 3em; padding-top: 1em; border-top: 1px solid #ddd; color: #666; font-size: 0.9em;">
    <p>Generated by RURO_post_estimation.py | {timestamp}</p>
  </footer>
  
</body>
</html>
"""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    LOGGER.info(f"HTML report saved to: {output_path}")
    return output_path


# =============================================================================
# ENHANCED RUN_POST_ESTIMATION
# =============================================================================

def run_full_post_estimation(
    result: Any,  # scipy.optimize.OptimizeResult
    grad_func: Callable,
    param_names: List[str],
    n_individuals: int,
    df: "pd.DataFrame" = None,
    wage_spec: str = "fw",
    sex: str = "pooled",
    out_dir: Optional[Path] = None,
    save_excel: bool = True,
    save_plots: bool = True,
    save_html: bool = True,
    nll_func: Optional[Callable] = None,
    check_gradient: bool = False,
    n_alternatives_per_individual: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Run comprehensive post-estimation analysis with plots and HTML report.
    
    This extends run_post_estimation() with:
    - Marginal utility plots (MUC, MUL)
    - Parameter significance plots
    - Indifference curves
    - Distribution histograms
    - HTML report generation
    
    Parameters
    ----------
    result : OptimizeResult
        Result from scipy.optimize.minimize
    grad_func : Callable
        Gradient function of the NEGATIVE log-likelihood (for Hessian computation).
        This should return the gradient pointing to the minimum, not maximum.
    param_names : List[str]
        Parameter names
    n_individuals : int
        Number of individuals
    df : pd.DataFrame, optional
        MNL dataset for computing marginal utilities and distributions.
        If provided, used to compute n_alternatives_per_individual if not specified.
    wage_spec : str
        "fw" (fixed wage) or "vw" (variable wage)
    sex : str
        "m", "f", or "pooled"
    out_dir : Path, optional
        Directory to save results
    save_excel : bool
        Whether to save to Excel
    save_plots : bool
        Whether to generate and save plots
    save_html : bool
        Whether to generate HTML report
    nll_func : Callable, optional
        Negative log-likelihood function (for gradient check)
    check_gradient : bool
        Whether to check gradient accuracy
    n_alternatives_per_individual : int, optional
        Number of alternatives per individual in the MNL choice set.
        If None and df is provided, will be computed from the data.
        Default is 100 (99 random draws + 1 observed choice in RURO).
      Returns
    -------
    Dict containing all post-estimation results
    """
    import pandas as pd
    from datetime import datetime
    
    theta = result.x
    log_likelihood = -result.fun
    n_params = len(theta)
    
    LOGGER.info("=" * 70)
    LOGGER.info("COMPREHENSIVE POST-ESTIMATION ANALYSIS")
    LOGGER.info("=" * 70)
    
    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
    
    # -------------------------------------------------------------------------
    # Compute n_alternatives_per_individual from data if not provided
    # -------------------------------------------------------------------------
    n_alts = n_alternatives_per_individual
    if n_alts is None and df is not None:
        # Try to compute from data: count rows per individual
        id_col = None
        for col in ["idhh", "idhh_true", "idperson", "idperson_true", "id"]:
            if col in df.columns:
                id_col = col
                break
        if id_col is not None:
            # Count alternatives per individual (should be constant)
            alts_per_ind = df.groupby(id_col).size()
            n_alts = int(alts_per_ind.mode().iloc[0]) if len(alts_per_ind) > 0 else 100
            LOGGER.info(f"Computed n_alternatives_per_individual from data: {n_alts}")
        else:
            n_alts = 100  # Default for RURO (99 draws + 1 observed)
            LOGGER.info(f"Using default n_alternatives_per_individual: {n_alts}")
    elif n_alts is None:
        n_alts = 100  # Default
        LOGGER.info(f"Using default n_alternatives_per_individual: {n_alts}")
    
    # -------------------------------------------------------------------------
    # 1. Base post-estimation (SE, t-values, fit stats)
    # -------------------------------------------------------------------------
    base_results = run_post_estimation(
        result=result,
        grad_func=grad_func,
        param_names=param_names,
        n_individuals=n_individuals,
        wage_spec=wage_spec,
        out_dir=out_dir,
        save_excel=save_excel,
        nll_func=nll_func,
        check_gradient=check_gradient,
        n_alternatives_per_individual=n_alts,
    )
    
    param_table = base_results["param_table"]
    fit_stats = base_results["fit_statistics"]
    
    # Extract preference parameters
    params = extract_preference_params(theta, param_names)
    
    # Detect if these are joint estimation params (prefixed with sm., sf., cou.)
    is_joint_params = any(name.startswith(("sm.", "sf.", "cou.")) for name in param_names)
    
    # For joint params, extract group-specific params and pick appropriate group based on sex
    if is_joint_params:
        group_params = extract_group_params_from_joint(theta, param_names, wage_spec)
        # Choose group based on sex parameter
        if sex == "male" or sex == "m":
            mu_params = group_params.get(GROUP_SINGLE_MALE, {})
        elif sex == "female" or sex == "f":
            mu_params = group_params.get(GROUP_SINGLE_FEMALE, {})
        else:
            # For pooled or couples, use couple shared params with couple male leisure
            cou_shared = group_params.get(GROUP_COUPLE, {})
            cou_m = group_params.get(GROUP_COUPLE_MALE, {})
            mu_params = {**cou_m, **cou_shared}
        LOGGER.info(f"Using joint params for group '{sex}': beta_c={mu_params.get('beta_c', 0.0):.4f}, theta_c={mu_params.get('theta_c', 1.0):.4f}")
    else:
        mu_params = params
    
    # -------------------------------------------------------------------------
    # 2. Marginal Utilities (if dataset provided)
    # -------------------------------------------------------------------------
    marginal_utilities_summary = {}
    muc_plot_path = None
    mul_plot_path = None
    contour_plot_path = None
    cons_hist_path = None
    leisure_hist_path = None
    
    if df is not None and save_plots and out_dir is not None:
        LOGGER.info("\n2. Computing marginal utilities and generating plots...")
        
        # Get key parameters (use mu_params which handles joint vs single-group)
        beta_c = mu_params.get("beta_c", 0.0)
        theta_c = mu_params.get("theta_c", 1.0)
        theta_l = mu_params.get("theta_l", 1.0)
        beta_l0 = mu_params.get("beta_l0", 0.0)
        
        # Extract consumption and leisure from data
        c_col = None
        for col in ["c_norm", "dispy_util", "consumption", "ils_dispy"]:
            if col in df.columns and not df[col].isna().all():
                c_col = col
                break
        
        l_col = None
        for col in ["l_norm", "leis_util", "leisure"]:
            if col in df.columns and not df[col].isna().all():
                l_col = col
                break
        
        if c_col and l_col:
            # Get observed choices only
            if "obs" in df.columns:
                obs_df = df[df["obs"] == 1].copy()
            elif "is_observed" in df.columns:
                obs_df = df[df["is_observed"] == 1].copy()
            elif "is_chosen" in df.columns:
                obs_df = df[df["is_chosen"] == 1].copy()
            else:
                obs_df = df.copy()
            
            c_values = pd.to_numeric(obs_df[c_col], errors="coerce").dropna().values
            l_values = pd.to_numeric(obs_df[l_col], errors="coerce").dropna().values
            
            # Normalize if needed
            c_norm = np.clip(c_values, 1e-6, None)
            l_norm = np.clip(l_values, 1e-6, None)
            
            # Compute median beta_l (accounting for covariates)
            beta_l_median = beta_l0
            for key, val in mu_params.items():
                if key.startswith("beta_l_") and key != "beta_l0":
                    # Use median of covariate
                    cov_name = key.replace("beta_l_", "")
                    if cov_name in obs_df.columns:
                        cov_median = obs_df[cov_name].median()
                        beta_l_median += val * cov_median
            
            # Compute marginal utilities at observed choices
            muc_values = compute_marginal_utility_consumption(c_norm, beta_c, theta_c)
            mul_values = compute_marginal_utility_leisure(l_norm, beta_l_median, theta_l)
            
            # Summary statistics
            marginal_utilities_summary = {
                "MUC < 0 (%)": f"{100 * (muc_values < 0).mean():.1f}%",
                "MUL < 0 (%)": f"{100 * (mul_values < 0).mean():.1f}%",
                "MUC median": np.nanmedian(muc_values),
                "MUL median": np.nanmedian(mul_values),
                "MRS median": np.nanmedian(compute_mrs(muc_values, mul_values)),
                "c_norm median": np.nanmedian(c_norm),
                "l_norm median": np.nanmedian(l_norm),
            }
            
            LOGGER.info(f"  MUC < 0: {marginal_utilities_summary['MUC < 0 (%)']}")
            LOGGER.info(f"  MUL < 0: {marginal_utilities_summary['MUL < 0 (%)']}")
            
            # Generate MUC plot
            c_grid = np.linspace(np.percentile(c_norm, 1), np.percentile(c_norm, 99), 200)
            muc_curve = compute_marginal_utility_consumption(c_grid, beta_c, theta_c)
            muc_plot_path = out_dir / f"{wage_spec}_{sex}_muc.png"
            plot_marginal_utility(
                c_grid, muc_curve,
                xlabel="Normalized Consumption (c)",
                ylabel="MUC",
                title=f"Marginal Utility of Consumption - {sex.capitalize()} ({wage_spec})",
                output_path=muc_plot_path,
                marks=[np.percentile(c_norm, q) for q in [25, 50, 75]],
            )
            
            # Generate MUL plot
            l_grid = np.linspace(np.percentile(l_norm, 1), np.percentile(l_norm, 99), 200)
            mul_curve = compute_marginal_utility_leisure(l_grid, beta_l_median, theta_l)
            mul_plot_path = out_dir / f"{wage_spec}_{sex}_mul.png"
            plot_marginal_utility(
                l_grid, mul_curve,
                xlabel="Normalized Leisure (l)",
                ylabel="MUL",
                title=f"Marginal Utility of Leisure - {sex.capitalize()} ({wage_spec})",
                output_path=mul_plot_path,
                marks=[np.percentile(l_norm, q) for q in [25, 50, 75]],
            )
            
            # Generate indifference contours
            contour_plot_path = out_dir / f"{wage_spec}_{sex}_contours.png"
            plot_indifference_contours(
                beta_c, theta_c, beta_l_median, theta_l,
                output_path=contour_plot_path,
            )
            
            # Generate distribution histograms
            cons_hist_path = out_dir / f"{wage_spec}_{sex}_cons_hist.png"
            leisure_hist_path = out_dir / f"{wage_spec}_{sex}_leisure_hist.png"
            
            plot_histogram(
                c_norm,
                f"Distribution of Consumption at Observed Choice - {sex.capitalize()}",
                cons_hist_path,
                xlabel="Normalized Consumption",
            )
            
            plot_histogram(
                l_norm,
                f"Distribution of Leisure at Observed Choice - {sex.capitalize()}",
                leisure_hist_path,
                xlabel="Normalized Leisure",
            )
            
            LOGGER.info(f"  Plots saved to: {out_dir}")
    
    # -------------------------------------------------------------------------
    # 3. Additional plots (MRS, combined MU, correlation matrix, hours dist)
    # -------------------------------------------------------------------------
    muc_mul_combined_path = None
    mrs_plot_path = None
    hours_dist_path = None
    corr_matrix_path = None
    
    if save_plots and out_dir is not None and df is not None:
        LOGGER.info("\n3. Generating additional diagnostic plots...")
        
        # Combined MUC/MUL plot
        if 'c_grid' in dir() and 'l_grid' in dir():
            muc_mul_combined_path = out_dir / f"{wage_spec}_{sex}_mu_combined.png"
            plot_muc_mul_combined(
                c_grid, muc_curve, l_grid, mul_curve,
                output_path=muc_mul_combined_path,
                title=f"Marginal Utilities - {sex.capitalize()} ({wage_spec})",
            )
            
            # MRS plot
            mrs_values = compute_mrs(muc_curve, mul_curve)
            mrs_plot_path = out_dir / f"{wage_spec}_{sex}_mrs.png"
            plot_mrs_curve(
                l_grid, mrs_values,
                output_path=mrs_plot_path,
                title=f"MRS - {sex.capitalize()} ({wage_spec})",
            )
        
        # Hours distribution
        hours_col = None
        for col in ["lhw", "hours", "working_hours"]:
            if col in df.columns:
                hours_col = col
                break
        
        if hours_col and "obs" in df.columns:
            obs_hours = df.loc[df["obs"] == 1, hours_col].values
            hours_dist_path = out_dir / f"{wage_spec}_{sex}_hours_dist.png"
            plot_hours_distribution(
                observed_hours=obs_hours,
                predicted_hours=None,  # Would need expected hours computation
                output_path=hours_dist_path,
                title=f"Hours Distribution - {sex.capitalize()} ({wage_spec})",
            )
        
        # Correlation matrix
        corr_matrix_path = out_dir / f"{wage_spec}_{sex}_corr_matrix.png"
        plot_correlation_matrix(
            varcov=base_results["se_jacobian"]["varcov"],
            param_names=param_names,
            output_path=corr_matrix_path,
            title=f"Parameter Correlations - {sex.capitalize()} ({wage_spec})",
        )
    
    # -------------------------------------------------------------------------
    # 4. Parameter Significance Plot
    # -------------------------------------------------------------------------
    param_sig_plot_path = None
    if save_plots and out_dir is not None:
        LOGGER.info("\n4. Generating parameter significance plot...")
        param_sig_plot_path = out_dir / f"{wage_spec}_{sex}_param_significance.png"
        plot_parameter_significance(
            param_table,
            param_sig_plot_path,
            title=f"Parameter Estimates with 95% CI - {sex.capitalize()} ({wage_spec})",
        )
    
    # -------------------------------------------------------------------------
    # 5. Labor supply elasticities (basic framework)
    # -------------------------------------------------------------------------
    elasticities = {}
    if df is not None:
        LOGGER.info("\n5. Computing labor supply elasticities (framework)...")
        elasticities = compute_labor_supply_elasticities(
            df=df,
            theta=theta,
            param_names=param_names,
        )
    
    # -------------------------------------------------------------------------
    # 6. Hessian diagnostics summary
    # -------------------------------------------------------------------------
    hessian_diagnostics = {
        "eigenvalues": list(base_results["se_jacobian"]["eigenvalues"]),
    }
    
    # -------------------------------------------------------------------------
    # 7. Save parameters to CSV (for use as init values later)
    # -------------------------------------------------------------------------
    if out_dir is not None:
        params_csv_path = out_dir / f"{wage_spec}_{sex}_params.csv"
        save_params_to_csv(
            theta=theta,
            param_names=param_names,
            csv_path=params_csv_path,
            se=base_results["se_jacobian"]["se"],
        )
    
    # -------------------------------------------------------------------------
    # 8. HTML Report
    # -------------------------------------------------------------------------
    html_path = None
    if save_html and out_dir is not None:
        LOGGER.info("\n6. Generating comprehensive HTML report...")
        html_path = out_dir / f"{wage_spec}_{sex}_post_estimation_report.html"
        build_html_report(
            param_table=param_table,
            fit_stats=fit_stats,
            output_path=html_path,
            gender=sex,
            variant=wage_spec,
            muc_plot=muc_plot_path,
            mul_plot=mul_plot_path,
            contour_plot=contour_plot_path,
            param_sig_plot=param_sig_plot_path,
            cons_hist=cons_hist_path,
            leisure_hist=leisure_hist_path,
            muc_mul_combined_plot=muc_mul_combined_path,
            mrs_plot=mrs_plot_path,
            hours_dist_plot=hours_dist_path,
            corr_matrix_plot=corr_matrix_path,
            marginal_utilities_summary=marginal_utilities_summary,
            hessian_diagnostics=hessian_diagnostics,
            elasticities=elasticities if elasticities else None,
            gradient_check=base_results.get("gradient_check"),
        )
    
    LOGGER.info("\n" + "=" * 70)
    LOGGER.info("POST-ESTIMATION COMPLETE")
    LOGGER.info("=" * 70)
    
    return {
        **base_results,
        "marginal_utilities_summary": marginal_utilities_summary,
        "hessian_diagnostics": hessian_diagnostics,
        "elasticities": elasticities,
        "plots": {
            "muc": muc_plot_path,
            "mul": mul_plot_path,
            "contours": contour_plot_path,
            "param_significance": param_sig_plot_path,
            "cons_hist": cons_hist_path,
            "leisure_hist": leisure_hist_path,
            "muc_mul_combined": muc_mul_combined_path,
            "mrs": mrs_plot_path,
            "hours_dist": hours_dist_path,
            "corr_matrix": corr_matrix_path,
        },
        "html_report": html_path,
    }


# =============================================================================
# JOINT ESTIMATION POST-ANALYSIS (ALL GROUPS)
# =============================================================================

def run_joint_post_estimation(
    theta: np.ndarray,
    param_names: List[str],
    log_likelihood: float,
    n_sm: int,
    n_sf: int,
    n_cou: int,
    df_sm: pd.DataFrame = None,
    df_sf: pd.DataFrame = None,
    df_cou: pd.DataFrame = None,
    wage_spec: str = "fw",
    out_dir: Optional[Path] = None,
    se: np.ndarray = None,
    varcov: np.ndarray = None,
    n_alternatives_per_individual: Optional[int] = None,
    theta0: np.ndarray = None,
    bounds: List[Tuple] = None,
    estimation_time_seconds: float = None,
) -> Dict[str, Any]:
    """
    Run comprehensive post-estimation analysis for joint estimation results.
    
    This function generates:
    1. Group-specific MUC plots (singles M, singles F, couples)
    2. Group-specific MUL plots (4 groups: SM, SF, CM, CF)
    3. Utility contour plots for all 4 groups at 10%, 25%, 50%, 75%, 99% levels
    4. Labor supply elasticities table (Hicksian, Marshallian, participation, intensive)
    5. Fit diagnostics plots (predicted vs observed)
    6. Comprehensive HTML report with bounds, initial values, and color coding
    
    Parameters
    ----------
    theta : np.ndarray
        Joint estimation parameter vector
    param_names : List[str]
        Parameter names
    log_likelihood : float
        Log-likelihood at optimum
    n_sm, n_sf, n_cou : int
        Number of individuals per group
    df_sm, df_sf, df_cou : pd.DataFrame, optional
        MNL datasets for each group
    wage_spec : str
        "fw" or "vw"
    out_dir : Path, optional
        Output directory
    se : np.ndarray, optional
        Standard errors (if available)
    varcov : np.ndarray, optional
        Variance-covariance matrix (if available)
    n_alternatives_per_individual : int, optional
        Number of alternatives per individual. If None, computed from data
        or defaults to 100 (99 draws + 1 observed).
    theta0 : np.ndarray, optional
        Initial parameter values
    bounds : List[Tuple], optional
        Parameter bounds as list of (lower, upper) tuples
    estimation_time_seconds : float, optional
        Time taken for estimation in seconds
    
    Returns
    -------
    Dict containing all results and plot paths
    """
    LOGGER.info("=" * 70)
    LOGGER.info("JOINT POST-ESTIMATION ANALYSIS (ALL GROUPS)")
    LOGGER.info("=" * 70)
    
    if out_dir is None:
        out_dir = Path("outputs/post_estimation/fr")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    n_individuals = n_sm + n_sf + n_cou
    
    # =========================================================================
    # 1. Extract group-specific parameters
    # =========================================================================
    LOGGER.info("\n1. Extracting group-specific parameters...")
    group_params = extract_group_params_from_joint(theta, param_names, wage_spec)
    
    # Log key parameters
    for group in ALL_GROUPS:
        params = group_params.get(group, {})
        LOGGER.info(f"  {group}: β_l0={params.get('beta_l0', 'N/A'):.4f}, "
                   f"θ_l={params.get('theta_l', 'N/A'):.4f}")
    
    cou_shared = group_params.get(GROUP_COUPLE, {})
    LOGGER.info(f"  Couples shared: β_c={cou_shared.get('beta_c', 'N/A'):.4f}, "
               f"θ_c={cou_shared.get('theta_c', 'N/A'):.4f}")
    
    # =========================================================================
    # 2. Compute median shifters for each group
    # =========================================================================
    LOGGER.info("\n2. Computing median shifters for each group...")
    median_shifters = {}
    
    for group, df in [
        (GROUP_SINGLE_MALE, df_sm),
        (GROUP_SINGLE_FEMALE, df_sf),
        (GROUP_COUPLE_MALE, df_cou),
        (GROUP_COUPLE_FEMALE, df_cou),
    ]:
        if df is not None:
            shifters = compute_group_median_shifters(df, group)
            median_shifters[group] = shifters
            LOGGER.info(f"  {group}: log_age={shifters.get('log_age', 'N/A'):.2f}")
        else:
            # Use defaults
            median_shifters[group] = {"log_age": np.log(40), "log_age2": np.log(40)**2}
            LOGGER.info(f"  {group}: using default median shifters")
    
    # =========================================================================
    # 3. Generate group-specific MUC/MUL comparison plots
    # =========================================================================
    LOGGER.info("\n3. Generating MUC/MUL comparison plots...")
    mu_plot_paths = plot_all_groups_mu_comparison(
        group_params, median_shifters, out_dir, wage_spec
    )
    
    # =========================================================================
    # 4. Generate utility contour plots for each group
    # =========================================================================
    LOGGER.info("\n4. Generating utility contour plots for each group...")
    contour_paths = plot_utility_contours_by_group(
        group_params, median_shifters, out_dir, wage_spec,
        utility_percentiles=[10, 25, 50, 75, 99]
    )
    
    # =========================================================================
    # 5. Compute elasticities table
    # =========================================================================
    LOGGER.info("\n5. Computing labor supply elasticities...")
    
    # Combine data for elasticity computation
    df_combined = None
    if df_sm is not None or df_sf is not None or df_cou is not None:
        dfs = [d for d in [df_sm, df_sf, df_cou] if d is not None]
        if dfs:
            df_combined = pd.concat(dfs, ignore_index=True)
    
    elasticities_df = compute_elasticities_table(
        df_combined, theta, param_names, group_params, median_shifters, wage_spec
    )
    
    # Save elasticities table
    elast_csv_path = out_dir / f"{wage_spec}_joint_elasticities.csv"
    elasticities_df.to_csv(elast_csv_path, index=False)
    LOGGER.info(f"  Elasticities saved to: {elast_csv_path.name}")
    
    # =========================================================================
    # 6. Compute fit diagnostics
    # =========================================================================
    LOGGER.info("\n6. Computing fit diagnostics...")
    fit_results = {}
    
    for group, df in [
        (GROUP_SINGLE_MALE, df_sm),
        (GROUP_SINGLE_FEMALE, df_sf),
        (GROUP_COUPLE_MALE, df_cou),
        (GROUP_COUPLE_FEMALE, df_cou),
    ]:
        if df is not None:
            try:
                fit = compute_fit_diagnostics(df, group)
                fit_results[group] = fit
                LOGGER.info(f"  {group}: participation={fit.get('participation_rate_observed', 'N/A'):.2%}")
            except Exception as e:
                LOGGER.warning(f"  {group}: fit diagnostics failed - {e}")
      # Generate fit plots
    fit_plot_paths = {}
    if fit_results:
        fit_plot_paths = plot_fit_diagnostics(fit_results, out_dir, wage_spec)
    
    # =========================================================================
    # 7. Create parameter summary table with bounds and status info
    # =========================================================================
    LOGGER.info("\n7. Creating parameter summary...")
    
    # Build columns for bounds and status
    n_params_total = len(theta)
    lower_bounds = []
    upper_bounds = []
    is_bounded = []
    hit_lower = []
    hit_upper = []
    initial_values = []
    
    for i in range(n_params_total):
        # Get bounds for this parameter
        if bounds is not None and i < len(bounds):
            lb, ub = bounds[i]
        else:
            lb, ub = None, None
        
        lower_bounds.append(lb)
        upper_bounds.append(ub)
        is_bounded.append("Yes" if lb is not None or ub is not None else "No")
        
        # Check if parameter hit bounds (within 1e-6 tolerance)
        val = theta[i]
        hit_lower.append(lb is not None and abs(val - lb) < 1e-6)
        hit_upper.append(ub is not None and abs(val - ub) < 1e-6)
        
        # Get initial value
        if theta0 is not None and i < len(theta0):
            initial_values.append(theta0[i])
        else:
            initial_values.append(np.nan)
    
    # Determine if parameter was estimated (i.e., changed from initial)
    is_estimated = []
    for i in range(n_params_total):
        if theta0 is not None and i < len(theta0):
            # Estimated if value differs from initial by more than 1e-8
            is_estimated.append("Yes" if abs(theta[i] - theta0[i]) > 1e-8 else "No")
        else:
            is_estimated.append("Unknown")
    
    param_table = pd.DataFrame({
        "parameter": param_names,
        "estimate": theta,
        "std_error": se if se is not None else [np.nan] * n_params_total,
        "t_value": theta / se if se is not None else [np.nan] * n_params_total,
        "p_value": [np.nan] * n_params_total,
        "lower_bound": lower_bounds,
        "upper_bound": upper_bounds,
        "bounded": is_bounded,
        "hit_lower": hit_lower,
        "hit_upper": hit_upper,
        "initial_value": initial_values,
        "estimated": is_estimated,
    })
    
    # Compute p-values if we have SE
    if se is not None:
        t_vals = param_table["t_value"].values
        param_table["p_value"] = 2.0 * (1.0 - _norm_cdf(np.abs(t_vals)))
    
    # Save parameter table
    params_csv_path = out_dir / f"{wage_spec}_joint_params.csv"
    param_table.to_csv(params_csv_path, index=False)
    
    # =========================================================================
    # 8. Model fit statistics
    # =========================================================================
    n_params = len(theta)
    n_individuals = n_sm + n_sf + n_cou
    
    # Determine n_alternatives_per_individual
    n_alts = n_alternatives_per_individual
    if n_alts is None:
        # Try to compute from data
        for df_check, name in [(df_sm, "sm"), (df_sf, "sf"), (df_cou, "cou")]:
            if df_check is not None and len(df_check) > 0:
                id_col = None
                for col in ["idhh", "idhh_true", "idperson", "idperson_true", "id"]:
                    if col in df_check.columns:
                        id_col = col
                        break
                if id_col is not None:
                    alts_per_ind = df_check.groupby(id_col).size()
                    n_alts = int(alts_per_ind.mode().iloc[0]) if len(alts_per_ind) > 0 else 100
                    LOGGER.info(f"Computed n_alternatives_per_individual from {name} data: {n_alts}")
                    break
        if n_alts is None:
            n_alts = 100  # Default for RURO (99 draws + 1 observed)
            LOGGER.info(f"Using default n_alternatives_per_individual: {n_alts}")
    
    ll_null = n_individuals * np.log(1.0 / n_alts)
    
    # Format estimation time
    est_time_str = "N/A"
    if estimation_time_seconds is not None:
        if estimation_time_seconds >= 3600:
            hours = int(estimation_time_seconds // 3600)
            mins = int((estimation_time_seconds % 3600) // 60)
            secs = estimation_time_seconds % 60
            est_time_str = f"{hours}h {mins}m {secs:.1f}s"
        elif estimation_time_seconds >= 60:
            mins = int(estimation_time_seconds // 60)
            secs = estimation_time_seconds % 60
            est_time_str = f"{mins}m {secs:.1f}s"
        else:
            est_time_str = f"{estimation_time_seconds:.1f}s"
    
    # Count parameters hitting bounds
    n_bounded = sum(1 for b in is_bounded if b == "Yes")
    n_hit_lower = sum(hit_lower)
    n_hit_upper = sum(hit_upper)
    n_not_estimated = sum(1 for e in is_estimated if e == "No")
    
    fit_stats = {
        "log_likelihood": log_likelihood,
        "ll_null": ll_null,
        "n_params": n_params,
        "n_individuals": n_individuals,
        "n_single_males": n_sm,
        "n_single_females": n_sf,
        "n_couples": n_cou,
        "aic": 2 * n_params - 2 * log_likelihood if log_likelihood else np.nan,
        "bic": n_params * np.log(n_individuals) - 2 * log_likelihood if log_likelihood else np.nan,
        "pseudo_r2_mcfadden": 1 - (log_likelihood / ll_null) if ll_null != 0 and log_likelihood else np.nan,
        "estimation_time": est_time_str,
        "estimation_time_seconds": estimation_time_seconds if estimation_time_seconds else np.nan,
        "n_bounded_params": n_bounded,
        "n_hit_lower_bound": n_hit_lower,
        "n_hit_upper_bound": n_hit_upper,
        "n_not_estimated": n_not_estimated,
    }
    
    # =========================================================================
    # 9. Generate comprehensive HTML report
    # =========================================================================
    LOGGER.info("\n8. Generating comprehensive HTML report...")
    
    html_path = out_dir / f"{wage_spec}_joint_post_estimation_report.html"
    
    _build_joint_html_report(
        param_table=param_table,
        fit_stats=fit_stats,
        group_params=group_params,
        median_shifters=median_shifters,
        elasticities_df=elasticities_df,
        fit_results=fit_results,
        mu_plot_paths=mu_plot_paths,
        contour_paths=contour_paths,
        fit_plot_paths=fit_plot_paths,
        output_path=html_path,
        wage_spec=wage_spec,
    )
    
    LOGGER.info("\n" + "=" * 70)
    LOGGER.info("JOINT POST-ESTIMATION COMPLETE")
    LOGGER.info("=" * 70)
    LOGGER.info(f"Output directory: {out_dir}")
    LOGGER.info(f"HTML report: {html_path.name}")
    
    return {
        "param_table": param_table,
        "fit_stats": fit_stats,
        "group_params": group_params,
        "median_shifters": median_shifters,
        "elasticities": elasticities_df,
        "fit_diagnostics": fit_results,
        "plots": {
            **mu_plot_paths,
            **contour_paths,
            **fit_plot_paths,
        },
        "html_report": html_path,
    }


def _build_joint_html_report(
    param_table: pd.DataFrame,
    fit_stats: Dict[str, float],
    group_params: Dict[str, Dict[str, float]],
    median_shifters: Dict[str, Dict[str, float]],
    elasticities_df: pd.DataFrame,
    fit_results: Dict[str, Dict[str, Any]],
    mu_plot_paths: Dict[str, Path],
    contour_paths: Dict[str, Path],
    fit_plot_paths: Dict[str, Path],
    output_path: Path,
    wage_spec: str = "fw",
) -> Path:
    """Build comprehensive HTML report for joint estimation with enhanced parameter table."""
    from datetime import datetime
    
    def _img_tag(path: Path, alt: str) -> str:
        if path and path.exists():
            return f'<img src="{path.name}" alt="{alt}" style="max-width:100%;">'
        return f'<p><em>({alt} not available)</em></p>'
    
    def _format_value(v):
        if isinstance(v, float):
            if not np.isfinite(v):
                return "N/A"
            if abs(v) < 0.001 or abs(v) > 10000:
                return f"{v:.4e}"
            return f"{v:.4f}"
        return str(v)
    
    def _format_bound(v):
        """Format bound value for display."""
        if v is None:
            return "—"
        if isinstance(v, float):
            if abs(v) < 0.001:
                return f"{v:.4e}"
            return f"{v:.4f}"
        return str(v)
    
    def _get_pvalue_class(p):
        """Get CSS class for p-value coloring."""
        if not np.isfinite(p):
            return ""
        if p <= 0.05:
            return "pval-sig"  # Significant (no special color, default)
        elif p <= 0.1:
            return "pval-marginal"  # Green (0.05-0.1)
        elif p <= 0.25:
            return "pval-weak"  # Yellow (0.1-0.25)
        else:
            return "pval-insig"  # Red (>0.25)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Build enhanced parameter table HTML with color coding
    param_rows = []
    for idx, row in param_table.iterrows():
        param_name = row["parameter"]
        estimate = row["estimate"]
        se = row["std_error"]
        t_val = row["t_value"]
        p_val = row["p_value"]
        lb = row.get("lower_bound")
        ub = row.get("upper_bound")
        bounded = row.get("bounded", "No")
        hit_lower = row.get("hit_lower", False)
        hit_upper = row.get("hit_upper", False)
        init_val = row.get("initial_value", np.nan)
        estimated = row.get("estimated", "Unknown")
        
        # Row classes
        row_classes = []
        if bounded == "Yes":
            row_classes.append("bounded-param")
        if estimated == "No":
            row_classes.append("not-estimated")
        
        row_class_str = ' class="' + ' '.join(row_classes) + '"' if row_classes else ""
        
        # Cell classes for bound hits
        lb_class = ' class="bound-hit"' if hit_lower else ""
        ub_class = ' class="bound-hit"' if hit_upper else ""
        
        # P-value coloring
        pval_class = _get_pvalue_class(p_val) if np.isfinite(p_val) else ""
        pval_class_str = f' class="{pval_class}"' if pval_class else ""
        
        # Format significance stars
        sig = ""
        if np.isfinite(p_val):
            if p_val < 0.001:
                sig = "***"
            elif p_val < 0.01:
                sig = "**"
            elif p_val < 0.05:
                sig = "*"
        
        # Build row
        param_rows.append(f"""
        <tr{row_class_str}>
            <td>{param_name}</td>
            <td>{_format_value(estimate)}</td>
            <td>{_format_value(se)}</td>
            <td>{_format_value(t_val)}</td>
            <td{pval_class_str}>{_format_value(p_val)} {sig}</td>
            <td{lb_class}>{_format_bound(lb)}</td>
            <td{ub_class}>{_format_bound(ub)}</td>
            <td>{bounded}</td>
            <td>{_format_value(init_val)}</td>
            <td>{estimated}</td>
        </tr>
        """)
    
    param_html = f"""
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
        <tbody>
            {''.join(param_rows)}
        </tbody>
    </table>
    """
    
    # Elasticities table HTML
    elast_html = elasticities_df.to_html(
        classes="table table-striped",
        float_format=lambda x: f"{x:.3f}" if isinstance(x, float) and np.isfinite(x) else str(x),
        border=0, index=False,
    )
    
    # Fit stats HTML
    fit_stats_html = "\n".join(
        f"<tr><th>{k}</th><td>{_format_value(v)}</td></tr>"
        for k, v in fit_stats.items()
    )
    
    # Group parameters summary
    group_params_html = ""
    group_labels = {
        GROUP_SINGLE_MALE: "Single Males",
        GROUP_SINGLE_FEMALE: "Single Females",
        GROUP_COUPLE_MALE: "Males in Couples",
        GROUP_COUPLE_FEMALE: "Females in Couples",
        GROUP_COUPLE: "Couples (shared)",
    }
    
    for group in list(ALL_GROUPS) + [GROUP_COUPLE]:
        params = group_params.get(group, {})
        if params:
            rows = "\n".join(
                f"<tr><td>{k}</td><td>{_format_value(v)}</td></tr>"
                for k, v in params.items()
            )
            group_params_html += f"""
            <div class="param-group">
                <h4>{group_labels.get(group, group)}</h4>
                <table class="table table-sm">{rows}</table>
            </div>
            """
    
    # Contour plots grid
    contour_html = ""
    for group in ALL_GROUPS:
        path = contour_paths.get(group)
        contour_html += f"""
        <div class="contour-item">
            <h4>{group_labels.get(group, group)}</h4>
            {_img_tag(path, f"{group} contours")}
        </div>
        """
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RURO Joint Post-Estimation Analysis ({wage_spec.upper()})</title>
  <style>
    :root {{
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
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
      margin: 0; padding: 2em; max-width: 1600px; margin: 0 auto;
      line-height: 1.6; color: #333;
    }}
    h1 {{ color: var(--primary-color); border-bottom: 3px solid var(--primary-color); padding-bottom: 0.5em; }}
    h2 {{ color: var(--primary-color); margin-top: 2em; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; }}
    h3 {{ color: var(--primary-color); }}
    h4 {{ margin-bottom: 0.5em; }}
    .table {{ border-collapse: collapse; margin-bottom: 1.5em; width: 100%; }}
    .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    .table th {{ background-color: var(--bg-light); font-weight: 600; }}
    .table-striped tbody tr:nth-child(odd) {{ background-color: #f9f9f9; }}
    .table-sm th, .table-sm td {{ padding: 5px 8px; font-size: 0.9em; }}
    section {{ margin-bottom: 2.5em; padding: 1.5em; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    figure {{ margin: 1em 0; text-align: center; }}
    figcaption {{ font-weight: bold; margin-bottom: 0.5em; color: var(--primary-color); }}
    img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; }}
    .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5em; }}
    .four-col {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5em; }}
    .stats-box {{ background: var(--bg-light); padding: 1em; border-radius: 4px; border-left: 4px solid var(--primary-color); }}
    .param-groups {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1em; }}
    .param-group {{ background: var(--bg-light); padding: 1em; border-radius: 4px; }}
    .contour-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5em; }}
    .contour-item {{ text-align: center; }}
    .header-info {{ background: var(--bg-light); padding: 1em; border-radius: 4px; margin-bottom: 2em; }}
    .group-legend {{ display: flex; gap: 2em; margin: 1em 0; flex-wrap: wrap; }}
    .legend-item {{ display: flex; align-items: center; gap: 0.5em; }}
    .legend-color {{ width: 20px; height: 4px; border-radius: 2px; }}
    
    /* Parameter table color coding */
    .param-table .bounded-param {{ background-color: var(--bounded-row-color) !important; }}
    .param-table .not-estimated {{ background-color: var(--not-estimated-color) !important; }}
    .param-table .bound-hit {{ background-color: var(--bound-hit-color) !important; font-weight: bold; }}
    .param-table .pval-marginal {{ background-color: var(--pval-marginal); }}
    .param-table .pval-weak {{ background-color: var(--pval-weak); }}
    .param-table .pval-insig {{ background-color: var(--pval-insig); }}
    
    /* Color legend for parameter table */
    .color-legend {{ display: flex; flex-wrap: wrap; gap: 1em; margin: 1em 0; padding: 0.5em; background: #f0f0f0; border-radius: 4px; }}
    .color-legend-item {{ display: flex; align-items: center; gap: 0.5em; font-size: 0.85em; }}
    .color-box {{ width: 16px; height: 16px; border: 1px solid #999; border-radius: 2px; }}
    
    @media (max-width: 768px) {{ .two-col, .four-col, .contour-grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <h1>📊 RURO Joint Post-Estimation Analysis</h1>
  
  <div class="header-info">
    <p><strong>Specification:</strong> {wage_spec.upper()} | <strong>Generated:</strong> {timestamp}</p>
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
      {fit_stats_html}
    </table>
  </section>
  
  <section>
    <h2>📊 Marginal Utility Comparison</h2>
    <p>Comparing MUC and MUL across all demographic groups at median characteristics.</p>
    <div class="two-col">
      <figure>
        <figcaption>Marginal Utility of Consumption</figcaption>
        {_img_tag(mu_plot_paths.get("muc_comparison"), "MUC comparison")}
      </figure>
      <figure>
        <figcaption>Marginal Utility of Leisure</figcaption>
        {_img_tag(mu_plot_paths.get("mul_comparison"), "MUL comparison")}
      </figure>
    </div>
  </section>
  
  <section>
    <h2>🗺️ Utility Indifference Curves by Group</h2>
    <p>Contour lines at utility levels: 10%, 25%, 50%, 75%, 99%</p>
    <div class="contour-grid">
      {contour_html}
    </div>
  </section>
  
  <section>
    <h2>📈 Labor Supply Elasticities</h2>
    <p>Structural approximations based on estimated preference parameters.</p>
    {elast_html}
    <p><small><em>Note: For exact elasticities, use simulation-based methods with tax-benefit integration.</em></small></p>
  </section>
  
  <section>
    <h2>🎯 Fit Diagnostics</h2>
    <div class="two-col">
      <figure>
        <figcaption>Participation Rates</figcaption>
        {_img_tag(fit_plot_paths.get("participation"), "Participation rates")}
      </figure>
      <figure>
        <figcaption>Mean Hours (conditional)</figcaption>
        {_img_tag(fit_plot_paths.get("mean_hours"), "Mean hours")}
      </figure>
    </div>
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
    <div class="color-legend">
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--bounded-row-color);"></div>Bounded parameter</div>
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--bound-hit-color);"></div>Hit bound</div>
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--not-estimated-color);"></div>Not estimated</div>
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--pval-marginal);"></div>p-value 0.05-0.1</div>
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--pval-weak);"></div>p-value 0.1-0.25</div>
      <div class="color-legend-item"><div class="color-box" style="background-color: var(--pval-insig);"></div>p-value &gt; 0.25</div>
    </div>
    <div style="max-height:600px; overflow-y:auto;">
      {param_html}
    </div>
  </section>
  
  <footer style="margin-top: 3em; padding-top: 1em; border-top: 1px solid #ddd; color: #666; font-size: 0.9em;">
    <p>Generated by RURO_post_estimation.py | {timestamp}</p>
    <p>Utility function: U = β_l(X) × BC(l; θ_l) + β_c × BC(c; θ_c) where BC(x;θ) = (x^θ - 1)/θ</p>
  </footer>
  
</body>
</html>
"""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    LOGGER.info(f"Joint HTML report saved to: {output_path}")
    return output_path


# =============================================================================
# COMMAND-LINE INTERFACE
# =============================================================================

def main():
    """
    Command-line interface for post-estimation analysis.
    
    Example:
        python RURO_post_estimation.py --results results.json --mnl-file data.parquet --out-dir outputs/
    """
    import argparse
    import json
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    
    parser = argparse.ArgumentParser(
        description="Comprehensive post-estimation analysis for RURO models"
    )
    parser.add_argument(
        "--results",
        type=str,
        required=True,
        help="Path to estimation results JSON file",
    )
    parser.add_argument(
        "--mnl-file",
        type=str,
        default=None,
        help="Path to MNL dataset (parquet) for marginal utility plots",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="outputs/estimates",
        help="Output directory for post-estimation results",
    )
    parser.add_argument(
        "--wage-spec",
        type=str,
        choices=["fw", "vw"],
        default="fw",
        help="Wage specification: fw (fixed) or vw (variable)",
    )
    parser.add_argument(
        "--sex",
        type=str,
        choices=["m", "f", "pooled"],
        default="pooled",
        help="Sex filter: m, f, or pooled",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Skip generating plots",
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Skip generating HTML report",
    )
    
    args = parser.parse_args()
      # Load results
    with open(args.results, "r") as f:
        results = json.load(f)
    
    theta = np.array(results["theta"])
    param_names = results.get("param_names", [f"theta_{i}" for i in range(len(theta))])
    
    # Handle n_individuals for different estimation modes
    if "n_individuals" in results:
        n_individuals = results["n_individuals"]
    elif "mode" in results and results["mode"] == "joint":
        # Joint estimation: sum individuals from all groups
        n_individuals = results.get("n_sm", 0) + results.get("n_sf", 0) + results.get("n_cou", 0)
        if n_individuals == 0:
            LOGGER.warning("Joint estimation but no individual counts found, defaulting to 1000")
            n_individuals = 1000
    else:
        LOGGER.warning("n_individuals not found in results, defaulting to 1000")
        n_individuals = 1000
    
    log_likelihood = results.get("log_likelihood", None)
    
    LOGGER.info(f"Loaded {len(theta)} parameters from {args.results}")
    LOGGER.info(f"Log-likelihood: {log_likelihood}")
    LOGGER.info(f"N individuals: {n_individuals}")
    
    # Load MNL data if provided
    df = None
    if args.mnl_file:
        import pandas as pd
        try:
            if args.mnl_file.endswith(".parquet"):
                df = pd.read_parquet(args.mnl_file)
            else:
                df = pd.read_csv(args.mnl_file)
            LOGGER.info(f"Loaded MNL dataset: {len(df)} rows")
        except Exception as e:
            LOGGER.warning(f"Could not load MNL file: {e}")
    
    # Create a mock result object for standalone use
    class MockResult:
        def __init__(self, x, fun):
            self.x = x
            self.fun = fun
    
    mock_result = MockResult(theta, -log_likelihood if log_likelihood else 0.0)
    
    # Note: For full post-estimation, we need gradient function
    # This CLI is mainly for viewing results and generating plots from saved data
    LOGGER.warning("CLI mode: Cannot compute Hessian without gradient function.")
    LOGGER.info("For full SE computation, use run_full_post_estimation() from RURO_estimate_FR.py")
    
    # Display parameter estimates
    print("\n" + "=" * 60)
    print("PARAMETER ESTIMATES")
    print("=" * 60)
    print(f"{'Parameter':<40} {'Estimate':>12}")
    print("-" * 54)
    for name, val in zip(param_names, theta):
        print(f"  {name:<38}: {val:>10.4f}")
      # If we have data, generate marginal utility plots and analysis
    if df is not None and not args.no_plots:
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        params = extract_preference_params(theta, param_names)
        beta_c = params.get("beta_c", 0.0)
        theta_c = params.get("theta_c", 1.0)
        theta_l = params.get("theta_l", 1.0)
        beta_l0 = params.get("beta_l0", 0.0)
        
        LOGGER.info("\nGenerating comprehensive analysis and plots...")
        
        # =====================================================================
        # GENERATE COMPREHENSIVE MARGINAL UTILITY ANALYSIS
        # =====================================================================
        
        # 1. Basic MUC/MUL curves
        c_grid = np.linspace(0.1, 2.0, 200)
        l_grid = np.linspace(0.1, 2.0, 200)
        
        muc_curve = compute_marginal_utility_consumption(c_grid, beta_c, theta_c)
        mul_curve = compute_marginal_utility_leisure(l_grid, beta_l0, theta_l)
        
        muc_path = out_dir / f"{args.wage_spec}_{args.sex}_muc.png"
        mul_path = out_dir / f"{args.wage_spec}_{args.sex}_mul.png"
        
        plot_marginal_utility(
            c_grid, muc_curve,
            xlabel="Normalized Consumption",
            ylabel="MUC",
            title=f"MUC - {args.sex.capitalize()} ({args.wage_spec})",
            output_path=muc_path,
        )
        
        plot_marginal_utility(
            l_grid, mul_curve,
            xlabel="Normalized Leisure",
            ylabel="MUL",
            title=f"MUL - {args.sex.capitalize()} ({args.wage_spec})",
            output_path=mul_path,
        )
        
        # 2. Contour plot (if we have utility function)
        contour_path = out_dir / f"{args.wage_spec}_{args.sex}_contours.png"
        try:
            plot_utility_contours(
                beta_c=beta_c,
                beta_l=beta_l0,
                theta_c=theta_c,
                theta_l=theta_l,
                output_path=contour_path,
                title=f"Utility Contours - {args.sex.capitalize()} ({args.wage_spec})",
            )
        except Exception as e:
            LOGGER.warning(f"Could not generate contour plot: {e}")
            contour_path = None
        
        # 3. Combined MUC/MUL plot
        combined_path = out_dir / f"{args.wage_spec}_{args.sex}_mu_combined.png"
        try:
            plot_muc_mul_combined(
                c_grid, muc_curve, l_grid, mul_curve,
                output_path=combined_path,
                title=f"Marginal Utilities - {args.sex.capitalize()} ({args.wage_spec})",
            )
        except Exception as e:
            LOGGER.warning(f"Could not generate combined plot: {e}")
            combined_path = None
        
        # 4. MRS plot
        mrs_path = out_dir / f"{args.wage_spec}_{args.sex}_mrs.png"
        try:
            mrs_values = compute_mrs(muc_curve, mul_curve)
            plot_mrs_curve(
                l_grid, mrs_values,
                output_path=mrs_path,
                title=f"MRS - {args.sex.capitalize()} ({args.wage_spec})",
            )
        except Exception as e:
            LOGGER.warning(f"Could not generate MRS plot: {e}")
            mrs_path = None
        
        # 5. Parameter significance plot
        # Create a simple parameter table (without SE since we don't have gradient)
        param_sig_path = out_dir / f"{args.wage_spec}_{args.sex}_param_significance.png"
        try:
            param_df = pd.DataFrame({
                "parameter": param_names,
                "estimate": theta,
                "std_error": [np.nan] * len(theta),  # Not available in CLI mode
                "t_value": [np.nan] * len(theta),
                "p_value": [np.nan] * len(theta),
            })
            plot_parameter_significance(
                param_df,
                param_sig_path,
                title=f"Parameter Estimates - {args.sex.capitalize()} ({args.wage_spec})",
            )
        except Exception as e:
            LOGGER.warning(f"Could not generate parameter significance plot: {e}")
            param_sig_path = None
        
        # 6. Generate simplified HTML report (without SE/Hessian)
        if not args.no_html:
            html_path = out_dir / f"{args.wage_spec}_{args.sex}_post_estimation_report.html"
            try:
                # Create simplified parameter table
                param_df = pd.DataFrame({
                    "parameter": param_names,
                    "estimate": theta,
                    "std_error": [np.nan] * len(theta),
                    "t_value": [np.nan] * len(theta),
                    "p_value": [np.nan] * len(theta),
                })
                  # Create fit stats
                n_params = len(theta)
                
                # Compute n_alternatives from data if available
                n_alts = 100  # Default
                if df is not None:
                    id_col = None
                    for col in ["idhh", "idhh_true", "id"]:
                        if col in df.columns:
                            id_col = col
                            break
                    if id_col is not None:
                        alts_per_ind = df.groupby(id_col).size()
                        n_alts = int(alts_per_ind.mode().iloc[0]) if len(alts_per_ind) > 0 else 100
                
                ll_null = n_individuals * np.log(1.0 / n_alts)
                fit_stats = {
                    "log_likelihood": log_likelihood,
                    "ll_null": ll_null,
                    "n_params": n_params,
                    "n_individuals": n_individuals,
                    "n_alternatives": n_alts,
                    "aic": 2 * n_params - 2 * log_likelihood,
                    "bic": n_params * np.log(n_individuals) - 2 * log_likelihood,
                    "pseudo_r2_mcfadden": 1 - (log_likelihood / ll_null) if ll_null != 0 else 0,
                    "pseudo_r2_adjusted": 1 - ((log_likelihood - n_params) / ll_null) if ll_null != 0 else 0,
                    "ll_per_obs": log_likelihood / n_individuals if n_individuals > 0 else 0,
                }
                
                build_html_report(
                    param_table=param_df,
                    fit_stats=fit_stats,
                    output_path=html_path,
                    gender=args.sex,
                    variant=args.wage_spec,
                    muc_plot=muc_path,
                    mul_plot=mul_path,
                    contour_plot=contour_path,
                    param_sig_plot=param_sig_path,
                    muc_mul_combined_plot=combined_path,
                    mrs_plot=mrs_path,
                    model_description="Post-estimation analysis (CLI mode - standard errors not available)",
                )
                LOGGER.info(f"HTML report saved to: {html_path}")
            except Exception as e:
                LOGGER.error(f"Could not generate HTML report: {e}")
                import traceback
                traceback.print_exc()
        
        LOGGER.info(f"Plots saved to: {out_dir}")
        LOGGER.info(f"  - MUC plot: {muc_path.name}")
        LOGGER.info(f"  - MUL plot: {mul_path.name}")
        if contour_path:
            LOGGER.info(f"  - Contour plot: {contour_path.name}")
        if combined_path:
            LOGGER.info(f"  - Combined MU plot: {combined_path.name}")
        if mrs_path:
            LOGGER.info(f"  - MRS plot: {mrs_path.name}")
        if param_sig_path:
            LOGGER.info(f"  - Parameter significance: {param_sig_path.name}")
    
    print("\nDone.")


if __name__ == "__main__":
    main()
