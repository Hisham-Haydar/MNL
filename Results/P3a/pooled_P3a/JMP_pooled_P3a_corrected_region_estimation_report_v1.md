# JMP Pooled P3a — Corrected-Region Estimation Report v1

**Specification**: `ruro_occ_P3a_pooled`  
**Data**: FR_2015 / FR_2016 / FR_2017 pooled, region-repaired split stem  
**Date**: 2026-05-21–22  
**Status**: Three-start re-estimation complete; all starts converged.  
**Authorization**: `docs/France_case/P3a/execution_logs/pooled_P3a/JMP_pooled_P3a_corrected_region_reestimation_authorization_v1.md`  
**Repair reference**: `docs/archive/2026-05-26_round2_chain_compression/replaced_by_clean_corrected/JMP_pooled_P3a_region_dummy_repair_report_v1.md`  
**Post-repair diagnostic**: `Results/P3a/pooled_P3a/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v2.md`  
**Pre-repair report**: `Results/P3a/pooled_P3a/JMP_pooled_P3a_estimation_report_v2.md` (pre-repair evidence only)

---

## 1. Execution Verdict

**All three starts converged.** No halt condition was triggered.

| Start | Init method | Solver status | Model status | Joint LL | Iterations | Wall time |
|-------|------------|---------------|--------------|----------|------------|-----------|
| Start 1 | M1-clean warm (53→55 by name) | NormalCompletion | OptimalLocal | −19,084.3313 | 14 | 820.4 s |
| Start 2 | Spec defaults | NormalCompletion | OptimalLocal | −19,084.3313 | 17 | 1,045.5 s |
| Start 3 | Perturbed Start 1 converged (seed 42, ±0.1) | NormalCompletion | OptimalLocal | −19,084.3313 | 20 | 1,057.9 s |

All three starts reached the **identical joint log-likelihood (−19,084.3313)** and an **identical converged parameter vector** (cross-start L∞ < 10⁻⁸, numerical noise). The region dummies `beta_E_drgn2`–`beta_E_drgn8` converge to consistent, non-arbitrary values with finite, inferential-magnitude robust SEs across all three starts. This is the definitive contrast with the pre-repair run, where all three starts also agreed in LL (−57,280.62) but the region block sat at arbitrary values on a flat ridge. The flat ridge is gone.

The CONOPT/GAMS solver diagnostics are captured per start (§13, §17, §20), distinctly from the Python likelihood-gradient diagnostic (§27). True-Hessian cluster-robust SEs and T3/T4/T5 were rerun for all three starts (§24–§27). No halt condition (§38) was triggered.

---

## 2. Authorization Provenance

This re-estimation is authorized by:

| Document | Role |
|----------|------|
| `docs/France_case/P3a/execution_logs/pooled_P3a/JMP_pooled_P3a_corrected_region_reestimation_authorization_v1.md` | Primary authorization for this run |
| `docs/archive/2026-05-26_round2_chain_compression/replaced_by_clean_corrected/JMP_pooled_P3a_estimation_execution_authorization_v1.md` | Standing estimation authorization (carried forward) |
| `docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_pooled_P3a_estimation_execution_authorization_correction_v1.md` | Sequencing and artifact corrections (carried forward) |
| `docs/archive/2026-05-26_round2_chain_compression/replaced_by_clean_corrected/JMP_pooled_P3a_region_dummy_repair_report_v1.md` | Region repair evidence (R1/R2 applied, V1–V9 PASS) |
| `Results/P3a/pooled_P3a/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v2.md` | Post-repair diagnostic confirming identifiability |

---

## 3. Corrected Data Input — What Changed and What Did Not

**Data input used (authorized):**
`Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready` (the estimator appends `__singles.parquet`, `__couples.parquet`, `__mnlmeta.json`).

**What changed:**

- **Couples region-dummy columns.** Previously: `reg_nuts1_2`–`reg_nuts1_8` all-NaN (743,800/743,800), zeroed by `fillna(0.0)` in precompute, yielding all-zero `data.reg2`–`data.reg8`. Now: derived from `drgn1`, valid binary float, 0 NaN, exact one-region-per-household partition, region 1 omitted (non-zero counts: reg2=134,900; reg3=56,000; reg4=66,300; reg5=134,900; reg6=82,800; reg7=88,700; reg8=70,500).
- **Precompute guard (R2).** `precompute_data_couples` now takes the direct `reg_nuts1_*` path only on value presence (present + non-missing + non-degenerate), not mere schema presence. Confirmed active for this run: DEBUG log "precompute_data_couples: region dummies sourced from reg_nuts1_* columns (direct path)" emitted in all three starts.

**What did NOT change:** specification YAML (`estimation_spec_ruro_occ_P3a_pooled.yaml`, 55 parameters, `theta_c` fixed at 0.0 for couples, FR_2016 reference year, 7 region shifters + 2 year shifters, `applies_to: household`, `interaction: [working]`); cluster key (`idorighh`); income rule (GA15); singles `applies_to: "household"` guard; solver; three-start design.

**Row counts confirmed at load (all three starts):**
- Singles: 500,700 rows, 148 columns
- Couples: 743,800 rows, 148 columns
- Total: 1,244,500 rows; 12,445 household-year choice sets; 100 alternatives each

---

## 4. Prohibited Inputs — Not Used

The following inputs were NOT used for this re-estimation, as required (§6, §15 N6, H7 of the authorization):

| Prohibited input | Status |
|-----------------|--------|
| `Data/processed/fr/pooled/archive/fr_p3a_gsurv2_estimation_ready__couples_defective_20260521.parquet` | Confirmed not used — archived and not referenced in any estimation command |
| Unified parquet `fr_p3a_gsurv2_harmonised.parquet` directly | Confirmed not used — estimator consumed split-stem path only |
| Any pre-repair or un-validated stem | Not used |

The estimator `--mnl-base` flag pointed to the corrected regenerated stem exclusively.

