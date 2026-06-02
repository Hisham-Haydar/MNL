"""
Welfare Stage Two — Increment Two-D: bounded node-pricing EUROMOD re-simulation
FEASIBILITY probe (existing nodes only). Feasibility-only source; prices NO redrawn
node, computes NO V_i^dir, writes NO storage/precompute/priced parquet.

WHY THIS IS MATERIALLY DIFFERENT FROM THE FAILED TWO-B PATH (the concrete, testable
input difference, named per Task 1):

  Two-B `_reprice_cell` reads its EUROMOD input rows from the PRICED file and selects
  a tiny subset with `groupby(stacked_hh_uid).head(rows_per_hh)`. The bpool rows are a
  HOUSEHOLD ROSTER: each (stacked_hh_uid, draw) carries every household member
  (decider + children + partner), one row per idperson; the unique key is
  (stacked_hh_uid, draw, idperson). `head(20)` slices by ROW COUNT, so for a
  multi-person household it can cut a draw's roster mid-way — e.g. it keeps the
  decider and one child of a 3-person household at draw 6 but drops the second child
  (which would be row 20). EUROMOD then computes that draw against an INCOMPLETE
  household, so household-level means-tested benefits (child benefits, housing AL,
  RSA) are wrong -> ils_ben diverges.

  Two-D instead (a) reads EUROMOD input from the PRECOMPUTE-LONG file (the build's own
  EUROMOD input source, never the priced OUTPUT), and (b) selects WHOLE HOUSEHOLDS at
  ROSTER-COMPLETE granularity: for the chosen households it takes ALL idperson rows
  for a bounded set of draws, so every (hh, draw) fed to EUROMOD has its FULL roster.
  This is the specific mechanism by which Two-D could re-derive ils_ben correctly
  where Two-B could not: EUROMOD sees complete tax units / households.

  It also keeps the build's exact node-dependent earnings fields (lhw, yivwg, yem,
  yem00, yemxp, yem_hour, yemmy, lunmy and partner analogues) as stored in
  precompute-long (these ARE the production node values for existing nodes), and feeds
  EUROMOD only raw_schema input columns -- never *_s / ils_* / tax-benefit OUTPUTS as
  inputs.

PARITY TARGET: the stored priced `ils_dispy` (+ components) on the DECIDER rows, since
those are the rows the welfare core consumes. For couples, also the household-joint
summed disposable income.

No W^3 welfare finding; no measure beyond W^3.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
import numpy as np
import pandas as pd
import pyarrow.parquet as pq


def _build_constants(build_module):
    import importlib
    mod = importlib.import_module(build_module)
    return {"system_pairing": mod._SYSTEM_PAIRING, "cpi": mod._CPI,
            "raw_schema": mod._RAW_SCHEMA, "em_output_cols": mod._EM_OUTPUT_COLS,
            "EuromodRunner": mod.EuromodRunner, "em_root": mod._EM_ROOT,
            "stamp": mod._stamp_draw_ids}


def resim_cell(cfg2, bc, *, year, mode, n_hh, max_draws, components, country_override):
    """Existing-node re-simulation parity for one year x mode cell, Two-D path:
    precompute-long source + roster-complete household selection."""
    from _bpool_paths import bpool_dir
    base = bpool_dir()
    if year not in bc["system_pairing"]:
        return {"year": year, "mode": mode, "status": "BLOCKED",
                "reason": f"year {year} not in build system pairing"}
    system_code, dataset_name = bc["system_pairing"][year]
    country = str(country_override or str(system_code).split("_")[0])
    raw_cols = bc["raw_schema"][year]
    draw_col = "draw" if mode == "singles" else "draw_joint"
    id_mult = 1_000 if mode == "singles" else 10_000

    precomp = base / f"{cfg2['precompute_long_stem']}__{year}__{mode}__long.parquet"
    priced = base / f"{cfg2['priced_long_stem']}__{year}__{mode}.parquet"
    if not precomp.exists() or not priced.exists():
        return {"year": year, "mode": mode, "status": "BLOCKED",
                "reason": f"precompute/priced absent ({precomp.exists()}/{priced.exists()})"}

    # choose the SAME first n_hh households as Two-B (deterministic), then take their
    # WHOLE rosters for the first max_draws draws -> roster-complete by construction.
    pl = pq.ParquetFile(precomp).read().to_pandas()
    hh_col = "stacked_hh_uid"
    uids = pl[hh_col].drop_duplicates().head(n_hh).tolist()
    draws = sorted(pl[pl[hh_col].isin(uids)][draw_col].unique())[:max_draws]
    sel = pl[(pl[hh_col].isin(uids)) & (pl[draw_col].isin(draws))].copy()
    # roster integrity check: every (hh,draw) keeps all its idperson rows from pl
    full_n = pl[pl[hh_col].isin(uids)].groupby([hh_col, draw_col]).size()
    sel_n = sel.groupby([hh_col, draw_col]).size()
    roster_complete = bool((sel_n.reindex(sel_n.index) == full_n.reindex(sel_n.index)).all())

    # build EUROMOD input from raw schema only (no *_s / ils_* fed back)
    stamped = bc["stamp"](sel.copy(), draw_col, id_mult)
    em = stamped[[c for c in raw_cols if c in stamped.columns]].copy()
    for c in em.columns:
        em[c] = pd.to_numeric(em[c], errors="coerce").fillna(0.0)

    t0 = time.time()
    # NOTE: EUROMOD assessment-unit (TUDef) warnings are captured RELIABLY at the
    # RUNNER level (process fd 1/2 redirect in run_stage2_resim.py), because the native
    # engine writes them to the process console (fd 1), which a per-cell in-Python
    # fd-2 redirect misses. Do not attempt per-cell capture here.
    try:
        runner = bc["EuromodRunner"](bc["em_root"])
        sim = runner.run_on_dataframe(em, country=country, system_code=system_code,
                                      dataset_name=dataset_name)
    except Exception as e:
        return {"year": year, "mode": mode, "status": "BLOCKED",
                "reason": f"EUROMOD run failed: {type(e).__name__}: {e}"}
    wall = time.time() - t0
    if "ils_dispy" not in sim.columns or len(sim) != len(sel):
        return {"year": year, "mode": mode, "status": "BLOCKED",
                "reason": f"EUROMOD output shape/cols mismatch (out={sim.shape}, in={len(sel)})"}

    # attach repriced outputs back to the selected rows
    out_cols = ["ils_dispy"] + [c for c in components if c in sim.columns]
    for c in out_cols:
        sel[f"__rep_{c}"] = pd.to_numeric(sim[c], errors="coerce").values

    # compare ONLY on decider rows against the stored priced values for the same key
    pr = pq.ParquetFile(priced).read_row_group(0).to_pandas()
    key = [hh_col, draw_col, "idperson"]
    storedcols = ["ils_dispy"] + [c for c in components if c in pr.columns]
    prk = pr[key + storedcols].drop_duplicates(key)
    dec = sel[sel.get("ruro_decider", 1) == 1] if "ruro_decider" in sel else sel
    m = dec[key + [f"__rep_{c}" for c in out_cols]].merge(prk, on=key, how="inner")
    tol = float(cfg2["resim"]["tol"])

    comp_div = {}
    for c in out_cols:
        if c in m.columns:
            d = np.abs(pd.to_numeric(m[f"__rep_{c}"], errors="coerce").to_numpy()
                       - pd.to_numeric(m[c], errors="coerce").to_numpy())
            comp_div[c] = {"n_above_tol": int(np.sum(d > tol)), "max_abs": float(np.nanmax(d))}
    dd = np.abs(pd.to_numeric(m["__rep_ils_dispy"], errors="coerce").to_numpy()
                - pd.to_numeric(m["ils_dispy"], errors="coerce").to_numpy())
    n_bad = int(np.sum(dd > tol))
    status = "PASS" if (float(np.nanmax(dd)) <= tol
                        and comp_div.get("ils_ben", {}).get("n_above_tol", 1) == 0) else "FAIL"

    cell = {"year": year, "mode": mode, "country": country, "system_code": system_code,
            "n_decider_rows_matched": int(len(m)),
            "n_hh": int(len(uids)), "n_draws": int(len(draws)),
            "roster_complete": roster_complete,
            "ils_dispy": {"max_abs_diff": float(np.nanmax(dd)),
                          "median_abs_diff": float(np.nanmedian(dd)),
                          "n_rows_above_tol": n_bad},
            "component_divergence": comp_div,
            "euromod_wall_seconds": round(wall, 3),
            "n_euromod_input_rows": int(len(em)),
            "status": status}

    if mode == "couples":
        m2 = dec[key + ["__rep_ils_dispy"]].merge(
            pr[key + ["ils_dispy"]].drop_duplicates(key), on=key, how="inner")
        g = m2.groupby([hh_col, draw_col])
        jrep = g["__rep_ils_dispy"].sum().to_numpy()
        jst = g["ils_dispy"].sum().to_numpy()
        jd = np.abs(jrep - jst)
        cell["household_joint_dispy"] = {"n_alternatives": int(len(jd)),
                                         "max_abs_diff": float(np.nanmax(jd)),
                                         "n_above_tol": int(np.sum(jd > tol))}
    if status != "PASS":
        # localise over TRUE components only (ils_origy/ils_ben/ils_tax/ils_sicdy),
        # never the aggregate ils_dispy (which is the sum, not a component).
        true_comps = [c for c in components if c in comp_div]
        bcomp = (max(true_comps, key=lambda c: comp_div[c]["max_abs"])
                 if true_comps else None)
        cell["failure_localised_to"] = bcomp
        cell["still_benefit_localised"] = (bcomp == "ils_ben")
    return cell


def resim_grid(cfg2):
    bc = _build_constants(cfg2["build_module"])
    rs = cfg2["resim"]
    cells = {}
    for year in cfg2["years"]:
        for mode in cfg2["modes"]:
            cells[f"{year}__{mode}"] = resim_cell(
                cfg2, bc, year=year, mode=mode, n_hh=int(rs["n_hh"]),
                max_draws=int(rs["max_draws"]), components=list(rs["components"]),
                country_override=rs.get("country_override"))
    all_pass = all(c.get("status") == "PASS" for c in cells.values())
    return {"all_cells_pass": all_pass, "cells": cells}
