"""
==============================================================================
RURO Post-Estimation Diagnostics Bundle
==============================================================================

A specification-agnostic, model-aware, solver-aware diagnostics object that
both the styled HTML report and the LLM Markdown summary consume.

Design goals
------------
* One normalized representation. HTML and Markdown render the same numbers.
* Sections are dynamic: each section carries ``available`` + ``unavailable_reason``
  so the renderer can either render the section or say *why it is missing*.
* Metric registry: every metric carries label, category, source, applicability,
  interpretation note, display precision, warning threshold, profile membership.
* Reorganized fit-statistics:
    A. Core likelihood and sample statistics
    B. Null-model and pseudo-R² diagnostics
    C. Bound / fixed-parameter diagnostics
    D. Economic sanity diagnostics  (NOT model-fit; surfaced separately)
* Profiles: ``decision`` / ``standard`` / ``full`` / ``technical`` filter which
  metrics and sections are rendered.

This module is *purely additive* to the existing post-estimation script. The
legacy combined "Model Fit Statistics" dump is preserved as a collapsed
appendix in both HTML and Markdown so nothing existing breaks; the four
reorganized sections are rendered alongside it.

Author: Enhanced RURO Pipeline
Created: 2026-05-22
==============================================================================
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


LOGGER = logging.getLogger(__name__)


# ==============================================================================
# Profile vocabulary
# ==============================================================================

PROFILE_CHOICES: Tuple[str, ...] = ("decision", "standard", "full", "technical")
DEFAULT_PROFILE: str = "standard"


# ==============================================================================
# Metric registry
# ==============================================================================

@dataclass(frozen=True)
class MetricSpec:
    """One entry in the metric registry."""
    key: str
    label: str
    category: str           # 'core' | 'null' | 'bounds' | 'economic' | 'solver' | 'inference' | 'hessian' | 'gradient' | 'data'
    source: str             # human-readable source path (informational)
    applicability: str      # when this metric is meaningful (free text)
    interpretation: str
    precision: int = 4
    threshold: Optional[str] = None
    profiles: Tuple[str, ...] = PROFILE_CHOICES  # which profiles include it
    appendix_only: bool = False                  # if True, only shown in technical profile

    def for_profile(self, profile: str) -> bool:
        if profile not in self.profiles:
            return False
        if self.appendix_only and profile != "technical":
            return False
        return True


# Registry. Add metrics here; renderers consult this to know how to format and
# whether to include a given metric for a given profile.
METRIC_REGISTRY: Dict[str, MetricSpec] = {m.key: m for m in [
    # A. Core likelihood and sample
    MetricSpec("log_likelihood", "Log-likelihood",
               category="core", source="results_json.summary.joint_ll",
               applicability="Always available when estimation converged.",
               interpretation="Higher (less negative) is better. Comparable only across runs with identical sample, alternative set, and prior weights.",
               precision=4),
    MetricSpec("n_observations", "Observations (rows)",
               category="core", source="results_json.summary.n_obs_total",
               applicability="Always.",
               interpretation="Long-format alternative-level row count.",
               precision=0),
    MetricSpec("n_groups", "Choice sets / groups",
               category="core", source="results_json.summary.n_groups_total",
               applicability="Always.",
               interpretation="Number of decision units (households).",
               precision=0),
    MetricSpec("n_alts_per_set", "Alternatives per choice set",
               category="core", source="derived: n_observations / n_groups",
               applicability="When n_groups > 0.",
               interpretation="Average alternatives per decision unit (may not be integer if unbalanced).",
               precision=2),
    MetricSpec("n_free_parameters", "Free parameters",
               category="core", source="parsed.bounds + theta",
               applicability="Always.",
               interpretation="Parameters being estimated freely (not fixed and not at a tight bound range).",
               precision=0),
    MetricSpec("n_fixed_parameters", "Fixed parameters",
               category="core", source="parsed.bounds (lb == ub)",
               applicability="Always.",
               interpretation="Parameters with lb == ub or fixed by spec.",
               precision=0),
    MetricSpec("AIC", "AIC",
               category="core", source="-2*ll + 2*k",
               applicability="Meaningful for nested or same-sample comparisons.",
               interpretation="Lower is better. Comparable only between models on the same data with the same null structure.",
               precision=4),
    MetricSpec("BIC", "BIC",
               category="core", source="-2*ll + log(n)*k",
               applicability="Meaningful for nested or same-sample comparisons.",
               interpretation="Lower is better. Penalises parameter count more than AIC.",
               precision=4),
    MetricSpec("AIC_per_obs", "AIC / n_obs",
               category="core", source="AIC / n_observations",
               applicability="When n_observations > 0.",
               interpretation="Per-observation AIC for cross-sample comparison sanity check.",
               precision=6),

    # B. Null-model / pseudo-R²
    MetricSpec("ll_null_uniform", "ll_null (uniform)",
               category="null", source="compute_null_log_likelihood",
               applicability="Requires data parquet to be readable.",
               interpretation="Log-likelihood of the uniform-choice null model.",
               precision=4),
    MetricSpec("ll_null_prior_corrected", "ll_null (prior-corrected)",
               category="null", source="compute_null_log_likelihood_prior_corrected",
               applicability="Requires data parquet with proposal/prior weights.",
               interpretation="Recommended null for sampled-alternative / job-choice models.",
               precision=4),
    MetricSpec("rho_squared_uniform", "ρ² (McFadden, uniform null)",
               category="null", source="1 - ll/ll_null_uniform",
               applicability="When ll_null_uniform is available and non-zero.",
               interpretation="0.2–0.4 is typically a 'good' fit for MNL. Comparable only across models with same uniform null structure.",
               precision=4),
    MetricSpec("rho_squared_prior_corrected", "ρ² (prior-corrected null)",
               category="null", source="1 - ll/ll_null_prior_corrected",
               applicability="When ll_null_prior_corrected is available and non-zero.",
               interpretation="The right pseudo-R² for sampled-alternative or job-choice models.",
               precision=4),
    MetricSpec("rho_squared_adj_uniform", "Adj. ρ² (uniform)",
               category="null", source="1 - (ll-k)/ll_null_uniform",
               applicability="When ll_null_uniform is available and non-zero.",
               interpretation="Penalises additional parameters.",
               precision=4),
    MetricSpec("rho_squared_adj_prior_corrected", "Adj. ρ² (prior-corrected)",
               category="null", source="1 - (ll-k)/ll_null_prior_corrected",
               applicability="When ll_null_prior_corrected is available and non-zero.",
               interpretation="Penalised pseudo-R² against the correct null.",
               precision=4),

    # C. Bound / fixed parameters
    MetricSpec("n_parameters", "Parameters (total)",
               category="bounds", source="parsed.param_names",
               applicability="Always.",
               interpretation="Total parameters in the specification.",
               precision=0),
    MetricSpec("n_parameters_with_bounds", "Parameters with bounds",
               category="bounds", source="parsed.bounds",
               applicability="When bounds are loaded.",
               interpretation="Parameters with at least one finite bound.",
               precision=0),
    MetricSpec("n_at_lower_bound", "At lower bound",
               category="bounds", source="abs(theta - lb) < tol",
               applicability="When bounds are present.",
               interpretation="0 is preferred. Non-zero usually indicates a binding economic constraint or a misspecified bound.",
               precision=0, threshold="warn if > 0"),
    MetricSpec("n_at_upper_bound", "At upper bound",
               category="bounds", source="abs(theta - ub) < tol",
               applicability="When bounds are present.",
               interpretation="0 is preferred. Non-zero may indicate truncation by spec.",
               precision=0, threshold="warn if > 0"),

    # D. Economic sanity
    MetricSpec("negative_muc_count", "Households with MUC < 0",
               category="economic", source="mu_results.totals",
               applicability="When MU diagnostics were computed.",
               interpretation="Count of households where marginal utility of consumption is non-positive at the chosen alternative.",
               precision=0, threshold="warn if > 0"),
    MetricSpec("negative_muc_pct", "% households with MUC < 0",
               category="economic", source="mu_results.totals",
               applicability="When MU diagnostics were computed.",
               interpretation="Share of households violating MUC > 0.",
               precision=2, threshold="warn if > 1%"),
    MetricSpec("negative_mul_count", "Households with MUL < 0",
               category="economic", source="mu_results.totals",
               applicability="When MU diagnostics were computed.",
               interpretation="Count of households where marginal utility of leisure is non-positive at the chosen alternative.",
               precision=0, threshold="warn if > 0"),
    MetricSpec("negative_mul_pct", "% households with MUL < 0",
               category="economic", source="mu_results.totals",
               applicability="When MU diagnostics were computed.",
               interpretation="Share of households violating MUL > 0.",
               precision=2, threshold="warn if > 1%"),

    # Solver
    MetricSpec("solver_name", "Solver",
               category="solver", source="results_json.metadata.opt_method or summary.solver",
               applicability="Always.",
               interpretation="Name of the optimization engine that produced the estimates.",
               precision=0),
    MetricSpec("solver_status", "Solver status",
               category="solver", source="results.<group>.message or listing file",
               applicability="When solver reports a status.",
               interpretation="'Optimal' / 'Normal Completion' indicate clean convergence.",
               precision=0),
    MetricSpec("model_status", "Model status",
               category="solver", source="listing file",
               applicability="CONOPT/GAMS only.",
               interpretation="GAMS model-status code, e.g. 'Locally Optimal'.",
               precision=0),
    MetricSpec("rgmax", "Reduced-gradient max (RGmax)",
               category="solver", source="solver.log / solver.lst (CONOPT)",
               applicability="CONOPT / GAMSPy runs only; requires solver log or listing.",
               interpretation="Solver-internal reduced-gradient norm at termination. DISTINCT from Python likelihood gradient at θ.",
               precision=6),

    # Gradient (Python score)
    MetricSpec("grad_inf_norm", "‖∇ log L‖∞ (Python score)",
               category="gradient", source="--gradient-diagnostics",
               applicability="When --gradient-diagnostics is supplied with --mnl-base and --spec-config.",
               interpretation="Infinity norm of the Python likelihood gradient at converged θ. NOT necessarily the solver reduced gradient when bounds or constraints are active.",
               precision=6),
    MetricSpec("grad_l2_norm", "‖∇ log L‖₂ (Python score)",
               category="gradient", source="--gradient-diagnostics",
               applicability="When --gradient-diagnostics is supplied.",
               interpretation="L2 norm of the Python likelihood gradient at converged θ.",
               precision=6),

    # Hessian
    MetricSpec("hessian_cond_number", "Hessian condition number",
               category="hessian", source="results_json.hessian_diagnostics or cluster-SE JSON",
               applicability="When Hessian is invertible.",
               interpretation="Large values (≫ 1e10) signal weak identification or near-singular Hessian.",
               precision=2, threshold="warn if > 1e10"),
    MetricSpec("hessian_n_negative_eigs", "Hessian negative eigenvalues",
               category="hessian", source="np.linalg.eigvalsh(H)",
               applicability="When Hessian is available.",
               interpretation="Should be 0 at a local optimum of the *negative* log-likelihood. >0 indicates saddle or non-optimal.",
               precision=0, threshold="warn if > 0"),
]}


def get_metric(key: str) -> Optional[MetricSpec]:
    return METRIC_REGISTRY.get(key)


# ==============================================================================
# DiagnosticsBundle dataclass
# ==============================================================================

@dataclass
class Section:
    """A bundle section with availability + reason."""
    available: bool = False
    unavailable_reason: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagnosticsBundle:
    """Normalized diagnostics object consumed by HTML + Markdown renderers."""
    profile: str = DEFAULT_PROFILE

    estimation_metadata: Dict[str, Any] = field(default_factory=dict)
    data_metadata: Dict[str, Any] = field(default_factory=dict)
    spec_metadata: Dict[str, Any] = field(default_factory=dict)

    solver: Section = field(default_factory=Section)
    likelihood_fit_core: Section = field(default_factory=Section)
    null_model_fit: Section = field(default_factory=Section)
    bounds_diagnostics: Section = field(default_factory=Section)
    economic_sanity: Section = field(default_factory=Section)
    inference: Section = field(default_factory=Section)
    robust_se: Section = field(default_factory=Section)
    hessian: Section = field(default_factory=Section)
    gradient_score: Section = field(default_factory=Section)
    probability_fit: Section = field(default_factory=Section)

    reproducibility: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ==============================================================================
# Builders
# ==============================================================================

def _safe_num(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        f = float(x)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


def _safe_int(x: Any) -> Optional[int]:
    f = _safe_num(x)
    return int(f) if f is not None else None


def build_diagnostics_bundle(
    *,
    profile: str,
    results_data: Dict[str, Any],
    parsed_params: Any,
    fit_stats: Dict[str, Any],
    bound_diagnostics: List[Dict[str, Any]],
    mu_results: Optional[Dict[str, Any]] = None,
    prob_diagnostics: Optional[Dict[str, Any]] = None,
    hessian_diagnostics: Optional[Dict[str, Any]] = None,
    cluster_se_data: Optional[Dict[str, Any]] = None,
    solver_diag: Optional[Dict[str, Any]] = None,
    gradient_diag: Optional[Dict[str, Any]] = None,
    repro_meta: Optional[Dict[str, Any]] = None,
    run_metadata: Optional[Dict[str, Any]] = None,
) -> DiagnosticsBundle:
    """Assemble a DiagnosticsBundle from already-computed pieces.

    All optional inputs degrade gracefully: missing pieces produce sections
    with ``available=False`` and a human-readable ``unavailable_reason``.
    """
    if profile not in PROFILE_CHOICES:
        LOGGER.warning("Unknown profile %r, falling back to %r", profile, DEFAULT_PROFILE)
        profile = DEFAULT_PROFILE

    bundle = DiagnosticsBundle(profile=profile)
    metadata = results_data.get("metadata", {}) or {}
    summary = results_data.get("summary", {}) or {}

    # --- estimation metadata
    bundle.estimation_metadata = {
        "specification": results_data.get("specification"),
        "wage_spec": results_data.get("wage_spec"),
        "group": metadata.get("group"),
        "opt_method": metadata.get("opt_method"),
        "analytical_gradient": metadata.get("analytical_gradient"),
        "command_line": results_data.get("command_line"),
        "timestamp": results_data.get("timestamp"),
    }

    # --- data metadata
    n_obs = _safe_int(summary.get("n_obs_total")) or _safe_int(fit_stats.get("n_observations"))
    n_groups = _safe_int(summary.get("n_groups_total")) or _safe_int(fit_stats.get("n_groups"))
    n_alts_per_set = None
    if n_obs and n_groups:
        n_alts_per_set = n_obs / n_groups
    bundle.data_metadata = {
        "n_observations": n_obs,
        "n_groups": n_groups,
        "n_alts_per_set": n_alts_per_set,
        "n_obs_long": _safe_int(fit_stats.get("n_obs_long")),
        "mnl_base": metadata.get("mnl_base"),
    }

    # --- spec metadata
    bundle.spec_metadata = {
        "spec_config": metadata.get("spec_config"),
        "n_parameters": _safe_int(fit_stats.get("n_parameters")) or len(getattr(parsed_params, "param_names", []) or []),
    }

    # --- bounds diagnostics (always available; values may be zero)
    n_params = bundle.spec_metadata["n_parameters"] or 0
    n_with_bounds = 0
    n_at_lower = 0
    n_at_upper = 0
    n_fixed = 0
    near_bound_list: List[Dict[str, Any]] = []
    bounds = getattr(parsed_params, "bounds", None)
    theta = getattr(parsed_params, "theta", None)
    names = getattr(parsed_params, "param_names", None) or []
    tol_bound = 1e-6
    tol_near = 1e-3
    if bounds is not None and theta is not None:
        for i, name in enumerate(names):
            if i >= len(bounds):
                continue
            lb, ub = bounds[i]
            if lb is not None or ub is not None:
                n_with_bounds += 1
            if lb is not None and ub is not None and abs(float(ub) - float(lb)) <= tol_bound:
                n_fixed += 1
                continue
            try:
                v = float(theta[i])
            except (TypeError, ValueError, IndexError):
                continue
            if lb is not None and abs(v - float(lb)) < tol_bound:
                n_at_lower += 1
                near_bound_list.append({"parameter": name, "estimate": v, "bound": float(lb), "side": "lower", "distance": 0.0})
            elif ub is not None and abs(v - float(ub)) < tol_bound:
                n_at_upper += 1
                near_bound_list.append({"parameter": name, "estimate": v, "bound": float(ub), "side": "upper", "distance": 0.0})
            elif lb is not None and (v - float(lb)) < tol_near:
                near_bound_list.append({"parameter": name, "estimate": v, "bound": float(lb), "side": "near_lower", "distance": v - float(lb)})
            elif ub is not None and (float(ub) - v) < tol_near:
                near_bound_list.append({"parameter": name, "estimate": v, "bound": float(ub), "side": "near_upper", "distance": float(ub) - v})

    n_free = max(0, (n_params or 0) - n_fixed)
    bundle.spec_metadata["n_free_parameters"] = n_free
    bundle.spec_metadata["n_fixed_parameters"] = n_fixed
    bundle.spec_metadata["n_parameters_with_bounds"] = n_with_bounds

    bundle.bounds_diagnostics = Section(
        available=True,
        data={
            "n_parameters": n_params,
            "n_free_parameters": n_free,
            "n_fixed_parameters": n_fixed,
            "n_parameters_with_bounds": n_with_bounds,
            "n_at_lower_bound": n_at_lower,
            "n_at_upper_bound": n_at_upper,
            "at_or_near_bounds": near_bound_list,
            "tol_at_bound": tol_bound,
            "tol_near_bound": tol_near,
        },
    )

    # --- A. core likelihood-fit
    ll = _safe_num(fit_stats.get("log_likelihood"))
    aic = _safe_num(fit_stats.get("AIC"))
    bic = _safe_num(fit_stats.get("BIC"))
    aic_per_obs = _safe_num(fit_stats.get("AIC_per_obs"))
    bundle.likelihood_fit_core = Section(
        available=ll is not None,
        unavailable_reason="" if ll is not None else "log_likelihood not present in fit_stats.",
        data={
            "log_likelihood": ll,
            "n_observations": n_obs,
            "n_groups": n_groups,
            "n_alts_per_set": n_alts_per_set,
            "n_free_parameters": n_free,
            "n_fixed_parameters": n_fixed,
            "AIC": aic,
            "BIC": bic,
            "AIC_per_obs": aic_per_obs,
        },
    )

    # --- B. null-model / pseudo-R²
    ll_null_uni = _safe_num(fit_stats.get("ll_null_uniform"))
    ll_null_prior = _safe_num(fit_stats.get("ll_null_prior_corrected"))
    rho2_uni = _safe_num(fit_stats.get("rho_squared_uniform"))
    rho2_prior = _safe_num(fit_stats.get("rho_squared_prior_corrected"))
    rho2_adj_uni = _safe_num(fit_stats.get("rho_squared_adj_uniform"))
    rho2_adj_prior = _safe_num(fit_stats.get("rho_squared_adj_prior_corrected"))
    null_available = any(v is not None for v in (ll_null_uni, ll_null_prior))
    bundle.null_model_fit = Section(
        available=null_available,
        unavailable_reason=("" if null_available else
                            "No null log-likelihood available. Supply --mnl-base so the script can read the parquet data and compute LL0."),
        data={
            "ll_null_uniform": ll_null_uni,
            "ll_null_prior_corrected": ll_null_prior,
            "rho_squared_uniform": rho2_uni,
            "rho_squared_prior_corrected": rho2_prior,
            "rho_squared_adj_uniform": rho2_adj_uni,
            "rho_squared_adj_prior_corrected": rho2_adj_prior,
            "note": ("ρ² values use McFadden's formulation 1 - LL/LL0. "
                     "For sampled-alternative / job-choice models the prior-corrected null is the right comparison; "
                     "the uniform null is kept for legacy comparability."),
        },
    )

    # --- D. economic sanity
    econ_data = {}
    if mu_results and isinstance(mu_results, dict):
        totals = mu_results.get("totals", {}) or {}
        for k in ("negative_muc_count", "negative_muc_pct",
                  "negative_mul_count", "negative_mul_pct",
                  "negative_mu_count", "negative_mu_pct",
                  "monotonicity_violations"):
            if k in totals:
                econ_data[k] = totals.get(k)
    bundle.economic_sanity = Section(
        available=bool(econ_data),
        unavailable_reason=("" if econ_data else
                            "Marginal-utility diagnostics not computed (requires --mnl-base)."),
        data=econ_data,
    )

    # --- Solver section
    solver_name = (
        (solver_diag or {}).get("solver_name")
        if isinstance(solver_diag, dict) else None
    )
    if not solver_name:
        solver_name = metadata.get("opt_method")
    solver_data = {
        "solver_name": solver_name,
        "objective_ll": ll,
        "wall_time_seconds": _safe_num(summary.get("total_walltime_seconds")),
    }
    # Pull per-group iteration / nfev / gradient info
    per_group_solver: List[Dict[str, Any]] = []
    results_groups = results_data.get("results", {}) or {}
    for gname, gdat in results_groups.items():
        if not isinstance(gdat, dict):
            continue
        per_group_solver.append({
            "group": gname,
            "success": gdat.get("success"),
            "message": gdat.get("message"),
            "n_iterations": gdat.get("n_iterations"),
            "n_function_evaluations": gdat.get("n_function_evaluations"),
            "gradient_norm_results_json": gdat.get("gradient_norm"),
            "final_ll": gdat.get("final_ll") or gdat.get("log_likelihood"),
            "walltime_seconds": gdat.get("walltime_seconds"),
        })
    if per_group_solver:
        solver_data["per_group"] = per_group_solver

    # Augment with parsed CONOPT/log artifacts if available
    listing = (solver_diag or {}).get("listing_diagnostics", {}) if isinstance(solver_diag, dict) else {}
    solver_log = (solver_diag or {}).get("solver_log_diagnostics", {}) if isinstance(solver_diag, dict) else {}
    rgmax = None
    if isinstance(listing, dict):
        for k in ("rgmax", "RGmax", "reduced_gradient_max", "max_reduced_gradient"):
            if k in listing:
                rgmax = _safe_num(listing[k])
                break
    if rgmax is None and isinstance(solver_log, dict):
        for k in ("rgmax", "RGmax", "reduced_gradient_max"):
            if k in solver_log:
                rgmax = _safe_num(solver_log[k])
                break
    if rgmax is not None:
        solver_data["rgmax"] = rgmax
    if isinstance(listing, dict):
        for k in ("solver_status", "model_status", "solve_time_s",
                  "equations", "variables", "nonzeros", "max_infeasibility"):
            if k in listing and k not in solver_data:
                solver_data[k] = listing[k]
    if isinstance(solver_log, dict):
        for k in ("termination_message",):
            if k in solver_log and k not in solver_data:
                solver_data[k] = solver_log[k]

    solver_section_available = (
        solver_data.get("solver_name") is not None
        or bool(per_group_solver)
        or rgmax is not None
        or bool(listing and not listing.get("_note"))
        or bool(solver_log and not solver_log.get("_note"))
    )
    bundle.solver = Section(
        available=solver_section_available,
        unavailable_reason=("" if solver_section_available else
                            "No solver metadata available."),
        data=solver_data,
    )

    # --- Hessian section
    hess_data: Dict[str, Any] = {}
    if hessian_diagnostics and isinstance(hessian_diagnostics, dict):
        for k in ("condition_number", "n_negative_eigenvalues",
                  "min_eigenvalue", "max_eigenvalue"):
            if k in hessian_diagnostics:
                hess_data[k] = hessian_diagnostics[k]
    if not hess_data and isinstance(results_data.get("hessian_diagnostics"), dict):
        rhd = results_data["hessian_diagnostics"]
        for k in ("condition_number", "n_negative_eigenvalues",
                  "min_eigenvalue", "max_eigenvalue"):
            if k in rhd:
                hess_data[k] = rhd[k]
    bundle.hessian = Section(
        available=bool(hess_data),
        unavailable_reason=("" if hess_data else
                            "Hessian diagnostics not present in results JSON or cluster-SE JSON."),
        data=hess_data,
    )

    # --- Robust SE / cluster section
    robust_available = bool(cluster_se_data)
    robust_data: Dict[str, Any] = {}
    if robust_available:
        checks = (cluster_se_data or {}).get("checks", {}) or {}
        robust_data = {
            "source_artifact": "cluster-SE JSON",
            "T3_cluster_count": checks.get("T3_cluster_count"),
            "T4_se_positivity": checks.get("T4_se_positivity"),
            "T5_robust_vs_hessian": checks.get("T5_robust_vs_hessian"),
            "PE3_data_loaded": checks.get("PE3_data_loaded"),
        }
    bundle.robust_se = Section(
        available=robust_available,
        unavailable_reason=("" if robust_available else
                            "Cluster-robust SEs require --cluster-se-json. Hessian SE is the primary inference source in this report."),
        data=robust_data,
    )

    # --- Gradient/score (Python likelihood gradient)
    if gradient_diag and isinstance(gradient_diag, dict) and gradient_diag.get("available"):
        bundle.gradient_score = Section(
            available=True,
            data={
                "inf_norm": _safe_num(gradient_diag.get("inf_norm")),
                "l2_norm": _safe_num(gradient_diag.get("l2_norm")),
                "top10": gradient_diag.get("top10") or gradient_diag.get("top_components"),
                "label_note": (
                    "Python likelihood-gradient (score at converged θ) computed by central differences. "
                    "This is NOT necessarily the solver reduced gradient when bounds or constraints are active."
                ),
            },
        )
    else:
        bundle.gradient_score = Section(
            available=False,
            unavailable_reason="Pass --gradient-diagnostics with --mnl-base and --spec-config to compute the Python likelihood gradient.",
        )

    # --- Inference table (per parameter)
    inf_rows: List[Dict[str, Any]] = []
    se_full = _extract_se_array(results_data, parsed_params)
    t_full = _extract_t_array(results_data, parsed_params)
    cluster_param_map = _cluster_se_param_map(cluster_se_data, parsed_params=parsed_params)
    for i, name in enumerate(names):
        try:
            est = float(theta[i]) if theta is not None and i < len(theta) else None
        except (TypeError, ValueError):
            est = None
        lb = ub = None
        if bounds is not None and i < len(bounds):
            lb, ub = bounds[i]
        fixed = (lb is not None and ub is not None
                 and abs(float(ub) - float(lb)) <= tol_bound)
        at_lower = (est is not None and lb is not None
                    and abs(est - float(lb)) < tol_bound)
        at_upper = (est is not None and ub is not None
                    and abs(est - float(ub)) < tol_bound)
        se_h = se_full[i] if se_full is not None and i < len(se_full) else None
        t_h = t_full[i] if t_full is not None and i < len(t_full) else None
        cl = cluster_param_map.get(name, {}) if cluster_param_map else {}
        se_rob = cl.get("se_robust") if cl else None
        t_rob = cl.get("t_robust") if cl else None
        p_rob = cl.get("p_robust") if cl else None
        primary_se = "robust" if se_rob is not None else ("hessian" if se_h is not None else "none")
        inf_rows.append({
            "parameter": name,
            "estimate": est,
            "se_hessian": _safe_num(se_h),
            "t_hessian": _safe_num(t_h),
            "se_robust": _safe_num(se_rob),
            "t_robust": _safe_num(t_rob),
            "p_robust": _safe_num(p_rob),
            "fixed": fixed,
            "at_lower_bound": bool(at_lower),
            "at_upper_bound": bool(at_upper),
            "primary_se": primary_se,
        })
    bundle.inference = Section(
        available=bool(inf_rows),
        unavailable_reason="" if inf_rows else "No parameters to report.",
        data={
            "rows": inf_rows,
            "primary_se_for_run": "robust" if cluster_param_map else "hessian",
            "note": (
                "Primary SE is robust/cluster when --cluster-se-json is supplied; "
                "otherwise the Hessian (classical) SE is primary."
            ),
        },
    )

    # --- Probability fit (top-level summary only; full lists stay in CSVs)
    pf_data: Dict[str, Any] = {}
    if prob_diagnostics and isinstance(prob_diagnostics, dict):
        if "prob_sum_errors" in prob_diagnostics:
            pf_data["prob_sum_errors"] = prob_diagnostics.get("prob_sum_errors")
        if "p_chosen_dist" in prob_diagnostics:
            pf_data["p_chosen_dist"] = prob_diagnostics.get("p_chosen_dist")
        worst = (prob_diagnostics.get("worst_fit_households") or [])[:10]
        if worst:
            pf_data["worst_fit_households_top10"] = worst
    bundle.probability_fit = Section(
        available=bool(pf_data),
        unavailable_reason="" if pf_data else "Probability diagnostics require --mnl-base.",
        data=pf_data,
    )

    # --- Reproducibility
    if repro_meta and isinstance(repro_meta, dict):
        bundle.reproducibility = dict(repro_meta)

    # --- Warnings / limitations
    if n_at_lower:
        bundle.warnings.append(f"{n_at_lower} parameter(s) at lower bound.")
    if n_at_upper:
        bundle.warnings.append(f"{n_at_upper} parameter(s) at upper bound.")
    if hess_data.get("n_negative_eigenvalues") and int(hess_data["n_negative_eigenvalues"]) > 0:
        bundle.warnings.append(
            f"Hessian has {hess_data['n_negative_eigenvalues']} negative eigenvalue(s); "
            "estimates may be at a saddle point."
        )
    cond = hess_data.get("condition_number")
    if cond is not None and isinstance(cond, (int, float)) and cond > 1e10:
        bundle.warnings.append(
            f"Hessian condition number is {cond:.2e} — weak identification likely."
        )
    if not bundle.null_model_fit.available:
        bundle.limitations.append("Pseudo-R² unavailable: supply --mnl-base.")
    if not bundle.solver.data.get("rgmax"):
        bundle.limitations.append(
            "CONOPT RGmax unavailable: supply --solver-log and --listing-file from a "
            "GAMSPy run that saved solver artifacts."
        )
    if not bundle.robust_se.available:
        bundle.limitations.append(
            "Cluster-robust SEs unavailable: supply --cluster-se-json."
        )
    if not bundle.gradient_score.available:
        bundle.limitations.append(
            "Python likelihood gradient unavailable: supply --gradient-diagnostics with --mnl-base and --spec-config."
        )

    return bundle


def _extract_se_array(results_data: Dict[str, Any], parsed_params: Any) -> Optional[np.ndarray]:
    """Return SE array aligned to parsed_params.param_names, or None."""
    se = results_data.get("standard_errors")
    if isinstance(se, dict):
        names = getattr(parsed_params, "param_names", []) or []
        return np.array([_safe_num(se.get(n)) for n in names], dtype=float)
    if isinstance(se, (list, tuple)):
        return np.array([_safe_num(v) for v in se], dtype=float)
    return None


def _extract_t_array(results_data: Dict[str, Any], parsed_params: Any) -> Optional[np.ndarray]:
    """Return t-values aligned to parsed_params.param_names, or None."""
    tv = results_data.get("t_values")
    if isinstance(tv, dict):
        names = getattr(parsed_params, "param_names", []) or []
        return np.array([_safe_num(tv.get(n)) for n in names], dtype=float)
    if isinstance(tv, (list, tuple)):
        return np.array([_safe_num(v) for v in tv], dtype=float)
    return None


def _cluster_se_param_map(
    cluster_se_data: Optional[Dict[str, Any]],
    parsed_params: Any = None,
) -> Dict[str, Dict[str, Any]]:
    """Map parameter name -> {se_robust, t_robust, p_robust} from cluster-SE JSON.

    Supports three known layouts:

    1. ``parameters``/``rows`` list of dicts (one row per parameter);
    2. ``parameters``/``rows`` dict keyed by parameter name;
    3. ``cluster_robust_se_artifacts.se_robust_vector`` parallel list to
       ``parsed_params.param_names`` (the layout used by
       ``cluster_robust_se.py``).
    """
    if not cluster_se_data:
        return {}
    out: Dict[str, Dict[str, Any]] = {}

    rows = cluster_se_data.get("parameters") or cluster_se_data.get("rows")
    if isinstance(rows, list):
        for r in rows:
            if not isinstance(r, dict):
                continue
            name = r.get("param") or r.get("parameter") or r.get("name")
            if not name:
                continue
            out[str(name)] = {
                "se_robust": r.get("se_robust") or r.get("robust_se"),
                "t_robust": r.get("t_robust") or r.get("t_ratio_robust"),
                "p_robust": r.get("p_robust") or r.get("p_value_robust"),
            }
    elif isinstance(rows, dict):
        for name, r in rows.items():
            if isinstance(r, dict):
                out[str(name)] = {
                    "se_robust": r.get("se_robust") or r.get("robust_se"),
                    "t_robust": r.get("t_robust") or r.get("t_ratio_robust"),
                    "p_robust": r.get("p_robust") or r.get("p_value_robust"),
                }

    # Parallel-vector layout (cluster_robust_se.py output)
    if not out and parsed_params is not None:
        names = list(getattr(parsed_params, "param_names", []) or [])
        arts = cluster_se_data.get("cluster_robust_se_artifacts") or {}
        if isinstance(arts, dict):
            se_robust_vec = arts.get("se_robust_vector") or []
            theta_vec = arts.get("converged_theta") or []
            if names and isinstance(se_robust_vec, list) and len(se_robust_vec) == len(names):
                for i, name in enumerate(names):
                    se_r = se_robust_vec[i] if i < len(se_robust_vec) else None
                    theta_i = theta_vec[i] if i < len(theta_vec) else None
                    t_r = None
                    try:
                        if se_r and theta_i is not None and float(se_r) > 0:
                            t_r = float(theta_i) / float(se_r)
                    except (TypeError, ValueError):
                        t_r = None
                    out[str(name)] = {
                        "se_robust": se_r,
                        "t_robust": t_r,
                        "p_robust": None,
                    }
    return out


# ==============================================================================
# Profile filtering
# ==============================================================================

# Section -> set of profiles in which the section is rendered.
SECTION_PROFILES: Dict[str, Tuple[str, ...]] = {
    "estimation_metadata":  PROFILE_CHOICES,
    "data_metadata":        PROFILE_CHOICES,
    "spec_metadata":        PROFILE_CHOICES,
    "solver":               ("standard", "full", "technical"),
    "likelihood_fit_core":  PROFILE_CHOICES,
    "null_model_fit":       ("decision", "standard", "full", "technical"),
    "bounds_diagnostics":   ("standard", "full", "technical"),
    "economic_sanity":      PROFILE_CHOICES,  # always relevant for adoption decisions
    "inference":            PROFILE_CHOICES,
    "robust_se":            ("standard", "full", "technical"),
    "hessian":              ("full", "technical"),
    "gradient_score":       ("full", "technical"),
    "probability_fit":      ("full", "technical"),
    "reproducibility":      ("standard", "full", "technical"),
    "legacy_appendix":      ("technical",),
}


def section_is_visible(section_name: str, profile: str) -> bool:
    """True iff a section should be rendered for the given profile."""
    return profile in SECTION_PROFILES.get(section_name, PROFILE_CHOICES)


# ==============================================================================
# Renderers — HTML
# ==============================================================================

def _fmt_num(v: Any, precision: int = 4) -> str:
    if v is None:
        return "—"
    f = _safe_num(v)
    if f is None:
        return str(v)
    if precision == 0:
        return f"{f:.0f}"
    if abs(f) < 1e-3 or abs(f) > 1e6:
        return f"{f:.{max(2, precision)}e}"
    return f"{f:.{precision}f}"


def _row_html(label: str, value: Any, precision: int = 4) -> str:
    return f"<tr><th>{label}</th><td>{_fmt_num(value, precision)}</td></tr>"


def render_fit_stats_split_html(bundle: DiagnosticsBundle) -> str:
    """Return the four reorganized fit-statistics sections as HTML.

    Sections A/B/C/D, dynamically gated by ``section_is_visible``.
    """
    parts: List[str] = []
    profile = bundle.profile

    # A. Core
    if section_is_visible("likelihood_fit_core", profile):
        s = bundle.likelihood_fit_core
        if s.available:
            d = s.data
            rows = "".join([
                _row_html("Log-likelihood", d.get("log_likelihood"), 4),
                _row_html("Observations (rows)", d.get("n_observations"), 0),
                _row_html("Choice sets / groups", d.get("n_groups"), 0),
                _row_html("Alternatives per choice set", d.get("n_alts_per_set"), 2),
                _row_html("Free parameters", d.get("n_free_parameters"), 0),
                _row_html("Fixed parameters", d.get("n_fixed_parameters"), 0),
                _row_html("AIC", d.get("AIC"), 4),
                _row_html("BIC", d.get("BIC"), 4),
                _row_html("AIC / n_obs", d.get("AIC_per_obs"), 6),
            ])
            parts.append(f"""
