"""
Optimizer-Protocol Diagnostic — FR_2016 couples pilot.

Authorization: docs/France_case/NC_pilot/design/JMP_NC_pilot_optimizer_multistart_design_memo_v1.md s22

SCOPE: Staged diagnostic to determine whether the HV-AGREE disagreement from
the three-start validation is a convergence-budget/conditioning artifact or
genuine multimodality. DIAGNOSTIC ONLY — NOT production, NOT verdict-grade.

  Stage 1 — Near-oracle basin test: theta_CONOPT + 3 small perturbations,
             maxiter=1500, tolerance-based stop (ftol/gtol allow success).
  Stage 2 — Cold-start recovery (defaults):
             (a) long L-BFGS-B (maxiter=1500);
             (b) Adam warm-up (500 steps) -> L-BFGS-B (maxiter=1000);
             (c) parameter scaling -> L-BFGS-B (maxiter=1500) -> invert.
  Stage 3 — beta_l0_m verdict at a CONVERGED (tolerance-stop) point only.

HARD CONSTRAINTS:
  - JAX float64 (jax_enable_x64 before any array).
  - No winner picked; no estimate accepted; no economic interpretation.
  - Same model, data, bounds, theta_c fixed 0.0.
  - Do NOT overwrite prior reports, oracle JSONs, or pkl.
  - New script + new report only.

Architecture: each sub-run executes in an isolated subprocess (RUN_JOB env var)
to prevent XLA/JAX memory accumulation across many long runs.
"""

import sys, os

# ---------------------------------------------------------------------------
# Subprocess dispatch: RUN_JOB env var names the job label; orchestrator
# (no env var) launches all subprocesses sequentially.
# ---------------------------------------------------------------------------
RUN_JOB = os.environ.get("RUN_JOB")   # e.g. "S1_A", "S1_C1", "S2a", "S2b", "S2c"

