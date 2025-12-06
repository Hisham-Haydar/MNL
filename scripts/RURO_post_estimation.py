#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RURO_post_estimation.py
=======================

Post-estimation analysis for RURO labor supply models.

Following Stijn Van Houtven's R code (Ruro_estimation_new.Rmd, Section 2.3):
- Variance-covariance matrix computation
- Standard errors and t-values
- Hessian diagnostics (eigenvalues check)
- Model fit statistics (AIC, BIC, pseudo R²)
- Gradient accuracy check

Usage:
    from RURO_post_estimation import run_post_estimation, compute_standard_errors
    
    # After estimation:
    post_results = run_post_estimation(
        result=opt_result,
        grad_func=gradient_function,
        param_names=param_names,
        n_individuals=n_individuals,
        out_dir=Path("outputs/estimates/fr"),
    )

Author: Hisham Haydar
Date: 2025-12-06
"""

import logging
import numpy as np
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

LOGGER = logging.getLogger(__name__)


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
    
    Following Stijn's R code:
    ```r
    f_numeric_hessian <- function(param, start_gradient, delta){
      sd_mat <- matrix(rep(0, length(param)^2), length(param))
      for (i in 1:length(param)){
        param_t <- param
        param_t[i] <- param[i]*(1+delta)
        sd_mat[,i] <- (f_gradient_optim(param_t)-start_gradient)/(param[i]*delta)
      }
      return(sd_mat)
    }
    ```
    
    Parameters
    ----------
    theta : np.ndarray
        Parameter vector at optimum
    grad_func : Callable
        Gradient function that takes theta and returns gradient vector
    delta : float
        Relative perturbation size (default 1e-4, as in Stijn's code)
    
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
        # Use relative perturbation like Stijn's code: param[i]*(1+delta)
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
    
    This is Stijn's "Jacobian" method:
    ```r
    hessian <- jacobian(f_gradient_optim, param)
    ```
    
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
    
    Following Stijn's R code (Section 2.3):
    ```r
    hessian <- jacobian(f_gradient_optim, param)
    varcov <- solve(hessian)
    SE <- sqrt(diag(solve(hessian)))
    TV <- param/SE
    ```
    
    Parameters
    ----------
    theta : np.ndarray
        Estimated parameters
    grad_func : Callable
        Gradient function
    param_names : List[str]
        Parameter names
    method : str
        "jacobian" (central diff, more accurate) or "numeric" (forward diff, Stijn's method)
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
    
    Following Stijn's R code:
    ```r
    check_gradient <- check.derivatives(.x = param, 
                                        func = f_likelihood_optim, 
                                        func_grad = f_gradient_optim, 
                                        check_derivatives_print = "all")
    ```
    
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
    check_gradient: bool = False,
) -> Dict[str, Any]:
    """
    Run full post-estimation analysis and optionally save results.
    
    Following Stijn's R workflow (Section 2.3):
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
        Gradient function
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
    LOGGER.info("\n2. Computing standard errors (numeric Hessian - Stijn's method)...")
    se_results_num = compute_standard_errors(
        theta, grad_func, param_names, method="numeric", delta=1e-4
    )
    
    # -------------------------------------------------------------------------
    # 3. Model fit statistics
    # -------------------------------------------------------------------------
    LOGGER.info("\n3. Computing model fit statistics...")
    fit_stats = compute_model_fit_statistics(
        log_likelihood=log_likelihood,
        n_params=n_params,
        n_individuals=n_individuals,
        n_alternatives_per_individual=100,  # RURO default
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
    # 5. Save to Excel (like Stijn's code)
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
                
                # Sheet 6: Numeric Hessian comparison (Stijn's method)
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
# COMMAND-LINE INTERFACE
# =============================================================================

def main():
    """
    Command-line interface for post-estimation analysis.
    
    Example:
        python RURO_post_estimation.py --results results.json --mnl-file data.parquet
    """
    import argparse
    import json
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    
    parser = argparse.ArgumentParser(
        description="Post-estimation analysis for RURO models"
    )
    parser.add_argument(
        "--results",
        type=str,
        required=True,
        help="Path to estimation results JSON file",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="outputs/estimates",
        help="Output directory for post-estimation results",
    )
    
    args = parser.parse_args()
    
    # Load results
    with open(args.results, "r") as f:
        results = json.load(f)
    
    theta = np.array(results["theta"])
    param_names = results.get("param_names", [f"theta_{i}" for i in range(len(theta))])
    
    LOGGER.info(f"Loaded {len(theta)} parameters from {args.results}")
    LOGGER.info(f"Log-likelihood: {results.get('log_likelihood', 'N/A')}")
    
    # Note: To compute standard errors, we need the gradient function
    # This requires re-loading the data and model specification
    LOGGER.warning("Full post-estimation requires gradient function - use from RURO_estimate_FR.py")
    LOGGER.info("For now, displaying loaded results only.")
    
    print("\nEstimated Parameters:")
    print("-" * 50)
    for name, val in zip(param_names, theta):
        print(f"  {name:<40}: {val:>10.4f}")


if __name__ == "__main__":
    main()
