"""
Full Pipeline Interactive Runner - Steps 1-4 with Fixed Data Preparation

This script exposes all major functions from france_data_prep.py → RURO_prep.py →
RURO_draws.py → RURO_euromod.py as interactive cells.

Use in an IDE that supports #%% cells (VS Code, Spyder, PyCharm). Execute the
cells in order to reproduce Steps 1-4 of run_fr_2016_joint_only.ps1 while
inspecting intermediate outputs at each stage.

Benefits:
- Inspect EUROMOD labor market variables (lma, lun, lmc) after Step 1
- Verify worker identification logic in Step 2
- Check wage draw variation in Step 3
- Monitor ils_dispy variation in Step 4
"""

#%% Imports and sys.path setup
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import numpy as np

if "__file__" in globals():
    SCRIPT_DIR = Path(__file__).resolve().parent
else:
    SCRIPT_DIR = Path.cwd()

if str(SCRIPT_DIR) not in sys.path:
    sys.path.append(str(SCRIPT_DIR))

PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


#%% Configuration (edit paths/parameters as needed)
PROJECT_ROOT = Path(r"U:\Desktop\Nizam_Hisham\MNL").resolve()
DATA_ROOT = Path(r"U:\EUROMOD-STORAGE\Data").resolve()
RAW_DIR = DATA_ROOT / "raw"
PROC = DATA_ROOT / "processed" / "fr" / "2016"
SCENARIO_DIR = Path(r"U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016")
RAW_MICRODATA = RAW_DIR / "FR_2016.txt"
EUROMOD_ROOT = Path(r"U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+")

YEAR = 2016
SYSTEM_YEAR = 2015
COUNTRY = "FR"
N_DRAWS = 99
WAGE_SPEC = "vw"
RANDOM_SEED_SINGLES = 12345
RANDOM_SEED_COUPLES = 67890

PROC.mkdir(parents=True, exist_ok=True)
SCENARIO_DIR.mkdir(parents=True, exist_ok=True)

print(f"Configuration:")
print(f"  Project Root: {PROJECT_ROOT}")
print(f"  Data Root: {DATA_ROOT}")
print(f"  Raw Data: {RAW_MICRODATA}")
print(f"  Output: {PROC}")
print(f"  Year: {YEAR}, System: {SYSTEM_YEAR}")
print(f"  Draws: {N_DRAWS}, Wage Spec: {WAGE_SPEC}")


#%% ============================================================================
#   STEP 1: DATA PREPARATION (france_data_prep.py)
#   ============================================================================

print("\n" + "="*80)
print("STEP 1: DATA PREPARATION (france_data_prep.py)")
print("="*80)

from france_data_prep import prepare_one_year

# Run full data preparation with EUROMOD simulation
# This will use the FIXED merge logic to prioritize EUROMOD outputs!
out_dir, metadata = prepare_one_year(
    country=COUNTRY,
    year=YEAR,
    raw_filename=f"{COUNTRY}_{YEAR}.txt",
    system_year=SYSTEM_YEAR,
    raw_dir=RAW_DIR,
    out_dir=PROC,
)

print(f"\nStep 1 Complete!")
print(f"  Output directory: {out_dir}")
print(f"  Processed file: {PROC / f'fr_{YEAR}_processed.parquet'}")


#%% STEP 1 Inspection: Check EUROMOD Labor Market Variables

print("\n" + "-"*80)
print("INSPECTING STEP 1 OUTPUT: Labor Market Variables")
print("-"*80)

# Load the processed data
df_processed = pd.read_parquet(PROC / f"fr_{YEAR}_processed.parquet")

print(f"\nProcessed data shape: {df_processed.shape}")
print(f"Columns: {len(df_processed.columns)}")

# Check for labor market variables
labor_vars = ["lma", "lun", "lmc", "lhw", "lhw_a", "lhw_a1", "lhw_a_9", "lhw_a_20", "les", "lunmy"]
print(f"\nLabor Market Variables:")
for var in labor_vars:
    if var in df_processed.columns:
        std_val = df_processed[var].std() if df_processed[var].notna().any() else 0
        mean_val = df_processed[var].mean() if df_processed[var].notna().any() else 0
        nonzero = (df_processed[var] > 0).sum() if df_processed[var].notna().any() else 0
        print(f"  {var:12s}: EXISTS - mean={mean_val:8.2f}, std={std_val:8.4f}, nonzero={nonzero:6d}")
    else:
        print(f"  {var:12s}: MISSING")

# Check for duplicate columns
dup_cols = df_processed.columns[df_processed.columns.duplicated()].tolist()
if dup_cols:
    print(f"\n⚠️  WARNING: Duplicate columns found: {dup_cols}")
else:
    print(f"\n✅ No duplicate columns")

