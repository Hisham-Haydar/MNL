"""
Profile the likelihood in the couples-male leisure block (beta_l0_m, theta_l_m).

The JAX synthetic gate showed this block won't converge in bounds: beta_l0_m
jams ~0 and theta_l_m wanders. Hypothesis: beta_l0_m~0 in the DGP makes the
term beta_l0_m*BC(l_m) ~0, so theta_l_m (its curvature) has no signal -> a flat
valley in (beta_l0_m, theta_l_m). This script MEASURES that flatness, before any
spec change. Diagnostic only -- no spec change, no estimation decision.

Three views, all on the SYNTHETIC data (same DGP as the gate, use_actual_choice):
  A. 2-D grid: hold the other 46 params at the base point, sweep
     (beta_l0_m, theta_l_m); report negLL surface. A near-constant ridge =
     flat valley = weak joint identification.
  B. 1-D profile of theta_l_m: for each theta_l_m on a grid, RE-OPTIMIZE the
     other couples-male leisure params (beta_l0_m, beta_l_age_m, beta_l_age2_m)
     with everything else fixed; report the profiled negLL. Flat profile =
     theta_l_m not identified.
  C. 1-D profile of beta_l0_m: symmetric.

The curvature of the profile at its minimum ~ the Fisher information for that
param; near-zero curvature = unidentified.

GPU-ready (x64, no device pinning).

USAGE:
  python jax_profile_couples_leisure.py --n-hh 0 \
    --couples-stem fr_p3a_bpool_engine_ready_20x20 \
    --out docs/.../RURO_couples_leisure_profile_v1.md
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
import joint_recovery_test as jrt          # noqa: E402

import jax                                  # noqa: E402
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp                     # noqa: E402

from jax_recovery_gate import _build_joint  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", type=Path,
                    default=_script_dir / "specs" / "estimation_spec_joint_pooled_v1_bll0.yaml")
    ap.add_argument("--engine-ready-stem", default="fr_p3a_bpool_engine_ready")
    ap.add_argument("--couples-stem", default="fr_p3a_bpool_engine_ready_20x20")
    ap.add_argument("--years", default="2015,2016,2017")
    ap.add_argument("--n-hh", type=int, default=0)
    ap.add_argument("--seed", type=int, default=20260530)
    ap.add_argument("--theta-star", type=Path,
                    default=_script_dir / "specs" / "theta_star_joint_v1.csv")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    print(f"JAX {jax.__version__}  backend={jax.default_backend()}")
    spec = sp.parse_specification(args.spec)
    pn = spec.all_param_names
    years = [] if args.years.strip().lower() == "all" else [int(y) for y in args.years.split(",")]
    rng = np.random.default_rng(args.seed)

    # data + synthetic DGP (identical to the gate)
    dsm, dsf, dco = jrt.build_data_objects(args.engine_ready_stem, years, args.n_hh,
                                           couples_stem=args.couples_stem)
    theta_star = np.asarray(jrt.load_theta_star_from_csv(args.theta_star, spec),
                            dtype=np.float64)
    sm_s, sf_s, cou_s = jrt.run_synthetic_dgp(spec, dsm, dsf, dco, theta_star, rng)
    joint = _build_joint(spec, sm_s, sf_s, cou_s, use_actual_choice=True)
    jval = jax.jit(joint)

    i_b0 = pn.index("beta_l0_m")
    i_tl = pn.index("theta_l_m")
    # couples-male leisure block params to re-optimize in the 1-D profiles
    cm_block = [pn.index(p) for p in
                ("beta_l0_m", "beta_l_age_m", "beta_l_age2_m", "theta_l_m")
                if p in pn]
    base = theta_star.copy()
    base_negll = float(jval(jnp.asarray(base)))
    print(f"\nbase point = theta_star;  negLL(base) = {base_negll:.4f}")
    print(f"  beta_l0_m(star) = {base[i_b0]:+.5f}   theta_l_m(star) = {base[i_tl]:+.5f}")

    R = {"base_negll": base_negll, "beta_l0_m_star": float(base[i_b0]),
         "theta_l_m_star": float(base[i_tl])}

    # ----- A. 2-D grid (other params fixed at base) -----
    print("\n--- A. 2-D grid (other 46 params fixed at base) ---")
    b0_grid = np.array([1e-4, 0.005, 0.05, 0.2, 0.5, 1.0, 2.0])  # beta_l0_m (>=0)
    tl_grid = np.array([-4.0, -2.0, -1.0, -0.82, -0.4, 0.0, 0.5, 0.9])  # theta_l_m
    surf = np.full((len(b0_grid), len(tl_grid)), np.nan)
    for ia, b0 in enumerate(b0_grid):
        for ib, tl in enumerate(tl_grid):
            t = base.copy(); t[i_b0] = b0; t[i_tl] = tl
            surf[ia, ib] = float(jval(jnp.asarray(t)))
    print("    negLL surface (rows=beta_l0_m, cols=theta_l_m):")
    print("       theta_l_m: " + " ".join(f"{x:+6.2f}" for x in tl_grid))
    for ia, b0 in enumerate(b0_grid):
        rng_row = surf[ia].max() - surf[ia].min()
        print(f"    b0={b0:7.4f}: " +
              " ".join(f"{surf[ia,ib]-base_negll:+6.1f}" for ib in range(len(tl_grid)))
              + f"   (row span={rng_row:.1f})")
    R["grid_b0"] = b0_grid.tolist(); R["grid_tl"] = tl_grid.tolist()
    R["grid_negll_minus_base"] = (surf - base_negll).tolist()
    # the valley: for each beta_l0_m, how much does negLL vary across theta_l_m?
    tl_spans = (surf.max(axis=1) - surf.min(axis=1))
    print("\n    theta_l_m sensitivity at each beta_l0_m "
          "(negLL span across theta_l_m grid):")
    for ia, b0 in enumerate(b0_grid):
        flag = "  <-- FLAT (theta_l_m ~unidentified here)" if tl_spans[ia] < 1.0 else ""
        print(f"    beta_l0_m={b0:7.4f}: span={tl_spans[ia]:8.2f}{flag}")
    R["tl_span_per_b0"] = tl_spans.tolist()

    # ----- helper: profile one param, re-optimizing the rest of the cm block -----
    def profile(free_idx, grid, label):
        print(f"\n--- {label} ---")
        others = [j for j in cm_block if j != free_idx]
        prof = []
        for g in grid:
            t0 = base.copy(); t0[free_idx] = g
            sub0 = t0[others]
            sub_bnds = [spec.bounds.get(pn[j], (None, None)) for j in others]

            def f(sub):
                tt = t0.copy(); tt[others] = sub
                return float(jval(jnp.asarray(tt)))
            # numeric grad via JAX on the full vector, restricted to `others`
            gfull = jax.jit(jax.grad(joint))
            def gfun(sub):
                tt = t0.copy(); tt[others] = sub
                gg = np.asarray(gfull(jnp.asarray(tt)))
                return gg[others]
            res = minimize(f, sub0, jac=gfun, method="L-BFGS-B",
                           bounds=sub_bnds, options={"maxiter": 300, "ftol": 1e-12})
            prof.append(float(res.fun))
        prof = np.array(prof)
        print(f"    {pn[free_idx]:14s} grid: " + " ".join(f"{x:+6.2f}" for x in grid))
        print(f"    profiled negLL-base: " +
              " ".join(f"{p-base_negll:+7.2f}" for p in prof))
        span = prof.max() - prof.min()
        argmin = grid[int(prof.argmin())]
        print(f"    profile span = {span:.3f}  (argmin at {pn[free_idx]}={argmin:+.3f})")
        if span < 2.0:
            print(f"    <-- FLAT PROFILE: {pn[free_idx]} is WEAKLY IDENTIFIED "
                  f"(span {span:.2f} < 2 over the grid)")
        return {"grid": grid.tolist(), "profiled_negll": prof.tolist(),
                "span": float(span), "argmin": float(argmin)}

    # ----- B. profile theta_l_m -----
    R["profile_theta_l_m"] = profile(i_tl,
                                     np.array([-4, -2, -1, -0.82, -0.4, 0.0, 0.5, 0.9]),
                                     "B. profile theta_l_m (re-opt beta_l0_m, age, age2)")

    # ----- C. profile beta_l0_m -----
    R["profile_beta_l0_m"] = profile(i_b0,
                                     np.array([1e-4, 0.005, 0.05, 0.2, 0.5, 1.0, 2.0, 5.0]),
                                     "C. profile beta_l0_m (re-opt theta_l_m, age, age2)")

    # ----- D. BOUNDED real-data couples-leisure estimate (the arbiter) -----
    # Synthetic flatness alone can't distinguish "model weakly identified" from
    # "theta_star built wrong". A BOUNDED (scipy box-constrained, NOT optimistix)
    # real-data fit settles it: if bounded REAL data ALSO drives beta_l0_m to its
    # floor -> block genuinely weak -> pinning theta_l_m justified. If bounded
    # real data finds INTERIOR beta_l0_m -> theta_star's ~0 was the artefact ->
    # fix is rebuilding theta_star, not pinning.
    # NOTE: this is a REAL-DATA diagnostic fit (couples-leisure ID only; NO
    # welfare/decomposition). Bounded = stays in valid spec region (the prior
    # real-data "PD" was OUT OF BOUNDS via unconstrained optimistix).
    print("\n--- D. BOUNDED real-data couples-leisure estimate (the arbiter) ---")
    print("    (real-data fit, box-constrained scipy; couples-leisure ID only)")
    joint_real = _build_joint(spec, dsm, dsf, dco, use_actual_choice=False)
    jval_real = jax.jit(joint_real)
    jgrad_real = jax.jit(jax.grad(joint_real))
    bnds_full = [spec.bounds.get(n, (None, None)) for n in pn]
    th0 = theta_star.copy()
    for i, (lo, hi) in enumerate(bnds_full):
        if lo is not None:
            th0[i] = max(th0[i], lo + 1e-9)
        if hi is not None:
            th0[i] = min(th0[i], hi - 1e-9)

    def fr(x):
        return float(jval_real(jnp.asarray(x)))
    def gr(x):
        return np.asarray(jgrad_real(jnp.asarray(x)), dtype=np.float64)

    t0 = time.time()
    _it = {"k": 0}
    def cb(xk):
        _it["k"] += 1
        if _it["k"] % 100 == 0 or _it["k"] == 1:
            print(f"      [realfit iter {_it['k']:4d}] negLL={fr(xk):.2f} "
                  f"max|g|={float(np.max(np.abs(gr(xk)))):.2e} [{time.time()-t0:.0f}s]",
                  flush=True)
    res = minimize(fr, th0, jac=gr, method="L-BFGS-B", bounds=bnds_full,
                   callback=cb, options={"maxiter": 4000, "gtol": 1e-6,
                                         "ftol": 1e-15, "maxls": 60})
    thr = res.x
    gfin = float(np.max(np.abs(gr(thr))))
    b0_real = float(thr[i_b0]); tl_real = float(thr[i_tl])
    b0_lo = spec.bounds.get("beta_l0_m", (None, None))[0]
    at_floor = (b0_lo is not None and abs(b0_real - float(b0_lo)) < 1e-4)
    print(f"    bounded real-data fit: negLL={res.fun:.2f} max|grad|={gfin:.2e} "
          f"[{time.time()-t0:.0f}s]")
    print(f"    beta_l0_m: star={base[i_b0]:+.5f}  bounded_real={b0_real:+.5f}  "
          f"floor={b0_lo}  at_floor={at_floor}")
    print(f"    theta_l_m: star={base[i_tl]:+.5f}  bounded_real={tl_real:+.5f}")
    R["bounded_realdata"] = {
        "beta_l0_m": b0_real, "theta_l_m": tl_real,
        "beta_l0_m_at_floor": bool(at_floor), "max_grad": gfin,
        "negll": float(res.fun), "converged": bool(gfin < 1e-2)}

    # ----- verdict -----
    print("\n" + "=" * 72)
    tl_flat = R["profile_theta_l_m"]["span"] < 2.0
    b0_flat = R["profile_beta_l0_m"]["span"] < 2.0
    print("PROFILE VERDICT")
    print(f"  theta_l_m profile span = {R['profile_theta_l_m']['span']:.2f} "
          f"-> {'FLAT (weakly identified)' if tl_flat else 'curved (identified)'}")
    print(f"  beta_l0_m profile span = {R['profile_beta_l0_m']['span']:.2f} "
          f"-> {'FLAT (weakly identified)' if b0_flat else 'curved (identified)'}")
    # The arbiter: bounded real-data beta_l0_m
    bd = R.get("bounded_realdata", {})
    b0_real_floor = bd.get("beta_l0_m_at_floor", None)
    print(f"\n  ARBITER (bounded real-data beta_l0_m): "
          f"{bd.get('beta_l0_m', float('nan')):+.5f}  "
          f"at_floor={b0_real_floor}")
    if tl_flat and b0_real_floor:
        verdict = ("theta_l_m WEAKLY IDENTIFIED and bounded REAL data ALSO drives "
                   "beta_l0_m to its floor -> the couples-male leisure block is "
                   "GENUINELY weak (not a theta_star artefact). FIX: pin theta_l_m "
                   "(or beta_l0_m) to a calibrated value, like beta_ll. Rebuilding "
                   "theta_star would NOT help.")
    elif tl_flat and (b0_real_floor is False):
        verdict = ("theta_l_m flat in SYNTHETIC, but bounded REAL data finds an "
                   "INTERIOR beta_l0_m -> theta_star's ~0 beta_l0_m was the "
                   "ARTEFACT. FIX: REBUILD theta_star with the bounded real-data "
                   "couples-male leisure values; do NOT pin. The model may be fine.")
    elif not tl_flat:
        verdict = ("theta_l_m profile is CURVED (identified) -> the gate's "
                   "non-convergence was solver/bound, not weak ID. Re-gate with "
                   "better convergence; no spec change needed.")
    else:
        verdict = "Inconclusive — inspect the profile + arbiter numbers."
    print(f"\n  => {verdict}")
    print("=" * 72)
    R["theta_l_m_flat"] = bool(tl_flat); R["beta_l0_m_flat"] = bool(b0_flat)
    R["verdict"] = verdict

    if args.out:
        import json
        L = ["# Couples-male leisure profile — (beta_l0_m, theta_l_m)", "",
             f"base negLL = {base_negll:.4f}; beta_l0_m(star)={base[i_b0]:+.5f}, "
             f"theta_l_m(star)={base[i_tl]:+.5f}", "",
             "> Diagnostic profile of the suspected flat valley. Synthetic DGP "
             "(use_actual_choice). No spec change.", "",
             f"**theta_l_m profile span = {R['profile_theta_l_m']['span']:.2f}** "
             f"({'FLAT — weakly identified' if tl_flat else 'curved — identified'})", "",
             f"**beta_l0_m profile span = {R['profile_beta_l0_m']['span']:.2f}** "
             f"({'FLAT — weakly identified' if b0_flat else 'curved — identified'})", "",
             "## Full JSON", "", "```json", json.dumps(R, indent=2), "```", ""]
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text("\n".join(L), encoding="utf-8")
        print(f"\n[out] {args.out}")


if __name__ == "__main__":
    main()
