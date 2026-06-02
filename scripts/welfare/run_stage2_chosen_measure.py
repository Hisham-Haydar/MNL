"""
Stage Two — Increment Two-G, Task 4 + Task 5: measure CHOSEN-alternative contamination
on a large deterministic couples sample, and a first-order theta_hat influence screen.

Task 4 — clean-reprice the chosen alternative only, (draw_joint=0, draw_male=0,
  draw_female=0), isolated roster + original IDs, for a large deterministic sample of
  households across years. Compare clean vs stored NOMINAL (ils_dispy/origy/ben/tax/
  sicdy + household-joint disposable) AND the exact estimator consumption variable
  (c_norm = joint ils_dispy_real / c_scale). Report |clean - stored| distributions,
  shares above material thresholds, component localisation.

Task 5 — first-order theta_hat influence screen (NO re-estimation): reuse the
  welfare/estimator couples V machinery; for each sampled HH compute stored V_chosen,
  clean V_chosen (replace ONLY the chosen alt's consumption with the clean value,
  holding all other alternatives fixed), Delta V_chosen, stored P_chosen, clean
  P_chosen, Delta P_chosen, and an approximate change in the household log-likelihood
  contribution. This is a first-order screen, NOT a re-estimation and NOT proof of
  parameter movement.

Audit-only: prices no redrawn node, writes no parquet, computes no V_i^dir,
re-estimates nothing.
"""
from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import welfare_assessment_unit_diag as wd  # noqa: E402
import welfare_chosen_contamination as cc  # noqa: E402
import welfare_core as wc  # noqa: E402

CHOSEN = {"draw_joint": 0, "draw_male": 0, "draw_female": 0}


