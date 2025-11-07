#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run DE prep + scenarios for selected years with correct EUROMOD system-year mapping.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:
    SCRIPT_DIR = Path.cwd() / "scripts"
PROJECT_ROOT = SCRIPT_DIR.parent
for candidate in (PROJECT_ROOT, SCRIPT_DIR):
    candidate_str = str(candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

from path_helpers import euromod_raw_root, DE_DEFAULT_SYSTEMS
from data_prep2 import prepare_one_year
from scenarios_de import build_scenarios_for_year


def _default_files() -> dict[int, str]:
    # year -> raw file name
    return {
        2014: "DE_2014_a3.txt",
        2015: "DE_2015_a1.txt",
        2016: "DE_2016_a1.txt",
    }


def _parse_sequence(values: Sequence[int] | None, fallback: Sequence[int]) -> Sequence[int]:
    return tuple(values) if values else tuple(fallback)


def main() -> None:
    ap = argparse.ArgumentParser(description="DE multi-year pipeline (prep + scenarios).")
    ap.add_argument("--years", nargs="+", type=int, default=[2014, 2015, 2016])
    ap.add_argument("--files", nargs="+", default=None,
                    help="List matching --years: e.g. DE_2014_a3.txt DE_2015_a1.txt DE_2016_a1.txt")
    ap.add_argument("--raw-dir", type=Path, default=None,
                    help="EUROMOD raw dir (default: env EUROMOD_RAW or U:\\EUROMOD-STORAGE\\Data\\raw)")
    ap.add_argument("--systems", nargs="+", type=int, default=None,
                    help="Optional explicit system-year list matching --years")
    args = ap.parse_args()

    years = _parse_sequence(args.years, (2014, 2015, 2016))
    raw_dir = args.raw_dir or euromod_raw_root()
    mapping_files = _default_files()
    if args.files:
        if len(args.files) != len(years):
            raise SystemExit("--files must match --years in length")
        mapping_files = {y: f for y, f in zip(years, args.files)}

    systems: dict[int, int] = {}
    if args.systems:
        if len(args.systems) != len(years):
            raise SystemExit("--systems must match --years in length")
        systems = {y: s for y, s in zip(years, args.systems)}

    for y in years:
        if y not in mapping_files:
            raise SystemExit(f"No raw file mapping provided for year {y}")
        raw_file = mapping_files[y]
        sys_y = systems.get(y, DE_DEFAULT_SYSTEMS.get(y, y))
        out_dir, _meta = prepare_one_year(
            country="DE",
            year=y,
            raw_filename=raw_file,
            system_year=sys_y,
            raw_dir=raw_dir,
            out_dir=None,
        )
        build_scenarios_for_year(year=y, system_year=sys_y, processed_dir=out_dir, out_dir=None)

    print("Done.")


if __name__ == "__main__":
    main()
