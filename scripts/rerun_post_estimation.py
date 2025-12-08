#!/usr/bin/env python3
"""
Rerun post-estimation analysis on existing estimation results.

Usage:
    python scripts/rerun_post_estimation.py
"""

import json
import logging
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.RURO_post_estimation import run_post_estimation, ParsedParameters

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
LOGGER = logging.getLogger(__name__)


def main():
    """Main function to run post-estimation."""
    # Paths
    project_root = Path(__file__).parent.parent
    year = 2016
    
    results_file = project_root / f'outputs/estimates/fr/{year}/fr_{year}_joint.json'
    mnl_file = Path(r'U:\EUROMOD-STORAGE\Data\processed\fr') / str(year) / f'fr_{year}_RURO_mnl.parquet'
    output_dir = project_root / f'outputs/estimates/fr/{year}/v2_cleaned'
    
    LOGGER.info("=" * 70)
    LOGGER.info("RERUNNING POST-ESTIMATION ANALYSIS")
    LOGGER.info("=" * 70)
    LOGGER.info(f"Results file: {results_file}")
    LOGGER.info(f"MNL file: {mnl_file}")
    LOGGER.info(f"Output dir: {output_dir}")
    
    # Check files exist
    if not results_file.exists():
        LOGGER.error(f"Results file not found: {results_file}")
        return 1
    
    # Load estimation results
    LOGGER.info("\nLoading estimation results...")
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    theta = np.array(results['theta'])
    param_names = results['param_names']
    log_likelihood = results.get('log_likelihood', results.get('final_ll', np.nan))
    
    LOGGER.info(f"  Parameters: {len(theta)}")
    LOGGER.info(f"  Log-likelihood: {log_likelihood:.4f}")
    
    # Load MNL data if available
    df_sm, df_sf, df_cou = None, None, None
    
    if mnl_file.exists():
        LOGGER.info("\nLoading MNL data...")
        df = pd.read_parquet(mnl_file)
        LOGGER.info(f"  Total observations: {len(df)}")
        
        # Split by group
        if 'group' in df.columns:
            df_sm = df[df['group'] == 1].copy() if 1 in df['group'].values else None
            df_sf = df[df['group'] == 2].copy() if 2 in df['group'].values else None
            df_cou = df[df['group'] == 10].copy() if 10 in df['group'].values else None
            
            if df_sm is not None:
                LOGGER.info(f"  Single males: {len(df_sm)}")
            if df_sf is not None:
                LOGGER.info(f"  Single females: {len(df_sf)}")
            if df_cou is not None:
                LOGGER.info(f"  Couples: {len(df_cou)}")
    else:
        LOGGER.warning(f"MNL file not found: {mnl_file}")
    
    # Run post-estimation
    LOGGER.info("\nRunning post-estimation...")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results_dict = run_post_estimation(
        theta=theta,
        param_names=param_names,
        log_likelihood=log_likelihood,
        df_sm=df_sm,
        df_sf=df_sf,
        df_cou=df_cou,
        out_dir=output_dir,
        std_errors=None,  # Will be computed if Hessian is available
        prefix='vw_joint_',
    )
    
    LOGGER.info("\nPost-estimation complete!")
    LOGGER.info(f"HTML report: {results_dict.get('html_report')}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
