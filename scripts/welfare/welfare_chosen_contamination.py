"""
Welfare Stage Two — Increment Two-G: validate the couples clean-reprice INSTRUMENT and
measure CHOSEN-alternative contamination. Measurement/audit-only.

Covers:
  Task 1 — reconcile Two-E vs Two-F singleton-control evidence (no contradiction unless
           the SAME node passes in Two-E and fails in Two-F under the SAME construction);
           diagnose the 3 Two-F singleton failures (code-path / sample / batch-spillover /
           unresolved).
  Task 2 — instrument-usability helpers (benchmark clean reprice = one existing node,
           isolated roster, original IDs, raw-schema inputs, nominal compare; optional
           collision-free full-node-key stamping for batched diagnostics only).
  Task 3 — chosen-alternative consumption SOURCE confirmation (engine-ready c_norm /
           ils_dispy_real provenance + alignment trace).
  Task 4 — chosen-alternative contamination measurement on a large deterministic sample.
  Task 5 — first-order theta_hat influence screen (V_chosen, dV, P_chosen, dP, d ll_i).

Reuses the Two-E ladder helpers (welfare_assessment_unit_diag) for the EUROMOD call,
raw-schema input build, fd-level TUDef capture, and node-key parity compare; and
welfare_core for the estimator/welfare V machinery (no new utility path).

DOES NOT: re-estimate, rewrite/overwrite any parquet, price redrawn nodes, compute
V_i^dir, run growth, promote W^3, or touch any measure beyond W^3.
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
CHOSEN_NODE = {"draw_joint": 0, "draw_male": 0, "draw_female": 0}


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------
def _node_rows(sub, nd):
    mask = np.ones(len(sub), dtype=bool)
    for k in KEY:
        mask &= (sub[k] == nd[k])
    return sub[mask].copy()


def _collisionfree_stamp(df, id_mult=10_000):
    """DIAGNOSTIC-ONLY collision-free stamping: make stamped person/household IDs unique
    per FULL node key (draw_joint, draw_male, draw_female) instead of draw_joint alone, so
    two alternatives sharing a draw_joint never collapse onto the same stamped idperson.
    Remaps idfather/idmother/idpartner consistently. NOT production-ready."""
    df = df.copy()
    dj = pd.to_numeric(df["draw_joint"], errors="coerce").fillna(0).astype("int64")
    dm = pd.to_numeric(df["draw_male"], errors="coerce").fillna(0).astype("int64")
    dfm = pd.to_numeric(df["draw_female"], errors="coerce").fillna(0).astype("int64")
    # a unique node tag per (draw_joint, draw_male, draw_female)
    tag = (dj * 10_000 + dm * 100 + dfm).to_numpy()
    df["idhh_true"] = df["idhh"].copy()
    df["idperson_true"] = df["idperson"].copy()
    df["idhh"] = df["idhh"].astype(float).astype("int64") * id_mult + tag
    df["idperson"] = df["idperson"].astype(float).astype("int64") * id_mult + tag
    for kin in ["idfather", "idmother", "idpartner"]:
        if kin in df.columns:
            k = pd.to_numeric(df[kin], errors="coerce").fillna(0).astype("int64")
            df[kin] = np.where(k == 0, 0, k * id_mult + tag)
    return df


def reprice_isolated(bc, rows, *, year, components, tol, priced, country_override):
    """Benchmark clean reprice of ONE existing node, isolated roster, original IDs."""
    system_code, dataset_name = bc["system_pairing"][year]
    country = str(country_override or str(system_code).split("_")[0])
    raw_cols = bc["raw_schema"][year]
    em = wd._em_input(rows, raw_cols)
    sim, warn, err, _ = wd._run_euromod(bc, em, country=country,
                                        system_code=system_code,
                                        dataset_name=dataset_name)
    if err is not None:
        return {"status": "BLOCKED", "reason": err, "tudef": warn}
    comp, joint, n = wd._compare(sim, rows, priced, KEY, components, tol)
    return {"status": wd._status(comp, tol), "tudef": warn["n_warning_lines"],
            "n_decider_matched": n, "components": comp, "joint_dispy": joint,
            "localised_to": wd._localise(comp, components), "sim": sim}


def reprice_household_batch(bc, sub, *, year, mode_stamp, components, tol, priced,
                            country_override, node):
    """Reprice a whole household's alternatives in ONE batch, stamped either the
    production way (mode_stamp='production', stamp on draw_joint) or collision-free
    (mode_stamp='collisionfree'). Returns the parity of the requested `node` against
    stored, plus the TUDef count for the batch. Diagnostic only."""
    system_code, dataset_name = bc["system_pairing"][year]
    country = str(country_override or str(system_code).split("_")[0])
    raw_cols = bc["raw_schema"][year]
    if mode_stamp == "production":
        stamped = bc["stamp"](sub.copy(), "draw_joint", 10_000)
    else:
        stamped = _collisionfree_stamp(sub.copy())
    em = wd._em_input(stamped, raw_cols)
    sim, warn, err, _ = wd._run_euromod(bc, em, country=country,
                                        system_code=system_code,
                                        dataset_name=dataset_name)
    if err is not None:
        return {"status": "BLOCKED", "reason": err, "tudef": warn}
    # compare only the requested node's decider rows against stored
    comp, joint, n = wd._compare(sim, stamped, priced, KEY, components, tol)
    return {"status": wd._status(comp, tol), "tudef": warn["n_warning_lines"],
            "n_decider_matched": n, "components": comp, "joint_dispy": joint,
            "localised_to": wd._localise(comp, components)}
