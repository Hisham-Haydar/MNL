#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
enh_job_universe.py
===================

Build discrete job universe grid from observed working deciders in RURO_ready data.

A "job" is a discrete bundle: (hours_bin, wage_bin, isco1-digit occupation).

This script:
1. Loads singles/couples RURO_ready.parquet from enh_RURO_prep.py
2. Defines hours bins (fixed cutpoints) and wage bins (data-dependent deciles/quantiles)
3. Builds job grid by counting observed (hours_bin, wage_bin, isco1) cells among working deciders
4. Computes empirical prior q_j ∝ cell_count (with optional Laplace smoothing)
5. Exports job_universe_{year}.parquet + metadata JSON sidecar

Output schema:
--------------
job_id : int
    Unique job identifier (0 = non-employment, 1..N = working jobs)
hours_bin : int
    Hours bin ID (0-indexed; -1 for non-employment)
wage_bin : int
    Wage bin ID (0-indexed; -1 for non-employment)
isco1 : int
    ISCO 1-digit occupation code (1-9; -1 for non-employment)
cell_count : int
    Number of observed working deciders in this job cell
hours_rep : float
    Representative hours for this job (mean of observations in cell)
wage_rep : float
    Representative wage for this job (mean of observations in cell)
q_j_prior : float
    Proposal prior probability (sums to 1 over working jobs, excluding job 0)

"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_HOURS_CUTPOINTS = [5, 16, 31, 43, 71]  # Bins: [5-15], [16-30], [31-42], [43-70]
DEFAULT_WAGE_BINS = 10  # Deciles
DEFAULT_MIN_CELL_THRESHOLD = 5  # Drop jobs with <5 observations
DEFAULT_SMOOTHING_ALPHA = 0.01  # Laplace smoothing (1% of mean cell count)
DEFAULT_SEED = 13
WEEKS_PER_MONTH = 52.0 / 12.0

# ISCO 1-digit valid codes
VALID_ISCO1 = list(range(1, 10))  # 1..9 major groups
OPTIONAL_ISCO1 = [0]  # Armed forces (include if present)
EXCLUDE_ISCO1 = [-1, -2]  # -1 non-applicable, -2 unknown

# Universe construction modes
UNIVERSE_MODE_EMPIRICAL_PRUNED = "empirical_pruned"  # Drop rare cells (original behavior)
UNIVERSE_MODE_EMPIRICAL_ALL = "empirical_all"  # Keep all observed cells
UNIVERSE_MODE_FULL_GRID = "full_grid"  # Complete grid with filled empty cells

# Representative value fill modes (for empty cells in full_grid)
REP_FILL_MODE_BIN_MEANS = "bin_means"  # Use observed bin means
REP_FILL_MODE_BIN_MIDPOINTS = "bin_midpoints"  # Use bin midpoints

# Job ID assignment modes
JOB_ID_MODE_DETERMINISTIC = "deterministic"  # Stable formula-based job_id
JOB_ID_MODE_SEQUENTIAL = "sequential"  # Sequential 1..N (original)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_dataframe(path: Path) -> pd.DataFrame:
    """Read DataFrame from parquet, csv, or pickle."""
    suf = path.suffix.lower()
    if suf == ".parquet":
        return pd.read_parquet(path)  # type: ignore[arg-type]
    if suf == ".csv":
        return pd.read_csv(path)
    if suf in {".pkl", ".pickle"}:
        return pd.read_pickle(path)
    raise ValueError(f"Unsupported format: {path}")


def _setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# ---------------------------------------------------------------------------
# Binning functions
# ---------------------------------------------------------------------------

def _parse_cutpoints(cutpoints_str: str) -> List[float]:
    """Parse comma-separated cutpoints string."""
    return [float(x.strip()) for x in cutpoints_str.split(",")]