if RUN_JOB is not None:
    # -----------------------------------------------------------------------
    # WORKER MODE
    # -----------------------------------------------------------------------
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    # float64 FIRST — before any JAX array
    _X64_ENABLED = False
    _X64_ERROR   = None
    try:
        import jax
        jax.config.update("jax_enable_x64", True)
        import jax.numpy as jnp
        _test = jnp.array(1.0, dtype=jnp.float64)
        assert _test.dtype == jnp.float64
        _X64_ENABLED = True
    except Exception as _e:
        _X64_ERROR = str(_e)

    import json, math, pickle, time, warnings
    from pathlib import Path
    import numpy as np
    from scipy.optimize import minimize

    REPO     = Path(__file__).resolve().parents[2].resolve()
    _enhanced = str(REPO / "scripts" / "enhanced")
    if _enhanced not in sys.path:
        sys.path.insert(0, _enhanced)

    PKL_PATH  = (REPO / "Data/pilot/nc_2016_couples/precomputed"
                 / "fr_pilot_nc_2016_couples_precomputed_loc.pkl")
    RESULT_S1 = (REPO / "Results/pilot/nc_2016_couples/diagnostic_rerun_v1"
                 / "start_1_warm_P3a/estimation_result.json")
    TMP_DIR   = REPO / "scripts/pilot/_tmp_optdiag"
    TMP_DIR.mkdir(exist_ok=True)

    EPS = 1e-12
    ORACLE_LL = -16527.14218317334

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
        "sigma", "beta_ll",
    ]
    BOUNDS_DICT = {
        "theta_l_m":    (-8.0, 0.95),  "theta_l_f":    (-8.0, 0.95),
        "beta_c":       (0.05, 50.0),  "beta_l0_m":    (1.0e-6, 50.0),
        "beta_l0_f":    (0.05, 50.0),
        "beta_l_age_m":   (-5.0, 5.0),  "beta_l_age2_m":  (-1.0, 1.0),
        "beta_l_age_f":   (-5.0, 5.0),  "beta_l_age2_f":  (-1.0, 1.0),
        "beta_l_nkids_f": (-5.0, 5.0),
        "beta_E": (-25.0, 25.0),        "beta_h_pt1": (-10.0, 10.0),
        "beta_h_pt2": (-10.0, 10.0),   "beta_h_ft": (-10.0, 10.0),
        "beta_w0": (-10.0, 20.0),      "beta_w_educL": (-5.0, 5.0),
        "beta_w_educH": (-5.0, 5.0),  "beta_w_pexp": (-1.0, 1.0),
        "beta_w_pexp2": (-0.1, 0.1),
        "beta_E_gsur":   (-10.0, 10.0), "beta_E_drgn2":  (-10.0, 10.0),
        "beta_E_drgn3":  (-10.0, 10.0), "beta_E_drgn4":  (-10.0, 10.0),
        "beta_E_drgn5":  (-10.0, 10.0), "beta_E_drgn6":  (-10.0, 10.0),
        "beta_E_drgn7":  (-10.0, 10.0), "beta_E_drgn8":  (-10.0, 10.0),
        "beta_occ_2_cm": (-10.0, 10.0), "beta_occ_3_cm": (-10.0, 10.0),
        "beta_occ_4_cm": (-10.0, 10.0), "beta_occ_2_cf": (-10.0, 10.0),
        "beta_occ_3_cf": (-10.0, 10.0), "beta_occ_4_cf": (-10.0, 10.0),
        "sigma": (0.1, 20.0),           "beta_ll": (0.0, 10.0),
    }
    BOUNDS = [BOUNDS_DICT.get(p, (None, None)) for p in PARAM_NAMES]

    DEFAULTS_DICT = {
        "beta_l0_m": 1e-6, "beta_l_age_m": 0.0059, "beta_l_age2_m": 0.0016,
        "theta_l_m": -0.682, "beta_l0_f": 2.605, "beta_l_age_f": -0.058,
        "beta_l_age2_f": 0.0053, "beta_l_nkids_f": 0.143, "theta_l_f": -0.658,
        "beta_c": 4.312, "beta_E": -2.398, "beta_h_pt1": -0.475,
        "beta_h_pt2": 0.425, "beta_h_ft": 1.406, "beta_E_gsur": -1.200,
        "beta_E_drgn2": 0.396, "beta_E_drgn3": 0.350, "beta_E_drgn4": 0.642,
        "beta_E_drgn5": 0.431, "beta_E_drgn6": 0.358, "beta_E_drgn7": 0.367,
        "beta_E_drgn8": 0.168,
        "beta_occ_2_cm": -1.503, "beta_occ_3_cm": -2.222, "beta_occ_4_cm": 0.476,
        "beta_occ_2_cf": 0.113, "beta_occ_3_cf": -0.329, "beta_occ_4_cf": 1.075,
        "beta_w0": 2.033, "beta_w_educL": -0.041, "beta_w_educH": 0.307,
        "beta_w_pexp": 0.0173, "beta_w_pexp2": -0.000182, "sigma": 0.403,
        "beta_ll": 2.656,
    }

    def clip_to_bounds(x):
        x = x.copy()
        for i, (lo, hi) in enumerate(BOUNDS):
            if lo is not None: x[i] = max(x[i], lo + 1e-10)
            if hi is not None: x[i] = min(x[i], hi - 1e-10)
        return x

    # ------------------------------------------------------------------ #
    # Load theta_CONOPT
    # ------------------------------------------------------------------ #
    with open(RESULT_S1) as fh:
        r1 = json.load(fh)
    theta_conopt_dict = {p: r1["parameters"][p] for p in PARAM_NAMES}
    theta_conopt_np   = np.array([theta_conopt_dict[p] for p in PARAM_NAMES],
                                  dtype=np.float64)

    # ------------------------------------------------------------------ #
    # Load precomputed object
    # ------------------------------------------------------------------ #
    with open(PKL_PATH, "rb") as fh:
        pc = pickle.load(fh)
    print(f"  pkl loaded: n_groups={pc.n_groups}")

    # ------------------------------------------------------------------ #
    # Build JAX LL function (reused v2/benchmark kernel, no logic change)
    # ------------------------------------------------------------------ #
    def build_jax_ll_fn(pc):
        N, J = pc.n_groups, pc.n_obs // pc.n_groups
        eps = float(EPS)
        log2pi_half = 0.5 * math.log(2.0 * math.pi)
        def f64(a): return jnp.array(a.reshape(N, J), dtype=jnp.float64)
        fixed = {
            "consumption": f64(pc.consumption), "leisure_m": f64(pc.leisure_male),
            "leisure_f": f64(pc.leisure_female), "prior": f64(pc.prior),
            "chosen": f64(pc.actual_choice), "working_m": f64(pc.working_male),
            "working_f": f64(pc.working_female), "log_wage_m": f64(pc.log_wage_male),
            "log_wage_f": f64(pc.log_wage_female), "age_m": f64(pc.age_norm_male),
            "age2_m": f64(pc.age_norm2_male), "age_f": f64(pc.age_norm_female),
            "age2_f": f64(pc.age_norm2_female), "n_kids": f64(pc.n_children),
            "gsur_m": f64(pc.gsur_male), "gsur_f": f64(pc.gsur_female),
            "reg2": f64(pc.reg2), "reg3": f64(pc.reg3), "reg4": f64(pc.reg4),
            "reg5": f64(pc.reg5), "reg6": f64(pc.reg6), "reg7": f64(pc.reg7),
            "reg8": f64(pc.reg8),
            "loc4_2_m": f64(pc.loc4_2_male), "loc4_3_m": f64(pc.loc4_3_male),
            "loc4_4_m": f64(pc.loc4_4_male), "loc4_2_f": f64(pc.loc4_2_female),
            "loc4_3_f": f64(pc.loc4_3_female), "loc4_4_f": f64(pc.loc4_4_female),
            "educL_m": f64(pc.educL_male),  "educH_m": f64(pc.educH_male),
            "pexp_m": f64(pc.pexp_years_male), "pexp2_m": f64(pc.pexp_years2_male),
            "educL_f": f64(pc.educL_female), "educH_f": f64(pc.educH_female),
            "pexp_f": f64(pc.pexp_years_female), "pexp2_f": f64(pc.pexp_years2_female),
            "wpt1_m": f64(pc.working_pt1_male), "wpt2_m": f64(pc.working_pt2_male),
            "wft_m": f64(pc.working_ft_male), "wpt1_f": f64(pc.working_pt1_female),
            "wpt2_f": f64(pc.working_pt2_female), "wft_f": f64(pc.working_ft_female),
        }
        def ll_fn(theta_vec):
            p = {k: theta_vec[i] for i, k in enumerate(PARAM_NAMES)}
            f = fixed
            def bc(x, theta):
                lx = jnp.log(x + eps); t = theta
                return lx * (1.0 + t*lx/2.0 + t*t*lx*lx/6.0
                             + t*t*t*lx*lx*lx/24.0 + t*t*t*t*lx*lx*lx*lx/120.0)
            bc_c = jnp.log(jnp.maximum(f["consumption"], eps))
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
                    + p["beta_w_educH"]*f["educH_m"] + p["beta_w_pexp"]*f["pexp_m"]
                    + p["beta_w_pexp2"]*f["pexp2_m"])
            mu_f = (p["beta_w0"] + p["beta_w_educL"]*f["educL_f"]
                    + p["beta_w_educH"]*f["educH_f"] + p["beta_w_pexp"]*f["pexp_f"]
                    + p["beta_w_pexp2"]*f["pexp2_f"])
            log_w_m = f["working_m"] * (-0.5*(f["log_wage_m"]-mu_m)**2/(sigma**2+eps)
                                         - jnp.log(sigma+eps) - log2pi_half
                                         - f["log_wage_m"])
            log_w_f = f["working_f"] * (-0.5*(f["log_wage_f"]-mu_f)**2/(sigma**2+eps)
                                         - jnp.log(sigma+eps) - log2pi_half
                                         - f["log_wage_f"])
            log_market = (p["beta_E_gsur"]*f["gsur_m"]*f["working_m"]*10.0
                          + p["beta_E_gsur"]*f["gsur_f"]*f["working_f"]*10.0)
            w_hh = f["working_m"] + f["working_f"]
            for coef, reg in [
                ("beta_E_drgn2","reg2"),("beta_E_drgn3","reg3"),("beta_E_drgn4","reg4"),
                ("beta_E_drgn5","reg5"),("beta_E_drgn6","reg6"),("beta_E_drgn7","reg7"),
                ("beta_E_drgn8","reg8")]:
                log_market = log_market + p[coef]*f[reg]*w_hh
            log_market = (log_market
                + p["beta_occ_2_cm"]*f["loc4_2_m"]*f["working_m"]
                + p["beta_occ_3_cm"]*f["loc4_3_m"]*f["working_m"]
                + p["beta_occ_4_cm"]*f["loc4_4_m"]*f["working_m"]
                + p["beta_occ_2_cf"]*f["loc4_2_f"]*f["working_f"]
                + p["beta_occ_3_cf"]*f["loc4_3_f"]*f["working_f"]
                + p["beta_occ_4_cf"]*f["loc4_4_f"]*f["working_f"])
            prior_sum = f["prior"].sum(axis=1, keepdims=True) + eps
            center = (f["prior"]*log_market).sum(axis=1, keepdims=True) / prior_sum
            log_market_c = log_market - center
            log_prior = jnp.log(f["prior"] + eps)
            utility = (u_pref + log_h_m + log_h_f + log_w_m + log_w_f
                       + log_market_c - log_prior)
            u_max = utility.max(axis=1, keepdims=True)
            log_den = jnp.log(jnp.exp(utility - u_max).sum(axis=1)) + u_max.squeeze()
            chosen_u = (f["chosen"] * utility).sum(axis=1)
            return (chosen_u - log_den).sum()
        return ll_fn

    ll_fn = build_jax_ll_fn(pc)
    vag   = jax.jit(jax.value_and_grad(ll_fn))

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #
    def bound_hit_diag(pname, value, grad_ll):
        lo, hi = BOUNDS_DICT.get(pname, (None, None))
        tol = 1e-6
        at_lower = (lo is not None) and (abs(value - lo) < tol)
        at_upper = (hi is not None) and (abs(value - hi) < tol)
        if not at_lower and not at_upper:
            return None
        ABS_FLAT = 0.05
        diag = {"param": pname, "value": float(value), "grad_ll": float(grad_ll),
                "at_lower": bool(at_lower), "at_upper": bool(at_upper),
                "bound": float(lo if at_lower else hi)}
        if at_lower:
            if grad_ll < -ABS_FLAT:
                diag["verdict"] = "ACTIVE_CONSTRAINT"
                diag["detail"]  = f"grad_ll={grad_ll:.4f}<0: wants to go below lower bound. Corner."
            elif abs(grad_ll) <= ABS_FLAT:
                diag["verdict"] = "NEAR_FLAT"
                diag["detail"]  = f"|grad_ll|={abs(grad_ll):.4f}<=0.05: incidental contact."
            else:
                diag["verdict"] = "INACTIVE"
                diag["detail"]  = f"grad_ll={grad_ll:.4f}>0: pushing away from lower bound."
        else:
            if grad_ll > ABS_FLAT:
                diag["verdict"] = "ACTIVE_CONSTRAINT"
                diag["detail"]  = f"grad_ll={grad_ll:.4f}>0: wants to go above upper bound. Corner."
            elif abs(grad_ll) <= ABS_FLAT:
                diag["verdict"] = "NEAR_FLAT"
                diag["detail"]  = f"|grad_ll|={abs(grad_ll):.4f}<=0.05: incidental contact."
            else:
                diag["verdict"] = "INACTIVE"
                diag["detail"]  = f"grad_ll={grad_ll:.4f}<0: pushing away from upper bound."
        return diag

    def get_bound_hits_and_diags(theta_f, grad_f):
        bound_hits = []
        bh_diags   = []
        for i, (p, (lo, hi)) in enumerate(zip(PARAM_NAMES, BOUNDS)):
            v = float(theta_f[i])
            if lo is not None and abs(v - lo) < 1e-7:
                bound_hits.append([p, "lower", float(lo), v])
            if hi is not None and abs(v - hi) < 1e-7:
                bound_hits.append([p, "upper", float(hi), v])
        for bh in bound_hits:
            pname, side, bval, pval = bh
            gi_ll = float(grad_f[PARAM_NAMES.index(pname)])
            d = bound_hit_diag(pname, pval, gi_ll)
            if d:
                bh_diags.append(d)
        return bound_hits, bh_diags

    class _NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):  return int(obj)
            if isinstance(obj, (np.floating,)): return float(obj)
            if isinstance(obj, (np.bool_,)):    return bool(obj)
            if isinstance(obj, np.ndarray):     return obj.tolist()
            return super().default(obj)

    def run_lbfgsb(theta0_np, maxiter, ftol=1e-9, gtol=1e-7, label=""):
        """Run L-BFGS-B from theta0_np; return result dict."""
        print(f"  [{label}] JIT warm-up ...")
        t0_wu = time.time()
        tv = jnp.array(theta0_np, dtype=jnp.float64)
        ll_s_jax, g_s_jax = vag(tv)
        warmup_ms = (time.time() - t0_wu) * 1000
        ll_start   = float(ll_s_jax)
        grad_start = np.array(g_s_jax, dtype=np.float64)
        gnorm_start = float(np.sqrt((grad_start**2).sum()))
        print(f"  [{label}] warm-up {warmup_ms:.0f}ms  LL={ll_start:.8f}  |g|={gnorm_start:.6f}")

        iter_log  = []
        nan_halt  = [False]
        t0_b      = time.time()
        t_last    = [time.time()]
        ic        = [0]

        def neg_ll_grad(x_np):
            xj = jnp.array(x_np, dtype=jnp.float64)
            val, grad = vag(xj)
            fv = float(val); gv = np.array(grad, dtype=np.float64)
            if not np.isfinite(fv) or not np.all(np.isfinite(gv)):
                nan_halt[0] = True
            return -fv, -gv

        def cb(x_np):
            ic[0] += 1
            xj = jnp.array(x_np, dtype=jnp.float64)
            val, grad = vag(xj)
            ll_v = float(val); gnorm = float(np.sqrt(np.sum(np.array(grad)**2)))
            t_now = time.time(); pi = t_now - t_last[0]; t_last[0] = t_now
            iter_log.append({"iter": ic[0], "ll": ll_v, "grad_norm": gnorm,
                              "per_iter_s": pi})
            if ic[0] % 50 == 0 or ic[0] <= 10:
                print(f"  [{label}] iter {ic[0]:4d}: LL={ll_v:.8f}  |g|={gnorm:.6f}  ({pi*1000:.0f}ms)")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            opt = minimize(neg_ll_grad, x0=theta0_np, method="L-BFGS-B", jac=True,
                           bounds=BOUNDS, callback=cb,
                           options={"maxiter": maxiter, "ftol": ftol, "gtol": gtol,
                                    "maxfun": maxiter*30, "disp": False, "iprint": -1})
        wall_s = time.time() - t0_b

        theta_f  = opt.x
        xj_f     = jnp.array(theta_f, dtype=jnp.float64)
        ll_f_jax, g_f_jax = vag(xj_f)
        ll_final  = float(ll_f_jax)
        grad_final = np.array(g_f_jax, dtype=np.float64)
        gnorm_final = float(np.sqrt((grad_final**2).sum()))

        converged = bool(opt.success)
        term_type = "TOLERANCE_STOP" if converged else "CAP_HIT"
        print(f"  [{label}] DONE  LL={ll_final:.8f}  |g|={gnorm_final:.6f}  "
              f"nit={opt.nit}  {term_type}  wall={wall_s:.1f}s")

        bound_hits, bh_diags = get_bound_hits_and_diags(theta_f, grad_final)
        delta_conopt = theta_f - theta_conopt_np

        return {
            "label": label, "method": "L-BFGS-B",
            "maxiter": maxiter, "ftol": ftol, "gtol": gtol,
            "ll_start": ll_start, "gnorm_start": gnorm_start,
            "ll_final": ll_final, "gnorm_final": gnorm_final,
            "iter_log_first10": iter_log[:10],
            "iter_log_last10":  iter_log[-10:],
            "nit": int(opt.nit), "nfev": int(opt.nfev),
            "opt_success": converged, "term_type": term_type,
            "opt_message": opt.message,
            "theta_start": {p: float(theta0_np[i]) for i, p in enumerate(PARAM_NAMES)},
            "theta_final": {p: float(theta_f[i])   for i, p in enumerate(PARAM_NAMES)},
            "grad_final":  {p: float(grad_final[i]) for i, p in enumerate(PARAM_NAMES)},
            "delta_from_conopt": {p: float(delta_conopt[i]) for i, p in enumerate(PARAM_NAMES)},
            "norm_dtheta_conopt": float(np.sqrt((delta_conopt**2).sum())),
            "bound_hits": bound_hits, "bh_diags": bh_diags,
            "nan_halt": bool(nan_halt[0]),
            "wall_s": wall_s, "warmup_ms": warmup_ms,
        }

    def run_adam_then_lbfgsb(theta0_np, adam_steps, adam_lr, lbfgsb_maxiter,
                              ftol=1e-9, gtol=1e-7, label=""):
        """Adam warm-up -> L-BFGS-B. Returns result dict."""
        print(f"  [{label}] Adam warm-up ({adam_steps} steps, lr={adam_lr}) ...")
        t0_wu = time.time()
        tv = jnp.array(theta0_np, dtype=jnp.float64)
        _, _ = vag(tv)   # JIT compile
        warmup_ms = (time.time() - t0_wu) * 1000

        # Adam parameters
        m  = np.zeros(len(PARAM_NAMES), dtype=np.float64)
        v2 = np.zeros(len(PARAM_NAMES), dtype=np.float64)
        b1, b2, ep = 0.9, 0.999, 1e-8
        theta_adam = theta0_np.copy()
        ll_adam_log = []

        t0_adam = time.time()
        for step in range(1, adam_steps + 1):
            xj = jnp.array(theta_adam, dtype=jnp.float64)
            ll_v_jax, g_jax = vag(xj)
            ll_v = float(ll_v_jax)
            g    = np.array(g_jax, dtype=np.float64)   # grad of LL (to maximise)
            if not np.isfinite(ll_v) or not np.all(np.isfinite(g)):
                print(f"  [{label}] Adam NaN at step {step} — switching to last finite theta")
                break
            m  = b1 * m  + (1 - b1) * g     # note: ascending (maximize LL)
            v2 = b2 * v2 + (1 - b2) * g**2
            m_hat = m  / (1 - b1**step)
            v_hat = v2 / (1 - b2**step)
            theta_adam = theta_adam + adam_lr * m_hat / (np.sqrt(v_hat) + ep)
            theta_adam = clip_to_bounds(theta_adam)
            if step % 100 == 0 or step <= 5:
                gnorm = float(np.sqrt((g**2).sum()))
                print(f"  [{label}] Adam step {step:4d}: LL={ll_v:.6f}  |g|={gnorm:.4f}")
                ll_adam_log.append({"step": step, "ll": ll_v, "grad_norm": gnorm})
        adam_wall_s = time.time() - t0_adam

        xj = jnp.array(theta_adam, dtype=jnp.float64)
        ll_after_adam = float(vag(xj)[0])
        print(f"  [{label}] After Adam: LL={ll_after_adam:.8f}  ({adam_wall_s:.1f}s)")
        print(f"  [{label}] Switching to L-BFGS-B (maxiter={lbfgsb_maxiter}) ...")

        res_lbfgsb = run_lbfgsb(theta_adam, maxiter=lbfgsb_maxiter, ftol=ftol, gtol=gtol,
                                 label=label + "_LBFGSB")

        return {
            "label": label, "method": "Adam->L-BFGS-B",
            "adam_steps": adam_steps, "adam_lr": adam_lr, "adam_wall_s": adam_wall_s,
            "ll_adam_log": ll_adam_log, "ll_after_adam": ll_after_adam,
            "theta_after_adam": {p: float(theta_adam[i]) for i, p in enumerate(PARAM_NAMES)},
            "warmup_ms": warmup_ms,
            **{k: v for k, v in res_lbfgsb.items() if k != "label"},
        }

    def run_scaled_lbfgsb(theta0_np, scale, maxiter, ftol=1e-9, gtol=1e-7, label=""):
        """Parameter scaling: optimize z = theta / scale, report in original space.
        scale[i] = abs(theta_conopt[i]) if != 0, else 1.0.
        """
        print(f"  [{label}] Scaled L-BFGS-B (maxiter={maxiter}) ...")
        t0_wu = time.time()
        tv = jnp.array(theta0_np, dtype=jnp.float64)
        _, _ = vag(tv)
        warmup_ms = (time.time() - t0_wu) * 1000

        scale_jax = jnp.array(scale, dtype=jnp.float64)
        # Scaled bounds
        scaled_bounds = []
        for i, (lo, hi) in enumerate(BOUNDS):
            s = scale[i]
            slo = (lo / s) if lo is not None else None
            shi = (hi / s) if hi is not None else None
            if s < 0:  # sign flip
                slo, shi = (shi, slo)
            scaled_bounds.append((slo, shi))

        def neg_ll_grad_scaled(z_np):
            theta_np = z_np * scale
            xj = jnp.array(theta_np, dtype=jnp.float64)
            val, grad_theta = vag(xj)
            fv = float(val); gv_theta = np.array(grad_theta, dtype=np.float64)
            if not np.isfinite(fv) or not np.all(np.isfinite(gv_theta)):
                return -fv, -gv_theta * scale
            gv_z = gv_theta * scale   # chain rule: dLL/dz = dLL/dtheta * scale
            return -fv, -gv_z

        z0 = theta0_np / scale
        iter_log = []
        nan_halt = [False]
        t0_b = time.time(); t_last = [time.time()]; ic = [0]

        def neg_ll_grad_scaled_nan(z_np):
            rv, rg = neg_ll_grad_scaled(z_np)
            if not np.isfinite(rv) or not np.all(np.isfinite(rg)):
                nan_halt[0] = True
            return rv, rg

        def cb(z_np):
            ic[0] += 1
            theta_cb = z_np * scale
            xj = jnp.array(theta_cb, dtype=jnp.float64)
            val, grad = vag(xj)
            ll_v = float(val); gnorm = float(np.sqrt(np.sum(np.array(grad)**2)))
            t_now = time.time(); pi = t_now - t_last[0]; t_last[0] = t_now
            iter_log.append({"iter": ic[0], "ll": ll_v, "grad_norm": gnorm, "per_iter_s": pi})
            if ic[0] % 50 == 0 or ic[0] <= 10:
                print(f"  [{label}] iter {ic[0]:4d}: LL={ll_v:.8f}  |g|={gnorm:.6f}  ({pi*1000:.0f}ms)")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            opt = minimize(neg_ll_grad_scaled_nan, x0=z0, method="L-BFGS-B", jac=True,
                           bounds=scaled_bounds, callback=cb,
                           options={"maxiter": maxiter, "ftol": ftol, "gtol": gtol,
                                    "maxfun": maxiter*30, "disp": False, "iprint": -1})
        wall_s = time.time() - t0_b

        theta_f  = opt.x * scale   # invert scaling
        xj_f     = jnp.array(theta_f, dtype=jnp.float64)
        ll_f_jax, g_f_jax = vag(xj_f)
        ll_final   = float(ll_f_jax)
        grad_final = np.array(g_f_jax, dtype=np.float64)
        gnorm_final = float(np.sqrt((grad_final**2).sum()))
        converged   = bool(opt.success)
        term_type   = "TOLERANCE_STOP" if converged else "CAP_HIT"
        print(f"  [{label}] DONE  LL={ll_final:.8f}  |g|={gnorm_final:.6f}  "
              f"nit={opt.nit}  {term_type}  wall={wall_s:.1f}s")

        bound_hits, bh_diags = get_bound_hits_and_diags(theta_f, grad_final)
        delta_conopt = theta_f - theta_conopt_np

        return {
            "label": label, "method": "Scaled-L-BFGS-B",
            "maxiter": maxiter, "ftol": ftol, "gtol": gtol,
            "ll_start": float(vag(jnp.array(theta0_np, dtype=jnp.float64))[0]),
            "gnorm_start": float(np.sqrt((np.array(vag(jnp.array(theta0_np, dtype=jnp.float64))[1])**2).sum())),
            "ll_final": ll_final, "gnorm_final": gnorm_final,
            "iter_log_first10": iter_log[:10], "iter_log_last10": iter_log[-10:],
            "nit": int(opt.nit), "nfev": int(opt.nfev),
            "opt_success": converged, "term_type": term_type,
            "opt_message": opt.message,
            "theta_start": {p: float(theta0_np[i]) for i, p in enumerate(PARAM_NAMES)},
            "theta_final": {p: float(theta_f[i]) for i, p in enumerate(PARAM_NAMES)},
            "grad_final":  {p: float(grad_final[i]) for i, p in enumerate(PARAM_NAMES)},
            "delta_from_conopt": {p: float(delta_conopt[i]) for i, p in enumerate(PARAM_NAMES)},
            "norm_dtheta_conopt": float(np.sqrt((delta_conopt**2).sum())),
            "bound_hits": bound_hits, "bh_diags": bh_diags,
            "nan_halt": bool(nan_halt[0]),
            "wall_s": wall_s, "warmup_ms": warmup_ms,
        }

    # ------------------------------------------------------------------ #
    # Per-job dispatch
    # ------------------------------------------------------------------ #
    MAXITER_S1  = 1500   # Stage-1: large budget
    MAXITER_S2a = 1500   # Stage-2a: long L-BFGS-B from defaults
    MAXITER_S2b = 1000   # Stage-2b: L-BFGS-B after Adam warm-up
    MAXITER_S2c = 1500   # Stage-2c: scaled L-BFGS-B

    FTOL = 1e-9   # tolerance-based stop enabled
    GTOL = 1e-7

    # Stage-1 perturbation specs: (seed, mag)
    PERTURB_SPECS = {
        "S1_C1": (42,  0.02),   # tight perturbation
        "S1_C2": (7,   0.05),   # medium perturbation
        "S1_C3": (99,  0.10),   # larger perturbation
    }

    if not _X64_ENABLED:
        result = {"job": RUN_JOB, "error": f"HV-X64: {_X64_ERROR}", "nan_halt": False}
    elif RUN_JOB == "S1_A":
        # Stage 1, start A: theta_CONOPT itself
        result = run_lbfgsb(theta_conopt_np, MAXITER_S1, ftol=FTOL, gtol=GTOL, label="S1_A")
    elif RUN_JOB in PERTURB_SPECS:
        seed, mag = PERTURB_SPECS[RUN_JOB]
        rng = np.random.default_rng(seed)
        noise = rng.normal(0.0, mag, size=len(PARAM_NAMES))
        theta0 = clip_to_bounds(theta_conopt_np * (1.0 + noise))
        result = run_lbfgsb(theta0, MAXITER_S1, ftol=FTOL, gtol=GTOL, label=RUN_JOB)
        result["perturb_seed"] = seed
        result["perturb_mag"]  = mag
    elif RUN_JOB == "S2a":
        # Stage 2a: long L-BFGS-B from defaults
        theta0 = clip_to_bounds(np.array([DEFAULTS_DICT[p] for p in PARAM_NAMES],
                                          dtype=np.float64))
        result = run_lbfgsb(theta0, MAXITER_S2a, ftol=FTOL, gtol=GTOL, label="S2a")
    elif RUN_JOB == "S2b":
        # Stage 2b: Adam warm-up -> L-BFGS-B from defaults
        theta0 = clip_to_bounds(np.array([DEFAULTS_DICT[p] for p in PARAM_NAMES],
                                          dtype=np.float64))
        result = run_adam_then_lbfgsb(theta0, adam_steps=500, adam_lr=1e-3,
                                       lbfgsb_maxiter=MAXITER_S2b,
                                       ftol=FTOL, gtol=GTOL, label="S2b")
    elif RUN_JOB == "S2c":
        # Stage 2c: parameter scaling -> L-BFGS-B from defaults -> invert
        # Scale = |theta_CONOPT|, with floor 1e-3
        scale = np.array([max(abs(theta_conopt_np[i]), 1e-3) for i in range(len(PARAM_NAMES))],
                          dtype=np.float64)
        theta0 = clip_to_bounds(np.array([DEFAULTS_DICT[p] for p in PARAM_NAMES],
                                          dtype=np.float64))
        result = run_scaled_lbfgsb(theta0, scale, MAXITER_S2c, ftol=FTOL, gtol=GTOL, label="S2c")
        result["scale"] = scale.tolist()
    else:
        result = {"job": RUN_JOB, "error": f"Unknown RUN_JOB={RUN_JOB!r}", "nan_halt": False}

    result["job"] = RUN_JOB

    with open(TMP_DIR / f"result_{RUN_JOB}.json", "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, cls=_NpEncoder)

    print(f"  [{RUN_JOB}] Result written.")
    sys.exit(0)


# ============================================================================
# ORCHESTRATOR MODE
# ============================================================================
import io, json, subprocess, time, datetime
from pathlib import Path
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO     = Path(__file__).resolve().parents[2].resolve()
PYTHON   = str(REPO / ".venv/Scripts/python.exe")
THIS     = str(Path(__file__).resolve())
TMP_DIR  = REPO / "scripts/pilot/_tmp_optdiag"
TMP_DIR.mkdir(exist_ok=True)
REPORT   = REPO / "Results/NC_pilot/JMP_NC_pilot_optimizer_protocol_diagnostic_report_v1.md"
ORACLE_LL = -16527.14218317334

STAGE1_JOBS = ["S1_A", "S1_C1", "S1_C2", "S1_C3"]
STAGE2_JOBS = ["S2a", "S2b", "S2c"]
ALL_JOBS    = STAGE1_JOBS + STAGE2_JOBS

print("=" * 70)
print("OPTIMIZER-PROTOCOL DIAGNOSTIC ORCHESTRATOR")
print("Authorization: docs/France_case/NC_pilot/design/JMP_NC_pilot_optimizer_multistart_design_memo_v1.md")
print("=" * 70)
print(f"Oracle LL: {ORACLE_LL}")
print(f"Jobs: {ALL_JOBS}")
print()

t_total_0 = time.time()
all_results = {}
job_times   = {}

for job in ALL_JOBS:
    print(f"--- Launching job {job} (subprocess) ---")
    env = {**os.environ, "RUN_JOB": job, "PYTHONIOENCODING": "utf-8"}
    t0 = time.time()
    proc = subprocess.run(
        [PYTHON, THIS], env=env, capture_output=False,
        timeout=7200,   # 2-hour watchdog per job
    )
    elapsed = time.time() - t0
    job_times[job] = elapsed
    print(f"  Job {job} finished in {elapsed:.1f}s  (exit={proc.returncode})")
    rfile = TMP_DIR / f"result_{job}.json"
    if rfile.exists():
        with open(rfile, encoding="utf-8") as fh:
            try:
                all_results[job] = json.load(fh)
            except Exception as e:
                all_results[job] = {"job": job, "error": f"JSON parse error: {e}"}
    else:
        all_results[job] = {"job": job, "error": "result file not found"}
    print()

total_wall = time.time() - t_total_0

# ============================================================================
# Analysis
# ============================================================================
AGREE_THRESH = 1e-2

def get_ll(job):
    r = all_results.get(job, {})
    return r.get("ll_final", None)

def get_term(job):
    r = all_results.get(job, {})
    return r.get("term_type", "UNKNOWN")

def get_converged(job):
    r = all_results.get(job, {})
    return r.get("opt_success", False)

# Stage 1 analysis
s1_lls = {j: get_ll(j) for j in STAGE1_JOBS if get_ll(j) is not None}
s1_converged = {j: get_converged(j) for j in STAGE1_JOBS}
s1_ll_vals = [v for v in s1_lls.values()]
s1_spread = (max(s1_ll_vals) - min(s1_ll_vals)) if len(s1_ll_vals) >= 2 else float("nan")
s1_agree = s1_spread < AGREE_THRESH if not np.isnan(s1_spread) else False
s1_any_converged = any(s1_converged.values())

# Stage 2 analysis — does B reach the Stage-1 basin?
s1_best_ll = max(s1_ll_vals) if s1_ll_vals else None
BASIN_TOL = 1.0   # within 1 LL unit of best S1 final = "reached basin"

s2_basin = {}
for job in STAGE2_JOBS:
    ll = get_ll(job)
    if ll is not None and s1_best_ll is not None:
        s2_basin[job] = (ll >= s1_best_ll - BASIN_TOL)
    else:
        s2_basin[job] = False

s2_any_reached = any(s2_basin.values())

# Stage-3: beta_l0_m verdict at first converged point
beta_l0m_verdict = "DEFERRED -- no tolerance-based stop achieved"
for job in STAGE1_JOBS + STAGE2_JOBS:
    r = all_results.get(job, {})
    if r.get("opt_success", False):
        diags = r.get("bh_diags", [])
        for d in diags:
            if d.get("param") == "beta_l0_m":
                beta_l0m_verdict = (f"[{job}] {d['verdict']}: {d['detail']}")
                break
        if "DEFERRED" not in beta_l0m_verdict:
            break

# ============================================================================
# Report writing
# ============================================================================
now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def fmt_ll(x):
    if x is None: return "ERROR"
    return f"{x:.8f}"

def fmt_term(job):
    t = get_term(job)
    r = all_results.get(job, {})
    nit = r.get("nit", "?")
    return f"{t} (nit={nit})"

def fmt_gnorm(job):
    r = all_results.get(job, {})
    v = r.get("gnorm_final", None)
    return f"{v:.6f}" if v is not None else "ERROR"

def iter_table(job, which="first"):
    r = all_results.get(job, {})
    key = "iter_log_first10" if which == "first" else "iter_log_last10"
    rows = r.get(key, [])
    if not rows:
        return "_No iteration log_"
    lines = ["| Iter | LL | ||g|| | per-iter (ms) |",
             "|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['iter']} | {row['ll']:.8f} | {row['grad_norm']:.6f} | {row['per_iter_s']*1000:.0f} |")
    return "\n".join(lines)

def bh_section(job):
    r = all_results.get(job, {})
    hits = r.get("bound_hits", [])
    diags = r.get("bh_diags", [])
    if not hits:
        return "No bound hits."
    lines = []
    for bh in hits:
        pname, side, bval, pval = bh
        lines.append(f"- `{pname}` at {side} bound {bval:.2e} (value={pval:.6e})")
    for d in diags:
        lines.append(f"  - **{d['param']}** verdict: **{d['verdict']}** -- {d['detail']}")
    return "\n".join(lines)

def error_section(job):
    r = all_results.get(job, {})
    err = r.get("error", None)
    if err:
        return f"**ERROR:** {err}"
    return ""

lines = []
lines.append("# JMP NC Pilot -- Optimizer-Protocol Diagnostic Report v1\n")
lines.append(f"*France RURO multi-year extension | v1 | {now_str}*\n")
lines.append("**Authorization:** `docs/France_case/NC_pilot/design/JMP_NC_pilot_optimizer_multistart_design_memo_v1.md` s22  ")
lines.append("**Script:** `scripts/pilot/_run_optimizer_protocol_diagnostic.py`  ")
lines.append(f"**Generated:** {now_str}\n")
lines.append("**SCOPE:** Staged optimizer-protocol diagnostic — NOT production, NOT verdict-grade. "
             "No winner picked; no estimate accepted; no SE/welfare/SA2/promotion.\n")
lines.append("**Architecture note:** Each job runs in an isolated subprocess (2-hour watchdog) "
             "to prevent XLA/JAX memory accumulation across many long runs. "
             "Reused validated v2/benchmark float64 JAX LL kernel; no logic change.\n")
lines.append("---\n")

# Section 1: Summary verdict
lines.append("## 1. Summary verdict\n")
lines.append(f"| Item | Value |")
lines.append("|---|---|")
lines.append(f"| Stage-1 LL spread (near-oracle starts) | {s1_spread:.4e} |")
lines.append(f"| Stage-1 basin agreement (< 0.01 threshold) | {'YES' if s1_agree else 'NO'} |")
lines.append(f"| Any Stage-1 start tolerance-converged | {'YES' if s1_any_converged else 'NO'} |")
lines.append(f"| Stage-2 any variant reached basin | {'YES' if s2_any_reached else 'NO'} |")
lines.append(f"| beta_l0_m verdict | {beta_l0m_verdict} |")

if s1_agree and s1_any_converged and s2_any_reached:
    verdict = "BUDGET/CONDITIONING ARTIFACT: all starts reach same basin under larger budget."
elif s1_agree and s1_any_converged and not s2_any_reached:
    verdict = "NEAR-ORACLE BASIN CONFIRMED; COLD-START RECOVERY FAILED -- escalate B protocol."
elif s1_agree and not s1_any_converged:
    verdict = "NEAR-ORACLE STARTS AGREE BUT NONE TOLERANCE-CONVERGED -- increase budget further."
elif not s1_agree:
    verdict = "NEAR-ORACLE STARTS DISAGREE AFTER LARGE BUDGET -- multimodality evidenced."
else:
    verdict = "UNDETERMINED -- check per-job details."

lines.append(f"| **Overall verdict** | **{verdict}** |\n")
lines.append("---\n")

# Section 2: Float64 confirmation
lines.append("## 2. Float64 confirmation\n")
lines.append("- `jax.config.update(\"jax_enable_x64\", True)` set at worker startup, before any JAX array.")
lines.append("- All pkl arrays cast to `jnp.float64`. JAX `value_and_grad` (JIT) in float64 throughout.\n")
lines.append("---\n")

# Section 3: Stage-1 results
lines.append("## 3. Stage-1 — Near-oracle basin test\n")
lines.append("**Starts:** theta_CONOPT (S1_A) + three small perturbations (S1_C1: seed=42 mag=0.02; "
             "S1_C2: seed=7 mag=0.05; S1_C3: seed=99 mag=0.10). maxiter=1500, ftol=1e-9, gtol=1e-7.\n")
lines.append("| Job | Start description | Initial LL | Final LL | Term type | nit | |g|_final | ||dth||_CONOPT | Wall(s) |")
lines.append("|---|---|---|---|---|---|---|---|---|")
s1_descs = {"S1_A": "theta_CONOPT", "S1_C1": "perturbed(seed=42,mag=0.02)",
            "S1_C2": "perturbed(seed=7,mag=0.05)", "S1_C3": "perturbed(seed=99,mag=0.10)"}
for job in STAGE1_JOBS:
    r = all_results.get(job, {})
    lines.append(
        f"| {job} | {s1_descs[job]} | {fmt_ll(r.get('ll_start'))} | {fmt_ll(r.get('ll_final'))} "
        f"| {fmt_term(job)} | {r.get('nit','?')} | {fmt_gnorm(job)} "
        f"| {r.get('norm_dtheta_conopt', float('nan')):.4e} | {job_times.get(job,0):.1f} |"
    )

lines.append(f"\n**LL spread across S1 starts:** {s1_spread:.6e}  "
             f"(threshold: {AGREE_THRESH:.0e})")
lines.append(f"**Basin agreement verdict:** {'PASS -- starts agree' if s1_agree else 'FAIL -- starts disagree'}\n")

for job in STAGE1_JOBS:
    lines.append(f"### {job} bound-hit diagnostics\n")
    lines.append(bh_section(job))
    err = error_section(job)
    if err: lines.append(f"\n{err}")
    lines.append("")

lines.append("### Stage-1 iteration logs (first/last 10)\n")
for job in STAGE1_JOBS:
    lines.append(f"**{job} — first 10 iterations:**\n")
    lines.append(iter_table(job, "first"))
    lines.append(f"\n**{job} — last 10 iterations:**\n")
    lines.append(iter_table(job, "last"))
    lines.append("")
lines.append("---\n")

# Section 4: Stage-2
lines.append("## 4. Stage-2 — Cold-start recovery test (defaults)\n")
lines.append("| Job | Method | Initial LL | Final LL | Term type | nit | |g|_final | Reached basin? | Wall(s) |")
lines.append("|---|---|---|---|---|---|---|---|---|")
s2_descs = {"S2a": "Long L-BFGS-B (maxiter=1500)",
            "S2b": "Adam(500 steps)->L-BFGS-B (maxiter=1000)",
            "S2c": "Scaled L-BFGS-B (maxiter=1500)"}
for job in STAGE2_JOBS:
    r = all_results.get(job, {})
    reached = "YES" if s2_basin.get(job, False) else "NO"
    lines.append(
        f"| {job} | {s2_descs[job]} | {fmt_ll(r.get('ll_start'))} | {fmt_ll(r.get('ll_final'))} "
        f"| {fmt_term(job)} | {r.get('nit','?')} | {fmt_gnorm(job)} "
        f"| {reached} | {job_times.get(job,0):.1f} |"
    )

lines.append(f"\n**Basin threshold used:** within {BASIN_TOL:.1f} LL unit of best Stage-1 final LL "
             f"({fmt_ll(s1_best_ll)})")
lines.append(f"**Cold-start recovery verdict:** "
             f"{'PASS -- at least one variant reached the basin' if s2_any_reached else 'FAIL -- no variant reached the basin'}\n")

for job in STAGE2_JOBS:
    lines.append(f"### {job} bound-hit diagnostics\n")
    lines.append(bh_section(job))
    err = error_section(job)
    if err: lines.append(f"\n{err}")
    lines.append("")

lines.append("### Stage-2 iteration logs (first/last 10)\n")
for job in STAGE2_JOBS:
    lines.append(f"**{job} — first 10 iterations:**\n")
    lines.append(iter_table(job, "first"))
    lines.append(f"\n**{job} — last 10 iterations:**\n")
    lines.append(iter_table(job, "last"))
    lines.append("")
lines.append("---\n")

# Section 5: Stage-3
lines.append("## 5. Stage-3 -- beta_l0_m verdict\n")
lines.append(f"**Verdict:** {beta_l0m_verdict}\n")
lines.append("> HV-ECON: No economic interpretation regardless of verdict. "
             "If corner is confirmed at a converged point, a specification review "
             "is required before any economic interpretation.\n")
lines.append("---\n")

# Section 6: Runtime
lines.append("## 6. Runtime\n")
lines.append("| Job | Wall time (s) | Term type |")
lines.append("|---|---|---|")
for job in ALL_JOBS:
    lines.append(f"| {job} | {job_times.get(job,0):.1f} | {get_term(job)} |")
lines.append(f"| **Total** | **{total_wall:.1f}** | -- |\n")
lines.append("---\n")

# Section 7: What was not executed
lines.append("## 7. What was not executed\n")
lines.append("- No CONOPT run. No GAMSPy estimation.\n"
             "- No Hessian. No SEs. No cluster-robust SEs.\n"
             "- No welfare. No SA2. No pilot promotion. No M1-clean displacement.\n"
             "- No 40x40 product set. No pooled/singles. No P3a rebuild.\n"
             "- Prior reports, oracle JSONs, pkl, and all production/pilot data: NOT modified.\n"
             "- No winner picked; no estimate accepted; no economic interpretation.\n")
lines.append("---\n")

# Section 8: Required final statements
lines.append("## Required Final Statements\n")
lines.append("- **Diagnostic optimizer-protocol run only** -- staged (Stage 1: near-oracle basin test; "
             "Stage 2: cold-start recovery). NOT production, NOT verdict-grade.\n"
             "- **No winner is picked** from any stage; no start is accepted as an estimate.\n"
             "- **float64 mandatory** (`jax_enable_x64=True` before any array); JAX `value_and_grad` "
             "(JIT) throughout each subprocess.\n"
             "- **`beta_l0_m` NOT interpreted economically.** Corner-vs-transient verdict reported "
             "at tolerance-converged points only (if none converged: deferred).\n"
             "- **Same model, data, bounds as pilot CONOPT spec.** `theta_c` FIXED at 0.0. "
             "No formula/data/bound changes.\n"
             "- **No Hessian/SE, welfare, SA2, or promotion.** No scaling-up. No denser product.\n"
             "- **Prior reports, oracle JSONs, pkl, and all production/pilot data: UNMODIFIED.**\n"
             "- **M1-clean 2016 remains the active baseline.** Corrected pooled P3a unaffected.\n"
             "- NC pilot not promoted.\n")
lines.append("---\n")
lines.append("*Status: optimizer-protocol diagnostic v1. Staged diagnostic; no estimate accepted; "
             "no inference/welfare/SA2/promotion. M1-clean 2016 active.*\n")

REPORT.write_text("\n".join(lines), encoding="utf-8")
print(f"Report written: {REPORT}")
print(f"Total wall time: {total_wall:.1f} s")
print("DONE. No Hessian, SE, welfare, SA2, or promotion.")
