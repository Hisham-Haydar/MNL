# Extended Post-Estimation Diagnostics

**Results JSON**: `estimation_results.json`  
**Specification**: Not available in supplied solver artifacts  
**Generated**: 2026-05-22T16:18:32.260392Z  
**Cluster column**: cluster_id

---

## 1. Inference Table

Full parameter table with Hessian SE, cluster-robust SE, t-ratios, and bound status. Supply `--cluster-se-json` to populate `se_robust` and `t_robust` columns.

| param | theta | se_hessian | se_robust | t_robust | p_robust | at_lower_bound | at_upper_bound | in_free_mask |
|---|---|---|---|---|---|---|---|---|
| beta_l0_sm | 4.328086 | 0.050209 | 0.781812 | 5.536 | 0.0000 | False | False | True |
| beta_l_age_sm | 0.043144 | 0.012663 | 0.022755 | 1.896 | 0.0580 | False | False | True |
| beta_l_age2_sm | 0.001724 | 0.001167 | 0.002058 | 0.837 | 0.4023 | False | False | True |
| beta_c_sm | 2.733147 | 0.066396 | 0.282414 | 9.678 | 0.0000 | False | False | True |
| theta_l_sm | -0.719206 | 0.047580 | 0.061439 | -11.706 | 0.0000 | False | False | True |
| beta_l0_sf | 4.460193 | 0.232333 | 0.877401 | 5.083 | 0.0000 | False | False | True |
| beta_l_age_sf | 0.038506 | 0.014160 | 0.028573 | 1.348 | 0.1778 | False | False | True |
| beta_l_age2_sf | 0.004610 | 0.001218 | 0.002535 | 1.819 | 0.0690 | False | False | True |
| beta_l_nkids_sf | 0.356277 | 0.182103 | 0.416413 | 0.856 | 0.3922 | False | False | True |
| beta_c_sf | 2.351327 | 0.065725 | 0.357395 | 6.579 | 0.0000 | False | False | True |
| theta_l_sf | -0.701604 | 0.026209 | 0.058010 | -12.095 | 0.0000 | False | False | True |
| theta_c_singles | 0.039244 | 0.014574 | 0.067078 | 0.585 | 0.5585 | False | False | True |
| beta_l0_m | 0.000001 | nan | 0.000000 | nan | nan | False | False | False |
| beta_l_age_m | 0.005870 | 0.009036 | 0.018983 | 0.309 | 0.7571 | False | False | True |
| beta_l_age2_m | 0.001646 | 0.000715 | 0.001244 | 1.323 | 0.1858 | False | False | True |
| theta_l_m | -0.681907 | 0.025689 | 0.037734 | -18.072 | 0.0000 | False | False | True |
| beta_l0_f | 2.605285 | 0.267620 | 0.766677 | 3.398 | 0.0007 | False | False | True |
| beta_l_age_f | -0.058032 | 0.012851 | 0.039474 | -1.470 | 0.1415 | False | False | True |
| beta_l_age2_f | 0.005288 | 0.001338 | 0.003798 | 1.392 | 0.1638 | False | False | True |
| beta_l_nkids_f | 0.142852 | 0.129419 | 0.364326 | 0.392 | 0.6950 | False | False | True |
| theta_l_f | -0.657847 | 0.013714 | 0.031404 | -20.948 | 0.0000 | False | False | True |
| beta_c | 4.312411 | 0.057720 | 0.455261 | 9.472 | 0.0000 | False | False | True |
| beta_E | -2.397723 | 0.128602 | 0.287991 | -8.326 | 0.0000 | False | False | True |
| beta_h_pt1 | -0.474816 | 0.063327 | 0.132469 | -3.584 | 0.0003 | False | False | True |
| beta_h_pt2 | 0.424756 | 0.065887 | 0.103702 | 4.096 | 0.0000 | False | False | True |
| beta_h_ft | 1.405924 | 0.030011 | 0.085405 | 16.462 | 0.0000 | False | False | True |
| beta_E_gsur | -1.199923 | 0.096488 | 0.191094 | -6.279 | 0.0000 | False | False | True |
| beta_E_drgn2 | 0.396497 | 0.158898 | 0.384543 | 1.031 | 0.3025 | False | False | True |
| beta_E_drgn3 | 0.350000 | 0.196859 | 0.399138 | 0.877 | 0.3805 | False | False | True |
| beta_E_drgn4 | 0.641609 | 0.219262 | 0.553706 | 1.159 | 0.2466 | False | False | True |
| beta_E_drgn5 | 0.431035 | 0.171955 | 0.442708 | 0.974 | 0.3302 | False | False | True |
| beta_E_drgn6 | 0.357738 | 0.192742 | 0.468154 | 0.764 | 0.4448 | False | False | True |
| beta_E_drgn7 | 0.367068 | 0.184294 | 0.436956 | 0.840 | 0.4009 | False | False | True |
| beta_E_drgn8 | 0.167527 | 0.170297 | 0.337045 | 0.497 | 0.6192 | False | False | True |
| beta_E_y2015 | -0.059090 | 0.119274 | 0.257281 | -0.230 | 0.8183 | False | False | True |
| beta_E_y2017 | 0.155430 | 0.126932 | 0.270128 | 0.575 | 0.5650 | False | False | True |
| beta_occ_2_sm | -1.496158 | 0.083229 | 0.110788 | -13.505 | 0.0000 | False | False | True |
| beta_occ_3_sm | -2.138378 | 0.108443 | 0.154417 | -13.848 | 0.0000 | False | False | True |
| beta_occ_4_sm | 0.074381 | 0.050617 | 0.057176 | 1.301 | 0.1933 | False | False | True |
| beta_occ_2_sf | -0.104983 | 0.065514 | 0.082604 | -1.271 | 0.2038 | False | False | True |
| beta_occ_3_sf | -0.532782 | 0.073541 | 0.089681 | -5.941 | 0.0000 | False | False | True |
| beta_occ_4_sf | 0.763932 | 0.052848 | 0.072780 | 10.496 | 0.0000 | False | False | True |
| beta_occ_2_cm | -1.502612 | 0.069743 | 0.157697 | -9.528 | 0.0000 | False | False | True |
| beta_occ_3_cm | -2.222216 | 0.090010 | 0.213548 | -10.406 | 0.0000 | False | False | True |
| beta_occ_4_cm | 0.476417 | 0.041701 | 0.086351 | 5.517 | 0.0000 | False | False | True |
| beta_occ_2_cf | 0.113438 | 0.061378 | 0.138650 | 0.818 | 0.4133 | False | False | True |
| beta_occ_3_cf | -0.329211 | 0.067960 | 0.156230 | -2.107 | 0.0351 | False | False | True |
| beta_occ_4_cf | 1.075478 | 0.049239 | 0.111613 | 9.636 | 0.0000 | False | False | True |
| beta_w0 | 2.033343 | 0.012791 | 0.094222 | 21.580 | 0.0000 | False | False | True |
| beta_w_educL | -0.041400 | 0.011429 | 0.074199 | -0.558 | 0.5769 | False | False | True |
| beta_w_educH | 0.306669 | 0.008690 | 0.060426 | 5.075 | 0.0000 | False | False | True |
| beta_w_pexp | 0.017306 | 0.001323 | 0.008753 | 1.977 | 0.0480 | False | False | True |
| beta_w_pexp2 | -0.000182 | 0.000030 | 0.000194 | -0.938 | 0.3482 | False | False | True |
| sigma | 0.403406 | 0.000221 | 0.001545 | 261.146 | 0.0000 | False | False | True |
| beta_ll | 2.655942 | 0.049107 | 0.374056 | 7.100 | 0.0000 | False | False | True |


