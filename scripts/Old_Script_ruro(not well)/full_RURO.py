#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fully self-contained RURO pipeline runner.

This single file consolidates the functionality of:
  - run_fr_2021_prep.py (stubbed: see notes below)
  - RURO_prep.py
  - RURO_draws.py
  - RURO_prep_mnl_basic.py
  - RURO_boxcox_mnl.py

Design goals
------------
* No project-local imports: every helper and loop lives in this file.
* You can execute individual stages with skip flags or supply existing
  intermediate files via CLI overrides.
* The FR prep stage (EUROMOD-heavy) is provided as a lightweight stub that
  simply checks for existing processed data; it avoids depending on the large
  data_prep2/my_functions stack. Point the later stages to already-prepared
  singles/couples filtering outputs to proceed end-to-end.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm


# ---------------------------------------------------------------------------
# Minimal path helpers (self contained)
# ---------------------------------------------------------------------------

ENV_HINTS = ("MNL_STORAGE_ROOT", "MNL_DATA_ROOT", "MNL_ROOT")  # storage hints to locate Data/


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


def resolve_storage_root() -> Path:
    """Locate storage root containing 'Data'."""
    env_candidates: list[Path] = []  # explicit env overrides first
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


def data_root() -> Path:
    storage = resolve_storage_root()
    data_dir = storage / "Data"
    if data_dir.exists():
        return data_dir
    if storage.name.lower() == "data":
        return storage
    raise FileNotFoundError("Resolved storage root does not contain 'Data'.")


def reports_root() -> Path:
    return resolve_storage_root() / "reports"


def outputs_root() -> Path:
    return resolve_storage_root() / "outputs"


def euromod_root(explicit: Path | None = None) -> Path:
    """Locate EUROMOD release root."""
    if explicit:
        return explicit
    env = os.environ.get("MNL_EUROMOD_ROOT")
    if env:
        candidate = Path(env).expanduser()
        if candidate.exists():
            return candidate
    storage = resolve_storage_root()
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


def euromod_raw_root() -> Path:
    env = os.environ.get("EUROMOD_RAW")
    if env:
        return Path(env).expanduser()
    return data_root() / "raw"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=getattr(logging, level.upper()), format="%(message)s")


# ---------------------------------------------------------------------------
# EUROMOD integration helpers (self contained wrappers)
# ---------------------------------------------------------------------------


def _read_microdata_file(path: Path) -> pd.DataFrame:
    """Read raw/processed microdata with flexible extensions."""
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
    """Thin wrapper around the euromod API to keep imports local."""

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
            # fallback to first available
            systems_iter = getattr(country_obj, "systems", country_obj.values())
            system = next(iter(systems_iter))
        dataset = None
        if hasattr(system, "datasets"):
            dataset = system.datasets.get(dataset_name)
        if dataset is None and getattr(system, "bestmatch_datasets", None):
            dataset = system.bestmatch_datasets[0]
        if dataset is None:
            raise KeyError(f"Dataset {dataset_name} not found in EUROMOD system {system_code}")
        return system, dataset

    def run_on_dataframe(self, df: pd.DataFrame, *, country: str, system_code: str, dataset_name: str) -> pd.DataFrame:
        system, dataset = self._resolve_system(country, system_code, dataset_name)
        sim = system.run(df, dataset.name)
        return sim.outputs[0]


def run_euromod_baseline(
    raw_path: Path,
    *,
    country: str,
    system_code: str,
    dataset_name: str,
    em_root: Path,
) -> pd.DataFrame:
    """Single EUROMOD run on raw microdata (baseline)."""
    runner = EuromodRunner(em_root)
    raw_df = _read_microdata_file(raw_path)
    return runner.run_on_dataframe(raw_df, country=country, system_code=system_code, dataset_name=dataset_name)


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
    hours_col: str = "lhw",
    wage_col: str = "yivwg",
) -> Path:
    """
    Run EUROMOD once per draw across all households (heavy).

    For each draw value, we create a household-level microdata snapshot with
    draw-specific hours/wages, run EUROMOD, save as h_<draw>.parquet, and also
    write a combined parquet of all simulated draws.
    """
    scenario_dir = scenario_dir.resolve()
    scenario_dir.mkdir(parents=True, exist_ok=True)

    template_df = _read_microdata_file(micro_template_path)
    runner = EuromodRunner(em_root)
    combined: list[pd.DataFrame] = []

    draw_ids = sorted(draws_df["draw"].unique())

    for draw_id in draw_ids:
        draw_subset = draws_df[draws_df["draw"] == draw_id]
        hours_map = pd.to_numeric(draw_subset.get(hours_col, draw_subset.get("lhw")), errors="coerce")
        wage_map = pd.to_numeric(draw_subset.get(wage_col, draw_subset.get("wage_ruro", draw_subset.get("yivwg"))), errors="coerce")
        hours_lookup = dict(zip(draw_subset[id_col], hours_map))
        wage_lookup = dict(zip(draw_subset[id_col], wage_map))

        em_input = template_df.copy()
        if hours_lookup:
            em_input[hours_col] = em_input[id_col].map(hours_lookup).fillna(em_input[hours_col])
        if wage_lookup:
            em_input[wage_col] = em_input[id_col].map(wage_lookup).fillna(em_input[wage_col])

        sim_df = runner.run_on_dataframe(em_input, country=country, system_code=system_code, dataset_name=dataset_name)
        sim_df["sim_draw"] = draw_id
        out_path = scenario_dir / f"h_{int(draw_id):03d}.parquet"
        sim_df.to_parquet(out_path, index=False)  # type: ignore[arg-type]
        combined.append(sim_df)

    combined_df = pd.concat(combined, axis=0, ignore_index=True) if combined else pd.DataFrame()
    combined_path = scenario_dir / "combined_draws.parquet"
    combined_df.to_parquet(combined_path, index=False)  # type: ignore[arg-type]
    return combined_path


