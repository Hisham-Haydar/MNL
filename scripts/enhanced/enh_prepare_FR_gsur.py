#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-12-22 20:44:09
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/
# @Version : 1.0.0


"""
prepare_FR_gsur.py
==================

Transform FR_gsur.xlsx (Eurostat unemployment rates by region, age, sex, education)
into a clean lookup table for RURO estimation.

**RURO Merge Strategy:**

The output file `FR_gsur_ruro.parquet` is designed to be merged onto RURO draws or
EUROMOD output datasets using the following join keys:

    (year, drgn1, dgn, educ3)

Where:
- year: int (calendar year)
- drgn1: int (French NUTS1 region code: 1-10, with 0=national FR)
- dgn: int (gender: 1=male, 0=female)
- educ3: int (education level: 0=low/ED0-2, 1=medium/ED3_4, 2=high/ED5-8, -1=TOTAL)
- gsur: float (unemployment rate as PROPORTION, not percent)

The lookup guarantees uniqueness on (year, drgn1, dgn, educ3) and includes an
`age_group_used` column for transparency on which age cohort was selected.

The Excel file has 120 sheets with different combinations of:
- Education: TOTAL, ED0-2 (low), ED3_4 (medium), ED5-8 (high)
- Sex: T (total), M (males), F (females)
- Age groups: Y15-24, Y15-29, Y15-74, Y_GE15, Y20-64, Y25-34, Y_GE25, Y35-44, Y45-54, Y55-64

Intermediate outputs include full and simplified datasets; main RURO output columns:
- year: int
- region_code: str (e.g., FR, FR1, FRB, etc.)
- region_name: str
- sex: str (T, M, F)
- education: str (TOTAL, ED0-2, ED3_4, ED5-8)
- age_group: str
- gsur: float (unemployment rate in percent)

For RURO estimation, we typically need:
- gsur by year, region, sex, education, and age group
- The model uses gsur to capture labor market conditions affecting job opportunities

Usage:
    python scripts/prepare_FR_gsur.py
    python scripts/prepare_FR_gsur.py --output-dir Data/external
    python scripts/prepare_FR_gsur.py --age-group Y25-34 --nuts1-codes FR1 FRB FRC FRD FRE FRF FRG FRH FRI FRJ
"""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOGGER = logging.getLogger(__name__)

# Age group mapping (from sheet names to codes)
AGE_GROUP_MAP = {
    "From 15 to 24 years [Y15-24]": "Y15-24",
    "From 15 to 29 years [Y15-29]": "Y15-29",
    "From 15 to 74 years [Y15-74]": "Y15-74",
    "15 years or over [Y_GE15]": "Y_GE15",
    "From 20 to 64 years [Y20-64]": "Y20-64",
    "From 25 to 34 years [Y25-34]": "Y25-34",
    "25 years or over [Y_GE25]": "Y_GE25",
    "From 35 to 44 years [Y35-44]": "Y35-44",
    "From 45 to 54 years [Y45-54]": "Y45-54",
    "From 55 to 64 years [Y55-64]": "Y55-64",
}

# Sex mapping
SEX_MAP = {
    "Total [T]": "T",
    "Males [M]": "M",
    "Females [F]": "F",
}

# Education mapping
EDUCATION_MAP = {
    "All ISCED 2011 levels [TOTAL]": "TOTAL",
    "Less than primary, primary and lower secondary education (levels 0-2) [ED0-2]": "ED0-2",
    "Upper secondary and post-secondary non-tertiary education (levels 3 and 4) [ED3_4]": "ED3_4",
    "Tertiary education (levels 5-8) [ED5-8]": "ED5-8",
}

# Canonical NUTS1 ordering for drgn1 mapping (can be overridden via CLI)
DEFAULT_NUTS1_ORDER = [
    "FR1",  # Île-de-France
    "FRB",  # Centre-Val de Loire
    "FRC",  # Bourgogne-Franche-Comté
    "FRD",  # Normandie
    "FRE",  # Hauts-de-France
    "FRF",  # Grand Est
    "FRG",  # Pays de la Loire
    "FRH",  # Bretagne
    "FRI",  # Nouvelle-Aquitaine
    "FRJ",  # Occitanie
    "FRK",  # Auvergne-Rhône-Alpes
    "FRL",  # Provence-Alpes-Côte d'Azur
    "FRM",  # Corse
    "FRY",  # Départements d'outre-mer (DOM)
]


