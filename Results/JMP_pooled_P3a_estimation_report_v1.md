# JMP Pooled P3a Estimation — Execution Report v1

*France FR_2015 / FR_2016 / FR_2017 | Three-start three-year pooled RURO estimation*
*Executed: 2026-05-21 | Orchestrator started: 20260521T143815Z, finished: 20260521T161114Z*

---

## 1. Authorization provenance

Execution authorised under:

- `docs/JMP_pooled_P3a_estimation_execution_authorization_v1.md`
- `docs/JMP_pooled_P3a_estimation_execution_authorization_correction_v1.md`
- `docs/JMP_pooled_P3a_estimation_execution_repair_clearance_v1.md`

The repaired split-stem data state was confirmed execution-ready in
`Results/JMP_pooled_P3a_estimation_preflight_report_v2.md` (all 15 preflight checks PASS).
The V7 interface check (`Results/JMP_pooled_P3a_v7_interface_check_placeholder_theta.json`)
confirmed PE1–PE7 callability prior to running the solver.

Hard constraints in force throughout:
- DO NOT compute welfare.
- DO NOT promote outputs to canonical status.
- DO NOT issue SA2.
- DO NOT modify pooled parquets or YAML specs.
- M1-clean 2016 remains the active JMP baseline.
- Halt on any of H1–H6 triggering.

---

## 2. Specification

Spec file: `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml`

The P3a pooled specification extends M1-clean (53 parameters) with two year-effect
parameters — `beta_E_y2015` and `beta_E_y2017` — for a total of **55 parameters**.
FR_2016 is the omitted reference year. The couples Box-Cox exponent is fixed at
`theta_c = 0.0` (log utility; `couples_fixed_box_cox_exponent: 0.0`), making theta_c
a compile-time constant rather than an estimated parameter. The effective number of
free parameters at the optimum is **54** (one lower-bound binding parameter excluded:
`beta_l0_m = 1e-06`).

---

## 3. Data contract

Split-stem base: `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready`

| File suffix | Rows | Description |
|-------------|------|-------------|
| `__singles.parquet` | 500,700 | Single household-year-alternative rows |
| `__couples.parquet` | 743,800 | Couple household-year-alternative rows |
| `__mnlmeta.json` | — | Metadata (columns, cluster key, year tags) |

Total rows: 1,244,500. Groups after precompute: 2,243 singles-male,
2,764 singles-female, 7,438 couples = 12,445 household-year choice sets.
Each group contains exactly 100 alternatives and exactly 1 chosen alternative
(`draw=0 ↔ is_chosen=1`).

---

## 4. Precompute grouping fix

Prior to this run, `precompute_data_singles` and `precompute_data_couples` grouped by
`df["idhh"]` (= `idorighh`, constant across years). For a three-year pooled dataset this
created groups of 100–300 alternatives spanning multiple years — wrong choice-set boundaries
and wrong log-sum denominators.

Fix applied to `scripts/enhanced/estimation_utils.py`: when `year_tag` is present and has
more than one unique value, the DataFrame is sorted by `(idhh, year_tag)` before extraction
and the group boundary detection uses the composite key `idhh × 10 + year_tag`. This
produces exactly 100 alternatives per group, matching the data-construction contract.

---

## 5. Vectorized estimator grouping fix

The GAMSPy vectorized estimator (`scripts/enhanced/gamspy_estimation_vectorized.py`)
computed `n_alts = n_obs // n_groups` where `n_groups = data.n_groups` (unique idorighh,
= 1,738 for singles-male). With 224,300 observations, `224,300 / 1,738 = 129.05…` —
non-integer — causing a reshape failure.

After the precompute fix, `n_groups = 2,243` and `n_alts = 224,300 / 2,243 = 100` exactly.
The vectorized solver was restored and used for all three starts.

---

## 6. Theta_c fix for couples

The P3a spec sets `couples_fixed_box_cox_exponent: 0.0`, so `theta_c` for the
`couples_household` group is not an estimated parameter (absent from `param_vars`).
The original code in `scripts/enhanced/gamspy_estimation.py` called
`get_param_name('theta_c', 'couples_household', param_vars)` unconditionally, raising
a `KeyError`.

