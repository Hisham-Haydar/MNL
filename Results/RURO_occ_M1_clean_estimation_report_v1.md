# RURO occ M1-clean Estimation Report v1

Date: 2026-05-18  
Spec: `scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml`  
Baseline: `scripts/enhanced/specifications/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml`  
Data stem: `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2`

---

## 1. Estimation overview

Three independent starts were run for `ruro_occ_M1_clean` using the vectorised GAMSPy/CONOPT solver (joint estimation: singles male + singles female + couples). All three converged to the same optimum. Results below are taken from Start 1 (warm-start run `run_2026-05-18_11-33-46`).

| Start | Run folder | Init strategy | LL | Iterations | Walltime |
|-------|-----------|--------------|-----|-----------|---------|
| S1 | `run_2026-05-18_11-33-46` | Warm from M0c_b2_GSURv2 | −6487.5522 | 12 | 320.9 s |
| S2 | `run_2026-05-18_11-42-09` | Spec defaults | −6487.5522 | 21 | 353.8 s |
| S3 | `run_2026-05-18_11-51-13` | Perturbed (M1-clean warm, seed=42) | −6487.5522 | 24 | 382.0 s |

**Artifact paths (canonical)**:  
`outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/<run_folder>/`

Each run folder contains all 8 artifacts: `estimation.log`, `estimation_results.json`, `estimation_results_singles_male.csv`, `estimation_results_singles_female.csv`, `estimation_results_couples.csv`, `estimation_summary.txt`, `identification_diagnostics.txt`, `specification_used.yaml`.

**Root-cause note (artifact displacement):** The `ensure_local_workdir()` function in `gamspy_estimation_vectorized.py` previously called `os.chdir()` to a local GAMS work directory when the process CWD was a UNC path. This redirected all subsequent relative-path saves away from the UNC repo root, placing them under `C:\Users\hisham\AppData\Local\gams_work\outputs\...`. The function has been patched to set `GAMSPY_WORKING_DIR` without altering the process CWD. The three run folders were populated by copying artifacts from the local gams_work path to the canonical UNC output directories; timestamps and file contents are unmodified.

---

## 2. Convergence verdict

**Converged.** All three starts reach SolveStatus `NormalCompletion` / ModelStatus `OptimalLocal` at LL = −6487.5522. The parameter vectors are bit-identical across starts (verified by comparing `estimation_results.json` parameter dictionaries). The global maximum is confirmed within the explored start set.

---

## 3. Parameter count

53 parameters parsed and estimated. Breakdown:

| Block | Count | Parameters |
|-------|-------|-----------|
| Market opportunity | 9 | `beta_E`, `beta_E_gsur`, `beta_E_drgn2`–`beta_E_drgn8` |
| Hours opportunity | 3 | `beta_h_pt1`, `beta_h_pt2`, `beta_h_ft` |
| Wage opportunity | 6 | `beta_w0`, `beta_w_educL`, `beta_w_educH`, `beta_w_pexp`, `beta_w_pexp2`, `sigma` |
| Occupation opportunity | 12 | `beta_occ_{2,3,4}_{sm,sf,cm,cf}` |
| Utility + leisure | 22 | `beta_c`, `beta_c_sm`, `beta_c_sf`, `theta_c_singles`, `beta_l0_{m,f,sm,sf}`, `theta_l_{m,f,sm,sf}`, `beta_l_age_{m,f,sm,sf}`, `beta_l_age2_{m,f,sm,sf}`, `beta_l_nkids_{f,sf}` |
| Couples | 1 | `beta_ll` |
| **Total** | **53** | |

---

## 4. Joint log-likelihood

| Specification | Params | Joint LL | ΔLL vs M0c_b2_GSURv2 |
|--------------|--------|---------|---------------------|
| M0c_b2_GSURv2 (baseline) | 47 | −6501.2082 | — |
| M1-clean | 53 | −6487.5522 | +13.656 |

