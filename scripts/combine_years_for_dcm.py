#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Combine DE scenario datasets (2014/2015/2016) into a single CPI-aligned panel
ready for DCM estimation (works with DCM1_boxcox.py and bio_boxcox.py).

Features:
- Reads per-year scenario outputs (same structure as your 2015 run).
- Adds year to IDs so repeated idhh/idperson don't collide across years.
- CPI-adjusts ALL 'consumption_*' columns to 2015 prices using the
  *income year* (2014->2013, 2015->2014, 2016->2015).
- Writes combined male/female wide files usable as --data-dir for estimators.

Inputs:
- Data location resolved by path_helpers.data_root()
- Default scenario folders: Data/processed/scenarios/DE_<year>/
- CPI source:
    (a) CSV via --cpi-file (columns: year,index), OR
    (b) inline JSON via --cpi-json '{"2013":..., "2014":..., "2015":...}', OR
    (c) fallback: no adjustment (factor=1) with a warning.

Outputs:
- Data/processed/scenarios/DE_2014_2016_combined/
    heads_wide_single_male_dcm.parquet
    heads_wide_single_female_dcm.parquet
    combine_meta.json
"""

from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np
import pandas as pd

from path_helpers import data_root, ensure_dir
try:
    # Optional helpers we added
    from path_helpers import DE_INCOME_YEAR  # type: ignore
except Exception:
    DE_INCOME_YEAR = {2014: 2013, 2015: 2014, 2016: 2015}

DEFAULT_YEARS = (2014, 2015, 2016)
BASE_CPI_YEAR = 2015

def _load_cpi_from_csv(csv_path: Path) -> Dict[int, float]:
    df = pd.read_csv(csv_path)
    # Expect columns: year, index  (index = CPI level; any scale is OK)
    c = {int(r["year"]): float(r["index"]) for _, r in df.iterrows()}
    return c

def _load_cpi(args) -> Dict[int, float]:
    # Priority: --cpi-json > --cpi-file > identity mapping
    if args.cpi_json:
        j = json.loads(args.cpi_json)
        return {int(k): float(v) for k, v in j.items()}
    if args.cpi_file and Path(args.cpi_file).exists():
        return _load_cpi_from_csv(Path(args.cpi_file))
    # Fallback: identity -> no adjustment, but warn
    print("[combine_years_for_dcm] WARNING: no CPI provided; using factor=1 for all years")
    return {}

def _income_year_for(micro_year: int) -> int:
    return DE_INCOME_YEAR.get(micro_year, micro_year)

def _cpi_factor(cpi: Dict[int, float], income_year: int, base_year: int) -> float:
    if not cpi:
        return 1.0
    if base_year not in cpi or income_year not in cpi:
        print(f"[combine_years_for_dcm] WARNING: missing CPI for {income_year} or {base_year}; factor=1")
        return 1.0
    return float(cpi[base_year]) / float(cpi[income_year])

def _unique_ids(df: pd.DataFrame, year: int) -> pd.DataFrame:
    out = df.copy()
    for col in ("idhh", "idperson"):
        if col in out.columns:
            # Preserve originals
            out[f"{col}_orig"] = out[col]
            # Keep ints if possible; otherwise make them ints safely
            base = pd.to_numeric(out[col], errors="coerce").fillna(0).astype(np.int64)
            out[col] = (year * 1_000_000 + base).astype(np.int64)
    out["panel_year"] = year
    return out

def _adjust_consumption_cols(df: pd.DataFrame, factor: float) -> pd.DataFrame:
    if factor == 1.0:
        return df
    out = df.copy()
    cons_cols = [c for c in out.columns if c.startswith("consumption_")]
    for c in cons_cols:
        out[c] = pd.to_numeric(out[c], errors="coerce") * factor
    return out

def _load_wide(dir_year: Path, gender: str) -> pd.DataFrame:
    # Your 2015-style filenames
    f = dir_year / f"heads_wide_single_{gender}_dcm.parquet"
    if not f.exists():
        raise FileNotFoundError(f"Missing wide file: {f}")
    return pd.read_parquet(f)

def _reorder_cols_for_dcm(df: pd.DataFrame) -> pd.DataFrame:
    # Bring key columns first; keep others unchanged
    first = [c for c in ("actual_choice","dag","num_children_total","DCH","dgn","idhh","idperson","panel_year") if c in df.columns]
    others = [c for c in df.columns if c not in first]
    return df[first + others]

def combine_years(years: Iterable[int], cpi: Dict[int, float], base_cpi_year: int, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    scenario_root = data_root() / "processed" / "scenarios"

    combined: Dict[str, List[pd.DataFrame]] = {"male": [], "female": []}
    meta_rows: List[Dict[str, object]] = []

    for y in years:
        year_dir = scenario_root / f"DE_{y}"
        if not year_dir.exists():
            raise FileNotFoundError(f"Scenario dir not found: {year_dir}")
        inc_y = _income_year_for(y)
        factor = _cpi_factor(cpi, inc_y, base_cpi_year)
        for g in ("male","female"):
            df = _load_wide(year_dir, g)
            df = _unique_ids(df, year=y)
            df = _adjust_consumption_cols(df, factor)
            df = _reorder_cols_for_dcm(df)
            combined[g].append(df)
            meta_rows.append({"year": y, "gender": g, "income_year": inc_y, "cpi_factor": factor, "rows": int(df.shape[0])})

    for g in ("male","female"):
        full = pd.concat(combined[g], ignore_index=True, sort=False)
        full.to_parquet(out_dir / f"heads_wide_single_{g}_dcm.parquet", index=False)

    meta = {
        "years": list(years),
        "base_cpi_year": base_cpi_year,
        "income_year_map": {int(k): int(v) for k, v in DE_INCOME_YEAR.items()},
        "rows": meta_rows,
        "output_dir": str(out_dir),
    }
    (out_dir / "combine_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return out_dir

def main():
    ap = argparse.ArgumentParser(description="Combine DE scenarios (2014/2015/2016) into one CPI-aligned panel for DCM.")
    ap.add_argument("--years", nargs="+", type=int, default=list(DEFAULT_YEARS))
    ap.add_argument("--base-cpi-year", type=int, default=BASE_CPI_YEAR)
    ap.add_argument("--cpi-file", type=str, default=None, help="CSV with columns: year,index")
    ap.add_argument("--cpi-json", type=str, default=None, help="Inline JSON mapping: {'2013':idx,'2014':idx,'2015':idx}")
    ap.add_argument("--out-name", type=str, default="DE_2014_2016_combined")
    args = ap.parse_args()

    cpi = _load_cpi(args)
    out_dir = data_root() / "processed" / "scenarios" / args.out_name
    combine_years(args.years, cpi, args.base_cpi_year, out_dir)
    print(f"[combine_years_for_dcm] Done -> {out_dir}")

if __name__ == "__main__":
    main()
