#!/usr/bin/env python
"""Diagnose non-significant preference shifters in M2d_type estimation."""

import pandas as pd
import numpy as np
from pathlib import Path

mnl_base = Path(r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016")
prefix = "fr_2016_RURO_mnl_job_gmm"

# Non-significant params from M2d_type:
# Singles male: beta_l_age2_sm (t=1.18), beta_l_educH_sm (t=-1.38)
# Singles female: beta_l_age_sf (t=-0.27), beta_l_age2_sf (t=0.75), beta_l_nkids_sf (t=-0.91)
# Couples female: beta_l_age2_f (t=-0.005), beta_l_nkids_f (t=-0.94)

print("=" * 80)
print("PREFERENCE SHIFTER DIAGNOSTICS")
print("Variables: age_norm, age_norm2, n_children, educH")
print("=" * 80)

# ---- SINGLES ----
fp = mnl_base / f"{prefix}__singles.parquet"
df_s = pd.read_parquet(fp)

# Split by gender
dgn = pd.to_numeric(df_s["dgn"], errors="coerce")
sm = df_s[dgn == 1].copy()
sf = df_s[dgn == 0].copy()

# Number of unique individuals (not just rows = individuals x draws)
for name, grp in [("SINGLES MALE", sm), ("SINGLES FEMALE", sf)]:
    n_rows = len(grp)
    n_persons = grp["idperson"].nunique() if "idperson" in grp.columns else "?"
    n_draws = grp["draw"].nunique() if "draw" in grp.columns else "?"
    n_chosen = (grp["is_chosen"] == 1).sum() if "is_chosen" in grp.columns else "?"

    print(f"\n{'='*80}")
    print(f"{name}")
    print(f"  Rows: {n_rows:,}  |  Unique persons: {n_persons}  |  Draws/person: {n_draws}  |  Chosen obs: {n_chosen}")
    print(f"{'='*80}")

    # Check each shifter variable
    for var in ["age_norm", "age_norm2", "n_children", "educH"]:
        if var not in grp.columns:
            print(f"\n  {var}: NOT IN DATA")
            continue

        vals = pd.to_numeric(grp[var], errors="coerce")

        # Key question: does this vary ACROSS individuals, or is it constant within person?
        # (If constant within person, effective N = n_persons, not n_rows)
        if "idperson" in grp.columns:
            person_means = grp.groupby("idperson")[var].first()  # value for each person
            n_unique_vals = person_means.nunique()
            person_std = person_means.std()
        else:
            n_unique_vals = vals.nunique()
            person_std = vals.std()

        print(f"\n  {var}:")
        print(f"    Mean:  {vals.mean():.4f}")
        print(f"    Std:   {vals.std():.4f}")
        print(f"    Min:   {vals.min():.4f}")
        print(f"    Max:   {vals.max():.4f}")
        print(f"    Unique values (per person): {n_unique_vals}")
        print(f"    Std across persons: {person_std:.4f}")

        if var == "n_children":
            print(f"    Nonzero: {(vals > 0).sum():,} ({100*(vals > 0).mean():.1f}%)")
            print(f"    Value counts:")
            for v, cnt in vals.value_counts().sort_index().head(8).items():
                print(f"      {v}: {cnt:,} ({100*cnt/len(vals):.1f}%)")

        if var == "educH":
            print(f"    educH=1: {(vals == 1).sum():,} ({100*(vals == 1).mean():.1f}%)")
            print(f"    educH=0: {(vals == 0).sum():,} ({100*(vals == 0).mean():.1f}%)")

# ---- COUPLES ----
fp = mnl_base / f"{prefix}__couples.parquet"
df_c = pd.read_parquet(fp)

for gender, label in [("male", "COUPLES MALE"), ("female", "COUPLES FEMALE")]:
    print(f"\n{'='*80}")
    print(f"{label}")

    n_rows = len(df_c)
    n_hh = df_c["idhh"].nunique() if "idhh" in df_c.columns else "?"
    n_draws = df_c["draw"].nunique() if "draw" in df_c.columns else "?"
    n_chosen = (df_c["is_chosen"] == 1).sum() if "is_chosen" in df_c.columns else "?"

    print(f"  Rows: {n_rows:,}  |  Unique HH: {n_hh}  |  Draws/HH: {n_draws}  |  Chosen obs: {n_chosen}")
    print(f"{'='*80}")

    for var_base in ["age_norm", "age_norm2", "n_children", "educH"]:
        var = f"{var_base}_{gender}"
        if var not in df_c.columns:
            # Try without suffix
            if var_base in df_c.columns:
                var = var_base
            else:
                print(f"\n  {var_base} ({var}): NOT IN DATA")
                continue

        vals = pd.to_numeric(df_c[var], errors="coerce")

        if "idhh" in df_c.columns:
            hh_vals = df_c.groupby("idhh")[var].first()
            n_unique_vals = hh_vals.nunique()
            hh_std = hh_vals.std()
        else:
            n_unique_vals = vals.nunique()
            hh_std = vals.std()

        print(f"\n  {var}:")
        print(f"    Mean:  {vals.mean():.4f}")
        print(f"    Std:   {vals.std():.4f}")
        print(f"    Min:   {vals.min():.4f}")
        print(f"    Max:   {vals.max():.4f}")
        print(f"    Unique values (per HH): {n_unique_vals}")
        print(f"    Std across HHs: {hh_std:.4f}")

        if "n_children" in var_base:
            print(f"    Nonzero: {(vals > 0).sum():,} ({100*(vals > 0).mean():.1f}%)")
            print(f"    Value counts:")
            for v, cnt in vals.value_counts().sort_index().head(8).items():
                print(f"      {v}: {cnt:,} ({100*cnt/len(vals):.1f}%)")

        if "educH" in var_base:
            print(f"    educH=1: {(vals == 1).sum():,} ({100*(vals == 1).mean():.1f}%)")
            print(f"    educH=0: {(vals == 0).sum():,} ({100*(vals == 0).mean():.1f}%)")

# ---- CORRELATION MATRIX ----
print(f"\n{'='*80}")
print("CORRELATION AMONG LEISURE SHIFTERS (chosen observations only)")
print(f"{'='*80}")

for name, grp, suffix in [
    ("SINGLES MALE", sm, ""),
    ("SINGLES FEMALE", sf, ""),
    ("COUPLES MALE", df_c, "_male"),
    ("COUPLES FEMALE", df_c, "_female"),
]:
    chosen = grp[grp["is_chosen"] == 1] if "is_chosen" in grp.columns else grp

    vars_to_check = []
    for vb in ["age_norm", "age_norm2", "n_children", "educH"]:
        v = f"{vb}{suffix}" if suffix and f"{vb}{suffix}" in chosen.columns else vb
        if v in chosen.columns:
            vars_to_check.append(v)

    if len(vars_to_check) >= 2:
        print(f"\n  {name} (N chosen = {len(chosen):,}):")
        corr = chosen[vars_to_check].apply(pd.to_numeric, errors="coerce").corr()
        print(corr.to_string())

print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
