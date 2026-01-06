#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
quick_verify.py
===============

Quick verification of RURO pipeline outputs.

Run this on the server after pipeline execution.

Usage:
    python server/quick_verify.py
"""

from pathlib import Path
import pandas as pd
import json

# Paths (adjust if needed)
DRAWS_DIR = Path("U:/EUROMOD-STORAGE/Data/processed/fr/2016")
EUROMOD_OUTPUT = Path("U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016/combined_draws_em.parquet")

print("=" * 80)
print("RURO PIPELINE QUICK VERIFICATION")
print("=" * 80)

# 1. Check draws files
print("\n1. DRAWS FILES")
print("-" * 80)

singles_path = DRAWS_DIR / "singles_RURO_ready_RURO_draws.parquet"
if singles_path.exists():
    df_s = pd.read_parquet(singles_path)
    print(f"Singles: {len(df_s):,} rows, {len(df_s.columns)} columns")

    if "draw" in df_s.columns:
        draws = sorted(df_s["draw"].unique())
        print(f"  Draws: {draws} (n_draws={len(draws)})")

    if "is_decider" in df_s.columns and "idperson_true" in df_s.columns:
        person_decider = df_s.groupby("idperson_true")["is_decider"].max()
        n_dec = (person_decider == 1).sum()
        n_nondec = (person_decider == 0).sum()
        print(f"  Deciders: {n_dec:,} persons")
        print(f"  Non-deciders: {n_nondec:,} persons")

        if "draw" in df_s.columns:
            n_draws = len(draws)
            expected = n_dec * n_draws + n_nondec
            print(f"  Expected rows: {n_dec:,} × {n_draws} + {n_nondec:,} = {expected:,}")
            print(f"  Actual rows: {len(df_s):,}")
            if len(df_s) == expected:
                print("  ✅ Row count OK")
            else:
                print(f"  ⚠️  Mismatch: {len(df_s) - expected:+,}")

    # Check metadata
    meta_path = singles_path.parent / f"{singles_path.stem}__drawsmeta.json"
    if meta_path.exists():
        with open(meta_path) as f:
            meta = json.load(f)
        print(f"  Metadata: id_multiplier={meta.get('id_multiplier')}, script={meta.get('script')}")
    else:
        print("  ⚠️  No metadata sidecar")

else:
    print("❌ Singles file not found")

couples_path = DRAWS_DIR / "couples_RURO_ready_RURO_draws.parquet"
if couples_path.exists():
    df_c = pd.read_parquet(couples_path)
    print(f"\nCouples: {len(df_c):,} rows, {len(df_c.columns)} columns")

    if "draw" in df_c.columns:
        draws = sorted(df_c["draw"].unique())
        print(f"  Draws: {draws} (n_draws={len(draws)})")

    if "is_decider" in df_c.columns and "idperson_true" in df_c.columns:
        person_decider = df_c.groupby("idperson_true")["is_decider"].max()
        n_dec = (person_decider == 1).sum()
        n_nondec = (person_decider == 0).sum()
        print(f"  Deciders: {n_dec:,} persons")
        print(f"  Non-deciders: {n_nondec:,} persons")

        if "draw" in df_c.columns:
            n_draws = len(draws)
            expected = n_dec * n_draws + n_nondec
            print(f"  Expected rows: {n_dec:,} × {n_draws} + {n_nondec:,} = {expected:,}")
            print(f"  Actual rows: {len(df_c):,}")
            if len(df_c) == expected:
                print("  ✅ Row count OK")
            else:
                print(f"  ⚠️  Mismatch: {len(df_c) - expected:+,}")

# 2. Check EUROMOD output
print("\n2. EUROMOD OUTPUT")
print("-" * 80)

if EUROMOD_OUTPUT.exists():
    df_em = pd.read_parquet(EUROMOD_OUTPUT)
    print(f"Combined output: {len(df_em):,} rows, {len(df_em.columns)} columns")

    if "draw" in df_em.columns:
        draws = sorted(df_em["draw"].unique())
        print(f"  Draws: {draws} (n_draws={len(draws)})")

    if "idperson_true" in df_em.columns:
        print(f"  Unique persons: {df_em['idperson_true'].nunique():,}")

    # Check ils_dispy variation (sample 10 persons)
    if "ils_dispy" in df_em.columns and "idperson_true" in df_em.columns and "draw" in df_em.columns:
        import numpy as np

        sample_persons = df_em["idperson_true"].unique()[:10]
        print(f"\n  ils_dispy variation check (sample {len(sample_persons)} persons):")

        for pid in sample_persons:
            person_data = df_em[df_em["idperson_true"] == pid][["draw", "ils_dispy"]]
            if len(person_data) > 1:
                std = person_data["ils_dispy"].std()
                min_val = person_data["ils_dispy"].min()
                max_val = person_data["ils_dispy"].max()
                print(f"    Person {pid}: std={std:.2f}, range=[{min_val:.2f}, {max_val:.2f}]")

    # Check metadata
    meta_path = EUROMOD_OUTPUT.parent / f"{EUROMOD_OUTPUT.stem}__euromodmeta.json"
    if meta_path.exists():
        with open(meta_path) as f:
            meta = json.load(f)
        print(f"\n  Metadata:")
        print(f"    system={meta.get('system')}")
        print(f"    n_rows={meta.get('n_rows'):,}")
        print(f"    n_draws={meta.get('n_draws')}")
        print(f"    id_multiplier={meta.get('id_multiplier')}")
        print(f"    script={meta.get('script')}")
    else:
        print("  ⚠️  No EUROMOD metadata sidecar")

else:
    print("❌ EUROMOD output not found")

# 3. Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

total_persons = 0
if singles_path.exists():
    total_persons += df_s["idperson_true"].nunique()
if couples_path.exists():
    total_persons += df_c["idperson_true"].nunique()

print(f"Total unique persons in draws: {total_persons:,}")

if EUROMOD_OUTPUT.exists():
    print(f"Total rows in EUROMOD output: {len(df_em):,}")
    if "draw" in df_em.columns:
        n_draws = len(df_em["draw"].unique())
        expected = total_persons * n_draws
        print(f"Expected (all persons × draws): {total_persons:,} × {n_draws} = {expected:,}")
        if len(df_em) == expected:
            print("✅ Perfect match!")
        else:
            diff = len(df_em) - expected
            print(f"Difference: {diff:+,}")

print("\n✅ Quick verification complete!")




df = pd.read_parquet(r"U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016/combined_draws_em.parquet")

# baseline household size from draw=0
base_size = (
    df[df["draw"] == 0]
    .groupby("idhh_true")["idperson_true"]
    .nunique()
    .rename("base_n")
)

# size by (household, draw)
hd_size = (
    df.groupby(["idhh_true", "draw"])["idperson_true"]
    .nunique()
    .rename("n_hd")
    .reset_index()
    .merge(base_size.reset_index(), on="idhh_true", how="left")
)

bad = hd_size[hd_size["n_hd"] != hd_size["base_n"]]
print("Bad (idhh_true,draw) pairs:", len(bad))
print(bad.head(20))
print("Total rows in draws:", len(df))
