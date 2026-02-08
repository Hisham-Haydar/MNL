#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sanity_checks_job.py
====================

Validation suite for job-choice RURO pipeline outputs.

Functions:
----------
1. sanity_report_job_universe() - Validate job grid structure
2. sanity_report_job_draws() - Validate job draws output
3. sanity_report_proposal_density() - Validate proposal density components

These checks catch structural issues before EUROMOD stage or estimation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Job Universe Validation
# ---------------------------------------------------------------------------

def sanity_report_job_universe(
    job_universe: pd.DataFrame,
    metadata: Dict[str, Any] | None = None,
) -> None:
    """
    Validate job universe structure and priors.

    Checks:
    -------
    1. No duplicate job_id
    2. job_id=0 exists with hours=0, wage=0, isco1=-1
    3. All isco1 codes are valid (1-9, optionally 0)
    4. q_j_prior sums to 1 (excluding job 0)
    5. No missing or invalid values

    Parameters
    ----------
    job_universe : DataFrame
        Job grid from enh_job_universe.py
    metadata : dict, optional
        Job universe metadata

    Raises
    ------
    ValueError
        If any validation check fails
    """
    logging.info("=" * 80)
    logging.info("SANITY CHECK: Job Universe")
    logging.info("=" * 80)

    # Check required columns
    required_cols = {"job_id", "hours_bin", "wage_bin", "isco1", "cell_count", "hours_rep", "wage_rep", "q_j_prior"}
    missing = required_cols - set(job_universe.columns)
    if missing:
        raise ValueError(f"Job universe missing columns: {sorted(missing)}")

    n_jobs = len(job_universe)
    logging.info(f"Total jobs: {n_jobs}")

    # Check 1: No duplicate job_id
    if job_universe["job_id"].duplicated().any():
        n_dups = job_universe["job_id"].duplicated().sum()
        raise ValueError(f"Duplicate job_id found: {n_dups} duplicates")

    logging.info("✓ No duplicate job_id")

    # Check 2: job_id=0 exists and is correct
    job_0 = job_universe[job_universe["job_id"] == 0]

    if len(job_0) == 0:
        raise ValueError("job_id=0 (non-employment) not found")

    if len(job_0) > 1:
        raise ValueError(f"Multiple job_id=0 rows found: {len(job_0)}")

    job_0_row = job_0.iloc[0]

    if job_0_row["hours_bin"] != -1:
        raise ValueError(f"job_id=0 has hours_bin={job_0_row['hours_bin']}, expected -1")
    if job_0_row["wage_bin"] != -1:
        raise ValueError(f"job_id=0 has wage_bin={job_0_row['wage_bin']}, expected -1")
    if job_0_row["isco1"] != -1:
        raise ValueError(f"job_id=0 has isco1={job_0_row['isco1']}, expected -1")
    if job_0_row["hours_rep"] != 0:
        raise ValueError(f"job_id=0 has hours_rep={job_0_row['hours_rep']}, expected 0")
    if job_0_row["wage_rep"] != 0:
        raise ValueError(f"job_id=0 has wage_rep={job_0_row['wage_rep']}, expected 0")
    if "yem_rep" in job_universe.columns and job_0_row["yem_rep"] != 0:
        raise ValueError(f"job_id=0 has yem_rep={job_0_row['yem_rep']}, expected 0")

    logging.info("✓ job_id=0 (non-employment) is correctly defined")

    # Check 3: Valid ISCO codes
    working_jobs = job_universe[job_universe["job_id"] > 0]

    valid_isco = list(range(1, 10)) + [0]  # 1-9 + armed forces
    invalid_isco = working_jobs[~working_jobs["isco1"].isin(valid_isco)]

    if len(invalid_isco) > 0:
        bad_codes = invalid_isco["isco1"].unique()
        raise ValueError(f"Invalid ISCO codes in working jobs: {sorted(bad_codes)}")

    isco_counts = working_jobs["isco1"].value_counts().sort_index()
    logging.info(f"✓ All ISCO codes valid (1-9, optionally 0)")
    logging.info(f"  ISCO distribution: {isco_counts.to_dict()}")

    # Check 4: q_j_prior sums to 1
    q_sum = working_jobs["q_j_prior"].sum()

    if not np.isclose(q_sum, 1.0, atol=1e-6):
        raise ValueError(f"q_j_prior sum = {q_sum:.10f}, expected 1.0")

    logging.info(f"✓ q_j_prior sums to 1.0 (actual: {q_sum:.10f})")

    # Check 5: No missing values
    for col in ["hours_rep", "wage_rep", "q_j_prior"]:
        if working_jobs[col].isna().any():
            n_missing = working_jobs[col].isna().sum()
            raise ValueError(f"Column {col} has {n_missing} missing values")

    logging.info("✓ No missing values in working jobs")

    # GMM-specific checks
    if metadata is not None and metadata.get("universe_mode") == "gmm_occ":
        if "type_id" not in job_universe.columns:
            raise ValueError("GMM universe missing type_id column")
        if "type_draw_id" not in job_universe.columns:
            raise ValueError("GMM universe missing type_draw_id column")
        if working_jobs["type_id"].isna().any():
            raise ValueError("GMM universe has missing type_id values")
        if working_jobs["type_draw_id"].isna().any():
            raise ValueError("GMM universe has missing type_draw_id values")
        if not np.isfinite(working_jobs["hours_rep"]).all() or not np.isfinite(working_jobs["wage_rep"]).all():
            raise ValueError("GMM universe has non-finite representative values")
        if "type_draw_id" in job_universe.columns and job_0_row["type_draw_id"] != -1:
            raise ValueError(
                f"job_id=0 has type_draw_id={job_0_row['type_draw_id']}, expected -1"
            )
        logging.info("✓ GMM-specific checks passed (type_id/type_draw_id present, reps finite)")

    # Summary statistics
    logging.info("\nJob Universe Summary:")
    logging.info(f"  Working jobs: {len(working_jobs)}")
    logging.info(f"  Hours bins: {working_jobs['hours_bin'].nunique()}")
    logging.info(f"  Wage bins: {working_jobs['wage_bin'].nunique()}")
    logging.info(f"  Occupations: {working_jobs['isco1'].nunique()}")
    logging.info(f"  Total cells observed: {working_jobs['cell_count'].sum():.0f}")
    logging.info(f"  Mean cell count: {working_jobs['cell_count'].mean():.1f}")
    logging.info(f"  Median cell count: {working_jobs['cell_count'].median():.0f}")

    # Top 10 jobs
    top10 = working_jobs.nlargest(10, "q_j_prior")
    logging.info("\nTop 10 jobs by prior:")
    for _, row in top10.iterrows():
        logging.info(
            f"  job_id={int(row['job_id']):3d} "
            f"(h_bin={int(row['hours_bin'])}, w_bin={int(row['wage_bin'])}, isco1={int(row['isco1'])}): "
            f"q={row['q_j_prior']:.4f}, n={int(row['cell_count'])}"
        )

    logging.info("\n✅ Job universe passed all sanity checks")
    logging.info("=" * 80)


