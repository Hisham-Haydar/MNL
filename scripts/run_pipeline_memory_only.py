"""
Memory-Only Pipeline Interactive Runner - Steps 1-4

No intermediate file writes! All dataframes kept in memory for fast iteration.
Perfect for debugging and inspection without disk I/O overhead.

Use in VS Code with #%% cells. Execute cells sequentially.
"""

#%% Imports and Configuration
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import numpy as np

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

DATA_ROOT = Path(r"U:\EUROMOD-STORAGE\Data")
RAW_MICRODATA = DATA_ROOT / "raw" / f"{COUNTRY}_{YEAR}.txt"
EUROMOD_ROOT = Path(r"U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+")

print(f"Configuration:")
print(f"  Year: {YEAR}, System: {SYSTEM_YEAR}")
print(f"  Draws: {N_DRAWS}, Wage Spec: {WAGE_SPEC}")
print(f"  Seeds: Singles={RANDOM_SEED_SINGLES}, Couples={RANDOM_SEED_COUPLES}")


#%% ============================================================================
#   STEP 1: DATA PREPARATION (france_data_prep.py)
#   Returns: df_processed (full dataset after EUROMOD simulation)
#   ============================================================================

print("\n" + "="*80)
print("STEP 1: DATA PREPARATION")
print("="*80)

# Ensure path setup also works when this cell is run standalone
if "SCRIPT_DIR" not in globals():
    if "__file__" in globals():
        SCRIPT_DIR = Path(__file__).resolve().parent
    else:
        SCRIPT_DIR = Path.cwd()
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.append(str(SCRIPT_DIR))
    PROJECT_ROOT = SCRIPT_DIR.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.append(str(PROJECT_ROOT))

from france_data_prep import prepare_one_year, separate_household_types

# Run full data preparation with FIXED merge logic
print("Running france_data_prep.py with FIXED merge logic...")
print("(EUROMOD simulation may take 30-60 seconds)")
print("\nNote: Step 1 writes to disk (EUROMOD requirement), but loads into memory immediately.")
print("      Steps 2-4 will be fully in-memory with no file writes.")

# Run prepare_one_year - this MUST write to disk because EUROMOD needs actual files
out_dir, metadata = prepare_one_year(
    country=COUNTRY,
    year=YEAR,
    raw_filename=f"{COUNTRY}_{YEAR}.txt",
    system_year=SYSTEM_YEAR,
    raw_dir=DATA_ROOT / "raw",
    out_dir=DATA_ROOT / "processed" / "fr" / str(YEAR),
)

# Load the processed data into memory immediately
processed_file = Path(metadata["export_result"]["data_path"])
df_processed = pd.read_parquet(processed_file)
print(f"\n✅ Loaded into memory: {df_processed.shape}")
print(f"   (Loaded from: {processed_file})")
print(f"   File stays on disk but all further operations are in-memory.")

# Check labor market variables
print("\n📊 Labor Market Variables Check:")
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
print("   (Data in memory, temp files cleaned up)")


#%% STEP 1 Inspection: Worker Identification Comparison

print("\n" + "-"*80)
print("WORKER IDENTIFICATION: lma vs les")
print("-"*80)

if "lma" in df_processed.columns and "les" in df_processed.columns and "lhw" in df_processed.columns:
    # Create worker flags using both methods
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
#   STEP 2: RURO PREPARATION
#   Returns: singles_ruro, couples_ruro
#   ============================================================================

print("\n" + "="*80)
print("STEP 2: RURO PREPARATION")
print("="*80)

from RURO_prep import _add_ruro_variables_basic, _maybe_add_column

# Separate into singles and couples (separate_household_types already imported above)
print("Separating household types...")
couples_df, singles_df = separate_household_types(df_processed)
print(f"  Singles: {singles_df.shape}")
print(f"  Couples: {couples_df.shape}")

# Add RURO variables - Singles
print("\nAdding RURO variables to singles...")
singles_ruro = _add_ruro_variables_basic(singles_df.copy(), default_year=YEAR)
_maybe_add_column(singles_ruro, "ruro_sample", 1)
print(f"  Singles RURO: {singles_ruro.shape}")

# Add RURO variables - Couples
print("Adding RURO variables to couples...")
couples_ruro = _add_ruro_variables_basic(couples_df.copy(), default_year=YEAR)
_maybe_add_column(couples_ruro, "ruro_sample", 1)
print(f"  Couples RURO: {couples_ruro.shape}")

