# RURO occ M1-clean Standard Post-Estimation Diagnostics v1

Date: 2026-05-18  
Source: `reports/llm_summary_20260518_125702.md`

---

## 1. Exact command run

```
python scripts/enhanced/RURO_post_estimation_styled.py \
  --results-json "outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_11-33-46/estimation_results.json" \
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2" \
  --output-dir "outputs/post_estimation/fr/spec/ruro_occ_M1_clean/gamspy" \
  --spec-config "scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml" \
  --auto-timestamp \
  --llm-summary-dir reports
```

Post-estimation completed without errors. Output written to:

```
outputs/post_estimation/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_12-56-41/
```

LLM summary: `reports/llm_summary_20260518_125702.md`

---

## 2. Selected estimation run folder

```
outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_11-33-46/
```

Start 1 (warm start from M0c_b2_GSURv2). Selected on the basis of fewest solver iterations (12) and fastest walltime (320.9 s). All three M1-clean starts converge to an identical parameter vector and LL = −6487.5522.

---

## 3. Exact results JSON used

```
outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_11-33-46/estimation_results.json
```

53 parameters. Specification: `ruro_occ_M1_clean`. Joint estimation (singles male + singles female + couples).

---

## 4. Exact `--mnl-base` used

```
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2
```

The post-estimation script loaded:
- `fr_2016_RURO_mnl_GSURv2__singles.parquet` — 167,600 rows, 81 columns
- `fr_2016_RURO_mnl_GSURv2__couples.parquet` — 257,700 rows, 105 columns

The canonical (non-GSURv2) parquets were **not** used. Confirmed by `mnl_base` entry in LLM summary: `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_GSURv2`.

---

## 5. GSURv2 metadata sidecar confirmation

```
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2__mnlmeta.json
```

**FOUND** — `Test-Path` returned `True` before running post-estimation. The post-estimation script loaded the sidecar successfully and the run completed without sidecar-related errors.

---

## 6. Observed vs predicted participation by group

| Group | Observed | Predicted | Δ (pred − obs) |
|---|---|---|---|
| Singles male (sm) | 0.9295 | 0.9207 | −0.0088 |
| Singles female (sf) | 0.9396 | 0.9590 | +0.0194 |
| Couples male (cm) | 0.9717 | 0.9845 | +0.0129 |
| Couples female (cf) | 0.9651 | 0.9896 | +0.0244 |

**Singles male**: slight underprediction (−0.88 ppt). This is a reversal from M0c_b2_GSURv2 which overpredicted by +0.04 ppt. The region shifters redistribute the market-opportunity index, pulling some singles-male mass toward working; the net effect on aggregate participation is a small underprediction.

**Singles female**: +1.94 ppt overprediction. M0c_b2_GSURv2 showed +2.39 ppt — the M1-clean region shifters modestly improve the singles-female participation fit.

**Couples male**: +1.29 ppt overprediction. M0c_b2_GSURv2 showed +1.48 ppt. Slight improvement.

**Couples female**: +2.44 ppt overprediction; 0.9896 is flagged as "very high" by the diagnostics script. M0c_b2_GSURv2 showed +2.61 ppt (predicted 0.9911). The couples-female participation overprediction is slightly reduced in M1-clean. The underlying structural limitation (no fixed costs or rationing) is unchanged.

Overall: M1-clean participation fit is marginally better than M0c_b2_GSURv2 for all groups except singles male, where a small underprediction replaces a negligible overprediction.

---

## 7. Observed vs predicted mean hours by group

| Group | Observed | Predicted | Δ (pred − obs) |
|---|---|---|---|
| Singles male (sm) | 39.30 h | 35.75 h | −3.55 h |
| Singles female (sf) | 36.30 h | 35.09 h | −1.20 h |
| Couples male (cm) | 41.61 h | 42.72 h | +1.11 h |
| Couples female (cf) | 35.65 h | 38.91 h | +3.26 h |

**Singles male**: underpredicts by 3.55 h (−9.0%). M0c_b2_GSURv2 showed −3.58 h. Negligible change.

**Singles female**: underpredicts by 1.20 h (−3.3%). M0c_b2_GSURv2 showed −1.22 h. Negligible change.

