"""
Welfare Stage Two — Increment Two-E: assessment-unit / ID-stamping DIAGNOSTIC.

Isolates whether Two-D's existing-node parity failure is driven by the EUROMOD
assessment-unit presentation (ID stamping + batched multi-draw rosters with
colliding person IDs) rather than by irrecoverable benefit state.

DIAGNOSTIC ONLY. Prices NO redrawn node, computes NO V_i^dir, runs NO 2x/4x growth,
promotes NO W^3, touches NO measure beyond W^3, writes NO storage/precompute/priced/
chunk parquet. Existing nodes only.

KEY STRUCTURAL FINDINGS THAT SHAPE THIS LADDER (established by direct schema/row
inspection of the precompute-long and priced-long parquets, recorded in the report):

  1. SINGLES node key = (stacked_hh_uid, draw). Each (hh, draw) is ONE clean roster:
     distinct idperson per row, no within-node ID collision. So singles cannot fail
     for a "two persons share an idperson" reason.

  2. COUPLES node key = (stacked_hh_uid, draw_joint, draw_male, draw_female), NOT
     draw_joint alone. A single draw_joint packs MULTIPLE labour-supply alternatives
     (distinct (draw_male, draw_female) combos) STACKED in the same block, each copy
     carrying the SAME idperson but DIFFERENT earnings. Two-D selected couples on
     draw_joint only, so it fed EUROMOD several stacked alternatives with COLLIDING
     idperson at once -> EUROMOD's TUDef sees "more than one possible partner" and the
     run is meaningless. This ladder uses the CORRECT node key so one node = one clean
     4-person roster (verified: exactly 4 rows, 4 distinct idperson, no collision).

PARITY TARGET: stored priced-long value for the SAME node, on DECIDER rows, NOMINAL
(no CPI/phi). Components: ils_dispy, ils_origy, ils_ben, ils_tax, ils_sicdy; for
couples also household-joint summed disposable income.

EUROMOD INPUT SOURCE: precompute-long (the build's own EUROMOD input source); only
raw-schema input columns are fed; never *_s / ils_* / tax-benefit OUTPUTS as inputs.

No W^3 welfare finding; no measure beyond W^3.
"""
from __future__ import annotations

import importlib
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pyarrow.parquet as pq  # noqa: E402


def build_constants(build_module):
    mod = importlib.import_module(build_module)
    return {"system_pairing": mod._SYSTEM_PAIRING, "raw_schema": mod._RAW_SCHEMA,
            "EuromodRunner": mod.EuromodRunner, "em_root": mod._EM_ROOT,
            "stamp": mod._stamp_draw_ids}


@contextmanager
def _capture_fd():
    """Capture BOTH process fd 1 and fd 2 (the native EUROMOD engine writes its
    TUDef partner warnings to the process console / fd 1, which an in-Python
    sys.stdout redirect misses). Yields a dict whose ['text'] is filled on exit."""
    holder = {"text": ""}
    tmp = tempfile.TemporaryFile(mode="w+b")  # noqa: SIM115 (manual fd lifecycle)
    saved_out, saved_err = os.dup(1), os.dup(2)
    os.dup2(tmp.fileno(), 1)
    os.dup2(tmp.fileno(), 2)
    try:
        yield holder
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        os.dup2(saved_out, 1)
        os.dup2(saved_err, 2)
        os.close(saved_out)
        os.close(saved_err)
        tmp.seek(0)
        holder["text"] = tmp.read().decode("utf-8", errors="replace")
        tmp.close()


def _count_tudef(text):
    lines = [ln for ln in text.splitlines()
             if "TUDef" in ln or "DefTu" in ln or "possible partner" in ln]
    import re
    units = sorted(set(re.findall(r"assessment unit '([^']+)'", text)))
    return {"n_warning_lines": len(lines), "distinct_units": units,
            "sample": lines[:3]}


def _node_key(mode):
    return (["stacked_hh_uid", "draw"] if mode == "singles"
            else ["stacked_hh_uid", "draw_joint", "draw_male", "draw_female"])


def _load(base, stem, year, mode, *, long_):
    suff = "__long" if long_ else ""
    p = base / f"{stem}__{year}__{mode}{suff}.parquet"
    if not p.exists():
        raise FileNotFoundError(p)
    return pq.ParquetFile(p).read().to_pandas(), p


def _run_euromod(bc, em_rows, *, country, system_code, dataset_name):
    """Run one EUROMOD call on a raw-schema-only input frame; capture TUDef warnings.
    Returns (sim_df_or_None, warn_dict, error_or_None)."""
    with _capture_fd() as cap:
        err = None
        sim = None
        try:
            runner = bc["EuromodRunner"](bc["em_root"])
            sim = runner.run_on_dataframe(em_rows, country=country,
                                          system_code=system_code,
                                          dataset_name=dataset_name)
        except Exception as e:  # noqa: BLE001
            err = f"{type(e).__name__}: {e}"
    return sim, _count_tudef(cap["text"]), err, cap["text"]


