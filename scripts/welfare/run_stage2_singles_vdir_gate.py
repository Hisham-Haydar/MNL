"""
Stage Two — Increment Two-K: SINGLES V_i^dir gate + smoke ONLY.

SINGLES TRACK ONLY. Does NOT touch couples, does NOT depend on the couples residual,
does NOT re-estimate, does NOT run the full-sample singles V_i^dir production cross-check,
and writes NO build/storage/engine-ready/priced/precompute/chunk parquet.

Task 1 — existing-node parity gate at production scope: on a deterministic singles sample
  larger than the Two-E ladder, across all 3 years x {singles_male, singles_female},
  clean-reprice EXISTING singles nodes (isolated roster, original IDs — the validated
  collision-free benchmark; singles node key (stacked_hh_uid, draw) makes the stamp unique)
  and confirm ils_dispy + each component (ils_origy/ils_ben/ils_tax/ils_sicdy) reproduce
  the stored value to machine tolerance. PASS requires EVERY sampled cell to reproduce,
  including ils_ben. If any cell fails -> STOP (do not run Task 2).

Task 2 — bounded V_i^dir smoke (only if Task 1 PASSES): see run_stage2_singles_vdir_smoke.

Reuses the Two-E helpers (welfare_assessment_unit_diag) for the EUROMOD call, raw-schema
input build, fd-level TUDef capture, and node-key parity compare. Config-driven; no
hardcoded case constants.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
import welfare_assessment_unit_diag as wd  # noqa: E402
import welfare_core as wc  # noqa: E402

SINGLES_KEY = ["stacked_hh_uid", "draw"]
_SEX_DGN = {"singles_male": 1.0, "singles_female": 0.0}


def _cell_parity(bc, pl, priced, *, year, sex, n_hh, nodes_per_hh, components, tol, cov):
    """Existing-node parity for one (year, sex) cell. Reprices ALL sampled nodes in ONE
    production-stamped EUROMOD batch (singles stamp `id*1000 + draw` is UNIQUE per node ->
    collision-free; Two-E Rung-3 verified the stamped singles batch reproduces stored), and
    compares to stored on decider rows keyed by (stacked_hh_uid, draw, original idperson)."""
    system_code, dataset_name = bc["system_pairing"][year]
    country = str(cov or str(system_code).split("_")[0])
    raw = bc["raw_schema"][year]
    dgn = _SEX_DGN[sex]
    sub_sex = pl[pl["dgn"] == dgn]
    uids = sub_sex["stacked_hh_uid"].drop_duplicates().sort_values().head(n_hh).tolist()
    # first nodes_per_hh existing draws per HH (deterministic)
    draws_keep = sorted(pl["draw"].unique())[:nodes_per_hh]
    sel = pl[(pl["stacked_hh_uid"].isin(uids)) & (pl["draw"].isin(draws_keep))].copy()
    n_hh_actual = int(sel["stacked_hh_uid"].nunique())

    # production singles stamp: id_mult=1000, unique per (id, draw)
    stamped = bc["stamp"](sel.copy(), "draw", 1_000)
    em = wd._em_input(stamped, raw)
    t0 = time.time()
    sim, warn, err, _ = wd._run_euromod(bc, em, country=country,
                                        system_code=system_code, dataset_name=dataset_name)
    wall = time.time() - t0
    if err is not None or sim is None:
        return {"year": year, "sex": sex, "system_code": system_code, "country": country,
                "n_hh": n_hh_actual, "status": "BLOCKED", "reason": err or "no sim",
                "n_euromod_input_rows": int(len(em)),
                "euromod_wall_seconds": round(wall, 3)}

    comp, _, nmatched = wd._compare(sim, stamped, priced, SINGLES_KEY, components, tol)
    bad_components = [c for c in components
                     if comp.get(c, {}).get("n_above_tol", 0) > 0]
    dispy_bad = comp.get("ils_dispy", {}).get("n_above_tol", 0) > 0
    status = "PASS" if (not bad_components and not dispy_bad and nmatched > 0) else \
             ("FAIL" if nmatched > 0 else "BLOCKED")
    return {
        "year": year, "sex": sex, "system_code": system_code, "country": country,
        "n_hh": n_hh_actual, "n_nodes_matched": int(nmatched),
        "n_euromod_input_rows": int(len(em)), "max_tudef": warn["n_warning_lines"],
        "component_parity": comp, "failing_components": bad_components,
        "status": status, "euromod_wall_seconds": round(wall, 3),
    }


def task1_parity_gate(cfg2, sg, bc, base):
    components = list(sg["components"])
    tol = float(sg["tol"])
    cov = sg.get("country_override")
    pg = sg["parity_gate"]
    cells = {}
    for year in sg["years"]:
        pl, _ = wd._load(base, cfg2["precompute_long_stem"], year, "singles", long_=True)
        priced, _ = wd._load(base, cfg2["priced_long_stem"], year, "singles", long_=False)
        for sex in sg["sexes"]:
            cell = _cell_parity(bc, pl, priced, year=year, sex=sex,
                                n_hh=int(pg["n_hh_per_cell"]),
                                nodes_per_hh=int(pg["nodes_per_hh"]),
                                components=components, tol=tol, cov=cov)
            cells[f"{year}__{sex}"] = cell
    all_pass = all(c["status"] == "PASS" for c in cells.values())
    return {"all_cells_pass": all_pass, "n_cells": len(cells),
            "sample_rule": (f"first {pg['n_hh_per_cell']} households by stacked_hh_uid "
                            f"within each (year, sex) cell; first {pg['nodes_per_hh']} "
                            f"existing draws per household (Two-E ladder used 6)"),
            "cells": cells}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-json", required=True)
    args = ap.parse_args()

    cfg = wc.load_config(args.config)
    cfg2 = cfg["stage2"]
    sg = cfg2["singles_vdir_gate"]
    bc = wd.build_constants(cfg2["build_module"])
    from _bpool_paths import bpool_dir
    base = bpool_dir()

    em_log = Path(args.out_json).with_name("stage2_singles_vdir_gate_euromod_console.log")
    _tmp = tempfile.TemporaryFile(mode="w+b")  # noqa: SIM115 (manual fd lifecycle)
    _so, _se = os.dup(1), os.dup(2)
    os.dup2(_tmp.fileno(), 1)
    os.dup2(_tmp.fileno(), 2)
    try:
        t1 = task1_parity_gate(cfg2, sg, bc, base)
    finally:
        os.dup2(_so, 1)
        os.dup2(_se, 2)
        os.close(_so)
        os.close(_se)
        _tmp.seek(0)
        console = _tmp.read().decode("utf-8", errors="replace")
        _tmp.close()
    em_log.write_text(console, encoding="utf-8")

    # throughput basis + projected cost of the later full singles run (Task 3)
    cells = t1["cells"]
    tot_wall = sum(c.get("euromod_wall_seconds", 0.0) for c in cells.values())
    tot_rows = sum(c.get("n_euromod_input_rows", 0) for c in cells.values())
    per_row = (tot_wall / tot_rows) if tot_rows else None
    proj = sg["projection"]
    total_hh = int(proj["singles_male_hh"]) + int(proj["singles_female_hh"])
    projection = {"basis_seconds_per_input_row": per_row,
                  "basis_note": ("batched basis; LOWER BOUND — excludes per-call model "
                                 "load / process spin-up; moot while the gate fails"),
                  "full_singles_households": total_hh, "rows_per_node_approx": 1,
                  "per_nodes_per_hh": {}}
    if per_row is not None:
        for npn in proj["nodes_per_hh"]:
            rows = total_hh * npn
            sec = per_row * rows
            projection["per_nodes_per_hh"][str(npn)] = {
                "nodes_per_hh": npn, "approx_input_rows": int(rows),
                "approx_seconds": round(sec, 1), "approx_hours": round(sec / 3600.0, 2)}

    gate_pass = bool(t1["all_cells_pass"])
    readiness = "READY" if gate_pass else "NOT_READY"
    task2 = {"status": "SKIPPED" if not gate_pass else "not_run_in_this_call",
             "reason": ("Task 1 existing-node parity gate FAILED; per the stop rule no "
                        "redrawn node is priced and the V_i^dir smoke is not run."
                        if not gate_pass else "gate passed; smoke is a separate call")}

    out = {"increment": "stage2_singles_vdir_gate_v1__task1",
           "track": "singles_only", "no_welfare_finding": True,
           "measures_touched": ["W3_only"], "re_estimated": False,
           "computed_full_vdir_production": False, "priced_couples": False,
           "priced_redrawn_node": False,
           "wrote_or_overwrote_parquet": False,
           "euromod_console_log": str(em_log),
           "task1_existing_node_parity": t1,
           "task2_vdir_smoke": task2,
           "task3_projection": projection,
           "readiness": readiness,
           "gate_pass": gate_pass,
           "scope_statement": (
               "SINGLES track only. No W^3 finding; nothing beyond W^3; no couples "
               "touched; nothing re-estimated; no full V_i^dir production run; no "
               "parquet written or overwritten.")}
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"[stage2:singles-gate] wrote {args.out_json}")
    print(f"  TASK1 all_cells_pass={t1['all_cells_pass']} ({t1['n_cells']} cells) "
          f"-> READINESS={readiness} | Task2 smoke: {task2['status']}")
    for name, c in t1["cells"].items():
        ben = c.get("component_parity", {}).get("ils_ben", {})
        print(f"  {name}: {c['status']} nodes={c.get('n_nodes_matched', 0)} "
              f"tudef={c.get('max_tudef', '-')} | ils_ben max={ben.get('max_abs', 0):.2e} "
              f"bad={ben.get('n_above_tol', 0)} | wall={c.get('euromod_wall_seconds', 0)}s "
              f"rows={c.get('n_euromod_input_rows', 0)}")


if __name__ == "__main__":
    main()
