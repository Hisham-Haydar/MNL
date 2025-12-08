#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-12-01 16:17:45
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)

TOTAL_LEISURE_HOURS = 80.0
WEEKS_PER_MONTH = 52.0 / 12.0
DCM_MIN_POSITIVE = 1e-6

# ---- Prior parameters (aligned with RURO_draws.py defaults) ----------------
DEFAULT_PI0_M = 0.10
DEFAULT_PI0_F = 0.10
DEFAULT_H_MIN = 1.0
DEFAULT_H_MAX = 70.0
DEFAULT_W_MIN = 1.0
DEFAULT_W_MAX = 120.0
DEFAULT_WAGE_SPEC = "vw"


def _read_df(path: Path) -> pd.DataFrame:
    suf = path.suffix.lower()
    if suf == ".parquet":
        return pd.read_parquet(path)  # type: ignore[arg-type]
    if suf == ".csv":
        return pd.read_csv(path)
    if suf in {".pkl", ".pickle"}:
        return pd.read_pickle(path)
    raise ValueError(f"Unsupported format for {path}")


def _write_df(df: pd.DataFrame, base: Path) -> Dict[str, Path]:
    out_parquet = base.with_suffix(".parquet")
    out_csv = base.with_suffix(".csv")
    df.to_parquet(out_parquet, index=False)  # type: ignore[arg-type]
    # Skip the CSV export for now; parquet output is sufficient for the pipeline.
    # df.to_csv(out_csv, index=False)
    return {"parquet": out_parquet}


def _merge_euromod_outputs(long_df: pd.DataFrame, em_df: pd.DataFrame) -> pd.DataFrame:
    if "idperson" not in long_df.columns or "draw" not in long_df.columns:
        raise KeyError("long_df must contain 'idperson' and 'draw'.")
    if "idperson_true" not in em_df.columns or "draw" not in em_df.columns:
        raise KeyError("EUROMOD combined df must contain 'idperson_true' and 'draw'.")

    merged = long_df.merge(
        em_df,
        left_on=["idperson", "draw"],
        right_on=["idperson_true", "draw"],
        how="left",
        suffixes=("", "_em"),
    )

    if merged["ils_dispy"].isna().any():
        missing = merged[merged["ils_dispy"].isna()][["idperson", "draw"]].head()
        raise ValueError(
            "Missing ils_dispy after merge; EUROMOD outputs did not align. "
            f"Example missing pairs: {missing.to_dict(orient='records')}"
        )

    if "idhh_true" in merged.columns:
        merged["idhh"] = merged["idhh_true"]

    drop_cols = [c for c in ["idperson_true", "idhh_true"] if c in merged.columns]
    merged = merged.drop(columns=drop_cols)
    return merged


