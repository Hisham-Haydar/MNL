#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Re-run FR 2021 preparation with EUROMOD system-year 2020.
"""

from __future__ import annotations

from pathlib import Path

from data_prep2 import prepare_one_year
from path_helpers import euromod_raw_root


def main() -> None:
    country = "FR"
    year = 2021
    system_year = 2020
    raw_filename = "FR_2021_c2.txt"

    raw_dir = euromod_raw_root()

    out_dir, meta = prepare_one_year(
        country=country,
        year=year,
        raw_filename=raw_filename,
        system_year=system_year,
        raw_dir=raw_dir,
        out_dir=None,   # will resolve to U:\EUROMOD-STORAGE\Data\processed\fr\2021
    )

    print("FR 2021 prepared with system-year 2020.")
    print("Output dir:", out_dir)
    print("Meta:", meta)


if __name__ == "__main__":
    main()
