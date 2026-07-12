# RURO Low-Token Post-Estimation Summary

Generated: 2026-07-12T12:39:08

## Purpose

Compact text-only report for Git, paper drafting, and LLM review.
Figures and large HTML output are intentionally omitted.

## Sources

| item | path_or_value |
| --- | --- |
| estimation_results_json | outputs\trial_singles2016\estimation_results_trial_singles2016.json |
| html_report | outputs\trial_singles2016\trial_singles2016_post_estimation_report_20260712_123905.html |
| post_output_dir | outputs\trial_singles2016 |
| params_csv | outputs\trial_singles2016\trial_singles2016_params.csv |
| elasticities_csv | outputs\trial_singles2016\trial_singles2016_elasticities.csv |
| mnl_base | outputs\trial_singles2016\fr_trial_singles2016 |
| spec_config | scripts\bpool\specs\estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml |

## Run Metadata

| field | value |
| --- | --- |
| specification | joint_pooled_v1_bll0_tlmpin |
| model_family | regular |
| market_opportunity_tier | NA |
| prior_correction_applied | NA |
| prior_correction_form | NA |
| market_centering_applied | 1 |
| wage_spec | vw |
| estimation_walltime_seconds | NA |

## Source Environment

| field | value |
| --- | --- |
| git_sha | 0e31d4974682 |
| git_branch | main |
| git_dirty | 1 |

## Choice Data Footprint

| dataset | rows | groups | alt_min | alt_median | alt_max | chosen_rows | working_rows | n_columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| singles | 155500 | 1555 | 100 | 100 | 100 | 1555 | 134642 | 199 |

## Per-Group Sample Sizes

| group | n_obs | n_households | alts_per_hh | n_chosen | n_working |
| --- | --- | --- | --- | --- | --- |
| singles_male | 71400 | 714 | 100 | 714 | 61486 |
| singles_female | 84100 | 841 | 100 | 841 | 73156 |

## Sample Descriptives (chosen alternatives, by group)

| group | variable | mean | std | min | max | n |
| --- | --- | --- | --- | --- | --- | --- |
| singles_male | age_norm | -0.0484 | 1.0731 | -2.2723 | 1.7277 | 714 |
| singles_male | age_norm2 | 1.1522 | 1.1766 | 0.0008 | 5.1636 | 714 |
| singles_male | educL | 0.1667 | 0.3729 | 0 | 1 | 714 |
| singles_male | educM | 0.458 | 0.4986 | 0 | 1 | 714 |
| singles_male | educH | 0.3754 | 0.4846 | 0 | 1 | 714 |
| singles_male | pexp_years | 1.0174 | 0.5726 | 0 | 2.2 | 714 |
| singles_male | n_children | 0.2031 | 0.5892 | 0 | 4 | 714 |
| singles_male | gsur | 0.098 | 0.04 | 0.0595 | 0.225 | 714 |
| singles_female | age_norm | 0.0411 | 1.0214 | -2.2723 | 1.7277 | 841 |
| singles_female | age_norm2 | 1.0437 | 1.098 | 0.0008 | 5.1636 | 841 |
| singles_female | educL | 0.1344 | 0.3412 | 0 | 1 | 841 |
| singles_female | educM | 0.434 | 0.4959 | 0 | 1 | 841 |
| singles_female | educH | 0.4316 | 0.4956 | 0 | 1 | 841 |
| singles_female | pexp_years | 0.9756 | 0.5285 | 0.0125 | 2.15 | 841 |
| singles_female | n_children | 0.6373 | 0.9066 | 0 | 5 | 841 |
| singles_female | gsur | 0.0915 | 0.0345 | 0.0532 | 0.183 | 841 |

## Proposal And Prior Diagnostics

| dataset | min_prior | max_abs_log_prior_minus_log_density | max_abs_prior_alias_reconstruction | missing_aliases | forbidden_columns_present |
| --- | --- | --- | --- | --- | --- |
| singles | 7.88777e-05 | 0 | 0 | none | lindi, log_q_total |

## Warnings And Review Flags

| type | message |
| --- | --- |
| probability | minimum chosen probability is very small (5.655e-09) |
| proposal | singles: forbidden diagnostic columns present: lindi, log_q_total |

## Convergence Health Summary

| metric | value |
| --- | --- |
| n_estimated_params | 47 |
| log_likelihood | -4106.6 |
| AIC | 8307.21 |
| BIC | 8558.62 |
| rho_squared | 0.515338 |
| n_significant_p<0.05 | 0 |
| pct_significant_p<0.05 | 0.0% |
| n_low_t<1.0 | 0 |
| pct_low_t<1.0 | 0.0% |
| n_degenerate_se | 0 |
| n_at_bound_strict | 0 |
| hessian_condition_number | NA |
| n_negative_eigenvalues | 0 |
| p_chosen_min | 5.65531e-09 |
| p_chosen_q10 | 0.00741596 |
| review_priority_flags | very_small_p_chosen_min |

## Model Index Equation

V_ij = U_ij + O^E_ij + O^H_ij + O^W_ij + O^Occ_ij - log_prior_ij

P_ij = exp(V_ij) / sum_k exp(V_ik)

