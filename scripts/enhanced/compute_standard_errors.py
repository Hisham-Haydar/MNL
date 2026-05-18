#!/usr/bin/env python
"""
==============================================================================
Compute Standard Errors for Existing Estimation Results
==============================================================================
This script loads existing estimation results and computes standard errors
using numerical Hessian approximation.

Usage:
    python compute_standard_errors.py \
        --results-json outputs/estimates/fr/2016_v2/estimation_results.json \
        --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
        --spec-config scripts/enhanced/specifications/estimation_spec_v2.yaml

Author: Enhanced RURO Pipeline
Created: 2026-01-09
==============================================================================
"""

import argparse
import json
import logging
import sys
import numpy as np
from pathlib import Path
from datetime import datetime
from scipy.stats import norm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from estimation_utils import (
    load_and_validate_mnl_data,
    precompute_data_singles,
    precompute_data_couples,
)
from estimation_spec_parser import parse_specification
from estimation_engine import compute_gradient_joint


def compute_standard_errors(
    theta: np.ndarray,
    grad_func,
    eps: float = 1e-5,
    use_pinv: bool = True,
    rcond: float = 1e-10,
) -> dict:
    """
    Compute standard errors using numerical Hessian approximation.
    
    Uses central differences on the gradient to approximate the Hessian,
    then inverts to get variance-covariance matrix.
    
    Parameters
    ----------
    theta : np.ndarray
        Parameter estimates
    grad_func : callable
        Function returning gradient of negative log-likelihood
    eps : float
        Step size for numerical differentiation
    use_pinv : bool
        If True, use Moore-Penrose pseudoinverse (more robust)
    rcond : float
        Cutoff for small singular values (for pinv)
    """
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
    
    # Check condition number
    try:
        cond = np.linalg.cond(H)
        logger.info(f"Hessian condition number: {cond:.2e}")
        if cond > 1e10:
            logger.warning(f"Hessian is ill-conditioned (cond={cond:.2e})")
    except:
        logger.warning("Could not compute condition number")
    
    # Compute variance-covariance matrix
    try:
        if use_pinv:
            # Use pseudoinverse - more robust for near-singular matrices
            logger.info("Using Moore-Penrose pseudoinverse for robustness...")
            varcov = np.linalg.pinv(H, rcond=rcond)
        else:
            varcov = np.linalg.inv(H)
            
        se = np.sqrt(np.abs(np.diag(varcov)))  # abs to handle numerical issues
        
        # Check for negative variances (indicates identification problems)
        neg_var = np.diag(varcov) < 0
        if np.any(neg_var):
            n_neg = np.sum(neg_var)
            logger.warning(f"Warning: {n_neg} parameters have negative variance (identification issue)")
            # Mark these as NaN
            se[neg_var] = np.nan
        
        # Flag parameters with very large SEs (likely poorly identified)
        large_se = se > 100 * np.abs(theta)
        if np.any(large_se & ~np.isnan(se)):
            n_large = np.sum(large_se & ~np.isnan(se))
            logger.warning(f"Warning: {n_large} parameters have very large SEs (poor identification)")
        
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
        return {
            'se': np.full(n_params, np.nan),
            'varcov': None,
            't_values': np.full(n_params, np.nan),
            'p_values': np.full(n_params, np.nan),
            'hessian': H,
        }