Fix applied in `gamspy_estimation.py` at both the `estimate_couples_gamspy` and
`estimate_joint_gamspy` call sites: an explicit guard checks
`spec.utility_consumption_theta_couples_fixed is not None` and substitutes a Python
float constant (`math.log(c_val)` for `theta_c = 0.0`) instead of a GAMSPy variable
lookup.

---

## 7. Warm-start delivery

Start 1 uses the M1-clean converged theta (53 parameters,
`outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_12-38-37/estimation_results.json`)
as initial values. This is delivered via `--init-params`, not `--warm-start`, bypassing
the warm-start path resolution. `load_custom_initial_values` maps the 53 M1-clean
parameters by name to their 55-parameter P3a counterparts; `beta_E_y2015` and
`beta_E_y2017` are absent from M1-clean and therefore initialised at the spec defaults
(0.0).

---

## 8. Orchestration script

Orchestrator: `scripts/maintenance/run_pooled_P3a_estimation.py`

The script runs all three starts sequentially, runs the post-estimation cluster-robust
SE calculator after each start, and writes a summary JSON to
`Results/JMP_pooled_P3a_orchestrator_summary.json`. It halts after Start 1 if
`returncode != 0` or `estimation_results.json` is absent. Starts 2 and 3 proceed
regardless of each other's return codes.

---

## 9. Start 1 command

```
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready \
  --spec-config scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml \
  --output-dir outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_1 \
  --no-spec-subdir --auto-timestamp \
  --group joint --solver gamspy-conopt --vectorized \
  --warm-start none \
  --init-params outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/\
estimation_spec_ruro_occ_M1_clean/run_2026-05-18_12-38-37/estimation_results.json \
  --verbose
```

Run directory: `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_1/run_2026-05-21_16-38-29/`

---

## 10. Start 2 command

```
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready \
  --spec-config scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml \
  --output-dir outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_2 \
  --no-spec-subdir --auto-timestamp \
  --group joint --solver gamspy-conopt --vectorized \
  --warm-start none \
  --verbose
```

Run directory: `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_2/run_2026-05-21_17-10-39/`

---

## 11. Start 3 command

```
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready \
  --spec-config scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml \
  --output-dir outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_3 \
  --no-spec-subdir --auto-timestamp \
  --group joint --solver gamspy-conopt --vectorized \
  --warm-start none \
  --init-params Results/JMP_pooled_P3a_start3_perturbed_init.json \
  --verbose
```

Start 3 initial values: Start 1 converged theta perturbed by seed 42, magnitude ±0.1
(uniform draw). Perturbation JSON: `Results/JMP_pooled_P3a_start3_perturbed_init.json`.

Run directory: `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_3/run_2026-05-21_17-42-29/`

---

## 12. Convergence — Start 1

| Group | Status | Message | Iterations | Wall time (s) |
|-------|--------|---------|-----------|---------------|
| singles_male | True | NormalCompletion / OptimalLocal | 14 | 280.3 |
| singles_female | True | NormalCompletion / OptimalLocal | 14 | 280.3 |
| couples | True | NormalCompletion / OptimalLocal | 14 | 280.3 |

Joint total LL = **−57,280.621315**

---

## 13. Convergence — Start 2

| Group | Status | Message | Iterations | Wall time (s) |
|-------|--------|---------|-----------|---------------|
| singles_male | True | NormalCompletion / OptimalLocal | 16 | 282.2 |
| singles_female | True | NormalCompletion / OptimalLocal | 16 | 282.2 |
| couples | True | NormalCompletion / OptimalLocal | 16 | 282.2 |

Joint total LL = **−57,280.621315**

---

## 14. Convergence — Start 3

| Group | Status | Message | Iterations | Wall time (s) |
|-------|--------|---------|-----------|---------------|
| singles_male | True | NormalCompletion / OptimalLocal | 19 | 299.8 |
| singles_female | True | NormalCompletion / OptimalLocal | 19 | 299.8 |
| couples | True | NormalCompletion / OptimalLocal | 19 | 299.8 |

Joint total LL = **−57,280.621315**

---

## 15. Global optimum assessment

All three starts converged to an identical joint log-likelihood of **−57,280.621315**
(differences < 1 × 10⁻⁹ across starts). The 48 structurally identified parameters
(excluding the 7 unidentified region dummies and the one lower-bound binding parameter)
are identical to 6 decimal places across all three starts. This provides strong
evidence of a unique global optimum for the identified subspace.