# Check ruro_decider distribution
if "ruro_decider" in df_processed.columns:
    decider_count = (df_processed["ruro_decider"] == 1).sum()
    print(f"\nRURO deciders: {decider_count:,} / {len(df_processed):,} ({decider_count/len(df_processed)*100:.1f}%)")


#%% STEP 1 Inspection: Compare lma vs les for Worker Identification

if "lma" in df_processed.columns and "les" in df_processed.columns:
    print("\n" + "-"*80)
    print("WORKER IDENTIFICATION: lma vs les")
    print("-"*80)

    # Create worker flags using both methods
    df_processed["worker_from_lma"] = (df_processed["lma"] == 1) & (df_processed["lhw"] > 0)
    df_processed["worker_from_les"] = (df_processed["les"] == 3) & (df_processed["lhw"] > 0)

    # Compare
    workers_lma = df_processed["worker_from_lma"].sum()
    workers_les = df_processed["worker_from_les"].sum()
    mismatch = (df_processed["worker_from_lma"] != df_processed["worker_from_les"]).sum()

    print(f"Workers identified by lma: {workers_lma:,}")
    print(f"Workers identified by les: {workers_les:,}")
    print(f"Mismatches: {mismatch:,} ({mismatch/len(df_processed)*100:.2f}%)")

    if mismatch > 0:
        print(f"\nInspecting mismatches (first 10):")
        mismatch_df = df_processed[df_processed["worker_from_lma"] != df_processed["worker_from_les"]]
        print(mismatch_df[["idperson", "lma", "les", "lhw", "worker_from_lma", "worker_from_les"]].head(10))


#%% ============================================================================
#   STEP 2: RURO PREPARATION (RURO_prep.py)
#   ============================================================================

print("\n" + "="*80)
print("STEP 2: RURO PREPARATION (RURO_prep.py)")
print("="*80)

from RURO_prep import (
    _resolve_processed_dir,
    _load_filtered_data,
    _add_ruro_variables_basic,
    _maybe_add_column,
)

processed_dir = _resolve_processed_dir(PROC, base_year=YEAR)
print(f"Resolved processed dir: {processed_dir}")

# Load singles and couples from Step 1 output
singles_df, couples_df = _load_filtered_data(processed_dir)
print(f"\nLoaded from Step 1:")
print(f"  Singles: {singles_df.shape}")
print(f"  Couples: {couples_df.shape}")


#%% STEP 2: Add RURO variables (Singles)

print("\n" + "-"*80)
print("Adding RURO Variables: SINGLES")
print("-"*80)

singles_ruro = _add_ruro_variables_basic(singles_df.copy(), default_year=YEAR)
_maybe_add_column(singles_ruro, "ruro_sample", 1)

print(f"Singles RURO shape: {singles_ruro.shape}")
print(f"Sample columns: {singles_ruro.columns.tolist()[:20]}")

# Check key RURO variables
ruro_vars = ["wage_ruro", "is_worker", "working", "working_pt1", "working_ft", "pexp", "educL", "educH"]
print(f"\nKey RURO variables (Singles):")
for var in ruro_vars:
    if var in singles_ruro.columns:
        if singles_ruro[var].dtype in [np.int64, np.float64]:
            mean_val = singles_ruro[var].mean()
            std_val = singles_ruro[var].std()
            print(f"  {var:15s}: mean={mean_val:8.2f}, std={std_val:8.4f}")
        else:
            print(f"  {var:15s}: dtype={singles_ruro[var].dtype}")


#%% STEP 2: Add RURO variables (Couples)

print("\n" + "-"*80)
print("Adding RURO Variables: COUPLES")
print("-"*80)

couples_ruro = _add_ruro_variables_basic(couples_df.copy(), default_year=YEAR)
_maybe_add_column(couples_ruro, "ruro_sample", 1)

print(f"Couples RURO shape: {couples_ruro.shape}")

# Check key RURO variables
print(f"\nKey RURO variables (Couples):")
for var in ruro_vars:
    if var in couples_ruro.columns:
        if couples_ruro[var].dtype in [np.int64, np.float64]:
            mean_val = couples_ruro[var].mean()
            std_val = couples_ruro[var].std()
            print(f"  {var:15s}: mean={mean_val:8.2f}, std={std_val:8.4f}")


#%% STEP 2: Write RURO_ready files

singles_out = processed_dir / "singles_RURO_ready.parquet"
couples_out = processed_dir / "couples_RURO_ready.parquet"

singles_ruro.to_parquet(singles_out, index=False)
couples_ruro.to_parquet(couples_out, index=False)

print(f"\nStep 2 Complete!")
print(f"  Wrote: {singles_out}")
print(f"  Wrote: {couples_out}")


#%% STEP 2 Inspection: Verify Worker Identification Uses lma

print("\n" + "-"*80)
print("WORKER IDENTIFICATION CHECK")
print("-"*80)

