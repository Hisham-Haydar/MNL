# RURO Low-Token Post-Estimation Summary

Generated: 2026-05-13T15:09:41

## Purpose

Compact text-only report for Git, paper drafting, and LLM review.
Figures and large HTML output are intentionally omitted.

## Sources

| item | path_or_value |
| --- | --- |
| estimation_results_json | U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\spec\stijn_occ\gamspy\estimation_spec_stijn_occ_M0\run_2026-05-13_15-02-16\estimation_results.json |
| html_report | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\stijn_occ\gamspy\estimation_spec_stijn_occ_M0\run_2026-05-13_15-09-17\fr_2016_stijn_occ_gamspy_post_estimation_report_20260513_150938.html |
| post_output_dir | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\stijn_occ\gamspy\estimation_spec_stijn_occ_M0\run_2026-05-13_15-09-17 |
| params_csv | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\stijn_occ\gamspy\estimation_spec_stijn_occ_M0\run_2026-05-13_15-09-17\fr_2016_stijn_occ_gamspy_params.csv |
| elasticities_csv | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\stijn_occ\gamspy\estimation_spec_stijn_occ_M0\run_2026-05-13_15-09-17\fr_2016_stijn_occ_gamspy_elasticities.csv |
| mnl_base | \\aff300msh.cifs.myliser.lu\ComputeShare\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl |
| spec_config | scripts\enhanced\estimation_spec_stijn_occ_M0.yaml |

## Run Metadata

| field | value |
| --- | --- |
| specification | stijn_occ_M0 |
| model_family | regular |
| market_opportunity_tier | NA |
| prior_correction_applied | 1 |
| prior_correction_form | -log(prior) |
| market_centering_applied | 1 |
| wage_spec | vw |
| estimation_walltime_seconds | 158.263 |

## Source Environment

| field | value |
| --- | --- |
| git_sha | e49b8f448268 |
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
| identification | ill-conditioned (kappa >= 1e10); 2 negative eigenvalue(s) - not at a local maximum or numerically singular |
| fit | cou_f: predicted participation is very high (1.0000) |
| fit | cou_m: predicted participation is very high (1.0000) |
| fit | sf: predicted participation is very high (1.0000) |
| fit | sm: predicted participation is very high (1.0000) |
| probability | minimum chosen probability is very small (1.557e-08) |
| hessian | negative eigenvalues present; inspect SE and local optimum diagnostics |

## Convergence Health Summary

| metric | value |
| --- | --- |
| n_estimated_params | 52 |
| log_likelihood | -6499.88 |
| AIC | 13103.8 |
| BIC | 13673.7 |
| rho_squared | 0.708807 |
| n_significant_p<0.05 | 37 |
| pct_significant_p<0.05 | 71.2% |
| n_low_t<1.0 | 9 |
| pct_low_t<1.0 | 17.3% |
| n_degenerate_se | 0 |
| n_at_bound_strict | 0 |
| hessian_condition_number | 6.76389e+10 |
| n_negative_eigenvalues | 2 |
| p_chosen_min | 1.55744e-08 |
| p_chosen_q10 | 0.0130419 |
| review_priority_flags | ill_conditioned_hessian, negative_eigenvalues_present, very_small_p_chosen_min |

## Model Index Equation

V_ij = U_ij + O^E_ij + O^H_ij + O^W_ij + O^Occ_ij - log_prior_ij

P_ij = exp(V_ij) / sum_k exp(V_ik)

## Utility / Preference Parameters By Group

Utility uses Box-Cox consumption and leisure. This table gives the
group-level consumption and leisure parameters resolved from the
estimated parameter vector.

| group | beta_c | theta_c | beta_l0 | beta_l_shifters | theta_l | beta_cl |
| --- | --- | --- | --- | --- | --- | --- |
| f | 5.26199 | 0.215302 | 5.69717 | beta_l_age=-0.0577507; beta_l_age2=0.00156521; beta_l_educH=-1.48897; beta_l_nkids=0.214934 | -0.695727 | NA |
| m | 5.26199 | 0.215302 | 2.70226 | beta_l_age=-0.00737894; beta_l_age2=0.00125552; beta_l_educH=-0.925907 | -0.733006 | NA |
| sf | 0.463007 | -1.08841 | 5.75853 | beta_l_age=-0.016458; beta_l_age2=0.00332398; beta_l_educH=-2.27103; beta_l_nkids=-0.049599 | -0.723846 | NA |
| sm | 0.717509 | -0.856029 | 4.46662 | beta_l_age=0.000844406; beta_l_age2=0.00178502; beta_l_educH=-1.30348 | -0.703775 | NA |

