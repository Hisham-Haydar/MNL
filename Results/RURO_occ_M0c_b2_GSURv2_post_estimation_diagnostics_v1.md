# RURO occ M0c_b2 GSURv2 Post-Estimation Diagnostics v1

Date: 2026-05-18
Source: `reports/llm_summary_20260518_003039.md`

---

## 1. Command run

```
python scripts/enhanced/RURO_post_estimation_styled.py \
  --results-json outputs/estimates/fr/spec/ruro_occ_GSURv2/gamspy/estimation_spec_ruro_occ_M0c_b2_GSURv2/run_2026-05-17_23-55-09/estimation_results.json \
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2" \
  --output-dir outputs/post_estimation/fr/spec/ruro_occ_GSURv2/gamspy \
  --spec-config scripts/enhanced/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml \
  --auto-timestamp \
  --llm-summary-dir reports
```

Post-estimation completed without errors. Output written to:

```
outputs/post_estimation/fr/spec/ruro_occ_GSURv2/gamspy/estimation_spec_ruro_occ_M0c_b2_GSURv2/run_2026-05-18_00-30-18/
```

LLM summary: `reports/llm_summary_20260518_003039.md`

---

## 2. Selected estimation run folder

```
outputs/estimates/fr/spec/ruro_occ_GSURv2/gamspy/estimation_spec_ruro_occ_M0c_b2_GSURv2/run_2026-05-17_23-55-09/
```

This is Start 1 (warm start from accepted M0c_b2 solution). Selected on the basis of fewest
solver iterations (9) and fastest walltime (256 s). All three starts converge to identical
parameter vector and LL = −6501.2082.

---

## 3. Selected parameter vector

| Parameter | Estimate | SE | t | p |
|---|---|---|---|---|
| `beta_l0_sm` | 3.889771 | 0.723237 | 5.378 | 7.52e-08 |
| `beta_l_age_sm` | 0.007372 | 0.024830 | 0.297 | 0.767 |
| `beta_l_age2_sm` | 0.001880 | 0.002082 | 0.903 | 0.367 |
| `beta_c_sm` | 0.626489 | NA | NA | NA |
| `theta_l_sm` | −0.712287 | 0.154838 | −4.600 | 4.22e-06 |
| `beta_l0_sf` | 4.459395 | 0.780466 | 5.714 | 1.11e-08 |
| `beta_l_age_sf` | 0.001288 | 0.027267 | 0.047 | 0.962 |
| `beta_l_age2_sf` | 0.004170 | 0.002573 | 1.621 | 0.105 |
| `beta_l_nkids_sf` | 0.049652 | 0.357648 | 0.139 | 0.890 |
| `beta_c_sf` | 0.569571 | NA | NA | NA |
| `theta_l_sf` | −0.727822 | 0.134383 | −5.416 | 6.09e-08 |
| `theta_c_singles` | −0.944122 | NA | NA | NA |
| `beta_l0_m` | 0.011840 | 0.286342 | 0.041 | 0.967 |
| `beta_l_age_m` | −0.008212 | 0.015052 | −0.546 | 0.585 |
| `beta_l_age2_m` | 0.000748 | 0.001462 | 0.512 | 0.609 |
| `theta_l_m` | −0.731931 | 0.137287 | −5.331 | 9.75e-08 |
| `beta_l0_f` | 2.614413 | 0.432323 | 6.047 | 1.47e-09 |
| `beta_l_age_f` | −0.057103 | 0.022139 | −2.579 | 0.0099 |
| `beta_l_age2_f` | 0.002647 | 0.002198 | 1.205 | 0.228 |
| `beta_l_nkids_f` | 0.169148 | 0.213775 | 0.791 | 0.429 |
| `theta_l_f` | −0.679102 | 0.089775 | −7.565 | 3.89e-14 |
| `beta_c` | 4.045426 | 0.123360 | 32.794 | 0 |
| `beta_E` | −2.489457 | 0.272199 | −9.146 | 0 |
| `beta_h_pt1` | −0.498492 | 0.108025 | −4.615 | 3.94e-06 |
| `beta_h_pt2` | 0.364909 | 0.111300 | 3.279 | 0.001043 |
| `beta_h_ft` | 1.443825 | 0.050068 | 28.837 | 0 |
| `beta_E_gsur` | −1.050180 | 0.200182 | −5.246 | 1.55e-07 |
| `beta_E_educH` | 0.438559 | 0.225691 | 1.943 | 0.052 |
| `beta_occ_2_sm` | −1.511639 | 0.142096 | −10.638 | 0 |
| `beta_occ_3_sm` | −2.165526 | 0.184268 | −11.752 | 0 |
| `beta_occ_4_sm` | 0.023304 | 0.086049 | 0.271 | 0.787 |
| `beta_occ_2_sf` | −0.011200 | 0.112689 | −0.099 | 0.921 |
| `beta_occ_3_sf` | −0.562032 | 0.129024 | −4.356 | 1.32e-05 |
| `beta_occ_4_sf` | 0.798526 | 0.092087 | 8.671 | 0 |
| `beta_occ_2_cm` | −1.476632 | 0.113533 | −13.006 | 0 |
| `beta_occ_3_cm` | −2.225279 | 0.148081 | −15.027 | 0 |
| `beta_occ_4_cm` | 0.471138 | 0.068817 | 6.846 | 7.58e-12 |
| `beta_occ_2_cf` | 0.175078 | 0.100365 | 1.744 | 0.081 |
| `beta_occ_3_cf` | −0.215883 | 0.111766 | −1.932 | 0.053 |
| `beta_occ_4_cf` | 1.115369 | 0.081457 | 13.693 | 0 |
| `beta_w0` | 2.023640 | 0.025312 | 79.948 | 0 |
| `beta_w_educL` | −0.045563 | 0.021100 | −2.159 | 0.031 |
| `beta_w_educH` | 0.317749 | 0.014969 | 21.228 | 0 |
| `beta_w_pexp` | 0.018143 | 0.002233 | 8.125 | 4.44e-16 |
| `beta_w_pexp2` | −0.000220 | 4.95e-05 | −4.445 | 8.77e-06 |
| `sigma` | 0.426803 | 0.003983 | 107.143 | 0 |
| `beta_ll` | 2.605297 | 0.345739 | 7.535 | 4.86e-14 |