def build_nuts1_to_drgn1_mapping(
    observed_codes: set[str],
    canonical_order: list[str],
) -> dict[str, int]:
    """
    Build region_code → drgn1 mapping, validating against observed codes.

    Returns dict with FR → 0 (national) and NUTS1 codes → 1, 2, 3, ...
    """
    mapping = {"FR": 0}  # National always maps to 0

    for idx, code in enumerate(canonical_order, start=1):
        if code in observed_codes:
            mapping[code] = idx

    return mapping


def parse_sheet_metadata(df: pd.DataFrame) -> Dict[str, str]:
    """
    Parse the header rows of a sheet to extract education, sex, and age group.
    """
    metadata = {}
    
    # Look for metadata in first ~10 rows
    for idx in range(min(10, len(df))):
        row = df.iloc[idx]
        first_col = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
        
        # Education
        if "ISCED" in first_col or "education" in first_col.lower():
            for key, val in EDUCATION_MAP.items():
                # Check all columns for the education level
                for col_val in row:
                    if pd.notna(col_val) and key in str(col_val):
                        metadata["education"] = val
                        break
        
        # Sex
        if "Sex [SEX]" in first_col:
            for key, val in SEX_MAP.items():
                for col_val in row:
                    if pd.notna(col_val) and key in str(col_val):
                        metadata["sex"] = val
                        break
        
        # Age group
        if "Age class [AGE]" in first_col:
            for key, val in AGE_GROUP_MAP.items():
                for col_val in row:
                    if pd.notna(col_val) and key in str(col_val):
                        metadata["age_group"] = val
                        break
    
    return metadata


