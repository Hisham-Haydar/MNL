#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
em_prep_core.py

Stage 1: Build a core EM-SILC micro dataset (person-level) for RURO.

- Reads EUROMOD input text files (e.g. FR_2016_a3.txt, FR_2017_a2.txt, FR_2018_a2.txt)
- Keeps key personal, labour and income variables as defined in the DRD documentation.
- Adds 'country' and 'year' columns.
- Optionally deflates monetary variables to a chosen base price year (HICP-based).
- Stacks years and writes a single Parquet file.

Designed to be year-agnostic and (largely) country-agnostic: file names and years
are passed via the command line.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd


# ----------------------------------------------------------------------
# Configuration: variables we keep (based on Drd_vars.txt)
# ----------------------------------------------------------------------

PERSONAL_VARS: List[str] = [
    "idhh", "idperson",
    "dag", "dgn", "dms",
    "deh", "dehde", "dey",
    "dcz", "ddi",
    "drgn1", "drgn2", "drgur", "drgmd", "drgru",
]

LABOUR_VARS: List[str] = [
    "les", "lcs", "lfs", "lindi", "loc",
    "liwmy", "liwmy_f", "liwftmy", "liwptmy",
    "lhw", "lhw_f",
    "liwwh", "liwwh_f",
    "lpemy", "lse", "lunmy", "lunmy_f", "lowas", "ltr",
]

INCOME_VARS: List[str] = [
    # main labour incomes
    "yem", "yem_f", "yse", "yse_f",
    "yemmy", "ysemy", "ymwdt",
    # pensions and benefits
    "bun", "bunmy", "bsa", "bsa00", "bsaot",
    "bfa", "bch00", "bched", "bchlg", "bchyc", "bchcc", "bchba", "bchot",
    "bho", "bhoot", "bhotn",
    "bed",
    "pdi", "pdimy", "pdi00", "bdi",
    "poa", "poamy", "poa00", "bsaoa",
    "psu", "psumy", "bsuwd",
    "bunct", "bunmt", "bsawk",
    # other incomes and taxes
    "yiy", "ypr", "ypt", "yptmp",
    "ypp", "yot",
    "yds", "ydses_o",
    "twl", "tis", "tad",
    # in-kind
    "kfb", "kfbcc", "kivho",
]

MONETARY_VARS: List[str] = [
    "yem", "yse", "bun", "bsa", "bfa", "bho",
    "bed", "pdi", "poa", "psu",
    "yiy", "ypr", "ypt", "yptmp", "ypp", "yot",
    "bch00", "bched", "bchlg", "bchyc", "bchcc", "bchba", "bchot",
    "bdi", "bsa00", "bsawk", "bsaoa", "bsuwd",
    "bunct", "bunmt",
    "poa00", "bsaot", "bhoot", "bhotn",
    "kfb", "kfbcc", "kivho",
    "yds", "ydses_o", "twl", "tis", "tad",
]

# Example HICP annual average index for France (all items, 2015–2017)
# You can extend or override this mapping via an external JSON later if needed.
HICP_FR: Dict[int, float] = {
    2015: 100.00,
    2016: 100.31,
    2017: 101.47,
    2018: 103.60,
}


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def build_logger(verbosity: int = 1) -> logging.Logger:
    logger = logging.getLogger("em_prep_core")
    if logger.handlers:
        return logger
    level = logging.INFO if verbosity == 1 else logging.DEBUG
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    return logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build core EM-SILC person-level dataset for RURO."
    )
    parser.add_argument(
        "--country",
        type=str,
        required=True,
        help="Two-letter EUROMOD country code, e.g. FR, BE, DE.",
    )
    parser.add_argument(
        "--years",
        type=int,
        nargs="+",
        required=True,
        help="List of survey years, e.g. 2016 2017 2018.",
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="Directory containing EUROMOD text files (country_year_xx.txt).",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to output Parquet file for the stacked core dataset.",
    )
    parser.add_argument(
        "--sep",
        type=str,
        default="\t",
        help="Column separator in EUROMOD txt files (default: tab).",
    )
    parser.add_argument(
        "--decimal",
        type=str,
        default=".",
        help="Decimal separator in EUROMOD txt files (default: '.').",
    )
    parser.add_argument(
        "--deflate",
        type=str,
        choices=["yes", "no"],
        default="yes",
        help="Whether to deflate monetary variables to base-price-year (default: yes).",
    )
    parser.add_argument(
        "--base-price-year",
        type=int,
        default=2016,
        help="Base year for price deflation (e.g. 2016).",
    )
    parser.add_argument(
        "--verbosity",
        type=int,
        default=1,
        help="0 = warnings, 1 = info, 2 = debug.",
    )

    return parser.parse_args()


