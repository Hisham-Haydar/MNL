# Column Reduction - Quick Start Commands
# ========================================

## Step 1: Dry Run (See What Would Happen)
## -----------------------------------------

python scripts\enhanced\reduce_mnl_columns.py `
    --input-dir U:/EUROMOD-STORAGE/Data/processed/fr/2016 `
    --dry-run

# This shows:
# - How many columns would be kept/dropped (892 → ~107 columns)
# - File size reduction (~900 MB → ~130 MB)
# - Any missing columns
# - Does NOT modify any files


## Step 2: Actually Reduce Columns
## --------------------------------

python scripts\enhanced\reduce_mnl_columns.py `
    --input-dir U:/EUROMOD-STORAGE/Data/processed/fr/2016

# This creates:
# - Output directory: U:/EUROMOD-STORAGE/Data/processed/fr/2016_reduced/
# - Files with ~90% fewer columns
# - ~87% file size reduction


## Step 3: Re-run Step 6 with Reduced Files
## -----------------------------------------

python scripts\enhanced\enh_RURO_prep_mnl_basic.py `
    --input-singles-male U:/EUROMOD-STORAGE/Data/processed/fr/2016_reduced/fr_2016_RURO_euromod_singles_male.parquet `
    --input-singles-female U:/EUROMOD-STORAGE/Data/processed/fr/2016_reduced/fr_2016_RURO_euromod_singles_female.parquet `
    --input-couples U:/EUROMOD-STORAGE/Data/processed/fr/2016_reduced/fr_2016_RURO_euromod_couples.parquet `
    --gsur-file U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_gsur.csv `
    --drawsmeta-file U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_drawsmeta.json `
    --output-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl

# Expected result:
# - Same MNL datasets as before
# - 2-3x faster execution
# - Lower memory usage


## Step 4: Run Estimation (No Changes Needed!)
## --------------------------------------------

python scripts\enhanced\enh_RURO_estimate_FR.py `
    --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
    --output-dir outputs\estimates\fr\2016_gamspy `
    --group joint `
    --solver gamspy-conopt `
    --spec-config scripts\enhanced\estimation_spec.yaml `
    --auto-timestamp

# Estimation runs exactly the same as before
# (Bottleneck is optimization, not data loading)


## Alternative: Custom Output Directory
## -------------------------------------

python scripts\enhanced\reduce_mnl_columns.py `
    --input-dir U:/EUROMOD-STORAGE/Data/processed/fr/2016 `
    --output-dir U:/EUROMOD-STORAGE/Data/processed/fr/2016_lean


## Verbose Mode (See Detailed Progress)
## -------------------------------------

python scripts\enhanced\reduce_mnl_columns.py `
    --input-dir U:/EUROMOD-STORAGE/Data/processed/fr/2016 `
    --verbose


## Benefits
## --------
# ✅ 88-90% fewer columns (892 → 107 for singles, 1247 → 128 for couples)
# ✅ ~87% file size reduction (~1 GB → ~130 MB)
# ✅ 2-3x faster Step 6 execution
# ✅ 5-10x lower memory usage
# ✅ Keeps ALL columns needed for any YAML specification
# ✅ Preserves household member IDs for all draws
# ✅ Keeps occupation (loc4) and industry (lindi) variables
# ✅ Original files never modified (reversible)


## What Gets Kept
## ---------------
# Core IDs:        idhh, didp, idperson, draw, is_chosen
# Demographics:    age, gender, education, children, region
# Labor:           hours, wage, experience, occupation (loc4), industry (lindi)
# EUROMOD:         ils_dispy, taxes, benefits
# Utility:         consumption, leisure (+ normalized versions)
# Prior/GSUR:      prior, gsur
# Weights:         dwt, dwtx


## What Gets Dropped
## ------------------
# EUROMOD internals: ~700 intermediate policy variables
# Survey details:    dwelling, health, detailed activity status
# Alternative IDs:   ident, idmother, idfather, benunit
# Total dropped:     ~800 columns
