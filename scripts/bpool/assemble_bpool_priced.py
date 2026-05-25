"""
Assembles chunk parquets produced by run_bpool_euromod_chunk.py into final
priced parquets and runs canary checks.

Usage:
    python assemble_bpool_priced.py

Reads chunks from U:/EUROMOD-STORAGE/new_data/chunks/
Writes final parquets to U:/EUROMOD-STORAGE/new_data/
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_BPOOL_DIR = Path("U:/EUROMOD-STORAGE/new_data")
_CHUNK_DIR = _BPOOL_DIR / "chunks"
_CPI = {2015: 1.0031, 2016: 1.0000, 2017: 0.9886}
_EM_OUTPUT_COLS = ["ils_dispy", "ils_origy", "ils_ben", "ils_tax", "ils_sicdy"]

_FR_PARQUET = {
    2015: Path("Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2015/fr_2015.parquet"),
    2016: Path("Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016.parquet"),
    2017: Path("Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2017/fr_2017.parquet"),
}

JOBS = [
    # (year, mode, n_chunks)
    (2017, "couples", 6),
    (2016, "singles", 1),
    (2016, "couples", 6),
    (2015, "singles", 1),
    (2015, "couples", 6),
]


def _run_canary(df: pd.DataFrame, year: int, mode: str) -> dict:
    results = {}
    draw_col = "draw" if mode == "singles" else "draw_joint"

    # C1: no nulls
    n_null = int(df["ils_dispy"].isna().sum())
    results["C1_nonull"] = {"n_null": n_null, "n_total": len(df), "pass": n_null == 0}

    # C2: non-work income
    if mode == "singles":
        nonwork = df[df.get("working", pd.Series(1, index=df.index)) == 0]
    else:
        nonwork = df[(df.get("working_male", pd.Series(1, index=df.index)) == 0) &
                     (df.get("working_female", pd.Series(1, index=df.index)) == 0)]
    if "ruro_decider" in df.columns and len(nonwork):
        nd = nonwork[nonwork["ruro_decider"] == 1]
        n_neg = int((nd["ils_dispy"] < 0).sum())
        med   = float(nd["ils_dispy"].median()) if len(nd) else float("nan")
        results["C2_nonwork_income"] = {
            "n_nonwork_decider_rows": len(nd),
            "n_neg_dispy": n_neg,
            "median_dispy": round(med, 2),
            "pass": (n_neg / max(len(nd), 1) < 0.05) and med > 0,
        }
    else:
        results["C2_nonwork_income"] = {"pass": None, "note": "cols absent"}

    # C3: internal consistency on chosen rows
    if draw_col in df.columns and "ruro_decider" in df.columns:
        if mode == "singles":
            chosen = df[df[draw_col] == 0]
        else:
            col = "is_chosen_joint"
            chosen = df[df[col] == 1] if col in df.columns else df[df[draw_col] == 0]
        dec = chosen[chosen["ruro_decider"] == 1] if "ruro_decider" in chosen.columns else chosen
        phi = _CPI[year]
        cpi_viol = int(((dec["ils_dispy_real"] - dec["ils_dispy"] * phi).abs() > 1e-6).sum()) if "ils_dispy_real" in dec.columns else 0
        if "working" in dec.columns and "yem" in dec.columns:
            wk = dec[dec["working"] == 1]
            corr = float(wk["yem"].corr(wk["ils_dispy"])) if len(wk) > 5 else float("nan")
            nw_med = float(dec[dec["working"] == 0]["ils_dispy"].median()) if (dec["working"] == 0).any() else float("nan")
        else:
            corr, nw_med = float("nan"), float("nan")
        results["C3_consistency"] = {
            "cpi_violations": cpi_viol,
            "corr_yem_dispy": round(corr, 4) if not np.isnan(corr) else None,
            "median_nonwork_dispy": round(nw_med, 2) if not np.isnan(nw_med) else None,
            "pass": cpi_viol == 0 and (np.isnan(corr) or corr > 0) and (np.isnan(nw_med) or nw_med > 0),
        }
    else:
        results["C3_consistency"] = {"pass": None, "note": "cols absent"}

    return results


def assemble_one(year: int, mode: str, n_chunks: int) -> dict:
    print(f"\n{'='*60}")
    print(f"ASSEMBLING {year} {mode} ({n_chunks} chunks)")
    print(f"{'='*60}")

    parts = []
    for ci in range(n_chunks):
        cp = _CHUNK_DIR / f"fr_p3a_bpool_priced__{year}__{mode}__c{ci}.parquet"
        if not cp.exists():
            raise FileNotFoundError(f"Missing chunk: {cp}")
        part = pd.read_parquet(cp)
        print(f"  chunk {ci}: {part.shape}")
        parts.append(part)

    # Concatenate in draw order. Chunks are already ordered (c0=draws[0,150), c1=[150,300), ...)
    # and within each chunk the original HH order from the long file is preserved, so no global
    # sort is needed - skipping it avoids a ~28 GB deep copy on couples files.
    df = pd.concat(parts, ignore_index=True)
    print(f"  Assembled: {df.shape}")

    # Canary
    canary = _run_canary(df, year, mode)
    all_c = True
    for k, v in canary.items():
        p = v.get("pass")
        if hasattr(p, "item"):
            p = p.item()
        status = "PASS" if p is True else ("FAIL" if p is False else "SKIP")
        if p is False:
            all_c = False
        print(f"    {status} {k}: {v}")

    # Write final parquet
    out_path = _BPOOL_DIR / f"fr_p3a_bpool_priced__{year}__{mode}.parquet"
    df.to_parquet(out_path, index=False)
    print(f"  Written: {out_path}  shape={df.shape}")

    return {
        "year": year, "mode": mode, "n_rows": len(df),
        "canary": canary, "canary_pass": all_c,
    }


def main() -> None:
    summary = {"files": {}}
    all_pass = True

    for year, mode, n_chunks in JOBS:
        out_path = _BPOOL_DIR / f"fr_p3a_bpool_priced__{year}__{mode}.parquet"
        if out_path.exists():
            print(f"Skipping {year} {mode} — already assembled: {out_path.name}")
            continue
        try:
            meta = assemble_one(year, mode, n_chunks)
            summary["files"][f"{year}_{mode}"] = meta
            all_pass &= meta["canary_pass"]
        except Exception as e:
            print(f"ERROR assembling {year} {mode}: {e}")
            summary["files"][f"{year}_{mode}"] = {"error": str(e)}
            all_pass = False

    summary["all_pass"] = all_pass
    meta_path = _BPOOL_DIR / "fr_p3a_bpool_priced__meta.json"
    with open(meta_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nSummary written: {meta_path}")
    if all_pass:
        print("ALL FILES ASSEMBLED AND CANARY PASSED")
    else:
        print("SOME FILES FAILED — review summary")
        sys.exit(1)


if __name__ == "__main__":
    main()
