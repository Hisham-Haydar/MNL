r"""Test L-BFGS-B multistart on RURO singles male 766 HH.

Hypothesis: scipy gradient-based solvers from theta* converge to a local maximum
at LL ~= -9737, but the LL has a higher local max at LL ~= -2501 that CONOPT
reaches. Question: does L-BFGS-B from sufficiently varied random starts find the
CONOPT basin at least once?

Method: 20 random starts uniform within bounds. Each runs L-BFGS-B to
convergence. Record best (lowest negLL) and distribution of all results.

Decision rule:
  - If best LL ≈ -2501: multistart works; free L-BFGS-B + multistart is the
    package strategy.
  - If best LL ≈ -9737 (everything traps in the same basin): random starts
    aren't enough; need smarter strategy (warm-start from singles est, or
    CONOPT-equivalent solver).
  - If best LL is something else (e.g. -5000): the LL has more than two basins
    and we've just discovered a third. Worth understanding.

~2-3 minutes wall time per L-BFGS-B run, 20 starts = ~40-60 min total.
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
N_STARTS = 20

print("=" * 78, flush=True)
print(f"L-BFGS-B multistart benchmark — singles male 2016 (766 HH), {N_STARTS} starts", flush=True)
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

bounds_tuple = spec.get_bounds_tuple()
bounds_list = [(b[0] if b and b[0] is not None else -np.inf,
                b[1] if b and b[1] is not None else np.inf) for b in bounds_tuple]
lo = np.array([b[0] for b in bounds_list])
hi = np.array([b[1] for b in bounds_list])
# Clip infinite bounds to spec range for random sampling
sample_lo = np.where(np.isfinite(lo), lo, -10.0)
sample_hi = np.where(np.isfinite(hi), hi, 10.0)

# Reference values
CONOPT_LL = -2501.7655
LBFGSB_TRAPPED_LL = -9737.3173
THETA_STAR_LL = float(llf(theta_star, data, spec)) * -1.0  # llf returns negLL
print(f"\nReference: CONOPT LL = {CONOPT_LL}, L-BFGS-B-trapped LL = {LBFGSB_TRAPPED_LL}")
print(f"LL at theta_star itself = {THETA_STAR_LL:.4f}")
print(f"Bounds: {N_STARTS} starts uniform within finite bounds (infinite bounds clipped to [-10,+10])\n", flush=True)

# Build start vectors
start_rng = np.random.default_rng(SEED + 100)
# Start 0 = theta_star (baseline)
# Start 1 = spec initial vector (matches the "cold" start the harness uses)
# Starts 2..N_STARTS-1 = uniform random within bounds
starts = [("theta_star", theta_star)]
starts.append(("spec_init", spec.get_initial_vector().astype(float)))
for i in range(2, N_STARTS):
    x0 = start_rng.uniform(sample_lo, sample_hi)
    starts.append((f"random_{i:02d}", x0))

results = []
overall_t0 = time.time()
for label, x0 in starts:
    print(f"--- start {label} (LL@start={llf(x0, data, spec):.2f}) ---", flush=True)
    t0 = time.time()
    try:
        res = scipy.optimize.minimize(
            lambda th: llf(th, data, spec),
            x0,
            jac=lambda th: gf(th, data, spec),
            method="L-BFGS-B",
            bounds=bounds_list,
            options={"maxiter": 1000, "ftol": 1e-10, "gtol": 1e-6},
        )
        wall = time.time() - t0
        ll = float(-res.fun)
        results.append({
            "start": label, "wall_s": round(wall, 1), "ll": round(ll, 4),
            "nit": int(res.nit), "success": bool(res.success),
            "msg": str(res.message)[:60],
        })
        print(f"  -> nit={res.nit}  LL={ll:.4f}  wall={wall:.1f}s  success={res.success}", flush=True)
    except Exception as exc:
        wall = time.time() - t0
        results.append({"start": label, "wall_s": round(wall, 1), "ll": None,
                        "error": f"{type(exc).__name__}: {str(exc)[:80]}"})
        print(f"  -> FAILED: {type(exc).__name__}", flush=True)

# Summary
total_wall = time.time() - overall_t0
print(f"\n" + "=" * 78, flush=True)
print(f"SUMMARY ({len(results)} starts, total wall {total_wall:.1f}s)", flush=True)
print("=" * 78, flush=True)

valid = [r for r in results if r.get("ll") is not None]
ll_vals = sorted([r["ll"] for r in valid])
print(f"\nLL distribution across {len(valid)} converged starts:")
print(f"  best (lowest negLL, highest LL): {ll_vals[0]:.4f}")
print(f"  worst (highest negLL):           {ll_vals[-1]:.4f}")
print(f"  median:                          {ll_vals[len(ll_vals)//2]:.4f}")
print(f"  unique basins (LL clustered within 0.5 negLL):")
clusters = []
for ll in ll_vals:
    placed = False
    for c in clusters:
        if abs(c[0] - ll) < 0.5:
            c.append(ll)
            placed = True
            break
    if not placed:
        clusters.append([ll])
for cl in sorted(clusters, key=lambda c: c[0]):
    print(f"    LL ≈ {np.median(cl):.4f}  ({len(cl)} starts)")

print(f"\nReference comparison:")
print(f"  CONOPT optimum: LL = {CONOPT_LL}")
print(f"  L-BFGS-B trapped (from theta*): LL = {LBFGSB_TRAPPED_LL}")
print(f"  Best multistart LL: {ll_vals[0]:.4f}")

if ll_vals[0] < CONOPT_LL + 1.0:
    print(f"  -> MULTISTART REACHES CONOPT BASIN (or better)")
elif ll_vals[0] < LBFGSB_TRAPPED_LL - 100:
    print(f"  -> Multistart finds a basin BETTER than theta_star trap but worse than CONOPT (third basin?)")
else:
    print(f"  -> Multistart traps at same basin as L-BFGS-B from theta* (gap to CONOPT: {abs(ll_vals[0] - CONOPT_LL):.2f})")

print(f"\nPer-start results (sorted by LL):")
print(f"  {'start':14s} {'wall_s':>8s} {'nit':>5s} {'LL':>12s}")
print(f"  {'-'*14} {'-'*8} {'-'*5} {'-'*12}")
for r in sorted(valid, key=lambda x: x["ll"]):
    print(f"  {r['start']:14s} {r['wall_s']:>8.1f} {r['nit']:>5d} {r['ll']:>12.4f}")