def _em_input(node_rows, raw_cols):
    em = node_rows[[c for c in raw_cols if c in node_rows.columns]].copy()
    for c in em.columns:
        em[c] = pd.to_numeric(em[c], errors="coerce").fillna(0.0)
    return em


def _compare(sim, node_rows, priced, key, components, tol):
    """Attach repriced outputs to node_rows (decider) and compare to stored priced
    on the node key + ORIGINAL idperson. Returns (per_component dict, joint dict|None,
    n_decider_matched)."""
    out_cols = ["ils_dispy"] + [c for c in components if c in sim.columns]
    nr = node_rows.reset_index(drop=True).copy()
    for c in out_cols:
        nr[f"__rep_{c}"] = pd.to_numeric(
            sim[c], errors="coerce").to_numpy()[: len(nr)]
    dec = nr[nr.get("ruro_decider", 1) == 1] if "ruro_decider" in nr else nr

    # priced join: priced 'idperson_true' is the ORIGINAL (un-stamped) id, which
    # equals precompute's idperson. Merge on node key + original idperson. On the
    # LEFT (repriced) side the original id is 'idperson' for un-stamped rungs (1/2/4)
    # and 'idperson_true' for the stamped rung (3) -- _stamp_draw_ids stamps idperson
    # in place and writes the original to idperson_true. Pick whichever the frame
    # carries so the stamped batch still joins (Rung 3 otherwise matched 0 rows).
    pid = "idperson_true" if "idperson_true" in priced.columns else "idperson"
    prk = priced.copy()
    prk["__orig_idperson"] = prk[pid]
    storedcols = ["ils_dispy"] + [c for c in components if c in prk.columns]
    join_keys = key + ["__orig_idperson"]
    left = dec.copy()
    left_orig = "idperson_true" if "idperson_true" in left.columns else "idperson"
    left["__orig_idperson"] = left[left_orig]
    m = (left[join_keys + [f"__rep_{c}" for c in out_cols]]
         .merge(prk[join_keys + storedcols].drop_duplicates(join_keys),
                on=join_keys, how="inner"))
    comp = {}
    for c in out_cols:
        if c in m.columns:
            d = np.abs(pd.to_numeric(m[f"__rep_{c}"], errors="coerce").to_numpy()
                       - pd.to_numeric(m[c], errors="coerce").to_numpy())
            comp[c] = {"n_above_tol": int(np.sum(d > tol)),
                       "max_abs": float(np.nanmax(d)) if len(d) else 0.0}
    joint = None
    if "draw_joint" in key:  # couples: household-joint disposable income
        g = m.groupby(key)
        jd = np.abs(g["__rep_ils_dispy"].sum().to_numpy()
                    - g["ils_dispy"].sum().to_numpy())
        joint = {"n_nodes": int(len(jd)),
                 "max_abs": float(np.nanmax(jd)) if len(jd) else 0.0,
                 "n_above_tol": int(np.sum(jd > tol))}
    return comp, joint, int(len(m))


def _status(comp, tol):
    if not comp:
        return "NO_MATCH"
    bad = any(v["n_above_tol"] > 0 for k, v in comp.items() if k != "ils_dispy") \
        or comp.get("ils_dispy", {}).get("n_above_tol", 0) > 0
    return "FAIL" if bad else "PASS"


def _localise(comp, components):
    true_comps = [c for c in components if c in comp]
    if not true_comps:
        return None
    return max(true_comps, key=lambda c: comp[c]["max_abs"])


def select_node_block(pl, mode, hh_uid, *, n_nodes):
    """Return the first n_nodes distinct existing nodes for one household as a list
    of (node_key_values_dict, node_rows_df), roster-complete by node key."""
    key = _node_key(mode)
    sub = pl[pl["stacked_hh_uid"] == hh_uid].copy()
    nodes = (sub[key].drop_duplicates().sort_values(key)
             .head(n_nodes).to_dict("records"))
    out = []
    for nd in nodes:
        mask = np.ones(len(sub), dtype=bool)
        for k, v in nd.items():
            mask &= (sub[k] == v)
        out.append((nd, sub[mask].copy()))
    return out


