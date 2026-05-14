# RURO Low-Token Post-Estimation Summary

Generated: 2026-05-14T18:30:53

## Purpose

Compact text-only report for Git, paper drafting, and LLM review.
Figures and large HTML output are intentionally omitted.

## Sources

| item | path_or_value |
| --- | --- |
| estimation_results_json | \\crc\users\hisham\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0c_b\run_2026-05-14_18-09-27\estimation_results.json |
| html_report | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0c_b\run_2026-05-14_18-30-28\fr_2016_ruro_occ_gamspy_M0c_b_post_estimation_report_20260514_183049.html |
| post_output_dir | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0c_b\run_2026-05-14_18-30-28 |
| params_csv | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0c_b\run_2026-05-14_18-30-28\fr_2016_ruro_occ_gamspy_M0c_b_params.csv |
| elasticities_csv | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0c_b\run_2026-05-14_18-30-28\fr_2016_ruro_occ_gamspy_M0c_b_elasticities.csv |
| mnl_base | Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl |
| spec_config | scripts\enhanced\estimation_spec_ruro_occ_M0c_b.yaml |

## Run Metadata

| field | value |
| --- | --- |
| specification | ruro_occ_M0c_b |
| model_family | regular |
| market_opportunity_tier | NA |
| prior_correction_applied | 1 |
| prior_correction_form | -log(prior) |
| market_centering_applied | 1 |
| wage_spec | vw |
| estimation_walltime_seconds | 192.093 |

## Source Environment

| field | value |
| --- | --- |
| git_sha | 03295ef10124 |
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
| probability | minimum chosen probability is very small (1.006e-09) |
| hessian | negative eigenvalues present; inspect SE and local optimum diagnostics |

## Convergence Health Summary

| metric | value |
| --- | --- |
| n_estimated_params | 47 |
| log_likelihood | -6509.32 |
| AIC | 13112.6 |
| BIC | 13627.8 |
| rho_squared | 0.708384 |
| n_significant_p<0.05 | 30 |
| pct_significant_p<0.05 | 63.8% |
| n_low_t<1.0 | 9 |
| pct_low_t<1.0 | 19.1% |
| n_degenerate_se | 0 |
| n_at_bound_strict | 1 |
| hessian_condition_number | 8.60948e+09 |
| n_negative_eigenvalues | 1 |
| p_chosen_min | 1.00562e-09 |
| p_chosen_q10 | 0.0157015 |
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
| f | 4.05097 | NA | 2.61335 | beta_l_age=-0.0573895; beta_l_age2=0.00279012; beta_l_nkids=0.176729; beta_ll=2.5865 | -0.67769 | NA |
| m | 4.05097 | NA | 0.05 | beta_l_age=-0.00790677; beta_l_age2=0.000608608; beta_ll=2.5865 | -0.732916 | NA |
| sf | 0.575919 | NA | 4.45862 | beta_l_age=0.00190725; beta_l_age2=0.00413364; beta_l_nkids=0.0567715; beta_ll=2.5865 | -0.728042 | NA |
| sm | 0.635715 | NA | 3.8739 | beta_l_age=0.00849109; beta_l_age2=0.00202841; beta_ll=2.5865 | -0.711959 | NA |

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
| employment_hours | beta_E * working | beta_E | joint | -2.84204 |
| employment_hours | beta_h_pt1 * working_pt1 | beta_h_pt1 | joint | -0.498779 |
| employment_hours | beta_h_pt2 * working_pt2 | beta_h_pt2 | joint | 0.36504 |
| employment_hours | beta_h_ft * working_ft | beta_h_ft | joint | 1.44406 |
| employment_hours | beta_E_gsur * gsur * working | beta_E_gsur | joint | -0.743761 |
| employment_hours | beta_E_educH * educH * working | beta_E_educH | joint | 0.613419 |
| wage_mean | beta_w0 * intercept | beta_w0 | joint | 2.02487 |
| wage_mean | beta_w_educL * educL | beta_w_educL | joint | -0.0510071 |
| wage_mean | beta_w_educH * educH | beta_w_educH | joint | 0.316116 |
| wage_mean | beta_w_pexp * pexp_years | beta_w_pexp | joint | 0.0180963 |
| wage_mean | beta_w_pexp2 * pexp_years2 | beta_w_pexp2 | joint | -0.000218631 |
| wage_sigma | sigma | sigma | joint | 0.426763 |
| occupation:sm | beta_occ_2_sm * loc4_2 * working | beta_occ_2_sm | joint | -1.51042 |
| occupation:sm | beta_occ_3_sm * loc4_3 * working | beta_occ_3_sm | joint | -2.16513 |
| occupation:sm | beta_occ_4_sm * loc4_4 * working | beta_occ_4_sm | joint | 0.0236334 |
| occupation:sf | beta_occ_2_sf * loc4_2 * working | beta_occ_2_sf | joint | -0.0105005 |
| occupation:sf | beta_occ_3_sf * loc4_3 * working | beta_occ_3_sf | joint | -0.560987 |
| occupation:sf | beta_occ_4_sf * loc4_4 * working | beta_occ_4_sf | joint | 0.798779 |
| occupation:cm | beta_occ_2_cm * loc4_2 * working | beta_occ_2_cm | joint | -1.47591 |
| occupation:cm | beta_occ_3_cm * loc4_3 * working | beta_occ_3_cm | joint | -2.22391 |
| occupation:cm | beta_occ_4_cm * loc4_4 * working | beta_occ_4_cm | joint | 0.47259 |
| occupation:cf | beta_occ_2_cf * loc4_2 * working | beta_occ_2_cf | joint | 0.176189 |
| occupation:cf | beta_occ_3_cf * loc4_3 * working | beta_occ_3_cf | joint | -0.216365 |
| occupation:cf | beta_occ_4_cf * loc4_4 * working | beta_occ_4_cf | joint | 1.1147 |

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
| joint | 1 | SolveStatus.NormalCompletion (ModelStatus.OptimalLocal) | 8 | 8 | NA | -6509.32 | 64.0309 |