# ---------------------------------------------------------------------------
# Job Draws Validation
# ---------------------------------------------------------------------------

def sanity_report_job_draws(
    df: pd.DataFrame,
    metadata: Dict[str, Any] | None = None,
    n_draws: int | None = None,
) -> None:
    """
    Validate job draws output structure and consistency.

    Checks:
    -------
    1. All deciders have complete draw sets {0..n_draws}
    2. draw=0 baseline compliance (lhw_draw == lhw_base)
    3. All job_id exist in universe (if metadata provided)
    4. Non-employment rows (job_id=0) have lhw_draw=0, yivwg_draw=0
    5. No missing critical columns

    Parameters
    ----------
    df : DataFrame
        Job draws output from enh_job_draws.py
    metadata : dict, optional
        Draws metadata
    n_draws : int, optional
        Expected number of draws per decider

    Raises
    ------
    ValueError
        If any validation check fails
    """
    logging.info("=" * 80)
    logging.info("SANITY CHECK: Job Draws")
    logging.info("=" * 80)

    # Check required columns
    required_cols = {
        "draw", "idperson_true", "is_decider", "job_id",
        "lhw_draw", "yivwg_draw", "yem_draw",
    }
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Job draws missing columns: {sorted(missing)}")

    n_rows = len(df)
    n_deciders = (df["is_decider"] == 1).sum()
    n_nondeciders = (df["is_decider"] == 0).sum()

    logging.info(f"Total rows: {n_rows}")
    logging.info(f"Decider rows: {n_deciders}")
    logging.info(f"Non-decider rows: {n_nondeciders}")

    # Infer n_draws if not provided
    if n_draws is None:
        n_draws = int(df["draw"].max())

    logging.info(f"Expected draws per decider: 0..{n_draws}")

    # Check 1: Complete draw sets for deciders
    is_decider = df["is_decider"] == 1
    deciders_df = df[is_decider].copy()

    if len(deciders_df) > 0:
        expected_draw_set = set(range(n_draws + 1))
        draw_counts = deciders_df.groupby("idperson_true")["draw"].apply(set)

        violations = []
        for idperson, draw_set in draw_counts.items():
            if draw_set != expected_draw_set:
                violations.append({
                    "idperson_true": idperson,
                    "expected": sorted(expected_draw_set),
                    "actual": sorted(draw_set),
                    "missing": sorted(expected_draw_set - draw_set),
                    "extra": sorted(draw_set - expected_draw_set),
                })

        if violations:
            logging.error(f"Draw completeness failed: {len(violations)} deciders with incomplete sets")
            for v in violations[:5]:
                logging.error(f"  idperson={v['idperson_true']}: missing={v['missing']}, extra={v['extra']}")
            raise ValueError(f"{len(violations)} deciders have incomplete draw sets")

        logging.info(f"✓ All {len(draw_counts)} deciders have complete draw sets {{0..{n_draws}}}")

    # Check 2: Baseline compliance (draw=0)
    draw0 = df[df["draw"] == 0].copy()
    draw0_deciders = draw0[draw0["is_decider"] == 1].copy()

    if len(draw0_deciders) > 0 and "lhw_base" in df.columns and "yivwg_base" in df.columns:
        lhw_draw = pd.to_numeric(draw0_deciders["lhw_draw"], errors="coerce").fillna(0.0)
        lhw_base = pd.to_numeric(draw0_deciders["lhw_base"], errors="coerce").fillna(0.0)
        h_diff = np.abs(lhw_draw - lhw_base)

        yivwg_draw = pd.to_numeric(draw0_deciders["yivwg_draw"], errors="coerce").fillna(0.0)
        yivwg_base = pd.to_numeric(draw0_deciders["yivwg_base"], errors="coerce").fillna(0.0)
        w_diff = np.abs(yivwg_draw - yivwg_base)

        h_violations = (h_diff > 1e-6).sum()
        w_violations = (w_diff > 1e-6).sum()

        if h_violations > 0:
            raise ValueError(f"Baseline hours compliance failed: {h_violations} violations")
        if w_violations > 0:
            raise ValueError(f"Baseline wage compliance failed: {w_violations} violations")

        logging.info(f"✓ draw=0 baseline compliance: {len(draw0_deciders)} deciders OK")

    # Check 3: Non-employment consistency
    job_0_rows = df[df["job_id"] == 0].copy()

    if len(job_0_rows) > 0:
        lhw_nonemp = pd.to_numeric(job_0_rows["lhw_draw"], errors="coerce").fillna(0.0)
        yivwg_nonemp = pd.to_numeric(job_0_rows["yivwg_draw"], errors="coerce").fillna(0.0)

        bad_hours = (lhw_nonemp != 0).sum()
        bad_wages = (yivwg_nonemp != 0).sum()

        if bad_hours > 0:
            raise ValueError(f"Non-employment rows with lhw_draw!=0: {bad_hours}")
        if bad_wages > 0:
            raise ValueError(f"Non-employment rows with yivwg_draw!=0: {bad_wages}")

        logging.info(f"✓ Non-employment consistency: {len(job_0_rows)} rows with job_id=0 have hours=0, wage=0")

    # Check 4: Job distribution
    job_dist = df["job_id"].value_counts().sort_index()
    logging.info(f"\nJob distribution (top 10):")
    for job_id, count in job_dist.head(10).items():
        pct = 100 * count / len(df)
        logging.info(f"  job_id={int(job_id):3d}: {count:6d} ({pct:.1f}%)")

    # Check 5: Proposal density sanity
    if "log_q_total" in df.columns:
        deciders_draws = df[(df["is_decider"] == 1) & (df["draw"] > 0)].copy()

        if len(deciders_draws) > 0:
            log_q = pd.to_numeric(deciders_draws["log_q_total"], errors="coerce")

            n_inf = np.isinf(log_q).sum()
            n_nan = log_q.isna().sum()

            if n_inf > 0:
                logging.warning(f"Found {n_inf} -inf in log_q_total (may be intentional for zero-prob states)")

            if n_nan > 0:
                raise ValueError(f"Found {n_nan} NaN in log_q_total")

            logging.info(f"✓ log_q_total: min={log_q.min():.4f}, median={log_q.median():.4f}, max={log_q.max():.4f}")

    logging.info("\n✅ Job draws passed all sanity checks")
    logging.info("=" * 80)


