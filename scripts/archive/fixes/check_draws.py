#!/usr/bin/env python
"""
RURO DIAGNOSTICS FIX SUMMARY
============================

PROBLEM IDENTIFIED:
------------------
EUROMOD was ignoring our input `yem` (employment income) values for 
hypothetical RURO scenarios. Instead, EUROMOD used baseline `yem` values 
for all draws, causing:
1. `ils_dispy` (disposable income) to be CONSTANT within choice sets
2. Consumption to have ZERO variation across alternatives
3. Gradients for β_c and θ_c to be mathematically ZERO
4. These parameters stuck at initial values (1.0 and 0.5)

ROOT CAUSE:
-----------
EUROMOD has internal uprating/calculation rules that recalculate `yem` 
from historical data, ignoring our input values from `lhw * yivwg * weeks`.
While `lhw` and `yivwg` DO vary in EUROMOD output (we verified this),
`yem` and `ils_earns` remain stuck at baseline values.

SOLUTION IMPLEMENTED:
--------------------
In `RURO_prep_mnl_basic.py`, added `_fix_ils_dispy_for_ruro_earnings()`:

1. Compute our own RURO earnings: `ruro_earnings = lhw * yivwg * WEEKS_PER_MONTH`
2. Get EUROMOD's earnings (stuck at baseline): `euromod_earnings = ils_earns`  
3. Compute adjustment: `earnings_diff = ruro_earnings - euromod_earnings`
4. Correct disposable income: `ils_dispy = ils_dispy_euromod + earnings_diff`

This ensures `ils_dispy` reflects the actual hypothetical earnings in each 
RURO draw, not the baseline earnings that EUROMOD was stuck with.

RESULTS:
--------
BEFORE FIX:
- Consumption unique values per person: 1 (constant!)
- β_c and θ_c stuck at initial values

AFTER FIX:
- Consumption unique values per person: ~68 average, up to 100
- β_c and θ_c now being estimated with meaningful values:
  - Single males: β_c=-1.64, θ_c=1.71
  - Single females: β_c=-1.99, θ_c=1.71
  - Couples: β_c=0.01, θ_c=-0.54
- Wage opportunity σ improved from ~18 to ~8 (still needs work)
"""
import pandas as pd
import numpy as np

# Load and verify the fix
mnl_df = pd.read_parquet('U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl.parquet')

print("=== RURO FIX VERIFICATION ===")
print(f"Total rows: {len(mnl_df)}")

# Check singles consumption variation
singles = mnl_df[mnl_df['sample_group'] == 'singles']
cons_var = singles.groupby('idperson')['consumption'].nunique()
print(f"\nSingles consumption variation per person:")
print(f"  Mean unique values: {cons_var.mean():.1f}")
print(f"  Min: {cons_var.min()}, Max: {cons_var.max()}")
print(f"  Persons with variation: {(cons_var > 1).sum()} / {len(cons_var)}")

# Verify the fix columns exist
fix_cols = ['ruro_earnings', 'euromod_earnings', 'earnings_diff', 'ils_dispy_euromod']
present = [c for c in fix_cols if c in singles.columns]
print(f"\nFix diagnostic columns present: {present}")
