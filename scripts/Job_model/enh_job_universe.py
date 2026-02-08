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
4. Assigns representative posted values (hours_rep, wage_rep) at bin- or cell-level
5. Computes empirical prior q_j ∝ cell_count (with optional Laplace smoothing)
6. Exports job_universe_{year}.parquet + metadata JSON sidecar

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
type_id : int
    Latent type within occupation (gmm_occ only; -1 for non-employment)
type_draw_id : int
    Within-type contract draw ID (gmm_occ only; 0=component representative, -1 for non-employment)
cell_count : int
    Number of observed working deciders in this job cell
hours_rep : float
    Representative hours for this job (bin-level summary statistic)
wage_rep : float
    Representative wage for this job (bin-level summary statistic)
yem_rep : float
    Representative monthly earnings (wage_rep * hours_rep * 52/12); 0 for job_id=0
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
UNIVERSE_MODE_GMM_OCC = "gmm_occ"  # Occupation-specific latent job types (GMM)
UNIVERSE_MODE_KMEANS_OCC = "kmeans_occ"  # Stub (future)
UNIVERSE_MODE_HIER_OCC = "hier_occ"  # Stub (future)

# Representative value fill modes (for empty cells in full_grid)
REP_FILL_MODE_BIN_MEANS = "bin_means"  # Use observed bin means
REP_FILL_MODE_BIN_MIDPOINTS = "bin_midpoints"  # Use bin midpoints
REP_LEVEL_BIN = "bin"
REP_LEVEL_CELL = "cell"

# GMM latent types (occupation-specific) - contract draws per type
DEFAULT_GMM_CONTRACT_DRAWS = 0

# Summary statistics for representative values
REP_STAT_MEAN = "mean"
REP_STAT_MEDIAN = "median"
REP_STAT_MODE = "mode"

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


def _summarize_numeric(series: pd.Series, method: str) -> float:
    """Summarize a numeric series with a deterministic scalar statistic."""
    x = pd.to_numeric(series, errors="coerce").dropna()
    if x.empty:
        return float("nan")

    if method == REP_STAT_MEAN:
        return float(x.mean())
    if method == REP_STAT_MEDIAN:
        return float(x.median())
    if method == REP_STAT_MODE:
        modes = x.mode(dropna=True)
        if modes.empty:
            return float(x.iloc[0])
        # Deterministic tie-breaker if multiple modes.
        return float(np.min(modes.to_numpy(dtype=float)))
    raise ValueError(f"Unknown representative statistic: {method}")


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

def _trimmed_mean(series: pd.Series, trim_q: float) -> float:
    x = pd.to_numeric(series, errors="coerce").dropna()
    if x.empty:
        return float("nan")
    if trim_q <= 0:
        return float(x.mean())
    lo = x.quantile(trim_q)
    hi = x.quantile(1.0 - trim_q)
    trimmed = x[(x >= lo) & (x <= hi)]
    if trimmed.empty:
        trimmed = x
    return float(trimmed.mean())


