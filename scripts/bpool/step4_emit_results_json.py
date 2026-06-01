"""
Emit per-group estimation_results.json from a joint baseline, so the REGULAR
post-estimation pipeline (RURO_post_estimation_styled.py) can produce the full
per-group report (participation/hours fit, wage/hours distributions, MUC/MUL,
indifference contours, elasticities, inference + hessian diagnostics) for each
of the 4 groups (singles-male, singles-female, couples-male, couples-female).

WHY: the joint baseline estimates sm+sf+couples together and writes a flat
theta_hat CSV + a custom report. The full plotting pipeline instead expects a
single-group estimation_results.json (the schema enh_RURO_estimate_FR.save_results_json
writes) + that group's microdata + the spec. This script bridges the two: it
writes one estimation_results.json per group, each carrying the FULL joint
parameter vector (so the spec-driven V-function is computed the joint way),
plus the joint SEs (Hessian + clustered) and hessian diagnostics. You then run
the regular post-estimation command once per group (see --print-commands).

AGNOSTIC: nothing here is country/year/spec-specific. Groups, param names,
SEs, and microdata stems are all derived from the spec + the joint JSON + CLI
stems. Works for the 47-param or 49-param (gsplit) joint baseline unchanged.

USAGE:
  python step4_emit_results_json.py \
    --spec specs/estimation_spec_joint_pooled_v1_bll0_tlmpin_gsplit.yaml \
    --theta-hat specs/theta_hat_realdata_901_gsplit_v1.csv \
    --baseline-json .../RURO_realdata_2016_2017_joint_901_gsplit_v1.md \
    --mnl-base-dir C:/Users/hisham/MNL/EUROMOD-STORAGE/new_data \
    --out-dir C:/Users/hisham/MNL/EUROMOD-STORAGE/outputs/post_estimation/realdata_joint_901_gsplit \
    --year-tag 2016 --print-commands
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

_script_dir = Path(__file__).resolve().parent
_enhanced_dir = _script_dir.parent / "enhanced"
sys.path.insert(0, str(_enhanced_dir))
sys.path.insert(0, str(_script_dir))

import estimation_spec_parser as sp          # noqa: E402


# Group key -> (pipeline group name, microdata stem suffix). The stem suffixes
# match the per-group engine-ready parquets (e.g. fr_p3a_bpool_engine_ready_sm2016).
# Couples-male / couples-female share the couples microdata; the pipeline splits
# them by its couples_male/couples_female group canonicalisation.
_GROUPS = [
    ("singles_male",   "sm"),
    ("singles_female", "sf"),
    ("couples_male",   "cm"),
    ("couples_female", "cf"),
]


def _load_json_or_md(path: Path) -> dict:
    text = Path(path).read_text(encoding="utf-8")
    s = text.lstrip()
    if s.startswith("{"):
        return json.loads(text)
    blocks = re.findall(r"```json\s*(.*?)```", text, flags=re.DOTALL)
    return json.loads(max(blocks, key=len)) if blocks else json.loads(text)


def _stem_for(group_key: str, mnl_base_dir: Path, base_stem: str,
              year_tag: str) -> Path:
    """Per-group microdata base path the pipeline's --mnl-base expects.
    Mirrors the slice runs: fr_p3a_bpool_engine_ready_<grp><year>."""
    grp = dict(_GROUPS)[group_key]
    # couples groups share the couples stem prefix 'c'
    short = {"sm": "sm", "sf": "sf", "cm": "c", "cf": "c"}[grp]
    return mnl_base_dir / f"{base_stem}_{short}{year_tag}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--theta-hat", type=Path, required=True,
                    help="Joint theta_hat CSV (parameter,value[,se_hessian,se_clustered]).")
    ap.add_argument("--baseline-json", type=Path, required=True,
                    help="Joint baseline JSON or .md (for hessian/cluster info).")
    ap.add_argument("--mnl-base-dir", type=Path, required=True)
    ap.add_argument("--base-stem", default="fr_p3a_bpool_engine_ready")
    ap.add_argument("--year-tag", default="2016",
                    help="Microdata stem year tag (e.g. 2016 for the *_sm2016 stems).")
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--se", choices=["hessian", "clustered"], default="clustered",
                    help="Which SE flavour to write into standard_errors.se "
                         "(the report's inference table). Default clustered "
                         "(the conservative one).")
    ap.add_argument("--print-commands", action="store_true",
                    help="Print the ready-to-run regular post-estimation "
                         "command for each group.")
    ap.add_argument("--joint-mode", action="store_true",
                    help="Emit ONE estimation_results.json with group='joint' "
                         "(instead of 4 per-group files). Run the pipeline ONCE "
                         "with --mnl-base = a stem that has BOTH __singles and "
                         "__couples parquets (e.g. fr_p3a_bpool_engine_ready) -> "
                         "a SINGLE unified report covering all 4 groups' plots "
                         "(like the JMP_pooled reference). This is the preferred "
                         "mode.")
    ap.add_argument("--joint-stem", default="fr_p3a_bpool_engine_ready",
                    help="For --joint-mode: the --mnl-base stem (must have both "
                         "__singles.parquet and __couples.parquet).")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    spec = sp.parse_specification(args.spec)
    pnames = list(spec.all_param_names)
    jb = _load_json_or_md(args.baseline_json)

    # theta_hat + SEs, aligned to spec param order
    df = pd.read_csv(args.theta_hat)
    val = dict(zip(df["parameter"].astype(str), df["value"].astype(float)))
    se_h = (dict(zip(df["parameter"].astype(str), df["se_hessian"]))
            if "se_hessian" in df.columns else {})
    se_c = (dict(zip(df["parameter"].astype(str), df["se_clustered"]))
            if "se_clustered" in df.columns else {})
    theta = np.array([val[n] for n in pnames], dtype=np.float64)
    se_src = se_c if args.se == "clustered" else se_h
    se_vec = [(_f(se_src.get(n))) for n in pnames]

    # parameters dict (flat names) — the joint vector; the spec drives V so the
    # pipeline computes each group's predicted probabilities the joint way.
    parameters = {n: float(theta[i]) for i, n in enumerate(pnames)}
    # include fixed (pinned) params so V is complete (the report shows them too)
    for fn, fv in (getattr(spec, "fixed_params", {}) or {}).items():
        parameters.setdefault(fn, float(fv))

    bounds_dict, initial_dict = {}, {}
    for n in pnames:
        if n in spec.bounds:
            lo, hi = spec.bounds[n]
            bounds_dict[n] = [lo, hi]
        initial_dict[n] = float(spec.initial_values.get(n, 0.0))

    hess = jb.get("hessian", {}) or {}
    hessian_diag = {
        "condition_number": hess.get("cond"),
        "min_eigenvalue": hess.get("min_eig"),
        "max_eigenvalue": None,
        "n_negative_eigenvalues": 0 if hess.get("pd") else None,
        "poorly_identified_params": [],
        "eigenvalues": None,
        "top_correlations": [],
    }

    # t / p from the chosen SE
    t_vals, p_vals = [], []
    from math import erf, sqrt
    def _norm_sf(z):
        return 0.5 * (1 - erf(abs(z) / sqrt(2)))
    for i, n in enumerate(pnames):
        s = se_vec[i]
        if s is None or s <= 0:
            t_vals.append(None); p_vals.append(None)
        else:
            t = float(theta[i] / s)
            t_vals.append(t); p_vals.append(2.0 * _norm_sf(t))

    standard_errors = {"se": se_vec, "t_values": t_vals, "p_values": p_vals}

    # per-group HH counts from the joint JSON (n_obs_total must be a real int —
    # the pipeline does `n_obs_total > 0`, which crashes on None).
    nhh = jb.get("n_hh", {}) or {}
    _grp_nhh = {"singles_male": nhh.get("sm", 0),
                "singles_female": nhh.get("sf", 0),
                "couples_male": nhh.get("cou", 0),
                "couples_female": nhh.get("cou", 0)}
    total_nhh = int(sum(int(v or 0) for v in nhh.values()))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    ts = datetime.now(timezone.utc).isoformat()
    _ll = (-float(jb.get("negLL")) if jb.get("negLL") is not None else None)
    _diag = jb.get("diagnostics", {}) or {}  # solver/timing/gradient diagnostics

    # joint-mode: a single 'joint' group whose --mnl-base stem carries BOTH
    # __singles and __couples parquets -> one unified report covering all groups
    # (the JMP_pooled reference shape). Otherwise the 4 per-group files.
    if args.joint_mode:
        _emit_list = [("joint", args.mnl_base_dir / args.joint_stem)]
        _nhh_for = {"joint": total_nhh}
    else:
        _emit_list = [(gk, _stem_for(gk, args.mnl_base_dir, args.base_stem,
                                     args.year_tag)) for gk, _ in _GROUPS]
        _nhh_for = _grp_nhh

    for group_key, stem in _emit_list:
        summary = {
            "joint_ll": _ll,
            "n_obs_total": int(_nhh_for.get(group_key, 0) or 0),
            "n_groups_total": int(_nhh_for.get(group_key, 0) or 0),
            # the report's header "Estimation" time reads total_walltime_seconds;
            # use the ESTIMATION wall (scipy+optimistix), not the whole-run total.
            "total_walltime_seconds": _diag.get("estimation_seconds"),
            "n_iterations": _diag.get("n_iterations"),
            "full_run_seconds": _diag.get("total_seconds"),
            "solver_timing": {k: _diag.get(k) for k in (
                "scipy_stage1_seconds", "optimistix_stage2_seconds",
                "estimation_seconds", "hessian_seconds", "sandwich_seconds",
                "post_estimation_seconds", "total_seconds")},
            "solver": _diag.get("solver"),
            "final_max_grad": _diag.get("final_max_grad"),
            "gradient_kind": _diag.get("gradient_kind"),
            "prior_correction_applied": True,
            "market_centering_applied": True,
            "source": "joint baseline re-emitted per group (step4_emit_results_json.py)",
        }
        out = {
            "specification": spec.name,
            "wage_spec": getattr(spec, "wage_spec", "vw"),
            "timestamp": ts,
            "command_line": " ".join(sys.argv),
            "metadata": {
                "mnl_base": str(stem),
                "spec_config": str(args.spec),
                "group": group_key,
                "n_jobs": -1,
                "opt_method": _diag.get("solver", "L-BFGS-B+optimistix (JAX)"),
                "analytical_gradient": True,
                "strict_validation": True,
                "solver_artifacts": {"saved": False, "solver_log": None,
                                     "listing_file": None},
                "note": ("joint baseline re-emitted per group; parameters are "
                         "the FULL joint vector, group selects the microdata/fit"),
            },
            "results": {
                group_key: {
                    "success": True,
                    "message": _diag.get("solver", "joint baseline (re-emit)"),
                    "n_iterations": _diag.get("n_iterations"),
                    "n_function_evaluations": _diag.get("n_function_evaluations"),
                    "final_ll": (-float(jb.get("negLL"))
                                 if jb.get("negLL") is not None else None),
                    "gradient_norm": _diag.get("final_max_grad", jb.get("max_grad")),
                    "walltime_seconds": _diag.get("estimation_seconds"),
                    # full timing + gradient breakdown (the report renders these)
                    "timing": {
                        "estimation_seconds": _diag.get("estimation_seconds"),
                        "scipy_stage1_seconds": _diag.get("scipy_stage1_seconds"),
                        "optimistix_stage2_seconds": _diag.get("optimistix_stage2_seconds"),
                        "hessian_seconds": _diag.get("hessian_seconds"),
                        "sandwich_seconds": _diag.get("sandwich_seconds"),
                        "post_estimation_seconds": _diag.get("post_estimation_seconds"),
                        "total_seconds": _diag.get("total_seconds"),
                    },
                    "gradient_kind": _diag.get("gradient_kind"),
                    "chosen_optimizer": _diag.get("chosen_optimizer"),
                    "parameters": parameters,
                    "theta": [float(x) for x in theta],
                    "bounds": bounds_dict,
                    "initial_values": initial_dict,
                    "convergence_diagnostics": {},
                }
            },
            "summary": summary,
            "standard_errors": standard_errors,
            "hessian_diagnostics": hessian_diag,
        }
        gdir = args.out_dir / group_key
        gdir.mkdir(parents=True, exist_ok=True)
        jpath = gdir / "estimation_results.json"
        jpath.write_text(json.dumps(out, indent=2), encoding="utf-8")
        written.append((group_key, jpath, stem))
        print(f"[emit] {group_key:<16} -> {jpath}")

    if args.print_commands:
        print("\n# Regular post-estimation command per group "
              "(produces the FULL report: fit, distributions, MUC/MUL, "
              "contours, elasticities, inference + hessian diagnostics):")
        for group_key, jpath, stem in written:
            print(
                f"\npython scripts/enhanced/RURO_post_estimation_styled.py \\\n"
                f"  --results-json \"{jpath}\" \\\n"
                f"  --mnl-base \"{stem}\" \\\n"
                f"  --output-dir \"{args.out_dir / group_key}\" \\\n"
                f"  --prefix \"{group_key}_\" \\\n"
                f"  --spec-config \"{args.spec}\" \\\n"
                f"  --compute-se")


def _f(x):
    if x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if (v != v) else v  # NaN -> None


if __name__ == "__main__":
    main()
