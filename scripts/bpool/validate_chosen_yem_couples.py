"""
Couples-only earnings integrity check on is_chosen_joint==1 rows.

For each deciding partner on the chosen row, compare yem/yem00/yemxp/yivwg/lhw
to the observed canonical fr_20YY.parquet for the SAME person.

Read-only; no changes.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
import pandas as pd

_BPOOL = Path("U:/EUROMOD-STORAGE/new_data")
_FR = {
    2015: Path("Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2015/fr_2015.parquet"),
    2016: Path("Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016.parquet"),
    2017: Path("Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2017/fr_2017.parquet"),
}
VARS = ["yem", "yem00", "yemxp", "yivwg", "lhw"]
TOL = 1e-6

def summarize(year: int) -> None:
    print(f"\n===== {year} couples =====")
    pf = pd.read_parquet(
        _BPOOL / f"fr_p3a_bpool_priced__{year}__couples.parquet",
        columns=["idhh_true", "idperson_true", "is_chosen_joint",
                 "ruro_decider", "draw_joint", "dgn", "idhh", "idperson"]
                + VARS,
    )
    chosen = pf[(pf["is_chosen_joint"] == 1) & (pf["ruro_decider"] == 1)].copy()

    cf = pd.read_parquet(
        _FR[year],
        columns=["idhh", "idperson", "dgn"] + VARS,
    )
    cf = cf.rename(columns={v: v + "_obs" for v in VARS}).rename(columns={"dgn": "dgn_obs"})

    m = chosen.merge(
        cf, left_on=["idhh_true", "idperson_true"],
        right_on=["idhh", "idperson"], how="inner",
        suffixes=("", "_y"),
    )
    print(f"  n chosen deciders: {len(chosen):,}   n matched: {len(m):,}")

    # Split by gender (head=male=1 vs partner=female=2 in EU-SILC convention)
    for label, gval in [("male/head (dgn=1)", 1), ("female/partner (dgn=2)", 2)]:
        sub = m[m["dgn"] == gval]
        if len(sub) == 0:
            print(f"  {label}: (no rows)")
            continue
        print(f"  {label}: n={len(sub):,}")
        for v in VARS:
            d = (sub[v] - sub[v + "_obs"]).abs()
            n_neq = int((d > TOL).sum())
            pct = 100.0 * n_neq / len(sub)
            print(f"    {v:6}  max|Δ|={d.max():>12.4f}  med|Δ|={d.median():>10.4f}  "
                  f"n!=obs={n_neq:>5,}  ({pct:5.2f}%)")


def collision_test(year: int) -> None:
    """For 10 sample couples: does is_chosen_joint==1 row share stamped idhh with draw_joint==0 simulated row?"""
    print(f"\n----- collision test {year} couples -----")
    pf = pd.read_parquet(
        _BPOOL / f"fr_p3a_bpool_priced__{year}__couples.parquet",
        columns=["idhh", "idhh_true", "idperson_true", "is_chosen_joint",
                 "draw_joint", "ruro_decider", "dgn"],
    )
    # Sample 10 households (by idhh_true) that appear with is_chosen_joint==1
    chosen_hhs = pf[pf["is_chosen_joint"] == 1]["idhh_true"].unique()
    sample = pd.Series(chosen_hhs).sample(n=10, random_state=0).tolist()

    print(f"  {'idhh_true':>10} | {'chosen_stamped_idhh':>22}  {'draw0_stamped_idhh':>22}  same?")
    for hh in sample:
        rows = pf[pf["idhh_true"] == hh]
        chosen_idhh = rows[rows["is_chosen_joint"] == 1]["idhh"].iloc[0] if (rows["is_chosen_joint"] == 1).any() else None
        # The simulated cell at draw_joint=0 is in rows where is_chosen_joint==0 and draw_joint==0
        sim_d0 = rows[(rows["is_chosen_joint"] == 0) & (rows["draw_joint"] == 0)]
        d0_idhh = sim_d0["idhh"].iloc[0] if len(sim_d0) else None
        same = (chosen_idhh == d0_idhh) if (chosen_idhh is not None and d0_idhh is not None) else None
        print(f"  {hh:>10} | {str(chosen_idhh):>22}  {str(d0_idhh):>22}  {same}")


for y in (2015, 2016, 2017):
    summarize(y)
    collision_test(y)
