"""
Build theta_star CSV for joint_pooled_v1 recovery test from Step 3 slice estimates.

Assembles the 49-parameter DGP anchor by:
  - Group-specific preference params: taken from the slice that identifies each block
    (sm from sm2016, sf from sf2016_FIXED, couples from c2016_warm)
  - Shared market/hours/wage/occupation params: precision-weighted average across
    the slices that identified them (couples for region/year/urban; shared for hours/wage)
  - Occupation: sm/_cm -> _m average; sf/_cf -> _f average

Output: scripts/bpool/specs/theta_star_joint_v1.csv  (parameter,value)
Usage:  python build_joint_theta_star.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

_STORE = Path(r"C:\Users\hisham\MNL\EUROMOD-STORAGE")
_EST_DIR = _STORE / "outputs" / "estimation" / "realdata_2016"
_OUT = Path(__file__).parent / "specs" / "theta_star_joint_v1.csv"


def _load(run_dir: str) -> dict:
    p = _EST_DIR / run_dir / "estimation_spec_bpool_p3a_v1" / "estimation_results.json"
    with open(p) as f:
        j = json.load(f)
    # results key is the group name, get the first (only) entry's parameters
    for v in j["results"].values():
        return v["parameters"]
    raise ValueError(f"No results in {p}")


def main():
    sm  = _load("sm2016_conopt_cold")
    sf  = _load("sf2016_conopt_warm_FIXED")
    cou = _load("c2016_conopt_warm")

    out = {}

    # -------------------------------------------------------------------------
    # Group-specific preference params (each from its own identified slice)
    # -------------------------------------------------------------------------
    for p in ["beta_l0_sm", "beta_l_age_sm", "beta_l_age2_sm", "theta_l_sm"]:
        out[p] = sm[p]
    for p in ["beta_l0_sf", "beta_l_age_sf", "beta_l_age2_sf",
              "beta_l_nkids_sf", "theta_l_sf"]:
        out[p] = sf[p]
    out["theta_c_singles"] = 0.5 * (sm["theta_c_singles"] + sf["theta_c_singles"])

    for p in ["beta_l0_m", "beta_l_age_m", "beta_l_age2_m", "theta_l_m"]:
        out[p] = cou[p]
    for p in ["beta_l0_f", "beta_l_age_f", "beta_l_age2_f",
              "beta_l_nkids_f", "theta_l_f"]:
        out[p] = cou[p]

    # beta_ll: force to 2.0 — the couples 2016 slice had it inert at bound 0.0,
    # but the DGP theta_star must be interior so the recovery test can diagnose
    # whether pooled identification moves it off the bound.
    out["beta_ll"] = 2.0

    # -------------------------------------------------------------------------
    # Hours opportunity: average sm + sf + couples (all three active)
    # -------------------------------------------------------------------------
    for p in ["beta_E", "beta_h_pt1", "beta_h_pt2", "beta_h_ft", "beta_h_lh"]:
        out[p] = (sm[p] + sf[p] + cou[p]) / 3.0

    # -------------------------------------------------------------------------
    # Market opportunity: couples identifies region/urban (sm/sf inert at 0);
    # use couples values directly; gsur is identified on all three — average
    # -------------------------------------------------------------------------
    out["beta_E_gsur"] = (sm["beta_E_gsur"] + sf["beta_E_gsur"]
                          + cou["beta_E_gsur"]) / 3.0
    for p in ["beta_E_drgn2", "beta_E_drgn3", "beta_E_drgn4", "beta_E_drgn5",
              "beta_E_drgn6", "beta_E_drgn7", "beta_E_drgn8",
              "beta_E_drgur", "beta_E_drgmd"]:
        out[p] = cou[p]
    # year shifters: inert on every 2016 single-year slice (all zero); use
    # small non-zero values as the DGP signal so the joint pool can identify them
    out["beta_E_y2015"] = 0.10
    out["beta_E_y2017"] = -0.10

    # -------------------------------------------------------------------------
    # Occupation: collapse sm/_cm -> _m, sf/_cf -> _f
    # -------------------------------------------------------------------------
    for k in [2, 3, 4]:
        sm_val  = sm.get(f"beta_occ_{k}_sm", 0.0)
        cm_val  = cou.get(f"beta_occ_{k}_cm", 0.0)
        sf_val  = sf.get(f"beta_occ_{k}_sf", 0.0)
        cf_val  = cou.get(f"beta_occ_{k}_cf", 0.0)
        # Collapse: average of the two marital-status blocks within gender.
        # If the couples block was inert (0.0), use the singles value only.
        out[f"beta_occ_{k}_m"] = (sm_val + cm_val) / 2.0 if cm_val != 0.0 else sm_val
        out[f"beta_occ_{k}_f"] = (sf_val + cf_val) / 2.0 if cf_val != 0.0 else sf_val

    # -------------------------------------------------------------------------
    # Wage technology: average all three
    # -------------------------------------------------------------------------
    for p in ["beta_w0", "beta_w_educL", "beta_w_educH",
              "beta_w_pexp", "beta_w_pexp2", "sigma"]:
        out[p] = (sm[p] + sf[p] + cou[p]) / 3.0

    # -------------------------------------------------------------------------
    # Write CSV
    # -------------------------------------------------------------------------
    rows = [{"parameter": k, "value": v} for k, v in out.items()]
    df = pd.DataFrame(rows)
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(_OUT, index=False)
    print(f"Written {len(df)} params to {_OUT}")

    # Sanity: check all 49 joint spec params are covered
    spec_path = Path(__file__).parent / "specs" / "estimation_spec_joint_pooled_v1.yaml"
    if spec_path.exists():
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "enhanced"))
        import estimation_spec_parser as sp
        spec = sp.parse_specification(spec_path)
        missing = [n for n in spec.all_param_names if n not in out]
        extra   = [n for n in out if n not in spec.all_param_names]
        print(f"Spec params:  {len(spec.all_param_names)}")
        print(f"CSV params:   {len(out)}")
        print(f"Missing from CSV: {missing}")
        print(f"Extra in CSV (ignored): {extra}")
        if not missing:
            print("ALL 49 PARAMS PRESENT — theta_star CSV is ready")
    print("\nPreview:")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