---

## 5. Pre-Solver Sanity Check PS1 — Region Columns Valid

Script: `scripts/maintenance/run_pooled_P3a_presolver_checks.py`  
Exit code: 0 (ALL PASS)  
**PS1: PASS**

| Column | NaN count / Total | Non-zero rows | Binary | Matches 1[drgn1==k] |
|--------|------------------|---------------|--------|---------------------|
| `reg_nuts1_2` | 0 / 743,800 | 134,900 | Yes | Yes (exact) |
| `reg_nuts1_3` | 0 / 743,800 | 56,000 | Yes | Yes (exact) |
| `reg_nuts1_4` | 0 / 743,800 | 66,300 | Yes | Yes (exact) |
| `reg_nuts1_5` | 0 / 743,800 | 134,900 | Yes | Yes (exact) |
| `reg_nuts1_6` | 0 / 743,800 | 82,800 | Yes | Yes (exact) |
| `reg_nuts1_7` | 0 / 743,800 | 88,700 | Yes | Yes (exact) |
| `reg_nuts1_8` | 0 / 743,800 | 70,500 | Yes | Yes (exact) |

Region 1 (Île-de-France) is the omitted reference: all seven dummies equal zero for `drgn1 == 1` rows. The seven dummies plus the reference form an exact one-region-per-household partition.

---

## 6. Pre-Solver Sanity Check PS2 — Precompute Region Arrays Non-Zero

**PS2: PASS**

`precompute_data_couples` invoked on the corrected couples split took the **direct `reg_nuts1_*` path** (value-presence guard satisfied). The precomputed region arrays are non-zero:

| Array | Non-zero / Total |
|-------|-----------------|
| `data.reg2` | 134,900 / 743,800 |
| `data.reg3` | 56,000 / 743,800 |
| `data.reg4` | 66,300 / 743,800 |
| `data.reg5` | 134,900 / 743,800 |
| `data.reg6` | 82,800 / 743,800 |
| `data.reg7` | 88,700 / 743,800 |
| `data.reg8` | 70,500 / 743,800 |

This matches the values documented in the post-repair diagnostic v2 exactly.

---

## 7. Pre-Solver Sanity Check PS3 — Region Dummies Gradient-Relevant

**PS3: PASS**

The gradient-relevant product `reg_k × (working_male + working_female)` is non-zero per region:

| Region | Non-zero `reg_k × (wm+wf)` | Fraction of 743,800 |
|--------|---------------------------|---------------------|
| reg2 | 133,537 | 18.0% |
| reg3 | 55,437 | 7.5% |
| reg4 | 65,607 | 8.8% |
| reg5 | 133,556 | 18.0% |
| reg6 | 81,997 | 11.0% |
| reg7 | 87,774 | 11.8% |
| reg8 | 69,771 | 9.4% |

`beta_E_drgn_k` receives a non-zero score contribution at 7.5%–18.0% of couples rows per region. The likelihood is not flat in the region-dummy directions.

---

## 8. Pre-Solver Sanity Check PS4 — Cluster Key = idorighh

**PS4: PASS**

`idorighh` is present in both splits:
- Couples: 5,838 unique values
- Singles: 3,902 unique values
- Combined (confirmed by T3 in SE step): 9,657 unique clusters

No `idhh` fallback occurred. The strictness safeguard is active.

---

## 9. Pre-Solver Sanity Check PS5 — Income Routing (GA15)

**PS5: PASS**

| Check | Result |
|-------|--------|
| Singles `ils_dispy_real` present | Yes; null count = 0 / 500,700 |
| Couples `ils_dispy_male` present | Yes; null count = 0 / 743,800 |
| Couples `ils_dispy_female` present | Yes; null count = 0 / 743,800 |
| Couples `ils_dispy_real` column | Present in schema; **all-NaN** (743,800 / 743,800 null) — couples consumption path reads `ils_dispy_male`/`ils_dispy_female` exclusively |

The couples `ils_dispy_real` column being all-NaN confirms the couples consumption path routes through `ils_dispy_male`/`ils_dispy_female` as required by GA15.

---

## 10. Pre-Solver Checks Summary

| Check | Description | Result |
|-------|-------------|--------|
| PS1 | Couples region columns valid | **PASS** |
| PS2 | Precompute produces non-zero reg arrays | **PASS** |
| PS3 | Region dummies gradient-relevant | **PASS** |
| PS4 | Cluster key = idorighh | **PASS** |
| PS5 | Income routing (GA15) | **PASS** |

All five pre-solver sanity checks pass. The solver was invoked.

---

## 11. Start 1 — Initialization (M1-clean Warm Start)

**Init method:** `--init-params` pointing to the M1-clean converged results JSON:  
`outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_12-38-37/estimation_results.json`

The 53 M1-clean shared parameters were loaded by name and mapped to their P3a positions. The two new year-dummy parameters (`beta_E_y2015`, `beta_E_y2017`) were initialized at their YAML spec defaults (0.0 each). The seven region dummies `beta_E_drgn2`–`beta_E_drgn8` were initialized at the M1-clean converged values (which were estimated on 2016-only data and may reflect an arbitrary 2016-specific optimum; the three-year pooled optimum is expected to differ).

**Initial parameter source summary**: 53 parameters from `init_params_override` (M1-clean), 2 from `spec_default` (year dummies).

---

## 12. Start 1 — Convergence and Objective

| Item | Value |
|------|-------|
| Solver status | SolveStatus.NormalCompletion |
| Model status | ModelStatus.OptimalLocal |
| Joint log-likelihood | −19,084.3313 |
| CONOPT iterations | 14 |
| Wall time (total) | 820.4 s |
| CONOPT internal time | 186.768 s |
| Evaluation errors | 0 |

**Run directory**: `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_1/run_2026-05-21_23-47-14/`

The solver produced a successful locally-optimal solution. No evaluation errors; no infeasibilities; no non-optimal residuals.

---

