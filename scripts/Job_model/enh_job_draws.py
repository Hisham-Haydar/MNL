#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
enh_job_draws.py
================

Generate RURO opportunity draws by sampling from discrete job universe grid.

This script is the job-choice analog of enh_RURO_draws.py. Instead of sampling
continuous (hours, wage) from Uniform distributions, we sample discrete job_id
from the empirical job universe built by enh_job_universe.py.

Key differences from continuous RURO:
--------------------------------------
1. Jobs are discrete bundles: (hours_bin, wage_bin, isco1)
2. Opportunity set Q_i contains {job_0, job_1, ..., job_N} where job_0 is non-employment
3. Proposal prior: q_j from empirical job frequencies (computed in enh_job_universe.py)
4. Hours/wage are REPRESENTATIVE values for the job cell, not individual draws

Output compatibility:
---------------------
Output schema is designed as a DROP-IN REPLACEMENT for enh_RURO_draws.py output.
enh_RURO_euromod.py can consume job draws WITHOUT modification by using column aliases:
  - lhw_draw → lhw, hours
  - yivwg_draw → yivwg, wage
  - yem_draw → yem

Usage:
------
python scripts/Job_model/enh_job_draws.py \\
  --singles-path "U:/Data/processed/fr/2016/singles_RURO_ready.parquet" \\
  --couples-path "U:/Data/processed/fr/2016/couples_RURO_ready.parquet" \\
  --job-universe "U:/Data/processed/fr/2016/job_model/job_universe_2016.parquet" \\
  --job-metadata "U:/Data/processed/fr/2016/job_model/job_universe_2016__meta.json" \\
  --n-draws 99 \\
  --pi0-m 0.10 \\
  --pi0-f 0.10 \\
  --seed 13

"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import math
import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_N_DRAWS = 99
DEFAULT_PI0_M = 0.10  # Mass at non-employment for men
DEFAULT_PI0_F = 0.10  # Mass at non-employment for women
DEFAULT_SEED = 13
WEEKS_PER_MONTH = 52.0 / 12.0

# Baseline modes
BASELINE_MODE_OBSERVED = "observed"  # Use actual lhw_base/yivwg_base
BASELINE_MODE_CELL_REP = "cell_rep"  # Use hours_rep/wage_rep from job universe (default)

# ---------------------------------------------------------------------------
# I/O Helpers
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