def main():
    parser = argparse.ArgumentParser(
        description="Compute standard errors for existing estimation results"
    )
    parser.add_argument(
        "--results-json",
        type=Path,
        required=True,
        help="Path to estimation_results.json"
    )
    parser.add_argument(
        "--mnl-base",
        type=Path,
        required=True,
        help="Base path for MNL datasets"
    )
    parser.add_argument(
        "--spec-config",
        type=Path,
        required=True,
        help="Path to YAML specification file"
    )
    parser.add_argument(
        "--eps",
        type=float,
        default=1e-5,
        help="Step size for numerical differentiation (default: 1e-5)"
    )
    
    args = parser.parse_args()
    
    logger.info("="*80)
    logger.info("Computing Standard Errors")
    logger.info("="*80)
    
    # Load results
    logger.info(f"Loading results from: {args.results_json}")
    with open(args.results_json, 'r') as f:
        results = json.load(f)
    
    # Get theta from results
    if 'joint' in results.get('results', {}):
        theta = np.array(results['results']['joint']['theta'])
        logger.info(f"Loaded joint theta with {len(theta)} parameters")
    else:
        # Try to find any group
        for group in ['singles_male', 'singles_female', 'couples']:
            if group in results.get('results', {}):
                theta = np.array(results['results'][group]['theta'])
                logger.info(f"Loaded {group} theta with {len(theta)} parameters")
                break
        else:
            raise ValueError("No theta found in results")
    
    # Load specification
    logger.info(f"Loading specification from: {args.spec_config}")
    spec = parse_specification(args.spec_config)
    
    # Load data
    logger.info(f"Loading data from: {args.mnl_base}")
    mnl_base = args.mnl_base
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
    
    data_sm = None
    data_sf = None
    data_cou = None
    
    if df_singles is not None:
        df_sm = df_singles[df_singles["dgn"] == 1]
        df_sf = df_singles[df_singles["dgn"] == 0]
        
        if len(df_sm) > 0:
            logger.info("Precomputing singles (male) data...")
            data_sm = precompute_data_singles(
                df=df_sm, metadata=metadata, is_male=True,
                include_wage_vars=include_wage_vars,
                include_loc_vars=include_loc_vars
            )
        
        if len(df_sf) > 0:
            logger.info("Precomputing singles (female) data...")
            data_sf = precompute_data_singles(
                df=df_sf, metadata=metadata, is_male=False,
                include_wage_vars=include_wage_vars,
                include_loc_vars=include_loc_vars
            )
    
    if df_couples is not None:
        logger.info("Precomputing couples data...")
        data_cou = precompute_data_couples(
            df=df_couples, metadata=metadata,
            include_wage_vars=include_wage_vars,
            include_loc_vars=include_loc_vars
        )
    
    # Build gradient function
    def grad_func(theta_):
        return compute_gradient_joint(theta_, data_sm, data_sf, data_cou, spec)
    
    # Compute SEs
    logger.info("")
    logger.info("="*80)
    logger.info("Computing Numerical Hessian and Standard Errors")
    logger.info("="*80)
    
    se_results = compute_standard_errors(theta, grad_func, eps=args.eps)
    
    # Print results table
    logger.info("")
    logger.info("="*80)
    logger.info("Parameter Estimates with Standard Errors")
    logger.info("="*80)
    logger.info(f"{'Parameter':<30} {'Estimate':>12} {'Std.Err':>12} {'t-value':>10} {'p-value':>10}")
    logger.info("-"*80)
    
    param_names = spec.all_param_names
    for i, name in enumerate(param_names):
        est = theta[i]
        se = se_results['se'][i]
        t = se_results['t_values'][i]
        p = se_results['p_values'][i]
        
        # Significance stars
        stars = ""
        if not np.isnan(p):
            if p < 0.001:
                stars = "***"
            elif p < 0.01:
                stars = "**"
            elif p < 0.05:
                stars = "*"
            elif p < 0.1:
                stars = "."
        
        se_str = f"{se:12.6f}" if not np.isnan(se) else "        N/A"
        t_str = f"{t:10.3f}" if not np.isnan(t) else "       N/A"
        p_str = f"{p:10.4f}" if not np.isnan(p) else "       N/A"
        
        logger.info(f"{name:<30} {est:12.6f} {se_str} {t_str} {p_str} {stars}")
    
    logger.info("-"*80)
    logger.info("Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1")
    
    # Count significant parameters
    n_sig_001 = np.sum(se_results['p_values'] < 0.001)
    n_sig_01 = np.sum((se_results['p_values'] >= 0.001) & (se_results['p_values'] < 0.01))
    n_sig_05 = np.sum((se_results['p_values'] >= 0.01) & (se_results['p_values'] < 0.05))
    n_sig_10 = np.sum((se_results['p_values'] >= 0.05) & (se_results['p_values'] < 0.1))
    n_not_sig = np.sum(se_results['p_values'] >= 0.1)
    n_nan = np.sum(np.isnan(se_results['p_values']))
    
    logger.info("")
    logger.info(f"Significance summary:")
    logger.info(f"  p < 0.001: {n_sig_001} parameters")
    logger.info(f"  p < 0.01:  {n_sig_01} parameters")
    logger.info(f"  p < 0.05:  {n_sig_05} parameters")
    logger.info(f"  p < 0.1:   {n_sig_10} parameters")
    logger.info(f"  p >= 0.1:  {n_not_sig} parameters")
    logger.info(f"  N/A:       {n_nan} parameters")
    
    # Update results JSON with SEs
    logger.info("")
    logger.info("="*80)
    logger.info("Updating Results JSON")
    logger.info("="*80)
    
    results['standard_errors'] = {
        'se': [float(x) if not np.isnan(x) else None for x in se_results['se']],
        't_values': [float(x) if not np.isnan(x) else None for x in se_results['t_values']],
        'p_values': [float(x) if not np.isnan(x) else None for x in se_results['p_values']],
    }
    
    # Also add to joint results if present
    if 'joint' in results.get('results', {}):
        results['results']['joint']['standard_errors'] = results['standard_errors']['se']
        results['results']['joint']['t_values'] = results['standard_errors']['t_values']
        results['results']['joint']['p_values'] = results['standard_errors']['p_values']
    
    # Save updated results
    output_path = args.results_json
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Updated results saved to: {output_path}")
    
    # Also save a CSV with the results
    import pandas as pd
    df_params = pd.DataFrame({
        'parameter': param_names,
        'estimate': theta,
        'std_error': se_results['se'],
        't_value': se_results['t_values'],
        'p_value': se_results['p_values'],
    })
    
    csv_path = args.results_json.parent / "parameters_with_se.csv"
    df_params.to_csv(csv_path, index=False)
    logger.info(f"Saved parameter table to: {csv_path}")
    
    logger.info("")
    logger.info("="*80)
    logger.info("Standard Error Computation Complete!")
    logger.info("="*80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
