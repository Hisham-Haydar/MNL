# RURO Low-Token Post-Estimation Summary

Generated: 2026-05-15T10:31:33

## Purpose

Compact text-only report for Git, paper drafting, and LLM review.
Figures and large HTML output are intentionally omitted.

## Sources

| item | path_or_value |
| --- | --- |
| estimation_results_json | U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0c_b2\run_2026-05-15_10-05-45\estimation_results.json |
| html_report | U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0c_b2\run_2026-05-15_10-05-45\estimation_spec_ruro_occ_M0c_b2\post_estimation_report_20260515_103129.html |
| post_output_dir | U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0c_b2\run_2026-05-15_10-05-45\estimation_spec_ruro_occ_M0c_b2 |
| params_csv | U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0c_b2\run_2026-05-15_10-05-45\estimation_spec_ruro_occ_M0c_b2\params.csv |
| elasticities_csv | U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0c_b2\run_2026-05-15_10-05-45\estimation_spec_ruro_occ_M0c_b2\elasticities.csv |
| mnl_base | Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl |
| spec_config | U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\estimation_spec_ruro_occ_M0c_b2.yaml |

## Run Metadata

| field | value |
| --- | --- |
| specification | ruro_occ_M0c_b2 |
| model_family | regular |
| market_opportunity_tier | NA |
| prior_correction_applied | 1 |
| prior_correction_form | -log(prior) |
| market_centering_applied | 1 |
| wage_spec | vw |
| estimation_walltime_seconds | 256.424 |

## Source Environment

| field | value |
| --- | --- |
| git_sha | c2a304c09270 |
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
| identification | ill-conditioned (kappa >= 1e10); 1 negative eigenvalue(s) - not at a local maximum or numerically singular |
| probability | minimum chosen probability is very small (1.005e-09) |
| hessian | negative eigenvalues present; inspect SE and local optimum diagnostics |

## Convergence Health Summary

| metric | value |
| --- | --- |
| n_estimated_params | 47 |
| log_likelihood | -6509.16 |
| AIC | 13112.3 |
| BIC | 13627.5 |
| rho_squared | 0.708392 |
| n_significant_p<0.05 | 30 |
| pct_significant_p<0.05 | 63.8% |
| n_low_t<1.0 | 10 |
| pct_low_t<1.0 | 21.3% |
| n_degenerate_se | 0 |
| n_at_bound_strict | 0 |
| hessian_condition_number | 5.05957e+10 |
| n_negative_eigenvalues | 1 |
| p_chosen_min | 1.00525e-09 |
| p_chosen_q10 | 0.0157001 |
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
| f | 4.05155 | NA | 2.58212 | beta_l_age=-0.057413; beta_l_age2=0.00279208; beta_l_nkids=0.176922; beta_ll=2.6237 | -0.677672 | NA |
| m | 4.05155 | NA | 0.0118786 | beta_l_age=-0.00787789; beta_l_age2=0.000617809; beta_ll=2.6237 | -0.731903 | NA |
| sf | 0.576015 | NA | 4.45884 | beta_l_age=0.00190756; beta_l_age2=0.00413348; beta_l_nkids=0.0566776; beta_ll=2.6237 | -0.728033 | NA |
| sm | 0.635814 | NA | 3.87402 | beta_l_age=0.00849058; beta_l_age2=0.0020284; beta_ll=2.6237 | -0.711949 | NA |

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
| employment_hours | beta_E * working | beta_E | joint | -2.84228 |
| employment_hours | beta_h_pt1 * working_pt1 | beta_h_pt1 | joint | -0.498736 |
| employment_hours | beta_h_pt2 * working_pt2 | beta_h_pt2 | joint | 0.365049 |
| employment_hours | beta_h_ft * working_ft | beta_h_ft | joint | 1.44406 |
| employment_hours | beta_E_gsur * gsur * working | beta_E_gsur | joint | -0.74378 |
| employment_hours | beta_E_educH * educH * working | beta_E_educH | joint | 0.613364 |
| wage_mean | beta_w0 * intercept | beta_w0 | joint | 2.02486 |
| wage_mean | beta_w_educL * educL | beta_w_educL | joint | -0.0510015 |
| wage_mean | beta_w_educH * educH | beta_w_educH | joint | 0.316109 |
| wage_mean | beta_w_pexp * pexp_years | beta_w_pexp | joint | 0.0180955 |
| wage_mean | beta_w_pexp2 * pexp_years2 | beta_w_pexp2 | joint | -0.000218625 |
| wage_sigma | sigma | sigma | joint | 0.426761 |
| occupation:sm | beta_occ_2_sm * loc4_2 * working | beta_occ_2_sm | joint | -1.5104 |
| occupation:sm | beta_occ_3_sm * loc4_3 * working | beta_occ_3_sm | joint | -2.16511 |
| occupation:sm | beta_occ_4_sm * loc4_4 * working | beta_occ_4_sm | joint | 0.0236535 |
| occupation:sf | beta_occ_2_sf * loc4_2 * working | beta_occ_2_sf | joint | -0.0104636 |
| occupation:sf | beta_occ_3_sf * loc4_3 * working | beta_occ_3_sf | joint | -0.560951 |
| occupation:sf | beta_occ_4_sf * loc4_4 * working | beta_occ_4_sf | joint | 0.798815 |
| occupation:cm | beta_occ_2_cm * loc4_2 * working | beta_occ_2_cm | joint | -1.47596 |
| occupation:cm | beta_occ_3_cm * loc4_3 * working | beta_occ_3_cm | joint | -2.22395 |
| occupation:cm | beta_occ_4_cm * loc4_4 * working | beta_occ_4_cm | joint | 0.472509 |
| occupation:cf | beta_occ_2_cf * loc4_2 * working | beta_occ_2_cf | joint | 0.176257 |
| occupation:cf | beta_occ_3_cf * loc4_3 * working | beta_occ_3_cf | joint | -0.216395 |
| occupation:cf | beta_occ_4_cf * loc4_4 * working | beta_occ_4_cf | joint | 1.11471 |

