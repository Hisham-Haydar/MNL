#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-11-28 13:25:34
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/
# @Version : 1.0.0


"""
RURO_prep.py

Minimal post-processing of the filtered datasets produced by data_prep2.py
to construct RURO-style explanatory variables needed for estimation.

Scope of this script
--------------------
Starting from:

    couples_filtering_final.<ext>
    singles_filtering_final.<ext>

it produces:

    couples_RURO_ready.<ext>
    singles_RURO_ready.<ext>

and only adds variables that are *not* already created in data_prep2:

    - ruro_group: 1 for singles, 10 for couples
    - wage_ruro: unified wage variable for workers, 0 for non-workers
    - is_worker: 1{les==3 and lhw>0}
    - working: 1{lhw>0}
    - working_pt1: 1{0 < lhw <= 20}
    - working_pt2: 1{20 < lhw <= 35}
    - working_ft: 1{lhw > 35}
    - pexp_years: potential experience in years (using dew if available)
    - pexp_years2: squared potential experience
    - yd1, yd2, yd3: year dummies based on input_year/system_year/yds

This script deliberately does NOT:
    - create education group dummies (educL, educH);
    - create region dummies (regW, regB);
    - compute equivalised income or CPI-uprated income;
    - touch your disposable-income variables.

Those can be handled separately for presentation/robustness checks.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, Tuple, cast

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Bootstrap paths (same style as data_prep2.py)
# ---------------------------------------------------------------------------
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:  # interactive environments
    SCRIPT_DIR = Path.cwd() / "scripts"
PROJECT_ROOT = (SCRIPT_DIR / "..").resolve()

# Make sure SCRIPT_DIR and PROJECT_ROOT are on sys.path (for path_helpers, scratch, etc.)
for candidate in (SCRIPT_DIR, PROJECT_ROOT):
    c_str = str(candidate)
    if c_str not in sys.path:
        sys.path.insert(0, c_str)


from path_helpers import data_root, ensure_dir, resolve_storage_root  # type: ignore

# Add scratch/ to the path so we can import setup_logging like in data_prep2.py
SCRATCH_DIR = PROJECT_ROOT / "scratch"
if SCRATCH_DIR.exists():
    sys.path.insert(0, str(SCRATCH_DIR))

from scratch.my_functions import setup_logging  # type: ignore



DEFAULT_COUNTRY = "fr"
DEFAULT_YEAR = 2021
DEFAULT_EXPORT_FORMAT = "parquet"


# ---------------------------------------------------------------------------
# Path resolution helper (keep near top so CLI can call it)
# ---------------------------------------------------------------------------
def _maybe_add_column(df: pd.DataFrame, name: str, values: Any) -> None:
    """
    Add a column `name` to df with given `values` only if it does not exist yet.

    This ensures RURO_prep does not overwrite variables already created in
    data_prep2.py or elsewhere in the pipeline.
    """
    if name not in df.columns:
        df[name] = values


def _resolve_processed_dir(
    arg_dir: Path | None,
    base_year: int,
    export_format: str = DEFAULT_EXPORT_FORMAT,
) -> Path:
    """
    Resolve the processed directory, preferring external storage (EUROMOD-STORAGE) when present.

    If a relative path is provided, it is searched under all known storage roots (data_root,
    resolve_storage_root, U:/EUROMOD-STORAGE, ~/EUROMOD-STORAGE).
    """
    if arg_dir is not None and arg_dir.is_absolute():
        return arg_dir

    rel = arg_dir if arg_dir is not None else Path("processed") / DEFAULT_COUNTRY / str(base_year)

    candidates: list[Path] = []
    try:
        candidates.append(resolve_storage_root())
    except Exception:
        pass
    # Explicit external hints
    candidates.append(Path(r"U:/EUROMOD-STORAGE"))
    candidates.append(Path.home() / "EUROMOD-STORAGE")
    # Fallback to repo-local data_root
    candidates.append(data_root().parent)

    chosen: Path | None = None
    for root in candidates:
        data_dir = root / "Data"
        options: list[Path] = []
        if data_dir.exists():
            options.append(data_dir / rel)
        options.append(root / rel)
        for candidate in options:
            if not candidate.exists():
                continue
            # Prefer a path that actually contains the expected singles file
            singles_candidate = candidate / f"singles_filtering_final.{export_format}"
            if singles_candidate.exists():
                return candidate.resolve()
            chosen = chosen or candidate

    # Fall back to first existing candidate or data_root-based path
    if chosen:
        return chosen.resolve()
    return (data_root() / rel).resolve()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_filtered_data(
    processed_dir: Path,
    export_format: str = DEFAULT_EXPORT_FORMAT,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load singles and couples filtered datasets produced by data_prep2.py.

    Expected filenames (as written via export_household_data with
    output_prefix 'couples_filtering' / 'singles_filtering'):

        couples_filtering_final.<export_format>
        singles_filtering_final.<export_format>
    """
    singles_path = processed_dir / f"singles_filtering_final.{export_format}"
    couples_path = processed_dir / f"couples_filtering_final.{export_format}"

    if not singles_path.exists():
        raise FileNotFoundError(f"Singles file not found: {singles_path}")
    if not couples_path.exists():
        raise FileNotFoundError(f"Couples file not found: {couples_path}")

    if export_format == "parquet":
        singles = pd.read_parquet(singles_path)  # type: ignore[arg-type]
        couples = pd.read_parquet(couples_path)  # type: ignore[arg-type]
    else:
        singles = pd.read_csv(singles_path)
        couples = pd.read_csv(couples_path)

    required = {"idhh", "idperson", "dag", "lhw", "les"}
    missing_s = required - set(singles.columns)
    missing_c = required - set(couples.columns)
    if missing_s:
        raise KeyError(f"Singles dataset is missing columns: {sorted(missing_s)}")
    if missing_c:
        raise KeyError(f"Couples dataset is missing columns: {sorted(missing_c)}")

    return singles, couples


