#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-11-28 13:25:34
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/
# @Version : 1.0.0


"""
RURO_prep.py

Minimal post-processing of the filtered datasets produced by data_prep2.py
to construct RURO-style explanatory variables needed for estimation.

Scope of this script
--------------------
Starting from:

    couples_filtering_final.<ext>
    singles_filtering_final.<ext>

it produces:

    couples_RURO_ready.<ext>
    singles_RURO_ready.<ext>

and only adds variables that are *not* already created in data_prep2:

    - ruro_group: 1 for singles, 10 for couples
    - ruro_sample: 1{ruro_decider == 1 AND dag >= 18}; others kept for EUROMOD only
    - wage_ruro: unified wage variable for workers, 0 for non-workers
    - is_worker: 1{les==3 & lhw>0}; uses lma only if informative (variation + any 1s)
    - working: 1{lhw>0}
    - working_pt1: 1{18.5 <= lhw <= 20.5} (focal ~20 hours)
    - working_pt2: 1{29.5 <= lhw <= 30.5} (focal ~30 hours)
    - working_ft: 1{37.5 <= lhw <= 40.5} (focal full-time)
    - pexp_years: potential experience in years (education-dependent start age)
    - pexp_years2: squared potential experience
    - pexp: potential experience / 100 (Stijn-style, in "hundreds of years")
    - educL: 1{deh in {0,1,2}} (low education dummy)
    - educH: 1{deh == 5} (high education dummy)
    - yd1, yd2, yd3: year dummies based on input_year/system_year
    - reg_nuts1_1 ... reg_nuts1_10: France NUTS 1 region dummies (from drgn1)
      (Île-de-France = reg_nuts1_1 is intended as the baseline at estimation)

This script deliberately does NOT:
    - compute equivalised income or CPI-uprated income;
    - touch your disposable-income variables.

Those can be handled separately for presentation/robustness checks.
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, cast

import numpy as np
import pandas as pd
from pandas.api import types as ptypes

# ---------------------------------------------------------------------------
# Bootstrap paths (same style as data_prep2.py)
# ---------------------------------------------------------------------------
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:  # interactive environments
    SCRIPT_DIR = Path.cwd() / "scripts"
PROJECT_ROOT = (SCRIPT_DIR / "..").resolve()

# Make sure SCRIPT_DIR and PROJECT_ROOT are on sys.path for local helpers.
for candidate in (SCRIPT_DIR, PROJECT_ROOT):
    c_str = str(candidate)
    if c_str not in sys.path:
        sys.path.insert(0, c_str)


from path_helpers import data_root, ensure_dir, resolve_storage_root  # type: ignore  # noqa: E402
from sanity_checks import sanity_report_ruro_prep  # type: ignore  # noqa: E402

# Legacy scratch helper is optional; use the fallback if it is archived/missing.
SCRATCH_DIR = PROJECT_ROOT / "scratch"
if SCRATCH_DIR.exists():
    sys.path.insert(0, str(SCRATCH_DIR))

try:
    from scratch.my_functions import setup_logging  # type: ignore
except Exception:
    def setup_logging(level: str = "INFO") -> None:
        """Fallback logging configuration when scratch.my_functions is unavailable."""
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logging.basicConfig(
            level=numeric_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )



DEFAULT_COUNTRY = "fr"
DEFAULT_YEAR = 2021
DEFAULT_EXPORT_FORMAT = "parquet"


# ---------------------------------------------------------------------------
# Path resolution helper (keep near top so CLI can call it)
# ---------------------------------------------------------------------------
def _maybe_add_column(df: pd.DataFrame, name: str, values: Any) -> None:
    """
    Add a column `name` to df with given `values` only if it does not exist yet.

    This ensures RURO_prep does not overwrite variables already created in
    data_prep2.py or elsewhere in the pipeline.
    """
    if name in df.columns:
        return
    # If a Series is passed and its index does not match df.index, warn and reindex.
    if isinstance(values, pd.Series) and not values.index.equals(df.index):
        logging.warning("Column %s: Series index misaligned; reindexing to df.index.", name)
        values = values.reindex(df.index)
    df[name] = values


def _load_colgroups_metadata(processed_dir: Path, year: int, export_format: str) -> Dict[str, Any]:
    """
    Load column-group metadata from input sidecar JSON if it exists.

    Looks for files like:
        - fr_{year}__colgroups.json (france_data_prep.py style)
        - colgroups.json (fallback)

    Returns dict with A_cols, B_cols, C_cols (or empty lists if not found).
    """
    # Try france_data_prep.py naming convention first
    sidecar_candidates = [
        processed_dir / f"fr_{year}__colgroups.json",
        processed_dir / "__colgroups.json",
        processed_dir / "colgroups.json",
    ]

    for sidecar_path in sidecar_candidates:
        if sidecar_path.exists():
            try:
                with open(sidecar_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                logging.info(f"Loaded column-group metadata from {sidecar_path}")
                return {
                    "A_cols": data.get("A_cols", []),
                    "B_cols": data.get("B_cols", []),
                    "C_cols": data.get("C_cols", []),
                    "metadata": data.get("metadata", {}),
                }
            except Exception as e:
                logging.warning(f"Failed to load {sidecar_path}: {e}")

    logging.info("No column-group sidecar found; will create fresh metadata")
    return {"A_cols": [], "B_cols": [], "C_cols": [], "metadata": {}}


def _write_colgroups_sidecar(
    output_path: Path,
    A_cols: List[str],
    B_cols: List[str],
    C_cols: List[str],
    force_input_cols_hint: List[str],
    metadata: Dict[str, Any],
) -> None:
    """
    Write column-group sidecar JSON for RURO_ready outputs.

    Creates a file like: singles_RURO_ready__colgroups.json
    """
    # Derive sidecar path from output path
    sidecar_path = output_path.parent / f"{output_path.stem}__colgroups.json"

    colgroups_json = {
        "A_cols": sorted(A_cols),
        "B_cols": sorted(B_cols),
        "C_cols": sorted(C_cols),
        "force_input_cols_hint": sorted(force_input_cols_hint),
        "metadata": {
            **metadata,
            "script": "enh_RURO_prep.py",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "output_file": str(output_path),
        },
    }

    try:
        with open(sidecar_path, "w", encoding="utf-8") as f:
            json.dump(colgroups_json, f, indent=2)
        logging.info(f"Wrote column-group sidecar to {sidecar_path}")
    except Exception as e:
        logging.warning(f"Failed to write sidecar {sidecar_path}: {e}")


def _ensure_true_ids_and_deciders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Guarantee presence of true ID columns and standardized decider flags.

    Creates/preserves:
        - idperson_true: copy of idperson before any transformations
        - idhh_true: copy of idhh before any transformations
        - hh_IsHead: 0/1 int (standardized from existing flags)
        - hh_IsPartner: 0/1 int (standardized from existing flags)
        - ruro_is_decider: 1 if head or partner, else 0
    """
    df = df.copy()

    # 1. True IDs: preserve original identifiers
    if "idperson_true" not in df.columns:
        df["idperson_true"] = df["idperson"].copy()
    if "idhh_true" not in df.columns:
        df["idhh_true"] = df["idhh"].copy()

    # 2. Standardize decider flags
    if "hh_IsHead" not in df.columns:
        df["hh_IsHead"] = 0
    df["hh_IsHead"] = pd.to_numeric(df["hh_IsHead"], errors="coerce").fillna(0).astype(int)

    if "hh_IsPartner" not in df.columns:
        df["hh_IsPartner"] = 0
    df["hh_IsPartner"] = pd.to_numeric(df["hh_IsPartner"], errors="coerce").fillna(0).astype(int)

    # 3. Unified decider marker
    ruro_is_decider = ((df["hh_IsHead"] == 1) | (df["hh_IsPartner"] == 1)).astype(int)
    df["ruro_is_decider"] = ruro_is_decider

    return df


