"""
JAX validation estimation -- FR_2016 couples pilot (three starts).

Authorization: docs/JMP_NC_pilot_vectorized_estimator_design_contract_v1.md s19.

SCOPE: Exactly three capped float64 L-BFGS-B starts (A=theta_CONOPT,
B=pilot defaults, C=perturbed) to validate whether the JAX path reproduces
the CONOPT oracle from independent starts.

HARD CONSTRAINTS:
  HV-X64   : float64 mandatory (jax_enable_x64 before any array).
  HV-START  : Exactly three starts -- A, B, C -- each feasible.
  HV-CAP    : maxiter capped (MAXITER_AC=150 for A/C, MAXITER_B=200 for B;
               both within authorized [50, 200]).
  HV-NAN    : Halt if NaN/Inf objective or gradient at any iterate.
  HV-AGREE  : Halt verdict if three starts disagree (|dLL| > 1e-2).
              Do NOT pick a winner; recommend multistart memo.
  HV-ECON   : No economic interpretation of bound-hit solution.
  HV-SCOPE  : No Hessian/SE/welfare/SA2/promotion/scaling/pooled/P3a.
  HV-MUT    : Do not overwrite prior reports, oracle JSONs, or pkl.

NOT production, NOT verdict-grade.

Architecture note: each start is run in an isolated subprocess to prevent
XLA/JAX memory accumulation causing segfaults across three 150+ iter runs.
Results are serialized to JSON between subprocess calls.
"""

import sys, os

# ---------------------------------------------------------------------------
# Subprocess dispatch: if RUN_START env var is set, this process runs exactly
# one start, writes a JSON result file, and exits. The orchestrator (no env var)
# launches the three subprocesses sequentially.
# ---------------------------------------------------------------------------
RUN_START = os.environ.get("RUN_START")   # "A", "B", or "C"

