# RURO Low-Token Post-Estimation Summary

Generated: 2026-05-14T12:54:14

## Purpose

Compact text-only report for Git, paper drafting, and LLM review.
Figures and large HTML output are intentionally omitted.

## Sources

| item | path_or_value |
| --- | --- |
| estimation_results_json | U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0b2\run_2026-05-14_12-46-04\estimation_results.json |
| html_report | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0b2\run_2026-05-14_12-53-49\fr_2016_ruro_occ_gamspy_M0b2_post_estimation_report_20260514_125410.html |
| post_output_dir | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0b2\run_2026-05-14_12-53-49 |
| params_csv | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0b2\run_2026-05-14_12-53-49\fr_2016_ruro_occ_gamspy_M0b2_params.csv |
| elasticities_csv | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0b2\run_2026-05-14_12-53-49\fr_2016_ruro_occ_gamspy_M0b2_elasticities.csv |
| mnl_base | Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl |
| spec_config | scripts\enhanced\estimation_spec_ruro_occ_M0b2.yaml |

## Run Metadata

| field | value |
| --- | --- |
| specification | ruro_occ_M0b2 |
| model_family | regular |
| market_opportunity_tier | NA |
| prior_correction_applied | 1 |
| prior_correction_form | -log(prior) |
| market_centering_applied | 1 |
| wage_spec | vw |
| estimation_walltime_seconds | 294.68 |

## Source Environment

| field | value |
| --- | --- |
| git_sha | f93c55b2815a |
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
| probability | minimum chosen probability is very small (1.162e-09) |
| hessian | negative eigenvalues present; inspect SE and local optimum diagnostics |

## Convergence Health Summary

| metric | value |
| --- | --- |
| n_estimated_params | 48 |
| log_likelihood | -6511.47 |
| AIC | 13118.9 |
| BIC | 13645.1 |
| rho_squared | 0.708288 |
| n_significant_p<0.05 | 29 |
| pct_significant_p<0.05 | 60.4% |
| n_low_t<1.0 | 9 |
| pct_low_t<1.0 | 18.8% |
| n_degenerate_se | 0 |
| n_at_bound_strict | 2 |
| hessian_condition_number | 8.52246e+09 |
| n_negative_eigenvalues | 1 |
| p_chosen_min | 1.16237e-09 |
| p_chosen_q10 | 0.0161541 |
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
| f | 3.92777 | 0 | 2.80029 | beta_l_age=-0.0546416; beta_l_age2=0.00270149; beta_l_nkids=0.182795; beta_ll=2 | -0.653351 | NA |
| m | 3.92777 | 0 | 0.125438 | beta_l_age=-0.0085413; beta_l_age2=0.00173456; beta_ll=2 | -0.670577 | NA |
| sf | 0.534713 | 0 | 4.38279 | beta_l_age=0.00164869; beta_l_age2=0.00413917; beta_l_nkids=0.0633136; beta_ll=2 | -0.729829 | NA |
| sm | 0.591531 | 0 | 3.81389 | beta_l_age=0.00821039; beta_l_age2=0.00202866; beta_ll=2 | -0.71544 | NA |

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
| employment_hours | beta_E * working | beta_E | joint | -2.83851 |
| employment_hours | beta_h_pt1 * working_pt1 | beta_h_pt1 | joint | -0.50087 |
| employment_hours | beta_h_pt2 * working_pt2 | beta_h_pt2 | joint | 0.370668 |
| employment_hours | beta_h_ft * working_ft | beta_h_ft | joint | 1.45297 |
| employment_hours | beta_E_gsur * gsur * working | beta_E_gsur | joint | -0.743345 |
| employment_hours | beta_E_educH * educH * working | beta_E_educH | joint | 0.612937 |
| wage_mean | beta_w0 * intercept | beta_w0 | joint | 2.0302 |
| wage_mean | beta_w_educL * educL | beta_w_educL | joint | -0.0515513 |
| wage_mean | beta_w_educH * educH | beta_w_educH | joint | 0.31745 |
| wage_mean | beta_w_pexp * pexp_years | beta_w_pexp | joint | 0.0181215 |
| wage_mean | beta_w_pexp2 * pexp_years2 | beta_w_pexp2 | joint | -0.000218554 |
| wage_sigma | sigma | sigma | joint | 0.427852 |
| occupation:sm | beta_occ_2_sm * loc4_2 * working | beta_occ_2_sm | joint | -1.5101 |
| occupation:sm | beta_occ_3_sm * loc4_3 * working | beta_occ_3_sm | joint | -2.16495 |
| occupation:sm | beta_occ_4_sm * loc4_4 * working | beta_occ_4_sm | joint | 0.0239881 |
| occupation:sf | beta_occ_2_sf * loc4_2 * working | beta_occ_2_sf | joint | -0.0103955 |
| occupation:sf | beta_occ_3_sf * loc4_3 * working | beta_occ_3_sf | joint | -0.560591 |
| occupation:sf | beta_occ_4_sf * loc4_4 * working | beta_occ_4_sf | joint | 0.798669 |
| occupation:cm | beta_occ_2_cm * loc4_2 * working | beta_occ_2_cm | joint | -1.47884 |
| occupation:cm | beta_occ_3_cm * loc4_3 * working | beta_occ_3_cm | joint | -2.22473 |
| occupation:cm | beta_occ_4_cm * loc4_4 * working | beta_occ_4_cm | joint | 0.471425 |
| occupation:cf | beta_occ_2_cf * loc4_2 * working | beta_occ_2_cf | joint | 0.180023 |
| occupation:cf | beta_occ_3_cf * loc4_3 * working | beta_occ_3_cf | joint | -0.209648 |
| occupation:cf | beta_occ_4_cf * loc4_4 * working | beta_occ_4_cf | joint | 1.11838 |

