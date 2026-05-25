# Move Manifest — 2026-05-25 docs/ reorganization

## Context
- Approver: Hisham Haydar
- Scope: docs/ only (no code, no Results/, no pre-existing archive content)
- Policy basis: docs/package/RURO_PACKAGE_PORTABILITY_AND_CLEANUP_POLICY_v1.md, docs/package/RURO_PROJECT_HYGIENE_CLEANUP_RECOMMENDATIONS.md
- Working tree: U:\Desktop\Nizam_Hisham\MNL

## Phase commit log
| Phase | Description | SHA |
|---|---|---|
| A | Scaffold dirs + READMEs (no moves) | 784d5f5 |
| B1a | Move files to docs/package/ | cc6ae27 |
| B1b | Move files to docs/methods/ | 9508336 |
| B1c | Move files to docs/specifications/ | 510ea09 |
| B1d | Move files to docs/estimation/ | 4b0abae |
| B1e | Move files to docs/reporting/ | 2539abd |
| B1f | Move files to docs/jmp_methodology/ | c97598c |
| B1g | Move stray RURO_R_REFERENCE_COMPARISON_SECTOR_OPPORTUNITY_PLAN.md to methods/ | d463cfa |
| B2a | Move docs/euromod_reference/ -> docs/France_case/euromod_reference/ | a3c8469 |
| B2b | Move docs/notes/ -> docs/France_case/notes/ | 97061b7 |
| B2c | Move docs/canary_reports/ -> docs/France_case/canary_reports/ | 758aa0b |
| B2d | Move docs/job_choice/ -> docs/France_case/job_choice/ | addb1b9 |
| B2e | Move docs/results/ -> docs/France_case/results/ | 9bb62de |
| B2f | Move France atom files -> docs/France_case/ | ad6d6bc |
| B2g | Move execution logs: NC_pilot (22 files) | 1499498 |
| B2h | Move execution logs: Bpool (4 files) | 25339ef |
| B2i | Move execution logs: occ_M0a/b/c (9 files) | 33bc298 |
| B2j | Move execution logs: occ_M1 (10 files) | 232300d |
| B2k | Move execution logs: pooled_P3a (15 files) | 04f2e0c |
| B2l | Move execution logs: stage_M1 (13 files) | 379e7a3 |
| B2m | Move execution logs: GSURv2 (16 files) + JMP_next_cycle plan | c03dbb1 |
| C | Archive 5 superseded versions with supersession notes | e24c1ec |
| D1 | Consolidate GSUR external acquisition chain (4 sources) | c088fcb |
| D2 | Consolidate GSUR rebuild chain (6 sources) | 1442878 |
| D3 | Consolidate multi-year 2015/2017 chain (3 sources) | 048f365 |
| E | Remove empty France_case/mirrored/ skeleton (no-op: was untracked) | — |
| F | Rewrite mirror index, fill manifest, fix cross-refs | 4e2cfa5 |

## Summary counts
- Moved to topical package subfolders (B1a–B1g): 5 + 6 + 4 + 10 + 5 + 8 + 1 = 39 files
- Moved to docs/France_case/ (B2a–B2m): 9 + 2 + 1 + 3 + 1 + 21 + 22 + 4 + 9 + 10 + 15 + 13 + 17 = 127 files
- Archived as superseded (C): 5 files
- Merged then archived (D1–D3): 4 + 6 + 3 = 13 files (into 3 consolidated docs)
- Mirror index rows updated: 14 (all France-related)
- Cross-reference fixes applied (F): ~98 files patched by automated path-mapping script

