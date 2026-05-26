"""
Post-estimation S5/S8 Hessian recomputation at the SAVED corrected-region
converged theta of pooled P3a Start 1.

This is fixed-theta evaluation only:
- No solver call
- No optimization step
- No re-estimation
- Theta is held identical to Results/JMP_pooled_P3a_corrected_start1_cluster_robust_se.json

Outputs:
- Results/JMP_pooled_P3a_corrected_true_hessian_54x54.npy   (recomputed H_free)
- Results/JMP_pooled_P3a_corrected_S5_S8_hessian_diag.json  (diag, eigenvalues,
  GSUR-region sub-block, conditioning, neg-variance enumeration)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
from path_helpers import resolve_repo_root, data_root  # noqa: E402

REPO = resolve_repo_root()
sys.path.insert(0, str(REPO / "scripts" / "enhanced"))

from estimation_spec_parser import parse_specification
from estimation_engine import compute_gradient_joint
from estimation_utils import load_and_validate_mnl_data
from estimation_utils import precompute_data_singles, precompute_data_couples


def _collect_extra_vars(spec) -> list:
    """Mirror run_cluster_robust_se._collect_extra_vars by deferring to it."""
    from run_cluster_robust_se import _collect_extra_vars as _c
    return _c(spec)


def main():
    se_json_path = REPO / "Results" / "JMP_pooled_P3a_corrected_start1_cluster_robust_se.json"
    spec_path = REPO / "scripts" / "enhanced" / "specifications" / "estimation_spec_ruro_occ_P3a_pooled.yaml"
    mnl_base = data_root() / "processed/fr/pooled/fr_p3a_gsurv2_estimation_ready"

    out_hess_npy = REPO / "Results" / "JMP_pooled_P3a_corrected_true_hessian_54x54.npy"
    out_diag_json = REPO / "Results" / "JMP_pooled_P3a_corrected_S5_S8_hessian_diag.json"

    print(f"Loading saved corrected theta from {se_json_path.name} ...")
    with open(se_json_path) as f:
        se_data = json.load(f)
    theta = np.array(se_data["cluster_robust_se_artifacts"]["converged_theta"], dtype=float)
    free_mask = np.array(se_data["cluster_robust_se_artifacts"]["free_mask"], dtype=bool)
    n_params = len(theta)
    n_free = int(free_mask.sum())
    free_idx = np.where(free_mask)[0]
    print(f"  theta len = {n_params}, n_free = {n_free}, ||theta|| = {np.linalg.norm(theta):.6f}")

    print(f"Parsing spec {spec_path.name} ...")
    spec = parse_specification(spec_path)
    assert len(spec.all_param_names) == n_params
    param_names = list(spec.all_param_names)
    print(f"  n_params from spec = {n_params}")
    print(f"  param at fixed bound: {[p for p,m in zip(param_names, free_mask) if not m]}")

    print(f"Loading data from {mnl_base.name} ...")
    df_singles, df_couples, metadata = load_and_validate_mnl_data(
        singles_path=Path(str(mnl_base) + "__singles.parquet"),
        couples_path=Path(str(mnl_base) + "__couples.parquet"),
        metadata_path=Path(str(mnl_base) + "__mnlmeta.json"),
        strict_validation=True,
    )
    print(f"  singles rows = {len(df_singles):,}  couples rows = {len(df_couples):,}")

    include_wage = (spec.wage_spec in ["vw", "loc_empirical"])
    include_loc = (spec.wage_spec == "loc_empirical")
    extra_vars = _collect_extra_vars(spec)

    gender_col = "dgn" if "dgn" in df_singles.columns else None
    df_sm = df_singles[df_singles[gender_col] == 1].copy()
    df_sf = df_singles[df_singles[gender_col] == 0].copy()
    for d in (df_sm, df_sf, df_couples):
        if "idhh" in d.columns and not d["idhh"].is_monotonic_increasing:
            d.sort_values("idhh", inplace=True)
            d.reset_index(drop=True, inplace=True)

    print("Precomputing data objects ...")
    data_sm = precompute_data_singles(
        df=df_sm, metadata=metadata, is_male=True,
        include_wage_vars=include_wage, include_loc_vars=include_loc,
        include_extra_vars=extra_vars,
    )
    data_sf = precompute_data_singles(
        df=df_sf, metadata=metadata, is_male=False,
        include_wage_vars=include_wage, include_loc_vars=include_loc,
        include_extra_vars=extra_vars,
    )
    data_cou = precompute_data_couples(
        df=df_couples, metadata=metadata,
        include_wage_vars=include_wage, include_loc_vars=include_loc,
        include_extra_vars=extra_vars,
    )
    print(f"  groups: sm={data_sm.n_groups} sf={data_sf.n_groups} cou={data_cou.n_groups}")

    # Verify gradient at theta is near zero (sanity: theta is a stationary point)
    g0 = compute_gradient_joint(theta, data_sm, data_sf, data_cou, spec)
    g0_free = g0[free_idx]
    print(f"||grad(theta)||_inf at saved theta (free coords) = {np.max(np.abs(g0_free)):.6e}")

    # Central-differences Hessian at the SAVED theta. No optimization.
    eps = 1e-5
    print(f"Recomputing true Hessian via central differences (eps={eps}) at SAVED theta ...")
    H_free = np.zeros((n_free, n_free))
    for col_idx, i in enumerate(free_idx):
        theta_p = theta.copy(); theta_p[i] += eps
        theta_m = theta.copy(); theta_m[i] -= eps
        g_p = compute_gradient_joint(theta_p, data_sm, data_sf, data_cou, spec)
        g_m = compute_gradient_joint(theta_m, data_sm, data_sf, data_cou, spec)
        H_free[:, col_idx] = (g_p[free_idx] - g_m[free_idx]) / (2 * eps)
        if (col_idx + 1) % 5 == 0 or col_idx == 0:
            print(f"  col {col_idx+1}/{n_free} done")

    H_free = 0.5 * (H_free + H_free.T)
    cond = float(np.linalg.cond(H_free))
    eigvals_full = np.linalg.eigvalsh(H_free)
    n_neg_eig = int(np.sum(eigvals_full < 0))
    print(f"H_free shape={H_free.shape}, cond={cond:.4e}, n_negative_eigvals={n_neg_eig}")
    print(f"  min eig={eigvals_full.min():.6e}  max eig={eigvals_full.max():.6e}")

    np.save(out_hess_npy, H_free)
    print(f"Saved {out_hess_npy.name}")

    # diag(H_free^-1) — Hessian-based variances
    H_free_inv = np.linalg.pinv(H_free, rcond=1e-10)
    diag_inv = np.diag(H_free_inv)
    # Map back to full n_params slot, with NaN for fixed
    hessian_variance_full = np.full(n_params, np.nan)
    hessian_variance_full[free_idx] = diag_inv

    neg_variance_idx = [int(i) for i in free_idx if hessian_variance_full[i] < 0]
    neg_variance_names = [param_names[i] for i in neg_variance_idx]
    print(f"n_params with NEGATIVE Hessian-based variance: {len(neg_variance_idx)}")
    for i, name in zip(neg_variance_idx, neg_variance_names):
        print(f"  {name}: H_inv_diag={hessian_variance_full[i]:.6e}")

    # GSUR + 7 region dummies sub-block (8x8 in FREE indexing)
    # full-index positions: 26 (gsur), 27..33 (drgn2..drgn8)
    gsur_region_full = list(range(26, 34))
    # Map to free indices: since beta_l0_m at pos 12 is the only fixed param,
    # the free index = full index for positions >= 13 -> shift by -1
    # We compute explicitly:
    full_to_free = -1 * np.ones(n_params, dtype=int)
    full_to_free[free_idx] = np.arange(n_free)
    gsur_region_free = [int(full_to_free[i]) for i in gsur_region_full]
    print(f"GSUR+region full indices: {gsur_region_full}")
    print(f"GSUR+region free indices: {gsur_region_free}")
    H_sub = H_free[np.ix_(gsur_region_free, gsur_region_free)]
    eig_sub = np.linalg.eigvalsh(H_sub)
    cond_sub = float(np.linalg.cond(H_sub))
    print(f"8x8 GSUR-region Hessian sub-block: eigvals={eig_sub}, cond={cond_sub:.4e}")

    # Also report 7x7 region-only Hessian sub-block (the S5 region block)
    region_full = list(range(27, 34))
    region_free = [int(full_to_free[i]) for i in region_full]
    H_region = H_free[np.ix_(region_free, region_free)]
    eig_region = np.linalg.eigvalsh(H_region)
    cond_region = float(np.linalg.cond(H_region))
    print(f"7x7 Region-only Hessian sub-block: eigvals={eig_region}, cond={cond_region:.4e}")

    # Robust SE vector (already saved) for reference
    se_robust = np.array(se_data["cluster_robust_se_artifacts"]["se_robust_vector"], dtype=float)
    se_hessian = np.array(
        [float(x) if x is not None and (isinstance(x, (int, float)) and not (isinstance(x, float) and np.isnan(x))) else float("nan")
         for x in se_data["cluster_robust_se_artifacts"]["se_hessian_vector"]]
    )

    # Compose output JSON
    out = {
        "criterion": "S5_S8_hessian_recompute",
        "source": "Results/JMP_pooled_P3a_corrected_start1_cluster_robust_se.json",
        "theta_norm": float(np.linalg.norm(theta)),
        "grad_at_theta_max_abs_free": float(np.max(np.abs(g0_free))),
        "n_params": n_params,
        "n_free": n_free,
        "eps": eps,
        "method": "central differences on compute_gradient_joint, FIXED-theta",
        "hessian_npy": str(out_hess_npy),
        "hessian_condition_number": cond,
        "hessian_eigenvalues_sorted": eigvals_full.tolist(),
        "hessian_min_eigenvalue": float(eigvals_full.min()),
        "hessian_max_eigenvalue": float(eigvals_full.max()),
        "hessian_n_negative_eigenvalues": n_neg_eig,
        "GSUR_region_subblock_8x8": {
            "param_names": [param_names[i] for i in gsur_region_full],
            "full_indices": gsur_region_full,
            "free_indices": gsur_region_free,
            "eigenvalues_sorted": eig_sub.tolist(),
            "condition_number": cond_sub,
            "min_eigenvalue": float(eig_sub.min()),
            "n_negative_eigenvalues": int(np.sum(eig_sub < 0)),
        },
        "Region_subblock_7x7": {
            "param_names": [param_names[i] for i in region_full],
            "eigenvalues_sorted": eig_region.tolist(),
            "condition_number": cond_region,
            "min_eigenvalue": float(eig_region.min()),
            "n_negative_eigenvalues": int(np.sum(eig_region < 0)),
        },
        "S8_negative_variance_enumeration": {
            "n_negative_variance_params": len(neg_variance_idx),
            "param_indices_full": neg_variance_idx,
            "param_names": neg_variance_names,
            "diag_H_inv_negative_values": [float(hessian_variance_full[i]) for i in neg_variance_idx],
            "se_robust_for_these": [float(se_robust[i]) for i in neg_variance_idx],
            "se_hessian_for_these": [float(se_hessian[i]) if np.isfinite(se_hessian[i]) else None for i in neg_variance_idx],
        },
        "no_solver": "CONFIRMED",
        "no_re_estimation": "CONFIRMED",
        "fixed_theta": "CONFIRMED",
    }
    with open(out_diag_json, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Saved {out_diag_json.name}")


if __name__ == "__main__":
    main()