def _build_hours_bins(cutpoints: List[float]) -> Tuple[np.ndarray, List[Tuple[float, float]]]:
    """
    Build hours bins from cutpoints.

    Parameters
    ----------
    cutpoints : list of float
        Bin edges. E.g., [5, 16, 31, 43, 71] creates bins:
        [5-15], [16-30], [31-42], [43-70]

    Returns
    -------
    edges : ndarray
        Bin edges for pd.cut (includes -inf, +inf)
    bin_labels : list of (lower, upper) tuples
        Human-readable bin ranges
    """
    if len(cutpoints) < 2:
        raise ValueError("Need at least 2 cutpoints to define bins")

    # pd.cut uses [lower, upper) convention
    # We want: [5, 15], [16, 30], [31, 42], [43, 70]
    # So edges: [-inf, 15.5, 30.5, 42.5, +inf]
    edges = [-np.inf]
    bin_labels = []

    for i in range(len(cutpoints) - 1):
        lower = cutpoints[i]
        upper = cutpoints[i + 1] - 1  # Inclusive upper bound
        bin_labels.append((lower, upper))
        # Edge at midpoint between upper and next lower
        edges.append(upper + 0.5)

    edges.append(np.inf)

    return np.array(edges), bin_labels


def _build_wage_bins(
    df: pd.DataFrame,
    *,
    wage_col: str = "yivwg_base",
    n_bins: int = DEFAULT_WAGE_BINS,
) -> Tuple[np.ndarray, List[Tuple[float, float]]]:
    """
    Build wage bins from observed working deciders (data-dependent quantiles).

    Parameters
    ----------
    df : DataFrame
        Working deciders with positive wages
    wage_col : str
        Wage column name
    n_bins : int
        Number of bins (e.g., 10 for deciles)

    Returns
    -------
    edges : ndarray
        Quantile-based bin edges
    bin_labels : list of (lower, upper) tuples
        Bin ranges
    """
    wages = pd.to_numeric(df[wage_col], errors="coerce").dropna()
    wages = wages[wages > 0]

    if len(wages) == 0:
        raise ValueError("No positive wages found for binning")

    # Compute quantiles
    quantiles = np.linspace(0, 1, n_bins + 1)
    edges = wages.quantile(quantiles).values

    # Ensure unique edges (in case of ties)
    edges = np.unique(edges)
    if len(edges) < 2:
        raise ValueError("Wage distribution has no variation (all same value)")

    # Extend edges to cover full range
    edges[0] = -np.inf
    edges[-1] = np.inf

    # Build bin labels
    bin_labels = []
    for i in range(len(edges) - 1):
        # For quantile bins, use actual edge values (not midpoints)
        lower = edges[i] if not np.isinf(edges[i]) else wages.min()
        upper = edges[i + 1] if not np.isinf(edges[i + 1]) else wages.max()
        bin_labels.append((lower, upper))

    return edges, bin_labels


def _assign_bins(
    df: pd.DataFrame,
    hours_edges: np.ndarray,
    wage_edges: np.ndarray,
) -> pd.DataFrame:
    """
    Assign hours_bin and wage_bin IDs to each observation.

    Parameters
    ----------
    df : DataFrame
        Working deciders with lhw_base and yivwg_base
    hours_edges, wage_edges : ndarray
        Bin edges from _build_hours_bins / _build_wage_bins

    Returns
    -------
    df_binned : DataFrame
        Input with added columns: hours_bin, wage_bin (0-indexed)
    """
    df = df.copy()

    # Assign bins (pd.cut returns categorical; convert to 0-indexed int)
    df["hours_bin"] = pd.cut(
        df["lhw_base"], bins=hours_edges, labels=False, include_lowest=True
    ).astype("Int64")

    df["wage_bin"] = pd.cut(
        df["yivwg_base"], bins=wage_edges, labels=False, include_lowest=True
    ).astype("Int64")

    # Convert to regular int (pd.cut may return nullable Int64)
    df["hours_bin"] = df["hours_bin"].fillna(-1).astype(int)
    df["wage_bin"] = df["wage_bin"].fillna(-1).astype(int)

    return df


# ---------------------------------------------------------------------------
# Job universe construction
# ---------------------------------------------------------------------------

