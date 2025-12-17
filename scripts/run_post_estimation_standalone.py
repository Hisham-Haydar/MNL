#!/usr/bin/env python
"""
Standalone Post-Estimation Script for Joint RURO Results

This script generates HTML diagnostics and statistics from an existing
estimation JSON file. It works around the limitations of CLI post-estimation.

Usage:
    python scripts/run_post_estimation_standalone.py
"""

import json
import logging
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from RURO_post_estimation import run_post_estimation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
LOGGER = logging.getLogger(__name__)

def main():
    """Run post-estimation analysis on saved joint estimation results."""

    # File paths
    results_file = Path('outputs/estimates/fr/2016/fr_2016_joint.json')
    mnl_file = Path('U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl.parquet')
    out_dir = Path('outputs/post_estimation/fr/2016/joint')

    # Create output directory
    out_dir.mkdir(parents=True, exist_ok=True)

    LOGGER.info("="*70)
    LOGGER.info("STANDALONE POST-ESTIMATION ANALYSIS")
    LOGGER.info("="*70)
    LOGGER.info(f"Results file: {results_file}")
    LOGGER.info(f"MNL dataset: {mnl_file}")
    LOGGER.info(f"Output directory: {out_dir}")

    # Load estimation results
    LOGGER.info("\nLoading estimation results...")
    with open(results_file, 'r') as f:
        results = json.load(f)

    theta = np.array(results['theta'])
    param_names = results['param_names']
    log_likelihood = results['log_likelihood']
    wage_spec = results.get('wage_spec', 'vw')
    n_individuals = results.get('n_individuals', results.get('n_sm', 0) + results.get('n_sf', 0) + results.get('n_cou', 0))
    theta0 = np.array(results.get('theta0', [0.0] * len(theta)))
    bounds = results.get('bounds', [(None, None)] * len(theta))
    estimation_time = results.get('estimation_time_seconds', 0.0)

    LOGGER.info(f"  Parameters: {len(theta)}")
    LOGGER.info(f"  Log-likelihood: {log_likelihood:,.4f}")
    LOGGER.info(f"  Wage spec: {wage_spec}")
    LOGGER.info(f"  Individuals: {n_individuals:,}")

    # Load MNL dataset
    LOGGER.info("\nLoading MNL dataset...")
    df = pd.read_parquet(mnl_file)
    LOGGER.info(f"  Rows: {len(df):,}")
    LOGGER.info(f"  Columns: {len(df.columns)}")

    # Split by group for post-estimation diagnostics
    LOGGER.info("\nSplitting dataset by group...")

    # Identify group column
    group_col = None
    for col in ['ruro_group', 'group', 'household_type']:
        if col in df.columns:
            group_col = col
            break

    if group_col is None:
        LOGGER.error("Could not find group column in dataset")
        LOGGER.info("Available columns (first 50):")
        LOGGER.info(f"  {df.columns[:50].tolist()}")
        raise ValueError("Group column not found")

    LOGGER.info(f"  Using group column: {group_col}")
    LOGGER.info(f"  Unique groups: {df[group_col].unique()}")

    # Split by group (1 = singles, 10 = couples)
    df_sm = df[df[group_col] == 1].copy() if 1 in df[group_col].values else None
    df_sf = df[df[group_col] == 1].copy() if 1 in df[group_col].values else None  # Will filter by sex if available
    df_cou = df[df[group_col] == 10].copy() if 10 in df[group_col].values else None

    # Further split singles by sex if sex column exists
    sex_col = None
    for col in ['sex', 'dgn', 'gender']:
        if col in df.columns:
            sex_col = col
            break

    if sex_col and df_sm is not None:
        # Check sex encoding (could be 1/2 or 'm'/'f')
        unique_sex = df[sex_col].unique()
        LOGGER.info(f"  Sex values: {unique_sex}")

        if 0 in unique_sex and 1 in unique_sex:
            # EUROMOD encoding (0=female, 1=male)
            df_sm = df[(df[group_col] == 1) & (df[sex_col] == 1)].copy()
            df_sf = df[(df[group_col] == 1) & (df[sex_col] == 0)].copy()
        elif 1 in unique_sex and 2 in unique_sex:
            # Alternative numeric encoding (1=male, 2=female)
            df_sm = df[(df[group_col] == 1) & (df[sex_col] == 1)].copy()
            df_sf = df[(df[group_col] == 1) & (df[sex_col] == 2)].copy()
        elif 'm' in unique_sex or 'f' in unique_sex:
            # String encoding
            df_sm = df[(df[group_col] == 1) & (df[sex_col] == 'm')].copy()
            df_sf = df[(df[group_col] == 1) & (df[sex_col] == 'f')].copy()

    LOGGER.info(f"  Single males: {len(df_sm) if df_sm is not None else 0:,} rows")
    LOGGER.info(f"  Single females: {len(df_sf) if df_sf is not None else 0:,} rows")
    LOGGER.info(f"  Couples: {len(df_cou) if df_cou is not None else 0:,} rows")

    # Sanity: replace NaN hours with 0 for couples to avoid NaN utilities
    if df_cou is not None:
        hour_cols = ['hours_male', 'hours_female', 'lhw_male', 'lhw_female', 'hours_m', 'hours_f', 'lhw_m', 'lhw_f']
        for col in hour_cols:
            if col in df_cou.columns:
                df_cou[col] = pd.to_numeric(df_cou[col], errors='coerce').fillna(0)

    # Note: Standard errors not available - will show as NaN
    std_errors = np.array(results.get('std_errors', [np.nan] * len(theta)))
    if np.all(np.isnan(std_errors)):
        LOGGER.warning("\nStandard errors not available (expected in joint estimation)")
        LOGGER.warning("  Reason: Gradient function not accessible after optimization")
        LOGGER.warning("  Impact: Parameter significance tests will not be available")

    # Run post-estimation analysis
    LOGGER.info("\nRunning post-estimation analysis...")
    LOGGER.info("-"*70)

    post_results = run_post_estimation(
        theta=theta,
        param_names=param_names,
        log_likelihood=log_likelihood,
        df_sm=df_sm,
        df_sf=df_sf,
        df_cou=df_cou,
        out_dir=out_dir,
        std_errors=std_errors if not np.all(np.isnan(std_errors)) else None,
        prefix=f'{wage_spec}_pooled_',
        n_individuals=n_individuals,
        param_bounds=dict(zip(param_names, bounds)) if bounds else None,
        initial_values=dict(zip(param_names, theta0)) if len(theta0) == len(theta) else None,
        wage_spec=wage_spec,
    )

    LOGGER.info("\n" + "="*70)
    LOGGER.info("POST-ESTIMATION COMPLETE")
    LOGGER.info("="*70)
    LOGGER.info(f"\nHTML Report: {post_results['html_report']}")
    LOGGER.info(f"Parameters CSV: {post_results['param_csv']}")
    LOGGER.info(f"Elasticities CSV: {post_results['elasticities_csv']}")
    LOGGER.info(f"\nDiagnostic plots:")
    for name, path in post_results['plot_paths'].items():
        LOGGER.info(f"  {name}: {path}")

    # Show key fit statistics
    fit_stats = post_results['fit_stats']
    LOGGER.info(f"\nModel Fit Statistics:")
    LOGGER.info(f"  Log-likelihood: {fit_stats['log_likelihood']:,.4f}")
    if 'rho_squared' in fit_stats:
        LOGGER.info(f"  Rho-squared: {fit_stats['rho_squared']:.4f}")
    LOGGER.info(f"  AIC: {fit_stats['AIC']:,.4f}")
    LOGGER.info(f"  BIC: {fit_stats['BIC']:,.4f}")

    LOGGER.info("\nDone!")


if __name__ == '__main__':
    main()