## Fit Statistics

| metric | value |
| --- | --- |
| log_likelihood | -6509.32 |
| ll_null_uniform | -19585.8 |
| ll_null_prior_corrected | -22321.6 |
| rho_squared | 0.708384 |
| rho_squared_adj | 0.706279 |
| rho_squared_uniform | 0.667651 |
| rho_squared_prior_corrected | 0.708384 |
| AIC | 13112.6 |
| BIC | 13627.8 |
| AIC_per_obs | 0.0308315 |
| n_observations | 425300 |
| n_groups | 4253 |
| n_parameters | 47 |
| n_obs_long | 425300 |

## Fit Moments

| group | participation_observed | participation_predicted | mean_hours_observed | mean_hours_predicted |
| --- | --- | --- | --- | --- |
| cou_f | 0.965076 | 0.988688 | 35.6466 | 38.9768 |
| cou_m | 0.971672 | 0.982982 | 41.6062 | 42.7852 |
| sf | 0.93956 | 0.951652 | 36.2971 | 35.0829 |
| sm | 0.929504 | 0.908373 | 39.3048 | 35.7176 |

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
| cou_m | hours_bins | 8 | 0.343 | 0.1701 |
| sf | hours_bins | 8 | 0.4044 | 0.2231 |
| sm | hours_bins | 8 | 0.7258 | 0.3896 |

## Observed vs Implied Log-Wage σ (chosen working alts)

| group | n | observed_mean_log_wage | observed_std_log_wage | implied_sigma |
| --- | --- | --- | --- | --- |
| singles_male | 712 | 2.6836 | 0.4502 | 0.426763 |
| singles_female | 855 | 2.6198 | 0.436 | 0.426763 |
| couples_male | 2504 | 2.7697 | 0.4402 | 0.426763 |
| couples_female | 2487 | 2.6221 | 0.436 | 0.426763 |

## Structural Elasticity Heuristics

These are curvature-based heuristics from the post-estimation script, not
policy-counterfactual elasticities.

| Group | Hicksian (compensated) | Marshallian (uncompensated) | Participation (extensive) | Intensive (conditional) | theta_l | theta_c | beta_l (at median X) | beta_c |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single Males | 1.712 | 1.612 | 0.514 | 1.198 | -0.712 | 0.500 | 3.874 | 0.636 |
| Single Females | 1.728 | 1.628 | 0.518 | 1.210 | -0.728 | 0.500 | 4.459 | 0.576 |
| Males in Couples | 1.733 | 1.633 | 0.520 | 1.213 | -0.733 | 0.500 | 0.050 | 4.051 |
| Females in Couples | 1.678 | 1.578 | 0.503 | 1.174 | -0.678 | 0.500 | 2.613 | 4.051 |

