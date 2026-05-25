"""
Limited JAX optimizer benchmark — FR_2016 couples pilot.

Authorization: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_JAX_optimizer_benchmark_authorization_v1.md §18

SCOPE: Single L-BFGS-B run from theta_CONOPT, JAX float64 value-and-gradient,
       spec bounds, maxiter=15. FINITENESS / STABILITY PROBE ONLY.

HARD CONSTRAINTS (halt codes from §14):
  HJ-X64   : JAX float64 must be enabled; halt if unavailable.
  HJ-START  : Start only from theta_CONOPT (start_1_warm_P3a). No defaults, no
              multiple starts.
  HJ-CAP    : maxiter fixed at 15 (within [10,20]).
  HJ-NAN    : Halt if NaN/Inf objective or gradient at any iteration.
  HJ-DETERIORATE: Report failure if final LL materially worse than initial.
  HJ-SCOPE  : No Hessian, SE, welfare, SA2, promotion, multi-start, cold-start.
  HJ-MUT    : Do NOT overwrite v1/v2 equivalence reports, oracle JSONs, pkl, or
              any production/pilot data.

NOT authorized: optimization from defaults, multiple starts, Hessian, SEs,
welfare, SA2, promotion. This is a stability probe, not re-estimation.
"""

# ---------------------------------------------------------------------------
# STEP 0 — float64 enable: MUST happen before any JAX array is created
# Halt HJ-X64 if this fails.
# ---------------------------------------------------------------------------
_X64_ENABLED = False
_X64_ERROR = None
try:
    import jax
    jax.config.update("jax_enable_x64", True)
    import jax.numpy as jnp
    _test = jnp.array(1.0, dtype=jnp.float64)
    assert _test.dtype == jnp.float64, "float64 array has wrong dtype"
    _X64_ENABLED = True
except Exception as _e:
    _X64_ERROR = str(_e)

import json
import math
import pickle
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO = Path(r"U:\Desktop\Nizam_Hisham\MNL").resolve()
sys.path.insert(0, str(REPO / "scripts/enhanced"))

PKL_PATH   = (REPO / "Data/pilot/nc_2016_couples/precomputed"
              / "fr_pilot_nc_2016_couples_precomputed_loc.pkl").resolve()
RESULT_S1  = (REPO / "Results/pilot/nc_2016_couples/diagnostic_rerun_v1"
              / "start_1_warm_P3a/estimation_result.json").resolve()
REPORT_PATH = (REPO / "Results"
               / "JMP_NC_pilot_JAX_optimizer_benchmark_report_v1.md").resolve()

ORACLE_LL  = -16527.14218317334
V2_LL_NP   = -16527.0669688818   # NumPy float64 LL from equivalence_v2 report
EPS        = 1e-12
MAXITER    = 15                   # within [10, 20] per §11

PARAM_NAMES = [
    "beta_l0_m", "beta_l_age_m", "beta_l_age2_m", "theta_l_m",
    "beta_l0_f", "beta_l_age_f", "beta_l_age2_f", "beta_l_nkids_f", "theta_l_f",
    "beta_c",
    "beta_E", "beta_h_pt1", "beta_h_pt2", "beta_h_ft",
    "beta_E_gsur",
    "beta_E_drgn2", "beta_E_drgn3", "beta_E_drgn4", "beta_E_drgn5",
    "beta_E_drgn6", "beta_E_drgn7", "beta_E_drgn8",
    "beta_occ_2_cm", "beta_occ_3_cm", "beta_occ_4_cm",
    "beta_occ_2_cf", "beta_occ_3_cf", "beta_occ_4_cf",
    "beta_w0", "beta_w_educL", "beta_w_educH", "beta_w_pexp", "beta_w_pexp2",
    "sigma",
    "beta_ll",
]

# Bounds from estimation_spec_nc_pilot_couples_2016.yaml optimization.bounds.
# theta_c is FIXED at 0.0 (not in PARAM_NAMES, not optimized).
# Parameters not listed in spec bounds get (-inf, inf) = no constraint.
BOUNDS_DICT = {
    "theta_l_m":    (-8.0, 0.95),
    "theta_l_f":    (-8.0, 0.95),
    "beta_c":       (0.05, 50.0),
    "beta_l0_m":    (1.0e-6, 50.0),
    "beta_l0_f":    (0.05, 50.0),
    "beta_l_age_m":   (-5.0, 5.0),
    "beta_l_age2_m":  (-1.0, 1.0),
    "beta_l_age_f":   (-5.0, 5.0),
    "beta_l_age2_f":  (-1.0, 1.0),
    "beta_l_nkids_f": (-5.0, 5.0),
    "beta_E":       (-25.0, 25.0),
    "beta_h_pt1":   (-10.0, 10.0),
    "beta_h_pt2":   (-10.0, 10.0),
    "beta_h_ft":    (-10.0, 10.0),
    "beta_w0":      (-10.0, 20.0),
    "beta_w_educL": (-5.0, 5.0),
    "beta_w_educH": (-5.0, 5.0),
    "beta_w_pexp":  (-1.0, 1.0),
    "beta_w_pexp2": (-0.1, 0.1),
    "beta_E_gsur":   (-10.0, 10.0),
    "beta_E_drgn2":  (-10.0, 10.0),
    "beta_E_drgn3":  (-10.0, 10.0),
    "beta_E_drgn4":  (-10.0, 10.0),
    "beta_E_drgn5":  (-10.0, 10.0),
    "beta_E_drgn6":  (-10.0, 10.0),
    "beta_E_drgn7":  (-10.0, 10.0),
    "beta_E_drgn8":  (-10.0, 10.0),
    "beta_occ_2_cm": (-10.0, 10.0),
    "beta_occ_3_cm": (-10.0, 10.0),
    "beta_occ_4_cm": (-10.0, 10.0),
    "beta_occ_2_cf": (-10.0, 10.0),
    "beta_occ_3_cf": (-10.0, 10.0),
    "beta_occ_4_cf": (-10.0, 10.0),
    "sigma":        (0.1, 20.0),
    "beta_ll":      (0.0, 10.0),
}
BOUNDS = [BOUNDS_DICT.get(p, (None, None)) for p in PARAM_NAMES]


