# RURO Low-Token Post-Estimation Summary

Generated: 2026-05-13T19:35:40

## Purpose

Compact text-only report for Git, paper drafting, and LLM review.
Figures and large HTML output are intentionally omitted.

## Sources

| item | path_or_value |
| --- | --- |
| estimation_results_json | U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0a_clean\run_2026-05-13_19-24-38\estimation_results.json |
| html_report | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0a_clean\run_2026-05-13_19-35-16\fr_2016_ruro_occ_gamspy_M0a_clean_post_estimation_report_20260513_193536.html |
| post_output_dir | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0a_clean\run_2026-05-13_19-35-16 |
| params_csv | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0a_clean\run_2026-05-13_19-35-16\fr_2016_ruro_occ_gamspy_M0a_clean_params.csv |
| elasticities_csv | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0a_clean\run_2026-05-13_19-35-16\fr_2016_ruro_occ_gamspy_M0a_clean_elasticities.csv |
| mnl_base | Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl |
| spec_config | scripts\enhanced\estimation_spec_ruro_occ_M0a_clean.yaml |

## Run Metadata

| field | value |
| --- | --- |
| specification | ruro_occ_M0a_clean |
| model_family | regular |
| market_opportunity_tier | NA |
| prior_correction_applied | 1 |
| prior_correction_form | -log(prior) |
| market_centering_applied | 1 |
| wage_spec | vw |
| estimation_walltime_seconds | 282.114 |

## Source Environment

| field | value |
| --- | --- |
| git_sha | 17781375570c |
| git_branch | main |
| git_dirty | 0 |

## Choice Data Footprint

| dataset | rows | groups | alt_min | alt_median | alt_max | chosen_rows | working_rows | n_columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| singles | 167600 | 1676 | 100 | 100 | 100 | 1676 | 150787 | 75 |
| couples | 257700 | 2577 | 100 | 100 | 100 | 2577 | male=231647; female=232007 | 93 |

## Per-Group Sample Sizes

| group | n_obs | n_households | alts_per_hh | n_chosen | n_working |
| --- | --- | --- | --- | --- | --- |
| singles_male | 76600 | 766 | 100 | 766 | 68942 |
| singles_female | 91000 | 910 | 100 | 910 | 81845 |
| couples_male | 257700 | 2577 | 100 | 2577 | 231647 |
| couples_female | 257700 | 2577 | 100 | 2577 | 232007 |

## Sample Descriptives (chosen alternatives, by group)

| group | variable | mean | std | min | max | n |
| --- | --- | --- | --- | --- | --- | --- |
| singles_male | age_norm | -0.683 | 11.2541 | -25.5811 | 20.4189 | 766 |
| singles_male | age_norm2 | 126.955 | 133.011 | 0.1754 | 654.395 | 766 |
| singles_male | educL | 0.1736 | 0.379 | 0 | 1 | 766 |
| singles_male | educM | 0.4504 | 0.4979 | 0 | 1 | 766 |
| singles_male | educH | 0.376 | 0.4847 | 0 | 1 | 766 |
| singles_male | pexp_years | 22.4117 | 12.3718 | 0 | 49 | 766 |
| singles_male | n_children | 0.188 | 0.5635 | 0 | 4 | 766 |
| singles_male | gsur | 0.0986 | 0.0463 | 0.04 | 0.21 | 766 |
| singles_female | age_norm | 0.5749 | 10.7626 | -23.5811 | 21.4189 | 910 |
| singles_female | age_norm2 | 116.036 | 122.721 | 0.1754 | 556.07 | 910 |
| singles_female | educL | 0.1352 | 0.3421 | 0 | 1 | 910 |
| singles_female | educM | 0.4352 | 0.4961 | 0 | 1 | 910 |
| singles_female | educH | 0.4297 | 0.4953 | 0 | 1 | 910 |
| singles_female | pexp_years | 22.5456 | 12.3448 | 0 | 49 | 910 |
| singles_female | n_children | 0.5505 | 0.8657 | 0 | 5 | 910 |
| singles_female | gsur | 0.0934 | 0.0379 | 0.048 | 0.2 | 910 |
| couples_male | age_norm | 0 | 9.6816 | -23.1424 | 21.8576 | 2577 |
| couples_male | age_norm2 | 93.6976 | 100.577 | 0.0203 | 535.571 | 2577 |
| couples_male | educL | 0.1432 | 0.3503 | 0 | 1 | 2577 |
| couples_male | educM | 0.466 | 0.4989 | 0 | 1 | 2577 |
| couples_male | educH | 0.3908 | 0.488 | 0 | 1 | 2577 |
| couples_male | pexp_years | 21.8 | 10.7286 | 0 | 48 | 2577 |
| couples_male | gsur | 0.0955 | 0.0444 | 0.04 | 0.21 | 2577 |
| couples_female | age_norm | 0 | 9.7911 | -21.156 | 23.844 | 2577 |
| couples_female | age_norm2 | 95.829 | 103.086 | 0.0243 | 568.537 | 2577 |
| couples_female | educL | 0.1195 | 0.3245 | 0 | 1 | 2577 |
| couples_female | educM | 0.4016 | 0.4903 | 0 | 1 | 2577 |
| couples_female | educH | 0.4789 | 0.4996 | 0 | 1 | 2577 |
| couples_female | pexp_years | 19.3425 | 10.9589 | 0 | 47 | 2577 |
| couples_female | gsur | 0.0913 | 0.0384 | 0.048 | 0.2 | 2577 |

