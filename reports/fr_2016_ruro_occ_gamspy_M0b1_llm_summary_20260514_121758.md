# RURO Low-Token Post-Estimation Summary

Generated: 2026-05-14T12:18:02

## Purpose

Compact text-only report for Git, paper drafting, and LLM review.
Figures and large HTML output are intentionally omitted.

## Sources

| item | path_or_value |
| --- | --- |
| estimation_results_json | U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0b1\run_2026-05-14_12-07-18\estimation_results.json |
| html_report | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0b1\run_2026-05-14_12-17-36\fr_2016_ruro_occ_gamspy_M0b1_post_estimation_report_20260514_121758.html |
| post_output_dir | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0b1\run_2026-05-14_12-17-36 |
| params_csv | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0b1\run_2026-05-14_12-17-36\fr_2016_ruro_occ_gamspy_M0b1_params.csv |
| elasticities_csv | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0b1\run_2026-05-14_12-17-36\fr_2016_ruro_occ_gamspy_M0b1_elasticities.csv |
| mnl_base | Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl |
| spec_config | scripts\enhanced\estimation_spec_ruro_occ_M0b1.yaml |

## Run Metadata

| field | value |
| --- | --- |
| specification | ruro_occ_M0b1 |
| model_family | regular |
| market_opportunity_tier | NA |
| prior_correction_applied | 1 |
| prior_correction_form | -log(prior) |
| market_centering_applied | 1 |
| wage_spec | vw |
| estimation_walltime_seconds | 344.439 |

## Source Environment

| field | value |
| --- | --- |
| git_sha | aa24a610edda |
| git_branch | main |
| git_dirty | 1 |

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
| fit | cou_f: predicted participation is very high (0.9998) |
| fit | cou_m: predicted participation is very high (0.9998) |
| probability | minimum chosen probability is very small (1.979e-87) |
| hessian | negative eigenvalues present; inspect SE and local optimum diagnostics |

## Convergence Health Summary

| metric | value |
| --- | --- |
| n_estimated_params | 48 |
| log_likelihood | -6506.79 |
| AIC | 13109.6 |
| BIC | 13635.7 |
| rho_squared | 0.708498 |
| n_significant_p<0.05 | 30 |
| pct_significant_p<0.05 | 62.5% |
| n_low_t<1.0 | 9 |
| pct_low_t<1.0 | 18.8% |
| n_degenerate_se | 0 |
| n_at_bound_strict | 1 |
| hessian_condition_number | 9.9009e+09 |
| n_negative_eigenvalues | 1 |
| p_chosen_min | 1.97891e-87 |
| p_chosen_q10 | 1.68898e-64 |
| review_priority_flags | negative_eigenvalues_present, parameters_at_bounds, very_small_p_chosen_min |

## Model Index Equation

V_ij = U_ij + O^E_ij + O^H_ij + O^W_ij + O^Occ_ij - log_prior_ij

P_ij = exp(V_ij) / sum_k exp(V_ik)

## Utility / Preference Parameters By Group

Utility uses Box-Cox consumption and leisure. This table gives the
group-level consumption and leisure parameters resolved from the
estimated parameter vector.

