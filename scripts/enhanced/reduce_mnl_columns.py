#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
reduce_mnl_columns.py
=====================

Reduce MNL dataset columns from 900+ to ~100 essential columns.

This script analyzes YAML specifications and data requirements to determine
which columns are actually needed for estimation, then creates reduced datasets
that keep only essential columns.

Run this BETWEEN Step 5 (EUROMOD) and Step 6 (MNL dataset creation):
    Step 5: enh_RURO_euromod.py → Full dataset with 900+ columns
    THIS SCRIPT: reduce_mnl_columns.py → Reduced dataset with ~100 columns
    Step 6: enh_RURO_prep_mnl_basic.py → MNL dataset (faster with fewer cols)
    Step 7: enh_RURO_estimate_FR.py → Estimation

Benefits:
    - Reduce memory usage by ~90%
    - Speed up MNL dataset creation
    - Speed up data loading in estimation
    - Easier debugging and inspection

Author: Enhanced RURO Pipeline
Created: 2026-01-16
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Set

import pandas as pd
import yaml

# ==============================================================================
# Column Categories
# ==============================================================================

# Core identification columns (ALWAYS keep)
CORE_ID_COLS = {
    # Household identifiers
    "idhh",           # Household ID (primary key for grouping)
    "idhh_true",      # True household ID (CRITICAL: Step 6 merge key from EUROMOD)
    "didp",           # Person ID within household
    "idperson",       # Global person ID
    "idperson_true",  # True person ID (CRITICAL: Step 6 merge key from EUROMOD)
    "hid",            # Alternative household ID
    
    # Draw/choice identifiers
    "draw",           # Draw number (0 = observed)
    "is_chosen",      # 1 if chosen alternative, 0 otherwise
    "draw_id",        # Alternative draw ID
    
    # Year identifiers
    "year",
    "year_for_ruro",
    "data_year",
    "year_for_draws",
}

# Demographics (person-level characteristics)
DEMOGRAPHIC_COLS = {
    # Age (used in Step 6 for normalization, Step 7 for estimation)
    "dag",            # Age (years)
    "age",            # Age
    "age_norm",       # Age demeaned (created in Step 6)
    "age_norm2",      # Age squared (created in Step 6)
    
    # Gender (CRITICAL: used in Step 6 for couples reshaping)
    "dgn",            # Gender (0=female, 1=male)
    "female",         # Female indicator
    "male",           # Male indicator
    
    # Education (used in Step 6 for GSUR merge, Step 7 for estimation)
    "deh",            # Education (EUROMOD code)
    "deh_male",       # Male education (couples)
    "deh_female",     # Female education (couples)
    "educ3",          # Education 3 categories (0=low, 1=mid, 2=high)
    "educ3_male",     # Male education 3 categories (couples, GSUR merge)
    "educ3_female",   # Female education 3 categories (couples, GSUR merge)
    "educL",          # Low education dummy
    "educM",          # Medium education dummy (reference)
    "educH",          # High education dummy
    "educL_male",     # Male low education (couples)
    "educM_male",     # Male medium education (couples)
    "educH_male",     # Male high education (couples)
    "educL_female",   # Female low education (couples)
    "educM_female",   # Female medium education (couples)
    "educH_female",   # Female high education (couples)
    
    # Children (used in Step 7 estimation)
    "n_children",     # Number of children in household
    "num_children_total", # Alternative children count (used in Step 6)
    "nkids",          # Alternative children count
    "nch02",          # Children 0-2
    "nch36",          # Children 3-6
    "nch712",         # Children 7-12
    "nch1317",        # Children 13-17
    
    # Couple status (CRITICAL: used in Step 6 for couples processing)
    "in_couple",      # In couple indicator
    "couple",         # Couple indicator
    "idpartner",      # Partner ID
    "ruro_group",     # RURO group (1=singles, 10=couples, CRITICAL for Step 6)
    "ruro_decider",   # Decision-maker in couple
    "ruro_sample",    # Sample indicator
    "keep_for_analysis", # Analysis filter
    
    # Region (CRITICAL: used in Step 6 for GSUR merge)
    "drgn",           # Region (detailed)
    "drgn1",          # Region (NUTS1 level) - 8 categories for France
    "reg_nuts1",      # NUTS1 region code
    "reg_nuts1_1",    # Île-de-France (reference)
    "reg_nuts1_2",    # Nord-Ouest
    "reg_nuts1_3",    # Nord-Est
    "reg_nuts1_4",    # Sud-Ouest
    "reg_nuts1_5",    # Centre-Est
    "reg_nuts1_6",    # Méditerranée
    "reg_nuts1_7",    # Ouest
    "reg_nuts1_8",    # Outre-mer
}

