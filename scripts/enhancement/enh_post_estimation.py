#!/usr/bin/env python
"""
Enhanced wrapper for RURO_post_estimation (base untouched).
- Logs which enhanced features (region/year dummies, columns) are available via meta.
- Delegates to base run_post_estimation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

import scripts.RURO_post_estimation as base


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Enhanced post-estimation wrapper.")
    ap.add_argument("--results-file", type=Path, required=True, help="Estimation JSON file.")
    ap.add_argument("--mnl-file", type=Path, required=True, help="MNL parquet file.")
    ap.add_argument("--out-dir", type=Path, default=Path("outputs/post_estimation/enh"), help="Output directory.")
    return ap.parse_args()


def main() -> None:
    args = parse_args()

    meta_path = args.mnl_file.with_name(f"{args.mnl_file.stem}_meta.json")
    if meta_path.exists():
        try:
            meta = json.load(meta_path.open("r"))
            print(f"[META] use_region_dummies={meta.get('use_region_dummies')}, use_year_dummies={meta.get('use_year_dummies')}")
            if meta.get("years_present"):
                print(f"[META] years_present={meta.get('years_present')}")
            print(f"[META] mean_dispy_norm={meta.get('mean_dispy_norm')}, mean_lhw_norm={meta.get('mean_lhw_norm')}")
        except Exception as e:
            print(f"[META] Could not read meta: {e}")
    else:
        print("[META] No meta JSON found adjacent to MNL.")

    with args.results_file.open("r") as f:
        results = json.load(f)
    theta = np.array(results["theta"])
    param_names = results["param_names"]
    log_likelihood = results.get("log_likelihood", -results.get("fun", 0.0))
    wage_spec = results.get("wage_spec", "vw")
    n_individuals = results.get("n_individuals", 0)

    df = pd.read_parquet(args.mnl_file)
    group_col = "ruro_group" if "ruro_group" in df.columns else None
    df_sm = df[df[group_col] == 1].copy() if group_col and 1 in df[group_col].values else df.copy()
    df_cou = df[df[group_col] == 10].copy() if group_col and 10 in df[group_col].values else None
    df_sf = None  # singles pooled unless split available

    out = base.run_post_estimation(
        theta=theta,
        param_names=param_names,
        log_likelihood=log_likelihood,
        df_sm=df_sm,
        df_sf=df_sf,
        df_cou=df_cou,
        out_dir=args.out_dir,
        wage_spec=wage_spec,
        n_individuals=n_individuals,
    )
    print(f"[POST] HTML report: {out.get('html_report')}")


if __name__ == "__main__":
    main()