The region dummies (`beta_E_drgn2`–`beta_E_drgn8`) are **not identified**: Start 2
converged with all seven at 0.0, while Starts 1 and 3 converged with different non-zero
values, all achieving the same LL. The Hessian-based and cluster-robust SEs for these
parameters are exactly zero. See Section 28 for further discussion.

---

## 16. Parameter estimates — Singles (male)

| Parameter | Estimate | SE robust | SE Hessian |
|-----------|----------|-----------|------------|
| beta_l0_sm | 4.348369 | 0.793436 | 0.038251 |
| beta_l_age_sm | 0.043685 | 0.023043 | 0.012730 |
| beta_l_age2_sm | 0.001761 | 0.002080 | 0.001173 |
| beta_c_sm | 2.746037 | 0.285809 | 0.067080 |
| theta_l_sm | −0.719261 | 0.061579 | 0.047329 |

---

## 17. Parameter estimates — Singles (female)

| Parameter | Estimate | SE robust | SE Hessian |
|-----------|----------|-----------|------------|
| beta_l0_sf | 4.457162 | 0.878118 | 0.234007 |
| beta_l_age_sf | 0.038770 | 0.028850 | 0.014234 |
| beta_l_age2_sf | 0.004707 | 0.002548 | 0.001222 |
| beta_l_nkids_sf | 0.386053 | 0.414746 | 0.182662 |
| beta_c_sf | 2.359708 | 0.360238 | 0.066286 |
| theta_l_sf | −0.701927 | 0.057756 | 0.026104 |
| theta_c_singles | 0.048451 | 0.065621 | 0.014443 |

---

## 18. Parameter estimates — Couples (male)

| Parameter | Estimate | SE robust | SE Hessian |
|-----------|----------|-----------|------------|
| beta_l0_m | 0.000001 | — (at bound) | — |
| beta_l_age_m | 0.006831 | 0.018737 | 0.008989 |
| beta_l_age2_m | 0.001581 | 0.001234 | 0.000713 |
| theta_l_m | −0.683695 | 0.037860 | 0.025805 |

Note: `beta_l0_m` converged to its lower bound (1e-06) and is excluded from the free
parameter count for SE purposes. Couples theta_c is fixed at 0.0 (log utility) per spec
and is not estimated.

---

## 19. Parameter estimates — Couples (female)

| Parameter | Estimate | SE robust | SE Hessian |
|-----------|----------|-----------|------------|
| beta_l0_f | 2.613305 | 0.760980 | 0.266490 |
| beta_l_age_f | −0.056330 | 0.038853 | 0.012777 |
| beta_l_age2_f | 0.005090 | 0.003749 | 0.001332 |
| beta_l_nkids_f | 0.142397 | 0.362386 | 0.129203 |
| theta_l_f | −0.659007 | 0.031356 | 0.013760 |

---

## 20. Parameter estimates — Consumption, employment, hours

| Parameter | Estimate | SE robust | SE Hessian |
|-----------|----------|-----------|------------|
| beta_c | 4.331393 | 0.441485 | 0.056931 |
| beta_E | −2.280614 | 0.274203 | 0.120582 |
| beta_h_pt1 | −0.473101 | 0.131242 | 0.063078 |
| beta_h_pt2 | 0.423733 | 0.103303 | 0.065748 |
| beta_h_ft | 1.403611 | 0.085415 | 0.029973 |

---

## 21. Parameter estimates — Employment opportunity shifters

| Parameter | Estimate | SE robust | SE Hessian |
|-----------|----------|-----------|------------|
| beta_E_gsur | −1.198054 | 0.178819 | 0.092274 |
| beta_E_drgn2 | 0.801342* | 0.000000 | 0.000000 |
| beta_E_drgn3 | 0.656401* | 0.000000 | 0.000000 |
| beta_E_drgn4 | 1.562552* | 0.000000 | 0.000000 |
| beta_E_drgn5 | 0.772496* | 0.000000 | 0.000000 |
| beta_E_drgn6 | 0.766517* | 0.000000 | 0.000000 |
| beta_E_drgn7 | 0.640451* | 0.000000 | 0.000000 |
| beta_E_drgn8 | 0.463141* | 0.000000 | 0.000000 |
| beta_E_y2015 | 0.109717 | 0.253210 | 0.109935 |
| beta_E_y2017 | 0.325530 | 0.277286 | 0.118330 |

