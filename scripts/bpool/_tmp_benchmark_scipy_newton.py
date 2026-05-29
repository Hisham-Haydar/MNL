"""Test scipy Newton-class methods on RURO singles male 766 HH.

Hypothesis: L-BFGS-B and trust-constr (BFGS approx) both get trapped at
LL=-9737 plateau. CONOPT (analytical Hessian) reaches LL=-2501. Question:
does scipy with FINITE-DIFFERENCE Hessian (real curvature info, no
approximation) also reach the CONOPT basin, or does it trap too?

Tests two scipy methods in order:
  1. trust-exact — Newton with trust region, designed for small problems
  2. Newton-CG — Newton with conjugate-gradient inner solver

Both use hess='3-point' (central FD) which is expensive but accurate.

Warm start from theta_star (same seed as harness so directly comparable
to L-BFGS-B/trust-constr/CONOPT results).

Read-only on data; produces no commitable artifacts.
"""
from __future__ import annotations
import sys
import time
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "enhanced"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import scipy.optimize  # noqa: E402
import estimation_spec_parser as sp  # noqa: E402
import recovery_test as rt  # noqa: E402

SPEC = Path(__file__).resolve().parent / "specs" / "estimation_spec_bpool_p3a_v1.yaml"
STEM = "fr_p3a_bpool_engine_ready"
SEED = 20260527

print("=" * 78, flush=True)
print("scipy Newton-class benchmark vs CONOPT — singles male 2016 (766 HH)", flush=True)
print("=" * 78, flush=True)

spec = sp.parse_specification(SPEC)
rng = np.random.default_rng(SEED)
print("loading slice ...", flush=True)
sl, meta, _ = rt.load_slice("fr", "singles", [2016], 999999, STEM, sex="male")
data = rt.precompute("singles", sl, meta, sex="male")
theta_star = rt.generate_theta_star(spec, rng)
print(f"  n_groups={data.n_groups} n_obs={data.n_obs} n_params={len(theta_star)}", flush=True)

# Synthesize choices (mirror harness)
llf = rt.ll_for("singles")
gf = rt.grad_for("singles")
comp = llf(theta_star, data, spec, return_components=True)
data.actual_choice = rt.draw_synthetic_choice(comp["V"], data.group_starts, data.group_ends, rng)
print(f"  synthetic chosen alts: {int(data.actual_choice.sum())} (= n_groups {data.n_groups})", flush=True)

bounds = spec.get_bounds_tuple()
lo = np.array([b[0] if b and b[0] is not None else -np.inf for b in bounds])
hi = np.array([b[1] if b and b[1] is not None else np.inf for b in bounds])

# Reference values
CONOPT_LL = -2501.7655
LBFGSB_LL = -9737.3173
print(f"\nReference: CONOPT LL = {CONOPT_LL}, L-BFGS-B trapped LL = {LBFGSB_LL}")
print(f"Goal: scipy Newton-class to reach CONOPT basin (LL <= -3000 indicative)\n", flush=True)


def run_one(name, kwargs):
    print(f"\n--- {name} ---", flush=True)
    t0 = time.time()
    pnames = spec.all_param_names
    state = {"k": 0}
    def cb(xk, state=state, t0=t0):
        state["k"] += 1
        f = llf(xk, data, spec)
        g = gf(xk, data, spec)
        gmax = float(np.max(np.abs(g)))
        # Less frequent printing since each iter is expensive (FD Hessian)
        if state["k"] <= 5 or state["k"] % 5 == 0:
            print(f"    iter {state['k']:3d}  negLL={f:.4f}  |g|max={gmax:.3e}  {time.time()-t0:.0f}s",
                  flush=True)
    try:
        res = scipy.optimize.minimize(
            lambda th: llf(th, data, spec),
            theta_star.copy(),
            jac=lambda th: gf(th, data, spec),
            callback=cb,
            **kwargs,
        )
        wall = time.time() - t0
        ll = float(-res.fun)
        gap_to_conopt = abs(ll - CONOPT_LL)
        gap_to_lbfgsb = abs(ll - LBFGSB_LL)
        which = "CONOPT basin" if gap_to_conopt < gap_to_lbfgsb else "trapped (L-BFGS-B basin)"
        print(f"  RESULT: nit={res.nit}  LL={ll:.4f}  success={res.success}  wall={wall:.1f}s  msg={res.message}",
              flush=True)
        print(f"  -> {which}  (gap to CONOPT: {gap_to_conopt:.2f}, gap to L-BFGS-B trapped: {gap_to_lbfgsb:.2f})",
              flush=True)
        return {"name": name, "wall_s": wall, "nit": int(res.nit), "ll": ll,
                "success": bool(res.success), "msg": str(res.message),
                "result": which}
    except Exception as exc:
        wall = time.time() - t0
        print(f"  FAILED: {type(exc).__name__}: {exc}", flush=True)
        return {"name": name, "wall_s": wall, "error": f"{type(exc).__name__}: {exc}"}


results = []

# Test 1: trust-exact with FD Hessian (UNBOUNDED — trust-exact does not support bounds)
# trust-exact: small-problem trust-region Newton with EXACT subproblem solve.
# Doesn't accept bounds, so we'd need to either:
#   - go unbounded and hope no parameter wanders off-bounds (risky)
#   - use trust-ncg which is similar but accepts approximate Newton too
# For a one-off benchmark let's run unconstrained and report.
results.append(run_one("trust-exact (FD Hessian, unbounded)", {
    "method": "trust-exact",
    "hess": "3-point",
    "options": {"maxiter": 100, "gtol": 1e-6}
}))

# Test 2: trust-ncg with FD Hessian (also unbounded for trust-ncg)
results.append(run_one("trust-ncg (FD Hessian, unbounded)", {
    "method": "trust-ncg",
    "hess": "3-point",
    "options": {"maxiter": 100, "xtol": 1e-6}
}))

# Test 3: Newton-CG with FD Hessian (unbounded only)
results.append(run_one("Newton-CG (FD Hessian, unbounded)", {
    "method": "Newton-CG",
    "hess": "3-point",
    "options": {"maxiter": 100, "xtol": 1e-6}
}))

# Test 4: trust-constr with hess='3-point' (BOUNDED — useful comparison since trust-constr supports bounds AND can use FD Hessian)
results.append(run_one("trust-constr (FD Hessian via 3-point, bounded)", {
    "method": "trust-constr",
    "hess": "3-point",
    "bounds": list(bounds),
    "options": {"maxiter": 100, "gtol": 1e-6, "xtol": 1e-6, "verbose": 0}
}))

print("\n" + "=" * 78, flush=True)
print("SUMMARY", flush=True)
print("=" * 78, flush=True)
for r in results:
    if "error" in r:
        print(f"  {r['name']:60s} ERROR: {r['error']}", flush=True)
    else:
        ll = r['ll']
        which = r['result']
        print(f"  {r['name']:60s} nit={r['nit']:4d}  LL={ll:>12.4f}  wall={r['wall_s']:>6.1f}s  -> {which}",
              flush=True)
