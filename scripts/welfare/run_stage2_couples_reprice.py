"""
Stage Two — Increment Two-F, Task 3 + Task 4: bounded clean-reprice magnitude check
(EUROMOD allowed here, existing nodes only) + approximate likelihood-impact screen.

Task 3 — on a deterministic stratified sample of EXISTING couples nodes across years:
  - chosen collision-exposed nodes (the chosen alt of the draw_joint=0 collision block);
  - nonchosen collision-exposed nodes (the other alt of that block);
  - singleton-draw_joint control nodes (should pass clean repricing);
  clean-reprice each node IN ISOLATION using the correct full node key
  (stacked_hh_uid, draw_joint, draw_male, draw_female) and ORIGINAL household
  relationships (no _stamp_draw_ids collision), then compare clean vs stored NOMINAL:
  ils_dispy / ils_origy / ils_ben / ils_tax / ils_sicdy + household-joint disposable.

Task 4 — for the clean-repriced sample only, a transparent first-order screen of whether
  the observed magnitude × theta_hat probability weight makes movement plausible. NOT a
  re-estimated likelihood and NOT proof of parameter movement.

Reuses the Two-E ladder helpers (welfare_assessment_unit_diag) for the EUROMOD call,
raw-schema input build, fd-level TUDef capture, and node-key parity compare. Audit-only:
prices NO redrawn node, writes NO parquet, computes NO V_i^dir, re-estimates NOTHING.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import welfare_assessment_unit_diag as wd  # noqa: E402
import welfare_core as wc  # noqa: E402

KEY = ["stacked_hh_uid", "draw_joint", "draw_male", "draw_female"]


def _select_sample(pl, rs):
    """Deterministic stratified existing-node sample from one year's precompute-long.
    Strata: chosen-exposed, nonchosen-exposed, singleton-control. Returns list of
    (stratum, node_key_dict, node_rows_df). Roster-complete by the full node key."""
    # distinct (dm,df) per (hh,draw_joint) block -> collision blocks have >1
    pair = pl["draw_male"].astype("int64") * 100000 + pl["draw_female"].astype("int64")
    blk = ["stacked_hh_uid", "draw_joint"]
    pl = pl.copy()
    pl["__nalts"] = pair.groupby([pl[k] for k in blk]).transform("nunique").to_numpy()
    n_hh = int(rs["n_hh_per_stratum"])
    max_per_hh = int(rs["max_exposed_nodes_per_hh"])

    # households that HAVE a collision block (every couple does, but stay general)
    coll_hh = (pl.loc[pl["__nalts"] > 1, "stacked_hh_uid"].drop_duplicates()
               .sort_values().head(n_hh).tolist())
    out = []
    for hh in coll_hh:
        sub = pl[pl["stacked_hh_uid"] == hh]
        exposed = sub[sub["__nalts"] > 1]
        nodes = exposed[KEY + ["is_chosen_joint"]].drop_duplicates(KEY)
        chosen = nodes[nodes["is_chosen_joint"] == 1].head(max_per_hh)
        nonchosen = nodes[nodes["is_chosen_joint"] != 1].head(max_per_hh)
        for _, nd in chosen.iterrows():
            out.append(("chosen_exposed", {k: int(nd[k]) for k in KEY},
                        _node_rows(sub, nd)))
        for _, nd in nonchosen.iterrows():
            out.append(("nonchosen_exposed", {k: int(nd[k]) for k in KEY},
                        _node_rows(sub, nd)))

    # singleton-draw_joint controls (block has exactly 1 alt) from the same households
    n_ctrl = int(rs["n_singleton_controls"])
    ctrl_added = 0
    for hh in coll_hh:
        if ctrl_added >= n_ctrl:
            break
        sub = pl[pl["stacked_hh_uid"] == hh]
        singletons = sub[sub["__nalts"] == 1][KEY].drop_duplicates(KEY)
        if len(singletons):
            nd = singletons.iloc[0]
            out.append(("singleton_control", {k: int(nd[k]) for k in KEY},
                        _node_rows(sub, nd)))
            ctrl_added += 1
    return out


def _node_rows(sub, nd):
    mask = np.ones(len(sub), dtype=bool)
    for k in KEY:
        mask &= (sub[k] == nd[k])
    return sub[mask].copy()


def _reprice_year(cfg2, bc, *, year, rs, components, tol, country_override):
    from _bpool_paths import bpool_dir
    base = bpool_dir()
    if year not in bc["system_pairing"]:
        return {"year": year, "status": "BLOCKED", "reason": "year not in pairing"}
    system_code, dataset_name = bc["system_pairing"][year]
    country = str(country_override or str(system_code).split("_")[0])
    raw_cols = bc["raw_schema"][year]
    pl, _ = wd._load(base, cfg2["precompute_long_stem"], year, "couples", long_=True)
    priced, _ = wd._load(base, cfg2["priced_long_stem"], year, "couples", long_=False)
    sample = _select_sample(pl, rs)

    nodes_out = []
    for stratum, nd, rows in sample:
        em = wd._em_input(rows, raw_cols)
        sim, warn, err, _ = wd._run_euromod(bc, em, country=country,
                                            system_code=system_code,
                                            dataset_name=dataset_name)
        if err is not None:
            nodes_out.append({"stratum": stratum, "node": nd,
                              "status": "BLOCKED", "reason": err, "tudef": warn})
            continue
        comp, joint, n = wd._compare(sim, rows, priced, KEY, components, tol)
        nodes_out.append({
            "stratum": stratum, "node": nd, "year": year,
            "n_decider_matched": n,
            "status": wd._status(comp, tol),
            "tudef_warnings": warn["n_warning_lines"],
            "components": comp,
            "joint_dispy": joint,
            "localised_to": wd._localise(comp, components)})
    return {"year": year, "n_nodes": len(nodes_out), "nodes": nodes_out}


def _summarise(per_year, tol):
    """Distribution of |clean - stored| by stratum + component, across all sampled
    nodes/years."""
    rows = []
    for yr in per_year:
        for nd in yr.get("nodes", []):
            if nd.get("status") in ("BLOCKED", None):
                continue
            comp = nd.get("components", {})
            for c, v in comp.items():
                rows.append({"stratum": nd["stratum"], "component": c,
                             "max_abs": v["max_abs"], "n_above_tol": v["n_above_tol"],
                             "node_status": nd["status"]})
    df = pd.DataFrame(rows)
    summ = {}
    if len(df):
        for (st, c), g in df.groupby(["stratum", "component"]):
            a = g["max_abs"].to_numpy()
            summ.setdefault(st, {})[c] = {
                "n_nodes": int(len(g)),
                "n_nodes_above_tol": int((g["n_above_tol"] > 0).sum()),
                "max_abs_diff": float(np.nanmax(a)) if len(a) else 0.0,
                "median_abs_diff": float(np.nanmedian(a)) if len(a) else 0.0,
                "mean_abs_diff": float(np.nanmean(a)) if len(a) else 0.0}
        # per-stratum node pass/fail
        node_rows = [(nd["stratum"], nd["status"]) for yr in per_year
                     for nd in yr.get("nodes", []) if nd.get("status") not in ("BLOCKED", None)]
        nd_df = pd.DataFrame(node_rows, columns=["stratum", "status"])
        for st, g in nd_df.groupby("stratum"):
            summ.setdefault(st, {})["_node_pass_fail"] = {
                "n_nodes": int(len(g)),
                "n_pass": int((g["status"] == "PASS").sum()),
                "n_fail": int((g["status"] == "FAIL").sum())}
    return summ


def _impact_screen(per_year, mass_csv):
    """Task 4 — first-order plausibility screen, NO re-estimation. For each sampled
    node, pair the clean-vs-stored ils_dispy magnitude with whether it is the chosen
    node and (for nonchosen) the household's theta_hat collision-exposed prob mass.
    Returns a qualitative bounded statement, not a re-estimated likelihood."""
    mass = pd.read_csv(mass_csv).set_index("stacked_hh_uid")["exposed_prob_mass"].to_dict()
    items = []
    for yr in per_year:
        for nd in yr.get("nodes", []):
            if nd.get("status") in ("BLOCKED", None):
                continue
            comp = nd.get("components", {})
            disp = comp.get("ils_dispy", {}).get("max_abs", 0.0)
            hh = nd["node"]["stacked_hh_uid"]
            items.append({"stratum": nd["stratum"], "is_chosen": nd["stratum"] == "chosen_exposed",
                          "dispy_abs_diff": float(disp),
                          "hh_exposed_prob_mass": float(mass.get(hh, float("nan")))})
    df = pd.DataFrame(items)
    out = {"n_sampled_nodes": int(len(df))}
    if len(df):
        chosen = df[df["is_chosen"]]
        nonchosen = df[~df["is_chosen"] & (df["stratum"] == "nonchosen_exposed")]
        out["chosen_nodes"] = {
            "n": int(len(chosen)),
            "median_dispy_abs_diff": float(np.nanmedian(chosen["dispy_abs_diff"])) if len(chosen) else None,
            "max_dispy_abs_diff": float(np.nanmax(chosen["dispy_abs_diff"])) if len(chosen) else None,
            "note": ("chosen alternative is ALWAYS collision-exposed (build shares "
                     "draw_joint=0 between chosen + first sim cell); its consumption "
                     "enters the likelihood directly via V_obs.")}
        if len(nonchosen):
            # weight magnitude by theta_hat prob mass: first-order |dV| proxy ~ dc only
            # qualitative; we report the product distribution, not a re-estimated LL.
            prod = nonchosen["dispy_abs_diff"] * nonchosen["hh_exposed_prob_mass"]
            out["nonchosen_nodes"] = {
                "n": int(len(nonchosen)),
                "median_dispy_abs_diff": float(np.nanmedian(nonchosen["dispy_abs_diff"])),
                "max_dispy_abs_diff": float(np.nanmax(nonchosen["dispy_abs_diff"])),
                "median_massweighted_dispy": float(np.nanmedian(prod)),
                "max_massweighted_dispy": float(np.nanmax(prod))}
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--mass-csv", required=True,
                    help="per-HH exposed prob mass CSV from run_stage2_couples_audit.py")
    args = ap.parse_args()

    cfg = wc.load_config(args.config)
    cfg2 = cfg["stage2"]
    rs = cfg2["couples_contamination_audit"]["reprice_sample"]
    components = list(rs["components"])
    tol = float(rs["tol"])
    cov = rs.get("country_override")
    bc = wd.build_constants(cfg2["build_module"])

    import os
    import tempfile
    em_log = Path(args.out_json).with_name("stage2_couples_reprice_euromod_console.log")
    _tmp = tempfile.TemporaryFile(mode="w+b")  # noqa: SIM115 (manual fd-redirect lifecycle)
    _so, _se = os.dup(1), os.dup(2)
    os.dup2(_tmp.fileno(), 1)
    os.dup2(_tmp.fileno(), 2)
    try:
        per_year = [_reprice_year(cfg2, bc, year=y, rs=rs, components=components,
                                  tol=tol, country_override=cov)
                    for y in rs["years"]]
    finally:
        os.dup2(_so, 1)
        os.dup2(_se, 2)
        os.close(_so)
        os.close(_se)
        _tmp.seek(0)
        console = _tmp.read().decode("utf-8", errors="replace")
        _tmp.close()
    em_log.write_text(console, encoding="utf-8")

    out = {"increment": "stage2_couples_contamination_audit_v1__task3_4",
           "no_welfare_finding": True, "measures_touched": ["W3_only"],
           "re_estimated": False, "priced_any_redrawn_node": False,
           "computed_v_dir": False, "wrote_parquet": False,
           "node_key": KEY, "tol": tol,
           "euromod_console_log": str(em_log),
           "task3_reprice_per_year": per_year,
           "task3_magnitude_summary": _summarise(per_year, tol),
           "task4_impact_screen": _impact_screen(per_year, args.mass_csv)}
    out["scope_statement"] = (
        "Audit-only. EUROMOD run only on existing-node clean-reprice subsets; no redrawn "
        "node priced, nothing re-estimated, no V_i^dir computed, no parquet written. "
        "Task 4 is a first-order plausibility screen, NOT a re-estimated likelihood.")

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"[stage2:couples-reprice] wrote {args.out_json}")
    for st, comps in out["task3_magnitude_summary"].items():
        pf = comps.get("_node_pass_fail", {})
        ben = comps.get("ils_ben", {})
        org = comps.get("ils_origy", {})
        print(f"  {st}: nodes={pf.get('n_nodes')} pass={pf.get('n_pass')} "
              f"fail={pf.get('n_fail')} | ils_ben max={ben.get('max_abs_diff', 0):.2f} "
              f"| ils_origy max={org.get('max_abs_diff', 0):.2f}")


if __name__ == "__main__":
    main()
