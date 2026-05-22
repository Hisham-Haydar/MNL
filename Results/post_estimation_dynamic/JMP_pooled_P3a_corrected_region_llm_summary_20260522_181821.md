# RURO Low-Token Post-Estimation Summary

Generated: 2026-05-22T18:18:32

## Purpose

Compact text-only report for Git, paper drafting, and LLM review.
Figures and large HTML output are intentionally omitted.

## Sources

| item | path_or_value |
| --- | --- |
| estimation_results_json | outputs\estimates\fr\spec\ruro_occ_P3a_pooled\gamspy\start_1\run_2026-05-21_23-47-14\estimation_results.json |
| html_report | Results\post_estimation_dynamic\estimation_spec_ruro_occ_P3a_pooled\run_2026-05-22_18-17-34\JMP_pooled_P3a_corrected_region_post_estimation_report_20260522_181821.html |
| post_output_dir | Results\post_estimation_dynamic\estimation_spec_ruro_occ_P3a_pooled\run_2026-05-22_18-17-34 |
| params_csv | Results\post_estimation_dynamic\estimation_spec_ruro_occ_P3a_pooled\run_2026-05-22_18-17-34\JMP_pooled_P3a_corrected_region_params.csv |
| elasticities_csv | Results\post_estimation_dynamic\estimation_spec_ruro_occ_P3a_pooled\run_2026-05-22_18-17-34\JMP_pooled_P3a_corrected_region_elasticities.csv |
| mnl_base | Data\processed\fr\pooled\fr_p3a_gsurv2_estimation_ready |
| spec_config | scripts\enhanced\specifications\estimation_spec_ruro_occ_P3a_pooled.yaml |

## Run Metadata

| field | value |
| --- | --- |
| specification | ruro_occ_P3a_pooled |
| model_family | regular |
| market_opportunity_tier | NA |
| prior_correction_applied | 1 |
| prior_correction_form | -log(prior) |
| market_centering_applied | 1 |
| wage_spec | vw |
| estimation_walltime_seconds | 820.441 |

## Source Environment

| field | value |
| --- | --- |
| git_sha | 0be727602be7 |
| git_branch | main |
| git_dirty | 1 |

## Choice Data Footprint

| dataset | rows | groups | alt_min | alt_median | alt_max | chosen_rows | working_rows | n_columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| singles | 500700 | 3902 | 100 | 100 | 200 | 5007 | 450439 | 148 |
| couples | 743800 | 5838 | 100 | 100 | 200 | 7438 | male=668927; female=669316 | 148 |

## Per-Group Sample Sizes

| group | n_obs | n_households | alts_per_hh | n_chosen | n_working |
| --- | --- | --- | --- | --- | --- |
| singles_male | 224300 | 1738 | 129.06 | 2243 | 201879 |
| singles_female | 276400 | 2164 | 127.73 | 2764 | 248560 |
| couples_male | 743800 | 5838 | 127.41 | 7438 | 668927 |
| couples_female | 743800 | 5838 | 127.41 | 7438 | 669316 |

## Sample Descriptives (chosen alternatives, by group)

| group | variable | mean | std | min | max | n |
| --- | --- | --- | --- | --- | --- | --- |
| singles_male | age_norm | -0.4502 | 11.0846 | -25.5811 | 21.5135 | 2243 |
| singles_male | age_norm2 | 123.016 | 128.971 | 0.0326 | 654.395 | 2243 |
| singles_male | educL | 0.1694 | 0.3752 | 0 | 1 | 2243 |
| singles_male | educM | 0.4498 | 0.4976 | 0 | 1 | 2243 |
| singles_male | educH | 0.3807 | 0.4857 | 0 | 1 | 2243 |
| singles_male | pexp_years | 21.6508 | 11.9533 | 0 | 49 | 2243 |
| singles_male | n_children | 0.1908 | 0.5565 | 0 | 4 | 2243 |
| singles_male | gsur | 0.096 | 0.0411 | 0.047 | 0.261 | 2243 |
| singles_female | age_norm | 0.3653 | 10.8769 | -24.8195 | 21.5135 | 2764 |
| singles_female | age_norm2 | 118.398 | 123.4 | 0.0326 | 616.007 | 2764 |
| singles_female | educL | 0.1436 | 0.3508 | 0 | 1 | 2764 |
| singles_female | educM | 0.4352 | 0.4959 | 0 | 1 | 2764 |
| singles_female | educH | 0.4211 | 0.4938 | 0 | 1 | 2764 |
| singles_female | pexp_years | 20.9239 | 11.7013 | 0 | 49 | 2764 |
| singles_female | n_children | 0.5438 | 0.8605 | 0 | 5 | 2764 |
| singles_female | gsur | 0.092 | 0.035 | 0.0478 | 0.23 | 2764 |
| couples_male | age_norm | 0 | 9.6878 | -23.8636 | 23.1364 | 7438 |
| couples_male | age_norm2 | 93.8407 | 101.076 | 0.0186 | 569.471 | 7438 |
| couples_male | educL | 0.1492 | 0.3563 | 0 | 1 | 7438 |
| couples_male | educM | 0.4636 | 0.4987 | 0 | 1 | 7438 |
| couples_male | educH | 0.3872 | 0.4871 | 0 | 1 | 7438 |
| couples_male | pexp_years | 21.386 | 10.5147 | 0 | 49 | 7438 |
| couples_male | gsur | 0.0945 | 0.0392 | 0.047 | 0.261 | 7438 |
| couples_female | age_norm | 0 | 9.7204 | -22.2545 | 25.2194 | 7438 |
| couples_female | age_norm2 | 94.4727 | 102.479 | 0.0243 | 636.019 | 7438 |
| couples_female | educL | 0.1206 | 0.3257 | 0 | 1 | 7438 |
| couples_female | educM | 0.4032 | 0.4906 | 0 | 1 | 7438 |
| couples_female | educH | 0.4762 | 0.4995 | 0 | 1 | 7438 |
| couples_female | pexp_years | 18.1845 | 10.3775 | 0 | 47 | 7438 |
| couples_female | gsur | 0.088 | 0.0336 | 0.0478 | 0.23 | 7438 |

## Proposal And Prior Diagnostics

| dataset | min_prior | max_abs_log_prior_minus_log_density | max_abs_prior_alias_reconstruction | missing_aliases | forbidden_columns_present |
| --- | --- | --- | --- | --- | --- |
| singles | 7.54603e-06 | 0 | 0 | none | none |
| couples | 5.90796e-11 | 0 | 0 | none | none |

## Warnings And Review Flags

| type | message |
| --- | --- |
| identification | weakly conditioned (1e6 <= kappa < 1e10); 5 negative eigenvalue(s) - not at a local maximum or numerically singular |
| fit | cou_f: predicted participation is very high (0.9904) |
| hessian | negative eigenvalues present; inspect SE and local optimum diagnostics |

## Convergence Health Summary

