#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RURO_euromod.py
===============

Implements the EUROMOD simulation stage for a Random Utility Random Opportunity
(RURO) labour supply model à la Aaberge & Colombino (1998) and Capeau & Decoster (2014).

This script follows the continuous RURO opportunity-set pipeline.

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
import datetime
import json
import logging
import math
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

# Ensure pythonnet uses CoreCLR (align with data_prep2.py)
os.environ.setdefault("PYTHONNET_RUNTIME", "coreclr")

# Add parent directory to path for sanity_checks import
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
except NameError:
    SCRIPT_DIR = Path.cwd()

from sanity_checks import sanity_report_euromod  # type: ignore  # noqa: E402

ENV_HINTS = ("MNL_STORAGE_ROOT", "MNL_DATA_ROOT", "MNL_ROOT")
DEFAULT_EUROMOD_HOURS_COL = "lhw"
DEFAULT_EUROMOD_WAGE_COL = "yivwg"
WEEKS_PER_MONTH = 52.0 / 12.0
FRANCE_STANDARD_HOURS = 35.0

# Known EUROMOD output prefixes to exclude from inputs
EUROMOD_OUTPUT_PREFIXES = ("ils_", "bho_", "bch_", "bdi_", "bed_", "bsa00_", "tin_", "tsc_")


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
    """
    Read DataFrame from various formats (consolidated from _read_microdata_file).

    Supports: .parquet, .csv, .txt, .dat (tab-delimited), .pkl, .pickle
    """
    suf = path.suffix.lower()
    if suf == ".parquet":
        return pd.read_parquet(path)  # type: ignore[arg-type]
    if suf == ".csv":
        return pd.read_csv(path)
    if suf in {".txt", ".dat"}:
        return pd.read_csv(path, sep="\t")
    if suf in {".pkl", ".pickle"}:
        return pd.read_pickle(path)
    raise ValueError(f"Unsupported dataset format: {path}")


