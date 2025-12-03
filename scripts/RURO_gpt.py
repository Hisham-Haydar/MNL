#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RURO Box–Cox MNL with group-specific preferences and opportunity functions.

One row per (idperson, draw, job alternative).

Preferences:
    For individual i in group g(i) ∈ {single_m, single_f, couple_m, couple_f}
    and alternative j:

        U_ij^pref =
            beta_c[g(i)] * BC(c_norm_ij; alpha_c)
          + beta_l_i    * BC(l_norm_ij; alpha_l),

    where:
        beta_l_i = beta_l0[g(i)] + sum_k delta_k * Z_{ik},

    Z_{ik} are individual-level shifters (same across j for given i),
    provided via --z-cols.

Opportunities:
    Hours h_ij, wage w_ij, occupation loc_ij, region r(i):

    1) Mass at zero hours:
        η_i = kappa0[g(i)] + lambda_r(i)
        π0_i = logistic(η_i) = P(h = 0 | i)

       For each alternative j of i:
         if h_ij = 0:  log f_ij = log π0_i
         if h_ij > 0:  log f_ij = log(1 - π0_i) + g(h_ij, w_ij, loc_ij)

    2) Positive-hours density (for h_ij > 0):
        h_tilde_ij = h_ij / T_HOURS
        logw_ij = log w_ij

        g(h_ij, w_ij, loc_ij) =
            theta_h1 * h_tilde_ij
          + theta_h2 * h_tilde_ij^2
          + theta_w1 * logw_ij
          + theta_w2 * logw_ij^2
          + psi_loc( loc_ij ),

       where psi_loc(baseline_loc) = 0, others are parameters.

Total systematic utility in the MNL:
    V_ij = U_ij^pref + log f_ij^opp.

Choice model:
    Conditional on the simulated opportunity set for i,
    choice follows MNL:

        P_ij = exp(V_ij) / sum_k exp(V_ik).

Likelihood:
    Sum over individuals of weights_i * log P_{i, chosen}.

Normalisation:
    - c_norm_ij = c_ij / y_ref
    - l_norm_ij = l_ij / l_ref

      y_ref:
        * --c-ref mean (default): mean positive consumption at chosen jobs
        * --c-ref p99           : 99th percentile of positive chosen consumption

      l_ref:
        * --l-ref minpos (default): min positive leisure at chosen jobs
        * --l-ref mean             : mean positive leisure at chosen jobs

Groups g(i):
    Constructed from (ruro_group, dgn):

    - ruro_group == 1  and dgn == 0 -> single_m
    - ruro_group == 1  and dgn == 1 -> single_f
    - ruro_group == 10 and dgn == 0 -> couple_m
    - ruro_group == 10 and dgn == 1 -> couple_f

Adjust mapping if your dgn coding differs (see build_ruro_data()).
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

T_HOURS_DEFAULT: float = 80.0
EPS: float = 1e-8


# ---------------------------------------------------------------------------
# Box–Cox helpers
# ---------------------------------------------------------------------------