| metric | value |
| --- | --- |
| n_estimated_params | 55 |
| log_likelihood | -19084.3 |
| AIC | 38278.7 |
| BIC | 38940.5 |
| rho_squared | 0.49352 |
| n_significant_p<0.05 | 37 |
| pct_significant_p<0.05 | 67.3% |
| n_low_t<1.0 | 3 |
| pct_low_t<1.0 | 5.5% |
| n_degenerate_se | 0 |
| n_at_bound_strict | 1 |
| hessian_condition_number | 3.31629e+09 |
| n_negative_eigenvalues | 5 |
| p_chosen_min | NA |
| p_chosen_q10 | NA |
| review_priority_flags | negative_eigenvalues_present, parameters_at_bounds |

## Model Index Equation

V_ij = U_ij + O^E_ij + O^H_ij + O^W_ij + O^Occ_ij - log_prior_ij

P_ij = exp(V_ij) / sum_k exp(V_ik)

## Utility / Preference Parameters By Group

Utility uses Box-Cox consumption and leisure. This table gives the
group-level consumption and leisure parameters resolved from the
estimated parameter vector.

| group | beta_c | theta_c | beta_l0 | beta_l_shifters | theta_l | beta_cl |
| --- | --- | --- | --- | --- | --- | --- |
| f | 4.31241 | NA | 2.60529 | beta_l_age=-0.0580316; beta_l_age2=0.0052876; beta_l_nkids=0.142852; beta_ll=2.65594 | -0.657847 | NA |
| m | 4.31241 | NA | 1e-06 | beta_l_age=0.00587034; beta_l_age2=0.00164643; beta_ll=2.65594 | -0.681907 | NA |
| sf | 2.35133 | NA | 4.46019 | beta_l_age=0.0385062; beta_l_age2=0.00460958; beta_l_nkids=0.356277; beta_ll=2.65594 | -0.701604 | NA |
| sm | 2.73315 | NA | 4.32809 | beta_l_age=0.0431437; beta_l_age2=0.0017236; beta_ll=2.65594 | -0.719206 | NA |

## Specification Block Inventory

| yaml_block | label | n_shifters | variables | coefficients |
| --- | --- | --- | --- | --- |
| utility.consumption.coefficient | consumption scale | 1 | - | beta_c |
| utility.consumption.box_cox_exponent | consumption theta_c | 1 | - | theta_c |
| utility.leisure.intercept | leisure intercept | 1 | - | beta_l0 |
| utility.leisure.box_cox_exponent | leisure theta_l | 1 | - | theta_l |
| utility.leisure.shifters | Utility-leisure shifters | 3 | age_norm, age_norm2, n_children | beta_l_age, beta_l_age2, beta_l_nkids |
| hours_opportunity | Employment/Hours | 4 | working, working_ft, working_pt1, working_pt2 | beta_E, beta_h_pt1, beta_h_pt2, beta_h_ft |
| market_opportunity | Market residual | 10 | gsur, reg2, reg3, reg4, reg5, reg6, reg7, reg8, year_2015_indicator, year_2017_indicator | beta_E_gsur, beta_E_drgn2, beta_E_drgn3, beta_E_drgn4, beta_E_drgn5, beta_E_drgn6, beta_E_drgn7, beta_E_drgn8, beta_E_y2015, beta_E_y2017 |
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
+ beta_E_drgn2 * reg2 * working
+ beta_E_drgn3 * reg3 * working
+ beta_E_drgn4 * reg4 * working
+ beta_E_drgn5 * reg5 * working
+ beta_E_drgn6 * reg6 * working
+ beta_E_drgn7 * reg7 * working
+ beta_E_drgn8 * reg8 * working
+ beta_E_y2015 * year_2015_indicator * working
+ beta_E_y2017 * year_2017_indicator * working

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
| employment_hours | beta_E * working | beta_E | joint | -2.39772 |
| employment_hours | beta_h_pt1 * working_pt1 | beta_h_pt1 | joint | -0.474816 |
| employment_hours | beta_h_pt2 * working_pt2 | beta_h_pt2 | joint | 0.424756 |
| employment_hours | beta_h_ft * working_ft | beta_h_ft | joint | 1.40592 |
| employment_hours | beta_E_gsur * gsur * working | beta_E_gsur | joint | -1.19992 |
| employment_hours | beta_E_drgn2 * reg2 * working | beta_E_drgn2 | joint | 0.396497 |
| employment_hours | beta_E_drgn3 * reg3 * working | beta_E_drgn3 | joint | 0.35 |
| employment_hours | beta_E_drgn4 * reg4 * working | beta_E_drgn4 | joint | 0.641609 |
| employment_hours | beta_E_drgn5 * reg5 * working | beta_E_drgn5 | joint | 0.431035 |
| employment_hours | beta_E_drgn6 * reg6 * working | beta_E_drgn6 | joint | 0.357738 |
| employment_hours | beta_E_drgn7 * reg7 * working | beta_E_drgn7 | joint | 0.367068 |
| employment_hours | beta_E_drgn8 * reg8 * working | beta_E_drgn8 | joint | 0.167527 |
| employment_hours | beta_E_y2015 * year_2015_indicator * working | beta_E_y2015 | joint | -0.0590898 |
| employment_hours | beta_E_y2017 * year_2017_indicator * working | beta_E_y2017 | joint | 0.15543 |
| wage_mean | beta_w0 * intercept | beta_w0 | joint | 2.03334 |
| wage_mean | beta_w_educL * educL | beta_w_educL | joint | -0.0414001 |
| wage_mean | beta_w_educH * educH | beta_w_educH | joint | 0.306669 |
| wage_mean | beta_w_pexp * pexp_years | beta_w_pexp | joint | 0.0173056 |
| wage_mean | beta_w_pexp2 * pexp_years2 | beta_w_pexp2 | joint | -0.000181961 |
| wage_sigma | sigma | sigma | joint | 0.403406 |
| occupation:sm | beta_occ_2_sm * loc4_2 * working | beta_occ_2_sm | joint | -1.49616 |
| occupation:sm | beta_occ_3_sm * loc4_3 * working | beta_occ_3_sm | joint | -2.13838 |
| occupation:sm | beta_occ_4_sm * loc4_4 * working | beta_occ_4_sm | joint | 0.0743814 |
| occupation:sf | beta_occ_2_sf * loc4_2 * working | beta_occ_2_sf | joint | -0.104983 |
| occupation:sf | beta_occ_3_sf * loc4_3 * working | beta_occ_3_sf | joint | -0.532782 |
| occupation:sf | beta_occ_4_sf * loc4_4 * working | beta_occ_4_sf | joint | 0.763932 |
| occupation:cm | beta_occ_2_cm * loc4_2 * working | beta_occ_2_cm | joint | -1.50261 |
| occupation:cm | beta_occ_3_cm * loc4_3 * working | beta_occ_3_cm | joint | -2.22222 |
| occupation:cm | beta_occ_4_cm * loc4_4 * working | beta_occ_4_cm | joint | 0.476417 |
| occupation:cf | beta_occ_2_cf * loc4_2 * working | beta_occ_2_cf | joint | 0.113438 |
| occupation:cf | beta_occ_3_cf * loc4_3 * working | beta_occ_3_cf | joint | -0.329211 |
| occupation:cf | beta_occ_4_cf * loc4_4 * working | beta_occ_4_cf | joint | 1.07548 |

