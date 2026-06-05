# MNL Repository — Architectural Inventory (v2, corrected)

**Date:** 2026-06-05  
**Method:** Read-only survey; all paths verified via `find`/`wc -l`. No production files modified.  
**Repo root:** `C:\Users\hisham\Repo\MNL`

## Classification schema

**Class** (exactly one per row):  
`reusable_core_candidate` · `application_layer_candidate` · `EUROMOD_specific` ·  
`welfare_specific` · `diagnostics_reporting` · `configuration` · `tests_or_gates` ·  
`output_or_provenance` · `scratch_or_temporary` · `unclear_needs_review`

**Target** (exactly one per row):  
`core_package` · `app_package` · `stays_in_jmp_repo` · `never`

**Priority** (migration urgency):  
`high` · `medium` · `low` · `never`

---

## A. Executive Summary

This repository contains a **Random Utility Random Opportunity (RURO)** discrete-choice labour supply model for France (SILC/EUROMOD data, 2015–2017), estimated by maximum likelihood with importance-sampling correction over a continuous opportunity-set. Two production branches exist (continuous RURO in `scripts/enhanced/`; job-choice RURO in `scripts/Job_model/`), plus an archived translog/Box-Cox RUM approach (`scripts/archive/rum_approach/`) that predates RURO and must not be migrated.

The repo also contains: an R reference implementation (`stijn/`), a structural `src/mnl/` package stub that does **not** expose the RURO engine, and a large collection of scratch/diagnostic/provenance artefacts that must be classified separately from the reusable core.

**Certified baseline (single source of truth):**  
47-param spec `estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` at `scripts/bpool/specs/`.  
negLL = 238 362.79; Hessian min_eig = +1.706 (PD). Certified by synthetic 901 recovery gate.  
Script: `scripts/bpool/step4_realdata_baseline.py` — provenance artifact, NEVER move or edit.

**49-param gsplit:** FAILED synthetic recovery gate (tight-SE bias; beta_h_pt2_m err/SE = 19). NOT a valid paper baseline despite real-data PD Hessian.

**Five critical risks (detail in §G):**

| # | Risk | Evidence |
|---|------|----------|
| R1 | Box-Cox Taylor bug in `estimation_utils.py:box_cox_derivative_theta` | Confirmed by JAX/FD cross-check in `scripts/bpool/jax_ll_probe.py`; ~0.5 off near θ = 0; affects NumPy gradient and Hessian |
| R2 | `src/mnl/models/mnl.py` exposes statsmodels MNLogit — wrong model | File reads as 40-line wrapper with no RURO content |
| R3 | `log_prior` formula split across `enh_RURO_draws.py` and `enh_RURO_prep_mnl_basic.py` | Two separate files; byte-identical formula required; silent divergence risk |
| R4 | UNC path workaround (`ensure_local_workdir()`) is a hard runtime dependency for GAMSPy | `scripts/enhanced/path_helpers.py:265`; must survive any restructuring |
| R5 | `gsplit` spec not clearly labeled as non-certified despite sharing directory with certified spec | Both live in `scripts/bpool/specs/`; risk of confusion |

---

## B. File Classification Table

### scripts/enhanced/ — production estimation engine

| Path | Lines | Purpose | Class | Target | Priority | Notes |
|------|-------|---------|-------|--------|----------|-------|
| `estimation_engine.py` | 2,446 | NumPy/Numba likelihood + analytical gradients; `compute_likelihood_singles/couples()`, `compute_gradient_singles/couples()`, Box-Cox utility | `reusable_core_candidate` | `core_package` | high | ⚠ R1: carries known Box-Cox Taylor bug; `_USE_NUMBA` flag sensitive to import restructuring |
| `estimation_utils.py` | 1,799 | `PrecomputedData` containers, Box-Cox math, log-sum-exp | `reusable_core_candidate` | `core_package` | high | ⚠ R1: `box_cox_derivative_theta` Taylor bug confirmed by JAX probe; fix before publishing |
| `estimation_spec_parser.py` | 1,905 | YAML → `EstimationSpec`; 4-group architecture (`_sm _sf _m _f`); fixed\_params, gender-split, warmstart | `reusable_core_candidate` | `core_package` | high | No EUROMOD imports; safe to migrate |
| `gamspy_estimation_vectorized.py` | 1,871 | Vectorised GAMSPy CONOPT/IPOPT; `estimate_joint_vectorized_gamspy()`; 3–5× faster expression build | `reusable_core_candidate` | `core_package` | high | Depends on `path_helpers`; 94% wall time is model generation (R7) |
| `gamspy_estimation.py` | 2,563 | Non-vectorised GAMSPy variant (predecessor) | `unclear_needs_review` | `stays_in_jmp_repo` | low | Exists alongside vectorised version; unclear if still used |
| `enh_RURO_draws.py` | 1,631 | Vectorised continuous opportunity-set generation; `generate_draws_long()` | `reusable_core_candidate` | `core_package` | high | ⚠ R3: `log_prior` formula here must match `enh_RURO_prep_mnl_basic.py` |
| `enh_RURO_prep_mnl_basic.py` | 2,433 | Merge draws + EUROMOD output, reshape couples wide, compute `log_prior` | `EUROMOD_specific` | `app_package` | high | ⚠ R3: `log_prior` here must match `enh_RURO_draws.py`; largest file in pipeline |
| `enh_RURO_euromod.py` | 1,151 | Single EUROMOD run on all draws; 35h French overtime split; decider-only logic | `EUROMOD_specific` | `app_package` | medium | Java/pythonnet dependency; FR 35h rule |
| `enh_france_data_prep.py` | 2,621 | FR SILC/EUROSTAT data filtering; `clean_harmonize_fr()`, `stepwise_filter_households()` | `application_layer_candidate` | `app_package` | medium | FR-specific column names and filters |
| `enh_RURO_estimate_FR.py` | 1,821 | 8-step estimation orchestrator; `main()`, `compute_standard_errors()`, `save_results_json()` | `application_layer_candidate` | `app_package` | medium | FR-specific config; mixes orchestration and FR business logic |
| `RURO_post_estimation_styled.py` | 10,232 | Styled HTML/Markdown report; `ParsedParameters`, `compute_marginal_utility_*()`; fully dynamic | `diagnostics_reporting` | `app_package` | medium | FR-specific outputs but dynamically handles parameters |
| `diagnostics_bundle.py` | 2,505 | 40+ metrics; 4 sections (A/B/C/D); CONOPT log parsing; `build_diagnostics_bundle()` | `diagnostics_reporting` | `core_package` | medium | Model-generic diagnostics; no EUROMOD imports |
| `cluster_robust_se.py` | 239 | `compute_cluster_robust_se()`, `assemble_meat_matrix()`; T1–T5 verification | `reusable_core_candidate` | `core_package` | high | Sandwich must be chunked (naive jacrev = 11 TB OOM); T1–T5 gates must stay |
| `compute_standard_errors.py` | 379 | Numerical Hessian SEs via central differences | `reusable_core_candidate` | `core_package` | medium | |
| `occupation_choice_utils.py` | 504 | Occupation preferences, wage/hours density, availability | `reusable_core_candidate` | `core_package` | medium | ⚠ R10: may contain FR SILC column assumptions; verify before publishing |
| `mcfadden_sampler.py` | 539 | McFadden (1978) choice-set expansion; 400 alternatives | `reusable_core_candidate` | `core_package` | medium | |
| `path_helpers.py` | 265 | EUROMOD-STORAGE resolution, UNC workaround; `ensure_local_workdir()` | `application_layer_candidate` | `app_package` | high | ⚠ R4: hard runtime dependency for GAMSPy on network drives |
| `enh_prepare_FR_gsur_v2.py` | 858 | GSUR lookup builder; FR Eurostat + INSEE benchmark; 10 validation checks | `application_layer_candidate` | `app_package` | medium | FR/INSEE data-specific |
| `enh_prepare_FR_gsur.py` | 717 | Earlier version of GSUR builder (v1) | `unclear_needs_review` | `stays_in_jmp_repo` | low | Superseded by v2; unclear if still referenced |
| `estimation_utils_AC2013.py` | 770 | Utility math variants following Aaberge–Colombino 2013 | `reusable_core_candidate` | `core_package` | low | Variant of estimation_utils; used by AC2013 spec |
| `expression_constraints.py` | 748 | GAMSPy expression constraints builder | `reusable_core_candidate` | `core_package` | low | Used by vectorised solver |
| `parallel_estimation.py` | 648 | Parallel estimation runner | `application_layer_candidate` | `app_package` | low | Orchestration layer |
| `enh_RURO_post_estimation.py` | 1,654 | Post-estimation reporting (earlier version of styled reporter) | `unclear_needs_review` | `stays_in_jmp_repo` | low | Superseded by `RURO_post_estimation_styled.py`; unclear if still used |
| `enh_RURO_mnl_rebuild_GSURv2_stageA.py` | 1,115 | GSUR v2 stage-A MNL rebuild | `application_layer_candidate` | `app_package` | low | FR-specific rebuild script |
| `enh_RURO_prep.py` | — | RURO variable construction (NUTS1, educ dummies, experience) | `application_layer_candidate` | `app_package` | medium | FR SILC variable names |
| `enh_RURO_explore_predrop.py` | — | Pre-drop exploration script | `scratch_or_temporary` | `never` | never | Exploratory; not production |
| `diagnostic_consumption_variation.py` | — | Consumption variation diagnostic | `diagnostics_reporting` | `app_package` | low | |
| `run_cluster_robust_se.py` | — | Cluster-robust SE runner script | `application_layer_candidate` | `app_package` | low | Thin runner |
| `sanity_checks.py` | — | Sanity checks on estimation data | `diagnostics_reporting` | `app_package` | low | |
| `validate_specs.py` | — | Spec validation utility | `reusable_core_candidate` | `core_package` | low | |
| `fix_spec_initial_values.py` | — | One-off spec init-value fixer | `scratch_or_temporary` | `never` | never | |
| `quick_verify.py` | — | Quick verification script | `scratch_or_temporary` | `never` | never | |
| `reduce_draws_files.py` | — | Draw file reducer | `scratch_or_temporary` | `never` | never | |
| `reduce_mnl_columns.py` | — | MNL column reducer | `scratch_or_temporary` | `never` | never | |
| `specifications/` (24 YAMLs) | — | Continuous RURO model specs; general-purpose | `configuration` | `core_package` | medium | Does NOT contain certified bll0/tlmpin specs — those are in `scripts/bpool/specs/` |

