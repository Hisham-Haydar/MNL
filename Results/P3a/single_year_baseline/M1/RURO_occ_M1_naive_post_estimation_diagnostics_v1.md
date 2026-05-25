# RURO occ M1-naive Standard Post-Estimation Diagnostics v1

Date: 2026-05-18
Specification: `ruro_occ_M1_naive` (54 parameters)
Comparison baseline: `ruro_occ_M1_clean` (53 parameters)

Sources:
- LLM summary: `reports/llm_summary_20260518_185053.md`
- Params CSV: `outputs/post_estimation/fr/spec/ruro_occ_M1_naive/gamspy/estimation_spec_ruro_occ_M1_naive/run_2026-05-18_18-50-21/params.csv`
- HTML report: `outputs/post_estimation/fr/spec/ruro_occ_M1_naive/gamspy/estimation_spec_ruro_occ_M1_naive/run_2026-05-18_18-50-21/post_estimation_report_20260518_185053.html`

---

## 1. Exact Command Run

```text
python scripts/enhanced/RURO_post_estimation_styled.py \
  --results-json "outputs/estimates/fr/spec/ruro_occ_M1_naive/gamspy/estimation_spec_ruro_occ_M1_naive/run_2026-05-18_17-50-20/estimation_results.json" \
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2" \
  --output-dir "outputs/post_estimation/fr/spec/ruro_occ_M1_naive/gamspy" \
  --spec-config "scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_naive.yaml" \
  --auto-timestamp \
  --llm-summary-dir reports
```

Invoked via wrapper `C:\Users\hisham\AppData\Local\Temp\run_m1naive_postestim.py` (local CWD required by pipeline). Script exited with return code 0. 26 output files written.

---

## 2. Selected Estimation Run Folder

```text
outputs/estimates/fr/spec/ruro_occ_M1_naive/gamspy/estimation_spec_ruro_occ_M1_naive/run_2026-05-18_17-50-20/
```

Start 1 (warm start from M1-clean + `beta_E_educH = 0.4386`). Selected on fewest solver iterations (10) and warm-start coherence. All three M1-naive starts converge to LL = −6485.5287 (identical parameter vector verified).

---

## 3. Exact Results JSON Used

```text
outputs/estimates/fr/spec/ruro_occ_M1_naive/gamspy/estimation_spec_ruro_occ_M1_naive/run_2026-05-18_17-50-20/estimation_results.json
```

54 parameters. Specification: `ruro_occ_M1_naive`. Joint estimation (singles male + singles female + couples).

---

## 4. Exact `--mnl-base` Used

```text
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2
```

Post-estimation script loaded:
- `fr_2016_RURO_mnl_GSURv2__singles.parquet` — 167,600 rows, 81 columns
- `fr_2016_RURO_mnl_GSURv2__couples.parquet` — 257,700 rows, 105 columns

Canonical (non-GSURv2) parquets were **not** used. Confirmed by `mnl_base` entry in LLM summary.

---

## 5. GSURv2 Metadata Sidecar

```text
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2__mnlmeta.json
```

**Present** — confirmed via `Test-Path` before running post-estimation. Proposal and prior diagnostics: max abs log-prior minus log-density = 0 (singles and couples); missing aliases: none; forbidden columns present: none. No sidecar-related errors in any run.

---

## 6. Observed vs Predicted Participation by Group

| Group | Observed | Predicted | Δ (ppt) | Direction |
|-------|---------|-----------|---------|-----------|
| Singles male (sm) | 0.9295 | 0.9003 | **−2.92 ppt** | Underpredicts |
| Singles female (sf) | 0.9396 | 0.9483 | +0.87 ppt | Slight overprediction |
| Couples male (cm) | 0.9717 | 0.9809 | +0.93 ppt | Overpredicts |
| Couples female (cf) | 0.9651 | 0.9871 | **+2.19 ppt** | Overpredicts (structural) |

Notable change from M1-clean: the sm participation underprediction worsens from −0.88 ppt (M1-clean) to −2.92 ppt (M1-naive). The `beta_E_educH` term adds an additional positive shift to the employment-opportunity index for high-education individuals, raising predicted participation for those groups. The net effect on sm is a further increase in predicted non-employment mass. For sf, participation fit improves (from +1.94 ppt overprediction in M1-clean to +0.87 ppt). The cf structural overprediction (near-universal employment in couples female) persists and is slightly reduced relative to M1-clean (+2.44 ppt), consistent with `beta_E` falling to −2.914 (more negative base employment opportunity offsetting the education gain).

---

## 7. Observed vs Predicted Mean Hours by Group