<section>
  <h2>📈 A. Core Likelihood and Sample Statistics</h2>
  <table class="table" style="width:auto;">{rows}</table>
</section>""")
        else:
            parts.append(f"""
<section>
  <h2>📈 A. Core Likelihood and Sample Statistics</h2>
  <p><em>Not available: {s.unavailable_reason or 'log_likelihood not present.'}</em></p>
</section>""")

    # B. Null-model / pseudo-R²
    if section_is_visible("null_model_fit", profile):
        s = bundle.null_model_fit
        if s.available:
            d = s.data
            rows = "".join([
                _row_html("ll_null (uniform)", d.get("ll_null_uniform"), 4),
                _row_html("ll_null (prior-corrected)", d.get("ll_null_prior_corrected"), 4),
                _row_html("ρ² (uniform)", d.get("rho_squared_uniform"), 4),
                _row_html("ρ² (prior-corrected)", d.get("rho_squared_prior_corrected"), 4),
                _row_html("Adj. ρ² (uniform)", d.get("rho_squared_adj_uniform"), 4),
                _row_html("Adj. ρ² (prior-corrected)", d.get("rho_squared_adj_prior_corrected"), 4),
            ])
            note = d.get("note", "")
            parts.append(f"""
<section>
  <h2>📈 B. Null-Model and Pseudo-R² Diagnostics</h2>
  <table class="table" style="width:auto;">{rows}</table>
  <p style="margin-top:0.5em;"><em>{note}</em></p>