| group | beta_c | theta_c | beta_l0 | beta_l_shifters | theta_l | beta_cl |
| --- | --- | --- | --- | --- | --- | --- |
| f | 5.88506 | 0.270948 | 3.00236 | beta_l_age=-0.0470642; beta_l_age2=0.00241227; beta_l_nkids=0.235972; beta_ll=2 | -0.659027 | NA |
| m | 5.88506 | 0.270948 | 0.379145 | beta_l_age=-0.00359813; beta_l_age2=0.00135636; beta_ll=2 | -0.682183 | NA |
| sf | 0.682013 | 0.270948 | 4.5571 | beta_l_age=0.00270705; beta_l_age2=0.00417307; beta_l_nkids=0.0833601; beta_ll=2 | -0.725936 | NA |
| sm | 0.752322 | 0.270948 | 3.96769 | beta_l_age=0.00976449; beta_l_age2=0.00200049; beta_ll=2 | -0.706253 | NA |

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
| employment_hours | beta_E * working | beta_E | joint | -2.78273 |
| employment_hours | beta_h_pt1 * working_pt1 | beta_h_pt1 | joint | -0.497428 |
| employment_hours | beta_h_pt2 * working_pt2 | beta_h_pt2 | joint | 0.374286 |
| employment_hours | beta_h_ft * working_ft | beta_h_ft | joint | 1.44936 |
| employment_hours | beta_E_gsur * gsur * working | beta_E_gsur | joint | -0.741392 |
| employment_hours | beta_E_educH * educH * working | beta_E_educH | joint | 0.552771 |
| wage_mean | beta_w0 * intercept | beta_w0 | joint | 2.04217 |
| wage_mean | beta_w_educL * educL | beta_w_educL | joint | -0.0479302 |
| wage_mean | beta_w_educH * educH | beta_w_educH | joint | 0.302264 |
| wage_mean | beta_w_pexp * pexp_years | beta_w_pexp | joint | 0.0168791 |
| wage_mean | beta_w_pexp2 * pexp_years2 | beta_w_pexp2 | joint | -0.000197949 |
| wage_sigma | sigma | sigma | joint | 0.419661 |
| occupation:sm | beta_occ_2_sm * loc4_2 * working | beta_occ_2_sm | joint | -1.51396 |
| occupation:sm | beta_occ_3_sm * loc4_3 * working | beta_occ_3_sm | joint | -2.17079 |
| occupation:sm | beta_occ_4_sm * loc4_4 * working | beta_occ_4_sm | joint | 0.0185186 |
| occupation:sf | beta_occ_2_sf * loc4_2 * working | beta_occ_2_sf | joint | -0.0181403 |
| occupation:sf | beta_occ_3_sf * loc4_3 * working | beta_occ_3_sf | joint | -0.569472 |
| occupation:sf | beta_occ_4_sf * loc4_4 * working | beta_occ_4_sf | joint | 0.790675 |
| occupation:cm | beta_occ_2_cm * loc4_2 * working | beta_occ_2_cm | joint | -1.47328 |
| occupation:cm | beta_occ_3_cm * loc4_3 * working | beta_occ_3_cm | joint | -2.21388 |
| occupation:cm | beta_occ_4_cm * loc4_4 * working | beta_occ_4_cm | joint | 0.475118 |
| occupation:cf | beta_occ_2_cf * loc4_2 * working | beta_occ_2_cf | joint | 0.187389 |
| occupation:cf | beta_occ_3_cf * loc4_3 * working | beta_occ_3_cf | joint | -0.207938 |
| occupation:cf | beta_occ_4_cf * loc4_4 * working | beta_occ_4_cf | joint | 1.12163 |

## Per-Block Parameter Counts and Significance

| block | n_params | n_estimable | n_sig_p<0.001 | n_sig_p<0.01 | n_sig_p<0.05 | n_sig_p<0.10 |
| --- | --- | --- | --- | --- | --- | --- |
| preference | 24 | 24 | 9 | 9 | 10 | 10 |
| employment_hours_opportunity | 4 | 4 | 4 | 4 | 4 | 4 |
| market_residual_opportunity | 2 | 2 | 1 | 1 | 2 | 2 |
| wage_opportunity | 6 | 6 | 5 | 5 | 6 | 6 |
| occupation_opportunity | 12 | 12 | 8 | 8 | 8 | 10 |

## Convergence By Result Block

| group | success | message | iterations | n_function_evaluations | gradient_norm | log_likelihood | walltime_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| joint | 1 | SolveStatus.NormalCompletion (ModelStatus.OptimalLocal) | 25 | 25 | NA | -6506.79 | 114.813 |

## Fit Statistics