## Per-Block Parameter Counts and Significance

| block | n_params | n_estimable | n_sig_p<0.001 | n_sig_p<0.01 | n_sig_p<0.05 | n_sig_p<0.10 |
| --- | --- | --- | --- | --- | --- | --- |
| preference | 23 | 23 | 9 | 10 | 10 | 10 |
| employment_hours_opportunity | 4 | 4 | 3 | 4 | 4 | 4 |
| market_residual_opportunity | 2 | 2 | 1 | 2 | 2 | 2 |
| wage_opportunity | 6 | 6 | 5 | 5 | 6 | 6 |
| occupation_opportunity | 12 | 12 | 8 | 8 | 8 | 10 |

## Convergence By Result Block

| group | success | message | iterations | n_function_evaluations | gradient_norm | log_likelihood | walltime_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| joint | 1 | SolveStatus.NormalCompletion (ModelStatus.OptimalLocal) | 20 | 20 | NA | -6509.16 | 85.4748 |

## Fit Statistics

| metric | value |
| --- | --- |
| log_likelihood | -6509.16 |
| ll_null_uniform | -19585.8 |
| ll_null_prior_corrected | -22321.6 |
| rho_squared | 0.708392 |
| rho_squared_adj | 0.706286 |
| rho_squared_uniform | 0.667659 |
| rho_squared_prior_corrected | 0.708392 |
| AIC | 13112.3 |
| BIC | 13627.5 |
| AIC_per_obs | 0.0308308 |
| n_observations | 425300 |
| n_groups | 4253 |
| n_parameters | 47 |
| n_obs_long | 425300 |

## Fit Moments

| group | participation_observed | participation_predicted | mean_hours_observed | mean_hours_predicted |
| --- | --- | --- | --- | --- |
| cou_f | 0.965076 | 0.988681 | 35.6466 | 38.9718 |
| cou_m | 0.971672 | 0.982967 | 41.6062 | 42.78 |
| sf | 0.93956 | 0.951641 | 36.2971 | 35.0828 |
| sm | 0.929504 | 0.908351 | 39.3048 | 35.7174 |

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
| cou_f | hours_bins | 8 | 0.5014 | 0.2343 |
| cou_m | hours_bins | 8 | 0.3423 | 0.1696 |
| sf | hours_bins | 8 | 0.4044 | 0.2231 |
| sm | hours_bins | 8 | 0.7258 | 0.3896 |

## Observed vs Implied Log-Wage σ (chosen working alts)

| group | n | observed_mean_log_wage | observed_std_log_wage | implied_sigma |
| --- | --- | --- | --- | --- |
| singles_male | 712 | 2.6836 | 0.4502 | 0.426761 |
| singles_female | 855 | 2.6198 | 0.436 | 0.426761 |
| couples_male | 2504 | 2.7697 | 0.4402 | 0.426761 |
| couples_female | 2487 | 2.6221 | 0.436 | 0.426761 |