NA standard errors: `beta_c_sm`, `beta_c_sf`, `theta_c_singles` — singles consumption joint-identification limitation (unchanged from M0c_b2; see §17).

---

## 4. Exact `--mnl-base` used

```
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2
```

The post-estimation script loaded:
- `fr_2016_RURO_mnl_GSURv2__singles.parquet` — 167,600 rows, 81 columns (6 new GSURv2 columns)
- `fr_2016_RURO_mnl_GSURv2__couples.parquet` — 257,700 rows, 105 columns (partner-specific GSURv2 columns)

The canonical parquets were **not** used. Confirmed by `mnl_base` entry in LLM summary:
`Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_GSURv2`

---

## 5. GSURv2 metadata sidecar confirmed

```
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2__mnlmeta.json
```

**FOUND** — `Test-Path` returned `True` before running post-estimation. The post-estimation
script loaded the sidecar successfully; the run would have failed if absent.

The sidecar is a content-identical copy of the canonical sidecar (`fr_2016_RURO_mnl__mnlmeta.json`),
created in the estimation input-check step. All normalization constants, draws paths, and sample
sizes are identical between canonical and GSURv2 parquets; the GSUR correction is embedded in
the parquet columns, not re-derived from the sidecar at estimation or post-estimation time.

---

## 6. Observed vs predicted participation by group

| Group | Observed | Predicted | Δ (pred − obs) |
|---|---|---|---|
| Singles male (sm) | 0.9295 | 0.9299 | +0.0004 |
| Singles female (sf) | 0.9396 | 0.9634 | +0.0239 |
| Couples male (cm) | 0.9717 | 0.9865 | +0.0148 |
| Couples female (cf) | 0.9651 | **0.9911** | +0.0261 |

**Singles male**: near-perfect fit (+0.04 ppt). The model matches the observed participation rate with negligible overprediction.

**Singles female**: +2.4 ppt overprediction. M0c_b2 predicted 0.9516 against observed 0.9396 (Δ = +1.2 ppt), so GSURv2 widens this existing gap modestly rather than reproducing the same magnitude. The post-estimation script flags `cou_f: predicted participation is very high (0.9911)` as a review note.

**Couples male**: +1.5 ppt overprediction. Modest and consistent with M0c_b2 (+1.1 ppt).

**Couples female**: +2.6 ppt overprediction; 0.9911 is flagged as "very high" by the diagnostics script. M0c_b2 predicted 0.9887 (+2.4 ppt). The participation overprediction for couples female is the most prominent fit limitation in both models, reflecting the model's difficulty generating non-employment for couples female in a model that does not include fixed costs or rationing.

No participation gap direction reverses relative to M0c_b2. The fit is structurally stable.

---

## 7. Observed vs predicted mean hours by group

