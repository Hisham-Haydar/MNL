#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RURO_euromod.py
===============

Implements the EUROMOD simulation stage for a Random Utility Random Opportunity
(RURO) labour supply model à la Aaberge & Colombino (1998) and Capeau & Decoster (2014).

This script follows the structure of Stijn Van Houtven's Belgian RURO implementation.

Key Design Decisions
--------------------
1. **Single combined EUROMOD run**: All draws (singles + couples) are concatenated
   into one dataframe and passed to EUROMOD in a single call. This ensures
   consistent tax-benefit treatment across all hypothetical job scenarios.

2. **Deciders identified from draws file**: Deciders (head/partner) are identified
   by having draws > 0 in the draws file. Non-deciders (children, elderly) only
   have draw=0 and are replicated for each draw scenario so EUROMOD can correctly
   compute household-level tax-benefit outcomes.

3. **Deciders only for hours/wage mutation**: Only household decision makers
   have their hours and wages overwritten according to the RURO draws. Children
   and other household members retain their original baseline hours/wages even
   for draw > 0, so that EUROMOD can correctly compute household-level outcomes.

4. **Draw-specific IDs**: To avoid ID clashes across draws, we create:
   - idhh = idhh_true * 1000 + draw
   - idperson = idperson_true * 1000 + draw
   - Kin IDs (idfather, idmother, idpartner) follow the same convention.
   The original IDs are preserved in `*_true` columns for later grouping.

5. **EUROMOD consistency fixes**: For working deciders (lma==1 and hours>0):
   - yem = hours * wage * weeks_per_month
   - bun = 0 (no unemployment benefits when working)
   - bsa = 0 (no social assistance when working)
   - yemmy = 12, lunmy = 0 (full-year employment)

Usage example:
    python scripts/RURO_euromod.py \\
      --singles-draws U:/EUROMOD-STORAGE/Data/processed/fr/2021/singles_RURO_ready_RURO_draws.parquet \\
      --couples-draws U:/EUROMOD-STORAGE/Data/processed/fr/2021/couples_RURO_ready_RURO_draws.parquet \\
      --microdata-template U:/EUROMOD-STORAGE/Data/raw/FR_2021_c2.txt \\
      --euromod-root U:/EUROMOD-STORAGE/EUROMOD_RELEASES_J1.0+/EUROMOD_RELEASES_J1.0+ \\
      --euromod-system FR_2020 \\
      --euromod-dataset FR_2021_c2 \\
      --scenario-dir U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios
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

ENV_HINTS = ("MNL_STORAGE_ROOT", "MNL_DATA_ROOT", "MNL_ROOT")
DEFAULT_EUROMOD_HOURS_COL = "lhw"
DEFAULT_EUROMOD_WAGE_COL = "yivwg"
WEEKS_PER_MONTH = 52.0 / 12.0


# ---------------------------------------------------------------------------
# Path helpers
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
        try:
            resolved = candidate.resolve(strict=False)
        except OSError:
            resolved = candidate
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
        cand = Path(env).expanduser()
        if cand.exists():
            return cand
    storage = _resolve_storage_root()
    for rel in (
        Path("EUROMOD_RELEASES_J1.0+") / "EUROMOD_RELEASES_J1.0+",
        Path("EUROMOD_RELEASES_J1.0+"),
        Path("EUROMOD_RELEASES"),
        Path("euromod_releases"),
    ):
        candidate = storage / rel
        if candidate.exists():
            return candidate
    for child in storage.iterdir():
        if child.is_dir() and "euromod" in child.name.lower():
            return child
    raise FileNotFoundError("EUROMOD release directory not found; set MNL_EUROMOD_ROOT.")


# ---------------------------------------------------------------------------
# EUROMOD runners
# ---------------------------------------------------------------------------

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
# EUROMOD combined run over existing draws
# ---------------------------------------------------------------------------