## Per-Block Parameter Counts and Significance

| block | n_params | n_estimable | n_sig_p<0.001 | n_sig_p<0.01 | n_sig_p<0.05 | n_sig_p<0.10 |
| --- | --- | --- | --- | --- | --- | --- |
| preference | 24 | 24 | 8 | 8 | 9 | 9 |
| employment_hours_opportunity | 4 | 4 | 4 | 4 | 4 | 4 |
| market_residual_opportunity | 2 | 2 | 1 | 2 | 2 | 2 |
| wage_opportunity | 6 | 6 | 5 | 5 | 6 | 6 |
| occupation_opportunity | 12 | 12 | 8 | 8 | 8 | 10 |

## Convergence By Result Block

| group | success | message | iterations | n_function_evaluations | gradient_norm | log_likelihood | walltime_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| joint | 1 | SolveStatus.NormalCompletion (ModelStatus.OptimalLocal) | 24 | 24 | NA | -6511.47 | 98.2268 |

## Fit Statistics

| metric | value |
| --- | --- |
| log_likelihood | -6511.47 |
| ll_null_uniform | -19585.8 |
| ll_null_prior_corrected | -22321.6 |
| rho_squared | 0.708288 |
| rho_squared_adj | 0.706138 |
| rho_squared_uniform | 0.667541 |
| rho_squared_prior_corrected | 0.708288 |
| AIC | 13118.9 |
| BIC | 13645.1 |
| AIC_per_obs | 0.0308463 |
| n_observations | 425300 |
| n_groups | 4253 |
| n_parameters | 48 |
| n_obs_long | 425300 |

## Fit Moments

| group | participation_observed | participation_predicted | mean_hours_observed | mean_hours_predicted |
| --- | --- | --- | --- | --- |
| cou_f | 0.965076 | 0.988442 | 35.6466 | 38.8335 |
| cou_m | 0.971672 | 0.982479 | 41.6062 | 42.6471 |
| sf | 0.93956 | 0.952123 | 36.2971 | 35.1367 |
| sm | 0.929504 | 0.909307 | 39.3048 | 35.7747 |

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
| cou_f | hours_bins | 8 | 0.4944 | 0.2322 |
| cou_m | hours_bins | 8 | 0.3322 | 0.1652 |
| sf | hours_bins | 8 | 0.4132 | 0.2247 |
| sm | hours_bins | 8 | 0.7128 | 0.3813 |

## Observed vs Implied Log-Wage σ (chosen working alts)

| group | n | observed_mean_log_wage | observed_std_log_wage | implied_sigma |
| --- | --- | --- | --- | --- |
| singles_male | 712 | 2.6836 | 0.4502 | 0.427852 |
| singles_female | 855 | 2.6198 | 0.436 | 0.427852 |
| couples_male | 2504 | 2.7697 | 0.4402 | 0.427852 |
| couples_female | 2487 | 2.6221 | 0.436 | 0.427852 |