def _write_dataframe(df: pd.DataFrame, output_path: Path) -> None:
    """Write DataFrame to parquet."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False, engine="pyarrow")  # type: ignore[arg-type]


def _write_draws_metadata(output_path: Path, metadata: Dict[str, Any]) -> None:
    """Write draws metadata sidecar JSON."""
    sidecar_path = output_path.parent / f"{output_path.stem}__drawsmeta.json"

    metadata_json = {
        **metadata,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "script": "enh_job_draws.py",
    }

    with open(sidecar_path, "w", encoding="utf-8") as f:
        json.dump(metadata_json, f, indent=2)
    logging.info(f"Wrote draws metadata to {sidecar_path}")


def _compute_id_multiplier(max_draw: int) -> int:
    """
    Compute ID multiplier for EUROMOD stage.

    ID multiplier ensures unique IDs: idperson_euromod = idperson_true * multiplier + draw
    """
    if max_draw < 0:
        return 1000
    multiplier = 10 ** math.ceil(math.log10(max_draw + 1))
    return max(multiplier, 1000)


# ---------------------------------------------------------------------------
# Baseline job assignment (draw=0)
# ---------------------------------------------------------------------------

def _assign_baseline_job(
    df: pd.DataFrame,
    job_universe: pd.DataFrame,
    hours_cutpoints: list[float],
    wage_cutpoints: list[float],
) -> pd.DataFrame:
    """
    Assign baseline job_id to each observation based on observed (lhw_base, yivwg_base, isco1).

    For working deciders: find job_id matching their bins + occupation.
    If exact match is missing, fall back deterministically to a job with the
    same (hours_bin, wage_bin) regardless of occupation.
    For non-workers (lhw_base==0): job_id=0.

    Parameters
    ----------
    df : DataFrame
        RURO_ready data with lhw_base, yivwg_base, loc_ruro
    job_universe : DataFrame
        Job grid with job_id, hours_bin, wage_bin, isco1
    hours_cutpoints, wage_cutpoints : list of float
        Bin edges for mapping observed values to bins

    Returns
    -------
    df_with_job : DataFrame
        Input with added column: baseline_job_id
    """
    df = df.copy()

    # Extract baseline labor inputs
    lhw = pd.to_numeric(df["lhw_base"], errors="coerce").fillna(0.0)
    yivwg = pd.to_numeric(df["yivwg_base"], errors="coerce").fillna(0.0)
    isco1_obs = pd.to_numeric(df.get("loc_ruro", -1), errors="coerce").fillna(-1).astype(int)

    # Non-workers: job_id=0
    baseline_job_id = np.zeros(len(df), dtype=int)

    # Working mask
    working_mask = (lhw > 0) & (yivwg > 0)

    if working_mask.any():
        # Build hours bins (same logic as enh_job_universe.py)
        hours_edges = [-np.inf]
        for i in range(len(hours_cutpoints) - 1):
            upper = hours_cutpoints[i + 1] - 1
            hours_edges.append(upper + 0.5)
        hours_edges.append(np.inf)
        hours_edges = np.array(hours_edges)

        # Wage bins
        wage_edges = np.array(wage_cutpoints)

        # Assign bins for working obs
        hours_bin_obs = pd.cut(
            lhw[working_mask], bins=hours_edges, labels=False, include_lowest=True
        ).fillna(-1).astype(int)

        wage_bin_obs = pd.cut(
            yivwg[working_mask], bins=wage_edges, labels=False, include_lowest=True
        ).fillna(-1).astype(int)

        # Build lookup: (hours_bin, wage_bin, isco1) -> job_id
        job_lookup = {}
        hw_lookup = {}
        hw_score = {}
        supported_isco = set()
        fallback_job_id = 0
        fallback_score = -np.inf
        prior_col = "prior" if "prior" in job_universe.columns else (
            "q_j_prior" if "q_j_prior" in job_universe.columns else None
        )

        for _, row in job_universe.iterrows():
            if row["job_id"] == 0:
                continue  # Skip non-employment
            h_bin = int(row["hours_bin"])
            w_bin = int(row["wage_bin"])
            isco = int(row["isco1"])
            jid = int(row["job_id"])
            key = (h_bin, w_bin, isco)
            job_lookup[key] = jid
            supported_isco.add(isco)

            # Use prior (if available) to choose deterministic fallback job.
            score = float(row[prior_col]) if prior_col is not None else -float(jid)
            hw_key = (h_bin, w_bin)
            if (hw_key not in hw_lookup) or (score > hw_score[hw_key]):
                hw_lookup[hw_key] = jid
                hw_score[hw_key] = score
            if score > fallback_score:
                fallback_job_id = jid
                fallback_score = score

        exact_match_count = 0
        fallback_hw_count = 0
        fallback_global_count = 0
        invalid_isco_count = 0
        invalid_bin_count = 0

        # Map working obs to job_id
        working_indices = np.where(working_mask)[0]
        for i, idx in enumerate(working_indices):
            h_bin = hours_bin_obs.iloc[i]
            w_bin = wage_bin_obs.iloc[i]
            isco = isco1_obs.iloc[idx]

            key = (h_bin, w_bin, isco)
            jid = job_lookup.get(key)
            if jid is not None:
                baseline_job_id[idx] = jid
                exact_match_count += 1
                continue

            if isco not in supported_isco:
                invalid_isco_count += 1
            if h_bin < 0 or w_bin < 0:
                invalid_bin_count += 1

            # Fallback 1: keep observed bins, relax occupation.
            hw_key = (h_bin, w_bin)
            jid = hw_lookup.get(hw_key)
            if jid is not None:
                baseline_job_id[idx] = jid
                fallback_hw_count += 1
                continue

            # Fallback 2: most likely working job in universe.
            baseline_job_id[idx] = fallback_job_id
            fallback_global_count += 1

        n_working = int(working_mask.sum())
        n_fallback = fallback_hw_count + fallback_global_count
        if n_fallback > 0:
            logging.warning(
                "Baseline job assignment used fallback for %d/%d working rows "
                "(exact=%d, same_bin=%d, global=%d).",
                n_fallback,
                n_working,
                exact_match_count,
                fallback_hw_count,
                fallback_global_count,
            )
            logging.warning(
                "Fallback diagnostics: invalid_isco=%d, invalid_bin=%d",
                invalid_isco_count,
                invalid_bin_count,
            )

    df["baseline_job_id"] = baseline_job_id

    return df


# ---------------------------------------------------------------------------
# Vectorized job draws
# ---------------------------------------------------------------------------

def generate_job_draws_long(
    df: pd.DataFrame,
    job_universe: pd.DataFrame,
    job_metadata: Dict[str, Any],
    *,
    n_draws: int = DEFAULT_N_DRAWS,
    pi0_m: float = DEFAULT_PI0_M,
    pi0_f: float = DEFAULT_PI0_F,
    baseline_mode: str = BASELINE_MODE_CELL_REP,
    rng_seed: int = DEFAULT_SEED,
) -> pd.DataFrame:
    """
    Generate long-format job draws for RURO estimation (vectorized).

    Steps:
    ------
    1. Identify deciders (hh_IsHead==1 or hh_IsPartner==1)
    2. Create draw=0 for ALL persons (baseline job_id from bins)
    3. For deciders only, sample draws 1..K:
       - With prob pi0_g: job_id=0 (non-employment)
       - With prob 1-pi0_g: sample job_id from q_j_prior
    4. Merge job attributes (hours_rep, wage_rep, isco1) onto draws
    5. Compute proposal densities (log_q_job, log_q_state, log_q_total)
    6. Create EUROMOD-compatible aliases (lhw, yivwg, yem)

    Parameters
    ----------
    df : DataFrame
        RURO_ready data (one row per person)
    job_universe : DataFrame
        Job grid from enh_job_universe.py
    job_metadata : dict
        Metadata with hours_cutpoints, wage_cutpoints
    n_draws : int
        Number of simulated draws per decider
    pi0_m, pi0_f : float
        Mass at non-employment (gender-specific)
    rng_seed : int
        Random seed

    Returns
    -------
    long_df : DataFrame
        Long format: (idperson, draw) with job attributes
    """
    rng = np.random.default_rng(rng_seed)

    df = df.copy().reset_index(drop=True)

    # -------------------------------------------------------------------------
    # 1. Ensure true IDs
    # -------------------------------------------------------------------------
    if "idperson_true" not in df.columns:
        if "idperson" in df.columns:
            df["idperson_true"] = df["idperson"].copy()
        else:
            raise KeyError("RURO_ready must contain 'idperson' or 'idperson_true'")

    if "idhh_true" not in df.columns:
        if "idhh" in df.columns:
            df["idhh_true"] = df["idhh"].copy()
        else:
            raise KeyError("RURO_ready must contain 'idhh' or 'idhh_true'")

    # -------------------------------------------------------------------------
    # 2. Decider mask
    # -------------------------------------------------------------------------
    has_decider_flags = "hh_IsHead" in df.columns

    if has_decider_flags:
        hh_is_head = pd.to_numeric(df["hh_IsHead"], errors="coerce").fillna(0).astype(int)
        hh_is_partner = pd.to_numeric(df.get("hh_IsPartner", 0), errors="coerce").fillna(0).astype(int)
        is_decider = (hh_is_head == 1) | (hh_is_partner == 1)

        n_deciders = is_decider.sum()
        n_nondeciders = (~is_decider).sum()
        logging.info(f"Job draws: {n_deciders} deciders, {n_nondeciders} non-deciders")
    else:
        logging.warning(
            "hh_IsHead/hh_IsPartner not found. Treating all persons as deciders."
        )
        is_decider = pd.Series(True, index=df.index)

    # -------------------------------------------------------------------------
    # 3. Gender for π₀
    # -------------------------------------------------------------------------
    if "dgn" in df.columns:
        dgn = pd.to_numeric(df["dgn"], errors="coerce").fillna(1).astype(int)
    else:
        dgn = pd.Series(1, index=df.index, dtype=int)

    pi0_vec = np.where(dgn == 1, pi0_m, pi0_f)

    # -------------------------------------------------------------------------
    # 4. Assign baseline job_id to all observations
    # -------------------------------------------------------------------------
    hours_cutpoints = job_metadata["hours_cutpoints"]
    wage_cutpoints = job_metadata["wage_cutpoints"]

    df_with_job = _assign_baseline_job(df, job_universe, hours_cutpoints, wage_cutpoints)

    # -------------------------------------------------------------------------
    # 5. Create draw=0 (baseline) for ALL persons
    # -------------------------------------------------------------------------
    df_draw0 = df_with_job.copy()
    df_draw0["draw"] = 0
    df_draw0["is_decider"] = is_decider.astype(int)
    df_draw0["is_chosen"] = is_decider.astype(int)  # Chosen alternative for deciders
    df_draw0["job_id"] = df_draw0["baseline_job_id"]

    # Merge job attributes from job_universe
    job_attrs = job_universe[["job_id", "hours_bin", "wage_bin", "isco1", "hours_rep", "wage_rep"]].copy()

    df_draw0 = df_draw0.merge(job_attrs, on="job_id", how="left", suffixes=("", "_job"))

    # For draw=0, use baseline labor inputs based on mode
    if baseline_mode == BASELINE_MODE_OBSERVED:
        # Use actual observed values
        df_draw0["lhw_draw"] = pd.to_numeric(df_draw0["lhw_base"], errors="coerce").fillna(0.0)
        df_draw0["yivwg_draw"] = pd.to_numeric(df_draw0["yivwg_base"], errors="coerce").fillna(0.0)
    elif baseline_mode == BASELINE_MODE_CELL_REP:
        # Use representative values from job universe (default)
        df_draw0["lhw_draw"] = df_draw0["hours_rep"].fillna(0.0)
        df_draw0["yivwg_draw"] = df_draw0["wage_rep"].fillna(0.0)
    else:
        raise ValueError(f"Unknown baseline_mode: {baseline_mode}")

    df_draw0["yem_draw"] = df_draw0["lhw_draw"] * df_draw0["yivwg_draw"] * WEEKS_PER_MONTH

    # Proposal density: draw=0 convention is prior=1.0, log_prior=0.0
    df_draw0["prior"] = 1.0
    df_draw0["log_prior"] = 0.0
    # Keep legacy columns for backward compatibility (set to 0)
    df_draw0["log_q_job"] = 0.0
    df_draw0["log_q_state"] = 0.0
    df_draw0["log_q_total"] = 0.0

    # Draw-specific occupation: deciders use sampled job occupation.
    # Keep observed occupation in loc_ruro_obs for diagnostics.
    if "isco1" in df_draw0.columns:
        isco_draw0 = pd.to_numeric(df_draw0["isco1"], errors="coerce").fillna(-1).astype(int)
        df_draw0["loc_ruro_draw"] = isco_draw0
        if "loc_ruro" in df_draw0.columns:
            loc_obs = pd.to_numeric(df_draw0["loc_ruro"], errors="coerce").fillna(-1).astype(int)
            df_draw0["loc_ruro_obs"] = loc_obs
            # Cast to int first so pandas does not warn on dtype-mismatch assignment.
            df_draw0["loc_ruro"] = loc_obs
            decider_mask_draw0 = df_draw0["is_decider"] == 1
            df_draw0.loc[decider_mask_draw0, "loc_ruro"] = isco_draw0[decider_mask_draw0]
        else:
            df_draw0["loc_ruro_obs"] = -1
            df_draw0["loc_ruro"] = np.where(df_draw0["is_decider"] == 1, isco_draw0, -1)

    # If no simulated draws requested, return baseline only
    if n_draws == 0:
        return df_draw0.reset_index(drop=True)

    # -------------------------------------------------------------------------
    # 6. Simulated draws (1..K) for DECIDERS ONLY
    # -------------------------------------------------------------------------
    decider_df = df_with_job[is_decider].copy().reset_index(drop=True)
    n_deciders_actual = len(decider_df)

    if n_deciders_actual == 0:
        logging.warning("No deciders found. Returning draw=0 only.")
        return df_draw0.reset_index(drop=True)

    logging.info(f"Generating {n_draws} job draws for {n_deciders_actual} deciders (vectorized)...")

    # -------------------------------------------------------------------------
    # 6a. Replicate deciders n_draws times
    # -------------------------------------------------------------------------
    person_idx = np.repeat(np.arange(n_deciders_actual), n_draws)
    draw_nums = np.tile(np.arange(1, n_draws + 1), n_deciders_actual)

    n_sim = n_deciders_actual * n_draws

    # Get pi0 for each simulated record
    decider_pi0 = pi0_vec[is_decider.to_numpy()]
    pi0_sim = decider_pi0[person_idx]

    # -------------------------------------------------------------------------
    # 6b. Sample employment vs non-employment
    # -------------------------------------------------------------------------
    u_emp = rng.random(n_sim)
    is_nonemployment = u_emp < pi0_sim
    is_working = ~is_nonemployment

    # -------------------------------------------------------------------------
    # 6c. Sample job_id for working draws
    # -------------------------------------------------------------------------
    job_id_sim = np.zeros(n_sim, dtype=int)  # Default: non-employment

    # Working jobs: job_id >= 1
    working_jobs = job_universe[job_universe["job_id"] > 0].copy()

    if len(working_jobs) == 0:
        raise ValueError("No working jobs in job_universe (only job_id=0)")

    job_ids = working_jobs["job_id"].to_numpy()

    # Use 'prior' column if available, else fall back to 'q_j_prior'
    if "prior" in working_jobs.columns:
        q_j = working_jobs["prior"].to_numpy()
    else:
        q_j = working_jobs["q_j_prior"].to_numpy()

    # Normalize q_j (should already sum to 1, but ensure)
    q_j = q_j / q_j.sum()

    n_working = is_working.sum()
    if n_working > 0:
        # Sample job_id from multinomial
        job_id_sim[is_working] = rng.choice(job_ids, size=n_working, p=q_j)

    # -------------------------------------------------------------------------
    # 6d. Build simulated draws DataFrame
    # -------------------------------------------------------------------------
    sim_df = decider_df.iloc[person_idx].copy().reset_index(drop=True)

    sim_df["draw"] = draw_nums
    sim_df["is_decider"] = 1
    sim_df["is_chosen"] = 0  # Not chosen (draw=0 is chosen)
    sim_df["job_id"] = job_id_sim

    # Merge job attributes
    sim_df = sim_df.merge(job_attrs, on="job_id", how="left", suffixes=("", "_job"))

    # Hours/wage from job universe (representative values)
    sim_df["lhw_draw"] = sim_df["hours_rep"].fillna(0.0)
    sim_df["yivwg_draw"] = sim_df["wage_rep"].fillna(0.0)
    sim_df["yem_draw"] = sim_df["lhw_draw"] * sim_df["yivwg_draw"] * WEEKS_PER_MONTH

    # -------------------------------------------------------------------------
    # 6e. Compute proposal density components
    # -------------------------------------------------------------------------
    eps = 1e-15

    # log_q_state: mass at employment vs non-employment
    log_q_state = np.where(
        is_nonemployment,
        np.log(np.clip(pi0_sim, eps, 1.0)),
        np.log(np.clip(1.0 - pi0_sim, eps, 1.0)),
    )

    # log_q_job: log probability of sampled job (for working draws)
    log_q_job = np.zeros(n_sim, dtype=float)
    job_prior = np.zeros(n_sim, dtype=float)  # q_j for sampled job

    if n_working > 0:
        # Map job_id to q_j
        job_to_q = dict(zip(job_ids, q_j))
        for i in np.where(is_working)[0]:
            jid = job_id_sim[i]
            qj = job_to_q.get(jid, eps)
            job_prior[i] = qj
            log_q_job[i] = np.log(qj)

    # Canonical prior and log_prior columns
    # For non-employment: prior = pi0
    # For employment: prior = (1 - pi0) * q_j
    prior = np.where(
        is_nonemployment,
        pi0_sim,
        (1.0 - pi0_sim) * job_prior
    )
    log_prior = np.log(np.clip(prior, eps, 1.0))

    sim_df["prior"] = prior
    sim_df["log_prior"] = log_prior
    # Keep legacy columns for backward compatibility
    sim_df["log_q_state"] = log_q_state
    sim_df["log_q_job"] = log_q_job
    sim_df["log_q_total"] = log_q_state + log_q_job

    # Draw-specific occupation for simulated decider draws.
    if "isco1" in sim_df.columns:
        isco_sim = pd.to_numeric(sim_df["isco1"], errors="coerce").fillna(-1).astype(int)
        sim_df["loc_ruro_draw"] = isco_sim
        if "loc_ruro" in sim_df.columns and "loc_ruro_obs" not in sim_df.columns:
            sim_df["loc_ruro_obs"] = pd.to_numeric(sim_df["loc_ruro"], errors="coerce").fillna(-1).astype(int)
        sim_df["loc_ruro"] = isco_sim

    # -------------------------------------------------------------------------
    # 7. Compute legacy proposal density for draw=0 (for backward compatibility)
    # -------------------------------------------------------------------------
    # Note: Draw=0 already has prior=1.0, log_prior=0.0 set above.
    # We compute log_q_state/log_q_job/log_q_total for legacy compatibility,
    # but these are NOT used in estimation (prior/log_prior are canonical).

    decider_baseline_job_id = df_with_job.loc[is_decider, "baseline_job_id"].to_numpy()
    decider_lhw_base = pd.to_numeric(df_with_job.loc[is_decider, "lhw_base"], errors="coerce").fillna(0.0).to_numpy()

    dec_work0 = decider_lhw_base > 0

    # log_q_state for baseline
    log_q_state0 = np.where(
        dec_work0,
        np.log(np.clip(1.0 - decider_pi0, eps, 1.0)),
        np.log(np.clip(decider_pi0, eps, 1.0)),
    )

    # log_q_job for baseline working jobs
    log_q_job0 = np.zeros(n_deciders_actual, dtype=float)
    if dec_work0.any():
        job_to_q = dict(zip(job_ids, q_j))
        for i, jid in enumerate(decider_baseline_job_id):
            if dec_work0[i] and jid > 0:
                log_q_job0[i] = np.log(job_to_q.get(jid, eps))

    df_draw0.loc[is_decider, "log_q_state"] = log_q_state0
    df_draw0.loc[is_decider, "log_q_job"] = log_q_job0
    df_draw0.loc[is_decider, "log_q_total"] = log_q_state0 + log_q_job0

    # -------------------------------------------------------------------------
    # 8. Concatenate draw=0 + simulated draws
    # -------------------------------------------------------------------------
    long_df = pd.concat([df_draw0, sim_df], ignore_index=True)

    # -------------------------------------------------------------------------
    # 9. Create EUROMOD-compatible aliases
    # -------------------------------------------------------------------------
    long_df["lhw"] = long_df["lhw_draw"]
    long_df["yivwg"] = long_df["yivwg_draw"]
    long_df["yem"] = long_df["yem_draw"]
    long_df["hours"] = long_df["lhw_draw"]
    long_df["wage"] = long_df["yivwg_draw"]

    # -------------------------------------------------------------------------
    # 10. Sort and finalize
    # -------------------------------------------------------------------------
    sort_cols = ["idperson_true", "draw"]
    if "idhh_true" in long_df.columns:
        sort_cols = ["idhh_true"] + sort_cols

    long_df = long_df.sort_values(sort_cols).reset_index(drop=True)

    # Ensure draw is int
    long_df["draw"] = long_df["draw"].astype(int)

    logging.info(f"Job draws: {len(long_df)} total rows ({len(df_draw0)} baseline + {len(sim_df)} simulated)")

    return long_df


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate_baseline_job_assignment(df: pd.DataFrame, baseline_mode: str) -> None:
    """
    Validate draw=0 baseline compliance.

    Checks:
    - draw=0 hours/wage match selected baseline mode
      * observed: lhw_base/yivwg_base
      * cell_rep: hours_rep/wage_rep
    - job_id=0 iff lhw_draw==0
    """
    draw0 = df[df["draw"] == 0].copy()
    deciders = draw0[draw0["is_decider"] == 1].copy()

    if len(deciders) == 0:
        logging.warning("No deciders at draw=0 for validation")
        return

    # Hours/wage check depends on baseline mode
    lhw_draw = pd.to_numeric(deciders["lhw_draw"], errors="coerce").fillna(0.0)
    yivwg_draw = pd.to_numeric(deciders["yivwg_draw"], errors="coerce").fillna(0.0)
    if baseline_mode == BASELINE_MODE_OBSERVED:
        lhw_ref = pd.to_numeric(deciders["lhw_base"], errors="coerce").fillna(0.0)
        yivwg_ref = pd.to_numeric(deciders["yivwg_base"], errors="coerce").fillna(0.0)
        hours_label = "lhw_base"
        wage_label = "yivwg_base"
    elif baseline_mode == BASELINE_MODE_CELL_REP:
        lhw_ref = pd.to_numeric(deciders["hours_rep"], errors="coerce").fillna(0.0)
        yivwg_ref = pd.to_numeric(deciders["wage_rep"], errors="coerce").fillna(0.0)
        hours_label = "hours_rep"
        wage_label = "wage_rep"
    else:
        raise ValueError(f"Unknown baseline_mode in validation: {baseline_mode}")

    h_diff = np.abs(lhw_draw - lhw_ref)
    w_diff = np.abs(yivwg_draw - yivwg_ref)

    if (h_diff > 1e-6).any():
        n_violations = int((h_diff > 1e-6).sum())
        logging.error(f"Baseline hours compliance failed: {n_violations} violations")
        raise ValueError(f"draw=0 hours do not match {hours_label} for {n_violations} deciders")

    if (w_diff > 1e-6).any():
        n_violations = int((w_diff > 1e-6).sum())
        logging.error(f"Baseline wage compliance failed: {n_violations} violations")
        raise ValueError(f"draw=0 wages do not match {wage_label} for {n_violations} deciders")

    # Job_id=0 iff lhw_draw==0
    job_id = deciders["job_id"].to_numpy()
    is_working = lhw_draw > 0

    bad_nonworking = (job_id != 0) & (~is_working)
    bad_working = (job_id == 0) & is_working

    if bad_nonworking.any() or bad_working.any():
        logging.error(f"Job assignment violations: {bad_nonworking.sum()} non-workers with job>0, {bad_working.sum()} workers with job=0")
        raise ValueError("Job assignment inconsistent with working status")

    logging.info(f"Baseline compliance validated: {len(deciders)} deciders OK")


def _validate_couples_draw_consistency(df: pd.DataFrame, household_type: str) -> None:
    """Validate couples have same draw sets."""
    if household_type != "couples":
        return

    if "idhh_true" not in df.columns or "draw" not in df.columns:
        logging.warning("Cannot validate couples: missing idhh_true or draw")
        return

    is_decider = df.get("is_decider", pd.Series(1, index=df.index))
    deciders_df = df[is_decider == 1].copy()

    if len(deciders_df) == 0:
        return

    violations = []

    for idhh, group in deciders_df.groupby("idhh_true"):
        n_deciders = group["idperson_true"].nunique() if "idperson_true" in group.columns else 0

        if n_deciders < 2:
            continue

        # Get draw sets per decider
        draw_sets = group.groupby("idperson_true")["draw"].apply(set)

        if len(draw_sets) < 2:
            continue

        # Check if all deciders have same draw set
        first_set = next(iter(draw_sets.values))
        if not all(s == first_set for s in draw_sets.values):
            violations.append({
                "idhh_true": idhh,
                "draw_sets": {pid: sorted(draws) for pid, draws in draw_sets.items()},
            })

    if violations:
        logging.error(f"Couples consistency failed: {len(violations)} households")
        for v in violations[:5]:
            logging.error(f"  Household {v['idhh_true']}: {v['draw_sets']}")
        raise ValueError(f"Couples draw consistency failed for {len(violations)} households")

    logging.info(f"Couples draw consistency validated for {household_type}")


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def generate_draws_from_ruro_ready(
    ruro_ready_path: Path,
    job_universe_path: Path,
    job_metadata_path: Path,
    *,
    household_type: str,
    n_draws: int = DEFAULT_N_DRAWS,
    pi0_m: float = DEFAULT_PI0_M,
    pi0_f: float = DEFAULT_PI0_F,
    baseline_mode: str = BASELINE_MODE_CELL_REP,
    rng_seed: int = DEFAULT_SEED,
) -> pd.DataFrame:
    """
    Main driver: load data, generate job draws, validate.

    Parameters
    ----------
    ruro_ready_path : Path
        Path to *_RURO_ready.parquet
    job_universe_path : Path
        Path to job_universe_{year}.parquet
    job_metadata_path : Path
        Path to job_universe_{year}__meta.json
    household_type : str
        "singles" or "couples"
    n_draws : int
        Number of draws per decider
    pi0_m, pi0_f : float
        Mass at non-employment
    rng_seed : int
        Random seed

    Returns
    -------
    long_df : DataFrame
        Job draws in long format
    """
    # Load inputs
    df = _read_dataframe(ruro_ready_path)
    job_universe = _read_dataframe(job_universe_path)

    with open(job_metadata_path, "r", encoding="utf-8") as f:
        job_metadata = json.load(f)

    logging.info(f"Loaded {household_type}: {len(df)} rows")
    logging.info(f"Job universe: {len(job_universe)} jobs")

    # Generate draws
    long_df = generate_job_draws_long(
        df,
        job_universe,
        job_metadata,
        n_draws=n_draws,
        pi0_m=pi0_m,
        pi0_f=pi0_f,
        baseline_mode=baseline_mode,
        rng_seed=rng_seed,
    )

    # Validate
    _validate_baseline_job_assignment(long_df, baseline_mode=baseline_mode)
    _validate_couples_draw_consistency(long_df, household_type)

    return long_df


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Generate RURO job draws by sampling from discrete job universe."
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
        "--job-universe",
        type=Path,
        required=True,
        help="Path to job_universe_{year}.parquet",
    )
    ap.add_argument(
        "--job-metadata",
        type=Path,
        required=True,
        help="Path to job_universe_{year}__meta.json",
    )
    ap.add_argument(
        "--n-draws",
        type=int,
        default=DEFAULT_N_DRAWS,
        help="Number of simulated draws per decider",
    )
    ap.add_argument(
        "--pi0-m",
        type=float,
        default=DEFAULT_PI0_M,
        help="Mass at non-employment for men",
    )
    ap.add_argument(
        "--pi0-f",
        type=float,
        default=DEFAULT_PI0_F,
        help="Mass at non-employment for women",
    )
    ap.add_argument(
        "--baseline-mode",
        type=str,
        choices=[BASELINE_MODE_OBSERVED, BASELINE_MODE_CELL_REP],
        default=BASELINE_MODE_CELL_REP,
        help=f"Baseline (draw=0) mode: {BASELINE_MODE_CELL_REP} (use hours_rep/wage_rep from job universe, default), "
             f"{BASELINE_MODE_OBSERVED} (use actual lhw_base/yivwg_base)",
    )
    ap.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Random seed",
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

    if args.singles_path is None and args.couples_path is None:
        raise ValueError("Must provide at least one of --singles-path or --couples-path")

    # Process singles
    if args.singles_path is not None:
        singles_path = Path(args.singles_path)
        if not singles_path.exists():
            raise FileNotFoundError(f"Singles file not found: {singles_path}")

        logging.info("=" * 80)
        logging.info("Processing SINGLES")
        logging.info("=" * 80)

        singles_long = generate_draws_from_ruro_ready(
            singles_path,
            args.job_universe,
            args.job_metadata,
            household_type="singles",
            n_draws=args.n_draws,
            pi0_m=args.pi0_m,
            pi0_f=args.pi0_f,
            baseline_mode=args.baseline_mode,
            rng_seed=args.seed,
        )

        # Output path: next to input, with suffix _jobdraws
        output_path = singles_path.parent / f"{singles_path.stem}_jobdraws.parquet"
        _write_dataframe(singles_long, output_path)

        # Metadata
        max_draw = int(singles_long["draw"].max())
        id_multiplier = _compute_id_multiplier(max_draw)

        metadata = {
            "n_draws": args.n_draws,
            "max_draw": max_draw,
            "seed": args.seed,
            "id_multiplier": id_multiplier,
            "household_type": "singles",
            "baseline_mode": args.baseline_mode,
            "distributional_params": {
                "pi0_m": args.pi0_m,
                "pi0_f": args.pi0_f,
            },
            "input_file": str(singles_path),
            "job_universe": str(args.job_universe),
            "job_metadata": str(args.job_metadata),
            "output_schema": list(singles_long.columns),
        }

        _write_draws_metadata(output_path, metadata)

        print(f"\nSingles job draws saved to: {output_path}")
        print(f"Metadata: {output_path.parent / (output_path.stem + '__drawsmeta.json')}")

    # Process couples
    if args.couples_path is not None:
        couples_path = Path(args.couples_path)
        if not couples_path.exists():
            raise FileNotFoundError(f"Couples file not found: {couples_path}")

        logging.info("=" * 80)
        logging.info("Processing COUPLES")
        logging.info("=" * 80)

        couples_long = generate_draws_from_ruro_ready(
            couples_path,
            args.job_universe,
            args.job_metadata,
            household_type="couples",
            n_draws=args.n_draws,
            pi0_m=args.pi0_m,
            pi0_f=args.pi0_f,
            baseline_mode=args.baseline_mode,
            rng_seed=args.seed + 1,  # Different seed for couples
        )

        # Output path
        output_path = couples_path.parent / f"{couples_path.stem}_jobdraws.parquet"
        _write_dataframe(couples_long, output_path)

        # Metadata
        max_draw = int(couples_long["draw"].max())
        id_multiplier = _compute_id_multiplier(max_draw)

        metadata = {
            "n_draws": args.n_draws,
            "max_draw": max_draw,
            "seed": args.seed + 1,
            "id_multiplier": id_multiplier,
            "household_type": "couples",
            "baseline_mode": args.baseline_mode,
            "distributional_params": {
                "pi0_m": args.pi0_m,
                "pi0_f": args.pi0_f,
            },
            "input_file": str(couples_path),
            "job_universe": str(args.job_universe),
            "job_metadata": str(args.job_metadata),
            "output_schema": list(couples_long.columns),
        }

        _write_draws_metadata(output_path, metadata)

        print(f"\nCouples job draws saved to: {output_path}")
        print(f"Metadata: {output_path.parent / (output_path.stem + '__drawsmeta.json')}")


if __name__ == "__main__":
    main()
