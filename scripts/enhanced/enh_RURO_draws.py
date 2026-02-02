#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-12-01 14:41:57
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/

"""
RURO_draws.py
=============

Implements the opportunity set generation for a Random Utility Random Opportunity
(RURO) labour supply model à la Aaberge & Colombino (1998) and Capeau & Decoster (2014).

Key Design Decisions
--------------------
1. **Deciders only**: The choice set is defined only for household decision makers
   (head and partner, flagged by `hh_IsHead` and `hh_IsPartner`). Children and other
   household members are *not* given simulated opportunities; they appear only with
   draw=0 and their observed hours/wage in this file. Non-deciders are replicated
   across all draws later in enh_RURO_euromod.py to ensure EUROMOD can correctly
   compute household-level tax-benefit outcomes for all draws.

2. **RURO opportunity density**:
   For each decider i:
   - With probability π₀,g(i) (gender-specific: pi0_m for men, pi0_f for women),
     the opportunity is **non-employment**: hours=0, wage=0, loc=-1.
   - With probability 1 - π₀,g(i), the opportunity is a **working job**:
       * hours ~ Uniform[h_min, h_max]
       * wage  ~ Uniform[w_min, w_max] if wage_spec="vw" (variable wage), else
                 fixed to observed wage if wage_spec="fw" (fixed wage)
       * occupation (loc):
         - If occ_spec="fixed": occupation is NOT sampled; working draws use
           baseline (observed) occupation, log_q_occ=0
         - If occ_spec="empirical": occupation is sampled from empirical
           frequencies (conditional on working, by stratum), contributing to
           the proposal density via log_q_occ

   **Gender-specific π₀**: The mass at zero hours depends only on gender (dgn),
   NOT on baseline labour market status (lma). This ensures all observed
   alternatives (including hours=0 for deciders) have positive proposal density.

3. **Observed job**: draw=0 preserves the baseline hours, wage, and occupation
   exactly (using lhw_base, yivwg_base columns). No perturbation.

Performance Optimization
------------------------
The `generate_draws_long()` function uses **fully vectorized NumPy/Pandas operations**
instead of Python loops for ~100x speedup on large datasets:

- All random draws (employment status, hours, wages) are generated in single
  vectorized calls to `numpy.random.Generator`
- DataFrame replication uses efficient `iloc` indexing with `np.repeat`
- No `iterrows()` or Python-level loops over individuals/draws

The vectorized implementation processes all n_deciders × n_draws records in bulk,
making it suitable for large-scale microsimulation studies.

From singles_RURO_ready / couples_RURO_ready (wide, one row per person),
construct a long RURO dataset with simulated opportunities:

  - draw = 0: observed job (chosen alternative)
  - draw >= 1: simulated opportunities from the RURO prior over (hours, wage)

This is the step that creates the (i, draw) structure for RURO_prep_mnl.py.
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

# Add parent directory to path for sanity_checks import
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
except NameError:
    SCRIPT_DIR = Path.cwd()

from sanity_checks import sanity_report_draws  # type: ignore  # noqa: E402


# ---------------------------------------------------------------------------
# Defaults 
# ---------------------------------------------------------------------------

TOTAL_LEISURE_HOURS = 80.0
WEEKS_PER_MONTH = 52.0 / 12.0

DCM_MIN_POSITIVE = 1e-6

DEFAULT_PI0_M = 0.10 # check the data for this info 
DEFAULT_PI0_F = 0.10

DEFAULT_H_MIN = 5.0
DEFAULT_H_MAX = 70.0
DEFAULT_W_MIN = 2.0
DEFAULT_W_MAX = 170.0

DEFAULT_WAGE_SPEC = "vw"  # "fw" or "vw"
DEFAULT_N_DRAWS = 99
DEFAULT_RNG_SEED = 17  # Lucky number for reproducibility


# --- Occupation (LOC = occupation, not location) ---
DEFAULT_OCC_SPEC = "fixed"  # "fixed" or "empirical"
DEFAULT_OCC_STRATA = ("dgn", "educ3")
DEFAULT_OCC_MIN_CELL = 30  # minimum obs per stratum for empirical probs
POOLED_STRATUM_KEY = ("__pooled__",)



# ---------------------------------------------------------------------------
# I/O
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


def _write_dataframe(
    df: pd.DataFrame, base_path: Path, suffix: str = "_draws"
) -> Dict[str, Path]:
    out_dir = base_path.parent
    base = base_path.stem + suffix
    parquet_path = out_dir / f"{base}.parquet"

    df.to_parquet(parquet_path, index=False, engine="pyarrow")  # type: ignore[arg-type]
    return {"parquet": parquet_path}


def _write_draws_metadata(
    output_path: Path,
    metadata: Dict[str, Any],
) -> None:
    """
    Write draws metadata sidecar JSON.

    Creates a file like: singles_RURO_draws__drawsmeta.json
    """
    sidecar_path = output_path.parent / f"{output_path.stem}__drawsmeta.json"

    metadata_json = {
        **metadata,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "script": "enh_RURO_draws.py",
    }

    try:
        with open(sidecar_path, "w", encoding="utf-8") as f:
            json.dump(metadata_json, f, indent=2)
        logging.info(f"Wrote draws metadata to {sidecar_path}")
    except Exception as e:
        logging.warning(f"Failed to write metadata {sidecar_path}: {e}")


def _compute_id_multiplier(max_draw: int) -> int:
    """
    Compute ID multiplier for EUROMOD stage: 10^ceil(log10(max_draw+1)), minimum 1000.

    This ensures unique IDs when multiplying: idperson_euromod = idperson_true * multiplier + draw
    """
    if max_draw < 0:
        return 1000
    import math
    multiplier = 10 ** math.ceil(math.log10(max_draw + 1))
    return max(multiplier, 1000)


def _validate_couples_draw_consistency(df: pd.DataFrame, household_type: str) -> None:
    """
    For couples data, validate that both deciders in each household have the same set of draws.

    Requirements:
    - Both deciders must have the same set of draw values
    - Both must have draw=0

    Raises ValueError if violated.
    """
    if household_type != "couples":
        return  # Skip validation for non-couples

    if "idhh_true" not in df.columns or "draw" not in df.columns:
        logging.warning("Cannot validate couples consistency: missing idhh_true or draw columns")
        return

    # Get deciders only
    is_decider = df.get("is_decider", pd.Series(1, index=df.index))
    deciders_df = df[is_decider == 1].copy()

    if len(deciders_df) == 0:
        return

    # For each household, check that all deciders have the same draw set
    violations = []

    for idhh, group in deciders_df.groupby("idhh_true"):
        n_deciders = group["idperson_true"].nunique() if "idperson_true" in group.columns else len(group["draw"].unique())

        # For couples, expect 2 deciders
        if n_deciders < 2:
            continue  # Not a couple household (might be single)

        # Get draw sets per decider
        if "idperson_true" in group.columns:
            draw_sets = group.groupby("idperson_true")["draw"].apply(set)
        else:
            # Fallback if idperson_true missing
            continue

        # Check if all deciders have the same draw set
        draw_sets_list = list(draw_sets.values)
        if len(draw_sets_list) < 2:
            continue

        first_set = draw_sets_list[0]
        if not all(s == first_set for s in draw_sets_list):
            violations.append({
                "idhh_true": idhh,
                "n_deciders": n_deciders,
                "draw_sets": {pid: sorted(draws) for pid, draws in draw_sets.items()},
            })
        elif 0 not in first_set:
            violations.append({
                "idhh_true": idhh,
                "n_deciders": n_deciders,
                "issue": "missing_draw_0",
                "draw_sets": {pid: sorted(draws) for pid, draws in draw_sets.items()},
            })

    if violations:
        logging.error(
            f"Couples draw consistency validation failed: {len(violations)} households with inconsistent draws"
        )
        # Show first few violations
        for v in violations[:5]:
            logging.error(f"  Household {v['idhh_true']}: {v}")

        raise ValueError(
            f"Couples draw consistency validation failed: {len(violations)} households "
            f"have deciders with inconsistent draw sets or missing draw=0. "
            f"See logs for details."
        )

    logging.info(f"Couples draw consistency validation passed for {household_type}")


def _validate_draw0_baseline_compliance(
    df: pd.DataFrame,
    baseline_cols: Dict[str, str],
    tolerance: float = 1e-6,
) -> None:
    """
    Validate that draw=0 uses baseline labor inputs exactly for all deciders.

    Args:
        df: DataFrame with draws
        baseline_cols: Dict mapping draw column name to baseline column name
            e.g., {"lhw": "lhw_base", "yivwg": "yivwg_base"}
        tolerance: Numeric tolerance for equality check

    Raises ValueError if violated.
    """
    # Get draw=0 deciders only
    is_draw0 = df["draw"] == 0
    is_decider = df.get("is_decider", pd.Series(1, index=df.index)) == 1
    draw0_deciders = df[is_draw0 & is_decider].copy()

    if len(draw0_deciders) == 0:
        logging.warning("No draw=0 deciders found for baseline compliance check")
        return

    violations = []

    for draw_col, baseline_col in baseline_cols.items():
        if draw_col not in df.columns:
            logging.warning(f"Draw column {draw_col} not in output; skipping baseline check")
            continue
        if baseline_col not in df.columns:
            logging.warning(f"Baseline column {baseline_col} not in output; skipping baseline check")
            continue

        draw_vals = pd.to_numeric(draw0_deciders[draw_col], errors="coerce").fillna(0.0)
        base_vals = pd.to_numeric(draw0_deciders[baseline_col], errors="coerce").fillna(0.0)

        diff = np.abs(draw_vals - base_vals)
        bad_mask = diff > tolerance

        if bad_mask.any():
            n_violations = bad_mask.sum()
            violations.append({
                "column": draw_col,
                "baseline": baseline_col,
                "n_violations": n_violations,
                "max_diff": diff.max(),
            })

    if violations:
        logging.error(f"Draw=0 baseline compliance check failed:")
        for v in violations:
            logging.error(f"  {v['column']} vs {v['baseline']}: {v['n_violations']} violations, max_diff={v['max_diff']:.6f}")

        # Show sample violating rows
        sample_cols = ["idhh_true", "idperson_true"] + list(baseline_cols.keys()) + list(baseline_cols.values())
        sample_cols = [c for c in sample_cols if c in draw0_deciders.columns]

        for draw_col, baseline_col in baseline_cols.items():
            if draw_col in draw0_deciders.columns and baseline_col in draw0_deciders.columns:
                draw_vals = pd.to_numeric(draw0_deciders[draw_col], errors="coerce").fillna(0.0)
                base_vals = pd.to_numeric(draw0_deciders[baseline_col], errors="coerce").fillna(0.0)
                bad_mask = np.abs(draw_vals - base_vals) > tolerance
                if bad_mask.any():
                    sample = draw0_deciders[bad_mask][sample_cols].head(10)
                    logging.error(f"Sample violations for {draw_col}:\n{sample.to_string()}")
                    break

        raise ValueError(
            f"Draw=0 baseline compliance check failed: draw=0 does not match baseline labor inputs. "
            f"See logs for details."
        )

    # Log compliance summary
    n_deciders = len(draw0_deciders)
    logging.info(f"Draw=0 baseline compliance: 100% ({n_deciders}/{n_deciders} deciders compliant)")


# ---------------------------------------------------------------------------
# Household income helpers
# ---------------------------------------------------------------------------
def _attach_other_members_income(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute other_members_income per household (sum of ils_dispy of non-head/partner).

    This aggregates the disposable income of children and other household members
    who are NOT decision makers (hh_IsHead==0 and hh_IsPartner==0).

    The resulting `other_members_income` column is used later in RURO_prep_mnl.py
    when computing total consumption for heads/partners only. It ensures that
    the utility specification correctly accounts for all household income sources
    even though only deciders have a choice set.
    """
    if "idhh" not in df.columns or "ils_dispy" not in df.columns:
        return df
    hh_is_head = (
        pd.to_numeric(df.get("hh_IsHead", 0), errors="coerce").fillna(0).astype(int)
    )
    hh_is_partner = (
        pd.to_numeric(df.get("hh_IsPartner", 0), errors="coerce").fillna(0).astype(int)
    )
    is_other = ~(hh_is_head.astype(bool) | hh_is_partner.astype(bool))
    other_income = df["ils_dispy"].where(is_other, 0.0)
    other_sum = other_income.groupby(df["idhh"]).sum()
    df["other_members_income"] = df["idhh"].map(other_sum).fillna(0.0)
    return df