| Group | Observed (h) | Predicted (h) | Δ (h) | vs M1-clean Δ |
|-------|-------------|--------------|-------|--------------|
| Singles male | 39.30 | 35.76 | −3.55 | negligible (M1-clean: −3.55) |
| Singles female | 36.30 | 35.10 | −1.20 | negligible (M1-clean: −1.20) |
| Couples male | 41.61 | 42.73 | +1.12 | negligible (M1-clean: +1.11) |
| Couples female | 35.65 | 38.93 | +3.28 | negligible (M1-clean: +3.26) |

Mean hours fit is essentially unchanged from M1-clean (maximum change 0.02 h across all groups). Adding `beta_E_educH` does not alter the hours-distribution first moment.

---

## 8. Hours-Bin Fit by Group

| Group | M1-naive L1 | M1-clean L1 | M0c_b2_GSURv2 L1 | Δ(naive − clean) | Direction |
|-------|------------|------------|-----------------|-----------------|-----------|
| Singles male | **0.7781** | 0.6945 | 0.6345 | **+0.084** | **Further regression** |
| Singles female | 0.4132 | 0.4176 | 0.4220 | −0.004 | ≈same |
| Couples male | 0.3329 | 0.3446 | 0.3500 | −0.012 | Small improvement |
| Couples female | 0.4959 | 0.4998 | 0.5050 | −0.004 | ≈same |

The singles-male hours-bin L1 distance worsens further from M1-clean (0.694 → 0.778, +12.1% relative to M1-clean; +22.6% relative to M0c\_b2\_GSURv2). The cause is the same mechanism as in M1-clean — all-positive region dummies shift mass into the 21–30 h bin — amplified by the additional positive `beta_E_educH` term for high-education individuals. The observed sm distribution has 48% of workers in the 31–40 h bin; the model predicts only 30% there and 62% in the 21–30 h bin (vs observed 26%). This is the largest quantitative regression relative to M1-clean.

Key hours-bin shares (sm):

| Bin | Observed | M1-naive pred | M1-clean pred |
|-----|---------|--------------|--------------|
| 0 (non-work) | 7.05% | 0% | 0% |
| 11–20 h | 4.83% | 7.57% | — |
| 21–30 h | 25.72% | **61.88%** | ~59% |
| 31–40 h | 48.04% | 30.03% | ~36% |
| 41–50 h | 7.70% | 0.26% | — |

For sf, cm, cf: hours-bin fit is essentially unchanged from M1-clean (L1 changes ≤ 0.012).

---

## 9. Wage Distribution Fit by Group

| Group | Obs mean €/h | Pred mean €/h | Δ% | Obs σ(log w) | Pred σ |
|-------|-------------|--------------|----|-----------|----|
| Singles male | 16.21 | 12.61 | −22% | 0.4502 | 0.4276 |
| Singles female | 15.11 | 12.75 | −16% | 0.4360 | 0.4276 |
| Couples male | 17.66 | 17.10 | −3% | 0.4402 | 0.4276 |
| Couples female | 15.17 | 15.93 | +5% | 0.4360 | 0.4276 |

Wage fit is **unchanged from M1-clean** in all dimensions. The Mincer block (`beta_w0`, `beta_w_educL`, `beta_w_educH`, `beta_w_pexp`, `beta_w_pexp2`) and `sigma` shift by ≤ 0.001 in absolute value between M1-clean and M1-naive. Quantile fit at q10/q50/q90:

| Group | Obs q10/q50/q90 | Pred q10/q50/q90 |
|-------|----------------|-----------------|
| Singles male | 9.15 / 14.26 / 25.44 | 6.18 / 11.49 / 20.17 |
| Singles female | 8.65 / 13.85 / 22.94 | 6.34 / 11.71 / 20.25 |
| Couples male | 10.06 / 15.29 / 27.87 | 9.00 / 14.97 / 27.75 |
| Couples female | 8.86 / 13.84 / 22.48 | 8.52 / 13.92 / 25.89 |

Singles wage underprediction (−22% for sm, −16% for sf) is a pre-existing structural limitation of the pooled Mincer specification, unchanged from both M0c\_b2\_GSURv2 and M1-clean.

---

## 10. loc4 Occupation Fit by Group

