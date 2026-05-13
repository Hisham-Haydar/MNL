# RURO ruro_occ_M0a_clean — Participation Pathology Diagnostic v1

Date: 2026-05-13T19:51:00

## 1. Input files

| item | path / value |
| --- | --- |
| spec YAML | `\\users\users\hisham\Desktop\Nizam_Hisham\MNL\scripts\enhanced\estimation_spec_ruro_occ_M0a_clean.yaml` |
| results JSON | `\\users\users\hisham\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0a_clean\run_2026-05-13_19-24-38\estimation_results.json` |
| post-est summary MD | `\\users\users\hisham\Desktop\Nizam_Hisham\MNL\reports\fr_2016_ruro_occ_gamspy_M0a_clean_llm_summary_20260513_193536.md` |
| singles parquet mtime | 2026-05-13T10:38:21 |
| couples parquet mtime | 2026-05-13T10:38:22 |
| joint_ll | -6521.4292 |
| n_params | 47 |
| sample seed | 17 |

## 2. Sanity checks

| check | result |
| --- | --- |
| `spec_name_matches` | 1 |
| `n_params_eq_47` | 1 |
| `theta_c_singles_in_params` | 1 |
| `theta_c_sm_absent` | 1 |
| `theta_c_sf_absent` | 1 |
| `theta_c_couples_present` | 1 |
| `singles_alts_per_hh_unique` | [100] |
| `couples_alts_per_hh_unique` | [100] |
| `singles_chosen_per_hh_unique` | [1] |
| `couples_chosen_per_hh_unique` | [1] |
| `singles_min_prior` | 0.0000 |
| `couples_min_prior` | 0.0000 |
| `singles_max_abs_log_prior_diff` | 0.0000 |
| `couples_max_abs_log_prior_diff` | 0.0000 |

## 3. Sample sizes

| group | n_hh sampled | n_hh total |
| --- | --- | --- |
| singles_male | 100 | 766 |
| singles_female | 100 | 910 |
| couples_male | 100 | 2,577 |
| couples_female | 100 | 2,577 |

## 4. V-component decomposition (median per group)

V_ij = U + O_E + O_H + O_market + O_W + O_Occ - log_prior. Couples reports the household V; the per-partner working filter is used to split work vs non-work rows. log_prior is read directly from the parquet (verified `log_prior == log(prior)` in D1).

| group | component | median work | median nonwork | work - nonwork |
| --- | --- | --- | --- | --- |
| singles_male | `U` | 6.2538 | 6.3883 | -0.1345 |
| singles_male | `O_E` | -2.7597 | 0.0000 | -2.7597 |
| singles_male | `O_H` | 0.0000 | 0.0000 | 0.0000 |
| singles_male | `O_market` | -0.0059 | 0.0000 | -0.0059 |
| singles_male | `O_W` | -16.0193 | 0.0000 | -16.0193 |
| singles_male | `O_Occ` | 0.0000 | 0.0000 | 0.0000 |
| singles_male | `minus_log_prior` | 10.6381 | 2.3026 | 8.3355 |
| singles_male | `V` | -1.9186 | 8.6909 | -10.6095 |
| singles_female | `U` | 7.0894 | 7.2052 | -0.1158 |
| singles_female | `O_E` | -2.7597 | 0.0000 | -2.7597 |
| singles_female | `O_H` | 0.0000 | 0.0000 | 0.0000 |
| singles_female | `O_market` | -0.0070 | 0.0000 | -0.0070 |
| singles_female | `O_W` | -16.1674 | 0.0000 | -16.1674 |
| singles_female | `O_Occ` | 0.0000 | 0.0000 | 0.0000 |
| singles_female | `minus_log_prior` | 10.6381 | 2.3026 | 8.3355 |
| singles_female | `V` | -0.3986 | 9.5078 | -9.9063 |
| couples_male | `U` | 406.8109 | 315.3855 | 91.4254 |
| couples_male | `O_E` | -5.5194 | -2.7597 | -2.7597 |
| couples_male | `O_H` | 0.0000 | 0.0000 | 0.0000 |
| couples_male | `O_market` | 0.5330 | 0.0000 | 0.5330 |
| couples_male | `O_W` | -29.9984 | -15.5330 | -14.4655 |
| couples_male | `O_Occ` | 0.4791 | 0.1878 | 0.2913 |
| couples_male | `minus_log_prior` | 20.8352 | 12.4147 | 8.4205 |
| couples_male | `V` | 393.0454 | 310.2504 | 82.7950 |
| couples_female | `U` | 406.3877 | 309.0448 | 97.3429 |
| couples_female | `O_E` | -5.5194 | -2.7597 | -2.7597 |
| couples_female | `O_H` | 0.0000 | 0.0000 | 0.0000 |
| couples_female | `O_market` | 0.5348 | -0.0059 | 0.5407 |
| couples_female | `O_W` | -29.8579 | -15.0105 | -14.8474 |
| couples_female | `O_Occ` | 0.4791 | 0.0000 | 0.4791 |
| couples_female | `minus_log_prior` | 20.8352 | 12.4147 | 8.4205 |
| couples_female | `V` | 392.8405 | 304.9830 | 87.8575 |