</section>""")
        else:
            parts.append(f"""
<section>
  <h2>📈 B. Null-Model and Pseudo-R² Diagnostics</h2>
  <p><em>Not available: {s.unavailable_reason}</em></p>
</section>""")

    # C. Bounds
    if section_is_visible("bounds_diagnostics", profile):
        s = bundle.bounds_diagnostics
        d = s.data
        rows = "".join([
            _row_html("Parameters (total)", d.get("n_parameters"), 0),
            _row_html("Free parameters", d.get("n_free_parameters"), 0),
            _row_html("Fixed parameters", d.get("n_fixed_parameters"), 0),
            _row_html("Parameters with bounds", d.get("n_parameters_with_bounds"), 0),
            _row_html("At lower bound", d.get("n_at_lower_bound"), 0),
            _row_html("At upper bound", d.get("n_at_upper_bound"), 0),
        ])
        listing = d.get("at_or_near_bounds") or []
        bound_list_html = ""
        if listing:
            rows_html = "".join(
                f"<tr><td>{r.get('parameter','')}</td><td>{r.get('side','')}</td>"
                f"<td>{_fmt_num(r.get('estimate'), 6)}</td>"
                f"<td>{_fmt_num(r.get('bound'), 6)}</td>"
                f"<td>{_fmt_num(r.get('distance'), 6)}</td></tr>"
                for r in listing
            )
            bound_list_html = (
                "<h4 style='margin-top:1em;'>Parameters at or near bounds</h4>"
                "<table class='table' style='width:auto;'>"
                "<thead><tr><th>parameter</th><th>side</th>"
                "<th>estimate</th><th>bound</th><th>distance</th></tr></thead>"
                f"<tbody>{rows_html}</tbody></table>"
            )
        parts.append(f"""