Net new parameters: 6 (−1 `beta_E_educH` + 7 `beta_E_drgn2`–`beta_E_drgn8`). The ΔLL = +13.656 is descriptive evidence of improved fit. A formal LR test is **not valid** here because the two models are not nested: M1-clean simultaneously drops `beta_E_educH` and adds seven region parameters. The joint significance of the region dummies will be assessed via the planned M1-specific Wald test (§19), which uses the 7×7 region sub-block of the numerical VCV matrix and does not require a nested-model comparison.

---

## 5. New parameters: region dummies (beta_E_drgn2–beta_E_drgn8)

Region of residence (EUROMOD `drgn1`, IDF = 1 reference) enters the employment-opportunity index. All seven region shifters are positive, indicating higher employment opportunity for non-IDF regions relative to IDF after conditioning on GSUR. All are individually significant at the 5% level except `beta_E_drgn8` (p = 0.097).

| Parameter | Variable | Region | Estimate | SE | t | p |
|-----------|---------|--------|---------|-----|---|---|
| `beta_E_drgn2` | `reg2` | Paris Basin | 0.8013 | 0.2664 | 3.008 | 0.0026 |
| `beta_E_drgn3` | `reg3` | North | 0.6564 | 0.3186 | 2.060 | 0.0394 |
| `beta_E_drgn4` | `reg4` | East | 1.5626 | 0.4100 | 3.811 | 0.0001 |
| `beta_E_drgn5` | `reg5` | West | 0.7725 | 0.2722 | 2.838 | 0.0045 |
| `beta_E_drgn6` | `reg6` | South-West | 0.7665 | 0.3275 | 2.341 | 0.0192 |
| `beta_E_drgn7` | `reg7` | Centre-East | 0.6405 | 0.3118 | 2.054 | 0.0399 |
| `beta_E_drgn8` | `reg8` | Mediterranean | 0.4631 | 0.2794 | 1.658 | 0.0974 |

All initial values were 0.0 (transferred from warm start via `fallback_default`). No bound hits on any drgn parameter.

---

## 6. Removed parameter: beta_E_educH

`beta_E_educH` (education-high as employment-opportunity shifter) is absent from M1-clean. In M0c_b2_GSURv2 its estimate was 0.4386 (SE = 0.2257, t = 1.943), marginally significant at 5%. Under the JMP ability/opportunity partition, education is classified as an ability dimension and must not enter the opportunity-side index.

---

## 7. GSUR parameter response

`beta_E_gsur` shifts from −1.0502 (M0c_b2_GSURv2) to −1.3289 (M1-clean), a change of −0.279. The strengthened GSUR coefficient reflects that region of residence absorbs part of the local unemployment variation previously loaded onto GSUR, requiring the GSUR term to adjust to maintain fit. Both estimates are highly significant (M1-clean: SE = 0.1631, t = −8.15).

---

## 8. Full parameter table

All 53 parameters from Start 1 (warm). The `[neg-var]` flag indicates negative diagonal entry in the numerical variance–covariance matrix (Hessian-based SE not available for these three parameters; see §11).