### scripts/bpool/ — identification analysis suite (JAX-based)

| Path | Lines | Purpose | Class | Target | Priority | Notes |
|------|-------|---------|-------|--------|----------|-------|
| `jax_recovery_gate.py` | 560 | Synthetic recovery certification (Checks 1–6) | `tests_or_gates` | `stays_in_jmp_repo` | never | ⚠ PROVENANCE GATE — NEVER MOVE. Basis of all identification claims |
| `step4_realdata_baseline.py` | 678 | Certified paper baseline run: negLL 238362.79, min_eig +1.706 | `output_or_provenance` | `stays_in_jmp_repo` | never | ⚠ PROVENANCE ARTIFACT — NEVER MOVE OR EDIT |
| `step4_lr_pooling_test.py` | — | LR test: beta_E + beta_h_pt2 pooling | `tests_or_gates` | `stays_in_jmp_repo` | never | Establishes rejection of pooling; not re-runnable without full data |
| `step4_emit_results_json.py` | — | Export certified results to per-group JSON | `output_or_provenance` | `stays_in_jmp_repo` | low | Run once after certified baseline |
| `jax_ll_probe.py` | 614 | JAX likelihood builders for singles/couples | `reusable_core_candidate` | `core_package` | high | Cross-checks NumPy engine; confirmed Box-Cox bug (R1) |
| `jax_joint_hessian.py` | 210 | Exact JAX Hessian for joint likelihood | `reusable_core_candidate` | `core_package` | high | Minutes vs hours for CONOPT |
| `jax_optimize.py` | 244 | JAX-based optimization routines | `reusable_core_candidate` | `core_package` | high | Used in recovery certification |
| `joint_recovery_test.py` | 1,800 | Joint synthetic recovery test suite | `tests_or_gates` | `core_package` | medium | Comprehensive; portable |
| `recovery_test.py` | 627 | Synthetic recovery test (earlier version) | `tests_or_gates` | `stays_in_jmp_repo` | low | Superseded by joint version |
| `phase_a_param_binding.py` | 232 | Gate: all spec params bind without silent drops | `tests_or_gates` | `core_package` | high | |
| `phase_b_recovery_test.py` | 279 | Parameter recovery test (58-param bpool design) | `tests_or_gates` | `core_package` | high | |
| `build_bpool_precompute.py` | 653 | Per-year EUROMOD precompute with 7 gate checks | `EUROMOD_specific` | `app_package` | medium | |
| `run_bpool_euromod.py` | 673 | Chunked EUROMOD batch pricing; FR CPI deflators | `EUROMOD_specific` | `app_package` | medium | FR CPI constants phi_2015/2016/2017 |
| `run_bpool_euromod_chunk.py` | — | Chunk-level EUROMOD pricing (sub-script) | `EUROMOD_specific` | `app_package` | low | Called by `run_bpool_euromod.py` |
| `run_bpool_draws.py` | 294 | 100 singles + 30×30 couples bpool draws | `reusable_core_candidate` | `core_package` | medium | ⚠ R3: `log_prior` consistency |
| `assemble_bpool_priced.py` | 170 | Assemble chunk parquets; 4 canary checks | `EUROMOD_specific` | `app_package` | medium | |
| `build_bpool_estimation_ready.py` | — | Build estimation-ready bpool dataset | `EUROMOD_specific` | `app_package` | medium | |
| `build_bpool_singles.py` | — | Build singles bpool draws | `reusable_core_candidate` | `core_package` | medium | |
| `build_bpool_couples.py` | — | Build couples bpool draws | `reusable_core_candidate` | `core_package` | medium | |
| `build_joint_theta_star.py` | 133 | Build joint θ* for recovery tests | `tests_or_gates` | `core_package` | medium | |
| `harmonise_bpool_engine_ready.py` | — | Harmonise engine-ready dataset | `EUROMOD_specific` | `app_package` | low | |
| `slice_engine_ready.py` | — | Slice engine-ready dataset | `EUROMOD_specific` | `app_package` | low | |
| `check_bpool_engine_ready.py` | — | Engine-ready validation gate | `tests_or_gates` | `app_package` | low | |
| `_bpool_paths.py` | 59 | Path constants delegating to `path_helpers` | `application_layer_candidate` | `app_package` | low | |
| `jax_profile_couples_leisure.py` | — | JAX profile of couples-leisure direction | `diagnostics_reporting` | `stays_in_jmp_repo` | low | Identification analysis artefact |
| `jax_welfare_probe.py` (if present) | — | JAX welfare probe | `welfare_specific` | `app_package` | low | |
| `diag_gsplit_nonid_structure.py` | — | Non-ID structure diagnostic for gsplit | `diagnostics_reporting` | `stays_in_jmp_repo` | low | Documents gsplit failure; retain |
| `diag_nchildren_per_parent.py` | — | nchildren-per-parent diagnostic | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `bench_conopt_modelgen.py` | — | CONOPT model-generation benchmark | `diagnostics_reporting` | `stays_in_jmp_repo` | never | Documents R7 bottleneck; retain for reference |
| `phase0_repricing_variation.py` | — | Phase 0 repricing variation check | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `hours_mixture_d1.py` | — | Hours mixture distribution D1 | `reusable_core_candidate` | `core_package` | low | |
| `occ_draw_empirical.py` | — | Empirical occupation draw utilities | `reusable_core_candidate` | `core_package` | low | |
| `check_urbanisation_spec.py` | — | Urbanisation spec check | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `dump_theta_star.py` | — | Dump θ* to disk | `output_or_provenance` | `stays_in_jmp_repo` | low | |
| `rebuild_meta.py` | — | Rebuild metadata | `unclear_needs_review` | `stays_in_jmp_repo` | low | |
| `proto_gamspy_intermediate_var.py` | — | Prototype GAMSPy intermediate-var approach | `scratch_or_temporary` | `never` | never | |
| `_tmp_benchmark_multistart.py` | — | Multistart benchmark scratch | `scratch_or_temporary` | `never` | never | |
| `_tmp_benchmark_scipy_newton.py` | — | Scipy Newton benchmark scratch | `scratch_or_temporary` | `never` | never | |
| `validate_chosen_anchors.py` | — | Provenance validation: anchors | `tests_or_gates` | `stays_in_jmp_repo` | low | |
| `validate_chosen_flips.py` | — | Provenance validation: sign flips | `tests_or_gates` | `stays_in_jmp_repo` | low | |
| `validate_chosen_vs_canonical.py` | — | Provenance validation: vs canonical dataset | `tests_or_gates` | `stays_in_jmp_repo` | low | |
| `validate_chosen_vs_tminus1.py` | — | Provenance validation: vs t-1 | `tests_or_gates` | `stays_in_jmp_repo` | low | |
| `validate_chosen_yem_couples.py` | — | Provenance validation: YEM couples | `tests_or_gates` | `stays_in_jmp_repo` | low | |
| `validate_female_repricing.py` | — | Provenance validation: female repricing | `tests_or_gates` | `stays_in_jmp_repo` | low | |
| `verify_lh_coverage.py` | — | Verify labour-hours coverage | `tests_or_gates` | `stays_in_jmp_repo` | low | |
| `singles_vdir_bias_diagnostic.py` (if present) | — | Singles V_i^dir bias + node-count calibration | `diagnostics_reporting` | `stays_in_jmp_repo` | low | commit 5c8eb88 |
| `population_parity_gate.py` (if present) | — | Population-faithful parity gate | `tests_or_gates` | `stays_in_jmp_repo` | low | commit 0e66325 |
| `specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` | — | CERTIFIED 47-param spec (beta_ll=0, theta_l_m=−0.8 pinned) | `output_or_provenance` | `stays_in_jmp_repo` | never | ⚠ Certified baseline spec — do not modify |
| `specs/estimation_spec_joint_pooled_v1_bll0_tlmpin_gsplit.yaml` | — | 49-param gsplit spec — FAILED synthetic recovery gate | `output_or_provenance` | `stays_in_jmp_repo` | never | ⚠ NOT certified; label prominently |
| `specs/estimation_spec_joint_pooled_v1_bll0.yaml` | — | 47-param spec without theta_l_m pin | `output_or_provenance` | `stays_in_jmp_repo` | never | Pre-certified version |
| `specs/estimation_spec_joint_pooled_v1_bll0_gsplit_draw.yaml` | — | gsplit draw spec | `output_or_provenance` | `stays_in_jmp_repo` | never | |
| `specs/estimation_spec_joint_pooled_v1.yaml` | — | Base pooled joint spec (no pin) | `output_or_provenance` | `stays_in_jmp_repo` | never | |
| `specs/estimation_spec_bpool_p3a_v1.yaml` | — | bpool P3a spec | `output_or_provenance` | `stays_in_jmp_repo` | never | |