<section>
  <h2>📈 C. Bound and Fixed-Parameter Diagnostics</h2>
  <table class="table" style="width:auto;">{rows}</table>
  {bound_list_html}
</section>""")

    # D. Economic sanity
    if section_is_visible("economic_sanity", profile):
        s = bundle.economic_sanity
        if s.available:
            d = s.data
            rows = "".join(_row_html(k, v) for k, v in d.items())
            parts.append(f"""
<section>
  <h2>📈 D. Economic Sanity Diagnostics</h2>
  <p><em>These are not model-fit statistics. They check whether estimated preferences are economically sensible.</em></p>
  <table class="table" style="width:auto;">{rows}</table>
</section>""")
        else:
            parts.append(f"""
<section>
  <h2>📈 D. Economic Sanity Diagnostics</h2>
  <p><em>Not available: {s.unavailable_reason}</em></p>
</section>""")

    return "\n".join(parts)


# ==============================================================================
# Renderers — Markdown
# ==============================================================================

def _md_table(headers: List[str], rows: List[List[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        cells = [_fmt_num(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else str(v)
                 for v in r]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def render_fit_stats_split_markdown(bundle: DiagnosticsBundle) -> List[str]:
    """Return Markdown lines for the four reorganized fit-statistics sections."""
    out: List[str] = []
    profile = bundle.profile

    if section_is_visible("likelihood_fit_core", profile):
        s = bundle.likelihood_fit_core
        out.append("## A. Core Likelihood and Sample Statistics")
        out.append("")
        if s.available:
            d = s.data
            out.append(_md_table(["metric", "value"], [
                ["log_likelihood", d.get("log_likelihood")],
                ["n_observations", d.get("n_observations")],
                ["n_groups", d.get("n_groups")],
                ["n_alts_per_set", d.get("n_alts_per_set")],
                ["n_free_parameters", d.get("n_free_parameters")],
                ["n_fixed_parameters", d.get("n_fixed_parameters")],
                ["AIC", d.get("AIC")],
                ["BIC", d.get("BIC")],
                ["AIC_per_obs", d.get("AIC_per_obs")],
            ]))
        else:
            out.append(f"_Not available: {s.unavailable_reason}_")
        out.append("")

    if section_is_visible("null_model_fit", profile):
        s = bundle.null_model_fit
        out.append("## B. Null-Model and Pseudo-R² Diagnostics")
        out.append("")
        if s.available:
            d = s.data
            out.append(_md_table(["metric", "value"], [
                ["ll_null_uniform", d.get("ll_null_uniform")],
                ["ll_null_prior_corrected", d.get("ll_null_prior_corrected")],
                ["rho_squared_uniform", d.get("rho_squared_uniform")],
                ["rho_squared_prior_corrected", d.get("rho_squared_prior_corrected")],
                ["rho_squared_adj_uniform", d.get("rho_squared_adj_uniform")],
                ["rho_squared_adj_prior_corrected", d.get("rho_squared_adj_prior_corrected")],
            ]))
            note = d.get("note", "")
            if note:
                out.append("")
                out.append(f"> {note}")
        else:
            out.append(f"_Not available: {s.unavailable_reason}_")
        out.append("")

    if section_is_visible("bounds_diagnostics", profile):
        s = bundle.bounds_diagnostics
        d = s.data
        out.append("## C. Bound and Fixed-Parameter Diagnostics")
        out.append("")
        out.append(_md_table(["metric", "value"], [
            ["n_parameters", d.get("n_parameters")],
            ["n_free_parameters", d.get("n_free_parameters")],
            ["n_fixed_parameters", d.get("n_fixed_parameters")],
            ["n_parameters_with_bounds", d.get("n_parameters_with_bounds")],
            ["n_at_lower_bound", d.get("n_at_lower_bound")],
            ["n_at_upper_bound", d.get("n_at_upper_bound")],
        ]))
        listing = d.get("at_or_near_bounds") or []
        if listing:
            out.append("")
            out.append("**Parameters at or near bounds:**")
            out.append("")
            out.append(_md_table(
                ["parameter", "side", "estimate", "bound", "distance"],
                [[r.get("parameter"), r.get("side"), r.get("estimate"),
                  r.get("bound"), r.get("distance")] for r in listing]
            ))
        out.append("")

    if section_is_visible("economic_sanity", profile):
        s = bundle.economic_sanity
        out.append("## D. Economic Sanity Diagnostics")
        out.append("")
        out.append("_These are not model-fit statistics; they check economic plausibility of estimated preferences._")
        out.append("")
        if s.available:
            d = s.data
            out.append(_md_table(["metric", "value"],
                                 [[k, v] for k, v in d.items()]))
        else:
            out.append(f"_Not available: {s.unavailable_reason}_")
        out.append("")

    return out


def render_solver_section_markdown(bundle: DiagnosticsBundle) -> List[str]:
    """Render solver diagnostics in Markdown, with CONOPT vs BFGS branching."""
    out: List[str] = ["## Solver Diagnostics", ""]
    s = bundle.solver
    if not s.available:
        out.append(f"_Not available: {s.unavailable_reason}_")
        out.append("")
        return out
    d = s.data
    name = (d.get("solver_name") or "").lower()
    is_conopt = "conopt" in name or "gams" in name
    is_bfgs = "bfgs" in name or "scipy" in name or "l-bfgs" in name

    rows = [
        ["solver_name", d.get("solver_name")],
        ["objective_ll", d.get("objective_ll")],
        ["wall_time_seconds", d.get("wall_time_seconds")],
    ]
    if is_conopt:
        for k in ("solver_status", "model_status", "rgmax",
                  "equations", "variables", "nonzeros",
                  "max_infeasibility", "solve_time_s",
                  "termination_message"):
            if k in d:
                rows.append([k, d.get(k)])
    elif is_bfgs:
        for grp in (d.get("per_group") or []):
            for k in ("success", "message", "n_iterations",
                      "n_function_evaluations", "gradient_norm_results_json"):
                rows.append([f"{grp.get('group')}.{k}", grp.get(k)])
    else:
        # Generic
        for k, v in d.items():
            if k in ("solver_name", "objective_ll", "wall_time_seconds", "per_group"):
                continue
            rows.append([k, v])
        for grp in (d.get("per_group") or []):
            for k in ("success", "n_iterations", "n_function_evaluations"):
                rows.append([f"{grp.get('group')}.{k}", grp.get(k)])

    out.append(_md_table(["field", "value"], rows))
    if is_conopt and "rgmax" not in d:
        out.append("")
        out.append("_CONOPT RGmax not present. Supply --solver-log and --listing-file from a GAMSPy run "
                   "that saved solver artifacts (see --save-solver-artifacts on the estimator)._")
    out.append("")
    return out


def render_gradient_section_markdown(bundle: DiagnosticsBundle) -> List[str]:
    out: List[str] = ["## Python Likelihood Gradient (score at θ)", ""]
    s = bundle.gradient_score
    if not s.available:
        out.append(f"_Not available: {s.unavailable_reason}_")
        out.append("")
        return out
    d = s.data
    out.append(_md_table(["field", "value"], [
        ["inf_norm", d.get("inf_norm")],
        ["l2_norm", d.get("l2_norm")],
    ]))
    out.append("")
    out.append(f"> {d.get('label_note', '')}")
    out.append("")
    return out


def render_inference_section_markdown(bundle: DiagnosticsBundle, max_rows: int = 200) -> List[str]:
    out: List[str] = ["## Inference Table (per parameter)", ""]
    s = bundle.inference
    if not s.available:
        out.append(f"_Not available: {s.unavailable_reason}_")
        return out
    d = s.data
    note = d.get("note", "")
    if note:
        out.append(f"> {note}")
        out.append("")
    rows = d.get("rows") or []
    headers = ["parameter", "estimate", "se_hessian", "t_hessian",
               "se_robust", "t_robust", "p_robust",
               "fixed", "at_lower_bound", "at_upper_bound", "primary_se"]
    table_rows = []
    for r in rows[:max_rows]:
        table_rows.append([r.get(h) for h in headers])
    out.append(_md_table(headers, table_rows))
    if len(rows) > max_rows:
        out.append("")
        out.append(f"_Showing first {max_rows} of {len(rows)} parameters. See enhanced_parameter_table.csv for the full list._")
    out.append("")
    return out


def render_decision_summary_markdown(bundle: DiagnosticsBundle) -> List[str]:
    """Short, adoption-relevant summary for the decision profile."""
    out: List[str] = ["# Decision Summary", ""]
    em = bundle.estimation_metadata
    dm = bundle.data_metadata
    out.append(f"- **Specification**: {em.get('specification') or '—'}")
    out.append(f"- **Solver**: {bundle.solver.data.get('solver_name') or em.get('opt_method') or '—'}")
    out.append(f"- **Observations / Groups**: {dm.get('n_observations')} / {dm.get('n_groups')}")
    out.append("")
    if bundle.likelihood_fit_core.available:
        c = bundle.likelihood_fit_core.data
        out.append(f"- **Log-likelihood**: {_fmt_num(c.get('log_likelihood'))}")
        if c.get("AIC") is not None:
            out.append(f"- **AIC / BIC**: {_fmt_num(c.get('AIC'))} / {_fmt_num(c.get('BIC'))}")
    if bundle.null_model_fit.available:
        n = bundle.null_model_fit.data
        if n.get("rho_squared_prior_corrected") is not None:
            out.append(f"- **ρ² (prior-corrected)**: {_fmt_num(n.get('rho_squared_prior_corrected'))}")
        elif n.get("rho_squared_uniform") is not None:
            out.append(f"- **ρ² (uniform)**: {_fmt_num(n.get('rho_squared_uniform'))}")
    b = bundle.bounds_diagnostics.data
    out.append(f"- **Bounds**: {b.get('n_at_lower_bound', 0)} at lower / {b.get('n_at_upper_bound', 0)} at upper "
               f"({b.get('n_fixed_parameters', 0)} fixed; {b.get('n_free_parameters', 0)} free)")
    if bundle.economic_sanity.available:
        e = bundle.economic_sanity.data
        sane = ", ".join(f"{k}={v}" for k, v in e.items())
        if sane:
            out.append(f"- **Economic sanity**: {sane}")
    if bundle.warnings:
        out.append("")
        out.append("**Warnings:**")
        for w in bundle.warnings:
            out.append(f"- {w}")
    if bundle.limitations:
        out.append("")
        out.append("**Reporting limitations:**")
        for w in bundle.limitations:
            out.append(f"- {w}")
    out.append("")
    return out


# ==============================================================================
# Artifact writers
# ==============================================================================

def _json_default(o: Any) -> Any:
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        if math.isnan(float(o)) or math.isinf(float(o)):
            return None
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, Path):
        return str(o)
    return str(o)


def write_bundle_artifacts(
    bundle: DiagnosticsBundle,
    output_dir: Path,
    prefix: str = "",
) -> Dict[str, Path]:
    """Write the canonical artifact files. Returns map of artifact_name -> Path."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: Dict[str, Path] = {}

    bundle_dict = bundle.to_dict()
    bundle_path = output_dir / f"{prefix}diagnostics_bundle.json"
    with open(bundle_path, "w", encoding="utf-8") as fh:
        json.dump(bundle_dict, fh, indent=2, default=_json_default)
    written["diagnostics_bundle"] = bundle_path

    # Enhanced parameter table CSV (always written when inference rows exist)
    inf_rows = (bundle.inference.data.get("rows") or []) if bundle.inference.available else []
    if inf_rows:
        df = pd.DataFrame(inf_rows)
        param_path = output_dir / f"{prefix}enhanced_parameter_table.csv"
        df.to_csv(param_path, index=False)
        written["enhanced_parameter_table"] = param_path

    # solver_diagnostics.json (only when solver section is available)
    if bundle.solver.available:
        sd_path = output_dir / f"{prefix}solver_diagnostics.json"
        with open(sd_path, "w", encoding="utf-8") as fh:
            json.dump(bundle.solver.data, fh, indent=2, default=_json_default)
        written["solver_diagnostics"] = sd_path

    # inference_diagnostics.json (only when inference data is available)
    if bundle.inference.available or bundle.robust_se.available or bundle.hessian.available:
        idata = {
            "inference": bundle.inference.data,
            "robust_se": bundle.robust_se.data if bundle.robust_se.available else {"available": False, "reason": bundle.robust_se.unavailable_reason},
            "hessian": bundle.hessian.data if bundle.hessian.available else {"available": False, "reason": bundle.hessian.unavailable_reason},
        }
        id_path = output_dir / f"{prefix}inference_diagnostics.json"
        with open(id_path, "w", encoding="utf-8") as fh:
            json.dump(idata, fh, indent=2, default=_json_default)
        written["inference_diagnostics"] = id_path

    return written
