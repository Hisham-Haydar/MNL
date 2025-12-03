#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Estimate a Box–Cox RURO-style MNL on long (idperson, draw) data.

Dataset: long format from RURO_prep_mnl_basic.py or similar:
    one row per (idperson, draw), with:
      - idperson
      - draw
      - is_chosen (1 for chosen alt, 0 otherwise)
      - consumption (net income / disposable)
      - hours (weekly hours)
      - leisure (optional; if missing, computed as T_HOURS - hours)

Utility specification (baseline, pooled):

    U_ij = beta_c * BC(c_norm_ij; alpha_c)
           + beta_l,ij * BC(l_norm_ij; alpha_l)
           + sum_r gamma_r * region_r,ij

with
    beta_l,ij = beta_l0 + sum_k delta_k * Z_{ik},

where Z_{ik} are individual-level preference shifters (same across j in a given i),
and region_r,ij are alternative-specific region dummies.

Normalisation:

  c_norm_ij = c_ij / c_ref,
  l_norm_ij = l_ij / l_ref,

where c_ref and l_ref are computed from the chosen alternatives:

  - c_ref:
      * default: mean positive chosen consumption
      * --c-ref p99: 99th percentile (p=0.99) of positive chosen consumption

  - l_ref:
      * default: min positive chosen leisure
      * --l-ref mean: mean positive chosen leisure

Box–Cox transform:

    BC(x; alpha) = (x^alpha - 1)/alpha           if alpha != 0
                 = log x                         if alpha -> 0.

Likelihood: MNL over the simulated opportunity set for each individual.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

from path_helpers import reports_root

LOGGER = logging.getLogger(__name__)

T_HOURS: float = 80.0       # total weekly leisure endowment
EPS: float = 1e-8


# ---------------------------------------------------------------------------
# Box–Cox helpers
# ---------------------------------------------------------------------------

def boxcox_transform(x: np.ndarray, alpha: float) -> np.ndarray:
    """Box–Cox transform with smooth limit at alpha→0.

    x is assumed strictly positive; we clip at EPS for safety.
    """
    x = np.clip(x, EPS, None)
    if abs(alpha) < 1e-8:
        return np.log(x)
    return (np.power(x, alpha) - 1.0) / alpha


def d_boxcox_dalpha(x: np.ndarray, alpha: float) -> np.ndarray:
    """Derivative of Box–Cox transform w.r.t. alpha."""
    x = np.clip(x, EPS, None)
    ln_x = np.log(x)
    if abs(alpha) < 1e-8:
        # limit alpha -> 0: 1/2 (ln x)^2
        return 0.5 * ln_x * ln_x
    x_a = np.power(x, alpha)
    num = alpha * x_a * ln_x - (x_a - 1.0)
    den = alpha * alpha
    return num / den


def boxcox_derivative(x: np.ndarray, alpha: float) -> np.ndarray:
    """Derivative of Box–Cox transform w.r.t. its argument x."""
    x = np.clip(x, EPS, None)
    if abs(alpha) < 1e-8:
        return 1.0 / x
    return np.power(x, alpha - 1.0)


# ---------------------------------------------------------------------------
# Data container
# ---------------------------------------------------------------------------

@dataclass
class RuroData:
    n_groups: int
    group_start: np.ndarray      # (G,)
    group_end: np.ndarray        # (G,)
    chosen_index: np.ndarray     # (G,) absolute row indices
    weights: np.ndarray          # (G,)

    cons: np.ndarray             # (M,)
    leis: np.ndarray             # (M,)
    c_norm: np.ndarray           # (M,)
    l_norm: np.ndarray           # (M,)

    y_ref: float                 # consumption reference
    l_ref: float                 # leisure reference
    c_ref_mode: str
    l_ref_mode: str

    # Preference shifters (individual-level, repeated across draws)
    z_per_row: np.ndarray        # (M, K) or (M, 0)
    z_names: List[str]

    # Region dummies (alternative-specific)
    region_mat: np.ndarray       # (M, R) or (M, 0)
    region_names: List[str]


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


# ---------------------------------------------------------------------------
# Data preparation and normalisation
# ---------------------------------------------------------------------------