## Structural Elasticity Heuristics

These are curvature-based heuristics from the post-estimation script, not
policy-counterfactual elasticities.

| Group | Hicksian (compensated) | Marshallian (uncompensated) | Participation (extensive) | Intensive (conditional) | theta_l | theta_c | beta_l (at median X) | beta_c |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single Males | 1.712 | 1.612 | 0.514 | 1.198 | -0.712 | 0.500 | 3.874 | 0.636 |
| Single Females | 1.728 | 1.628 | 0.518 | 1.210 | -0.728 | 0.500 | 4.459 | 0.576 |
| Males in Couples | 1.732 | 1.632 | 0.520 | 1.212 | -0.732 | 0.500 | 0.012 | 4.052 |
| Females in Couples | 1.678 | 1.578 | 0.503 | 1.174 | -0.678 | 0.500 | 2.582 | 4.052 |

## Marginal Utility Diagnostics

| Group | beta_c | theta_c | MUC Positive? | MUC Diminishing? | Well-Behaved? | MUC at Median C | C where MUC=1 | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single Males | 0.635814 | 0.5 | yes | yes | yes | 0.635814 | 0.404259 | NA |
| Single Females | 0.576015 | 0.5 | yes | yes | yes | 0.576015 | 0.331793 | NA |
| Males in Couples | 4.05155 | 0 | yes | yes | yes | 4.05155 | 4.05155 | NA |
| Females in Couples | 4.05155 | 0 | yes | yes | yes | 4.05155 | 4.05155 | NA |

## Marginal Utility Distribution Summary

| group | N | n_neg_muc | pct_neg_muc | mean_muc | n_neg_mul | pct_neg_mul | mean_mul |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cou_f | 2577 | 0 | 0 | 0.0639744 | 0 | 0 | 0.00545188 |
| cou_m | 2577 | 0 | 0 | 0.0639744 | 0 | 0 | 2.83237e-05 |
| sf | 766 | 0 | 0 | 0.0133526 | 0 | 0 | 0.00980199 |
| sm | 910 | 0 | 0 | 0.014728 | 0 | 0 | 0.00732206 |
| total | NA | 0 | 0 | NA | 0 | 0 | NA |

## Probability Diagnostics

| metric | value |
| --- | --- |
| prob_sum_max_error | 7.77156e-16 |
| prob_sum_mean_error | 1.31332e-16 |
| prob_sum_pct_off_by_0.01 | 0 |
| prob_sum_pct_off_by_0.001 | 0 |
| p_chosen_min | 1.00525e-09 |
| p_chosen_max | 0.999325 |
| p_chosen_mean | 0.388501 |
| p_chosen_median | 0.269595 |
| p_chosen_q10 | 0.0157001 |
| p_chosen_q25 | 0.0670941 |
| p_chosen_q75 | 0.722936 |
| p_chosen_q90 | 0.920116 |

## Worst-Fit Households

| rank | idhh | group | p_chosen | ll_i |
| --- | --- | --- | --- | --- |
| 1 | 4012700 | sm | 1.00525e-09 | -20.718 |
| 2 | 3600001 | sf | 1.19838e-09 | -20.5423 |
| 3 | 4264600 | cou | 5.2677e-09 | -19.0617 |
| 4 | 1935801 | sm | 1.23888e-08 | -18.2065 |
| 5 | 3457500 | sm | 3.29169e-08 | -17.2293 |
| 6 | 1918802 | sf | 4.5581e-08 | -16.9038 |
| 7 | 1729600 | cou | 2.80869e-07 | -15.0854 |
| 8 | 3233100 | cou | 5.49571e-07 | -14.4141 |
| 9 | 2989700 | cou | 1.91052e-06 | -13.1681 |
| 10 | 3317202 | sf | 3.54995e-06 | -12.5486 |

## Identification Diagnostics

| metric | value |
| --- | --- |
| condition_number | 5.05957e+10 |
| min_eigenvalue | -13.8871 |
| max_eigenvalue | 1.36737e+10 |
| n_negative_eigenvalues | 1 |

_Interpretation: ill-conditioned (kappa >= 1e10); 1 negative eigenvalue(s) - not at a local maximum or numerically singular._