def _compute_deterministic_job_id(
    hours_bin: int,
    wage_bin: int,
    isco1: int,
    *,
    isco_rank_map: Dict[int, int],
    n_hours_bins: int,
    n_wage_bins: int,
) -> int:
    """
    Compute deterministic job_id from (hours_bin, wage_bin, isco1).

    Formula: job_id = 1 + (isco_rank * H * W) + ((hours_bin-1) * W) + (wage_bin-1)

    where:
    - isco_rank: 0-indexed rank in sorted ISCO codes
    - H: number of hours bins
    - W: number of wage bins
    - hours_bin, wage_bin: 0-indexed bin IDs

    Parameters
    ----------
    hours_bin, wage_bin, isco1 : int
        Job bundle coordinates (0-indexed)
    isco_rank_map : dict
        Mapping from isco1 code to 0-indexed rank
    n_hours_bins, n_wage_bins : int
        Grid dimensions

    Returns
    -------
    job_id : int
        Deterministic job identifier (1-indexed)
    """
    isco_rank = isco_rank_map[isco1]
    job_id = 1 + (isco_rank * n_hours_bins * n_wage_bins) + (hours_bin * n_wage_bins) + wage_bin
    return int(job_id)


def _build_job_universe(
    df: pd.DataFrame,
    *,
    isco_col: str = "loc_ruro",
    isco_codes: List[int],
    n_hours_bins: int,
    n_wage_bins: int,
    hours_labels: List[Tuple[float, float]],
    wage_labels: List[Tuple[float, float]],
    universe_mode: str = UNIVERSE_MODE_EMPIRICAL_PRUNED,
    rep_fill_mode: str = REP_FILL_MODE_BIN_MEANS,
    job_id_mode: str = JOB_ID_MODE_SEQUENTIAL,
    min_cell_threshold: int = DEFAULT_MIN_CELL_THRESHOLD,
    smoothing_alpha: float = DEFAULT_SMOOTHING_ALPHA,
) -> pd.DataFrame:
    """
    Build job universe from working deciders with assigned bins.

    Steps:
    1. Group by (hours_bin, wage_bin, isco1): count, mean hours/wage
    2. Apply universe mode:
       - empirical_pruned: drop cells with count < min_cell_threshold
       - empirical_all: keep all observed cells
       - full_grid: create complete (isco × hours × wage) grid, fill empty cells
    3. Compute prior q_j ∝ cell_count (with Laplace smoothing)
    4. Assign job_id (deterministic or sequential)
    5. Prepend job_id=0 (non-employment)

    Parameters
    ----------
    df : DataFrame
        Binned working deciders (has hours_bin, wage_bin, isco1 cols)
    isco_col : str
        ISCO column name (default: loc_ruro)
    isco_codes : list of int
        Valid ISCO codes for this dataset
    n_hours_bins, n_wage_bins : int
        Grid dimensions
    hours_labels, wage_labels : list of (lower, upper) tuples
        Bin ranges for computing midpoints
    universe_mode : str
        One of: empirical_pruned, empirical_all, full_grid
    rep_fill_mode : str
        Representative-value strategy for hours_rep / wage_rep in full_grid:
        - bin_means: use observed bin means for all cells (default)
        - bin_midpoints: use bin midpoints for all cells
    job_id_mode : str
        One of: deterministic, sequential
    min_cell_threshold : int
        Drop cells with fewer observations (empirical_pruned only)
    smoothing_alpha : float
        Laplace smoothing parameter (fraction of mean cell count)

    Returns
    -------
    job_universe : DataFrame
        Schema: job_id, job_idx, hours_bin, wage_bin, isco1, cell_count, hours_rep, wage_rep,
                prior, log_prior, q_j_prior (alias for prior)
    """
    # Ensure isco1 is int
    df = df.copy()
    df["isco1"] = pd.to_numeric(df[isco_col], errors="coerce").fillna(-2).astype(int)

    # Filter valid ISCO codes
    df_valid = df[df["isco1"].isin(isco_codes)].copy()

    if len(df_valid) == 0:
        raise ValueError("No valid ISCO codes found in working deciders")

    # Group by (hours_bin, wage_bin, isco1) - get empirical cells
    empirical_cells = (
        df_valid.groupby(["hours_bin", "wage_bin", "isco1"], dropna=False)
        .agg(
            cell_count=("lhw_base", "size"),
            hours_rep=("lhw_base", "mean"),
            wage_rep=("yivwg_base", "mean"),
        )
        .reset_index()
    )

    # Apply universe mode
    if universe_mode == UNIVERSE_MODE_EMPIRICAL_PRUNED:
        # Drop small cells (original behavior)
        grouped = empirical_cells[empirical_cells["cell_count"] >= min_cell_threshold].copy()
        if len(grouped) == 0:
            raise ValueError(f"No cells survive min_cell_threshold={min_cell_threshold}")
        logging.info(f"Universe mode: empirical_pruned (dropped {len(empirical_cells) - len(grouped)} cells < {min_cell_threshold})")

    elif universe_mode == UNIVERSE_MODE_EMPIRICAL_ALL:
        # Keep all observed cells
        grouped = empirical_cells.copy()
        logging.info(f"Universe mode: empirical_all ({len(grouped)} observed cells)")

    elif universe_mode == UNIVERSE_MODE_FULL_GRID:
        # Create complete (isco × hours × wage) grid
        from itertools import product
        full_grid = pd.DataFrame(
            list(product(range(n_hours_bins), range(n_wage_bins), isco_codes)),
            columns=["hours_bin", "wage_bin", "isco1"]
        )

        # Merge empirical cells onto full grid
        grouped = full_grid.merge(
            empirical_cells,
            on=["hours_bin", "wage_bin", "isco1"],
            how="left"
        )

        # Fill missing cell_count with 0
        grouped["cell_count"] = grouped["cell_count"].fillna(0).astype(int)

        # Build common bin-level representative values
        # (used for all cells to keep job bundles consistent by bin)
        hours_bin_means = df_valid.groupby("hours_bin")["lhw_base"].mean().to_dict()
        wage_bin_means = df_valid.groupby("wage_bin")["yivwg_base"].mean().to_dict()

        def get_midpoint(label):
            return (label[0] + label[1]) / 2.0

        hours_midpoints = {i: get_midpoint(label) for i, label in enumerate(hours_labels)}
        wage_midpoints = {i: get_midpoint(label) for i, label in enumerate(wage_labels)}

        # Set representative values according to strategy.
        # NOTE: This applies to ALL cells (not only empties), so each job in the
        # same bin shares the same representative hours/wage by construction.
        if rep_fill_mode == REP_FILL_MODE_BIN_MEANS:
            grouped["hours_rep"] = grouped["hours_bin"].map(hours_bin_means)
            grouped["wage_rep"] = grouped["wage_bin"].map(wage_bin_means)
            # Fallback to midpoints if an entire bin has no observations.
            grouped["hours_rep"] = grouped["hours_rep"].fillna(grouped["hours_bin"].map(hours_midpoints)).fillna(0.0)
            grouped["wage_rep"] = grouped["wage_rep"].fillna(grouped["wage_bin"].map(wage_midpoints)).fillna(0.0)

        elif rep_fill_mode == REP_FILL_MODE_BIN_MIDPOINTS:
            grouped["hours_rep"] = grouped["hours_bin"].map(hours_midpoints).fillna(0.0)
            grouped["wage_rep"] = grouped["wage_bin"].map(wage_midpoints).fillna(0.0)

        else:
            raise ValueError(f"Unknown rep_fill_mode: {rep_fill_mode}")

        n_empty = (grouped["cell_count"] == 0).sum()
        logging.info(
            f"Universe mode: full_grid ({len(grouped)} total cells, "
            f"{n_empty} empty cells; representatives set by {rep_fill_mode})"
        )

    else:
        raise ValueError(f"Unknown universe_mode: {universe_mode}")

    # Compute prior with Laplace smoothing
    mean_count = grouped["cell_count"].mean() if len(grouped) > 0 else 1.0
    smoothing_constant = smoothing_alpha * mean_count

    grouped["prior"] = (grouped["cell_count"] + smoothing_constant) / (
        grouped["cell_count"].sum() + smoothing_constant * len(grouped)
    )
    grouped["log_prior"] = np.log(grouped["prior"])

    # Add alias for backward compatibility
    grouped["q_j_prior"] = grouped["prior"]

    # Assign job_id based on mode
    if job_id_mode == JOB_ID_MODE_DETERMINISTIC:
        # Create ISCO rank map (0-indexed)
        isco_sorted = sorted(isco_codes)
        isco_rank_map = {code: rank for rank, code in enumerate(isco_sorted)}

        # Compute deterministic job_id for each row
        grouped["job_id"] = grouped.apply(
            lambda row: _compute_deterministic_job_id(
                int(row["hours_bin"]),
                int(row["wage_bin"]),
                int(row["isco1"]),
                isco_rank_map=isco_rank_map,
                n_hours_bins=n_hours_bins,
                n_wage_bins=n_wage_bins,
            ),
            axis=1
        )

        # Also store sequential index for backward compat
        grouped["job_idx"] = np.arange(1, len(grouped) + 1, dtype=int)

        logging.info(f"Job ID mode: deterministic (formula-based, range: {grouped['job_id'].min()}-{grouped['job_id'].max()})")

    elif job_id_mode == JOB_ID_MODE_SEQUENTIAL:
        # Sequential 1..N (original behavior)
        grouped["job_id"] = np.arange(1, len(grouped) + 1, dtype=int)
        grouped["job_idx"] = grouped["job_id"].copy()

        logging.info(f"Job ID mode: sequential (1..{len(grouped)})")

    else:
        raise ValueError(f"Unknown job_id_mode: {job_id_mode}")

    # Prepend job_id=0 (non-employment)
    job_0 = pd.DataFrame(
        {
            "job_id": [0],
            "job_idx": [0],
            "hours_bin": [-1],
            "wage_bin": [-1],
            "isco1": [-1],
            "cell_count": [0],
            "hours_rep": [0.0],
            "wage_rep": [0.0],
            "prior": [0.0],
            "log_prior": [-np.inf],
            "q_j_prior": [0.0],
        }
    )

    job_universe = pd.concat([job_0, grouped], ignore_index=True)

    # Order columns
    col_order = ["job_id", "job_idx", "hours_bin", "wage_bin", "isco1", "cell_count",
                 "hours_rep", "wage_rep", "prior", "log_prior", "q_j_prior"]
    job_universe = job_universe[col_order]

    return job_universe


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def build_job_universe_from_ruro_ready(
    singles_path: Path | None,
    couples_path: Path | None,
    *,
    output_dir: Path,
    year: int,
    hours_cutpoints: List[float] = DEFAULT_HOURS_CUTPOINTS,
    wage_bins: int = DEFAULT_WAGE_BINS,
    isco_codes: List[int] | None = None,
    include_isco0: bool = False,
    universe_mode: str = UNIVERSE_MODE_EMPIRICAL_PRUNED,
    rep_fill_mode: str = REP_FILL_MODE_BIN_MEANS,
    job_id_mode: str = JOB_ID_MODE_SEQUENTIAL,
    min_cell_threshold: int = DEFAULT_MIN_CELL_THRESHOLD,
    smoothing_alpha: float = DEFAULT_SMOOTHING_ALPHA,
    seed: int = DEFAULT_SEED,
) -> Dict[str, Any]:
    """
    Main driver: load RURO_ready data, build job universe, export outputs.

    Parameters
    ----------
    singles_path, couples_path : Path or None
        Paths to *_RURO_ready.parquet files
    output_dir : Path
        Output directory for job universe
    year : int
        Year label for output files
    hours_cutpoints : list of float
        Hours bin edges
    wage_bins : int
        Number of wage bins
    min_cell_threshold : int
        Minimum observations per job cell
    smoothing_alpha : float
        Laplace smoothing parameter
    seed : int
        Random seed (for reproducibility)

    Returns
    -------
    metadata : dict
        Summary statistics and paths
    """
    np.random.seed(seed)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine ISCO codes
    if isco_codes is None:
        isco_codes = VALID_ISCO1.copy()
        if include_isco0:
            isco_codes = OPTIONAL_ISCO1 + isco_codes
    else:
        isco_codes = sorted(isco_codes)

    logging.info(f"ISCO codes: {isco_codes}")

    # -------------------------------------------------------------------------
    # 1. Load and combine singles/couples
    # -------------------------------------------------------------------------
    dfs = []

    if singles_path is not None:
        singles_path = Path(singles_path)
        if not singles_path.exists():
            raise FileNotFoundError(f"Singles file not found: {singles_path}")
        singles_df = _read_dataframe(singles_path)
        dfs.append(singles_df)
        logging.info(f"Loaded singles: {len(singles_df)} rows")

    if couples_path is not None:
        couples_path = Path(couples_path)
        if not couples_path.exists():
            raise FileNotFoundError(f"Couples file not found: {couples_path}")
        couples_df = _read_dataframe(couples_path)
        dfs.append(couples_df)
        logging.info(f"Loaded couples: {len(couples_df)} rows")

    if len(dfs) == 0:
        raise ValueError("Must provide at least one of --singles-path or --couples-path")

    combined_df = pd.concat(dfs, ignore_index=True)
    logging.info(f"Combined dataset: {len(combined_df)} rows")

    # -------------------------------------------------------------------------
    # 2. Filter working deciders
    # -------------------------------------------------------------------------
    # Required columns
    required_cols = {"is_worker", "lhw_base", "yivwg_base", "loc_ruro"}
    missing = required_cols - set(combined_df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    # Filter: working deciders (is_worker==1, positive hours/wage)
    is_worker = pd.to_numeric(combined_df["is_worker"], errors="coerce").fillna(0).astype(int)
    lhw = pd.to_numeric(combined_df["lhw_base"], errors="coerce").fillna(0.0)
    yivwg = pd.to_numeric(combined_df["yivwg_base"], errors="coerce").fillna(0.0)

    working_mask = (is_worker == 1) & (lhw > 0) & (yivwg > 0)
    working_df = combined_df[working_mask].copy()

    logging.info(f"Working deciders: {len(working_df)} / {len(combined_df)} ({100*len(working_df)/len(combined_df):.1f}%)")

    if len(working_df) == 0:
        raise ValueError("No working deciders found (is_worker==1, lhw_base>0, yivwg_base>0)")

    # -------------------------------------------------------------------------
    # 3. Build bins
    # -------------------------------------------------------------------------
    hours_edges, hours_labels = _build_hours_bins(hours_cutpoints)
    logging.info(f"Hours bins: {len(hours_labels)} bins from cutpoints {hours_cutpoints}")
    for i, (lo, hi) in enumerate(hours_labels):
        logging.info(f"  Bin {i}: [{lo:.1f}, {hi:.1f}]")

    wage_edges, wage_labels = _build_wage_bins(working_df, n_bins=wage_bins)
    logging.info(f"Wage bins: {len(wage_labels)} bins (data-dependent {wage_bins}-tiles)")
    for i, (lo, hi) in enumerate(wage_labels):
        logging.info(f"  Bin {i}: [{lo:.2f}, {hi:.2f}]")

    # -------------------------------------------------------------------------
    # 4. Assign bins to working deciders
    # -------------------------------------------------------------------------
    working_binned = _assign_bins(working_df, hours_edges, wage_edges)

    # -------------------------------------------------------------------------
    # 5. Build job universe
    # -------------------------------------------------------------------------
    job_universe = _build_job_universe(
        working_binned,
        isco_col="loc_ruro",
        isco_codes=isco_codes,
        n_hours_bins=len(hours_labels),
        n_wage_bins=len(wage_labels),
        hours_labels=hours_labels,
        wage_labels=wage_labels,
        universe_mode=universe_mode,
        rep_fill_mode=rep_fill_mode,
        job_id_mode=job_id_mode,
        min_cell_threshold=min_cell_threshold,
        smoothing_alpha=smoothing_alpha,
    )

    logging.info(f"Job universe: {len(job_universe)-1} working jobs + 1 non-employment")
    logging.info(f"  Total cells: {len(job_universe)}")
    logging.info(f"  prior sum (excluding job 0): {job_universe[job_universe['job_id']>0]['prior'].sum():.6f}")

    # Top 10 jobs by prior
    top10 = job_universe[job_universe["job_id"] > 0].nlargest(10, "prior")
    logging.info("Top 10 jobs by prior probability:")
    for _, row in top10.iterrows():
        logging.info(
            f"  job_id={int(row['job_id']):5d} job_idx={int(row['job_idx']):3d} "
            f"(h_bin={int(row['hours_bin'])}, w_bin={int(row['wage_bin'])}, isco1={int(row['isco1'])}): "
            f"prior={row['prior']:.4f}, n={int(row['cell_count'])}"
        )

    # -------------------------------------------------------------------------
    # 6. Export job universe
    # -------------------------------------------------------------------------
    output_path = output_dir / f"job_universe_{year}.parquet"
    job_universe.to_parquet(output_path, index=False)  # type: ignore[arg-type]
    logging.info(f"Saved job universe to {output_path}")

    # -------------------------------------------------------------------------
    # 7. Export metadata sidecar
    # -------------------------------------------------------------------------
    metadata = {
        "year": year,
        "seed": seed,
        "hours_cutpoints": hours_cutpoints,
        "hours_bin_labels": [(float(lo), float(hi)) for lo, hi in hours_labels],
        "n_hours_bins": len(hours_labels),
        "wage_bins": wage_bins,
        "wage_cutpoints": wage_edges.tolist(),
        "wage_bin_labels": [(float(lo), float(hi)) for lo, hi in wage_labels],
        "n_wage_bins": len(wage_labels),
        "isco1_codes": isco_codes,
        "include_isco0": include_isco0,
        "universe_mode": universe_mode,
        "rep_fill_mode": rep_fill_mode,
        "job_id_mode": job_id_mode,
        "n_jobs": int(len(job_universe) - 1),  # Excluding job 0
        "n_cells_total": int(len(job_universe)),
        "n_empty_cells": int((job_universe["cell_count"] == 0).sum()),
        "n_working_deciders": int(len(working_binned)),
        "min_cell_threshold": min_cell_threshold,
        "smoothing_alpha": smoothing_alpha,
        "prior_sum": float(job_universe[job_universe["job_id"] > 0]["prior"].sum()),
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "script": "enh_job_universe.py",
        "input_files": {
            "singles": str(singles_path) if singles_path else None,
            "couples": str(couples_path) if couples_path else None,
        },
        "output_file": str(output_path),
    }

    metadata_path = output_dir / f"job_universe_{year}__meta.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logging.info(f"Saved metadata to {metadata_path}")

    return metadata


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Build discrete job universe from RURO_ready data for job-choice RURO model."
    )
    ap.add_argument(
        "--singles-path",
        type=Path,
        default=None,
        help="Path to singles_RURO_ready.parquet",
    )
    ap.add_argument(
        "--couples-path",
        type=Path,
        default=None,
        help="Path to couples_RURO_ready.parquet",
    )
    ap.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Output directory for job universe and metadata",
    )
    ap.add_argument(
        "--year",
        type=int,
        required=True,
        help="Year label for output files (e.g., 2016)",
    )
    ap.add_argument(
        "--hours-cutpoints",
        type=str,
        default=",".join(map(str, DEFAULT_HOURS_CUTPOINTS)),
        help="Comma-separated hours bin cutpoints (default: 5,16,31,43,71)",
    )
    ap.add_argument(
        "--wage-bins",
        type=int,
        default=DEFAULT_WAGE_BINS,
        help="Number of wage bins (e.g., 10 for deciles, 5 for quintiles)",
    )
    ap.add_argument(
        "--isco-codes",
        type=str,
        default=None,
        help="Comma-separated ISCO codes to include (default: 1-9, or 0,1-9 if --include-isco0)",
    )
    ap.add_argument(
        "--include-isco0",
        type=int,
        choices=[0, 1],
        default=0,
        help="Include ISCO code 0 (armed forces): 0=no, 1=yes (default: 0)",
    )
    ap.add_argument(
        "--universe-mode",
        type=str,
        choices=[UNIVERSE_MODE_EMPIRICAL_PRUNED, UNIVERSE_MODE_EMPIRICAL_ALL, UNIVERSE_MODE_FULL_GRID],
        default=UNIVERSE_MODE_EMPIRICAL_PRUNED,
        help=f"Universe construction mode: {UNIVERSE_MODE_EMPIRICAL_PRUNED} (drop rare cells, backward compat), "
             f"{UNIVERSE_MODE_EMPIRICAL_ALL} (keep all observed), {UNIVERSE_MODE_FULL_GRID} (complete grid with filled empty cells, RECOMMENDED)",
    )
    ap.add_argument(
        "--rep-fill-mode",
        type=str,
        choices=[REP_FILL_MODE_BIN_MEANS, REP_FILL_MODE_BIN_MIDPOINTS],
        default=REP_FILL_MODE_BIN_MEANS,
        help=f"Representative value fill mode for empty cells in full_grid: "
             f"{REP_FILL_MODE_BIN_MEANS} (observed bin means), {REP_FILL_MODE_BIN_MIDPOINTS} (bin midpoints)",
    )
    ap.add_argument(
        "--job-id-mode",
        type=str,
        choices=[JOB_ID_MODE_DETERMINISTIC, JOB_ID_MODE_SEQUENTIAL],
        default=JOB_ID_MODE_SEQUENTIAL,
        help=f"Job ID assignment mode: {JOB_ID_MODE_DETERMINISTIC} (stable formula-based), "
             f"{JOB_ID_MODE_SEQUENTIAL} (sequential 1..N, backward compat)",
    )
    ap.add_argument(
        "--min-cell-threshold",
        type=int,
        default=DEFAULT_MIN_CELL_THRESHOLD,
        help="Minimum observations per job cell (only used in empirical_pruned mode)",
    )
    ap.add_argument(
        "--smoothing-alpha",
        type=float,
        default=DEFAULT_SMOOTHING_ALPHA,
        help="Laplace smoothing parameter (fraction of mean cell count)",
    )
    ap.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Random seed for reproducibility",
    )
    ap.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    return ap.parse_args()