## Utility / Preference Parameters By Group

Utility uses Box-Cox consumption and leisure. This table gives the
group-level consumption and leisure parameters resolved from the
estimated parameter vector.

| group | beta_c | theta_c | beta_l0 | beta_l_shifters | theta_l | beta_cl |
| --- | --- | --- | --- | --- | --- | --- |
| f | NA | NA | 10.0522 | beta_l_age=-1.78025; beta_l_age2=1; beta_l_nkids=0.58572 | -2.13174 | NA |
| m | NA | NA | 1e-06 | beta_l_age=-0.0672369; beta_l_age2=0.0877505 | NA | NA |
| sf | NA | NA | 8.13454 | beta_l_age=-0.92701; beta_l_age2=1; beta_l_nkids=1.40262 | -2.1128 | NA |
| sm | NA | NA | 4.79827 | beta_l_age=0.370015; beta_l_age2=1 | -2.3943 | NA |

## Specification Block Inventory

| yaml_block | label | n_shifters | variables | coefficients |
| --- | --- | --- | --- | --- |
| utility.consumption.coefficient | consumption scale | 1 | - | beta_c |
| utility.consumption.box_cox_exponent | consumption theta_c | 1 | - | theta_c |
| utility.leisure.intercept | leisure intercept | 1 | - | beta_l0 |
| utility.leisure.box_cox_exponent | leisure theta_l | 1 | - | theta_l |
| utility.leisure.shifters | Utility-leisure shifters | 3 | age_norm, age_norm2, n_children | beta_l_age, beta_l_age2, beta_l_nkids |
| hours_opportunity | Employment/Hours | 5 | working, working_ft, working_lh, working_pt1, working_pt2 | beta_E, beta_h_pt1, beta_h_pt2, beta_h_ft, beta_h_lh |
| market_opportunity | Market residual | 12 | drgmd, drgur, gsur, reg2, reg3, reg4, reg5, reg6, reg7, reg8, year_2015_indicator, year_2017_indicator | beta_E_gsur, beta_E_drgn2, beta_E_drgn3, beta_E_drgn4, beta_E_drgn5, beta_E_drgn6, beta_E_drgn7, beta_E_drgn8, beta_E_y2015, beta_E_y2017, beta_E_drgur, beta_E_drgmd |
| wage_opportunity.mean_shifters | Mincer mean | 5 | educH, educL, intercept, pexp_years, pexp_years2 | beta_w0, beta_w_educL, beta_w_educH, beta_w_pexp, beta_w_pexp2 |
| wage_opportunity.variance | Mincer sigma | 1 | - | sigma |
| occupation_opportunity | Occupation | 6 | loc4_2, loc4_3, loc4_4 | beta_occ_2_m, beta_occ_3_m, beta_occ_4_m, beta_occ_2_f, beta_occ_3_f, beta_occ_4_f |

## Opportunity Equations — Symbolic

```text
O^E + O^H =
+ beta_E * working
+ beta_h_pt1 * working_pt1
+ beta_h_pt2 * working_pt2
+ beta_h_ft * working_ft
+ beta_h_lh * working_lh
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
+ beta_E_drgur * drgur * working
+ beta_E_drgmd * drgmd * working

mu_w =
+ beta_w0
+ beta_w_educL * educL
+ beta_w_educH * educH
+ beta_w_pexp * pexp_years
+ beta_w_pexp2 * pexp_years2
log(wage) = mu_w + eps,  eps ~ N(0, sigma^2)

O^Occ (reference loc4=1):
applies_to=male:
+ beta_occ_2_m * loc4_2 * working
+ beta_occ_3_m * loc4_3 * working
+ beta_occ_4_m * loc4_4 * working
applies_to=female:
+ beta_occ_2_f * loc4_2 * working
+ beta_occ_3_f * loc4_3 * working
+ beta_occ_4_f * loc4_4 * working
```

## Opportunity Equations — Numerical (estimated coefficients bound)