## Structural Elasticity Heuristics

These are curvature-based heuristics from the post-estimation script, not
policy-counterfactual elasticities.

| Group | Hicksian (compensated) | Marshallian (uncompensated) | Participation (extensive) | Intensive (conditional) | theta_l | theta_c | beta_l (at median X) | beta_c |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single Males | 1.715 | 1.615 | 0.515 | 1.201 | -0.715 | 0.000 | 3.814 | 0.592 |
| Single Females | 1.730 | 1.630 | 0.519 | 1.211 | -0.730 | 0.000 | 4.383 | 0.535 |
| Males in Couples | 1.671 | 1.571 | 0.501 | 1.169 | -0.671 | 0.000 | 0.125 | 3.928 |
| Females in Couples | 1.653 | 1.553 | 0.496 | 1.157 | -0.653 | 0.000 | 2.800 | 3.928 |

## Marginal Utility Diagnostics

| Group | beta_c | theta_c | MUC Positive? | MUC Diminishing? | Well-Behaved? | MUC at Median C | C where MUC=1 | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single Males | 0.591531 | 0 | yes | yes | yes | 0.591531 | 0.591531 | NA |
| Single Females | 0.534713 | 0 | yes | yes | yes | 0.534713 | 0.534713 | NA |
| Males in Couples | 3.92777 | 0 | yes | yes | yes | 3.92777 | 3.92777 | NA |
| Females in Couples | 3.92777 | 0 | yes | yes | yes | 3.92777 | 3.92777 | NA |

## Marginal Utility Distribution Summary

| group | N | n_neg_muc | pct_neg_muc | mean_muc | n_neg_mul | pct_neg_mul | mean_mul |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cou_f | 2577 | 0 | 0 | 0.00101243 | 0 | 0 | 0.00643392 |
| cou_m | 2577 | 0 | 0 | 0.00101243 | 0 | 0 | 0.000366102 |
| sf | 766 | 0 | 0 | 0.000300672 | 0 | 0 | 0.00959709 |
| sm | 910 | 0 | 0 | 0.000330106 | 0 | 0 | 0.00712506 |
| total | NA | 0 | 0 | NA | 0 | 0 | NA |

## Probability Diagnostics

| metric | value |
| --- | --- |
| prob_sum_max_error | 8.88178e-16 |
| prob_sum_mean_error | 1.37597e-16 |
| prob_sum_pct_off_by_0.01 | 0 |
| prob_sum_pct_off_by_0.001 | 0 |
| p_chosen_min | 1.16237e-09 |
| p_chosen_max | 0.999331 |
| p_chosen_mean | 0.389968 |
| p_chosen_median | 0.272457 |
| p_chosen_q10 | 0.0161541 |
| p_chosen_q25 | 0.0676135 |
| p_chosen_q75 | 0.726993 |
| p_chosen_q90 | 0.921927 |

## Worst-Fit Households

| rank | idhh | group | p_chosen | ll_i |
| --- | --- | --- | --- | --- |
| 1 | 4012700 | sm | 1.16237e-09 | -20.5728 |
| 2 | 3600001 | sf | 1.38374e-09 | -20.3985 |
| 3 | 4264600 | cou | 6.2948e-09 | -18.8835 |
| 4 | 1935801 | sm | 1.40949e-08 | -18.0775 |
| 5 | 3457500 | sm | 3.74931e-08 | -17.0991 |
| 6 | 1918802 | sf | 5.11956e-08 | -16.7876 |
| 7 | 1729600 | cou | 3.07205e-07 | -14.9958 |
| 8 | 3233100 | cou | 6.25363e-07 | -14.2849 |
| 9 | 2989700 | cou | 2.00131e-06 | -13.1217 |
| 10 | 3317202 | sf | 4.05801e-06 | -12.4148 |

## Identification Diagnostics

| metric | value |
| --- | --- |
| condition_number | 8.52246e+09 |
| min_eigenvalue | -18.8553 |
| max_eigenvalue | 1.35859e+10 |
| n_negative_eigenvalues | 1 |

_Interpretation: weakly conditioned (1e6 <= kappa < 1e10); 1 negative eigenvalue(s) - not at a local maximum or numerically singular._

## Initial → Final Movement (top 15 by |Δ|)