## A. Topical package relocations (B1)
| Old path (under docs/) | New path | Subfolder | Commit SHA |
|---|---|---|---|
| RURO_NAMING_AND_PACKAGE_SCOPE_v1.md | docs/package/RURO_NAMING_AND_PACKAGE_SCOPE_v1.md | package | cc6ae27 |
| RURO_PACKAGE_PORTABILITY_AND_CLEANUP_POLICY_v1.md | docs/package/... | package | cc6ae27 |
| RURO_PROJECT_HYGIENE_CLEANUP_RECOMMENDATIONS.md | docs/package/... | package | cc6ae27 |
| RURO_PROJECT_MEMORY_MAP.md | docs/package/... | package | cc6ae27 |
| RURO_RETURN_GUIDE_DATA_RESULTS_AND_CLEANUP.md | docs/package/... | package | cc6ae27 |
| RURO_PREFERENCE_ESTIMATION_CAPABILITIES.md | docs/methods/... | methods | 9508336 |
| RURO_METHODS_AND_PIPELINE_MANUAL_v1.md | docs/methods/... | methods | 9508336 |
| RURO_CURRENT_STATE_AND_IDENTIFICATION.md | docs/methods/... | methods | 9508336 |
| RURO_JOB_MODEL_GMM_METHOD_NOTE.md | docs/methods/... | methods | 9508336 |
| RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md | docs/methods/... | methods | 9508336 |
| RURO_R_REFERENCE_COMPARISON_AND_ACTION_PLAN.md | docs/methods/... | methods | 9508336 |
| RURO_R_REFERENCE_COMPARISON_SECTOR_OPPORTUNITY_PLAN.md | docs/methods/... | methods | d463cfa |
| RURO_model_spec_contract_v4_ruro_occ.md | docs/specifications/... | specifications | 510ea09 |
| RURO_SPECIFICATIONS_LAYOUT_v1.md | docs/specifications/... | specifications | 510ea09 |
| RURO_CONTINUOUS_MNL_VARIABLE_DICTIONARY_v1.md | docs/specifications/... | specifications | 510ea09 |
| RURO_occ_pipeline_audit_v1.md | docs/specifications/... | specifications | 510ea09 |
| GAMSPy_Integration_Roadmap.md | docs/estimation/... | estimation | 4b0abae |
| GAMSPy_Quick_Start.md | docs/estimation/... | estimation | 4b0abae |
| GAMSPy_vs_SciPy_Architecture_Comparison.md | docs/estimation/... | estimation | 4b0abae |
| RURO_ENHANCED_PIPELINE_COMMANDS.md | docs/estimation/... | estimation | 4b0abae |
| RURO_GSUR_DATA_AND_MERGE_NOTE.md | docs/estimation/... | estimation | 4b0abae |
| RURO_ACTIVE_RESULTS_REGISTRY.md | docs/estimation/... | estimation | 4b0abae |
| RURO_cluster_robust_SE_design_audit_v1.md | docs/estimation/... | estimation | 4b0abae |
| RURO_cluster_robust_SE_implementation_report_v1.md | docs/estimation/... | estimation | 4b0abae |
| RURO_cluster_robust_SE_implementation_correction_v1.md | docs/estimation/... | estimation | 4b0abae |
| RURO_gamspy_solver_artifact_capture_v1.md | docs/estimation/... | estimation | 4b0abae |
| RURO_post_estimation_dynamic_reporting_design_v1.md | docs/reporting/... | reporting | 2539abd |
| RURO_post_estimation_dynamic_reporting_phase2_report_v1.md | docs/reporting/... | reporting | 2539abd |
| RURO_post_estimation_dynamic_reporting_phase2_1_report_v1.md | docs/reporting/... | reporting | 2539abd |
| RURO_post_estimation_styled_general_reporting_enhancement_v1.md | docs/reporting/... | reporting | 2539abd |
| RURO_low_token_post_estimation_summary_v1.md | docs/reporting/... | reporting | 2539abd |
| JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md | docs/jmp_methodology/... | jmp_methodology | c97598c |
| JMP_welfare_scaffolding_design_memo_v2.md | docs/jmp_methodology/... | jmp_methodology | c97598c |
| JMP_welfare_measurement_decisions_memo_v2.md | docs/jmp_methodology/... | jmp_methodology | c97598c |
| JMP_estimator_architecture_decision_v1.md | docs/jmp_methodology/... | jmp_methodology | c97598c |
| JMP_couples_opportunity_draw_design_note_v1.md | docs/jmp_methodology/... | jmp_methodology | c97598c |
| JMP_conditional_wage_on_occupation_decision_note_v1.md | docs/jmp_methodology/... | jmp_methodology | c97598c |
| JMP_docs_results_cleanup_plan_v1.md | docs/jmp_methodology/... | jmp_methodology | c97598c |
| JMP_docs_results_cleanup_second_pass_plan_v1.md | docs/jmp_methodology/... | jmp_methodology | c97598c |

Note: a planned file `RURO_R_REFERENCE_SECTOR_OPPORTUNITY_PLAN.md` did not exist in the working tree — the actual file is the single `RURO_R_REFERENCE_COMPARISON_SECTOR_OPPORTUNITY_PLAN.md` (B1g).

