"""
Multi-start robustness check for ruro_occ_M0b2.

Runs 4 starts with identical spec/data/engine, varying only the initial parameter
vector.  Each start is submitted with --warm-start none and --init-params <json>.

Start design
------------
S1 : spec defaults  (theta_c=-1, beta_ll=0, beta_l0=1, beta_c=1, all opp=0)
S2 : small random perturbation around spec defaults  (sigma=0.15, seed=42)
S3 : perturbation around the current M0b2 solution   (sigma=0.10, seed=7)
S4 : dispersed interior start  (manually chosen, away from boundary)

All starts are clipped to the parameter bounds declared in the spec.

Usage
-----
    python Results/_M0b2_multistart_runner.py [--dry-run]

With --dry-run the init JSON files are written and the commands are printed but
not executed.
"""

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
SCRIPT  = REPO_ROOT / "scripts" / "enhanced" / "enh_RURO_estimate_FR.py"
SPEC    = REPO_ROOT / "scripts" / "enhanced" / "estimation_spec_ruro_occ_M0b2.yaml"
OUTPUT_DIR = REPO_ROOT / "outputs" / "estimates" / "fr" / "spec" / "ruro_occ" / "gamspy"
RESULTS_DIR = Path(__file__).resolve().parent  # Results/
STARTS_DIR  = RESULTS_DIR / "_M0b2_multistart_inits"

# Reference M0b2 solution (single run)
REFERENCE_JSON = (
    REPO_ROOT
    / "outputs" / "estimates" / "fr" / "spec" / "ruro_occ" / "gamspy"
    / "estimation_spec_ruro_occ_M0b2" / "run_2026-05-14_12-46-04"
    / "estimation_results.json"
)

# ---------------------------------------------------------------------------
# Bounds (from estimation_spec_ruro_occ_M0b2.yaml — replicated for clipping)
# ---------------------------------------------------------------------------
BOUNDS = {
    "theta_l_sm":       (-8.0,  0.95),
    "theta_l_sf":       (-8.0,  0.95),
    "theta_l_m":        (-8.0,  0.95),
    "theta_l_f":        (-8.0,  0.95),
    "theta_c_singles":  (-8.0,  0.95),
    "theta_c":          (-8.0,  0.0),     # tightened in M0b2
    "beta_c_sm":        (0.05,  50.0),
    "beta_c_sf":        (0.05,  50.0),
    "beta_c":           (0.05,  50.0),
    "beta_l0_sm":       (0.05,  50.0),
    "beta_l0_sf":       (0.05,  50.0),
    "beta_l0_m":        (0.05,  50.0),
    "beta_l0_f":        (0.05,  50.0),
    "beta_l_age_sm":    (-5.0,  5.0),
    "beta_l_age2_sm":   (-1.0,  1.0),
    "beta_l_age_sf":    (-5.0,  5.0),
    "beta_l_age2_sf":   (-1.0,  1.0),
    "beta_l_age_m":     (-5.0,  5.0),
    "beta_l_age2_m":    (-1.0,  1.0),
    "beta_l_age_f":     (-5.0,  5.0),
    "beta_l_age2_f":    (-1.0,  1.0),
    "beta_l_nkids_sf":  (-5.0,  5.0),
    "beta_l_nkids_f":   (-5.0,  5.0),
    "beta_E":           (-25.0, 25.0),
    "beta_h_pt1":       (-10.0, 10.0),
    "beta_h_pt2":       (-10.0, 10.0),
    "beta_h_ft":        (-10.0, 10.0),
    "beta_w0":          (-10.0, 20.0),
    "beta_w_educL":     (-5.0,  5.0),
    "beta_w_educH":     (-5.0,  5.0),
    "beta_w_pexp":      (-1.0,  1.0),
    "beta_w_pexp2":     (-0.1,  0.1),
    "beta_E_gsur":      (-10.0, 10.0),
    "beta_E_educH":     (-10.0, 10.0),
    "beta_occ_2_sm":    (-10.0, 10.0),
    "beta_occ_3_sm":    (-10.0, 10.0),
    "beta_occ_4_sm":    (-10.0, 10.0),
    "beta_occ_2_sf":    (-10.0, 10.0),
    "beta_occ_3_sf":    (-10.0, 10.0),
    "beta_occ_4_sf":    (-10.0, 10.0),
    "beta_occ_2_cm":    (-10.0, 10.0),
    "beta_occ_3_cm":    (-10.0, 10.0),
    "beta_occ_4_cm":    (-10.0, 10.0),
    "beta_occ_2_cf":    (-10.0, 10.0),
    "beta_occ_3_cf":    (-10.0, 10.0),
    "beta_occ_4_cf":    (-10.0, 10.0),
    "sigma":            (0.1,   20.0),
    "beta_ll":          (-2.0,  2.0),
}