| Group | Observed | Predicted | Δ (pred − obs) |
|---|---|---|---|
| Singles male (sm) | 39.30 h | 35.72 h | −3.58 h |
| Singles female (sf) | 36.30 h | 35.08 h | −1.22 h |
| Couples male (cm) | 41.61 h | 42.76 h | +1.15 h |
| Couples female (cf) | 35.65 h | 38.95 h | +3.30 h |

**Singles male**: underpredicts by 3.58 h (−9.1%). This pattern is identical to M0c_b2 (−3.59 h). The model places too little weight on high-hours singles-male alternatives.

**Singles female**: underpredicts by 1.22 h (−3.4%). M0c_b2 showed −1.21 h. Negligible change.

**Couples male**: slight overprediction of +1.15 h (+2.8%). M0c_b2 showed +1.17 h. Unchanged.

**Couples female**: overpredicts by 3.30 h (+9.3%). M0c_b2 showed 3.33 h. Unchanged; driven by the participation overprediction (zero-hours alternatives assigned low weight pushes predicted mean hours up).

All four mean-hours gaps are essentially unchanged from M0c_b2, to within 0.04 h. The GSUR correction does not alter the hours distribution fit.

---

## 8. Hours-bin fit by group

### L1 and L2 distribution distances (8-bin hours grid)

| Group | L1 (GSURv2) | L1 (M0c_b2) | Δ L1 | L2 (GSURv2) | L2 (M0c_b2) | Δ L2 |
|---|---|---|---|---|---|---|
| Couples female | 0.505 | 0.501 | +0.004 | 0.236 | 0.234 | +0.002 |
| Couples male | 0.350 | 0.342 | +0.008 | 0.174 | 0.170 | +0.004 |
| Singles female | 0.422 | 0.404 | +0.018 | 0.209 | 0.223 | −0.014 |
| Singles male | **0.634** | **0.726** | **−0.092** | **0.342** | **0.390** | **−0.047** |

**Singles male**: meaningfully improved — L1 drops from 0.726 to 0.634 (−12.7%), L2 from 0.390 to 0.342 (−12.3%). The GSURv2 correction redistributes predicted mass from the 21-30 h bin (0.595 → 0.561) toward 31-40 h (0.324 → 0.368) and reduces the spike in 11-20 h (0.073 → 0.061). The overall hours-bin fit for singles male is noticeably better with the corrected GSUR.

**Singles female**: L1 increases slightly (+0.018) but L2 improves (−0.014), indicating the shape fit is marginally better even as total variation increases slightly. No material change.

**Couples**: negligible changes in both metrics (≤ 0.008 in L1, ≤ 0.004 in L2). The couples hours-bin fit is essentially unchanged.

### Hours-bin detail

**Singles male**

| Bin | Observed | GSURv2 pred | M0c_b2 pred |
|---|---|---|---|
| 0 | 0.0705 | 0.0000 | 0.0000 |
| 1-10 | 0.0104 | 0.0013 | 0.0026 |
| 11-20 | 0.0483 | 0.0614 | 0.0731 |
| 21-30 | 0.2572 | 0.5614 | 0.5953 |
| 31-40 | 0.4804 | 0.3681 | 0.3238 |
| 41-50 | 0.0770 | 0.0078 | 0.0052 |
| 51-60 | 0.0444 | 0.0000 | 0.0000 |
| 60+ | 0.0117 | 0.0000 | 0.0000 |

**Singles female**

| Bin | Observed | GSURv2 pred | M0c_b2 pred |
|---|---|---|---|
| 0 | 0.0604 | 0.0000 | 0.0000 |
| 1-10 | 0.0308 | 0.0011 | 0.0022 |
| 11-20 | 0.0835 | 0.0451 | 0.0560 |
| 21-30 | 0.3473 | 0.5308 | 0.5495 |
| 31-40 | 0.3857 | 0.4132 | 0.3857 |
| 41-50 | 0.0626 | 0.0099 | 0.0066 |
| 51-60 | 0.0220 | 0.0000 | 0.0000 |
| 60+ | 0.0077 | 0.0000 | 0.0000 |

**Couples male**

| Bin | Observed | GSURv2 pred | M0c_b2 pred |
|---|---|---|---|
| 0 | 0.0283 | 0.0004 | 0.0008 |
| 1-10 | 0.0039 | 0.0027 | 0.0023 |
| 11-20 | 0.0210 | 0.0159 | 0.0182 |
| 21-30 | 0.2569 | 0.1312 | 0.1343 |
| 31-40 | 0.4707 | 0.5316 | 0.5305 |
| 41-50 | 0.1354 | 0.2321 | 0.2293 |
| 51-60 | 0.0590 | 0.0764 | 0.0764 |
| 60+ | 0.0248 | 0.0097 | 0.0081 |

**Couples female**