# Labor market variables (hours, wages, occupation)
LABOR_MARKET_COLS = {
    # Hours (CRITICAL: used in Step 6 to compute leisure)
    "hours",          # Weekly hours worked
    "hours_observed", # Observed hours (for draw=0)
    "hours_male",     # Male hours (couples, used in Step 6)
    "hours_female",   # Female hours (couples, used in Step 6)
    "lhw",            # Hours worked (alternative name)
    "working",        # Working indicator (hours > 0)
    "working_pt1",    # Part-time 1 indicator (~20h)
    "working_pt2",    # Part-time 2 indicator (~30h)
    "working_ft",     # Full-time indicator (~40h)
    
    # Wages (used in Step 7 estimation)
    "wage",           # Hourly wage
    "wage_observed",  # Observed wage
    "wage_male",      # Male wage (couples)
    "wage_female",    # Female wage (couples)
    "lwage",          # Log wage
    "yem",            # Earnings
    
    # Experience (used in Step 7 estimation)
    "pexp_years",     # Potential experience (years) - singles
    "pexp_years2",    # Potential experience squared - singles
    "pexp_years_male",    # Male experience (years) - couples
    "pexp_years_female",  # Female experience (years) - couples
    "pexp_years2_male",   # Male experience squared - couples
    "pexp_years2_female", # Female experience squared - couples
    "pexp2_male",     # Alias for pexp_years2_male
    "pexp2_female",   # Alias for pexp_years2_female
    "exp",            # Experience
    "exp2",           # Experience squared
    
    # Occupation (LOC4 = 4 major ISCO groups, used in Step 7 estimation)
    "loc",            # Occupation code (detailed)
    "loc4",           # Occupation 4 groups (1=managers, 2=prof, 3=tech, 4=other)
    "loc4_1",         # Managers dummy
    "loc4_2",         # Professionals dummy
    "loc4_3",         # Technicians dummy
    "loc4_4",         # Clerks/service dummy
    "loc4_male",      # Male occupation (couples)
    "loc4_female",    # Female occupation (couples)
    
    # Industry (NACE) is dropped for occupation-opportunity M0 per contract §15/§25.
    # `lindi` is reserved for the M6 industry-opportunity extension; the
    # M0 MNL must not carry it. Held upstream in RURO-ready files for
    # traceability. Restore here only when activating M6.
    # "lindi",
    # "industry",
    # "nace",
}

# EUROMOD tax-benefit outputs
EUROMOD_COLS = {
    # Disposable income components
    "ils_dispy",      # Household disposable income (CRITICAL: used in Step 6 for consumption)
    "ils_dispy_em",   # EUROMOD disposable income (alternative name)
    "ils_dispy_male", # Male disposable income (CRITICAL: for couples consumption_male in Step 6)
    "ils_dispy_female", # Female disposable income (CRITICAL: for couples consumption_female in Step 6)
    "ils_origy",      # Original income
    "ils_earns",      # Earnings
    "ils_pen",        # Pensions
    "ils_sicdy",      # Social insurance contributions (employee)
    "ils_sic",        # Social insurance contributions (total)
    "tin_s",          # Income tax
    "tsy_s",          # Social contributions
    "bsa_s",          # Social assistance
    "bun_s",          # Unemployment benefits
    "bfa_s",          # Family benefits
    "bho_s",          # Housing benefits
    
    # Person-level income (for couples decomposition)
    "yem_male",       # Male earnings
    "yem_female",     # Female earnings
    "ils_earns_male", # Male earnings (EUROMOD)
    "ils_earns_female", # Female earnings (EUROMOD)
}

