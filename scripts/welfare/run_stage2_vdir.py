"""
Stage Two — Increment Two-A runner: V_i^dir feasibility re-audit + repair.
Storage-level template-availability audit + singles/couples redraw probes + the
EUROMOD reprice PARITY smoke + multiplier (node-growth) status. Reads the config.

Scope decision (fixed by the production ESS numbers): the singles cross-check is
DESIGNED to run on the FULL singles_male and singles_female samples (85-90% below
threshold -> flagged subset is nearly the whole; a blanket cross-check is cleaner
than a conditional one); couples on the genuine sub-threshold flag (median ESS ~63,
1285/7438 flagged). This runner records that designed scope and the per-group target
counts, then reports the storage-level template availability and the EUROMOD reprice
parity gate that must PASS before any redrawn node is priced.

Per the increment scope: this is a feasibility + parity smoke only. Production
|V_dir - V_IS| and the 2x/4x growth are DEFERRED to a separately-authorised run
(and are additionally BLOCKED while reprice parity does not pass). No W^3 welfare
finding is produced; no measure beyond W^3 is touched.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

_THIS = Path(__file__).resolve()
sys.path.insert(0, str(_THIS.parent))
import welfare_core as wc  # noqa: E402
import welfare_vdir as wv  # noqa: E402


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--seed", type=int, default=20260601)
    args = ap.parse_args()

    cfg = wc.load_config(args.config)
    spec = wc.load_spec(cfg)
    theta = wc.load_theta(cfg, spec)
    ess_thr = float(cfg["core"]["integration"]["ess_threshold"])

    R = {"increment": "stage2_vdir_crosscheck_v2", "spec": spec.name,
         "config": args.config, "ess_threshold": ess_thr,
         "scope_note": ("singles cross-check designed on FULL samples (85-90% below "
                        "ESS threshold); couples on sub-threshold flagged subset."),
         "no_welfare_finding": True, "measures_touched": ["W3_only"]}

    # ---- load production data, compute Stage-One welfare (V_i^IS, ESS) ----
    data = wc.load_data(cfg, n_hh=0)
    wc.assert_resolution(cfg, data)
    groups = cfg["unit"]["report_groups"]
    gws = {g: wc.compute_group_welfare(data[g], spec, theta, g) for g in groups}

    # ---- A. designed cross-check scope (targets) + EUROMOD-on-nodes boundary ----
    R["A_vdir_crosscheck"] = {}
    for g in groups:
        gw = gws[g]
        below = np.asarray(gw.ess) < ess_thr
        if g == "couples":
            target = "sub_threshold_flagged"
            n_target = int(np.sum(below))
        else:
            target = "full_sample"
            n_target = int(gw.n_groups)
        R["A_vdir_crosscheck"][g] = {
            "designed_target": target,
            "n_target_households": n_target,
            "n_groups_total": int(gw.n_groups),
            "n_below_ess_threshold": int(np.sum(below)),
        }

    cfg2 = cfg["stage2"]

    # ---- A1. RE-AUDIT: storage-level template availability (priced/precompute long)
    R["A_euromod_on_nodes"] = wv.euromod_on_nodes_status(cfg2)
    feasible = R["A_euromod_on_nodes"]["feasible_via_template_overwrite"]

    # ---- A2. redraw machinery: probe BOTH singles and couples node generation ----
    R["A_redraw_machinery"] = _probe_redraw(cfg, groups)

    # ---- A3. EUROMOD-on-nodes PARITY (Gate-0 analogue) — only if templates feasible
    eon = cfg2["euromod_on_nodes"]
    if feasible:
        R["A_euromod_parity"] = wv.euromod_reprice_parity(
            cfg2, year=int(eon["smoke_year"]), mode=str(eon["smoke_mode"]),
            n_hh=int(eon["smoke_n_hh"]), tol=float(eon["parity_tol"]))
    else:
        R["A_euromod_parity"] = {"status": "BLOCKED",
                                 "reason": "templates not feasible; parity not attempted"}

    parity_ok = (R["A_euromod_parity"].get("status") == "PASS")

    # ---- A4. status: V_dir values still NOT computed this increment ----
    # Per the prompt: if the bounded EUROMOD touch is FEASIBLE, stop after the smoke
    # feasibility report and wait for separate production-run authorisation. So even
    # when parity passes we do NOT compute production |V_dir - V_IS|.
    R["A_status"] = {
        "vdir_values_computed": False,
        "stop_reason": ("Increment Two-A is a feasibility + parity smoke only. The "
                        "bounded EUROMOD-on-nodes touch is "
                        + ("FEASIBLE and parity-VALIDATED" if (feasible and parity_ok)
                           else ("FEASIBLE but parity NOT passed" if feasible
                                 else "NOT feasible at storage level"))
                        + "; per the increment scope, production V_dir is deferred to "
                          "a separately-authorised run."),
        "blocked_or_deferred_households": {
            g: R["A_vdir_crosscheck"][g]["n_target_households"] for g in groups},
        "escalated_set": [],
        "escalation_note": ("escalation trigger is persistent |V_dir - V_IS| beyond "
                            "tolerance; no V_dir value is computed this increment, so "
                            "it cannot fire. No household escalated."),
    }

    # ---- B. multiplier stability ----
    fractions = [0.25, 0.5, 0.75, 1.0]
    R["B_multiplier_stability"] = {
        "configured_multipliers": cfg["core"]["integration"]["per_household_stability"]["draw_multipliers"],
        "full_2x_4x_status": ("DEFERRED" if feasible else "BLOCKED"),
        "full_2x_4x_reason": (
            "growing beyond the existing node count requires NEW nodes drawn from "
            "g_hat, whose consumption c_is needs EUROMOD-on-nodes. Re-audit (A) shows "
            "this is FEASIBLE via the priced-long template-overwrite path (no "
            "wholesale rebuild), so the full 2x/4x growth is DEFERRED to a "
            "separately-authorised production run alongside V_dir — it is welfare-"
            "integral node GROWTH, distinct from estimation-draw rebuilding."
            if feasible else
            "priced-long templates not feasible at storage level; node growth stays "
            "BLOCKED."),
        "existing_node_subsample_probe": {},
        "subsample_note": ("a WEAKER stability probe that needs NO new consumption: "
                           "subsample the EXISTING nodes at fractions and measure "
                           "V_i^IS drift as node count grows toward the full set. "
                           "Convergence here is necessary-not-sufficient for the full "
                           "draw-growth gate, which stays BLOCKED."),
    }
    for g in groups:
        sub = wv.node_subsample_stability(gws[g], theta, spec, data[g], g,
                                          fractions, np.random.default_rng(args.seed + 7))
        R["B_multiplier_stability"]["existing_node_subsample_probe"][g] = sub

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(R, f, indent=2, default=float)
    print(f"[stage2:vdir] wrote {args.out_json}")
    print(f"  templates feasible (priced/precompute long): {feasible}")
    print(f"  v1 wholesale-rebuild conclusion holds: "
          f"{R['A_euromod_on_nodes']['v1_wholesale_rebuild_conclusion_holds']}")
    print(f"  EUROMOD reprice parity: {R['A_euromod_parity'].get('status')} "
          f"(max_abs={R['A_euromod_parity'].get('max_abs_diff')})")
    print(f"  redraw machinery probe: {R['A_redraw_machinery']['status']}")
    print(f"  V_dir values computed: {R['A_status']['vdir_values_computed']} "
          f"(deferred HH: {R['A_status']['blocked_or_deferred_households']})")
    for g in groups:
        sub = R["B_multiplier_stability"]["existing_node_subsample_probe"][g]
        s100 = sub.get(0.75, {})
        print(f"  [{g}] node-subsample drift @0.75: max={s100.get('max_drift'):.2e} "
              f"median={s100.get('median_drift'):.2e}")


def _probe_redraw(cfg, groups):
    """Exercise the g_hat redraw to PROVE the machinery draws node LOCATIONS via the
    estimator's own functions — for BOTH singles and couples. Produces NO welfare
    value (consumption pricing is the separately-gated EUROMOD touch). Agnostic:
    stems from config; year_tag READ FROM THE DATA ROW (the build's own convention),
    not a hardcoded year map."""
    try:
        dm = wv._load_draw_machinery()
        mincer = dm["load_mincer"]()
    except Exception as e:
        return {"status": "DRAW_MACHINERY_IMPORT_FAILED", "error": f"{type(e).__name__}: {e}"}

    import pandas as pd
    from _bpool_paths import bpool_dir
    stem = cfg["baseline"]["engine_ready_stem"]
    probe = {}

    # singles legs
    sdf = pd.read_parquet(bpool_dir() / f"{stem}__singles.parquet")
    for g in ("singles_male", "singles_female"):
        if g not in groups:
            continue
        sex = 1.0 if g == "singles_male" else 0.0
        df = sdf[(sdf["dgn"] == sex) & (sdf["draw"] == 0)].head(3)
        nodes_drawn = 0
        for _, r in df.iterrows():
            yt = int(r["year_tag"])                         # READ from data, not mapped
            nd = wv.redraw_nodes_singles(r.to_dict(), 50, np.random.default_rng(1), mincer, dm, year_tag=yt)
            nodes_drawn += int(len(nd["hours"]))
        probe[g] = {"machinery": "BUILT", "households_probed": int(len(df)),
                    "nodes_drawn": nodes_drawn,
                    "consumption_priced": False}

    # couples leg — JOINT two-partner node generation. The couples engine-ready data
    # is WIDE: per-partner covariates are _male/_female-suffixed (educL_male, ...);
    # extract a singles-like covariate dict per partner by stripping the suffix.
    if "couples" in groups:
        cstem = cfg["baseline"]["couples_stem"]
        need = ["educL", "educH", "educ3", "pexp_years", "pexp_years2"]
        try:
            cdf = pd.read_parquet(bpool_dir() / f"{cstem}__couples.parquet")
            hh = cdf["stacked_hh_uid"].drop_duplicates().head(2)
            nodes_drawn = 0
            n_hh = 0
            for uid in hh:
                row = cdf[cdf["stacked_hh_uid"] == uid].iloc[0]
                yt = int(row["year_tag"])
                m = {k: row[f"{k}_male"] for k in need if f"{k}_male" in cdf.columns}
                f = {k: row[f"{k}_female"] for k in need if f"{k}_female" in cdf.columns}
                m["dgn"] = 1
                f["dgn"] = 0
                if not m or not f:
                    continue
                nd = wv.redraw_nodes_couples({"male": m, "female": f}, 30,
                                             np.random.default_rng(2), mincer, dm, year_tag=yt)
                nodes_drawn += int(len(nd["male"]["hours"]) + len(nd["female"]["hours"]))
                n_hh += 1
            probe["couples"] = {"machinery": "BUILT", "households_probed": n_hh,
                                "nodes_drawn_per_partner_summed": nodes_drawn,
                                "consumption_priced": False,
                                "note": ("joint two-partner node locations generated "
                                         "via the estimator channel structure (per-"
                                         "partner _male/_female covariates); joint "
                                         "EUROMOD pricing of both partners' overwritten "
                                         "choices shares the singles parity gate.")}
        except Exception as e:
            probe["couples"] = {"machinery": "BLOCKED",
                                "reason": f"couples node probe failed: {type(e).__name__}: {e}"}

    return {"status": "ok_locations_only_consumption_pricing_separately_gated",
            "per_group": probe,
            "note": ("g_hat redraw draws (w,h,occ,emp) via the estimator's own "
                     "functions for singles AND couples; consumption pricing at these "
                     "nodes is the bounded EUROMOD touch, gated on the reprice "
                     "parity check.")}


if __name__ == "__main__":
    main()