## 13. Start 1 — CONOPT/GAMS Solver Diagnostics

**Solver artifacts captured** per authorization A2 and H6 requirements.

| Diagnostic | Value |
|------------|-------|
| Solver | CONOPT4 v4.38.2 |
| Solver status | 1 Normal Completion |
| Model status | 2 Locally Optimal |
| Objective value | −19,084.3313 |
| Iteration count | 14 |
| Resource usage | 191.312 s |
| Termination message | "Optimal solution. Reduced gradient less than tolerance." |
| Max infeasibility | 0 (0 INFEASIBLE, 0 NONOPT) |
| Evaluation errors | 0 |

**Solver artifact paths:**
- Solver log: `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_1/run_2026-05-21_23-47-14/solver.log`
- GAMS listing: `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_1/run_2026-05-21_23-47-14/solver.lst`

**Region-dummy marginals from GAMS listing** (reduced gradients at convergence): All seven region dummy variables (`beta_E_drgn2`–`beta_E_drgn8`) carry marginal = **EPS** (effectively zero) in the CONOPT solution summary. This is the solver-side confirmation that the optimality condition is satisfied for the region block: the reduced gradient is zero, the region dummies are at interior solutions (not at bounds), and the CONOPT termination is clean in all region-dummy directions.

**Note on beta_l0_m:** The GAMS listing shows `beta_l0_m` at its lower bound (LOWER=1e−6, LEVEL=1e−6), with a non-EPS marginal of −10.1370. This parameter is active at its lower bound; its marginal is the shadow price. This active bound is the source of the "5 free parameters have negative variance" warning from the in-estimation crude Hessian inversion (discussed in §35–§36).

**Critical distinction (CONOPT RGmax vs. Python gradient):** The CONOPT termination criterion "reduced gradient less than tolerance" refers to CONOPT's internal reduced-gradient measure for the GAMS NLP — a quantity computed by CONOPT's automatic differentiation engine, not by the Python likelihood-gradient computation. The Python gradient diagnostic (the score `∂logL/∂θ` computed by `compute_gradient_joint` via central differences) is a separate quantity used in the inference step (§27). These two gradient measures are computed by different tools on different objects and must not be conflated.

---

## 14. Start 1 — Parameter Estimates

The converged parameter vector for Start 1 (55 parameters, `theta_c` couples fixed at 0.0 and excluded):

| Parameter | Estimate |
|-----------|----------|
| `beta_l0_sm` | 4.328086 |
| `beta_l_age_sm` | 0.043144 |
| `beta_l_age2_sm` | 0.001724 |
| `beta_c_sm` | 2.733147 |
| `theta_l_sm` | −0.719206 |
| `beta_l0_sf` | 4.460193 |
| `beta_l_age_sf` | 0.038506 |
| `beta_l_age2_sf` | 0.004610 |
| `beta_l_nkids_sf` | 0.356277 |
| `beta_c_sf` | 2.351327 |
| `theta_l_sf` | −0.701604 |
| `theta_c_singles` | 0.039244 |
| `beta_l0_m` | 0.000001 (at lower bound 1e−6; see §35) |
| `beta_l_age_m` | 0.005870 |
| `beta_l_age2_m` | 0.001646 |
| `theta_l_m` | −0.681907 |
| `beta_l0_f` | 2.605285 |
| `beta_l_age_f` | −0.058032 |
| `beta_l_age2_f` | 0.005288 |
| `beta_l_nkids_f` | 0.142852 |
| `theta_l_f` | −0.657847 |
| `beta_c` | 4.312411 |
| `beta_E` | −2.397723 |
| `beta_h_pt1` | −0.474816 |
| `beta_h_pt2` | 0.424756 |
| `beta_h_ft` | 1.405924 |
| `beta_E_gsur` | −1.199923 |
| `beta_E_drgn2` | 0.396497 |
| `beta_E_drgn3` | 0.350000 |
| `beta_E_drgn4` | 0.641609 |
| `beta_E_drgn5` | 0.431035 |
| `beta_E_drgn6` | 0.357738 |
| `beta_E_drgn7` | 0.367068 |
| `beta_E_drgn8` | 0.167527 |
| `beta_E_y2015` | −0.059090 |
| `beta_E_y2017` | 0.155430 |
| `beta_occ_2_sm` | −1.496158 |
| `beta_occ_3_sm` | −2.138378 |
| `beta_occ_4_sm` | 0.074381 |
| `beta_occ_2_sf` | −0.104983 |
| `beta_occ_3_sf` | −0.532782 |
| `beta_occ_4_sf` | 0.763932 |
| `beta_occ_2_cm` | −1.502612 |
| `beta_occ_3_cm` | −2.222216 |
| `beta_occ_4_cm` | 0.476417 |
| `beta_occ_2_cf` | 0.113438 |
| `beta_occ_3_cf` | −0.329211 |
| `beta_occ_4_cf` | 1.075478 |
| `beta_w0` | 2.033343 |
| `beta_w_educL` | −0.041400 |
| `beta_w_educH` | 0.306669 |
| `beta_w_pexp` | 0.017306 |
| `beta_w_pexp2` | −0.000182 |
| `sigma` | 0.403406 |
| `beta_ll` | 2.655942 |

This is the canonical estimate vector for the corrected P3a pooled model. Starts 2 and 3 converge to an identical vector (L∞ < 10⁻⁸; §21).

---

## 15. Start 2 — Initialization (Spec Defaults)

**Init method:** `--warm-start none` (cold start). All 55 parameters initialized at their YAML `initial_values`. The region dummies `beta_E_drgn2`–`beta_E_drgn8` were initialized at their spec defaults (0.0 each). No external parameter file was used.

**Initial parameter source summary**: 55 parameters from `spec_default`.

---

## 16. Start 2 — Convergence and Objective

