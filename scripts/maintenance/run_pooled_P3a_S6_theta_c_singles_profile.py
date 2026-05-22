"""
S6 LL profile in theta_c_singles at the saved corrected theta.

Vary only theta_c_singles around its converged value, hold all other
coordinates fixed, evaluate the joint negative log-likelihood via the
existing likelihood code.  Deterministic, no optimization.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(r"\\crc\users\hisham\Desktop\Nizam_Hisham\MNL")
sys.path.insert(0, str(REPO / "scripts" / "enhanced"))

from estimation_spec_parser import parse_specification
from estimation_engine import compute_likelihood_joint
from estimation_utils import load_and_validate_mnl_data, precompute_data_singles, precompute_data_couples
from run_cluster_robust_se import _collect_extra_vars


def main():
    se_json_path = REPO / "Results" / "JMP_pooled_P3a_corrected_start1_cluster_robust_se.json"
    spec_path = REPO / "scripts" / "enhanced" / "specifications" / "estimation_spec_ruro_occ_P3a_pooled.yaml"
    mnl_base = REPO / "Data" / "processed" / "fr" / "pooled" / "fr_p3a_gsurv2_estimation_ready"
    out_path = REPO / "Results" / "JMP_pooled_P3a_corrected_S6_theta_c_singles_LL_profile.json"

    with open(se_json_path) as f:
        se_data = json.load(f)
    theta = np.array(se_data["cluster_robust_se_artifacts"]["converged_theta"], dtype=float)

    p3a_names = [
        "beta_l0_sm","beta_l_age_sm","beta_l_age2_sm","beta_c_sm","theta_l_sm",
        "beta_l0_sf","beta_l_age_sf","beta_l_age2_sf","beta_l_nkids_sf","beta_c_sf","theta_l_sf",
        "theta_c_singles","beta_l0_m","beta_l_age_m","beta_l_age2_m","theta_l_m","beta_l0_f",
        "beta_l_age_f","beta_l_age2_f","beta_l_nkids_f","theta_l_f","beta_c","beta_E",
        "beta_h_pt1","beta_h_pt2","beta_h_ft","beta_E_gsur","beta_E_drgn2","beta_E_drgn3",
        "beta_E_drgn4","beta_E_drgn5","beta_E_drgn6","beta_E_drgn7","beta_E_drgn8",
        "beta_E_y2015","beta_E_y2017","beta_occ_2_sm","beta_occ_3_sm","beta_occ_4_sm",
        "beta_occ_2_sf","beta_occ_3_sf","beta_occ_4_sf","beta_occ_2_cm","beta_occ_3_cm",
        "beta_occ_4_cm","beta_occ_2_cf","beta_occ_3_cf","beta_occ_4_cf","beta_w0",
        "beta_w_educL","beta_w_educH","beta_w_pexp","beta_w_pexp2","sigma","beta_ll",
    ]
    i_tcs = p3a_names.index("theta_c_singles")
    tcs_hat = float(theta[i_tcs])
    print(f"saved theta_c_singles = {tcs_hat:.6f}")

    spec = parse_specification(spec_path)
    df_singles, df_couples, metadata = load_and_validate_mnl_data(
        singles_path=Path(str(mnl_base) + "__singles.parquet"),
        couples_path=Path(str(mnl_base) + "__couples.parquet"),
        metadata_path=Path(str(mnl_base) + "__mnlmeta.json"),
        strict_validation=True,
    )
    include_wage = (spec.wage_spec in ["vw", "loc_empirical"])
    include_loc = (spec.wage_spec == "loc_empirical")
    extra_vars = _collect_extra_vars(spec)
    df_sm = df_singles[df_singles["dgn"] == 1].copy()
    df_sf = df_singles[df_singles["dgn"] == 0].copy()
    for d in (df_sm, df_sf, df_couples):
        if "idhh" in d.columns and not d["idhh"].is_monotonic_increasing:
            d.sort_values("idhh", inplace=True)
            d.reset_index(drop=True, inplace=True)
    data_sm = precompute_data_singles(df=df_sm, metadata=metadata, is_male=True,
                                      include_wage_vars=include_wage, include_loc_vars=include_loc,
                                      include_extra_vars=extra_vars)
    data_sf = precompute_data_singles(df=df_sf, metadata=metadata, is_male=False,
                                      include_wage_vars=include_wage, include_loc_vars=include_loc,
                                      include_extra_vars=extra_vars)
    data_cou = precompute_data_couples(df=df_couples, metadata=metadata,
                                       include_wage_vars=include_wage, include_loc_vars=include_loc,
                                       include_extra_vars=extra_vars)

    # Reference: nLL at saved theta
    nll_hat = float(compute_likelihood_joint(theta, data_sm, data_sf, data_cou, spec))
    ll_hat = -nll_hat
    print(f"saved joint LL = {ll_hat:.6f} (saved per JSON: {se_data.get('joint_ll', 'n/a')})")

    # Bounded grid: cover both directions around saved value, generously
    grid = np.array([
        tcs_hat - 1.50,
        tcs_hat - 1.00,
        tcs_hat - 0.50,
        tcs_hat - 0.20,
        tcs_hat - 0.10,
        tcs_hat - 0.05,
        tcs_hat - 0.01,
        tcs_hat,
        tcs_hat + 0.01,
        tcs_hat + 0.05,
        tcs_hat + 0.10,
        tcs_hat + 0.20,
        tcs_hat + 0.50,
        tcs_hat + 1.00,
        tcs_hat + 1.50,
        # Also probe the M1-clean value (~ -1.048483)
        -1.048483,
    ], dtype=float)
    grid = np.unique(np.round(grid, 6))
    grid.sort()

    print("Profiling joint LL across grid in theta_c_singles ...")
    results = []
    for g in grid:
        th = theta.copy()
        th[i_tcs] = g
        nll = float(compute_likelihood_joint(th, data_sm, data_sf, data_cou, spec))
        ll = -nll
        d_ll = ll - ll_hat
        print(f"  theta_c_singles = {g:+.6f}  joint_LL = {ll:.4f}  ΔLL vs hat = {d_ll:+.4f}")
        results.append({"theta_c_singles": g, "nll": nll, "ll": ll, "delta_ll_vs_hat": d_ll})

    out = {
        "criterion": "S6_theta_c_singles_LL_profile",
        "saved_theta_c_singles": tcs_hat,
        "saved_joint_LL": ll_hat,
        "grid": grid.tolist(),
        "profile": results,
        "note": "Deterministic LL evaluations. theta varied only on theta_c_singles axis; all other coordinates held at saved converged values.",
        "no_optimization": "CONFIRMED",
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Saved: {out_path.name}")


if __name__ == "__main__":
    main()