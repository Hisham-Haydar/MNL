#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-12-01 16:17:45
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Dict, Optional

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

# ---- GSUR (Group-Specific Unemployment Rate) --------------------------------
# Default path to GSUR lookup table (France)
DEFAULT_GSUR_PATH = Path(__file__).resolve().parent.parent / "Data" / "external" / "FR_gsur_ruro.parquet"


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
    df.to_csv(out_csv, index=False)
    return {"parquet": out_parquet, "csv": out_csv}


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
    df = df.copy()

    for col in ("lma", "dgn", "hours", "loc"):
        if col not in df.columns:
            raise KeyError(f"RURO dataset must contain '{col}' before computing the prior.")

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

    pi0 = np.zeros(len(df), dtype=float)
    active = lma > 0
    mask_m = active & (dgn == 1)
    mask_f = active & (dgn == 0)

    pi0[mask_m.to_numpy()] = pi0_m
    pi0[mask_f.to_numpy()] = pi0_f
    df["pi0"] = pi0

    h_support = max(h_max - h_min, DCM_MIN_POSITIVE)
    w_support = max(w_max - w_min, DCM_MIN_POSITIVE)

    hours_zero = hours <= 0
    hours_pos = ~hours_zero

    loc_pos = pd.to_numeric(df.loc[hours_pos, "loc"], errors="coerce").dropna().unique()
    loc_support = float(len(loc_pos))
    if loc_support <= 0:
        loc_support = 1.0
        LOGGER.warning(
            "No non-missing loc values among positive-hour jobs; "
            "treating loc_support as 1."
        )

    prior_density = np.empty(len(df), dtype=float)

    if wage_spec == "fw":
        prior_density[hours_zero.to_numpy()] = pi0[hours_zero.to_numpy()]
        prior_density[hours_pos.to_numpy()] = (
            (1.0 - pi0[hours_pos.to_numpy()])
            * (1.0 / h_support)
            * (1.0 / loc_support)
        )
    elif wage_spec == "vw":
        prior_density[hours_zero.to_numpy()] = pi0[hours_zero.to_numpy()]
        prior_density[hours_pos.to_numpy()] = (
            (1.0 - pi0[hours_pos.to_numpy()])
            * (1.0 / h_support)
            * (1.0 / w_support)
            * (1.0 / loc_support)
        )
    else:
        raise ValueError("wage_spec must be 'fw' or 'vw'.")

    prior_density = np.clip(prior_density, 1e-16, None)
    df["prior"] = np.log(prior_density)

    return df


