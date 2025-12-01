#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-12-01 12:47:45
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/


# %%
"""
RURO_prepare_mnl.py

Builds RURO–MNL-ready long datasets from the RURO_prep output
for BOTH singles and couples.

For each provided RURO_prep file (singles or couples), it:

1. Loads the RURO dataset (long: one row per (hh, person, draw)).
2. If necessary, runs EUROMOD once on that dataset to obtain disposable income.
3. Constructs:
   - hours (from lhw),
   - leisure = 80 - lhw (no normalisation here),
   - household-level consumption (sum of ils_dispy per (idhh, draw)),
   - choice indicator is_chosen (draw == 0),
   - log prior density over opportunities (hours, wage, loc).

It writes a *_RURO_MNL.parquet and *_RURO_MNL.csv next to the input file.

All normalisation (Box–Cox, scaling of c and l, etc.) is left to the
RURO_estimation step.
"""

from __future__ import annotations

import os
os.environ.setdefault("PYTHONNET_RUNTIME", "coreclr")

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import euromod as em

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:
    # Interactive (Jupyter, IPython)
    import inspect
    SCRIPT_DIR = Path(inspect.getfile(inspect.currentframe())).resolve().parent
    if not SCRIPT_DIR.exists():
        SCRIPT_DIR = Path.cwd()

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from path_helpers import data_root, euromod_root, ensure_dir, resolve_storage_root  # type: ignore

PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = data_root()
PROCESSED_DIR = ensure_dir(DATA_DIR / "processed")

LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# EUROMOD system identifiers (adapt to FR 2021)
TARGET_COUNTRY = "FR"
TARGET_SYSTEM = "FR_2021"
TARGET_DATASET = "FR_2021_a1"  # adapt if different

TOTAL_LEISURE_HOURS = 80.0    # weekly time endowment for leisure definition
DCM_MIN_POSITIVE = 1e-6       # guard for logs / ratios

# Prior parameters – defaults inspired by Stijn's example
DEFAULT_PI0_M = 0.10
DEFAULT_PI0_F = 0.10
DEFAULT_H_MIN = 1.0
DEFAULT_H_MAX = 70.0
DEFAULT_W_MIN = 1.0
DEFAULT_W_MAX = 120.0

# Wage specification: "fw" (fixed) or "vw" (variable)
DEFAULT_WAGE_SPEC = "fw"


# ---------------------------------------------------------------------------
# Euromod context
# ---------------------------------------------------------------------------
@dataclass
class EuromodContext:
    model: em.Model
    system: em.System
    dataset_name: str


def _prepare_euromod(
    country: str = TARGET_COUNTRY,
    system_name: str = TARGET_SYSTEM,
    dataset_name: Optional[str] = TARGET_DATASET,
) -> EuromodContext:
    """Initialise EUROMOD model and select system/dataset."""
    model_root = euromod_root()
    model = em.Model(str(model_root))
    country_obj = model[country]

    try:
        system = country_obj[system_name]
    except KeyError:
        # Fallback: first system if named system not found
        system = next(iter(country_obj.values()))

    # Resolve dataset name robustly: if provided and present, keep; otherwise fall back to bestmatch/first
    if dataset_name:
        try:
            if hasattr(system, "datasets") and dataset_name in getattr(system, "datasets", {}):
                resolved_dataset = getattr(system, "datasets")[dataset_name]
                dataset_name = getattr(resolved_dataset, "name", dataset_name)
            else:
                dataset_name = ""
        except Exception:
            dataset_name = ""

    if not dataset_name:
        try:
            dataset = system.bestmatch_datasets[0]
            dataset_name = getattr(dataset, "name", "")
        except Exception:
            dataset_name = ""

    return EuromodContext(model=model, system=system, dataset_name=dataset_name or "")


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------
def _read_dataframe(path: Path) -> pd.DataFrame:
    """Read RURO dataset from any supported format."""
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path)  # type: ignore[arg-type]
    if suffix == ".feather":
        return pd.read_feather(path)  # type: ignore[arg-type]
    if suffix in {".pkl", ".pickle"}:
        return pd.read_pickle(path)
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".txt":
        return pd.read_csv(path, sep="\t")
    raise ValueError(f"Unsupported dataset format for RURO input: {path}")