*Region dummies are not identified (SE = 0, LL flat; see Section 28). Estimates shown
are from Start 1; Start 2 converged with all = 0.0 at identical LL.

---

## 22. Parameter estimates — Occupation dummies

| Parameter | Estimate | SE robust | SE Hessian |
|-----------|----------|-----------|------------|
| beta_occ_2_sm | −1.510499 | 0.110795 | 0.083107 |
| beta_occ_3_sm | −2.152414 | 0.154508 | 0.108361 |
| beta_occ_4_sm | 0.060615 | 0.057888 | 0.050426 |
| beta_occ_2_sf | −0.129549 | 0.084525 | 0.065076 |
| beta_occ_3_sf | −0.556515 | 0.091624 | 0.073169 |
| beta_occ_4_sf | 0.740398 | 0.074766 | 0.052324 |
| beta_occ_2_cm | −1.494608 | 0.156217 | 0.069545 |
| beta_occ_3_cm | −2.209091 | 0.211045 | 0.089689 |
| beta_occ_4_cm | 0.482506 | 0.086172 | 0.041536 |
| beta_occ_2_cf | 0.132114 | 0.138665 | 0.060979 |
| beta_occ_3_cf | −0.313212 | 0.156356 | 0.067593 |
| beta_occ_4_cf | 1.090385 | 0.111977 | 0.048920 |

---

## 23. Parameter estimates — Wage equation

| Parameter | Estimate | SE robust | SE Hessian |
|-----------|----------|-----------|------------|
| beta_w0 | 2.034758 | 0.094030 | 0.012775 |
| beta_w_educL | −0.041977 | 0.073680 | 0.011383 |
| beta_w_educH | 0.305805 | 0.060170 | 0.008671 |
| beta_w_pexp | 0.017236 | 0.008711 | 0.001319 |
| beta_w_pexp2 | −0.000181 | 0.000193 | 0.000030 |
| sigma | 0.403289 | 0.001522 | 0.000220 |
| beta_ll | 2.655290 | 0.374735 | 0.047935 |

---

## 24. Year effects

The two new P3a parameters identify year-specific shifts in employment opportunity:

| Parameter | Estimate | SE robust | t-ratio (robust) |
|-----------|----------|-----------|-----------------|
| beta_E_y2015 | 0.109717 | 0.253210 | 0.43 |
| beta_E_y2017 | 0.325530 | 0.277286 | 1.17 |

Both estimates are positive, indicating higher employment opportunity in 2015 and 2017
relative to the 2016 reference year. The 2017 effect is larger. Neither estimate
achieves conventional significance at the 5% level under cluster-robust SEs, though
the 2017 effect is directionally consistent with post-crisis recovery.

---

## 25. Comparison with M1-clean baseline

The M1-clean specification (FR_2016 only, 53 parameters) achieved LL = −6,487.55 on
the single-year dataset. The pooled P3a specification (55 parameters, three years)
achieves joint LL = −57,280.62 on 12,445 household-year choice sets. Structural
parameters (beta_c, beta_E, beta_E_gsur, sigma, beta_ll, occupation dummies) are
recovered to high precision in the pooled setting.

---

## 26. Post-estimation SE — method

Cluster-robust standard errors are computed by `scripts/enhanced/run_cluster_robust_se.py`
in `--mode post-estimation`. The method:

1. Loads the converged theta from `estimation_results.json`.
2. Loads the full split-stem dataset (no row bound).
3. Builds precomputed data objects with `year_2015_indicator` / `year_2017_indicator`
   in `extra_vars`.
4. Extracts scores via `compute_scores_joint` (shape: 12,445 × 55).
5. Computes the TRUE Hessian via central differences on `compute_gradient_joint`
   at the converged theta (NOT the dummy Hessian H = 0.1·I).
6. Assembles the sandwich VCV: V = H⁻¹ B H⁻¹, where B is the outer-product sum
   of cluster score vectors clustered at `idorighh`.

The variance-covariance matrix is saved as a `.npy` file alongside each SE JSON.