def _try_read_drawsmeta_sidecar(draws_path: Path) -> Optional[Dict[str, Any]]:
    """
    Attempt to read __drawsmeta.json sidecar file from draws parquet path.

    Returns None if not found or if parsing fails.
    """
    sidecar_path = draws_path.parent / f"{draws_path.stem}__drawsmeta.json"
    if not sidecar_path.exists():
        return None
    try:
        with open(sidecar_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.warning(f"Failed to read draws metadata from {sidecar_path}: {e}")
        return None


def _compute_id_multiplier(max_draw: int, drawsmeta: Optional[Dict[str, Any]] = None) -> int:
    """
    Determine ID multiplier for draw-specific IDs.

    Priority:
    1. If drawsmeta contains 'id_multiplier', use it (preferred).
    2. Otherwise compute: 10 ** ceil(log10(max_draw + 1)), minimum 1000.

    Returns
    -------
    int
        ID multiplier (e.g., 1000 for max_draw=99, 10000 for max_draw=999).
    """
    # Priority 1: read from metadata
    if drawsmeta is not None and "id_multiplier" in drawsmeta:
        multiplier = int(drawsmeta["id_multiplier"])
        logging.info(f"RURO_euromod: Using id_multiplier={multiplier} from draws metadata sidecar")
        return multiplier

    # Priority 2: compute from max_draw
    if max_draw < 0:
        multiplier = 1000
    else:
        multiplier = 10 ** math.ceil(math.log10(max_draw + 1))
        multiplier = max(multiplier, 1000)

    logging.info(f"RURO_euromod: Computed id_multiplier={multiplier} from max_draw={max_draw} (no metadata sidecar found)")
    return multiplier


def _write_euromod_metadata(
    output_path: Path,
    *,
    system_code: str,
    dataset_name: str,
    n_rows: int,
    n_draws: int,
    id_multiplier: int,
    carried_columns: list[str],
) -> None:
    """
    Write EUROMOD run metadata sidecar JSON.

    Creates a file like: combined_draws_em__euromodmeta.json
    """
    sidecar_path = output_path.parent / f"{output_path.stem}__euromodmeta.json"

    metadata_json = {
        "system": system_code,
        "dataset": dataset_name,
        "n_rows": n_rows,
        "n_draws": n_draws,
        "id_multiplier": id_multiplier,
        "carried_columns": carried_columns,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "script": "enh_RURO_euromod.py",
    }

    try:
        with open(sidecar_path, "w", encoding="utf-8") as f:
            json.dump(metadata_json, f, indent=2)
        logging.info(f"RURO_euromod: Wrote EUROMOD metadata to {sidecar_path}")
    except Exception as e:
        logging.warning(f"RURO_euromod: Failed to write EUROMOD metadata {sidecar_path}: {e}")


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
    drawsmeta: Optional[Dict[str, Any]] = None,
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
    em_input = _read_dataframe(micro_template_path)

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
    # Optional occupation override from job-based draws.
    if "loc_ruro" in draws_df.columns:
        override_cols.append("loc_ruro")
    if "isco1" in draws_df.columns:
        override_cols.append("isco1")
    # Preserve job-model identifiers and metadata in merged/carry output.
    optional_job_cols = [
        "job_id",
        "hours_bin",
        "wage_bin",
        "baseline_job_id",
        "loc_ruro_draw",
        "loc_ruro_obs",
    ]
    for col in optional_job_cols:
        if col in draws_df.columns and col not in override_cols:
            override_cols.append(col)

    draws_sub = draws_df[override_cols].copy()
    
    # -------------------------------------------------------------------------
    # 3. Identify deciders vs non-deciders from the draws dataframe
    #
    #    The draws file comes from RURO_draws.py which:
    #    - Gives deciders (head/partner) draws 0, 1, 2, ..., N
    #    - Gives non-deciders (children, etc.) draw=0 ONLY
    #
    #    PREFERRED: Use explicit is_decider column if present in draws file.
    #    FALLBACK: Infer deciders as those who have draw > 0.
    #
    #    Non-deciders need to be replicated for each draw scenario so EUROMOD
    #    can compute household-level outcomes correctly.
    # -------------------------------------------------------------------------
    all_draws = sorted(draws_df["draw"].unique())
    max_draw = max(all_draws)

    # Compute ID multiplier dynamically (from metadata or from max_draw)
    id_multiplier = _compute_id_multiplier(max_draw, drawsmeta)

    # Identify deciders: prefer explicit column, fallback to draw>0 inference
    if "is_decider" in draws_df.columns:
        decider_ids = set(draws_df.loc[draws_df["is_decider"] == 1, id_col].unique())
        nondecider_ids = set(draws_df.loc[draws_df["is_decider"] == 0, id_col].unique())
        logging.info(f"RURO_euromod: Using explicit 'is_decider' column from draws file")
    else:
        # Fallback: infer from draw > 0
        person_max_draw = draws_df.groupby(id_col)["draw"].max()
        decider_ids = set(person_max_draw[person_max_draw > 0].index)
        nondecider_ids = set(person_max_draw[person_max_draw == 0].index)
        logging.info(f"RURO_euromod: Inferring deciders from draw > 0 (is_decider column not found)")

    logging.info(f"RURO_euromod: {len(decider_ids)} deciders, "
                 f"{len(nondecider_ids)} non-deciders in draws file.")
    
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

    # ---------------------------------------------------------------------
    # 6b. Sanity check: drop orphan (household, draw) rows that contain no decider
    #     This can happen if non-deciders were replicated over draws that are not
    #     actually available for a specific household (e.g., incomplete draw grids).
    # ---------------------------------------------------------------------
    if "idhh_true" in merged.columns:
        pairs = merged.loc[is_decider, ["idhh_true", "draw"]].drop_duplicates()
        before = len(merged)
        merged = (
            merged.merge(pairs.assign(_keep=1), on=["idhh_true", "draw"], how="inner")
                  .drop(columns="_keep")
        )
        dropped = before - len(merged)
        if dropped > 0:
            logging.warning(
                f"RURO_euromod: Dropped {dropped} orphan rows with no decider for their (idhh_true, draw)."
            )
        # Recompute is_decider after dropping
        is_decider = merged[id_col].isin(decider_ids)

    # -------------------------------------------------------------------------
    # 7. Labour-market activity flag (lma) - optional SILC/EUROMOD data variable
    #    NOTE: lma is a labor market attachment flag from SILC data (if present).
    #    This is NOT the same as the removed 'ruro_lma' pipeline variable.
    #    For RURO, lma is only used for diagnostics; working status is determined
    #    by hours>0 in the draw-specific opportunities.
    # -------------------------------------------------------------------------
    if "lma" in merged.columns:
        lma_raw = merged["lma"]
    else:
        # If lma is missing, assume everyone is labor-market attached (lma=1).
        # This is a fallback for datasets without SILC labor market flags.
        # For RURO, this mainly affects diagnostics since working status is determined by hours>0.
        logging.info(
            "RURO_euromod: 'lma' column (labor market attachment from SILC) not found in template. "
            "Using lma=1 for all persons (fallback). Working status is determined by hours>0 in RURO draws."
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
    # 10. YIVWG (hourly wage) assignment for EUROMOD input
    #     CRITICAL: Preserve wage for non-working deciders (lhw==0)
    # -------------------------------------------------------------------------
    # For working deciders: use draw-specific wage
    # For non-working deciders (lhw==0): KEEP baseline wage (do NOT zero out)
    # For non-deciders: keep baseline wage
    final_yivwg = np.where(working_mask, yivwg_from_draws, baseline_yivwg)
    merged[wage_col] = final_yivwg

    # -------------------------------------------------------------------------
    # 10b. Optional occupation override for deciders (job-choice draws)
    # -------------------------------------------------------------------------
    if "loc_ruro" in merged.columns or "loc_ruro_draw" in merged.columns:
        baseline_loc = (
            pd.to_numeric(merged["loc_ruro"], errors="coerce").fillna(-1).astype(int)
            if "loc_ruro" in merged.columns
            else pd.Series(-1, index=merged.index, dtype=int)
        )
        loc_from_draws = (
            pd.to_numeric(merged["loc_ruro_draw"], errors="coerce").fillna(-1).astype(int)
            if "loc_ruro_draw" in merged.columns
            else baseline_loc
        )
        merged["loc_ruro"] = np.where(is_decider, loc_from_draws, baseline_loc).astype(int)

    # LHW: Already set above via hours_col at line 628
    # Retrieve FINAL lhw that will be sent to EUROMOD
    final_lhw = pd.to_numeric(merged[hours_col], errors="coerce").fillna(0.0)

    # -------------------------------------------------------------------------
    # 11. CRITICAL FIX: Deterministic earnings identity from FINAL inputs
    #
    #     French EUROMOD uses yem00 (regular) + yemxp (overtime):
    #     - yem00: Regular employment income (hours ≤ 35 per week)
    #     - yemxp: Overtime pay (hours > 35 per week)
    #
    #     Compute yem00/yemxp/yem from FINAL lhw and FINAL yivwg (wage_col)
    #     that are being sent to EUROMOD, NOT from intermediate draw values.
    #     This ensures the identity yem = yem00 + yemxp holds exactly.
    # -------------------------------------------------------------------------
    FRANCE_STANDARD_HOURS = 35.0

    # Get baseline values for non-deciders
    baseline_yem00 = pd.to_numeric(merged["yem00"], errors="coerce").fillna(0.0) if "yem00" in merged.columns else pd.Series(0.0, index=merged.index)
    baseline_yemxp = pd.to_numeric(merged["yemxp"], errors="coerce").fillna(0.0) if "yemxp" in merged.columns else pd.Series(0.0, index=merged.index)
    baseline_yem = pd.to_numeric(merged["yem"], errors="coerce").fillna(0.0) if "yem" in merged.columns else pd.Series(0.0, index=merged.index)

    # Compute earnings for DECIDERS from FINAL lhw and FINAL yivwg
    # Split final hours into regular (≤35) and overtime (>35)
    regular_hours_final = np.minimum(final_lhw, FRANCE_STANDARD_HOURS)
    overtime_hours_final = np.maximum(final_lhw - FRANCE_STANDARD_HOURS, 0.0)

    # Calculate regular and overtime income using FINAL wage
    yem00_computed = regular_hours_final * final_yivwg * WEEKS_PER_MONTH
    yemxp_computed = overtime_hours_final * final_yivwg * WEEKS_PER_MONTH
    yem_computed = yem00_computed + yemxp_computed

    # Apply to DECIDERS only:
    # - working (lhw>0): use computed values
    # - not working (lhw==0): zero earnings (yem00=yemxp=yem=0), but yivwg already preserved above
    # NON-DECIDERS: keep baseline values
    merged["yem00"] = np.where(is_decider, yem00_computed, baseline_yem00)
    merged["yemxp"] = np.where(is_decider, yemxp_computed, baseline_yemxp)
    merged["yem"] = np.where(is_decider, yem_computed, baseline_yem)

    logging.info(f"RURO_euromod: ✅ Set yem00/yemxp/yem from FINAL lhw and FINAL yivwg (deterministic identity)")
    logging.info(f"RURO_euromod:    {working_mask.sum()} working deciders, {not_working_decider.sum()} non-working deciders")
    if working_mask.sum() > 0:
        n_overtime = (overtime_hours_final[working_mask] > 0).sum()
        logging.info(f"RURO_euromod:    yem00 range: {yem00_computed[working_mask].min():.2f} to {yem00_computed[working_mask].max():.2f}")
        logging.info(f"RURO_euromod:    {n_overtime} deciders with overtime (lhw > 35)")

    # -------------------------------------------------------------------------
    # 12. ASSERTION: Verify earnings identity yem = yem00 + yemxp
    # -------------------------------------------------------------------------
    final_yem = pd.to_numeric(merged["yem"], errors="coerce").fillna(0.0)
    final_yem00_check = pd.to_numeric(merged["yem00"], errors="coerce").fillna(0.0)
    final_yemxp_check = pd.to_numeric(merged["yemxp"], errors="coerce").fillna(0.0)

    identity_diff = (final_yem - (final_yem00_check + final_yemxp_check)).abs()
    max_diff = identity_diff.max()
    n_violations = (identity_diff > 1e-6).sum()

    if n_violations > 0:
        logging.error(f"RURO_euromod: ASSERTION FAILED - yem identity violated in {n_violations} rows! max_diff={max_diff:.6f}")
        raise ValueError(f"Earnings identity yem = yem00 + yemxp violated in {n_violations} rows (max_diff={max_diff:.6f})")

    logging.info(f"RURO_euromod: ✅ Earnings identity assertion passed (max_diff={max_diff:.10f})")

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
        merged["idhh"] = merged["idhh_true"] * id_multiplier + draw

    base_id = merged[f"{id_col}_true"]
    merged[id_col] = base_id * id_multiplier + draw

    # Kin IDs: 0 for missing, id * id_multiplier + draw otherwise
    for kin in ["idfather", "idmother", "idpartner"]:
        if kin in merged.columns:
            kin_old = pd.to_numeric(merged[kin], errors="coerce").fillna(0).astype(int)
            kin_new = np.where(kin_old == 0, 0, kin_old * id_multiplier + draw)
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
    # 15. Enforce explicit EUROMOD input schema
    #     Build EUROMOD input as: (template_cols ∪ force_input_cols) - output_cols
    #     Carry RURO-specific columns (draw, *_true, log_q_*) outside for merge-back
    # -------------------------------------------------------------------------

    # Columns from original template (baseline microdata)
    template_cols = original_template_cols

    # Force-input columns: scenario-specific inputs that MUST be sent even if not in template
    # These are the columns we've explicitly set for RURO draws
    force_input_cols_candidates = {hours_col, wage_col, "yem", "yem00", "yemxp", "yemmy", "lunmy", "bun", "bsa"}
    force_input_cols = {c for c in force_input_cols_candidates if c in merged.columns}

    # Build EUROMOD input column set: template columns + forced inputs
    euromod_input_cols_raw = template_cols | force_input_cols

    # Filter out EUROMOD output columns (prefixes from constant EUROMOD_OUTPUT_PREFIXES)
    # These should NEVER be sent as inputs; EUROMOD will compute them
    output_cols = [c for c in merged.columns
                   if any(c.startswith(prefix) for prefix in EUROMOD_OUTPUT_PREFIXES)]

    # Final EUROMOD input columns: raw set minus output columns
    euromod_input_cols = {c for c in euromod_input_cols_raw if c not in output_cols and c in merged.columns}

    # Build carry columns: everything NOT going to EUROMOD that we need to merge back
    # This includes: draw, *_true, log_q_*, hours, wage, and any other RURO-specific metadata
    carry_cols_set = {c for c in merged.columns if c not in euromod_input_cols}

    # Determine stable merge keys for merge-back
    # Prefer draw-specific IDs (idhh, idperson) if available
    # Otherwise use (*_true, draw) combination
    if id_col in merged.columns and "idhh" in merged.columns:
        # Draw-specific IDs are available (after multiplier transformation)
        key_cols = ["idhh", id_col]
    elif f"{id_col}_true" in merged.columns and "draw" in merged.columns:
        # Use true IDs + draw
        key_cols = [f"{id_col}_true", "draw"]
        if "idhh_true" in merged.columns:
            key_cols.insert(0, "idhh_true")
    else:
        raise ValueError("RURO_euromod: Cannot determine stable merge keys. Need either (idhh, idperson) or (*_true, draw)")

    # Ensure key columns are in carry set (they're needed for merge-back)
    for k in key_cols:
        carry_cols_set.add(k)

    carry_cols = sorted(carry_cols_set)

    logging.info(f"RURO_euromod: Building EUROMOD input schema:")
    logging.info(f"RURO_euromod:   - Template columns: {len(template_cols)}")
    logging.info(f"RURO_euromod:   - Force-input columns: {len(force_input_cols)} {sorted(force_input_cols)}")
    logging.info(f"RURO_euromod:   - Output columns filtered: {len(output_cols)}")
    logging.info(f"RURO_euromod:   - Final EUROMOD input columns: {len(euromod_input_cols)}")
    logging.info(f"RURO_euromod:   - Carry columns (for merge-back): {len(carry_cols)}")
    logging.info(f"RURO_euromod:   - Merge keys: {key_cols}")

    # Create EUROMOD input dataframe (explicit schema)
    euromod_input_df = merged[sorted(euromod_input_cols)].copy()

    # Create carry dataframe (all non-input columns + merge keys)
    carry_df = merged[carry_cols].copy()

    # Validation: check for output columns in input
    actual_output_in_input = [c for c in euromod_input_df.columns if c in output_cols]
    if actual_output_in_input:
        logging.warning(f"RURO_euromod: WARNING - Output columns in EUROMOD input: {actual_output_in_input[:5]}")

    logging.info(f"RURO_euromod: EUROMOD input shape: {euromod_input_df.shape}")
    logging.info(f"RURO_euromod: Carry data shape: {carry_df.shape}")

    # -------------------------------------------------------------------------
    # 16. Run EUROMOD simulation
    # -------------------------------------------------------------------------
    runner = EuromodRunner(em_root)
    sim_df = runner.run_on_dataframe(euromod_input_df, country=country, system_code=system_code, dataset_name=dataset_name)

    logging.info(f"RURO_euromod: EUROMOD simulation complete - output shape: {sim_df.shape}")

    # DEBUG: Verify ils_dispy values after EUROMOD
    if "ils_dispy" in sim_df.columns:
        logging.info(f"RURO_euromod DEBUG: ils_dispy after EUROMOD - min={sim_df['ils_dispy'].min():.2f}, "
                    f"max={sim_df['ils_dispy'].max():.2f}, mean={sim_df['ils_dispy'].mean():.2f}, "
                    f"nunique={sim_df['ils_dispy'].nunique()}")

    # -------------------------------------------------------------------------
    # 17. Robust merge-back: Add carry columns to EUROMOD output using stable keys
    #     Do NOT rely on row order - use explicit key-based merge
    # -------------------------------------------------------------------------

    # Identify which carry columns are NOT already in EUROMOD output (to avoid conflicts)
    euromod_output_cols_set = set(sim_df.columns)
    carry_cols_to_add = [c for c in carry_cols if c not in euromod_output_cols_set]

    logging.info(f"RURO_euromod: Merge-back preparation:")
    logging.info(f"RURO_euromod:   - EUROMOD output columns: {len(euromod_output_cols_set)}")
    logging.info(f"RURO_euromod:   - Carry columns to add: {len(carry_cols_to_add)} (out of {len(carry_cols)} total)")
    logging.info(f"RURO_euromod:   - Merge keys: {key_cols}")

    # Prepare carry dataframe for merge: keys + unique carry columns
    merge_carry_cols = list(set(key_cols + carry_cols_to_add))
    carry_df_for_merge = carry_df[merge_carry_cols].copy()

    # Harmonize key dtypes for safe merge
    for k in key_cols:
        if k in carry_df_for_merge.columns:
            carry_df_for_merge[k] = pd.to_numeric(carry_df_for_merge[k], errors="coerce").fillna(0).astype(int)
        if k in sim_df.columns:
            sim_df[k] = pd.to_numeric(sim_df[k], errors="coerce").fillna(0).astype(int)

    # Check for duplicate keys in carry data
    if carry_df_for_merge.duplicated(subset=key_cols).any():
        n_dups = carry_df_for_merge.duplicated(subset=key_cols).sum()
        dup_keys = carry_df_for_merge[carry_df_for_merge.duplicated(subset=key_cols, keep=False)][key_cols].drop_duplicates()
        logging.error(f"RURO_euromod: MERGE FAILED - {n_dups} duplicate keys in carry_df!")
        logging.error(f"RURO_euromod: First 5 duplicate keys:\n{dup_keys.head().to_string()}")
        raise ValueError(f"Carry dataframe has {n_dups} duplicate keys {key_cols}. Cannot safely merge back.")

    # Perform validated merge using ultra-memory-efficient direct assignment
    # For very large datasets (>1M rows), even set_index() can fail due to memory.
    # Use direct column assignment which requires no copies or intermediate arrays.
    #
    # CRITICAL SAFETY CHECK: Verify EUROMOD preserved row order by checking key alignment
    try:
        # Get columns to add (exclude key columns and columns already in EUROMOD output)
        euromod_output_cols_set = set(sim_df.columns)
        cols_to_add = [c for c in carry_cols_to_add if c not in euromod_output_cols_set]

        # Row order integrity check: verify keys match between sim_df and carry_df
        # Sample random rows to check alignment (cheap verification)
        n_rows = len(sim_df)
        if n_rows != len(carry_df_for_merge):
            logging.error(f"RURO_euromod: ROW COUNT MISMATCH - sim_df has {n_rows} rows, carry_df has {len(carry_df_for_merge)} rows!")
            raise ValueError(
                f"EUROMOD output has {n_rows} rows but carry data has {len(carry_df_for_merge)} rows. "
                f"Cannot safely use direct assignment."
            )

        # Sample up to 1000 random rows for key verification
        n_sample = min(1000, n_rows)
        sample_indices = np.random.choice(n_rows, size=n_sample, replace=False)

        # Check key alignment for sampled rows
        mismatches = []
        for idx in sample_indices:
            for k in key_cols:
                sim_val = sim_df.iloc[idx][k]
                carry_val = carry_df_for_merge.iloc[idx][k]
                if sim_val != carry_val:
                    mismatches.append({
                        "row": idx,
                        "key": k,
                        "sim_df": sim_val,
                        "carry_df": carry_val,
                    })
                    if len(mismatches) >= 10:  # Stop after finding 10 mismatches
                        break
            if len(mismatches) >= 10:
                break

        if mismatches:
            logging.error(f"RURO_euromod: ROW ORDER INTEGRITY CHECK FAILED!")
            logging.error(f"RURO_euromod: Found {len(mismatches)} key mismatches in {n_sample} sampled rows")
            for mm in mismatches[:5]:
                logging.error(f"RURO_euromod:   Row {mm['row']}, key '{mm['key']}': sim_df={mm['sim_df']}, carry_df={mm['carry_df']}")
            raise ValueError(
                f"Row order integrity check failed: keys do not align between sim_df and carry_df. "
                f"EUROMOD may have reordered rows. Cannot use direct assignment."
            )

        logging.info(f"RURO_euromod: ✅ Row order integrity check passed ({n_sample} sampled rows verified)")

        if cols_to_add:
            # Directly assign columns from carry_df to sim_df (no merge, no copy)
            # This is safe because we've verified row order is preserved
            for col in cols_to_add:
                sim_df[col] = carry_df_for_merge[col].values

            logging.info(f"RURO_euromod: ✅ Added {len(cols_to_add)} carry columns via direct assignment (zero-copy)")
        else:
            logging.info(f"RURO_euromod: No carry columns to add (all already in EUROMOD output)")

        result_df = sim_df
        logging.info(f"RURO_euromod: ✅ Merge-back successful using zero-copy direct assignment")
    except Exception as e:
        logging.error(f"RURO_euromod: Merge-back failed with error: {e}")
        logging.error(f"RURO_euromod: sim_df shape: {sim_df.shape}, carry_df shape: {carry_df_for_merge.shape}")
        if len(sim_df) != len(carry_df_for_merge):
            logging.error(f"RURO_euromod: ROW COUNT MISMATCH - cannot use direct assignment!")
            logging.error(f"RURO_euromod: This indicates EUROMOD may have dropped or added rows.")
        raise

    logging.info(f"RURO_euromod: Final merged dataset: {result_df.shape[0]} rows, {result_df.shape[1]} columns")

    # -------------------------------------------------------------------------
    # 18. Verification diagnostics: ils_dispy variation across draws
    #     Sample up to 100 persons and check within-person std of ils_dispy
    # -------------------------------------------------------------------------
    if "ils_dispy" in result_df.columns and "draw" in result_df.columns and f"{id_col}_true" in result_df.columns:
        # Sample up to 100 unique persons
        unique_persons = result_df[f"{id_col}_true"].unique()
        n_sample = min(100, len(unique_persons))
        sampled_persons = np.random.choice(unique_persons, size=n_sample, replace=False)

        # Compute within-person std of ils_dispy across draws
        person_stds = []
        for person_id in sampled_persons:
            person_data = result_df[result_df[f"{id_col}_true"] == person_id]["ils_dispy"]
            if len(person_data) > 1:
                person_stds.append(person_data.std())

        if person_stds:
            person_stds_arr = np.array(person_stds)
            min_std = person_stds_arr.min()
            median_std = np.median(person_stds_arr)
            max_std = person_stds_arr.max()

            logging.info(f"RURO_euromod VERIFICATION: ils_dispy within-person std over {n_sample} sampled persons:")
            logging.info(f"RURO_euromod:   min={min_std:.6f}, median={median_std:.6f}, max={max_std:.6f}")

            # Warn if most persons have near-zero std (ils_dispy not varying across draws)
            near_zero_count = (person_stds_arr < 1e-6).sum()
            near_zero_pct = near_zero_count / len(person_stds_arr) * 100
            if near_zero_pct > 50:
                logging.warning(f"RURO_euromod WARNING: {near_zero_pct:.1f}% of sampled persons have ils_dispy std < 1e-6!")
                logging.warning(f"RURO_euromod: This suggests EUROMOD may not be recalculating disposable income across draws.")
            else:
                logging.info(f"RURO_euromod: ✅ ils_dispy varies across draws ({near_zero_pct:.1f}% near-zero std)")
        else:
            logging.warning("RURO_euromod: Cannot compute ils_dispy std - insufficient data for sampled persons")
    else:
        logging.info("RURO_euromod: Skipping ils_dispy verification (missing required columns)")

    # -------------------------------------------------------------------------
    # 19. Write EUROMOD metadata sidecar
    # -------------------------------------------------------------------------
    combined_path = scenario_dir / "combined_draws_em.parquet"

    # Compute metadata values
    n_draws = len(result_df["draw"].unique()) if "draw" in result_df.columns else 0

    _write_euromod_metadata(
        combined_path,
        system_code=system_code,
        dataset_name=dataset_name,
        n_rows=len(result_df),
        n_draws=n_draws,
        id_multiplier=id_multiplier,
        carried_columns=carry_cols_to_add,
    )

    # -------------------------------------------------------------------------
    # 19.5. Runtime sanity checks (catch structural issues before writing output)
    # -------------------------------------------------------------------------
    logging.info("Running runtime sanity checks on EUROMOD outputs...")

    # Prepare metadata for sanity checks
    sanity_metadata = {
        "expected_rows": len(result_df),
        "n_draws": n_draws,
    }

    try:
        sanity_report_euromod(result_df, metadata=sanity_metadata)
        logging.info("✓ EUROMOD outputs passed all sanity checks")
    except Exception as e:
        logging.error(f"EUROMOD outputs FAILED sanity checks: {e}")
        raise

    # -------------------------------------------------------------------------
    # 20. Save combined output (EUROMOD output + carry columns)
    # -------------------------------------------------------------------------
    result_df.to_parquet(combined_path, index=False)  # type: ignore[arg-type]
    logging.info(f"RURO_euromod: ✅ Saved result_df with {len(result_df.columns)} columns to {combined_path}")
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

    # Read drawsmeta sidecar from singles file
    drawsmeta_s = _try_read_drawsmeta_sidecar(singles_path)

    drawsmeta_c = None
    if args.couples_draws:
        couples_path = Path(args.couples_draws).resolve()
        if not couples_path.exists():
            raise FileNotFoundError(f"Couples draws file not found: {couples_path}")
        couples_df = _read_dataframe(couples_path)
        combined.append(couples_df)
        # Read drawsmeta sidecar from couples file
        drawsmeta_c = _try_read_drawsmeta_sidecar(couples_path)

    # Reconcile metadata from singles and couples (consistency check)
    drawsmeta = None
    metas = [m for m in (drawsmeta_s, drawsmeta_c) if m is not None]
    if metas:
        id_mults = {int(m["id_multiplier"]) for m in metas if "id_multiplier" in m}
        if len(id_mults) > 1:
            raise ValueError(
                f"Inconsistent id_multiplier across draws files: {sorted(id_mults)}. "
                f"Singles and couples draws must use the same id_multiplier."
            )
        if id_mults:
            drawsmeta = {"id_multiplier": int(next(iter(id_mults)))}
            logging.info(f"RURO_euromod: Using id_multiplier={drawsmeta['id_multiplier']} from draws metadata sidecar(s)")

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
        drawsmeta=drawsmeta,
    )
    print(f"EUROMOD combined draws saved at: {combined_path}")


if __name__ == "__main__":
    main()