# Consumption and leisure (computed from income in Step 6, used in Step 7)
UTILITY_COLS = {
    # Consumption (computed in Step 6 from ils_dispy, used in Step 7 estimation)
    "consumption",    # Household consumption (CRITICAL: Step 7 singles estimation)
    "consumption_male",   # Male consumption (CRITICAL: Step 7 couples estimation)
    "consumption_female", # Female consumption (CRITICAL: Step 7 couples estimation)
    
    # Leisure (computed in Step 6 from hours, used in Step 7)
    "leisure",        # Leisure hours (CRITICAL: Step 7 singles)
    "leisure_male",   # Male leisure (CRITICAL: Step 7 couples)
    "leisure_female", # Female leisure (CRITICAL: Step 7 couples)
    
    # Normalized versions (computed in Step 6, used in Step 7)
    "c_norm",         # Normalized consumption
    "l_norm",         # Normalized leisure
    "l_norm_male",    # Normalized male leisure
    "l_norm_female",  # Normalized female leisure
    "log_c_norm",     # Log normalized consumption
    "log_l_norm",     # Log normalized leisure
    "log_l_norm_male",    # Log normalized male leisure
    "log_l_norm_female",  # Log normalized female leisure
    
    # Raw log versions (may be created in Step 6)
    "log_c",          # Log consumption (unnormalized)
    "log_l",          # Log leisure (unnormalized)
}

# Prior and GSUR (used in Step 7 estimation)
PRIOR_GSUR_COLS = {
    # Prior probability (CRITICAL: used in Step 7 likelihood computation)
    "prior",          # Prior probability (from draw generation)
    "log_prior",      # Log prior (used in Step 7 log-likelihood)
    "prior_h",        # Hours prior component
    "prior_w",        # Wage prior component

    # Frozen RURO M0 proposal components
    "log_q_E",
    "log_q_H",
    "log_q_W",
    "log_q_Occ",
    "log_q_E_male",
    "log_q_E_female",
    "log_q_H_male",
    "log_q_H_female",
    "log_q_W_male",
    "log_q_W_female",
    "log_q_Occ_male",
    "log_q_Occ_female",
    
    # GSUR unemployment rates (used in wage opportunity cost in Step 7)
    "gsur",           # Group-specific unemployment rate (singles)
    "gsur_male",      # Male GSUR (couples)
    "gsur_female",    # Female GSUR (couples)
    "u_rate",         # Alternative unemployment rate name
    "u_rate_male",    # Male unemployment rate
    "u_rate_female",  # Female unemployment rate
}

# Weights and other metadata
METADATA_COLS = {
    "dwt",            # Person weight
    "dwtx",           # Household weight
    "weight",         # Weight
    "idperson_draw",  # Person-draw composite ID
    "idhh_draw",      # Household-draw composite ID
    "sample_group",   # Sample group (created in Step 6)
    "chosen",         # Alternative name for is_chosen (used in Step 8)
    "other_members_income", # Other household members' income (used in Step 6 for singles consumption)
    
    # Original IDs (used in Step 6 couples reshape)
    "idorighh",       # Original household ID
    "idorigperson",   # Original person ID
    "idfather",       # Father ID
    "idmother",       # Mother ID
    
    # Household composition flags
    "hh_IsHead",      # Household head indicator
    "hh_IsPartner",   # Partner indicator
}

# Step 8 (Post-estimation) specific columns
POST_ESTIMATION_COLS = {
    # Predicted values (created in Step 7, used in Step 8)
    "log_opp",        # Log opportunity cost (singles)
    "log_opp_male",   # Male log opportunity cost (couples)
    "log_opp_female", # Female log opportunity cost (couples)
    
    # Probability diagnostics
    "prob",           # Choice probability
    "log_prob",       # Log probability
    
    # Gender/group indicators for post-estimation analysis
    "gender",         # Gender indicator (alternative to dgn)
}