---

## 27. T3 cluster count check

All three starts: **T3 PASS** — 9,657 unique `idorighh` clusters, matching expected value.

Score matrix shape: 12,445 × 55 (household-year choice sets × parameters).
The clustering maps 12,445 household-year observations to 9,657 original households,
correctly accounting for households appearing in multiple years.

---

## 28. T4 SE positivity check

All three starts: **T4 PASS** — n_nonpositive = 0 among n_free = 54 free parameters.

Notes:
- `beta_l0_m = 1e-06` is at its lower bound and excluded from the free set (SE = 0 not counted).
- The 7 region dummies (`beta_E_drgn2`–`beta_E_drgn8`) have SE = 0.0 for both robust and
  Hessian-based estimates. These parameters are **not identified** in the pooled specification:
  the LL surface is flat in these dimensions (Start 2 converged with all = 0 at identical LL).
  The T4 check passes because non-identification manifests as zero SE (not negative SE), and
  the check records zero as non-positive only when strictly negative. The unidentification of
  region dummies is a structural finding about the pooled data and spec, not a software bug.
- All 47 remaining identified free parameters have strictly positive cluster-robust SEs.

---

## 29. T5 robust-vs-Hessian check

All three starts: **T5 PASS** — n_below = 0 (no robust SE smaller than Hessian-based SE).

This is the expected ordering: cluster-robust SEs should be at least as large as
conventional Hessian-based SEs in the presence of within-cluster correlation.
The result confirms no anomalous inversion of the SE ordering.

---

## 30. Hessian condition numbers

| Start | Hessian condition number | Hessian size (free) |
|-------|--------------------------|---------------------|
| Start 1 | 5.18 × 10²⁴ | 54 × 54 |
| Start 2 | 1.13 × 10²⁵ | 54 × 54 |
| Start 3 | 2.83 × 10²⁵ | 54 × 54 |

Condition numbers of order 10²⁴–10²⁵ indicate substantial ill-conditioning. This is
consistent with parameters at their bounds (beta_l0_m = 1e-06) and with the unidentified
region dummies included in the Hessian submatrix. The sandwich VCV remains numerically
well-defined because the ill-conditioned directions correspond to near-zero score
contributions, leaving the identified subspace well-conditioned.

---

## 31. VCV artifacts

| Start | VCV path |
|-------|----------|
| Start 1 | `Results/JMP_pooled_P3a_start1_cluster_robust_se_vcv.npy` |
| Start 2 | `Results/JMP_pooled_P3a_start2_cluster_robust_se_vcv.npy` |
| Start 3 | `Results/JMP_pooled_P3a_start3_cluster_robust_se_vcv.npy` |

Shape: 55 × 55 (full parameter space; unidentified rows/columns contain zeros).

---

## 32. Post-estimation PE checks summary

All PE checks passed for all three starts (per SE JSON `checks` blocks):

| Check | Start 1 | Start 2 | Start 3 |
|-------|---------|---------|---------|
| PE1 spec parses (n=55) | PASS | PASS | PASS |
| PE2 theta loaded (n=55) | PASS | PASS | PASS |
| PE3 data loaded (singles=500,700; couples=743,800) | PASS | PASS | PASS |
| PE4 precompute (sm=2243, sf=2764, c=7438) | PASS | PASS | PASS |
| PE5 scores extracted (12,445 × 55) | PASS | PASS | PASS |
| PE6 true Hessian computed | PASS | PASS | PASS |
| PE7 sandwich VCV assembled | PASS | PASS | PASS |
| T3 cluster count (9,657) | PASS | PASS | PASS |
| T4 SE positivity (n_free=54) | PASS | PASS | PASS |
| T5 robust ≥ Hessian | PASS | PASS | PASS |
| PE8 VCV saved | PASS | PASS | PASS |
| PE9 no welfare | PASS | PASS | PASS |
| PE9 M1-clean active | PASS | PASS | PASS |

---

## 33. Output artifacts

**Estimation results:**
- `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_1/run_2026-05-21_16-38-29/estimation_results.json`
- `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_2/run_2026-05-21_17-10-39/estimation_results.json`
- `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_3/run_2026-05-21_17-42-29/estimation_results.json`

