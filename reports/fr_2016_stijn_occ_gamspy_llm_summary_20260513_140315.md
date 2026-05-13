# RURO Low-Token Post-Estimation Summary

Generated: 2026-05-13T14:03:15

## Purpose

Compact text-only report for Git, paper drafting, and LLM review.
Figures and large HTML output are intentionally omitted.

## Sources

| item | path_or_value |
| --- | --- |
| estimation_results_json | U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\spec\stijn_occ\gamspy\estimation_spec_stijn_occ_M0\run_2026-05-13_11-27-40\estimation_results.json |
| html_report | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\stijn_occ\gamspy\estimation_spec_stijn_occ_M0\run_2026-05-13_14-02-54\fr_2016_stijn_occ_gamspy_post_estimation_report_20260513_140315.html |
| post_output_dir | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\stijn_occ\gamspy\estimation_spec_stijn_occ_M0\run_2026-05-13_14-02-54 |
| params_csv | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\stijn_occ\gamspy\estimation_spec_stijn_occ_M0\run_2026-05-13_14-02-54\fr_2016_stijn_occ_gamspy_params.csv |
| elasticities_csv | U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\spec\stijn_occ\gamspy\estimation_spec_stijn_occ_M0\run_2026-05-13_14-02-54\fr_2016_stijn_occ_gamspy_elasticities.csv |
| mnl_base | Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl |
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
| estimation_walltime_seconds | 300.917 |

## Convergence By Result Block

| group | success | message | iterations | log_likelihood | walltime_seconds |
| --- | --- | --- | --- | --- | --- |
| joint | 1 | SolveStatus.NormalCompletion (ModelStatus.OptimalLocal) | 29 | NA | 100.306 |

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

## Parameter Estimates By Block

