# JMP Pooled P3a — Post-Estimation Diagnostics Report v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-22*

Document class: narrow post-estimation diagnostics report (S4, S5, S6, S8).
Authorised by `docs/France_case/P3a/execution_logs/pooled_P3a/JMP_pooled_P3a_post_estimation_diagnostics_authorization_v1.md`.
Read-only / fixed-theta arithmetic on saved corrected-region artifacts. **No
solver, no re-estimation, no welfare, no SA2 verdict, no canonical promotion,
no S10/S11 simulation.** M1-clean 2016 remains the active JMP baseline.

---

## 1. Diagnostics verdict

| Criterion | Adjudication | Deciding number |
|---|---|---|
| **S4** Region joint robust Wald | **FAIL** | W = 2.658, df = 7, p = 0.9148 (well-conditioned, cond V_R = 6.31) |
| **S5** GSUR-region Hessian eigenvalues | **PASS** | All 8 eigenvalues of GSUR-region Hessian sub-block POSITIVE (range 20.44 to 910.28; cond = 44.54) |
| **S6** Preference block vs M1-clean | **FAIL** | 14/27 focused params breach |Δ| > 10%; singles-consumption block diverges 4–5×; 3 sign flips; LL-profile shows non-stationary slice in `theta_c_singles` (Δ-LL = +761 at θ = −0.161 vs saved θ̂ = +0.039) |
| **S8** Negative-variance enumeration | **FAIL** | 5 negative-variance entries: `beta_l0_sm`, `theta_l_sm`, `theta_l_sf`, `theta_l_m`, `theta_l_f` — none coincide with M1-clean's three (`beta_c_sm`, `beta_c_sf`, `theta_c_singles`); they are concentrated in the leisure block |

**Overall.** The corrected-region pooled P3a is identified (T3/T4/T5 pass, the SE sandwich is finite for all 54 free parameters), but three of the four diagnostics fail. S4 fails decisively (the seven region dummies are jointly not different from zero at p = 0.91 with a well-conditioned VCV — a sharp reversal of the M1-clean benchmark W = 28.18, p = 0.0002). S6 fails on the preference block; the singles-consumption block is sharply different from M1-clean and the LL profile in `theta_c_singles` is non-stationary at the saved theta. S8 fails: the negative-variance set has shifted entirely from M1-clean's singles-consumption block to a new leisure block. Only S5 passes (GSUR-region Hessian eigenvalues are all positive). The pooled P3a remains NOT SA2-ready.

---

## 2. Authorization scope

Per `docs/France_case/P3a/execution_logs/pooled_P3a/JMP_pooled_P3a_post_estimation_diagnostics_authorization_v1.md`:

- Authorised: S4 (Wald), S5 (GSUR-region Hessian eigenvalues; permitted to recompute the true Hessian at the saved theta), S6 (Δ table vs M1-clean + LL profile in `theta_c_singles` at saved theta), S8 (negative-variance enumeration).
- Not authorised: solver, re-estimation, welfare, SA2 verdict, canonical promotion, M1-clean displacement, spec modification, S10/S11 simulation, any use of pre-repair pooled artifacts.

All numerics in this report are functions of saved corrected-region artifacts plus one deterministic Hessian recomputation at the SAVED converged theta (fixed-theta evaluation; no optimisation step taken).

---

## 3. Files and artifacts inspected

**Corrected-region cluster-robust VCV files (the source of truth for S4):**
- `Results/JMP_pooled_P3a_corrected_start1_cluster_robust_se_vcv.npy`
- `Results/JMP_pooled_P3a_corrected_start2_cluster_robust_se_vcv.npy`
- `Results/JMP_pooled_P3a_corrected_start3_cluster_robust_se_vcv.npy`

**Corrected-region SE JSONs (saved converged theta, robust SE vector, Hessian-based SE vector, `free_mask`, Hessian condition number 3.316 × 10⁹):**
- `Results/JMP_pooled_P3a_corrected_start1_cluster_robust_se.json`
- `Results/JMP_pooled_P3a_corrected_start2_cluster_robust_se.json`
- `Results/JMP_pooled_P3a_corrected_start3_cluster_robust_se.json`

**Corrected-region estimation result JSONs (theta, hessian_diagnostics with n_negative_eigenvalues=5):**
- `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_1/run_2026-05-21_23-47-14/estimation_results.json`
- `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_2/run_2026-05-22_00-18-36/estimation_results.json`
- `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_3/run_2026-05-22_00-53-54/estimation_results.json`

**M1-clean verdict-selected baseline (S6, S8 comparison):**
- `outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_11-33-46/estimation_results.json` (joint LL = −6487.5522)