def _read_dataframe(path: Path) -> pd.DataFrame:
    suf = path.suffix.lower()
    if suf == ".parquet":
        return pd.read_parquet(path)  # type: ignore[arg-type]
    if suf == ".csv":
        return pd.read_csv(path)
    if suf in {".pkl", ".pickle"}:
        return pd.read_pickle(path)
    raise ValueError(f"Unsupported dataset format: {path}")


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
    Run EUROMOD once on a combined draws dataframe (singles + couples, all draws).
    
    This function implements the EUROMOD stage of the RURO pipeline:
    
    1. Merge draw-specific hours/wage from RURO draws into EUROMOD microdata.
    2. Apply decider-only logic: only heads and partners have their hours/wages
       mutated according to draws; children and other members keep baseline values.
    3. Apply EUROMOD consistency fixes for hypothetical working scenarios.
    4. Create draw-specific IDs to form a panel-like structure.
    5. Run EUROMOD once on the full dataset.
    6. Save combined output to `combined_draws_em.parquet`.
    
    Parameters
    ----------
    draws_df : pd.DataFrame
        Long dataset with (idperson, draw) from RURO_draws.py.
    micro_template_path : Path
        Baseline EUROMOD microdata file.
    country : str
        Country code (e.g., "FR").
    system_code : str
        EUROMOD system code (e.g., "FR_2020").
    dataset_name : str
        EUROMOD dataset name (e.g., "FR_2021_c2").
    em_root : Path
        Path to EUROMOD release directory.
    scenario_dir : Path
        Output directory for EUROMOD results.
    id_col : str
        Person ID column name (default: "idperson").
    hours_col : str
        Hours column to overwrite (default: "lhw").
    wage_col : str
        Wage column to overwrite (default: "yivwg").
    
    Returns
    -------
    Path
        Path to the combined EUROMOD output file.
    """
    import logging
    
    scenario_dir = scenario_dir.resolve()
    scenario_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # 1. Load EUROMOD baseline microdata and store original columns
    # -------------------------------------------------------------------------
    em_input = _read_microdata_file(micro_template_path)

    # Store original EUROMOD template columns for later filtering
    # CRITICAL: Only columns that exist in the original dataset should be sent to EUROMOD
    # This prevents EUROMOD from receiving pre-calculated outputs (like ils_dispy from draws)
    original_template_cols = set(em_input.columns)
    logging.info(f"RURO_euromod: Original template has {len(original_template_cols)} columns")
    logging.info(f"RURO_euromod: ils_dispy in original template: {'ils_dispy' in original_template_cols}")

    # Show first 20 columns
    orig_cols_list = list(original_template_cols)[:20]
    logging.info(f"RURO_euromod: First 20 original columns: {orig_cols_list}")

    # -------------------------------------------------------------------------
    # 2. Validate draws dataframe
    # -------------------------------------------------------------------------
    if "draw" not in draws_df.columns:
        raise KeyError("draws_df must contain a 'draw' column.")
    if id_col not in draws_df.columns:
        raise KeyError(f"draws_df must contain '{id_col}'.")

    override_cols = [id_col, "draw"]
    if "hours" in draws_df.columns:
        override_cols.append("hours")
    if "wage" in draws_df.columns:
        override_cols.append("wage")
    # CRITICAL: Include yem and yivwg from draws to ensure EUROMOD uses
    # the correct employment income for each hypothetical scenario.
    # The draws file computes yem = lhw * wage * WEEKS_PER_MONTH for each draw.
    if "yem" in draws_df.columns:
        override_cols.append("yem")
    if "yivwg" in draws_df.columns:
        override_cols.append("yivwg")
    if "lhw" in draws_df.columns:
        override_cols.append("lhw")

    draws_sub = draws_df[override_cols].copy()
    
    # -------------------------------------------------------------------------
    # 3. Identify deciders vs non-deciders from the draws dataframe
    #    
    #    The draws file comes from RURO_draws.py which:
    #    - Gives deciders (head/partner) draws 0, 1, 2, ..., N
    #    - Gives non-deciders (children, etc.) draw=0 ONLY
    #    
    #    We identify deciders as those who have draw > 0.
    #    Non-deciders need to be replicated for each draw scenario so EUROMOD
    #    can compute household-level outcomes correctly.
    # -------------------------------------------------------------------------
    all_draws = sorted(draws_df["draw"].unique())
    max_draw = max(all_draws)
    
    # Deciders: have at least one draw > 0
    person_max_draw = draws_df.groupby(id_col)["draw"].max()
    decider_ids = set(person_max_draw[person_max_draw > 0].index)
    nondecider_ids = set(person_max_draw[person_max_draw == 0].index)
    
    logging.info(f"RURO_euromod: {len(decider_ids)} deciders (draw > 0), "
                 f"{len(nondecider_ids)} non-deciders (draw=0 only) in draws file.")
    
    # -------------------------------------------------------------------------
    # 4. Build full dataset: deciders + replicated non-deciders for each draw
    #    
    #    For EUROMOD household calculations:
    #    - Deciders: merge with draws to get (idperson, draw, hours, wage)
    #    - Non-deciders: replicate baseline for each draw 0..N
    # -------------------------------------------------------------------------
    
    # 4a. Deciders: merge with draws
    decider_draws = draws_sub[draws_sub[id_col].isin(decider_ids)]
    decider_merged = em_input.merge(decider_draws, on=id_col, how="inner", suffixes=("", "_draw"))
    
    # 4b. Non-deciders: replicate baseline for each draw
    nondecider_baseline = em_input[em_input[id_col].isin(nondecider_ids)].copy()
    if len(nondecider_baseline) > 0 and max_draw > 0:
        # Replicate for each draw
        nondecider_records = []
        for d in all_draws:
            nd_copy = nondecider_baseline.copy()
            nd_copy["draw"] = d
            # Non-deciders keep baseline hours/wage
            if "hours" not in nd_copy.columns and hours_col in nd_copy.columns:
                nd_copy["hours"] = nd_copy[hours_col]
            if "wage" not in nd_copy.columns and wage_col in nd_copy.columns:
                nd_copy["wage"] = nd_copy[wage_col]
            nondecider_records.append(nd_copy)
        nondecider_merged = pd.concat(nondecider_records, axis=0, ignore_index=True)
        logging.info(f"RURO_euromod: Replicated {len(nondecider_baseline)} non-deciders "
                     f"across {len(all_draws)} draws = {len(nondecider_merged)} rows.")
    else:
        nondecider_merged = pd.DataFrame()
    
    # 4c. Combine deciders and non-deciders
    if len(nondecider_merged) > 0:
        merged = pd.concat([decider_merged, nondecider_merged], axis=0, ignore_index=True)
    else:
        merged = decider_merged
    
    if merged.empty:
        raise ValueError("EUROMOD input after merging with draws is empty. Check id alignment.")
    
    logging.info(f"RURO_euromod: Combined dataset has {len(merged)} rows "
                 f"({len(decider_merged)} decider rows + {len(nondecider_merged) if len(nondecider_merged) > 0 else 0} non-decider rows).")

    # -------------------------------------------------------------------------
    # 5. Store "true" IDs for later grouping in RURO_prep_mnl
    #    These allow us to reconstruct the individual and household across draws.
    # -------------------------------------------------------------------------
    if "idhh" in merged.columns:
        merged["idhh_true"] = merged["idhh"]
    merged[f"{id_col}_true"] = merged[id_col]

    draw = pd.to_numeric(merged["draw"], errors="coerce").fillna(0).astype(int)

    # -------------------------------------------------------------------------
    # 6. Decider mask for hours/wage mutation
    #    Deciders get hours/wage from draws; non-deciders keep baseline.
    # -------------------------------------------------------------------------
    is_decider = merged[id_col].isin(decider_ids)
    logging.info(f"RURO_euromod: {is_decider.sum()} rows are deciders, "
                 f"{(~is_decider).sum()} rows are non-deciders.")

    # -------------------------------------------------------------------------
    # 7. Labour-market activity flag (lma)
    #    Fallback to lma=1 if missing, but document this as a strong assumption.
    # -------------------------------------------------------------------------
    if "lma" in merged.columns:
        lma_raw = merged["lma"]
    else:
        # STRONG ASSUMPTION: If lma is missing, we assume everyone is labour-market active.
        # This should rarely occur with properly prepared EUROMOD microdata.
        logging.warning(
            "RURO_euromod: 'lma' column not found in EUROMOD template. "
            "Assuming lma=1 for all persons. This is a strong assumption."
        )
        lma_raw = pd.Series(1, index=merged.index)
    lma = pd.to_numeric(lma_raw, errors="coerce").fillna(1).astype(int)

    # -------------------------------------------------------------------------
    # 8. Hours and wage from RURO draws
    #    For deciders, these come from the draws file (merged with _draw suffix).
    #    For non-deciders, they keep baseline values.
    # -------------------------------------------------------------------------
    # Hours: prefer draws value (_draw suffix) over template value
    if "hours_draw" in merged.columns:
        h_raw = merged["hours_draw"]
    elif "hours" in merged.columns:
        h_raw = merged["hours"]
    elif hours_col in merged.columns:
        h_raw = merged[hours_col]
    else:
        h_raw = pd.Series(0.0, index=merged.index)
    h = pd.to_numeric(h_raw, errors="coerce").fillna(0.0)

    # Wage: prefer draws value (_draw suffix) over template value
    if "wage_draw" in merged.columns:
        w_raw = merged["wage_draw"]
    elif "wage" in merged.columns:
        w_raw = merged["wage"]
    elif wage_col in merged.columns:
        w_raw = merged[wage_col]
    else:
        w_raw = pd.Series(0.0, index=merged.index)
    w = pd.to_numeric(w_raw, errors="coerce").fillna(0.0)
    
    # yem: prefer draws value (_draw suffix) - this is the computed yem = lhw * wage * WEEKS_PER_MONTH
    if "yem_draw" in merged.columns:
        yem_from_draws = pd.to_numeric(merged["yem_draw"], errors="coerce").fillna(0.0)
    elif "yem" in merged.columns:
        yem_from_draws = pd.to_numeric(merged["yem"], errors="coerce").fillna(0.0)
    else:
        yem_from_draws = pd.Series(0.0, index=merged.index)
    
    # yivwg: prefer draws value (_draw suffix) - hourly wage
    if "yivwg_draw" in merged.columns:
        yivwg_from_draws = pd.to_numeric(merged["yivwg_draw"], errors="coerce").fillna(0.0)
    elif "yivwg" in merged.columns:
        yivwg_from_draws = pd.to_numeric(merged["yivwg"], errors="coerce").fillna(0.0)
    else:
        yivwg_from_draws = w.copy()  # Fall back to wage
    
    # lhw: prefer draws value (_draw suffix) - weekly hours
    if "lhw_draw" in merged.columns:
        lhw_from_draws = pd.to_numeric(merged["lhw_draw"], errors="coerce").fillna(0.0)
    elif "lhw" in merged.columns:
        lhw_from_draws = pd.to_numeric(merged["lhw"], errors="coerce").fillna(0.0)
    else:
        lhw_from_draws = h.copy()  # Fall back to hours

    # -------------------------------------------------------------------------
    # 9. Apply hours/wage/yem/yivwg overrides for DECIDERS ONLY
    #    Non-deciders keep their baseline EUROMOD values.
    # -------------------------------------------------------------------------
    # Store baseline values (from EUROMOD template)
    baseline_h = pd.to_numeric(merged[hours_col], errors="coerce").fillna(0.0) if hours_col in merged.columns else h.copy()
    baseline_w = pd.to_numeric(merged[wage_col], errors="coerce").fillna(0.0) if wage_col in merged.columns else w.copy()
    baseline_yem = pd.to_numeric(merged["yem"], errors="coerce").fillna(0.0) if "yem" in merged.columns else pd.Series(0.0, index=merged.index)
    baseline_yivwg = pd.to_numeric(merged[wage_col], errors="coerce").fillna(0.0) if wage_col in merged.columns else pd.Series(0.0, index=merged.index)
    
    # For deciders: use draw-specific hours; for non-deciders: keep baseline
    final_h = np.where(is_decider, h, baseline_h)
    merged[hours_col] = final_h
    merged["hours"] = final_h

    # For deciders: use draw-specific wage (if working); for non-deciders: keep baseline
    # -------------------------------------------------------------------------
    # CRITICAL FIX: For RURO, we should NOT require lma==1 for working_mask.
    # The RURO model offers hypothetical jobs to people who may be unemployed (les=5),
    # inactive (les=7), etc. If a decider has hours > 0 in their draw, they should
    # be treated as "working" for that hypothetical scenario.
    # 
    # The lma variable is NOT a standard SILC variable (not in DRD) and may be
    # incorrectly set to 0 for labor force participants. Using hours > 0 alone
    # is the correct criterion for RURO hypothetical scenarios.
    # -------------------------------------------------------------------------
    working_mask = is_decider & (pd.Series(final_h, index=merged.index) > 0.0)
    not_working_decider = is_decider & (pd.Series(final_h, index=merged.index) <= 0.0)
    
    # Log how many deciders are affected
    n_working = working_mask.sum()
    n_not_working = not_working_decider.sum()
    n_deciders_total = is_decider.sum()
    logging.info(f"RURO_euromod: {n_working} decider-rows have hours > 0 (working), "
                 f"{n_not_working} have hours = 0 (not working)")
    
    # Apply wage for working deciders; baseline for non-working deciders and non-deciders
    final_w = np.where(working_mask, w, baseline_w)
    merged[wage_col] = final_w
    merged["wage"] = final_w

    # -------------------------------------------------------------------------
    # 10. CRITICAL FIX: French EUROMOD uses yem00 (regular) + yemxp (overtime)
    #
    #     The French system (EUROMO_sys_france_2015.md) uses:
    #     - yem00: Regular employment income (hours ≤ 35 per week)
    #     - yemxp: Overtime pay (hours > 35 per week)
    #
    #     France has a 35-hour standard workweek. We must split employment income
    #     into regular and overtime components for EUROMOD to calculate ils_dispy correctly.
    # -------------------------------------------------------------------------
    FRANCE_STANDARD_HOURS = 35.0

    # Split hours into regular (≤35) and overtime (>35)
    regular_hours = np.minimum(lhw_from_draws, FRANCE_STANDARD_HOURS)
    overtime_hours = np.maximum(lhw_from_draws - FRANCE_STANDARD_HOURS, 0.0)

    # Calculate regular and overtime income
    yem00_from_draws = regular_hours * yivwg_from_draws * WEEKS_PER_MONTH
    yemxp_from_draws = overtime_hours * yivwg_from_draws * WEEKS_PER_MONTH

    # Get baseline yem00 and yemxp for non-deciders
    baseline_yem00 = pd.to_numeric(merged["yem00"], errors="coerce").fillna(0.0) if "yem00" in merged.columns else pd.Series(0.0, index=merged.index)
    baseline_yemxp = pd.to_numeric(merged["yemxp"], errors="coerce").fillna(0.0) if "yemxp" in merged.columns else pd.Series(0.0, index=merged.index)

    # Set yem00 (regular employment income) - CRITICAL for ils_dispy!
    if "yem00" in merged.columns or "yem00" in original_template_cols:
        final_yem00 = np.where(working_mask, yem00_from_draws,
                              np.where(not_working_decider, 0.0, baseline_yem00))
        merged["yem00"] = final_yem00
        logging.info(f"RURO_euromod: ✅ Set yem00 (regular employment income) for {working_mask.sum()} working deciders")
        logging.info(f"RURO_euromod:    yem00 range: {yem00_from_draws[working_mask].min():.2f} to {yem00_from_draws[working_mask].max():.2f}, mean={yem00_from_draws[working_mask].mean():.2f}")
    else:
        logging.warning(f"RURO_euromod: ⚠️  yem00 not in template columns - this may cause ils_dispy to stay constant!")

    # Set yemxp (overtime pay)
    if "yemxp" in merged.columns or "yemxp" in original_template_cols:
        final_yemxp = np.where(working_mask, yemxp_from_draws,
                              np.where(not_working_decider, 0.0, baseline_yemxp))
        merged["yemxp"] = final_yemxp
        n_overtime = (overtime_hours[working_mask] > 0).sum()
        logging.info(f"RURO_euromod: ✅ Set yemxp (overtime pay) for {working_mask.sum()} working deciders ({n_overtime} with overtime)")
        if n_overtime > 0:
            logging.info(f"RURO_euromod:    yemxp range: {yemxp_from_draws[working_mask & (overtime_hours > 0)].min():.2f} to {yemxp_from_draws[working_mask & (overtime_hours > 0)].max():.2f}")
    else:
        logging.warning(f"RURO_euromod: ⚠️  yemxp not in template columns")

    # -------------------------------------------------------------------------
    # 11. EUROMOD consistency fixes for RURO hypothetical jobs
    #     Set yem (total) for compatibility, and update yivwg/lhw
    # -------------------------------------------------------------------------

    # YEM (total employment income): yem00 + yemxp for compatibility
    # Some EUROMOD policies may still reference yem
    baseline_yem = pd.to_numeric(merged["yem"], errors="coerce").fillna(0.0) if "yem" in merged.columns else pd.Series(0.0, index=merged.index)
    final_yem = np.where(working_mask, yem_from_draws,
                        np.where(not_working_decider, 0.0, baseline_yem))
    merged["yem"] = final_yem
    logging.info(f"RURO_euromod: Set yem (total employment income) for compatibility")

    # YIVWG: Hourly wage - use draws value for working deciders
    final_yivwg = np.where(working_mask, yivwg_from_draws,
                          np.where(not_working_decider, 0.0, baseline_yivwg))
    merged[wage_col] = final_yivwg
    
    # LHW: Already set above via hours_col, but ensure consistency
    # (lhw and hours should be the same for RURO)

    # -------------------------------------------------------------------------
    # 12. Additional EUROMOD consistency fixes
    # -------------------------------------------------------------------------

    # BUN: Unemployment benefits = 0 when working
    if "bun" in merged.columns:
        bun = pd.to_numeric(merged["bun"], errors="coerce").fillna(0.0)
        bun.loc[working_mask] = 0.0
        merged["bun"] = bun

    # BSA: Social assistance = 0 when working
    if "bsa" in merged.columns:
        bsa = pd.to_numeric(merged["bsa"], errors="coerce").fillna(0.0)
        bsa.loc[working_mask] = 0.0
        merged["bsa"] = bsa

    # YEMMY/LUNMY: Months in employment/unemployment
    if "yemmy" in merged.columns and "lunmy" in merged.columns:
        yemmy = pd.to_numeric(merged["yemmy"], errors="coerce")
        lunmy = pd.to_numeric(merged["lunmy"], errors="coerce")
        yemmy.loc[working_mask] = 12  # Full-year employment
        lunmy.loc[working_mask] = 0   # No unemployment months
        merged["yemmy"] = yemmy
        merged["lunmy"] = lunmy

    # -------------------------------------------------------------------------
    # 13. Draw-specific IDs (panel-like structure for EUROMOD)
    #     This allows EUROMOD to treat each draw as a separate "household" while
    #     we can still reconstruct original groupings via *_true columns.
    # -------------------------------------------------------------------------
    if "idhh" in merged.columns:
        merged["idhh"] = merged["idhh_true"] * 1000 + draw

    base_id = merged[f"{id_col}_true"]
    merged[id_col] = base_id * 1000 + draw

    # Kin IDs: 0 for missing, id * 1000 + draw otherwise
    for kin in ["idfather", "idmother", "idpartner"]:
        if kin in merged.columns:
            kin_old = pd.to_numeric(merged[kin], errors="coerce").fillna(0).astype(int)
            kin_new = np.where(kin_old == 0, 0, kin_old * 1000 + draw)
            merged[kin] = kin_new

    # -------------------------------------------------------------------------
    # 14. Sort for EUROMOD stability and filter columns
    # -------------------------------------------------------------------------
    sort_cols = []
    if "idhh" in merged.columns:
        sort_cols.append("idhh")
    if id_col in merged.columns:
        sort_cols.append(id_col)
    if sort_cols:
        merged = merged.sort_values(sort_cols).reset_index(drop=True)

    # DEBUG: Verify yem00/yemxp/yem values before EUROMOD
    if "yem00" in merged.columns:
        logging.info(f"RURO_euromod DEBUG: yem00 before EUROMOD - min={merged['yem00'].min():.2f}, "
                    f"max={merged['yem00'].max():.2f}, mean={merged['yem00'].mean():.2f}, "
                    f"nunique={merged['yem00'].nunique()}")
    if "yemxp" in merged.columns:
        logging.info(f"RURO_euromod DEBUG: yemxp before EUROMOD - min={merged['yemxp'].min():.2f}, "
                    f"max={merged['yemxp'].max():.2f}, mean={merged['yemxp'].mean():.2f}, "
                    f"nunique={merged['yemxp'].nunique()}")
    if "yem" in merged.columns:
        logging.info(f"RURO_euromod DEBUG: yem before EUROMOD - min={merged['yem'].min():.2f}, "
                    f"max={merged['yem'].max():.2f}, mean={merged['yem'].mean():.2f}, "
                    f"nunique={merged['yem'].nunique()}")
        # Sample one person to verify varying yem
        sample_person = merged[f"{id_col}_true"].iloc[0]
        sample_data = merged[merged[f"{id_col}_true"] == sample_person][['draw', 'yem', 'lhw', 'yivwg']].head(5)
        logging.info(f"RURO_euromod DEBUG: Sample person {sample_person} yem values:\n{sample_data.to_string()}")

    # -------------------------------------------------------------------------
    # 15. CRITICAL FIX: Column filtering before EUROMOD
    #     Only send columns that exist in original template to EUROMOD.
    #     EUROMOD does NOT recalculate fields that already exist in the input.
    #     We filter to only original template columns and store draw-specific columns
    #     to merge back after EUROMOD completes.
    # -------------------------------------------------------------------------

    # KEY INSIGHT: yem, lhw, yivwg exist in BOTH template and draws
    # We must use the DRAWN values (which vary), not template values (constant)!
    # So we CANNOT just filter to "columns in original template"
    # Instead: Filter out ils_* outputs and draw metadata, but KEEP drawn inputs

    # Find all ils_* OUTPUT columns to filter (not inputs like ils_earns)
    ils_output_cols = [c for c in merged.columns if c.startswith('ils_') and c != 'ils_earns']

    # Find draw metadata columns (draw, *_true, etc.) - not in original template
    draw_metadata_cols = [c for c in merged.columns if c not in original_template_cols and not c.startswith('ils_')]

    # Columns to filter out (not send to EUROMOD)
    cols_to_filter = set(ils_output_cols) | set(draw_metadata_cols)

    # Columns to send: everything EXCEPT filtered columns
    # This includes yem/lhw/yivwg with DRAWN values!
    cols_to_send = [c for c in merged.columns if c not in cols_to_filter]

    print(f"\n{'='*80}")
    print(f"RURO_euromod FIX: merged has {len(merged.columns)} total columns")
    print(f"RURO_euromod FIX: Filtering out {len(ils_output_cols)} ils_* output columns")
    print(f"RURO_euromod FIX: Filtering out {len(draw_metadata_cols)} draw metadata columns")
    print(f"RURO_euromod FIX: Sending {len(cols_to_send)} columns to EUROMOD")
    print(f"RURO_euromod FIX: ils_dispy will be filtered: {'ils_dispy' in cols_to_filter}")

    # Critical check: yem should be in cols_to_send and should VARY!
    if 'yem' in merged.columns:
        yem_std = merged['yem'].std()
        yem_in_send = 'yem' in cols_to_send
        print(f"RURO_euromod FIX: yem std={yem_std:.2f} yem in cols_to_send={yem_in_send}")
        if yem_std > 100 and yem_in_send:
            print(f"RURO_euromod FIX: [OK] yem VARIES and will be sent to EUROMOD - GOOD!")
        else:
            print(f"RURO_euromod FIX: [WARNING] yem problem detected!")

    print(f"{'='*80}\n")

    # Store filtered columns to merge back later
    draw_specific_data = merged[list(cols_to_filter)].copy()

    # Create dataset for EUROMOD with DRAWN values
    merged_for_euromod = merged[cols_to_send].copy()

    logging.info(f"RURO_euromod: Sending {len(cols_to_send)} columns to EUROMOD")
    logging.info(f"RURO_euromod: ils_dispy filtered out: {'ils_dispy' not in merged_for_euromod.columns}")

    runner = EuromodRunner(em_root)
    sim_df = runner.run_on_dataframe(merged_for_euromod, country=country, system_code=system_code, dataset_name=dataset_name)

    # DEBUG: Verify yem values after EUROMOD
    if "yem" in sim_df.columns:
        logging.info(f"RURO_euromod DEBUG: yem after EUROMOD - min={sim_df['yem'].min():.2f}, "
                    f"max={sim_df['yem'].max():.2f}, mean={sim_df['yem'].mean():.2f}, "
                    f"nunique={sim_df['yem'].nunique()}")

    # DEBUG: Verify ils_dispy values after EUROMOD
    if "ils_dispy" in sim_df.columns:
        logging.info(f"RURO_euromod DEBUG: ils_dispy after EUROMOD - min={sim_df['ils_dispy'].min():.2f}, "
                    f"max={sim_df['ils_dispy'].max():.2f}, mean={sim_df['ils_dispy'].mean():.2f}, "
                    f"nunique={sim_df['ils_dispy'].nunique()}")
        # Sample one person to verify varying ils_dispy
        if f"{id_col}_true" in merged.columns:
            sample_person = merged[f"{id_col}_true"].iloc[0]
            # Find matching rows in sim_df using original ID before draw-specific transformation
            # EUROMOD output has draw-specific IDs (id * 1000 + draw), so we need to extract the base ID
            if id_col in sim_df.columns:
                sim_df_base_ids = sim_df[id_col] // 1000
                sample_mask = (sim_df_base_ids == sample_person)
                if sample_mask.any():
                    sample_data = sim_df[sample_mask][['ils_dispy']].head(5)
                    sample_data.index = range(len(sample_data))
                    logging.info(f"RURO_euromod DEBUG: Sample person {sample_person} ils_dispy values from EUROMOD:\n{sample_data.to_string()}")

    # -------------------------------------------------------------------------
    # 16. Merge EUROMOD output with draw-specific data
    #     CRITICAL FIX: EUROMOD output has FULL PRIORITY
    #     - Keep ALL columns from EUROMOD simulation (original + new simulation outputs)
    #     - Only add draw-specific columns that are UNIQUE (don't exist in EUROMOD output)
    # -------------------------------------------------------------------------

    # Step 1: Identify which filtered columns are unique (not in EUROMOD output)
    euromod_output_cols = set(sim_df.columns)
    unique_draw_cols = cols_to_filter - euromod_output_cols

    logging.info(f"RURO_euromod: EUROMOD output has {len(euromod_output_cols)} columns")
    logging.info(f"RURO_euromod: Of {len(cols_to_filter)} filtered columns, "
                f"{len(unique_draw_cols)} are unique (not in EUROMOD output)")
    logging.info(f"RURO_euromod: Unique draw columns to add: {list(unique_draw_cols)[:10]}...")

    # Step 2: Add ONLY unique draw-specific columns to EUROMOD output
    #         EUROMOD columns (including common ones like yem, lhw) take priority
    for col in unique_draw_cols:
        if col in draw_specific_data.columns:
            sim_df[col] = draw_specific_data[col].values

    # Step 3: Verify row count matches
    if len(sim_df) != len(draw_specific_data):
        logging.warning(f"RURO_euromod: Row count mismatch! EUROMOD output has {len(sim_df)} rows, "
                       f"but draw_specific_data has {len(draw_specific_data)} rows")

    logging.info(f"RURO_euromod: Final merged dataset has {len(sim_df)} rows and {len(sim_df.columns)} columns")

    # Step 4: Verify that EUROMOD-calculated ils_dispy was used (not pre-EUROMOD baseline)
    if "ils_dispy" in sim_df.columns and "draw" in sim_df.columns:
        # Check if ils_dispy varies within persons across draws
        if f"{id_col}_true" in sim_df.columns:
            sample_person = sim_df[f"{id_col}_true"].iloc[0]
            person_data = sim_df[sim_df[f"{id_col}_true"] == sample_person].head(5)
            ils_std = person_data["ils_dispy"].std()
            logging.info(f"RURO_euromod VERIFICATION: Sample person {sample_person} ils_dispy std={ils_std:.6f} "
                        f"(should be > 0 if EUROMOD recalculated)")
            if ils_std < 1e-6:
                logging.warning(f"RURO_euromod WARNING: ils_dispy appears constant for person {sample_person}! "
                              f"EUROMOD may not have recalculated disposable income.")

    # -------------------------------------------------------------------------
    # 17. Save combined output
    # -------------------------------------------------------------------------
    combined_path = scenario_dir / "combined_draws_em.parquet"
    sim_df.to_parquet(combined_path, index=False)  # type: ignore[arg-type]
    return combined_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run EUROMOD on existing RURO draws (combined run).")
    ap.add_argument("--singles-draws", required=True, help="Path to singles_RURO_ready_RURO_draws file (parquet/csv/pkl).")
    ap.add_argument("--couples-draws", required=False, help="Path to couples_RURO_ready_RURO_draws file (optional).")
    ap.add_argument("--microdata-template", required=True, help="Baseline microdata file (txt/csv/parquet/pkl) to mutate per draw.")
    ap.add_argument("--euromod-root", type=Path, default=None, help="Path to EUROMOD release (override).")
    ap.add_argument("--euromod-system", type=str, required=True, help="EUROMOD system code, e.g., FR_2020.")
    ap.add_argument("--euromod-dataset", type=str, required=True, help="EUROMOD dataset name, e.g., FR_2021_c2.")
    ap.add_argument("--scenario-dir", type=Path, default=None, help="Output dir for EUROMOD scenarios (default: storage/interim/ruro/<country>/scenarios).")
    ap.add_argument("--euromod-hours-col", type=str, default=DEFAULT_EUROMOD_HOURS_COL, help="Column to overwrite for hours.")
    ap.add_argument("--euromod-wage-col", type=str, default=DEFAULT_EUROMOD_WAGE_COL, help="Column to overwrite for wages.")
    return ap.parse_args()


def main() -> None:
    """
    Main entry point: concatenate singles and couples draws, run EUROMOD once.
    
    This implements the "single EUROMOD run on all draws" philosophy:
    1. Load singles draws (required) and couples draws (optional).
    2. Concatenate into a single DataFrame.
    3. Drop rows with missing draw or idperson.
    4. Call run_euromod_for_draws once on the full dataset.
    5. Output: combined_draws_em.parquet
    
    This approach is more efficient than running EUROMOD per-draw and ensures
    consistent treatment of all hypothetical job scenarios.
    """
    args = parse_args()

    singles_path = Path(args.singles_draws).resolve()
    if not singles_path.exists():
        raise FileNotFoundError(f"Singles draws file not found: {singles_path}")
    singles_df = _read_dataframe(singles_path)
    combined = [singles_df]

    if args.couples_draws:
        couples_path = Path(args.couples_draws).resolve()
        if not couples_path.exists():
            raise FileNotFoundError(f"Couples draws file not found: {couples_path}")
        couples_df = _read_dataframe(couples_path)
        combined.append(couples_df)

    # Concatenate all draws into a single DataFrame
    combined_df = pd.concat(combined, axis=0, ignore_index=True)
    # Clean: drop rows with missing draw or idperson
    combined_df = combined_df.replace([np.inf, -np.inf], np.nan).dropna(subset=["draw", "idperson"])

    micro_path = Path(args.microdata_template).resolve()
    em_root = _euromod_root(args.euromod_root)
    scenario_dir = (
        args.scenario_dir.resolve()
        if args.scenario_dir
        else (_resolve_storage_root() / "interim" / "ruro" / args.euromod_system.split("_")[0].lower() / "scenarios")
    )

    # Run EUROMOD once on all draws
    combined_path = run_euromod_for_draws(
        combined_df,
        micro_path,
        country=args.euromod_system.split("_")[0],
        system_code=args.euromod_system,
        dataset_name=args.euromod_dataset,
        em_root=em_root,
        scenario_dir=scenario_dir,
        id_col="idperson",
        hours_col=args.euromod_hours_col,
        wage_col=args.euromod_wage_col,
    )
    print(f"EUROMOD combined draws saved at: {combined_path}")


if __name__ == "__main__":
    main()
