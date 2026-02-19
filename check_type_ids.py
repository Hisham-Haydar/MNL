#!/usr/bin/env python
"""Diagnose type_id variables in MNL data for M2d_type estimation."""

import pandas as pd
from pathlib import Path

mnl_base = Path(r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016")
prefix = "fr_2016_RURO_mnl_job_gmm"

print("=" * 80)
print("STEP 1: Check which type_id columns exist in the data")
print("=" * 80)

for group in ["singles", "couples"]:
    fp = mnl_base / f"{prefix}__{group}.parquet"
    if not fp.exists():
        print(f"\n{group}: FILE NOT FOUND at {fp}")
        continue
    df = pd.read_parquet(fp)
    type_cols = [c for c in df.columns if "type" in c.lower()]
    print(f"\n{group.upper()} ({len(df):,} rows, {len(df.columns)} cols)")
    print(f"  type-related columns: {type_cols}")

    for col in type_cols:
        vals = df[col].value_counts().sort_index()
        print(f"\n  {col}:")
        for v, cnt in vals.items():
            pct = 100 * cnt / len(df)
            print(f"    {v}: {cnt:,} ({pct:.1f}%)")

print("\n" + "=" * 80)
print("STEP 2: Check type_id dummy variables (type_id_0, type_id_1, type_id_2, type_id_3)")
print("=" * 80)

for group in ["singles", "couples"]:
    fp = mnl_base / f"{prefix}__{group}.parquet"
    if not fp.exists():
        continue
    df = pd.read_parquet(fp)
    print(f"\n{group.upper()}:")

    for k in range(4):
        col = f"type_id_{k}"
        if group == "couples":
            # Check both gender-specific and base
            for suffix in ["", "_male", "_female"]:
                c = f"type_id_{k}{suffix}"
                if c in df.columns:
                    n_nonzero = (df[c] != 0).sum()
                    pct = 100 * n_nonzero / len(df)
                    print(f"  {c}: {n_nonzero:,} nonzero ({pct:.1f}%), mean={df[c].mean():.4f}")
                else:
                    print(f"  {c}: NOT IN DATA")
        else:
            if col in df.columns:
                n_nonzero = (df[col] != 0).sum()
                pct = 100 * n_nonzero / len(df)
                print(f"  {col}: {n_nonzero:,} nonzero ({pct:.1f}%), mean={df[col].mean():.4f}")
            else:
                print(f"  {col}: NOT IN DATA")

print("\n" + "=" * 80)
print("STEP 3: Cross-tab type_id with working status")
print("=" * 80)

for group in ["singles", "couples"]:
    fp = mnl_base / f"{prefix}__{group}.parquet"
    if not fp.exists():
        continue
    df = pd.read_parquet(fp)
    print(f"\n{group.upper()}:")

    # Find the base type_id column
    type_col = None
    for candidate in ["type_id", "gmm_type", "type"]:
        if candidate in df.columns:
            type_col = candidate
            break
        # For couples, check gender-specific
        for suffix in ["_male", "_female"]:
            c = f"{candidate}{suffix}"
            if c in df.columns:
                type_col = c
                break

    if type_col is None:
        print("  No type_id column found!")
        continue

    working_col = "working" if "working" in df.columns else None
    if group == "couples":
        for wc in ["working_male", "working_female"]:
            if wc in df.columns:
                working_col = wc
                break

    if working_col:
        ct = pd.crosstab(df[type_col], df[working_col], margins=True)
        print(f"  Cross-tab {type_col} x {working_col}:")
        print(ct.to_string())
    else:
        print(f"  {type_col} value counts:")
        print(df[type_col].value_counts().sort_index().to_string())

print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