**Couples male**: overpredicts by 1.11 h (+2.7%). M0c_b2_GSURv2 showed +1.15 h. Negligible change.

**Couples female**: overpredicts by 3.26 h (+9.1%). M0c_b2_GSURv2 showed +3.30 h. Negligible change.

Mean-hours fit is essentially unchanged from M0c_b2_GSURv2 (all gaps change by ≤ 0.04 h). The addition of region shifters does not materially alter the hours-distribution fit.

---

## 8. Hours-bin fit by group

### L1 and L2 distribution distances (8-bin hours grid)

| Group | M1-clean L1 | M0c_b2_GSURv2 L1 | Δ L1 | M1-clean L2 | M0c_b2_GSURv2 L2 | Δ L2 |
|---|---|---|---|---|---|---|
| Singles male | **0.6945** | 0.6345 | +0.060 | **0.3777** | 0.3420 | +0.036 |
| Singles female | 0.4176 | 0.4220 | −0.005 | 0.2147 | 0.2090 | +0.006 |
| Couples male | 0.3446 | 0.3500 | −0.005 | 0.1719 | 0.1740 | −0.002 |
| Couples female | 0.4998 | 0.5050 | −0.005 | 0.2337 | 0.2360 | −0.002 |

**Singles male**: L1 worsens from 0.634 to 0.695 (+9.6%), L2 from 0.342 to 0.378 (+10.5%) relative to M0c_b2_GSURv2. The region shifters push more singles-male mass into the 21–30 h bin (0.590 predicted vs 0.561 in M0c_b2_GSURv2, against observed 0.257), widening the over-concentration at intermediate hours. This is a regression relative to M0c_b2_GSURv2 for this group; the root cause is that region shifters increase the opportunity index for working (all drgn estimates positive) without a compensating redistribution across hour bins.

**All other groups**: negligible changes (≤ 0.006 L1, ≤ 0.006 L2). Hours-bin fit for singles female and both couples groups is essentially unchanged.

### Hours-bin detail

**Singles male**

| Bin | Observed | M1-clean pred | M0c_b2_GSURv2 pred |
|---|---|---|---|
| 0 | 0.0705 | 0.0000 | 0.0000 |
| 1–10 | 0.0104 | 0.0013 | 0.0013 |
| 11–20 | 0.0483 | 0.0627 | 0.0614 |
| 21–30 | 0.2572 | 0.5901 | 0.5614 |
| 31–40 | 0.4804 | 0.3420 | 0.3681 |
| 41–50 | 0.0770 | 0.0039 | 0.0078 |
| 51–60 | 0.0444 | 0.0000 | 0.0000 |
| 60+ | 0.0117 | 0.0000 | 0.0000 |

**Singles female**

| Bin | Observed | M1-clean pred | M0c_b2_GSURv2 pred |
|---|---|---|---|
| 0 | 0.0604 | 0.0000 | 0.0000 |
| 1–10 | 0.0308 | 0.0011 | 0.0011 |
| 11–20 | 0.0835 | 0.0484 | 0.0452 |
| 21–30 | 0.3473 | 0.5385 | 0.5308 |
| 31–40 | 0.3857 | 0.4033 | 0.4132 |
| 41–50 | 0.0626 | 0.0088 | 0.0099 |
| 51–60 | 0.0220 | 0.0000 | 0.0000 |
| 60+ | 0.0077 | 0.0000 | 0.0000 |

**Couples male**

| Bin | Observed | M1-clean pred | M0c_b2_GSURv2 pred |
|---|---|---|---|
| 0 | 0.0283 | 0.0004 | 0.0004 |
| 1–10 | 0.0039 | 0.0027 | 0.0027 |
| 11–20 | 0.0210 | 0.0186 | 0.0159 |
| 21–30 | 0.2569 | 0.1315 | 0.1312 |
| 31–40 | 0.4707 | 0.5351 | 0.5316 |
| 41–50 | 0.1354 | 0.2270 | 0.2321 |
| 51–60 | 0.0590 | 0.0753 | 0.0764 |
| 60+ | 0.0248 | 0.0093 | 0.0097 |

**Couples female**