## Proposal And Prior Diagnostics

| dataset | min_prior | max_abs_log_prior_minus_log_density | max_abs_prior_alias_reconstruction | missing_aliases | forbidden_columns_present |
| --- | --- | --- | --- | --- | --- |
| singles | 7.8191e-06 | 0 | 0 | none | none |
| couples | 6.28983e-11 | 0 | 0 | none | none |

## Warnings And Review Flags

| type | message |
| --- | --- |
| identification | weakly conditioned (1e6 <= kappa < 1e10); 1 negative eigenvalue(s) - not at a local maximum or numerically singular |
| fit | cou_f: predicted participation is very high (1.0000) |
| fit | cou_m: predicted participation is very high (1.0000) |
| fit | sf: predicted participation is very high (1.0000) |
| fit | sm: predicted participation is very high (1.0000) |
| probability | minimum chosen probability is very small (1.178e-08) |
| hessian | negative eigenvalues present; inspect SE and local optimum diagnostics |

## Convergence Health Summary

| metric | value |
| --- | --- |
| n_estimated_params | 47 |
| log_likelihood | -6521.43 |
| AIC | 13136.9 |
| BIC | 13652 |
| rho_squared | 0.707842 |
| n_significant_p<0.05 | 31 |
| pct_significant_p<0.05 | 66.0% |
| n_low_t<1.0 | 7 |
| pct_low_t<1.0 | 14.9% |
| n_degenerate_se | 0 |
| n_at_bound_strict | 0 |
| hessian_condition_number | 9.94133e+09 |
| n_negative_eigenvalues | 1 |
| p_chosen_min | 1.17838e-08 |
| p_chosen_q10 | 0.0107093 |
| review_priority_flags | negative_eigenvalues_present, very_small_p_chosen_min |

## Model Index Equation

V_ij = U_ij + O^E_ij + O^H_ij + O^W_ij + O^Occ_ij - log_prior_ij

P_ij = exp(V_ij) / sum_k exp(V_ik)

## Utility / Preference Parameters By Group

Utility uses Box-Cox consumption and leisure. This table gives the
group-level consumption and leisure parameters resolved from the
estimated parameter vector.

| group | beta_c | theta_c | beta_l0 | beta_l_shifters | theta_l | beta_cl |
| --- | --- | --- | --- | --- | --- | --- |
| f | 6.15368 | 0.318888 | 4.84496 | beta_l_age=-0.0467143; beta_l_age2=0.00240137; beta_l_nkids=0.241246 | -0.697005 | NA |
| m | 6.15368 | 0.318888 | 2.3263 | beta_l_age=-0.00438717; beta_l_age2=0.00148976 | -0.739209 | NA |
| sf | 0.67674 | 0.318888 | 4.53152 | beta_l_age=0.00271211; beta_l_age2=0.00418775; beta_l_nkids=0.0948926 | -0.726808 | NA |
| sm | 0.747506 | 0.318888 | 3.953 | beta_l_age=0.00987964; beta_l_age2=0.00199617 | -0.707345 | NA |

## Specification Block Inventory

| yaml_block | label | n_shifters | variables | coefficients |
| --- | --- | --- | --- | --- |
| utility.consumption.coefficient | consumption scale | 1 | - | beta_c |
| utility.consumption.box_cox_exponent | consumption theta_c | 1 | - | theta_c |
| utility.leisure.intercept | leisure intercept | 1 | - | beta_l0 |
| utility.leisure.box_cox_exponent | leisure theta_l | 1 | - | theta_l |
| utility.leisure.shifters | Utility-leisure shifters | 3 | age_norm, age_norm2, n_children | beta_l_age, beta_l_age2, beta_l_nkids |
| hours_opportunity | Employment/Hours | 4 | working, working_ft, working_pt1, working_pt2 | beta_E, beta_h_pt1, beta_h_pt2, beta_h_ft |
| market_opportunity | Market residual | 2 | educH, gsur | beta_E_gsur, beta_E_educH |
| wage_opportunity.mean_shifters | Mincer mean | 5 | educH, educL, intercept, pexp_years, pexp_years2 | beta_w0, beta_w_educL, beta_w_educH, beta_w_pexp, beta_w_pexp2 |
| wage_opportunity.variance | Mincer sigma | 1 | - | sigma |
| occupation_opportunity | Occupation | 12 | loc4_2, loc4_3, loc4_4 | beta_occ_2_sm, beta_occ_3_sm, beta_occ_4_sm, beta_occ_2_sf, beta_occ_3_sf, beta_occ_4_sf, beta_occ_2_cm, beta_occ_3_cm, beta_occ_4_cm, beta_occ_2_cf, beta_occ_3_cf, beta_occ_4_cf |

