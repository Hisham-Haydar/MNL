#!/usr/bin/env python
"""
Reduce draws files by removing unnecessary EUROMOD columns.

The draws files (singles/couples_RURO_ready_RURO_draws.parquet) currently have
~600 columns, most of which are duplicate EUROMOD outputs that are already in
the combined_draws_em.parquet file.

This script reduces them to ~50-60 essential columns needed for Step 6:
- IDs (person, household, draw tracking)
- Draw-specific variables (hours, wage that vary by alternative)
- Demographics (constant person characteristics)
- Prior probabilities
- Metadata

Expected reduction: 600 columns → ~50-60 columns (~90% reduction)
"""

import argparse
import pandas as pd
from pathlib import Path
from typing import Set
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# ESSENTIAL COLUMNS FOR DRAWS FILES
# ============================================================================
# These are the ONLY columns needed from draws files for Step 6 MNL prep
# Everything else (EUROMOD outputs, internals) should be removed

DRAWS_ID_COLS = {
    # Person/household identifiers
    "idperson",
    "idhh", 
    "idperson_true",
    "idhh_true",
    "idpartner",
    "idorighh",
    "idorigperson",
    
    # Draw tracking
    "draw",
    "is_chosen",
    "is_decider",
}

DRAWS_DRAW_SPECIFIC_COLS = {
    # Variables that VARY across draws (the actual alternatives)
    "hours",        # Hours worked in this alternative
    "wage",         # Wage in this alternative
    "yem",          # Employment income in this alternative
    "working",      # Working indicator
    "working_pt1",  # Part-time 1 indicator
    "working_pt2",  # Part-time 2 indicator
    "working_ft",   # Full-time indicator
    
    # Occupation varies by draw
    "loc",          # Occupation code
    "loc4",         # 4-category occupation (user requested)
    "loc_raw",
    "loc_ruro",
    
    # Draw-specific probabilities
    "log_q_state",
    "log_q_hours", 
    "log_q_wage",
    "log_q_occ",
    "log_q_total",
}

DRAWS_DEMOGRAPHICS_COLS = {
    # Person characteristics (constant across draws)
    "dag",          # Age
    "dgn",          # Gender
    "deh",          # Education level
    "drgn1",        # Region (for GSUR merge)
    "drgn2",
    "dec",          # Citizenship
    "dms",          # Marital status
    
    # Children counts
    "num_children_total",
    "num_children_0_3",
    "num_children_3_6", 
    "num_children_6_11",
    "num_children_11_17",
    
    # Education indicators
    "educL",
    "educH",
    "educ3",        # For GSUR merge
    
    # Experience
    "pexp",
    "pexp_years",
    "pexp_years2",
    "yd1", "yd2", "yd3",
}

DRAWS_LABOR_COLS = {
    # Labor market variables (base/reference values)
    "lhw",          # Hours worked (observed)
    "lhw_base",     # Base hours
    "lhw_base_raw",
    "lindi",        # Industry code (user requested)
    "lfs",          # Labor force status
    "les",          # Employment status
    
    # Wage variables (base/observed)
    "wage_for_draws",
    "wage_emp_obs",
    "wage_final",
    "wage_ruro",
    "wage_draw",
    "wage_draw_raw",
    "wage_source",
}

DRAWS_METADATA_COLS = {
    # Weights
    "dwt",
    
    # RURO metadata
    "ruro_group",
    "ruro_sample",
    "ruro_is_decider",
    "ruro_decider",
    "ruro_valid_decider_state",
    "ruro_invalid_decider_state",
    
    # Household composition
    "hh_n_ruro_deciders",
    "hh_joint_ok",
    "hh_IsHead",
    "hh_IsPartner",
    
    # Filtering
    "keep_for_analysis",
    
    # Year identifiers
    "data_year",
    "system_year",
    "year_for_ruro",
}

DRAWS_REGION_COLS = {
    # Region dummies (for models)
    "reg_nuts1_1",
    "reg_nuts1_2",
    "reg_nuts1_3",
    "reg_nuts1_4",
    "reg_nuts1_5",
    "reg_nuts1_6",
    "reg_nuts1_7",
    "reg_nuts1_8",
    "reg_nuts1_9",
    "reg_nuts1_10",
}

DRAWS_OTHER_COLS = {
    # Other member's income (for couples)
    "other_members_income",
    
    # Couple-specific
    "in_couple",
}

# Combine all essential columns
DRAWS_ESSENTIAL_COLS = (
    DRAWS_ID_COLS |
    DRAWS_DRAW_SPECIFIC_COLS |
    DRAWS_DEMOGRAPHICS_COLS |
    DRAWS_LABOR_COLS |
    DRAWS_METADATA_COLS |
    DRAWS_REGION_COLS |
    DRAWS_OTHER_COLS
)

logger.info(f"Total essential columns defined: {len(DRAWS_ESSENTIAL_COLS)}")

# ============================================================================
# COLUMNS TO DEFINITELY DROP (EUROMOD bloat)
# ============================================================================