## Specification Block Inventory

| yaml_block | label | n_shifters | variables | coefficients |
| --- | --- | --- | --- | --- |
| utility.consumption.coefficient | consumption scale | 1 | - | beta_c |
| utility.consumption.box_cox_exponent | consumption theta_c | 1 | - | theta_c |
| utility.leisure.intercept | leisure intercept | 1 | - | beta_l0 |
| utility.leisure.box_cox_exponent | leisure theta_l | 1 | - | theta_l |
| utility.leisure.shifters | Utility-leisure shifters | 4 | age_norm, age_norm2, educH, n_children | beta_l_age, beta_l_age2, beta_l_nkids, beta_l_educH |
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
| employment_hours | beta_E * working | beta_E | joint | -2.6148 |
| employment_hours | beta_h_pt1 * working_pt1 | beta_h_pt1 | joint | -0.52032 |
| employment_hours | beta_h_pt2 * working_pt2 | beta_h_pt2 | joint | 0.372057 |
| employment_hours | beta_h_ft * working_ft | beta_h_ft | joint | 1.46325 |
| employment_hours | beta_E_gsur * gsur * working | beta_E_gsur | joint | -0.771874 |
| employment_hours | beta_E_educH * educH * working | beta_E_educH | joint | 0.257516 |
| wage_mean | beta_w0 * intercept | beta_w0 | joint | 2.04108 |
| wage_mean | beta_w_educL * educL | beta_w_educL | joint | -0.0475667 |
| wage_mean | beta_w_educH * educH | beta_w_educH | joint | 0.305522 |
| wage_mean | beta_w_pexp * pexp_years | beta_w_pexp | joint | 0.0173702 |
| wage_mean | beta_w_pexp2 * pexp_years2 | beta_w_pexp2 | joint | -0.000205608 |
| wage_sigma | sigma | sigma | joint | 0.42316 |
| occupation:sm | beta_occ_2_sm * loc4_2 * working | beta_occ_2_sm | joint | -1.51286 |
| occupation:sm | beta_occ_3_sm * loc4_3 * working | beta_occ_3_sm | joint | -2.17256 |
| occupation:sm | beta_occ_4_sm * loc4_4 * working | beta_occ_4_sm | joint | 0.0175251 |
| occupation:sf | beta_occ_2_sf * loc4_2 * working | beta_occ_2_sf | joint | -0.0147421 |
| occupation:sf | beta_occ_3_sf * loc4_3 * working | beta_occ_3_sf | joint | -0.574523 |
| occupation:sf | beta_occ_4_sf * loc4_4 * working | beta_occ_4_sf | joint | 0.793362 |
| occupation:cm | beta_occ_2_cm * loc4_2 * working | beta_occ_2_cm | joint | -1.47074 |
| occupation:cm | beta_occ_3_cm * loc4_3 * working | beta_occ_3_cm | joint | -2.20606 |
| occupation:cm | beta_occ_4_cm * loc4_4 * working | beta_occ_4_cm | joint | 0.486156 |
| occupation:cf | beta_occ_2_cf * loc4_2 * working | beta_occ_2_cf | joint | 0.205 |
| occupation:cf | beta_occ_3_cf * loc4_3 * working | beta_occ_3_cf | joint | -0.190384 |
| occupation:cf | beta_occ_4_cf * loc4_4 * working | beta_occ_4_cf | joint | 1.14601 |

## Per-Block Parameter Counts and Significance

| block | n_params | n_estimable | n_sig_p<0.001 | n_sig_p<0.01 | n_sig_p<0.05 | n_sig_p<0.10 |
| --- | --- | --- | --- | --- | --- | --- |
| preference | 28 | 28 | 13 | 17 | 17 | 17 |
| employment_hours_opportunity | 4 | 4 | 4 | 4 | 4 | 4 |
| market_residual_opportunity | 2 | 2 | 1 | 1 | 1 | 1 |
| wage_opportunity | 6 | 6 | 5 | 5 | 6 | 6 |
| occupation_opportunity | 12 | 12 | 8 | 8 | 9 | 10 |