## Per-Block Parameter Counts and Significance

| block | n_params | n_estimable | n_sig_p<0.001 | n_sig_p<0.01 | n_sig_p<0.05 | n_sig_p<0.10 |
| --- | --- | --- | --- | --- | --- | --- |
| preference | 23 | 23 | 10 | 12 | 13 | 14 |
| employment_hours_opportunity | 4 | 4 | 4 | 4 | 4 | 4 |
| market_residual_opportunity | 10 | 10 | 1 | 2 | 5 | 7 |
| wage_opportunity | 6 | 6 | 6 | 6 | 6 | 6 |
| occupation_opportunity | 12 | 12 | 9 | 9 | 9 | 10 |

## Convergence By Result Block

| group | success | message | iterations | n_function_evaluations | gradient_norm | log_likelihood | walltime_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| joint | 1 | SolveStatus.NormalCompletion (ModelStatus.OptimalLocal) | 14 | 14 | NA | -19084.3 | 273.48 |

## Solver Diagnostics

| field | value |
|---|---|
| solver_name | L-BFGS-B |
| objective_ll | -19084.3313 |
| wall_time_seconds | 820.4411 |
| joint.success | True |
| joint.message | SolveStatus.NormalCompletion (ModelStatus.OptimalLocal) |
| joint.n_iterations | 14.0000 |
| joint.n_function_evaluations | 14.0000 |
| joint.gradient_norm_results_json | None |

## CONOPT Technical Trace (appendix)

| field | value |
|---|---|
| iteration_rows_parsed | 4.0000 |
| final_iteration | 14.0000 |
| final_objective | -19084.3313 |
| final_rgmax (CONOPT reduced gradient) | 5.4000e-08 |
| final_ninf | None |
| final_nsb | 54.0000 |
| final_step | None |
| step_min | 1.0000 |
| step_median | 1.0000 |
| ok_T_count | 3.0000 |
| ok_F_count | 0.0000e+00 |
| ok_F_share | 0.0000e+00 |
| mx_T_count | 0.0000e+00 |
| mx_T_share | 0.0000e+00 |
| in_itr_max | 13.0000 |
| in_itr_mean | 10.0000 |

**Phase counts:**

| phase | iterations |
|---|---|
| 4 | 4.0000 |

## A. Core Likelihood and Sample Statistics

| metric | value |
|---|---|
| log_likelihood | -19084.3313 |
| n_observations | 1.2445e+06 |
| n_groups | 12445.0000 |
| n_alts_per_set | 100.0000 |
| n_free_parameters | 55.0000 |
| n_fixed_parameters | 0.0000e+00 |
| AIC | 38278.6626 |
| BIC | 38940.5461 |
| AIC_per_obs | 0.0308 |

## B. Null-Model and Pseudo-R² Diagnostics

| metric | value |
|---|---|
| ll_null_uniform | -46729.3207 |
| ll_null_prior_corrected | -37680.3446 |
| rho_squared_uniform | 0.5916 |
| rho_squared_prior_corrected | 0.4935 |
| rho_squared_adj_uniform | 0.5904 |
| rho_squared_adj_prior_corrected | 0.4921 |

> ρ² values use McFadden's formulation 1 - LL/LL0. For sampled-alternative / job-choice models the prior-corrected null is the right comparison; the uniform null is kept for legacy comparability.

## C. Bound and Fixed-Parameter Diagnostics

| metric | value |
|---|---|
| n_parameters | 55.0000 |
| n_free_parameters | 55.0000 |
| n_fixed_parameters | 0.0000e+00 |
| n_parameters_with_bounds | 55.0000 |
| n_at_lower_bound | 1.0000 |
| n_at_upper_bound | 0.0000e+00 |

**Parameters at or near bounds:**

| parameter | side | estimate | bound | distance |
|---|---|---|---|---|
| joint.beta_l0_m | lower | 1.0000e-06 | 1.0000e-06 | 0.0000e+00 |

## D. Economic Sanity Diagnostics

_These are not model-fit statistics; they check economic plausibility of estimated preferences._

_Not available: Marginal-utility diagnostics not computed (requires --mnl-base)._

## Parameter Estimates (by block — from DiagnosticsBundle)

_**Primary SE: cluster-robust.** Hessian SE shown as diagnostic/classical._

### Block: `preference` (23 params)

| parameter | estimate | se_hessian | t_hessian | se_robust | t_robust | p_robust | fixed | at_lower | at_upper | primary_se |
|---|---|---|---|---|---|---|---|---|---|---|
| joint.beta_l0_sm | 4.3281 | None | None | 0.7818 | 5.5360 | None | False | False | False | robust |
| joint.beta_l_age_sm | 0.0431 | None | None | 0.0228 | 1.8960 | None | False | False | False | robust |
| joint.beta_l_age2_sm | 0.0017 | None | None | 0.0021 | 0.8375 | None | False | False | False | robust |
| joint.beta_c_sm | 2.7331 | None | None | 0.2824 | 9.6778 | None | False | False | False | robust |
| joint.theta_l_sm | -0.7192 | None | None | 0.0614 | -11.7060 | None | False | False | False | robust |
| joint.beta_l0_sf | 4.4602 | None | None | 0.8774 | 5.0834 | None | False | False | False | robust |
| joint.beta_l_age_sf | 0.0385 | None | None | 0.0286 | 1.3477 | None | False | False | False | robust |
| joint.beta_l_age2_sf | 0.0046 | None | None | 0.0025 | 1.8186 | None | False | False | False | robust |
| joint.beta_l_nkids_sf | 0.3563 | None | None | 0.4164 | 0.8556 | None | False | False | False | robust |
| joint.beta_c_sf | 2.3513 | None | None | 0.3574 | 6.5791 | None | False | False | False | robust |
| joint.theta_l_sf | -0.7016 | None | None | 0.0580 | -12.0946 | None | False | False | False | robust |
| joint.theta_c_singles | 0.0392 | None | None | 0.0671 | 0.5850 | None | False | False | False | robust |
| joint.beta_l0_m | 1.0000e-06 | None | None | 0.0000e+00 | None | None | False | True | False | robust |
| joint.beta_l_age_m | 0.0059 | None | None | 0.0190 | 0.3092 | None | False | False | False | robust |
| joint.beta_l_age2_m | 0.0016 | None | None | 0.0012 | 1.3231 | None | False | False | False | robust |
| joint.theta_l_m | -0.6819 | None | None | 0.0377 | -18.0716 | None | False | False | False | robust |
| joint.beta_l0_f | 2.6053 | None | None | 0.7667 | 3.3982 | None | False | False | False | robust |
| joint.beta_l_age_f | -0.0580 | None | None | 0.0395 | -1.4701 | None | False | False | False | robust |
| joint.beta_l_age2_f | 0.0053 | None | None | 0.0038 | 1.3923 | None | False | False | False | robust |
| joint.beta_l_nkids_f | 0.1429 | None | None | 0.3643 | 0.3921 | None | False | False | False | robust |
| joint.theta_l_f | -0.6578 | None | None | 0.0314 | -20.9482 | None | False | False | False | robust |
| joint.beta_c | 4.3124 | None | None | 0.4553 | 9.4724 | None | False | False | False | robust |
| joint.beta_ll | 2.6559 | None | None | 0.3741 | 7.1004 | None | False | False | False | robust |