## Opportunity Equations — Symbolic

```text
O^E + O^H =
+ beta_E * working
+ beta_h_pt1 * working_pt1
+ beta_h_pt2 * working_pt2
+ beta_h_ft * working_ft
+ beta_E_gsur * gsur * working
+ beta_E_educH * educH * working

mu_w =
+ beta_w0
+ beta_w_educL * educL
+ beta_w_educH * educH
+ beta_w_pexp * pexp_years
+ beta_w_pexp2 * pexp_years2
log(wage) = mu_w + eps,  eps ~ N(0, sigma^2)

O^Occ (reference loc4=1):
applies_to=sm:
+ beta_occ_2_sm * loc4_2 * working
+ beta_occ_3_sm * loc4_3 * working
+ beta_occ_4_sm * loc4_4 * working
applies_to=sf:
+ beta_occ_2_sf * loc4_2 * working
+ beta_occ_3_sf * loc4_3 * working
+ beta_occ_4_sf * loc4_4 * working
applies_to=cm:
+ beta_occ_2_cm * loc4_2 * working
+ beta_occ_3_cm * loc4_3 * working
+ beta_occ_4_cm * loc4_4 * working
applies_to=cf:
+ beta_occ_2_cf * loc4_2 * working
+ beta_occ_3_cf * loc4_3 * working
+ beta_occ_4_cf * loc4_4 * working
```

## Opportunity Equations — Numerical (estimated coefficients bound)

| block | term | coefficient | source_group | value |
| --- | --- | --- | --- | --- |
| employment_hours | beta_E * working | beta_E | joint | -2.7597 |
| employment_hours | beta_h_pt1 * working_pt1 | beta_h_pt1 | joint | -0.499056 |
| employment_hours | beta_h_pt2 * working_pt2 | beta_h_pt2 | joint | 0.377181 |
| employment_hours | beta_h_ft * working_ft | beta_h_ft | joint | 1.45359 |
| employment_hours | beta_E_gsur * gsur * working | beta_E_gsur | joint | -0.740758 |
| employment_hours | beta_E_educH * educH * working | beta_E_educH | joint | 0.549463 |
| wage_mean | beta_w0 * intercept | beta_w0 | joint | 2.04761 |
| wage_mean | beta_w_educL * educL | beta_w_educL | joint | -0.0478467 |
| wage_mean | beta_w_educH * educH | beta_w_educH | joint | 0.300722 |
| wage_mean | beta_w_pexp * pexp_years | beta_w_pexp | joint | 0.0167247 |
| wage_mean | beta_w_pexp2 * pexp_years2 | beta_w_pexp2 | joint | -0.000194818 |
| wage_sigma | sigma | sigma | joint | 0.41895 |
| occupation:sm | beta_occ_2_sm * loc4_2 * working | beta_occ_2_sm | joint | -1.51538 |
| occupation:sm | beta_occ_3_sm * loc4_3 * working | beta_occ_3_sm | joint | -2.17257 |
| occupation:sm | beta_occ_4_sm * loc4_4 * working | beta_occ_4_sm | joint | 0.0168988 |
| occupation:sf | beta_occ_2_sf * loc4_2 * working | beta_occ_2_sf | joint | -0.0210542 |
| occupation:sf | beta_occ_3_sf * loc4_3 * working | beta_occ_3_sf | joint | -0.572369 |
| occupation:sf | beta_occ_4_sf * loc4_4 * working | beta_occ_4_sf | joint | 0.787611 |
| occupation:cm | beta_occ_2_cm * loc4_2 * working | beta_occ_2_cm | joint | -1.47303 |
| occupation:cm | beta_occ_3_cm * loc4_3 * working | beta_occ_3_cm | joint | -2.21121 |
| occupation:cm | beta_occ_4_cm * loc4_4 * working | beta_occ_4_cm | joint | 0.479122 |
| occupation:cf | beta_occ_2_cf * loc4_2 * working | beta_occ_2_cf | joint | 0.18778 |
| occupation:cf | beta_occ_3_cf * loc4_3 * working | beta_occ_3_cf | joint | -0.201979 |
| occupation:cf | beta_occ_4_cf * loc4_4 * working | beta_occ_4_cf | joint | 1.12366 |

## Per-Block Parameter Counts and Significance

| block | n_params | n_estimable | n_sig_p<0.001 | n_sig_p<0.01 | n_sig_p<0.05 | n_sig_p<0.10 |
| --- | --- | --- | --- | --- | --- | --- |
| preference | 23 | 23 | 10 | 10 | 11 | 11 |
| employment_hours_opportunity | 4 | 4 | 4 | 4 | 4 | 4 |
| market_residual_opportunity | 2 | 2 | 1 | 1 | 2 | 2 |
| wage_opportunity | 6 | 6 | 5 | 5 | 6 | 6 |
| occupation_opportunity | 12 | 12 | 8 | 8 | 8 | 10 |

