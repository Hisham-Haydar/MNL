# RURO Recovery Test Results — bpool_p3a_v1 (58 params)

> ## VERDICT: ❌ DID NOT PASS — did not converge; recovery inconclusive
>
> The warm start **hit maxiter=400 without converging** (`success=False`), and the
> Hessian at the stopping point is **NOT positive-definite** (min eigenvalue
> **−0.0124**, condition number **inf**). The reported point is therefore **not a local
> optimum**, so the per-param recovery table below reflects a **non-converged iterate**,
> not a recovered solution. Only **3 / 38 testable params** are within tol & correct sign.
>
> **Failure is structural, concentrated in the couples consumption/leisure SCALE block:**
> `beta_c` (θ*=0.75 → 22.45), `beta_l0_m` (0.01 → 21.05), `theta_l_m` (−0.75 → −4.96) all
> **drifted to / toward their bounds**. In the Box-Cox couples utility
> `U = beta_c·BC(c) + beta_l0_m·BC(l_m) + beta_l0_f·BC(l_f) + …`, these three free scale
> parameters can **co-scale without changing choice probabilities** → a utility-scale
> indeterminacy (flat ridge) → the negative Hessian eigenvalue. **This is NOT a
> sample-size artifact** (a normalization indeterminacy does not sharpen with more data),
> so "re-test on the full pool" would NOT fix it. The well-identified blocks (occupation,
> region, urbanisation, hours) also show wrong signs/large errors here **only because the
> optimizer never reached the optimum** along that flat ridge — not necessarily because
> they are themselves unidentified.
>
> **Likely remedy (to verify, not yet applied):** normalize the utility scale — e.g. fix
> `beta_c = 1` (consumption coefficient) so leisure/consumption levels are pinned. The NC
> pilot reported finite `beta_c`≈2.18 / `beta_l0_m`≈0.012, so either the pilot was
> identified by a feature this slice lacks, or it stopped on the same ridge without
> recovery validation. The recovery test cannot pass until the scale is normalized.
>
> **G3b urbanisation×region verdict below is UNRELIABLE** (computed from a non-PD,
> non-invertible covariance → nan correlations). Defer until the model converges.

**mode:** couples  **years:** 2016  **n_hh:** 300  **solver:** scipy-trustconstr  **seed:** 20260527

theta* generated generically from spec (initial+bounds), no param names hardcoded; synthetic choice drawn (vectorized) from theta* on the REAL alternatives.

**Solver behaviour:** L-BFGS-B (spec default) STALLED (grinds, |g| oscillates 1e2–1e4, no convergence — reproduces NC-pilot finding). CONOPT/GAMSPy works but ~3.5 h/start model-generation at full size. scipy trust-constr (Hessian/trust-region, used here) navigates the manifold best but **did not converge on this slice** due to the scale indeterminacy above. NOTE: variable-scaling fixes WERE applied and were necessary — pexp_years and age_norm rescaled to decades so pexp_years2∈[0,6], age_norm2∈[0,6] (previously 0–2400 / 0–640 dominated |g|max); these resolved the wage/age conditioning but exposed the deeper consumption/leisure scale issue.


## Starts
| start | success | LL | nit | sec |
|---|---|---|---|---|
| warm | False | -6175.864 | 400 | 523.6 |

**G2** max|warm−cold| (testable) = nan

## G3 Conditioning
- PD: **False**
- cond: **inf**
- min eig: **-1.237e-02**, max: 2.381e+05

## G3b market-opportunity collinearity (generic)
- worst |corr| = **nan** (None)
- **Verdict: market-opp access shifters SEPARATELY IDENTIFIED**


_Inert on this slice (excluded from G1): ['beta_E_y2015', 'beta_E_y2017', 'beta_c_sf', 'beta_c_sm', 'beta_l0_sf', 'beta_l0_sm', 'beta_l_age2_sf', 'beta_l_age2_sm', 'beta_l_age_sf', 'beta_l_age_sm', 'beta_l_nkids_sf', 'beta_occ_2_sf', 'beta_occ_2_sm', 'beta_occ_3_sf', 'beta_occ_3_sm', 'beta_occ_4_sf', 'beta_occ_4_sm', 'theta_c_singles', 'theta_l_sf', 'theta_l_sm']_


## G1 / G4 per-param recovery