def build_ruro_data(
    df: pd.DataFrame,
    *,
    id_col: str = "idperson",
    choice_col: str = "is_chosen",
    cons_col: str = "consumption",
    hours_col: Optional[str] = "hours",
    leisure_col: Optional[str] = None,
    weight_col: Optional[str] = None,
    t_hours: float = T_HOURS,
    c_ref_mode: str = "mean",      # "mean" or "p99"
    l_ref_mode: str = "minpos",    # "minpos" or "mean"
    z_cols: Optional[List[str]] = None,
    region_cols: Optional[List[str]] = None,
) -> RuroData:
    """Prepare long RURO data for estimation.

    Assumes df has one row per (id, draw) and exactly one chosen alt per id.

    Normalisation modes:
        c_ref_mode ∈ {"mean", "p99"}
        l_ref_mode ∈ {"minpos", "mean"}
    """

    for col in (id_col, choice_col, cons_col):
        if col not in df.columns:
            raise KeyError(f"Dataset missing required column '{col}'")

    if leisure_col is None and hours_col is None:
        raise ValueError("Either 'hours_col' or 'leisure_col' must be provided.")

    df = df.copy()

    # Ensure numeric types for key columns
    numeric_cols = [cons_col, choice_col]
    if hours_col:
        numeric_cols.append(hours_col)
    if leisure_col:
        numeric_cols.append(leisure_col)
    if weight_col:
        numeric_cols.append(weight_col)

    for col in numeric_cols:
        if col and col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Sort by id and draw to build contiguous groups
    sort_cols = [id_col]
    if "draw" in df.columns:
        sort_cols.append("draw")
    df.sort_values(sort_cols, inplace=True)
    df.reset_index(drop=True, inplace=True)

    ids = df[id_col].to_numpy()
    choice = (df[choice_col] > 0).to_numpy(dtype=bool)
    cons = df[cons_col].to_numpy(dtype=float)

    # Leisure
    if leisure_col and leisure_col in df.columns:
        leis = df[leisure_col].to_numpy(dtype=float)
    else:
        if hours_col not in df.columns:
            raise KeyError(f"hours_col='{hours_col}' not found in dataset.")
        hours = df[hours_col].to_numpy(dtype=float)
        leis = t_hours - hours

    # Group structure
    unique_ids, group_start = np.unique(ids, return_index=True)
    n_groups = unique_ids.size
    group_end = np.empty_like(group_start)
    group_end[:-1] = group_start[1:]
    group_end[-1] = len(df)

    # Chosen alternative index & weights
    chosen_index = np.empty(n_groups, dtype=int)
    weights = np.ones(n_groups, dtype=float)

    for g in range(n_groups):
        s = group_start[g]
        e = group_end[g]
        ch_g = choice[s:e]
        if not np.any(ch_g):
            raise ValueError(f"Group {g} (id={unique_ids[g]}) has no chosen alternative.")
        if np.sum(ch_g) > 1:
            raise ValueError(f"Group {g} (id={unique_ids[g]}) has multiple chosen alternatives.")
        local_idx = np.argmax(ch_g)
        chosen_index[g] = s + local_idx
        if weight_col and weight_col in df.columns:
            w = float(df.iloc[s][weight_col])
            if not np.isfinite(w) or w <= 0:
                w = 1.0
            weights[g] = w

    # --- Preference shifters Z (individual-level) ---
    if z_cols is None:
        z_cols = []
    for z in z_cols:
        if z not in df.columns:
            raise KeyError(f"Requested shifter column '{z}' not found in dataset.")
    if z_cols:
        df[z_cols] = df[z_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        z_per_row = df[z_cols].to_numpy(dtype=float)
    else:
        z_per_row = np.zeros((len(df), 0), dtype=float)

    # --- Region dummies (alternative-specific) ---
    if region_cols is None:
        region_cols = []
    for r in region_cols:
        if r not in df.columns:
            raise KeyError(f"Requested region column '{r}' not found in dataset.")
    if region_cols:
        df[region_cols] = df[region_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        region_mat = df[region_cols].to_numpy(dtype=float)
    else:
        region_mat = np.zeros((len(df), 0), dtype=float)

    # --- Normalisation based on chosen alternatives ---
    cons_chosen = cons[chosen_index]
    leis_chosen = leis[chosen_index]

    cons_pos = cons_chosen[np.isfinite(cons_chosen) & (cons_chosen > 0.0)]
    if cons_pos.size == 0:
        raise ValueError("No positive consumption values among chosen alternatives.")

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
        raise ValueError("No positive leisure values among chosen alternatives.")

    if l_ref_mode == "minpos":
        l_ref = float(leis_pos.min())
    elif l_ref_mode == "mean":
        l_ref = float(leis_pos.mean())
    else:
        raise ValueError("l_ref_mode must be 'minpos' or 'mean'.")

    c_norm = cons / y_ref
    l_norm = leis / l_ref

    if np.any(c_norm <= 0) or np.any(l_norm <= 0):
        LOGGER.warning("Some normalised c or l are non-positive; they will be clipped at EPS in Box–Cox.")

    LOGGER.info("c_ref_mode = %s, y_ref = %.3f", c_ref_mode, y_ref)
    LOGGER.info("l_ref_mode = %s, l_ref = %.3f", l_ref_mode, l_ref)

    return RuroData(
        n_groups=n_groups,
        group_start=group_start,
        group_end=group_end,
        chosen_index=chosen_index,
        weights=weights,
        cons=cons,
        leis=leis,
        c_norm=c_norm,
        l_norm=l_norm,
        y_ref=y_ref,
        l_ref=l_ref,
        c_ref_mode=c_ref_mode,
        l_ref_mode=l_ref_mode,
        z_per_row=z_per_row,
        z_names=list(z_cols),
        region_mat=region_mat,
        region_names=list(region_cols),
    )


# ---------------------------------------------------------------------------
# Likelihood and gradient
# ---------------------------------------------------------------------------

def neg_loglik_and_grad(theta: np.ndarray, data: RuroData) -> Tuple[float, np.ndarray]:
    """Return (negative log-likelihood, gradient) for current parameter vector.

    Parameter vector:
        theta = [alpha_c, alpha_l, beta_c, beta_l0,
                 delta_1, ..., delta_K,
                 gamma_1, ..., gamma_R]
    """
    M = data.c_norm.shape[0]
    K = data.z_per_row.shape[1]
    R = data.region_mat.shape[1]

    expected_len = 4 + K + R
    if len(theta) != expected_len:
        raise ValueError(f"theta length {len(theta)} incompatible with K={K}, R={R} (expected {expected_len}).")

    alpha_c = theta[0]
    alpha_l = theta[1]
    beta_c = theta[2]
    beta_l0 = theta[3]

    if K > 0:
        delta = theta[4:4 + K]
    else:
        delta = np.zeros(0, dtype=float)
    if R > 0:
        gamma = theta[4 + K:]
    else:
        gamma = np.zeros(0, dtype=float)

    # Leisure slope per row (individual-specific)
    if K > 0:
        beta_l_row = beta_l0 + data.z_per_row @ delta
    else:
        beta_l_row = np.full(M, beta_l0, dtype=float)

    # Box–Cox terms
    bc_c = boxcox_transform(data.c_norm, alpha_c)
    bc_l = boxcox_transform(data.l_norm, alpha_l)
    bc_c_dalpha = d_boxcox_dalpha(data.c_norm, alpha_c)
    bc_l_dalpha = d_boxcox_dalpha(data.l_norm, alpha_l)

    # Region term
    if R > 0:
        region_term = data.region_mat @ gamma
    else:
        region_term = np.zeros(M, dtype=float)

    # Utility index
    util = beta_c * bc_c + beta_l_row * bc_l + region_term

    # Derivatives of V_ij w.r.t parameters (row-level)
    dV_dalpha_c_full = beta_c * bc_c_dalpha
    dV_dalpha_l_full = beta_l_row * bc_l_dalpha
    dV_dbeta_c_full = bc_c
    dV_dbeta_l0_full = bc_l

    if K > 0:
        dV_ddelta_full = data.z_per_row * bc_l[:, None]    # (M, K)
    else:
        dV_ddelta_full = np.zeros((M, 0), dtype=float)

    if R > 0:
        dV_dgamma_full = data.region_mat                    # (M, R)
    else:
        dV_dgamma_full = np.zeros((M, 0), dtype=float)

    nll = 0.0
    grad = np.zeros_like(theta)

    G = data.n_groups
    for g in range(G):
        s = data.group_start[g]
        e = data.group_end[g]
        idx = slice(s, e)

        u_g = util[idx]
        u_max = float(np.max(u_g))
        exp_u = np.exp(u_g - u_max)
        denom = float(exp_u.sum())
        if denom <= 0.0 or not np.isfinite(denom):
            return 1e12, np.zeros_like(theta)
        p_g = exp_u / denom

        # Index of chosen alternative within group
        j_star_abs = data.chosen_index[g]
        j_star_loc = j_star_abs - s

        w = data.weights[g]

        p_star = float(p_g[j_star_loc])
        if p_star <= 0.0 or not np.isfinite(p_star):
            return 1e12, np.zeros_like(theta)
        nll -= w * math.log(p_star)

        # Slice derivatives for this group
        dV_dalpha_c = dV_dalpha_c_full[s:e]
        dV_dalpha_l = dV_dalpha_l_full[s:e]
        dV_dbeta_c = dV_dbeta_c_full[s:e]
        dV_dbeta_l0 = dV_dbeta_l0_full[s:e]

        # Expectations
        EV_alpha_c = float(np.dot(p_g, dV_dalpha_c))
        EV_alpha_l = float(np.dot(p_g, dV_dalpha_l))
        EV_beta_c = float(np.dot(p_g, dV_dbeta_c))
        EV_beta_l0 = float(np.dot(p_g, dV_dbeta_l0))

        # Chosen derivatives
        dV_star_alpha_c = float(dV_dalpha_c[j_star_loc])
        dV_star_alpha_l = float(dV_dalpha_l[j_star_loc])
        dV_star_beta_c = float(dV_dbeta_c[j_star_loc])
        dV_star_beta_l0 = float(dV_dbeta_l0[j_star_loc])

        grad[0] -= w * (dV_star_alpha_c - EV_alpha_c)
        grad[1] -= w * (dV_star_alpha_l - EV_alpha_l)
        grad[2] -= w * (dV_star_beta_c - EV_beta_c)
        grad[3] -= w * (dV_star_beta_l0 - EV_beta_l0)

        # Delta_k (preference shifters in leisure slope)
        if K > 0:
            dV_ddelta_g = dV_ddelta_full[s:e, :]    # (J_g, K)
            EV_delta = p_g @ dV_ddelta_g            # (K,)
            dV_star_delta = dV_ddelta_g[j_star_loc, :]  # (K,)
            grad[4:4 + K] -= w * (dV_star_delta - EV_delta)

        # Gamma_r (region dummies)
        if R > 0:
            dV_dgamma_g = dV_dgamma_full[s:e, :]    # (J_g, R)
            EV_gamma = p_g @ dV_dgamma_g            # (R,)
            dV_star_gamma = dV_dgamma_g[j_star_loc, :]  # (R,)
            grad[4 + K:] -= w * (dV_star_gamma - EV_gamma)

    return nll, grad


def neg_loglik(theta: np.ndarray, data: RuroData) -> float:
    nll, _ = neg_loglik_and_grad(theta, data)
    return nll


def grad_neg_loglik(theta: np.ndarray, data: RuroData) -> np.ndarray:
    _, grad = neg_loglik_and_grad(theta, data)
    return grad


# ---------------------------------------------------------------------------
# Estimation and diagnostics
# ---------------------------------------------------------------------------

def approximate_hessian(theta: np.ndarray, data: RuroData, eps: float = 1e-5) -> np.ndarray:
    """Observed Hessian of the *sum* negative log-likelihood via central differences."""
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


def compute_null_loglik(data: RuroData) -> float:
    """Null model with equal probability over each individual's choice set."""
    ll = 0.0
    for g in range(data.n_groups):
        J_g = data.group_end[g] - data.group_start[g]
        if J_g <= 0:
            continue
        w = data.weights[g]
        ll -= w * math.log(J_g)
    return ll


def run_estimation(data: RuroData, output_dir: Path, model_name: str = "ruro_boxcox") -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    K = data.z_per_row.shape[1]
    R = data.region_mat.shape[1]

    # Initial parameters: [alpha_c, alpha_l, beta_c, beta_l0, delta..., gamma...]
    theta0 = np.zeros(4 + K + R, dtype=float)
    theta0[0] = 0.10    # alpha_c
    theta0[1] = 0.10    # alpha_l
    theta0[2] = 1.00    # beta_c
    theta0[3] = 1.00    # beta_l0
    # delta_k and gamma_r initialised at 0

    LOGGER.info("Initial theta (len=%d): %s", len(theta0), theta0)

    result = minimize(
        neg_loglik,
        theta0,
        args=(data,),
        method="L-BFGS-B",
        jac=grad_neg_loglik,
        options={"maxiter": 2000, "disp": True},
    )

    if not result.success:
        LOGGER.warning("Optimiser did not fully converge: %s", result.message)

    theta_hat = result.x
    nll_star, _ = neg_loglik_and_grad(theta_hat, data)
    ll_star = -nll_star
    ll_null = compute_null_loglik(data)

    LOGGER.info("theta_hat = %s", theta_hat)

    k = len(theta_hat)
    rho2 = 1.0 - ll_star / ll_null if ll_null != 0 else float("nan")
    rho2_adj = 1.0 - (ll_star - k) / ll_null if ll_null != 0 else float("nan")

    # Approximate Hessian and standard errors
    H = approximate_hessian(theta_hat, data)
    H = 0.5 * (H + H.T)
    try:
        cov = np.linalg.inv(H)
    except np.linalg.LinAlgError:
        LOGGER.warning("Hessian not invertible; falling back to pseudo-inverse.")
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

    LOGGER.info("Log-likelihood at optimum: %.4f", ll_star)
    LOGGER.info("LL(null): %.4f  rho²=%.4f  rho²_adj=%.4f", ll_null, rho2, rho2_adj)

    # AIC / BIC using number of groups as 'observations'
    n_obs = data.n_groups
    aic = 2 * k - 2 * ll_star
    bic = math.log(n_obs) * k - 2 * ll_star
    LOGGER.info("AIC=%.2f  BIC=%.2f  (n_groups=%d)", aic, bic, n_obs)

    # Assemble parameter names
    names: List[str] = ["alpha_c", "alpha_l", "beta_c", "beta_l0"]
    names.extend([f"delta_{z}" for z in data.z_names])
    names.extend([f"gamma_{r}" for r in data.region_names])

    param_dict = {n: float(v) for n, v in zip(names, theta_hat)}
    se_dict = {n: float(s) for n, s in zip(names, se)}
    t_dict = {n: float(t) if np.isfinite(t) else float("nan") for n, t in zip(names, t_vals)}
    p_dict = {n: float(p) if np.isfinite(p) else float("nan") for n, p in zip(names, p_vals)}

    # Save results to JSON
    meta = {
        "model": model_name,
        "theta_hat": param_dict,
        "se": se_dict,
        "t_values": t_dict,
        "p_values": p_dict,
        "ll_star": float(ll_star),
        "ll_null": float(ll_null),
        "rho2": float(rho2),
        "rho2_adj": float(rho2_adj),
        "aic": float(aic),
        "bic": float(bic),
        "n_groups": int(n_obs),
        "y_ref": float(data.y_ref),
        "l_ref": float(data.l_ref),
        "c_ref_mode": data.c_ref_mode,
        "l_ref_mode": data.l_ref_mode,
        "z_names": data.z_names,
        "region_names": data.region_names,
    }

    out_path = output_dir / f"{model_name}_results.json"
    out_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    LOGGER.info("Saved results to %s", out_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RURO Box–Cox MNL estimation on long data.")
    parser.add_argument(
        "--data-path",
        type=Path,
        required=True,
        help="Path to RURO MNL long dataset (e.g. fr_2021_RURO_mnl.parquet).",
    )
    parser.add_argument("--id-col", default="idperson", help="Individual identifier column (default: idperson).")
    parser.add_argument("--choice-col", default="is_chosen", help="Choice indicator column (1=chosen, 0=otherwise).")
    parser.add_argument("--cons-col", default="consumption", help="Consumption / net income column name.")
    parser.add_argument("--hours-col", default="hours", help="Hours worked column name (if leisure not provided).")
    parser.add_argument("--leisure-col", default=None, help="Leisure column name (optional, overrides hours).")
    parser.add_argument("--weight-col", default=None, help="Sampling weight column (optional).")
    parser.add_argument("--t-hours", type=float, default=T_HOURS, help="Total time endowment for leisure (default 80).")

    parser.add_argument(
        "--c-ref",
        choices=("mean", "p99"),
        default="mean",
        help="Reference for consumption normalisation: mean (default) or 99th percentile of chosen consumption.",
    )
    parser.add_argument(
        "--l-ref",
        choices=("minpos", "mean"),
        default="minpos",
        help="Reference for leisure normalisation: min positive chosen leisure (default) or mean chosen leisure.",
    )

    parser.add_argument(
        "--z-cols",
        nargs="*",
        default=None,
        help="Columns used as individual-level preference shifters in the leisure slope (beta_l).",
    )
    parser.add_argument(
        "--region-cols",
        nargs="*",
        default=None,
        help=(
            "Columns used as alternative-specific region dummies in utility. "
            "Omit the base region (e.g. Ile-de-France FR10) so it becomes the reference."
        ),
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=reports_root() / "mle_ruro" / "boxcox",
        help="Directory to store estimation outputs.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Logging verbosity.",
    )
    parser.add_argument("--model-name", default="ruro_boxcox", help="Base name for output files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format="%(message)s")

    df = _read_dataframe(args.data_path)
    LOGGER.info("Loaded dataset %s with %d rows and %d columns.", args.data_path, len(df), df.shape[1])

    data = build_ruro_data(
        df,
        id_col=args.id_col,
        choice_col=args.choice_col,
        cons_col=args.cons_col,
        hours_col=args.hours_col,
        leisure_col=args.leisure_col,
        weight_col=args.weight_col,
        t_hours=args.t_hours,
        c_ref_mode=args.c_ref,
        l_ref_mode=args.l_ref,
        z_cols=args.z_cols,
        region_cols=args.region_cols,
    )

    run_estimation(data, args.output_dir, model_name=args.model_name)


if __name__ == "__main__":
    main()