| metric | value |
| --- | --- |
| log_likelihood | -6506.79 |
| ll_null_uniform | -19585.8 |
| ll_null_prior_corrected | -22321.6 |
| rho_squared | 0.708498 |
| rho_squared_adj | 0.706347 |
| rho_squared_uniform | 0.66778 |
| rho_squared_prior_corrected | 0.708498 |
| AIC | 13109.6 |
| BIC | 13635.7 |
| AIC_per_obs | 0.0308243 |
| n_observations | 425300 |
| n_groups | 4253 |
| n_parameters | 48 |
| n_obs_long | 425300 |

## Fit Moments

| group | participation_observed | participation_predicted | mean_hours_observed | mean_hours_predicted |
| --- | --- | --- | --- | --- |
| cou_f | 0.965076 | 0.999757 | 35.6466 | 60.2118 |
| cou_m | 0.971672 | 0.999769 | 41.6062 | 60.4315 |
| sf | 0.93956 | 0.953009 | 36.2971 | 35.0134 |
| sm | 0.929504 | 0.911006 | 39.3048 | 35.6362 |

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
| cou_f | hours_bins | 8 | 1.7408 | 0.7605 |
| cou_m | hours_bins | 8 | 1.4754 | 0.712 |
| sf | hours_bins | 8 | 0.4154 | 0.2281 |
| sm | hours_bins | 8 | 0.7232 | 0.3869 |

## Observed vs Implied Log-Wage σ (chosen working alts)

| group | n | observed_mean_log_wage | observed_std_log_wage | implied_sigma |
| --- | --- | --- | --- | --- |
| singles_male | 712 | 2.6836 | 0.4502 | 0.419661 |
| singles_female | 855 | 2.6198 | 0.436 | 0.419661 |
| couples_male | 2504 | 2.7697 | 0.4402 | 0.419661 |
| couples_female | 2487 | 2.6221 | 0.436 | 0.419661 |

## Structural Elasticity Heuristics

These are curvature-based heuristics from the post-estimation script, not
policy-counterfactual elasticities.

| Group | Hicksian (compensated) | Marshallian (uncompensated) | Participation (extensive) | Intensive (conditional) | theta_l | theta_c | beta_l (at median X) | beta_c |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single Males | 1.706 | 1.606 | 0.512 | 1.194 | -0.706 | 0.271 | 3.968 | 0.752 |
| Single Females | 1.726 | 1.626 | 0.518 | 1.208 | -0.726 | 0.271 | 4.557 | 0.682 |
| Males in Couples | 1.682 | 1.582 | 0.505 | 1.178 | -0.682 | 0.271 | 0.379 | 5.885 |
| Females in Couples | 1.659 | 1.559 | 0.498 | 1.161 | -0.659 | 0.271 | 3.002 | 5.885 |

## Marginal Utility Diagnostics

| Group | beta_c | theta_c | MUC Positive? | MUC Diminishing? | Well-Behaved? | MUC at Median C | C where MUC=1 | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single Males | 0.752322 | 0.270948 | yes | yes | yes | 0.752322 | 0.676815 | NA |
| Single Females | 0.682013 | 0.270948 | yes | yes | yes | 0.682013 | 0.591592 | NA |
| Males in Couples | 5.88506 | 0.270948 | yes | yes | yes | 5.88506 | 11.3717 | NA |
| Females in Couples | 5.88506 | 0.270948 | yes | yes | yes | 5.88506 | 11.3717 | NA |

## Marginal Utility Distribution Summary

| group | N | n_neg_muc | pct_neg_muc | mean_muc | n_neg_mul | pct_neg_mul | mean_mul |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cou_f | 2577 | 0 | 0 | 0.0140504 | 0 | 0 | 0.00685404 |
| cou_m | 2577 | 0 | 0 | 0.0140504 | 0 | 0 | 0.00106494 |
| sf | 766 | 0 | 0 | 0.00286155 | 0 | 0 | 0.0100861 |
| sm | 910 | 0 | 0 | 0.0031466 | 0 | 0 | 0.00763955 |
| total | NA | 0 | 0 | NA | 0 | 0 | NA |

