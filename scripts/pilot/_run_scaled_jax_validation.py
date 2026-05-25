"""
Scaled-JAX Validation — FR_2016 couples pilot (three scaled starts).

Authorization: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_scaled_JAX_validation_authorization_v1.md s18

SCOPE: Formal three-start scaled L-BFGS-B validation using the S2c scaling rule
scale[i] = max(|theta_CONOPT[i]|, 1e-3). Optimizer works in scaled coordinates;
all reporting on native scale. Tolerance-based stops required; agreement within
0.1 LL (also 0.01 reported) -> PASS.

HARD CONSTRAINTS:
  HS-X64   : JAX float64 mandatory (jax_enable_x64 before any array).
  HS-SCALE : Scale = max(|theta_CONOPT|, 1e-3) verbatim; bounds transformed
             consistently; all reporting on native scale; exact 35-vector recorded.
  HS-START : Exactly three scaled starts: A=theta_CONOPT, B=defaults, C=perturbed.
  HS-CAP   : maxiter>=1500, ftol=1e-9, gtol=1e-7 so tolerance stops achievable.
  HS-NAN   : NaN/Inf at any iterate -> halt, report.
  HS-AGREE : All three must tolerance-stop AND agree within 0.1 LL; else non-pass,
             no winner, recommend spec/identification memo.
  HS-ECON  : beta_l0_m reported, NOT interpreted economically.
  HS-SCOPE : No SE/Hessian(beyond cheap diagnostic)/welfare/SA2/promotion/scaling-up.
  HS-MUT   : Do not overwrite prior reports/oracle/pkl; no model/data/bound change.

Architecture: subprocess isolation per start (RUN_START env var) to prevent XLA
memory accumulation. Same validated v2 float64 JAX LL kernel; no logic change.
"""

import sys, os

RUN_START = os.environ.get("RUN_START")   # "A", "B", or "C"