def merge_gsur(
    df: pd.DataFrame,
    gsur_path: Optional[Path] = None,
    year: Optional[int] = None,
) -> pd.DataFrame:
    """
    Merge group-specific unemployment rate (GSUR) onto individuals.
    
    GSUR is used as a regressor in the hours opportunity density to capture
    labor market conditions for each demographic group. It does NOT affect draws.
    
    Matching is done on: (year, drgn1, dgn, education_level)
    
    Following Stijn Van Houtven's approach:
    - GSUR varies by sex (dgn), age group, education level, region, and year
    - In the hours opportunity: hopp = ... + β_gsur * working * gsur + ...
    
    Parameters
    ----------
    df : pd.DataFrame
        MNL dataset with columns: dgn, deh (or educL/educH), drgn1, year (optional)
    gsur_path : Path, optional
        Path to GSUR lookup table (parquet). Defaults to FR_gsur_ruro.parquet.
    year : int, optional
        Data year for filtering GSUR. If None, tries to extract from df['year'].
    
    Returns
    -------
    pd.DataFrame
        Input dataframe with added 'gsur' column (unemployment rate as proportion).
    """
    if gsur_path is None:
        gsur_path = DEFAULT_GSUR_PATH
    
    gsur_path = Path(gsur_path)
    if not gsur_path.exists():
        LOGGER.warning(f"GSUR file not found at {gsur_path}; gsur will be set to 0.")
        df = df.copy()
        df["gsur"] = 0.0
        return df
    
    # Load GSUR lookup
    gsur_df = pd.read_parquet(gsur_path)
    LOGGER.info(f"Loaded GSUR lookup with {len(gsur_df)} rows from {gsur_path.name}")
    
    # Determine year
    if year is None:
        if "year" in df.columns:
            year = int(df["year"].mode().iloc[0])
        else:
            # Default to most recent year in GSUR data
            year = int(gsur_df["year"].max())
            LOGGER.warning(f"No year specified; using most recent GSUR year: {year}")
    
    # Filter GSUR to relevant year
    gsur_year = gsur_df[gsur_df["year"] == year].copy()
    if gsur_year.empty:
        # Try closest year
        available_years = sorted(gsur_df["year"].unique())
        closest_year = min(available_years, key=lambda y: abs(y - year))
        LOGGER.warning(f"No GSUR data for year {year}; using {closest_year}")
        gsur_year = gsur_df[gsur_df["year"] == closest_year].copy()
    
    df = df.copy()
    
    # Create education category in main df
    # educL = ED0-2 (low), educM = ED3_4 (medium), educH = ED5-8 (high)
    if "educL" in df.columns and "educH" in df.columns:
        educL = pd.to_numeric(df["educL"], errors="coerce").fillna(0)
        educH = pd.to_numeric(df["educH"], errors="coerce").fillna(0)
        df["_educ_cat"] = np.where(
            educL == 1, "ED0-2",
            np.where(educH == 1, "ED5-8", "ED3_4")
        )
    elif "deh" in df.columns:
        deh = pd.to_numeric(df["deh"], errors="coerce").fillna(3)
        df["_educ_cat"] = np.where(
            deh.isin([0, 1, 2]), "ED0-2",
            np.where(deh == 5, "ED5-8", "ED3_4")
        )
    else:
        LOGGER.warning("No education variable (educL/educH or deh); using TOTAL gsur.")
        df["_educ_cat"] = "TOTAL"
    
    # Ensure dgn exists
    if "dgn" not in df.columns:
        LOGGER.warning("No 'dgn' column; assuming all males (dgn=1).")
        df["dgn"] = 1
    
    # Ensure drgn1 exists (region)
    if "drgn1" not in df.columns:
        LOGGER.warning("No 'drgn1' column; using national average (drgn1=0).")
        df["drgn1"] = 0
    
    dgn = pd.to_numeric(df["dgn"], errors="coerce").fillna(1).astype(int)
    drgn1 = pd.to_numeric(df["drgn1"], errors="coerce").fillna(0).astype(int)
    
    # Prepare GSUR for merging (exclude TOTAL education for now)
    gsur_merge = gsur_year[gsur_year["education"] != "TOTAL"][
        ["drgn1", "dgn", "education", "gsur"]
    ].copy()
    
    # Merge GSUR onto df
    n_before = len(df)
    df = df.merge(
        gsur_merge,
        left_on=["drgn1", "dgn", "_educ_cat"],
        right_on=["drgn1", "dgn", "education"],
        how="left",
        suffixes=("", "_gsur")
    )
    
    # Fill missing gsur with national average for same sex/education
    missing_mask = df["gsur"].isna()
    if missing_mask.any():
        n_missing = missing_mask.sum()
        LOGGER.info(f"Filling {n_missing} missing gsur values with national average...")
        
        # Get national averages (drgn1 == 0)
        national_gsur = gsur_year[
            (gsur_year["drgn1"] == 0) & (gsur_year["education"] != "TOTAL")
        ].set_index(["dgn", "education"])["gsur"].to_dict()
        
        # Fill missing values
        for idx in df[missing_mask].index:
            key = (int(df.loc[idx, "dgn"]), df.loc[idx, "_educ_cat"])
            if key in national_gsur:
                df.loc[idx, "gsur"] = national_gsur[key]
            else:
                # Ultimate fallback: overall average
                df.loc[idx, "gsur"] = gsur_year["gsur"].mean()
    
    # Clean up temporary columns
    df = df.drop(columns=["_educ_cat", "education"], errors="ignore")
    
    # Ensure gsur is float and fill any remaining NaN
    df["gsur"] = pd.to_numeric(df["gsur"], errors="coerce").fillna(0.0)
    
    LOGGER.info(f"GSUR merged: mean={df['gsur'].mean():.4f}, range=[{df['gsur'].min():.4f}, {df['gsur'].max():.4f}]")
    
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
    ap.add_argument(
        "--gsur-file",
        type=str,
        default=None,
        help="Path to GSUR lookup table (parquet). If not provided, uses default FR_gsur_ruro.parquet.",
    )
    ap.add_argument(
        "--year",
        type=int,
        default=None,
        help="Data year for GSUR lookup. If not provided, extracted from data or uses most recent.",
    )
    ap.add_argument(
        "--no-gsur",
        action="store_true",
        help="Skip GSUR merge (gsur column will be 0).",
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
    singles_mnl = _build_mnl_block(singles_long, sample_group="singles")

    frames = [singles_mnl]

    if args.couples_draws:
        couples_path = Path(args.couples_draws).resolve()
        if not couples_path.exists():
            raise FileNotFoundError(f"Couples draws file not found: {couples_path}")
        couples_long = _read_df(couples_path)
        couples_long = _merge_euromod_outputs(couples_long, em_df)
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

    # Merge GSUR (group-specific unemployment rate) for estimation
    # GSUR is used as a regressor in hours opportunity density, NOT in draws/prior
    if not args.no_gsur:
        gsur_path = Path(args.gsur_file) if args.gsur_file else None
        full_mnl = merge_gsur(full_mnl, gsur_path=gsur_path, year=args.year)
    else:
        full_mnl["gsur"] = 0.0
        LOGGER.info("GSUR merge skipped (--no-gsur flag); gsur set to 0.")

    out_base = Path(args.out_base).resolve()
    outputs = _write_df(full_mnl, out_base)
    print("MNL dataset written to:")
    for k, v in outputs.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
