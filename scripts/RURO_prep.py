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
    - is_worker: 1{lma==1 & lhw>0} if lma exists, else 1{les==3 & lhw>0}
    - working: 1{lhw>0}
    - working_pt1: 1{18.5 <= lhw <= 20.5} (focal ~20 hours)
    - working_pt2: 1{29.5 <= lhw <= 30.5} (focal ~30 hours)
    - working_ft: 1{37.5 <= lhw <= 40.5} (focal full-time)
    - pexp_years: potential experience in years (education-dependent start age)
    - pexp_years2: squared potential experience
    - pexp: potential experience / 100 (Stijn-style, in "hundreds of years")
    - educL: 1{deh in {0,1,2}} (low education dummy)
    - educH: 1{deh == 5} (high education dummy)
    - yd1, yd2, yd3: year dummies based on input_year/system_year/yds
    - reg_nuts1_1 ... reg_nuts1_10: France NUTS 1 region dummies (from drgn1)
      (Île-de-France = reg_nuts1_1 is intended as the baseline at estimation)

This script deliberately does NOT:
    - compute equivalised income or CPI-uprated income;
    - touch your disposable-income variables.

Those can be handled separately for presentation/robustness checks.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Tuple, cast

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Bootstrap paths (same style as data_prep2.py)
# ---------------------------------------------------------------------------
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:  # interactive environments
    SCRIPT_DIR = Path.cwd() / "scripts"
PROJECT_ROOT = (SCRIPT_DIR / "..").resolve()

# Make sure SCRIPT_DIR and PROJECT_ROOT are on sys.path (for path_helpers, scratch, etc.)
for candidate in (SCRIPT_DIR, PROJECT_ROOT):
    c_str = str(candidate)
    if c_str not in sys.path:
        sys.path.insert(0, c_str)


from path_helpers import data_root, ensure_dir, resolve_storage_root  # type: ignore

# Add scratch/ to the path so we can import setup_logging like in data_prep2.py
SCRATCH_DIR = PROJECT_ROOT / "scratch"
if SCRATCH_DIR.exists():
    sys.path.insert(0, str(SCRATCH_DIR))

try:
    from scratch.my_functions import setup_logging  # type: ignore