## Probability Diagnostics

| metric | value |
| --- | --- |
| prob_sum_max_error | 6.66134e-16 |
| prob_sum_mean_error | 1.06141e-16 |
| prob_sum_pct_off_by_0.01 | 0 |
| prob_sum_pct_off_by_0.001 | 0 |
| p_chosen_min | 1.97891e-87 |
| p_chosen_max | 0.849088 |
| p_chosen_mean | 0.0485696 |
| p_chosen_median | 8.33959e-50 |
| p_chosen_q10 | 1.68898e-64 |
| p_chosen_q25 | 3.7343e-59 |
| p_chosen_q75 | 0.0468114 |
| p_chosen_q90 | 0.170107 |

## Worst-Fit Households

| rank | idhh | group | p_chosen | ll_i |
| --- | --- | --- | --- | --- |
| 1 | 1483000 | cou | 1.76584e-61 | -46.0517 |
| 2 | 1485200 | cou | 5.11422e-52 | -46.0517 |
| 3 | 1485300 | cou | 3.19767e-42 | -46.0517 |
| 4 | 1487600 | cou | 4.8499e-41 | -46.0517 |
| 5 | 1498600 | cou | 1.88353e-56 | -46.0517 |
| 6 | 1500001 | cou | 2.09318e-56 | -46.0517 |
| 7 | 1501900 | cou | 1.0926e-44 | -46.0517 |
| 8 | 1502700 | cou | 1.6767e-58 | -46.0517 |
| 9 | 1505900 | cou | 3.06884e-54 | -46.0517 |
| 10 | 1511600 | cou | 2.08366e-53 | -46.0517 |

## Identification Diagnostics

| metric | value |
| --- | --- |
| condition_number | 9.9009e+09 |
| min_eigenvalue | -4.61066 |
| max_eigenvalue | 1.48778e+10 |
| n_negative_eigenvalues | 1 |

_Interpretation: weakly conditioned (1e6 <= kappa < 1e10); 1 negative eigenvalue(s) - not at a local maximum or numerically singular._

## Initial → Final Movement (top 15 by |Δ|)

| block | parameter | initial_value | final_estimate | delta |
| --- | --- | --- | --- | --- |
| preference | joint.beta_c | 1 | 5.88506 | 4.88506 |
| preference | joint.beta_l0_sf | 1 | 4.5571 | 3.5571 |
| preference | joint.beta_l0_sm | 1 | 3.96769 | 2.96769 |
| employment_hours_opportunity | joint.beta_E | 0 | -2.78273 | -2.78273 |
| occupation_opportunity | joint.beta_occ_3_cm | 0 | -2.21388 | -2.21388 |
| occupation_opportunity | joint.beta_occ_3_sm | 0 | -2.17079 | -2.17079 |
| preference | joint.beta_l0_f | 1 | 3.00236 | 2.00236 |
| preference | joint.beta_ll | 0 | 2 | 2 |
| occupation_opportunity | joint.beta_occ_2_sm | 0 | -1.51396 | -1.51396 |
| occupation_opportunity | joint.beta_occ_2_cm | 0 | -1.47328 | -1.47328 |
| employment_hours_opportunity | joint.beta_h_ft | 0 | 1.44936 | 1.44936 |
| preference | joint.theta_c | -1 | 0.270948 | 1.27095 |
| occupation_opportunity | joint.beta_occ_4_cf | 0 | 1.12163 | 1.12163 |
| occupation_opportunity | joint.beta_occ_4_sf | 0 | 0.790675 | 0.790675 |
| market_residual_opportunity | joint.beta_E_gsur | 0 | -0.741392 | -0.741392 |

## Top High-Correlation Parameter Pairs