def _infer_year_series(df: pd.DataFrame, default_year: int) -> pd.Series:
    """
    Get a per-observation year series used for pexp and year dummies.

    Priority (as documented):
        1. 'input_year' if present (from prepare_one_year)
        2. 'system_year' if present
        3. 'yds' if present (original EU-SILC income year)
        4. fallback: default_year (scalar)
    """
    if "input_year" in df.columns:
        year = cast(pd.Series, pd.to_numeric(df["input_year"], errors="coerce"))
    elif "system_year" in df.columns:
        year = cast(pd.Series, pd.to_numeric(df["system_year"], errors="coerce"))
    elif "yds" in df.columns:
        year = cast(pd.Series, pd.to_numeric(df["yds"], errors="coerce"))
    else:
        year = pd.Series(default_year, index=df.index, dtype="float64")

    year = cast(pd.Series, year).fillna(default_year).astype(int)
    return year


def _add_ruro_variables_basic(
    df: pd.DataFrame,
    *,
    default_year: int = DEFAULT_YEAR,
) -> pd.DataFrame:
    """
    Add only the RURO variables that are not already in data_prep2 outputs:

        - ruro_group is set outside this function (singles vs couples).
        - wage_ruro
        - is_worker, working, working_pt1, working_pt2, working_ft
        - pexp_years, pexp_years2
        - yd1, yd2, yd3
        - (optionally) hours, wage as aliases for lhw and wage_ruro

    Assumes df has at least:
        'dag', 'lhw', 'les', 'idperson', 'idhh',
    and ideally 'dew' (year of graduation) plus a year variable
    (input_year/system_year/yds).

    **Crucially**: never overwrites columns that already exist.
    """
    df = df.copy()

    # ---------------------------
    # 1. Year variable and dummies
    # ---------------------------
    year = _infer_year_series(df, default_year)

    _maybe_add_column(df, "year_for_ruro", year)

    uniq_years = np.sort(year.unique())
    yd1_year = int(uniq_years[0]) if len(uniq_years) >= 1 else default_year
    yd2_year = int(uniq_years[1]) if len(uniq_years) >= 2 else yd1_year
    yd3_year = int(uniq_years[2]) if len(uniq_years) >= 3 else yd1_year

    yd1 = (year == yd1_year).astype(int)
    yd2 = (year == yd2_year).astype(int)
    yd3 = (year == yd3_year).astype(int)

    _maybe_add_column(df, "yd1", yd1)
    _maybe_add_column(df, "yd2", yd2)
    _maybe_add_column(df, "yd3", yd3)

    # ---------------------------
    # 2. Potential experience (years)
    # ---------------------------
    dag = cast(pd.Series, pd.to_numeric(df["dag"], errors="coerce"))

    # Use the already-inferred year (avoid recomputation)
    year_for_calc = year

    if "dew" in df.columns:
        grad_year = cast(pd.Series, pd.to_numeric(df["dew"], errors="coerce"))

        # Treat clearly invalid graduation years as missing:
        # - negative values (like FR's -1)
        # - unrealistically early (< 1900) or beyond the reference year+1
        grad_year_clean = cast(
            pd.Series,
            grad_year.where(
                (grad_year >= 1900) & (grad_year <= year_for_calc + 1),
                np.nan,
            ),
        )

        # Start from age-based potential experience
        pexp = cast(pd.Series, (dag - 18).clip(lower=0))

        # Where a clean graduation year exists, override with calendar-based pexp
        mask = grad_year_clean.notna()
        pexp.loc[mask] = (year_for_calc.loc[mask] - grad_year_clean.loc[mask]).clip(lower=0)
    else:
        pexp = cast(pd.Series, (dag - 18).clip(lower=0))

    # Define pexp_years and pexp_years2 consistently
    pexp_years = cast(pd.Series, pexp.astype(float))
    pexp_years2 = cast(pd.Series, (pexp_years ** 2).astype(float))

    _maybe_add_column(df, "pexp_years", pexp_years)
    _maybe_add_column(df, "pexp_years2", pexp_years2)

    # If you later want the exact Stijn-style pexp in "hundreds of years" (≈ /100),
    # you can create an alias here:
    if "pexp" not in df.columns:
        df["pexp"] = df["pexp_years"]

    # ---------------------------
    # 3. Unified wage and working indicators
    # ---------------------------
    # Choose source for wage: prefer 'wage_final', then 'w_emp_strict', then 'yivwg'
    wage_source = None
    for cand in ["wage_final", "w_emp_strict", "yivwg"]:
        if cand in df.columns:
            wage_source = cand
            break
    if wage_source is None:
        raise KeyError(
            "No wage variable found for RURO. Expected one of "
            "'wage_final', 'w_emp_strict', or 'yivwg'."
        )

    lhw = cast(pd.Series, pd.to_numeric(df["lhw"], errors="coerce")).fillna(0.0)
    les = cast(pd.Series, pd.to_numeric(df["les"], errors="coerce"))

    # Stijn's 'lma == 1 & hours > 0' is conceptually your "in labour market AND positive hours".
    # Here we define 'is_worker' = {les == 3 and lhw > 0}.
    is_worker = les.eq(3) & (lhw > 0.0)
    _maybe_add_column(df, "is_worker", is_worker.astype(int))

    wage_numeric = cast(pd.Series, pd.to_numeric(df[wage_source], errors="coerce")).fillna(0.0)
    wage_ruro = np.where(is_worker, wage_numeric, 0.0)
    _maybe_add_column(df, "wage_ruro", wage_ruro)

    working = (lhw > 0.0).astype(int)
    working_pt1 = ((lhw > 0.0) & (lhw <= 20.0)).astype(int)
    working_pt2 = ((lhw > 20.0) & (lhw <= 35.0)).astype(int)
    working_ft = (lhw > 35.0).astype(int)

    _maybe_add_column(df, "working", working)
    _maybe_add_column(df, "working_pt1", working_pt1)
    _maybe_add_column(df, "working_pt2", working_pt2)
    _maybe_add_column(df, "working_ft", working_ft)

    # Optional: Stijn uses 'hours' and 'wage' in his RURO likelihood.
    # Provide aliases if they don't exist, to smooth later porting.
    _maybe_add_column(df, "hours", lhw)
    _maybe_add_column(df, "wage", wage_ruro)

    return df