def _validate_decider_counts(df: pd.DataFrame, expected_count: int, household_type: str) -> None:
    """
    Validate that each household has exactly expected_count deciders.

    Args:
        df: DataFrame with idhh_true and ruro_is_decider
        expected_count: 1 for singles, 2 for couples
        household_type: "singles" or "couples" (for error messages)

    Raises:
        ValueError: if any household has wrong decider count
    """
    decider_counts = df.groupby("idhh_true")["ruro_is_decider"].sum()
    violations = decider_counts[decider_counts != expected_count]

    if len(violations) > 0:
        # Log detailed violation info
        violation_summary = violations.value_counts().sort_index()
        logging.error(
            f"Decider count validation failed for {household_type}:\n"
            f"Expected {expected_count} decider(s) per household, found violations in {len(violations)} households:\n"
            f"{violation_summary.to_dict()}"
        )

        # Show sample violating households
        sample_idhh = violations.head(10).index.tolist()
        sample_df = df[df["idhh_true"].isin(sample_idhh)][
            ["idhh_true", "idperson_true", "hh_IsHead", "hh_IsPartner", "ruro_is_decider"]
        ]
        logging.error(f"Sample violating households:\n{sample_df.to_string()}")

        raise ValueError(
            f"Decider count validation failed for {household_type}: "
            f"{len(violations)} households have wrong decider count (expected {expected_count}). "
            f"Check logs for details."
        )

    logging.info(
        f"Decider count validation passed for {household_type}: "
        f"all {len(decider_counts)} households have exactly {expected_count} decider(s)"
    )