## Initial → Final Movement (top 15 by |Δ|)

| block | parameter | initial_value | final_estimate | delta |
| --- | --- | --- | --- | --- |
| preference | joint.beta_l0_sf | 1 | 4.45884 | 3.45884 |
| preference | joint.beta_c | 1 | 4.05155 | 3.05155 |
| preference | joint.beta_l0_sm | 1 | 3.87402 | 2.87402 |
| employment_hours_opportunity | joint.beta_E | 0 | -2.84228 | -2.84228 |
| occupation_opportunity | joint.beta_occ_3_cm | 0 | -2.22395 | -2.22395 |
| occupation_opportunity | joint.beta_occ_3_sm | 0 | -2.16511 | -2.16511 |
| preference | joint.beta_l0_f | 1 | 2.58212 | 1.58212 |
| occupation_opportunity | joint.beta_occ_2_sm | 0 | -1.5104 | -1.5104 |
| occupation_opportunity | joint.beta_occ_2_cm | 0 | -1.47596 | -1.47596 |
| employment_hours_opportunity | joint.beta_h_ft | 0 | 1.44406 | 1.44406 |
| occupation_opportunity | joint.beta_occ_4_cf | 0 | 1.11471 | 1.11471 |
| occupation_opportunity | joint.beta_occ_4_sf | 0 | 0.798815 | 0.798815 |
| market_residual_opportunity | joint.beta_E_gsur | 0 | -0.74378 | -0.74378 |
| preference | joint.beta_ll | 2 | 2.6237 | 0.623695 |
| market_residual_opportunity | joint.beta_E_educH | 0 | 0.613364 | 0.613364 |

## Top High-Correlation Parameter Pairs

| param_i | param_j | correlation |
| --- | --- | --- |
| theta_c_singles | beta_c | -1.08376 |
| beta_c_sm | beta_c_sf | -1.05424 |
| beta_c_sf | theta_c_singles | -1.04367 |
| beta_c_sm | theta_c_singles | -1.0341 |
| beta_w_pexp | beta_w_pexp2 | -0.960304 |
| beta_E | beta_E_gsur | -0.950204 |
| beta_c_sm | beta_c | -0.949731 |
| beta_c_sf | beta_c | -0.928876 |

## Weakest Eigenvector Diagnostics

_None._

## Parameters At Bounds

_None._

## Parameters Near Bounds (within 5% of bound width)

| block | parameter | estimate | lower_bound | upper_bound | flags |
| --- | --- | --- | --- | --- | --- |
| preference | joint.beta_c_sm | 0.635814 | 0.05 | 50 | near_lower(delta=0.586) |
| preference | joint.beta_c_sf | 0.576015 | 0.05 | 50 | near_lower(delta=0.526) |
| preference | joint.beta_l0_m | 0.0118786 | 1e-06 | 50 | near_lower(delta=0.0119) |
| wage_opportunity | joint.sigma | 0.426761 | 0.1 | 20 | near_lower(delta=0.327) |

## Top Significant Coefficients (top 15 by |t|)

| block | parameter | estimate | std_error | t_value | p_value |
| --- | --- | --- | --- | --- | --- |
| wage_opportunity | joint.sigma | 0.426761 | 0.00395749 | 107.836 | 0 |
| wage_opportunity | joint.beta_w0 | 2.02486 | 0.0252355 | 80.2387 | 0 |
| preference | joint.beta_c | 4.05155 | 0.120458 | 33.6347 | 0 |
| employment_hours_opportunity | joint.beta_h_ft | 1.44406 | 0.0500587 | 28.8473 | 0 |
| wage_opportunity | joint.beta_w_educH | 0.316109 | 0.0149503 | 21.144 | 0 |
| occupation_opportunity | joint.beta_occ_3_cm | -2.22395 | 0.147951 | -15.0317 | 0 |
| occupation_opportunity | joint.beta_occ_4_cf | 1.11471 | 0.0814026 | 13.6938 | 0 |
| occupation_opportunity | joint.beta_occ_2_cm | -1.47596 | 0.113766 | -12.9736 | 0 |
| occupation_opportunity | joint.beta_occ_3_sm | -2.16511 | 0.184235 | -11.7518 | 0 |
| occupation_opportunity | joint.beta_occ_2_sm | -1.5104 | 0.142052 | -10.6327 | 0 |
| employment_hours_opportunity | joint.beta_E | -2.84228 | 0.299093 | -9.50301 | 0 |
| occupation_opportunity | joint.beta_occ_4_sf | 0.798815 | 0.0920474 | 8.67831 | 0 |
| wage_opportunity | joint.beta_w_pexp | 0.0180955 | 0.00223149 | 8.10917 | 4.44089e-16 |
| preference | joint.beta_ll | 2.6237 | 0.346006 | 7.5828 | 3.37508e-14 |
| preference | joint.theta_l_f | -0.677672 | 0.0896975 | -7.55508 | 4.19664e-14 |