# Check if is_worker correlates with lma (if lma exists)
if "lma" in singles_ruro.columns and "is_worker" in singles_ruro.columns:
    correlation = singles_ruro["lma"].corr(singles_ruro["is_worker"])
    print(f"Singles: Correlation between lma and is_worker: {correlation:.4f}")
    print(f"  (Should be ~1.0 if using lma correctly)")

    # Cross-tabulation
    print(f"\nSingles: is_worker vs lma cross-tab:")
    print(pd.crosstab(singles_ruro["is_worker"], singles_ruro["lma"], margins=True))

if "lma" in couples_ruro.columns and "is_worker" in couples_ruro.columns:
    correlation = couples_ruro["lma"].corr(couples_ruro["is_worker"])
    print(f"\nCouples: Correlation between lma and is_worker: {correlation:.4f}")


#%% ============================================================================
#   STEP 3: GENERATE DRAWS (RURO_draws.py)
#   ============================================================================

print("\n" + "="*80)
print("STEP 3: GENERATE DRAWS (RURO_draws.py)")
print("="*80)

from RURO_draws import _attach_other_members_income, generate_draws_long

# Singles draws
print("\nGenerating Singles Draws...")
singles_ready = pd.read_parquet(singles_out)
singles_ready = _attach_other_members_income(singles_ready)
singles_draws = generate_draws_long(
    singles_ready,
    n_draws=N_DRAWS,
    wage_spec=WAGE_SPEC,
    rng_seed=RANDOM_SEED_SINGLES,
)
singles_draws_out = processed_dir / "singles_RURO_ready_RURO_draws.parquet"
singles_draws.to_parquet(singles_draws_out, index=False)

print(f"  Singles draws: {len(singles_draws):,} rows")
print(f"  Wrote: {singles_draws_out}")


#%% STEP 3: Couples Draws

print("\nGenerating Couples Draws...")
couples_ready = pd.read_parquet(couples_out)
couples_ready = _attach_other_members_income(couples_ready)
couples_draws = generate_draws_long(
    couples_ready,
    n_draws=N_DRAWS,
    wage_spec=WAGE_SPEC,
    rng_seed=RANDOM_SEED_COUPLES,
)
couples_draws_out = processed_dir / "couples_RURO_ready_RURO_draws.parquet"
couples_draws.to_parquet(couples_draws_out, index=False)

print(f"  Couples draws: {len(couples_draws):,} rows")
print(f"  Wrote: {couples_draws_out}")

print(f"\nStep 3 Complete!")


#%% STEP 3 Inspection: Check Draw Variation

print("\n" + "-"*80)
print("DRAW VARIATION CHECK")
print("-"*80)

# Sample a few persons and check variation
sample_person_singles = singles_draws["idperson"].iloc[0]
sample_data = singles_draws[singles_draws["idperson"] == sample_person_singles].sort_values("draw").head(10)

print(f"Singles Sample Person {sample_person_singles} (first 10 draws):")
cols_to_show = ["draw", "lhw", "yivwg", "yem"]
available_cols = [c for c in cols_to_show if c in sample_data.columns]
print(sample_data[available_cols].to_string(index=False))

# Check std across all draws for this person
person_draws = singles_draws[singles_draws["idperson"] == sample_person_singles]
for col in ["lhw", "yivwg", "yem"]:
    if col in person_draws.columns:
        std_val = person_draws[col].std()
        status = "VARIES" if std_val > 1e-6 else "CONSTANT"
        print(f"  {col} std: {std_val:.6f} ({status})")

# Check yem calculation: yem = wpm * lhw * yivwg
if all(c in person_draws.columns for c in ["lhw", "yivwg", "yem"]):
    wpm = 52 / 12  # weeks per month
    calculated_yem = person_draws["lhw"] * person_draws["yivwg"] * wpm
    actual_yem = person_draws["yem"]
    diff = (calculated_yem - actual_yem).abs().mean()
    print(f"\nYem calculation check (yem = wpm × lhw × yivwg):")
    print(f"  Mean absolute difference: {diff:.2f}")
    print(f"  Calculation is {'CORRECT' if diff < 1 else 'INCORRECT'}")


#%% ============================================================================
#   STEP 4: EUROMOD SIMULATION (RURO_euromod.py)
#   ============================================================================

print("\n" + "="*80)
print("STEP 4: EUROMOD SIMULATION (RURO_euromod.py)")
print("="*80)

from RURO_euromod import run_euromod_for_draws, _read_microdata_file

# Combine draws
singles_draws_df = pd.read_parquet(singles_draws_out)
couples_draws_df = pd.read_parquet(couples_draws_out)
combined_draws_df = pd.concat([singles_draws_df, couples_draws_df], ignore_index=True)

print(f"Combined draws shape: {combined_draws_df.shape}")