def _fit_gmm_for_occ(
    df_occ: pd.DataFrame,
    *,
    kmax: int,
    min_comp_count: int,
    min_comp_weight: float,
    rep_stat: str,
    trim_q: float,
    seed: int,
    cov_type: str,
) -> Dict[str, Any]:
    from sklearn.mixture import GaussianMixture

    lhw = pd.to_numeric(df_occ["lhw_base"], errors="coerce").to_numpy()
    yivwg = pd.to_numeric(df_occ["yivwg_base"], errors="coerce").to_numpy()
    valid = (lhw > 0) & (yivwg > 0)
    lhw = lhw[valid]
    yivwg = yivwg[valid]
    if len(lhw) == 0:
        raise ValueError("No valid observations for GMM fit")

    logw = np.log(yivwg)
    X = np.column_stack([logw, lhw])

    scaler_mean = X.mean(axis=0)
    scaler_std = X.std(axis=0)
    scaler_std = np.where(scaler_std == 0, 1.0, scaler_std)
    X_std = (X - scaler_mean) / scaler_std

    best = None
    for k in range(1, kmax + 1):
        gmm = GaussianMixture(
            n_components=k,
            covariance_type=cov_type,
            random_state=seed,
            reg_covar=1e-6,
        )
        gmm.fit(X_std)
        weights = gmm.weights_
        resp = gmm.predict_proba(X_std)
        hard = resp.argmax(axis=1)
        counts = np.bincount(hard, minlength=k)
        if (weights < min_comp_weight).any() or (counts < min_comp_count).any():
            continue
        bic = gmm.bic(X_std)
        if best is None or bic < best["bic"]:
            best = {
                "gmm": gmm,
                "bic": bic,
                "weights": weights,
                "counts": counts,
                "hard": hard,
            }

    if best is None:
        logging.warning("No GMM fit passed constraints; falling back to K=1.")
        gmm = GaussianMixture(
            n_components=1,
            covariance_type=cov_type,
            random_state=seed,
            reg_covar=1e-6,
        )
        gmm.fit(X_std)
        weights = gmm.weights_
        resp = gmm.predict_proba(X_std)
        hard = resp.argmax(axis=1)
        counts = np.bincount(hard, minlength=1)
    else:
        gmm = best["gmm"]
        weights = best["weights"]
        counts = best["counts"]
        hard = best["hard"]

    if rep_stat == "mean":
        means_std = gmm.means_
        means = means_std * scaler_std + scaler_mean
        wage_rep = np.exp(means[:, 0])
        hours_rep = means[:, 1]
    elif rep_stat == "trimmed_mean":
        wage_rep = []
        hours_rep = []
        for k in range(gmm.n_components):
            mask = hard == k
            if not mask.any():
                wage_rep.append(float(np.exp(scaler_mean[0])))
                hours_rep.append(float(scaler_mean[1]))
                continue
            logw_k = logw[mask]
            lhw_k = lhw[mask]
            wage_rep.append(float(np.exp(_trimmed_mean(pd.Series(logw_k), trim_q))))
            hours_rep.append(float(_trimmed_mean(pd.Series(lhw_k), trim_q)))
        wage_rep = np.array(wage_rep)
        hours_rep = np.array(hours_rep)
    else:
        raise ValueError(f"Unknown gmm rep_stat: {rep_stat}")

    return {
        "k": int(gmm.n_components),
        "weights": weights.tolist(),
        "counts": counts.tolist(),
        "means": gmm.means_.tolist(),
        "covariances": gmm.covariances_.tolist(),
        "scaler_mean": scaler_mean.tolist(),
        "scaler_std": scaler_std.tolist(),
        "hours_rep": hours_rep.tolist(),
        "wage_rep": wage_rep.tolist(),
    }