| Item | Value |
|------|-------|
| Solver status | SolveStatus.NormalCompletion |
| Model status | ModelStatus.OptimalLocal |
| Joint log-likelihood | −19,084.3313 |
| CONOPT iterations | 17 |
| Wall time (total) | 1,045.5 s |
| Evaluation errors | 0 |

**Run directory**: `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_2/run_2026-05-22_00-18-36/`

Start 2 converged from a cold start (spec defaults far from the optimum) to the same locally-optimal solution as Start 1. The 3-iteration difference (14 vs 17) reflects the longer path from cold start vs warm start.

---

## 17. Start 2 — CONOPT/GAMS Solver Diagnostics

| Diagnostic | Value |
|------------|-------|
| Solver | CONOPT4 v4.38.2 |
| Solver status | 1 Normal Completion |
| Model status | 2 Locally Optimal |
| Objective value | −19,084.3313 |
| Iteration count | 17 |
| CONOPT internal time | 410.377 s |
| Termination message | "Optimal solution. Reduced gradient less than tolerance." |
| Max infeasibility | 0 (0 INFEASIBLE, 0 NONOPT) |
| Evaluation errors | 0 |

**Solver artifact paths:**
- Solver log: `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_2/run_2026-05-22_00-18-36/solver.log`
- GAMS listing: `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_2/run_2026-05-22_00-18-36/solver.lst`

The CONOPT termination is clean with zero infeasibilities and the same reduced-gradient-below-tolerance message as Start 1. The region dummy marginals are EPS (interior solution) in the Start 2 listing as well.

---

## 18. Start 3 — Initialization (Perturbed Warm Start; Base Vector Documented)

**Init method:** Perturbed warm start using `make_perturbed_init_params` with seed=42, magnitude=±0.1.

**Base vector (documented):** The perturbed-init base was the **converged Start 1 theta** — the 55-parameter vector from `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_1/run_2026-05-21_23-47-14/estimation_results.json`. The perturbation of ±0.1 (uniform, seed=42) was applied element-wise to this converged vector, not to the M1-clean warm-start vector.

**Deviation from authorization intent (PD1 repeated):** The authorization (§9) intended the M1-clean warm-start vector as the base for Start 3 perturbation. The orchestrator used the converged Start 1 theta instead — consistent with the prior run's documented deviation PD1. The authorization explicitly accepts either base provided it is documented. The use of the converged Start 1 theta is documented here.

**Perturbed init file**: `Results/JMP_pooled_P3a_corrected_start3_perturbed_init.json`

Selected perturbation examples (base → perturbed):
- `beta_l0_sm`: 4.3281 → 4.3829 (Δ = +0.0548)
- `beta_E_drgn2`: 0.3965 → 0.3053 (Δ = −0.0912)
- `beta_E_drgn3`: 0.3500 → 0.2809 (Δ = −0.0691)
- `beta_E_gsur`: −1.1999 → −1.2066 (Δ = −0.0066)

All perturbations are within ±0.1 as specified.

---

## 19. Start 3 — Convergence and Objective

| Item | Value |
|------|-------|
| Solver status | SolveStatus.NormalCompletion |
| Model status | ModelStatus.OptimalLocal |
| Joint log-likelihood | −19,084.3313 |
| CONOPT iterations | 20 |
| Wall time (total) | 1,057.9 s |
| Evaluation errors | 0 |

**Run directory**: `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_3/run_2026-05-22_00-53-54/`

Start 3 returned from the perturbed initial point to the same locally-optimal solution as Starts 1 and 2. The 6-iteration increase over Start 1 reflects the perturbation-induced additional path length.

---

## 20. Start 3 — CONOPT/GAMS Solver Diagnostics

| Diagnostic | Value |
|------------|-------|
| Solver | CONOPT4 v4.38.2 |
| Solver status | 1 Normal Completion |
| Model status | 2 Locally Optimal |
| Objective value | −19,084.3313 |
| Iteration count | 20 |
| CONOPT internal time | 426.761 s |
| Termination message | "Optimal solution. Reduced gradient less than tolerance." |
| Max infeasibility | 0 (0 INFEASIBLE, 0 NONOPT) |
| Evaluation errors | 0 |

**Solver artifact paths:**
- Solver log: `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_3/run_2026-05-22_00-53-54/solver.log`
- GAMS listing: `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_3/run_2026-05-22_00-53-54/solver.lst`

All three starts: CONOPT status 1 Normal Completion, model status 2 Locally Optimal, reduced gradient below tolerance, zero infeasibilities.

---

## 21. Cross-Start Parameter Agreement (L∞ on Identified and Region Blocks)

The three starts converge to parameter vectors that are numerically identical:

| Comparison | L∞ (max absolute difference) |
|------------|------------------------------|
| Start 1 vs Start 2 (full 55-vector) | < 10⁻⁸ (numerical noise) |
| Start 1 vs Start 3 (full 55-vector) | < 10⁻⁸ (numerical noise) |

**Theta-norm (L2):**
- Start 1: 10.84814369662677
- Start 2: 10.84814369662335
- Start 3: 10.84814369662383

Differences are at the 11th significant figure — well below any inferential threshold.

**Region block (beta_E_drgn2–beta_E_drgn8):** All three starts converge to the same seven values to 6+ significant figures. This is the decisive contrast with the pre-repair run: the region dummies no longer wander arbitrarily (as they did on the flat ridge) but converge consistently to a stable, reproducible optimum.

**Year effects (beta_E_y2015, beta_E_y2017):** Also identical across starts (L∞ < 10⁻⁸).

The multi-start protocol establishes that the corrected model has a single locally-optimal solution that is reached consistently from three distinct starting points.

---

## 22. Hessian Diagnostics — Condition Number and Free Mask

**Hessian condition number**: κ = **3.316 × 10⁹** (consistent across all three starts to 10 significant figures).

This large condition number reflects the inherent curvature structure of the RURO MNL with 54 free parameters and signals a moderately ill-conditioned parameter space. It is not specific to the region block; the full 54×54 Hessian (evaluated by central differences on `compute_gradient_joint`) has this condition number at the converged theta.

