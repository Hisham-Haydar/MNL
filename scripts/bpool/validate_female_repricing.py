"""
Couples-only diagnostic to distinguish:
  BUG A: female partner never repriced across draws (build-invalidating)
  BUG B: female was repriced but ruro_decider flag is missing (cosmetic)

Read-only across all 3 years.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
import pandas as pd

_BPOOL = Path("U:/EUROMOD-STORAGE/new_data")

def analyze_year(year: int) -> None:
    print(f"\n{'='*70}")
    print(f"YEAR {year}")
    print(f"{'='*70}")
    p = _BPOOL / f"fr_p3a_bpool_priced__{year}__couples.parquet"
    cols = ["idhh_true", "idperson_true", "is_chosen_joint", "draw_joint",
            "draw_male", "draw_female", "ruro_decider", "dgn", "idpartner",
            "yem", "yem00", "lhw", "idperson", "idhh"]
    df = pd.read_parquet(p, columns=cols)
    print(f"  total rows: {len(df):,}")
    print(f"  unique HHs: {df['idhh_true'].nunique():,}")

    # ============================================================
    # (1) ruro_decider × dgn breakdown
    # ============================================================
    print(f"\n  --- (1) ruro_decider==1 × dgn breakdown ---")
    dec = df[df["ruro_decider"] == 1]
    print(f"  total ruro_decider==1 rows: {len(dec):,}")
    print(f"  dgn values in full file: {sorted(df['dgn'].dropna().unique().tolist())}")
    print(f"\n  On chosen rows (is_chosen_joint==1):")
    ch_dec = dec[dec["is_chosen_joint"] == 1]
    print(f"    {ch_dec.groupby('dgn').size().to_dict()}")
    print(f"\n  On simulated rows (is_chosen_joint==0):")
    sim_dec = dec[dec["is_chosen_joint"] == 0]
    print(f"    {sim_dec.groupby('dgn').size().to_dict()}")

    # ============================================================
    # (2) Did female earnings vary across draws?
    # Identify female members. Strategy: for each HH, list its 2 adults
    # (rows where ruro_decider could apply, i.e. working-age). Use dgn.
    # ============================================================
    print(f"\n  --- (2) Does FEMALE yem vary across draw_joint? ---")
    print(f"  dgn value counts in this file: {df['dgn'].value_counts(dropna=False).to_dict()}")
    # In EU-SILC FR_2016: dgn=0 typically = female, dgn=1 = male. Confirm with canon.
    # Here we test both possibilities.
    for fcode, label in [(0, "dgn=0"), (2, "dgn=2")]:
        sub = df[df["dgn"] == fcode]
        if len(sub) == 0:
            print(f"    {label}: no rows")
            continue
        # Restrict to working-age adults (proxy: appears in many draws as ruro_decider candidate)
        # Just compute nunique(yem) across draw_joint per (idhh_true, idperson_true)
        gb = sub.groupby(["idhh_true", "idperson_true"])
        nun_yem = gb["yem"].nunique()
        nun_yem00 = gb["yem00"].nunique()
        n_draws = gb["draw_joint"].nunique()
        n_persons = len(nun_yem)
        print(f"    {label}: n_persons={n_persons:,}")
        print(f"      median nunique(yem)    across draws: {nun_yem.median():.1f}   (min={nun_yem.min()}, max={nun_yem.max()})")
        print(f"      median nunique(yem00)  across draws: {nun_yem00.median():.1f}   (min={nun_yem00.min()}, max={nun_yem00.max()})")
        print(f"      median nunique(draw_joint) per pers: {n_draws.median():.0f}")
        n_one = int((nun_yem == 1).sum())
        n_many = int((nun_yem > 1).sum())
        print(f"      persons with nunique(yem)==1: {n_one:,} ({100*n_one/n_persons:.1f}%)")
        print(f"      persons with nunique(yem) >1: {n_many:,} ({100*n_many/n_persons:.1f}%)")
        if n_many > 0:
            sample = nun_yem[nun_yem > 1].sample(min(3, n_many), random_state=0)
            print(f"      sample persons with varying yem (idhh_true, idperson_true) -> nunique(yem):")
            for k, v in sample.items():
                print(f"         {k} -> {v} unique yem values")

    # ============================================================
    # (3) Confirm female identification in long file
    # ============================================================
    print(f"\n  --- (3) How to identify the FEMALE in the long file? ---")
    # Show first 4 rows for 1 sample HH
    sample_hh = df["idhh_true"].dropna().iloc[0]
    rows = df[(df["idhh_true"] == sample_hh) & (df["draw_joint"] == 0) & (df["is_chosen_joint"] == 0)]
    print(f"  Sample HH idhh_true={sample_hh} at draw_joint=0 (simulated):")
    print(rows[["idperson_true", "dgn", "idpartner", "ruro_decider",
                "yem", "lhw", "draw_male", "draw_female"]].to_string(index=False))

    # ============================================================
    # (4) Cross-check: does draw_female actually vary the female's yem?
    # ============================================================
    print(f"\n  --- (4) Direct test: for one HH, female yem vs draw_female ---")
    rows_all = df[df["idhh_true"] == sample_hh]
    print(f"  Total rows for HH {sample_hh}: {len(rows_all)}")
    # Pick the row with dgn matching female - try both
    for fcode in [0, 2]:
        fem_rows = rows_all[(rows_all["dgn"] == fcode) & (rows_all["is_chosen_joint"] == 0)]
        if len(fem_rows) == 0:
            continue
        print(f"  Female candidate dgn={fcode}: {len(fem_rows)} simulated rows")
        # Group by draw_female; if female is repriced, yem should vary
        if "draw_female" in fem_rows.columns:
            yem_by_df = fem_rows.groupby("draw_female")["yem"].first()
            print(f"    yem at draw_female=0,1,2,...,5: {yem_by_df.head(6).tolist()}")
            print(f"    nunique(yem) across draw_female: {fem_rows['yem'].nunique()}")
            yem_by_dm = fem_rows.groupby("draw_male")["yem"].first()
            print(f"    yem at draw_male=0,1,2,...,5  : {yem_by_dm.head(6).tolist()}")


for year in (2015, 2016, 2017):
    analyze_year(year)

print(f"\n{'='*70}")
print("VERDICT:")
print("  If FEMALE nunique(yem) ~1 across draws -> BUG A (never repriced)")
print("  If FEMALE nunique(yem) ~30 across draw_female -> BUG B (flag-only)")
print(f"{'='*70}")
