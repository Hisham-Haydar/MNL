#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-12-24 (Enhanced)
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/

"""
enh_RURO_prep_mnl_basic.py
==========================

Enhanced MNL dataset preparation for RURO estimation.

Integrates cleanly with enhanced pipeline:
    enh_france_data_prep.py → enh_RURO_prep.py → enh_RURO_draws.py →
    enh_RURO_euromod.py → enh_prepare_FR_gsur.py → enh_RURO_prep_mnl_basic.py →
    enh_RURO_estimate_FR.py (future)

Key enhancements:
    1. Drawsmeta integration: Prior parameters auto-aligned with draw generation
    2. Proper GSUR integration: External unemployment rates (not endogenous dummies)
    3. Consumption/leisure normalization: Pre-normalized for estimator stability
    4. Couples validation: Strict invariant checks to prevent corruption
    5. Split prior computation: Clean singles/couples separation
    6. Separate outputs: Singles/couples files + comprehensive metadata sidecar
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

# Add parent directory to path for sanity_checks import
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
except NameError:
    SCRIPT_DIR = Path.cwd()

from sanity_checks import sanity_report_mnl_dataset, sanity_report_couples_gender_balance  # type: ignore  # noqa: E402

LOGGER = logging.getLogger(__name__)

TOTAL_LEISURE_HOURS = 80.0
DCM_MIN_POSITIVE = 1.0  # Floor for consumption/leisure (matches R code: pmax(1, ils_dispy))

# ---- Prior parameters (will be overridden by drawsmeta if provided) ----------------
DEFAULT_PI0_M = 0.10
DEFAULT_PI0_F = 0.10
DEFAULT_H_MIN = 1.0
DEFAULT_H_MAX = 70.0
DEFAULT_W_MIN = 1.0
DEFAULT_W_MAX = 120.0
DEFAULT_WAGE_SPEC = "vw"


# =========================================================================
# UTILITY FUNCTIONS
# =========================================================================

def _read_df(path: Path) -> pd.DataFrame:
    """Read dataframe from parquet, CSV, or pickle."""
    suf = path.suffix.lower()
    if suf == ".parquet":
        return pd.read_parquet(path)  # type: ignore[arg-type]
    if suf == ".csv":
        return pd.read_csv(path)
    if suf in {".pkl", ".pickle"}:
        return pd.read_pickle(path)
    raise ValueError(f"Unsupported format for {path}")


def _coerce_binary_01(s: pd.Series, name: str) -> pd.Series:
    """
    Robustly coerce a binary indicator to {0,1}.
    Handles numeric, bool, and common string encodings.

    Args:
        s: Input series with binary indicator
        name: Name for logging purposes

    Returns:
        Series with values in {0, 1}
    """
    if s is None or len(s) == 0:
        return pd.Series(0, index=pd.RangeIndex(0), dtype="int8")

    x = s.copy()

    # If boolean dtype
    if x.dtype == bool:
        return x.astype("int8")

    # Try numeric first
    xn = pd.to_numeric(x, errors="coerce")
    if xn.notna().any():
        # Map any nonzero to 1, zeros to 0 (protect against 2, 9, etc.)
        out = (xn.fillna(0) != 0).astype("int8")
        return out

    # Fall back to strings
    xs = x.astype(str).str.strip().str.lower()
    true_set = {"1", "y", "yes", "true", "t", "attached", "active", "in", "ok"}
    false_set = {"0", "n", "no", "false", "f", "inactive", "out", "na", "nan", ""}

    out = pd.Series(0, index=x.index, dtype="int8")
    out.loc[xs.isin(true_set)] = 1
    out.loc[xs.isin(false_set)] = 0

    # Anything else stays 0 but we warn
    unknown = ~(xs.isin(true_set) | xs.isin(false_set))
    if unknown.any():
        vals = xs[unknown].value_counts().head(10).to_dict()
        logging.warning(f"[{name}] Unrecognized binary labels mapped to 0. Top labels: {vals}")

    return out


def _load_drawsmeta(path: Path) -> Dict[str, Any]:
    """Load draws metadata sidecar JSON."""
    if not path.exists():
        raise FileNotFoundError(f"Drawsmeta sidecar not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _ensure_year_column(df: pd.DataFrame) -> None:
    """
    Ensure 'year' column exists in DataFrame, deriving from fallback columns if needed.

    This helper consolidates duplicate year column normalization logic.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to modify in-place

    Raises
    ------
    KeyError
        If no year column can be derived

    Notes
    -----
    Modifies df in-place. Checks in order: year, year_for_ruro, data_year.
    """
    if "year" not in df.columns:
        if "year_for_ruro" in df.columns:
            df["year"] = df["year_for_ruro"]
        elif "data_year" in df.columns:
            df["year"] = df["data_year"]
        else:
            raise KeyError("GSUR merge requires 'year' column")


def _derive_educ3_from_deh(df: pd.DataFrame, deh_col: str = "deh", educ3_col: str = "educ3") -> None:
    """
    Derive educ3 (3-level education) from deh column if not present.

    This helper consolidates duplicate deh→educ3 conversion logic.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to modify in-place
    deh_col : str, default="deh"
        Source column name (detailed education harmonized)
    educ3_col : str, default="educ3"
        Target column name (3-level education)

    Raises
    ------
    KeyError
        If neither educ3_col nor deh_col exists

    Notes
    -----
    Modifies df in-place. Mapping: deh ∈ {0,1,2} → 0 (low), {3,4} → 1 (medium), 5 → 2 (high).
    """
    if educ3_col not in df.columns:
        if deh_col not in df.columns:
            raise KeyError(f"GSUR merge requires '{educ3_col}' or '{deh_col}'")

        deh = pd.to_numeric(df[deh_col], errors="coerce")
        # Map deh to educ3: 0-2=low(0), 3-4=medium(1), 5=high(2)
        educ3 = pd.Series(-1, index=df.index, dtype="Int64")
        educ3.loc[deh.isin([0, 1, 2])] = 0
        educ3.loc[deh.isin([3, 4])] = 1
        educ3.loc[deh == 5] = 2
        df[educ3_col] = educ3


def _standardize_gsur_age_group_column(gsur_df: pd.DataFrame) -> pd.DataFrame:
    """Ensure GSUR lookup exposes `age_group` when possible."""
    out = gsur_df.copy()
    if "age_group" not in out.columns and "age_group_used" in out.columns:
        out["age_group"] = out["age_group_used"]
    return out


def _map_age_to_gsur_group(age_series: pd.Series) -> pd.Series:
    """Map numeric age to GSUR age-group labels used in FR_gsur files."""
    age = pd.to_numeric(age_series, errors="coerce")
    group = pd.Series("Y20-64", index=age.index, dtype="object")  # Full-bracket fallback

    group.loc[age < 25] = "Y15-24"
    group.loc[(age >= 25) & (age < 35)] = "Y25-34"
    group.loc[(age >= 35) & (age < 45)] = "Y35-44"
    group.loc[(age >= 45) & (age < 55)] = "Y45-54"
    group.loc[(age >= 55) & (age < 65)] = "Y55-64"
    return group


def _pick_gsur_full_age_fallback(available_age_groups: pd.Series) -> Optional[str]:
    """Pick fallback full age bracket from available GSUR age-group labels."""
    available = set(pd.Series(available_age_groups).dropna().astype(str).unique())
    for candidate in ["Y20-64", "Y15-74", "Y_GE15", "Y_GE25"]:
        if candidate in available:
            return candidate
    return None


def _apply_decider_filter_couples(
    df: pd.DataFrame,
    decider_mask: pd.Series,
    filter_name: str
) -> pd.DataFrame:
    """
    Apply decider filtering for couples data at household-draw level.

    This helper consolidates duplicate couples filtering logic across multiple fallback branches.

    Parameters
    ----------
    df : pd.DataFrame
        Couples DataFrame with idhh and draw columns
    decider_mask : pd.Series
        Boolean mask indicating decider rows
    filter_name : str
        Name of filter being applied (for logging)

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame containing only household-draws with at least one decider

    Notes
    -----
    For couples, we filter at household-draw level: if a household-draw contains at least one
    decider, we keep all members of that household-draw (needed for joint estimation).
    """
    decider_hh_draws = df.loc[decider_mask, ["idhh", "draw"]].drop_duplicates()
    out = df.merge(decider_hh_draws, on=["idhh", "draw"], how="inner")
    logging.info(
        f"Decider restriction (couples, household-level): kept {out.shape[0]}/{df.shape[0]} rows using {filter_name} "
        f"({len(decider_hh_draws)} household-draws)"
    )
    return out


# =========================================================================
# EUROMOD MERGE & DECIDER RESTRICTION
# =========================================================================

def _merge_euromod_outputs(long_df: pd.DataFrame, em_df: pd.DataFrame) -> pd.DataFrame:
    """Merge RURO draws with EUROMOD outputs (strict validation)."""
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

    # CRITICAL: Handle column collision for ils_dispy
    # If long_df had ils_dispy (e.g., from draws) but EUROMOD also returns ils_dispy,
    # the merge creates ils_dispy (from long_df) and ils_dispy_em (from em_df).
    # ALWAYS prefer EUROMOD's authoritative ils_dispy_em (counterfactual disposable income).
    if "ils_dispy_em" in merged.columns:
        ils_from_em = merged["ils_dispy_em"]
        em_missing_rate = ils_from_em.isna().mean()

        # ALWAYS use EUROMOD output (counterfactual income) when available
        logging.info(
            f"EUROMOD merge: Using ils_dispy_em (EUROMOD counterfactual output) as canonical ils_dispy "
            f"(missing rate: {em_missing_rate:.1%})"
        )
        merged["ils_dispy"] = ils_from_em

    # Now validate ils_dispy is present and not all missing
    if "ils_dispy" not in merged.columns or merged["ils_dispy"].isna().all():
        raise ValueError(
            "No valid ils_dispy after merge; check that EUROMOD outputs contain disposable income. "
            f"Available columns: {[c for c in merged.columns if 'ils' in c.lower()]}"
        )

    if merged["ils_dispy"].isna().any():
        missing_rate = merged["ils_dispy"].isna().mean()
        if missing_rate > 0.1:  # More than 10% missing
            missing = merged[merged["ils_dispy"].isna()][["idperson", "draw"]].head()
            raise ValueError(
                f"Missing ils_dispy in {missing_rate:.1%} of rows after merge; EUROMOD outputs did not align fully. "
                f"Example missing pairs: {missing.to_dict(orient='records')}"
            )
        else:
            logging.warning(
                f"EUROMOD merge: {missing_rate:.1%} of rows have missing ils_dispy (acceptable threshold)"
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

    For both singles and couples, only deciders (heads/partners) are kept.
    Non-deciders (children, other adults) are excluded from the MNL estimation sample.
    They were needed for EUROMOD household calculations but not for labor supply estimation.
    """
    df = df.copy()

    # Determine if this is couples data
    is_couples = "ruro_group" in df.columns and (df["ruro_group"] == 10).any()

    # 1) Head/partner flags (preferred definition)
    has_head = "hh_IsHead" in df.columns
    has_partner = "hh_IsPartner" in df.columns
    if has_head or has_partner:
        head = df["hh_IsHead"] if has_head else 0
        partner = df["hh_IsPartner"] if has_partner else 0
        decider_mask = (pd.to_numeric(head, errors="coerce").fillna(0).astype(int) == 1) | \
                       (pd.to_numeric(partner, errors="coerce").fillna(0).astype(int) == 1)

        if is_couples and "idhh" in df.columns and "draw" in df.columns:
            # Couples: keep only deciders (heads/partners), excluding children and non-deciders
            # The household-draw level filtering was incorrectly keeping ALL members including children
            out = df.loc[decider_mask].copy()
            n_hh_draws = out.groupby(["idhh", "draw"]).ngroups
            logging.info(
                "Decider restriction (couples, household-level): kept %d/%d rows "
                "(%d household-draws with deciders only, excluding children)",
                out.shape[0],
                df.shape[0],
                n_hh_draws
            )
        else:
            # Singles: row-level restriction
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

        if is_couples and "idhh" in df.columns and "draw" in df.columns:
            # Couples: household-draw level
            out = _apply_decider_filter_couples(df, decider_mask, "ruro_decider")
        else:
            # Singles: row-level
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

        if is_couples and "idhh" in df.columns and "draw" in df.columns:
            # Couples: household-draw level
            out = _apply_decider_filter_couples(df, decider_mask, "lma==1")
        else:
            # Singles: row-level
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