## Convergence By Result Block

| group | success | message | iterations | n_function_evaluations | gradient_norm | log_likelihood | walltime_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| joint | 1 | SolveStatus.NormalCompletion (ModelStatus.OptimalLocal) | 1 | 1 | NA | -6499.88 | 52.7544 |

## Fit Statistics

| metric | value |
| --- | --- |
| log_likelihood | -6499.88 |
| ll_null_uniform | -19585.8 |
| ll_null_prior_corrected | -22321.6 |
| rho_squared | 0.708807 |
| rho_squared_adj | 0.706478 |
| rho_squared_uniform | 0.668133 |
| rho_squared_prior_corrected | 0.708807 |
| AIC | 13103.8 |
| BIC | 13673.7 |
| AIC_per_obs | 0.0308106 |
| n_observations | 425300 |
| n_groups | 4253 |
| n_parameters | 52 |
| n_obs_long | 425300 |

## Fit Moments

| group | participation_observed | participation_predicted | mean_hours_observed | mean_hours_predicted |
| --- | --- | --- | --- | --- |
| cou_f | 0.965076 | 1 | 35.6466 | 58.0623 |
| cou_m | 0.971672 | 1 | 41.6062 | 58.6181 |
| sf | 0.929504 | 0.999971 | 39.3048 | 34.1073 |
| sm | 0.93956 | 0.999972 | 36.2971 | 34.442 |

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
| cou_f | hours_bins | 8 | 1.6601 | 0.7153 |
| cou_m | hours_bins | 8 | 1.4055 | 0.667 |
| sf | hours_bins | 8 | 0.799 | 0.4403 |
| sm | hours_bins | 8 | 0.5341 | 0.284 |

## Observed vs Implied Log-Wage σ (chosen working alts)

| group | n | observed_mean_log_wage | observed_std_log_wage | implied_sigma |
| --- | --- | --- | --- | --- |
| singles_male | 712 | 2.6836 | 0.4502 | 0.42316 |
| singles_female | 855 | 2.6198 | 0.436 | 0.42316 |
| couples_male | 2504 | 2.7697 | 0.4402 | 0.42316 |
| couples_female | 2487 | 2.6221 | 0.436 | 0.42316 |

## Structural Elasticity Heuristics

These are curvature-based heuristics from the post-estimation script, not
policy-counterfactual elasticities.

| Group | Hicksian (compensated) | Marshallian (uncompensated) | Participation (extensive) | Intensive (conditional) | theta_l | theta_c | beta_l (at median X) | beta_c |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single Males | 1.704 | 1.604 | 0.511 | 1.193 | -0.704 | -0.856 | 4.467 | 0.718 |
| Single Females | 1.724 | 1.624 | 0.517 | 1.207 | -0.724 | -1.088 | 5.759 | 0.463 |
| Males in Couples | 1.733 | 1.633 | 0.520 | 1.213 | -0.733 | 0.215 | 2.702 | 5.262 |
| Females in Couples | 1.696 | 1.596 | 0.509 | 1.187 | -0.696 | 0.215 | 5.697 | 5.262 |

## Marginal Utility Diagnostics

| Group | beta_c | theta_c | MUC Positive? | MUC Diminishing? | Well-Behaved? | MUC at Median C | C where MUC=1 | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single Males | 0.717509 | -0.856029 | yes | yes | yes | 0.717509 | 0.836223 | NA |
| Single Females | 0.463007 | -1.08841 | yes | yes | yes | 0.463007 | 0.691627 | NA |
| Males in Couples | 5.26199 | 0.215302 | yes | yes | yes | 5.26199 | 8.29881 | NA |
| Females in Couples | 5.26199 | 0.215302 | yes | yes | yes | 5.26199 | 8.29881 | NA |

## Marginal Utility Distribution Summary

| group | N | n_neg_muc | pct_neg_muc | mean_muc | n_neg_mul | pct_neg_mul | mean_mul |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cou_f | 2577 | 0 | 0 | 0.00794718 | 0 | 0 | 0.00901546 |
| cou_m | 2577 | 0 | 0 | 0.00794718 | 0 | 0 | 0.00543259 |
| sf | 766 | 0 | 0 | 9.31081e-08 | 0 | 0 | 0.00963801 |
| sm | 910 | 0 | 0 | 7.46436e-07 | 0 | 0 | 0.00703391 |
| total | NA | 0 | 0 | NA | 0 | 0 | NA |