## Marginal Utility Diagnostics

| Group | beta_c | theta_c | MUC Positive? | MUC Diminishing? | Well-Behaved? | MUC at Median C | C where MUC=1 | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single Males | 0.635715 | 0.5 | yes | yes | yes | 0.635715 | 0.404134 | NA |
| Single Females | 0.575919 | 0.5 | yes | yes | yes | 0.575919 | 0.331683 | NA |
| Males in Couples | 4.05097 | 0.5 | yes | yes | yes | 4.05097 | 16.4104 | NA |
| Females in Couples | 4.05097 | 0.5 | yes | yes | yes | 4.05097 | 16.4104 | NA |

## Marginal Utility Distribution Summary

| group | N | n_neg_muc | pct_neg_muc | mean_muc | n_neg_mul | pct_neg_mul | mean_mul |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cou_f | 2577 | 0 | 0 | 0.0639653 | 0 | 0 | 0.00551224 |
| cou_m | 2577 | 0 | 0 | 0.0639653 | 0 | 0 | 0.000118825 |
| sf | 766 | 0 | 0 | 0.0133504 | 0 | 0 | 0.00980133 |
| sm | 910 | 0 | 0 | 0.0147257 | 0 | 0 | 0.00732157 |
| total | NA | 0 | 0 | NA | 0 | 0 | NA |

## Probability Diagnostics

| metric | value |
| --- | --- |
| prob_sum_max_error | 8.88178e-16 |
| prob_sum_mean_error | 1.31201e-16 |
| prob_sum_pct_off_by_0.01 | 0 |
| prob_sum_pct_off_by_0.001 | 0 |
| p_chosen_min | 1.00562e-09 |
| p_chosen_max | 0.999324 |
| p_chosen_mean | 0.388436 |
| p_chosen_median | 0.269602 |
| p_chosen_q10 | 0.0157015 |
| p_chosen_q25 | 0.0671025 |
| p_chosen_q75 | 0.722563 |
| p_chosen_q90 | 0.920054 |

## Worst-Fit Households

| rank | idhh | group | p_chosen | ll_i |
| --- | --- | --- | --- | --- |
| 1 | 4012700 | sm | 1.00562e-09 | -20.7177 |
| 2 | 3600001 | sf | 1.19874e-09 | -20.542 |
| 3 | 4264600 | cou | 5.26081e-09 | -19.063 |
| 4 | 1935801 | sm | 1.23919e-08 | -18.2062 |
| 5 | 3457500 | sm | 3.2928e-08 | -17.2289 |
| 6 | 1918802 | sf | 4.55927e-08 | -16.9035 |
| 7 | 1729600 | cou | 2.80876e-07 | -15.0854 |
| 8 | 3233100 | cou | 5.49043e-07 | -14.4151 |
| 9 | 2989700 | cou | 1.91101e-06 | -13.1679 |
| 10 | 3317202 | sf | 3.55095e-06 | -12.5483 |

## Identification Diagnostics

| metric | value |
| --- | --- |
| condition_number | 8.60948e+09 |
| min_eigenvalue | -13.892 |
| max_eigenvalue | 1.36732e+10 |
| n_negative_eigenvalues | 1 |

_Interpretation: weakly conditioned (1e6 <= kappa < 1e10); 1 negative eigenvalue(s) - not at a local maximum or numerically singular._

## Initial → Final Movement (top 15 by |Δ|)