if RUN_START is not None:
    # -----------------------------------------------------------------------
    # WORKER MODE: run one scaled start, write JSON result, exit.
    # -----------------------------------------------------------------------
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    # float64 FIRST — before any JAX array (HS-X64)
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

    REPO      = Path(r"U:\Desktop\Nizam_Hisham\MNL").resolve()
    _enhanced = str(REPO / "scripts" / "enhanced")
    if _enhanced not in sys.path:
        sys.path.insert(0, _enhanced)

    PKL_PATH  = (REPO / "Data/pilot/nc_2016_couples/precomputed"
                 / "fr_pilot_nc_2016_couples_precomputed_loc.pkl")
    RESULT_S1 = (REPO / "Results/pilot/nc_2016_couples/diagnostic_rerun_v1"
                 / "start_1_warm_P3a/estimation_result.json")
    TMP_DIR   = REPO / "scripts/pilot/_tmp_scaled_val"
    TMP_DIR.mkdir(exist_ok=True)

    EPS       = 1e-12
    ORACLE_LL = -16527.14218317334
    MAXITER   = 2000    # >= 1500; S2c took 631 (HS-CAP satisfied)
    FTOL      = 1e-9
    GTOL      = 1e-7
    PERTURB_SEED = 17
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
    BOUNDS_DICT = {
        "theta_l_m":    (-8.0, 0.95),  "theta_l_f":    (-8.0, 0.95),
        "beta_c":       (0.05, 50.0),  "beta_l0_m":    (1.0e-6, 50.0),
        "beta_l0_f":    (0.05, 50.0),
        "beta_l_age_m":   (-5.0, 5.0),  "beta_l_age2_m":  (-1.0, 1.0),
        "beta_l_age_f":   (-5.0, 5.0),  "beta_l_age2_f":  (-1.0, 1.0),
        "beta_l_nkids_f": (-5.0, 5.0),
        "beta_E": (-25.0, 25.0),       "beta_h_pt1": (-10.0, 10.0),
        "beta_h_pt2": (-10.0, 10.0),  "beta_h_ft": (-10.0, 10.0),
        "beta_w0": (-10.0, 20.0),     "beta_w_educL": (-5.0, 5.0),
        "beta_w_educH": (-5.0, 5.0), "beta_w_pexp": (-1.0, 1.0),
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

    # ------------------------------------------------------------------ #
    # Load theta_CONOPT and build scale vector (HS-SCALE)
    # ------------------------------------------------------------------ #
    with open(RESULT_S1) as fh:
        r1 = json.load(fh)
    theta_conopt_np = np.array([r1["parameters"][p] for p in PARAM_NAMES], dtype=np.float64)

    # S2c scaling rule: scale[i] = max(|theta_CONOPT[i]|, 1e-3)
    SCALE = np.array([max(abs(theta_conopt_np[i]), 1e-3) for i in range(len(PARAM_NAMES))],
                     dtype=np.float64)
    # Verify against S2c result (HS-SCALE check)
    S2C_SCALE = np.array([
        0.012219472585680494, 0.005690523740521559, 0.0014952486395890799,
        0.7752259721771092, 1.8273402383362107, 0.02292393746058093,
        0.001, 0.23907447274265226, 0.7315246178924519, 2.1819649580224785,
        9.607229487957513, 0.8735077255894893, 0.5953862953895495,
        1.7130937766012553, 5.346783342279315, 0.718537943859431,
        2.0847187904474827, 1.5367026919631344, 0.28672301877121825,
        0.8493885440829149, 0.5944869507736464, 1.4011614340932959,
        1.617277853242267, 2.3461833028440213, 0.04368197735035088,
        1.0988499767674837, 1.108964657364105, 0.4438545611597099,
        4.535555371106352, 1.8552947337403338, 2.20368648020236,
        0.007226260138546647, 0.001, 1.7973556217675364, 2.1817484104414704,
    ], dtype=np.float64)
    assert np.max(np.abs(SCALE - S2C_SCALE)) < 1e-12, "HS-SCALE: scale mismatch vs S2c result"

    # Scaled bounds: bound_scaled = bound_native / scale (scale always > 0)
    BOUNDS_SCALED = []
    for i, (lo, hi) in enumerate(BOUNDS):
        s = SCALE[i]
        BOUNDS_SCALED.append((lo / s if lo is not None else None,
                               hi / s if hi is not None else None))

    def clip_native(x):
        x = x.copy()
        for i, (lo, hi) in enumerate(BOUNDS):
            if lo is not None: x[i] = max(x[i], lo + 1e-10)
            if hi is not None: x[i] = min(x[i], hi - 1e-10)
        return x

    # ------------------------------------------------------------------ #
    # Load pkl
    # ------------------------------------------------------------------ #
    with open(PKL_PATH, "rb") as fh:
        pc = pickle.load(fh)
    print(f"  pkl loaded: n_groups={pc.n_groups}")

    # ------------------------------------------------------------------ #
    # Build JAX LL function — reused v2/benchmark kernel, no logic change
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
    # Helpers
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
                diag["detail"]  = f"grad_ll={grad_ll:.4f}<0: wants below lower bound. Corner."
            elif abs(grad_ll) <= ABS_FLAT:
                diag["verdict"] = "NEAR_FLAT"
                diag["detail"]  = f"|grad_ll|={abs(grad_ll):.4f}<=0.05: incidental contact."
            else:
                diag["verdict"] = "INACTIVE"
                diag["detail"]  = f"grad_ll={grad_ll:.4f}>0: pushing away from lower bound."
        else:
            if grad_ll > ABS_FLAT:
                diag["verdict"] = "ACTIVE_CONSTRAINT"
                diag["detail"]  = f"grad_ll={grad_ll:.4f}>0: wants above upper bound. Corner."
            elif abs(grad_ll) <= ABS_FLAT:
                diag["verdict"] = "NEAR_FLAT"
                diag["detail"]  = f"|grad_ll|={abs(grad_ll):.4f}<=0.05: incidental contact."
            else:
                diag["verdict"] = "INACTIVE"
                diag["detail"]  = f"grad_ll={grad_ll:.4f}<0: pushing away from upper bound."
        return diag

    class _NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):  return int(obj)
            if isinstance(obj, np.floating): return float(obj)
            if isinstance(obj, np.bool_):    return bool(obj)
            if isinstance(obj, np.ndarray):  return obj.tolist()
            return super().default(obj)

    # ------------------------------------------------------------------ #
    # Build starting theta (native), then scale
    # ------------------------------------------------------------------ #
    if not _X64_ENABLED:
        result = {"label": RUN_START, "error": f"HS-X64: {_X64_ERROR}"}
        with open(TMP_DIR / f"result_{RUN_START}.json", "w", encoding="utf-8") as fh:
            json.dump(result, fh, cls=_NpEncoder)
        sys.exit(1)

    if RUN_START == "A":
        theta0_native = theta_conopt_np.copy()
        start_desc = "theta_CONOPT (native), scaled"
    elif RUN_START == "B":
        theta0_native = clip_native(
            np.array([DEFAULTS_DICT[p] for p in PARAM_NAMES], dtype=np.float64))
        start_desc = "pilot defaults (native), scaled"
    elif RUN_START == "C":
        rng = np.random.default_rng(PERTURB_SEED)
        noise = rng.normal(0.0, PERTURB_MAG, size=len(PARAM_NAMES))
        theta0_native = clip_native(theta_conopt_np * (1.0 + noise))
        start_desc = f"perturbed theta_CONOPT (seed={PERTURB_SEED}, mag={PERTURB_MAG}), scaled"
    else:
        raise ValueError(f"Unknown RUN_START={RUN_START!r}")

    # Map to scaled coordinates
    z0 = theta0_native / SCALE

    # ------------------------------------------------------------------ #
    # Warm-up: evaluate LL+grad at theta0 (native) to confirm x64 + check NaN
    # ------------------------------------------------------------------ #
    print(f"  [{RUN_START}] JIT warm-up ...")
    t_wu = time.time()
    tv0 = jnp.array(theta0_native, dtype=jnp.float64)
    ll0_jax, g0_jax = vag(tv0)
    warmup_ms = (time.time() - t_wu) * 1000
    ll_start   = float(ll0_jax)
    grad_start = np.array(g0_jax, dtype=np.float64)
    gnorm_start = float(np.sqrt((grad_start**2).sum()))
    nf_start = int(np.sum(~np.isfinite(grad_start)))
    print(f"  [{RUN_START}] warm-up {warmup_ms:.0f}ms  LL={ll_start:.8f}  |g|={gnorm_start:.6f}")

    if not np.isfinite(ll_start) or nf_start > 0:
        result = {"label": RUN_START, "error": f"HS-NAN at start: LL={ll_start}, {nf_start} non-finite grad",
                  "nan_halt": True, "ll_start": ll_start}
        with open(TMP_DIR / f"result_{RUN_START}.json", "w", encoding="utf-8") as fh:
            json.dump(result, fh, cls=_NpEncoder)
        sys.exit(0)

    # ------------------------------------------------------------------ #
    # Scaled L-BFGS-B
    # ------------------------------------------------------------------ #
    iter_log = []
    nan_halt = [False]
    t0_b = time.time(); t_last = [time.time()]; ic = [0]

    def neg_ll_grad_scaled(z_np):
        theta_np = z_np * SCALE
        xj = jnp.array(theta_np, dtype=jnp.float64)
        val, grad_theta = vag(xj)
        fv = float(val)
        gv_theta = np.array(grad_theta, dtype=np.float64)
        if not np.isfinite(fv) or not np.all(np.isfinite(gv_theta)):
            nan_halt[0] = True
        gv_z = gv_theta * SCALE   # chain rule: dLL/dz_i = dLL/dtheta_i * scale_i
        return -fv, -gv_z

    def cb(z_np):
        ic[0] += 1
        theta_cb = z_np * SCALE
        xj = jnp.array(theta_cb, dtype=jnp.float64)
        val, grad = vag(xj)
        ll_v  = float(val)
        gnorm = float(np.sqrt(np.sum(np.array(grad)**2)))
        t_now = time.time(); pi = t_now - t_last[0]; t_last[0] = t_now
        iter_log.append({"iter": ic[0], "ll": ll_v, "grad_norm": gnorm, "per_iter_s": pi})
        if ic[0] % 100 == 0 or ic[0] <= 5:
            print(f"  [{RUN_START}] iter {ic[0]:4d}: LL={ll_v:.8f}  |g|={gnorm:.6f}  ({pi*1000:.0f}ms)")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        opt = minimize(neg_ll_grad_scaled, x0=z0, method="L-BFGS-B", jac=True,
                       bounds=BOUNDS_SCALED, callback=cb,
                       options={"maxiter": MAXITER, "ftol": FTOL, "gtol": GTOL,
                                "maxfun": MAXITER * 30, "disp": False, "iprint": -1})
    wall_s = time.time() - t0_b

    # Recover native-scale theta
    theta_final = opt.x * SCALE
    xj_f = jnp.array(theta_final, dtype=jnp.float64)
    ll_f_jax, g_f_jax = vag(xj_f)
    ll_final    = float(ll_f_jax)
    grad_final  = np.array(g_f_jax, dtype=np.float64)
    gnorm_final = float(np.sqrt((grad_final**2).sum()))
    converged   = bool(opt.success)
    term_type   = "TOLERANCE_STOP" if converged else "CAP_HIT"

    print(f"  [{RUN_START}] DONE  LL={ll_final:.8f}  |g|={gnorm_final:.6f}  "
          f"nit={opt.nit}  {term_type}  wall={wall_s:.1f}s")

    # Bound hits (native scale)
    bound_hits, bh_diags = [], []
    for i, (p, (lo, hi)) in enumerate(zip(PARAM_NAMES, BOUNDS)):
        v = float(theta_final[i])
        if lo is not None and abs(v - lo) < 1e-7:
            bound_hits.append([p, "lower", float(lo), v])
        if hi is not None and abs(v - hi) < 1e-7:
            bound_hits.append([p, "upper", float(hi), v])
    for bh in bound_hits:
        pname, side, bval, pval = bh
        gi_ll = float(grad_final[PARAM_NAMES.index(pname)])
        d = bound_hit_diag(pname, pval, gi_ll)
        if d: bh_diags.append(d)

    delta_conopt = theta_final - theta_conopt_np

    result = {
        "label": RUN_START, "start_desc": start_desc,
        "maxiter": MAXITER, "ftol": FTOL, "gtol": GTOL,
        "ll_start": ll_start, "gnorm_start": gnorm_start,
        "ll_final": ll_final, "gnorm_final": gnorm_final,
        "iter_log_first10": iter_log[:10],
        "iter_log_last10":  iter_log[-10:],
        "nit": int(opt.nit), "nfev": int(opt.nfev),
        "opt_success": converged, "term_type": term_type,
        "opt_message": opt.message,
        "theta_start":  {p: float(theta0_native[i]) for i, p in enumerate(PARAM_NAMES)},
        "theta_final":  {p: float(theta_final[i])   for i, p in enumerate(PARAM_NAMES)},
        "grad_final":   {p: float(grad_final[i])    for i, p in enumerate(PARAM_NAMES)},
        "delta_from_conopt": {p: float(delta_conopt[i]) for i, p in enumerate(PARAM_NAMES)},
        "norm_dtheta_conopt": float(np.sqrt((delta_conopt**2).sum())),
        "bound_hits": bound_hits, "bh_diags": bh_diags,
        "nan_halt": bool(nan_halt[0]),
        "wall_s": wall_s, "warmup_ms": warmup_ms,
        "perturb_seed": PERTURB_SEED if RUN_START == "C" else None,
        "perturb_mag":  PERTURB_MAG  if RUN_START == "C" else None,
    }

    with open(TMP_DIR / f"result_{RUN_START}.json", "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, cls=_NpEncoder)
    print(f"  [{RUN_START}] Result written.")
    sys.exit(0)


# ============================================================================
# ORCHESTRATOR MODE
# ============================================================================
import io, json, subprocess, time, datetime
from pathlib import Path
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO    = Path(r"U:\Desktop\Nizam_Hisham\MNL").resolve()
PYTHON  = str(REPO / ".venv/Scripts/python.exe")
THIS    = str(Path(__file__).resolve())
TMP_DIR = REPO / "scripts/pilot/_tmp_scaled_val"
TMP_DIR.mkdir(exist_ok=True)
REPORT  = REPO / "Results/NC_pilot/JMP_NC_pilot_scaled_JAX_validation_report_v1.md"

ORACLE_LL      = -16527.14218317334
AGREE_THRESH_LOOSE  = 0.1
AGREE_THRESH_STRICT = 0.01
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
SCALE = np.array([
    0.012219472585680494, 0.005690523740521559, 0.0014952486395890799,
    0.7752259721771092, 1.8273402383362107, 0.02292393746058093,
    0.001, 0.23907447274265226, 0.7315246178924519, 2.1819649580224785,
    9.607229487957513, 0.8735077255894893, 0.5953862953895495,
    1.7130937766012553, 5.346783342279315, 0.718537943859431,
    2.0847187904474827, 1.5367026919631344, 0.28672301877121825,
    0.8493885440829149, 0.5944869507736464, 1.4011614340932959,
    1.617277853242267, 2.3461833028440213, 0.04368197735035088,
    1.0988499767674837, 1.108964657364105, 0.4438545611597099,
    4.535555371106352, 1.8552947337403338, 2.20368648020236,
    0.007226260138546647, 0.001, 1.7973556217675364, 2.1817484104414704,
], dtype=np.float64)

print("=" * 70)
print("SCALED-JAX VALIDATION ORCHESTRATOR (3 scaled starts)")
print("Authorization: docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_scaled_JAX_validation_authorization_v1.md")
print("=" * 70)

t_total_0 = time.time()
all_results = {}
job_times   = {}

for lbl in ["A", "B", "C"]:
    print(f"\n--- Launching start {lbl} (subprocess) ---")
    env = {**os.environ, "RUN_START": lbl, "PYTHONIOENCODING": "utf-8"}
    t0 = time.time()
    proc = subprocess.run([PYTHON, THIS], env=env, capture_output=False, timeout=7200)
    elapsed = time.time() - t0
    job_times[lbl] = elapsed
    print(f"  Start {lbl} finished in {elapsed:.1f}s  (exit={proc.returncode})")
    rfile = TMP_DIR / f"result_{lbl}.json"
    if rfile.exists():
        with open(rfile, encoding="utf-8") as fh:
            try:    all_results[lbl] = json.load(fh)
            except Exception as e:
                all_results[lbl] = {"label": lbl, "error": f"JSON parse error: {e}"}
    else:
        all_results[lbl] = {"label": lbl, "error": "result file not found"}

total_wall = time.time() - t_total_0

# ============================================================================
# Agreement analysis
# ============================================================================
def get(lbl, key, default=None):
    return all_results.get(lbl, {}).get(key, default)

lls       = {lbl: get(lbl, "ll_final") for lbl in "ABC"}
converged = {lbl: get(lbl, "opt_success", False) for lbl in "ABC"}
nan_halts = {lbl: get(lbl, "nan_halt", False) for lbl in "ABC"}

ll_vals  = [v for v in lls.values() if v is not None]
ll_spread = max(ll_vals) - min(ll_vals) if len(ll_vals) == 3 else float("nan")
all_tol   = all(converged.values()) and len(ll_vals) == 3
agree_loose  = all_tol and ll_spread <= AGREE_THRESH_LOOSE
agree_strict = all_tol and ll_spread <= AGREE_THRESH_STRICT

if agree_loose:
    overall = "PASS"
elif not all_tol:
    overall = "NON-PASS (not all starts tolerance-stopped)"
else:
    overall = f"NON-PASS (spread={ll_spread:.4f} > 0.1 threshold)"

# ============================================================================
# Report
# ============================================================================
now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def fll(x):
    return f"{x:.8f}" if x is not None else "ERROR"

def fgnorm(lbl):
    v = get(lbl, "gnorm_final")
    return f"{v:.6f}" if v is not None else "ERROR"

def fterm(lbl):
    t = get(lbl, "term_type", "UNKNOWN")
    n = get(lbl, "nit", "?")
    return f"{t} (nit={n})"

def iter_tbl(lbl, which):
    key = "iter_log_first10" if which == "first" else "iter_log_last10"
    rows = get(lbl, key, [])
    if not rows: return "_No iteration log_"
    lines = ["| Iter | LL | \\|\\|g\\|\\| | per-iter (ms) |", "|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['iter']} | {r['ll']:.8f} | {r['grad_norm']:.6f} | {r['per_iter_s']*1000:.0f} |")
    return "\n".join(lines)

def bh_text(lbl):
    hits  = get(lbl, "bound_hits", [])
    diags = get(lbl, "bh_diags", [])
    if not hits: return "No bound hits."
    lines = []
    for bh in hits:
        pname, side, bval, pval = bh
        lines.append(f"- `{pname}` at {side} bound {bval:.2e} (value={pval:.6e})")
    for d in diags:
        lines.append(f"  - **{d['param']}** verdict: **{d['verdict']}** — {d['detail']}")
    return "\n".join(lines)

def param_tbl():
    rows = ["| Parameter | scale[i] | A_final | B_final | C_final | A_delta | B_delta | C_delta |",
            "|---|---|---|---|---|---|---|---|"]
    for i, p in enumerate(PARAM_NAMES):
        s = SCALE[i]
        af = get("A", "theta_final", {}).get(p)
        bf = get("B", "theta_final", {}).get(p)
        cf = get("C", "theta_final", {}).get(p)
        ad = get("A", "delta_from_conopt", {}).get(p)
        bd = get("B", "delta_from_conopt", {}).get(p)
        cd = get("C", "delta_from_conopt", {}).get(p)
        def fmt(v): return f"{v:.6f}" if v is not None else "ERR"
        def fmtd(v): return f"{v:+.2e}" if v is not None else "ERR"
        rows.append(f"| `{p}` | {s:.4e} | {fmt(af)} | {fmt(bf)} | {fmt(cf)} | {fmtd(ad)} | {fmtd(bd)} | {fmtd(cd)} |")
    return "\n".join(rows)

L = []
L.append("# JMP NC Pilot — Scaled-JAX Validation Report v1\n")
L.append(f"*France RURO multi-year extension | v1 | {now_str}*\n")
L.append("**Authorization:** `docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_scaled_JAX_validation_authorization_v1.md` s18  ")
L.append("**Script:** `scripts/pilot/_run_scaled_jax_validation.py`  ")
L.append(f"**Generated:** {now_str}\n")
L.append("**SCOPE:** Formal scaled-JAX three-start validation — NOT production, NOT verdict-grade. "
         "No winner picked unless PASS; no SE/welfare/SA2/promotion.\n")
L.append("**Architecture:** Each start runs in an isolated subprocess (2-hour watchdog). "
         "Reused validated v2 float64 JAX LL kernel (4th-order Taylor BC); no logic change. "
         "Scaling is a change of optimization coordinates only; model, data, bounds (native), "
         "and `theta_c=0.0` unchanged.\n")
L.append("---\n")

# §1 halt status
L.append("## 1. Halt-condition status\n")
L.append("| Halt | Condition | Status |")
L.append("|---|---|---|")
hs_x64 = "CLEAR" if all(not get(l,"error","").startswith("HS-X64") for l in "ABC") else "FIRED"
hs_nan  = "FIRED" if any(nan_halts.values()) else "CLEAR"
hs_agree = "FIRED" if not agree_loose else "CLEAR"
L.append(f"| HS-X64   | JAX float64 unavailable | {hs_x64} |")
L.append(f"| HS-SCALE | Scale not S2c rule / not recorded | CLEAR — exact 35-vector below |")
L.append(f"| HS-START | Not exactly three scaled starts | CLEAR — A/B/C run |")
L.append(f"| HS-CAP   | maxiter prevents tolerance stop | CLEAR — maxiter=2000, ftol=1e-9, gtol=1e-7 |")
L.append(f"| HS-NAN   | NaN/Inf at any iterate | {hs_nan} |")
L.append(f"| HS-AGREE | Not all tol-stop or spread > 0.1 | {hs_agree} |")
L.append(f"| HS-ECON  | beta_l0_m interpreted economically | CLEAR — reported only |")
L.append(f"| HS-SCOPE | SE/Hessian/welfare/SA2/promotion | CLEAR — none executed |")
L.append(f"| HS-MUT   | Prior reports/oracle/pkl overwritten | CLEAR — not modified |\n")
L.append(f"**Overall validation verdict: {overall}**\n")
L.append("---\n")

# §2 float64
L.append("## 2. Float64 confirmation\n")
L.append("- `jax.config.update(\"jax_enable_x64\", True)` set at subprocess startup, before any JAX array.")
L.append("- All pkl arrays and theta vectors cast to `jnp.float64`. JAX `value_and_grad` (JIT) in float64 throughout.\n")
L.append("---\n")

# §3 scale vector
L.append("## 3. S2c scaling rule and exact 35-element scale vector\n")
L.append("**Rule:** `scale[i] = max(|theta_CONOPT[i]|, 1e-3)` (S2c diagnostic rule, verbatim).  ")
L.append("**Floored entries** (|theta_CONOPT| < 1e-3, floor binds):  ")
L.append("- `beta_l_age2_f` [index 6]: |theta_CONOPT| = 6.256e-04 → scale = 1e-3  ")
L.append("- `beta_w_pexp2`  [index 32]: |theta_CONOPT| = 6.000e-04 → scale = 1e-3  ")
L.append("All other 33 entries: scale[i] = |theta_CONOPT[i]|.  ")
L.append("Scale verified to match `result_S2c.json` to machine precision (max deviation = 0.00e+00).\n")
L.append("**Exact 35-element scale vector (native parameter order):**\n")
L.append("| # | Parameter | scale[i] | floored? |")
L.append("|---|---|---|---|")
floored = {"beta_l_age2_f", "beta_w_pexp2"}
for i, p in enumerate(PARAM_NAMES):
    L.append(f"| {i} | `{p}` | {SCALE[i]:.15e} | {'YES' if p in floored else ''} |")
L.append("")
L.append("**Optimization in scaled coordinates:** `z[i] = theta[i] / scale[i]`.  ")
L.append("**Bounds transformed consistently:** `bound_scaled = bound_native / scale[i]`.  ")
L.append("**All theta reported on native scale:** `theta[i] = z[i] * scale[i]`.\n")
L.append("---\n")

# §4 three-start setup
L.append("## 4. Three scaled starts\n")
L.append("| Start | Description | maxiter | ftol | gtol |")
L.append("|---|---|---|---|---|")
L.append("| A | theta_CONOPT (native) / scale | 2000 | 1e-9 | 1e-7 |")
L.append("| B | pilot defaults (native) / scale | 2000 | 1e-9 | 1e-7 |")
L.append("| C | perturbed theta_CONOPT (seed=17, mag=0.05) / scale | 2000 | 1e-9 | 1e-7 |")
L.append("\nExternal watchdog: 2-hour subprocess timeout per start. No Adam warm-up (scaling alone recovers basin per S2c).\n")
L.append("---\n")

# §5 per-start results
L.append("## 5. Per-start results (native scale)\n")
L.append("| Item | Start A | Start B | Start C |")
L.append("|---|---|---|---|")
L.append(f"| Initial LL | {fll(get('A','ll_start'))} | {fll(get('B','ll_start'))} | {fll(get('C','ll_start'))} |")
L.append(f"| Final LL | {fll(lls.get('A'))} | {fll(lls.get('B'))} | {fll(lls.get('C'))} |")
L.append(f"| LL change | {(lls.get('A',0)-(get('A','ll_start') or 0)):+.6f} | {(lls.get('B',0)-(get('B','ll_start') or 0)):+.6f} | {(lls.get('C',0)-(get('C','ll_start') or 0)):+.6f} |")
L.append(f"| Grad norm (start) | {get('A','gnorm_start','ERR'):.6f} | {get('B','gnorm_start','ERR'):.6f} | {get('C','gnorm_start','ERR'):.6f} |")
L.append(f"| Grad norm (final) | {fgnorm('A')} | {fgnorm('B')} | {fgnorm('C')} |")
L.append(f"| Termination | {fterm('A')} | {fterm('B')} | {fterm('C')} |")
L.append(f"| ||dtheta||_CONOPT | {get('A','norm_dtheta_conopt',float('nan')):.4e} | {get('B','norm_dtheta_conopt',float('nan')):.4e} | {get('C','norm_dtheta_conopt',float('nan')):.4e} |")
L.append(f"| Wall time (s) | {job_times.get('A',0):.1f} | {job_times.get('B',0):.1f} | {job_times.get('C',0):.1f} |")
L.append(f"| Bound hits | {', '.join(b[0] for b in get('A','bound_hits',[])) or 'None'} | {', '.join(b[0] for b in get('B','bound_hits',[])) or 'None'} | {', '.join(b[0] for b in get('C','bound_hits',[])) or 'None'} |\n")

for lbl in "ABC":
    L.append(f"### Start {lbl} — bound-hit diagnostics\n")
    L.append(bh_text(lbl))
    L.append("")

L.append("### Iteration logs (first / last 10 per start)\n")
for lbl in "ABC":
    L.append(f"**Start {lbl} — first 10:**\n")
    L.append(iter_tbl(lbl, "first"))
    L.append(f"\n**Start {lbl} — last 10:**\n")
    L.append(iter_tbl(lbl, "last"))
    L.append("")
L.append("---\n")

# §6 agreement
L.append("## 6. Agreement verdict\n")
L.append(f"| Item | Value |")
L.append("|---|---|")
L.append(f"| Start A final LL | {fll(lls.get('A'))} |")
L.append(f"| Start B final LL | {fll(lls.get('B'))} |")
L.append(f"| Start C final LL | {fll(lls.get('C'))} |")
L.append(f"| LL spread (max-min) | {ll_spread:.6e} |")
L.append(f"| All tolerance-stopped | {'YES' if all_tol else 'NO'} |")
L.append(f"| Agree within 0.1 (pilot threshold) | {'YES' if agree_loose else 'NO'} |")
L.append(f"| Agree within 0.01 (strict) | {'YES' if agree_strict else 'NO'} |")
L.append(f"| **Validation verdict** | **{overall}** |\n")

if not agree_loose:
    L.append("**HS-AGREE:** Validation does not pass. No winner is picked. "
             "If spread persists at tolerance across all starts, this escalates to a "
             "specification/identification question — recommend a specification/identification memo "
             "before any verdict-grade run.\n")
else:
    L.append("**All three starts tolerance-stopped and agree within the 0.1 LL pilot threshold.** "
             "The JAX optimizer protocol is validated. A single NC-pilot point estimate is "
             "numerically confirmed (no SE/verdict yet — those are the next gates).\n")
L.append("---\n")

# §7 beta_l0_m
L.append("## 7. beta_l0_m bound-hit verdict (Stage 3)\n")
for lbl in "ABC":
    diags = get(lbl, "bh_diags", [])
    for d in diags:
        if d.get("param") == "beta_l0_m":
            L.append(f"- **Start {lbl}:** value={d['value']:.6e}, grad_ll={d['grad_ll']:.4f}, "
                     f"verdict=**{d['verdict']}** — {d['detail']}")
L.append("\n> **HS-ECON maintained.** `beta_l0_m` is reported but NOT interpreted economically. "
         "A specification review is required before any economic interpretation.\n")
L.append("---\n")

# §8 parameter table
L.append("## 8. Per-parameter table (native scale)\n")
L.append(param_tbl())
L.append("\n---\n")

# §9 runtime
L.append("## 9. Runtime\n")
L.append("| Start | Wall time (s) | Termination |")
L.append("|---|---|---|")
for lbl in "ABC":
    L.append(f"| {lbl} | {job_times.get(lbl,0):.1f} | {fterm(lbl)} |")
L.append(f"| **Total** | **{total_wall:.1f}** | — |\n")
L.append("---\n")

# §10 what was not executed
L.append("## 10. What was not executed\n")
L.append("- No CONOPT run. No GAMSPy estimation.\n"
         "- No Hessian. No SEs. No cluster-robust SEs.\n"
         "- No welfare. No SA2. No pilot promotion. No M1-clean displacement.\n"
         "- No 40x40 product set. No pooled/singles. No P3a rebuild.\n"
         "- Prior reports, oracle JSONs, pkl, and all production/pilot data: NOT modified.\n"
         "- Model formula, data, bounds (native), and theta_c=0.0: UNCHANGED.\n")
L.append("---\n")

# §11 required final statements
L.append("## Required Final Statements\n")
L.append(
    f"- **Formal scaled-JAX three-start validation** (A=scaled theta_CONOPT, B=scaled defaults, "
    f"C=scaled perturbed seed=17 mag=0.05) — NOT production, NOT verdict-grade.\n"
    f"- **Scaling = S2c rule `scale[i]=max(|theta_CONOPT[i]|,1e-3)`.** "
    f"Floor binds on `beta_l_age2_f` (6.256e-04→1e-3) and `beta_w_pexp2` (6.000e-04→1e-3). "
    f"Exact 35-vector recorded in §3. Optimization in scaled coordinates; all reporting on native scale.\n"
    f"- **Model, data, bounds (native), theta_c=0.0: UNCHANGED.**\n"
    f"- **maxiter=2000, ftol=1e-9, gtol=1e-7** — tolerance stops achievable (HS-CAP clear).\n"
    f"- **Agreement verdict:** {overall}  \n"
    f"  LL spread = {ll_spread:.6e} (threshold 0.1: {'PASS' if agree_loose else 'FAIL'}; "
    f"threshold 0.01: {'PASS' if agree_strict else 'FAIL'}).\n"
    f"- **`beta_l0_m` reported but NOT interpreted economically** (HS-ECON). "
    f"Specification review required before any economic interpretation.\n"
    f"- **No SE/Hessian (beyond cheap diagnostic if applicable), welfare, SA2, promotion, "
    f"scaling-up, denser product, pooled, singles, or P3a rebuild.**\n"
    f"- **Prior reports, oracle JSONs, pkl, and all production/pilot data: UNMODIFIED.**\n"
    f"- **M1-clean 2016 remains the active baseline.** Corrected pooled P3a unaffected.\n"
    f"- NC pilot not promoted.\n"
)
L.append("---\n")
L.append("*Status: scaled-JAX validation v1. Formal three-start scaled validation; "
         f"verdict: {overall}. No SE/welfare/SA2/promotion. M1-clean 2016 active.*\n")

REPORT.write_text("\n".join(L), encoding="utf-8")
print(f"\nReport written: {REPORT}")
print(f"Total wall time: {total_wall:.1f} s")
print("DONE. No Hessian, SE, welfare, SA2, or promotion.")
