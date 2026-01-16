# Test Column Reduction Script - Dry Run
# =======================================
# Run this to see what the column reduction would do WITHOUT modifying any files

python scripts\enhanced\reduce_mnl_columns.py `
    --input-dir U:/EUROMOD-STORAGE/Data/processed/fr/2016 `
    --dry-run

# Expected output:
# ================================================================================
# MNL Dataset Column Reduction
# ================================================================================
# Input directory: U:/EUROMOD-STORAGE/Data/processed/fr/2016
# Output directory: U:/EUROMOD-STORAGE/Data/processed/fr/2016_reduced
# Spec directory: u:\Desktop\Nizam_Hisham\MNL\scripts\enhanced
# DRY RUN MODE - No files will be written
#
# Found 4 YAML specifications:
#   - estimation_spec.yaml
#   - estimation_spec_AC2013.yaml
#   - estimation_spec_loc_empirical.yaml
#   - estimation_spec_v2.yaml
#
# Analyzing required columns...
#   Analyzing estimation_spec.yaml...
#     Found 35 variables
#   Analyzing estimation_spec_AC2013.yaml...
#     Found 32 variables
#   Analyzing estimation_spec_loc_empirical.yaml...
#     Found 39 variables
#   Analyzing estimation_spec_v2.yaml...
#     Found 35 variables
# Total required columns: 107
#
# Processing Singles Male...
# Reading fr_2016_RURO_euromod_singles_male.parquet...
#   Original columns: 892
#   Kept columns: 107
#   Dropped columns: 785
#   Reduction: 88.0%
#   [DRY RUN] Original size: 245.3 MB
#   [DRY RUN] Estimated reduced size: 32.1 MB
#   [DRY RUN] Estimated compression: 7.64x
#
# Processing Singles Female...
# Reading fr_2016_RURO_euromod_singles_female.parquet...
#   Original columns: 892
#   Kept columns: 107
#   Dropped columns: 785
#   Reduction: 88.0%
#   [DRY RUN] Original size: 312.7 MB
#   [DRY RUN] Estimated reduced size: 41.2 MB
#   [DRY RUN] Estimated compression: 7.59x
#
# Processing Couples...
# Reading fr_2016_RURO_euromod_couples.parquet...
#   Original columns: 1247
#   Kept columns: 128
#   Dropped columns: 1119
#   Reduction: 89.7%
#   [DRY RUN] Original size: 487.9 MB
#   [DRY RUN] Estimated reduced size: 58.4 MB
#   [DRY RUN] Estimated compression: 8.35x
#
# ================================================================================
# SUMMARY
# ================================================================================
# Singles Male:
#   Columns: 892 → 107 (88.0% reduction)
#   Size: 245.3 MB → 32.1 MB (7.64x compression)
#
# Singles Female:
#   Columns: 892 → 107 (88.0% reduction)
#   Size: 312.7 MB → 41.2 MB (7.59x compression)
#
# Couples:
#   Columns: 1247 → 128 (89.7% reduction)
#   Size: 487.9 MB → 58.4 MB (8.35x compression)
#
# Total:
#   Original: 1045.9 MB
#   Reduced: 131.7 MB
#   Savings: 914.2 MB (87.4%)
#   Compression: 7.94x
#
# DRY RUN COMPLETE - No files were written
# Remove --dry-run flag to actually reduce columns
# ================================================================================

# If the dry run looks good, run the actual reduction:
# python scripts\enhanced\reduce_mnl_columns.py --input-dir U:/EUROMOD-STORAGE/Data/processed/fr/2016