### Block: `employment_hours_opportunity` (13 params)

| parameter | estimate | se_hessian | t_hessian | se_robust | t_robust | p_robust | fixed | at_lower | at_upper | primary_se |
|---|---|---|---|---|---|---|---|---|---|---|
| joint.beta_h_pt1 | -0.4748 | None | None | 0.1325 | -3.5844 | None | False | False | False | robust |
| joint.beta_h_pt2 | 0.4248 | None | None | 0.1037 | 4.0959 | None | False | False | False | robust |
| joint.beta_h_ft | 1.4059 | None | None | 0.0854 | 16.4619 | None | False | False | False | robust |
| joint.beta_E_gsur | -1.1999 | None | None | 0.1911 | -6.2792 | None | False | False | False | robust |
| joint.beta_E_drgn2 | 0.3965 | None | None | 0.3845 | 1.0311 | None | False | False | False | robust |
| joint.beta_E_drgn3 | 0.3500 | None | None | 0.3991 | 0.8769 | None | False | False | False | robust |
| joint.beta_E_drgn4 | 0.6416 | None | None | 0.5537 | 1.1588 | None | False | False | False | robust |
| joint.beta_E_drgn5 | 0.4310 | None | None | 0.4427 | 0.9736 | None | False | False | False | robust |
| joint.beta_E_drgn6 | 0.3577 | None | None | 0.4682 | 0.7641 | None | False | False | False | robust |
| joint.beta_E_drgn7 | 0.3671 | None | None | 0.4370 | 0.8401 | None | False | False | False | robust |
| joint.beta_E_drgn8 | 0.1675 | None | None | 0.3370 | 0.4970 | None | False | False | False | robust |
| joint.beta_E_y2015 | -0.0591 | None | None | 0.2573 | -0.2297 | None | False | False | False | robust |
| joint.beta_E_y2017 | 0.1554 | None | None | 0.2701 | 0.5754 | None | False | False | False | robust |

### Block: `wage_opportunity` (6 params)

| parameter | estimate | se_hessian | t_hessian | se_robust | t_robust | p_robust | fixed | at_lower | at_upper | primary_se |
|---|---|---|---|---|---|---|---|---|---|---|
| joint.beta_w0 | 2.0333 | None | None | 0.0942 | 21.5804 | None | False | False | False | robust |
| joint.beta_w_educL | -0.0414 | None | None | 0.0742 | -0.5580 | None | False | False | False | robust |
| joint.beta_w_educH | 0.3067 | None | None | 0.0604 | 5.0751 | None | False | False | False | robust |
| joint.beta_w_pexp | 0.0173 | None | None | 0.0088 | 1.9771 | None | False | False | False | robust |
| joint.beta_w_pexp2 | -1.8196e-04 | None | None | 1.9399e-04 | -0.9380 | None | False | False | False | robust |
| joint.sigma | 0.4034 | None | None | 0.0015 | 261.1459 | None | False | False | False | robust |

### Block: `occupation_opportunity` (12 params)

| parameter | estimate | se_hessian | t_hessian | se_robust | t_robust | p_robust | fixed | at_lower | at_upper | primary_se |
|---|---|---|---|---|---|---|---|---|---|---|
| joint.beta_occ_2_sm | -1.4962 | None | None | 0.1108 | -13.5048 | None | False | False | False | robust |
| joint.beta_occ_3_sm | -2.1384 | None | None | 0.1544 | -13.8481 | None | False | False | False | robust |
| joint.beta_occ_4_sm | 0.0744 | None | None | 0.0572 | 1.3009 | None | False | False | False | robust |
| joint.beta_occ_2_sf | -0.1050 | None | None | 0.0826 | -1.2709 | None | False | False | False | robust |
| joint.beta_occ_3_sf | -0.5328 | None | None | 0.0897 | -5.9408 | None | False | False | False | robust |
| joint.beta_occ_4_sf | 0.7639 | None | None | 0.0728 | 10.4965 | None | False | False | False | robust |
| joint.beta_occ_2_cm | -1.5026 | None | None | 0.1577 | -9.5285 | None | False | False | False | robust |
| joint.beta_occ_3_cm | -2.2222 | None | None | 0.2135 | -10.4062 | None | False | False | False | robust |
| joint.beta_occ_4_cm | 0.4764 | None | None | 0.0864 | 5.5172 | None | False | False | False | robust |
| joint.beta_occ_2_cf | 0.1134 | None | None | 0.1386 | 0.8182 | None | False | False | False | robust |
| joint.beta_occ_3_cf | -0.3292 | None | None | 0.1562 | -2.1072 | None | False | False | False | robust |
| joint.beta_occ_4_cf | 1.0755 | None | None | 0.1116 | 9.6358 | None | False | False | False | robust |

### Block: `other` (1 params)

| parameter | estimate | se_hessian | t_hessian | se_robust | t_robust | p_robust | fixed | at_lower | at_upper | primary_se |
|---|---|---|---|---|---|---|---|---|---|---|
| joint.beta_E | -2.3977 | None | None | 0.2880 | -8.3257 | None | False | False | False | robust |

## Identification & Hessian Diagnostics (from DiagnosticsBundle)

| field | value |
|---|---|
| condition_number | 3.32e+09 |
| min_eigenvalue | -1.3846e+06 |
| max_eigenvalue | 3.7182e+10 |
| n_negative_eigenvalues | 5 ⚠ should be 0 at a local optimum |

**Top parameter correlations:**

| param_i | param_j | corr |
|---|---|---|
| beta_l0_sm | theta_l_sm | 4.9198 |
| beta_l0_sm | beta_l_age2_sm | -3.9048 |
| beta_l0_sm | beta_l_age_sm | -3.1968 |
| beta_l0_sm | sigma | -3.0328 |
| theta_l_m | beta_ll | 2.2843 |
| beta_l0_sm | beta_c_sm | 2.0070 |
| beta_l0_sm | theta_c_singles | -1.5899 |
| theta_c_singles | sigma | 1.2655 |
| beta_l0_sf | beta_l_age2_sf | -1.1164 |
| beta_c_sf | sigma | -1.0295 |
| beta_w_pexp | beta_w_pexp2 | -0.9619 |
| beta_l0_sf | beta_l_nkids_sf | -0.9354 |
| beta_c | sigma | -0.9235 |

