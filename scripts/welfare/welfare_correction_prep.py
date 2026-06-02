"""
Welfare Stage Two — Increment Two-H: bound the singleton stored-target residual,
characterise couples model fit, and (gate-conditional) produce a SIDE-ARTEFACT
correction candidate for the couples draw_joint=0 collision block.

Measurement/audit-only. DOES NOT: re-estimate, overwrite/rewrite any engine-ready /
priced / precompute / chunk parquet, compute V_i^dir, run growth, promote W^3, or touch
any measure beyond W^3. The Task-3 correction candidate is a NEW side artifact, NOT a
build parquet and NOT authorised as estimator input until separately reviewed.

Reuses the Two-E helper module welfare_assessment_unit_diag for the EUROMOD call,
raw-schema input build, and fd-level TUDef capture. Collision-free full-node-key stamping
is done here with a DENSE per-batch node ordinal (dense_collisionfree_stamp) to keep
stamped IDs bounded for large draw_joint. The collision-free batch == isolated clean
reprice was verified in Two-G.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import welfare_assessment_unit_diag as wd  # noqa: E402

KEY = ["stacked_hh_uid", "draw_joint", "draw_male", "draw_female"]


def block_distinct_alts(df):
    """Per-row distinct (draw_male, draw_female) count within (stacked_hh_uid, draw_joint).
    >1 marks a collision block; ==1 marks a singleton block."""
    pair = (df["draw_male"].astype("int64") * 100000
            + df["draw_female"].astype("int64"))
    return pair.groupby([df["stacked_hh_uid"], df["draw_joint"]]).transform("nunique").to_numpy()


def dense_collisionfree_stamp(df, id_mult=10_000):
    """Collision-free stamping with a DENSE per-batch node ordinal (0..N-1) instead of
    encoding (draw_joint, draw_male, draw_female) into the tag. This keeps stamped IDs
    BOUNDED (orig_id * id_mult + ordinal, ordinal < id_mult) even for large draw_joint,
    avoiding the oversized-ID EUROMOD abort seen when draw_joint approaches 900 with the
    (dj,dm,df)-encoded tag. Every distinct full-node-key block gets a unique ordinal, so
    no two alternatives sharing a draw_joint collapse onto the same stamped idperson;
    kinship (idfather/idmother/idpartner) is remapped consistently within each node.
    DIAGNOSTIC ONLY; not production-ready. id_mult must exceed the number of distinct
    nodes in the batch (asserted)."""
    df = df.copy()
    node_id = (df["stacked_hh_uid"].astype("int64").astype(str) + "_"
               + df["draw_joint"].astype("int64").astype(str) + "_"
               + df["draw_male"].astype("int64").astype(str) + "_"
               + df["draw_female"].astype("int64").astype(str))
    ordinal = node_id.astype("category").cat.codes.to_numpy().astype("int64")
    n_nodes = int(ordinal.max()) + 1 if len(ordinal) else 0
    if n_nodes >= id_mult:
        raise ValueError(f"dense stamp: {n_nodes} nodes >= id_mult {id_mult}; raise id_mult")
    df["idhh_true"] = df["idhh"].copy()
    df["idperson_true"] = df["idperson"].copy()
    df["idhh"] = df["idhh"].astype(float).astype("int64") * id_mult + ordinal
    df["idperson"] = df["idperson"].astype(float).astype("int64") * id_mult + ordinal
    for kin in ["idfather", "idmother", "idpartner"]:
        if kin in df.columns:
            k = pd.to_numeric(df[kin], errors="coerce").fillna(0).astype("int64")
            df[kin] = np.where(k == 0, 0, k * id_mult + ordinal)
    return df


def batched_collisionfree_reprice(bc, node_rows, *, year, components, tol, priced,
                                  country_override):
    """Clean-reprice a set of existing nodes (possibly many households / nodes) in ONE
    collision-free-stamped EUROMOD batch, and compare to stored priced NOMINAL on decider
    rows keyed by (full node key, original idperson). Returns (per_node_records, warn,
    err): one record per (hh, node) with clean/stored components + joint disposable.

    node_rows must already be the concatenation of full rosters for the chosen nodes
    (roster-complete per node). The collision-free stamp makes every (node, person)
    globally unique, so there is no cross-node collision in the batch."""
    system_code, dataset_name = bc["system_pairing"][year]
    country = str(country_override or str(system_code).split("_")[0])
    raw_cols = bc["raw_schema"][year]
    stamped = dense_collisionfree_stamp(node_rows.copy())
    em = wd._em_input(stamped, raw_cols)
    sim, warn, err, _ = wd._run_euromod(bc, em, country=country,
                                        system_code=system_code, dataset_name=dataset_name)
    if err is not None or sim is None:
        return [], warn, (err or "no sim")

    rep_cols = ["ils_dispy"] + [c for c in components if c in sim.columns]
    st = stamped.reset_index(drop=True).copy()
    for c in rep_cols:
        st[f"__rep_{c}"] = pd.to_numeric(sim[c], errors="coerce").to_numpy()[: len(st)]
    keepcols = KEY + ["idperson_true", "ruro_decider"] + [f"__rep_{c}" for c in rep_cols]
    dec = st.loc[st.get("ruro_decider", 1) == 1, keepcols].copy()
    dec["__orig_idperson"] = dec["idperson_true"]

    pid = "idperson_true" if "idperson_true" in priced.columns else "idperson"
    pr = priced[priced.get("ruro_decider", 1) == 1].copy()
    pr["__orig_idperson"] = pr[pid]
    stored_cols = ["ils_dispy"] + [c for c in components if c in pr.columns]

    recs = []
    for keyvals, d in dec.groupby(KEY):
        nd = dict(zip(KEY, keyvals))
        p = pr
        for k in KEY:
            p = p[p[k] == nd[k]]
        if len(p) == 0 or len(d) == 0:
            recs.append({"node": {k: int(nd[k]) for k in KEY}, "status": "BLOCKED",
                         "reason": "stored/node absent"})
            continue
        m = d.merge(p[["__orig_idperson"] + stored_cols], on="__orig_idperson", how="inner")
        comp = {}
        for c in rep_cols:
            if c in m.columns and f"__rep_{c}" in m.columns:
                diff = np.abs(pd.to_numeric(m[f"__rep_{c}"], errors="coerce").to_numpy()
                              - pd.to_numeric(m[c], errors="coerce").to_numpy())
                comp[c] = {"n_above_tol": int((diff > tol).sum()),
                           "max_abs": float(np.nanmax(diff)) if len(diff) else 0.0}
        bad = any(v["n_above_tol"] > 0 for k, v in comp.items() if k != "ils_dispy")
        clean_jd = float(pd.to_numeric(m["__rep_ils_dispy"], errors="coerce").sum())
        stored_jd = float(pd.to_numeric(m["ils_dispy"], errors="coerce").sum())
        # per-decider stored/clean for ils_ben (for the cross-decider check)
        per_dec = []
        for _, r in m.iterrows():
            per_dec.append({
                "idperson_true": int(r["__orig_idperson"]),
                "stored_ils_ben": float(r.get("ils_ben", float("nan"))),
                "clean_ils_ben": float(r.get("__rep_ils_ben", float("nan"))),
            })
        recs.append({
            "node": {k: int(nd[k]) for k in KEY},
            "status": "FAIL" if bad else "PASS",
            "components": {k: v for k, v in comp.items() if k != "ils_dispy"},
            "joint_dispy_nominal": {"clean": clean_jd, "stored": stored_jd,
                                    "abs_diff": abs(clean_jd - stored_jd)},
            "localised_to": (max([k for k in comp if k != "ils_dispy"],
                                 key=lambda k: comp[k]["max_abs"]) if bad else None),
            "per_decider": per_dec,
        })
    return recs, warn, None


def resilient_reprice(bc, node_rows, *, year, components, tol, priced, country_override,
                      min_block=1):
    """Like batched_collisionfree_reprice, but RESILIENT to EUROMOD batch aborts: if the
    whole batch aborts (one bad node can abort the native engine), split the node set in
    half and recurse, isolating the offending node(s) as BLOCKED rather than losing the
    whole batch. Returns (recs, max_tudef, blocked_nodes)."""
    node_keys = node_rows[KEY].drop_duplicates().to_records(index=False)
    node_keys = [tuple(int(v) for v in k) for k in node_keys]

    def _run(keys):
        mask = node_rows[KEY].apply(tuple, axis=1).isin(set(keys))
        rows = node_rows[mask.to_numpy()]
        recs, warn, err = batched_collisionfree_reprice(
            bc, rows, year=year, components=components, tol=tol, priced=priced,
            country_override=country_override)
        tud = warn["n_warning_lines"] if isinstance(warn, dict) else 0
        if err is None:
            return recs, tud, []
        # aborted: split
        if len(keys) <= min_block:
            return [], tud, [{"node": dict(zip(KEY, k)), "reason": str(err)[:120]}
                             for k in keys]
        mid = len(keys) // 2
        r1, t1, b1 = _run(keys[:mid])
        r2, t2, b2 = _run(keys[mid:])
        return r1 + r2, max(t1, t2), b1 + b2

    return _run(node_keys)


def cross_decider_benefit_signature(rec):
    """Two-G hypothesis: when a node fails, does the failing decider's STORED ils_ben
    approximate the OTHER decider's stored or clean ils_ben (a cross-decider/partner
    benefit attribution)? Returns a dict flagging the pattern if 2 deciders present."""
    pd_ = rec.get("per_decider", [])
    if len(pd_) != 2 or rec.get("status") != "FAIL":
        return None
    a, b = pd_
    # identify the failing decider = larger |stored-clean|
    da = abs(a["stored_ils_ben"] - a["clean_ils_ben"])
    db = abs(b["stored_ils_ben"] - b["clean_ils_ben"])
    fail, other = (a, b) if da >= db else (b, a)
    gap = fail["stored_ils_ben"] - fail["clean_ils_ben"]
    # does the stored surplus on the failing decider approximate the partner's benefit?
    approximates_partner_stored = abs(gap - other["stored_ils_ben"]) <= 1.0
    approximates_partner_clean = abs(gap - other["clean_ils_ben"]) <= 1.0
    return {
        "failing_idperson": fail["idperson_true"],
        "stored_minus_clean_on_failing": float(gap),
        "partner_stored_ils_ben": float(other["stored_ils_ben"]),
        "partner_clean_ils_ben": float(other["clean_ils_ben"]),
        "gap_approximates_partner_stored_ils_ben": bool(approximates_partner_stored),
        "gap_approximates_partner_clean_ils_ben": bool(approximates_partner_clean),
    }