| block | parameter | initial_value | final_estimate | delta |
| --- | --- | --- | --- | --- |
| preference | joint.beta_l0_sf | 1 | 4.38279 | 3.38279 |
| preference | joint.beta_c | 1 | 3.92777 | 2.92777 |
| employment_hours_opportunity | joint.beta_E | 0 | -2.83851 | -2.83851 |
| preference | joint.beta_l0_sm | 1 | 3.81389 | 2.81389 |
| occupation_opportunity | joint.beta_occ_3_cm | 0 | -2.22473 | -2.22473 |
| occupation_opportunity | joint.beta_occ_3_sm | 0 | -2.16495 | -2.16495 |
| preference | joint.beta_ll | 0 | 2 | 2 |
| preference | joint.beta_l0_f | 1 | 2.80029 | 1.80029 |
| occupation_opportunity | joint.beta_occ_2_sm | 0 | -1.5101 | -1.5101 |
| occupation_opportunity | joint.beta_occ_2_cm | 0 | -1.47884 | -1.47884 |
| employment_hours_opportunity | joint.beta_h_ft | 0 | 1.45297 | 1.45297 |
| occupation_opportunity | joint.beta_occ_4_cf | 0 | 1.11838 | 1.11838 |
| preference | joint.theta_c | -1 | 0 | 1 |
| preference | joint.beta_l0_m | 1 | 0.125438 | -0.874562 |
| occupation_opportunity | joint.beta_occ_4_sf | 0 | 0.798669 | 0.798669 |

## Top High-Correlation Parameter Pairs

| param_i | param_j | correlation |
| --- | --- | --- |
| beta_c_sm | beta_c_sf | -1.06865 |
| beta_c_sf | theta_c_singles | -1.0545 |
| beta_c_sm | theta_c_singles | -1.04233 |
| beta_w_pexp | beta_w_pexp2 | -0.960191 |
| beta_E | beta_E_gsur | -0.949876 |
| theta_c_singles | beta_c | -0.904386 |

## Weakest Eigenvector Diagnostics

_None._

## Parameters At Bounds

| parameter | estimate | bound | side |
| --- | --- | --- | --- |
| joint.theta_c | 0 | 0 | upper |
| joint.beta_ll | 2 | 2 | upper |

## Parameters Near Bounds (within 5% of bound width)

| block | parameter | estimate | lower_bound | upper_bound | flags |
| --- | --- | --- | --- | --- | --- |
| preference | joint.beta_c_sm | 0.591531 | 0.05 | 50 | near_lower(delta=0.542) |
| preference | joint.beta_c_sf | 0.534713 | 0.05 | 50 | near_lower(delta=0.485) |
| preference | joint.beta_l0_m | 0.125438 | 0.05 | 50 | near_lower(delta=0.0754) |
| wage_opportunity | joint.sigma | 0.427852 | 0.1 | 20 | near_lower(delta=0.328) |

## Top Significant Coefficients (top 15 by |t|)

| block | parameter | estimate | std_error | t_value | p_value |
| --- | --- | --- | --- | --- | --- |
| wage_opportunity | joint.sigma | 0.427852 | 0.00406771 | 105.182 | 0 |
| wage_opportunity | joint.beta_w0 | 2.0302 | 0.0254411 | 79.8002 | 0 |
| preference | joint.beta_c | 3.92777 | 0.130057 | 30.2005 | 0 |
| employment_hours_opportunity | joint.beta_h_ft | 1.45297 | 0.0500549 | 29.0275 | 0 |
| wage_opportunity | joint.beta_w_educH | 0.31745 | 0.0150316 | 21.1189 | 0 |
| occupation_opportunity | joint.beta_occ_3_cm | -2.22473 | 0.14761 | -15.0717 | 0 |
| occupation_opportunity | joint.beta_occ_4_cf | 1.11838 | 0.0811949 | 13.774 | 0 |
| occupation_opportunity | joint.beta_occ_2_cm | -1.47884 | 0.113527 | -13.0263 | 0 |
| occupation_opportunity | joint.beta_occ_3_sm | -2.16495 | 0.18422 | -11.752 | 0 |
| occupation_opportunity | joint.beta_occ_2_sm | -1.5101 | 0.142039 | -10.6316 | 0 |
| employment_hours_opportunity | joint.beta_E | -2.83851 | 0.297999 | -9.52522 | 0 |
| occupation_opportunity | joint.beta_occ_4_sf | 0.798669 | 0.0920475 | 8.67671 | 0 |
| wage_opportunity | joint.beta_w_pexp | 0.0181215 | 0.00224057 | 8.08788 | 6.66134e-16 |
| occupation_opportunity | joint.beta_occ_4_cm | 0.471425 | 0.0685645 | 6.87564 | 6.17129e-12 |
| preference | joint.theta_l_f | -0.653351 | 0.102658 | -6.36435 | 1.96124e-10 |