except Exception:
    import logging

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
    if name not in df.columns:
        df[name] = values


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
    # Fallback to repo-local data_root
    candidates.append(data_root().parent)

    chosen: Path | None = None
    for root in candidates:
        data_dir = root / "Data"
        options: list[Path] = []
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

    Priority (as documented):
        1. 'input_year' if present (from prepare_one_year)
        2. 'system_year' if present
        3. 'yds' if present (original EU-SILC income year)
        4. fallback: default_year (scalar)
    """
    if "input_year" in df.columns:
        year = cast(pd.Series, pd.to_numeric(df["input_year"], errors="coerce"))
    elif "system_year" in df.columns:
        year = cast(pd.Series, pd.to_numeric(df["system_year"], errors="coerce"))
    elif "yds" in df.columns:
        year = cast(pd.Series, pd.to_numeric(df["yds"], errors="coerce"))
    else:
        year = pd.Series(default_year, index=df.index, dtype="float64")

    year = cast(pd.Series, year).fillna(default_year).astype(int)
    return year

def _enforce_loc_for_nonworkers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure that occupation 'loc' is set to -1 for non-workers in the EUROMOD input.

    We use the RURO convention:
        - if 'lma' exists: workers are (lma == 1) AND (lhw > 0)
        - otherwise:       workers are (les == 3) AND (lhw > 0)

    This assumes that 'loc' has already been constructed upstream
    (from SILC / occupation codes) in the EUROMOD input data.
    """
    if "loc" not in df.columns:
        # Nothing to do if occupation is not available
        return df

    df = df.copy()

    loc = pd.to_numeric(df["loc"], errors="coerce")
    les = pd.to_numeric(df["les"], errors="coerce")
    lhw = pd.to_numeric(df["lhw"], errors="coerce").fillna(0.0)

    lma = None
    if "lma" in df.columns:
        lma = pd.to_numeric(df["lma"], errors="coerce")

    if lma is not None:
        is_worker = (lma == 1) & (lhw > 0.0)
    else:
        is_worker = les.eq(3) & (lhw > 0.0)

    nonworker_mask = ~is_worker
    loc.loc[nonworker_mask] = -1

    if loc.notna().any():
        df["loc"] = loc.astype(int)
    else:
        df["loc"] = loc

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
                import logging

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

    # Validate drgn1 values are in expected range (protects against DRD mapping changes)
    valid_regions = set(range(1, 11))
    observed_regions = set(np.unique(drgn1.dropna()))
    if not observed_regions <= valid_regions:
        raise ValueError(
            f"drgn1 takes values outside 1..10: {observed_regions - valid_regions}. "
            "Check DRD mapping for France."
        )

    # France NUTS 1 region names (for documentation purposes only)
    nuts1_names = {
        1: "Île-de-France",
        2: "Bassin Parisien",
        3: "Nord-Pas-de-Calais",
        4: "Est",
        5: "Ouest",
        6: "Sud-Ouest",
        7: "Rhône-Alpes/Auvergne",
        8: "Méditerranée",
        9: "DOM",
        10: "Extra-regio",
    }

    # Create dummies for each region (1-10).
    # NB: In the RURO estimation, reg_nuts1_1 (Île-de-France) will be
    # omitted as the baseline region.
    for reg_num in range(1, 11):
        col_name = f"reg_nuts1_{reg_num}"
        if col_name not in df.columns:
            df[col_name] = (drgn1 == reg_num).astype(int)

    # Store drgn1 back if it was computed
    if "drgn1" not in df.columns or df["drgn1"].isna().all():
        df["drgn1"] = drgn1.astype("Int64")

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
    # ---------------------------    # If ruro_decider is missing but hh_IsHead/hh_IsPartner exist, construct it
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

    # From here on, we still compute all RURO variables for everyone,
    # but the estimation sample will later restrict to ruro_sample == 1.

    # ---------------------------
    # 1. Year variable and dummies
    # ---------------------------
    year = _infer_year_series(df, default_year)

    _maybe_add_column(df, "year_for_ruro", year)

    uniq_years = np.sort(year.unique())
    yd1_year = int(uniq_years[0]) if len(uniq_years) >= 1 else default_year
    yd2_year = int(uniq_years[1]) if len(uniq_years) >= 2 else yd1_year
    yd3_year = int(uniq_years[2]) if len(uniq_years) >= 3 else yd1_year

    yd1 = (year == yd1_year).astype(int)
    yd2 = (year == yd2_year).astype(int)
    yd3 = (year == yd3_year).astype(int)

    _maybe_add_column(df, "yd1", yd1)
    _maybe_add_column(df, "yd2", yd2)
    _maybe_add_column(df, "yd3", yd3)

    # ---------------------------
    # 2. Potential experience (dew/dey-based, data-driven)
    # ---------------------------
    # Potential experience: primary = year_for_ruro - dew (year of degree),
    # fallback = dag - 6 - dey (age minus schooling), clipped at zero.
    dag = pd.to_numeric(df["dag"], errors="coerce")

    if "deh" not in df.columns:
        raise KeyError("RURO_prep expected 'deh' (education code) in the filtered data for France.")
    deh = pd.to_numeric(df["deh"], errors="coerce")

    # Use year_for_ruro from df (may differ from `year` if column pre-existed)
    year_for_pexp = pd.to_numeric(df["year_for_ruro"], errors="coerce")

    # dew = year of attaining highest degree (if available)
    dew = None
    if "dew" in df.columns:
        dew = pd.to_numeric(df["dew"], errors="coerce")

    # dey = number of years in education (if available)
    dey = None
    if "dey" in df.columns:
        dey = pd.to_numeric(df["dey"], errors="coerce")

    # Primary potential experience: year - dew
    if dew is not None:
        pexp_from_dew = (year_for_pexp - dew).where(dew.notna(), np.nan)
    else:
        pexp_from_dew = pd.Series(np.nan, index=df.index)

    # Fallback potential experience: dag - 6 - dey
    if dey is not None:
        pexp_from_dey = (dag - 6.0 - dey).where(dey.notna(), np.nan)
    else:
        pexp_from_dey = pd.Series(np.nan, index=df.index)

    # Combine, giving priority to dew-based measure
    pexp_raw = pexp_from_dew.where(pexp_from_dew.notna(), pexp_from_dey)

    # Final safeguard: no negative potential experience
    pexp_years = pexp_raw.clip(lower=0).astype(float)
    pexp_years2 = (pexp_years ** 2).astype(float)

    _maybe_add_column(df, "pexp_years", pexp_years)
    _maybe_add_column(df, "pexp_years2", pexp_years2)

    # Stijn-style scaling: hundreds of years
    if "pexp" not in df.columns:
        df["pexp"] = (pexp_years / 100.0).astype(float)

    # ---------------------------
    # 2b. Education dummies (low vs high, middle is baseline)
    # ---------------------------
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

    lhw = cast(pd.Series, pd.to_numeric(df["lhw"], errors="coerce")).fillna(0.0)
    les = cast(pd.Series, pd.to_numeric(df["les"], errors="coerce"))

    # Worker definition: prefer 'lma' if present, fallback to les == 3
    lma = None
    if "lma" in df.columns:
        lma = cast(pd.Series, pd.to_numeric(df["lma"], errors="coerce"))

    if lma is not None:
        is_worker_bool = (lma == 1) & (lhw > 0.0)
    else:
        # Fallback: treat les == 3 (employed) with positive hours as workers
        is_worker_bool = les.eq(3) & (lhw > 0.0)

    _maybe_add_column(df, "is_worker", is_worker_bool.astype(int))

    wage_numeric = cast(pd.Series, pd.to_numeric(df[wage_source], errors="coerce")).fillna(0.0)
    wage_ruro = np.where(is_worker_bool, wage_numeric, 0.0)
    _maybe_add_column(df, "wage_ruro", wage_ruro)

    # Working and part-time dummies: narrow bands around focal hours (Stijn-style)
    # working = 1{lhw > 0}
    # working_pt1 = 1{18.5 ≤ lhw ≤ 20.5} (≈ 20 hours)
    # working_pt2 = 1{29.5 ≤ lhw ≤ 30.5} (≈ 30 hours)
    # working_ft  = 1{37.5 ≤ lhw ≤ 40.5} (≈ full-time range)
    working = (lhw > 0.0).astype(int)
    working_pt1 = ((lhw >= 18.5) & (lhw <= 20.5)).astype(int)
    working_pt2 = ((lhw >= 29.5) & (lhw <= 30.5)).astype(int)
    working_ft = ((lhw >= 37.5) & (lhw <= 40.5)).astype(int)

    _maybe_add_column(df, "working", working)
    _maybe_add_column(df, "working_pt1", working_pt1)
    _maybe_add_column(df, "working_pt2", working_pt2)
    _maybe_add_column(df, "working_ft", working_ft)

    # Aliases for 'hours' and 'wage' (Stijn's RURO likelihood uses these names)
    _maybe_add_column(df, "hours", lhw)
    _maybe_add_column(df, "wage", wage_ruro)

    # --- Enforce RURO convention on occupation: loc = -1 for non-workers ---
    df = _enforce_loc_for_nonworkers(df)

    # --- Add French NUTS 1 region dummies ---
    df = _add_france_nuts1_region_dummies(df)

    return df

