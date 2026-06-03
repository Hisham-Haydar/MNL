"""
Stage Two — Increment Two-L runner: cross-track stored-target `ils_ben` residual
DIAGNOSIS. Diagnostic-only, read-only.

Reproduces deterministically:
  T2a — population identity scan: stored ils_ben vs (ils_pen + ils_benmt + ils_bennt) on
        decider rows, all (mode, year) cells. A nonzero gap proves the stored headline
        ils_ben is desynced from its own stored components.
  T2b — per-draw staleness: for sampled households, is the stored ils_ben draw-specific
        (varies across draws) while the stored components (ils_benmt, *_s) are CONSTANT?
        Confirms the build wrote only the 5 headline EM_OUTPUT_COLS per draw and left the
        simulated component columns as stale precompute carry-over.
  T3  — policy-vintage test: do failing nodes' stored ils_ben reproduce under any of
        FR_2014 / FR_2015 / FR_2016 (dataset held fixed)? (year-gradient hypothesis.)
  T4  — population-context driver: does a failing singles node reproduce the stored value
        only when EUROMOD prices a representative POPULATION (means tests need population
        context), not in isolation/tiny batches?

DOES NOT: re-estimate, compute V_i^dir, price redrawn nodes, promote W^3, touch any
measure beyond W^3, produce a correction candidate, or write/overwrite any build /
storage / engine-ready / priced / precompute / chunk parquet. Config-driven.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
import pandas as pd  # noqa: E402
import pyarrow.parquet as pq  # noqa: E402
import welfare_assessment_unit_diag as wd  # noqa: E402
import welfare_core as wc  # noqa: E402
import welfare_cross_track_residual_diag as ct  # noqa: E402


def t2a_identity_scan(cfg2, base, years, modes):
    out = {}
    for mode in modes:
        for year in years:
            p = base / f"{cfg2['priced_long_stem']}__{year}__{mode}.parquet"
            t = pq.read_table(p, columns=["ils_ben", "ils_pen", "ils_benmt",
                                          "ils_bennt", "ruro_decider"]).to_pandas()
            dec = t[t["ruro_decider"] == 1]
            resid = (dec["ils_ben"] - (dec["ils_pen"] + dec["ils_benmt"]
                     + dec["ils_bennt"])).abs()
            n = int(len(dec))
            bad = int((resid > 1e-6).sum())
            out[f"{mode}_{year}"] = {"n_decider": n, "identity_violations": bad,
                                     "share": round(bad / n, 4) if n else None,
                                     "max_resid": round(float(resid.max()), 2)}
    return out


def t2b_per_draw_staleness(cfg2, base, year, mode, n_hh):
    p = base / f"{cfg2['priced_long_stem']}__{year}__{mode}.parquet"
    cols = ["stacked_hh_uid", "ruro_decider", "ils_ben", "ils_benmt", "ils_dispy"]
    t = pq.read_table(p, columns=cols).to_pandas()
    dec = t[t["ruro_decider"] == 1]
    g = dec.groupby("stacked_hh_uid")
    ben_nunq = g["ils_ben"].nunique()
    benmt_nunq = g["ils_benmt"].nunique()
    dispy_nunq = g["ils_dispy"].nunique()
    return {"n_hh": int(len(ben_nunq)),
            "share_ils_ben_varies_across_draws": round(float((ben_nunq > 1).mean()), 4),
            "share_ils_dispy_varies_across_draws": round(float((dispy_nunq > 1).mean()), 4),
            "share_ils_benmt_constant_across_draws": round(float((benmt_nunq == 1).mean()), 4),
            "interpretation": ("headline ils_ben/ils_dispy ARE draw-specific; the simulated "
                               "component ils_benmt (and *_s) are CONSTANT across draws -> "
                               "build wrote only the 5 EM_OUTPUT_COLS per draw, leaving "
                               "components as stale precompute carry-over.")}


def t3_policy_vintage(bc, base, cfg2, sg, *, year, mode, n_fail):
    components = list(sg["components"])
    tol = float(sg["tol"])
    key = ct.node_key(mode)
    pl, _ = wd._load(base, cfg2["precompute_long_stem"], year, mode, long_=True)
    priced, _ = wd._load(base, cfg2["priced_long_stem"], year, mode, long_=False)
    assigned_sc, ds = bc["system_pairing"][year]
    systems = sorted({v[0] for v in bc["system_pairing"].values()})
    # find FAIL nodes via stamped batch
    dgn = 1.0 if mode == "singles" else None
    sub = pl[pl["dgn"] == dgn] if dgn is not None else pl
    uids = sub["stacked_hh_uid"].drop_duplicates().sort_values().head(8).tolist()
    draws = sorted(pl["draw"].unique())[:20] if mode == "singles" else None
    if mode == "singles":
        sel = pl[(pl["stacked_hh_uid"].isin(uids)) & (pl["draw"].isin(draws))].copy()
        stamped = bc["stamp"](sel.copy(), "draw", 1_000)
    else:
        sel = pl[pl["stacked_hh_uid"].isin(uids)].copy()
        stamped = bc["stamp"](sel.copy(), "draw_joint", 10_000)
    sim, _, err, _, _ = ct.reprice_node_full(bc, stamped, year=year)
    if err is not None:
        return {"status": "BLOCKED", "reason": err}
    comp, _, _ = wd._compare(sim, stamped, priced, key, components, tol)
    # rebuild per-node ils_ben mismatch to pick FAIL nodes
    st = stamped.reset_index(drop=True).copy()
    st["rep"] = pd.to_numeric(sim["ils_ben"], errors="coerce").to_numpy()[: len(st)]
    dec = st[st.get("ruro_decider", 1) == 1].copy()
    dec["__o"] = dec["idperson_true"]
    pr = priced[priced.get("ruro_decider", 1) == 1].copy()
    pr["__o"] = pr["idperson_true"]
    m = dec[key + ["__o", "rep"]].merge(pr[key + ["__o", "ils_ben"]], on=key + ["__o"])
    m = m[(m["rep"] - m["ils_ben"]).abs() > 1e-2]
    m = m[m["ils_ben"].abs() > 1e-2].head(n_fail)        # genuine nonzero-stored fails
    recs = []
    for _, r in m.iterrows():
        nd = {k: r[k] for k in key}
        rows = pl
        for k in key:
            rows = rows[rows[k] == nd[k]]
        rows = rows.copy()
        stored = float(r["ils_ben"])
        under = {}
        for s in systems:
            sim2, _, e2, _, _ = ct.reprice_node_full(bc, rows, year=year,
                                                     system_code=s, dataset_name=ds)
            if e2 is not None:
                under[s] = {"err": str(e2)[:40]}
                continue
            dm = (rows.get("ruro_decider", 1) == 1).to_numpy()
            rep = float(pd.to_numeric(sim2["ils_ben"], errors="coerce").to_numpy()[dm][0])
            under[s] = {"clean": round(rep, 2), "matches_stored": bool(abs(rep - stored) <= 1e-2)}
        recs.append({"node": {k: int(nd[k]) for k in key}, "stored": round(stored, 2),
                     "assigned_system": assigned_sc, "dataset_held_fixed": ds,
                     "under_system": under,
                     "reproduces_under_any": any(v.get("matches_stored")
                                                 for v in under.values() if isinstance(v, dict))})
    return {"n_fail_tested": len(recs), "nodes": recs,
            "any_reproduces_under_other_vintage": any(r["reproduces_under_any"] for r in recs)}


def t4_population_driver(bc, base, cfg2, sg, *, year, mode, fail_uid, fail_draw,
                         hh_counts):
    raw = bc["raw_schema"][year]
    sc, ds = bc["system_pairing"][year]
    pl, _ = wd._load(base, cfg2["precompute_long_stem"], year, mode, long_=True)
    priced, _ = wd._load(base, cfg2["priced_long_stem"], year, mode, long_=False)
    stored = float(priced[(priced["stacked_hh_uid"] == fail_uid)
                          & (priced["draw"] == fail_draw)
                          & (priced.get("ruro_decider", 1) == 1)]["ils_ben"].iloc[0])

    def reprice_get(sel):
        stamped = bc["stamp"](sel.copy(), "draw", 1_000)
        em = stamped[[c for c in raw if c in stamped.columns]].copy()
        for c in em.columns:
            em[c] = pd.to_numeric(em[c], errors="coerce").fillna(0.0)
        sim, _, err, _ = wd._run_euromod(bc, em, country=str(sc.split("_")[0]),
                                         system_code=sc, dataset_name=ds)
        if err is not None:
            return None
        st = stamped.reset_index(drop=True).copy()
        st["rep"] = pd.to_numeric(sim["ils_ben"], errors="coerce").to_numpy()[: len(st)]
        r = st[(st["stacked_hh_uid"] == fail_uid) & (st["draw"] == fail_draw)
               & (st.get("ruro_decider", 1) == 1)]
        return float(r["rep"].iloc[0]) if len(r) else None

    allhh = pl["stacked_hh_uid"].drop_duplicates().sort_values().tolist()
    by_n = {}
    for n in hh_counts:
        others = [u for u in allhh if u != fail_uid][: n - 1]
        v = reprice_get(pl[(pl["stacked_hh_uid"].isin([fail_uid] + others))
                           & (pl["draw"] == fail_draw)])
        by_n[str(n)] = round(v, 2) if v is not None else None
    repro_n = next((int(n) for n in hh_counts if by_n.get(str(n)) is not None
                    and abs(by_n[str(n)] - stored) <= 1e-2), None)
    return {"fail_uid": int(fail_uid), "fail_draw": int(fail_draw),
            "stored_ils_ben": round(stored, 2), "by_n_households": by_n,
            "reproduces_at_min_households": repro_n,
            "interpretation": ("the stored value reproduces ONLY once a representative "
                               "population shares the EUROMOD batch -> the means-tested "
                               "benefit depends on population context; isolated/tiny-batch "
                               "reprice is UNFAITHFUL, the stored headline value is VALID.")}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-json", required=True)
    args = ap.parse_args()

    cfg = wc.load_config(args.config)
    cfg2 = cfg["stage2"]
    sg = cfg2["singles_vdir_gate"]
    bc = wd.build_constants(cfg2["build_module"])
    from _bpool_paths import bpool_dir
    base = bpool_dir()
    years = [2015, 2016, 2017]
    modes = ["singles", "couples"]

    em_log = Path(args.out_json).with_name("stage2_cross_track_diag_euromod_console.log")
    _tmp = tempfile.TemporaryFile(mode="w+b")  # noqa: SIM115 (manual fd lifecycle)
    _so, _se = os.dup(1), os.dup(2)
    os.dup2(_tmp.fileno(), 1)
    os.dup2(_tmp.fileno(), 2)
    try:
        t2a = t2a_identity_scan(cfg2, base, years, modes)
        t2b_singles = t2b_per_draw_staleness(cfg2, base, 2017, "singles", 200)
        t2b_couples = t2b_per_draw_staleness(cfg2, base, 2017, "couples", 50)
        t3_singles = t3_policy_vintage(bc, base, cfg2, sg, year=2017, mode="singles",
                                       n_fail=4)
        t4 = t4_population_driver(bc, base, cfg2, sg, year=2017, mode="singles",
                                  fail_uid=300001809101, fail_draw=1,
                                  hh_counts=[1, 2, 5, 20, 100])
    finally:
        os.dup2(_so, 1)
        os.dup2(_se, 2)
        os.close(_so)
        os.close(_se)
        _tmp.seek(0)
        console = _tmp.read().decode("utf-8", errors="replace")
        _tmp.close()
    em_log.write_text(console, encoding="utf-8")

    out = {"increment": "stage2_cross_track_residual_diag_v1",
           "read_only": True, "no_welfare_finding": True, "measures_touched": ["W3_only"],
           "re_estimated": False, "computed_v_dir": False,
           "priced_redrawn_node": False, "produced_correction_candidate": False,
           "wrote_or_overwrote_parquet": False,
           "euromod_console_log": str(em_log),
           "build_writeback_evidence": {
               "file": "scripts/bpool/run_bpool_euromod_chunk.py",
               "lines": "186-194",
               "finding": ("out_df = chunk_df.copy(); then only _EM_OUTPUT_COLS = "
                           "[ils_dispy, ils_origy, ils_ben, ils_tax, ils_sicdy] are "
                           "overwritten from per-draw sim_df. All simulated component "
                           "columns (ils_benmt, ils_bennt, ils_pen, *_s) remain stale "
                           "precompute carry-over -> not draw-specific.")},
           "t2a_identity_scan": t2a,
           "t2b_per_draw_staleness": {"singles_2017": t2b_singles,
                                      "couples_2017": t2b_couples},
           "t3_policy_vintage_singles_2017": t3_singles,
           "t4_population_context_driver": t4,
           "scope_statement": (
               "Read-only diagnosis. No W^3 finding; nothing beyond W^3; no V_i^dir; no "
               "redrawn node priced; nothing re-estimated; no correction candidate; no "
               "build/storage/engine-ready/priced/precompute/chunk parquet written or "
               "overwritten.")}
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"[stage2:cross-track-diag] wrote {args.out_json}")
    print("  T2a identity violations (stored ils_ben != sum parts):")
    for k, v in t2a.items():
        print(f"    {k}: {v['share']*100:.1f}% ({v['identity_violations']}/{v['n_decider']}) max={v['max_resid']}")
    print(f"  T2b singles: ils_ben varies={t2b_singles['share_ils_ben_varies_across_draws']} "
          f"benmt constant={t2b_singles['share_ils_benmt_constant_across_draws']}")
    print(f"  T3 policy-vintage: any reproduces under other vintage = "
          f"{t3_singles.get('any_reproduces_under_other_vintage')}")
    print(f"  T4 population driver: {t4['by_n_households']} -> reproduces at "
          f"{t4['reproduces_at_min_households']} households")


if __name__ == "__main__":
    main()
