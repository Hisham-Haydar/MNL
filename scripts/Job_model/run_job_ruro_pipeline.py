#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_job_ruro_pipeline.py
=========================

End-to-end orchestrator for job-choice RURO pipeline.

Executes the full workflow:
1. Build job universe (enh_job_universe.py)
2. Generate job draws (enh_job_draws.py)
3. Run EUROMOD (enh_RURO_euromod.py)

This script is a convenience wrapper. You can also run each stage manually
for debugging or flexibility.

Usage:
------
python scripts/Job_model/run_job_ruro_pipeline.py \\
  --singles-path "U:/Data/processed/fr/2016/singles_RURO_ready.parquet" \\
  --couples-path "U:/Data/processed/fr/2016/couples_RURO_ready.parquet" \\
  --microdata-template "U:/Data/raw/FR_2016_c2.txt" \\
  --year 2016 \\
  --n-draws 99 \\
  --wage-bins 10 \\
  --euromod-system FR_2020 \\
  --euromod-dataset FR_2021_c2 \\
  --seed 13

"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _run_command(cmd: list[str], description: str) -> None:
    """
    Run a subprocess command and handle errors.

    Parameters
    ----------
    cmd : list of str
        Command to execute
    description : str
        Human-readable description for logging
    """
    logging.info("=" * 80)
    logging.info(f"STEP: {description}")
    logging.info("=" * 80)
    logging.info(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=False, text=True)

    if result.returncode != 0:
        logging.error(f"Command failed with return code {result.returncode}")
        sys.exit(result.returncode)

    logging.info(f"✓ {description} completed successfully\n")


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------