# ---------------------------------------------------------------------------
# Spec defaults (from initial_values block in the YAML)
# ---------------------------------------------------------------------------
SPEC_DEFAULTS = {
    "beta_l0_sm": 1.0, "beta_l_age_sm": 0.0, "beta_l_age2_sm": 0.0,
    "beta_c_sm": 1.0, "theta_l_sm": -1.0,
    "beta_l0_sf": 1.0, "beta_l_age_sf": 0.0, "beta_l_age2_sf": 0.0,
    "beta_l_nkids_sf": 0.0, "beta_c_sf": 1.0, "theta_l_sf": -1.0,
    "theta_c_singles": -1.0,
    "beta_l0_m": 1.0, "beta_l_age_m": 0.0, "beta_l_age2_m": 0.0, "theta_l_m": -1.0,
    "beta_l0_f": 1.0, "beta_l_age_f": 0.0, "beta_l_age2_f": 0.0,
    "beta_l_nkids_f": 0.0, "theta_l_f": -1.0,
    "beta_c": 1.0, "theta_c": -1.0,
    "beta_E": 0.0, "beta_h_pt1": 0.0, "beta_h_pt2": 0.0, "beta_h_ft": 0.0,
    "beta_E_gsur": 0.0, "beta_E_educH": 0.0,
    "beta_w0": 2.0, "beta_w_educL": -0.1, "beta_w_educH": 0.2,
    "beta_w_pexp": 0.02, "beta_w_pexp2": -0.0003,
    "beta_occ_2_sm": 0.0, "beta_occ_3_sm": 0.0, "beta_occ_4_sm": 0.0,
    "beta_occ_2_sf": 0.0, "beta_occ_3_sf": 0.0, "beta_occ_4_sf": 0.0,
    "beta_occ_2_cm": 0.0, "beta_occ_3_cm": 0.0, "beta_occ_4_cm": 0.0,
    "beta_occ_2_cf": 0.0, "beta_occ_3_cf": 0.0, "beta_occ_4_cf": 0.0,
    "sigma": 0.5,
    "beta_ll": 0.0,
}

# M0b2 solution from the reference run
REFERENCE_SOLUTION = {
    "beta_l0_sm": 3.813892833312898,
    "beta_l_age_sm": 0.008210388333225231,
    "beta_l_age2_sm": 0.0020286612976004852,
    "beta_c_sm": 0.5915306827836431,
    "theta_l_sm": -0.7154401271724009,
    "beta_l0_sf": 4.382791849883912,
    "beta_l_age_sf": 0.0016486949743743972,
    "beta_l_age2_sf": 0.004139171315172886,
    "beta_l_nkids_sf": 0.06331364039393389,
    "beta_c_sf": 0.5347130534206086,
    "theta_l_sf": -0.7298287761132185,
    "theta_c_singles": -0.9708105318300417,
    "beta_l0_m": 0.12543841925304045,
    "beta_l_age_m": -0.008541296516880141,
    "beta_l_age2_m": 0.0017345627932301175,
    "theta_l_m": -0.670576916853743,
    "beta_l0_f": 2.800286241668201,
    "beta_l_age_f": -0.05464164624185155,
    "beta_l_age2_f": 0.002701491262445235,
    "beta_l_nkids_f": 0.18279501707034174,
    "theta_l_f": -0.6533509444711295,
    "beta_c": 3.927768445388829,
    "theta_c": 0.0,          # at bound — perturb to interior
    "beta_E": -2.838506971797773,
    "beta_h_pt1": -0.5008697664485797,
    "beta_h_pt2": 0.3706675876778732,
    "beta_h_ft": 1.4529671196502776,
    "beta_E_gsur": -0.7433447749588191,
    "beta_E_educH": 0.6129372602877088,
    "beta_occ_2_sm": -1.510097907067818,
    "beta_occ_3_sm": -2.1649475307812813,
    "beta_occ_4_sm": 0.023988099606829807,
    "beta_occ_2_sf": -0.010395529546702992,
    "beta_occ_3_sf": -0.5605909788383006,
    "beta_occ_4_sf": 0.7986693597926113,
    "beta_occ_2_cm": -1.4788431296350952,
    "beta_occ_3_cm": -2.2247339140564155,
    "beta_occ_4_cm": 0.47142505292313663,
    "beta_occ_2_cf": 0.1800231305923301,
    "beta_occ_3_cf": -0.2096475081406149,
    "beta_occ_4_cf": 1.1183773886059807,
    "beta_w0": 2.0302035822197326,
    "beta_w_educL": -0.05155130853894612,
    "beta_w_educH": 0.317450037381364,
    "beta_w_pexp": 0.018121477411289375,
    "beta_w_pexp2": -0.00021855352279319452,
    "sigma": 0.42785194452110714,
    "beta_ll": 2.0,          # at bound — perturb to interior
}


