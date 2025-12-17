"""
Explicit Pipeline Runner - Steps 1-4 WITH INLINED FUNCTIONS

This script makes EVERY operation explicit with clear dataframe names:
- df_before_euromod_step1: What goes INTO EUROMOD in Step 1
- df_after_euromod_step1: What comes OUT of EUROMOD in Step 1
- df_before_euromod_step4: What goes INTO EUROMOD in Step 4
- df_after_euromod_step4: What comes OUT of EUROMOD in Step 4

All functions are inlined so you can see EXACTLY what's happening.
Perfect for debugging and understanding the data flow.

Use in VS Code with #%% cells. Execute cells sequentially.
"""

#%% Imports and Configuration
from __future__ import annotations

import sys
import os
from pathlib import Path

import pandas as pd
import numpy as np

# Setup pythonnet for EUROMOD
os.environ.setdefault("PYTHONNET_RUNTIME", "coreclr")

# Path setup
if "__file__" in globals():
    SCRIPT_DIR = Path(__file__).resolve().parent
else:
    SCRIPT_DIR = Path.cwd()

if str(SCRIPT_DIR) not in sys.path:
    sys.path.append(str(SCRIPT_DIR))

PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Configuration
YEAR = 2016
SYSTEM_YEAR = 2015
COUNTRY = "FR"
N_DRAWS = 99
WAGE_SPEC = "vw"
RANDOM_SEED_SINGLES = 12345
RANDOM_SEED_COUPLES = 67890
HOUSEHOLD_SAMPLE_SIZE = None  # set to None to disable sampling
RANDOM_SEED_SAMPLE = 24680
WEEKS_PER_MONTH = 52.0 / 12.0

DATA_ROOT = Path(r"U:\EUROMOD-STORAGE\Data")
RAW_MICRODATA = DATA_ROOT / "raw" / f"{COUNTRY}_{YEAR}.txt"
EUROMOD_ROOT = Path(r"U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+")

print(f"Configuration:")
print(f"  Year: {YEAR}, System: {SYSTEM_YEAR}")
print(f"  Draws: {N_DRAWS}, Wage Spec: {WAGE_SPEC}")
print(f"  Seeds: Singles={RANDOM_SEED_SINGLES}, Couples={RANDOM_SEED_COUPLES}")


#%% ============================================================================
#   STEP 1: DATA PREPARATION - EXPLICIT VERSION
#   Returns: df_processed (full dataset after EUROMOD simulation)
#   ============================================================================

print("\n" + "="*80)
print("STEP 1: DATA PREPARATION (EXPLICIT)")
print("="*80)

import euromod as em

# 1.1 Load raw EUROMOD microdata
print("\n1.1 Loading raw EUROMOD microdata...")
df_raw_input = pd.read_csv(RAW_MICRODATA, sep="\t")
print(f"   df_raw_input: {df_raw_input.shape}")
print(f"   Columns: {list(df_raw_input.columns[:20])}...")

# 1.2 Setup EUROMOD
print("\n1.2 Setting up EUROMOD simulation...")
mod = em.Model(str(EUROMOD_ROOT))
country_mod = mod[COUNTRY]
eumod = country_mod[f"{COUNTRY}_{SYSTEM_YEAR}"]

# Find dataset
dataset = None
if hasattr(eumod, "datasets"):
    for ds in eumod.datasets:
        ds_name = getattr(ds, "name", str(ds))
        if str(YEAR) in ds_name:
            dataset = ds
            break

dataset_name = getattr(dataset, "name", f"{COUNTRY}_{YEAR}") if dataset else f"{COUNTRY}_{YEAR}"
print(f"   System: {COUNTRY}_{SYSTEM_YEAR}")
print(f"   Dataset: {dataset_name}")

# 1.3 CRITICAL INSPECTION: What goes INTO EUROMOD
print("\n1.3 📊 BEFORE EUROMOD SIMULATION:")
df_before_euromod_step1 = df_raw_input.copy()
print(f"   df_before_euromod_step1: {df_before_euromod_step1.shape}")
print(f"   Labor market variables in INPUT:")
for var in ["lma", "lun", "lmc", "lhw", "les"]:
    if var in df_before_euromod_step1.columns:
        std_val = df_before_euromod_step1[var].std()
        mean_val = df_before_euromod_step1[var].mean()
        print(f"     {var}: mean={mean_val:.2f}, std={std_val:.4f}")
    else:
        print(f"     {var}: ❌ MISSING")

