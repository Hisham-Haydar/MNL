"""
JAX synthetic recovery gate (Checks 1-6) — fast equivalent of the CONOPT gate.

Runs the SAME six-check synthetic recovery the sanctioned CONOPT harness
(joint_recovery_test.py) runs, but with the validated JAX backend as the
optimizer + exact Hessian instead of CONOPT. Same theta_star, same synthetic
DGP (jrt.run_synthetic_dgp), same shared/group param partition, same
thresholds, same G3b verdict (jrt._hessian_verdict). Minutes instead of ~11h.

CORRECTNESS: the JAX LL uses use_actual_choice=True (the synthetic Gumbel-max
choice lands anywhere, not at col 0). Both JAX paths are validated:
  - real-data col-0 == numpy engine to machine precision
  - synthetic actual_choice == hand-computed importance-sampling LL exactly

CHECKS (mirror joint_recovery_test.py):
  1 Synthetic DGP        : draw synthetic choices from theta_star (jrt)
  2 Shared recovery      : warm-fit, max|theta_hat - theta_star| on 29 shared
  3 Group-specific       : per-block max|err| (incl. beta_ll if present)
  4 Two-start agreement  : warm(theta_star) vs cold(spec init), max|warm-cold|
  5 Hessian PD @ MLE     : exact jax.hessian + G3b verdict
  6 Contamination        : group-specific beta_E DGP, shared-g forced

STRICT thresholds (production-resolution proper draws): C2<=0.05, C3<=0.10,
C4<=1e-6. GPU-ready (jax_enable_x64, no device pinning).

USAGE (48-param beta_ll=0 gate, full data):
  python jax_recovery_gate.py \
    --spec .../estimation_spec_joint_pooled_v1_bll0.yaml \
    --n-hh 0 --couples-stem fr_p3a_bpool_engine_ready_20x20 \
    --tighten-leisure-bounds \
    --report .../RURO_jax_recovery_gate_bll0_v1.md
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
import optimistix as optx                   # noqa: E402

from jax_ll_probe import build_jax_singles_ll, build_jax_couples_ll  # noqa: E402


def _build_joint(spec, dsm, dsf, dco, use_actual_choice):
    f_sm, _ = build_jax_singles_ll(dsm, spec, is_male=True,
                                   use_actual_choice=use_actual_choice)
    f_sf, _ = build_jax_singles_ll(dsf, spec, is_male=False,
                                   use_actual_choice=use_actual_choice)
    f_cou, _ = build_jax_couples_ll(dco, spec,
                                    use_actual_choice=use_actual_choice)

    def joint(theta):
        return f_sm(theta) + f_sf(theta) + f_cou(theta)
    return jax.jit(joint)


def _bounds(spec):
    out = []
    for n in spec.all_param_names:
        lo, hi = spec.bounds.get(n, (None, None))
        out.append((None if lo is None else float(lo),
                    None if hi is None else float(hi)))
    return out


def _optimize(joint, theta0, bnds, gtol, maxiter, label, verbose=True):
    """Two-stage scipy L-BFGS-B (box) -> optimistix BFGS (tight). Returns theta_hat."""
    jval = jax.jit(joint)
    jgrad = jax.jit(jax.grad(joint))

    def fun(x):
        return float(jval(jnp.asarray(x)))

    def grad(x):
        return np.asarray(jgrad(jnp.asarray(x)), dtype=np.float64)

    t0 = time.time()
    _it = {"k": 0}
    def cb(xk):
        _it["k"] += 1
        if verbose and (_it["k"] % 50 == 0 or _it["k"] == 1):
            print(f"      [{label} iter {_it['k']:4d}] negLL={fun(xk):.3f} "
                  f"max|g|={float(np.max(np.abs(grad(xk)))):.2e} "
                  f"[{time.time()-t0:.0f}s]", flush=True)
    res = minimize(fun, theta0, jac=grad, method="L-BFGS-B", bounds=bnds,
                   callback=cb, options={"maxiter": maxiter, "gtol": gtol,
                                         "ftol": 1e-15, "maxls": 60})
    th_scipy = res.x
    ll_scipy = fun(th_scipy)
    # optimistix polish (unconstrained) — can escape to infinity on ill-posed
    # sub-problems, so we KEEP it only if it improved AND stayed finite + in a
    # sane neighbourhood of the bounded scipy solution.
    sol = optx.minimise(lambda y, _a: joint(y),
                        optx.BFGS(rtol=gtol, atol=gtol),
                        jnp.asarray(th_scipy), max_steps=maxiter, throw=False)
    th_ox = np.asarray(sol.value, dtype=np.float64)
    # Project optimistix result back into bounds (guards unconstrained escape).
    th_ox_clip = th_ox.copy()
    for i, (lo, hi) in enumerate(bnds):
        if lo is not None:
            th_ox_clip[i] = max(th_ox_clip[i], lo)
        if hi is not None:
            th_ox_clip[i] = min(th_ox_clip[i], hi)
    ll_ox_clip = fun(th_ox_clip)
    # choose the best FINITE in-bounds point
    cands = [(ll_scipy, th_scipy, "scipy")]
    if np.isfinite(ll_ox_clip):
        cands.append((ll_ox_clip, th_ox_clip, "optimistix"))
    ll_best, th, which = min(cands, key=lambda c: c[0])
    gfin = float(np.max(np.abs(grad(th))))
    print(f"    [{label}] negLL={ll_best:.4f} max|grad|={gfin:.3e} "
          f"({which}) [{time.time()-t0:.0f}s]", flush=True)
    return th, float(ll_best), gfin


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
    ap.add_argument("--tighten-leisure-bounds", action="store_true")
    ap.add_argument("--gtol", type=float, default=1e-6)
    ap.add_argument("--maxiter", type=int, default=3000)
    ap.add_argument("--report", type=Path, default=None)
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

    rng = np.random.default_rng(args.seed)
    bnds = _bounds(spec)

    # ---- load data, theta_star (clamped) ----
    data_sm, data_sf, data_cou = jrt.build_data_objects(
        args.engine_ready_stem, years, args.n_hh, couples_stem=args.couples_stem)
    print(f"loaded: sm={data_sm.n_groups} sf={data_sf.n_groups} "
          f"cou={data_cou.n_groups} (cou alts={data_cou.n_obs//data_cou.n_groups})")
    theta_star = np.asarray(jrt.load_theta_star_from_csv(args.theta_star, spec),
                            dtype=np.float64)
    for i, (lo, hi) in enumerate(bnds):
        if lo is not None:
            theta_star[i] = max(theta_star[i], lo + 1e-9)
        if hi is not None:
            theta_star[i] = min(theta_star[i], hi - 1e-9)
    theta_cold = np.array([float(spec.initial_values.get(n, 0.0)) for n in pnames])
    for i, (lo, hi) in enumerate(bnds):
        if lo is not None:
            theta_cold[i] = max(theta_cold[i], lo + 1e-9)
        if hi is not None:
            theta_cold[i] = min(theta_cold[i], hi - 1e-9)

    R = {"spec": spec.name, "n_params": len(pnames),
         "n_hh": {"sm": data_sm.n_groups, "sf": data_sf.n_groups, "cou": data_cou.n_groups},
         "couples_alts": data_cou.n_obs // data_cou.n_groups}
    thr_c2, thr_c3, thr_c4 = 0.05, 0.10, 1e-6

    # ===== CHECK 1: synthetic DGP =====
    print("\n--- CHECK 1: synthetic DGP ---")
    sm_s, sf_s, cou_s = jrt.run_synthetic_dgp(spec, data_sm, data_sf, data_cou,
                                              theta_star, rng)
    c1 = (int(sm_s.actual_choice.sum()) == data_sm.n_groups
          and int(sf_s.actual_choice.sum()) == data_sf.n_groups
          and int(cou_s.actual_choice.sum()) == data_cou.n_groups)
    R["check1"] = {"passed": bool(c1)}
    print(f"  CHECK 1: {'PASS' if c1 else 'FAIL'}")

    # joint negLL on the synthetic data (actual_choice path)
    joint = _build_joint(spec, sm_s, sf_s, cou_s, use_actual_choice=True)

    # ===== CHECK 2: shared-from-pooled recovery (warm) =====
    print("\n--- CHECK 2: shared recovery (warm) ---")
    theta_warm, ll_warm, g_warm = _optimize(joint, theta_star, bnds,
                                            args.gtol, args.maxiter, "C2/warm")
    SUF = ("_sm", "_sf", "_m", "_f")
    shared_idx = [i for i, n in enumerate(pnames)
                  if not any(n.endswith(s) for s in SUF)
                  and n not in ("theta_c_singles", "beta_ll")]
    errs = np.abs(theta_warm[shared_idx] - theta_star[shared_idx])
    c2_max = float(errs.max()); c2_worst = pnames[shared_idx[int(errs.argmax())]]
    c2 = c2_max <= thr_c2
    R["check2"] = {"max_err": c2_max, "worst": c2_worst, "thresh": thr_c2,
                   "passed": bool(c2), "ll": ll_warm, "max_grad": g_warm,
                   "theta_hat": theta_warm.tolist()}
    print(f"  CHECK 2: max|err|={c2_max:.4f} ({c2_worst})  "
          f"{'PASS' if c2 else 'FAIL'}")

    # ===== CHECK 3: group-specific recovery =====
    print("\n--- CHECK 3: group-specific recovery ---")
    blocks = {
        "sm_leisure": [i for i, n in enumerate(pnames) if n.endswith("_sm")],
        "sf_leisure": [i for i, n in enumerate(pnames) if n.endswith("_sf")],
        "theta_c_singles": ([pnames.index("theta_c_singles")]
                            if "theta_c_singles" in pnames else []),
        "m_leisure": [i for i, n in enumerate(pnames) if n.endswith("_m")],
        "f_leisure": [i for i, n in enumerate(pnames) if n.endswith("_f")],
        "beta_ll": ([pnames.index("beta_ll")] if "beta_ll" in pnames else []),
    }
    c3_blocks = {}; c3_all = True
    for b, idx in blocks.items():
        if not idx:
            c3_blocks[b] = {"n": 0, "max_err": None, "passed": True}
            continue
        e = np.abs(theta_warm[idx] - theta_star[idx])
        me = float(e.max()); ok = me <= thr_c3
        c3_all = c3_all and ok
        c3_blocks[b] = {"n": len(idx), "max_err": me,
                        "worst": pnames[idx[int(e.argmax())]], "passed": bool(ok)}
        print(f"  {b}: max|err|={me:.4f}  {'PASS' if ok else 'FAIL'}")
    R["check3"] = {"blocks": c3_blocks, "thresh": thr_c3, "passed": bool(c3_all)}
    print(f"  CHECK 3: {'PASS' if c3_all else 'FAIL'}")

    # ===== CHECK 4: two-start agreement =====
    print("\n--- CHECK 4: two-start agreement (cold) ---")
    theta_cold_hat, ll_cold, g_cold = _optimize(joint, theta_cold, bnds,
                                               args.gtol, args.maxiter, "C4/cold")
    diff = np.abs(theta_warm - theta_cold_hat)
    c4_max = float(diff.max()); c4 = c4_max <= thr_c4
    disagreed = sorted([(pnames[i], float(diff[i]))
                        for i in np.where(diff > thr_c4)[0]], key=lambda x: -x[1])
    R["check4"] = {"max_diff": c4_max, "thresh": thr_c4, "passed": bool(c4),
                   "ll_warm": ll_warm, "ll_cold": ll_cold,
                   "disagreed": disagreed[:15]}
    print(f"  CHECK 4: max|warm-cold|={c4_max:.3e}  {'PASS' if c4 else 'FAIL'}")
    if disagreed:
        for n, dv in disagreed[:8]:
            print(f"    {n}: {dv:.3e}")

    # ===== CHECK 5: Hessian PD at the warm MLE =====
    print("\n--- CHECK 5: exact Hessian @ MLE ---")
    t0 = time.time()
    H = np.asarray(jax.jit(jax.hessian(joint))(jnp.asarray(theta_warm)))
    H = 0.5 * (H + H.T)
    v = jrt._hessian_verdict(spec, H)
    w = v["eig"]
    print(f"  jax.hessian {time.time()-t0:.1f}s  PD={v['pd_ok']}  "
          f"min_eig={float(w.min()):.3e}")
    print(f"  {v['verdict_str']}")
    R["check5"] = {"pd": bool(v["pd_ok"]), "min_eig": float(w.min()),
                   "n_nonpos": int(np.sum(w <= 1e-8)),
                   "verdict": v["verdict_str"], "passed": bool(v["pd_ok"])}
    print(f"  CHECK 5: {'PASS' if v['pd_ok'] else 'FAIL'}")

    # ===== CHECK 6: contamination =====
    print("\n--- CHECK 6: contamination (group-specific beta_E DGP) ---")
    BE = {"sm": -1.94, "sf": -1.00, "cou": -0.71}
    if "beta_E" in pnames:
        ie = pnames.index("beta_E")
        def mk(b):
            t = theta_star.copy(); t[ie] = b; return t
        rng_c = np.random.default_rng(args.seed + 6)
        import copy
        def draw_s(data, th):
            import estimation_engine as ee
            comp = ee.compute_likelihood_singles(th, data, spec, return_components=True)
            ac = jrt.draw_synthetic_choice(comp["V"], data.group_starts, data.group_ends, rng_c)
            d = copy.copy(data); d.actual_choice = ac; return d
        def draw_c(data, th):
            import estimation_engine as ee
            comp = ee.compute_likelihood_couples(th, data, spec, return_components=True)
            ac = jrt.draw_synthetic_choice(comp["V"], data.group_starts, data.group_ends, rng_c)
            d = copy.copy(data); d.actual_choice = ac; return d
        sm_c = draw_s(data_sm, mk(BE["sm"]))
        sf_c = draw_s(data_sf, mk(BE["sf"]))
        cou_c = draw_c(data_cou, mk(BE["cou"]))
        joint_c = _build_joint(spec, sm_c, sf_c, cou_c, use_actual_choice=True)
        theta_cont, _, _ = _optimize(joint_c, theta_star, bnds, args.gtol,
                                    args.maxiter, "C6/contam")
        be_hat = float(theta_cont[ie]); be_clean = float(theta_warm[ie])
        pwavg = (BE["sm"] + BE["sf"] + BE["cou"]) / 3
        inside = min(BE.values()) <= be_hat <= max(BE.values())
        # preference displacement
        disp = {}
        for b, idx in blocks.items():
            if not idx or b == "beta_ll":
                continue
            disp[b] = float(np.max(np.abs(theta_cont[idx] - theta_warm[idx])))
        R["check6"] = {"beta_e_dgp": BE, "beta_e_pwavg": pwavg,
                       "beta_e_contaminated": be_hat, "beta_e_clean": be_clean,
                       "inside_range": bool(inside), "pref_displacement": disp}
        print(f"  forced beta_E={be_hat:.4f} (clean={be_clean:.4f}, "
              f"pwavg={pwavg:.3f}, inside_range={inside})")
        for b, dv in disp.items():
            print(f"    pref displacement {b}: {dv:.4f}")
    else:
        R["check6"] = {"note": "beta_E not in spec"}

    # ===== summary =====
    print("\n" + "=" * 72)
    print("JAX SYNTHETIC RECOVERY GATE — SUMMARY")
    print("=" * 72)
    table = [("1 Synthetic DGP", R["check1"]["passed"]),
             ("2 Shared recovery", R["check2"]["passed"]),
             ("3 Group-specific", R["check3"]["passed"]),
             ("4 Two-start agreement", R["check4"]["passed"]),
             ("5 Hessian PD @ MLE", R["check5"]["passed"]),
             ("6 Contamination", True)]
    for nm, ok in table:
        print(f"  {nm:<24} {'PASS' if ok else 'FAIL'}")
    all15 = all(ok for _, ok in table[:5])
    R["all_checks_1_5_pass"] = bool(all15)
    print()
    print("  >> Checks 1-5 " + ("ALL PASS" if all15 else "NOT all pass")
          + "; Check 6 characterised.")
    print("=" * 72)

    if args.report:
        _write_report(args.report, R)
        print(f"\n[report] {args.report}")


def _write_report(path, R):
    import json
    L = [f"# JAX synthetic recovery gate — {R['spec']}", "",
         f"**Params:** {R['n_params']}  **Couples alts:** {R['couples_alts']}  "
         f"**HH:** sm={R['n_hh']['sm']} sf={R['n_hh']['sf']} cou={R['n_hh']['cou']}",
         "",
         "> Synthetic recovery on the validated JAX backend (use_actual_choice=True). "
         "Same 6 checks / thresholds / G3b verdict as the CONOPT gate; JAX optimizer "
         "+ exact jax.hessian instead of CONOPT.", "",
         "| Check | Result | Detail |", "|---|---|---|",
         f"| 1 Synthetic DGP | {'PASS' if R['check1']['passed'] else 'FAIL'} | one chosen alt/HH |",
         f"| 2 Shared recovery | {'PASS' if R['check2']['passed'] else 'FAIL'} | "
         f"max\\|err\\|={R['check2']['max_err']:.4f} ({R['check2']['worst']}), thr={R['check2']['thresh']} |",
         f"| 3 Group-specific | {'PASS' if R['check3']['passed'] else 'FAIL'} | thr={R['check3']['thresh']} |",
         f"| 4 Two-start | {'PASS' if R['check4']['passed'] else 'FAIL'} | "
         f"max\\|warm-cold\\|={R['check4']['max_diff']:.3e}, thr={R['check4']['thresh']} |",
         f"| 5 Hessian PD | {'PASS' if R['check5']['passed'] else 'FAIL'} | "
         f"min_eig={R['check5']['min_eig']:.3e}; {R['check5']['verdict']} |",
         f"| 6 Contamination | DONE | see JSON |", "",
         f"**Checks 1-5: {'ALL PASS' if R['all_checks_1_5_pass'] else 'NOT all pass'}.**", "",
         "### Check 3 blocks", "", "| Block | max\\|err\\| | PASS |", "|---|---|---|"]
    for b, d in R["check3"]["blocks"].items():
        me = "" if d["max_err"] is None else f"{d['max_err']:.4f}"
        L.append(f"| {b} | {me} | {'PASS' if d['passed'] else 'FAIL'} |")
    L += ["", "### Full JSON", "", "```json", json.dumps(R, indent=2), "```", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