def _prepare_ruro_basic(
    processed_dir: Path,
    *,
    base_year: int = DEFAULT_YEAR,
    export_format: str = DEFAULT_EXPORT_FORMAT,
    log_level: str = "INFO",
) -> Dict[str, Any]:
    """
    High-level driver:

      1. Load singles and couples filtered datasets from processed_dir.
      2. Tag ruro_group (singles vs couples).
      3. Add basic RURO variables via _add_ruro_variables_basic, including:
         - education dummies (educL, educH)
         - French NUTS 1 region dummies (reg_nuts1_1 ... reg_nuts1_10)
      4. Export RURO-ready datasets.

    This function does NOT touch disposable income, equivalence scales,
    or CPI uprating. It DOES construct education dummies and NUTS1 region
    dummies needed for RURO estimation.
    """
    setup_logging(log_level)
    processed_dir = ensure_dir(processed_dir)

    singles, couples = _load_filtered_data(processed_dir, base_year=base_year, export_format=export_format)

    # ruro_group: group code for later estimation
    singles["ruro_group"] = 1   # singles
    couples["ruro_group"] = 10  # couples

    singles_ruro = _add_ruro_variables_basic(singles, default_year=base_year)
    couples_ruro = _add_ruro_variables_basic(couples, default_year=base_year)

    out_singles = processed_dir / f"singles_RURO_ready.{export_format}"
    out_couples = processed_dir / f"couples_RURO_ready.{export_format}"

    if export_format == "parquet":
        singles_ruro.to_parquet(out_singles, index=False)  # type: ignore[arg-type]
        couples_ruro.to_parquet(out_couples, index=False)  # type: ignore[arg-type]
    else:
        singles_ruro.to_csv(out_singles, index=False)
        couples_ruro.to_csv(out_couples, index=False)

    meta: Dict[str, Any] = {
        "processed_dir": str(processed_dir),
        "base_year": int(base_year),
        "export_format": export_format,
        "singles_rows": int(singles_ruro.shape[0]),
        "couples_rows": int(couples_ruro.shape[0]),
        "singles_file": str(out_singles),
        "couples_file": str(out_couples),
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