def boxcox_transform(x: np.ndarray, alpha: float) -> np.ndarray:
    """Box–Cox transform with smooth limit at alpha→0."""
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
    # group (individual) structure
    n_groups: int
    group_start: np.ndarray      # (G,)
    group_end: np.ndarray        # (G,)
    chosen_index: np.ndarray     # (G,) absolute row index of chosen alternative
    weights: np.ndarray          # (G,)

    # row-level arrays (M rows)
    cons: np.ndarray             # (M,)
    leis: np.ndarray             # (M,)
    hours: np.ndarray            # (M,)
    wage: np.ndarray             # (M,)
    c_norm: np.ndarray           # (M,)
    l_norm: np.ndarray           # (M,)

    # per-row group id (0..3) and loc index
    row_group_ids: np.ndarray    # (M,) values 0..3
    loc_index: np.ndarray        # (M,) values 0..L-1

    # group-level tags
    group_ids: np.ndarray        # (G,) values 0..3
    group_names: List[str]       # length 4
    region_index: np.ndarray     # (G,) values 0..R-1

    # labels
    region_labels: List[str]     # [0] is baseline region
    loc_labels: List[str]        # [0] is baseline loc (by design)
    loc_baseline_label: str

    # preference shifters (individual-level, repeated in rows)
    z_per_row: np.ndarray        # (M, K) or (M, 0)
    z_names: List[str]

    # normalisation meta
    y_ref: float
    l_ref: float
    c_ref_mode: str
    l_ref_mode: str

    # time endowment
    t_hours: float


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
        # assume tab-separated if txt
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
    wage_col: str = "wage",
    loc_col: str = "loc",
    region_col: str = "drgn1",
    weight_col: Optional[str] = None,
    t_hours: float = T_HOURS_DEFAULT,
    c_ref_mode: str = "mean",      # "mean" or "p99"
    l_ref_mode: str = "minpos",    # "minpos" or "mean"
    z_cols: Optional[List[str]] = None,
) -> RuroData:
    """
    Prepare long RURO data for estimation:

        - One row per (id, draw, alternative).
        - Exactly one chosen alternative per individual.
        - 4 preference/opportunity groups from (ruro_group, dgn).
        - Region categories from region_col (e.g. drgn1).
        - LOC categories from loc_col (baseline loc chosen as 0 if present, else modal LOC).
    """

    # Required columns
    required = [id_col, choice_col, cons_col, region_col, wage_col, loc_col, "ruro_group", "dgn"]
    if leisure_col is None and hours_col is None:
        raise ValueError("Either 'hours_col' or 'leisure_col' must be provided.")
    if hours_col is not None:
        required.append(hours_col)
    if leisure_col is not None:
        required.append(leisure_col)
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Dataset missing required columns: {missing}")

    df = df.copy()

    # Numeric conversion
    num_cols = [cons_col, choice_col, wage_col]
    if hours_col:
        num_cols.append(hours_col)
    if leisure_col:
        num_cols.append(leisure_col)
    if weight_col:
        num_cols.append(weight_col)
    num_cols.extend(["ruro_group", "dgn"])
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Sort by id and draw for stability
    sort_cols = [id_col]
    if "draw" in df.columns:
        sort_cols.append("draw")
    df.sort_values(sort_cols, inplace=True)
    df.reset_index(drop=True, inplace=True)

    ids = df[id_col].to_numpy()
    choice = (df[choice_col] > 0).to_numpy(dtype=bool)
    cons = df[cons_col].to_numpy(dtype=float)

    # Leisure and hours
    if leisure_col and leisure_col in df.columns:
        leis = df[leisure_col].to_numpy(dtype=float)
        if hours_col and hours_col in df.columns:
            hours = df[hours_col].to_numpy(dtype=float)
        else:
            hours = t_hours - leis
    else:
        if hours_col not in df.columns:
            raise KeyError(f"hours_col='{hours_col}' not found in dataset.")
        hours = df[hours_col].to_numpy(dtype=float)
        leis = t_hours - hours

    # Wages
    wage = df[wage_col].to_numpy(dtype=float)
    # clip to positive for safety in logs later
    wage = np.clip(wage, EPS, None)

    # LOC raw
    loc_raw = df[loc_col].to_numpy()

    # Group (person) structure
    unique_ids, group_start = np.unique(ids, return_index=True)
    n_groups = unique_ids.size
    group_end = np.empty_like(group_start)
    group_end[:-1] = group_start[1:]
    group_end[-1] = len(df)

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

    # Preference shifters Z
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

    # Normalisation based on chosen alts
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

    # ----------------------------------------------------------------------
    # 4 preference/opportunity groups from ruro_group & dgn
    # Convention used here (adjust if your coding differs):
    #   ruro_group == 1  and dgn == 0 -> single_m
    #   ruro_group == 1  and dgn == 1 -> single_f
    #   ruro_group == 10 and dgn == 0 -> couple_m
    #   ruro_group == 10 and dgn == 1 -> couple_f
    # ----------------------------------------------------------------------
    ruro_group = pd.to_numeric(df["ruro_group"], errors="coerce").fillna(0).to_numpy(dtype=int)
    dgn = pd.to_numeric(df["dgn"], errors="coerce").fillna(0).to_numpy(dtype=int)

    group_names = ["single_m", "single_f", "couple_m", "couple_f"]

    def _group_id(rg: int, sex: int) -> int:
        if rg == 1 and sex == 0:
            return 0  # single_m
        if rg == 1 and sex == 1:
            return 1  # single_f
        if rg == 10 and sex == 0:
            return 2  # couple_m
        if rg == 10 and sex == 1:
            return 3  # couple_f
        raise ValueError(f"Unexpected (ruro_group, dgn)=({rg},{sex}) when building 4 groups.")

    group_ids = np.empty(n_groups, dtype=int)
    for g in range(n_groups):
        s = group_start[g]
        rg = int(ruro_group[s])
        sex = int(dgn[s])
        group_ids[g] = _group_id(rg, sex)

    # per-row group ids
    row_group_ids = np.empty(len(df), dtype=int)
    for g in range(n_groups):
        s = group_start[g]
        e = group_end[g]
        row_group_ids[s:e] = group_ids[g]

    # Regions
    region_series = df[region_col]
    if region_series.isna().all():
        raise ValueError(f"All values of region column '{region_col}' are missing.")
    region_labels_unique = pd.unique(region_series.dropna())
    region_labels_sorted = sorted(region_labels_unique.tolist())
    region_labels = [str(lab) for lab in region_labels_sorted]
    R_types = len(region_labels)
    region_label_to_index = {lab: idx for idx, lab in enumerate(region_labels)}

    region_index = np.empty(n_groups, dtype=int)
    for g in range(n_groups):
        s = group_start[g]
        reg_val = region_series.iloc[s]
        if pd.isna(reg_val):
            raise ValueError(f"Missing {region_col} for id {unique_ids[g]} at group start.")
        region_index[g] = region_label_to_index[str(reg_val)]

    # LOC categories
    loc_series = pd.Series(loc_raw)
    unique_loc_vals = pd.unique(loc_series.dropna())
    if unique_loc_vals.size == 0:
        raise ValueError(f"No non-missing values found in loc column '{loc_col}'.")

    # baseline: loc==0 if present, else modal loc
    if 0 in unique_loc_vals:
        baseline_loc_label = 0
    else:
        vc = loc_series.dropna().value_counts()
        baseline_loc_label = vc.idxmax()

    other_loc_labels = sorted([val for val in unique_loc_vals if val != baseline_loc_label])
    loc_labels = [baseline_loc_label] + other_loc_labels
    loc_labels_str = [str(lab) for lab in loc_labels]
    loc_label_to_index = {lab: idx for idx, lab in enumerate(loc_labels)}

    loc_index = np.empty(len(df), dtype=int)
    for i in range(len(df)):
        val = loc_raw[i]
        if pd.isna(val):
            raise ValueError(f"Missing loc value at row {i}")
        loc_index[i] = loc_label_to_index[val]

    return RuroData(
        n_groups=n_groups,
        group_start=group_start,
        group_end=group_end,
        chosen_index=chosen_index,
        weights=weights,
        cons=cons,
        leis=leis,
        hours=hours,
        wage=wage,
        c_norm=c_norm,
        l_norm=l_norm,
        row_group_ids=row_group_ids,
        loc_index=loc_index,
        group_ids=group_ids,
        group_names=group_names,
        region_index=region_index,
        region_labels=region_labels_str,
        loc_labels=loc_labels_str,
        loc_baseline_label=str(baseline_loc_label),
        z_per_row=z_per_row,
        z_names=list(z_cols),
        y_ref=y_ref,
        l_ref=l_ref,
        c_ref_mode=c_ref_mode,
        l_ref_mode=l_ref_mode,
        t_hours=float(t_hours),
    )


