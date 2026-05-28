"""
PHASE B — parameter-recovery test on the 58-param B-pool design (couples 2016 slice).

Per the prompt's recovery-test design. Reuses the REAL B-pool choice sets, log_prior,
and ils_dispy_real (no data re-simulation): we set a known theta*, compute choice probs
under theta* on the real alternatives, DRAW one synthetic chosen alternative per
household, then re-estimate from 2 starts and check recovery + conditioning.

Slice: couples 2016 only. NOTE: a 2016-only slice has year_2015/2017_indicator ≡ 0, so
beta_E_y2015 / beta_E_y2017 are structurally inert here (not recoverable from this slice
by design) — they are EXCLUDED from G1 and flagged for the full pool, not declared
unidentified. All other blocks (occ, gsur, h_lh, drgur, drgmd, thetas, leisure, wage)
DO vary within 2016 and are tested.

Solver: scipy L-BFGS-B (spec default) with analytical gradient. If it stalls, report and
note CONOPT as the alternative (gamspy path).

NO real-data (true is_chosen) estimate is interpreted. Output written to
docs/.../RURO_recovery_test_results_v1.md.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.optimize

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "enhanced"))
from _bpool_paths import bpool_dir  # noqa: E402
import estimation_spec_parser as sp   # noqa: E402
import estimation_utils as eu          # noqa: E402
import estimation_engine as ee         # noqa: E402

_BP = bpool_dir()
_SPEC = Path(__file__).resolve().parent / "specs" / "estimation_spec_bpool_p3a_v1.yaml"
_META = json.load(open(_BP / "fr_p3a_bpool_engine_ready__mnlmeta.json"))
_RNG = np.random.default_rng(20260527)

# Year params inert on a single-year (2016) slice -> excluded from G1, flagged for pool.
_YEAR_PARAMS = {"beta_E_y2015", "beta_E_y2017"}


def make_theta_star(spec) -> np.ndarray:
    """Plausible, non-trivial theta*: vary signs/magnitudes; non-zero at-risk params."""
    th = spec.get_initial_vector().astype(float).copy()
    idx = spec.get_param_index
    vals = {
        # singles leisure (male / female)
        "beta_l0_sm": 1.2, "beta_l_age_sm": 0.15, "beta_l_age2_sm": -0.05, "beta_c_sm": 0.9, "theta_l_sm": -0.8,
        "beta_l0_sf": 1.0, "beta_l_age_sf": 0.20, "beta_l_age2_sf": -0.06, "beta_l_nkids_sf": 0.30, "beta_c_sf": 1.1, "theta_l_sf": -0.7,
        "theta_c_singles": -0.9,
        # couples leisure
        "beta_l0_m": 0.5, "beta_l_age_m": 0.10, "beta_l_age2_m": -0.04, "theta_l_m": -0.6,
        "beta_l0_f": 1.3, "beta_l_age_f": 0.18, "beta_l_age2_f": -0.05, "beta_l_nkids_f": 0.40, "theta_l_f": -0.7,
        "beta_c": 1.0,
        # hours opportunity (incl. at-risk beta_h_lh)
        "beta_E": -0.5, "beta_h_pt1": 0.40, "beta_h_pt2": 0.25, "beta_h_ft": 0.60, "beta_h_lh": -0.35,
        # market opportunity (at-risk: gsur, urbanisation, region, year)
        "beta_E_gsur": 0.50, "beta_E_drgn2": 0.20, "beta_E_drgn3": -0.15, "beta_E_drgn4": 0.10,
        "beta_E_drgn5": -0.20, "beta_E_drgn6": 0.12, "beta_E_drgn7": -0.10, "beta_E_drgn8": 0.18,
        "beta_E_y2015": 0.15, "beta_E_y2017": -0.12,
        "beta_E_drgur": 0.35, "beta_E_drgmd": -0.20,
        # occupation opportunity (dead in pilot pre-loc4 -> deliberate non-zero)
        "beta_occ_2_sm": 0.30, "beta_occ_3_sm": -0.25, "beta_occ_4_sm": 0.20,
        "beta_occ_2_sf": -0.20, "beta_occ_3_sf": 0.28, "beta_occ_4_sf": -0.18,
        "beta_occ_2_cm": 0.22, "beta_occ_3_cm": -0.30, "beta_occ_4_cm": 0.16,
        "beta_occ_2_cf": -0.24, "beta_occ_3_cf": 0.26, "beta_occ_4_cf": -0.14,
        # wage
        "beta_w0": 2.0, "beta_w_educL": -0.15, "beta_w_educH": 0.25, "beta_w_pexp": 0.03, "beta_w_pexp2": -0.0004,
        "sigma": 0.55,
        # couples interaction
        "beta_ll": 1.5,
    }
    for name, v in vals.items():
        th[idx(name)] = v
    return th


def draw_synthetic_choice_couples(theta_star, data, spec, rng) -> np.ndarray:
    """Compute per-alternative probs under theta* on the real alternatives, draw one
    chosen alt per group. Returns a new actual_choice array (1.0 at drawn alt)."""
    comp = ee.compute_likelihood_couples(theta_star, data, spec, return_components=True)
    V = comp["V"]
    gs, ge = data.group_starts, data.group_ends
    new_choice = np.zeros(data.n_obs)
    for g in range(data.n_groups):
        lo, hi = gs[g], ge[g]
        Vg = V[lo:hi]
        Vg = Vg - Vg.max()
        p = np.exp(Vg); p = p / p.sum()
        j = rng.choice(hi - lo, p=p)
        new_choice[lo + j] = 1.0
    return new_choice


def numerical_hessian(theta, grad_func, eps=1e-5):
    n = len(theta)
    H = np.zeros((n, n))
    for i in range(n):
        tp = theta.copy(); tp[i] += eps
        tm = theta.copy(); tm[i] -= eps
        H[:, i] = (grad_func(tp) - grad_func(tm)) / (2 * eps)
    return 0.5 * (H + H.T)


def main():
    spec = sp.parse_specification(_SPEC)
    pnames = spec.all_param_names
    assert len(pnames) == 58

    # --- slice: couples 2016 only ---
    c = pd.read_parquet(_BP / "fr_p3a_bpool_engine_ready__couples.parquet")
    c16 = c[c["data_year"] == 2016].copy()
    uids = pd.Series(c16["stacked_hh_uid"].unique()).head(300)   # ~300 HH slice
    sl = c16[c16["stacked_hh_uid"].isin(uids)].sort_values(["idhh", "draw_joint"]).reset_index(drop=True)
    print(f"slice: couples 2016, {sl['stacked_hh_uid'].nunique()} HH, {len(sl):,} rows")
    data = eu.precompute_data_couples(sl, _META, include_wage_vars=True, include_loc_vars=True)

    # --- theta* + synthetic choice ---
    theta_star = make_theta_star(spec)
    new_choice = draw_synthetic_choice_couples(theta_star, data, spec, _RNG)
    data.actual_choice = new_choice
    n_chosen = int(new_choice.sum())
    print(f"synthetic chosen alts drawn: {n_chosen} (= n_groups {data.n_groups})")

    # --- objective + gradient on the synthetic-choice data ---
    bounds = spec.get_bounds_tuple()
    def negll(th): return ee.compute_likelihood_couples(th, data, spec)
    def grad(th):  return ee.compute_gradient_couples(th, data, spec)

    starts = {"warm(theta*)": theta_star.copy(), "cold(spec defaults)": spec.get_initial_vector().astype(float)}
    results = {}
    for label, x0 in starts.items():
        t0 = time.time()
        _it = {"k": 0}
        def _cb(xk, _it=_it, _t0=t0):
            _it["k"] += 1
            f = negll(xk); gnorm = float(np.max(np.abs(grad(xk))))
            print(f"    [{label}] iter {_it['k']:4d}  negLL={f:.6f}  |proj g|max={gnorm:.3e}  "
                  f"{time.time()-_t0:.0f}s", flush=True)
        res = scipy.optimize.minimize(negll, x0, jac=grad, method=spec.opt_method,
                                      bounds=bounds, callback=_cb,
                                      options={"maxiter": spec.opt_max_iterations,
                                               "ftol": 1e-10, "gtol": 1e-7})
        dt = time.time() - t0
        results[label] = {"theta": res.x, "ll": -res.fun, "success": bool(res.success),
                          "msg": str(res.message), "nit": int(getattr(res, "nit", -1)), "sec": round(dt, 1)}
        print(f"  start={label:20} success={res.success} LL={-res.fun:.4f} nit={getattr(res,'nit','?')} {dt:.1f}s  ({res.message})")

    # use warm start as theta_hat for gates (closest to truth; cold is the G2 cross-check)
    theta_hat = results["warm(theta*)"]["theta"]
    theta_cold = results["cold(spec defaults)"]["theta"]

    # --- Hessian / conditioning at theta_hat ---
    H = numerical_hessian(theta_hat, grad)
    eigvals = np.linalg.eigvalsh(H)
    pd_ok = bool(np.all(eigvals > 0))
    cond = float(eigvals.max() / eigvals.min()) if eigvals.min() > 0 else float("inf")
    try:
        cov = np.linalg.inv(H)
        se = np.sqrt(np.clip(np.diag(cov), 0, None))
    except np.linalg.LinAlgError:
        cov = None; se = np.full(len(theta_hat), np.nan)

    # --- G1 per-param recovery ---
    rows = []
    for i, name in enumerate(pnames):
        err = theta_hat[i] - theta_star[i]
        se_i = se[i] if se is not None else np.nan
        err_se = abs(err) / se_i if (se_i and np.isfinite(se_i) and se_i > 0) else np.nan
        wrong_sign = (np.sign(theta_hat[i]) != np.sign(theta_star[i])) and abs(theta_star[i]) > 1e-3
        inert = name in _YEAR_PARAMS
        rows.append({"param": name, "theta_star": theta_star[i], "theta_hat": theta_hat[i],
                     "abs_err": abs(err), "err_over_se": err_se, "wrong_sign": wrong_sign,
                     "inert_on_slice": inert})
    g1 = pd.DataFrame(rows)

    # G2 reproducibility (exclude inert year params from the agreement metric)
    mask_testable = ~g1["param"].isin(_YEAR_PARAMS)
    g2_max_diff = float(np.max(np.abs(theta_hat - theta_cold)[mask_testable.values]))

    # G3b urbanisation x region correlation in Hessian-implied covariance
    def corr(a, b):
        if cov is None: return np.nan
        ia, ib = spec.get_param_index(a), spec.get_param_index(b)
        va, vb = cov[ia, ia], cov[ib, ib]
        return float(cov[ia, ib] / np.sqrt(va * vb)) if va > 0 and vb > 0 else np.nan
    reg_params = [f"beta_E_drgn{k}" for k in range(2, 9)]
    g3b = {
        "corr(drgur, drgmd)": corr("beta_E_drgur", "beta_E_drgmd"),
        "max|corr(drgur, regK)|": float(np.nanmax([abs(corr("beta_E_drgur", r)) for r in reg_params])),
        "max|corr(drgmd, regK)|": float(np.nanmax([abs(corr("beta_E_drgmd", r)) for r in reg_params])),
    }

    out = {"theta_star": {n: float(theta_star[i]) for i, n in enumerate(pnames)},
           "starts": {k: {kk: (vv.tolist() if isinstance(vv, np.ndarray) else vv)
                          for kk, vv in v.items()} for k, v in results.items()},
           "g1": g1, "g2_max_diff_warm_vs_cold": g2_max_diff,
           "conditioning": {"pd": pd_ok, "cond": cond, "min_eig": float(eigvals.min()),
                            "max_eig": float(eigvals.max())},
           "g3b": g3b, "se": se, "eigvals": eigvals, "pnames": pnames,
           "n_hh": int(sl["stacked_hh_uid"].nunique()), "solver": spec.opt_method}
    _write_report(out)
    _print_summary(out)


def _print_summary(out):
    g1 = out["g1"]
    test = g1[~g1["inert_on_slice"]]
    tol = 0.10  # abs-error tolerance on the slice (economic-block params)
    print("\n" + "="*72)
    print("PHASE B SUMMARY")
    print("="*72)
    print(f"  solver: {out['solver']}")
    print(f"  G2 reproducibility (max|warm-cold|, testable): {out['g2_max_diff_warm_vs_cold']:.3e}")
    print(f"  G3 conditioning: PD={out['conditioning']['pd']}  cond={out['conditioning']['cond']:.3e}  "
          f"min_eig={out['conditioning']['min_eig']:.3e}")
    print(f"  G3b corr(drgur,drgmd)={out['g3b']['corr(drgur, drgmd)']:.3f}  "
          f"max|corr(drgur,reg)|={out['g3b']['max|corr(drgur, regK)|']:.3f}  "
          f"max|corr(drgmd,reg)|={out['g3b']['max|corr(drgmd, regK)|']:.3f}")
    bad = test[(test["abs_err"] > tol) | (test["wrong_sign"])]
    print(f"  G1 recovery: {len(test)-len(bad)}/{len(test)} testable params within tol={tol} & correct sign")
    if len(bad):
        print("  G1 flags:")
        for _, r in bad.iterrows():
            print(f"    {r['param']:16} theta*={r['theta_star']:+.3f} hat={r['theta_hat']:+.3f} "
                  f"abs_err={r['abs_err']:.3f} err/se={r['err_over_se']:.2f} wrong_sign={r['wrong_sign']}")
    print(f"  (year params inert on 2016 slice, excluded from G1: {sorted(_YEAR_PARAMS)})")


def _write_report(out):
    g1 = out["g1"]
    doc = Path("U:/Desktop/Nizam_Hisham/MNL/docs/France_case/P3a/execution_logs/Bpool")
    doc.mkdir(parents=True, exist_ok=True)
    p = doc / "RURO_recovery_test_results_v1.md"
    lines = []
    lines.append("# RURO Recovery Test Results v1 — bpool_p3a_v1 (58 params)\n")
    lines.append(f"**Date:** 2026-05-27  •  **Design:** B-pool product, couples 2016 slice "
                 f"({out['n_hh']} HH)  •  **Solver:** {out['solver']}\n")
    lines.append("Synthetic chosen alternative drawn from theta* on the REAL B-pool "
                 "alternatives (log_prior, ils_dispy_real, choice sets reused; no data "
                 "re-simulation). No real-data estimate interpreted.\n")
    lines.append("\n## Starts\n")
    lines.append("| start | success | LL | nit | sec |")
    lines.append("|---|---|---|---|---|")
    for k, v in out["starts"].items():
        lines.append(f"| {k} | {v['success']} | {v['ll']:.3f} | {v['nit']} | {v['sec']} |")
    lines.append(f"\n**G2 reproducibility:** max|theta_warm − theta_cold| (testable) = "
                 f"{out['g2_max_diff_warm_vs_cold']:.3e}\n")
    c = out["conditioning"]
    lines.append(f"\n## G3 Conditioning (Hessian at theta_hat)\n")
    lines.append(f"- positive-definite: **{c['pd']}**")
    lines.append(f"- condition number: **{c['cond']:.3e}**")
    lines.append(f"- smallest eigenvalue: **{c['min_eig']:.3e}**, largest: {c['max_eig']:.3e}\n")
    g = out["g3b"]
    lines.append(f"\n## G3b Urbanisation × Region (key verdict)\n")
    lines.append(f"- corr(beta_E_drgur, beta_E_drgmd) = **{g['corr(drgur, drgmd)']:.3f}**")
    lines.append(f"- max|corr(beta_E_drgur, reg2..8)| = **{g['max|corr(drgur, regK)|']:.3f}**")
    lines.append(f"- max|corr(beta_E_drgmd, reg2..8)| = **{g['max|corr(drgmd, regK)|']:.3f}**")
    redundant = (g["max|corr(drgur, regK)|"] > 0.9) or (g["max|corr(drgmd, regK)|"] > 0.9)
    lines.append(f"- **Verdict: urbanisation {'SPATIALLY REDUNDANT with region' if redundant else 'IDENTIFIED SEPARATELY from region'}**\n")
    lines.append("\n## G1 / G4 per-param recovery\n")
    lines.append("| param | theta* | theta_hat | abs_err | err/se | wrong_sign | note |")
    lines.append("|---|---|---|---|---|---|---|")
    for _, r in g1.iterrows():
        note = "INERT on 2016 slice (flag for pool)" if r["inert_on_slice"] else ""
        es = f"{r['err_over_se']:.2f}" if np.isfinite(r["err_over_se"]) else "n/a"
        lines.append(f"| {r['param']} | {r['theta_star']:+.4f} | {r['theta_hat']:+.4f} | "
                     f"{r['abs_err']:.4f} | {es} | {r['wrong_sign']} | {note} |")
    p.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport written: {p}")


if __name__ == "__main__":
    main()
