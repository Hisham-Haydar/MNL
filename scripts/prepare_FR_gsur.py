#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
prepare_FR_gsur.py
==================

Transform FR_gsur.xlsx (Eurostat unemployment rates by region, age, sex, education)
into a clean lookup table for RURO estimation.

The Excel file has 120 sheets with different combinations of:
- Education: TOTAL, ED0-2 (low), ED3_4 (medium), ED5-8 (high)
- Sex: T (total), M (males), F (females)
- Age groups: Y15-24, Y15-29, Y15-74, Y_GE15, Y20-64, Y25-34, Y_GE25, Y35-44, Y45-54, Y55-64

Output: A clean parquet/CSV with columns:
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
"""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOGGER = logging.getLogger(__name__)

# Sheet metadata mapping from your description
SHEET_INFO = {
    # Sheet name pattern: (education, sex, age_group)
    # Education codes
    "TOTAL": "TOTAL",      # All ISCED 2011 levels
    "ED0-2": "ED0-2",      # Less than primary, primary and lower secondary (low)
    "ED3_4": "ED3_4",      # Upper secondary and post-secondary non-tertiary (medium)
    "ED5-8": "ED5-8",      # Tertiary education (high)
}

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


def create_ruro_gsur_lookup(full_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a RURO-ready gsur lookup table.
    
    For each combination of (year, drgn1, dgn, education), return gsur.
    
    Uses:
    - Y20-64 age group (working-age population)
    - Male (dgn=1) and Female (dgn=0) separately
    - Education levels mapped to EUROMOD education codes
    """
    # Use Y20-64 as the primary age group for RURO
    df = full_df[full_df["age_group"] == "Y20-64"].copy()
    
    # Keep only M/F (not Total)
    df = df[df["sex"].isin(["M", "F"])].copy()
    
    # Map region codes to EUROMOD drgn1 (1-10 for France NUTS1)
    # FR1 = 1, FRB = 2, FRC = 3, etc.
    region_order = ["FR1", "FRB", "FRC", "FRD", "FRE", "FRF", "FRG", "FRH", "FRI", "FRJ", "FRK", "FRL", "FRM", "FRY"]
    region_to_drgn1 = {r: i+1 for i, r in enumerate(region_order)}
    
    # Add national (FR) as drgn1=0
    region_to_drgn1["FR"] = 0
    
    df["drgn1"] = df["region_code"].map(region_to_drgn1)
    df = df[df["drgn1"].notna()].copy()
    df["drgn1"] = df["drgn1"].astype(int)
    
    # Map sex to dgn
    df["dgn"] = df["sex"].map({"M": 1, "F": 0})
    
    # Map education to EUROMOD-style codes
    # educL = ED0-2, educM = ED3_4, educH = ED5-8
    edu_map = {
        "ED0-2": "educL",
        "ED3_4": "educM", 
        "ED5-8": "educH",
        "TOTAL": "educALL",
    }
    df["educ_code"] = df["education"].map(edu_map)
    
    # Rename gsur and convert to proportion (currently in percent)
    df["gsur"] = df["gsur"] / 100.0
    
    # Select and rename columns
    result = df[[
        "year", "drgn1", "region_code", "region_name",
        "dgn", "sex", "education", "educ_code", "gsur"
    ]].copy()
    
    # Sort
    result = result.sort_values(["year", "drgn1", "dgn", "education"]).reset_index(drop=True)
    
    return result


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
    ruro_df = create_ruro_gsur_lookup(full_df)
    ruro_path = output_dir / "FR_gsur_ruro.parquet"
    ruro_df.to_parquet(ruro_path, index=False)
    LOGGER.info(f"RURO lookup saved to {ruro_path}")
    
    ruro_csv_path = output_dir / "FR_gsur_ruro.csv"
    ruro_df.to_csv(ruro_csv_path, index=False)
    LOGGER.info(f"RURO lookup saved to {ruro_csv_path}")
    
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