# 1.4 RUN EUROMOD SIMULATION
print("\n1.4 ⏱️  Running EUROMOD simulation (30-60 seconds)...")
print("   (This runs EUROMOD tax-benefit calculations on the raw data)")
sim = eumod.run(df_before_euromod_step1, dataset_name)
df_after_euromod_step1 = sim.outputs[0]
#%% 
# 1.5 CRITICAL INSPECTION: What comes OUT of EUROMOD
print("\n1.5 📊 AFTER EUROMOD SIMULATION:")
print(f"   df_after_euromod_step1: {df_after_euromod_step1.shape}")
print(f"   Labor market variables in EUROMOD OUTPUT:")
for var in ["lma", "lun", "lmc", "lhw", "les"]:
    if var in df_after_euromod_step1.columns:
        std_val = df_after_euromod_step1[var].std()
        mean_val = df_after_euromod_step1[var].mean()
        status = "✅ VARIES" if std_val > 1e-6 else "⚠️  CONSTANT"
        print(f"     {var}: {status} mean={mean_val:.2f}, std={std_val:.4f}")
    else:
        print(f"     {var}: ❌ MISSING")

# 1.6 Add household structure flags (head/partner identification)
print("\n1.6 Adding household structure flags...")

# Find head ID column
head_id_col = None
for col in ["tu_household_fr_HeadID", "tu_hh_fr_HeadID", "tu_hh_HeadID"]:
    if col in df_after_euromod_step1.columns:
        head_id_col = col
        break

if head_id_col and "idperson" in df_after_euromod_step1.columns:
    df_after_euromod_step1["hh_IsHead"] = (
        df_after_euromod_step1[head_id_col] == df_after_euromod_step1["idperson"]
    ).astype(int)
else:
    # Fallback: first person in household
    df_after_euromod_step1["hh_IsHead"] = (
        df_after_euromod_step1.groupby("idhh").cumcount() == 0
    ).astype(int)

print(f"   Heads identified: {df_after_euromod_step1['hh_IsHead'].sum()}")

# Partner identification
if "idpartner" in df_after_euromod_step1.columns and head_id_col:
    head_info = df_after_euromod_step1[df_after_euromod_step1["hh_IsHead"] == 1][
        ["idhh", "idperson", "idpartner"]
    ].copy()
    head_info.rename(columns={"idperson": "head_id", "idpartner": "head_partner_id"}, inplace=True)

    df_after_euromod_step1 = df_after_euromod_step1.merge(
        head_info[["idhh", "head_id", "head_partner_id"]], on="idhh", how="left"
    )

    df_after_euromod_step1["hh_IsPartner"] = (
        (
            (df_after_euromod_step1["idperson"] == df_after_euromod_step1["head_partner_id"])
            | (df_after_euromod_step1["idpartner"] == df_after_euromod_step1["head_id"])
        )
        & (df_after_euromod_step1["hh_IsHead"] != 1)
    ).astype(int)

    df_after_euromod_step1.drop(columns=["head_id", "head_partner_id"], inplace=True)
else:
    df_after_euromod_step1["hh_IsPartner"] = 0

print(f"   Partners identified: {df_after_euromod_step1['hh_IsPartner'].sum()}")

# RURO decider flag
df_after_euromod_step1["ruro_decider"] = (
    (df_after_euromod_step1["hh_IsHead"] == 1) | (df_after_euromod_step1["hh_IsPartner"] == 1)
).astype(int)

print(f"   RURO deciders: {df_after_euromod_step1['ruro_decider'].sum()}")

# 1.7 CRITICAL FIX: Merge with original data, prioritizing EUROMOD outputs
print("\n1.7 Merging EUROMOD outputs with original data...")
print("   (Prioritizing EUROMOD simulation outputs over input values)")

# Get columns unique to original df (not in simulation)
df_only_cols = [c for c in df_before_euromod_step1.columns
                if c not in df_after_euromod_step1.columns and c != "idperson"]

print(f"   EUROMOD simulation columns: {len(df_after_euromod_step1.columns)}")
print(f"   Original-only columns: {len(df_only_cols)}")

# Merge: Keep ALL EUROMOD outputs, add unique original columns
df_processed = df_after_euromod_step1.merge(
    df_before_euromod_step1[["idperson"] + df_only_cols],
    on="idperson",
    how="left",
    suffixes=("", "_original")
)