## B. France relocations (B2)
| Old path (under docs/) | New path | Bucket | Commit SHA |
|---|---|---|---|
| euromod_reference/ (9 files) | docs/France_case/euromod_reference/ | subdir | a3c8469 |
| notes/ (2 files) | docs/France_case/notes/ | subdir | 97061b7 |
| canary_reports/ (1 file) | docs/France_case/canary_reports/ | subdir | 758aa0b |
| job_choice/ (3 files) | docs/France_case/job_choice/ | subdir | addb1b9 |
| results/ (1 file) | docs/France_case/results/ | subdir | 9bb62de |
| 21 France atom files (FR2016_*, RURO_FR2016_*, RURO_data_audit_v1*, JMP_GSUR_year_alignment, RURO_GSUR_local_O1, RURO_GSUR_SOURCE_AND_MERGE_AUDIT, RURO_GSUR_rebuild_specification_v2_1, RURO_sample_funnel, RURO_prep_mnl_gsur_year_support, RURO_EXTERNAL_STORAGE_HYGIENE_AUDIT_2026-05-12, RURO_PROJECT_HYGIENE_CLEANUP_LOG_2026-05-11, RURO_WORKSPACE_AUDIT_2026-05-11, RURO_ruro_occ_M0_file_sync_check, RURO_ruro_occ_M0_rebuild_command_plan, RURO_ruro_occ_baseline_spec, RURO_ruro_occ_baseline_implementation_report, RURO_ruro_occ_post_estimation_report_fix, RURO_spec_redesign_decisions_v2, RURO_pilot_gsurv2_verification, JMP_multi_year_CPI_HICP_source_decision) | docs/France_case/ | root | ad6d6bc |
| JMP_NC_pilot_* (22 files) | docs/France_case/execution_logs/NC_pilot/ | NC_pilot | 1499498 |
| RURO_Bpool_* (4 files) | docs/France_case/execution_logs/Bpool/ | Bpool | 25339ef |
| RURO_occ_M0a/b/c_* (9 files) | docs/France_case/execution_logs/occ_M0a,b,c/ | occ_M0 | 33bc298 |
| RURO_occ_M1_* + RURO_post_estimation_M1_* + RURO_occ_P3a_GA17 + RURO_ruro_occ_M0_estimation_run (10 files) | docs/France_case/execution_logs/occ_M1/ | occ_M1 | 232300d |
| JMP_pooled_P3a_* (15 files) | docs/France_case/execution_logs/pooled_P3a/ | pooled_P3a | 04f2e0c |
| JMP_multi_year_stage_M1_* + JMP_stage_M1_* + JMP_multi_year_sample_construction_descriptives + JMP_stage_M1_V9_validation_patch_note (13 files) | docs/France_case/execution_logs/stage_M1/ | stage_M1 | 379e7a3 |
| JMP_GSURv2_* (16 files) + JMP_next_cycle_opportunity_respecification_plan | docs/France_case/execution_logs/GSURv2/ + docs/France_case/execution_logs/ | GSURv2 | c03dbb1 |

## B'. JMP per-file classification
| File | Destination | Reason |
|---|---|---|
| JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md | docs/jmp_methodology/ | methodology, not tied to FR years/data/EUROMOD |
| JMP_welfare_scaffolding_design_memo_v2.md | docs/jmp_methodology/ | welfare methodology, country-agnostic |
| JMP_welfare_measurement_decisions_memo_v2.md | docs/jmp_methodology/ | welfare methodology, country-agnostic |
| JMP_estimator_architecture_decision_v1.md | docs/jmp_methodology/ | estimator architecture, country-agnostic |
| JMP_couples_opportunity_draw_design_note_v1.md | docs/jmp_methodology/ | methodology design |
| JMP_conditional_wage_on_occupation_decision_note_v1.md | docs/jmp_methodology/ | methodology design |
| JMP_docs_results_cleanup_plan_v1.md | docs/jmp_methodology/ | repo-hygiene methodology |
| JMP_docs_results_cleanup_second_pass_plan_v1.md | docs/jmp_methodology/ | repo-hygiene methodology |
| JMP_multi_year_CPI_HICP_source_decision_v1.md | docs/France_case/ | FR-specific CPI/HICP series decision |
| JMP_GSUR_year_alignment_decision_v1.md | docs/France_case/ | FR GSUR year alignment |
| All JMP_NC_pilot_*, JMP_pooled_P3a_*, JMP_multi_year_stage_M1_*, JMP_stage_M1_*, JMP_GSURv2_* | docs/France_case/execution_logs/<bucket>/ | dated execution logs on FR data |
| JMP_single_year_replication_2015_2017_authorization/command_plan/addendum (3 files) | merged → JMP_multi_year_2015_2017_consolidated_v1.md, sources archived | 2015/2017 FR replication |
| JMP_next_cycle_opportunity_respecification_plan_v1.md | docs/France_case/execution_logs/ | FR run planning |

