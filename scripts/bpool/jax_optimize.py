"""
JAX-backed warm-started optimizer for the RURO joint MNL, + exact Check-5.

Uses the machine-precision-validated JAX joint negLL (jax_ll_probe builders,
assembled in jax_joint_hessian.build_joint_neg_ll) and its jax.grad as the
objective+gradient for scipy's L-BFGS-B (box-constrained, honours spec bounds).
Warm-starts from theta_star to de-risk the multi-basin trap that bit cold
scipy runs historically. After convergence it computes the EXACT Hessian
(jax.hessian) AT THE MLE and applies the G3b verdict -- this is the real
Check-5 test (the v2 gate evaluates the Hessian at the converged theta_hat,
not at theta_star).

NO GAMS / NO CONOPT. On a GPU machine the same code runs on the GPU (x64,
no device pinning).

VALIDATION mode (--validate-vs-conopt): run on the 49-param spec at full data;
the converged LL must match the v2 CONOPT result (negLL ~ 49040.64) to confirm
the JAX+scipy optimizer finds the same basin as CONOPT.

USAGE:
  # validate the optimizer against the v2 CONOPT result (49-param, full data):
  python jax_optimize.py --spec .../estimation_spec_joint_pooled_v1.yaml \
      --n-hh 0 --tighten-leisure-bounds --hessian

  # the real test: 48-param beta_ll=0, converge + exact Check-5 at the MLE:
  python jax_optimize.py --spec .../estimation_spec_joint_pooled_v1_bll0.yaml \
      --n-hh 0 --tighten-leisure-bounds --hessian
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

_script_dir = Path(__file__).resolve().parent
_enhanced_dir = _script_dir.parent / "enhanced"
sys.path.insert(0, str(_enhanced_dir))
sys.path.insert(0, str(_script_dir))

import estimation_spec_parser as sp        # noqa: E402
import estimation_engine as ee             # noqa: E402
import joint_recovery_test as jrt          # noqa: E402

import jax                                  # noqa: E402
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp                     # noqa: E402

from jax_joint_hessian import build_joint_neg_ll  # noqa: E402


def _bounds_list(spec):
    out = []
    for n in spec.all_param_names:
        if n in spec.bounds:
            lo, hi = spec.bounds[n]
            out.append((None if lo is None else float(lo),
                        None if hi is None else float(hi)))
        else:
            out.append((None, None))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", type=Path,
                    default=_script_dir / "specs" / "estimation_spec_joint_pooled_v1_bll0.yaml")
    ap.add_argument("--engine-ready-stem", default="fr_p3a_bpool_engine_ready")
    ap.add_argument("--couples-stem", default="fr_p3a_bpool_engine_ready_20x20")
    ap.add_argument("--years", default="2015,2016,2017")
    ap.add_argument("--n-hh", type=int, default=300)
    ap.add_argument("--theta-star", type=Path,
                    default=_script_dir / "specs" / "theta_star_joint_v1.csv")
    ap.add_argument("--tighten-leisure-bounds", action="store_true")
    ap.add_argument("--hessian", action="store_true",
                    help="After convergence, compute exact jax.hessian at the MLE "
                         "and apply the G3b Check-5 verdict.")
    ap.add_argument("--solver", default="both",
                    choices=["scipy", "optimistix", "both"],
                    help="scipy=L-BFGS-B only; optimistix=BFGS polish after a "
                         "scipy warm pass; both=scipy then optimistix (default).")
    ap.add_argument("--gtol", type=float, default=1e-6)
    ap.add_argument("--maxiter", type=int, default=2000)
    ap.add_argument("--out-csv", type=Path, default=None,
                    help="Write the converged theta_hat (parameter,value) CSV.")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    print(f"JAX {jax.__version__}  backend={jax.default_backend()}  "
          f"x64={jax.config.read('jax_enable_x64')}")

    spec = sp.parse_specification(args.spec)
    pnames = spec.all_param_names
    years = [] if args.years.strip().lower() == "all" else [int(y) for y in args.years.split(",")]
    print(f"spec: {spec.name}  ({len(pnames)} params)")

    if args.tighten_leisure_bounds:
        for pn in ("theta_l_sm", "theta_l_sf", "theta_l_m", "theta_l_f"):
            if pn in spec.bounds:
                spec.bounds[pn] = (-4.0, -0.3)
        print("  [remedy] tightened leisure bounds to [-4.0,-0.3]")

    t0 = time.time()
    data_sm, data_sf, data_cou = jrt.build_data_objects(
        args.engine_ready_stem, years, args.n_hh, couples_stem=args.couples_stem)
    print(f"loaded in {time.time()-t0:.1f}s  sm={data_sm.n_groups} "
          f"sf={data_sf.n_groups} cou={data_cou.n_groups} "
          f"(cou alts={data_cou.n_obs//data_cou.n_groups})")

    # theta_star (clamped) as warm start
    theta0 = np.asarray(jrt.load_theta_star_from_csv(args.theta_star, spec), dtype=np.float64)
    bnds = _bounds_list(spec)
    for i, (lo, hi) in enumerate(bnds):
        if lo is not None:
            theta0[i] = max(theta0[i], lo + 1e-9)
        if hi is not None:
            theta0[i] = min(theta0[i], hi - 1e-9)

    # JAX objective + gradient (jit-compiled)
    joint = build_joint_neg_ll(spec, data_sm, data_sf, data_cou)
    jval = jax.jit(joint)
    jgrad = jax.jit(jax.grad(joint))
    # warm compile
    th0 = jnp.asarray(theta0)
    _ = float(jval(th0)); _ = np.asarray(jgrad(th0))

    def fun(x):
        return float(jval(jnp.asarray(x)))

    def grad(x):
        return np.asarray(jgrad(jnp.asarray(x)), dtype=np.float64)

    print(f"\n  warm-start negLL = {fun(theta0):.6f}")

    # Stage 1: scipy L-BFGS-B (box-constrained) gets into the basin fast.
    print(f"  Stage 1: scipy L-BFGS-B (box-constrained, JAX grad) ...")
    t0 = time.time()
    res = minimize(fun, theta0, jac=grad, method="L-BFGS-B", bounds=bnds,
                   options={"maxiter": args.maxiter, "gtol": args.gtol,
                            "ftol": 1e-15, "maxls": 60})
    theta_hat = res.x
    g1 = float(np.max(np.abs(grad(theta_hat))))
    print(f"    {time.time()-t0:.1f}s  negLL={res.fun:.6f}  max|grad|={g1:.3e}  "
          f"iters={res.nit}")

    # Stage 2: optimistix BFGS (pure-JAX, tight) polishes to small gradient.
    # Unconstrained: warm-started from the stage-1 (in-bounds) point. We verify
    # interiority afterwards; if the MLE is interior the unconstrained optimum
    # equals the constrained one and the exact Hessian there is the valid Check-5.
    if args.solver in ("optimistix", "both"):
        import optimistix as optx
        print(f"  Stage 2: optimistix BFGS (pure-JAX, rtol={args.gtol}) ...")
        t0 = time.time()
        def ox_fn(y, _args):
            return joint(y)
        solver = optx.BFGS(rtol=args.gtol, atol=args.gtol)
        sol = optx.minimise(ox_fn, solver, jnp.asarray(theta_hat),
                            max_steps=args.maxiter, throw=False)
        theta_hat = np.asarray(sol.value, dtype=np.float64)
        g2 = float(np.max(np.abs(grad(theta_hat))))
        print(f"    {time.time()-t0:.1f}s  negLL={fun(theta_hat):.6f}  "
              f"max|grad|={g2:.3e}  result={sol.result}")

    gnorm = float(np.max(np.abs(grad(theta_hat))))
    print(f"\n  FINAL max|grad| at theta_hat = {gnorm:.3e}")

    # Interiority check: is any param at a bound? (bound-binding invalidates the
    # unconstrained Hessian as the identification test).
    at_bound = []
    for i, (lo, hi) in enumerate(bnds):
        v = theta_hat[i]
        if lo is not None and abs(v - lo) < 1e-5:
            at_bound.append((pnames[i], "lo", float(lo)))
        if hi is not None and abs(v - hi) < 1e-5:
            at_bound.append((pnames[i], "hi", float(hi)))
    if at_bound:
        print(f"  WARNING: {len(at_bound)} param(s) at a bound: "
              f"{[(n, s) for n, s, _ in at_bound]}")
        print("  -> unconstrained Hessian Check-5 is only valid for interior MLEs.")
    else:
        print("  interiority: PASS (no param at a bound) — Hessian Check-5 valid.")

    # Cross-check the converged negLL against the production engine
    ll_eng = float(ee.compute_likelihood_joint(theta_hat, data_sm, data_sf, data_cou, spec))
    print(f"  engine negLL at theta_hat = {ll_eng:.6f}  "
          f"(Δ vs JAX = {abs(ll_eng-fun(theta_hat)):.2e})")

    if args.out_csv:
        import csv
        args.out_csv.parent.mkdir(parents=True, exist_ok=True)
        with open(args.out_csv, "w", newline="") as f:
            w = csv.writer(f); w.writerow(["parameter", "value"])
            for n, v in zip(pnames, theta_hat):
                w.writerow([n, float(v)])
        print(f"  [csv] theta_hat -> {args.out_csv}")

    # ---- exact Check-5 Hessian AT THE MLE ----
    if args.hessian:
        print(f"\n  computing exact jax.hessian AT THE MLE ({len(pnames)} params) ...")
        t0 = time.time()
        H = np.asarray(jax.jit(jax.hessian(joint))(jnp.asarray(theta_hat)))
        H = 0.5 * (H + H.T)
        print(f"  jax.hessian done in {time.time()-t0:.2f}s")
        v = jrt._hessian_verdict(spec, H)
        w = v["eig"]
        neg = w[w <= 1e-8]  # near-zero or negative = weak/flat at the MLE
        print(f"\n  [EXACT HESSIAN @ MLE] {v['verdict_str']}")
        print(f"    PD={v['pd_ok']}  min_eig={float(w.min()):.3e}  "
              f"n_eig<=1e-8={len(neg)}")
        print(f"    smallest 6 eigenvalues: {np.round(np.sort(w)[:6], 4)}")
        print("\n" + "=" * 72)
        if v["pd_ok"]:
            print("  CHECK 5 @ MLE: PASS (PD) — identified.")
            print(f"  -> {spec.name} is identified at its MLE.")
        else:
            print("  CHECK 5 @ MLE: FAIL (non-PD).")
            bd = v["bad_dirs"][0][1] if v["bad_dirs"] else []
            print(f"  flat direction loads on: "
                  f"{', '.join(f'{n}({w:.2f})' for n, w in bd[:5])}")
        print("=" * 72)


if __name__ == "__main__":
    main()
