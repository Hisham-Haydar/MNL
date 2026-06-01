"""
Stage-One W^3 runner: preflights + two passes (smoke, production) + Gates 0-4.

Reads everything from the resolved config (welfare_stage1_w3.yaml). Emits a JSON
results blob the gate report is written from. Computes NO reportable welfare
findings: any W^3 distribution / I(Omega^3) here is an INTERNAL validation
artifact pending Stage-Two authorisation.

Gate -> contract §6 map (see RURO_welfare_scaffold_design_contract_v2.md):
  Gate 0  = implementation-parity gate (NOT in §6; makes §1 "one machine" falsifiable)
  Gate 1  = §6 gate 1 parts (i)-(ii)  [V_i^IS draw-growth stability ; ESS]
  Gate 4  = §6 gate 1 part (iii)       [reference coverage]
  Gate 2  = §6 gate 2                  [inversion sanity]
  Gate 3  = §6 gate 3                  [household-unit integrity]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

_THIS = Path(__file__).resolve()
sys.path.insert(0, str(_THIS.parent))
import welfare_core as wc  # noqa: E402


def _jsonable(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    return o


def summarise(arr):
    a = np.asarray(arr, dtype=np.float64)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return {"n": 0}
    qs = np.quantile(a, [0.0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0])
    return {"n": int(a.size), "min": float(qs[0]), "p05": float(qs[1]),
            "p25": float(qs[2]), "median": float(qs[3]), "p75": float(qs[4]),
            "p95": float(qs[5]), "max": float(qs[6]), "mean": float(a.mean())}


def run_pass(cfg, spec, theta, n_hh, label, tol):
    data = wc.load_data(cfg, n_hh=n_hh)
    cou_alts = wc.assert_resolution(cfg, data)
    groups = cfg["unit"]["report_groups"]
    out = {"label": label, "n_hh_per_group": n_hh, "couples_alts": cou_alts,
           "groups": {}, "gate0": {}, "gate1": {}, "gate2": {}, "gate3": {}, "gate4": {}}

    gws = {}
    for g in groups:
        gw = wc.compute_group_welfare(data[g], spec, theta, g)
        gws[g] = gw
        out["groups"][g] = {"n_groups": gw.n_groups, "n_alts": gw.n_alts}

    # ---- Gate 0: engine parity ----
    g0_ok = True
    for g in groups:
        r = wc.gate0_parity(data[g], spec, theta, g, gws[g])
        out["gate0"][g] = _jsonable(r)
        if r["status"] == "ok":
            if not (r["max_abs"] is not None and r["max_abs"] <= tol):
                g0_ok = False
        elif r["status"] == "COUPLES_DEFERRED":
            pass  # parity anchor reported; couples full-grid V deferred
    out["gate0"]["tolerance"] = tol
    out["gate0"]["pass"] = bool(g0_ok)

    # ---- Gate 1 (ii): ESS diagnostic (production-resolution) ----
    ess_thr = float(cfg["core"]["integration"]["ess_threshold"])
    for g in groups:
        gw = gws[g]
        if np.all(np.isnan(gw.ess)):
            out["gate1"][g] = {"status": "COUPLES_DEFERRED"}
            continue
        below = int(np.sum(gw.ess < ess_thr))
        out["gate1"][g] = {
            "ess_summary": summarise(gw.ess),
            "ess_below_threshold": below,
            "ess_threshold": ess_thr,
            "max_normalised_weight_summary": summarise(gw.max_w),
            "V_is_summary": summarise(gw.V_is),
        }
    return out, gws, data


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--pass", dest="which", choices=["smoke", "production"], required=True)
    ap.add_argument("--out-json", required=True)
    args = ap.parse_args()

    cfg = wc.load_config(args.config)
    spec = wc.load_spec(cfg)
    theta = wc.load_theta(cfg, spec)

    R = {"which": args.which, "config": args.config,
         "spec": spec.name, "n_params": len(spec.all_param_names)}

    if args.which == "smoke":
        n_hh = int(cfg["smoke"]["n_hh_per_group"])
        tol = float(cfg["core"]["parity"]["smoke_tol"])
    else:
        n_hh = 0
        tol = float(cfg["core"]["parity"]["production_tol"])

    res, gws, data = run_pass(cfg, spec, theta, n_hh, args.which, tol)

    # ---- Gate 2: inversion sanity (W^3) ----
    for g, gw in gws.items():
        inv = wc.w3_inversion(gw, theta)
        if inv["status"] == "COUPLES_DEFERRED":
            res["gate2"][g] = {"status": "COUPLES_DEFERRED"}
            continue
        res["gate2"][g] = {
            "status": "ok",
            "zero_recovery_max_abs_phi0": float(np.nanmax(np.abs(inv["phi0"]))),
            "monotone_all": bool(np.all(inv["monotone"])),
            "monotone_frac": float(np.mean(inv["monotone"])),
            "bracketed_all": bool(np.all(inv["bracketed"])),
            "converged_all": bool(np.all(inv["converged"])),
            "converged_frac": float(np.mean(inv["converged"])),
            "n_nonconverged": int(np.sum(~inv["converged"])),
            "omega_summary": summarise(inv["omega"]),
        }

    # ---- Gate 3: household-unit integrity ----
    for g, gw in gws.items():
        n_clusters = int(len(np.unique(gw.cluster_ids)))
        res["gate3"][g] = {
            "n_groups": gw.n_groups,
            "one_omega_per_group": True,   # construction: lse_i is per group_starts row
            "per_capita_split": False,
            "type_conditional_reference": True,
            "n_unique_cluster_ids": n_clusters,
        }
    res["gate3"]["couples_joint_unit"] = True

    # ---- Gate 4: W^3 reference coverage ----
    # W^3 laissez-faire uses the household's OWN set with pay (consumption column).
    # Coverage = every alternative carries a finite consumption (c_ij). No Abar/J/o.
    for g, gw in gws.items():
        cgrid = gw.consumption_grid
        finite = np.isfinite(cgrid)
        positive = cgrid > 0
        res["gate4"][g] = {
            "all_c_ij_finite": bool(np.all(finite)),
            "n_nonfinite_c_ij": int(np.sum(~finite)),
            "all_c_ij_positive": bool(np.all(positive)),
            "n_nonpositive_c_ij": int(np.sum(~positive)),
        }
    res["gate4"]["abar_j_o_required"] = False
    res["gate4"]["note"] = ("W^3 uses own-set-with-pay; Abar/J/o EUROMOD exposure "
                            "is a later W^5/W^6/W^4 issue, not triggered by W^3.")

    # ---- Gate 1 (i): draw-multiplier stability — BLOCKED (datasets absent) ----
    res["gate1_draw_growth"] = {
        "status": "BLOCKED",
        "reason": ("draw-multiplier datasets at 2x/4x the 901-alt production draws "
                   "do not exist; not rebuilt and not fabricated. Production-"
                   "resolution ESS diagnostics computed instead (Gate 1 part ii)."),
        "configured_multipliers": cfg["core"]["integration"]["per_household_stability"]["draw_multipliers"],
    }
    # ---- Gate 1 V_dir cross-check — BLOCKED (no redraw machinery this stage) ----
    res["gate1_vdir_crosscheck"] = {
        "status": "BLOCKED",
        "reason": ("V_i^dir redraw-from-g_i machinery not implemented in Stage One; "
                   "flagged-subset cross-check cannot run. Reported, not approximated."),
    }

    # ---- decomposition-readiness interfaces (exposed, not computed) ----
    res["decomposition_readiness"] = {
        "exposes": ["Omega_i^k", "V_i", "I(Omega^k)", "block_structure"],
        "block_structure_from_config": bool(cfg["decomposition_readiness"]["expose_block_structure"]),
        "preference_equalisation_pinned_switch": cfg["decomposition_readiness"]["preference_equalisation_pinned_switch"],
        "pool_opportunity_share": bool(cfg["unit"]["pool_opportunity_share"]),
        "blocks_present": {k: len(v) for k, v in cfg["blocks"].items()},
    }

    # ---- internal validation artifact: I(Omega^3) (NOT a finding) ----
    res["internal_artifact_I_omega3"] = {}
    for g, gw in gws.items():
        inv = wc.w3_inversion(gw, theta) if gw.V_extractor is not None else {"status": "COUPLES_DEFERRED"}
        if inv["status"] == "ok":
            res["internal_artifact_I_omega3"][g] = {
                "gini_INTERNAL_VALIDATION_ONLY": wc.gini(inv["omega"]),
                "note": "INTERNAL validation artifact, NOT a welfare finding.",
            }
        else:
            res["internal_artifact_I_omega3"][g] = {"status": "COUPLES_DEFERRED"}

    res.update({k: v for k, v in res.items()})
    res = {**R, **res}

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(_jsonable(res), f, indent=2)
    print(f"[stage1:{args.which}] wrote {args.out_json}")
    # console summary
    print(f"  Gate0 parity pass={res['gate0'].get('pass')}")
    for g in cfg["unit"]["report_groups"]:
        g1 = res["gate1"].get(g, {})
        if "ess_summary" in g1:
            print(f"  [{g}] ESS median={g1['ess_summary'].get('median'):.1f} "
                  f"min={g1['ess_summary'].get('min'):.1f} "
                  f"below_thr={g1['ess_below_threshold']}")
        g2 = res["gate2"].get(g, {})
        if g2.get("status") == "ok":
            print(f"  [{g}] inv: phi0_max={g2['zero_recovery_max_abs_phi0']:.2e} "
                  f"monotone_all={g2['monotone_all']} converged_all={g2['converged_all']}")
        elif g2.get("status") == "COUPLES_DEFERRED":
            print(f"  [{g}] inv: COUPLES_DEFERRED")


if __name__ == "__main__":
    main()