## Parameter Estimates By Block

| block | parameter | estimate | std_error | t_value | p_value | lower_bound | upper_bound | initial_value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| employment_hours_opportunity | joint.beta_E | -2.83851 | 0.297999 | -9.52522 | 0 | -25 | 25 | 0 |
| employment_hours_opportunity | joint.beta_h_ft | 1.45297 | 0.0500549 | 29.0275 | 0 | -10 | 10 | 0 |
| employment_hours_opportunity | joint.beta_h_pt1 | -0.50087 | 0.107837 | -4.64469 | 3.40586e-06 | -10 | 10 | 0 |
| employment_hours_opportunity | joint.beta_h_pt2 | 0.370668 | 0.111114 | 3.33591 | 0.000850215 | -10 | 10 | 0 |
| market_residual_opportunity | joint.beta_E_educH | 0.612937 | 0.234986 | 2.6084 | 0.00909669 | -10 | 10 | 0 |
| market_residual_opportunity | joint.beta_E_gsur | -0.743345 | 0.219743 | -3.38279 | 0.000717538 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_cf | 0.180023 | 0.0999975 | 1.80028 | 0.071817 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_cm | -1.47884 | 0.113527 | -13.0263 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_sf | -0.0103955 | 0.112621 | -0.0923057 | 0.926455 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_sm | -1.5101 | 0.142039 | -10.6316 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_cf | -0.209648 | 0.111339 | -1.88297 | 0.0597048 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_cm | -2.22473 | 0.14761 | -15.0717 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_sf | -0.560591 | 0.128959 | -4.34704 | 1.37988e-05 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_sm | -2.16495 | 0.18422 | -11.752 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_cf | 1.11838 | 0.0811949 | 13.774 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_cm | 0.471425 | 0.0685645 | 6.87564 | 6.17129e-12 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_sf | 0.798669 | 0.0920475 | 8.67671 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_sm | 0.0239881 | 0.0860229 | 0.278857 | 0.780355 | -10 | 10 | 0 |
| preference | joint.beta_c | 3.92777 | 0.130057 | 30.2005 | 0 | 0.05 | 50 | 1 |
| preference | joint.beta_c_sf | 0.534713 | NA | NA | NA | 0.05 | 50 | 1 |
| preference | joint.beta_c_sm | 0.591531 | NA | NA | NA | 0.05 | 50 | 1 |
| preference | joint.beta_l0_f | 2.80029 | 0.741014 | 3.77899 | 0.000157464 | 0.05 | 50 | 1 |
| preference | joint.beta_l0_m | 0.125438 | 0.398873 | 0.314482 | 0.753155 | 0.05 | 50 | 1 |
| preference | joint.beta_l0_sf | 4.38279 | 0.772554 | 5.67312 | 1.40222e-08 | 0.05 | 50 | 1 |
| preference | joint.beta_l0_sm | 3.81389 | 0.71372 | 5.34368 | 9.10785e-08 | 0.05 | 50 | 1 |
| preference | joint.beta_l_age2_f | 0.00270149 | 0.00213485 | 1.26542 | 0.20572 | -1 | 1 | 0 |
| preference | joint.beta_l_age2_m | 0.00173456 | 0.00139455 | 1.24381 | 0.213569 | -1 | 1 | 0 |
| preference | joint.beta_l_age2_sf | 0.00413917 | 0.00256438 | 1.6141 | 0.106506 | -1 | 1 | 0 |
| preference | joint.beta_l_age2_sm | 0.00202866 | 0.00208511 | 0.972928 | 0.330589 | -1 | 1 | 0 |
| preference | joint.beta_l_age_f | -0.0546416 | 0.0216933 | -2.51883 | 0.0117746 | -5 | 5 | 0 |
| preference | joint.beta_l_age_m | -0.0085413 | 0.0141428 | -0.603933 | 0.545888 | -5 | 5 | 0 |
| preference | joint.beta_l_age_sf | 0.00164869 | 0.0271942 | 0.0606267 | 0.951656 | -5 | 5 | 0 |
| preference | joint.beta_l_age_sm | 0.00821039 | 0.0248426 | 0.330497 | 0.741025 | -5 | 5 | 0 |
| preference | joint.beta_l_nkids_f | 0.182795 | 0.208354 | 0.877328 | 0.380309 | -5 | 5 | 0 |
| preference | joint.beta_l_nkids_sf | 0.0633136 | 0.35785 | 0.176928 | 0.859565 | -5 | 5 | 0 |
| preference | joint.beta_ll | 2 | NA | NA | NA | -2 | 2 | 0 |
| preference | joint.theta_c | 0 | NA | NA | NA | -8 | 0 | -1 |
| preference | joint.theta_c_singles | -0.970811 | NA | NA | NA | -8 | 0.95 | -1 |
| preference | joint.theta_l_f | -0.653351 | 0.102658 | -6.36435 | 1.96124e-10 | -8 | 0.95 | -1 |
| preference | joint.theta_l_m | -0.670577 | 0.15532 | -4.31739 | 1.57889e-05 | -8 | 0.95 | -1 |
| preference | joint.theta_l_sf | -0.729829 | 0.135019 | -5.40538 | 6.46709e-08 | -8 | 0.95 | -1 |
| preference | joint.theta_l_sm | -0.71544 | 0.155577 | -4.59862 | 4.25303e-06 | -8 | 0.95 | -1 |
| wage_opportunity | joint.beta_w0 | 2.0302 | 0.0254411 | 79.8002 | 0 | -10 | 20 | 2 |
| wage_opportunity | joint.beta_w_educH | 0.31745 | 0.0150316 | 21.1189 | 0 | -5 | 5 | 0.2 |
| wage_opportunity | joint.beta_w_educL | -0.0515513 | 0.0212084 | -2.43071 | 0.0150695 | -5 | 5 | -0.1 |
| wage_opportunity | joint.beta_w_pexp | 0.0181215 | 0.00224057 | 8.08788 | 6.66134e-16 | -1 | 1 | 0.02 |
| wage_opportunity | joint.beta_w_pexp2 | -0.000218554 | 4.96433e-05 | -4.40248 | 1.0702e-05 | -0.1 | 0.1 | -0.0003 |
| wage_opportunity | joint.sigma | 0.427852 | 0.00406771 | 105.182 | 0 | 0.1 | 20 | 0.5 |