| block | term | coefficient | source_group | value |
| --- | --- | --- | --- | --- |
| employment_hours | beta_E * working | beta_E | joint | -1.72836 |
| employment_hours | beta_h_pt1 * working_pt1 | beta_h_pt1 | joint | -0.163635 |
| employment_hours | beta_h_pt2 * working_pt2 | beta_h_pt2 | joint | 0.18044 |
| employment_hours | beta_h_ft * working_ft | beta_h_ft | joint | 1.35889 |
| employment_hours | beta_h_lh * working_lh | beta_h_lh | joint | -0.898749 |
| employment_hours | beta_E_gsur * gsur * working | beta_E_gsur | joint | -1.04902 |
| employment_hours | beta_E_drgn2 * reg2 * working | beta_E_drgn2 | joint | -0.322619 |
| employment_hours | beta_E_drgn3 * reg3 * working | beta_E_drgn3 | joint | -0.196977 |
| employment_hours | beta_E_drgn4 * reg4 * working | beta_E_drgn4 | joint | -0.833315 |
| employment_hours | beta_E_drgn5 * reg5 * working | beta_E_drgn5 | joint | -0.406423 |
| employment_hours | beta_E_drgn6 * reg6 * working | beta_E_drgn6 | joint | -0.584852 |
| employment_hours | beta_E_drgn7 * reg7 * working | beta_E_drgn7 | joint | -0.415387 |
| employment_hours | beta_E_drgn8 * reg8 * working | beta_E_drgn8 | joint | -0.441965 |
| employment_hours | beta_E_y2015 * year_2015_indicator * working | beta_E_y2015 | joint | -0.254606 |
| employment_hours | beta_E_y2017 * year_2017_indicator * working | beta_E_y2017 | joint | -0.0694711 |
| employment_hours | beta_E_drgur * drgur * working | beta_E_drgur | joint | 0.0034228 |
| employment_hours | beta_E_drgmd * drgmd * working | beta_E_drgmd | joint | 0.0358074 |
| wage_mean | beta_w0 * intercept | beta_w0 | joint | 2.13676 |
| wage_mean | beta_w_educL * educL | beta_w_educL | joint | 0.0182873 |
| wage_mean | beta_w_educH * educH | beta_w_educH | joint | 0.323746 |
| wage_mean | beta_w_pexp * pexp_years | beta_w_pexp | joint | 0.227847 |
| wage_mean | beta_w_pexp2 * pexp_years2 | beta_w_pexp2 | joint | -0.0117863 |
| wage_sigma | sigma | sigma | joint | 0.419664 |
| occupation:male | beta_occ_2_m * loc4_2 * working | beta_occ_2_m | joint | -1.59165 |
| occupation:male | beta_occ_3_m * loc4_3 * working | beta_occ_3_m | joint | -2.2941 |
| occupation:male | beta_occ_4_m * loc4_4 * working | beta_occ_4_m | joint | 0.290643 |
| occupation:female | beta_occ_2_f * loc4_2 * working | beta_occ_2_f | joint | -0.0475805 |
| occupation:female | beta_occ_3_f * loc4_3 * working | beta_occ_3_f | joint | -0.472919 |
| occupation:female | beta_occ_4_f * loc4_4 * working | beta_occ_4_f | joint | 0.771794 |

## Per-Block Parameter Counts and Significance

| block | n_params | n_estimable | n_sig_p<0.001 | n_sig_p<0.01 | n_sig_p<0.05 | n_sig_p<0.10 |
| --- | --- | --- | --- | --- | --- | --- |
| preference | 18 | 18 | 0 | 0 | 0 | 0 |
| employment_hours_opportunity | 5 | 5 | 0 | 0 | 0 | 0 |
| market_residual_opportunity | 12 | 12 | 0 | 0 | 0 | 0 |
| wage_opportunity | 6 | 6 | 0 | 0 | 0 | 0 |
| occupation_opportunity | 6 | 6 | 0 | 0 | 0 | 0 |

## Convergence By Result Block

| group | success | message | iterations | n_function_evaluations | gradient_norm | log_likelihood | walltime_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| joint | 1 | notebook trial fit (singles-only; occ+couples+year pinned); source=theta_trial_singles_2016_v3_final.csv | NA | NA | NA | -4106.6 | NA |

## Solver Diagnostics

| field | value |
|---|---|
| solver_name | notebook trial (warm->fit) |
| objective_ll | -4106.6042 |
| wall_time_seconds | None |
| solver_family | other |
| not_applicable_fields | ['rgmax', 'model_status', 'equations', 'variables', 'nonzeros', 'max_infeasibility', 'generation_time_s', 'solve_time_s', 'conopt_trace'] |
| joint.success | True |
| joint.n_iterations | None |
| joint.n_function_evaluations | None |

## CONOPT Technical Trace (appendix)

## A. Core Likelihood and Sample Statistics

| metric | value |
|---|---|
| log_likelihood | -4106.6042 |
| n_observations | 1555.0000 |
| n_groups | 1555.0000 |
| n_alts_per_set | 1.0000 |
| n_free_parameters | 47.0000 |
| n_fixed_parameters | 0.0000e+00 |
| AIC | 8307.2084 |
| BIC | 8558.6223 |
| AIC_per_obs | 5.3423 |

## B. Null-Model and Pseudo-R² Diagnostics

| metric | value |
|---|---|
| ll_null_uniform | -7161.0396 |
| ll_null_prior_corrected | -8473.1288 |
| rho_squared_uniform | 0.4265 |
| rho_squared_prior_corrected | 0.5153 |
| rho_squared_adj_uniform | 0.4200 |
| rho_squared_adj_prior_corrected | 0.5098 |

> ρ² values use McFadden's formulation 1 - LL/LL0. For sampled-alternative / job-choice models the prior-corrected null is the right comparison; the uniform null is kept for legacy comparability.

## C. Bound and Fixed-Parameter Diagnostics

| metric | value |
|---|---|
| n_parameters | 47.0000 |
| n_free_parameters | 47.0000 |
| n_fixed_parameters | 0.0000e+00 |
| n_parameters_with_bounds | 0.0000e+00 |
| n_at_lower_bound | 0.0000e+00 |
| n_at_upper_bound | 0.0000e+00 |

## D. Economic Sanity Diagnostics

