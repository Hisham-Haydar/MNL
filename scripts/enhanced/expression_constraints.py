"""
Expression-level constraints for estimation objectives.

This module provides lightweight, spec-driven expression constraints
that can be attached to SciPy and GAMSPy objectives without depending
on country/year-specific columns.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Optional, Sequence

import numpy as np

from estimation_spec_parser import EstimationSpec


SUPPORTED_EXPRESSIONS = {"muc", "mul", "dmuc_dc", "dmul_dl", "param_diff"}
SUPPORTED_GROUPS = {
    "singles_male",
    "singles_female",
    "couples_male",
    "couples_female",
    "couples_household",
    "couples",
    "global",
}

_SUFFIX_BY_GROUP = {
    "singles_male": "_sm",
    "singles_female": "_sf",
    "couples_male": "_m",
    "couples_female": "_f",
    "couples_household": "",
    "couples": "",
    "global": "",
}

LOG_EPS = 1e-12


def _normalize_group_name(group: str) -> str:
    return str(group).strip().lower()


def _normalize_active_groups(active_groups: Optional[Iterable[str]]) -> Optional[set[str]]:
    if active_groups is None:
        return None
    return {_normalize_group_name(g) for g in active_groups}


def get_active_constraints(
    spec: EstimationSpec,
    active_groups: Optional[Iterable[str]] = None,
) -> List[Dict[str, Any]]:
    """Return constraints that apply to the active estimation groups."""
    if not getattr(spec, "expression_constraints_enabled", False):
        return []
    constraints = list(getattr(spec, "expression_constraints", []) or [])
    if not constraints:
        return []

    active = _normalize_active_groups(active_groups)
    if active is None:
        return constraints

    filtered: List[Dict[str, Any]] = []
    for constraint in constraints:
        group = _normalize_group_name(constraint.get("group", ""))
        if group in active:
            filtered.append(constraint)
            continue
        if group == "global":
            filtered.append(constraint)
            continue
        if group == "couples":
            # Household-level alias: apply whenever either couples group is active.
            if "couples_male" in active or "couples_female" in active or "couples_household" in active:
                filtered.append(constraint)
    return filtered


def _candidate_param_names(base_name: str, group: str) -> List[str]:
    suffix = _SUFFIX_BY_GROUP.get(group, "")
    if suffix:
        return [f"{base_name}{suffix}", base_name]
    return [base_name]


def _resolve_param_value(
    params: Dict[str, float],
    base_name: Optional[str],
    group: str,
    required: bool = False,
) -> Optional[float]:
    if not base_name:
        return None
    for name in _candidate_param_names(base_name, group):
        if name in params:
            return float(params[name])
    if required:
        raise ValueError(
            f"Expression constraint references missing parameter '{base_name}' for group '{group}'."
        )
    return None


def _resolve_param_symbol(
    param_vars: Dict[str, Any],
    base_name: Optional[str],
    group: str,
    required: bool = False,
) -> Optional[Any]:
    if not base_name:
        return None
    for name in _candidate_param_names(base_name, group):
        if name in param_vars:
            return param_vars[name]
    if required:
        raise ValueError(
            f"Expression constraint references missing parameter '{base_name}' for group '{group}'."
        )
    return None


def _bc_scalar(x: float, theta: float) -> float:
    x_safe = max(float(x), LOG_EPS)
    if abs(theta) < 1e-8:
        return math.log(x_safe)
    return (math.exp(theta * math.log(x_safe)) - 1.0) / theta


def _dbc_dx_scalar(x: float, theta: float) -> float:
    x_safe = max(float(x), LOG_EPS)
    return math.exp((theta - 1.0) * math.log(x_safe))


def _d2bc_dx2_scalar(x: float, theta: float) -> float:
    x_safe = max(float(x), LOG_EPS)
    return (theta - 1.0) * math.exp((theta - 2.0) * math.log(x_safe))


def _at_value(at: Dict[str, float], key: str, default: float) -> float:
    return float(at.get(key, default))


def _coalesce_none(value: Optional[Any], default: Any = 0.0) -> Any:
    """Return value unless it is None (safe for symbolic objects)."""
    return default if value is None else value


def _first_non_none(*values: Optional[Any], default: Any = 0.0) -> Any:
    """Return first value that is not None (safe for symbolic objects)."""
    for value in values:
        if value is not None:
            return value
    return default


def _utility_component_scalar(
    x: float,
    theta: Optional[float],
    utility_form: str,
) -> float:
    x_safe = max(float(x), LOG_EPS)
    if utility_form == "linear":
        return x_safe
    if utility_form == "log":
        return math.log(x_safe)
    # box_cox fallback
    if theta is None:
        return math.log(x_safe)
    return _bc_scalar(x_safe, float(theta))


def _utility_derivative_scalar(
    x: float,
    theta: Optional[float],
    utility_form: str,
) -> float:
    x_safe = max(float(x), LOG_EPS)
    if utility_form == "linear":
        return 1.0
    if utility_form == "log":
        return 1.0 / x_safe
    # box_cox fallback
    if theta is None:
        return 1.0 / x_safe
    return _dbc_dx_scalar(x_safe, float(theta))


def _utility_second_derivative_scalar(
    x: float,
    theta: Optional[float],
    utility_form: str,
) -> float:
    x_safe = max(float(x), LOG_EPS)
    if utility_form == "linear":
        return 0.0
    if utility_form == "log":
        return -1.0 / (x_safe * x_safe)
    if theta is None:
        return -1.0 / (x_safe * x_safe)
    return _d2bc_dx2_scalar(x_safe, float(theta))


def _resolve_single_leisure_beta_numpy(
    params: Dict[str, float],
    spec: EstimationSpec,
    group: str,
    at: Dict[str, float],
) -> float:
    beta_l = _resolve_param_value(
        params, spec.utility_leisure_intercept, group, required=True
    )
    for shifter in spec.utility_leisure_shifters:
        var_name = shifter["variable"]
        if shifter.get("gender_specific") and var_name == "n_children" and group in {"singles_male", "couples_male"}:
            continue
        coef_val = _resolve_param_value(params, shifter["coefficient"], group, required=False)
        if coef_val is None:
            continue
        beta_l += coef_val * _at_value(at, var_name, 0.0)
    return beta_l


def _resolve_single_leisure_beta_symbol(
    param_vars: Dict[str, Any],
    spec: EstimationSpec,
    group: str,
    at: Dict[str, float],
) -> Any:
    beta_l = _resolve_param_symbol(
        param_vars, spec.utility_leisure_intercept, group, required=True
    )
    for shifter in spec.utility_leisure_shifters:
        var_name = shifter["variable"]
        if shifter.get("gender_specific") and var_name == "n_children" and group in {"singles_male", "couples_male"}:
            continue
        coef_sym = _resolve_param_symbol(param_vars, shifter["coefficient"], group, required=False)
        if coef_sym is None:
            continue
        beta_l = beta_l + coef_sym * _at_value(at, var_name, 0.0)
    return beta_l


def evaluate_constraint_value_numpy(
    theta: np.ndarray,
    spec: EstimationSpec,
    constraint: Dict[str, Any],
) -> float:
    """
    Evaluate one expression constraint in NumPy space.
    """
    params = spec.unpack_parameters(theta)
    expression = _normalize_group_name(constraint["expression"])
    group = _normalize_group_name(constraint["group"])
    at = constraint.get("at", {}) or {}

    if expression not in SUPPORTED_EXPRESSIONS:
        raise ValueError(f"Unsupported expression constraint '{expression}'.")
    if group not in SUPPORTED_GROUPS:
        raise ValueError(f"Unsupported constraint group '{group}'.")

    if expression == "param_diff":
        lhs_param = constraint.get("lhs_param")
        rhs_param = constraint.get("rhs_param")
        lhs_val = _resolve_param_value(params, lhs_param, group, required=True)
        rhs_val = _resolve_param_value(params, rhs_param, group, required=False)
        if rhs_val is None:
            rhs_val = 0.0
        return float(lhs_val - rhs_val)

    c = _at_value(at, "consumption", 1.0)
    theta_c_group = "couples_household" if group.startswith("couples") else group
    fixed_couples_theta = getattr(spec, "utility_consumption_theta_couples_fixed", None)
    if group.startswith("couples") and fixed_couples_theta is not None:
        theta_c = float(fixed_couples_theta)
    else:
        theta_c_base = (
            spec.theta_c_param_name(theta_c_group)
            if hasattr(spec, "theta_c_param_name")
            else spec.utility_consumption_theta
        )
        theta_c = _resolve_param_value(
            params,
            theta_c_base,
            theta_c_group,
            required=(spec.utility_form == "box_cox" and theta_c_base is not None),
        )
    # beta_c may be fixed (scale-normalisation numeraire) — then it is a compile-time
    # constant, not in `params`. Mirror the fixed-theta_c handling above.
    _fixed_beta_c = getattr(spec, "utility_consumption_coef_fixed", None)
    if _fixed_beta_c is not None:
        beta_c = float(_fixed_beta_c)
    else:
        beta_c = _resolve_param_value(params, spec.utility_consumption_coef, theta_c_group, required=True)
    bc_c = _utility_component_scalar(c, theta_c, spec.utility_form)
    dbc_c = _utility_derivative_scalar(c, theta_c, spec.utility_form)

    if group in {"singles_male", "singles_female"}:
        l = _at_value(at, "leisure", 1.0)
        theta_l = _resolve_param_value(
            params,
            spec.utility_leisure_theta,
            group,
            required=(spec.utility_form == "box_cox" and spec.utility_leisure_theta is not None),
        )
        bc_l = _utility_component_scalar(l, theta_l, spec.utility_form)
        dbc_l = _utility_derivative_scalar(l, theta_l, spec.utility_form)
        beta_cl = 0.0
        if spec.utility_consumption_leisure_interaction_coef:
            beta_cl = _coalesce_none(_resolve_param_value(
                params,
                spec.utility_consumption_leisure_interaction_coef,
                group,
                required=False,
            ))
        beta_l = _resolve_single_leisure_beta_numpy(params, spec, group, at)
        if expression == "muc":
            return float((beta_c + beta_cl * bc_l) * dbc_c)
        if expression == "dmuc_dc":
            d2bc_c = _utility_second_derivative_scalar(c, theta_c, spec.utility_form)
            return float((beta_c + beta_cl * bc_l) * d2bc_c)
        if expression == "mul":
            return float((beta_l + beta_cl * bc_c) * dbc_l)
        d2bc_l = _utility_second_derivative_scalar(l, theta_l, spec.utility_form)
        return float((beta_l + beta_cl * bc_c) * d2bc_l)

    # Couples
    l_m = _at_value(at, "leisure_male", _at_value(at, "leisure", 1.0))
    l_f = _at_value(
        at,
        "leisure_female",
        _at_value(at, "leisure_partner", _at_value(at, "leisure", 1.0)),
    )
    theta_l_m = _resolve_param_value(
        params,
        spec.utility_leisure_theta,
        "couples_male",
        required=(spec.utility_form == "box_cox" and spec.utility_leisure_theta is not None),
    )
    theta_l_f = _resolve_param_value(
        params,
        spec.utility_leisure_theta,
        "couples_female",
        required=(spec.utility_form == "box_cox" and spec.utility_leisure_theta is not None),
    )
    bc_l_m = _utility_component_scalar(l_m, theta_l_m, spec.utility_form)
    bc_l_f = _utility_component_scalar(l_f, theta_l_f, spec.utility_form)

    beta_cl_m = 0.0
    beta_cl_f = 0.0
    if spec.utility_consumption_leisure_interaction_coef:
        beta_cl_m = _coalesce_none(_resolve_param_value(
            params,
            spec.utility_consumption_leisure_interaction_coef,
            "couples_male",
            required=False,
        ))
        beta_cl_f = _coalesce_none(_resolve_param_value(
            params,
            spec.utility_consumption_leisure_interaction_coef,
            "couples_female",
            required=False,
        ))

    if expression == "muc":
        return float((beta_c + beta_cl_m * bc_l_m + beta_cl_f * bc_l_f) * dbc_c)
    if expression == "dmuc_dc":
        d2bc_c = _utility_second_derivative_scalar(c, theta_c, spec.utility_form)
        return float((beta_c + beta_cl_m * bc_l_m + beta_cl_f * bc_l_f) * d2bc_c)

    if group not in {"couples_male", "couples_female"}:
        raise ValueError(
            "MUL/DMUL constraints for couples must use group 'couples_male' or 'couples_female'."
        )

    own_group = group
    partner_group = "couples_female" if own_group == "couples_male" else "couples_male"
    l_own = l_m if own_group == "couples_male" else l_f
    l_partner = l_f if own_group == "couples_male" else l_m
    theta_l_own = theta_l_m if own_group == "couples_male" else theta_l_f
    theta_l_partner = theta_l_f if own_group == "couples_male" else theta_l_m
    dbc_l_own = _utility_derivative_scalar(l_own, theta_l_own, spec.utility_form)
    bc_l_partner = _utility_component_scalar(l_partner, theta_l_partner, spec.utility_form)
    beta_l_own = _resolve_single_leisure_beta_numpy(params, spec, own_group, at)
    beta_cl_own = beta_cl_m if own_group == "couples_male" else beta_cl_f
    beta_interact = 0.0
    if spec.couples_interaction_coef:
        beta_interact = _first_non_none(
            _resolve_param_value(
                params, spec.couples_interaction_coef, partner_group, required=False
            ),
            _resolve_param_value(
                params, spec.couples_interaction_coef, "couples_household", required=False
            ),
        )
    pref_term = beta_l_own + beta_cl_own * bc_c + beta_interact * bc_l_partner
    if expression == "mul":
        return float(pref_term * dbc_l_own)
    d2bc_l_own = _utility_second_derivative_scalar(l_own, theta_l_own, spec.utility_form)
    return float(pref_term * d2bc_l_own)


def compute_expression_constraints_penalty_numpy(
    theta: np.ndarray,
    spec: EstimationSpec,
    active_groups: Optional[Iterable[str]] = None,
    hard_penalty_value: float = 1e16,
) -> float:
    """
    Compute scalar penalty added to negative log-likelihood (SciPy objective).

    - soft: weighted squared hinge penalty
    - hard: returns a very large penalty when violated
    """
    constraints = get_active_constraints(spec, active_groups=active_groups)
    if not constraints:
        return 0.0

    penalty_total = 0.0
    for constraint in constraints:
        value = evaluate_constraint_value_numpy(theta, spec, constraint)
        lower = constraint.get("lower")
        upper = constraint.get("upper")
        mode = _normalize_group_name(constraint.get("mode", spec.expression_constraints_default_mode))
        weight = float(constraint.get("weight", spec.expression_constraints_default_weight))

        low_violation = max(0.0, (float(lower) - value)) if lower is not None else 0.0
        up_violation = max(0.0, (value - float(upper))) if upper is not None else 0.0

        if mode == "hard":
            if low_violation > 0.0 or up_violation > 0.0:
                return float(hard_penalty_value)
            continue

        penalty_total += weight * (low_violation * low_violation + up_violation * up_violation)

    return float(penalty_total)


def _dbc_dx_symbol(x_value: float, theta_symbol: Any, gp_exp: Any, gp_log: Any, log_eps: float) -> Any:
    # x^(theta-1) implemented via exp((theta-1) * log(x)) to avoid POWER with variable exponent.
    return gp_exp((theta_symbol - 1.0) * gp_log(float(x_value) + log_eps))


def _d2bc_dx2_symbol(x_value: float, theta_symbol: Any, gp_exp: Any, gp_log: Any, log_eps: float) -> Any:
    # (theta-1) * x^(theta-2)
    return (theta_symbol - 1.0) * gp_exp((theta_symbol - 2.0) * gp_log(float(x_value) + log_eps))


def _utility_component_symbol(
    x_value: float,
    theta_symbol: Optional[Any],
    utility_form: str,
    box_cox_transform_fn: Any,
    gp_log: Any,
    log_eps: float,
) -> Any:
    x_safe = float(x_value) + log_eps
    if utility_form == "linear":
        return float(x_value)
    if utility_form == "log":
        return gp_log(x_safe)
    if theta_symbol is None:
        return gp_log(x_safe)
    return box_cox_transform_fn(float(x_value), theta_symbol)


def _utility_derivative_symbol(
    x_value: float,
    theta_symbol: Optional[Any],
    utility_form: str,
    gp_exp: Any,
    gp_log: Any,
    log_eps: float,
) -> Any:
    x_safe = float(x_value) + log_eps
    if utility_form == "linear":
        return 1.0
    if utility_form == "log":
        return 1.0 / x_safe
    if theta_symbol is None:
        return 1.0 / x_safe
    return _dbc_dx_symbol(float(x_value), theta_symbol, gp_exp, gp_log, log_eps)


def _utility_second_derivative_symbol(
    x_value: float,
    theta_symbol: Optional[Any],
    utility_form: str,
    gp_exp: Any,
    gp_log: Any,
    log_eps: float,
) -> Any:
    x_safe = float(x_value) + log_eps
    if utility_form == "linear":
        return 0.0
    if utility_form == "log":
        return -1.0 / (x_safe * x_safe)
    if theta_symbol is None:
        return -1.0 / (x_safe * x_safe)
    return _d2bc_dx2_symbol(float(x_value), theta_symbol, gp_exp, gp_log, log_eps)


def evaluate_constraint_value_gamspy(
    spec: EstimationSpec,
    param_vars: Dict[str, Any],
    constraint: Dict[str, Any],
    box_cox_transform_fn: Any,
    gp_exp: Any,
    gp_log: Any,
    log_eps: float,
) -> Any:
    """
    Build GAMSPy expression for one constraint value.
    """
    expression = _normalize_group_name(constraint["expression"])
    group = _normalize_group_name(constraint["group"])
    at = constraint.get("at", {}) or {}

    if expression not in SUPPORTED_EXPRESSIONS:
        raise ValueError(f"Unsupported expression constraint '{expression}'.")
    if group not in SUPPORTED_GROUPS:
        raise ValueError(f"Unsupported constraint group '{group}'.")

    if expression == "param_diff":
        lhs_param = constraint.get("lhs_param")
        rhs_param = constraint.get("rhs_param")
        lhs_sym = _resolve_param_symbol(param_vars, lhs_param, group, required=True)
        rhs_sym = _resolve_param_symbol(param_vars, rhs_param, group, required=False)
        if rhs_sym is None:
            rhs_sym = 0.0
        return lhs_sym - rhs_sym

    c = _at_value(at, "consumption", 1.0)
    theta_c_group = "couples_household" if group.startswith("couples") else group
    fixed_couples_theta = getattr(spec, "utility_consumption_theta_couples_fixed", None)
    if group.startswith("couples") and fixed_couples_theta is not None:
        theta_c = float(fixed_couples_theta)
    else:
        theta_c_base = (
            spec.theta_c_param_name(theta_c_group)
            if hasattr(spec, "theta_c_param_name")
            else spec.utility_consumption_theta
        )
        theta_c = _resolve_param_symbol(
            param_vars,
            theta_c_base,
            theta_c_group,
            required=(spec.utility_form == "box_cox" and theta_c_base is not None),
        )
    # beta_c may be fixed (scale-normalisation numeraire) — then it is a compile-time
    # constant, not a GAMSPy variable. Mirror the fixed-theta_c handling above.
    _fixed_beta_c = getattr(spec, "utility_consumption_coef_fixed", None)
    if _fixed_beta_c is not None:
        beta_c = float(_fixed_beta_c)
    else:
        beta_c = _resolve_param_symbol(param_vars, spec.utility_consumption_coef, theta_c_group, required=True)
    bc_c = _utility_component_symbol(
        c, theta_c, spec.utility_form, box_cox_transform_fn, gp_log, log_eps
    )
    dbc_c = _utility_derivative_symbol(c, theta_c, spec.utility_form, gp_exp, gp_log, log_eps)

    if group in {"singles_male", "singles_female"}:
        l = _at_value(at, "leisure", 1.0)
        theta_l = _resolve_param_symbol(
            param_vars,
            spec.utility_leisure_theta,
            group,
            required=(spec.utility_form == "box_cox" and spec.utility_leisure_theta is not None),
        )
        bc_l = _utility_component_symbol(
            l, theta_l, spec.utility_form, box_cox_transform_fn, gp_log, log_eps
        )
        dbc_l = _utility_derivative_symbol(l, theta_l, spec.utility_form, gp_exp, gp_log, log_eps)
        beta_cl = 0.0
        if spec.utility_consumption_leisure_interaction_coef:
            beta_cl = _coalesce_none(_resolve_param_symbol(
                param_vars,
                spec.utility_consumption_leisure_interaction_coef,
                group,
                required=False,
            ))
        beta_l = _resolve_single_leisure_beta_symbol(param_vars, spec, group, at)
        if expression == "muc":
            return (beta_c + beta_cl * bc_l) * dbc_c
        if expression == "dmuc_dc":
            d2bc_c = _utility_second_derivative_symbol(c, theta_c, spec.utility_form, gp_exp, gp_log, log_eps)
            return (beta_c + beta_cl * bc_l) * d2bc_c
        if expression == "mul":
            return (beta_l + beta_cl * bc_c) * dbc_l
        d2bc_l = _utility_second_derivative_symbol(l, theta_l, spec.utility_form, gp_exp, gp_log, log_eps)
        return (beta_l + beta_cl * bc_c) * d2bc_l

    # Couples
    l_m = _at_value(at, "leisure_male", _at_value(at, "leisure", 1.0))
    l_f = _at_value(
        at,
        "leisure_female",
        _at_value(at, "leisure_partner", _at_value(at, "leisure", 1.0)),
    )
    theta_l_m = _resolve_param_symbol(
        param_vars,
        spec.utility_leisure_theta,
        "couples_male",
        required=(spec.utility_form == "box_cox" and spec.utility_leisure_theta is not None),
    )
    theta_l_f = _resolve_param_symbol(
        param_vars,
        spec.utility_leisure_theta,
        "couples_female",
        required=(spec.utility_form == "box_cox" and spec.utility_leisure_theta is not None),
    )
    bc_l_m = _utility_component_symbol(
        l_m, theta_l_m, spec.utility_form, box_cox_transform_fn, gp_log, log_eps
    )
    bc_l_f = _utility_component_symbol(
        l_f, theta_l_f, spec.utility_form, box_cox_transform_fn, gp_log, log_eps
    )

    beta_cl_m = 0.0
    beta_cl_f = 0.0
    if spec.utility_consumption_leisure_interaction_coef:
        beta_cl_m = _coalesce_none(_resolve_param_symbol(
            param_vars,
            spec.utility_consumption_leisure_interaction_coef,
            "couples_male",
            required=False,
        ))
        beta_cl_f = _coalesce_none(_resolve_param_symbol(
            param_vars,
            spec.utility_consumption_leisure_interaction_coef,
            "couples_female",
            required=False,
        ))

    if expression == "muc":
        return (beta_c + beta_cl_m * bc_l_m + beta_cl_f * bc_l_f) * dbc_c
    if expression == "dmuc_dc":
        d2bc_c = _utility_second_derivative_symbol(c, theta_c, spec.utility_form, gp_exp, gp_log, log_eps)
        return (beta_c + beta_cl_m * bc_l_m + beta_cl_f * bc_l_f) * d2bc_c

    if group not in {"couples_male", "couples_female"}:
        raise ValueError(
            "MUL/DMUL constraints for couples must use group 'couples_male' or 'couples_female'."
        )

    own_group = group
    partner_group = "couples_female" if own_group == "couples_male" else "couples_male"
    l_own = l_m if own_group == "couples_male" else l_f
    l_partner = l_f if own_group == "couples_male" else l_m
    theta_l_own = theta_l_m if own_group == "couples_male" else theta_l_f
    theta_l_partner = theta_l_f if own_group == "couples_male" else theta_l_m
    dbc_l_own = _utility_derivative_symbol(
        l_own, theta_l_own, spec.utility_form, gp_exp, gp_log, log_eps
    )
    bc_l_partner = _utility_component_symbol(
        l_partner, theta_l_partner, spec.utility_form, box_cox_transform_fn, gp_log, log_eps
    )
    beta_l_own = _resolve_single_leisure_beta_symbol(param_vars, spec, own_group, at)
    beta_cl_own = beta_cl_m if own_group == "couples_male" else beta_cl_f
    beta_interact = 0.0
    if spec.couples_interaction_coef:
        beta_interact = _first_non_none(
            _resolve_param_symbol(
                param_vars, spec.couples_interaction_coef, partner_group, required=False
            ),
            _resolve_param_symbol(
                param_vars, spec.couples_interaction_coef, "couples_household", required=False
            ),
        )
    pref_term = beta_l_own + beta_cl_own * bc_c + beta_interact * bc_l_partner
    if expression == "mul":
        return pref_term * dbc_l_own
    d2bc_l_own = _utility_second_derivative_symbol(
        l_own, theta_l_own, spec.utility_form, gp_exp, gp_log, log_eps
    )
    return pref_term * d2bc_l_own


def build_expression_constraints_gamspy(
    spec: EstimationSpec,
    param_vars: Dict[str, Any],
    box_cox_transform_fn: Any,
    gp_exp: Any,
    gp_log: Any,
    log_eps: float,
    active_groups: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """
    Build GAMSPy-ready soft penalties and hard-bound definitions.

    Returns dict with:
      - "soft_penalty_expr": objective penalty expression (subtract from LL)
      - "hard_bounds": list of dict(name, value_expr, lower, upper)
      - "n_active": number of active constraints
    """
    constraints = get_active_constraints(spec, active_groups=active_groups)
    if not constraints:
        return {"soft_penalty_expr": 0.0, "hard_bounds": [], "n_active": 0}

    # Smooth approximation of max(0, x): log(1 + exp(kx)) / k.
    kappa = 50.0
    soft_penalty_expr = 0.0
    hard_bounds: List[Dict[str, Any]] = []

    for idx, constraint in enumerate(constraints):
        value_expr = evaluate_constraint_value_gamspy(
            spec=spec,
            param_vars=param_vars,
            constraint=constraint,
            box_cox_transform_fn=box_cox_transform_fn,
            gp_exp=gp_exp,
            gp_log=gp_log,
            log_eps=log_eps,
        )
        mode = _normalize_group_name(constraint.get("mode", spec.expression_constraints_default_mode))
        lower = constraint.get("lower")
        upper = constraint.get("upper")
        weight = float(constraint.get("weight", spec.expression_constraints_default_weight))
        name = str(constraint.get("name", f"expr_constraint_{idx}")).strip() or f"expr_constraint_{idx}"

        if mode == "hard":
            hard_bounds.append({
                "name": name,
                "value_expr": value_expr,
                "lower": lower,
                "upper": upper,
            })
            continue

        if lower is not None:
            x_low = float(lower) - value_expr
            low_pos = gp_log(1.0 + gp_exp(kappa * x_low)) / kappa
            soft_penalty_expr = soft_penalty_expr + weight * low_pos * low_pos
        if upper is not None:
            x_up = value_expr - float(upper)
            up_pos = gp_log(1.0 + gp_exp(kappa * x_up)) / kappa
            soft_penalty_expr = soft_penalty_expr + weight * up_pos * up_pos

    return {
        "soft_penalty_expr": soft_penalty_expr,
        "hard_bounds": hard_bounds,
        "n_active": len(constraints),
    }