#%% STEP 4: Inspect Baseline Microdata

micro_template_df = _read_microdata_file(RAW_MICRODATA)
print(f"\nEUROMOD template columns (first 20): {micro_template_df.columns[:20].tolist()}")
print(f"Total template columns: {len(micro_template_df.columns)}")


#%% STEP 4: Run EUROMOD

print("\nRunning EUROMOD simulation...")
print("This may take 3-5 minutes...")

combined_output_path = run_euromod_for_draws(
    combined_draws_df,
    RAW_MICRODATA,
    country=COUNTRY,
    system_code=f"{COUNTRY}_{SYSTEM_YEAR}",
    dataset_name=f"{COUNTRY}_{YEAR}",
    em_root=EUROMOD_ROOT,
    scenario_dir=SCENARIO_DIR,
)

print(f"\nStep 4 Complete!")
print(f"  EUROMOD output: {combined_output_path}")


#%% STEP 4 Inspection: Check ils_dispy Variation!

print("\n" + "-"*80)
print("CRITICAL CHECK: ils_dispy VARIATION")
print("-"*80)

df_em = pd.read_parquet(combined_output_path)
print(f"EUROMOD output shape: {df_em.shape}")

# Check ils_dispy variation per person
if "idperson_true" in df_em.columns and "ils_dispy" in df_em.columns:
    person_stats = df_em.groupby("idperson_true").agg({
        "ils_dispy": ["std", "mean", "count"],
        "yem": ["std", "mean"]
    })

    person_stats.columns = ["_".join(col).strip("_") for col in person_stats.columns]

    # Identify persons with constant vs varying ils_dispy
    constant_ils_dispy = person_stats[person_stats["ils_dispy_std"] < 1e-6]
    varying_ils_dispy = person_stats[person_stats["ils_dispy_std"] >= 1e-6]

    print(f"\nils_dispy Variation Summary:")
    print(f"  Total persons: {len(person_stats):,}")
    print(f"  Persons with CONSTANT ils_dispy: {len(constant_ils_dispy):,} ({len(constant_ils_dispy)/len(person_stats)*100:.1f}%)")
    print(f"  Persons with VARYING ils_dispy: {len(varying_ils_dispy):,} ({len(varying_ils_dispy)/len(person_stats)*100:.1f}%)")

    # Check how many constant ils_dispy have varying yem (the problem case)
    constant_ils_varying_yem = constant_ils_dispy[constant_ils_dispy["yem_std"] > 1]
    print(f"  Persons with constant ils_dispy BUT varying yem: {len(constant_ils_varying_yem):,} ({len(constant_ils_varying_yem)/len(person_stats)*100:.1f}%)")

    # Show examples of working vs broken
    print(f"\n✅ WORKING Examples (varying ils_dispy):")
    for pid in varying_ils_dispy.index[:3]:
        row = person_stats.loc[pid]
        print(f"  Person {pid}: ils_dispy std={row['ils_dispy_std']:.2f}, yem std={row['yem_std']:.2f}")

    print(f"\n❌ BROKEN Examples (constant ils_dispy with varying yem):")
    for pid in constant_ils_varying_yem.index[:3]:
        row = person_stats.loc[pid]
        print(f"  Person {pid}: ils_dispy std={row['ils_dispy_std']:.2f}, yem std={row['yem_std']:.2f}")

    # Overall assessment
    problem_rate = len(constant_ils_varying_yem) / len(person_stats) * 100
    if problem_rate < 10:
        print(f"\n🎉 SUCCESS! Problem rate is only {problem_rate:.1f}% (down from 58.2%!)")
    elif problem_rate < 30:
        print(f"\n✅ IMPROVEMENT! Problem rate is {problem_rate:.1f}% (was 58.2%)")
    else:
        print(f"\n⚠️  STILL PROBLEMATIC: {problem_rate:.1f}% have constant ils_dispy (was 58.2%)")
else:
    print("⚠️  Cannot check: missing idperson_true or ils_dispy columns")


#%% FINAL SUMMARY

print("\n" + "="*80)
print("PIPELINE INSPECTION COMPLETE")
print("="*80)

print(f"\nFiles Created:")
print(f"  Step 1: {PROC / f'fr_{YEAR}_processed.parquet'}")
print(f"  Step 2: {singles_out}")
print(f"  Step 2: {couples_out}")
print(f"  Step 3: {singles_draws_out}")
print(f"  Step 3: {couples_draws_out}")
print(f"  Step 4: {combined_output_path}")

print(f"\nNext Steps:")
print(f"  1. Review the ils_dispy variation check above")
print(f"  2. If improved (< 10% problem rate), proceed with Steps 5-7")
print(f"  3. If still problematic, investigate further")

print(f"\n✨ All cells executed successfully!")

# %%