_These are not model-fit statistics; they check economic plausibility of estimated preferences._

| metric | value |
|---|---|
| negative_muc_count | 0.0000e+00 |
| negative_muc_pct | 0.0000e+00 |
| negative_mul_count | 0.0000e+00 |
| negative_mul_pct | 0.0000e+00 |

## Parameter Estimates (by block — from DiagnosticsBundle)

_**Primary SE: Hessian (classical).** Supply `--cluster-se-json` for cluster-robust SE._

### Block: `preference` (18 params)

| parameter | estimate | se_hessian | t_hessian | se_robust | t_robust | p_robust | fixed | at_lower | at_upper | primary_se |
|---|---|---|---|---|---|---|---|---|---|---|
| joint.beta_l0_sm | 4.7983 | None | None | None | None | None | False | False | False | none |
| joint.beta_l_age_sm | 0.3700 | None | None | None | None | None | False | False | False | none |
| joint.beta_l_age2_sm | 1.0000 | None | None | None | None | None | False | False | False | none |
| joint.theta_l_sm | -2.3943 | None | None | None | None | None | False | False | False | none |
| joint.beta_l0_sf | 8.1345 | None | None | None | None | None | False | False | False | none |
| joint.beta_l_age_sf | -0.9270 | None | None | None | None | None | False | False | False | none |
| joint.beta_l_age2_sf | 1.0000 | None | None | None | None | None | False | False | False | none |
| joint.beta_l_nkids_sf | 1.4026 | None | None | None | None | None | False | False | False | none |
| joint.theta_l_sf | -2.1128 | None | None | None | None | None | False | False | False | none |
| joint.theta_c_singles | -0.0771 | None | None | None | None | None | False | False | False | none |
| joint.beta_l0_m | 1.0000e-06 | None | None | None | None | None | False | False | False | none |
| joint.beta_l_age_m | -0.0672 | None | None | None | None | None | False | False | False | none |
| joint.beta_l_age2_m | 0.0878 | None | None | None | None | None | False | False | False | none |
| joint.beta_l0_f | 10.0522 | None | None | None | None | None | False | False | False | none |
| joint.beta_l_age_f | -1.7803 | None | None | None | None | None | False | False | False | none |
| joint.beta_l_age2_f | 1.0000 | None | None | None | None | None | False | False | False | none |
| joint.beta_l_nkids_f | 0.5857 | None | None | None | None | None | False | False | False | none |
| joint.theta_l_f | -2.1317 | None | None | None | None | None | False | False | False | none |

### Block: `employment_hours_opportunity` (16 params)

| parameter | estimate | se_hessian | t_hessian | se_robust | t_robust | p_robust | fixed | at_lower | at_upper | primary_se |
|---|---|---|---|---|---|---|---|---|---|---|
| joint.beta_h_pt1 | -0.1636 | None | None | None | None | None | False | False | False | none |
| joint.beta_h_pt2 | 0.1804 | None | None | None | None | None | False | False | False | none |
| joint.beta_h_ft | 1.3589 | None | None | None | None | None | False | False | False | none |
| joint.beta_h_lh | -0.8987 | None | None | None | None | None | False | False | False | none |
| joint.beta_E_gsur | -1.0490 | None | None | None | None | None | False | False | False | none |
| joint.beta_E_drgn2 | -0.3226 | None | None | None | None | None | False | False | False | none |
| joint.beta_E_drgn3 | -0.1970 | None | None | None | None | None | False | False | False | none |
| joint.beta_E_drgn4 | -0.8333 | None | None | None | None | None | False | False | False | none |
| joint.beta_E_drgn5 | -0.4064 | None | None | None | None | None | False | False | False | none |
| joint.beta_E_drgn6 | -0.5849 | None | None | None | None | None | False | False | False | none |
| joint.beta_E_drgn7 | -0.4154 | None | None | None | None | None | False | False | False | none |
| joint.beta_E_drgn8 | -0.4420 | None | None | None | None | None | False | False | False | none |
| joint.beta_E_y2015 | -0.2546 | None | None | None | None | None | False | False | False | none |
| joint.beta_E_y2017 | -0.0695 | None | None | None | None | None | False | False | False | none |
| joint.beta_E_drgur | 0.0034 | None | None | None | None | None | False | False | False | none |
| joint.beta_E_drgmd | 0.0358 | None | None | None | None | None | False | False | False | none |

### Block: `wage_opportunity` (6 params)

| parameter | estimate | se_hessian | t_hessian | se_robust | t_robust | p_robust | fixed | at_lower | at_upper | primary_se |
|---|---|---|---|---|---|---|---|---|---|---|
| joint.beta_w0 | 2.1368 | None | None | None | None | None | False | False | False | none |
| joint.beta_w_educL | 0.0183 | None | None | None | None | None | False | False | False | none |
| joint.beta_w_educH | 0.3237 | None | None | None | None | None | False | False | False | none |
| joint.beta_w_pexp | 0.2278 | None | None | None | None | None | False | False | False | none |
| joint.beta_w_pexp2 | -0.0118 | None | None | None | None | None | False | False | False | none |
| joint.sigma | 0.4197 | None | None | None | None | None | False | False | False | none |