## Probability & Fit Diagnostics (from DiagnosticsBundle)

**Probability-sum sanity check:**

| field | value |
|---|---|
| max_error | 1.0000 |
| mean_error | 0.4006 |
| pct_off_by_0.01 | 40.0616 |
| pct_off_by_0.001 | 40.0616 |

**P(chosen) distribution:**

| field | value |
|---|---|
| min | nan |
| max | nan |
| mean | nan |
| median | nan |
| q10 | nan |
| q25 | nan |
| q75 | nan |
| q90 | nan |

**Worst-fit households (top 10):**

| # | idhh | group | p_chosen | ll_i |
|---|---|---|---|---|
| 1.0000 | 500.0000 | sm | nan | nan |
| 2.0000 | 2000.0000 | sm | nan | nan |
| 3.0000 | 2200.0000 | sm | nan | nan |
| 4.0000 | 3800.0000 | sm | nan | nan |
| 5.0000 | 9500.0000 | sm | nan | nan |
| 6.0000 | 11300.0000 | sm | nan | nan |
| 7.0000 | 16100.0000 | sm | nan | nan |
| 8.0000 | 20100.0000 | sm | nan | nan |
| 9.0000 | 21100.0000 | sm | nan | nan |
| 10.0000 | 25300.0000 | sm | nan | nan |

## Fit Statistics (legacy combined table — kept for backward compatibility)

| metric | value |
| --- | --- |
| log_likelihood | -19084.3 |
| ll_null_uniform | -46729.3 |
| ll_null_prior_corrected | -37680.3 |
| rho_squared | 0.49352 |
| rho_squared_adj | 0.492061 |
| rho_squared_uniform | 0.591598 |
| rho_squared_prior_corrected | 0.49352 |
| AIC | 38278.7 |
| BIC | 38940.5 |
| AIC_per_obs | 0.0307583 |
| n_observations | 1244500 |
| n_groups | 12445 |
| n_parameters | 55 |
| n_obs_long | 1244500 |

## Fit Moments

| group | participation_observed | participation_predicted | mean_hours_observed | mean_hours_predicted |
| --- | --- | --- | --- | --- |
| cou_f | 0.961818 | 0.990362 | 35.56 | 38.706 |
| cou_m | 0.971767 | 0.987764 | 41.4826 | 42.5787 |
| sf | 0.930174 | 0 | 36.0599 | 0 |
| sm | 0.918859 | 0 | 39.3649 | 0 |

## Observed Hours Quantiles (chosen working alts)

| group | n | q10 | q25 | q50 | q75 | q90 |
| --- | --- | --- | --- | --- | --- | --- |
| singles_male | 2061 | 34 | 35 | 39 | 42 | 50 |
| singles_female | 2571 | 24 | 34 | 36 | 40 | 45 |
| couples_male | 7228 | 35 | 35 | 39 | 45 | 55 |
| couples_female | 7154 | 24 | 32 | 35 | 40 | 45 |

## Distribution Fit Summary (observed vs predicted hours bins)

| group | dimension | n_bins | L1_distance | L2_distance |
| --- | --- | --- | --- | --- |
| cou_f | hours_bins | 8 | 0.5226 | 0.2506 |
| cou_m | hours_bins | 8 | 0.3575 | 0.1775 |
| sf | hours_bins | 8 | 1.8603 | 1.0692 |
| sm | hours_bins | 8 | 1.8377 | 1.0707 |

## Observed vs Implied Log-Wage σ (chosen working alts)

| group | n | observed_mean_log_wage | observed_std_log_wage | implied_sigma |
| --- | --- | --- | --- | --- |
| singles_male | 2061 | 2.7096 | 0.4279 | 0.403406 |
| singles_female | 2571 | 2.6302 | 0.4225 | 0.403406 |
| couples_male | 7228 | 2.7744 | 0.4194 | 0.403406 |
| couples_female | 7154 | 2.612 | 0.4261 | 0.403406 |

## Structural Elasticity Heuristics

These are curvature-based heuristics from the post-estimation script, not
policy-counterfactual elasticities.

| Group | Hicksian (compensated) | Marshallian (uncompensated) | Participation (extensive) | Intensive (conditional) | theta_l | theta_c | beta_l (at median X) | beta_c |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single Males | 1.719 | 1.619 | 0.516 | 1.203 | -0.719 | 0.500 | 4.328 | 2.733 |
| Single Females | 1.702 | 1.602 | 0.510 | 1.191 | -0.702 | 0.500 | 4.460 | 2.351 |
| Males in Couples | 1.682 | 1.582 | 0.505 | 1.177 | -0.682 | 0.500 | 0.000 | 4.312 |
| Females in Couples | 1.658 | 1.558 | 0.497 | 1.160 | -0.658 | 0.500 | 2.605 | 4.312 |

## Marginal Utility Diagnostics

| Group | beta_c | theta_c | MUC Positive? | MUC Diminishing? | Well-Behaved? | MUC at Median C | C where MUC=1 | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single Males | 2.73315 | 0.5 | yes | yes | yes | 2.73315 | 7.47009 | NA |
| Single Females | 2.35133 | 0.5 | yes | yes | yes | 2.35133 | 5.52874 | NA |
| Males in Couples | 4.31241 | 0 | yes | yes | yes | 4.31241 | 4.31241 | NA |
| Females in Couples | 4.31241 | 0 | yes | yes | yes | 4.31241 | 4.31241 | NA |

## Marginal Utility Distribution Summary

| group | N | n_neg_muc | pct_neg_muc | mean_muc | n_neg_mul | pct_neg_mul | mean_mul |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cou_f | 7438 | 0 | 0 | 0.068128 | 0 | 0 | NA |
| cou_m | 7438 | 0 | 0 | 0.068128 | 0 | 0 | NA |
| sf | 2243 | 0 | 0 | 0.0586694 | 0 | 0 | 0.0107863 |
| sm | 2764 | 0 | 0 | 0.0639724 | 0 | 0 | 0.00786277 |
| total | NA | 0 | 0 | NA | 0 | 0 | NA |

## Probability Diagnostics

| metric | value |
| --- | --- |
| prob_sum_max_error | 1 |
| prob_sum_mean_error | 0.400616 |
| prob_sum_pct_off_by_0.01 | 40.0616 |
| prob_sum_pct_off_by_0.001 | 40.0616 |
| p_chosen_min | NA |
| p_chosen_max | NA |
| p_chosen_mean | NA |
| p_chosen_median | NA |
| p_chosen_q10 | NA |
| p_chosen_q25 | NA |
| p_chosen_q75 | NA |
| p_chosen_q90 | NA |

## Worst-Fit Households

