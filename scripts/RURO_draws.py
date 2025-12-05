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

This script follows the structure of Stijn Van Houtven's Belgian RURO implementation.

Key Design Decisions
--------------------
1. **Deciders only**: The choice set is defined only for household decision makers
   (head and partner, flagged by `hh_IsHead` and `hh_IsPartner`). Children and other
   household members are *not* given simulated opportunities; they appear only with
   draw=0 and their observed hours/wage, so that EUROMOD can correctly compute
   household-level tax-benefit outcomes.

2. **RURO opportunity density** (hours and wages only, following Stijn's implementation):
   For each decider i:
   - With probability π₀,g(i) (gender-specific: pi0_m for men, pi0_f for women),
     the opportunity is **non-employment**: hours=0, wage=0, loc=-1.
   - With probability 1 - π₀,g(i), the opportunity is a **working job**:
       * hours ~ Uniform[h_min, h_max]
       * wage  ~ Uniform[w_min, w_max] if wage_spec="vw" (variable wage), else
                 fixed to observed wage if wage_spec="fw" (fixed wage)
   
   **Note**: Occupation (`loc`) does NOT enter the opportunity density. For working
   draws, `loc` is set to the baseline (observed) occupation; for non-employment
   draws, `loc` is set to -1. This matches Stijn's `f_choicesets_est()` where the
   prior is only over hours and wages.

3. **Observed job**: draw=0 preserves the observed hours, wage, and occupation
   exactly as in the RURO_ready input. No perturbation.

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
import os
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

# Ensure pythonnet uses CoreCLR (align with data_prep2.py)
os.environ.setdefault("PYTHONNET_RUNTIME", "coreclr")

# ---------------------------------------------------------------------------
# Minimal path/helpers for EUROMOD integration (self contained)
# ---------------------------------------------------------------------------


def _collect_candidates() -> tuple[Path, ...]:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    seen: set[Path] = set()
    candidates: list[Path] = []

    def add(path: Path | str | None) -> None:
        if not path:
            return
        candidate = Path(path).expanduser()
        resolved = candidate
        try:
            resolved = candidate.resolve(strict=False)
        except OSError:
            pass
        if resolved in seen:
            return
        seen.add(resolved)
        candidates.append(resolved)

    add(repo_root)
    add(repo_root.parent)
    add(script_dir)
    add(script_dir.parent)

    for env in ENV_HINTS:
        raw = os.environ.get(env)
        if raw:
            env_path = Path(raw).expanduser()
            add(env_path)
            add(env_path.parent)

    add("U:/EUROMOD-STORAGE")
    add(Path.home() / "EUROMOD-STORAGE")

    return tuple(candidates)


def _resolve_storage_root() -> Path:
    env_candidates: list[Path] = []
    for env in ENV_HINTS:
        raw = os.environ.get(env)
        if raw:
            env_path = Path(raw).expanduser()
            env_candidates.append(env_path)
            env_candidates.append(env_path.parent)

    explicit_candidates = [Path(r"U:/EUROMOD-STORAGE"), Path.home() / "EUROMOD-STORAGE"]
    repo_candidates = [c for c in _collect_candidates() if c not in env_candidates + explicit_candidates]

    preferred: list[Path] = []
    for candidate in env_candidates + explicit_candidates + repo_candidates:
        data_dir = candidate / "Data"
        if data_dir.exists():
            if (data_dir / "processed").exists() or (data_dir / "raw").exists():
                return candidate
            preferred.append(candidate)
        if candidate.name.lower() == "data" and candidate.exists():
            if (candidate / "processed").exists() or (candidate / "raw").exists():
                return candidate.parent
            preferred.append(candidate.parent)
    if preferred:
        return preferred[0]
    raise FileNotFoundError("Unable to locate storage root containing 'Data'. Set MNL_DATA_ROOT or MNL_STORAGE_ROOT.")


def _euromod_root(explicit: Path | None = None) -> Path:
    if explicit:
        return explicit
    env = os.environ.get("MNL_EUROMOD_ROOT")
    if env:
        candidate = Path(env).expanduser()
        if candidate.exists():
            return candidate
    storage = _resolve_storage_root()
    for rel in (
        Path("EUROMOD_RELEASES_J1.0+") / "EUROMOD_RELEASES_J1.0+",
        Path("EUROMOD_RELEASES_J1.0+"),
        Path("EUROMOD_RELEASES"),
        Path("euromod_releases"),
    ):
        cand = storage / rel
        if cand.exists():
            return cand
    for child in storage.iterdir():
        if child.is_dir() and "euromod" in child.name.lower():
            return child
    raise FileNotFoundError("EUROMOD release directory not found; set MNL_EUROMOD_ROOT.")


def _read_microdata_file(path: Path) -> pd.DataFrame:
    suf = path.suffix.lower()
    if suf in {".txt", ".dat"}:
        return pd.read_csv(path, sep="\t")
    if suf == ".csv":
        return pd.read_csv(path)
    if suf == ".parquet":
        return pd.read_parquet(path)  # type: ignore[arg-type]
    if suf == ".pkl":
        return pd.read_pickle(path)
    raise ValueError(f"Unsupported microdata format for EUROMOD: {path}")


class EuromodRunner:
    """Thin wrapper around the euromod API (imports locally)."""

    def __init__(self, root: Path):
        try:
            import euromod as em  # type: ignore
        except Exception as exc:
            raise ImportError("euromod package is required for EUROMOD runs.") from exc
        self.em = em
        self.model = em.Model(str(root))

    def _resolve_system(self, country: str, system_code: str, dataset_name: str):
        country_obj = self.model[country.upper()]
        try:
            system = country_obj[system_code]
        except KeyError:
            systems_iter = getattr(country_obj, "systems", country_obj.values())
            system = next(iter(systems_iter))
        dataset = None
        if hasattr(system, "datasets"):
            ds = system.datasets
            if hasattr(ds, "get"):
                dataset = ds.get(dataset_name)
            elif hasattr(ds, "__getitem__"):
                try:
                    dataset = ds[dataset_name]
                except Exception:
                    dataset = None
            if dataset is None:
                # try to match by name attribute
                try:
                    dataset = next((d for d in ds if getattr(d, "name", "") == dataset_name))
                except Exception:
                    dataset = None
            if dataset is None:
                try:
                    dataset = next(iter(ds))
                except Exception:
                    dataset = None
        if dataset is None and getattr(system, "bestmatch_datasets", None):
            dataset = system.bestmatch_datasets[0]
        if dataset is None and hasattr(system, "values"):
            try:
                dataset = next(iter(system.values()))
            except Exception:
                dataset = None
        if dataset is None:
            raise KeyError(f"Dataset {dataset_name} not found in EUROMOD system {system_code}")
        return system, dataset

    def run_on_dataframe(self, df: pd.DataFrame, *, country: str, system_code: str, dataset_name: str) -> pd.DataFrame:
        system, dataset = self._resolve_system(country, system_code, dataset_name)
        sim = system.run(df, dataset.name)
        return sim.outputs[0]
# ---------------------------------------------------------------------------
# Defaults (keep in sync with RURO_prep_mnl.py)
# ---------------------------------------------------------------------------

TOTAL_LEISURE_HOURS = 80.0
WEEKS_PER_MONTH = 52.0 / 12.0

DCM_MIN_POSITIVE = 1e-6

DEFAULT_PI0_M = 0.10
DEFAULT_PI0_F = 0.10

DEFAULT_H_MIN = 1.0
DEFAULT_H_MAX = 70.0
DEFAULT_W_MIN = 1.0
DEFAULT_W_MAX = 120.0

DEFAULT_WAGE_SPEC = "vw"       # "fw" or "vw"
DEFAULT_N_DRAWS = 99
DEFAULT_RNG_SEED = 17  # Lucky number for reproducibility

# EUROMOD defaults/hooks
ENV_HINTS = ("MNL_STORAGE_ROOT", "MNL_DATA_ROOT", "MNL_ROOT")
DEFAULT_EUROMOD_HOURS_COL = "lhw"
DEFAULT_EUROMOD_WAGE_COL = "yivwg"


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


def _write_dataframe(df: pd.DataFrame, base_path: Path, suffix: str = "_draws") -> Dict[str, Path]:
    out_dir = base_path.parent
    base = base_path.stem + suffix
    parquet_path = out_dir / f"{base}.parquet"
    csv_path = out_dir / f"{base}.csv"

    df.to_parquet(parquet_path, index=False, engine="pyarrow")  # type: ignore[arg-type]
    # CSV export temporarily disabled because it is unused and costly.
    # df.to_csv(csv_path, index=False)
    return {"parquet": parquet_path}


def _prepare_euromod_dataset(
    template_df: pd.DataFrame,
    draw_df: pd.DataFrame,
    *,
    id_col: str,
    hours_col: str,
    wage_col: str,
) -> pd.DataFrame:
    """Merge draw-specific hours/wage into a copy of template microdata."""
    out = template_df.copy()
    # Map hours/wage by id
    hours_map = pd.to_numeric(draw_df[hours_col], errors="coerce")
    wage_map = pd.to_numeric(draw_df[wage_col], errors="coerce")
    hours_lookup = dict(zip(draw_df[id_col], hours_map))
    wage_lookup = dict(zip(draw_df[id_col], wage_map))
    if hours_lookup:
        out[hours_col] = out[id_col].map(hours_lookup).fillna(out[hours_col])
    if wage_lookup:
        out[wage_col] = out[id_col].map(wage_lookup).fillna(out[wage_col])
    return out


def run_euromod_for_draws(
    draws_df: pd.DataFrame,
    micro_template_path: Path,
    *,
    country: str,
    system_code: str,
    dataset_name: str,
    em_root: Path,
    scenario_dir: Path,
    id_col: str = "idperson",
    hours_col: str = DEFAULT_EUROMOD_HOURS_COL,
    wage_col: str = DEFAULT_EUROMOD_WAGE_COL,
) -> Path:
    """
    EUROMOD call:

      * Build ONE big EM input containing ALL draws (singles + couples).
      * Apply hours/wage/benefit adjustments before EUROMOD:
          - hours / lhw from RURO draws
          - wage / yivwg from RURO draws
          - yem consistency for lma == 1
          - bun, bsa = 0 when working (lma == 1 and hours > 0)
          - yemmy = 12, lunmy = 0 when working (if present)
      * Create draw-specific IDs (idhh, idperson, kin IDs) to avoid clashes.
      * Run EUROMOD ONCE and save a single combined file.
    """
    scenario_dir = scenario_dir.resolve()
    scenario_dir.mkdir(parents=True, exist_ok=True)

    # 1. EUROMOD baseline microdata 
    template_df = _read_microdata_file(micro_template_path)

    # 2. Check that we have draw information
    if "draw" not in draws_df.columns:
        raise KeyError("`draws_df` must contain a 'draw' column.")
    if id_col not in draws_df.columns:
        raise KeyError(f"`draws_df` must contain '{id_col}'.")

    # 3. Keep only what we need from the long RURO draws:
    #    (id, draw, hours, wage). hours/wage come from generate_draws_long.
    override_cols = [id_col, "draw"]
    if "hours" in draws_df.columns:
        override_cols.append("hours")
    if "wage" in draws_df.columns:
        override_cols.append("wage")

    draws_sub = draws_df[override_cols].copy()

    # 4. Merge: one EM row per (idperson, draw)
    #    template_df has one row per person; draws_sub has one row per (person, draw).
    #    Inner join replicates the household/person structure across all draws.
    em_input = template_df.merge(draws_sub, on=id_col, how="inner", suffixes=("", "_draw"))

    if em_input.empty:
        raise ValueError("EUROMOD input after merging with draws is empty. "
                         "Check that micro_template and RURO draws share the same idperson.")

    # 5. Store "true" ids for later grouping in RURO_prep_mnl
    if "idhh" in em_input.columns:
        em_input["idhh_true"] = em_input["idhh"]
    em_input[f"{id_col}_true"] = em_input[id_col]

    # 6. Labour-market & hours/wage variables
    draw = pd.to_numeric(em_input["draw"], errors="coerce").fillna(0).astype(int)

    # labour-market activity flag (lma), fallback 1 if missing
    if "lma" in em_input.columns:
        lma_raw = em_input["lma"]
    else:
        lma_raw = pd.Series(1, index=em_input.index)
    lma = pd.to_numeric(lma_raw, errors="coerce").fillna(1).astype(int)

    # hours and wage from the RURO draws
    if "hours" in em_input.columns:
        h_raw = em_input["hours"]
    elif hours_col in em_input.columns:
        h_raw = em_input[hours_col]
    else:
        h_raw = pd.Series(0.0, index=em_input.index)
    h = pd.to_numeric(h_raw, errors="coerce").fillna(0.0)

    if "wage" in em_input.columns:
        w_raw = em_input["wage"]
    elif wage_col in em_input.columns:
        w_raw = em_input[wage_col]
    else:
        w_raw = pd.Series(0.0, index=em_input.index)
    w = pd.to_numeric(w_raw, errors="coerce").fillna(0.0)

    # -- HOURS / LHW --
    # overwrite EUROMOD hours column and keep an alias 'hours'
    em_input[hours_col] = h
    em_input["hours"] = h

    # -- WAGES / YIVWG --
    # For active (lma == 1) when hours > 0 we plug in the simulated wage; otherwise keep EM wage.
    if wage_col in em_input.columns:
        base_w = pd.to_numeric(em_input[wage_col], errors="coerce").fillna(0.0)
    else:
        base_w = w.copy()

    working_mask = (lma == 1) & (h > 0.0)
    em_input[wage_col] = np.where(working_mask, w, base_w)
    em_input["wage"] = em_input[wage_col]

    # -- YEM --
    # For labour-market active persons, ensure yem = hours * wage * weeks_per_month.
    if "yem" in em_input.columns:
        yem = pd.to_numeric(em_input["yem"], errors="coerce").fillna(0.0)
        yem.loc[working_mask] = h[working_mask] * em_input.loc[working_mask, wage_col] * WEEKS_PER_MONTH
        em_input["yem"] = yem

    # -- BENEFITS: BUN / BSA --
    if "bun" in em_input.columns:
        bun = pd.to_numeric(em_input["bun"], errors="coerce").fillna(0.0)
        bun.loc[working_mask] = 0.0
        em_input["bun"] = bun

    if "bsa" in em_input.columns:
        bsa = pd.to_numeric(em_input["bsa"], errors="coerce").fillna(0.0)
        bsa.loc[working_mask] = 0.0
        em_input["bsa"] = bsa

    # -- MONTHS IN WORK / UNEMPLOYMENT: YEMMY / LUNMY --
    if "yemmy" in em_input.columns and "lunmy" in em_input.columns:
        yemmy = pd.to_numeric(em_input["yemmy"], errors="coerce")
        lunmy = pd.to_numeric(em_input["lunmy"], errors="coerce")
        yemmy.loc[working_mask] = 12
        lunmy.loc[working_mask] = 0
        em_input["yemmy"] = yemmy
        em_input["lunmy"] = lunmy

    # 7. Draw-specific IDs (households, persons, kin)
    if "idhh" in em_input.columns:
        em_input["idhh"] = em_input["idhh_true"] * 1000 + draw

    base_id = em_input[f"{id_col}_true"]
    em_input[id_col] = base_id * 1000 + draw

    for kin in ["idfather", "idmother", "idpartner"]:
        if kin in em_input.columns:
            kin_old = pd.to_numeric(em_input[kin], errors="coerce").fillna(0).astype(int)
            kin_new = np.where(kin_old == 0, 0, kin_old * 1000 + draw)
            em_input[kin] = kin_new

    # 8. Run EUROMOD ONCE on the full dataset
    runner = EuromodRunner(em_root)
    # Ensure household/person ordering for EUROMOD stability
    sort_cols = []
    if "idhh" in em_input.columns:
        sort_cols.append("idhh")
    if id_col in em_input.columns:
        sort_cols.append(id_col)
    if sort_cols:
        em_input = em_input.sort_values(sort_cols).reset_index(drop=True)
    sim_df = runner.run_on_dataframe(
        em_input,
        country=country,
        system_code=system_code,
        dataset_name=dataset_name,
    )

    # Reattach draw and "true" ids
    sim_df["draw"] = em_input["draw"].values
    if "idhh_true" in em_input.columns:
        sim_df["idhh_true"] = em_input["idhh_true"].values
    sim_df[f"{id_col}_true"] = em_input[f"{id_col}_true"].values

    # 9. Save a single combined file for all draws
    combined_path = scenario_dir / "combined_draws_em.parquet"
    sim_df.to_parquet(combined_path, index=False)  # type: ignore[arg-type]

    return combined_path

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
    hh_is_head = pd.to_numeric(df.get("hh_IsHead", 0), errors="coerce").fillna(0).astype(int)
    hh_is_partner = pd.to_numeric(df.get("hh_IsPartner", 0), errors="coerce").fillna(0).astype(int)
    is_other = ~(hh_is_head.astype(bool) | hh_is_partner.astype(bool))
    other_income = df["ils_dispy"].where(is_other, 0.0)
    other_sum = other_income.groupby(df["idhh"]).sum()
    df["other_members_income"] = df["idhh"].map(other_sum).fillna(0.0)
    return df


# ---------------------------------------------------------------------------
# Helpers for loc and pi0
# ---------------------------------------------------------------------------

def _build_loc_distribution(df: pd.DataFrame) -> Optional[Dict[Any, float]]:
    """
    Build an empirical distribution over loc based on *working* individuals.

    Preferred definition of working:
        - if 'is_worker' exists (from RURO_prep.py): use that;
        - otherwise: hours > 0 (and lma == 1 if available).
    """
    if "loc" not in df.columns:
        return None

    # --- Working indicator ---
    if "is_worker" in df.columns:
        mask = pd.to_numeric(df["is_worker"], errors="coerce").fillna(0).astype(int) == 1
    else:
        # Fallback: hours > 0 (and lma == 1 if available)
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

    # Exclude "no occupation" code from the empirical distribution
    loc_series = pd.to_numeric(df.loc[mask, "loc"], errors="coerce")
    loc_series = loc_series[loc_series != -1]

    if loc_series.empty:
        return None

    counts = loc_series.value_counts(dropna=True)
    total = counts.sum()
    if total <= 0:
        return None

    return (counts / total).to_dict()


def _sample_loc(
    loc_probs: Optional[Dict[Any, float]],
    size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    if not loc_probs or size == 0:
        return np.array([None] * size, dtype=object)
    keys = np.array(list(loc_probs.keys()))
    p = np.array(list(loc_probs.values()), dtype=float)
    p = p / p.sum()
    idx = rng.choice(len(keys), size=size, p=p)
    return keys[idx]


def _draw_loc(loc_probs: Optional[Dict[Any, float]], rng: np.random.Generator, fallback: Any) -> Any:
    """
    Draw a single loc from a discrete distribution; fallback to observed loc if probs unavailable.
    """
    if not loc_probs:
        return fallback
    keys = np.array(list(loc_probs.keys()))
    p = np.array(list(loc_probs.values()), dtype=float)
    p = p / p.sum()
    idx = rng.choice(len(keys), p=p)
    return keys[idx]


# ---------------------------------------------------------------------------
# Core: make long draws
# ---------------------------------------------------------------------------

def generate_draws_long(
    df: pd.DataFrame,
    *,
    n_draws: int = DEFAULT_N_DRAWS,
    wage_spec: str = DEFAULT_WAGE_SPEC,
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
        * For inactive persons (lma != 1), π₀ = 0 (no extra mass at zero).
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
      their observed hours/wage/loc, for EUROMOD tax-benefit calculations.
    - If decider flags are missing, all persons are treated as deciders
      (with a warning).

    Output Structure
    ----------------
    - draw=0: observed job (exactly as in RURO_ready, is_chosen=1)
    - draw>=1: simulated opportunities (is_chosen=0)
    """
    import logging
    
    if n_draws < 0:
        raise ValueError("n_draws must be >= 0")

    df = df.copy().reset_index(drop=True)

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
        hh_is_head = pd.to_numeric(df["hh_IsHead"], errors="coerce").fillna(0).astype(int)
        hh_is_partner = pd.to_numeric(df.get("hh_IsPartner", 0), errors="coerce").fillna(0).astype(int)
        is_decider = (hh_is_head == 1) | (hh_is_partner == 1)
        n_deciders = is_decider.sum()
        n_nondeciders = (~is_decider).sum()
        logging.info(f"RURO_draws: {n_deciders} deciders, {n_nondeciders} non-deciders in input.")
    else:
        # No decider flags: assume all persons are deciders (backwards-compatible)
        logging.warning(
            "RURO_draws: hh_IsHead/hh_IsPartner columns not found. "
            "Assuming all persons in input are decision makers (heads/partners). "
            "If this is incorrect, ensure upstream filtering or add decider flags."
        )
        is_decider = pd.Series(True, index=df.index)

    # -------------------------------------------------------------------------
    # Hours alias
    # -------------------------------------------------------------------------
    if "hours" in df.columns:
        hours = pd.to_numeric(df["hours"], errors="coerce").fillna(0.0)
    elif "lhw" in df.columns:
        hours = pd.to_numeric(df["lhw"], errors="coerce").fillna(0.0)
        df["hours"] = hours
    else:
        raise KeyError("RURO_ready dataset must contain 'hours' or 'lhw'.")

    # -------------------------------------------------------------------------
    # Wage alias
    # -------------------------------------------------------------------------
    if "wage" in df.columns:
        wage = pd.to_numeric(df["wage"], errors="coerce").fillna(0.0)
    elif "wage_ruro" in df.columns:
        wage = pd.to_numeric(df["wage_ruro"], errors="coerce").fillna(0.0)
        df["wage"] = wage
    elif "yivwg" in df.columns:
        wage = pd.to_numeric(df["yivwg"], errors="coerce").fillna(0.0)
        df["wage"] = wage
    else:
        raise KeyError("RURO_ready dataset must contain 'wage', 'wage_ruro' or 'yivwg'.")

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

    # π₀ vector: probability of non-employment opportunity
    #   - pi0_m for active men (lma == 1 and dgn == 1)
    #   - pi0_f for active women (lma == 1 and dgn == 0)
    #   - 0 for inactive persons (lma != 1)
    pi0_vec = np.zeros(len(df), dtype=float)
    mask_m = (lma == 1) & (dgn == 1)  # active men
    mask_f = (lma == 1) & (dgn == 0)  # active women
    pi0_vec[mask_m.to_numpy()] = pi0_m
    pi0_vec[mask_f.to_numpy()] = pi0_f    # Inactive persons (lma != 1) have pi0 = 0 by default    # -------------------------------------------------------------------------
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
    df_draw0["is_chosen"] = 1

    # If no draws requested, return just the observed jobs
    if n_draws == 0:
        return df_draw0.reset_index(drop=True)

    # -------------------------------------------------------------------------
    # Part 2: Simulated opportunities (draw >= 1) for DECIDERS ONLY
    # -------------------------------------------------------------------------
    decider_df = df[is_decider].copy().reset_index(drop=True)
    n_deciders_actual = len(decider_df)
    
    if n_deciders_actual == 0:
        logging.warning("RURO_draws: No deciders found. Returning only observed jobs (draw=0).")
        return df_draw0.reset_index(drop=True)

    logging.info(f"RURO_draws: Generating {n_draws} draws for {n_deciders_actual} deciders (vectorized)...")
    
    # Total number of simulated records: n_deciders * n_draws
    n_sim = n_deciders_actual * n_draws
    
    # Replicate each decider n_draws times
    # Index into decider_df: [0,0,...,0, 1,1,...,1, ..., n-1,n-1,...,n-1]
    # Each person repeated n_draws times consecutively
    person_idx = np.repeat(np.arange(n_deciders_actual), n_draws)
    
    # Draw numbers: [1,2,...,n_draws, 1,2,...,n_draws, ...]
    draw_nums = np.tile(np.arange(1, n_draws + 1), n_deciders_actual)
    
    # Get pi0 for each simulated record (replicated from decider pi0_vec)
    decider_pi0 = pi0_vec[is_decider.to_numpy()]
    pi0_sim = decider_pi0[person_idx]
    
    # Get observed wage for each simulated record (for fixed wage spec)
    decider_wages = wage[is_decider].to_numpy()
    obs_wage_sim = decider_wages[person_idx]
    
    # Get baseline loc for each simulated record
    if "loc" in decider_df.columns:
        decider_loc = pd.to_numeric(decider_df["loc"], errors="coerce").fillna(-1).to_numpy()
    else:
        decider_loc = np.full(n_deciders_actual, -1)
    base_loc_sim = decider_loc[person_idx]
    
    # -------------------------------------------------------------------------
    # Vectorized random draws
    # -------------------------------------------------------------------------
    # Uniform draws to determine employment vs non-employment
    u_emp = rng.random(n_sim)
    is_nonemployment = u_emp < pi0_sim
    is_working = ~is_nonemployment
    
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
    loc_sim = np.where(is_nonemployment, -1, base_loc_sim)
    
    # yem: wage * hours * weeks_per_month
    yem_sim = wage_sim * hours_sim * WEEKS_PER_MONTH
    
    # -------------------------------------------------------------------------
    # Build simulated DataFrame efficiently
    # -------------------------------------------------------------------------
    # Replicate decider rows n_draws times using iloc indexing
    sim_df = decider_df.iloc[person_idx].copy().reset_index(drop=True)
    
    # Overwrite with simulated values
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
    if "loc" in sim_df.columns:
        sim_df["loc"] = loc_sim
    
    # -------------------------------------------------------------------------
    # Concatenate: draw=0 (all persons) + draws 1..n (deciders only)
    # -------------------------------------------------------------------------
    long_df = pd.concat([df_draw0, sim_df], ignore_index=True)
    
    # Sort by idperson and draw for consistency
    sort_cols = ["idperson", "draw"]
    if "idhh" in long_df.columns:
        sort_cols = ["idhh"] + sort_cols
    long_df = long_df.sort_values(sort_cols).reset_index(drop=True)
    
    logging.info(f"RURO_draws: Generated {len(long_df)} total records ({len(df_draw0)} observed + {len(sim_df)} simulated).")
    
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
    ap.add_argument("--pi0-m", type=float, default=DEFAULT_PI0_M,
                    help="Mass at zero hours for active men.")
    ap.add_argument("--pi0-f", type=float, default=DEFAULT_PI0_F,
                    help="Mass at zero hours for active women.")
    ap.add_argument("--h-min", type=float, default=DEFAULT_H_MIN,
                    help="Lower bound of hour support.")
    ap.add_argument("--h-max", type=float, default=DEFAULT_H_MAX,
                    help="Upper bound of hour support.")
    ap.add_argument("--w-min", type=float, default=DEFAULT_W_MIN,
                    help="Lower bound of wage support.")
    ap.add_argument("--w-max", type=float, default=DEFAULT_W_MAX,
                    help="Upper bound of wage support.")
    ap.add_argument("--rng-seed", type=int, default=DEFAULT_RNG_SEED,
                    help="Seed for the RNG (reproducible draws).")
    ap.add_argument("--run-euromod", action="store_true",
                    help="Run EUROMOD once on all draws ( combined run).")
    ap.add_argument("--euromod-root", type=str, default=None,
                    help="Path to EUROMOD release; defaults to env/resolved storage.")
    ap.add_argument("--euromod-system", type=str, default=None,
                    help="EUROMOD system code (default: <country>_<year>).")
    ap.add_argument("--euromod-dataset", type=str, default=None,
                    help="EUROMOD dataset name (default: raw stem).")
    ap.add_argument("--microdata-template", type=str, default=None,
                    help="Baseline microdata file to mutate per draw (required for EUROMOD).")
    ap.add_argument("--euromod-hours-col", type=str, default=DEFAULT_EUROMOD_HOURS_COL,
                    help="Column to overwrite for hours in EUROMOD runs.")
    ap.add_argument("--euromod-wage-col", type=str, default=DEFAULT_EUROMOD_WAGE_COL,
                    help="Column to overwrite for wages in EUROMOD runs.")
    ap.add_argument("--scenario-dir", type=str, default=None,
                    help="Output directory for EUROMOD scenarios (default: storage/interim/ruro/<country>/scenarios).")
    return ap.parse_args()


def main() -> None:
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
        pi0_m=args.pi0_m,
        pi0_f=args.pi0_f,
        h_min=args.h_min,
        h_max=args.h_max,
        w_min=args.w_min,
        w_max=args.w_max,
        rng_seed=args.rng_seed,
    )
    singles_out = _write_dataframe(singles_long, singles_path, suffix="_RURO_draws")
    print("Singles draws saved to:")
    for k, v in singles_out.items():
        print(f"  {k}: {v}")

    combined_draws = [singles_long]

    if args.couples_path:
        couples_path = Path(args.couples_path).resolve()
        if not couples_path.exists():
            raise FileNotFoundError(f"Couples RURO_ready file not found: {couples_path}")
        couples_df = _read_dataframe(couples_path)
        couples_df = _attach_other_members_income(couples_df)
        couples_long = generate_draws_long(
            couples_df,
            n_draws=args.n_draws,
            wage_spec=args.wage_spec,
            pi0_m=args.pi0_m,
            pi0_f=args.pi0_f,
            h_min=args.h_min,
            h_max=args.h_max,
            w_min=args.w_min,
            w_max=args.w_max,
            rng_seed=args.rng_seed + 1,  # different seed for couples
        )
        couples_out = _write_dataframe(couples_long, couples_path, suffix="_RURO_draws")
        print("Couples draws saved to:")
        for k, v in couples_out.items():
            print(f"  {k}: {v}")
        combined_draws.append(couples_long)

    # Optional EUROMOD simulation (single combined run for all draws)
    if args.run_euromod:
        print(
            "[RURO_draws] INFO: EUROMOD stage has been moved to scripts/RURO_euromod.py.\n"
            "Please run that script with your generated draws to avoid duplicate work."
        )

if __name__ == "__main__":
    main()