def get_required_columns_from_yaml(yaml_path: Path) -> Set[str]:
    """
    Extract all variable names referenced in YAML specification.
    
    Returns set of column names that must be kept.
    """
    with open(yaml_path, 'r', encoding='utf-8') as f:
        spec = yaml.safe_load(f)
    
    required = set()
    
    # Utility leisure shifters
    if 'utility' in spec and 'leisure' in spec['utility']:
        shifters = spec['utility']['leisure'].get('shifters', [])
        for shifter in shifters:
            if 'variable' in shifter:
                required.add(shifter['variable'])
    
    # Hours opportunity shifters
    if 'hours_opportunity' in spec:
        shifters = spec['hours_opportunity'].get('shifters', [])
        for shifter in shifters:
            if 'variable' in shifter:
                required.add(shifter['variable'])
    
    # Wage opportunity shifters
    if 'wage_opportunity' in spec:
        mean_shifters = spec['wage_opportunity'].get('mean_shifters', [])
        for shifter in mean_shifters:
            if 'variable' in shifter:
                var = shifter['variable']
                if var != 'intercept':  # Skip intercept
                    required.add(var)
        
        # Occupation-based wage spec
        groups = spec['wage_opportunity'].get('groups', [])
        for group in groups:
            if 'variable' in group:
                required.add(group['variable'])
    
    return required


def get_all_required_columns(yaml_paths: List[Path]) -> Set[str]:
    """
    Get union of all columns needed across all YAML specifications.
    
    This ensures the reduced dataset works with ALL possible specifications
    AND all columns used in Steps 6, 7, and 8 are preserved.
    
    Priority order:
    1. Core columns (IDs, choice indicators) - ALWAYS needed
    2. Step 6 columns (demographics, EUROMOD outputs) - needed to CREATE MNL dataset
    3. Step 7 columns (consumption, leisure, prior, GSUR) - needed for ESTIMATION
    4. Step 8 columns (probabilities, diagnostics) - needed for POST-ESTIMATION
    5. YAML spec columns - specification-specific variables
    """
    all_required = set()
    
    # Add core columns (ALWAYS keep - needed for all steps)
    all_required.update(CORE_ID_COLS)
    all_required.update(DEMOGRAPHIC_COLS)
    all_required.update(LABOR_MARKET_COLS)
    all_required.update(EUROMOD_COLS)
    all_required.update(UTILITY_COLS)
    all_required.update(PRIOR_GSUR_COLS)
    all_required.update(METADATA_COLS)
    all_required.update(POST_ESTIMATION_COLS)
    
    # Add variables from YAML specs (specification-specific)
    for yaml_path in yaml_paths:
        if yaml_path.exists():
            logging.info(f"  Analyzing {yaml_path.name}...")
            yaml_cols = get_required_columns_from_yaml(yaml_path)
            all_required.update(yaml_cols)
            logging.info(f"    Found {len(yaml_cols)} variables")
    
    return all_required


