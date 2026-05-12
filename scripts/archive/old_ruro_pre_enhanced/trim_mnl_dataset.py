#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Trim a RURO MNL dataset to only the columns needed for estimation.

Usage example (PowerShell):
python scripts/trim_mnl_dataset.py `
  --input "U:/EUROMOD-STORAGE/Data/processed/fr/2021/fr_2021_RURO_mnl.parquet" `
  --output "U:/EUROMOD-STORAGE/Data/processed/fr/2021/fr_2021_RURO_mnl_trim.parquet" `
  --z-cols dag dag2 `
  --extra-cols pexp_years pexp_years2 yd1 yd2
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

import pandas as pd


def _read_df(path: Path) -> pd.DataFrame:
    suf = path.suffix.lower()
    if suf == ".parquet":
        return pd.read_parquet(path)  # type: ignore[arg-type]
    if suf == ".csv":
        return pd.read_csv(path)
    if suf in {".pkl", ".pickle"}:
        return pd.read_pickle(path)
    raise ValueError(f"Unsupported input format: {path}")


def _write_df(df: pd.DataFrame, path: Path) -> None:
    suf = path.suffix.lower()
    if suf == ".parquet":
        df.to_parquet(path, index=False)  # type: ignore[arg-type]
    elif suf == ".csv":
        df.to_csv(path, index=False)
    elif suf in {".pkl", ".pickle"}:
        df.to_pickle(path)
    else:
        raise ValueError(f"Unsupported output format: {path}")


def _unique(seq: Iterable[str]) -> List[str]:
    out: list[str] = []
    seen: set[str] = set()
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Trim RURO MNL dataset to required columns before estimation."
    )
    ap.add_argument("--input", required=True, type=str, help="Path to full MNL dataset (parquet/csv/pkl).")
    ap.add_argument("--output", required=True, type=str, help="Path to trimmed dataset (parquet/csv/pkl).")
    ap.add_argument(
        "--z-cols",
        nargs="*",
        default=None,
        help="Optional preference shifters to retain (passed later to --z-cols in the estimator).",
    )
    ap.add_argument(
        "--extra-cols",
        nargs="*",
        default=None,
        help="Any other columns to keep (e.g., yd1 yd2 region dummies).",
    )
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    df = _read_df(input_path)

    # Core columns that should always be kept if present
    core_cols = [
        "idperson",
        "draw",
        "is_chosen",
        "consumption",
        "hours",
        "leisure",
        "wage",
        "wage_ruro",
        "yivwg",
        "loc",
        "drgn1",
        "ruro_group",
        "dgn",
        "educL",
        "educH",
        "pexp_years",
        "pexp_years2",
        "dag",
        "drgur",
        "yd1",
        "yd2",
        "idhh",
        "idhh_true",
        "idperson_true",
        "other_members_income",
    ]

    z_cols = args.z_cols or []
    extra_cols = args.extra_cols or []

    requested = _unique(core_cols + z_cols + extra_cols)
    keep = [c for c in requested if c in df.columns]

    missing = [c for c in requested if c not in df.columns]
    if missing:
        print(f"Warning: dropping missing columns (not found in data): {missing}")

    trimmed = df[keep].copy()
    _write_df(trimmed, output_path)

    print(f"Trimmed dataset saved to: {output_path}")
    print(f"Kept columns ({len(keep)}): {keep}")


if __name__ == "__main__":
    main()