## Probability Diagnostics

| metric | value |
| --- | --- |
| prob_sum_max_error | 7.77156e-16 |
| prob_sum_mean_error | 1.31567e-16 |
| prob_sum_pct_off_by_0.01 | 0 |
| prob_sum_pct_off_by_0.001 | 0 |
| p_chosen_min | 1.55744e-08 |
| p_chosen_max | 0.999769 |
| p_chosen_mean | 0.370685 |
| p_chosen_median | 0.254708 |
| p_chosen_q10 | 0.0130419 |
| p_chosen_q25 | 0.0706689 |
| p_chosen_q75 | 0.680971 |
| p_chosen_q90 | 0.908549 |

## Worst-Fit Households

| rank | idhh | group | p_chosen | ll_i |
| --- | --- | --- | --- | --- |
| 1 | 4012700 | sm | 1.55744e-08 | -17.9776 |
| 2 | 4264600 | cou | 2.19888e-08 | -17.6327 |
| 3 | 3600001 | sf | 7.53574e-08 | -16.401 |
| 4 | 3251600 | cou | 1.95667e-07 | -15.4469 |
| 5 | 4034500 | cou | 2.37262e-07 | -15.2541 |
| 6 | 3951700 | cou | 4.07029e-07 | -14.7144 |
| 7 | 1729600 | cou | 4.10343e-07 | -14.7063 |
| 8 | 1935801 | sm | 5.17911e-07 | -14.4735 |
| 9 | 3972500 | cou | 5.99528e-07 | -14.3271 |
| 10 | 2969600 | cou | 7.33846e-07 | -14.125 |

## Identification Diagnostics

| metric | value |
| --- | --- |
| condition_number | 6.76389e+10 |
| min_eigenvalue | -26.008 |
| max_eigenvalue | 1.42219e+10 |
| n_negative_eigenvalues | 2 |

_Interpretation: ill-conditioned (kappa >= 1e10); 2 negative eigenvalue(s) - not at a local maximum or numerically singular._

## Initial → Final Movement (top 15 by |Δ|)

| block | parameter | initial_value | final_estimate | delta |
| --- | --- | --- | --- | --- |
| preference | joint.beta_l0_sm | 4.46662 | 4.46662 | 0 |
| preference | joint.beta_l_age_sm | 0.000844406 | 0.000844406 | 0 |
| preference | joint.beta_l_age2_sm | 0.00178502 | 0.00178502 | 0 |
| preference | joint.beta_l_educH_sm | -1.30348 | -1.30348 | 0 |
| preference | joint.beta_c_sm | 0.717509 | 0.717509 | 0 |
| preference | joint.theta_l_sm | -0.703775 | -0.703775 | 0 |
| preference | joint.theta_c_sm | -0.856029 | -0.856029 | 0 |
| preference | joint.beta_l0_sf | 5.75853 | 5.75853 | 0 |
| preference | joint.beta_l_age_sf | -0.016458 | -0.016458 | 0 |
| preference | joint.beta_l_age2_sf | 0.00332398 | 0.00332398 | 0 |
| preference | joint.beta_l_nkids_sf | -0.049599 | -0.049599 | 0 |
| preference | joint.beta_l_educH_sf | -2.27103 | -2.27103 | 0 |
| preference | joint.beta_c_sf | 0.463007 | 0.463007 | 0 |
| preference | joint.theta_l_sf | -0.723846 | -0.723846 | 0 |
| preference | joint.theta_c_sf | -1.08841 | -1.08841 | 0 |

## Top High-Correlation Parameter Pairs

| param_i | param_j | correlation |
| --- | --- | --- |
| beta_c_sf | theta_c_sf | -1.03508 |
| beta_l0_sf | beta_l_educH_sf | 0.996282 |
| beta_c_sm | theta_c_sm | 0.987515 |
| beta_l0_f | beta_l_educH_f | 0.978699 |
| beta_l0_sm | beta_l_educH_sm | 0.97121 |
| beta_w_pexp | beta_w_pexp2 | -0.960684 |
| beta_E | beta_E_gsur | -0.946534 |
| beta_c | theta_c | 0.934548 |
| beta_c_sm | beta_c | -0.918172 |
| theta_c_sm | beta_c | -0.916495 |

