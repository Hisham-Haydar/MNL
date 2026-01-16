#!/usr/bin/env python
"""Quick verification that reduce_mnl_columns.py has all essential columns."""

import sys
from pathlib import Path

# Add script directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts' / 'enhanced'))

from reduce_mnl_columns import (
    CORE_ID_COLS,
    DEMOGRAPHIC_COLS,
    LABOR_MARKET_COLS,
    EUROMOD_COLS,
    UTILITY_COLS,
    PRIOR_GSUR_COLS,
    METADATA_COLS,
)

print("="*80)
print("Column Reduction Script - Verification")
print("="*80)
print()

print("Column Categories:")
print(f"  Core IDs:       {len(CORE_ID_COLS):3d} columns")
print(f"  Demographics:   {len(DEMOGRAPHIC_COLS):3d} columns")
print(f"  Labor Market:   {len(LABOR_MARKET_COLS):3d} columns")
print(f"  EUROMOD:        {len(EUROMOD_COLS):3d} columns")
print(f"  Utility:        {len(UTILITY_COLS):3d} columns")
print(f"  Prior/GSUR:     {len(PRIOR_GSUR_COLS):3d} columns")
print(f"  Metadata:       {len(METADATA_COLS):3d} columns")

all_cols = (
    CORE_ID_COLS | DEMOGRAPHIC_COLS | LABOR_MARKET_COLS | 
    EUROMOD_COLS | UTILITY_COLS | PRIOR_GSUR_COLS | METADATA_COLS
)
print(f"  TOTAL:          {len(all_cols):3d} columns")
print()

print("Key Columns Verification:")
key_cols = {
    'Household ID': ['idhh', 'didp', 'idperson'],
    'Draw/Choice': ['draw', 'is_chosen'],
    'Labor': ['hours', 'wage', 'working', 'pexp_years'],
    'Utility': ['consumption', 'leisure', 'c_norm', 'l_norm'],
    'Demographics': ['age_norm', 'educL', 'educH', 'n_children', 'female'],
    'Prior/GSUR': ['prior', 'gsur'],
    'Occupation/Industry': ['loc4', 'loc4_1', 'loc4_2', 'loc4_3', 'loc4_4', 'lindi'],
    'Region': ['drgn1', 'reg_nuts1_2', 'reg_nuts1_3'],
}

all_present = True
for category, cols in key_cols.items():
    missing = [col for col in cols if col not in all_cols]
    if missing:
        print(f"  ✗ {category}: MISSING {missing}")
        all_present = False
    else:
        print(f"  ✓ {category}: All {len(cols)} columns present")

print()
if all_present:
    print("✅ ALL KEY COLUMNS PRESENT")
else:
    print("❌ SOME KEY COLUMNS MISSING")

print()
print("Sample columns from each category:")
for name, cols_set in [
    ('Core IDs', CORE_ID_COLS),
    ('Demographics', DEMOGRAPHIC_COLS),
    ('Labor', LABOR_MARKET_COLS),
]:
    sample = sorted(list(cols_set))[:5]
    print(f"  {name}: {', '.join(sample)}")

print("="*80)