def _write_outputs(df: pd.DataFrame, input_path: Path, suffix: str = "_RURO_MNL") -> dict[str, Path]:
    """Write MNL-ready dataset in parquet and csv formats next to the input file."""
    out_dir = input_path.parent
    base = input_path.stem + suffix

    parquet_path = out_dir / f"{base}.parquet"
    csv_path = out_dir / f"{base}.csv"

    df.to_parquet(parquet_path, engine="pyarrow", compression="snappy")  # type: ignore[arg-type]
    df.to_csv(csv_path, index=False)

    LOGGER.info("RURO–MNL dataset saved to %s and %s", parquet_path, csv_path)
    return {"parquet": parquet_path, "csv": csv_path}


# ---------------------------------------------------------------------------
# Path resolution helper
# ---------------------------------------------------------------------------
def _resolve_input_path(raw: str, label: str | None = None) -> Path:
    """
    Try to resolve the given path string to an existing file, with fallbacks to the
    detected storage root (EUROMOD-STORAGE) to handle drive/UNC differences.
    """
    candidates: list[Path] = []
    p = Path(raw)
    candidates.append(p)

    # Common typo correction
    if "raedy" in p.name:
        candidates.append(Path(str(p).replace("raedy", "ready")))

    # If we have a storage root, try mapping under it
    try:
        storage = resolve_storage_root()
        # If raw is absolute and not under storage, try relative mapping
        try:
            rel = p.relative_to(storage)
        except Exception:
            rel = None
        if rel is None:
            # If path contains EUROMOD-STORAGE, strip up to it and reattach to storage root
            parts = p.parts
            if "EUROMOD-STORAGE" in parts:
                idx = parts.index("EUROMOD-STORAGE")
                rel = Path(*parts[idx + 1 :])
        if rel is not None:
            candidates.append(storage / rel)
        # If raw is relative, also try storage / raw
        if not p.is_absolute():
            candidates.append(storage / p)
    except Exception:
        pass

    # Also try mapping U: drive to a common UNC prefix
    if p.drive and p.drive.upper().startswith("U:"):
        try:
            rel = p.relative_to(p.anchor)
            candidates.append(Path(r"\\users\\users\\hisham\\EUROMOD-STORAGE") / rel)
        except Exception:
            pass

    # If a label is provided, try standard RURO_prep output names in the same folder
    if label:
        parent = p.parent if p.name else Path(".")
        suffix = p.suffix if p.suffix else ".parquet"
        candidates.append(parent / f"{label}_RURO_ready{suffix}")
        if suffix != ".parquet":
            candidates.append(parent / f"{label}_RURO_ready.parquet")

    # Deduplicate while preserving order
    seen = set()
    for c in candidates:
        if c not in seen and c.exists():
            return c
        seen.add(c)

    # If nothing exists, return the first candidate (original path) so caller can report it
    return candidates[0]