| block | parameter | initial_value | final_estimate | delta |
| --- | --- | --- | --- | --- |
| preference | joint.beta_ll | 2 | 2.5865 | 0.5865 |
| preference | joint.beta_l0_f | 2.80029 | 2.61335 | -0.186934 |
| preference | joint.beta_c | 3.92777 | 4.05097 | 0.123206 |
| preference | joint.beta_l0_sf | 4.38279 | 4.45862 | 0.0758269 |
| preference | joint.beta_l0_m | 0.125438 | 0.05 | -0.0754384 |
| preference | joint.theta_l_m | -0.670577 | -0.732916 | -0.0623389 |
| preference | joint.beta_l0_sm | 3.81389 | 3.8739 | 0.0600035 |
| preference | joint.beta_c_sm | 0.591531 | 0.635715 | 0.0441844 |
| preference | joint.beta_c_sf | 0.534713 | 0.575919 | 0.0412061 |
| preference | joint.theta_c_singles | -0.970811 | -0.935803 | 0.0350079 |
| preference | joint.theta_l_f | -0.653351 | -0.67769 | -0.0243388 |
| employment_hours_opportunity | joint.beta_h_ft | 1.45297 | 1.44406 | -0.00890432 |
| occupation_opportunity | joint.beta_occ_3_cf | -0.209648 | -0.216365 | -0.00671786 |
| preference | joint.beta_l_nkids_sf | 0.0633136 | 0.0567715 | -0.00654215 |
| preference | joint.beta_l_nkids_f | 0.182795 | 0.176729 | -0.00606591 |

## Top High-Correlation Parameter Pairs

| param_i | param_j | correlation |
| --- | --- | --- |
| theta_c_singles | beta_c | -1.08597 |
| beta_c_sm | beta_c_sf | -1.05437 |
| beta_c_sf | theta_c_singles | -1.04383 |
| beta_c_sm | theta_c_singles | -1.03423 |
| beta_w_pexp | beta_w_pexp2 | -0.960306 |
| beta_c_sm | beta_c | -0.95112 |
| beta_E | beta_E_gsur | -0.95021 |
| beta_c_sf | beta_c | -0.930153 |

## Weakest Eigenvector Diagnostics

_None._

## Parameters At Bounds

| parameter | estimate | bound | side |
| --- | --- | --- | --- |
| joint.beta_l0_m | 0.05 | 0.05 | lower |

## Parameters Near Bounds (within 5% of bound width)

| block | parameter | estimate | lower_bound | upper_bound | flags |
| --- | --- | --- | --- | --- | --- |
| preference | joint.beta_c_sm | 0.635715 | 0.05 | 50 | near_lower(delta=0.586) |
| preference | joint.beta_c_sf | 0.575919 | 0.05 | 50 | near_lower(delta=0.526) |
| wage_opportunity | joint.sigma | 0.426763 | 0.1 | 20 | near_lower(delta=0.327) |

## Top Significant Coefficients (top 15 by |t|)

| block | parameter | estimate | std_error | t_value | p_value |
| --- | --- | --- | --- | --- | --- |
| wage_opportunity | joint.sigma | 0.426763 | 0.0039574 | 107.839 | 0 |
| wage_opportunity | joint.beta_w0 | 2.02487 | 0.0252353 | 80.2394 | 0 |
| preference | joint.beta_c | 4.05097 | 0.120822 | 33.5285 | 0 |
| employment_hours_opportunity | joint.beta_h_ft | 1.44406 | 0.0500596 | 28.8468 | 0 |
| wage_opportunity | joint.beta_w_educH | 0.316116 | 0.0149507 | 21.1439 | 0 |
| occupation_opportunity | joint.beta_occ_3_cm | -2.22391 | 0.147943 | -15.0322 | 0 |
| occupation_opportunity | joint.beta_occ_4_cf | 1.1147 | 0.0813798 | 13.6975 | 0 |
| occupation_opportunity | joint.beta_occ_2_cm | -1.47591 | 0.113754 | -12.9746 | 0 |
| occupation_opportunity | joint.beta_occ_3_sm | -2.16513 | 0.184236 | -11.7519 | 0 |
| occupation_opportunity | joint.beta_occ_2_sm | -1.51042 | 0.142052 | -10.6329 | 0 |
| employment_hours_opportunity | joint.beta_E | -2.84204 | 0.299124 | -9.50122 | 0 |
| occupation_opportunity | joint.beta_occ_4_sf | 0.798779 | 0.092047 | 8.67795 | 0 |
| wage_opportunity | joint.beta_w_pexp | 0.0180963 | 0.00223156 | 8.10926 | 4.44089e-16 |
| preference | joint.theta_l_f | -0.67769 | 0.0925501 | -7.32241 | 2.43583e-13 |
| occupation_opportunity | joint.beta_occ_4_cm | 0.47259 | 0.0687698 | 6.87205 | 6.32849e-12 |