# ---------------------------------------------------------------------------
# Occupation helpers (LOC = occupation, not location)
# ---------------------------------------------------------------------------

# _---------------------------------------------------------------------------
# create LOC distribution
# ---------------------------------------------------------------------------


def _infer_occ_col(df: pd.DataFrame) -> str:
    """
    Prefer task-group occupation 'loc4' if present.
    Fallback to 'loc_ruro' then 'loc' if needed (but Case B should use loc4).
    """
    for c in ("loc4", "loc_ruro", "loc"):
        if c in df.columns:
            return c
    raise KeyError("No occupation column found. Expected one of: loc4, loc_ruro, loc.")


def _build_occ_probs_by_stratum(
    df: pd.DataFrame,
    *,
    occ_col: str,
    strata_cols: tuple[str, ...],
    working_mask: pd.Series,
    valid_occ: tuple[int, ...] = (1, 2, 3, 4),
    min_cell: int = 30,
) -> dict[tuple, tuple[np.ndarray, np.ndarray]]:
    """
    Returns mapping:
        stratum_key -> (occ_values_array, prob_array)
    using empirical frequencies among WORKING individuals.

    Also stores a pooled fallback under POOLED_STRATUM_KEY.
    """
    use = df.loc[working_mask, list(strata_cols) + [occ_col]].copy()
    if use.empty:
        return {}

    # Fix dtype: convert occupation to numeric int reliably (Goal B)
    occ = pd.to_numeric(use[occ_col], errors="coerce").astype("Int64")
    use = use.loc[occ.isin(valid_occ)].copy()
    if use.empty:
        return {}

    # Overwrite occ_col with validated numeric values to ensure value_counts works
    use[occ_col] = occ.loc[use.index].astype(int)

    # pooled distribution
    pooled_counts = use[occ_col].value_counts(dropna=True)
    pooled_vals = pooled_counts.index.to_numpy(dtype=np.int16)
    pooled_p = (pooled_counts / pooled_counts.sum()).to_numpy(dtype=float)

    out: dict[tuple, tuple[np.ndarray, np.ndarray]] = {}
    out[POOLED_STRATUM_KEY] = (pooled_vals, pooled_p)

    # stratum sizes
    stratum_n = use.groupby(list(strata_cols), dropna=False).size()

    # stratum-specific distribution
    grp = use.groupby(list(strata_cols))[occ_col].value_counts(dropna=True)
    probs = grp / grp.groupby(level=list(range(len(strata_cols)))).sum()

    for key, sub in probs.groupby(level=list(range(len(strata_cols)))):
        key_t = tuple(key) if isinstance(key, tuple) else (key,)
        if float(stratum_n.loc[key]) < float(min_cell):
            continue  # will fallback to pooled

        occ_vals = np.array([int(ix[-1]) for ix in sub.index], dtype=np.int16)
        p = sub.to_numpy(dtype=float)
        p = p / p.sum()
        out[key_t] = (occ_vals, p)

    return out


