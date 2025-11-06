#!/usr/bin/env python
"""
Estimate a pooled multinomial logit with Box–Cox utilities.

The script mirrors the CLI surface of ``scripts/DCM1.py`` while replacing the
translog specification by the Box–Cox form described in the project notes.
It supports gender-pooled estimation with leisure-slope shifters, reports the
usual diagnostics (LL*, AIC/BIC, rho², accuracy), and writes analyser-ready
artifacts under ``reports/biogeme/boxcox/``.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp
from scipy.stats import norm

from path_helpers import data_root, reports_root

LOGGER = logging.getLogger(__name__)

T_HOURS: float = 80.0
EPS: float = 1e-6


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def boxcox_transform(x: np.ndarray, alpha: float) -> np.ndarray:
    """Box–Cox transform with a smooth limit at alpha→0."""
    x = np.clip(x, EPS, None)
    if abs(alpha) < 1e-6:
        return np.log(x)
    return (np.power(x, alpha) - 1.0) / alpha


def d_boxcox_dalpha(x: np.ndarray, alpha: float) -> np.ndarray:
    """Derivative of the Box–Cox transform w.r.t. the power parameter alpha."""
    x = np.clip(x, EPS, None)
    ln_x = np.log(x)
    if abs(alpha) < 1e-6:
        return 0.5 * ln_x * ln_x
    x_alpha = np.power(x, alpha)
    numerator = alpha * x_alpha * ln_x - (x_alpha - 1.0)
    denominator = alpha * alpha
    return numerator / denominator


def softmax(utilities: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Row-wise softmax that respects availability mask."""
    avail = mask.astype(bool)
    masked_utils = np.where(avail, utilities, -np.inf)
    max_u = np.max(masked_utils, axis=1, keepdims=True)
    max_u = np.where(np.isfinite(max_u), max_u, 0.0)
    exps = np.exp(masked_utils - max_u)
    exps = exps * avail
    sums = exps.sum(axis=1, keepdims=True)
    sums = np.where(sums <= 0.0, 1.0, sums)
    return exps / sums


def boxcox_derivative(x: np.ndarray, alpha: float) -> np.ndarray:
    """Derivative of the Box–Cox transform w.r.t its argument."""
    x = np.clip(x, EPS, None)
    if abs(alpha) < 1e-6:
        return 1.0 / x
    return np.power(x, alpha - 1.0)


