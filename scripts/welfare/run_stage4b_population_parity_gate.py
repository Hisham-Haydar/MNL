"""
STAGE FOUR, INCREMENT FOUR-B — population-faithful existing-node parity gate against the STAGED
reproducible welfare-pricing reference. The population-scale Gate-0 analogue that licenses
redrawn-node welfare pricing.

For each year x mode cell, re-prices ONE COMPLETE PRODUCTION CHUNK of the staged reference
through the patched all-component chunk worker, at the EXACT production chunk band the staged
reference was itself priced in. This is the population-faithful unit Two-L/Two-N require: the
EUROMOD batch is the SAME representative population batch as the staged chunk (every household
across the chunk's full draw band), NOT an isolated node or a narrow draw sub-slice. (A narrow
sub-band, even with all households present, is a DIFFERENT batch — the means-tested benefit
depends on the full chunk batch composition, Two-L — so it is not a faithful reprice.) The
reprice is compared to the STAGED reference stored chunk (staging_twoN) on the 6 headline
columns + every shared ils_* / *_s component, by node key, to machine tolerance.

Reads the welfare.stage4 config (Four-A) for the staged stem, staged chunk dir, pinned
references, and the population-batch / no-double-deflation discipline. Config-driven; nothing
country/year/spec-specific is hardcoded.

Does NOT: price redrawn nodes, compute V_i^dir, promote W^3, re-estimate, swap/overwrite/move/
delete production parquet, promote the staged baseline to canonical, or overwrite the certified
baseline. The reprice output goes to a SCRATCH dir (never production, never the staging
reference). Nothing beyond W^3.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402
from _bpool_paths import bpool_dir  # noqa: E402

_CONFIG = Path("scripts/welfare/configs/welfare_stage1_w3.yaml")
_WORKER = Path("scripts/bpool/run_bpool_euromod_chunk.py").resolve()
TOL = 1e-6
_HEADLINE = ["ils_dispy", "ils_origy", "ils_ben", "ils_tax", "ils_sicdy", "ils_dispy_real"]
# EXACT production chunk definitions (from the Two-N manifest). The parity reprice uses a FULL
# production chunk per cell so the EUROMOD batch == the staged chunk's own population batch.
# To keep cost bounded we reprice ONE chunk per (year, mode): the singles chunk (c0, the only
# singles chunk, [0,101)) and the FIRST couples chunk (c0, [0,150)). Both are complete chunks,
# not sub-slices, so they are population-faithful by construction (Three-A proved full-chunk
# re-runs reproduce staging to 0.0).
_CELL_CHUNK = {
    "singles": {"chunk_id": 0, "draw_lo": 0, "draw_hi": 101},
    "couples": {"chunk_id": 0, "draw_lo": 0, "draw_hi": 150},
}
_SCRATCH_CHUNK_ID = 90  # distinct id so the scratch parquet can never collide with c0..c5
_KEY = {"singles": ["stacked_hh_uid", "draw", "idperson_true"],
        "couples": ["stacked_hh_uid", "draw_joint", "draw_male", "draw_female",
                    "idperson_true"]}


def _load_stage4():
    if not _CONFIG.exists():
        raise SystemExit(f"STOP: welfare config missing: {_CONFIG}")
    with open(_CONFIG) as f:
        cfg = yaml.safe_load(f)
    s4 = cfg.get("welfare", {}).get("stage4")
    if s4 is None:
        raise SystemExit("STOP: welfare.stage4 config missing (run Four-A first)")
    return s4


def reprice_band(bp, staged_chunk_dir, scratch, year, mode, chunk_id, lo, hi, timeout,
                 regen=False):
    """Re-price the FULL production chunk c{chunk_id} = band [lo,hi) of (year,mode) at POPULATION
    scale via the patched worker, to the SCRATCH dir, then compare to the EXACT staged reference
    stored chunk (staging_twoN c{chunk_id}) in full, by node key. The reprice band == the staged
    chunk band, so the EUROMOD batch is the SAME population batch. Returns the parity record."""
    staged_chunk = staged_chunk_dir / f"fr_p3a_bpool_priced__{year}__{mode}__c{chunk_id}.parquet"
    if not staged_chunk.exists():
        return {"year": year, "mode": mode, "status": "BLOCKED",
                "reason": f"staged reference chunk missing: {staged_chunk}"}

    reprice_pq = scratch / f"fr_p3a_bpool_priced__{year}__{mode}__c{_SCRATCH_CHUNK_ID}.parquet"
    if regen:
        # reuse the existing scratch reprice (no EUROMOD re-run); only re-derive the comparison
        if not reprice_pq.exists():
            return {"year": year, "mode": mode, "status": "BLOCKED",
                    "reason": f"--regen-from-scratch but scratch reprice missing: {reprice_pq}"}
        wall = None
    else:
        # --- run the patched worker on the FULL production chunk band -> scratch ---
        cmd = [sys.executable, str(_WORKER), "--year", str(year), "--mode", mode,
               "--draw-lo", str(lo), "--draw-hi", str(hi),
               "--chunk-id", str(_SCRATCH_CHUNK_ID), "--staging-dir", str(scratch)]
        t0 = time.time()
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        wall = round(time.time() - t0, 1)
        if proc.returncode != 0 or not reprice_pq.exists():
            return {"year": year, "mode": mode, "status": "REPRICE_FAILED",
                    "reason": (proc.stderr or proc.stdout or "")[-600:], "wall_seconds": wall}

    reb = pd.read_parquet(reprice_pq)
    # the staged reference chunk in FULL (same band by construction)
    stg = pd.read_parquet(staged_chunk)

    key = [k for k in _KEY[mode] if k in reb.columns and k in stg.columns]
    n_hh = int(reb["stacked_hh_uid"].nunique())
    full_hh = int(stg["stacked_hh_uid"].nunique())

    shared = [c for c in reb.columns if c in stg.columns]
    comp_cols = sorted([c for c in shared
                        if (c.startswith("ils_") or c.endswith("_s")) and c not in _HEADLINE])
    m = reb[key + [c for c in _HEADLINE + comp_cols if c in reb.columns]].merge(
        stg[key + [c for c in _HEADLINE + comp_cols if c in stg.columns]].drop_duplicates(key),
        on=key, how="inner", suffixes=("_reb", "_stg"))

    def _maxabs(cols):
        res = {}
        worst = {}
        ok = True
        for c in cols:
            a = f"{c}_reb"
            b = f"{c}_stg"
            if a not in m.columns or b not in m.columns:
                continue
            d = np.abs(pd.to_numeric(m[a], errors="coerce").to_numpy()
                       - pd.to_numeric(m[b], errors="coerce").to_numpy())
            nbad = int(np.sum(d > TOL))
            mx = float(np.nanmax(d)) if len(d) else 0.0
            res[c] = {"max_abs": mx, "n_above_tol": nbad}
            if nbad > 0:
                worst[c] = mx
                ok = False
        return res, worst, ok

    hl_res, hl_worst, hl_ok = _maxabs([c for c in _HEADLINE if c in reb.columns])
    cp_res, cp_worst, cp_ok = _maxabs(comp_cols)

    return {
        "year": year, "mode": mode, "status": "OK",
        "chunk_id": chunk_id, "band": [lo, hi], "scratch_chunk": str(reprice_pq),
        "staged_reference_chunk": str(staged_chunk),
        "wall_seconds": wall,
        "n_rows_repriced": int(len(reb)), "n_rows_compared": int(len(m)),
        "n_hh_in_batch": n_hh, "full_staged_chunk_hh": full_hh,
        "population_faithful": bool(n_hh == full_hh),  # full HH population in the chunk batch
        "keys": key,
        "headline_parity": {"per_column": hl_res, "worst": hl_worst, "ok": hl_ok},
        "component_parity": {"n_components": len(comp_cols), "per_column_failures": cp_worst,
                             "ok": cp_ok},
        "cell_pass": bool(hl_ok and cp_ok),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--scratch-dir", required=True,
                    help="reprice output dir; MUST NOT be production new_data root, chunks/, "
                         "staging_twoN, or staging_threeB1_priced")
    ap.add_argument("--years", default="2015,2016,2017")
    ap.add_argument("--modes", default="singles,couples")
    ap.add_argument("--per-cell-timeout", type=int, default=14400)
    ap.add_argument("--regen-from-scratch", action="store_true",
                    help="reuse the existing scratch reprice chunks (no EUROMOD re-run); only "
                         "re-derive the parity comparison + provenance JSON (resumability)")
    args = ap.parse_args()

    s4 = _load_stage4()
    wpr = s4["welfare_pricing_reference"]
    bp = bpool_dir()
    staged_chunk_dir = bp / wpr["staged_chunk_dir_name"]            # staging_twoN
    staged_priced_dir = bp / wpr["staged_priced_dir_name"]         # staging_threeB1_priced
    scratch = Path(args.scratch_dir).resolve()

    # safety: scratch must not be production / staging reference
    forbidden = {bp.resolve(), (bp / "chunks").resolve(),
                 staged_chunk_dir.resolve(), staged_priced_dir.resolve()}
    if scratch in forbidden:
        raise SystemExit(f"REFUSE: scratch '{scratch}' is production or a staging reference dir.")
    # Four-A scope guard assertion
    sg = s4.get("scope_guards", {})
    if sg.get("prices_redrawn_node") or sg.get("computes_v_dir"):
        raise SystemExit("REFUSE: Four-A scope_guards forbid redrawn pricing / V_i^dir.")
    scratch.mkdir(parents=True, exist_ok=True)

    years = [int(y) for y in args.years.split(",")]
    modes = [m.strip() for m in args.modes.split(",")]

    cells = []
    all_pass = True
    stopped = False
    for year in years:
        for mode in modes:
            ch = _CELL_CHUNK[mode]
            cid, lo, hi = ch["chunk_id"], ch["draw_lo"], ch["draw_hi"]
            rec = reprice_band(bp, staged_chunk_dir, scratch, year, mode, cid, lo, hi,
                               args.per_cell_timeout, regen=args.regen_from_scratch)
            cells.append(rec)
            cp = rec.get("cell_pass", False)
            all_pass = all_pass and bool(cp) and rec.get("status") == "OK"
            print(f"[four-B] {year} {mode} chunk c{cid} band[{lo},{hi}): "
                  f"status={rec.get('status')} "
                  f"pop_faithful={rec.get('population_faithful')} "
                  f"hl_ok={rec.get('headline_parity',{}).get('ok')} "
                  f"comp_ok={rec.get('component_parity',{}).get('ok')} "
                  f"n_hh={rec.get('n_hh_in_batch')}/{rec.get('full_staged_chunk_hh')}",
                  flush=True)
            # STOP on the first failing/blocked cell (do not continue pricing)
            if rec.get("status") != "OK" or not cp:
                stopped = True
                break
        if stopped:
            break

    ready = bool(all_pass and not stopped
                 and len(cells) == len(years) * len(modes))

    carried_constraints = {
        "use_staged_reproducible_reference_not_production_canonical": True,
        "staged_engine_ready_stem": wpr["staged_engine_ready_stem"],
        "price_counterfactual_nodes_in_representative_population_batches": True,
        "counterfactual_wages_nominal_frame_before_euromod": True,
        "return_disposable_income_to_real_via_phi_y_after_euromod": True,
        "no_double_deflation": s4["pricing_discipline"]["no_double_deflation"],
        "no_silent_interpolation": True,
        "reuse_full_chunk_population_batch_construction": True,
        "do_not_optimise_to_sub_bands_or_isolated_nodes": True,
        "full_chunk_construction_note": (
            "The V_i^dir runner MUST reprice within the complete production chunk batch (the "
            "full chunk band the staged reference was priced in), NOT a draw sub-band or "
            "isolated node. Four-B's method correction showed a sub-band is a DIFFERENT EUROMOD "
            "batch and breaks means-tested-benefit (ils_benmt/bsa) parity while income and "
            "contributions still reproduce."),
    }

    out = {
        "increment": "stage4b_population_parity_gate_v1",
        "priced_redrawn_node": False, "computed_v_dir": False, "promoted_w3": False,
        "re_estimated": False, "promoted_to_canonical": False,
        "production_parquet_swapped_or_overwritten_or_moved_or_deleted": False,
        "overwrote_certified_baseline": False,
        "measures_touched": ["W3_only"],
        "config_block": "welfare.stage4",
        "staged_reference": {
            "stem": wpr["staged_engine_ready_stem"],
            "staged_chunk_dir": str(staged_chunk_dir),
            "staged_priced_dir": str(staged_priced_dir)},
        "scratch_dir": str(scratch),
        "tol": TOL, "production_chunk_definitions": _CELL_CHUNK,
        "coverage": {
            "chunks_per_cell_tested": "one full production chunk per year x mode (singles c0 "
                                      "[0,101); couples c0 [0,150))",
            "couples_chunks_not_all_tested": "couples have 6 chunks/year; Four-B tests c0 only",
            "rationale": ("acceptable as a gate/smoke: Three-A established full-chunk determinism "
                          "at production scale (full chunk re-run reproduces staging to 0.0); "
                          "Four-B confirms the c0 band for every year. The V_i^dir runner MUST "
                          "reuse the full-chunk population-batch construction and must NOT "
                          "optimise down to draw sub-bands or isolated nodes."),
        },
        "task1_2_parity_grid": cells,
        "all_cells_pass": all_pass,
        "stopped_on_failure": stopped,
        "task3_readiness": {
            "population_faithful_and_ready_for_singles_vdir_gate": ready,
            "all_tested_cells_pass": all_pass,
            "carried_forward_vdir_constraints": carried_constraints,
            "note": ("READY licenses ONLY the singles V_i^dir gate-and-smoke as a SEPARATE "
                     "authorisation; this increment prices no redrawn node and computes no "
                     "V_i^dir."),
        },
        "scope_statement": (
            "Population-faithful existing-node parity gate against the staged welfare-pricing "
            "reference. Reprice output to a scratch dir only. No redrawn pricing, no V_i^dir, "
            "no W^3 promotion, no re-estimation, no production swap, no canonical promotion, no "
            "production overwrite. Nothing beyond W^3."),
    }
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"[four-B] ALL CELLS PASS={all_pass} stopped={stopped} "
          f"READY_for_singles_vdir={ready}")
    print(f"[four-B] wrote {args.out_json}")


if __name__ == "__main__":
    main()