def parse_sheet_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse the actual data from a sheet (regions × years).
    """
    # Find the row with TIME header
    time_row = None
    for idx in range(min(15, len(df))):
        row = df.iloc[idx]
        if any(str(v).strip() == "TIME" for v in row if pd.notna(v)):
            time_row = idx
            break
    
    if time_row is None:
        return pd.DataFrame()
    
    # Find header row with GEO (Codes)
    geo_row = None
    for idx in range(time_row, min(time_row + 5, len(df))):
        row = df.iloc[idx]
        first_val = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
        if "GEO (Codes)" in first_val:
            geo_row = idx
            break
    
    if geo_row is None:
        return pd.DataFrame()
    
    # Extract years from TIME row
    time_vals = df.iloc[time_row]
    years = []
    year_cols = []
    for col_idx, val in enumerate(time_vals):
        if pd.notna(val):
            try:
                year = int(float(str(val).strip()))
                if 2000 <= year <= 2030:
                    years.append(year)
                    year_cols.append(col_idx)
            except (ValueError, TypeError):
                pass
    
    # Parse data rows (starting after GEO header)
    data_rows = []
    for idx in range(geo_row + 1, len(df)):
        row = df.iloc[idx]
        region_code = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        region_name = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
        
        # Skip non-region rows (footnotes, etc.)
        if not region_code or region_code.startswith("Special") or region_code.startswith(":"):
            continue
        if not re.match(r"^FR[A-Z0-9]*$", region_code):
            continue
        
        # Extract unemployment rates for each year
        for year, col_idx in zip(years, year_cols):
            val = row.iloc[col_idx] if col_idx < len(row) else np.nan
            
            # Parse numeric value (handle special cases)
            if pd.isna(val):
                gsur = np.nan
            elif isinstance(val, (int, float)):
                gsur = float(val)
            else:
                val_str = str(val).strip()
                if val_str in (":", "", "-"):
                    gsur = np.nan
                else:
                    try:
                        gsur = float(val_str)
                    except ValueError:
                        gsur = np.nan
            
            data_rows.append({
                "year": year,
                "region_code": region_code,
                "region_name": region_name,
                "gsur": gsur,
            })
    
    return pd.DataFrame(data_rows)


def process_all_sheets(xlsx_path: Path) -> pd.DataFrame:
    """
    Process all sheets in the Excel file and combine into one DataFrame.
    """
    xlsx = pd.ExcelFile(xlsx_path)
    
    all_data = []
    
    # Skip Summary and Structure sheets
    data_sheets = [s for s in xlsx.sheet_names if s.startswith("Sheet")]
    
    LOGGER.info(f"Processing {len(data_sheets)} sheets...")
    
    for sheet_name in data_sheets:
        try:
            df = pd.read_excel(xlsx, sheet_name=sheet_name, header=None)
            
            # Parse metadata
            metadata = parse_sheet_metadata(df)
            if not metadata:
                LOGGER.warning(f"Could not parse metadata for {sheet_name}")
                continue
            
            # Parse data
            data = parse_sheet_data(df)
            if data.empty:
                LOGGER.warning(f"No data found in {sheet_name}")
                continue
            
            # Add metadata columns
            data["education"] = metadata.get("education", "UNKNOWN")
            data["sex"] = metadata.get("sex", "UNKNOWN")
            data["age_group"] = metadata.get("age_group", "UNKNOWN")
            data["sheet"] = sheet_name
            
            all_data.append(data)
            
        except Exception as e:
            LOGGER.warning(f"Error processing {sheet_name}: {e}")
            continue
    
    if not all_data:
        raise ValueError("No data extracted from any sheet!")
    
    combined = pd.concat(all_data, ignore_index=True)
    LOGGER.info(f"Combined data: {len(combined)} rows")
    
    return combined


def create_simplified_gsur(full_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a simplified GSUR lookup for RURO estimation.
    
    For RURO, we typically want gsur by:
    - year
    - region (NUTS1 level: FR1, FRB, FRC, etc.)
    - sex (dgn: 1=male, 0=female)
    - education (educL=ED0-2, educM=ED3_4, educH=ED5-8)
    - age group (use Y20-64 or Y25-34 as default for working-age population)
    
    We'll focus on:
    - NUTS1 regions (2-3 character codes: FR, FR1, FRB, etc.)
    - Age group Y20-64 (main working age)
    - All education levels
    - Both sexes
    """
    # Filter to working-age population
    working_age_groups = ["Y20-64", "Y25-34", "Y_GE25"]
    df = full_df[full_df["age_group"].isin(working_age_groups)].copy()
    
    # Filter to NUTS1 regions (short codes)
    # FR = national, FR1, FRB, FRC, etc. = NUTS1
    df = df[df["region_code"].str.len() <= 3].copy()
    
    # Create dgn mapping (sex)
    df["dgn"] = df["sex"].map({"M": 1, "F": 0, "T": -1})
    
    # Create education mapping
    df["educ_level"] = df["education"].map({
        "ED0-2": "L",      # Low
        "ED3_4": "M",      # Medium
        "ED5-8": "H",      # High
        "TOTAL": "ALL",    # All levels
    })
    
    # Pivot to get one row per (year, region, sex, education, age_group)
    # and drop duplicates
    df = df.drop_duplicates(subset=["year", "region_code", "sex", "education", "age_group"])
    
    # Select columns for output
    output_cols = [
        "year", "region_code", "region_name", 
        "sex", "dgn", "education", "educ_level", 
        "age_group", "gsur"
    ]
    
    return df[output_cols].copy()