def _restrict_to_deciders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Restrict the RURO long dataset to *deciders* only.

    Priority of definitions:
      1. If hh_IsHead or hh_IsPartner exist: deciders = heads or partners.
      2. Else if ruro_decider exists: deciders = 1{ruro_decider == 1}.
      3. Else if lma exists: deciders = 1{lma == 1}.
      4. Else: return df unchanged (with a warning).

    Non-deciders (children, other adults) are needed for EUROMOD but must be
    dropped from the MNL estimation sample.
    """
    df = df.copy()

    # 1) Head/partner flags (preferred definition)
    has_head = "hh_IsHead" in df.columns
    has_partner = "hh_IsPartner" in df.columns
    if has_head or has_partner:
        head = df["hh_IsHead"] if has_head else 0
        partner = df["hh_IsPartner"] if has_partner else 0
        decider_mask = (pd.to_numeric(head, errors="coerce").fillna(0).astype(int) == 1) | \
                       (pd.to_numeric(partner, errors="coerce").fillna(0).astype(int) == 1)
        out = df.loc[decider_mask].copy()
        logging.info(
            "Decider restriction: kept %d/%d rows using hh_IsHead/hh_IsPartner.",
            out.shape[0],
            df.shape[0],
        )
        return out

    # 2) ruro_decider flag
    if "ruro_decider" in df.columns:
        decider_flag = pd.to_numeric(df["ruro_decider"], errors="coerce").fillna(0).astype(int)
        decider_mask = decider_flag == 1
        out = df.loc[decider_mask].copy()
        logging.info(
            "Decider restriction: kept %d/%d rows using ruro_decider.",
            out.shape[0],
            df.shape[0],
        )
        return out

    # 3) lma as fallback (labour-market attached)
    if "lma" in df.columns:
        lma = pd.to_numeric(df["lma"], errors="coerce").fillna(0).astype(int)
        decider_mask = lma == 1
        out = df.loc[decider_mask].copy()
        logging.info(
            "Decider restriction: kept %d/%d rows using lma==1.",
            out.shape[0],
            df.shape[0],
        )
        return out

    # 4) Last resort: keep everyone, but warn
    logging.warning(
        "Decider restriction could not be applied: "
        "hh_IsHead/hh_IsPartner, ruro_decider, and lma are all missing. "
        "Proceeding with full sample."
    )
    return df


def _build_mnl_block(df: pd.DataFrame, sample_group: str) -> pd.DataFrame:
    df = df.copy()

    if "idperson" not in df.columns or "draw" not in df.columns or "is_chosen" not in df.columns:
        raise KeyError("Expected columns 'idperson', 'draw', 'is_chosen'.")
    if "ils_dispy" not in df.columns:
        raise KeyError("Expected EUROMOD disposable income 'ils_dispy' after merge.")

    hours = pd.to_numeric(df.get("hours", df.get("lhw")), errors="coerce").fillna(0.0)
    df["hours"] = hours

    leisure = TOTAL_LEISURE_HOURS - hours
    leisure = leisure.clip(lower=DCM_MIN_POSITIVE)
    df["leisure"] = leisure

    ils = pd.to_numeric(df["ils_dispy"], errors="coerce")
    other_raw = df["other_members_income"] if "other_members_income" in df.columns else pd.Series(0.0, index=df.index)
    other_inc = pd.to_numeric(other_raw, errors="coerce").fillna(0.0)
    ruro_group = pd.to_numeric(df.get("ruro_group", 0), errors="coerce").fillna(0)

    cons = ils.copy()

    singles_mask = ruro_group.eq(1)
    cons.loc[singles_mask] = ils.loc[singles_mask] + other_inc.loc[singles_mask]

    couples_mask = ruro_group.eq(10)
    if couples_mask.any() and "idhh" in df.columns:
        hh_total = (
            ils.groupby([df["idhh"], df["draw"]])
               .transform("sum")
        )
        cons.loc[couples_mask] = hh_total.loc[couples_mask]

    cons = cons.clip(lower=DCM_MIN_POSITIVE)
    df["consumption"] = cons

    df["log_c"] = np.log(cons)
    df["log_l"] = np.log(leisure)
    df["sample_group"] = sample_group

    # Education dummies from highest status (deh) if available
    if "deh" in df.columns:
        deh_num = pd.to_numeric(df["deh"], errors="coerce")
        df["educL"] = (deh_num.isin([0, 1, 2])).astype(int)
        df["educH"] = (deh_num == 5).astype(int)
        df["educM"] = (~df["educL"].astype(bool) & ~df["educH"].astype(bool)).astype(int)

    # Experience squared helper if not already present
    if "pexp_years" in df.columns and "pexp_years2" not in df.columns:
        pexp_num = pd.to_numeric(df["pexp_years"], errors="coerce").fillna(0.0)
        df["pexp_years2"] = pexp_num * pexp_num

    return df


def _build_loc_distribution(df: pd.DataFrame) -> Optional[Dict[Any, float]]:
    """
    Empirical distribution over loc among working observations (hours > 0 and lma == 1 if present).
    
    NOTE: This function is retained for possible future use but is NOT called in the current
    implementation. The RURO prior (following Stijn's implementation) depends only on hours
    and wages, not on occupation.
    """
    if "loc" not in df.columns:
        return None

    if "hours" in df.columns:
        hours = pd.to_numeric(df["hours"], errors="coerce").fillna(0.0)
    elif "lhw" in df.columns:
        hours = pd.to_numeric(df["lhw"], errors="coerce").fillna(0.0)
    else:
        return None

    mask = hours > 0
    if "lma" in df.columns:
        lma = pd.to_numeric(df["lma"], errors="coerce").fillna(0).astype(int)
        mask &= lma == 1

    if not mask.any():
        return None

    loc_series = pd.to_numeric(df.loc[mask, "loc"], errors="coerce")
    loc_series = loc_series[loc_series != -1]
    if loc_series.empty:
        return None

    counts = loc_series.value_counts(dropna=True)
    total = counts.sum()
    if total <= 0:
        return None

    return (counts / total).to_dict()


def _compute_prior(
    df: pd.DataFrame,
    *,
    wage_spec: str = DEFAULT_WAGE_SPEC,
    pi0_m: float = DEFAULT_PI0_M,
    pi0_f: float = DEFAULT_PI0_F,
    h_min: float = DEFAULT_H_MIN,
    h_max: float = DEFAULT_H_MAX,
    w_min: float = DEFAULT_W_MIN,
    w_max: float = DEFAULT_W_MAX,
) -> pd.DataFrame:
    """
    Compute the RURO prior (log-density) for each observation in the MNL dataset.
    
    The prior is a product of:
      - A discrete mass at zero hours (π₀, gender-specific)
      - A continuous uniform density over hours (if working)
      - A continuous uniform density over wages (if wage_spec="vw" and working)
    
    This exactly follows Stijn Van Houtven's `f_choicesets_est()` and matches the
    Aaberge–Colombino / Capeau–Decoster RURO methodology.
    
    **Importantly**: Occupation (`loc`) does NOT enter the prior. The opportunity
    density is over hours and wages only.
    
    For singles (ruro_group == 1):
        - If hours == 0: prior = π₀
        - If hours > 0 and wage_spec == "fw": prior = (1 - π₀) / (h_max - h_min)
        - If hours > 0 and wage_spec == "vw": prior = (1 - π₀) / [(h_max - h_min) * (w_max - w_min)]
    
    For couples (ruro_group == 10):
        - The joint prior is the product of male and female priors.
        - Uses hours_m, hours_f, wage_m, wage_f columns.
    
    Parameters
    ----------
    df : pd.DataFrame
        Long MNL dataset with columns: lma, dgn, hours, wage, ruro_group, and
        for couples: hours_m, hours_f, wage_m, wage_f.
    wage_spec : str
        "fw" for fixed wages, "vw" for variable wages.
    pi0_m, pi0_f : float
        Mass at zero hours for active men/women.
    h_min, h_max : float
        Bounds of hour support.
    w_min, w_max : float
        Bounds of wage support (used only if wage_spec == "vw").
    
    Returns
    -------
    pd.DataFrame
        Input dataframe with added column "prior" (log-prior).
    """
    df = df.copy()

    # Validate required columns (loc is NOT required)
    for col in ("lma", "dgn", "hours"):
        if col not in df.columns:
            raise KeyError(f"RURO dataset must contain '{col}' before computing the prior.")

    # Wage column
    if "wage" in df.columns:
        wage = pd.to_numeric(df["wage"], errors="coerce")
    elif "wage_ruro" in df.columns:
        wage = pd.to_numeric(df["wage_ruro"], errors="coerce")
    elif "yivwg" in df.columns:
        wage = pd.to_numeric(df["yivwg"], errors="coerce")
    else:
        raise KeyError("RURO dataset must contain 'wage', 'wage_ruro' or 'yivwg'.")
    df["wage"] = wage

    lma = pd.to_numeric(df["lma"], errors="coerce").fillna(0).astype(int)
    dgn = pd.to_numeric(df["dgn"], errors="coerce").fillna(1).astype(int)
    hours = pd.to_numeric(df["hours"], errors="coerce").fillna(0.0)

    # π₀ assignment (per-observation, gender-specific for active individuals)
    pi0 = np.zeros(len(df), dtype=float)
    active = lma > 0
    mask_m = active & (dgn == 1)
    mask_f = active & (dgn == 0)
    pi0[mask_m.to_numpy()] = pi0_m
    pi0[mask_f.to_numpy()] = pi0_f
    df["pi0"] = pi0

    # Validate hour/wage bounds
    h_range = h_max - h_min
    if h_range <= 0:
        raise ValueError("Invalid hours support for prior computation (h_max must exceed h_min).")
    w_range = w_max - w_min
    if wage_spec == "vw" and w_range <= 0:
        raise ValueError("Invalid wage support for prior computation (w_max must exceed w_min).")

    # Get ruro_group for singles vs couples logic
    ruro_group = pd.to_numeric(df.get("ruro_group", 1), errors="coerce").fillna(1).astype(int)
    
    # Initialize prior density array
    prior_density = np.empty(len(df), dtype=float)
    
    # -------------------------------------------------------------------------
    # Singles (ruro_group == 1): prior over individual hours and wages
    # -------------------------------------------------------------------------
    singles_mask = (ruro_group == 1).to_numpy()
    
    h_singles = hours.to_numpy()
    pi0_singles = pi0
    
    # Hours component
    prior_h_singles = np.where(
        h_singles <= 0,
        pi0_singles,
        (1.0 - pi0_singles) / h_range
    )
    
    if wage_spec == "fw":
        # Fixed wages: prior only over hours
        prior_density[singles_mask] = prior_h_singles[singles_mask]
    else:
        # Variable wages: hours × wage
        prior_w_singles = np.where(
            h_singles <= 0,
            1.0,  # when hours=0, wage is structurally 0; no wage density
            1.0 / w_range
        )
        prior_density[singles_mask] = (prior_h_singles * prior_w_singles)[singles_mask]
    
    # -------------------------------------------------------------------------
    # Couples (ruro_group == 10): joint prior = male prior × female prior
    # -------------------------------------------------------------------------
    couples_mask = (ruro_group == 10).to_numpy()
    
    if couples_mask.any():
        # For couples, we need hours_m, hours_f, wage_m, wage_f
        # If not present, fall back to per-person hours/wage (less accurate but functional)
        if "hours_m" in df.columns and "hours_f" in df.columns:
            h_m = pd.to_numeric(df["hours_m"], errors="coerce").fillna(0.0).to_numpy()
            h_f = pd.to_numeric(df["hours_f"], errors="coerce").fillna(0.0).to_numpy()
        else:
            # Fallback: use individual hours (couples data should have hours_m/hours_f)
            LOGGER.warning("Couples data missing hours_m/hours_f; using individual 'hours' column.")
            h_m = hours.to_numpy()
            h_f = hours.to_numpy()
        
        if "wage_m" in df.columns and "wage_f" in df.columns:
            w_m = pd.to_numeric(df["wage_m"], errors="coerce").fillna(0.0).to_numpy()
            w_f = pd.to_numeric(df["wage_f"], errors="coerce").fillna(0.0).to_numpy()
        else:
            LOGGER.warning("Couples data missing wage_m/wage_f; using individual 'wage' column.")
            w_m = wage.to_numpy()
            w_f = wage.to_numpy()
        
        # Male prior components
        prior_h_m = np.where(
            h_m <= 0,
            pi0_m,
            (1.0 - pi0_m) / h_range
        )
        
        # Female prior components
        prior_h_f = np.where(
            h_f <= 0,
            pi0_f,
            (1.0 - pi0_f) / h_range
        )
        
        if wage_spec == "fw":
            # Fixed wages: joint prior = prior_h_m × prior_h_f
            prior_density[couples_mask] = (prior_h_m * prior_h_f)[couples_mask]
        else:
            # Variable wages: include wage densities
            prior_w_m = np.where(h_m <= 0, 1.0, 1.0 / w_range)
            prior_w_f = np.where(h_f <= 0, 1.0, 1.0 / w_range)
            prior_density[couples_mask] = (
                prior_h_m * prior_w_m * prior_h_f * prior_w_f
            )[couples_mask]

    # Clip to avoid log(0) and take log
    prior_density = np.clip(prior_density, 1e-16, None)
    df["prior"] = np.log(prior_density)

    return df


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Prepare RURO MNL estimation dataset by merging draws with EUROMOD outputs."
    )
    ap.add_argument(
        "--singles-draws",
        type=str,
        required=True,
        help="Path to singles_RURO_ready_RURO_draws.parquet (or .csv, .pkl).",
    )
    ap.add_argument(
        "--couples-draws",
        type=str,
        required=False,
        help="Path to couples_RURO_ready_RURO_draws.parquet (optional).",
    )
    ap.add_argument(
        "--euromod-combined",
        type=str,
        required=True,
        help="Path to combined_draws_em.parquet (from RURO_euromod.py).",
    )
    ap.add_argument(
        "--out-base",
        type=str,
        required=True,
        help="Base path for output (without extension), e.g. fr_2021_RURO_mnl",
    )
    ap.add_argument(
        "--wage-spec",
        type=str,
        choices=["fw", "vw"],
        default=DEFAULT_WAGE_SPEC,
        help="Wage opportunity specification used for the prior: 'fw' fixed or 'vw' variable.",
    )
    ap.add_argument(
        "--pi0-m",
        type=float,
        default=DEFAULT_PI0_M,
        help="Mass at zero hours for active men.",
    )
    ap.add_argument(
        "--pi0-f",
        type=float,
        default=DEFAULT_PI0_F,
        help="Mass at zero hours for active women.",
    )
    ap.add_argument(
        "--h-min",
        type=float,
        default=DEFAULT_H_MIN,
        help="Lower bound of hour support for opportunities.",
    )
    ap.add_argument(
        "--h-max",
        type=float,
        default=DEFAULT_H_MAX,
        help="Upper bound of hour support for opportunities.",
    )
    ap.add_argument(
        "--w-min",
        type=float,
        default=DEFAULT_W_MIN,
        help="Lower bound of wage support for opportunities.",
    )
    ap.add_argument(
        "--w-max",
        type=float,
        default=DEFAULT_W_MAX,
        help="Upper bound of wage support for opportunities.",
    )
    return ap.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    args = parse_args()

    em_path = Path(args.euromod_combined).resolve()
    if not em_path.exists():
        raise FileNotFoundError(f"EUROMOD combined file not found: {em_path}")
    em_df = _read_df(em_path)

    singles_path = Path(args.singles_draws).resolve()
    if not singles_path.exists():
        raise FileNotFoundError(f"Singles draws file not found: {singles_path}")
    singles_long = _read_df(singles_path)
    singles_long = _merge_euromod_outputs(singles_long, em_df)

    # Keep only deciders (head/partner/lma==1) for estimation
    singles_long = _restrict_to_deciders(singles_long)

    singles_mnl = _build_mnl_block(singles_long, sample_group="singles")

    frames = [singles_mnl]

    if args.couples_draws:
        couples_path = Path(args.couples_draws).resolve()
        if not couples_path.exists():
            raise FileNotFoundError(f"Couples draws file not found: {couples_path}")
        couples_long = _read_df(couples_path)
        couples_long = _merge_euromod_outputs(couples_long, em_df)

        # Keep only deciders in couples (head/partner)
        couples_long = _restrict_to_deciders(couples_long)

        couples_mnl = _build_mnl_block(couples_long, sample_group="couples")
        frames.append(couples_mnl)

    full_mnl = pd.concat(frames, axis=0, ignore_index=True)

    if full_mnl[["idperson", "draw"]].isna().any().any():
        raise ValueError("Found NaNs in idperson/draw after merge; check EUROMOD alignment.")

    full_mnl = _compute_prior(
        full_mnl,
        wage_spec=args.wage_spec,
        pi0_m=args.pi0_m,
        pi0_f=args.pi0_f,
        h_min=args.h_min,
        h_max=args.h_max,
        w_min=args.w_min,
        w_max=args.w_max,
    )

    out_base = Path(args.out_base).resolve()
    outputs = _write_df(full_mnl, out_base)
    print("MNL dataset written to:")
    for k, v in outputs.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