## Convergence By Result Block

| group | success | message | iterations | n_function_evaluations | gradient_norm | log_likelihood | walltime_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| joint | 1 | SolveStatus.NormalCompletion (ModelStatus.OptimalLocal) | 27 | 27 | NA | -6521.43 | 94.0381 |

## Fit Statistics

| metric | value |
| --- | --- |
| log_likelihood | -6521.43 |
| ll_null_uniform | -19585.8 |
| ll_null_prior_corrected | -22321.6 |
| rho_squared | 0.707842 |
| rho_squared_adj | 0.705736 |
| rho_squared_uniform | 0.667033 |
| rho_squared_prior_corrected | 0.707842 |
| AIC | 13136.9 |
| BIC | 13652 |
| AIC_per_obs | 0.0308885 |
| n_observations | 425300 |
| n_groups | 4253 |
| n_parameters | 47 |
| n_obs_long | 425300 |

## Fit Moments

| group | participation_observed | participation_predicted | mean_hours_observed | mean_hours_predicted |
| --- | --- | --- | --- | --- |
| cou_f | 0.965076 | 1 | 35.6466 | 58.5092 |
| cou_m | 0.971672 | 1 | 41.6062 | 58.7331 |
| sf | 0.929504 | 1 | 39.3048 | 63.5143 |
| sm | 0.93956 | 1 | 36.2971 | 63.7757 |

## Observed Hours Quantiles (chosen working alts)

| group | n | q10 | q25 | q50 | q75 | q90 |
| --- | --- | --- | --- | --- | --- | --- |
| singles_male | 712 | 33 | 35 | 39 | 42 | 50 |
| singles_female | 855 | 24 | 35 | 36 | 40 | 45 |
| couples_male | 2504 | 35 | 35 | 40 | 45 | 55 |
| couples_female | 2487 | 24 | 32 | 35 | 40 | 45 |

## Distribution Fit Summary (observed vs predicted hours bins)

| group | dimension | n_bins | L1_distance | L2_distance |
| --- | --- | --- | --- | --- |
| cou_f | hours_bins | 8 | 1.6539 | 0.7076 |
| cou_m | hours_bins | 8 | 1.3838 | 0.6578 |
| sf | hours_bins | 8 | 1.8616 | 0.8752 |
| sm | hours_bins | 8 | 1.9187 | 0.8736 |

## Observed vs Implied Log-Wage σ (chosen working alts)

| group | n | observed_mean_log_wage | observed_std_log_wage | implied_sigma |
| --- | --- | --- | --- | --- |
| singles_male | 712 | 2.6836 | 0.4502 | 0.41895 |
| singles_female | 855 | 2.6198 | 0.436 | 0.41895 |
| couples_male | 2504 | 2.7697 | 0.4402 | 0.41895 |
| couples_female | 2487 | 2.6221 | 0.436 | 0.41895 |

## Structural Elasticity Heuristics

These are curvature-based heuristics from the post-estimation script, not
policy-counterfactual elasticities.

| Group | Hicksian (compensated) | Marshallian (uncompensated) | Participation (extensive) | Intensive (conditional) | theta_l | theta_c | beta_l (at median X) | beta_c |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single Males | 1.707 | 1.607 | 0.512 | 1.195 | -0.707 | 0.319 | 3.953 | 0.748 |
| Single Females | 1.727 | 1.627 | 0.518 | 1.209 | -0.727 | 0.319 | 4.532 | 0.677 |
| Males in Couples | 1.739 | 1.639 | 0.522 | 1.217 | -0.739 | 0.319 | 2.326 | 6.154 |
| Females in Couples | 1.697 | 1.597 | 0.509 | 1.188 | -0.697 | 0.319 | 4.845 | 6.154 |

## Marginal Utility Diagnostics

| Group | beta_c | theta_c | MUC Positive? | MUC Diminishing? | Well-Behaved? | MUC at Median C | C where MUC=1 | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single Males | 0.747506 | 0.318888 | yes | yes | yes | 0.747506 | 0.652293 | NA |
| Single Females | 0.67674 | 0.318888 | yes | yes | yes | 0.67674 | 0.563673 | NA |
| Males in Couples | 6.15368 | 0.318888 | yes | yes | yes | 6.15368 | 14.4078 | NA |
| Females in Couples | 6.15368 | 0.318888 | yes | yes | yes | 6.15368 | 14.4078 | NA |

## Marginal Utility Distribution Summary

