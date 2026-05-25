"""RURO ruro_occ_M0 — Proposal-adequacy diagnostic.

Read-only audit of within-household variation in (C, L) and non-employment
mass in the proposal draws, to distinguish over-parameterisation from
draws-side starvation as the root cause of the M0 identification failure.

Run:
    python Results/_proposal_adequacy_diag_ruro_occ_M0.py

Writes:
    Results/_proposal_adequacy_diag_ruro_occ_M0.json
    Results/P3a/single_year_baseline/M0/RURO_ruro_occ_M0_proposal_adequacy_diag_v1.md
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Inputs
# ----------------------------------------------------------------------------

PRIMARY_PATHS = {
    "singles": r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet",
    "couples": r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet",
}
FALLBACK_PATHS = {
    "singles": r"\\aff300msh.cifs.myliser.lu\ComputeShare\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl__singles.parquet",
    "couples": r"\\aff300msh.cifs.myliser.lu\ComputeShare\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl__couples.parquet",
}

THETA_C_GRID = [-1.0, -0.5, 0.0, 0.215, 0.5]
THETA_L_GRID = [-1.0, -0.7, -0.5, 0.0]

# Exact M0 estimated thetas (from run_2026-05-13_11-27-40 / 15-02-16).
# Used for the verdict-relevant identification check; the grid above is for
# the curvature shape across theta.
M0_THETA_C = {
    "singles_male": -0.856029,
    "singles_female": -1.088410,
    "couples_household": 0.215302,
}
M0_THETA_L = {
    "singles_male": -0.703775,
    "singles_female": -0.723846,
    "couples_male": -0.733006,
    "couples_female": -0.695727,
}

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------


def log(msg: str) -> None:
    sys.stdout.write(f"{msg}\n")
    sys.stdout.flush()


def resolve_path(name: str) -> Path:
    p = Path(PRIMARY_PATHS[name])
    if p.exists():
        return p
    pf = Path(FALLBACK_PATHS[name])
    if pf.exists():
        log(f"  using fallback path for {name}: {pf}")
        return pf
    raise FileNotFoundError(f"Cannot find {name} parquet at primary or fallback path.")


def pick_first_present(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def bc(x: np.ndarray, theta: float, eps: float = 1e-6) -> np.ndarray:
    """Box-Cox transform on positive x; clips to >= eps before transform."""
    x_safe = np.clip(x, eps, None)
    if abs(theta) < 1e-12:
        return np.log(x_safe)
    return (np.power(x_safe, theta) - 1.0) / theta


def quantile_row(values: np.ndarray, qs=(0.10, 0.25, 0.50, 0.75, 0.90)) -> Dict[str, float]:
    if len(values) == 0:
        return {f"q{int(q*100):02d}": float("nan") for q in qs}
    out = {}
    for q in qs:
        out[f"q{int(q*100):02d}"] = float(np.quantile(values, q))
    return out


def within_between_ratio(
    df: pd.DataFrame, value_col: str, hh_col: str
) -> Tuple[float, float, np.ndarray]:
    """Return (median_within_std, between_std, within_std_array)."""
    g = df.groupby(hh_col)[value_col]
    within_std = g.std(ddof=0).to_numpy()
    between_std = float(np.std(g.mean().to_numpy(), ddof=0))
    median_within = float(np.nanmedian(within_std)) if len(within_std) else float("nan")
    return median_within, between_std, within_std


def per_hh_stat(df: pd.DataFrame, value_col: str, hh_col: str, fn: str) -> np.ndarray:
    g = df.groupby(hh_col)[value_col]
    if fn == "std":
        return g.std(ddof=0).to_numpy()
    if fn == "range":
        return (g.max() - g.min()).to_numpy()
    if fn == "mean":
        return g.mean().to_numpy()
    raise ValueError(fn)


def rank_corr_per_hh(df: pd.DataFrame, hh_col: str, c_col: str, l_col: str) -> np.ndarray:
    """Spearman correlation of (C, L) computed per household via rank-mean."""

    def _spearman(s: pd.DataFrame) -> float:
        if len(s) < 3:
            return float("nan")
        c = s[c_col].rank().to_numpy()
        l = s[l_col].rank().to_numpy()
        if np.std(c) < 1e-12 or np.std(l) < 1e-12:
            return float("nan")
        return float(np.corrcoef(c, l)[0, 1])

    out = df.groupby(hh_col, sort=False).apply(_spearman)
    return out.to_numpy()


# ----------------------------------------------------------------------------
# Group resolver
# ----------------------------------------------------------------------------


def resolve_singles(df: pd.DataFrame) -> Dict[str, Any]:
    info: Dict[str, Any] = {"file": "singles"}
    info["hh_col"] = pick_first_present(df, ["idhh", "idhh_true", "hh_id"])
    info["chosen_col"] = pick_first_present(df, ["is_chosen", "chosen"])
    info["gender_col"] = pick_first_present(df, ["dgn", "sex", "female", "male", "gender"])
    info["consumption_col"] = pick_first_present(df, ["consumption", "c_norm", "C", "ils_dispy", "ils_dispy_em"])
    info["leisure_col"] = pick_first_present(df, ["leisure", "L", "l_norm", "leisure_norm"])
    info["working_col"] = pick_first_present(df, ["working"])
    info["hours_col"] = pick_first_present(df, ["hours", "lhw", "h"])
    info["log_q_E_col"] = pick_first_present(df, ["log_q_E"])
    return info


def resolve_couples(df: pd.DataFrame) -> Dict[str, Any]:
    info: Dict[str, Any] = {"file": "couples"}
    info["hh_col"] = pick_first_present(df, ["idhh", "idhh_true", "hh_id"])
    info["chosen_col"] = pick_first_present(df, ["is_chosen", "chosen"])
    # household-level consumption (shared between male/female views)
    info["consumption_col"] = pick_first_present(df, ["consumption", "c_norm", "C", "ils_dispy", "ils_dispy_em"])
    # per-partner columns
    info["leisure_male_col"] = pick_first_present(df, ["leisure_male", "L_male", "l_norm_male"])
    info["leisure_female_col"] = pick_first_present(df, ["leisure_female", "L_female", "l_norm_female"])
    info["working_male_col"] = pick_first_present(df, ["working_male"])
    info["working_female_col"] = pick_first_present(df, ["working_female"])
    info["hours_male_col"] = pick_first_present(df, ["hours_male", "lhw_male", "h_male"])
    info["hours_female_col"] = pick_first_present(df, ["hours_female", "lhw_female", "h_female"])
    info["log_q_E_male_col"] = pick_first_present(df, ["log_q_E_male"])
    info["log_q_E_female_col"] = pick_first_present(df, ["log_q_E_female"])
    return info


# ----------------------------------------------------------------------------
# Diagnostics
# ----------------------------------------------------------------------------


def d1a_raw_variation(
    df: pd.DataFrame, hh_col: str, value_col: str, label: str
) -> Dict[str, Any]:
    log(f"  [{label}] D1a raw {value_col} variation")
    within_std = per_hh_stat(df, value_col, hh_col, "std")
    within_range = per_hh_stat(df, value_col, hh_col, "range")
    within_mean = per_hh_stat(df, value_col, hh_col, "mean")
    between_std = float(np.std(within_mean, ddof=0))
    median_within = float(np.nanmedian(within_std))
    r_raw = median_within / between_std if between_std > 0 else float("nan")
    return {
        "n_hh": int(len(within_std)),
        "within_std_quantiles": quantile_row(within_std),
        "within_range_quantiles": quantile_row(within_range),
        "within_mean_quantiles": quantile_row(within_mean),
        "between_std": between_std,
        "median_within_std": median_within,
        "R_raw": r_raw,
    }


def d1b_bc_variation(
    df: pd.DataFrame, hh_col: str, value_col: str, theta_grid: List[float], label: str
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for theta in theta_grid:
        log(f"  [{label}] D1b BC {value_col} at theta={theta:+.3f}")
        rows.append(_r_bc_at_theta(df, hh_col, value_col, theta))
    return rows


def _r_bc_at_theta(
    df: pd.DataFrame, hh_col: str, value_col: str, theta: float
) -> Dict[str, Any]:
    bc_col = f"__bc_{value_col}_{theta:+.6f}"
    df[bc_col] = bc(df[value_col].to_numpy(dtype=float), theta)
    med_w, between, within = within_between_ratio(df, bc_col, hh_col)
    r_bc = med_w / between if between > 0 else float("nan")
    row = {
        "theta": float(theta),
        "within_std_q25": float(np.quantile(within, 0.25)),
        "within_std_q50": float(np.quantile(within, 0.50)),
        "within_std_q75": float(np.quantile(within, 0.75)),
        "between_std": between,
        "R_BC": r_bc,
    }
    df.drop(columns=[bc_col], inplace=True)
    return row


def d1d_rank_corr(
    df: pd.DataFrame, hh_col: str, c_col: str, l_col: str, working_col: str, label: str
) -> Dict[str, Any]:
    log(f"  [{label}] D1d rank-corr(C, L)")
    rc_all = rank_corr_per_hh(df, hh_col, c_col, l_col)
    rc_all = rc_all[~np.isnan(rc_all)]
    # working-only
    work_df = df[df[working_col] == 1]
    rc_work = rank_corr_per_hh(work_df, hh_col, c_col, l_col)
    rc_work = rc_work[~np.isnan(rc_work)]
    return {
        "all_alts": {
            "n_hh": int(len(rc_all)),
            "median": float(np.median(rc_all)) if len(rc_all) else float("nan"),
            "q10": float(np.quantile(rc_all, 0.10)) if len(rc_all) else float("nan"),
            "q90": float(np.quantile(rc_all, 0.90)) if len(rc_all) else float("nan"),
        },
        "working_alts_only": {
            "n_hh": int(len(rc_work)),
            "median": float(np.median(rc_work)) if len(rc_work) else float("nan"),
            "q10": float(np.quantile(rc_work, 0.10)) if len(rc_work) else float("nan"),
            "q90": float(np.quantile(rc_work, 0.90)) if len(rc_work) else float("nan"),
        },
    }


def d2a_nonwork_share(
    df: pd.DataFrame, hh_col: str, working_col: str, label: str
) -> Dict[str, Any]:
    log(f"  [{label}] D2a non-work share per hh ({working_col})")
    g = df.groupby(hh_col)[working_col]
    n_alts = g.size()
    n_nonwork = (1 - df[working_col]).groupby(df[hh_col]).sum()
    share = (n_nonwork / n_alts).to_numpy(dtype=float)
    return {
        "n_hh": int(len(share)),
        "quantiles": quantile_row(share),
        "pct_hh_share_lt_5pct": float((share < 0.05).mean()),
        "pct_hh_share_lt_10pct": float((share < 0.10).mean()),
        "pct_hh_share_eq_0": float((share == 0).mean()),
    }


def d2b_observed_vs_proposal(
    df: pd.DataFrame, hh_col: str, working_col: str, chosen_col: str, label: str
) -> Dict[str, Any]:
    log(f"  [{label}] D2b observed (chosen) non-employment vs proposal median")
    chosen = df[df[chosen_col] == 1]
    obs_nonwork_rate = float((chosen[working_col] == 0).mean())
    n_alts = df.groupby(hh_col).size()
    n_nonwork = (1 - df[working_col]).groupby(df[hh_col]).sum()
    proposal_share = (n_nonwork / n_alts).to_numpy(dtype=float)
    proposal_median = float(np.median(proposal_share))
    return {
        "obs_nonwork_rate": obs_nonwork_rate,
        "proposal_median_share": proposal_median,
        "gap": obs_nonwork_rate - proposal_median,
    }


def d2c_log_q_e(
    df: pd.DataFrame, working_col: str, log_q_e_col: str, label: str
) -> Dict[str, Any]:
    log(f"  [{label}] D2c log_q_E mean on work vs non-work ({log_q_e_col})")
    if log_q_e_col is None or log_q_e_col not in df.columns:
        return {"missing": True, "log_q_e_col": log_q_e_col}
    work_mask = df[working_col] == 1
    return {
        "log_q_e_col": log_q_e_col,
        "mean_working": float(df.loc[work_mask, log_q_e_col].mean()),
        "mean_nonwork": float(df.loc[~work_mask, log_q_e_col].mean()),
        "diff": float(df.loc[work_mask, log_q_e_col].mean()
                      - df.loc[~work_mask, log_q_e_col].mean()),
    }


# ----------------------------------------------------------------------------
# Group runner
# ----------------------------------------------------------------------------


def run_singles(df: pd.DataFrame, info: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {"column_resolution": info}
    hh = info["hh_col"]; c = info["consumption_col"]; l = info["leisure_col"]
    work = info["working_col"]; chosen = info["chosen_col"]
    gender = info["gender_col"]
    log_q_e = info["log_q_E_col"]

    for label, dgn_value in [("singles_male", 1), ("singles_female", 0)]:
        log(f"\n--- {label} ---")
        sub = df[df[gender] == dgn_value].copy() if gender else df.copy()
        log(f"  rows: {len(sub):,}, households: {sub[hh].nunique():,}")
        if work not in sub.columns and "hours" in sub.columns:
            sub[work] = (sub["hours"] > 0).astype(int)
        group_out: Dict[str, Any] = {
            "n_rows": int(len(sub)),
            "n_hh": int(sub[hh].nunique()),
        }
        if c:
            group_out["D1a_consumption"] = d1a_raw_variation(sub, hh, c, label)
            group_out["D1b_consumption_BC"] = d1b_bc_variation(sub, hh, c, THETA_C_GRID, label)
            m0_theta_c = M0_THETA_C.get(label)
            if m0_theta_c is not None:
                log(f"  [{label}] D1b BC consumption at M0 theta={m0_theta_c:+.6f}")
                group_out["D1b_at_M0_theta"] = _r_bc_at_theta(sub, hh, c, m0_theta_c)
        if l:
            group_out["D1a_leisure"] = d1a_raw_variation(sub, hh, l, label)
            group_out["D1c_leisure_BC"] = d1b_bc_variation(sub, hh, l, THETA_L_GRID, label)
            m0_theta_l = M0_THETA_L.get(label)
            if m0_theta_l is not None:
                log(f"  [{label}] D1c BC leisure at M0 theta={m0_theta_l:+.6f}")
                group_out["D1c_at_M0_theta"] = _r_bc_at_theta(sub, hh, l, m0_theta_l)
        if c and l and work in sub.columns:
            group_out["D1d_rank_corr"] = d1d_rank_corr(sub, hh, c, l, work, label)
        if work in sub.columns:
            group_out["D2a_nonwork_share"] = d2a_nonwork_share(sub, hh, work, label)
            group_out["D2b_observed_vs_proposal"] = d2b_observed_vs_proposal(
                sub, hh, work, chosen, label
            )
            group_out["D2c_log_q_e"] = d2c_log_q_e(sub, work, log_q_e, label)
        out[label] = group_out
    return out


def run_couples(df: pd.DataFrame, info: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {"column_resolution": info}
    hh = info["hh_col"]; c = info["consumption_col"]; chosen = info["chosen_col"]

    # Consumption is household-level (one series); compute it once and note duplication.
    couples_c_block: Dict[str, Any] = {}
    if c:
        log("\n--- couples (household consumption) ---")
        couples_c_block["D1a_consumption"] = d1a_raw_variation(df, hh, c, "couples (hh)")
        couples_c_block["D1b_consumption_BC"] = d1b_bc_variation(df, hh, c, THETA_C_GRID, "couples (hh)")
        m0_theta_c = M0_THETA_C.get("couples_household")
        if m0_theta_c is not None:
            log(f"  [couples (hh)] D1b BC consumption at M0 theta={m0_theta_c:+.6f}")
            couples_c_block["D1b_at_M0_theta"] = _r_bc_at_theta(df, hh, c, m0_theta_c)
        couples_c_block["note"] = (
            "Couples `consumption` is a household-level aggregate, shared between "
            "couples_male and couples_female views. Reported once."
        )
    out["couples_household_consumption"] = couples_c_block

    for label, partner in [("couples_male", "male"), ("couples_female", "female")]:
        log(f"\n--- {label} ---")
        l = info[f"leisure_{partner}_col"]
        work = info[f"working_{partner}_col"]
        log_q_e = info[f"log_q_E_{partner}_col"]
        hours = info[f"hours_{partner}_col"]
        if work is None and hours:
            log(f"  deriving working_{partner} = ({hours} > 0)")
            df[f"__work_{partner}"] = (df[hours] > 0).astype(int)
            work = f"__work_{partner}"
        log(f"  rows: {len(df):,}, households: {df[hh].nunique():,}")
        group_out: Dict[str, Any] = {
            "n_rows": int(len(df)),
            "n_hh": int(df[hh].nunique()),
            "working_col_used": work,
            "leisure_col_used": l,
            "log_q_e_col_used": log_q_e,
        }
        if l:
            group_out["D1a_leisure"] = d1a_raw_variation(df, hh, l, label)
            group_out["D1c_leisure_BC"] = d1b_bc_variation(df, hh, l, THETA_L_GRID, label)
            m0_theta_l = M0_THETA_L.get(label)
            if m0_theta_l is not None:
                log(f"  [{label}] D1c BC leisure at M0 theta={m0_theta_l:+.6f}")
                group_out["D1c_at_M0_theta"] = _r_bc_at_theta(df, hh, l, m0_theta_l)
        if c and l and work in df.columns:
            group_out["D1d_rank_corr"] = d1d_rank_corr(df, hh, c, l, work, label)
        if work in df.columns:
            group_out["D2a_nonwork_share"] = d2a_nonwork_share(df, hh, work, label)
            group_out["D2b_observed_vs_proposal"] = d2b_observed_vs_proposal(
                df, hh, work, chosen, label
            )
            group_out["D2c_log_q_e"] = d2c_log_q_e(df, work, log_q_e, label)
        out[label] = group_out
        if work and work.startswith("__work_"):
            df.drop(columns=[work], inplace=True)
    return out


# ----------------------------------------------------------------------------
# Verdict synthesis
# ----------------------------------------------------------------------------


def compute_verdict(results: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
    """Determine PASS / FLAG / FAIL using R_BC_C evaluated AT the M0
    estimated theta values (not at arbitrary grid corners).

    Also surfaces D1d working-conditional rank correlation and D2a non-work
    median share so the verdict integrates all three identification
    channels: marginal-BC variation, joint (C, L) separability, and beta_E.
    """
    detail: Dict[str, Any] = {}

    # 1. R_BC_C at M0 theta_c values (direct lookup from D1b_at_M0)
    r_bc_at_m0: Dict[str, float] = {}
    for grp_key, store_key in (
        ("singles_male", "singles"),
        ("singles_female", "singles"),
        ("couples_household", "couples"),
    ):
        if store_key == "couples":
            grp = results[store_key].get("couples_household_consumption", {})
        else:
            grp = results[store_key].get(grp_key, {})
        m0_row = grp.get("D1b_at_M0_theta")
        if m0_row and "R_BC" in m0_row:
            r_bc_at_m0[grp_key] = m0_row["R_BC"]
    detail["R_BC_C_at_M0"] = r_bc_at_m0

    min_r_at_m0 = min(
        (v for v in r_bc_at_m0.values() if not np.isnan(v)),
        default=float("nan"),
    )

    # 2. Non-work mass median
    nw_medians: Dict[str, float] = {}
    for grp_key, store_key in (
        ("singles_male", "singles"),
        ("singles_female", "singles"),
        ("couples_male", "couples"),
        ("couples_female", "couples"),
    ):
        d2a = results[store_key].get(grp_key, {}).get("D2a_nonwork_share")
        if d2a:
            nw_medians[grp_key] = d2a["quantiles"]["q50"]
    detail["nonwork_share_medians"] = nw_medians
    min_nw_median = min(
        (v for v in nw_medians.values() if not np.isnan(v)),
        default=float("nan"),
    )

    # 3. C-L rank correlation (working alts only — the operationally relevant slice)
    rank_corr_working: Dict[str, float] = {}
    for grp_key, store_key in (
        ("singles_male", "singles"),
        ("singles_female", "singles"),
        ("couples_male", "couples"),
        ("couples_female", "couples"),
    ):
        d1d = results[store_key].get(grp_key, {}).get("D1d_rank_corr", {})
        working = d1d.get("working_alts_only", {})
        if "median" in working:
            rank_corr_working[grp_key] = working["median"]
    detail["rank_corr_working_medians"] = rank_corr_working
    min_rank_corr = min(
        (v for v in rank_corr_working.values() if not np.isnan(v)),
        default=float("nan"),
    )

    # Verdict construction — each channel checked independently
    fail_reasons: List[str] = []
    flag_reasons: List[str] = []

    if not np.isnan(min_r_at_m0):
        if min_r_at_m0 < 0.1:
            fail_reasons.append(
                f"R_BC_C at M0 theta lowest = {min_r_at_m0:.3f} < 0.1 (beta_c, theta_c) unidentified"
            )
        elif min_r_at_m0 < 0.3:
            flag_reasons.append(
                f"R_BC_C at M0 theta lowest = {min_r_at_m0:.3f} in marginal band [0.1, 0.3]"
            )

    if not np.isnan(min_nw_median):
        if min_nw_median < 0.05:
            fail_reasons.append(
                f"non-work share median lowest = {min_nw_median:.3f} < 5% (beta_E unidentified)"
            )
        elif min_nw_median < 0.08:
            flag_reasons.append(
                f"non-work share median lowest = {min_nw_median:.3f} below comfortable 8% floor"
            )

    if not np.isnan(min_rank_corr) and min_rank_corr <= -0.85:
        fail_reasons.append(
            f"rank-corr(C, L) on working alts lowest = {min_rank_corr:.3f} <= -0.85 (C, L collinear)"
        )

    if fail_reasons:
        verdict = "FAIL"
    elif flag_reasons:
        verdict = "FLAG"
    else:
        verdict = "PASS"

    # Rationale text
    parts: List[str] = []
    if r_bc_at_m0:
        bits = ", ".join(f"{k}={v:.3f}" for k, v in r_bc_at_m0.items())
        parts.append(f"R_BC_C at M0 thetas: {bits}.")
    parts.append(
        f"Non-work median share lowest at {min_nw_median:.3f}; "
        f"working-only rank-corr(C, L) lowest at {min_rank_corr:.3f}."
    )
    if verdict == "FAIL":
        parts.append(
            "FAIL: " + "; ".join(fail_reasons)
            + ". Proposal redesign needed before any spec-level repair will "
              "stabilise the Hessian. M0a (parameter removal/pooling) is "
              "unlikely to clear Gate B2 on its own."
        )
    elif verdict == "FLAG":
        parts.append(
            "FLAG: " + "; ".join(flag_reasons)
            + ". M0a is worth running, but plan to re-evaluate "
              "R_BC_C at the M0a converged theta. If R_BC_C drops further "
              "after pooling, draws-side widening may also be needed."
        )
    else:
        parts.append(
            "PASS: within-hh variation in consumption, leisure, and non-work "
            "mass is sufficient to identify the M0 preference block at the "
            "M0 estimated thetas. The M0 identification failure is "
            "over-parameterisation, not draws-side starvation. M0a "
            "(drop 5 params via beta_l_educH removal + theta_c singles pool) "
            "is the right next move."
        )

    rationale = " ".join(parts)
    return verdict, rationale, detail


# ----------------------------------------------------------------------------
# Reporting
# ----------------------------------------------------------------------------


def fmt(value, fmt_str=".4f"):
    if value is None or (isinstance(value, float) and (np.isnan(value) or np.isinf(value))):
        return "NA"
    if isinstance(value, (int, np.integer)):
        return f"{int(value):,}"
    if isinstance(value, float):
        return format(value, fmt_str)
    return str(value)


def md_q_row(label: str, q: Dict[str, float]) -> str:
    return f"| {label} | {fmt(q.get('q10'))} | {fmt(q.get('q25'))} | {fmt(q.get('q50'))} | {fmt(q.get('q75'))} | {fmt(q.get('q90'))} |"


def write_report(
    out_path: Path,
    metadata: Dict[str, Any],
    results: Dict[str, Any],
    verdict: str,
    rationale: str,
    verdict_detail: Dict[str, Any],
) -> None:
    lines: List[str] = []
    lines.append("# RURO ruro_occ_M0 — Proposal-Adequacy Diagnostic v1")
    lines.append("")
    lines.append(f"Date: {metadata['date']}")
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(f"**{verdict}.** {rationale}")
    lines.append("")
    lines.append("Thresholds (per the prompt):")
    lines.append("")
    lines.append("- `R_BC_C(theta) >= 0.3` → identifiable; `< 0.1` → FAIL; `[0.1, 0.3]` → marginal.")
    lines.append("- Median per-hh non-work share `< 5%` flags thin non-employment mass.")
    lines.append("- Median rank-corr(C, L) over working alts `<= -0.85` flags consumption/leisure collinearity within choice sets.")
    lines.append("")
    lines.append("Unweighted statistics throughout; EUROMOD household weight `dwt` is intentionally not applied (diagnostic, not population estimate).")
    lines.append("")

    # Input files
    lines.append("## Input files")
    lines.append("")
    lines.append("| dataset | path | size (B) | mtime | n_rows | n_columns | n_households |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for name in ("singles", "couples"):
        m = metadata["files"][name]
        lines.append(
            f"| {name} | `{m['path']}` | {m['size']:,} | {m['mtime']} | "
            f"{m['n_rows']:,} | {m['n_cols']} | {m['n_hh']:,} |"
        )
    lines.append("")

    # Column resolution
    lines.append("## Column resolution")
    lines.append("")
    lines.append("| dataset | role | column used |")
    lines.append("| --- | --- | --- |")
    s_res = results["singles"]["column_resolution"]
    for role in ("hh_col", "chosen_col", "gender_col", "consumption_col", "leisure_col", "working_col", "hours_col", "log_q_E_col"):
        lines.append(f"| singles | {role} | `{s_res.get(role)}` |")
    c_res = results["couples"]["column_resolution"]
    for role in ("hh_col", "chosen_col", "consumption_col", "leisure_male_col", "leisure_female_col", "working_male_col", "working_female_col", "hours_male_col", "hours_female_col", "log_q_E_male_col", "log_q_E_female_col"):
        lines.append(f"| couples | {role} | `{c_res.get(role)}` |")
    lines.append("")
    lines.append("Note: couples `consumption` is a household-level aggregate; both `couples_male` and `couples_female` views see the same C column. To avoid duplicated rows in D1a / D1b, couples C is reported once under `couples (household)`.")
    lines.append("")

    # D1 consumption
    lines.append("## D1 — Consumption and leisure variation")
    lines.append("")
    lines.append("### D1a Raw consumption — within-hh std quantiles per group")
    lines.append("")
    lines.append("| group | q10 | q25 | q50 | q75 | q90 | between_hh_std | R_C_raw |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for grp_name, grp_data, key in [
        ("singles_male", results["singles"].get("singles_male", {}), "D1a_consumption"),
        ("singles_female", results["singles"].get("singles_female", {}), "D1a_consumption"),
        ("couples (household)", results["couples"].get("couples_household_consumption", {}), "D1a_consumption"),
    ]:
        d = grp_data.get(key)
        if d is None:
            continue
        q = d["within_std_quantiles"]
        lines.append(
            f"| {grp_name} | {fmt(q['q10'])} | {fmt(q['q25'])} | {fmt(q['q50'])} | "
            f"{fmt(q['q75'])} | {fmt(q['q90'])} | {fmt(d['between_std'])} | "
            f"{fmt(d['R_raw'])} |"
        )
    lines.append("")

    # M0-anchor evaluation (verdict-relevant)
    lines.append("### D1b BIS — R_BC_C evaluated AT the M0 estimated thetas (verdict-relevant)")
    lines.append("")
    lines.append("R_BC_C at the grid corner thetas can dip near zero for purely numerical reasons (e.g. Box-Cox compression near theta=-1 on large C). The verdict-relevant question is whether identification holds at the theta the estimator actually picked. M0 estimates: theta_c_sm = -0.856, theta_c_sf = -1.088, couples theta_c = +0.215.")
    lines.append("")
    lines.append("| group | M0 theta | within_std q25 | q50 | q75 | between_std | R_BC_C |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for grp_name, grp_key, store_key in [
        ("singles_male", "singles_male", "singles"),
        ("singles_female", "singles_female", "singles"),
        ("couples (household)", "couples_household_consumption", "couples"),
    ]:
        row = results[store_key].get(grp_key, {}).get("D1b_at_M0_theta")
        if not row:
            continue
        lines.append(
            f"| {grp_name} | {row['theta']:+.4f} | "
            f"{fmt(row['within_std_q25'])} | {fmt(row['within_std_q50'])} | "
            f"{fmt(row['within_std_q75'])} | {fmt(row['between_std'])} | "
            f"{fmt(row['R_BC'])} |"
        )
    lines.append("")

    lines.append("### D1b Box-Cox consumption — R_BC_C by anchor grid")
    lines.append("")
    lines.append("| group | theta | within_std q25 | q50 | q75 | between_std | R_BC_C |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for grp_name, grp_key, store_key in [
        ("singles_male", "singles_male", "singles"),
        ("singles_female", "singles_female", "singles"),
        ("couples (household)", "couples_household_consumption", "couples"),
    ]:
        rows = results[store_key].get(grp_key, {}).get("D1b_consumption_BC", [])
        for row in rows:
            lines.append(
                f"| {grp_name} | {row['theta']:+.3f} | "
                f"{fmt(row['within_std_q25'])} | {fmt(row['within_std_q50'])} | "
                f"{fmt(row['within_std_q75'])} | {fmt(row['between_std'])} | "
                f"{fmt(row['R_BC'])} |"
            )
    lines.append("")

    # D1c leisure
    lines.append("### D1c Leisure — raw within-hh std + Box-Cox R_BC_L by theta")
    lines.append("")
    lines.append("| group | scope | theta or 'raw' | within_std q25 | q50 | q75 | between_std | R_BC |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for grp_name, grp_key, store_key in [
        ("singles_male", "singles_male", "singles"),
        ("singles_female", "singles_female", "singles"),
        ("couples_male", "couples_male", "couples"),
        ("couples_female", "couples_female", "couples"),
    ]:
        grp = results[store_key].get(grp_key, {})
        raw = grp.get("D1a_leisure")
        if raw:
            q = raw["within_std_quantiles"]
            lines.append(
                f"| {grp_name} | raw | — | {fmt(q['q25'])} | {fmt(q['q50'])} | "
                f"{fmt(q['q75'])} | {fmt(raw['between_std'])} | {fmt(raw['R_raw'])} |"
            )
        for row in grp.get("D1c_leisure_BC", []):
            lines.append(
                f"| {grp_name} | BC | {row['theta']:+.3f} | "
                f"{fmt(row['within_std_q25'])} | {fmt(row['within_std_q50'])} | "
                f"{fmt(row['within_std_q75'])} | {fmt(row['between_std'])} | "
                f"{fmt(row['R_BC'])} |"
            )
    lines.append("")

    # D1d rank correlation
    lines.append("### D1d Rank correlation between C and L, per household")
    lines.append("")
    lines.append("Reported two ways: over all 100 alts (includes non-work cluster) and over working alts only (the operationally relevant slice for the consumption/leisure separability question).")
    lines.append("")
    lines.append("| group | scope | n_hh | median | q10 | q90 |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for grp_name, grp_key, store_key in [
        ("singles_male", "singles_male", "singles"),
        ("singles_female", "singles_female", "singles"),
        ("couples_male", "couples_male", "couples"),
        ("couples_female", "couples_female", "couples"),
    ]:
        d = results[store_key].get(grp_key, {}).get("D1d_rank_corr", {})
        for scope_key, scope_label in [("all_alts", "all 100 alts"), ("working_alts_only", "working alts only")]:
            stats = d.get(scope_key, {})
            lines.append(
                f"| {grp_name} | {scope_label} | {fmt(stats.get('n_hh'))} | "
                f"{fmt(stats.get('median'))} | {fmt(stats.get('q10'))} | {fmt(stats.get('q90'))} |"
            )
    lines.append("")

    # D2 nonwork
    lines.append("## D2 — Non-employment mass")
    lines.append("")
    lines.append("### D2a Share of non-work alternatives per household")
    lines.append("")
    lines.append("| group | q10 | q25 | q50 | q75 | q90 | pct hh share < 5% | pct < 10% | pct == 0 |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for grp_name, grp_key, store_key in [
        ("singles_male", "singles_male", "singles"),
        ("singles_female", "singles_female", "singles"),
        ("couples_male", "couples_male", "couples"),
        ("couples_female", "couples_female", "couples"),
    ]:
        d = results[store_key].get(grp_key, {}).get("D2a_nonwork_share")
        if not d:
            continue
        q = d["quantiles"]
        lines.append(
            f"| {grp_name} | {fmt(q['q10'])} | {fmt(q['q25'])} | {fmt(q['q50'])} | "
            f"{fmt(q['q75'])} | {fmt(q['q90'])} | {fmt(d['pct_hh_share_lt_5pct'])} | "
            f"{fmt(d['pct_hh_share_lt_10pct'])} | {fmt(d['pct_hh_share_eq_0'])} |"
        )
    lines.append("")

    lines.append("### D2b Observed (chosen) non-employment vs proposal median")
    lines.append("")
    lines.append("| group | obs nonwork rate | proposal median share | gap (obs - proposal) |")
    lines.append("| --- | --- | --- | --- |")
    for grp_name, grp_key, store_key in [
        ("singles_male", "singles_male", "singles"),
        ("singles_female", "singles_female", "singles"),
        ("couples_male", "couples_male", "couples"),
        ("couples_female", "couples_female", "couples"),
    ]:
        d = results[store_key].get(grp_key, {}).get("D2b_observed_vs_proposal")
        if not d:
            continue
        lines.append(
            f"| {grp_name} | {fmt(d['obs_nonwork_rate'])} | "
            f"{fmt(d['proposal_median_share'])} | {fmt(d['gap'])} |"
        )
    lines.append("")

    lines.append("### D2c Mean log_q_E on working vs non-work")
    lines.append("")
    lines.append("| group | log_q_E column | mean (working) | mean (non-work) | diff |")
    lines.append("| --- | --- | --- | --- | --- |")
    for grp_name, grp_key, store_key in [
        ("singles_male", "singles_male", "singles"),
        ("singles_female", "singles_female", "singles"),
        ("couples_male", "couples_male", "couples"),
        ("couples_female", "couples_female", "couples"),
    ]:
        d = results[store_key].get(grp_key, {}).get("D2c_log_q_e")
        if not d:
            continue
        if d.get("missing"):
            lines.append(f"| {grp_name} | _missing: `{d['log_q_e_col']}`_ | NA | NA | NA |")
            continue
        lines.append(
            f"| {grp_name} | `{d['log_q_e_col']}` | "
            f"{fmt(d['mean_working'])} | {fmt(d['mean_nonwork'])} | {fmt(d['diff'])} |"
        )
    lines.append("")

    # Diagnostic summary
    lines.append("## Diagnostic summary")
    lines.append("")
    lines.append(rationale)
    lines.append("")

    # Files produced
    lines.append("## Files produced")
    lines.append("")
    lines.append("| file | purpose |")
    lines.append("| --- | --- |")
    lines.append("| `Results/_proposal_adequacy_diag_ruro_occ_M0.py` | reusable script |")
    lines.append("| `Results/_proposal_adequacy_diag_ruro_occ_M0.json` | machine-readable results |")
    lines.append("| `Results/P3a/single_year_baseline/M0/RURO_ruro_occ_M0_proposal_adequacy_diag_v1.md` | this report |")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main() -> int:
    out_dir = Path(__file__).resolve().parent
    json_path = out_dir / "_proposal_adequacy_diag_ruro_occ_M0.json"
    md_path = out_dir / "RURO_ruro_occ_M0_proposal_adequacy_diag_v1.md"

    metadata: Dict[str, Any] = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "files": {},
    }

    log("Loading parquets...")
    paths = {k: resolve_path(k) for k in PRIMARY_PATHS}
    for name, p in paths.items():
        st = p.stat()
        metadata["files"][name] = {
            "path": str(p),
            "size": st.st_size,
            "mtime": datetime.datetime.fromtimestamp(st.st_mtime).isoformat(),
        }
    df_s = pd.read_parquet(paths["singles"])
    df_c = pd.read_parquet(paths["couples"])
    metadata["files"]["singles"]["n_rows"] = int(len(df_s))
    metadata["files"]["singles"]["n_cols"] = int(len(df_s.columns))
    metadata["files"]["couples"]["n_rows"] = int(len(df_c))
    metadata["files"]["couples"]["n_cols"] = int(len(df_c.columns))

    log("Resolving columns...")
    s_info = resolve_singles(df_s)
    c_info = resolve_couples(df_c)
    metadata["files"]["singles"]["n_hh"] = int(df_s[s_info["hh_col"]].nunique())
    metadata["files"]["couples"]["n_hh"] = int(df_c[c_info["hh_col"]].nunique())

    log(f"singles columns: {s_info}")
    log(f"couples columns: {c_info}")

    log("\nRunning singles diagnostics...")
    s_results = run_singles(df_s, s_info)
    log("\nRunning couples diagnostics...")
    c_results = run_couples(df_c, c_info)
    results = {"singles": s_results, "couples": c_results}

    log("\nComputing verdict...")
    verdict, rationale, verdict_detail = compute_verdict(results)
    log(f"Verdict: {verdict}")
    log(f"R_BC_C at M0 thetas: {verdict_detail.get('R_BC_C_at_M0')}")

    payload = {
        "metadata": metadata,
        "thresholds": {
            "R_BC_C_fail": 0.1,
            "R_BC_C_marginal": 0.3,
            "nonwork_thin_share_threshold_pct": 5,
            "nonwork_flag_share_threshold_pct": 8,
            "rank_corr_collinearity_threshold": -0.85,
        },
        "M0_anchors": {
            "theta_c": M0_THETA_C,
            "theta_l": M0_THETA_L,
        },
        "results": results,
        "verdict": verdict,
        "verdict_detail": verdict_detail,
        "rationale": rationale,
    }
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    log(f"Wrote {json_path}")

    write_report(md_path, metadata, results, verdict, rationale, verdict_detail)
    log(f"Wrote {md_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
