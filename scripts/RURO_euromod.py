#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run EUROMOD on existing RURO draws (singles and optionally couples).

Usage example:
    python scripts/RURO_euromod.py \
      --singles-draws U:/EUROMOD-STORAGE/Data/processed/fr/2021/singles_RURO_ready_RURO_draws.parquet \
      --couples-draws U:/EUROMOD-STORAGE/Data/processed/fr/2021/couples_RURO_ready_RURO_draws.parquet \
      --microdata-template U:/EUROMOD-STORAGE/Data/raw/FR_2021_c2.txt \
      --euromod-root U:/EUROMOD-STORAGE/EUROMOD_RELEASES_J1.0+/EUROMOD_RELEASES_J1.0+ \
      --euromod-system FR_2020 \
      --euromod-dataset FR_2021_c2 \
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
    """
    scenario_dir = scenario_dir.resolve()
    scenario_dir.mkdir(parents=True, exist_ok=True)

    em_input = _read_microdata_file(micro_template_path)

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
    merged = em_input.merge(draws_sub, on=id_col, how="inner", suffixes=("", "_draw"))
    if merged.empty:
        raise ValueError("EUROMOD input after merging with draws is empty. Check id alignment.")

    if "idhh" in merged.columns:
        merged["idhh_true"] = merged["idhh"]
    merged[f"{id_col}_true"] = merged[id_col]

    draw = pd.to_numeric(merged["draw"], errors="coerce").fillna(0).astype(int)

    lma_raw = merged["lma"] if "lma" in merged.columns else pd.Series(1, index=merged.index)
    lma = pd.to_numeric(lma_raw, errors="coerce").fillna(1).astype(int)

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

    merged[hours_col] = h
    merged["hours"] = h

    base_w = pd.to_numeric(merged[wage_col], errors="coerce").fillna(0.0) if wage_col in merged.columns else w.copy()
    working_mask = (lma == 1) & (h > 0.0)
    merged[wage_col] = np.where(working_mask, w, base_w)
    merged["wage"] = merged[wage_col]

    if "yem" in merged.columns:
        yem = pd.to_numeric(merged["yem"], errors="coerce").fillna(0.0)
        yem.loc[working_mask] = h[working_mask] * merged.loc[working_mask, wage_col] * WEEKS_PER_MONTH
        merged["yem"] = yem

    if "bun" in merged.columns:
        bun = pd.to_numeric(merged["bun"], errors="coerce").fillna(0.0)
        bun.loc[working_mask] = 0.0
        merged["bun"] = bun

    if "bsa" in merged.columns:
        bsa = pd.to_numeric(merged["bsa"], errors="coerce").fillna(0.0)
        bsa.loc[working_mask] = 0.0
        merged["bsa"] = bsa

    if "yemmy" in merged.columns and "lunmy" in merged.columns:
        yemmy = pd.to_numeric(merged["yemmy"], errors="coerce")
        lunmy = pd.to_numeric(merged["lunmy"], errors="coerce")
        yemmy.loc[working_mask] = 12
        lunmy.loc[working_mask] = 0
        merged["yemmy"] = yemmy
        merged["lunmy"] = lunmy

    if "idhh" in merged.columns:
        merged["idhh"] = merged["idhh_true"] * 1000 + draw

    base_id = merged[f"{id_col}_true"]
    merged[id_col] = base_id * 1000 + draw

    for kin in ["idfather", "idmother", "idpartner"]:
        if kin in merged.columns:
            kin_old = pd.to_numeric(merged[kin], errors="coerce").fillna(0).astype(int)
            kin_new = np.where(kin_old == 0, 0, kin_old * 1000 + draw)
            merged[kin] = kin_new

    # sort for EUROMOD stability
    sort_cols = []
    if "idhh" in merged.columns:
        sort_cols.append("idhh")
    if id_col in merged.columns:
        sort_cols.append(id_col)
    if sort_cols:
        merged = merged.sort_values(sort_cols).reset_index(drop=True)

    runner = EuromodRunner(em_root)
    sim_df = runner.run_on_dataframe(merged, country=country, system_code=system_code, dataset_name=dataset_name)

    sim_df["draw"] = merged["draw"].values
    if "idhh_true" in merged.columns:
        sim_df["idhh_true"] = merged["idhh_true"].values
    sim_df[f"{id_col}_true"] = merged[f"{id_col}_true"].values

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

    combined_df = pd.concat(combined, axis=0, ignore_index=True)
    combined_df = combined_df.replace([np.inf, -np.inf], np.nan).dropna(subset=["draw", "idperson"])

    micro_path = Path(args.microdata_template).resolve()
    em_root = _euromod_root(args.euromod_root)
    scenario_dir = (
        args.scenario_dir.resolve()
        if args.scenario_dir
        else (_resolve_storage_root() / "interim" / "ruro" / args.euromod_system.split("_")[0].lower() / "scenarios")
    )

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