def clip(params: dict) -> dict:
    """Clip all parameters to their bounds."""
    out = {}
    for k, v in params.items():
        lo, hi = BOUNDS[k]
        out[k] = float(np.clip(v, lo, hi))
    return out


def perturb(base: dict, sigma: float, seed: int) -> dict:
    """
    Add Gaussian noise to all parameters and clip to bounds.
    Parameters at their bound are pulled 10% into the interior before
    perturbation so the noise can explore both directions.
    """
    rng = np.random.default_rng(seed)
    out = {}
    for k, v in base.items():
        lo, hi = BOUNDS[k]
        width = hi - lo
        # Pull bound-hits to 10% interior
        if v >= hi - 1e-9:
            v = hi - 0.10 * width
        elif v <= lo + 1e-9:
            v = lo + 0.10 * width
        noise = rng.normal(0.0, sigma * width)
        out[k] = float(np.clip(v + noise, lo, hi))
    return out


def make_init_json(params: dict) -> dict:
    """Wrap params dict in the estimation_results.json 'results' envelope."""
    return {
        "results": {
            "singles_male": {"parameters": params},
        }
    }


def write_init(params: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(make_init_json(params), f, indent=2)
    print(f"  Wrote init: {path.name}")


# ---------------------------------------------------------------------------
# Dispersed interior start (S4)
# ---------------------------------------------------------------------------
# Chosen manually to be clearly away from the boundary:
# - theta_c = -2.0  (inside the [-8, 0] bound, not at 0)
# - beta_ll = 0.5   (inside [-2, 2], not at 2)
# - beta_c = 2.0    (lower than M0b2 but positive)
# - leisure intercepts near M0b2 but halved
# - occupation and wage params from M0b2 solution (well-identified block)
S4_INTERIOR = {
    "beta_l0_sm": 2.0, "beta_l_age_sm": 0.0, "beta_l_age2_sm": 0.002,
    "beta_c_sm": 0.8, "theta_l_sm": -0.5,
    "beta_l0_sf": 2.5, "beta_l_age_sf": 0.002, "beta_l_age2_sf": 0.002,
    "beta_l_nkids_sf": 0.05, "beta_c_sf": 0.7, "theta_l_sf": -0.5,
    "theta_c_singles": -2.0,
    "beta_l0_m": 1.0, "beta_l_age_m": -0.01, "beta_l_age2_m": 0.002,
    "theta_l_m": -0.5,
    "beta_l0_f": 1.5, "beta_l_age_f": -0.03, "beta_l_age2_f": 0.003,
    "beta_l_nkids_f": 0.15, "theta_l_f": -0.5,
    "beta_c": 2.0, "theta_c": -2.0,   # well inside bound
    "beta_E": -2.0, "beta_h_pt1": -0.5, "beta_h_pt2": 0.3, "beta_h_ft": 1.0,
    "beta_E_gsur": -0.5, "beta_E_educH": 0.4,
    "beta_w0": 2.03, "beta_w_educL": -0.05, "beta_w_educH": 0.32,
    "beta_w_pexp": 0.018, "beta_w_pexp2": -0.00022,
    "beta_occ_2_sm": -1.5, "beta_occ_3_sm": -2.2, "beta_occ_4_sm": 0.02,
    "beta_occ_2_sf": 0.0,  "beta_occ_3_sf": -0.5, "beta_occ_4_sf": 0.8,
    "beta_occ_2_cm": -1.5, "beta_occ_3_cm": -2.2, "beta_occ_4_cm": 0.5,
    "beta_occ_2_cf": 0.2,  "beta_occ_3_cf": -0.2, "beta_occ_4_cf": 1.1,
    "sigma": 0.43,
    "beta_ll": 0.5,   # well inside bound
}


def build_starts() -> list[tuple[str, dict, str]]:
    """Return list of (label, params, description)."""
    starts = []

    # S1: spec defaults
    starts.append(("S1_spec_defaults", SPEC_DEFAULTS,
                    "Spec defaults from YAML initial_values block"))

    # S2: perturb spec defaults (sigma=0.15, seed=42)
    # Use a reduced sigma for Box-Cox exponents so they stay well inside bounds.
    s2 = perturb(SPEC_DEFAULTS, sigma=0.15, seed=42)
    # Additional guard: theta_c_singles must stay below -0.1 (well inside [-8, 0.95])
    s2["theta_c_singles"] = float(np.clip(s2["theta_c_singles"], -8.0, -0.1))
    starts.append(("S2_perturb_defaults", s2,
                    "Gaussian perturbation around spec defaults (sigma=0.15, seed=42, tc_s clipped to <=-.1)"))

    # S3: perturb M0b2 solution (sigma=0.10, seed=7)
    s3 = perturb(REFERENCE_SOLUTION, sigma=0.10, seed=7)
    starts.append(("S3_perturb_solution", s3,
                    "Gaussian perturbation around M0b2 solution (sigma=0.10, seed=7)"))

    # S4: dispersed interior
    starts.append(("S4_dispersed_interior", clip(S4_INTERIOR),
                    "Manually dispersed interior start (theta_c=-2, beta_ll=0.5, beta_c=2)"))

    return starts


def run_estimation(init_json: Path, label: str, dry_run: bool) -> dict:
    """Run a single estimation and return a result summary dict."""
    cmd = [
        str(PYTHON), str(SCRIPT),
        "--mnl-base", "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl",
        "--output-dir", str(OUTPUT_DIR),
        "--group", "joint",
        "--solver", "gamspy-conopt",
        "--vectorized",
        "--spec-config", str(SPEC),
        "--warm-start", "none",
        "--init-params", str(init_json),
        "--auto-timestamp",
        "--verbose",
    ]
    cmd_str = " ".join(f'"{c}"' if " " in c else c for c in cmd)

    print(f"\n{'='*72}")
    print(f"START: {label}")
    print(f"{'='*72}")
    print(f"Command:\n  {cmd_str}\n")

    result = {
        "label": label,
        "init_json": str(init_json),
        "command": cmd_str,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "run_folder": None,
        "success": None,
        "final_ll": None,
        "walltime": None,
        "returncode": None,
        "error": None,
    }

    if dry_run:
        print("  [DRY-RUN] Skipping execution.")
        result["success"] = "dry_run"
        return result

    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=False,
            text=True,
            cwd=str(REPO_ROOT),
        )
        result["returncode"] = proc.returncode
        result["walltime"] = round(time.time() - t0, 1)
        if proc.returncode != 0:
            result["success"] = False
            result["error"] = f"returncode={proc.returncode}"
        else:
            result["success"] = True
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        result["walltime"] = round(time.time() - t0, 1)

    result["ended_at"] = datetime.now(timezone.utc).isoformat()
    return result


