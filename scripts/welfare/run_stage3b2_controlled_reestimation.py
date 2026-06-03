"""
STAGE THREE, INCREMENT THREE-B2 — controlled real-data re-estimation on the validated staged
engine-ready baseline.

Runs the CERTIFIED estimation path (scripts/bpool/step4_realdata_baseline.py: warm-start ->
two-stage optimiser -> exact jax.hessian PD check -> idorighh-clustered sandwich -> per-param
table) on the STAGED engine-ready stem, initialised from the certified theta_hat. Then compares
the re-estimated theta against the certified theta parameter-by-parameter under the
PRE-REGISTERED Three-A movement criterion, and emits a REAL-DATA-ONLY verdict.

Does NOT: run synthetic recovery, compute V_i^dir, price redrawn nodes, promote W^3, swap/
overwrite/move/delete any production parquet, promote any baseline to canonical, or overwrite
the certified theta_hat CSV. Synthetic recovery is the separate Three-B3 increment.

STOP conditions (do not force a verdict):
  - re-estimation does not converge            -> INCONCLUSIVE, STOP;
  - Hessian non-PD / clustered SEs unavailable -> INCONCLUSIVE, STOP.

Verdict (decomposition-relevant blocks = ability/wage + opportunity/access + preference):
  REAL-DATA IMMATERIAL  — all decomposition-relevant |delta|/cert_clustered_SE within band;
  REAL-DATA MATERIAL    — at least one decomposition-relevant param outside the band;
  INCONCLUSIVE          — convergence or SE failure.
This is NOT the final A/B verdict — synthetic recovery (Three-B3) is still required.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

_STEP4 = Path("scripts/bpool/step4_realdata_baseline.py").resolve()
_STAGED_STEM = "fr_p3a_bpool_engine_ready_staged_threeB1"
_CERT_SPEC = Path("scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml")
_CERT_THETA = Path("scripts/bpool/specs/theta_hat_realdata_901_v1.csv")
_REBUILT_THETA = Path("scripts/bpool/specs/theta_hat_rebuilt_realdata_901_v1.csv")

# Pre-registered movement band (Three-A criterion): a decomposition-relevant parameter's
# movement is IMMATERIAL if |delta| <= BAND_SIGMA * certified_clustered_SE.
_BAND_SIGMA = 1.0

# Block partition (matches step4 _classify_block), grouped into the decomposition-relevant
# super-blocks the criterion targets, plus the fixed/pinned set.
_BLOCK_TO_SUPER = {
    "wage_opp": "ability_wage",
    "market_hours_opp": "opportunity_access",
    "occupation_opp": "opportunity_access",
    "couples_leisure": "preference",
    "singles_leisure": "preference",
    "other": "other",
}
_DECOMP_RELEVANT = {"ability_wage", "opportunity_access", "preference"}


def _classify_block(name):
    if name.endswith("_sm") or name.endswith("_sf") or name == "theta_c_singles":
        return "singles_leisure"
    if name.endswith("_m") or name.endswith("_f"):
        if name.startswith("beta_occ_"):
            return "occupation_opp"
        return "couples_leisure"
    if name.startswith("beta_E") or name == "beta_E":
        return "market_hours_opp"
    if name.startswith("beta_h_"):
        return "market_hours_opp"
    if name.startswith("beta_occ_"):
        return "occupation_opp"
    if name.startswith("beta_w") or name == "sigma":
        return "wage_opp"
    return "other"


def run_reestimation(out_csv, out_json, report_md, theta_star, years, n_hh, timeout):
    """Invoke the certified step4 path on the staged stem, warm-started from theta_star.
    Returns (returncode, stdout_tail)."""
    cmd = [sys.executable, str(_STEP4),
           "--spec", str(_CERT_SPEC),
           "--engine-ready-stem", _STAGED_STEM,
           "--couples-stem", _STAGED_STEM,
           "--years", years,
           "--n-hh", str(n_hh),
           "--theta-star", str(theta_star),
           "--out-csv", str(out_csv),
           "--out-json", str(out_json),
           "--report", str(report_md)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    tail = (proc.stdout or "")[-3000:] + "\n--STDERR--\n" + (proc.stderr or "")[-1500:]
    return proc.returncode, tail


def compare_parameters(cert_csv, rebuilt_csv):
    """Per-parameter comparison: certified vs rebuilt value, delta, both clustered SEs,
    |delta|/cert_clustered_SE. Tabulated by super-block."""
    cert = pd.read_csv(cert_csv).set_index("parameter")
    reb = pd.read_csv(rebuilt_csv).set_index("parameter")
    rows = []
    for p in cert.index:
        if p not in reb.index:
            rows.append({"param": p, "missing_in_rebuilt": True})
            continue
        cv = float(cert.loc[p, "value"])
        rv = float(reb.loc[p, "value"])
        c_se = cert.loc[p, "se_clustered"]
        c_se = float(c_se) if pd.notna(c_se) else None
        r_se = reb.loc[p, "se_clustered"] if "se_clustered" in reb.columns else None
        r_se = float(r_se) if (r_se is not None and pd.notna(r_se)) else None
        delta = rv - cv
        ratio = (abs(delta) / c_se) if (c_se and c_se > 0) else None
        block = _classify_block(p)
        rows.append({
            "param": p, "block": block, "super_block": _BLOCK_TO_SUPER.get(block, "other"),
            "certified": cv, "rebuilt": rv, "delta": delta,
            "cert_clustered_se": c_se, "rebuilt_clustered_se": r_se,
            "abs_delta_over_cert_se": ratio,
            "within_band": (ratio is not None and ratio <= _BAND_SIGMA),
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", required=True, help="Three-B2 provenance JSON")
    ap.add_argument("--years", default="2015,2016,2017")
    ap.add_argument("--n-hh", type=int, default=0)
    ap.add_argument("--timeout", type=int, default=36000, help="re-estimation wall cap (s)")
    ap.add_argument("--skip-reestimation", action="store_true",
                    help="reuse an existing rebuilt CSV + step4 JSON (resumability)")
    args = ap.parse_args()

    rebuilt_csv = _REBUILT_THETA
    step4_json = Path("outputs/welfare/stage1_w3/stage3b2_step4_rebuilt.json")
    report_md = Path("outputs/welfare/stage1_w3/stage3b2_step4_report.md")

    # Hard guard: never overwrite the certified theta CSV.
    if rebuilt_csv.resolve() == _CERT_THETA.resolve():
        raise SystemExit("REFUSE: rebuilt theta CSV path equals the certified CSV.")

    reest_rc = None
    reest_tail = None
    if not args.skip_reestimation:
        reest_rc, reest_tail = run_reestimation(
            rebuilt_csv, step4_json, report_md, _CERT_THETA, args.years, args.n_hh,
            args.timeout)

    # Load step4 result diagnostics (Tasks 2-3 evidence)
    if not step4_json.exists():
        out = {"increment": "stage3b2_controlled_reestimation_v1",
               "verdict": "INCONCLUSIVE",
               "stop_reason": "step4 result JSON missing (re-estimation did not complete)",
               "reestimation_returncode": reest_rc, "reestimation_tail": reest_tail}
        Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out_json, "w") as f:
            json.dump(out, f, indent=2, default=float)
        print("[three-B2] INCONCLUSIVE: step4 JSON missing; STOP")
        return

    with open(step4_json) as f:
        R = json.load(f)

    # ---- Task 3 evidence first (Hessian PD is the real convergence evidence) ----
    hess = R.get("hessian", {})
    pd_ok = bool(hess.get("pd"))
    params = R.get("params", [])
    n_clu_se = sum(1 for r in params if r.get("se_clustered") is not None)
    n_params = len(params)
    se_ok = bool(pd_ok and n_params > 0 and n_clu_se == n_params)
    at_bound = R.get("at_bound", [])

    # ---- Task 2: convergence (explicit, no implied STRICT gradient convergence) ----
    diag = R.get("diagnostics", {})
    negLL = R.get("negLL")
    start_negLL = diag.get("start_negLL")
    final_max_grad = diag.get("final_max_grad", R.get("max_grad"))
    max_grad = R.get("max_grad")
    in_bounds = R.get("in_bounds")
    optimizer = R.get("optimizer")
    improvement = (float(start_negLL) - float(negLL)) if (start_negLL is not None
                                                          and negLL is not None) else None
    # We DO NOT claim strict gradient convergence: this BFGS family terminates at a stall-floor
    # gradient (step4: "the BFGS-family analogue of CONOPT RGmax"), the same for the certified
    # and staged fits. The convergence basis is: finite negLL, in bounds, NEGLIGIBLE objective
    # improvement from the certified warm start, and a PD Hessian at the solution. The final
    # gradient is REPORTED (not used as a strict pass/fail), matching the certified convention.
    finite_in_bounds = bool(in_bounds and negLL is not None and np.isfinite(negLL)
                            and (reest_rc in (0, None)))
    negligible_improvement = bool(improvement is not None and abs(improvement) < 1.0)
    numerically_settled = bool(finite_in_bounds and pd_ok and negligible_improvement)
    convergence_basis = (
        "finite/in-bounds negLL; negligible objective improvement from certified warm start "
        f"(dnegLL={improvement:.2e} nats); PD Hessian at the solution "
        f"(min_eig={hess.get('min_eig')}); certified-family BFGS stall-floor gradient "
        f"(final_max_grad={final_max_grad}) REPORTED, not used as strict gradient convergence."
        if improvement is not None else
        "finite/in-bounds negLL; PD Hessian; BFGS stall-floor gradient reported (no start "
        "negLL recorded).")
    # Keep `converged` as a back-compatible alias of the explicit determination.
    converged = numerically_settled

    # STOP conditions
    if not converged:
        verdict = "INCONCLUSIVE"
        stop_reason = ("re-estimation not numerically settled "
                       f"(finite_in_bounds={finite_in_bounds}, pd_hessian={pd_ok}, "
                       f"negligible_improvement={negligible_improvement}, "
                       f"improvement={improvement}, rc={reest_rc})")
    elif not se_ok:
        verdict = "INCONCLUSIVE"
        stop_reason = (f"Hessian PD={pd_ok}; clustered SE available for {n_clu_se}/{n_params} "
                       "params — cannot compute the A/B comparison")
    else:
        stop_reason = None
        # ---- Task 4: parameter comparison under the pre-registered criterion ----
        comp = compare_parameters(_CERT_THETA, rebuilt_csv)
        decomp = [r for r in comp if r.get("super_block") in _DECOMP_RELEVANT]
        outside = [r for r in decomp if r.get("within_band") is False
                   and r.get("abs_delta_over_cert_se") is not None]
        # ---- Task 5: verdict ----
        verdict = "REAL-DATA MATERIAL" if outside else "REAL-DATA IMMATERIAL"

    # assemble super-block summary (only if we ran the comparison)
    block_summary = None
    comp_rows = None
    worst = None
    if stop_reason is None:
        comp_rows = comp
        block_summary = {}
        for sb in sorted(set(_BLOCK_TO_SUPER.values())):
            sub = [r for r in comp if r.get("super_block") == sb]
            ratios = [r["abs_delta_over_cert_se"] for r in sub
                      if r.get("abs_delta_over_cert_se") is not None]
            block_summary[sb] = {
                "n_params": len(sub),
                "n_within_band": sum(1 for r in sub if r.get("within_band")),
                "n_outside_band": sum(1 for r in sub if r.get("within_band") is False
                                      and r.get("abs_delta_over_cert_se") is not None),
                "max_abs_delta_over_se": float(max(ratios)) if ratios else None,
                "median_abs_delta_over_se": float(np.median(ratios)) if ratios else None,
            }
        worst = sorted([r for r in comp if r.get("abs_delta_over_cert_se") is not None],
                       key=lambda r: -r["abs_delta_over_cert_se"])[:10]

    out = {
        "increment": "stage3b2_controlled_reestimation_v1",
        "no_synthetic_recovery": True, "computed_v_dir": False, "priced_redrawn_node": False,
        "promoted_w3": False, "promoted_to_canonical": False,
        "production_parquet_swapped_or_overwritten_or_moved_or_deleted": False,
        "overwrote_certified_theta": False,
        "measures_touched": ["W3_only"],
        "staged_stem": _STAGED_STEM, "certified_spec": str(_CERT_SPEC),
        "warm_start_from": str(_CERT_THETA),
        "rebuilt_theta_csv": str(rebuilt_csv),
        "band_sigma": _BAND_SIGMA,
        "reestimation_returncode": reest_rc,
        "task2_convergence": {
            "start_negLL_at_certified_theta": start_negLL,
            "final_negLL": negLL,
            "improvement_start_minus_final": improvement,
            "final_max_grad": final_max_grad,
            "max_grad_reported": max_grad,
            "optimizer": optimizer,
            "in_bounds": in_bounds, "out_of_bounds": R.get("out_of_bounds"),
            "numerically_settled": numerically_settled,
            "convergence_basis": convergence_basis,
            "gradient_note": (
                "final_max_grad is the BFGS-family stall-floor gradient (step4: 'the "
                "BFGS-family analogue of CONOPT RGmax'), the same convention as the certified "
                "fit; it is REPORTED, not used as a strict gradient-convergence pass/fail. "
                "Numerical settling is established by finite/in-bounds negLL + negligible "
                "objective improvement from the certified warm start + a PD Hessian."),
            "converged": converged,  # back-compat alias of numerically_settled
            "wall_seconds": R.get("diagnostics", {}).get("total_seconds"),
            "n_hh": R.get("n_hh"), "couples_alts": R.get("couples_alts"),
            "singles_alts": R.get("singles_alts"),
        },
        "task3_uncertainty": {
            "hessian_pd": pd_ok, "min_eig": hess.get("min_eig"), "cond": hess.get("cond"),
            "hessian_verdict": hess.get("verdict"),
            "clustered_se_available": f"{n_clu_se}/{n_params}",
            "cluster_key": R.get("cluster_key"),
            "cluster_source_key": "idorighh",
            "cluster_key_note": (
                "step4's self-describing `cluster_key` field falls back to the generic label "
                "'cluster' when the data object does not expose a name; the ACTUAL clustering "
                "is on idorighh (engine-ready sets cluster_id = idorighh), identical to the "
                "certified estimate. See cluster_summary for the cluster/group counts."),
            "cluster_summary": R.get("cluster_summary"),
            "params_at_bound": at_bound,
            "se_ok": se_ok,
        },
        "task4_parameter_comparison": {
            "band": f"|delta| <= {_BAND_SIGMA} * certified_clustered_SE",
            "super_block_summary": block_summary,
            "worst_10_by_abs_delta_over_cert_se": worst,
            "per_param": comp_rows,
        },
        "task5_verdict": {
            "real_data_verdict": verdict,
            "stop_reason": stop_reason,
            "is_final_AB_verdict": False,
            "note": "Real-data movement only. NOT the final A/B verdict — synthetic recovery "
                    "(Three-B3) on the staged reproducible baseline is still required.",
            "next_increment_if_clean": ("Three-B3: synthetic recovery on the staged "
                                        "reproducible baseline" if verdict.startswith(
                                            "REAL-DATA") else
                                        "resolve convergence/SE failure before proceeding"),
        },
        "scope_statement": (
            "Controlled real-data re-estimation only. No synthetic recovery, no V_i^dir, no "
            "redrawn pricing, no W^3 promotion, no production swap, no promotion to canonical, "
            "and the certified theta_hat CSV was NOT overwritten (rebuilt theta written to a "
            "new versioned artifact)."),
    }
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)

    print(f"[three-B2] re-estimation rc={reest_rc}")
    print(f"[three-B2] T2 numerically_settled={numerically_settled} "
          f"final_negLL={negLL} improvement={improvement} "
          f"final_max_grad={final_max_grad} (stall-floor, reported) optimizer={optimizer}")
    print(f"[three-B2] T3 Hessian PD={pd_ok} min_eig={hess.get('min_eig')} "
          f"clustered_SE={n_clu_se}/{n_params} se_ok={se_ok} at_bound={len(at_bound)}")
    if block_summary:
        for sb, d in block_summary.items():
            print(f"[three-B2] T4 {sb}: {d['n_within_band']}/{d['n_params']} within band, "
                  f"max|d|/SE={d['max_abs_delta_over_se']}")
    print(f"[three-B2] T5 VERDICT: {verdict}" + (f"  ({stop_reason})" if stop_reason else ""))
    print(f"[three-B2] wrote {args.out_json}")


if __name__ == "__main__":
    main()
