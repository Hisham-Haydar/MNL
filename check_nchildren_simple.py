#!/usr/bin/env python
"""Simple n_children variation check using Z: drive path."""

import pandas as pd
from pathlib import Path

# Use Z: drive path (works in PowerShell estimation commands)
mnl_base = Path("Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_job_gmm")

print("=" * 80)
print("N_CHILDREN VARIATION CHECK")
print(f"Data path: {mnl_base}")
print("=" * 80)

# Check each group
for group_name in ["singles_male", "singles_female", "couples"]:
    file_path = mnl_base / f"{group_name}.parquet"

    print(f"\n{'='*80}")
    print(f"{group_name.upper()}")
    print(f"{'='*80}")

    if not file_path.exists():
        print(f"FILE NOT FOUND: {file_path}")
        continue

    # Read only n_children column(s)
    df = pd.read_parquet(file_path)

    print(f"Total rows: {len(df):,}")

    # Check n_children (singles and couples base)
    if 'n_children' in df.columns:
        nkids = df['n_children']
        print(f"\nn_children:")
        print(f"  Mean:    {nkids.mean():.4f}")
        print(f"  Std:     {nkids.std():.4f}")
        print(f"  Min:     {nkids.min():.0f}")
        print(f"  Max:     {nkids.max():.0f}")
        print(f"  Nonzero: {100 * (nkids > 0).mean():.2f}%")
        print(f"\n  Value counts:")
        for val, count in nkids.value_counts().sort_index().items():
            pct = 100 * count / len(nkids)
            print(f"    {val:.0f}: {count:,} ({pct:.2f}%)")

    # For couples, check gender-specific versions
    if group_name == "couples":
        for gender in ['male', 'female']:
            col = f'n_children_{gender}'
            if col in df.columns:
                nkids = df[col]
                print(f"\n{col}:")
                print(f"  Mean:    {nkids.mean():.4f}")
                print(f"  Std:     {nkids.std():.4f}")
                print(f"  Min:     {nkids.min():.0f}")
                print(f"  Max:     {nkids.max():.0f}")
                print(f"  Nonzero: {100 * (nkids > 0).mean():.2f}%")

print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