def find_input_file(country: str, year: int, input_dir: Path) -> Path:
    """
    Locate EUROMOD txt file like 'FR_2016_a3.txt' using a simple glob pattern.
    Raises an error if no or multiple matches are found.
    """
    pattern = f"{country.upper()}_{year}_*.txt"
    matches = list(input_dir.glob(pattern))
    if len(matches) == 0:
        raise FileNotFoundError(f"No file matching pattern {pattern} in {input_dir}")
    if len(matches) > 1:
        raise RuntimeError(
            f"Multiple files matching pattern {pattern} in {input_dir}: {matches}"
        )
    return matches[0]


def load_em_file(path: Path, sep: str, decimal: str, logger: logging.Logger) -> pd.DataFrame:
    logger.info(f"Reading EUROMOD input file: {path}")
    df = pd.read_csv(
        path,
        sep=sep,
        decimal=decimal,
        dtype=str,  # read as string first to avoid weird parsing
    )
    # Let pandas infer numeric on a second pass for convenience
    df = df.apply(pd.to_numeric, errors="ignore")
    logger.info(f"Loaded {df.shape[0]:,} rows and {df.shape[1]:,} columns.")
    return df


def compute_deflator(
    year: int,
    base_year: int,
    hicp_mapping: Dict[int, float],
) -> float:
    """
    Compute deflator factor: multiply nominal values in 'year' by this to express in base_year prices.
    """
    if year not in hicp_mapping or base_year not in hicp_mapping:
        raise KeyError(
            f"HICP index missing for year={year} or base_year={base_year}."
        )
    return hicp_mapping[base_year] / hicp_mapping[year]


def deflate_monetary_columns(
    df: pd.DataFrame,
    year: int,
    base_year: int,
    logger: logging.Logger,
    hicp_mapping: Dict[int, float] = HICP_FR,
    monetary_vars: List[str] = MONETARY_VARS,
) -> pd.DataFrame:
    factor = compute_deflator(year, base_year, hicp_mapping)
    if np.isclose(factor, 1.0):
        logger.info(
            f"Year {year}: deflator factor ≈ 1.0 (base year {base_year}) — skipping scaling."
        )
        return df

    intersect = [v for v in monetary_vars if v in df.columns]
    logger.info(
        f"Year {year}: applying deflator factor {factor:.5f} to {len(intersect)} monetary variables."
    )
    for v in intersect:
        df[v] = pd.to_numeric(df[v], errors="coerce") * factor
    return df


def select_core_variables(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    wanted = PERSONAL_VARS + LABOUR_VARS + INCOME_VARS
    cols = [c for c in wanted if c in df.columns]

    missing = [c for c in wanted if c not in df.columns]
    if missing:
        logger.debug(f"Variables not found in this file (will be silently dropped): {missing}")

    logger.info(f"Keeping {len(cols)} variables out of {len(wanted)} configured.")
    return df[cols]


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main() -> None:
    args = parse_args()
    logger = build_logger(args.verbosity)

    country = args.country.upper()
    years = args.years
    input_dir = Path(args.input_dir)
    output_path = Path(args.output)
    deflate = args.deflate == "yes"

    all_years = []

    for year in years:
        logger.info(f"Processing country={country}, year={year}")
        em_file = find_input_file(country, year, input_dir)
        df_raw = load_em_file(em_file, sep=args.sep, decimal=args.decimal, logger=logger)

        # Select core variables
        df_core = select_core_variables(df_raw, logger=logger)

        # Add identifiers
        df_core["country"] = country
        df_core["year"] = year

        # Optionally deflate monetary values to base price year
        if deflate:
            df_core = deflate_monetary_columns(
                df_core,
                year=year,
                base_year=args.base_price_year,
                logger=logger,
            )

        all_years.append(df_core)

    if not all_years:
        raise RuntimeError("No data loaded — nothing to write.")

    df_all = pd.concat(all_years, axis=0, ignore_index=True)
    logger.info(
        f"Final stacked dataset: {df_all.shape[0]:,} rows, {df_all.shape[1]:,} columns."
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_all.to_parquet(output_path, index=False)
    logger.info(f"Wrote core dataset to: {output_path}")


if __name__ == "__main__":
    main()