## 2. Solver Convergence Diagnostics

**GAMSPy version**: Not available in supplied solver artifacts
**Solver**: Not available in supplied solver artifacts

**Per-group convergence:**

| Group | Final LL | Iterations | Fn Evals | Wall (s) | Success | Solve Status | Model Status |
|-------|----------|------------|----------|----------|---------|--------------|--------------|
| singles_male | -19084.331307 | 14 | Not available in supplied solver artifacts | 273.48037163416546 | True | NormalCompletion | OptimalLocal |
| singles_female | -19084.331307 | 14 | Not available in supplied solver artifacts | 273.48037163416546 | True | NormalCompletion | OptimalLocal |
| couples | -19084.331307 | 14 | Not available in supplied solver artifacts | 273.48037163416546 | True | NormalCompletion | OptimalLocal |

**GAMS listing file diagnostics** (from `--listing-file`):

| Field | Value |
|-------|-------|
| GAMS solver | Not available in supplied solver artifacts |
| Solver status | Normal Completion |
| Model status | Locally Optimal |
| Equations | Not available in supplied solver artifacts |
| Variables | Not available in supplied solver artifacts |
| Nonzeros | Not available in supplied solver artifacts |
| Max infeasibility | Not available in supplied solver artifacts |
| Solve time (s) | 191.312 |
| Generation time (s) | Not available in supplied solver artifacts |
| Active bounds count | Not available in supplied solver artifacts |