## Parameter Estimates By Block

| block | parameter | estimate | std_error | t_value | p_value | lower_bound | upper_bound | initial_value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| employment_hours_opportunity | joint.beta_E | -2.84204 | 0.299124 | -9.50122 | 0 | -25 | 25 | -2.83851 |
| employment_hours_opportunity | joint.beta_h_ft | 1.44406 | 0.0500596 | 28.8468 | 0 | -10 | 10 | 1.45297 |
| employment_hours_opportunity | joint.beta_h_pt1 | -0.498779 | 0.10794 | -4.62088 | 3.82117e-06 | -10 | 10 | -0.50087 |
| employment_hours_opportunity | joint.beta_h_pt2 | 0.36504 | 0.111314 | 3.27938 | 0.00104036 | -10 | 10 | 0.370668 |
| market_residual_opportunity | joint.beta_E_educH | 0.613419 | 0.236158 | 2.59749 | 0.00939078 | -10 | 10 | 0.612937 |
| market_residual_opportunity | joint.beta_E_gsur | -0.743761 | 0.220686 | -3.37023 | 0.000751068 | -10 | 10 | -0.743345 |
| occupation_opportunity | joint.beta_occ_2_cf | 0.176189 | 0.100274 | 1.75708 | 0.0789044 | -10 | 10 | 0.180023 |
| occupation_opportunity | joint.beta_occ_2_cm | -1.47591 | 0.113754 | -12.9746 | 0 | -10 | 10 | -1.47884 |
| occupation_opportunity | joint.beta_occ_2_sf | -0.0105005 | 0.112635 | -0.0932253 | 0.925725 | -10 | 10 | -0.0103955 |
| occupation_opportunity | joint.beta_occ_2_sm | -1.51042 | 0.142052 | -10.6329 | 0 | -10 | 10 | -1.5101 |
| occupation_opportunity | joint.beta_occ_3_cf | -0.216365 | 0.111627 | -1.93829 | 0.0525878 | -10 | 10 | -0.209648 |
| occupation_opportunity | joint.beta_occ_3_cm | -2.22391 | 0.147943 | -15.0322 | 0 | -10 | 10 | -2.22473 |
| occupation_opportunity | joint.beta_occ_3_sf | -0.560987 | 0.128972 | -4.34967 | 1.36342e-05 | -10 | 10 | -0.560591 |
| occupation_opportunity | joint.beta_occ_3_sm | -2.16513 | 0.184236 | -11.7519 | 0 | -10 | 10 | -2.16495 |
| occupation_opportunity | joint.beta_occ_4_cf | 1.1147 | 0.0813798 | 13.6975 | 0 | -10 | 10 | 1.11838 |
| occupation_opportunity | joint.beta_occ_4_cm | 0.47259 | 0.0687698 | 6.87205 | 6.32849e-12 | -10 | 10 | 0.471425 |
| occupation_opportunity | joint.beta_occ_4_sf | 0.798779 | 0.092047 | 8.67795 | 0 | -10 | 10 | 0.798669 |
| occupation_opportunity | joint.beta_occ_4_sm | 0.0236334 | 0.0860264 | 0.274723 | 0.783529 | -10 | 10 | 0.0239881 |
| preference | joint.beta_c | 4.05097 | 0.120822 | 33.5285 | 0 | 0.05 | 50 | 3.92777 |
| preference | joint.beta_c_sf | 0.575919 | NA | NA | NA | 0.05 | 50 | 0.534713 |
| preference | joint.beta_c_sm | 0.635715 | NA | NA | NA | 0.05 | 50 | 0.591531 |
| preference | joint.beta_l0_f | 2.61335 | 0.646921 | 4.03968 | 5.35243e-05 | 0.05 | 50 | 2.80029 |
| preference | joint.beta_l0_m | 0.05 | NA | NA | NA | 0.05 | 50 | 0.125438 |
| preference | joint.beta_l0_sf | 4.45862 | 0.780814 | 5.71022 | 1.1283e-08 | 0.05 | 50 | 4.38279 |
| preference | joint.beta_l0_sm | 3.8739 | 0.720913 | 5.3736 | 7.71817e-08 | 0.05 | 50 | 3.81389 |
| preference | joint.beta_l_age2_f | 0.00279012 | 0.00220601 | 1.26478 | 0.20595 | -1 | 1 | 0.00270149 |
| preference | joint.beta_l_age2_m | 0.000608608 | 0.00145424 | 0.418507 | 0.675576 | -1 | 1 | 0.00173456 |
| preference | joint.beta_l_age2_sf | 0.00413364 | 0.00256804 | 1.60964 | 0.107475 | -1 | 1 | 0.00413917 |
| preference | joint.beta_l_age2_sm | 0.00202841 | 0.00208357 | 0.97353 | 0.33029 | -1 | 1 | 0.00202866 |
| preference | joint.beta_l_age_f | -0.0573895 | 0.0222188 | -2.58292 | 0.00979682 | -5 | 5 | -0.0546416 |
| preference | joint.beta_l_age_m | -0.00790677 | 0.0150499 | -0.525372 | 0.599325 | -5 | 5 | -0.0085413 |
| preference | joint.beta_l_age_sf | 0.00190725 | 0.0272253 | 0.0700542 | 0.944151 | -5 | 5 | 0.00164869 |
| preference | joint.beta_l_age_sm | 0.00849109 | 0.024821 | 0.342092 | 0.732281 | -5 | 5 | 0.00821039 |
| preference | joint.beta_l_nkids_f | 0.176729 | 0.215871 | 0.818677 | 0.41297 | -5 | 5 | 0.182795 |
| preference | joint.beta_l_nkids_sf | 0.0567715 | 0.35795 | 0.158602 | 0.873983 | -5 | 5 | 0.0633136 |
| preference | joint.beta_ll | 2.5865 | 0.389479 | 6.64092 | 3.11733e-11 | 0 | 10 | 2 |
| preference | joint.theta_c_singles | -0.935803 | NA | NA | NA | -8 | 0.95 | -0.970811 |
| preference | joint.theta_l_f | -0.67769 | 0.0925501 | -7.32241 | 2.43583e-13 | -8 | 0.95 | -0.653351 |
| preference | joint.theta_l_m | -0.732916 | 0.118951 | -6.16148 | 7.20666e-10 | -8 | 0.95 | -0.670577 |
| preference | joint.theta_l_sf | -0.728042 | 0.134401 | -5.41695 | 6.06228e-08 | -8 | 0.95 | -0.729829 |
| preference | joint.theta_l_sm | -0.711959 | 0.154657 | -4.60346 | 4.15521e-06 | -8 | 0.95 | -0.71544 |
| wage_opportunity | joint.beta_w0 | 2.02487 | 0.0252353 | 80.2394 | 0 | -10 | 20 | 2.0302 |
| wage_opportunity | joint.beta_w_educH | 0.316116 | 0.0149507 | 21.1439 | 0 | -5 | 5 | 0.31745 |
| wage_opportunity | joint.beta_w_educL | -0.0510071 | 0.0211244 | -2.4146 | 0.0157524 | -5 | 5 | -0.0515513 |
| wage_opportunity | joint.beta_w_pexp | 0.0180963 | 0.00223156 | 8.10926 | 4.44089e-16 | -1 | 1 | 0.0181215 |
| wage_opportunity | joint.beta_w_pexp2 | -0.000218631 | 4.94572e-05 | -4.42061 | 9.84239e-06 | -0.1 | 0.1 | -0.000218554 |
| wage_opportunity | joint.sigma | 0.426763 | 0.0039574 | 107.839 | 0 | 0.1 | 20 | 0.427852 |