**Specification + data (used only by the §6/§11 Hessian + LL-profile recomputations, at the SAVED theta):**
- `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml` (read-only)
- `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__{singles,couples,mnlmeta}.parquet|.json`

**Diagnostic artifacts created in this report:**
- `Results/JMP_pooled_P3a_corrected_S4_wald.json` (S4 Wald statistics, all three starts)
- `Results/JMP_pooled_P3a_corrected_true_hessian_54x54.npy` (recomputed 54×54 true Hessian at saved theta)
- `Results/JMP_pooled_P3a_corrected_S5_S8_hessian_diag.json` (eigenvalues, GSUR-region sub-block, negative-variance enumeration)
- `Results/JMP_pooled_P3a_corrected_S6_preference_comparison.json` (preference-block Δ table vs M1-clean)
- `Results/JMP_pooled_P3a_corrected_S6_theta_c_singles_LL_profile.json` (LL profile in `theta_c_singles` at saved theta)

**Scripts used (under `scripts/maintenance/`):**
- `run_pooled_P3a_S5_S8_hessian_recompute.py` — fixed-theta central-difference Hessian recompute (uses `compute_gradient_joint` from `scripts/enhanced/estimation_engine.py`).
- `run_pooled_P3a_S6_preference_comparison.py` — arithmetic on saved JSONs.
- `run_pooled_P3a_S6_theta_c_singles_profile.py` — fixed-theta LL evaluations using `compute_likelihood_joint`.

---

## 4. S4 region joint robust Wald test

**Coefficients (from saved corrected Start 1 theta, positions 27–33 / 0-indexed):**

| param | value |
|---|---|
| `beta_E_drgn2` | +0.396497 |
| `beta_E_drgn3` | +0.350001 |
| `beta_E_drgn4` | +0.641609 |
| `beta_E_drgn5` | +0.431035 |
| `beta_E_drgn6` | +0.357738 |
| `beta_E_drgn7` | +0.367068 |
| `beta_E_drgn8` | +0.167527 |

(Cross-start L∞ differences in the full converged theta: Start 1 vs 2 = 4.82 × 10⁻¹²; Start 1 vs 3 = 4.78 × 10⁻¹². The three starts converged to bit-identical thetas to ~picoscale precision.)

**7 × 7 region VCV sub-block (cluster-robust sandwich, from the corrected `.npy`):**

| start | V_R eigenvalues (sorted) | cond V_R | min eig |
|---|---|---|---|
| Start 1 | 0.0770, 0.1046, 0.1301, 0.1456, 0.1618, 0.2281, 0.4863 | 6.31 | 7.70 × 10⁻² |
| Start 2 | 0.0770, 0.1046, 0.1301, 0.1456, 0.1618, 0.2281, 0.4863 | 6.31 | 7.70 × 10⁻² |
| Start 3 | 0.0770, 0.1046, 0.1301, 0.1456, 0.1618, 0.2281, 0.4863 | 6.31 | 7.70 × 10⁻² |

**V_R is well-conditioned (cond = 6.31; smallest eigenvalue ~0.077).** A plain matrix inverse is reliable here; pseudo-inverse is not required.

