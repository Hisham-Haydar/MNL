#!/usr/bin/env python
"""
Compute fit statistics for Phase 4 estimation results.

This script computes:
- Rho-squared (McFadden's pseudo R²)
- Adjusted rho-squared
- AIC (Akaike Information Criterion)
- BIC (Bayesian Information Criterion)
- Standard errors from numerical Hessian

These statistics were missing from the original estimation output.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path

def compute_fit_statistics(results_file, mnl_file=None):
    """
    Compute fit statistics from estimation results.

    Parameters:
    -----------
    results_file : str
        Path to JSON results file
    mnl_file : str, optional
        Path to MNL dataset (needed for null log-likelihood)
    """
    # Load results
    print(f"Loading results from: {results_file}")
    with open(results_file, 'r') as f:
        results = json.load(f)

    # Extract key values
    ll_final = results['log_likelihood']
    n_params = len(results['theta'])
    n_individuals = results.get('n_individuals', None)

    print(f"\n{'='*70}")
    print(f"ESTIMATION RESULTS SUMMARY")
    print(f"{'='*70}")
    print(f"Mode: {results.get('mode', 'unknown')}")
    print(f"Wage spec: {results.get('wage_spec', 'unknown')}")
    print(f"Convergence: {results.get('success', False)}")
    print(f"Message: {results.get('message', 'N/A')}")
    print(f"\n{'='*70}")
    print(f"LIKELIHOOD")
    print(f"{'='*70}")
    print(f"Final log-likelihood: {ll_final:,.4f}")
    print(f"Number of parameters: {n_params}")
    print(f"Number of individuals: {n_individuals:,}" if n_individuals else "N/A")
    print(f"Iterations: {results.get('n_iterations', 'N/A')}")
    print(f"Function evaluations: {results.get('n_fev', 'N/A')}")
    print(f"Estimation time: {results.get('estimation_time_seconds', 0):.2f} seconds")

    # Compute fit statistics if we have MNL file
    if mnl_file and Path(mnl_file).exists():
        print(f"\nLoading MNL dataset from: {mnl_file}")
        df = pd.read_parquet(mnl_file)

        # Compute null log-likelihood (all probabilities = 1/J)
        # Group by individual and count alternatives
        # Try multiple ID column names
        id_col = None
        for candidate in ['ruro_id', 'idhh', 'idperson', 'id']:
            if candidate in df.columns:
                id_col = candidate
                break

        if id_col is None:
            raise ValueError(f"Could not find ID column. Available: {df.columns[:20].tolist()}")

        n_alts = df.groupby(id_col).size()
        ll_null = -np.sum(np.log(n_alts))

        print(f"\n{'='*70}")
        print(f"FIT STATISTICS")
        print(f"{'='*70}")
        print(f"Null log-likelihood (equal probabilities): {ll_null:,.4f}")

        # McFadden's pseudo R²
        rho_squared = 1 - (ll_final / ll_null)
        print(f"Rho-squared (McFadden's R²): {rho_squared:.4f}")

        # Adjusted rho-squared
        rho_squared_adj = 1 - ((ll_final - n_params) / ll_null)
        print(f"Adjusted rho-squared: {rho_squared_adj:.4f}")

        # AIC
        aic = 2 * n_params - 2 * ll_final
        print(f"AIC: {aic:,.4f}")

        # BIC
        n_obs = len(df)
        bic = n_params * np.log(n_obs) - 2 * ll_final
        print(f"BIC: {bic:,.4f}")

        # AIC per observation
        aic_per_obs = aic / n_obs
        print(f"AIC per observation: {aic_per_obs:.6f}")

    else:
        print("\nMNL file not provided or not found. Skipping fit statistics.")
        ll_null = None
        rho_squared = None
        rho_squared_adj = None
        aic = None
        bic = None

    # Check for standard errors
    print(f"\n{'='*70}")
    print(f"STANDARD ERRORS & INFERENCE")
    print(f"{'='*70}")

    has_se = 'std_errors' in results
    has_t = 't_values' in results
    has_pval = 'p_values' in results

    print(f"Standard errors computed: {'YES' if has_se else 'NO'}")
    print(f"T-values computed: {'YES' if has_t else 'NO'}")
    print(f"P-values computed: {'YES' if has_pval else 'NO'}")

    if has_se:
        se = np.array(results['std_errors'])
        theta = np.array(results['theta'])

        # Count significant parameters (|t| > 1.96)
        if has_t:
            t_vals = np.array(results['t_values'])
        else:
            t_vals = theta / se

        n_sig_05 = np.sum(np.abs(t_vals) > 1.96)
        n_sig_01 = np.sum(np.abs(t_vals) > 2.576)

        print(f"\nSignificant at 5%: {n_sig_05}/{n_params} ({100*n_sig_05/n_params:.1f}%)")
        print(f"Significant at 1%: {n_sig_01}/{n_params} ({100*n_sig_01/n_params:.1f}%)")

        # Parameters with SE = NaN
        n_nan_se = np.sum(np.isnan(se))
        if n_nan_se > 0:
            print(f"\nWARNING: {n_nan_se} parameters have NaN standard errors!")

        # Parameters with very large SE (> 1000)
        n_large_se = np.sum(se > 1000)
        if n_large_se > 0:
            print(f"WARNING: {n_large_se} parameters have very large SE (> 1000)!")

    # Parameter summary
    print(f"\n{'='*70}")
    print(f"PARAMETER SUMMARY")
    print(f"{'='*70}")

    param_names = results.get('param_names', [f'param_{i}' for i in range(n_params)])
    theta = np.array(results['theta'])
    theta0 = np.array(results['theta0'])

    # Parameters that moved from initial values
    moved = np.abs(theta - theta0) > 1e-6
    n_moved = np.sum(moved)

    print(f"Parameters moved from initial: {n_moved}/{n_params} ({100*n_moved/n_params:.1f}%)")
    print(f"Parameters at initial values: {n_params - n_moved}/{n_params} ({100*(n_params-n_moved)/n_params:.1f}%)")

    # Parameters exactly at zero
    at_zero = np.abs(theta) < 1e-10
    n_zero = np.sum(at_zero)
    print(f"Parameters exactly at zero: {n_zero}/{n_params} ({100*n_zero/n_params:.1f}%)")

    # Check bounds
    if 'bounds' in results:
        bounds = results['bounds']
        at_lower = []
        at_upper = []
        for i, (lb, ub) in enumerate(bounds):
            if lb is not None and np.abs(theta[i] - lb) < 1e-6:
                at_lower.append(i)
            if ub is not None and np.abs(theta[i] - ub) < 1e-6:
                at_upper.append(i)

        if at_lower:
            print(f"\nWARNING: {len(at_lower)} parameters at lower bound:")
            for i in at_lower[:5]:  # Show first 5
                print(f"  {param_names[i]}: {theta[i]:.6f}")
            if len(at_lower) > 5:
                print(f"  ... and {len(at_lower)-5} more")

        if at_upper:
            print(f"\nWARNING: {len(at_upper)} parameters at upper bound:")
            for i in at_upper[:5]:
                print(f"  {param_names[i]}: {theta[i]:.6f}")
            if len(at_upper) > 5:
                print(f"  ... and {len(at_upper)-5} more")

    # Group-wise summary
    print(f"\n{'='*70}")
    print(f"PARAMETER GROUPS")
    print(f"{'='*70}")

    groups = {
        'SM Prefs': (0, 9),
        'SF Prefs': (9, 18),
        'COU Prefs': (18, 34),
        'HOPP_M': (34, 41),
        'HOPP_F': (41, 48),
        'WOPP_M': (48, 54),
        'WOPP_F': (54, 60),
    }

    for group_name, (start, end) in groups.items():
        if end <= n_params:
            group_theta = theta[start:end]
            group_theta0 = theta0[start:end]
            group_moved = np.abs(group_theta - group_theta0) > 1e-6
            n_group_moved = np.sum(group_moved)
            n_group = end - start

            print(f"{group_name:12s} [{start:2d}:{end:2d}]: {n_group_moved:2d}/{n_group:2d} moved ({100*n_group_moved/n_group:5.1f}%)")

    # Save enhanced results
    enhanced_results = results.copy()
    if ll_null is not None:
        enhanced_results.update({
            'll_null': ll_null,
            'rho_squared': rho_squared,
            'rho_squared_adj': rho_squared_adj,
            'aic': aic,
            'bic': bic,
            'aic_per_obs': aic_per_obs,
        })

    # Save to new file
    enhanced_file = results_file.replace('.json', '_with_fit_stats.json')
    print(f"\n{'='*70}")
    print(f"Saving enhanced results to: {enhanced_file}")
    with open(enhanced_file, 'w') as f:
        json.dump(enhanced_results, f, indent=2)

    print(f"{'='*70}\n")

    return enhanced_results


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python compute_fit_statistics.py <results_file> [mnl_file]")
        sys.exit(1)

    results_file = sys.argv[1]
    mnl_file = sys.argv[2] if len(sys.argv) > 2 else None

    compute_fit_statistics(results_file, mnl_file)
