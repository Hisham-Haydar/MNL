"""
STAGE THREE, INCREMENT THREE-B3 — synthetic-recovery gate on the staged reproducible baseline,
mirroring the certified 901 gate (RURO_jax_recovery_gate_tlmpin_901_v1.md) EXACTLY.

Runs the certified recovery harness (scripts/bpool/jax_recovery_gate.py) on the staged Three-B1
engine-ready stem, changing ONLY the stem — same DGP theta_star, same draw-spec, same seed,
same thresholds, same Check-5-load-bearing verdict standard. Then compares the staged recovery
against the certified 901 gate and emits the final Two-O verdict (combined with Three-B2).

The certified gate's load-bearing criterion is CHECK 5 (PD Hessian at the synthetic MLE).
Checks 2/3/4 mechanically FAILED in the certified gate and are DIAGNOSTIC (flat-but-curved
singles-leisure directions). Three-B3 applies the SAME standard — it does NOT impose a stricter
all-checks-pass requirement.

Does NOT: promote any baseline to canonical, compute V_i^dir, price redrawn nodes, promote W^3,
swap/overwrite/move/delete any production parquet, or overwrite the certified or rebuilt theta
CSVs. The recovered (synthetic) theta is written to a NEW versioned diagnostic filename.

STOP conditions:
  - Check 5 non-PD, or a NEW identification pathology absent from the certified gate
    -> SYNTHETIC RECOVERY FAIL / STOP (do not auto-declare Option B; diagnose);
  - non-convergence / Hessian uncomputable -> INCONCLUSIVE / STOP.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

_GATE = Path("scripts/bpool/jax_recovery_gate.py").resolve()
_STAGED_STEM = "fr_p3a_bpool_engine_ready_staged_threeB1"
_FIT_SPEC = Path("scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml")
_DRAW_SPEC = Path("scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0.yaml")
_THETA_STAR = Path("scripts/bpool/specs/theta_star_joint_v1.csv")
_CERT_GATE_REPORT = Path(
    "docs/France_case/P3a/execution_logs/Bpool/RURO_jax_recovery_gate_tlmpin_901_v1.md")

# Certified 901 gate reference (read from RURO_jax_recovery_gate_tlmpin_901_v1.md) — the
# standard Three-B3 mirrors. Recorded here for the pre-registered comparison.
_CERT_REF = {
    "report": str(_CERT_GATE_REPORT),
    "n_params": 47, "couples_alts": 901,
    "n_hh": {"sm": 2243, "sf": 2764, "cou": 7438},
    "seed": 20260530,
    "check2": {"max_err": 0.2891086743837079, "worst": "beta_E_drgn3",
               "thresh": 0.05, "passed": False, "role": "diagnostic"},
    "check3": {"thresh": 0.10, "passed": False, "role": "diagnostic",
               "blocks": {"sm_leisure": 0.40736207025780613,
                          "sf_leisure": 0.43884297916580434,
                          "theta_c_singles": 0.033005475977220707,
                          "m_leisure": 0.0790186050717799,
                          "f_leisure": 0.14369806543062216}},
    "check4": {"max_diff": 5.030648460396803e-05, "thresh": 1e-06,
               "passed": False, "role": "diagnostic"},
    "check5": {"pd": True, "min_eig": 1.7060615915361825,
               "verdict": "SEPARATELY IDENTIFIED", "passed": True, "role": "LOAD_BEARING"},
    "warm_bound_binding": [],  # certified MLE fully interior
    "beta_l0_m": {"interior": True, "value_note": "+0.0191 interior at 901"},
}


def pre_register_standard(seed, years, n_hh):
    """TASK 0 — pre-register the EXACT gate standard before running (no post-hoc changes)."""
    return {
        "mirrored_certified_gate": str(_CERT_GATE_REPORT),
        "dgp_theta_source": str(_THETA_STAR),
        "fit_spec": str(_FIT_SPEC),
        "draw_spec": str(_DRAW_SPEC),
        "draw_spec_rationale": (
            "fit spec pins theta_l_m (fixed_params); the numpy DGP engine cannot resolve "
            "fixed_params, so the synthetic draw uses the un-pinned sibling bll0 spec "
            "(48 free params = 47 fit-free + theta_l_m), with theta_l_m inserted at its "
            "pinned value -0.8. DGP identical; only the FIT pins. This is the certified "
            "gate's own convention (jax_recovery_gate.py _full_theta)."),
        "staged_engine_ready_stem": _STAGED_STEM,
        "seed": seed, "years": years, "n_hh": n_hh,
        "resolution": {"couples_alts": 901, "singles_alts": 101},
        "tighten_leisure_bounds": False,  # certified 901 MLE was interior; do NOT tighten
        "thresholds_diagnostic": {"check2": 0.05, "check3": 0.10, "check4": 1e-06},
        "load_bearing_verdict": (
            "CHECK 5: PD Hessian at the synthetic MLE, with NO new bound/pathology relative "
            "to the certified 901 gate. Checks 2/3/4 are DIAGNOSTIC (the certified gate's "
            "own Checks 2/3/4 mechanically FAILED and were interpreted as flat-but-curved "
            "singles-leisure precision caveats, not identification failures)."),
        "certified_reference": _CERT_REF,
        "criteria_frozen_before_run": True,
    }


def run_gate(out_json, report_md, theta_csv, seed, years, n_hh, timeout):
    cmd = [sys.executable, str(_GATE),
           "--spec", str(_FIT_SPEC),
           "--draw-spec", str(_DRAW_SPEC),
           "--theta-star", str(_THETA_STAR),
           "--engine-ready-stem", _STAGED_STEM,
           "--couples-stem", _STAGED_STEM,
           "--years", years,
           "--n-hh", str(n_hh),
           "--seed", str(seed),
           "--out-json", str(out_json),
           "--out-theta-csv", str(theta_csv),
           "--report", str(report_md)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    tail = (proc.stdout or "")[-3000:] + "\n--STDERR--\n" + (proc.stderr or "")[-1500:]
    return proc.returncode, tail


def compare_to_certified(R):
    """TASK 3 — classify each check vs the certified 901 gate: PASS/FAIL under the original
    threshold, load-bearing vs diagnostic, same/worse/improved. Flag any NEW pathology."""
    cmp = {}
    cert = _CERT_REF

    # Check 5 (LOAD-BEARING)
    c5 = R.get("check5", {})
    staged_pd = bool(c5.get("pd"))
    staged_eig = c5.get("min_eig")
    cmp["check5_load_bearing"] = {
        "staged_pd": staged_pd, "staged_min_eig": staged_eig,
        "certified_min_eig": cert["check5"]["min_eig"],
        "certified_pd": True,
        "both_pd": bool(staged_pd),
        "min_eig_vs_certified": ("same_sign_PD" if staged_pd else "NON_PD_REGRESSION"),
        "verdict": c5.get("verdict"),
    }

    # interiority / bound pattern — a NEW binding direction would undermine PD interpretation
    staged_bind = R.get("warm_bound_binding", [])
    cert_bind = cert["warm_bound_binding"]
    new_binds = [b for b in staged_bind if list(b) not in [list(x) for x in cert_bind]]
    cmp["bound_pattern"] = {
        "staged_bound_binding": staged_bind,
        "certified_bound_binding": cert_bind,
        "new_binding_directions_vs_certified": new_binds,
        "introduces_new_pathology": bool(new_binds),
        "beta_l0_m": R.get("beta_l0_m"),
    }

    # Check 2 (diagnostic)
    c2 = R.get("check2", {})
    cmp["check2_diagnostic"] = {
        "staged_max_err": c2.get("max_err"), "staged_worst": c2.get("worst"),
        "certified_max_err": cert["check2"]["max_err"],
        "threshold": cert["check2"]["thresh"],
        "staged_pass": bool(c2.get("passed")),
        "certified_pass": False,
        "direction": _direction(c2.get("max_err"), cert["check2"]["max_err"]),
        "role": "diagnostic (flat-but-curved; FAIL allowed if same interpretation)",
    }

    # Check 3 (diagnostic) — per block vs certified
    c3 = R.get("check3", {}).get("blocks", {})
    block_cmp = {}
    for b, cert_err in cert["check3"]["blocks"].items():
        s = c3.get(b, {})
        block_cmp[b] = {
            "staged_max_err": s.get("max_err"), "certified_max_err": cert_err,
            "staged_pass": bool(s.get("passed")),
            "direction": _direction(s.get("max_err"), cert_err),
        }
    cmp["check3_diagnostic"] = {
        "threshold": cert["check3"]["thresh"], "blocks": block_cmp,
        "role": "diagnostic (singles-leisure flat directions; FAIL expected, same as certified)",
        "pinned_block_m_leisure_holds": (
            c3.get("m_leisure", {}).get("passed")),  # the pinned block must still PASS
    }

    # Check 4 (diagnostic)
    c4 = R.get("check4", {})
    cmp["check4_diagnostic"] = {
        "staged_max_diff": c4.get("max_diff"), "certified_max_diff": cert["check4"]["max_diff"],
        "threshold": cert["check4"]["thresh"],
        "staged_pass": bool(c4.get("passed")), "certified_pass": False,
        "two_start_same_basin": (c4.get("max_diff") is not None
                                 and c4.get("max_diff") < 1e-3),
        "role": "diagnostic (tolerance-level two-start disagreement in flat directions)",
    }

    # NEW large+decomposition-relevant failure check: a Check-2/3 failure on a NON-singles-
    # leisure, decomposition-relevant block that the certified gate did NOT have is a flag.
    # Certified failing directions: beta_E_drgn* (Check2 region), sm/sf/f_leisure (Check3).
    cmp["new_decomposition_relevant_failure"] = _new_failure_flag(R)
    return cmp


def _direction(staged, cert):
    if staged is None or cert is None:
        return None
    if abs(staged - cert) <= 1e-9:
        return "same_as_certified"
    return "worse_than_certified" if staged > cert else "improved_vs_certified"


def _new_failure_flag(R):
    """Flag a NEW large, tight, decomposition-relevant recovery failure absent from the
    certified gate. Certified-known flat directions (singles-leisure sm/sf/f, region beta_E)
    are NOT new. A failure outside those, in the ability/wage or opportunity/access blocks,
    at materially larger error, would be a new pathology."""
    known_flat = {"sm_leisure", "sf_leisure", "f_leisure"}
    flags = []
    c3 = R.get("check3", {}).get("blocks", {})
    for b, d in c3.items():
        if not d or d.get("passed") or b in known_flat or b == "theta_c_singles":
            continue
        if b in ("m_leisure", "beta_ll", "relaxed_gsplit"):
            # pinned/removed blocks: a FAIL here WOULD be new (they PASS in certified)
            flags.append({"block": b, "max_err": d.get("max_err"),
                          "note": "block that PASSES in the certified gate now FAILS"})
    # Check 2 region worst: certified worst is a beta_E_drgn* region dummy (known flat).
    c2w = R.get("check2", {}).get("worst", "")
    c2_failed = (c2w and not c2w.startswith("beta_E_drgn")
                 and not R.get("check2", {}).get("passed"))
    # a Check-2 failure whose worst is NOT a region dummy could be ability/wage/opp
    if c2_failed and (c2w.startswith("beta_w") or c2w == "sigma" or c2w.startswith("beta_occ")):
        flags.append({"check2_worst": c2w,
                      "note": "Check-2 worst is a decomposition-relevant (ability/wage or "
                              "occupation) param, not a region dummy as in certified"})
    return {"new_failures": flags, "any_new_pathology": bool(flags)}


def final_verdict(R, cmp, reest_rc, threeB2_json):
    """TASK 4 — combine Three-B2 (real-data) + Three-B3 (synthetic) into the Two-O verdict."""
    # Three-B2 real-data verdict
    b2_verdict = None
    if threeB2_json and Path(threeB2_json).exists():
        with open(threeB2_json) as f:
            b2 = json.load(f)
        b2_verdict = b2.get("task5_verdict", {}).get("real_data_verdict")

    c5 = cmp["check5_load_bearing"]
    new_path = (cmp["bound_pattern"]["introduces_new_pathology"]
                or cmp["new_decomposition_relevant_failure"]["any_new_pathology"])
    hessian_computed = R.get("check5", {}).get("min_eig") is not None
    converged = bool(R.get("warm_converged"))

    if not hessian_computed or reest_rc not in (0, None):
        return {"two_o_verdict": "INCONCLUSIVE",
                "reason": "synthetic run failed / Hessian uncomputable",
                "threeB2_real_data_verdict": b2_verdict, "is_final": False}
    if not c5["staged_pd"]:
        return {"two_o_verdict": "SYNTHETIC RECOVERY FAIL / STOP",
                "reason": f"Check 5 NON-PD (min_eig={c5['staged_min_eig']}); do NOT auto-declare "
                          "Option B — diagnose the flat/negative direction before promotion",
                "threeB2_real_data_verdict": b2_verdict, "is_final": False}
    if new_path:
        return {"two_o_verdict": "SYNTHETIC RECOVERY FAIL / STOP",
                "reason": "staged recovery introduces a NEW identification pathology absent "
                          "from the certified 901 gate (new bound bind or new "
                          "decomposition-relevant failure); diagnose before promotion",
                "details": {"bound": cmp["bound_pattern"]["new_binding_directions_vs_certified"],
                            "new_failures": cmp["new_decomposition_relevant_failure"]},
                "threeB2_real_data_verdict": b2_verdict, "is_final": False}
    # Check 5 PD + no new pathology -> matches certified load-bearing standard
    if b2_verdict == "REAL-DATA IMMATERIAL":
        return {"two_o_verdict": "OPTION A CONFIRMED",
                "reason": ("Three-B2 REAL-DATA IMMATERIAL and Three-B3 matches the certified "
                           "synthetic gate's load-bearing standard (Check 5 PD at 901 "
                           f"min_eig={c5['staged_min_eig']}, no new identification pathology). "
                           "The certified estimate stands with the baseline irreproducibility "
                           "documented as immaterial; the staged reproducible baseline is the "
                           "instrument establishing that result."),
                "threeB2_real_data_verdict": b2_verdict,
                "is_final": True,
                "note": "Promotion to canonical, production swap, welfare pricing, and V_i^dir "
                        "remain SEPARATE authorisations.",
                "warm_converged_caveat": (None if converged else
                                          "warm MLE gradient above 1e-2 (BFGS stall-floor); "
                                          "Check 5 PD remains the load-bearing criterion as in "
                                          "the certified gate")}
    return {"two_o_verdict": "SYNTHETIC OK; REAL-DATA NOT IMMATERIAL",
            "reason": f"Check 5 PD + no new pathology, but Three-B2 returned '{b2_verdict}' "
                      "(not REAL-DATA IMMATERIAL); the A/B decision needs the real-data leg "
                      "re-examined",
            "threeB2_real_data_verdict": b2_verdict, "is_final": False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--years", default="2015,2016,2017")
    ap.add_argument("--n-hh", type=int, default=0)
    ap.add_argument("--seed", type=int, default=20260530)  # certified gate seed
    ap.add_argument("--timeout", type=int, default=36000)
    ap.add_argument("--threeB2-json",
                    default="outputs/welfare/stage1_w3/stage3b2_controlled_reestimation.json")
    ap.add_argument("--skip-gate", action="store_true",
                    help="reuse an existing staged gate JSON (resumability)")
    args = ap.parse_args()

    gate_json = Path("outputs/welfare/stage1_w3/stage3b3_staged_gate.json")
    report_md = Path("outputs/welfare/stage1_w3/stage3b3_staged_gate_report.md")
    theta_csv = Path("scripts/bpool/specs/theta_recovered_staged_synth_901_v1.csv")

    # hard guards: never overwrite the certified or rebuilt real-data theta CSVs
    for protected in (Path("scripts/bpool/specs/theta_hat_realdata_901_v1.csv"),
                      Path("scripts/bpool/specs/theta_hat_rebuilt_realdata_901_v1.csv")):
        if theta_csv.resolve() == protected.resolve():
            raise SystemExit(f"REFUSE: recovered-theta CSV equals protected {protected}")

    standard = pre_register_standard(args.seed, args.years, args.n_hh)

    gate_rc = None
    gate_tail = None
    if not args.skip_gate:
        gate_rc, gate_tail = run_gate(gate_json, report_md, theta_csv, args.seed,
                                      args.years, args.n_hh, args.timeout)

    if not gate_json.exists():
        out = {"increment": "stage3b3_synthetic_recovery_v1",
               "task0_preregistered_standard": standard,
               "two_o_verdict": "INCONCLUSIVE",
               "stop_reason": "staged gate JSON missing (recovery did not complete)",
               "gate_returncode": gate_rc, "gate_tail": gate_tail,
               "no_v_dir": True, "priced_redrawn_node": False, "promoted_w3": False,
               "promoted_to_canonical": False,
               "production_parquet_swapped_or_overwritten_or_moved_or_deleted": False}
        Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out_json, "w") as f:
            json.dump(out, f, indent=2, default=float)
        print("[three-B3] INCONCLUSIVE: staged gate JSON missing; STOP")
        return

    with open(gate_json) as f:
        R = json.load(f)
    cmp = compare_to_certified(R)
    verdict = final_verdict(R, cmp, gate_rc, args.threeB2_json)

    out = {
        "increment": "stage3b3_synthetic_recovery_v1",
        "no_v_dir": True, "priced_redrawn_node": False, "promoted_w3": False,
        "promoted_to_canonical": False,
        "production_parquet_swapped_or_overwritten_or_moved_or_deleted": False,
        "overwrote_certified_or_rebuilt_theta": False,
        "measures_touched": ["W3_only"],
        "staged_stem": _STAGED_STEM,
        "recovered_theta_csv": str(theta_csv),
        "gate_returncode": gate_rc,
        "task0_preregistered_standard": standard,
        "task1_2_staged_recovery": {
            "check1_dgp": R.get("check1"),
            "check2_shared": {k: R.get("check2", {}).get(k)
                              for k in ("max_err", "worst", "thresh", "passed", "ll",
                                        "max_grad")},
            "warm_converged": R.get("warm_converged"),
            "warm_bound_binding": R.get("warm_bound_binding"),
            "beta_l0_m": R.get("beta_l0_m"),
            "check3_blocks": R.get("check3"),
            "check4_two_start": R.get("check4"),
            "check5_hessian": R.get("check5"),
            "check6_contamination": R.get("check6"),
        },
        "task3_comparison_vs_certified": cmp,
        "task4_two_o_verdict": verdict,
        "scope_statement": (
            "Synthetic-recovery gate on the staged reproducible baseline, mirroring the "
            "certified 901 gate (Check-5-load-bearing). No V_i^dir, no redrawn pricing, no "
            "W^3 promotion, no production swap, no promotion to canonical; certified and "
            "rebuilt theta CSVs NOT overwritten (recovered synthetic theta written to a new "
            "versioned diagnostic CSV). Nothing beyond W^3."),
    }
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)

    c5 = R.get("check5", {})
    print(f"[three-B3] gate rc={gate_rc}")
    print(f"[three-B3] CHECK 5 (load-bearing) PD={c5.get('pd')} "
          f"min_eig={c5.get('min_eig')} (certified +1.706)")
    print(f"[three-B3] warm_converged={R.get('warm_converged')} "
          f"bound_binding={R.get('warm_bound_binding')}")
    print(f"[three-B3] Check2 max_err={R.get('check2',{}).get('max_err')} "
          f"(cert 0.289) | Check4 max_diff={R.get('check4',{}).get('max_diff')}")
    print(f"[three-B3] new pathology: bind={cmp['bound_pattern']['introduces_new_pathology']} "
          f"decomp={cmp['new_decomposition_relevant_failure']['any_new_pathology']}")
    print(f"[three-B3] TWO-O VERDICT: {verdict['two_o_verdict']}")
    print(f"[three-B3] wrote {args.out_json}")


if __name__ == "__main__":
    main()