# Remove duplicate columns
dup_cols = df_processed.columns[df_processed.columns.duplicated()].tolist()
if dup_cols:
    print(f"   Found {len(dup_cols)} duplicate columns, removing...")
    df_processed = df_processed.loc[:, ~df_processed.columns.duplicated()]

print(f"   df_processed: {df_processed.shape}")

# 1.8 Final check: Labor market variables
print("\n1.8 📊 FINAL DATA (after merge):")
labor_vars = ["lma", "lun", "lmc", "lhw", "les"]
for var in labor_vars:
    if var in df_processed.columns:
        std_val = df_processed[var].std() if df_processed[var].notna().any() else 0
        mean_val = df_processed[var].mean() if df_processed[var].notna().any() else 0
        nonzero = (df_processed[var] > 0).sum()
        status = "✅ VARIES" if std_val > 1e-6 else "⚠️  CONSTANT"
        print(f"  {var:8s}: {status} (mean={mean_val:7.2f}, std={std_val:7.4f}, nonzero={nonzero:6d})")
    else:
        print(f"  {var:8s}: ❌ MISSING")

print("\n✅ Step 1 Complete!")
print(f"   df_processed: {df_processed.shape}")
print(f"   Available for inspection: df_before_euromod_step1, df_after_euromod_step1, df_processed")

# Optional: down-sample households before draws/EUROMOD to speed up experimentation
if HOUSEHOLD_SAMPLE_SIZE:
    unique_hh = df_processed["idhh"].unique()
    sample_size = min(HOUSEHOLD_SAMPLE_SIZE, len(unique_hh))
    rng_sample = np.random.default_rng(RANDOM_SEED_SAMPLE)
    sampled_hhs = rng_sample.choice(unique_hh, size=sample_size, replace=False)
    df_processed_sampled = df_processed[df_processed["idhh"].isin(sampled_hhs)].copy()
    print(f"\n⚡ Household sampling enabled: selected {sample_size} households out of {len(unique_hh)} total.")
    print(f"   df_processed_sampled: {df_processed_sampled.shape}")
else:
    df_processed_sampled = df_processed


#%% STEP 1 Inspection: Worker Identification Comparison

print("\n" + "-"*80)
print("WORKER IDENTIFICATION: lma vs les")
print("-"*80)

if "lma" in df_processed.columns and "les" in df_processed.columns and "lhw" in df_processed.columns:
    worker_from_lma = (df_processed["lma"] == 1) & (df_processed["lhw"] > 0)
    worker_from_les = (df_processed["les"] == 3) & (df_processed["lhw"] > 0)

    workers_lma = worker_from_lma.sum()
    workers_les = worker_from_les.sum()
    mismatch = (worker_from_lma != worker_from_les).sum()

    print(f"Workers identified by lma: {workers_lma:,}")
    print(f"Workers identified by les: {workers_les:,}")
    print(f"Mismatches: {mismatch:,} ({mismatch/len(df_processed)*100:.2f}%)")

    if workers_lma > 0:
        print("\n✅ lma is working! Using lma for worker identification.")
    else:
        print("\n⚠️  lma all zeros - will use les fallback")
else:
    print("⚠️  Cannot compare - missing required columns")


#%% ============================================================================
#   STEP 2: RURO PREPARATION - SIMPLIFIED
#   Returns: singles_ruro, couples_ruro
#   ============================================================================

print("\n" + "="*80)
print("STEP 2: RURO PREPARATION")
print("="*80)

# Import needed functions
from RURO_prep import _add_ruro_variables_basic, _maybe_add_column
from france_data_prep import separate_household_types

# Separate into singles and couples
print("Separating household types...")
couples_df, singles_df = separate_household_types(df_processed_sampled)
print(f"  Singles: {singles_df.shape}")
print(f"  Couples: {couples_df.shape}")

# Add RURO variables
print("\nAdding RURO variables to singles...")
singles_ruro = _add_ruro_variables_basic(singles_df.copy(), default_year=YEAR)
_maybe_add_column(singles_ruro, "ruro_sample", 1)
print(f"  Singles RURO: {singles_ruro.shape}")

print("Adding RURO variables to couples...")
couples_ruro = _add_ruro_variables_basic(couples_df.copy(), default_year=YEAR)
_maybe_add_column(couples_ruro, "ruro_sample", 1)
print(f"  Couples RURO: {couples_ruro.shape}")