def run_job_ruro_pipeline(
    singles_path: Path | None,
    couples_path: Path | None,
    microdata_template: Path,
    *,
    year: int,
    output_dir: Path | None = None,
    n_draws: int = 99,
    hours_cutpoints: str = "5,16,31,43,71",
    wage_bins: int = 10,
    isco_codes: str | None = None,
    include_isco0: bool = False,
    universe_mode: str = "empirical_pruned",
    rep_fill_mode: str = "bin_means",
    job_id_mode: str = "sequential",
    min_cell_threshold: int = 5,
    smoothing_alpha: float = 0.01,
    pi0_m: float = 0.10,
    pi0_f: float = 0.10,
    baseline_mode: str = "observed",
    euromod_system: str = "FR_2020",
    euromod_dataset: str = "FR_2021_c2",
    euromod_root: Path | None = None,
    scenario_dir: Path | None = None,
    seed: int = 13,
) -> None:
    """
    Run complete job-choice RURO pipeline.

    Parameters
    ----------
    singles_path, couples_path : Path or None
        Paths to *_RURO_ready.parquet files
    microdata_template : Path
        Baseline EUROMOD microdata file
    year : int
        Year label
    output_dir : Path, optional
        Output directory for job universe (default: same as singles_path parent)
    n_draws : int
        Number of simulated draws per decider
    hours_cutpoints : str
        Comma-separated hours bin cutpoints
    wage_bins : int
        Number of wage bins
    min_cell_threshold : int
        Minimum observations per job cell
    smoothing_alpha : float
        Laplace smoothing parameter
    pi0_m, pi0_f : float
        Mass at non-employment
    euromod_system : str
        EUROMOD system code (e.g., "FR_2020")
    euromod_dataset : str
        EUROMOD dataset name (e.g., "FR_2021_c2")
    euromod_root : Path, optional
        EUROMOD release directory (inferred if omitted)
    scenario_dir : Path, optional
        EUROMOD scenario output directory (inferred if omitted)
    seed : int
        Random seed
    """
    # -------------------------------------------------------------------------
    # Resolve paths
    # -------------------------------------------------------------------------
    if singles_path is None and couples_path is None:
        raise ValueError("Must provide at least one of --singles-path or --couples-path")

    # Infer output_dir if not provided
    if output_dir is None:
        if singles_path is not None:
            output_dir = singles_path.parent / "job_model"
        elif couples_path is not None:
            output_dir = couples_path.parent / "job_model"
        else:
            raise ValueError("Cannot infer output_dir")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Infer scenario_dir if not provided
    if scenario_dir is None:
        scenario_dir = output_dir / "euromod_scenarios"

    scenario_dir = Path(scenario_dir)
    scenario_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # Step 1: Build Job Universe
    # -------------------------------------------------------------------------
    job_universe_path = output_dir / f"job_universe_{year}.parquet"
    job_metadata_path = output_dir / f"job_universe_{year}__meta.json"

    cmd_universe = [
        sys.executable,
        "scripts/Job_model/enh_job_universe.py",
        "--output-dir", str(output_dir),
        "--year", str(year),
        "--hours-cutpoints", hours_cutpoints,
        "--wage-bins", str(wage_bins),
        "--universe-mode", universe_mode,
        "--rep-fill-mode", rep_fill_mode,
        "--job-id-mode", job_id_mode,
        "--include-isco0", str(1 if include_isco0 else 0),
        "--min-cell-threshold", str(min_cell_threshold),
        "--smoothing-alpha", str(smoothing_alpha),
        "--seed", str(seed),
    ]

    if isco_codes is not None:
        cmd_universe += ["--isco-codes", isco_codes]

    if singles_path is not None:
        cmd_universe += ["--singles-path", str(singles_path)]
    if couples_path is not None:
        cmd_universe += ["--couples-path", str(couples_path)]

    _run_command(cmd_universe, "Build Job Universe")

    # -------------------------------------------------------------------------
    # Step 2: Generate Job Draws
    # -------------------------------------------------------------------------
    cmd_draws = [
        sys.executable,
        "scripts/Job_model/enh_job_draws.py",
        "--job-universe", str(job_universe_path),
        "--job-metadata", str(job_metadata_path),
        "--n-draws", str(n_draws),
        "--pi0-m", str(pi0_m),
        "--pi0-f", str(pi0_f),
        "--baseline-mode", baseline_mode,
        "--seed", str(seed),
    ]

    singles_draws_path = None
    couples_draws_path = None

    if singles_path is not None:
        cmd_draws += ["--singles-path", str(singles_path)]
        singles_draws_path = singles_path.parent / f"{singles_path.stem}_jobdraws.parquet"

    if couples_path is not None:
        cmd_draws += ["--couples-path", str(couples_path)]
        couples_draws_path = couples_path.parent / f"{couples_path.stem}_jobdraws.parquet"

    _run_command(cmd_draws, "Generate Job Draws")

    # -------------------------------------------------------------------------
    # Step 3: Run EUROMOD
    # -------------------------------------------------------------------------
    cmd_euromod = [
        sys.executable,
        "scripts/enhanced/enh_RURO_euromod.py",
        "--microdata-template", str(microdata_template),
        "--euromod-system", euromod_system,
        "--euromod-dataset", euromod_dataset,
        "--scenario-dir", str(scenario_dir),
    ]

    if singles_draws_path is not None:
        cmd_euromod += ["--singles-draws", str(singles_draws_path)]

    if couples_draws_path is not None:
        cmd_euromod += ["--couples-draws", str(couples_draws_path)]

    if euromod_root is not None:
        cmd_euromod += ["--euromod-root", str(euromod_root)]

    _run_command(cmd_euromod, "Run EUROMOD")

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    logging.info("\n" + "=" * 80)
    logging.info("✅ JOB-CHOICE RURO PIPELINE COMPLETED SUCCESSFULLY")
    logging.info("=" * 80)
    logging.info(f"Job universe: {job_universe_path}")
    logging.info(f"Job metadata: {job_metadata_path}")

    if singles_draws_path:
        logging.info(f"Singles draws: {singles_draws_path}")
    if couples_draws_path:
        logging.info(f"Couples draws: {couples_draws_path}")

    combined_em_path = scenario_dir / "combined_draws_em.parquet"
    if combined_em_path.exists():
        logging.info(f"EUROMOD output: {combined_em_path}")

    logging.info("=" * 80)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Run end-to-end job-choice RURO pipeline: universe → draws → EUROMOD"
    )

    # Input paths
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
        "--microdata-template",
        type=Path,
        required=True,
        help="Baseline EUROMOD microdata file",
    )

    # Output paths
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for job universe and draws (default: {singles_path}/job_model)",
    )
    ap.add_argument(
        "--scenario-dir",
        type=Path,
        default=None,
        help="EUROMOD scenario output directory (default: {output_dir}/euromod_scenarios)",
    )

    # Job universe parameters
    ap.add_argument(
        "--year",
        type=int,
        required=True,
        help="Year label (e.g., 2016)",
    )
    ap.add_argument(
        "--hours-cutpoints",
        type=str,
        default="5,16,31,43,71",
        help="Comma-separated hours bin cutpoints",
    )
    ap.add_argument(
        "--wage-bins",
        type=int,
        default=10,
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
        action="store_true",
        help="Include ISCO code 0 (armed forces)",
    )
    ap.add_argument(
        "--universe-mode",
        type=str,
        default="empirical_pruned",
        choices=["empirical_pruned", "empirical_all", "full_grid"],
        help="Universe construction mode (default: empirical_pruned; recommended: full_grid for soft constraints)",
    )
    ap.add_argument(
        "--rep-fill-mode",
        type=str,
        default="bin_means",
        choices=["bin_means", "bin_midpoints"],
        help="Representative value fill mode for empty cells in full_grid (default: bin_means)",
    )
    ap.add_argument(
        "--job-id-mode",
        type=str,
        default="sequential",
        choices=["deterministic", "sequential"],
        help="Job ID assignment mode (default: sequential; use deterministic for stable cross-year IDs)",
    )
    ap.add_argument(
        "--min-cell-threshold",
        type=int,
        default=5,
        help="Minimum observations per job cell (only used in empirical_pruned mode)",
    )
    ap.add_argument(
        "--smoothing-alpha",
        type=float,
        default=0.01,
        help="Laplace smoothing parameter",
    )

    # Job draws parameters
    ap.add_argument(
        "--n-draws",
        type=int,
        default=99,
        help="Number of simulated draws per decider",
    )
    ap.add_argument(
        "--pi0-m",
        type=float,
        default=0.10,
        help="Mass at non-employment for men",
    )
    ap.add_argument(
        "--pi0-f",
        type=float,
        default=0.10,
        help="Mass at non-employment for women",
    )
    ap.add_argument(
        "--baseline-mode",
        type=str,
        default="observed",
        choices=["observed", "cell_rep"],
        help="Baseline (draw=0) mode: observed (use actual lhw_base/yivwg_base), cell_rep (use hours_rep/wage_rep)",
    )

    # EUROMOD parameters
    ap.add_argument(
        "--euromod-system",
        type=str,
        default="FR_2020",
        help="EUROMOD system code",
    )
    ap.add_argument(
        "--euromod-dataset",
        type=str,
        default="FR_2021_c2",
        help="EUROMOD dataset name",
    )
    ap.add_argument(
        "--euromod-root",
        type=Path,
        default=None,
        help="EUROMOD release directory (auto-detected if omitted)",
    )

    # Other
    ap.add_argument(
        "--seed",
        type=int,
        default=13,
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

    run_job_ruro_pipeline(
        singles_path=args.singles_path,
        couples_path=args.couples_path,
        microdata_template=args.microdata_template,
        year=args.year,
        output_dir=args.output_dir,
        n_draws=args.n_draws,
        hours_cutpoints=args.hours_cutpoints,
        wage_bins=args.wage_bins,
        isco_codes=args.isco_codes,
        include_isco0=args.include_isco0,
        universe_mode=args.universe_mode,
        rep_fill_mode=args.rep_fill_mode,
        job_id_mode=args.job_id_mode,
        min_cell_threshold=args.min_cell_threshold,
        smoothing_alpha=args.smoothing_alpha,
        pi0_m=args.pi0_m,
        pi0_f=args.pi0_f,
        baseline_mode=args.baseline_mode,
        euromod_system=args.euromod_system,
        euromod_dataset=args.euromod_dataset,
        euromod_root=args.euromod_root,
        scenario_dir=args.scenario_dir,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