def _clean_reprice_chosen(cfg2, bc, *, year, hh_list, components, tol, cov, pl, priced):
    """Clean-reprice the chosen node (0,0,0) for ALL hh in hh_list in ONE collision-free
    batched EUROMOD call (collision-free full-node-key stamping makes every household's
    chosen roster globally unique, so there is no cross-/within-household collision; Task 1
    verified collision-free batch == isolated clean to machine tolerance). This avoids one
    EUROMOD model-load per household. Returns a per-hh dict list with stored/clean nominal
    components + joint disposable."""
    system_code, dataset_name = bc["system_pairing"][year]
    country = str(cov or str(system_code).split("_")[0])
    raw_cols = bc["raw_schema"][year]

    chosen = pl[(pl["draw_joint"] == 0) & (pl["draw_male"] == 0) & (pl["draw_female"] == 0)
                & (pl["stacked_hh_uid"].isin(hh_list))].copy()
    stamped = cc._collisionfree_stamp(chosen)            # unique per node; original in *_true
    em = wd._em_input(stamped, raw_cols)
    sim, warn, err, _ = wd._run_euromod(bc, em, country=country,
                                        system_code=system_code, dataset_name=dataset_name)
    out = []
    if err is not None or sim is None:
        for hh in hh_list:
            out.append({"hh": int(hh), "status": "BLOCKED", "reason": err or "no sim"})
        return out

    rep_cols = ["ils_dispy"] + [c for c in components if c in sim.columns]
    st = stamped.reset_index(drop=True).copy()
    for c in rep_cols:
        st[f"__rep_{c}"] = pd.to_numeric(sim[c], errors="coerce").to_numpy()[: len(st)]
    # keep ONLY keys + repriced cols on the left, so the priced merge does not collide
    # with precompute's own carried ils_* output columns (which we must not use).
    keep = ["stacked_hh_uid", "idperson_true"] + [f"__rep_{c}" for c in rep_cols]
    dec = st.loc[st.get("ruro_decider", 1) == 1, keep].copy()
    dec["__orig_idperson"] = dec["idperson_true"]

    # stored priced chosen-node deciders, keyed by original idperson
    prn = priced[(priced["draw_joint"] == 0) & (priced["draw_male"] == 0)
                 & (priced["draw_female"] == 0) & (priced.get("ruro_decider", 1) == 1)
                 & (priced["stacked_hh_uid"].isin(hh_list))].copy()
    pid = "idperson_true" if "idperson_true" in prn.columns else "idperson"
    prn["__orig_idperson"] = prn[pid]

    for hh in hh_list:
        d = dec[dec["stacked_hh_uid"] == hh]
        p = prn[prn["stacked_hh_uid"] == hh]
        if len(d) == 0 or len(p) == 0:
            out.append({"hh": int(hh), "status": "BLOCKED", "reason": "node/stored absent"})
            continue
        m = d.merge(p[["__orig_idperson"] + ["ils_dispy"] + [c for c in components if c in p.columns]],
                    on="__orig_idperson", how="inner")
        comp = {}
        for c in ["ils_dispy"] + [c for c in components if c in m.columns and f"__rep_{c}" in m.columns]:
            diff = np.abs(pd.to_numeric(m[f"__rep_{c}"], errors="coerce").to_numpy()
                          - pd.to_numeric(m[c], errors="coerce").to_numpy())
            comp[c] = {"n_above_tol": int((diff > tol).sum()),
                       "max_abs": float(np.nanmax(diff)) if len(diff) else 0.0}
        bad = any(v["n_above_tol"] > 0 for k, v in comp.items() if k != "ils_dispy")
        clean_dispy = float(pd.to_numeric(m["__rep_ils_dispy"], errors="coerce").sum())
        stored_dispy = float(pd.to_numeric(m["ils_dispy"], errors="coerce").sum())
        out.append({
            "hh": int(hh), "year": int(year),
            "status": "FAIL" if bad else "PASS",
            "tudef": int(warn["n_warning_lines"]),
            "components": {k: v for k, v in comp.items() if k != "ils_dispy"},
            "joint_dispy": None,
            "localised_to": (max([k for k in comp if k != "ils_dispy"],
                                 key=lambda k: comp[k]["max_abs"]) if bad else None),
            "joint_dispy_nominal": {"clean": clean_dispy, "stored": stored_dispy,
                                    "abs_diff": abs(clean_dispy - stored_dispy)}})
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--n-hh-per-year", type=int, default=120)
    args = ap.parse_args()

    cfg = wc.load_config(args.config)
    cfg2 = cfg["stage2"]
    rs = cfg2["couples_contamination_audit"]["reprice_sample"]
    components = list(rs["components"])
    tol = float(rs["tol"])
    cov = rs.get("country_override")
    bc = wd.build_constants(cfg2["build_module"])
    bm = importlib.import_module(cfg2["build_module"])
    cpi = bm._CPI
    from _bpool_paths import bpool_dir
    base = bpool_dir()

    # ---- material thresholds (nominal euro/month on |Δ joint disposable|) ----
    material_thresholds = [1.0, 10.0, 50.0, 100.0, 250.0]

    # ---- Task 4: clean-reprice chosen node on a large deterministic sample ----
    em_log = Path(args.out_json).with_name("stage2_chosen_measure_euromod_console.log")
    _tmp = tempfile.TemporaryFile(mode="w+b")  # noqa: SIM115 (manual fd lifecycle)
    _so, _se = os.dup(1), os.dup(2)
    os.dup2(_tmp.fileno(), 1)
    os.dup2(_tmp.fileno(), 2)
    per_year_records = {}
    try:
        for year in rs["years"]:
            pl, _ = wd._load(base, cfg2["precompute_long_stem"], year, "couples", long_=True)
            priced, _ = wd._load(base, cfg2["priced_long_stem"], year, "couples", long_=False)
            hh_list = (pl["stacked_hh_uid"].drop_duplicates().sort_values()
                       .head(args.n_hh_per_year).tolist())
            per_year_records[year] = _clean_reprice_chosen(
                cfg2, bc, year=year, hh_list=hh_list, components=components, tol=tol,
                cov=cov, pl=pl, priced=priced)
    finally:
        os.dup2(_so, 1)
        os.dup2(_se, 2)
        os.close(_so)
        os.close(_se)
        _tmp.seek(0)
        console = _tmp.read().decode("utf-8", errors="replace")
        _tmp.close()
    em_log.write_text(console, encoding="utf-8")

    # flatten to a per-hh frame
    rows = []
    for year, recs in per_year_records.items():
        for rec in recs:
            if rec.get("status") in ("BLOCKED", None):
                continue
            jd = rec.get("joint_dispy_nominal", {})
            comp = rec.get("components", {})
            rows.append({
                "hh": rec["hh"], "year": year, "status": rec["status"],
                "tudef": rec["tudef"],
                "joint_dispy_abs_diff": jd.get("abs_diff", float("nan")),
                "clean_joint_dispy": jd.get("clean", float("nan")),
                "stored_joint_dispy": jd.get("stored", float("nan")),
                "ils_ben_max_abs": comp.get("ils_ben", {}).get("max_abs", 0.0),
                "ils_tax_max_abs": comp.get("ils_tax", {}).get("max_abs", 0.0),
                "ils_origy_max_abs": comp.get("ils_origy", {}).get("max_abs", 0.0),
                "ils_sicdy_max_abs": comp.get("ils_sicdy", {}).get("max_abs", 0.0),
                "localised_to": rec.get("localised_to"),
            })
    df = pd.DataFrame(rows)

    def _dist(a):
        a = np.asarray(a, dtype=float)
        a = a[np.isfinite(a)]
        if not len(a):
            return {}
        qs = [0.0, 0.5, 0.9, 0.99, 1.0]
        return {"n": int(len(a)), "mean": float(a.mean()), "median": float(np.median(a)),
                "max": float(a.max()),
                "quantiles": {str(q): float(np.quantile(a, q)) for q in qs}}

    task4 = {
        "n_sampled_hh": int(len(df)),
        "n_fail_clean_reprice": int((df["status"] == "FAIL").sum()) if len(df) else 0,
        "share_fail_clean_reprice": float((df["status"] == "FAIL").mean()) if len(df) else 0.0,
        "income_contrib_machine_zero": {
            "ils_origy_max_over_sample": float(df["ils_origy_max_abs"].max()) if len(df) else None,
            "ils_sicdy_max_over_sample": float(df["ils_sicdy_max_abs"].max()) if len(df) else None},
        "joint_dispy_abs_diff_distribution": _dist(df["joint_dispy_abs_diff"]) if len(df) else {},
        "ils_ben_abs_diff_distribution": _dist(df["ils_ben_max_abs"]) if len(df) else {},
        "share_above_material_thresholds_joint_dispy": {
            str(t): float((df["joint_dispy_abs_diff"] > t).mean()) for t in material_thresholds
        } if len(df) else {},
        "n_above_material_thresholds_joint_dispy": {
            str(t): int((df["joint_dispy_abs_diff"] > t).sum()) for t in material_thresholds
        } if len(df) else {},
        "component_localisation_counts": (
            df["localised_to"].value_counts().to_dict() if len(df) else {}),
        "material_thresholds_eur_per_month": material_thresholds,
        "tudef_max_over_sample": int(df["tudef"].max()) if len(df) else None,
    }

    # ---- Task 5: first-order theta_hat influence screen ----
    task5 = _influence_screen(cfg, df, cpi)

    out = {"increment": "stage2_couples_chosen_contamination_v1__task4_5",
           "no_welfare_finding": True, "measures_touched": ["W3_only"],
           "re_estimated": False, "priced_any_redrawn_node": False,
           "computed_v_dir": False, "wrote_parquet": False,
           "chosen_node": CHOSEN, "n_hh_per_year": args.n_hh_per_year,
           "euromod_console_log": str(em_log),
           "task4_chosen_contamination": task4,
           "task5_influence_screen": task5,
           "scope_statement": (
               "Audit-only. EUROMOD on existing chosen-node clean reprices only; no "
               "redrawn node priced, nothing re-estimated, no V_i^dir computed, no "
               "parquet written. Task 5 is a first-order screen, NOT a re-estimated "
               "likelihood and NOT proof of theta_hat movement.")}

    if len(df):
        df.to_csv(args.out_csv, index=False)
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"[stage2:chosen-measure] wrote {args.out_json}")
    t4 = task4
    print(f"  Task4: {t4['n_sampled_hh']} hh | fail clean reprice "
          f"{t4['n_fail_clean_reprice']} ({t4['share_fail_clean_reprice']*100:.1f}%) | "
          f"joint-dispy |diff| median="
          f"{t4['joint_dispy_abs_diff_distribution'].get('median', float('nan')):.2f} "
          f"max={t4['joint_dispy_abs_diff_distribution'].get('max', float('nan')):.2f}")
    print(f"  Task4 share |diff joint-dispy|> thresholds: {t4['share_above_material_thresholds_joint_dispy']}")
    if task5.get("status") == "ok":
        print(f"  Task5: |dV_chosen| median={task5['dV_chosen']['median']:.4f} "
              f"max={task5['dV_chosen']['max']:.4f} | |dP_chosen| median={task5['dP_chosen']['median']:.3e} "
              f"max={task5['dP_chosen']['max']:.3e} | |d_ll_i| median={task5['d_ll_i']['median']:.4f} "
              f"max={task5['d_ll_i']['max']:.4f}")
    else:
        print(f"  Task5 status: {task5.get('status')} -- {task5.get('reason')}")