print("\n✅ Step 2 Complete!")


#%% ============================================================================
#   STEP 3: GENERATE DRAWS - SIMPLIFIED
#   Returns: singles_draws, couples_draws
#   ============================================================================

print("\n" + "="*80)
print("STEP 3: GENERATE DRAWS")
print("="*80)

from RURO_draws import _attach_other_members_income, generate_draws_long

# Singles draws
print("Generating singles draws...")
singles_ready = _attach_other_members_income(singles_ruro.copy())
singles_draws = generate_draws_long(
    singles_ready,
    n_draws=N_DRAWS,
    wage_spec=WAGE_SPEC,
    rng_seed=RANDOM_SEED_SINGLES,
)
print(f"  Singles draws: {singles_draws.shape[0]:,} rows")

# Couples draws
print("Generating couples draws...")
couples_ready = _attach_other_members_income(couples_ruro.copy())
couples_draws = generate_draws_long(
    couples_ready,
    n_draws=N_DRAWS,
    wage_spec=WAGE_SPEC,
    rng_seed=RANDOM_SEED_COUPLES,
)
print(f"  Couples draws: {couples_draws.shape[0]:,} rows")

print("\n✅ Step 3 Complete!")


#%% ============================================================================
#   STEP 4: EUROMOD SIMULATION ON DRAWS - EXPLICIT VERSION
#   Returns: combined_draws_em
#   ============================================================================

print("\n" + "="*80)
print("STEP 4: EUROMOD SIMULATION ON DRAWS (EXPLICIT)")
print("="*80)

# 4.1 Combine draws
print("\n4.1 Combining singles and couples draws...")
combined_draws = pd.concat([singles_draws, couples_draws], ignore_index=True)
print(f"   combined_draws: {combined_draws.shape}")

# 4.2 Load EUROMOD baseline microdata (template)
print("\n4.2 Loading EUROMOD template microdata...")
df_euromod_template = pd.read_csv(RAW_MICRODATA, sep="\t")
print(f"   df_euromod_template: {df_euromod_template.shape}")

# Store original template columns
original_template_cols = set(df_euromod_template.columns)
print(f"   Original template has {len(original_template_cols)} columns")
print(f"   ils_dispy in template: {'ils_dispy' in original_template_cols}")

# 4.3 Identify deciders vs non-deciders
print("\n4.3 Identifying deciders vs non-deciders...")

all_draws = sorted(combined_draws["draw"].unique())
max_draw = max(all_draws)
print(f"   Total draws: {len(all_draws)} (0 to {max_draw})")

# Deciders: have at least one draw > 0
person_max_draw = combined_draws.groupby("idperson")["draw"].max()
decider_ids = set(person_max_draw[person_max_draw > 0].index)
nondecider_ids = set(person_max_draw[person_max_draw == 0].index)

print(f"   Deciders (draw > 0): {len(decider_ids)} persons")
print(f"   Non-deciders (draw=0 only): {len(nondecider_ids)} persons")

# 4.4 Build full dataset for EUROMOD
print("\n4.4 Building EUROMOD input dataset...")

# Get override columns from draws
override_cols = ["idperson", "draw"]
for col in ["hours", "wage", "yem", "yivwg", "lhw"]:
    if col in combined_draws.columns:
        override_cols.append(col)

draws_sub = combined_draws[override_cols].copy()

# Merge deciders with draws
decider_draws = draws_sub[draws_sub["idperson"].isin(decider_ids)]
decider_merged = df_euromod_template.merge(
    decider_draws, on="idperson", how="inner", suffixes=("", "_draw")
)

print(f"   Decider rows after merge: {len(decider_merged)}")

# Replicate non-deciders for each draw
nondecider_baseline = df_euromod_template[df_euromod_template["idperson"].isin(nondecider_ids)].copy()

if len(nondecider_baseline) > 0 and max_draw > 0:
    nondecider_records = []
    for d in all_draws:
        nd_copy = nondecider_baseline.copy()
        nd_copy["draw"] = d
        # Non-deciders keep baseline hours/wage
        if "hours" not in nd_copy.columns and "lhw" in nd_copy.columns:
            nd_copy["hours"] = nd_copy["lhw"]
        if "wage" not in nd_copy.columns and "yivwg" in nd_copy.columns:
            nd_copy["wage"] = nd_copy["yivwg"]
        nondecider_records.append(nd_copy)
    nondecider_merged = pd.concat(nondecider_records, axis=0, ignore_index=True)
    print(f"   Non-decider rows (replicated): {len(nondecider_merged)}")
