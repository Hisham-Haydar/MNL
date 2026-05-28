"""
Parameter-recovery test for the RURO MNL — PACKAGE-GRADE: vectorized, and
specification / country / year / mode AGNOSTIC.

No spec parameter name is hardcoded. theta* is generated from (initial value, bounds)
per param via a generic block rule, so the test works for any spec (58-param bpool,
40-wage-param B3, a different country's region/year set, etc.). The slice is selected
by CLI (country, year(s), mode, n_hh). Inert params (e.g. a year indicator that is
constant on a single-year slice) are detected FROM THE DATA, not a hardcoded name list.

Method (reuses REAL alternatives — no data re-simulation):
  1. theta* from spec (generic, non-trivial, in-bounds; opportunity shifters get
     alternating-sign non-zero values so every block is exercised).
  2. choice probs under theta* on the real choice sets -> draw one synthetic chosen
     alternative per group (VECTORIZED segmented Gumbel-max, no per-group loop).
  3. re-estimate from >=2 starts (warm=theta*, cold=spec init); record convergence.
  4. gates G1 (recovery), G2 (reproducibility), G3 (conditioning), G3b (named
     collinearity probe, generic), G4 (block recovery).

Estimation itself is NOT launched here by default — see --run. Per project policy,
prefer running the printed PowerShell command in a terminal to watch iterations live.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Parallelism for ONE estimation: the LL/gradient is a sum over independent households,
# which the engine vectorizes and (where numba is present) runs group-parallel via prange.
# Give numba/BLAS the core budget BEFORE importing the engine. Override with --threads.
_DEFAULT_THREADS = min(28, os.cpu_count() or 1)
os.environ.setdefault("NUMBA_NUM_THREADS", str(_DEFAULT_THREADS))

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "enhanced"))
from _bpool_paths import bpool_dir  # noqa: E402
import estimation_spec_parser as sp   # noqa: E402
import estimation_utils as eu          # noqa: E402
import estimation_engine as ee         # noqa: E402


# ----------------------------------------------------------------------------
# Generic, spec-agnostic theta* generation
# ----------------------------------------------------------------------------
def generate_theta_star(spec, rng, scale_perturb=0.25, shifter_frac=0.12) -> np.ndarray:
    """
    Build a plausible, non-trivial, in-bounds theta* WITHOUT naming any parameter.

    Rule, per param, from (initial value v0, bounds [lo,hi]):
      - |v0| > eps (scale/level params, e.g. leisure intercepts, beta_c, sigma, wage
        intercept): theta* = v0 * (1 + scale_perturb * s), s alternating +/-1, clipped.
      - v0 == 0 (opportunity shifters that the model leaves at 0 by default): assign a
        deterministic NON-ZERO value = shifter_frac * (half-width of finite bounds) with
        ALTERNATING SIGN across such params, so every block is exercised and at-risk
        params (occupation, gsur, urbanisation, long-hours) get real signal.
      - box-cox exponents (detected as bounded strictly negative-friendly, v0 < 0):
        keep sign, perturb magnitude.
    Deterministic given rng seed; fully driven by the spec, so any country/year/spec works.
    """
    names = spec.all_param_names
    th = np.array([float(spec.initial_values.get(n, 0.0)) for n in names], dtype=float)
    bt = spec.get_bounds_tuple()
    eps = 1e-6
    sign = 1.0
    for i, n in enumerate(names):
        v0 = th[i]
        lo, hi = (-np.inf, np.inf)
        if bt and i < len(bt) and bt[i] is not None:
            lo = bt[i][0] if bt[i][0] is not None else -np.inf
            hi = bt[i][1] if bt[i][1] is not None else np.inf
        if abs(v0) > eps:
            # scale/level/box-cox param: perturb around its own initial value
            val = v0 * (1.0 + scale_perturb * sign)
        else:
            # opportunity shifter defaulted to 0: assign non-zero alternating-sign signal
            half = 0.5 * (hi - lo) if np.isfinite(hi) and np.isfinite(lo) else 1.0
            val = sign * shifter_frac * half
        # keep strictly inside bounds
        pad = 1e-6
        if np.isfinite(lo):
            val = max(val, lo + pad)
        if np.isfinite(hi):
            val = min(val, hi - pad)
        th[i] = val
        sign = -sign
    return th


# ----------------------------------------------------------------------------
# Vectorized synthetic-choice draw (segmented Gumbel-max, no per-group loop)
# ----------------------------------------------------------------------------
def draw_synthetic_choice(V: np.ndarray, group_starts, group_ends, rng) -> np.ndarray:
    """
    One draw per group from softmax(V) within each group, fully vectorized.
    Gumbel-max trick: argmax_j (V_j + Gumbel_j) ~ Categorical(softmax(V)). The argmax is
    taken WITHIN each contiguous group via a segmented reduce — no Python loop over groups.
    Returns actual_choice (1.0 at the drawn alt in each group, else 0.0).
    """
    n = V.shape[0]
    g = np.repeat(np.arange(len(group_starts)), (group_ends - group_starts))
    gumbel = -np.log(-np.log(rng.uniform(size=n)))
    key = V + gumbel
    # segmented argmax: for each group, the index (global) of max key.
    order = np.lexsort((-key, g))            # sort by group asc, key desc
    first_in_group = np.ones(n, dtype=bool)
    g_sorted = g[order]
    first_in_group[1:] = g_sorted[1:] != g_sorted[:-1]
    chosen_global = order[first_in_group]    # first row of each group in sorted order = its argmax
    out = np.zeros(n)
    out[chosen_global] = 1.0
    return out


# ----------------------------------------------------------------------------
# Inert-param detection (data-driven, not name-based)
# ----------------------------------------------------------------------------
def detect_inert_params(spec, data, ll_func, theta_star, base_ll=None, tol=1e-7) -> list[str]:
    """
    A param is 'inert on this slice' if nudging it does not move the LL — i.e. its data
    column is constant/zero on the slice (e.g. a year indicator on a single-year slice,
    or an occupation level absent from the slice). Detected by perturbation, generic.
    """
    if base_ll is None:
        base_ll = ll_func(theta_star, data, spec)
    bt = spec.get_bounds_tuple()
    inert = []
    for i, n in enumerate(spec.all_param_names):
        tp = theta_star.copy()
        step = 0.2
        if bt and i < len(bt) and bt[i] is not None and bt[i][1] is not None and tp[i] + step > bt[i][1]:
            step = -step
        tp[i] += step
        if abs(ll_func(tp, data, spec) - base_ll) <= tol:
            inert.append(n)
    return inert


# ----------------------------------------------------------------------------
# Numerical Hessian (loop is over params — inherent to finite differences)
# ----------------------------------------------------------------------------
def numerical_hessian(theta, grad_func, eps=1e-5, workers=1) -> np.ndarray:
    """Central-difference Hessian. The n columns are independent finite-difference
    gradient pairs -> embarrassingly parallel across params (workers>1)."""
    n = len(theta)
    H = np.empty((n, n))

    def col(i):
        tp = theta.copy(); tp[i] += eps
        tm = theta.copy(); tm[i] -= eps
        return i, (grad_func(tp) - grad_func(tm)) / (2 * eps)

    if workers and workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for i, c in ex.map(col, range(n)):
                H[:, i] = c
    else:
        for i in range(n):
            _, c = col(i); H[:, i] = c
    return 0.5 * (H + H.T)


# ----------------------------------------------------------------------------
# Mode dispatch — country/year/mode agnostic data loading
# ----------------------------------------------------------------------------
def load_slice(country: str, mode: str, years: list[int], n_hh: int, engine_ready_stem: str):
    """Load an engine-ready parquet slice. Stem is parameterized; country/year via columns."""
    path = bpool_dir() / f"{engine_ready_stem}__{mode}.parquet"
    df = pd.read_parquet(path)
    if years:
        df = df[df["data_year"].isin(years)].copy()
    draw_col = "draw" if mode == "singles" else "draw_joint"
    uids = pd.Series(df["stacked_hh_uid"].unique())
    if n_hh and n_hh < len(uids):
        uids = uids.head(n_hh)
    sl = df[df["stacked_hh_uid"].isin(uids)].sort_values(["idhh", draw_col]).reset_index(drop=True)
    meta_path = bpool_dir() / f"{engine_ready_stem}__mnlmeta.json"
    meta = json.load(open(meta_path))
    return sl, meta, draw_col


def precompute(mode, sl, meta):
    if mode == "singles":
        return eu.precompute_data_singles(sl, meta, is_male=True, include_wage_vars=True, include_loc_vars=True)
    return eu.precompute_data_couples(sl, meta, include_wage_vars=True, include_loc_vars=True)


def ll_for(mode):
    return ee.compute_likelihood_singles if mode == "singles" else ee.compute_likelihood_couples


def grad_for(mode):
    return ee.compute_gradient_singles if mode == "singles" else ee.compute_gradient_couples


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", type=Path,
                    default=Path(__file__).resolve().parent / "specs" / "estimation_spec_bpool_p3a_v1.yaml")
    ap.add_argument("--engine-ready-stem", default="fr_p3a_bpool_engine_ready",
                    help="stem of the engine-ready parquets ({stem}__{mode}.parquet, {stem}__mnlmeta.json)")
    ap.add_argument("--country", default="fr")
    ap.add_argument("--mode", default="couples", choices=["singles", "couples"])
    ap.add_argument("--years", default="2016", help="comma-separated, or 'all'")
    ap.add_argument("--n-hh", type=int, default=300)
    ap.add_argument("--seed", type=int, default=20260527)
    ap.add_argument("--threads", type=int, default=_DEFAULT_THREADS,
                    help="numba threads for the per-household LL/gradient (one estimation "
                         "is parallel over households, not over solver iterations)")
    ap.add_argument("--parallel-starts", action="store_true",
                    help="run the warm and cold starts concurrently (independent optimizations)")
    ap.add_argument("--starts", default="warm,cold",
                    help="comma-separated subset of {warm,cold}. 'warm' alone gives G1/G3/G3b/G4 "
                         "(skips G2 reproducibility) at half the time.")
    ap.add_argument("--solver", default=None,
                    choices=[None, "scipy", "scipy-trustconstr",
                             "gamspy-conopt", "gamspy-ipopt", "gamspy-knitro"],
                    help="override the spec's optimization.method. scipy = L-BFGS-B (spec "
                         "default, stalls on this manifold); scipy-trustconstr = "
                         "Hessian/trust-region (navigates the curved manifold, no GAMS, fast); "
                         "gamspy-conopt = production solver (converges but ~3.5h/start at full "
                         "size). Default: use spec.opt_method.")
    ap.add_argument("--reslim", type=int, default=1800,
                    help="CONOPT wall-time cap in seconds (gamspy reslim; matches NC pilot). "
                         "NOTE: GAMSPy model GENERATION (not the solve) is the binding cost "
                         "for this vectorized NLP — can be hours at full size.")
    ap.add_argument("--flat-tol", type=float, default=1e-6,
                    help="objective-change threshold for the flat-objective early stop "
                         "(trust-constr). Loosen (e.g. 5e-3) to stop at a near-optimum when a "
                         "thin-margin variance param like sigma keeps the gradient from "
                         "reaching gtol on a finite slice.")
    ap.add_argument("--maxiter", type=int, default=None,
                    help="hard iteration cap (overrides spec.opt_max_iterations). Use to bound "
                         "a slice run that won't crush gtol on a thin-margin param.")
    ap.add_argument("--run", action="store_true",
                    help="actually run the optimizer here (default: print the PowerShell "
                         "command to run in a terminal so iterations are visible live)")
    ap.add_argument("--report", type=Path,
                    default=Path("U:/Desktop/Nizam_Hisham/MNL/docs/France_case/P3a/execution_logs/Bpool")
                            / "RURO_recovery_test_results_v2_raw.md")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    years = [] if args.years.strip().lower() == "all" else [int(y) for y in args.years.split(",")]
    rng = np.random.default_rng(args.seed)
    spec = sp.parse_specification(args.spec)
    pnames = spec.all_param_names
    print(f"spec '{getattr(spec,'name','?')}': {len(pnames)} params  | mode={args.mode} "
          f"country={args.country} years={years or 'all'} n_hh={args.n_hh}")

    if not args.run:
        cmd = (f'& "U:\\Desktop\\Nizam_Hisham\\MNL\\.venv\\Scripts\\python.exe" -u '
               f'"{Path(__file__)}" --run --mode {args.mode} --years {args.years} '
               f'--n-hh {args.n_hh} --engine-ready-stem {args.engine_ready_stem}')
        print("\nTo run the recovery test in your terminal (live iterations):\n")
        print(cmd + "\n")
        print("(Add 2>&1 | Tee-Object <log> to also save the console.)")
        return

    import scipy.optimize
    solver = (args.solver or "scipy")
    if solver == "scipy":
        solver = "scipy"  # spec.opt_method is L-BFGS-B; scipy path below
    print(f"solver: {solver if solver != 'scipy' else 'scipy/' + spec.opt_method}")
    # Apply the per-eval thread budget (one estimation is parallel over households).
    if ee.HAS_NUMBA:
        try:
            import numba
            numba.set_num_threads(max(1, args.threads))
            print(f"numba threads (per-household LL/gradient): {numba.get_num_threads()}")
        except Exception as _e:
            print(f"numba thread set skipped: {_e}")
    else:
        print("numba not available — LL/gradient run vectorized single-process (BLAS-threaded)")

    sl, meta, draw_col = load_slice(args.country, args.mode, years, args.n_hh, args.engine_ready_stem)
    print(f"slice: {args.mode} {years or 'all'}  {sl['stacked_hh_uid'].nunique()} HH  {len(sl):,} rows")
    data = precompute(args.mode, sl, meta)
    llf, gf = ll_for(args.mode), grad_for(args.mode)

    theta_star = generate_theta_star(spec, rng)
    comp = llf(theta_star, data, spec, return_components=True)
    data.actual_choice = draw_synthetic_choice(comp["V"], data.group_starts, data.group_ends, rng)
    print(f"synthetic chosen alts: {int(data.actual_choice.sum())} (= n_groups {data.n_groups})")

    inert = detect_inert_params(spec, data, llf, theta_star)
    if inert:
        print(f"inert on this slice (excluded from G1, flag for pool): {inert}")

    bounds = spec.get_bounds_tuple()
    negll = lambda th: llf(th, data, spec)
    grad = lambda th: gf(th, data, spec)

    def run_start_scipy(label, x0):
        # All solver knobs come from the spec YAML (the spec "has everything").
        t0 = time.time(); it = {"k": 0}
        def cb(xk, label=label, it=it, t0=t0):
            it["k"] += 1
            print(f"    [{label}] iter {it['k']:4d}  negLL={negll(xk):.6f}  "
                  f"|g|max={np.max(np.abs(grad(xk))):.3e}  {time.time()-t0:.0f}s", flush=True)
        # Live iterations come from our callback (cb); the per-iteration display is NOT
        # delegated to L-BFGS-B's disp/iprint (deprecated, removed in SciPy 1.18).
        res = scipy.optimize.minimize(
            negll, x0, jac=grad, method=spec.opt_method, bounds=bounds, callback=cb,
            options={"maxiter": spec.opt_max_iterations,
                     "ftol": spec.opt_tolerance,
                     "gtol": spec.opt_gradient_tolerance})
        out = {"theta": res.x, "ll": float(-res.fun), "success": bool(res.success),
               "msg": str(res.message), "nit": int(getattr(res, "nit", -1)),
               "sec": round(time.time() - t0, 1)}
        print(f"  {label}: success={res.success} LL={-res.fun:.4f} nit={getattr(res,'nit','?')} "
              f"{out['sec']}s ({res.message})", flush=True)
        return label, out

    def run_start_gamspy(label, x0):
        # CONOPT/IPOPT/KNITRO via GAMSPy on the SAME synthetic-choice data. The gamspy
        # estimator builds its own NLP; no per-iteration callback (it prints its own log).
        # Capture the CONOPT solver log AND the GAMS listing (.lst) to outputs/logs so they
        # are retrievable (write_listing_file=True, report_solution=1 inside the estimator).
        gsolver = solver.split("-")[1]
        logdir = bpool_dir().parent / "outputs" / "logs"
        logdir.mkdir(parents=True, exist_ok=True)
        stamp = f"recovery_{args.mode}_{args.years}_{gsolver}_{label}"
        artifacts = {"solver_log": str(logdir / f"{stamp}.solver.log"),
                     "listing_file": str(logdir / f"{stamp}.lst")}
        t0 = time.time()
        if args.mode == "singles":
            from gamspy_estimation_vectorized import estimate_singles_vectorized_gamspy as est
        else:
            from gamspy_estimation_vectorized import estimate_couples_vectorized_gamspy as est
        # CONOPT caps matching the NC pilot's working invocation
        # (_run_diagnostic_estimation_rerun.py): iterlim major-iters, reslim wall-seconds.
        # NOTE: GAMSPy model GENERATION for this vectorized NLP is the binding cost
        # (~3.4-3.5 h/start in the pilot at full size) — NOT the CONOPT solve. Expect a
        # long "Generating NLP model" phase before any solver iterations appear.
        solver_options = {"iterlim": spec.opt_max_iterations, "reslim": args.reslim}
        print(f"    [{label}] GAMSPy {gsolver.upper()} solving "
              f"(options={solver_options}; model-gen may take a long time) ...", flush=True)
        print(f"      solver log -> {artifacts['solver_log']}", flush=True)
        print(f"      listing    -> {artifacts['listing_file']}", flush=True)
        gd = est(data, spec, theta_init=x0, solver=gsolver, verbose=True,
                 solver_options=solver_options, solver_artifacts=artifacts)
        out = {"theta": np.asarray(gd["theta"]), "ll": float(gd["log_likelihood"]),
               "success": ("Optimal" in gd["solver_status"] or "Normal" in gd["solver_status"]),
               "msg": f"{gd['solver_status']} ({gd['model_status']})",
               "nit": int(gd.get("n_iterations") or -1), "sec": round(time.time() - t0, 1)}
        print(f"  {label}: success={out['success']} LL={out['ll']:.4f} nit={out['nit']} "
              f"{out['sec']}s ({out['msg']})", flush=True)
        return label, out

    def run_start_trustconstr(label, x0):
        # Trust-region constrained solver: analytical gradient + BFGS Hessian approx.
        # Handles the curved manifold L-BFGS-B grinds on; no GAMS model-gen cost.
        # Two practical fixes for the recovery setting:
        #  (1) report WHICH param owns max|g| each iter (identifies a stuck/weak direction).
        #  (2) early-stop when the objective is FLAT for several iters (it has reached the
        #      optimum; gtol=1e-6 on a finite slice is often unreachable when a param sits
        #      on a shallow ridge — that residual gradient is itself the identification
        #      finding, not a reason to spin thousands of iters).
        from scipy.optimize import Bounds, BFGS
        t0 = time.time(); st = {"k": 0, "prev": None, "flat": 0}
        lo = np.array([b[0] if b and b[0] is not None else -np.inf for b in bounds])
        hi = np.array([b[1] if b and b[1] is not None else np.inf for b in bounds])
        sb = Bounds(lo, hi, keep_feasible=False)
        flat_tol = args.flat_tol    # objective change below this = "flat" (configurable)
        flat_need = 15              # consecutive flat iters -> declare at-optimum and stop

        def cb(xk, state=None, label=label, st=st, t0=t0):
            st["k"] += 1
            f = negll(xk); g = grad(xk)
            gi = int(np.argmax(np.abs(g))); gmax = float(np.abs(g[gi]))
            gname = pnames[gi]
            if st["prev"] is not None and abs(st["prev"] - f) < flat_tol:
                st["flat"] += 1
            else:
                st["flat"] = 0
            st["prev"] = f
            if st["k"] % 1 == 0:
                print(f"    [{label}] iter {st['k']:4d}  negLL={f:.6f}  |g|max={gmax:.3e} "
                      f"@{gname}  flat={st['flat']}  {time.time()-t0:.0f}s", flush=True)
            if st["flat"] >= flat_need:
                print(f"    [{label}] objective flat for {flat_need} iters "
                      f"(at optimum; max|g|={gmax:.3e} @ {gname}) -> stopping.", flush=True)
                return True   # trust-constr terminates when callback returns True
            return False

        _maxit = args.maxiter if args.maxiter else spec.opt_max_iterations
        res = scipy.optimize.minimize(
            negll, x0, jac=grad, hess=BFGS(), method="trust-constr", bounds=sb, callback=cb,
            options={"maxiter": _maxit,
                     "gtol": spec.opt_gradient_tolerance,
                     "xtol": spec.opt_tolerance, "verbose": 0})
        g_fin = grad(res.x); gi = int(np.argmax(np.abs(g_fin)))
        out = {"theta": res.x, "ll": float(-res.fun), "success": bool(res.success),
               "msg": str(res.message), "nit": int(getattr(res, "niter", getattr(res, "nit", -1))),
               "sec": round(time.time() - t0, 1),
               "final_gmax": float(np.abs(g_fin[gi])), "final_gmax_param": pnames[gi]}
        print(f"  {label}: success={res.success} LL={-res.fun:.4f} nit={out['nit']} "
              f"{out['sec']}s  final max|g|={out['final_gmax']:.3e} @ {out['final_gmax_param']} "
              f"({res.message})", flush=True)
        return label, out

    if solver == "scipy":
        run_start = run_start_scipy
    elif solver == "scipy-trustconstr":
        run_start = run_start_trustconstr
    else:
        run_start = run_start_gamspy

    all_starts = {"warm": theta_star.copy(), "cold": spec.get_initial_vector().astype(float)}
    want = [s.strip() for s in args.starts.split(",") if s.strip() in all_starts]
    if "warm" not in want:
        want = ["warm"] + want  # warm is required (theta_hat for the gates)
    starts = {k: all_starts[k] for k in want}
    print(f"starts: {list(starts)}")
    results = {}
    if args.parallel_starts:
        # The two starts are independent optimizations -> run concurrently. (Note: this
        # competes with numba's intra-eval threads; sensible when threads < cores/2.)
        with ThreadPoolExecutor(max_workers=len(starts)) as ex:
            for label, out in ex.map(lambda kv: run_start(*kv), list(starts.items())):
                results[label] = out
    else:
        for label, x0 in starts.items():
            _, results[label] = run_start(label, x0)

    _gates_and_report(spec, args, data, results, theta_star, inert, grad,
                      hess_workers=1, solver_label=solver)


def _gates_and_report(spec, args, data, results, theta_star, inert, grad,
                      hess_workers=1, solver_label="scipy"):
    pnames = spec.all_param_names
    theta_hat = results["warm"]["theta"]
    theta_cold = results["cold"]["theta"] if "cold" in results else None  # G2 needs both starts
    H = numerical_hessian(theta_hat, grad, workers=hess_workers)
    eig = np.linalg.eigvalsh(H)
    pd_ok = bool(np.all(eig > 0))
    cond = float(eig.max() / eig.min()) if eig.min() > 0 else float("inf")
    try:
        cov = np.linalg.inv(H); se = np.sqrt(np.clip(np.diag(cov), 0, None))
    except np.linalg.LinAlgError:
        cov, se = None, np.full(len(theta_hat), np.nan)

    inert_set = set(inert)
    rows = []
    for i, n in enumerate(pnames):
        err = theta_hat[i] - theta_star[i]
        es = abs(err) / se[i] if (se is not None and np.isfinite(se[i]) and se[i] > 0) else np.nan
        rows.append(dict(param=n, theta_star=theta_star[i], theta_hat=theta_hat[i], abs_err=abs(err),
                         err_over_se=es, wrong_sign=(np.sign(theta_hat[i]) != np.sign(theta_star[i]) and abs(theta_star[i]) > 1e-3),
                         inert=n in inert_set))
    g1 = pd.DataFrame(rows)
    testable = ~g1["param"].isin(inert_set)
    if theta_cold is not None and testable.any():
        g2 = float(np.max(np.abs(theta_hat - theta_cold)[testable.values]))
    else:
        g2 = float("nan")  # only one start ran -> G2 reproducibility not assessed

    # G3b generic collinearity probe: report the largest off-diagonal correlation among
    # the market-opportunity household shifters (region + any access dummies). Names pulled
    # from the spec's market_opportunity block — no hardcoding.
    mkt = [s["coefficient"] for s in getattr(spec, "market_opportunity_shifters", []) or []]
    def corr(a, b):
        if cov is None or a not in pnames or b not in pnames: return np.nan
        ia, ib = spec.get_param_index(a), spec.get_param_index(b)
        return float(cov[ia, ib] / np.sqrt(cov[ia, ia] * cov[ib, ib])) if cov[ia, ia] > 0 and cov[ib, ib] > 0 else np.nan
    pair_corrs = {f"{a}|{b}": corr(a, b) for j, a in enumerate(mkt) for b in mkt[j + 1:]}
    worst = max(((abs(v), k) for k, v in pair_corrs.items() if np.isfinite(v)), default=(np.nan, None))

    print("\n" + "=" * 72 + "\nRECOVERY SUMMARY\n" + "=" * 72)
    print(f"  solver={solver_label}  G2 max|warm-cold|(testable)={g2:.3e}")
    print(f"  G3 PD={pd_ok} cond={cond:.3e} min_eig={eig.min():.3e}")
    if worst[1]:
        print(f"  G3b worst market-opp |corr| = {worst[0]:.3f}  ({worst[1]})")
    tol = 0.10
    bad = g1[testable & ((g1["abs_err"] > tol) | g1["wrong_sign"])]
    print(f"  G1 recovery: {int(testable.sum()) - len(bad)}/{int(testable.sum())} testable within tol={tol} & correct sign")
    for _, r in bad.iterrows():
        print(f"    {r['param']:16} *={r['theta_star']:+.3f} hat={r['theta_hat']:+.3f} "
              f"err={r['abs_err']:.3f} err/se={r['err_over_se']:.2f} wrong_sign={r['wrong_sign']}")

    _write_md(args.report, spec, args, results, g1, g2, pd_ok, cond, eig, pair_corrs, worst, inert, solver_label)
    print(f"\nReport: {args.report}")


def _write_md(path, spec, args, results, g1, g2, pd_ok, cond, eig, pair_corrs, worst, inert, solver_label="scipy"):
    path.parent.mkdir(parents=True, exist_ok=True)
    L = [f"# RURO Recovery Test Results — {getattr(spec,'name','spec')} ({len(spec.all_param_names)} params)\n",
         f"**mode:** {args.mode}  **years:** {args.years}  **n_hh:** {args.n_hh}  "
         f"**solver:** {solver_label}  **seed:** {args.seed}\n",
         "theta* generated generically from spec (initial+bounds), no param names hardcoded; "
         "synthetic choice drawn (vectorized) from theta* on the REAL alternatives.\n",
         "\n## Starts\n| start | success | LL | nit | sec |", "|---|---|---|---|---|"]
    for k, v in results.items():
        L.append(f"| {k} | {v['success']} | {v['ll']:.3f} | {v['nit']} | {v['sec']} |")
    L += [f"\n**G2** max|warm−cold| (testable) = {g2:.3e}",
          f"\n## G3 Conditioning\n- PD: **{pd_ok}**\n- cond: **{cond:.3e}**\n- min eig: **{eig.min():.3e}**, max: {eig.max():.3e}",
          f"\n## G3b market-opportunity collinearity (generic)\n- worst |corr| = **{worst[0]:.3f}** ({worst[1]})"]
    redundant = np.isfinite(worst[0]) and worst[0] > 0.9
    L.append(f"- **Verdict: market-opp access shifters {'NEAR-COLLINEAR (spatially redundant)' if redundant else 'SEPARATELY IDENTIFIED'}**\n")
    if inert:
        L.append(f"\n_Inert on this slice (excluded from G1): {sorted(inert)}_\n")
    L += ["\n## G1 / G4 per-param recovery\n",
          "| param | theta* | theta_hat | abs_err | err/se | wrong_sign | inert |",
          "|---|---|---|---|---|---|---|"]
    for _, r in g1.iterrows():
        es = f"{r['err_over_se']:.2f}" if np.isfinite(r["err_over_se"]) else "n/a"
        L.append(f"| {r['param']} | {r['theta_star']:+.4f} | {r['theta_hat']:+.4f} | "
                 f"{r['abs_err']:.4f} | {es} | {r['wrong_sign']} | {r['inert']} |")
    path.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