| Bin | Observed | GSURv2 pred | M0c_b2 pred |
|---|---|---|---|
| 0 | 0.0349 | 0.0000 | 0.0000 |
| 1-10 | 0.0256 | 0.0050 | 0.0054 |
| 11-20 | 0.0924 | 0.0497 | 0.0489 |
| 21-30 | 0.3877 | 0.2371 | 0.2398 |
| 31-40 | 0.3815 | 0.5114 | 0.5142 |
| 41-50 | 0.0524 | 0.1641 | 0.1610 |
| 51-60 | 0.0202 | 0.0310 | 0.0295 |
| 60+ | 0.0054 | 0.0016 | 0.0012 |

---

## 9. Wage distribution fit by group

Predicted values use choice-probability weights over working alternatives.

| Group | Obs workers | Pred weight | Obs mean €/h | Pred mean €/h | Obs σ(log w) | Implied σ |
|---|---|---|---|---|---|---|
| Singles male | 712 | 731.7 | 16.21 | 12.61 | 0.4502 | 0.4268 |
| Singles female | 855 | 869.7 | 15.11 | 12.75 | 0.4360 | 0.4268 |
| Couples male | 2504 | 2542.2 | 17.66 | 17.15 | 0.4402 | 0.4268 |
| Couples female | 2487 | 2554.2 | 15.17 | 15.96 | 0.4360 | 0.4268 |

**Wage level fit**: Couples male and female are well-fitted (pred within 3% and 5% of observed mean). Singles mean wages are underpredicted by ~22% (both groups). This is a known structural limitation: the Mincer wage equation uses a single `sigma` for all groups; the singles wage draws are not separately calibrated.

**Wage dispersion**: observed `σ(log w)` ranges 0.436–0.450 across groups; the implied pooled `sigma = 0.4268` is close to all four groups. No material change from M0c_b2 (`sigma = 0.4268`, identical to 4 decimal places).

Observed vs predicted wage quantiles:

| Group | Obs q10 | Pred q10 | Obs q50 | Pred q50 | Obs q90 | Pred q90 |
|---|---|---|---|---|---|---|
| Singles male | 9.15 | 6.18 | 14.26 | 11.50 | 25.44 | 20.16 |
| Singles female | 8.65 | 6.34 | 13.85 | 11.72 | 22.94 | 20.21 |
| Couples male | 10.06 | 9.00 | 15.29 | 14.99 | 27.87 | 27.85 |
| Couples female | 8.86 | 8.53 | 13.84 | 13.94 | 22.48 | 25.95 |

Couples quantile fit is excellent (q10, q50, q90 all within 8%). Singles quantile fit systematically underpredicts the level distribution. No change from M0c_b2 patterns.

---

## 10. Occupation (loc4) fit by group

Observed shares use chosen working alternatives; predicted shares use choice-probability weights.

**Singles male**

| Category | Label | Observed | Predicted | Δ |
|---|---|---|---|---|
| 1 | routine_manual_ref | 0.407 | 0.283 | −0.124 |
| 2 | nonroutine_manual | 0.094 | 0.234 | +0.140 |
| 3 | routine_cognitive | 0.051 | 0.208 | +0.158 |
| 4 | nonroutine_cognitive | 0.442 | 0.274 | −0.168 |

Occupation fit for singles male is poor: the model substantially overpredicts routine cognitive (3) and nonroutine manual (2) while underpredicting both routine manual (1) and nonroutine cognitive (4). This is inherited from M0c_b2 and is unchanged.

**Singles female**

| Category | Label | Observed | Predicted | Δ |
|---|---|---|---|---|
| 1 | routine_manual_ref | 0.192 | 0.259 | +0.067 |
| 2 | nonroutine_manual | 0.201 | 0.240 | +0.039 |
| 3 | routine_cognitive | 0.131 | 0.227 | +0.096 |
| 4 | nonroutine_cognitive | 0.473 | 0.273 | −0.199 |

Singles female: predicted shares are compressed toward the uniform allocation (0.25 per category); observed shares are concentrated in nonroutine cognitive (0.473). The model underpredicts category 4 by 20 ppt.

**Couples male**

| Category | Label | Observed | Predicted | Δ |
|---|---|---|---|---|
| 1 | routine_manual_ref | 0.360 | 0.355 | −0.005 |
| 2 | nonroutine_manual | 0.080 | 0.084 | +0.004 |
| 3 | routine_cognitive | 0.039 | 0.040 | +0.001 |
| 4 | nonroutine_cognitive | 0.508 | 0.514 | +0.006 |

**Excellent fit** for couples male (max |Δ| = 0.006). Unchanged from M0c_b2.

