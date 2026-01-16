#!/usr/bin/env python
"""Quick test to count columns in reduce_mnl_columns.py"""

import sys
sys.path.insert(0, 'scripts/enhanced')

from reduce_mnl_columns import (
    CORE_ID_COLS,
    DEMOGRAPHIC_COLS,
    LABOR_MARKET_COLS,
    EUROMOD_COLS,
    UTILITY_COLS,
    PRIOR_GSUR_COLS,
    METADATA_COLS,
    POST_ESTIMATION_COLS
)

print("=" * 80)
print("COLUMN CATEGORIES IN REDUCE_MNL_COLUMNS.PY")
print("=" * 80)
print()
print(f"CORE_ID_COLS:          {len(CORE_ID_COLS):3d} columns")
print(f"DEMOGRAPHIC_COLS:      {len(DEMOGRAPHIC_COLS):3d} columns")
print(f"LABOR_MARKET_COLS:     {len(LABOR_MARKET_COLS):3d} columns")
print(f"EUROMOD_COLS:          {len(EUROMOD_COLS):3d} columns")
print(f"UTILITY_COLS:          {len(UTILITY_COLS):3d} columns")
print(f"PRIOR_GSUR_COLS:       {len(PRIOR_GSUR_COLS):3d} columns")
print(f"METADATA_COLS:         {len(METADATA_COLS):3d} columns")
print(f"POST_ESTIMATION_COLS:  {len(POST_ESTIMATION_COLS):3d} columns")
print("-" * 80)

all_cols = (CORE_ID_COLS | DEMOGRAPHIC_COLS | LABOR_MARKET_COLS | 
            EUROMOD_COLS | UTILITY_COLS | PRIOR_GSUR_COLS | 
            METADATA_COLS | POST_ESTIMATION_COLS)

print(f"TOTAL UNIQUE COLUMNS:  {len(all_cols):3d} columns")
print()
print("This is the BASE set of columns BEFORE adding YAML-specific variables.")
print("The actual reduced dataset will have a few more columns from YAML specs.")
print("=" * 80)