# Check key RURO variables
print("\n📊 Key RURO Variables:")
ruro_vars = ["wage_ruro", "is_worker", "working", "pexp", "educL", "educH"]
for var in ruro_vars:
    if var in singles_ruro.columns:
        if singles_ruro[var].dtype in [np.int64, np.float64]:
            mean_val = singles_ruro[var].mean()
            std_val = singles_ruro[var].std()
            print(f"  {var:15s}: mean={mean_val:7.2f}, std={std_val:7.4f}")

print("\n✅ Step 2 Complete!")
print(f"   singles_ruro: {singles_ruro.shape}")
print(f"   couples_ruro: {couples_ruro.shape}")


#%% STEP 2 Inspection: is_worker Correlation with lma

print("\n" + "-"*80)
print("WORKER FLAG VALIDATION")
print("-"*80)

if "lma" in singles_ruro.columns and "is_worker" in singles_ruro.columns:
    correlation = singles_ruro["lma"].corr(singles_ruro["is_worker"])
    print(f"Singles: Correlation(lma, is_worker) = {correlation:.4f}")
    print(f"  (Should be ~1.0 if using lma correctly)")

    # Cross-tab
    print(f"\nCross-tabulation:")
    crosstab = pd.crosstab(singles_ruro["is_worker"], singles_ruro["lma"], margins=True)
    print(crosstab)

    if correlation > 0.95:
        print("\n✅ Strong correlation - is_worker correctly uses lma!")
    else:
        print(f"\n⚠️  Weak correlation - may be using les fallback")


#%% ============================================================================
#   STEP 3: GENERATE DRAWS
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
print(f"   singles_draws: {singles_draws.shape}")
print(f"   couples_draws: {couples_draws.shape}")


#%% STEP 3 Inspection: Check Draw Variation

print("\n" + "-"*80)
print("DRAW VARIATION CHECK")
print("-"*80)

# Sample one person
sample_person = singles_draws["idperson"].iloc[0]
person_data = singles_draws[singles_draws["idperson"] == sample_person].sort_values("draw").head(10)

print(f"Sample Person {sample_person} (first 10 draws):")
cols_to_show = ["draw", "lhw", "yivwg", "yem"]
available_cols = [c for c in cols_to_show if c in person_data.columns]
print(person_data[available_cols].to_string(index=False))

# Check std
person_all_draws = singles_draws[singles_draws["idperson"] == sample_person]
print(f"\nVariation across all {len(person_all_draws)} draws:")
for col in ["lhw", "yivwg", "yem"]:
    if col in person_all_draws.columns:
        std_val = person_all_draws[col].std()
        status = "✅ VARIES" if std_val > 1e-6 else "⚠️  CONSTANT"
        print(f"  {col:6s}: std={std_val:10.4f} {status}")

# Check yem calculation
if all(c in person_all_draws.columns for c in ["lhw", "yivwg", "yem"]):
    wpm = 52 / 12
    calculated_yem = person_all_draws["lhw"] * person_all_draws["yivwg"] * wpm
    actual_yem = person_all_draws["yem"]
    diff = (calculated_yem - actual_yem).abs().mean()
    status = "✅ CORRECT" if diff < 1 else "⚠️  INCORRECT"
    print(f"\nYem calculation (yem = wpm × lhw × yivwg):")
    print(f"  Mean absolute difference: {diff:.2f} {status}")


#%% ============================================================================
#   STEP 4: EUROMOD SIMULATION ON DRAWS
#   Returns: combined_draws_em
#   ============================================================================

print("\n" + "="*80)
print("STEP 4: EUROMOD SIMULATION ON DRAWS")
print("="*80)

from RURO_euromod import run_euromod_for_draws

# Combine draws
combined_draws = pd.concat([singles_draws, couples_draws], ignore_index=True)
print(f"Combined draws: {combined_draws.shape}")

# Run EUROMOD (this takes 3-5 minutes)
print("\n⏱️  Running EUROMOD simulation (this takes 3-5 minutes)...")
print("   Creating scenarios and simulating...")

SCENARIO_DIR = Path(r"U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016")
SCENARIO_DIR.mkdir(parents=True, exist_ok=True)

combined_output_path = run_euromod_for_draws(
    combined_draws,
    RAW_MICRODATA,
    country=COUNTRY,
    system_code=f"{COUNTRY}_{SYSTEM_YEAR}",
    dataset_name=f"{COUNTRY}_{YEAR}",
    em_root=EUROMOD_ROOT,
    scenario_dir=SCENARIO_DIR,
)

