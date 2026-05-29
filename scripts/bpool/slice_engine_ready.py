"""Slice the multi-year bpool engine-ready parquet into a single-year /
gender subset, producing a fresh `<base>__singles.parquet` (and matching
`__mnlmeta.json`) ready to feed enh_RURO_estimate_FR.py via --mnl-base.

Keeps the full per-HH alternative set (101 rows for singles, 901 for
couples) — filters by chosen-row's (year, dgn) and includes ALL rows for
the surviving households so the choice set is intact.

Usage:
  python scripts/bpool/slice_engine_ready.py \
      --src-base C:/Users/hisham/MNL/EUROMOD-STORAGE/new_data/fr_p3a_bpool_engine_ready \
      --out-base C:/Users/hisham/MNL/EUROMOD-STORAGE/new_data/fr_p3a_bpool_engine_ready_sm2016 \
      --household-type singles \
      --year 2016 \
      --dgn 1
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-base", required=True, help="Source --mnl-base stem (no extension)")
    ap.add_argument("--out-base", required=True, help="Output --mnl-base stem (no extension)")
    ap.add_argument("--household-type", choices=["singles", "couples"], required=True)
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--dgn", type=int, default=None,
                    help="Gender of decider (1=male, 0=female). Singles only; ignored for couples.")
    args = ap.parse_args()

    src = Path(args.src_base)
    out = Path(args.out_base)
    out.parent.mkdir(parents=True, exist_ok=True)

    src_pq = Path(f"{src}__{args.household_type}.parquet")
    if not src_pq.exists():
        raise SystemExit(f"Missing {src_pq}")
    print(f"Loading {src_pq.name}...")
    df = pd.read_parquet(src_pq)
    print(f"  rows={len(df):,}  cols={len(df.columns)}")

    # Find chosen rows in target slice; keep all rows for the surviving HHs.
    chosen = df[df["is_chosen"] == 1].copy()
    # Year column varies by household type: singles has `year`; couples has
    # `data_year` / `year_for_ruro` (same values). Pick whichever is present.
    year_col = "year" if "year" in chosen.columns else (
        "data_year" if "data_year" in chosen.columns else "year_for_ruro"
    )
    print(f"  using year column: {year_col!r}")
    sel = (chosen[year_col] == args.year)
    if args.household_type == "singles" and args.dgn is not None:
        sel &= (chosen["dgn"] == float(args.dgn))
    chosen_subset = chosen[sel]
    keep_hh = set(chosen_subset["idhh"].unique())
    print(f"  selected chosen rows: {len(chosen_subset)} (n_hh = {len(keep_hh)})")
    if len(keep_hh) == 0:
        raise SystemExit("No households match the slice. Check --year / --dgn.")

    sub = df[df["idhh"].isin(keep_hh)].copy()
    print(f"  slice rows: {len(sub):,} ({len(sub) / len(keep_hh):.0f} per HH)")

    # Write the slice and the (empty) couples / opposite parquet so --mnl-base
    # finds matching siblings. enh_RURO_estimate_FR will not estimate them
    # when --group is restricted.
    out_target = Path(f"{out}__{args.household_type}.parquet")
    sub.to_parquet(out_target, compression="snappy", index=False)
    print(f"  wrote {out_target}")

    # For the OTHER household type, write an empty stub with the original schema
    # so enh_RURO_estimate_FR doesn't error on the missing sibling file.
    other = "couples" if args.household_type == "singles" else "singles"
    other_src = Path(f"{src}__{other}.parquet")
    other_out = Path(f"{out}__{other}.parquet")
    if other_src.exists():
        print(f"  writing 0-row stub for {other_out.name} (schema preserved)")
        empty = pd.read_parquet(other_src).iloc[:0]
        empty.to_parquet(other_out, compression="snappy", index=False)

    # Copy the mnlmeta JSON straight across (annotate the slice provenance).
    meta_src = Path(f"{src}__mnlmeta.json")
    meta_out = Path(f"{out}__mnlmeta.json")
    if meta_src.exists():
        m = json.loads(meta_src.read_text(encoding="utf-8"))
        m["sliced_from"] = str(meta_src)
        m["slice_filter"] = {
            "household_type": args.household_type, "year": args.year, "dgn": args.dgn,
            "n_hh_kept": len(keep_hh), "n_rows_kept": int(len(sub)),
        }
        meta_out.write_text(json.dumps(m, indent=2), encoding="utf-8")
        print(f"  wrote {meta_out}")
    else:
        print(f"  WARNING: {meta_src} not found; skipping mnlmeta copy")

    print("Done.")


if __name__ == "__main__":
    main()