## Hours Distribution Shares

| group | hours_bin | observed_share | predicted_share |
| --- | --- | --- | --- |
| cou_f | 0 | 0.0349243 | 0 |
| cou_f | 1-10 | 0.0256112 | 0.00582072 |
| cou_f | 11-20 | 0.0923555 | 0.0500582 |
| cou_f | 21-30 | 0.38766 | 0.241754 |
| cou_f | 31-40 | 0.381451 | 0.517656 |
| cou_f | 41-50 | 0.0523865 | 0.155219 |
| cou_f | 51-60 | 0.0201785 | 0.0283275 |
| cou_f | 60+ | 0.00543267 | 0.00116414 |
| cou_m | 0 | 0.0283275 | 0.000776096 |
| cou_m | 1-10 | 0.00388048 | 0.00271634 |
| cou_m | 11-20 | 0.0209546 | 0.0190144 |
| cou_m | 21-30 | 0.256888 | 0.138533 |
| cou_m | 31-40 | 0.470702 | 0.529686 |
| cou_m | 41-50 | 0.135429 | 0.227784 |
| cou_m | 51-60 | 0.0589833 | 0.0737291 |
| cou_m | 60+ | 0.0248351 | 0.00776096 |
| sf | 0 | 0.0604396 | 0 |
| sf | 1-10 | 0.0307692 | 0.0010989 |
| sf | 11-20 | 0.0835165 | 0.0527473 |
| sf | 21-30 | 0.347253 | 0.550549 |
| sf | 31-40 | 0.385714 | 0.389011 |
| sf | 41-50 | 0.0626374 | 0.00659341 |
| sf | 51-60 | 0.021978 | 0 |
| sf | 60+ | 0.00769231 | 0 |
| sm | 0 | 0.0704961 | 0 |
| sm | 1-10 | 0.0104439 | 0.00261097 |
| sm | 11-20 | 0.0483029 | 0.073107 |
| sm | 21-30 | 0.25718 | 0.588773 |
| sm | 31-40 | 0.480418 | 0.330287 |
| sm | 41-50 | 0.0770235 | 0.00522193 |
| sm | 51-60 | 0.0443864 | 0 |
| sm | 60+ | 0.0117493 | 0 |