| rank | idhh | group | p_chosen | ll_i |
| --- | --- | --- | --- | --- |
| 1 | 500 | sm | NA | NA |
| 2 | 2000 | sm | NA | NA |
| 3 | 2200 | sm | NA | NA |
| 4 | 3800 | sm | NA | NA |
| 5 | 9500 | sm | NA | NA |
| 6 | 11300 | sm | NA | NA |
| 7 | 16100 | sm | NA | NA |
| 8 | 20100 | sm | NA | NA |
| 9 | 21100 | sm | NA | NA |
| 10 | 25300 | sm | NA | NA |

## Identification Diagnostics

| metric | value |
| --- | --- |
| condition_number | 3.31629e+09 |
| min_eigenvalue | -1.38465e+06 |
| max_eigenvalue | 3.71819e+10 |
| n_negative_eigenvalues | 5 |

_Interpretation: weakly conditioned (1e6 <= kappa < 1e10); 5 negative eigenvalue(s) - not at a local maximum or numerically singular._

## Initial → Final Movement (top 15 by |Δ|)

| block | parameter | initial_value | final_estimate | delta |
| --- | --- | --- | --- | --- |
| preference | joint.beta_c_sm | 0.553672 | 2.73315 | 2.17947 |
| preference | joint.beta_c_sf | 0.505586 | 2.35133 | 1.84574 |
| preference | joint.theta_c_singles | -1.04848 | 0.0392437 | 1.08773 |
| market_residual_opportunity | joint.beta_E_drgn4 | 1.56255 | 0.641609 | -0.920942 |
| preference | joint.beta_l0_sm | 3.83617 | 4.32809 | 0.491916 |
| preference | joint.beta_l_nkids_sf | -0.0824215 | 0.356277 | 0.438698 |
| market_residual_opportunity | joint.beta_E_drgn6 | 0.766517 | 0.357738 | -0.408779 |
| market_residual_opportunity | joint.beta_E_drgn2 | 0.801342 | 0.396497 | -0.404845 |
| market_residual_opportunity | joint.beta_E_drgn5 | 0.772496 | 0.431035 | -0.341461 |
| preference | joint.beta_c | 4.00003 | 4.31241 | 0.312381 |
| market_residual_opportunity | joint.beta_E_drgn3 | 0.656401 | 0.35 | -0.306401 |
| market_residual_opportunity | joint.beta_E_drgn8 | 0.463141 | 0.167527 | -0.295615 |
| market_residual_opportunity | joint.beta_E_drgn7 | 0.640451 | 0.367068 | -0.273383 |
| occupation_opportunity | joint.beta_occ_2_sf | 0.0510192 | -0.104983 | -0.156002 |
| market_residual_opportunity | joint.beta_E_y2017 | 0 | 0.15543 | 0.15543 |

## Top High-Correlation Parameter Pairs

| param_i | param_j | correlation |
| --- | --- | --- |
| beta_l0_sm | theta_l_sm | 4.91979 |
| beta_l0_sm | beta_l_age2_sm | -3.9048 |
| beta_l0_sm | beta_l_age_sm | -3.19682 |
| beta_l0_sm | sigma | -3.03278 |
| theta_l_m | beta_ll | 2.28428 |
| beta_l0_sm | beta_c_sm | 2.00702 |
| beta_l0_sm | theta_c_singles | -1.58992 |
| theta_c_singles | sigma | 1.26547 |
| beta_l0_sf | beta_l_age2_sf | -1.11636 |
| beta_c_sf | sigma | -1.0295 |

## Weakest Eigenvector Diagnostics

_None._

## Parameters At Bounds

| parameter | estimate | bound | side |
| --- | --- | --- | --- |
| joint.beta_l0_m | 1e-06 | 1e-06 | lower |

## Parameters Near Bounds (within 5% of bound width)

| block | parameter | estimate | lower_bound | upper_bound | flags |
| --- | --- | --- | --- | --- | --- |
| preference | joint.beta_c_sf | 2.35133 | 0.05 | 50 | near_lower(delta=2.3) |
| wage_opportunity | joint.sigma | 0.403406 | 0.1 | 20 | near_lower(delta=0.303) |

## Top Significant Coefficients (top 15 by |t|)

| block | parameter | estimate | std_error | t_value | p_value |
| --- | --- | --- | --- | --- | --- |
| wage_opportunity | joint.sigma | 0.403406 | 0.000220677 | 1828.04 | 0 |
| wage_opportunity | joint.beta_w0 | 2.03334 | 0.0127911 | 158.966 | 0 |
| preference | joint.beta_c | 4.31241 | 0.0577204 | 74.7121 | 0 |
| preference | joint.beta_ll | 2.65594 | 0.049107 | 54.0848 | 0 |
| employment_hours_opportunity | joint.beta_h_ft | 1.40592 | 0.0300106 | 46.8476 | 0 |
| preference | joint.beta_c_sm | 2.73315 | 0.0663963 | 41.1642 | 0 |
| preference | joint.beta_c_sf | 2.35133 | 0.0657251 | 35.7752 | 0 |
| wage_opportunity | joint.beta_w_educH | 0.306669 | 0.00869016 | 35.2892 | 0 |
| occupation_opportunity | joint.beta_occ_3_cm | -2.22222 | 0.0900099 | -24.6886 | 0 |
| occupation_opportunity | joint.beta_occ_4_cf | 1.07548 | 0.0492391 | 21.8419 | 0 |
| occupation_opportunity | joint.beta_occ_2_cm | -1.50261 | 0.069743 | -21.545 | 0 |
| occupation_opportunity | joint.beta_occ_3_sm | -2.13838 | 0.108443 | -19.719 | 0 |
| preference | joint.beta_l0_sf | 4.46019 | 0.232333 | 19.1975 | 0 |
| employment_hours_opportunity | joint.beta_E | -2.39772 | 0.128602 | -18.6445 | 0 |
| occupation_opportunity | joint.beta_occ_2_sm | -1.49616 | 0.0832292 | -17.9764 | 0 |

## Parameter Estimates By Block