**Wald statistic (W = b_R' V_R⁻¹ b_R, ~ χ²(7) under H₀):**

| start | W | p-value | method |
|---|---|---|---|
| Start 1 | 2.6577 | 0.9148 | inverse |
| Start 2 | 2.6577 | 0.9148 | inverse |
| Start 3 | 2.6577 | 0.9148 | inverse |

Cross-start spread of W: 2.05 × 10⁻⁸ (numerical-stability check passed).

**Benchmark (context only).** M1-clean 2016 region block: W = 28.18, df = 7, p = 0.0002.

**Note.** Individual region t-ratios (each in the range ≈0.50–1.45) are not the S4 test and do not override the joint result; the joint test is the criterion.

## 5. S4 adjudication

**S4 FAILS.** W = 2.658, df = 7, p = 0.9148. The seven region dummies are jointly not different from zero at the 1% level (or any reasonable level). V_R is well-conditioned (cond = 6.31), so this is not a numerical artefact. The joint Wald is decisive — the pooled region block, although identified, contributes no jointly significant variation in market opportunity once the cluster-robust covariance is accounted for. This is a sharp reversal of M1-clean 2016, where the same restriction was rejected at p = 0.0002 (W = 28.18). The collapse plausibly reflects the change of the region channel from a singles + couples-individual signal (M1-clean) to a couples-only signal (pooled P3a after the R1 region repair), but the diagnostic does not require attribution: the joint test is what S4 is, and it fails.

---

## 6. S5 GSUR-region Hessian/eigenvalue check

**Hessian source.** The full 54 × 54 true Hessian was NOT persisted in the saved estimation result JSONs (only `hessian_diagnostics.eigenvalues` and `condition_number` were saved). Per authorization §5, the true Hessian was **deterministically recomputed at the saved corrected-region converged theta** via central differences on `compute_gradient_joint` (eps = 1 × 10⁻⁵), using the existing estimation engine and the corrected split-stem data. **No optimization step was taken at any point** — the recomputation is a fixed-theta evaluation.

**Confirmation that conditioning matches the saved diagnostic.** Recomputed Hessian condition number = **3.3163 × 10⁹** — bit-matching the value 3.316291991 × 10⁹ recorded in the corrected-region SE JSONs (`PE6_true_hessian.condition_number`). The recompute is therefore on the same numerical object the original SE step used.

**Saved Hessian artifact.** `Results/JMP_pooled_P3a_corrected_true_hessian_54x54.npy` (54 × 54, dtype float64).

**Full 54×54 Hessian summary:**
- Condition number: 3.3163 × 10⁹
- Min eigenvalue: −1.385 × 10⁶
- Max eigenvalue: +3.718 × 10¹⁰
- **Number of negative eigenvalues: 5** (matches the `n_negative_eigenvalues: 5` recorded in the estimation result `hessian_diagnostics`).

**GSUR-region 8 × 8 Hessian sub-block** (parameters: `beta_E_gsur`, `beta_E_drgn2`, … , `beta_E_drgn8`; full-index 26–33; free-index 25–32 since `beta_l0_m` at fixed bound is the sole `False` in `free_mask`):

Eigenvalues, sorted ascending:
**20.44, 27.28, 33.10, 36.12, 41.14, 44.39, 52.76, 910.28** — **all positive**.

Sub-block condition number: **44.54**.
Smallest eigenvalue: **20.44** (numerical tolerance: well above any plausible floating-point noise on a Hessian of this scale).

**Region-only 7 × 7 Hessian sub-block** (for cross-reference): eigenvalues 24.12, 33.08, 33.16, 37.01, 43.89, 45.03, 55.01; cond = 2.28; all positive.

**Cross-start consistency.** The 7 × 7 robust VCV sub-block (§4) is identical to numerical precision across the three starts; the recomputed Hessian uses only the saved Start 1 theta, and the L∞ cross-start theta differences (4.8 × 10⁻¹²) imply the Hessian sub-block at Start 2 or Start 3 would be the same to working precision.

## 7. S5 adjudication

**S5 PASSES.** The 8 × 8 GSUR-region true-Hessian sub-block has no negative eigenvalues (range 20.44 to 910.28). The sub-block is well-conditioned (cond = 44.54), and the smallest eigenvalue is sufficiently far above any plausible numerical-tolerance threshold to be unambiguous. The cluster-robust VCV diagonal in the same block is strictly positive (§4 and T4-PASS in the SE JSONs). The corresponding robust VCV sub-block is also well-conditioned (cond = 6.31 for the region-only piece; the 8 × 8 robust block inherits the same conditioning structure). The five negative Hessian eigenvalues of the full matrix (§6 and §11) therefore lie OUTSIDE the GSUR-region sub-block. **S5 isolates the conditioning of the market-opportunity / region block, and that block is well-posed at the saved theta.** This is the only criterion among the four that clears cleanly.

---

## 8. S6 preference-block comparison to M1-clean

**M1-clean baseline artifact used.** `outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_11-33-46/estimation_results.json` — the **verdict-selected** M1-clean run per `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_verdict_v1.md`, joint LL = −6487.5522. No substitution was made.

**Shared parameter count.** 53 shared (M1-clean has 53 params; pooled P3a has 55). The two P3a-only parameters are `beta_E_y2015` and `beta_E_y2017` (year indicators), excluded from the comparison.

**Per-parameter Δ table — focused preference block:**

| param | M1-clean | Pooled corrected | abs Δ | rel % | flag |
|---|---:|---:|---:|---:|---|
| `beta_l0_sm` | +3.836170 | +4.328086 | +0.491916 | +12.82% | >10% |
| `beta_l_age_sm` | +0.004052 | +0.043144 | +0.039092 | +964.83% | >10% |
| `beta_l_age2_sm` | +0.001755 | +0.001724 | −0.000031 | −1.77% | — |
| `beta_c_sm` | +0.553672 | **+2.733147** | +2.179475 | **+393.64%** | >10% (~5×) |
| `theta_l_sm` | −0.712470 | −0.719206 | −0.006736 | −0.95% | — |
| `beta_l0_sf` | +4.469536 | +4.460193 | −0.009344 | −0.21% | — |
| `beta_l_age_sf` | +0.000335 | +0.038506 | +0.038171 | +11382.63% | >10% |
| `beta_l_age2_sf` | +0.003931 | +0.004610 | +0.000679 | +17.26% | >10% |
| `beta_l_nkids_sf` | −0.082422 | +0.356277 | +0.438698 | +532.26% | >10%, **SIGN-FLIP** |
| `beta_c_sf` | +0.505586 | **+2.351327** | +1.845741 | **+365.07%** | >10% (~4.6×) |
| `theta_l_sf` | −0.722669 | −0.701604 | +0.021065 | +2.91% | — |
| `theta_c_singles` | −1.048483 | **+0.039244** | +1.087726 | +103.74% | >10%, **SIGN-FLIP** |
| `beta_l0_m` | +0.012080 | +0.000001 | −0.012079 | −99.99% | bound-active in pooled |
| `beta_l_age_m` | −0.010336 | +0.005870 | +0.016206 | +156.79% | >10%, **SIGN-FLIP** |
| `beta_l_age2_m` | +0.000927 | +0.001646 | +0.000719 | +77.56% | >10% |
| `theta_l_m` | −0.731400 | −0.681907 | +0.049493 | +6.77% | — |
| `beta_l0_f` | +2.592348 | +2.605285 | +0.012937 | +0.50% | — |
| `beta_l_age_f` | −0.059381 | −0.058032 | +0.001349 | +2.27% | — |
| `beta_l_age2_f` | +0.003009 | +0.005288 | +0.002278 | +75.70% | >10% |
| `beta_l_nkids_f` | +0.169459 | +0.142852 | −0.026608 | −15.70% | >10% |
| `theta_l_f` | −0.678130 | −0.657847 | +0.020283 | +2.99% | — |
| `beta_c` | +4.000030 | +4.312411 | +0.312381 | +7.81% | — |
| `beta_E` | −2.499276 | −2.397723 | +0.101553 | +4.06% | — |
| `beta_h_pt1` | −0.502194 | −0.474816 | +0.027377 | +5.45% | — |
| `beta_h_pt2` | +0.372247 | +0.424756 | +0.052510 | +14.11% | >10% |
| `beta_h_ft` | +1.449680 | +1.405924 | −0.043756 | −3.02% | — |
| `beta_ll` | +2.617465 | +2.655942 | +0.038477 | +1.47% | — |

**Summary of the focused preference block (27 params shown):**
- **14 of 27** breach |Δ| > 10%.
- **3 sign flips**: `beta_l_nkids_sf`, `theta_c_singles`, `beta_l_age_m`.
- Singles-consumption block (`beta_c_sm`, `beta_c_sf`, `theta_c_singles`) diverges 4–5× and contains a sign flip — the largest substantive shift in the table.
- Leisure curvature (`theta_l_sm`, `theta_l_sf`, `theta_l_m`, `theta_l_f`) and the labour-supply intercepts (`beta_l0_sf`, `beta_l0_f`) are stable across the M1-clean / pooled comparison.
- `beta_ll` (a key passing-S7 number) is stable: +1.47%.
- `beta_l0_m` is bound-active in the pooled corrected fit (at 1 × 10⁻⁶ lower bound) — this is `free_mask = False` for that slot and contributes a known robust SE = 0 in the corrected SE JSON.

The leisure shifters (`beta_l_age_sm`, `beta_l_age_sf`, `beta_l_age_m`, `beta_l_age2_m`, `beta_l_age2_f`, `beta_l_nkids_sf`, `beta_l_nkids_f`) all show large relative shifts, with sign flips in two of them; the leisure block is **also** unstable across the M1-clean / pooled comparison, despite the leisure-curvature terms (`theta_l_*`) being stable.

## 9. S6 singles-consumption diagnosis

The singles-consumption block (`beta_c_sm`, `beta_c_sf`, `theta_c_singles`) is the largest substantive S6 shift and warrants particular interpretation.

**Standard errors:**

| param | M1-clean Hessian SE | Pooled corrected robust SE | Pooled corrected Hessian SE |
|---|---|---|---|
| `beta_c_sm` | None (negative variance in M1-clean) | 0.282414 | 0.066396 |
| `beta_c_sf` | None (negative variance in M1-clean) | 0.357395 | 0.065725 |
| `theta_c_singles` | None (negative variance in M1-clean) | 0.067078 | 0.014574 |

**Comment.** In M1-clean these three are exactly the parameters with negative Hessian-based variance (the M1-clean verdict V1 limitation). In the pooled corrected run, their robust SEs are finite and positive, and their Hessian SEs are also positive — meaning the H⁻¹ diagonal is positive for these three in the pooled fit. **The pooled corrected run has not inherited M1-clean's negative-variance entries for the singles-consumption block.** Robust t-ratios in the corrected pooled run are large in magnitude (e.g., `beta_c_sm` t ≈ 2.73/0.28 = 9.7; `beta_c_sf` t ≈ 2.35/0.36 = 6.6; `theta_c_singles` t ≈ 0.039/0.067 = 0.58).

**LL profile in `theta_c_singles` at the saved theta.** Holding every other coordinate fixed at its saved value, varying only `theta_c_singles`:

| `theta_c_singles` | joint LL | Δ-LL vs saved |
|---:|---:|---:|
| −1.461 | −2,442,358 | −2,233,203 (catastrophic) |
| −1.048 *(M1-clean value)* | −302,604 | −93,449 (catastrophic) |
| −0.961 | −258,221 | −49,066 |
| −0.461 | −209,177 | −21 |
| **−0.161** | **−208,394** | **+761** (BEST seen) |
| −0.061 | −208,713 | +442 |
| −0.011 | −208,923 | +233 |
| +0.029 | −209,107 | +48 |
| **+0.039 (saved)** | **−209,155** | 0 |
| +0.049 | −209,204 | −49 |
| +0.089 | −209,405 | −250 |
| +0.139 | −209,667 | −512 |
| +0.239 | −210,209 | −1054 |
| +0.539 | −211,774 | −2619 |
| +1.039 | −213,528 | −4373 |
| +1.539 | −214,110 | −4955 |

(Joint LL values here come from `compute_likelihood_joint`, which returns the per-row × all-rows sum; the relative shape is what matters. The saved-theta value (−209,155.05) sets the reference; the saved-JSON `summary.joint_ll` = −19,084.33 is a per-cluster / rescaled version of the same object.)

**Reading the profile.** The saved theta is NOT a local minimum of the negative LL in the `theta_c_singles` coordinate when other coordinates are held fixed. A higher-LL value sits at `theta_c_singles ≈ −0.16`, with Δ-LL = +761 over the saved theta. The profile is monotone decreasing for `theta_c_singles > 0.04`, and **non-monotone** with a hump to the left, before collapsing catastrophically as θ approaches the M1-clean value of −1.05 (Δ-LL ≈ −93,449). The right-arm decline indicates joint-LL gradient is non-zero in this slice at the saved theta — the solver has not zeroed the partial in `theta_c_singles` while holding the rest of theta fixed.

**Verdict on the divergence.** This is the signature of **weak-identification drift** in the `theta_c_singles` direction (consistent with the LL slope being non-zero at the saved theta in this coordinate slice while the cross-coordinate optimisation has stopped at a flat region), **not** of a genuine multi-year re-identification of the singles-consumption block onto a strict alternative interior optimum. A genuine re-identification would show the saved theta as a local minimum of the negative LL when one coordinate is varied. The profile evidence is therefore in tension with treating the pooled-corrected singles-consumption point estimates as reliable identification of a new economic optimum.

**A caveat on the LL gradient.** The recomputed `||∇LL||_∞` at the saved theta in free coords is 7.99 × 10⁷, which is large in raw units but is consistent across the three starts (since their thetas agree to L∞ < 10⁻¹¹). This warns that the corrected pooled fit's first-order conditions are not zeroed to machine precision in the joint problem, reinforcing the LL-profile interpretation rather than contradicting it.

## 10. S6 adjudication

**S6 FAILS.** The literal S6 threshold (max |Δ| < 10% vs M1-clean) is breached by 14 of 27 focused preference parameters, including three sign flips and a 4–5× shift in the singles-consumption block. The singles-consumption diagnosis points to **weak-identification drift** (LL profile non-stationary in `theta_c_singles` at the saved theta, with a higher-LL region at θ ≈ −0.16) rather than to a genuine multi-year re-identification of a new interior optimum. The leisure-curvature parameters (`theta_l_*`) and `beta_ll` are stable across the comparison, but the leisure-shifter block (age/age² / nkids) and the singles-consumption block are not. The pooled corrected fit therefore does not satisfy S6, and the divergence does not warrant a re-framing of the model as having identified a new economic optimum — it warrants treating the pooled-corrected point estimates in these blocks as weakly identified.

---

## 11. S8 negative-variance enumeration

**Source.** `diag(H⁻¹)` from the recomputed 54 × 54 true Hessian at the saved corrected-region theta. The full 54-vector H⁻¹-diagonal has 5 negative entries — matching the `n_negative_eigenvalues: 5` recorded in `hessian_diagnostics.n_negative_eigenvalues` from each corrected-region estimation result JSON and the warning "5 free parameters have negative variance" in the corrected SE step.

**The five parameters with negative Hessian-based variance (corrected pooled P3a):**

| # | param | block | diag(H⁻¹) | robust SE | Hessian SE |
|---|---|---|---|---|---|
| 1 | `beta_l0_sm` | singles-male leisure intercept | −2.521 × 10⁻³ | 0.781812 | 0.050209 |
| 2 | `theta_l_sm` | singles-male leisure curvature | −2.264 × 10⁻³ | 0.061439 | 0.047580 |
| 3 | `theta_l_sf` | singles-female leisure curvature | −6.869 × 10⁻⁴ | 0.058010 | 0.026209 |
| 4 | `theta_l_m` | couples-male leisure curvature | −6.599 × 10⁻⁴ | 0.037734 | 0.025689 |
| 5 | `theta_l_f` | couples-female leisure curvature | −1.881 × 10⁻⁴ | 0.031404 | 0.013714 |

(The "Hessian SE" column reports `sqrt(|diag(H⁻¹)|)`, which is what the SE JSON saves for these slots — the absolute value is taken because the underlying variance is negative.)

**M1-clean comparison.** M1-clean's three negative-variance entries are `beta_c_sm`, `beta_c_sf`, `theta_c_singles` (per `RURO_occ_M1_clean_verdict_v1.md` V1 — the M1-clean SE list returns `None` for these three slots). **The corrected pooled run's negative-variance set is entirely disjoint from M1-clean's.**

- All three of M1-clean's negative-variance singles-consumption parameters have **positive** Hessian variance in the pooled corrected fit.
- All five pooled-corrected negative-variance entries lie in the **leisure block** — the leisure intercept for singles male and the four leisure curvatures (singles male, singles female, couples male, couples female).
- None of the five is in the region block (`beta_E_drgn2`–`beta_E_drgn8`) or in the GSUR-region block (consistent with S5 PASS: the 8 × 8 GSUR-region Hessian sub-block has no negative eigenvalues).

**Two beyond M1-clean's three.** S8 was framed as "no NEW negative-variance entries beyond M1-clean's three." Here the count is not 3 + 2; it is **5 NEW entries** (the M1-clean three have rotated out and a different five have appeared). This is a stronger failure than the naive "3 + 2" framing implied: the negative-variance set has moved entirely, into a different block.

**Connection to S6.** Four of the five (`theta_l_sm`, `theta_l_sf`, `theta_l_m`, `theta_l_f`) are the leisure-curvature parameters that S6 found stable in absolute value across the M1-clean / pooled comparison (Δ ≈ 0–7%). Their absolute values being stable while their Hessian-based variances are negative says the LL is **flat** in their directions at the saved theta (the curvature is not well-defined in sign), even though the point estimates land in similar places to M1-clean. The fifth (`beta_l0_sm`) showed a +12.8% Δ in S6 — a smaller but still flag-worthy shift.

**Connection to S5.** The 8 × 8 GSUR-region Hessian sub-block has eigenvalues 20.4–910.3, all positive (S5 PASS). The five Hessian negative eigenvalues of the full matrix sit **outside** this sub-block. S5 and S8 are therefore internally consistent: the region block is well-posed; the leisure block is the location of the H curvature problem.

## 12. S8 adjudication

**S8 FAILS.** Five parameters have negative Hessian-based variance, none of them M1-clean's three. The negative-variance set has not merely grown — it has migrated, from the singles-consumption block (M1-clean) to the leisure block (pooled corrected: leisure intercept singles-male + the four leisure curvatures). The pooled corrected fit therefore has neither inherited M1-clean's structural V1 limitation nor cleaned it up; it has replaced it with a different, more pervasive curvature-deficiency pattern in the leisure block. This is not a benign artefact of the `beta_l0_m` bound — that parameter is fixed (`free_mask = False`) and does not appear in `diag(H⁻¹)`. It is also not a region-block issue (S5 PASS rules that out). The five entries are an empirical finding that the pooled corrected estimation has identified the wage/region/labour-supply block but has not pinned down the leisure block — a finding consistent with the S6 LL-profile result that the saved theta is non-stationary in directions adjacent to the leisure block.

---

## 13. Updated SA2-readiness table

Re-scoring the eleven SA2 criteria with the four diagnostics now adjudicated. S1, S2, S3, S7, S9 were already PASS per `docs/France_case/P3a/execution_logs/pooled_P3a/JMP_pooled_P3a_corrected_region_post_estimation_review_v1.md`; S10 and S11 remain a later gate.

| Criterion | Status (pre) | Status (now) | Source |
|---|---|---|---|
| S1 stability across starts | PASS | PASS | review v1; cross-start theta L∞ = 4.8 × 10⁻¹² confirmed here |
| S2 GSUR robust t-test | PASS | PASS | review v1 |
| S3 GSUR vs M1-clean ratio | PASS | PASS | review v1 |
| S4 region joint Wald | OPEN | **FAIL** | §4–5, this report |
| S5 GSUR-region Hessian eigvals | OPEN | **PASS** | §6–7, this report |
| S6 preference block vs M1-clean | OPEN | **FAIL** | §8–10, this report |
| S7 `beta_ll` t-test | PASS | PASS | review v1 |
| S8 negative-variance enumeration | OPEN | **FAIL** | §11–12, this report |
| S9 Gate-A / GA1–GA17 | PASS | PASS | review v1 |
| S10 participation fit | OPEN (sim) | OPEN (sim) | requires authorised S10/S11 simulation — later gate |
| S11 mean-hours fit | OPEN (sim) | OPEN (sim) | requires authorised S10/S11 simulation — later gate |

**Net effect.** Five PASS (S1, S2, S3, S5, S7, S9 → six PASS with S5 now added). Three FAIL (S4, S6, S8). Two open (S10, S11) deferred. **The pooled corrected P3a is NOT SA2-ready.**

---

## 14. Whether S10/S11 simulation may now be authorized

**No.** S10/S11 (participation and mean-hours fit) are simulation-dependent and were always a separate gate. Even if S10/S11 are run later and pass, the S4/S6/S8 failures established here are not erased by a good simulation fit — they bear on the identification and the interpretability of the preference block, which the simulation fit does not address. The decision to authorise S10/S11 should follow a re-specification or re-estimation that addresses the S4, S6, S8 findings, not precede it. The reasonable next action ahead of S10/S11 is to use the diagnostic findings here (region block jointly insignificant; weak identification in singles-consumption; new negative-variance set in the leisure block) to scope a respecification, NOT to spend simulation budget on a fit that is already known to have a non-identified preference block. **S10/S11 simulation remains deferred.**

---

## 15. Whether SA2 verdict may now be drafted

**No.** Three of four diagnostics fail (S4, S6, S8). The SA2-readiness table has three explicit failures plus two simulation-dependent open criteria. SA2 is reachable only when S1–S11 all pass; the corrected pooled fit fails at least S4, S6, S8. **No SA2 verdict may be drafted from these diagnostics.** Specifically, S4 (the joint Wald collapse, well-conditioned) is on its own a sufficient basis to withhold an SA2 verdict, because the region block — central to the market-opportunity layer of the JMP decomposition — is jointly insignificant in the pooled corrected fit.

---

## 16. Whether welfare computation is authorized

**No.** Welfare computation remains gated behind an accepted SA2 verdict. With three diagnostic failures and S10/S11 still pending, no SA2 verdict exists. No welfare is authorised. The diagnostic findings here, in particular the weak identification in `theta_c_singles` shown by the LL profile, additionally cast doubt on the reliability of any money-metric well-being computation built on the pooled corrected singles-consumption block. Welfare must wait for a re-specification that resolves the S4/S6/S8 failures and then earns an SA2 verdict.

---

## 17. Whether M1-clean remains active

**Yes.** M1-clean 2016 (verdict-selected run `outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_11-33-46/`, joint LL = −6487.55) remains the active JMP baseline. The diagnostics here strengthen rather than weaken that position: the corrected pooled P3a, in addition to producing an SA2-ineligible diagnostic set, has migrated the Hessian negative-variance set out of M1-clean's known three (singles-consumption) and into a different block (leisure intercept + four leisure curvatures), with weak identification in `theta_c_singles` at the saved theta. There is no basis here to displace M1-clean.

---

## 18. What was not executed

The following actions were authorised by the diagnostics memo's NOT-AUTHORIZED list and explicitly not performed:

- **No solver was run.** The GAMSPy / CONOPT solver was not invoked. The §6 Hessian recompute was a deterministic central-difference evaluation on `compute_gradient_joint` at the saved theta; the §9 LL profile was a deterministic evaluation of `compute_likelihood_joint` at the saved theta with only `theta_c_singles` varied.
- **No re-estimation was performed.** The saved corrected-region converged theta was used unchanged everywhere. No optimisation step was taken.
- **No welfare was computed.** The welfare integrals (consumer-surplus / money-metric well-being) were not evaluated.
- **No SA2 verdict was issued.** The SA2 readiness table (§13) is a re-scoring of S1–S11 status, not an SA2 verdict.
- **No output was promoted to canonical status.** This report and the small JSON / `.npy` artifacts produced are diagnostic outputs, not canonical estimates.
- **No specification modification was made.** `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml` was read only.
- **No S10/S11 simulation was run.** Participation-fit and mean-hours-fit simulations remain a later gate.
- **No M1-clean displacement.** M1-clean 2016 remains the active baseline.
- **No pre-repair pooled artifact was used.** All inputs were corrected-region artifacts (the three `JMP_pooled_P3a_corrected_*_vcv.npy` files, the three corrected SE JSONs, the three corrected estimation result JSONs, and the verdict-selected M1-clean run). The earlier pre-repair `JMP_pooled_P3a_start{1,2,3}_cluster_robust_se*.{json,npy}` files were not loaded for any computation in this report.
- **No Hessian recomputation at the wrong point.** The §6 Hessian recompute was performed only at the saved corrected-region converged theta loaded from `Results/JMP_pooled_P3a_corrected_start1_cluster_robust_se.json` (`cluster_robust_se_artifacts.converged_theta`). No perturbed, re-optimised, or alternative-start theta was used.
- **No VCV pseudo-inverse without disclosure.** The 7 × 7 region V_R sub-block is well-conditioned (cond = 6.31) and was inverted with `numpy.linalg.inv`. The 8 × 8 GSUR-region Hessian sub-block has cond = 44.54 and was eigen-decomposed with `numpy.linalg.eigvalsh`. No pseudo-inverse was substituted without disclosure.

---

## 19. Immediate next task

The four narrow diagnostics are now adjudicated. The pooled corrected P3a is NOT SA2-ready (three failures: S4, S6, S8). The immediate next task is **NOT** to run further simulation-side checks on the same fit, and it is **NOT** to issue an SA2 verdict.

The immediate next task is to return this diagnostics report to the project chat for an **updated SA2-readiness verdict**, which will record S4 = FAIL, S5 = PASS, S6 = FAIL, S8 = FAIL alongside the previously-passing S1, S2, S3, S7, S9 and the still-deferred S10, S11. That verdict, in turn, scopes the next decision: whether the corrected pooled P3a is salvageable by a constrained respecification (e.g., dropping the now-jointly-insignificant region block, or constraining `theta_c_singles` to its M1-clean value to absorb the weak identification), or whether the pooled multi-year extension is to be paused while the diagnostics findings are documented and M1-clean 2016 retained as the working baseline for the JMP.

That follow-up decision is **not** authorised by the present memo and is **not** taken here. Welfare, canonical promotion, M1-clean displacement, S10/S11 simulation, and any re-estimation all remain gated.

---

**Required final statements**

- **S4 FAILS.** W = 2.658, df = 7, p = 0.9148, well-conditioned (cond V_R = 6.31), cross-start spread 2.1 × 10⁻⁸. The seven region dummies are jointly not different from zero.
- **S5 PASSES.** The 8 × 8 GSUR-region true-Hessian sub-block at the saved theta has all-positive eigenvalues (range 20.44 to 910.28; cond = 44.54). The recomputed full Hessian condition number 3.3163 × 10⁹ bit-matches the value 3.316 × 10⁹ recorded in the corrected SE JSONs, confirming the recompute is on the same numerical object as the original SE step.
- **S6 FAILS.** 14 of 27 focused preference parameters breach |Δ| > 10% vs M1-clean; three sign flips; the singles-consumption block diverges 4–5×; the LL profile in `theta_c_singles` at the saved theta is non-stationary with a higher-LL region at θ ≈ −0.16 (Δ-LL = +761), indicating weak-identification drift rather than re-identification.
- **S8 FAILS.** Five parameters with negative Hessian-based variance (`beta_l0_sm`, `theta_l_sm`, `theta_l_sf`, `theta_l_m`, `theta_l_f`), entirely disjoint from M1-clean's three. The negative-variance set has migrated from the singles-consumption block to the leisure block.
- **No solver was run.** The §6 Hessian recompute used central differences on `compute_gradient_joint` at the saved theta, fixed-theta evaluation only. No optimisation step was taken at any point.
- **No re-estimation was performed.** The saved corrected-region converged theta was held fixed throughout, including for both the Hessian recompute and the LL profile.
- **No welfare was computed.**
- **No SA2 verdict was issued.**
- **S10/S11 simulation remains a later separate gate**, not authorised by the present memo.
- **M1-clean 2016 remains the active JMP baseline.**

---

*Status: narrow post-estimation diagnostics report (S4 = FAIL, S5 = PASS, S6 = FAIL, S8 = FAIL). The corrected pooled P3a is NOT SA2-ready. M1-clean 2016 remains active. No welfare, no SA2 verdict, no canonical promotion, no S10/S11 simulation, and no M1-clean displacement is taken or authorised by this report.*
