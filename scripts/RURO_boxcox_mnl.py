#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Estimate a simple Box–Cox RURO-style MNL on long (id, draw) data.

This script is designed for the RURO_MNL long dataset produced by
`RURO_prep_mnl_basic.py`. It expects one row per individual–alternative
(draw), with a binary choice indicator.

Utility specification (pooled, no covariates for now):

    U_ij = beta_c * BC(c_norm_ij; alpha_c) + beta_l * BC(l_norm_ij; alpha_l),

where
    c_norm_ij = c_ij / mean(c_i*),
    l_norm_ij = l_ij / min_{i} { l_i* > 0 },

c_ij  = consumption of alternative j for individual i,
l_ij  = leisure of alternative j for individual i.

Here c_i* and l_i* denote the consumption and leisure of the chosen
alternative for individual i. The Box–Cox transform is

    BC(x; alpha) = (x^alpha - 1)/alpha                    if alpha != 0
                 = log x                                  if alpha -> 0.

The likelihood is the usual MNL likelihood over the simulated opportunity
set for each individual (observed job + simulated jobs).
"""

from __future__ import annotations

import argparse
import json
import logging
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

from path_helpers import reports_root

LOGGER = logging.getLogger(__name__)

T_HOURS: float = 80.0      # total weekly leisure endowment
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
    group_start: np.ndarray    # shape (G,)
    group_end: np.ndarray      # shape (G,)
    chosen_index: np.ndarray   # shape (G,) absolute row indices
    weights: np.ndarray        # shape (G,)
    cons: np.ndarray           # shape (M,)
    leis: np.ndarray           # shape (M,)
    c_norm: np.ndarray         # shape (M,)
    l_norm: np.ndarray         # shape (M,)
    y_ref: float
    l_min_pos: float


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


def build_ruro_data(
    df: pd.DataFrame,
    *,
    id_col: str = "idperson",
    choice_col: str = "is_chosen",
    cons_col: str = "consumption",
    hours_col: str | None = "hours",
    leisure_col: str | None = None,
    weight_col: str | None = None,
    t_hours: float = T_HOURS,
) -> RuroData:
    """Prepare long RURO data for estimation.

    Assumes df has one row per (id, draw) and exactly one chosen alt per id.
    """
    for col in (id_col, choice_col, cons_col):
        if col not in df.columns:
            raise KeyError(f"Dataset missing required column '{col}'")

    if leisure_col is None and hours_col is None:
        raise ValueError("Either 'hours_col' or 'leisure_col' must be provided.")

    df = df.copy()

    # Ensure numeric types
    for col in [cons_col, choice_col] + ([hours_col] if hours_col else []) + ([leisure_col] if leisure_col else []):
        if col and col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if weight_col and weight_col in df.columns:
        df[weight_col] = pd.to_numeric(df[weight_col], errors="coerce").fillna(1.0)
    else:
        weight_col = None

    # Sort by id (and draw if present) to make groups contiguous
    sort_cols = [id_col]
    if "draw" in df.columns:
        sort_cols.append("draw")
    df.sort_values(sort_cols, inplace=True)
    df.reset_index(drop=True, inplace=True)

    ids = df[id_col].to_numpy()
    choice = (df[choice_col] > 0).to_numpy(dtype=bool)
    cons = df[cons_col].to_numpy(dtype=float)

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

    # Chosen index per group
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
        if weight_col:
            # take weight from chosen row; any row in group should be identical
            w = float(df.iloc[s][weight_col])
            if not np.isfinite(w) or w <= 0:
                w = 1.0
            weights[g] = w

    # Normalisations based on chosen alternatives
    cons_chosen = cons[chosen_index]
    leis_chosen = leis[chosen_index]

    cons_pos = cons_chosen[np.isfinite(cons_chosen) & (cons_chosen > 0.0)]
    if cons_pos.size == 0:
        raise ValueError("No positive consumption values among chosen alternatives.")
    y_ref = float(cons_pos.mean())

    leis_pos = leis_chosen[np.isfinite(leis_chosen) & (leis_chosen > 0.0)]
    if leis_pos.size == 0:
        raise ValueError("No positive leisure values among chosen alternatives.")
    l_min_pos = float(leis_pos.min())

    c_norm = cons / y_ref
    l_norm = leis / l_min_pos

    if np.any(c_norm <= 0) or np.any(l_norm <= 0):
        LOGGER.warning("Some normalised c or l are non-positive; they will be clipped at EPS in Box–Cox.")

    LOGGER.info("y_ref (mean chosen consumption) = %.3f", y_ref)
    LOGGER.info("l_min_pos (min positive chosen leisure) = %.3f", l_min_pos)

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
        l_min_pos=l_min_pos,
    )


# ---------------------------------------------------------------------------
# Likelihood and gradient
# ---------------------------------------------------------------------------

def neg_loglik_and_grad(theta: np.ndarray, data: RuroData) -> Tuple[float, np.ndarray]:
    """Return (negative log-likelihood, gradient) for current parameter vector.

    theta = [alpha_c, alpha_l, beta_c, beta_l]
    """
    alpha_c, alpha_l, beta_c, beta_l = theta
    M = data.c_norm.shape[0]
    G = data.n_groups

    # Box–Cox terms for all rows at once
    bc_c = boxcox_transform(data.c_norm, alpha_c)          # shape (M,)
    bc_l = boxcox_transform(data.l_norm, alpha_l)          # shape (M,)
    bc_c_dalpha = d_boxcox_dalpha(data.c_norm, alpha_c)
    bc_l_dalpha = d_boxcox_dalpha(data.l_norm, alpha_l)

    # Utilities
    util = beta_c * bc_c + beta_l * bc_l                   # shape (M,)

    nll = 0.0
    grad = np.zeros(4, dtype=float)   # [alpha_c, alpha_l, beta_c, beta_l]

    for g in range(G):
        s = data.group_start[g]
        e = data.group_end[g]
        idx = slice(s, e)

        u_g = util[idx]
        bc_c_g = bc_c[idx]
        bc_l_g = bc_l[idx]
        bc_c_da_g = bc_c_dalpha[idx]
        bc_l_da_g = bc_l_dalpha[idx]

        # stabilised softmax
        u_max = float(np.max(u_g))
        exp_u = np.exp(u_g - u_max)
        denom = float(exp_u.sum())
        if denom <= 0.0 or not np.isfinite(denom):
            return 1e12, np.zeros_like(grad)
        p_g = exp_u / denom

        # locate chosen alternative within group
        j_star_abs = data.chosen_index[g]
        j_star_loc = j_star_abs - s

        w = data.weights[g]

        # contribution to log-likelihood
        p_star = float(p_g[j_star_loc])
        if p_star <= 0.0 or not np.isfinite(p_star):
            return 1e12, np.zeros_like(grad)
        nll -= w * math.log(p_star)

        # derivatives of utility for each alternative in group
        dV_dalpha_c = beta_c * bc_c_da_g
        dV_dalpha_l = beta_l * bc_l_da_g
        dV_dbeta_c = bc_c_g
        dV_dbeta_l = bc_l_g

        # expected derivatives under choice probabilities
        EV_alpha_c = float(np.dot(p_g, dV_dalpha_c))
        EV_alpha_l = float(np.dot(p_g, dV_dalpha_l))
        EV_beta_c = float(np.dot(p_g, dV_dbeta_c))
        EV_beta_l = float(np.dot(p_g, dV_dbeta_l))

        # chosen derivatives
        dV_star_alpha_c = float(dV_dalpha_c[j_star_loc])
        dV_star_alpha_l = float(dV_dalpha_l[j_star_loc])
        dV_star_beta_c = float(dV_dbeta_c[j_star_loc])
        dV_star_beta_l = float(dV_dbeta_l[j_star_loc])

        grad[0] -= w * (dV_star_alpha_c - EV_alpha_c)
        grad[1] -= w * (dV_star_alpha_l - EV_alpha_l)
        grad[2] -= w * (dV_star_beta_c - EV_beta_c)
        grad[3] -= w * (dV_star_beta_l - EV_beta_l)

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

    # Initial parameters: [alpha_c, alpha_l, beta_c, beta_l]
    theta0 = np.array([0.10, 0.10, 1.0, 1.0], dtype=float)

    LOGGER.info("Initial theta: %s", theta0)

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
    nll_star = neg_loglik(theta_hat, data)
    ll_star = -nll_star
    ll_null = compute_null_loglik(data)

    alpha_c, alpha_l, beta_c, beta_l = theta_hat
    LOGGER.info(
        "theta_hat = [alpha_c=%.4f, alpha_l=%.4f, beta_c=%.4f, beta_l=%.4f]",
        alpha_c, alpha_l, beta_c, beta_l,
    )

    # Diagnostics
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

    se = np.sqrt(np.maximum(np.diag(cov), 0.0))
    t_vals = theta_hat / se
    p_vals = 2.0 * (1.0 - norm.cdf(np.abs(t_vals)))

    # Print summary to log
    names = ["alpha_c", "alpha_l", "beta_c", "beta_l"]
    LOGGER.info("Log-likelihood at optimum: %.4f", ll_star)
    LOGGER.info("LL(null): %.4f  rho²=%.4f  rho²_adj=%.4f", ll_null, rho2, rho2_adj)
    LOGGER.info("Parameter estimates:")
    for name, val, s, t, p in zip(names, theta_hat, se, t_vals, p_vals):
        LOGGER.info("  %-8s  %10.6f  (se=%10.6f, t=%8.3f, p=%6.4f)", name, val, s, t, p)

    # Save to JSON
    meta = {
        "model": model_name,
        "theta_hat": {n: float(v) for n, v in zip(names, theta_hat)},
        "se": {n: float(s) for n, s in zip(names, se)},
        "t_values": {n: float(t) for n, t in zip(names, t_vals)},
        "p_values": {n: float(p) for n, p in zip(names, p_vals)},
        "ll_star": float(ll_star),
        "ll_null": float(ll_null),
        "rho2": float(rho2),
        "rho2_adj": float(rho2_adj),
        "y_ref": float(data.y_ref),
        "l_min_pos": float(data.l_min_pos),
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
    )

    run_estimation(data, args.output_dir, model_name=args.model_name)


if __name__ == "__main__":
    main()
