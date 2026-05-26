"""S6 preference-block comparison: pooled corrected vs M1-clean verdict-selected."""
import json
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
from path_helpers import outputs_root, resolve_repo_root  # noqa: E402

REPO = resolve_repo_root()

m1_path = outputs_root() / "estimates/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_11-33-46/estimation_results.json"
with open(m1_path) as f:
    m1 = json.load(f)
m1_params = m1["results"]["singles_male"]["parameters"]
m1_names = list(m1_params.keys())
m1_se_list = m1["standard_errors"]["se"]

se_p3a = REPO / "Results" / "JMP_pooled_P3a_corrected_start1_cluster_robust_se.json"
with open(se_p3a) as f:
    p3a = json.load(f)
p3a_theta = np.array(p3a["cluster_robust_se_artifacts"]["converged_theta"])
p3a_se_robust = np.array(p3a["cluster_robust_se_artifacts"]["se_robust_vector"])
p3a_se_hessian = p3a["cluster_robust_se_artifacts"]["se_hessian_vector"]

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

shared = [n for n in p3a_names if n in m1_params]
p3a_only = [n for n in p3a_names if n not in m1_params]
print(f"Shared params: {len(shared)}; P3a-only: {p3a_only}")

# Full comparison over all shared params
rows = []
for name in shared:
    v_m1 = m1_params[name]
    v_p3a = p3a_theta[p3a_names.index(name)]
    delta = v_p3a - v_m1
    rel = (delta / abs(v_m1) * 100) if abs(v_m1) > 1e-6 else float("nan")
    sign_flip = (v_m1 * v_p3a < 0) and (abs(v_m1) > 1e-3 or abs(v_p3a) > 1e-3)
    rows.append({
        "name": name, "m1": float(v_m1), "pooled": float(v_p3a),
        "delta_abs": float(delta), "delta_rel_pct": float(rel), "sign_flip": bool(sign_flip),
        "breaches_10pct": (bool(abs(rel) > 10) if not np.isnan(rel) else None),
    })

# Print focus subset
focus = ["beta_c_sm","beta_c_sf","theta_c_singles","beta_ll",
         "theta_l_sm","theta_l_sf","theta_l_m","theta_l_f",
         "beta_l_age_sm","beta_l_age2_sm","beta_l_age_sf","beta_l_age2_sf",
         "beta_l_nkids_sf","beta_l_age_m","beta_l_age2_m",
         "beta_l_age_f","beta_l_age2_f","beta_l_nkids_f",
         "beta_l0_sm","beta_l0_sf","beta_l0_m","beta_l0_f",
         "beta_c","beta_E","beta_h_pt1","beta_h_pt2","beta_h_ft"]

print(f"\n{'param':22s} | {'M1-clean':>13s} | {'Pooled':>13s} | {'abs delta':>13s} | {'rel %':>10s}")
print("-" * 85)
for r in rows:
    if r["name"] not in focus:
        continue
    flag = "  >10%" if (r["breaches_10pct"] is True) else ""
    flag += "  SIGN-FLIP" if r["sign_flip"] else ""
    rel = r["delta_rel_pct"]
    rel_str = f"{rel:>9.2f}%" if not np.isnan(rel) else "       n/a"
    print(f"{r['name']:22s} | {r['m1']:>13.6f} | {r['pooled']:>13.6f} | {r['delta_abs']:>+13.6f} | {rel_str}{flag}")

# Singles-consumption block SEs
print("\n=== Singles-consumption block SEs ===")
sing_cons_block = {}
for name in ["beta_c_sm","beta_c_sf","theta_c_singles"]:
    i_p = p3a_names.index(name)
    i_m = m1_names.index(name)
    se_r = float(p3a_se_robust[i_p])
    se_h = p3a_se_hessian[i_p]
    m1_se = m1_se_list[i_m]
    print(f"  {name}:")
    print(f"    M1-clean Hessian SE: {m1_se}")
    print(f"    Pooled corrected robust SE: {se_r:.6f}")
    print(f"    Pooled corrected Hessian SE: {se_h}")
    sing_cons_block[name] = {
        "m1_clean_hessian_se": m1_se,
        "pooled_corrected_robust_se": se_r,
        "pooled_corrected_hessian_se": se_h,
    }

# Count breaches in focused preference block
breach_count = sum(1 for r in rows if r["name"] in focus and r["breaches_10pct"] is True)
sign_flip_count = sum(1 for r in rows if r["name"] in focus and r["sign_flip"])
print(f"\nFocused preference block: {breach_count} of {len([r for r in rows if r['name'] in focus])} params breach |Δ| > 10%")
print(f"Focused preference block: {sign_flip_count} sign flips")

out = {
    "criterion": "S6_preference_block_vs_M1_clean",
    "m1_clean_artifact": str(m1_path),
    "m1_clean_joint_ll": m1["summary"]["joint_ll"],
    "shared_params_count": len(shared),
    "p3a_only_params": p3a_only,
    "all_shared_comparison": rows,
    "singles_consumption_SEs": sing_cons_block,
    "summary": {
        "n_focus_params": len([r for r in rows if r["name"] in focus]),
        "n_focus_breach_10pct": breach_count,
        "n_focus_sign_flip": sign_flip_count,
    },
}
out_path = REPO / "Results" / "JMP_pooled_P3a_corrected_S6_preference_comparison.json"
with open(out_path, "w") as f:
    json.dump(out, f, indent=2)
print(f"\nSaved: {out_path.name}")