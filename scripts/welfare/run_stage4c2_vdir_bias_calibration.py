"""
STAGE FOUR, INCREMENT FOUR-C2 only — bounded singles V_i^dir bias-mechanism diagnostic and
node-count calibration.

Tests whether the Four-C high-ESS V_i^dir vs V_i^IS residual is finite-S log-mean-exp (Jensen)
bias, by running SINGLE-PASS node counts S in {20, 60, 100} on the SAME Four-C ESS-spanning
6-household subset + seed, dumping per-node integrand vectors (contract utility-only u(c,l) AND
the full-V diagnostic object), regressing the agreement residual against 1/S, computing the
analytic finite-S bias from CV^2, selecting the gate object, and deriving the node-count
requirement S* for the full singles run.

Single-pass only, S <= 100 (existing draw-slot capacity). Does NOT implement multi-pass, does
NOT run the full singles V_i^dir, does NOT touch couples, does NOT promote W^3 or compute any
measure beyond W^3, does NOT produce a reportable welfare distribution, does NOT swap production
or promote any baseline to canonical, and does NOT re-estimate.

Reuses the Four-C machinery unchanged (population-faithful pricing with the authoritative
yem=yem00+yemxp identity; redraw from g_hat; node_V_singles_terms for per-node u + full-V;
v_is_and_ess_singles for V_IS/ESS). Config-driven; country/year/spec-agnostic.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "scripts/bpool")
sys.path.insert(0, "scripts/enhanced")
sys.path.insert(0, "scripts/pilot")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import run_stage4c_singles_vdir_smoke as c4  # noqa: E402
import welfare_vdir as wvd  # noqa: E402
from _bpool_paths import bpool_dir  # noqa: E402

_S_GRID = [20, 60, 100]
_ESS_THRESHOLD = 30.0
_GATE_TOL_NATS = 0.5


def _cv2(nu):
    """CV^2 of exp(nu): Var(exp nu)/Mean(exp nu)^2. The leading finite-S log-mean-exp (Jensen)
    bias of log(mean_S exp(nu)) is -CV^2/(2S) (delta method on log of a sample mean)."""
    e = np.exp(np.asarray(nu, dtype=np.float64) - float(np.max(nu)))  # stable, scale-invariant
    m = float(np.mean(e))
    v = float(np.var(e))
    return (v / (m * m)) if m > 0 else float("nan")


def _logmeanexp(a):
    a = np.asarray(a, dtype=np.float64)
    mx = float(np.max(a))
    return mx + float(np.log(np.mean(np.exp(a - mx))))


def _regress_1_over_S(s_vals, y_vals):
    """OLS of y on x=1/S. Returns slope, intercept (y at 1/S->0, i.e. S->inf), R^2."""
    x = np.array([1.0 / s for s in s_vals], dtype=np.float64)
    y = np.asarray(y_vals, dtype=np.float64)
    if len(x) < 2 or np.allclose(x, x[0]):
        return None, None, None
    A = np.vstack([x, np.ones_like(x)]).T
    (slope, intercept), *_ = np.linalg.lstsq(A, y, rcond=None)
    yhat = slope * x + intercept
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = (1.0 - ss_res / ss_tot) if ss_tot > 0 else 1.0
    return float(slope), float(intercept), float(r2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--scratch-dir", required=True)
    ap.add_argument("--year", type=int, default=2016)
    ap.add_argument("--n-hh", type=int, default=6)
    ap.add_argument("--seed", type=int, default=20260604)  # Four-C seed
    ap.add_argument("--s-grid", default="20,60,100")
    args = ap.parse_args()

    s_grid = [int(s) for s in args.s_grid.split(",")]
    if max(s_grid) > 100:
        raise SystemExit("REFUSE: single-pass S must be <= 100 (existing draw-slot capacity).")

    stage4, vgate, stage2 = c4._load_cfg()
    bp = bpool_dir()
    scratch = Path(args.scratch_dir).resolve()
    staged_chunk_dir = bp / stage4["welfare_pricing_reference"]["staged_chunk_dir_name"]
    staged_priced_dir = bp / stage4["welfare_pricing_reference"]["staged_priced_dir_name"]
    if scratch in {bp.resolve(), (bp / "chunks").resolve(), staged_chunk_dir.resolve(),
                   staged_priced_dir.resolve()}:
        raise SystemExit(f"REFUSE: scratch '{scratch}' is production / staging reference")
    scratch.mkdir(parents=True, exist_ok=True)

    year, mode, n_hh, seed = args.year, "singles", args.n_hh, args.seed
    staged_stem = stage4["welfare_pricing_reference"]["staged_engine_ready_stem"]
    precomp_stem = stage2.get("precompute_long_stem", c4._PRECOMP_STEM_DEFAULT)
    bc = c4._build_constants(vgate)
    system_code, dataset_name = bc["system_pairing"][year]
    country = str(system_code).split("_")[0]
    phi = bc["cpi"][year]

    smeta = json.loads((bp / f"{staged_stem}__mnlmeta.json").read_text())
    c_scale = float(smeta["normalization"]["singles"]["c_scale"])
    l_scale = float(smeta["normalization"]["singles"]["l_scale"])

    precomp = bp / f"{precomp_stem}__{year}__{mode}__long.parquet"
    precomp_df = pd.read_parquet(precomp)
    _draws = pd.to_numeric(precomp_df["draw"], errors="coerce")
    draw_band = (int(_draws.min()), int(_draws.max()) + 1)
    year_tag = c4._year_tag_from_rows(precomp_df, year)

    import estimation_spec_parser as sp
    from enh_RURO_draws import _ensure_educ3
    er = _ensure_educ3(pd.read_parquet(bp / f"{staged_stem}__{mode}.parquet"))
    er0 = er[er["draw"] == 0].drop_duplicates("stacked_hh_uid").set_index("stacked_hh_uid")
    spec = sp.parse_specification(c4._CERT_SPEC)
    theta = c4._load_theta(spec)

    # --- reproduce the EXACT Four-C ESS-spanning subset (same seed, same pool rule) ---
    pool_uids = (precomp_df[precomp_df["draw"] == 0]["stacked_hh_uid"].drop_duplicates()
                 .sort_values().head(max(n_hh * 30, 200)).tolist())
    pool_ess = c4.v_is_and_ess_singles(bp, staged_stem, pool_uids, theta, spec)
    ess_sorted = sorted(((u, pool_ess[u]["ess"]) for u in pool_uids if u in pool_ess),
                        key=lambda kv: kv[1])
    n_high = max(1, n_hh // 2)
    n_low = n_hh - n_high
    uids = sorted(set([u for u, _ in ess_sorted[:n_low]]
                      + [u for u, _ in ess_sorted[-n_high:]]))
    vis = c4.v_is_and_ess_singles(bp, staged_stem, uids, theta, spec)

    # n_draws (data-driven, like Four-C) for the like-for-like V_IS log-mean basis
    sdec = precomp_df[precomp_df.get("ruro_decider", 1) == 1]
    n_draws = int(sdec.groupby("stacked_hh_uid")["draw"].nunique().mode().iloc[0])
    log_ndraws = float(np.log(n_draws))

    dm = wvd._load_draw_machinery()
    mincer = dm["load_mincer"]()
    Smax = max(s_grid)

    # ---- TASK 0: for each HH, redraw Smax nodes ONCE (per-HH deterministic seed) so the S-grid
    #      is NESTED (larger S supersets smaller S); price the Smax nodes population-faithfully
    #      ONCE; then take the first S nodes for each S. Dump per-node integrand vectors. ----
    per_hh = {}
    blocked = None
    for uid in uids:
        if uid not in er0.index:
            blocked = {"uid": int(uid), "reason": "uid not in staged engine-ready covariates"}
            break
        cov = er0.loc[uid]
        hh_row = {"dgn": float(cov["dgn"]), "educ3": int(cov["educ3"]),
                  "educL": float(cov["educL"]), "educH": float(cov["educH"]),
                  "pexp_years": float(cov["pexp_years"]),
                  "pexp_years2": float(cov["pexp_years2"])}
        # per-HH deterministic RNG so node sets are reproducible + nested across S
        rng = np.random.default_rng(seed + (int(uid) % 1_000_000))
        nodes = wvd.redraw_nodes_singles(hh_row, Smax, rng, mincer, dm, year_tag=year_tag)
        priced, st = c4.price_nodes_population_faithful(
            bc, year, mode, precomp_df, uid, nodes, phi, country, system_code, dataset_name,
            draw_band)
        if st["status"] != "OK":
            blocked = {"uid": int(uid), **st}
            break
        # per-node integrand vectors (utility-only u, full-V) for ALL Smax priced nodes
        n = len(priced)
        cons_real = pd.to_numeric(priced["ils_dispy_real"], errors="coerce").to_numpy()
        c_norm = np.clip(cons_real, c4.DCM_MIN_POSITIVE, None) / c_scale
        hrs = pd.to_numeric(priced["hours"], errors="coerce").to_numpy()
        leisure = np.clip(c4.TOTAL_LEISURE_HOURS - hrs, c4.DCM_MIN_POSITIVE, None)
        l_norm = leisure / l_scale
        working = pd.to_numeric(priced["working"], errors="coerce").to_numpy()
        wage = pd.to_numeric(priced["wage"], errors="coerce").to_numpy()
        V_full, terms = c4.node_V_singles_terms(
            spec, theta, c_norm=c_norm, l_norm=l_norm, working=working, wage=wage,
            priced_row=priced, c_scale=c_scale)
        u = np.asarray(terms["u"], dtype=np.float64)
        Vf = np.asarray(V_full, dtype=np.float64)
        per_hh[uid] = {"u": u, "full_V": Vf, "ess": vis[uid]["ess"],
                       "max_w": vis[uid]["max_w"], "V_i_is": vis[uid]["V_i_is"],
                       "n_priced": int(n), "n_work": int(np.sum(working))}

    if blocked is not None:
        out = {"increment": "stage4c2_vdir_bias_calibration_v1", "status": "BLOCKED",
               "blocked": blocked, **_scope()}
        Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out_json).write_text(json.dumps(out, indent=2, default=float))
        print(f"[four-C2] BLOCKED: {blocked}")
        return

    # ---- per-S V_dir for both objects (nested: first S of the Smax integrand vector) ----
    objects = ("u", "full_V")
    per_hh_curves = {}
    for uid, h in per_hh.items():
        rec = {"ess": h["ess"], "max_w": h["max_w"], "V_i_is": h["V_i_is"],
               "n_work": h["n_work"], "objects": {}}
        for obj in objects:
            nu_all = h[obj]
            vdir_by_s = {}
            cv2_by_s = {}
            for S in s_grid:
                nu = nu_all[:S]
                vdir_by_s[S] = _logmeanexp(nu)
                cv2_by_s[S] = _cv2(nu)
            # 1/S regression of V_dir(S) -> intercept estimates V_dir(inf)
            slope, intercept, r2 = _regress_1_over_S(s_grid, [vdir_by_s[S] for S in s_grid])
            # like-for-like agreement target: V_dir(full_V) vs V_IS - log(n_draws); for the
            # utility-only object the reference is the same V_dir(inf) self-limit (the contract
            # welfare object has no full-V/V_IS counterpart, so its gate is self-convergence +
            # corrected bias). We report both.
            vis_logmean = h["V_i_is"] - log_ndraws
            rec["objects"][obj] = {
                "vdir_by_s": vdir_by_s, "cv2_by_s": cv2_by_s,
                "vdir_inf_intercept": intercept, "slope_1_over_S": slope, "r2": r2,
                "vis_logmean_basis": vis_logmean,
                # delta vs V_IS (full-V object is the like-for-like one)
                "delta_common_by_s": {S: vdir_by_s[S] - vis_logmean for S in s_grid},
                "delta_common_inf": (intercept - vis_logmean
                                     if intercept is not None else None),
                # analytic finite-S bias-corrected V_dir at each S: V_dir + CV^2/(2S)
                "vdir_biascorrected_by_s": {
                    S: vdir_by_s[S] + cv2_by_s[S] / (2.0 * S) for S in s_grid},
            }
        per_hh_curves[uid] = rec

    # ---- TASK 1: 1/S regression summary on the LIKE-FOR-LIKE delta (full_V) for high-ESS ----
    high = [u for u in per_hh_curves if per_hh_curves[u]["ess"] >= _ESS_THRESHOLD]
    low = [u for u in per_hh_curves if per_hh_curves[u]["ess"] < _ESS_THRESHOLD]
    task1 = {}
    for obj in objects:
        rows = {}
        for uid in per_hh_curves:
            o = per_hh_curves[uid]["objects"][obj]
            dcom = [o["delta_common_by_s"][S] for S in s_grid]
            sl, ic, r2 = _regress_1_over_S(s_grid, dcom)
            rows[int(uid)] = {"ess": per_hh_curves[uid]["ess"], "slope": sl,
                              "intercept": ic, "r2": r2,
                              "delta_common_by_s": o["delta_common_by_s"]}
        hi_ic = [rows[u]["intercept"] for u in [int(x) for x in high]
                 if rows[u]["intercept"] is not None]
        task1[obj] = {
            "per_hh": rows,
            "high_ess_intercept_median": float(np.median(hi_ic)) if hi_ic else None,
            "high_ess_intercept_abs_max": float(np.max(np.abs(hi_ic))) if hi_ic else None,
            "interpretation": (
                "near-zero intercept + negative 1/S slope => finite-S log-mean-exp bias/noise; "
                "nonzero intercept => persistent construction/pricing/integration offset (STOP)"),
        }

    # ---- TASK 2/3: object diagnostics (CV^2, implied bias, corrected/uncorrected agreement) ----
    def _object_summary(obj):
        out = {"per_hh": {}}
        for uid in per_hh_curves:
            o = per_hh_curves[uid]["objects"][obj]
            cv2_100 = o["cv2_by_s"][max(s_grid)]
            out["per_hh"][int(uid)] = {
                "ess": per_hh_curves[uid]["ess"],
                "cv2_at_Smax": cv2_100,
                "implied_bias_at_Smax": cv2_100 / (2.0 * max(s_grid)),
                "delta_common_at_Smax": o["delta_common_by_s"][max(s_grid)],
                "delta_common_inf": o["delta_common_inf"],
                "vdir_biascorrected_at_Smax": o["vdir_biascorrected_by_s"][max(s_grid)],
            }
        hi = [out["per_hh"][int(u)] for u in [int(x) for x in high]]
        out["high_ess_delta_common_inf_abs_max"] = (
            float(np.max(np.abs([r["delta_common_inf"] for r in hi
                                 if r["delta_common_inf"] is not None]))) if hi else None)
        out["high_ess_cv2_median"] = (float(np.median([r["cv2_at_Smax"] for r in hi]))
                                      if hi else None)
        return out

    task3 = {obj: _object_summary(obj) for obj in objects}

    # ---- TASK 4: node-count requirement S* on the GATE OBJECT (utility-only, the contract
    #      welfare object). S* keeps the finite-S bias |CV^2/(2S)| <= tol on the worst CV^2. ----
    gate_obj = "u"  # contract welfare object: V_i^dir integrates own-preference utility only
    all_cv2 = [per_hh_curves[u]["objects"][gate_obj]["cv2_by_s"][max(s_grid)]
               for u in per_hh_curves]
    cv2_max_all = float(np.max(all_cv2))
    cv2_p90 = float(np.quantile(all_cv2, 0.9))
    # S* so bias <= tol: CV^2/(2S) <= tol  ->  S >= CV^2/(2 tol)
    s_star_worst = int(np.ceil(cv2_max_all / (2.0 * _GATE_TOL_NATS)))
    s_star_p90 = int(np.ceil(cv2_p90 / (2.0 * _GATE_TOL_NATS)))
    task4 = {
        "gate_object": gate_obj,
        "tol_nats": _GATE_TOL_NATS,
        "cv2_distribution": {"max": cv2_max_all, "p90": cv2_p90,
                             "median": float(np.median(all_cv2)),
                             "per_hh": {int(u): per_hh_curves[u]["objects"][gate_obj][
                                 "cv2_by_s"][max(s_grid)] for u in per_hh_curves}},
        "s_star_uncorrected": {
            "formula": "S* = ceil(CV^2 / (2*tol))",
            "worst_cv2": s_star_worst, "p90_cv2": s_star_p90},
        "single_pass_capacity": n_draws - 1,
        "exceeds_single_pass_capacity": bool(s_star_worst > (n_draws - 1)),
        "with_analytic_correction_note": (
            "with the leading CV^2/(2S) correction applied to V_dir, the residual bias is "
            "O(1/S^2); the practical S* is then set by Monte-Carlo VARIANCE (~CV^2/S), not the "
            "leading bias. Reported descriptively; the correction is exact only to leading order."),
    }

    # ---- TASK 5: verdict ----
    # gate object intercept (on the self-convergence basis: V_dir(inf) is the intercept; for the
    # contract object there is no V_IS counterpart, so the licensing test is (a) negative 1/S
    # slope (bias shrinks with S) and (b) corrected agreement / well-behaved CV^2). For the
    # full_V diagnostic object we DO have V_IS: the high-ESS delta_common intercept must be ~0.
    fullv_ic_absmax = task1["full_V"]["high_ess_intercept_abs_max"]
    fullv_ic_med = task1["full_V"]["high_ess_intercept_median"]
    # slopes negative? (bias shrinks as S rises -> delta_common rises toward intercept)
    slopes_neg = all(
        (task1["full_V"]["per_hh"][int(u)]["slope"] or 0) < 0 for u in high
        if task1["full_V"]["per_hh"][int(u)]["slope"] is not None)
    intercept_near_zero = (fullv_ic_absmax is not None and fullv_ic_absmax <= _GATE_TOL_NATS)

    if fullv_ic_absmax is None:
        verdict = "INCONCLUSIVE"
        reason = "no high-ESS household / insufficient S-stability"
    elif intercept_near_zero:
        verdict = "BIAS MECHANISM CONFIRMED / FULL-RUN DESIGN READY"
        reason = (f"high-ESS full-V delta_common intercept (S->inf) is near zero "
                  f"(abs_max {fullv_ic_absmax:.3f} <= {_GATE_TOL_NATS}); the residual is "
                  f"finite-S log-mean-exp bias (slopes negative={slopes_neg}). Recommended S* "
                  f"(utility-only gate, worst CV^2) = {s_star_worst}.")
    else:
        verdict = "PERSISTENT OFFSET / STOP"
        reason = (f"high-ESS full-V delta_common intercept (S->inf) abs_max "
                  f"{fullv_ic_absmax:.3f} > {_GATE_TOL_NATS}: a persistent offset remains after "
                  f"removing finite-S bias -> diagnose construction/pricing/integration before "
                  f"any full run.")

    out = {
        "increment": "stage4c2_vdir_bias_calibration_v1", "status": "OK",
        "is_welfare_distribution": False, "bounded_diagnostic": True,
        **_scope(),
        "task0": {"year": year, "mode": mode, "n_hh": n_hh, "seed": seed,
                  "s_grid": s_grid, "nested_nodes": True, "single_pass": True,
                  "max_S_le_100": max(s_grid) <= 100, "staged_stem": staged_stem,
                  "uids": [int(u) for u in uids], "n_draws": n_draws,
                  "high_ess_uids": [int(u) for u in high],
                  "low_ess_uids": [int(u) for u in low],
                  "yem_identity": "yem00=min(lhw,35)*yivwg*52/12; yemxp=max(lhw-35,0)*yivwg*52/12; yem=yem00+yemxp"},
        "task1_one_over_S_regression": task1,
        "task2_3_object_diagnostics": task3,
        "task4_node_count_requirement": task4,
        "task5_verdict": {
            "verdict": verdict, "reason": reason,
            "gate_object": "utility_only_u(c,l) [contract welfare object]",
            "gate_object_rationale": (
                "V_i^dir integrates the household's OWN-PREFERENCE utility u(c,l) under direct "
                "sampling from g_hat (contract: the opportunity/proposal terms are the sampling "
                "density, replaced by the uniform weight). The full-V object is a DIAGNOSTIC "
                "equivalence to the IS/full-V machinery (it carries log g_hat - log_prior) and "
                "is used here only to test the 1/S intercept against the existing V_IS; the "
                "LICENSING gate for the welfare run is the utility-only object."),
            "high_ess_fullV_intercept_abs_max": fullv_ic_absmax,
            "high_ess_fullV_intercept_median": fullv_ic_med,
            "slopes_negative": slopes_neg,
            "recommended_s_star_uncorrected_worst_cv2": s_star_worst,
            "recommended_s_star_uncorrected_p90_cv2": s_star_p90,
            "multi_pass_required": bool(s_star_worst > (n_draws - 1)),
            "is_final": False,
            "separate_authorisations_remaining": [
                "full singles V_i^dir production run", "couples V_i^dir", "W^3 promotion",
                "measure-family extension", "any reportable welfare/inequality number",
                "multi-pass pricing (if S* > single-pass capacity)"],
        },
    }
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_json).write_text(json.dumps(out, indent=2, default=float))

    print(f"[four-C2] S-grid {s_grid} on {len(uids)} HH (high-ESS {len(high)}, low {len(low)})")
    for uid in sorted(per_hh_curves, key=lambda u: per_hh_curves[u]["ess"]):
        o = per_hh_curves[uid]["objects"]["full_V"]
        ess = per_hh_curves[uid]["ess"]
        print(f"  uid={uid} ESS={ess:.1f} | full_V dcommon "
              f"S20={o['delta_common_by_s'][s_grid[0]]:+.2f} "
              f"S{s_grid[-1]}={o['delta_common_by_s'][s_grid[-1]]:+.2f} "
              f"inf={o['delta_common_inf']:+.2f} cv2@Smax={o['cv2_by_s'][max(s_grid)]:.2f}")
    print(f"[four-C2] high-ESS full-V intercept abs_max={fullv_ic_absmax} "
          f"median={fullv_ic_med} slopes_neg={slopes_neg}")
    print(f"[four-C2] S* (utility-only gate, worst CV^2)={s_star_worst} "
          f"(p90={s_star_p90}) | single-pass cap={n_draws-1} "
          f"multi_pass_required={out['task5_verdict']['multi_pass_required']}")
    print(f"[four-C2] VERDICT: {verdict}")
    print(f"[four-C2] wrote {args.out_json}")


def _scope():
    return {
        "multi_pass": False, "ran_full_singles_vdir": False, "touched_couples": False,
        "promoted_w3": False, "measure_beyond_w3": False,
        "produced_reportable_welfare_distribution": False,
        "production_parquet_swapped_or_overwritten_or_moved_or_deleted": False,
        "promoted_to_canonical": False, "re_estimated": False,
        "scope_statement": (
            "Bounded singles V_i^dir bias-mechanism diagnostic + node-count calibration. "
            "Single-pass S<=100 only. No multi-pass, no full run, no couples, no W^3 promotion, "
            "no measure beyond W^3, no reportable welfare distribution, no production swap, no "
            "canonical promotion, no re-estimation."),
    }


if __name__ == "__main__":
    main()