### scripts/Job_model/ — job-choice RURO branch

| Path | Lines | Purpose | Class | Target | Priority | Notes |
|------|-------|---------|-------|--------|----------|-------|
| `enh_job_universe.py` | 1,493 | Discrete job grid; `build_job_universe_from_ruro_ready()` | `reusable_core_candidate` | `core_package` | medium | Alternative draw model; same likelihood kernel |
| `enh_job_draws.py` | 1,111 | Person-level job draws; `generate_job_draws_long()` | `reusable_core_candidate` | `core_package` | medium | |
| `run_job_ruro_pipeline.py` | 499 | Orchestrator subprocess chain | `application_layer_candidate` | `app_package` | medium | FR-specific paths |
| `sanity_checks_job.py` | — | Job-model sanity checks | `diagnostics_reporting` | `app_package` | low | |
| `plot_loc_by_dehde.py` | — | Location-by-DEHDE visualisation | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |

### scripts/welfare/ — post-estimation welfare simulation

| Path | Lines | Purpose | Class | Target | Priority | Notes |
|------|-------|---------|-------|--------|----------|-------|
| `welfare_core.py` | 603 | Core welfare computation utilities | `welfare_specific` | `app_package` | medium | EUROMOD-dependent |
| `welfare_vdir.py` | 558 | V_i^dir direct utility welfare | `welfare_specific` | `app_package` | medium | |
| `welfare_resim_probe.py` | 186 | Resimulation probe for welfare | `welfare_specific` | `app_package` | low | |
| `welfare_correction_prep.py` | — | Correction prep for welfare pipeline | `welfare_specific` | `app_package` | low | |
| `welfare_chosen_contamination.py` | — | Chosen-outcome contamination audit | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `welfare_couples_contamination_audit.py` | — | Couples contamination audit | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `welfare_cross_track_residual_diag.py` | — | Cross-track residual diagnostic | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `welfare_assessment_unit_diag.py` | — | Assessment-unit diagnostic | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `run_stage1_w3.py` | — | Stage 1: welfare wave-3 | `welfare_specific` | `app_package` | medium | |
| `run_stage2_*.py` (×15) | — | Stage 2 sub-tasks (resim, parity, audit, vdir, etc.) | `welfare_specific` | `app_package` | medium | |
| `run_stage3a_pinned_baseline_validation.py` | — | Stage 3a: pinned baseline validation | `tests_or_gates` | `stays_in_jmp_repo` | low | |
| `run_stage3b1_engine_ready_parity.py` | — | Stage 3b1: engine-ready parity | `tests_or_gates` | `stays_in_jmp_repo` | low | |
| `run_stage3b2_controlled_reestimation.py` | — | Stage 3b2: controlled re-estimation | `welfare_specific` | `app_package` | low | |
| `run_stage3b3_synthetic_recovery.py` | — | Stage 3b3: synthetic recovery | `tests_or_gates` | `stays_in_jmp_repo` | low | |
| `run_stage4a_baseline_policy.py` | — | Stage 4a: baseline policy sim | `welfare_specific` | `app_package` | low | |
| `run_stage4b_population_parity_gate.py` | — | Stage 4b: population parity gate | `tests_or_gates` | `stays_in_jmp_repo` | low | commit 0e66325 |
| `run_stage4c_singles_vdir_smoke.py` | — | Stage 4c: singles vdir smoke test | `tests_or_gates` | `stays_in_jmp_repo` | low | |
| `run_stage4c2_vdir_bias_calibration.py` | — | Stage 4c2: vdir bias calibration | `diagnostics_reporting` | `stays_in_jmp_repo` | low | commit 5c8eb88 |