else:
    nondecider_merged = pd.DataFrame()

# Combine
if len(nondecider_merged) > 0:
    df_before_euromod_step4 = pd.concat([decider_merged, nondecider_merged], axis=0, ignore_index=True)
else:
    df_before_euromod_step4 = decider_merged

print(f"   df_before_euromod_step4: {df_before_euromod_step4.shape}")

# 4.5 Store true IDs and create draw-specific IDs
print("\n4.5 Creating draw-specific IDs...")

if "idhh" in df_before_euromod_step4.columns:
    df_before_euromod_step4["idhh_true"] = df_before_euromod_step4["idhh"]

df_before_euromod_step4["idperson_true"] = df_before_euromod_step4["idperson"]

draw = pd.to_numeric(df_before_euromod_step4["draw"], errors="coerce").fillna(0).astype(int)

# Create draw-specific IDs to avoid clashes
df_before_euromod_step4["idperson"] = df_before_euromod_step4["idperson_true"] * 1000 + draw

if "idhh" in df_before_euromod_step4.columns:
    df_before_euromod_step4["idhh"] = df_before_euromod_step4["idhh_true"] * 1000 + draw

# CRITICAL: Transform kin IDs (idfather, idmother, idpartner) too!
for kin_col in ["idfather", "idmother", "idpartner"]:
    if kin_col in df_before_euromod_step4.columns:
        kin_true_col = f"{kin_col}_true"
        df_before_euromod_step4[kin_true_col] = df_before_euromod_step4[kin_col]
        kin_raw = pd.to_numeric(df_before_euromod_step4[kin_col], errors="coerce").fillna(0).astype(int)
        df_before_euromod_step4[kin_col] = np.where(kin_raw > 0, kin_raw * 1000 + draw, 0)
        print(f"   Transformed {kin_col} (× 1000 + draw where > 0)")

print(f"   Created draw-specific IDs (× 1000 + draw)")

# 4.6 Apply hours/wage from draws (deciders only)
print("\n4.6 Applying hours/wage from RURO draws...")

is_decider = df_before_euromod_step4["idperson_true"].isin(decider_ids)
print(f"   Decider rows: {is_decider.sum()}")
print(f"   Non-decider rows: {(~is_decider).sum()}")

# Get lma (labor market active)
if "lma" in df_before_euromod_step4.columns:
    lma = pd.to_numeric(df_before_euromod_step4["lma"], errors="coerce").fillna(1).astype(int)
else:
    lma = pd.Series(1, index=df_before_euromod_step4.index)

# Hours from draws
if "hours_draw" in df_before_euromod_step4.columns:
    h = pd.to_numeric(df_before_euromod_step4["hours_draw"], errors="coerce").fillna(0.0)
elif "hours" in df_before_euromod_step4.columns:
    h = pd.to_numeric(df_before_euromod_step4["hours"], errors="coerce").fillna(0.0)
elif "lhw" in df_before_euromod_step4.columns:
    h = pd.to_numeric(df_before_euromod_step4["lhw"], errors="coerce").fillna(0.0)
else:
    h = pd.Series(0.0, index=df_before_euromod_step4.index)

# Wage from draws
if "wage_draw" in df_before_euromod_step4.columns:
    w = pd.to_numeric(df_before_euromod_step4["wage_draw"], errors="coerce").fillna(0.0)
elif "wage" in df_before_euromod_step4.columns:
    w = pd.to_numeric(df_before_euromod_step4["wage"], errors="coerce").fillna(0.0)
elif "yivwg" in df_before_euromod_step4.columns:
    w = pd.to_numeric(df_before_euromod_step4["yivwg"], errors="coerce").fillna(0.0)
else:
    w = pd.Series(0.0, index=df_before_euromod_step4.index)

# Get yem, yivwg, lhw from draws (with _draw suffix priority)
if "yem_draw" in df_before_euromod_step4.columns:
    yem_from_draws = pd.to_numeric(df_before_euromod_step4["yem_draw"], errors="coerce").fillna(0.0)
