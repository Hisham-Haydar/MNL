"""
Read-only diagnostic: per-parent child counts from EUROMOD input microdata.

Replicates the upstream child-count derivation (enh_france_data_prep.py:1648-1727):
  child = household member with dag in [0,17]; attribute to father via idfather and
  mother via idmother; num_children_total = per-parent count.

Then, for COUPLE households, compares the male partner's count vs the female
partner's count, and against the single `n_children` carried into the estimation-ready
couples parquet (which upstream sets = mother's value).

Purpose: decide whether the female-only collapse (n_children = mother's count) is the
right modelling choice, or whether male/female counts diverge enough to warrant a
per-parent treatment.

NO changes; reports only.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

import numpy as np
import pandas as pd

from _bpool_paths import FR_PARQUETS, bpool_dir  # noqa: E402

_YEARS = (2015, 2016, 2017)


def per_parent_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Return DataFrame indexed by parent idperson -> num_children_total (dag 0-17)."""
    children_mask = df["dag"].between(0, 17)
    kids = df.loc[children_mask, ["idfather", "idmother"]].copy()
    father = kids.loc[(kids["idfather"].notna()) & (kids["idfather"] != 0), ["idfather"]]
    father = father.rename(columns={"idfather": "parent_id"})
    mother = kids.loc[(kids["idmother"].notna()) & (kids["idmother"] != 0), ["idmother"]]
    mother = mother.rename(columns={"idmother": "parent_id"})
    allp = pd.concat([father, mother], ignore_index=True)
    counts = allp.groupby("parent_id").size().rename("nchild_as_parent")
    return counts


def analyze_year(year: int) -> dict:
    df = pd.read_parquet(
        FR_PARQUETS[year],
        columns=["idhh", "idperson", "idmother", "idfather", "idpartner", "dag", "dgn"],
    )
    counts = per_parent_counts(df)

    # Attach per-person count (0 if person is nobody's parent)
    df = df.merge(counts, left_on="idperson", right_index=True, how="left")
    df["nchild_as_parent"] = df["nchild_as_parent"].fillna(0).astype(int)

    # Identify couple households: a HH containing a male (dgn=1) and female (dgn=0)
    # who are each other's partner (idpartner links). Restrict to adults dag>=18.
    adults = df[df["dag"] >= 18].copy()
    # Couple = HH where some person has a nonzero idpartner pointing within HH
    partnered = adults[(adults["idpartner"].notna()) & (adults["idpartner"] != 0)]
    couple_hhs = partnered["idhh"].unique()

    rows = []
    for hh in couple_hhs:
        members = adults[adults["idhh"] == hh]
        males = members[members["dgn"] == 1]
        females = members[members["dgn"] == 0]
        if len(males) == 0 or len(females) == 0:
            continue
        # take the partnered male & female (head + partner)
        m = males.iloc[0]
        f = females.iloc[0]
        rows.append({
            "idhh": hh,
            "male_id": m["idperson"], "male_nchild": int(m["nchild_as_parent"]),
            "female_id": f["idperson"], "female_nchild": int(f["nchild_as_parent"]),
        })
    cpl = pd.DataFrame(rows)
    if len(cpl) == 0:
        return {"year": year, "n_couples": 0}

    cpl["diff"] = (cpl["male_nchild"] - cpl["female_nchild"])
    n_diff = int((cpl["diff"] != 0).sum())
    n_male_more = int((cpl["diff"] > 0).sum())
    n_female_more = int((cpl["diff"] < 0).sum())

    return {
        "year": year,
        "n_couples": len(cpl),
        "male_nchild_mean": round(float(cpl["male_nchild"].mean()), 4),
        "female_nchild_mean": round(float(cpl["female_nchild"].mean()), 4),
        "n_diff": n_diff,
        "pct_diff": round(100.0 * n_diff / len(cpl), 2),
        "n_male_more": n_male_more,
        "n_female_more": n_female_more,
        "max_abs_diff": int(cpl["diff"].abs().max()),
        "diff_distribution": cpl["diff"].value_counts().sort_index().to_dict(),
        "_cpl": cpl,
    }


def main() -> None:
    print("Per-parent child-count diagnostic (children = dag 0-17, via idmother/idfather)\n")
    print(f"{'year':<6} {'n_couples':>10} {'male_mean':>10} {'female_mean':>12} "
          f"{'n_diff':>8} {'%diff':>7} {'M>F':>6} {'F>M':>6} {'maxabs':>7}")
    print("-" * 80)
    all_cpl = []
    for y in _YEARS:
        r = analyze_year(y)
        if r["n_couples"] == 0:
            print(f"{y:<6} (no couples found)")
            continue
        all_cpl.append(r.pop("_cpl").assign(year=y))
        print(f"{y:<6} {r['n_couples']:>10,} {r['male_nchild_mean']:>10} "
              f"{r['female_nchild_mean']:>12} {r['n_diff']:>8,} {r['pct_diff']:>6}% "
              f"{r['n_male_more']:>6,} {r['n_female_more']:>6,} {r['max_abs_diff']:>7}")
        print(f"        diff distribution (male - female): {r['diff_distribution']}")

    cpl = pd.concat(all_cpl, ignore_index=True)
    print("\n" + "=" * 80)
    print("POOLED (all 3 years)")
    print("=" * 80)
    n = len(cpl)
    nd = int((cpl["diff"] != 0).sum())
    print(f"  total couples: {n:,}")
    print(f"  male nchild mean:   {cpl['male_nchild'].mean():.4f}")
    print(f"  female nchild mean: {cpl['female_nchild'].mean():.4f}")
    print(f"  couples where male != female count: {nd:,} ({100*nd/n:.2f}%)")
    print(f"     male has MORE: {(cpl['diff']>0).sum():,}   female has MORE: {(cpl['diff']<0).sum():,}")
    print(f"  pooled diff distribution (male - female): {cpl['diff'].value_counts().sort_index().to_dict()}")

    # Compare against estimation n_children (= mother's value upstream)
    print("\n  Interpretation:")
    print("  - Upstream sets estimation n_children = MOTHER's (female) count.")
    print(f"  - For {100*nd/n:.1f}% of couples the father's count differs from the mother's.")
    if nd / n < 0.02:
        print("  => Divergence is negligible (<2%). Female-only collapse is defensible;")
        print("     male/female child counts coincide for ~all couples.")
    elif nd / n < 0.10:
        print("  => Modest divergence (2-10%). Female-only collapse loses some father-side")
        print("     variation but affects a small minority of couples.")
    else:
        print("  => Material divergence (>10%). Per-parent treatment would change the")
        print("     leisure shifter for a non-trivial share of couples; reconsider collapse.")


if __name__ == "__main__":
    main()