## Parameter Estimates By Block

| block | parameter | estimate | std_error | t_value | p_value | lower_bound | upper_bound | initial_value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| employment_hours_opportunity | joint.beta_E | -2.84228 | 0.299093 | -9.50301 | 0 | -25 | 25 | 0 |
| employment_hours_opportunity | joint.beta_h_ft | 1.44406 | 0.0500587 | 28.8473 | 0 | -10 | 10 | 0 |
| employment_hours_opportunity | joint.beta_h_pt1 | -0.498736 | 0.107946 | -4.62024 | 3.83296e-06 | -10 | 10 | 0 |
| employment_hours_opportunity | joint.beta_h_pt2 | 0.365049 | 0.111314 | 3.27944 | 0.00104013 | -10 | 10 | 0 |
| market_residual_opportunity | joint.beta_E_educH | 0.613364 | 0.236147 | 2.59738 | 0.00939382 | -10 | 10 | 0 |
| market_residual_opportunity | joint.beta_E_gsur | -0.74378 | 0.220674 | -3.3705 | 0.00075033 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_cf | 0.176257 | 0.100276 | 1.75771 | 0.0787975 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_cm | -1.47596 | 0.113766 | -12.9736 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_sf | -0.0104636 | 0.112635 | -0.0928983 | 0.925984 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_sm | -1.5104 | 0.142052 | -10.6327 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_cf | -0.216395 | 0.111651 | -1.93814 | 0.0526067 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_cm | -2.22395 | 0.147951 | -15.0317 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_sf | -0.560951 | 0.128973 | -4.34938 | 1.36523e-05 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_sm | -2.16511 | 0.184235 | -11.7518 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_cf | 1.11471 | 0.0814026 | 13.6938 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_cm | 0.472509 | 0.0687809 | 6.86977 | 6.43063e-12 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_sf | 0.798815 | 0.0920474 | 8.67831 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_sm | 0.0236535 | 0.0860265 | 0.274956 | 0.78335 | -10 | 10 | 0 |
| preference | joint.beta_c | 4.05155 | 0.120458 | 33.6347 | 0 | 0.05 | 50 | 1 |
| preference | joint.beta_c_sf | 0.576015 | NA | NA | NA | 0.05 | 50 | 1 |
| preference | joint.beta_c_sm | 0.635814 | NA | NA | NA | 0.05 | 50 | 1 |
| preference | joint.beta_l0_f | 2.58212 | 0.431157 | 5.98882 | 2.11366e-09 | 0.05 | 50 | 1 |
| preference | joint.beta_l0_m | 0.0118786 | 0.28595 | 0.041541 | 0.966865 | 1e-06 | 50 | 0.01 |
| preference | joint.beta_l0_sf | 4.45884 | 0.780706 | 5.71129 | 1.12123e-08 | 0.05 | 50 | 1 |
| preference | joint.beta_l0_sm | 3.87402 | 0.720788 | 5.3747 | 7.67092e-08 | 0.05 | 50 | 1 |
| preference | joint.beta_l_age2_f | 0.00279208 | 0.00219795 | 1.27031 | 0.203975 | -1 | 1 | 0 |
| preference | joint.beta_l_age2_m | 0.000617809 | 0.00146258 | 0.422411 | 0.672725 | -1 | 1 | 0 |
| preference | joint.beta_l_age2_sf | 0.00413348 | 0.00256801 | 1.6096 | 0.107484 | -1 | 1 | 0 |
| preference | joint.beta_l_age2_sm | 0.0020284 | 0.00208351 | 0.973548 | 0.330281 | -1 | 1 | 0 |
| preference | joint.beta_l_age_f | -0.057413 | 0.0221319 | -2.59413 | 0.00948306 | -5 | 5 | 0 |
| preference | joint.beta_l_age_m | -0.00787789 | 0.0150426 | -0.523707 | 0.600483 | -5 | 5 | 0 |
| preference | joint.beta_l_age_sf | 0.00190756 | 0.0272253 | 0.0700656 | 0.944141 | -5 | 5 | 0 |
| preference | joint.beta_l_age_sm | 0.00849058 | 0.0248209 | 0.342073 | 0.732296 | -5 | 5 | 0 |
| preference | joint.beta_l_nkids_f | 0.176922 | 0.213729 | 0.827787 | 0.407791 | -5 | 5 | 0 |
| preference | joint.beta_l_nkids_sf | 0.0566776 | 0.357938 | 0.158345 | 0.874185 | -5 | 5 | 0 |
| preference | joint.beta_ll | 2.6237 | 0.346006 | 7.5828 | 3.37508e-14 | 0 | 10 | 2 |
| preference | joint.theta_c_singles | -0.935749 | NA | NA | NA | -8 | 0.95 | -1 |
| preference | joint.theta_l_f | -0.677672 | 0.0896975 | -7.55508 | 4.19664e-14 | -8 | 0.95 | -1 |
| preference | joint.theta_l_m | -0.731903 | 0.136983 | -5.34304 | 9.14027e-08 | -8 | 0.95 | -1 |
| preference | joint.theta_l_sf | -0.728033 | 0.13439 | -5.41732 | 6.04991e-08 | -8 | 0.95 | -1 |
| preference | joint.theta_l_sm | -0.711949 | 0.154649 | -4.60364 | 4.15167e-06 | -8 | 0.95 | -1 |
| wage_opportunity | joint.beta_w0 | 2.02486 | 0.0252355 | 80.2387 | 0 | -10 | 20 | 2 |
| wage_opportunity | joint.beta_w_educH | 0.316109 | 0.0149503 | 21.144 | 0 | -5 | 5 | 0.2 |
| wage_opportunity | joint.beta_w_educL | -0.0510015 | 0.0211242 | -2.41437 | 0.0157626 | -5 | 5 | -0.1 |
| wage_opportunity | joint.beta_w_pexp | 0.0180955 | 0.00223149 | 8.10917 | 4.44089e-16 | -1 | 1 | 0.02 |
| wage_opportunity | joint.beta_w_pexp2 | -0.000218625 | 4.94555e-05 | -4.42063 | 9.84143e-06 | -0.1 | 0.1 | -0.0003 |
| wage_opportunity | joint.sigma | 0.426761 | 0.00395749 | 107.836 | 0 | 0.1 | 20 | 0.5 |

