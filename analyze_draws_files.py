#!/usr/bin/env python
"""Analyze draws files to see if column reduction is needed."""

import pandas as pd
from pathlib import Path

singles_path = Path("U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_RURO_draws.parquet")
couples_path = Path("U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_RURO_draws.parquet")

print("="*80)
print("DRAWS FILES ANALYSIS - Do They Need Reduction?")
print("="*80)

# Singles
print("\n### SINGLES DRAWS ###")
if singles_path.exists():
    df_singles = pd.read_parquet(singles_path)
    print(f"File: {singles_path.name}")
    print(f"Size: {singles_path.stat().st_size / (1024**2):.1f} MB")
    print(f"Rows: {len(df_singles):,}")
    print(f"Columns: {len(df_singles.columns):,}")
    
    # Categorize columns
    euromod_outputs = [c for c in df_singles.columns if c.startswith(('ils_', 'tin_', 'tsc_', 'bsa_', 'bun_', 'bho_', 'bfa_'))]
    euromod_internals = [c for c in df_singles.columns if c.startswith(('i_', 'il_', 'tu_'))]
    essential = [c for c in df_singles.columns if c not in euromod_outputs and c not in euromod_internals]
    
    print(f"\nColumn breakdown:")
    print(f"  EUROMOD outputs (ils_, tin_, etc.): {len(euromod_outputs)}")
    print(f"  EUROMOD internals (i_, il_, tu_): {len(euromod_internals)}")
    print(f"  Essential (IDs, demographics, draws): {len(essential)}")
    print(f"\nPotential reduction: {len(euromod_outputs) + len(euromod_internals)} columns can be removed")
    print(f"  → Would go from {len(df_singles.columns)} to ~{len(essential)} columns")
    
    print(f"\nFirst 30 columns:")
    for i, col in enumerate(df_singles.columns[:30], 1):
        category = "EUROMOD" if col in euromod_outputs else "INTERNAL" if col in euromod_internals else "ESSENTIAL"
        print(f"  {i:3d}. [{category:9s}] {col}")
    
    if len(euromod_outputs) > 0:
        print(f"\nSample EUROMOD output columns (should be in EUROMOD file, not draws):")
        for col in euromod_outputs[:10]:
            print(f"  - {col}")
    
    if len(euromod_internals) > 0:
        print(f"\nSample EUROMOD internal columns (not needed for MNL):")
        for col in euromod_internals[:10]:
            print(f"  - {col}")
else:
    print(f"File not found: {singles_path}")

# Couples
print("\n" + "="*80)
print("### COUPLES DRAWS ###")
if couples_path.exists():
    df_couples = pd.read_parquet(couples_path)
    print(f"File: {couples_path.name}")
    print(f"Size: {couples_path.stat().st_size / (1024**2):.1f} MB")
    print(f"Rows: {len(df_couples):,}")
    print(f"Columns: {len(df_couples.columns):,}")
    
    # Categorize columns
    euromod_outputs = [c for c in df_couples.columns if c.startswith(('ils_', 'tin_', 'tsc_', 'bsa_', 'bun_', 'bho_', 'bfa_'))]
    euromod_internals = [c for c in df_couples.columns if c.startswith(('i_', 'il_', 'tu_'))]
    essential = [c for c in df_couples.columns if c not in euromod_outputs and c not in euromod_internals]
    
    print(f"\nColumn breakdown:")
    print(f"  EUROMOD outputs (ils_, tin_, etc.): {len(euromod_outputs)}")
    print(f"  EUROMOD internals (i_, il_, tu_): {len(euromod_internals)}")
    print(f"  Essential (IDs, demographics, draws): {len(essential)}")
    print(f"\nPotential reduction: {len(euromod_outputs) + len(euromod_internals)} columns can be removed")
    print(f"  → Would go from {len(df_couples.columns)} to ~{len(essential)} columns")
else:
    print(f"File not found: {couples_path}")

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)
print("\nIf draws files contain EUROMOD outputs/internals:")
print("  ✓ YES - Column reduction is needed!")
print("  ✓ These columns are duplicates (already in combined_draws_em.parquet)")
print("  ✓ Reducing them will speed up Step 6 and reduce memory usage")
print("\nIf draws files only contain essential columns:")
print("  ✗ NO - Column reduction not needed")
print("  ✗ Draws files are already optimized")
print("="*80)

