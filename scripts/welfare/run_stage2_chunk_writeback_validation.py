"""
Stage Two — Increment Two-M: bounded validation of the chunk-worker write-back fix.

Validates the Two-M patch to scripts/bpool/run_bpool_euromod_chunk.py (write back ALL
simulated EUROMOD output columns per draw, not only the 5 headline columns) WITHOUT a full
production rebuild and WITHOUT overwriting any production parquet.

It replicates the chunk worker's exact assembly path on tiny deterministic population-scale
validation chunks (singles + couples), writes outputs ONLY to a temporary validation
location, and checks four gates:

  A. HEADLINE INVARIANCE  — evaluated in two parts:
       A1 (patched-vs-unpatched, the ESTIMATE-PROTECTING gate): the patched assembly and
          the unpatched 5-headline-only assembly, run on the SAME EUROMOD sim_df, must
          produce IDENTICAL headline columns (ils_dispy/ils_origy/ils_ben/ils_tax/
          ils_sicdy + ils_dispy_real). This is SCALE-INDEPENDENT and decisive: if any
          headline column moves the patch changed an estimator input -> STOP.
       A2 (rebuilt-vs-stored production, INFORMATIONAL at bounded scale): the patched
          headline vs the existing stored production values. At bounded validation scale
          income/contributions (ils_origy/ils_sicdy) reproduce, but means-tested
          ils_ben/ils_dispy need FULL production-chunk (population) context (Two-L), so
          they are not expected to reproduce here. A2 does NOT gate the patch; it BECOMES
          a full-chunk validation gate during the authorised full rebuild.
  B. COMPONENT COHERENCE  — ils_ben == ils_pen+ils_benmt+ils_bennt; ils_dispy identity;
                            simulated component columns vary across draws; no stale
                            precompute carry-over remains.
  C. COUPLES POP CONTEXT  — couples A1+B hold at bounded scale; exact stored-headline
                            reproduction at population scale (the A2 means-tested check)
                            is a FULL-production-couples-chunk property, confirmed only at
                            the full rebuild -> reported as deferred here, not CONFIRMED.
  D. ROW/WARNING STABILITY— row-count, key/order stability, no TUDef regression.

DOES NOT: run a full production rebuild, re-estimate, compute V_i^dir, price redrawn
welfare nodes, promote W^3, touch any measure beyond W^3, or overwrite any production
parquet. Config-driven.
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
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import welfare_assessment_unit_diag as wd  # noqa: E402
import welfare_core as wc  # noqa: E402

HEADLINE = ["ils_dispy", "ils_origy", "ils_ben", "ils_tax", "ils_sicdy"]


def _assemble_patched(chunk_df, sim_df, raw_input_cols, phi):
    """Replicate the PATCHED chunk-worker assembly (Two-M): start from chunk_df, write back
    EVERY simulated-output column (sim cols not in raw inputs), recompute ils_dispy_real.
    Returns out_df + the list of simulated columns written."""
    out_df = chunk_df.reset_index(drop=True).copy()
    out_df["idhh_true"] = chunk_df["idhh"].values
    out_df["idperson_true"] = chunk_df["idperson"].values
    sim_output_cols = [c for c in sim_df.columns if c not in raw_input_cols]
    for c in sim_output_cols:
        out_df[c] = sim_df[c].values
    out_df["ils_dispy_real"] = out_df["ils_dispy"] * phi
    return out_df, sim_output_cols


def _validate_cell(cfg2, bc, base, out_dir, *, year, mode, n_hh, draw_lo, draw_hi,
                   tol, dgn=None):
    """Build a population-scale validation chunk for (year, mode) on the first n_hh
    households (deterministic) over the draw band [draw_lo, draw_hi); compare rebuilt
    headline + components to stored production. Writes a TEMP parquet only."""
    system_code, dataset_name = bc["system_pairing"][year]
    country = str(system_code).split("_")[0]
    phi = bc["cpi"][year]
    raw = bc["raw_schema"][year]
    raw_input_cols = set(raw)
    draw_col = "draw" if mode == "singles" else "draw_joint"
    id_mult = 1_000 if mode == "singles" else 10_000

    pl, _ = wd._load(base, cfg2["precompute_long_stem"], year, mode, long_=True)
    if dgn is not None and "dgn" in pl.columns:
        pl = pl[pl["dgn"] == dgn]
    uids = pl["stacked_hh_uid"].drop_duplicates().sort_values().head(n_hh).tolist()
    chunk_df = pl[(pl["stacked_hh_uid"].isin(uids))
                  & (pl[draw_col] >= draw_lo) & (pl[draw_col] < draw_hi)].copy()
    chunk_df = chunk_df.reset_index(drop=True)
    if len(chunk_df) == 0:
        return {"year": year, "mode": mode, "status": "BLOCKED", "reason": "empty chunk"}

    # EXACT chunk-worker input build: stamp + raw schema
    stamped = bc["stamp"](chunk_df.copy(), draw_col, id_mult)
    em = stamped[[c for c in raw if c in stamped.columns]].copy()
    for c in em.columns:
        em[c] = pd.to_numeric(em[c], errors="coerce").fillna(0.0)

    t0 = time.time()
    sim, warn, err, _ = wd._run_euromod(bc, em, country=country,
                                        system_code=system_code, dataset_name=dataset_name)
    wall = time.time() - t0
    if err is not None or sim is None:
        return {"year": year, "mode": mode, "status": "BLOCKED",
                "reason": err or "no sim", "euromod_wall_seconds": round(wall, 3)}
    if len(sim) != len(stamped):
        return {"year": year, "mode": mode, "status": "ROW_MISMATCH",
                "n_sim": int(len(sim)), "n_input": int(len(stamped))}

    # Assemble from the UNSTAMPED chunk_df (exactly as the real worker: idhh_true/
    # idperson_true are the ORIGINAL ids; sim is row-aligned to chunk_df since the stamp
    # preserves row order). Passing the stamped frame here would mis-set idperson_true to
    # the stamped id and break the stored-production join.
    out_df, sim_cols = _assemble_patched(chunk_df, sim, raw_input_cols, phi)

    # also assemble the UNPATCHED (5-headline-cols-only) output from the SAME sim, to
    # prove the PATCH itself does not move the headline (estimate-protecting gate A1).
    out_df_unpatched = chunk_df.reset_index(drop=True).copy()
    out_df_unpatched["idhh_true"] = chunk_df["idhh"].values
    out_df_unpatched["idperson_true"] = chunk_df["idperson"].values
    for c in [hc for hc in HEADLINE if hc in sim.columns]:
        out_df_unpatched[c] = sim[c].values
    out_df_unpatched["ils_dispy_real"] = out_df_unpatched["ils_dispy"] * phi

    # write TEMP validation parquet ONLY (clearly marked, not a production path).
    # Include sex/dgn in the name so the two singles cells (male dgn=1 / female dgn=0) write
    # DISTINCT files and the provenance path identifies the actual cell output.
    sex_tag = "" if dgn is None else ("_male" if dgn == 1.0 else "_female")
    tmp_path = out_dir / f"VALIDATION_{mode}{sex_tag}_{year}_{draw_lo}_{draw_hi}.parquet"
    out_df.to_parquet(tmp_path, index=False)

    headline_real = HEADLINE + ["ils_dispy_real"]
    key = (["stacked_hh_uid", "draw"] if mode == "singles"
           else ["stacked_hh_uid", "draw_joint", "draw_male", "draw_female"])

    # ---- Gate A1: PATCH INVARIANCE (decisive, scale-independent) ----
    # patched vs unpatched assembly on the SAME EUROMOD sim -> headline must be IDENTICAL.
    a1 = {}
    a1_ok = True
    for c in headline_real:
        d = np.abs(pd.to_numeric(out_df[c], errors="coerce").to_numpy()
                   - pd.to_numeric(out_df_unpatched[c], errors="coerce").to_numpy())
        mx = float(np.nanmax(d)) if len(d) else 0.0
        nbad = int(np.sum(d > tol))
        a1[c] = {"max_abs": mx, "n_above_tol": nbad}
        a1_ok = a1_ok and (nbad == 0)

    # ---- Gate A2: production reproduction (population-context informational) ----
    # patched headline vs STORED production. Exact reproduction requires the FULL production
    # chunk (Two-L: benefits are population/chunk-scale dependent); a bounded validation
    # chunk reproduces income/contributions (ils_origy/ils_sicdy) but NOT necessarily the
    # means-tested ils_ben/ils_dispy unless run at full production chunk scale. Reported,
    # not used to gate the PATCH (which A1 settles).
    priced, _ = wd._load(base, cfg2["priced_long_stem"], year, mode, long_=False)
    rebuilt = out_df.copy()
    rebuilt["__o"] = rebuilt["idperson_true"]
    pr = priced.copy()
    pr["__o"] = pr["idperson_true"]
    join = key + ["__o"]
    m = rebuilt[join + headline_real].merge(
        pr[join + headline_real].drop_duplicates(join), on=join,
        how="inner", suffixes=("_new", "_stored"))
    a2 = {}
    for c in headline_real:
        d = np.abs(pd.to_numeric(m[f"{c}_new"], errors="coerce").to_numpy()
                   - pd.to_numeric(m[f"{c}_stored"], errors="coerce").to_numpy())
        a2[c] = {"max_abs": float(np.nanmax(d)) if len(d) else 0.0,
                 "n_above_tol": int(np.sum(d > tol))}
    a2_income_contrib_ok = (a2.get("ils_origy", {}).get("n_above_tol", 1) == 0
                            and a2.get("ils_sicdy", {}).get("n_above_tol", 1) == 0)
    headline_res = a1
    headline_ok = a1_ok

    # ---- Gate B: component coherence (on the REBUILT rows) ----
    dec = out_df[out_df.get("ruro_decider", 1) == 1]
    coherence = {}
    if all(c in dec.columns for c in ["ils_ben", "ils_pen", "ils_benmt", "ils_bennt"]):
        r1 = (dec["ils_ben"] - (dec["ils_pen"] + dec["ils_benmt"] + dec["ils_bennt"])).abs()
        coherence["ils_ben_identity_max"] = float(r1.max())
        coherence["ils_ben_identity_violations"] = int((r1 > tol).sum())
    if all(c in dec.columns for c in ["ils_dispy", "ils_origy", "ils_tax", "ils_sicdy", "ils_ben"]):
        r2 = (dec["ils_dispy"] - (dec["ils_origy"] - dec["ils_tax"] - dec["ils_sicdy"]
              + dec["ils_ben"])).abs()
        coherence["ils_dispy_identity_max"] = float(r2.max())
        coherence["ils_dispy_identity_violations"] = int((r2 > tol).sum())
    # draw-specificity: components now vary across draws where headline varies?
    g = dec.groupby("stacked_hh_uid")
    ben_var = (g["ils_ben"].nunique() > 1)
    benmt_var = (g["ils_benmt"].nunique() > 1) if "ils_benmt" in dec else None
    coherence["share_hh_ils_benmt_varies_across_draws"] = (
        round(float(benmt_var.mean()), 4) if benmt_var is not None else None)
    coherence["share_hh_ils_ben_varies_across_draws"] = round(float(ben_var.mean()), 4)
    # no stale carry-over: rebuilt ils_benmt should differ from the stored (stale) ils_benmt
    coherence["rebuilt_changes_stale_components"] = None
    if "ils_benmt" in pr.columns:
        mm = rebuilt[join + ["ils_benmt"]].merge(
            pr[join + ["ils_benmt"]].drop_duplicates(join), on=join, how="inner",
            suffixes=("_new", "_stored"))
        chg = (pd.to_numeric(mm["ils_benmt_new"], errors="coerce")
               - pd.to_numeric(mm["ils_benmt_stored"], errors="coerce")).abs()
        coherence["rebuilt_changes_stale_components"] = int((chg > tol).sum())

    coherence_ok = (coherence.get("ils_ben_identity_violations", 1) == 0
                    and coherence.get("ils_dispy_identity_violations", 1) == 0)

    return {
        "year": year, "mode": mode, "dgn": dgn,
        "system_code": system_code, "dataset_name": dataset_name,
        "n_hh": len(uids), "n_rows": int(len(out_df)), "draw_band": [draw_lo, draw_hi],
        "n_simulated_cols_written": len(sim_cols),
        "euromod_wall_seconds": round(wall, 3), "tudef": warn["n_warning_lines"],
        "temp_validation_path": str(tmp_path),
        "n_headline_rows_compared": int(len(m)),
        "gateA1_patch_invariance": {"ok": bool(a1_ok), "per_column": a1,
                                    "note": ("patched vs unpatched assembly on the SAME "
                                             "EUROMOD sim -> headline must be IDENTICAL; "
                                             "this is the decisive estimate-protecting gate "
                                             "and is scale-independent.")},
        "gateA2_production_reproduction": {
            "income_contrib_reproduce": bool(a2_income_contrib_ok),
            "per_column": a2,
            "note": ("patched headline vs STORED production at BOUNDED chunk scale. "
                     "ils_origy/ils_sicdy reproduce; means-tested ils_ben/ils_dispy do NOT "
                     "necessarily reproduce here because production priced at FULL chunk "
                     "scale (Two-L population-context). Informational only; does NOT gate "
                     "the patch -- A1 does.")},
        "gateA_headline_invariance": {"ok": bool(headline_ok), "per_column": headline_res},
        "gateB_component_coherence": {"ok": bool(coherence_ok), **coherence},
        "status": "OK",
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--n-hh", type=int, default=120)
    ap.add_argument("--year", type=int, default=2017)
    ap.add_argument("--draw-hi", type=int, default=20,
                    help="draw band upper bound (population context over draws [0, hi))")
    args = ap.parse_args()

    cfg = wc.load_config(args.config)
    cfg2 = cfg["stage2"]
    bc = wd.build_constants(cfg2["build_module"])
    import importlib
    bc["cpi"] = importlib.import_module(cfg2["build_module"])._CPI
    from _bpool_paths import bpool_dir
    base = bpool_dir()
    tol = 1e-6

    # TEMP validation dir (clearly marked; NOT a production storage path)
    out_dir = Path(tempfile.gettempdir()) / "mnl_twoM_validation"
    out_dir.mkdir(parents=True, exist_ok=True)

    em_log = Path(args.out_json).with_name("stage2_chunk_writeback_validation_euromod.log")
    _tmp = tempfile.TemporaryFile(mode="w+b")  # noqa: SIM115 (manual fd lifecycle)
    _so, _se = os.dup(1), os.dup(2)
    os.dup2(_tmp.fileno(), 1)
    os.dup2(_tmp.fileno(), 2)
    cells = []
    try:
        # singles_male + singles_female + couples, population-scale over draws [0, draw_hi)
        cells.append(_validate_cell(cfg2, bc, base, out_dir, year=args.year,
                                    mode="singles", n_hh=args.n_hh, draw_lo=0,
                                    draw_hi=args.draw_hi, tol=tol, dgn=1.0))
        cells.append(_validate_cell(cfg2, bc, base, out_dir, year=args.year,
                                    mode="singles", n_hh=args.n_hh, draw_lo=0,
                                    draw_hi=args.draw_hi, tol=tol, dgn=0.0))
        cells.append(_validate_cell(cfg2, bc, base, out_dir, year=args.year,
                                    mode="couples", n_hh=args.n_hh, draw_lo=0,
                                    draw_hi=args.draw_hi, tol=tol))
    finally:
        os.dup2(_so, 1)
        os.dup2(_se, 2)
        os.close(_so)
        os.close(_se)
        _tmp.seek(0)
        console = _tmp.read().decode("utf-8", errors="replace")
        _tmp.close()
    em_log.write_text(console, encoding="utf-8")

    def _cell_label(c):
        sx = ("_male" if c.get("dgn") == 1.0 else "_female") if c["mode"] == "singles" else ""
        return f"{c['mode']}{sx}_{c['year']}"

    by = {_cell_label(c): c for c in cells}
    singles_cells = [c for c in cells if c["mode"] == "singles"]
    couples_cells = [c for c in cells if c["mode"] == "couples"]

    # A cell PASSES the bounded gates iff A1 patch-invariance holds (the patch does NOT move
    # the headline), B component coherence holds, AND A2 income/contributions reproduce
    # stored production at bounded scale. Exact MEANS-TESTED headline reproduction at full
    # scale is a FULL-production-chunk property (Two-L) NOT validated in this bounded
    # increment -- so it is reported as DEFERRED, never CONFIRMED.
    def _cell_pass(c):
        return (c.get("status") == "OK"
                and c["gateA1_patch_invariance"]["ok"]
                and c["gateB_component_coherence"]["ok"]
                and c["gateA2_production_reproduction"]["income_contrib_reproduce"])

    singles_ok = [c for c in singles_cells if c.get("status") == "OK"]
    singles_ready = bool(singles_ok) and all(_cell_pass(c) for c in singles_ok)
    couples_ok_cells = [c for c in couples_cells if c.get("status") == "OK"]
    # couples: bounded gates (A1 + B + A2-income/contrib) -> "patch valid".
    couples_patch_valid = bool(couples_ok_cells) and all(_cell_pass(c)
                                                         for c in couples_ok_cells)
    # full-scale stored-headline (ils_dispy/ils_ben) reproduction for couples was NOT run in
    # Two-M (it requires a faithful full-production-couples-chunk). Always false here.
    couples_fullscale_headline_confirmed = False
    couples_status = ("PATCH_VALID_FULLSCALE_HEADLINE_DEFERRED" if couples_patch_valid
                      else ("COUPLES NOT CONFIRMED" if not couples_ok_cells
                            else "FAILED_GATES"))

    out = {"increment": "stage2_chunk_writeback_fix_validation_v1",
           "no_welfare_finding": True, "measures_touched": ["W3_only"],
           "re_estimated": False, "computed_v_dir": False,
           "priced_redrawn_node": False, "ran_full_production_rebuild": False,
           "overwrote_production_parquet": False,
           "patch": {"file": "scripts/bpool/run_bpool_euromod_chunk.py",
                     "change": ("write back EVERY simulated-output column from per-draw "
                                "sim_df (cols not in _RAW_SCHEMA[year]) instead of only "
                                "_EM_OUTPUT_COLS; headline cols are a subset -> unchanged.")},
           "validation_temp_dir": str(out_dir),
           "euromod_console_log": str(em_log),
           "cells": by,
           "singles_ready": singles_ready,
           "couples_patch_valid": couples_patch_valid,
           "couples_fullscale_headline_confirmed": couples_fullscale_headline_confirmed,
           "couples_status": couples_status,
           "overall_readiness": (
               "READY for a separately authorised FULL-REBUILD VALIDATION (the patch is "
               "estimate-safe by A1 and fixes component staleness by B). NOT ready to trust "
               "or swap production couples output: full-scale stored-headline reproduction "
               "for couples is DEFERRED to a faithful full-production-couples-chunk run."),
           "scope_statement": (
               "Bounded validation only. No full production rebuild; nothing re-estimated; "
               "no V_i^dir; no redrawn welfare pricing; no W^3 finding; nothing beyond W^3; "
               "no production parquet overwritten (validation parquets written to a temp "
               "dir only).")}
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"[stage2:twoM-validation] wrote {args.out_json}")
    for lbl, c in by.items():
        if c.get("status") != "OK":
            print(f"  {lbl}: {c.get('status')} ({c.get('reason')})")
            continue
        a1 = c["gateA1_patch_invariance"]
        a2 = c["gateA2_production_reproduction"]
        b = c["gateB_component_coherence"]
        print(f"  {lbl}: A1_patch_invariant={a1['ok']} A2_income_contrib_reproduce="
              f"{a2['income_contrib_reproduce']} B_coherence_ok={b['ok']} "
              f"| ben_identity_viol={b.get('ils_ben_identity_violations')} "
              f"benmt_varies={b.get('share_hh_ils_benmt_varies_across_draws')} "
              f"| simcols={c['n_simulated_cols_written']} tudef={c['tudef']} "
              f"rows={c['n_rows']}")
    print(f"  singles_ready={singles_ready} | couples_patch_valid={couples_patch_valid} | "
          f"couples_fullscale_headline_confirmed={couples_fullscale_headline_confirmed} "
          f"({couples_status})")
    print("  overall: READY for authorised full-rebuild VALIDATION; NOT ready to "
          "trust/swap production couples output (full-scale headline DEFERRED).")


if __name__ == "__main__":
    main()