## Weakest Eigenvector Diagnostics

_None._

## Parameters At Bounds

_None._

## Parameters Near Bounds (within 5% of bound width)

| block | parameter | estimate | lower_bound | upper_bound | flags |
| --- | --- | --- | --- | --- | --- |
| preference | joint.beta_c_sm | 0.717509 | 0.05 | 50 | near_lower(delta=0.668) |
| preference | joint.beta_c_sf | 0.463007 | 0.05 | 50 | near_lower(delta=0.413) |
| wage_opportunity | joint.sigma | 0.42316 | 0.1 | 20 | near_lower(delta=0.323) |

## Top Significant Coefficients (top 15 by |t|)

| block | parameter | estimate | std_error | t_value | p_value |
| --- | --- | --- | --- | --- | --- |
| wage_opportunity | joint.sigma | 0.42316 | 0.0040911 | 103.434 | 0 |
| wage_opportunity | joint.beta_w0 | 2.04108 | 0.0265072 | 77.001 | 0 |
| preference | joint.beta_l0_f | 5.69717 | 0.121995 | 46.7001 | 0 |
| preference | joint.beta_l0_sf | 5.75853 | 0.182695 | 31.5199 | 0 |
| employment_hours_opportunity | joint.beta_h_ft | 1.46325 | 0.0499151 | 29.3148 | 0 |
| preference | joint.beta_l0_sm | 4.46662 | 0.159036 | 28.0856 | 0 |
| wage_opportunity | joint.beta_w_educH | 0.305522 | 0.0150065 | 20.3594 | 0 |
| occupation_opportunity | joint.beta_occ_3_cm | -2.20606 | 0.147763 | -14.9297 | 0 |
| occupation_opportunity | joint.beta_occ_4_cf | 1.14601 | 0.0817332 | 14.0214 | 0 |
| occupation_opportunity | joint.beta_occ_2_cm | -1.47074 | 0.113888 | -12.9138 | 0 |
| occupation_opportunity | joint.beta_occ_3_sm | -2.17256 | 0.184534 | -11.7732 | 0 |
| preference | joint.beta_c | 5.26199 | 0.4629 | 11.3675 | 0 |
| preference | joint.theta_l_f | -0.695727 | 0.0630221 | -11.0394 | 0 |
| occupation_opportunity | joint.beta_occ_2_sm | -1.51286 | 0.142327 | -10.6295 | 0 |
| employment_hours_opportunity | joint.beta_E | -2.6148 | 0.302197 | -8.65263 | 0 |

## Parameter Estimates By Block