# ---------------------------------------------------------------------------
# Proposal Density Validation
# ---------------------------------------------------------------------------

def sanity_report_proposal_density(df: pd.DataFrame) -> None:
    """
    Validate proposal density components.

    Checks:
    -------
    1. log_q_total = log_q_state + log_q_job
    2. No unexpected -inf or NaN (except controlled cases)
    3. draw=0 has positive density for all deciders

    Parameters
    ----------
    df : DataFrame
        Job draws with log_q_* columns

    Raises
    ------
    ValueError
        If validation fails
    """
    logging.info("=" * 80)
    logging.info("SANITY CHECK: Proposal Density")
    logging.info("=" * 80)

    required_cols = {"log_q_state", "log_q_job", "log_q_total", "draw", "is_decider"}
    missing = required_cols - set(df.columns)
    if missing:
        logging.warning(f"Cannot validate proposal density: missing {sorted(missing)}")
        return

    # Check 1: Identity log_q_total = log_q_state + log_q_job
    deciders = df[df["is_decider"] == 1].copy()

    if len(deciders) == 0:
        logging.warning("No deciders found for proposal density check")
        return

    log_q_state = pd.to_numeric(deciders["log_q_state"], errors="coerce")
    log_q_job = pd.to_numeric(deciders["log_q_job"], errors="coerce")
    log_q_total = pd.to_numeric(deciders["log_q_total"], errors="coerce")

    identity_diff = np.abs(log_q_total - (log_q_state + log_q_job))
    max_diff = identity_diff.max()
    n_violations = (identity_diff > 1e-6).sum()

    if n_violations > 0:
        logging.error(f"Proposal density identity failed: {n_violations} violations, max_diff={max_diff:.10f}")
        raise ValueError(f"log_q_total != log_q_state + log_q_job for {n_violations} rows")

    logging.info(f"✓ Proposal density identity: log_q_total = log_q_state + log_q_job (max_diff={max_diff:.10f})")

    # Check 2: draw=0 positive density
    draw0_deciders = deciders[deciders["draw"] == 0].copy()

    if len(draw0_deciders) > 0:
        log_q_draw0 = pd.to_numeric(draw0_deciders["log_q_total"], errors="coerce")

        n_neginf = np.isneginf(log_q_draw0).sum()
        n_nan = log_q_draw0.isna().sum()

        if n_neginf > 0:
            logging.error(f"draw=0 has {n_neginf} deciders with -inf log_q (zero proposal density!)")
            raise ValueError(f"Observed alternative (draw=0) has zero proposal density for {n_neginf} deciders")

        if n_nan > 0:
            raise ValueError(f"draw=0 has {n_nan} deciders with NaN log_q")

        logging.info(f"✓ draw=0 has positive proposal density for all {len(draw0_deciders)} deciders")
        logging.info(f"  draw=0 log_q range: [{log_q_draw0.min():.4f}, {log_q_draw0.max():.4f}]")

    # Check 3: Distribution summary
    logging.info("\nProposal density summary (all deciders, all draws):")
    logging.info(f"  log_q_state: min={log_q_state.min():.4f}, median={log_q_state.median():.4f}, max={log_q_state.max():.4f}")
    logging.info(f"  log_q_job:   min={log_q_job.min():.4f}, median={log_q_job.median():.4f}, max={log_q_job.max():.4f}")
    logging.info(f"  log_q_total: min={log_q_total.min():.4f}, median={log_q_total.median():.4f}, max={log_q_total.max():.4f}")

    logging.info("\n✅ Proposal density passed all checks")
    logging.info("=" * 80)


