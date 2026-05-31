"""
Exact joint Hessian via jax.hessian on the VALIDATED JAX backend (Check 5).

The v2 recovery gate's Check 5 computes a NUMERICAL Hessian (49 columns x 2
central-difference gradient evals) of the joint negLL, using the production
numpy gradient -- which carries the box_cox_derivative_theta Taylor bug near
theta_c. That bug contaminates the Hessian exactly where the v2 gate found a
non-PD direction.

This module computes the EXACT Hessian by autodiff (jax.hessian) on the joint
negLL = singles_male + singles_female + couples, reusing the JAX builders that
were validated to machine precision against the engine (jax_ll_probe.py). It:

  1. assembles joint_neg_ll(theta) from the three validated group builders;
  2. confirms joint negLL + gradient still match the engine (sanity);
  3. computes H_jax = jax.hessian(joint_neg_ll)(theta) -- exact;
  4. computes H_num = engine numerical Hessian (the v2 Check-5 path) for
     comparison;
  5. runs the SAME G3b verdict (_hessian_verdict) on BOTH and reports whether
     the exact Hessian changes the PD verdict.

If H_jax is PD where H_num was not, the v2 Check-5 FAIL was (partly) the engine
gradient bug, not a real flat direction. If H_jax is ALSO non-PD on the same
beta_ll subspace, the weak identification is real and survives exact derivatives.

GPU-ready (jax_enable_x64, no device pinning). jax.hessian parallelises on a
GPU machine unchanged.

USAGE:
  python jax_joint_hessian.py --n-hh 300 --couples-stem fr_p3a_bpool_engine_ready_20x20
  python jax_joint_hessian.py --n-hh 0   --couples-stem fr_p3a_bpool_engine_ready_20x20
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

_script_dir = Path(__file__).resolve().parent
_enhanced_dir = _script_dir.parent / "enhanced"
sys.path.insert(0, str(_enhanced_dir))
sys.path.insert(0, str(_script_dir))

import estimation_spec_parser as sp        # noqa: E402
import estimation_utils as eu              # noqa: E402
import estimation_engine as ee             # noqa: E402
import joint_recovery_test as jrt          # noqa: E402

import jax                                  # noqa: E402
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp                     # noqa: E402

# the validated builders
from jax_ll_probe import build_jax_singles_ll, build_jax_couples_ll  # noqa: E402


def build_joint_neg_ll(spec, data_sm, data_sf, data_cou):
    """joint negLL(theta) = singles_male + singles_female + couples, one shared
    49-vector. Each sub-builder is the machine-precision-validated JAX fn."""
    f_sm, _ = build_jax_singles_ll(data_sm, spec, is_male=True)
    f_sf, _ = build_jax_singles_ll(data_sf, spec, is_male=False)
    f_cou, _ = build_jax_couples_ll(data_cou, spec)

    def joint(theta):
        return f_sm(theta) + f_sf(theta) + f_cou(theta)

    return jax.jit(joint)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", type=Path,
                    default=_script_dir / "specs" / "estimation_spec_joint_pooled_v1.yaml")
    ap.add_argument("--engine-ready-stem", default="fr_p3a_bpool_engine_ready")
    ap.add_argument("--couples-stem", default="fr_p3a_bpool_engine_ready_20x20")
    ap.add_argument("--years", default="2015,2016,2017")
    ap.add_argument("--n-hh", type=int, default=300)
    ap.add_argument("--theta-star", type=Path,
                    default=_script_dir / "specs" / "theta_star_joint_v1.csv")
    ap.add_argument("--theta-csv", type=Path, default=None,
                    help="Optional: evaluate the Hessian at an arbitrary theta CSV "
                         "(e.g. a converged theta_hat) instead of theta_star.")
    ap.add_argument("--tighten-leisure-bounds", action="store_true",
                    help="Apply the v2 remedy (theta_l_* in [-4,-0.3]) before "
                         "clamping theta -- matches the v2 gate setup.")
    ap.add_argument("--skip-numerical", action="store_true",
                    help="Skip the engine numerical Hessian (slow at full data); "
                         "report only the exact JAX Hessian verdict.")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    print(f"JAX {jax.__version__}  backend={jax.default_backend()}  "
          f"x64={jax.config.read('jax_enable_x64')}  devices={jax.devices()}")

    spec = sp.parse_specification(args.spec)
    pnames = spec.all_param_names
    years = [] if args.years.strip().lower() == "all" else [int(y) for y in args.years.split(",")]

    if args.tighten_leisure_bounds:
        for pn in ("theta_l_sm", "theta_l_sf", "theta_l_m", "theta_l_f"):
            if pn in spec.bounds:
                spec.bounds[pn] = (-4.0, -0.3)
        print("  [remedy] tightened leisure bounds to [-4.0,-0.3]")

    # ---- load all three groups (same as the gate) ----
    t0 = time.time()
    data_sm, data_sf, data_cou = jrt.build_data_objects(
        args.engine_ready_stem, years, args.n_hh, couples_stem=args.couples_stem)
    print(f"loaded in {time.time()-t0:.1f}s  sm={data_sm.n_groups} "
          f"sf={data_sf.n_groups} cou={data_cou.n_groups} "
          f"(cou alts={data_cou.n_obs//data_cou.n_groups})")

    # ---- theta (clamped into bounds like the gate) ----
    src = args.theta_csv if args.theta_csv else args.theta_star
    theta = np.asarray(jrt.load_theta_star_from_csv(src, spec), dtype=np.float64)
    for i, pn in enumerate(pnames):
        if pn in spec.bounds:
            lo, hi = spec.bounds[pn]
            if lo is not None:
                theta[i] = max(theta[i], float(lo) + 1e-9)
            if hi is not None:
                theta[i] = min(theta[i], float(hi) - 1e-9)

    # ---- build joint JAX negLL; sanity-check LL + grad vs engine ----
    joint = build_joint_neg_ll(spec, data_sm, data_sf, data_cou)
    th = jnp.asarray(theta, dtype=jnp.float64)
    t0 = time.time()
    ll_jax = float(joint(th))           # triggers compile
    jgrad = jax.jit(jax.grad(joint))
    g_jax = np.asarray(jgrad(th))       # triggers grad compile
    t_compile = time.time() - t0

    ll_eng = float(ee.compute_likelihood_joint(theta, data_sm, data_sf, data_cou, spec))
    g_eng = np.asarray(ee.compute_gradient_joint(theta, data_sm, data_sf, data_cou, spec))
    ll_d = abs(ll_jax - ll_eng)
    g_d = float(np.max(np.abs(g_jax - g_eng)))
    g_wi = int(np.argmax(np.abs(g_jax - g_eng)))
    print(f"\n  sanity: negLL jax={ll_jax:.6f} eng={ll_eng:.6f} |Δ|={ll_d:.2e}")
    print(f"  sanity: max|Δgrad|={g_d:.2e} at {pnames[g_wi]} "
          f"(expected ~theta_c_singles from the engine Taylor bug)")

    # ---- EXACT Hessian via jax.hessian ----
    print(f"\n  computing exact jax.hessian ({len(pnames)} params) ...")
    t0 = time.time()
    H_jax_fn = jax.jit(jax.hessian(joint))
    H_jax = np.asarray(H_jax_fn(th))
    H_jax = 0.5 * (H_jax + H_jax.T)
    t_hess_jax = time.time() - t0
    print(f"  jax.hessian done in {t_hess_jax:.2f}s")

    vj = jrt._hessian_verdict(spec, H_jax)
    print(f"\n  [EXACT JAX HESSIAN] {vj['verdict_str']}")
    print(f"    PD={vj['pd_ok']}  n_nonpos_eig={sum(1 for e in vj['eig'] if e <= 0)}  "
          f"min_eig={float(np.min(vj['eig'])):.3e}")

    # ---- engine numerical Hessian (the v2 Check-5 path) for comparison ----
    if not args.skip_numerical:
        print(f"\n  computing engine NUMERICAL Hessian (v2 Check-5 path) ...")
        def grad_func(t):
            return ee.compute_gradient_joint(t, data_sm, data_sf, data_cou, spec)
        t0 = time.time()
        H_num = jrt.numerical_hessian(theta, grad_func, workers=min(8, 8))
        t_hess_num = time.time() - t0
        print(f"  numerical Hessian done in {t_hess_num:.1f}s")
        vn = jrt._hessian_verdict(spec, H_num)
        print(f"\n  [ENGINE NUMERICAL HESSIAN] {vn['verdict_str']}")
        print(f"    PD={vn['pd_ok']}  n_nonpos_eig={sum(1 for e in vn['eig'] if e <= 0)}  "
              f"min_eig={float(np.min(vn['eig'])):.3e}")

        hd = float(np.max(np.abs(H_jax - H_num)))
        print(f"\n  max|H_jax - H_num| = {hd:.3e}")

        # ---- the decisive comparison ----
        print("\n" + "=" * 72)
        if vj['pd_ok'] and not vn['pd_ok']:
            print("  VERDICT: EXACT Hessian is PD where the NUMERICAL one was NOT.")
            print("  -> the v2 Check-5 non-PD was (partly) the engine gradient bug,")
            print("     not a real flat direction. Re-assess identification.")
        elif (not vj['pd_ok']) and (not vn['pd_ok']):
            print("  VERDICT: BOTH non-PD on the same subspace -> the weak")
            print("  identification is REAL and survives exact derivatives.")
            print("  The memo §5 beta_ll treatment stands.")
        elif vj['pd_ok'] and vn['pd_ok']:
            print("  VERDICT: BOTH PD -> identified.")
        else:
            print("  VERDICT: exact non-PD but numerical PD -- investigate "
                  "(unexpected; check Hessian eps / sample).")
        print("=" * 72)
    else:
        print("\n  (numerical Hessian skipped; exact JAX verdict above is authoritative)")

    print(f"\n  timing: jax compile+grad={t_compile:.1f}s  jax.hessian={t_hess_jax:.2f}s")


if __name__ == "__main__":
    main()