| Group | Occ cat | Observed | Predicted | |Δ| |
|-------|---------|---------|-----------|-----|
| Singles male | 1 (routine manual, ref) | 40.73% | 28.26% | 12.47% |
| Singles male | 2 (nonroutine manual) | 9.41% | 23.45% | 14.04% |
| Singles male | 3 (routine cognitive) | 5.06% | 20.89% | 15.84% |
| Singles male | 4 (nonroutine cognitive) | 44.24% | 27.37% | 16.87% |
| Singles female | 1 (routine manual, ref) | 19.18% | 25.86% | 6.68% |
| Singles female | 2 (nonroutine manual) | 20.12% | 23.99% | 3.87% |
| Singles female | 3 (routine cognitive) | 13.10% | 22.79% | 9.69% |
| Singles female | 4 (nonroutine cognitive) | 47.25% | 27.28% | **19.97%** |
| Couples male | 1 (routine manual, ref) | 36.02% | 35.71% | 0.31% |
| Couples male | 2 (nonroutine manual) | 8.03% | 8.38% | 0.35% |
| Couples male | 3 (routine cognitive) | 3.91% | 3.91% | 0.00% |
| Couples male | 4 (nonroutine cognitive) | 50.80% | 51.26% | 0.47% |
| Couples female | 1 (routine manual, ref) | 17.01% | 17.14% | 0.13% |
| Couples female | 2 (nonroutine manual) | 20.63% | 20.33% | 0.30% |
| Couples female | 3 (routine cognitive) | 15.24% | 14.75% | 0.49% |
| Couples female | 4 (nonroutine cognitive) | 47.00% | 47.73% | 0.72% |

Occupation fit is **unchanged from M1-clean**. Couples shares are excellent (max |Δ| = 0.72% for cf, 0.47% for cm). Singles shares remain poor: sm over-predicts routine cognitive (cat 3) by 15.8 ppt and under-predicts nonroutine cognitive (cat 4) by 16.9 ppt; sf under-predicts nonroutine cognitive (cat 4) by 20.0 ppt. These are inherited limitations from M0c\_b2\_GSURv2 and M1-clean; they reflect the model's insufficient within-group occupation heterogeneity for singles and are not caused by `beta_E_educH`.

---

## 11. Chosen Probability Distribution

| Metric | M1-naive | M1-clean | Change |
|--------|---------|---------|--------|
| p\_chosen\_min | 1.137×10⁻⁹ | 1.161×10⁻⁹ | negligible |
| p\_chosen\_q10 | 0.01610 | 0.01528 | +0.001 |
| p\_chosen\_q25 | 0.06708 | 0.06649 | +0.001 |
| p\_chosen\_mean | 0.38810 | 0.38982 | −0.002 |
| p\_chosen\_median | 0.26933 | 0.27221 | −0.003 |
| p\_chosen\_q75 | 0.72275 | 0.72569 | −0.003 |
| p\_chosen\_q90 | 0.92006 | 0.92252 | −0.002 |
| p\_chosen\_max | 0.99931 | 0.99934 | negligible |

Probability normalisation: max error = 7.77×10⁻¹⁶, mean error = 1.27×10⁻¹⁶ — machine precision, confirming correct normalisation across all 4,253 choice sets.

One flag: minimum chosen probability = 1.137×10⁻⁹ (below threshold 1×10⁻⁸). Same household as M0c\_b2\_GSURv2 and M1-clean (idhh = 4012700, singles male group). Not newly introduced by M1-naive.

The chosen-probability distribution is essentially unchanged from M1-clean across all quantiles (all differences < 0.003). The second worst-fit household (idhh = 3600001, sf) is also unchanged.

---

## 12. Non-Work Probability Distribution

| Group | Obs non-work | Pred non-work | Δ | vs M1-clean |
|-------|-------------|--------------|---|------------|
| Singles male | 7.05% | 9.97% | +2.92 ppt | M1-clean: +0.88 ppt (worsened) |
| Singles female | 6.04% | 5.17% | −0.87 ppt | M1-clean: −1.94 ppt (improved) |
| Couples male | 2.83% | 1.91% | −0.92 ppt | M1-clean: −1.29 ppt (improved) |
| Couples female | 3.49% | 1.29% | **−2.19 ppt** | M1-clean: −2.44 ppt (slightly improved) |