def create_ruro_gsur_lookup(
    full_df: pd.DataFrame,
    age_group: str = "Y20-64",
    nuts1_order: Optional[list[str]] = None,
) -> pd.DataFrame:
    """
    Create a RURO-ready gsur lookup table.

    Produces a unique lookup on (year, drgn1, dgn, educ3) with robust handling of:
    - Region mapping (data-driven + validated)
    - Age group selection (fallback chain)
    - Duplicate resolution (deterministic mean)
    - Bounds validation (gsur ∈ [0, 1])

    Args:
        full_df: Combined GSUR data from all sheets
        age_group: Preferred age group (default: Y20-64)
        nuts1_order: Optional explicit NUTS1 ordering for drgn1 assignment

    Returns:
        DataFrame with columns:
            year, drgn1, region_code, region_name, dgn, sex,
            education, educ_code, educ3, gsur, age_group_used, region_key
    """
    if nuts1_order is None:
        nuts1_order = DEFAULT_NUTS1_ORDER

    # Step 1: Filter to M/F only (exclude Total)
    df = full_df[full_df["sex"].isin(["M", "F"])].copy()

    # Step 2: Age group selection with fallback chain
    age_fallback_chain = [age_group, "Y25-34", "Y_GE25"]
    selected_age_group = None

    for candidate_age in age_fallback_chain:
        if candidate_age in df["age_group"].unique():
            selected_age_group = candidate_age
            LOGGER.info(f"Using age group: {selected_age_group}")
            break

    if selected_age_group is None:
        # Ultimate fallback: use any available age group
        available = df["age_group"].unique()
        if len(available) == 0:
            raise ValueError("No age groups found in data after filtering to M/F")
        selected_age_group = available[0]
        LOGGER.warning(
            f"Preferred age groups {age_fallback_chain} not found. "
            f"Using fallback: {selected_age_group}"
        )

    df = df[df["age_group"] == selected_age_group].copy()
    df["age_group_used"] = selected_age_group

    # Step 3: Build region → drgn1 mapping (data-driven + validated)
    observed_nuts1 = set(df["region_code"].unique())
    nuts1_observed = {c for c in observed_nuts1 if len(c) <= 3 and c.startswith("FR")}

    region_to_drgn1 = build_nuts1_to_drgn1_mapping(nuts1_observed, nuts1_order)

    # Log mapping validation
    mapped_codes = set(region_to_drgn1.keys())
    unmapped_codes = nuts1_observed - mapped_codes

    if unmapped_codes:
        LOGGER.warning(
            f"NUTS1 codes in data but not mapped to drgn1: {sorted(unmapped_codes)}"
        )

    LOGGER.info(f"Region → drgn1 mapping: {len(mapped_codes)} codes mapped")
    LOGGER.info(f"  Mapped: {sorted(mapped_codes)}")

    # Apply mapping
    df["drgn1"] = df["region_code"].map(region_to_drgn1)

    # Filter to successfully mapped regions only
    before_filter = len(df)
    df = df[df["drgn1"].notna()].copy()
    after_filter = len(df)

    if before_filter > after_filter:
        LOGGER.warning(
            f"Dropped {before_filter - after_filter} rows with unmapped region codes"
        )

    df["drgn1"] = df["drgn1"].astype(int)

    # Step 4: Map sex to dgn (RURO convention: M=1, F=0)
    df["dgn"] = df["sex"].map({"M": 1, "F": 0})

    # Step 5: Map education to EUROMOD-style codes
    edu_map = {
        "ED0-2": "educL",
        "ED3_4": "educM",
        "ED5-8": "educH",
        "TOTAL": "educALL",
    }
    df["educ_code"] = df["education"].map(edu_map)

    # Step 6: Add educ3 numeric column for joining (aligned with RURO pipeline)
    educ3_map = {
        "ED0-2": 0,  # Low
        "ED3_4": 1,  # Medium
        "ED5-8": 2,  # High
        "TOTAL": -1, # All levels (or could use pd.NA)
    }
    df["educ3"] = df["education"].map(educ3_map)

    # Step 7: Convert gsur to proportion (currently in percent)
    df["gsur"] = df["gsur"] / 100.0

    # Step 8: Ensure uniqueness on (year, drgn1, dgn, educ3)
    # If duplicates exist (e.g., multiple regions per drgn1, or data errors),
    # take the mean and log a warning
    key_cols = ["year", "drgn1", "dgn", "educ3"]

    # Check for duplicates
    dup_check = df.groupby(key_cols).size()
    duplicates = dup_check[dup_check > 1]

    if len(duplicates) > 0:
        LOGGER.warning(
            f"Found {len(duplicates)} key combinations with multiple gsur values. "
            f"Taking mean across duplicates."
        )
        # Show sample
        sample_keys = duplicates.head(3).index.tolist()
        for key in sample_keys:
            subset = df[
                (df["year"] == key[0])
                & (df["drgn1"] == key[1])
                & (df["dgn"] == key[2])
                & (df["educ3"] == key[3])
            ]
            LOGGER.warning(
                f"  Key {key}: {len(subset)} rows, "
                f"gsur range [{subset['gsur'].min():.4f}, {subset['gsur'].max():.4f}]"
            )

        # Aggregate: take mean gsur, keep first values for metadata
        agg_dict = {
            "gsur": "mean",
            "region_code": "first",
            "region_name": "first",
            "sex": "first",
            "education": "first",
            "educ_code": "first",
            "age_group_used": "first",
        }
        result = df.groupby(key_cols, as_index=False).agg(agg_dict)
    else:
        result = df[[
            "year", "drgn1", "region_code", "region_name",
            "dgn", "sex", "education", "educ_code", "educ3",
            "gsur", "age_group_used"
        ]].copy()

    # Step 9: Add region_key (aliasing drgn1 for explicit join clarity)
    result["region_key"] = result["drgn1"]

    # Step 10: Validate gsur bounds (must be in [0, 1] after conversion)
    out_of_bounds = result[(result["gsur"] < 0) | (result["gsur"] > 1)]
    if len(out_of_bounds) > 0:
        LOGGER.error(
            f"Found {len(out_of_bounds)} rows with gsur outside [0, 1]. "
            f"Range: [{result['gsur'].min():.4f}, {result['gsur'].max():.4f}]"
        )
        LOGGER.error(f"Sample out-of-bounds rows:\n{out_of_bounds.head().to_string()}")
        raise ValueError(
            f"GSUR validation failed: {len(out_of_bounds)} rows have unemployment "
            f"rate outside valid [0, 1] range."
        )

    LOGGER.info(f"GSUR bounds OK: all values in [{result['gsur'].min():.4f}, {result['gsur'].max():.4f}]")

    # Sort
    result = result.sort_values(["year", "drgn1", "dgn", "education"]).reset_index(drop=True)

    # Validation 2: Assert uniqueness of RURO keys (now using educ3)
    key_cols_final = ["year", "drgn1", "dgn", "educ3"]
    dup_check_final = result.groupby(key_cols_final).size()
    duplicates_final = dup_check_final[dup_check_final > 1]

    if len(duplicates_final) > 0:
        # Build error message with first ~20 duplicated keys
        dup_list = []
        for key, count in duplicates_final.head(20).items():
            dup_list.append(f"  {key}: {count} occurrences")

        dup_summary = "\n".join(dup_list)
        raise ValueError(
            f"RURO key uniqueness validation failed: {len(duplicates_final)} duplicated keys found.\n"
            f"Keys = (year, drgn1, dgn, educ3) should be unique.\n"
            f"First {min(20, len(duplicates_final))} duplicated keys:\n{dup_summary}"
        )

    # INFO logs: Final counts and coverage
    n_years = result["year"].nunique()
    n_drgn1 = result["drgn1"].nunique()
    n_dgn = result["dgn"].nunique()
    n_educ3 = result["educ3"].nunique()
    expected_rows = n_years * n_drgn1 * n_dgn * n_educ3
    missing_rate = result["gsur"].isna().mean() * 100

    LOGGER.info(f"RURO lookup validation: {len(result)} rows (expected: {expected_rows} = {n_years} years × {n_drgn1} regions × {n_dgn} genders × {n_educ3} education levels)")
    LOGGER.info(f"RURO lookup missing rate: {missing_rate:.2f}% of gsur values are missing")

    return result