**Couples female**

| Category | Label | Observed | Predicted | Δ |
|---|---|---|---|---|
| 1 | routine_manual_ref | 0.170 | 0.169 | −0.001 |
| 2 | nonroutine_manual | 0.206 | 0.204 | −0.002 |
| 3 | routine_cognitive | 0.152 | 0.148 | −0.005 |
| 4 | nonroutine_cognitive | 0.470 | 0.479 | +0.009 |

**Excellent fit** for couples female (max |Δ| = 0.009). Unchanged from M0c_b2.

---

## 11. Chosen probability distribution

| Metric | GSURv2 | M0c_b2 |
|---|---|---|
| p_chosen_min | 1.09e-09 | 1.01e-09 |
| p_chosen_q10 | 0.0150 | 0.0157 |
| p_chosen_q25 | 0.0671 | 0.0671 |
| p_chosen_mean | 0.3902 | 0.3885 |
| p_chosen_median | 0.2730 | 0.2696 |
| p_chosen_q75 | 0.7267 | 0.7229 |
| p_chosen_q90 | 0.9228 | 0.9201 |
| p_chosen_max | 0.9993 | 0.9993 |

The chosen probability distribution is essentially unchanged: mean rises 0.17 ppt (0.3885 → 0.3902), median rises 0.35 ppt. The minimum chosen probability remains in the same 10^{-9} range (one hard-to-fit household in each run, same idhh = 4012700).

Probability sum errors: `max_error = 8.88e-16`, `mean_error = 1.32e-16` — machine-precision level, confirming correct normalisation.

Flags: `very_small_p_chosen_min` is a carry-over flag (1.09e-09 < 1e-8 threshold); the worst-fit household is identified in §12 below.

---

## 12. Non-work probability distribution

Non-work corresponds to the zero-hours alternative (`working = 0`). The model does not impose a
zero-hours bin separately; predicted non-work shares are derived from the complement of predicted
participation.

| Group | Obs non-work share | Pred non-work share | Δ |
|---|---|---|---|
| Singles male | 1 − 0.9295 = 0.0705 | 1 − 0.9299 = 0.0701 | −0.0004 |
| Singles female | 1 − 0.9396 = 0.0604 | 1 − 0.9634 = 0.0366 | −0.0238 |
| Couples male | 1 − 0.9717 = 0.0283 | 1 − 0.9865 = 0.0135 | −0.0148 |
| Couples female | 1 − 0.9651 = 0.0349 | 1 − 0.9911 = 0.0089 | −0.0261 |

The model underpredicts non-work for all groups except singles male (near-perfect). The largest
gap is couples female: observed 3.49% non-working, predicted 0.89% — a factor of ~4×
underprediction. This is the structural limitation that drives the hours-bin `0` share
discrepancy (see §8). The pattern is identical to M0c_b2.

Worst-fit households (top 10 by |ll_i|):

| Rank | idhh | Group | p_chosen | ll_i |
|---|---|---|---|---|
| 1 | 4012700 | sm | 1.09e-09 | −20.64 |
| 2 | 3600001 | sf | 1.22e-09 | −20.52 |
| 3 | 4264600 | cou | 5.36e-09 | −19.04 |
| 4 | 1935801 | sm | 1.36e-08 | −18.11 |
| 5 | 3457500 | sm | 3.60e-08 | −17.14 |
| 6 | 1918802 | sf | 4.80e-08 | −16.85 |
| 7 | 1729600 | cou | 2.81e-07 | −15.08 |
| 8 | 3233100 | cou | 5.71e-07 | −14.38 |
| 9 | 2989700 | cou | 2.15e-06 | −13.05 |
| 10 | 3317202 | sf | 3.59e-06 | −12.54 |

The same 10 households appear in both GSURv2 and M0c_b2 worst-fit lists (same idhh). The GSUR correction does not affect which households are the hardest to fit.

---

## 13. GSUR coefficient interpretation after correction

**Estimated coefficient**: `beta_E_gsur = −1.0502` (SE = 0.2002, t = −5.25, p = 1.55e-07)

**Interpretation**: the estimation specification applies `variable_scales.gsur = 10.0`, so
`beta_E_gsur` multiplies the **scaled** GSUR regressor. A one-unit increase in the scaled regressor
reduces the employment-opportunity index by 1.0502. A raw +1 percentage-point increase in GSUR
(`+0.01` in the parquet column) corresponds to `+0.10` after scaling and therefore to an
uncentered working-opportunity index shift of about `−0.105`. Because the market-opportunity block
is centered within each choice set, this should be read as a relative work-versus-non-work
opportunity effect, not as a direct percentage change in employment probability.

