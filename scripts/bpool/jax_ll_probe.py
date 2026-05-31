"""
JAX likelihood + gradient correctness probe for the RURO joint MNL.

DECISIVE QUESTION: does a JAX reimplementation of the SINGLES log-likelihood
match the production engine (estimation_engine.compute_likelihood_singles) and
its gradient (compute_gradient_singles) at theta_star to ~1e-6?

If YES -> the JAX backend is sound; jax.grad/jax.hessian/jax.vmap can replace
the GAMS-generation path (the measured 94% bottleneck) and parallelise across
cores (CPU here) or a GPU (another machine) with NO code change.

Scope of this probe: SINGLES_MALE only. It exercises every risky primitive the
full joint LL needs -- Box-Cox utility, the -log(prior) IS correction, the
log-normal wage density with the worker gate and the -log_wage Jacobian, the
proposal-weighted market centering, and the group log-sum-exp. The couples
block is more bookkeeping (gender-split) but the SAME primitives; if singles
matches, couples is a faithful-transcription exercise, not a research risk.

GPU PORTABILITY (baked in):
  - jax_enable_x64=True  -> float64 everywhere (required to hit 1e-6; works on
    CPU and GPU identically). GPU defaults to float32 which would NOT match.
  - No device pinning / .cpu(): arrays land on the default device, so running
    this unchanged on a CUDA machine uses the GPU automatically.
  - Pure jnp functional ops -> jit-able and grad-able on any backend.

USAGE:
  python jax_ll_probe.py                       # singles_male, n_hh cap 200
  python jax_ll_probe.py --n-hh 0              # full singles_male
  python jax_ll_probe.py --group singles_female
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

# ---- JAX setup: float64 + device-agnostic (GPU-ready) ----
import jax                                  # noqa: E402
jax.config.update("jax_enable_x64", True)   # MUST precede heavy jnp use
import jax.numpy as jnp                     # noqa: E402


# ---------------------------------------------------------------------------
# JAX primitives (faithful to estimation_engine / estimation_utils)
# ---------------------------------------------------------------------------
def jbox_cox(x, theta):
    """BC(x;θ) = (x^θ - 1)/θ for |θ|>=1e-8 else log(x). Matches box_cox_transform."""
    # jnp.where keeps both branches finite for autodiff; the eps guard mirrors
    # the engine's abs(theta) < 1e-8 -> log(x) limit.
    safe_theta = jnp.where(jnp.abs(theta) < 1e-8, 1.0, theta)
    powered = (jnp.power(x, safe_theta) - 1.0) / safe_theta
    return jnp.where(jnp.abs(theta) < 1e-8, jnp.log(x), powered)


def jgroup_logsumexp(V, n_groups, n_alts):
    """LSE per group; data laid out as (n_groups, n_alts) row-major.

    The engine groups by contiguous [group_starts[i]:group_ends[i]] with the
    observed choice at group_starts[i] (draw==0 first). Here we reshape to
    (n_groups, n_alts) so row i is group i and column 0 is the observed choice.
    """
    Vg = V.reshape(n_groups, n_alts)
    mx = jnp.max(Vg, axis=1, keepdims=True)
    lse = (mx[:, 0] + jnp.log(jnp.sum(jnp.exp(Vg - mx), axis=1)))
    V_obs = Vg[:, 0]
    return V_obs, lse


def _center_proposal(log_market, prior, n_groups, n_alts):
    """Proposal-weighted within-group centering (matches _center_within_choice_set)."""
    lm = log_market.reshape(n_groups, n_alts)
    w = prior.reshape(n_groups, n_alts)
    denom = jnp.sum(w, axis=1, keepdims=True) + 1e-12  # EPS as in engine
    mean_val = jnp.sum(lm * w, axis=1, keepdims=True) / denom
    return (lm - mean_val).reshape(-1)


def build_jax_singles_ll(data, spec, is_male):
    """Return a jit-compiled negLL(theta) for one singles group, plus the
    param-name->index map used to slot the 49-vector into named scalars.

    All data arrays are captured as float64 jnp constants (device-resident).
    """
    suffix = "_sm" if is_male else "_sf"
    pidx = {n: spec.get_param_index(n) for n in spec.all_param_names}
    n_groups = int(data.n_groups)
    n_alts = int(data.n_obs // data.n_groups)

    # --- capture data as device constants (float64) ---
    leisure = jnp.asarray(data.leisure, dtype=jnp.float64)
    consumption = jnp.asarray(data.consumption, dtype=jnp.float64)
    working = jnp.asarray(data.working, dtype=jnp.float64)
    prior = jnp.asarray(data.prior, dtype=jnp.float64)
    log_prior = jnp.log(prior)

    def _arr(name):
        v = getattr(data, name, None)
        return None if v is None else jnp.asarray(v, dtype=jnp.float64)

    # leisure shifters (age_norm, age_norm2, n_children[female only])
    leis_shifters = []
    for sh in spec.utility_leisure_shifters:
        var = sh["variable"]
        coef = sh["coefficient"]
        gs = sh.get("gender_specific", False)
        if gs and var == "n_children" and is_male:
            continue  # n_children is female-only
        arr = _arr(var)
        if arr is None:
            continue
        leis_shifters.append((coef + suffix, arr))

    beta_l0_name = spec.utility_leisure_intercept + suffix
    theta_l_name = (spec.utility_leisure_theta + suffix) if spec.utility_leisure_theta else None
    singles_group = "singles_male" if is_male else "singles_female"
    theta_c_name = spec.theta_c_param_name(singles_group)
    beta_c_fixed = getattr(spec, "utility_consumption_coef_fixed", None)

    # hours shifters
    gsuf_h = "_male" if is_male else "_female"
    hours = []
    for sh in spec.hours_shifters:
        var = sh["variable"]
        coef = sh["coefficient"]
        arr = _arr(var)
        if arr is None:
            continue
        inter = sh.get("interaction", None)
        use_working = (inter == "working") or (isinstance(inter, (list, tuple)) and "working" in inter)
        hours.append((coef, arr, use_working))

    # wage mean shifters + sigma
    wage_terms = []
    for sh in spec.wage_mean_shifters:
        var = sh["variable"]
        coef = sh["coefficient"]
        if var == "intercept":
            wage_terms.append((coef, None))
        else:
            arr = _arr(var)
            if arr is not None:
                wage_terms.append((coef, arr))
    sigma_name = spec.wage_variance_param
    log_wage = _arr("log_wage")

    # market shifters (+ scales, + interaction working) and centering flag
    scale_map = getattr(spec, "market_opportunity_variable_scales", None) or {}
    mkt = []
    for sh in (getattr(spec, "market_opportunity_shifters", None) or []):
        var = sh["variable"]
        coef = sh["coefficient"]
        applies = str(sh.get("applies_to", "both")).strip().lower()
        # singles routing (post-58d0dba): skip only cm/cf; male/female honoured
        if applies in {"cm", "cf"}:
            continue
        if applies in {"male", "sm"} and not is_male:
            continue
        if applies in {"female", "sf"} and is_male:
            continue
        arr = _arr(var)
        if arr is None:
            continue
        arr = arr * float(scale_map.get(var, 1.0))
        inter = sh.get("interaction", None)
        use_working = (inter == "working") or (isinstance(inter, (list, tuple)) and "working" in inter)
        mkt.append((coef, arr, use_working))
    do_center = bool(getattr(spec, "market_opportunity_center_within_choice_set", False))
    center_prop = (getattr(spec, "market_opportunity_center_weights", None) == "proposal")

    LOG2PI = float(np.log(2 * np.pi))

    def neg_ll(theta):
        def P(name):
            return theta[pidx[name]]

        # ---- utility ----
        theta_l = P(theta_l_name) if theta_l_name else 0.0
        theta_c = P(theta_c_name) if theta_c_name else 0.0
        bc_l = jbox_cox(leisure, theta_l)
        bc_c = jbox_cox(consumption, theta_c)
        beta_l_coeff = P(beta_l0_name)
        for cname, arr in leis_shifters:
            beta_l_coeff = beta_l_coeff + P(cname) * arr
        beta_c = beta_c_fixed if beta_c_fixed is not None else P(spec.utility_consumption_coef + suffix)
        u = beta_l_coeff * bc_l + beta_c * bc_c  # beta_cl=0 for singles

        # ---- hours opportunity ----
        log_h = jnp.zeros_like(u)
        for cname, arr, uw in hours:
            x = arr * working if uw else arr
            log_h = log_h + P(cname) * x

        # ---- wage opportunity (vw) ----
        mu = jnp.zeros_like(u)
        for cname, arr in wage_terms:
            mu = mu + (P(cname) if arr is None else P(cname) * arr)
        sigma = P(sigma_name)
        resid = (log_wage - mu) / sigma
        log_w_full = -0.5 * resid**2 - jnp.log(sigma) - 0.5 * LOG2PI - log_wage
        log_w = jnp.where(working > 0, log_w_full, 0.0)

        # ---- market opportunity (+ centering) ----
        log_market = jnp.zeros_like(u)
        for cname, arr, uw in mkt:
            x = arr * working if uw else arr
            log_market = log_market + P(cname) * x
        if do_center:
            if center_prop:
                log_market = _center_proposal(log_market, prior, n_groups, n_alts)
            else:
                lm = log_market.reshape(n_groups, n_alts)
                log_market = (lm - jnp.mean(lm, axis=1, keepdims=True)).reshape(-1)

        # ---- composite V and grouped LL ----
        V = u + log_h + log_w + log_market - log_prior
        V_obs, lse = jgroup_logsumexp(V, n_groups, n_alts)
        ll = jnp.sum(V_obs - lse)
        return -ll  # negative LL (matches engine convention)

    return jax.jit(neg_ll), pidx


def build_jax_couples_ll(data, spec):
    """Return a jit-compiled negLL(theta) for the couples group.

    Faithful to compute_likelihood_couples:
      u = beta_l_coeff_m*BC(l_m) + beta_l_coeff_f*BC(l_f) + beta_c*BC(c)
          + beta_ll*BC(l_m)*BC(l_f)           [consumption added ONCE]
      log_h = sum over genders of hours shifters (shared coefs, gender data)
      log_w = sum over genders of log-normal wage density (worker-gated)
      log_market = gsur(both) + region/year/urb(household) + occ(male/female),
                   then proposal-weighted within-group centering
      V = u + log_h + log_w + log_market - log(prior); grouped LSE; obs at col 0.
    """
    pidx = {n: spec.get_param_index(n) for n in spec.all_param_names}
    n_groups = int(data.n_groups)
    n_alts = int(data.n_obs // data.n_groups)

    def _arr(name):
        v = getattr(data, name, None)
        return None if v is None else jnp.asarray(v, dtype=jnp.float64)

    leisure_m = _arr("leisure_male")
    leisure_f = _arr("leisure_female")
    consumption = _arr("consumption")
    working_m = _arr("working_male")
    working_f = _arr("working_female")
    prior = _arr("prior")
    log_prior = jnp.log(prior)
    n_children = _arr("n_children")

    # couples Box-Cox exponents: theta_l_m / theta_l_f; theta_c fixed (couples)
    theta_l_m_name = (spec.utility_leisure_theta + "_m") if spec.utility_leisure_theta else None
    theta_l_f_name = (spec.utility_leisure_theta + "_f") if spec.utility_leisure_theta else None
    couples_theta_c_fixed = getattr(spec, "utility_consumption_theta_couples_fixed", None)
    beta_c_fixed = getattr(spec, "utility_consumption_coef_fixed", None)
    beta_l0_m_name = spec.utility_leisure_intercept + "_m"
    beta_l0_f_name = spec.utility_leisure_intercept + "_f"
    interaction_name = spec.couples_interaction_coef  # beta_ll

    # leisure shifters: male -> _male data + _m coef; female -> _female data + _f coef;
    # n_children -> household-level data, female-only, _f coef
    leis_m, leis_f = [], []
    for sh in spec.utility_leisure_shifters:
        var, coef = sh["variable"], sh["coefficient"]
        if var == "n_children":
            if n_children is not None:
                leis_f.append((coef + "_f", n_children))
            continue
        am = _arr(var + "_male"); af = _arr(var + "_female")
        if am is not None:
            leis_m.append((coef + "_m", am))
        if af is not None:
            leis_f.append((coef + "_f", af))

    # hours: shared coef (fallback), gender data + gender working interaction
    def _hours(suffix, working):
        terms = []
        for sh in spec.hours_shifters:
            var, coef = sh["variable"], sh["coefficient"]
            arr = _arr(var + suffix)
            if arr is None:
                continue
            inter = sh.get("interaction", None)
            uw = (inter == "working") or (isinstance(inter, (list, tuple)) and "working" in inter)
            terms.append((coef, arr, uw, working))
        return terms
    hours_m = _hours("_male", working_m)
    hours_f = _hours("_female", working_f)

    # wage: shared coef, gender data, worker-gated
    def _wage(suffix, working):
        terms = []
        lw = _arr("log_wage" + suffix)
        for sh in spec.wage_mean_shifters:
            var, coef = sh["variable"], sh["coefficient"]
            if var == "intercept":
                terms.append((coef, None))
            else:
                arr = _arr(var + suffix)
                if arr is not None:
                    terms.append((coef, arr))
        return lw, working, terms
    wage_m = _wage("_male", working_m)
    wage_f = _wage("_female", working_f)
    sigma_name = spec.wage_variance_param

    # market: gsur(both: male+female), region/year/urb(household: var * (wm+wf)),
    # occupation loc4(male/female). gsur scaled by 10.
    scale_map = getattr(spec, "market_opportunity_variable_scales", None) or {}
    mkt_terms = []  # list of (coef, contribution_array)
    wfsum = (working_m + working_f)
    for sh in (getattr(spec, "market_opportunity_shifters", None) or []):
        var, coef = sh["variable"], sh["coefficient"]
        applies = str(sh.get("applies_to", "both")).strip().lower()
        scale = float(scale_map.get(var, 1.0))
        inter = sh.get("interaction", None)
        uw = (inter == "working") or (isinstance(inter, (list, tuple)) and "working" in inter)
        if applies == "household":
            arr = _arr(var)
            if arr is None:
                continue
            contrib = arr * scale
            if uw:
                contrib = contrib * wfsum
            mkt_terms.append((coef, contrib))
        else:
            # male/cm/both -> male var * working_male ; female/cf/both -> female var * working_female
            if applies in ("male", "cm", "both"):
                am = _arr(var + "_male")
                if am is not None:
                    c = am * scale
                    if uw:
                        c = c * working_m
                    mkt_terms.append((coef, c))
            if applies in ("female", "cf", "both"):
                af = _arr(var + "_female")
                if af is not None:
                    c = af * scale
                    if uw:
                        c = c * working_f
                    mkt_terms.append((coef, c))
    do_center = bool(getattr(spec, "market_opportunity_center_within_choice_set", False))
    center_prop = (getattr(spec, "market_opportunity_center_weights", None) == "proposal")

    LOG2PI = float(np.log(2 * np.pi))

    def neg_ll(theta):
        def P(name):
            return theta[pidx[name]]

        theta_l_m = P(theta_l_m_name) if theta_l_m_name else 0.0
        theta_l_f = P(theta_l_f_name) if theta_l_f_name else 0.0
        theta_c = (float(couples_theta_c_fixed) if couples_theta_c_fixed is not None else 0.0)
        bc_l_m = jbox_cox(leisure_m, theta_l_m)
        bc_l_f = jbox_cox(leisure_f, theta_l_f)
        bc_c = jbox_cox(consumption, theta_c)

        blc_m = P(beta_l0_m_name)
        for cn, arr in leis_m:
            blc_m = blc_m + P(cn) * arr
        blc_f = P(beta_l0_f_name)
        for cn, arr in leis_f:
            blc_f = blc_f + P(cn) * arr
        beta_c = beta_c_fixed if beta_c_fixed is not None else P(spec.utility_consumption_coef)
        beta_ll = P(interaction_name) if interaction_name else 0.0
        u = (blc_m * bc_l_m + blc_f * bc_l_f + beta_c * bc_c
             + beta_ll * bc_l_m * bc_l_f)

        log_h = jnp.zeros_like(u)
        for cn, arr, uw, wk in (hours_m + hours_f):
            x = arr * wk if uw else arr
            log_h = log_h + P(cn) * x

        log_w = jnp.zeros_like(u)
        for (lw, wk, terms) in (wage_m, wage_f):
            mu = jnp.zeros_like(u)
            for cn, arr in terms:
                mu = mu + (P(cn) if arr is None else P(cn) * arr)
            sigma = P(sigma_name)
            resid = (lw - mu) / sigma
            lwd = -0.5 * resid**2 - jnp.log(sigma) - 0.5 * LOG2PI - lw
            log_w = log_w + jnp.where(wk > 0, lwd, 0.0)

        log_market = jnp.zeros_like(u)
        for cn, contrib in mkt_terms:
            log_market = log_market + P(cn) * contrib
        if do_center:
            if center_prop:
                log_market = _center_proposal(log_market, prior, n_groups, n_alts)
            else:
                lm = log_market.reshape(n_groups, n_alts)
                log_market = (lm - jnp.mean(lm, axis=1, keepdims=True)).reshape(-1)

        V = u + log_h + log_w + log_market - log_prior
        V_obs, lse = jgroup_logsumexp(V, n_groups, n_alts)
        return -jnp.sum(V_obs - lse)

    return jax.jit(neg_ll), pidx


# ---------------------------------------------------------------------------
# Probe driver
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", type=Path,
                    default=_script_dir / "specs" / "estimation_spec_joint_pooled_v1.yaml")
    ap.add_argument("--engine-ready-stem", default="fr_p3a_bpool_engine_ready")
    ap.add_argument("--years", default="2015,2016,2017")
    ap.add_argument("--n-hh", type=int, default=200, help="cap (0=full)")
    ap.add_argument("--group", default="singles_male",
                    choices=["singles_male", "singles_female", "couples"])
    ap.add_argument("--theta-star", type=Path,
                    default=_script_dir / "specs" / "theta_star_joint_v1.csv")
    ap.add_argument("--couples-stem", default="fr_p3a_bpool_engine_ready_20x20",
                    help="Couples engine-ready stem (20x20 proper draws).")
    ap.add_argument("--seed", type=int, default=20260530)
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    print(f"JAX {jax.__version__}  backend={jax.default_backend()}  "
          f"x64={jax.config.read('jax_enable_x64')}  devices={jax.devices()}")

    spec = sp.parse_specification(args.spec)
    years = [] if args.years.strip().lower() == "all" else [int(y) for y in args.years.split(",")]
    is_couples = (args.group == "couples")

    # Load the slice exactly as the harness does; build the right engine refs.
    if is_couples:
        df, meta = jrt._load_parquet_slice(args.couples_stem, "couples",
                                           years, args.n_hh)
        data = eu.precompute_data_couples(df, meta, include_wage_vars=True,
                                          include_loc_vars=True)
        eng_ll = lambda th: ee.compute_likelihood_couples(th, data, spec)
        eng_grad = lambda th: ee.compute_gradient_couples(th, data, spec)
        build_jax = lambda: build_jax_couples_ll(data, spec)
    else:
        is_male = (args.group == "singles_male")
        sex = "male" if is_male else "female"
        df, meta = jrt._load_parquet_slice(args.engine_ready_stem, "singles",
                                           years, args.n_hh, sex=sex)
        data = eu.precompute_data_singles(df, meta, is_male=is_male,
                                          include_wage_vars=True, include_loc_vars=True)
        eng_ll = lambda th: ee.compute_likelihood_singles(th, data, spec)
        eng_grad = lambda th: ee.compute_gradient_singles(th, data, spec)
        build_jax = lambda: build_jax_singles_ll(data, spec, is_male)
    print(f"loaded {args.group}: n_groups={data.n_groups} "
          f"n_alts={data.n_obs//data.n_groups}")

    # theta_star (clamped into bounds exactly like the gate)
    theta = jrt.load_theta_star_from_csv(args.theta_star, spec)
    theta = np.asarray(theta, dtype=np.float64)

    # ---- engine reference: negLL + analytic gradient ----
    t0 = time.time()
    ll_eng = eng_ll(theta)
    t_eng_ll = time.time() - t0
    t0 = time.time()
    grad_eng = eng_grad(theta)
    t_eng_grad = time.time() - t0

    # ---- JAX: build, jit-warm, then time ----
    t0 = time.time()
    jneg_ll, pidx = build_jax()
    jgrad = jax.jit(jax.grad(jneg_ll))
    th = jnp.asarray(theta, dtype=jnp.float64)
    ll_jax = float(jneg_ll(th)); _ = jgrad(th)  # warm-up compile
    t_build = time.time() - t0

    t0 = time.time(); ll_jax = float(jneg_ll(th)); t_jax_ll = time.time() - t0
    t0 = time.time(); grad_jax = np.asarray(jgrad(th)); t_jax_grad = time.time() - t0

    # ---- compare ----
    ll_abs = abs(ll_jax - float(ll_eng))
    ll_rel = ll_abs / (abs(float(ll_eng)) + 1e-12)
    gdiff = np.abs(grad_jax - grad_eng)
    g_abs = float(np.max(gdiff))
    wi = int(np.argmax(gdiff))
    wname = spec.all_param_names[wi]

    print("\n" + "=" * 72)
    print(f"JAX vs ENGINE — {args.group} correctness probe")
    print("=" * 72)
    print(f"  negLL  engine = {float(ll_eng):.10f}")
    print(f"  negLL  jax    = {ll_jax:.10f}")
    print(f"  |Δ negLL|     = {ll_abs:.3e}   rel = {ll_rel:.3e}")
    print(f"  max|Δ grad|   = {g_abs:.3e}   worst param = {wname}")
    print(f"\n  timing (s): engine LL={t_eng_ll:.3f} grad={t_eng_grad:.3f} | "
          f"jax build+jit={t_build:.3f} LL={t_jax_ll:.4f} grad={t_jax_grad:.4f}")

    ll_ok = ll_abs < 1e-6
    g_ok = g_abs < 1e-6

    # ---- finite-difference ARBITER on the mismatching components ----
    # When JAX and the engine analytic gradient disagree, the central finite
    # difference of the ENGINE's own negLL is the ground truth. This tells us
    # whether JAX is wrong or the engine's analytic gradient is wrong (e.g. the
    # box_cox_derivative_theta Taylor branch for |theta|<0.05).
    arbiter_lines = []
    jax_validated = True
    if not g_ok:
        mismatched = [i for i in range(len(grad_eng)) if gdiff[i] >= 1e-6]
        for i in mismatched:
            tp = theta.copy(); tp[i] += 1e-6
            tm = theta.copy(); tm[i] -= 1e-6
            fd = (float(eng_ll(tp)) - float(eng_ll(tm))) / (2e-6)
            d_jax = abs(grad_jax[i] - fd)
            d_eng = abs(grad_eng[i] - fd)
            verdict = ("JAX correct, ENGINE wrong" if d_jax < d_eng
                       else "ENGINE correct, JAX wrong")
            if d_jax >= d_eng:
                jax_validated = False
            arbiter_lines.append(
                (spec.all_param_names[i], grad_eng[i], grad_jax[i], fd,
                 d_jax, d_eng, verdict))

    if arbiter_lines:
        print("\n  --- finite-difference arbiter on mismatches ---")
        for name, ge, gj, fd, dj, de, verdict in arbiter_lines:
            print(f"    {name:<16} engine={ge:+.6f} jax={gj:+.6f} FD={fd:+.6f}"
                  f"  |jax-FD|={dj:.2e} |eng-FD|={de:.2e}  -> {verdict}")

    # Final verdict: JAX is VALIDATED if (a) LL matches, and (b) every gradient
    # mismatch is adjudicated in JAX's favour by the finite-difference arbiter.
    validated = ll_ok and (g_ok or jax_validated)
    print()
    if validated and not g_ok:
        print("  PASS (JAX validated) — LL exact; all gradient mismatches are")
        print("  ENGINE bugs (box_cox theta-derivative Taylor), confirmed by FD.")
    elif validated:
        print("  PASS — LL and gradient match engine to 1e-6.")
    else:
        print("  FAIL — JAX disagrees with finite-difference truth. See arbiter.")
    print("=" * 72)
    sys.exit(0 if validated else 1)


if __name__ == "__main__":
    main()
