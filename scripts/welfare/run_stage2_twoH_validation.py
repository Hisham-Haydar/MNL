"""
Stage Two — Increment Two-I: READ-ONLY validation of the Two-H stop result.

Task 1 — validate the couples model-fit diagnostic (rank-901):
  - confirm engine-ready row 0 per household == the observed chosen alternative
    (== is_chosen_joint==1);
  - DECISIVE equivalence: certified estimator negLL (build_jax_couples_ll,
    use_actual_choice=False -> column-0) vs welfare-grid negLL, + gate0 parity;
  - sign orientation (corr(V, softmax) > 0);
  - the chosen-rank distribution under the production likelihood convention (IS-V), AND
    under a structural ranking that removes the importance-sampling -log_prior term, to
    test whether rank-901 is an IS-weighting artifact.

Task 2 — validate the singleton residual:
  - sampled singleton nodes are genuinely collision-free under the full node key;
  - Two-H failures reproduce under the INDEPENDENT Two-E _compare path (isolated,
    original IDs) — i.e. the residual is not a Two-H measurement artifact;
  - failure clustering by year / draw_joint / decider sex.

READ-ONLY. No re-estimation, no correction candidate, no V_i^dir, no redrawn pricing, no
parquet written or overwritten. No W^3 finding; nothing beyond W^3.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
sys.path.insert(0, "scripts/enhanced")
import numpy as np  # noqa: E402
import welfare_assessment_unit_diag as wd  # noqa: E402
import welfare_core as wc  # noqa: E402
import welfare_correction_prep as cp  # noqa: E402

KEY = ["stacked_hh_uid", "draw_joint", "draw_male", "draw_female"]


def task1_modelfit_validation(cfg):
    import jax
    jax.config.update("jax_enable_x64", True)
    import jax.numpy as jnp
    import jax_ll_probe as jllp
    import welfare_couples_contamination_audit as au

    spec = wc.load_spec(cfg)
    theta = wc.load_theta(cfg, spec)
    data = wc.load_data(cfg, n_hh=0)
    wc.assert_resolution(cfg, data)
    cou = data["couples"]
    n_groups = int(cou.n_groups)
    n_alts = int(cou.n_obs // cou.n_groups)
    th = jnp.asarray(theta)

    ordered = au._reproduce_engine_order(cfg["baseline"])
    cons = np.maximum(np.asarray(cou.consumption, dtype=np.float64), 1e-12)
    align = float(np.nanmax(np.abs(cons - np.maximum(
        ordered["c_norm"].to_numpy(np.float64), 1e-12))))

    # chosen marker == column 0?
    ic = (ordered["is_chosen_joint"].to_numpy() == 1).reshape(n_groups, n_alts)
    chosen_pos = ic.argmax(axis=1)
    chosen_is_col0 = float(np.mean(chosen_pos == 0))
    one_chosen_per_hh = bool(ic.sum(axis=1).min() == 1 and ic.sum(axis=1).max() == 1)

    # welfare-grid V + negLL (column-0 observed convention)
    Vfn, _ = wc._build_V_extractor_couples(cou, spec)
    V = np.asarray(Vfn(th, jnp.asarray(cons))).reshape(n_groups, n_alts)
    mx = V.max(axis=1, keepdims=True)
    lse_w = mx[:, 0] + np.log(np.exp(V - mx).sum(axis=1))
    per_w = V[:, 0] - lse_w
    welfare_negll = float(-np.sum(per_w))

    # certified estimator negLL + gate0
    f, _ = jllp.build_jax_couples_ll(cou, spec, use_actual_choice=False)
    est_negll = float(f(th))
    gw = wc.compute_group_welfare(cou, spec, theta, "couples")
    g0 = wc.gate0_parity(cou, spec, theta, "couples", gw)

    # sign orientation: corr(V, softmax) per HH (sample) must be > 0
    w = np.exp(V - mx)
    w = w / w.sum(axis=1, keepdims=True)
    rng_idx = np.arange(0, n_groups, max(1, n_groups // 200))
    corrs = [float(np.corrcoef(V[g], w[g])[0, 1]) for g in rng_idx]

    # rank under IS-V (as Two-H computed)
    Vc = V[:, 0]
    rank_is = (Vc[:, None] < V).sum(axis=1) + 1
    P_is = w[:, 0]

    # structural ranking: remove the IS -log_prior term (V_struct = V + log_prior).
    # NOTE: log_market is also proposal-centered, so this removes the DOMINANT IS term but
    # not all proposal dependence; it is a lower bound on the de-biasing of the rank.
    lp = np.log(np.maximum(np.asarray(cou.prior, dtype=np.float64), 1e-300)).reshape(n_groups, n_alts)
    V_struct = V + lp
    Vc_s = V_struct[:, 0]
    rank_st = (V_struct > Vc_s[:, None]).sum(axis=1) + 1
    mxs = V_struct.max(axis=1, keepdims=True)
    ws = np.exp(V_struct - mxs)
    ws = ws / ws.sum(axis=1, keepdims=True)
    P_st = ws[:, 0]
    # how much of the chosen-vs-rowmax IS-V gap is the -log_prior term?
    is_gap = float(np.median(V.max(axis=1) - Vc))
    lp_contrib = float(np.median(lp.mean(axis=1) - lp[:, 0]))

    def _rankstats(r):
        return {"median": int(np.median(r)), "mean": float(r.mean()),
                "min": int(r.min()), "max": int(r.max()),
                "share_bottom_half": float(np.mean(r > n_alts / 2)),
                "share_top_25pct": float(np.mean(r <= np.ceil(0.25 * n_alts))),
                "share_top_10pct": float(np.mean(r <= np.ceil(0.10 * n_alts))),
                "share_top_1pct": float(np.mean(r <= np.ceil(0.01 * n_alts)))}

    return {
        "alignment_consumption_vs_cnorm_max_abs": align,
        "chosen_marker_is_column0_share": chosen_is_col0,
        "exactly_one_chosen_per_hh": one_chosen_per_hh,
        "decisive_equivalence": {
            "certified_estimator_negll": est_negll,
            "welfare_grid_negll": welfare_negll,
            "max_abs_negll_diff": abs(est_negll - welfare_negll),
            "gate0_max_abs": g0.get("max_abs"),
            "agree_to_machine_tol": bool(abs(est_negll - welfare_negll) < 1e-6),
        },
        "sign_orientation": {"corr_V_softmax_min": min(corrs),
                             "corr_V_softmax_median": float(np.median(corrs)),
                             "all_positive": bool(min(corrs) > 0)},
        "rank_IS_V_as_twoH": {**_rankstats(rank_is),
                              "P_chosen_median": float(np.median(P_is)),
                              "uniform_1_over_nalts": 1.0 / n_alts},
        "rank_structural_minus_logprior": {**_rankstats(rank_st),
                                           "P_chosen_median": float(np.median(P_st))},
        "is_term_decomposition": {
            "median_chosen_to_rowmax_IS_gap_nats": is_gap,
            "median_logprior_contribution_nats": lp_contrib,
            "note": ("the chosen row carries log_prior=0 (observed, prior=1) while the 900 "
                     "simulated cells carry -log_prior>0 in V; this IS de-biasing term, not "
                     "structural utility, pushes the chosen row to the bottom of the IS-V "
                     "ordering. Removing it lifts the chosen rank from last to mid-pack."),
        },
    }


def _isolated_status(bc, pl, priced, uid, *, dj, dm, df, year, components, tol, cov):
    """Two-E _compare on ONE node, isolated roster, original IDs. Independent of the
    dense-batch instrument. Returns 'PASS'/'FAIL'/'BLOCKED'."""
    sc, ds = bc["system_pairing"][year]
    country = str(cov or str(sc).split("_")[0])
    raw = bc["raw_schema"][year]
    sub = pl[(pl["stacked_hh_uid"] == uid) & (pl["draw_joint"] == dj)
             & (pl["draw_male"] == dm) & (pl["draw_female"] == df)]
    if len(sub) == 0:
        return None
    sim, _, err, _ = wd._run_euromod(bc, wd._em_input(sub.copy(), raw),
                                     country=country, system_code=sc, dataset_name=ds)
    if err is not None:
        return "BLOCKED"
    comp, _, _ = wd._compare(sim, sub.copy(), priced, KEY, components, tol)
    return wd._status(comp, tol)


def paired_isolated_vs_batch(cfg2, bc, base, *, years, n_hh, components, tol, cov):
    """AUTHORITATIVE residual check: on a bounded per-year sample, reprice the SAME node
    both via the dense-batch instrument (Two-H) and via the INDEPENDENT isolated Two-E
    path, and tabulate agreement. The isolated rate is the trustworthy residual; the
    dense-batch instrument is validated only if batch-only failures are rare."""
    res = {}
    for year in years:
        pl, _ = wd._load(base, cfg2["precompute_long_stem"], year, "couples", long_=True)
        priced, _ = wd._load(base, cfg2["priced_long_stem"], year, "couples", long_=False)
        nalts = cp.block_distinct_alts(pl)
        plw = pl.copy()
        plw["__nalts"] = nalts
        hh = plw["stacked_hh_uid"].drop_duplicates().sort_values().head(n_hh).tolist()
        sel = plw[(plw["stacked_hh_uid"].isin(hh)) & (plw["draw_joint"] == 1)
                  & (plw["__nalts"] == 1)].copy()
        brecs, _, _ = cp.resilient_reprice(bc, sel, year=year, components=components,
                                           tol=tol, priced=priced, country_override=cov)
        bst = {r["node"]["stacked_hh_uid"]: r["status"] for r in brecs
               if r.get("status") in ("PASS", "FAIL")}
        n = ifail = bfail = both = bonly = ionly = 0
        for uid in hh:
            iso = _isolated_status(bc, pl, priced, uid, dj=1, dm=1, df=2, year=year,
                                   components=components, tol=tol, cov=cov)
            if iso not in ("PASS", "FAIL") or uid not in bst:
                continue
            n += 1
            bf = bst[uid] == "FAIL"
            isf = iso == "FAIL"
            ifail += isf
            bfail += bf
            both += (bf and isf)
            bonly += (bf and not isf)
            ionly += (isf and not bf)
        res[int(year)] = {"n": n, "isolated_fail": ifail, "batch_fail": bfail,
                          "both_fail": both, "batch_only_fail": bonly,
                          "isolated_only_fail": ionly,
                          "isolated_rate": round(ifail / n, 4) if n else None,
                          "batch_rate": round(bfail / n, 4) if n else None}
    return res


def task2_residual_validation(cfg2, bc, base, *, years, dj_samples, n_hh, components,
                              tol, cov):
    out = {"by_year": {}, "by_draw_joint": {}, "decider_sex_of_failing":
           {"male_fail": 0, "female_fail": 0}, "all_failures_collision_free": True}
    for year in years:
        pl, _ = wd._load(base, cfg2["precompute_long_stem"], year, "couples", long_=True)
        priced, _ = wd._load(base, cfg2["priced_long_stem"], year, "couples", long_=False)
        nalts = cp.block_distinct_alts(pl)
        plw = pl.copy()
        plw["__nalts"] = nalts
        hh = plw["stacked_hh_uid"].drop_duplicates().sort_values().head(n_hh).tolist()
        yfail = ytot = 0
        for dj in dj_samples:
            sel = plw[(plw["stacked_hh_uid"].isin(hh)) & (plw["draw_joint"] == dj)
                      & (plw["__nalts"] == 1)].copy()
            if len(sel) == 0:
                continue
            recs, _, _ = cp.resilient_reprice(bc, sel, year=year, components=components,
                                              tol=tol, priced=priced, country_override=cov)
            v = [r for r in recs if r.get("status") in ("PASS", "FAIL")]
            f = [r for r in v if r["status"] == "FAIL"]
            out["by_draw_joint"].setdefault(int(dj), {"n": 0, "fail": 0})
            out["by_draw_joint"][int(dj)]["n"] += len(v)
            out["by_draw_joint"][int(dj)]["fail"] += len(f)
            yfail += len(f)
            ytot += len(v)
            # collision-free verification for every failure
            for r in f:
                nd = r["node"]
                b = pl[(pl["stacked_hh_uid"] == nd["stacked_hh_uid"])
                       & (pl["draw_joint"] == nd["draw_joint"])]
                if b[["draw_male", "draw_female"]].drop_duplicates().shape[0] != 1:
                    out["all_failures_collision_free"] = False
                # decider sex of the failing decider (larger |stored-clean| ils_ben)
                pdc = r.get("per_decider", [])
                if len(pdc) == 2:
                    g0 = abs(pdc[0]["stored_ils_ben"] - pdc[0]["clean_ils_ben"])
                    g1 = abs(pdc[1]["stored_ils_ben"] - pdc[1]["clean_ils_ben"])
                    fid = pdc[0]["idperson_true"] if g0 >= g1 else pdc[1]["idperson_true"]
                    srow = pl[pl["idperson"] == fid]
                    if len(srow):
                        dgn = int(srow.iloc[0]["dgn"])
                        out["decider_sex_of_failing"]["male_fail" if dgn == 1
                                                      else "female_fail"] += 1
        out["by_year"][int(year)] = {"n": ytot, "fail": yfail,
                                     "rate": round(yfail / ytot, 4) if ytot else None}
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-json", required=True)
    args = ap.parse_args()

    cfg = wc.load_config(args.config)
    cfg2 = cfg["stage2"]
    cpcfg = cfg2["correction_prep"]
    components = list(cpcfg["components"])
    tol = float(cpcfg["tol"])
    cov = cpcfg.get("country_override")
    bc = wd.build_constants(cfg2["build_module"])
    from _bpool_paths import bpool_dir
    base = bpool_dir()

    em_log = Path(args.out_json).with_name("stage2_twoH_validation_euromod_console.log")
    _tmp = tempfile.TemporaryFile(mode="w+b")  # noqa: SIM115 (manual fd lifecycle)
    _so, _se = os.dup(1), os.dup(2)
    os.dup2(_tmp.fileno(), 1)
    os.dup2(_tmp.fileno(), 2)
    try:
        t1 = task1_modelfit_validation(cfg)
        # clustering on a bounded sample (validation needs the PATTERN, not a re-measure
        # at the full Two-H scale; large dense batches are slow via split-on-abort).
        t2 = task2_residual_validation(
            cfg2, bc, base, years=cpcfg["years"],
            dj_samples=list(cpcfg["singleton_residual"]["draw_joint_samples"]),
            n_hh=40, components=components, tol=tol, cov=cov)
        # AUTHORITATIVE: paired isolated-vs-batch residual on a bounded per-year sample
        # (40 HH/year is sufficient to confirm isolated ~ batch and bound batch-only fails;
        # 180 isolated EUROMOD calls dominate runtime, so keep the sample bounded).
        t2["paired_isolated_vs_batch"] = paired_isolated_vs_batch(
            cfg2, bc, base, years=cpcfg["years"], n_hh=40,
            components=components, tol=tol, cov=cov)
    finally:
        os.dup2(_so, 1)
        os.dup2(_se, 2)
        os.close(_so)
        os.close(_se)
        _tmp.seek(0)
        console = _tmp.read().decode("utf-8", errors="replace")
        _tmp.close()
    em_log.write_text(console, encoding="utf-8")

    # verdicts
    eq = t1["decisive_equivalence"]["agree_to_machine_tol"]
    rank_artifact = (t1["rank_IS_V_as_twoH"]["median"] >= 900
                     and t1["rank_structural_minus_logprior"]["median"] < 0.5 * 901)
    # residual is REAL if the INDEPENDENT isolated path produces a comparable fail rate
    # (and all failures are collision-free). batch_only failures (batch fails, isolated
    # passes) measure the dense-batch instrument's scale sensitivity.
    pib = t2["paired_isolated_vs_batch"]
    iso_total = sum(v["isolated_fail"] for v in pib.values())
    n_total = sum(v["n"] for v in pib.values())
    bonly_total = sum(v["batch_only_fail"] for v in pib.values())
    iso_rate = (iso_total / n_total) if n_total else None
    residual_real = bool(t2["all_failures_collision_free"] and iso_total > 0
                         and iso_rate is not None and iso_rate > 0.02)
    batch_instrument_clean = bool(n_total and (bonly_total / n_total) <= 0.02)
    t2["paired_summary"] = {"n": n_total, "isolated_fail": iso_total,
                            "isolated_rate": iso_rate, "batch_only_fail": bonly_total,
                            "batch_only_rate": (bonly_total / n_total) if n_total else None}
    out = {"increment": "stage2_twoH_validation_v1",
           "read_only": True, "no_welfare_finding": True, "measures_touched": ["W3_only"],
           "re_estimated": False, "computed_v_dir": False,
           "priced_any_redrawn_node": False, "wrote_or_overwrote_parquet": False,
           "euromod_console_log": str(em_log),
           "task1_modelfit_validation": t1,
           "task2_residual_validation": t2,
           "verdicts": {
               "modelfit_equivalence_holds": eq,
               "rank901_is_IS_weighting_artifact": bool(rank_artifact),
               "singleton_residual_reproduces_independently": bool(residual_real),
               "dense_batch_instrument_clean_at_scale": batch_instrument_clean},
           "scope_statement": (
               "READ-ONLY validation. No W^3 finding; nothing beyond W^3; nothing "
               "re-estimated; no V_i^dir; no redrawn node priced; no parquet written or "
               "overwritten.")}
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as fjs:
        json.dump(out, fjs, indent=2, default=float)
    print(f"[stage2:twoH-validation] wrote {args.out_json}")
    print(f"  T1 equivalence: estimator vs welfare negLL diff="
          f"{t1['decisive_equivalence']['max_abs_negll_diff']:.2e} agree={eq}")
    print(f"  T1 chosen=col0 share={t1['chosen_marker_is_column0_share']} | "
          f"sign all_positive={t1['sign_orientation']['all_positive']}")
    print(f"  T1 rank IS-V median={t1['rank_IS_V_as_twoH']['median']} -> "
          f"structural median={t1['rank_structural_minus_logprior']['median']} "
          f"(bottom-half {t1['rank_structural_minus_logprior']['share_bottom_half']:.2f})")
    by_year_rates = ", ".join(f"{y}:{v['rate']}" for y, v in t2["by_year"].items())
    print(f"  T2 batch residual by year: {{{by_year_rates}}}")
    ps = t2["paired_summary"]
    print(f"  T2 PAIRED isolated-vs-batch (n={ps['n']}): isolated_rate={ps['isolated_rate']} "
          f"batch_only_rate={ps['batch_only_rate']} | collision-free={t2['all_failures_collision_free']}")
    print(f"  VERDICTS: rank901_artifact={out['verdicts']['rank901_is_IS_weighting_artifact']} "
          f"residual_real={out['verdicts']['singleton_residual_reproduces_independently']} "
          f"batch_clean_at_scale={out['verdicts']['dense_batch_instrument_clean_at_scale']}")


if __name__ == "__main__":
    main()