## 5. Structural P(nonwork) per group

Reported post-estimation `participation_predicted` = 1.0000 for all four groups (uniform; persists from M0 → M0a-equality → M0a-clean).

| group | median P(nonwork) | q10 | q25 | q75 | q90 | mean | observed nonwork rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | 0.0744 | 0.0364 | 0.0558 | 0.1071 | 0.1488 | 0.0880 | 0.0705 |
| singles_female | 0.0349 | 0.0206 | 0.0258 | 0.0612 | 0.0920 | 0.0501 | 0.0604 |
| couples_male | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0283 |
| couples_female | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0349 |

## 6. Non-work contribution audit

Expectation: working-gated opportunity terms (O_H, O_market, O_W, O_Occ) are exactly zero on non-work rows. log_prior on non-work rows should equal `log_q_E` only (since non-work has zero H, W, Occ proposal-density contributions by construction).

| group | n_nonwork | max\|O_H\| | max\|O_market\| | max\|O_W\| | max\|O_Occ\| | mean log_prior |
| --- | --- | --- | --- | --- | --- | --- |
| singles_male | 1,053 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -2.3026 |
| singles_female | 1,010 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -2.3026 |
| couples_male | 1,017 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -12.0565 |
| couples_female | 942 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -11.9934 |

## 7. Suspect code paths

### `post_est_fit_diagnostics_singles_param_lookup`

- file: `scripts/enhanced/RURO_post_estimation_styled.py`
- lines: 4652-4664
- issue:

  Singles V is reconstructed with params.get('beta_c', 1.0), params.get('theta_c', 0.5), params.get('theta_l', 0.5), and compute_beta_l_full(df_g, params, suffix='').
  For singles, the parameter dictionary contains gender-suffixed keys (beta_c_sm/sf, theta_l_sm/sf, beta_l0_sm/sf) — never the unsuffixed 'beta_c'/'theta_c'/'theta_l'/'beta_l0'.
  All four lookups silently fall back to the defaults, producing a V that does not reflect the estimated singles preferences..

### `post_est_fit_diagnostics_log_opp`

- file: `scripts/enhanced/RURO_post_estimation_styled.py`
- lines: 4671-4674
- issue:

  V += log_opp only if the column is pre-attached to df_g.
  compute_fit_diagnostics does not call _add_predicted_probabilities, so for singles the V used in the participation_predicted aggregation contains U_pref (with wrong params) minus log_prior, with NO opportunity contribution..

### `compute_beta_l_full_suffix`

- file: `scripts/enhanced/RURO_post_estimation_styled.py`
- lines: 4922-4923
- issue:

  beta_l0 lookup uses 'beta_l0' when suffix=''.
  Singles dict has beta_l0_sm or beta_l0_sf only; falls back to 0.0..

## 8. Verdict

ROOT CAUSE: post-estimation reporting code at scripts/enhanced/RURO_post_estimation_styled.py:4652. Spec-side and engine code are correct. Recommended fix: use group-suffixed parameter lookups (e.g. params['beta_c_sm'] for singles_male) inside compute_fit_diagnostics instead of params.get('beta_c', 1.0), and pass suffix='_sm'/'_sf' to compute_beta_l_full, then include the opportunity layer (log_opp or component recomputation) in V.