Result: docs/France_case/jmp/ is currently empty (kept as scaffold for future France-tied JMP memos that are not execution logs).

## C. Superseded versions archived
| Old path (under docs/) | Archive path | Superseded by | Commit SHA |
|---|---|---|---|
| JMP_multi_year_and_cross_validation_strategy_memo_v3.md | docs/archive/2026-05-25_docs_supersession/superseded_versions/ | docs/jmp_methodology/JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md | e24c1ec |
| RURO_model_spec_contract_v1.md | docs/archive/2026-05-25_docs_supersession/superseded_versions/ | docs/specifications/RURO_model_spec_contract_v4_ruro_occ.md | e24c1ec |
| RURO_model_spec_contract_v2_continuous_enhanced.md | (same) | (same v4) | e24c1ec |
| RURO_model_spec_contract_v3_ruro_occ.md | (same) | (same v4) | e24c1ec |
| RURO_spec_redesign_decisions_v1.md | (same) | docs/France_case/RURO_spec_redesign_decisions_v2.md | e24c1ec |

Each archived file has a top-of-file blockquote linking to its superseder.

## D. Merged source archives
| Consolidated doc | Source archived | Archive path | Commit SHA |
|---|---|---|---|
| docs/France_case/consolidated/RURO_GSUR_external_acquisition_consolidated_v1.md | RURO_GSUR_external_acquisition_decision_v2.md | docs/archive/2026-05-25_docs_supersession/merged_sources/gsur_external_acquisition/ | c088fcb |
| (same) | RURO_GSUR_external_acquisition_report_v1.md | (same) | c088fcb |
| (same) | RURO_GSUR_external_acquisition_verification_claude_v1.md | (same) | c088fcb |
| (same) | RURO_GSUR_external_acquisition_completion_v1.md | (same) | c088fcb |
| docs/France_case/consolidated/RURO_GSUR_rebuild_consolidated_v1.md | RURO_GSUR_StageA_authorization_v1.md | docs/archive/2026-05-25_docs_supersession/merged_sources/gsur_rebuild/ | 1442878 |
| (same) | RURO_GSUR_v2_stageA_implementation_report_v1.md | (same) | 1442878 |
| (same) | RURO_GSUR_O2_denominator_resolution_v1.md | (same) | 1442878 |
| (same) | RURO_GSUR_O7_crosswalk_signoff_request_v1.md | (same) | 1442878 |
| (same) | RURO_GSUR_O7_crosswalk_signoff_v1.md | (same) | 1442878 |
| (same) | RURO_GSUR_v2_1_open_decisions_resolution_v1.md | (same) | 1442878 |
| docs/France_case/consolidated/JMP_multi_year_2015_2017_consolidated_v1.md | JMP_single_year_replication_2015_2017_authorization_v1.md | docs/archive/2026-05-25_docs_supersession/merged_sources/multi_year_2015_2017_command/ | 048f365 |
| (same) | JMP_single_year_replication_2015_2017_command_plan_v2.md | (same) | 048f365 |
| (same) | JMP_single_year_replication_2015_2017_command_plan_addendum_v1.md | (same) | 048f365 |

The v2.1 governing spec (RURO_GSUR_rebuild_specification_v2_1.md) is kept standalone in docs/France_case/, NOT merged.