def run_ladder(cfg2, *, mode, hh_uid, n_nodes, components, tol, country_override):
    bc = build_constants(cfg2["build_module"])
    from _bpool_paths import bpool_dir
    base = bpool_dir()
    year = cfg2["assessment_unit_diag"]["year"]
    system_code, dataset_name = bc["system_pairing"][year]
    country = str(country_override or str(system_code).split("_")[0])
    raw_cols = bc["raw_schema"][year]
    key = _node_key(mode)
    draw_col = "draw" if mode == "singles" else "draw_joint"
    id_mult = 1_000 if mode == "singles" else 10_000

    pl, pl_path = _load(base, cfg2["precompute_long_stem"], year, mode, long_=True)
    priced, pr_path = _load(base, cfg2["priced_long_stem"], year, mode, long_=False)
    nodes = select_node_block(pl, mode, hh_uid, n_nodes=n_nodes)
    if not nodes:
        return {"mode": mode, "hh_uid": hh_uid, "status": "BLOCKED",
                "reason": "household not found in precompute-long"}

    result = {"mode": mode, "hh_uid": int(hh_uid), "year": year,
              "system_code": system_code, "country": country,
              "node_key": key, "n_nodes_requested": n_nodes,
              "n_nodes_selected": len(nodes),
              "first_node": {k: (int(v) if isinstance(v, (int, np.integer)) else v)
                             for k, v in nodes[0][0].items()},
              "roster_size_first_node": int(len(nodes[0][1])),
              "distinct_idperson_first_node": int(nodes[0][1]["idperson"].nunique())}

    # ---- RUNG 1: single node, ORIGINAL IDs, no stamping ----
    rows0 = nodes[0][1]
    em0 = _em_input(rows0, raw_cols)
    sim0, warn0, err0, _ = _run_euromod(bc, em0, country=country,
                                        system_code=system_code,
                                        dataset_name=dataset_name)
    if err0 is not None:
        result["rung1"] = {"status": "BLOCKED", "reason": err0, "tudef": warn0}
    else:
        c0, j0, n0 = _compare(sim0, rows0, priced, key, components, tol)
        result["rung1"] = {"status": _status(c0, tol), "stamping": "none",
                           "n_decider_matched": n0, "components": c0,
                           "joint_dispy": j0, "tudef": warn0,
                           "localised_to": _localise(c0, components)}

    # ---- RUNG 2: several nodes, each its OWN one-node EUROMOD call, original IDs ----
    per_node = []
    for nd, rows in nodes:
        em = _em_input(rows, raw_cols)
        sim, warn, err, _ = _run_euromod(bc, em, country=country,
                                         system_code=system_code,
                                         dataset_name=dataset_name)
        if err is not None:
            per_node.append({"node": {k: int(nd[k]) for k in key},
                             "status": "BLOCKED", "reason": err, "tudef": warn})
            continue
        c, j, n = _compare(sim, rows, priced, key, components, tol)
        per_node.append({"node": {k: int(nd[k]) for k in key},
                         "status": _status(c, tol), "n_decider_matched": n,
                         "components": c, "joint_dispy": j, "tudef": warn,
                         "localised_to": _localise(c, components)})
    r2_pass = all(p.get("status") == "PASS" for p in per_node)
    r2_first_div = next((p["localised_to"] for p in per_node
                         if p.get("status") == "FAIL"), None)
    result["rung2"] = {"status": "PASS" if r2_pass else "FAIL",
                       "stamping": "none_separate_calls",
                       "per_node": per_node,
                       "first_component_to_diverge": r2_first_div}

    # ---- RUNG 3: same nodes, ONE batch, current production _stamp_draw_ids ----
    batch = pd.concat([rows for _, rows in nodes], ignore_index=True)
    stamped = bc["stamp"](batch.copy(), draw_col, id_mult)
    em3 = _em_input(stamped, raw_cols)
    sim3, warn3, err3, _ = _run_euromod(bc, em3, country=country,
                                        system_code=system_code,
                                        dataset_name=dataset_name)
    if err3 is not None:
        result["rung3"] = {"status": "BLOCKED", "reason": err3, "tudef": warn3}
    else:
        c3, j3, n3 = _compare(sim3, stamped, priced, key, components, tol)
        result["rung3"] = {"status": _status(c3, tol),
                           "stamping": "production_stamp_draw_ids_batched",
                           "n_decider_matched": n3, "components": c3,
                           "joint_dispy": j3, "tudef": warn3,
                           "localised_to": _localise(c3, components)}

    # ---- verdict for this case ----
    r1 = result.get("rung1", {})
    r3 = result.get("rung3", {})
    r1_pass = r1.get("status") == "PASS"
    r3_pass = r3.get("status") == "PASS"
    r1_warnfree = r1.get("tudef", {}).get("n_warning_lines", 1) == 0
    if not r1_pass and r1_warnfree:
        verdict = ("clean_household_failure: a single clean household-draw with "
                   "original IDs and zero TUDef warnings STILL fails parity -> not "
                   "merely a multi-draw stamping artefact for this case.")
    elif r1_pass and r2_pass and not r3_pass:
        verdict = ("current_stamping_artefact: clean single/separate-call repricing "
                   "passes, but the production stamped batched presentation fails -> "
                   "_stamp_draw_ids / batched multi-draw presentation is the binding "
                   "artefact for existing-node parity in this case.")
    elif r1_pass and r2_pass and r3_pass:
        verdict = ("all_clean_pass: existing-node state is sufficient; even the "
                   "production stamped batch reproduces parity for this case.")
    else:
        verdict = ("mixed_or_unresolved: see per-rung statuses; not a clean "
                   "single-cause attribution.")
    result["case_verdict"] = verdict
    result["sources"] = {"precompute_long": str(pl_path), "priced_long": str(pr_path)}
    return result