# ---------------------------------------------------------------------------
# Likelihood and gradient
# ---------------------------------------------------------------------------

def neg_loglik_and_grad(theta: np.ndarray, data: RuroData) -> Tuple[float, np.ndarray]:
    """
    Return (negative log-likelihood, gradient) for current parameter vector.

    Parameter vector layout:

        theta = [
            alpha_c, alpha_l,                                          (2)
            beta_c[g=0..3],                                            (4)
            beta_l0[g=0..3],                                           (4)
            delta_k (k=0..K-1),                                        (K)
            kappa0[g=0..3],                                            (4)
            lambda_r (r=1..R-1),                                       (R-1)  baseline r=0
            theta_h1, theta_h2, theta_w1, theta_w2,                    (4)
            psi_loc for non-baseline locs (L-1),                       (L-1)
        ]
    """
    M = data.c_norm.shape[0]
    K = data.z_per_row.shape[1]
    G_types = len(data.group_names)    # should be 4
    R_types = len(data.region_labels)
    L_types = len(data.loc_labels)

    # index bookkeeping
    idx_alpha_c = 0
    idx_alpha_l = 1
    idx_beta_c_start = 2
    idx_beta_l0_start = idx_beta_c_start + G_types          # 6
    idx_delta_start = idx_beta_l0_start + G_types           # 10
    idx_kappa0_start = idx_delta_start + K
    idx_lambda_start = idx_kappa0_start + G_types
    idx_theta_start = idx_lambda_start + max(R_types - 1, 0)
    idx_psi_start = idx_theta_start + 4
    expected_len = idx_psi_start + max(L_types - 1, 0)

    if len(theta) != expected_len:
        raise ValueError(
            f"theta length {len(theta)} incompatible with "
            f"K={K}, G={G_types}, R={R_types}, L={L_types} (expected {expected_len})."
        )

    alpha_c = theta[idx_alpha_c]
    alpha_l = theta[idx_alpha_l]

    beta_c_vec = theta[idx_beta_c_start: idx_beta_c_start + G_types]           # (4,)
    beta_l0_vec = theta[idx_beta_l0_start: idx_beta_l0_start + G_types]       # (4,)

    if K > 0:
        delta_vec = theta[idx_delta_start: idx_delta_start + K]               # (K,)
    else:
        delta_vec = np.zeros(0, dtype=float)

    kappa0_vec = theta[idx_kappa0_start: idx_kappa0_start + G_types]          # (4,)

    if R_types > 1:
        lambda_vec = theta[idx_lambda_start: idx_lambda_start + (R_types - 1)]
    else:
        lambda_vec = np.zeros(0, dtype=float)

    theta_h1, theta_h2, theta_w1, theta_w2 = theta[idx_theta_start: idx_theta_start + 4]

    if L_types > 1:
        psi_vec = theta[idx_psi_start: idx_psi_start + (L_types - 1)]         # (L-1,)
    else:
        psi_vec = np.zeros(0, dtype=float)

    # full psi vector with baseline loc having psi=0
    psi_full = np.zeros(L_types, dtype=float)
    if L_types > 1:
        psi_full[1:] = psi_vec

    # Box–Cox terms for all rows
    bc_c = boxcox_transform(data.c_norm, alpha_c)
    bc_l = boxcox_transform(data.l_norm, alpha_l)
    bc_c_dalpha = d_boxcox_dalpha(data.c_norm, alpha_c)
    bc_l_dalpha = d_boxcox_dalpha(data.l_norm, alpha_l)

    # group-specific beta_c per row
    beta_c_row = beta_c_vec[data.row_group_ids]  # (M,)

    # beta_l_row = beta_l0[group] + delta · Z
    beta_l_row = np.zeros(M, dtype=float)
    if K > 0:
        z_times_delta = data.z_per_row @ delta_vec  # (M,)
    else:
        z_times_delta = np.zeros(M, dtype=float)

    for g_type in range(G_types):
        mask = (data.row_group_ids == g_type)
        if np.any(mask):
            beta_l_row[mask] = beta_l0_vec[g_type] + z_times_delta[mask]

    # preference utility for all rows
    util_pref = beta_c_row * bc_c + beta_l_row * bc_l

    # derivatives of preference part w.r.t Box–Cox alphas
    dV_dalpha_c_full = beta_c_row * bc_c_dalpha
    dV_dalpha_l_full = beta_l_row * bc_l_dalpha

    # for deltas: dV/d delta_k = Z_k * BC(l)
    if K > 0:
        dV_ddelta_full = data.z_per_row * bc_l[:, None]      # (M, K)
    else:
        dV_ddelta_full = np.zeros((M, 0), dtype=float)

    # hours & wage (opp part)
    hours_all = data.hours
    wage_all = data.wage
    loc_index_all = data.loc_index

    nll = 0.0
    grad = np.zeros_like(theta)

    G = data.n_groups
    for g_idx in range(G):
        s = data.group_start[g_idx]
        e = data.group_end[g_idx]
        idx = slice(s, e)

        g_type = int(data.group_ids[g_idx])         # 0..3
        reg_idx = int(data.region_index[g_idx])     # 0..R_types-1
        w_i = data.weights[g_idx]

        # slice row-level arrays
        u_pref_g = util_pref[idx]
        dV_dalpha_c = dV_dalpha_c_full[idx]
        dV_dalpha_l = dV_dalpha_l_full[idx]
        bc_c_g = bc_c[idx]
        bc_l_g = bc_l[idx]
        beta_c_g_row = beta_c_row[idx]
        beta_l_g_row = beta_l_row[idx]

        hours_g = hours_all[idx]
        wage_g = wage_all[idx]
        loc_idx_g = loc_index_all[idx]

        # zero vs positive hours
        is_zero = hours_g <= 0.0
        is_pos = ~is_zero

        # π0_i via logit
        eta_i = float(kappa0_vec[g_type])
        if R_types > 1 and reg_idx > 0:
            eta_i += float(lambda_vec[reg_idx - 1])

        # numerically stable logistic
        if eta_i >= 0:
            exp_minus_eta = math.exp(-eta_i)
            pi0_i = 1.0 / (1.0 + exp_minus_eta)
        else:
            exp_eta = math.exp(eta_i)
            pi0_i = exp_eta / (1.0 + exp_eta)

        pi0_i = min(max(pi0_i, EPS), 1.0 - EPS)

        log_prior_g = np.empty(e - s, dtype=float)
        log_pi0 = math.log(pi0_i)
        log_1m = math.log(1.0 - pi0_i)
        log_prior_g[is_zero] = log_pi0
        log_prior_g[is_pos] = log_1m

        # parametric opportunity density g(h,w,loc) for positive jobs
        g_opp_g = np.zeros(e - s, dtype=float)
        if np.any(is_pos):
            h_tilde = hours_g[is_pos] / data.t_hours
            h_sq = h_tilde * h_tilde
            logw = np.log(np.clip(wage_g[is_pos], EPS, None))
            logw_sq = logw * logw
            loc_pos = loc_idx_g[is_pos]

            g_opp_pos = (
                theta_h1 * h_tilde
                + theta_h2 * h_sq
                + theta_w1 * logw
                + theta_w2 * logw_sq
            )
            # add psi_loc
            g_opp_pos += psi_full[loc_pos]
            g_opp_g[is_pos] = g_opp_pos
            # for zero hours, g_opp_g stays at 0

        # opportunity log-density
        log_f_g = log_prior_g.copy()
        log_f_g[is_pos] += g_opp_g[is_pos]

        # total utility
        u_g = u_pref_g + log_f_g

        # MNL probabilities for this individual
        u_max = float(np.max(u_g))
        exp_u = np.exp(u_g - u_max)
        denom = float(exp_u.sum())
        if denom <= 0.0 or not np.isfinite(denom):
            return 1e12, np.zeros_like(theta)
        p_g = exp_u / denom

        # index of chosen alternative
        j_star_abs = data.chosen_index[g_idx]
        j_star_loc = j_star_abs - s

        p_star = float(p_g[j_star_loc])
        if p_star <= 0.0 or not np.isfinite(p_star):
            return 1e12, np.zeros_like(theta)
        nll -= w_i * math.log(p_star)

        # --------------------------------------------------------------
        # Gradient contributions (score identity)
        # For each parameter θ:
        #   ∂ℓ/∂θ = Σ_i w_i [ ∂V_{i j*}/∂θ - Σ_j P_ij ∂V_ij/∂θ ].
        # --------------------------------------------------------------

        # dlog f / dη_i (mass part)
        dlogf_deta = np.zeros(e - s, dtype=float)
        dlogf_deta[is_zero] = 1.0 - pi0_i
        dlogf_deta[is_pos] = -pi0_i

        # ---- alpha_c ----
        EV_alpha_c = float(np.dot(p_g, dV_dalpha_c))
        dV_star_alpha_c = float(dV_dalpha_c[j_star_loc])
        grad[idx_alpha_c] -= w_i * (dV_star_alpha_c - EV_alpha_c)

        # ---- alpha_l ----
        EV_alpha_l = float(np.dot(p_g, dV_dalpha_l))
        dV_star_alpha_l = float(dV_dalpha_l[j_star_loc])
        grad[idx_alpha_l] -= w_i * (dV_star_alpha_l - EV_alpha_l)

        # ---- beta_c[g_type] ----
        # derivative is BC(c_norm) for this individual's rows
        EV_beta_c = float(np.dot(p_g, bc_c_g))
        dV_star_beta_c = float(bc_c_g[j_star_loc])
        grad[idx_beta_c_start + g_type] -= w_i * (dV_star_beta_c - EV_beta_c)

        # ---- beta_l0[g_type] ----
        EV_beta_l0 = float(np.dot(p_g, bc_l_g))
        dV_star_beta_l0 = float(bc_l_g[j_star_loc])
        grad[idx_beta_l0_start + g_type] -= w_i * (dV_star_beta_l0 - EV_beta_l0)

        # ---- delta_k ----
        if K > 0:
            dV_ddelta_g = dV_ddelta_full[idx, :]  # (J_g, K)
            EV_delta = p_g @ dV_ddelta_g          # (K,)
            dV_star_delta = dV_ddelta_g[j_star_loc, :]  # (K,)
            grad[idx_delta_start: idx_delta_start + K] -= w_i * (dV_star_delta - EV_delta)

        # ---- kappa0[g_type] (mass at zero) ----
        EV_eta = float(np.dot(p_g, dlogf_deta))
        dV_star_eta = float(dlogf_deta[j_star_loc])
        grad[idx_kappa0_start + g_type] -= w_i * (dV_star_eta - EV_eta)

        # ---- lambda_region_r (if non-baseline) ----
        if R_types > 1 and reg_idx > 0:
            lambda_idx = idx_lambda_start + (reg_idx - 1)
            grad[lambda_idx] -= w_i * (dV_star_eta - EV_eta)

        # ---- theta_h1, theta_h2, theta_w1, theta_w2 ----
        # Build derivative vectors (J_g) with zeros for h=0
        dV_dtheta_h1 = np.zeros(e - s, dtype=float)
        dV_dtheta_h2 = np.zeros(e - s, dtype=float)
        dV_dtheta_w1 = np.zeros(e - s, dtype=float)
        dV_dtheta_w2 = np.zeros(e - s, dtype=float)
        if np.any(is_pos):
            h_tilde = hours_g[is_pos] / data.t_hours
            h_sq = h_tilde * h_tilde
            logw = np.log(np.clip(wage_g[is_pos], EPS, None))
            logw_sq = logw * logw
            dV_dtheta_h1[is_pos] = h_tilde
            dV_dtheta_h2[is_pos] = h_sq
            dV_dtheta_w1[is_pos] = logw
            dV_dtheta_w2[is_pos] = logw_sq

        for offset, dV_dtheta in enumerate(
            [dV_dtheta_h1, dV_dtheta_h2, dV_dtheta_w1, dV_dtheta_w2]
        ):
            EV_theta = float(np.dot(p_g, dV_dtheta))
            dV_star_theta = float(dV_dtheta[j_star_loc])
            grad[idx_theta_start + offset] -= w_i * (dV_star_theta - EV_theta)

        # ---- psi_loc parameters (non-baseline LOCs) ----
        # derivative is 1 for rows with given loc and h>0, else 0
        if L_types > 1:
            for loc_idx_param in range(1, L_types):
                param_pos = idx_psi_start + (loc_idx_param - 1)
                mask_loc = (loc_idx_g == loc_idx_param) & is_pos
                if not np.any(mask_loc):
                    continue
                dV_dpsi = mask_loc.astype(float)
                EV_psi = float(np.dot(p_g, dV_dpsi))
                dV_star_psi = float(dV_dpsi[j_star_loc])
                grad[param_pos] -= w_i * (dV_star_psi - EV_psi)

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


