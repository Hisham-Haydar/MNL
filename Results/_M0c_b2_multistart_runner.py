"""
Multi-start robustness check for ruro_occ_M0c_b2.

Runs 3 starts with identical spec/data/engine, varying only the initial
parameter vector. Each start uses --warm-start none and --init-params <json>.

Start design
------------
S1 : spec defaults           (beta_l0_m=0.01, beta_ll=2.0, all others at YAML defaults)
S2 : warm-start from M0c_b   (beta_l0_m=0.050 M0c_b bound, beta_ll=2.587 M0c_b solution)
S3 : dispersed interior      (beta_l0_m=1.0, beta_ll=5.0, beta_c=2, theta_c_singles=-1.5)

The perturb_defaults start (S2 in M0b2) is intentionally omitted — it caused
a GAMS arithmetic overflow in M0b2 (theta_c=0, beta_c near zero) and provides
no additional information given the M0c_b2 bound structure.

Usage
-----
    python Results/_M0c_b2_multistart_runner.py [--dry-run]
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
REPO_ROOT  = Path(__file__).resolve().parent.parent
PYTHON     = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
SCRIPT     = REPO_ROOT / "scripts" / "enhanced" / "enh_RURO_estimate_FR.py"
SPEC       = REPO_ROOT / "scripts" / "enhanced" / "estimation_spec_ruro_occ_M0c_b2.yaml"
OUTPUT_DIR = REPO_ROOT / "outputs" / "estimates" / "fr" / "spec" / "ruro_occ" / "gamspy"
RESULTS_DIR = Path(__file__).resolve().parent   # Results/
STARTS_DIR  = RESULTS_DIR / "_M0c_b2_multistart_inits"

# M0c_b reference solution
M0C_B_JSON = (
    REPO_ROOT
    / "outputs" / "estimates" / "fr" / "spec" / "ruro_occ" / "gamspy"
    / "estimation_spec_ruro_occ_M0c_b" / "run_2026-05-14_18-03-32"
    / "estimation_results.json"
)

# ---------------------------------------------------------------------------
# Bounds (from estimation_spec_ruro_occ_M0c_b2.yaml)
# ---------------------------------------------------------------------------
BOUNDS = {
    "theta_l_sm":       (-8.0,  0.95),
    "theta_l_sf":       (-8.0,  0.95),
    "theta_l_m":        (-8.0,  0.95),
    "theta_l_f":        (-8.0,  0.95),
    "theta_c_singles":  (-8.0,  0.95),
    # theta_c is NOT estimated in M0c_b2 (fixed at 0.0)
    "beta_c_sm":        (0.05,  50.0),
    "beta_c_sf":        (0.05,  50.0),
    "beta_c":           (0.05,  50.0),
    "beta_l0_sm":       (0.05,  50.0),
    "beta_l0_sf":       (0.05,  50.0),
    "beta_l0_m":        (1e-6,  50.0),   # RELAXED bound
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
    "beta_ll":          (0.0,   10.0),
}

# ---------------------------------------------------------------------------
# Spec defaults (from YAML initial_values block)
# ---------------------------------------------------------------------------
SPEC_DEFAULTS = {
    "beta_l0_sm": 1.0, "beta_l_age_sm": 0.0, "beta_l_age2_sm": 0.0,
    "beta_c_sm": 1.0, "theta_l_sm": -1.0,
    "beta_l0_sf": 1.0, "beta_l_age_sf": 0.0, "beta_l_age2_sf": 0.0,
    "beta_l_nkids_sf": 0.0, "beta_c_sf": 1.0, "theta_l_sf": -1.0,
    "theta_c_singles": -1.0,
    "beta_l0_m": 0.01,   # M0c_b2 interior start
    "beta_l_age_m": 0.0, "beta_l_age2_m": 0.0, "theta_l_m": -1.0,
    "beta_l0_f": 1.0, "beta_l_age_f": 0.0, "beta_l_age2_f": 0.0,
    "beta_l_nkids_f": 0.0, "theta_l_f": -1.0,
    "beta_c": 1.0,
    "beta_E": 0.0, "beta_h_pt1": 0.0, "beta_h_pt2": 0.0, "beta_h_ft": 0.0,
    "beta_E_gsur": 0.0, "beta_E_educH": 0.0,
    "beta_w0": 2.0, "beta_w_educL": -0.1, "beta_w_educH": 0.2,
    "beta_w_pexp": 0.02, "beta_w_pexp2": -0.0003,
    "beta_occ_2_sm": 0.0, "beta_occ_3_sm": 0.0, "beta_occ_4_sm": 0.0,
    "beta_occ_2_sf": 0.0, "beta_occ_3_sf": 0.0, "beta_occ_4_sf": 0.0,
    "beta_occ_2_cm": 0.0, "beta_occ_3_cm": 0.0, "beta_occ_4_cm": 0.0,
    "beta_occ_2_cf": 0.0, "beta_occ_3_cf": 0.0, "beta_occ_4_cf": 0.0,
    "sigma": 0.5,
    "beta_ll": 2.0,
}

# M0c_b solution — warm-start base for S2
M0C_B_SOLUTION = {
    "beta_l0_sm": 3.8738963488214653,
    "beta_l_age_sm": 0.008491091199549702,
    "beta_l_age2_sm": 0.0020284148902118787,
    "beta_c_sm": 0.635715082998644,
    "theta_l_sm": -0.7119594820382561,
    "beta_l0_sf": 4.458618723695226,
    "beta_l_age_sf": 0.0019072475553389271,
    "beta_l_age2_sf": 0.004133635702890313,
    "beta_l_nkids_sf": 0.056771485539015634,
    "beta_c_sf": 0.5759191693700898,
    "theta_l_sf": -0.7280419219426024,
    "theta_c_singles": -0.9358026317472644,
    "beta_l0_m": 0.050,             # M0c_b was at bound; use as-is for S2
    "beta_l_age_m": -0.007906769556612915,
    "beta_l_age2_m": 0.0006086080711105012,
    "theta_l_m": -0.7329157729011593,
    "beta_l0_f": 2.6133525539417883,
    "beta_l_age_f": -0.05738948794414411,
    "beta_l_age2_f": 0.002790122399612525,
    "beta_l_nkids_f": 0.17672910784723966,
    "theta_l_f": -0.677689699568494,
    "beta_c": 4.050974395613109,
    "beta_E": -2.8420398478346103,
    "beta_h_pt1": -0.498778705585631,
    "beta_h_pt2": 0.36503978133283926,
    "beta_h_ft": 1.4440628020812214,
    "beta_E_gsur": -0.7437606333582467,
    "beta_E_educH": 0.6134190374518135,
    "beta_occ_2_sm": -1.5104183390745827,
    "beta_occ_3_sm": -2.1651262281177783,
    "beta_occ_4_sm": 0.023633387532973647,
    "beta_occ_2_sf": -0.01050045090930524,
    "beta_occ_3_sf": -0.5609873573019456,
    "beta_occ_4_sf": 0.7987792906283999,
    "beta_occ_2_cm": -1.4759147563230401,
    "beta_occ_3_cm": -2.2239079898168517,
    "beta_occ_4_cm": 0.47258961979322145,
    "beta_occ_2_cf": 0.17618927456075792,
    "beta_occ_3_cf": -0.21636537113223236,
    "beta_occ_4_cf": 1.1147015001020164,
    "beta_w0": 2.024868654102717,
    "beta_w_educL": -0.05100712020896628,
    "beta_w_educH": 0.31611605934032283,
    "beta_w_pexp": 0.018096308998926374,
    "beta_w_pexp2": -0.00021863083190904484,
    "sigma": 0.42676318602387164,
    "beta_ll": 2.586500289813485,
}

# Dispersed interior start (S3)
S3_INTERIOR = {
    "beta_l0_sm": 2.0, "beta_l_age_sm": 0.0, "beta_l_age2_sm": 0.002,
    "beta_c_sm": 0.8, "theta_l_sm": -0.5,
    "beta_l0_sf": 2.5, "beta_l_age_sf": 0.002, "beta_l_age2_sf": 0.002,
    "beta_l_nkids_sf": 0.05, "beta_c_sf": 0.7, "theta_l_sf": -0.5,
    "theta_c_singles": -1.5,
    "beta_l0_m": 1.0,    # clearly interior in [1e-6, 50]
    "beta_l_age_m": -0.01, "beta_l_age2_m": 0.002, "theta_l_m": -0.5,
    "beta_l0_f": 1.5, "beta_l_age_f": -0.03, "beta_l_age2_f": 0.003,
    "beta_l_nkids_f": 0.15, "theta_l_f": -0.5,
    "beta_c": 2.0,
    "beta_E": -2.0, "beta_h_pt1": -0.5, "beta_h_pt2": 0.3, "beta_h_ft": 1.0,
    "beta_E_gsur": -0.5, "beta_E_educH": 0.4,
    "beta_w0": 2.03, "beta_w_educL": -0.05, "beta_w_educH": 0.32,
    "beta_w_pexp": 0.018, "beta_w_pexp2": -0.00022,
    "beta_occ_2_sm": -1.5, "beta_occ_3_sm": -2.2, "beta_occ_4_sm": 0.02,
    "beta_occ_2_sf": 0.0,  "beta_occ_3_sf": -0.5, "beta_occ_4_sf": 0.8,
    "beta_occ_2_cm": -1.5, "beta_occ_3_cm": -2.2, "beta_occ_4_cm": 0.5,
    "beta_occ_2_cf": 0.2,  "beta_occ_3_cf": -0.2, "beta_occ_4_cf": 1.1,
    "sigma": 0.43,
    "beta_ll": 5.0,   # mid-range in [0, 10]
}


def clip(params: dict) -> dict:
    out = {}
    for k, v in params.items():
        if k in BOUNDS:
            lo, hi = BOUNDS[k]
            out[k] = float(np.clip(v, lo, hi))
        else:
            out[k] = float(v)
    return out


def make_init_json(params: dict) -> dict:
    return {"results": {"singles_male": {"parameters": params}}}


def write_init(params: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(make_init_json(params), f, indent=2)
    print(f"  Wrote init: {path.name}")


def build_starts() -> list:
    starts = []

    # S1: spec defaults
    starts.append(("S1_spec_defaults", clip(SPEC_DEFAULTS),
                    "YAML spec defaults (beta_l0_m=0.01, beta_ll=2.0)"))

    # S2: M0c_b warm-start (beta_l0_m at previous bound, beta_ll at M0c_b solution)
    starts.append(("S2_warmstart_M0c_b", clip(M0C_B_SOLUTION),
                    "M0c_b solution as warm-start (beta_l0_m=0.050, beta_ll=2.587)"))

    # S3: dispersed interior
    starts.append(("S3_dispersed_interior", clip(S3_INTERIOR),
                    "Dispersed interior (beta_l0_m=1.0, beta_ll=5.0, beta_c=2, tc_s=-1.5)"))

    return starts


def run_estimation(init_json: Path, label: str, dry_run: bool) -> dict:
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
        proc = subprocess.run(cmd, capture_output=False, text=True, cwd=str(REPO_ROOT))
        result["returncode"] = proc.returncode
        result["walltime"] = round(time.time() - t0, 1)
        result["success"] = proc.returncode == 0
        if proc.returncode != 0:
            result["error"] = f"returncode={proc.returncode}"
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        result["walltime"] = round(time.time() - t0, 1)

    result["ended_at"] = datetime.now(timezone.utc).isoformat()
    return result


def find_latest_run_folder() -> Path | None:
    base = OUTPUT_DIR / "estimation_spec_ruro_occ_M0c_b2"
    if not base.exists():
        return None
    runs = sorted(base.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    return runs[0] if runs else None


def read_run_summary(run_folder: Path) -> dict:
    summary: dict = {"run_folder": str(run_folder)}

    results_path = run_folder / "estimation_results.json"
    diag_path    = run_folder / "identification_diagnostics.txt"

    if results_path.exists():
        with open(results_path) as f:
            data = json.load(f)
        first = next(iter(data["results"].values()))
        summary["success"]      = first.get("success")
        summary["message"]      = first.get("message", "")
        summary["final_ll"]     = first.get("final_ll")
        summary["n_iterations"] = first.get("n_iterations")
        summary["walltime"]     = first.get("walltime_seconds")
        params = first.get("parameters", {})
        summary["beta_l0_m"]       = params.get("beta_l0_m")
        summary["beta_ll"]         = params.get("beta_ll")
        summary["beta_c"]          = params.get("beta_c")
        summary["theta_c_singles"] = params.get("theta_c_singles")
        summary["params"]          = params

    if diag_path.exists():
        for line in diag_path.read_text().splitlines():
            if "hessian_condition_number:" in line:
                try: summary["kappa"] = float(line.split(":")[-1].strip())
                except ValueError: pass
            elif "hessian_negative_eigenvalues:" in line:
                try: summary["neg_eigenvalues"] = int(line.split(":")[-1].strip())
                except ValueError: pass
            elif "negative_variances_from_varcov:" in line:
                try: summary["neg_variances"] = int(line.split(":")[-1].strip())
                except ValueError: pass
            elif "bounded_hits_total:" in line:
                try: summary["bounded_hits_total"] = int(line.split(":")[-1].strip())
                except ValueError: pass

    return summary


def main():
    parser = argparse.ArgumentParser(description="M0c_b2 multi-start runner")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    STARTS_DIR.mkdir(parents=True, exist_ok=True)

    starts = build_starts()
    print(f"\nM0c_b2 multi-start robustness check -- {len(starts)} starts")
    print(f"Spec: {SPEC}")
    print(f"Init JSONs -> {STARTS_DIR}\n")

    init_paths = []
    for label, params, desc in starts:
        path = STARTS_DIR / f"{label}_init.json"
        write_init(params, path)
        init_paths.append((label, params, desc, path))

    print("\nStart vector summary (key parameters):")
    print(f"{'label':<30} {'b_l0_m':>10} {'beta_ll':>10} {'beta_c':>10} {'tc_s':>10}")
    print("-" * 64)
    for label, params, desc, _ in init_paths:
        print(f"{label:<30} {params['beta_l0_m']:>10.4f} {params['beta_ll']:>10.3f} "
              f"{params['beta_c']:>10.3f} {params['theta_c_singles']:>10.3f}")

    run_results = []
    summaries = []

    for label, params, desc, init_path in init_paths:
        run_meta = run_estimation(init_path, label, dry_run=args.dry_run)
        run_results.append((label, desc, run_meta))

        if not args.dry_run and run_meta.get("success"):
            time.sleep(2)
            run_folder = find_latest_run_folder()
            if run_folder:
                run_meta["run_folder"] = str(run_folder)
                s = read_run_summary(run_folder)
                s["label"]       = label
                s["description"] = desc
                summaries.append(s)
                print(f"\n  Run folder: {run_folder.name}")
                print(f"  LL = {s.get('final_ll')}")
                print(f"  beta_l0_m = {s.get('beta_l0_m')}, beta_ll = {s.get('beta_ll')}")
                print(f"  kappa = {s.get('kappa')}, neg_eig = {s.get('neg_eigenvalues')}")
            else:
                summaries.append({"label": label, "description": desc,
                                   "error": "run folder not found"})
        elif args.dry_run:
            summaries.append({"label": label, "description": desc, "success": "dry_run"})
        else:
            summaries.append({"label": label, "description": desc,
                               "success": False, "error": run_meta.get("error")})

    summary_path = RESULTS_DIR / "_M0c_b2_multistart_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summaries, f, indent=2, default=str)
    print(f"\nSummary JSON -> {summary_path}")

    print("\n" + "="*72)
    print("M0c_b2 MULTISTART RESULTS SUMMARY")
    print("="*72)
    ref_ll = -6509.324974310221  # M0c_b reference
    print(f"{'label':<30} {'LL':>12} {'b_l0_m':>10} {'bll':>8} {'kappa':>12} {'neg_eig':>8}")
    print("-"*72)
    for s in summaries:
        if s.get("success") == "dry_run":
            print(f"{s['label']:<30} {'[dry-run]':>12}")
        else:
            ll   = s.get("final_ll", float("nan"))
            blm  = s.get("beta_l0_m", float("nan"))
            bll  = s.get("beta_ll",   float("nan"))
            kap  = s.get("kappa",     float("nan"))
            neig = s.get("neg_eigenvalues", "?")
            flag = " *** BETTER" if (isinstance(ll, float) and ll < ref_ll - 0.1) else ""
            ll_str   = f"{ll:.4f}"  if isinstance(ll,  float) else str(ll)
            blm_str  = f"{blm:.6f}" if isinstance(blm, float) else str(blm)
            bll_str  = f"{bll:.4f}" if isinstance(bll, float) else str(bll)
            kap_str  = f"{kap:.3e}" if isinstance(kap, float) else str(kap)
            print(f"{s['label']:<30} {ll_str:>12} {blm_str:>10} {bll_str:>8} "
                  f"{kap_str:>12} {str(neig):>6}{flag}")
    print(f"\nM0c_b reference LL = {ref_ll:.4f}")


if __name__ == "__main__":
    main()