elif "yem" in df_before_euromod_step4.columns:
    yem_from_draws = pd.to_numeric(df_before_euromod_step4["yem"], errors="coerce").fillna(0.0)
else:
    yem_from_draws = h * w * WEEKS_PER_MONTH  # Calculate

if "yivwg_draw" in df_before_euromod_step4.columns:
    yivwg_from_draws = pd.to_numeric(df_before_euromod_step4["yivwg_draw"], errors="coerce").fillna(0.0)
elif "yivwg" in df_before_euromod_step4.columns:
    yivwg_from_draws = pd.to_numeric(df_before_euromod_step4["yivwg"], errors="coerce").fillna(0.0)
else:
    yivwg_from_draws = w.copy()

if "lhw_draw" in df_before_euromod_step4.columns:
    lhw_from_draws = pd.to_numeric(df_before_euromod_step4["lhw_draw"], errors="coerce").fillna(0.0)
elif "lhw" in df_before_euromod_step4.columns:
    lhw_from_draws = pd.to_numeric(df_before_euromod_step4["lhw"], errors="coerce").fillna(0.0)
else:
    lhw_from_draws = h.copy()

# Worker mask: decider + active + has hours
worker_mask = is_decider & (lma == 1) & (h > 0)

print(f"   Workers (will get mutated hours/wage): {worker_mask.sum()}")

# Apply mutations for workers
df_before_euromod_step4["lhw"] = np.where(worker_mask, lhw_from_draws, df_before_euromod_step4["lhw"])
df_before_euromod_step4["yivwg"] = np.where(worker_mask, yivwg_from_draws, df_before_euromod_step4["yivwg"])

# CRITICAL FIX: French system uses yem00 (regular) + yemxp (overtime)
# France: 35 hours/week standard, overtime above that
FRANCE_STANDARD_HOURS = 35.0

# Calculate regular and overtime income
regular_hours = np.minimum(lhw_from_draws, FRANCE_STANDARD_HOURS)
overtime_hours = np.maximum(lhw_from_draws - FRANCE_STANDARD_HOURS, 0)

yem00_from_draws = regular_hours * yivwg_from_draws * WEEKS_PER_MONTH
yemxp_from_draws = overtime_hours * yivwg_from_draws * WEEKS_PER_MONTH

# Set yem00 (CRITICAL - this is what EUROMOD uses in ils_dispy!)
if "yem00" in df_before_euromod_step4.columns:
    df_before_euromod_step4["yem00"] = np.where(worker_mask, yem00_from_draws, df_before_euromod_step4["yem00"])
    print(f"   ✅ Set yem00 (regular employment income) for {worker_mask.sum()} workers")
else:
    print(f"   ⚠️  WARNING: yem00 not in template columns!")

# Set yemxp (overtime pay)
if "yemxp" in df_before_euromod_step4.columns:
    df_before_euromod_step4["yemxp"] = np.where(worker_mask, yemxp_from_draws, df_before_euromod_step4["yemxp"])
    print(f"   ✅ Set yemxp (overtime pay) for {worker_mask.sum()} workers")
else:
    print(f"   ⚠️  WARNING: yemxp not in template columns!")

# Also set yem for compatibility (total = regular + overtime)
df_before_euromod_step4["yem"] = np.where(worker_mask, yem_from_draws, df_before_euromod_step4.get("yem", 0))

# Consistency fixes for workers
if "bun" in df_before_euromod_step4.columns:
    df_before_euromod_step4["bun"] = np.where(worker_mask, 0, df_before_euromod_step4["bun"])
if "bsa" in df_before_euromod_step4.columns:
    df_before_euromod_step4["bsa"] = np.where(worker_mask, 0, df_before_euromod_step4["bsa"])
if "yemmy" in df_before_euromod_step4.columns:
    df_before_euromod_step4["yemmy"] = np.where(worker_mask, 12, df_before_euromod_step4["yemmy"])
if "lunmy" in df_before_euromod_step4.columns:
    df_before_euromod_step4["lunmy"] = np.where(worker_mask, 0, df_before_euromod_step4["lunmy"])

print(f"   Applied mutations to workers")

# 4.7 CRITICAL: Filter to ONLY original template columns + Sort for EUROMOD
print("\n4.7 ⚠️  CRITICAL: Filtering to original template columns + Sorting...")
print(f"   Columns before filter: {len(df_before_euromod_step4.columns)}")

