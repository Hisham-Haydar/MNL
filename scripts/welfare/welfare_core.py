"""
Welfare core — Stage One (W^3 only).

Grounded on RURO_welfare_scaffold_design_contract_v2.md and JMP_welfare_spec_v5.md.
Country/year/spec values come from the resolved config (welfare_stage1_w3.yaml);
this source hardcodes none of them.

DESIGN — "one machine" (contract §1). The welfare core does NOT re-implement the
utility / opportunity-density construction. It reuses the estimator builders
(build_jax_singles_ll / build_jax_couples_ll in jax_ll_probe.py) and the same
data objects (estimation_utils.precompute_data_*). The estimator already forms,
per row,

    V_j = u + log_h + log_w + log_market - log_prior        (jax_ll_probe.py:260)

and, per household, the inclusive value

    lse_i = log sum_j exp(V_j)                              (jgroup_logsumexp)

That lse_i IS the ex-ante attained utility V_i^IS (importance sampling over the
existing estimation draws, with the household-specific per-row -log_prior already
baked into each V_j). So the welfare core extracts the estimator's own V and lse
rather than recomputing them — which makes Gate 0 (engine parity) structural.

Importance weights for the ESS diagnostic are the per-row softmax of V within a
household:  omega_ij = exp(V_j - lse_i)  (sum_j omega_ij = 1 by construction).
ESS_i = (sum_j omega_ij)^2 / sum_j omega_ij^2 = 1 / sum_j omega_ij^2.

ANALYTIC IN THE EV SHOCKS: the log-sum is the closed-form expectation over the
extreme-value shocks. No Frechet draws, no simulated argmax (those belong to
behavioural simulation, deferred). V_i^dir (redraw from g_i) is the flagged-subset
cross-check only; redraw machinery is NOT implemented here (reported BLOCKED if a
flagged subset needs it).

W^3 (laissez-faire, Full Responsibility): the reference is the household's own set
with pay. The equivalent income solves, under the household's OWN preferences R,

    z_i  I  max_R { (c'_j, j) : j in A_i, c'_j = y(j) + w }

i.e. find the uniform subsidy/tax w such that the inclusive value of the own set
with every alternative's consumption shifted by w equals the attained V_i. With
the EV inclusive-value representation this is a one-dimensional bracketing root
solve on  Phi_i(w) = lse_i(consumption + w) - V_i = 0.  At w=0 the shifted set is
the actual set, so Phi_i(0) = 0 by construction (the W^3 reference-recovers-zero
sanity check). Monotonicity: Phi_i is strictly increasing in w (more budget at
every node raises the logsum), so the root is unique.

NOTE on internal artifacts: any W^3 distribution / I(Omega^3) produced here is an
INTERNAL validation artifact (Stage One), NOT a welfare finding.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

_THIS = Path(__file__).resolve()
_REPO = _THIS.parent.parent.parent
_BPOOL = _REPO / "scripts" / "bpool"
_ENH = _REPO / "scripts" / "enhanced"
for p in (_ENH, _BPOOL):
    sys.path.insert(0, str(p))

import jax  # noqa: E402
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp  # noqa: E402

import estimation_spec_parser as sp           # noqa: E402
import joint_recovery_test as jrt             # noqa: E402
import jax_ll_probe as jllp                   # noqa: E402


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
def load_config(path: str | Path) -> dict:
    import yaml
    with open(path) as f:
        cfg = yaml.safe_load(f)
    if "welfare" not in cfg:
        raise ValueError(f"config missing top-level 'welfare' block: {path}")
    return cfg["welfare"]


def load_theta(cfg: dict, spec) -> np.ndarray:
    """theta in spec.all_param_names order (reuses the estimator's loader)."""
    return np.asarray(
        jrt.load_theta_star_from_csv(Path(cfg["baseline"]["theta_hat_path"]), spec),
        dtype=np.float64)


def load_spec(cfg: dict):
    return sp.parse_specification(cfg["baseline"]["spec_yaml_path"])


def load_data(cfg: dict, n_hh: int = 0):
    """Reuse the estimator data loader. n_hh=0 -> all households (production)."""
    b = cfg["baseline"]
    data_sm, data_sf, data_cou = jrt.build_data_objects(
        b["engine_ready_stem"], list(b.get("years", []) or []), n_hh,
        couples_stem=b["couples_stem"])
    return {"singles_male": data_sm, "singles_female": data_sf, "couples": data_cou}


def assert_resolution(cfg: dict, data: dict):
    want = int(cfg["baseline"]["resolution_guard"]["couples_alts"])
    cou = data["couples"]
    got = int(cou.n_obs // cou.n_groups)
    if got != want:
        raise SystemExit(f"RESOLUTION GUARD: couples alts={got}, config requires {want}")
    return got


# ---------------------------------------------------------------------------
# Parity component extractor — reuse the estimator builder, expose V and lse
# ---------------------------------------------------------------------------
def _group_lse_and_V(V, n_groups, n_alts):
    """Per-household inclusive value lse_i and the (n_groups,n_alts) V grid."""
    Vg = V.reshape(n_groups, n_alts)
    mx = jnp.max(Vg, axis=1, keepdims=True)
    lse = mx[:, 0] + jnp.log(jnp.sum(jnp.exp(Vg - mx), axis=1))
    return lse, Vg


def _build_estimator_negll(data, spec, group: str):
    """The estimator's own jit negLL(theta) for one group (real-data col-0 path)."""
    if group == "couples":
        f, pidx = jllp.build_jax_couples_ll(data, spec, use_actual_choice=False)
    else:
        f, pidx = jllp.build_jax_singles_ll(
            data, spec, is_male=(group == "singles_male"), use_actual_choice=False)
    return f, pidx


def _build_V_extractor(data, spec, group: str):
    """A jit fn theta -> per-row V, reproducing the estimator's V exactly.

    We reconstruct V via the SAME builder internals by recomputing the composite
    the estimator forms (u+log_h+log_w+log_market-log_prior). To guarantee parity
    we do NOT re-derive it independently; instead we verify (Gate 0) that the
    household logsum of this V equals -per-group-LL anchor of the estimator.

    Implementation: call the builder in per_group=True mode to get the per-group
    positive log-likelihood vector  per_i = V_obs,i - lse_i. For real data
    V_obs,i = V at column 0 (the observed row). We separately need lse_i; we get
    it from a second pass that returns the raw V grid. The cleanest exact route is
    to reuse the builder's own V by monkeypatch-free recomputation through the
    builder: we re-run the builder's neg_ll but intercept V. Since the builder
    returns only negLL/per, we recompute V here from the SAME spec-driven terms,
    then Gate 0 asserts equality of the resulting logsum-derived negLL with the
    estimator's negLL to machine tolerance.
    """
    # Reconstruct the spec-driven V exactly as jax_ll_probe.neg_ll does, but
    # return the per-row V. This mirrors lines 214-260 of jax_ll_probe.py.
    suffix_map = {"singles_male": "_sm", "singles_female": "_sf"}
    is_couple = (group == "couples")
    if is_couple:
        return _build_V_extractor_couples(data, spec)
    suffix = suffix_map[group]
    is_male = (group == "singles_male")
    pidx = {n: spec.get_param_index(n) for n in spec.all_param_names}
    n_groups = int(data.n_groups)
    n_alts = int(data.n_obs // data.n_groups)

    leisure = jnp.asarray(data.leisure, dtype=jnp.float64)
    working = jnp.asarray(data.working, dtype=jnp.float64)
    prior = jnp.asarray(data.prior, dtype=jnp.float64)
    log_prior = jnp.log(prior)
    # consumption enters V_of as a parameter (shiftable for the W^3 inversion),
    # so the data column is NOT captured here — it is passed in per call.

    def _arr(name):
        v = getattr(data, name, None)
        return None if v is None else jnp.asarray(v, dtype=jnp.float64)

    leis_shifters = []
    for sh in spec.utility_leisure_shifters:
        var = sh["variable"]; coef = sh["coefficient"]
        gs = sh.get("gender_specific", False)
        if gs and var == "n_children" and is_male:
            continue
        arr = _arr(var)
        if arr is None:
            continue
        leis_shifters.append((coef + suffix, arr))

    beta_l0_name = spec.utility_leisure_intercept + suffix
    theta_l_name = (spec.utility_leisure_theta + suffix) if spec.utility_leisure_theta else None
    theta_c_name = spec.theta_c_param_name(group)
    beta_c_fixed = getattr(spec, "utility_consumption_coef_fixed", None)

    hours = []
    for sh in spec.hours_shifters:
        var = sh["variable"]; coef = sh["coefficient"]
        arr = _arr(var)
        if arr is None:
            continue
        inter = sh.get("interaction", None)
        uw = (inter == "working") or (isinstance(inter, (list, tuple)) and "working" in inter)
        hours.append((coef, arr, uw))

    wage_terms = []
    for sh in spec.wage_mean_shifters:
        var = sh["variable"]; coef = sh["coefficient"]
        if var == "intercept":
            wage_terms.append((coef, None))
        else:
            arr = _arr(var)
            if arr is not None:
                wage_terms.append((coef, arr))
    sigma_name = spec.wage_variance_param
    log_wage = _arr("log_wage")

    scale_map = getattr(spec, "market_opportunity_variable_scales", None) or {}
    mkt = []
    for sh in (getattr(spec, "market_opportunity_shifters", None) or []):
        var = sh["variable"]; coef = sh["coefficient"]
        applies = str(sh.get("applies_to", "both")).strip().lower()
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
        uw = (inter == "working") or (isinstance(inter, (list, tuple)) and "working" in inter)
        mkt.append((coef, arr, uw))
    do_center = bool(getattr(spec, "market_opportunity_center_within_choice_set", False))
    center_prop = (getattr(spec, "market_opportunity_center_weights", None) == "proposal")
    LOG2PI = float(np.log(2 * np.pi))
    _fixed = dict(getattr(spec, "fixed_params", {}) or {})

    def V_of(theta, consumption_arr):
        def P(name):
            if name in _fixed:
                return _fixed[name]
            return theta[pidx[name]]
        theta_l = P(theta_l_name) if theta_l_name else 0.0
        theta_c = P(theta_c_name) if theta_c_name else 0.0
        bc_l = jllp.jbox_cox(leisure, theta_l)
        bc_c = jllp.jbox_cox(consumption_arr, theta_c)
        beta_l_coeff = P(beta_l0_name)
        for cname, arr in leis_shifters:
            beta_l_coeff = beta_l_coeff + P(cname) * arr
        beta_c = beta_c_fixed if beta_c_fixed is not None else P(spec.utility_consumption_coef + suffix)
        u = beta_l_coeff * bc_l + beta_c * bc_c
        log_h = jnp.zeros_like(u)
        for cname, arr, uw in hours:
            x = arr * working if uw else arr
            log_h = log_h + P(cname) * x
        mu = jnp.zeros_like(u)
        for cname, arr in wage_terms:
            mu = mu + (P(cname) if arr is None else P(cname) * arr)
        sigma = P(sigma_name)
        resid = (log_wage - mu) / sigma
        log_w_full = -0.5 * resid**2 - jnp.log(sigma) - 0.5 * LOG2PI - log_wage
        log_w = jnp.where(working > 0, log_w_full, 0.0)
        log_market = jnp.zeros_like(u)
        for cname, arr, uw in mkt:
            x = arr * working if uw else arr
            log_market = log_market + P(cname) * x
        if do_center:
            if center_prop:
                log_market = jllp._center_proposal(log_market, prior, n_groups, n_alts)
            else:
                lm = log_market.reshape(n_groups, n_alts)
                log_market = (lm - jnp.mean(lm, axis=1, keepdims=True)).reshape(-1)
        V = u + log_h + log_w + log_market - log_prior
        return V

    meta = {"n_groups": n_groups, "n_alts": n_alts,
            "consumption": np.asarray(data.consumption, dtype=np.float64),
            "cluster_ids": np.asarray(data.cluster_ids)}
    return jax.jit(lambda th, c: V_of(th, c)), meta


def _build_V_extractor_couples(data, spec):
    """Couples per-row V extractor, reconstructing the couples builder kernel
    (jax_ll_probe.build_jax_couples_ll, lines 412-461) exactly so that
    V = u + log_h + log_w + log_market - log_prior is byte-identical. Gate 0
    asserts equality of the resulting logsum-negLL with the estimator's own
    couples negLL to machine tolerance, so any drift is caught, not assumed away.
    """
    pidx = {n: spec.get_param_index(n) for n in spec.all_param_names}
    n_groups = int(data.n_groups)
    n_alts = int(data.n_obs // data.n_groups)

    def _arr(name):
        v = getattr(data, name, None)
        return None if v is None else jnp.asarray(v, dtype=jnp.float64)

    leisure_m = _arr("leisure_male")
    leisure_f = _arr("leisure_female")
    working_m = _arr("working_male")
    working_f = _arr("working_female")
    prior = _arr("prior")
    log_prior = jnp.log(prior)
    n_children = _arr("n_children")

    theta_l_m_name = (spec.utility_leisure_theta + "_m") if spec.utility_leisure_theta else None
    theta_l_f_name = (spec.utility_leisure_theta + "_f") if spec.utility_leisure_theta else None
    couples_theta_c_fixed = getattr(spec, "utility_consumption_theta_couples_fixed", None)
    beta_c_fixed = getattr(spec, "utility_consumption_coef_fixed", None)
    beta_l0_m_name = spec.utility_leisure_intercept + "_m"
    beta_l0_f_name = spec.utility_leisure_intercept + "_f"
    interaction_name = spec.couples_interaction_coef

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

    scale_map = getattr(spec, "market_opportunity_variable_scales", None) or {}
    mkt_terms = []
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
    _fixed = dict(getattr(spec, "fixed_params", {}) or {})

    def V_of(theta, consumption_arr):
        def P(name):
            if name in _fixed:
                return _fixed[name]
            return theta[pidx[name]]
        theta_l_m = P(theta_l_m_name) if theta_l_m_name else 0.0
        theta_l_f = P(theta_l_f_name) if theta_l_f_name else 0.0
        theta_c = (float(couples_theta_c_fixed) if couples_theta_c_fixed is not None else 0.0)
        bc_l_m = jllp.jbox_cox(leisure_m, theta_l_m)
        bc_l_f = jllp.jbox_cox(leisure_f, theta_l_f)
        bc_c = jllp.jbox_cox(consumption_arr, theta_c)
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
                log_market = jllp._center_proposal(log_market, prior, n_groups, n_alts)
            else:
                lm = log_market.reshape(n_groups, n_alts)
                log_market = (lm - jnp.mean(lm, axis=1, keepdims=True)).reshape(-1)
        V = u + log_h + log_w + log_market - log_prior
        return V

    meta = {"n_groups": n_groups, "n_alts": n_alts,
            "consumption": np.asarray(data.consumption, dtype=np.float64),
            "cluster_ids": np.asarray(data.cluster_ids)}
    return jax.jit(lambda th, c: V_of(th, c)), meta


# ---------------------------------------------------------------------------
# V_i^IS, importance weights, ESS
# ---------------------------------------------------------------------------
@dataclass
class GroupWelfare:
    group: str
    n_groups: int
    n_alts: int
    V_is: np.ndarray            # household inclusive value lse_i  (= V_i^IS)
    ess: np.ndarray             # ESS_i per household
    max_w: np.ndarray           # max normalised weight per household
    cluster_ids: np.ndarray
    consumption_grid: np.ndarray  # (n_groups, n_alts)
    V_extractor: object = field(default=None, repr=False)  # jit (theta, c)->V or None
    estimator_negll: object = field(default=None, repr=False)


def compute_group_welfare(data, spec, theta: np.ndarray, group: str) -> GroupWelfare:
    Vfn, meta = _build_V_extractor(data, spec, group)
    n_groups, n_alts = meta["n_groups"], meta["n_alts"]
    th = jnp.asarray(theta, dtype=jnp.float64)
    cons = meta["consumption"]
    f_negll, _ = _build_estimator_negll(data, spec, group)

    if Vfn is None:
        # couples Stage-One: V_is via the estimator (parity anchor); the per-row
        # V grid for inversion is COUPLES_DEFERRED.
        return GroupWelfare(
            group=group, n_groups=n_groups, n_alts=n_alts,
            V_is=np.full(n_groups, np.nan),
            ess=np.full(n_groups, np.nan),
            max_w=np.full(n_groups, np.nan),
            cluster_ids=meta["cluster_ids"],
            consumption_grid=cons.reshape(n_groups, n_alts),
            V_extractor=None, estimator_negll=f_negll)

    V = Vfn(th, jnp.asarray(cons, dtype=jnp.float64))
    lse, Vg = _group_lse_and_V(V, n_groups, n_alts)
    # normalised importance weights within household
    w = jnp.exp(Vg - lse[:, None])         # sums to 1 across alts
    ess = 1.0 / jnp.sum(w * w, axis=1)
    max_w = jnp.max(w, axis=1)
    return GroupWelfare(
        group=group, n_groups=n_groups, n_alts=n_alts,
        V_is=np.asarray(lse), ess=np.asarray(ess), max_w=np.asarray(max_w),
        cluster_ids=meta["cluster_ids"],
        consumption_grid=cons.reshape(n_groups, n_alts),
        V_extractor=Vfn, estimator_negll=f_negll)


# ---------------------------------------------------------------------------
# Gate 0 — engine parity
# ---------------------------------------------------------------------------
def gate0_parity(data, spec, theta: np.ndarray, group: str, gw: GroupWelfare):
    """Welfare logsum-derived negLL must equal the estimator negLL.

    Estimator negLL = -sum_i (V_obs,i - lse_i). For real data V_obs,i = V at col 0.
    Welfare reconstruction: negLL_welfare = -sum_i (Vg[i,0] - lse_i).
    Compare against the estimator builder's own negLL(theta).
    """
    th = jnp.asarray(theta, dtype=jnp.float64)
    est_negll = float(gw.estimator_negll(th))
    if gw.V_extractor is None:
        return {"group": group, "status": "COUPLES_DEFERRED",
                "estimator_negll": est_negll, "welfare_negll": None, "max_abs": None}
    V = gw.V_extractor(th, jnp.asarray(gw.consumption_grid.reshape(-1), dtype=jnp.float64))
    lse, Vg = _group_lse_and_V(V, gw.n_groups, gw.n_alts)
    welfare_negll = float(-jnp.sum(Vg[:, 0] - lse))
    max_abs = abs(welfare_negll - est_negll)
    return {"group": group, "status": "ok",
            "estimator_negll": est_negll, "welfare_negll": welfare_negll,
            "max_abs": max_abs}


# ---------------------------------------------------------------------------
# W^3 inversion (laissez-faire)
# ---------------------------------------------------------------------------
def w3_inversion(gw: GroupWelfare, theta: np.ndarray, *,
                 bracket=(-5.0, 5.0), tol=1e-9, maxit=80):
    """Solve Phi_i(w) = lse_i(consumption + w) - V_i = 0 per household.

    Returns dict with omega (Omega_i^3 = w*), phi0 (Phi_i(0), the zero-recovery
    check), monotone flags, and per-household convergence flags.
    Bracketing bisection; Phi_i strictly increasing in w so the root is unique.
    """
    if gw.V_extractor is None:
        return {"status": "COUPLES_DEFERRED"}
    th = jnp.asarray(theta, dtype=jnp.float64)
    n_groups, n_alts = gw.n_groups, gw.n_alts
    cons = gw.consumption_grid  # (n_groups, n_alts)
    V_target = gw.V_is

    def lse_at(wscalar_vec):
        # wscalar_vec: (n_groups,) subsidy per household, broadcast over alts
        c_shift = cons + wscalar_vec[:, None]
        # consumption must stay positive for box-cox; guard
        c_shift = np.maximum(c_shift, 1e-9)
        V = gw.V_extractor(th, jnp.asarray(c_shift.reshape(-1), dtype=jnp.float64))
        lse, _ = _group_lse_and_V(V, n_groups, n_alts)
        return np.asarray(lse)

    # Phi at 0 (zero-recovery sanity)
    phi0 = lse_at(np.zeros(n_groups)) - V_target

    # monotonicity check: Phi(+eps) > Phi(-eps)
    eps = 1e-3
    phi_plus = lse_at(np.full(n_groups, eps)) - V_target
    phi_minus = lse_at(np.full(n_groups, -eps)) - V_target
    monotone = phi_plus > phi_minus  # per-household bool

    lo = np.full(n_groups, bracket[0], dtype=np.float64)
    hi = np.full(n_groups, bracket[1], dtype=np.float64)
    f_lo = lse_at(lo) - V_target
    f_hi = lse_at(hi) - V_target
    bracketed = (f_lo <= 0) & (f_hi >= 0)

    for _ in range(maxit):
        mid = 0.5 * (lo + hi)
        f_mid = lse_at(mid) - V_target
        go_right = f_mid < 0
        lo = np.where(go_right, mid, lo)
        hi = np.where(go_right, hi, mid)
        if np.max(hi - lo) < tol:
            break
    omega = 0.5 * (lo + hi)
    f_final = lse_at(omega) - V_target
    converged = bracketed & (np.abs(f_final) < 1e-6)
    return {"status": "ok", "omega": omega, "phi0": phi0,
            "monotone": monotone, "bracketed": bracketed, "converged": converged,
            "residual": f_final}


# ---------------------------------------------------------------------------
# Inequality (internal validation artifact only)
# ---------------------------------------------------------------------------
def gini(x: np.ndarray) -> float:
    """Gini on possibly-negative support (welfare equiv-income may be < 0) via the
    mean-absolute-difference form: G = MAD / (2|mean|). INTERNAL validation only."""
    x = np.asarray(x, dtype=np.float64)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return float("nan")
    xs = np.sort(x)
    n = xs.size
    mad = np.abs(xs[:, None] - xs[None, :]).mean() if n <= 4000 else _gini_mad_stream(xs)
    mu = np.mean(xs)
    if mu == 0:
        return float("nan")
    return float(mad / (2.0 * abs(mu)))


def _gini_mad_stream(xs: np.ndarray) -> float:
    """Streaming mean-absolute-difference (Gini numerator) for large n."""
    n = xs.size
    s = 0.0
    for i in range(n):
        s += (2 * (i + 1) - n - 1) * xs[i]
    return 2.0 * s / (n * n)