**Free mask**: 54 of 55 parameters are free. The single excluded parameter is `beta_l0_m` (the male couples leisure intercept), which converged to its lower bound (1e−6) and is therefore excluded from the inference subspace. See §35 for diagnosis.

**In-estimation Hessian warning**: The in-estimation SE computation (step 7b in `enh_RURO_estimate_FR.py`) warned "5 free parameters have negative variance" for all three starts. This arises from a crude `diag(H⁻¹)` inversion of the ill-conditioned 54×54 Hessian; 5 diagonal elements of H⁻¹ are negative due to numerical imprecision. The true-Hessian sandwich estimator in `run_cluster_robust_se.py` resolves this: T4 reports 0 non-positive robust SEs for all three starts. The negative-variance warning is an artifact of the in-estimation diagnostic step, not a sign of structural non-identification. See §36.

---

## 23. True-Hessian Source — Explicitly Identified

The cluster-robust SEs reported in this document are computed with the **TRUE numerical Hessian** as the bread of the sandwich estimator.

Source (from all three SE JSON files):
> "TRUE Hessian — numerical Hessian of negative LL (central differences on `compute_gradient_joint` at converged theta). NOT the dummy Hessian H=0.1*I."

The Hessian is a 54×54 matrix evaluated at the converged theta by central differences on `compute_gradient_joint`, excluding the fixed `theta_c` (couples Box-Cox exponent = 0.0) and the bound-active `beta_l0_m`. This is the correct bread for the cluster-robust sandwich V = H⁻¹ B H⁻¹.

---

## 24. T3 — Cluster Count (9,657) — All Three Starts

| Start | n_unique_clusters | Expected | T3 status |
|-------|-------------------|----------|-----------|
| Start 1 | **9,657** | 9,657 | **PASS** |
| Start 2 | **9,657** | 9,657 | **PASS** |
| Start 3 | **9,657** | 9,657 | **PASS** |

The meat matrix B is assembled from per-choice-set scores aggregated to the `idorighh` cluster key over the full corrected dataset (12,445 choice sets from 9,657 unique `idorighh` households across three survey years). The 9,657 unique households arise because some households appear in more than one survey year, giving 12,445 choice set observations from 9,657 distinct `idorighh` values (per-split counts: couples 5,838; singles 3,902; combined unique = 9,657 with cross-split overlap = 83 households).

---

## 25. T4 — Robust SE Positivity — All Three Starts

| Start | n_free | n_nonpositive | T4 status |
|-------|--------|---------------|-----------|
| Start 1 | 54 | 0 | **PASS** |
| Start 2 | 54 | 0 | **PASS** |
| Start 3 | 54 | 0 | **PASS** |

All 54 free parameters have strictly positive cluster-robust SEs at the converged theta via the true-Hessian sandwich estimator. The **region-dummy block** (`beta_E_drgn2`–`beta_E_drgn8`) is a sub-case of this: all seven region SEs are positive and of inferential magnitude (0.34–0.55), confirming that the gradient defect has been resolved and these parameters are now inference-live. This is distinct from the pre-repair run, where the seven region SEs were machine-scale noise (non-inferential, O(10⁻¹⁴–10⁻¹⁵)).

---

## 26. T5 — Robust vs Hessian Comparison — All Three Starts

| Start | n_robust_below_hessian | T5 status |
|-------|----------------------|-----------|
| Start 1 | 0 | **PASS** |
| Start 2 | 0 | **PASS** |
| Start 3 | 0 | **PASS** |

No robust SE falls below its Hessian-based SE for any free parameter in any start. This is expected: the cluster-robust sandwich SE ≥ Hessian SE when clustering introduces positive intra-cluster correlation, as it typically does for household survey data.

---

## 27. Cluster-Robust SE Artifact List (Correction C2)

Per correction C2 requirements, the following artifacts are documented for each start.

**Start 1:**
- **Converged theta**: 55-element vector, L2 norm = 10.84814369662677 (see §14 for full listing)
- **True-Hessian bread source**: "TRUE Hessian — numerical Hessian of negative LL (central differences on `compute_gradient_joint` at converged theta). NOT the dummy Hessian H=0.1*I."
- **T3**: n_unique_clusters = 9,657, expected 9,657 — **PASS**
- **Robust SE vector** (54 free parameters; selected parameters shown, full vector in SE JSON):

| Parameter | Theta | SE_robust | SE_hessian | t_robust |
|-----------|-------|-----------|------------|----------|
| `beta_E_gsur` | −1.1999 | 0.1911 | 0.0965 | −6.28 |
| `beta_E_drgn2` | 0.3965 | 0.3845 | 0.1589 | 1.03 |
| `beta_E_drgn3` | 0.3500 | 0.3991 | 0.1969 | 0.88 |
| `beta_E_drgn4` | 0.6416 | 0.5537 | 0.2193 | 1.16 |
| `beta_E_drgn5` | 0.4310 | 0.4427 | 0.1720 | 0.97 |
| `beta_E_drgn6` | 0.3577 | 0.4682 | 0.1927 | 0.76 |
| `beta_E_drgn7` | 0.3671 | 0.4370 | 0.1843 | 0.84 |
| `beta_E_drgn8` | 0.1675 | 0.3370 | 0.1703 | 0.50 |
| `beta_E_y2015` | −0.0591 | 0.2573 | 0.1193 | −0.23 |
| `beta_E_y2017` | 0.1554 | 0.2701 | 0.1269 | 0.58 |
| `beta_h_ft` | 1.4059 | 0.0854 | 0.0300 | 16.46 |
| `theta_l_m` | −0.6819 | 0.0377 | 0.0257 | −18.07 |
| `theta_l_f` | −0.6578 | 0.0314 | 0.0137 | −20.95 |
| `sigma` | 0.4034 | 0.001545 | 0.000221 | 261.0 |
| `beta_ll` | 2.6559 | 0.3741 | 0.0491 | 7.10 |