| param_i | param_j | correlation |
| --- | --- | --- |
| theta_c_singles | beta_c | -1.24427 |
| beta_c_sm | beta_c | -1.18032 |
| beta_c_sf | beta_c | -1.16868 |
| theta_c_singles | sigma | 1.1373 |
| beta_c_sm | sigma | 1.08606 |
| beta_c_sf | sigma | 1.08605 |
| beta_c_sm | beta_c_sf | -1.03403 |
| beta_c_sf | theta_c_singles | -1.02851 |
| beta_c_sm | theta_c_singles | -1.0224 |
| beta_c | theta_c | 1.01123 |

## Weakest Eigenvector Diagnostics

_None._

## Parameters At Bounds

| parameter | estimate | bound | side |
| --- | --- | --- | --- |
| joint.beta_ll | 2 | 2 | upper |

## Parameters Near Bounds (within 5% of bound width)

| block | parameter | estimate | lower_bound | upper_bound | flags |
| --- | --- | --- | --- | --- | --- |
| preference | joint.beta_c_sm | 0.752322 | 0.05 | 50 | near_lower(delta=0.702) |
| preference | joint.beta_c_sf | 0.682013 | 0.05 | 50 | near_lower(delta=0.632) |
| preference | joint.beta_l0_m | 0.379145 | 0.05 | 50 | near_lower(delta=0.329) |
| wage_opportunity | joint.sigma | 0.419661 | 0.1 | 20 | near_lower(delta=0.32) |

## Top Significant Coefficients (top 15 by |t|)

| block | parameter | estimate | std_error | t_value | p_value |
| --- | --- | --- | --- | --- | --- |
| wage_opportunity | joint.sigma | 0.419661 | 0.00326189 | 128.656 | 0 |
| wage_opportunity | joint.beta_w0 | 2.04217 | 0.0254932 | 80.1063 | 0 |
| employment_hours_opportunity | joint.beta_h_ft | 1.44936 | 0.0500127 | 28.9798 | 0 |
| wage_opportunity | joint.beta_w_educH | 0.302264 | 0.0145336 | 20.7976 | 0 |
| occupation_opportunity | joint.beta_occ_3_cm | -2.21388 | 0.147244 | -15.0355 | 0 |
| occupation_opportunity | joint.beta_occ_4_cf | 1.12163 | 0.0810774 | 13.8341 | 0 |
| occupation_opportunity | joint.beta_occ_2_cm | -1.47328 | 0.113308 | -13.0025 | 0 |
| preference | joint.beta_c | 5.88506 | 0.484368 | 12.15 | 0 |
| occupation_opportunity | joint.beta_occ_3_sm | -2.17079 | 0.184455 | -11.7686 | 0 |
| occupation_opportunity | joint.beta_occ_2_sm | -1.51396 | 0.142198 | -10.6468 | 0 |
| employment_hours_opportunity | joint.beta_E | -2.78273 | 0.297186 | -9.3636 | 0 |
| occupation_opportunity | joint.beta_occ_4_sf | 0.790675 | 0.0920727 | 8.58751 | 0 |
| wage_opportunity | joint.beta_w_pexp | 0.0168791 | 0.00217889 | 7.74664 | 9.32587e-15 |
| occupation_opportunity | joint.beta_occ_4_cm | 0.475118 | 0.0684317 | 6.94295 | 3.84004e-12 |
| preference | joint.theta_l_f | -0.659027 | 0.0978423 | -6.7356 | 1.63254e-11 |

## Parameter Estimates By Block