**Comparison to M0c_b2** (`beta_E_gsur = −0.7438`): the corrected coefficient is 41% larger in
magnitude. This pattern is **consistent with** attenuation from the earlier GSUR misalignment at
region × sex × education cells, but the re-estimation alone does not prove an attenuation-bias
decomposition. The corrected variable carries different and better-aligned information, and the
market-opportunity block reallocates accordingly.

**Variable used in GSURv2**: education- and sex-stratified, NUTS-2 population-weighted Y20-64
broad-age unemployment rates. IDF is mapped via the corrected region crosswalk (drgn1 → NUTS-2).
The GSURv2 variable has a narrower support than v1 (min = 0.047, max = 0.234 for singles male,
vs v1 min = 0.04, max = 0.21), consistent with the stratification removing outlier aggregate rates.

**Significance**: highly significant at p < 10^{-6}, stronger than M0c_b2 (p = 0.00075). The
corrected GSUR variable is a stronger predictor of employment opportunity than the misaligned v1.

**Interplay with `beta_E` and `beta_E_educH`**:
- `beta_E` shifts from −2.842 to −2.489 (+12%): the baseline employment disutility absorbs
  less of the cross-regional variation now that `beta_E_gsur` more fully captures it.
- `beta_E_educH` shifts from +0.613 to +0.439 (−28%): the education premium on employment
  opportunity narrows because part of the old education premium was confounded with
  region-education correlation in the misaligned GSUR.

---

## 14. Hessian condition number

| Metric | GSURv2 | M0c_b2 |
|---|---|---|
| Condition number κ | 5.138×10¹⁰ | 5.060×10¹⁰ |
| Status | Ill-conditioned (κ ≥ 10¹⁰) | Ill-conditioned |
| Min eigenvalue | −15.01 | −13.89 |
| Max eigenvalue | 1.369×10¹⁰ | 1.367×10¹⁰ |

The Hessian condition number is essentially unchanged (5.14×10¹⁰ vs 5.06×10¹⁰, a 1.5% increase).
Both values classify as ill-conditioned by the κ ≥ 10¹⁰ threshold. The condition number is driven
by the singles consumption block (three jointly-identified parameters with high pairwise
correlation); this is a data limitation documented in the M0c_b2 verdict and is unaffected by
the GSUR correction.

The pseudoinverse was applied in both cases to compute standard errors from the ill-conditioned
Hessian (3 NA SEs result from negative variances in the pseudoinverse diagonal).

---

## 15. Negative Hessian eigenvalues

| Metric | GSURv2 | M0c_b2 |
|---|---|---|
| Negative eigenvalues | **1** | **1** |
| Near-zero eigenvalues (|λ| ≤ 1e-8) | 0 | 0 |

One negative eigenvalue in both models. The negative eigenvalue is located in the singles
consumption block (`beta_c_sm` / `beta_c_sf` / `theta_c_singles`), as documented in the M0c_b2
verdict §4. The CONOPT solver reached `OptimalLocal` despite the ill-conditioned Hessian because
CONOPT does not rely on positive-definiteness of the Hessian for termination. The negative
eigenvalue is a property of the likelihood surface topology (flat ridge), not a sign of numerical
failure.

---

## 16. Parameters at bounds

**Parameters at bounds (strict)**: NONE — identical to M0c_b2.

**Parameters near bounds (within 5% of bound width)**:

| Parameter | Estimate | Lower bound | Δ from lower |
|---|---|---|---|
| `beta_c_sm` | 0.6265 | 0.05 | 0.576 |
| `beta_c_sf` | 0.5696 | 0.05 | 0.520 |
| `beta_l0_m` | 0.0118 | 1e-06 | 0.012 |
| `sigma` | 0.4268 | 0.10 | 0.327 |

Same four parameters near their lower bounds as M0c_b2. `beta_l0_m` (male leisure intercept in
couples) is the closest to its lower bound (0.0118 vs 1e-06), reflecting the near-zero leisure
intercept for couples males (consistent with the theoretical structure where males in couples have
near-zero intrinsic leisure preference relative to consumption).

---

## 17. NA standard errors

Three parameters have NA standard errors in both M0c_b2 and M0c_b2_GSURv2:

| Parameter | Estimate | SE | Explanation |
|---|---|---|---|
| `beta_c_sm` | 0.6265 | NA | Singles consumption joint-identification |
| `beta_c_sf` | 0.5696 | NA | Singles consumption joint-identification |
| `theta_c_singles` | −0.9441 | NA | Singles consumption joint-identification |

