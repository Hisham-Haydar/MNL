"""
Welfare Stage Two — Increment Two-L: cross-track stored-target `ils_ben` residual
DIAGNOSIS (singles + couples). Diagnostic-only.

DOES NOT: re-estimate, compute V_i^dir, price redrawn nodes, promote W^3, touch any
measure beyond W^3, produce a correction candidate, or write/overwrite any build /
storage / engine-ready / priced / precompute / chunk parquet.

Reuses the Two-E helpers (welfare_assessment_unit_diag) for the EUROMOD call, raw-schema
input build, and fd-level TUDef capture. Adds a benefit-decomposition reprice that returns
the full simulated `*_s` benefit breakdown (not just ils_dispy + 4 components), so the
ils_ben gap can be localised to a sub-component (Task 2), and a cross-policy-system reprice
(Task 3) and full-chunk-context reprice (Task 4).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import welfare_assessment_unit_diag as wd  # noqa: E402

# simulated benefit sub-components persisted in priced (and produced by EUROMOD sim),
# grouped for Task-2 localisation.
BENEFIT_GROUPS = {
    "housing": ["bhotn_s", "bchlg_s"],
    "child_family": ["bch00_s", "bchyc_s", "bched_s", "bchba_s", "bchcc_s", "bchot_s",
                     "bchor_s"],
    "social_assistance": ["bsa00_s", "bsaoa_s"],
    "activity_allowance_ppe": ["bsawk_s", "bmact_s", "bpact_s", "tinrf_s"],
    "unemployment": ["bunmt_s", "bunct_s", "bunctmy_s"],
    "disability": ["bdi_s"],
    "other_benefit": ["bsuwd_s"],
}
ALL_BEN_S = [c for g in BENEFIT_GROUPS.values() for c in g]
SUBTOTALS = ["ils_ben", "ils_benmt", "ils_bennt", "ils_pen", "ils_bensim"]


def node_key(mode):
    return (["stacked_hh_uid", "draw"] if mode == "singles"
            else ["stacked_hh_uid", "draw_joint", "draw_male", "draw_female"])


def reprice_node_full(bc, rows, *, year, system_code=None, dataset_name=None,
                      country_override=None):
    """Clean isolated reprice of ONE node; return the FULL EUROMOD sim frame (all benefit
    *_s + subtotals), plus TUDef + error. If system_code/dataset_name are given they
    OVERRIDE the year's pairing (Task 3 cross-policy-system test)."""
    sc, ds = bc["system_pairing"][year]
    sc = system_code or sc
    ds = dataset_name or ds
    country = str(country_override or str(sc).split("_")[0])
    raw = bc["raw_schema"][year]
    em = wd._em_input(rows, raw)
    sim, warn, err, _ = wd._run_euromod(bc, em, country=country, system_code=sc,
                                        dataset_name=ds)
    return sim, warn, err, sc, ds


def decompose_node(sim, rows, priced, key, *, tol):
    """Per-decider stored-vs-clean for ils_ben subtotals + every benefit sub-component
    available in BOTH sim and priced. Returns the localisation of the ils_ben gap."""
    nr = rows.reset_index(drop=True).copy()
    sim_cols = [c for c in (SUBTOTALS + ALL_BEN_S + ["ils_dispy", "ils_origy",
                "ils_tax", "ils_sicdy"]) if c in sim.columns]
    for c in sim_cols:
        nr[f"__rep_{c}"] = pd.to_numeric(sim[c], errors="coerce").to_numpy()[: len(nr)]
    dec = nr[nr.get("ruro_decider", 1) == 1].copy()
    lo = "idperson_true" if "idperson_true" in dec.columns else "idperson"
    dec["__o"] = dec[lo]
    pid = "idperson_true" if "idperson_true" in priced.columns else "idperson"
    pr = priced.copy()
    pr["__o"] = pr[pid]
    stored_cols = [c for c in sim_cols if c in pr.columns]
    m = dec[key + ["__o"] + [f"__rep_{c}" for c in sim_cols]].merge(
        pr[key + ["__o"] + stored_cols].drop_duplicates(key + ["__o"]),
        on=key + ["__o"], how="inner")
    # ils_ben gap per decider; localise by which sub-component / subtotal diverges
    comp = {}
    for c in sim_cols:
        if c in m.columns and f"__rep_{c}" in m.columns:
            d = np.abs(pd.to_numeric(m[f"__rep_{c}"], errors="coerce").to_numpy()
                       - pd.to_numeric(m[c], errors="coerce").to_numpy())
            comp[c] = {"max_abs": float(np.nanmax(d)) if len(d) else 0.0,
                       "n_above_tol": int(np.sum(d > tol))}
    # group localisation
    grp = {}
    for gname, members in BENEFIT_GROUPS.items():
        gmax = max((comp[c]["max_abs"] for c in members if c in comp), default=0.0)
        gbad = sum(comp[c]["n_above_tol"] for c in members if c in comp)
        grp[gname] = {"max_abs": gmax, "n_above_tol": gbad}
    ils_ben_gap = comp.get("ils_ben", {}).get("max_abs", 0.0)
    localised = max(grp, key=lambda g: grp[g]["max_abs"]) if grp else None
    return {"components": comp, "benefit_groups": grp,
            "ils_ben_gap_max_abs": ils_ben_gap,
            "localised_group": localised,
            "localised_group_max_abs": grp.get(localised, {}).get("max_abs", 0.0)
            if localised else 0.0,
            "n_decider_matched": int(len(m))}


def reprice_and_status(bc, rows, priced, key, components, tol, *, year):
    """Quick PASS/FAIL on ils_dispy+components (isolated). Returns (status, comp, tudef)."""
    sim, warn, err, _, _ = reprice_node_full(bc, rows, year=year)
    if err is not None or sim is None:
        return "BLOCKED", {}, (warn["n_warning_lines"] if isinstance(warn, dict) else 0)
    comp, _, n = wd._compare(sim, rows, priced, key, components, tol)
    return wd._status(comp, tol), comp, warn["n_warning_lines"]