| block | parameter | estimate | std_error | t_value | p_value | lower_bound | upper_bound | initial_value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| employment_hours_opportunity | joint.beta_E | -2.78273 | 0.297186 | -9.3636 | 0 | -25 | 25 | 0 |
| employment_hours_opportunity | joint.beta_h_ft | 1.44936 | 0.0500127 | 28.9798 | 0 | -10 | 10 | 0 |
| employment_hours_opportunity | joint.beta_h_pt1 | -0.497428 | 0.107735 | -4.61715 | 3.8905e-06 | -10 | 10 | 0 |
| employment_hours_opportunity | joint.beta_h_pt2 | 0.374286 | 0.111074 | 3.36969 | 0.000752541 | -10 | 10 | 0 |
| market_residual_opportunity | joint.beta_E_educH | 0.552771 | 0.234466 | 2.35757 | 0.0183948 | -10 | 10 | 0 |
| market_residual_opportunity | joint.beta_E_gsur | -0.741392 | 0.218326 | -3.39581 | 0.00068426 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_cf | 0.187389 | 0.0998175 | 1.87731 | 0.0604752 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_cm | -1.47328 | 0.113308 | -13.0025 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_sf | -0.0181403 | 0.112746 | -0.160896 | 0.872176 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_sm | -1.51396 | 0.142198 | -10.6468 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_cf | -0.207938 | 0.11096 | -1.87398 | 0.0609329 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_cm | -2.21388 | 0.147244 | -15.0355 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_sf | -0.569472 | 0.129091 | -4.41141 | 1.02702e-05 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_sm | -2.17079 | 0.184455 | -11.7686 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_cf | 1.12163 | 0.0810774 | 13.8341 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_cm | 0.475118 | 0.0684317 | 6.94295 | 3.84004e-12 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_sf | 0.790675 | 0.0920727 | 8.58751 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_sm | 0.0185186 | 0.0861295 | 0.215009 | 0.82976 | -10 | 10 | 0 |
| preference | joint.beta_c | 5.88506 | 0.484368 | 12.15 | 0 | 0.05 | 50 | 1 |
| preference | joint.beta_c_sf | 0.682013 | NA | NA | NA | 0.05 | 50 | 1 |
| preference | joint.beta_c_sm | 0.752322 | NA | NA | NA | 0.05 | 50 | 1 |
| preference | joint.beta_l0_f | 3.00236 | 0.731482 | 4.10449 | 4.05213e-05 | 0.05 | 50 | 1 |
| preference | joint.beta_l0_m | 0.379145 | 0.398941 | 0.950378 | 0.34192 | 0.05 | 50 | 1 |
| preference | joint.beta_l0_sf | 4.5571 | 0.796001 | 5.72499 | 1.03438e-08 | 0.05 | 50 | 1 |
| preference | joint.beta_l0_sm | 3.96769 | 0.738758 | 5.37077 | 7.84029e-08 | 0.05 | 50 | 1 |
| preference | joint.beta_l_age2_f | 0.00241227 | 0.00213783 | 1.12837 | 0.259163 | -1 | 1 | 0 |
| preference | joint.beta_l_age2_m | 0.00135636 | 0.00139726 | 0.970729 | 0.331683 | -1 | 1 | 0 |
| preference | joint.beta_l_age2_sf | 0.00417307 | 0.00258105 | 1.61681 | 0.105919 | -1 | 1 | 0 |
| preference | joint.beta_l_age2_sm | 0.00200049 | 0.00208015 | 0.961705 | 0.336198 | -1 | 1 | 0 |
| preference | joint.beta_l_age_f | -0.0470642 | 0.0213125 | -2.20829 | 0.027224 | -5 | 5 | 0 |
| preference | joint.beta_l_age_m | -0.00359813 | 0.0142541 | -0.252428 | 0.80071 | -5 | 5 | 0 |
| preference | joint.beta_l_age_sf | 0.00270705 | 0.0272972 | 0.0991697 | 0.921004 | -5 | 5 | 0 |
| preference | joint.beta_l_age_sm | 0.00976449 | 0.0247546 | 0.394452 | 0.693248 | -5 | 5 | 0 |
| preference | joint.beta_l_nkids_f | 0.235972 | 0.21203 | 1.11292 | 0.265742 | -5 | 5 | 0 |
| preference | joint.beta_l_nkids_sf | 0.0833601 | 0.361151 | 0.230818 | 0.817456 | -5 | 5 | 0 |
| preference | joint.beta_ll | 2 | NA | NA | NA | -2 | 2 | 0 |
| preference | joint.theta_c | 0.270948 | 0.0777493 | 3.4849 | 0.000492328 | -8 | 0.95 | -1 |
| preference | joint.theta_c_singles | -0.836942 | NA | NA | NA | -8 | 0.95 | -1 |
| preference | joint.theta_l_f | -0.659027 | 0.0978423 | -6.7356 | 1.63254e-11 | -8 | 0.95 | -1 |
| preference | joint.theta_l_m | -0.682183 | 0.140973 | -4.8391 | 1.30426e-06 | -8 | 0.95 | -1 |
| preference | joint.theta_l_sf | -0.725936 | 0.134159 | -5.41101 | 6.26715e-08 | -8 | 0.95 | -1 |
| preference | joint.theta_l_sm | -0.706253 | 0.154297 | -4.57723 | 4.71169e-06 | -8 | 0.95 | -1 |
| wage_opportunity | joint.beta_w0 | 2.04217 | 0.0254932 | 80.1063 | 0 | -10 | 20 | 2 |
| wage_opportunity | joint.beta_w_educH | 0.302264 | 0.0145336 | 20.7976 | 0 | -5 | 5 | 0.2 |
| wage_opportunity | joint.beta_w_educL | -0.0479302 | 0.0204396 | -2.34497 | 0.0190287 | -5 | 5 | -0.1 |
| wage_opportunity | joint.beta_w_pexp | 0.0168791 | 0.00217889 | 7.74664 | 9.32587e-15 | -1 | 1 | 0.02 |
| wage_opportunity | joint.beta_w_pexp2 | -0.000197949 | 4.82056e-05 | -4.10636 | 4.01942e-05 | -0.1 | 0.1 | -0.0003 |
| wage_opportunity | joint.sigma | 0.419661 | 0.00326189 | 128.656 | 0 | 0.1 | 20 | 0.5 |