| Parameter | Estimate | SE | t | p |
|-----------|---------|-----|---|---|
| `beta_l0_sm` | 3.836170 | 0.6929 | 5.537 | 0.0000 |
| `beta_l_age_sm` | 0.004052 | 0.0246 | 0.165 | 0.8693 |
| `beta_l_age2_sm` | 0.001755 | 0.0021 | 0.851 | 0.3946 |
| `beta_c_sm` | 0.553672 | [neg-var] | — | — |
| `theta_l_sm` | −0.712470 | 0.1501 | −4.745 | 0.0000 |
| `beta_l0_sf` | 4.469536 | 0.7641 | 5.850 | 0.0000 |
| `beta_l_age_sf` | 0.000335 | 0.0269 | 0.012 | 0.9901 |
| `beta_l_age2_sf` | 0.003931 | 0.0025 | 1.559 | 0.1190 |
| `beta_l_nkids_sf` | −0.082422 | 0.3447 | −0.239 | 0.8110 |
| `beta_c_sf` | 0.505586 | [neg-var] | — | — |
| `theta_l_sf` | −0.722669 | 0.1310 | −5.517 | 0.0000 |
| `theta_c_singles` | −1.048483 | [neg-var] | — | — |
| `beta_l0_m` | 0.012080 | 0.2882 | 0.042 | 0.9666 |
| `beta_l_age_m` | −0.010336 | 0.0153 | −0.678 | 0.4981 |
| `beta_l_age2_m` | 0.000927 | 0.0015 | 0.627 | 0.5307 |
| `theta_l_m` | −0.731400 | 0.1391 | −5.257 | 0.0000 |
| `beta_l0_f` | 2.592348 | 0.4353 | 5.956 | 0.0000 |
| `beta_l_age_f` | −0.059381 | 0.0226 | −2.632 | 0.0085 |
| `beta_l_age2_f` | 0.003009 | 0.0022 | 1.345 | 0.1787 |
| `beta_l_nkids_f` | 0.169459 | 0.2142 | 0.791 | 0.4290 |
| `theta_l_f` | −0.678130 | 0.0915 | −7.412 | 0.0000 |
| `beta_c` | 4.000030 | 0.1439 | 27.792 | 0.0000 |
| `beta_E` | −2.499276 | 0.2155 | −11.599 | 0.0000 |
| `beta_h_pt1` | −0.502194 | 0.1092 | −4.601 | 0.0000 |
| `beta_h_pt2` | 0.372247 | 0.1118 | 3.329 | 0.0009 |
| `beta_h_ft` | 1.449680 | 0.0503 | 28.838 | 0.0000 |
| `beta_E_gsur` | −1.328948 | 0.1631 | −8.150 | 0.0000 |
| `beta_E_drgn2` | 0.801342 | 0.2664 | 3.008 | 0.0026 |
| `beta_E_drgn3` | 0.656401 | 0.3186 | 2.060 | 0.0394 |
| `beta_E_drgn4` | 1.562552 | 0.4100 | 3.811 | 0.0001 |
| `beta_E_drgn5` | 0.772496 | 0.2722 | 2.838 | 0.0045 |
| `beta_E_drgn6` | 0.766517 | 0.3275 | 2.341 | 0.0192 |
| `beta_E_drgn7` | 0.640451 | 0.3118 | 2.054 | 0.0399 |
| `beta_E_drgn8` | 0.463141 | 0.2794 | 1.658 | 0.0974 |
| `beta_occ_2_sm` | −1.474430 | 0.1425 | −10.347 | 0.0000 |
| `beta_occ_3_sm` | −2.129195 | 0.1845 | −11.542 | 0.0000 |
| `beta_occ_4_sm` | 0.060419 | 0.0867 | 0.697 | 0.4859 |
| `beta_occ_2_sf` | 0.051019 | 0.1141 | 0.447 | 0.6549 |
| `beta_occ_3_sf` | −0.500047 | 0.1303 | −3.837 | 0.0001 |
| `beta_occ_4_sf` | 0.859079 | 0.0939 | 9.152 | 0.0000 |
| `beta_occ_2_cm` | −1.495560 | 0.1141 | −13.111 | 0.0000 |
| `beta_occ_3_cm` | −2.251328 | 0.1491 | −15.102 | 0.0000 |
| `beta_occ_4_cm` | 0.459406 | 0.0692 | 6.634 | 0.0000 |
| `beta_occ_2_cf` | 0.131868 | 0.1015 | 1.299 | 0.1939 |
| `beta_occ_3_cf` | −0.249050 | 0.1128 | −2.208 | 0.0272 |
| `beta_occ_4_cf` | 1.085850 | 0.0820 | 13.237 | 0.0000 |
| `beta_w0` | 2.016252 | 0.0258 | 78.217 | 0.0000 |
| `beta_w_educL` | −0.040563 | 0.0213 | −1.904 | 0.0569 |
| `beta_w_educH` | 0.323990 | 0.0150 | 21.578 | 0.0000 |
| `beta_w_pexp` | 0.018461 | 0.0023 | 8.203 | 0.0000 |
| `beta_w_pexp2` | −0.000226 | 0.0000 | −4.535 | 0.0000 |
| `sigma` | 0.427474 | 0.0042 | 102.439 | 0.0000 |
| `beta_ll` | 2.617465 | 0.3499 | 7.480 | 0.0000 |