## 3. CONOPT / GAMS Solver Diagnostics

> CONOPT-specific fields (RGmax, tolerances, equations/variables/nonzeros) are parsed from the GAMS listing file supplied via `--listing-file`.  If not supplied all fields report «Not available in supplied solver artifacts».  **Best practice**: configure the estimator to save the GAMS listing file and solver log for every run so these fields are always populated.

| Field | Value |
|-------|-------|
| RGmax (solver-internal reduced gradient norm) | Not available in supplied solver artifacts |
| CONOPT RTOL (optimality tolerance) | Not available in supplied solver artifacts |
| CONOPT FTOL (feasibility tolerance) | Not available in supplied solver artifacts |
| RGmax ≤ RTOL | Not available in supplied solver artifacts |

> **Note**: CONOPT RGmax is the solver-internal reduced gradient norm from GAMS/CONOPT. It is **not** the Python likelihood gradient (score) shown in the next section.


## 4. Python Likelihood Gradient Diagnostics

> **Scope**: This section reports the *Python-side* likelihood gradient — the score vector ∂ log L / ∂ θ at the converged parameter vector, computed via central-difference numerical differentiation by the RURO Python engine.  It is **distinct** from the CONOPT solver’s reduced gradient (RGmax).

*Not available in supplied solver artifacts*

## 5. Hessian Diagnostics

| Field | Value |
|-------|-------|
| Source | cluster_robust_se_json (PE6_true_hessian) |
| n_free (identified block) | 54 |
| Hessian shape (free × free) | [54, 54] |
| VCV condition number | 3316291991.058079 |
| Near-singular warning (cond > 1e12) | False |
| SE Hessian range (positive SEs) | 2.9791551810430465e-05 – 0.26762035426051667 |
| SE Robust range (positive SEs) | 0.00019398763793806182 – 0.877400569286903 |

**T5 robust-vs-hessian**: {'n_below': 0, 'below': []}


## 6. Data Diagnostics

**Cluster column**: `cluster_id`

**T3 cluster count**: {'passed': True, 'n_unique_clusters': 9657, 'expected': 9657}
**T4 SE positivity**: {'passed': True, 'n_nonpositive': 0, 'n_free': 54}
**T5 robust-vs-hessian**: {'n_below': 0, 'below': []}
**PE3 data loaded**: {'passed': True, 'n_singles': 500700, 'n_couples': 743800}


## 7. Comparison Run

*Parameter vector length mismatch: main=55, comparison=53.*

## 8. Reproducibility Metadata

**Timestamp (UTC)**: 2026-05-22T16:18:32.260392Z  
**Python**: 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]  
**Platform**: Windows-2022Server-10.0.20348-SP0  
**Git SHA**: 0be727602be7  
**Git branch**: main  
**Git dirty**: True  

**Package versions:**

| Package | Version |
|---------|---------|
| numpy | 2.3.5 |
| pandas | 2.3.3 |
| scipy | 1.16.2 |
| gamspy | 1.17.2 |
| pyarrow | 21.0.0 |
| yaml | 6.0.3 |

**File hashes (SHA-256, first 16 hex digits):**

| Artifact | Hash |
|----------|------|
| results_json | `df6c7c7c49f70f70` |
| spec_config | `8497d236a62bb23b` |
| mnl_base_singles | `c1c9f525fab92bd1` |
| mnl_base_couples | `6b2cf5cf906b303d` |