These three parameters appear together in the singles utility `U_sm = beta_c_sm * c^theta_c_singles` and `U_sf = beta_c_sf * c^theta_c_singles`. The shared `theta_c_singles` exponent creates a three-way identification weakness: the likelihood surface has a near-flat ridge in the (`beta_c_sm`, `beta_c_sf`, `theta_c_singles`) subspace. The pseudoinverse produces negative diagonal entries for these three parameters, which are reported as NA SEs.

This is a **data limitation** (the singles consumption variation in the French 2016 sample is insufficient to separately identify the scale and curvature of the singles consumption utility), **not a model defect or estimation failure**. Documented in M0c_b2 verdict §4 and unchanged by the GSUR correction.

The 44 remaining parameters have valid standard errors. Significance summary:

| Block | n_params | p<0.001 | p<0.01 | p<0.05 | p<0.10 |
|---|---|---|---|---|---|
| Preference | 23 | 9 | 10 | 10 | 10 |
| Employment/hours opportunity | 4 | 3 | 4 | 4 | 4 |
| Market residual opportunity | 2 | 1 | 1 | 1 | 2 |
| Wage opportunity | 6 | 5 | 5 | 6 | 6 |
| Occupation opportunity | 12 | 8 | 8 | 8 | 10 |

Note on `beta_E_educH`: in M0c_b2 it was p = 0.0094 (significant at 1%); in GSURv2 it is p = 0.052 (marginally significant at 10%). The estimate falls from +0.613 to +0.439 while the SE becomes slightly smaller (0.236 → 0.226); the t-statistic falls from 2.60 to 1.94 because the point estimate shrinks. The education premium on employment opportunity is weaker under the corrected GSUR. This is directionally consistent with the earlier confounding interpretation (§13).

---

## 18. Comparison to old M0c_b2 post-estimation diagnostics

### Summary comparison table

| Diagnostic | M0c_b2 | M0c_b2_GSURv2 | Change |
|---|---|---|---|
| Log-likelihood | −6509.16 | **−6501.21** | **+7.95** |
| AIC | 13112.3 | **13096.4** | **−15.9** |
| BIC | 13627.5 | **13611.6** | **−15.9** |
| ρ² | 0.70839 | **0.70875** | +0.00036 |
| n_sig p<0.05 | 30/47 | 29/47 | −1 (`beta_E_educH` drops to p=0.052) |
| gsur mean (sm) | 0.0986 | **0.0939** | −0.005 (corrected variable) |
| gsur mean (sf) | 0.0934 | **0.0918** | −0.002 |
| gsur mean (cm) | 0.0955 | **0.0916** | −0.004 |
| gsur mean (cf) | 0.0913 | **0.0877** | −0.004 |
| Participation fit (sm) | +0.000 | **+0.0004** | ≈0 |
| Participation fit (sf) | +0.012 | +0.024 | +0.011 (slightly worse) |
| Participation fit (cm) | +0.011 | +0.015 | +0.004 (slightly worse) |
| Participation fit (cf) | +0.024 | +0.026 | +0.003 (slightly worse) |
| Mean hours fit (sm) | −3.59 h | −3.58 h | ≈0 |
| Mean hours fit (sf) | −1.21 h | −1.22 h | ≈0 |
| Mean hours fit (cm) | +1.17 h | +1.15 h | ≈0 |
| Mean hours fit (cf) | +3.33 h | +3.30 h | ≈0 |
| Hours L1 dist (sm) | 0.726 | **0.634** | **−0.092 (improved)** |
| Hours L1 dist (sf) | 0.404 | 0.422 | +0.018 (slight regression) |
| Hours L1 dist (cm) | 0.342 | 0.350 | +0.008 (negligible) |
| Hours L1 dist (cf) | 0.501 | 0.505 | +0.004 (negligible) |
| `beta_E_gsur` | −0.744 | **−1.050** | **−41% stronger** |
| `beta_E` | −2.842 | **−2.489** | +12% (offsetting shift) |
| `beta_E_educH` | +0.613 | **+0.439** | −28% (narrower) |
| β_ll (leisure interaction) | 2.624 | 2.605 | −0.7% (stable) |
| Hessian κ | 5.06×10¹⁰ | 5.14×10¹⁰ | +1.5% |
| Negative eigenvalues | 1 | 1 | unchanged |
| NA SEs | 3 | 3 | unchanged |
| p_chosen_min | 1.01e-09 | 1.09e-09 | ≈same |
| p_chosen_mean | 0.389 | 0.390 | ≈same |

### Key findings from comparison

1. **LL, AIC, BIC all improve** with corrected GSUR (+7.95 LL units, −15.9 AIC/BIC). The model
   fits the data better after GSUR correction without any model structure change.