| group | N | n_neg_muc | pct_neg_muc | mean_muc | n_neg_mul | pct_neg_mul | mean_mul |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cou_f | 2577 | 0 | 0 | 0.0218044 | 0 | 0 | 0.00884405 |
| cou_m | 2577 | 0 | 0 | 0.0218044 | 0 | 0 | 0.00541533 |
| sf | 766 | 0 | 0 | 0.00405751 | 0 | 0 | 0.00894206 |
| sm | 910 | 0 | 0 | 0.0044704 | 0 | 0 | 0.00715925 |
| total | NA | 0 | 0 | NA | 0 | 0 | NA |

## Probability Diagnostics

| metric | value |
| --- | --- |
| prob_sum_max_error | 6.66134e-16 |
| prob_sum_mean_error | 1.29034e-16 |
| prob_sum_pct_off_by_0.01 | 0 |
| prob_sum_pct_off_by_0.001 | 0 |
| p_chosen_min | 1.17838e-08 |
| p_chosen_max | 0.999745 |
| p_chosen_mean | 0.364254 |
| p_chosen_median | 0.241243 |
| p_chosen_q10 | 0.0107093 |
| p_chosen_q25 | 0.0665394 |
| p_chosen_q75 | 0.669534 |
| p_chosen_q90 | 0.90632 |

## Worst-Fit Households

| rank | idhh | group | p_chosen | ll_i |
| --- | --- | --- | --- | --- |
| 1 | 4012700 | sm | 1.17838e-08 | -18.2565 |
| 2 | 3600001 | sf | 1.80617e-08 | -17.8295 |
| 3 | 4264600 | cou | 1.8122e-08 | -17.8261 |
| 4 | 3251600 | cou | 9.54942e-08 | -16.1642 |
| 5 | 4034500 | cou | 2.24594e-07 | -15.309 |
| 6 | 1935801 | sm | 2.53899e-07 | -15.1863 |
| 7 | 1729600 | cou | 3.1309e-07 | -14.9768 |
| 8 | 3457500 | sm | 3.45169e-07 | -14.8792 |
| 9 | 3951700 | cou | 4.16851e-07 | -14.6905 |
| 10 | 1918802 | sf | 5.13172e-07 | -14.4827 |

## Identification Diagnostics

| metric | value |
| --- | --- |
| condition_number | 9.94133e+09 |
| min_eigenvalue | -4.46924 |
| max_eigenvalue | 1.50137e+10 |
| n_negative_eigenvalues | 1 |

_Interpretation: weakly conditioned (1e6 <= kappa < 1e10); 1 negative eigenvalue(s) - not at a local maximum or numerically singular._

## Initial → Final Movement (top 15 by |Δ|)

| block | parameter | initial_value | final_estimate | delta |
| --- | --- | --- | --- | --- |
| preference | joint.beta_c | 1 | 6.15368 | 5.15368 |
| preference | joint.beta_l0_f | 1 | 4.84496 | 3.84496 |
| preference | joint.beta_l0_sf | 1 | 4.53152 | 3.53152 |
| preference | joint.beta_l0_sm | 1 | 3.953 | 2.953 |
| employment_hours_opportunity | joint.beta_E | 0 | -2.7597 | -2.7597 |
| occupation_opportunity | joint.beta_occ_3_cm | 0 | -2.21121 | -2.21121 |
| occupation_opportunity | joint.beta_occ_3_sm | 0 | -2.17257 | -2.17257 |
| occupation_opportunity | joint.beta_occ_2_sm | 0 | -1.51538 | -1.51538 |
| occupation_opportunity | joint.beta_occ_2_cm | 0 | -1.47303 | -1.47303 |
| employment_hours_opportunity | joint.beta_h_ft | 0 | 1.45359 | 1.45359 |
| preference | joint.beta_l0_m | 1 | 2.3263 | 1.3263 |
| preference | joint.theta_c | -1 | 0.318888 | 1.31889 |
| occupation_opportunity | joint.beta_occ_4_cf | 0 | 1.12366 | 1.12366 |
| occupation_opportunity | joint.beta_occ_4_sf | 0 | 0.787611 | 0.787611 |
| market_residual_opportunity | joint.beta_E_gsur | 0 | -0.740758 | -0.740758 |

## Top High-Correlation Parameter Pairs

| param_i | param_j | correlation |
| --- | --- | --- |
| theta_c_singles | beta_c | -1.26809 |
| beta_c_sm | beta_c | -1.20378 |
| beta_c_sf | beta_c | -1.19211 |
| theta_c_singles | sigma | 1.15125 |
| beta_c_sm | sigma | 1.09961 |
| beta_c_sf | sigma | 1.09949 |
| beta_c_sm | beta_c_sf | -1.03451 |
| beta_c_sf | theta_c_singles | -1.02883 |
| beta_c_sm | theta_c_singles | -1.02261 |
| beta_c | theta_c | 1.01019 |

## Weakest Eigenvector Diagnostics

_None._

## Parameters At Bounds

_None._

## Parameters Near Bounds (within 5% of bound width)

