"""
Stage Two — Increment Two-E runner: assessment-unit / ID-stamping DIAGNOSTIC ladder.

Runs the Rung 1-3 ladder (and optional Rung 4) on two deterministic existing-node
cases (one singles benefit-recipient HH with a dependent child; one couples HH with
TUDef-relevant partner structure), persists a provenance JSON + EUROMOD console log,
and prints a per-rung summary.

DIAGNOSTIC ONLY. Prices no redrawn node; computes no V_i^dir; runs no 2x/4x growth;
promotes no W^3; touches no measure beyond W^3; writes no storage/precompute/priced/
chunk parquet. No W^3 welfare finding is produced.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import welfare_assessment_unit_diag as wd  # noqa: E402
import welfare_core as wc  # noqa: E402


def _rung4_alt_keying(cfg2, case_cfg, mode, hh_uid, components, tol, country_override):
    """OPTIONAL Rung 4 — relationship-preserving alternative in-memory keying,
    DIAGNOSTIC ONLY. Only invoked when Rungs 1-2 PASS and Rung 3 FAILS. Makes each
    node's person IDs globally unique by node index WHILE preserving every
    within-household relationship (idpartner/idfather/idmother remapped consistently),
    then runs the same nodes in one batch. NOT production-ready; not used to price
    redrawn nodes."""
    import numpy as np
    import pandas as pd
    bc = wd.build_constants(cfg2["build_module"])
    from _bpool_paths import bpool_dir
    base = bpool_dir()
    year = cfg2["assessment_unit_diag"]["year"]
    system_code, dataset_name = bc["system_pairing"][year]
    country = str(country_override or str(system_code).split("_")[0])
    raw_cols = bc["raw_schema"][year]
    key = wd._node_key(mode)
    pl, _ = wd._load(base, cfg2["precompute_long_stem"], year, mode, long_=True)
    priced, _ = wd._load(base, cfg2["priced_long_stem"], year, mode, long_=False)
    nodes = wd.select_node_block(pl, mode, hh_uid, n_nodes=case_cfg["n_nodes"])

    # Required relationship fields. If any kinship field referenced is itself
    # ambiguous (e.g. an idpartner pointing outside the node roster), STOP.
    kin = [c for c in ("idpartner", "idfather", "idmother") if c in pl.columns]
    frames = []
    for i, (_, rows) in enumerate(nodes):
        r = rows.copy().reset_index(drop=True)
        roster_ids = set(pd.to_numeric(r["idperson"], errors="coerce").astype("Int64"))
        for kc in kin:
            ref = pd.to_numeric(r[kc], errors="coerce").fillna(0).astype("Int64")
            unresolved = [int(v) for v in ref.unique()
                          if v != 0 and v not in roster_ids]
            if unresolved:
                return {"status": "STOP",
                        "reason": (f"ambiguous relationship field {kc}: references "
                                   f"{unresolved} not in node roster; cannot remap "
                                   "consistently — STOP per spec."),
                        "node_index": i}
        # offset every id in this node by a node-unique block; remap kinship too
        off = (i + 1) * 1_000_000_000
        r["idperson"] = pd.to_numeric(r["idperson"], errors="coerce").astype("Int64") + off
        r["idhh"] = pd.to_numeric(r["idhh"], errors="coerce").astype("Int64") + off
        for kc in kin:
            ref = pd.to_numeric(r[kc], errors="coerce").fillna(0).astype("Int64")
            r[kc] = np.where(ref == 0, 0, ref + off)
        frames.append((rows, r))
    batch_orig = pd.concat([o for o, _ in frames], ignore_index=True)
    batch_keyed = pd.concat([k for _, k in frames], ignore_index=True)
    em = wd._em_input(batch_keyed, raw_cols)
    sim, warn, err, _ = wd._run_euromod(bc, em, country=country,
                                        system_code=system_code,
                                        dataset_name=dataset_name)
    if err is not None:
        return {"status": "BLOCKED", "reason": err, "tudef": warn}
    # compare on ORIGINAL ids (batch_orig carries the un-offset idperson, aligned
    # row-for-row with the offset batch fed to EUROMOD)
    comp, joint, n = wd._compare(sim, batch_orig, priced, key, components, tol)
    return {"status": wd._status(comp, tol),
            "scheme": "node_offset_relationship_preserving",
            "n_decider_matched": n, "components": comp, "joint_dispy": joint,
            "tudef": warn, "localised_to": wd._localise(comp, components),
            "note": ("DIAGNOSTIC ONLY: not production-ready; not used to price "
                     "redrawn nodes.")}


def _stamping_collision_evidence(cfg2, mode, hh_uid, n_nodes):
    """Read-only: for the selected node block, count how many DISTINCT stored nodes
    collapse to the SAME production-stamped idperson (idperson*id_mult + draw_col).
    Singles stamp on `draw` (unique per node) -> no collision; couples stamp on
    `draw_joint`, which can pack >1 (draw_male,draw_female) alternative -> collision.
    This makes the report's central mechanism reproducible without a welfare finding."""
    from _bpool_paths import bpool_dir
    base = bpool_dir()
    year = cfg2["assessment_unit_diag"]["year"]
    draw_col = "draw" if mode == "singles" else "draw_joint"
    id_mult = 1_000 if mode == "singles" else 10_000
    pl, _ = wd._load(base, cfg2["precompute_long_stem"], year, mode, long_=True)
    nodes = wd.select_node_block(pl, mode, hh_uid, n_nodes=n_nodes)
    key = wd._node_key(mode)
    n_distinct_nodes = len(nodes)
    # stamped idperson for the FIRST decider of each node
    stamped_ids, node_tuples = [], []
    for nd, rows in nodes:
        dec = rows[rows.get("ruro_decider", 1) == 1] if "ruro_decider" in rows else rows
        if len(dec) == 0:
            continue
        idp = int(float(dec.iloc[0]["idperson"]))
        dv = int(nd[draw_col])
        stamped_ids.append(idp * id_mult + dv)
        node_tuples.append(tuple(int(nd[k]) for k in key))
    n_distinct_stamped = len(set(stamped_ids))
    return {"node_key": key, "stamp_on": draw_col, "id_mult": id_mult,
            "n_distinct_nodes_selected": n_distinct_nodes,
            "n_distinct_stamped_first_decider_ids": n_distinct_stamped,
            "stamping_collision_present": n_distinct_stamped < len(stamped_ids),
            "n_colliding_nodes": len(stamped_ids) - n_distinct_stamped}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-json", required=True)
    args = ap.parse_args()

    cfg = wc.load_config(args.config)
    cfg2 = cfg["stage2"]
    diag = cfg2["assessment_unit_diag"]
    components = list(diag["components"])
    tol = float(diag["tol"])
    cov = diag.get("country_override")

    cases = diag["cases"]
    out = {"increment": "stage2_assessment_unit_diagnosis_v1",
           "no_welfare_finding": True, "measures_touched": ["W3_only"],
           "no_production_pricing": True, "diagnostic_only": True,
           "node_key_correction": (
               "Couples node key is (stacked_hh_uid, draw_joint, draw_male, "
               "draw_female); draw_joint ALONE (as Two-D used) packs multiple stacked "
               "alternatives with colliding idperson. Singles node key is "
               "(stacked_hh_uid, draw), already a clean roster."),
           "year": diag["year"], "tol": tol, "components": components,
           "cases": {}}

    for label, cc in cases.items():
        res = wd.run_ladder(cfg2, mode=cc["mode"], hh_uid=int(cc["hh_uid"]),
                            n_nodes=int(cc["n_nodes"]), components=components,
                            tol=tol, country_override=cov)
        # Rung 4 only if Rungs 1 & 2 PASS and Rung 3 FAILS.
        r1 = res.get("rung1", {}).get("status")
        r2 = res.get("rung2", {}).get("status")
        r3 = res.get("rung3", {}).get("status")
        if r1 == "PASS" and r2 == "PASS" and r3 == "FAIL":
            res["rung4"] = _rung4_alt_keying(cfg2, cc, cc["mode"],
                                             int(cc["hh_uid"]), components, tol, cov)
        else:
            res["rung4"] = {"status": "SKIPPED",
                            "reason": "only run when Rung1&2 PASS and Rung3 FAIL; "
                                      f"observed r1={r1} r2={r2} r3={r3}"}
        res["stamping_collision_evidence"] = _stamping_collision_evidence(
            cfg2, cc["mode"], int(cc["hh_uid"]), int(cc["n_nodes"]))
        out["cases"][label] = res

    out["scope_statement"] = (
        "No W^3 welfare finding is produced and no measure beyond W^3 is touched. "
        "EUROMOD was run only on tiny EXISTING-node diagnostic subsets; NO "
        "PRODUCTION/REDRAWN node was priced, no V_i^dir computed, no 2x/4x growth run, "
        "no storage/precompute/priced/chunk parquet written. Any rung PASS does NOT "
        "unblock production: redrawn-node pricing still requires a separately "
        "authorised per-node EUROMOD path and a parity-passing batching/keying scheme.")

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"[stage2:audiag] wrote {args.out_json}")
    for label, res in out["cases"].items():
        if res.get("status") == "BLOCKED":
            print(f"  {label}: BLOCKED ({res.get('reason')})")
            continue
        print(f"  == {label} ({res['mode']} hh={res['hh_uid']}) "
              f"node_key={res['node_key']} roster={res['roster_size_first_node']} "
              f"distinct_idperson={res['distinct_idperson_first_node']}")
        for rk in ("rung1", "rung2", "rung3", "rung4"):
            r = res.get(rk, {})
            tud = r.get("tudef", {})
            extra = ""
            if "components" in r and r["components"]:
                cd = r["components"]
                ben = cd.get("ils_ben", {})
                org = cd.get("ils_origy", {})
                extra = (f" ils_ben(max={ben.get('max_abs', 0):.2f},"
                         f"bad={ben.get('n_above_tol', 0)}) "
                         f"ils_origy(max={org.get('max_abs', 0):.2f},"
                         f"bad={org.get('n_above_tol', 0)})")
            print(f"     {rk}: {r.get('status')} "
                  f"tudef={tud.get('n_warning_lines', '-')} "
                  f"loc={r.get('localised_to')}{extra}")
        print(f"     VERDICT: {res.get('case_verdict')}")


if __name__ == "__main__":
    main()