def reduce_dataset(
    input_path: Path,
    output_path: Path,
    required_cols: Set[str],
    dry_run: bool = False
) -> Dict[str, any]:
    """
    Reduce dataset to only required columns.
    
    Parameters
    ----------
    input_path : Path
        Input parquet file
    output_path : Path
        Output parquet file
    required_cols : Set[str]
        Columns to keep
    dry_run : bool
        If True, only report what would be done (don't write output)
    
    Returns
    -------
    dict with:
        - original_cols: int - Number of columns in original
        - kept_cols: int - Number of columns kept
        - dropped_cols: int - Number of columns dropped
        - original_size_mb: float - Original file size (MB)
        - reduced_size_mb: float - Reduced file size (MB)
        - compression_ratio: float - Size reduction ratio
    """
    logging.info(f"Reading {input_path.name}...")
    df = pd.read_parquet(input_path)
    
    original_cols = len(df.columns)
    original_size_mb = input_path.stat().st_size / (1024**2)
    
    # Find columns to keep (intersection of required and available)
    available_cols = set(df.columns)
    cols_to_keep = sorted(required_cols & available_cols)
    cols_to_drop = sorted(available_cols - required_cols)
    
    # Warn about missing required columns
    missing_cols = required_cols - available_cols
    if missing_cols:
        logging.warning(f"  Missing {len(missing_cols)} required columns:")
        for col in sorted(missing_cols)[:10]:  # Show first 10
            logging.warning(f"    - {col}")
        if len(missing_cols) > 10:
            logging.warning(f"    ... and {len(missing_cols) - 10} more")
    
    # Create reduced dataset
    df_reduced = df[cols_to_keep].copy()
    
    kept_cols = len(cols_to_keep)
    dropped_cols = len(cols_to_drop)
    
    logging.info(f"  Original columns: {original_cols:,}")
    logging.info(f"  Kept columns: {kept_cols:,}")
    logging.info(f"  Dropped columns: {dropped_cols:,}")
    logging.info(f"  Reduction: {100 * dropped_cols / original_cols:.1f}%")
    
    if not dry_run:
        logging.info(f"  Writing to {output_path}...")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_reduced.to_parquet(output_path, compression='snappy', index=False)
        
        reduced_size_mb = output_path.stat().st_size / (1024**2)
        compression_ratio = original_size_mb / reduced_size_mb if reduced_size_mb > 0 else 0
        
        logging.info(f"  Original size: {original_size_mb:.1f} MB")
        logging.info(f"  Reduced size: {reduced_size_mb:.1f} MB")
        logging.info(f"  Compression: {compression_ratio:.2f}x")
    else:
        reduced_size_mb = original_size_mb * (kept_cols / original_cols)  # Estimate
        compression_ratio = original_size_mb / reduced_size_mb if reduced_size_mb > 0 else 0
        
        logging.info(f"  [DRY RUN] Original size: {original_size_mb:.1f} MB")
        logging.info(f"  [DRY RUN] Estimated reduced size: {reduced_size_mb:.1f} MB")
        logging.info(f"  [DRY RUN] Estimated compression: {compression_ratio:.2f}x")
    
    return {
        'original_cols': original_cols,
        'kept_cols': kept_cols,
        'dropped_cols': dropped_cols,
        'missing_cols': len(missing_cols),
        'original_size_mb': original_size_mb,
        'reduced_size_mb': reduced_size_mb,
        'compression_ratio': compression_ratio,
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Reduce MNL dataset columns from 900+ to ~100 essential columns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (show what would be done)
  python reduce_mnl_columns.py --input-dir U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016 --dry-run

  # Actually reduce columns
  python reduce_mnl_columns.py --input-dir U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016

  # Specify custom output directory
  python reduce_mnl_columns.py \\
      --input-dir U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016 \\
      --output-dir U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016_reduced

Notes:
  - Run this BETWEEN Step 4 (EUROMOD) and Step 6 (MNL dataset creation)
  - Input file: combined_draws_em.parquet (EUROMOD output from Step 4)
  - Output file: Same name in output directory (or _reduced suffix)
  - Preserves all columns needed for any YAML specification variant
"""
    )
    
    parser.add_argument(
        '--input-dir',
        type=Path,
        required=True,
        help='Directory containing EUROMOD output files'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        help='Output directory (default: input-dir with _reduced suffix)'
    )
    
    parser.add_argument(
        '--spec-dir',
        type=Path,
        default=Path(__file__).parent,
        help='Directory containing YAML specification files (default: script directory)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without writing files'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Validate input directory
    if not args.input_dir.exists():
        logging.error(f"Input directory does not exist: {args.input_dir}")
        sys.exit(1)
    
    # Set output directory
    if args.output_dir is None:
        args.output_dir = args.input_dir.parent / f"{args.input_dir.name}_reduced"
    
    logging.info("="*80)
    logging.info("MNL Dataset Column Reduction")
    logging.info("="*80)
    logging.info(f"Input directory: {args.input_dir}")
    logging.info(f"Output directory: {args.output_dir}")
    logging.info(f"Spec directory: {args.spec_dir}")
    if args.dry_run:
        logging.info("DRY RUN MODE - No files will be written")
    logging.info("")
    
    # Find all YAML specifications
    yaml_files = list(args.spec_dir.glob("estimation_spec*.yaml"))
    if not yaml_files:
        logging.warning(f"No YAML specifications found in {args.spec_dir}")
        logging.warning("Using default column set only")
    else:
        logging.info(f"Found {len(yaml_files)} YAML specifications:")
        for yaml_file in yaml_files:
            logging.info(f"  - {yaml_file.name}")
    logging.info("")
    
    # Get all required columns
    logging.info("Analyzing required columns...")
    required_cols = get_all_required_columns(yaml_files)
    logging.info(f"Total required columns: {len(required_cols)}")
    logging.info("")
      # Process the combined EUROMOD output file
    # This is what Step 6 actually reads!
    files = [
        ("combined_draws_em.parquet", "Combined EUROMOD Output"),
    ]
    
    results = {}
    
    for filename, label in files:
        input_path = args.input_dir / filename
        output_path = args.output_dir / filename
        
        if not input_path.exists():
            logging.warning(f"File not found: {input_path}")
            continue
        
        logging.info(f"Processing {label}...")
        result = reduce_dataset(input_path, output_path, required_cols, dry_run=args.dry_run)
        results[label] = result
        logging.info("")
      # Summary
    logging.info("="*80)
    logging.info("SUMMARY")
    logging.info("="*80)
    
    for label, result in results.items():
        logging.info(f"{label}:")
        logging.info(f"  Columns: {result['original_cols']} → {result['kept_cols']} "
                    f"({100 * result['dropped_cols'] / result['original_cols']:.1f}% reduction)")
        logging.info(f"  Size: {result['original_size_mb']:.1f} MB → {result['reduced_size_mb']:.1f} MB "
                    f"({result['compression_ratio']:.2f}x compression)")
        if result['missing_cols'] > 0:
            logging.info(f"  ⚠ Missing {result['missing_cols']} required columns")
    
    if results:
        total_original_size = sum(r['original_size_mb'] for r in results.values())
        total_reduced_size = sum(r['reduced_size_mb'] for r in results.values())
        total_compression = total_original_size / total_reduced_size if total_reduced_size > 0 else 0
        
        logging.info("")
        logging.info("Total:")
        logging.info(f"  Original: {total_original_size:.1f} MB")
        logging.info(f"  Reduced: {total_reduced_size:.1f} MB")
        if total_original_size > 0:
            logging.info(f"  Savings: {total_original_size - total_reduced_size:.1f} MB "
                        f"({100 * (total_original_size - total_reduced_size) / total_original_size:.1f}%)")
            logging.info(f"  Compression: {total_compression:.2f}x")
    else:
        logging.warning("")
        logging.warning("No files were processed! Check that input files exist.")
    
    if args.dry_run:
        logging.info("")
        logging.info("DRY RUN COMPLETE - No files were written")
        logging.info("Remove --dry-run flag to actually reduce columns")
    else:
        logging.info("")
        logging.info("COLUMN REDUCTION COMPLETE")
        logging.info(f"Reduced files saved to: {args.output_dir}")
        logging.info("")
        logging.info("Next steps:")
        logging.info("  1. Update Step 6 command to use reduced files:")
        logging.info(f"     --input-dir {args.output_dir}")
        logging.info("  2. Re-run Step 6 (MNL dataset creation) - should be faster!")
        logging.info("  3. Re-run Step 7 (estimation) - should be faster!")
    
    logging.info("="*80)


if __name__ == "__main__":
    main()