---

## 9. Warm-start transfer (Start 1)

| Source | Count | Parameters |
|--------|-------|-----------|
| Transferred from M0c_b2_GSURv2 | 46 | All M0c_b2_GSURv2 params except `beta_E_educH` |
| Fallback default (0.0) | 7 | `beta_E_drgn2`–`beta_E_drgn8` |
| Total | 53 | |

`beta_E_educH` (present in source, absent from M1-clean) was discarded by the warm-start loader. The 7 new region parameters were initialised at 0.0 and converged to the values in §5.

---

## 10. Parameter stability across starts

All three starts converge to the same parameter vector (bit-identical in `estimation_results.json`). The Start 3 perturbation was ±5% of the M1-clean warm-start vector (seed=42), stored in `Results/_M1_clean_perturbed_init_s42_wrapped.json`. No start found a better optimum. The solution is numerically stable.

---

## 11. Hessian and identification diagnostics

| Diagnostic | M0c_b2_GSURv2 | M1-clean |
|-----------|--------------|---------|
| Condition number | 5.14 × 10¹⁰ | 5.10 × 10¹⁰ |
| Negative eigenvalues | 1 | 1 |
| Near-zero eigenvalues (|λ| ≤ 10⁻⁸) | 0 | 0 |
| Negative variances in VCV | 3 | 3 |
| Valid SEs | 44/47 | 50/53 |
| Bound hits | 0 | 0 |

The three negative-variance parameters — `beta_c_sm`, `beta_c_sf`, `theta_c_singles` — are the same block in both M0c_b2_GSURv2 and M1-clean. This is a pre-existing identification issue in the singles consumption/Box-Cox block inherited from M0c_b2_GSURv2 and is not introduced by M1-clean. The Moore-Penrose pseudoinverse is used for the remaining 50 parameters.

Top correlations (Hessian-based):

| Pair | Correlation |
|------|------------|
| `beta_c_sm` ↔ `beta_c_sf` | −1.108 |
| `beta_c_sf` ↔ `theta_c_singles` | −1.086 |
| `beta_c_sm` ↔ `theta_c_singles` | −1.067 |
| `beta_w_pexp` ↔ `beta_w_pexp2` | −0.960 |

Correlations exceeding ±1.0 are artefacts of the pseudoinverse applied to the ill-conditioned block and confirm near-collinearity in the consumption preference parameters for singles.

---

## 12. Bound hits

Zero bound hits on all 53 parameters across all three starts. The seven region dummies moved from 0.0 to values between 0.46 and 1.56, well within their [−10.0, 10.0] bounds.

---

## 13. Key structural changes vs M0c_b2_GSURv2

| Change | M0c_b2_GSURv2 | M1-clean |
|--------|--------------|---------|
| `beta_E_educH` | 0.4386 (SE=0.2257, t=1.943) | **removed** |
| `beta_E_gsur` | −1.0502 (SE=0.1581) | −1.3289 (SE=0.1631) |
| `beta_E_drgn2`–`beta_E_drgn8` | absent | 0.46–1.56 (all pos.) |
| `beta_ll` | 2.6053 | 2.6175 |
| `beta_E` | −2.4895 | −2.4993 |

The stable `beta_E` indicates the base employment-opportunity intercept is not disturbed by the region shifters. The GSUR strengthening (−0.279 in absolute value) is the primary equilibrating response.

---

## 14. Utility block stability

All utility parameters are close to their M0c_b2_GSURv2 counterparts. Box-Cox exponents: `theta_l_sm` = −0.712, `theta_l_sf` = −0.723, `theta_l_m` = −0.731, `theta_l_f` = −0.678 (all negative, leisure is concave in all four groups). `theta_c_singles` = −1.048 (log-utility neighbourhood). `theta_c` for couples is fixed at 0.0 (log-utility, not estimated). `beta_ll` = 2.617 (strong leisure complementarity in couples).