| block | parameter | estimate | lower_bound | upper_bound | flags |
| --- | --- | --- | --- | --- | --- |
| preference | joint.beta_c_sm | 0.747506 | 0.05 | 50 | near_lower(delta=0.698) |
| preference | joint.beta_c_sf | 0.67674 | 0.05 | 50 | near_lower(delta=0.627) |
| preference | joint.beta_l0_m | 2.3263 | 0.05 | 50 | near_lower(delta=2.28) |
| wage_opportunity | joint.sigma | 0.41895 | 0.1 | 20 | near_lower(delta=0.319) |

## Top Significant Coefficients (top 15 by |t|)

| block | parameter | estimate | std_error | t_value | p_value |
| --- | --- | --- | --- | --- | --- |
| wage_opportunity | joint.sigma | 0.41895 | 0.0032656 | 128.292 | 0 |
| wage_opportunity | joint.beta_w0 | 2.04761 | 0.0254738 | 80.381 | 0 |
| employment_hours_opportunity | joint.beta_h_ft | 1.45359 | 0.0500423 | 29.0473 | 0 |
| wage_opportunity | joint.beta_w_educH | 0.300722 | 0.014487 | 20.7581 | 0 |
| occupation_opportunity | joint.beta_occ_3_cm | -2.21121 | 0.147256 | -15.0161 | 0 |
| occupation_opportunity | joint.beta_occ_4_cf | 1.12366 | 0.0810914 | 13.8568 | 0 |
| occupation_opportunity | joint.beta_occ_2_cm | -1.47303 | 0.113381 | -12.9918 | 0 |
| preference | joint.beta_c | 6.15368 | 0.498888 | 12.3348 | 0 |
| occupation_opportunity | joint.beta_occ_3_sm | -2.17257 | 0.184474 | -11.7771 | 0 |
| occupation_opportunity | joint.beta_occ_2_sm | -1.51538 | 0.142204 | -10.6564 | 0 |
| employment_hours_opportunity | joint.beta_E | -2.7597 | 0.298265 | -9.25251 | 0 |
| occupation_opportunity | joint.beta_occ_4_sf | 0.787611 | 0.0920487 | 8.55646 | 0 |
| preference | joint.theta_l_f | -0.697005 | 0.0899751 | -7.74664 | 9.32587e-15 |
| wage_opportunity | joint.beta_w_pexp | 0.0167247 | 0.0021732 | 7.69587 | 1.39888e-14 |
| occupation_opportunity | joint.beta_occ_4_cm | 0.479122 | 0.0684667 | 6.99789 | 2.59859e-12 |

## Parameter Estimates By Block

