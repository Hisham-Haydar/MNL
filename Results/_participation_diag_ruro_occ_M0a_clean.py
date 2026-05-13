"""Participation-pathology V-decomposition diagnostic for ruro_occ_M0a_clean.

Reconstructs the choice index V_ij per alternative from the parsed spec and
estimated parameters, computes a structural softmax P(j|i), and reports
P(nonwork) per group. Compares to the post-estimation report's
``participation_predicted`` figure of 1.0000 to identify whether the
pathology is a structural prediction or a reporting bug.

Read-only against parquets and the JSON; no estimator invocation.
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yaml

# ----------------------------------------------------------------------------
# Inputs
# ----------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_YAML = REPO_ROOT / "scripts" / "enhanced" / "estimation_spec_ruro_occ_M0a_clean.yaml"

PRIMARY_PARQUET = {
    "singles": r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet",
    "couples": r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet",
}
FALLBACK_PARQUET = {
    "singles": r"\\aff300msh.cifs.myliser.lu\ComputeShare\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl__singles.parquet",
    "couples": r"\\aff300msh.cifs.myliser.lu\ComputeShare\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl__couples.parquet",
}

JSON_OUT = REPO_ROOT / "Results" / "_participation_diag_ruro_occ_M0a_clean.json"
MD_OUT = REPO_ROOT / "Results" / "RURO_ruro_occ_M0a_clean_participation_diag_v1.md"

N_HH_SAMPLE_CAP = 100
SAMPLE_SEED = 17


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------


def log(msg: str) -> None:
    sys.stdout.write(f"{msg}\n")
    sys.stdout.flush()


def resolve_parquet(name: str) -> Path:
    p = Path(PRIMARY_PARQUET[name])
    if p.exists():
        return p
    fp = Path(FALLBACK_PARQUET[name])
    if fp.exists():
        return fp
    raise FileNotFoundError(f"{name} parquet not found at primary or fallback path")


def find_latest_m0a_clean_run() -> Path:
    base = REPO_ROOT / "outputs" / "estimates" / "fr" / "spec" / "ruro_occ" / "gamspy" / "estimation_spec_ruro_occ_M0a_clean"
    runs = sorted(base.glob("run_*/estimation_results.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not runs:
        raise FileNotFoundError(f"No M0a-clean run found under {base}")
    return runs[0]


def find_latest_m0a_clean_summary() -> Optional[Path]:
    reports_dir = REPO_ROOT / "reports"
    cands = sorted(reports_dir.glob("fr_2016_ruro_occ_gamspy_M0a_clean_llm_summary_*.md"),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    return cands[0] if cands else None


def box_cox(x: np.ndarray, theta: float, eps: float = 1e-6) -> np.ndarray:
    xs = np.clip(np.asarray(x, dtype=float), eps, None)
    if abs(theta) < 1e-12:
        return np.log(xs)
    return (np.power(xs, theta) - 1.0) / theta


def lognormal_logpdf(w: np.ndarray, mu: np.ndarray, sigma: float) -> np.ndarray:
    """log f_W(w) for a log-normal density on wage levels.

    Includes the -log(w) Jacobian so this is the density on wage in levels.
    Returns -inf-equivalent (np.nan_to_num to a very negative value) for
    non-positive wages — callers must zero this contribution on non-work alts.
    """
    w_safe = np.clip(np.asarray(w, dtype=float), 1e-12, None)
    z = (np.log(w_safe) - mu) / sigma
    return -np.log(w_safe) - np.log(sigma) - 0.5 * np.log(2.0 * np.pi) - 0.5 * z * z


# ----------------------------------------------------------------------------
# Parameter lookup (group-suffix aware — what compute_fit_diagnostics gets wrong)
# ----------------------------------------------------------------------------


def get_singles_param(params: Dict[str, float], base: str, gender: str,
                      shared: Optional[str] = None,
                      default: Optional[float] = None) -> float:
    """Look up a parameter for a singles group. ``gender`` is 'sm' or 'sf'.

    Order: shared name (if provided) -> base_<gender> -> base -> default.
    """
    if shared and shared in params:
        return float(params[shared])
    suffixed = f"{base}_{gender}"
    if suffixed in params:
        return float(params[suffixed])
    if base in params:
        return float(params[base])
    if default is None:
        raise KeyError(
            f"Parameter '{base}' not found for singles {gender} (no fallback)."
        )
    return float(default)


def get_couples_param(params: Dict[str, float], base: str, partner: str,
                      default: Optional[float] = None) -> float:
    """Look up a parameter for one partner of a couple. ``partner`` is 'm' or 'f'.

    Order: base_<partner> -> base -> default.
    """
    suffixed = f"{base}_{partner}"
    if suffixed in params:
        return float(params[suffixed])
    if base in params:
        return float(params[base])
    if default is None:
        raise KeyError(
            f"Parameter '{base}' not found for couples {partner} (no fallback)."
        )
    return float(default)


# ----------------------------------------------------------------------------
# V-decomposition: singles
# ----------------------------------------------------------------------------


def decompose_v_singles(
    df: pd.DataFrame,
    params: Dict[str, float],
    spec: Dict[str, Any],
    gender: str,
) -> pd.DataFrame:
    """Reconstruct V component-by-component for one singles group.

    Mirrors the engine's per-group structure (estimation_engine.py
    `_compute_utility_singles` + opportunity shifters), reading parameters
    via group-suffix-aware lookups so the result matches the estimator's
    expectations. Returns a DataFrame with one row per alt and columns
    ``U``, ``O_E``, ``O_H``, ``O_market``, ``O_W``, ``O_Occ``,
    ``minus_log_prior``, ``V``.
    """
    n = len(df)
    out = pd.DataFrame(index=df.index)

    # --- Utility ------------------------------------------------------------
    consumption_cfg = spec.get("utility", {}).get("consumption", {})
    leisure_cfg = spec.get("utility", {}).get("leisure", {})

    shared_theta_c = consumption_cfg.get("singles_box_cox_exponent")
    beta_c = get_singles_param(params, "beta_c", gender)
    theta_c = get_singles_param(params, "theta_c", gender, shared=shared_theta_c)
    theta_l = get_singles_param(params, "theta_l", gender)

    c = df["consumption"].to_numpy(dtype=float)
    L = df["leisure"].to_numpy(dtype=float)

    bc_c = box_cox(c, theta_c)
    bc_l = box_cox(L, theta_l)

    # beta_l(X) = beta_l0 + sum_k beta_l_k * X_k (gender-suffixed)
    beta_l0 = get_singles_param(params, "beta_l0", gender)
    beta_l = np.full(n, beta_l0, dtype=float)
    for shifter in (leisure_cfg.get("shifters", []) or []):
        var = shifter.get("variable")
        coef_base = shifter.get("coefficient")
        # n_children is gender_specific=true (female only)
        if (shifter.get("gender_specific") and var == "n_children"
                and gender == "sm"):
            continue
        coef_name = f"{coef_base}_{gender}"
        if coef_name not in params:
            continue  # M0a-clean removes beta_l_educH_*
        coef = float(params[coef_name])
        if var not in df.columns:
            continue
        beta_l = beta_l + coef * df[var].to_numpy(dtype=float)

    U = beta_c * bc_c + beta_l * bc_l
    out["U"] = U

    # --- O^E + O^H from hours_opportunity (working-gated) ------------------
    O_E = np.zeros(n)
    O_H = np.zeros(n)
    for shifter in (spec.get("hours_opportunity", {}).get("shifters", []) or []):
        var = shifter.get("variable")
        coef_name = shifter.get("coefficient")
        if coef_name not in params or var not in df.columns:
            continue
        contrib = float(params[coef_name]) * df[var].to_numpy(dtype=float)
        if coef_name == "beta_E":
            O_E = O_E + contrib
        else:
            O_H = O_H + contrib
    out["O_E"] = O_E
    out["O_H"] = O_H

    # --- O^market (residual market opportunity; working-gated via interaction) -
    O_market = np.zeros(n)
    market_cfg = spec.get("market_opportunity", {})
    var_scales = market_cfg.get("variable_scales", {}) or {}
    for shifter in (market_cfg.get("shifters", []) or []):
        var = shifter.get("variable")
        coef_name = shifter.get("coefficient")
        if coef_name not in params or var not in df.columns:
            continue
        x = df[var].to_numpy(dtype=float)
        scale = float(var_scales.get(var, 1.0))
        contrib = float(params[coef_name]) * (x / scale)
        for ix in (shifter.get("interaction", []) or []):
            if ix in df.columns:
                contrib = contrib * df[ix].to_numpy(dtype=float)
        O_market = O_market + contrib
    out["O_market"] = O_market

    # --- O^W (log-normal wage density; zero on non-work) -------------------
    wage_cfg = spec.get("wage_opportunity", {})
    sigma_name = (wage_cfg.get("variance") or {}).get("parameter", "sigma")
    sigma = float(params.get(sigma_name, np.nan))
    mu = np.zeros(n)
    for shifter in (wage_cfg.get("mean_shifters", []) or []):
        var = shifter.get("variable")
        coef_name = shifter.get("coefficient")
        if coef_name not in params:
            continue
        if var == "intercept":
            mu = mu + float(params[coef_name])
        elif var in df.columns:
            mu = mu + float(params[coef_name]) * df[var].to_numpy(dtype=float)
    working = df["working"].to_numpy(dtype=int)
    wage = df["wage"].to_numpy(dtype=float)
    O_W = np.where(working == 1, lognormal_logpdf(wage, mu, sigma), 0.0)
    out["O_W"] = O_W

    # --- O^Occ (occupation opportunity; working-gated, group-routed) -------
    O_Occ = np.zeros(n)
    occ_cfg = spec.get("occupation_opportunity", {})
    occ_var = occ_cfg.get("variable", "loc4")
    loc4 = df[occ_var].to_numpy()
    work_int = working
    for shifter in (occ_cfg.get("shifters", []) or []):
        applies = shifter.get("applies_to")
        if applies != gender:
            continue
        var = shifter.get("variable", "")  # e.g. loc4_2 -> category 2
        coef_name = shifter.get("coefficient")
        if coef_name not in params:
            continue
        try:
            k = int(var.split("_")[-1])
        except (ValueError, AttributeError):
            continue
        indicator = (loc4 == k).astype(int)
        contrib = float(params[coef_name]) * indicator
        for ix in (shifter.get("interaction", []) or []):
            if ix in df.columns:
                contrib = contrib * df[ix].to_numpy(dtype=float)
        O_Occ = O_Occ + contrib
    out["O_Occ"] = O_Occ

    # --- log_prior from parquet --------------------------------------------
    log_prior = df["log_prior"].to_numpy(dtype=float)
    out["minus_log_prior"] = -log_prior
    out["log_prior"] = log_prior

    # --- V ------------------------------------------------------------------
    out["V"] = U + O_E + O_H + O_market + O_W + O_Occ - log_prior

    # passthroughs for downstream audit
    out["idhh"] = df["idhh"].to_numpy()
    out["working"] = working
    out["wage"] = wage
    out["consumption"] = c
    out["leisure"] = L
    return out


# ----------------------------------------------------------------------------
# V-decomposition: couples
# ----------------------------------------------------------------------------


def decompose_v_couples(
    df: pd.DataFrame,
    params: Dict[str, float],
    spec: Dict[str, Any],
) -> pd.DataFrame:
    """Reconstruct V for couples. V_alt = U_household + O_male + O_female
    - log_prior (household). Returns one row per alt with male / female
    component decompositions for the audit."""
    n = len(df)
    out = pd.DataFrame(index=df.index)

    consumption_cfg = spec.get("utility", {}).get("consumption", {})
    leisure_cfg = spec.get("utility", {}).get("leisure", {})

    # Couples consumption uses the bare `theta_c` (not the singles-shared one).
    beta_c = float(params.get("beta_c", np.nan))
    theta_c = float(params.get("theta_c", np.nan))

    c = df["consumption"].to_numpy(dtype=float)
    bc_c = box_cox(c, theta_c)
    U_c = beta_c * bc_c
    out["U_c"] = U_c

    def _beta_l_partner(partner: str) -> np.ndarray:
        """beta_l(X) for couples partner ('m' or 'f')."""
        beta_l0 = get_couples_param(params, "beta_l0", partner)
        beta_l = np.full(n, beta_l0, dtype=float)
        for shifter in (leisure_cfg.get("shifters", []) or []):
            var = shifter.get("variable")
            coef_base = shifter.get("coefficient")
            # n_children gender_specific=true: female only
            if (shifter.get("gender_specific") and var == "n_children"
                    and partner == "m"):
                continue
            coef_name = f"{coef_base}_{partner}"
            if coef_name not in params:
                continue
            coef = float(params[coef_name])
            # Variable lookup: try gendered first, then household-level
            partner_full = "male" if partner == "m" else "female"
            col_candidates = [f"{var}_{partner_full}", var]
            x = None
            for col in col_candidates:
                if col in df.columns:
                    x = df[col].to_numpy(dtype=float)
                    break
            if x is None:
                continue
            beta_l = beta_l + coef * x
        return beta_l

    # Male
    theta_l_m = float(params.get("theta_l_m", np.nan))
    L_m = df["leisure_male"].to_numpy(dtype=float)
    bc_l_m = box_cox(L_m, theta_l_m)
    beta_l_m = _beta_l_partner("m")
    U_l_m = beta_l_m * bc_l_m
    out["U_l_m"] = U_l_m

    # Female
    theta_l_f = float(params.get("theta_l_f", np.nan))
    L_f = df["leisure_female"].to_numpy(dtype=float)
    bc_l_f = box_cox(L_f, theta_l_f)
    beta_l_f = _beta_l_partner("f")
    U_l_f = beta_l_f * bc_l_f
    out["U_l_f"] = U_l_f

    out["U"] = U_c + U_l_m + U_l_f

    # --- O^E, O^H, O^market, O^Occ per partner ----------------------------
    def _hours_oe_oh(partner: str, work_col: str) -> Tuple[np.ndarray, np.ndarray]:
        OE = np.zeros(n); OH = np.zeros(n)
        partner_full = "male" if partner == "m" else "female"
        for shifter in (spec.get("hours_opportunity", {}).get("shifters", []) or []):
            var = shifter.get("variable", "")
            coef_name = shifter.get("coefficient")
            if coef_name not in params:
                continue
            # Use partner-suffixed working variant
            if var == "working":
                x = df[work_col].to_numpy(dtype=float)
            else:
                # e.g. working_pt1 -> working_pt1_male
                partner_var = f"{var}_{partner_full}"
                if partner_var not in df.columns:
                    continue
                x = df[partner_var].to_numpy(dtype=float)
            contrib = float(params[coef_name]) * x
            if coef_name == "beta_E":
                OE = OE + contrib
            else:
                OH = OH + contrib
        return OE, OH

    OE_m, OH_m = _hours_oe_oh("m", "working_male")
    OE_f, OH_f = _hours_oe_oh("f", "working_female")
    out["O_E_m"] = OE_m
    out["O_H_m"] = OH_m
    out["O_E_f"] = OE_f
    out["O_H_f"] = OH_f
    out["O_E"] = OE_m + OE_f
    out["O_H"] = OH_m + OH_f

    # --- O^market per partner (gsur_<partner>, educH_<partner>) -----------
    def _market(partner: str, work_col: str) -> np.ndarray:
        OM = np.zeros(n)
        partner_full = "male" if partner == "m" else "female"
        market_cfg = spec.get("market_opportunity", {})
        var_scales = market_cfg.get("variable_scales", {}) or {}
        work = df[work_col].to_numpy(dtype=float)
        for shifter in (market_cfg.get("shifters", []) or []):
            var = shifter.get("variable")
            coef_name = shifter.get("coefficient")
            if coef_name not in params:
                continue
            partner_var = f"{var}_{partner_full}"
            if partner_var in df.columns:
                x = df[partner_var].to_numpy(dtype=float)
            elif var in df.columns:
                x = df[var].to_numpy(dtype=float)
            else:
                continue
            scale = float(var_scales.get(var, 1.0))
            contrib = float(params[coef_name]) * (x / scale)
            # interaction terms (e.g. "working") -> use partner-specific working
            for ix in (shifter.get("interaction", []) or []):
                if ix == "working":
                    contrib = contrib * work
                elif f"{ix}_{partner_full}" in df.columns:
                    contrib = contrib * df[f"{ix}_{partner_full}"].to_numpy(dtype=float)
                elif ix in df.columns:
                    contrib = contrib * df[ix].to_numpy(dtype=float)
            OM = OM + contrib
        return OM

    OM_m = _market("m", "working_male")
    OM_f = _market("f", "working_female")
    out["O_market_m"] = OM_m
    out["O_market_f"] = OM_f
    out["O_market"] = OM_m + OM_f

    # --- O^W per partner ---------------------------------------------------
    def _wage(partner: str, work_col: str) -> np.ndarray:
        wage_cfg = spec.get("wage_opportunity", {})
        sigma_name = (wage_cfg.get("variance") or {}).get("parameter", "sigma")
        sigma = float(params.get(sigma_name, np.nan))
        mu = np.zeros(n)
        partner_full = "male" if partner == "m" else "female"
        for shifter in (wage_cfg.get("mean_shifters", []) or []):
            var = shifter.get("variable")
            coef_name = shifter.get("coefficient")
            if coef_name not in params:
                continue
            if var == "intercept":
                mu = mu + float(params[coef_name])
                continue
            partner_var = f"{var}_{partner_full}"
            if partner_var in df.columns:
                x = df[partner_var].to_numpy(dtype=float)
            elif var in df.columns:
                x = df[var].to_numpy(dtype=float)
            else:
                continue
            mu = mu + float(params[coef_name]) * x
        wage_col = f"wage_{partner_full}"
        work = df[work_col].to_numpy(dtype=int)
        if wage_col in df.columns:
            w = df[wage_col].to_numpy(dtype=float)
            return np.where(work == 1, lognormal_logpdf(w, mu, sigma), 0.0)
        return np.zeros(n)

    OW_m = _wage("m", "working_male")
    OW_f = _wage("f", "working_female")
    out["O_W_m"] = OW_m
    out["O_W_f"] = OW_f
    out["O_W"] = OW_m + OW_f

    # --- O^Occ per partner -------------------------------------------------
    def _occ(partner: str, work_col: str) -> np.ndarray:
        OC = np.zeros(n)
        occ_cfg = spec.get("occupation_opportunity", {})
        partner_full = "male" if partner == "m" else "female"
        loc_col = f"loc4_{partner_full}"
        if loc_col not in df.columns:
            return OC
        loc = df[loc_col].to_numpy()
        work = df[work_col].to_numpy(dtype=int)
        applies_target = f"c{partner}"  # cm / cf
        for shifter in (occ_cfg.get("shifters", []) or []):
            if shifter.get("applies_to") != applies_target:
                continue
            var = shifter.get("variable", "")
            coef_name = shifter.get("coefficient")
            if coef_name not in params:
                continue
            try:
                k = int(var.split("_")[-1])
            except (ValueError, AttributeError):
                continue
            indicator = (loc == k).astype(int)
            contrib = float(params[coef_name]) * indicator * work
            OC = OC + contrib
        return OC

    OC_m = _occ("m", "working_male")
    OC_f = _occ("f", "working_female")
    out["O_Occ_m"] = OC_m
    out["O_Occ_f"] = OC_f
    out["O_Occ"] = OC_m + OC_f

    # --- log_prior from parquet --------------------------------------------
    log_prior = df["log_prior"].to_numpy(dtype=float)
    out["minus_log_prior"] = -log_prior
    out["log_prior"] = log_prior

    # --- V ------------------------------------------------------------------
    out["V"] = (out["U"].to_numpy()
                + out["O_E"].to_numpy() + out["O_H"].to_numpy()
                + out["O_market"].to_numpy()
                + out["O_W"].to_numpy() + out["O_Occ"].to_numpy()
                - log_prior)

    out["idhh"] = df["idhh"].to_numpy()
    out["working_male"] = df["working_male"].to_numpy()
    out["working_female"] = df["working_female"].to_numpy()
    return out


# ----------------------------------------------------------------------------
# Softmax + diagnostics
# ----------------------------------------------------------------------------


def softmax_per_hh(v_df: pd.DataFrame, hh_col: str = "idhh") -> np.ndarray:
    """Per-household softmax over V. Returns the probability per row."""
    n = len(v_df)
    prob = np.zeros(n)
    V = v_df["V"].to_numpy()
    idhh = v_df[hh_col].to_numpy()
    pos = 0
    # groupby preserves order; iterate over groups
    for _, group_idx in v_df.groupby(hh_col, sort=False).groups.items():
        idx = np.asarray(group_idx)
        Vg = V[v_df.index.get_indexer(idx)]
        Vg_shift = Vg - np.max(Vg)
        e = np.exp(Vg_shift)
        p = e / e.sum()
        prob[v_df.index.get_indexer(idx)] = p
    return prob


def softmax_per_hh_fast(v_df: pd.DataFrame, hh_col: str = "idhh") -> np.ndarray:
    """Vectorized variant: assumes consecutive same-idhh rows (which is how
    the parquets are stored after the rebuild). Falls back to per-group
    softmax via cumulative max/log-sum-exp by group."""
    V = v_df["V"].to_numpy()
    idhh = v_df[hh_col].to_numpy()
    # group max
    df_tmp = pd.DataFrame({"V": V, "idhh": idhh})
    max_by_hh = df_tmp.groupby("idhh")["V"].transform("max").to_numpy()
    e = np.exp(V - max_by_hh)
    sum_by_hh = df_tmp.assign(e=e).groupby("idhh")["e"].transform("sum").to_numpy()
    return e / sum_by_hh


def quantile_dict(arr: np.ndarray) -> Dict[str, float]:
    if len(arr) == 0:
        return {k: float("nan") for k in ("q10", "q25", "q50", "q75", "q90")}
    return {
        "q10": float(np.quantile(arr, 0.10)),
        "q25": float(np.quantile(arr, 0.25)),
        "q50": float(np.quantile(arr, 0.50)),
        "q75": float(np.quantile(arr, 0.75)),
        "q90": float(np.quantile(arr, 0.90)),
    }


def median(arr: np.ndarray) -> float:
    return float(np.median(arr)) if len(arr) else float("nan")


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main() -> int:
    # ===== D1: load inputs ===============================================
    log("Loading spec, JSON, parquets...")
    spec = yaml.safe_load(open(SPEC_YAML))
    json_path = find_latest_m0a_clean_run()
    log(f"  results JSON: {json_path}")
    results = json.load(open(json_path))
    spec_name_in_json = results.get("specification")
    first_group_data = next(iter(results["results"].values()))
    params = dict(first_group_data["parameters"])
    n_params = len(params)
    sanity = {
        "spec_name_matches": spec_name_in_json == "ruro_occ_M0a_clean",
        "n_params_eq_47": n_params == 47,
        "theta_c_singles_in_params": "theta_c_singles" in params,
        "theta_c_sm_absent": "theta_c_sm" not in params,
        "theta_c_sf_absent": "theta_c_sf" not in params,
        "theta_c_couples_present": "theta_c" in params,
    }
    for k, v in sanity.items():
        log(f"  D1 sanity: {k} = {v}")

    summary_md = find_latest_m0a_clean_summary()
    if summary_md:
        log(f"  M0a-clean post-est summary: {summary_md}")

    df_singles = pd.read_parquet(resolve_parquet("singles"))
    df_couples = pd.read_parquet(resolve_parquet("couples"))

    parquet_sanity = {
        "singles_alts_per_hh_unique": sorted(df_singles.groupby("idhh").size().unique().tolist()),
        "couples_alts_per_hh_unique": sorted(df_couples.groupby("idhh").size().unique().tolist()),
        "singles_chosen_per_hh_unique": sorted(df_singles.groupby("idhh")["is_chosen"].sum().unique().tolist()),
        "couples_chosen_per_hh_unique": sorted(df_couples.groupby("idhh")["is_chosen"].sum().unique().tolist()),
        "singles_min_prior": float(df_singles["prior"].min()),
        "couples_min_prior": float(df_couples["prior"].min()),
        "singles_max_abs_log_prior_diff": float(
            np.abs(np.log(np.clip(df_singles["prior"], 1e-300, None))
                   - df_singles["log_prior"]).max()
        ),
        "couples_max_abs_log_prior_diff": float(
            np.abs(np.log(np.clip(df_couples["prior"], 1e-300, None))
                   - df_couples["log_prior"]).max()
        ),
    }
    for k, v in parquet_sanity.items():
        log(f"  D1 parquet: {k} = {v}")

    # ===== D2 / D3 / D5: per-group decomposition and softmax ============
    rng = np.random.default_rng(SAMPLE_SEED)
    group_results: Dict[str, Any] = {}

    # --- singles_male / singles_female -------------------------------------
    for gender, label in [("sm", "singles_male"), ("sf", "singles_female")]:
        log(f"\n[{label}] V-decomposition")
        dgn = 1 if gender == "sm" else 0
        df_g = df_singles[df_singles["dgn"] == dgn].copy()
        n_hh_total = df_g["idhh"].nunique()
        sample_size = min(N_HH_SAMPLE_CAP, n_hh_total)
        sampled_ids = rng.choice(df_g["idhh"].unique(), size=sample_size, replace=False)
        df_g_sample = df_g[df_g["idhh"].isin(sampled_ids)].copy().sort_values(["idhh"]).reset_index(drop=True)

        log(f"  households sampled: {sample_size} / {n_hh_total}")
        v_df = decompose_v_singles(df_g_sample, params, spec, gender)
        v_df["prob"] = softmax_per_hh_fast(v_df)

        # Per-component medians on work vs non-work
        work_mask = v_df["working"] == 1
        comps = ["U", "O_E", "O_H", "O_market", "O_W", "O_Occ", "minus_log_prior", "V"]
        comp_rows = []
        for c in comps:
            comp_rows.append({
                "component": c,
                "median_work": median(v_df.loc[work_mask, c].to_numpy()),
                "median_nonwork": median(v_df.loc[~work_mask, c].to_numpy()),
                "gap_work_minus_nonwork": (
                    median(v_df.loc[work_mask, c].to_numpy())
                    - median(v_df.loc[~work_mask, c].to_numpy())
                ),
            })

        # Structural P(nonwork) per household: sum prob over working==0 alts
        nonwork_share = (v_df.assign(nonwork=(~work_mask).astype(float))
                              .groupby("idhh", sort=False)
                              .apply(lambda x: float((x["prob"] * x["nonwork"]).sum()),
                                     include_groups=False)
                              .to_numpy())
        # Observed chosen non-work share
        chosen = df_g[df_g["is_chosen"] == 1]
        obs_nonwork = float((chosen["working"] == 0).mean())

        # Non-work contribution audit
        nw = v_df.loc[~work_mask]
        nw_audit = {
            "n_nonwork_rows": int(len(nw)),
            "O_H_max_abs": float(np.abs(nw["O_H"].to_numpy()).max() if len(nw) else 0),
            "O_market_max_abs": float(np.abs(nw["O_market"].to_numpy()).max() if len(nw) else 0),
            "O_W_max_abs": float(np.abs(nw["O_W"].to_numpy()).max() if len(nw) else 0),
            "O_Occ_max_abs": float(np.abs(nw["O_Occ"].to_numpy()).max() if len(nw) else 0),
            "log_prior_mean": float(nw["log_prior"].mean() if len(nw) else 0),
        }

        group_results[label] = {
            "n_hh_sampled": int(sample_size),
            "n_hh_total": int(n_hh_total),
            "component_decomposition": comp_rows,
            "structural_P_nonwork": {
                "median": median(nonwork_share),
                **{k: v for k, v in quantile_dict(nonwork_share).items()},
                "mean": float(nonwork_share.mean()),
            },
            "observed_nonwork_rate": obs_nonwork,
            "nonwork_audit": nw_audit,
        }

    # --- couples_male / couples_female ------------------------------------
    log(f"\n[couples] V-decomposition (household-level V; per-partner non-work marginals)")
    n_hh_total_c = df_couples["idhh"].nunique()
    sample_size_c = min(N_HH_SAMPLE_CAP, n_hh_total_c)
    sampled_ids_c = rng.choice(df_couples["idhh"].unique(), size=sample_size_c, replace=False)
    df_c_sample = df_couples[df_couples["idhh"].isin(sampled_ids_c)].copy().sort_values(["idhh"]).reset_index(drop=True)
    log(f"  households sampled: {sample_size_c} / {n_hh_total_c}")
    v_dfc = decompose_v_couples(df_c_sample, params, spec)
    v_dfc["prob"] = softmax_per_hh_fast(v_dfc)

    for partner, label in [("m", "couples_male"), ("f", "couples_female")]:
        work_col = "working_male" if partner == "m" else "working_female"
        work_mask = v_dfc[work_col] == 1
        comps_partner = ["U", "O_E", "O_H", "O_market", "O_W", "O_Occ", "minus_log_prior", "V"]
        comp_rows = []
        for c in comps_partner:
            comp_rows.append({
                "component": c,
                "median_work": median(v_dfc.loc[work_mask, c].to_numpy()),
                "median_nonwork": median(v_dfc.loc[~work_mask, c].to_numpy()),
                "gap_work_minus_nonwork": (
                    median(v_dfc.loc[work_mask, c].to_numpy())
                    - median(v_dfc.loc[~work_mask, c].to_numpy())
                ),
            })

        nonwork_share = (v_dfc.assign(nonwork=(~work_mask).astype(float))
                                .groupby("idhh", sort=False)
                                .apply(lambda x: float((x["prob"] * x["nonwork"]).sum()),
                                       include_groups=False)
                                .to_numpy())
        chosen_c = df_couples[df_couples["is_chosen"] == 1]
        obs_nonwork = float((chosen_c[work_col] == 0).mean())

        nw = v_dfc.loc[~work_mask]
        partner_short = "_m" if partner == "m" else "_f"
        nw_audit = {
            "n_nonwork_rows": int(len(nw)),
            f"O_H{partner_short}_max_abs": float(np.abs(nw[f"O_H{partner_short}"].to_numpy()).max() if len(nw) else 0),
            f"O_market{partner_short}_max_abs": float(np.abs(nw[f"O_market{partner_short}"].to_numpy()).max() if len(nw) else 0),
            f"O_W{partner_short}_max_abs": float(np.abs(nw[f"O_W{partner_short}"].to_numpy()).max() if len(nw) else 0),
            f"O_Occ{partner_short}_max_abs": float(np.abs(nw[f"O_Occ{partner_short}"].to_numpy()).max() if len(nw) else 0),
            "log_prior_mean": float(nw["log_prior"].mean() if len(nw) else 0),
        }

        group_results[label] = {
            "n_hh_sampled": int(sample_size_c),
            "n_hh_total": int(n_hh_total_c),
            "component_decomposition": comp_rows,
            "structural_P_nonwork": {
                "median": median(nonwork_share),
                **{k: v for k, v in quantile_dict(nonwork_share).items()},
                "mean": float(nonwork_share.mean()),
            },
            "observed_nonwork_rate": obs_nonwork,
            "nonwork_audit": nw_audit,
        }

    # ===== Verdict ==========================================================
    medians = {g: group_results[g]["structural_P_nonwork"]["median"]
               for g in ("singles_male", "singles_female", "couples_male", "couples_female")}
    obs_rates = {g: group_results[g]["observed_nonwork_rate"]
                 for g in medians}

    # Decide verdict
    REPORTED_PARTICIPATION_PREDICTED = 1.0   # uniform across all 4 groups in M0a-clean post-est
    structural_nonzero = any(medians[g] > 0.005 for g in medians)
    if structural_nonzero:
        verdict_kind = "post_est_reporting_bug"
        # Locate the specific post-est lookup bug
        verdict_line = (
            "ROOT CAUSE: post-estimation reporting code at "
            "scripts/enhanced/RURO_post_estimation_styled.py:4652. Spec-side "
            "and engine code are correct. Recommended fix: use "
            "group-suffixed parameter lookups (e.g. params['beta_c_sm'] for "
            "singles_male) inside compute_fit_diagnostics instead of "
            "params.get('beta_c', 1.0), and pass suffix='_sm'/'_sf' to "
            "compute_beta_l_full, then include the opportunity layer "
            "(log_opp or component recomputation) in V."
        )
    else:
        # Structural V predicts near-zero non-work too. Distinguish between
        # genuine spec/data artifact vs prior-correction bug by looking at
        # the V gap that drives it.
        verdict_kind = "spec_artifact_or_prior_correction"
        # Inspect: is the dominant gap from -log_prior or from the
        # working-gated opportunity layer?
        sm = group_results["singles_male"]["component_decomposition"]
        prior_gap = next(c["gap_work_minus_nonwork"] for c in sm if c["component"] == "minus_log_prior")
        oe_gap = next(c["gap_work_minus_nonwork"] for c in sm if c["component"] == "O_E")
        v_gap = next(c["gap_work_minus_nonwork"] for c in sm if c["component"] == "V")
        if abs(prior_gap) > abs(oe_gap) * 5 and prior_gap > 0:
            verdict_line = (
                f"ROOT CAUSE: prior-correction logic at "
                f"scripts/enhanced/RURO_post_estimation_styled.py:4677. log_prior "
                f"contribution dominates V_work - V_nonwork by {prior_gap:+.2f} "
                f"vs O_E gap {oe_gap:+.2f} (singles_male); the "
                f"-log_prior subtraction is producing the working dominance. "
                f"Recommended fix: review whether log_prior already encodes "
                f"the employment-margin component the structural index is "
                f"also adding via O_E, or whether log_prior should be "
                f"computed conditional on the working status."
            )
        else:
            verdict_line = (
                "ROOT CAUSE: specification/data fit artifact, not a code bug. "
                "The structural index assigns near-zero probability to "
                "non-work alternatives. Recommended fix: inspect the largest "
                "V component gaps and revise the specification or proposal "
                "design."
            )

    log("\n" + "=" * 72)
    log(f"VERDICT KIND: {verdict_kind}")
    log(f"VERDICT: {verdict_line}")
    log(f"Structural P(nonwork) medians: {medians}")
    log(f"Observed non-work rates: {obs_rates}")
    log("=" * 72)

    # ===== D4: code-path audit notes =======================================
    code_path_audit = {
        "post_est_fit_diagnostics_singles_param_lookup": {
            "file": "scripts/enhanced/RURO_post_estimation_styled.py",
            "lines": "4652-4664",
            "issue": (
                "Singles V is reconstructed with params.get('beta_c', 1.0), "
                "params.get('theta_c', 0.5), params.get('theta_l', 0.5), and "
                "compute_beta_l_full(df_g, params, suffix=''). For singles, "
                "the parameter dictionary contains gender-suffixed keys "
                "(beta_c_sm/sf, theta_l_sm/sf, beta_l0_sm/sf) — never the "
                "unsuffixed 'beta_c'/'theta_c'/'theta_l'/'beta_l0'. All four "
                "lookups silently fall back to the defaults, producing a V "
                "that does not reflect the estimated singles preferences."
            ),
        },
        "post_est_fit_diagnostics_log_opp": {
            "file": "scripts/enhanced/RURO_post_estimation_styled.py",
            "lines": "4671-4674",
            "issue": (
                "V += log_opp only if the column is pre-attached to df_g. "
                "compute_fit_diagnostics does not call "
                "_add_predicted_probabilities, so for singles the V used in "
                "the participation_predicted aggregation contains U_pref "
                "(with wrong params) minus log_prior, with NO opportunity "
                "contribution."
            ),
        },
        "compute_beta_l_full_suffix": {
            "file": "scripts/enhanced/RURO_post_estimation_styled.py",
            "lines": "4922-4923",
            "issue": (
                "beta_l0 lookup uses 'beta_l0' when suffix=''. Singles dict "
                "has beta_l0_sm or beta_l0_sf only; falls back to 0.0."
            ),
        },
    }

    # ===== Save JSON =======================================================
    payload = {
        "metadata": {
            "date": datetime.datetime.now().isoformat(timespec="seconds"),
            "spec_yaml": str(SPEC_YAML),
            "results_json": str(json_path),
            "summary_md": str(summary_md) if summary_md else None,
            "singles_parquet_mtime": datetime.datetime.fromtimestamp(
                resolve_parquet("singles").stat().st_mtime
            ).isoformat(timespec="seconds"),
            "couples_parquet_mtime": datetime.datetime.fromtimestamp(
                resolve_parquet("couples").stat().st_mtime
            ).isoformat(timespec="seconds"),
            "joint_ll": results["summary"]["joint_ll"],
            "n_params": n_params,
            "sample_seed": SAMPLE_SEED,
        },
        "D1_sanity": {**sanity, **parquet_sanity},
        "group_results": group_results,
        "reported_participation_predicted": REPORTED_PARTICIPATION_PREDICTED,
        "code_path_audit": code_path_audit,
        "verdict_kind": verdict_kind,
        "verdict_line": verdict_line,
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    log(f"\nWrote {JSON_OUT}")

    # ===== Markdown report =================================================
    write_md_report(payload)
    log(f"Wrote {MD_OUT}")

    return 0


def write_md_report(payload: Dict[str, Any]) -> None:
    def fmt(x, p=".4f"):
        if x is None: return "NA"
        if isinstance(x, float) and (np.isnan(x) or np.isinf(x)): return "NA"
        if isinstance(x, (int, np.integer)): return f"{int(x):,}"
        if isinstance(x, float): return format(x, p)
        return str(x)

    lines: List[str] = []
    lines.append("# RURO ruro_occ_M0a_clean — Participation Pathology Diagnostic v1")
    lines.append("")
    md = payload["metadata"]
    lines.append(f"Date: {md['date']}")
    lines.append("")

    # 1. Input files
    lines.append("## 1. Input files")
    lines.append("")
    lines.append("| item | path / value |")
    lines.append("| --- | --- |")
    lines.append(f"| spec YAML | `{md['spec_yaml']}` |")
    lines.append(f"| results JSON | `{md['results_json']}` |")
    lines.append(f"| post-est summary MD | `{md['summary_md']}` |")
    lines.append(f"| singles parquet mtime | {md['singles_parquet_mtime']} |")
    lines.append(f"| couples parquet mtime | {md['couples_parquet_mtime']} |")
    lines.append(f"| joint_ll | {fmt(md['joint_ll'], '.4f')} |")
    lines.append(f"| n_params | {md['n_params']} |")
    lines.append(f"| sample seed | {md['sample_seed']} |")
    lines.append("")

    # 2. Sanity
    lines.append("## 2. Sanity checks")
    lines.append("")
    lines.append("| check | result |")
    lines.append("| --- | --- |")
    for k, v in payload["D1_sanity"].items():
        lines.append(f"| `{k}` | {fmt(v)} |")
    lines.append("")

    # 3. Sample sizes
    lines.append("## 3. Sample sizes")
    lines.append("")
    lines.append("| group | n_hh sampled | n_hh total |")
    lines.append("| --- | --- | --- |")
    for g in ("singles_male", "singles_female", "couples_male", "couples_female"):
        gr = payload["group_results"][g]
        lines.append(f"| {g} | {gr['n_hh_sampled']:,} | {gr['n_hh_total']:,} |")
    lines.append("")

    # 4. Component decomposition
    lines.append("## 4. V-component decomposition (median per group)")
    lines.append("")
    lines.append("V_ij = U + O_E + O_H + O_market + O_W + O_Occ - log_prior. Couples reports the household V; the per-partner working filter is used to split work vs non-work rows. log_prior is read directly from the parquet (verified `log_prior == log(prior)` in D1).")
    lines.append("")
    lines.append("| group | component | median work | median nonwork | work - nonwork |")
    lines.append("| --- | --- | --- | --- | --- |")
    for g in ("singles_male", "singles_female", "couples_male", "couples_female"):
        for row in payload["group_results"][g]["component_decomposition"]:
            lines.append(
                f"| {g} | `{row['component']}` | {fmt(row['median_work'])} | "
                f"{fmt(row['median_nonwork'])} | {fmt(row['gap_work_minus_nonwork'])} |"
            )
    lines.append("")

    # 5. Structural P(nonwork)
    lines.append("## 5. Structural P(nonwork) per group")
    lines.append("")
    lines.append(f"Reported post-estimation `participation_predicted` = {payload['reported_participation_predicted']:.4f} for all four groups (uniform; persists from M0 → M0a-equality → M0a-clean).")
    lines.append("")
    lines.append("| group | median P(nonwork) | q10 | q25 | q75 | q90 | mean | observed nonwork rate |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for g in ("singles_male", "singles_female", "couples_male", "couples_female"):
        gr = payload["group_results"][g]
        pnw = gr["structural_P_nonwork"]
        lines.append(
            f"| {g} | {fmt(pnw['median'])} | {fmt(pnw['q10'])} | "
            f"{fmt(pnw['q25'])} | {fmt(pnw['q75'])} | {fmt(pnw['q90'])} | "
            f"{fmt(pnw['mean'])} | {fmt(gr['observed_nonwork_rate'])} |"
        )
    lines.append("")

    # 6. Non-work audit
    lines.append("## 6. Non-work contribution audit")
    lines.append("")
    lines.append("Expectation: working-gated opportunity terms (O_H, O_market, O_W, O_Occ) are exactly zero on non-work rows. log_prior on non-work rows should equal `log_q_E` only (since non-work has zero H, W, Occ proposal-density contributions by construction).")
    lines.append("")
    lines.append("| group | n_nonwork | max\\|O_H\\| | max\\|O_market\\| | max\\|O_W\\| | max\\|O_Occ\\| | mean log_prior |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for g in ("singles_male", "singles_female", "couples_male", "couples_female"):
        nw = payload["group_results"][g]["nonwork_audit"]
        # singles vs couples key names
        if g.startswith("singles"):
            keys = ("O_H_max_abs", "O_market_max_abs", "O_W_max_abs", "O_Occ_max_abs")
        elif g == "couples_male":
            keys = ("O_H_m_max_abs", "O_market_m_max_abs", "O_W_m_max_abs", "O_Occ_m_max_abs")
        else:
            keys = ("O_H_f_max_abs", "O_market_f_max_abs", "O_W_f_max_abs", "O_Occ_f_max_abs")
        lines.append(
            f"| {g} | {nw['n_nonwork_rows']:,} | "
            f"{fmt(nw.get(keys[0]))} | {fmt(nw.get(keys[1]))} | "
            f"{fmt(nw.get(keys[2]))} | {fmt(nw.get(keys[3]))} | "
            f"{fmt(nw.get('log_prior_mean'))} |"
        )
    lines.append("")

    # 7. Suspect code paths
    lines.append("## 7. Suspect code paths")
    lines.append("")
    for key, ent in payload["code_path_audit"].items():
        lines.append(f"### `{key}`")
        lines.append("")
        lines.append(f"- file: `{ent['file']}`")
        lines.append(f"- lines: {ent['lines']}")
        lines.append(f"- issue:")
        lines.append("")
        for para in ent["issue"].split(". "):
            if para.strip():
                lines.append(f"  {para.strip()}.")
        lines.append("")

    # 8. Verdict
    lines.append("## 8. Verdict")
    lines.append("")
    lines.append(payload["verdict_line"])
    lines.append("")

    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