| block | parameter | estimate | std_error | t_value | p_value | lower_bound | upper_bound | initial_value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| employment_hours_opportunity | joint.beta_E | -2.39772 | 0.128602 | -18.6445 | 0 | -25 | 25 | -2.49928 |
| employment_hours_opportunity | joint.beta_h_ft | 1.40592 | 0.0300106 | 46.8476 | 0 | -10 | 10 | 1.44968 |
| employment_hours_opportunity | joint.beta_h_pt1 | -0.474816 | 0.0633265 | -7.4979 | 6.4837e-14 | -10 | 10 | -0.502194 |
| employment_hours_opportunity | joint.beta_h_pt2 | 0.424756 | 0.0658871 | 6.44674 | 1.14284e-10 | -10 | 10 | 0.372247 |
| market_residual_opportunity | joint.beta_E_drgn2 | 0.396497 | 0.158898 | 2.49529 | 0.0125853 | -10 | 10 | 0.801342 |
| market_residual_opportunity | joint.beta_E_drgn3 | 0.35 | 0.196859 | 1.77792 | 0.0754168 | -10 | 10 | 0.656401 |
| market_residual_opportunity | joint.beta_E_drgn4 | 0.641609 | 0.219262 | 2.92623 | 0.00343098 | -10 | 10 | 1.56255 |
| market_residual_opportunity | joint.beta_E_drgn5 | 0.431035 | 0.171955 | 2.50668 | 0.0121871 | -10 | 10 | 0.772496 |
| market_residual_opportunity | joint.beta_E_drgn6 | 0.357738 | 0.192742 | 1.85604 | 0.0634479 | -10 | 10 | 0.766517 |
| market_residual_opportunity | joint.beta_E_drgn7 | 0.367068 | 0.184294 | 1.99176 | 0.0463977 | -10 | 10 | 0.640451 |
| market_residual_opportunity | joint.beta_E_drgn8 | 0.167527 | 0.170297 | 0.983735 | 0.325246 | -10 | 10 | 0.463141 |
| market_residual_opportunity | joint.beta_E_gsur | -1.19992 | 0.0964877 | -12.436 | 0 | -10 | 10 | -1.32895 |
| market_residual_opportunity | joint.beta_E_y2015 | -0.0590898 | 0.119274 | -0.495412 | 0.62031 | -5 | 5 | 0 |
| market_residual_opportunity | joint.beta_E_y2017 | 0.15543 | 0.126932 | 1.22451 | 0.220759 | -5 | 5 | 0 |
| occupation_opportunity | joint.beta_occ_2_cf | 0.113438 | 0.0613783 | 1.84818 | 0.0645767 | -10 | 10 | 0.131868 |
| occupation_opportunity | joint.beta_occ_2_cm | -1.50261 | 0.069743 | -21.545 | 0 | -10 | 10 | -1.49556 |
| occupation_opportunity | joint.beta_occ_2_sf | -0.104983 | 0.0655137 | -1.60246 | 0.109054 | -10 | 10 | 0.0510192 |
| occupation_opportunity | joint.beta_occ_2_sm | -1.49616 | 0.0832292 | -17.9764 | 0 | -10 | 10 | -1.47443 |
| occupation_opportunity | joint.beta_occ_3_cf | -0.329211 | 0.0679603 | -4.84416 | 1.2715e-06 | -10 | 10 | -0.24905 |
| occupation_opportunity | joint.beta_occ_3_cm | -2.22222 | 0.0900099 | -24.6886 | 0 | -10 | 10 | -2.25133 |
| occupation_opportunity | joint.beta_occ_3_sf | -0.532782 | 0.073541 | -7.24469 | 4.33431e-13 | -10 | 10 | -0.500047 |
| occupation_opportunity | joint.beta_occ_3_sm | -2.13838 | 0.108443 | -19.719 | 0 | -10 | 10 | -2.12919 |
| occupation_opportunity | joint.beta_occ_4_cf | 1.07548 | 0.0492391 | 21.8419 | 0 | -10 | 10 | 1.08585 |
| occupation_opportunity | joint.beta_occ_4_cm | 0.476417 | 0.0417006 | 11.4247 | 0 | -10 | 10 | 0.459406 |
| occupation_opportunity | joint.beta_occ_4_sf | 0.763932 | 0.0528484 | 14.4551 | 0 | -10 | 10 | 0.859079 |
| occupation_opportunity | joint.beta_occ_4_sm | 0.0743814 | 0.050617 | 1.4695 | 0.141699 | -10 | 10 | 0.0604191 |
| preference | joint.beta_c | 4.31241 | 0.0577204 | 74.7121 | 0 | 0.05 | 50 | 4.00003 |
| preference | joint.beta_c_sf | 2.35133 | 0.0657251 | 35.7752 | 0 | 0.05 | 50 | 0.505586 |
| preference | joint.beta_c_sm | 2.73315 | 0.0663963 | 41.1642 | 0 | 0.05 | 50 | 0.553672 |
| preference | joint.beta_l0_f | 2.60529 | 0.26762 | 9.735 | 0 | 0.05 | 50 | 2.59235 |
| preference | joint.beta_l0_m | 1e-06 | NA | NA | NA | 1e-06 | 50 | 0.0120803 |
| preference | joint.beta_l0_sf | 4.46019 | 0.232333 | 19.1975 | 0 | 0.05 | 50 | 4.46954 |
| preference | joint.beta_l0_sm | 4.32809 | NA | NA | NA | 0.05 | 50 | 3.83617 |
| preference | joint.beta_l_age2_f | 0.0052876 | 0.00133796 | 3.95198 | 7.75056e-05 | -1 | 1 | 0.00300942 |
| preference | joint.beta_l_age2_m | 0.00164643 | 0.000715202 | 2.30204 | 0.0213327 | -1 | 1 | 0.00092724 |
| preference | joint.beta_l_age2_sf | 0.00460958 | 0.00121779 | 3.78521 | 0.00015358 | -1 | 1 | 0.00393105 |
| preference | joint.beta_l_age2_sm | 0.0017236 | 0.00116738 | 1.47647 | 0.139817 | -1 | 1 | 0.00175459 |
| preference | joint.beta_l_age_f | -0.0580316 | 0.0128508 | -4.51578 | 6.30832e-06 | -5 | 5 | -0.0593808 |
| preference | joint.beta_l_age_m | 0.00587034 | 0.00903579 | 0.649676 | 0.515901 | -5 | 5 | -0.0103361 |
| preference | joint.beta_l_age_sf | 0.0385062 | 0.0141602 | 2.71933 | 0.00654152 | -5 | 5 | 0.000335343 |
| preference | joint.beta_l_age_sm | 0.0431437 | 0.0126629 | 3.40709 | 0.000656605 | -5 | 5 | 0.00405169 |
| preference | joint.beta_l_nkids_f | 0.142852 | 0.129419 | 1.10379 | 0.269685 | -5 | 5 | 0.169459 |
| preference | joint.beta_l_nkids_sf | 0.356277 | 0.182103 | 1.95646 | 0.0504115 | -5 | 5 | -0.0824215 |
| preference | joint.beta_ll | 2.65594 | 0.049107 | 54.0848 | 0 | 0 | 10 | 2.61746 |
| preference | joint.theta_c_singles | 0.0392437 | 0.0145739 | 2.69275 | 0.00708661 | -8 | 0.95 | -1.04848 |
| preference | joint.theta_l_f | -0.657847 | NA | NA | NA | -8 | 0.95 | -0.67813 |
| preference | joint.theta_l_m | -0.681907 | NA | NA | NA | -8 | 0.95 | -0.7314 |
| preference | joint.theta_l_sf | -0.701604 | NA | NA | NA | -8 | 0.95 | -0.722669 |
| preference | joint.theta_l_sm | -0.719206 | NA | NA | NA | -8 | 0.95 | -0.71247 |
| wage_opportunity | joint.beta_w0 | 2.03334 | 0.0127911 | 158.966 | 0 | -10 | 20 | 2.01625 |
| wage_opportunity | joint.beta_w_educH | 0.306669 | 0.00869016 | 35.2892 | 0 | -5 | 5 | 0.32399 |
| wage_opportunity | joint.beta_w_educL | -0.0414001 | 0.0114288 | -3.62244 | 0.000291833 | -5 | 5 | -0.0405631 |
| wage_opportunity | joint.beta_w_pexp | 0.0173056 | 0.00132262 | 13.0844 | 0 | -1 | 1 | 0.0184615 |
| wage_opportunity | joint.beta_w_pexp2 | -0.000181961 | 2.97916e-05 | -6.10782 | 1.01003e-09 | -0.1 | 0.1 | -0.000226179 |
| wage_opportunity | joint.sigma | 0.403406 | 0.000220677 | 1828.04 | 0 | 0.1 | 20 | 0.427474 |