| block | parameter | estimate | std_error | t_value | p_value | lower_bound | upper_bound | initial_value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| employment_hours_opportunity | joint.beta_E | -2.6148 | 0.302197 | -8.65263 | 0 | -25 | 25 | -2.6148 |
| employment_hours_opportunity | joint.beta_h_ft | 1.46325 | 0.0499151 | 29.3148 | 0 | -10 | 10 | 1.46325 |
| employment_hours_opportunity | joint.beta_h_pt1 | -0.52032 | 0.108553 | -4.79325 | 1.64105e-06 | -10 | 10 | -0.52032 |
| employment_hours_opportunity | joint.beta_h_pt2 | 0.372057 | 0.110967 | 3.35285 | 0.000799846 | -10 | 10 | 0.372057 |
| market_residual_opportunity | joint.beta_E_educH | 0.257516 | 0.240949 | 1.06876 | 0.285178 | -10 | 10 | 0.257516 |
| market_residual_opportunity | joint.beta_E_gsur | -0.771874 | 0.221257 | -3.48859 | 0.000485584 | -10 | 10 | -0.771874 |
| occupation_opportunity | joint.beta_occ_2_cf | 0.205 | 0.100711 | 2.03553 | 0.0417975 | -10 | 10 | 0.205 |
| occupation_opportunity | joint.beta_occ_2_cm | -1.47074 | 0.113888 | -12.9138 | 0 | -10 | 10 | -1.47074 |
| occupation_opportunity | joint.beta_occ_2_sf | -0.0147421 | 0.112918 | -0.130555 | 0.896127 | -10 | 10 | -0.0147421 |
| occupation_opportunity | joint.beta_occ_2_sm | -1.51286 | 0.142327 | -10.6295 | 0 | -10 | 10 | -1.51286 |
| occupation_opportunity | joint.beta_occ_3_cf | -0.190384 | 0.11152 | -1.70716 | 0.0877915 | -10 | 10 | -0.190384 |
| occupation_opportunity | joint.beta_occ_3_cm | -2.20606 | 0.147763 | -14.9297 | 0 | -10 | 10 | -2.20606 |
| occupation_opportunity | joint.beta_occ_3_sf | -0.574523 | 0.129046 | -4.45209 | 8.50376e-06 | -10 | 10 | -0.574523 |
| occupation_opportunity | joint.beta_occ_3_sm | -2.17256 | 0.184534 | -11.7732 | 0 | -10 | 10 | -2.17256 |
| occupation_opportunity | joint.beta_occ_4_cf | 1.14601 | 0.0817332 | 14.0214 | 0 | -10 | 10 | 1.14601 |
| occupation_opportunity | joint.beta_occ_4_cm | 0.486156 | 0.0687146 | 7.075 | 1.49436e-12 | -10 | 10 | 0.486156 |
| occupation_opportunity | joint.beta_occ_4_sf | 0.793362 | 0.0922157 | 8.60332 | 0 | -10 | 10 | 0.793362 |
| occupation_opportunity | joint.beta_occ_4_sm | 0.0175251 | 0.0860748 | 0.203603 | 0.838663 | -10 | 10 | 0.0175251 |
| preference | joint.beta_c | 5.26199 | 0.4629 | 11.3675 | 0 | 0.05 | 50 | 5.26199 |
| preference | joint.beta_c_sf | 0.463007 | NA | NA | NA | 0.05 | 50 | 0.463007 |
| preference | joint.beta_c_sm | 0.717509 | 0.265951 | 2.6979 | 0.00697783 | 0.05 | 50 | 0.717509 |
| preference | joint.beta_l0_f | 5.69717 | 0.121995 | 46.7001 | 0 | 0.05 | 50 | 5.69717 |
| preference | joint.beta_l0_m | 2.70226 | 0.420329 | 6.42893 | 1.28507e-10 | 0.05 | 50 | 2.70226 |
| preference | joint.beta_l0_sf | 5.75853 | 0.182695 | 31.5199 | 0 | 0.05 | 50 | 5.75853 |
| preference | joint.beta_l0_sm | 4.46662 | 0.159036 | 28.0856 | 0 | 0.05 | 50 | 4.46662 |
| preference | joint.beta_l_age2_f | 0.00156521 | 0.00212253 | 0.737429 | 0.460861 | -1 | 1 | 0.00156521 |
| preference | joint.beta_l_age2_m | 0.00125552 | 0.00147658 | 0.850284 | 0.395167 | -1 | 1 | 0.00125552 |
| preference | joint.beta_l_age2_sf | 0.00332398 | 0.00252889 | 1.3144 | 0.188711 | -1 | 1 | 0.00332398 |
| preference | joint.beta_l_age2_sm | 0.00178502 | 0.00204537 | 0.872715 | 0.382818 | -1 | 1 | 0.00178502 |
| preference | joint.beta_l_age_f | -0.0577507 | 0.021519 | -2.6837 | 0.00728116 | -5 | 5 | -0.0577507 |
| preference | joint.beta_l_age_m | -0.00737894 | 0.0151219 | -0.487965 | 0.625575 | -5 | 5 | -0.00737894 |
| preference | joint.beta_l_age_sf | -0.016458 | 0.0267033 | -0.616327 | 0.537679 | -5 | 5 | -0.016458 |
| preference | joint.beta_l_age_sm | 0.000844406 | 0.0246245 | 0.0342913 | 0.972645 | -5 | 5 | 0.000844406 |
| preference | joint.beta_l_educH_f | -1.48897 | 0.321195 | -4.63573 | 3.55682e-06 | -8 | 5 | -1.48897 |
| preference | joint.beta_l_educH_m | -0.925907 | 0.31475 | -2.94172 | 0.00326395 | -8 | 5 | -0.925907 |
| preference | joint.beta_l_educH_sf | -2.27103 | 0.341114 | -6.65768 | 2.78175e-11 | -8 | 5 | -2.27103 |
| preference | joint.beta_l_educH_sm | -1.30348 | 0.372398 | -3.50023 | 0.000464864 | -8 | 5 | -1.30348 |
| preference | joint.beta_l_nkids_f | 0.214934 | 0.206719 | 1.03974 | 0.298461 | -5 | 5 | 0.214934 |
| preference | joint.beta_l_nkids_sf | -0.049599 | 0.344685 | -0.143897 | 0.885582 | -5 | 5 | -0.049599 |
| preference | joint.theta_c | 0.215302 | 0.0741963 | 2.90178 | 0.00371044 | -8 | 0.95 | 0.215302 |
| preference | joint.theta_c_sf | -1.08841 | NA | NA | NA | -8 | 0.95 | -1.08841 |
| preference | joint.theta_c_sm | -0.856029 | 0.21686 | -3.94738 | 7.90099e-05 | -8 | 0.95 | -0.856029 |
| preference | joint.theta_l_f | -0.695727 | 0.0630221 | -11.0394 | 0 | -8 | 0.95 | -0.695727 |
| preference | joint.theta_l_m | -0.733006 | 0.12475 | -5.8758 | 4.20806e-09 | -8 | 0.95 | -0.733006 |
| preference | joint.theta_l_sf | -0.723846 | 0.0852958 | -8.48631 | 0 | -8 | 0.95 | -0.723846 |
| preference | joint.theta_l_sm | -0.703775 | 0.0989561 | -7.112 | 1.14375e-12 | -8 | 0.95 | -0.703775 |
| wage_opportunity | joint.beta_w0 | 2.04108 | 0.0265072 | 77.001 | 0 | -10 | 20 | 2.04108 |
| wage_opportunity | joint.beta_w_educH | 0.305522 | 0.0150065 | 20.3594 | 0 | -5 | 5 | 0.305522 |
| wage_opportunity | joint.beta_w_educL | -0.0475667 | 0.0209238 | -2.27333 | 0.0230064 | -5 | 5 | -0.0475667 |
| wage_opportunity | joint.beta_w_pexp | 0.0173702 | 0.00221956 | 7.82595 | 5.10703e-15 | -1 | 1 | 0.0173702 |
| wage_opportunity | joint.beta_w_pexp2 | -0.000205608 | 4.91101e-05 | -4.18667 | 2.83076e-05 | -0.1 | 0.1 | -0.000205608 |
| wage_opportunity | joint.sigma | 0.42316 | 0.0040911 | 103.434 | 0 | 0.1 | 20 | 0.42316 |