### Block: `occupation_opportunity` (6 params)

| parameter | estimate | se_hessian | t_hessian | se_robust | t_robust | p_robust | fixed | at_lower | at_upper | primary_se |
|---|---|---|---|---|---|---|---|---|---|---|
| joint.beta_occ_2_m | -1.5916 | None | None | None | None | None | False | False | False | none |
| joint.beta_occ_3_m | -2.2941 | None | None | None | None | None | False | False | False | none |
| joint.beta_occ_4_m | 0.2906 | None | None | None | None | None | False | False | False | none |
| joint.beta_occ_2_f | -0.0476 | None | None | None | None | None | False | False | False | none |
| joint.beta_occ_3_f | -0.4729 | None | None | None | None | None | False | False | False | none |
| joint.beta_occ_4_f | 0.7718 | None | None | None | None | None | False | False | False | none |

### Block: `other` (1 params)

| parameter | estimate | se_hessian | t_hessian | se_robust | t_robust | p_robust | fixed | at_lower | at_upper | primary_se |
|---|---|---|---|---|---|---|---|---|---|---|
| joint.beta_E | -1.7284 | None | None | None | None | None | False | False | False | none |

## Identification & Hessian Diagnostics (from DiagnosticsBundle)

_Not available: Hessian diagnostics not present in results JSON or cluster-SE JSON._

## Probability & Fit Diagnostics (from DiagnosticsBundle)

**Probability-sum sanity check:**

| field | value |
|---|---|
| max_error | 4.4409e-16 |
| mean_error | 9.6600e-17 |
| pct_off_by_0.01 | 0.0000e+00 |
| pct_off_by_0.001 | 0.0000e+00 |

**P(chosen) distribution:**

| field | value |
|---|---|
| min | 5.6553e-09 |
| max | 0.8319 |
| mean | 0.1400 |
| median | 0.1016 |
| q10 | 0.0074 |
| q25 | 0.0368 |
| q75 | 0.1862 |
| q90 | 0.3624 |

**Worst-fit households (top 10):**

| # | idhh | group | p_chosen | ll_i |
|---|---|---|---|---|
| 1.0000 | 3.6000e+06 | sf | 5.6553e-09 | -18.9907 |
| 2.0000 | 1.9188e+06 | sf | 5.5351e-08 | -16.7096 |
| 3.0000 | 3.4575e+06 | sm | 1.0665e-07 | -16.0537 |
| 4.0000 | 3.4087e+06 | sm | 2.2312e-05 | -10.7104 |
| 5.0000 | 2.1914e+06 | sm | 4.1901e-05 | -10.0802 |
| 6.0000 | 3.3828e+06 | sm | 6.4318e-05 | -9.6517 |
| 7.0000 | 3.3172e+06 | sf | 6.9361e-05 | -9.5762 |
| 8.0000 | 4.2880e+06 | sm | 7.2339e-05 | -9.5341 |
| 9.0000 | 3.8646e+06 | sm | 8.0880e-05 | -9.4225 |
| 10.0000 | 3.0900e+06 | sf | 8.4847e-05 | -9.3747 |

## Fit Statistics (legacy combined table — kept for backward compatibility)

| metric | value |
| --- | --- |
| log_likelihood | -4106.6 |
| ll_null_uniform | -7161.04 |
| ll_null_prior_corrected | -8473.13 |
| rho_squared | 0.515338 |
| rho_squared_adj | 0.509791 |
| rho_squared_uniform | 0.426535 |
| rho_squared_prior_corrected | 0.515338 |
| AIC | 8307.21 |
| BIC | 8558.62 |
| AIC_per_obs | 5.34226 |
| n_observations | 1555 |
| n_groups | 1555 |
| n_parameters | 47 |
| n_obs_long | 155500 |

## Fit Moments

| group | participation_observed | participation_predicted | mean_hours_observed | mean_hours_predicted |
| --- | --- | --- | --- | --- |
| sf | 0.871581 | 0.874044 | 36.3124 | 35.5259 |
| sm | 0.861345 | 0.921569 | 39.387 | 36.0889 |

## Observed Hours Quantiles (chosen working alts)

| group | n | q10 | q25 | q50 | q75 | q90 |
| --- | --- | --- | --- | --- | --- | --- |
| singles_male | 615 | 35 | 35 | 39 | 42 | 50 |
| singles_female | 733 | 25 | 35 | 36 | 40 | 45 |

## Distribution Fit Summary (observed vs predicted hours bins)

| group | dimension | n_bins | L1_distance | L2_distance |
| --- | --- | --- | --- | --- |
| sf | hours_bins | 12 | 0.6849 | 0.2598 |
| sm | hours_bins | 12 | 0.7955 | 0.3202 |

## Observed vs Implied Log-Wage σ (chosen working alts)

| group | n | observed_mean_log_wage | observed_std_log_wage | implied_sigma |
| --- | --- | --- | --- | --- |
| singles_male | 615 | 2.6835 | 0.4474 | 0.419664 |
| singles_female | 733 | 2.6009 | 0.4467 | 0.419664 |

## Structural Elasticity Heuristics

