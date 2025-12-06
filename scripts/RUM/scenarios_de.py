#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build DE scenarios for a given micro-data year using the correct EUROMOD system year.
This reuses the same pipeline you used for 2015 and applies it to 2014 and 2016.
"""

from __future__ import annotations

import argparse
import json
import sys
import types
from pathlib import Path
from typing import Any

import pandas as pd

try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:
    SCRIPT_DIR = Path.cwd() / "scripts"
PROJECT_ROOT = SCRIPT_DIR.parent
for candidate in (PROJECT_ROOT, SCRIPT_DIR):
    candidate_str = str(candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

from path_helpers import data_root, reports_root, DE_DEFAULT_SYSTEMS

DATA_ROOT = data_root()
REPORTS_ROOT = reports_root()
_SCENARIOS_MODULE: types.ModuleType | None = None


def _load_scenarios_module() -> types.ModuleType:
    """Load scripts/scenarios.py without executing its interactive tail."""
    global _SCENARIOS_MODULE
    if _SCENARIOS_MODULE is not None:
        return _SCENARIOS_MODULE

    source_path = SCRIPT_DIR / "scenarios.py"
    if not source_path.exists():
        raise FileNotFoundError(f"Missing scenarios pipeline: {source_path}")

    source = source_path.read_text(encoding="utf-8")
    normalized = source.replace("\r\n", "\n")
    marker = 'if __name__ == "__main__":'
    idx = normalized.find(marker)
    if idx != -1:
        tail = normalized.find("\n#%%", idx)
        if tail != -1:
            normalized = normalized[:tail]
    module_name = "scenarios_dynamic"
    module = types.ModuleType(module_name)
    module.__file__ = str(source_path)
    sys.modules[module_name] = module
    exec(compile(normalized, str(source_path), "exec"), module.__dict__)
    _SCENARIOS_MODULE = module
    return module


def _stringify_meta(value: Any) -> Any:
    """Convert nested Paths to strings so they can be JSON-encoded."""
    if isinstance(value, dict):
        return {k: _stringify_meta(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_stringify_meta(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    return value


def build_scenarios_for_year(
    *,
    year: int,
    system_year: int | None = None,
    processed_dir: Path | None = None,
    out_dir: Path | None = None,
) -> Path:
    processed_dir = processed_dir or (DATA_ROOT / "processed" / "de" / str(year))
    if not processed_dir.exists():
        raise FileNotFoundError(f"Processed dir not found: {processed_dir}")

    out_dir = out_dir or (DATA_ROOT / "processed" / "scenarios" / f"DE_{year}")
    out_dir.mkdir(parents=True, exist_ok=True)

    if system_year is None:
        system_year = DE_DEFAULT_SYSTEMS.get(year, year)

    clean_file = processed_dir / f"de_{year}_clean.parquet"
    if not clean_file.exists():
        raise FileNotFoundError(f"Missing cleaned parquet: {clean_file}")
    clean_df = pd.read_parquet(clean_file)

    dataset_name = f"DE_{year}_a1"
    meta_path = processed_dir / "prep_meta.json"
    raw_path = None
    if meta_path.exists():
        prep_meta = json.loads(meta_path.read_text(encoding="utf-8"))
        raw_path = prep_meta.get("raw_path")
        dataset_name = prep_meta.get("dataset_name") or dataset_name
        if raw_path and not prep_meta.get("dataset_name"):
            dataset_name = Path(raw_path).stem

    scenarios_mod = _load_scenarios_module()
    scenarios_mod.DATA_DIR = DATA_ROOT
    scenarios_mod.PROCESSED_DIR = processed_dir
    scenarios_mod.SCENARIO_DIR = out_dir
    scenarios_mod.TARGET_SYSTEM = f"DE_{system_year}"
    scenarios_mod.TARGET_DATASET = dataset_name
    if hasattr(scenarios_mod, "ensure_dir"):
        scenarios_mod.ensure_dir(out_dir)

    context = scenarios_mod._prepare_euromod()
    results = scenarios_mod.run_all_scenarios(context=context)

    result_meta = _stringify_meta(results)
    meta = {
        "year": year,
        "system_year": system_year,
        "dataset_name": dataset_name,
        "processed_dir": str(processed_dir),
        "scenario_dir": str(out_dir),
        "clean_rows": int(clean_df.shape[0]),
        "clean_cols": int(clean_df.shape[1]),
        "raw_path": raw_path,
        "reports_root": str(REPORTS_ROOT),
        "results": result_meta,
    }
    (out_dir / "scenarios_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return out_dir


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Build DE scenarios for a given year.")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--system-year", type=int, default=None)
    parser.add_argument("--processed-dir", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args()
    build_scenarios_for_year(
        year=args.year,
        system_year=args.system_year,
        processed_dir=args.processed_dir,
        out_dir=args.out_dir,
    )


if __name__ == "__main__":
    _cli()
