"""
Stage Two — Increment Two-N: full-scale validation of the staging rebuild (Tasks 2-4).

Reads the rebuilt staging chunks (scripts staging_twoN/), assembles them per (year, mode)
in draw order, and compares against the EXISTING stored production priced files:

  TASK 2 — full-scale HEADLINE PARITY gate. Per year x mode, on ALL rows AND on DECIDER
           rows separately (decider rows are estimator-facing), the 6 headline columns
           (ils_dispy/ils_origy/ils_ben/ils_tax/ils_sicdy + ils_dispy_real) must equal the
           stored production to machine tolerance. PASS requires decider-row parity; all-row
           parity is also reported. Couples reported explicitly.
  TASK 3 — full-scale COMPONENT COHERENCE gate on the rebuilt staging data: ils_ben identity,
           ils_dispy identity, draw-specificity, no stale carry-over. Violation counts per
           cell.
  TASK 4 — readiness: singles_ready / couples_ready / overall_ready_for_separate_swap.

READ-ONLY against production. DOES NOT swap/overwrite/move/delete any production parquet,
re-estimate, compute V_i^dir, price redrawn nodes, promote W^3, or touch any measure beyond
W^3.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from _bpool_paths import bpool_dir  # noqa: E402

HEADLINE = ["ils_dispy", "ils_origy", "ils_ben", "ils_tax", "ils_sicdy", "ils_dispy_real"]
TOL = 1e-6
_COUPLES_NCHUNKS = 6
_KEY = {"singles": ["stacked_hh_uid", "draw", "idperson_true"],
        "couples": ["stacked_hh_uid", "draw_joint", "draw_male", "draw_female",
                    "idperson_true"]}


def _assemble_staging(staging, year, mode):
    """Concatenate staged chunks for (year, mode) in chunk order (= draw order)."""
    n_chunks = 1 if mode == "singles" else _COUPLES_NCHUNKS
    parts = []
    for cid in range(n_chunks):
        p = staging / f"fr_p3a_bpool_priced__{year}__{mode}__c{cid}.parquet"
        if not p.exists():
            return None, f"missing staged chunk c{cid}"
        parts.append(pd.read_parquet(p))
    return pd.concat(parts, ignore_index=True), None


def _headline_parity(reb, prod, key, *, decider_only):
    left = reb
    right = prod
    if decider_only:
        left = left[left.get("ruro_decider", 1) == 1]
        right = right[right.get("ruro_decider", 1) == 1]
    cols = [c for c in HEADLINE if c in left.columns and c in right.columns]
    m = left[key + cols].merge(right[key + cols].drop_duplicates(key), on=key,
                               how="inner", suffixes=("_reb", "_prod"))
    res = {}
    ok = True
    for c in cols:
        d = np.abs(pd.to_numeric(m[f"{c}_reb"], errors="coerce").to_numpy()
                   - pd.to_numeric(m[f"{c}_prod"], errors="coerce").to_numpy())
        nbad = int(np.sum(d > TOL))
        res[c] = {"max_abs": float(np.nanmax(d)) if len(d) else 0.0, "n_above_tol": nbad}
        ok = ok and (nbad == 0)
    return {"ok": bool(ok), "n_rows_compared": int(len(m)), "per_column": res}


def _coherence(reb):
    dec = reb[reb.get("ruro_decider", 1) == 1]
    out = {}
    if all(c in dec.columns for c in ["ils_ben", "ils_pen", "ils_benmt", "ils_bennt"]):
        r = (dec["ils_ben"] - (dec["ils_pen"] + dec["ils_benmt"] + dec["ils_bennt"])).abs()
        out["ils_ben_identity_violations"] = int((r > TOL).sum())
        out["ils_ben_identity_max"] = float(r.max())
    if all(c in dec.columns for c in HEADLINE[:5]):
        r2 = (dec["ils_dispy"] - (dec["ils_origy"] - dec["ils_tax"] - dec["ils_sicdy"]
              + dec["ils_ben"])).abs()
        out["ils_dispy_identity_violations"] = int((r2 > TOL).sum())
        out["ils_dispy_identity_max"] = float(r2.max())
    # draw-specificity: components vary across draws where headline varies
    g = dec.groupby("stacked_hh_uid")
    out["share_hh_ils_ben_varies"] = round(float((g["ils_ben"].nunique() > 1).mean()), 4)
    if "ils_benmt" in dec:
        out["share_hh_ils_benmt_varies"] = round(
            float((g["ils_benmt"].nunique() > 1).mean()), 4)
    out["ok"] = (out.get("ils_ben_identity_violations", 1) == 0
                 and out.get("ils_dispy_identity_violations", 1) == 0)
    return out


def _no_stale_carryover(reb, prod, key):
    """Rebuilt ils_benmt should DIFFER from the stale stored production on a nontrivial
    share of rows (proof the component is now draw-specific, not carry-over)."""
    if "ils_benmt" not in reb.columns or "ils_benmt" not in prod.columns:
        return None
    m = reb[key + ["ils_benmt"]].merge(prod[key + ["ils_benmt"]].drop_duplicates(key),
                                       on=key, how="inner", suffixes=("_reb", "_prod"))
    chg = (pd.to_numeric(m["ils_benmt_reb"], errors="coerce")
           - pd.to_numeric(m["ils_benmt_prod"], errors="coerce")).abs()
    return {"n_rows": int(len(m)), "n_benmt_changed_vs_stale_production": int((chg > TOL).sum())}


def validate_cell(base, staging, year, mode):
    reb, err = _assemble_staging(staging, year, mode)
    if reb is None:
        return {"year": year, "mode": mode, "status": "BLOCKED", "reason": err}
    prod_path = base / f"fr_p3a_bpool_priced__{year}__{mode}.parquet"
    prod = pd.read_parquet(prod_path)
    key = _KEY[mode]

    t2_all = _headline_parity(reb, prod, key, decider_only=False)
    t2_dec = _headline_parity(reb, prod, key, decider_only=True)
    t3 = _coherence(reb)
    stale = _no_stale_carryover(reb, prod, key)

    return {"year": year, "mode": mode, "status": "OK",
            "rebuilt_rows": int(len(reb)), "production_rows": int(len(prod)),
            "rows_match": bool(len(reb) == len(prod)),
            "task2_headline_parity": {"all_rows": t2_all, "decider_rows": t2_dec},
            "task3_component_coherence": t3,
            "no_stale_carryover": stale}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--years", default="2015,2016,2017")
    args = ap.parse_args()

    base = bpool_dir()
    staging = base / "staging_twoN"
    years = [int(y) for y in args.years.split(",")]

    cells = {}
    for year in years:
        for mode in ["singles", "couples"]:
            cells[f"{year}__{mode}"] = validate_cell(base, staging, year, mode)

    def _cell_pass(c):
        # PASS = decider-row headline parity holds AND component coherence holds.
        return (c.get("status") == "OK"
                and c["task2_headline_parity"]["decider_rows"]["ok"]
                and c["task3_component_coherence"]["ok"])

    singles_cells = [c for c in cells.values() if c.get("mode") == "singles"]
    couples_cells = [c for c in cells.values() if c.get("mode") == "couples"]
    singles_ok = [c for c in singles_cells if c.get("status") == "OK"]
    couples_ok = [c for c in couples_cells if c.get("status") == "OK"]
    singles_ready = (len(singles_ok) == len(singles_cells) and bool(singles_ok)
                     and all(_cell_pass(c) for c in singles_ok))
    couples_ready = (len(couples_ok) == len(couples_cells) and bool(couples_ok)
                     and all(_cell_pass(c) for c in couples_ok))
    overall = bool(singles_ready and couples_ready)

    out = {"increment": "stage2_full_rebuild_staging_v1__validation",
           "no_welfare_finding": True, "measures_touched": ["W3_only"],
           "re_estimated": False, "computed_v_dir": False, "priced_redrawn_node": False,
           "production_parquet_swapped_or_overwritten_or_moved_or_deleted": False,
           "staging_dir": str(staging), "tol": TOL,
           "cells": cells,
           "singles_ready": singles_ready,
           "couples_ready": couples_ready,
           "overall_ready_for_separate_swap_authorisation": overall,
           "swap_performed": False,
           "scope_statement": (
               "Read-only full-scale validation of the staging rebuild. No production "
               "parquet swapped, overwritten, moved, or deleted. No re-estimation, no "
               "V_i^dir, no redrawn pricing, no W^3 finding, nothing beyond W^3. The swap "
               "of staging into production is a SEPARATE authorisation and was NOT done.")}
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"[two-N validation] wrote {args.out_json}")
    for lbl, c in cells.items():
        if c.get("status") != "OK":
            print(f"  {lbl}: {c['status']} ({c.get('reason')})")
            continue
        dec = c["task2_headline_parity"]["decider_rows"]
        allr = c["task2_headline_parity"]["all_rows"]
        t3 = c["task3_component_coherence"]
        print(f"  {lbl}: rows_match={c['rows_match']} | T2 decider_ok={dec['ok']} "
              f"all_ok={allr['ok']} | T3 coherence_ok={t3['ok']} "
              f"ben_viol={t3.get('ils_ben_identity_violations')} "
              f"benmt_varies={t3.get('share_hh_ils_benmt_varies')}")
    print(f"  singles_ready={singles_ready} couples_ready={couples_ready} "
          f"overall_ready_for_separate_swap={overall} (swap NOT performed)")


if __name__ == "__main__":
    main()