EUROMOD_OUTPUT_PREFIXES = [
    "ils_",     # EUROMOD output variables (already in combined_draws_em)
    "tin_",     # Tax outputs
    "tsc_",     # Social contribution outputs
    "bsa_",     # Social assistance benefits
    "bun_",     # Unemployment benefits
    "bho_",     # Housing benefits
    "bfa_",     # Family benefits
    "bed_",     # Education benefits
    "bch_",     # Child benefits
    "bchlg_",   # Large family benefits
    "bched_",   # Education benefits
    "bdi_",     # Disability benefits
]

EUROMOD_INTERNAL_PREFIXES = [
    "i_",       # EUROMOD internal calculations
    "il_",      # EUROMOD intermediate variables
    "tu_",      # Tax unit variables
]

INPUT_VARIABLE_SUFFIX = "_input"  # Original input variables (pre-EUROMOD)

# Other EUROMOD variables to drop
EUROMOD_OTHER_DROPS = {
    "ypr", "yprrt", "yptmp", "ymwdt",  # Pre-EUROMOD income components
    "yse", "yiy", "ypp", "yot", "ypt",  # Other income components
    "xed00", "xhl00", "xhcmomi", "xhcrt", "xhcot", "xmp", "xpp", "xhc",  # Expenditure
    "kfbcc", "kivho", "kfb", "kfbmy",  # Capital
    "afc", "amrrm", "amrtn", "ate", "aco", "aca",  # Assets
    "temp_convcoef",  # Temporary EUROMOD variable
}


def identify_columns_to_drop(all_columns: list) -> tuple[Set[str], Set[str]]:
    """
    Identify which columns to keep vs drop.
    
    Returns:
        (keep_cols, drop_cols) - sets of column names
    """
    all_cols_set = set(all_columns)
    
    # Start with essential columns
    keep_cols = DRAWS_ESSENTIAL_COLS & all_cols_set
    
    # Find columns to drop
    drop_cols = set()
    
    # Drop EUROMOD outputs
    for prefix in EUROMOD_OUTPUT_PREFIXES:
        drop_cols.update([c for c in all_cols_set if c.startswith(prefix)])
    
    # Drop EUROMOD internals
    for prefix in EUROMOD_INTERNAL_PREFIXES:
        drop_cols.update([c for c in all_cols_set if c.startswith(prefix)])
    
    # Drop _input variables (original values before EUROMOD)
    drop_cols.update([c for c in all_cols_set if c.endswith(INPUT_VARIABLE_SUFFIX)])
    
    # Drop other EUROMOD variables
    drop_cols.update(EUROMOD_OTHER_DROPS & all_cols_set)
    
    # Remove any overlap (essential columns take priority)
    drop_cols = drop_cols - keep_cols
    
    # Find columns not in essential or drop lists (ambiguous)
    ambiguous_cols = all_cols_set - keep_cols - drop_cols
    
    return keep_cols, drop_cols, ambiguous_cols