## Hours Distribution Shares

| group | hours_bin | observed_share | predicted_share |
| --- | --- | --- | --- |
| cou_f | 0 | 0.0349243 | 0 |
| cou_f | 1-10 | 0.0256112 | 0.00543267 |
| cou_f | 11-20 | 0.0923555 | 0.0488941 |
| cou_f | 21-30 | 0.38766 | 0.239814 |
| cou_f | 31-40 | 0.381451 | 0.514164 |
| cou_f | 41-50 | 0.0523865 | 0.16104 |
| cou_f | 51-60 | 0.0201785 | 0.0294917 |
| cou_f | 60+ | 0.00543267 | 0.00116414 |
| cou_m | 0 | 0.0283275 | 0.000776096 |
| cou_m | 1-10 | 0.00388048 | 0.00232829 |
| cou_m | 11-20 | 0.0209546 | 0.0182383 |
| cou_m | 21-30 | 0.256888 | 0.134265 |
| cou_m | 31-40 | 0.470702 | 0.530462 |
| cou_m | 41-50 | 0.135429 | 0.229336 |
| cou_m | 51-60 | 0.0589833 | 0.0764455 |
| cou_m | 60+ | 0.0248351 | 0.00814901 |
| sf | 0 | 0.0604396 | 0 |
| sf | 1-10 | 0.0307692 | 0.0021978 |
| sf | 11-20 | 0.0835165 | 0.056044 |
| sf | 21-30 | 0.347253 | 0.549451 |
| sf | 31-40 | 0.385714 | 0.385714 |
| sf | 41-50 | 0.0626374 | 0.00659341 |
| sf | 51-60 | 0.021978 | 0 |
| sf | 60+ | 0.00769231 | 0 |
| sm | 0 | 0.0704961 | 0 |
| sm | 1-10 | 0.0104439 | 0.00261097 |
| sm | 11-20 | 0.0483029 | 0.073107 |
| sm | 21-30 | 0.25718 | 0.5953 |
| sm | 31-40 | 0.480418 | 0.32376 |
| sm | 41-50 | 0.0770235 | 0.00522193 |
| sm | 51-60 | 0.0443864 | 0 |
| sm | 60+ | 0.0117493 | 0 |

