"""
Step 4 — deliverable 3: LR pooling test for beta_E and beta_h_pt2 (male vs female).

The baseline (estimation_spec_joint_pooled_v1_bll0_tlmpin) SHARES beta_E and
beta_h_pt2 across all four legs (singles-male, singles-female, couples-male,
couples-female). The 901 gate's Check 6 flagged that beta_E lands outside the
group-specific range under forced sharing — motivating a formal test of pooling.

This runs, for EACH of {beta_E, beta_h_pt2} independently:
  - RESTRICTED  = baseline (shared coef), warm-started from the baseline MLE.
  - RELAXED     = the coef split male/female (per the user's chosen relaxation:
                  male legs = singles-male + couples-male; female legs =
                  singles-female + couples-female). Implemented via the builders'
                  gender_split= hook (coef -> coef_m / coef_f). df = 1.
  - LR statistic = 2*(LL_relaxed - LL_restricted) ~ chi2(1); report p-value.

DECISION: if the test REJECTS pooling (p < 0.05) for a param, that param should
be relaxed to gender-specific in the baseline (one increment, written reason)
and the baseline re-estimated before it is final. This script REPORTS the
decision; it does NOT mutate the certified spec (that's a deliberate follow-up).

Backend: JAX, constrained two-stage optimizer (same as the baseline). Warm-start
the relaxed fit from the baseline MLE with the split coef seeded at the shared
value (so the relaxed nests the restricted).

USAGE:
  python step4_lr_pooling_test.py \
    --spec specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml \
    --theta-hat specs/theta_hat_realdata_901_v1.csv \
    --couples-stem fr_p3a_bpool_engine_ready --n-hh 0 \
    --report ../../docs/France_case/P3a/execution_logs/Bpool/RURO_realdata_lr_pooling_901_v1.md
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2

_script_dir = Path(__file__).resolve().parent
_enhanced_dir = _script_dir.parent / "enhanced"
sys.path.insert(0, str(_enhanced_dir))
sys.path.insert(0, str(_script_dir))

import estimation_spec_parser as sp          # noqa: E402
import joint_recovery_test as jrt            # noqa: E402

import jax                                    # noqa: E402
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp                       # noqa: E402

from jax_ll_probe import build_jax_singles_ll, build_jax_couples_ll  # noqa: E402


def _build_joint(spec, dsm, dsf, dco, gender_split=None):
    f_sm, _ = build_jax_singles_ll(dsm, spec, is_male=True, gender_split=gender_split)
    f_sf, _ = build_jax_singles_ll(dsf, spec, is_male=False, gender_split=gender_split)
    f_co, _ = build_jax_couples_ll(dco, spec, gender_split=gender_split)

    def joint(theta):
        return f_sm(theta) + f_sf(theta) + f_co(theta)
    return jax.jit(joint)


def _relax_spec(spec, base_coef):
    """Return a deep-copied spec where `base_coef` is split into base_coef_m /
    base_coef_f: remove the shared name from all_param_names/bounds/initial,
    insert the two gendered names (same bounds, seeded later). The builders'
    gender_split hook reads coef_m / coef_f for the male / female legs."""
    s = copy.deepcopy(spec)
    names = list(s.all_param_names)
    if base_coef not in names:
        raise SystemExit(f"{base_coef} not in spec params")
    i = names.index(base_coef)
    m, f = base_coef + "_m", base_coef + "_f"
    names[i:i + 1] = [m, f]
    s.all_param_names = names
    # bounds: copy the shared coef's bounds to both
    bnd = s.bounds.get(base_coef, (None, None))
    s.bounds.pop(base_coef, None)
    s.bounds[m] = bnd
    s.bounds[f] = bnd
    # initial_values: copy
    iv = s.initial_values.get(base_coef, 0.0)
    if base_coef in s.initial_values:
        del s.initial_values[base_coef]
    s.initial_values[m] = iv
    s.initial_values[f] = iv
    return s, m, f


def _bounds_list(spec):
    out = []
    for n in spec.all_param_names:
        lo, hi = spec.bounds.get(n, (None, None))
        out.append((None if lo is None else float(lo),
                    None if hi is None else float(hi)))
    return out


def _optimize(joint, theta0, bnds, gtol, maxiter, label):
    jval = jax.jit(joint)
    jgrad = jax.jit(jax.grad(joint))

    def fun(x):
        return float(jval(jnp.asarray(x)))

    def grad(x):
        return np.asarray(jgrad(jnp.asarray(x)), dtype=np.float64)

    _ = fun(theta0); _ = grad(theta0)
    t0 = time.time()
    _it = {"k": 0}
    def cb(xk):
        _it["k"] += 1
        if _it["k"] % 25 == 0 or _it["k"] == 1:
            print(f"      [{label} iter {_it['k']:4d}] negLL={fun(xk):.4f} "
                  f"max|g|={float(np.max(np.abs(grad(xk)))):.3e} "
                  f"[{time.time()-t0:.0f}s]", flush=True)
    res = minimize(fun, theta0, jac=grad, method="L-BFGS-B", bounds=bnds,
                   callback=cb, options={"maxiter": maxiter, "gtol": gtol,
                                         "ftol": 1e-15, "maxls": 60})
    th = res.x
    ll = fun(th)
    # optimistix polish, projected in-bounds
    import optimistix as optx
    sol = optx.minimise(lambda y, _a: joint(y),
                        optx.BFGS(rtol=gtol, atol=gtol),
                        jnp.asarray(th), max_steps=maxiter, throw=False)
    # np.asarray of a JAX array is read-only; copy before projecting in-bounds.
    th_ox = np.array(sol.value, dtype=np.float64, copy=True)
    for i, (lo, hi) in enumerate(bnds):
        if lo is not None:
            th_ox[i] = max(th_ox[i], lo)
        if hi is not None:
            th_ox[i] = min(th_ox[i], hi)
    ll_ox = fun(th_ox)
    if np.isfinite(ll_ox) and ll_ox < ll:
        th, ll = th_ox, ll_ox
    g = float(np.max(np.abs(grad(th))))
    print(f"    [{label}] negLL={ll:.6f} max|grad|={g:.3e} [{time.time()-t0:.0f}s]",
          flush=True)
    return th, ll, g


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", type=Path,
                    default=_script_dir / "specs" / "estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml")
    ap.add_argument("--theta-hat", type=Path,
                    default=_script_dir / "specs" / "theta_hat_realdata_901_v1.csv",
                    help="Baseline MLE CSV (parameter,value[,...]) — warm start.")
    ap.add_argument("--engine-ready-stem", default="fr_p3a_bpool_engine_ready")
    ap.add_argument("--couples-stem", default="fr_p3a_bpool_engine_ready")
    ap.add_argument("--years", default="2015,2016,2017")
    ap.add_argument("--n-hh", type=int, default=0)
    ap.add_argument("--params", default="beta_E,beta_h_pt2",
                    help="Comma list of base coefs to test (each split m/f).")
    ap.add_argument("--gtol", type=float, default=1e-6)
    ap.add_argument("--maxiter", type=int, default=3000)
    ap.add_argument("--report", type=Path, default=None)
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    print(f"JAX {jax.__version__}  backend={jax.default_backend()}")
    spec = sp.parse_specification(args.spec)
    pnames = spec.all_param_names
    years = [] if args.years.strip().lower() == "all" else [int(y) for y in args.years.split(",")]
    test_params = [p.strip() for p in args.params.split(",") if p.strip()]
    print(f"spec: {spec.name} ({len(pnames)} params)  testing: {test_params}")

    data_sm, data_sf, data_cou = jrt.build_data_objects(
        args.engine_ready_stem, years, args.n_hh, couples_stem=args.couples_stem)
    cou_alts = data_cou.n_obs // data_cou.n_groups
    print(f"loaded sm={data_sm.n_groups} sf={data_sf.n_groups} cou={data_cou.n_groups} "
          f"(cou alts={cou_alts})")
    if cou_alts != 901:
        raise SystemExit(f"STOP: couples alts/HH={cou_alts}, expected 901.")

    # ---- RESTRICTED: baseline at the supplied MLE; re-polish to be safe ----
    theta_hat = np.asarray(jrt.load_theta_star_from_csv(args.theta_hat, spec),
                           dtype=np.float64)
    bnds = _bounds_list(spec)
    for i, (lo, hi) in enumerate(bnds):
        if lo is not None:
            theta_hat[i] = max(theta_hat[i], lo + 1e-9)
        if hi is not None:
            theta_hat[i] = min(theta_hat[i], hi - 1e-9)
    joint_r = _build_joint(spec, data_sm, data_sf, data_cou)
    print("\n--- RESTRICTED (shared) baseline ---")
    th_r, ll_r, g_r = _optimize(joint_r, theta_hat, bnds, args.gtol, args.maxiter,
                                "restricted")
    print(f"  restricted negLL={ll_r:.6f}")

    R = {"spec": spec.name, "couples_alts": int(cou_alts),
         "restricted_negLL": float(ll_r), "restricted_maxgrad": float(g_r),
         "tests": []}

    # baseline name->value for seeding the split
    base_map = dict(zip(pnames, th_r))

    for bc in test_params:
        print(f"\n=== LR test: relax {bc} -> {bc}_m / {bc}_f ===")
        s_rel, mname, fname = _relax_spec(spec, bc)
        rel_names = s_rel.all_param_names
        bnds_rel = _bounds_list(s_rel)
        joint_x = _build_joint(s_rel, data_sm, data_sf, data_cou,
                               gender_split={bc})
        # warm start: baseline values, with split coef seeded at the shared value
        shared_val = base_map[bc]
        theta0 = np.array([base_map.get(n, shared_val if n in (mname, fname)
                                        else s_rel.initial_values.get(n, 0.0))
                           for n in rel_names], dtype=np.float64)
        for i, (lo, hi) in enumerate(bnds_rel):
            if lo is not None:
                theta0[i] = max(theta0[i], lo + 1e-9)
            if hi is not None:
                theta0[i] = min(theta0[i], hi - 1e-9)
        # sanity: at the seed, relaxed negLL must equal restricted negLL (nested)
        ll_seed = float(jax.jit(joint_x)(jnp.asarray(theta0)))
        nest_gap = abs(ll_seed - ll_r)
        print(f"  nesting check: relaxed negLL at seed={ll_seed:.6f} "
              f"(restricted={ll_r:.6f}, |Δ|={nest_gap:.2e}; expect ~0)")
        th_x, ll_x, g_x = _optimize(joint_x, theta0, bnds_rel, args.gtol,
                                    args.maxiter, f"relax:{bc}")
        lr = 2.0 * (ll_r - ll_x)  # ll are NEG-LL; relaxed LL >= restricted LL
        # (ll_r - ll_x) since negLL: restricted negLL >= relaxed negLL -> lr >= 0
        pval = float(chi2.sf(max(lr, 0.0), df=1))
        mval = float(th_x[rel_names.index(mname)])
        fval = float(th_x[rel_names.index(fname)])
        reject = pval < 0.05
        print(f"  {bc}_m={mval:.5f}  {bc}_f={fval:.5f}  (shared was {shared_val:.5f})")
        print(f"  LR={lr:.4f}  df=1  p={pval:.4g}  -> "
              f"{'REJECT pooling (relax to gender-specific)' if reject else 'FAIL TO REJECT (pooling OK)'}")
        R["tests"].append({
            "param": bc, "shared_value": float(shared_val),
            "relaxed_negLL": float(ll_x), "relaxed_maxgrad": float(g_x),
            "nesting_gap_at_seed": float(nest_gap),
            "estimate_m": mval, "estimate_f": fval,
            "LR_stat": float(lr), "df": 1, "p_value": pval,
            "reject_pooling": bool(reject),
            "decision": ("relax to gender-specific" if reject else "keep shared"),
        })

    print("\n" + "=" * 72)
    print("LR POOLING TEST — SUMMARY")
    for t in R["tests"]:
        print(f"  {t['param']:<12} LR={t['LR_stat']:8.3f} p={t['p_value']:.4g} "
              f"-> {t['decision']}")
    print("=" * 72)

    if args.report:
        _write_report(args.report, R)
        print(f"\n[report] {args.report}")


def _write_report(path, R):
    L = [f"# Step 4 — LR pooling test (male vs female): {R['spec']}", "",
         "> Deliverable 3. Tests whether beta_E and beta_h_pt2 can be pooled "
         "across male/female legs, or must be gender-specific. RESTRICTED = "
         "baseline (shared); RELAXED = coef split male/female (male legs = "
         "singles-male + couples-male; female legs = singles-female + "
         "couples-female), df=1. LR = 2(LL_relaxed - LL_restricted) ~ chi2(1).",
         "",
         f"**Restricted (baseline) negLL** = {R['restricted_negLL']:.6f} "
         f"(max|grad|={R['restricted_maxgrad']:.2e})  **Couples alts** = {R['couples_alts']}",
         "", "| Param | shared | est_m | est_f | LR | p (chi2,df=1) | decision |",
         "|---|---|---|---|---|---|---|"]
    for t in R["tests"]:
        L.append(f"| {t['param']} | {t['shared_value']:.4f} | {t['estimate_m']:.4f} | "
                 f"{t['estimate_f']:.4f} | {t['LR_stat']:.3f} | {t['p_value']:.4g} | "
                 f"**{t['decision']}** |")
    L += ["", "### Notes", "",
          "- Nesting check (relaxed negLL at the shared-value seed == restricted "
          "negLL) is reported per param in the JSON (`nesting_gap_at_seed`); it "
          "must be ~0 for the LR statistic to be valid.",
          "- A REJECT means the baseline should relax that param to gender-"
          "specific (one increment, written reason) and be re-estimated before "
          "it is final. This script reports the decision; it does not mutate the "
          "certified spec.",
          "", "## Full JSON", "", "```json", json.dumps(R, indent=2), "```", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