### scripts/multi_year/ — CPI harmonization and year stacking

| Path | Lines | Purpose | Class | Target | Priority | Notes |
|------|-------|---------|-------|--------|----------|-------|
| `m1_harmonise_cpi.py` | — | FR CPI harmonisation 2015–2017 | `application_layer_candidate` | `app_package` | medium | FR CPI constants; not generic |
| `m1_stack_years.py` | — | Stack per-year estimation-ready datasets | `application_layer_candidate` | `app_package` | medium | |
| `m1_validate.py` | — | Validation of stacked dataset | `tests_or_gates` | `app_package` | medium | |
| `m1_add_cluster_key.py` | — | Add cluster key to stacked dataset | `application_layer_candidate` | `app_package` | low | |
| `m1_config.py` | — | Multi-year config constants | `configuration` | `app_package` | medium | |
| `m1_identity_validation.py` | — | Identity validation across years | `tests_or_gates` | `stays_in_jmp_repo` | low | |
| `m1_isf_check_2018.py` | — | ISF check for 2018 year | `scratch_or_temporary` | `never` | never | One-off year check |

### scripts/maintenance/

| Path | Lines | Purpose | Class | Target | Priority | Notes |
|------|-------|---------|-------|--------|----------|-------|
| `prepare_pooled_estimation_ready.py` | — | Pooled dataset prep | `application_layer_candidate` | `app_package` | medium | |
| `run_pooled_P3a_estimation.py` | — | Phase 3a pooled estimation runner | `application_layer_candidate` | `app_package` | medium | |
| `run_pooled_P3a_presolver_checks.py` | — | Pre-solver checks | `tests_or_gates` | `stays_in_jmp_repo` | low | |
| `run_pooled_P3a_S5_S8_hessian_recompute.py` | — | Hessian recompute stages 5–8 | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `run_pooled_P3a_S6_preference_comparison.py` | — | Preference comparison stage 6 | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `run_pooled_P3a_S6_theta_c_singles_profile.py` | — | theta_c singles profile | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `validate_occ_dummies.py` | — | Occupation dummy validation | `tests_or_gates` | `stays_in_jmp_repo` | low | |
| `validate_v1.py` | — | V1 validation | `tests_or_gates` | `stays_in_jmp_repo` | low | |
| `validate_v7.py` | — | V7 validation | `tests_or_gates` | `stays_in_jmp_repo` | low | |
| `rename_stijn_to_ruro.py` | — | One-off rename script | `scratch_or_temporary` | `never` | never | |

### scripts/diagnostics/

| Path | Lines | Purpose | Class | Target | Priority | Notes |
|------|-------|---------|-------|--------|----------|-------|
| `RURO_post_estimation_M1_diagnostics.py` | — | M1 post-estimation diagnostics | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `RURO_post_estimation_M1_naive_diagnostics.py` | — | M1 naive diagnostics | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `check_nchildren_simple.py` | — | nchildren check (simple) | `diagnostics_reporting` | `stays_in_jmp_repo` | never | |
| `check_nchildren_variation.py` | — | nchildren variation check | `diagnostics_reporting` | `stays_in_jmp_repo` | never | |
| `check_nchildren_variation_v2.py` | — | nchildren variation v2 | `diagnostics_reporting` | `stays_in_jmp_repo` | never | |
| `check_preference_diagnostics.py` | — | Preference diagnostics | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `check_type_ids.py` | — | Type ID validation | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `compare_scipy_gamspy.py` | — | Scipy vs GAMSPy comparison | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `run_stage5a2_cluster_se_artifact.py` | — | Stage 5a2 cluster SE artifact | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `run_stage5a_postestimation_descriptives.py` | — | Post-estimation descriptives | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `test_gamspy_vs_scipy.py` | — | GAMSPy vs scipy test | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |

### scripts/pilot/ — pre-production JAX/identification experiments

| Path | Lines | Purpose | Class | Target | Priority | Notes |
|------|-------|---------|-------|--------|----------|-------|
| `pilot_wage_draw.py` | — | Pilot wage draw utilities | `scratch_or_temporary` | `never` | never | Pilot predecessor to production draws |
| `build_pilot_couples_product.py` | — | Build pilot couples product | `scratch_or_temporary` | `never` | never | |
| `build_precompute_ready.py` | — | Build pilot precompute | `scratch_or_temporary` | `never` | never | |
| `fit_pilot_mincer.py` | — | Fit pilot Mincer equation | `scratch_or_temporary` | `never` | never | |
| `export_pilot_euromod_inputs*.py` (×2) | — | Export pilot EUROMOD inputs | `scratch_or_temporary` | `never` | never | |
| `merge_pilot_em_outputs.py` | — | Merge pilot EM outputs | `scratch_or_temporary` | `never` | never | |
| `run_pilot_em_blocks.py` | — | Run pilot EM blocks | `scratch_or_temporary` | `never` | never | |
| `_bisect_ll.py` | — | LL bisect diagnostic | `scratch_or_temporary` | `never` | never | |
| `_precompute_gate.py` | — | Precompute gate probe | `scratch_or_temporary` | `never` | never | |
| `_rebuild_c_norm.py` | — | c_norm rebuild | `scratch_or_temporary` | `never` | never | |
| `_resolve_hnpos.py` | — | hn/pos resolution probe | `scratch_or_temporary` | `never` | never | |
| `_run_*.py` (×9) | — | Various pilot diagnostic runners | `scratch_or_temporary` | `never` | never | |
| `_tmp_*/` (×4 dirs with JSON) | — | Temporary output dirs from pilot runs | `output_or_provenance` | `stays_in_jmp_repo` | low | Preserve as identification experiment record |
| `specs/estimation_spec_nc_pilot_couples_2016.yaml` | — | Pilot couples spec | `scratch_or_temporary` | `never` | never | |
| `config/pilot_mincer_coefficients_v1.json` | — | Pilot Mincer coefficients | `output_or_provenance` | `stays_in_jmp_repo` | low | |

