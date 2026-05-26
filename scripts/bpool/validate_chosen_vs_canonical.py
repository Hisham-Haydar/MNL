"""
Cross-check that the priced B-pool's CHOSEN row reproduces the canonical
fr_20YY.parquet ils_dispy for the same household (decider rows only).

Read-only. Reports per file:
    n_matched, max |Δ|, median |Δ|, count(|Δ|>1 €), PASS/FAIL.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
import pandas as pd

from _bpool_paths import bpool_dir, FR_PARQUETS  # noqa: E402
_BPOOL_DIR  = bpool_dir()
_FR_PARQUET = FR_PARQUETS
FILES = [(y, m) for y in (2015, 2016, 2017) for m in ("singles", "couples")]

TOL = 1.0  # euros

def check_one(year: int, mode: str) -> dict:
    p_priced = _BPOOL_DIR / f"fr_p3a_bpool_priced__{year}__{mode}.parquet"
    p_canon  = _FR_PARQUET[year]

    # Pick chosen rows + decider only from priced parquet
    chosen_flag = "is_chosen" if mode == "singles" else "is_chosen_joint"
    cols_priced = ["idhh_true", "idperson_true", chosen_flag,
                   "ruro_decider", "ils_dispy"]
    pf = pd.read_parquet(p_priced, columns=cols_priced)
    chosen = pf[(pf[chosen_flag] == 1) & (pf["ruro_decider"] == 1)].copy()
    chosen = chosen.rename(columns={"ils_dispy": "ils_dispy_priced"})

    # Canonical decider rows (match on idhh, idperson)
    cf = pd.read_parquet(p_canon, columns=["idhh", "idperson", "ils_dispy"])
    cf = cf.rename(columns={"ils_dispy": "ils_dispy_canon"})

    # Join on (idhh_true == idhh) AND (idperson_true == idperson)
    merged = chosen.merge(
        cf,
        left_on=["idhh_true", "idperson_true"],
        right_on=["idhh", "idperson"],
        how="inner",
    )

    n_chosen = len(chosen)
    n_match  = len(merged)
    diff     = (merged["ils_dispy_priced"] - merged["ils_dispy_canon"]).abs()
    max_d    = float(diff.max()) if n_match else float("nan")
    med_d    = float(diff.median()) if n_match else float("nan")
    n_over   = int((diff > TOL).sum())
    p_over   = 100.0 * n_over / max(n_match, 1)
    status   = "PASS" if (n_match > 0 and max_d <= TOL) else "FAIL"

    return {
        "file": f"{year}_{mode}",
        "n_chosen_deciders": n_chosen,
        "n_matched": n_match,
        "max_abs_diff": max_d,
        "median_abs_diff": med_d,
        "n_over_1eur": n_over,
        "pct_over_1eur": round(p_over, 3),
        "status": status,
    }

print(f"{'file':<14} {'n_chosen':>10} {'n_match':>10} {'max|Δ|':>12} {'med|Δ|':>12} {'n>1€':>10} {'pct':>8}  status")
print("-" * 100)
rows = []
all_pass = True
for y, m in FILES:
    r = check_one(y, m)
    rows.append(r)
    print(f"{r['file']:<14} {r['n_chosen_deciders']:>10,} {r['n_matched']:>10,} "
          f"{r['max_abs_diff']:>12.4f} {r['median_abs_diff']:>12.4f} "
          f"{r['n_over_1eur']:>10,} {r['pct_over_1eur']:>7}% {r['status']:>6}")
    if r["status"] != "PASS":
        all_pass = False

print("-" * 100)
print(f"OVERALL: {'PASS' if all_pass else 'FAIL'}")