def ensure_columns(df: pd.DataFrame, cols: Iterable[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"Dataset is missing required column(s): {missing}")


def detect_labels(df: pd.DataFrame, labels: Sequence[str] | None = None) -> Tuple[str, ...]:
    if labels:
        provided = tuple(labels)
        missing = [
            lab
            for lab in provided
            if f"consumption_{lab}" not in df.columns or f"lhw_{lab}" not in df.columns
        ]
        if missing:
            raise KeyError(f"Requested labels missing from dataset: {missing}")
        return provided

    labs = [
        col.split("consumption_", 1)[1]
        for col in df.columns
        if col.startswith("consumption_")
    ]
    labs = sorted(set(labs), key=lambda s: (len(s), s))
    if not labs:
        raise ValueError("Could not detect scenario labels (expected consumption_*)")
    for lab in labs:
        ensure_columns(df, [f"lhw_{lab}"])
    return tuple(labs)


def clip_unit_interval(arr: np.ndarray) -> np.ndarray:
    return np.clip(arr, EPS, 1.0)


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------

@dataclass
class ModelData:
    labels: Tuple[str, ...]
    C_norm: np.ndarray            # shape (N, J)
    L_norm: np.ndarray            # shape (N, J)
    consumption_raw: np.ndarray   # shape (N, J)
    lhw_raw: np.ndarray           # shape (N, J)
    availability: np.ndarray      # bool matrix (N, J)
    actual_idx: np.ndarray        # (N,)
    actual_choice: pd.Series
    y_ref: float
    Z_matrix: np.ndarray          # shape (N, K) – may be empty
    Z_names: List[str]
    features: Dict[str, np.ndarray]
    has_gender_param: bool


def compute_reference_consumption(consumption: np.ndarray, actual_idx: np.ndarray, quantile: float) -> float:
    cons_actual = consumption[np.arange(len(consumption)), actual_idx]
    cons_actual = cons_actual[np.isfinite(cons_actual) & (cons_actual > 0)]
    if cons_actual.size == 0:
        raise ValueError("No valid consumption values found to compute y_ref.")
    for q in (quantile, 0.95, 0.90):
        y_ref = float(np.quantile(cons_actual, q))
        if np.isfinite(y_ref) and y_ref > 0:
            return y_ref
    y_ref = float(np.max(cons_actual))
    if not np.isfinite(y_ref) or y_ref <= 0:
        raise ValueError("Failed to determine a positive reference consumption (y_ref).")
    return y_ref


def prepare_dataset(
    df: pd.DataFrame,
    labels: Tuple[str, ...],
    *,
    gender_column: str = "dgn",
    c_scale_quantile: float = 0.99,
) -> ModelData:
    ensure_columns(df, ["actual_choice", "dag", "num_children_total", "DCH"])

    df_num = df.copy()
    numeric_cols = [
        c
        for c in df.columns
        if c.startswith(("consumption_", "lhw_", "avail_"))
        or c in {"dag", "num_children_total", "DCH", gender_column}
    ]
    df_num[numeric_cols] = df_num[numeric_cols].apply(pd.to_numeric, errors="coerce")

    for lab in labels:
        ensure_columns(df_num, [f"consumption_{lab}", f"lhw_{lab}"])

    actual_choice = df_num["actual_choice"].astype(str)
    label_to_index = {lab: idx for idx, lab in enumerate(labels)}
    if not actual_choice.isin(label_to_index).all():
        invalid = actual_choice[~actual_choice.isin(label_to_index)].unique()
        raise ValueError(f"Encountered actual_choice outside provided labels: {invalid}")
    actual_idx = actual_choice.map(label_to_index).to_numpy(dtype=int)

    consumption = np.stack([df_num[f"consumption_{lab}"].to_numpy(dtype=float) for lab in labels], axis=1)
    lhw = np.stack([df_num[f"lhw_{lab}"].to_numpy(dtype=float) for lab in labels], axis=1)

    availability = []
    for lab in labels:
        col = f"avail_{lab}"
        if col in df_num.columns:
            availability.append((df_num[col].to_numpy(dtype=float) > 0).astype(bool))
        else:
            availability.append(np.ones(len(df_num), dtype=bool))
    availability = np.stack(availability, axis=1)

    if np.any(~availability[np.arange(len(df_num)), actual_idx]):
        raise ValueError("Actual choice marked unavailable for some heads.")

    y_ref = compute_reference_consumption(consumption, actual_idx, c_scale_quantile)

    C_norm = clip_unit_interval(consumption / y_ref)
    L_norm = clip_unit_interval((T_HOURS - lhw) / T_HOURS)

    age = pd.to_numeric(df_num["dag"], errors="coerce").fillna(16.0)
    age_norm = np.clip((age - 16.0) / (65.0 - 16.0), 0.0, 1.0).to_numpy(dtype=float)
    age2_norm = np.square(age_norm)
    child_norm = np.clip(
        pd.to_numeric(df_num["num_children_total"], errors="coerce").fillna(0.0) / 5.0,
        0.0,
        1.0,
    ).to_numpy(dtype=float)
    dch = pd.to_numeric(df_num["DCH"], errors="coerce").fillna(0.0).clip(0.0, 1.0).to_numpy(dtype=float)

    has_gender_param = False
    gender_vector = None
    if gender_column in df_num.columns:
        gender_vector = pd.to_numeric(df_num[gender_column], errors="coerce").fillna(0.0).clip(0.0, 1.0).to_numpy(dtype=float)
        if np.unique(gender_vector).size > 1:
            has_gender_param = True

    Z_names: List[str] = ["delta_age", "delta_age2", "delta_child", "delta_dch"]
    Z_columns: List[np.ndarray] = [age_norm, age2_norm, child_norm, dch]
    if has_gender_param and gender_vector is not None:
        Z_names.append("delta_gender")
        Z_columns.append(gender_vector)
    Z_matrix = np.stack(Z_columns, axis=1) if Z_columns else np.zeros((len(df_num), 0))

    features = {
        "age_norm": age_norm,
        "age2_norm": age2_norm,
        "child_norm": child_norm,
        "dch": dch,
    }
    if gender_vector is not None:
        features["gender"] = gender_vector

    return ModelData(
        labels=labels,
        C_norm=C_norm,
        L_norm=L_norm,
        consumption_raw=consumption,
        lhw_raw=lhw,
        availability=availability,
        actual_idx=actual_idx,
        actual_choice=actual_choice,
        y_ref=y_ref,
        Z_matrix=Z_matrix,
        Z_names=Z_names,
        features=features,
        has_gender_param=has_gender_param,
    )


# ---------------------------------------------------------------------------
# Parameter handling
# ---------------------------------------------------------------------------

@dataclass
class ParamStructure:
    param_names: List[str]
    delta_names: List[str]
    asc_labels: List[str]


def build_param_structure(labels: Tuple[str, ...], data: ModelData, include_ascs: bool) -> ParamStructure:
    names = ["alpha_c", "alpha_l", "beta_c", "beta_l0"]
    delta_names = data.Z_names
    names.extend(delta_names)

    asc_labels: List[str] = []
    if include_ascs and len(labels) > 1:
        asc_labels = list(labels[1:])
        names.extend(f"ASC_{lab}" for lab in asc_labels)

    return ParamStructure(param_names=names, delta_names=delta_names, asc_labels=asc_labels)


def unpack_params(theta: np.ndarray, structure: ParamStructure) -> Dict[str, float]:
    values: Dict[str, float] = {}
    idx = 0
    values["alpha_c"] = float(theta[idx]); idx += 1
    values["alpha_l"] = float(theta[idx]); idx += 1
    values["beta_c"] = float(theta[idx]); idx += 1
    values["beta_l0"] = float(theta[idx]); idx += 1

    for delta_name in structure.delta_names:
        values[delta_name] = float(theta[idx]); idx += 1

    for lab in structure.asc_labels:
        values[f"ASC_{lab}"] = float(theta[idx]); idx += 1

    return values


def initial_theta(structure: ParamStructure) -> np.ndarray:
    init = []
    init.extend([0.1, 0.1])  # alpha_c, alpha_l
    init.extend([1.0, 1.0])  # beta_c, beta_l0
    init.extend([0.0] * len(structure.delta_names))
    init.extend([0.0] * len(structure.asc_labels))
    return np.array(init, dtype=float)


# ---------------------------------------------------------------------------
# Likelihood and prediction
# ---------------------------------------------------------------------------

def compute_terms(params: Dict[str, float], data: ModelData, structure: ParamStructure) -> Dict[str, np.ndarray]:
    alpha_c = params["alpha_c"]
    alpha_l = params["alpha_l"]
    beta_c = params["beta_c"]
    beta_l0 = params["beta_l0"]

    bc_c = boxcox_transform(data.C_norm, alpha_c)
    bc_l = boxcox_transform(data.L_norm, alpha_l)
    bc_c_dalpha = d_boxcox_dalpha(data.C_norm, alpha_c)
    bc_l_dalpha = d_boxcox_dalpha(data.L_norm, alpha_l)

    if structure.delta_names:
        delta_vector = np.array([params[name] for name in structure.delta_names], dtype=float)
        beta_l = beta_l0 + data.Z_matrix @ delta_vector
    else:
        beta_l = np.full(data.C_norm.shape[0], beta_l0)

    return {
        "bc_c": bc_c,
        "bc_l": bc_l,
        "bc_c_dalpha": bc_c_dalpha,
        "bc_l_dalpha": bc_l_dalpha,
        "beta_l": beta_l,
        "beta_c": beta_c,
    }


def assemble_utilities(theta: np.ndarray, data: ModelData, structure: ParamStructure) -> np.ndarray:
    params = unpack_params(theta, structure)
    terms = compute_terms(params, data, structure)

    utilities = params["beta_c"] * terms["bc_c"] + terms["beta_l"][:, None] * terms["bc_l"]

    if structure.asc_labels:
        asc = np.zeros(len(data.labels))
        for lab in structure.asc_labels:
            asc[data.labels.index(lab)] = params[f"ASC_{lab}"]
        utilities = utilities + asc

    utilities = np.where(data.availability, utilities, -np.inf)
    return utilities


def negative_log_likelihood(theta: np.ndarray, data: ModelData, structure: ParamStructure) -> float:
    utilities = assemble_utilities(theta, data, structure)
    if np.any(np.isinf(utilities).all(axis=1)):
        return 1e12
    log_denom = logsumexp(utilities, axis=1)
    chosen_util = utilities[np.arange(len(data.actual_idx)), data.actual_idx]
    if np.any(~np.isfinite(chosen_util)):
        return 1e12
    log_prob = chosen_util - log_denom
    if np.any(~np.isfinite(log_prob)):
        return 1e12
    return -float(np.sum(log_prob))


def assemble_partials(theta: np.ndarray, data: ModelData, structure: ParamStructure) -> Dict[str, np.ndarray]:
    params = unpack_params(theta, structure)
    terms = compute_terms(params, data, structure)
    availability = data.availability.astype(float)

    partials: Dict[str, np.ndarray] = {}
    partials["alpha_c"] = params["beta_c"] * terms["bc_c_dalpha"]
    partials["alpha_l"] = terms["beta_l"][:, None] * terms["bc_l_dalpha"]
    partials["beta_c"] = terms["bc_c"]
    partials["beta_l0"] = terms["bc_l"]

    for idx, delta_name in enumerate(structure.delta_names):
        Zk = data.Z_matrix[:, idx]
        partials[delta_name] = (Zk[:, None]) * terms["bc_l"]

    for lab in structure.asc_labels:
        mat = np.zeros_like(terms["bc_c"])
        j = data.labels.index(lab)
        mat[:, j] = availability[:, j]
        partials[f"ASC_{lab}"] = mat

    for key, value in partials.items():
        partials[key] = value * availability

    return partials


def predict_choices(theta: np.ndarray, data: ModelData, structure: ParamStructure) -> np.ndarray:
    utilities = assemble_utilities(theta, data, structure)
    return np.argmax(utilities, axis=1)


def compute_null_loglik(data: ModelData) -> float:
    avail_counts = np.sum(data.availability, axis=1).astype(float)
    if np.any(avail_counts <= 0):
        raise ValueError("Found head with no available alternatives.")
    return -float(np.sum(np.log(avail_counts)))


def score_matrix(theta: np.ndarray, data: ModelData, structure: ParamStructure) -> np.ndarray:
    utilities = assemble_utilities(theta, data, structure)
    probs = softmax(utilities, data.availability)
    partials = assemble_partials(theta, data, structure)

    indicator = np.zeros_like(probs)
    indicator[np.arange(len(data.actual_idx)), data.actual_idx] = 1.0
    indicator = indicator * data.availability

    w = indicator - probs

    scores = np.zeros((len(data.actual_idx), len(structure.param_names)))
    for idx, name in enumerate(structure.param_names):
        scores[:, idx] = np.sum(w * partials[name], axis=1)
    return scores


def approximate_hessian(theta: np.ndarray, data: ModelData, structure: ParamStructure, eps: float = 1e-4) -> np.ndarray:
    k = len(theta)
    H = np.zeros((k, k), dtype=float)
    f0 = negative_log_likelihood(theta, data, structure)
    eye = np.eye(k)
    for i in range(k):
        ei = eye[i] * eps
        f_plus = negative_log_likelihood(theta + ei, data, structure)
        f_minus = negative_log_likelihood(theta - ei, data, structure)
        H[i, i] = (f_plus - 2.0 * f0 + f_minus) / (eps ** 2)
        for j in range(i + 1, k):
            ej = eye[j] * eps
            f_pp = negative_log_likelihood(theta + ei + ej, data, structure)
            f_pm = negative_log_likelihood(theta + ei - ej, data, structure)
            f_mp = negative_log_likelihood(theta - ei + ej, data, structure)
            f_mm = negative_log_likelihood(theta - ei - ej, data, structure)
            value = (f_pp - f_pm - f_mp + f_mm) / (4.0 * eps ** 2)
            H[i, j] = H[j, i] = value
    return H

def _make_spd(M: np.ndarray, lam: float = 1e-8) -> np.ndarray:
    """Return a symmetric positive-definite version of M by eigenvalue floor."""
    S = 0.5 * (M + M.T)
    vals, vecs = np.linalg.eigh(S)
    vals = np.clip(vals, lam, None)
    return (vecs * vals) @ vecs.T

# ---------------------------------------------------------------------------
# Diagnostics & outputs
# ---------------------------------------------------------------------------

def flatten_params(theta: np.ndarray, structure: ParamStructure) -> Dict[str, float]:
    params = unpack_params(theta, structure)
    ordered = {}
    for name in structure.param_names:
        ordered[name] = params.get(name, 0.0)
    return ordered


def build_parameter_dataframe(
    param_values: Dict[str, float],
    structure: ParamStructure,
    *,
    se: np.ndarray,
    t_values: np.ndarray,
    p_values: np.ndarray,
    se_rob: np.ndarray,
    t_values_rob: np.ndarray,
    p_values_rob: np.ndarray,
) -> pd.DataFrame:
    records = []
    for idx, name in enumerate(structure.param_names):
        records.append(
            {
                "Name": name,
                "Value": param_values[name],
                "StdErr": se[idx],
                "t": t_values[idx],
                "p": p_values[idx],
                "RobustSE": se_rob[idx],
                "Robust t": t_values_rob[idx],
                "Robust p": p_values_rob[idx],
            }
        )
    return pd.DataFrame.from_records(records).set_index("Name")


PARAM_LABELS = {
    "alpha_c": "Box-Cox power (consumption)",
    "alpha_l": "Box-Cox power (leisure)",
    "beta_c": "Consumption coefficient",
    "beta_l0": "Baseline leisure coefficient",
    "delta_age": "Leisure shift · age",
    "delta_age2": "Leisure shift · age²",
    "delta_child": "Leisure shift · children",
    "delta_dch": "Leisure shift · childcare dummy",
    "delta_gender": "Leisure shift · gender",
}

PARAM_DESCRIPTIONS = {
    "alpha_c": "Box–Cox power applied to normalised consumption.",
    "alpha_l": "Box–Cox power applied to normalised leisure.",
    "beta_c": "Marginal utility level for consumption.",
    "beta_l0": "Baseline leisure slope before shifters.",
    "delta_age": "Adjustment to leisure slope with age (normalised 16–65).",
    "delta_age2": "Quadratic age adjustment to the leisure slope.",
    "delta_child": "Leisure slope shift with number of children (0–5 scaled).",
    "delta_dch": "Leisure slope shift for households with high childcare demand.",
    "delta_gender": "Leisure slope shift for gender indicator.",
}


def write_parameter_metadata(
    output_dir: Path,
    model_name: str,
    param_df: pd.DataFrame,
    meta: Dict[str, object],
) -> None:
    param_csv = output_dir / f"{model_name}_parameters.csv"
    param_df.to_csv(param_csv)

    meta_path = output_dir / f"{model_name}_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    labels_path = output_dir / f"{model_name}_param_labels.json"
    descriptions_path = output_dir / f"{model_name}_param_descriptions.json"

    labels: Dict[str, str] = {}
    descriptions: Dict[str, str] = {}
    for name in param_df.index:
        if name.startswith("ASC_"):
            labels[name] = f"ASC {name.split('ASC_', 1)[1]}"
            descriptions[name] = "Alternative-specific constant."
        else:
            labels[name] = PARAM_LABELS.get(name, name)
            descriptions[name] = PARAM_DESCRIPTIONS.get(name, "")

    labels_path.write_text(json.dumps(labels, indent=2), encoding="utf-8")
    descriptions_path.write_text(json.dumps(descriptions, indent=2), encoding="utf-8")


def confusion_matrix(actual: Sequence[str], predicted: Sequence[str], labels: Tuple[str, ...]) -> pd.DataFrame:
    frame = pd.DataFrame({"actual": actual, "predicted": [labels[idx] for idx in predicted]})
    return pd.crosstab(frame["actual"], frame["predicted"], dropna=False).reindex(index=labels, columns=labels, fill_value=0)


# ---------------------------------------------------------------------------
# Marginal utility helper for analyser
# ---------------------------------------------------------------------------

def muc_mul_point(
    params: Dict[str, float],
    consumption: float,
    leisure: float,
    y_ref: float,
    Z: Dict[str, float],
    T: float = T_HOURS,
) -> Tuple[float, float]:
    c_norm = clip_unit_interval(np.array([consumption / y_ref], dtype=float))[0]
    l_norm = clip_unit_interval(np.array([(T - leisure) / T], dtype=float))[0]

    alpha_c = params["alpha_c"]
    alpha_l = params["alpha_l"]
    beta_c = params["beta_c"]
    beta_l = params["beta_l0"]
    for key, value in Z.items():
        name = f"delta_{key}"
        if name in params:
            beta_l += params[name] * value

    muc = beta_c * boxcox_derivative(np.array([c_norm]), alpha_c)[0] / y_ref
    mul = beta_l * boxcox_derivative(np.array([l_norm]), alpha_l)[0] / T
    return float(muc), float(mul)


def muc_mul(
    params: Dict[str, float],
    consumption: float,
    leisure: float,
    y_ref: float,
    Z: Dict[str, float],
) -> Tuple[float, float]:
    return muc_mul_point(params, consumption, leisure, y_ref, Z, T=T_HOURS)


def generate_mucmul_draws(
    param_values: Dict[str, float],
    data: ModelData,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    n = len(data.actual_idx)
    idx = np.arange(n)
    head_index = (
        data.actual_choice.index
        if isinstance(data.actual_choice, pd.Series)
        else pd.RangeIndex(n)
    )

    C_actual = data.consumption_raw[idx, data.actual_idx]
    L_actual = T_HOURS - data.lhw_raw[idx, data.actual_idx]
    C_norm_actual = data.C_norm[idx, data.actual_idx]
    L_norm_actual = data.L_norm[idx, data.actual_idx]

    c_med = float(np.nanmedian(C_actual))
    l_med = float(np.nanmedian(L_actual))

    feature_key_map = {
        "age_norm": "age",
        "age2_norm": "age2",
        "child_norm": "child",
        "dch": "dch",
        "gender": "gender",
    }

    Z_medians: Dict[str, float] = {}
    for feat_key, arr in data.features.items():
        if feat_key in feature_key_map:
            Z_medians[feature_key_map[feat_key]] = float(np.nanmedian(arr))

    muc_med, mul_med = muc_mul_point(param_values, c_med, l_med, data.y_ref, Z_medians, T=T_HOURS)
    mrs_med = mul_med / muc_med if muc_med != 0 else np.nan

    records: List[Dict[str, object]] = []
    for i in range(n):
        Z_actual: Dict[str, float] = {}
        for feat_key, arr in data.features.items():
            if feat_key in feature_key_map:
                Z_actual[feature_key_map[feat_key]] = float(arr[i])

        muc_actual, mul_actual = muc_mul_point(
            param_values,
            C_actual[i],
            L_actual[i],
            data.y_ref,
            Z_actual,
            T=T_HOURS,
        )
        mrs_actual = mul_actual / muc_actual if muc_actual != 0 else np.nan

        records.append(
            {
                "head_index": head_index[i],
                "actual_choice": data.actual_choice.iloc[i] if isinstance(data.actual_choice, pd.Series) else data.actual_choice[i],
                "C_actual": C_actual[i],
                "L_actual": L_actual[i],
                "C_norm_actual": C_norm_actual[i],
                "L_norm_actual": L_norm_actual[i],
                "MUC_actual": muc_actual,
                "MUL_actual": mul_actual,
                "MRS_actual": mrs_actual,
                "MUC_actual_pos": muc_actual > 0,
                "MUL_actual_pos": mul_actual > 0,
                "MUC_med": muc_med,
                "MUL_med": mul_med,
                "MRS_med": mrs_med,
                "MUC_med_pos": muc_med > 0,
                "MUL_med_pos": mul_med > 0,
            }
        )

    draws_df = pd.DataFrame.from_records(records).set_index("head_index")

    summary = {
        "share_MUC_actual_neg": float(draws_df["MUC_actual"].lt(0).mean()),
        "share_MUL_actual_neg": float(draws_df["MUL_actual"].lt(0).mean()),
        "share_MUC_med_neg": float(draws_df["MUC_med"].lt(0).mean()),
        "share_MUL_med_neg": float(draws_df["MUL_med"].lt(0).mean()),
        "median_consumption_actual": c_med,
        "median_leisure_actual": l_med,
        "MUC_med": muc_med,
        "MUL_med": mul_med,
        "y_ref": data.y_ref,
        "T": T_HOURS,
    }

    return draws_df, summary


# ---------------------------------------------------------------------------
# Estimation workflow
# ---------------------------------------------------------------------------

def estimate(
    gender_key: str,
    df: pd.DataFrame,
    labels: Tuple[str, ...],
    *,
    include_ascs: bool,
    gender_column: str,
    output_dir: Path,
    log_level: int,
    c_scale_quantile: float,
    variant: str,
) -> None:
    data = prepare_dataset(df, labels, gender_column=gender_column, c_scale_quantile=c_scale_quantile)
    structure = build_param_structure(labels, data, include_ascs=include_ascs)

    LOGGER.info("[%s] Parameter vector: %s", gender_key, structure.param_names)

    theta0 = initial_theta(structure)
    bounds = [(-2.0, 2.0), (-2.0, 2.0)] + [(None, None)] * (len(theta0) - 2)

    result = minimize(
        negative_log_likelihood,
        theta0,
        args=(data, structure),
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": 1000, "disp": log_level <= logging.DEBUG},
    )

    if not result.success:
        LOGGER.warning("[%s] Optimiser did not converge: %s", gender_key, result.message)

    theta_hat = result.x
    ll_star = -negative_log_likelihood(theta_hat, data, structure)
    ll_null = compute_null_loglik(data)

    param_values = flatten_params(theta_hat, structure)
    predicted = predict_choices(theta_hat, data, structure)
    accuracy = float(np.mean(predicted == data.actual_idx))

    k_params = len(structure.param_names)
    n_obs = len(data.actual_idx)
    rho2 = float(1.0 - ll_star / ll_null) if ll_null != 0 else float("nan")
    rho2_adj = float(1.0 - (ll_star - k_params) / ll_null) if ll_null != 0 else float("nan")
    aic = 2 * k_params - 2 * ll_star
    bic = math.log(n_obs) * k_params - 2 * ll_star

    cm = confusion_matrix(data.actual_choice, predicted, labels)

    scores = score_matrix(theta_hat, data, structure)

    hess_inv_obj = getattr(result, "hess_inv", None)
    Hinv = None
    if hess_inv_obj is not None:
        if hasattr(hess_inv_obj, "todense"):
            Hinv = np.asarray(hess_inv_obj.todense(), dtype=float)
        else:
            try:
                Hinv = np.asarray(hess_inv_obj, dtype=float)
            except Exception:
                Hinv = None

    if Hinv is None or Hinv.shape != (k_params, k_params):
        H = approximate_hessian(theta_hat, data, structure)
        H = 0.5 * (H + H.T)
        # --- NEW: ridge to avoid near-singularity
        lam = 1e-6 * max(1.0, np.max(np.abs(np.diag(H))))
        H = H + lam * np.eye(k_params)
        Hinv = np.linalg.pinv(H)

    Hinv = 0.5 * (Hinv + Hinv.T)
    cov = _make_spd(Hinv, lam=1e-8)

    G = scores.T @ scores
    cov_rob = Hinv @ G @ Hinv
    cov_rob = _make_spd(cov_rob, lam=1e-8)

    values_vector = np.array([param_values[name] for name in structure.param_names], dtype=float)

    diag_cov = np.diag(cov)
    diag_cov_rob = np.diag(cov_rob)
    se = np.sqrt(np.where(diag_cov >= 0, diag_cov, np.nan))
    se_rob = np.sqrt(np.where(diag_cov_rob >= 0, diag_cov_rob, np.nan))

    with np.errstate(divide="ignore", invalid="ignore"):
        t_values = np.divide(values_vector, se, out=np.full_like(values_vector, np.nan), where=se > 0)
        t_values_rob = np.divide(values_vector, se_rob, out=np.full_like(values_vector, np.nan), where=se_rob > 0)

    p_values = np.where(np.isnan(t_values), np.nan, 2.0 * norm.sf(np.abs(t_values)))
    p_values_rob = np.where(np.isnan(t_values_rob), np.nan, 2.0 * norm.sf(np.abs(t_values_rob)))

    param_df = build_parameter_dataframe(
        param_values,
        structure,
        se=se,
        t_values=t_values,
        p_values=p_values,
        se_rob=se_rob,
        t_values_rob=t_values_rob,
        p_values_rob=p_values_rob,
    )

    draws_df, muc_summary = generate_mucmul_draws(param_values, data)

    min_eig = float(np.min(np.linalg.eigvalsh(0.5 * (cov + cov.T))))

    LOGGER.info("[%s] Log-likelihood at optimum: %.4f", gender_key, ll_star)
    LOGGER.info("[%s] LL(null)=%.4f  rho²=%.4f  rho²_adj=%.4f", gender_key, ll_null, rho2, rho2_adj)
    LOGGER.info("[%s] AIC=%.2f  BIC=%.2f", gender_key, aic, bic)
    LOGGER.info("[%s] Accuracy=%.2f%%", gender_key, accuracy * 100.0)
    LOGGER.info("[%s] Confusion matrix:\n%s", gender_key, cm)
    LOGGER.info("[%s] Parameter count K=%d  min_eig(cov)=%.3e", gender_key, k_params, min_eig)
    LOGGER.info(
        "[%s] Share MUC<0 actual=%.2f%%  MUL<0 actual=%.2f%%",
        gender_key,
        muc_summary["share_MUC_actual_neg"] * 100.0,
        muc_summary["share_MUL_actual_neg"] * 100.0,
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    model_name = f"boxcox_{gender_key}_{variant}".replace(".", "_")
    meta = {
        "spec": "boxcox",
        "labels": list(labels),
        "include_ascs": include_ascs,
        "pooled": gender_key == "pooled",
        "variant": variant,
        "c_scale_quantile": c_scale_quantile,
        "log_likelihood": ll_star,
        "null_log_likelihood": ll_null,
        "rho2": rho2,
        "rho2_adj": rho2_adj,
        "aic": aic,
        "bic": bic,
        "accuracy": accuracy,
        "k_params": k_params,
        "min_eig_cov": min_eig,
        "y_ref": data.y_ref,
        "T": T_HOURS,
        "parameters": param_values,
    }
    meta.update({k: float(v) for k, v in muc_summary.items()})
    meta.update({
    "parameters_csv": f"{model_name}_parameters.csv",
    "confusion_csv": f"{model_name}_confusion.csv",
})

    write_parameter_metadata(output_dir, model_name, param_df, meta)

    cm_path = output_dir / f"{model_name}_confusion.csv"
    cm.to_csv(cm_path)

    draws_path = output_dir / f"{model_name}_mucmul_draws.csv"
    draws_df.to_csv(draws_path)

    muc_summary_path = output_dir / f"{model_name}_mucmul_summary.json"
    muc_summary_path.write_text(json.dumps(muc_summary, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estimate a Box–Cox MNL model.")
    parser.add_argument("--genders", nargs="+", choices=("male", "female"), default=["male", "female"])
    parser.add_argument("--labels", nargs="+", help="Scenario labels to include (default: all detected).")
    parser.add_argument("--auto-labels", action="store_true", help="Detect labels from dataset columns.")
    parser.add_argument("--include-ascs", action="store_true", help="Include ASC parameters (base fixed).")
    parser.add_argument("--pooled", action="store_true", help="Estimate pooled model with gender shifter.")
    parser.add_argument("--gender-column", default="dgn", help="Gender column name (1=female, 0=male).")
    parser.add_argument("--center-logs", action="store_true", help=argparse.SUPPRESS)  # compatibility placeholder
    parser.add_argument("--y-scale", type=float, default=1.0, help=argparse.SUPPRESS)  # compatibility placeholder
    parser.add_argument("--c-scale-quantile", type=float, default=0.99, help="Quantile for consumption normalisation (default 0.99).")
    parser.add_argument("--output-dir", type=Path, default=reports_root() / "biogeme" / "boxcox", help="Output directory base.")
    parser.add_argument("--data-dir", type=Path, default=data_root() / "processed" / "scenarios", help="Input directory for wide datasets.")
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR"), help="Logging verbosity.")
    return parser.parse_args()


def load_wide_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset: {path}")
    return pd.read_parquet(path)


def maybe_add_gender(df: pd.DataFrame, gender_value: float, column: str) -> pd.DataFrame:
    df = df.copy()
    if column not in df.columns:
        df[column] = gender_value
    return df


def run_for_gender(
    gender_key: str,
    df: pd.DataFrame,
    labels: Tuple[str, ...],
    args: argparse.Namespace,
) -> None:
    variant = f"{'ascsON' if args.include_ascs else 'ascsOFF'}_q{int(round(args.c_scale_quantile * 100))}"
    output_dir = args.output_dir / f"{gender_key}_{variant}"
    estimate(
        gender_key,
        df,
        labels,
        include_ascs=args.include_ascs,
        gender_column=args.gender_column,
        output_dir=output_dir,
        log_level=getattr(logging, args.log_level.upper()),
        c_scale_quantile=args.c_scale_quantile,
        variant=variant,
    )


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format="%(message)s")

    labels_arg = tuple(args.labels) if args.labels and not args.auto_labels else None

    if args.pooled:
        male_path = args.data_dir / "heads_wide_single_male_dcm.parquet"
        female_path = args.data_dir / "heads_wide_single_female_dcm.parquet"
        male_df = maybe_add_gender(load_wide_dataset(male_path), 0.0, args.gender_column)
        female_df = maybe_add_gender(load_wide_dataset(female_path), 1.0, args.gender_column)

        labels = detect_labels(male_df, labels_arg)
        labels_f = detect_labels(female_df, labels)
        if labels != labels_f:
            raise ValueError("Scenario labels differ between genders; align datasets before pooling.")

        common_cols = sorted(set(male_df.columns).intersection(female_df.columns))
        pooled_df = pd.concat([male_df[common_cols], female_df[common_cols]], ignore_index=True, sort=False)
        run_for_gender("pooled", pooled_df, labels, args)
        return

    for gender in args.genders:
        try:
            dataset_path = args.data_dir / f"heads_wide_single_{gender}_dcm.parquet"
            df = load_wide_dataset(dataset_path)
            labels = detect_labels(df, labels_arg)
            run_for_gender(gender, df, labels, args)
        except Exception as exc:
            LOGGER.error("[%s] Estimation failed: %s", gender, exc, exc_info=True)


if __name__ == "__main__":
    main()

"""
Example usage:

# Pooled estimation with ASC parameters
python scripts/DCM1_boxcox.py --pooled --include-ascs

# Male-only estimation without ASCs
python scripts/DCM1_boxcox.py --genders male
"""