## Hours Distribution Shares

| group | hours_bin | observed_share | predicted_share |
| --- | --- | --- | --- |
| cou_f | 0 | 0.0349243 | 0 |
| cou_f | 1-10 | 0.0256112 | 0 |
| cou_f | 11-20 | 0.0923555 | 0.00155219 |
| cou_f | 21-30 | 0.38766 | 0.00620877 |
| cou_f | 31-40 | 0.381451 | 0.0438494 |
| cou_f | 41-50 | 0.0523865 | 0.16298 |
| cou_f | 51-60 | 0.0201785 | 0.462553 |
| cou_f | 60+ | 0.00543267 | 0.322856 |
| cou_m | 0 | 0.0283275 | 0 |
| cou_m | 1-10 | 0.00388048 | 0 |
| cou_m | 11-20 | 0.0209546 | 0.000388048 |
| cou_m | 21-30 | 0.256888 | 0.00543267 |
| cou_m | 31-40 | 0.470702 | 0.0372526 |
| cou_m | 41-50 | 0.135429 | 0.166861 |
| cou_m | 51-60 | 0.0589833 | 0.458285 |
| cou_m | 60+ | 0.0248351 | 0.331781 |
| sf | 0 | 0.0604396 | 0 |
| sf | 1-10 | 0.0307692 | 0.0021978 |
| sf | 11-20 | 0.0835165 | 0.0549451 |
| sf | 21-30 | 0.347253 | 0.554945 |
| sf | 31-40 | 0.385714 | 0.38022 |
| sf | 41-50 | 0.0626374 | 0.00769231 |
| sf | 51-60 | 0.021978 | 0 |
| sf | 60+ | 0.00769231 | 0 |
| sm | 0 | 0.0704961 | 0 |
| sm | 1-10 | 0.0104439 | 0.00261097 |
| sm | 11-20 | 0.0483029 | 0.0744125 |
| sm | 21-30 | 0.25718 | 0.592689 |
| sm | 31-40 | 0.480418 | 0.325065 |
| sm | 41-50 | 0.0770235 | 0.00522193 |
| sm | 51-60 | 0.0443864 | 0 |
| sm | 60+ | 0.0117493 | 0 |

## Wage Distribution Summary

Observed values use chosen working alternatives. Predicted values use
choice-probability weights over working alternatives.