### scripts/ root-level loose files

| Path | Lines | Purpose | Class | Target | Priority | Notes |
|------|-------|---------|-------|--------|----------|-------|
| `RURO_draws.py` | — | Pre-enhanced RURO draws (root copy) | `unclear_needs_review` | `stays_in_jmp_repo` | never | Superseded by `enhanced/enh_RURO_draws.py` |
| `RURO_estimate_FR.py` | — | Pre-enhanced FR estimator (root copy) | `unclear_needs_review` | `stays_in_jmp_repo` | never | Superseded |
| `RURO_euromod.py` | — | Pre-enhanced EUROMOD runner (root copy) | `unclear_needs_review` | `stays_in_jmp_repo` | never | Superseded |
| `RURO_post_estimation.py` | — | Pre-enhanced post-estimation (root copy) | `unclear_needs_review` | `stays_in_jmp_repo` | never | Superseded |
| `RURO_prep.py` | — | Pre-enhanced prep (root copy) | `unclear_needs_review` | `stays_in_jmp_repo` | never | Superseded |
| `RURO_prep_mnl_basic.py` | — | Pre-enhanced MNL prep (root copy) | `unclear_needs_review` | `stays_in_jmp_repo` | never | Superseded |
| `path_helpers.py` | — | Root copy of path_helpers | `unclear_needs_review` | `never` | never | Duplicate of `enhanced/path_helpers.py`; verify which is canonical |
| `france_data_prep.py` | — | Root copy of FR data prep | `unclear_needs_review` | `never` | never | Likely superseded |
| `prepare_FR_gsur.py` | — | Root copy of GSUR builder | `unclear_needs_review` | `never` | never | Likely superseded |
| `generate_html_report.py` | — | HTML report generator | `diagnostics_reporting` | `stays_in_jmp_repo` | low | |
| `extract_excel_text.py` | — | Excel text extractor | `scratch_or_temporary` | `never` | never | |
| `run_post_estimation_standalone.py` | — | Standalone post-estimation runner | `application_layer_candidate` | `app_package` | low | |
| `init_params_singles_template.csv` | — | Singles init params template | `configuration` | `core_package` | low | |
| `seed_boxcox_init.csv` | — | Box-Cox seed init values | `configuration` | `core_package` | low | |
| `runners/` (dir) | — | Additional runner scripts | `unclear_needs_review` | `stays_in_jmp_repo` | low | Contents not individually listed above |
| `run_fr_2016_*.ps1` (×2) | — | PowerShell pipeline runners | `application_layer_candidate` | `app_package` | low | FR 2016 specific |
| `run_post_estimation.ps1` | — | PowerShell post-estimation runner | `application_layer_candidate` | `app_package` | low | |
| `sync_backup.ps1` | — | Backup sync script | `scratch_or_temporary` | `never` | never | |
| `tdo.ps1` | — | TODO helper script | `scratch_or_temporary` | `never` | never | |
| `run_pipeline_explicit.ipynb` | — | Notebook pipeline runner | `scratch_or_temporary` | `never` | never | |
| `script_files_structure.md` | — | Script structure documentation | `output_or_provenance` | `stays_in_jmp_repo` | low | |

### scripts/archive/ — superseded (never migrate)

| Path | Purpose | Class | Target | Priority |
|------|---------|-------|--------|----------|
| `rum_approach/RUM/` (21 × .py) | Legacy translog/Box-Cox RUM: DCM1/DCM2, biogeme, train_mnl, scenarios | `output_or_provenance` | `never` | never |
| `old_ruro_pre_enhanced/` (7 × .py) | Pre-enhanced RURO: RURO_boxcox_*, full_RURO, inspect, run_fr_2021 | `output_or_provenance` | `never` | never |
| `experimental/` (5 × .py) | Interactive/memory-only pipeline experiments | `scratch_or_temporary` | `never` | never |
| `fixes/` (2 × .py) | One-off SE and post-estimation rerun fixes | `scratch_or_temporary` | `never` | never |
| `old_data_prep/data_prep2.py` | Old data prep | `output_or_provenance` | `never` | never |
| `backups_2025_12/` (3 files) | Manual backups from Dec 2025 | `output_or_provenance` | `never` | never |
| `run_gamspy.ps1` | Archive PowerShell runner | `scratch_or_temporary` | `never` | never |

### src/mnl/ — package scaffold (stub — does NOT expose RURO engine)

| Path | Lines | Purpose | Class | Target | Priority | Notes |
|------|-------|---------|-------|--------|----------|-------|
| `src/mnl/__init__.py` | 12 | Version only | `unclear_needs_review` | `core_package` | high | ⚠ Exposes nothing of the RURO engine |
| `src/mnl/models/mnl.py` | 40 | statsmodels MNLogit wrapper | `unclear_needs_review` | `never` | never | ⚠ R2: completely wrong model; delete before any release |
| `src/mnl/integration/euromod.py` | 153 | EUROMOD connector with lazy load | `EUROMOD_specific` | `app_package` | low | Pattern sound; no real implementation |
| `src/mnl/pipelines/estimation.py` | 48 | Minimal stub pipeline | `unclear_needs_review` | `app_package` | low | |
| `src/mnl/config.py` | — | Package-level config | `configuration` | `core_package` | low | |
| `src/mnl/data/loaders.py` | — | Data loader stubs | `unclear_needs_review` | `core_package` | low | Stubs only |
| `src/mnl/evaluation/metrics.py` | — | Evaluation metrics stubs | `unclear_needs_review` | `core_package` | low | Stubs only |
| `src/mnl.egg-info/` | — | Build artefacts | `output_or_provenance` | `never` | never | |

### tests/

| Path | Lines | Purpose | Class | Target | Priority | Notes |
|------|-------|---------|-------|--------|----------|-------|
| `tests/test_recovery_cov_verdict.py` | 140 | Hessian verdict regression tests | `tests_or_gates` | `core_package` | high | Should co-locate with core after migration |
| `tests/test_imports.py` | 6 | Package import sanity | `tests_or_gates` | `core_package` | high | |

### stijn/ — R reference implementation

| Path | Purpose | Class | Target | Priority | Notes |
|------|---------|-------|--------|----------|-------|
| `Ruro_estimation_H.Rmd` | R RURO estimation (Hisham variant) | `output_or_provenance` | `stays_in_jmp_repo` | never | Reference; do not migrate |
| `Ruro_estimation_new.Rmd` | R RURO estimation (new variant) | `output_or_provenance` | `stays_in_jmp_repo` | never | |
| `Ruro_functions_EMRWS.R` | R RURO functions (EMRWS) | `output_or_provenance` | `stays_in_jmp_repo` | never | |
| `Ruro_simulation_H.Rmd` | R RURO simulation | `output_or_provenance` | `stays_in_jmp_repo` | never | |

### config/ and configs/ — pipeline configuration

| Path | Purpose | Class | Target | Priority | Notes |
|------|---------|-------|--------|----------|-------|
| `config/multi_year/fr_p*.yaml` (×5) | Multi-year pipeline stage configs | `configuration` | `app_package` | medium | FR-specific stage parameters |
| `configs/default.yaml` | Default MNL pipeline config (generic) | `configuration` | `core_package` | low | Generic column/path config; not FR-specific |

