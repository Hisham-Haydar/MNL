#!/usr/bin/env python
"""
Enhanced wrapper for RURO_prep_mnl_basic (keeps base untouched)
---------------------------------------------------------------

- Country/year agnostic; only adds richer derived features after base prep.
- Optional normalization/country/year flags (metadata only).
- Writes a meta JSON with available columns and provided hints.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Ensure base scripts are importable when run directly
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import RURO_prep_mnl_basic as base


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enhanced wrapper for RURO_prep_mnl_basic (post-process only).",
        add_help=False,
    )
    parser.add_argument("--mean-dispy-norm", type=float, default=None)
    parser.add_argument("--mean-lhw-norm", type=float, default=None)
    parser.add_argument("--country", type=str, default=None)
    parser.add_argument("--year", type=str, default=None)
    parser.add_argument("--use-region-dummies", action="store_true", default=True)
    parser.add_argument("--use-year-dummies", action="store_true", default=False)

    args, forward_args = parser.parse_known_args()

    if args.mean_dispy_norm is not None:
        os.environ["RURO_MEAN_DISPY_NORM"] = str(args.mean_dispy_norm)
    if args.mean_lhw_norm is not None:
        os.environ["RURO_MEAN_LHW_NORM"] = str(args.mean_lhw_norm)
    if args.country:
        os.environ["RURO_COUNTRY"] = args.country
    if args.year:
        os.environ["RURO_YEAR"] = args.year

    out_base: Path | None = None
    for i, tok in enumerate(forward_args):
        if tok == "--out-base" and i + 1 < len(forward_args):
            out_base = Path(forward_args[i + 1]).resolve()
            break

    sys.argv = [sys.argv[0]] + forward_args
    base.main()

    try:
        if out_base is None:
            return
        parquet_path = out_base.with_suffix(".parquet")
        if not parquet_path.exists():
            return

        df = base.pd.read_parquet(parquet_path)  # type: ignore[attr-defined]

        if "dag" in df.columns:
            dag = base.pd.to_numeric(df["dag"], errors="coerce")
            dag = dag.clip(lower=1e-6)
            df["log_age"] = base.np.log(dag)
            df["log_age2"] = df["log_age"] ** 2

        for col in ["children0_3", "children4_6", "children7_9"]:
            if col not in df.columns and "n_children" in df.columns:
                df[col] = base.np.nan

        if args.use_region_dummies and "drgn1" in df.columns:
            dr = base.pd.to_numeric(df["drgn1"], errors="coerce").fillna(0).astype(int)
            regions = sorted(r for r in dr.unique() if base.np.isfinite(r))
            for r in regions:
                if r == 1:
                    continue
                df[f"drgn1_{r}"] = (dr == r).astype(int)

        years_present = []
        if args.use_year_dummies:
            if "year" not in df.columns and "ddt" in df.columns:
                try:
                    df["year"] = base.pd.to_numeric(df["ddt"].astype(str).str.slice(-4), errors="coerce")
                except Exception:
                    df["year"] = base.np.nan
            if "year" in df.columns:
                years = sorted(y for y in df["year"].dropna().unique())
                years_present = [int(y) for y in years]
                for y in years:
                    df[f"year_{int(y)}"] = (df["year"] == y).astype(int)

        df.to_parquet(parquet_path, index=False)

        # Compute normalization hints from observed choices if available
        mean_dispy_norm = args.mean_dispy_norm
        mean_lhw_norm = args.mean_lhw_norm
        try:
            obs_mask = None
            if "is_chosen" in df.columns:
                obs_mask = df["is_chosen"] == 1
            elif "draw" in df.columns:
                obs_mask = df["draw"] == 0
            if obs_mask is not None:
                if mean_dispy_norm is None:
                    if "ils_dispy" in df.columns:
                        mean_dispy_norm = base.pd.to_numeric(df.loc[obs_mask, "ils_dispy"], errors="coerce").mean()
                    elif "dispy_util" in df.columns:
                        mean_dispy_norm = base.pd.to_numeric(df.loc[obs_mask, "dispy_util"], errors="coerce").mean()
                if mean_lhw_norm is None:
                    if "lhw" in df.columns:
                        mean_lhw_norm = base.pd.to_numeric(df.loc[obs_mask, "lhw"], errors="coerce").mean()
                    elif "hours" in df.columns:
                        hrs = base.pd.to_numeric(df.loc[obs_mask, "hours"], errors="coerce")
                        mean_lhw_norm = hrs.mean()
                    elif "hours_male" in df.columns and "hours_female" in df.columns:
                        hrs_m = base.pd.to_numeric(df.loc[obs_mask, "hours_male"], errors="coerce")
                        hrs_f = base.pd.to_numeric(df.loc[obs_mask, "hours_female"], errors="coerce")
                        mean_lhw_norm = base.np.nanmean(base.np.concatenate([hrs_m.values, hrs_f.values]))
        except Exception:
            pass

        meta = {
            "columns": sorted(df.columns.tolist()),
            "mean_dispy_norm": mean_dispy_norm,
            "mean_lhw_norm": mean_lhw_norm,
            "country": args.country,
            "year": args.year,
            "use_region_dummies": args.use_region_dummies,
            "use_year_dummies": args.use_year_dummies,
            "years_present": years_present,
        }
        meta_path = out_base.parent / f"{out_base.name}_meta.json"
        with meta_path.open("w") as f:
            json.dump(meta, f, indent=2)
    except Exception as e:
        print(f"[WARN] Post-processing enhanced MNL failed: {e}")


if __name__ == "__main__":
    main()