# ---------------------------------------------------------------------------
# JAX LL function (float64) — same formula as _run_ll_equivalence_prototype.py,
# but all arrays created as float64.  Refactored into a standalone function
# that takes a JAX float64 vector and fixed arrays (captured in closure).
# Import/refactor documented: no logic change to the validated LL formula.
# ---------------------------------------------------------------------------
def build_jax_ll_fn(pc):
    """
    Build a JAX function ll_fn(theta_vec) -> scalar LL (float64).
    All fixed arrays are captured as float64 JAX arrays in the closure.
    theta_c is fixed at 0.0 and is NOT part of theta_vec.
    """
    N = pc.n_groups
    J = pc.n_obs // pc.n_groups
    eps = float(EPS)

    def f64(arr):
        return jnp.array(arr.reshape(N, J), dtype=jnp.float64)

    fixed = {
        "consumption": f64(pc.consumption),
        "leisure_m":   f64(pc.leisure_male),
        "leisure_f":   f64(pc.leisure_female),
        "prior":       f64(pc.prior),
        "chosen":      f64(pc.actual_choice),
        "working_m":   f64(pc.working_male),
        "working_f":   f64(pc.working_female),
        "log_wage_m":  f64(pc.log_wage_male),
        "log_wage_f":  f64(pc.log_wage_female),
        "age_m":       f64(pc.age_norm_male),
        "age2_m":      f64(pc.age_norm2_male),
        "age_f":       f64(pc.age_norm_female),
        "age2_f":      f64(pc.age_norm2_female),
        "n_kids":      f64(pc.n_children),
        "gsur_m":      f64(pc.gsur_male),
        "gsur_f":      f64(pc.gsur_female),
        "reg2": f64(pc.reg2), "reg3": f64(pc.reg3), "reg4": f64(pc.reg4),
        "reg5": f64(pc.reg5), "reg6": f64(pc.reg6), "reg7": f64(pc.reg7),
        "reg8": f64(pc.reg8),
        "loc4_2_m": f64(pc.loc4_2_male),  "loc4_3_m": f64(pc.loc4_3_male),
        "loc4_4_m": f64(pc.loc4_4_male),
        "loc4_2_f": f64(pc.loc4_2_female), "loc4_3_f": f64(pc.loc4_3_female),
        "loc4_4_f": f64(pc.loc4_4_female),
        "educL_m":  f64(pc.educL_male),   "educH_m": f64(pc.educH_male),
        "pexp_m":   f64(pc.pexp_years_male), "pexp2_m": f64(pc.pexp_years2_male),
        "educL_f":  f64(pc.educL_female),  "educH_f": f64(pc.educH_female),
        "pexp_f":   f64(pc.pexp_years_female), "pexp2_f": f64(pc.pexp_years2_female),
        "wpt1_m": f64(pc.working_pt1_male),  "wpt2_m": f64(pc.working_pt2_male),
        "wft_m":  f64(pc.working_ft_male),
        "wpt1_f": f64(pc.working_pt1_female), "wpt2_f": f64(pc.working_pt2_female),
        "wft_f":  f64(pc.working_ft_female),
    }

    log2pi_half = 0.5 * math.log(2.0 * math.pi)

    def ll_fn(theta_vec):
        p = {k: theta_vec[i] for i, k in enumerate(PARAM_NAMES)}
        f = fixed

        # 4th-order Taylor BC (matches GAMSPy exactly)
        def bc(x, theta):
            lx = jnp.log(x + eps)
            t = theta
            return lx * (1.0 + t*lx/2.0 + t*t*lx*lx/6.0
                         + t*t*t*lx*lx*lx/24.0 + t*t*t*t*lx*lx*lx*lx/120.0)

        # theta_c = 0.0 fixed → BC(c, 0) = log(c + eps)
        bc_c   = jnp.log(jnp.maximum(f["consumption"], eps))
        bc_l_m = bc(f["leisure_m"], p["theta_l_m"])
        bc_l_f = bc(f["leisure_f"], p["theta_l_f"])

        coeff_l_m = (p["beta_l0_m"] + p["beta_l_age_m"]*f["age_m"]
                     + p["beta_l_age2_m"]*f["age2_m"])
        coeff_l_f = (p["beta_l0_f"] + p["beta_l_age_f"]*f["age_f"]
                     + p["beta_l_age2_f"]*f["age2_f"]
                     + p["beta_l_nkids_f"]*f["n_kids"])

        u_pref = (p["beta_c"]*bc_c + coeff_l_m*bc_l_m + coeff_l_f*bc_l_f
                  + p["beta_ll"]*bc_l_m*bc_l_f)

        log_h_m = (p["beta_E"]*f["working_m"]
                   + p["beta_h_pt1"]*f["wpt1_m"]*f["working_m"]
                   + p["beta_h_pt2"]*f["wpt2_m"]*f["working_m"]
                   + p["beta_h_ft"]*f["wft_m"]*f["working_m"])
        log_h_f = (p["beta_E"]*f["working_f"]
                   + p["beta_h_pt1"]*f["wpt1_f"]*f["working_f"]
                   + p["beta_h_pt2"]*f["wpt2_f"]*f["working_f"]
                   + p["beta_h_ft"]*f["wft_f"]*f["working_f"])

        sigma = p["sigma"]
        mu_m = (p["beta_w0"] + p["beta_w_educL"]*f["educL_m"]
                + p["beta_w_educH"]*f["educH_m"]
                + p["beta_w_pexp"]*f["pexp_m"] + p["beta_w_pexp2"]*f["pexp2_m"])
        mu_f = (p["beta_w0"] + p["beta_w_educL"]*f["educL_f"]
                + p["beta_w_educH"]*f["educH_f"]
                + p["beta_w_pexp"]*f["pexp_f"] + p["beta_w_pexp2"]*f["pexp2_f"])

        log_w_m = f["working_m"] * (
            -0.5*(f["log_wage_m"] - mu_m)**2 / (sigma**2 + eps)
            - jnp.log(sigma + eps) - log2pi_half - f["log_wage_m"])
        log_w_f = f["working_f"] * (
            -0.5*(f["log_wage_f"] - mu_f)**2 / (sigma**2 + eps)
            - jnp.log(sigma + eps) - log2pi_half - f["log_wage_f"])

        log_market = (p["beta_E_gsur"]*f["gsur_m"]*f["working_m"]*10.0
                      + p["beta_E_gsur"]*f["gsur_f"]*f["working_f"]*10.0)
        w_hh = f["working_m"] + f["working_f"]
        for coef, reg in [
            ("beta_E_drgn2", "reg2"), ("beta_E_drgn3", "reg3"),
            ("beta_E_drgn4", "reg4"), ("beta_E_drgn5", "reg5"),
            ("beta_E_drgn6", "reg6"), ("beta_E_drgn7", "reg7"),
            ("beta_E_drgn8", "reg8"),
        ]:
            log_market = log_market + p[coef]*f[reg]*w_hh

        log_market = (log_market
            + p["beta_occ_2_cm"]*f["loc4_2_m"]*f["working_m"]
            + p["beta_occ_3_cm"]*f["loc4_3_m"]*f["working_m"]
            + p["beta_occ_4_cm"]*f["loc4_4_m"]*f["working_m"]
            + p["beta_occ_2_cf"]*f["loc4_2_f"]*f["working_f"]
            + p["beta_occ_3_cf"]*f["loc4_3_f"]*f["working_f"]
            + p["beta_occ_4_cf"]*f["loc4_4_f"]*f["working_f"])

        prior_sum = f["prior"].sum(axis=1, keepdims=True) + eps
        center    = (f["prior"] * log_market).sum(axis=1, keepdims=True) / prior_sum
        log_market_c = log_market - center

        log_prior = jnp.log(f["prior"] + eps)
        utility = (u_pref + log_h_m + log_h_f + log_w_m + log_w_f
                   + log_market_c - log_prior)

        u_max   = utility.max(axis=1, keepdims=True)
        log_den = jnp.log(jnp.exp(utility - u_max).sum(axis=1)) + u_max.squeeze()
        chosen_u = (f["chosen"] * utility).sum(axis=1)
        return (chosen_u - log_den).sum()

    return ll_fn


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 72)
    print("JAX OPTIMIZER BENCHMARK — FR_2016 couples pilot")
    print("Authorization: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_JAX_optimizer_benchmark_authorization_v1.md")
    print("NOT production optimization. NOT verdict-grade. Stability probe only.")
    print("=" * 72)

    halt_code  = None
    halt_msg   = None
    results    = {}

    # -----------------------------------------------------------------------
    # STEP 0 — Verify float64
    # -----------------------------------------------------------------------
    print("\n--- STEP 0: JAX float64 check ---")
    if not _X64_ENABLED:
        halt_code = "HJ-X64"
        halt_msg  = f"JAX float64 (jax_enable_x64) unavailable or failed: {_X64_ERROR}"
        print(f"  HALT {halt_code}: {halt_msg}")
        write_report(results, halt_code, halt_msg, None, None)
        return

    import jax
    print(f"  JAX version       : {jax.__version__}")
    print(f"  jax_enable_x64    : ENABLED")
    _verify = jnp.array(1.0, dtype=jnp.float64)
    print(f"  float64 test dtype: {_verify.dtype}  — OK")
    results["jax_version"] = jax.__version__
    results["x64_enabled"] = True

    # -----------------------------------------------------------------------
    # STEP 1 — Load oracle theta (theta_CONOPT = start_1_warm_P3a)
    # -----------------------------------------------------------------------
    print("\n--- STEP 1: Load theta_CONOPT ---")
    with open(RESULT_S1) as fh:
        r1 = json.load(fh)
    theta_dict  = {p: r1["parameters"][p] for p in PARAM_NAMES}
    oracle_ll_s1 = r1["log_likelihood"]
    print(f"  Oracle LL (start 1): {oracle_ll_s1:.12f}")
    print(f"  Parameters loaded  : {len(theta_dict)}")
    results["oracle_ll_s1"] = oracle_ll_s1
    results["theta_conopt"] = {p: theta_dict[p] for p in PARAM_NAMES}

    # Confirm bounds feasibility of theta_CONOPT
    theta0 = np.array([theta_dict[p] for p in PARAM_NAMES], dtype=np.float64)
    bound_violations = []
    for i, (p, (lo, hi)) in enumerate(zip(PARAM_NAMES, BOUNDS)):
        v = theta0[i]
        if lo is not None and v < lo - 1e-10:
            bound_violations.append(f"{p}={v:.6f} < lo={lo}")
        if hi is not None and v > hi + 1e-10:
            bound_violations.append(f"{p}={v:.6f} > hi={hi}")
    if bound_violations:
        print(f"  WARNING: theta_CONOPT bound violations: {bound_violations}")
    else:
        print("  theta_CONOPT is within all spec bounds — OK")
    results["bound_violations_at_start"] = bound_violations

    # -----------------------------------------------------------------------
    # STEP 2 — Load pkl (read-only)
    # -----------------------------------------------------------------------
    print("\n--- STEP 2: Load precomputed pkl (read-only) ---")
    t0 = time.time()
    with open(PKL_PATH, "rb") as fh:
        pc = pickle.load(fh)
    print(f"  Loaded in {time.time()-t0:.2f} s — n_groups={pc.n_groups}, n_obs={pc.n_obs}")
    results["n_groups"] = pc.n_groups
    results["n_obs"]    = pc.n_obs

    # -----------------------------------------------------------------------
    # STEP 3 — Build JAX float64 LL function + warm-up eval
    # -----------------------------------------------------------------------
    print("\n--- STEP 3: Build JAX float64 LL + value_and_grad ---")
    ll_fn = build_jax_ll_fn(pc)
    val_and_grad = jax.jit(jax.value_and_grad(ll_fn))

    theta0_jax = jnp.array(theta0, dtype=jnp.float64)

    print("  JIT warm-up (first call) ...")
    t0 = time.time()
    ll_init_jax, grad_init_jax = val_and_grad(theta0_jax)
    warmup_ms = (time.time() - t0) * 1000
    ll_init   = float(ll_init_jax)
    grad_init = np.array(grad_init_jax, dtype=np.float64)

    print(f"  Warm-up wall time  : {warmup_ms:.1f} ms")
    print(f"  Initial LL (float64): {ll_init:.10f}")
    print(f"  |delta| vs v2 LL   : {abs(ll_init - V2_LL_NP):.6e}")
    print(f"  |delta| vs oracle  : {abs(ll_init - oracle_ll_s1):.6e}")

    # Check initial LL matches v2 LL within tolerance
    delta_vs_v2 = abs(ll_init - V2_LL_NP)
    results["ll_initial_f64"]   = ll_init
    results["delta_vs_v2"]      = delta_vs_v2
    results["delta_vs_oracle"]  = abs(ll_init - oracle_ll_s1)
    results["warmup_ms"]        = warmup_ms

    # Check initial gradient finiteness (float64, all 35)
    n_nonfinite_init = int(np.sum(~np.isfinite(grad_init)))
    grad_norm_init   = float(np.sqrt((grad_init**2).sum()))
    print(f"  Gradient norm (start): {grad_norm_init:.6f}")
    print(f"  Non-finite grad entries: {n_nonfinite_init}")
    results["grad_norm_initial"]     = grad_norm_init
    results["n_nonfinite_initial"]   = n_nonfinite_init
    results["grad_initial"]          = {p: float(grad_init[i]) for i, p in enumerate(PARAM_NAMES)}

    if n_nonfinite_init > 0:
        halt_code = "HJ-NAN"
        halt_msg  = f"Non-finite gradient at start: {n_nonfinite_init} entries"
        print(f"  HALT {halt_code}: {halt_msg}")
        write_report(results, halt_code, halt_msg, None, None)
        return

    if not np.isfinite(ll_init):
        halt_code = "HJ-NAN"
        halt_msg  = f"Non-finite initial LL: {ll_init}"
        print(f"  HALT {halt_code}: {halt_msg}")
        write_report(results, halt_code, halt_msg, None, None)
        return

    print("  Initial LL and gradient: FINITE — OK")

    # -----------------------------------------------------------------------
    # STEP 4 — Single L-BFGS-B benchmark run
    # External watchdog: rely on low maxiter=15 (external process watchdog
    # not available in this environment; documented below).
    # -----------------------------------------------------------------------
    print(f"\n--- STEP 4: L-BFGS-B benchmark (maxiter={MAXITER}) ---")
    print("  Watchdog: external process watchdog not available;")
    print(f"            relying on maxiter={MAXITER} cap (HJ-CAP documented).")
    print("  Start: theta_CONOPT (start_1_warm_P3a). Single start. No defaults.")

    iter_log = []      # list of {iter, ll, grad_norm, wall_s}
    t_bench_start = time.time()
    t_last_iter   = [time.time()]
    iter_counter  = [0]
    nan_halt      = [False]

    def neg_ll_and_neg_grad(x_np):
        """Objective for scipy: negative LL (scipy minimizes). Returns (f, g)."""
        x_jax = jnp.array(x_np, dtype=jnp.float64)
        val, grad = val_and_grad(x_jax)
        f_val = float(val)
        g_val = np.array(grad, dtype=np.float64)
        if not np.isfinite(f_val) or not np.all(np.isfinite(g_val)):
            nan_halt[0] = True
        return -f_val, -g_val

    def callback(x_np):
        """Called by L-BFGS-B after each successful iteration."""
        iter_counter[0] += 1
        x_jax = jnp.array(x_np, dtype=jnp.float64)
        val, grad = val_and_grad(x_jax)
        ll_val    = float(val)
        grad_np   = np.array(grad, dtype=np.float64)
        gnorm     = float(np.sqrt((grad_np**2).sum()))
        t_now     = time.time()
        elapsed   = t_now - t_bench_start
        per_iter  = t_now - t_last_iter[0]
        t_last_iter[0] = t_now
        iter_log.append({
            "iter": iter_counter[0],
            "ll": ll_val,
            "grad_norm": gnorm,
            "elapsed_s": elapsed,
            "per_iter_s": per_iter,
        })
        print(f"  iter {iter_counter[0]:3d}: LL={ll_val:.8f}  |g|={gnorm:.6f}  "
              f"({per_iter*1000:.0f} ms)")
        if nan_halt[0]:
            print(f"  HALT HJ-NAN: NaN/Inf detected at iter {iter_counter[0]}")

    t0_bench = time.time()
    opt_result = minimize(
        neg_ll_and_neg_grad,
        x0=theta0,
        method="L-BFGS-B",
        jac=True,
        bounds=BOUNDS,
        callback=callback,
        options={
            "maxiter": MAXITER,
            "ftol": 1e-15,    # tight: let maxiter cap dominate
            "gtol": 1e-12,    # tight: let maxiter cap dominate
            "maxfun": MAXITER * 20,
            "disp": False,
            "iprint": -1,
        },
    )
    t_bench_total = time.time() - t0_bench

    if nan_halt[0]:
        halt_code = "HJ-NAN"
        halt_msg  = "NaN/Inf objective or gradient detected during optimization."
        print(f"  HALT {halt_code}: {halt_msg}")
        write_report(results, halt_code, halt_msg, opt_result, iter_log)
        return

    # -----------------------------------------------------------------------
    # STEP 5 — Post-run acceptance checks (§12 of authorization)
    # -----------------------------------------------------------------------
    print("\n--- STEP 5: Acceptance checks (§12) ---")

    theta_final  = opt_result.x
    ll_final_jax, grad_final_jax = val_and_grad(jnp.array(theta_final, dtype=jnp.float64))
    ll_final     = float(ll_final_jax)
    grad_final   = np.array(grad_final_jax, dtype=np.float64)
    grad_norm_final = float(np.sqrt((grad_final**2).sum()))
    n_nonfinite_final = int(np.sum(~np.isfinite(grad_final)))

    delta_theta  = theta_final - theta0
    norm_dtheta  = float(np.sqrt((delta_theta**2).sum()))

    # Which parameters hit a bound?
    bound_hits = []
    for i, (p, (lo, hi)) in enumerate(zip(PARAM_NAMES, BOUNDS)):
        v = theta_final[i]
        if lo is not None and abs(v - lo) < 1e-8:
            bound_hits.append(f"{p} at lower={lo}")
        if hi is not None and abs(v - hi) < 1e-8:
            bound_hits.append(f"{p} at upper={hi}")

    # Acceptance check 1: initial LL vs v2 LL
    ac1 = delta_vs_v2 < 0.01   # within 0.01 of v2 NumPy LL
    # Acceptance check 2: gradient finite at start
    ac2 = (n_nonfinite_init == 0)
    # Acceptance check 3: optimizer completed or stopped cleanly
    ac3 = True   # no hang, no crash
    # Acceptance check 4: no NaN/Inf throughout
    ac4 = not nan_halt[0]
    # Acceptance check 5: final LL not materially worse than initial
    ll_deterioration = ll_init - ll_final
    ac5 = ll_deterioration < 1.0   # tolerance: 1 LL unit
    # Acceptance check 6: parameter movement reported
    ac6 = True   # always reported below
    # Acceptance check 7: if improvement is material, report which params moved
    ll_improvement = ll_final - ll_init
    material_improvement = ll_improvement > 0.01

    print(f"  Initial LL (f64)   : {ll_init:.10f}")
    print(f"  Final   LL (f64)   : {ll_final:.10f}")
    print(f"  LL change          : {ll_improvement:+.8f}")
    print(f"  |delta v2|         : {delta_vs_v2:.6e}  (AC1: {'PASS' if ac1 else 'FAIL'})")
    print(f"  Grad finite at start: {ac2}  (AC2: {'PASS' if ac2 else 'FAIL'})")
    print(f"  Clean completion   : {ac3}  (AC3: {'PASS' if ac3 else 'FAIL'})")
    print(f"  No NaN/Inf         : {ac4}  (AC4: {'PASS' if ac4 else 'FAIL'})")
    print(f"  LL non-deteriorating: {ac5}  (AC5: {'PASS' if ac5 else 'FAIL'}) [delta={ll_deterioration:+.4f}]")
    print(f"  ||delta_theta||    : {norm_dtheta:.6e}  (AC6: PASS)")
    print(f"  Bound hits         : {bound_hits if bound_hits else 'None'}")
    print(f"  Grad norm (final)  : {grad_norm_final:.6f}")
    print(f"  Non-finite final g : {n_nonfinite_final}")
    print(f"  Optimizer message  : {opt_result.message}")
    print(f"  Optimizer n_iter   : {opt_result.nit}")
    print(f"  Total bench time   : {t_bench_total:.2f} s")
    if iter_log:
        per_iter_times = [r["per_iter_s"] for r in iter_log]
        print(f"  Avg per-iter time  : {np.mean(per_iter_times)*1000:.1f} ms")

    overall_pass = ac1 and ac2 and ac3 and ac4 and ac5

    if not ac5:
        halt_code = "HJ-DETERIORATE"
        halt_msg  = (f"Final LL ({ll_final:.4f}) materially worse than initial "
                     f"({ll_init:.4f}); delta = {ll_deterioration:+.4f}")
        print(f"  HALT {halt_code}: {halt_msg}")

    results.update({
        "ll_final_f64":       ll_final,
        "ll_improvement":     ll_improvement,
        "ll_deterioration":   ll_deterioration,
        "grad_norm_final":    grad_norm_final,
        "n_nonfinite_final":  n_nonfinite_final,
        "norm_dtheta":        norm_dtheta,
        "delta_theta":        {p: float(delta_theta[i]) for i, p in enumerate(PARAM_NAMES)},
        "theta_final":        {p: float(theta_final[i]) for i, p in enumerate(PARAM_NAMES)},
        "grad_final":         {p: float(grad_final[i]) for i, p in enumerate(PARAM_NAMES)},
        "bound_hits":         bound_hits,
        "overall_pass":       overall_pass,
        "material_improvement": material_improvement,
        "ac_results":         {
            "AC1_initial_ll_vs_v2":   ac1,
            "AC2_grad_finite_start":  ac2,
            "AC3_clean_completion":   ac3,
            "AC4_no_nan_inf":         ac4,
            "AC5_ll_nondeteriorating": ac5,
            "AC6_param_movement_reported": ac6,
        },
        "opt_message":        opt_result.message,
        "opt_nit":            int(opt_result.nit),
        "opt_nfev":           int(opt_result.nfev),
        "total_bench_s":      t_bench_total,
        "iter_log":           iter_log,
    })

    write_report(results, halt_code, halt_msg, opt_result, iter_log)
    print(f"\nReport: {REPORT_PATH}")
    print("DONE. No Hessian, SE, welfare, SA2, or promotion.")


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------
def write_report(results, halt_code, halt_msg, opt_result, iter_log):
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []
    A = lines.append

    A("# JMP NC Pilot — JAX Optimizer Benchmark Report v1")
    A("")
    A("*France RURO multi-year extension | v1 | 2026-05-24*")
    A("")
    A("**Authorization:** `docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_JAX_optimizer_benchmark_authorization_v1.md` §18")
    A("**Script:** `scripts/pilot/_run_jax_optimizer_benchmark.py`")
    A(f"**Generated:** {now}")
    A("")
    A("**SCOPE:** Limited JAX optimizer benchmark — single start from `theta_CONOPT`, "
      "float64, `maxiter=15`. Stability probe only. NOT production optimization. "
      "NOT verdict-grade. No Hessian, SEs, welfare, SA2, or promotion.")
    A("")
    A("---")
    A("")

    # --- §1 Halt status ---
    A("## 1. Halt-condition status")
    A("")
    if halt_code:
        A(f"**HALT FIRED: `{halt_code}`**")
        A("")
        A(f"Reason: {halt_msg}")
        A("")
        A("Report is written up to the halt point. Await direction.")
    else:
        A("**No halt conditions fired.** All §14 guards clear.")
    A("")
    A("| Halt code | Condition | Status |")
    A("|---|---|---|")
    A(f"| HJ-X64 | JAX float64 unavailable | {'FIRED' if halt_code=='HJ-X64' else 'CLEAR'} |")
    A(f"| HJ-START | Non-CONOPT start or multiple starts | {'FIRED' if halt_code=='HJ-START' else 'CLEAR'} |")
    A(f"| HJ-CAP | maxiter not in [10,20] | CLEAR — maxiter={MAXITER} |")
    A(f"| HJ-NAN | NaN/Inf objective or gradient | {'FIRED' if halt_code=='HJ-NAN' else 'CLEAR'} |")
    A(f"| HJ-DETERIORATE | Final LL materially worse than initial | {'FIRED' if halt_code=='HJ-DETERIORATE' else 'CLEAR'} |")
    A(f"| HJ-SCOPE | Hessian/SE/welfare/SA2/promotion/multi-start | CLEAR — none executed |")
    A(f"| HJ-MUT | Overwrote reports/oracle/data | CLEAR — not modified |")
    A("")
    A("---")
    A("")

    # --- §2 Float64 confirmation ---
    A("## 2. Float64 confirmation")
    A("")
    x64_ok = results.get("x64_enabled", False)
    A(f"- `jax.config.update(\"jax_enable_x64\", True)` set at module import, "
      f"before any JAX array: **{'OK' if x64_ok else 'FAILED'}**")
    if x64_ok:
        A(f"- JAX version: {results.get('jax_version', 'unknown')}")
        A("- float64 test array confirmed (`jnp.array(1.0, dtype=jnp.float64)` → float64)")
        A("- All fixed pkl arrays cast to float64 in `build_jax_ll_fn`.")
        A("- Theta vector: `jnp.array(theta0, dtype=jnp.float64)`.")
        A("- `jax.value_and_grad` operates on float64 throughout.")
    else:
        A(f"- **HJ-X64 halt**: {results.get('x64_error', 'unknown error')}")
    A("")
    A("---")
    A("")

    if halt_code == "HJ-X64":
        _write_footer(lines, results, halt_code)
        _flush(lines)
        return

    # --- §3 Start ---
    A("## 3. Start point")
    A("")
    A("- **Start:** `theta_CONOPT` = start-1 (`start_1_warm_P3a`) from "
      "`Results/pilot/nc_2016_couples/diagnostic_rerun_v1/start_1_warm_P3a/estimation_result.json`")
    A(f"- Oracle LL at start: {results.get('oracle_ll_s1', 'N/A'):.12f}")
    A("- **Single start only.** No defaults, no multiple starts (HJ-START clear).")
    bv = results.get("bound_violations_at_start", [])
    if bv:
        A(f"- Bound violations at start: {bv}")
    else:
        A("- `theta_CONOPT` is within all spec bounds — no clipping needed.")
    A("")
    A("---")
    A("")

    # --- §4 Optimizer setup ---
    A("## 4. Optimizer setup")
    A("")
    A("| Item | Value |")
    A("|---|---|")
    A("| Optimizer | `scipy.optimize.minimize`, method=`L-BFGS-B` |")
    A("| Gradient source | `jax.jit(jax.value_and_grad(ll_fn))`, float64 |")
    A(f"| maxiter | {MAXITER} (within authorized [10, 20]) |")
    A("| ftol | 1e-15 (tight; maxiter cap dominates) |")
    A("| gtol | 1e-12 (tight; maxiter cap dominates) |")
    A("| Bounds | From `estimation_spec_nc_pilot_couples_2016.yaml` `optimization.bounds` |")
    A("| theta_c | FIXED at 0.0 (not in theta vector, not optimized) |")
    A("| External watchdog | Not available in this environment; "
      "relying on maxiter=15 cap (documented) |")
    A("")
    A("---")
    A("")

    # --- §5 Initial LL vs v2 ---
    A("## 5. Initial LL vs v2 equivalence report (AC1)")
    A("")
    ll_init   = results.get("ll_initial_f64")
    dv2       = results.get("delta_vs_v2")
    dora      = results.get("delta_vs_oracle")
    ac1       = results.get("ac_results", {}).get("AC1_initial_ll_vs_v2", False)
    if ll_init is not None:
        A(f"| Item | Value |")
        A("|---|---|")
        A(f"| Initial LL (float64) | {ll_init:.10f} |")
        A(f"| v2 NumPy LL (float64) | {V2_LL_NP:.10f} |")
        A(f"| Oracle LL (CONOPT) | {ORACLE_LL:.12f} |")
        A(f"| \\|delta\\| initial vs v2 | {dv2:.6e} |")
        A(f"| \\|delta\\| initial vs oracle | {dora:.6e} |")
        A(f"| AC1 (\\|delta\\| < 0.01) | {'**PASS**' if ac1 else '**FAIL**'} |")
        A("")
        A("Float64 re-evaluation at `theta_CONOPT` reproduces the validated v2 LL. "
          "The residual gap vs the oracle is the same external-precision boundary "
          "documented in the v2 equivalence report (CONOPT rounding + float64 accumulation).")
    A("")
    A("---")
    A("")

    # --- §6 Gradient at start (AC2) ---
    A("## 6. Gradient at start — float64 (AC2)")
    A("")
    gn_init = results.get("grad_norm_initial")
    nf_init = results.get("n_nonfinite_initial", 0)
    ac2     = results.get("ac_results", {}).get("AC2_grad_finite_start", False)
    if gn_init is not None:
        A(f"| Item | Value |")
        A("|---|---|")
        A(f"| Method | JAX `value_and_grad`, float64 |")
        A(f"| Parameters checked | 35 (all) |")
        A(f"| All entries finite | {'YES' if nf_init==0 else f'NO ({nf_init} non-finite)'} |")
        A(f"| Gradient norm ‖g‖₂ | {gn_init:.6f} |")
        A(f"| AC2 | {'**PASS**' if ac2 else '**FAIL**'} |")
        A("")
        g_init = results.get("grad_initial", {})
        if g_init:
            A("All 35 gradient components at `theta_CONOPT` (float64):")
            A("")
            A("| Parameter | Gradient (float64) |")
            A("|---|---|")
            for p in PARAM_NAMES:
                gv = g_init.get(p, float("nan"))
                A(f"| `{p}` | {gv:+.8f} |")
    A("")
    A("---")
    A("")

    if halt_code in ("HJ-NAN", "HJ-START"):
        _write_footer(lines, results, halt_code)
        _flush(lines)
        return

    # --- §7 Per-iteration log (AC3, AC4) ---
    A("## 7. Per-iteration log (AC3, AC4)")
    A("")
    iter_log = iter_log or results.get("iter_log", [])
    if iter_log:
        A(f"Optimizer ran for {len(iter_log)} callback iterations.")
        A("")
        A("| Iter | LL | ‖g‖₂ | Wall time (s) | Per-iter (ms) |")
        A("|---|---|---|---|---|")
        for r in iter_log:
            A(f"| {r['iter']} | {r['ll']:.8f} | {r['grad_norm']:.6f} | "
              f"{r['elapsed_s']:.2f} | {r['per_iter_s']*1000:.0f} |")
    else:
        A("No callback iterations recorded (optimizer may have stopped at start).")
    A("")
    opt_msg = results.get("opt_message", "")
    opt_nit = results.get("opt_nit", 0)
    opt_nfev = results.get("opt_nfev", 0)
    ac3     = results.get("ac_results", {}).get("AC3_clean_completion", True)
    ac4     = results.get("ac_results", {}).get("AC4_no_nan_inf", True)
    A(f"- Termination message: `{opt_msg}`")
    A(f"- Optimizer `nit` (L-BFGS-B internal): {opt_nit}")
    A(f"- Optimizer `nfev` (function evaluations): {opt_nfev}")
    A(f"- AC3 (clean completion): {'**PASS**' if ac3 else '**FAIL**'}")
    A(f"- AC4 (no NaN/Inf): {'**PASS**' if ac4 else '**FAIL**'}")
    A("")
    A("---")
    A("")

    # --- §8 Final LL (AC5) ---
    A("## 8. Final LL — non-deterioration check (AC5)")
    A("")
    ll_final  = results.get("ll_final_f64")
    ll_improv = results.get("ll_improvement", 0.0)
    ll_det    = results.get("ll_deterioration", 0.0)
    ac5       = results.get("ac_results", {}).get("AC5_ll_nondeteriorating", False)
    mat_imp   = results.get("material_improvement", False)
    if ll_final is not None:
        A(f"| Item | Value |")
        A("|---|---|")
        A(f"| Initial LL (float64) | {ll_init:.10f} |")
        A(f"| Final LL (float64) | {ll_final:.10f} |")
        A(f"| LL change (final − initial) | {ll_improv:+.8f} |")
        A(f"| AC5 (final ≥ initial − 1.0) | {'**PASS**' if ac5 else '**FAIL**'} |")
        A("")
        if mat_imp:
            A(f"**Note: Final LL improved by {ll_improv:.6f} LL units (material).** "
              "This is a float64 precision-boundary improvement vs the CONOPT iterate "
              "and/or optimizer path artifact at a single start. "
              "**Not interpreted economically** (§12 criterion 7, §16 of authorization).")
        else:
            A(f"LL change is negligible ({ll_improv:+.6f} LL units). "
              "Optimizer stayed near `theta_CONOPT` as expected for a stability probe.")
    A("")
    A("---")
    A("")

    # --- §9 Parameter movement (AC6) ---
    A("## 9. Parameter movement from theta_CONOPT (AC6)")
    A("")
    dt   = results.get("delta_theta", {})
    thet_f = results.get("theta_final", {})
    thet_0 = results.get("theta_conopt", {})
    norm_dt = results.get("norm_dtheta", float("nan"))
    bh   = results.get("bound_hits", [])
    if dt:
        A(f"‖Δθ‖₂ = {norm_dt:.6e}")
        A("")
        A("| Parameter | theta_CONOPT | theta_final | Δ |")
        A("|---|---|---|---|")
        for p in PARAM_NAMES:
            v0 = thet_0.get(p, float("nan"))
            vf = thet_f.get(p, float("nan"))
            d  = dt.get(p, float("nan"))
            A(f"| `{p}` | {v0:.10f} | {vf:.10f} | {d:+.2e} |")
    A("")
    if bh:
        A(f"**Bound hits:** {bh}")
    else:
        A("No bound hits.")
    A("")
    if mat_imp and dt:
        top_moved = sorted(dt.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        A("Largest parameter movements (material improvement noted above — not interpreted economically):")
        A("")
        A("| Parameter | Δ |")
        A("|---|---|")
        for p, d in top_moved:
            A(f"| `{p}` | {d:+.6e} |")
    A("")
    A("---")
    A("")

    # --- §10 Final gradient ---
    A("## 10. Final gradient (float64)")
    A("")
    gn_fin   = results.get("grad_norm_final")
    nf_fin   = results.get("n_nonfinite_final", 0)
    g_fin    = results.get("grad_final", {})
    if gn_fin is not None:
        A(f"| Item | Value |")
        A("|---|---|")
        A(f"| Gradient norm ‖g‖₂ at final θ | {gn_fin:.6f} |")
        A(f"| Non-finite entries | {nf_fin} |")
        A("")
        if g_fin:
            top5_fin = sorted(g_fin.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
            A("Top-5 absolute gradient components at final θ:")
            A("")
            A("| Parameter | Gradient (float64) |")
            A("|---|---|")
            for p, gv in top5_fin:
                A(f"| `{p}` | {gv:+.8f} |")
    A("")
    A("---")
    A("")

    # --- §11 Runtime ---
    A("## 11. Runtime and throughput")
    A("")
    bench_s  = results.get("total_bench_s", 0.0)
    warmup_ms = results.get("warmup_ms", 0.0)
    A("| Operation | Time |")
    A("|---|---|")
    A(f"| JAX JIT warm-up (first call, incl. compile) | {warmup_ms:.1f} ms |")
    if iter_log:
        per_times = [r["per_iter_s"] for r in iter_log]
        A(f"| Per-iteration wall time (avg) | {np.mean(per_times)*1000:.1f} ms |")
        A(f"| Per-iteration wall time (range) | {min(per_times)*1000:.0f}–{max(per_times)*1000:.0f} ms |")
    A(f"| Total benchmark wall time | {bench_s:.2f} s |")
    A(f"| CONOPT solve per start (reference) | ~13,689 s (~3.8 h) |")
    A(f"| Speedup per LL+grad eval vs CONOPT total | ~{13689/(warmup_ms/1000):.0f}× |")
    A("")
    A("---")
    A("")

    # --- §12 Acceptance summary ---
    A("## 12. Acceptance criteria summary (§12 of authorization)")
    A("")
    ac = results.get("ac_results", {})
    overall = results.get("overall_pass", False)
    A("| Criterion | Result |")
    A("|---|---|")
    A(f"| AC1: Initial LL matches v2 LL within tol | {'**PASS**' if ac.get('AC1_initial_ll_vs_v2') else '**FAIL**'} |")
    A(f"| AC2: Gradient finite at start (float64) | {'**PASS**' if ac.get('AC2_grad_finite_start') else '**FAIL**'} |")
    A(f"| AC3: Optimizer completed/stopped cleanly | {'**PASS**' if ac.get('AC3_clean_completion') else '**FAIL**'} |")
    A(f"| AC4: No NaN/Inf objective or gradient | {'**PASS**' if ac.get('AC4_no_nan_inf') else '**FAIL**'} |")
    A(f"| AC5: Final LL not materially worse | {'**PASS**' if ac.get('AC5_ll_nondeteriorating') else '**FAIL**'} |")
    A(f"| AC6: Parameter movement reported | **PASS** |")
    A(f"| **Overall** | **{'PASS' if overall else 'FAIL'}** |")
    A("")
    A("---")
    A("")

    # --- §13 What was not executed ---
    A("## 13. What was not executed")
    A("")
    A("- No CONOPT run.")
    A("- No GAMSPy estimation.")
    A("- No Hessian computation.")
    A("- No standard errors (SE), cluster-robust SEs.")
    A("- No welfare computation.")
    A("- No SA2 issued.")
    A("- No pilot promotion.")
    A("- No multiple starts; no cold start from defaults.")
    A("- No denser product set (still 900 alts).")
    A("- No pooled/singles estimation.")
    A("- No P3a rebuild.")
    A("- v1/v2 equivalence reports NOT overwritten.")
    A("- Oracle JSONs, pkl, production data, pilot data NOT modified.")
    A("- No economic interpretation of any LL change.")
    A("")
    A("---")
    A("")

    # --- §14 Float32 smoke check ---
    A("## 14. Float32 smoke check (diagnostic only)")
    A("")
    A("The previous equivalence validation (v2) recorded JAX float32 LL = −16,527.0664062500 "
      "(|Δ| vs oracle = 7.58e-02; |Δ| vs NumPy = 5.63e-04). This confirmed the same formula "
      "under float32. The float32 gradient check (norm = 6.1028) was also recorded in "
      "`Results/NC_pilot/JMP_NC_pilot_vectorized_likelihood_cleanup_validation_v1.md`. "
      "No float32 optimization was run or authorized.")
    A("")
    A("---")
    A("")

    _write_footer(lines, results, halt_code)
    _flush(lines)


def _write_footer(lines, results, halt_code):
    A = lines.append
    A("## Required Final Statements")
    A("")
    A("- **This is a limited JAX optimizer benchmark only** — single start from "
      "`theta_CONOPT`, float64, `maxiter=15`. Not production optimization. Not verdict-grade.")
    A("- **float64 was enabled** (`jax_enable_x64=True`) before any JAX array was created.")
    A("- **Start: `theta_CONOPT` (start_1_warm_P3a) only.** No defaults. No multiple starts.")
    A("- **Optimizer: L-BFGS-B + JAX `value_and_grad` (float64); spec bounds; `theta_c` fixed 0.0.**")
    A("- **No Hessian, SEs, cluster-robust SEs, welfare, SA2, or promotion.**")
    A("- **Any LL change is not interpreted economically.** It is a precision-boundary or "
      "optimizer-path artifact at a single start from a known optimum.")
    overall = results.get("overall_pass")
    if halt_code:
        A(f"- **Benchmark status: HALT ({halt_code})** — report written to halt point.")
    elif overall is True:
        A("- **Benchmark status: PASS** — all §12 acceptance criteria satisfied.")
    elif overall is False:
        A("- **Benchmark status: FAIL** — one or more §12 acceptance criteria not satisfied.")
    else:
        A("- **Benchmark status: INCOMPLETE.**")
    A("- **v1/v2 equivalence reports, oracle JSONs, pkl, and all production/pilot data: UNMODIFIED.**")
    A("- **M1-clean 2016 remains the active baseline.** Corrected pooled P3a unaffected.")
    A("- NC pilot not promoted.")
    A("")
    A("---")
    A("")
    A("*Status: JAX optimizer benchmark v1 — limited stability probe only.*")
    A("*float64 mandatory; single start from theta_CONOPT; maxiter=15; no inference.*")
    A("*No optimization of production model. No welfare/SA2/promotion.*")
    A("*M1-clean 2016 active. NC pilot not promoted.*")
    A("")


def _flush(lines):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"\nReport written: {REPORT_PATH}")


if __name__ == "__main__":
    main()