def _build_job_universe_gmm_occ(
    df: pd.DataFrame,
    *,
    isco_col: str,
    isco_codes: List[int],
    kmax: int,
    min_comp_count: int,
    min_comp_weight: float,
    rep_stat: str,
    trim_q: float,
    contract_draws: int,
    smoothing_alpha: float,
    job_id_mode: str,
    seed: int,
    cov_type: str,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    df = df.copy()
    df["isco1"] = pd.to_numeric(df[isco_col], errors="coerce").fillna(-2).astype(int)
    df = df[df["isco1"].isin(isco_codes)].copy()

    if df.empty:
        raise ValueError("No valid ISCO codes found in working deciders")

    total_working = len(df)
    occ_counts = df["isco1"].value_counts().to_dict()
    occ_share = {int(k): v / total_working for k, v in occ_counts.items()}

    jobs = []
    gmm_meta = {}
    rng = np.random.default_rng(seed)
    draws_per_type = int(max(contract_draws, 0))
    for isco in sorted(isco_codes):
        df_occ = df[df["isco1"] == isco].copy()
        if df_occ.empty:
            logging.warning("No data for ISCO %s; skipping.", isco)
            continue
        occ_fit = _fit_gmm_for_occ(
            df_occ,
            kmax=kmax,
            min_comp_count=min_comp_count,
            min_comp_weight=min_comp_weight,
            rep_stat=rep_stat,
            trim_q=trim_q,
            seed=seed,
            cov_type=cov_type,
        )
        gmm_meta[str(isco)] = occ_fit
        k = occ_fit["k"]
        weights = np.array(occ_fit["weights"], dtype=float)
        means = np.array(occ_fit["means"], dtype=float)
        covariances = np.array(occ_fit["covariances"], dtype=float)
        scaler_mean = np.array(occ_fit["scaler_mean"], dtype=float)
        scaler_std = np.array(occ_fit["scaler_std"], dtype=float)
        for type_id in range(k):
            # Representative (draw_id=0)
            jobs.append(
                {
                    "isco1": int(isco),
                    "type_id": int(type_id),
                    "type_draw_id": 0,
                    "hours_bin": -1,
                    "wage_bin": -1,
                    "cell_count": int(occ_fit["counts"][type_id]),
                    "hours_rep": float(occ_fit["hours_rep"][type_id]),
                    "wage_rep": float(occ_fit["wage_rep"][type_id]),
                    "mix_weight": float(occ_fit["weights"][type_id]),
                }
            )
            if draws_per_type > 0:
                # Sample from the component distribution in standardized space.
                mean_k = means[type_id]
                cov_k = covariances[type_id]
                draws = rng.multivariate_normal(mean_k, cov_k, size=draws_per_type)
                X = draws * scaler_std + scaler_mean
                logw = X[:, 0]
                hours = X[:, 1]
                wage = np.exp(logw)
                # Guard against non-positive hours (rare but possible with Gaussian tails).
                if np.any(hours <= 0):
                    n_bad = int(np.sum(hours <= 0))
                    logging.warning(
                        "GMM draws produced %d non-positive hours for ISCO %s type %s; clipping to 0.1.",
                        n_bad,
                        isco,
                        type_id,
                    )
                    hours = np.maximum(hours, 0.1)
                for draw_id in range(1, draws_per_type + 1):
                    jobs.append(
                        {
                            "isco1": int(isco),
                            "type_id": int(type_id),
                            "type_draw_id": int(draw_id),
                            "hours_bin": -1,
                            "wage_bin": -1,
                            "cell_count": int(occ_fit["counts"][type_id]),
                            "hours_rep": float(hours[draw_id - 1]),
                            "wage_rep": float(wage[draw_id - 1]),
                            "mix_weight": float(occ_fit["weights"][type_id]),
                        }
                    )

    if not jobs:
        raise ValueError("No latent job types created (empty job list)")

    grouped = pd.DataFrame(jobs)

    # Compute prior: occ_share * mix_weight / (1 + contract_draws) with Laplace smoothing.
    denom = 1.0 + draws_per_type
    raw = grouped["isco1"].map(occ_share).to_numpy() * grouped["mix_weight"].to_numpy() / denom
    mean_raw = raw.mean() if len(raw) > 0 else 1.0
    smoothing_constant = smoothing_alpha * mean_raw
    grouped["prior"] = (raw + smoothing_constant) / (raw.sum() + smoothing_constant * len(raw))
    grouped["log_prior"] = np.log(grouped["prior"])
    grouped["q_j_prior"] = grouped["prior"]

    # Assign job_id
    if job_id_mode == JOB_ID_MODE_DETERMINISTIC:
        isco_sorted = sorted(grouped["isco1"].unique())
        isco_rank_map = {code: rank for rank, code in enumerate(isco_sorted)}
        grouped["job_id"] = grouped.apply(
            lambda row: int(
                1
                + isco_rank_map[int(row["isco1"])] * kmax * (draws_per_type + 1)
                + int(row["type_id"]) * (draws_per_type + 1)
                + int(row["type_draw_id"])
            ),
            axis=1,
        )
        grouped = grouped.sort_values(["isco1", "type_id", "type_draw_id"]).reset_index(drop=True)
        grouped["job_idx"] = np.arange(1, len(grouped) + 1, dtype=int)
    else:
        grouped = grouped.sort_values(["isco1", "type_id", "type_draw_id"]).reset_index(drop=True)
        grouped["job_id"] = np.arange(1, len(grouped) + 1, dtype=int)
        grouped["job_idx"] = grouped["job_id"].copy()

    # Prepend job_id=0
    job_0 = pd.DataFrame(
        {
            "job_id": [0],
            "job_idx": [0],
            "hours_bin": [-1],
            "wage_bin": [-1],
            "isco1": [-1],
            "type_id": [-1],
            "type_draw_id": [-1],
            "cell_count": [0],
            "hours_rep": [0.0],
            "wage_rep": [0.0],
            "mix_weight": [0.0],
            "prior": [0.0],
            "log_prior": [-np.inf],
            "q_j_prior": [0.0],
        }
    )

    job_universe = pd.concat([job_0, grouped], ignore_index=True)
    job_universe["yem_rep"] = job_universe["wage_rep"] * job_universe["hours_rep"] * WEEKS_PER_MONTH
    job_universe.loc[job_universe["job_id"] == 0, "yem_rep"] = 0.0

    col_order = [
        "job_id",
        "job_idx",
        "hours_bin",
        "wage_bin",
        "isco1",
        "type_id",
        "type_draw_id",
        "cell_count",
        "hours_rep",
        "wage_rep",
        "yem_rep",
        "prior",
        "log_prior",
        "q_j_prior",
    ]
    job_universe = job_universe[col_order]

    meta = {
        "kmax": kmax,
        "min_comp_count": min_comp_count,
        "min_comp_weight": min_comp_weight,
        "rep_stat": rep_stat,
        "trim_q": trim_q,
        "cov_type": cov_type,
        "contract_draws": draws_per_type,
        "occupations": gmm_meta,
    }

    return job_universe, meta


def _write_gmm_diagnostics(
    gmm_meta: Dict[str, Any],
    output_dir: Path,
    year: int,
) -> None:
    """
    Write per-ISCO diagnostics for GMM latent types to CSV and log a short summary.
    """
    rows = []
    for isco_str, occ in gmm_meta.get("occupations", {}).items():
        try:
            weights = np.array(occ["weights"], dtype=float)
            counts = np.array(occ["counts"], dtype=float)
            hours_rep = np.array(occ["hours_rep"], dtype=float)
            wage_rep = np.array(occ["wage_rep"], dtype=float)
            k = int(occ.get("k", len(weights)))
            # Convert covariances to original scale for rough dispersion diagnostics.
            covs = np.array(occ["covariances"], dtype=float)
            scaler_std = np.array(occ["scaler_std"], dtype=float)
            # logw std and hours std per component in original scale
            logw_std = []
            hours_std = []
            for cov in covs:
                # cov is in standardized space; unscale by std
                cov_orig = cov * np.outer(scaler_std, scaler_std)
                logw_std.append(float(np.sqrt(max(cov_orig[0, 0], 0.0))))
                hours_std.append(float(np.sqrt(max(cov_orig[1, 1], 0.0))))
            rows.append(
                {
                    "isco1": int(isco_str),
                    "k": k,
                    "min_weight": float(np.min(weights)) if weights.size else float("nan"),
                    "max_weight": float(np.max(weights)) if weights.size else float("nan"),
                    "min_count": float(np.min(counts)) if counts.size else float("nan"),
                    "max_count": float(np.max(counts)) if counts.size else float("nan"),
                    "mean_hours_rep": float(np.mean(hours_rep)) if hours_rep.size else float("nan"),
                    "mean_wage_rep": float(np.mean(wage_rep)) if wage_rep.size else float("nan"),
                    "median_hours_rep": float(np.median(hours_rep)) if hours_rep.size else float("nan"),
                    "median_wage_rep": float(np.median(wage_rep)) if wage_rep.size else float("nan"),
                    "mean_logw_std": float(np.mean(logw_std)) if len(logw_std) else float("nan"),
                    "mean_hours_std": float(np.mean(hours_std)) if len(hours_std) else float("nan"),
                }
            )
        except Exception as exc:  # pragma: no cover - defensive
            logging.warning("Failed to summarize GMM diagnostics for ISCO %s: %s", isco_str, exc)

    if not rows:
        logging.warning("GMM diagnostics skipped: no occupation metadata found.")
        return

    diag_df = pd.DataFrame(rows).sort_values("isco1")
    out_csv = output_dir / f"job_universe_{year}__gmm_diagnostics.csv"
    diag_df.to_csv(out_csv, index=False)
    logging.info("Saved GMM diagnostics to %s", out_csv)

    # Short log summary
    logging.info("GMM summary (per ISCO):")
    for _, row in diag_df.iterrows():
        logging.info(
            "  ISCO %s: K=%d, weight[min,max]=[%.3f, %.3f], "
            "count[min,max]=[%.0f, %.0f], mean_hours_rep=%.2f, mean_wage_rep=%.2f",
            int(row["isco1"]),
            int(row["k"]),
            row["min_weight"],
            row["max_weight"],
            row["min_count"],
            row["max_count"],
            row["mean_hours_rep"],
            row["mean_wage_rep"],
        )

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
    rep_level: str = REP_LEVEL_BIN,
    hours_rep_stat: str = REP_STAT_MEAN,
    wage_rep_stat: str = REP_STAT_MEAN,
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
        Representative-value strategy:
        - bin_means: use bin-level summary stats (configured by *_rep_stat)
        - bin_midpoints: use bin midpoints
    hours_rep_stat, wage_rep_stat : str
        Bin-level summary statistics for hours_rep / wage_rep when
        rep_fill_mode == bin_means. One of: mean, median, mode.
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
        .agg(cell_count=("lhw_base", "size"))
        .reset_index()
    )

    cell_rep = None
    if rep_level == REP_LEVEL_CELL:
        cell_rep = (
            df_valid.groupby(["hours_bin", "wage_bin", "isco1"], dropna=False)
            .agg(
                hours_rep=("lhw_base", lambda s: _summarize_numeric(s, hours_rep_stat)),
                wage_rep=("yivwg_base", lambda s: _summarize_numeric(s, wage_rep_stat)),
            )
            .reset_index()
        )

    # Common bin-level representative values (for all universe modes).
    hours_bin_stats = (
        df_valid.groupby("hours_bin")["lhw_base"]
        .apply(lambda s: _summarize_numeric(s, hours_rep_stat))
        .to_dict()
    )
    wage_bin_stats = (
        df_valid.groupby("wage_bin")["yivwg_base"]
        .apply(lambda s: _summarize_numeric(s, wage_rep_stat))
        .to_dict()
    )

    def get_midpoint(label: Tuple[float, float]) -> float:
        return (label[0] + label[1]) / 2.0

    hours_midpoints = {i: get_midpoint(label) for i, label in enumerate(hours_labels)}
    wage_midpoints = {i: get_midpoint(label) for i, label in enumerate(wage_labels)}

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

        n_empty = (grouped["cell_count"] == 0).sum()
        logging.info(
            f"Universe mode: full_grid ({len(grouped)} total cells, "
            f"{n_empty} empty cells)"
        )

    else:
        raise ValueError(f"Unknown universe_mode: {universe_mode}")

    # Assign representative values by chosen strategy. This is done for ALL
    # universe modes to keep the job-bundle interpretation consistent.
    if rep_level == REP_LEVEL_BIN:
        if rep_fill_mode == REP_FILL_MODE_BIN_MEANS:
            grouped["hours_rep"] = grouped["hours_bin"].map(hours_bin_stats)
            grouped["wage_rep"] = grouped["wage_bin"].map(wage_bin_stats)
            grouped["hours_rep"] = grouped["hours_rep"].fillna(grouped["hours_bin"].map(hours_midpoints)).fillna(0.0)
            grouped["wage_rep"] = grouped["wage_rep"].fillna(grouped["wage_bin"].map(wage_midpoints)).fillna(0.0)
            logging.info(
                "Representative values: bin statistics "
                f"(hours={hours_rep_stat}, wage={wage_rep_stat})"
            )
        elif rep_fill_mode == REP_FILL_MODE_BIN_MIDPOINTS:
            grouped["hours_rep"] = grouped["hours_bin"].map(hours_midpoints).fillna(0.0)
            grouped["wage_rep"] = grouped["wage_bin"].map(wage_midpoints).fillna(0.0)
            logging.info("Representative values: bin midpoints (hours and wage)")
        else:
            raise ValueError(f"Unknown rep_fill_mode: {rep_fill_mode}")
    elif rep_level == REP_LEVEL_CELL:
        if cell_rep is None:
            raise ValueError("cell_rep was not computed for rep_level=cell")
        grouped = grouped.merge(cell_rep, on=["hours_bin", "wage_bin", "isco1"], how="left")
        if rep_fill_mode == REP_FILL_MODE_BIN_MEANS:
            grouped["hours_rep"] = grouped["hours_rep"].fillna(grouped["hours_bin"].map(hours_bin_stats))
            grouped["wage_rep"] = grouped["wage_rep"].fillna(grouped["wage_bin"].map(wage_bin_stats))
            grouped["hours_rep"] = grouped["hours_rep"].fillna(grouped["hours_bin"].map(hours_midpoints)).fillna(0.0)
            grouped["wage_rep"] = grouped["wage_rep"].fillna(grouped["wage_bin"].map(wage_midpoints)).fillna(0.0)
            logging.info(
                "Representative values: cell stats with bin-stat fallback "
                f"(hours={hours_rep_stat}, wage={wage_rep_stat})"
            )
        elif rep_fill_mode == REP_FILL_MODE_BIN_MIDPOINTS:
            grouped["hours_rep"] = grouped["hours_rep"].fillna(grouped["hours_bin"].map(hours_midpoints)).fillna(0.0)
            grouped["wage_rep"] = grouped["wage_rep"].fillna(grouped["wage_bin"].map(wage_midpoints)).fillna(0.0)
            logging.info("Representative values: cell stats with bin midpoint fallback")
        else:
            raise ValueError(f"Unknown rep_fill_mode: {rep_fill_mode}")
    else:
        raise ValueError(f"Unknown rep_level: {rep_level}")

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
            "yem_rep": [0.0],
        }
    )

    job_universe = pd.concat([job_0, grouped], ignore_index=True)
    job_universe["yem_rep"] = job_universe["wage_rep"] * job_universe["hours_rep"] * WEEKS_PER_MONTH
    job_universe.loc[job_universe["job_id"] == 0, "yem_rep"] = 0.0

    # Order columns
    col_order = ["job_id", "job_idx", "hours_bin", "wage_bin", "isco1", "cell_count",
                 "hours_rep", "wage_rep", "yem_rep", "prior", "log_prior", "q_j_prior"]
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
    rep_level: str = REP_LEVEL_BIN,
    hours_rep_stat: str = REP_STAT_MEAN,
    wage_rep_stat: str = REP_STAT_MEAN,
    job_id_mode: str = JOB_ID_MODE_SEQUENTIAL,
    min_cell_threshold: int = DEFAULT_MIN_CELL_THRESHOLD,
    smoothing_alpha: float = DEFAULT_SMOOTHING_ALPHA,
    gmm_kmax: int = 6,
    gmm_min_comp_count: int = 50,
    gmm_min_comp_weight: float = 0.03,
    gmm_rep_stat: str = "mean",
    gmm_trim_q: float = 0.10,
    gmm_cov_type: str = "full",
    gmm_contract_draws: int = DEFAULT_GMM_CONTRACT_DRAWS,
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
    hours_rep_stat, wage_rep_stat : str
        Summary statistics for bin-level representative hours/wages
        when rep_fill_mode == bin_means (mean, median, mode)
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

    logging.info(
        f"Working deciders: {len(working_df)} / {len(combined_df)} "
        f"({100*len(working_df)/len(combined_df):.1f}%)"
    )

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
    # 4. Assign bins to working deciders / build latent universe
    # -------------------------------------------------------------------------
    gmm_meta = None
    n_working_deciders = len(working_df)
    if universe_mode == UNIVERSE_MODE_GMM_OCC:
        job_universe, gmm_meta = _build_job_universe_gmm_occ(
            working_df,
            isco_col="loc_ruro",
            isco_codes=isco_codes,
            kmax=gmm_kmax,
            min_comp_count=gmm_min_comp_count,
            min_comp_weight=gmm_min_comp_weight,
            rep_stat=gmm_rep_stat,
            trim_q=gmm_trim_q,
            contract_draws=gmm_contract_draws,
            smoothing_alpha=smoothing_alpha,
            job_id_mode=job_id_mode,
            seed=seed,
            cov_type=gmm_cov_type,
        )
    elif universe_mode in {UNIVERSE_MODE_KMEANS_OCC, UNIVERSE_MODE_HIER_OCC}:
        raise NotImplementedError(f"Universe mode '{universe_mode}' is not yet implemented.")
    else:
        working_binned = _assign_bins(working_df, hours_edges, wage_edges)

        # ---------------------------------------------------------------------
        # 5. Build job universe (grid modes)
        # ---------------------------------------------------------------------
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
            rep_level=rep_level,
            hours_rep_stat=hours_rep_stat,
            wage_rep_stat=wage_rep_stat,
            job_id_mode=job_id_mode,
            min_cell_threshold=min_cell_threshold,
            smoothing_alpha=smoothing_alpha,
        )

    logging.info(f"Job universe: {len(job_universe)-1} working jobs + 1 non-employment")
    logging.info(f"  Total cells: {len(job_universe)}")
    logging.info(f"  prior sum (excluding job 0): {job_universe[job_universe['job_id']>0]['prior'].sum():.6f}")

    if rep_level == REP_LEVEL_BIN and universe_mode not in {UNIVERSE_MODE_GMM_OCC, UNIVERSE_MODE_KMEANS_OCC, UNIVERSE_MODE_HIER_OCC}:
        working_jobs = job_universe[job_universe["job_id"] > 0]
        hours_rep_nunique = working_jobs.groupby("hours_bin")["hours_rep"].nunique()
        wage_rep_nunique = working_jobs.groupby("wage_bin")["wage_rep"].nunique()
        if (hours_rep_nunique > 1).any():
            logging.warning("Hours_rep not unique within some hours_bin (rep_level=bin).")
        if (wage_rep_nunique > 1).any():
            logging.warning("Wage_rep not unique within some wage_bin (rep_level=bin).")

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
        "rep_level": rep_level,
        "hours_rep_stat": hours_rep_stat,
        "wage_rep_stat": wage_rep_stat,
        "gmm_kmax": gmm_kmax,
        "gmm_min_comp_count": gmm_min_comp_count,
        "gmm_min_comp_weight": gmm_min_comp_weight,
        "gmm_rep_stat": gmm_rep_stat,
        "gmm_trim_q": gmm_trim_q,
        "gmm_cov_type": gmm_cov_type,
        "gmm_contract_draws": gmm_contract_draws,
        "job_id_mode": job_id_mode,
        "n_jobs": int(len(job_universe) - 1),  # Excluding job 0
        "n_cells_total": int(len(job_universe)),
        "n_empty_cells": int((job_universe["cell_count"] == 0).sum()),
        "n_working_deciders": int(n_working_deciders),
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
    if gmm_meta is not None:
        metadata["gmm_occ"] = gmm_meta
        job_map_cols = ["job_id", "isco1", "type_id"]
        if "type_draw_id" in job_universe.columns:
            job_map_cols.append("type_draw_id")
        job_map = job_universe[job_universe["job_id"] > 0][job_map_cols].to_dict(orient="records")
        metadata["job_id_map"] = job_map
        _write_gmm_diagnostics(gmm_meta, output_dir, year)

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
        choices=[
            UNIVERSE_MODE_EMPIRICAL_PRUNED,
            UNIVERSE_MODE_EMPIRICAL_ALL,
            UNIVERSE_MODE_FULL_GRID,
            UNIVERSE_MODE_GMM_OCC,
            UNIVERSE_MODE_KMEANS_OCC,
            UNIVERSE_MODE_HIER_OCC,
        ],
        default=UNIVERSE_MODE_EMPIRICAL_PRUNED,
        help=f"Universe construction mode: {UNIVERSE_MODE_EMPIRICAL_PRUNED} (drop rare cells, backward compat), "
             f"{UNIVERSE_MODE_EMPIRICAL_ALL} (keep all observed), {UNIVERSE_MODE_FULL_GRID} (complete grid with filled empty cells, RECOMMENDED), "
             f"{UNIVERSE_MODE_GMM_OCC} (occupation-specific latent job types)",
    )
    ap.add_argument(
        "--rep-level",
        type=str,
        choices=[REP_LEVEL_BIN, REP_LEVEL_CELL],
        default=REP_LEVEL_BIN,
        help="Representative-value level: bin (default, posted bundle) or cell (legacy behavior)",
    )
    ap.add_argument(
        "--rep-fill-mode",
        type=str,
        choices=[REP_FILL_MODE_BIN_MEANS, REP_FILL_MODE_BIN_MIDPOINTS],
        default=REP_FILL_MODE_BIN_MEANS,
        help=f"Representative-value strategy: "
             f"{REP_FILL_MODE_BIN_MEANS} (bin-level stats), {REP_FILL_MODE_BIN_MIDPOINTS} (bin midpoints)",
    )
    ap.add_argument(
        "--gmm-kmax",
        type=int,
        default=6,
        help="Maximum components per occupation for gmm_occ (default: 6)",
    )
    ap.add_argument(
        "--gmm-min-comp-count",
        type=int,
        default=50,
        help="Minimum count per component for gmm_occ (default: 50)",
    )
    ap.add_argument(
        "--gmm-min-comp-weight",
        type=float,
        default=0.03,
        help="Minimum component weight for gmm_occ (default: 0.03)",
    )
    ap.add_argument(
        "--gmm-rep-stat",
        type=str,
        choices=["mean", "trimmed_mean"],
        default="mean",
        help="Representative value for gmm_occ components (mean or trimmed_mean)",
    )
    ap.add_argument(
        "--gmm-trim-q",
        type=float,
        default=0.10,
        help="Trim quantile for trimmed_mean (default: 0.10)",
    )
    ap.add_argument(
        "--gmm-cov-type",
        type=str,
        default="full",
        choices=["full", "diag", "tied", "spherical"],
        help="GaussianMixture covariance_type for gmm_occ",
    )
    ap.add_argument(
        "--gmm-contract-draws",
        type=int,
        default=DEFAULT_GMM_CONTRACT_DRAWS,
        help="Number of within-type contract draws to add per GMM component (default: 0)",
    )
    ap.add_argument(
        "--hours-rep-stat",
        type=str,
        choices=[REP_STAT_MEAN, REP_STAT_MEDIAN, REP_STAT_MODE],
        default=REP_STAT_MEAN,
        help="Summary stat for hours_rep when --rep-fill-mode=bin_means (default: mean)",
    )
    ap.add_argument(
        "--wage-rep-stat",
        type=str,
        choices=[REP_STAT_MEAN, REP_STAT_MEDIAN, REP_STAT_MODE],
        default=REP_STAT_MEAN,
        help="Summary stat for wage_rep when --rep-fill-mode=bin_means (default: mean)",
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
        rep_level=args.rep_level,
        hours_rep_stat=args.hours_rep_stat,
        wage_rep_stat=args.wage_rep_stat,
        job_id_mode=args.job_id_mode,
        min_cell_threshold=args.min_cell_threshold,
        smoothing_alpha=args.smoothing_alpha,
        gmm_kmax=args.gmm_kmax,
        gmm_min_comp_count=args.gmm_min_comp_count,
        gmm_min_comp_weight=args.gmm_min_comp_weight,
        gmm_rep_stat=args.gmm_rep_stat,
        gmm_trim_q=args.gmm_trim_q,
        gmm_cov_type=args.gmm_cov_type,
        gmm_contract_draws=args.gmm_contract_draws,
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
