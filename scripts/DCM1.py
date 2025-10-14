# -*- coding: utf-8 -*-
"""Feature construction for discrete choice modelling (DCM) inputs.

This script enriches the wide household heads datasets with utility shifters
and interaction terms required by the DCM estimation stage.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCENARIO_DIR = PROJECT_ROOT / "Data" / "processed" / "scenarios"
DEFAULT_GENDERS: tuple[str, ...] = ("male", "female")
BASE_FILENAME_TEMPLATE = "heads_wide_single_{gender}.parquet"
OUTPUT_FILENAME_TEMPLATE = "heads_wide_single_{gender}_dcm.parquet"


LOGGER = logging.getLogger(__name__)


def _safe_log(series: pd.Series) -> pd.Series:
    """Return the natural log, guarding against non-positive inputs."""
    numeric = pd.to_numeric(series, errors="coerce")
    with np.errstate(divide="ignore", invalid="ignore"):
        logged = np.where(numeric > 0, np.log(numeric), np.nan)
    return pd.Series(logged, index=series.index, dtype=float)


def _detect_scenarios(df: pd.DataFrame) -> list[str]:
    """Infer scenario suffixes from consumption columns."""
    suffixes: list[str] = []
    for col in df.columns:
        if not col.startswith("consumption_"):
            continue
        suffix = col.split("consumption_", 1)[1]
        if not suffix:
            continue
        # Skip baseline columns such as 'consumption_original'
        if suffix.lower().startswith("orig"):
            continue
        suffixes.append(suffix)
    unique_suffixes = sorted({s for s in suffixes if f"lhw_{s}" in df.columns})
    if not unique_suffixes:
        raise ValueError("No scenario columns detected (expected consumption_<suffix>).")
    return unique_suffixes


def _ensure_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")


def _augment_gender_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Add log-based features and interactions for every scenario."""
    df = df.copy()

    _ensure_columns(
        df,
        [
            "dag",
            "num_children_total",
            "num_children_0_3",
            "num_children_3_6",
        ],
    )

    df["Lage"] = _safe_log(df["dag"])
    df["l2age"] = df["Lage"] ** 2
    df["DCH"] = ((df["num_children_0_3"] > 1) | (df["num_children_3_6"] > 1)).astype(int)

    scenarios = _detect_scenarios(df)
    LOGGER.info("Detected scenarios: %s", ", ".join(scenarios))

    for suffix in scenarios:
        consumption_col = f"consumption_{suffix}"
        hours_col = f"lhw_{suffix}"

        _ensure_columns(df, [consumption_col, hours_col])

        logy_col = f"logy_{suffix}"
        logl_col = f"logl_{suffix}"

        df[logy_col] = _safe_log(df[consumption_col])

        gap_hours = 80.0 - pd.to_numeric(df[hours_col], errors="coerce")
        gap_hours = gap_hours.where(gap_hours > 0, np.nan)
        df[logl_col] = _safe_log(gap_hours)

        df[f"log2y_{suffix}"] = df[logy_col] ** 2
        df[f"log2l_{suffix}"] = df[logl_col] ** 2
        df[f"logyl_{suffix}"] = df[logl_col] * df[logy_col]
        df[f"Leila_{suffix}"] = df[logl_col] * df["Lage"]
        df[f"Leila2_{suffix}"] = df[logl_col] * df["l2age"]
        df[f"lochi_{suffix}"] = df[logl_col] * df["num_children_total"]
        df[f"logdc_{suffix}"] = df[logl_col] * df["DCH"]

    return df


def _output_paths(gender: str) -> tuple[Path, Path]:
    input_path = SCENARIO_DIR / BASE_FILENAME_TEMPLATE.format(gender=gender)
    output_path = SCENARIO_DIR / OUTPUT_FILENAME_TEMPLATE.format(gender=gender)
    return input_path, output_path


def process_gender(gender: str, overwrite: bool = True) -> dict[str, Path]:
    """Load, enrich, and persist the DCM-ready dataset for the given gender."""
    input_path, output_path = _output_paths(gender)
    if not input_path.exists():
        raise FileNotFoundError(f"Missing input dataset: {input_path}")

    LOGGER.info("Loading %s", input_path)
    df = pd.read_parquet(input_path)
    augmented = _augment_gender_dataset(df)

    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {output_path}")

    LOGGER.info("Writing parquet to %s", output_path)
    augmented.to_parquet(output_path, engine="pyarrow", compression="snappy")

    csv_path = output_path.with_suffix(".csv")
    LOGGER.info("Writing CSV to %s", csv_path)
    augmented.to_csv(csv_path, index=False)

    return {"input": input_path, "parquet": output_path, "csv": csv_path}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Augment wide scenario datasets with DCM covariates.",
    )
    parser.add_argument(
        "--genders",
        nargs="+",
        choices=DEFAULT_GENDERS,
        default=list(DEFAULT_GENDERS),
        help="List of genders to process (default: both).",
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Prevent overwriting existing outputs.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = parse_args(argv)

    results = {}
    for gender in args.genders:
        LOGGER.info("Processing gender: %s", gender)
        outputs = process_gender(gender, overwrite=not args.no_overwrite)
        results[gender] = outputs

    for gender, paths in results.items():
        LOGGER.info(
            "[%s] input=%s parquet=%s csv=%s",
            gender,
            paths["input"],
            paths["parquet"],
            paths["csv"],
        )


if __name__ == "__main__":
    main()