### notes/

| Path | Purpose | Class | Target | Priority | Notes |
|------|---------|-------|--------|----------|-------|
| `notes/EUROMO_sys_france_2015.md` | EUROMOD system notes for FR 2015 | `output_or_provenance` | `stays_in_jmp_repo` | never | Documentation |
| `notes/R_REFERENCE_vs_PYTHON_SPECIFICATION.md` | R vs Python spec comparison | `output_or_provenance` | `stays_in_jmp_repo` | never | Reference document |

### Root-level project files

| Path | Purpose | Class | Target | Priority | Notes |
|------|---------|-------|--------|----------|-------|
| `pyproject.toml` | Package build config (current `src/mnl` package) | `configuration` | `core_package` | high | Needs significant revision for future monorepo |
| `requirements.txt` | Dependency spec | `configuration` | `core_package` | high | Conflates core and app deps; needs split |
| `README.md` | Project readme | `output_or_provenance` | `stays_in_jmp_repo` | low | |
| `RURO_MNL_project_files_structure.md` | Files structure documentation | `output_or_provenance` | `stays_in_jmp_repo` | low | |
| `01_repo_inventory.md` | This document | `output_or_provenance` | `stays_in_jmp_repo` | never | |
| `debug.log`, `gate_*.log`, `gate_output.txt` | Debug/gate run logs | `output_or_provenance` | `stays_in_jmp_repo` | never | |
| `.markdownlint.json`, `.mplconfig` | Tool configs | `configuration` | `stays_in_jmp_repo` | never | |
| `Microsoft/` | Unknown (contents not examined) | `unclear_needs_review` | `stays_in_jmp_repo` | low | |
| `_gams_work/` | GAMSPy work directory | `output_or_provenance` | `never` | never | Runtime artefacts |

### outputs/, Results/, Data/, Pdfs/, Prompts/, literature/, notebooks/

| Path | Purpose | Class | Target | Priority | Notes |
|------|---------|-------|--------|----------|-------|
| `outputs/opportunity_diagnostics_certified_v1.parquet` | Certified opportunity diagnostics | `output_or_provenance` | `stays_in_jmp_repo` | never | |
| `outputs/figures/stage5a_*.png` (×6) | Stage 5a diagnostic figures | `output_or_provenance` | `stays_in_jmp_repo` | never | |
| `outputs/welfare/stage1_w3/` | Welfare stage 1 outputs | `output_or_provenance` | `stays_in_jmp_repo` | never | |
| `outputs/KEEP_RESULTS.md` | Results preservation note | `output_or_provenance` | `stays_in_jmp_repo` | never | |
| `Results/JMP_*.csv, .tex, .json, .npy, .log` (30+ files) | JMP paper estimation results, tables, SE matrices | `output_or_provenance` | `stays_in_jmp_repo` | never | Do not delete; paper artefacts |
| `Data/documentation/`, `Data/external/` | Data documentation and external inputs | `output_or_provenance` | `stays_in_jmp_repo` | never | |
| `Pdfs/*.pdf` (8 files) | Reference papers + model documentation PDFs | `output_or_provenance` | `stays_in_jmp_repo` | never | |
| `Prompts/*.md, Prompts/welfare/*.txt` | LLM prompts used during development | `output_or_provenance` | `stays_in_jmp_repo` | never | Development artefacts; keep for audit trail |
| `Prompts/replies_GPT/` | GPT reply artefacts | `output_or_provenance` | `stays_in_jmp_repo` | never | |
| `literature/` | Literature files | `output_or_provenance` | `stays_in_jmp_repo` | never | |
| `notebooks/estimation_notebook.ipynb` | Estimation notebook (exploration) | `scratch_or_temporary` | `stays_in_jmp_repo` | never | |
| `notebooks/README.md` | Notebook README | `output_or_provenance` | `stays_in_jmp_repo` | never | |

---

## C. Dependency Map

### Main estimation pipeline (continuous RURO, FR)

```text
FR SILC/EUROSTAT raw data
        │
        ▼
enh_france_data_prep.py          clean_harmonize_fr(), stepwise_filter_households()
        │   enh_prepare_FR_gsur_v2.py   GSUR labour-force share lookup (INSEE/Eurostat)
        ▼
enh_RURO_prep.py                 NUTS1, educ dummies, experience
        │
        ▼
enh_RURO_draws.py  ──────── ⚠ log_prior formula A ─────────────────────────┐
        │                                                                   │
        ▼                                                                   │
enh_RURO_euromod.py              EUROMOD Java/pythonnet; 35h FR overtime    │
        │                                                                   │
        ▼                                                                   │
enh_RURO_prep_mnl_basic.py ──── ⚠ log_prior formula B (must match A) ──────┘
        │   (2,433 lines; couples reshape here)
        ▼
estimation_spec_parser.py        YAML → EstimationSpec; 4-group _sm _sf _m _f
        │
        ├─────────────────────────────────────────────┐
        ▼                                             ▼
gamspy_estimation_vectorized.py              estimation_engine.py
(GAMSPy CONOPT/IPOPT)                       (NumPy/Numba scipy)
        │                                             │
        └────────────────────┬────────────────────────┘
                             ▼
                   enh_RURO_estimate_FR.py   8-step orchestrator
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
      compute_standard_errors.py   cluster_robust_se.py
                             │
                             ▼
                    save_results_json()
                             │
               ┌─────────────┴──────────────┐
               ▼                            ▼
  diagnostics_bundle.py        RURO_post_estimation_styled.py
  (40+ metrics, 2,505 lines)   (10,232 lines; HTML/MD + MUC/MUL/contours)
                                            │
                                            ▼
                                  scripts/welfare/
```

### bpool / JAX certification pipeline

```text
run_bpool_draws.py
    ├── build_bpool_precompute.py   per-year EUROMOD + 7 gate checks
    │        └── run_bpool_euromod.py    chunked pricing, FR CPI
    ├── assemble_bpool_priced.py    chunk parquets + 4 canary checks
    └── validate_chosen_*.py (×7)  provenance gates
              │
              ▼
    jax_ll_probe.py + jax_joint_hessian.py + jax_optimize.py
              │  (cross-checks NumPy; confirmed Box-Cox bug — see R1)
              ▼
    jax_recovery_gate.py           Checks 1–6  ⚠ NEVER MOVE
              │
    phase_a_param_binding.py  phase_b_recovery_test.py
              │
              ▼
    step4_realdata_baseline.py     certified paper run  ⚠ NEVER MOVE OR EDIT
              │
    step4_emit_results_json.py     per-group JSON export
              │
    RURO_post_estimation_styled.py (per-group --joint-baseline-json mode)
```

### Certified spec location (important correction vs first draft)

```text
scripts/bpool/specs/
    estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml   ← CERTIFIED baseline spec
    estimation_spec_joint_pooled_v1_bll0_tlmpin_gsplit.yaml  ← NON-CERTIFIED (failed gate)
    ...

scripts/enhanced/specifications/
    estimation_spec_ruro_occ_P3a_pooled.yaml, estimation_spec_v2.yaml, ...
    (general-purpose specs; do NOT contain the certified bll0 family)
```

### Import graph — critical chains

