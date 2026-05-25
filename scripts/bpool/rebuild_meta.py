"""Rebuilds fr_p3a_bpool_priced__meta.json by running canary on all 6 final parquets."""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from assemble_bpool_priced import _run_canary, _BPOOL_DIR

JOBS = [
    (2015, "singles"), (2015, "couples"),
    (2016, "singles"), (2016, "couples"),
    (2017, "singles"), (2017, "couples"),
]

summary = {"files": {}}
all_pass = True
for year, mode in JOBS:
    p = _BPOOL_DIR / f"fr_p3a_bpool_priced__{year}__{mode}.parquet"
    if not p.exists():
        print(f"MISSING {p.name}")
        all_pass = False
        continue
    print(f"Reading {p.name} ...")
    df = pd.read_parquet(p)
    canary = _run_canary(df, year, mode)
    file_pass = True
    for k, v in canary.items():
        pv = v.get("pass")
        if hasattr(pv, "item"):
            pv = pv.item()
        status = "PASS" if pv is True else ("FAIL" if pv is False else "SKIP")
        if pv is False:
            file_pass = False
        print(f"    {status} {k}: {v}")
    summary["files"][f"{year}_{mode}"] = {
        "year": year, "mode": mode, "n_rows": len(df),
        "canary": canary, "canary_pass": file_pass,
    }
    if not file_pass:
        all_pass = False

summary["all_pass"] = all_pass
out = _BPOOL_DIR / "fr_p3a_bpool_priced__meta.json"
with open(out, "w") as f:
    json.dump(summary, f, indent=2, default=str)
print(f"\nWritten: {out}")
print(f"ALL PASS: {all_pass}")