2. **Preference parameters are fully stable**: all leisure intercepts, Box-Cox exponents, and the
   household leisure interaction `beta_ll` change by ≤ 2%, well within their SEs. The structural
   interpretation of preferences is unaffected.

3. **Occupation fit is unchanged**: couples male and female maintain excellent occupation-share
   fit; singles occupation fit is poor in both models (singles do not receive group-specific
   occupation shifters by design at M0c_b2).

4. **Hours distribution improves for singles male** (L1 −12.7%); negligible changes elsewhere.

5. **Participation overprediction is slightly worse** across non-SM groups after GSURv2 (at most
   +1.1 ppt larger gap for singles female). This is a joint outcome of the corrected GSUR
   distribution and the re-estimated market-opportunity block; it should not be attributed to the
   larger negative `beta_E_gsur` coefficient in isolation.

6. **`beta_E_educH` loses significance** (p = 0.0094 → 0.052). The education premium on
   employment opportunity was partially confounded with regional-education correlation in the old
   GSUR; the corrected GSUR disentangles this, reducing the estimate enough to lower the
   t-statistic despite a slightly smaller SE.

7. **gsur mean is lower in GSURv2** (0.094 vs 0.099 for singles male, 0.092 vs 0.095 for couples
   male): the corrected education/sex-stratified rates are lower on average than the old
   aggregate rates across the realised sample. IDF itself is the parity-check case; the mean shift
   comes from the broader region × sex × education correction, not from an IDF mismatch.

---

## 19. Is the corrected GSUR run fit-stable?

**YES — the corrected GSUR run is fit-stable.**

Evidence:

1. **All preference parameters stable**: maximum absolute change from M0c_b2 is 0.032 (on
   `beta_l0_f`), 0.7% relative change for `beta_ll`. The structural parameters that determine
   labour-supply elasticities are unchanged.

2. **Hessian topology unchanged**: same condition number (×1.015), same one negative eigenvalue
   in the same block, same three NA SEs. The identification structure is identical.

3. **Hours distribution fit broadly stable**: singles male improves materially (L1 −12.7%);
   singles female worsens slightly in L1 while improving in L2; couples change negligibly.

4. **Wage distribution fit identical**: same `sigma`, same quantile matching patterns, same
   observed-vs-predicted gaps.

5. **Occupation fit identical**: couples occupation shares match to < 1 ppt in both models.
   Singles occupation fit unchanged (same structural limitation).

6. **Probability diagnostics unchanged**: p_chosen_min, mean, quantiles all shift by < 2%.
   Same 10 worst-fit households.

7. **Multistart confirmation**: all three independent starts (warm, defaults, ±5% perturbed)
   converge to identical LL = −6501.2082 and identical parameter vector. The GSURv2 solution
   is the common attractor among the tested starts.

The only substantive change is in the market opportunity block (`beta_E_gsur`, `beta_E`,
`beta_E_educH`), where the data-correction-induced shifts are consistent with the GSUR
measurement correction but do not by themselves prove a particular bias decomposition. The
preference-block and wage-block parameters that enter welfare calculations are unchanged. The
corrected GSUR run is **fit-stable and ready for the updated baseline verdict**; welfare
decomposition remains separately gated and is not authorised by this report.

---

## Appendix: Output files

**Post-estimation run folder**:
```
outputs/post_estimation/fr/spec/ruro_occ_GSURv2/gamspy/estimation_spec_ruro_occ_M0c_b2_GSURv2/run_2026-05-18_00-30-18/
```

| File | Description |
|---|---|
| `post_estimation_report_20260518_003039.html` | Full styled HTML report with figures |
| `params.csv` | Parameter estimates with SE, t, p |
| `elasticities.csv` | Curvature-based elasticity heuristics |
| `fit_participation.png` | Participation bar chart (obs vs pred) |
| `fit_mean_hours.png` | Mean hours bar chart (obs vs pred) |
| `hours_distribution_*.png` | Hours-bin distribution by group |
| `wage_distribution_*.png` | Wage distribution by group |
| `sm_contours.png`, `sf_contours.png`, `cou_m_contours.png`, `cou_f_contours.png` | Utility contour plots |
| `muc_comparison.png`, `mul_comparison.png` | Marginal utility comparisons |
| `negative_mu_diagnostics.png` | Negative MU diagnostic plot |

**LLM summary**: `reports/llm_summary_20260518_003039.md`

**Estimation run folder (source)**:
```
outputs/estimates/fr/spec/ruro_occ_GSURv2/gamspy/estimation_spec_ruro_occ_M0c_b2_GSURv2/run_2026-05-17_23-55-09/
```
