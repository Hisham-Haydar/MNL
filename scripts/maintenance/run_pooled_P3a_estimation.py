"""
Pooled P3a three-start estimation orchestrator.

Authorisation: docs/JMP_pooled_P3a_estimation_execution_authorization_v1.md
               docs/JMP_pooled_P3a_estimation_execution_authorization_correction_v1.md
               docs/JMP_pooled_P3a_estimation_execution_repair_clearance_v1.md

Runs three starts sequentially, then post-estimation cluster-robust SE
after each converged start.  Writes per-start results to a common output
tree and prints a summary JSON when all three are done.

Usage (from MNL repo root):
    .venv\\Scripts\\python.exe scripts/maintenance/run_pooled_P3a_estimation.py

DO NOT compute welfare.  DO NOT promote outputs to canonical status.
DO NOT issue SA2.  DO NOT modify pooled parquets or YAML specs.
"""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Paths (all relative to repo root, resolved below)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]          # …/MNL
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"

SPEC = ROOT / "scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml"
MNL_BASE = ROOT / "Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready"

M1CLEAN_JSON = (
    ROOT
    / "outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy"
    / "estimation_spec_ruro_occ_M1_clean/run_2026-05-18_12-38-37"
    / "estimation_results.json"
)

OUTPUT_BASE = ROOT / "outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy"
RESULTS_DIR = ROOT / "Results"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run(cmd: list, label: str) -> subprocess.CompletedProcess:
    logger.info("=" * 70)
    logger.info("RUNNING: %s", label)
    logger.info("CMD: %s", " ".join(str(c) for c in cmd))
    logger.info("=" * 70)
    t0 = time.time()
    result = subprocess.run(cmd, cwd=ROOT, capture_output=False)
    elapsed = time.time() - t0
    logger.info("Finished %s in %.1f s  (returncode=%d)", label, elapsed, result.returncode)
    return result


def load_converged_theta(results_json: Path) -> np.ndarray:
    """Extract the joint converged theta from an estimation_results.json."""
    with open(results_json) as f:
        data = json.load(f)
    results = data.get("results", {})
    # Try joint → singles_male → couples in order
    for key in ("joint", "singles_male", "couples"):
        if key in results:
            block = results[key]
            theta = block.get("theta")
            if isinstance(theta, list) and len(theta) > 0:
                return np.array(theta, dtype=float)
            params = block.get("parameters")
            if isinstance(params, dict) and params:
                return np.array(list(params.values()), dtype=float)
    raise RuntimeError(f"Cannot find theta in {results_json}")


