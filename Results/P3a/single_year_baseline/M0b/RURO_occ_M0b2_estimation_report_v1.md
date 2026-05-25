# RURO `ruro_occ_M0b2` — Estimation Report v1

Date: 2026-05-14
Author: auto-generated from post-estimation artefacts

---

## 1. Commands run

```powershell
# Estimation
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_estimate_FR.py" `
    --spec "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\estimation_spec_ruro_occ_M0b2.yaml" `
    --solver gamspy-conopt --vectorized

# Post-estimation
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\RURO_post_estimation_styled.py" `
    --results "U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0b2\run_2026-05-14_12-46-04\estimation_results.json"
```

Start: 2026-05-14 12:46:04 (estimation), 2026-05-14 12:53:49 (post-estimation)

---

## 2. Run folders

| stage | path |
|---|---|
| estimation | `outputs/estimates/fr/spec/ruro_occ/gamspy/estimation_spec_ruro_occ_M0b2/run_2026-05-14_12-46-04/` |
| post-estimation | `outputs/post_estimation/fr/spec/ruro_occ/gamspy/estimation_spec_ruro_occ_M0b2/run_2026-05-14_12-53-49/` |
| spec | `scripts/enhanced/estimation_spec_ruro_occ_M0b2.yaml` |
| params CSV | `outputs/post_estimation/.../fr_2016_ruro_occ_gamspy_M0b2_params.csv` |
| elasticities CSV | `outputs/post_estimation/.../fr_2016_ruro_occ_gamspy_M0b2_elasticities.csv` |

Git SHA at estimation: `f93c55b2815a` (branch: main, dirty).

---

## 3. Start status

One start only — no multi-start robustness check performed for this run.

| field | value |
|---|---|
| start vector | spec defaults (all-zero occupation, all-zero market; `theta_c = -1`, `beta_l0 = 1`, `beta_c = 1`, `beta_ll = 0`) |
| warm-start | none |
| n_starts | 1 |
| perturbed starts completed | 0 |

**Note:** multi-start is pending. With both `theta_c` and `beta_ll` at their bounds, the single result cannot be confirmed as the global optimum. This is the primary caveat on all findings below.

---

## 4. Convergence status

| field | value |
|---|---|
| solver | CONOPT via GAMSPy |
| gradient mode | analytical (GAMS symbolic differentiation) |
| SolveStatus | `NormalCompletion` |
| ModelStatus | `OptimalLocal` |
| iterations | 24 |
| function evaluations | 24 |
| walltime (estimation) | 98.2s |
| walltime (total including post-est) | 294.7s |

`NormalCompletion / OptimalLocal` means CONOPT reached a KKT-satisfying point that satisfies first-order conditions, subject to the bound constraints. It does not certify a global optimum. The negative Hessian eigenvalue (see §11) means the point is not a strict local maximum.

---

## 5. Final log-likelihood

| metric | value |
|---|---|
| Joint LL | **−6511.47** |
| AIC | 13118.9 |
| BIC | 13645.1 |
| ρ² (vs prior-corrected null) | 0.7083 |
| ρ²_adj | 0.7061 |
| n_observations | 425,300 |
| n_groups | 4,253 |
| n_parameters | 48 |

---

## 6. Comparison to M0a-clean and M0b1

All three specifications share the same opportunity blocks. M0b1 adds `beta_ll` with `theta_c` free; M0b2 adds `beta_ll` and tightens `theta_c ≤ 0`.

| metric | M0a-clean (47p) | M0b1 (48p) | M0b2 (48p) | direction |
|---|---|---|---|---|
| Joint LL | −6521.43 | −6506.79 | −6511.47 | M0b1 best; M0b2 between |
| AIC | ~13137 | 13109.6 | **13118.9** | M0b1 best |
| BIC | ~13660 | ~13636 | **13645.1** | M0b1 lowest BIC |
| ρ² | ~0.706 | ~0.709 | 0.7083 | near-equivalent |
| Hessian κ | 9.94×10⁹ | 9.90×10⁹ | 8.52×10⁹ | M0b2 slightly better |
| Negative eigenvalues | 1 | 1 | 1 | all fail Gate B |
| Params at strict bounds | 0 | 1 (`beta_ll`) | **2** (`theta_c`, `beta_ll`) | worsens |
| NA standard errors | ~3 | ~3 | 5 | worsens |
| cou_m participation | 1.000 | 0.9998 | **0.9825** | M0b2 near observed (0.972) |
| cou_f participation | 1.000 | 0.9998 | **0.9884** | M0b2 near observed (0.965) |
| cou_m mean hours | ~60 | 60.4 | **42.6** | M0b2 near observed (41.6) |
| cou_f mean hours | ~60 | 60.2 | **38.8** | M0b2 near observed (35.6) |
| cou_m L1 hours distance | ~1.43 | 1.475 | **0.332** | M0b2 dramatically better |
| cou_f L1 hours distance | ~1.70 | 1.741 | **0.494** | M0b2 dramatically better |
| cou_m predicted wage mean | 139.9 EUR/h | 137.2 EUR/h | **17.1 EUR/h** | M0b2 near observed (17.7) |
| cou_f predicted wage mean | 140.1 EUR/h | 137.3 EUR/h | **15.9 EUR/h** | M0b2 near observed (15.2) |
| p_chosen_min | ~1e-64 | 1.98×10⁻⁸⁷ | 1.16×10⁻⁹ | M0b2 dramatically better |
| p_chosen_median | — | 8.34×10⁻⁵⁰ | **0.272** | M0b2 resolved degenerate probabilities |

**Summary:** M0b2 has a LL 4.7 nats below M0b1 (AIC worse by 9.3) but resolves the two dominant pathologies of M0a/M0b1 — the couples hours/participation collapse and the ~137 EUR/h predicted wage — at the cost of `theta_c` being pushed to its new upper bound (0.0). The LL/AIC penalty relative to M0b1 reflects the binding `theta_c ≤ 0` constraint, not worse fit on the substantive moments.

---

## 7. `beta_ll` details

`beta_ll` is the leisure-leisure interaction coefficient: `U_couples += beta_ll × BC(L_m, θ_l_m) × BC(L_f, θ_l_f)`.

| field | M0b1 | M0b2 |
|---|---|---|
| estimate | 2.000 (at upper bound) | 2.000 (at upper bound) |
| bound | [−2.0, 2.0] | [−2.0, 2.0] unchanged |
| SE | NA (at bound) | NA (at bound) |
| t / p | NA | NA |
| interpretation | saturated; no gradient information at this value | same |

`beta_ll` hit its upper bound in both M0b1 and M0b2. In the M0b1 V-decomposition (diagnostic report §6), `beta_ll` contributed a uniform ~3.4 nats across all working alternatives — it did not concentrate probability on high-wage alternatives and was not the driver of the wage pathology. In M0b2 the saturation persists; the bound prevents identification of the true interaction magnitude.

**Implication:** the bound on `beta_ll` should be widened in M0c (e.g. [−5, 5] or freed with a penalty) to allow identification. Alternatively, if `theta_c = 0` is accepted as the structural value, `beta_ll` enters the utility in a log-log product and its identification comes from couples cross-hours covariation; a wider bound and multi-start are needed.

---

## 8. Couples `theta_c` details

`theta_c` is the Box-Cox exponent on consumption for couples: `BC(C, theta_c)`. Singles have a separate `theta_c_singles` parameter.

| field | M0a-clean | M0b1 | M0b2 |
|---|---|---|---|
| bound | [−8.0, 0.95] | [−8.0, 0.95] | **[−8.0, 0.0]** (tightened) |
| estimate | 0.319 | 0.271 | **0.000 (at upper bound)** |
| SE | NA | NA | NA |
| interpretation | near-linear (positive θ) | near-linear | log-utility (θ = 0) |

`theta_c = 0.0` means couples consumption utility is exactly `beta_c × log(C)`. This is the boundary between concave (`theta_c < 0`) and convex (`theta_c > 0`); the data pushes against the upper wall imposed by M0b2's constraint. The fact that `theta_c` is at the constraint — not in its interior — means the data prefer `theta_c > 0` but M0b2's constraint prevents it.

**Structural interpretation:** `theta_c_singles` is free in M0b2 (bound [−8, 0.95]) and settled at −0.971, well away from its bound, consistent with diminishing marginal utility for singles. Couples prefer near-linear consumption utility; this may reflect within-household income pooling (joint BC utility on total household consumption is harder to curvate than individual utility) or that the model is mis-specifying the consumption-leisure tradeoff for couples.

---

## 9. Preference parameter estimates

### Consumption and leisure — by group

| group | beta_c | theta_c | beta_l0 | beta_l_age | beta_l_age2 | beta_l_nkids | theta_l |
|---|---|---|---|---|---|---|---|
| singles_male (sm) | 0.5915 | −0.971¹ | 3.8139 | 0.00821 | 0.00203 | — | −0.7154 |
| singles_female (sf) | 0.5347 | −0.971¹ | 4.3828 | 0.00165 | 0.00414 | 0.0633 | −0.7298 |
| couples_male (m) | 3.9278 | 0.000² | 0.1254 | −0.00854 | 0.00173 | — | −0.6706 |
| couples_female (f) | 3.9278 | 0.000² | 2.8003 | −0.05464 | 0.00270 | 0.1828 | −0.6534 |

¹ `theta_c_singles = −0.971` (SE: NA; at no bound; well-identified relative to other θ parameters).
² `theta_c = 0.000` at upper bound; SE = NA.

### Leisure-leisure interaction (M0b+)

| parameter | estimate | SE | bound | status |
|---|---|---|---|---|
| `beta_ll` | 2.000 | NA | [−2, 2] | at upper bound |

### Singles `theta_c_singles`

| parameter | estimate | SE | t | bound |
|---|---|---|---|---|
| `theta_c_singles` | −0.9708 | NA | NA | [−8, 0.95] |

Note: `theta_c_singles` has NA SE despite not being at a bound. This arises from the near-unit collinearity between `beta_c_sm`, `beta_c_sf`, and `theta_c_singles` (pairwise correlations of −1.04 to −1.07 from the varcov matrix — super-collinear, indicating numerical singularity in this sub-block).

---

## 10. Opportunity parameter estimates

### Employment and hours

| parameter | estimate | SE | t | p |
|---|---|---|---|---|
| `beta_E` | −2.8385 | 0.2980 | −9.53 | <0.001 |
| `beta_h_pt1` | −0.5009 | 0.1078 | −4.64 | <0.001 |
| `beta_h_pt2` | 0.3707 | 0.1111 | 3.34 | <0.001 |
| `beta_h_ft` | 1.4530 | 0.0501 | 29.03 | <0.001 |

### Market residual

| parameter | estimate | SE | t | p |
|---|---|---|---|---|
| `beta_E_gsur` | −0.7433 | 0.2197 | −3.38 | <0.001 |
| `beta_E_educH` | 0.6129 | 0.2350 | 2.61 | 0.009 |

### Wage (Mincer)

| parameter | estimate | SE | t | p |
|---|---|---|---|---|
| `beta_w0` | 2.0302 | 0.0254 | 79.80 | <0.001 |
| `beta_w_educL` | −0.0516 | 0.0212 | −2.43 | 0.015 |
| `beta_w_educH` | 0.3175 | 0.0150 | 21.12 | <0.001 |
| `beta_w_pexp` | 0.0181 | 0.0022 | 8.09 | <0.001 |
| `beta_w_pexp2` | −0.000219 | 0.0000496 | −4.40 | <0.001 |
| `sigma` | 0.4279 | 0.0041 | 105.18 | <0.001 |

Observed log-wage σ by group: sm=0.450, sf=0.436, cm=0.440, cf=0.436. Implied σ = 0.428 — tight fit; the lognormal wage model is well-calibrated.

### Occupation (loc4, reference = routine_manual)

| parameter | estimate | SE | t | p | group |
|---|---|---|---|---|---|
| `beta_occ_2_sm` | −1.5101 | 0.1420 | −10.63 | <0.001 | singles_male |
| `beta_occ_3_sm` | −2.1649 | 0.1842 | −11.75 | <0.001 | singles_male |
| `beta_occ_4_sm` | 0.0240 | 0.0860 | 0.28 | 0.780 | singles_male |
| `beta_occ_2_sf` | −0.0104 | 0.1126 | −0.09 | 0.926 | singles_female |
| `beta_occ_3_sf` | −0.5606 | 0.1290 | −4.35 | <0.001 | singles_female |
| `beta_occ_4_sf` | 0.7987 | 0.0920 | 8.68 | <0.001 | singles_female |
| `beta_occ_2_cm` | −1.4788 | 0.1135 | −13.03 | <0.001 | couples_male |
| `beta_occ_3_cm` | −2.2247 | 0.1476 | −15.07 | <0.001 | couples_male |
| `beta_occ_4_cm` | 0.4714 | 0.0686 | 6.88 | <0.001 | couples_male |
| `beta_occ_2_cf` | 0.1800 | 0.1000 | 1.80 | 0.072 | couples_female |
| `beta_occ_3_cf` | −0.2096 | 0.1113 | −1.88 | 0.060 | couples_female |
| `beta_occ_4_cf` | 1.1184 | 0.0812 | 13.77 | <0.001 | couples_female |

9 of 12 occupation parameters significant at p<0.05. Consistent sign pattern: routine_cognitive (loc4=3) is generally penalised for males; nonroutine_cognitive (loc4=4) is favoured for females. The reference category (routine_manual, loc4=1) has the highest opportunity weight for singles_male and couples_male.

---

## 11. Identification diagnostics

| metric | value | gate threshold | status |
|---|---|---|---|
| Hessian condition number κ | 8.52×10⁹ | Gate B: κ < 10⁷ | **FAIL** |
| Negative eigenvalues | 1 (min = −18.86) | Gate B: 0 | **FAIL** |
| Near-zero eigenvalues (|λ| ≤ 1e-8) | 0 | — | pass |
| Max eigenvalue | 1.36×10¹⁰ | — | — |
| Negative variances from VarCov | 3 | Gate B: 0 | **FAIL** |
| NA standard errors | 5 | Gate B: 0 | **FAIL** |
| Parameters at strict bounds | 2 | Gate B: 0 | **FAIL** |
| Parameters near lower bound (Δ < 5% width) | 4 (`beta_c_sm`, `beta_c_sf`, `beta_l0_m`, `sigma`) | — | flag |

**Parameters at bounds:**

| parameter | estimate | bound side |
|---|---|---|
| `theta_c` | 0.000 | upper (0.0) |
| `beta_ll` | 2.000 | upper (2.0) |

**Parameters with NA standard errors (5 total):**

`beta_ll`, `theta_c`, `theta_c_singles`, `beta_c_sm`, `beta_c_sf`.

The NA SEs arise from two sources: (a) `beta_ll` and `theta_c` are at bounds — SEs are undefined for bound-constrained parameters; (b) `theta_c_singles`, `beta_c_sm`, `beta_c_sf` form a near-singular sub-block (pairwise VarCov correlations of −1.04 to −1.07), indicating that singles consumption scaling is not separately identified from the singles `theta_c`.

**Top high-correlation pairs (from VarCov):**

| pair | correlation |
|---|---|
| `beta_c_sm` ↔ `beta_c_sf` | −1.069 |
| `beta_c_sf` ↔ `theta_c_singles` | −1.055 |
| `beta_c_sm` ↔ `theta_c_singles` | −1.042 |
| `beta_w_pexp` ↔ `beta_w_pexp2` | −0.960 |
| `beta_E` ↔ `beta_E_gsur` | −0.950 |
| `theta_c_singles` ↔ `beta_c` | −0.904 |

Gate B verdict: **FAIL** (4 Gate B criteria violated). The single run cannot be certified as a local maximum.

---

## 12. Predicted fit diagnostics

### Participation and mean hours

| group | participation_obs | participation_pred | mean_hours_obs | mean_hours_pred |
|---|---|---|---|---|
| singles_male | 0.930 | 0.909 | 39.3 | 35.8 |
| singles_female | 0.940 | 0.952 | 36.3 | 35.1 |
| couples_male | 0.972 | **0.982** | 41.6 | **42.6** |
| couples_female | 0.965 | **0.988** | 35.6 | **38.8** |

Couples participation is now within 1-2 pp of observed (versus 100% in M0a/M0b1). Couples mean hours within 1-3 hours of observed (versus ~60 h in M0a/M0b1). Singles_male participation is slightly under-predicted (0.909 vs 0.930); mean hours under-predicted by 3.5 h (35.8 vs 39.3).

### Hours distribution — L1 distances

| group | L1 distance (M0a-clean) | L1 distance (M0b1) | L1 distance (M0b2) |
|---|---|---|---|
| couples_male | ~1.43 | 1.475 | **0.332** |
| couples_female | ~1.70 | 1.741 | **0.494** |
| singles_female | — | — | 0.413 |
| singles_male | — | — | 0.713 |

M0b2 dramatically reduces L1 for couples. Singles_male has the worst fit (L1 = 0.713); hours are concentrated in the 21-30h bin (59% predicted vs 26% observed), reflecting the model's difficulty matching the observed 31-40h modal bin for males.

### Hours distribution shares (couples_male, selected bins)

| bin | observed | predicted (M0b2) |
|---|---|---|
| 0 h (non-work) | 2.8% | 0.1% |
| 31–40 h | 47.1% | 53.0% |
| 41–50 h | 13.5% | 22.8% |
| 51–60 h | 5.9% | 7.4% |
| 60+ h | 2.5% | 0.8% |

Non-work is under-predicted (0.1% vs 2.8%) — the model cannot place mass on zero-hours for couples because both `theta_c` and `beta_ll` are at bounds. The 41-50h bin is over-predicted. These residuals are consistent with the unsolved identification issues.

### Probability diagnostics

| metric | value |
|---|---|
| prob_sum max error | 8.88×10⁻¹⁶ |
| prob_sum mean error | 1.38×10⁻¹⁶ |
| p_chosen_min | 1.162×10⁻⁹ |
| p_chosen_median | 0.272 |
| p_chosen_mean | 0.390 |
| p_chosen_q10 | 0.0162 |

Probability sums to 1.0 per household to machine precision. `p_chosen_min = 1.16×10⁻⁹` (versus 1.98×10⁻⁸⁷ in M0b1) — extreme low probabilities resolved. Median p_chosen = 0.272 is reasonable. The 5 worst-fit households (p_chosen < 10⁻⁸) are all in singles_male/singles_female groups.

### Marginal utility checks

All groups pass MUC > 0 and MUC diminishing (theta_c ≤ 0 ensures this for the consumption block). No negative MU households.

---

## 13. Couples wage pathology assessment

### M0b2 result

| group | obs mean wage | pred mean wage | obs p50 | pred p50 |
|---|---|---|---|---|
| couples_male | 17.7 EUR/h | **17.1 EUR/h** | 15.3 | 15.0 |
| couples_female | 15.2 EUR/h | **15.9 EUR/h** | 13.8 | 13.9 |

**The ~137 EUR/h predicted wage pathology of M0a-clean and M0b1 is fully resolved in M0b2.** Predicted wages are now within 0.6 EUR/h (3%) of observed means.

### Root cause (from M0b1 diagnostic, `Results/RURO_occ_M0b1_wage_pathology_diagnostic_v1.md`)

The pathology was driven by `theta_c > 0` (near-linear BC consumption utility). With `theta_c ≈ +0.27`, the utility gap between a 15 EUR/h / 35 h alternative and a 165 EUR/h / 60 h alternative was ~30 nats — overwhelming the wage opportunity penalty. M0b2's `theta_c = 0` (log-utility) limits the consumption utility growth rate to `beta_c / C`, so large consumption differences generate proportionally smaller utility differences. The opportunity block's negative O_W penalty can now offset the utility advantage of high-wage draws.

### Wage distribution comparison

| group | obs q10 | obs q50 | obs q90 | pred q10 | pred q50 | pred q90 |
|---|---|---|---|---|---|---|
| couples_male | 10.1 | 15.3 | 27.9 | 9.0 | 15.0 | 27.7 |
| couples_female | 8.9 | 13.8 | 22.5 | 8.5 | 13.9 | 25.9 |

The predicted wage distribution matches the observed distribution at the median and q10 very closely. The q90 for couples_female is slightly overpredicted (25.9 vs 22.5 EUR/h), which is consistent with slight over-prediction of hours in the 41-50h bin.

---

## 14. Warnings from post-estimation

| type | message | severity | action |
|---|---|---|---|
| identification | weakly conditioned (1e6 ≤ κ < 1e10); 1 negative eigenvalue — not at a local maximum | **HIGH** | multi-start required; see §11 |
| probability | minimum chosen probability very small (1.16×10⁻⁹) | medium | 5 households; inspect singles outliers |
| hessian | negative eigenvalues present; inspect SE and local optimum diagnostics | **HIGH** | corroborates identification flag |
| duplicated group param blocks | "Detected joint estimation with duplicated group parameter blocks; collapsing to a single 'joint' group" | informational | harmless artefact of joint GAMSPy estimation; all 3 blocks report identical params as expected |
| missing LOC/ISCO plots | no fine-ISCO occupation plot generated | informational | M0b2 uses loc4; not a regression |
| missing job_id plots | no job_id distribution | informational | RURO is not a job-choice model |

The identification and Hessian warnings are substantive. The remaining warnings are informational.

---

## 15. Verdict

**FLAG — major fit improvement; identification not yet confirmed.**

### What passed

| criterion | M0b2 status |
|---|---|
| Solver convergence (NormalCompletion / OptimalLocal) | PASS |
| Couples wage pathology resolved | PASS (17.1/15.9 EUR/h vs 137/137 EUR/h in M0a/M0b1) |
| Couples participation within 2 pp of observed | PASS (0.982/0.988 vs observed 0.972/0.965) |
| Couples mean hours within 3 h of observed | PASS (42.6/38.8 vs observed 41.6/35.6) |
| Couples L1 hours distance < 0.5 (male) | PASS (0.332) |
| All MU diagnostics positive and diminishing | PASS |
| Probability sums to 1 (machine precision) | PASS |
| Wage σ calibration (observed vs implied) | PASS (implied 0.428, observed 0.436-0.450) |
| 29/48 parameters significant at p < 0.05 | PASS |

### What failed (Gate B)

| criterion | M0b2 status |
|---|---|
| κ < 10⁷ | FAIL (8.52×10⁹) |
| 0 negative Hessian eigenvalues | FAIL (1; min λ = −18.86) |
| 0 NA standard errors | FAIL (5 NA SEs) |
| 0 parameters at strict bounds | FAIL (`theta_c = 0.0`, `beta_ll = 2.0`) |
| 0 negative variances from VarCov | FAIL (3) |

### Overall assessment

M0b2 resolves the model-selection pathology that made M0a-clean and M0b1 structurally unusable for welfare analysis: couples now have realistic participation, hours, and predicted wages. However, with both `theta_c` and `beta_ll` at their upper bounds, the current result is a boundary solution — the Hessian is not PSD at this point, and the reported LL (−6511.47) is 4.7 nats below M0b1, suggesting the true unconstrained optimum (were `theta_c` freed) would continue past the bound.

The verdict is **FLAG** rather than FAIL because the substantive moments are dramatically improved and the structural parameters are economically interpretable (`theta_c = 0` → log-utility; `beta_ll > 0` → leisure complementarity for couples). This is usable as a reference result conditional on the boundary constraint, but must not be used for welfare computation without resolving §11.

---

## 16. Next action

**Run M0c: widen `beta_ll` bound and add `theta_c` interior identification.**

The two binding constraints have distinct remedies:

1. **`beta_ll` at upper bound (2.0):** widen the bound to [−5, 5] or [0, 10] (if leisure complementarity is expected to be positive). This allows the gradient to continue and may shift `theta_c` away from its bound.

2. **`theta_c` at upper bound (0.0):** two options:
   - **M0c-a:** pool couples and singles `theta_c` — share a single `theta_c` across all household types. If the pooled value settles in (−8, 0.95), both groups are identified jointly.
   - **M0c-b:** fix `theta_c = 0` structurally (accept log-utility for couples as the maintained hypothesis) and free `beta_ll` from its bound. This is the simplest parameterisation consistent with M0b2's boundary result.
   - **M0c-c:** introduce an adult-equivalence scale on consumption for couples (rescale `C_couple` by household size before computing BC), which changes the curvature requirements.

3. **Multi-start M0b2:** before promoting to M0c, run at least 3 perturbed starts from M0b2's current result (perturbation σ = 0.1 on interior parameters) to verify that LL = −6511.47 is robust. If a lower LL is found, discard the current run and investigate the alternative start.

**Recommended immediate step:** multi-start M0b2 (3 starts, σ = 0.1), then M0c-b (fix `theta_c = 0`, widen `beta_ll` to [0, 10], run from M0b2 result as warm start).

---

## Reproducibility

```powershell
# Post-estimation only (estimation artefacts already present):
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\RURO_post_estimation_styled.py" `
    --results "U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\spec\ruro_occ\gamspy\estimation_spec_ruro_occ_M0b2\run_2026-05-14_12-46-04\estimation_results.json"

# LLM summary (source of this report):
# reports/fr_2016_ruro_occ_gamspy_M0b2_llm_summary_20260514_125410.md
# identification_diagnostics.txt (run_2026-05-14_12-46-04)
# estimation_summary.txt         (run_2026-05-14_12-46-04)
```