# ---------------------------------------------------------------------------
# Core transformations
# ---------------------------------------------------------------------------
def _run_euromod_if_needed(ctx: EuromodContext, df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure disposable income is available.
    If 'ils_dispy' is absent, run EUROMOD and merge outputs.
    """
    if "ils_dispy" in df.columns:
        LOGGER.info("Column 'ils_dispy' already present – skipping EUROMOD run.")
        return df

    if "idperson" not in df.columns:
        raise KeyError("RURO dataset must contain 'idperson' to merge EUROMOD outputs.")

    LOGGER.info("Running EUROMOD on RURO dataset...")
    sim = ctx.system.run(df, ctx.dataset_name if ctx.dataset_name else None)
    sim_df = sim.outputs[0]
    if not isinstance(sim_df, pd.DataFrame):
        sim_df = sim_df.to_dataframe()  # type: ignore[attr-defined]

    # Avoid overwriting core inputs; rename colliding columns (except idperson)
    rename_map = {
        col: f"{col}_sim"
        for col in sim_df.columns
        if col in df.columns and col != "idperson"
    }
    sim_renamed = sim_df.rename(columns=rename_map)

    merged = df.merge(sim_renamed, on="idperson", how="left", validate="one_to_one")

    # Decide which column to treat as disposable income
    if "ils_dispy_sim" in merged.columns:
        merged["ils_dispy"] = merged["ils_dispy_sim"]
    elif "ils_dispy" not in merged.columns:
        raise KeyError(
            "EUROMOD output did not provide 'ils_dispy' or 'ils_dispy_sim'. "
            "Check system configuration."
        )

    return merged


def _compute_hours_and_leisure(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute hours and leisure from weekly hours.

    No normalisation here; we only define:
        hours   = lhw
        leisure = TOTAL_LEISURE_HOURS - lhw
    """
    if "lhw" not in df.columns:
        raise KeyError("RURO dataset must contain 'lhw' for hours.")

    df = df.copy()
    df["hours"] = pd.to_numeric(df["lhw"], errors="coerce")

    if df["hours"].isna().any():
        raise ValueError("Missing values in 'lhw' – cannot construct leisure.")

    df["leisure"] = TOTAL_LEISURE_HOURS - df["hours"]
    neg_leis = df["leisure"] <= 0
    if neg_leis.any():
        LOGGER.warning(
            "Found %d observations with non-positive leisure; clipping to %g.",
            int(neg_leis.sum()),
            DCM_MIN_POSITIVE,
        )
        df.loc[neg_leis, "leisure"] = DCM_MIN_POSITIVE

    return df


def _compute_consumption(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construct 'consumption' as household-level disposable income
    (sum of ils_dispy across household members), per (idhh, draw).

    This is done for both singles and couples. For singles, this
    collapses to individual disposable income.
    """
    required = {"idhh", "draw", "ils_dispy"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns for consumption computation: {sorted(missing)}")

    df = df.copy()

    # Sum ils_dispy at household-draw level and broadcast back
    cons = (
        df.groupby(["idhh", "draw"])["ils_dispy"]
        .transform("sum")
        .astype(float)
    )
    df["consumption"] = cons

    if (df["consumption"] < 0).any():
        LOGGER.warning(
            "Some (idhh, draw) combinations have negative consumption; "
            "check tax-benefit simulation and data."
        )

    return df


def _compute_choice_indicator(df: pd.DataFrame) -> pd.DataFrame:
    """Add is_chosen indicator: 1 if draw == 0 (observed job), else 0."""
    df = df.copy()
    if "draw" not in df.columns:
        raise KeyError("RURO dataset must contain 'draw' to identify chosen alternative.")

    df["is_chosen"] = (df["draw"] == 0).astype(int)

    # Each person should have exactly one chosen alternative (draw==0)
    sum_chosen = df.groupby("idperson")["is_chosen"].sum()
    if not (sum_chosen == 1).all():
        bad = sum_chosen[sum_chosen != 1]
        LOGGER.warning(
            "For some individuals, is_chosen does not sum to 1; "
            "check RURO_prep output. Problematic ids (first 10): %s",
            bad.index[:10].tolist(),
        )
    return df


def _compute_prior(
    df: pd.DataFrame,
    wage_spec: str = DEFAULT_WAGE_SPEC,
    pi0_m: float = DEFAULT_PI0_M,
    pi0_f: float = DEFAULT_PI0_F,
    h_min: float = DEFAULT_H_MIN,
    h_max: float = DEFAULT_H_MAX,
    w_min: float = DEFAULT_W_MIN,
    w_max: float = DEFAULT_W_MAX,
) -> pd.DataFrame:
    """
    Compute the log prior over opportunities (hours, wages, loc) for RURO.

    - Prior is defined at the individual job level (singles or spouses in couples).
    - wage_spec = "fw": prior over (h, loc).
    - wage_spec = "vw": prior over (h, w, loc).

    In "spirit of Stijn's code":
      * π0_m, π0_f are masses at zero hours for men and women.
      * 'lma' > 0 identifies the labour-market sample (singles & couples).
      * 'loc' is treated as a discrete occupation code; we assume a
        uniform prior over its support among positive-hour jobs.
    """
    df = df.copy()

    # Basic checks / variables
    for col in ("lma", "dgn", "hours", "loc"):
        if col not in df.columns:
            raise KeyError(f"RURO dataset must contain '{col}'.")

    # Wage variable (hourly)
    if "wage" in df.columns:
        wage = pd.to_numeric(df["wage"], errors="coerce")
    elif "yivwg" in df.columns:
        wage = pd.to_numeric(df["yivwg"], errors="coerce")
    else:
        raise KeyError("RURO dataset must contain 'wage' or 'yivwg'.")
    df["wage"] = wage

    lma = df["lma"].astype(int)
    dgn = df["dgn"].astype(int)
    hours = df["hours"]

    # Gender-specific mass at zero hours, for all observations with lma > 0
    pi0 = np.zeros(len(df), dtype=float)
    active = lma > 0
    mask_m = active & (dgn == 1)
    mask_f = active & (dgn == 0)

    pi0[mask_m.to_numpy()] = pi0_m
    pi0[mask_f.to_numpy()] = pi0_f
    df["pi0"] = pi0

    # Continuous supports
    h_support = max(h_max - h_min, DCM_MIN_POSITIVE)
    w_support = max(w_max - w_min, DCM_MIN_POSITIVE)

    hours_zero = hours <= 0
    hours_pos = ~hours_zero

    # Occupation support (number of distinct loc values for positive-hour jobs)
    loc_pos = df.loc[hours_pos, "loc"].dropna().unique()
    loc_support = float(len(loc_pos))
    if loc_support <= 0:
        loc_support = 1.0
        LOGGER.warning(
            "No non-missing loc values among positive-hour jobs; "
            "treating loc_support as 1."
        )

    prior_density = np.empty(len(df), dtype=float)

    if wage_spec == "fw":
        # Fixed wages: prior over hours and loc
        prior_density[hours_zero.to_numpy()] = pi0[hours_zero.to_numpy()]
        prior_density[hours_pos.to_numpy()] = (
            (1.0 - pi0[hours_pos.to_numpy()])
            * (1.0 / h_support)
            * (1.0 / loc_support)
        )
    elif wage_spec == "vw":
        # Variable wages: prior over hours, wages and loc (independent uniform)
        prior_density[hours_zero.to_numpy()] = pi0[hours_zero.to_numpy()]
        prior_density[hours_pos.to_numpy()] = (
            (1.0 - pi0[hours_pos.to_numpy()])
            * (1.0 / h_support)
            * (1.0 / w_support)
            * (1.0 / loc_support)
        )
    else:
        raise ValueError("wage_spec must be 'fw' or 'vw'.")

    prior_density = np.clip(prior_density, 1e-16, None)
    df["prior"] = np.log(prior_density)

    return df


def build_ruro_mnl_dataset(
    input_path: Path,
    country: str = TARGET_COUNTRY,
    system_name: str = TARGET_SYSTEM,
    dataset_name: Optional[str] = TARGET_DATASET,
    wage_spec: str = DEFAULT_WAGE_SPEC,
    pi0_m: float = DEFAULT_PI0_M,
    pi0_f: float = DEFAULT_PI0_F,
    h_min: float = DEFAULT_H_MIN,
    h_max: float = DEFAULT_H_MAX,
    w_min: float = DEFAULT_W_MIN,
    w_max: float = DEFAULT_W_MAX,
) -> pd.DataFrame:
    """
    Full pipeline for a given RURO_prep output (singles or couples):

    - load RURO_prep output
    - EUROMOD (if needed)
    - hours & leisure
    - household consumption
    - choice indicator
    - prior(h, w, loc)
    """
    LOGGER.info("Loading RURO dataset from %s", input_path)
    df = _read_dataframe(input_path)

    ctx = _prepare_euromod(country=country, system_name=system_name, dataset_name=dataset_name)
    df = _run_euromod_if_needed(ctx, df)
    df = _compute_hours_and_leisure(df)
    df = _compute_consumption(df)
    df = _compute_choice_indicator(df)
    df = _compute_prior(
        df,
        wage_spec=wage_spec,
        pi0_m=pi0_m,
        pi0_f=pi0_f,
        h_min=h_min,
        h_max=h_max,
        w_min=w_min,
        w_max=w_max,
    )

    # Keep everything for now; RURO_estimation can subset / transform.
    return df


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare RURO–MNL dataset(s) from RURO_prep outputs (singles and/or couples)."
    )
    parser.add_argument(
        "--singles-path",
        type=str,
        help="Path to RURO singles dataset (output of RURO_prep.py).",
    )
    parser.add_argument(
        "--couples-path",
        type=str,
        help="Path to RURO couples dataset (output of RURO_prep.py).",
    )
    parser.add_argument(
        "--country",
        type=str,
        default=TARGET_COUNTRY,
        help=f"EUROMOD country code (default: {TARGET_COUNTRY}).",
    )
    parser.add_argument(
        "--system",
        type=str,
        default=TARGET_SYSTEM,
        help=f"EUROMOD system name (default: {TARGET_SYSTEM}).",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=TARGET_DATASET,
        help=f"EUROMOD dataset name (default: {TARGET_DATASET}).",
    )
    parser.add_argument(
        "--wage-spec",
        type=str,
        choices=["fw", "vw"],
        default=DEFAULT_WAGE_SPEC,
        help="Wage opportunity specification: 'fw' fixed or 'vw' variable.",
    )
    parser.add_argument(
        "--pi0-m",
        type=float,
        default=DEFAULT_PI0_M,
        help="Mass at zero hours for men (pi0_m).",
    )
    parser.add_argument(
        "--pi0-f",
        type=float,
        default=DEFAULT_PI0_F,
        help="Mass at zero hours for women (pi0_f).",
    )
    parser.add_argument(
        "--h-min",
        type=float,
        default=DEFAULT_H_MIN,
        help="Lower bound of hour support for opportunities.",
    )
    parser.add_argument(
        "--h-max",
        type=float,
        default=DEFAULT_H_MAX,
        help="Upper bound of hour support for opportunities.",
    )
    parser.add_argument(
        "--w-min",
        type=float,
        default=DEFAULT_W_MIN,
        help="Lower bound of wage support for opportunities.",
    )
    parser.add_argument(
        "--w-max",
        type=float,
        default=DEFAULT_W_MAX,
        help="Upper bound of wage support for opportunities.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = parse_args(argv)

    if not args.singles_path and not args.couples_path:
        raise ValueError("Provide at least one of --singles-path or --couples-path.")

    paths = []
    if args.singles_path:
        paths.append(("singles", _resolve_input_path(args.singles_path, label="singles")))
    if args.couples_path:
        paths.append(("couples", _resolve_input_path(args.couples_path, label="couples")))

    ctx_kwargs = dict(
        country=args.country,
        system_name=args.system,
        dataset_name=args.dataset,
        wage_spec=args.wage_spec,
        pi0_m=args.pi0_m,
        pi0_f=args.pi0_f,
        h_min=args.h_min,
        h_max=args.h_max,
        w_min=args.w_min,
        w_max=args.w_max,
    )

    for label, input_path in paths:
        if not input_path.exists():
            raise FileNotFoundError(f"RURO {label} file not found: {input_path}")

        LOGGER.info("Processing %s dataset at %s", label, input_path)
        df_mnl = build_ruro_mnl_dataset(input_path=input_path, **ctx_kwargs)
        _write_outputs(df_mnl, input_path, suffix="_RURO_MNL")


if __name__ == "__main__":
    main()