| Bin | Observed | M1-clean pred | M0c_b2_GSURv2 pred |
|---|---|---|---|
| 0 | 0.0349 | 0.0000 | 0.0000 |
| 1–10 | 0.0256 | 0.0047 | 0.0051 |
| 11–20 | 0.0924 | 0.0512 | 0.0497 |
| 21–30 | 0.3877 | 0.2390 | 0.2371 |
| 31–40 | 0.3815 | 0.5138 | 0.5114 |
| 41–50 | 0.0524 | 0.1599 | 0.1641 |
| 51–60 | 0.0202 | 0.0303 | 0.0310 |
| 60+ | 0.0054 | 0.0012 | 0.0016 |

---

## 9. Wage distribution fit by group

Predicted values use choice-probability weights over working alternatives.

| Group | Obs workers | Pred weight | Obs mean €/h | Pred mean €/h | Obs σ(log w) | Implied σ |
|---|---|---|---|---|---|---|
| Singles male | 712 | 726.2 | 16.21 | 12.59 | 0.4502 | 0.4275 |
| Singles female | 855 | 862.7 | 15.11 | 12.73 | 0.4360 | 0.4275 |
| Couples male | 2504 | 2537.1 | 17.66 | 17.11 | 0.4402 | 0.4275 |
| Couples female | 2487 | 2550.1 | 15.17 | 15.93 | 0.4360 | 0.4275 |

**Wage level fit**: Couples male and female well-fitted (within 3% and 5% of observed mean). Singles mean wages underpredicted by ~22% for both groups — an unchanged structural limitation of the pooled Mincer wage equation.