def run_estimation(data: RuroData, output_dir: Path, model_name: str = "ruro_boxcox_groupopps") -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    K = data.z_per_row.shape[1]
    G_types = len(data.group_names)
    R_types = len(data.region_labels)
    L_types = len(data.loc_labels)

    idx_alpha_c = 0
    idx_alpha_l = 1
    idx_beta_c_start = 2
    idx_beta_l0_start = idx_beta_c_start + G_types
    idx_delta_start = idx_beta_l0_start + G_types
    idx_kappa0_start = idx_delta_start + K
    idx_lambda_start = idx_kappa0_start + G_types
    idx_theta_start = idx_lambda_start + max(R_types - 1, 0)
    idx_psi_start = idx_theta_start + 4
    n_theta = idx_psi_start + max(L_types - 1, 0)

    # initial parameters
    theta0 = np.zeros(n_theta, dtype=float)
    theta0[idx_alpha_c] = 0.10
    theta0[idx_alpha_l] = 0.10

    # beta_c and beta_l0 by group
    for g in range(G_types):
        theta0[idx_beta_c_start + g] = 1.0
        theta0[idx_beta_l0_start + g] = 1.0

    # delta_k already 0

    # kappa0: choose π0 ≈ 0.1 as starting point
    pi0_init = 0.10
    eta_init = math.log(pi0_init / (1.0 - pi0_init))
    for g in range(G_types):
        theta0[idx_kappa0_start + g] = eta_init

    # lambda_r, theta_h*, theta_w*, psi_loc* already 0

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

    # Hessian and standard errors
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

    n_obs = data.n_groups
    aic = 2 * k - 2 * ll_star
    bic = math.log(n_obs) * k - 2 * ll_star
    LOGGER.info("AIC=%.2f  BIC=%.2f  (n_groups=%d)", aic, bic, n_obs)

    # Parameter names in same order as theta
    names: List[str] = []
    names.append("alpha_c")
    names.append("alpha_l")

    # beta_c and beta_l0
    for g, gname in enumerate(data.group_names):
        names.append(f"beta_c_{gname}")
    for g, gname in enumerate(data.group_names):
        names.append(f"beta_l0_{gname}")

    # delta_k
    for zname in data.z_names:
        names.append(f"delta_{zname}")

    # kappa0
    for g, gname in enumerate(data.group_names):
        names.append(f"kappa0_{gname}")

    # lambda_region (non-baseline)
    if R_types > 1:
        for r in range(1, R_types):
            lab = data.region_labels[r]
            names.append(f"lambda_region_{lab}")

    # theta_h*, theta_w*
    names.extend(["theta_h1", "theta_h2", "theta_w1", "theta_w2"])

    # psi_loc (non-baseline locs)
    if L_types > 1:
        for l_idx in range(1, L_types):
            lab = data.loc_labels[l_idx]
            names.append(f"psi_loc_{lab}")

    if len(names) != k:
        raise RuntimeError(f"Internal name/parameter length mismatch: {len(names)} names vs {k} parameters.")

    # dictionaries for JSON
    param_dict = {n: float(v) for n, v in zip(names, theta_hat)}
    se_dict = {n: float(s) for n, s in zip(names, se)}
    t_dict = {n: float(t) if np.isfinite(t) else float("nan") for n, t in zip(names, t_vals)}
    p_dict = {n: float(p) if np.isfinite(p) else float("nan") for n, p in zip(names, p_vals)}

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
        "group_names": data.group_names,
        "region_labels": data.region_labels,
        "loc_labels": data.loc_labels,
        "loc_baseline_label": data.loc_baseline_label,
        "z_names": data.z_names,
        "t_hours": float(data.t_hours),
    }

    out_path = output_dir / f"{model_name}_results.json"
    out_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    LOGGER.info("Saved results to %s", out_path)

    # Parameter CSV
    param_rows = []
    for i, name in enumerate(names):
        param_rows.append(
            {
                "Name": name,
                "Value": float(theta_hat[i]),
                "StdErr": float(se[i]),
                "t": float(t_vals[i]),
                "p": float(p_vals[i]),
            }
        )
    param_df = pd.DataFrame.from_records(param_rows).set_index("Name")
    param_csv = output_dir / f"{model_name}_parameters.csv"
    param_df.to_csv(param_csv)
    LOGGER.info("Saved parameter table to %s", param_csv)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="RURO Box–Cox MNL with group-specific preferences and opportunity functions."
    )
    parser.add_argument(
        "--data-path",
        type=Path,
        required=True,
        help="Path to long RURO MNL dataset (parquet/csv/pkl).",
    )
    parser.add_argument("--id-col", default="idperson", help="Individual identifier column.")
    parser.add_argument("--choice-col", default="is_chosen", help="Choice indicator column (1=chosen, 0=otherwise).")
    parser.add_argument("--cons-col", default="consumption", help="Consumption / net income column name.")
    parser.add_argument("--hours-col", default="hours", help="Hours worked column name (if leisure not provided).")
    parser.add_argument("--leisure-col", default=None, help="Leisure column name (optional, overrides hours).")
    parser.add_argument("--wage-col", default="wage", help="Hourly wage column name.")
    parser.add_argument("--loc-col", default="loc", help="Occupation/LOC column name.")
    parser.add_argument("--region-col", default="drgn1", help="Region column (e.g. NUTS1).")
    parser.add_argument("--weight-col", default=None, help="Sampling weight column (optional).")
    parser.add_argument(
        "--t-hours",
        type=float,
        default=T_HOURS_DEFAULT,
        help="Total time endowment for leisure (e.g. 80 or 168).",
    )

    parser.add_argument(
        "--c-ref",
        choices=("mean", "p99"),
        default="mean",
        help="Reference for consumption normalisation: mean or 99th percentile of chosen consumption.",
    )
    parser.add_argument(
        "--l-ref",
        choices=("minpos", "mean"),
        default="minpos",
        help="Reference for leisure normalisation: min positive or mean chosen leisure.",
    )

    parser.add_argument(
        "--z-cols",
        nargs="*",
        default=None,
        help="Columns used as individual-level preference shifters in the leisure slope (beta_l).",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=reports_root() / "mle_ruro" / "boxcox_groupopps",
        help="Directory to store estimation outputs.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Logging verbosity.",
    )
    parser.add_argument("--model-name", default="ruro_boxcox_groupopps", help="Base name for output files.")
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
        wage_col=args.wage_col,
        loc_col=args.loc_col,
        region_col=args.region_col,
        weight_col=args.weight_col,
        t_hours=args.t_hours,
        c_ref_mode=args.c_ref,
        l_ref_mode=args.l_ref,
        z_cols=args.z_cols,
    )

    run_estimation(data, args.output_dir, model_name=args.model_name)


if __name__ == "__main__":
    main()