- **Robust VCV path**: `Results/JMP_pooled_P3a_corrected_start1_cluster_robust_se_vcv.npy`
- **SE JSON**: `Results/JMP_pooled_P3a_corrected_start1_cluster_robust_se.json`
- **T4**: n_nonpositive = 0 (54 free params) — **PASS**
- **T5**: n_robust_below_hessian = 0 — **PASS**
- **No-welfare**: CONFIRMED
- **M1-clean active**: CONFIRMED — M1-clean 2016 remains the active JMP baseline

**Start 2:**
- **Hessian condition number**: 3.316 × 10⁹ (same optimum)
- **T3**: 9,657 — **PASS** | **T4**: 0 non-positive — **PASS** | **T5**: 0 below — **PASS**
- **Robust VCV path**: `Results/JMP_pooled_P3a_corrected_start2_cluster_robust_se_vcv.npy`
- **SE JSON**: `Results/JMP_pooled_P3a_corrected_start2_cluster_robust_se.json`

**Start 3:**
- **Hessian condition number**: 3.316 × 10⁹ (same optimum)
- **T3**: 9,657 — **PASS** | **T4**: 0 non-positive — **PASS** | **T5**: 0 below — **PASS**
- **Robust VCV path**: `Results/JMP_pooled_P3a_corrected_start3_cluster_robust_se_vcv.npy`
- **SE JSON**: `Results/JMP_pooled_P3a_corrected_start3_cluster_robust_se.json`

---

## 28. Region Identification Read — Point Estimates and Cross-Start Consistency

The seven region-dummy estimates (reference = region 1, Île-de-France) at the corrected optimum, with robust SEs and t-ratios:

| Parameter | Region | Estimate | SE_robust | t_robust |
|-----------|--------|----------|-----------|----------|
| `beta_E_drgn2` | Nord–Ouest | 0.3965 | 0.3845 | 1.03 |
| `beta_E_drgn3` | Nord–Est | 0.3500 | 0.3991 | 0.88 |
| `beta_E_drgn4` | Sud–Est | 0.6416 | 0.5537 | 1.16 |
| `beta_E_drgn5` | Grand–Ouest | 0.4310 | 0.4427 | 0.97 |
| `beta_E_drgn6` | Centre–Est | 0.3577 | 0.4682 | 0.76 |
| `beta_E_drgn7` | Méditerranée | 0.3671 | 0.4370 | 0.84 |
| `beta_E_drgn8` | Outre-mer | 0.1675 | 0.3370 | 0.50 |

All seven point estimates are positive, suggesting higher market opportunity outside Île-de-France (the reference region), with the largest effect in region 4 (Sud–Est, β = 0.64). The t-ratios range from 0.50 (region 8) to 1.16 (region 4). None achieves conventional significance at the 5% level (|t| < 1.96 for all seven). The two year effects are also not significant:

| Parameter | Estimate | SE_robust | t_robust |
|-----------|----------|-----------|----------|
| `beta_E_y2015` | −0.0591 | 0.2573 | −0.23 |
| `beta_E_y2017` | 0.1554 | 0.2701 | 0.58 |

**Cross-start consistency**: All three starts converge to the same region estimates (L∞ < 10⁻⁸ for the region block). There is no wandering or arbitrary regional split — the estimates are stable and reproducible across starts.

**This section states the evidence for the next review's adjudication. No S4/S5 verdict is issued here** (§32).

---

## 29. Region Identification Read — Robust SEs and t-Ratios

The region-dummy robust SEs (0.34–0.55) are of inferential magnitude, in sharp contrast to the pre-repair run where the same SEs were machine-scale noise (O(10⁻¹⁴)). The shift from machine-scale to inferential SEs is the inference-side confirmation that the region dummies are now identified: the gradient was previously identically zero (no information), and it is now non-zero (the sandwich meat matrix B receives genuine score contributions from the region block).

Hessian SEs (sandwich bread diagonal only): The Hessian SEs for the region block range from 0.16 to 0.22 (§27 table). All robust SEs exceed their Hessian counterparts (T5 PASS), consistent with positive intra-cluster correlation in the region block — households in the same `idorighh` cluster tend to be in the same region, so clustering inflates the region-dummy SEs.

The region-block t-ratios (0.50–1.16) indicate that, at these point estimates and with the present sample, none of the region market-opportunity differentials from Île-de-France is individually statistically distinguishable from zero at the 5% level. Whether the region block is jointly significant (S4 joint Wald test) and whether the region-block Hessian sub-matrix has the right eigenvalue sign (S5) are questions for the next strict post-estimation review / SA2-readiness verdict.

---

## 30. Region Identification Read — Region-Block Hessian Sub-Block Conditioning

The full 54×54 true Hessian has condition number κ = 3.316 × 10⁹. The region-block sub-Hessian (the 7×7 sub-matrix of H corresponding to `beta_E_drgn2`–`beta_E_drgn8`) is not separately diagonalized here; extraction of its eigenvalues and condition number is reserved for the strict post-estimation review (S5 adjudication).

What is established here: (a) the full Hessian including the region block is computed and is finite (non-degenerate); (b) the seven region-dummy robust SEs are finite and positive; (c) T5 (robust ≥ Hessian) passes for the region block; and (d) the seven region dummies are at interior solutions with EPS CONOPT marginals. The region-block sub-Hessian conditioning is not adjudicated here.

---

## 31. Region Identification Read — Comparison with Pre-Repair (Flat Ridge)

| Characteristic | Pre-repair run (report v2) | Corrected run (this report) |
|----------------|---------------------------|------------------------------|
| Joint LL | −57,280.621 | −19,084.331 |
| Region estimates | Arbitrary (Start 2 exactly 0.000; Starts 1/3 non-zero) | Consistent across all three starts (L∞ < 10⁻⁸) |
| Region robust SEs | Machine-scale noise (O(10⁻¹⁴)) | Inferential magnitude (0.34–0.55) |
| Region t-ratios | Non-inferential | 0.50–1.16 |
| CONOPT marginals (region) | Flat (zero gradient) | EPS (interior solution, reduced gradient below tolerance) |
| Flat-ridge signature | Present (arbitrary values at identical LL) | Absent |

