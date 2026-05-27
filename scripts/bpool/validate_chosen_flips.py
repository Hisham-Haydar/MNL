"""
Read-only diagnostic: for the 280 chosen-row decider participation flips,
characterize WHY they flip (les vs yem/lhw disagreement, or unstructured).

Reports per year and overall:
  - Flip direction A1: obs-nonworker -> chosen-worker  (yem_obs==0, yem_chosen>0)
  - Flip direction A2: obs-worker    -> chosen-nonworker (yem_obs>0, yem_chosen==0)
For each direction, cross-tabulate les × (yem_obs sign) × (lhw_obs sign).
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

import numpy as np
import pandas as pd

from _bpool_paths import bpool_dir, FR_PARQUETS  # noqa: E402
_BPOOL = bpool_dir()
_FR    = FR_PARQUETS

# EUROMOD `les` codes per the DRD (authoritative):
#    0 Pre-school
#    1 Farmer
#    2 Employer or self-employed
#    3 Employee
#    4 Pensioner
#    5 Unemployed
#    6 Student
#    7 Inactive
#    8 Sick or Disabled
#    9 Other
#   10 Family worker
EMPLOYED_CODES = {1, 2, 3, 10}                # any earner status
UNEMP_INACTIVE = {0, 4, 5, 6, 7, 8, 9}        # non-earners


def collect_flips(year: int, mode: str) -> pd.DataFrame:
    chosen_flag = "is_chosen" if mode == "singles" else "is_chosen_joint"
    # 'working' is only present on singles files. Couples derive a per-row working
    # state from yem on the fly (working = yem > 0) which is what we actually want.
    requested = ["idhh_true", "idperson_true", chosen_flag, "ruro_decider",
                 "yem", "yivwg", "lhw", "dgn", "les",
                 "les_input", "les_orig", "les_enforced"]
    if mode == "singles":
        requested.append("working")
    pf = pd.read_parquet(
        _BPOOL / f"fr_p3a_bpool_priced__{year}__{mode}.parquet",
        columns=requested,
    )
    chosen = pf[(pf[chosen_flag] == 1) & (pf["ruro_decider"] == 1)].copy()
    rename_map = {"yem":"yem_ch", "yivwg":"yivwg_ch", "lhw":"lhw_ch", "les":"les_ch"}
    if mode == "singles":
        rename_map["working"] = "working_ch"
    chosen = chosen.rename(columns=rename_map)

    cf = pd.read_parquet(_FR[year],
        columns=["idhh","idperson","yem","yivwg","lhw","les","dgn"])
    cf = cf.rename(columns={
        "yem":"yem_obs","yivwg":"yivwg_obs","lhw":"lhw_obs","les":"les_obs","dgn":"dgn_obs",
    })

    m = chosen.merge(cf, left_on=["idhh_true","idperson_true"],
                     right_on=["idhh","idperson"], how="inner")

    working_obs = m["yem_obs"] > 0
    working_ch  = m["yem_ch"]  > 0
    flips = m[working_obs != working_ch].copy()
    flips["year"]      = year
    flips["mode"]      = mode
    flips["direction"] = np.where(
        (~working_obs.loc[flips.index]) & working_ch.loc[flips.index],
        "obs_nonw->ch_w",
        "obs_w->ch_nonw",
    )
    return flips


def main() -> None:
    print("Chosen-row participation flips — full attribution\n")
    all_flips = []
    for y in (2015, 2016, 2017):
        for mode in ("singles", "couples"):
            f = collect_flips(y, mode)
            all_flips.append(f)
            print(f"  {y} {mode:<7}: {len(f):>4} flips")
    flips = pd.concat(all_flips, ignore_index=True)
    print(f"\nTotal flips: {len(flips)}")
    print(f"  obs_nonw->ch_w : {(flips['direction']=='obs_nonw->ch_w').sum()}")
    print(f"  obs_w->ch_nonw : {(flips['direction']=='obs_w->ch_nonw').sum()}")

    # ---------- direction A1: obs nonworker -> chosen worker ----------
    print("\n" + "="*78)
    print("DIRECTION A1: obs nonworker -> chosen worker  (yem_obs==0 -> yem_ch>0)")
    print("="*78)
    A1 = flips[flips["direction"] == "obs_nonw->ch_w"]
    print(f"Total A1: {len(A1)}")
    print("\n  les_obs distribution:")
    print(A1["les_obs"].value_counts().sort_index().to_string())
    print("\n  les_ch  distribution:")
    print(A1["les_ch"].value_counts(dropna=False).sort_index().to_string())
    print("\n  (les_obs employed-like {1-4}) AND yem_obs==0:")
    emp_butzero = A1[A1["les_obs"].isin(EMPLOYED_CODES) & (A1["yem_obs"]==0)]
    print(f"    n = {len(emp_butzero)}  (employed les but zero observed earnings — recovered to working chosen)")
    print("\n  cross-tab les_obs × (lhw_obs>0):")
    A1["lhw_pos_obs"] = A1["lhw_obs"] > 0
    print(pd.crosstab(A1["les_obs"], A1["lhw_pos_obs"], margins=True).to_string())
    print("\n  cross-tab les_obs × les_ch (chosen-row les category, top combos):")
    ct = pd.crosstab(A1["les_obs"], A1["les_ch"])
    print(ct.to_string())
    # sample rows
    print("\n  sample A1 (10 rows):")
    print(A1[["year","mode","dgn","les_obs","yem_obs","lhw_obs","les_ch","yem_ch","lhw_ch"]]
          .head(10).to_string(index=False))

    # ---------- direction A2: obs worker -> chosen nonworker ----------
    print("\n" + "="*78)
    print("DIRECTION A2: obs worker -> chosen nonworker  (yem_obs>0 -> yem_ch==0)")
    print("="*78)
    A2 = flips[flips["direction"] == "obs_w->ch_nonw"]
    print(f"Total A2: {len(A2)}")
    print("\n  les_obs distribution:")
    print(A2["les_obs"].value_counts().sort_index().to_string())
    print("\n  les_ch  distribution:")
    print(A2["les_ch"].value_counts(dropna=False).sort_index().to_string())
    print("\n  (les_obs unemployed/inactive {5-10,0}) AND yem_obs>0:")
    nonemp_buty = A2[A2["les_obs"].isin(UNEMP_INACTIVE) & (A2["yem_obs"]>0)]
    print(f"    n = {len(nonemp_buty)}  (non-employed les but positive observed earnings — pushed to chosen=nonworker)")
    print("\n  cross-tab les_obs × (lhw_obs>0):")
    A2["lhw_pos_obs"] = A2["lhw_obs"] > 0
    print(pd.crosstab(A2["les_obs"], A2["lhw_pos_obs"], margins=True).to_string())
    print("\n  cross-tab les_obs × les_ch:")
    ct2 = pd.crosstab(A2["les_obs"], A2["les_ch"])
    print(ct2.to_string())
    # sample rows
    print("\n  sample A2 (10 rows):")
    print(A2[["year","mode","dgn","les_obs","yem_obs","lhw_obs","les_ch","yem_ch","lhw_ch"]]
          .head(10).to_string(index=False))

    # ---------- structural attribution ----------
    print("\n" + "="*78)
    print("STRUCTURAL ATTRIBUTION")
    print("="*78)
    # A1: definitional disagreement = les_obs employed AND yem_obs==0
    A1_def  = A1[A1["les_obs"].isin(EMPLOYED_CODES) & (A1["yem_obs"]==0)]
    A1_resid = len(A1) - len(A1_def)
    # A2: definitional = les_obs non-employed AND yem_obs>0
    A2_def  = A2[A2["les_obs"].isin(UNEMP_INACTIVE) & (A2["yem_obs"]>0)]
    A2_resid = len(A2) - len(A2_def)
    print(f"  A1 (obs_nonw->ch_w)   n={len(A1):>4}")
    print(f"     les-vs-yem defn disagreement (les employed, yem==0): {len(A1_def):>4}")
    print(f"     unstructured residual                                : {A1_resid:>4}")
    print(f"  A2 (obs_w->ch_nonw)   n={len(A2):>4}")
    print(f"     les-vs-yem defn disagreement (les non-employed, yem>0): {len(A2_def):>4}")
    print(f"     unstructured residual                                  : {A2_resid:>4}")
    total = len(flips)
    structural = len(A1_def) + len(A2_def)
    print(f"\n  TOTAL flips:        {total}")
    print(f"  structural (defn):   {structural}  ({100*structural/total:.1f}%)")
    print(f"  unstructured:        {total-structural}  ({100*(total-structural)/total:.1f}%)")
    print()
    print("VERDICT:")
    if structural / total >= 0.8:
        print("  -> Flips are driven by les-vs-yem definitional disagreement.")
        print("     The B-pool 'working' flag was set from les; the canonical 'working'")
        print("     test (yem>0) disagrees for these rows. NOT a build bug, but a")
        print("     definitional inconsistency that should be reconciled.")
    elif structural / total <= 0.2:
        print("  -> Flips are mostly unstructured; build pipeline bug.")
    else:
        print("  -> Flips are mixed: some definitional, some unstructured.")


if __name__ == "__main__":
    main()