# CRITICAL: Keep ONLY columns that exist in original template
# Do NOT send metadata columns (draw, *_true) to EUROMOD!
cols_to_send = [c for c in df_before_euromod_step4.columns if c in original_template_cols]

df_euromod_input_filtered = df_before_euromod_step4[cols_to_send].copy()

print(f"   Columns after filter: {len(df_euromod_input_filtered.columns)}")
print(f"   ils_dispy in filtered input: {'ils_dispy' in df_euromod_input_filtered.columns}")

# CRITICAL: Sort by household and person ID (EUROMOD requirement!)
# EUROMOD expects data sorted by (idhh, idperson)
if "idhh" in df_euromod_input_filtered.columns and "idperson" in df_euromod_input_filtered.columns:
    print(f"\n   Sorting by (idhh, idperson)...")
    print(f"     Before sort: first 5 idhh values = {df_euromod_input_filtered['idhh'].head().tolist()}")

    df_euromod_input_filtered = df_euromod_input_filtered.sort_values(
        ["idhh", "idperson"]
    ).reset_index(drop=True)

    print(f"     After sort: first 5 idhh values = {df_euromod_input_filtered['idhh'].head().tolist()}")
    print(f"   ✅ Data sorted by household!")

    # Verify household sizes
    hh_sizes = df_euromod_input_filtered.groupby("idhh").size()
    max_hh_size = hh_sizes.max()
    print(f"\n   Household size check:")
    print(f"     Max household size: {max_hh_size} members")
    if max_hh_size > 50:
        print(f"     ⚠️  WARNING: {(hh_sizes > 50).sum()} households exceed 50 members!")
        print(f"     Largest households: {hh_sizes.nlargest(5).to_dict()}")
    else:
        print(f"     ✅ All households ≤ 50 members")
else:
    print(f"   ⚠️  WARNING: Cannot sort - missing idhh or idperson columns!")

# 4.8 CRITICAL INSPECTION: What goes INTO EUROMOD Step 4
print("\n4.8 📊 BEFORE EUROMOD STEP 4:")
print(f"   df_euromod_input_filtered: {df_euromod_input_filtered.shape}")
print(f"   Sample data check:")

# Show sample of the data being sent to EUROMOD
print(f"   First 5 rows (first few columns):")
cols_to_show = ["idhh", "idperson", "lhw", "yivwg", "yem"]
available = [c for c in cols_to_show if c in df_euromod_input_filtered.columns]
if available:
    print(df_euromod_input_filtered[available].head(10).to_string(index=False))

print(f"\n   Metadata preserved in df_before_euromod_step4 (not sent to EUROMOD):")
print(f"     Has idperson_true: {'idperson_true' in df_before_euromod_step4.columns}")
print(f"     Has idhh_true: {'idhh_true' in df_before_euromod_step4.columns}")
print(f"     Has draw: {'draw' in df_before_euromod_step4.columns}")

#%%

# 4.9 RUN EUROMOD SIMULATION ON DRAWS
print("\n4.9 ⏱️  Running EUROMOD simulation on draws (3-5 minutes)...")
print("   (This runs EUROMOD tax-benefit calculations on all hypothetical scenarios)")

sim_step4 = eumod.run(df_euromod_input_filtered, dataset_name)
df_after_euromod_step4 = sim_step4.outputs[0]
#%%

# 4.9b Restore metadata columns to output
print("\n4.9b Restoring metadata columns to EUROMOD output...")
# EUROMOD output doesn't have our metadata columns, so we need to merge them back
# The order should be preserved since we sorted, but let's merge to be safe
if "idperson" in df_after_euromod_step4.columns:
    # Create mapping from draw-specific IDs to metadata
    metadata_cols = ["idperson", "idperson_true", "idhh_true", "draw"]
    if all(c in df_before_euromod_step4.columns for c in metadata_cols):
        id_map = df_before_euromod_step4[metadata_cols].drop_duplicates()
        df_after_euromod_step4 = df_after_euromod_step4.merge(
            id_map,
            on="idperson",
            how="left"
        )
        print(f"   ✅ Restored metadata: idperson_true, idhh_true, draw")
    else:
        print(f"   ⚠️  Cannot restore metadata - missing columns in df_before_euromod_step4")
#%% 
# 4.10 CRITICAL INSPECTION: What comes OUT of EUROMOD Step 4
print("\n4.10 📊 AFTER EUROMOD STEP 4:")
print(f"   df_after_euromod_step4: {df_after_euromod_step4.shape}")