| param | theta* | theta_hat | abs_err | err/se | wrong_sign | inert |
|---|---|---|---|---|---|---|
| beta_l0_sm | +1.2500 | +6.7998 | 5.5498 | n/a | False | True |
| beta_l_age_sm | -0.6000 | -0.2595 | 0.3405 | n/a | False | True |
| beta_l_age2_sm | +0.1200 | +0.6688 | 0.5488 | n/a | False | True |
| beta_c_sm | +0.7500 | +2.1919 | 1.4419 | n/a | False | True |
| theta_l_sm | -1.2500 | -1.9796 | 0.7296 | n/a | False | True |
| beta_l0_sf | +0.7500 | +4.0722 | 3.3222 | n/a | False | True |
| beta_l_age_sf | +0.6000 | -1.0947 | 1.6947 | n/a | True | True |
| beta_l_age2_sf | -0.1200 | +0.2002 | 0.3202 | n/a | True | True |
| beta_l_nkids_sf | +0.6000 | -0.4123 | 1.0123 | n/a | True | True |
| beta_c_sf | +0.7500 | +3.5646 | 2.8146 | n/a | False | True |
| theta_l_sf | -1.2500 | -1.5082 | 0.2582 | n/a | False | True |
| theta_c_singles | -0.7500 | +0.0279 | 0.7779 | n/a | True | True |
| beta_l0_m | +0.0125 | +21.0526 | 21.0401 | n/a | False | False |
| beta_l_age_m | -0.6000 | -1.6929 | 1.0929 | n/a | False | False |
| beta_l_age2_m | +0.1200 | -0.7402 | 0.8602 | n/a | True | False |
| theta_l_m | -0.7500 | -4.9607 | 4.2107 | n/a | False | False |
| beta_l0_f | +1.2500 | +0.1391 | 1.1109 | n/a | False | False |
| beta_l_age_f | -0.6000 | -0.1537 | 0.4463 | n/a | False | False |
| beta_l_age2_f | +0.1200 | +0.1112 | 0.0088 | n/a | False | False |
| beta_l_nkids_f | -0.6000 | +0.1043 | 0.7043 | n/a | True | False |
| theta_l_f | -1.2500 | +0.9314 | 2.1814 | n/a | True | False |
| beta_c | +0.7500 | +22.4486 | 21.6986 | n/a | False | False |
| beta_E | +3.0000 | -1.1937 | 4.1937 | n/a | True | False |
| beta_h_pt1 | -1.2000 | -0.8285 | 0.3715 | n/a | False | False |
| beta_h_pt2 | +1.2000 | +0.0432 | 1.1568 | n/a | False | False |
| beta_h_ft | -1.2000 | -0.5465 | 0.6535 | n/a | False | False |
| beta_h_lh | +1.2000 | -9.9948 | 11.1948 | n/a | True | False |
| beta_E_gsur | -1.2000 | -3.3620 | 2.1620 | n/a | False | False |
| beta_E_drgn2 | +1.2000 | -1.1908 | 2.3908 | n/a | True | False |
| beta_E_drgn3 | -1.2000 | +1.2275 | 2.4275 | n/a | True | False |
| beta_E_drgn4 | +1.2000 | -0.6744 | 1.8744 | n/a | True | False |
| beta_E_drgn5 | -1.2000 | -1.5736 | 0.3736 | n/a | False | False |
| beta_E_drgn6 | +1.2000 | +2.4824 | 1.2824 | n/a | False | False |
| beta_E_drgn7 | -1.2000 | +1.1783 | 2.3783 | n/a | True | False |
| beta_E_drgn8 | +1.2000 | +2.6813 | 1.4813 | n/a | False | False |
| beta_E_y2015 | -0.6000 | -0.5228 | 0.0772 | n/a | False | True |
| beta_E_y2017 | +0.6000 | +1.2133 | 0.6133 | n/a | False | True |
| beta_E_drgur | -1.2000 | -0.3071 | 0.8929 | n/a | False | False |
| beta_E_drgmd | +1.2000 | -1.2587 | 2.4587 | n/a | True | False |
| beta_occ_2_sm | -1.2000 | -1.2648 | 0.0648 | n/a | False | True |
| beta_occ_3_sm | +1.2000 | +1.3056 | 0.1056 | n/a | False | True |
| beta_occ_4_sm | -1.2000 | -1.2247 | 0.0247 | n/a | False | True |
| beta_occ_2_sf | +1.2000 | +1.1638 | 0.0362 | n/a | False | True |
| beta_occ_3_sf | -1.2000 | -1.2205 | 0.0205 | n/a | False | True |
| beta_occ_4_sf | +1.2000 | +1.1436 | 0.0564 | n/a | False | True |
| beta_occ_2_cm | -1.2000 | -1.8054 | 0.6054 | n/a | False | False |
| beta_occ_3_cm | +1.2000 | -1.7934 | 2.9934 | n/a | True | False |
| beta_occ_4_cm | -1.2000 | +0.7079 | 1.9079 | n/a | True | False |
| beta_occ_2_cf | +1.2000 | +0.1911 | 1.0089 | n/a | False | False |
| beta_occ_3_cf | -1.2000 | -0.4323 | 0.7677 | n/a | False | False |
| beta_occ_4_cf | +1.2000 | +0.8799 | 0.3201 | n/a | False | False |
| beta_w0 | +1.5000 | +1.8297 | 0.3297 | n/a | False | False |
| beta_w_educL | -0.1250 | -0.1228 | 0.0022 | n/a | False | False |
| beta_w_educH | +0.1500 | +0.2507 | 0.1007 | n/a | False | False |
| beta_w_pexp | +0.0250 | +0.3339 | 0.3089 | n/a | False | False |
| beta_w_pexp2 | -0.0002 | -0.0985 | 0.0982 | n/a | False | False |
| sigma | +0.6250 | +0.2578 | 0.3672 | n/a | False | False |
| beta_ll | +1.5000 | +2.2490 | 0.7490 | n/a | False | False |