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

2. **Deciders only for hours/wage mutation**: Only household decision makers
   (head and partner, flagged by `hh_IsHead` and `hh_IsPartner`) have their
   hours and wages overwritten according to the RURO draws. Children and other
   household members retain their original baseline hours/wages even for draw > 0,
   so that EUROMOD can correctly compute household-level outcomes.

3. **Draw-specific IDs**: To avoid ID clashes across draws, we create:
   - idhh = idhh_true * 1000 + draw
   - idperson = idperson_true * 1000 + draw
   - Kin IDs (idfather, idmother, idpartner) follow the same convention.
   The original IDs are preserved in `*_true` columns for later grouping.

4. **EUROMOD consistency fixes**: For working deciders (lma==1 and hours>0):
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
    # 1. Load EUROMOD baseline microdata
    # -------------------------------------------------------------------------
    em_input = _read_microdata_file(micro_template_path)

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

    draws_sub = draws_df[override_cols].copy()
    
    # -------------------------------------------------------------------------
    # 3. Merge: one EM row per (idperson, draw)
    # -------------------------------------------------------------------------
    merged = em_input.merge(draws_sub, on=id_col, how="inner", suffixes=("", "_draw"))
    if merged.empty:
        raise ValueError("EUROMOD input after merging with draws is empty. Check id alignment.")

    # -------------------------------------------------------------------------
    # 4. Store "true" IDs for later grouping in RURO_prep_mnl
    #    These allow us to reconstruct the individual and household across draws.
    # -------------------------------------------------------------------------
    if "idhh" in merged.columns:
        merged["idhh_true"] = merged["idhh"]
    merged[f"{id_col}_true"] = merged[id_col]

    draw = pd.to_numeric(merged["draw"], errors="coerce").fillna(0).astype(int)

    # -------------------------------------------------------------------------
    # 5. Decider mask: only heads/partners have hours/wages mutated
    #    Children and other members keep their baseline values for EUROMOD.
    # -------------------------------------------------------------------------
    has_decider_flags = "hh_IsHead" in merged.columns
    if has_decider_flags:
        hh_is_head = pd.to_numeric(merged["hh_IsHead"], errors="coerce").fillna(0).astype(int)
        hh_is_partner = pd.to_numeric(merged.get("hh_IsPartner", 0), errors="coerce").fillna(0).astype(int)
        is_decider = (hh_is_head == 1) | (hh_is_partner == 1)
        logging.info(f"RURO_euromod: Applying hours/wage overrides only to {is_decider.sum()} deciders.")
    else:
        # No decider flags: apply overrides to all (backwards-compatible)
        logging.warning(
            "RURO_euromod: hh_IsHead/hh_IsPartner columns not found in EUROMOD template. "
            "Assuming all persons are decision makers. "
            "This is a strong assumption; hours/wages will be overwritten for everyone."
        )
        is_decider = pd.Series(True, index=merged.index)

    # -------------------------------------------------------------------------
    # 6. Labour-market activity flag (lma)
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
    # 7. Hours and wage from RURO draws
    # -------------------------------------------------------------------------
    if "hours" in merged.columns:
        h_raw = merged["hours"]
    elif hours_col in merged.columns:
        h_raw = merged[hours_col]
    else:
        h_raw = pd.Series(0.0, index=merged.index)
    h = pd.to_numeric(h_raw, errors="coerce").fillna(0.0)

    if "wage" in merged.columns:
        w_raw = merged["wage"]
    elif wage_col in merged.columns:
        w_raw = merged[wage_col]
    else:
        w_raw = pd.Series(0.0, index=merged.index)
    w = pd.to_numeric(w_raw, errors="coerce").fillna(0.0)

    # -------------------------------------------------------------------------
    # 8. Apply hours/wage overrides for DECIDERS ONLY
    #    Non-deciders keep their baseline EUROMOD values.
    # -------------------------------------------------------------------------
    # Store baseline values
    baseline_h = pd.to_numeric(merged[hours_col], errors="coerce").fillna(0.0) if hours_col in merged.columns else h.copy()
    baseline_w = pd.to_numeric(merged[wage_col], errors="coerce").fillna(0.0) if wage_col in merged.columns else w.copy()
    
    # For deciders: use draw-specific hours; for non-deciders: keep baseline
    final_h = np.where(is_decider, h, baseline_h)
    merged[hours_col] = final_h
    merged["hours"] = final_h

    # For deciders: use draw-specific wage (if working); for non-deciders: keep baseline
    # Working mask applies only to deciders who are labour-market active with positive hours
    working_mask = is_decider & (lma == 1) & (pd.Series(final_h, index=merged.index) > 0.0)
    
    final_w = np.where(working_mask, w, baseline_w)
    merged[wage_col] = final_w
    merged["wage"] = final_w

    # -------------------------------------------------------------------------
    # 9. EUROMOD consistency fixes for RURO hypothetical jobs
    #    These adjustments ensure that EUROMOD treats hypothetical working
    #    scenarios correctly (transition from UB/SA to employment).
    # -------------------------------------------------------------------------
    
    # YEM: Employment income = hours * wage * weeks_per_month
    if "yem" in merged.columns:
        yem = pd.to_numeric(merged["yem"], errors="coerce").fillna(0.0)
        yem.loc[working_mask] = (
            pd.Series(final_h, index=merged.index)[working_mask] 
            * merged.loc[working_mask, wage_col] 
            * WEEKS_PER_MONTH
        )
        merged["yem"] = yem

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
    # 10. Draw-specific IDs (panel-like structure for EUROMOD)
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
    # 11. Sort for EUROMOD stability and run
    # -------------------------------------------------------------------------
    sort_cols = []
    if "idhh" in merged.columns:
        sort_cols.append("idhh")
    if id_col in merged.columns:
        sort_cols.append(id_col)
    if sort_cols:
        merged = merged.sort_values(sort_cols).reset_index(drop=True)

    runner = EuromodRunner(em_root)
    sim_df = runner.run_on_dataframe(merged, country=country, system_code=system_code, dataset_name=dataset_name)

    # -------------------------------------------------------------------------
    # 12. Reattach draw and "true" IDs to output
    # -------------------------------------------------------------------------
    sim_df["draw"] = merged["draw"].values
    if "idhh_true" in merged.columns:
        sim_df["idhh_true"] = merged["idhh_true"].values
    sim_df[f"{id_col}_true"] = merged[f"{id_col}_true"].values

    # -------------------------------------------------------------------------
    # 13. Save combined output
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