# Check ils_dispy variation
if "ils_dispy" in df_after_euromod_step4.columns and "idperson_true" in df_after_euromod_step4.columns:
    print(f"\n   🎯 ils_dispy Variation Check:")
    person_stats = df_after_euromod_step4.groupby("idperson_true").agg({
        "ils_dispy": ["std", "mean", "count"]
    })
    person_stats.columns = ["_".join(col).strip("_") for col in person_stats.columns]

    constant_ils = person_stats[person_stats["ils_dispy_std"] < 1e-6]
    varying_ils = person_stats[person_stats["ils_dispy_std"] >= 1e-6]

    total = len(person_stats)
    const_count = len(constant_ils)
    varying_count = len(varying_ils)

    print(f"     Total persons: {total:,}")
    print(f"     Constant ils_dispy: {const_count:,} ({const_count/total*100:.1f}%)")
    print(f"     Varying ils_dispy:  {varying_count:,} ({varying_count/total*100:.1f}%)")

    if varying_count/total > 0.9:
        print(f"     🎉 SUCCESS! > 90% of persons have varying ils_dispy!")
    elif varying_count/total > 0.5:
        print(f"     ✅ GOOD! > 50% of persons have varying ils_dispy")
    else:
        print(f"     ⚠️  PROBLEM: < 50% of persons have varying ils_dispy")

# Store final result
combined_draws_em = df_after_euromod_step4.copy()

print("\n✅ Step 4 Complete!")
print(f"   combined_draws_em: {combined_draws_em.shape}")
print(f"   Available for inspection: df_before_euromod_step4, df_euromod_input_filtered, df_after_euromod_step4, combined_draws_em")


#%% FINAL SUMMARY

print("\n" + "="*80)
print("✨ PIPELINE COMPLETE - ALL CRITICAL DATAFRAMES AVAILABLE")
print("="*80)

print(f"\nAvailable DataFrames:")
print(f"\n  STEP 1:")
print(f"    df_raw_input:              {df_raw_input.shape if 'df_raw_input' in locals() else 'Not loaded'}")
print(f"    df_before_euromod_step1:   {df_before_euromod_step1.shape if 'df_before_euromod_step1' in locals() else 'Not loaded'}")
print(f"    df_after_euromod_step1:    {df_after_euromod_step1.shape if 'df_after_euromod_step1' in locals() else 'Not loaded'}")
print(f"    df_processed:              {df_processed.shape if 'df_processed' in locals() else 'Not loaded'}")

print(f"\n  STEP 2:")
print(f"    singles_ruro:              {singles_ruro.shape if 'singles_ruro' in locals() else 'Not loaded'}")
print(f"    couples_ruro:              {couples_ruro.shape if 'couples_ruro' in locals() else 'Not loaded'}")

print(f"\n  STEP 3:")
print(f"    singles_draws:             {singles_draws.shape if 'singles_draws' in locals() else 'Not loaded'}")
print(f"    couples_draws:             {couples_draws.shape if 'couples_draws' in locals() else 'Not loaded'}")
print(f"    combined_draws:            {combined_draws.shape if 'combined_draws' in locals() else 'Not loaded'}")

print(f"\n  STEP 4:")
print(f"    df_euromod_template:       {df_euromod_template.shape if 'df_euromod_template' in locals() else 'Not loaded'}")
print(f"    df_before_euromod_step4:   {df_before_euromod_step4.shape if 'df_before_euromod_step4' in locals() else 'Not loaded'}")
print(f"    df_euromod_input_filtered: {df_euromod_input_filtered.shape if 'df_euromod_input_filtered' in locals() else 'Not loaded'}")
print(f"    df_after_euromod_step4:    {df_after_euromod_step4.shape if 'df_after_euromod_step4' in locals() else 'Not loaded'}")
print(f"    combined_draws_em:         {combined_draws_em.shape if 'combined_draws_em' in locals() else 'Not loaded'}")

print(f"\n💡 Next Steps:")
print(f"  1. Inspect any dataframe using VS Code Data Wrangler or pandas")
print(f"  2. Check ils_dispy variation results above")
print(f"  3. Compare BEFORE vs AFTER EUROMOD dataframes")
print(f"  4. If successful, proceed to Steps 5-7 or export to files")

# %%