def main() -> None:
    args = parse_args()
    _setup_logging(args.log_level)

    hours_cutpoints = _parse_cutpoints(args.hours_cutpoints)

    # Parse ISCO codes if provided
    isco_codes_list = None
    if args.isco_codes is not None:
        isco_codes_list = [int(x.strip()) for x in args.isco_codes.split(",")]

    metadata = build_job_universe_from_ruro_ready(
        singles_path=args.singles_path,
        couples_path=args.couples_path,
        output_dir=args.output_dir,
        year=args.year,
        hours_cutpoints=hours_cutpoints,
        wage_bins=args.wage_bins,
        isco_codes=isco_codes_list,
        include_isco0=bool(args.include_isco0),
        universe_mode=args.universe_mode,
        rep_fill_mode=args.rep_fill_mode,
        job_id_mode=args.job_id_mode,
        min_cell_threshold=args.min_cell_threshold,
        smoothing_alpha=args.smoothing_alpha,
        seed=args.seed,
    )

    print("\n" + "=" * 80)
    print("Job Universe Built Successfully")
    print("=" * 80)
    print(f"Output: {metadata['output_file']}")
    print(f"Metadata: {metadata['output_file'].replace('.parquet', '__meta.json')}")
    print(f"Number of jobs: {metadata['n_jobs']} (excluding non-employment)")
    print(f"Working deciders: {metadata['n_working_deciders']}")
    print("=" * 80)


if __name__ == "__main__":
    main()