## E. Mirror index updates
| Original (outside docs/) | Old mirror | New mirror |
|---|---|---|
| Data/documentation/euromod_fr_2015_2017_input_output_reference.md | docs/euromod_reference/ | docs/France_case/euromod_reference/ |
| Data/documentation/euromod_fr_2015_2017_input_variables.csv | docs/euromod_reference/ | docs/France_case/euromod_reference/ |
| Data/documentation/euromod_fr_2015_2017_output_variable_index.csv | docs/euromod_reference/ | docs/France_case/euromod_reference/ |
| Data/documentation/euromod_fr_2015_2017_standard_income_concepts.csv | docs/euromod_reference/ | docs/France_case/euromod_reference/ |
| Data/documentation/FR_2015_index.md | docs/euromod_reference/ | docs/France_case/euromod_reference/ |
| Data/documentation/FR_2015_all_tables_compact.md | docs/euromod_reference/ | docs/France_case/euromod_reference/ |
| Data/documentation/FR_2015_index.jsonl | docs/euromod_reference/ | docs/France_case/euromod_reference/ |
| Data/documentation/DRD_FR_2016_a3_export.txt | docs/euromod_reference/ | docs/France_case/euromod_reference/ |
| Data/documentation/DRD_FR_2016_index.jsonl | docs/euromod_reference/ | docs/France_case/euromod_reference/ |
| Results/P3a/single_year_baseline/M0/RURO_ruro_occ_M0_rebuild_canary_report_v1.md | docs/canary_reports/ | docs/France_case/canary_reports/ |
| scripts/Job_model/README_job_model.md | docs/job_choice/ | docs/France_case/job_choice/ |
| scripts/Job_model/ACCEPTANCE_TESTS.md | docs/job_choice/ | docs/France_case/job_choice/ |
| scripts/Job_model/Commands_job.txt | docs/job_choice/ | docs/France_case/job_choice/ |
| outputs/KEEP_RESULTS.md | docs/results/ | docs/France_case/results/ |
| notes/EUROMO_sys_france_2015.md | docs/notes/ | docs/France_case/notes/ |
| notes/R_REFERENCE_vs_PYTHON_SPECIFICATION.md | docs/notes/ | docs/France_case/notes/ |

## F. Cross-reference fixes
Applied via automated path-mapping replacement script across:
- repo root README.md
- docs/MIRRORED_DOCUMENTS_INDEX.md, docs/PIPELINE_ENTRYPOINTS.md, docs/mirrored/root/README.md
- all non-archive docs/**/*.md (98 files in total patched)
- scripts/enhanced/README.md, scripts/enhanced/*.py, scripts/enhanced/specifications/*.yaml, scripts/bpool/specs/*.yaml, scripts/pilot/*.py
- Results/*.md (non-archive)
- outputs/KEEP_RESULTS.md

Specific scripts/code files patched (paths were string-literal references to old docs/ paths):
- scripts/enhanced/cluster_robust_se.py
- scripts/enhanced/enh_prepare_FR_gsur_v2.py
- scripts/enhanced/enh_RURO_explore_predrop.py
- scripts/enhanced/enh_RURO_mnl_rebuild_GSURv2_stageA.py
- scripts/pilot/_run_ll_equivalence_prototype.py
- scripts/bpool/specs/estimation_spec_bpool_p3a_v1.yaml
- scripts/enhanced/specifications/estimation_spec_ruro_occ_M0.yaml
- scripts/enhanced/specifications/estimation_spec_ruro_occ_M0a.yaml

These were string-substituted, not behavior-changed. Verify before next code run.

## G. Deferred follow-ups
- Authorial pass: rewrite the three consolidated docs as single coherent narratives (current Phase D delivers structural merges with pointers, not synthesized prose).
- Rename `_v1` / `_v2` suffixes off general docs once stable.
- `Results/` reorganization — separate pass.
- `scripts/` reorganization and RUM/RURO package vs France-adapter code split.
- Audit any remaining hard-coded paths inside script code that weren't matched by the F-phase script.
- France_case/jmp/ scaffolded but empty; populate as France-tied JMP memos appear.

## H. Verification log
Ran at Gate F (this commit). See the plan file's "Verification" section for the 9 PowerShell checks.

- check 1 (top-level docs root file count, expect ~5): PASS — 5 chrome files (README, ROADMAP, PIPELINE_ENTRYPOINTS, MIRRORED_DOCUMENTS_INDEX, ACKNOWLEDGEMENTS).
- check 2 (no France filenames at root): PASS.
- check 3 (topical subdirs populated): PASS.
- check 4 (France_case populated): PASS.
- check 5 (archive supersession subdir populated): PASS (5 superseded + 13 merged sources).
- check 6 (git history preserved for moved files via --follow): PASS (verified on FR2016_RURO_pipeline_report.md and GAMSPy_Quick_Start.md).
- check 7 (mirror index has no stale paths): PASS.
- check 8 (no France hard paths outside France_case/ or archive/): see Gate F verification.
- check 9 (no inbound references to old top-level paths from non-archive locations): see Gate F verification.
