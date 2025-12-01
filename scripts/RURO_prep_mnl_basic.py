#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-12-01 16:17:45
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/


from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

TOTAL_LEISURE_HOURS = 80.0
WEEKS_PER_MONTH = 52.0 / 12.0
DCM_MIN_POSITIVE = 1e-6


def _read_df(path: Path) -> pd.DataFrame:
    suf = path.suffix.lower()
    if suf == ".parquet":
        return pd.read_parquet(path)  # type: ignore[arg-type]
    if suf == ".csv":
        return pd.read_csv(path)
    if suf in {".pkl", ".pickle"}:
        return pd.read_pickle(path)
    raise ValueError(f"Unsupported format for {path}")


def _write_df(df: pd.DataFrame, base: Path) -> Dict[str, Path]:
    out_parquet = base.with_suffix(".parquet")
    out_csv = base.with_suffix(".csv")
    df.to_parquet(out_parquet, index=False)  # type: ignore[arg-type]
    df.to_csv(out_csv, index=False)
    return {"parquet": out_parquet, "csv": out_csv}


def _build_mnl_block(df: pd.DataFrame, sample_group: str) -> pd.DataFrame:
    """
    Build the MNL regressor block from a *_RURO_draws long dataframe.
    Builds consumption using ils_dispy plus other_members_income (when available).
    """
    df = df.copy()

    # Basic sanity
    if "idperson" not in df.columns or "draw" not in df.columns or "is_chosen" not in df.columns:
        raise KeyError("Expected columns 'idperson', 'draw', 'is_chosen' in RURO_draws data.")

    # Hours & income
    hours = pd.to_numeric(df.get("hours", df.get("lhw")), errors="coerce").fillna(0.0)
    df["hours"] = hours

    # Make sure yem exists and is coherent
    if "yem" not in df.columns:
        wage = pd.to_numeric(df.get("wage", df.get("wage_ruro", df.get("yivwg"))),
                             errors="coerce").fillna(0.0)
        df["yem"] = wage * hours * WEEKS_PER_MONTH

    # Consumption: ils_dispy + other_members_income (when available)
    if "ils_dispy" in df.columns:
        cons_base = pd.to_numeric(df["ils_dispy"], errors="coerce").fillna(0.0)
    else:
        cons_base = pd.to_numeric(df["yem"], errors="coerce").fillna(0.0)
    if "other_members_income" in df.columns:
        other_inc = pd.to_numeric(df["other_members_income"], errors="coerce").fillna(0.0)
    else:
        other_inc = pd.Series(0.0, index=df.index)

    if "ruro_group" in df.columns:
        ruro_group = pd.to_numeric(df["ruro_group"], errors="coerce").fillna(0)
    else:
        ruro_group = pd.Series(0, index=df.index)
    cons = cons_base.copy()
    # Singles: add other members' income to head
    singles_mask = ruro_group.eq(1)
    cons.loc[singles_mask] = cons_base.loc[singles_mask] + other_inc.loc[singles_mask]
    # Couples: household consumption = head + partner + other members
    couples_mask = ruro_group.eq(10)
    if couples_mask.any() and "idhh" in df.columns:
        hh_total = (cons_base + other_inc).groupby(df["idhh"]).transform("sum")
        cons.loc[couples_mask] = hh_total.loc[couples_mask]

    cons = cons.clip(lower=DCM_MIN_POSITIVE)

    leisure = TOTAL_LEISURE_HOURS - hours
    leisure = leisure.clip(lower=DCM_MIN_POSITIVE)

    # Simple log specification (you can later switch to Box–Cox)
    df["log_c"] = np.log(cons)
    df["log_l"] = np.log(leisure)

    # Optionally, normalisations (e.g., divide by 1000) can be added later

    # Keep a compact set of columns for the MNL
    keep_cols = [
        "idperson", "draw", "is_chosen",
        "ruro_group",
        "log_c", "log_l",
        "hours", "yem",
        "wage", "wage_ruro", "yivwg",
        "dgn", "pexp_years", "pexp_years2",
        "loc", "yd1", "yd2", "yd3",
    ]
    existing = [c for c in keep_cols if c in df.columns]
    out = df[existing].copy()
    out["sample_group"] = sample_group
    return out


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Prepare RURO MNL estimation dataset from *_RURO_draws long files."
    )
    ap.add_argument(
        "--singles-draws",
        type=str,
        required=True,
        help="Path to singles_RURO_ready_RURO_draws.parquet (or .csv, .pkl).",
    )
    ap.add_argument(
        "--couples-draws",
        type=str,
        required=False,
        help="Path to couples_RURO_ready_RURO_draws.parquet (optional).",
    )
    ap.add_argument(
        "--out-base",
        type=str,
        required=True,
        help="Base path for output (without extension), e.g. fr_2021_RURO_mnl",
    )
    return ap.parse_args()


def main() -> None:
    args = parse_args()

    singles_path = Path(args.singles_draws).resolve()
    if not singles_path.exists():
        raise FileNotFoundError(f"Singles draws file not found: {singles_path}")
    singles_long = _read_df(singles_path)
    singles_mnl = _build_mnl_block(singles_long, sample_group="singles")

    frames = [singles_mnl]

    if args.couples_draws:
        couples_path = Path(args.couples_draws).resolve()
        if not couples_path.exists():
            raise FileNotFoundError(f"Couples draws file not found: {couples_path}")
        couples_long = _read_df(couples_path)
        couples_mnl = _build_mnl_block(couples_long, sample_group="couples")
        frames.append(couples_mnl)

    full_mnl = pd.concat(frames, axis=0, ignore_index=True)

    out_base = Path(args.out_base).resolve()
    outputs = _write_df(full_mnl, out_base)
    print("MNL dataset written to:")
    for k, v in outputs.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
