#!/usr/bin/env python
"""Quick script to check n_children variation in MNL data."""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
from path_helpers import outputs_root  # noqa: E402

# Paths to the data files from the latest M2c run
data_dir = outputs_root() / "estimates/fr/spec/job_choice/gamspy/run_2026-02-19_10-48-35"

files = {
    "singles_male": data_dir / "data_singles_male.parquet",
    "singles_female": data_dir / "data_singles_female.parquet",
    "couples": data_dir / "data_couples.parquet",
}

print("=" * 80)
print("N_CHILDREN VARIATION CHECK")
print("=" * 80)

for group_name, file_path in files.items():
    if not file_path.exists():
        print(f"\n{group_name.upper()}: FILE NOT FOUND")
        continue

    # Read only the columns we need
    cols_to_read = ['n_children', 'educH', 'age_norm', 'age_norm2']

    # For couples, also check the gender-specific versions
    if group_name == "couples":
        cols_to_read.extend(['n_children_male', 'n_children_female'])

    # Load data
    df = pd.read_parquet(file_path)

    # Check which columns actually exist
    available_cols = [c for c in cols_to_read if c in df.columns]

    print(f"\n{group_name.upper()} (N={len(df):,} rows)")
    print("-" * 80)

    # n_children statistics
    if 'n_children' in df.columns:
        nkids = df['n_children']
        print(f"n_children:")
        print(f"  Mean:    {nkids.mean():.4f}")
        print(f"  Std:     {nkids.std():.4f}")
        print(f"  Min:     {nkids.min():.0f}")
        print(f"  Max:     {nkids.max():.0f}")
        print(f"  Nonzero: {100 * (nkids > 0).mean():.2f}%")
        print(f"  Value counts (top 5):")
        for val, count in nkids.value_counts().head().items():
            pct = 100 * count / len(nkids)
            print(f"    {val:.0f}: {count:,} ({pct:.2f}%)")

    # Couples: check gender-specific versions
    if group_name == "couples":
        for gender in ['male', 'female']:
            col = f'n_children_{gender}'
            if col in df.columns:
                nkids = df[col]
                print(f"\nn_children_{gender}:")
                print(f"  Mean:    {nkids.mean():.4f}")
                print(f"  Std:     {nkids.std():.4f}")
                print(f"  Min:     {nkids.min():.0f}")
                print(f"  Max:     {nkids.max():.0f}")
                print(f"  Nonzero: {100 * (nkids > 0).mean():.2f}%")

    # educH statistics
    if 'educH' in df.columns:
        educH = df['educH']
        print(f"\neducH:")
        print(f"  Mean:    {educH.mean():.4f} ({100 * educH.mean():.2f}% high-educated)")
        print(f"  Std:     {educH.std():.4f}")

    # age_norm statistics
    if 'age_norm' in df.columns:
        age_norm = df['age_norm']
        print(f"\nage_norm:")
        print(f"  Mean:    {age_norm.mean():.4f}")
        print(f"  Std:     {age_norm.std():.4f}")
        print(f"  Min:     {age_norm.min():.2f}")
        print(f"  Max:     {age_norm.max():.2f}")

    # For couples, check gender-specific age_norm
    if group_name == "couples":
        for gender in ['male', 'female']:
            col = f'age_norm_{gender}'
            if col in df.columns:
                age_norm = df[col]
                print(f"\nage_norm_{gender}:")
                print(f"  Mean:    {age_norm.mean():.4f}")
                print(f"  Std:     {age_norm.std():.4f}")

print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