These are curvature-based heuristics from the post-estimation script, not
policy-counterfactual elasticities.

| Group | Hicksian (compensated) | Marshallian (uncompensated) | Participation (extensive) | Intensive (conditional) | theta_l | theta_c | beta_l (at median X) | beta_c |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single Males | 3.394 | 3.294 | 1.018 | 2.376 | -2.394 | -0.077 | 4.798 | 1.000 |
| Single Females | 3.113 | 3.013 | 0.934 | 2.179 | -2.113 | -0.077 | 8.135 | 1.000 |
| Males in Couples | 0.500 | 0.400 | 0.150 | 0.350 | 0.500 | -0.077 | 0.000 | 1.000 |
| Females in Couples | 3.132 | 3.032 | 0.940 | 2.192 | -2.132 | -0.077 | 10.052 | 1.000 |

## Marginal Utility Diagnostics

| Group | beta_c | theta_c | MUC Positive? | MUC Diminishing? | Well-Behaved? | MUC at Median C | C where MUC=1 | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single Males | 1 | 0.5 | yes | yes | yes | 1 | 1 | NA |
| Single Females | 1 | 0.5 | yes | yes | yes | 1 | 1 | NA |
| Males in Couples | 1 | 0 | yes | yes | yes | 1 | 1 | NA |
| Females in Couples | 1 | 0 | yes | yes | yes | 1 | 1 | NA |

## Marginal Utility Distribution Summary

| group | N | n_neg_muc | pct_neg_muc | mean_muc | n_neg_mul | pct_neg_mul | mean_mul |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sf | 714 | 0 | 0 | 0.0301854 | 0 | 0 | 0.000181317 |
| sm | 841 | 0 | 0 | 0.0247972 | 0 | 0 | 3.08467e-05 |
| total | NA | 0 | 0 | NA | 0 | 0 | NA |

## Probability Diagnostics

| metric | value |
| --- | --- |
| prob_sum_max_error | 4.44089e-16 |
| prob_sum_mean_error | 9.66001e-17 |
| prob_sum_pct_off_by_0.01 | 0 |
| prob_sum_pct_off_by_0.001 | 0 |
| p_chosen_min | 5.65531e-09 |
| p_chosen_max | 0.831864 |
| p_chosen_mean | 0.139967 |
| p_chosen_median | 0.101597 |
| p_chosen_q10 | 0.00741596 |
| p_chosen_q25 | 0.0368373 |
| p_chosen_q75 | 0.186213 |
| p_chosen_q90 | 0.362418 |

## Worst-Fit Households

| rank | idhh | group | p_chosen | ll_i |
| --- | --- | --- | --- | --- |
| 1 | 3600001 | sf | 5.65531e-09 | -18.9907 |
| 2 | 1918802 | sf | 5.53506e-08 | -16.7096 |
| 3 | 3457500 | sm | 1.06651e-07 | -16.0537 |
| 4 | 3408700 | sm | 2.23125e-05 | -10.7104 |
| 5 | 2191400 | sm | 4.19013e-05 | -10.0802 |
| 6 | 3382800 | sm | 6.43185e-05 | -9.65166 |
| 7 | 3317202 | sf | 6.93613e-05 | -9.57618 |
| 8 | 4288000 | sm | 7.23389e-05 | -9.53415 |
| 9 | 3864601 | sm | 8.08796e-05 | -9.42255 |
| 10 | 3090000 | sf | 8.4847e-05 | -9.37466 |

## Identification Diagnostics

_None._


## Initial → Final Movement (top 15 by |Δ|)

| block | parameter | initial_value | final_estimate | delta |
| --- | --- | --- | --- | --- |
| preference | joint.beta_l0_sf | 3.72851 | 8.13454 | 4.40603 |
| preference | joint.beta_l_age_sf | 0.498636 | -0.92701 | -1.42565 |
| employment_hours_opportunity | joint.beta_h_pt1 | -1.43327 | -0.163635 | 1.26964 |
| employment_hours_opportunity | joint.beta_E | -0.752653 | -1.72836 | -0.975704 |
| market_residual_opportunity | joint.beta_E_drgn4 | -0.0168586 | -0.833315 | -0.816456 |
| preference | joint.theta_l_sf | -1.34909 | -2.1128 | -0.763719 |
| market_residual_opportunity | joint.beta_E_drgmd | -0.667545 | 0.0358074 | 0.703352 |
| preference | joint.beta_l_age2_sm | 0.38188 | 1 | 0.61812 |
| market_residual_opportunity | joint.beta_E_drgn6 | -0.048459 | -0.584852 | -0.536393 |
| market_residual_opportunity | joint.beta_E_drgur | -0.530488 | 0.0034228 | 0.533911 |
| preference | joint.theta_l_sm | -1.86161 | -2.3943 | -0.532687 |
| preference | joint.beta_l_nkids_sf | 1.73949 | 1.40262 | -0.33687 |
| employment_hours_opportunity | joint.beta_h_lh | -1.21848 | -0.898749 | 0.319735 |
| employment_hours_opportunity | joint.beta_h_ft | 1.04132 | 1.35889 | 0.317572 |
| preference | joint.beta_l_age_sm | 0.677531 | 0.370015 | -0.307515 |

