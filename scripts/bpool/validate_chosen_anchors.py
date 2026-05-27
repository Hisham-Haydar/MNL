"""
Read-only triage: for chosen-row deciders only, separate three failure modes.

A. Participation anchor bug: chosen working-state != observed working-state.
B. Hours anchor bug:        among same-state workers, chosen lhw != observed lhw.
C. Layer-1 reconstruction:  among same-lhw rows, is yem_chosen == lhw*yivwg*(52/12)?
                            And how does that compare to observed survey yem (benign).

Definitions:
  working_obs    = (yem_obs > 0)         from canonical
  working_chosen = (yem_chosen > 0)      from priced chosen row
Tolerance: 1e-6 for exact float equality; lhw uses 1e-3 hours.

No changes; reports counts only.
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

TOL_LHW = 1e-3
TOL_YEM = 1.0    # euros for layer-1 reconstruction check
TOL_DIFF = 1e-6  # exact float comparisons

WEEKS_PER_MONTH = 52.0 / 12.0


def check_one(year: int, mode: str) -> dict:
    p = _BPOOL / f"fr_p3a_bpool_priced__{year}__{mode}.parquet"
    chosen_flag = "is_chosen" if mode == "singles" else "is_chosen_joint"
    pf = pd.read_parquet(p, columns=[
        "idhh_true", "idperson_true", chosen_flag, "ruro_decider",
        "yem", "yivwg", "lhw", "dgn",
    ])
    chosen = pf[(pf[chosen_flag] == 1) & (pf["ruro_decider"] == 1)].copy()
    chosen = chosen.rename(columns={"yem":"yem_ch", "yivwg":"yivwg_ch", "lhw":"lhw_ch"})

    cf = pd.read_parquet(_FR[year], columns=["idhh","idperson","yem","yivwg","lhw","dgn"])
    cf = cf.rename(columns={"yem":"yem_obs", "yivwg":"yivwg_obs", "lhw":"lhw_obs", "dgn":"dgn_obs"})

    m = chosen.merge(
        cf, left_on=["idhh_true","idperson_true"],
        right_on=["idhh","idperson"], how="inner",
    )
    n_match = len(m)

    # ---- A. participation anchor ----
    working_obs = m["yem_obs"] > 0
    working_ch  = m["yem_ch"]  > 0
    A_disagree  = int((working_obs != working_ch).sum())
    A_obs_nonw_ch_w = int(((~working_obs) & working_ch).sum())   # observed non-worker, chosen worker
    A_obs_w_ch_nonw = int((working_obs & (~working_ch)).sum())   # observed worker, chosen non-worker

    # ---- B. hours anchor (among rows where working-state matches) ----
    same_state = (working_obs == working_ch)
    workers    = same_state & working_obs & working_ch
    if workers.any():
        sub = m[workers]
        dlhw = (sub["lhw_ch"] - sub["lhw_obs"]).abs()
        B_mismatch = int((dlhw > TOL_LHW).sum())
        B_n_workers = int(workers.sum())
        B_max = float(dlhw.max())
        B_med = float(dlhw.median())
    else:
        B_mismatch = B_n_workers = 0
        B_max = B_med = float("nan")

    # ---- C. Layer-1 reconstruction: yem_ch ?= lhw_ch * yivwg_ch * 52/12 ----
    if workers.any():
        sub = m[workers].copy()
        same_lhw = (sub["lhw_ch"] - sub["lhw_obs"]).abs() <= TOL_LHW
        sub = sub[same_lhw]
        if len(sub) > 0:
            recon = sub["lhw_ch"] * sub["yivwg_ch"] * WEEKS_PER_MONTH
            d_recon = (sub["yem_ch"] - recon).abs()
            C_recon_n        = len(sub)
            C_recon_mismatch = int((d_recon > TOL_YEM).sum())
            C_recon_max      = float(d_recon.max())
            C_recon_med      = float(d_recon.median())

            # And: how far is the reconstruction from survey yem (benign divergence)
            d_survey = (sub["yem_ch"] - sub["yem_obs"]).abs()
            C_survey_n_over = int((d_survey > TOL_YEM).sum())
            C_survey_max    = float(d_survey.max())
            C_survey_med    = float(d_survey.median())
        else:
            C_recon_n = C_recon_mismatch = C_survey_n_over = 0
            C_recon_max = C_recon_med = C_survey_max = C_survey_med = float("nan")
    else:
        C_recon_n = C_recon_mismatch = C_survey_n_over = 0
        C_recon_max = C_recon_med = C_survey_max = C_survey_med = float("nan")

    return {
        "year": year, "mode": mode, "n_match": n_match,
        "A_disagree": A_disagree,
        "A_obs_nonw_ch_w": A_obs_nonw_ch_w,
        "A_obs_w_ch_nonw": A_obs_w_ch_nonw,
        "B_n_same_state_workers": B_n_workers,
        "B_lhw_mismatch": B_mismatch,
        "B_lhw_max_abs": B_max,
        "B_lhw_med_abs": B_med,
        "C_n_same_lhw_workers": C_recon_n,
        "C_recon_mismatch_gt1eur": C_recon_mismatch,
        "C_recon_max_abs": C_recon_max,
        "C_recon_med_abs": C_recon_med,
        "C_survey_gap_gt1eur": C_survey_n_over,
        "C_survey_gap_max": C_survey_max,
        "C_survey_gap_med": C_survey_med,
    }


def main() -> None:
    print("Chosen-row anchor triage — read-only\n")
    print(f"{'file':<14} {'n_match':>8} | "
          f"{'A_disagree':>11} {'(obs_nw->w)':>12} {'(obs_w->nw)':>12} | "
          f"{'B_workers':>10} {'B_lhw_mis':>10} {'B_max':>10}")
    print("-" * 102)
    rows = []
    for y in (2015, 2016, 2017):
        for mode in ("singles", "couples"):
            r = check_one(y, mode)
            rows.append(r)
            print(f"{r['year']}_{r['mode']:<7} {r['n_match']:>8,} | "
                  f"{r['A_disagree']:>11,} {r['A_obs_nonw_ch_w']:>12,} "
                  f"{r['A_obs_w_ch_nonw']:>12,} | "
                  f"{r['B_n_same_state_workers']:>10,} {r['B_lhw_mismatch']:>10,} "
                  f"{r['B_lhw_max_abs']:>10.4f}")
    print()
    print("Layer-1 reconstruction check (C): yem_ch ?= lhw_ch * yivwg_ch * 52/12 on same-lhw workers")
    print(f"{'file':<14} {'C_n':>8} {'recon_mis':>10} {'recon_max':>12} {'recon_med':>12} | "
          f"{'survey_gap_n':>14} {'survey_max':>12} {'survey_med':>12}")
    print("-" * 110)
    for r in rows:
        print(f"{r['year']}_{r['mode']:<7} {r['C_n_same_lhw_workers']:>8,} "
              f"{r['C_recon_mismatch_gt1eur']:>10,} {r['C_recon_max_abs']:>12.4f} "
              f"{r['C_recon_med_abs']:>12.4f} | "
              f"{r['C_survey_gap_gt1eur']:>14,} {r['C_survey_gap_max']:>12.2f} "
              f"{r['C_survey_gap_med']:>12.4f}")

    print()
    any_A = any(r["A_disagree"] > 0 for r in rows)
    any_B = any(r["B_lhw_mismatch"] > 0 for r in rows)
    print("VERDICT")
    print(f"  A (participation anchor): {'BUG' if any_A else 'OK'}")
    print(f"  B (hours anchor)        : {'BUG' if any_B else 'OK'}")
    print(f"  C (reconstruction)      : informational (yem_ch = lhw*yivwg*52/12; "
          f"survey gap is benign)")


if __name__ == "__main__":
    main()