| block | parameter | estimate | std_error | t_value | p_value | lower_bound | upper_bound | initial_value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| employment_hours_opportunity | joint.beta_E | -2.6148 | 0.302197 | -8.65263 | 0 | -25 | 25 | 0 |
| employment_hours_opportunity | joint.beta_h_ft | 1.46325 | 0.0499151 | 29.3148 | 0 | -10 | 10 | 0 |
| employment_hours_opportunity | joint.beta_h_pt1 | -0.52032 | 0.108553 | -4.79325 | 1.64105e-06 | -10 | 10 | 0 |
| employment_hours_opportunity | joint.beta_h_pt2 | 0.372057 | 0.110967 | 3.35285 | 0.000799846 | -10 | 10 | 0 |
| market_residual_opportunity | joint.beta_E_educH | 0.257516 | 0.240949 | 1.06876 | 0.285178 | -10 | 10 | 0 |
| market_residual_opportunity | joint.beta_E_gsur | -0.771874 | 0.221257 | -3.48859 | 0.000485584 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_cf | 0.205 | 0.100711 | 2.03553 | 0.0417975 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_cm | -1.47074 | 0.113888 | -12.9138 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_sf | -0.0147421 | 0.112918 | -0.130555 | 0.896127 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_2_sm | -1.51286 | 0.142327 | -10.6295 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_cf | -0.190384 | 0.11152 | -1.70716 | 0.0877915 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_cm | -2.20606 | 0.147763 | -14.9297 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_sf | -0.574523 | 0.129046 | -4.45209 | 8.50376e-06 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_3_sm | -2.17256 | 0.184534 | -11.7732 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_cf | 1.14601 | 0.0817332 | 14.0214 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_cm | 0.486156 | 0.0687146 | 7.075 | 1.49436e-12 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_sf | 0.793362 | 0.0922157 | 8.60332 | 0 | -10 | 10 | 0 |
| occupation_opportunity | joint.beta_occ_4_sm | 0.0175251 | 0.0860748 | 0.203603 | 0.838663 | -10 | 10 | 0 |
| preference | joint.beta_c | 5.26199 | 0.4629 | 11.3675 | 0 | 0.05 | 50 | 1 |
| preference | joint.beta_c_sf | 0.463007 | NA | NA | NA | 0.05 | 50 | 1 |
| preference | joint.beta_c_sm | 0.717509 | 0.265951 | 2.6979 | 0.00697783 | 0.05 | 50 | 1 |
| preference | joint.beta_l0_f | 5.69717 | 0.121995 | 46.7001 | 0 | 0.05 | 50 | 1 |
| preference | joint.beta_l0_m | 2.70226 | 0.420329 | 6.42893 | 1.28507e-10 | 0.05 | 50 | 1 |
| preference | joint.beta_l0_sf | 5.75853 | 0.182695 | 31.5199 | 0 | 0.05 | 50 | 1 |
| preference | joint.beta_l0_sm | 4.46662 | 0.159036 | 28.0856 | 0 | 0.05 | 50 | 1 |
| preference | joint.beta_l_age2_f | 0.00156521 | 0.00212253 | 0.737429 | 0.460861 | -1 | 1 | 0 |
| preference | joint.beta_l_age2_m | 0.00125552 | 0.00147658 | 0.850284 | 0.395167 | -1 | 1 | 0 |
| preference | joint.beta_l_age2_sf | 0.00332398 | 0.00252889 | 1.3144 | 0.188711 | -1 | 1 | 0 |
| preference | joint.beta_l_age2_sm | 0.00178502 | 0.00204537 | 0.872715 | 0.382818 | -1 | 1 | 0 |
| preference | joint.beta_l_age_f | -0.0577507 | 0.021519 | -2.6837 | 0.00728116 | -5 | 5 | 0 |
| preference | joint.beta_l_age_m | -0.00737894 | 0.0151219 | -0.487965 | 0.625575 | -5 | 5 | 0 |
| preference | joint.beta_l_age_sf | -0.016458 | 0.0267033 | -0.616327 | 0.537679 | -5 | 5 | 0 |
| preference | joint.beta_l_age_sm | 0.000844406 | 0.0246245 | 0.0342913 | 0.972645 | -5 | 5 | 0 |
| preference | joint.beta_l_educH_f | -1.48897 | 0.321195 | -4.63573 | 3.55682e-06 | -8 | 5 | 0 |
| preference | joint.beta_l_educH_m | -0.925907 | 0.31475 | -2.94172 | 0.00326395 | -8 | 5 | 0 |
| preference | joint.beta_l_educH_sf | -2.27103 | 0.341114 | -6.65768 | 2.78175e-11 | -8 | 5 | 0 |
| preference | joint.beta_l_educH_sm | -1.30348 | 0.372398 | -3.50023 | 0.000464864 | -8 | 5 | 0 |
| preference | joint.beta_l_nkids_f | 0.214934 | 0.206719 | 1.03974 | 0.298461 | -5 | 5 | 0 |
| preference | joint.beta_l_nkids_sf | -0.049599 | 0.344685 | -0.143897 | 0.885582 | -5 | 5 | 0 |
| preference | joint.theta_c | 0.215302 | 0.0741963 | 2.90178 | 0.00371044 | -8 | 0.95 | -1 |
| preference | joint.theta_c_sf | -1.08841 | NA | NA | NA | -8 | 0.95 | -1 |
| preference | joint.theta_c_sm | -0.856029 | 0.21686 | -3.94738 | 7.90099e-05 | -8 | 0.95 | -1 |
| preference | joint.theta_l_f | -0.695727 | 0.0630221 | -11.0394 | 0 | -8 | 0.95 | -1 |
| preference | joint.theta_l_m | -0.733006 | 0.12475 | -5.8758 | 4.20806e-09 | -8 | 0.95 | -1 |
| preference | joint.theta_l_sf | -0.723846 | 0.0852958 | -8.48631 | 0 | -8 | 0.95 | -1 |
| preference | joint.theta_l_sm | -0.703775 | 0.0989561 | -7.112 | 1.14375e-12 | -8 | 0.95 | -1 |
| wage_opportunity | joint.beta_w0 | 2.04108 | 0.0265072 | 77.001 | 0 | -10 | 20 | 2 |
| wage_opportunity | joint.beta_w_educH | 0.305522 | 0.0150065 | 20.3594 | 0 | -5 | 5 | 0.2 |
| wage_opportunity | joint.beta_w_educL | -0.0475667 | 0.0209238 | -2.27333 | 0.0230064 | -5 | 5 | -0.1 |
| wage_opportunity | joint.beta_w_pexp | 0.0173702 | 0.00221956 | 7.82595 | 5.10703e-15 | -1 | 1 | 0.02 |
| wage_opportunity | joint.beta_w_pexp2 | -0.000205608 | 4.91101e-05 | -4.18667 | 2.83076e-05 | -0.1 | 0.1 | -0.0003 |
| wage_opportunity | joint.sigma | 0.42316 | 0.0040911 | 103.434 | 0 | 0.1 | 20 | 0.5 |

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

## Notes For Use

- This Markdown file is the preferred low-token artifact for LLM review.
- Use the HTML report only when plots or visual diagnostics are needed.
- Generated output folders remain local unless explicitly added to Git.