## Top High-Correlation Parameter Pairs

_None._

## Weakest Eigenvector Diagnostics

_None._

## Parameters At Bounds

_None._

## Parameters Near Bounds (within 5% of bound width)

_No parameters within 5% of a bound._

## Top Significant Coefficients (top 15 by |t|)

_No t-values available._

## Parameter Estimates By Block

| block | parameter | estimate | std_error | t_value | p_value | lower_bound | upper_bound | initial_value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| employment_hours_opportunity | joint.beta_E | -1.72836 | NA | NA | NA | NA | NA | -0.752653 |
| employment_hours_opportunity | joint.beta_h_ft | 1.35889 | NA | NA | NA | NA | NA | 1.04132 |
| employment_hours_opportunity | joint.beta_h_lh | -0.898749 | NA | NA | NA | NA | NA | -1.21848 |
| employment_hours_opportunity | joint.beta_h_pt1 | -0.163635 | NA | NA | NA | NA | NA | -1.43327 |
| employment_hours_opportunity | joint.beta_h_pt2 | 0.18044 | NA | NA | NA | NA | NA | -0.103695 |
| market_residual_opportunity | joint.beta_E_drgmd | 0.0358074 | NA | NA | NA | NA | NA | -0.667545 |
| market_residual_opportunity | joint.beta_E_drgn2 | -0.322619 | NA | NA | NA | NA | NA | -0.0750286 |
| market_residual_opportunity | joint.beta_E_drgn3 | -0.196977 | NA | NA | NA | NA | NA | 0.0313138 |
| market_residual_opportunity | joint.beta_E_drgn4 | -0.833315 | NA | NA | NA | NA | NA | -0.0168586 |
| market_residual_opportunity | joint.beta_E_drgn5 | -0.406423 | NA | NA | NA | NA | NA | -0.140207 |
| market_residual_opportunity | joint.beta_E_drgn6 | -0.584852 | NA | NA | NA | NA | NA | -0.048459 |
| market_residual_opportunity | joint.beta_E_drgn7 | -0.415387 | NA | NA | NA | NA | NA | -0.175153 |
| market_residual_opportunity | joint.beta_E_drgn8 | -0.441965 | NA | NA | NA | NA | NA | -0.365694 |
| market_residual_opportunity | joint.beta_E_drgur | 0.0034228 | NA | NA | NA | NA | NA | -0.530488 |
| market_residual_opportunity | joint.beta_E_gsur | -1.04902 | NA | NA | NA | NA | NA | -1.30619 |
| market_residual_opportunity | joint.beta_E_y2015 | -0.254606 | NA | NA | NA | NA | NA | NA |
| market_residual_opportunity | joint.beta_E_y2017 | -0.0694711 | NA | NA | NA | NA | NA | NA |
| occupation_opportunity | joint.beta_occ_2_f | -0.0475805 | NA | NA | NA | NA | NA | NA |
| occupation_opportunity | joint.beta_occ_2_m | -1.59165 | NA | NA | NA | NA | NA | NA |
| occupation_opportunity | joint.beta_occ_3_f | -0.472919 | NA | NA | NA | NA | NA | NA |
| occupation_opportunity | joint.beta_occ_3_m | -2.2941 | NA | NA | NA | NA | NA | NA |
| occupation_opportunity | joint.beta_occ_4_f | 0.771794 | NA | NA | NA | NA | NA | NA |
| occupation_opportunity | joint.beta_occ_4_m | 0.290643 | NA | NA | NA | NA | NA | NA |
| preference | joint.beta_l0_f | 10.0522 | NA | NA | NA | NA | NA | NA |
| preference | joint.beta_l0_m | 1e-06 | NA | NA | NA | NA | NA | NA |
| preference | joint.beta_l0_sf | 8.13454 | NA | NA | NA | NA | NA | 3.72851 |
| preference | joint.beta_l0_sm | 4.79827 | NA | NA | NA | NA | NA | 4.54866 |
| preference | joint.beta_l_age2_f | 1 | NA | NA | NA | NA | NA | NA |
| preference | joint.beta_l_age2_m | 0.0877505 | NA | NA | NA | NA | NA | NA |
| preference | joint.beta_l_age2_sf | 1 | NA | NA | NA | NA | NA | 1 |
| preference | joint.beta_l_age2_sm | 1 | NA | NA | NA | NA | NA | 0.38188 |
| preference | joint.beta_l_age_f | -1.78025 | NA | NA | NA | NA | NA | NA |
| preference | joint.beta_l_age_m | -0.0672369 | NA | NA | NA | NA | NA | NA |
| preference | joint.beta_l_age_sf | -0.92701 | NA | NA | NA | NA | NA | 0.498636 |
| preference | joint.beta_l_age_sm | 0.370015 | NA | NA | NA | NA | NA | 0.677531 |
| preference | joint.beta_l_nkids_f | 0.58572 | NA | NA | NA | NA | NA | NA |
| preference | joint.beta_l_nkids_sf | 1.40262 | NA | NA | NA | NA | NA | 1.73949 |
| preference | joint.theta_c_singles | -0.0770659 | NA | NA | NA | NA | NA | 0.00758098 |
| preference | joint.theta_l_f | -2.13174 | NA | NA | NA | NA | NA | NA |
| preference | joint.theta_l_sf | -2.1128 | NA | NA | NA | NA | NA | -1.34909 |
| preference | joint.theta_l_sm | -2.3943 | NA | NA | NA | NA | NA | -1.86161 |
| wage_opportunity | joint.beta_w0 | 2.13676 | NA | NA | NA | NA | NA | 2.19682 |
| wage_opportunity | joint.beta_w_educH | 0.323746 | NA | NA | NA | NA | NA | 0.338203 |
| wage_opportunity | joint.beta_w_educL | 0.0182873 | NA | NA | NA | NA | NA | -0.0607639 |
| wage_opportunity | joint.beta_w_pexp | 0.227847 | NA | NA | NA | NA | NA | 0.38278 |
| wage_opportunity | joint.beta_w_pexp2 | -0.0117863 | NA | NA | NA | NA | NA | -0.0822425 |
| wage_opportunity | joint.sigma | 0.419664 | NA | NA | NA | NA | NA | 0.389825 |