## Hours Distribution Shares

| group | hours_bin | observed_share | predicted_share |
| --- | --- | --- | --- |
| cou_f | 0 | 0.0349243 | 0 |
| cou_f | 1-10 | 0.0256112 | 0 |
| cou_f | 11-20 | 0.0923555 | 0.00271634 |
| cou_f | 21-30 | 0.38766 | 0.0135817 |
| cou_f | 31-40 | 0.381451 | 0.0756694 |
| cou_f | 41-50 | 0.0523865 | 0.214591 |
| cou_f | 51-60 | 0.0201785 | 0.451688 |
| cou_f | 60+ | 0.00543267 | 0.241754 |
| cou_m | 0 | 0.0283275 | 0 |
| cou_m | 1-10 | 0.00388048 | 0 |
| cou_m | 11-20 | 0.0209546 | 0.000388048 |
| cou_m | 21-30 | 0.256888 | 0.0135817 |
| cou_m | 31-40 | 0.470702 | 0.0640279 |
| cou_m | 41-50 | 0.135429 | 0.204501 |
| cou_m | 51-60 | 0.0589833 | 0.457897 |
| cou_m | 60+ | 0.0248351 | 0.259604 |
| sf | 0 | 0.0704961 | 0 |
| sf | 1-10 | 0.0104439 | 0 |
| sf | 11-20 | 0.0483029 | 0 |
| sf | 21-30 | 0.25718 | 0.656658 |
| sf | 31-40 | 0.480418 | 0.343342 |
| sf | 41-50 | 0.0770235 | 0 |
| sf | 51-60 | 0.0443864 | 0 |
| sf | 60+ | 0.0117493 | 0 |
| sm | 0 | 0.0604396 | 0 |
| sm | 1-10 | 0.0307692 | 0 |
| sm | 11-20 | 0.0835165 | 0 |
| sm | 21-30 | 0.347253 | 0.601099 |
| sm | 31-40 | 0.385714 | 0.398901 |
| sm | 41-50 | 0.0626374 | 0 |
| sm | 51-60 | 0.021978 | 0 |
| sm | 60+ | 0.00769231 | 0 |