## Hours Distribution Shares

| group | hours_bin | observed_share | predicted_share |
| --- | --- | --- | --- |
| cou_f | 0 | 0.0349243 | 0 |
| cou_f | 1-10 | 0.0256112 | 0.00543267 |
| cou_f | 11-20 | 0.0923555 | 0.0488941 |
| cou_f | 21-30 | 0.38766 | 0.239814 |
| cou_f | 31-40 | 0.381451 | 0.513776 |
| cou_f | 41-50 | 0.0523865 | 0.161428 |
| cou_f | 51-60 | 0.0201785 | 0.0294917 |
| cou_f | 60+ | 0.00543267 | 0.00116414 |
| cou_m | 0 | 0.0283275 | 0.000776096 |
| cou_m | 1-10 | 0.00388048 | 0.00232829 |
| cou_m | 11-20 | 0.0209546 | 0.0182383 |
| cou_m | 21-30 | 0.256888 | 0.133877 |
| cou_m | 31-40 | 0.470702 | 0.530462 |
| cou_m | 41-50 | 0.135429 | 0.229724 |
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
| singles_male | 712 | 720.659 | 16.2131 | 12.6085 | 9.15372 | 14.2557 | 25.4434 | 6.18439 | 11.4962 | 20.1599 |
| singles_female | 855 | 857.052 | 15.1069 | 12.748 | 8.65411 | 13.8516 | 22.9432 | 6.35414 | 11.7166 | 20.2143 |
| couples_male | 2504 | 2533.14 | 17.656 | 17.1365 | 10.0631 | 15.2895 | 27.8735 | 9.00629 | 14.9892 | 27.797 |
| couples_female | 2487 | 2547.85 | 15.1712 | 15.9618 | 8.86239 | 13.8393 | 22.4802 | 8.52888 | 13.9357 | 25.9491 |