## Hours Distribution Shares

| group | hours_bin | observed_share | predicted_share |
| --- | --- | --- | --- |
| cou_f | 0 | 0.0381823 | 0.000513875 |
| cou_f | 1-10 | 0.0232589 | 0.00479616 |
| cou_f | 11-20 | 0.093708 | 0.04642 |
| cou_f | 21-30 | 0.393385 | 0.23878 |
| cou_f | 31-40 | 0.375773 | 0.539911 |
| cou_f | 41-50 | 0.0512234 | 0.140116 |
| cou_f | 51-60 | 0.0196289 | 0.0279205 |
| cou_f | 60+ | 0.00484001 | 0.00154162 |
| cou_m | 0 | 0.0282334 | 0.000171292 |
| cou_m | 1-10 | 0.00564668 | 0.00342583 |
| cou_m | 11-20 | 0.0188223 | 0.0190134 |
| cou_m | 21-30 | 0.257327 | 0.127955 |
| cou_m | 31-40 | 0.47943 | 0.543851 |
| cou_m | 41-50 | 0.129336 | 0.224734 |
| cou_m | 51-60 | 0.0545846 | 0.0733128 |
| cou_m | 60+ | 0.0266201 | 0.00753683 |
| sf | 0 | 0.0698263 | 1 |
| sf | 1-10 | 0.0307525 | 0 |
| sf | 11-20 | 0.0893632 | 0 |
| sf | 21-30 | 0.333936 | 0 |
| sf | 31-40 | 0.392547 | 0 |
| sf | 41-50 | 0.0539074 | 0 |
| sf | 51-60 | 0.0213459 | 0 |
| sf | 60+ | 0.00832127 | 0 |
| sm | 0 | 0.0811413 | 1 |
| sm | 1-10 | 0.0084708 | 0 |
| sm | 11-20 | 0.0445831 | 0 |
| sm | 21-30 | 0.263041 | 0 |
| sm | 31-40 | 0.472136 | 0 |
| sm | 41-50 | 0.0784663 | 0 |
| sm | 51-60 | 0.0401248 | 0 |
| sm | 60+ | 0.0120374 | 0 |

## Wage Distribution Summary

Observed values use chosen working alternatives. Predicted values use
choice-probability weights over working alternatives.

| group | n_observed_working | predicted_worker_weight | obs_mean | pred_mean | obs_q10 | obs_q50 | obs_q90 | pred_q10 | pred_q50 | pred_q90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | 2061 | 0 | 16.4824 | NA | 9.52404 | 14.6356 | 25.2404 | NA | NA | NA |
| singles_female | 2571 | 0 | 15.1901 | NA | 9.10714 | 13.8132 | 23.0098 | NA | NA | NA |
| couples_male | 7228 | 5766.56 | 17.5728 | 16.8218 | 10.2908 | 15.478 | 27.01 | 9.27955 | 15.0812 | 26.3761 |
| couples_female | 7154 | 5781.73 | 14.9221 | 15.476 | 8.95039 | 13.751 | 21.8646 | 8.58968 | 13.793 | 24.5096 |

## Occupation Distribution Shares

Observed shares use chosen working alternatives. Predicted shares use
choice-probability weights over working alternatives. Category labels
are reported for loc4-style variables when available.

| group | occupation_column | category | label | observed_share | predicted_share | observed_count | predicted_weight |
| --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | loc4 | -2 | unknown_observed_working | 0.00630762 | NA | 13 | 0 |
| singles_male | loc4 | 1 | routine_manual_ref | 0.406599 | NA | 838 | 0 |
| singles_male | loc4 | 2 | nonroutine_manual | 0.0946143 | NA | 195 | 0 |
| singles_male | loc4 | 3 | routine_cognitive | 0.0504609 | NA | 104 | 0 |
| singles_male | loc4 | 4 | nonroutine_cognitive | 0.442018 | NA | 911 | 0 |
| singles_female | loc4 | -2 | unknown_observed_working | 0.00311163 | NA | 8 | 0 |
| singles_female | loc4 | 1 | routine_manual_ref | 0.205757 | NA | 529 | 0 |
| singles_female | loc4 | 2 | nonroutine_manual | 0.190198 | NA | 489 | 0 |
| singles_female | loc4 | 3 | routine_cognitive | 0.133022 | NA | 342 | 0 |
| singles_female | loc4 | 4 | nonroutine_cognitive | 0.467911 | NA | 1203 | 0 |
| couples_male | loc4_male | -2 | unknown_observed_working | 0.013005 | 0.00731306 | 94 | 42.1712 |
| couples_male | loc4_male | 1 | routine_manual_ref | 0.363309 | 0.362971 | 2626 | 2093.1 |
| couples_male | loc4_male | 2 | nonroutine_manual | 0.0774765 | 0.0793401 | 560 | 457.52 |
| couples_male | loc4_male | 3 | routine_cognitive | 0.03943 | 0.0399135 | 285 | 230.164 |
| couples_male | loc4_male | 4 | nonroutine_cognitive | 0.506779 | 0.510462 | 3663 | 2943.61 |
| couples_female | loc4_female | -1 | nonwork | 0.000139782 | 8.1068e-05 | 1 | 0.468713 |
| couples_female | loc4_female | -2 | unknown_observed_working | 0.00167738 | 0.00106798 | 12 | 6.17478 |
| couples_female | loc4_female | 1 | routine_manual_ref | 0.171373 | 0.174777 | 1226 | 1010.51 |
| couples_female | loc4_female | 2 | nonroutine_manual | 0.204221 | 0.203703 | 1461 | 1177.75 |
| couples_female | loc4_female | 3 | routine_cognitive | 0.149427 | 0.144306 | 1069 | 834.342 |
| couples_female | loc4_female | 4 | nonroutine_cognitive | 0.473162 | 0.476065 | 3385 | 2752.48 |

## Notes For Use

- This Markdown file is the preferred low-token artifact for LLM review.
- Use the HTML report only when plots or visual diagnostics are needed.
- Generated output folders remain local unless explicitly added to Git.