## Wage Distribution Summary

Observed values use chosen working alternatives. Predicted values use
choice-probability weights over working alternatives.

| group | n_observed_working | predicted_worker_weight | obs_mean | pred_mean | obs_q10 | obs_q50 | obs_q90 | pred_q10 | pred_q50 | pred_q90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | 712 | 721.135 | 16.2131 | 12.689 | 9.15372 | 14.2557 | 25.4434 | 6.219 | 11.5609 | 20.2671 |
| singles_female | 855 | 857.562 | 15.1069 | 12.8286 | 8.65411 | 13.8516 | 22.9432 | 6.37174 | 11.7883 | 20.4001 |
| couples_male | 2504 | 2531.85 | 17.656 | 17.1128 | 10.0631 | 15.2895 | 27.8735 | 9.01167 | 14.978 | 27.7463 |
| couples_female | 2487 | 2547.21 | 15.1712 | 15.9357 | 8.86239 | 13.8393 | 22.4802 | 8.52965 | 13.9324 | 25.8875 |

## Occupation Distribution Shares

Observed shares use chosen working alternatives. Predicted shares use
choice-probability weights over working alternatives. Category labels
are reported for loc4-style variables when available.

| group | occupation_column | category | label | observed_share | predicted_share | observed_count | predicted_weight |
| --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | loc4 | -2 | unknown_observed_working | 0.00561798 | 0.000340946 | 4 | 0.245868 |
| singles_male | loc4 | 1 | routine_manual_ref | 0.407303 | 0.282708 | 290 | 203.871 |
| singles_male | loc4 | 2 | nonroutine_manual | 0.0941011 | 0.234272 | 67 | 168.942 |
| singles_male | loc4 | 3 | routine_cognitive | 0.0505618 | 0.208788 | 36 | 150.564 |
| singles_male | loc4 | 4 | nonroutine_cognitive | 0.442416 | 0.273892 | 315 | 197.513 |
| singles_female | loc4 | -2 | unknown_observed_working | 0.00350877 | 0.000853594 | 3 | 0.73201 |
| singles_female | loc4 | 1 | routine_manual_ref | 0.191813 | 0.258363 | 164 | 221.562 |
| singles_female | loc4 | 2 | nonroutine_manual | 0.20117 | 0.239794 | 172 | 205.638 |
| singles_female | loc4 | 3 | routine_cognitive | 0.130994 | 0.227895 | 112 | 195.434 |
| singles_female | loc4 | 4 | nonroutine_cognitive | 0.472515 | 0.273095 | 404 | 234.196 |
| couples_male | loc4_male | -2 | unknown_observed_working | 0.0123802 | 0.00732673 | 31 | 18.5502 |
| couples_male | loc4_male | 1 | routine_manual_ref | 0.360224 | 0.35537 | 902 | 899.742 |
| couples_male | loc4_male | 2 | nonroutine_manual | 0.0802716 | 0.0840379 | 201 | 212.771 |
| couples_male | loc4_male | 3 | routine_cognitive | 0.0391374 | 0.0396173 | 98 | 100.305 |
| couples_male | loc4_male | 4 | nonroutine_cognitive | 0.507987 | 0.513649 | 1272 | 1300.48 |
| couples_female | loc4_female | -2 | unknown_observed_working | 0.00120627 | 0.000536688 | 3 | 1.36706 |
| couples_female | loc4_female | 1 | routine_manual_ref | 0.170084 | 0.16856 | 423 | 429.358 |
| couples_female | loc4_female | 2 | nonroutine_manual | 0.206273 | 0.204337 | 513 | 520.49 |
| couples_female | loc4_female | 3 | routine_cognitive | 0.152392 | 0.14811 | 379 | 377.268 |
| couples_female | loc4_female | 4 | nonroutine_cognitive | 0.470044 | 0.478457 | 1169 | 1218.73 |

## Notes For Use

- This Markdown file is the preferred low-token artifact for LLM review.
- Use the HTML report only when plots or visual diagnostics are needed.
- Generated output folders remain local unless explicitly added to Git.
