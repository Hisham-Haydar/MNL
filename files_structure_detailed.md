# Git-Visible Repository File Structure

Generated: 2026-06-13 15:37:19 +02:00

Git root: C:\Users\hisham\Repo\MNL

Scope: tracked files plus untracked files not ignored by Git. Every dot-prefixed directory and conventional environment/dependency directory is excluded even if Git-visible. Dot-prefixed files outside excluded directories remain included.

The report file files_structure_detailed.md is excluded from its own inventory. Gitlinks/submodules are listed but not traversed.

## Summary

- Directories represented: 154
- Regular files: 1.213
- Gitlinks/submodules: 1
- Tracked entries: 1.214
- Untracked, non-ignored entries: 0
- Missing tracked files: 0
- Total regular-file size: 122,54 MB (128.495.709 bytes)
- Text files with counted lines: 1.079
- Total text lines: 890.807
- Binary files with line count marked N/A: 134

## Tree

```text
[DIR] MNL/
|-- [DIR] config/
|   |-- [DIR] multi_year/
|   |   |-- [FILE] fr_p2_stage_m1.yaml | git: tracked | mode: 100644 | size: 4,83 KB (4.944 B) | type: .yaml | lines: 155
|   |   |-- [FILE] fr_p3a_gsurv2_stage_m1.yaml | git: tracked | mode: 100644 | size: 5,82 KB (5.956 B) | type: .yaml | lines: 171
|   |   |-- [FILE] fr_p3a_stage_m1.yaml | git: tracked | mode: 100644 | size: 6,81 KB (6.977 B) | type: .yaml | lines: 182
|   |   |-- [FILE] fr_p3b_stage_m1.yaml | git: tracked | mode: 100644 | size: 5,22 KB (5.345 B) | type: .yaml | lines: 163
|   |   \-- [FILE] fr_p4_stage_m1.yaml | git: tracked | mode: 100644 | size: 4,96 KB (5.074 B) | type: .yaml | lines: 159
|   \-- [FILE] config_files_structure.md | git: tracked | mode: 100644 | size: 560 B (560 B) | type: .md | lines: N/A (binary)
|-- [DIR] configs/
|   \-- [FILE] default.yaml | git: tracked | mode: 100644 | size: 425 B (425 B) | type: .yaml | lines: 18
|-- [DIR] Data/
|   |-- [DIR] documentation/
|   |   |-- [FILE] DRD_FR_2016_a3_export.txt | git: tracked | mode: 100644 | size: 37,70 KB (38.605 B) | type: .txt | lines: 581
|   |   |-- [FILE] DRD_FR_2016_index.jsonl | git: tracked | mode: 100644 | size: 29,88 KB (30.592 B) | type: .jsonl | lines: 131
|   |   |-- [FILE] euromod_fr_2015_2017_input_output_reference.md | git: tracked | mode: 100644 | size: 20,07 KB (20.552 B) | type: .md | lines: 200
|   |   |-- [FILE] euromod_fr_2015_2017_input_variables.csv | git: tracked | mode: 100644 | size: 69,99 KB (71.674 B) | type: .csv | lines: 282
|   |   |-- [FILE] euromod_fr_2015_2017_output_variable_index.csv | git: tracked | mode: 100644 | size: 14,78 KB (15.135 B) | type: .csv | lines: 133
|   |   |-- [FILE] euromod_fr_2015_2017_standard_income_concepts.csv | git: tracked | mode: 100644 | size: 79,40 KB (81.310 B) | type: .csv | lines: 715
|   |   |-- [FILE] FR_2015_all_tables_compact.md | git: tracked | mode: 100644 | size: 111,54 KB (114.215 B) | type: .md | lines: 4.314
|   |   |-- [FILE] FR_2015_index.jsonl | git: tracked | mode: 100644 | size: 67,26 KB (68.878 B) | type: .jsonl | lines: 510
|   |   \-- [FILE] FR_2015_index.md | git: tracked | mode: 100644 | size: 59,60 KB (61.035 B) | type: .md | lines: 2.561
|   |-- [DIR] external/
|   |   |-- [FILE] cpi.xlsx | git: tracked | mode: 100644 | size: 11,56 KB (11.833 B) | type: .xlsx | lines: N/A (binary)
|   |   |-- [FILE] cpi_hicp_fr_harmonisation.csv | git: tracked | mode: 100644 | size: 893 B (893 B) | type: .csv | lines: 5
|   |   |-- [FILE] cpi_hicp_fr_harmonisation_TEMPLATE.csv | git: tracked | mode: 100644 | size: 481 B (481 B) | type: .csv | lines: 5
|   |   |-- [FILE] fr_drgn1_to_nuts2_crosswalk.csv | git: tracked | mode: 100644 | size: 768 B (768 B) | type: .csv | lines: 23
|   |   |-- [FILE] FR_gsur.xlsx | git: tracked | mode: 100644 | size: 1,03 MB (1.077.164 B) | type: .xlsx | lines: N/A (binary)
|   |   |-- [FILE] FR_gsur_full.csv | git: tracked | mode: 100644 | size: 4,61 MB (4.837.605 B) | type: .csv | lines: 90.721
|   |   |-- [FILE] FR_gsur_full.parquet | git: tracked | mode: 100644 | size: 98,63 KB (100.997 B) | type: .parquet | lines: N/A (binary)
|   |   |-- [FILE] FR_gsur_ruro.csv | git: tracked | mode: 100644 | size: 142,38 KB (145.799 B) | type: .csv | lines: 2.161
|   |   |-- [FILE] FR_gsur_ruro.parquet | git: tracked | mode: 100644 | size: 11,41 KB (11.688 B) | type: .parquet | lines: N/A (binary)
|   |   |-- [FILE] FR_gsur_ruro_v2_stageA.parquet | git: tracked | mode: 100644 | size: 7,27 KB (7.444 B) | type: .parquet | lines: N/A (binary)
|   |   |-- [FILE] FR_gsur_ruro_v2_stageA_y2014.parquet | git: tracked | mode: 100644 | size: 7,27 KB (7.441 B) | type: .parquet | lines: N/A (binary)
|   |   |-- [FILE] FR_gsur_ruro_v2_stageA_y2014__sidecar.json | git: tracked | mode: 100644 | size: 659 B (659 B) | type: .json | lines: 16
|   |   |-- [FILE] FR_gsur_ruro_v2_stageA_y2015.parquet | git: tracked | mode: 100644 | size: 7,26 KB (7.433 B) | type: .parquet | lines: N/A (binary)
|   |   |-- [FILE] FR_gsur_ruro_v2_stageA_y2015__sidecar.json | git: tracked | mode: 100644 | size: 662 B (662 B) | type: .json | lines: 16
|   |   |-- [FILE] FR_gsur_ruro_v2_stageA_y2016.parquet | git: tracked | mode: 100644 | size: 7,27 KB (7.444 B) | type: .parquet | lines: N/A (binary)
|   |   |-- [FILE] FR_gsur_ruro_v2_stageA_y2016__sidecar.json | git: tracked | mode: 100644 | size: 661 B (661 B) | type: .json | lines: 16
|   |   |-- [FILE] FR_gsur_simple.parquet | git: tracked | mode: 100644 | size: 17,95 KB (18.382 B) | type: .parquet | lines: N/A (binary)
|   |   |-- [FILE] gsur_crosswalk_source.txt | git: tracked | mode: 100644 | size: 2,00 KB (2.051 B) | type: .txt | lines: 39
|   |   |-- [FILE] insee_001688526_2016.csv | git: tracked | mode: 100644 | size: 477 B (477 B) | type: .csv | lines: 6
|   |   |-- [FILE] lfst_r_lfp2acedu_2014_full.csv | git: tracked | mode: 100644 | size: 1,67 MB (1.748.855 B) | type: .csv | lines: 19.484
|   |   |-- [FILE] lfst_r_lfp2acedu_2015_full.csv | git: tracked | mode: 100644 | size: 1,65 MB (1.730.363 B) | type: .csv | lines: 19.427
|   |   |-- [FILE] lfst_r_lfp2acedu_2016_full.csv | git: tracked | mode: 100644 | size: 1,65 MB (1.732.181 B) | type: .csv | lines: 19.445
|   |   |-- [FILE] lfst_r_lfp2acedu_FR_2016.tsv | git: tracked | mode: 100644 | size: 85,99 KB (88.055 B) | type: .tsv | lines: 987
|   |   |-- [FILE] lfst_r_lfsd2pop_2014_full.csv | git: tracked | mode: 100644 | size: 6,93 MB (7.266.302 B) | type: .csv | lines: 82.159
|   |   |-- [FILE] lfst_r_lfsd2pop_2015_full.csv | git: tracked | mode: 100644 | size: 6,87 MB (7.206.128 B) | type: .csv | lines: 82.141
|   |   |-- [FILE] lfst_r_lfsd2pop_2016_full.csv | git: tracked | mode: 100644 | size: 6,88 MB (7.214.941 B) | type: .csv | lines: 82.189
|   |   |-- [FILE] lfst_r_lfsd2pop_FR_2016.tsv | git: tracked | mode: 100644 | size: 348,71 KB (357.080 B) | type: .tsv | lines: 4.058
|   |   |-- [FILE] NUTS2013-NUTS2016.xlsx | git: tracked | mode: 100644 | size: 365,18 KB (373.947 B) | type: .xlsx | lines: N/A (binary)
|   |   \-- [FILE] smic.xlsx | git: tracked | mode: 100644 | size: 10,37 KB (10.622 B) | type: .xlsx | lines: N/A (binary)
|   |-- [FILE] data_files_structure.md | git: tracked | mode: 100644 | size: 3,18 KB (3.252 B) | type: .md | lines: N/A (binary)
|   \-- [FILE] README.md | git: tracked | mode: 100644 | size: 276 B (276 B) | type: .md | lines: 7
|-- [DIR] docs/
|   |-- [DIR] archive/
|   |   |-- [DIR] 2026-05-20_post_gsurv2_mnl_rebuild/
|   |   |   |-- [FILE] JMP_GSURv2_multi_year_extension_construction_authorization_correction_v1.md | git: tracked | mode: 100644 | size: 9,65 KB (9.879 B) | type: .md | lines: 205
|   |   |   |-- [FILE] JMP_GSURv2_multi_year_extension_remediation_authorization_correction_v1.md | git: tracked | mode: 100644 | size: 15,92 KB (16.307 B) | type: .md | lines: 293
|   |   |   |-- [FILE] JMP_GSURv2_multi_year_extension_remediation_authorization_final_wording_fix_v1.md | git: tracked | mode: 100644 | size: 9,96 KB (10.204 B) | type: .md | lines: 208
|   |   |   |-- [FILE] JMP_GSURv2_script_remediation_documentation_fix_v1.md | git: tracked | mode: 100644 | size: 4,91 KB (5.026 B) | type: .md | lines: 107
|   |   |   |-- [FILE] JMP_GSURv2_y2016_provenance_lock_plan_correction_v1.md | git: tracked | mode: 100644 | size: 8,54 KB (8.745 B) | type: .md | lines: 168
|   |   |   |-- [FILE] JMP_multi_year_and_cross_validation_strategy_memo_v1.md | git: tracked | mode: 100644 | size: 36,96 KB (37.842 B) | type: .md | lines: 748
|   |   |   |-- [FILE] JMP_multi_year_and_cross_validation_strategy_memo_v2.md | git: tracked | mode: 100644 | size: 58,64 KB (60.046 B) | type: .md | lines: 1.225
|   |   |   |-- [FILE] JMP_multi_year_sample_construction_descriptives_correction_report_v1.md | git: tracked | mode: 100644 | size: 10,49 KB (10.746 B) | type: .md | lines: 163
|   |   |   |-- [FILE] JMP_multi_year_stage_M1_execution_readiness_report_v1.md | git: tracked | mode: 100644 | size: 18,51 KB (18.951 B) | type: .md | lines: 375
|   |   |   |-- [FILE] JMP_multi_year_stage_M1_implementation_plan_v1.md | git: tracked | mode: 100644 | size: 35,25 KB (36.099 B) | type: .md | lines: 616
|   |   |   |-- [FILE] JMP_single_year_replication_2015_2017_command_plan_v1.md | git: tracked | mode: 100644 | size: 32,30 KB (33.079 B) | type: .md | lines: 660
|   |   |   |-- [FILE] JMP_welfare_measurement_decisions_memo_v1.md | git: tracked | mode: 100644 | size: 65,53 KB (67.104 B) | type: .md | lines: 1.329
|   |   |   |-- [FILE] JMP_welfare_scaffolding_design_memo_v1.md | git: tracked | mode: 100644 | size: 75,21 KB (77.010 B) | type: .md | lines: 1.690
|   |   |   |-- [FILE] RURO_GSUR_external_acquisition_decision_v1.md | git: tracked | mode: 100644 | size: 37,36 KB (38.255 B) | type: .md | lines: 866
|   |   |   |-- [FILE] RURO_GSUR_rebuild_specification_v1.md | git: tracked | mode: 100644 | size: 18,90 KB (19.354 B) | type: .md | lines: 439
|   |   |   |-- [FILE] RURO_GSUR_rebuild_specification_v2.md | git: tracked | mode: 100644 | size: 36,93 KB (37.820 B) | type: .md | lines: 878
|   |   |   \-- [FILE] RURO_occ_M1_clean_design_memo_v1.md | git: tracked | mode: 100644 | size: 50,88 KB (52.097 B) | type: .md | lines: 1.099
|   |   |-- [DIR] 2026-05-25_docs_supersession/
|   |   |   |-- [DIR] merged_sources/
|   |   |   |   |-- [DIR] gsur_external_acquisition/
|   |   |   |   |   |-- [FILE] RURO_GSUR_external_acquisition_completion_v1.md | git: tracked | mode: 100644 | size: 15,97 KB (16.351 B) | type: .md | lines: 399
|   |   |   |   |   |-- [FILE] RURO_GSUR_external_acquisition_decision_v2.md | git: tracked | mode: 100644 | size: 40,09 KB (41.056 B) | type: .md | lines: 899
|   |   |   |   |   |-- [FILE] RURO_GSUR_external_acquisition_report_v1.md | git: tracked | mode: 100644 | size: 22,76 KB (23.302 B) | type: .md | lines: 149
|   |   |   |   |   \-- [FILE] RURO_GSUR_external_acquisition_verification_claude_v1.md | git: tracked | mode: 100644 | size: 23,21 KB (23.762 B) | type: .md | lines: 149
|   |   |   |   |-- [DIR] gsur_rebuild/
|   |   |   |   |   |-- [FILE] RURO_GSUR_O2_denominator_resolution_v1.md | git: tracked | mode: 100644 | size: 11,56 KB (11.833 B) | type: .md | lines: 274
|   |   |   |   |   |-- [FILE] RURO_GSUR_O7_crosswalk_signoff_request_v1.md | git: tracked | mode: 100644 | size: 13,06 KB (13.369 B) | type: .md | lines: 330
|   |   |   |   |   |-- [FILE] RURO_GSUR_O7_crosswalk_signoff_v1.md | git: tracked | mode: 100644 | size: 795 B (795 B) | type: .md | lines: 22
|   |   |   |   |   |-- [FILE] RURO_GSUR_StageA_authorization_v1.md | git: tracked | mode: 100644 | size: 10,89 KB (11.151 B) | type: .md | lines: 228
|   |   |   |   |   |-- [FILE] RURO_GSUR_v2_1_open_decisions_resolution_v1.md | git: tracked | mode: 100644 | size: 14,58 KB (14.931 B) | type: .md | lines: 363
|   |   |   |   |   \-- [FILE] RURO_GSUR_v2_stageA_implementation_report_v1.md | git: tracked | mode: 100644 | size: 13,30 KB (13.624 B) | type: .md | lines: 312
|   |   |   |   \-- [DIR] multi_year_2015_2017_command/
|   |   |   |       |-- [FILE] JMP_single_year_replication_2015_2017_authorization_v1.md | git: tracked | mode: 100644 | size: 14,31 KB (14.655 B) | type: .md | lines: 330
|   |   |   |       |-- [FILE] JMP_single_year_replication_2015_2017_command_plan_addendum_v1.md | git: tracked | mode: 100644 | size: 7,48 KB (7.655 B) | type: .md | lines: 169
|   |   |   |       \-- [FILE] JMP_single_year_replication_2015_2017_command_plan_v2.md | git: tracked | mode: 100644 | size: 32,97 KB (33.763 B) | type: .md | lines: 670
|   |   |   |-- [DIR] superseded_versions/
|   |   |   |   |-- [FILE] JMP_multi_year_and_cross_validation_strategy_memo_v3.md | git: tracked | mode: 100644 | size: 69,16 KB (70.822 B) | type: .md | lines: 1.417
|   |   |   |   |-- [FILE] RURO_model_spec_contract_v1.md | git: tracked | mode: 100644 | size: 27,16 KB (27.807 B) | type: .md | lines: 973
|   |   |   |   |-- [FILE] RURO_model_spec_contract_v2_continuous_enhanced.md | git: tracked | mode: 100644 | size: 32,01 KB (32.774 B) | type: .md | lines: 543
|   |   |   |   |-- [FILE] RURO_model_spec_contract_v3_ruro_occ.md | git: tracked | mode: 100644 | size: 33,92 KB (34.732 B) | type: .md | lines: 1.161
|   |   |   |   \-- [FILE] RURO_spec_redesign_decisions_v1.md | git: tracked | mode: 100644 | size: 13,06 KB (13.378 B) | type: .md | lines: 167
|   |   |   \-- [FILE] README.md | git: tracked | mode: 100644 | size: 1,37 KB (1.403 B) | type: .md | lines: 22
|   |   |-- [DIR] 2026-05-26_round2_chain_compression/
|   |   |   |-- [DIR] audit_reaudit_chain/
|   |   |   |   |-- [FILE] .gitkeep | git: tracked | mode: 100644 | size: 0 B (0 B) | type: .gitkeep | lines: 0
|   |   |   |   |-- [FILE] JMP_GSURv2_multi_year_extension_implementation_audit_addendum_v1.md | git: tracked | mode: 100644 | size: 35,56 KB (36.409 B) | type: .md | lines: 682
|   |   |   |   |-- [FILE] JMP_GSURv2_multi_year_extension_implementation_audit_v1.md | git: tracked | mode: 100644 | size: 29,96 KB (30.679 B) | type: .md | lines: 668
|   |   |   |   \-- [FILE] JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md | git: tracked | mode: 100644 | size: 48,79 KB (49.963 B) | type: .md | lines: 990
|   |   |   |-- [DIR] doc_only_corrections/
|   |   |   |   |-- [FILE] .gitkeep | git: tracked | mode: 100644 | size: 0 B (0 B) | type: .gitkeep | lines: 0
|   |   |   |   |-- [FILE] JMP_GSURv2_MNL_rebuild_authorization_correction_v1.md | git: tracked | mode: 100644 | size: 6,01 KB (6.159 B) | type: .md | lines: 133
|   |   |   |   |-- [FILE] JMP_GSURv2_MNL_rebuild_verdict_correction_v1.md | git: tracked | mode: 100644 | size: 9,75 KB (9.988 B) | type: .md | lines: 140
|   |   |   |   |-- [FILE] JMP_GSURv2_multi_year_extension_construction_verdict_correction_v1.md | git: tracked | mode: 100644 | size: 10,01 KB (10.252 B) | type: .md | lines: 193
|   |   |   |   |-- [FILE] JMP_pooled_P3a_estimation_design_memo_correction_v1.md | git: tracked | mode: 100644 | size: 20,06 KB (20.542 B) | type: .md | lines: 449
|   |   |   |   |-- [FILE] JMP_pooled_P3a_estimation_design_memo_review_addendum_v1.md | git: tracked | mode: 100644 | size: 34,45 KB (35.279 B) | type: .md | lines: 677
|   |   |   |   |-- [FILE] JMP_pooled_P3a_estimation_execution_authorization_correction_v1.md | git: tracked | mode: 100644 | size: 12,18 KB (12.471 B) | type: .md | lines: 197
|   |   |   |   |-- [FILE] JMP_stage_M1_P3a_GSURv2_stacking_authorization_correction_v1.md | git: tracked | mode: 100644 | size: 4,40 KB (4.506 B) | type: .md | lines: 116
|   |   |   |   |-- [FILE] JMP_stage_M1_P3a_GSURv2_stacking_execution_report_correction_v1.md | git: tracked | mode: 100644 | size: 6,57 KB (6.724 B) | type: .md | lines: 174
|   |   |   |   \-- [FILE] JMP_stage_M1_P3a_GSURv2_stacking_execution_report_heading_addendum_v1.md | git: tracked | mode: 100644 | size: 9,33 KB (9.554 B) | type: .md | lines: 220
|   |   |   |-- [DIR] replaced_by_clean_corrected/
|   |   |   |   |-- [FILE] .gitkeep | git: tracked | mode: 100644 | size: 0 B (0 B) | type: .gitkeep | lines: 0
|   |   |   |   |-- [FILE] JMP_pooled_P3a_estimation_execution_authorization_v1.md | git: tracked | mode: 100644 | size: 42,84 KB (43.870 B) | type: .md | lines: 887
|   |   |   |   |-- [FILE] JMP_pooled_P3a_estimation_execution_repair_authorization_v1.md | git: tracked | mode: 100644 | size: 35,17 KB (36.012 B) | type: .md | lines: 692
|   |   |   |   |-- [FILE] JMP_pooled_P3a_estimation_execution_repair_clearance_v1.md | git: tracked | mode: 100644 | size: 20,03 KB (20.514 B) | type: .md | lines: 416
|   |   |   |   |-- [FILE] JMP_pooled_P3a_estimation_execution_repair_report_v1.md | git: tracked | mode: 100644 | size: 19,36 KB (19.826 B) | type: .md | lines: 396
|   |   |   |   |-- [FILE] JMP_pooled_P3a_post_estimation_review_v1.md | git: tracked | mode: 100644 | size: 31,79 KB (32.553 B) | type: .md | lines: 658
|   |   |   |   |-- [FILE] JMP_pooled_P3a_region_dummy_repair_authorization_v1.md | git: tracked | mode: 100644 | size: 30,00 KB (30.723 B) | type: .md | lines: 609
|   |   |   |   |-- [FILE] JMP_pooled_P3a_region_dummy_repair_report_v1.md | git: tracked | mode: 100644 | size: 19,69 KB (20.160 B) | type: .md | lines: 374
|   |   |   |   \-- [FILE] RURO_occ_M0a_implementation_report_v1.md | git: tracked | mode: 100644 | size: 13,69 KB (14.019 B) | type: .md | lines: 332
|   |   |   |-- [DIR] strategy_v1_superseded/
|   |   |   |   |-- [FILE] .gitkeep | git: tracked | mode: 100644 | size: 0 B (0 B) | type: .gitkeep | lines: 0
|   |   |   |   \-- [FILE] JMP_NC_pilot_stage5_euromod_amendment_v1.md | git: tracked | mode: 100644 | size: 23,60 KB (24.162 B) | type: .md | lines: 488
|   |   |   |-- [DIR] workspace_audits_superseded/
|   |   |   |   |-- [FILE] .gitkeep | git: tracked | mode: 100644 | size: 0 B (0 B) | type: .gitkeep | lines: 0
|   |   |   |   |-- [FILE] RURO_EXTERNAL_STORAGE_HYGIENE_AUDIT_2026-05-12.md | git: tracked | mode: 100644 | size: 18,48 KB (18.920 B) | type: .md | lines: 556
|   |   |   |   |-- [FILE] RURO_PROJECT_HYGIENE_CLEANUP_LOG_2026-05-11.md | git: tracked | mode: 100644 | size: 5,06 KB (5.179 B) | type: .md | lines: 108
|   |   |   |   \-- [FILE] RURO_WORKSPACE_AUDIT_2026-05-11.md | git: tracked | mode: 100644 | size: 8,38 KB (8.584 B) | type: .md | lines: 159
|   |   |   \-- [FILE] README.md | git: tracked | mode: 100644 | size: 2,26 KB (2.317 B) | type: .md | lines: 25
|   |   |-- [DIR] commands/
|   |   |   |-- [FILE] commands_20260122_143200.txt | git: tracked | mode: 100644 | size: 729 B (729 B) | type: .txt | lines: 9
|   |   |   \-- [FILE] commands_legacy.txt | git: tracked | mode: 100644 | size: 3,73 KB (3.818 B) | type: .txt | lines: 80
|   |   |-- [DIR] implementation_history/
|   |   |   |-- [FILE] DONE.md | git: tracked | mode: 100644 | size: 12,61 KB (12.915 B) | type: .md | lines: 349
|   |   |   |-- [FILE] IMPLEMENTATION_SUMMARY.md | git: tracked | mode: 100644 | size: 8,59 KB (8.796 B) | type: .md | lines: 268
|   |   |   |-- [FILE] POST_ESTIMATION_IMPROVEMENTS.md | git: tracked | mode: 100644 | size: 24,85 KB (25.446 B) | type: .md | lines: 668
|   |   |   |-- [FILE] README_legacy_2026-05-11.md | git: tracked | mode: 100644 | size: 8,74 KB (8.947 B) | type: .md | lines: 264
|   |   |   \-- [FILE] VECTORIZED_IMPLEMENTATION_STATUS.md | git: tracked | mode: 100644 | size: 9,66 KB (9.891 B) | type: .md | lines: 291
|   |   |-- [DIR] inventories/
|   |   |   \-- [DIR] external_storage_2026-05-12/
|   |   |       |-- [FILE] external_storage_cross_root_differences_2026-05-12.csv | git: tracked | mode: 100644 | size: 9,62 KB (9.850 B) | type: .csv | lines: 51
|   |   |       |-- [FILE] external_storage_full_file_inventory_2026-05-12.csv | git: tracked | mode: 100644 | size: 2,01 MB (2.103.230 B) | type: .csv | lines: 7.982
|   |   |       |-- [FILE] external_storage_key_metadata_summary_2026-05-12.csv | git: tracked | mode: 100644 | size: 2,25 KB (2.301 B) | type: .csv | lines: 9
|   |   |       |-- [FILE] external_storage_report_files_2026-05-12.csv | git: tracked | mode: 100644 | size: 144,07 KB (147.527 B) | type: .csv | lines: 949
|   |   |       |-- [FILE] external_storage_reports_results_inventory_2026-05-12.csv | git: tracked | mode: 100644 | size: 2,01 MB (2.103.230 B) | type: .csv | lines: 7.982
|   |   |       |-- [FILE] external_storage_reports_topfolders_2026-05-12.csv | git: tracked | mode: 100644 | size: 874 B (874 B) | type: .csv | lines: 7
|   |   |       |-- [FILE] external_storage_ruro_directory_inventory_2026-05-12.csv | git: tracked | mode: 100644 | size: 63,12 KB (64.639 B) | type: .csv | lines: 396
|   |   |       |-- [FILE] external_storage_ruro_file_inventory_2026-05-12.csv | git: tracked | mode: 100644 | size: 566,57 KB (580.171 B) | type: .csv | lines: 2.101
|   |   |       |-- [FILE] external_storage_ruro1_topfolders_2026-05-12.csv | git: tracked | mode: 100644 | size: 4,75 KB (4.869 B) | type: .csv | lines: 37
|   |   |       |-- [FILE] external_storage_top_level_inventory_2026-05-12.csv | git: tracked | mode: 100644 | size: 4,52 KB (4.633 B) | type: .csv | lines: 36
|   |   |       |-- [FILE] repo_estimation_results_summary_2026-05-12.csv | git: tracked | mode: 100644 | size: 88,06 KB (90.171 B) | type: .csv | lines: 116
|   |   |       |-- [FILE] repo_estimation_runs_inventory_2026-05-12.csv | git: tracked | mode: 100644 | size: 35,05 KB (35.892 B) | type: .csv | lines: 169
|   |   |       \-- [FILE] repo_outputs_file_inventory_2026-05-12.csv | git: tracked | mode: 100644 | size: 1,61 MB (1.688.177 B) | type: .csv | lines: 3.968
|   |   |-- [DIR] job_choice_notes/
|   |   |   |-- [FILE] JOB_CHOICE_MODEL_DIAGNOSIS.md | git: tracked | mode: 100644 | size: 11,82 KB (12.102 B) | type: .md | lines: 253
|   |   |   |-- [FILE] JOB_CHOICE_PIPELINE.md | git: tracked | mode: 100644 | size: 32,57 KB (33.353 B) | type: .md | lines: 719
|   |   |   \-- [FILE] JOB_CHOICE_PIPELINE_WALKTHROUGH.md | git: tracked | mode: 100644 | size: 11,35 KB (11.621 B) | type: .md | lines: 353
|   |   |-- [DIR] occupation_choice_notes/
|   |   |   |-- [FILE] OCCUPATION_CHOICE_AGNOSTIC_DESIGN.md | git: tracked | mode: 100644 | size: 9,72 KB (9.950 B) | type: .md | lines: 281
|   |   |   |-- [FILE] OCCUPATION_CHOICE_DESIGN.md | git: tracked | mode: 100644 | size: 14,27 KB (14.615 B) | type: .md | lines: 392
|   |   |   |-- [FILE] OCCUPATION_CHOICE_MATHEMATICAL_SPECIFICATION.md | git: tracked | mode: 100644 | size: 20,53 KB (21.021 B) | type: .md | lines: 639
|   |   |   |-- [FILE] OCCUPATION_CHOICE_SUMMARY.md | git: tracked | mode: 100644 | size: 12,32 KB (12.613 B) | type: .md | lines: 238
|   |   |   \-- [FILE] OCCUPATION_VS_EDUCATION_CHOICE.md | git: tracked | mode: 100644 | size: 8,64 KB (8.848 B) | type: .md | lines: 270
|   |   |-- [DIR] scratch_2026-05-11/
|   |   |   |-- [FILE] my_functions.py | git: tracked | mode: 100644 | size: 55,48 KB (56.809 B) | type: .py | lines: 1.554
|   |   |   |-- [FILE] Ruro_estimation_new.Rmd | git: tracked | mode: 100644 | size: 93,39 KB (95.630 B) | type: .rmd | lines: 1.878
|   |   |   \-- [FILE] RURO_post_estimation_OLD_backup_20251208.py | git: tracked | mode: 100644 | size: 263,09 KB (269.400 B) | type: .py | lines: 7.191
|   |   \-- [FILE] README.md | git: tracked | mode: 100644 | size: 445 B (445 B) | type: .md | lines: 13
|   |-- [DIR] estimation/
|   |   |-- [FILE] GAMSPy_Integration_Roadmap.md | git: tracked | mode: 100644 | size: 20,69 KB (21.185 B) | type: .md | lines: 688
|   |   |-- [FILE] GAMSPy_Quick_Start.md | git: tracked | mode: 100644 | size: 8,71 KB (8.920 B) | type: .md | lines: 295
|   |   |-- [FILE] GAMSPy_vs_SciPy_Architecture_Comparison.md | git: tracked | mode: 100644 | size: 39,05 KB (39.990 B) | type: .md | lines: 1.167
|   |   |-- [FILE] RURO_ACTIVE_RESULTS_REGISTRY.md | git: tracked | mode: 100644 | size: 3,23 KB (3.306 B) | type: .md | lines: 120
|   |   |-- [FILE] RURO_cluster_robust_SE_design_audit_v1.md | git: tracked | mode: 100644 | size: 26,51 KB (27.146 B) | type: .md | lines: 612
|   |   |-- [FILE] RURO_cluster_robust_SE_implementation_correction_v1.md | git: tracked | mode: 100644 | size: 7,71 KB (7.892 B) | type: .md | lines: 183
|   |   |-- [FILE] RURO_cluster_robust_SE_implementation_report_v1.md | git: tracked | mode: 100644 | size: 12,21 KB (12.501 B) | type: .md | lines: 320
|   |   |-- [FILE] RURO_ENHANCED_PIPELINE_COMMANDS.md | git: tracked | mode: 100644 | size: 16,09 KB (16.481 B) | type: .md | lines: 439
|   |   |-- [FILE] RURO_gamspy_solver_artifact_capture_v1.md | git: tracked | mode: 100644 | size: 4,55 KB (4.661 B) | type: .md | lines: 131
|   |   \-- [FILE] RURO_GSUR_DATA_AND_MERGE_NOTE.md | git: tracked | mode: 100644 | size: 11,24 KB (11.507 B) | type: .md | lines: 447
|   |-- [DIR] France_case/
|   |   |-- [DIR] _shared/
|   |   |   |-- [DIR] data_audits/
|   |   |   |   |-- [FILE] RURO_data_audit_v1.md | git: tracked | mode: 100644 | size: 52,55 KB (53.815 B) | type: .md | lines: 981
|   |   |   |   |-- [FILE] RURO_data_audit_v1_addendum.md | git: tracked | mode: 100644 | size: 17,55 KB (17.973 B) | type: .md | lines: 384
|   |   |   |   |-- [FILE] RURO_FR2016_CONTINUOUS_DATA_BUILD_AUDIT_v1.md | git: tracked | mode: 100644 | size: 17,50 KB (17.924 B) | type: .md | lines: 404
|   |   |   |   |-- [FILE] RURO_prep_mnl_gsur_year_support_report_v1.md | git: tracked | mode: 100644 | size: 14,65 KB (15.000 B) | type: .md | lines: 336
|   |   |   |   \-- [FILE] RURO_sample_funnel_v1.md | git: tracked | mode: 100644 | size: 12,06 KB (12.354 B) | type: .md | lines: 305
|   |   |   |-- [DIR] euromod_reference/
|   |   |   |   |-- [FILE] DRD_FR_2016_a3_export.txt | git: tracked | mode: 100644 | size: 37,70 KB (38.605 B) | type: .txt | lines: 581
|   |   |   |   |-- [FILE] DRD_FR_2016_index.jsonl | git: tracked | mode: 100644 | size: 29,88 KB (30.592 B) | type: .jsonl | lines: 131
|   |   |   |   |-- [FILE] euromod_fr_2015_2017_input_output_reference.md | git: tracked | mode: 100644 | size: 20,64 KB (21.138 B) | type: .md | lines: 208
|   |   |   |   |-- [FILE] euromod_fr_2015_2017_input_variables.csv | git: tracked | mode: 100644 | size: 69,99 KB (71.674 B) | type: .csv | lines: 282
|   |   |   |   |-- [FILE] euromod_fr_2015_2017_output_variable_index.csv | git: tracked | mode: 100644 | size: 14,78 KB (15.135 B) | type: .csv | lines: 133
|   |   |   |   |-- [FILE] euromod_fr_2015_2017_standard_income_concepts.csv | git: tracked | mode: 100644 | size: 79,40 KB (81.310 B) | type: .csv | lines: 715
|   |   |   |   |-- [FILE] FR_2015_all_tables_compact.md | git: tracked | mode: 100644 | size: 111,54 KB (114.215 B) | type: .md | lines: 4.314
|   |   |   |   |-- [FILE] FR_2015_index.jsonl | git: tracked | mode: 100644 | size: 67,26 KB (68.878 B) | type: .jsonl | lines: 510
|   |   |   |   \-- [FILE] FR_2015_index.md | git: tracked | mode: 100644 | size: 59,60 KB (61.035 B) | type: .md | lines: 2.561
|   |   |   |-- [DIR] governance/
|   |   |   |   |-- [FILE] JMP_ability_opportunity_cut_v1.md | git: tracked | mode: 100644 | size: 19,85 KB (20.326 B) | type: .md | lines: 181
|   |   |   |   |-- [FILE] JMP_GSUR_year_alignment_decision_v1.md | git: tracked | mode: 100644 | size: 5,70 KB (5.837 B) | type: .md | lines: 106
|   |   |   |   |-- [FILE] JMP_joint_estimation_spec_v1.md | git: tracked | mode: 100644 | size: 22,27 KB (22.809 B) | type: .md | lines: 186
|   |   |   |   |-- [FILE] JMP_multi_year_CPI_HICP_source_decision_v1.md | git: tracked | mode: 100644 | size: 4,56 KB (4.674 B) | type: .md | lines: 86
|   |   |   |   \-- [FILE] RURO_spec_redesign_decisions_v2.md | git: tracked | mode: 100644 | size: 11,48 KB (11.758 B) | type: .md | lines: 139
|   |   |   |-- [DIR] gsur/
|   |   |   |   |-- [FILE] RURO_GSUR_external_acquisition_consolidated_v1.md | git: tracked | mode: 100644 | size: 5,05 KB (5.172 B) | type: .md | lines: 56
|   |   |   |   |-- [FILE] RURO_GSUR_local_O1_evidence_audit_v1.md | git: tracked | mode: 100644 | size: 19,50 KB (19.973 B) | type: .md | lines: 447
|   |   |   |   |-- [FILE] RURO_GSUR_rebuild_specification_v2_1.md | git: tracked | mode: 100644 | size: 43,78 KB (44.834 B) | type: .md | lines: 1.030
|   |   |   |   \-- [FILE] RURO_GSUR_SOURCE_AND_MERGE_AUDIT_v1.md | git: tracked | mode: 100644 | size: 30,44 KB (31.174 B) | type: .md | lines: 952
|   |   |   |-- [DIR] notes/
|   |   |   |   |-- [FILE] EUROMO_sys_france_2015.md | git: tracked | mode: 100644 | size: 6,02 KB (6.164 B) | type: .md | lines: 151
|   |   |   |   \-- [FILE] R_REFERENCE_vs_PYTHON_SPECIFICATION.md | git: tracked | mode: 100644 | size: 8,77 KB (8.977 B) | type: .md | lines: 450
|   |   |   |-- [DIR] results/
|   |   |   |   \-- [FILE] KEEP_RESULTS.md | git: tracked | mode: 100644 | size: 320 B (320 B) | type: .md | lines: 10
|   |   |   \-- [FILE] README.md | git: tracked | mode: 100644 | size: 1,69 KB (1.730 B) | type: .md | lines: 28
|   |   |-- [DIR] About_data/
|   |   |   |-- [FILE] feedback_bpool_chosen_row_is_reconstructed.md | git: tracked | mode: 100644 | size: 2,26 KB (2.311 B) | type: .md | lines: 46
|   |   |   |-- [FILE] feedback_bpool_les_vs_yem_flips_are_structural.md | git: tracked | mode: 100644 | size: 1,73 KB (1.769 B) | type: .md | lines: 33
|   |   |   |-- [FILE] feedback_naming_policy_ruro.md | git: tracked | mode: 100644 | size: 2,97 KB (3.043 B) | type: .md | lines: 58
|   |   |   |-- [FILE] MEMORY.md | git: tracked | mode: 100644 | size: 4,65 KB (4.759 B) | type: .md | lines: 63
|   |   |   \-- [FILE] reference_drd_fr_input_variables.md | git: tracked | mode: 100644 | size: 7,56 KB (7.743 B) | type: .md | lines: 159
|   |   |-- [DIR] cleanup/
|   |   |   |-- [FILE] MOVE_MANIFEST_2026-05-25.md | git: tracked | mode: 100644 | size: 17,29 KB (17.710 B) | type: .md | lines: 219
|   |   |   |-- [FILE] MOVE_MANIFEST_2026-05-26_round2.md | git: tracked | mode: 100644 | size: 16,92 KB (17.323 B) | type: .md | lines: 198
|   |   |   \-- [FILE] MOVE_MANIFEST_2026-05-27_round3.md | git: tracked | mode: 100644 | size: 15,31 KB (15.673 B) | type: .md | lines: 219
|   |   |-- [DIR] job_model/
|   |   |   |-- [FILE] ACCEPTANCE_TESTS.md | git: tracked | mode: 100644 | size: 15,09 KB (15.457 B) | type: .md | lines: 419
|   |   |   |-- [FILE] Commands_job.txt | git: tracked | mode: 100644 | size: 3,79 KB (3.885 B) | type: .txt | lines: 85
|   |   |   |-- [FILE] README.md | git: tracked | mode: 100644 | size: 1,59 KB (1.630 B) | type: .md | lines: 23
|   |   |   \-- [FILE] README_job_model.md | git: tracked | mode: 100644 | size: 7,79 KB (7.976 B) | type: .md | lines: 204
|   |   |-- [DIR] NC_pilot/
|   |   |   |-- [DIR] design/
|   |   |   |   |-- [FILE] JMP_NC_pilot_beta_l0_m_specification_review_v1.md | git: tracked | mode: 100644 | size: 14,30 KB (14.641 B) | type: .md | lines: 306
|   |   |   |   |-- [FILE] JMP_NC_pilot_optimizer_multistart_design_memo_v1.md | git: tracked | mode: 100644 | size: 17,67 KB (18.093 B) | type: .md | lines: 380
|   |   |   |   |-- [FILE] JMP_NC_pilot_spec_contract_v1.md | git: tracked | mode: 100644 | size: 31,76 KB (32.524 B) | type: .md | lines: 668
|   |   |   |   \-- [FILE] JMP_NC_pilot_vectorized_estimator_design_contract_v1.md | git: tracked | mode: 100644 | size: 17,37 KB (17.783 B) | type: .md | lines: 378
|   |   |   |-- [DIR] execution_logs/
|   |   |   |   |-- [FILE] JMP_NC_pilot_diagnostic_estimation_authorization_v1.md | git: tracked | mode: 100644 | size: 16,25 KB (16.645 B) | type: .md | lines: 374
|   |   |   |   |-- [FILE] JMP_NC_pilot_diagnostic_estimation_rerun_amendment_v1.md | git: tracked | mode: 100644 | size: 16,91 KB (17.315 B) | type: .md | lines: 348
|   |   |   |   |-- [FILE] JMP_NC_pilot_diagnostic_estimation_verdict_v1.md | git: tracked | mode: 100644 | size: 12,69 KB (12.993 B) | type: .md | lines: 285
|   |   |   |   |-- [FILE] JMP_NC_pilot_draw_joint_precompute_compatibility_authorization_v1.md | git: tracked | mode: 100644 | size: 16,04 KB (16.420 B) | type: .md | lines: 340
|   |   |   |   |-- [FILE] JMP_NC_pilot_HN_POS_resolution_authorization_v1.md | git: tracked | mode: 100644 | size: 19,29 KB (19.751 B) | type: .md | lines: 417
|   |   |   |   |-- [FILE] JMP_NC_pilot_JAX_optimizer_benchmark_authorization_v1.md | git: tracked | mode: 100644 | size: 15,85 KB (16.229 B) | type: .md | lines: 342
|   |   |   |   |-- [FILE] JMP_NC_pilot_loc4_precompute_augmentation_authorization_v1.md | git: tracked | mode: 100644 | size: 17,23 KB (17.639 B) | type: .md | lines: 350
|   |   |   |   |-- [FILE] JMP_NC_pilot_normalization_rebuild_authorization_v1.md | git: tracked | mode: 100644 | size: 16,32 KB (16.713 B) | type: .md | lines: 356
|   |   |   |   |-- [FILE] JMP_NC_pilot_optimizer_protocol_diagnostic_correction_v1.md | git: tracked | mode: 100644 | size: 10,77 KB (11.030 B) | type: .md | lines: 218
|   |   |   |   |-- [FILE] JMP_NC_pilot_post_em_merge_amendment_v1.md | git: tracked | mode: 100644 | size: 19,72 KB (20.191 B) | type: .md | lines: 408
|   |   |   |   |-- [FILE] JMP_NC_pilot_precompute_readiness_amendment_v1.md | git: tracked | mode: 100644 | size: 14,95 KB (15.308 B) | type: .md | lines: 332
|   |   |   |   |-- [FILE] JMP_NC_pilot_precompute_slice_authorization_v1.md | git: tracked | mode: 100644 | size: 18,90 KB (19.355 B) | type: .md | lines: 394
|   |   |   |   |-- [FILE] JMP_NC_pilot_scaled_JAX_estimator_acceptance_memo_v1.md | git: tracked | mode: 100644 | size: 13,55 KB (13.876 B) | type: .md | lines: 255
|   |   |   |   |-- [FILE] JMP_NC_pilot_scaled_JAX_validation_authorization_v1.md | git: tracked | mode: 100644 | size: 18,64 KB (19.084 B) | type: .md | lines: 385
|   |   |   |   |-- [FILE] JMP_NC_pilot_stage1_4_scope_amendment_v1.md | git: tracked | mode: 100644 | size: 19,66 KB (20.130 B) | type: .md | lines: 390
|   |   |   |   |-- [FILE] JMP_NC_pilot_stage5_strategy_amendment_v2.md | git: tracked | mode: 100644 | size: 26,96 KB (27.608 B) | type: .md | lines: 533
|   |   |   |   \-- [FILE] JMP_NC_pilot_vectorized_likelihood_cleanup_authorization_v1.md | git: tracked | mode: 100644 | size: 11,68 KB (11.965 B) | type: .md | lines: 250
|   |   |   \-- [FILE] README.md | git: tracked | mode: 100644 | size: 1,83 KB (1.876 B) | type: .md | lines: 32
|   |   |-- [DIR] P3a/
|   |   |   |-- [DIR] canary_reports/
|   |   |   |   \-- [FILE] RURO_ruro_occ_M0_rebuild_canary_report_v1.md | git: tracked | mode: 100644 | size: 10,40 KB (10.645 B) | type: .md | lines: 196
|   |   |   |-- [DIR] consolidated/
|   |   |   |   |-- [FILE] JMP_multi_year_2015_2017_consolidated_v1.md | git: tracked | mode: 100644 | size: 2,07 KB (2.122 B) | type: .md | lines: 36
|   |   |   |   |-- [FILE] RURO_GSUR_rebuild_consolidated_v1.md | git: tracked | mode: 100644 | size: 4,07 KB (4.170 B) | type: .md | lines: 57
|   |   |   |   \-- [FILE] RURO_pilot_gsurv2_verification_v1.md | git: tracked | mode: 100644 | size: 7,39 KB (7.569 B) | type: .md | lines: 160
|   |   |   |-- [DIR] design/
|   |   |   |   |-- [FILE] FR2016_RURO_pipeline_report.md | git: tracked | mode: 100644 | size: 42,02 KB (43.029 B) | type: .md | lines: 872
|   |   |   |   |-- [FILE] JMP_next_cycle_opportunity_respecification_plan_v1.md | git: tracked | mode: 100644 | size: 34,64 KB (35.471 B) | type: .md | lines: 737
|   |   |   |   |-- [FILE] JMP_pooled_P3a_estimation_design_memo_v1.md | git: tracked | mode: 100644 | size: 41,98 KB (42.984 B) | type: .md | lines: 957
|   |   |   |   |-- [FILE] RURO_ruro_occ_baseline_implementation_report_v1.md | git: tracked | mode: 100644 | size: 9,75 KB (9.988 B) | type: .md | lines: 252
|   |   |   |   |-- [FILE] RURO_ruro_occ_baseline_spec_v1.md | git: tracked | mode: 100644 | size: 30,66 KB (31.394 B) | type: .md | lines: 1.064
|   |   |   |   |-- [FILE] RURO_ruro_occ_M0_file_sync_check_v1.md | git: tracked | mode: 100644 | size: 3,55 KB (3.640 B) | type: .md | lines: 77
|   |   |   |   |-- [FILE] RURO_ruro_occ_M0_rebuild_command_plan_v1.md | git: tracked | mode: 100644 | size: 17,43 KB (17.851 B) | type: .md | lines: 447
|   |   |   |   \-- [FILE] RURO_ruro_occ_post_estimation_report_fix_v1.md | git: tracked | mode: 100644 | size: 11,44 KB (11.716 B) | type: .md | lines: 214
|   |   |   |-- [DIR] execution_logs/
|   |   |   |   |-- [DIR] Bpool/
|   |   |   |   |   |-- [DIR] realdata_901_gsplit_unified_report/
|   |   |   |   |   |   |-- [FILE] joint_cou_f_contours.png | git: tracked | mode: 100644 | size: 76,67 KB (78.505 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_cou_f_mu.png | git: tracked | mode: 100644 | size: 68,07 KB (69.701 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_cou_m_contours.png | git: tracked | mode: 100644 | size: 55,28 KB (56.610 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_cou_m_mu.png | git: tracked | mode: 100644 | size: 62,19 KB (63.680 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_diagnostics_bundle.json | git: tracked | mode: 100644 | size: 32,83 KB (33.614 B) | type: .json | lines: 966
|   |   |   |   |   |   |-- [FILE] joint_elasticities.csv | git: tracked | mode: 100644 | size: 407 B (407 B) | type: .csv | lines: 5
|   |   |   |   |   |   |-- [FILE] joint_enhanced_parameter_table.csv | git: tracked | mode: 100644 | size: 8,53 KB (8.739 B) | type: .csv | lines: 51
|   |   |   |   |   |   |-- [FILE] joint_fit_mean_hours.png | git: tracked | mode: 100644 | size: 31,12 KB (31.865 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_fit_participation.png | git: tracked | mode: 100644 | size: 30,25 KB (30.981 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_hours_distribution_couples_female.png | git: tracked | mode: 100644 | size: 59,56 KB (60.987 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_hours_distribution_couples_male.png | git: tracked | mode: 100644 | size: 61,41 KB (62.887 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_hours_distribution_singles_female.png | git: tracked | mode: 100644 | size: 60,33 KB (61.774 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_hours_distribution_singles_male.png | git: tracked | mode: 100644 | size: 60,33 KB (61.774 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_hours_distribution_total.png | git: tracked | mode: 100644 | size: 59,31 KB (60.731 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_muc_comparison.png | git: tracked | mode: 100644 | size: 59,63 KB (61.063 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_mul_comparison.png | git: tracked | mode: 100644 | size: 68,68 KB (70.324 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_negative_mu_diagnostics.png | git: tracked | mode: 100644 | size: 31,81 KB (32.570 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_params.csv | git: tracked | mode: 100644 | size: 5,12 KB (5.245 B) | type: .csv | lines: 51
|   |   |   |   |   |   |-- [FILE] joint_post_estimation_report_20260601_093237.html | git: tracked | mode: 100644 | size: 76,47 KB (78.302 B) | type: .html | lines: 1.303
|   |   |   |   |   |   |-- [FILE] joint_sf_contours.png | git: tracked | mode: 100644 | size: 82,97 KB (84.959 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_sf_mu.png | git: tracked | mode: 100644 | size: 63,62 KB (65.144 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_sm_contours.png | git: tracked | mode: 100644 | size: 81,57 KB (83.528 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_sm_mu.png | git: tracked | mode: 100644 | size: 64,30 KB (65.847 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_wage_distribution_couples_female.png | git: tracked | mode: 100644 | size: 70,24 KB (71.922 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_wage_distribution_couples_male.png | git: tracked | mode: 100644 | size: 76,45 KB (78.283 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_wage_distribution_singles_female.png | git: tracked | mode: 100644 | size: 73,25 KB (75.012 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   |-- [FILE] joint_wage_distribution_singles_male.png | git: tracked | mode: 100644 | size: 78,05 KB (79.922 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |   \-- [FILE] joint_wage_distribution_total.png | git: tracked | mode: 100644 | size: 69,34 KB (71.002 B) | type: .png | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] benchmark_gamspy_options_v1.json | git: tracked | mode: 100644 | size: 3,05 KB (3.127 B) | type: .json | lines: 122
|   |   |   |   |   |-- [FILE] benchmark_gamspy_options_v1.log | git: tracked | mode: 100644 | size: 6,74 KB (6.906 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] benchmark_multistart_singles_male.log | git: tracked | mode: 100644 | size: 3,38 KB (3.462 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] benchmark_scipy_lbfgsb_singles_male.log | git: tracked | mode: 100644 | size: 29,86 KB (30.574 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] benchmark_scipy_newton_singles_male.log | git: tracked | mode: 100644 | size: 6,18 KB (6.324 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] conopt_bench_300.json | git: tracked | mode: 100644 | size: 12,67 KB (12.970 B) | type: .json | lines: 330
|   |   |   |   |   |-- [FILE] conopt_freeze_300.json | git: tracked | mode: 100644 | size: 2,40 KB (2.456 B) | type: .json | lines: 84
|   |   |   |   |   |-- [FILE] conopt_freeze_levels_300.json | git: tracked | mode: 100644 | size: 2,40 KB (2.454 B) | type: .json | lines: 84
|   |   |   |   |   |-- [FILE] lh_coverage_20x20.json | git: tracked | mode: 100644 | size: 1,53 KB (1.567 B) | type: .json | lines: 71
|   |   |   |   |   |-- [FILE] realdata_901_joint_baseline_report.html | git: tracked | mode: 100644 | size: 16,05 KB (16.433 B) | type: .html | lines: 160
|   |   |   |   |   |-- [FILE] recovery_singles_female_full2016_v1.log | git: tracked | mode: 100644 | size: 80,75 KB (82.686 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] recovery_singles_male_full2016_thetaL_neg.log | git: tracked | mode: 100644 | size: 64,43 KB (65.978 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] recovery_singles_male_full2016_v1.log | git: tracked | mode: 100644 | size: 65,03 KB (66.594 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] recovery_singles_male_v1.log | git: tracked | mode: 100644 | size: 67,93 KB (69.560 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] recovery_v2_console.log | git: tracked | mode: 100644 | size: 114,49 KB (117.238 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] recovery_v3_couples_full.log | git: tracked | mode: 100644 | size: 110,61 KB (113.262 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] recovery_v3_couples_full_conopt.log | git: tracked | mode: 100644 | size: 1,88 KB (1.920 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] recovery_v3_couples_full_conopt_wc.log | git: tracked | mode: 100644 | size: 7,35 KB (7.524 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] recovery_v3_couples300.log | git: tracked | mode: 100644 | size: 82,74 KB (84.722 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] recovery_v3_singles_female.log | git: tracked | mode: 100644 | size: 69,95 KB (71.626 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] recovery_v3_singles_female_conopt_wc.log | git: tracked | mode: 100644 | size: 5,32 KB (5.446 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] recovery_v3_singles_male.log | git: tracked | mode: 100644 | size: 65,09 KB (66.648 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] recovery_v3_singles_male_conopt.log | git: tracked | mode: 100644 | size: 5,38 KB (5.512 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] recovery_v3_singles_male_conopt_wc.log | git: tracked | mode: 100644 | size: 6,28 KB (6.434 B) | type: .log | lines: N/A (binary)
|   |   |   |   |   |-- [FILE] RURO_Bpool_arc_lessons_learned_v1.md | git: tracked | mode: 100644 | size: 14,90 KB (15.253 B) | type: .md | lines: 281
|   |   |   |   |   |-- [FILE] RURO_Bpool_column_diff_v1.md | git: tracked | mode: 100644 | size: 21,12 KB (21.625 B) | type: .md | lines: 396
|   |   |   |   |   |-- [FILE] RURO_Bpool_draws_verification_v1.md | git: tracked | mode: 100644 | size: 25,10 KB (25.702 B) | type: .md | lines: 566
|   |   |   |   |   |-- [FILE] RURO_Bpool_euromod_run_v1.md | git: tracked | mode: 100644 | size: 6,02 KB (6.164 B) | type: .md | lines: 125
|   |   |   |   |   |-- [FILE] RURO_Bpool_precompute_gate_v1.md | git: tracked | mode: 100644 | size: 14,82 KB (15.175 B) | type: .md | lines: 331
|   |   |   |   |   |-- [FILE] RURO_build_fix_wage_idorighh_v1.md | git: tracked | mode: 100644 | size: 4,06 KB (4.159 B) | type: .md | lines: 103
|   |   |   |   |   |-- [FILE] RURO_conopt_modelgen_benchmark.md | git: tracked | mode: 100644 | size: 1,54 KB (1.574 B) | type: .md | lines: 36
|   |   |   |   |   |-- [FILE] RURO_couples_leisure_profile_v1.md | git: tracked | mode: 100644 | size: 3,92 KB (4.017 B) | type: .md | lines: 178
|   |   |   |   |   |-- [FILE] RURO_gsplit_nonid_structure_v1.md | git: tracked | mode: 100644 | size: 6,83 KB (6.997 B) | type: .md | lines: 115
|   |   |   |   |   |-- [FILE] RURO_jax_bll0_realdata_hessian_v1.md | git: tracked | mode: 100644 | size: 5,11 KB (5.232 B) | type: .md | lines: 110
|   |   |   |   |   |-- [FILE] RURO_jax_recovery_gate_bll0_v1.md | git: tracked | mode: 100644 | size: 5,69 KB (5.825 B) | type: .md | lines: 239
|   |   |   |   |   |-- [FILE] RURO_jax_recovery_gate_bll0_v2.md | git: tracked | mode: 100644 | size: 5,83 KB (5.974 B) | type: .md | lines: 246
|   |   |   |   |   |-- [FILE] RURO_jax_recovery_gate_gsplit_901_v1.md | git: tracked | mode: 100644 | size: 12,07 KB (12.362 B) | type: .md | lines: 369
|   |   |   |   |   |-- [FILE] RURO_jax_recovery_gate_tlmpin_901_v1.md | git: tracked | mode: 100644 | size: 11,62 KB (11.896 B) | type: .md | lines: 341
|   |   |   |   |   |-- [FILE] RURO_jax_recovery_gate_tlmpin_v1.md | git: tracked | mode: 100644 | size: 8,54 KB (8.750 B) | type: .md | lines: 295
|   |   |   |   |   |-- [FILE] RURO_joint_recovery_test_design_v1.md | git: tracked | mode: 100644 | size: 20,41 KB (20.895 B) | type: .md | lines: 324
|   |   |   |   |   |-- [FILE] RURO_joint_recovery_test_results_v1.md | git: tracked | mode: 100644 | size: 11,25 KB (11.524 B) | type: .md | lines: 225
|   |   |   |   |   |-- [FILE] RURO_joint_recovery_test_results_v2.md | git: tracked | mode: 100644 | size: 12,00 KB (12.290 B) | type: .md | lines: 288
|   |   |   |   |   |-- [FILE] RURO_realdata_2016_2017_joint_901_gsplit_v1.md | git: tracked | mode: 100644 | size: 21,93 KB (22.457 B) | type: .md | lines: 661
|   |   |   |   |   |-- [FILE] RURO_realdata_2016_2017_joint_901_v1.md | git: tracked | mode: 100644 | size: 20,48 KB (20.971 B) | type: .md | lines: 624
|   |   |   |   |   |-- [FILE] RURO_realdata_2016_estimation_v1.md | git: tracked | mode: 100644 | size: 10,07 KB (10.312 B) | type: .md | lines: 190
|   |   |   |   |   |-- [FILE] RURO_realdata_2016_postestimation_v1.md | git: tracked | mode: 100644 | size: 8,29 KB (8.491 B) | type: .md | lines: 157
|   |   |   |   |   |-- [FILE] RURO_realdata_lr_pooling_901_v1.md | git: tracked | mode: 100644 | size: 2,33 KB (2.388 B) | type: .md | lines: 56
|   |   |   |   |   |-- [FILE] RURO_realdata_multibasin_test_v1.md | git: tracked | mode: 100644 | size: 7,63 KB (7.808 B) | type: .md | lines: 166
|   |   |   |   |   |-- [FILE] RURO_recovery_test_results_v3.md | git: tracked | mode: 100644 | size: 26,37 KB (27.006 B) | type: .md | lines: 261
|   |   |   |   |   |-- [FILE] RURO_recovery_test_results_v3_couples_full_conopt_wc_raw.md | git: tracked | mode: 100644 | size: 4,90 KB (5.020 B) | type: .md | lines: 87
|   |   |   |   |   |-- [FILE] RURO_recovery_test_results_v3_singles_female_conopt_wc_raw.md | git: tracked | mode: 100644 | size: 5,12 KB (5.238 B) | type: .md | lines: 87
|   |   |   |   |   |-- [FILE] RURO_recovery_test_results_v3_singles_male_conopt_wc_raw.md | git: tracked | mode: 100644 | size: 5,13 KB (5.256 B) | type: .md | lines: 87
|   |   |   |   |   |-- [FILE] RURO_solver_multibasin_findings_v1.md | git: tracked | mode: 100644 | size: 14,75 KB (15.104 B) | type: .md | lines: 188
|   |   |   |   |   \-- [FILE] theta_hat_bll0_jax.csv | git: tracked | mode: 100644 | size: 1,57 KB (1.603 B) | type: .csv | lines: 49
|   |   |   |   |-- [DIR] GSURv2/
|   |   |   |   |   |-- [FILE] JMP_GSURv2_MNL_rebuild_authorization_v1.md | git: tracked | mode: 100644 | size: 45,11 KB (46.194 B) | type: .md | lines: 1.013
|   |   |   |   |   |-- [FILE] JMP_GSURv2_MNL_rebuild_verdict_v1.md | git: tracked | mode: 100644 | size: 43,62 KB (44.671 B) | type: .md | lines: 932
|   |   |   |   |   |-- [FILE] JMP_GSURv2_multi_year_extension_construction_authorization_v1.md | git: tracked | mode: 100644 | size: 51,20 KB (52.429 B) | type: .md | lines: 1.099
|   |   |   |   |   |-- [FILE] JMP_GSURv2_multi_year_extension_construction_report_v1.md | git: tracked | mode: 100644 | size: 19,87 KB (20.351 B) | type: .md | lines: 490
|   |   |   |   |   |-- [FILE] JMP_GSURv2_multi_year_extension_construction_verdict_v1.md | git: tracked | mode: 100644 | size: 37,41 KB (38.304 B) | type: .md | lines: 780
|   |   |   |   |   |-- [FILE] JMP_GSURv2_multi_year_extension_design_memo_v1.md | git: tracked | mode: 100644 | size: 54,51 KB (55.815 B) | type: .md | lines: 1.089
|   |   |   |   |   |-- [FILE] JMP_GSURv2_multi_year_extension_readiness_reaudit_v1.md | git: tracked | mode: 100644 | size: 22,81 KB (23.359 B) | type: .md | lines: 505
|   |   |   |   |   |-- [FILE] JMP_GSURv2_O7_crosswalk_signoff_v1.md | git: tracked | mode: 100644 | size: 1,62 KB (1.663 B) | type: .md | lines: 61
|   |   |   |   |   |-- [FILE] JMP_GSURv2_script_remediation_report_v1.md | git: tracked | mode: 100644 | size: 9,67 KB (9.902 B) | type: .md | lines: 248
|   |   |   |   |   \-- [FILE] JMP_GSURv2_y2016_provenance_lock_plan_v1.md | git: tracked | mode: 100644 | size: 23,95 KB (24.526 B) | type: .md | lines: 531
|   |   |   |   |-- [DIR] multi_year_stage_M1/
|   |   |   |   |   |-- [FILE] JMP_multi_year_sample_construction_descriptives_report_v1.md | git: tracked | mode: 100644 | size: 32,41 KB (33.190 B) | type: .md | lines: 498
|   |   |   |   |   |-- [FILE] JMP_multi_year_stage_M1_execution_readiness_report_v2.md | git: tracked | mode: 100644 | size: 26,77 KB (27.417 B) | type: .md | lines: 473
|   |   |   |   |   |-- [FILE] JMP_multi_year_stage_M1_generalization_fix_report_v1.md | git: tracked | mode: 100644 | size: 6,65 KB (6.812 B) | type: .md | lines: 179
|   |   |   |   |   |-- [FILE] JMP_multi_year_stage_M1_generalization_report_v1.md | git: tracked | mode: 100644 | size: 16,42 KB (16.818 B) | type: .md | lines: 361
|   |   |   |   |   |-- [FILE] JMP_multi_year_stage_M1_implementation_plan_v2.md | git: tracked | mode: 100644 | size: 35,45 KB (36.303 B) | type: .md | lines: 619
|   |   |   |   |   |-- [FILE] JMP_multi_year_stage_M1_implementation_report_v1.md | git: tracked | mode: 100644 | size: 16,74 KB (17.143 B) | type: .md | lines: 383
|   |   |   |   |   |-- [FILE] JMP_multi_year_stage_M1_P3a_construction_verdict_v1.md | git: tracked | mode: 100644 | size: 58,00 KB (59.389 B) | type: .md | lines: 1.174
|   |   |   |   |   |-- [FILE] JMP_stage_M1_P3a_GSURv2_construction_verdict_v1.md | git: tracked | mode: 100644 | size: 18,28 KB (18.722 B) | type: .md | lines: 394
|   |   |   |   |   |-- [FILE] JMP_stage_M1_P3a_GSURv2_stacking_authorization_v1.md | git: tracked | mode: 100644 | size: 37,68 KB (38.580 B) | type: .md | lines: 822
|   |   |   |   |   \-- [FILE] JMP_stage_M1_V9_validation_patch_note_v1.md | git: tracked | mode: 100644 | size: 7,54 KB (7.723 B) | type: .md | lines: 212
|   |   |   |   |-- [DIR] pooled_P3a/
|   |   |   |   |   |-- [FILE] JMP_pooled_P3a_corrected_region_post_estimation_review_v1.md | git: tracked | mode: 100644 | size: 32,51 KB (33.294 B) | type: .md | lines: 655
|   |   |   |   |   |-- [FILE] JMP_pooled_P3a_corrected_region_reestimation_authorization_v1.md | git: tracked | mode: 100644 | size: 35,65 KB (36.510 B) | type: .md | lines: 701
|   |   |   |   |   |-- [FILE] JMP_pooled_P3a_post_estimation_diagnostics_authorization_v1.md | git: tracked | mode: 100644 | size: 30,21 KB (30.933 B) | type: .md | lines: 577
|   |   |   |   |   |-- [FILE] JMP_pooled_P3a_SA2_readiness_strategic_decision_v1.md | git: tracked | mode: 100644 | size: 24,48 KB (25.064 B) | type: .md | lines: 471
|   |   |   |   |   \-- [FILE] RURO_occ_P3a_pooled_GA17_clearance_addendum_v1.md | git: tracked | mode: 100644 | size: 33,96 KB (34.774 B) | type: .md | lines: 674
|   |   |   |   \-- [DIR] single_year_baseline/
|   |   |   |       |-- [DIR] M0a-clean/
|   |   |   |       |   |-- [FILE] RURO_occ_M0a_clean_implementation_report_v1.md | git: tracked | mode: 100644 | size: 16,00 KB (16.380 B) | type: .md | lines: 275
|   |   |   |       |   |-- [FILE] RURO_occ_M0a_clean_post_estimation_patch_report_v1.md | git: tracked | mode: 100644 | size: 10,24 KB (10.483 B) | type: .md | lines: 196
|   |   |   |       |   \-- [FILE] RURO_ruro_occ_M0_estimation_run_2026-05-13.md | git: tracked | mode: 100644 | size: 6,54 KB (6.700 B) | type: .md | lines: 228
|   |   |   |       |-- [DIR] M0b/
|   |   |   |       |   |-- [FILE] RURO_occ_M0b_design_memo_v1.md | git: tracked | mode: 100644 | size: 27,82 KB (28.491 B) | type: .md | lines: 708
|   |   |   |       |   |-- [FILE] RURO_occ_M0b_implementation_audit_v1.md | git: tracked | mode: 100644 | size: 12,77 KB (13.074 B) | type: .md | lines: 316
|   |   |   |       |   \-- [FILE] RURO_occ_M0b_implementation_report_v1.md | git: tracked | mode: 100644 | size: 9,77 KB (10.007 B) | type: .md | lines: 295
|   |   |   |       |-- [DIR] M0c/
|   |   |   |       |   |-- [FILE] RURO_occ_M0c_b_implementation_report_v1.md | git: tracked | mode: 100644 | size: 10,41 KB (10.658 B) | type: .md | lines: 209
|   |   |   |       |   |-- [FILE] RURO_occ_M0c_b2_GSURv2_verdict_v1.md | git: tracked | mode: 100644 | size: 36,82 KB (37.700 B) | type: .md | lines: 822
|   |   |   |       |   \-- [FILE] RURO_occ_M0c_b2_verdict_v1.md | git: tracked | mode: 100644 | size: 21,16 KB (21.664 B) | type: .md | lines: 470
|   |   |   |       \-- [DIR] M1/
|   |   |   |           |-- [FILE] RURO_occ_M1_clean_design_memo_v2.md | git: tracked | mode: 100644 | size: 57,83 KB (59.223 B) | type: .md | lines: 1.228
|   |   |   |           |-- [FILE] RURO_occ_M1_clean_implementation_audit_v1.md | git: tracked | mode: 100644 | size: 17,34 KB (17.760 B) | type: .md | lines: 471
|   |   |   |           |-- [FILE] RURO_occ_M1_clean_verdict_v1.md | git: tracked | mode: 100644 | size: 53,75 KB (55.038 B) | type: .md | lines: 1.094
|   |   |   |           |-- [FILE] RURO_occ_M1_clean_YAML_implementation_report_v1.md | git: tracked | mode: 100644 | size: 8,88 KB (9.089 B) | type: .md | lines: 208
|   |   |   |           |-- [FILE] RURO_occ_M1_naive_robustness_verdict_v1.md | git: tracked | mode: 100644 | size: 62,82 KB (64.325 B) | type: .md | lines: 1.253
|   |   |   |           |-- [FILE] RURO_occ_M1_naive_YAML_implementation_report_v1.md | git: tracked | mode: 100644 | size: 7,69 KB (7.878 B) | type: .md | lines: 226
|   |   |   |           |-- [FILE] RURO_post_estimation_M1_diagnostics_implementation_report_v1.md | git: tracked | mode: 100644 | size: 10,57 KB (10.827 B) | type: .md | lines: 241
|   |   |   |           \-- [FILE] RURO_post_estimation_M1_naive_diagnostics_implementation_report_v1.md | git: tracked | mode: 100644 | size: 15,49 KB (15.859 B) | type: .md | lines: 325
|   |   |   \-- [FILE] README.md | git: tracked | mode: 100644 | size: 2,31 KB (2.369 B) | type: .md | lines: 34
|   |   |-- [FILE] OUTPUTS_FRANCE_CASE_2026-05-26.md | git: tracked | mode: 100644 | size: 4,99 KB (5.106 B) | type: .md | lines: 124
|   |   \-- [FILE] README.md | git: tracked | mode: 100644 | size: 1,60 KB (1.635 B) | type: .md | lines: 20
|   |-- [DIR] jmp_methodology/
|   |   |-- [FILE] JMP_conditional_wage_on_occupation_decision_note_v1.md | git: tracked | mode: 100644 | size: 7,67 KB (7.854 B) | type: .md | lines: 166
|   |   |-- [FILE] JMP_couples_opportunity_draw_design_note_v1.md | git: tracked | mode: 100644 | size: 14,71 KB (15.058 B) | type: .md | lines: 304
|   |   |-- [FILE] JMP_docs_results_cleanup_plan_v1.md | git: tracked | mode: 100644 | size: 8,54 KB (8.740 B) | type: .md | lines: 183
|   |   |-- [FILE] JMP_docs_results_cleanup_second_pass_plan_v1.md | git: tracked | mode: 100644 | size: 26,98 KB (27.623 B) | type: .md | lines: 311
|   |   |-- [FILE] JMP_estimator_architecture_decision_v1.md | git: tracked | mode: 100644 | size: 17,01 KB (17.421 B) | type: .md | lines: 367
|   |   |-- [FILE] JMP_measure_mapping_memo_v1.md | git: tracked | mode: 100644 | size: 9,98 KB (10.223 B) | type: .md | lines: 145
|   |   |-- [FILE] JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md | git: tracked | mode: 100644 | size: 69,57 KB (71.242 B) | type: .md | lines: 1.415
|   |   |-- [FILE] JMP_welfare_measurement_decisions_memo_v2.md | git: tracked | mode: 100644 | size: 67,26 KB (68.878 B) | type: .md | lines: 1.355
|   |   |-- [FILE] JMP_welfare_scaffolding_design_memo_v2.md | git: tracked | mode: 100644 | size: 79,79 KB (81.709 B) | type: .md | lines: 1.776
|   |   |-- [FILE] JMP_welfare_spec_v1.md | git: tracked | mode: 100644 | size: 22,28 KB (22.819 B) | type: .md | lines: 411
|   |   |-- [FILE] JMP_welfare_spec_v2.md | git: tracked | mode: 100644 | size: 28,77 KB (29.464 B) | type: .md | lines: 509
|   |   |-- [FILE] JMP_welfare_spec_v3.md | git: tracked | mode: 100644 | size: 24,92 KB (25.516 B) | type: .md | lines: 424
|   |   |-- [FILE] JMP_welfare_spec_v4.md | git: tracked | mode: 100644 | size: 30,36 KB (31.087 B) | type: .md | lines: 503
|   |   |-- [FILE] JMP_welfare_spec_v5.md | git: tracked | mode: 100644 | size: 34,87 KB (35.706 B) | type: .md | lines: 570
|   |   |-- [FILE] RURO_certified_styled_report_pointer_v1.md | git: tracked | mode: 100644 | size: 7,58 KB (7.763 B) | type: .md | lines: 119
|   |   |-- [FILE] RURO_loc4_four_density_decision_memo_v1.md | git: tracked | mode: 100644 | size: 40,72 KB (41.695 B) | type: .md | lines: 567
|   |   |-- [FILE] RURO_postestimation_descriptives_v1.html | git: tracked | mode: 100644 | size: 500,57 KB (512.585 B) | type: .html | lines: 656
|   |   |-- [FILE] RURO_postestimation_descriptives_v1.md | git: tracked | mode: 100644 | size: 8,33 KB (8.528 B) | type: .md | lines: 159
|   |   |-- [FILE] RURO_rebuild_stage1_pinned_baseline_validation_v1.md | git: tracked | mode: 100644 | size: 11,52 KB (11.792 B) | type: .md | lines: 209
|   |   |-- [FILE] RURO_rebuild_stage2_controlled_reestimation_realdata_v1.md | git: tracked | mode: 100644 | size: 8,65 KB (8.858 B) | type: .md | lines: 163
|   |   |-- [FILE] RURO_rebuild_stage2_engine_ready_parity_v1.md | git: tracked | mode: 100644 | size: 10,13 KB (10.375 B) | type: .md | lines: 200
|   |   |-- [FILE] RURO_rebuild_stage2_synthetic_recovery_v1.md | git: tracked | mode: 100644 | size: 10,10 KB (10.346 B) | type: .md | lines: 170
|   |   |-- [FILE] RURO_welfare_F3R2_reconciliation_joint_parity_v1.md | git: tracked | mode: 100644 | size: 1,81 KB (1.857 B) | type: .md | lines: 55
|   |   |-- [FILE] RURO_welfare_F3R2A_repair_diagnosis_v1.md | git: tracked | mode: 100644 | size: 1,71 KB (1.754 B) | type: .md | lines: 51
|   |   |-- [FILE] RURO_welfare_F3R2B_gate_bc_v1.md | git: tracked | mode: 100644 | size: 1,14 KB (1.168 B) | type: .md | lines: 34
|   |   |-- [FILE] RURO_welfare_F4A_measure_core_report_v1.md | git: tracked | mode: 100644 | size: 7,42 KB (7.597 B) | type: .md | lines: 118
|   |   |-- [FILE] RURO_welfare_F4B_normalization_contract_decision_v1.md | git: tracked | mode: 100644 | size: 14,37 KB (14.716 B) | type: .md | lines: 254
|   |   |-- [FILE] RURO_welfare_F4C_final_singles_measures_report_v1.md | git: tracked | mode: 100644 | size: 5,89 KB (6.035 B) | type: .md | lines: 80
|   |   |-- [FILE] RURO_welfare_F5_primary_scope_ratification_v1.md | git: tracked | mode: 100644 | size: 3,95 KB (4.046 B) | type: .md | lines: 76
|   |   |-- [FILE] RURO_welfare_F5R_crosssection_scope_reconciliation_v1.md | git: tracked | mode: 100644 | size: 6,66 KB (6.823 B) | type: .md | lines: 79
|   |   |-- [FILE] RURO_welfare_gate_report_W3_v1.md | git: tracked | mode: 100644 | size: 13,99 KB (14.324 B) | type: .md | lines: 270
|   |   |-- [FILE] RURO_welfare_scaffold_design_contract_v1.md | git: tracked | mode: 100644 | size: 26,39 KB (27.025 B) | type: .md | lines: 472
|   |   |-- [FILE] RURO_welfare_scaffold_design_contract_v2.md | git: tracked | mode: 100644 | size: 31,10 KB (31.846 B) | type: .md | lines: 535
|   |   |-- [FILE] RURO_welfare_singles_measure_family_F5_report_v1.md | git: tracked | mode: 100644 | size: 5,98 KB (6.125 B) | type: .md | lines: 102
|   |   |-- [FILE] RURO_welfare_singles_Vi_production_report_v1.md | git: tracked | mode: 100644 | size: 13,66 KB (13.986 B) | type: .md | lines: 369
|   |   |-- [FILE] RURO_welfare_stage2_assessment_unit_diagnosis_v1.md | git: tracked | mode: 100644 | size: 12,79 KB (13.096 B) | type: .md | lines: 210
|   |   |-- [FILE] RURO_welfare_stage2_baseline_provenance_decision_memo_v1.md | git: tracked | mode: 100644 | size: 19,27 KB (19.731 B) | type: .md | lines: 297
|   |   |-- [FILE] RURO_welfare_stage2_benefit_state_recoverability_v1.md | git: tracked | mode: 100644 | size: 15,71 KB (16.084 B) | type: .md | lines: 234
|   |   |-- [FILE] RURO_welfare_stage2_chunk_writeback_fix_validation_v1.md | git: tracked | mode: 100644 | size: 9,59 KB (9.816 B) | type: .md | lines: 176
|   |   |-- [FILE] RURO_welfare_stage2_couples_chosen_contamination_v1.md | git: tracked | mode: 100644 | size: 13,67 KB (14.000 B) | type: .md | lines: 243
|   |   |-- [FILE] RURO_welfare_stage2_couples_contamination_audit_v1.md | git: tracked | mode: 100644 | size: 13,46 KB (13.778 B) | type: .md | lines: 241
|   |   |-- [FILE] RURO_welfare_stage2_couples_correction_prep_v1.md | git: tracked | mode: 100644 | size: 9,69 KB (9.923 B) | type: .md | lines: 172
|   |   |-- [FILE] RURO_welfare_stage2_cross_track_benefit_residual_diagnosis_v1.md | git: tracked | mode: 100644 | size: 12,22 KB (12.513 B) | type: .md | lines: 209
|   |   |-- [FILE] RURO_welfare_stage2_full_rebuild_validation_v1.md | git: tracked | mode: 100644 | size: 14,09 KB (14.427 B) | type: .md | lines: 225
|   |   |-- [FILE] RURO_welfare_stage2_parity_v1.md | git: tracked | mode: 100644 | size: 10,94 KB (11.206 B) | type: .md | lines: 191
|   |   |-- [FILE] RURO_welfare_stage2_resim_feasibility_v1.md | git: tracked | mode: 100644 | size: 12,04 KB (12.327 B) | type: .md | lines: 215
|   |   |-- [FILE] RURO_welfare_stage2_singles_vdir_gate_v1.md | git: tracked | mode: 100644 | size: 8,06 KB (8.257 B) | type: .md | lines: 145
|   |   |-- [FILE] RURO_welfare_stage2_twoH_validation_v1.md | git: tracked | mode: 100644 | size: 9,47 KB (9.697 B) | type: .md | lines: 166
|   |   |-- [FILE] RURO_welfare_stage2_vdir_crosscheck_v1.md | git: tracked | mode: 100644 | size: 9,98 KB (10.221 B) | type: .md | lines: 198
|   |   |-- [FILE] RURO_welfare_stage2_vdir_crosscheck_v2.md | git: tracked | mode: 100644 | size: 10,99 KB (11.249 B) | type: .md | lines: 202
|   |   |-- [FILE] RURO_welfare_stage4_baseline_policy_v1.md | git: tracked | mode: 100644 | size: 7,23 KB (7.404 B) | type: .md | lines: 123
|   |   |-- [FILE] RURO_welfare_stage4_population_parity_gate_v1.md | git: tracked | mode: 100644 | size: 8,82 KB (9.033 B) | type: .md | lines: 139
|   |   |-- [FILE] RURO_welfare_stage4_singles_vdir_bias_calibration_v1.md | git: tracked | mode: 100644 | size: 11,43 KB (11.705 B) | type: .md | lines: 197
|   |   |-- [FILE] RURO_welfare_stage4_singles_vdir_smoke_v1.md | git: tracked | mode: 100644 | size: 12,64 KB (12.945 B) | type: .md | lines: 225
|   |   |-- [FILE] The_draft_theorypaper.tex | git: tracked | mode: 100644 | size: 50,71 KB (51.930 B) | type: .tex | lines: 955
|   |   \-- [FILE] welfare_proposal_individualisation_check.md | git: tracked | mode: 100644 | size: 6,46 KB (6.610 B) | type: .md | lines: 121
|   |-- [DIR] methods/
|   |   |-- [FILE] RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md | git: tracked | mode: 100644 | size: 11,89 KB (12.177 B) | type: .md | lines: 428
|   |   |-- [FILE] RURO_CURRENT_STATE_AND_IDENTIFICATION.md | git: tracked | mode: 100644 | size: 9,79 KB (10.028 B) | type: .md | lines: 134
|   |   |-- [FILE] RURO_JOB_MODEL_GMM_METHOD_NOTE.md | git: tracked | mode: 100644 | size: 14,59 KB (14.944 B) | type: .md | lines: 473
|   |   |-- [FILE] RURO_METHODS_AND_PIPELINE_MANUAL_v1.md | git: tracked | mode: 100644 | size: 21,62 KB (22.141 B) | type: .md | lines: 873
|   |   |-- [FILE] RURO_PREFERENCE_ESTIMATION_CAPABILITIES.md | git: tracked | mode: 100644 | size: 28,11 KB (28.788 B) | type: .md | lines: 565
|   |   |-- [FILE] RURO_R_REFERENCE_COMPARISON_AND_ACTION_PLAN.md | git: tracked | mode: 100644 | size: 11,56 KB (11.838 B) | type: .md | lines: 238
|   |   \-- [FILE] RURO_R_REFERENCE_COMPARISON_SECTOR_OPPORTUNITY_PLAN.md | git: tracked | mode: 100644 | size: 22,08 KB (22.615 B) | type: .md | lines: 686
|   |-- [DIR] mirrored/
|   |   \-- [DIR] root/
|   |       \-- [FILE] README.md | git: tracked | mode: 100644 | size: 21,84 KB (22.365 B) | type: .md | lines: 523
|   |-- [DIR] package/
|   |   |-- [FILE] AGENT_HANDOFF.md | git: tracked | mode: 100644 | size: 4,95 KB (5.067 B) | type: .md | lines: 122
|   |   |-- [FILE] PROMPT_outputs_migration_2026-05-26.md | git: tracked | mode: 100644 | size: 5,35 KB (5.479 B) | type: .md | lines: 133
|   |   |-- [FILE] PROMPT_RUM_RURO_refactor_plan_2026-05-26.md | git: tracked | mode: 100644 | size: 11,68 KB (11.959 B) | type: .md | lines: 340
|   |   |-- [FILE] RUM_RURO_codebase_audit_v1.md | git: tracked | mode: 100644 | size: 25,79 KB (26.405 B) | type: .md | lines: 540
|   |   |-- [FILE] RUM_RURO_codebase_audit_v2.md | git: tracked | mode: 100644 | size: 29,33 KB (30.033 B) | type: .md | lines: 606
|   |   |-- [FILE] RUM_RURO_package_refactor_plan_v1.md | git: tracked | mode: 100644 | size: 28,73 KB (29.423 B) | type: .md | lines: 639
|   |   |-- [FILE] RUM_RURO_package_refactor_plan_v2.md | git: tracked | mode: 100644 | size: 39,78 KB (40.736 B) | type: .md | lines: 882
|   |   |-- [FILE] RURO_DATA_CONSOLIDATION_2026-05-26.md | git: tracked | mode: 100644 | size: 10,35 KB (10.603 B) | type: .md | lines: 211
|   |   |-- [FILE] RURO_DATA_STORAGE_AND_PATH_RESOLUTION.md | git: tracked | mode: 100644 | size: 8,37 KB (8.569 B) | type: .md | lines: 242
|   |   |-- [FILE] RURO_NAMING_AND_PACKAGE_SCOPE_v1.md | git: tracked | mode: 100644 | size: 4,08 KB (4.181 B) | type: .md | lines: 103
|   |   |-- [FILE] RURO_OUTPUT_PATH_DESIGN.md | git: tracked | mode: 100644 | size: 4,41 KB (4.515 B) | type: .md | lines: 131
|   |   |-- [FILE] RURO_PACKAGE_PORTABILITY_AND_CLEANUP_POLICY_v1.md | git: tracked | mode: 100644 | size: 8,54 KB (8.746 B) | type: .md | lines: 393
|   |   |-- [FILE] RURO_PATH_MIGRATION_HANDOFF.md | git: tracked | mode: 100644 | size: 13,20 KB (13.520 B) | type: .md | lines: 314
|   |   |-- [FILE] RURO_PROJECT_HYGIENE_CLEANUP_RECOMMENDATIONS.md | git: tracked | mode: 100644 | size: 19,87 KB (20.342 B) | type: .md | lines: 686
|   |   |-- [FILE] RURO_PROJECT_MEMORY_MAP.md | git: tracked | mode: 100644 | size: 11,21 KB (11.475 B) | type: .md | lines: 342
|   |   \-- [FILE] RURO_RETURN_GUIDE_DATA_RESULTS_AND_CLEANUP.md | git: tracked | mode: 100644 | size: 13,66 KB (13.991 B) | type: .md | lines: 468
|   |-- [DIR] reference/
|   |   \-- [FILE] euromod_income_concepts_and_disposable_income.md | git: tracked | mode: 100644 | size: 44,44 KB (45.511 B) | type: .md | lines: 746
|   |-- [DIR] reporting/
|   |   |-- [FILE] RURO_low_token_post_estimation_summary_v1.md | git: tracked | mode: 100644 | size: 7,70 KB (7.888 B) | type: .md | lines: 191
|   |   |-- [FILE] RURO_post_estimation_dynamic_reporting_design_v1.md | git: tracked | mode: 100644 | size: 15,85 KB (16.234 B) | type: .md | lines: 355
|   |   |-- [FILE] RURO_post_estimation_dynamic_reporting_phase2_1_report_v1.md | git: tracked | mode: 100644 | size: 10,88 KB (11.141 B) | type: .md | lines: 220
|   |   |-- [FILE] RURO_post_estimation_dynamic_reporting_phase2_report_v1.md | git: tracked | mode: 100644 | size: 13,23 KB (13.549 B) | type: .md | lines: 283
|   |   \-- [FILE] RURO_post_estimation_styled_general_reporting_enhancement_v1.md | git: tracked | mode: 100644 | size: 12,38 KB (12.677 B) | type: .md | lines: 289
|   |-- [DIR] specifications/
|   |   |-- [FILE] RURO_CONTINUOUS_MNL_VARIABLE_DICTIONARY_v1.md | git: tracked | mode: 100644 | size: 11,75 KB (12.031 B) | type: .md | lines: 242
|   |   |-- [FILE] RURO_model_spec_contract_v4_ruro_occ.md | git: tracked | mode: 100644 | size: 39,06 KB (39.994 B) | type: .md | lines: 609
|   |   |-- [FILE] RURO_occ_pipeline_audit_v1.md | git: tracked | mode: 100644 | size: 20,54 KB (21.035 B) | type: .md | lines: 207
|   |   \-- [FILE] RURO_SPECIFICATIONS_LAYOUT_v1.md | git: tracked | mode: 100644 | size: 1,76 KB (1.799 B) | type: .md | lines: 63
|   |-- [FILE] ACKNOWLEDGEMENTS.md | git: tracked | mode: 100644 | size: 639 B (639 B) | type: .md | lines: 13
|   |-- [FILE] docs_files_structure.md | git: tracked | mode: 100644 | size: 48,68 KB (49.848 B) | type: .md | lines: N/A (binary)
|   |-- [FILE] JMP_literature_review_skeleton_v1.md | git: tracked | mode: 100644 | size: 42,96 KB (43.987 B) | type: .md | lines: 372
|   |-- [FILE] JMP_results_campaign_roadmap_v1.md | git: tracked | mode: 100644 | size: 17,64 KB (18.064 B) | type: .md | lines: 158
|   |-- [FILE] MIRRORED_DOCUMENTS_INDEX.md | git: tracked | mode: 100644 | size: 4,82 KB (4.935 B) | type: .md | lines: 91
|   |-- [FILE] PIPELINE_ENTRYPOINTS.md | git: tracked | mode: 100644 | size: 2,93 KB (3.002 B) | type: .md | lines: 92
|   |-- [FILE] README.md | git: tracked | mode: 100644 | size: 1,63 KB (1.665 B) | type: .md | lines: 25
|   \-- [FILE] ROADMAP.md | git: tracked | mode: 100644 | size: 8,23 KB (8.432 B) | type: .md | lines: 238
|-- [DIR] literature/
|   |-- [FILE] Aaberge_Colombino_2011_Empirical Optimal Income Taxation (1).pdf | git: tracked | mode: 100644 | size: 396,00 KB (405.502 B) | type: .pdf | lines: N/A (binary)
|   |-- [FILE] Dagsvik et al. - 2014 - THEORETICAL AND PRACTICAL ARGUMENTS FOR MODELING LABOR SUPPLY AS A CHOICE AMONG LATENT JOBS.pdf | git: tracked | mode: 100644 | size: 359,41 KB (368.037 B) | type: .pdf | lines: N/A (binary)
|   |-- [FILE] ijm-00139.pdf | git: tracked | mode: 100644 | size: 1,47 MB (1.543.168 B) | type: .pdf | lines: N/A (binary)
|   |-- [FILE] Thumbs.db | git: tracked | mode: 100644 | size: 11,50 KB (11.776 B) | type: .db | lines: N/A (binary)
|   \-- [FILE] Van Soest - 1995 - Structural Models of Family Labor Supply A Discrete Choice Approach.pdf | git: tracked | mode: 100644 | size: 3,09 MB (3.245.124 B) | type: .pdf | lines: N/A (binary)
|-- [DIR] Microsoft/
|   \-- [DIR] Windows/
|       \-- [DIR] PowerShell/
|           \-- [FILE] ModuleAnalysisCache | git: tracked | mode: 100644 | size: 8,85 KB (9.063 B) | type: (none) | lines: N/A (binary)
|-- [DIR] notebooks/
|   |-- [FILE] estimation_notebook.ipynb | git: tracked | mode: 100644 | size: 25,64 KB (26.259 B) | type: .ipynb | lines: 581
|   \-- [FILE] README.md | git: tracked | mode: 100644 | size: 184 B (184 B) | type: .md | lines: 5
|-- [DIR] notes/
|   |-- [FILE] EUROMO_sys_france_2015.md | git: tracked | mode: 100644 | size: 6,02 KB (6.164 B) | type: .md | lines: 151
|   |-- [FILE] notes_files_structure.md | git: tracked | mode: 100644 | size: 394 B (394 B) | type: .md | lines: N/A (binary)
|   \-- [FILE] R_REFERENCE_vs_PYTHON_SPECIFICATION.md | git: tracked | mode: 100644 | size: 8,77 KB (8.977 B) | type: .md | lines: 450
|-- [DIR] outputs/
|   |-- [DIR] figures/
|   |   |-- [FILE] stage5a_task1_se_asymmetry.png | git: tracked | mode: 100644 | size: 28,86 KB (29.549 B) | type: .png | lines: N/A (binary)
|   |   |-- [FILE] stage5a_task2_opportunity_effcount.png | git: tracked | mode: 100644 | size: 40,37 KB (41.341 B) | type: .png | lines: N/A (binary)
|   |   |-- [FILE] stage5a_task3_attractiveness_vs_opportunity.png | git: tracked | mode: 100644 | size: 138,68 KB (142.006 B) | type: .png | lines: N/A (binary)
|   |   |-- [FILE] stage5a_task4_heterogeneity_region.png | git: tracked | mode: 100644 | size: 38,00 KB (38.913 B) | type: .png | lines: N/A (binary)
|   |   |-- [FILE] stage5a_task5_hours_offsets.png | git: tracked | mode: 100644 | size: 28,63 KB (29.322 B) | type: .png | lines: N/A (binary)
|   |   |-- [FILE] stage5a_task5_loc4_wage_densities.png | git: tracked | mode: 100644 | size: 34,68 KB (35.512 B) | type: .png | lines: N/A (binary)
|   |   \-- [FILE] stage5a_task6_ess.png | git: tracked | mode: 100644 | size: 45,32 KB (46.410 B) | type: .png | lines: N/A (binary)
|   |-- [DIR] welfare/
|   |   |-- [DIR] fastlane/
|   |   |   |-- [FILE] couples_ViIS_capture_v1.parquet | git: tracked | mode: 100644 | size: 260,61 KB (266.862 B) | type: .parquet | lines: N/A (binary)
|   |   |   |-- [FILE] couples_ViIS_dualstem_v1.parquet | git: tracked | mode: 100644 | size: 804,39 KB (823.699 B) | type: .parquet | lines: N/A (binary)
|   |   |   |-- [FILE] f3_task2_gate3b_30hh_100nodes.json | git: tracked | mode: 100644 | size: 77,56 KB (79.426 B) | type: .json | lines: 4.018
|   |   |   |-- [FILE] f3_tasks1_5_summary.json | git: tracked | mode: 100644 | size: 5,47 KB (5.598 B) | type: .json | lines: 181
|   |   |   |-- [FILE] f3r2_joint_batch_parity_2016_singles_v1.json | git: tracked | mode: 100644 | size: 2,75 KB (2.821 B) | type: .json | lines: 115
|   |   |   |-- [FILE] f3r2_reconciliation_manifest_v1.json | git: tracked | mode: 100644 | size: 9,34 KB (9.560 B) | type: .json | lines: 302
|   |   |   |-- [FILE] f3r2_run_log.txt | git: tracked | mode: 100644 | size: 16,83 KB (17.232 B) | type: .txt | lines: 162
|   |   |   |-- [FILE] f3r2a_joint_batch_diagnosis_v1.json | git: tracked | mode: 100644 | size: 933 B (933 B) | type: .json | lines: 40
|   |   |   |-- [FILE] f3r2a_repair_manifest_v1.json | git: tracked | mode: 100644 | size: 32,21 KB (32.980 B) | type: .json | lines: 1.253
|   |   |   |-- [FILE] f3r2b_diagnosis_v1.json | git: tracked | mode: 100644 | size: 4,19 KB (4.295 B) | type: .json | lines: 205
|   |   |   |-- [FILE] F4A_manifest_v1.json | git: tracked | mode: 100644 | size: 14,11 KB (14.449 B) | type: .json | lines: 357
|   |   |   |-- [FILE] F4C_manifest_v1.json | git: tracked | mode: 100644 | size: 7,31 KB (7.488 B) | type: .json | lines: 226
|   |   |   |-- [FILE] F5_manifest_v1.json | git: tracked | mode: 100644 | size: 13,61 KB (13.934 B) | type: .json | lines: 397
|   |   |   |-- [FILE] F5R_crosssection_manifest_v1.json | git: tracked | mode: 100644 | size: 51,34 KB (52.570 B) | type: .json | lines: 1.409
|   |   |   |-- [FILE] singles_measure_family_F5_households_v1.parquet | git: tracked | mode: 100644 | size: 488,17 KB (499.891 B) | type: .parquet | lines: N/A (binary)
|   |   |   |-- [FILE] singles_measure_family_F5_v1.parquet | git: tracked | mode: 100644 | size: 19,81 KB (20.282 B) | type: .parquet | lines: N/A (binary)
|   |   |   |-- [FILE] singles_measure_family_F5R_crosssection_v1.parquet | git: tracked | mode: 100644 | size: 20,93 KB (21.430 B) | type: .parquet | lines: N/A (binary)
|   |   |   |-- [FILE] singles_measures_F4A_v1.parquet | git: tracked | mode: 100644 | size: 334,11 KB (342.125 B) | type: .parquet | lines: N/A (binary)
|   |   |   |-- [FILE] singles_measures_F4C_v1.parquet | git: tracked | mode: 100644 | size: 422,22 KB (432.352 B) | type: .parquet | lines: N/A (binary)
|   |   |   |-- [FILE] singles_Vi_production_v1.parquet | git: tracked | mode: 100644 | size: 270,76 KB (277.257 B) | type: .parquet | lines: N/A (binary)
|   |   |   \-- [FILE] singles_ViIS_dualstem_v1.parquet | git: tracked | mode: 100644 | size: 555,31 KB (568.635 B) | type: .parquet | lines: N/A (binary)
|   |   |-- [DIR] fastlane_anchors_v1/
|   |   |   \-- [FILE] manifest.json | git: tracked | mode: 100644 | size: 7,48 KB (7.657 B) | type: .json | lines: 218
|   |   |-- [DIR] fastlane_anchors_v2/
|   |   |   |-- [FILE] anchor_primary_uid200001593700_priced_nodes_v1.parquet | git: tracked | mode: 100644 | size: 11,03 KB (11.296 B) | type: .parquet | lines: N/A (binary)
|   |   |   |-- [FILE] anchor_top_ess_sf_2016_uid200003672000_priced_nodes_v1.parquet | git: tracked | mode: 100644 | size: 11,40 KB (11.674 B) | type: .parquet | lines: N/A (binary)
|   |   |   \-- [FILE] anchor_top_ess_sm_2016_uid200003504101_priced_nodes_v1.parquet | git: tracked | mode: 100644 | size: 10,88 KB (11.143 B) | type: .parquet | lines: N/A (binary)
|   |   |-- [DIR] fastlane_anchors_v3/
|   |   |   |-- [FILE] anchor_primary_uid200001593700_em_input_v3.parquet | git: tracked | mode: 100644 | size: 19,80 KB (20.275 B) | type: .parquet | lines: N/A (binary)
|   |   |   |-- [FILE] anchor_primary_uid200001593700_nodes_v3.parquet | git: tracked | mode: 100644 | size: 5,28 KB (5.405 B) | type: .parquet | lines: N/A (binary)
|   |   |   |-- [FILE] anchor_primary_uid200001593700_priced_v3.parquet | git: tracked | mode: 100644 | size: 213,27 KB (218.393 B) | type: .parquet | lines: N/A (binary)
|   |   |   |-- [FILE] anchor_primary_uid200001593700_provenance_v3.json | git: tracked | mode: 100644 | size: 6,21 KB (6.363 B) | type: .json | lines: 300
|   |   |   |-- [FILE] anchor_top_ess_sf_2016_uid200003672000_em_input_v3.parquet | git: tracked | mode: 100644 | size: 20,20 KB (20.682 B) | type: .parquet | lines: N/A (binary)
|   |   |   |-- [FILE] anchor_top_ess_sf_2016_uid200003672000_nodes_v3.parquet | git: tracked | mode: 100644 | size: 5,43 KB (5.556 B) | type: .parquet | lines: N/A (binary)
|   |   |   |-- [FILE] anchor_top_ess_sf_2016_uid200003672000_priced_v3.parquet | git: tracked | mode: 100644 | size: 218,24 KB (223.477 B) | type: .parquet | lines: N/A (binary)
|   |   |   |-- [FILE] anchor_top_ess_sf_2016_uid200003672000_provenance_v3.json | git: tracked | mode: 100644 | size: 6,25 KB (6.401 B) | type: .json | lines: 300
|   |   |   |-- [FILE] anchor_top_ess_sm_2016_uid200003504101_em_input_v3.parquet | git: tracked | mode: 100644 | size: 19,89 KB (20.364 B) | type: .parquet | lines: N/A (binary)
|   |   |   |-- [FILE] anchor_top_ess_sm_2016_uid200003504101_nodes_v3.parquet | git: tracked | mode: 100644 | size: 5,31 KB (5.434 B) | type: .parquet | lines: N/A (binary)
|   |   |   |-- [FILE] anchor_top_ess_sm_2016_uid200003504101_priced_v3.parquet | git: tracked | mode: 100644 | size: 213,26 KB (218.379 B) | type: .parquet | lines: N/A (binary)
|   |   |   \-- [FILE] anchor_top_ess_sm_2016_uid200003504101_provenance_v3.json | git: tracked | mode: 100644 | size: 6,25 KB (6.403 B) | type: .json | lines: 300
|   |   \-- [DIR] stage1_w3/
|   |       |-- [FILE] production_results.json | git: tracked | mode: 100644 | size: 9,06 KB (9.275 B) | type: .json | lines: 315
|   |       |-- [FILE] smoke_results.json | git: tracked | mode: 100644 | size: 9,02 KB (9.234 B) | type: .json | lines: 315
|   |       |-- [FILE] stage2_assessment_unit_diag.json | git: tracked | mode: 100644 | size: 21,99 KB (22.517 B) | type: .json | lines: 758
|   |       |-- [FILE] stage2_benefit_state_inventory.json | git: tracked | mode: 100644 | size: 16,58 KB (16.982 B) | type: .json | lines: 793
|   |       |-- [FILE] stage2_chosen_measure.json | git: tracked | mode: 100644 | size: 3,79 KB (3.886 B) | type: .json | lines: 128
|   |       |-- [FILE] stage2_chosen_measure_euromod_console.log | git: tracked | mode: 100644 | size: 0 B (0 B) | type: .log | lines: 0
|   |       |-- [FILE] stage2_chosen_measure_per_hh.csv | git: tracked | mode: 100644 | size: 101,86 KB (104.302 B) | type: .csv | lines: 901
|   |       |-- [FILE] stage2_chosen_task1.json | git: tracked | mode: 100644 | size: 8,47 KB (8.673 B) | type: .json | lines: 306
|   |       |-- [FILE] stage2_chosen_task1_euromod_console.log | git: tracked | mode: 100644 | size: 0 B (0 B) | type: .log | lines: 0
|   |       |-- [FILE] stage2_chunk_writeback_validation.json | git: tracked | mode: 100644 | size: 12,27 KB (12.568 B) | type: .json | lines: 380
|   |       |-- [FILE] stage2_chunk_writeback_validation_euromod.log | git: tracked | mode: 100644 | size: 10,56 KB (10.818 B) | type: .log | lines: 108
|   |       |-- [FILE] stage2_correction_prep_euromod_console.log | git: tracked | mode: 100644 | size: 402 B (402 B) | type: .log | lines: 4
|   |       |-- [FILE] stage2_couples_contamination_audit.json | git: tracked | mode: 100644 | size: 4,83 KB (4.947 B) | type: .json | lines: 141
|   |       |-- [FILE] stage2_couples_correction_prep.json | git: tracked | mode: 100644 | size: 8,40 KB (8.599 B) | type: .json | lines: 294
|   |       |-- [FILE] stage2_couples_exposed_mass_per_hh.csv | git: tracked | mode: 100644 | size: 313,75 KB (321.283 B) | type: .csv | lines: 7.439
|   |       |-- [FILE] stage2_couples_reprice.json | git: tracked | mode: 100644 | size: 83,60 KB (85.611 B) | type: .json | lines: 3.136
|   |       |-- [FILE] stage2_couples_reprice_euromod_console.log | git: tracked | mode: 100644 | size: 0 B (0 B) | type: .log | lines: 0
|   |       |-- [FILE] stage2_cross_track_diag_euromod_console.log | git: tracked | mode: 100644 | size: 0 B (0 B) | type: .log | lines: 0
|   |       |-- [FILE] stage2_cross_track_residual_diag.json | git: tracked | mode: 100644 | size: 5,97 KB (6.111 B) | type: .json | lines: 190
|   |       |-- [FILE] stage2_full_rebuild_staging.json | git: tracked | mode: 100644 | size: 31,73 KB (32.491 B) | type: .json | lines: 1.247
|   |       |-- [FILE] stage2_full_rebuild_validation.json | git: tracked | mode: 100644 | size: 14,92 KB (15.280 B) | type: .json | lines: 518
|   |       |-- [FILE] stage2_parity_results.json | git: tracked | mode: 100644 | size: 7,45 KB (7.628 B) | type: .json | lines: 242
|   |       |-- [FILE] stage2_parity_smoke_rows_diag.csv | git: tracked | mode: 100644 | size: 11,18 KB (11.450 B) | type: .csv | lines: 101
|   |       |-- [FILE] stage2_resim_euromod_console.log | git: tracked | mode: 100644 | size: 8,01 KB (8.200 B) | type: .log | lines: 102
|   |       |-- [FILE] stage2_resim_results.json | git: tracked | mode: 100644 | size: 10,44 KB (10.686 B) | type: .json | lines: 330
|   |       |-- [FILE] stage2_singles_vdir_gate.json | git: tracked | mode: 100644 | size: 7,80 KB (7.987 B) | type: .json | lines: 282
|   |       |-- [FILE] stage2_singles_vdir_gate_euromod_console.log | git: tracked | mode: 100644 | size: 0 B (0 B) | type: .log | lines: 0
|   |       |-- [FILE] stage2_twoH_validation.json | git: tracked | mode: 100644 | size: 4,33 KB (4.436 B) | type: .json | lines: 154
|   |       |-- [FILE] stage2_twoH_validation_euromod_console.log | git: tracked | mode: 100644 | size: 804 B (804 B) | type: .log | lines: 8
|   |       |-- [FILE] stage2_vdir_results.json | git: tracked | mode: 100644 | size: 5,63 KB (5.761 B) | type: .json | lines: 183
|   |       |-- [FILE] stage2_vdir_v2_results.json | git: tracked | mode: 100644 | size: 8,99 KB (9.208 B) | type: .json | lines: 230
|   |       |-- [FILE] stage3a_pinned_baseline_validation.json | git: tracked | mode: 100644 | size: 14,87 KB (15.231 B) | type: .json | lines: 460
|   |       |-- [FILE] stage3a_pinned_rebuild_config.json | git: tracked | mode: 100644 | size: 12,34 KB (12.635 B) | type: .json | lines: 619
|   |       |-- [FILE] stage3b1_engine_ready_parity.json | git: tracked | mode: 100644 | size: 10,07 KB (10.315 B) | type: .json | lines: 275
|   |       |-- [FILE] stage3b2_controlled_reestimation.json | git: tracked | mode: 100644 | size: 29,30 KB (30.007 B) | type: .json | lines: 804
|   |       |-- [FILE] stage3b2_step4_rebuilt.json | git: tracked | mode: 100644 | size: 15,55 KB (15.923 B) | type: .json | lines: 538
|   |       |-- [FILE] stage3b2_step4_report.md | git: tracked | mode: 100644 | size: 21,33 KB (21.847 B) | type: .md | lines: 643
|   |       |-- [FILE] stage3b3_staged_gate.json | git: tracked | mode: 100644 | size: 4,77 KB (4.887 B) | type: .json | lines: 214
|   |       |-- [FILE] stage3b3_staged_gate_report.md | git: tracked | mode: 100644 | size: 6,27 KB (6.416 B) | type: .md | lines: 258
|   |       |-- [FILE] stage3b3_synthetic_recovery.json | git: tracked | mode: 100644 | size: 10,86 KB (11.117 B) | type: .json | lines: 334
|   |       |-- [FILE] stage4a_baseline_policy.json | git: tracked | mode: 100644 | size: 4,53 KB (4.634 B) | type: .json | lines: 125
|   |       |-- [FILE] stage4b_population_parity_gate.json | git: tracked | mode: 100644 | size: 12,84 KB (13.144 B) | type: .json | lines: 420
|   |       |-- [FILE] stage4c_singles_vdir_smoke.json | git: tracked | mode: 100644 | size: 11,03 KB (11.293 B) | type: .json | lines: 394
|   |       |-- [FILE] stage4c_singles_vdir_smoke_n60.json | git: tracked | mode: 100644 | size: 14,49 KB (14.835 B) | type: .json | lines: 629
|   |       |-- [FILE] stage4c2_vdir_bias_calibration.json | git: tracked | mode: 100644 | size: 13,35 KB (13.675 B) | type: .json | lines: 355
|   |       |-- [FILE] stage5a_postestimation_descriptives.json | git: tracked | mode: 100644 | size: 19,52 KB (19.988 B) | type: .json | lines: 664
|   |       \-- [FILE] stage5a2_styled_enhanced.json | git: tracked | mode: 100644 | size: 4,02 KB (4.114 B) | type: .json | lines: 66
|   |-- [FILE] KEEP_RESULTS.md | git: tracked | mode: 100644 | size: 320 B (320 B) | type: .md | lines: 10
|   |-- [FILE] opportunity_diagnostics_certified_v1.parquet | git: tracked | mode: 100644 | size: 1,20 MB (1.257.210 B) | type: .parquet | lines: N/A (binary)
|   \-- [FILE] outputs_files_structure.md | git: tracked | mode: 100644 | size: 5,38 KB (5.512 B) | type: .md | lines: N/A (binary)
|-- [DIR] Pdfs/
|   |-- [FILE] Bargain et al_2013_Welfare, labor supply and heterogeneous preferences.pdf | git: tracked | mode: 100644 | size: 647,51 KB (663.049 B) | type: .pdf | lines: N/A (binary)
|   |-- [FILE] Bargain et al_2014_Comparing inequality aversion across countries when labor supply responses.pdf | git: tracked | mode: 100644 | size: 940,91 KB (963.492 B) | type: .pdf | lines: N/A (binary)
|   |-- [FILE] M0_cont.pdf | git: tracked | mode: 100644 | size: 7,38 MB (7.734.216 B) | type: .pdf | lines: N/A (binary)
|   |-- [FILE] M0a_cont.pdf | git: tracked | mode: 100644 | size: 7,04 MB (7.383.708 B) | type: .pdf | lines: N/A (binary)
|   |-- [FILE] M0b1.pdf | git: tracked | mode: 100644 | size: 7,35 MB (7.707.232 B) | type: .pdf | lines: N/A (binary)
|   |-- [FILE] m0b2.pdf | git: tracked | mode: 100644 | size: 6,85 MB (7.178.867 B) | type: .pdf | lines: N/A (binary)
|   |-- [FILE] M0C_b2.pdf | git: tracked | mode: 100644 | size: 7,03 MB (7.373.339 B) | type: .pdf | lines: N/A (binary)
|   \-- [FILE] p3a_joint.pdf | git: tracked | mode: 100644 | size: 7,37 MB (7.732.835 B) | type: .pdf | lines: N/A (binary)
|-- [DIR] Prompts/
|   |-- [DIR] Bpool/
|   |   \-- [FILE] RURO_reparameterise_utility_to_ACS_form_v2.md | git: tracked | mode: 100644 | size: 8,96 KB (9.174 B) | type: .md | lines: 133
|   |-- [DIR] Prototype/
|   |   \-- [FILE] Prompt_f3 | git: tracked | mode: 100644 | size: 4,54 KB (4.649 B) | type: (none) | lines: 72
|   |-- [DIR] replies/
|   |   \-- [FILE] codex_! | git: tracked | mode: 100644 | size: 8,57 KB (8.778 B) | type: (none) | lines: 97
|   |-- [DIR] welfare/
|   |   |-- [FILE] Prompt1.txt | git: tracked | mode: 100644 | size: 3,92 KB (4.018 B) | type: .txt | lines: 22
|   |   |-- [FILE] Prompt10.txt | git: tracked | mode: 100644 | size: 4,11 KB (4.204 B) | type: .txt | lines: 60
|   |   |-- [FILE] Prompt11.txt | git: tracked | mode: 100644 | size: 3,52 KB (3.604 B) | type: .txt | lines: 50
|   |   |-- [FILE] prompt12.txt | git: tracked | mode: 100644 | size: 4,65 KB (4.761 B) | type: .txt | lines: 64
|   |   |-- [FILE] Prompt13.txt | git: tracked | mode: 100644 | size: 4,75 KB (4.867 B) | type: .txt | lines: 63
|   |   |-- [FILE] Prompt14.txt | git: tracked | mode: 100644 | size: 3,76 KB (3.846 B) | type: .txt | lines: 74
|   |   |-- [FILE] Prompt15.txt | git: tracked | mode: 100644 | size: 3,71 KB (3.800 B) | type: .txt | lines: 74
|   |   |-- [FILE] Prompt16.txt | git: tracked | mode: 100644 | size: 5,14 KB (5.266 B) | type: .txt | lines: 118
|   |   |-- [FILE] Prompt17.txt | git: tracked | mode: 100644 | size: 3,91 KB (4.000 B) | type: .txt | lines: 105
|   |   |-- [FILE] Prompt18.txt | git: tracked | mode: 100644 | size: 5,38 KB (5.509 B) | type: .txt | lines: 153
|   |   |-- [FILE] Prompt19.txt | git: tracked | mode: 100644 | size: 5,93 KB (6.075 B) | type: .txt | lines: 121
|   |   |-- [FILE] Prompt2.txt | git: tracked | mode: 100644 | size: 2,87 KB (2.942 B) | type: .txt | lines: 45
|   |   |-- [FILE] Prompt20.txt | git: tracked | mode: 100644 | size: 5,31 KB (5.434 B) | type: .txt | lines: 127
|   |   |-- [FILE] Prompt21.txt | git: tracked | mode: 100644 | size: 4,72 KB (4.831 B) | type: .txt | lines: 122
|   |   |-- [FILE] Prompt3.txt | git: tracked | mode: 100644 | size: 4,29 KB (4.391 B) | type: .txt | lines: 63
|   |   |-- [FILE] Prompt4.txt | git: tracked | mode: 100644 | size: 4,04 KB (4.133 B) | type: .txt | lines: 61
|   |   |-- [FILE] Prompt5.txt | git: tracked | mode: 100644 | size: 3,97 KB (4.065 B) | type: .txt | lines: 61
|   |   |-- [FILE] Prompt6.txt | git: tracked | mode: 100644 | size: 2,63 KB (2.692 B) | type: .txt | lines: 43
|   |   |-- [FILE] Prompt7.txt | git: tracked | mode: 100644 | size: 3,13 KB (3.200 B) | type: .txt | lines: 43
|   |   |-- [FILE] Prompt8.txt | git: tracked | mode: 100644 | size: 3,13 KB (3.200 B) | type: .txt | lines: 43
|   |   \-- [FILE] Prompt9.txt | git: tracked | mode: 100644 | size: 3,88 KB (3.976 B) | type: .txt | lines: 54
|   |-- [FILE] Compact_After_data_relocation.md | git: tracked | mode: 100644 | size: 7,61 KB (7.793 B) | type: .md | lines: 122
|   |-- [FILE] JMP_ability_vs_opportunity_framework_v1.md | git: tracked | mode: 100644 | size: 25,76 KB (26.380 B) | type: .md | lines: 579
|   |-- [FILE] JMP_next_step_recommendation_v1.md | git: tracked | mode: 100644 | size: 23,03 KB (23.580 B) | type: .md | lines: 458
|   |-- [FILE] Output_cleaning_prompt.md | git: tracked | mode: 100644 | size: 5,35 KB (5.477 B) | type: .md | lines: 133
|   |-- [FILE] Prompts_files_structure.md | git: tracked | mode: 100644 | size: 2,37 KB (2.428 B) | type: .md | lines: N/A (binary)
|   |-- [FILE] question_answer_Ab_opp.md | git: tracked | mode: 100644 | size: 13,58 KB (13.907 B) | type: .md | lines: 167
|   |-- [FILE] replies_GPT | git: tracked | mode: 100644 | size: 30,18 KB (30.907 B) | type: (none) | lines: 822
|   |-- [FILE] RURO_GSUR_v2_stageA_MNL_rebuild_prompt_corrected_v1.md | git: tracked | mode: 100644 | size: 16,02 KB (16.405 B) | type: .md | lines: 355
|   |-- [FILE] RURO_GSUR_v2_stageA_MNL_rebuild_prompt_corrected_v2.md | git: tracked | mode: 100644 | size: 21,04 KB (21.545 B) | type: .md | lines: 464
|   |-- [FILE] RURO_occ_M0c_b2_implementation_and_estimation_prompt_v1.md | git: tracked | mode: 100644 | size: 12,17 KB (12.458 B) | type: .md | lines: 275
|   |-- [FILE] RURO_ruro_occ_M0_proposal_adequacy_diag_prompt_v1.md | git: tracked | mode: 100644 | size: 13,36 KB (13.685 B) | type: .md | lines: 319
|   |-- [FILE] RURO_ruro_occ_M0a_clean_rename_and_participation_diag_prompts_v1.md | git: tracked | mode: 100644 | size: 17,91 KB (18.338 B) | type: .md | lines: 530
|   |-- [FILE] series_of_Prompts.md | git: tracked | mode: 100644 | size: 156,86 KB (160.622 B) | type: .md | lines: 2.585
|   \-- [FILE] series2.md | git: tracked | mode: 100644 | size: 16,04 KB (16.430 B) | type: .md | lines: 528
|-- [DIR] Results/
|   |-- [DIR] _M0b2_multistart_inits/
|   |   |-- [FILE] S1_spec_defaults_init.json | git: tracked | mode: 100644 | size: 1,46 KB (1.497 B) | type: .json | lines: 56
|   |   |-- [FILE] S2_perturb_defaults_init.json | git: tracked | mode: 100644 | size: 2,10 KB (2.155 B) | type: .json | lines: 56
|   |   |-- [FILE] S3_perturb_solution_init.json | git: tracked | mode: 100644 | size: 2,13 KB (2.184 B) | type: .json | lines: 56
|   |   \-- [FILE] S4_dispersed_interior_init.json | git: tracked | mode: 100644 | size: 1,49 KB (1.529 B) | type: .json | lines: 56
|   |-- [DIR] _M0c_b2_multistart_inits/
|   |   |-- [FILE] S1_spec_defaults_init.json | git: tracked | mode: 100644 | size: 1,44 KB (1.472 B) | type: .json | lines: 55
|   |   |-- [FILE] S2_warmstart_M0c_b_init.json | git: tracked | mode: 100644 | size: 2,15 KB (2.200 B) | type: .json | lines: 55
|   |   \-- [FILE] S3_dispersed_interior_init.json | git: tracked | mode: 100644 | size: 1,47 KB (1.503 B) | type: .json | lines: 55
|   |-- [DIR] _shared/
|   |   |-- [FILE] JMP_docs_results_cleanup_report_v1.md | git: tracked | mode: 100644 | size: 11,90 KB (12.184 B) | type: .md | lines: 221
|   |   |-- [FILE] JMP_docs_results_cleanup_second_pass_execution_report_v1.md | git: tracked | mode: 100644 | size: 11,86 KB (12.142 B) | type: .md | lines: 209
|   |   |-- [FILE] JMP_docs_results_cleanup_second_pass_report_v1.md | git: tracked | mode: 100644 | size: 14,15 KB (14.494 B) | type: .md | lines: 250
|   |   |-- [FILE] JMP_opportunity_block_readonly_diagnostic_v1.md | git: tracked | mode: 100644 | size: 23,97 KB (24.548 B) | type: .md | lines: 586
|   |   \-- [FILE] RURO_cluster_robust_SE_static_validation_v1.md | git: tracked | mode: 100644 | size: 1,97 KB (2.020 B) | type: .md | lines: 40
|   |-- [DIR] archive/
|   |   |-- [DIR] 2026-05-20_post_gsurv2_mnl_rebuild/
|   |   |   |-- [FILE] JMP_GSURv2_MNL_rebuild_report_v1.md | git: tracked | mode: 100644 | size: 22,23 KB (22.768 B) | type: .md | lines: 546
|   |   |   |-- [FILE] JMP_multi_year_feasibility_audit_addendum_v1.md | git: tracked | mode: 100644 | size: 15,83 KB (16.210 B) | type: .md | lines: 234
|   |   |   |-- [FILE] JMP_multi_year_stage_M1_P3a_execution_report_v1.md | git: tracked | mode: 100644 | size: 22,06 KB (22.594 B) | type: .md | lines: 455
|   |   |   |-- [FILE] JMP_multi_year_stage_M1_P3a_full_execution_addendum_v1.md | git: tracked | mode: 100644 | size: 18,54 KB (18.982 B) | type: .md | lines: 250
|   |   |   |-- [FILE] JMP_multi_year_stage_M1_readiness_addendum_v1.md | git: tracked | mode: 100644 | size: 11,58 KB (11.862 B) | type: .md | lines: 167
|   |   |   |-- [FILE] JMP_multi_year_stage_M1_static_validation_report_v1.md | git: tracked | mode: 100644 | size: 9,26 KB (9.482 B) | type: .md | lines: 235
|   |   |   |-- [FILE] JMP_multi_year_stage_M1_static_validation_report_v2.md | git: tracked | mode: 100644 | size: 7,68 KB (7.865 B) | type: .md | lines: 244
|   |   |   \-- [FILE] M1_identity_validation_summary.md | git: tracked | mode: 100644 | size: 1,72 KB (1.761 B) | type: .md | lines: 76
|   |   \-- [DIR] 2026-05-27_results_stale_runs/
|   |       |-- [FILE] M1_cluster_key_check_20260520_093638.csv | git: tracked | mode: 100644 | size: 321 B (321 B) | type: .csv | lines: 7
|   |       |-- [FILE] M1_cluster_key_check_20260520_100856.csv | git: tracked | mode: 100644 | size: 321 B (321 B) | type: .csv | lines: 7
|   |       |-- [FILE] M1_cpi_harmonisation_check_20260520_093602.csv | git: tracked | mode: 100644 | size: 244 B (244 B) | type: .csv | lines: 4
|   |       |-- [FILE] M1_cpi_harmonisation_check_20260520_100824.csv | git: tracked | mode: 100644 | size: 542 B (542 B) | type: .csv | lines: 4
|   |       |-- [FILE] M1_raw_id_preservation_check_20260520_093734.csv | git: tracked | mode: 100644 | size: 134 B (134 B) | type: .csv | lines: 5
|   |       |-- [FILE] M1_raw_id_preservation_check_20260520_100947.csv | git: tracked | mode: 100644 | size: 138 B (138 B) | type: .csv | lines: 5
|   |       |-- [FILE] M1_raw_id_preservation_check_20260520_223735.csv | git: tracked | mode: 100644 | size: 138 B (138 B) | type: .csv | lines: 5
|   |       |-- [FILE] M1_stacked_id_manifest_20260520_093417.csv | git: tracked | mode: 100644 | size: 476 B (476 B) | type: .csv | lines: 4
|   |       |-- [FILE] M1_stacked_id_manifest_20260520_093734.csv | git: tracked | mode: 100644 | size: 968 B (968 B) | type: .csv | lines: 4
|   |       |-- [FILE] M1_stacked_id_manifest_20260520_100713.csv | git: tracked | mode: 100644 | size: 620 B (620 B) | type: .csv | lines: 4
|   |       |-- [FILE] M1_stacked_id_manifest_20260520_100947.csv | git: tracked | mode: 100644 | size: 968 B (968 B) | type: .csv | lines: 4
|   |       |-- [FILE] M1_stacked_id_manifest_20260520_223633.csv | git: tracked | mode: 100644 | size: 620 B (620 B) | type: .csv | lines: 4
|   |       |-- [FILE] M1_stacked_id_manifest_20260520_223735.csv | git: tracked | mode: 100644 | size: 968 B (968 B) | type: .csv | lines: 4
|   |       |-- [FILE] M1_validation_summary_20260520_093734.csv | git: tracked | mode: 100644 | size: 1,38 KB (1.418 B) | type: .csv | lines: 20
|   |       |-- [FILE] M1_validation_summary_20260520_100947.csv | git: tracked | mode: 100644 | size: 1,78 KB (1.820 B) | type: .csv | lines: 20
|   |       |-- [FILE] M1_validation_summary_20260520_223735.csv | git: tracked | mode: 100644 | size: 1,82 KB (1.860 B) | type: .csv | lines: 10
|   |       \-- [FILE] README.md | git: tracked | mode: 100644 | size: 1,44 KB (1.473 B) | type: .md | lines: 21
|   |-- [DIR] diagnostics/
|   |   \-- [FILE] smoke_test_stdout_20260521.txt | git: tracked | mode: 100644 | size: 9,31 KB (9.532 B) | type: .txt | lines: N/A (binary)
|   |-- [DIR] figures/
|   |   \-- [DIR] multi_year_descriptives/
|   |       |-- [FILE] fr_2015_all_hours_by_gender.png | git: tracked | mode: 100644 | size: 33,38 KB (34.183 B) | type: .png | lines: N/A (binary)
|   |       |-- [FILE] fr_2015_all_ils_dispy.png | git: tracked | mode: 100644 | size: 43,91 KB (44.964 B) | type: .png | lines: N/A (binary)
|   |       |-- [FILE] fr_2015_all_lhw.png | git: tracked | mode: 100644 | size: 36,77 KB (37.654 B) | type: .png | lines: N/A (binary)
|   |       |-- [FILE] fr_2015_all_yem.png | git: tracked | mode: 100644 | size: 38,59 KB (39.513 B) | type: .png | lines: N/A (binary)
|   |       |-- [FILE] fr_2015_couples_lhw.png | git: tracked | mode: 100644 | size: 40,64 KB (41.617 B) | type: .png | lines: N/A (binary)
|   |       |-- [FILE] fr_2015_singles_lhw.png | git: tracked | mode: 100644 | size: 35,72 KB (36.578 B) | type: .png | lines: N/A (binary)
|   |       |-- [FILE] fr_2016_all_hours_by_gender.png | git: tracked | mode: 100644 | size: 33,67 KB (34.478 B) | type: .png | lines: N/A (binary)
|   |       |-- [FILE] fr_2016_all_ils_dispy.png | git: tracked | mode: 100644 | size: 37,35 KB (38.244 B) | type: .png | lines: N/A (binary)
|   |       |-- [FILE] fr_2016_all_lhw.png | git: tracked | mode: 100644 | size: 36,27 KB (37.144 B) | type: .png | lines: N/A (binary)
|   |       |-- [FILE] fr_2016_all_yem.png | git: tracked | mode: 100644 | size: 38,45 KB (39.372 B) | type: .png | lines: N/A (binary)
|   |       |-- [FILE] fr_2016_couples_lhw.png | git: tracked | mode: 100644 | size: 40,98 KB (41.965 B) | type: .png | lines: N/A (binary)
|   |       |-- [FILE] fr_2016_singles_lhw.png | git: tracked | mode: 100644 | size: 40,75 KB (41.733 B) | type: .png | lines: N/A (binary)
|   |       |-- [FILE] fr_2017_all_hours_by_gender.png | git: tracked | mode: 100644 | size: 37,67 KB (38.573 B) | type: .png | lines: N/A (binary)
|   |       |-- [FILE] fr_2017_all_ils_dispy.png | git: tracked | mode: 100644 | size: 41,16 KB (42.147 B) | type: .png | lines: N/A (binary)
|   |       |-- [FILE] fr_2017_all_lhw.png | git: tracked | mode: 100644 | size: 40,89 KB (41.868 B) | type: .png | lines: N/A (binary)
|   |       |-- [FILE] fr_2017_all_yem.png | git: tracked | mode: 100644 | size: 41,19 KB (42.180 B) | type: .png | lines: N/A (binary)
|   |       |-- [FILE] fr_2017_couples_lhw.png | git: tracked | mode: 100644 | size: 39,24 KB (40.179 B) | type: .png | lines: N/A (binary)
|   |       \-- [FILE] fr_2017_singles_lhw.png | git: tracked | mode: 100644 | size: 40,39 KB (41.362 B) | type: .png | lines: N/A (binary)
|   |-- [DIR] NC_pilot/
|   |   |-- [DIR] diagnostic_estimation_v1/
|   |   |   |-- [DIR] start_default/
|   |   |   |   \-- [FILE] estimation_results.json | git: tracked | mode: 100644 | size: 2,66 KB (2.727 B) | type: .json | lines: 128
|   |   |   |-- [DIR] start_perturbed/
|   |   |   |   \-- [FILE] estimation_results.json | git: tracked | mode: 100644 | size: 2,78 KB (2.849 B) | type: .json | lines: 128
|   |   |   \-- [DIR] start_warm/
|   |   |       \-- [FILE] estimation_results.json | git: tracked | mode: 100644 | size: 3,67 KB (3.759 B) | type: .json | lines: 130
|   |   |-- [FILE] JMP_NC_pilot_beta_l0_m_diagnostic_report_v1.md | git: tracked | mode: 100644 | size: 30,07 KB (30.788 B) | type: .md | lines: 589
|   |   |-- [FILE] JMP_NC_pilot_build_report_v1.md | git: tracked | mode: 100644 | size: 14,52 KB (14.865 B) | type: .md | lines: 338
|   |   |-- [FILE] JMP_NC_pilot_diagnostic_estimation_rerun_report_v1.md | git: tracked | mode: 100644 | size: 12,59 KB (12.894 B) | type: .md | lines: 328
|   |   |-- [FILE] JMP_NC_pilot_draw_joint_precompute_compatibility_report_v1.md | git: tracked | mode: 100644 | size: 16,49 KB (16.889 B) | type: .md | lines: 408
|   |   |-- [FILE] JMP_NC_pilot_draw_joint_repointing_audit_v1.md | git: tracked | mode: 100644 | size: 28,66 KB (29.347 B) | type: .md | lines: 581
|   |   |-- [FILE] JMP_NC_pilot_EUROMOD_runner_confirmation_v1.md | git: tracked | mode: 100644 | size: 36,61 KB (37.486 B) | type: .md | lines: 722
|   |   |-- [FILE] JMP_nc_pilot_feasibility_audit_v1.md | git: tracked | mode: 100644 | size: 34,37 KB (35.194 B) | type: .md | lines: 505
|   |   |-- [FILE] JMP_NC_pilot_HN_POS_resolution_report_v1.md | git: tracked | mode: 100644 | size: 13,76 KB (14.089 B) | type: .md | lines: 365
|   |   |-- [FILE] JMP_NC_pilot_JAX_optimizer_benchmark_report_v1.md | git: tracked | mode: 100644 | size: 12,16 KB (12.450 B) | type: .md | lines: 320
|   |   |-- [FILE] JMP_NC_pilot_JAX_validation_estimation_report_v1.md | git: tracked | mode: 100644 | size: 14,76 KB (15.115 B) | type: .md | lines: 300
|   |   |-- [FILE] JMP_NC_pilot_loc4_precompute_augmentation_report_v1.md | git: tracked | mode: 100644 | size: 12,14 KB (12.427 B) | type: .md | lines: 326
|   |   |-- [FILE] JMP_NC_pilot_normalization_rebuild_report_v1.md | git: tracked | mode: 100644 | size: 13,37 KB (13.690 B) | type: .md | lines: 329
|   |   |-- [FILE] JMP_NC_pilot_optimizer_protocol_diagnostic_report_v1.md | git: tracked | mode: 100644 | size: 13,74 KB (14.073 B) | type: .md | lines: 347
|   |   |-- [FILE] JMP_NC_pilot_post_em_merge_report_v1.md | git: tracked | mode: 100644 | size: 16,15 KB (16.539 B) | type: .md | lines: 464
|   |   |-- [FILE] JMP_NC_pilot_precompute_readiness_report_v1.md | git: tracked | mode: 100644 | size: 16,57 KB (16.965 B) | type: .md | lines: 436
|   |   |-- [FILE] JMP_NC_pilot_precompute_report_v1.md | git: tracked | mode: 100644 | size: 15,34 KB (15.708 B) | type: .md | lines: 391
|   |   |-- [FILE] JMP_NC_pilot_precompute_report_v2.md | git: tracked | mode: 100644 | size: 18,04 KB (18.475 B) | type: .md | lines: 477
|   |   |-- [FILE] JMP_NC_pilot_scaled_JAX_validation_report_v1.md | git: tracked | mode: 100644 | size: 16,03 KB (16.412 B) | type: .md | lines: 337
|   |   |-- [FILE] JMP_NC_pilot_stage1_4_build_report_v1.md | git: tracked | mode: 100644 | size: 27,55 KB (28.213 B) | type: .md | lines: 642
|   |   |-- [FILE] JMP_NC_pilot_stage5_euromod_build_report_v1.md | git: tracked | mode: 100644 | size: 21,31 KB (21.818 B) | type: .md | lines: 453
|   |   |-- [FILE] JMP_NC_pilot_stage5_strategy_v2_build_report_v1.md | git: tracked | mode: 100644 | size: 21,81 KB (22.333 B) | type: .md | lines: 501
|   |   |-- [FILE] JMP_NC_pilot_vectorized_likelihood_cleanup_validation_v1.md | git: tracked | mode: 100644 | size: 6,20 KB (6.344 B) | type: .md | lines: 186
|   |   |-- [FILE] JMP_NC_pilot_vectorized_likelihood_equivalence_v1.md | git: tracked | mode: 100644 | size: 8,30 KB (8.502 B) | type: .md | lines: 199
|   |   \-- [FILE] JMP_NC_pilot_vectorized_likelihood_equivalence_v2.md | git: tracked | mode: 100644 | size: 13,05 KB (13.361 B) | type: .md | lines: 360
|   |-- [DIR] P3a/
|   |   |-- [DIR] gsurv2/
|   |   |   |-- [FILE] JMP_GSURv2_external_file_remediation_report_v1.md | git: tracked | mode: 100644 | size: 17,00 KB (17.408 B) | type: .md | lines: 385
|   |   |   |-- [FILE] JMP_GSURv2_MNL_rebuild_correction_report_v1.md | git: tracked | mode: 100644 | size: 9,66 KB (9.892 B) | type: .md | lines: 221
|   |   |   |-- [FILE] JMP_GSURv2_MNL_rebuild_report_v2.md | git: tracked | mode: 100644 | size: 21,78 KB (22.306 B) | type: .md | lines: 586
|   |   |   |-- [FILE] JMP_GSURv2_multi_year_extension_validation_report_v1.md | git: tracked | mode: 100644 | size: 14,04 KB (14.375 B) | type: .md | lines: 353
|   |   |   |-- [FILE] JMP_GSURv2_script_remediation_static_validation_v1.md | git: tracked | mode: 100644 | size: 5,09 KB (5.209 B) | type: .md | lines: 164
|   |   |   |-- [FILE] RURO_GSUR_v2_stageA_lookup_validation_report_v1.md | git: tracked | mode: 100644 | size: 14,57 KB (14.921 B) | type: .md | lines: 342
|   |   |   \-- [FILE] RURO_GSUR_v2_stageA_MNL_rebuild_report_v1.md | git: tracked | mode: 100644 | size: 11,98 KB (12.264 B) | type: .md | lines: 328
|   |   |-- [DIR] multi_year_stage_M1/
|   |   |   |-- [FILE] JMP_multi_year_EUROMOD_output_readiness_v1.md | git: tracked | mode: 100644 | size: 6,56 KB (6.722 B) | type: .md | lines: 128
|   |   |   |-- [FILE] JMP_multi_year_external_assets_inventory_v1.md | git: tracked | mode: 100644 | size: 7,10 KB (7.271 B) | type: .md | lines: 123
|   |   |   |-- [FILE] JMP_multi_year_feasibility_audit_addendum_v2.md | git: tracked | mode: 100644 | size: 14,16 KB (14.503 B) | type: .md | lines: 204
|   |   |   |-- [FILE] JMP_multi_year_feasibility_audit_v1.md | git: tracked | mode: 100644 | size: 27,67 KB (28.329 B) | type: .md | lines: 452
|   |   |   |-- [FILE] JMP_multi_year_single_year_MNL_readiness_v1.md | git: tracked | mode: 100644 | size: 9,35 KB (9.572 B) | type: .md | lines: 179
|   |   |   |-- [FILE] JMP_multi_year_stage_M1_execution_readiness_v1.md | git: tracked | mode: 100644 | size: 3,93 KB (4.029 B) | type: .md | lines: 124
|   |   |   |-- [FILE] JMP_multi_year_stage_M1_P3a_full_execution_report_v1.md | git: tracked | mode: 100644 | size: 21,11 KB (21.613 B) | type: .md | lines: 491
|   |   |   |-- [FILE] JMP_multi_year_stage_M1_readiness_addendum_v2.md | git: tracked | mode: 100644 | size: 9,14 KB (9.361 B) | type: .md | lines: 144
|   |   |   |-- [FILE] JMP_multi_year_stage_M1_static_validation_report_v3.md | git: tracked | mode: 100644 | size: 6,53 KB (6.682 B) | type: .md | lines: 223
|   |   |   |-- [FILE] JMP_single_year_2016_local_mirror_report_v1.md | git: tracked | mode: 100644 | size: 14,39 KB (14.739 B) | type: .md | lines: 241
|   |   |   |-- [FILE] JMP_single_year_consolidated_readiness_verdict_v1.md | git: tracked | mode: 100644 | size: 12,52 KB (12.819 B) | type: .md | lines: 211
|   |   |   |-- [FILE] JMP_single_year_FR2015_gsurY2014_rebuild_report_v1.md | git: tracked | mode: 100644 | size: 16,37 KB (16.763 B) | type: .md | lines: 380
|   |   |   |-- [FILE] JMP_single_year_FR2015_replication_addendum_v1.md | git: tracked | mode: 100644 | size: 18,00 KB (18.433 B) | type: .md | lines: 384
|   |   |   |-- [FILE] JMP_single_year_FR2015_replication_report_v1.md | git: tracked | mode: 100644 | size: 18,31 KB (18.745 B) | type: .md | lines: 487
|   |   |   |-- [FILE] JMP_single_year_FR2016_gsurY2015_rebuild_report_v1.md | git: tracked | mode: 100644 | size: 20,79 KB (21.285 B) | type: .md | lines: 421
|   |   |   |-- [FILE] JMP_single_year_FR2017_replication_report_v1.md | git: tracked | mode: 100644 | size: 28,33 KB (29.009 B) | type: .md | lines: 644
|   |   |   |-- [FILE] JMP_stage_M1_P3a_GSURv2_stacking_execution_report_v1.md | git: tracked | mode: 100644 | size: 19,17 KB (19.627 B) | type: .md | lines: 402
|   |   |   \-- [FILE] M1_identity_validation_summary.md | git: tracked | mode: 100644 | size: 1,73 KB (1.768 B) | type: .md | lines: 76
|   |   |-- [DIR] pooled_P3a/
|   |   |   |-- [FILE] JMP_pooled_P3a_corrected_region_estimation_report_v1.md | git: tracked | mode: 100644 | size: 43,74 KB (44.788 B) | type: .md | lines: 745
|   |   |   |-- [FILE] JMP_pooled_P3a_estimation_preflight_report_v1.md | git: tracked | mode: 100644 | size: 16,77 KB (17.170 B) | type: .md | lines: 386
|   |   |   |-- [FILE] JMP_pooled_P3a_estimation_preflight_report_v2.md | git: tracked | mode: 100644 | size: 6,59 KB (6.744 B) | type: .md | lines: 163
|   |   |   |-- [FILE] JMP_pooled_P3a_estimation_report_v1.md | git: tracked | mode: 100644 | size: 23,97 KB (24.542 B) | type: .md | lines: 588
|   |   |   |-- [FILE] JMP_pooled_P3a_estimation_report_v2.md | git: tracked | mode: 100644 | size: 28,85 KB (29.541 B) | type: .md | lines: 576
|   |   |   |-- [FILE] JMP_pooled_P3a_post_estimation_diagnostics_report_v1.md | git: tracked | mode: 100644 | size: 34,62 KB (35.448 B) | type: .md | lines: 373
|   |   |   |-- [FILE] JMP_pooled_P3a_region_dummy_nonident_diagnostic_v1.md | git: tracked | mode: 100644 | size: 32,65 KB (33.429 B) | type: .md | lines: 582
|   |   |   |-- [FILE] JMP_pooled_P3a_region_dummy_nonident_diagnostic_v2.md | git: tracked | mode: 100644 | size: 12,22 KB (12.517 B) | type: .md | lines: 209
|   |   |   \-- [FILE] RURO_occ_P3a_pooled_gate_A_parse_report_v1.md | git: tracked | mode: 100644 | size: 15,59 KB (15.965 B) | type: .md | lines: 353
|   |   \-- [DIR] single_year_baseline/
|   |       |-- [DIR] M0/
|   |       |   |-- [FILE] RURO_occ_M0_verdict_v1.md | git: tracked | mode: 100644 | size: 25,49 KB (26.100 B) | type: .md | lines: 532
|   |       |   |-- [FILE] RURO_ruro_occ_M0_baseline_decision_v1.md | git: tracked | mode: 100644 | size: 25,49 KB (26.100 B) | type: .md | lines: 532
|   |       |   |-- [FILE] RURO_ruro_occ_M0_full_rebuild_report_v1.md | git: tracked | mode: 100644 | size: 24,98 KB (25.577 B) | type: .md | lines: 614
|   |       |   |-- [FILE] RURO_ruro_occ_M0_mnl_validation_report_v1.md | git: tracked | mode: 100644 | size: 9,58 KB (9.812 B) | type: .md | lines: 242
|   |       |   |-- [FILE] RURO_ruro_occ_M0_proposal_adequacy_diag_v1.md | git: tracked | mode: 100644 | size: 9,72 KB (9.954 B) | type: .md | lines: 169
|   |       |   |-- [FILE] RURO_ruro_occ_M0_rebuild_canary_report_v1.md | git: tracked | mode: 100644 | size: 10,40 KB (10.645 B) | type: .md | lines: 196
|   |       |   \-- [FILE] RURO_ruro_occ_M0_triage_memo_v1.md | git: tracked | mode: 100644 | size: 26,22 KB (26.850 B) | type: .md | lines: 500
|   |       |-- [DIR] M0a/
|   |       |   |-- [FILE] RURO_occ_M0a_clean_verdict_v1.md | git: tracked | mode: 100644 | size: 36,23 KB (37.101 B) | type: .md | lines: 808
|   |       |   |-- [FILE] RURO_occ_M0a_simplification_plan_v1.md | git: tracked | mode: 100644 | size: 21,47 KB (21.982 B) | type: .md | lines: 529
|   |       |   \-- [FILE] RURO_ruro_occ_M0a_clean_participation_diag_v1.md | git: tracked | mode: 100644 | size: 6,84 KB (7.004 B) | type: .md | lines: 139
|   |       |-- [DIR] M0b/
|   |       |   |-- [FILE] RURO_occ_M0b_gate_A_parse_report_v1.md | git: tracked | mode: 100644 | size: 5,68 KB (5.812 B) | type: .md | lines: 180
|   |       |   |-- [FILE] RURO_occ_M0b_smoke_test_report_v1.md | git: tracked | mode: 100644 | size: 6,61 KB (6.767 B) | type: .md | lines: 184
|   |       |   |-- [FILE] RURO_occ_M0b1_wage_pathology_diagnostic_v1.md | git: tracked | mode: 100644 | size: 8,89 KB (9.106 B) | type: .md | lines: 209
|   |       |   |-- [FILE] RURO_occ_M0b2_estimation_report_v1.md | git: tracked | mode: 100644 | size: 22,21 KB (22.748 B) | type: .md | lines: 438
|   |       |   \-- [FILE] RURO_occ_M0b2_multistart_report_v1.md | git: tracked | mode: 100644 | size: 13,06 KB (13.378 B) | type: .md | lines: 259
|   |       |-- [DIR] M0c/
|   |       |   |-- [FILE] RURO_occ_M0c_b_estimation_report_v1.md | git: tracked | mode: 100644 | size: 8,81 KB (9.020 B) | type: .md | lines: 200
|   |       |   |-- [FILE] RURO_occ_M0c_b_gate_A_parse_report_v1.md | git: tracked | mode: 100644 | size: 4,73 KB (4.848 B) | type: .md | lines: 177
|   |       |   |-- [FILE] RURO_occ_M0c_b2_estimation_report_v1.md | git: tracked | mode: 100644 | size: 15,26 KB (15.623 B) | type: .md | lines: 339
|   |       |   |-- [FILE] RURO_occ_M0c_b2_gate_A_parse_report_v1.md | git: tracked | mode: 100644 | size: 1,41 KB (1.444 B) | type: .md | lines: 42
|   |       |   |-- [FILE] RURO_occ_M0c_b2_GSURv2_estimation_input_check_v1.md | git: tracked | mode: 100644 | size: 7,02 KB (7.188 B) | type: .md | lines: 174
|   |       |   |-- [FILE] RURO_occ_M0c_b2_GSURv2_estimation_report_v1.md | git: tracked | mode: 100644 | size: 20,10 KB (20.579 B) | type: .md | lines: 471
|   |       |   |-- [FILE] RURO_occ_M0c_b2_GSURv2_post_estimation_diagnostics_v1.md | git: tracked | mode: 100644 | size: 30,13 KB (30.851 B) | type: .md | lines: 631
|   |       |   \-- [FILE] RURO_occ_M0c_design_memo_v1.md | git: tracked | mode: 100644 | size: 27,67 KB (28.331 B) | type: .md | lines: 656
|   |       \-- [DIR] M1/
|   |           |-- [FILE] RURO_occ_M1_clean_estimation_report_v1.md | git: tracked | mode: 100644 | size: 16,26 KB (16.649 B) | type: .md | lines: 288
|   |           |-- [FILE] RURO_occ_M1_clean_gate_A_parse_report_v1.md | git: tracked | mode: 100644 | size: 5,52 KB (5.649 B) | type: .md | lines: 133
|   |           |-- [FILE] RURO_occ_M1_clean_post_estimation_diagnostics_v1.md | git: tracked | mode: 100644 | size: 32,50 KB (33.279 B) | type: .md | lines: 699
|   |           |-- [FILE] RURO_occ_M1_clean_standard_post_estimation_diagnostics_v1.md | git: tracked | mode: 100644 | size: 26,70 KB (27.339 B) | type: .md | lines: 542
|   |           |-- [FILE] RURO_occ_M1_clean_supplementary_diagnostics_v1.md | git: tracked | mode: 100644 | size: 4,23 KB (4.333 B) | type: .md | lines: 121
|   |           |-- [FILE] RURO_occ_M1_naive_estimation_report_v1.md | git: tracked | mode: 100644 | size: 16,17 KB (16.560 B) | type: .md | lines: 304
|   |           |-- [FILE] RURO_occ_M1_naive_gate_A_parse_report_v1.md | git: tracked | mode: 100644 | size: 9,86 KB (10.095 B) | type: .md | lines: 108
|   |           |-- [FILE] RURO_occ_M1_naive_post_estimation_diagnostics_v1.md | git: tracked | mode: 100644 | size: 29,36 KB (30.061 B) | type: .md | lines: 491
|   |           \-- [FILE] RURO_occ_M1_naive_supplementary_diagnostics_v1.md | git: tracked | mode: 100644 | size: 15,17 KB (15.532 B) | type: .md | lines: 311
|   |-- [DIR] pilot/
|   |   \-- [DIR] nc_2016_couples/
|   |       \-- [DIR] diagnostic_rerun_v1/
|   |           |-- [DIR] start_1_warm_P3a/
|   |           |   |-- [FILE] estimation_result.json | git: tracked | mode: 100644 | size: 3,05 KB (3.121 B) | type: .json | lines: 98
|   |           |   |-- [FILE] solver.log | git: tracked | mode: 100644 | size: 4,18 KB (4.277 B) | type: .log | lines: 92
|   |           |   \-- [FILE] solver.lst | git: tracked | mode: 100644 | size: 8,01 KB (8.200 B) | type: .lst | lines: 154
|   |           |-- [DIR] start_2_yaml_defaults/
|   |           |   |-- [FILE] estimation_result2.json | git: tracked | mode: 100644 | size: 3,01 KB (3.080 B) | type: .json | lines: 98
|   |           |   |-- [FILE] solver2.log | git: tracked | mode: 100644 | size: 4,19 KB (4.287 B) | type: .log | lines: 92
|   |           |   \-- [FILE] solver2.lst | git: tracked | mode: 100644 | size: 8,01 KB (8.205 B) | type: .lst | lines: 154
|   |           \-- [FILE] diagnostic_rerun_summary.json | git: tracked | mode: 100644 | size: 13,47 KB (13.797 B) | type: .json | lines: 480
|   |-- [FILE] _canary_ruro_occ_M0.py | git: tracked | mode: 100644 | size: 13,67 KB (14.003 B) | type: .py | lines: 274
|   |-- [FILE] _canary_ruro_occ_M0_results.json | git: tracked | mode: 100644 | size: 2,47 KB (2.525 B) | type: .json | lines: 120
|   |-- [FILE] _M0a_clean_post_est_fit_check.json | git: tracked | mode: 100644 | size: 866 B (866 B) | type: .json | lines: 26
|   |-- [FILE] _M0a_clean_post_est_fit_check.py | git: tracked | mode: 100644 | size: 2,01 KB (2.058 B) | type: .py | lines: 48
|   |-- [FILE] _M0a_clean_spec_check.py | git: tracked | mode: 100644 | size: 10,65 KB (10.905 B) | type: .py | lines: 280
|   |-- [FILE] _M0b_smoke_test.py | git: tracked | mode: 100644 | size: 17,18 KB (17.596 B) | type: .py | lines: 428
|   |-- [FILE] _M0b2_multistart_runner.py | git: tracked | mode: 100644 | size: 19,47 KB (19.939 B) | type: .py | lines: 498
|   |-- [FILE] _M0b2_multistart_summary.json | git: tracked | mode: 100644 | size: 8,33 KB (8.534 B) | type: .json | lines: 209
|   |-- [FILE] _M0c_b2_GSURv2_perturbed_init_s42.json | git: tracked | mode: 100644 | size: 1,79 KB (1.833 B) | type: .json | lines: 49
|   |-- [FILE] _M0c_b2_GSURv2_perturbed_init_s42_wrapped.json | git: tracked | mode: 100644 | size: 2,15 KB (2.198 B) | type: .json | lines: 55
|   |-- [FILE] _M0c_b2_multistart_runner.py | git: tracked | mode: 100644 | size: 17,26 KB (17.678 B) | type: .py | lines: 435
|   |-- [FILE] _M0c_b2_multistart_summary.json | git: tracked | mode: 100644 | size: 8,29 KB (8.488 B) | type: .json | lines: 203
|   |-- [FILE] _M1_clean_perturbed_init_s42_wrapped.json | git: tracked | mode: 100644 | size: 7,26 KB (7.438 B) | type: .json | lines: 177
|   |-- [FILE] _M1_naive_perturbed_init_s42.json | git: tracked | mode: 100644 | size: 7,39 KB (7.565 B) | type: .json | lines: 180
|   |-- [FILE] _M1_naive_warm_start_s1.json | git: tracked | mode: 100644 | size: 7,43 KB (7.612 B) | type: .json | lines: 180
|   |-- [FILE] _participation_diag_ruro_occ_M0a_clean.json | git: tracked | mode: 100644 | size: 12,24 KB (12.538 B) | type: .json | lines: 347
|   |-- [FILE] _participation_diag_ruro_occ_M0a_clean.py | git: tracked | mode: 100644 | size: 44,10 KB (45.155 B) | type: .py | lines: 1.026
|   |-- [FILE] _proposal_adequacy_diag_ruro_occ_M0.json | git: tracked | mode: 100644 | size: 26,47 KB (27.107 B) | type: .json | lines: 779
|   |-- [FILE] _proposal_adequacy_diag_ruro_occ_M0.py | git: tracked | mode: 100644 | size: 38,21 KB (39.122 B) | type: .py | lines: 908
|   |-- [FILE] _step2_euromod.log | git: tracked | mode: 100644 | size: 772 B (772 B) | type: .log | lines: 12
|   |-- [FILE] _step3_mnl_prep.log | git: tracked | mode: 100644 | size: 6,91 KB (7.079 B) | type: .log | lines: 218
|   |-- [FILE] _validation_ruro_occ_M0.json | git: tracked | mode: 100644 | size: 4,91 KB (5.023 B) | type: .json | lines: 200
|   |-- [FILE] _validation_ruro_occ_M0.py | git: tracked | mode: 100644 | size: 8,46 KB (8.659 B) | type: .py | lines: 182
|   |-- [FILE] _wage_pathology_diag_ruro_occ_M0b1.json | git: tracked | mode: 100644 | size: 10,62 KB (10.876 B) | type: .json | lines: 284
|   |-- [FILE] _wage_pathology_diag_ruro_occ_M0b1.py | git: tracked | mode: 100644 | size: 20,08 KB (20.558 B) | type: .py | lines: 447
|   |-- [FILE] JMP_docs_results_cleanup_manifest_v1.csv | git: tracked | mode: 100644 | size: 4,28 KB (4.384 B) | type: .csv | lines: 16
|   |-- [FILE] JMP_docs_results_cleanup_second_pass_manifest_v1.csv | git: tracked | mode: 100644 | size: 19,35 KB (19.818 B) | type: .csv | lines: 107
|   |-- [FILE] JMP_multi_year_cleaning_attrition_table_v1.csv | git: tracked | mode: 100644 | size: 3,25 KB (3.332 B) | type: .csv | lines: 52
|   |-- [FILE] JMP_multi_year_cleaning_attrition_table_v1.tex | git: tracked | mode: 100644 | size: 4,21 KB (4.311 B) | type: .tex | lines: 69
|   |-- [FILE] JMP_multi_year_descriptive_stats_v1.csv | git: tracked | mode: 100644 | size: 3,49 KB (3.577 B) | type: .csv | lines: 16
|   |-- [FILE] JMP_multi_year_descriptive_stats_v1.tex | git: tracked | mode: 100644 | size: 2,85 KB (2.917 B) | type: .tex | lines: 29
|   |-- [FILE] JMP_pooled_P3a_corrected_orchestrator_summary.json | git: tracked | mode: 100644 | size: 2,22 KB (2.271 B) | type: .json | lines: 28
|   |-- [FILE] JMP_pooled_P3a_corrected_S4_wald.json | git: tracked | mode: 100644 | size: 1,76 KB (1.803 B) | type: .json | lines: 75
|   |-- [FILE] JMP_pooled_P3a_corrected_S5_S8_hessian_diag.json | git: tracked | mode: 100644 | size: 4,29 KB (4.388 B) | type: .json | lines: 180
|   |-- [FILE] JMP_pooled_P3a_corrected_S6_preference_comparison.json | git: tracked | mode: 100644 | size: 14,58 KB (14.930 B) | type: .json | lines: 511
|   |-- [FILE] JMP_pooled_P3a_corrected_S6_theta_c_singles_LL_profile.json | git: tracked | mode: 100644 | size: 3,14 KB (3.219 B) | type: .json | lines: 123
|   |-- [FILE] JMP_pooled_P3a_corrected_start1_cluster_robust_se.json | git: tracked | mode: 100644 | size: 8,55 KB (8.760 B) | type: .json | lines: 335
|   |-- [FILE] JMP_pooled_P3a_corrected_start1_cluster_robust_se_vcv.npy | git: tracked | mode: 100644 | size: 23,76 KB (24.328 B) | type: .npy | lines: N/A (binary)
|   |-- [FILE] JMP_pooled_P3a_corrected_start2_cluster_robust_se.json | git: tracked | mode: 100644 | size: 8,57 KB (8.775 B) | type: .json | lines: 335
|   |-- [FILE] JMP_pooled_P3a_corrected_start2_cluster_robust_se_vcv.npy | git: tracked | mode: 100644 | size: 23,76 KB (24.328 B) | type: .npy | lines: N/A (binary)
|   |-- [FILE] JMP_pooled_P3a_corrected_start3_cluster_robust_se.json | git: tracked | mode: 100644 | size: 8,55 KB (8.756 B) | type: .json | lines: 335
|   |-- [FILE] JMP_pooled_P3a_corrected_start3_cluster_robust_se_vcv.npy | git: tracked | mode: 100644 | size: 23,76 KB (24.328 B) | type: .npy | lines: N/A (binary)
|   |-- [FILE] JMP_pooled_P3a_corrected_start3_perturbed_init.json | git: tracked | mode: 100644 | size: 2,62 KB (2.683 B) | type: .json | lines: 119
|   |-- [FILE] JMP_pooled_P3a_corrected_true_hessian_54x54.npy | git: tracked | mode: 100644 | size: 22,91 KB (23.456 B) | type: .npy | lines: N/A (binary)
|   |-- [FILE] JMP_pooled_P3a_orchestrator.log | git: tracked | mode: 100644 | size: 95,66 KB (97.960 B) | type: .log | lines: 1.653
|   |-- [FILE] JMP_pooled_P3a_orchestrator_summary.json | git: tracked | mode: 100644 | size: 2,22 KB (2.271 B) | type: .json | lines: 28
|   |-- [FILE] JMP_pooled_P3a_start1_cluster_robust_se.json | git: tracked | mode: 100644 | size: 8,61 KB (8.814 B) | type: .json | lines: 335
|   |-- [FILE] JMP_pooled_P3a_start1_cluster_robust_se_vcv.npy | git: tracked | mode: 100644 | size: 23,76 KB (24.328 B) | type: .npy | lines: N/A (binary)
|   |-- [FILE] JMP_pooled_P3a_start2_cluster_robust_se.json | git: tracked | mode: 100644 | size: 8,50 KB (8.703 B) | type: .json | lines: 335
|   |-- [FILE] JMP_pooled_P3a_start2_cluster_robust_se_vcv.npy | git: tracked | mode: 100644 | size: 23,76 KB (24.328 B) | type: .npy | lines: N/A (binary)
|   |-- [FILE] JMP_pooled_P3a_start3_cluster_robust_se.json | git: tracked | mode: 100644 | size: 8,60 KB (8.804 B) | type: .json | lines: 335
|   |-- [FILE] JMP_pooled_P3a_start3_cluster_robust_se_vcv.npy | git: tracked | mode: 100644 | size: 23,76 KB (24.328 B) | type: .npy | lines: N/A (binary)
|   |-- [FILE] JMP_pooled_P3a_start3_perturbed_init.json | git: tracked | mode: 100644 | size: 2,61 KB (2.674 B) | type: .json | lines: 119
|   |-- [FILE] JMP_pooled_P3a_v7_interface_check_placeholder_theta.json | git: tracked | mode: 100644 | size: 7,59 KB (7.771 B) | type: .json | lines: 337
|   |-- [FILE] JMP_pooled_P3a_v7_interface_placeholder.json | git: tracked | mode: 100644 | size: 961 B (961 B) | type: .json | lines: 64
|   |-- [FILE] M1_cluster_key_check_20260520_223716.csv | git: tracked | mode: 100644 | size: 321 B (321 B) | type: .csv | lines: 7
|   |-- [FILE] M1_cpi_harmonisation_check_20260520_223658.csv | git: tracked | mode: 100644 | size: 542 B (542 B) | type: .csv | lines: 4
|   |-- [FILE] m1_diag_run.log | git: tracked | mode: 100644 | size: 4,46 KB (4.566 B) | type: .log | lines: N/A (binary)
|   |-- [FILE] M1_raw_id_preservation_check_20260520_223909.csv | git: tracked | mode: 100644 | size: 138 B (138 B) | type: .csv | lines: 5
|   |-- [FILE] M1_stacked_id_manifest_20260520_223909.csv | git: tracked | mode: 100644 | size: 968 B (968 B) | type: .csv | lines: 4
|   |-- [FILE] M1_validation_summary_20260520_223909.csv | git: tracked | mode: 100644 | size: 1,89 KB (1.940 B) | type: .csv | lines: 10
|   |-- [FILE] MOVE_MANIFEST_2026-05-27_results.md | git: tracked | mode: 100644 | size: 7,39 KB (7.564 B) | type: .md | lines: 114
|   |-- [FILE] rename_stijn_to_ruro_manifest_20260513T144955Z.csv | git: tracked | mode: 100644 | size: 114,44 KB (117.188 B) | type: .csv | lines: 846
|   |-- [FILE] rename_stijn_to_ruro_manifest_20260513T145355Z.csv | git: tracked | mode: 100644 | size: 114,70 KB (117.449 B) | type: .csv | lines: 848
|   |-- [FILE] rename_stijn_to_ruro_manifest_20260513T145806Z.csv | git: tracked | mode: 100644 | size: 114,97 KB (117.729 B) | type: .csv | lines: 848
|   |-- [FILE] rename_stijn_to_ruro_manifest_20260520T103345Z.csv | git: tracked | mode: 100644 | size: 2,89 KB (2.963 B) | type: .csv | lines: 20
|   |-- [FILE] rename_stijn_to_ruro_manifest_20260520T103438Z.csv | git: tracked | mode: 100644 | size: 2,89 KB (2.963 B) | type: .csv | lines: 20
|   |-- [FILE] rename_stijn_to_ruro_manifest_20260520T103853Z.csv | git: tracked | mode: 100644 | size: 2,89 KB (2.963 B) | type: .csv | lines: 20
|   |-- [FILE] results_files_structure.md | git: tracked | mode: 100644 | size: 25,64 KB (26.258 B) | type: .md | lines: N/A (binary)
|   |-- [FILE] RURO_occ_M1_clean_hessian_region_block_20260518_125924.csv | git: tracked | mode: 100644 | size: 1,15 KB (1.176 B) | type: .csv | lines: 9
|   |-- [FILE] RURO_occ_M1_clean_vcv_region_block_20260518_125924.csv | git: tracked | mode: 100644 | size: 926 B (926 B) | type: .csv | lines: 8
|   |-- [FILE] RURO_occ_M1_naive_hessian_gsur_educ_region_block_20260518_170632.csv | git: tracked | mode: 100644 | size: 1,42 KB (1.458 B) | type: .csv | lines: 10
|   |-- [FILE] RURO_occ_M1_naive_vcv_educ_gsur_region_block_20260518_170632.csv | git: tracked | mode: 100644 | size: 1,44 KB (1.472 B) | type: .csv | lines: 10
|   \-- [FILE] RURO_occ_M1_naive_vcv_region_block_20260518_170632.csv | git: tracked | mode: 100644 | size: 926 B (926 B) | type: .csv | lines: 8
|-- [DIR] scripts/
|   |-- [DIR] archive/
|   |   |-- [DIR] backups_2025_12/
|   |   |   |-- [FILE] estimation_spec.yaml.backup | git: tracked | mode: 100644 | size: 6,83 KB (6.995 B) | type: .backup | lines: 199
|   |   |   |-- [FILE] estimation_spec_loc_empirical.yaml.backup | git: tracked | mode: 100644 | size: 7,04 KB (7.209 B) | type: .backup | lines: 225
|   |   |   \-- [FILE] RURO_estimate_FR.py.backup_20251216_143415 | git: tracked | mode: 100644 | size: 239,16 KB (244.899 B) | type: .backup_20251216_143415 | lines: 6.169
|   |   |-- [DIR] experimental/
|   |   |   |-- [FILE] run_draws_euromod_interactive.py | git: tracked | mode: 100644 | size: 4,60 KB (4.708 B) | type: .py | lines: 140
|   |   |   |-- [FILE] run_full_pipeline_interactive.py | git: tracked | mode: 100644 | size: 16,51 KB (16.903 B) | type: .py | lines: 464
|   |   |   |-- [FILE] run_pipeline_explicit.py | git: tracked | mode: 100644 | size: 29,85 KB (30.565 B) | type: .py | lines: 711
|   |   |   |-- [FILE] run_pipeline_memory_only.py | git: tracked | mode: 100644 | size: 14,73 KB (15.079 B) | type: .py | lines: 400
|   |   |   \-- [FILE] simple.py | git: tracked | mode: 100644 | size: 1,07 KB (1.095 B) | type: .py | lines: 36
|   |   |-- [DIR] fixes/
|   |   |   |-- [FILE] recompute_se.py | git: tracked | mode: 100644 | size: 4,06 KB (4.160 B) | type: .py | lines: 136
|   |   |   \-- [FILE] rerun_post_estimation.py | git: tracked | mode: 100644 | size: 3,41 KB (3.496 B) | type: .py | lines: 109
|   |   |-- [DIR] old_data_prep/
|   |   |   \-- [FILE] data_prep2.py | git: tracked | mode: 100644 | size: 65,11 KB (66.677 B) | type: .py | lines: 1.585
|   |   |-- [DIR] old_ruro_pre_enhanced/
|   |   |   |-- [FILE] full_RURO.py | git: tracked | mode: 100644 | size: 54,78 KB (56.095 B) | type: .py | lines: 1.486
|   |   |   |-- [FILE] inspect_RURO_fr_2021.py | git: tracked | mode: 100644 | size: 908 B (908 B) | type: .py | lines: 37
|   |   |   |-- [FILE] run_fr_2021_prep.py | git: tracked | mode: 100644 | size: 864 B (864 B) | type: .py | lines: 38
|   |   |   |-- [FILE] RURO_boxcox_group_opportunities.py | git: tracked | mode: 100644 | size: 43,83 KB (44.878 B) | type: .py | lines: 1.255
|   |   |   |-- [FILE] RURO_boxcox_mnl.py | git: tracked | mode: 100644 | size: 25,81 KB (26.431 B) | type: .py | lines: 766
|   |   |   |-- [FILE] RURO_gpt.py | git: tracked | mode: 100644 | size: 38,53 KB (39.455 B) | type: .py | lines: 1.113
|   |   |   \-- [FILE] trim_mnl_dataset.py | git: tracked | mode: 100644 | size: 3,60 KB (3.682 B) | type: .py | lines: 131
|   |   |-- [DIR] rum_approach/
|   |   |   \-- [DIR] RUM/
|   |   |       |-- [FILE] analyzer_runner.py | git: tracked | mode: 100644 | size: 1,86 KB (1.900 B) | type: .py | lines: 53
|   |   |       |-- [FILE] bio_boxcox.py | git: tracked | mode: 100644 | size: 21,05 KB (21.553 B) | type: .py | lines: 546
|   |   |       |-- [FILE] biotest.py | git: tracked | mode: 100644 | size: 2,09 KB (2.145 B) | type: .py | lines: 76
|   |   |       |-- [FILE] combine_years_for_dcm.py | git: tracked | mode: 100644 | size: 8,16 KB (8.351 B) | type: .py | lines: 207
|   |   |       |-- [FILE] data_prep.py | git: tracked | mode: 100644 | size: 20,95 KB (21.457 B) | type: .py | lines: 621
|   |   |       |-- [FILE] DCM1.py | git: tracked | mode: 100644 | size: 31,80 KB (32.559 B) | type: .py | lines: 884
|   |   |       |-- [FILE] DCM1_boxcox.py | git: tracked | mode: 100644 | size: 49,45 KB (50.640 B) | type: .py | lines: 1.303
|   |   |       |-- [FILE] DCM1_boxcox_gender_split.py | git: tracked | mode: 100644 | size: 4,48 KB (4.584 B) | type: .py | lines: 137
|   |   |       |-- [FILE] DCM1_gamspy.py | git: tracked | mode: 100644 | size: 22,06 KB (22.585 B) | type: .py | lines: 573
|   |   |       |-- [FILE] DCM2_gamspy.py | git: tracked | mode: 100644 | size: 58,75 KB (60.156 B) | type: .py | lines: 1.575
|   |   |       |-- [FILE] DCM2_gamspy_gender_split.py | git: tracked | mode: 100644 | size: 4,29 KB (4.394 B) | type: .py | lines: 112
|   |   |       |-- [FILE] MLE_dcm.py | git: tracked | mode: 100644 | size: 16,96 KB (17.362 B) | type: .py | lines: 451
|   |   |       |-- [FILE] old_biogeme.py | git: tracked | mode: 100644 | size: 20,35 KB (20.834 B) | type: .py | lines: 670
|   |   |       |-- [FILE] old_prep.py | git: tracked | mode: 100644 | size: 30,90 KB (31.644 B) | type: .py | lines: 879
|   |   |       |-- [FILE] process2_py.py | git: tracked | mode: 100644 | size: 17,20 KB (17.616 B) | type: .py | lines: 430
|   |   |       |-- [FILE] run_de_multi_year.py | git: tracked | mode: 100644 | size: 2,93 KB (3.003 B) | type: .py | lines: 85
|   |   |       |-- [FILE] run_euromod.py | git: tracked | mode: 100644 | size: 3,40 KB (3.486 B) | type: .py | lines: 112
|   |   |       |-- [FILE] scenarios.py | git: tracked | mode: 100644 | size: 30,77 KB (31.506 B) | type: .py | lines: 821
|   |   |       |-- [FILE] scenarios_de.py | git: tracked | mode: 100644 | size: 5,08 KB (5.205 B) | type: .py | lines: 151
|   |   |       |-- [FILE] set_biogeme_env.py | git: tracked | mode: 100644 | size: 92 B (92 B) | type: .py | lines: 4
|   |   |       \-- [FILE] train_mnl.py | git: tracked | mode: 100644 | size: 1,27 KB (1.296 B) | type: .py | lines: 49
|   |   |-- [FILE] README.md | git: tracked | mode: 100644 | size: 291 B (291 B) | type: .md | lines: 13
|   |   \-- [FILE] run_gamspy.ps1 | git: tracked | mode: 100644 | size: 1,32 KB (1.350 B) | type: .ps1 | lines: 19
|   |-- [DIR] bpool/
|   |   |-- [DIR] specs/
|   |   |   |-- [FILE] estimation_spec_bpool_p3a_v1.yaml | git: tracked | mode: 100644 | size: 15,13 KB (15.494 B) | type: .yaml | lines: 472
|   |   |   |-- [FILE] estimation_spec_joint_pooled_v1.yaml | git: tracked | mode: 100644 | size: 14,32 KB (14.666 B) | type: .yaml | lines: 455
|   |   |   |-- [FILE] estimation_spec_joint_pooled_v1_bll0.yaml | git: tracked | mode: 100644 | size: 15,06 KB (15.424 B) | type: .yaml | lines: 455
|   |   |   |-- [FILE] estimation_spec_joint_pooled_v1_bll0_gsplit_draw.yaml | git: tracked | mode: 100644 | size: 15,57 KB (15.945 B) | type: .yaml | lines: 463
|   |   |   |-- [FILE] estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml | git: tracked | mode: 100644 | size: 15,55 KB (15.925 B) | type: .yaml | lines: 462
|   |   |   |-- [FILE] estimation_spec_joint_pooled_v1_bll0_tlmpin_gsplit.yaml | git: tracked | mode: 100644 | size: 16,80 KB (17.199 B) | type: .yaml | lines: 481
|   |   |   |-- [FILE] theta_hat_realdata_901_gsplit_v1.csv | git: tracked | mode: 100644 | size: 3,48 KB (3.565 B) | type: .csv | lines: 50
|   |   |   |-- [FILE] theta_hat_realdata_901_v1.csv | git: tracked | mode: 100644 | size: 3,34 KB (3.423 B) | type: .csv | lines: 48
|   |   |   |-- [FILE] theta_hat_rebuilt_realdata_901_v1.csv | git: tracked | mode: 100644 | size: 3,35 KB (3.427 B) | type: .csv | lines: 48
|   |   |   |-- [FILE] theta_recovered_staged_synth_901_v1.csv | git: tracked | mode: 100644 | size: 1,54 KB (1.580 B) | type: .csv | lines: 48
|   |   |   \-- [FILE] theta_star_joint_v1.csv | git: tracked | mode: 100644 | size: 1,56 KB (1.595 B) | type: .csv | lines: 50
|   |   |-- [FILE] __init__.py | git: tracked | mode: 100644 | size: 31 B (31 B) | type: .py | lines: 1
|   |   |-- [FILE] _bpool_paths.py | git: tracked | mode: 100644 | size: 1,82 KB (1.866 B) | type: .py | lines: 59
|   |   |-- [FILE] _tmp_benchmark_multistart.py | git: tracked | mode: 100644 | size: 6,71 KB (6.872 B) | type: .py | lines: 157
|   |   |-- [FILE] _tmp_benchmark_scipy_newton.py | git: tracked | mode: 100644 | size: 6,18 KB (6.324 B) | type: .py | lines: 152
|   |   |-- [FILE] assemble_bpool_priced.py | git: tracked | mode: 100644 | size: 6,10 KB (6.248 B) | type: .py | lines: 170
|   |   |-- [FILE] bench_conopt_modelgen.py | git: tracked | mode: 100644 | size: 27,19 KB (27.841 B) | type: .py | lines: 589
|   |   |-- [FILE] bpool_explained.md | git: tracked | mode: 100644 | size: 40,03 KB (40.993 B) | type: .md | lines: 485
|   |   |-- [FILE] build_bpool_couples.py | git: tracked | mode: 100644 | size: 20,97 KB (21.478 B) | type: .py | lines: 520
|   |   |-- [FILE] build_bpool_estimation_ready.py | git: tracked | mode: 100644 | size: 27,54 KB (28.196 B) | type: .py | lines: 617
|   |   |-- [FILE] build_bpool_precompute.py | git: tracked | mode: 100644 | size: 30,44 KB (31.167 B) | type: .py | lines: 653
|   |   |-- [FILE] build_bpool_singles.py | git: tracked | mode: 100644 | size: 17,34 KB (17.758 B) | type: .py | lines: 413
|   |   |-- [FILE] build_joint_theta_star.py | git: tracked | mode: 100644 | size: 5,97 KB (6.115 B) | type: .py | lines: 133
|   |   |-- [FILE] check_bpool_engine_ready.py | git: tracked | mode: 100644 | size: 14,32 KB (14.660 B) | type: .py | lines: 288
|   |   |-- [FILE] check_urbanisation_spec.py | git: tracked | mode: 100644 | size: 6,72 KB (6.877 B) | type: .py | lines: 150
|   |   |-- [FILE] diag_gsplit_nonid_structure.py | git: tracked | mode: 100644 | size: 7,99 KB (8.184 B) | type: .py | lines: 203
|   |   |-- [FILE] diag_nchildren_per_parent.py | git: tracked | mode: 100644 | size: 6,37 KB (6.520 B) | type: .py | lines: 147
|   |   |-- [FILE] dump_theta_star.py | git: tracked | mode: 100644 | size: 2,46 KB (2.522 B) | type: .py | lines: 65
|   |   |-- [FILE] harmonise_bpool_engine_ready.py | git: tracked | mode: 100644 | size: 13,85 KB (14.186 B) | type: .py | lines: 289
|   |   |-- [FILE] hours_mixture_d1.py | git: tracked | mode: 100644 | size: 8,26 KB (8.461 B) | type: .py | lines: 237
|   |   |-- [FILE] jax_joint_hessian.py | git: tracked | mode: 100644 | size: 9,53 KB (9.759 B) | type: .py | lines: 210
|   |   |-- [FILE] jax_ll_probe.py | git: tracked | mode: 100644 | size: 26,77 KB (27.408 B) | type: .py | lines: 614
|   |   |-- [FILE] jax_optimize.py | git: tracked | mode: 100644 | size: 10,59 KB (10.847 B) | type: .py | lines: 244
|   |   |-- [FILE] jax_profile_couples_leisure.py | git: tracked | mode: 100644 | size: 13,82 KB (14.151 B) | type: .py | lines: 285
|   |   |-- [FILE] jax_recovery_gate.py | git: tracked | mode: 100644 | size: 27,69 KB (28.352 B) | type: .py | lines: 560
|   |   |-- [FILE] joint_recovery_test.py | git: tracked | mode: 100644 | size: 79,13 KB (81.027 B) | type: .py | lines: 1.800
|   |   |-- [FILE] launch_chunks.ps1 | git: tracked | mode: 100644 | size: 4,40 KB (4.502 B) | type: .ps1 | lines: 121
|   |   |-- [FILE] occ_draw_empirical.py | git: tracked | mode: 100644 | size: 4,29 KB (4.393 B) | type: .py | lines: 122
|   |   |-- [FILE] phase_a_param_binding.py | git: tracked | mode: 100644 | size: 10,82 KB (11.079 B) | type: .py | lines: 232
|   |   |-- [FILE] phase_b_recovery_test.py | git: tracked | mode: 100644 | size: 14,17 KB (14.511 B) | type: .py | lines: 279
|   |   |-- [FILE] phase0_repricing_variation.py | git: tracked | mode: 100644 | size: 5,77 KB (5.909 B) | type: .py | lines: 133
|   |   |-- [FILE] proto_gamspy_intermediate_var.py | git: tracked | mode: 100644 | size: 9,03 KB (9.246 B) | type: .py | lines: 173
|   |   |-- [FILE] rebuild_meta.py | git: tracked | mode: 100644 | size: 1,54 KB (1.576 B) | type: .py | lines: 51
|   |   |-- [FILE] recovery_test.py | git: tracked | mode: 100644 | size: 34,18 KB (35.002 B) | type: .py | lines: 627
|   |   |-- [FILE] run_bpool_draws.py | git: tracked | mode: 100644 | size: 11,33 KB (11.601 B) | type: .py | lines: 294
|   |   |-- [FILE] run_bpool_euromod.py | git: tracked | mode: 100644 | size: 30,47 KB (31.206 B) | type: .py | lines: 673
|   |   |-- [FILE] run_bpool_euromod_chunk.py | git: tracked | mode: 100644 | size: 10,98 KB (11.247 B) | type: .py | lines: 238
|   |   |-- [FILE] slice_engine_ready.py | git: tracked | mode: 100644 | size: 4,34 KB (4.440 B) | type: .py | lines: 102
|   |   |-- [FILE] step4_emit_results_json.py | git: tracked | mode: 100644 | size: 15,13 KB (15.493 B) | type: .py | lines: 336
|   |   |-- [FILE] step4_lr_pooling_test.py | git: tracked | mode: 100644 | size: 13,17 KB (13.491 B) | type: .py | lines: 298
|   |   |-- [FILE] step4_realdata_baseline.py | git: tracked | mode: 100644 | size: 31,98 KB (32.744 B) | type: .py | lines: 678
|   |   |-- [FILE] validate_chosen_anchors.py | git: tracked | mode: 100644 | size: 6,52 KB (6.679 B) | type: .py | lines: 159
|   |   |-- [FILE] validate_chosen_flips.py | git: tracked | mode: 100644 | size: 7,74 KB (7.926 B) | type: .py | lines: 175
|   |   |-- [FILE] validate_chosen_vs_canonical.py | git: tracked | mode: 100644 | size: 2,92 KB (2.993 B) | type: .py | lines: 80
|   |   |-- [FILE] validate_chosen_vs_tminus1.py | git: tracked | mode: 100644 | size: 9,68 KB (9.914 B) | type: .py | lines: 217
|   |   |-- [FILE] validate_chosen_yem_couples.py | git: tracked | mode: 100644 | size: 3,49 KB (3.575 B) | type: .py | lines: 85
|   |   |-- [FILE] validate_female_repricing.py | git: tracked | mode: 100644 | size: 6,05 KB (6.196 B) | type: .py | lines: 118
|   |   \-- [FILE] verify_lh_coverage.py | git: tracked | mode: 100644 | size: 9,49 KB (9.722 B) | type: .py | lines: 231
|   |-- [DIR] diagnostics/
|   |   |-- [FILE] check_nchildren_simple.py | git: tracked | mode: 100644 | size: 2,05 KB (2.095 B) | type: .py | lines: 61
|   |   |-- [FILE] check_nchildren_variation.py | git: tracked | mode: 100644 | size: 3,53 KB (3.615 B) | type: .py | lines: 101
|   |   |-- [FILE] check_nchildren_variation_v2.py | git: tracked | mode: 100644 | size: 1,72 KB (1.758 B) | type: .py | lines: 51
|   |   |-- [FILE] check_preference_diagnostics.py | git: tracked | mode: 100644 | size: 6,09 KB (6.241 B) | type: .py | lines: 158
|   |   |-- [FILE] check_type_ids.py | git: tracked | mode: 100644 | size: 3,53 KB (3.613 B) | type: .py | lines: 107
|   |   |-- [FILE] compare_scipy_gamspy.py | git: tracked | mode: 100644 | size: 6,94 KB (7.104 B) | type: .py | lines: 174
|   |   |-- [FILE] README.md | git: tracked | mode: 100644 | size: 474 B (474 B) | type: .md | lines: 11
|   |   |-- [FILE] run_stage5a_postestimation_descriptives.py | git: tracked | mode: 100644 | size: 42,19 KB (43.198 B) | type: .py | lines: 951
|   |   |-- [FILE] run_stage5a2_cluster_se_artifact.py | git: tracked | mode: 100644 | size: 8,86 KB (9.074 B) | type: .py | lines: 183
|   |   |-- [FILE] RURO_post_estimation_M1_diagnostics.py | git: tracked | mode: 100644 | size: 27,03 KB (27.674 B) | type: .py | lines: 774
|   |   |-- [FILE] RURO_post_estimation_M1_naive_diagnostics.py | git: tracked | mode: 100644 | size: 28,89 KB (29.584 B) | type: .py | lines: 724
|   |   \-- [FILE] test_gamspy_vs_scipy.py | git: tracked | mode: 100644 | size: 11,01 KB (11.275 B) | type: .py | lines: 310
|   |-- [DIR] enhanced/
|   |   |-- [DIR] specifications/
|   |   |   |-- [FILE] estimation_spec.yaml | git: tracked | mode: 100644 | size: 13,07 KB (13.381 B) | type: .yaml | lines: 331
|   |   |   |-- [FILE] estimation_spec_AC2013.yaml | git: tracked | mode: 100644 | size: 21,05 KB (21.557 B) | type: .yaml | lines: 601
|   |   |   |-- [FILE] estimation_spec_enhanced_minimal.yaml | git: tracked | mode: 100644 | size: 8,90 KB (9.113 B) | type: .yaml | lines: 201
|   |   |   |-- [FILE] estimation_spec_enhanced_minimal_v2.yaml | git: tracked | mode: 100644 | size: 11,05 KB (11.317 B) | type: .yaml | lines: 237
|   |   |   |-- [FILE] estimation_spec_job_choice_v0_id_enhanced.yaml | git: tracked | mode: 100644 | size: 7,19 KB (7.360 B) | type: .yaml | lines: 264
|   |   |   |-- [FILE] estimation_spec_job_choice_v0_id_strict.yaml | git: tracked | mode: 100644 | size: 4,44 KB (4.544 B) | type: .yaml | lines: 177
|   |   |   |-- [FILE] estimation_spec_job_choice_v0_minimal.yaml | git: tracked | mode: 100644 | size: 2,96 KB (3.033 B) | type: .yaml | lines: 123
|   |   |   |-- [FILE] estimation_spec_job_choice_v0_plus.yaml | git: tracked | mode: 100644 | size: 4,85 KB (4.968 B) | type: .yaml | lines: 190
|   |   |   |-- [FILE] estimation_spec_job_choice_v0_plus_b.yaml | git: tracked | mode: 100644 | size: 8,18 KB (8.381 B) | type: .yaml | lines: 278
|   |   |   |-- [FILE] estimation_spec_job_choice_v0_plus_c.yaml | git: tracked | mode: 100644 | size: 8,88 KB (9.092 B) | type: .yaml | lines: 317
|   |   |   |-- [FILE] estimation_spec_job_choice_v1.yaml | git: tracked | mode: 100644 | size: 10,60 KB (10.855 B) | type: .yaml | lines: 342
|   |   |   |-- [FILE] estimation_spec_job_choice_v1_dummies.yaml | git: tracked | mode: 100644 | size: 14,29 KB (14.633 B) | type: .yaml | lines: 457
|   |   |   |-- [FILE] estimation_spec_job_choice_v2.yaml | git: tracked | mode: 100644 | size: 16,47 KB (16.865 B) | type: .yaml | lines: 523
|   |   |   |-- [FILE] estimation_spec_job_M0.yaml | git: tracked | mode: 100644 | size: 2,75 KB (2.814 B) | type: .yaml | lines: 118
|   |   |   |-- [FILE] estimation_spec_job_M1.yaml | git: tracked | mode: 100644 | size: 3,33 KB (3.407 B) | type: .yaml | lines: 136
|   |   |   |-- [FILE] estimation_spec_job_M2.yaml | git: tracked | mode: 100644 | size: 5,00 KB (5.118 B) | type: .yaml | lines: 181
|   |   |   |-- [FILE] estimation_spec_job_M2_centered.yaml | git: tracked | mode: 100644 | size: 4,16 KB (4.255 B) | type: .yaml | lines: 158
|   |   |   |-- [FILE] estimation_spec_job_M2_lite.yaml | git: tracked | mode: 100644 | size: 3,73 KB (3.818 B) | type: .yaml | lines: 146
|   |   |   |-- [FILE] estimation_spec_job_M2_lite_scaled.yaml | git: tracked | mode: 100644 | size: 3,80 KB (3.888 B) | type: .yaml | lines: 150
|   |   |   |-- [FILE] estimation_spec_job_M2_plus.yaml | git: tracked | mode: 100644 | size: 21,35 KB (21.867 B) | type: .yaml | lines: 642
|   |   |   |-- [FILE] estimation_spec_job_M2_scaled.yaml | git: tracked | mode: 100644 | size: 4,16 KB (4.261 B) | type: .yaml | lines: 159
|   |   |   |-- [FILE] estimation_spec_job_M2b.yaml | git: tracked | mode: 100644 | size: 5,40 KB (5.526 B) | type: .yaml | lines: 195
|   |   |   |-- [FILE] estimation_spec_job_M2c.yaml | git: tracked | mode: 100644 | size: 8,08 KB (8.275 B) | type: .yaml | lines: 267
|   |   |   |-- [FILE] estimation_spec_job_M2d_type.yaml | git: tracked | mode: 100644 | size: 6,11 KB (6.261 B) | type: .yaml | lines: 218
|   |   |   |-- [FILE] estimation_spec_job_M2e_a.yaml | git: tracked | mode: 100644 | size: 8,99 KB (9.205 B) | type: .yaml | lines: 290
|   |   |   |-- [FILE] estimation_spec_job_M2e_b.yaml | git: tracked | mode: 100644 | size: 8,24 KB (8.437 B) | type: .yaml | lines: 271
|   |   |   |-- [FILE] estimation_spec_job_M2e_hours.yaml | git: tracked | mode: 100644 | size: 6,88 KB (7.045 B) | type: .yaml | lines: 239
|   |   |   |-- [FILE] estimation_spec_job_M2e_type_fit.yaml | git: tracked | mode: 100644 | size: 6,55 KB (6.705 B) | type: .yaml | lines: 240
|   |   |   |-- [FILE] estimation_spec_job_M2f_hybrid.yaml | git: tracked | mode: 100644 | size: 7,57 KB (7.749 B) | type: .yaml | lines: 261
|   |   |   |-- [FILE] estimation_spec_job_M2g_unified_opportunity.yaml | git: tracked | mode: 100644 | size: 8,63 KB (8.839 B) | type: .yaml | lines: 293
|   |   |   |-- [FILE] estimation_spec_job_M2h_pruned.yaml | git: tracked | mode: 100644 | size: 7,04 KB (7.211 B) | type: .yaml | lines: 247
|   |   |   |-- [FILE] estimation_spec_job_M3.yaml | git: tracked | mode: 100644 | size: 4,18 KB (4.276 B) | type: .yaml | lines: 156
|   |   |   |-- [FILE] estimation_spec_loc_empirical.yaml | git: tracked | mode: 100644 | size: 6,05 KB (6.199 B) | type: .yaml | lines: 246
|   |   |   |-- [FILE] estimation_spec_minimal.yaml | git: tracked | mode: 100644 | size: 3,95 KB (4.043 B) | type: .yaml | lines: 130
|   |   |   |-- [FILE] estimation_spec_minimal_theta0.yaml | git: tracked | mode: 100644 | size: 3,92 KB (4.014 B) | type: .yaml | lines: 129
|   |   |   |-- [FILE] estimation_spec_occupation_choice.yaml | git: tracked | mode: 100644 | size: 13,38 KB (13.702 B) | type: .yaml | lines: 432
|   |   |   |-- [FILE] estimation_spec_pooled_consumption.yaml | git: tracked | mode: 100644 | size: 3,38 KB (3.464 B) | type: .yaml | lines: 100
|   |   |   |-- [FILE] estimation_spec_pooled_leisure.yaml | git: tracked | mode: 100644 | size: 3,24 KB (3.320 B) | type: .yaml | lines: 100
|   |   |   |-- [FILE] estimation_spec_ruro_occ_M0.yaml | git: tracked | mode: 100644 | size: 10,62 KB (10.877 B) | type: .yaml | lines: 351
|   |   |   |-- [FILE] estimation_spec_ruro_occ_M0a.yaml | git: tracked | mode: 100644 | size: 10,92 KB (11.185 B) | type: .yaml | lines: 352
|   |   |   |-- [FILE] estimation_spec_ruro_occ_M0a_clean.yaml | git: tracked | mode: 100644 | size: 10,25 KB (10.492 B) | type: .yaml | lines: 329
|   |   |   |-- [FILE] estimation_spec_ruro_occ_M0b1.yaml | git: tracked | mode: 100644 | size: 9,34 KB (9.562 B) | type: .yaml | lines: 330
|   |   |   |-- [FILE] estimation_spec_ruro_occ_M0b2.yaml | git: tracked | mode: 100644 | size: 9,42 KB (9.651 B) | type: .yaml | lines: 326
|   |   |   |-- [FILE] estimation_spec_ruro_occ_M0c_b.yaml | git: tracked | mode: 100644 | size: 10,40 KB (10.649 B) | type: .yaml | lines: 344
|   |   |   |-- [FILE] estimation_spec_ruro_occ_M0c_b2.yaml | git: tracked | mode: 100644 | size: 9,15 KB (9.371 B) | type: .yaml | lines: 316
|   |   |   |-- [FILE] estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml | git: tracked | mode: 100644 | size: 9,16 KB (9.378 B) | type: .yaml | lines: 316
|   |   |   |-- [FILE] estimation_spec_ruro_occ_M1_clean.yaml | git: tracked | mode: 100644 | size: 11,01 KB (11.274 B) | type: .yaml | lines: 369
|   |   |   |-- [FILE] estimation_spec_ruro_occ_M1_naive.yaml | git: tracked | mode: 100644 | size: 10,14 KB (10.385 B) | type: .yaml | lines: 349
|   |   |   |-- [FILE] estimation_spec_ruro_occ_P3a_pooled.yaml | git: tracked | mode: 100644 | size: 11,05 KB (11.316 B) | type: .yaml | lines: 373
|   |   |   |-- [FILE] estimation_spec_simple.yaml | git: tracked | mode: 100644 | size: 5,25 KB (5.372 B) | type: .yaml | lines: 175
|   |   |   |-- [FILE] estimation_spec_ultra_minimal.yaml | git: tracked | mode: 100644 | size: 3,00 KB (3.075 B) | type: .yaml | lines: 93
|   |   |   |-- [FILE] estimation_spec_v2.yaml | git: tracked | mode: 100644 | size: 10,29 KB (10.539 B) | type: .yaml | lines: 314
|   |   |   |-- [FILE] estimation_spec_v3.yaml | git: tracked | mode: 100644 | size: 14,99 KB (15.354 B) | type: .yaml | lines: 440
|   |   |   \-- [FILE] README.md | git: tracked | mode: 100644 | size: 732 B (732 B) | type: .md | lines: 17
|   |   |-- [FILE] checking.ipynb | git: tracked | mode: 100644 | size: 145,02 KB (148.499 B) | type: .ipynb | lines: 6.535
|   |   |-- [FILE] cluster_robust_se.py | git: tracked | mode: 100644 | size: 8,60 KB (8.811 B) | type: .py | lines: 240
|   |   |-- [FILE] compute_standard_errors.py | git: tracked | mode: 100644 | size: 12,94 KB (13.249 B) | type: .py | lines: 379
|   |   |-- [FILE] diagnostic_consumption_variation.py | git: tracked | mode: 100644 | size: 8,39 KB (8.589 B) | type: .py | lines: 209
|   |   |-- [FILE] diagnostics_bundle.py | git: tracked | mode: 100644 | size: 107,75 KB (110.333 B) | type: .py | lines: 2.505
|   |   |-- [FILE] enh_france_data_prep.py | git: tracked | mode: 100644 | size: 109,58 KB (112.209 B) | type: .py | lines: 2.621
|   |   |-- [FILE] enh_pipeline.ps1 | git: tracked | mode: 100644 | size: 20,89 KB (21.387 B) | type: .ps1 | lines: 534
|   |   |-- [FILE] enh_prepare_FR_gsur.py | git: tracked | mode: 100644 | size: 24,93 KB (25.533 B) | type: .py | lines: 717
|   |   |-- [FILE] enh_prepare_FR_gsur_v2.py | git: tracked | mode: 100644 | size: 33,74 KB (34.550 B) | type: .py | lines: 859
|   |   |-- [FILE] enh_RURO_draws.py | git: tracked | mode: 100644 | size: 64,52 KB (66.072 B) | type: .py | lines: 1.631
|   |   |-- [FILE] enh_RURO_estimate_FR.py | git: tracked | mode: 100644 | size: 72,47 KB (74.212 B) | type: .py | lines: 1.821
|   |   |-- [FILE] enh_RURO_euromod.py | git: tracked | mode: 100644 | size: 54,74 KB (56.051 B) | type: .py | lines: 1.151
|   |   |-- [FILE] enh_RURO_explore_predrop.py | git: tracked | mode: 100644 | size: 38,63 KB (39.561 B) | type: .py | lines: 907
|   |   |-- [FILE] enh_RURO_mnl_rebuild_GSURv2_stageA.py | git: tracked | mode: 100644 | size: 45,54 KB (46.633 B) | type: .py | lines: 1.116
|   |   |-- [FILE] enh_RURO_post_estimation.py | git: tracked | mode: 100644 | size: 54,96 KB (56.274 B) | type: .py | lines: 1.654
|   |   |-- [FILE] enh_RURO_prep.py | git: tracked | mode: 100644 | size: 55,06 KB (56.386 B) | type: .py | lines: 1.339
|   |   |-- [FILE] enh_RURO_prep_mnl_basic.py | git: tracked | mode: 100644 | size: 96,69 KB (99.013 B) | type: .py | lines: 2.433
|   |   |-- [FILE] estimation_engine.py | git: tracked | mode: 100644 | size: 91,89 KB (94.097 B) | type: .py | lines: 2.446
|   |   |-- [FILE] estimation_spec_parser.py | git: tracked | mode: 100644 | size: 80,07 KB (81.990 B) | type: .py | lines: 1.905
|   |   |-- [FILE] estimation_utils.py | git: tracked | mode: 100644 | size: 73,93 KB (75.700 B) | type: .py | lines: 1.799
|   |   |-- [FILE] estimation_utils_AC2013.py | git: tracked | mode: 100644 | size: 24,55 KB (25.137 B) | type: .py | lines: 770
|   |   |-- [FILE] expression_constraints.py | git: tracked | mode: 100644 | size: 27,25 KB (27.903 B) | type: .py | lines: 748
|   |   |-- [FILE] fix_spec_initial_values.py | git: tracked | mode: 100644 | size: 8,80 KB (9.011 B) | type: .py | lines: 283
|   |   |-- [FILE] gamspy_estimation.py | git: tracked | mode: 100644 | size: 104,88 KB (107.393 B) | type: .py | lines: 2.563
|   |   |-- [FILE] gamspy_estimation_vectorized.py | git: tracked | mode: 100644 | size: 70,26 KB (71.943 B) | type: .py | lines: 1.871
|   |   |-- [FILE] mcfadden_sampler.py | git: tracked | mode: 100644 | size: 15,80 KB (16.176 B) | type: .py | lines: 539
|   |   |-- [FILE] occupation_choice_utils.py | git: tracked | mode: 100644 | size: 16,81 KB (17.209 B) | type: .py | lines: 504
|   |   |-- [FILE] parallel_estimation.py | git: tracked | mode: 100644 | size: 23,86 KB (24.432 B) | type: .py | lines: 648
|   |   |-- [FILE] path_helpers.py | git: tracked | mode: 100644 | size: 8,63 KB (8.835 B) | type: .py | lines: 265
|   |   |-- [FILE] quick_verify.py | git: tracked | mode: 100644 | size: 6,64 KB (6.799 B) | type: .py | lines: 196
|   |   |-- [FILE] README.md | git: tracked | mode: 100644 | size: 10,56 KB (10.813 B) | type: .md | lines: 305
|   |   |-- [FILE] reduce_draws_files.py | git: tracked | mode: 100644 | size: 15,60 KB (15.974 B) | type: .py | lines: 496
|   |   |-- [FILE] reduce_mnl_columns.py | git: tracked | mode: 100644 | size: 24,85 KB (25.451 B) | type: .py | lines: 644
|   |   |-- [FILE] run_cluster_robust_se.py | git: tracked | mode: 100644 | size: 54,73 KB (56.040 B) | type: .py | lines: 1.227
|   |   |-- [FILE] run_diagnostics.ps1 | git: tracked | mode: 100644 | size: 3,25 KB (3.326 B) | type: .ps1 | lines: 85
|   |   |-- [FILE] run_enhanced_pipeline.ps1 | git: tracked | mode: 100644 | size: 36,79 KB (37.677 B) | type: .ps1 | lines: 851
|   |   |-- [FILE] RURO_post_estimation_styled.py | git: tracked | mode: 100644 | size: 426,54 KB (436.782 B) | type: .py | lines: 10.232
|   |   |-- [FILE] sanity_checks.py | git: tracked | mode: 100644 | size: 25,44 KB (26.046 B) | type: .py | lines: 667
|   |   \-- [FILE] validate_specs.py | git: tracked | mode: 100644 | size: 5,88 KB (6.017 B) | type: .py | lines: 174
|   |-- [DIR] Job_model/
|   |   |-- [FILE] ACCEPTANCE_TESTS.md | git: tracked | mode: 100644 | size: 15,09 KB (15.457 B) | type: .md | lines: 419
|   |   |-- [FILE] Commands_job.txt | git: tracked | mode: 100644 | size: 3,79 KB (3.885 B) | type: .txt | lines: 85
|   |   |-- [FILE] enh_job_draws.py | git: tracked | mode: 100644 | size: 41,13 KB (42.120 B) | type: .py | lines: 1.110
|   |   |-- [FILE] enh_job_universe.py | git: tracked | mode: 100644 | size: 55,47 KB (56.806 B) | type: .py | lines: 1.492
|   |   |-- [FILE] New Text Document.txt | git: tracked | mode: 100644 | size: 6,48 KB (6.639 B) | type: .txt | lines: 165
|   |   |-- [FILE] plot_loc_by_dehde.py | git: tracked | mode: 100644 | size: 6,01 KB (6.151 B) | type: .py | lines: 170
|   |   |-- [FILE] README_job_model.md | git: tracked | mode: 100644 | size: 7,79 KB (7.976 B) | type: .md | lines: 204
|   |   |-- [FILE] run_job_ruro_pipeline.py | git: tracked | mode: 100644 | size: 15,53 KB (15.903 B) | type: .py | lines: 498
|   |   \-- [FILE] sanity_checks_job.py | git: tracked | mode: 100644 | size: 21,14 KB (21.647 B) | type: .py | lines: 542
|   |-- [DIR] maintenance/
|   |   |-- [FILE] prepare_pooled_estimation_ready.py | git: tracked | mode: 100644 | size: 24,88 KB (25.474 B) | type: .py | lines: 579
|   |   |-- [FILE] rename_stijn_to_ruro.py | git: tracked | mode: 100644 | size: 16,40 KB (16.795 B) | type: .py | lines: 444
|   |   |-- [FILE] run_pooled_P3a_estimation.py | git: tracked | mode: 100644 | size: 12,38 KB (12.681 B) | type: .py | lines: 326
|   |   |-- [FILE] run_pooled_P3a_presolver_checks.py | git: tracked | mode: 100644 | size: 11,46 KB (11.737 B) | type: .py | lines: 317
|   |   |-- [FILE] run_pooled_P3a_S5_S8_hessian_recompute.py | git: tracked | mode: 100644 | size: 10,44 KB (10.694 B) | type: .py | lines: 228
|   |   |-- [FILE] run_pooled_P3a_S6_preference_comparison.py | git: tracked | mode: 100644 | size: 5,35 KB (5.477 B) | type: .py | lines: 119
|   |   |-- [FILE] run_pooled_P3a_S6_theta_c_singles_profile.py | git: tracked | mode: 100644 | size: 5,87 KB (6.011 B) | type: .py | lines: 134
|   |   |-- [FILE] validate_occ_dummies.py | git: tracked | mode: 100644 | size: 1,93 KB (1.978 B) | type: .py | lines: 50
|   |   |-- [FILE] validate_v1.py | git: tracked | mode: 100644 | size: 1,13 KB (1.153 B) | type: .py | lines: 21
|   |   \-- [FILE] validate_v7.py | git: tracked | mode: 100644 | size: 5,14 KB (5.268 B) | type: .py | lines: 110
|   |-- [DIR] multi_year/
|   |   |-- [FILE] __init__.py | git: tracked | mode: 100644 | size: 47 B (47 B) | type: .py | lines: 1
|   |   |-- [FILE] m1_add_cluster_key.py | git: tracked | mode: 100644 | size: 10,44 KB (10.694 B) | type: .py | lines: 282
|   |   |-- [FILE] m1_config.py | git: tracked | mode: 100644 | size: 10,53 KB (10.780 B) | type: .py | lines: 269
|   |   |-- [FILE] m1_harmonise_cpi.py | git: tracked | mode: 100644 | size: 13,01 KB (13.321 B) | type: .py | lines: 364
|   |   |-- [FILE] m1_identity_validation.py | git: tracked | mode: 100644 | size: 18,67 KB (19.120 B) | type: .py | lines: 505
|   |   |-- [FILE] m1_isf_check_2018.py | git: tracked | mode: 100644 | size: 21,96 KB (22.488 B) | type: .py | lines: 596
|   |   |-- [FILE] m1_stack_years.py | git: tracked | mode: 100644 | size: 17,58 KB (18.006 B) | type: .py | lines: 455
|   |   |-- [FILE] m1_validate.py | git: tracked | mode: 100644 | size: 30,88 KB (31.619 B) | type: .py | lines: 822
|   |   \-- [FILE] run_m1_p3a.ps1 | git: tracked | mode: 100644 | size: 13,06 KB (13.370 B) | type: .ps1 | lines: 308
|   |-- [DIR] pilot/
|   |   |-- [DIR] _tmp_beta_diag/
|   |   |   |-- [FILE] result_PARTICIPATION.json | git: tracked | mode: 100644 | size: 3,96 KB (4.055 B) | type: .json | lines: 100
|   |   |   |-- [FILE] result_PROFILE.json | git: tracked | mode: 100644 | size: 8,31 KB (8.510 B) | type: .json | lines: 249
|   |   |   |-- [FILE] result_REOPT_CONOPT.json | git: tracked | mode: 100644 | size: 4,58 KB (4.691 B) | type: .json | lines: 119
|   |   |   |-- [FILE] result_REOPT_FLOOR.json | git: tracked | mode: 100644 | size: 4,54 KB (4.648 B) | type: .json | lines: 119
|   |   |   \-- [FILE] result_REOPT_NEG.json | git: tracked | mode: 100644 | size: 4,75 KB (4.868 B) | type: .json | lines: 121
|   |   |-- [DIR] _tmp_optdiag/
|   |   |   |-- [FILE] result_S1_A.json | git: tracked | mode: 100644 | size: 7,63 KB (7.818 B) | type: .json | lines: 229
|   |   |   |-- [FILE] result_S1_C1.json | git: tracked | mode: 100644 | size: 9,64 KB (9.869 B) | type: .json | lines: 315
|   |   |   |-- [FILE] result_S1_C2.json | git: tracked | mode: 100644 | size: 9,63 KB (9.861 B) | type: .json | lines: 315
|   |   |   |-- [FILE] result_S1_C3.json | git: tracked | mode: 100644 | size: 9,62 KB (9.855 B) | type: .json | lines: 315
|   |   |   |-- [FILE] result_S2a.json | git: tracked | mode: 100644 | size: 9,08 KB (9.293 B) | type: .json | lines: 313
|   |   |   |-- [FILE] result_S2b.json | git: tracked | mode: 100644 | size: 12,10 KB (12.387 B) | type: .json | lines: 406
|   |   |   \-- [FILE] result_S2c.json | git: tracked | mode: 100644 | size: 10,06 KB (10.302 B) | type: .json | lines: 350
|   |   |-- [DIR] _tmp_scaled_val/
|   |   |   |-- [FILE] result_A.json | git: tracked | mode: 100644 | size: 9,70 KB (9.933 B) | type: .json | lines: 314
|   |   |   |-- [FILE] result_B.json | git: tracked | mode: 100644 | size: 9,25 KB (9.471 B) | type: .json | lines: 314
|   |   |   \-- [FILE] result_C.json | git: tracked | mode: 100644 | size: 9,72 KB (9.950 B) | type: .json | lines: 314
|   |   |-- [DIR] _tmp_validation/
|   |   |   |-- [FILE] result_A.json | git: tracked | mode: 100644 | size: 37,14 KB (38.029 B) | type: .json | lines: 1.312
|   |   |   |-- [FILE] result_B.json | git: tracked | mode: 100644 | size: 45,07 KB (46.155 B) | type: .json | lines: 1.644
|   |   |   \-- [FILE] result_C.json | git: tracked | mode: 100644 | size: 36,96 KB (37.846 B) | type: .json | lines: 1.312
|   |   |-- [DIR] config/
|   |   |   \-- [FILE] pilot_mincer_coefficients_v1.json | git: tracked | mode: 100644 | size: 5,20 KB (5.322 B) | type: .json | lines: 135
|   |   |-- [DIR] specs/
|   |   |   \-- [FILE] estimation_spec_nc_pilot_couples_2016.yaml | git: tracked | mode: 100644 | size: 8,37 KB (8.568 B) | type: .yaml | lines: 288
|   |   |-- [FILE] _bisect_ll.py | git: tracked | mode: 100644 | size: 8,79 KB (9.005 B) | type: .py | lines: 157
|   |   |-- [FILE] _precompute_gate.py | git: tracked | mode: 100644 | size: 14,75 KB (15.109 B) | type: .py | lines: 352
|   |   |-- [FILE] _rebuild_c_norm.py | git: tracked | mode: 100644 | size: 16,36 KB (16.748 B) | type: .py | lines: 356
|   |   |-- [FILE] _resolve_hnpos.py | git: tracked | mode: 100644 | size: 18,29 KB (18.729 B) | type: .py | lines: 380
|   |   |-- [FILE] _run_beta_l0_m_diagnostic.py | git: tracked | mode: 100644 | size: 73,60 KB (75.371 B) | type: .py | lines: 1.441
|   |   |-- [FILE] _run_diagnostic_estimation.py | git: tracked | mode: 100644 | size: 17,43 KB (17.848 B) | type: .py | lines: 378
|   |   |-- [FILE] _run_diagnostic_estimation_rerun.py | git: tracked | mode: 100644 | size: 35,77 KB (36.633 B) | type: .py | lines: 826
|   |   |-- [FILE] _run_jax_optimizer_benchmark.py | git: tracked | mode: 100644 | size: 41,16 KB (42.146 B) | type: .py | lines: 964
|   |   |-- [FILE] _run_jax_validation_estimation.py | git: tracked | mode: 100644 | size: 40,32 KB (41.284 B) | type: .py | lines: 883
|   |   |-- [FILE] _run_ll_equivalence_prototype.py | git: tracked | mode: 100644 | size: 52,33 KB (53.590 B) | type: .py | lines: 1.197
|   |   |-- [FILE] _run_loc4_precompute_augmentation.py | git: tracked | mode: 100644 | size: 19,30 KB (19.765 B) | type: .py | lines: 418
|   |   |-- [FILE] _run_optimizer_protocol_diagnostic.py | git: tracked | mode: 100644 | size: 44,23 KB (45.291 B) | type: .py | lines: 932
|   |   |-- [FILE] _run_precompute.py | git: tracked | mode: 100644 | size: 17,33 KB (17.750 B) | type: .py | lines: 397
|   |   |-- [FILE] _run_scaled_jax_validation.py | git: tracked | mode: 100644 | size: 39,95 KB (40.905 B) | type: .py | lines: 796
|   |   |-- [FILE] _validate_draw_patch.py | git: tracked | mode: 100644 | size: 8,51 KB (8.719 B) | type: .py | lines: 196
|   |   |-- [FILE] build_pilot_couples_product.py | git: tracked | mode: 100644 | size: 21,07 KB (21.578 B) | type: .py | lines: 440
|   |   |-- [FILE] build_precompute_ready.py | git: tracked | mode: 100644 | size: 17,00 KB (17.409 B) | type: .py | lines: 370
|   |   |-- [FILE] export_pilot_euromod_inputs.py | git: tracked | mode: 100644 | size: 16,50 KB (16.894 B) | type: .py | lines: 350
|   |   |-- [FILE] export_pilot_euromod_inputs_v2.py | git: tracked | mode: 100644 | size: 16,55 KB (16.950 B) | type: .py | lines: 373
|   |   |-- [FILE] fit_pilot_mincer.py | git: tracked | mode: 100644 | size: 11,99 KB (12.278 B) | type: .py | lines: 282
|   |   |-- [FILE] merge_pilot_em_outputs.py | git: tracked | mode: 100644 | size: 21,25 KB (21.765 B) | type: .py | lines: 464
|   |   |-- [FILE] pilot_wage_draw.py | git: tracked | mode: 100644 | size: 7,86 KB (8.044 B) | type: .py | lines: 218
|   |   \-- [FILE] run_pilot_em_blocks.py | git: tracked | mode: 100644 | size: 5,25 KB (5.374 B) | type: .py | lines: 122
|   |-- [DIR] runners/
|   |   \-- [DIR] legacy/
|   |       |-- [FILE] cleanup_final.ps1 | git: tracked | mode: 100644 | size: 6,41 KB (6.562 B) | type: .ps1 | lines: 191
|   |       |-- [FILE] README.md | git: tracked | mode: 100644 | size: 400 B (400 B) | type: .md | lines: 18
|   |       |-- [FILE] run_gamspy_estimation.ps1 | git: tracked | mode: 100644 | size: 2,80 KB (2.864 B) | type: .ps1 | lines: 75
|   |       |-- [FILE] RUN_NOW.ps1 | git: tracked | mode: 100644 | size: 1,11 KB (1.140 B) | type: .ps1 | lines: 30
|   |       |-- [FILE] RUN_OPTIMIZED_ESTIMATION.ps1 | git: tracked | mode: 100644 | size: 1,94 KB (1.984 B) | type: .ps1 | lines: 46
|   |       |-- [FILE] RUN_PIPELINE_WITH_REDUCED_FILES.ps1 | git: tracked | mode: 100644 | size: 4,87 KB (4.986 B) | type: .ps1 | lines: 116
|   |       |-- [FILE] RUN_POST_ESTIMATION_STYLED.ps1 | git: tracked | mode: 100644 | size: 477 B (477 B) | type: .ps1 | lines: 9
|   |       \-- [FILE] RUN_WITH_SCIPY.ps1 | git: tracked | mode: 100644 | size: 1,94 KB (1.985 B) | type: .ps1 | lines: 43
|   |-- [DIR] welfare/
|   |   |-- [DIR] configs/
|   |   |   \-- [FILE] welfare_stage1_w3.yaml | git: tracked | mode: 100644 | size: 19,06 KB (19.518 B) | type: .yaml | lines: 303
|   |   |-- [DIR] fastlane/
|   |   |   |-- [FILE] run_f3_tasks1_5.py | git: tracked | mode: 100644 | size: 15,10 KB (15.460 B) | type: .py | lines: 357
|   |   |   |-- [FILE] run_f3r2_reconcile_joint_parity.py | git: tracked | mode: 100644 | size: 45,11 KB (46.192 B) | type: .py | lines: 1.066
|   |   |   |-- [FILE] run_f3r2a_repair_diagnosis.py | git: tracked | mode: 100644 | size: 50,31 KB (51.518 B) | type: .py | lines: 1.221
|   |   |   |-- [FILE] run_f3r2b_gate_bc_fix.py | git: tracked | mode: 100644 | size: 26,94 KB (27.591 B) | type: .py | lines: 666
|   |   |   |-- [FILE] run_f4a_singles_measure_core.py | git: tracked | mode: 100644 | size: 48,26 KB (49.423 B) | type: .py | lines: 939
|   |   |   |-- [FILE] run_f4c_final_singles_measures.py | git: tracked | mode: 100644 | size: 29,85 KB (30.570 B) | type: .py | lines: 566
|   |   |   |-- [FILE] run_f5_singles_measure_family.py | git: tracked | mode: 100644 | size: 29,27 KB (29.976 B) | type: .py | lines: 640
|   |   |   \-- [FILE] run_f5r_crosssection_reconciliation.py | git: tracked | mode: 100644 | size: 21,00 KB (21.501 B) | type: .py | lines: 402
|   |   |-- [FILE] run_stage1_w3.py | git: tracked | mode: 100644 | size: 9,30 KB (9.523 B) | type: .py | lines: 229
|   |   |-- [FILE] run_stage2_assessment_unit_diag.py | git: tracked | mode: 100644 | size: 10,24 KB (10.481 B) | type: .py | lines: 205
|   |   |-- [FILE] run_stage2_chosen_measure.py | git: tracked | mode: 100644 | size: 16,61 KB (17.009 B) | type: .py | lines: 351
|   |   |-- [FILE] run_stage2_chosen_task1.py | git: tracked | mode: 100644 | size: 13,62 KB (13.950 B) | type: .py | lines: 280
|   |   |-- [FILE] run_stage2_chunk_writeback_validation.py | git: tracked | mode: 100644 | size: 19,70 KB (20.169 B) | type: .py | lines: 367
|   |   |-- [FILE] run_stage2_correction_prep.py | git: tracked | mode: 100644 | size: 20,88 KB (21.381 B) | type: .py | lines: 421
|   |   |-- [FILE] run_stage2_couples_audit.py | git: tracked | mode: 100644 | size: 5,06 KB (5.178 B) | type: .py | lines: 115
|   |   |-- [FILE] run_stage2_couples_reprice.py | git: tracked | mode: 100644 | size: 12,40 KB (12.696 B) | type: .py | lines: 268
|   |   |-- [FILE] run_stage2_cross_track_diag.py | git: tracked | mode: 100644 | size: 13,17 KB (13.485 B) | type: .py | lines: 260
|   |   |-- [FILE] run_stage2_full_rebuild_staging.py | git: tracked | mode: 100644 | size: 15,80 KB (16.182 B) | type: .py | lines: 310
|   |   |-- [FILE] run_stage2_full_rebuild_validation.py | git: tracked | mode: 100644 | size: 9,09 KB (9.310 B) | type: .py | lines: 196
|   |   |-- [FILE] run_stage2_parity.py | git: tracked | mode: 100644 | size: 2,66 KB (2.724 B) | type: .py | lines: 67
|   |   |-- [FILE] run_stage2_resim.py | git: tracked | mode: 100644 | size: 6,99 KB (7.157 B) | type: .py | lines: 140
|   |   |-- [FILE] run_stage2_singles_vdir_gate.py | git: tracked | mode: 100644 | size: 9,33 KB (9.556 B) | type: .py | lines: 196
|   |   |-- [FILE] run_stage2_twoH_validation.py | git: tracked | mode: 100644 | size: 17,60 KB (18.018 B) | type: .py | lines: 357
|   |   |-- [FILE] run_stage2_vdir.py | git: tracked | mode: 100644 | size: 11,93 KB (12.220 B) | type: .py | lines: 242
|   |   |-- [FILE] run_stage3a_pinned_baseline_validation.py | git: tracked | mode: 100644 | size: 28,68 KB (29.368 B) | type: .py | lines: 594
|   |   |-- [FILE] run_stage3b1_engine_ready_parity.py | git: tracked | mode: 100644 | size: 30,51 KB (31.239 B) | type: .py | lines: 600
|   |   |-- [FILE] run_stage3b2_controlled_reestimation.py | git: tracked | mode: 100644 | size: 16,63 KB (17.026 B) | type: .py | lines: 338
|   |   |-- [FILE] run_stage3b3_synthetic_recovery.py | git: tracked | mode: 100644 | size: 19,45 KB (19.913 B) | type: .py | lines: 384
|   |   |-- [FILE] run_stage4a_baseline_policy.py | git: tracked | mode: 100644 | size: 11,32 KB (11.592 B) | type: .py | lines: 234
|   |   |-- [FILE] run_stage4b_population_parity_gate.py | git: tracked | mode: 100644 | size: 14,33 KB (14.673 B) | type: .py | lines: 287
|   |   |-- [FILE] run_stage4c_singles_vdir_smoke.py | git: tracked | mode: 100644 | size: 45,26 KB (46.348 B) | type: .py | lines: 873
|   |   |-- [FILE] run_stage4c2_vdir_bias_calibration.py | git: tracked | mode: 100644 | size: 20,97 KB (21.473 B) | type: .py | lines: 405
|   |   |-- [FILE] welfare_assessment_unit_diag.py | git: tracked | mode: 100644 | size: 14,27 KB (14.615 B) | type: .py | lines: 313
|   |   |-- [FILE] welfare_chosen_contamination.py | git: tracked | mode: 100644 | size: 5,76 KB (5.895 B) | type: .py | lines: 112
|   |   |-- [FILE] welfare_core.py | git: tracked | mode: 100644 | size: 25,44 KB (26.053 B) | type: .py | lines: 603
|   |   |-- [FILE] welfare_correction_prep.py | git: tracked | mode: 100644 | size: 10,08 KB (10.320 B) | type: .py | lines: 197
|   |   |-- [FILE] welfare_couples_contamination_audit.py | git: tracked | mode: 100644 | size: 10,84 KB (11.097 B) | type: .py | lines: 224
|   |   |-- [FILE] welfare_cross_track_residual_diag.py | git: tracked | mode: 100644 | size: 5,30 KB (5.430 B) | type: .py | lines: 111
|   |   |-- [FILE] welfare_resim_probe.py | git: tracked | mode: 100644 | size: 9,42 KB (9.645 B) | type: .py | lines: 186
|   |   \-- [FILE] welfare_vdir.py | git: tracked | mode: 100644 | size: 28,41 KB (29.096 B) | type: .py | lines: 558
|   |-- [FILE] extract_excel_text.py | git: tracked | mode: 100644 | size: 765 B (765 B) | type: .py | lines: 24
|   |-- [FILE] france_data_prep.py | git: tracked | mode: 100644 | size: 67,86 KB (69.486 B) | type: .py | lines: 1.718
|   |-- [FILE] generate_html_report.py | git: tracked | mode: 100644 | size: 11,08 KB (11.346 B) | type: .py | lines: 325
|   |-- [FILE] init_params_singles_template.csv | git: tracked | mode: 100644 | size: 2,39 KB (2.444 B) | type: .csv | lines: 38
|   |-- [FILE] path_helpers.py | git: tracked | mode: 100644 | size: 8,71 KB (8.922 B) | type: .py | lines: 266
|   |-- [FILE] prepare_FR_gsur.py | git: tracked | mode: 100644 | size: 15,40 KB (15.774 B) | type: .py | lines: 453
|   |-- [FILE] run_fr_2016_joint_only.ps1 | git: tracked | mode: 100644 | size: 28,66 KB (29.351 B) | type: .ps1 | lines: 677
|   |-- [FILE] run_fr_2016_pipeline.ps1 | git: tracked | mode: 100644 | size: 21,90 KB (22.423 B) | type: .ps1 | lines: 518
|   |-- [FILE] run_pipeline_explicit.ipynb | git: tracked | mode: 100644 | size: 152,58 KB (156.240 B) | type: .ipynb | lines: 3.327
|   |-- [FILE] run_post_estimation.ps1 | git: tracked | mode: 100644 | size: 5,83 KB (5.975 B) | type: .ps1 | lines: 150
|   |-- [FILE] run_post_estimation_standalone.py | git: tracked | mode: 100644 | size: 7,25 KB (7.427 B) | type: .py | lines: 186
|   |-- [FILE] RURO_draws.py | git: tracked | mode: 100644 | size: 37,09 KB (37.976 B) | type: .py | lines: 913
|   |-- [FILE] RURO_estimate_FR.py | git: tracked | mode: 100644 | size: 244,33 KB (250.197 B) | type: .py | lines: 6.201
|   |-- [FILE] RURO_euromod.py | git: tracked | mode: 100644 | size: 39,47 KB (40.415 B) | type: .py | lines: 810
|   |-- [FILE] RURO_post_estimation.py | git: tracked | mode: 100644 | size: 108,93 KB (111.547 B) | type: .py | lines: 2.836
|   |-- [FILE] RURO_prep.py | git: tracked | mode: 100644 | size: 27,55 KB (28.215 B) | type: .py | lines: 729
|   |-- [FILE] RURO_prep_mnl_basic.py | git: tracked | mode: 100644 | size: 31,36 KB (32.115 B) | type: .py | lines: 815
|   |-- [FILE] script_files_structure.md | git: tracked | mode: 100644 | size: 29,21 KB (29.906 B) | type: .md | lines: N/A (binary)
|   |-- [FILE] scripts_files_structure.md | git: tracked | mode: 100644 | size: 34,10 KB (34.922 B) | type: .md | lines: N/A (binary)
|   |-- [FILE] seed_boxcox_init.csv | git: tracked | mode: 100644 | size: 310 B (310 B) | type: .csv | lines: 13
|   |-- [FILE] sync_backup.ps1 | git: tracked | mode: 100644 | size: 5,98 KB (6.125 B) | type: .ps1 | lines: 146
|   \-- [FILE] tdo.ps1 | git: tracked | mode: 100644 | size: 2,11 KB (2.157 B) | type: .ps1 | lines: 39
|-- [DIR] src/
|   \-- [DIR] mnl/
|       |-- [DIR] data/
|       |   |-- [FILE] __init__.py | git: tracked | mode: 100644 | size: 176 B (176 B) | type: .py | lines: 6
|       |   \-- [FILE] loaders.py | git: tracked | mode: 100644 | size: 1,22 KB (1.253 B) | type: .py | lines: 39
|       |-- [DIR] evaluation/
|       |   |-- [FILE] __init__.py | git: tracked | mode: 100644 | size: 171 B (171 B) | type: .py | lines: 6
|       |   \-- [FILE] metrics.py | git: tracked | mode: 100644 | size: 771 B (771 B) | type: .py | lines: 22
|       |-- [DIR] integration/
|       |   |-- [FILE] __init__.py | git: tracked | mode: 100644 | size: 201 B (201 B) | type: .py | lines: 5
|       |   \-- [FILE] euromod.py | git: tracked | mode: 100644 | size: 5,96 KB (6.101 B) | type: .py | lines: 152
|       |-- [DIR] models/
|       |   |-- [FILE] __init__.py | git: tracked | mode: 100644 | size: 129 B (129 B) | type: .py | lines: 6
|       |   \-- [FILE] mnl.py | git: tracked | mode: 100644 | size: 1,39 KB (1.423 B) | type: .py | lines: 39
|       |-- [DIR] pipelines/
|       |   |-- [FILE] __init__.py | git: tracked | mode: 100644 | size: 169 B (169 B) | type: .py | lines: 6
|       |   \-- [FILE] estimation.py | git: tracked | mode: 100644 | size: 1,44 KB (1.475 B) | type: .py | lines: 47
|       |-- [FILE] __init__.py | git: tracked | mode: 100644 | size: 309 B (309 B) | type: .py | lines: 11
|       \-- [FILE] config.py | git: tracked | mode: 100644 | size: 1,42 KB (1.455 B) | type: .py | lines: 45
|-- [DIR] stijn/
|   |-- [FILE] .Rhistory | git: tracked | mode: 100644 | size: 0 B (0 B) | type: .rhistory | lines: 0
|   |-- [FILE] Ruro_estimation_H.Rmd | git: tracked | mode: 100644 | size: 68,69 KB (70.337 B) | type: .rmd | lines: 1.416
|   |-- [FILE] Ruro_estimation_new.Rmd | git: tracked | mode: 100644 | size: 93,39 KB (95.630 B) | type: .rmd | lines: 1.878
|   |-- [FILE] Ruro_functions_EMRWS.R | git: tracked | mode: 100644 | size: 60,07 KB (61.511 B) | type: .r | lines: 1.068
|   |-- [FILE] Ruro_simulation_H.Rmd | git: tracked | mode: 100644 | size: 306,23 KB (313.579 B) | type: .rmd | lines: 6.538
|   \-- [FILE] stijn_files_structure.md | git: tracked | mode: 100644 | size: 496 B (496 B) | type: .md | lines: N/A (binary)
|-- [DIR] tests/
|   |-- [FILE] test_imports.py | git: tracked | mode: 100644 | size: 130 B (130 B) | type: .py | lines: 5
|   \-- [FILE] test_recovery_cov_verdict.py | git: tracked | mode: 100644 | size: 5,58 KB (5.709 B) | type: .py | lines: 139
|-- [GITLINK] dclaborsupply-monorepo/ | git: tracked | mode: 160000 | contents: separate repository, not traversed
|-- [FILE] .gitignore | git: tracked | mode: 100644 | size: 595 B (595 B) | type: .gitignore | lines: 39
|-- [FILE] .markdownlint.json | git: tracked | mode: 100644 | size: 61 B (61 B) | type: .json | lines: 5
|-- [FILE] 01_repo_inventory.md | git: tracked | mode: 100644 | size: 70,76 KB (72.455 B) | type: .md | lines: 749
|-- [FILE] 02_package_architecture_memo.md | git: tracked | mode: 100644 | size: 10,49 KB (10.746 B) | type: .md | lines: 208
|-- [FILE] 03_migration_matrix.md | git: tracked | mode: 100644 | size: 27,96 KB (28.626 B) | type: .md | lines: 127
|-- [FILE] debug.log | git: tracked | mode: 100644 | size: 2,80 KB (2.869 B) | type: .log | lines: 27
|-- [FILE] gate_gsplit_901_run.log | git: tracked | mode: 100644 | size: 15,04 KB (15.398 B) | type: .log | lines: N/A (binary)
|-- [FILE] gate_output.txt | git: tracked | mode: 100644 | size: 2,81 KB (2.881 B) | type: .txt | lines: 34
|-- [FILE] Project_files_structure.md | git: tracked | mode: 100644 | size: 5,04 MB (5.281.220 B) | type: .md | lines: N/A (binary)
|-- [FILE] pyproject.toml | git: tracked | mode: 100644 | size: 1,21 KB (1.234 B) | type: .toml | lines: 62
|-- [FILE] README.md | git: tracked | mode: 100644 | size: 22,67 KB (23.214 B) | type: .md | lines: 529
|-- [FILE] requirements.txt | git: tracked | mode: 100644 | size: 4,48 KB (4.590 B) | type: .txt | lines: 224
\-- [FILE] RURO_MNL_project_files_structure.md | git: tracked | mode: 100644 | size: 473,47 KB (484.835 B) | type: .md | lines: 9.350
```