def find_latest_run_folder() -> Path | None:
    """Return the most-recently created run folder under estimation_spec_ruro_occ_M0b2/."""
    base = OUTPUT_DIR / "estimation_spec_ruro_occ_M0b2"
    if not base.exists():
        return None
    runs = sorted(base.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    return runs[0] if runs else None


def read_run_summary(run_folder: Path) -> dict:  # type: ignore[type-arg]
    """Parse estimation_results.json and identification_diagnostics.txt."""
    summary: dict = {"run_folder": str(run_folder)}

    results_path = run_folder / "estimation_results.json"
    diag_path    = run_folder / "identification_diagnostics.txt"

    if results_path.exists():
        with open(results_path) as f:
            data = json.load(f)
        # Pull from first group (they're all identical in joint estimation)
        first = next(iter(data["results"].values()))
        summary["success"] = first.get("success")
        summary["message"] = first.get("message", "")
        summary["final_ll"] = first.get("final_ll")
        summary["n_iterations"] = first.get("n_iterations")
        summary["walltime"] = first.get("walltime_seconds")
        params = first.get("parameters", {})
        summary["theta_c"]  = params.get("theta_c")
        summary["beta_ll"]  = params.get("beta_ll")
        summary["beta_c"]   = params.get("beta_c")
        summary["theta_c_singles"] = params.get("theta_c_singles")
        summary["params"] = params

    if diag_path.exists():
        lines = diag_path.read_text().splitlines()
        for line in lines:
            if "hessian_condition_number:" in line:
                try:
                    summary["kappa"] = float(line.split(":")[-1].strip())
                except ValueError:
                    pass
            elif "hessian_negative_eigenvalues:" in line:
                try:
                    summary["neg_eigenvalues"] = int(line.split(":")[-1].strip())
                except ValueError:
                    pass
            elif "negative_variances_from_varcov:" in line:
                try:
                    summary["neg_variances"] = int(line.split(":")[-1].strip())
                except ValueError:
                    pass

    return summary


def main():
    parser = argparse.ArgumentParser(description="M0b2 multi-start runner")
    parser.add_argument("--dry-run", action="store_true",
                        help="Write init JSONs and print commands without running")
    args = parser.parse_args()

    STARTS_DIR.mkdir(parents=True, exist_ok=True)

    starts = build_starts()
    print(f"\nM0b2 multi-start robustness check -- {len(starts)} starts")
    print(f"Spec: {SPEC}")
    print(f"Init JSONs -> {STARTS_DIR}\n")

    # Write all init JSONs first
    init_paths = []
    for label, params, desc in starts:
        path = STARTS_DIR / f"{label}_init.json"
        write_init(params, path)
        init_paths.append((label, params, desc, path))

    # Print start vector summary
    print("\nStart vector summary (key parameters):")
    print(f"{'label':<30} {'theta_c':>10} {'beta_ll':>10} {'beta_c':>10} {'theta_c_s':>10}")
    print("-" * 72)
    for label, params, desc, _ in init_paths:
        print(f"{label:<30} {params['theta_c']:>10.3f} {params['beta_ll']:>10.3f} "
              f"{params['beta_c']:>10.3f} {params['theta_c_singles']:>10.3f}")

    # Run estimations sequentially
    run_results = []
    summaries = []

    for label, params, desc, init_path in init_paths:
        run_meta = run_estimation(init_path, label, dry_run=args.dry_run)
        run_results.append((label, desc, run_meta))

        if not args.dry_run and run_meta.get("success"):
            # Give the filesystem a moment then find the new run folder
            time.sleep(2)
            run_folder = find_latest_run_folder()
            if run_folder:
                run_meta["run_folder"] = str(run_folder)
                s = read_run_summary(run_folder)
                s["label"] = label
                s["description"] = desc
                summaries.append(s)
                print(f"\n  Run folder: {run_folder.name}")
                print(f"  LL = {s.get('final_ll')}")
                print(f"  theta_c = {s.get('theta_c')}, beta_ll = {s.get('beta_ll')}")
                print(f"  kappa = {s.get('kappa')}, neg_eig = {s.get('neg_eigenvalues')}")
            else:
                summaries.append({"label": label, "description": desc,
                                   "error": "run folder not found"})
        elif args.dry_run:
            summaries.append({"label": label, "description": desc, "success": "dry_run"})
        else:
            summaries.append({"label": label, "description": desc,
                               "success": False, "error": run_meta.get("error")})

    # Write summary JSON
    summary_path = RESULTS_DIR / "_M0b2_multistart_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summaries, f, indent=2, default=str)
    print(f"\nSummary JSON -> {summary_path}")

    # Print final table
    print("\n" + "="*72)
    print("MULTISTART RESULTS SUMMARY")
    print("="*72)
    print(f"{'label':<30} {'LL':>12} {'tc':>8} {'bll':>8} {'kappa':>12} {'neg_eig':>8}")
    print("-"*72)
    ref_ll = -6511.473121262083
    for s in summaries:
        if s.get("success") == "dry_run":
            print(f"{s['label']:<30} {'[dry-run]':>12}")
        else:
            ll   = s.get("final_ll", float("nan"))
            tc   = s.get("theta_c",  float("nan"))
            bll  = s.get("beta_ll",  float("nan"))
            kap  = s.get("kappa",    float("nan"))
            neig = s.get("neg_eigenvalues", "?")
            flag = " *** BETTER" if (isinstance(ll, float) and ll < ref_ll - 0.1) else ""
            print(f"{s['label']:<30} {ll:>12.4f} {tc:>8.4f} {bll:>8.4f} "
                  f"{kap:>12.3e} {neig:>6}{flag}")
    print(f"\nReference (run_2026-05-14_12-46-04) LL = {ref_ll:.4f}")


if __name__ == "__main__":
    main()