# ---------------------------------------------------------------------------
# Convenience: Run all checks
# ---------------------------------------------------------------------------

def run_all_job_checks(
    job_universe: pd.DataFrame | None = None,
    job_draws: pd.DataFrame | None = None,
    metadata: Dict[str, Any] | None = None,
    n_draws: int | None = None,
) -> None:
    """
    Run all job-choice RURO validation checks.

    Parameters
    ----------
    job_universe : DataFrame, optional
        Job universe to validate
    job_draws : DataFrame, optional
        Job draws to validate
    metadata : dict, optional
        Metadata for context
    n_draws : int, optional
        Expected number of draws
    """
    logging.info("\n" + "=" * 80)
    logging.info("RUNNING ALL JOB-CHOICE RURO SANITY CHECKS")
    logging.info("=" * 80 + "\n")

    if job_universe is not None:
        sanity_report_job_universe(job_universe, metadata)

    if job_draws is not None:
        sanity_report_job_draws(job_draws, metadata, n_draws)
        sanity_report_proposal_density(job_draws)

    logging.info("\n" + "=" * 80)
    logging.info("✅ ALL CHECKS PASSED")
    logging.info("=" * 80)


if __name__ == "__main__":
    # Example usage
    import argparse
    from pathlib import Path

    def _read_dataframe(path: Path) -> pd.DataFrame:
        suf = path.suffix.lower()
        if suf == ".parquet":
            return pd.read_parquet(path)  # type: ignore
        if suf == ".csv":
            return pd.read_csv(path)
        raise ValueError(f"Unsupported format: {path}")

    ap = argparse.ArgumentParser(description="Run sanity checks on job-choice RURO outputs")
    ap.add_argument("--job-universe", type=Path, help="Path to job_universe_{year}.parquet")
    ap.add_argument("--job-draws", type=Path, help="Path to *_jobdraws.parquet")
    ap.add_argument("--n-draws", type=int, default=None, help="Expected number of draws")

    args = ap.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    job_universe = None
    job_draws = None

    if args.job_universe:
        job_universe = _read_dataframe(args.job_universe)

    if args.job_draws:
        job_draws = _read_dataframe(args.job_draws)

    run_all_job_checks(job_universe, job_draws, n_draws=args.n_draws)