def _ensure_baseline_labor_references(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Ensure baseline labor-input reference columns exist for draw=0 consistency.

    Creates (if not present):
        - lhw_base := lhw
        - yivwg_base := yivwg
        - yem00_base, yemxp_base, yem_base (if source columns exist)

    Returns:
        (modified_df, list_of_baseline_cols_created)
    """
    df = df.copy()
    baseline_cols_created = []

    # Core labor inputs
    if "lhw" in df.columns and "lhw_base" not in df.columns:
        df["lhw_base"] = df["lhw"].copy()
        baseline_cols_created.append("lhw_base")

    if "yivwg" in df.columns and "yivwg_base" not in df.columns:
        df["yivwg_base"] = df["yivwg"].copy()
        baseline_cols_created.append("yivwg_base")

    # Additional EUROMOD wage/employment columns
    for col in ["yem00", "yemxp", "yem"]:
        baseline_col = f"{col}_base"
        if col in df.columns and baseline_col not in df.columns:
            df[baseline_col] = df[col].copy()
            baseline_cols_created.append(baseline_col)

    if baseline_cols_created:
        logging.info(f"Created baseline labor reference columns: {baseline_cols_created}")

    return df, baseline_cols_created


def _resolve_processed_dir(
    arg_dir: Path | None,
    base_year: int,
    export_format: str = DEFAULT_EXPORT_FORMAT,
) -> Path:
    """
    Resolve the processed directory, preferring external storage (EUROMOD-STORAGE) when present.

    If a relative path is provided, it is searched under all known storage roots (data_root,
    resolve_storage_root, U:/EUROMOD-STORAGE, ~/EUROMOD-STORAGE).
    """
    if arg_dir is not None and arg_dir.is_absolute():
        return arg_dir

    rel = arg_dir if arg_dir is not None else Path("processed") / DEFAULT_COUNTRY / str(base_year)

    candidates: list[Path] = []
    try:
        candidates.append(resolve_storage_root())
    except Exception:
        pass
    # Explicit external hints
    candidates.append(Path(r"U:/EUROMOD-STORAGE"))
    candidates.append(Path.home() / "EUROMOD-STORAGE")
    # Repo-local data_root is often the correct anchor (e.g. <repo>/data)
    candidates.append(data_root())
    candidates.append(data_root().parent)

    chosen: Path | None = None
    for root in candidates:
        options: list[Path] = []
        # If the candidate root already is a 'Data' folder, use it directly.
        if root.name.lower() == "data":
            options.append(root / rel)
        else:
            # Prefer root/Data/<rel> when the Data subfolder exists, otherwise consider root/<rel>.
            data_dir = root / "Data"
            if data_dir.exists():
                options.append(data_dir / rel)
            options.append(root / rel)
        for candidate in options:
            if not candidate.exists():
                continue
            # Prefer a path that actually contains the expected files
            primary_singles = candidate / f"singles_filtering_final.{export_format}"
            primary_couples = candidate / f"couples_filtering_final.{export_format}"
            alt_singles = candidate / f"fr_{base_year}_singles.{export_format}"
            alt_couples = candidate / f"fr_{base_year}_couples.{export_format}"

            has_primary = primary_singles.exists() and primary_couples.exists()
            has_alt = alt_singles.exists() and alt_couples.exists()

            if has_primary or has_alt:
                return candidate.resolve()
            chosen = chosen or candidate

    if chosen:
        raise FileNotFoundError(
            f"Found candidate processed dir {chosen} but expected RURO files "
            f"were missing (singles/couples in either filtering_final.* or fr_{base_year}_*.{export_format})."
        )
    raise FileNotFoundError(
        "Could not locate a processed directory containing singles/couples RURO inputs. "
        "Please run france_data_prep.py first or pass --processed-dir explicitly."
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _log_ruro_summary(df: pd.DataFrame, name: str) -> None:
    """Lightweight diagnostic logging for RURO-ready datasets."""
    # Safe defaults for possibly-missing columns
    hh = int(df["idhh"].nunique()) if "idhh" in df.columns else 0
    n = len(df)
    ruro_sample = int(df.get("ruro_sample", pd.Series(0, index=df.index)).sum())
    working = float(df.get("working", pd.Series(0, index=df.index)).mean())
    isw = float(df.get("is_worker", pd.Series(0, index=df.index)).mean())

    w_series = pd.to_numeric(df.get("wage_ruro", pd.Series(0, index=df.index)), errors="coerce")
    w_pos = w_series[w_series > 0].dropna()

    drgn1_s = df.get("drgn1", pd.Series(np.nan, index=df.index))
    drgn1_missing = float(pd.isna(drgn1_s).mean())
    drgn1_uniq = int(pd.Series(drgn1_s).dropna().nunique())

    # Prefer loc_ruro when available; otherwise fall back to loc
    loc_s = pd.to_numeric(df.get("loc_ruro", df.get("loc", pd.Series(np.nan, index=df.index))), errors="coerce")
    loc_missing = float(pd.isna(loc_s).mean())
    loc_uniq = int(loc_s.dropna().nunique())

    # loc4 (collapsed 4-group occupation) diagnostics
    loc4_s = pd.to_numeric(df.get("loc4", pd.Series(np.nan, index=df.index)), errors="coerce")
    loc4_missing = float(pd.isna(loc4_s).mean())
    loc4_uniq = int(loc4_s.dropna().nunique())

    logging.info(
        "[%s] rows=%d households=%d ruro_sample=%d mean(working)=%.3f mean(is_worker)=%.3f "
        "w_pos_n=%d w_pos_p50=%s drgn1_missing=%.3f drgn1_uniq=%d loc_missing=%.3f loc_uniq=%d loc4_missing=%.3f loc4_uniq=%d",
        name,
        n,
        hh,
        ruro_sample,
        working,
        isw,
        len(w_pos),
        float(w_pos.median()) if len(w_pos) else np.nan,
        drgn1_missing,
        drgn1_uniq,
        loc_missing,
        loc_uniq,
        loc4_missing,
        loc4_uniq,
    )
    # Warn when lma exists but is degenerate (no variation or no workers flagged)
    # lma = labor market attachment flag from SILC/EUROMOD data (if present)
    if "lma" in df.columns:
        lma = pd.to_numeric(df["lma"], errors="coerce").fillna(0)
        informative = (lma == 1).any() and lma.nunique(dropna=True) > 1
        if not informative:
            logging.warning(
                "[%s] 'lma' column (labor market attachment from SILC data) exists but is not informative "
                "(no lma==1 flags or no variation). Worker identification will use 'les' (employment status) instead.",
                name,
            )

def _compute_is_worker(df: pd.DataFrame) -> pd.Series:
    """
    Compute is_worker boolean Series for France RURO data.

    Worker identification logic (hierarchical):
      1. If 'lma' (labor market attachment from SILC) exists and is informative: use lma==1 & lhw>0
      2. Otherwise: use les==3 (employee) & lhw>0

    Note: lma is a SILC/EUROMOD data variable (not the removed ruro_lma pipeline variable).
    Always requires positive hours (lhw > 0) to flag as worker.
    """
    lhw = pd.to_numeric(df.get("lhw", pd.Series(0, index=df.index)), errors="coerce").fillna(0.0)
    les = pd.to_numeric(df.get("les", pd.Series(np.nan, index=df.index)), errors="coerce")

    if "lma" in df.columns:
        lma = pd.to_numeric(df["lma"], errors="coerce").fillna(0)
        # Use lma only when it contains any lma==1 and has variation (non-degenerate)
        if (lma == 1).any() and lma.nunique(dropna=True) > 1:
            return (lma == 1) & (lhw > 0.0)
    return les.eq(3) & (lhw > 0.0)

def _load_filtered_data(
    processed_dir: Path,
    export_format: str = DEFAULT_EXPORT_FORMAT,
    base_year: int | None = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load singles and couples filtered datasets produced by data_prep2.py or france_data_prep.py.

    Supports two naming conventions:
        1. couples_filtering_final.<export_format> / singles_filtering_final.<export_format>
           (from data_prep2.py)
        2. fr_{year}_couples.<export_format> / fr_{year}_singles.<export_format>
           (from france_data_prep.py)
    """
    # Try naming convention 1: data_prep2.py style
    singles_path = processed_dir / f"singles_filtering_final.{export_format}"
    couples_path = processed_dir / f"couples_filtering_final.{export_format}"

    # If not found, try naming convention 2: france_data_prep.py style
    if not singles_path.exists() or not couples_path.exists():
        # Try to infer year from directory name or use base_year
        year = base_year
        if year is None:
            # Try to extract year from directory name (e.g., .../fr/2016/)
            try:
                year = int(processed_dir.name)
            except ValueError:
                pass
        
        if year is not None:
            alt_singles = processed_dir / f"fr_{year}_singles.{export_format}"
            alt_couples = processed_dir / f"fr_{year}_couples.{export_format}"
            if alt_singles.exists() and alt_couples.exists():
                singles_path = alt_singles
                couples_path = alt_couples

    if not singles_path.exists():
        raise FileNotFoundError(f"Singles file not found: {singles_path}")
    if not couples_path.exists():
        raise FileNotFoundError(f"Couples file not found: {couples_path}")

    if export_format == "parquet":
        singles = pd.read_parquet(singles_path)  # type: ignore[arg-type]
        couples = pd.read_parquet(couples_path)  # type: ignore[arg-type]
    else:
        singles = pd.read_csv(singles_path)
        couples = pd.read_csv(couples_path)

    required = {"idhh", "idperson", "dag", "lhw", "les"}
    missing_s = required - set(singles.columns)
    missing_c = required - set(couples.columns)
    if missing_s:
        raise KeyError(f"Singles dataset is missing columns: {sorted(missing_s)}")
    if missing_c:
        raise KeyError(f"Couples dataset is missing columns: {sorted(missing_c)}")

    return singles, couples


def _infer_year_series(df: pd.DataFrame, default_year: int) -> pd.Series:
    """
    Get a per-observation year series used for pexp and year dummies.

    Priority (safe):
      1. data_year (explicit stamp by france prep)
      2. input_year (compatibility alias)
      3. system_year
      4. fallback: default_year (scalar)

    NEVER use 'yds' here (FR uses yds for disposable income).
    Implausible years (<1900 or >2100) are replaced by default_year.
    """
    if "data_year" in df.columns:
        year = pd.to_numeric(df["data_year"], errors="coerce")
    elif "input_year" in df.columns:
        year = pd.to_numeric(df["input_year"], errors="coerce")
    elif "system_year" in df.columns:
        year = pd.to_numeric(df["system_year"], errors="coerce")
    else:
        year = pd.Series(default_year, index=df.index, dtype="float64")

    # Fill missing and coerce to int
    year = year.fillna(default_year).astype(int)

    # Replace implausible years with default_year (keeps vectorized)
    plausible_mask = (year >= 1900) & (year <= 2100)
    year = year.where(plausible_mask, int(default_year)).astype(int)
    return year

def _enforce_loc_for_nonworkers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure that occupation 'loc' is set to -1 for non-workers in the EUROMOD input.

    We use the RURO convention:
        - if 'lma' exists and contains any 1: workers are (lma == 1) AND (lhw > 0)
        - otherwise:       workers are (les == 3) AND (lhw > 0)

    Produces:
      - loc_raw : original loc copied for traceability (if not present)
      - loc_ruro : cleaned loc where nonworkers == -1, unknown worker == -2, stored as int16
    """
    if "loc" not in df.columns:
        # Nothing to do if occupation is not available
        return df

    df = df.copy()

    # Preserve raw ISCO for traceability
    if "loc_raw" not in df.columns:
        df["loc_raw"] = df["loc"]

    loc = pd.to_numeric(df["loc"], errors="coerce")
    les = pd.to_numeric(df["les"], errors="coerce")
    lhw = pd.to_numeric(df["lhw"], errors="coerce").fillna(0.0)

    # Reuse centralized worker computation to avoid drift
    is_worker = _compute_is_worker(df)

    # RURO convention:
    #  - nonworker -> -1
    #  - worker with missing/invalid ISCO -> -2 (keeps them distinct from nonworkers)
    loc_ruro = loc.copy().fillna(-2)
    loc_ruro.loc[~is_worker] = -1
    df["loc_ruro"] = loc_ruro.astype(np.int16)

    return df


def _collapse_loc_to_loc4(
    df: pd.DataFrame,
    *,
    loc_col: str = "loc_ruro",
    out_col: str = "loc4",
    elementary_as_nonroutine_manual: bool = False,
) -> pd.DataFrame:
    """
    Collapse ISCO 1-digit occupation into 4 task groups:
        1 = routine_manual
        2 = nonroutine_manual
        3 = routine_cognitive
        4 = nonroutine_cognitive
       -1 = nonworker (lhw == 0, by RURO convention)
       -2 = unknown worker occupation (worker but missing/invalid ISCO)

    This is a pragmatic 1-digit mapping; treat as a modelling choice.
    """
    if loc_col not in df.columns:
        return df

    df = df.copy()
    loc = pd.to_numeric(df[loc_col], errors="coerce").fillna(-2).astype(int)

    # Start all as unknown (-2)
    loc4 = pd.Series(-2, index=df.index, dtype="int16")

    # Nonworkers -> -1
    loc4.loc[loc == -1] = -1

    # ISCO major groups (1..9) mapping (ISCO-08)
    # 1 Managers, 2 Professionals, 3 Technicians -> nonroutine_cognitive (4)
    loc4.loc[loc.isin([1, 2, 3])] = 4
    # 4 Clerical -> routine_cognitive (3)
    loc4.loc[loc == 4] = 3
    # 5 Service/Sales -> nonroutine_manual (2)
    loc4.loc[loc == 5] = 2
    # 6-8 -> routine_manual (1)
    loc4.loc[loc.isin([6, 7, 8])] = 1
    # 9 Elementary -> default routine_manual (1) or optionally nonroutine_manual (2)
    if elementary_as_nonroutine_manual:
        loc4.loc[loc == 9] = 2
    else:
        loc4.loc[loc == 9] = 1

    # Optional: track armed forces separately (ISCO major group 0) without forcing into loc4
    if (loc == 0).any():
        df["loc_armed"] = (loc == 0).astype(np.int8)
        # leave loc4 as -2 for loc==0 so it remains explicit unknown for task groups

    df[out_col] = loc4.astype(np.int16)
    return df


def _add_france_nuts1_region_dummies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add French NUTS 1 region dummies from drgn1 (or derive from drgn2/db040).

    France has 10 NUTS 1 regions:
        1 = Île-de-France (FR10)
        2 = Champagne-Ardenne, Picardie, Haute-Normandie, Centre, Basse-Normandie, Bourgogne
            (FR21-FR26) → Basin Parisien
        3 = Nord-Pas-de-Calais (FR30)
        4 = Lorraine, Alsace, Franche-Comté (FR41-FR43) → Est
        5 = Pays de la Loire, Bretagne, Poitou-Charentes (FR51-FR53) → Ouest
        6 = Aquitaine, Midi-Pyrénées, Limousin (FR61-FR63) → Sud-Ouest
        7 = Rhône-Alpes, Auvergne (FR71-FR72)
        8 = Languedoc-Roussillon, Provence-Alpes-Côte d'Azur, Corse (FR81-FR83) → Méditerranée
        9 = DOM (FR91-FR94: Guadeloupe, Martinique, Guyane, Réunion)
        10 = Extra-regio / unknown (FRZZ)

    Creates dummies: reg_nuts1_1, reg_nuts1_2, ..., reg_nuts1_10
    Also creates drgn1 if only drgn2 is present.

    Mapping from drgn2 to drgn1 (per the Stata do file):
        drgn1 = 1  if drgn2 == 1
        drgn1 = 2  if drgn2 in [2,3,4,5,6,7]
        drgn1 = 3  if drgn2 == 8
        drgn1 = 4  if drgn2 in [9,10,11]
        drgn1 = 5  if drgn2 in [12,13,14]
        drgn1 = 6  if drgn2 in [15,16,17]
        drgn1 = 7  if drgn2 in [18,19]
        drgn1 = 8  if drgn2 in [20,21,22]
        drgn1 = 9  if drgn2 in [23,24,25,26]
        drgn1 = 10 if drgn2 == 27
    """
    df = df.copy()

    # If drgn1 is not present, try to derive from drgn2
    if "drgn1" not in df.columns:
        if "drgn2" in df.columns:
            drgn2 = pd.to_numeric(df["drgn2"], errors="coerce")

            # Mapping from drgn2 to drgn1
            drgn2_to_drgn1 = {
                1: 1,
                2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2,
                8: 3,
                9: 4, 10: 4, 11: 4,
                12: 5, 13: 5, 14: 5,
                15: 6, 16: 6, 17: 6,
                18: 7, 19: 7,
                20: 8, 21: 8, 22: 8,
                                23: 9, 24: 9, 25: 9, 26: 9,
                27: 10,
            }
            mapped_drgn1 = drgn2.map(drgn2_to_drgn1)
            if mapped_drgn1.isna().any():
                unmapped = sorted(drgn2.loc[mapped_drgn1.isna()].dropna().unique())
                logging.warning(
                    "RURO_prep: drgn2 contained values with no NUTS1 mapping; leaving drgn1 as NaN. "
                    f"Unmapped drgn2 values: {unmapped}"
                )
            df["drgn1"] = mapped_drgn1.astype("Int64")
        else:
            # No region info available, skip
            return df

    # Now create dummies from drgn1
    drgn1 = pd.to_numeric(df["drgn1"], errors="coerce")
    # Treat missing as "unknown/extra-regio" (10) so it is explicitly represented
    drgn1 = drgn1.fillna(10)
    # CRITICAL: Write back to dataframe so downstream merges see the filled value
    df["drgn1"] = drgn1.astype(np.int16)

    # Validate drgn1 values are in expected range (protects against DRD mapping changes)
    valid_regions = set(range(1, 11))
    observed_regions = set(np.unique(drgn1.dropna()))
    if not observed_regions <= valid_regions:
        raise ValueError(
            f"drgn1 takes values outside 1..10: {observed_regions - valid_regions}. "
            "Check DRD mapping for France."
        )

    # France NUTS 1 region names (for documentation purposes only)
    _nuts1_names = {
        1: "Île-de-France",
        2: "Bassin Parisien",
        3: "Nord-Est",
        4: "Nord-Ouest",
        5: "Sud-Est",
     }

    # Create dummies for each region (1-10).
    # NB: In the RURO estimation, reg_nuts1_1 (Île-de-France) will be
    # omitted as the baseline region.
    # KEEP ALL DUMMIES HERE: do not drop the baseline in the prep step.
    # The estimator should explicitly omit `reg_nuts1_1` (Île-de-France) when
    # building the model. This preserves information in the dataset and avoids
    # accidental silent drops of columns during preprocessing.
    for reg_num in range(1, 11):
        col_name = f"reg_nuts1_{reg_num}"
        if col_name not in df.columns:
            df[col_name] = (drgn1 == reg_num).astype(int)

    return df


def _add_ruro_variables_basic(
    df: pd.DataFrame,
    *,
    default_year: int = DEFAULT_YEAR,
) -> pd.DataFrame:
    """
    Add only the RURO variables that are not already in data_prep2 outputs:

        - ruro_group is set outside this function (singles vs couples).
        - ruro_sample: 1{ruro_decider == 1 AND dag >= 18} (estimation sample flag)
        - wage_ruro, is_worker
        - working, working_pt1, working_pt2, working_ft (focal bands)
        - pexp_years, pexp_years2, pexp (Stijn-style, education-dependent)
        - educL, educH (education dummies)
        - yd1, yd2, yd3
        - reg_nuts1_1 ... reg_nuts1_10: French NUTS 1 region dummies
        - (optionally) hours, wage as aliases for lhw and wage_ruro

    Assumes df has at least:
        'dag', 'deh', 'lhw', 'les', 'idperson', 'idhh', 'ruro_decider',
    and ideally 'lma' (labour market attachment), 'drgn1' or 'drgn2' (region),
    plus a year variable (input_year/system_year/yds).

    **Crucially**: never overwrites columns that already exist.
    
    Note on ruro_sample:
        - ruro_decider = 1 for household head and partner (defined upstream in
          france_data_prep.py); = 0 for children and other household members.
        - ruro_sample = 1 for adult deciders (dag >= 18) who enter RURO estimation.
        - All household members are kept in the data for EUROMOD tax-benefit
          calculations, but downstream RURO estimation scripts should filter
          on ruro_sample == 1.
    """
    df = df.copy()

    # ---------------------------
    # 0. RURO estimation sample (deciders only, adults)
    # ---------------------------    
    # # If ruro_decider is missing but hh_IsHead/hh_IsPartner exist, construct it
    if "ruro_decider" not in df.columns:
        if "hh_IsHead" in df.columns:
            hh_is_head = pd.to_numeric(df["hh_IsHead"], errors="coerce").fillna(0).astype(int)
            hh_is_partner = pd.Series(0, index=df.index)
            if "hh_IsPartner" in df.columns:
                hh_is_partner = pd.to_numeric(df["hh_IsPartner"], errors="coerce").fillna(0).astype(int)
            df["ruro_decider"] = ((hh_is_head == 1) | (hh_is_partner == 1)).astype(int)
        else:
            raise KeyError(
                "RURO_prep expected 'ruro_decider' (or 'hh_IsHead'/'hh_IsPartner') in the filtered data. "
                "It should be 1 for household head/partner and 0 for all "
                "other members, defined upstream in france_data_prep.py."
            )

    ruro_decider = pd.to_numeric(df["ruro_decider"], errors="coerce").fillna(0).astype(int)
    dag_local = pd.to_numeric(df["dag"], errors="coerce")

    # Adults only (standard threshold: dag >= 18)
    is_adult = dag_local >= 18

    ruro_sample = (ruro_decider == 1) & is_adult
    _maybe_add_column(df, "ruro_sample", ruro_sample.astype(int))

    # ---------------------------
    # 0b. RURO labour market attachment (active population)
    # ---------------------------
    # NOTE: LES filtering (allowed_les = [3, 5, 7]) is already enforced at household-level
    # in enh_france_data_prep.py. Households where ANY decider (head/partner) has les NOT in [3,5,7]
    # are dropped entirely. Therefore, all remaining deciders MUST have les in [3,5,7].
    # The redundant ruro_lma flag has been removed from this pipeline.

    # Diagnostic breakdown by les value (for logging purposes only)
    if "les" in df.columns and logging.getLogger().isEnabledFor(logging.DEBUG):
        les_counts = df.groupby(pd.to_numeric(df["les"], errors="coerce")).size()
        logging.debug(f"les distribution: {les_counts.to_dict()}")

    # From here on, we compute all RURO variables for everyone.
    # The estimation sample restriction to deciders happens in enh_RURO_prep_mnl_basic.py.

    # ---------------------------
    # 1. Year variable and dummies
    # ---------------------------
    year = _infer_year_series(df, default_year)
    _maybe_add_column(df, "year_for_ruro", year)

    # Sanity check / lightweight guard to avoid re-introducing yds-like bugs:
    yvals = pd.to_numeric(df["year_for_ruro"], errors="coerce")
    y_min = int(yvals.min())
    y_max = int(yvals.max())
    logging.info("year_for_ruro: nunique=%d min=%d max=%d", int(yvals.nunique()), y_min, y_max)
    if y_min < 1900 or y_max > 2100:
        logging.error(
            "Inferred year_for_ruro contains implausible values (min=%s max=%s). Aborting.", y_min, y_max
        )
        raise ValueError("Inferred year_for_ruro contains implausible values. Check upstream year stamping.")

    uniq_years = np.sort(pd.to_numeric(year, errors="coerce").unique())
    # Robust year-dummy construction:
    # - if single year: yd1=1, yd2=0, yd3=0
    # - if two years: yd1=min, yd2=max, yd3=0
    # - if 3+ years: take first three distinct years
    if len(uniq_years) >= 1:
        yd1_year = int(uniq_years[0])
    else:
        yd1_year = int(default_year)

    yd2_year = int(uniq_years[1]) if len(uniq_years) >= 2 else None
    yd3_year = int(uniq_years[2]) if len(uniq_years) >= 3 else None

    yd1 = (year == yd1_year).astype(np.int8)
    if yd2_year is not None:
        yd2 = (year == yd2_year).astype(np.int8)
    else:
        yd2 = pd.Series(0, index=df.index, dtype=np.int8)
    if yd3_year is not None:
        yd3 = (year == yd3_year).astype(np.int8)
    else:
        yd3 = pd.Series(0, index=df.index, dtype=np.int8)

    _maybe_add_column(df, "yd1", yd1)
    _maybe_add_column(df, "yd2", yd2)
    _maybe_add_column(df, "yd3", yd3)

    # ---------------------------
    # 2. Potential experience (dew/dey-based, data-driven) with safety guards
    # ---------------------------
    dag = pd.to_numeric(df["dag"], errors="coerce")
    year_series = pd.to_numeric(df["year_for_ruro"], errors="coerce")

    # dew = year of attaining highest degree (if available)
    if "dew" in df.columns:
        dew_num = pd.to_numeric(df["dew"], errors="coerce")
    else:
        dew_num = None

    # Primary: year_for_ruro - dew, but only when dew is plausibly a calendar year
    pexp_from_dew = pd.Series(np.nan, index=df.index)
    if dew_num is not None:
        dew_valid = (
            dew_num.notna()
            & (dew_num != -1)
            & (dew_num >= 1900)
            & (dew_num <= 2100)
            & (dew_num <= year_series)
        )
        pexp_from_dew = (year_series - dew_num).where(dew_valid, np.nan)

    # Secondary: liwwh (months of work history) -> years
    pexp_from_liwwh = pd.Series(np.nan, index=df.index)
    if "liwwh" in df.columns:
        liwwh = pd.to_numeric(df["liwwh"], errors="coerce")
        pexp_from_liwwh = (liwwh / 12.0).where(liwwh.notna() & (liwwh > 0), np.nan)

    # Fallback: dag - 6 - dey (years in education)
    pexp_from_dey = pd.Series(np.nan, index=df.index)
    if "dey" in df.columns:
        dey_num = pd.to_numeric(df["dey"], errors="coerce")
        dey_valid = dey_num.notna() & (dey_num >= 0) & (dey_num <= 100)
        pexp_from_dey = (dag - 6.0 - dey_num).where(dey_valid, np.nan)

    # Combine priority: liwwh -> dew -> dey
    pexp_raw = pexp_from_liwwh.where(pexp_from_liwwh.notna(), pexp_from_dew)
    pexp_raw = pexp_raw.where(pexp_raw.notna(), pexp_from_dey)

    # Final safeguards: non-negative, cap by age-consistency (dag - 15), fill NaNs with 0
    cap_by_age = (dag - 15.0).clip(lower=0.0)
    pexp_years = pexp_raw.fillna(0.0).clip(lower=0.0)
    # enforce elementwise cap
    pexp_years = pd.Series(np.minimum(pexp_years.fillna(0.0), cap_by_age.fillna(0.0)), index=df.index).astype(
        float
    )
    pexp_years = pexp_years.fillna(0.0)
    pexp_years2 = (pexp_years ** 2).astype(float)

    _maybe_add_column(df, "pexp_years", pexp_years)
    _maybe_add_column(df, "pexp_years2", pexp_years2)

    # scaling: hundreds of years
    if "pexp" not in df.columns:
        df["pexp"] = (pexp_years / 100.0).astype(float)

    # ---------------------------
    # 2b. Education dummies (low vs high, middle is baseline)
    # ---------------------------
    # Compatibility: accept either 'deh' or 'dehde' as the education code.
    # If only 'dehde' is present (as produced by the France prep), create 'deh' as an alias.
    if "deh" not in df.columns:
        if "dehde" in df.columns:
            df["deh"] = pd.to_numeric(df["dehde"], errors="coerce")
        else:
            raise KeyError(
                "RURO_prep expected 'deh' (education code) or 'dehde' (highest education) "
                "in the filtered data for France."
            )
    deh = pd.to_numeric(df["deh"], errors="coerce")

    educL = deh.isin([0, 1, 2]).astype(int)
    educH = deh.eq(5).astype(int)

    _maybe_add_column(df, "educL", educL)
    _maybe_add_column(df, "educH", educH)

    # ---------------------------
    # 3. Unified wage and working indicators
    # ---------------------------
    # Choose source for wage: prefer 'wage_final', then 'w_emp_strict', then 'yivwg'
    wage_source = None
    for cand in ["wage_final", "w_emp_strict", "yivwg"]:
        if cand in df.columns:
            wage_source = cand
            break
    if wage_source is None:
        raise KeyError(
            "No wage variable found for RURO. Expected one of "
            "'wage_final', 'w_emp_strict', or 'yivwg'."
        )

    _lhw = cast(pd.Series, pd.to_numeric(df["lhw"], errors="coerce")).fillna(0.0)
    _les = cast(pd.Series, pd.to_numeric(df["les"], errors="coerce"))
    # Centralized worker logic (FR-safe)
    is_worker_bool = _compute_is_worker(df)
    _maybe_add_column(df, "is_worker", is_worker_bool.astype(np.int8))

    # Base hourly wage measure (raw, regardless of worker state)
    wage_numeric = cast(pd.Series, pd.to_numeric(df[wage_source], errors="coerce")).fillna(0.0).astype(float)
    _maybe_add_column(df, "wage_for_draws", wage_numeric)

    # Wage in the RURO observed-state definition (0 for non-workers)
    wage_ruro = np.where(is_worker_bool.to_numpy(), wage_numeric.to_numpy(), 0.0).astype(float)
    _maybe_add_column(df, "wage_ruro", wage_ruro)
    _maybe_add_column(df, "hours", _lhw)
    _maybe_add_column(df, "wage", wage_ruro)
    # Working and part-time dummies: narrow bands around focal hours (Stijn-style)
    # working = 1{lhw > 0}
    # working_pt1 = 1{18.5 ≤ lhw ≤ 20.5} (≈ 20 hours)
    # working_pt2 = 1{29.5 ≤ lhw ≤ 30.5} (≈ 30 hours)
    # working_ft  = 1{37.5 ≤ lhw ≤ 40.5} (≈ full-time range)
    working = (_lhw > 0.0).astype(int)
    working_pt1 = ((_lhw >= 18.5) & (_lhw <= 20.5)).astype(int)
    working_pt2 = ((_lhw >= 29.5) & (_lhw <= 30.5)).astype(int)
    working_ft = ((_lhw >= 37.5) & (_lhw <= 40.5)).astype(int)

    _maybe_add_column(df, "working", working)
    _maybe_add_column(df, "working_pt1", working_pt1)
    _maybe_add_column(df, "working_pt2", working_pt2)
    _maybe_add_column(df, "working_ft", working_ft)
    # ------------------------------------------------------------------
    # DIAGNOSTIC A: observed-state coherence for estimation-sample deciders
    # ------------------------------------------------------------------
    # For adult deciders in the estimation sample: if they work, they must have positive wage_for_draws
    bad = (
        (pd.to_numeric(df["ruro_sample"], errors="coerce").fillna(0).astype(int) == 1)
        & (pd.to_numeric(df["is_worker"], errors="coerce").fillna(0).astype(int) == 1)
        & (pd.to_numeric(df["wage_for_draws"], errors="coerce").fillna(0.0) <= 0.0)
    )
    if bad.any():
        cols = [c for c in ["idperson", "idhh", "dag", "lhw", "les", "lma", "wage_for_draws", "wage_ruro"] if c in df.columns]
        logging.warning(
            "RURO_prep: Found %d ruro_sample deciders with is_worker ==1 but non-positive wage_for_draws. Example rows:\n%s",
            int(bad.sum()),
            df.loc[bad, cols].head(10).to_string(index=False),
        )

    # ------------------------------------------------------------------
    # 3b. NEW: decider-state + joint-household hygiene flags (for RURO joint estimation)
    # ------------------------------------------------------------------
    # Decider rows only: "invalid observed state" = works positive hours but NOT classified as worker.
    # In your current pipeline this typically implies wage_ruro==0 and will break the wage/hour likelihood logic.
    invalid_decider_state = (
        (pd.to_numeric(df["ruro_sample"], errors="coerce").fillna(0).astype(int) == 1)
        & (pd.to_numeric(df["working"], errors="coerce").fillna(0).astype(int) == 1)
        & (pd.to_numeric(df["is_worker"], errors="coerce").fillna(0).astype(int) == 0)
    )
    _maybe_add_column(df, "ruro_invalid_decider_state", invalid_decider_state.astype(np.int8))
    invalid_worker_no_hours = (
        (df["ruro_sample"] == 1)
        & (df["is_worker"] == 1)
        & (df["working"] == 0)
    )
    _maybe_add_column(df, "ruro_invalid_worker_no_hours", invalid_worker_no_hours.astype(np.int8))


    # A decider is "valid for RURO estimation" if:
    # - either non-working, or
    # - working and classified as worker (so we have a coherent wage/hours state)
    valid_decider_state = (
        (pd.to_numeric(df["ruro_sample"], errors="coerce").fillna(0).astype(int) == 1)
        & (~invalid_decider_state)
    )
    _maybe_add_column(df, "ruro_valid_decider_state", valid_decider_state.astype(np.int8))

    # Household-level: number of adult deciders in the RURO sample (as currently defined)
    hh_n_deciders = (
        df.groupby("idhh")["ruro_sample"].transform("sum").fillna(0).astype(np.int16)
    )
    _maybe_add_column(df, "hh_n_ruro_deciders", hh_n_deciders.astype(np.int16))

    # Household-level: any invalid decider state inside hh (max over rows is enough because invalid flag is 0/1)
    hh_any_invalid = (
        df.groupby("idhh")["ruro_invalid_decider_state"].transform("max").fillna(0).astype(np.int8)
    )
    _maybe_add_column(df, "hh_any_invalid_decider_state", hh_any_invalid.astype(np.int8))

    # Household-level: "joint-couple OK" = exactly 2 deciders AND no invalid decider state
    hh_joint_ok = (hh_n_deciders == 2) & (hh_any_invalid == 0)
    _maybe_add_column(df, "hh_joint_ok", hh_joint_ok.astype(np.int8))


    # --- Enforce RURO convention on occupation: loc = -1 for non-workers ---
    df = _enforce_loc_for_nonworkers(df)
    # Collapse ISCO-1digit -> 4 task groups (loc4) for estimation-ready covariate
    df = _collapse_loc_to_loc4(df, loc_col="loc_ruro", out_col="loc4")

    # --- Add French NUTS 1 region dummies ---
    df = _add_france_nuts1_region_dummies(df)

    # ------------------------------------------------------------------
    # Compact storage: cast common dummy columns to small integer dtypes
    # This reduces parquet size and speeds up subsequent I/O/replication.
    # ------------------------------------------------------------------
    int8_cols = [
        "educL", "educH", "working", "working_pt1", "working_pt2", "working_ft",
        "yd1", "yd2", "yd3", "is_worker", "ruro_sample",
        "ruro_invalid_decider_state", "ruro_valid_decider_state",
        "hh_any_invalid_decider_state", "ruro_invalid_worker_no_hours","hh_joint_ok",
    ]

    # Add region dummies reg_nuts1_1 .. reg_nuts1_10
    int8_cols += [f"reg_nuts1_{i}" for i in range(1, 11)]

    for col in int8_cols:
        if col in df.columns:
            # Only cast when column is not already an integer dtype to avoid
            # silently overwriting user-provided integer types.
            try:
                if not ptypes.is_integer_dtype(df[col].dtype):
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(np.int8)
            except Exception:
                logging.debug("Could not cast column %s to int8; leaving as-is.", col)

    return df

def _prepare_ruro_basic(
    processed_dir: Path,
    *,
    base_year: int = DEFAULT_YEAR,
    export_format: str = DEFAULT_EXPORT_FORMAT,
    log_level: str = "INFO",
) -> Dict[str, Any]:
    """
    High-level driver with enhanced column-group metadata tracking:

      1. Load singles and couples filtered datasets from processed_dir.
      2. Load column-group metadata (A/B/C cols) from input sidecar if present.
      3. Ensure true IDs (idperson_true, idhh_true) and decider flags.
      4. Create baseline labor-input references (lhw_base, yivwg_base, etc.).
      5. Tag ruro_group (singles vs couples).
      6. Add basic RURO variables via _add_ruro_variables_basic.
      7. Validate decider counts (singles=1, couples=2 per household).
      8. Export RURO-ready datasets with column-group sidecar JSONs.

    This function does NOT touch disposable income, equivalence scales,
    or CPI uprating. It DOES construct education dummies and NUTS1 region
    dummies needed for RURO estimation.
    """
    setup_logging(log_level)
    processed_dir = ensure_dir(processed_dir)

    # =========================================================================
    # 1. Load input data
    # =========================================================================
    singles, couples = _load_filtered_data(processed_dir, base_year=base_year, export_format=export_format)

    # =========================================================================
    # 2. Load column-group metadata from input sidecar (if exists)
    # =========================================================================
    colgroups_meta = _load_colgroups_metadata(processed_dir, base_year, export_format)
    inherited_A_cols = set(colgroups_meta["A_cols"])
    inherited_B_cols = set(colgroups_meta["B_cols"])
    inherited_C_cols = set(colgroups_meta["C_cols"])
    inherited_metadata = colgroups_meta["metadata"]

    # Track initial columns (before RURO prep adds anything)
    initial_singles_cols = set(singles.columns)
    initial_couples_cols = set(couples.columns)

    # If no sidecar was found, treat initial columns as A_cols
    if not inherited_A_cols:
        inherited_A_cols = initial_singles_cols | initial_couples_cols
        logging.info("No inherited A_cols; using initial columns as A_cols")

    # =========================================================================
    # 3. Ensure true IDs and standardize decider flags
    # =========================================================================
    singles = _ensure_true_ids_and_deciders(singles)
    couples = _ensure_true_ids_and_deciders(couples)

    # =========================================================================
    # 4. Create baseline labor-input references (Goal 5)
    # =========================================================================
    singles, singles_baseline_cols = _ensure_baseline_labor_references(singles)
    couples, couples_baseline_cols = _ensure_baseline_labor_references(couples)

    # =========================================================================
    # 5. Tag ruro_group and add RURO variables
    # =========================================================================
    # ruro_group: group code for later estimation
    # Deterministic label: intentionally overwrite/define ruro_group here.
    singles["ruro_group"] = np.int16(1)    # singles
    couples["ruro_group"] = np.int16(10)   # couples

    singles_ruro = _add_ruro_variables_basic(singles, default_year=base_year)
    _log_ruro_summary(singles_ruro, "singles")

    couples_ruro = _add_ruro_variables_basic(couples, default_year=base_year)
    _log_ruro_summary(couples_ruro, "couples")

    # =========================================================================
    # 6. Validate decider counts (Goal 4)
    # =========================================================================
    _validate_decider_counts(singles_ruro, expected_count=1, household_type="singles")
    _validate_decider_counts(couples_ruro, expected_count=2, household_type="couples")

    # =========================================================================
    # 7. Compute column groups for output sidecar
    # =========================================================================
    # New columns created by this script
    new_singles_cols = set(singles_ruro.columns) - initial_singles_cols
    new_couples_cols = set(couples_ruro.columns) - initial_couples_cols
    new_cols_combined = new_singles_cols | new_couples_cols

    # Final A/B/C for output sidecar
    # A_cols: inherited from input
    # B_cols: inherited B + new cols created here (including baseline refs)
    # C_cols: inherited from input (unchanged by RURO prep)
    final_A_cols = list(inherited_A_cols)
    final_B_cols = list(inherited_B_cols | new_cols_combined)
    final_C_cols = list(inherited_C_cols)

    # Force-input columns hint (Goal 6): labor inputs that will be overwritten in draws
    force_input_candidates = ["lhw", "yivwg", "yem00", "yemxp", "yem"]
    force_input_cols_singles = [c for c in force_input_candidates if c in singles_ruro.columns]
    force_input_cols_couples = [c for c in force_input_candidates if c in couples_ruro.columns]

    # =========================================================================
    # 8. Export RURO-ready datasets with sidecar JSONs
    # =========================================================================
    out_singles = processed_dir / f"singles_RURO_ready.{export_format}"
    out_couples = processed_dir / f"couples_RURO_ready.{export_format}"

    if export_format == "parquet":
        singles_ruro.to_parquet(out_singles, index=False)  # type: ignore[arg-type]
        couples_ruro.to_parquet(out_couples, index=False)  # type: ignore[arg-type]
    else:
        singles_ruro.to_csv(out_singles, index=False)
        couples_ruro.to_csv(out_couples, index=False)

    # Write column-group sidecar for singles
    _write_colgroups_sidecar(
        output_path=out_singles,
        A_cols=final_A_cols,
        B_cols=final_B_cols,
        C_cols=final_C_cols,
        force_input_cols_hint=force_input_cols_singles,
        metadata={
            **inherited_metadata,
            "household_type": "singles",
            "base_year": base_year,
            "new_cols_created": sorted(new_singles_cols),
        },
    )

    # Write column-group sidecar for couples
    _write_colgroups_sidecar(
        output_path=out_couples,
        A_cols=final_A_cols,
        B_cols=final_B_cols,
        C_cols=final_C_cols,
        force_input_cols_hint=force_input_cols_couples,
        metadata={
            **inherited_metadata,
            "household_type": "couples",
            "base_year": base_year,
            "new_cols_created": sorted(new_couples_cols),
        },
    )

    # =========================================================================
    # 9. Runtime sanity checks (catch structural issues before downstream stages)
    # =========================================================================
    logging.info("Running runtime sanity checks on RURO_prep outputs...")

    # Prepare metadata for sanity checks
    singles_ids = set(singles_ruro["idhh"].unique())
    couples_ids = set(couples_ruro["idhh"].unique())

    sanity_metadata = {
        "household_types": {
            "singles": singles_ids,
            "couples": couples_ids,
        }
    }

    # Run sanity checks for both household types
    try:
        sanity_report_ruro_prep(singles_ruro, metadata=sanity_metadata)
        logging.info("✓ Singles dataset passed all sanity checks")
    except Exception as e:
        logging.error(f"Singles dataset FAILED sanity checks: {e}")
        raise

    try:
        sanity_report_ruro_prep(couples_ruro, metadata=sanity_metadata)
        logging.info("✓ Couples dataset passed all sanity checks")
    except Exception as e:
        logging.error(f"Couples dataset FAILED sanity checks: {e}")
        raise

    logging.info("All RURO_prep sanity checks passed ✓\n")

    meta: Dict[str, Any] = {
        "processed_dir": str(processed_dir),
        "base_year": int(base_year),
        "export_format": export_format,
        "singles_rows": int(singles_ruro.shape[0]),
        "couples_rows": int(couples_ruro.shape[0]),
        "singles_file": str(out_singles),
        "couples_file": str(out_couples),
        "singles_sidecar": str(out_singles.parent / f"{out_singles.stem}__colgroups.json"),
        "couples_sidecar": str(out_couples.parent / f"{out_couples.stem}__colgroups.json"),
    }
    return meta


def _cli_ruro_prep_basic() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Construct RURO-style explanatory variables on top of "
            "data_prep2 outputs (no equivalence scales, no CPI)."
        )
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=None,        help=(
            "Directory where data_prep2 wrote couples_filtering_final.* and "
            "singles_filtering_final.*. "
            "If omitted, defaults to data_root()/processed/fr/2021."
        ),
    )
    parser.add_argument(
        "--base-year",
        type=int,
        default=DEFAULT_YEAR,
        help="Reference year used when inferring years (only used as fallback).",
    )
    parser.add_argument(
        "--export-format",
        type=str,
        default=DEFAULT_EXPORT_FORMAT,
        choices=["parquet", "csv"],
        help="Output format for RURO-ready datasets.",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level for the script.",    )
    args = parser.parse_args()

    processed_dir = _resolve_processed_dir(args.processed_dir, args.base_year, args.export_format)

    meta = _prepare_ruro_basic(
        processed_dir=processed_dir,
        base_year=args.base_year,
        export_format=args.export_format,
        log_level=args.log_level,
    )
    print("RURO preparation (basic) completed:")
    for k, v in meta.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    _cli_ruro_prep_basic()

    # Example diagnostic (to run in a notebook, not here):
    # df = pd.read_parquet("path/to/singles_RURO_ready.parquet")
    # df["check_dew"] = df["pexp_years"] - (df["year_for_ruro"] - df["dew"])
    # print(df.loc[df["dew"].notna(), "check_dew"].value_counts().head())
    # df["check_dey"] = df["pexp_years"] - (df["dag"] - 6 - df["dey"])
    # print(df.loc[df["dew"].isna() & df["dey"].notna(), "check_dey"].value_counts().head())