def _sample_occ_vectorized_by_stratum(
    *,
    stratum_keys: np.ndarray,  # shape (n_sim,)
    probs_map: dict[tuple, tuple[np.ndarray, np.ndarray]],
    rng: np.random.Generator,
    fallback_occ: np.ndarray,  # shape (n_sim,) e.g. observed occ replicated
) -> tuple[np.ndarray, np.ndarray]:
    """
    Sample occupation per record, allowing stratum-specific probabilities.

    Returns:
      occ_drawn: int16 array
      log_q_occ: float array (log probability for drawn occ; 0 if fallback used)
    """
    n = len(stratum_keys)
    occ_out = fallback_occ.astype(np.int16, copy=True)
    logq = np.zeros(n, dtype=float)

    # For speed: handle each stratum in a small loop (few strata)
    # stratum_keys elements are tuples; stored as object dtype
    uniq = pd.unique(stratum_keys)
    for k in uniq:
        key = tuple(k) if isinstance(k, (list, tuple, np.ndarray)) else (k,)
        idx = np.where(stratum_keys == k)[0]
        spec = probs_map.get(key, None)
        if spec is None:
            spec = probs_map.get(POOLED_STRATUM_KEY, None)
        if spec is None:
            # absolute fallback: keep observed occupation
            continue
        occ_vals, p = spec
        draw_idx = rng.choice(len(occ_vals), size=len(idx), p=p)
        occ_draw = occ_vals[draw_idx]
        occ_out[idx] = occ_draw

        # log probability of the drawn occ
        # map occ_vals->p
        # small dict OK since occ_vals length ≤ 4
        p_map = {int(o): float(pp) for o, pp in zip(occ_vals, p)}
        logq[idx] = np.log([p_map[int(o)] for o in occ_draw])

    return occ_out, logq


def _log_q_occ_for_given_occ(
    *,
    occ: np.ndarray,  # shape (n,)
    stratum_keys: np.ndarray,  # shape (n,), object dtype tuples
    probs_map: dict[tuple, tuple[np.ndarray, np.ndarray]],
    eps: float = 1e-15,
) -> np.ndarray:
    """
    Compute log q_occ for a given occupation vector under the same stratum-specific
    empirical probabilities used for sampling.

    If a stratum is missing, falls back to POOLED_STRATUM_KEY. If an occupation code
    is missing from the stratum distribution, also falls back to pooled (then eps).
    """
    n = len(occ)
    out = np.zeros(n, dtype=float)
    if n == 0 or not probs_map:
        return out

    uniq = pd.unique(stratum_keys)
    pooled = probs_map.get(POOLED_STRATUM_KEY, None)
    pooled_map = None
    if pooled is not None:
        occ_vals_p, p_p = pooled
        pooled_map = {int(o): float(pp) for o, pp in zip(occ_vals_p, p_p)}

    for k in uniq:
        key = tuple(k) if isinstance(k, (list, tuple, np.ndarray)) else (k,)
        idx = np.where(stratum_keys == k)[0]
        spec = probs_map.get(key, None)
        if spec is None:
            spec = pooled
        if spec is None:
            continue

        occ_vals, p = spec
        p_map = {int(o): float(pp) for o, pp in zip(occ_vals, p)}
        probs = np.array([p_map.get(int(o), 0.0) for o in occ[idx]], dtype=float)

        if (probs == 0.0).any() and pooled_map is not None:
            probs = np.where(
                probs == 0.0,
                np.array([pooled_map.get(int(o), eps) for o in occ[idx]], dtype=float),
                probs,
            )

        out[idx] = np.log(np.clip(probs, eps, 1.0))

    return out