## Wage Distribution Summary

Observed values use chosen working alternatives. Predicted values use
choice-probability weights over working alternatives.

| group | n_observed_working | predicted_worker_weight | obs_mean | pred_mean | obs_q10 | obs_q50 | obs_q90 | pred_q10 | pred_q50 | pred_q90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | 712 | 765.361 | 16.2131 | 18.5389 | 9.15372 | 14.2557 | 25.4434 | 9.7124 | 16.7912 | 29.7178 |
| singles_female | 855 | 908.591 | 15.1069 | 17.8953 | 8.65411 | 13.8516 | 22.9432 | 9.27435 | 15.9754 | 29.1144 |
| couples_male | 2504 | 2572.19 | 17.656 | 19.6818 | 10.0631 | 15.2895 | 27.8735 | 10.0692 | 16.3188 | 33.4694 |
| couples_female | 2487 | 2566.34 | 15.1712 | 18.1835 | 8.86239 | 13.8393 | 22.4802 | 9.32536 | 14.7541 | 31.5051 |

## Occupation Distribution Shares

Observed shares use chosen working alternatives. Predicted shares use
choice-probability weights over working alternatives. Category labels
are reported for loc4-style variables when available.

| group | occupation_column | category | label | observed_share | predicted_share | observed_count | predicted_weight |
| --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | loc4 | -2 | unknown_observed_working | 0.00561798 | 0.000502043 | 4 | 0.384244 |
| singles_male | loc4 | 1 | routine_manual_ref | 0.407303 | 0.287971 | 290 | 220.402 |
| singles_male | loc4 | 2 | nonroutine_manual | 0.0941011 | 0.222801 | 67 | 170.523 |
| singles_male | loc4 | 3 | routine_cognitive | 0.0505618 | 0.20878 | 36 | 159.792 |
| singles_male | loc4 | 4 | nonroutine_cognitive | 0.442416 | 0.279946 | 315 | 214.26 |
| singles_female | loc4 | -2 | unknown_observed_working | 0.00350877 | 0.000801495 | 3 | 0.728232 |
| singles_female | loc4 | 1 | routine_manual_ref | 0.191813 | 0.249065 | 164 | 226.298 |
| singles_female | loc4 | 2 | nonroutine_manual | 0.20117 | 0.235892 | 172 | 214.33 |
| singles_female | loc4 | 3 | routine_cognitive | 0.130994 | 0.23581 | 112 | 214.255 |
| singles_female | loc4 | 4 | nonroutine_cognitive | 0.472515 | 0.278431 | 404 | 252.98 |
| couples_male | loc4_male | -2 | unknown_observed_working | 0.0123802 | 0.0065084 | 31 | 16.7409 |
| couples_male | loc4_male | 1 | routine_manual_ref | 0.360224 | 0.340241 | 902 | 875.165 |
| couples_male | loc4_male | 2 | nonroutine_manual | 0.0802716 | 0.158405 | 201 | 407.449 |
| couples_male | loc4_male | 3 | routine_cognitive | 0.0391374 | 0.118667 | 98 | 305.234 |
| couples_male | loc4_male | 4 | nonroutine_cognitive | 0.507987 | 0.376178 | 1272 | 967.603 |
| couples_female | loc4_female | -2 | unknown_observed_working | 0.00120627 | 0.000618965 | 3 | 1.58847 |
| couples_female | loc4_female | 1 | routine_manual_ref | 0.170084 | 0.224623 | 423 | 576.459 |
| couples_female | loc4_female | 2 | nonroutine_manual | 0.206273 | 0.232771 | 513 | 597.371 |
| couples_female | loc4_female | 3 | routine_cognitive | 0.152392 | 0.196098 | 379 | 503.254 |
| couples_female | loc4_female | 4 | nonroutine_cognitive | 0.470044 | 0.345889 | 1169 | 887.668 |

## Notes For Use

- This Markdown file is the preferred low-token artifact for LLM review.
- Use the HTML report only when plots or visual diagnostics are needed.
- Generated output folders remain local unless explicitly added to Git.