def make_perturbed_init_params(base_theta: np.ndarray, seed: int, magnitude: float,
                                param_names: list, out_path: Path) -> None:
    """Write a perturbed init-params JSON compatible with --init-params."""
    rng = np.random.default_rng(seed)
    perturbation = rng.uniform(-magnitude, magnitude, size=len(base_theta))
    perturbed = base_theta + perturbation
    payload = {
        "param_names": param_names,
        "theta": perturbed.tolist(),
        "_perturbation_seed": seed,
        "_perturbation_magnitude": magnitude,
        "_base_source": "start_1_converged",
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    logger.info("Wrote perturbed init params to %s", out_path)


def load_param_names_from_spec() -> list:
    """Parse spec to get ordered parameter names."""
    sys.path.insert(0, str(ROOT / "scripts/enhanced"))
    from estimation_spec_parser import parse_specification
    spec = parse_specification(SPEC)
    return spec.all_param_names


def find_run_dir(base: Path) -> Path:
    """Find the most-recently modified run_* subdirectory."""
    candidates = sorted(
        [d for d in base.iterdir() if d.is_dir() and d.name.startswith("run_")],
        key=lambda d: d.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise RuntimeError(f"No run_* directory found under {base}")
    return candidates[0]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    logger.info("Pooled P3a estimation orchestrator — %s", ts())
    logger.info("Repo root: %s", ROOT)
    logger.info("Spec: %s", SPEC)
    logger.info("MNL base: %s", MNL_BASE)

    # Confirm required files exist
    for p, label in [
        (PYTHON, "Python interpreter"),
        (SPEC, "Pooled spec YAML"),
        (M1CLEAN_JSON, "M1-clean estimation results"),
        (Path(str(MNL_BASE) + "__singles.parquet"), "Singles parquet"),
        (Path(str(MNL_BASE) + "__couples.parquet"), "Couples parquet"),
        (Path(str(MNL_BASE) + "__mnlmeta.json"), "MNL metadata"),
    ]:
        if not p.exists():
            logger.error("MISSING: %s  (%s)", p, label)
            sys.exit(1)
        logger.info("OK: %s", label)

    ESTIMATOR = ROOT / "scripts/enhanced/enh_RURO_estimate_FR.py"
    SE_CLI = ROOT / "scripts/enhanced/run_cluster_robust_se.py"
    SPEC_SUBDIR = "estimation_spec_ruro_occ_P3a_pooled"

    summary = {
        "orchestrator": "run_pooled_P3a_estimation.py",
        "started": ts(),
        "starts": {},
    }

    # -----------------------------------------------------------------------
    # START 1 — warm from M1-clean
    # -----------------------------------------------------------------------
    logger.info(">>> START 1: warm from M1-clean (--init-params, no --vectorized)")
    r1 = run([
        str(PYTHON), str(ESTIMATOR),
        "--mnl-base", str(MNL_BASE),
        "--spec-config", str(SPEC),
        "--output-dir", str(OUTPUT_BASE / "start_1"),
        "--no-spec-subdir",
        "--auto-timestamp",
        "--group", "joint",
        "--solver", "gamspy-conopt",
        "--warm-start", "none",
        "--init-params", str(M1CLEAN_JSON),
        "--verbose",
    ], "Start 1 estimation")

    start1_base = OUTPUT_BASE / "start_1"
    start1_run_dir = find_run_dir(start1_base)
    start1_results = start1_run_dir / "estimation_results.json"
    logger.info("Start 1 run dir: %s", start1_run_dir)

    se1_output = RESULTS_DIR / "JMP_pooled_P3a_start1_cluster_robust_se.json"
    run([
        str(PYTHON), str(SE_CLI),
        "--spec", str(SPEC),
        "--mnl-base", str(MNL_BASE),
        "--results-json", str(start1_results),
        "--output", str(se1_output),
        "--mode", "post-estimation",
        "--cluster-col", "idorighh",
    ], "Start 1 post-estimation SE")

    summary["starts"]["start_1"] = {
        "run_dir": str(start1_run_dir),
        "results_json": str(start1_results),
        "se_output": str(se1_output),
        "returncode": r1.returncode,
        "init_params_source": str(M1CLEAN_JSON),
        "init_method": "init-params from M1-clean (load_custom_initial_values maps 53→55 by name; beta_E_y2015=beta_E_y2017=0.0 from spec default)",
    }

    if r1.returncode != 0 or not start1_results.exists():
        logger.error("START 1 FAILED (returncode=%d, results exist=%s) — halting orchestration.",
                     r1.returncode, start1_results.exists())
        summary["finished"] = ts()
        summary["status"] = "HALTED after Start 1 failure"
        summary_path = RESULTS_DIR / "JMP_pooled_P3a_orchestrator_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        return 1

    # -----------------------------------------------------------------------
    # START 2 — spec defaults (warm-start none)
    # -----------------------------------------------------------------------
    logger.info(">>> START 2: spec defaults")
    r2 = run([
        str(PYTHON), str(ESTIMATOR),
        "--mnl-base", str(MNL_BASE),
        "--spec-config", str(SPEC),
        "--output-dir", str(OUTPUT_BASE / "start_2"),
        "--no-spec-subdir",
        "--auto-timestamp",
        "--group", "joint",
        "--solver", "gamspy-conopt",
        "--warm-start", "none",
        "--verbose",
    ], "Start 2 estimation")

    start2_base = OUTPUT_BASE / "start_2"
    start2_run_dir = find_run_dir(start2_base)
    start2_results = start2_run_dir / "estimation_results.json"
    logger.info("Start 2 run dir: %s", start2_run_dir)

    se2_output = RESULTS_DIR / "JMP_pooled_P3a_start2_cluster_robust_se.json"
    run([
        str(PYTHON), str(SE_CLI),
        "--spec", str(SPEC),
        "--mnl-base", str(MNL_BASE),
        "--results-json", str(start2_results),
        "--output", str(se2_output),
        "--mode", "post-estimation",
        "--cluster-col", "idorighh",
    ], "Start 2 post-estimation SE")

    summary["starts"]["start_2"] = {
        "run_dir": str(start2_run_dir),
        "results_json": str(start2_results),
        "se_output": str(se2_output),
        "returncode": r2.returncode,
    }

    # -----------------------------------------------------------------------
    # START 3 — perturbed warm start (seed 42, ±0.1)
    # -----------------------------------------------------------------------
    logger.info(">>> START 3: perturbed warm start from Start 1")
    param_names = load_param_names_from_spec()
    theta1 = load_converged_theta(start1_results)
    perturbed_json = RESULTS_DIR / "JMP_pooled_P3a_start3_perturbed_init.json"
    make_perturbed_init_params(theta1, seed=42, magnitude=0.1,
                                param_names=param_names, out_path=perturbed_json)

    r3 = run([
        str(PYTHON), str(ESTIMATOR),
        "--mnl-base", str(MNL_BASE),
        "--spec-config", str(SPEC),
        "--output-dir", str(OUTPUT_BASE / "start_3"),
        "--no-spec-subdir",
        "--auto-timestamp",
        "--group", "joint",
        "--solver", "gamspy-conopt",
        "--warm-start", "none",
        "--init-params", str(perturbed_json),
        "--verbose",
    ], "Start 3 estimation")

    start3_base = OUTPUT_BASE / "start_3"
    start3_run_dir = find_run_dir(start3_base)
    start3_results = start3_run_dir / "estimation_results.json"
    logger.info("Start 3 run dir: %s", start3_run_dir)

    se3_output = RESULTS_DIR / "JMP_pooled_P3a_start3_cluster_robust_se.json"
    run([
        str(PYTHON), str(SE_CLI),
        "--spec", str(SPEC),
        "--mnl-base", str(MNL_BASE),
        "--results-json", str(start3_results),
        "--output", str(se3_output),
        "--mode", "post-estimation",
        "--cluster-col", "idorighh",
    ], "Start 3 post-estimation SE")

    summary["starts"]["start_3"] = {
        "run_dir": str(start3_run_dir),
        "results_json": str(start3_results),
        "se_output": str(se3_output),
        "returncode": r3.returncode,
        "perturbed_init_json": str(perturbed_json),
    }

    summary["finished"] = ts()
    summary_path = RESULTS_DIR / "JMP_pooled_P3a_orchestrator_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info("Summary written to %s", summary_path)
    logger.info("Orchestration complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())