def reduce_draws_file(
    input_path: Path,
    output_path: Path,
    dry_run: bool = False
) -> None:
    """
    Reduce a draws file by keeping only essential columns.
    
    Args:
        input_path: Path to input parquet file
        output_path: Path to output parquet file
        dry_run: If True, only report what would be done
    """
    logger.info("="*80)
    logger.info(f"Processing: {input_path.name}")
    logger.info("="*80)
    
    # Load file
    logger.info(f"Loading {input_path}...")
    df = pd.read_parquet(input_path)
    
    original_size_mb = input_path.stat().st_size / (1024**2)
    original_cols = len(df.columns)
    original_rows = len(df)
    
    logger.info(f"Original file:")
    logger.info(f"  Size: {original_size_mb:.1f} MB")
    logger.info(f"  Rows: {original_rows:,}")
    logger.info(f"  Columns: {original_cols:,}")
    
    # Identify columns
    keep_cols, drop_cols, ambiguous_cols = identify_columns_to_drop(df.columns.tolist())
    
    logger.info(f"\nColumn analysis:")
    logger.info(f"  Essential columns found: {len(keep_cols)}")
    logger.info(f"  Bloat columns to drop: {len(drop_cols)}")
    logger.info(f"  Ambiguous columns: {len(ambiguous_cols)}")
    
    if ambiguous_cols:
        logger.warning(f"\nAmbiguous columns (not in essential or drop lists):")
        for col in sorted(ambiguous_cols)[:20]:
            logger.warning(f"  - {col}")
        if len(ambiguous_cols) > 20:
            logger.warning(f"  ... and {len(ambiguous_cols) - 20} more")
        logger.warning(f"\nThese will be KEPT by default. Add to drop list if not needed.")
    
    # Show sample of columns to drop
    logger.info(f"\nSample columns to drop:")
    sample_drops = sorted(drop_cols)[:30]
    for col in sample_drops:
        logger.info(f"  - {col}")
    if len(drop_cols) > 30:
        logger.info(f"  ... and {len(drop_cols) - 30} more")
    
    # Final keep list: essential + ambiguous (conservative approach)
    final_keep_cols = sorted(keep_cols | ambiguous_cols)
    
    logger.info(f"\nFinal column count: {len(final_keep_cols)}")
    logger.info(f"Reduction: {original_cols} → {len(final_keep_cols)} ({(1 - len(final_keep_cols)/original_cols)*100:.1f}% reduction)")
    
    if dry_run:
        logger.info("\n[DRY RUN] Would save reduced file to:")
        logger.info(f"  {output_path}")
        logger.info("[DRY RUN] No files were modified.")
        return
    
    # Create reduced dataframe
    logger.info(f"\nCreating reduced dataframe...")
    df_reduced = df[final_keep_cols].copy()
    
    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save reduced file
    logger.info(f"Saving to {output_path}...")
    df_reduced.to_parquet(output_path, index=False, compression='snappy')
    
    # Report results
    reduced_size_mb = output_path.stat().st_size / (1024**2)
    size_reduction_pct = (1 - reduced_size_mb / original_size_mb) * 100
    compression_ratio = original_size_mb / reduced_size_mb
    
    logger.info("\n" + "="*80)
    logger.info("REDUCTION COMPLETE!")
    logger.info("="*80)
    logger.info(f"Output file: {output_path}")
    logger.info(f"\nSize:")
    logger.info(f"  Before: {original_size_mb:.1f} MB")
    logger.info(f"  After:  {reduced_size_mb:.1f} MB")
    logger.info(f"  Savings: {original_size_mb - reduced_size_mb:.1f} MB ({size_reduction_pct:.1f}% reduction)")
    logger.info(f"  Compression ratio: {compression_ratio:.1f}x")
    logger.info(f"\nColumns:")
    logger.info(f"  Before: {original_cols}")
    logger.info(f"  After:  {len(final_keep_cols)}")
    logger.info(f"  Removed: {original_cols - len(final_keep_cols)}")
    logger.info(f"\nRows: {original_rows:,} (unchanged)")
    logger.info("="*80)


def main():
    parser = argparse.ArgumentParser(
        description="Reduce draws files by removing unnecessary EUROMOD columns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview changes without modifying files)
  python reduce_draws_files.py --dry-run

  # Reduce both singles and couples files
  python reduce_draws_files.py
  
  # Reduce only singles file
  python reduce_draws_files.py --singles-only
  
  # Custom input/output paths
  python reduce_draws_files.py \\
    --singles-input path/to/singles.parquet \\
    --singles-output path/to/singles_reduced.parquet
        """
    )
    
    parser.add_argument(
        "--singles-input",
        type=Path,
        default=Path("U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_RURO_draws.parquet"),
        help="Path to singles draws file"
    )
    
    parser.add_argument(
        "--singles-output",
        type=Path,
        default=Path("U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_RURO_draws_reduced.parquet"),
        help="Path to save reduced singles file"
    )
    
    parser.add_argument(
        "--couples-input",
        type=Path,
        default=Path("U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_RURO_draws.parquet"),
        help="Path to couples draws file"
    )
    
    parser.add_argument(
        "--couples-output",
        type=Path,
        default=Path("U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_RURO_draws_reduced.parquet"),
        help="Path to save reduced couples file"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )
    
    parser.add_argument(
        "--singles-only",
        action="store_true",
        help="Only process singles file"
    )
    
    parser.add_argument(
        "--couples-only",
        action="store_true",
        help="Only process couples file"
    )
    
    args = parser.parse_args()
    
    # Validate inputs exist
    if not args.couples_only and not args.singles_input.exists():
        logger.error(f"Singles input file not found: {args.singles_input}")
        return
    
    if not args.singles_only and not args.couples_input.exists():
        logger.error(f"Couples input file not found: {args.couples_input}")
        return
    
    if args.dry_run:
        logger.info("\n" + "="*80)
        logger.info("DRY RUN MODE - No files will be modified")
        logger.info("="*80 + "\n")
    
    # Process files
    if not args.couples_only:
        reduce_draws_file(args.singles_input, args.singles_output, args.dry_run)
    
    if not args.singles_only:
        print()  # Blank line between files
        reduce_draws_file(args.couples_input, args.couples_output, args.dry_run)
    
    logger.info("\n✓ All done!")
    
    if not args.dry_run:
        logger.info("\nNext steps:")
        logger.info("  1. Run Step 6 with reduced files:")
        logger.info("     python scripts/enhanced/enh_RURO_prep_mnl_basic.py \\")
        logger.info("       --singles-draws <singles_reduced.parquet> \\")
        logger.info("       --couples-draws <couples_reduced.parquet> \\")
        logger.info("       --euromod-combined <combined_draws_em_reduced.parquet> ...")
        logger.info("  2. Check MNL dataset column count (should be ~100 instead of 641)")
        logger.info("  3. Compare Step 6 runtime (should be 2-3x faster)")


if __name__ == "__main__":
    main()
