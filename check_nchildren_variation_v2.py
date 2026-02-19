#!/usr/bin/env python
"""Check n_children variation in MNL data files from latest M2c estimation."""

import pandas as pd
import numpy as np
from pathlib import Path

# Use data files from latest M2c estimation run
# (These are the actual files used in the problematic estimation)
data_dir = Path(r"Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016")

files = {
    "singles_male": data_dir / "fr_2016_RURO_mnl_job_gmm__singles.parquet",
    "singles_female": data_dir / "fr_2016_RURO_mnl_job_gmm__singles.parquet",
    "couples": data_dir / "fr_2016_RURO_mnl_job_gmm__couples.parquet",
}

print("=" * 80)
print("N_CHILDREN VARIATION CHECK")
print("Data source: M2c estimation run (2026-02-19_10-48-35)")
print("=" * 80)

for group_name, file_path in files.items():
    if not file_path.exists():
        print(f"\n{group_name.upper()}: FILE NOT FOUND at {file_path}")
        continue

    print(f"\nLoading {group_name} data...")

    # Read only n_children column to save memory
    df = pd.read_parquet(file_path, columns=['n_children'])

    print(f"\n{group_name.upper()} (N={len(df):,} rows)")
    print("-" * 80)

    nkids = df['n_children']
    print(f"n_children:")
    print(f"  Mean:    {nkids.mean():.4f}")
    print(f"  Std:     {nkids.std():.4f}")
    print(f"  Min:     {nkids.min():.0f}")
    print(f"  Max:     {nkids.max():.0f}")
    print(f"  Nonzero: {100 * (nkids > 0).mean():.2f}%")
    print(f"  Median:  {nkids.median():.0f}")
    print(f"\n  Value counts:")
    for val, count in nkids.value_counts().sort_index().items():
        pct = 100 * count / len(nkids)
        print(f"    {val:.0f} children: {count:,} ({pct:.2f}%)")

print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