| group | n_observed_working | predicted_worker_weight | obs_mean | pred_mean | obs_q10 | obs_q50 | obs_q90 | pred_q10 | pred_q50 | pred_q90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | 712 | 722.106 | 16.2131 | 12.5447 | 9.15372 | 14.2557 | 25.4434 | 6.24207 | 11.4832 | 19.9548 |
| singles_female | 855 | 858.75 | 15.1069 | 12.6705 | 8.65411 | 13.8516 | 22.9432 | 6.40551 | 11.6865 | 19.9643 |
| couples_male | 2504 | 2576.4 | 17.656 | 137.207 | 10.0631 | 15.2895 | 27.8735 | 96.0222 | 145.227 | 166.241 |
| couples_female | 2487 | 2576.37 | 15.1712 | 137.315 | 8.86239 | 13.8393 | 22.4802 | 97.3791 | 145.076 | 166.368 |

## Occupation Distribution Shares

Observed shares use chosen working alternatives. Predicted shares use
choice-probability weights over working alternatives. Category labels
are reported for loc4-style variables when available.

| group | occupation_column | category | label | observed_share | predicted_share | observed_count | predicted_weight |
| --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | loc4 | -2 | unknown_observed_working | 0.00561798 | 0.000342788 | 4 | 0.247529 |
| singles_male | loc4 | 1 | routine_manual_ref | 0.407303 | 0.283243 | 290 | 204.531 |
| singles_male | loc4 | 2 | nonroutine_manual | 0.0941011 | 0.233968 | 67 | 168.949 |
| singles_male | loc4 | 3 | routine_cognitive | 0.0505618 | 0.208145 | 36 | 150.303 |
| singles_male | loc4 | 4 | nonroutine_cognitive | 0.442416 | 0.274301 | 315 | 198.074 |
| singles_female | loc4 | -2 | unknown_observed_working | 0.00350877 | 0.000866197 | 3 | 0.743847 |
| singles_female | loc4 | 1 | routine_manual_ref | 0.191813 | 0.258961 | 164 | 222.382 |
| singles_female | loc4 | 2 | nonroutine_manual | 0.20117 | 0.239714 | 172 | 205.854 |
| singles_female | loc4 | 3 | routine_cognitive | 0.130994 | 0.227024 | 112 | 194.957 |
| singles_female | loc4 | 4 | nonroutine_cognitive | 0.472515 | 0.273436 | 404 | 234.813 |
| couples_male | loc4_male | -2 | unknown_observed_working | 0.0123802 | 8.76895e-35 | 31 | 2.25923e-31 |
| couples_male | loc4_male | 1 | routine_manual_ref | 0.360224 | 0.27472 | 902 | 707.791 |
| couples_male | loc4_male | 2 | nonroutine_manual | 0.0802716 | 0.140084 | 201 | 360.913 |
| couples_male | loc4_male | 3 | routine_cognitive | 0.0391374 | 0.0889366 | 98 | 229.137 |
| couples_male | loc4_male | 4 | nonroutine_cognitive | 0.507987 | 0.496259 | 1272 | 1278.56 |
| couples_female | loc4_female | -2 | unknown_observed_working | 0.00120627 | 6.21956e-51 | 3 | 1.60239e-47 |
| couples_female | loc4_female | 1 | routine_manual_ref | 0.170084 | 0.235774 | 423 | 607.442 |
| couples_female | loc4_female | 2 | nonroutine_manual | 0.206273 | 0.153083 | 513 | 394.399 |
| couples_female | loc4_female | 3 | routine_cognitive | 0.152392 | 0.100035 | 379 | 257.728 |
| couples_female | loc4_female | 4 | nonroutine_cognitive | 0.470044 | 0.511108 | 1169 | 1316.81 |

## Notes For Use

- This Markdown file is the preferred low-token artifact for LLM review.
- Use the HTML report only when plots or visual diagnostics are needed.
- Generated output folders remain local unless explicitly added to Git.