def _ensure_educ3(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure a 3-level education categorical variable exists:
      educ3 = 0 (low), 1 (middle), 2 (high)

    Priority:
      - if educ3 exists, keep it
      - else if educL/educH exist, construct it
      - else if deh exists, map it (customize if needed)
    """
    if "educ3" in df.columns:
        return df

    df = df.copy()

    if "educL" in df.columns and "educH" in df.columns:
        educL = pd.to_numeric(df["educL"], errors="coerce").fillna(0).astype(int)
        educH = pd.to_numeric(df["educH"], errors="coerce").fillna(0).astype(int)

        # Guard against invalid combination (should not happen; if it does, treat as missing -> middle)
        invalid = (educL == 1) & (educH == 1)
        if invalid.any():
            # choose your policy: set to middle (1) or set to NaN then later fallback
            educL = educL.mask(invalid, 0)
            educH = educH.mask(invalid, 0)

        educ3 = pd.Series(1, index=df.index, dtype=int)  # middle default
        educ3.loc[educL == 1] = 0
        educ3.loc[educH == 1] = 2
        df["educ3"] = educ3.astype(np.int8)
        return df

    # Optional mapping from deh (if you want draws to work even without educL/H)
    if "deh" in df.columns:
        deh = pd.to_numeric(df["deh"], errors="coerce")
        educ3 = pd.Series(1, index=df.index, dtype=int)
        educ3.loc[deh.isin([0, 1, 2])] = 0
        educ3.loc[deh.eq(5)] = 2
        df["educ3"] = educ3.astype(np.int8)
        return df

    # If nothing available, put everyone in one bucket
    df["educ3"] = 1
    return df


# ---------------------------------------------------------------------------
# Core: make long draws
# ---------------------------------------------------------------------------


def generate_draws_long(
    df: pd.DataFrame,
    *,
    n_draws: int = DEFAULT_N_DRAWS,
    wage_spec: str = DEFAULT_WAGE_SPEC,
    occ_spec: str = DEFAULT_OCC_SPEC,
    occ_strata: tuple[str, ...] = DEFAULT_OCC_STRATA,
    occ_min_cell: int = DEFAULT_OCC_MIN_CELL,
    pi0_m: float = DEFAULT_PI0_M,
    pi0_f: float = DEFAULT_PI0_F,
    h_min: float = DEFAULT_H_MIN,
    h_max: float = DEFAULT_H_MAX,
    w_min: float = DEFAULT_W_MIN,
    w_max: float = DEFAULT_W_MAX,
    rng_seed: int = DEFAULT_RNG_SEED,
) -> pd.DataFrame:
    """
    Take a RURO_ready dataset (one row per person) and return a long dataset
    with (idperson, draw) opportunities.

    RURO Opportunity Density (Aaberge–Colombino style)
    --------------------------------------------------
    For each decision maker i (head or partner):

    - With probability π₀,g(i):
        * Non-employment opportunity: hours=0, wage=0, loc=-1
        * π₀ is gender-specific: pi0_m for active men (lma==1, dgn==1),
          pi0_f for active women (lma==1, dgn==0).
      - With probability 1 - π₀,g(i):
        * Working job opportunity:
            - hours ~ Uniform[h_min, h_max]
            - wage  ~ Uniform[w_min, w_max] if wage_spec="vw",
                      or fixed to observed wage if wage_spec="fw"
            - loc is NOT drawn; working draws keep the baseline occupation

    Decider-Only Logic
    ------------------
    Following Stijn's RURO implementation:
    - If hh_IsHead and hh_IsPartner columns exist, only those individuals
      (heads and partners) get simulated draws (draw >= 1).
    - Non-deciders (children, other adults) appear only with draw=0 and
      their baseline hours/wage/loc in THIS file. They are replicated across
      all draws downstream in enh_RURO_euromod.py for EUROMOD household completeness.
    - If decider flags are missing, all persons are treated as deciders
      (with a warning).

    Occupation Specification
    ------------------------
    - occ_spec="fixed" (default): Occupation NOT sampled. Working draws keep
      baseline occupation, log_q_occ=0. Non-employment draws have loc=-1.
    - occ_spec="empirical": Occupation sampled from empirical frequencies
      conditional on working (by strata), contributing log_q_occ to proposal density.

    Output Structure
    ----------------
    - draw=0: observed job (baseline values from lhw_base/yivwg_base, is_chosen=1 for deciders)
    - draw>=1: simulated opportunities (is_chosen=0)
    """
    import logging

    if n_draws < 0:
        raise ValueError("n_draws must be >= 0")

    df = df.copy().reset_index(drop=True)
    df = _ensure_educ3(df)

    # =========================================================================
    # Ensure true IDs (Goal 1)
    # =========================================================================
    if "idperson_true" not in df.columns:
        if "idperson" in df.columns:
            df["idperson_true"] = df["idperson"].copy()
        else:
            raise KeyError("RURO_ready must contain 'idperson' or 'idperson_true'")

    if "idhh_true" not in df.columns:
        if "idhh" in df.columns:
            df["idhh_true"] = df["idhh"].copy()
        else:
            raise KeyError("RURO_ready must contain 'idhh' or 'idhh_true'")

    # -------------------------------------------------------------------------
    # Canonical hours / wage aliases (ALWAYS)
    #   hours := lhw (weekly hours)
    #   wage  := yivwg (hourly wage)  [fallback: wage_final if present]
    # -------------------------------------------------------------------------
    if "lhw" not in df.columns:
        raise KeyError("RURO_ready must contain 'lhw' (weekly hours).")
    df["lhw"] = pd.to_numeric(df["lhw"], errors="coerce").fillna(0.0)
    df["hours"] = df["lhw"]  # overwrite any stale 'hours'

    # =========================================================================
    # Canonicalize baseline columns (robustness fix)
    # =========================================================================
    # If lhw_base or yivwg_base exist from upstream prep but differ from the
    # canonical cleaned values (lhw, yivwg/wage_final), we must synchronize
    # them to prevent draw=0 support checks from failing on stale data.
    #
    # This prevents errors like: upstream lhw_base=130 while canonical lhw=70
    # after capping/harmonization in prep stage.

    # A) Hours baseline canonicalization
    h_cur = pd.to_numeric(df["lhw"], errors="coerce").fillna(0.0)

    if "lhw_base" in df.columns:
        h_old = pd.to_numeric(df["lhw_base"], errors="coerce").fillna(0.0)

        # Check if baseline differs materially from canonical
        if not np.allclose(h_old.values, h_cur.values, atol=1e-9, rtol=0.0):
            # Preserve raw baseline for diagnostics
            if "lhw_base_raw" not in df.columns:
                df["lhw_base_raw"] = h_old.copy()

            # Count differences
            n_changed = (np.abs(h_old.values - h_cur.values) > 1e-9).sum()

            # Stats for positive hours only (working deciders)
            working_mask_old = h_old > 0
            working_mask_cur = h_cur > 0

            if working_mask_old.any():
                old_stats = h_old[working_mask_old].describe(percentiles=[])
                old_str = f"min={old_stats['min']:.2f}, median={old_stats['50%']:.2f}, max={old_stats['max']:.2f}"
            else:
                old_str = "no positive hours"

            if working_mask_cur.any():
                cur_stats = h_cur[working_mask_cur].describe(percentiles=[])
                cur_str = f"min={cur_stats['min']:.2f}, median={cur_stats['50%']:.2f}, max={cur_stats['max']:.2f}"
            else:
                cur_str = "no positive hours"

            logging.warning(
                f"RURO_draws: lhw_base differs from canonical lhw in {n_changed} rows. "
                f"Overwriting lhw_base with canonical lhw to prevent stale baseline issues.\n"
                f"  Old lhw_base (positive): {old_str}\n"
                f"  New lhw_base (positive): {cur_str}\n"
                f"  Raw baseline preserved in 'lhw_base_raw' column."
            )

            # Overwrite with canonical
            df["lhw_base"] = h_cur.copy()
    else:
        # No baseline column exists - create from canonical
        df["lhw_base"] = h_cur.copy()
        logging.info("Created lhw_base from canonical lhw for draw=0 baseline compliance")

    # B) Wage baseline canonicalization
    # Canonical wage: prefer yivwg, fallback to wage_final
    if "yivwg" in df.columns:
        y_cur = pd.to_numeric(df["yivwg"], errors="coerce").fillna(0.0)
    elif "wage_final" in df.columns:
        y_cur = pd.to_numeric(df["wage_final"], errors="coerce").fillna(0.0)
    else:
        y_cur = pd.Series(0.0, index=df.index)

    if "yivwg_base" in df.columns:
        y_old = pd.to_numeric(df["yivwg_base"], errors="coerce").fillna(0.0)

        # Check if baseline differs materially from canonical
        if not np.allclose(y_old.values, y_cur.values, atol=1e-9, rtol=0.0):
            # Preserve raw baseline for diagnostics
            if "yivwg_base_raw" not in df.columns:
                df["yivwg_base_raw"] = y_old.copy()

            # Count differences
            n_changed = (np.abs(y_old.values - y_cur.values) > 1e-9).sum()

            # Stats for positive wages only (working deciders)
            working_mask_old = y_old > 0
            working_mask_cur = y_cur > 0

            if working_mask_old.any():
                old_stats = y_old[working_mask_old].describe(percentiles=[])
                old_str = f"min={old_stats['min']:.2f}, median={old_stats['50%']:.2f}, max={old_stats['max']:.2f}"
            else:
                old_str = "no positive wages"

            if working_mask_cur.any():
                cur_stats = y_cur[working_mask_cur].describe(percentiles=[])
                cur_str = f"min={cur_stats['min']:.2f}, median={cur_stats['50%']:.2f}, max={cur_stats['max']:.2f}"
            else:
                cur_str = "no positive wages"

            logging.warning(
                f"RURO_draws: yivwg_base differs from canonical wage in {n_changed} rows. "
                f"Overwriting yivwg_base with canonical wage to prevent stale baseline issues.\n"
                f"  Old yivwg_base (positive): {old_str}\n"
                f"  New yivwg_base (positive): {cur_str}\n"
                f"  Raw baseline preserved in 'yivwg_base_raw' column."
            )

            # Overwrite with canonical
            df["yivwg_base"] = y_cur.copy()
    else:
        # No baseline column exists - create from canonical
        df["yivwg_base"] = y_cur.copy()
        logging.info("Created yivwg_base from canonical wage for draw=0 baseline compliance")

    # Prefer yivwg as requested; but if missing/unreliable for some, fallback to wage_final
    if "yivwg" in df.columns:
        df["yivwg"] = pd.to_numeric(df["yivwg"], errors="coerce")
    else:
        df["yivwg"] = np.nan

    if "wage_final" in df.columns:
        wf = pd.to_numeric(df["wage_final"], errors="coerce")
    else:
        wf = pd.Series(np.nan, index=df.index)

    # Wage alias used by draws:
    # - if yivwg is present use it
    # - otherwise use wage_final
    df["wage"] = df["yivwg"].where(df["yivwg"].notna(), wf)
    df["wage"] = pd.to_numeric(df["wage"], errors="coerce").fillna(0.0)

    hours = df["hours"]
    wage = df["wage"]

    # -------------------------------------------------------------------------
    # Basic checks: idperson is required
    # -------------------------------------------------------------------------
    if "idperson" not in df.columns:
        raise KeyError("RURO_ready dataset must contain 'idperson'.")

    # -------------------------------------------------------------------------
    # Decider mask: only heads and partners get simulated opportunities
    # -------------------------------------------------------------------------
    has_decider_flags = "hh_IsHead" in df.columns
    if has_decider_flags:
        hh_is_head = (
            pd.to_numeric(df["hh_IsHead"], errors="coerce").fillna(0).astype(int)
        )
        hh_is_partner = (
            pd.to_numeric(df.get("hh_IsPartner", 0), errors="coerce")
            .fillna(0)
            .astype(int)
        )
        is_decider = (hh_is_head == 1) | (hh_is_partner == 1)
        n_deciders = is_decider.sum()
        n_nondeciders = (~is_decider).sum()
        logging.info(
            f"RURO_draws: {n_deciders} deciders, {n_nondeciders} non-deciders in input."
        )
    else:
        # No decider flags: assume all persons are deciders (backwards-compatible)
        logging.warning(
            "RURO_draws: hh_IsHead/hh_IsPartner columns not found. "
            "Assuming all persons in input are decision makers (heads/partners). "
            "If this is incorrect, ensure upstream filtering or add decider flags."
        )
        is_decider = pd.Series(True, index=df.index)
        
    # -------------------------------------------------------------------------
    # Occupation column (LOC = occupation, not location)
    # -------------------------------------------------------------------------
    occ_col = _infer_occ_col(df)

    # -------------------------------------------------------------------------
    # Labour market / gender indicators for π₀ (mass at zero hours)
    # -------------------------------------------------------------------------
    # lma: labour market activity flag (1 = active)
    # dgn: gender (1 = male, 0 = female in EUROMOD convention)
    if "lma" in df.columns:
        lma = pd.to_numeric(df["lma"], errors="coerce").fillna(1).astype(int)
    else:
        lma = pd.Series(1, index=df.index, dtype=int)
    if "dgn" in df.columns:
        dgn = pd.to_numeric(df["dgn"], errors="coerce").fillna(1).astype(int)
    else:
        dgn = pd.Series(1, index=df.index, dtype=int)

    # π₀ vector: probability of non-employment opportunity (mass at zero hours).
    #
    # IMPORTANT: π₀ depends ONLY on gender (dgn), NOT on baseline labour-market
    # status (lma). This ensures the observed alternative (draw=0) has strictly
    # positive proposal density even if hours==0 for deciders. RURO draws are
    # hypothetical opportunities; even currently inactive persons may receive
    # job offers, and observed non-employment must be in the support of q(·).
    pi0_vec = np.full(len(df), 0.5 * (pi0_m + pi0_f), dtype=float)
    dgn_arr = dgn.to_numpy()
    pi0_vec[dgn_arr == 1] = pi0_m  # men
    pi0_vec[dgn_arr == 0] = pi0_f  # women    
    # # -------------------------------------------------------------------------
    # Random generator for hours/wages only (VECTORIZED)
    # -------------------------------------------------------------------------
    # We no longer draw occupations (loc). The opportunity density
    # is over hours and wages only, as in Stijn's RURO implementation.
    rng = np.random.default_rng(rng_seed)

    # =========================================================================
    # VECTORIZED IMPLEMENTATION (replaces slow iterrows loop)
    # =========================================================================
    #
    # Strategy:
    # 1. Create draw=0 records for ALL persons (observed job)
    # 2. For deciders only, create draws 1..n_draws using vectorized operations
    # 3. Concatenate efficiently using pandas
    #
    # This is ~100x faster than iterrows for large datasets.
    # =========================================================================

    # -------------------------------------------------------------------------
    # Part 1: Observed job (draw=0) for ALL persons
    # -------------------------------------------------------------------------
    df_draw0 = df.copy()
    df_draw0["draw"] = 0
    df_draw0["is_decider"] = is_decider.astype(int)

    # =========================================================================
    # Goal 6: Enforce draw=0 uses baseline labor inputs exactly
    # =========================================================================
    # For deciders, set draw=0 hours/wage from baseline columns
    if is_decider.any():
        df_draw0.loc[is_decider, "lhw"] = df_draw0.loc[is_decider, "lhw_base"]
        df_draw0.loc[is_decider, "hours"] = df_draw0.loc[is_decider, "lhw_base"]
        df_draw0.loc[is_decider, "yivwg"] = df_draw0.loc[is_decider, "yivwg_base"]
        df_draw0.loc[is_decider, "wage"] = df_draw0.loc[is_decider, "yivwg_base"]
        if "wage_ruro" in df_draw0.columns:
            df_draw0.loc[is_decider, "wage_ruro"] = df_draw0.loc[is_decider, "yivwg_base"]

        # Recompute yem from baseline if present
        if "yem" in df_draw0.columns:
            df_draw0.loc[is_decider, "yem"] = (
                df_draw0.loc[is_decider, "yivwg_base"]
                * df_draw0.loc[is_decider, "lhw_base"]
                * WEEKS_PER_MONTH
            )

    # chosen alternative should exist ONLY for agents with a choice set
    df_draw0["is_chosen"] = df_draw0["is_decider"]
    # Non-employment convention: occupation is undefined -> set to -1 when hours==0
    # (keep baseline occupation in df/decider_df for working draws of currently non-working people)
    df_draw0.loc[
        pd.to_numeric(df_draw0["hours"], errors="coerce").fillna(0.0).to_numpy() <= 0.0,
        occ_col,
    ] = -1

    # proposal components are defined only for simulated draws; set 0 on draw=0
    df_draw0["log_q_state"] = 0.0
    df_draw0["log_q_hours"] = 0.0
    df_draw0["log_q_wage"] = 0.0
    df_draw0["log_q_occ"] = 0.0
    df_draw0["log_q_total"] = 0.0

    # If no draws requested, return just the observed jobs
    if n_draws == 0:
        return df_draw0.reset_index(drop=True)

    # -------------------------------------------------------------------------
    # Part 2: Simulated opportunities (draw >= 1) for DECIDERS ONLY
    # -------------------------------------------------------------------------
    decider_df = df[is_decider].copy().reset_index(drop=True)

    n_deciders_actual = len(decider_df)

    if n_deciders_actual == 0:
        logging.warning(
            "RURO_draws: No deciders found. Returning only observed jobs (draw=0)."
        )
        return df_draw0.reset_index(drop=True)

    logging.info(
        f"RURO_draws: Generating {n_draws} draws for {n_deciders_actual} deciders (vectorized)..."
    )

    # ---------------------------------------------------------------------
    # Proposal density for the OBSERVED alternative (draw=0) for DECIDERS
    # ---------------------------------------------------------------------
    # Goal C: Use baseline columns (lhw_base, yivwg_base) to ensure consistency
    # with draw=0 values assigned in df_draw0
    dec_hours0 = (
        pd.to_numeric(decider_df["lhw_base"], errors="coerce").fillna(0.0).to_numpy()
    )
    dec_wage0 = (
        pd.to_numeric(decider_df["yivwg_base"], errors="coerce").fillna(0.0).to_numpy()
    )
    dec_work0 = dec_hours0 > 0.0

    # Support checks: q(z_obs) must be positive for any observed working state
    bad_h = dec_work0 & ((dec_hours0 < h_min) | (dec_hours0 > h_max))
    if bad_h.any():
        # Enhanced diagnostics: show distribution of baseline hours among working deciders
        working_hours = dec_hours0[dec_work0]
        if len(working_hours) > 0:
            pcts = np.percentile(working_hours, [1, 5, 50, 95, 99])
            diag_str = (
                f"\n  Baseline hours distribution (working deciders only):\n"
                f"    min={working_hours.min():.2f}, p01={pcts[0]:.2f}, p05={pcts[1]:.2f}, "
                f"median={pcts[2]:.2f}, p95={pcts[3]:.2f}, p99={pcts[4]:.2f}, max={working_hours.max():.2f}\n"
                f"  Current bounds: h_min={h_min}, h_max={h_max}\n"
            )
        else:
            diag_str = "\n  (No working deciders to analyze)\n"

        cols = [c for c in ["idperson", "idhh", "lhw_base", "lhw", "hours", "les"] if c in decider_df.columns]
        offenders = decider_df.loc[bad_h, cols].head(20)

        raise ValueError(
            f"Observed (draw=0) hours fall outside [h_min, h_max] for {int(bad_h.sum())} deciders.\n"
            f"{diag_str}"
            f"Example offenders (first 20):\n{offenders.to_string(index=False)}\n\n"
            "Increase --h-min/--h-max or fix units / harmonize hours in data_prep."
        )

    if wage_spec == "vw":
        bad_w = dec_work0 & ((dec_wage0 < w_min) | (dec_wage0 > w_max))
        if bad_w.any():
            # Enhanced diagnostics: show distribution of baseline wages among working deciders
            working_wages = dec_wage0[dec_work0]
            if len(working_wages) > 0:
                pcts = np.percentile(working_wages, [1, 5, 50, 95, 99])
                diag_str = (
                    f"\n  Baseline wage distribution (working deciders only):\n"
                    f"    min={working_wages.min():.2f}, p01={pcts[0]:.2f}, p05={pcts[1]:.2f}, "
                    f"median={pcts[2]:.2f}, p95={pcts[3]:.2f}, p99={pcts[4]:.2f}, max={working_wages.max():.2f}\n"
                    f"  Current bounds: w_min={w_min}, w_max={w_max}\n"
                )
            else:
                diag_str = "\n  (No working deciders to analyze)\n"

            cols = [c for c in ["idperson", "idhh", "yivwg_base", "yivwg", "wage", "wage_final", "les"] if c in decider_df.columns]
            offenders = decider_df.loc[bad_w, cols].head(20)

            raise ValueError(
                f"Observed (draw=0) wages fall outside [w_min, w_max] for {int(bad_w.sum())} deciders.\n"
                f"{diag_str}"
                f"Example offenders (first 20):\n{offenders.to_string(index=False)}\n\n"
                "Increase --w-min/--w-max or ensure wage units match / harmonize wages in data_prep."
            )

    eps = 1e-15
    pi0_dec = pi0_vec[is_decider.to_numpy()]
    log_q_state0 = np.where(
        dec_work0,
        np.log(np.clip(1.0 - pi0_dec, eps, 1.0)),
        np.log(np.clip(pi0_dec, eps, 1.0)),
    )
    log_q_hours0 = np.where(dec_work0, -np.log(h_max - h_min), 0.0)

    if wage_spec == "vw":
        log_q_wage0 = np.where(dec_work0, -np.log(w_max - w_min), 0.0)
    else:
        log_q_wage0 = np.zeros_like(log_q_state0)

    df_draw0.loc[is_decider, "log_q_state"] = log_q_state0
    df_draw0.loc[is_decider, "log_q_hours"] = log_q_hours0
    df_draw0.loc[is_decider, "log_q_wage"] = log_q_wage0

    # Total number of simulated records: n_deciders * n_draws
    n_sim = n_deciders_actual * n_draws

    # Replicate each decider n_draws times
    # Index into decider_df: [0,0,...,0, 1,1,...,1, ..., n-1,n-1,...,n-1]
    # Each person repeated n_draws times consecutively
    person_idx = np.repeat(np.arange(n_deciders_actual), n_draws)

    # Draw numbers: [1,2,...,n_draws, 1,2,...,n_draws, ...]
    draw_nums = np.tile(np.arange(1, n_draws + 1), n_deciders_actual)

    if occ_col not in decider_df.columns:
        raise KeyError(f"Occupation column '{occ_col}' not found in decider_df.")
    # observed occupation for deciders (fallback / baseline)

    occ_obs_dec = (
        pd.to_numeric(decider_df[occ_col], errors="coerce")
        .fillna(-2)
        .astype(int)
        .to_numpy()
    )
    # --- SAFETY: ensure baseline occupation is valid for simulated working draws ---
    # Valid task groups assumed: 1..4 (loc4). If missing/invalid, impute pooled mode
    # from observed working deciders; fallback to 1 if no valid pool exists.
    valid_occ = (occ_obs_dec >= 1) & (occ_obs_dec <= 4)
    if not valid_occ.all():
        pool = occ_obs_dec[dec_work0 & valid_occ]
        if pool.size > 0:
            counts = np.bincount(pool.astype(int), minlength=5)  # indices 0..4
            mode_occ = int(np.argmax(counts[1:5]) + 1)           # restrict to 1..4
        else:
            mode_occ = 1
        occ_obs_dec[~valid_occ] = mode_occ

    occ_obs_sim = occ_obs_dec[person_idx]  # now person_idx exists

    # Get pi0 for each simulated record (replicated from decider pi0_vec)
    decider_pi0 = pi0_vec[is_decider.to_numpy()]
    pi0_sim = decider_pi0[person_idx]

    # Get observed wage for each simulated record (for fixed wage spec)
    decider_wages = wage[is_decider].to_numpy()
    obs_wage_sim = decider_wages[person_idx]

    # -------------------------------------------------------------------------
    # Vectorized random draws
    # -------------------------------------------------------------------------
    # Uniform draws to determine employment vs non-employment
    u_emp = rng.random(n_sim)
    is_nonemployment = u_emp < pi0_sim
    is_working = ~is_nonemployment
    # -------------------------------------------------------------------------
    # Occupation draws (Case B)
    # -------------------------------------------------------------------------
    # Default: keep observed occupation for working draws; enforce -1 for non-employment
    occ_sim = occ_obs_sim.astype(np.int16, copy=True)
    log_q_occ = np.zeros(n_sim, dtype=float)

    if occ_spec == "empirical":
        # empirical probs based on observed WORKING deciders (draw=0 info)
        dec_hours_obs = pd.to_numeric(
            decider_df.get("hours", decider_df.get("lhw", 0.0)), errors="coerce"
        ).fillna(0.0)
        dec_working_obs = dec_hours_obs > 0

        # keep only strata columns that exist
        strata_cols = tuple([c for c in occ_strata if c in decider_df.columns])
        if len(strata_cols) == 0:
            # collapse to one stratum
            decider_df["__all__"] = 1
            strata_cols = ("__all__",)

        probs_map = _build_occ_probs_by_stratum(
            decider_df,
            occ_col=occ_col,
            strata_cols=strata_cols,
            working_mask=dec_working_obs,
            valid_occ=(1, 2, 3, 4),
            min_cell=occ_min_cell,
        )

        # replicated stratum keys for simulated records
        dec_stratum = (
            decider_df[list(strata_cols)]
            .astype(object)
            .apply(tuple, axis=1)
            .to_numpy(dtype=object)
        )
        # log q_occ for the observed alternative (draw=0), for working deciders only
        logq_obs = _log_q_occ_for_given_occ(
            occ=occ_obs_dec,
            stratum_keys=dec_stratum,
            probs_map=probs_map,
        )
        log_q_occ0 = np.zeros(n_deciders_actual, dtype=float)
        work0 = dec_working_obs.to_numpy()
        log_q_occ0[work0] = logq_obs[work0]
        df_draw0.loc[is_decider, "log_q_occ"] = log_q_occ0

        stratum_sim = dec_stratum[person_idx]

        # draw occ only for working simulated records
        occ_work, logq_work = _sample_occ_vectorized_by_stratum(
            stratum_keys=stratum_sim[is_working],
            probs_map=probs_map,
            rng=rng,
            fallback_occ=occ_obs_sim[is_working],
        )
        occ_sim[is_working] = occ_work
        log_q_occ[is_working] = logq_work

    # enforce non-employment convention
    occ_sim[is_nonemployment] = -1
    log_q_occ[is_nonemployment] = 0.0
    # Finalize proposal density for draw=0 (observed) deciders
    df_draw0.loc[is_decider, "log_q_total"] = (
        df_draw0.loc[
            is_decider, ["log_q_state", "log_q_hours", "log_q_wage", "log_q_occ"]
        ]
        .sum(axis=1)
        .to_numpy()
    )

    # Hours: 0 for non-employment, Uniform[h_min, h_max] for working
    hours_sim = np.zeros(n_sim, dtype=float)
    n_working = is_working.sum()
    if n_working > 0:
        hours_sim[is_working] = rng.uniform(h_min, h_max, size=n_working)

    # Wages: 0 for non-employment
    # For working: Uniform[w_min, w_max] if vw, else observed wage
    wage_sim = np.zeros(n_sim, dtype=float)
    if n_working > 0:
        if wage_spec == "vw":
            wage_sim[is_working] = rng.uniform(w_min, w_max, size=n_working)
        else:
            # Fixed wage: use observed wage
            wage_sim[is_working] = obs_wage_sim[is_working]

    # Loc: -1 for non-employment, baseline loc for working

    # yem: wage * hours * weeks_per_month
    yem_sim = wage_sim * hours_sim * WEEKS_PER_MONTH

    # -------------------------------------------------------------------------
    # Proposal density components (importance-sampling correction)
    # -------------------------------------------------------------------------
    eps = 1e-15

    log_q_state = np.zeros(n_sim, dtype=float)
    log_q_state[is_nonemployment] = np.log(np.clip(pi0_sim[is_nonemployment], eps, 1.0))
    log_q_state[is_working] = np.log(np.clip(1.0 - pi0_sim[is_working], eps, 1.0))

    log_q_hours = np.zeros(n_sim, dtype=float)
    if h_max <= h_min:
        raise ValueError("h_max must be > h_min for Uniform hours.")
    log_q_hours[is_working] = -np.log(h_max - h_min)

    log_q_wage = np.zeros(n_sim, dtype=float)
    if wage_spec == "vw":
        if w_max <= w_min:
            raise ValueError("w_max must be > w_min for Uniform wages.")
        log_q_wage[is_working] = -np.log(w_max - w_min)
    elif wage_spec == "fw":
        # degenerate at observed wage: treat as "not sampled" for proposal accounting
        log_q_wage[:] = 0.0
    else:
        raise ValueError("Unsupported wage_spec.")

    log_q_total = log_q_state + log_q_hours + log_q_wage + log_q_occ

    # -------------------------------------------------------------------------
    # Build simulated DataFrame efficiently
    # -------------------------------------------------------------------------
    # Replicate decider rows n_draws times using iloc indexing
    sim_df = decider_df.iloc[person_idx].copy().reset_index(drop=True)

    # Overwrite with simulated values
    sim_df["is_decider"] = 1
    sim_df["draw"] = draw_nums
    sim_df["is_chosen"] = 0
    sim_df["hours"] = hours_sim
    if "lhw" in sim_df.columns:
        sim_df["lhw"] = hours_sim
    sim_df["wage"] = wage_sim
    if "wage_ruro" in sim_df.columns:
        sim_df["wage_ruro"] = wage_sim
    if "yivwg" in sim_df.columns:
        sim_df["yivwg"] = wage_sim
    if "yem" in sim_df.columns:
        sim_df["yem"] = yem_sim

    # occupation used in estimation
    sim_df[occ_col] = occ_sim

    # proposal components
    sim_df["log_q_state"] = log_q_state
    sim_df["log_q_hours"] = log_q_hours
    sim_df["log_q_wage"] = log_q_wage
    sim_df["log_q_occ"] = log_q_occ
    sim_df["log_q_total"] = log_q_total

    # -------------------------------------------------------------------------
    # Concatenate: draw=0 (all persons) + draws 1..n (deciders only)
    # -------------------------------------------------------------------------
    long_df = pd.concat([df_draw0, sim_df], ignore_index=True)

    # =========================================================================
    # Goal 3: Ensure draw is int type
    # =========================================================================
    long_df["draw"] = long_df["draw"].astype(int)

    # Sort by idperson and draw for consistency
    sort_cols = ["idperson_true", "draw"]
    if "idhh_true" in long_df.columns:
        sort_cols = ["idhh_true"] + sort_cols
    long_df = long_df.sort_values(sort_cols).reset_index(drop=True)

    # =========================================================================
    # Goal 5: Logging - decider vs non-decider counts
    # =========================================================================
    n_deciders_out = (long_df["is_decider"] == 1).sum()
    n_nondeciders_out = (long_df["is_decider"] == 0).sum()
    logging.info(
        f"RURO_draws output: {n_deciders_out} decider rows, {n_nondeciders_out} non-decider rows"
    )

    # Check that non-deciders appear only at draw=0
    if n_nondeciders_out > 0:
        nondecider_draws = long_df[long_df["is_decider"] == 0]["draw"].unique()
        if not (len(nondecider_draws) == 1 and nondecider_draws[0] == 0):
            logging.warning(
                f"Non-deciders found at draws other than 0: {sorted(nondecider_draws)}"
            )
        else:
            logging.info("Non-deciders appear only at draw=0 (as expected)")

    logging.info(
        f"RURO_draws: Generated {len(long_df)} total records ({len(df_draw0)} observed + {len(sim_df)} simulated)."
    )

    # =========================================================================
    # Additional check #1: Per-person draw grid completeness for DECIDERS
    # =========================================================================
    # Validate that each decider has exactly draws {0, 1, ..., n_draws}
    if n_draws > 0:
        decider_mask_output = long_df["is_decider"] == 1
        deciders_output = long_df[decider_mask_output].copy()

        if len(deciders_output) > 0:
            expected_draw_set = set(range(n_draws + 1))  # {0, 1, 2, ..., n_draws}
            draw_counts = deciders_output.groupby("idperson_true")["draw"].apply(set)

            violations = []
            for idperson, draw_set in draw_counts.items():
                if draw_set != expected_draw_set:
                    violations.append({
                        "idperson_true": idperson,
                        "expected": sorted(expected_draw_set),
                        "actual": sorted(draw_set),
                        "missing": sorted(expected_draw_set - draw_set),
                        "extra": sorted(draw_set - expected_draw_set),
                    })

            if violations:
                logging.error(
                    f"Draw grid completeness validation failed: {len(violations)} deciders "
                    f"have incomplete or incorrect draw sets"
                )
                # Show first few violations
                for v in violations[:5]:
                    logging.error(
                        f"  idperson_true={v['idperson_true']}: "
                        f"missing={v['missing']}, extra={v['extra']}"
                    )

                raise ValueError(
                    f"Draw grid completeness check failed: {len(violations)} deciders "
                    f"do not have the expected draw set {{0, 1, ..., {n_draws}}}. "
                    f"This indicates a bug in draw generation. See logs for details."
                )

            logging.info(
                f"Draw grid completeness: 100% ({len(draw_counts)}/{len(draw_counts)} "
                f"deciders have complete draw sets {{0..{n_draws}}})"
            )

    return long_df


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Generate RURO long datasets with simulated draws from RURO_ready inputs."
    )
    ap.add_argument(
        "--singles-path",
        type=str,
        required=True,
        help="Path to singles_RURO_ready.parquet (or .csv, .pkl, ...).",
    )
    ap.add_argument(
        "--couples-path",
        type=str,
        required=False,
        help="Path to couples_RURO_ready.parquet (if available).",
    )
    ap.add_argument(
        "--n-draws",
        type=int,
        default=DEFAULT_N_DRAWS,
        help="Number of simulated opportunities per person (excluding the observed job).",
    )
    ap.add_argument(
        "--wage-spec",
        type=str,
        choices=["fw", "vw"],
        default=DEFAULT_WAGE_SPEC,
        help="Wage opportunity specification: 'fw' fixed, 'vw' variable.",
    )
    ap.add_argument(
        "--occ-spec",
        type=str,
        choices=["fixed", "empirical"],
        default=DEFAULT_OCC_SPEC,
        help="Occupation opportunity spec: fixed (keep observed) or empirical (draw from observed frequencies).",
    )
    ap.add_argument(
        "--occ-strata",
        nargs="+",
        default=list(DEFAULT_OCC_STRATA),
        help="Strata columns for empirical occ probs (e.g., dgn educ3).",
    )
    ap.add_argument(
        "--occ-min-cell",
        type=int,
        default=DEFAULT_OCC_MIN_CELL,
        help="Minimum obs per stratum to use stratum-specific occ probs; otherwise pooled fallback.",
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
    ap.add_argument(
        "--rng-seed",
        type=int,
        default=DEFAULT_RNG_SEED,
        help="Seed for the RNG (reproducible draws).",
    )

    return ap.parse_args()


def main() -> None:
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    args = parse_args()

    singles_path = Path(args.singles_path).resolve()
    if not singles_path.exists():
        raise FileNotFoundError(f"Singles RURO_ready file not found: {singles_path}")
    singles_df = _read_dataframe(singles_path)
    singles_df = _attach_other_members_income(singles_df)
    singles_long = generate_draws_long(
        singles_df,
        n_draws=args.n_draws,
        wage_spec=args.wage_spec,
        occ_spec=args.occ_spec,
        occ_strata=tuple(args.occ_strata),
        occ_min_cell=args.occ_min_cell,
        pi0_m=args.pi0_m,
        pi0_f=args.pi0_f,
        h_min=args.h_min,
        h_max=args.h_max,
        w_min=args.w_min,
        w_max=args.w_max,
        rng_seed=args.rng_seed,
    )

    # =========================================================================
    # Validations (Goals 2, 6, 8)
    # =========================================================================
    # Note: singles don't need couples consistency check
    _validate_draw0_baseline_compliance(
        singles_long,
        baseline_cols={"lhw": "lhw_base", "yivwg": "yivwg_base"},
        tolerance=1e-6,
    )

    singles_out = _write_dataframe(singles_long, singles_path, suffix="_RURO_draws")

    # =========================================================================
    # Goal 4: Write metadata sidecar for singles
    # =========================================================================
    max_draw_singles = int(singles_long["draw"].max())
    id_multiplier_singles = _compute_id_multiplier(max_draw_singles)

    singles_metadata = {
        "n_draws": args.n_draws,
        "max_draw": max_draw_singles,
        "seed": args.rng_seed,
        "id_multiplier": id_multiplier_singles,
        "household_type": "singles",
        "distributional_params": {
            "pi0_m": args.pi0_m,
            "pi0_f": args.pi0_f,
            "h_min": args.h_min,
            "h_max": args.h_max,
            "w_min": args.w_min,
            "w_max": args.w_max,
            "wage_spec": args.wage_spec,
            "occ_spec": args.occ_spec,
            "occ_strata": list(args.occ_strata),
            "occ_min_cell": args.occ_min_cell,
        },
        "input_file": str(singles_path),
        "output_schema": list(singles_long.columns),
    }
    _write_draws_metadata(singles_out["parquet"], singles_metadata)

    print("Singles draws saved to:")
    for k, v in singles_out.items():
        print(f"  {k}: {v}")
    print(f"  metadata: {singles_out['parquet'].parent / (singles_out['parquet'].stem + '__drawsmeta.json')}")

    # =========================================================================
    # Runtime sanity checks for singles draws
    # =========================================================================
    logging.info("Running runtime sanity checks on singles draws...")
    try:
        sanity_report_draws(singles_long, metadata=singles_metadata, n_draws=args.n_draws)
        logging.info("✓ Singles draws passed all sanity checks")
    except Exception as e:
        logging.error(f"Singles draws FAILED sanity checks: {e}")
        raise

    combined_draws = [singles_long]

    if args.couples_path:
        couples_path = Path(args.couples_path).resolve()
        if not couples_path.exists():
            raise FileNotFoundError(
                f"Couples RURO_ready file not found: {couples_path}"
            )
        couples_df = _read_dataframe(couples_path)
        couples_df = _attach_other_members_income(couples_df)
        couples_long = generate_draws_long(
            couples_df,
            n_draws=args.n_draws,
            wage_spec=args.wage_spec,
            occ_spec=args.occ_spec,
            occ_strata=tuple(args.occ_strata),
            occ_min_cell=args.occ_min_cell,
            pi0_m=args.pi0_m,
            pi0_f=args.pi0_f,
            h_min=args.h_min,
            h_max=args.h_max,
            w_min=args.w_min,
            w_max=args.w_max,
            rng_seed=args.rng_seed + 1,  # different seed for couples
        )

        # =====================================================================
        # Validations for couples (Goals 2, 6, 8)
        # =====================================================================
        _validate_couples_draw_consistency(couples_long, household_type="couples")
        _validate_draw0_baseline_compliance(
            couples_long,
            baseline_cols={"lhw": "lhw_base", "yivwg": "yivwg_base"},
            tolerance=1e-6,
        )

        couples_out = _write_dataframe(couples_long, couples_path, suffix="_RURO_draws")

        # =====================================================================
        # Goal 4: Write metadata sidecar for couples
        # =====================================================================
        max_draw_couples = int(couples_long["draw"].max())
        id_multiplier_couples = _compute_id_multiplier(max_draw_couples)

        couples_metadata = {
            "n_draws": args.n_draws,
            "max_draw": max_draw_couples,
            "seed": args.rng_seed + 1,
            "id_multiplier": id_multiplier_couples,
            "household_type": "couples",
            "distributional_params": {
                "pi0_m": args.pi0_m,
                "pi0_f": args.pi0_f,
                "h_min": args.h_min,
                "h_max": args.h_max,
                "w_min": args.w_min,
                "w_max": args.w_max,
                "wage_spec": args.wage_spec,
                "occ_spec": args.occ_spec,
                "occ_strata": list(args.occ_strata),
                "occ_min_cell": args.occ_min_cell,
            },
            "input_file": str(couples_path),
            "output_schema": list(couples_long.columns),
        }
        _write_draws_metadata(couples_out["parquet"], couples_metadata)

        print("Couples draws saved to:")
        for k, v in couples_out.items():
            print(f"  {k}: {v}")
        print(f"  metadata: {couples_out['parquet'].parent / (couples_out['parquet'].stem + '__drawsmeta.json')}")

        # =====================================================================
        # Runtime sanity checks for couples draws
        # =====================================================================
        logging.info("Running runtime sanity checks on couples draws...")
        try:
            sanity_report_draws(couples_long, metadata=couples_metadata, n_draws=args.n_draws)
            logging.info("✓ Couples draws passed all sanity checks")
        except Exception as e:
            logging.error(f"Couples draws FAILED sanity checks: {e}")
            raise

        combined_draws.append(couples_long)


if __name__ == "__main__":
    main()