---

## 15. Wage block stability

Wage parameters are unchanged in character from M0c_b2_GSURv2. `beta_w_educH` = 0.324 (t = 21.6) reflects wage returns to high education — note this is a wage parameter, not an opportunity parameter, and is correctly retained in M1-clean. `sigma` = 0.427, well inside its [0.1, 20.0] bounds.

---

## 16. Occupation block stability

All 12 occupation shifters are stable. Pattern: occupation 3 (clerical/service) carries large negative coefficients for both singles male and coupled male (−2.13, −2.25); occupation 4 (high-skill) is positive for females (sf: 0.859, cf: 1.086). This pattern is preserved from M0c_b2_GSURv2.

---

## 17. Observations and groups

| Group | Observations | Groups |
|-------|-------------|--------|
| Singles male | 76,600 | 766 |
| Singles female | 91,000 | 910 |
| Couples | 257,700 | 2,577 |
| **Total (joint)** | **425,300** | **4,253** |

---

## 18. Estimation infrastructure notes

- **Solver:** GAMSPy/CONOPT (vectorised joint formulation)
- **Hessian:** Numerical (finite differences, 53×53), computed post-convergence
- **Proposal correction:** −log(prior), applied once per alternative
- **Market opportunity centering:** Within choice set, weights = proposal
- **Variable scales:** `gsur: 10.0`
- **Expression constraints:** 2 soft constraints (marginal utility of leisure > 0 at reference point for couples), weight = 1000.0
- **Spec parsed from:** `scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml` (confirmed present in `specification_used.yaml` in each run folder)

---

## 19. Pre-conditions for post-estimation

The following M1-specific diagnostics are required before the post-estimation step can satisfy the design memo v2 §21. They are not blocking for estimation itself and are not implemented in the current step:

1. **Joint Wald test** for `beta_E_drgn2 = beta_E_drgn3 = ... = beta_E_drgn8 = 0` using the 7×7 sub-block of the numerical Hessian-based VCV matrix. The ΔLL reported in §4 is descriptive only (the two models are not nested); formal joint significance of the region dummies must be assessed by this Wald test.
2. **7×7 region covariance sub-block** extracted from the full 53×53 numerical VCV, with pairwise correlation flags for |corr| > 0.7.
3. **Region-conditional GSUR Hessian sub-matrix** eigenvalues: the 8×8 sub-block spanning {`beta_E_gsur`, `beta_E_drgn2`–`beta_E_drgn8`} to verify that the GSUR/region opportunity block is well-separated in curvature.

These require a supplementary diagnostic script (e.g., `scripts/enhanced/RURO_post_estimation_M1_diagnostics.py`) and are tracked as a pre-post-estimation requirement, not a pre-estimation blocker.

---

## 20. Artifact verification summary

All 8 artifacts confirmed present in all 3 run folders at the canonical UNC path:

```
outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/
  run_2026-05-18_11-33-46/  [S1 warm]    — estimation.log + 7 artifacts ✓
  run_2026-05-18_11-42-09/  [S2 default] — estimation.log + 7 artifacts ✓
  run_2026-05-18_11-51-13/  [S3 perturb] — estimation.log + 7 artifacts ✓
```

---

## 21. Step completion status

**Step 3 complete.** The M1-clean estimation has converged in 3 independent starts to a single optimum (LL = −6487.5522). All artifacts are physically present at their canonical paths. The specification is confirmed correctly implemented (53 parameters, seven region dummies estimated, GSUR responds appropriately, no bound hits, 50/53 valid SEs with the same 3-parameter negative-variance block as M0c_b2_GSURv2).

The next step is standard post-estimation diagnostics followed by the M1-specific supplementary diagnostics described in §19. Welfare scaffolding is a separate, later stage and is not authorised here.