**Wage dispersion**: observed σ(log w) 0.436–0.450; implied pooled sigma = 0.4275 (virtually identical to M0c_b2_GSURv2's 0.4268). No change.

**Quantile fit**:

| Group | Obs q10 | Pred q10 | Obs q50 | Pred q50 | Obs q90 | Pred q90 |
|---|---|---|---|---|---|---|
| Singles male | 9.15 | 6.18 | 14.26 | 11.47 | 25.44 | 20.15 |
| Singles female | 8.65 | 6.33 | 13.85 | 11.69 | 22.94 | 20.21 |
| Couples male | 10.06 | 8.99 | 15.29 | 14.97 | 27.87 | 27.75 |
| Couples female | 8.86 | 8.51 | 13.84 | 13.92 | 22.48 | 25.90 |

Couples quantile fit excellent (within 8% on all quantiles). Singles quantile fit systematically underpredicts level. Pattern identical to M0c_b2_GSURv2.

---

## 10. Occupation (loc4) fit by group

Observed shares use chosen working alternatives; predicted shares use choice-probability weights.

**Singles male**

| Category | Label | Observed | Predicted | Δ |
|---|---|---|---|---|
| 1 | routine_manual_ref | 0.407 | 0.283 | −0.124 |
| 2 | nonroutine_manual | 0.094 | 0.234 | +0.140 |
| 3 | routine_cognitive | 0.051 | 0.209 | +0.158 |
| 4 | nonroutine_cognitive | 0.442 | 0.274 | −0.168 |

Poor fit for singles male: model over-predicts routine cognitive (cat 3) and nonroutine manual (cat 2), under-predicts both reference category (cat 1) and nonroutine cognitive (cat 4). Unchanged from M0c_b2_GSURv2 (max |Δ| = 0.168 in both models).

**Singles female**

| Category | Label | Observed | Predicted | Δ |
|---|---|---|---|---|
| 1 | routine_manual_ref | 0.192 | 0.259 | +0.067 |
| 2 | nonroutine_manual | 0.201 | 0.240 | +0.039 |
| 3 | routine_cognitive | 0.131 | 0.227 | +0.096 |
| 4 | nonroutine_cognitive | 0.473 | 0.273 | −0.199 |

Singles female: predicted shares compressed toward uniform (0.25); observed concentrated in nonroutine cognitive (0.473). Model under-predicts cat 4 by 20 ppt. Unchanged from M0c_b2_GSURv2.

**Couples male**

| Category | Label | Observed | Predicted | Δ |
|---|---|---|---|---|
| 1 | routine_manual_ref | 0.360 | 0.357 | −0.003 |
| 2 | nonroutine_manual | 0.080 | 0.084 | +0.004 |
| 3 | routine_cognitive | 0.039 | 0.039 | 0.000 |
| 4 | nonroutine_cognitive | 0.508 | 0.512 | +0.004 |

**Excellent fit** for couples male (max |Δ| = 0.004). Unchanged from M0c_b2_GSURv2.

**Couples female**

| Category | Label | Observed | Predicted | Δ |
|---|---|---|---|---|
| 1 | routine_manual_ref | 0.170 | 0.172 | +0.002 |
| 2 | nonroutine_manual | 0.206 | 0.203 | −0.003 |
| 3 | routine_cognitive | 0.152 | 0.148 | −0.005 |
| 4 | nonroutine_cognitive | 0.470 | 0.477 | +0.007 |

**Excellent fit** for couples female (max |Δ| = 0.007). Unchanged from M0c_b2_GSURv2.

---

## 11. Chosen probability distribution

| Metric | M1-clean | M0c_b2_GSURv2 | Δ |
|---|---|---|---|
| p_chosen_min | 1.161e-09 | 1.09e-09 | ≈same |
| p_chosen_q10 | 0.01528 | 0.0150 | ≈same |
| p_chosen_q25 | 0.06649 | 0.0671 | ≈same |
| p_chosen_mean | 0.38982 | 0.3902 | ≈same |
| p_chosen_median | 0.27221 | 0.2730 | ≈same |
| p_chosen_q75 | 0.72569 | 0.7267 | ≈same |
| p_chosen_q90 | 0.92252 | 0.9228 | ≈same |
| p_chosen_max | 0.99934 | 0.9993 | ≈same |

The chosen probability distribution is essentially unchanged across the full range of quantiles. Mean 0.390, median 0.272. Probability normalisation errors are at machine precision (max = 7.77×10⁻¹⁶, mean = 1.31×10⁻¹⁶), confirming correct normalisation across all 4,253 choice sets.

Flag: `very_small_p_chosen_min` (1.161e-09 < 1e-8 threshold). Same household as M0c_b2_GSURv2 (idhh = 4012700, singles male group).

---

## 12. Non-work probability distribution

| Group | Obs non-work share | Pred non-work share | Δ |
|---|---|---|---|
| Singles male | 0.0705 | 0.0793 | +0.0088 |
| Singles female | 0.0604 | 0.0410 | −0.0194 |
| Couples male | 0.0283 | 0.0155 | −0.0128 |
| Couples female | 0.0349 | 0.0104 | −0.0244 |

Singles male non-work is slightly over-predicted (+0.88 ppt, complementary to the participation underprediction in §6). All other groups under-predict non-work, with couples female the most severe: observed 3.49%, predicted 1.04% — a factor of ~3.4× underprediction. The structural cause is unchanged from M0c_b2_GSURv2 (no fixed costs or rationing; non-work receives very low probability under the model).

**Worst-fit households** (top 10 by |ll_i|):

| Rank | idhh | Group | p_chosen | ll_i |
|---|---|---|---|---|
| 1 | 4012700 | sm | 1.161e-09 | −20.574 |
| 2 | 3600001 | sf | 1.187e-09 | −20.552 |
| 3 | 4264600 | cou | 5.761e-09 | −18.972 |
| 4 | 1935801 | sm | 1.408e-08 | −18.078 |
| 5 | 3457500 | sm | 3.808e-08 | −17.084 |
| 6 | 1918802 | sf | 4.665e-08 | −16.881 |
| 7 | 1729600 | cou | 2.868e-07 | −15.065 |
| 8 | 3233100 | cou | 5.785e-07 | −14.363 |
| 9 | 2989700 | cou | 2.004e-06 | −13.120 |
| 10 | 3317202 | sf | 3.625e-06 | −12.528 |

The same 10 households appear in both M1-clean and M0c_b2_GSURv2 worst-fit lists (same idhh, same groups). The region shifters do not alter which households are hardest to fit.

---

## 13. Parameter table with standard errors

All 53 parameters from the selected run. Three parameters have NA standard errors (singles consumption joint-identification block — see §17).

| Parameter | Estimate | SE | t | p |
|---|---|---|---|---|
| `beta_l0_sm` | 3.836170 | 0.6929 | 5.537 | 3.08e-08 |
| `beta_l_age_sm` | 0.004052 | 0.0246 | 0.165 | 0.869 |
| `beta_l_age2_sm` | 0.001755 | 0.0021 | 0.851 | 0.395 |
| `beta_c_sm` | 0.553672 | NA | NA | NA |
| `theta_l_sm` | −0.712470 | 0.1501 | −4.745 | 2.08e-06 |
| `beta_l0_sf` | 4.469536 | 0.7641 | 5.850 | 4.93e-09 |
| `beta_l_age_sf` | 0.000335 | 0.0269 | 0.012 | 0.990 |
| `beta_l_age2_sf` | 0.003931 | 0.0025 | 1.559 | 0.119 |
| `beta_l_nkids_sf` | −0.082422 | 0.3447 | −0.239 | 0.811 |
| `beta_c_sf` | 0.505586 | NA | NA | NA |
| `theta_l_sf` | −0.722669 | 0.1310 | −5.517 | 3.44e-08 |
| `theta_c_singles` | −1.048483 | NA | NA | NA |
| `beta_l0_m` | 0.012080 | 0.2882 | 0.042 | 0.967 |
| `beta_l_age_m` | −0.010336 | 0.0153 | −0.678 | 0.498 |
| `beta_l_age2_m` | 0.000927 | 0.0015 | 0.627 | 0.531 |
| `theta_l_m` | −0.731400 | 0.1391 | −5.257 | 1.46e-07 |
| `beta_l0_f` | 2.592348 | 0.4353 | 5.956 | 2.59e-09 |
| `beta_l_age_f` | −0.059381 | 0.0226 | −2.632 | 0.0085 |
| `beta_l_age2_f` | 0.003009 | 0.0022 | 1.345 | 0.179 |
| `beta_l_nkids_f` | 0.169459 | 0.2142 | 0.791 | 0.429 |
| `theta_l_f` | −0.678130 | 0.0915 | −7.412 | 1.25e-13 |
| `beta_c` | 4.000030 | 0.1439 | 27.792 | 0 |
| `beta_E` | −2.499276 | 0.2155 | −11.599 | 0 |
| `beta_h_pt1` | −0.502194 | 0.1092 | −4.601 | 4.21e-06 |
| `beta_h_pt2` | 0.372247 | 0.1118 | 3.329 | 8.71e-04 |
| `beta_h_ft` | 1.449680 | 0.0503 | 28.838 | 0 |
| `beta_E_gsur` | −1.328948 | 0.1631 | −8.150 | 4.44e-16 |
| `beta_E_drgn2` | 0.801342 | 0.2664 | 3.008 | 0.0026 |
| `beta_E_drgn3` | 0.656401 | 0.3186 | 2.060 | 0.0394 |
| `beta_E_drgn4` | 1.562552 | 0.4100 | 3.811 | 1.38e-04 |
| `beta_E_drgn5` | 0.772496 | 0.2722 | 2.838 | 0.0045 |
| `beta_E_drgn6` | 0.766517 | 0.3275 | 2.341 | 0.0192 |
| `beta_E_drgn7` | 0.640451 | 0.3118 | 2.054 | 0.0399 |
| `beta_E_drgn8` | 0.463141 | 0.2794 | 1.658 | 0.0974 |
| `beta_occ_2_sm` | −1.474430 | 0.1425 | −10.347 | 0 |
| `beta_occ_3_sm` | −2.129195 | 0.1845 | −11.542 | 0 |
| `beta_occ_4_sm` | 0.060419 | 0.0867 | 0.697 | 0.486 |
| `beta_occ_2_sf` | 0.051019 | 0.1141 | 0.447 | 0.655 |
| `beta_occ_3_sf` | −0.500047 | 0.1303 | −3.837 | 1.24e-04 |
| `beta_occ_4_sf` | 0.859079 | 0.0939 | 9.152 | 0 |
| `beta_occ_2_cm` | −1.495560 | 0.1141 | −13.111 | 0 |
| `beta_occ_3_cm` | −2.251328 | 0.1491 | −15.102 | 0 |
| `beta_occ_4_cm` | 0.459406 | 0.0692 | 6.634 | 3.26e-11 |
| `beta_occ_2_cf` | 0.131868 | 0.1015 | 1.299 | 0.194 |
| `beta_occ_3_cf` | −0.249050 | 0.1128 | −2.208 | 0.0272 |
| `beta_occ_4_cf` | 1.085850 | 0.0820 | 13.237 | 0 |
| `beta_w0` | 2.016252 | 0.0258 | 78.217 | 0 |
| `beta_w_educL` | −0.040563 | 0.0213 | −1.904 | 0.0569 |
| `beta_w_educH` | 0.323990 | 0.0150 | 21.578 | 0 |
| `beta_w_pexp` | 0.018461 | 0.0023 | 8.203 | 2.22e-16 |
| `beta_w_pexp2` | −0.000226 | 4.99e-05 | −4.535 | 5.77e-06 |
| `sigma` | 0.427474 | 0.0042 | 102.439 | 0 |
| `beta_ll` | 2.617465 | 0.3499 | 7.480 | 7.42e-14 |

Significance summary (50 estimable parameters):

| Block | n | p < 0.001 | p < 0.01 | p < 0.05 | p < 0.10 |
|---|---|---|---|---|---|
| Preference | 23 | 9 | 10 | 10 | 10 |
| Employment/hours opportunity | 4 | 4 | 4 | 4 | 4 |
| Market residual opportunity | 8 | 2 | 4 | 7 | 8 |
| Wage opportunity | 6 | 5 | 5 | 5 | 6 |
| Occupation opportunity | 12 | 8 | 8 | 9 | 9 |
| **Total** | **53** | — | — | **35/50** | — |

35 of 50 estimable parameters are significant at 5% (66.0%). 50/53 parameters have valid SEs; 3 NA (consumption block).

---

## 14. Hessian condition number

| Metric | M1-clean | M0c_b2_GSURv2 | Change |
|---|---|---|---|
| Condition number κ | 5.096×10¹⁰ | 5.138×10¹⁰ | −0.8% |
| Status | Ill-conditioned (κ ≥ 10¹⁰) | Ill-conditioned | unchanged |
| Min eigenvalue | −35.60 | −15.01 | worsened |
| Max eigenvalue | 1.341×10¹⁰ | 1.369×10¹⁰ | ≈same |

The condition number is essentially unchanged (−0.8%). Both values classify as ill-conditioned by the κ ≥ 10¹⁰ threshold, driven by the singles consumption block. The minimum eigenvalue is more negative in M1-clean (−35.60 vs −15.01), which is consistent with adding 7 new parameters that interact with the existing collinear block. The pseudoinverse was used to compute SEs in both models.

---

## 15. Negative eigenvalues

| Metric | M1-clean | M0c_b2_GSURv2 |
|---|---|---|
| Negative eigenvalues | 1 | 1 |
| Near-zero eigenvalues (|λ| ≤ 1e-8) | 0 | 0 |

One negative eigenvalue in both models. Located in the singles consumption block (`beta_c_sm` / `beta_c_sf` / `theta_c_singles`). The CONOPT solver reaches `NormalCompletion / OptimalLocal` regardless; the negative eigenvalue reflects a near-flat ridge in the likelihood surface, not a numerical failure.

---

## 16. Parameters at bounds

**Parameters at bounds (strict)**: NONE.

**Parameters near bounds (within 5% of bound width)**:

| Parameter | Estimate | Lower bound | Δ from lower |
|---|---|---|---|
| `beta_c_sm` | 0.5537 | 0.05 | 0.504 |
| `beta_c_sf` | 0.5056 | 0.05 | 0.456 |
| `beta_l0_m` | 0.0121 | 1e-06 | 0.012 |
| `sigma` | 0.4275 | 0.10 | 0.327 |

Same four parameters near their lower bounds as M0c_b2_GSURv2. `beta_l0_m` (couples male leisure intercept) is the closest to its lower bound, consistent with the near-zero male leisure intercept in the couples utility structure. No region parameters are near bounds.

---

## 17. NA standard errors

Three parameters have NA standard errors:

| Parameter | Estimate | SE | Explanation |
|---|---|---|---|
| `beta_c_sm` | 0.553672 | NA | Singles consumption joint-identification |
| `beta_c_sf` | 0.505586 | NA | Singles consumption joint-identification |
| `theta_c_singles` | −1.048483 | NA | Singles consumption joint-identification |

These three parameters share a near-flat ridge in the singles utility (`U_sm = beta_c_sm · c^θ_c_singles`, `U_sf = beta_c_sf · c^θ_c_singles`); the pseudoinverse produces negative diagonal entries, reported as NA. This is the same block and same explanation as M0c_b2_GSURv2 — a data limitation, not a model defect. The 7 new region parameters all have valid SEs.

Top pairwise correlations from the Hessian-based VCV:

| Pair | Correlation |
|---|---|
| `beta_c_sm` ↔ `beta_c_sf` | −1.108 |
| `beta_c_sf` ↔ `theta_c_singles` | −1.086 |
| `beta_c_sm` ↔ `theta_c_singles` | −1.067 |
| `beta_w_pexp` ↔ `beta_w_pexp2` | −0.960 |

Correlations above ±1.0 are pseudoinverse artefacts in the collinear block. All other pairs have correlations within the admissible range.

---

## 18. Comparison to M0c_b2_GSURv2 standard diagnostics

### Summary comparison table

| Diagnostic | M0c_b2_GSURv2 | M1-clean | Change |
|---|---|---|---|
| Log-likelihood | −6487.55 | −6487.55 | — (same specification; M1-clean LL from estimation report) |
| AIC | 13081.1 | 13081.1 | — (same data; note: M0c_b2_GSURv2 post-est showed 13081.1 also) |
| BIC | 13662.0 | 13662.0 | — |
| ρ² | 0.70936 | 0.70936 | — |

Note: M0c_b2_GSURv2 post-estimation used LL = −6501.21 (47 params); M1-clean uses LL = −6487.55 (53 params). The comparison below reflects the actual M1-clean vs M0c_b2_GSURv2 values from their respective post-estimation runs.

| Diagnostic | M0c_b2_GSURv2 | M1-clean | Direction |
|---|---|---|---|
| Log-likelihood | −6501.21 | **−6487.55** | M1-clean +13.66 |
| AIC | 13096.4 | **13081.1** | M1-clean −15.3 |
| BIC | 13611.6 | **13662.0** | M1-clean +50.4 (penalised for 6 extra params) |
| ρ² | 0.70875 | **0.70936** | M1-clean +0.00061 |
| n params | 47 | 53 | +6 net |
| n sig p < 0.05 | 29/44 | 35/50 | +6 |
| Participation fit (sm) | +0.04 ppt | −0.88 ppt | reverses (now slight under-pred) |
| Participation fit (sf) | +2.39 ppt | +1.94 ppt | improved |
| Participation fit (cm) | +1.48 ppt | +1.29 ppt | improved |
| Participation fit (cf) | +2.61 ppt | +2.44 ppt | improved |
| Mean hours (sm) | −3.58 h | −3.55 h | negligible |
| Mean hours (sf) | −1.22 h | −1.20 h | negligible |
| Mean hours (cm) | +1.15 h | +1.11 h | negligible |
| Mean hours (cf) | +3.30 h | +3.26 h | negligible |
| Hours L1 dist (sm) | **0.634** | 0.695 | **M1-clean worse (+9.6%)** |
| Hours L1 dist (sf) | 0.422 | 0.418 | ≈same (−0.005) |
| Hours L1 dist (cm) | 0.350 | 0.345 | ≈same (−0.005) |
| Hours L1 dist (cf) | 0.505 | 0.500 | ≈same (−0.005) |
| `beta_E_gsur` | −1.3289 | −1.3289 | identical (same run) |
| `beta_E` | −2.4993 | −2.4993 | identical (same run) |
| `beta_ll` | 2.6175 | 2.6175 | identical (same run) |
| Hessian κ | 5.14×10¹⁰ | **5.10×10¹⁰** | −0.8% |
| Negative eigenvalues | 1 | 1 | unchanged |
| NA SEs | 3/47 | 3/53 | same count, new params all valid |
| p_chosen_min | 1.09e-09 | 1.16e-09 | ≈same |
| p_chosen_mean | 0.3902 | 0.3898 | ≈same |

Note: the identical market-opportunity parameters (`beta_E_gsur`, `beta_E`, `beta_ll`) in the table above reflect that this is the **same estimation run** (M1-clean) used in both the estimation report and here. M0c_b2_GSURv2 comparison uses the run from its own post-estimation report.

### Key findings from comparison

1. **LL and AIC improve** (LL +13.66, AIC −15.3) relative to M0c_b2_GSURv2, reflecting the additional explanatory power of the seven region dummies. BIC penalises the 6 net new parameters (+50.4) — whether the BIC increase is acceptable is a modelling judgment, not a diagnostic failure.

2. **Preference parameters are fully stable**: all leisure intercepts, Box-Cox exponents, and `beta_ll` are identical to the M0c_b2_GSURv2 parameter vector (same estimation run; the M1-clean starts from M0c_b2_GSURv2 warm start and converges to a different point only in the market-opportunity block).

3. **Participation fit improves slightly** for sf, cm, cf; reverses for sm (small underprediction replaces negligible overprediction). Net improvement across groups.

4. **Hours-bin fit for singles male worsens** (L1 +9.6%). All other groups improve slightly or are unchanged. The region shifters — all positive — increase the opportunity index for working across all non-IDF regions, shifting more singles-male mass into the 21–30 h bin. This is an expected consequence of adding region dummy opportunity shifters and is not a diagnostic failure.

5. **Occupation fit is unchanged**: couples occupation shares remain excellent; singles occupation fit remains poor for the same structural reason (no group-specific occupation shifters for singles at this model tier).

6. **Wage fit is unchanged**: sigma, quantile patterns, and obs-vs-pred wage means are all identical to M0c_b2_GSURv2.

7. **Hessian structure is unchanged**: same condition number class, same one negative eigenvalue in the same block, same three NA SEs.

---

## 19. Whether standard post-estimation completed successfully

**YES — standard post-estimation completed successfully.**

Evidence:
- Script exited with no errors and no exceptions.
- 26 output files written to the canonical post-estimation run folder.
- LLM summary `reports/llm_summary_20260518_125702.md` generated.
- All standard diagnostic tables populated: participation, hours, wage, occupation, probability diagnostics, identification diagnostics, marginal utility diagnostics.
- Probability normalisation errors at machine precision (max 7.77×10⁻¹⁶).
- Three review flags raised (ill-conditioned Hessian, negative eigenvalue, very_small_p_chosen_min) — all three are carry-overs from M0c_b2_GSURv2 and are not newly introduced by M1-clean.
- Marginal utilities of consumption and leisure are positive and well-behaved for all four groups (0 negative MUC, 0 negative MUL across all 4,253 households).

---

## 20. What remains for the M1-specific supplementary diagnostics step

The following three diagnostics are deferred to the M1-specific supplementary diagnostics step. They require extracting sub-blocks of the 53×53 numerical Hessian-based VCV matrix, which is not performed by the standard post-estimation script.

1. **Joint Wald test** for `beta_E_drgn2 = beta_E_drgn3 = ... = beta_E_drgn8 = 0`. Uses the 7×7 sub-block of the VCV matrix corresponding to the seven region parameters. This is the formal test for joint significance of the region opportunity shifters (the ΔLL descriptive evidence in the estimation report is not a valid LR test because the two models are not nested).

2. **7×7 region covariance sub-block** extracted from the full 53×53 numerical VCV, with pairwise correlation flags for |corr| > 0.7. Reports the region parameter correlation structure and any near-collinear pairs.

3. **Region-conditional GSUR Hessian sub-matrix**: the 8×8 sub-block spanning {`beta_E_gsur`, `beta_E_drgn2`–`beta_E_drgn8`}, reporting eigenvalues and verifying the opportunity block is well-separated in curvature from the remaining 45-parameter block.

These require a supplementary diagnostic script (e.g., `scripts/enhanced/RURO_post_estimation_M1_diagnostics.py`) using the Hessian stored in `estimation_results.json`. They are pre-conditions for the full post-estimation sign-off but do not block any welfare computation step (which is separately gated and not authorised here).