## Wage Distribution Summary

Observed values use chosen working alternatives. Predicted values use
choice-probability weights over working alternatives.

| group | n_observed_working | predicted_worker_weight | obs_mean | pred_mean | obs_q10 | obs_q50 | obs_q90 | pred_q10 | pred_q50 | pred_q90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | 712 | 720.647 | 16.2131 | 12.6083 | 9.15372 | 14.2557 | 25.4434 | 6.18438 | 11.4962 | 20.1599 |
| singles_female | 855 | 857.038 | 15.1069 | 12.7477 | 8.65411 | 13.8516 | 22.9432 | 6.35389 | 11.716 | 20.2142 |
| couples_male | 2504 | 2533.11 | 17.656 | 17.1363 | 10.0631 | 15.2895 | 27.8735 | 9.00641 | 14.9892 | 27.7924 |
| couples_female | 2487 | 2547.83 | 15.1712 | 15.9613 | 8.86239 | 13.8393 | 22.4802 | 8.52899 | 13.9356 | 25.9489 |

## Occupation Distribution Shares

Observed shares use chosen working alternatives. Predicted shares use
choice-probability weights over working alternatives. Category labels
are reported for loc4-style variables when available.

| group | occupation_column | category | label | observed_share | predicted_share | observed_count | predicted_weight |
| --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | loc4 | -2 | unknown_observed_working | 0.00561798 | 0.000338926 | 4 | 0.244246 |
| singles_male | loc4 | 1 | routine_manual_ref | 0.407303 | 0.282626 | 290 | 203.674 |
| singles_male | loc4 | 2 | nonroutine_manual | 0.0941011 | 0.234399 | 67 | 168.919 |
| singles_male | loc4 | 3 | routine_cognitive | 0.0505618 | 0.208685 | 36 | 150.388 |
| singles_male | loc4 | 4 | nonroutine_cognitive | 0.442416 | 0.27395 | 315 | 197.421 |
| singles_female | loc4 | -2 | unknown_observed_working | 0.00350877 | 0.000850355 | 3 | 0.728787 |
| singles_female | loc4 | 1 | routine_manual_ref | 0.191813 | 0.258599 | 164 | 221.629 |
| singles_female | loc4 | 2 | nonroutine_manual | 0.20117 | 0.239811 | 172 | 205.527 |
| singles_female | loc4 | 3 | routine_cognitive | 0.130994 | 0.227679 | 112 | 195.129 |
| singles_female | loc4 | 4 | nonroutine_cognitive | 0.472515 | 0.273061 | 404 | 234.023 |
| couples_male | loc4_male | -2 | unknown_observed_working | 0.0123802 | 0.007306 | 31 | 18.5069 |
| couples_male | loc4_male | 1 | routine_manual_ref | 0.360224 | 0.35484 | 902 | 898.848 |
| couples_male | loc4_male | 2 | nonroutine_manual | 0.0802716 | 0.0842024 | 201 | 213.294 |
| couples_male | loc4_male | 3 | routine_cognitive | 0.0391374 | 0.0396443 | 98 | 100.423 |
| couples_male | loc4_male | 4 | nonroutine_cognitive | 0.507987 | 0.514007 | 1272 | 1302.03 |
| couples_female | loc4_female | -2 | unknown_observed_working | 0.00120627 | 0.000544389 | 3 | 1.38701 |
| couples_female | loc4_female | 1 | routine_manual_ref | 0.170084 | 0.168903 | 423 | 430.337 |
| couples_female | loc4_female | 2 | nonroutine_manual | 0.206273 | 0.203977 | 513 | 519.7 |
| couples_female | loc4_female | 3 | routine_cognitive | 0.152392 | 0.147807 | 379 | 376.587 |
| couples_female | loc4_female | 4 | nonroutine_cognitive | 0.470044 | 0.478768 | 1169 | 1219.82 |

## Notes For Use

- This Markdown file is the preferred low-token artifact for LLM review.
- Use the HTML report only when plots or visual diagnostics are needed.
- Generated output folders remain local unless explicitly added to Git.