# Load result into memory
print(f"\nLoading EUROMOD output into memory...")
combined_draws_em = pd.read_parquet(combined_output_path)
print(f"  EUROMOD output: {combined_draws_em.shape}")

print("\n✅ Step 4 Complete!")
print(f"   combined_draws_em: {combined_draws_em.shape}")


#%% STEP 4 CRITICAL CHECK: ils_dispy Variation! 🎯

print("\n" + "="*80)
print("🎯 CRITICAL CHECK: ils_dispy VARIATION")
print("="*80)

if "idperson_true" in combined_draws_em.columns and "ils_dispy" in combined_draws_em.columns:
    # Calculate variation per person
    person_stats = combined_draws_em.groupby("idperson_true").agg({
        "ils_dispy": ["std", "mean", "count"],
        "yem": ["std", "mean"]
    })

    person_stats.columns = ["_".join(col).strip("_") for col in person_stats.columns]

    # Classify persons
    constant_ils_dispy = person_stats[person_stats["ils_dispy_std"] < 1e-6]
    varying_ils_dispy = person_stats[person_stats["ils_dispy_std"] >= 1e-6]
    constant_ils_varying_yem = constant_ils_dispy[constant_ils_dispy["yem_std"] > 1]

    # Results
    total = len(person_stats)
    const_count = len(constant_ils_dispy)
    varying_count = len(varying_ils_dispy)
    problem_count = len(constant_ils_varying_yem)

    print(f"📊 Summary:")
    print(f"  Total persons: {total:,}")
    print(f"  Constant ils_dispy: {const_count:,} ({const_count/total*100:.1f}%)")
    print(f"  Varying ils_dispy:  {varying_count:,} ({varying_count/total*100:.1f}%)")
    print(f"  Problem cases (const ils_dispy + varying yem): {problem_count:,} ({problem_count/total*100:.1f}%)")

    # Assessment
    problem_rate = problem_count / total * 100
    print(f"\n🎯 Assessment:")
    if problem_rate < 10:
        print(f"   🎉 SUCCESS! Problem rate is only {problem_rate:.1f}%!")
        print(f"   ✅ Fix is working - down from 58.2%!")
    elif problem_rate < 30:
        print(f"   ✅ IMPROVEMENT! Problem rate is {problem_rate:.1f}% (was 58.2%)")
    else:
        print(f"   ⚠️  STILL PROBLEMATIC: {problem_rate:.1f}% (was 58.2%)")

    # Show examples
    print(f"\n✅ Working Examples (varying ils_dispy):")
    for pid in varying_ils_dispy.index[:3]:
        row = person_stats.loc[pid]
        print(f"   Person {pid}: ils_dispy std={row['ils_dispy_std']:.2f}, yem std={row['yem_std']:.2f}")

    if problem_count > 0:
        print(f"\n❌ Broken Examples (constant ils_dispy, varying yem):")
        for pid in constant_ils_varying_yem.index[:3]:
            row = person_stats.loc[pid]
            print(f"   Person {pid}: ils_dispy std={row['ils_dispy_std']:.2f}, yem std={row['yem_std']:.2f}")
else:
    print("⚠️  Cannot check - missing required columns")


#%% FINAL SUMMARY

print("\n" + "="*80)
print("✨ PIPELINE COMPLETE - ALL DATA IN MEMORY")
print("="*80)

print(f"\nAvailable DataFrames:")
print(f"  df_processed:       {df_processed.shape if 'df_processed' in locals() else 'Not loaded'}")
print(f"  singles_ruro:       {singles_ruro.shape if 'singles_ruro' in locals() else 'Not loaded'}")
print(f"  couples_ruro:       {couples_ruro.shape if 'couples_ruro' in locals() else 'Not loaded'}")
print(f"  singles_draws:      {singles_draws.shape if 'singles_draws' in locals() else 'Not loaded'}")
print(f"  couples_draws:      {couples_draws.shape if 'couples_draws' in locals() else 'Not loaded'}")
print(f"  combined_draws_em:  {combined_draws_em.shape if 'combined_draws_em' in locals() else 'Not loaded'}")

print(f"\n💡 Next Steps:")
print(f"  1. Review ils_dispy variation results above")
print(f"  2. If successful (< 10% problem rate), proceed to Steps 5-7")
print(f"  3. Explore any dataframe interactively in new cells")
print(f"  4. Export to files only when ready for full pipeline run")

# %%
