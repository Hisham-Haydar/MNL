#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-12-02 20:56:43
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/


"""
RURO Box–Cox MNL with group-specific preferences and opportunity densities.

This script estimates a RURO-style Box–Cox multinomial logit on a long (idperson, draw)
dataset produced by RURO_prep_mnl_basic.py (after EUROMOD integration).

Utility:
    V_ij = U_pref_ij + log f_ij^opp
with group-specific consumption/leisure slopes and a parametric opportunity density over
hours, wages, occupation, and region, including mass at zero hours.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

from path_helpers import reports_root

LOGGER = logging.getLogger(__name__)

T_HOURS_DEFAULT: float = 80.0  # total weekly time endowment (continuous-RURO, 80 hours)
LEIS_HOURS_MIN: float = 1.0
C_NORM_MIN: float = 0.2
C_NORM_MAX: float = 5.0
L_NORM_MIN: float = 0.2
L_NORM_MAX: float = 5.0
EPS_BOXCOX: float = 1e-6  # epsilon for Box–Cox to avoid extreme derivatives


# ---------------------------------------------------------------------------
# Box–Cox helpers
# ---------------------------------------------------------------------------

def boxcox_transform(x: np.ndarray, alpha: float) -> np.ndarray:
    """Box–Cox transform with smooth limit at alpha→0."""
    x = np.clip(x, EPS_BOXCOX, None)
    if abs(alpha) < 1e-8:
        return np.log(x)
    return (np.power(x, alpha) - 1.0) / alpha


def d_boxcox_dalpha(x: np.ndarray, alpha: float) -> np.ndarray:
    """Derivative of Box–Cox transform w.r.t. alpha."""
    x = np.clip(x, EPS_BOXCOX, None)
    ln_x = np.log(x)
    if abs(alpha) < 1e-8:
        return 0.5 * ln_x * ln_x
    x_a = np.power(x, alpha)
    num = alpha * x_a * ln_x - (x_a - 1.0)
    den = alpha * alpha
    return num / den


def boxcox_derivative(x: np.ndarray, alpha: float) -> np.ndarray:
    """Derivative of Box–Cox transform w.r.t its argument."""
    x = np.clip(x, EPS_BOXCOX, None)
    if abs(alpha) < 1e-8:
        return 1.0 / x
    return np.power(x, alpha - 1.0)


# ---------------------------------------------------------------------------
# Data container
# ---------------------------------------------------------------------------

@dataclass
class RuroData:
    n_individuals: int
    group_start: np.ndarray
    group_end: np.ndarray
    chosen_index: np.ndarray
    weights: np.ndarray

    cons: np.ndarray
    leis: np.ndarray
    hours: np.ndarray
    wage: np.ndarray
    prior: np.ndarray
    c_norm: np.ndarray
    l_norm: np.ndarray
    educL: np.ndarray
    educH: np.ndarray
    pexp: np.ndarray
    pexp2: np.ndarray
    yd1: np.ndarray
    yd2: np.ndarray
    dag: np.ndarray
    rural: np.ndarray

    group_ids: np.ndarray          # (n_individuals,) values 0..3
    region_ids: np.ndarray         # (n_individuals,) region index
    row_group_ids: np.ndarray      # (M,) group id per row
    row_region_ids: np.ndarray     # (M,) region id per row
    loc_ids: np.ndarray            # (M,) loc index

    y_ref: float
    l_ref: float
    c_ref_mode: str
    l_ref_mode: str
    t_hours: float

    z_per_row: np.ndarray          # (M, K) or (M, 0)
    z_names: List[str]

    group_names: List[str]
    region_labels: List[str]
    loc_labels: List[str]
    loc_baseline_label: str


# ---------------------------------------------------------------------------
# I/O helper
# ---------------------------------------------------------------------------

def _read_dataframe(path: Path) -> pd.DataFrame:
    suf = path.suffix.lower()
    if suf == ".parquet":
        return pd.read_parquet(path)  # type: ignore[arg-type]
    if suf == ".feather":
        return pd.read_feather(path)  # type: ignore[arg-type]
    if suf in {".pkl", ".pickle"}:
        return pd.read_pickle(path)
    if suf == ".csv":
        return pd.read_csv(path)
    if suf == ".txt":
        return pd.read_csv(path, sep="\t")
    raise ValueError(f"Unsupported dataset format: {path}")


def _logistic(x: np.ndarray) -> np.ndarray:
    """Numerically stable logistic."""
    x_clipped = np.clip(x, -50, 50)
    return 1.0 / (1.0 + np.exp(-x_clipped))


# ---------------------------------------------------------------------------
# Data preparation
# ---------------------------------------------------------------------------

def _assign_group(ruro_group: float, dgn: float) -> int:
    if ruro_group == 1 and dgn == 1:
        return 0  # single_m
    if ruro_group == 1 and dgn == 0:
        return 1  # single_f
    if ruro_group == 10 and dgn == 1:
        return 2  # couple_m
    if ruro_group == 10 and dgn == 0:
        return 3  # couple_f
    raise ValueError(f"Invalid (ruro_group, dgn) combination: ({ruro_group}, {dgn})")


def build_ruro_data(
    df: pd.DataFrame,
    *,
    id_col: str = "idperson",
    choice_col: str = "is_chosen",
    cons_col: str = "consumption",
    hours_col: Optional[str] = "hours",
    leisure_col: Optional[str] = "leisure",
    wage_col: str = "wage",
    loc_col: str = "loc",
    region_col: str = "drgn1",
    weight_col: Optional[str] = None,
    t_hours: float = T_HOURS_DEFAULT,
    c_ref_mode: str = "mean",
    l_ref_mode: str = "mean",
    z_cols: Optional[List[str]] = None,
    ignore_regions: bool = False,
) -> RuroData:
    required = [id_col, choice_col, cons_col, loc_col, "ruro_group", "dgn"]
    for col in required:
        if col not in df.columns:
            raise KeyError(f"Dataset missing required column '{col}'")
    if leisure_col is None and hours_col is None:
        raise ValueError("Either hours_col or leisure_col must be provided.")

    df = df.copy()

    # Ensure numeric types
    num_cols = [cons_col, choice_col, loc_col, "ruro_group", "dgn"]
    if hours_col:
        num_cols.append(hours_col)
    if leisure_col:
        num_cols.append(leisure_col)
    if wage_col:
        num_cols.append(wage_col)
    if weight_col:
        num_cols.append(weight_col)
    if z_cols:
        num_cols.extend(z_cols)
    if not ignore_regions:
        num_cols.append(region_col)
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Sort
    sort_cols = [id_col]
    if "draw" in df.columns:
        sort_cols.append("draw")
    df.sort_values(sort_cols, inplace=True)
    df.reset_index(drop=True, inplace=True)

    ids = df[id_col].to_numpy()
    choice = (df[choice_col] > 0).to_numpy(dtype=bool)
    cons = df[cons_col].to_numpy(dtype=float)
    # Education dummies from prepared columns or deh
    if "educL" in df.columns and "educH" in df.columns:
        educL = pd.to_numeric(df["educL"], errors="coerce").fillna(0.0).to_numpy(dtype=float)
        educH = pd.to_numeric(df["educH"], errors="coerce").fillna(0.0).to_numpy(dtype=float)
    elif "deh" in df.columns:
        deh_num = pd.to_numeric(df["deh"], errors="coerce")
        educL = deh_num.isin([0, 1, 2]).astype(float).to_numpy()
        educH = (deh_num == 5).astype(float).to_numpy()
    else:
        educL = np.zeros(len(df), dtype=float)
        educH = np.zeros(len(df), dtype=float)

    # Experience (years) and square
    pexp = pd.to_numeric(df.get("pexp_years", df.get("pexp", 0.0)), errors="coerce").fillna(0.0).to_numpy(dtype=float)
    pexp2 = pd.to_numeric(df.get("pexp_years2", pexp * pexp), errors="coerce").fillna(0.0).to_numpy(dtype=float)

    # Year dummies (baseline absorbed)
    yd1 = pd.to_numeric(df.get("yd1", 0.0), errors="coerce").fillna(0.0).to_numpy(dtype=float)
    yd2 = pd.to_numeric(df.get("yd2", 0.0), errors="coerce").fillna(0.0).to_numpy(dtype=float)

    # Age and rural/urban
    dag = pd.to_numeric(df.get("dag", 0.0), errors="coerce").fillna(0.0).to_numpy(dtype=float)
    rural = pd.to_numeric(df.get("drgur", 0.0), errors="coerce").fillna(0.0).to_numpy(dtype=float)

    # Leisure + hours
    if leisure_col and leisure_col in df.columns:
        # Use leisure from the MNL prep step (TOTAL_LEISURE_HOURS = 80 in RURO_prep_mnl_basic.py)
        leis_hours = pd.to_numeric(df[leisure_col], errors="coerce").to_numpy(dtype=float)
        if hours_col and hours_col in df.columns:
            hours = pd.to_numeric(df[hours_col], errors="coerce").to_numpy(dtype=float)
        else:
            hours = (t_hours - leis_hours).astype(float)
    else:
        if hours_col not in df.columns:
            raise KeyError(f"hours_col='{hours_col}' not found.")
        hours = pd.to_numeric(df[hours_col], errors="coerce").to_numpy(dtype=float)
        leis_hours = t_hours - hours
    # Clip leisure to [LEIS_HOURS_MIN, t_hours] to avoid negative/zero leisure
    leis_hours = np.clip(leis_hours, LEIS_HOURS_MIN, t_hours)
    # IMPORTANT: keep leisure in HOURS (no division by t_hours)
    leis = leis_hours
    if LOGGER.isEnabledFor(logging.INFO):
        total = leis_hours.size
        share_zero = float((leis_hours == LEIS_HOURS_MIN).sum()) / total
        share_full = float((leis_hours == t_hours).sum()) / total
        LOGGER.info(
            "Leisure clipping stats: share_min=%.6f, share_full=%.6f",
            share_zero,
            share_full,
        )

    # Wage
    if wage_col in df.columns:
        wage = pd.to_numeric(df[wage_col], errors="coerce").to_numpy(dtype=float)
    elif "wage_ruro" in df.columns:
        wage = pd.to_numeric(df["wage_ruro"], errors="coerce").to_numpy(dtype=float)
    elif "yivwg" in df.columns:
        wage = pd.to_numeric(df["yivwg"], errors="coerce").to_numpy(dtype=float)
    else:
        raise KeyError("Dataset must contain a wage column (wage, wage_ruro, or yivwg).")

    # Group structure
    unique_ids, group_start = np.unique(ids, return_index=True)
    n_individuals = unique_ids.size
    group_end = np.empty_like(group_start)
    group_end[:-1] = group_start[1:]
    group_end[-1] = len(df)

    chosen_index = np.empty(n_individuals, dtype=int)
    weights = np.ones(n_individuals, dtype=float)

    group_ids = np.empty(n_individuals, dtype=int)
    region_ids = np.empty(n_individuals, dtype=int)

    # Build region indices (labels sorted)
    if ignore_regions:
        region_labels = ["baseline_region"]
        region_to_idx = {"baseline_region": 0}
        region_series = pd.Series(["baseline_region"] * len(df))
    else:
        if region_col not in df.columns:
            raise KeyError(f"Dataset missing required column '{region_col}'")
        region_labels = sorted(df[region_col].dropna().unique().tolist())
        if not region_labels:
            raise ValueError("No region labels found.")
        region_to_idx = {lab: i for i, lab in enumerate(region_labels)}
        region_series = df[region_col]

    # Build loc indices (baseline: 0 if exists else modal)
    loc_labels_all = df[loc_col].dropna().astype(int)
    if loc_labels_all.empty:
        raise ValueError("No loc values found.")
    loc_counts = loc_labels_all.value_counts()
    loc_labels_unique = sorted(loc_counts.index.unique().tolist())
    if 0 in loc_labels_unique:
        loc_baseline = 0
    else:
        loc_baseline = int(loc_counts.idxmax())
    loc_labels = [loc_baseline] + [l for l in loc_labels_unique if l != loc_baseline]
    loc_to_idx = {lab: i for i, lab in enumerate(loc_labels)}
    loc_baseline_label = str(loc_baseline)

    # z columns
    if z_cols is None:
        z_cols = []
    for z in z_cols:
        if z not in df.columns:
            raise KeyError(f"Requested shifter column '{z}' not found.")
    if z_cols:
        df[z_cols] = df[z_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        z_per_row = df[z_cols].to_numpy(dtype=float)
    else:
        z_per_row = np.zeros((len(df), 0), dtype=float)

    row_group_ids = np.empty(len(df), dtype=int)
    row_region_ids = np.empty(len(df), dtype=int)
    loc_ids = np.empty(len(df), dtype=int)

    # Assign groups and validate choice
    ruro_group_series = pd.to_numeric(df["ruro_group"], errors="coerce").fillna(-1)
    dgn_series = pd.to_numeric(df["dgn"], errors="coerce").fillna(-1)
    loc_series = df[loc_col]

    for g, s in enumerate(group_start):
        e = group_end[g]
        ch_g = choice[s:e]
        if not np.any(ch_g):
            raise ValueError(f"Individual {unique_ids[g]} has no chosen alternative.")
        if np.sum(ch_g) > 1:
            raise ValueError(f"Individual {unique_ids[g]} has multiple chosen alternatives.")
        chosen_index[g] = s + np.argmax(ch_g)

        # weight
        if weight_col and weight_col in df.columns:
            w = float(df.iloc[s][weight_col])
            if not np.isfinite(w) or w <= 0:
                w = 1.0
            weights[g] = w

        # group assignment
        rg = ruro_group_series.iloc[s]
        dgn = dgn_series.iloc[s]
        group_ids[g] = _assign_group(rg, dgn)

        # region
        reg_val = region_series.iloc[s]
        if reg_val not in region_to_idx:
            raise ValueError(f"Region label {reg_val} not in region_labels.")
        reg_idx = region_to_idx[reg_val]
        region_ids[g] = reg_idx
        row_region_ids[s:e] = reg_idx
        row_group_ids[s:e] = group_ids[g]

    # loc indices per row
    for i, loc_val in enumerate(loc_series):
        if loc_val not in loc_to_idx:
            raise ValueError(f"loc label {loc_val} not found in loc mapping.")
        loc_ids[i] = loc_to_idx[loc_val]

    # Normalisation using chosen alts
    cons_chosen = cons[chosen_index]
    # Use leisure already normalised to [0,1]
    leis_chosen = leis[chosen_index]
    cons_pos = cons_chosen[np.isfinite(cons_chosen) & (cons_chosen > 0.0)]
    if cons_pos.size == 0:
        raise ValueError("No positive consumption among chosen alternatives.")
    if c_ref_mode == "mean":
        y_ref = float(cons_pos.mean())
    elif c_ref_mode == "p99":
        y_ref = float(np.quantile(cons_pos, 0.99))
        if not np.isfinite(y_ref) or y_ref <= 0:
            y_ref = float(cons_pos.mean())
    else:
        raise ValueError("c_ref_mode must be 'mean' or 'p99'.")

    leis_pos = leis_chosen[np.isfinite(leis_chosen) & (leis_chosen > 0.0)]
    if leis_pos.size == 0:
        raise ValueError("No positive leisure among chosen alternatives.")
    if l_ref_mode == "minpos":
        l_ref = float(leis_pos.min())
    elif l_ref_mode == "mean":
        l_ref = float(leis_pos.mean())
    else:
        raise ValueError("l_ref_mode must be 'minpos' or 'mean'.")

    c_norm = cons / y_ref
    l_norm = leis / l_ref
    nonpos_c = int(np.sum(c_norm <= 0))
    nonpos_l = int(np.sum(l_norm <= 0))
    if nonpos_c or nonpos_l:
        LOGGER.warning(
            "Some normalised c or l are non-positive; they will be clipped. "
            "counts c<=0=%d, l<=0=%d",
            nonpos_c,
            nonpos_l,
        )
    # Clip Box–Cox inputs to safe range
    c_norm = np.clip(c_norm, C_NORM_MIN, C_NORM_MAX)
    l_norm = np.clip(l_norm, L_NORM_MIN, L_NORM_MAX)

    if "prior" not in df.columns:
        raise KeyError("RURO MNL dataset must contain a 'prior' column with log opportunity density.")
    prior = pd.to_numeric(df["prior"], errors="coerce").to_numpy(dtype=float)

    group_names = ["single_m", "single_f", "couple_m", "couple_f"]

    return RuroData(
        n_individuals=n_individuals,
        group_start=group_start,
        group_end=group_end,
        chosen_index=chosen_index,
        weights=weights,
        cons=cons,
        leis=leis,
        hours=hours,
        wage=wage,
        prior=prior,
        c_norm=c_norm,
        l_norm=l_norm,
        educL=educL,
        educH=educH,
        pexp=pexp,
        pexp2=pexp2,
        yd1=yd1,
        yd2=yd2,
        dag=dag,
        rural=rural,
        group_ids=group_ids,
        region_ids=region_ids,
        row_group_ids=row_group_ids,
        row_region_ids=row_region_ids,
        loc_ids=loc_ids,
        y_ref=y_ref,
        l_ref=l_ref,
        c_ref_mode=c_ref_mode,
        l_ref_mode=l_ref_mode,
        t_hours=t_hours,
        z_per_row=z_per_row,
        z_names=list(z_cols) if z_cols else [],
        group_names=group_names,
        region_labels=[str(lab) for lab in region_labels],
        loc_labels=[str(lab) for lab in loc_labels],
        loc_baseline_label=str(loc_baseline_label),
    )


# ---------------------------------------------------------------------------
# Parameter handling
# ---------------------------------------------------------------------------

def _param_names(data: RuroData) -> List[str]:
    names = [
        "alpha_c",
        "alpha_l",
        "beta_c_single_m",
        "beta_c_single_f",
        "beta_c_couple_m",
        "beta_c_couple_f",
        "beta_l0_single_m",
        "beta_l0_single_f",
        "beta_l0_couple_m",
        "beta_l0_couple_f",
    ]
    names.extend([f"delta_{z}" for z in data.z_names])
    names.extend([
        "kappa0_single_m",
        "kappa0_single_f",
        "kappa0_couple_m",
        "kappa0_couple_f",
    ])
    names.extend(["kappa_educL", "kappa_educH"])
    # Region effects (skip baseline region index 0)
    for lab in data.region_labels[1:]:
        names.append(f"lambda_region_{lab}")
    names.extend(["theta_h1", "theta_h2"])
    # LOC covariate slopes (shared feature set per loc)
    loc_feature_labels = ["educL", "educH", "age", "rural"]
    for lab in data.loc_labels[1:]:
        for feat in loc_feature_labels:
            names.append(f"phi_loc_{lab}_{feat}")
    names.extend([
        "gamma_w0",
        "gamma_w_educL",
        "gamma_w_educH",
        "gamma_w_pexp",
        "gamma_w_pexp2",
        "gamma_w_yd1",
        "gamma_w_yd2",
        "log_sigma_w",
    ])
    # LOC effects (skip baseline loc index 0)
    for lab in data.loc_labels[1:]:
        names.append(f"psi_loc_{lab}")
    return names


def _theta_slices(data: RuroData) -> Tuple[int, int, int, int, int, int, int, int, int, int, int, int]:
    K = len(data.z_names)
    Rm1 = max(len(data.region_labels) - 1, 0)
    Lm1 = max(len(data.loc_labels) - 1, 0)
    loc_feat_count = 4  # educL, educH, age, rural
    idx = 0
    idx_alpha = idx
    idx += 2
    idx_beta_c = idx
    idx += 4
    idx_beta_l0 = idx
    idx += 4
    idx_delta = idx
    idx += K
    idx_kappa0 = idx
    idx += 4
    idx_kappa_educ = idx
    idx += 2
    idx_lambda = idx
    idx += Rm1
    idx_theta = idx  # hours poly
    idx += 2
    idx_phi_loc = idx
    idx += Lm1 * loc_feat_count
    idx_gamma_w = idx
    idx += 7  # wage mean shifters
    idx_log_sigma = idx
    idx += 1
    idx_psi = idx
    idx += Lm1
    total_len = idx
    return (
        idx_alpha,
        idx_beta_c,
        idx_beta_l0,
        idx_delta,
        idx_kappa0,
        idx_kappa_educ,
        idx_lambda,
        idx_theta,
        idx_phi_loc,
        idx_gamma_w,
        idx_log_sigma,
        idx_psi,
        total_len,
    )


# ---------------------------------------------------------------------------
# Likelihood and gradient
# ---------------------------------------------------------------------------

def _logit_prob_and_grad(
    u: np.ndarray,
    dV: np.ndarray,
    chosen_loc: int,
    weight: float,
    grad: np.ndarray,
) -> float:
    """
    Compute logit probability and accumulate gradient contribution.
    u: utilities (J,)
    dV: derivatives w.r.t parameters (J, P)
    chosen_loc: index of chosen alternative within u
    weight: individual weight
    grad: gradient vector to update in-place
    """
    u_max = float(np.max(u))
    exp_u = np.exp(u - u_max)
    denom = float(exp_u.sum())
    if denom <= 0.0 or not np.isfinite(denom):
        return 1e12
    p = exp_u / denom
    p_star = float(p[chosen_loc])
    if p_star <= 0.0 or not np.isfinite(p_star):
        return 1e12
    # gradient
    EV = p @ dV
    dV_star = dV[chosen_loc]
    grad -= weight * (dV_star - EV)
    return -weight * math.log(p_star)


def neg_loglik_and_grad(theta: np.ndarray, data: RuroData) -> Tuple[float, np.ndarray]:
    (
        idx_alpha,
        idx_beta_c,
        idx_beta_l0,
        idx_delta,
        idx_kappa0,
        idx_kappa_educ,
        idx_lambda,
        idx_theta,
        idx_phi_loc,
        idx_gamma_w,
        idx_log_sigma,
        idx_psi,
        k_expected,
    ) = _theta_slices(data)
    if len(theta) != k_expected:
        raise ValueError(f"Theta length {len(theta)} incompatible (expected {k_expected}).")

    K = len(data.z_names)

    alpha_c = theta[idx_alpha]
    alpha_l = theta[idx_alpha + 1]

    beta_c = theta[idx_beta_c:idx_beta_c + 4]
    beta_l0 = theta[idx_beta_l0:idx_beta_l0 + 4]
    delta = theta[idx_delta:idx_delta + K] if K > 0 else np.zeros(0, dtype=float)

    M = len(data.cons)
    P = len(theta)
    grad = np.zeros(P, dtype=float)

    # Box–Cox terms for all rows (vectorised)
    bc_c = boxcox_transform(data.c_norm, alpha_c)
    bc_l = boxcox_transform(data.l_norm, alpha_l)
    bc_c_da = d_boxcox_dalpha(data.c_norm, alpha_c)
    bc_l_da = d_boxcox_dalpha(data.l_norm, alpha_l)

    log_prior_all = data.prior.astype(float)

    row_gid = data.row_group_ids.astype(int)
    beta_l_row_all = beta_l0[row_gid]
    if K > 0:
        beta_l_row_all = beta_l_row_all + data.z_per_row @ delta
    u_pref_all = beta_c[row_gid] * bc_c + beta_l_row_all * bc_l

    nll_total = 0.0
    G = data.n_individuals

    for i in range(G):
        s = data.group_start[i]
        e = data.group_end[i]
        idx_slice = slice(s, e)
        g_id = int(data.group_ids[i])

        rows_len = e - s
        z_rows = data.z_per_row[idx_slice] if K > 0 else np.zeros((rows_len, 0), dtype=float)

        u_pref = u_pref_all[idx_slice]
        log_prior = log_prior_all[idx_slice]
        V = u_pref + log_prior

        # Derivative matrix dV/dtheta per row
        dV = np.zeros((rows_len, P), dtype=float)
        dV[:, idx_alpha] = beta_c[g_id] * bc_c_da[idx_slice]
        dV[:, idx_alpha + 1] = beta_l_row_all[idx_slice] * bc_l_da[idx_slice]
        dV[:, idx_beta_c + g_id] = bc_c[idx_slice]
        dV[:, idx_beta_l0 + g_id] = bc_l[idx_slice]
        if K > 0:
            dV[:, idx_delta:idx_delta + K] = z_rows * bc_l[idx_slice, None]

        chosen_loc = data.chosen_index[i] - s
        w_i = data.weights[i]
        nll = _logit_prob_and_grad(V, dV, chosen_loc, w_i, grad)
        if not np.isfinite(nll):
            return 1e12, np.zeros_like(theta)
        nll_total += nll

    return nll_total, grad


def neg_loglik(theta: np.ndarray, data: RuroData) -> float:
    nll, _ = neg_loglik_and_grad(theta, data)
    return nll


def grad_neg_loglik(theta: np.ndarray, data: RuroData) -> np.ndarray:
    _, grad = neg_loglik_and_grad(theta, data)
    return grad


# ---------------------------------------------------------------------------
# Diagnostics and estimation
# ---------------------------------------------------------------------------

def compute_null_loglik(data: RuroData) -> float:
    ll = 0.0
    for i in range(data.n_individuals):
        J = data.group_end[i] - data.group_start[i]
        if J > 0:
            ll -= data.weights[i] * math.log(J)
    return ll


def compute_prior_only_loglik(data: RuroData) -> float:
    """
    Log-likelihood of a model with utilities equal to the prior only:
        V_id = log f^opp_id
    This is the "RURO opportunities only" benchmark (no preferences).
    """
    ll = 0.0
    for i in range(data.n_individuals):
        s = data.group_start[i]
        e = data.group_end[i]
        if e <= s:
            continue
        log_prior = data.prior[s:e].astype(float)
        u_max = float(np.max(log_prior))
        exp_u = np.exp(log_prior - u_max)
        denom = float(exp_u.sum())
        if denom <= 0.0 or not np.isfinite(denom):
            J = e - s
            if J > 0:
                ll += -data.weights[i] * math.log(J)
            continue
        p = exp_u / denom
        chosen_loc = data.chosen_index[i] - s
        p_star = float(p[chosen_loc])
        if p_star <= 0.0 or not np.isfinite(p_star):
            J = e - s
            if J > 0:
                ll += -data.weights[i] * math.log(J)
            continue
        ll += data.weights[i] * math.log(p_star)
    return ll


def approximate_hessian(theta: np.ndarray, data: RuroData, eps: float = 1e-5) -> np.ndarray:
    k = len(theta)
    H = np.zeros((k, k), dtype=float)
    f0 = neg_loglik(theta, data)
    eye = np.eye(k)

    def h(i: int) -> float:
        return eps * max(1.0, abs(theta[i]))

    for i in range(k):
        hi = h(i)
        ei = eye[i] * hi
        f_plus = neg_loglik(theta + ei, data)
        f_minus = neg_loglik(theta - ei, data)
        H[i, i] = (f_plus - 2.0 * f0 + f_minus) / (hi * hi)
        for j in range(i + 1, k):
            hj = h(j)
            ej = eye[j] * hj
            f_pp = neg_loglik(theta + ei + ej, data)
            f_pm = neg_loglik(theta + ei - ej, data)
            f_mp = neg_loglik(theta - ei + ej, data)
            f_mm = neg_loglik(theta - ei - ej, data)
            H_ij = (f_pp - f_pm - f_mp + f_mm) / (4.0 * hi * hj)
            H[i, j] = H[j, i] = H_ij
    return H


def run_estimation(
    data: RuroData,
    output_dir: Path,
    *,
    model_name: str = "ruro_boxcox_groupopps",
    compute_hessian: bool = False,
    eval_initial_only: bool = False,
    maxiter: int = 2000,
    pgtol: float = 1e-5,
    ftol: float = 1e-9,
    init_json: Path | None = None,
    init_csv: Path | None = None,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    names = _param_names(data)
    (
        idx_alpha,
        idx_beta_c,
        idx_beta_l0,
        idx_delta,
        idx_kappa0,
        idx_kappa_educ,
        idx_lambda,
        idx_theta,
        idx_phi_loc,
        idx_gamma_w,
        idx_log_sigma,
        idx_psi,
        k_expected,
    ) = _theta_slices(data)

    # initial theta
    theta0 = np.zeros(k_expected, dtype=float)
    theta0[0] = 0.10  # alpha_c
    theta0[1] = 0.10  # alpha_l
    theta0[2:6] = 1.0  # beta_c
    theta0[6:10] = 1.0  # beta_l0
    # kappa0 for pi0 ≈ 0.1
    init_kappa = math.log(0.1 / 0.9)
    theta0[idx_kappa0:idx_kappa0 + 4] = init_kappa
    theta0[idx_kappa_educ:idx_kappa_educ + 2] = 0.0
    theta0[idx_theta:idx_theta + 2] = 0.1  # mild slope on hours
    theta0[idx_gamma_w:idx_gamma_w + 7] = 0.0
    theta0[idx_log_sigma] = 0.0  # sigma_w = 1

    # Optional: load initial theta from JSON/CSV
    init_sources = []
    if init_json:
        init_sources.append(("json", init_json))
    if init_csv:
        init_sources.append(("csv", init_csv))
    if init_sources:
        init_map: dict[str, float] = {}
        for src_kind, src_path in init_sources:
            try:
                if src_kind == "json":
                    obj = json.loads(init_json.read_text(encoding="utf-8"))
                    theta_hat = obj.get("theta_hat", obj if isinstance(obj, dict) else {})
                    init_map.update({k: float(v) for k, v in theta_hat.items() if v is not None})
                else:
                    df_init = pd.read_csv(init_csv)
                    if {"Name", "Value"}.issubset(df_init.columns):
                        init_map.update({str(r["Name"]): float(r["Value"]) for _, r in df_init.iterrows()})
            except Exception as exc:
                LOGGER.warning("Could not load init parameters from %s: %s", src_path, exc)
        if init_map:
            for pos, name in enumerate(names):
                if name in init_map:
                    theta0[pos] = init_map[name]
            LOGGER.info("Loaded %d initial parameters from provided source(s).", len(init_map))

    LOGGER.info("Initial theta length=%d", len(theta0))

    # Optional dry-run: evaluate NLL/grad at initial theta and exit
    if eval_initial_only:
        nll0, grad0 = neg_loglik_and_grad(theta0, data)
        grad_norm = float(np.linalg.norm(grad0))
        LOGGER.info("Initial NLL: %.6f |grad|: %.6f", nll0, grad_norm)
        return

    iter_state = {"k": 0}

    def _cb(xk: np.ndarray) -> None:
        iter_state["k"] += 1
        try:
            nll_cb, grad_cb = neg_loglik_and_grad(xk, data)
            grad_norm = float(np.linalg.norm(grad_cb))
            LOGGER.info("[iter %4d] nll=%.6f |grad|=%.6f", iter_state["k"], nll_cb, grad_norm)
        except Exception as exc:
            LOGGER.warning("Callback eval failed at iter %d: %s", iter_state["k"], exc)

    bounds = [(None, None)] * len(theta0)
    bounds[idx_alpha] = (0.10, 3.00)       # alpha_c bounds
    bounds[idx_alpha + 1] = (-2.50, -0.20) # alpha_l bounds

    result = minimize(
        neg_loglik,
        theta0,
        args=(data,),
        method="L-BFGS-B",
        jac=grad_neg_loglik,
        callback=_cb,
        options={
            "maxiter": maxiter,
            "ftol": ftol,   # relative f-change tolerance
            "gtol": pgtol,  # projected gradient tolerance
            "maxls": 50,    # default line-search steps
        },
        bounds=bounds,
    )

    if not result.success:
        LOGGER.warning("Optimiser did not fully converge: %s", result.message)
    LOGGER.info("Optimizer status=%s message=%s", result.status, result.message)

    theta_hat = result.x
    nll_star, _ = neg_loglik_and_grad(theta_hat, data)
    ll_star = -nll_star
    ll_null = compute_null_loglik(data)
    ll_prior_only = compute_prior_only_loglik(data)

    k = len(theta_hat)
    rho2 = 1.0 - ll_star / ll_null if ll_null != 0 else float("nan")
    rho2_adj = 1.0 - (ll_star - k) / ll_null if ll_null != 0 else float("nan")
    if ll_prior_only != 0 and np.isfinite(ll_prior_only):
        rho2_prior = 1.0 - ll_star / ll_prior_only
        rho2_prior_adj = 1.0 - (ll_star - k) / ll_prior_only
    else:
        rho2_prior = float("nan")
        rho2_prior_adj = float("nan")

    # Hessian and SEs (optional, disabled by default for speed)
    if compute_hessian:
        H = approximate_hessian(theta_hat, data)
        H = 0.5 * (H + H.T)
        try:
            cov = np.linalg.inv(H)
        except np.linalg.LinAlgError:
            LOGGER.warning("Hessian not invertible; using pseudo-inverse.")
            cov = np.linalg.pinv(H)
        diag_cov = np.diag(cov)
        se = np.sqrt(np.maximum(diag_cov, 0.0))
        t_vals = np.empty_like(theta_hat)
        p_vals = np.empty_like(theta_hat)
        for i in range(k):
            if se[i] > 0:
                t_vals[i] = theta_hat[i] / se[i]
                p_vals[i] = 2.0 * (1.0 - norm.cdf(abs(t_vals[i])))
            else:
                t_vals[i] = np.nan
                p_vals[i] = np.nan
    else:
        LOGGER.info("Skipping Hessian/SE computation (compute_hessian=False).")
        se = np.full_like(theta_hat, np.nan)
        t_vals = np.full_like(theta_hat, np.nan)
        p_vals = np.full_like(theta_hat, np.nan)

    n_obs = data.n_individuals
    aic = 2 * k - 2 * ll_star
    bic = math.log(n_obs) * k - 2 * ll_star

    param_dict = {n: float(v) for n, v in zip(names, theta_hat)}
    se_dict = {n: float(s) for n, s in zip(names, se)}
    t_dict = {n: (float(t) if np.isfinite(t) else float("nan")) for n, t in zip(names, t_vals)}
    p_dict = {n: (float(p) if np.isfinite(p) else float("nan")) for n, p in zip(names, p_vals)}

    # ------------------------------------------------------------------
    # Predictive accuracy and MUC/MUL diagnostics at the chosen alt
    # ------------------------------------------------------------------
    (
        idx_alpha,
        idx_beta_c,
        idx_beta_l0,
        idx_delta,
        idx_kappa0,
        idx_kappa_educ,
        idx_lambda,
        idx_theta,
        idx_phi_loc,
        idx_gamma_w,
        idx_log_sigma,
        idx_psi,
        _,
    ) = _theta_slices(data)
    alpha_c = theta_hat[idx_alpha]
    alpha_l = theta_hat[idx_alpha + 1]
    beta_c = theta_hat[idx_beta_c:idx_beta_c + 4]
    beta_l0 = theta_hat[idx_beta_l0:idx_beta_l0 + 4]
    delta = theta_hat[idx_delta:idx_delta + len(data.z_names)] if len(data.z_names) else np.zeros(0, dtype=float)
    # Box-Cox terms
    bc_c = boxcox_transform(data.c_norm, alpha_c)
    bc_l = boxcox_transform(data.l_norm, alpha_l)
    beta_l_row = beta_l0[data.row_group_ids]
    if delta.size:
        beta_l_row = beta_l_row + data.z_per_row @ delta
    pref_util = beta_c[data.row_group_ids] * bc_c + beta_l_row * bc_l

    log_prior = data.prior.astype(float)
    V = pref_util + log_prior

    pred_correct = 0.0
    total_w = 0.0
    p_chosen: list[float] = []
    for g in range(data.n_individuals):
        s, e = data.group_start[g], data.group_end[g]
        u_g = V[s:e]
        u_max = float(np.max(u_g))
        exp_u = np.exp(u_g - u_max)
        denom = float(exp_u.sum())
        if denom <= 0.0:
            continue
        p_g = exp_u / denom
        j_star_loc = data.chosen_index[g] - s
        p_chosen.append(float(p_g[j_star_loc]))
        pred_loc = int(np.argmax(p_g))
        if pred_loc == j_star_loc:
            pred_correct += data.weights[g]
        total_w += data.weights[g]
    accuracy = pred_correct / total_w if total_w > 0 else float("nan")
    p_chosen_mean = float(np.mean(p_chosen)) if p_chosen else float("nan")

    # MUC/MUL at chosen alternative
    chosen_rows = data.chosen_index
    bc_c_dx = boxcox_derivative(data.c_norm[chosen_rows], alpha_c)
    bc_l_dx = boxcox_derivative(data.l_norm[chosen_rows], alpha_l)
    beta_c_ch = beta_c[data.row_group_ids[chosen_rows]]
    beta_l_ch = beta_l_row[chosen_rows]
    muc = beta_c_ch * bc_c_dx / data.y_ref
    mul = beta_l_ch * bc_l_dx / data.l_ref

    def _summ(arr: np.ndarray) -> dict:
        arr = arr[np.isfinite(arr)]
        if arr.size == 0:
            return {}
        return {
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "p10": float(np.quantile(arr, 0.10)),
            "p90": float(np.quantile(arr, 0.90)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "share_negative": float(np.mean(arr < 0.0)),
        }

    muc_stats = _summ(muc)
    mul_stats = _summ(mul)
    leis_hours_chosen = np.clip(data.t_hours - data.hours[chosen_rows], LEIS_HOURS_MIN, data.t_hours)
    l_norm_chosen = data.l_norm[chosen_rows]
    leis_hours_stats = _summ(leis_hours_chosen)
    l_norm_stats = _summ(l_norm_chosen)

    meta = {
        "model": model_name,
        "theta_hat": param_dict,
        "se": se_dict,
        "t_values": t_dict,
        "p_values": p_dict,
        "ll_star": float(ll_star),
        "ll_null": float(ll_null),
        "ll_prior_only": float(ll_prior_only),
        "rho2": float(rho2),
        "rho2_adj": float(rho2_adj),
        "rho2_prior": float(rho2_prior),
        "rho2_prior_adj": float(rho2_prior_adj),
        "aic": float(aic),
        "bic": float(bic),
        "n_individuals": int(n_obs),
        "y_ref": float(data.y_ref),
        "l_ref": float(data.l_ref),
        "c_ref_mode": data.c_ref_mode,
        "l_ref_mode": data.l_ref_mode,
        "group_names": data.group_names,
        "region_labels": data.region_labels,
        "loc_labels": data.loc_labels,
        "loc_baseline": data.loc_baseline_label,
        "z_names": data.z_names,
        "t_hours": float(data.t_hours),
        "accuracy": float(accuracy),
        "p_chosen_mean": float(p_chosen_mean),
        "muc_stats": muc_stats,
        "mul_stats": mul_stats,
        "leis_hours_chosen_stats": leis_hours_stats,
        "l_norm_chosen_stats": l_norm_stats,
    }

    out_json = output_dir / f"{model_name}_results.json"
    out_json.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    LOGGER.info("Saved JSON results to %s", out_json)

    # Parameter CSV (enabled for downstream diagnostics)
    try:
        import csv  # noqa: F401

        out_csv = output_dir / f"{model_name}_parameters.csv"
        df_params = pd.DataFrame({
            "Name": names,
            "Value": theta_hat,
            "StdErr": se,
            "t": t_vals,
            "p": p_vals,
        })
        df_params.to_csv(out_csv, index=False)
        LOGGER.info("Saved parameter table to %s", out_csv)
    except Exception as exc:
        LOGGER.warning("Could not write parameter CSV: %s", exc)

    # Simple HTML summary for quick diagnostics
    try:
        html_lines = [
            "<html><body>",
            f"<h1>{model_name}</h1>",
            "<h2>Fit statistics</h2>",
            "<ul>",
            f"<li>LL*: {ll_star:.4f}</li>",
            f"<li>LL(null): {ll_null:.4f}</li>",
            f"<li>LL(prior-only): {ll_prior_only:.4f}</li>",
            f"<li>rho^2: {rho2:.4f}</li>",
            f"<li>rho^2_adj: {rho2_adj:.4f}</li>",
            f"<li>rho^2 (vs prior-only): {rho2_prior:.4f}</li>",
            f"<li>AIC: {aic:.2f}</li>",
            f"<li>BIC: {bic:.2f}</li>",
            f"<li>Accuracy (predicted vs chosen): {accuracy:.4f}</li>",
            f"<li>Mean P(chosen): {p_chosen_mean:.4f}</li>",
            "</ul>",
        ]
        def _stat_block(title: str, stats: dict) -> list[str]:
            if not stats:
                return [f"<p>No {title} stats available.</p>"]
            return [
                f"<h3>{title}</h3>",
                "<ul>",
                f"<li>Mean: {stats.get('mean', float('nan')):.4f}</li>",
                f"<li>Median: {stats.get('median', float('nan')):.4f}</li>",
                f"<li>P10: {stats.get('p10', float('nan')):.4f}</li>",
                f"<li>P90: {stats.get('p90', float('nan')):.4f}</li>",
                f"<li>Min/Max: {stats.get('min', float('nan')):.4f} / {stats.get('max', float('nan')):.4f}</li>",
                f"<li>Share negative: {stats.get('share_negative', float('nan')):.4f}</li>",
                "</ul>",
            ]

        html_lines.extend(_stat_block("MUC at chosen", muc_stats))
        html_lines.extend(_stat_block("MUL at chosen", mul_stats))
        html_lines.extend(_stat_block("Leisure (hours) at chosen", leis_hours_stats))
        html_lines.extend(_stat_block("Normalised leisure at chosen", l_norm_stats))
        html_lines.append(f"<p>Parameter table: {out_csv.name if 'out_csv' in locals() else 'n/a'}</p>")
        html_lines.append("</body></html>")

        out_html = output_dir / f"{model_name}_summary.html"
        out_html.write_text("\n".join(html_lines), encoding="utf-8")
        LOGGER.info("Saved HTML summary to %s", out_html)
    except Exception as exc:
        LOGGER.warning("Could not write HTML summary: %s", exc)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="RURO Box–Cox MNL estimation with group-specific preferences and opportunity functions."
    )
    parser.add_argument("--data-path", type=Path, required=True,
                        help="Path to long RURO MNL dataset (parquet/csv/pkl).")
    parser.add_argument("--id-col", default="idperson")
    parser.add_argument("--choice-col", default="is_chosen")
    parser.add_argument("--cons-col", default="consumption")
    parser.add_argument("--hours-col", default="hours")
    parser.add_argument("--leisure-col", default="leisure")
    parser.add_argument("--wage-col", default="wage")
    parser.add_argument("--loc-col", default="loc")
    parser.add_argument("--region-col", default="drgn1")
    parser.add_argument("--weight-col", default=None)
    parser.add_argument("--t-hours", type=float, default=T_HOURS_DEFAULT,
                        help="Time endowment for leisure (e.g. 80 or 168).")
    parser.add_argument("--c-ref", choices=("mean", "p99"), default="mean")
    parser.add_argument("--l-ref", choices=("minpos", "mean"), default="mean")
    parser.add_argument("--z-cols", nargs="*", default=None,
                        help="Individual-level preference shifters (ex. dag dag2 dgn drgur).")
    parser.add_argument("--ignore-regions", action="store_true",
                        help="Ignore region effects (treat all as one baseline region).")
    parser.add_argument("--output-dir", type=Path,
                        default=reports_root() / "mle_ruro" / "boxcox_groupopps")
    parser.add_argument("--model-name", default="ruro_boxcox_groupopps")
    parser.add_argument("--log-level", default="INFO",
                        choices=("DEBUG", "INFO", "WARNING", "ERROR"))
    parser.add_argument(
        "--num-threads",
        type=int,
        default=None,
        help="Optional override for BLAS/NumExpr thread count to better utilise CPU.",
    )
    parser.add_argument(
        "--maxiter",
        type=int,
        default=2000,
        help="Maximum L-BFGS-B iterations.",
    )
    parser.add_argument(
        "--pgtol",
        type=float,
        default=1e-5,
        help="L-BFGS-B projected gradient tolerance (smaller => tighter).",
    )
    parser.add_argument(
        "--ftol",
        type=float,
        default=1e-9,
        help="Relative f-change tolerance for convergence (smaller => tighter).",
    )
    parser.add_argument(
        "--init-json",
        type=Path,
        default=None,
        help="Optional JSON file with theta_hat to seed initial parameters (keys must match parameter names).",
    )
    parser.add_argument(
        "--init-csv",
        type=Path,
        default=None,
        help="Optional CSV file with columns Name,Value to seed initial parameters.",
    )
    parser.add_argument(
        "--compute-hessian",
        action="store_true",
        help="Compute Hessian/SEs at the solution (disabled by default to save time).",
    )
    parser.add_argument(
        "--eval-initial-only",
        action="store_true",
        help="Evaluate likelihood/gradient at initial parameters and exit (no optimisation).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                        format="%(message)s")

    if args.num_threads and args.num_threads > 0:
        import os

        val = str(args.num_threads)
        os.environ["OMP_NUM_THREADS"] = val
        os.environ["MKL_NUM_THREADS"] = val
        os.environ["NUMEXPR_NUM_THREADS"] = val
        LOGGER.info("Set thread env (OMP/MKL/NUMEXPR) to %s", val)

    df = _read_dataframe(args.data_path)
    LOGGER.info("Loaded dataset %s with %d rows and %d columns.",
                args.data_path, len(df), df.shape[1])

    data = build_ruro_data(
        df,
        id_col=args.id_col,
        choice_col=args.choice_col,
        cons_col=args.cons_col,
        hours_col=args.hours_col,
        leisure_col=args.leisure_col,
        wage_col=args.wage_col,
        loc_col=args.loc_col,
        region_col=args.region_col,
        weight_col=args.weight_col,
        t_hours=args.t_hours,
        c_ref_mode=args.c_ref,
        l_ref_mode=args.l_ref,
        z_cols=args.z_cols,
        ignore_regions=args.ignore_regions,
    )

    run_estimation(
        data,
        args.output_dir,
        model_name=args.model_name,
        compute_hessian=args.compute_hessian,
        eval_initial_only=args.eval_initial_only,
        maxiter=args.maxiter,
        pgtol=args.pgtol,
        ftol=args.ftol,
        init_json=args.init_json,
        init_csv=args.init_csv,
    )


if __name__ == "__main__":
    main()