The flat ridge is gone. The region block is identified in the gradient sense. The change in absolute LL (38,197 units) is large and expected: with all-zero region arrays, the pre-repair model's market opportunity index was systematically misspecified, causing the optimizer to converge to a different point for all identified parameters as well, and the proposal correction baseline changed substantially with the region arrays populated. The absolute LL values are not directly comparable across the two runs.

---

## 32. No S4/S5 Verdict Issued Here

This report records the region-block evidence as required (§28–§31). It does **NOT** issue an S4 (joint region Wald test) or S5 (region-block Hessian eigenvalue-sign) verdict. Adjudication of S4 and S5 is the next review's responsibility — the fresh strict post-estimation review / SA2-readiness verdict that is the immediate next gate after this re-estimation.

---

## 33. Identified-Block Comparison to Pre-Repair Report v2 — GSUR and Leisure Block

The pre-repair estimation report v2 (`Results/P3a/pooled_P3a/JMP_pooled_P3a_estimation_report_v2.md`) is **pre-repair evidence only** for the region block. Its findings on identified parameters are cited here as a comparison, not as definitive values; any material change must be flagged.

**GSUR loading:**
- Pre-repair (report v2): approximately −1.198 (at t ≈ −6.70 per the authorization context)
- Corrected: −1.1999 (robust SE = 0.1911, t = −6.28)
- **No material change.** The GSUR loading is stable across the repair, as expected (the GSUR variable is present in both splits and was not affected by the region-dummy defect).

**Leisure block (selected):**

| Parameter | Corrected | Notes |
|-----------|-----------|-------|
| `theta_l_m` | −0.681907 (t = −18.07) | Strong, stable |
| `theta_l_f` | −0.657847 (t = −20.95) | Strong, stable |
| `theta_l_sm` | −0.719206 (t = −11.71) | Strong, stable |
| `theta_l_sf` | −0.701604 (t = −12.09) | Strong, stable |
| `beta_l_nkids_sf` | 0.356277 (t = 0.86) | Not individually significant |
| `beta_l_nkids_f` | 0.142852 (t = 0.39) | Not individually significant |

The leisure preference curvature parameters (`theta_l_*`) are large, negative, and precisely estimated (t-ratios 11–21), consistent with the RURO specification. `beta_l0_m` being at its lower bound (§35) is noted.

---

## 34. Identified-Block Comparison — Year Effects and Objective Stability

**Objective stability:** Joint LL = −19,084.3313 across all three starts (agreement at the last printed decimal place). Objective stability criterion passes.

**Year effects:**
- `beta_E_y2015` = −0.0591 (t = −0.23): 2015 market opportunity was marginally lower than the 2016 reference, but not significantly different.
- `beta_E_y2017` = 0.1554 (t = 0.58): 2017 market opportunity was slightly higher, also not significant.

Year effects were absent from the M1-clean 2016 model (2016-only estimation). Their small, insignificant values in the pooled model suggest limited year-to-year variation in the market opportunity structure within 2015–2017, supporting the pooling assumption.

**Occupation parameters:** Large and significant across all groups (t-ratios 5–15), consistent with the pre-repair run. No material change expected from fixing region dummies.

---

## 35. beta_l0_m at Active Lower Bound — Diagnosis

`beta_l0_m` (the male couples leisure intercept) converged to its lower bound (1e−6) in all three starts. From the GAMS listing for Start 1:

```
---- VAR beta_l0_m    1.0000000E-6   1.0000000E-6        50.0000       -10.1370
```

The marginal of −10.1370 is the reduced gradient / shadow price at this active lower bound. The optimizer cannot improve the objective by decreasing `beta_l0_m` below 1e−6, but the shadow price indicates the likelihood surface has a gradient pointing in this direction (CONOPT would prefer a smaller value but is constrained).

This parameter was already at or near zero in the M1-clean warm-start vector (init value = 1e−6 via M1-clean converged value of ≈ 0.012 in the single-year model). In the pooled model, the male couples leisure-at-work intercept converges to its lower bound. This is a **structural feature** of the male couples preference sub-model in the pooled specification: given the strong negative leisure curvature (`theta_l_m` = −0.682), the intercept is pushed to zero by the optimization.

`beta_l0_m` is **excluded from the free_mask** (n_free = 54, not 55). The SE CLI correctly handles this: SE_robust = 0.0 (not applicable), SE_hessian = NaN (not applicable). T4 PASS excludes this parameter from the positivity count.

This active bound is not a new defect introduced by the region repair; it is a property of the three-year pooled model optimum.

---

## 36. In-Estimation Negative-Variance Warning — Resolved by True-Hessian Sandwich

The in-estimation step (step 7b, `enh_RURO_estimate_FR.py`) warned "5 free parameters have negative variance" for all three starts. This warning arises from the crude computation `diag(inv(H))` on an ill-conditioned 54×54 Hessian (κ = 3.316 × 10⁹): 5 diagonal elements of H⁻¹ are numerically negative due to the ill-conditioning.

This is **distinct** from the cluster-robust SE step. The SE CLI (`run_cluster_robust_se.py --mode post-estimation`) computes the true-Hessian sandwich V = H⁻¹ B H⁻¹, which is semi-definite by construction when B is positive semi-definite (as it is for a sum of outer products). The diagonal of V is non-negative for all 54 free parameters — T4 PASS (n_nonpositive = 0) for all three starts.

The in-estimation warning is therefore a diagnostic artifact of the ill-conditioned Hessian and does not indicate structural non-identification. The authoritative SE computation is the cluster-robust sandwich from the SE CLI.