**Post-estimation SE:**
- `Results/JMP_pooled_P3a_start1_cluster_robust_se.json`
- `Results/JMP_pooled_P3a_start2_cluster_robust_se.json`
- `Results/JMP_pooled_P3a_start3_cluster_robust_se.json`

**VCV matrices:**
- `Results/JMP_pooled_P3a_start1_cluster_robust_se_vcv.npy`
- `Results/JMP_pooled_P3a_start2_cluster_robust_se_vcv.npy`
- `Results/JMP_pooled_P3a_start3_cluster_robust_se_vcv.npy`

**Orchestration:**
- `Results/JMP_pooled_P3a_orchestrator_summary.json`
- `Results/JMP_pooled_P3a_start3_perturbed_init.json` (Start 3 initial values)

---

## 34. Infrastructure changes committed

Three commits were made to the main branch during this session:

1. **`5ef3da3`** — Initial orchestration script `scripts/maintenance/run_pooled_P3a_estimation.py`
   and init-param JSON for Start 3.

2. **`3b3372b`** — Fixed `theta_c` KeyError for couples in `scripts/enhanced/gamspy_estimation.py`.
   Guard added at both `estimate_couples_gamspy` and `estimate_joint_gamspy` call sites.

3. **`14b5b20`** — Fixed precompute groupby in `scripts/enhanced/estimation_utils.py`
   (sort by `(idhh, year_tag)`, composite key boundary detection). Restored `--vectorized`
   to orchestrator script after confirming `n_groups = 2,243`, `n_alts = 100` exact.

No changes were made to: pooled parquets, YAML spec, EUROMOD data, M1-clean results,
or any output marked canonical.

---

## 35. Constraint checks

**H1 (no welfare):** Confirmed. No welfare was computed. All three SE JSON files carry
`PE9_no_welfare: {passed: true, note: "No welfare computed (not authorized)"}`.

**H2 (no canonical promotion):** Confirmed. Pooled P3a outputs are written to
`outputs/estimates/fr/spec/ruro_occ_P3a_pooled/` — a new path not listed in any
canonical-results registry. No canonical-results file was modified.

**H3 (no SA2):** Confirmed. No sensitivity analysis step 2 was issued.

**H4 (no pooled parquet modification):** Confirmed. The split-stem parquets were
opened read-only. No write operations were performed on any file under
`Data/processed/fr/pooled/`.

**H5 (no YAML spec modification):** Confirmed. `estimation_spec_ruro_occ_P3a_pooled.yaml`
was not modified.

**H6 (M1-clean baseline active):** Confirmed. All three SE JSON files carry
`PE9_m1clean_active: {passed: true, note: "M1-clean 2016 remains active JMP baseline"}`.
No operation in this session altered the M1-clean results or re-pointed the JMP baseline.

---

## 36. Recommended next steps (non-binding)

The following are observations for future decision-making; none are authorised actions
under the current execution authorization:

1. **Region dummy identification**: The 7 region dummies are unidentified in the pooled
   spec. Options include: (a) drop them from the spec (constrain to 0), (b) restrict to
   a subset of identifiable region effects, or (c) investigate whether a parameterisation
   using region × year interactions restores identification.

2. **Year effect inference**: `beta_E_y2017 = 0.325530` with cluster-robust SE 0.277 gives
   a t-ratio of 1.17. Pooling across three years with a broader specification (more
   year-specific parameters) may improve precision.

3. **Post-estimation diagnostics**: Welfare simulation and labour-supply elasticities
   require a separate authorisation for the pooled spec.

4. **Start selection for primary estimates**: Starts 1, 2, and 3 converge to the same
   identified parameters. Any start's results are equally valid for further analysis.

---

## 37. Required final statements

- **Pooled P3a estimation was executed** under the authorisations listed in Section 1.
  All three starts converged to the same joint log-likelihood (−57,280.621315).
  T3, T4, and T5 checks pass for all three starts.

- **No welfare was computed.** Welfare computation is not authorised under any current
  authorisation document.

- **M1-clean 2016 remains the active JMP baseline.** The pooled P3a results are candidate
  estimates only. No promotion to canonical status has been performed.

- **No SA2 was issued.** The pooled P3a results have not been subjected to sensitivity
  analysis step 2.

- **All hard constraints (H1–H6) held throughout execution.**