## Occupation Distribution Shares

Observed shares use chosen working alternatives. Predicted shares use
choice-probability weights over working alternatives. Category labels
are reported for loc4-style variables when available.

| group | occupation_column | category | label | observed_share | predicted_share | observed_count | predicted_weight |
| --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | loc4 | -2 | unknown_observed_working | 0.00561798 | 0.000338928 | 4 | 0.244251 |
| singles_male | loc4 | 1 | routine_manual_ref | 0.407303 | 0.282627 | 290 | 203.677 |
| singles_male | loc4 | 2 | nonroutine_manual | 0.0941011 | 0.234399 | 67 | 168.922 |
| singles_male | loc4 | 3 | routine_cognitive | 0.0505618 | 0.208685 | 36 | 150.391 |
| singles_male | loc4 | 4 | nonroutine_cognitive | 0.442416 | 0.27395 | 315 | 197.425 |
| singles_female | loc4 | -2 | unknown_observed_working | 0.00350877 | 0.000850354 | 3 | 0.728797 |
| singles_female | loc4 | 1 | routine_manual_ref | 0.191813 | 0.258599 | 164 | 221.632 |
| singles_female | loc4 | 2 | nonroutine_manual | 0.20117 | 0.239811 | 172 | 205.531 |
| singles_female | loc4 | 3 | routine_cognitive | 0.130994 | 0.227679 | 112 | 195.133 |
| singles_female | loc4 | 4 | nonroutine_cognitive | 0.472515 | 0.273061 | 404 | 234.027 |
| couples_male | loc4_male | -2 | unknown_observed_working | 0.0123802 | 0.00730444 | 31 | 18.5032 |
| couples_male | loc4_male | 1 | routine_manual_ref | 0.360224 | 0.354826 | 902 | 898.825 |
| couples_male | loc4_male | 2 | nonroutine_manual | 0.0802716 | 0.0842074 | 201 | 213.309 |
| couples_male | loc4_male | 3 | routine_cognitive | 0.0391374 | 0.0396466 | 98 | 100.43 |
| couples_male | loc4_male | 4 | nonroutine_cognitive | 0.507987 | 0.514016 | 1272 | 1302.08 |
| couples_female | loc4_female | -2 | unknown_observed_working | 0.00120627 | 0.000544442 | 3 | 1.38715 |
| couples_female | loc4_female | 1 | routine_manual_ref | 0.170084 | 0.16891 | 423 | 430.357 |
| couples_female | loc4_female | 2 | nonroutine_manual | 0.206273 | 0.203965 | 513 | 519.672 |
| couples_female | loc4_female | 3 | routine_cognitive | 0.152392 | 0.147801 | 379 | 376.573 |
| couples_female | loc4_female | 4 | nonroutine_cognitive | 0.470044 | 0.47878 | 1169 | 1219.86 |

## Notes For Use

- This Markdown file is the preferred low-token artifact for LLM review.
- Use the HTML report only when plots or visual diagnostics are needed.
- Generated output folders remain local unless explicitly added to Git.