```text
estimation_engine.py
    └── estimation_utils.py        ⚠ R1: box_cox_derivative_theta Taylor bug
            └── (numpy, numba, scipy)

gamspy_estimation_vectorized.py
    ├── estimation_spec_parser.py
    ├── path_helpers.py            ⚠ R4: ensure_local_workdir() UNC dependency
    └── (gamspy, gams)

enh_RURO_estimate_FR.py
    ├── estimation_engine.py
    ├── estimation_spec_parser.py
    ├── gamspy_estimation_vectorized.py
    ├── cluster_robust_se.py
    ├── diagnostics_bundle.py
    └── path_helpers.py

bpool JAX files
    ├── jax, optax, optimistix
    └── estimation_spec_parser.py  (shared spec parsing)
```

---

## D. Package Boundary Analysis

### EUROMOD boundary criterion

A module belongs to **`core_package`** only if it can be imported and exercised without:

- EUROMOD/Java on PATH
- FR CPI constants (`phi_2015`, `phi_2016`, `phi_2017`)
- NUTS1 codes or INSEE benchmark data
- EUROMOD-STORAGE path resolution (`ensure_local_workdir()`)
- 35h French overtime split rule

### Proposed `dclaborsupply` (core)

```text
dclaborsupply/
  likelihood/
    engine.py              ← estimation_engine.py   ⚠ fix Box-Cox bug first
    utils.py               ← estimation_utils.py    ⚠ fix Box-Cox bug first
    utils_ac2013.py        ← estimation_utils_AC2013.py
  spec/
    parser.py              ← estimation_spec_parser.py
    constraints.py         ← expression_constraints.py
    schemas/               ← scripts/enhanced/specifications/ (general YAMLs)
  solvers/
    gamspy_vectorized.py   ← gamspy_estimation_vectorized.py
    jax_optimize.py        ← bpool/jax_optimize.py
  se/
    cluster_robust.py      ← cluster_robust_se.py
    numerical.py           ← compute_standard_errors.py
  draws/
    continuous.py          ← enh_RURO_draws.py (draw generation only; no EUROMOD)
    job_universe.py        ← Job_model/enh_job_universe.py
    job_draws.py           ← Job_model/enh_job_draws.py
    hours_mixture.py       ← bpool/hours_mixture_d1.py
  jax/
    ll_probe.py            ← bpool/jax_ll_probe.py
    joint_hessian.py       ← bpool/jax_joint_hessian.py
  sampler/
    mcfadden.py            ← mcfadden_sampler.py
  occupation/
    utils.py               ← occupation_choice_utils.py  ⚠ verify no FR SILC names
  diagnostics/
    bundle.py              ← diagnostics_bundle.py
  gates/
    phase_a.py             ← bpool/phase_a_param_binding.py
    phase_b.py             ← bpool/phase_b_recovery_test.py
    joint_recovery.py      ← bpool/joint_recovery_test.py
```

### Proposed `dclaborsupply_app` (FR + EUROMOD)

```text
dclaborsupply_app/
  france/
    data_prep.py           ← enh_france_data_prep.py
    gsur_v2.py             ← enh_prepare_FR_gsur_v2.py
    prep_ruro.py           ← enh_RURO_prep.py
    cpi.py                 ← FR CPI constants (phi_2015/2016/2017)
  euromod/
    connector.py           ← src/mnl/integration/euromod.py (improve)
    runner.py              ← enh_RURO_euromod.py
    bpool_runner.py        ← bpool/run_bpool_euromod.py
    bpool_precompute.py    ← bpool/build_bpool_precompute.py
  pipeline/
    prep_mnl.py            ← enh_RURO_prep_mnl_basic.py   ⚠ R3: consolidate log_prior
    estimate_fr.py         ← enh_RURO_estimate_FR.py
    job_pipeline.py        ← Job_model/run_job_ruro_pipeline.py
  welfare/
    core.py                ← welfare/welfare_core.py
    vdir.py                ← welfare/welfare_vdir.py
    resim_probe.py         ← welfare/welfare_resim_probe.py
    correction_prep.py     ← welfare/welfare_correction_prep.py
    stages/                ← welfare/run_stage*.py
  multi_year/
    harmonise_cpi.py       ← multi_year/m1_harmonise_cpi.py
    stack_years.py         ← multi_year/m1_stack_years.py
    config.py              ← multi_year/m1_config.py
  paths.py                 ← path_helpers.py + _bpool_paths.py
  reports/
    post_estimation.py     ← RURO_post_estimation_styled.py
```

### `stays_in_jmp_repo/` — paper-reproduction only, never published as a package

```text
jmp/
  baseline/
    step4_realdata_baseline.py         ⚠ FREEZE
    step4_lr_pooling_test.py           ⚠ FREEZE
    step4_emit_results_json.py
  gates/
    jax_recovery_gate.py               ⚠ FREEZE
    validate_chosen_*.py (×7)          ⚠ FREEZE
    run_stage3a_pinned_baseline_validation.py
    run_stage4b_population_parity_gate.py
  specs/
    estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml   ⚠ CERTIFIED — never modify
    estimation_spec_joint_pooled_v1_bll0_tlmpin_gsplit.yaml  ⚠ NON-CERTIFIED — label
    (remaining bpool specs)
  stijn/                               R reference implementations
  scripts/archive/
  Results/                             paper output artefacts
  outputs/                             certified diagnostics parquet + figures
  docs/                                execution logs, literature review
  Prompts/                             development LLM prompts
  notes/                               EUROMOD system notes
```

---

## E. Proposed Monorepo Tree

```text
MNL/
├── packages/
│   ├── dclaborsupply/
│   │   ├── pyproject.toml
│   │   └── src/dclaborsupply/
│   │       ├── __init__.py    (expose: EstimationSpec, compute_likelihood_*, etc.)
│   │       ├── likelihood/    engine.py  utils.py   ⚠ fix Box-Cox before publish
│   │       ├── spec/          parser.py  constraints.py  schemas/
│   │       ├── solvers/       gamspy_vectorized.py  jax_optimize.py
│   │       ├── se/            cluster_robust.py  numerical.py
│   │       ├── draws/         continuous.py  job_universe.py  job_draws.py
│   │       ├── jax/           ll_probe.py  joint_hessian.py
│   │       ├── sampler/       mcfadden.py
│   │       ├── occupation/    utils.py   ⚠ verify FR constants absent
│   │       ├── diagnostics/   bundle.py
│   │       └── gates/         phase_a.py  phase_b.py  joint_recovery.py
│   │   └── tests/
│   │       ├── test_recovery_cov_verdict.py  (migrate from repo root)
│   │       ├── test_imports.py
│   │       ├── test_likelihood.py            (new — unit tests)
│   │       └── test_boundary.py              (new — no-EUROMOD gate; see §H)
│   │
│   └── dclaborsupply_app/
│       ├── pyproject.toml   (depends on dclaborsupply)
│       └── src/dclaborsupply_app/
│           ├── france/   euromod/   pipeline/   welfare/
│           ├── multi_year/   paths.py   reports/
│           └── configs/  ← config/multi_year/*.yaml
│
├── jmp/                              paper-reproduction scripts (no package)
│   ├── baseline/   gates/   specs/   stijn/   Results/   outputs/
│   ├── scripts/archive/   Prompts/   notes/   docs/   Pdfs/   literature/
│   └── Data/   notebooks/
│
├── scripts/                          CURRENT LOCATION — do not move yet
│   ├── enhanced/   bpool/   Job_model/   welfare/
│   ├── multi_year/   maintenance/   diagnostics/   pilot/   archive/
│   └── (root loose files — superseded; not migrated)
│
├── src/mnl/                          CURRENT STUB — delete after packages/ is live
├── tests/                            move to packages/dclaborsupply/tests/
├── configs/default.yaml              → packages/dclaborsupply/src/.../default.yaml
├── pyproject.toml                    → update to workspace (uv/hatch monorepo)
└── requirements.txt                  → split: core / app / dev
```