## Hours Distribution Shares

| group | hours_bin | observed_share | predicted_share |
| --- | --- | --- | --- |
| sf | 0 | 0.128419 | 0 |
| sf | 0-10 | 0.0059453 | 0.00713436 |
| sf | 10-17.5 | 0.0261593 | 0.0606421 |
| sf | 21.5-28.5 | 0.0570749 | 0.175981 |
| sf | 30.5-33.5 | 0.0309156 | 0.154578 |
| sf | 40.5-44.5 | 0.0499405 | 0.0439952 |
| sf | 70+ | 0 | 0 |
| sf | F35 ref (33.5-36.5) | 0.255648 | 0.219976 |
| sf | FT (36.5-40.5) | 0.25327 | 0.193817 |
| sf | LH (44.5-70) | 0.118906 | 0.0059453 |
| sf | PT1 (17.5-21.5) | 0.0380499 | 0.0511296 |
| sf | PT2 (28.5-30.5) | 0.0356718 | 0.0868014 |
| sm | 0 | 0.138655 | 0 |
| sm | 0-10 | 0.00280112 | 0.00420168 |
| sm | 10-17.5 | 0.0070028 | 0.0238095 |
| sm | 21.5-28.5 | 0.0280112 | 0.106443 |
| sm | 30.5-33.5 | 0.00980392 | 0.20028 |
| sm | 40.5-44.5 | 0.0602241 | 0.057423 |
| sm | 70+ | 0 | 0 |
| sm | F35 ref (33.5-36.5) | 0.247899 | 0.281513 |
| sm | FT (36.5-40.5) | 0.317927 | 0.221289 |
| sm | LH (44.5-70) | 0.169468 | 0.00980392 |
| sm | PT1 (17.5-21.5) | 0.012605 | 0.022409 |
| sm | PT2 (28.5-30.5) | 0.00560224 | 0.0728291 |

## Wage Distribution Summary

Observed values use chosen working alternatives. Predicted values use
choice-probability weights over working alternatives.

| group | n_observed_working | predicted_worker_weight | obs_mean | pred_mean | obs_q10 | obs_q50 | obs_q90 | pred_q10 | pred_q50 | pred_q90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | 615 | 664.015 | 16.1187 | 14.5654 | 9.15803 | 14.5673 | 25.2172 | 7.42026 | 13.279 | 23.148 |
| singles_female | 733 | 779.804 | 14.8695 | 14.2428 | 8.45438 | 13.5552 | 22.5924 | 7.21532 | 12.8477 | 22.7881 |

## Occupation Distribution Shares

Observed shares use chosen working alternatives. Predicted shares use
choice-probability weights over working alternatives. Category labels
are reported for loc4-style variables when available.

| group | occupation_column | category | label | observed_share | predicted_share | observed_count | predicted_weight |
| --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | loc4 | 1 | routine_manual_ref | 0.380488 | 0.328848 | 234 | 218.36 |
| singles_male | loc4 | 2 | nonroutine_manual | 0.099187 | 0.085765 | 61 | 56.9493 |
| singles_male | loc4 | 3 | routine_cognitive | 0.0536585 | 0.0465574 | 33 | 30.9148 |
| singles_male | loc4 | 4 | nonroutine_cognitive | 0.466667 | 0.538829 | 287 | 357.791 |
| singles_female | loc4 | 1 | routine_manual_ref | 0.188267 | 0.162692 | 138 | 126.868 |
| singles_female | loc4 | 2 | nonroutine_manual | 0.19236 | 0.167504 | 141 | 130.62 |
| singles_female | loc4 | 3 | routine_cognitive | 0.135061 | 0.119591 | 99 | 93.2573 |
| singles_female | loc4 | 4 | nonroutine_cognitive | 0.484311 | 0.550213 | 355 | 429.059 |

## Notes For Use

- This Markdown file is the preferred low-token artifact for LLM review.
- Use the HTML report only when plots or visual diagnostics are needed.
- Generated output folders remain local unless explicitly added to Git.
