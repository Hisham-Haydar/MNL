#!/usr/bin/env python
"""Debug script for post-estimation."""
import sys
sys.path.insert(0, 'scripts/enhanced')
import traceback
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')

from RURO_post_estimation_styled import run_styled_post_estimation
from pathlib import Path

try:
    run_styled_post_estimation(
        results_json_path=Path('outputs/estimates/fr/2016/estimation_results.json'),
        mnl_base=Path('U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl'),
        output_dir=Path('outputs/estimates/fr/2016/post_estimation_v3'),
    )
except Exception as e:
    print(f"\n{'='*60}")
    print("EXCEPTION CAUGHT:")
    print('='*60)
    traceback.print_exc()
    sys.exit(1)