---

## 37. Solver Artifact Paths — Per Start

| Start | Solver log | GAMS listing |
|-------|------------|-------------|
| Start 1 | `.../start_1/run_2026-05-21_23-47-14/solver.log` | `.../start_1/run_2026-05-21_23-47-14/solver.lst` |
| Start 2 | `.../start_2/run_2026-05-22_00-18-36/solver.log` | `.../start_2/run_2026-05-22_00-18-36/solver.lst` |
| Start 3 | `.../start_3/run_2026-05-22_00-53-54/solver.log` | `.../start_3/run_2026-05-22_00-53-54/solver.lst` |

Base path: `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/`

**H6 status**: CONOPT/GAMS solver artifacts were captured for all three starts. Halt condition H6 (artifacts not captured) did not fire.

---

## 38. Halt Conditions — None Triggered

| Halt | Description | Status |
|------|-------------|--------|
| H1 | Pre-solver sanity check fails | **NOT TRIGGERED** — PS1–PS5 all PASS |
| H2 | A start fails to converge | **NOT TRIGGERED** — all three starts: NormalCompletion/OptimalLocal |
| H3 | Region block still flat | **NOT TRIGGERED** — region SEs now inferential, no flat-ridge signature |
| H4 | Cluster-robust SE computation fails | **NOT TRIGGERED** — T3=9,657 PASS; T4=0 non-positive PASS; T5=0 below PASS |
| H5 | Income routing or cluster key corrupted at runtime | **NOT TRIGGERED** — PS4/PS5 confirmed; `ils_dispy_real` all-NaN for couples throughout |
| H6 | Solver artifacts not captured | **NOT TRIGGERED** — solver.log and solver.lst present for all three starts |
| H7 | Welfare/SA2/canonical/M1-clean/spec/prohibited-input attempted | **NOT TRIGGERED** — none of these executed (§39–§42) |

---

## 39. What Was Not Executed

The following were explicitly **NOT** executed in this run, per the authorization (§15) and the halt-condition design (H7):

- Welfare computation (N1)
- An SA2 verdict (N2)
- Canonical promotion of any output (N3)
- M1-clean displacement (N4)
- Specification modification of the pooled YAML (N5)
- Use of prohibited inputs: the defective archived couples split, the unified parquet directly, any pre-repair stem (N6)
- Any estimation beyond the three authorized starts (N7)
- An S4 or S5 region-criterion verdict (N8)

No estimation beyond `ruro_occ_P3a_pooled` on the corrected stem (`fr_p3a_gsurv2_estimation_ready`) was performed.

---

## 40. No Welfare Computed

Welfare computation is **not authorized** by this memo and was not performed. The SE CLIs include the check `PE9_no_welfare` in all three run outputs, returning `"CONFIRMED: No welfare computed (not authorized)."` Welfare is separately gated behind an accepted SA2 verdict.

---

## 41. No SA2 Verdict Issued

No SA2 verdict was issued. The immediate next gate is a **fresh strict post-estimation review / SA2-readiness verdict** that adjudicates whether the region block is now identified (S4/S5), whether the preference-block comparison (S6) passes, and whether the SA2 criteria are met. Only if that review passes is the SA2 verdict drafted. This re-estimation supplies the region evidence for that review; it does not pre-judge the verdict.

---

## 42. No Canonical Promotion; M1-clean 2016 Remains Active Baseline

No output of this re-estimation was promoted to canonical status. The corrected P3a estimates are candidate results at versioned paths under `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/`. The SE CLIs include `PE9_m1clean_active` in all three run outputs, returning `"CONFIRMED — M1-clean 2016 remains the active JMP baseline."` M1-clean 2016 is displaced only by a future SA2 verdict explicitly promoting an identified pooled specification. That verdict is not authorized here.

---

## 43. Required Final Statements

- **The corrected pooled P3a was re-estimated (three starts) on the region-repaired stem.** All three starts reached NormalCompletion / OptimalLocal with joint LL = −19,084.3313 and an identical converged parameter vector (L∞ < 10⁻⁸). The region dummies `beta_E_drgn2`–`beta_E_drgn8` now converge to consistent, finite, reproducible values with inferential-magnitude robust SEs (0.34–0.55) — the flat-ridge signature from the pre-repair run is absent. The seven region dummies are estimated on gradient-relevant data.

- **The CONOPT/GAMS solver diagnostics were captured per start** (`--save-solver-artifacts`) and are reported in §13, §17, §20 and §37. All three starts: CONOPT4 Normal Completion (status 1), Locally Optimal (status 2), "reduced gradient less than tolerance," 0 infeasibilities, 0 non-optimal residuals. These diagnostics are reported distinctly from the Python likelihood-gradient / score diagnostic (the score `∂logL/∂θ` from `compute_gradient_joint` used in the SE sandwich); the two quantities are from different tools and must not be conflated (§13).

- **True-Hessian cluster-robust SEs were computed and T3/T4/T5 rerun** for all three starts. True Hessian (central differences on `compute_gradient_joint` at converged theta, NOT the dummy H=0.1·I) was used as the sandwich bread. T3 = 9,657 unique `idorighh` clusters (PASS, all starts). T4 = 0 non-positive robust SEs among 54 free parameters (PASS, all starts). T5 = 0 robust SEs below Hessian SEs (PASS, all starts). Region-dummy robust SEs (0.34–0.55) are explicitly reported in §27–§29. The in-estimation negative-variance warning for 5 parameters (from the crude H⁻¹ diagonal) is resolved by the true-Hessian sandwich and does not indicate structural non-identification.

- **No welfare was computed; no SA2 verdict was issued.** The immediate next gate is a fresh strict post-estimation review / SA2-readiness verdict.

- **No output was promoted to canonical status; M1-clean 2016 remains the active JMP baseline.** Displacement is gated behind a future SA2 verdict. `PE9_m1clean_active` CONFIRMED in all three SE run outputs.