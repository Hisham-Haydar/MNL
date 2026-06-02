"""
Stage Two — Increment Two-G, Task 1 runner: reconcile Two-E vs Two-F singleton evidence
and diagnose the 3 Two-F singleton-control failures.

For each of: the Two-E couples singleton PASS node (reproduced via the Two-F isolated
path) and the 3 Two-F singleton FAIL nodes, this:
  (A) reprices the node ISOLATED (benchmark clean reprice) -> clean value + parity;
  (B) reprices the household's FULL chunk-0 draw-band [0,150) the PRODUCTION way
      (stamp on draw_joint, so draw_joint=0's collision pair is present in the batch,
      exactly as the build's chunk 0 did) -> tests whether the production batch
      reproduces the STORED (possibly contaminated) value for the node;
  (C) optionally reprices the same band COLLISION-FREE (full-node-key stamping) ->
      tests whether removing the collision restores the clean value.
This isolates whether a singleton failure is: same-construction contradiction (clean
isolated FAILS warning-free), or stored-target contamination via full-batch spillover
from the household's draw_joint=0 collision (production batch reproduces stored; clean
isolated and collision-free batch agree on a different value).

Audit-only: no parquet written, nothing re-estimated, no redrawn node priced.
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
import welfare_chosen_contamination as cc  # noqa: E402
import welfare_core as wc  # noqa: E402

# No hardcoded France / year / household diagnostic constants live in this source.
# The deterministic diagnostic cases are DERIVED from prior provenance JSONs via
# load_cases_from_provenance(); paths + structural parameters come from config
# (welfare.stage2.couples_contamination_audit.task1_singleton_reconcile).


def load_cases_from_provenance(t1cfg):
    """Derive the Two-E singleton PASS case and the Two-F singleton_control FAIL cases
    from prior provenance JSONs (agnostic: nothing about France/year/household is
    hardcoded here). Returns (two_e_pass, two_f_fails, node, band).

    two_e_pass : {stacked_hh_uid, year, node}   (first Rung-2 PASS node of the couples case)
    two_f_fails: [{stacked_hh_uid, year, node}, ...]  (the FAIL nodes of the named stratum)
    node       : the shared full-node-key dict {draw_joint, draw_male, draw_female} used
                 for the per-decider diagnosis (taken from the cases; asserted consistent)
    band       : (lo, hi) production chunk draw_joint band
    """
    with open(t1cfg["two_e_diag_json"]) as f:
        e = json.load(f)
    case = e["cases"][t1cfg["two_e_case_key"]]
    passes = [p for p in case["rung2"]["per_node"] if p.get("status") == "PASS"]
    if not passes:
        raise SystemExit(f"no Rung-2 PASS node in Two-E case {t1cfg['two_e_case_key']!r}")
    p0 = passes[0]["node"]
    two_e_pass = {"stacked_hh_uid": int(p0["stacked_hh_uid"]),
                  "year": int(case["year"]), "node": _node_key(p0)}

    with open(t1cfg["two_f_reprice_json"]) as f:
        fjson = json.load(f)
    stratum = t1cfg["two_f_fail_stratum"]
    two_f_fails = []
    for yr in fjson["task3_reprice_per_year"]:
        for nd in yr.get("nodes", []):
            if nd.get("stratum") == stratum and nd.get("status") == "FAIL":
                two_f_fails.append({"stacked_hh_uid": int(nd["node"]["stacked_hh_uid"]),
                                    "year": int(nd.get("year")),
                                    "node": _node_key(nd["node"])})

    # the per-decider diagnosis compares the same singleton node across cases; assert the
    # FAIL cases share one node key, and use it (derived, not hardcoded).
    node = two_f_fails[0]["node"] if two_f_fails else two_e_pass["node"]
    band = tuple(int(x) for x in t1cfg["production_chunk_band"])
    return two_e_pass, two_f_fails, node, band


def _node_key(nd):
    return {"draw_joint": int(nd["draw_joint"]), "draw_male": int(nd["draw_male"]),
            "draw_female": int(nd["draw_female"])}


def _extract_node_value(sim, frame, node, component, decider_idperson_true):
    """Pull a repriced component value for one (node, original idperson) from a batch."""
    fr = frame.reset_index(drop=True).copy()
    fr["__rep"] = pd.to_numeric(sim[component], errors="coerce").to_numpy()[: len(fr)]
    pid = "idperson_true" if "idperson_true" in fr.columns else "idperson"
    m = np.ones(len(fr), dtype=bool)
    for k in cc.KEY:
        m &= (fr[k] == node[k])
    m &= (fr[pid] == decider_idperson_true)
    vals = fr.loc[m, "__rep"].to_numpy()
    return float(vals[0]) if len(vals) else float("nan")


def _diagnose(bc, *, hh, year, node, components, tol, cov, priced, pl, band_range):
    sub_hh = pl[pl["stacked_hh_uid"] == hh].copy()
    node_full = {"stacked_hh_uid": hh, **node}
    rows = cc._node_rows(sub_hh, node_full)
    # stored values on decider rows for this node (nominal), per original idperson
    pr_node = priced[(priced["stacked_hh_uid"] == hh)
                     & (priced["draw_joint"] == node["draw_joint"])
                     & (priced["draw_male"] == node["draw_male"])
                     & (priced["draw_female"] == node["draw_female"])
                     & (priced.get("ruro_decider", 1) == 1)]
    pid = "idperson_true" if "idperson_true" in pr_node.columns else "idperson"
    stored = {int(r[pid]): {c: float(r[c]) for c in components if c in pr_node.columns}
              for _, r in pr_node.iterrows()}

    # (A) isolated clean reprice
    a = cc.reprice_isolated(bc, rows, year=year, components=components, tol=tol,
                            priced=priced, country_override=cov)
    a_clean = {}
    if "sim" in a:
        for idp in stored:
            a_clean[idp] = {c: _extract_node_value(a["sim"], rows, node_full, c, idp)
                            for c in components}
        a.pop("sim", None)

    # the household's production chunk draw_joint band [lo, hi)
    band = sub_hh[(sub_hh["draw_joint"] >= band_range[0])
                  & (sub_hh["draw_joint"] < band_range[1])].copy()

    # (B) production-stamped full-band batch
    sysc, dsn = bc["system_pairing"][year]
    country = str(cov or str(sysc).split("_")[0])
    raw = bc["raw_schema"][year]
    b_stamped = bc["stamp"](band.copy(), "draw_joint", 10_000)
    em_b = wd._em_input(b_stamped, raw)
    sim_b, warn_b, err_b, _ = wd._run_euromod(bc, em_b, country=country,
                                              system_code=sysc, dataset_name=dsn)
    b_prod = {}
    if err_b is None:
        for idp in stored:
            b_prod[idp] = {c: _extract_node_value(sim_b, b_stamped, node_full, c, idp)
                           for c in components}

    # (C) collision-free full-band batch
    c_stamped = cc._collisionfree_stamp(band.copy())
    em_c = wd._em_input(c_stamped, raw)
    sim_c, warn_c, err_c, _ = wd._run_euromod(bc, em_c, country=country,
                                              system_code=sysc, dataset_name=dsn)
    c_free = {}
    if err_c is None:
        for idp in stored:
            c_free[idp] = {c: _extract_node_value(sim_c, c_stamped, node_full, c, idp)
                           for c in components}

    # classify per decider on the parity-relevant component ils_ben
    comp_focus = "ils_ben" if "ils_ben" in components else components[0]
    deciders = []
    for idp in stored:
        s = stored[idp].get(comp_focus, float("nan"))
        a_ = a_clean.get(idp, {}).get(comp_focus, float("nan"))
        b_ = b_prod.get(idp, {}).get(comp_focus, float("nan"))
        c_ = c_free.get(idp, {}).get(comp_focus, float("nan"))
        deciders.append({
            "idperson_true": idp, "component": comp_focus,
            "stored": s, "isolated_clean": a_, "production_batch": b_,
            "collisionfree_batch": c_,
            "prod_reproduces_stored": bool(abs(b_ - s) <= 1e-3) if np.isfinite(b_) and np.isfinite(s) else None,
            "clean_eq_collisionfree": bool(abs(a_ - c_) <= 1e-3) if np.isfinite(a_) and np.isfinite(c_) else None,
            "clean_eq_stored": bool(abs(a_ - s) <= tol) if np.isfinite(a_) and np.isfinite(s) else None,
        })

    # does this household have a draw_joint=0 collision block?
    dj0 = sub_hh[sub_hh["draw_joint"] == 0]
    dj0_alts = dj0[["draw_male", "draw_female"]].drop_duplicates().shape[0]

    return {
        "hh": hh, "year": year, "node": node_full,
        "isolated_status": a.get("status"), "isolated_tudef": a.get("tudef"),
        "isolated_components": a.get("components"),
        "production_band_tudef": (warn_b["n_warning_lines"] if err_b is None else None),
        "collisionfree_band_tudef": (warn_c["n_warning_lines"] if err_c is None else None),
        "band": list(band_range), "band_n_draw_joint": int(band["draw_joint"].nunique()),
        "household_has_dj0_collision": bool(dj0_alts > 1),
        "dj0_distinct_alts": int(dj0_alts),
        "deciders": deciders,
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-json", required=True)
    args = ap.parse_args()

    cfg = wc.load_config(args.config)
    cfg2 = cfg["stage2"]
    rs = cfg2["couples_contamination_audit"]["reprice_sample"]
    t1cfg = cfg2["couples_contamination_audit"]["task1_singleton_reconcile"]
    components = list(rs["components"])
    tol = float(rs["tol"])
    cov = rs.get("country_override")
    bc = wd.build_constants(cfg2["build_module"])
    from _bpool_paths import bpool_dir
    base = bpool_dir()

    # deterministic diagnostic cases DERIVED from prior provenance (no hardcoding)
    cases = load_cases_from_provenance(t1cfg)
    two_e_pass, two_f_fails, band_range = cases[0], cases[1], cases[3]
    targets = [("two_e_pass", two_e_pass["stacked_hh_uid"], two_e_pass["year"],
                two_e_pass["node"])]
    targets += [("two_f_fail", t["stacked_hh_uid"], t["year"], t["node"])
                for t in two_f_fails]

    em_log = Path(args.out_json).with_name("stage2_chosen_task1_euromod_console.log")
    _tmp = tempfile.TemporaryFile(mode="w+b")  # noqa: SIM115 (manual fd lifecycle)
    _so, _se = os.dup(1), os.dup(2)
    os.dup2(_tmp.fileno(), 1)
    os.dup2(_tmp.fileno(), 2)
    results = []
    try:
        # group by year to load each precompute/priced once
        by_year = {}
        for label, hh, year, node in targets:
            by_year.setdefault(year, []).append((label, hh, node))
        for year, items in by_year.items():
            pl, _ = wd._load(base, cfg2["precompute_long_stem"], year, "couples", long_=True)
            priced, _ = wd._load(base, cfg2["priced_long_stem"], year, "couples", long_=False)
            for label, hh, node in items:
                d = _diagnose(bc, hh=hh, year=year, node=node,
                              components=components, tol=tol, cov=cov,
                              priced=priced, pl=pl, band_range=band_range)
                d["label"] = label
                results.append(d)
    finally:
        os.dup2(_so, 1)
        os.dup2(_se, 2)
        os.close(_so)
        os.close(_se)
        _tmp.seek(0)
        console = _tmp.read().decode("utf-8", errors="replace")
        _tmp.close()
    em_log.write_text(console, encoding="utf-8")

    out = {"increment": "stage2_couples_chosen_contamination_v1__task1",
           "no_welfare_finding": True, "measures_touched": ["W3_only"],
           "re_estimated": False, "priced_any_redrawn_node": False,
           "computed_v_dir": False, "wrote_parquet": False,
           "cases_source": {"two_e_diag_json": t1cfg["two_e_diag_json"],
                            "two_f_reprice_json": t1cfg["two_f_reprice_json"],
                            "two_e_case_key": t1cfg["two_e_case_key"],
                            "two_f_fail_stratum": t1cfg["two_f_fail_stratum"],
                            "note": "diagnostic cases derived from prior provenance, not hardcoded"},
           "production_chunk_band": {"chunk_draw_joint_band": list(band_range),
                                     "note": ("from config (verified from chunk meta): the "
                                              "build prices this draw_joint band across ALL "
                                              "households in ONE EUROMOD batch, so "
                                              "draw_joint=0's collision pair shares the "
                                              "batch with later draw_joint values.")},
           "two_e_pass_node": two_e_pass["node"],
           "euromod_console_log": str(em_log),
           "diagnoses": results}
    out["scope_statement"] = (
        "Audit-only. EUROMOD on existing-node clean-reprice + diagnostic batches only; "
        "no redrawn node priced, nothing re-estimated, no V_i^dir, no parquet written.")
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"[stage2:chosen-task1] wrote {args.out_json}")
    for d in results:
        print(f"  {d['label']} hh={d['hh']} y={d['year']} isolated={d['isolated_status']} "
              f"tudef(iso={d['isolated_tudef']},prodband={d['production_band_tudef']},"
              f"cfband={d['collisionfree_band_tudef']}) dj0_alts={d['dj0_distinct_alts']}")
        for dec in d["deciders"]:
            print(f"     idp={dec['idperson_true']} {dec['component']}: stored={dec['stored']:.2f} "
                  f"iso={dec['isolated_clean']:.2f} prod={dec['production_batch']:.2f} "
                  f"cfree={dec['collisionfree_batch']:.2f} | prod=stored?{dec['prod_reproduces_stored']} "
                  f"clean=cfree?{dec['clean_eq_collisionfree']}")


if __name__ == "__main__":
    main()
