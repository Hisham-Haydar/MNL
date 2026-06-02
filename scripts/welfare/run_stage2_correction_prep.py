"""
Stage Two — Increment Two-H orchestrator: Task 1 (singleton-residual bound),
Task 2 (couples model-fit), GATE, Task 3 (draw_joint=0 correction-candidate side
artifact, gate-conditional), Task 4 (correction diagnostics).

Audit-only. No re-estimation, no V_i^dir, no redrawn pricing, no build-parquet overwrite.
The Task-3 side artifact is a NEW file, not authorised as estimator input until reviewed.

Run modes (--tasks): "12" (Tasks 1-2 + gate only), "all" (1-2, gate, 3-4 if gate passes).
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import welfare_assessment_unit_diag as wd  # noqa: E402
import welfare_core as wc  # noqa: E402
import welfare_correction_prep as cp  # noqa: E402


# ===========================================================================
# Task 1 — singleton-residual prevalence bound
# ===========================================================================
def task1_singleton_residual(cfg2, bc, base, *, cpcfg, components, tol, cov):
    sr = cpcfg["singleton_residual"]
    n_hh = int(sr["n_hh_per_year"])
    dj_samples = list(sr["draw_joint_samples"])
    per_node_all = []
    fd_logs = []
    blocked_all = []
    for year in cpcfg["years"]:
        pl, _ = wd._load(base, cfg2["precompute_long_stem"], year, "couples", long_=True)
        priced, _ = wd._load(base, cfg2["priced_long_stem"], year, "couples", long_=False)
        nalts = cp.block_distinct_alts(pl)
        plw = pl.copy()
        plw["__nalts"] = nalts
        hh_list = (plw["stacked_hh_uid"].drop_duplicates().sort_values().head(n_hh).tolist())
        # batch PER draw_joint (resilient to one-bad-node aborts) over genuinely singleton
        # blocks (nalts==1) for the deterministic first-n_hh households.
        for dj in dj_samples:
            sel = plw[(plw["stacked_hh_uid"].isin(hh_list))
                      & (plw["draw_joint"] == dj) & (plw["__nalts"] == 1)].copy()
            if len(sel) == 0:
                continue
            recs, tud, blocked = cp.resilient_reprice(
                bc, sel, year=year, components=components, tol=tol, priced=priced,
                country_override=cov)
            for r in recs:
                r["year"] = year
                r["cross_decider"] = cp.cross_decider_benefit_signature(r)
            per_node_all.extend(recs)
            for b in blocked:
                b["year"] = year
            blocked_all.extend(blocked)
            fd_logs.append((year, dj, tud, len(blocked)))

    # summarise
    valid = [r for r in per_node_all if r.get("status") in ("PASS", "FAIL")]
    n = len(valid)
    n_fail = sum(1 for r in valid if r["status"] == "FAIL")
    by_year = {}
    for yr in cpcfg["years"]:
        vy = [r for r in valid if r.get("year") == yr]
        by_year[int(yr)] = {"n": len(vy),
                            "n_fail": sum(1 for r in vy if r["status"] == "FAIL"),
                            "fail_rate": (sum(1 for r in vy if r["status"] == "FAIL") / len(vy)) if vy else None}
    # component localisation + |diff| dist (joint dispy) + cross-decider hits
    jd = np.array([r["joint_dispy_nominal"]["abs_diff"] for r in valid
                   if "joint_dispy_nominal" in r], dtype=float)
    loc = {}
    for r in valid:
        if r["status"] == "FAIL" and r.get("localised_to"):
            loc[r["localised_to"]] = loc.get(r["localised_to"], 0) + 1
    cdx = [r["cross_decider"] for r in valid if r.get("cross_decider")]
    cd_partner_hits = sum(1 for c in cdx
                          if c.get("gap_approximates_partner_stored_ils_ben")
                          or c.get("gap_approximates_partner_clean_ils_ben"))

    def _d(a):
        a = a[np.isfinite(a)]
        if not len(a):
            return {}
        qs = [0.0, 0.5, 0.9, 0.99, 1.0]
        return {"n": int(len(a)), "mean": float(a.mean()), "median": float(np.median(a)),
                "max": float(a.max()), "quantiles": {str(q): float(np.quantile(a, q)) for q in qs}}

    fail_rate = (n_fail / n) if n else None
    if fail_rate is None:
        verdict = "no_sample"
    elif fail_rate < 0.02:
        verdict = "negligible"
    elif fail_rate < 0.30:
        verdict = "non_negligible"
    else:
        verdict = "unresolved_large"
    return {
        "n_singleton_nodes": n, "n_fail": n_fail, "residual_fail_rate": fail_rate,
        "n_blocked_nodes": len(blocked_all),
        "blocked_samples": blocked_all[:10],
        "by_year": by_year,
        "component_localisation": loc,
        "joint_dispy_abs_diff_distribution": _d(jd),
        "cross_decider": {"n_fail_with_two_deciders": len(cdx),
                          "n_gap_approximates_partner_benefit": cd_partner_hits,
                          "share": (cd_partner_hits / len(cdx)) if cdx else None,
                          "samples": cdx[:5]},
        "per_drawjoint_batches": [{"year": y, "draw_joint": dj, "tudef": t, "n_blocked": nb}
                                  for (y, dj, t, nb) in fd_logs],
        "verdict": verdict,
    }


# ===========================================================================
# Task 2 — couples model fit at theta_hat
# ===========================================================================
def task2_model_fit(cfg, cpcfg):
    import jax.numpy as jnp
    import welfare_couples_contamination_audit as au
    spec = wc.load_spec(cfg)
    theta = wc.load_theta(cfg, spec)
    data = wc.load_data(cfg, n_hh=0)
    wc.assert_resolution(cfg, data)
    cou = data["couples"]
    n_groups = int(cou.n_groups)
    n_alts = int(cou.n_obs // cou.n_groups)

    ordered = au._reproduce_engine_order(cfg["baseline"])
    cons = np.maximum(np.asarray(cou.consumption, dtype=np.float64), 1e-12)
    if float(np.nanmax(np.abs(cons - np.maximum(ordered["c_norm"].to_numpy(np.float64), 1e-12)))) > 1e-9:
        return {"status": "mapping_ambiguous", "reason": "alignment failed"}

    Vfn, _ = wc._build_V_extractor_couples(cou, spec)
    V = np.asarray(Vfn(jnp.asarray(theta), jnp.asarray(cons))).reshape(n_groups, n_alts)
    mx = V.max(axis=1, keepdims=True)
    w = np.exp(V - mx)
    w = w / w.sum(axis=1, keepdims=True)
    chosen = (ordered["is_chosen_joint"].to_numpy() == 1).reshape(n_groups, n_alts)
    chosen_pos = chosen.argmax(axis=1)
    gi = np.arange(n_groups)
    P_chosen = w[gi, chosen_pos]
    # rank of chosen within its set (1 = best). rank = #alts with strictly higher V + 1
    Vc = V[gi, chosen_pos][:, None]
    rank = (Vc < V).sum(axis=1) + 1
    pct_rank = 1.0 - (rank - 1) / n_alts        # 1.0 = best, ~0 = worst
    tf = list(cpcfg["model_fit"]["top_fractions"])
    uni = 1.0 / float(cpcfg["model_fit"]["uniform_benchmark_alts"])

    def _q(a):
        qs = [0.0, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0]
        return {str(q): float(np.quantile(a, q)) for q in qs}
    return {
        "status": "ok", "n_households": n_groups, "n_alts": n_alts,
        "uniform_benchmark": uni,
        "P_chosen": {"mean": float(P_chosen.mean()), "median": float(np.median(P_chosen)),
                     "min": float(P_chosen.min()), "max": float(P_chosen.max()),
                     "quantiles": _q(P_chosen),
                     "share_below_uniform": float(np.mean(P_chosen < uni))},
        "chosen_rank": {"mean": float(rank.mean()), "median": float(np.median(rank)),
                        "min": int(rank.min()), "max": int(rank.max()),
                        "quantiles": {k: float(v) for k, v in _q(rank.astype(float)).items()}},
        "chosen_percentile_rank": {"mean": float(pct_rank.mean()),
                                   "median": float(np.median(pct_rank)),
                                   "quantiles": _q(pct_rank)},
        "share_in_top": {str(f): float(np.mean(rank <= max(1, int(np.ceil(f * n_alts)))))
                         for f in tf},
        "share_bottom_half": float(np.mean(pct_rank < 0.5)),
        "interpretation": (
            "P_chosen is read together with chosen_rank: near-zero absolute P_chosen with "
            "GOOD rank (chosen near the top of the 901-alt set) indicates GRID FINENESS "
            "(mass spread thinly over many near-equivalent alternatives); near-zero "
            "P_chosen with POOR rank indicates genuine MISFIT. Reported, not overclaimed."),
    }


# ===========================================================================
# Task 3 — correction-candidate side artifact (gate-conditional)
# ===========================================================================
def task3_correction_candidate(cfg2, bc, base, out_dir, *, cpcfg, components, tol, cov):
    """Reprice, collision-free batched, the TWO draw_joint=0 alternatives (chosen (0,0,0)
    + first-sim-cell sharing draw_joint=0) for ALL couples, each year. Write a NEW side
    parquet with full node keys, stored vs clean consumption + components, TUDef, metadata.
    Returns diagnostics. Writes NO build/storage parquet."""
    rows_out = []
    blocked = []
    coverage = {}
    for year in cpcfg["years"]:
        system_code = bc["system_pairing"][year][0]
        pl, _ = wd._load(base, cfg2["precompute_long_stem"], year, "couples", long_=True)
        priced, _ = wd._load(base, cfg2["priced_long_stem"], year, "couples", long_=False)
        dj0 = pl[pl["draw_joint"] == 0].copy()                # both alts of the collision block
        n_hh_year = int(dj0["stacked_hh_uid"].nunique())
        recs, warn, err = cp.batched_collisionfree_reprice(
            bc, dj0, year=year, components=components, tol=tol, priced=priced,
            country_override=cov)
        if err is not None:
            blocked.append({"year": year, "reason": err, "n_hh": n_hh_year})
            coverage[int(year)] = {"n_hh": n_hh_year, "n_nodes_repriced": 0}
            continue
        # stored joint ils_dispy_real for c_norm-equivalent reporting needs CPI
        phi = float(bc["cpi"][year]) if "cpi" in bc else 1.0
        for r in recs:
            if r.get("status") == "BLOCKED":
                blocked.append({"year": year, "node": r["node"], "reason": r.get("reason")})
                continue
            nd = r["node"]
            is_chosen = (nd["draw_male"] == 0 and nd["draw_female"] == 0)
            jd = r["joint_dispy_nominal"]
            rows_out.append({
                "data_year": int(year), "system_code": system_code,
                "stacked_hh_uid": int(nd["stacked_hh_uid"]),
                "draw_joint": int(nd["draw_joint"]), "draw_male": int(nd["draw_male"]),
                "draw_female": int(nd["draw_female"]),
                "node_type": "chosen" if is_chosen else "first_sim_cell",
                "stored_joint_ils_dispy_nominal": jd["stored"],
                "clean_joint_ils_dispy_nominal": jd["clean"],
                "abs_diff_joint_ils_dispy_nominal": jd["abs_diff"],
                "stored_joint_ils_dispy_real": jd["stored"] * phi,
                "clean_joint_ils_dispy_real": jd["clean"] * phi,
                "cpi_phi": phi,
                "ils_ben_max_abs": r["components"].get("ils_ben", {}).get("max_abs", 0.0),
                "ils_tax_max_abs": r["components"].get("ils_tax", {}).get("max_abs", 0.0),
                "ils_origy_max_abs": r["components"].get("ils_origy", {}).get("max_abs", 0.0),
                "ils_sicdy_max_abs": r["components"].get("ils_sicdy", {}).get("max_abs", 0.0),
                "status": r["status"], "localised_to": r.get("localised_to"),
                "tudef_batch": int(warn["n_warning_lines"]) if isinstance(warn, dict) else None,
            })
        coverage[int(year)] = {"n_hh": n_hh_year,
                               "n_nodes_repriced": sum(1 for r in recs if r.get("status") != "BLOCKED")}
    art = pd.DataFrame(rows_out)
    art_path = out_dir / cpcfg["correction_candidate"]["side_artifact_name"]
    if len(art):
        art.to_parquet(art_path, index=False)
    return {"side_artifact": str(art_path), "n_rows": int(len(art)),
            "coverage": coverage, "blocked": blocked, "artifact_df": art}


def task4_diagnostics(cfg2, bc, base, art, *, cpcfg, components, tol, cov):
    """Correction-candidate diagnostics + singleton-control guard."""
    if art is None or not len(art):
        return {"status": "no_artifact"}

    def _dist(a):
        a = np.asarray(a, float)
        a = a[np.isfinite(a)]
        if not len(a):
            return {}
        return {"n": int(len(a)), "median": float(np.median(a)), "mean": float(a.mean()),
                "max": float(a.max()),
                "quantiles": {q: float(np.quantile(a, float(q)))
                              for q in ["0.5", "0.9", "0.99", "1.0"]}}
    out = {"coverage_total_nodes": int(len(art)),
           "n_chosen": int((art["node_type"] == "chosen").sum()),
           "n_first_sim_cell": int((art["node_type"] == "first_sim_cell").sum())}
    for nt in ["chosen", "first_sim_cell"]:
        sub = art[art["node_type"] == nt]
        out[nt] = {
            "n": int(len(sub)),
            "fail_rate": float((sub["status"] == "FAIL").mean()) if len(sub) else None,
            "abs_diff_joint_dispy": _dist(sub["abs_diff_joint_ils_dispy_nominal"]),
            "localisation": sub.loc[sub["status"] == "FAIL", "localised_to"].value_counts().to_dict(),
            "income_machine_zero": {"ils_origy_max": float(sub["ils_origy_max_abs"].max()),
                                    "ils_sicdy_max": float(sub["ils_sicdy_max_abs"].max())},
        }

    # singleton-control guard: reprice 1 singleton node/HH for a subset of the SAME
    # households the correction touched (first n_hh by uid per year) and confirm the
    # correction process leaves unrelated nodes intact (PASS expected, modulo the Task-1
    # residual baseline).
    guard = {}
    n_guard = 100
    for year in cpcfg["years"]:
        pl, _ = wd._load(base, cfg2["precompute_long_stem"], year, "couples", long_=True)
        priced, _ = wd._load(base, cfg2["priced_long_stem"], year, "couples", long_=False)
        nalts = cp.block_distinct_alts(pl)
        plw = pl.copy()
        plw["__nalts"] = nalts
        hh_list = plw["stacked_hh_uid"].drop_duplicates().sort_values().head(n_guard).tolist()
        # one singleton node per HH (draw_joint=1, the first singleton)
        sel = plw[(plw["stacked_hh_uid"].isin(hh_list)) & (plw["draw_joint"] == 1)
                  & (plw["__nalts"] == 1)].copy()
        recs, tud, blocked = cp.resilient_reprice(
            bc, sel, year=year, components=components, tol=tol, priced=priced,
            country_override=cov)
        valid = [r for r in recs if r.get("status") in ("PASS", "FAIL")]
        guard[int(year)] = {"n": len(valid), "n_blocked": len(blocked),
                            "n_pass": sum(1 for r in valid if r["status"] == "PASS"),
                            "n_fail": sum(1 for r in valid if r["status"] == "FAIL"),
                            "tudef": int(tud)}
    out["singleton_control_guard"] = guard
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--tasks", default="all", choices=["12", "all"])
    args = ap.parse_args()

    cfg = wc.load_config(args.config)
    cfg2 = cfg["stage2"]
    cpcfg = cfg2["correction_prep"]
    components = list(cpcfg["components"])
    tol = float(cpcfg["tol"])
    cov = cpcfg.get("country_override")
    bc = wd.build_constants(cfg2["build_module"])
    # attach CPI for real-consumption reporting (read from build module, not hardcoded)
    import importlib
    bc["cpi"] = importlib.import_module(cfg2["build_module"])._CPI
    from _bpool_paths import bpool_dir
    base = bpool_dir()
    out_dir = Path(args.out_json).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    em_log = Path(args.out_json).with_name("stage2_correction_prep_euromod_console.log")
    _tmp = tempfile.TemporaryFile(mode="w+b")  # noqa: SIM115 (manual fd lifecycle)
    _so, _se = os.dup(1), os.dup(2)
    os.dup2(_tmp.fileno(), 1)
    os.dup2(_tmp.fileno(), 2)
    try:
        t1 = task1_singleton_residual(cfg2, bc, base, cpcfg=cpcfg,
                                      components=components, tol=tol, cov=cov)
        t2 = task2_model_fit(cfg, cpcfg)
        # GATE — proceed to Task 3 only if the singleton residual is NEGLIGIBLE (a
        # non-negligible UNRESOLVED residual would contaminate the same share of corrected
        # draw_joint=0 values, invalidating the candidate), the instrument is usable, and
        # the mapping is unambiguous.
        gate_cfg = cpcfg["gate"]
        rate = t1.get("residual_fail_rate")
        instrument_usable = (t1.get("verdict") != "no_sample")
        max_rate = float(gate_cfg["max_singleton_residual_fail_rate"])
        residual_negligible = (rate is not None and rate <= max_rate)
        require_negligible = bool(gate_cfg.get("require_residual_negligible", True))
        residual_ok = residual_negligible if require_negligible else (rate is not None)
        mapping_ok = (t2.get("status") == "ok")
        gate_pass = bool(instrument_usable and residual_ok and mapping_ok
                         and args.tasks == "all")
        if not residual_ok:
            gate_reason = (f"singleton residual fail rate {rate:.4f} exceeds the "
                           f"'negligible' threshold {max_rate} and is unresolved "
                           f"(verdict={t1.get('verdict')}); a non-negligible unresolved "
                           "residual would contaminate the same share of corrected "
                           "draw_joint=0 values -> correction candidate NOT produced.")
        elif args.tasks != "all":
            gate_reason = "tasks-12 mode: Tasks 1-2 + gate only (Task 3 not requested)."
        elif gate_pass:
            gate_reason = "all gate conditions met; correction candidate authorised to build."
        else:
            gate_reason = "instrument or mapping condition failed."
        gate = {"instrument_usable": instrument_usable,
                "singleton_residual_fail_rate": rate,
                "require_residual_negligible": require_negligible,
                "negligible_threshold": max_rate,
                "singleton_residual_negligible": residual_negligible,
                "residual_ok": residual_ok,
                "residual_verdict": t1.get("verdict"),
                "mapping_unambiguous": mapping_ok,
                "tasks_arg": args.tasks,
                "gate_pass": gate_pass,
                "gate_reason": gate_reason}
        t3 = t4 = None
        if gate_pass:
            t3 = task3_correction_candidate(cfg2, bc, base, out_dir, cpcfg=cpcfg,
                                            components=components, tol=tol, cov=cov)
            art = t3.pop("artifact_df", None)
            t4 = task4_diagnostics(cfg2, bc, base, art, cpcfg=cpcfg,
                                   components=components, tol=tol, cov=cov)
    finally:
        os.dup2(_so, 1)
        os.dup2(_se, 2)
        os.close(_so)
        os.close(_se)
        _tmp.seek(0)
        console = _tmp.read().decode("utf-8", errors="replace")
        _tmp.close()
    em_log.write_text(console, encoding="utf-8")

    out = {"increment": "stage2_couples_correction_prep_v1",
           "no_welfare_finding": True, "measures_touched": ["W3_only"],
           "re_estimated": False, "computed_v_dir": False,
           "priced_any_redrawn_node": False, "overwrote_build_parquet": False,
           "euromod_console_log": str(em_log),
           "task1_singleton_residual": t1,
           "task2_model_fit": t2,
           "gate": gate,
           "task3_correction_candidate": t3,
           "task4_diagnostics": t4,
           "scope_statement": (
               "Audit-only. No W^3 finding; no measure beyond W^3; nothing re-estimated; "
               "no V_i^dir; no redrawn node priced; no build/storage/engine-ready parquet "
               "written or overwritten. The Task-3 side artifact (if produced) is a NEW "
               "correction CANDIDATE, NOT authorised as estimator input until separately "
               "reviewed.")}
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"[stage2:correction-prep] wrote {args.out_json}")
    print(f"  Task1 residual: {t1['n_fail']}/{t1['n_singleton_nodes']} fail "
          f"(rate={t1['residual_fail_rate']}) verdict={t1['verdict']}")
    if t2.get("status") == "ok":
        print(f"  Task2 fit: P_chosen median={t2['P_chosen']['median']:.3e} vs uniform "
              f"{t2['uniform_benchmark']:.3e} | chosen rank median={t2['chosen_rank']['median']} "
              f"| share top-1%={t2['share_in_top'].get('0.01')}")
    print(f"  GATE pass={gate['gate_pass']} (residual_ok={gate['residual_ok']}, "
          f"mapping_ok={gate['mapping_unambiguous']}, tasks={args.tasks})")
    print(f"  GATE reason: {gate['gate_reason']}")
    if t3 is not None:
        print(f"  Task3 side artifact: {t3['n_rows']} rows -> {t3['side_artifact']}")
    else:
        print("  Task3/4: SKIPPED (gate did not pass) -- no correction candidate produced.")


if __name__ == "__main__":
    main()