def _influence_screen(cfg, df, cpi):
    """First-order theta_hat influence: reuse welfare_core couples V; replace ONLY the
    chosen alt's consumption with the clean value and recompute V_chosen, P_chosen, ll_i."""
    import jax.numpy as jnp
    import welfare_couples_contamination_audit as au
    if not len(df):
        return {"status": "no_sample"}
    spec = wc.load_spec(cfg)
    theta = wc.load_theta(cfg, spec)
    data = wc.load_data(cfg, n_hh=0)
    wc.assert_resolution(cfg, data)
    cou = data["couples"]
    n_groups = int(cou.n_groups)
    n_alts = int(cou.n_obs // cou.n_groups)
    c_scale = _c_scale(cfg)

    ordered = au._reproduce_engine_order(cfg["baseline"])
    cons = np.maximum(np.asarray(cou.consumption, dtype=np.float64), 1e-12)
    if float(np.nanmax(np.abs(cons - np.maximum(ordered["c_norm"].to_numpy(np.float64), 1e-12)))) > 1e-9:
        return {"status": "mapping_ambiguous", "reason": "alignment failed in Task5"}

    Vfn, _ = wc._build_V_extractor_couples(cou, spec)
    th = jnp.asarray(theta)
    V0 = np.asarray(Vfn(th, jnp.asarray(cons)))
    Vg0 = V0.reshape(n_groups, n_alts)

    # locate the chosen alt position per group: is_chosen_joint==1 (== (0,0,0))
    chosen = (ordered["is_chosen_joint"].to_numpy() == 1).reshape(n_groups, n_alts)
    hh_grid = ordered["stacked_hh_uid"].to_numpy().reshape(n_groups, n_alts)[:, 0]
    chosen_pos = chosen.argmax(axis=1)                          # one chosen per HH

    # map sampled (hh -> clean joint nominal dispy); clean c_norm = clean_real / c_scale
    clean_map = {}
    for _, r in df.iterrows():
        if not np.isfinite(r["clean_joint_dispy"]):
            continue
        phi = float(cpi.get(int(r["year"]), 1.0))
        clean_map[int(r["hh"])] = (float(r["clean_joint_dispy"]) * phi) / c_scale

    # build a clean consumption grid: replace chosen alt's c_norm for sampled HHs only
    cons_grid = cons.reshape(n_groups, n_alts).copy()
    rows_idx = []
    for gi in range(n_groups):
        hh = int(hh_grid[gi])
        if hh in clean_map:
            cons_grid[gi, chosen_pos[gi]] = max(clean_map[hh], 1e-12)
            rows_idx.append(gi)
    V1 = np.asarray(Vfn(th, jnp.asarray(cons_grid.reshape(-1)))).reshape(n_groups, n_alts)

    def _lse(Vg):
        mx = Vg.max(axis=1, keepdims=True)
        return (mx[:, 0] + np.log(np.exp(Vg - mx).sum(axis=1)))
    lse0 = _lse(Vg0)
    lse1 = _lse(V1)
    gi = np.asarray(rows_idx, dtype=int)
    cp = chosen_pos[gi]
    Vc0 = Vg0[gi, cp]
    Vc1 = V1[gi, cp]
    P0 = np.exp(Vc0 - lse0[gi])
    P1 = np.exp(Vc1 - lse1[gi])
    dV = Vc1 - Vc0
    dP = P1 - P0
    # household LL contribution at the OBSERVED (chosen) alt = V_chosen - lse
    ll0 = Vc0 - lse0[gi]
    ll1 = Vc1 - lse1[gi]
    d_ll = ll1 - ll0

    def _d(a):
        a = np.abs(np.asarray(a, float))
        a = a[np.isfinite(a)]
        if not len(a):
            return {}
        qs = [0.5, 0.9, 0.99, 1.0]
        return {"n": int(len(a)), "median": float(np.median(a)), "mean": float(a.mean()),
                "max": float(a.max()),
                "quantiles": {str(q): float(np.quantile(a, q)) for q in qs}}
    return {"status": "ok", "n_households_screened": int(len(gi)),
            "c_scale": c_scale,
            "dV_chosen": _d(dV), "dP_chosen": _d(dP), "d_ll_i": _d(d_ll),
            "stored_P_chosen": {"median": float(np.median(P0)), "mean": float(P0.mean()),
                                "min": float(P0.min()), "max": float(P0.max())},
            "note": ("first-order screen: only the chosen alt's consumption is replaced "
                     "by its clean reprice; all other alternatives held fixed; theta_hat "
                     "unchanged. NOT a re-estimation; NOT proof of parameter movement.")}


def _c_scale(cfg):
    from _bpool_paths import bpool_dir
    stem = cfg["baseline"]["couples_stem"]
    with open(bpool_dir() / f"{stem}__mnlmeta.json") as _f:
        meta = json.load(_f)
    norm = meta["normalization"]
    return float(norm["couples"]["c_scale"] if "couples" in norm else norm["c_scale"])


if __name__ == "__main__":
    main()