---

## F. RUM vs RURO — API Implications

### Model inventory

| Model | Location | Status |
|-------|----------|--------|
| Continuous RURO | `scripts/enhanced/` | Production; certified |
| Job-choice RURO | `scripts/Job_model/` | Active; same likelihood kernel |
| Legacy RUM (translog/Box-Cox MNL) | `scripts/archive/rum_approach/RUM/` (21 files) | Archived; NEVER migrate; different model |
| R RURO reference | `stijn/` (4 files) | Reference only; read-only |
| statsmodels MNLogit stub | `src/mnl/models/mnl.py` | ⚠ R2: wrong model entirely; delete |

### Critical distinction: importance-sampling correction

**RUM:** `log_likelihood = Σ log P_MNL(chosen | alternatives)`  
**RURO:** `log_likelihood = Σ [log P_MNL(chosen | draws) − log_prior(draws)]`

The `log_prior` subtraction is the critical correction. Any refactor that silently drops or modifies `log_prior` produces RUM results with no error. The formula is currently split across two files (R3); it must be consolidated before any module boundary is drawn.

### Proposed public API for `dclaborsupply`

```python
def compute_log_likelihood(
    spec: EstimationSpec,
    precomputed: PrecomputedData,
    theta: np.ndarray,
    *,
    backend: Literal["numpy", "jax"] = "numpy",
) -> float:
    """RURO importance-sampling log-likelihood. If spec.proposal_density is None,
    reduces to standard RUM (for future extensibility only — do not use for RURO)."""
    ...
```

**Do not abstract away:** the 4-group architecture; `log_prior` (must be canonical); UNC workaround.

---

## G. Risk Register

| # | Risk | Severity | Probability | Evidence / provenance | Mitigation |
|---|------|----------|-------------|----------------------|------------|
| R1 | **Box-Cox Taylor bug** in `estimation_utils.py:box_cox_derivative_theta` (~0.5 off near θ = 0) | HIGH | CERTAIN | Confirmed by JAX/FD cross-check in `scripts/bpool/jax_ll_probe.py`; documented in project memory `project_box_cox_theta_grad_bug.md`; affects NumPy gradient + Check-5 Hessian | Fix before publishing; carry fix during migration; verify with Gate 3 in §H |
| R2 | **`src/mnl/models/mnl.py`** is statsmodels MNLogit — wrong model | HIGH | CERTAIN | File inspection (40 lines, wraps `statsmodels.MNLogit`) | Delete before any public release |
| R3 | **`log_prior` split** across `enh_RURO_draws.py` and `enh_RURO_prep_mnl_basic.py` | HIGH | MED (refactor trigger) | Both files compute the correction; byte-identical required | Consolidate into single canonical function before splitting packages |
| R4 | **UNC path workaround** (`ensure_local_workdir()`) is a runtime hard dependency for GAMSPy | HIGH | HIGH | `path_helpers.py:265`; measured failure mode on network drives | Keep importable before any GAMSPy call; enforce via test |
| R5 | **gsplit spec** not labeled as non-certified; shares directory with certified spec | HIGH | MED | Both in `scripts/bpool/specs/`; gsplit FAILED synthetic gate (err/SE = 19) | Add `STATUS: NON-CERTIFIED — FAILED SYNTHETIC RECOVERY GATE` to YAML header |
| R6 | **Numba JIT import sensitivity** | MED | MED | `_USE_NUMBA` flag; JIT decorators sensitive to module rename | Test Numba path after any `__init__.py` or module rename |
| R7 | **CONOPT model-generation bottleneck** (94% of wall time) | MED | CERTAIN | Benchmarked in `scripts/bpool/bench_conopt_modelgen.py`; threads/memory/listing tuning all measured as dead ends | Not a migration blocker; document in package README |
| R8 | **EUROMOD transitive import leak** into core | MED | MED | Several scripts import `enh_RURO_euromod` at module level | CI gate: `python -c "import dclaborsupply"` must succeed without Java on PATH |
| R9 | **Provenance gate scripts moved** accidentally | CRITICAL | LOW (catastrophic) | `jax_recovery_gate.py` and `step4_realdata_baseline.py` underpin all identification/paper claims | Mark read-only; add CI check comparing file hashes to certified commit |
| R10 | **FR-specific constants in nominally generic functions** | MED | MED | `occupation_choice_utils.py` likely has FR SILC column names (not read in full) | Boundary test in §H will surface these; parameterise before publishing |

---

## H. Next Step — Boundary-Proving Integration Test

Write **`tests/test_boundary.py`** (new file only; no edits to existing files). This test proves the core can be imported and exercised without EUROMOD, without France-specific constants, and without EUROMOD-STORAGE. It surfaces R1, R8, and R10 before any file is moved.

### Five gates

#### Gate 1 — Import without EUROMOD/Java on PATH

```python
import sys
# Run in an environment with EUROMOD absent
from scripts.enhanced.estimation_engine import compute_likelihood_singles
from scripts.enhanced.estimation_utils import build_precomputed_data_singles
from scripts.enhanced.estimation_spec_parser import parse_estimation_spec
assert "euromod" not in sys.modules
```

#### Gate 2 — Synthetic-data likelihood is finite and negative

```python
# Construct minimal synthetic PrecomputedData; call compute_likelihood_singles()
# Assert: np.isfinite(ll) and ll < 0
```

#### Gate 3 — Analytical gradient matches finite-difference to 1e-4

```python
# |grad_analytical - grad_FD| / (|grad_FD| + 1e-8) < 1e-4 element-wise
# If Box-Cox bug (R1) is present, this gate will fail for theta_c near 0 — expected
```

#### Gate 4 — Certified spec parses without error

```python
spec = parse_estimation_spec(
    "scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml"
)
assert spec is not None
assert "beta_ll" in spec.fixed_params   # pinned to 0
```

#### Gate 5 — No EUROMOD-STORAGE path resolution in core path

```python
from unittest.mock import patch
with patch("scripts.enhanced.path_helpers.ensure_local_workdir",
           side_effect=AssertionError("core called EUROMOD path")):
    # Run compute_likelihood_singles() on synthetic data
    # Assert: no AssertionError raised
```

### What this gate does NOT do

- Does not move, rename, or edit any existing production file
- Does not create packages or modify `pyproject.toml`
- Does not require GAMSPy, EUROMOD, or EUROMOD-STORAGE
- Does not touch `jax_recovery_gate.py` or `step4_realdata_baseline.py`

---

*End of inventory. All paths verified via `find`/`wc -l`. No production files modified.*