def validate_ruro_coverage(ruro_df: pd.DataFrame) -> None:
    """
    Validate RURO lookup coverage and report missing data.

    Checks:
    - Coverage across years, regions, genders, education levels
    - Missing gsur values per year
    - Warns if >10% missing for any year
    """
    LOGGER.info("")
    LOGGER.info("=" * 60)
    LOGGER.info("RURO LOOKUP COVERAGE VALIDATION")
    LOGGER.info("=" * 60)

    # Dimensions coverage
    LOGGER.info(f"Years: {sorted(ruro_df['year'].unique())}")
    LOGGER.info(f"drgn1 values: {sorted(ruro_df['drgn1'].unique())}")
    LOGGER.info(f"dgn values: {sorted(ruro_df['dgn'].unique())}")
    LOGGER.info(f"educ3 values: {sorted(ruro_df['educ3'].unique())}")

    # Missing data analysis by year
    LOGGER.info("")
    LOGGER.info("Missing gsur values by year:")

    for year in sorted(ruro_df["year"].unique()):
        year_df = ruro_df[ruro_df["year"] == year]
        total_rows = len(year_df)
        missing_rows = year_df["gsur"].isna().sum()
        missing_pct = (missing_rows / total_rows * 100) if total_rows > 0 else 0

        status = "OK" if missing_pct <= 10 else "WARNING"
        LOGGER.info(f"  {year}: {missing_rows}/{total_rows} missing ({missing_pct:.1f}%) [{status}]")

        if missing_pct > 10:
            LOGGER.warning(
                f"Year {year} has >{missing_pct:.1f}% missing gsur values. "
                f"This may impact RURO estimation coverage."
            )

    LOGGER.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Prepare FR_gsur data for RURO estimation")
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=None,
        help="Path to FR_gsur.xlsx (default: external_data_root()/FR_gsur.xlsx)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        default=None,
        help="Output directory for processed files (default: external_data_root())"
    )
    parser.add_argument(
        "--age-group",
        type=str,
        default="Y20-64",
        help="Preferred age group for RURO lookup (default: Y20-64, with fallbacks)"
    )
    parser.add_argument(
        "--nuts1-codes",
        nargs="+",
        default=None,
        help="Explicit NUTS1 code ordering for drgn1 assignment (e.g., FR1 FRB FRC ...)"
    )
    args = parser.parse_args()

    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from path_helpers import external_data_root  # noqa: E402
    _ext = external_data_root()
    input_path = args.input if args.input is not None else _ext / "FR_gsur.xlsx"
    output_dir = args.output_dir if args.output_dir is not None else _ext
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    LOGGER.info(f"Reading {input_path}...")
    
    # Process all sheets
    full_df = process_all_sheets(input_path)
    
    # Save full dataset
    full_path = output_dir / "FR_gsur_full.parquet"
    full_df.to_parquet(full_path, index=False)
    LOGGER.info(f"Full dataset saved to {full_path}")
    
    # Also save as CSV for inspection
    full_csv_path = output_dir / "FR_gsur_full.csv"
    full_df.to_csv(full_csv_path, index=False)
    LOGGER.info(f"Full dataset saved to {full_csv_path}")
    
    # Create simplified version
    simple_df = create_simplified_gsur(full_df)
    simple_path = output_dir / "FR_gsur_simple.parquet"
    simple_df.to_parquet(simple_path, index=False)
    LOGGER.info(f"Simplified dataset saved to {simple_path}")
    
    # Create RURO-ready lookup
    ruro_df = create_ruro_gsur_lookup(
        full_df,
        age_group=args.age_group,
        nuts1_order=args.nuts1_codes,
    )
    ruro_path = output_dir / "FR_gsur_ruro.parquet"
    ruro_df.to_parquet(ruro_path, index=False)
    LOGGER.info(f"RURO lookup saved to {ruro_path}")

    ruro_csv_path = output_dir / "FR_gsur_ruro.csv"
    ruro_df.to_csv(ruro_csv_path, index=False)
    LOGGER.info(f"RURO lookup saved to {ruro_csv_path}")

    # Validate RURO coverage
    validate_ruro_coverage(ruro_df)

    # Print summary
    LOGGER.info("")
    LOGGER.info("=" * 60)
    LOGGER.info("SUMMARY")
    LOGGER.info("=" * 60)
    LOGGER.info(f"Full dataset: {len(full_df)} rows")
    LOGGER.info(f"  Years: {sorted(full_df['year'].unique())}")
    LOGGER.info(f"  Regions: {len(full_df['region_code'].unique())} unique")
    LOGGER.info(f"  Education levels: {full_df['education'].unique().tolist()}")
    LOGGER.info(f"  Sex: {full_df['sex'].unique().tolist()}")
    LOGGER.info(f"  Age groups: {full_df['age_group'].unique().tolist()}")
    LOGGER.info("")
    LOGGER.info(f"RURO lookup: {len(ruro_df)} rows")
    LOGGER.info(f"  Years: {sorted(ruro_df['year'].unique())}")
    LOGGER.info(f"  drgn1 values: {sorted(ruro_df['drgn1'].unique())}")
    LOGGER.info("")
    
    # Show sample of RURO data
    LOGGER.info("Sample of RURO lookup (year=2021, drgn1=1, dgn=1):")
    sample = ruro_df[(ruro_df["year"] == 2021) & (ruro_df["drgn1"] == 1) & (ruro_df["dgn"] == 1)]
    if len(sample) > 0:
        print(sample.to_string(index=False))
    else:
        # Try another year
        sample = ruro_df[(ruro_df["drgn1"] == 1) & (ruro_df["dgn"] == 1)].head(5)
        print(sample.to_string(index=False))


if __name__ == "__main__":
    main()