# =========================================================================
# GSUR INTEGRATION (EXTERNAL UNEMPLOYMENT RATES)
# =========================================================================

def _merge_gsur_singles(
    df: pd.DataFrame,
    gsur_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge GSUR unemployment rates onto singles MNL dataset.

    Base merge keys: (year, drgn1, dgn, educ3)
    Optional age-aware merge keys: (year, drgn1, dgn, educ3, age_group)

    If GSUR has age groups and singles has age information, merge on age-group first,
    then fallback to a full-age GSUR bracket when available.
    """
    df = df.copy()

    # Ensure required core columns
    _ensure_year_column(df)
    _derive_educ3_from_deh(df, deh_col="deh", educ3_col="educ3")

    gsur_std = _standardize_gsur_age_group_column(gsur_df)
    gsur_has_age_group = (
        "age_group" in gsur_std.columns and gsur_std["age_group"].notna().any()
    )

    age_col = next(
        (c for c in ["dag", "age", "age_years"] if c in df.columns),
        None,
    )

    base_keys = ["year", "drgn1", "dgn", "educ3"]
    missing_keys = [k for k in base_keys if k not in df.columns]
    if missing_keys:
        raise KeyError(f"GSUR merge requires columns: {missing_keys}")

    df_before = len(df)

    if gsur_has_age_group and age_col is not None:
        df["_gsur_age_group"] = _map_age_to_gsur_group(df[age_col])

        merge_keys = base_keys + ["_gsur_age_group"]
        gsur_lookup = gsur_std.rename(columns={"age_group": "_gsur_age_group"})[
            merge_keys + ["gsur"]
        ].drop_duplicates(subset=merge_keys)

        df = df.merge(
            gsur_lookup,
            on=merge_keys,
            how="left",
            validate="m:1",
        )

        # Fallback to full age bracket if fine age-group did not match.
        missing_mask = df["gsur"].isna()
        if missing_mask.any():
            fallback_group = _pick_gsur_full_age_fallback(gsur_std["age_group"])
            if fallback_group is not None:
                fallback_lookup = (
                    gsur_std.loc[
                        gsur_std["age_group"].astype(str) == fallback_group,
                        base_keys + ["gsur"],
                    ]
                    .drop_duplicates(subset=base_keys)
                )
                fallback_values = df.loc[missing_mask, base_keys].merge(
                    fallback_lookup,
                    on=base_keys,
                    how="left",
                    validate="m:1",
                )["gsur"]
                n_filled = int(fallback_values.notna().sum())
                df.loc[missing_mask, "gsur"] = fallback_values.to_numpy()
                if n_filled > 0:
                    logging.info(
                        "GSUR merge (singles): filled %d rows using fallback age_group=%s",
                        n_filled,
                        fallback_group,
                    )
            else:
                logging.warning(
                    "GSUR merge (singles): no full-age fallback age_group found in GSUR file."
                )

        df = df.drop(columns=["_gsur_age_group"], errors="ignore")
    else:
        if gsur_has_age_group and age_col is None:
            logging.warning(
                "GSUR has age_group but singles data has no age column; using age-agnostic fallback merge."
            )

        gsur_lookup = gsur_std[base_keys + ["gsur"]].drop_duplicates(subset=base_keys)
        df = df.merge(
            gsur_lookup,
            on=base_keys,
            how="left",
            validate="m:1",
        )

    if len(df) != df_before:
        raise ValueError(
            f"GSUR merge changed row count: {df_before} -> {len(df)}. "
            "Check for duplicate keys in GSUR lookup."
        )

    missing_rate = df["gsur"].isna().mean()
    if missing_rate > 0:
        logging.warning(
            "GSUR merge (singles): %.1f%% of rows have missing gsur. "
            "Check GSUR coverage for observed key combinations.",
            100 * missing_rate,
        )

        missing_by_year = df.groupby("year")["gsur"].apply(lambda x: x.isna().mean())
        for year, rate in missing_by_year.items():
            if rate > 0:
                logging.warning("  Year %s: %.1f%% missing GSUR", year, 100 * rate)

    return df


def _merge_gsur_couples_wide(
    df: pd.DataFrame,
    gsur_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge GSUR unemployment rates onto couples MNL dataset (wide format).

    Male/female merges use (year, drgn1, educ3_gender) and optionally age-group
    if GSUR age groups are available and age columns exist in couples data.
    """
    df = df.copy()

    _ensure_year_column(df)
    gsur_std = _standardize_gsur_age_group_column(gsur_df)
    gsur_has_age_group = (
        "age_group" in gsur_std.columns and gsur_std["age_group"].notna().any()
    )

    # Ensure educ3_male / educ3_female are present.
    for gender in ["male", "female"]:
        educ3_col = f"educ3_{gender}"
        deh_col = f"deh_{gender}"

        if educ3_col not in df.columns:
            if deh_col in df.columns:
                _derive_educ3_from_deh(df, deh_col=deh_col, educ3_col=educ3_col)
            else:
                eL, eM, eH = f"educL_{gender}", f"educM_{gender}", f"educH_{gender}"
                if all(c in df.columns for c in [eL, eM, eH]):
                    logging.info("GSUR merge: deriving %s from educL/M/H dummies", educ3_col)
                    df[educ3_col] = np.select(
                        [df[eL] == 1, df[eM] == 1, df[eH] == 1],
                        [0, 1, 2],
                        default=-1,
                    ).astype("Int64")
                else:
                    raise KeyError(
                        f"GSUR merge requires '{educ3_col}' or '{deh_col}' "
                        f"(or educL/M/H_{gender} dummies)."
                    )

    for gender, dgn_value in [("male", 1), ("female", 0)]:
        gsur_col = f"gsur_{gender}"
        educ3_col = f"educ3_{gender}"
        age_candidates = [
            f"dag_{gender}",
            f"age_{gender}",
            f"age_years_{gender}",
            "dag",
            "age",
            "age_years",
        ]
        age_col = next((c for c in age_candidates if c in df.columns), None)

        base_keys_df = ["year", "drgn1", educ3_col]
        gsur_gender = gsur_std[gsur_std["dgn"] == dgn_value].copy()

        if gsur_has_age_group and age_col is not None:
            age_key = f"_gsur_age_group_{gender}"
            df[age_key] = _map_age_to_gsur_group(df[age_col])

            merge_keys_df = base_keys_df + [age_key]
            gsur_lookup = gsur_gender.rename(
                columns={"educ3": educ3_col, "age_group": age_key, "gsur": gsur_col}
            )[merge_keys_df + [gsur_col]].drop_duplicates(subset=merge_keys_df)

            df = df.merge(
                gsur_lookup,
                on=merge_keys_df,
                how="left",
                validate="m:1",
            )

            missing_mask = df[gsur_col].isna()
            if missing_mask.any():
                fallback_group = _pick_gsur_full_age_fallback(gsur_gender["age_group"])
                if fallback_group is not None:
                    fallback_lookup = gsur_gender.loc[
                        gsur_gender["age_group"].astype(str) == fallback_group,
                        ["year", "drgn1", "educ3", "gsur"],
                    ].rename(columns={"educ3": educ3_col, "gsur": gsur_col})
                    fallback_lookup = fallback_lookup.drop_duplicates(subset=base_keys_df)

                    fallback_values = df.loc[missing_mask, base_keys_df].merge(
                        fallback_lookup,
                        on=base_keys_df,
                        how="left",
                        validate="m:1",
                    )[gsur_col]
                    n_filled = int(fallback_values.notna().sum())
                    df.loc[missing_mask, gsur_col] = fallback_values.to_numpy()
                    if n_filled > 0:
                        logging.info(
                            "GSUR merge (%s): filled %d rows using fallback age_group=%s",
                            gender,
                            n_filled,
                            fallback_group,
                        )
                else:
                    logging.warning(
                        "GSUR merge (%s): no full-age fallback age_group found in GSUR file.",
                        gender,
                    )

            df = df.drop(columns=[age_key], errors="ignore")
        else:
            if gsur_has_age_group and age_col is None:
                logging.warning(
                    "GSUR has age_group but couples data has no %s age column; using age-agnostic fallback merge.",
                    gender,
                )

            gsur_lookup = gsur_gender[["year", "drgn1", "educ3", "gsur"]].rename(
                columns={"educ3": educ3_col, "gsur": gsur_col}
            ).drop_duplicates(subset=base_keys_df)

            df = df.merge(
                gsur_lookup,
                on=base_keys_df,
                how="left",
                validate="m:1",
            )

        missing_rate = df[gsur_col].isna().mean()
        if missing_rate > 0:
            logging.warning(
                "GSUR merge (%s): %.1f%% missing. Check coverage for observed key combinations.",
                gender,
                100 * missing_rate,
            )

    return df


# =========================================================================
# MNL BLOCK BUILDERS
# =========================================================================

def _build_mnl_block(df: pd.DataFrame, sample_group: str) -> pd.DataFrame:
    """Build MNL dataset for singles."""
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

    # Keep labor-status indicators aligned with draw-specific hours.
    df["working"] = (hours > 0).astype(int)
    df["working_pt1"] = ((hours >= 18.5) & (hours <= 21.5)).astype(int)  # ~20-21h part-time
    df["working_pt2"] = ((hours >= 29.5) & (hours <= 30.5)).astype(int)  # ~30h part-time
    df["working_ft"] = ((hours >= 37.5) & (hours <= 40.5)).astype(int)   # ~40h full-time

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

    # Age normalization (for preference parameters)
    if "dag" in df.columns:
        dag_values = pd.to_numeric(df["dag"], errors="coerce")
        dag_mean = dag_values.mean()
        df["age_norm"] = dag_values - dag_mean
        df["age_norm2"] = df["age_norm"] ** 2
        logging.debug(f"Created age_norm (mean=0.00, std={df['age_norm'].std():.2f})")

    # Total children count (create alias for compatibility)
    if "num_children_total" in df.columns:
        df["n_children"] = pd.to_numeric(df["num_children_total"], errors="coerce").fillna(0)
        logging.debug(f"Created n_children alias (mean={df['n_children'].mean():.2f})")

    return df


def _build_mnl_block_couples_wide(df: pd.DataFrame, sample_group: str) -> pd.DataFrame:
    """Build MNL dataset for couples in WIDE format (_male/_female columns)."""
    df = df.copy()

    if "idperson" not in df.columns or "draw" not in df.columns or "is_chosen" not in df.columns:
        raise KeyError("Expected columns 'idperson', 'draw', 'is_chosen'.")
    # CRITICAL: For couples, consumption is PERSON-LEVEL (consumption_male and consumption_female)
    if "consumption_male" not in df.columns or "consumption_female" not in df.columns:
        raise KeyError(
            "Expected PERSON-LEVEL consumption columns 'consumption_male' and 'consumption_female' after reshape."
        )

    # For couples in wide format, process male and female separately
    for gender in ["male", "female"]:
        # Hours and leisure
        lhw_col = f"lhw_{gender}"
        hours_col = f"hours_{gender}"
        leisure_col = f"leisure_{gender}"

        if lhw_col in df.columns:
            hours = pd.to_numeric(df[lhw_col], errors="coerce").fillna(0.0)
            df[hours_col] = hours

            leisure = TOTAL_LEISURE_HOURS - hours
            leisure = leisure.clip(lower=DCM_MIN_POSITIVE)
            df[leisure_col] = leisure

            df[f"log_l_{gender}"] = np.log(leisure)

            # Working status indicators (for hours opportunity)
            # Focal hours peaks for RURO opportunity draws (narrow bands around typical schedules)
            df[f"working_{gender}"] = (hours > 0).astype(int)
            df[f"working_pt1_{gender}"] = ((hours >= 18.5) & (hours <= 21.5)).astype(int)  # ~20-21h part-time
            df[f"working_pt2_{gender}"] = ((hours >= 29.5) & (hours <= 30.5)).astype(int)  # ~30h part-time
            df[f"working_ft_{gender}"] = ((hours >= 37.5) & (hours <= 40.5)).astype(int)   # ~40h full-time

        # NOTE: GSUR is now merged externally, NOT set to working dummy

        # Wages: Log-transformation (for wage opportunity)
        # Robust wage column detection (wage / wage_ruro / yivwg)
        wage_col = None
        for candidate in [f"wage_{gender}", f"wage_ruro_{gender}", f"yivwg_{gender}"]:
            if candidate in df.columns:
                wage_col = candidate
                break

        if wage_col is not None:
            wage = pd.to_numeric(df[wage_col], errors="coerce").fillna(1.0)
            wage = wage.clip(lower=DCM_MIN_POSITIVE)
            df[f"wage_{gender}"] = wage  # Standardize column name
            df[f"log_wage_{gender}"] = np.log(wage)

        # Education dummies from deh_male/deh_female
        deh_col = f"deh_{gender}"
        if deh_col in df.columns:
            deh_num = pd.to_numeric(df[deh_col], errors="coerce")
            df[f"educL_{gender}"] = (deh_num.isin([0, 1, 2])).astype(int)
            df[f"educH_{gender}"] = (deh_num == 5).astype(int)
            df[f"educM_{gender}"] = (~df[f"educL_{gender}"].astype(bool) & ~df[f"educH_{gender}"].astype(bool)).astype(int)

        # Experience variables (for wage opportunity)
        # Priority: use pexp_years_{gender} if it exists (from reshape of raw pexp_years)
        # Otherwise, convert pexp_{gender} (RURO /100 scaling) back to years by multiplying by 100
        pexp_years_col = f"pexp_years_{gender}"
        pexp_col = f"pexp_{gender}"

        if pexp_years_col in df.columns:
            # Already have pexp_years from reshape - use it directly
            pexp_years_num = pd.to_numeric(df[pexp_years_col], errors="coerce").fillna(0.0)
            df[pexp_years_col] = pexp_years_num  # Ensure numeric
            df[f"pexp_years2_{gender}"] = pexp_years_num ** 2
            logging.debug(f"Using existing {pexp_years_col} (mean={pexp_years_num.mean():.2f} years)")
        elif pexp_col in df.columns:
            # Only have RURO-scaled pexp (scaled by /100) - convert to years
            pexp_num = pd.to_numeric(df[pexp_col], errors="coerce").fillna(0.0)
            pexp_years_num = pexp_num * 100.0  # Convert back to actual years
            df[pexp_years_col] = pexp_years_num
            df[f"pexp_years2_{gender}"] = pexp_years_num ** 2
            logging.debug(f"Created {pexp_years_col} from {pexp_col} * 100 (mean={pexp_years_num.mean():.2f} years)")

        # Create alias for estimation code compatibility
        if f"pexp_years2_{gender}" in df.columns:
            df[f"pexp2_{gender}"] = df[f"pexp_years2_{gender}"]

        # Age normalization (for preference/opportunity terms).
        # Prefer dag_{gender}; fall back to age_{gender} if needed.
        dag_col = f"dag_{gender}"
        age_col = f"age_{gender}"
        age_source_col = dag_col if dag_col in df.columns else (age_col if age_col in df.columns else None)
        if age_source_col is not None:
            age_values = pd.to_numeric(df[age_source_col], errors="coerce")
            age_mean = age_values.mean()
            df[f"age_norm_{gender}"] = age_values - age_mean
            df[f"age_norm2_{gender}"] = df[f"age_norm_{gender}"] ** 2
            logging.debug(
                f"Created age_norm_{gender} from {age_source_col} "
                f"(mean=0.00, std={df[f'age_norm_{gender}'].std():.2f})"
            )

        # Total children count (create alias for compatibility)
        num_children_col = f"num_children_total_{gender}"
        if num_children_col in df.columns:
            df[f"n_children_{gender}"] = pd.to_numeric(df[num_children_col], errors="coerce").fillna(0)
            logging.debug(f"Created n_children_{gender} alias (mean={df[f'n_children_{gender}'].mean():.2f})")

    # Create household-level n_children (same for both partners, use female's value)
    # This allows specs to use n_children for couples without gender suffix
    if "n_children_female" in df.columns:
        df["n_children"] = df["n_children_female"]
        logging.debug(f"Created household n_children alias (mean={df['n_children'].mean():.2f})")

    # NOTE: For couples, consumption_male and consumption_female are already created in reshape
    # No need to create a single 'consumption' column - couples utility uses BC(c_male + c_female)
    df["sample_group"] = sample_group

    return df


# =========================================================================
# COUPLES RESHAPE WITH VALIDATION
# =========================================================================

def _reshape_couples_to_wide(df: pd.DataFrame, allow_unbalanced: bool = False) -> pd.DataFrame:
    """
    Reshape couples data from long format (2 rows per household-draw) to
    wide format (1 row per household-draw with _male and _female columns).

    Enhanced with validation checks:
        - Exactly 2 rows per (idhh, draw)
        - is_chosen consistency across partners
        - Household-level variable consistency
    """
    # Empty guard: return empty DataFrame if input is empty
    if df.empty:
        logging.info("Couples reshape: input is empty; returning empty DataFrame.")
        return df

    if "ruro_group" not in df.columns:
        raise KeyError("Expected 'ruro_group' column for couples identification.")

    # Only reshape couples data (ruro_group == 10)
    is_couple = df["ruro_group"] == 10

    if not is_couple.any():
        logging.info("No couples data to reshape (ruro_group != 10).")
        return df

    df_couples = df[is_couple].copy()
    df_non_couples = df[~is_couple].copy()

    if "dgn" not in df_couples.columns:
        raise KeyError("Couples data must have 'dgn' column for gender identification.")

    if "idhh" not in df_couples.columns:
        raise KeyError("Couples data must have 'idhh' column for household identification.")

    if "draw" not in df_couples.columns:
        raise KeyError("Couples data must have 'draw' column.")

    # Verify we have 2 rows per household-draw
    dgn = pd.to_numeric(df_couples["dgn"], errors="coerce").fillna(-1).astype(int)
    rows_per_hh_draw = df_couples.groupby(["idhh", "draw"]).size()

    expected_rows = 2
    n_bad = (rows_per_hh_draw != expected_rows).sum()

    if n_bad > 0:
        # Show examples of violations
        bad_hh_draws = rows_per_hh_draw[rows_per_hh_draw != expected_rows].head(10)
        logging.error(
            f"Couples reshape validation FAILED: {n_bad}/{len(rows_per_hh_draw)} "
            f"household-draws have wrong row count (expected {expected_rows}).\n"
            f"Examples:\n{bad_hh_draws}"
        )

        # Strict mode: raise unless --allow-unbalanced-couples
        if not allow_unbalanced:
            raise ValueError(
                f"Couples reshape requires exactly {expected_rows} rows per (idhh, draw). "
                f"Found {n_bad} violations. Pass --allow-unbalanced-couples to proceed anyway."
            )
        else:
            logging.warning("Proceeding with unbalanced couples (--allow-unbalanced-couples enabled)")

    # CRITICAL: Validate gender composition per (idhh, draw) BEFORE building male/female splits
    # Each household-draw must have exactly one dgn==1 (male) and one dgn==0 (female)
    gender_counts = df_couples.groupby(["idhh", "draw"])["dgn"].apply(
        lambda x: pd.Series({"n_male": (x == 1).sum(), "n_female": (x == 0).sum()})
    ).unstack()

    gender_violations = gender_counts[
        (gender_counts["n_male"] != 1) | (gender_counts["n_female"] != 1)
    ]

    if len(gender_violations) > 0:
        n_violations = len(gender_violations)
        sample_violations = gender_violations.head(10)

        logging.error(
            f"Gender composition validation FAILED: {n_violations} household-draws "
            f"do not have exactly 1 male and 1 female.\n"
            f"Sample violations:\n{sample_violations}"
        )

        if not allow_unbalanced:
            raise ValueError(
                f"Couples reshape requires exactly 1 male (dgn==1) and 1 female (dgn==0) "
                f"per (idhh, draw). Found {n_violations} violations. "
                f"Pass --allow-unbalanced-couples to proceed anyway."
            )
        else:
            # Drop violating household-draws before proceeding
            valid_hh_draws = gender_counts[
                (gender_counts["n_male"] == 1) & (gender_counts["n_female"] == 1)
            ].index

            before_drop = len(df_couples)
            df_couples = df_couples.set_index(["idhh", "draw"]).loc[valid_hh_draws].reset_index()
            after_drop = len(df_couples)

            logging.warning(
                f"Dropped {before_drop - after_drop} rows from {n_violations} "
                f"household-draws with invalid gender composition (--allow-unbalanced-couples enabled)"
            )

            if df_couples.empty:
                logging.error("All couples data dropped after gender validation!")
                return pd.DataFrame()

            # Recompute dgn after filtering
            dgn = pd.to_numeric(df_couples["dgn"], errors="coerce").fillna(-1).astype(int)

    # Identify male/female rows
    male_mask = dgn == 1
    female_mask = dgn == 0

    df_male = df_couples[male_mask].copy()
    df_female = df_couples[female_mask].copy()

    logging.info(f"Reshaping couples: {len(df_male)} male rows, {len(df_female)} female rows")

    # Columns to exclude from pivoting (keep as-is or merge later)
    id_cols = {"idhh", "draw", "idperson", "idorighh", "idorigperson", "idpartner", "idfather", "idmother"}

    # Flag columns: end with _f, _s, _a, _o (common EUROMOD flag suffixes)
    flag_suffixes = ("_f", "_s", "_a", "_o")
    flag_cols = {c for c in df_couples.columns if any(c.endswith(suf) for suf in flag_suffixes)}

    # Structural columns that shouldn't be gender-specific
    structural_cols = {
        "ruro_group", "ruro_decider", "hh_IsHead", "hh_IsPartner",
        "dgn",  # gender indicator itself
        "sample_group", "chosen", "is_chosen"
    }

    # EUROMOD internal/temporary columns (usually start with i_, il_, tu_)
    internal_prefixes = ("i_", "il_", "tu_", "temp_")
    internal_cols = {c for c in df_couples.columns if any(c.startswith(pre) for pre in internal_prefixes)}

    # Household-level columns (same for both partners)
    household_cols = {
        "idhh", "draw", "idorighh", "ruro_group",
        "keep_for_analysis", "ruro_sample",
        "is_chosen", "chosen",  # Choice indicators
        "other_members_income",  # Household income
        # NOTE: ils_dispy/ils_dispy_em are PERSON-level (vary by each person's hours in each draw)
        # They should be PIVOTED to _male/_female, NOT treated as household-level
        "drgn1",  # Region (required for GSUR merge)
        "year", "year_for_ruro", "data_year"  # Time identifiers (required for GSUR merge)
    }

    # Determine which columns to pivot
    exclude_cols = id_cols | flag_cols | structural_cols | internal_cols
    pivot_cols = []
    for col in df_couples.columns:
        if col not in exclude_cols:
            # Additional filter: skip EUROMOD benefit/tax aggregates (usually start with ils_, tis_, etc.)
            # EXCEPTION: ils_dispy and ils_dispy_em are PERSON-level consumption - MUST be pivoted!
            if col in ("ils_dispy", "ils_dispy_em"):
                pivot_cols.append(col)  # Force pivot for disposable income
            elif col.startswith(("ils_", "tis_", "tsc_", "tin_", "bsa", "bun", "bho", "bdi")):
                continue  # Skip other EUROMOD aggregates
            else:
                pivot_cols.append(col)

    logging.info(f"Pivoting {len(pivot_cols)} columns to _male/_female format")
    logging.info(f"Excluded {len(exclude_cols)} columns from pivoting (flags, IDs, internals)")

    # Rename male/female columns
    rename_male = {col: f"{col}_male" for col in pivot_cols}
    rename_female = {col: f"{col}_female" for col in pivot_cols}

    df_male_renamed = df_male.rename(columns=rename_male)
    df_female_renamed = df_female.rename(columns=rename_female)

    # Merge on (idhh, draw)
    merge_keys = ["idhh", "draw"]
    df_wide = df_male_renamed.merge(
        df_female_renamed,
        on=merge_keys,
        how="inner",
        suffixes=("_MALE_DUP", "_FEMALE_DUP")
    )

    # Check is_chosen consistency across partners
    if "is_chosen_male" in df_wide.columns and "is_chosen_female" in df_wide.columns:
        is_chosen_match = (
            df_wide["is_chosen_male"] == df_wide["is_chosen_female"]
        ).all()

        if not is_chosen_match:
            mismatches = df_wide[
                df_wide["is_chosen_male"] != df_wide["is_chosen_female"]
            ][["idhh", "draw", "is_chosen_male", "is_chosen_female"]].head(20)

            raise ValueError(
                f"is_chosen mismatch between partners in {len(mismatches)} rows.\n"
                f"This indicates data corruption or incorrect decider restriction.\n"
                f"Examples:\n{mismatches}"
            )

    # Preserve one copy of household-level columns before dropping duplicates
    dup_male_cols = [c for c in df_wide.columns if c.endswith("_MALE_DUP")]
    dup_female_cols = [c for c in df_wide.columns if c.endswith("_FEMALE_DUP")]

    # SPECIAL HANDLING: ils_dispy_male and ils_dispy_female need floor applied (EUROMOD can return negative)
    # These are PERSON-LEVEL variables (vary by each person's hours choice) so we keep BOTH!
    if "ils_dispy_male" in df_wide.columns and "ils_dispy_female" in df_wide.columns:
        # Apply floor to both male and female disposable income
        before_male_min = df_wide["ils_dispy_male"].min()
        before_female_min = df_wide["ils_dispy_female"].min()

        df_wide["ils_dispy_male"] = df_wide["ils_dispy_male"].clip(lower=DCM_MIN_POSITIVE)
        df_wide["ils_dispy_female"] = df_wide["ils_dispy_female"].clip(lower=DCM_MIN_POSITIVE)

        n_floored_male = (df_wide["ils_dispy_male"] == DCM_MIN_POSITIVE).sum()
        n_floored_female = (df_wide["ils_dispy_female"] == DCM_MIN_POSITIVE).sum()

        logging.info(
            f"Applied consumption floor={DCM_MIN_POSITIVE} to couples disposable income:\n"
            f"  Male:   min {before_male_min:.2f} → {df_wide['ils_dispy_male'].min():.2f} ({n_floored_male} obs floored)\n"
            f"  Female: min {before_female_min:.2f} → {df_wide['ils_dispy_female'].min():.2f} ({n_floored_female} obs floored)"
        )

    # Defragment once before adding restored columns.
    df_wide = df_wide.copy()

    # Restore duplicate columns in one batch to avoid per-column insert fragmentation.
    restored_cols: Dict[str, pd.Series] = {}
    for male_col in dup_male_cols:
        base_name = male_col.replace("_MALE_DUP", "")
        if base_name not in df_wide.columns:
            restored_cols[base_name] = df_wide[male_col]
    if restored_cols:
        df_wide = pd.concat(
            [df_wide, pd.DataFrame(restored_cols, index=df_wide.index)],
            axis=1,
        )

    # Now drop all duplicate columns
    drop_cols = dup_male_cols + dup_female_cols
    if drop_cols:
        logging.info(f"Dropping {len(drop_cols)} duplicate columns from merge (kept {len(dup_male_cols)} originals)")
        df_wide = df_wide.drop(columns=drop_cols)

    # Ensure one copy of household-level variables with consistency checks.
    household_restored_cols: Dict[str, pd.Series] = {}
    household_gender_cols_to_drop = []
    for var in household_cols:
        male_var = f"{var}_male"
        female_var = f"{var}_female"

        # Check if variable exists in gendered form
        if male_var in df_wide.columns and female_var in df_wide.columns:
            # Verify consistency for critical household variables
            if var in {"drgn1", "year", "year_for_ruro", "data_year", "idhh", "draw"}:
                mismatch_mask = df_wide[male_var] != df_wide[female_var]
                if mismatch_mask.any():
                    n_mismatches = mismatch_mask.sum()
                    examples = df_wide[mismatch_mask][["idhh", "draw", male_var, female_var]].head(5)
                    raise ValueError(
                        f"Household variable '{var}' mismatch between partners in {n_mismatches} rows.\n"
                        f"Examples:\n{examples}"
                    )

            # Use male version as canonical (they should be identical after check).
            if var not in df_wide.columns:
                household_restored_cols[var] = df_wide[male_var]
        elif male_var in df_wide.columns and var not in df_wide.columns:
            # Only male version exists, use it.
            household_restored_cols[var] = df_wide[male_var]

        household_gender_cols_to_drop.extend([male_var, female_var])

    if household_restored_cols:
        df_wide = pd.concat(
            [df_wide, pd.DataFrame(household_restored_cols, index=df_wide.index)],
            axis=1,
        )

    # Drop gender-specific versions of household vars.
    if household_gender_cols_to_drop:
        df_wide = df_wide.drop(
            columns=list(dict.fromkeys(household_gender_cols_to_drop)),
            errors="ignore",
        )

    # Create household-level idperson for couples (use idhh since household is the decision unit)
    if "idperson" not in df_wide.columns and "idhh" in df_wide.columns:
        df_wide["idperson"] = df_wide["idhh"]
        logging.info("Created household-level idperson from idhh for couples")

    # Defragment once after structural column creation.
    df_wide = df_wide.copy()

    # Create consumption_male and consumption_female from ils_dispy_male and ils_dispy_female
    # These are PERSON-LEVEL variables (vary by each person's hours choice in each draw)
    if "ils_dispy_male" in df_wide.columns and "ils_dispy_female" in df_wide.columns:
        df_wide = df_wide.drop(columns=["consumption_male", "consumption_female"], errors="ignore")
        df_wide = pd.concat(
            [
                df_wide,
                pd.DataFrame(
                    {
                        "consumption_male": df_wide["ils_dispy_male"],
                        "consumption_female": df_wide["ils_dispy_female"],
                    },
                    index=df_wide.index,
                ),
            ],
            axis=1,
        )
        logging.info(
            f"Created consumption_male and consumption_female from ils_dispy_male/female "
            f"(min_male: {df_wide['consumption_male'].min():.2f}, "
            f"min_female: {df_wide['consumption_female'].min():.2f})"
        )
    else:
        logging.warning(
            "Missing ils_dispy_male or ils_dispy_female columns - consumption will not be created!"
        )

    logging.info(f"Reshaped couples data: {len(df_wide)} rows (was {len(df_couples)} in long format)")

    # If there were singles in the input, we cannot combine them with reshaped couples
    if not df_non_couples.empty:
        logging.warning(
            f"Input contained {len(df_non_couples)} non-couples rows. "
            "Returning only reshaped couples data. Singles should be processed separately."
        )

    return df_wide


# =========================================================================
# NORMALIZATION
# =========================================================================

def _normalize_singles(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Normalize consumption and leisure for singles using observed choice.

    Returns:
        (normalized_df, scaling_constants_dict)
    """
    df = df.copy()

    # Identify chosen observations
    if "is_chosen" in df.columns:
        chosen_mask = df["is_chosen"] == 1
    elif "draw" in df.columns:
        chosen_mask = df["draw"] == 0
    else:
        raise KeyError("Cannot identify chosen observations (need 'is_chosen' or 'draw')")

    # Consumption: mean of ALL observations (not just chosen)
    # Using only chosen creates selection bias in normalization
    c_scale = float(df["consumption"].mean())

    if c_scale <= 0:
        raise ValueError(f"Invalid consumption scaling constant: {c_scale}")

    # Leisure: minimum of positive chosen leisure
    l_chosen = df.loc[chosen_mask, "leisure"]
    l_positive = l_chosen[l_chosen > 0]

    if len(l_positive) == 0:
        logging.warning("No positive leisure in chosen observations; using overall minimum")
        l_positive = df["leisure"][df["leisure"] > 0]

    l_scale = float(l_positive.min()) if len(l_positive) > 0 else 1.0

    # Create normalized variables
    df["c_norm"] = df["consumption"] / c_scale
    df["l_norm"] = df["leisure"] / l_scale
    df["log_c_norm"] = np.log(df["c_norm"].clip(lower=DCM_MIN_POSITIVE))
    df["log_l_norm"] = np.log(df["l_norm"].clip(lower=DCM_MIN_POSITIVE))

    scaling = {
        "c_scale": c_scale,
        "l_scale": l_scale,
        "n_chosen": int(chosen_mask.sum())
    }

    logging.info(f"Singles normalization: c_scale={c_scale:.2f}, l_scale={l_scale:.2f}")

    return df, scaling


def _normalize_couples_wide(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Normalize consumption and leisure for couples (wide format).

    CRITICAL: Consumption is PERSON-LEVEL (varies by each person's hours choice in each draw).
    Male and female consumption are normalized separately but use the SAME scaling factor.
    Individual leisure: gender-specific minima
    """
    df = df.copy()

    # Identify chosen observations
    if "is_chosen" in df.columns:
        chosen_mask = df["is_chosen"] == 1
    elif "draw" in df.columns:
        chosen_mask = df["draw"] == 0
    else:
        raise KeyError("Cannot identify chosen observations")

    # Consumption scaling: Use mean of HOUSEHOLD SUM from ALL observations
    # CRITICAL: We must use ALL observations, not just chosen, to avoid biasing the scale
    # If we only use chosen, then mean(c_norm for chosen) = 1.0 by construction,
    # which creates an artificial negative relationship if non-chosen have higher consumption
    consumption_all = df["consumption_male"] + df["consumption_female"]
    c_scale = float(consumption_all.mean())  # Mean of HOUSEHOLD consumption across ALL draws

    # Leisure: gender-specific minima
    l_male_chosen = df.loc[chosen_mask, "leisure_male"]
    l_female_chosen = df.loc[chosen_mask, "leisure_female"]

    l_male_positive = l_male_chosen[l_male_chosen > 0]
    l_female_positive = l_female_chosen[l_female_chosen > 0]

    l_male_scale = float(l_male_positive.min()) if len(l_male_positive) > 0 else 1.0
    l_female_scale = float(l_female_positive.min()) if len(l_female_positive) > 0 else 1.0

    # Create normalized HOUSEHOLD consumption
    # We normalize the SUM, not each component separately!
    df["consumption"] = df["consumption_male"] + df["consumption_female"]
    df["c_norm"] = df["consumption"] / c_scale
    df["log_c_norm"] = np.log(df["c_norm"].clip(lower=DCM_MIN_POSITIVE))

    for gender, l_scale in [("male", l_male_scale), ("female", l_female_scale)]:
        df[f"l_norm_{gender}"] = df[f"leisure_{gender}"] / l_scale
        df[f"log_l_norm_{gender}"] = np.log(
            df[f"l_norm_{gender}"].clip(lower=DCM_MIN_POSITIVE)
        )

    scaling = {
        "c_scale": c_scale,
        "l_male_scale": l_male_scale,
        "l_female_scale": l_female_scale,
        "n_chosen": int(chosen_mask.sum())
    }

    logging.info(
        f"Couples normalization: c_scale={c_scale:.2f}, "
        f"l_male_scale={l_male_scale:.2f}, l_female_scale={l_female_scale:.2f}"
    )

    return df, scaling


# =========================================================================
# PRIOR COMPUTATION (SPLIT BY SAMPLE GROUP)
# =========================================================================

def _copy_proposal_component_aliases(df: pd.DataFrame) -> pd.DataFrame:
    """Expose draw proposal components under RURO layered proposal names."""
    aliases = {
        "log_q_state": "log_q_E",
        "log_q_hours": "log_q_H",
        "log_q_wage": "log_q_W",
        "log_q_occ": "log_q_Occ",
    }
    for source, target in aliases.items():
        if source in df.columns and target not in df.columns:
            df[target] = df[source]

    for suffix in ("male", "female"):
        for source_base, target_base in aliases.items():
            source = f"{source_base}_{suffix}"
            target = f"{target_base}_{suffix}"
            if source in df.columns and target not in df.columns:
                df[target] = df[source]
    return df


def _component_log_q_singles(df: pd.DataFrame) -> Optional[np.ndarray]:
    required = ("log_q_E", "log_q_H", "log_q_W", "log_q_Occ")
    if not all(col in df.columns for col in required):
        return None
    if "working" in df.columns:
        working = pd.to_numeric(df["working"], errors="coerce").fillna(0.0).to_numpy()
    else:
        working = (pd.to_numeric(df["hours"], errors="coerce").fillna(0.0).to_numpy() > 0).astype(float)
    return (
        pd.to_numeric(df["log_q_E"], errors="coerce").fillna(0.0).to_numpy()
        + working
        * (
            pd.to_numeric(df["log_q_H"], errors="coerce").fillna(0.0).to_numpy()
            + pd.to_numeric(df["log_q_W"], errors="coerce").fillna(0.0).to_numpy()
            + pd.to_numeric(df["log_q_Occ"], errors="coerce").fillna(0.0).to_numpy()
        )
    )


def _component_log_q_couples(df: pd.DataFrame) -> Optional[np.ndarray]:
    total = np.zeros(len(df), dtype=float)
    for suffix in ("male", "female"):
        required = (
            f"log_q_E_{suffix}",
            f"log_q_H_{suffix}",
            f"log_q_W_{suffix}",
            f"log_q_Occ_{suffix}",
        )
        if not all(col in df.columns for col in required):
            return None
        working_col = f"working_{suffix}"
        hours_col = f"hours_{suffix}"
        if working_col in df.columns:
            working = pd.to_numeric(df[working_col], errors="coerce").fillna(0.0).to_numpy()
        else:
            working = (
                pd.to_numeric(df[hours_col], errors="coerce").fillna(0.0).to_numpy() > 0
            ).astype(float)
        total = total + (
            pd.to_numeric(df[f"log_q_E_{suffix}"], errors="coerce").fillna(0.0).to_numpy()
            + working
            * (
                pd.to_numeric(df[f"log_q_H_{suffix}"], errors="coerce").fillna(0.0).to_numpy()
                + pd.to_numeric(df[f"log_q_W_{suffix}"], errors="coerce").fillna(0.0).to_numpy()
                + pd.to_numeric(df[f"log_q_Occ_{suffix}"], errors="coerce").fillna(0.0).to_numpy()
            )
        )
    return total


def _compute_prior_singles(
    df: pd.DataFrame,
    *,
    wage_spec: str,
    pi0_m: float,
    pi0_f: float,
    h_min: float,
    h_max: float,
    w_min: float,
    w_max: float,
) -> pd.DataFrame:
    """
    Compute RURO prior for singles dataset.

    NOTE: This function assumes the input has already been filtered to lma==1
    (labour-market-attached population). All individuals are treated as active.
    """
    df = df.copy()
    df = _copy_proposal_component_aliases(df)

    component_log_q = _component_log_q_singles(df)
    if component_log_q is not None:
        finite_mask = np.isfinite(component_log_q)
        if not finite_mask.any():
            raise ValueError("Singles prior: layered log_q components have no finite values.")
        fallback = float(np.nanmedian(component_log_q[finite_mask]))
        component_log_q = np.where(finite_mask, component_log_q, fallback)
        prior_density = np.exp(np.clip(component_log_q, -700, 700))
        prior_density = np.clip(prior_density, 1e-16, None)
        df["prior"] = prior_density
        df["log_prior"] = np.log(prior_density)
        df.attrs["prior_source"] = "layered_log_q"
        logging.info(
            "Prior (singles): using RURO layered proposal density "
            "log_q_E + working*(log_q_H + log_q_W + log_q_Occ)."
        )
        return df

    # Job-choice draws path:
    # If draw-level proposal density is available, use it directly.
    # This keeps Step 6 spec-agnostic: continuous draws use formula prior,
    # job draws use the sampled job proposal density.
    if "log_q_total" in df.columns:
        log_q = pd.to_numeric(df["log_q_total"], errors="coerce")
        if log_q.notna().any():
            missing_rate = float(log_q.isna().mean())
            if missing_rate > 0:
                logging.warning(
                    f"Singles prior: log_q_total has {missing_rate:.1%} missing values; "
                    "using finite fallback for those rows."
                )

            log_q_arr = log_q.to_numpy()
            finite_mask = np.isfinite(log_q_arr)
            if not finite_mask.any():
                raise ValueError("Singles prior: log_q_total has no finite values.")

            fallback = float(np.nanmedian(log_q_arr[finite_mask]))
            log_q_arr = np.where(finite_mask, log_q_arr, fallback)

            prior_density = np.exp(np.clip(log_q_arr, -700, 700))
            prior_density = np.clip(prior_density, 1e-16, None)
            df["prior"] = prior_density
            df["log_prior"] = np.log(prior_density)
            df.attrs["prior_source"] = "job_draw_log_q_total"

            logging.info(
                "Prior (singles): using job-draw proposal density from 'log_q_total'."
            )
            return df

    # Validate required columns
    for col in ("dgn", "hours"):
        if col not in df.columns:
            raise KeyError(f"Singles dataset must contain '{col}' before computing the prior.")

    # Wage column
    if "wage" in df.columns:
        wage = pd.to_numeric(df["wage"], errors="coerce")
    elif "wage_ruro" in df.columns:
        wage = pd.to_numeric(df["wage_ruro"], errors="coerce")
    elif "yivwg" in df.columns:
        wage = pd.to_numeric(df["yivwg"], errors="coerce")
    else:
        raise KeyError("Singles dataset must contain 'wage', 'wage_ruro' or 'yivwg'.")
    df["wage"] = wage

    dgn = pd.to_numeric(df["dgn"], errors="coerce").fillna(1).astype(int)
    hours = pd.to_numeric(df["hours"], errors="coerce").fillna(0.0)

    # π₀ assignment (per-observation, gender-specific)
    # All individuals are lma==1, so assign pi0 by gender
    pi0 = np.zeros(len(df), dtype=float)
    mask_m = (dgn == 1)
    mask_f = (dgn == 0)
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

    h_arr = hours.to_numpy()

    # Hours component
    prior_h = np.where(
        h_arr <= 0,
        pi0,
        (1.0 - pi0) / h_range
    )

    if wage_spec == "fw":
        # Fixed wages: prior only over hours
        prior_density = prior_h
    else:
        # Variable wages: hours × wage
        prior_w = np.where(
            h_arr <= 0,
            1.0,  # when hours=0, wage is structurally 0; no wage density
            1.0 / w_range
        )
        prior_density = prior_h * prior_w

    # Clip to avoid log(0) and take log
    prior_density = np.clip(prior_density, 1e-16, None)
    # RURO convention: prior on original (density) scale, log_prior = log(prior).
    # Engine subtracts np.log(data.prior); if prior were stored on the log scale
    # the engine would compute log(log(...)) and silently misspecify.
    df["prior"] = prior_density
    df["log_prior"] = np.log(prior_density)
    df.attrs["prior_source"] = "continuous_formula"

    return df


def _compute_prior_couples_wide(
    df: pd.DataFrame,
    *,
    wage_spec: str,
    pi0_m: float,
    pi0_f: float,
    h_min: float,
    h_max: float,
    w_min: float,
    w_max: float,
) -> pd.DataFrame:
    """Compute RURO prior for couples dataset (wide format)."""
    df = df.copy()
    df = _copy_proposal_component_aliases(df)

    component_log_q = _component_log_q_couples(df)
    if component_log_q is not None:
        finite_mask = np.isfinite(component_log_q)
        if not finite_mask.any():
            raise ValueError("Couples prior: layered log_q components have no finite values.")
        fallback = float(np.nanmedian(component_log_q[finite_mask]))
        component_log_q = np.where(finite_mask, component_log_q, fallback)
        prior_density = np.exp(np.clip(component_log_q, -700, 700))
        prior_density = np.clip(prior_density, 1e-16, None)
        df["prior"] = prior_density
        df["log_prior"] = np.log(prior_density)
        df.attrs["prior_source"] = "layered_log_q_joint"
        logging.info(
            "Prior (couples): using RURO layered proposal density summed over spouses."
        )
        return df

    # Job-choice draws path:
    # Couples wide keeps draw proposal density in gendered columns after reshape.
    if "log_q_total_male" in df.columns and "log_q_total_female" in df.columns:
        log_q_m = pd.to_numeric(df["log_q_total_male"], errors="coerce")
        log_q_f = pd.to_numeric(df["log_q_total_female"], errors="coerce")

        valid = np.isfinite(log_q_m.to_numpy()) & np.isfinite(log_q_f.to_numpy())
        if valid.any():
            missing_rate = 1.0 - float(valid.mean())
            if missing_rate > 0:
                logging.warning(
                    f"Couples prior: log_q_total_male/female has {missing_rate:.1%} invalid rows; "
                    "using finite fallback for those rows."
                )

            m_arr = log_q_m.to_numpy()
            f_arr = log_q_f.to_numpy()

            m_fallback = float(np.nanmedian(m_arr[np.isfinite(m_arr)]))
            f_fallback = float(np.nanmedian(f_arr[np.isfinite(f_arr)]))

            m_arr = np.where(np.isfinite(m_arr), m_arr, m_fallback)
            f_arr = np.where(np.isfinite(f_arr), f_arr, f_fallback)

            log_q_joint = m_arr + f_arr
            prior_density = np.exp(np.clip(log_q_joint, -700, 700))
            prior_density = np.clip(prior_density, 1e-16, None)

            df["prior"] = prior_density
            df["log_prior"] = np.log(prior_density)
            df.attrs["prior_source"] = "job_draw_log_q_total_joint"

            logging.info(
                "Prior (couples): using joint job-draw proposal density from "
                "'log_q_total_male + log_q_total_female'."
            )
            return df

    # For couples, we need hours_male, hours_female
    if "hours_male" not in df.columns or "hours_female" not in df.columns:
        raise KeyError("Couples dataset must have 'hours_male' and 'hours_female' columns.")

    h_m = pd.to_numeric(df["hours_male"], errors="coerce").fillna(0.0).to_numpy()
    h_f = pd.to_numeric(df["hours_female"], errors="coerce").fillna(0.0).to_numpy()

    # Wage columns (if vw) - robust detection
    if wage_spec == "vw":
        # Detect male wage column
        wage_male_col = None
        for candidate in ["wage_male", "wage_ruro_male", "yivwg_male"]:
            if candidate in df.columns:
                wage_male_col = candidate
                break

        # Detect female wage column
        wage_female_col = None
        for candidate in ["wage_female", "wage_ruro_female", "yivwg_female"]:
            if candidate in df.columns:
                wage_female_col = candidate
                break

        if wage_male_col is None or wage_female_col is None:
            raise KeyError(
                f"Couples dataset with wage_spec='vw' requires wage columns for both genders. "
                f"Found: wage_male={wage_male_col}, wage_female={wage_female_col}"
            )

        w_m = pd.to_numeric(df[wage_male_col], errors="coerce").fillna(0.0).to_numpy()
        w_f = pd.to_numeric(df[wage_female_col], errors="coerce").fillna(0.0).to_numpy()

    # Validate bounds
    h_range = h_max - h_min
    if h_range <= 0:
        raise ValueError("Invalid hours support for prior computation.")
    w_range = w_max - w_min
    if wage_spec == "vw" and w_range <= 0:
        raise ValueError("Invalid wage support for prior computation.")

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
        prior_density = prior_h_m * prior_h_f
    else:
        # Variable wages: include wage densities
        prior_w_m = np.where(h_m <= 0, 1.0, 1.0 / w_range)
        prior_w_f = np.where(h_f <= 0, 1.0, 1.0 / w_range)
        prior_density = prior_h_m * prior_w_m * prior_h_f * prior_w_f

    # Clip and log
    prior_density = np.clip(prior_density, 1e-16, None)
    # RURO convention: prior on original (density) scale, log_prior = log(prior).
    df["prior"] = prior_density
    df["log_prior"] = np.log(prior_density)
    df.attrs["prior_source"] = "continuous_formula"

    return df


# =========================================================================
# COLUMN FILTERING FOR REDUCED DATASET SIZE
# =========================================================================

def get_essential_columns_for_estimation() -> set[str]:
    """
    Get the minimal set of columns needed for Steps 6, 7, and 8.
    
    This reduces the MNL dataset from 900+ columns to ~100 essential columns,
    resulting in ~85-90% file size reduction and 2-3x faster data loading.
    
    Returns
    -------
    set[str]
        Set of column names to keep in the final MNL dataset.
    """
    essential = set()
    
    # ---- Core IDs (ALWAYS needed) ----
    essential.update({
        # Household/person IDs
        "idhh", "idhh_true", "didp", "idperson", "idperson_true", "hid",
        # Draw/choice IDs
        "draw", "is_chosen", "draw_id", "chosen",
        # Year
        "year", "year_for_ruro", "data_year", "year_for_draws",
    })
    
    # ---- Demographics (Step 6 + Step 7) ----
    essential.update({
        # Age
        "dag", "age", "age_norm", "age_norm2",
        "dag_male", "dag_female", "age_male", "age_female",
        "age_norm_male", "age_norm_female", "age_norm2_male", "age_norm2_female",
        # Gender
        "dgn", "female", "male", "gender",
        # Education
        "deh", "deh_male", "deh_female",
        "educ3", "educ3_male", "educ3_female",
        "educL", "educM", "educH",
        "educL_male", "educM_male", "educH_male",
        "educL_female", "educM_female", "educH_female",
        # Children
        "n_children", "num_children_total", "nkids",
        "nch02", "nch36", "nch712", "nch1317",
        # Couple status
        "in_couple", "couple", "idpartner",
        "ruro_group", "ruro_decider", "ruro_sample", "keep_for_analysis",
        # Region (GSUR merge)
        "drgn", "drgn1", "reg_nuts1",
        "reg_nuts1_1", "reg_nuts1_2", "reg_nuts1_3", "reg_nuts1_4",
        "reg_nuts1_5", "reg_nuts1_6", "reg_nuts1_7", "reg_nuts1_8",
    })
    
    # ---- Labor market (Step 6 + Step 7) ----
    essential.update({
        # Hours
        "hours", "hours_observed", "hours_male", "hours_female",
        "lhw", "working", "working_pt1", "working_pt2", "working_ft",
        # Gendered working indicators (couples; engine routes male/female via these)
        "working_male", "working_female",
        "working_pt1_male", "working_pt1_female",
        "working_pt2_male", "working_pt2_female",
        "working_ft_male", "working_ft_female",
        # Wages
        "wage", "wage_observed", "wage_male", "wage_female",
        "lwage", "yem",
        # Experience
        "pexp_years", "pexp_years2", "exp", "exp2",
        "pexp_male", "pexp_female", "pexp2_male", "pexp2_female",
        "pexp_years_male", "pexp_years_female", "pexp_years2_male", "pexp_years2_female",
        # Occupation
        "loc", "loc4", "loc4_1", "loc4_2", "loc4_3", "loc4_4",
        "loc4_male", "loc4_female",
        # Industry DROPPED for occupation-opportunity M0 (contract §15/§25; reserved for M6).
        # Restore "lindi", "industry", "nace" only when activating M6.
        # Job-choice identifiers are intentionally excluded from frozen M0.
    })
    
    # ---- EUROMOD outputs (Step 6 consumption) ----
    essential.update({
        # Disposable income (CRITICAL for consumption)
        "ils_dispy", "ils_dispy_em",
        "ils_dispy_male", "ils_dispy_female",
        # Other income components
        "ils_origy", "ils_earns", "ils_pen",
        "ils_sicdy", "ils_sic",
        "tin_s", "tsy_s", "bsa_s", "bun_s", "bfa_s", "bho_s",
        # Person-level income (couples)
        "yem_male", "yem_female",
        "ils_earns_male", "ils_earns_female",
    })
    
    # ---- Utility variables (Step 6 creates, Step 7 uses) ----
    essential.update({
        # Consumption
        "consumption", "consumption_male", "consumption_female",
        # Leisure
        "leisure", "leisure_male", "leisure_female",
        # Normalized versions
        "c_norm", "l_norm", "l_norm_male", "l_norm_female",
        "log_c_norm", "log_l_norm",
        "log_l_norm_male", "log_l_norm_female",
        # Raw log versions
        "log_c", "log_l",
    })
    
    # ---- Prior and GSUR (Step 7 estimation) ----
    essential.update({
        # Prior probability
        "prior", "log_prior", "prior_h", "prior_w",
        # Frozen M0 per-layer proposal components.
        "log_q_E", "log_q_H", "log_q_W", "log_q_Occ",
        "log_q_E_male", "log_q_E_female",
        "log_q_H_male", "log_q_H_female",
        "log_q_W_male", "log_q_W_female",
        "log_q_Occ_male", "log_q_Occ_female",
        # GSUR unemployment rates
        "gsur", "gsur_male", "gsur_female",
        "u_rate", "u_rate_male", "u_rate_female",
    })
    
    # ---- Weights and metadata ----
    essential.update({
        "dwt", "dwtx", "weight",
        "idperson_draw", "idhh_draw",
        "sample_group",
        "other_members_income",
        # Original IDs (couples reshape)
        "idorighh", "idorigperson", "idfather", "idmother",
        # Household composition
        "hh_IsHead", "hh_IsPartner",
    })
    
    # ---- Post-estimation (Step 8) ----
    essential.update({
        # Predicted values
        "log_opp", "log_opp_male", "log_opp_female",
        # Probabilities
        "prob", "log_prob",
    })
    
    return essential


def filter_to_essential_columns(df: pd.DataFrame, group: str = "unknown") -> pd.DataFrame:
    """
    Filter dataframe to essential columns only, reducing file size by ~85-90%.
    
    Parameters
    ----------
    df : pd.DataFrame
        Full MNL dataset with 900+ columns
    group : str
        Group name for logging (e.g., "singles", "couples")
    
    Returns
    -------
    pd.DataFrame
        Filtered dataframe with ~100 essential columns
    """
    essential = get_essential_columns_for_estimation()
    
    # Find which essential columns actually exist in the dataframe
    available = set(df.columns)
    to_keep = sorted(essential & available)
    
    # Log what we're keeping vs dropping
    n_original = len(df.columns)
    n_kept = len(to_keep)
    n_dropped = n_original - n_kept
    pct_reduction = 100.0 * n_dropped / n_original if n_original > 0 else 0.0
    
    logging.info(f"Column filtering ({group}):")
    logging.info(f"  Original columns: {n_original}")
    logging.info(f"  Essential columns kept: {n_kept}")
    logging.info(f"  Columns dropped: {n_dropped} ({pct_reduction:.1f}% reduction)")
    
    # Show sample of dropped columns (first 10)
    dropped_cols = sorted(available - essential)
    if dropped_cols:
        sample_dropped = dropped_cols[:10]
        logging.info(f"  Sample dropped: {sample_dropped}")
        if len(dropped_cols) > 10:
            logging.info(f"  ... and {len(dropped_cols) - 10} more")
    
    # Return filtered dataframe
    return df[to_keep].copy()


# =========================================================================
# FILE WRITING
# =========================================================================

def write_mnl_outputs(
    singles_df: pd.DataFrame,
    out_base: Path,
    metadata: Dict[str, Any],
    *,
    couples_df: Optional[pd.DataFrame] = None,
    write_combined: bool = False,
    filter_columns: bool = True  # NEW: Enable column filtering by default
) -> Dict[str, Path]:
    """
    Write MNL outputs with separate singles/couples files + metadata sidecar.

    Outputs:
        - {out_base}__singles.parquet
        - {out_base}__couples.parquet (if couples_df provided)
        - {out_base}__mnlmeta.json (metadata sidecar)
        - {out_base}__combined.parquet (optional, if write_combined=True)

    Parameters
    ----------
    singles_df : pd.DataFrame
        Singles MNL dataset
    out_base : Path
        Output base path (without extension)
    metadata : Dict[str, Any]
        Metadata dictionary to write to sidecar JSON
    couples_df : Optional[pd.DataFrame]
        Couples MNL dataset (if None, couples file not written)
    write_combined : bool
        If True, also write combined singles+couples file
    filter_columns : bool
        If True, filter to essential columns before writing (reduces file size by ~85-90%)

    Returns
    -------
    Dict[str, Path]
        Dictionary mapping output type to file path
    """
    outputs = {}

    # Apply column filtering if requested
    if filter_columns:
        logging.info("=" * 80)
        logging.info("COLUMN FILTERING ENABLED")
        logging.info("=" * 80)
        singles_df = filter_to_essential_columns(singles_df, group="singles")
        if couples_df is not None:
            couples_df = filter_to_essential_columns(couples_df, group="couples")

    # Singles
    singles_path = out_base.parent / f"{out_base.stem}__singles.parquet"
    singles_df.to_parquet(singles_path, index=False)
    outputs["singles"] = singles_path
    
    # Calculate file size
    size_mb = singles_path.stat().st_size / (1024 * 1024)
    logging.info(f"Wrote singles MNL: {singles_path} ({len(singles_df):,} rows, {len(singles_df.columns)} cols, {size_mb:.1f} MB)")

    # Couples (if provided)
    if couples_df is not None:
        couples_path = out_base.parent / f"{out_base.stem}__couples.parquet"
        couples_df.to_parquet(couples_path, index=False)
        outputs["couples"] = couples_path
        
        size_mb = couples_path.stat().st_size / (1024 * 1024)
        logging.info(f"Wrote couples MNL: {couples_path} ({len(couples_df):,} rows, {len(couples_df.columns)} cols, {size_mb:.1f} MB)")

    # Metadata sidecar
    meta_path = out_base.parent / f"{out_base.stem}__mnlmeta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    outputs["metadata"] = meta_path
    logging.info(f"Wrote metadata sidecar: {meta_path}")

    # Combined (optional)
    if write_combined:
        frames = [singles_df]
        if couples_df is not None:
            frames.append(couples_df)

        combined_df = pd.concat(frames, axis=0, ignore_index=True)
        combined_path = out_base.parent / f"{out_base.stem}__combined.parquet"
        combined_df.to_parquet(combined_path, index=False)
        outputs["combined"] = combined_path
        
        size_mb = combined_path.stat().st_size / (1024 * 1024)
        logging.info(f"Wrote combined MNL: {combined_path} ({len(combined_df):,} rows, {len(combined_df.columns)} cols, {size_mb:.1f} MB)")

    return outputs


# =========================================================================
# CLI ARGUMENT PARSING
# =========================================================================

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Enhanced RURO MNL estimation dataset preparation."
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
        help="Path to combined_draws_em.parquet (from enh_RURO_euromod.py).",
    )
    ap.add_argument(
        "--out-base",
        type=str,
        required=True,
        help="Base path for output (without extension), e.g. fr_2021_RURO_mnl",
    )

    # Prior parameters (overridden by drawsmeta if provided)
    ap.add_argument(
        "--drawsmeta",
        type=str,
        default=None,
        help="Path to drawsmeta JSON sidecar (e.g., singles_...__drawsmeta.json). "
             "Overrides prior parameters to match draw generation."
    )
    ap.add_argument(
        "--wage-spec",
        type=str,
        choices=["fw", "vw"],
        default=DEFAULT_WAGE_SPEC,
        help="Wage opportunity specification: 'fw' fixed or 'vw' variable.",
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
        help="Lower bound of hour support.",
    )
    ap.add_argument(
        "--h-max",
        type=float,
        default=DEFAULT_H_MAX,
        help="Upper bound of hour support.",
    )
    ap.add_argument(
        "--w-min",
        type=float,
        default=DEFAULT_W_MIN,
        help="Lower bound of wage support.",
    )
    ap.add_argument(
        "--w-max",
        type=float,
        default=DEFAULT_W_MAX,
        help="Upper bound of wage support.",
    )

    # GSUR integration
    ap.add_argument(
        "--gsur-file",
        type=str,
        default=None,
        help="Path to GSUR lookup file (FR_gsur_ruro.parquet from enh_prepare_FR_gsur.py). "
             "Required for estimation with unemployment-rate-adjusted opportunities."
    )

    # Output options
    ap.add_argument(
        "--write-combined",
        action="store_true",
        help="Write combined singles+couples parquet in addition to separate files."
    )
    ap.add_argument(
        "--allow-unbalanced-couples",
        action="store_true",
        help="Allow couples households with != 2 rows per draw (not recommended)."
    )
    ap.add_argument(
        "--no-column-filter",
        action="store_true",
        help="Disable column filtering (write all columns instead of ~100 essential). "
             "By default, only essential columns are written to reduce file size by ~85-90%%."
    )

    # Metadata
    ap.add_argument(
        "--year",
        type=int,
        default=None,
        help="Year of the dataset (for metadata only).",
    )

    return ap.parse_args()


# =========================================================================
# MAIN
# =========================================================================

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    args = parse_args()

    # -------------------------------------------------------------------------
    # 1. Load drawsmeta and override prior parameters
    # -------------------------------------------------------------------------
    if args.drawsmeta:
        meta_full = _load_drawsmeta(Path(args.drawsmeta))
        # enh_RURO_draws.py writes prior parameters under "distributional_params";
        # accept that nested form first, fall back to flat for older sidecars.
        meta = meta_full.get("distributional_params", meta_full)

        # Override with draws parameters
        args.h_min = meta["h_min"]
        args.h_max = meta["h_max"]
        args.w_min = meta["w_min"]
        args.w_max = meta["w_max"]
        args.pi0_m = meta.get("pi0_m", args.pi0_m)
        args.pi0_f = meta.get("pi0_f", args.pi0_f)
        args.wage_spec = meta.get("wage_spec", args.wage_spec)

        logging.info(f"Loaded prior parameters from drawsmeta: {args.drawsmeta}")
        logging.info(f"  h_min={args.h_min}, h_max={args.h_max}")
        logging.info(f"  w_min={args.w_min}, w_max={args.w_max}")
        logging.info(f"  pi0_m={args.pi0_m}, pi0_f={args.pi0_f}")
        logging.info(f"  wage_spec={args.wage_spec}")

    # -------------------------------------------------------------------------
    # 2. Load EUROMOD outputs
    # -------------------------------------------------------------------------
    em_path = Path(args.euromod_combined).resolve()
    if not em_path.exists():
        raise FileNotFoundError(f"EUROMOD combined file not found: {em_path}")
    em_df = _read_df(em_path)
    logging.info(f"Loaded EUROMOD outputs: {len(em_df):,} rows")

    # -------------------------------------------------------------------------
    # 3. Load GSUR lookup (if provided)
    # -------------------------------------------------------------------------
    gsur_df = None
    if args.gsur_file:
        gsur_path = Path(args.gsur_file).resolve()
        if not gsur_path.exists():
            raise FileNotFoundError(f"GSUR file not found: {gsur_path}")
        gsur_df = _read_df(gsur_path)
        logging.info(f"Loaded GSUR lookup: {len(gsur_df):,} rows")

    # -------------------------------------------------------------------------
    # 4. Process singles
    # -------------------------------------------------------------------------
    singles_path = Path(args.singles_draws).resolve()
    if not singles_path.exists():
        raise FileNotFoundError(f"Singles draws file not found: {singles_path}")

    singles_long = _read_df(singles_path)
    logging.info(f"Loaded singles draws: {len(singles_long):,} rows")

    singles_long = _merge_euromod_outputs(singles_long, em_df)
    singles_long = _restrict_to_deciders(singles_long)

    # NOTE: LES filtering (allowed_les = [3, 5, 7]) is already enforced at household-level
    # in enh_france_data_prep.py. All remaining deciders (filtered by _restrict_to_deciders above)
    # are guaranteed to have les in [3,5,7]. The redundant ruro_lma filter has been removed.
    logging.info(
        f"Singles estimation sample after decider restriction: {len(singles_long):,} rows"
    )

    # Empty sample guard
    if singles_long.empty:
        raise RuntimeError(
            "Singles sample is empty after decider/lma filtering. "
            "Fix lma/decider definitions upstream or check data quality."
        )

    singles_mnl = _build_mnl_block(singles_long, sample_group="singles")

    # Merge GSUR
    if gsur_df is not None:
        singles_mnl = _merge_gsur_singles(singles_mnl, gsur_df)

    # Normalize
    singles_mnl, singles_scaling = _normalize_singles(singles_mnl)

    # Compute prior
    singles_mnl = _compute_prior_singles(
        singles_mnl,
        wage_spec=args.wage_spec,
        pi0_m=args.pi0_m,
        pi0_f=args.pi0_f,
        h_min=args.h_min,
        h_max=args.h_max,
        w_min=args.w_min,
        w_max=args.w_max,
    )

    logging.info(f"Singles MNL dataset ready: {len(singles_mnl):,} rows, {len(singles_mnl.columns)} columns")

    # -------------------------------------------------------------------------
    # 5. Process couples (if provided)
    # -------------------------------------------------------------------------
    couples_mnl = None
    couples_scaling = None

    if args.couples_draws:
        couples_path = Path(args.couples_draws).resolve()
        if not couples_path.exists():
            raise FileNotFoundError(f"Couples draws file not found: {couples_path}")

        couples_long = _read_df(couples_path)
        logging.info(f"Loaded couples draws: {len(couples_long):,} rows")

        couples_long = _merge_euromod_outputs(couples_long, em_df)
        couples_long = _restrict_to_deciders(couples_long)

        # NOTE: LES filtering (allowed_les = [3, 5, 7]) is already enforced at household-level
        # in enh_france_data_prep.py. All remaining deciders (filtered by _restrict_to_deciders above)
        # are guaranteed to have les in [3,5,7]. The redundant ruro_lma filter has been removed.
        logging.info(
            f"Couples estimation sample after decider restriction: {len(couples_long):,} rows"
        )

        # Empty sample guard: skip entire couples pipeline if no data
        if couples_long.empty:
            logging.warning(
                "Couples sample empty after decider/lma filtering. Skipping couples pipeline."
            )
            couples_mnl = None
            couples_scaling = None
        else:
            # =====================================================================
            # Runtime sanity check: Validate couples gender composition BEFORE reshape
            # =====================================================================
            logging.info("Running couples gender balance sanity check before reshape...")
            try:
                sanity_report_couples_gender_balance(couples_long, stage="MNL_prep_couples")
                logging.info("✓ Couples gender balance check passed")
            except Exception as e:
                logging.error(f"Couples gender balance FAILED: {e}")
                raise

            # Reshape to wide format (with validation)
            couples_wide = _reshape_couples_to_wide(couples_long, allow_unbalanced=args.allow_unbalanced_couples)

            couples_mnl = _build_mnl_block_couples_wide(couples_wide, sample_group="couples")

            # Merge GSUR
            if gsur_df is not None:
                couples_mnl = _merge_gsur_couples_wide(couples_mnl, gsur_df)

            # Normalize
            couples_mnl, couples_scaling = _normalize_couples_wide(couples_mnl)

            # Compute prior
            couples_mnl = _compute_prior_couples_wide(
                couples_mnl,
                wage_spec=args.wage_spec,
                pi0_m=args.pi0_m,
                pi0_f=args.pi0_f,
                h_min=args.h_min,
                h_max=args.h_max,
                w_min=args.w_min,
                w_max=args.w_max,
            )

            logging.info(f"Couples MNL dataset ready: {len(couples_mnl):,} rows, {len(couples_mnl.columns)} columns")

    # -------------------------------------------------------------------------
    # 6. Build metadata sidecar
    # -------------------------------------------------------------------------
    metadata = {
        "script": "enh_RURO_prep_mnl_basic.py",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "inputs": {
            "singles_draws": str(singles_path),
            "couples_draws": str(couples_path) if args.couples_draws else None,
            "euromod_combined": str(em_path),
            "gsur_file": str(args.gsur_file) if args.gsur_file else None,
            "drawsmeta": str(args.drawsmeta) if args.drawsmeta else None,
        },
        "prior_parameters": {
            "wage_spec": args.wage_spec,
            "pi0_m": args.pi0_m,
            "pi0_f": args.pi0_f,
            "h_min": args.h_min,
            "h_max": args.h_max,
            "w_min": args.w_min,
            "w_max": args.w_max,
            "source": "drawsmeta" if args.drawsmeta else "CLI arguments",
            "effective_prior_source_singles": singles_mnl.attrs.get("prior_source", "unknown"),
            "effective_prior_source_couples": (
                couples_mnl.attrs.get("prior_source", "unknown") if couples_mnl is not None else None
            ),
        },
        "sample_sizes": {
            "singles_deciders": int(singles_mnl[singles_mnl["is_chosen"] == 1]["idperson"].nunique()) if "is_chosen" in singles_mnl.columns and "idperson" in singles_mnl.columns else len(singles_mnl),
            "couples_deciders": int(couples_mnl[couples_mnl["is_chosen"] == 1]["idhh"].nunique()) if couples_mnl is not None and "is_chosen" in couples_mnl.columns and "idhh" in couples_mnl.columns else 0,
            "singles_total_rows": len(singles_mnl),
            "couples_total_rows": len(couples_mnl) if couples_mnl is not None else 0,
            "n_draws": len(singles_mnl["draw"].unique()) if "draw" in singles_mnl.columns else None,
        },
        "normalization": {
            "singles": singles_scaling,
            "couples": couples_scaling,
        },
        "columns": {
            "singles": list(singles_mnl.columns),
            "couples": list(couples_mnl.columns) if couples_mnl is not None else None,
        },
        "year": args.year,
    }

    # -------------------------------------------------------------------------
    # 6.5. Runtime sanity checks on final MNL datasets
    # -------------------------------------------------------------------------
    logging.info("\n" + "=" * 80)
    logging.info("Running final MNL dataset sanity checks...")
    logging.info("=" * 80)

    # Singles sanity checks
    try:
        sanity_report_mnl_dataset(singles_mnl, household_type="singles", metadata=metadata)
        logging.info("✓ Singles MNL dataset passed all sanity checks")
    except Exception as e:
        logging.error(f"Singles MNL dataset FAILED sanity checks: {e}")
        raise

    # Couples sanity checks (if couples data exists)
    if couples_mnl is not None and not couples_mnl.empty:
        try:
            sanity_report_mnl_dataset(couples_mnl, household_type="couples", metadata=metadata)
            logging.info("✓ Couples MNL dataset passed all sanity checks")
        except Exception as e:
            logging.error(f"Couples MNL dataset FAILED sanity checks: {e}")
            raise

    logging.info("All MNL dataset sanity checks passed ✓\n")

    # -------------------------------------------------------------------------
    # 7. Write outputs
    # -------------------------------------------------------------------------
    out_base = Path(args.out_base).resolve()
    outputs = write_mnl_outputs(
        singles_mnl,
        out_base,
        metadata,
        couples_df=couples_mnl,
        write_combined=args.write_combined,
        filter_columns=not args.no_column_filter  # Default: filter enabled
    )

    print("\n" + "=" * 80)
    print("MNL dataset preparation complete!")
    print("=" * 80)
    print("\nOutput files:")
    for k, v in outputs.items():
        print(f"  {k}: {v}")
    print()


if __name__ == "__main__":
    main()