Non-work probabilities are the mirror of participation fit (§6). The worsening of sm non-work prediction (+2.92 ppt overprediction vs M1-clean's +0.88 ppt) is the most notable change. The cf structural underprediction of non-employment (predicted 1.29% vs observed 3.49%) is slightly better than M1-clean (1.04% predicted), but both models severely under-predict non-employment for couples female.

---

## 13. Parameter Table with Standard Errors

Full 54-parameter table (from `params.csv`):

| Block | Parameter | Estimate | SE | t | p | Sig |
|-------|-----------|----------|-----|---|---|-----|
| **Preference** | | | | | | |
| | `beta_l0_sm` | 3.8164 | 0.6903 | 5.529 | 3.2×10⁻⁸ | *** |
| | `beta_l_age_sm` | 0.00466 | 0.02464 | 0.189 | 0.850 | — |
| | `beta_l_age2_sm` | 0.00186 | 0.00206 | 0.902 | 0.367 | — |
| | `beta_c_sm` | 0.5496 | NA | NA | NA | NA |
| | `theta_l_sm` | −0.7128 | 0.1502 | −4.745 | 2.1×10⁻⁶ | *** |
| | `beta_l0_sf` | 4.4586 | 0.7624 | 5.848 | 5.0×10⁻⁹ | *** |
| | `beta_l_age_sf` | 0.000408 | 0.02687 | 0.015 | 0.988 | — |
| | `beta_l_age2_sf` | 0.00391 | 0.00252 | 1.554 | 0.120 | — |
| | `beta_l_nkids_sf` | −0.08586 | 0.34420 | −0.249 | 0.803 | — |
| | `beta_c_sf` | 0.5020 | NA | NA | NA | NA |
| | `theta_l_sf` | −0.7228 | 0.1309 | −5.520 | 3.4×10⁻⁸ | *** |
| | `theta_c_singles` | −1.0518 | NA | NA | NA | NA |
| | `beta_l0_m` | 0.01212 | 0.2887 | 0.042 | 0.967 | — |
| | `beta_l_age_m` | −0.00967 | 0.01525 | −0.634 | 0.526 | — |
| | `beta_l_age2_m` | 0.000863 | 0.001479 | 0.583 | 0.560 | — |
| | `theta_l_m` | −0.7319 | 0.1393 | −5.254 | 1.5×10⁻⁷ | *** |
| | `beta_l0_f` | 2.6033 | 0.4362 | 5.968 | 2.4×10⁻⁹ | *** |
| | `beta_l_age_f` | −0.05971 | 0.02259 | −2.644 | 0.0082 | ** |
| | `beta_l_age2_f` | 0.002948 | 0.002238 | 1.318 | 0.188 | — |
| | `beta_l_nkids_f` | 0.16361 | 0.21465 | 0.762 | 0.446 | — |
| | `theta_l_f` | −0.6778 | 0.09157 | −7.401 | 1.3×10⁻¹³ | *** |
| | `beta_c` | 3.9918 | 0.1442 | 27.67 | 0 | *** |
| | `beta_ll` | 2.6187 | 0.3506 | 7.469 | 8.1×10⁻¹⁴ | *** |
| **Employment / hours opportunity** | | | | | | |
| | `beta_E` | −2.9138 | 0.3026 | −9.631 | 0 | *** |
| | `beta_h_pt1` | −0.5005 | 0.1091 | −4.588 | 4.5×10⁻⁶ | *** |
| | `beta_h_pt2` | 0.3728 | 0.1118 | 3.334 | 0.0009 | *** |
| | `beta_h_ft` | 1.4497 | 0.05027 | 28.84 | 0 | *** |
| **Market residual opportunity** | | | | | | |
| | `beta_E_gsur` | −1.0479 | 0.2197 | −4.770 | 1.8×10⁻⁶ | *** |
| | `beta_E_educH` | 0.4503 | 0.2323 | 1.938 | 0.0526 | (.) |
| | `beta_E_drgn2` | 0.8215 | 0.2671 | 3.076 | 0.0021 | ** |
| | `beta_E_drgn3` | 0.5563 | 0.3222 | 1.727 | 0.0842 | (.) |
| | `beta_E_drgn4` | 1.5422 | 0.4114 | 3.749 | 0.0002 | *** |
| | `beta_E_drgn5` | 0.8062 | 0.2735 | 2.948 | 0.0032 | ** |
| | `beta_E_drgn6` | 0.7780 | 0.3282 | 2.370 | 0.0178 | * |
| | `beta_E_drgn7` | 0.6591 | 0.3114 | 2.117 | 0.0343 | * |
| | `beta_E_drgn8` | 0.4376 | 0.2806 | 1.560 | 0.1188 | — |
| **Wage opportunity** | | | | | | |
| | `beta_w0` | 2.0184 | 0.02580 | 78.24 | 0 | *** |
| | `beta_w_educL` | −0.04445 | 0.02140 | −2.077 | 0.0378 | * |
| | `beta_w_educH` | 0.32013 | 0.01514 | 21.14 | 0 | *** |
| | `beta_w_pexp` | 0.018536 | 0.002252 | 8.229 | 2.2×10⁻¹⁶ | *** |
| | `beta_w_pexp2` | −0.000228 | 4.99×10⁻⁵ | −4.564 | 5.0×10⁻⁶ | *** |
| | `sigma` | 0.42762 | 0.004177 | 102.4 | 0 | *** |
| **Occupation opportunity** | | | | | | |
| | `beta_occ_2_sm` | −1.4743 | 0.1425 | −10.35 | 0 | *** |
| | `beta_occ_3_sm` | −2.1299 | 0.1845 | −11.55 | 0 | *** |
| | `beta_occ_4_sm` | 0.05966 | 0.08667 | 0.688 | 0.491 | — |
| | `beta_occ_2_sf` | 0.05517 | 0.1142 | 0.483 | 0.629 | — |
| | `beta_occ_3_sf` | −0.4963 | 0.1303 | −3.807 | 0.0001 | *** |
| | `beta_occ_4_sf` | 0.8623 | 0.09395 | 9.179 | 0 | *** |
| | `beta_occ_2_cm` | −1.4961 | 0.1140 | −13.12 | 0 | *** |
| | `beta_occ_3_cm` | −2.2539 | 0.1490 | −15.13 | 0 | *** |
| | `beta_occ_4_cm` | 0.45565 | 0.06929 | 6.576 | 4.8×10⁻¹¹ | *** |
| | `beta_occ_2_cf` | 0.13110 | 0.1014 | 1.293 | 0.196 | — |
| | `beta_occ_3_cf` | −0.25322 | 0.1127 | −2.247 | 0.0246 | * |
| | `beta_occ_4_cf` | 1.07960 | 0.08208 | 13.15 | 0 | *** |

Significance codes: `***` p < 0.001, `**` p < 0.01, `*` p < 0.05, `(.)` p < 0.10, `—` p ≥ 0.10, `NA` negative variance.

**Block significance summary:**

| Block | n params | n estimable | p < 0.05 | p ≥ 0.05 | NA SE |
|-------|---------|------------|---------|---------|-------|
| Preference | 23 | 20 | 10 | 10 | 3 |
| Employment/hours opportunity | 4 | 4 | 4 | 0 | 0 |
| Market residual opportunity | 9 | 9 | 6 | 3 | 0 |
| Wage opportunity | 6 | 6 | 6 | 0 | 0 |
| Occupation opportunity | 12 | 12 | 9 | 3 | 0 |
| **Total** | **54** | **51** | **35** | **13** | **3** |

35 of 51 estimable parameters significant at 5% (68.6%). This matches M1-clean (35/50 = 70%).

---

## 14. Hessian Condition Number

| Metric | M1-naive | M1-clean | Change |
|--------|---------|---------|--------|
| Condition number κ | **5.148×10¹⁰** | 5.096×10¹⁰ | +1.0% |
| Classification | Ill-conditioned (κ ≥ 10¹⁰) | Ill-conditioned | unchanged |
| Min eigenvalue | −36.30 | −35.60 | slightly more negative |
| Max eigenvalue | 1.341×10¹⁰ | — | — |

The Hessian remains ill-conditioned. The 1% increase in κ relative to M1-clean is negligible. The minimum eigenvalue worsens marginally (−36.30 vs −35.60), consistent with the addition of one further parameter interacting with the collinear singles-consumption block through the shared opportunity index. CONOPT reaches `NormalCompletion / OptimalLocal` regardless.

---

## 15. Negative Eigenvalues

| Metric | M1-naive | M1-clean |
|--------|---------|---------|
| Negative eigenvalues | **1** | 1 |
| Near-zero eigenvalues (|λ| ≤ 1e-8) | 0 | 0 |

The single negative eigenvalue is unchanged in count from M1-clean. It is localised in the singles-consumption block (`beta_c_sm` / `beta_c_sf` / `theta_c_singles`), as confirmed by the high off-diagonal correlations in that block (up to −1.110). Adding `beta_E_educH` did not introduce a new negative direction in the Hessian.

---

## 16. Parameters at Bounds

**No parameters at strict bounds** (confirmed in post-estimation diagnostics: "Parameters At Bounds: None").

Four parameters are **near lower bounds** (within 5% of bound width), identical to M1-clean:

| Parameter | Estimate | Lower bound | Δ from bound |
|-----------|---------|------------|-------------|
| `beta_c_sm` | 0.5496 | 0.05 | 0.50 |
| `beta_c_sf` | 0.5020 | 0.05 | 0.45 |
| `beta_l0_m` | 0.01212 | 1×10⁻⁶ | 0.012 |
| `sigma` | 0.42762 | 0.10 | 0.33 |

No market-opportunity parameters are near any bound. `beta_E_educH` (0.4503) is well within its bounds [−10, 10].

---

## 17. NA Standard Errors

Three parameters have NA standard errors (identical to M0c\_b2\_GSURv2 and M1-clean):

| Parameter | Estimate | SE | Cause |
|-----------|---------|----|----|
| `beta_c_sm` | 0.5496 | NA | Singles consumption joint-identification ridge |
| `beta_c_sf` | 0.5020 | NA | Singles consumption joint-identification ridge |
| `theta_c_singles` | −1.0518 | NA | Singles consumption joint-identification ridge |

The pseudoinverse produces negative diagonal entries for these three parameters. This is a data limitation (insufficient singles consumption variation to separately identify two scale parameters and their shared exponent), inherited unchanged from M0c\_b2\_GSURv2. The three NA SEs are all in the preference block; **no market-opportunity parameter has an NA SE**. All nine market-residual opportunity parameters (`beta_E_gsur`, `beta_E_educH`, `beta_E_drgn2`–`beta_E_drgn8`) have valid standard errors.

Cross-parameter correlations exceeding |0.90| (pseudoinverse artefacts in the collinear block):

| Pair | Correlation |
|------|------------|
| `beta_c_sm` ↔ `beta_c_sf` | −1.110 |
| `beta_c_sf` ↔ `theta_c_singles` | −1.087 |
| `beta_c_sm` ↔ `theta_c_singles` | −1.068 |
| `beta_w_pexp` ↔ `beta_w_pexp2` | −0.960 |
| `beta_E` ↔ `beta_E_gsur` | −0.912 |

The `beta_E` ↔ `beta_E_gsur` correlation (−0.912) is a new entry relative to the M1-clean table and is expected: with `beta_E_educH` present, the base employment intercept `beta_E` and the GSUR coefficient share more of the employment-opportunity variation, increasing their co-movement in the Hessian. This is structurally coherent, not a collinearity alarm.

---

## 18. `beta_E_educH` Interpretation

| Source | Estimate | SE | t | p |
|--------|---------|----|----|---|
| M0c\_b2\_GSURv2 | 0.4386 | — | — | — |
| M1-naive (selected) | **0.4503** | **0.2323** | **1.938** | **0.0526** |

`beta_E_educH = 0.4503` is positive: higher-educated individuals (educH = 1) face a better employment-opportunity draw conditional on GSUR score and region. The estimate is stable and consistent with M0c\_b2\_GSURv2 (0.4386; difference of 0.012). The point estimate is robust across all three M1-naive estimation starts (unique attractor).

Statistical significance is **borderline**: Wald p ≈ 0.053, just above the 5% threshold. The LR test vs M1-clean gives χ²(1) = 4.047, p ≈ 0.044. Both inferential routes point to the same conclusion: marginal evidence for retaining `beta_E_educH` in the opportunity block. See §20 for the structural comparison.

The wage block also contains `beta_w_educH` (education in the ability/Mincer block, estimate 0.3201, p < 0.001). The two `educH` terms capture different mechanisms: `beta_w_educH` is the log-wage return to education (ability channel); `beta_E_educH` is the employment-opportunity premium for educated workers conditional on GSUR and region (opportunity channel). The model allows both to be present simultaneously (M1-naive) or only the ability channel (M1-clean). The adjudication of which specification is correct for the JMP welfare partition is the subject of the M1-naive robustness verdict.

---

## 19. `beta_E_gsur` Comparison to M1-clean

| Specification | `beta_E_gsur` | SE | t | p |
|---------------|-------------|----|----|---|
| M0c\_b2\_GSURv2 | −1.0502 | 0.2002 | −5.25 | 1.6×10⁻⁷ |
| M1-clean | −1.3289 | 0.1631 | −8.15 | 4.4×10⁻¹⁶ |
| M1-naive | **−1.0479** | **0.2197** | **−4.770** | **1.8×10⁻⁶** |

`beta_E_gsur` reverts from −1.3289 (M1-clean) to −1.0479 (M1-naive), recovering M0c\_b2\_GSURv2's value of −1.0502 to within 0.002. This is the key structural finding of M1-naive:

The 0.281-unit strengthening of `beta_E_gsur` in M1-clean (from −1.050 to −1.329) was caused entirely by the removal of `beta_E_educH`, which forced GSUR to absorb the education-on-opportunity signal. When `beta_E_educH` is restored (M1-naive), GSUR reverts to its M0c\_b2\_GSURv2 level. This implies that the education-GSUR interaction is important: GSUR and `educH` capture complementary but correlated variation in employment opportunity. In M1-clean, the GSUR coefficient represents "GSUR + absorbed education signal"; in M1-naive, it represents "GSUR alone, conditional on education".

The SE on `beta_E_gsur` widens slightly in M1-naive (0.2197 vs 0.1631 in M1-clean), consistent with the partition of variance between two correlated predictors. The `beta_E` ↔ `beta_E_gsur` correlation (−0.912) is higher in M1-naive than in M1-clean, reflecting increased co-movement in the opportunity intercept and GSUR coefficient when education absorbs some of the variation.

---

## 20. Region-Dummy Comparison to M1-clean

| Parameter | M1-clean | M1-clean SE | M1-naive | M1-naive SE | Δ(naive − clean) |
|-----------|---------|------------|---------|------------|-----------------|
| `beta_E_drgn2` | 0.8013 | 0.2664 | 0.8215 | 0.2671 | +0.020 |
| `beta_E_drgn3` | 0.6564 | 0.3186 | 0.5563 | 0.3222 | −0.100 |
| `beta_E_drgn4` | 1.5626 | 0.4100 | 1.5422 | 0.4114 | −0.020 |
| `beta_E_drgn5` | 0.7725 | 0.2722 | 0.8062 | 0.2735 | +0.034 |
| `beta_E_drgn6` | 0.7665 | 0.3275 | 0.7780 | 0.3282 | +0.012 |
| `beta_E_drgn7` | 0.6405 | 0.3118 | 0.6591 | 0.3114 | +0.019 |
| `beta_E_drgn8` | 0.4631 | 0.2794 | 0.4376 | 0.2806 | −0.026 |

All seven region dummies are stable: shifts ≤ 0.10 in absolute value, with `beta_E_drgn3` the largest mover (−0.100). No region dummy changes sign. The regional ordering is preserved (drgn4 > drgn2 ≈ drgn5 ≈ drgn6 > drgn3 ≈ drgn7 > drgn8 in both models). Standard errors are essentially unchanged (maximum SE change 0.004).

Individual significance in M1-naive: five of seven remain significant at 5% (`beta_E_drgn2`, `beta_E_drgn4`, `beta_E_drgn5`, `beta_E_drgn6`, `beta_E_drgn7`). `beta_E_drgn3` (North; p = 0.084) and `beta_E_drgn8` (Mediterranean; p = 0.119) are not individually significant at 5%, compared to M1-clean where six of seven were significant (only drgn8 failed at 5%). The weakening of drgn3 (from p = 0.039 in M1-clean to p = 0.084 in M1-naive) is consistent with `beta_E_educH` absorbing part of the North-region education correlation — a minor but real reallocation.

The joint region block test (Wald, 7 d.f.) is reported in the supplementary diagnostics step, not here.

---

## 21. Comparison to M1-clean Diagnostics

Summary comparison table:

| Diagnostic | M0c\_b2\_GSURv2 | M1-clean | M1-naive | Direction |
|-----------|----------------|---------|---------|-----------|
| Log-likelihood | −6501.21 | −6487.55 | −6485.53 | M1-naive +2.02 |
| AIC | 13096.4 | 13081.1 | **13079.1** | M1-naive better by 2.0 |
| BIC | 13611.6 | 13662.0 | **13670.9** | M1-naive worse by 8.9 |
| McFadden ρ² | 0.70875 | 0.70936 | **0.70945** | M1-naive +0.00009 |
| Parameters | 47 | 53 | 54 | +1 vs M1-clean |
| Valid SEs | 44/47 | 50/53 | 51/54 | +1 vs M1-clean |
| NA SEs | 3 | 3 | 3 | unchanged |
| p < 0.05 (estimable) | 29/44 | 35/50 | 35/51 | same count |
| Participation Δ (sm) | +0.04 ppt | −0.88 ppt | **−2.92 ppt** | **Worsened** |
| Participation Δ (sf) | +2.39 ppt | +1.94 ppt | +0.87 ppt | Improved |
| Participation Δ (cm) | +1.48 ppt | +1.29 ppt | +0.93 ppt | Improved |
| Participation Δ (cf) | +2.61 ppt | +2.44 ppt | +2.19 ppt | Improved |
| Hours-bin L1 (sm) | 0.634 | 0.695 | **0.778** | **Further regression** |
| Hours-bin L1 (sf) | 0.422 | 0.418 | 0.413 | ≈same |
| Hours-bin L1 (cm) | 0.350 | 0.345 | 0.333 | Small improvement |
| Hours-bin L1 (cf) | 0.505 | 0.500 | 0.496 | Small improvement |
| Occupation fit (cm/cf) | max |Δ| ≤ 0.007 | max |Δ| ≤ 0.007 | max |Δ| ≤ 0.007 | unchanged |
| Wage fit | unchanged | unchanged | unchanged | — |
| Hessian κ | 5.14×10¹⁰ | 5.10×10¹⁰ | 5.15×10¹⁰ | +1% vs M1-clean |
| Negative eigenvalues | 1 | 1 | 1 | unchanged |
| `beta_E_gsur` | −1.0502 | −1.3289 | **−1.0479** | Reverts to M0c level |
| `beta_E_educH` | 0.4386 | — | **0.4503** | Restored; p = 0.053 |

Key structural changes from M1-clean to M1-naive:

1. `beta_E_educH` re-introduced: 0.4503, t = 1.938, p = 0.053 — borderline significance.
2. `beta_E_gsur` reverts to M0c\_b2\_GSURv2 level (−1.048 vs −1.329 in M1-clean).
3. `beta_E` intercept falls to −2.914 (from −2.499 in M1-clean), compensating for the positive educH shift at the sample mean.
4. Singles-male participation fit worsens materially (−0.88 ppt → −2.92 ppt underprediction).
5. Singles-male hours-bin L1 worsens further (+12% relative to M1-clean).
6. Participation fit for sf, cm, cf all improve slightly.
7. AIC improves by 2.0 relative to M1-clean; BIC worsens by 8.9.
8. All preference, wage, occupation, and hours-opportunity parameters are stable (all shifts < 0.006 in absolute value for non-opportunity blocks).

---

## 22. Whether Standard Post-Estimation Completed Successfully

**Yes.** Post-estimation completed without errors:
- Return code: 0
- Output directory: `outputs/post_estimation/fr/spec/ruro_occ_M1_naive/gamspy/estimation_spec_ruro_occ_M1_naive/run_2026-05-18_18-50-21/`
- Files written: 26 (23 PNG figures, 1 HTML report, `params.csv`, `elasticities.csv`)
- LLM summary written: `reports/llm_summary_20260518_185053.md`
- No exception tracebacks; no file write failures
- Probability normalisation: machine precision (max error 7.77×10⁻¹⁶)
- Marginal utilities: all positive and well-behaved across all 4,253 households (0 negative MUC, 0 negative MUL)

**Post-estimation pipeline warnings** (non-fatal, all pre-existing):
- `ill-conditioned Hessian (κ ≥ 10¹⁰); 1 negative eigenvalue` — inherited from M0c\_b2\_GSURv2 and M1-clean
- `minimum chosen probability is very small (1.137×10⁻⁹)` — same household as prior specifications
- `negative eigenvalues present; inspect SE and local optimum diagnostics` — same singles-consumption block as prior specifications
- `No job_id columns found for job distribution plots` — expected (GSURv2 MNL base does not carry job-level identifiers)
- `No LOC/ISCO columns found for LOC distribution plots` — expected (loc4 aggregated variable; raw ISCO not in parquet)

---

## Summary Assessment

Standard post-estimation diagnostics completed successfully. The fit profile of M1-naive is coherent and structurally interpretable. The primary new finding relative to M1-clean is the further worsening of singles-male participation and hours-bin fit caused by the additional positive `beta_E_educH` term. The `beta_E_gsur` reversion to the M0c\_b2\_GSURv2 level is structurally confirmed as expected.

**Diagnostics that pass without qualification:**
- Convergence and uniqueness (three starts, identical LL)
- No bound hits; no new NA SEs; no new Hessian failure modes
- Probability normalisation at machine precision
- Marginal utilities all positive
- Preference, wage, occupation, and hours-opportunity blocks stable
- Wage fit unchanged from M1-clean and M0c\_b2\_GSURv2
- Occupation fit (couples) excellent; singles inherited limitation unchanged

**Diagnostics that failed or remain weak (all pre-existing or expected):**
- Singles-male hours-bin L1 = 0.778 (M1-naive) vs 0.695 (M1-clean) vs 0.634 (M0c\_b2\_GSURv2): progressive regression
- Singles-male participation underprediction: −2.92 ppt (M1-naive) vs −0.88 ppt (M1-clean): worsened
- Couples-female non-work underprediction: 1.29% predicted vs 3.49% observed (structural, unchanged)
- `beta_E_drgn3` individual non-significance (p = 0.084) — weaker than M1-clean (p = 0.039)
- Three NA SEs (singles-consumption block, unchanged from all prior specifications)
- BIC worsens by 8.9 relative to M1-clean (+54.9 relative to M0c\_b2\_GSURv2)

**Pending before the M1-naive robustness verdict:**
- Supplementary diagnostics: joint Wald test for `beta_E_drgn2`–`beta_E_drgn8`; 7×7 region VCV block; 9×9 GSUR+educH+region Hessian sub-block eigenvalues