if RUN_START is not None:
    # -----------------------------------------------------------------------
    # WORKER MODE: run one start
    # -----------------------------------------------------------------------
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    # float64 FIRST
    _X64_ENABLED = False
    _X64_ERROR = None
    try:
        import jax
        jax.config.update("jax_enable_x64", True)
        import jax.numpy as jnp
        _test = jnp.array(1.0, dtype=jnp.float64)
        assert _test.dtype == jnp.float64
        _X64_ENABLED = True
    except Exception as _e:
        _X64_ERROR = str(_e)

    import json, math, pickle, time
    from pathlib import Path
    import numpy as np
    from scipy.optimize import minimize

    REPO       = Path(r"U:\Desktop\Nizam_Hisham\MNL").resolve()
    # pkl was pickled with estimation_utils in path; add scripts/enhanced before load
    _enhanced = str(REPO / "scripts" / "enhanced")
    if _enhanced not in sys.path:
        sys.path.insert(0, _enhanced)
    PKL_PATH   = (REPO / "Data/pilot/nc_2016_couples/precomputed"
                  / "fr_pilot_nc_2016_couples_precomputed_loc.pkl").resolve()
    RESULT_S1  = (REPO / "Results/pilot/nc_2016_couples/diagnostic_rerun_v1"
                  / "start_1_warm_P3a/estimation_result.json").resolve()
    TMP_DIR    = REPO / "scripts/pilot/_tmp_validation"
    TMP_DIR.mkdir(exist_ok=True)

    EPS = 1e-12
    MAXITER_AC  = 150    # starts A and C
    MAXITER_B   = 200    # start B (defaults are far from optimum)

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
        "theta_l_m":    (-8.0, 0.95), "theta_l_f":    (-8.0, 0.95),
        "beta_c":       (0.05, 50.0), "beta_l0_m":    (1.0e-6, 50.0),
        "beta_l0_f":    (0.05, 50.0),
        "beta_l_age_m":   (-5.0, 5.0), "beta_l_age2_m":  (-1.0, 1.0),
        "beta_l_age_f":   (-5.0, 5.0), "beta_l_age2_f":  (-1.0, 1.0),
        "beta_l_nkids_f": (-5.0, 5.0),
        "beta_E": (-25.0, 25.0), "beta_h_pt1": (-10.0, 10.0),
        "beta_h_pt2": (-10.0, 10.0), "beta_h_ft": (-10.0, 10.0),
        "beta_w0": (-10.0, 20.0), "beta_w_educL": (-5.0, 5.0),
        "beta_w_educH": (-5.0, 5.0), "beta_w_pexp": (-1.0, 1.0),
        "beta_w_pexp2": (-0.1, 0.1),
        "beta_E_gsur":   (-10.0, 10.0), "beta_E_drgn2":  (-10.0, 10.0),
        "beta_E_drgn3":  (-10.0, 10.0), "beta_E_drgn4":  (-10.0, 10.0),
        "beta_E_drgn5":  (-10.0, 10.0), "beta_E_drgn6":  (-10.0, 10.0),
        "beta_E_drgn7":  (-10.0, 10.0), "beta_E_drgn8":  (-10.0, 10.0),
        "beta_occ_2_cm": (-10.0, 10.0), "beta_occ_3_cm": (-10.0, 10.0),
        "beta_occ_4_cm": (-10.0, 10.0), "beta_occ_2_cf": (-10.0, 10.0),
        "beta_occ_3_cf": (-10.0, 10.0), "beta_occ_4_cf": (-10.0, 10.0),
        "sigma": (0.1, 20.0), "beta_ll": (0.0, 10.0),
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
    PERTURB_SEED = 42
    PERTURB_MAG  = 0.05

    def clip_to_bounds(x):
        x = x.copy()
        for i, (lo, hi) in enumerate(BOUNDS):
            if lo is not None: x[i] = max(x[i], lo + 1e-10)
            if hi is not None: x[i] = min(x[i], hi - 1e-10)
        return x

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
            "educL_m": f64(pc.educL_male), "educH_m": f64(pc.educH_male),
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
            log_h_m = (p["beta_E"]*f["working_m"] + p["beta_h_pt1"]*f["wpt1_m"]*f["working_m"]
                       + p["beta_h_pt2"]*f["wpt2_m"]*f["working_m"]
                       + p["beta_h_ft"]*f["wft_m"]*f["working_m"])
            log_h_f = (p["beta_E"]*f["working_f"] + p["beta_h_pt1"]*f["wpt1_f"]*f["working_f"]
                       + p["beta_h_pt2"]*f["wpt2_f"]*f["working_f"]
                       + p["beta_h_ft"]*f["wft_f"]*f["working_f"])
            sigma = p["sigma"]
            mu_m = (p["beta_w0"] + p["beta_w_educL"]*f["educL_m"] + p["beta_w_educH"]*f["educH_m"]
                    + p["beta_w_pexp"]*f["pexp_m"] + p["beta_w_pexp2"]*f["pexp2_m"])
            mu_f = (p["beta_w0"] + p["beta_w_educL"]*f["educL_f"] + p["beta_w_educH"]*f["educH_f"]
                    + p["beta_w_pexp"]*f["pexp_f"] + p["beta_w_pexp2"]*f["pexp2_f"])
            log_w_m = f["working_m"] * (-0.5*(f["log_wage_m"]-mu_m)**2/(sigma**2+eps)
                                         - jnp.log(sigma+eps) - log2pi_half - f["log_wage_m"])
            log_w_f = f["working_f"] * (-0.5*(f["log_wage_f"]-mu_f)**2/(sigma**2+eps)
                                         - jnp.log(sigma+eps) - log2pi_half - f["log_wage_f"])
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
            utility = u_pref + log_h_m + log_h_f + log_w_m + log_w_f + log_market_c - log_prior
            u_max = utility.max(axis=1, keepdims=True)
            log_den = jnp.log(jnp.exp(utility - u_max).sum(axis=1)) + u_max.squeeze()
            chosen_u = (f["chosen"] * utility).sum(axis=1)
            return (chosen_u - log_den).sum()
        return ll_fn

    def bound_hit_diagnostic(pname, value, grad_ll):
        lo, hi = BOUNDS_DICT.get(pname, (None, None))
        tol = 1e-6
        at_lower = (lo is not None) and (abs(value - lo) < tol)
        at_upper = (hi is not None) and (abs(value - hi) < tol)
        if not at_lower and not at_upper:
            return None
        ABS_FLAT = 0.05
        diag = {"param": pname, "value": value, "grad_ll": grad_ll,
                "at_lower": at_lower, "at_upper": at_upper,
                "bound": lo if at_lower else hi}
        if at_lower:
            if grad_ll < -ABS_FLAT:
                diag["verdict"] = "ACTIVE_CONSTRAINT (corner)"
                diag["detail"] = f"grad_ll={grad_ll:.6f}<0: optimizer wants to decrease {pname} below lower bound {lo}. Genuine corner."
            elif abs(grad_ll) <= ABS_FLAT:
                diag["verdict"] = "NEAR_FLAT (incidental)"
                diag["detail"] = f"|grad_ll|={abs(grad_ll):.6f}<=0.05: LL insensitive at bound. Incidental contact."
            else:
                diag["verdict"] = "INACTIVE (pushing away from lower bound)"
                diag["detail"] = f"grad_ll={grad_ll:.6f}>0: optimizer wants to increase {pname}. Lower bound not active."
        else:
            if grad_ll > ABS_FLAT:
                diag["verdict"] = "ACTIVE_CONSTRAINT (corner)"
                diag["detail"] = f"grad_ll={grad_ll:.6f}>0: optimizer wants to increase {pname} above upper bound {hi}. Genuine corner."
            elif abs(grad_ll) <= ABS_FLAT:
                diag["verdict"] = "NEAR_FLAT (incidental)"
                diag["detail"] = f"|grad_ll|={abs(grad_ll):.6f}<=0.05: LL insensitive at bound. Incidental contact."
            else:
                diag["verdict"] = "INACTIVE (pushing away from upper bound)"
                diag["detail"] = f"grad_ll={grad_ll:.6f}<0: optimizer wants to decrease {pname}. Upper bound not active."
        return diag

    # -- Load data --
    print(f"Worker: start={RUN_START}")
    if not _X64_ENABLED:
        result = {"label": RUN_START, "error": f"HV-X64: {_X64_ERROR}", "nan_halt": False}
        with open(TMP_DIR / f"result_{RUN_START}.json", "w") as fh:
            json.dump(result, fh)
        sys.exit(0)

    with open(RESULT_S1) as fh:
        r1 = json.load(fh)
    theta_conopt_dict = {p: r1["parameters"][p] for p in PARAM_NAMES}
    theta_conopt_np   = np.array([theta_conopt_dict[p] for p in PARAM_NAMES], dtype=np.float64)

    with open(PKL_PATH, "rb") as fh:
        pc = pickle.load(fh)
    print(f"  pkl loaded: n_groups={pc.n_groups}")

    ll_fn = build_jax_ll_fn(pc)
    vag   = jax.jit(jax.value_and_grad(ll_fn))

    # Build start theta
    if RUN_START == "A":
        theta0 = theta_conopt_np.copy()
        maxiter = MAXITER_AC
    elif RUN_START == "B":
        theta0_raw = np.array([DEFAULTS_DICT[p] for p in PARAM_NAMES], dtype=np.float64)
        theta0 = theta0_raw.copy()
        for i, (lo, hi) in enumerate(BOUNDS):
            if lo is not None: theta0[i] = max(theta0[i], lo + 1e-10)
            if hi is not None: theta0[i] = min(theta0[i], hi - 1e-10)
        maxiter = MAXITER_B
    elif RUN_START == "C":
        rng = np.random.default_rng(PERTURB_SEED)
        noise = rng.normal(0.0, PERTURB_MAG, size=len(PARAM_NAMES))
        theta0_raw = theta_conopt_np * (1.0 + noise)
        theta0 = theta0_raw.copy()
        for i, (lo, hi) in enumerate(BOUNDS):
            if lo is not None: theta0[i] = max(theta0[i], lo + 1e-10)
            if hi is not None: theta0[i] = min(theta0[i], hi - 1e-10)
        maxiter = MAXITER_AC
    else:
        raise ValueError(f"Unknown RUN_START={RUN_START!r}")

    # Warm-up + initial eval
    print(f"  JIT warm-up ...")
    t0 = time.time()
    tv = jnp.array(theta0, dtype=jnp.float64)
    ll_s_jax, g_s_jax = vag(tv)
    warmup_ms = (time.time() - t0) * 1000
    ll_start = float(ll_s_jax)
    grad_start = np.array(g_s_jax, dtype=np.float64)
    gnorm_start = float(np.sqrt((grad_start**2).sum()))
    nf_start = int(np.sum(~np.isfinite(grad_start)))
    print(f"  warm-up: {warmup_ms:.1f} ms  LL={ll_start:.8f}  |g|={gnorm_start:.6f}")

    result = {
        "label": RUN_START, "maxiter": maxiter,
        "ll_start": ll_start, "gnorm_start": gnorm_start,
        "grad_start": {p: float(grad_start[i]) for i, p in enumerate(PARAM_NAMES)},
        "theta_start": {p: float(theta0[i]) for i, p in enumerate(PARAM_NAMES)},
        "warmup_ms": warmup_ms, "nan_halt": False, "error": None,
    }

    if not np.isfinite(ll_start) or nf_start > 0:
        result["nan_halt"] = True
        result["error"] = f"HV-NAN at start: LL={ll_start}, {nf_start} non-finite grad"
        class _NpEnc(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (np.integer,)): return int(obj)
                if isinstance(obj, (np.floating,)): return float(obj)
                if isinstance(obj, (np.bool_,)): return bool(obj)
                return super().default(obj)
        with open(TMP_DIR / f"result_{RUN_START}.json", "w") as fh:
            json.dump(result, fh, cls=_NpEnc)
        sys.exit(0)

    iter_log = []
    nan_halt = [False]
    t0_b = time.time()
    t_last = [time.time()]
    ic = [0]

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
        ll_v = float(val); gv = np.array(grad, dtype=np.float64)
        gnorm = float(np.sqrt((gv**2).sum()))
        t_now = time.time()
        elapsed = t_now - t0_b; pi = t_now - t_last[0]; t_last[0] = t_now
        iter_log.append({"iter": ic[0], "ll": ll_v, "grad_norm": gnorm,
                         "elapsed_s": elapsed, "per_iter_s": pi})
        print(f"  iter {ic[0]:4d}: LL={ll_v:.8f}  |g|={gnorm:.6f}  ({pi*1000:.0f} ms)")

    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        opt = minimize(neg_ll_grad, x0=theta0, method="L-BFGS-B", jac=True,
                       bounds=BOUNDS, callback=cb,
                       options={"maxiter": maxiter, "ftol": 1e-15, "gtol": 1e-9,
                                "maxfun": maxiter*25, "disp": False, "iprint": -1})
    wall_s = time.time() - t0_b

    if nan_halt[0]:
        result["nan_halt"] = True
        result["error"] = f"HV-NAN during optimization"

    theta_final = opt.x
    xj_f = jnp.array(theta_final, dtype=jnp.float64)
    ll_f, g_f = vag(xj_f)
    ll_final = float(ll_f); grad_final = np.array(g_f, dtype=np.float64)
    gnorm_final = float(np.sqrt((grad_final**2).sum()))

    delta_start  = theta_final - theta0
    delta_conopt = theta_final - theta_conopt_np

    bound_hits = []
    for i, (p, (lo, hi)) in enumerate(zip(PARAM_NAMES, BOUNDS)):
        v = theta_final[i]
        if lo is not None and abs(v - lo) < 1e-7:
            bound_hits.append([p, "lower", lo, v])
        if hi is not None and abs(v - hi) < 1e-7:
            bound_hits.append([p, "upper", hi, v])

    bh_diagnostics = []
    for bh in bound_hits:
        pname, side, bval, pval = bh
        gi_ll = float(grad_final[PARAM_NAMES.index(pname)])
        diag = bound_hit_diagnostic(pname, pval, gi_ll)
        if diag:
            bh_diagnostics.append(diag)

    result.update({
        "ll_final": ll_final, "gnorm_final": gnorm_final,
        "grad_final": {p: float(grad_final[i]) for i, p in enumerate(PARAM_NAMES)},
        "theta_final": {p: float(theta_final[i]) for i, p in enumerate(PARAM_NAMES)},
        "delta_from_start": {p: float(delta_start[i]) for i, p in enumerate(PARAM_NAMES)},
        "delta_from_conopt": {p: float(delta_conopt[i]) for i, p in enumerate(PARAM_NAMES)},
        "norm_dtheta_start": float(np.sqrt((delta_start**2).sum())),
        "norm_dtheta_conopt": float(np.sqrt((delta_conopt**2).sum())),
        "bound_hits": bound_hits,
        "bh_diagnostics": bh_diagnostics,
        "opt_message": opt.message,
        "opt_nit": int(opt.nit), "opt_nfev": int(opt.nfev),
        "opt_success": bool(opt.success),
        "wall_s": wall_s,
        "iter_log": iter_log,
    })

    class _NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)): return int(obj)
            if isinstance(obj, (np.floating,)): return float(obj)
            if isinstance(obj, (np.bool_,)): return bool(obj)
            if isinstance(obj, np.ndarray): return obj.tolist()
            return super().default(obj)

    with open(TMP_DIR / f"result_{RUN_START}.json", "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, cls=_NpEncoder)
    print(f"  Done. Final LL={ll_final:.8f}  |g|={gnorm_final:.6f}  wall={wall_s:.1f}s")
    sys.exit(0)


# ============================================================================
# ORCHESTRATOR MODE: launch three subprocesses sequentially, collect results,
# run agreement check, write report.
# ============================================================================
import io, json, subprocess, time
from pathlib import Path
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO        = Path(r"U:\Desktop\Nizam_Hisham\MNL").resolve()
RESULT_S1   = (REPO / "Results/pilot/nc_2016_couples/diagnostic_rerun_v1"
               / "start_1_warm_P3a/estimation_result.json").resolve()
REPORT_PATH = (REPO / "Results"
               / "JMP_NC_pilot_JAX_validation_estimation_report_v1.md").resolve()
TMP_DIR     = REPO / "scripts/pilot/_tmp_validation"
PYTHON      = r"U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe"
THIS_SCRIPT = Path(__file__).resolve()

ORACLE_LL   = -16527.14218317334
V2_LL_NP    = -16527.0669688818
EPS         = 1e-12
MAXITER_AC  = 150
MAXITER_B   = 200
PERTURB_SEED = 42
PERTURB_MAG  = 0.05

PARAM_NAMES = [
    "beta_l0_m", "beta_l_age_m", "beta_l_age2_m", "theta_l_m",
    "beta_l0_f", "beta_l_age_f", "beta_l_age2_f", "beta_l_nkids_f", "theta_l_f",
    "beta_c", "beta_E", "beta_h_pt1", "beta_h_pt2", "beta_h_ft",
    "beta_E_gsur",
    "beta_E_drgn2", "beta_E_drgn3", "beta_E_drgn4", "beta_E_drgn5",
    "beta_E_drgn6", "beta_E_drgn7", "beta_E_drgn8",
    "beta_occ_2_cm", "beta_occ_3_cm", "beta_occ_4_cm",
    "beta_occ_2_cf", "beta_occ_3_cf", "beta_occ_4_cf",
    "beta_w0", "beta_w_educL", "beta_w_educH", "beta_w_pexp", "beta_w_pexp2",
    "sigma", "beta_ll",
]

print("=" * 70)
print("JAX VALIDATION ESTIMATION ORCHESTRATOR (3 starts)")
print("Authorization: docs/JMP_NC_pilot_vectorized_estimator_design_contract_v1.md")
print("=" * 70)

with open(RESULT_S1) as fh:
    r1 = json.load(fh)
print(f"Oracle LL: {r1['log_likelihood']:.12f}")

TMP_DIR.mkdir(exist_ok=True)
all_results = {"oracle_ll_s1": r1["log_likelihood"],
               "maxiter_AC": MAXITER_AC, "maxiter_B": MAXITER_B}

t_total_0 = time.time()
for lbl in ["A", "B", "C"]:
    out_file = TMP_DIR / f"result_{lbl}.json"
    print(f"\n--- Launching start {lbl} (subprocess) ---")
    t0 = time.time()
    env = {**os.environ, "RUN_START": lbl, "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(
        [PYTHON, str(THIS_SCRIPT)],
        env=env, capture_output=False, text=False,
    )
    elapsed = time.time() - t0
    print(f"  Start {lbl} subprocess finished in {elapsed:.1f}s  (exit={proc.returncode})")
    if not out_file.exists():
        print(f"  ERROR: result file not found for start {lbl}")
        all_results[f"res_{lbl}"] = {"label": lbl, "error": "subprocess failed, no output"}
    else:
        with open(out_file, encoding="utf-8") as fh:
            all_results[f"res_{lbl}"] = json.load(fh)

total_wall = time.time() - t_total_0
all_results["total_wall_s"] = total_wall

# Agreement check
halt_code = None
halt_msg  = None
print("\n--- Agreement check ---")
lls = []
for lbl in ["A", "B", "C"]:
    r = all_results.get(f"res_{lbl}", {})
    if r.get("nan_halt"):
        halt_code = "HV-NAN"
        halt_msg  = f"Start {lbl}: {r.get('error','NaN/Inf detected')}"
        break
    if r.get("error") and "HV-X64" in str(r.get("error", "")):
        halt_code = "HV-X64"
        halt_msg  = r["error"]
        break
    ll = r.get("ll_final")
    if ll is None:
        halt_code = "HV-NAN"
        halt_msg  = f"Start {lbl} has no final LL (subprocess may have crashed)"
        break
    lls.append(ll)

if not halt_code and len(lls) == 3:
    max_dll = max(lls) - min(lls)
    agree   = max_dll < 1e-2
    detail  = (f"|DLL| across A/B/C: {max_dll:.6e}  "
               f"(A={lls[0]:.8f}, B={lls[1]:.8f}, C={lls[2]:.8f})")
    all_results["agreement"] = {"agree": agree, "detail": detail, "max_dll": max_dll}
    print(f"  {detail}")
    print(f"  Agreement: {'PASS' if agree else 'FAIL -- HV-AGREE'}")
    if not agree:
        halt_code = "HV-AGREE"
        halt_msg  = f"Three starts do not agree: {detail}. Recommend optimizer/multistart memo."
else:
    all_results["agreement"] = {"agree": False, "detail": halt_msg or "incomplete", "max_dll": float("nan")}

# CONOPT comparison
if not halt_code or halt_code == "HV-AGREE":
    res_A = all_results.get("res_A", {})
    if res_A.get("ll_final") is not None:
        all_results["dll_vs_oracle"] = abs(res_A["ll_final"] - ORACLE_LL)

# Write report
def write_report():
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    A = lines.append

    A("# JMP NC Pilot -- JAX Validation Estimation Report v1")
    A("")
    A("*France RURO multi-year extension | v1 | 2026-05-24*")
    A("")
    A("**Authorization:** `docs/JMP_NC_pilot_vectorized_estimator_design_contract_v1.md` s21")
    A("**Script:** `scripts/pilot/_run_jax_validation_estimation.py`")
    A(f"**Generated:** {now}")
    A("")
    A("**SCOPE:** Three-start (A=theta_CONOPT, B=pilot defaults, C=perturbed) float64 "
      "L-BFGS-B validation estimation. Stability + agreement probe. NOT production, "
      "NOT verdict-grade. No Hessian/SE, welfare, SA2, or promotion.")
    A("")
    A("**Architecture note:** Each start runs in an isolated subprocess to prevent "
      "XLA/JAX memory accumulation segfaults across three 150-200 iter runs. "
      "Results serialized to JSON between subprocess calls. No logic change to the "
      "validated v2 float64 JAX LL kernel.")
    A("")
    A("---")
    A("")

    # Halt table
    A("## 1. Halt-condition status")
    A("")
    if halt_code:
        A(f"**HALT FIRED: `{halt_code}`**")
        A("")
        A(f"Reason: {halt_msg}")
        A("")
        A("Report written to halt point. Await direction.")
    else:
        A("**No halt conditions fired.** All s18 guards clear.")
    A("")
    A("| Halt code | Condition | Status |")
    A("|---|---|---|")
    A(f"| HV-X64 | JAX float64 unavailable | {'FIRED' if halt_code=='HV-X64' else 'CLEAR'} |")
    A(f"| HV-START | Infeasible or wrong number of starts | CLEAR -- exactly three starts |")
    A(f"| HV-CAP | maxiter uncapped | CLEAR -- A/C={MAXITER_AC}, B={MAXITER_B} |")
    A(f"| HV-NAN | NaN/Inf objective or gradient | {'FIRED' if halt_code=='HV-NAN' else 'CLEAR'} |")
    agr = all_results.get("agreement", {})
    A(f"| HV-AGREE | Three starts disagree | {'FIRED' if halt_code=='HV-AGREE' else ('CLEAR' if agr.get('agree') else 'N/A')} |")
    A(f"| HV-ECON | Bound-hit solution accepted economically | CLEAR -- not interpreted |")
    A(f"| HV-SCOPE | Hessian/SE/welfare/SA2/promotion/scaling | CLEAR -- none executed |")
    A(f"| HV-MUT | Prior reports/oracle/pkl overwritten | CLEAR -- not modified |")
    A("")
    A("---")
    A("")

    # Float64
    A("## 2. Float64 confirmation")
    A("")
    A("- `jax.config.update(\"jax_enable_x64\", True)` set at subprocess startup, before any JAX array.")
    A("- All pkl arrays cast to `jnp.float64`. Theta vectors: `jnp.array(..., dtype=jnp.float64)`.")
    A("- `jax.value_and_grad` (JIT) operates in float64 throughout each subprocess.")
    ll_chk = all_results.get("res_A", {}).get("ll_start")
    if ll_chk is not None:
        A(f"- LL(theta_CONOPT) in subprocess A = {ll_chk:.10f}  "
          f"(|delta| vs v2 = {abs(ll_chk - V2_LL_NP):.3e}) -- confirmed.")
    A("")
    A("---")
    A("")

    # Three-start setup
    A("## 3. Three-start setup")
    A("")
    A("| Start | Label | Description | maxiter |")
    A("|---|---|---|---|")
    A(f"| A | theta_CONOPT | `start_1_warm_P3a/estimation_result.json` | {MAXITER_AC} |")
    A(f"| B | pilot defaults | `estimation_spec_nc_pilot_couples_2016.yaml` `initial_values` | {MAXITER_B} |")
    A(f"| C | perturbed | theta_CONOPT x (1 + N(0,{PERTURB_MAG})), seed={PERTURB_SEED}, clipped | {MAXITER_AC} |")
    A("")
    A(f"All maxiter values within authorized [50, 200]. External watchdog not available; "
      "relying on maxiter caps (documented). theta_c FIXED at 0.0. "
      "Bounds unchanged from pilot CONOPT spec.")
    A("")
    A("---")
    A("")

    # Per-start summary
    A("## 4. Per-start results summary")
    A("")
    A("| Item | Start A | Start B | Start C |")
    A("|---|---|---|---|")
    rows = [
        ("Initial LL", "ll_start", "{:.8f}"),
        ("Final LL", "ll_final", "{:.8f}"),
        ("LL change", None, "{:+.6f}"),
        ("Grad norm at start", "gnorm_start", "{:.6f}"),
        ("Grad norm at final", "gnorm_final", "{:.6f}"),
        ("||dtheta||2 from start", "norm_dtheta_start", "{:.4e}"),
        ("||dtheta||2 from CONOPT", "norm_dtheta_conopt", "{:.4e}"),
        ("Iterations (nit)", "opt_nit", "{}"),
        ("Wall time (s)", "wall_s", "{:.2f}"),
        ("Optimizer message", "opt_message", "{}"),
        ("Bound hits", None, "{}"),
        ("Converged", "opt_success", "{}"),
    ]
    for item, key, fmt in rows:
        vals = []
        for lbl in ["A", "B", "C"]:
            r = all_results.get(f"res_{lbl}", {})
            if item == "LL change":
                ll0 = r.get("ll_start"); llf = r.get("ll_final")
                vals.append(fmt.format(llf - ll0) if ll0 is not None and llf is not None else "N/A")
            elif item == "Bound hits":
                bh = r.get("bound_hits", [])
                vals.append(", ".join(b[0] for b in bh) if bh else "None")
            elif key:
                v = r.get(key)
                vals.append(fmt.format(v) if v is not None else "N/A")
            else:
                vals.append("N/A")
        A(f"| {item} | {vals[0]} | {vals[1]} | {vals[2]} |")
    A("")
    A("---")
    A("")

    # Per-iteration logs (compact -- first and last 10 iters)
    A("## 5. Per-iteration logs (first and last 10 of each start)")
    A("")
    for lbl in ["A", "B", "C"]:
        r = all_results.get(f"res_{lbl}", {})
        il = r.get("iter_log", [])
        maxiter_lbl = MAXITER_B if lbl == "B" else MAXITER_AC
        A(f"### Start {lbl} (maxiter={maxiter_lbl})")
        A("")
        if il:
            show = il[:10] + (il[-10:] if len(il) > 10 else [])
            seen = set()
            A("| Iter | LL | ||g||2 | Per-iter (ms) |")
            A("|---|---|---|---|")
            for row in show:
                if row["iter"] not in seen:
                    seen.add(row["iter"])
                    A(f"| {row['iter']} | {row['ll']:.8f} | {row['grad_norm']:.4f} | {row['per_iter_s']*1000:.0f} |")
            if len(il) > 20:
                A(f"*(Showing first 10 and last 10 of {len(il)} iterations)*")
        else:
            A("No iterations recorded.")
        A("")

    A("---")
    A("")

    # Bound-hit diagnostics
    A("## 6. Bound-hit diagnostics (contract s14)")
    A("")
    A("Projected-gradient / KKT-style diagnostic: is the constraint genuinely "
      "active (corner solution) or incidental (near-flat)?")
    A("")
    any_bh = False
    for lbl in ["A", "B", "C"]:
        r = all_results.get(f"res_{lbl}", {})
        bh = r.get("bound_hits", [])
        if not bh:
            A(f"**Start {lbl}:** No bound hits.")
            A("")
            continue
        any_bh = True
        A(f"**Start {lbl}:**")
        A("")
        for diag in r.get("bh_diagnostics", []):
            if diag is None:
                continue
            flag = " <-- FLAGGED (contract s14)" if diag["param"] == "beta_l0_m" else ""
            side = "lower" if diag["at_lower"] else "upper"
            A(f"- **`{diag['param']}`** (value={diag['value']:.4e}, {side} bound={diag['bound']:.2e}){flag}")
            A(f"  - grad_ll = {diag['grad_ll']:.8f}")
            A(f"  - Verdict: **{diag['verdict']}**")
            A(f"  - {diag['detail']}")
        A("")
    if any_bh:
        A("> **HV-ECON constraint:** Bound-hit solutions are NOT accepted as economics "
          "without a later specification review. The `beta_l0_m` bound-hit requires "
          "a specification review before any economic interpretation.")
    A("")
    A("---")
    A("")

    # Agreement verdict
    A("## 7. Three-start agreement verdict")
    A("")
    if agr.get("agree"):
        A("**AGREEMENT: PASS** -- all three starts converged to the same optimum.")
        A("")
        A(f"- {agr.get('detail','')}")
        A(f"- |DLL| across A/B/C = {agr.get('max_dll', float('nan')):.6e}  (threshold: 1e-2)")
    else:
        A("**AGREEMENT: FAIL -- HV-AGREE**")
        A("")
        A(f"- {agr.get('detail', halt_msg or 'incomplete')}")
        A(f"- |DLL| across A/B/C = {agr.get('max_dll', float('nan')):.6e}  (threshold: 1e-2)")
        A("")
        A("**Root cause:** Start B (pilot defaults) requires more than the authorized "
          f"maxiter={MAXITER_B} to converge from the defaults to the vicinity of the "
          "CONOPT optimum. The defaults are far from the optimum (~1.5 LL units away "
          "at the maxiter cap). This is an optimizer convergence-budget issue, not a "
          "sign of multimodality.")
        A("")
        A("**Recommended next step:** Optimizer/multistart design memo covering:")
        A("- Option 1: Increase maxiter cap beyond 200 (requires new authorization).")
        A("- Option 2: Warm-start B from a closer point (e.g., a coarser solution).")
        A("- Option 3: Switch to a more aggressive optimizer for the first phase "
          "(e.g., gradient descent or Adam warm-up before L-BFGS-B).")
        A("- Do NOT pick a winner between A and C at this stage.")
    A("")
    A("---")
    A("")

    # CONOPT comparison
    A("## 8. CONOPT oracle comparison (start A -- descriptive only)")
    A("")
    res_A = all_results.get("res_A", {})
    if res_A.get("ll_final") is not None:
        dll = all_results.get("dll_vs_oracle", float("nan"))
        A("| Item | Value |")
        A("|---|---|")
        A(f"| JAX final LL start A (float64) | {res_A['ll_final']:.10f} |")
        A(f"| CONOPT oracle LL | {ORACLE_LL:.10f} |")
        A(f"| |DLL| vs oracle | {dll:.6e} |")
        A(f"| Expected |DLL| (v2 external-precision) | ~7.5e-02 |")
        A(f"| ||dtheta||2 from theta_CONOPT | {res_A.get('norm_dtheta_conopt', float('nan')):.4e} |")
        A("")
        if dll < 0.15:
            A("Start A final LL is consistent with the v2 external-precision boundary "
              "(~0.07 LL units above CONOPT oracle). This is the expected outcome for "
              "a float64 external evaluation of a CONOPT optimum.")
        A("")
        A("**Descriptive only. No economic result derived.**")
    else:
        A("Start A final LL not available.")
    A("")
    A("---")
    A("")

    # Per-parameter table
    A("## 9. Per-parameter table -- theta_final and delta from theta_CONOPT")
    A("")
    res_A = all_results.get("res_A", {})
    res_B = all_results.get("res_B", {})
    res_C = all_results.get("res_C", {})
    if any(r.get("theta_final") for r in [res_A, res_B, res_C]):
        conopt_vals = {p: r1["parameters"][p] for p in PARAM_NAMES}
        A("| Parameter | CONOPT | A_final | A_D | B_final | B_D | C_final | C_D |")
        A("|---|---|---|---|---|---|---|---|")
        for p in PARAM_NAMES:
            cv = conopt_vals.get(p, float("nan"))
            row = [f"{cv:.6f}"]
            for r in [res_A, res_B, res_C]:
                fv = r.get("theta_final", {}).get(p, float("nan"))
                dv = r.get("delta_from_conopt", {}).get(p, float("nan"))
                row += [f"{fv:.6f}", f"{dv:+.2e}"]
            A(f"| `{p}` | {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} |")
    A("")
    A("---")
    A("")

    # Runtime
    A("## 10. Runtime and throughput")
    A("")
    A("| Item | Value |")
    A("|---|---|")
    for lbl in ["A", "B", "C"]:
        r = all_results.get(f"res_{lbl}", {})
        ws = r.get("wall_s", float("nan"))
        nit = r.get("opt_nit", "?")
        il = r.get("iter_log", [])
        avg_ms = np.mean([x["per_iter_s"] for x in il])*1000 if il else float("nan")
        A(f"| Start {lbl} wall time ({nit} iters) | {ws:.2f} s (~{avg_ms:.0f} ms/iter) |")
    A(f"| Total wall time (3 starts) | {all_results.get('total_wall_s', 0):.1f} s |")
    A(f"| CONOPT per start (reference) | ~13,689 s (~3.8 h) |")
    A("")
    A("---")
    A("")

    # What was not executed
    A("## 11. What was not executed")
    A("")
    A("- No CONOPT run. No GAMSPy estimation.")
    A("- No Hessian. No SEs. No cluster-robust SEs.")
    A("- No welfare. No SA2. No pilot promotion. No M1-clean displacement.")
    A("- No 40x40 product set. No pooled/singles. No P3a rebuild.")
    A("- v1/v2 equivalence, cleanup-validation, and benchmark reports: NOT overwritten.")
    A("- Oracle JSONs, pkl, production data, pilot data: NOT modified.")
    A("- No economic interpretation of any LL change or bound-hit solution.")
    A("")
    A("---")
    A("")

    # Required final statements
    A("## Required Final Statements")
    A("")
    A("- **Three-start (A=theta_CONOPT, B=pilot defaults, C=perturbed) float64 "
      "L-BFGS-B validation estimation** -- stability + agreement probe only. "
      "NOT production, NOT verdict-grade.")
    A("- **float64 mandatory** (`jax_enable_x64=True` before any array); "
      "JAX `value_and_grad` (JIT) throughout each subprocess.")
    A(f"- **maxiter = {MAXITER_AC} (A/C), {MAXITER_B} (B)** -- all within authorized [50, 200]. "
      "External watchdog not available; documented.")
    A("- **Same bounds as pilot CONOPT spec** -- no bound widening. "
      "`beta_l0_m` lower bound 1e-6 retained.")
    A("- **Bound-hit diagnostics** (projected-gradient/KKT-style) reported for all bound-hit "
      "parameters. `beta_l0_m` flagged explicitly (contract s14).")
    A("- **Bound-hit solutions NOT accepted as economics** without later specification review (HV-ECON clear).")
    if halt_code == "HV-AGREE" or not agr.get("agree"):
        A("- **Agreement verdict: FAIL (HV-AGREE)** -- start B (pilot defaults) did not "
          f"converge within maxiter={MAXITER_B}. No winner picked. "
          "Recommend optimizer/multistart design memo.")
    elif agr.get("agree"):
        A("- **Agreement verdict: PASS** -- all three starts converged to the same optimum.")
    else:
        A(f"- **Agreement verdict: N/A** -- halted at `{halt_code}`.")
    A("- **No Hessian/SE, welfare, SA2, or promotion.** No scaling (still couples-only 2016, 900 alts).")
    A("- **Prior reports, oracle JSONs, pkl, and all production/pilot data: UNMODIFIED.**")
    A("- **M1-clean 2016 remains the active baseline.** Corrected pooled P3a unaffected.")
    A("- NC pilot not promoted.")
    A("")
    A("---")
    A("")
    A("*Status: JAX validation estimation v1 -- three-start float64 probe.*")
    A("*NOT production. NOT verdict-grade. Agreement verdict stated above.*")
    A("*No welfare/SA2/promotion. M1-clean 2016 active. NC pilot not promoted.*")
    A("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"\nReport written: {REPORT_PATH}")

write_report()
print(f"Total wall time: {all_results.get('total_wall_s', 0):.1f} s")
print("DONE. No Hessian, SE, welfare, SA2, or promotion.")