| block | parameter | estimate | std_error | t_value | p_value | lower_bound | upper_bound | initial_value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| employment_hours_opportunity | joint.beta_E | -2.7597 | 0.298265 | -9.25251 | 0 | -25 | 25 | 0 |
| employment_hours_opportunity | joint.beta_h_ft | 1.45359 | 0.0500423 | 29.0473 | 0 | -10 | 10 | 0 |
| employment_hours_opportunity | joint.beta_h_pt1 | -0.499056 | 0.107673 | -4.63491 | 3.57101e-06 | -10 | 10 | 0 |
| employment_hours_opportunity | joint.beta_h_pt2 | 0.377181 | 0.111062 | 3.39613 | 0.00068347 | -10 | 10 | 0 |
| market_residual_opportunity | joint.beta_E_educH | 0.549463 | 0.235168 | 2.33647 | 0.0194669 | -10 | 10 | 0 |
| market_residual_opportunity | joint.beta_E_gsur | -0.740758 | 0.219095 | -3.38098 | 0.000722266 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_cf | 0.18778 | 0.0998564 | 1.8805 | 0.0600401 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_cm | -1.47303 | 0.113381 | -12.9918 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_sf | -0.0210542 | 0.112731 | -0.186764 | 0.851845 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_sm | -1.51538 | 0.142204 | -10.6564 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_cf | -0.201979 | 0.110933 | -1.82072 | 0.0686489 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_cm | -2.21121 | 0.147256 | -15.0161 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_sf | -0.572369 | 0.129082 | -4.43416 | 9.24302e-06 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_sm | -2.17257 | 0.184474 | -11.7771 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_cf | 1.12366 | 0.0810914 | 13.8568 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_cm | 0.479122 | 0.0684667 | 6.99789 | 2.59859e-12 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_sf | 0.787611 | 0.0920487 | 8.55646 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_sm | 0.0168988 | 0.0861322 | 0.196196 | 0.844457 | -10 | 10 | 0 |
| preference | joint.beta_c | 6.15368 | 0.498888 | 12.3348 | 0 | 0.05 | 50 | 1 |
| preference | joint.beta_c_sf | 0.67674 | NA | NA | NA | 0.05 | 50 | 1 |
| preference | joint.beta_c_sm | 0.747506 | NA | NA | NA | 0.05 | 50 | 1 |
| preference | joint.beta_l0_f | 4.84496 | 0.698708 | 6.93417 | 4.08606e-12 | 0.05 | 50 | 1 |
| preference | joint.beta_l0_m | 2.3263 | 0.348408 | 6.67694 | 2.43985e-11 | 0.05 | 50 | 1 |
| preference | joint.beta_l0_sf | 4.53152 | 0.794617 | 5.70277 | 1.17877e-08 | 0.05 | 50 | 1 |
| preference | joint.beta_l0_sm | 3.953 | 0.738949 | 5.34949 | 8.82019e-08 | 0.05 | 50 | 1 |
| preference | joint.beta_l_age2_f | 0.00240137 | 0.00224501 | 1.06965 | 0.284779 | -1 | 1 | 0 |
| preference | joint.beta_l_age2_m | 0.00148976 | 0.00147617 | 1.00921 | 0.312876 | -1 | 1 | 0 |
| preference | joint.beta_l_age2_sf | 0.00418775 | 0.00258289 | 1.62134 | 0.104944 | -1 | 1 | 0 |
| preference | joint.beta_l_age2_sm | 0.00199617 | 0.00208127 | 0.959113 | 0.337502 | -1 | 1 | 0 |
| preference | joint.beta_l_age_f | -0.0467143 | 0.0222951 | -2.09527 | 0.0361468 | -5 | 5 | 0 |
| preference | joint.beta_l_age_m | -0.00438717 | 0.0150796 | -0.290933 | 0.771102 | -5 | 5 | 0 |
| preference | joint.beta_l_age_sf | 0.00271211 | 0.0273045 | 0.0993286 | 0.920877 | -5 | 5 | 0 |
| preference | joint.beta_l_age_sm | 0.00987964 | 0.0247678 | 0.398891 | 0.689974 | -5 | 5 | 0 |
| preference | joint.beta_l_nkids_f | 0.241246 | 0.222472 | 1.08439 | 0.278192 | -5 | 5 | 0 |
| preference | joint.beta_l_nkids_sf | 0.0948926 | 0.362074 | 0.262081 | 0.793259 | -5 | 5 | 0 |
| preference | joint.theta_c | 0.318888 | 0.0769517 | 4.14401 | 3.41292e-05 | -8 | 0.95 | -1 |
| preference | joint.theta_c_singles | -0.835741 | NA | NA | NA | -8 | 0.95 | -1 |
| preference | joint.theta_l_f | -0.697005 | 0.0899751 | -7.74664 | 9.32587e-15 | -8 | 0.95 | -1 |
| preference | joint.theta_l_m | -0.739209 | 0.123364 | -5.99212 | 2.07128e-09 | -8 | 0.95 | -1 |
| preference | joint.theta_l_sf | -0.726808 | 0.134623 | -5.39883 | 6.70767e-08 | -8 | 0.95 | -1 |
| preference | joint.theta_l_sm | -0.707345 | 0.154958 | -4.56475 | 5.00081e-06 | -8 | 0.95 | -1 |
| wage_opportunity | joint.beta_w0 | 2.04761 | 0.0254738 | 80.381 | 0 | -10 | 20 | 2 |
| wage_opportunity | joint.beta_w_educH | 0.300722 | 0.014487 | 20.7581 | 0 | -5 | 5 | 0.2 |
| wage_opportunity | joint.beta_w_educL | -0.0478467 | 0.020395 | -2.346 | 0.0189763 | -5 | 5 | -0.1 |
| wage_opportunity | joint.beta_w_pexp | 0.0167247 | 0.0021732 | 7.69587 | 1.39888e-14 | -1 | 1 | 0.02 |
| wage_opportunity | joint.beta_w_pexp2 | -0.000194818 | 4.80484e-05 | -4.05462 | 5.02163e-05 | -0.1 | 0.1 | -0.0003 |
| wage_opportunity | joint.sigma | 0.41895 | 0.0032656 | 128.292 | 0 | 0.1 | 20 | 0.5 |

## Hours Distribution Shares

| group | hours_bin | observed_share | predicted_share |
| --- | --- | --- | --- |
| cou_f | 0 | 0.0349243 | 0 |
| cou_f | 1-10 | 0.0256112 | 0 |
| cou_f | 11-20 | 0.0923555 | 0.00465658 |
| cou_f | 21-30 | 0.38766 | 0.0197905 |
| cou_f | 31-40 | 0.381451 | 0.0706248 |
| cou_f | 41-50 | 0.0523865 | 0.197516 |
| cou_f | 51-60 | 0.0201785 | 0.414435 |
| cou_f | 60+ | 0.00543267 | 0.292976 |
| cou_m | 0 | 0.0283275 | 0 |
| cou_m | 1-10 | 0.00388048 | 0 |
| cou_m | 11-20 | 0.0209546 | 0.00349243 |
| cou_m | 21-30 | 0.256888 | 0.0205666 |
| cou_m | 31-40 | 0.470702 | 0.064804 |
| cou_m | 41-50 | 0.135429 | 0.188591 |
| cou_m | 51-60 | 0.0589833 | 0.423749 |
| cou_m | 60+ | 0.0248351 | 0.298797 |
| sf | 0 | 0.0704961 | 0 |
| sf | 1-10 | 0.0104439 | 0 |
| sf | 11-20 | 0.0483029 | 0 |
| sf | 21-30 | 0.25718 | 0 |
| sf | 31-40 | 0.480418 | 0 |
| sf | 41-50 | 0.0770235 | 0.0130548 |
| sf | 51-60 | 0.0443864 | 0.620104 |
| sf | 60+ | 0.0117493 | 0.366841 |
| sm | 0 | 0.0604396 | 0 |
| sm | 1-10 | 0.0307692 | 0 |
| sm | 11-20 | 0.0835165 | 0 |
| sm | 21-30 | 0.347253 | 0 |
| sm | 31-40 | 0.385714 | 0 |
| sm | 41-50 | 0.0626374 | 0.010989 |
| sm | 51-60 | 0.021978 | 0.6 |
| sm | 60+ | 0.00769231 | 0.389011 |