# ---------------------------------------------------------------------------
# Stage 0: FR prep stub (self contained)
# ---------------------------------------------------------------------------

def prepare_fr_2021_stub(
    *,
    raw_dir: Optional[Path],
    raw_filename: str,
    out_dir: Optional[Path],
    country: str = "FR",
    year: int = 2021,
    system_year: int = 2020,
) -> tuple[Path, Dict[str, Any]]:
    """
    Lightweight placeholder for the EUROMOD-heavy prep stage.

    This stub does NOT run EUROMOD. It simply resolves output directories and
    verifies that the requested raw file exists. Use this when you already have
    processed/filtering outputs and want to keep the pipeline self contained.
    """
    raw_dir = raw_dir or euromod_raw_root()  # default EUROMOD raw location
    out_dir = out_dir or (data_root() / "processed" / country.lower() / str(year))
    ensure_dir(out_dir)

    raw_path = raw_dir / raw_filename
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw micro-data not found: {raw_path}")

    meta: Dict[str, Any] = {
        "country": country,
        "year": year,
        "system_year": system_year,
        "raw_path": str(raw_path),
        "processed_dir": str(out_dir),
        "note": "Placeholder prep used; no EUROMOD run performed.",
    }
    (out_dir / "prep_meta_stub.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return out_dir, meta


# ---------------------------------------------------------------------------
# Stage 1: RURO_prep (inline from scripts/RURO_prep.py)
# ---------------------------------------------------------------------------

DEFAULT_COUNTRY = "fr"
DEFAULT_YEAR = 2021
DEFAULT_EXPORT_FORMAT = "parquet"


def _maybe_add_column(df: pd.DataFrame, name: str, values: Any) -> None:
    if name not in df.columns:
        df[name] = values


def _resolve_processed_dir(
    arg_dir: Path | None,
    base_year: int,
    export_format: str = DEFAULT_EXPORT_FORMAT,
) -> Path:
    if arg_dir is not None and arg_dir.is_absolute():  # absolute override wins
        return arg_dir

    rel = arg_dir if arg_dir is not None else Path("processed") / DEFAULT_COUNTRY / str(base_year)

    candidates: list[Path] = []  # search external first, then local
    try:
        candidates.append(resolve_storage_root())
    except Exception:
        pass
    candidates.append(Path(r"U:/EUROMOD-STORAGE"))
    candidates.append(Path.home() / "EUROMOD-STORAGE")
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
            singles_candidate = candidate / f"singles_filtering_final.{export_format}"
            if singles_candidate.exists():
                return candidate.resolve()
            chosen = chosen or candidate

    if chosen:
        return chosen.resolve()
    return (data_root() / rel).resolve()


def _load_filtered_data(
    processed_dir: Path,
    export_format: str = DEFAULT_EXPORT_FORMAT,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    singles_path = processed_dir / f"singles_filtering_final.{export_format}"
    couples_path = processed_dir / f"couples_filtering_final.{export_format}"

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
    if "input_year" in df.columns:
        year = pd.to_numeric(df["input_year"], errors="coerce")
    elif "system_year" in df.columns:
        year = pd.to_numeric(df["system_year"], errors="coerce")
    elif "yds" in df.columns:
        year = pd.to_numeric(df["yds"], errors="coerce")
    else:
        year = pd.Series(default_year, index=df.index, dtype="float64")
    year = year.fillna(default_year).astype(int)
    return year


def _add_ruro_variables_basic(
    df: pd.DataFrame,
    *,
    default_year: int = DEFAULT_YEAR,
) -> pd.DataFrame:
    df = df.copy()

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

    dag = pd.to_numeric(df["dag"], errors="coerce")
    year_for_calc = year

    if "dew" in df.columns:
        grad_year = pd.to_numeric(df["dew"], errors="coerce")
        grad_year_clean = grad_year.where(
            (grad_year >= 1900) & (grad_year <= year_for_calc + 1),
            np.nan,
        )
        pexp = (dag - 18).clip(lower=0)
        mask = grad_year_clean.notna()
        pexp.loc[mask] = (year_for_calc.loc[mask] - grad_year_clean.loc[mask]).clip(lower=0)
    else:
        pexp = (dag - 18).clip(lower=0)

    pexp_years = pexp.astype(float)
    pexp_years2 = (pexp_years ** 2).astype(float)

    _maybe_add_column(df, "pexp_years", pexp_years)
    _maybe_add_column(df, "pexp_years2", pexp_years2)

    if "pexp" not in df.columns:
        df["pexp"] = df["pexp_years"]

    wage_source = None
    for cand in ["wage_final", "w_emp_strict", "yivwg"]:
        if cand in df.columns:
            wage_source = cand
            break
    if wage_source is None:
        raise KeyError("No wage variable found for RURO. Expected one of 'wage_final', 'w_emp_strict', or 'yivwg'.")

    lhw = pd.to_numeric(df["lhw"], errors="coerce").fillna(0.0)
    les = pd.to_numeric(df["les"], errors="coerce")

    is_worker = les.eq(3) & (lhw > 0.0)
    _maybe_add_column(df, "is_worker", is_worker.astype(int))

    wage_numeric = pd.to_numeric(df[wage_source], errors="coerce").fillna(0.0)
    wage_ruro = np.where(is_worker, wage_numeric, 0.0)
    _maybe_add_column(df, "wage_ruro", wage_ruro)

    working = (lhw > 0.0).astype(int)
    working_pt1 = ((lhw > 0.0) & (lhw <= 20.0)).astype(int)
    working_pt2 = ((lhw > 20.0) & (lhw <= 35.0)).astype(int)
    working_ft = (lhw > 35.0).astype(int)

    _maybe_add_column(df, "working", working)
    _maybe_add_column(df, "working_pt1", working_pt1)
    _maybe_add_column(df, "working_pt2", working_pt2)
    _maybe_add_column(df, "working_ft", working_ft)

    _maybe_add_column(df, "hours", lhw)
    _maybe_add_column(df, "wage", wage_ruro)

    return df


def _prepare_ruro_basic(
    processed_dir: Path,
    *,
    base_year: int = DEFAULT_YEAR,
    export_format: str = DEFAULT_EXPORT_FORMAT,
) -> Dict[str, Any]:
    setup_logging("INFO")
    processed_dir = ensure_dir(processed_dir)

    singles, couples = _load_filtered_data(processed_dir, export_format=export_format)

    singles["ruro_group"] = 1   # singles marker
    couples["ruro_group"] = 10  # couples marker

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


# ---------------------------------------------------------------------------
# Stage 2: RURO_draws (inline from scripts/RURO_draws.py)
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

DEFAULT_WAGE_SPEC = "vw"
DEFAULT_N_DRAWS = 99
DEFAULT_RNG_SEED = 13


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
    df.to_csv(csv_path, index=False)
    return {"parquet": parquet_path, "csv": csv_path}


def _attach_other_members_income(df: pd.DataFrame) -> pd.DataFrame:
    if "idhh" not in df.columns or "ils_dispy" not in df.columns:
        return df
    hh_is_head = pd.to_numeric(df.get("hh_IsHead", 0), errors="coerce").fillna(0).astype(int)
    hh_is_partner = pd.to_numeric(df.get("hh_IsPartner", 0), errors="coerce").fillna(0).astype(int)
    is_other = ~(hh_is_head.astype(bool) | hh_is_partner.astype(bool))
    other_income = df["ils_dispy"].where(is_other, 0.0)
    other_sum = other_income.groupby(df["idhh"]).sum()
    df["other_members_income"] = df["idhh"].map(other_sum).fillna(0.0)
    return df


def _build_loc_distribution(df: pd.DataFrame) -> Optional[Dict[Any, float]]:
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

    counts = df.loc[mask, "loc"].value_counts(dropna=True)
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
    if n_draws < 0:
        raise ValueError("n_draws must be >= 0")

    df = df.copy().reset_index(drop=True)

    if "idperson" not in df.columns:  # must identify individuals
        raise KeyError("RURO_ready dataset must contain 'idperson'.")

    if "hours" in df.columns:
        hours = pd.to_numeric(df["hours"], errors="coerce").fillna(0.0)
    elif "lhw" in df.columns:
        hours = pd.to_numeric(df["lhw"], errors="coerce").fillna(0.0)
        df["hours"] = hours
    else:
        raise KeyError("RURO_ready dataset must contain 'hours' or 'lhw'.")

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

    if "lma" in df.columns:
        lma = pd.to_numeric(df["lma"], errors="coerce").fillna(1).astype(int)
    else:
        lma = pd.Series(1, index=df.index, dtype=int)
    if "dgn" in df.columns:
        dgn = pd.to_numeric(df["dgn"], errors="coerce").fillna(1).astype(int)
    else:
        dgn = pd.Series(1, index=df.index, dtype=int)

    pi0_vec = np.zeros(len(df), dtype=float)
    mask_m = (lma == 1) & (dgn == 1)
    mask_f = (lma == 1) & (dgn == 0)
    pi0_vec[mask_m.to_numpy()] = pi0_m
    pi0_vec[mask_f.to_numpy()] = pi0_f

    loc_probs = _build_loc_distribution(df)
    rng = np.random.default_rng(rng_seed)

    records: list[Dict[str, Any]] = []

    for i, row in df.iterrows():
        base: Dict[str, Any] = row.to_dict()

        r0 = base.copy()
        r0["draw"] = 0
        r0["is_chosen"] = 1
        records.append(r0)

        if n_draws == 0:
            continue

        pi0_i = float(pi0_vec[i])

        for j in range(1, n_draws + 1):
            rj = base.copy()

            u = rng.random()
            if u < pi0_i:
                h = 0.0
                w = 0.0
            else:
                h = float(rng.uniform(h_min, h_max))
                if wage_spec == "vw":
                    w = float(rng.uniform(w_min, w_max))
                else:
                    w = float(wage[i])

            rj["hours"] = h
            rj["lhw"] = h

            rj["wage"] = w
            if "wage_ruro" in rj:
                rj["wage_ruro"] = w
            if "yivwg" in rj:
                rj["yivwg"] = w
            if "yem" in rj:
                rj["yem"] = w * h * WEEKS_PER_MONTH

            if "loc" in rj:
                if (h > 0.0) and loc_probs:
                    rj["loc"] = _sample_loc(loc_probs, 1, rng)[0]
                else:
                    rj["loc"] = base.get("loc", rj.get("loc"))

            rj["draw"] = j
            rj["is_chosen"] = 0
            records.append(rj)

    long_df = pd.DataFrame.from_records(records)
    return long_df


# ---------------------------------------------------------------------------
# Stage 3: RURO_prep_mnl_basic (inline)
# ---------------------------------------------------------------------------

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


def _build_mnl_block(df: pd.DataFrame, sample_group: str) -> pd.DataFrame:
    df = df.copy()

    if "idperson" not in df.columns or "draw" not in df.columns or "is_chosen" not in df.columns:
        raise KeyError("Expected columns 'idperson', 'draw', 'is_chosen' in RURO_draws data.")

    hours = pd.to_numeric(df.get("hours", df.get("lhw")), errors="coerce").fillna(0.0)
    df["hours"] = hours

    if "yem" not in df.columns:
        wage = pd.to_numeric(df.get("wage", df.get("wage_ruro", df.get("yivwg"))), errors="coerce").fillna(0.0)
        df["yem"] = wage * hours * WEEKS_PER_MONTH

    if "ils_dispy" in df.columns:
        cons_base = pd.to_numeric(df["ils_dispy"], errors="coerce").fillna(0.0)
    else:
        cons_base = pd.to_numeric(df["yem"], errors="coerce").fillna(0.0)
    if "other_members_income" in df.columns:
        other_inc = pd.to_numeric(df["other_members_income"], errors="coerce").fillna(0.0)
    else:
        other_inc = pd.Series(0.0, index=df.index)

    if "ruro_group" in df.columns:
        ruro_group = pd.to_numeric(df["ruro_group"], errors="coerce").fillna(0)
    else:
        ruro_group = pd.Series(0, index=df.index)
    cons = cons_base.copy()
    singles_mask = ruro_group.eq(1)
    cons.loc[singles_mask] = cons_base.loc[singles_mask] + other_inc.loc[singles_mask]
    couples_mask = ruro_group.eq(10)
    if couples_mask.any() and "idhh" in df.columns:
        hh_total = (cons_base + other_inc).groupby(df["idhh"]).transform("sum")
        cons.loc[couples_mask] = hh_total.loc[couples_mask]

    cons = cons.clip(lower=DCM_MIN_POSITIVE)

    leisure = TOTAL_LEISURE_HOURS - hours
    leisure = leisure.clip(lower=DCM_MIN_POSITIVE)

    df["log_c"] = np.log(cons)
    df["log_l"] = np.log(leisure)

    keep_cols = [
        "idperson", "draw", "is_chosen",
        "ruro_group",
        "log_c", "log_l",
        "hours", "yem",
        "wage", "wage_ruro", "yivwg",
        "dgn", "pexp_years", "pexp_years2",
        "loc", "yd1", "yd2", "yd3",
    ]
    existing = [c for c in keep_cols if c in df.columns]
    out = df[existing].copy()
    out["sample_group"] = sample_group
    return out


# ---------------------------------------------------------------------------
# Stage 4: RURO_boxcox_mnl (inline)
# ---------------------------------------------------------------------------

T_HOURS: float = 80.0
EPS: float = 1e-8


def boxcox_transform(x: np.ndarray, alpha: float) -> np.ndarray:
    x = np.clip(x, EPS, None)
    if abs(alpha) < 1e-8:
        return np.log(x)
    return (np.power(x, alpha) - 1.0) / alpha


def d_boxcox_dalpha(x: np.ndarray, alpha: float) -> np.ndarray:
    x = np.clip(x, EPS, None)
    ln_x = np.log(x)
    if abs(alpha) < 1e-8:
        return 0.5 * ln_x * ln_x
    x_a = np.power(x, alpha)
    num = alpha * x_a * ln_x - (x_a - 1.0)
    den = alpha * alpha
    return num / den


def boxcox_derivative(x: np.ndarray, alpha: float) -> np.ndarray:
    x = np.clip(x, EPS, None)
    if abs(alpha) < 1e-8:
        return 1.0 / x
    return np.power(x, alpha - 1.0)


@dataclass
class RuroData:
    n_groups: int
    group_start: np.ndarray
    group_end: np.ndarray
    chosen_index: np.ndarray
    weights: np.ndarray
    cons: np.ndarray
    leis: np.ndarray
    c_norm: np.ndarray
    l_norm: np.ndarray
    y_ref: float
    l_min_pos: float


def build_ruro_data(
    df: pd.DataFrame,
    *,
    id_col: str = "idperson",
    choice_col: str = "is_chosen",
    cons_col: str = "consumption",
    hours_col: str | None = "hours",
    leisure_col: str | None = None,
    weight_col: str | None = None,
    t_hours: float = T_HOURS,
) -> RuroData:
    for col in (id_col, choice_col, cons_col):
        if col not in df.columns:
            raise KeyError(f"Dataset missing required column '{col}'")

    if leisure_col is None and hours_col is None:
        raise ValueError("Either 'hours_col' or 'leisure_col' must be provided.")

    df = df.copy()

    for col in [cons_col, choice_col] + ([hours_col] if hours_col else []) + ([leisure_col] if leisure_col else []):
        if col and col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if weight_col and weight_col in df.columns:
        df[weight_col] = pd.to_numeric(df[weight_col], errors="coerce").fillna(1.0)
    else:
        weight_col = None

    sort_cols = [id_col]
    if "draw" in df.columns:
        sort_cols.append("draw")
    df.sort_values(sort_cols, inplace=True)
    df.reset_index(drop=True, inplace=True)

    ids = df[id_col].to_numpy()
    choice = (df[choice_col] > 0).to_numpy(dtype=bool)
    cons = df[cons_col].to_numpy(dtype=float)

    if leisure_col and leisure_col in df.columns:
        leis = df[leisure_col].to_numpy(dtype=float)
    else:
        if hours_col not in df.columns:
            raise KeyError(f"hours_col='{hours_col}' not found in dataset.")
        hours = df[hours_col].to_numpy(dtype=float)
        leis = t_hours - hours

    unique_ids, group_start = np.unique(ids, return_index=True)
    n_groups = unique_ids.size
    group_end = np.empty_like(group_start)
    group_end[:-1] = group_start[1:]
    group_end[-1] = len(df)

    chosen_index = np.empty(n_groups, dtype=int)
    weights = np.ones(n_groups, dtype=float)

    for g in range(n_groups):
        s = group_start[g]
        e = group_end[g]
        ch_g = choice[s:e]
        if not np.any(ch_g):
            raise ValueError(f"Group {g} (id={unique_ids[g]}) has no chosen alternative.")
        if np.sum(ch_g) > 1:
            raise ValueError(f"Group {g} (id={unique_ids[g]}) has multiple chosen alternatives.")
        local_idx = np.argmax(ch_g)
        chosen_index[g] = s + local_idx
        if weight_col:
            w = float(df.iloc[s][weight_col])
            if not np.isfinite(w) or w <= 0:
                w = 1.0
            weights[g] = w

    cons_chosen = cons[chosen_index]
    leis_chosen = leis[chosen_index]

    cons_pos = cons_chosen[np.isfinite(cons_chosen) & (cons_chosen > 0.0)]
    if cons_pos.size == 0:
        raise ValueError("No positive consumption values among chosen alternatives.")
    y_ref = float(cons_pos.mean())

    leis_pos = leis_chosen[np.isfinite(leis_chosen) & (leis_chosen > 0.0)]
    if leis_pos.size == 0:
        raise ValueError("No positive leisure values among chosen alternatives.")
    l_min_pos = float(leis_pos.min())

    c_norm = cons / y_ref
    l_norm = leis / l_min_pos

    return RuroData(
        n_groups=n_groups,
        group_start=group_start,
        group_end=group_end,
        chosen_index=chosen_index,
        weights=weights,
        cons=cons,
        leis=leis,
        c_norm=c_norm,
        l_norm=l_norm,
        y_ref=y_ref,
        l_min_pos=l_min_pos,
    )


def neg_loglik_and_grad(theta: np.ndarray, data: RuroData) -> Tuple[float, np.ndarray]:
    alpha_c, alpha_l, beta_c, beta_l = theta
    M = data.c_norm.shape[0]
    G = data.n_groups

    bc_c = boxcox_transform(data.c_norm, alpha_c)
    bc_l = boxcox_transform(data.l_norm, alpha_l)
    bc_c_dalpha = d_boxcox_dalpha(data.c_norm, alpha_c)
    bc_l_dalpha = d_boxcox_dalpha(data.l_norm, alpha_l)

    util = beta_c * bc_c + beta_l * bc_l

    nll = 0.0
    grad = np.zeros(4, dtype=float)

    for g in range(G):
        s = data.group_start[g]
        e = data.group_end[g]
        idx = slice(s, e)

        u_g = util[idx]
        bc_c_g = bc_c[idx]
        bc_l_g = bc_l[idx]
        bc_c_da_g = bc_c_dalpha[idx]
        bc_l_da_g = bc_l_dalpha[idx]

        u_max = float(np.max(u_g))
        exp_u = np.exp(u_g - u_max)
        denom = float(exp_u.sum())
        if denom <= 0.0 or not np.isfinite(denom):
            return 1e12, np.zeros_like(grad)
        p_g = exp_u / denom

        j_star_abs = data.chosen_index[g]
        j_star_loc = j_star_abs - s

        w = data.weights[g]

        p_star = float(p_g[j_star_loc])
        if p_star <= 0.0 or not np.isfinite(p_star):
            return 1e12, np.zeros_like(grad)
        nll -= w * math.log(p_star)

        dV_dalpha_c = beta_c * bc_c_da_g
        dV_dalpha_l = beta_l * bc_l_da_g
        dV_dbeta_c = bc_c_g
        dV_dbeta_l = bc_l_g

        EV_alpha_c = float(np.dot(p_g, dV_dalpha_c))
        EV_alpha_l = float(np.dot(p_g, dV_dalpha_l))
        EV_beta_c = float(np.dot(p_g, dV_dbeta_c))
        EV_beta_l = float(np.dot(p_g, dV_dbeta_l))

        dV_star_alpha_c = float(dV_dalpha_c[j_star_loc])
        dV_star_alpha_l = float(dV_dalpha_l[j_star_loc])
        dV_star_beta_c = float(dV_dbeta_c[j_star_loc])
        dV_star_beta_l = float(dV_dbeta_l[j_star_loc])

        grad[0] -= w * (dV_star_alpha_c - EV_alpha_c)
        grad[1] -= w * (dV_star_alpha_l - EV_alpha_l)
        grad[2] -= w * (dV_star_beta_c - EV_beta_c)
        grad[3] -= w * (dV_star_beta_l - EV_beta_l)

    return nll, grad


def neg_loglik(theta: np.ndarray, data: RuroData) -> float:
    nll, _ = neg_loglik_and_grad(theta, data)
    return nll


def grad_neg_loglik(theta: np.ndarray, data: RuroData) -> np.ndarray:
    _, grad = neg_loglik_and_grad(theta, data)
    return grad


def approximate_hessian(theta: np.ndarray, data: RuroData, eps: float = 1e-5) -> np.ndarray:
    k = len(theta)
    H = np.zeros((k, k), dtype=float)
    f0 = neg_loglik(theta, data)
    eye = np.eye(k)

    def h(i: int) -> float:
        return eps * max(1.0, abs(theta[i]))

    for i in range(k):
        hi = h(i)
        ei = eye[i] * hi
        f_plus = neg_loglik(theta + ei, data)
        f_minus = neg_loglik(theta - ei, data)
        H[i, i] = (f_plus - 2.0 * f0 + f_minus) / (hi * hi)

        for j in range(i + 1, k):
            hj = h(j)
            ej = eye[j] * hj
            f_pp = neg_loglik(theta + ei + ej, data)
            f_pm = neg_loglik(theta + ei - ej, data)
            f_mp = neg_loglik(theta - ei + ej, data)
            f_mm = neg_loglik(theta - ei - ej, data)
            H_ij = (f_pp - f_pm - f_mp + f_mm) / (4.0 * hi * hj)
            H[i, j] = H[j, i] = H_ij

    return H


def compute_null_loglik(data: RuroData) -> float:
    ll = 0.0
    for g in range(data.n_groups):
        J_g = data.group_end[g] - data.group_start[g]
        if J_g <= 0:
            continue
        w = data.weights[g]
        ll -= w * math.log(J_g)
    return ll


def run_estimation(data: RuroData, output_dir: Path, model_name: str = "ruro_boxcox") -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    theta0 = np.array([0.10, 0.10, 1.0, 1.0], dtype=float)

    logging.info("Initial theta: %s", theta0)

    result = minimize(
        neg_loglik,
        theta0,
        args=(data,),
        method="L-BFGS-B",
        jac=grad_neg_loglik,
        options={"maxiter": 2000, "disp": True},
    )

    if not result.success:
        logging.warning("Optimiser did not fully converge: %s", result.message)

    theta_hat = result.x
    nll_star = neg_loglik(theta_hat, data)
    ll_star = -nll_star
    ll_null = compute_null_loglik(data)

    alpha_c, alpha_l, beta_c, beta_l = theta_hat
    logging.info(
        "theta_hat = [alpha_c=%.4f, alpha_l=%.4f, beta_c=%.4f, beta_l=%.4f]",
        alpha_c, alpha_l, beta_c, beta_l,
    )

    k = len(theta_hat)
    rho2 = 1.0 - ll_star / ll_null if ll_null != 0 else float("nan")
    rho2_adj = 1.0 - (ll_star - k) / ll_null if ll_null != 0 else float("nan")

    H = approximate_hessian(theta_hat, data)
    H = 0.5 * (H + H.T)
    try:
        cov = np.linalg.inv(H)
    except np.linalg.LinAlgError:
        logging.warning("Hessian not invertible; falling back to pseudo-inverse.")
        cov = np.linalg.pinv(H)

    se = np.sqrt(np.maximum(np.diag(cov), 0.0))
    t_vals = theta_hat / se
    p_vals = 2.0 * (1.0 - norm.cdf(np.abs(t_vals)))

    names = ["alpha_c", "alpha_l", "beta_c", "beta_l"]
    logging.info("Log-likelihood at optimum: %.4f", ll_star)
    logging.info("LL(null): %.4f  rho2=%.4f  rho2_adj=%.4f", ll_null, rho2, rho2_adj)
    logging.info("Parameter estimates:")
    for name, val, s, t, p in zip(names, theta_hat, se, t_vals, p_vals):
        logging.info("  %-8s  %10.6f  (se=%10.6f, t=%8.3f, p=%6.4f)", name, val, s, t, p)

    meta = {
        "model": model_name,
        "theta_hat": {n: float(v) for n, v in zip(names, theta_hat)},
        "se": {n: float(s) for n, s in zip(names, se)},
        "t_values": {n: float(t) for n, t in zip(names, t_vals)},
        "p_values": {n: float(p) for n, p in zip(names, p_vals)},
        "ll_star": float(ll_star),
        "ll_null": float(ll_null),
        "rho2": float(rho2),
        "rho2_adj": float(rho2_adj),
        "y_ref": float(data.y_ref),
        "l_min_pos": float(data.l_min_pos),
    }

    out_path = output_dir / f"{model_name}_results.json"
    out_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    logging.info("Saved results to %s", out_path)


# ---------------------------------------------------------------------------
# Pipeline orchestration (self contained)
# ---------------------------------------------------------------------------

COUNTRY_DEFAULT = "FR"
YEAR_DEFAULT = 2021
SYSTEM_YEAR_DEFAULT = 2020
RAW_FILE_DEFAULT = "FR_2021_c2.txt"


def _find_existing(paths: list[Path | None]) -> Optional[Path]:
    for p in paths:
        if p and p.exists():
            return p
    return None


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Self-contained RURO pipeline runner.")

    ap.add_argument("--run-prep", action="store_true", help="Run lightweight FR prep stub (otherwise expects existing processed data).")
    ap.add_argument("--run-ruro-prep", action="store_true", help="Run RURO_prep stage to build RURO_ready files.")
    ap.add_argument("--run-draws", action="store_true", help="Run RURO_draws stage to create long draws.")
    ap.add_argument("--run-mnl", action="store_true", help="Run RURO_prep_mnl_basic stage.")
    ap.add_argument("--run-boxcox", action="store_true", help="Run Box-Cox MNL estimation.")
    ap.add_argument("--run-euromod-base", action="store_true", help="Run EUROMOD once on raw microdata before RURO.")
    ap.add_argument("--run-euromod-draws", action="store_true", help="Run EUROMOD for each draw (very slow).")

    ap.add_argument("--country", default=COUNTRY_DEFAULT, help="Country code (default: FR).")
    ap.add_argument("--year", type=int, default=YEAR_DEFAULT, help="Input micro-data year (default: 2021).")
    ap.add_argument("--system-year", type=int, default=SYSTEM_YEAR_DEFAULT, help="EUROMOD system year (default: 2020).")
    ap.add_argument("--raw-file", default=RAW_FILE_DEFAULT, help="Raw micro-data filename (default: FR_2021_c2.txt).")
    ap.add_argument("--raw-dir", type=Path, default=None, help="EUROMOD raw directory override.")
    ap.add_argument("--processed-dir", type=Path, default=None, help="Processed directory override.")
    ap.add_argument("--export-format", default=DEFAULT_EXPORT_FORMAT, choices=["parquet", "csv"], help="Export format for RURO_prep outputs.")
    ap.add_argument("--euromod-root", type=Path, default=None, help="Path to EUROMOD release (override).")
    ap.add_argument("--euromod-system", default=None, help="EUROMOD system code, defaults to <country>_<system_year>.")
    ap.add_argument("--euromod-dataset", default=None, help="EUROMOD dataset name, defaults to raw file stem.")
    ap.add_argument("--microdata-template", type=Path, default=None, help="Microdata file to mutate for per-draw EUROMOD runs.")
    ap.add_argument("--euromod-hours-col", default="lhw", help="Column to overwrite with simulated hours in EUROMOD runs.")
    ap.add_argument("--euromod-wage-col", default="yivwg", help="Column to overwrite with simulated wages in EUROMOD runs.")
    ap.add_argument("--scenario-dir", type=Path, default=None, help="Output directory for EUROMOD per-draw scenarios (default: storage/interim/ruro/<country>/scenarios).")

    ap.add_argument("--singles-ruro", type=Path, default=None, help="Existing singles_RURO_ready file.")
    ap.add_argument("--couples-ruro", type=Path, default=None, help="Existing couples_RURO_ready file.")
    ap.add_argument("--singles-draws", type=Path, default=None, help="Existing singles RURO draws file.")
    ap.add_argument("--couples-draws", type=Path, default=None, help="Existing couples RURO draws file.")
    ap.add_argument("--mnl-path", type=Path, default=None, help="Existing RURO MNL dataset.")

    ap.add_argument("--n-draws", type=int, default=DEFAULT_N_DRAWS, help="Number of simulated draws per person.")
    ap.add_argument("--wage-spec", choices=["fw", "vw"], default=DEFAULT_WAGE_SPEC, help="Wage specification for draws.")
    ap.add_argument("--pi0-m", type=float, default=DEFAULT_PI0_M, help="Mass at zero hours for active men.")
    ap.add_argument("--pi0-f", type=float, default=DEFAULT_PI0_F, help="Mass at zero hours for active women.")
    ap.add_argument("--h-min", type=float, default=DEFAULT_H_MIN, help="Lower bound of hours support.")
    ap.add_argument("--h-max", type=float, default=DEFAULT_H_MAX, help="Upper bound of hours support.")
    ap.add_argument("--w-min", type=float, default=DEFAULT_W_MIN, help="Lower bound of wage support.")
    ap.add_argument("--w-max", type=float, default=DEFAULT_W_MAX, help="Upper bound of wage support.")
    ap.add_argument("--rng-seed", type=int, default=DEFAULT_RNG_SEED, help="Base RNG seed for draws.")

    ap.add_argument("--t-hours", type=float, default=T_HOURS, help="Total leisure endowment for Box-Cox prep.")
    ap.add_argument("--model-name", default="ruro_boxcox", help="Model name used for Box-Cox outputs.")
    ap.add_argument("--boxcox-output-dir", type=Path, default=None, help="Override Box-Cox output directory.")

    ap.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging verbosity.")

    return ap.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging(args.log_level)

    country = args.country.upper()
    year = int(args.year)
    export_format = args.export_format
    raw_dir_path = args.raw_dir or euromod_raw_root()
    raw_path = raw_dir_path / args.raw_file
    em_system_code = args.euromod_system or f"{country}_{args.system_year}"
    em_dataset = args.euromod_dataset or Path(args.raw_file).stem
    em_root_path: Optional[Path] = None
    combined_draws: list[pd.DataFrame] = []

    processed_dir: Optional[Path] = args.processed_dir

    if args.run_prep:
        # Stub prep: verify raw file, create processed dir marker
        processed_dir, _prep_meta = prepare_fr_2021_stub(
            raw_dir=raw_dir_path,
            raw_filename=args.raw_file,
            out_dir=processed_dir,
            country=country,
            year=year,
            system_year=args.system_year,
        )
        logging.info("Prep stub finished -> %s", processed_dir)
    elif processed_dir is None:
        processed_dir = data_root() / "processed" / country.lower() / str(year)
        logging.info("Using default processed dir: %s", processed_dir)

    if args.run_euromod_base:
        em_root_path = euromod_root(args.euromod_root)
        base_df = run_euromod_baseline(
            raw_path,
            country=country,
            system_code=em_system_code,
            dataset_name=em_dataset,
            em_root=em_root_path,
        )
        base_out = processed_dir / f"{country.lower()}_{year}_euromod_base.parquet"
        base_df.to_parquet(base_out, index=False)  # type: ignore[arg-type]
        logging.info("EUROMOD baseline saved to %s", base_out)

    singles_ruro = args.singles_ruro
    couples_ruro = args.couples_ruro
    if args.run_ruro_prep:
        # Build RURO_ready wide files from filtering outputs
        processed_dir = _resolve_processed_dir(processed_dir, year, export_format)
        ruro_meta = _prepare_ruro_basic(
            processed_dir=processed_dir,
            base_year=year,
            export_format=export_format,
        )
        singles_ruro = Path(ruro_meta["singles_file"])
        couples_ruro = Path(ruro_meta["couples_file"])
        logging.info("RURO prep completed. Singles: %s  Couples: %s", singles_ruro, couples_ruro)
    else:
        if singles_ruro is None:
            singles_ruro = _find_existing(
                [
                    processed_dir / f"singles_RURO_ready.{export_format}",
                    processed_dir / "singles_RURO_ready.parquet",
                    processed_dir / "singles_RURO_ready.csv",
                ]
            )
        if couples_ruro is None:
            couples_ruro = _find_existing(
                [
                    processed_dir / f"couples_RURO_ready.{export_format}",
                    processed_dir / "couples_RURO_ready.parquet",
                    processed_dir / "couples_RURO_ready.csv",
                ]
            )

    if singles_ruro is None and args.run_ruro_prep:
        raise SystemExit("RURO prep failed to produce singles RURO file.")

    singles_draws = args.singles_draws
    couples_draws = args.couples_draws
    if args.run_draws:
        # Simulate opportunity draws (long format)
        if singles_ruro is None:
            raise SystemExit("Missing singles RURO_ready file; cannot run draws.")
        draw_outputs = {}
        singles_df = _read_dataframe(singles_ruro)
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
        draw_outputs["singles"] = _write_dataframe(singles_long, singles_ruro, suffix="_RURO_draws")
        singles_draws = draw_outputs["singles"]["parquet"]
        combined_draws.append(singles_long)

        if couples_ruro and couples_ruro.exists():
            couples_df = _read_dataframe(couples_ruro)
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
                rng_seed=args.rng_seed + 1,
            )
            draw_outputs["couples"] = _write_dataframe(couples_long, couples_ruro, suffix="_RURO_draws")
            couples_draws = draw_outputs["couples"]["parquet"]
            combined_draws.append(couples_long)

        logging.info("Draws completed. Singles draws: %s Couples draws: %s", singles_draws, couples_draws)
    else:
        if singles_draws is None and singles_ruro:
            singles_draws = _find_existing(
                [
                    singles_ruro.with_name(f"{singles_ruro.stem}_RURO_draws.parquet"),
                    singles_ruro.with_name(f"{singles_ruro.stem}_RURO_draws.csv"),
                ]
            )
        if couples_draws is None and couples_ruro:
            couples_draws = _find_existing(
                [
                    couples_ruro.with_name(f"{couples_ruro.stem}_RURO_draws.parquet"),
                    couples_ruro.with_name(f"{couples_ruro.stem}_RURO_draws.csv"),
                ]
            )
        if singles_draws and Path(singles_draws).exists():
            combined_draws.append(_read_dataframe(Path(singles_draws)))
        if couples_draws and Path(couples_draws).exists():
            combined_draws.append(_read_dataframe(Path(couples_draws)))

    mnl_path = args.mnl_path
    mnl_df: pd.DataFrame | None = None
    if args.run_mnl:
        # Build MNL estimation dataset from draws
        if singles_draws is None:
            raise SystemExit("Missing singles draws file; cannot build MNL dataset.")
        default_base = processed_dir / f"{country.lower()}_{year}_RURO_mnl"
        out_base = mnl_path.with_suffix("") if mnl_path else default_base
        singles_long = _read_df(singles_draws)
        singles_mnl = _build_mnl_block(singles_long, sample_group="singles")
        frames = [singles_mnl]
        if couples_draws and couples_draws.exists():
            couples_long = _read_df(couples_draws)
            couples_mnl = _build_mnl_block(couples_long, sample_group="couples")
            frames.append(couples_mnl)
        mnl_df = pd.concat(frames, axis=0, ignore_index=True)
        mnl_outputs = _write_df(mnl_df, out_base)
        mnl_path = mnl_outputs["parquet"]
        logging.info("MNL dataset written to %s", mnl_path)
    else:
        if mnl_path is None:
            mnl_path = _find_existing(
                [
                    processed_dir / f"{country.lower()}_{year}_RURO_mnl.parquet",
                    processed_dir / f"{country.lower()}_{year}_RURO_mnl.csv",
                ]
            )

    if mnl_df is None and mnl_path:
        mnl_df = pd.read_parquet(mnl_path) if mnl_path.suffix.lower() == ".parquet" else pd.read_csv(mnl_path)

    if args.run_boxcox:
        # Run Box-Cox RURO MNL estimation
        if mnl_df is None:
            raise SystemExit("Missing MNL dataset; cannot run Box-Cox estimation.")
        df_box = mnl_df.copy()
        if "consumption" not in df_box.columns:
            log_c = pd.to_numeric(df_box.get("log_c"), errors="coerce")
            df_box["consumption"] = np.exp(np.clip(log_c, a_min=None, a_max=50.0))
        if "hours" not in df_box.columns and "lhw" in df_box.columns:
            df_box["hours"] = pd.to_numeric(df_box["lhw"], errors="coerce")
        df_box["leisure"] = args.t_hours - pd.to_numeric(df_box["hours"], errors="coerce")
        df_box["is_chosen"] = pd.to_numeric(df_box["is_chosen"], errors="coerce").fillna(0).astype(int)
        clean = df_box[
            ["idperson", "draw", "is_chosen", "consumption", "hours", "leisure"]
        ].replace([np.inf, -np.inf], np.nan).dropna()
        clean = clean.loc[(clean["consumption"] > 0) & (clean["leisure"] > 0) & (clean["hours"] >= 0)]
        data = build_ruro_data(
            clean,
            id_col="idperson",
            choice_col="is_chosen",
            cons_col="consumption",
            hours_col="hours",
            leisure_col=None,
            weight_col=None,
            t_hours=args.t_hours,
        )
        out_dir = args.boxcox_output_dir or (reports_root() / "mle_ruro" / "boxcox")
        run_estimation(data, out_dir, model_name=args.model_name)
        logging.info("Box-Cox estimation completed. Outputs at %s", out_dir)
    else:
        logging.info("Box-Cox estimation skipped.")

    if args.run_euromod_draws:
        if not combined_draws and singles_draws is None:
            raise SystemExit("Missing draws data; cannot run EUROMOD per draw.")
        em_root_path = em_root_path or euromod_root(args.euromod_root)
        micro_path = args.microdata_template or raw_path
        if not combined_draws:
            combined_draws.append(_read_dataframe(Path(singles_draws)))
        combined_df = pd.concat(combined_draws, axis=0, ignore_index=True)
        scenario_dir = (
            args.scenario_dir
            if args.scenario_dir
            else (resolve_storage_root() / "interim" / "ruro" / country.lower() / "scenarios")
        )
        combined_path = run_euromod_for_draws(
            combined_df,
            micro_path,
            country=country,
            system_code=em_system_code,
            dataset_name=em_dataset,
            em_root=em_root_path,
            scenario_dir=scenario_dir,
            id_col="idperson",
            hours_col=args.euromod_hours_col,
            wage_col=args.euromod_wage_col,
        )
        logging.info("EUROMOD per-draw scenarios saved under %s (combined: %s)", scenario_dir, combined_path)
    elif args.run_euromod_base:
        logging.info("EUROMOD per-draw runs skipped.")


if __name__ == "__main__":
    main()