def _prepare_ruro_basic(
    processed_dir: Path,
    *,
    base_year: int = DEFAULT_YEAR,
    export_format: str = DEFAULT_EXPORT_FORMAT,
) -> Dict[str, Any]:
    """
    High-level driver:

      1. Load singles and couples filtered datasets from processed_dir.
      2. Tag ruro_group (singles vs couples).
      3. Add basic RURO variables via _add_ruro_variables_basic.
      4. Export RURO-ready datasets.

    This function does NOT touch disposable income, equivalence scales,
    CPI, or education/region coding.
    """
    setup_logging("INFO")
    processed_dir = ensure_dir(processed_dir)

    singles, couples = _load_filtered_data(processed_dir, export_format=export_format)

    # ruro_group: group code for later estimation
    singles["ruro_group"] = 1   # singles
    couples["ruro_group"] = 10  # couples

    singles_ruro = _add_ruro_variables_basic(singles, default_year=base_year)
    couples_ruro = _add_ruro_variables_basic(couples, default_year=base_year)

    out_singles = processed_dir / f"singles_RURO_ready.{export_format}"
    out_couples = processed_dir / f"couples_RURO_ready.{export_format}"

    if export_format == "parquet":
        singles_ruro.to_parquet(out_singles, index=False)  # type: ignore[arg-type]
        couples_ruro.to_parquet(out_couples, index=False)  # type: ignore[arg-type]
    else:
        singles_ruro.to_csv(out_singles, index=False)
        couples_ruro.to_csv(out_couples, index=False)

    meta: Dict[str, Any] = {
        "processed_dir": str(processed_dir),
        "base_year": int(base_year),
        "export_format": export_format,
        "singles_rows": int(singles_ruro.shape[0]),
        "couples_rows": int(couples_ruro.shape[0]),
        "singles_file": str(out_singles),
        "couples_file": str(out_couples),
    }
    return meta


def _cli_ruro_prep_basic() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Construct minimal RURO-style explanatory variables on top of "
            "data_prep2 outputs (no equivalence scales, no CPI, no educL/H)."
        )
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=None,
        help=(
            "Directory where data_prep2 wrote couples_filtering_final.* and "
            "singles_filtering_final.*. "
            "If omitted, defaults to data_root()/processed/fr/2021."
        ),
    )
    parser.add_argument(
        "--base-year",
        type=int,
        default=DEFAULT_YEAR,
        help="Reference year used when inferring years (only used as fallback).",
    )
    parser.add_argument(
        "--export-format",
        type=str,
        default=DEFAULT_EXPORT_FORMAT,
        choices=["parquet", "csv"],
        help="Output format for RURO-ready datasets.",
    )
    args = parser.parse_args()

    processed_dir = _resolve_processed_dir(args.processed_dir, args.base_year, args.export_format)

    meta = _prepare_ruro_basic(
        processed_dir=processed_dir,
        base_year=args.base_year,
        export_format=args.export_format,
    )
    print("RURO preparation (basic) completed:")
    for k, v in meta.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    _cli_ruro_prep_basic()