## Wage Distribution Summary

Observed values use chosen working alternatives. Predicted values use
choice-probability weights over working alternatives.

| group | n_observed_working | predicted_worker_weight | obs_mean | pred_mean | obs_q10 | obs_q50 | obs_q90 | pred_q10 | pred_q50 | pred_q90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | 712 | 760.289 | 16.2131 | 15.4828 | 9.15372 | 14.2557 | 25.4434 | 7.838 | 14.0385 | 24.7579 |
| singles_female | 855 | 902.609 | 15.1069 | 15.4895 | 8.65411 | 13.8516 | 22.9432 | 7.85572 | 13.8585 | 24.8082 |
| couples_male | 2504 | 2571.91 | 17.656 | 19.8063 | 10.0631 | 15.2895 | 27.8735 | 10.0869 | 16.3461 | 33.8556 |
| couples_female | 2487 | 2565.97 | 15.1712 | 18.2348 | 8.86239 | 13.8393 | 22.4802 | 9.33223 | 14.7971 | 31.5865 |

## Occupation Distribution Shares

Observed shares use chosen working alternatives. Predicted shares use
choice-probability weights over working alternatives. Category labels
are reported for loc4-style variables when available.

| group | occupation_column | category | label | observed_share | predicted_share | observed_count | predicted_weight |
| --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | loc4 | -2 | unknown_observed_working | 0.00561798 | 0.000334116 | 4 | 0.254025 |
| singles_male | loc4 | 1 | routine_manual_ref | 0.407303 | 0.285533 | 290 | 217.087 |
| singles_male | loc4 | 2 | nonroutine_manual | 0.0941011 | 0.230106 | 67 | 174.947 |
| singles_male | loc4 | 3 | routine_cognitive | 0.0505618 | 0.206765 | 36 | 157.201 |
| singles_male | loc4 | 4 | nonroutine_cognitive | 0.442416 | 0.277263 | 315 | 210.8 |
| singles_female | loc4 | -2 | unknown_observed_working | 0.00350877 | 0.000760786 | 3 | 0.686692 |
| singles_female | loc4 | 1 | routine_manual_ref | 0.191813 | 0.257561 | 164 | 232.477 |
| singles_female | loc4 | 2 | nonroutine_manual | 0.20117 | 0.236774 | 172 | 213.715 |
| singles_female | loc4 | 3 | routine_cognitive | 0.130994 | 0.227053 | 112 | 204.94 |
| singles_female | loc4 | 4 | nonroutine_cognitive | 0.472515 | 0.277851 | 404 | 250.79 |
| couples_male | loc4_male | -2 | unknown_observed_working | 0.0123802 | 0.00647898 | 31 | 16.6633 |
| couples_male | loc4_male | 1 | routine_manual_ref | 0.360224 | 0.338569 | 902 | 870.767 |
| couples_male | loc4_male | 2 | nonroutine_manual | 0.0802716 | 0.159153 | 201 | 409.327 |
| couples_male | loc4_male | 3 | routine_cognitive | 0.0391374 | 0.119451 | 98 | 307.216 |
| couples_male | loc4_male | 4 | nonroutine_cognitive | 0.507987 | 0.376348 | 1272 | 967.932 |
| couples_female | loc4_female | -2 | unknown_observed_working | 0.00120627 | 0.000595021 | 3 | 1.5268 |
| couples_female | loc4_female | 1 | routine_manual_ref | 0.170084 | 0.224088 | 423 | 575.001 |
| couples_female | loc4_female | 2 | nonroutine_manual | 0.206273 | 0.232763 | 513 | 597.261 |
| couples_female | loc4_female | 3 | routine_cognitive | 0.152392 | 0.196406 | 379 | 503.972 |
| couples_female | loc4_female | 4 | nonroutine_cognitive | 0.470044 | 0.346149 | 1169 | 888.206 |

## Notes For Use

- This Markdown file is the preferred low-token artifact for LLM review.
- Use the HTML report only when plots or visual diagnostics are needed.
- Generated output folders remain local unless explicitly added to Git.
