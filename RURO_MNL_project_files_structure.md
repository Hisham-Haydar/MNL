# RURO MNL Project File Structure

> **Historical snapshot - not live project state (annotated 2026-07-22).** Point-in-time file-structure snapshot, retained for reference only. For current state see JMP_project_state_v1.md (Job_Market_paper) and the sole certified baseline joint_pooled_v1_bll0_tlmpin (negLL 238504.6360973987). Do not treat paths here as current.

Generated from: U:\Desktop\Nizam_Hisham\MNL
Generated on: 2026-05-12 14:39:19
Excluded: hidden items, dot-prefixed items, venv, env, __pycache__, node_modules, dist, build
the folders and subfolders are : 
```text
+---[DIR] _gams_work/
+---[DIR] configs/
|   \---[FILE] default.yaml | size: 407 B | ext: .yaml
+---[DIR] Data/
|   +---[DIR] documentation/
|   |   +---[FILE] DRD_FR_2016_a3_export.txt | size: 37.70 KB | ext: .txt
|   |   +---[FILE] DRD_FR_2016_index.jsonl | size: 29.88 KB | ext: .jsonl
|   |   +---[FILE] FR_2015_all_tables_compact.md | size: 111.54 KB | ext: .md
|   |   +---[FILE] FR_2015_index.jsonl | size: 67.26 KB | ext: .jsonl
|   |   \---[FILE] FR_2015_index.md | size: 59.60 KB | ext: .md
|   +---[DIR] external/
|   |   +---[FILE] cpi.xlsx | size: 11.56 KB | ext: .xlsx
|   |   +---[FILE] FR_gsur.xlsx | size: 1.03 MB | ext: .xlsx
|   |   +---[FILE] FR_gsur_full.csv | size: 4.61 MB | ext: .csv
|   |   +---[FILE] FR_gsur_full.parquet | size: 98.63 KB | ext: .parquet
|   |   +---[FILE] FR_gsur_ruro.csv | size: 142.38 KB | ext: .csv
|   |   +---[FILE] FR_gsur_ruro.parquet | size: 11.41 KB | ext: .parquet
|   |   +---[FILE] FR_gsur_simple.parquet | size: 17.95 KB | ext: .parquet
|   |   \---[FILE] smic.xlsx | size: 10.37 KB | ext: .xlsx
|   \---[FILE] README.md | size: 270 B | ext: .md
+---[DIR] docs/
|   +---[DIR] archive/
|   |   +---[DIR] commands/
|   |   |   +---[FILE] commands_20260122_143200.txt | size: 725 B | ext: .txt
|   |   |   \---[FILE] commands_legacy.txt | size: 3.73 KB | ext: .txt
|   |   +---[DIR] implementation_history/
|   |   |   +---[FILE] DONE.md | size: 12.59 KB | ext: .md
|   |   |   +---[FILE] IMPLEMENTATION_SUMMARY.md | size: 8.59 KB | ext: .md
|   |   |   +---[FILE] POST_ESTIMATION_IMPROVEMENTS.md | size: 24.85 KB | ext: .md
|   |   |   +---[FILE] README_legacy_2026-05-11.md | size: 8.65 KB | ext: .md
|   |   |   \---[FILE] VECTORIZED_IMPLEMENTATION_STATUS.md | size: 9.66 KB | ext: .md
|   |   +---[DIR] inventories/
|   |   |   +---[DIR] external_storage_2026-05-12/
|   |   |   |   +---[FILE] external_storage_cross_root_differences_2026-05-12.csv | size: 9.62 KB | ext: .csv
|   |   |   |   +---[FILE] external_storage_full_file_inventory_2026-05-12.csv | size: 2.01 MB | ext: .csv
|   |   |   |   +---[FILE] external_storage_key_metadata_summary_2026-05-12.csv | size: 2.25 KB | ext: .csv
|   |   |   |   +---[FILE] external_storage_report_files_2026-05-12.csv | size: 144.07 KB | ext: .csv
|   |   |   |   +---[FILE] external_storage_reports_results_inventory_2026-05-12.csv | size: 2.01 MB | ext: .csv
|   |   |   |   +---[FILE] external_storage_reports_topfolders_2026-05-12.csv | size: 874 B | ext: .csv
|   |   |   |   +---[FILE] external_storage_ruro_directory_inventory_2026-05-12.csv | size: 63.12 KB | ext: .csv
|   |   |   |   +---[FILE] external_storage_ruro_file_inventory_2026-05-12.csv | size: 566.57 KB | ext: .csv
|   |   |   |   +---[FILE] external_storage_ruro1_topfolders_2026-05-12.csv | size: 4.75 KB | ext: .csv
|   |   |   |   +---[FILE] external_storage_top_level_inventory_2026-05-12.csv | size: 4.52 KB | ext: .csv
|   |   |   |   +---[FILE] repo_estimation_results_summary_2026-05-12.csv | size: 88.06 KB | ext: .csv
|   |   |   |   +---[FILE] repo_estimation_runs_inventory_2026-05-12.csv | size: 35.05 KB | ext: .csv
|   |   |   |   \---[FILE] repo_outputs_file_inventory_2026-05-12.csv | size: 1.61 MB | ext: .csv
|   |   |   \---[FILE] RURO_MNL_project_files_structure_2026-05-11.md | size: 465.33 KB | ext: .md
|   |   +---[DIR] job_choice_notes/
|   |   |   +---[FILE] JOB_CHOICE_MODEL_DIAGNOSIS.md | size: 11.57 KB | ext: .md
|   |   |   +---[FILE] JOB_CHOICE_PIPELINE.md | size: 32.57 KB | ext: .md
|   |   |   \---[FILE] JOB_CHOICE_PIPELINE_WALKTHROUGH.md | size: 11.00 KB | ext: .md
|   |   +---[DIR] occupation_choice_notes/
|   |   |   +---[FILE] OCCUPATION_CHOICE_AGNOSTIC_DESIGN.md | size: 9.72 KB | ext: .md
|   |   |   +---[FILE] OCCUPATION_CHOICE_DESIGN.md | size: 14.27 KB | ext: .md
|   |   |   +---[FILE] OCCUPATION_CHOICE_MATHEMATICAL_SPECIFICATION.md | size: 20.53 KB | ext: .md
|   |   |   +---[FILE] OCCUPATION_CHOICE_SUMMARY.md | size: 12.32 KB | ext: .md
|   |   |   \---[FILE] OCCUPATION_VS_EDUCATION_CHOICE.md | size: 8.64 KB | ext: .md
|   |   +---[DIR] scratch_2026-05-11/
|   |   |   +---[FILE] my_functions.py | size: 55.48 KB | ext: .py
|   |   |   +---[FILE] Ruro_estimation_new.Rmd | size: 93.39 KB | ext: .Rmd
|   |   |   \---[FILE] RURO_post_estimation_OLD_backup_20251208.py | size: 263.09 KB | ext: .py
|   |   \---[FILE] README.md | size: 432 B | ext: .md
|   +---[FILE] FR2016_RURO_pipeline_report.md | size: 41.17 KB | ext: .md
|   +---[FILE] GAMSPy_Integration_Roadmap.md | size: 20.68 KB | ext: .md
|   +---[FILE] GAMSPy_Quick_Start.md | size: 8.69 KB | ext: .md
|   +---[FILE] GAMSPy_vs_SciPy_Architecture_Comparison.md | size: 39.05 KB | ext: .md
|   +---[FILE] PIPELINE_ENTRYPOINTS.md | size: 2.41 KB | ext: .md
|   +---[FILE] ROADMAP.md | size: 8.23 KB | ext: .md
|   +---[FILE] RURO_ACTIVE_RESULTS_REGISTRY.md | size: 3.11 KB | ext: .md
|   +---[FILE] RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md | size: 11.46 KB | ext: .md
|   +---[FILE] RURO_CURRENT_STATE_AND_IDENTIFICATION.md | size: 9.63 KB | ext: .md
|   +---[FILE] RURO_ENHANCED_PIPELINE_COMMANDS.md | size: 15.64 KB | ext: .md
|   +---[FILE] RURO_EXTERNAL_STORAGE_HYGIENE_AUDIT_2026-05-12.md | size: 17.57 KB | ext: .md
|   +---[FILE] RURO_GSUR_DATA_AND_MERGE_NOTE.md | size: 10.79 KB | ext: .md
|   +---[FILE] RURO_JOB_MODEL_GMM_METHOD_NOTE.md | size: 14.06 KB | ext: .md
|   +---[FILE] RURO_model_spec_contract_v1.md | size: 26.52 KB | ext: .md
|   +---[FILE] RURO_PREFERENCE_ESTIMATION_CAPABILITIES.md | size: 27.56 KB | ext: .md
|   +---[FILE] RURO_PROJECT_HYGIENE_CLEANUP_LOG_2026-05-11.md | size: 4.57 KB | ext: .md
|   +---[FILE] RURO_PROJECT_HYGIENE_CLEANUP_RECOMMENDATIONS.md | size: 19.11 KB | ext: .md
|   +---[FILE] RURO_PROJECT_MEMORY_MAP.md | size: 10.00 KB | ext: .md
|   +---[FILE] RURO_RETURN_GUIDE_DATA_RESULTS_AND_CLEANUP.md | size: 12.87 KB | ext: .md
|   +---[FILE] RURO_R_REFERENCE_COMPARISON_AND_ACTION_PLAN.md | size: 11.20 KB | ext: .md
|   +---[FILE] RURO_R_REFERENCE_COMPARISON_SECTOR_OPPORTUNITY_PLAN.md | size: 21.24 KB | ext: .md
|   \---[FILE] RURO_WORKSPACE_AUDIT_2026-05-11.md | size: 7.88 KB | ext: .md
+---[DIR] literature/
|   +---[FILE] Aaberge_Colombino_2011_Empirical Optimal Income Taxation (1).pdf | size: 396.00 KB | ext: .pdf
|   \---[FILE] ijm-00139.pdf | size: 1.47 MB | ext: .pdf
+---[DIR] logs/
+---[DIR] Microsoft/
|   \---[DIR] Windows/
|       \---[DIR] PowerShell/
|           \---[FILE] ModuleAnalysisCache | size: 8.85 KB | ext: [no extension]
+---[DIR] notebooks/
|   +---[FILE] estimation_notebook.ipynb | size: 25.08 KB | ext: .ipynb
|   \---[FILE] README.md | size: 179 B | ext: .md
+---[DIR] notes/
|   +---[FILE] EUROMO_sys_france_2015.md | size: 6.02 KB | ext: .md
|   \---[FILE] R_REFERENCE_vs_PYTHON_SPECIFICATION.md | size: 8.44 KB | ext: .md
+---[DIR] outputs/
|   +---[DIR] diagnostics/
|   |   +---[DIR] loc_by_dehde/
|   |   |   +---[FILE] couples_loc_by_dehde_0.png | size: 24.55 KB | ext: .png
|   |   |   +---[FILE] couples_loc_by_dehde_100.png | size: 24.71 KB | ext: .png
|   |   |   +---[FILE] couples_loc_by_dehde_200.png | size: 24.02 KB | ext: .png
|   |   |   +---[FILE] couples_loc_by_dehde_32.png | size: 21.89 KB | ext: .png
|   |   |   +---[FILE] couples_loc_by_dehde_33.png | size: 21.59 KB | ext: .png
|   |   |   +---[FILE] couples_loc_by_dehde_344.png | size: 23.47 KB | ext: .png
|   |   |   +---[FILE] couples_loc_by_dehde_353.png | size: 24.12 KB | ext: .png
|   |   |   +---[FILE] couples_loc_by_dehde_354.png | size: 28.31 KB | ext: .png
|   |   |   +---[FILE] couples_loc_by_dehde_440.png | size: 21.60 KB | ext: .png
|   |   |   +---[FILE] couples_loc_by_dehde_500.png | size: 26.43 KB | ext: .png
|   |   |   +---[FILE] couples_loc4_by_dehde_0.png | size: 22.70 KB | ext: .png
|   |   |   +---[FILE] couples_loc4_by_dehde_100.png | size: 23.19 KB | ext: .png
|   |   |   +---[FILE] couples_loc4_by_dehde_200.png | size: 24.27 KB | ext: .png
|   |   |   +---[FILE] couples_loc4_by_dehde_32.png | size: 22.33 KB | ext: .png
|   |   |   +---[FILE] couples_loc4_by_dehde_33.png | size: 22.02 KB | ext: .png
|   |   |   +---[FILE] couples_loc4_by_dehde_344.png | size: 23.94 KB | ext: .png
|   |   |   +---[FILE] couples_loc4_by_dehde_353.png | size: 23.19 KB | ext: .png
|   |   |   +---[FILE] couples_loc4_by_dehde_354.png | size: 24.80 KB | ext: .png
|   |   |   +---[FILE] couples_loc4_by_dehde_440.png | size: 21.90 KB | ext: .png
|   |   |   +---[FILE] couples_loc4_by_dehde_500.png | size: 26.65 KB | ext: .png
|   |   |   +---[FILE] singles_loc_by_dehde_0.png | size: 27.53 KB | ext: .png
|   |   |   +---[FILE] singles_loc_by_dehde_100.png | size: 22.88 KB | ext: .png
|   |   |   +---[FILE] singles_loc_by_dehde_200.png | size: 26.16 KB | ext: .png
|   |   |   +---[FILE] singles_loc_by_dehde_33.png | size: 21.64 KB | ext: .png
|   |   |   +---[FILE] singles_loc_by_dehde_344.png | size: 23.24 KB | ext: .png
|   |   |   +---[FILE] singles_loc_by_dehde_353.png | size: 23.86 KB | ext: .png
|   |   |   +---[FILE] singles_loc_by_dehde_354.png | size: 28.11 KB | ext: .png
|   |   |   +---[FILE] singles_loc_by_dehde_440.png | size: 24.05 KB | ext: .png
|   |   |   +---[FILE] singles_loc_by_dehde_500.png | size: 26.91 KB | ext: .png
|   |   |   +---[FILE] singles_loc4_by_dehde_0.png | size: 22.86 KB | ext: .png
|   |   |   +---[FILE] singles_loc4_by_dehde_100.png | size: 26.01 KB | ext: .png
|   |   |   +---[FILE] singles_loc4_by_dehde_200.png | size: 25.18 KB | ext: .png
|   |   |   +---[FILE] singles_loc4_by_dehde_33.png | size: 22.05 KB | ext: .png
|   |   |   +---[FILE] singles_loc4_by_dehde_344.png | size: 23.44 KB | ext: .png
|   |   |   +---[FILE] singles_loc4_by_dehde_353.png | size: 22.35 KB | ext: .png
|   |   |   +---[FILE] singles_loc4_by_dehde_354.png | size: 24.43 KB | ext: .png
|   |   |   +---[FILE] singles_loc4_by_dehde_440.png | size: 24.38 KB | ext: .png
|   |   |   \---[FILE] singles_loc4_by_dehde_500.png | size: 26.70 KB | ext: .png
|   |   \---[FILE] pre_estimation_diagnostics.json | size: 2.88 KB | ext: .json
|   +---[DIR] estimates/
|   |   \---[DIR] fr/
|   |       +---[DIR] 2016/
|   |       |   +---[DIR] post_estimation/
|   |       |   |   +---[FILE] elasticities.csv | size: 425 B | ext: .csv
|   |       |   |   +---[FILE] fit_mean_hours.png | size: 32.44 KB | ext: .png
|   |       |   |   +---[FILE] fit_participation.png | size: 32.47 KB | ext: .png
|   |       |   |   +---[FILE] muc_comparison.png | size: 74.63 KB | ext: .png
|   |       |   |   +---[FILE] mul_comparison.png | size: 86.77 KB | ext: .png
|   |       |   |   +---[FILE] negative_mu_diagnostics.png | size: 43.58 KB | ext: .png
|   |       |   |   +---[FILE] params.csv | size: 2.28 KB | ext: .csv
|   |       |   |   +---[FILE] post_estimation_report_20260109_060407.html | size: 28.75 KB | ext: .html
|   |       |   |   +---[FILE] post_estimation_report_20260109_060422.html | size: 28.75 KB | ext: .html
|   |       |   |   +---[FILE] post_estimation_report_20260109_060436.html | size: 28.75 KB | ext: .html
|   |       |   |   +---[FILE] post_estimation_report_20260109_060514.html | size: 28.75 KB | ext: .html
|   |       |   |   +---[FILE] post_estimation_report_20260109_060538.html | size: 28.75 KB | ext: .html
|   |       |   |   +---[FILE] post_estimation_report_20260109_060554.html | size: 28.75 KB | ext: .html
|   |       |   |   +---[FILE] post_estimation_report_20260109_060932.html | size: 44.38 KB | ext: .html
|   |       |   |   +---[FILE] sf_contours.png | size: 133.85 KB | ext: .png
|   |       |   |   +---[FILE] sf_mu.png | size: 73.88 KB | ext: .png
|   |       |   |   +---[FILE] sm_contours.png | size: 120.42 KB | ext: .png
|   |       |   |   \---[FILE] sm_mu.png | size: 69.01 KB | ext: .png
|   |       |   +---[DIR] post_estimation_new/
|   |       |   |   +---[FILE] fr_2016_cou_f_contours.png | size: 134.19 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_cou_f_mu.png | size: 72.72 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_cou_m_contours.png | size: 113.11 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_cou_m_mu.png | size: 71.52 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_elasticities.csv | size: 463 B | ext: .csv
|   |       |   |   +---[FILE] fr_2016_fit_mean_hours.png | size: 33.53 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_fit_participation.png | size: 33.63 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_muc_comparison.png | size: 85.85 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_mul_comparison.png | size: 97.29 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_negative_mu_diagnostics.png | size: 45.03 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_params.csv | size: 2.28 KB | ext: .csv
|   |       |   |   +---[FILE] fr_2016_post_estimation_report_20260109_091536.html | size: 44.50 KB | ext: .html
|   |       |   |   +---[FILE] fr_2016_sf_contours.png | size: 133.85 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_sf_mu.png | size: 73.88 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_sm_contours.png | size: 120.42 KB | ext: .png
|   |       |   |   \---[FILE] fr_2016_sm_mu.png | size: 69.01 KB | ext: .png
|   |       |   +---[DIR] post_estimation_v2/
|   |       |   |   +---[FILE] elasticities.csv | size: 463 B | ext: .csv
|   |       |   |   +---[FILE] fit_mean_hours.png | size: 32.44 KB | ext: .png
|   |       |   |   +---[FILE] fit_participation.png | size: 32.47 KB | ext: .png
|   |       |   |   +---[FILE] muc_comparison.png | size: 74.63 KB | ext: .png
|   |       |   |   +---[FILE] mul_comparison.png | size: 86.77 KB | ext: .png
|   |       |   |   +---[FILE] negative_mu_diagnostics.png | size: 43.58 KB | ext: .png
|   |       |   |   +---[FILE] params.csv | size: 2.28 KB | ext: .csv
|   |       |   |   +---[FILE] post_estimation_report_20260109_062137.html | size: 44.46 KB | ext: .html
|   |       |   |   +---[FILE] sf_contours.png | size: 133.85 KB | ext: .png
|   |       |   |   +---[FILE] sf_mu.png | size: 73.88 KB | ext: .png
|   |       |   |   +---[FILE] sm_contours.png | size: 120.42 KB | ext: .png
|   |       |   |   \---[FILE] sm_mu.png | size: 69.01 KB | ext: .png
|   |       |   +---[DIR] post_estimation_v3/
|   |       |   |   +---[FILE] elasticities.csv | size: 463 B | ext: .csv
|   |       |   |   +---[FILE] fit_mean_hours.png | size: 33.53 KB | ext: .png
|   |       |   |   +---[FILE] fit_participation.png | size: 33.63 KB | ext: .png
|   |       |   |   +---[FILE] muc_comparison.png | size: 74.63 KB | ext: .png
|   |       |   |   +---[FILE] mul_comparison.png | size: 86.77 KB | ext: .png
|   |       |   |   +---[FILE] negative_mu_diagnostics.png | size: 43.58 KB | ext: .png
|   |       |   |   +---[FILE] params.csv | size: 2.28 KB | ext: .csv
|   |       |   |   +---[FILE] post_estimation_report_20260109_064201.html | size: 43.29 KB | ext: .html
|   |       |   |   +---[FILE] post_estimation_report_20260109_064246.html | size: 43.29 KB | ext: .html
|   |       |   |   +---[FILE] post_estimation_report_20260109_064331.html | size: 43.29 KB | ext: .html
|   |       |   |   +---[FILE] post_estimation_report_20260109_064520.html | size: 43.29 KB | ext: .html
|   |       |   |   +---[FILE] post_estimation_report_20260109_064616.html | size: 43.29 KB | ext: .html
|   |       |   |   +---[FILE] post_estimation_report_20260109_064717.html | size: 43.29 KB | ext: .html
|   |       |   |   +---[FILE] post_estimation_report_20260109_064850.html | size: 43.29 KB | ext: .html
|   |       |   |   +---[FILE] sf_contours.png | size: 133.85 KB | ext: .png
|   |       |   |   +---[FILE] sf_mu.png | size: 73.88 KB | ext: .png
|   |       |   |   +---[FILE] sm_contours.png | size: 120.42 KB | ext: .png
|   |       |   |   \---[FILE] sm_mu.png | size: 69.01 KB | ext: .png
|   |       |   +---[DIR] post_estimation_v4/
|   |       |   |   +---[FILE] fr_2016_cou_f_contours.png | size: 134.19 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_cou_f_mu.png | size: 72.72 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_cou_m_contours.png | size: 113.11 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_cou_m_mu.png | size: 71.52 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_elasticities.csv | size: 463 B | ext: .csv
|   |       |   |   +---[FILE] fr_2016_fit_mean_hours.png | size: 34.45 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_fit_participation.png | size: 34.54 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_muc_comparison.png | size: 85.85 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_mul_comparison.png | size: 97.29 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_params.csv | size: 2.28 KB | ext: .csv
|   |       |   |   +---[FILE] fr_2016_post_estimation_report_20260109_072805.html | size: 41.76 KB | ext: .html
|   |       |   |   +---[FILE] fr_2016_sf_contours.png | size: 133.85 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_sf_mu.png | size: 73.88 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_sm_contours.png | size: 120.42 KB | ext: .png
|   |       |   |   \---[FILE] fr_2016_sm_mu.png | size: 69.01 KB | ext: .png
|   |       |   +---[DIR] post_estimation_v5/
|   |       |   |   +---[FILE] fr_2016_cou_f_contours.png | size: 134.19 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_cou_f_mu.png | size: 72.72 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_cou_m_contours.png | size: 113.11 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_cou_m_mu.png | size: 71.52 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_elasticities.csv | size: 463 B | ext: .csv
|   |       |   |   +---[FILE] fr_2016_fit_mean_hours.png | size: 33.53 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_fit_participation.png | size: 33.63 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_muc_comparison.png | size: 85.85 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_mul_comparison.png | size: 97.29 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_negative_mu_diagnostics.png | size: 43.58 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_params.csv | size: 2.28 KB | ext: .csv
|   |       |   |   +---[FILE] fr_2016_post_estimation_report_20260109_074300.html | size: 42.55 KB | ext: .html
|   |       |   |   +---[FILE] fr_2016_sf_contours.png | size: 133.85 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_sf_mu.png | size: 73.88 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_sm_contours.png | size: 120.42 KB | ext: .png
|   |       |   |   \---[FILE] fr_2016_sm_mu.png | size: 69.01 KB | ext: .png
|   |       |   +---[DIR] post_estimation_v6/
|   |       |   |   +---[FILE] fr_2016_cou_f_contours.png | size: 134.19 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_cou_f_mu.png | size: 72.72 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_cou_m_contours.png | size: 113.11 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_cou_m_mu.png | size: 71.52 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_elasticities.csv | size: 463 B | ext: .csv
|   |       |   |   +---[FILE] fr_2016_fit_mean_hours.png | size: 33.53 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_fit_participation.png | size: 33.63 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_muc_comparison.png | size: 85.85 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_mul_comparison.png | size: 97.29 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_negative_mu_diagnostics.png | size: 43.58 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_params.csv | size: 2.28 KB | ext: .csv
|   |       |   |   +---[FILE] fr_2016_post_estimation_report_20260109_080500.html | size: 42.60 KB | ext: .html
|   |       |   |   +---[FILE] fr_2016_sf_contours.png | size: 133.85 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_sf_mu.png | size: 73.88 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_sm_contours.png | size: 120.42 KB | ext: .png
|   |       |   |   \---[FILE] fr_2016_sm_mu.png | size: 69.01 KB | ext: .png
|   |       |   +---[DIR] post_estimation_v7/
|   |       |   |   +---[FILE] cou_f_contours.png | size: 134.19 KB | ext: .png
|   |       |   |   +---[FILE] cou_f_mu.png | size: 72.72 KB | ext: .png
|   |       |   |   +---[FILE] cou_m_contours.png | size: 113.11 KB | ext: .png
|   |       |   |   +---[FILE] cou_m_mu.png | size: 71.52 KB | ext: .png
|   |       |   |   +---[FILE] elasticities.csv | size: 463 B | ext: .csv
|   |       |   |   +---[FILE] fit_mean_hours.png | size: 33.53 KB | ext: .png
|   |       |   |   +---[FILE] fit_participation.png | size: 33.63 KB | ext: .png
|   |       |   |   +---[FILE] muc_comparison.png | size: 85.85 KB | ext: .png
|   |       |   |   +---[FILE] mul_comparison.png | size: 97.29 KB | ext: .png
|   |       |   |   +---[FILE] negative_mu_diagnostics.png | size: 45.03 KB | ext: .png
|   |       |   |   +---[FILE] params.csv | size: 2.28 KB | ext: .csv
|   |       |   |   +---[FILE] post_estimation_report_20260109_081850.html | size: 44.41 KB | ext: .html
|   |       |   |   +---[FILE] sf_contours.png | size: 133.85 KB | ext: .png
|   |       |   |   +---[FILE] sf_mu.png | size: 73.88 KB | ext: .png
|   |       |   |   +---[FILE] sm_contours.png | size: 120.42 KB | ext: .png
|   |       |   |   \---[FILE] sm_mu.png | size: 69.01 KB | ext: .png
|   |       |   +---[DIR] test_run/
|   |       |   |   +---[FILE] estimation.log | size: 11.58 KB | ext: .log
|   |       |   |   +---[FILE] estimation_results.json | size: 6.89 KB | ext: .json
|   |       |   |   +---[FILE] estimation_summary.txt | size: 488 B | ext: .txt
|   |       |   |   \---[FILE] specification_used.yaml | size: 11.95 KB | ext: .yaml
|   |       |   +---[DIR] test_run2/
|   |       |   |   +---[FILE] estimation.log | size: 13.75 KB | ext: .log
|   |       |   |   +---[FILE] estimation_results.json | size: 6.88 KB | ext: .json
|   |       |   |   +---[FILE] estimation_summary.txt | size: 488 B | ext: .txt
|   |       |   |   \---[FILE] specification_used.yaml | size: 11.95 KB | ext: .yaml
|   |       |   +---[FILE] estimation.log | size: 29.05 KB | ext: .log
|   |       |   +---[FILE] estimation_results.json | size: 10.75 KB | ext: .json
|   |       |   +---[FILE] estimation_results_couples.csv | size: 1.64 KB | ext: .csv
|   |       |   +---[FILE] estimation_results_singles_female.csv | size: 1.54 KB | ext: .csv
|   |       |   +---[FILE] estimation_results_singles_male.csv | size: 1.52 KB | ext: .csv
|   |       |   +---[FILE] estimation_summary.txt | size: 489 B | ext: .txt
|   |       |   +---[FILE] fr_2016_joint.json | size: 7.71 KB | ext: .json
|   |       |   +---[FILE] fr_2016_joint_with_fit_stats.json | size: 7.91 KB | ext: .json
|   |       |   \---[FILE] specification_used.yaml | size: 11.95 KB | ext: .yaml
|   |       +---[DIR] 2016_gamspy/
|   |       |   +---[DIR] run_2026-01-16_11-35-36/
|   |       |   |   \---[FILE] estimation.log | size: 11.71 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-16_11-46-07/
|   |       |   |   \---[FILE] estimation.log | size: 9.71 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-16_11-48-57/
|   |       |   |   \---[FILE] estimation.log | size: 9.71 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-16_11-51-21/
|   |       |   |   \---[FILE] estimation.log | size: 9.75 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-16_12-01-32/
|   |       |   |   \---[FILE] estimation.log | size: 11.70 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-16_16-07-59/
|   |       |   |   \---[FILE] estimation.log | size: 11.99 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-16_16-24-38/
|   |       |   |   \---[FILE] estimation.log | size: 12.15 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-16_16-28-31/
|   |       |   |   \---[FILE] estimation.log | size: 12.15 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-16_16-53-03/
|   |       |   |   \---[FILE] estimation.log | size: 12.80 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-16_18-30-52/
|   |       |   |   \---[FILE] estimation.log | size: 12.40 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-16_18-37-23/
|   |       |   |   \---[FILE] estimation.log | size: 9.35 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-16_18-41-47/
|   |       |   |   \---[FILE] estimation.log | size: 12.38 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-16_19-10-34/
|   |       |   |   \---[FILE] estimation.log | size: 9.36 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-16_19-45-00/
|   |       |   |   \---[FILE] estimation.log | size: 14.88 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-16_19-55-17/
|   |       |   |   \---[FILE] estimation.log | size: 14.49 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-16_20-10-05/
|   |       |   |   +---[FILE] estimation.log | size: 15.66 KB | ext: .log
|   |       |   |   +---[FILE] estimation_results.json | size: 25.11 KB | ext: .json
|   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.52 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.52 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.52 KB | ext: .csv
|   |       |   |   \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       |   +---[DIR] run_2026-01-16_20-22-31/
|   |       |   |   +---[FILE] estimation.log | size: 22.44 KB | ext: .log
|   |       |   |   +---[FILE] estimation_results.json | size: 25.11 KB | ext: .json
|   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.52 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.52 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.52 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_summary.txt | size: 7.21 KB | ext: .txt
|   |       |   |   \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       |   +---[DIR] run_2026-01-17_01-24-03/
|   |       |   |   \---[FILE] estimation.log | size: 405.03 MB | ext: .log
|   |       |   +---[DIR] run_2026-01-17_09-11-59/
|   |       |   |   \---[FILE] estimation.log | size: 13.78 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-17_09-26-49/
|   |       |   |   \---[FILE] estimation.log | size: 13.78 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-17_09-42-32/
|   |       |   |   \---[FILE] estimation.log | size: 13.89 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-17_09-55-53/
|   |       |   |   \---[FILE] estimation.log | size: 13.89 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-17_10-09-26/
|   |       |   |   +---[FILE] estimation.log | size: 22.67 KB | ext: .log
|   |       |   |   +---[FILE] estimation_results.json | size: 26.36 KB | ext: .json
|   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.71 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.71 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.71 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_summary.txt | size: 7.32 KB | ext: .txt
|   |       |   |   \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       |   +---[DIR] run_2026-01-17_14-43-21/
|   |       |   |   \---[FILE] estimation.log | size: 13.69 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-17_14-53-16/
|   |       |   |   +---[FILE] estimation.log | size: 22.47 KB | ext: .log
|   |       |   |   +---[FILE] estimation_results.json | size: 26.35 KB | ext: .json
|   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.71 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.71 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.71 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_summary.txt | size: 7.32 KB | ext: .txt
|   |       |   |   \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       |   +---[DIR] run_2026-01-17_15-09-45/
|   |       |   |   \---[FILE] estimation.log | size: 10.57 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-17_15-10-15/
|   |       |   |   +---[FILE] estimation.log | size: 23.43 KB | ext: .log
|   |       |   |   +---[FILE] estimation_results.json | size: 26.34 KB | ext: .json
|   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.71 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.71 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.71 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_summary.txt | size: 7.32 KB | ext: .txt
|   |       |   |   \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       |   +---[DIR] run_2026-01-17_19-29-22/
|   |       |   |   \---[FILE] estimation.log | size: 10.20 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-17_19-29-40/
|   |       |   |   \---[FILE] estimation.log | size: 11.34 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-17_19-32-00/
|   |       |   |   \---[FILE] estimation.log | size: 11.69 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-17_19-42-09/
|   |       |   |   +---[FILE] estimation.log | size: 23.42 KB | ext: .log
|   |       |   |   +---[FILE] estimation_results.json | size: 27.84 KB | ext: .json
|   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.96 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.96 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.96 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_summary.txt | size: 7.32 KB | ext: .txt
|   |       |   |   \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       |   +---[DIR] run_2026-01-19_16-41-16/
|   |       |   |   \---[FILE] estimation.log | size: 3.97 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-19_16-44-20/
|   |       |   |   \---[FILE] estimation.log | size: 11.34 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-19_18-25-06/
|   |       |   |   \---[FILE] estimation.log | size: 11.61 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-19_18-28-33/
|   |       |   |   \---[FILE] estimation.log | size: 11.61 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-20_10-46-39/
|   |       |   |   \---[FILE] estimation.log | size: 16.36 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-20_11-15-28/
|   |       |   |   \---[FILE] estimation.log | size: 17.13 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-20_11-45-14/
|   |       |   |   \---[FILE] estimation.log | size: 16.78 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-20_13-35-25/
|   |       |   |   \---[FILE] estimation.log | size: 14.47 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-20_14-05-59/
|   |       |   |   +---[FILE] estimation.log | size: 23.84 KB | ext: .log
|   |       |   |   +---[FILE] estimation_results.json | size: 33.75 KB | ext: .json
|   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.88 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.88 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.88 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_summary.txt | size: 7.32 KB | ext: .txt
|   |       |   |   \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       |   +---[DIR] run_2026-01-20_15-30-09/
|   |       |   |   +---[FILE] estimation.log | size: 23.94 KB | ext: .log
|   |       |   |   +---[FILE] estimation_results.json | size: 33.06 KB | ext: .json
|   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.83 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.83 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.83 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_summary.txt | size: 7.32 KB | ext: .txt
|   |       |   |   \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       |   +---[DIR] run_2026-01-20_15-57-10/
|   |       |   |   +---[FILE] estimation.log | size: 24.00 KB | ext: .log
|   |       |   |   +---[FILE] estimation_results.json | size: 33.06 KB | ext: .json
|   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.83 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.83 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.83 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_summary.txt | size: 7.32 KB | ext: .txt
|   |       |   |   \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       |   +---[DIR] run_2026-01-21_00-29-45/
|   |       |   |   \---[FILE] estimation.log | size: 14.90 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-21_01-01-29/
|   |       |   |   +---[FILE] estimation.log | size: 18.23 KB | ext: .log
|   |       |   |   \---[FILE] estimation_results.json | size: 6.79 KB | ext: .json
|   |       |   +---[DIR] run_2026-01-21_10-59-49/
|   |       |   |   +---[FILE] estimation.log | size: 18.40 KB | ext: .log
|   |       |   |   \---[FILE] estimation_results.json | size: 6.79 KB | ext: .json
|   |       |   +---[DIR] run_2026-01-22_00-51-46/
|   |       |   |   +---[FILE] estimation.log | size: 25.73 KB | ext: .log
|   |       |   |   +---[FILE] estimation_results.json | size: 33.90 KB | ext: .json
|   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.83 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.83 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.83 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_summary.txt | size: 7.32 KB | ext: .txt
|   |       |   |   \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       |   +---[DIR] run_2026-01-22_13-38-57/
|   |       |   |   +---[FILE] estimation.log | size: 25.73 KB | ext: .log
|   |       |   |   +---[FILE] estimation_results.json | size: 51.51 KB | ext: .json
|   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.83 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.83 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.83 KB | ext: .csv
|   |       |   |   +---[FILE] estimation_summary.txt | size: 7.32 KB | ext: .txt
|   |       |   |   \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       |   +---[DIR] run_2026-01-22_14-37-07/
|   |       |   |   \---[FILE] estimation.log | size: 14.65 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-22_15-27-38/
|   |       |   |   \---[FILE] estimation.log | size: 11.50 KB | ext: .log
|   |       |   \---[DIR] run_2026-01-22_15-32-40/
|   |       |       +---[FILE] estimation.log | size: 23.71 KB | ext: .log
|   |       |       +---[FILE] estimation_results.json | size: 37.05 KB | ext: .json
|   |       |       +---[FILE] estimation_results_couples.csv | size: 1.14 KB | ext: .csv
|   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.14 KB | ext: .csv
|   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.14 KB | ext: .csv
|   |       |       +---[FILE] estimation_summary.txt | size: 5.15 KB | ext: .txt
|   |       |       \---[FILE] specification_used.yaml | size: 5.53 KB | ext: .yaml
|   |       +---[DIR] 2016_gamspy_fixed/
|   |       |   +---[DIR] run_2026-01-18_10-48-35/
|   |       |   |   \---[FILE] estimation.log | size: 4.11 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-18_10-50-19/
|   |       |   |   \---[FILE] estimation.log | size: 5.92 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-18_10-51-31/
|   |       |   |   \---[FILE] estimation.log | size: 8.32 KB | ext: .log
|   |       |   \---[DIR] run_2026-01-18_10-55-25/
|   |       |       +---[FILE] estimation.log | size: 23.44 KB | ext: .log
|   |       |       +---[FILE] estimation_results.json | size: 27.84 KB | ext: .json
|   |       |       +---[FILE] estimation_results_couples.csv | size: 1.95 KB | ext: .csv
|   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.95 KB | ext: .csv
|   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.95 KB | ext: .csv
|   |       |       +---[FILE] estimation_summary.txt | size: 7.32 KB | ext: .txt
|   |       |       \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       +---[DIR] 2016_gamspy_tight/
|   |       |   \---[DIR] run_2026-01-18_16-55-57/
|   |       |       +---[FILE] estimation.log | size: 23.72 KB | ext: .log
|   |       |       +---[FILE] estimation_results.json | size: 27.88 KB | ext: .json
|   |       |       +---[FILE] estimation_results_couples.csv | size: 1.95 KB | ext: .csv
|   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.95 KB | ext: .csv
|   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.95 KB | ext: .csv
|   |       |       +---[FILE] estimation_summary.txt | size: 7.32 KB | ext: .txt
|   |       |       \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       +---[DIR] 2016_legacy/
|   |       |   +---[FILE] cou_f_contours.png | size: 123.36 KB | ext: .png
|   |       |   +---[FILE] cou_f_mu.png | size: 64.89 KB | ext: .png
|   |       |   +---[FILE] cou_m_contours.png | size: 81.40 KB | ext: .png
|   |       |   +---[FILE] cou_m_mu.png | size: 69.99 KB | ext: .png
|   |       |   +---[FILE] elasticities.csv | size: 465 B | ext: .csv
|   |       |   +---[FILE] estimation.log | size: 29.67 KB | ext: .log
|   |       |   +---[FILE] estimation_results.json | size: 14.12 KB | ext: .json
|   |       |   +---[FILE] estimation_summary.txt | size: 489 B | ext: .txt
|   |       |   +---[FILE] fit_mean_hours.png | size: 30.15 KB | ext: .png
|   |       |   +---[FILE] fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   +---[FILE] muc_comparison.png | size: 76.96 KB | ext: .png
|   |       |   +---[FILE] mul_comparison.png | size: 73.23 KB | ext: .png
|   |       |   +---[FILE] negative_mu_diagnostics.png | size: 38.65 KB | ext: .png
|   |       |   +---[FILE] params.csv | size: 4.24 KB | ext: .csv
|   |       |   +---[FILE] params_with_se.csv | size: 3.44 KB | ext: .csv
|   |       |   +---[FILE] post_estimation_report_20260109_103100.html | size: 46.26 KB | ext: .html
|   |       |   +---[FILE] sf_contours.png | size: 107.35 KB | ext: .png
|   |       |   +---[FILE] sf_mu.png | size: 66.27 KB | ext: .png
|   |       |   +---[FILE] sm_contours.png | size: 87.28 KB | ext: .png
|   |       |   +---[FILE] sm_mu.png | size: 65.28 KB | ext: .png
|   |       |   \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       +---[DIR] 2016_scipy/
|   |       |   +---[DIR] run_2026-01-16_23-53-37/
|   |       |   |   \---[FILE] estimation.log | size: 18.30 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-17_15-20-10/
|   |       |   |   \---[FILE] estimation.log | size: 13.73 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-20_12-28-08/
|   |       |   |   \---[FILE] estimation.log | size: 4.13 KB | ext: .log
|   |       |   +---[DIR] run_2026-01-20_12-31-49/
|   |       |   |   +---[FILE] estimation.log | size: 28.76 KB | ext: .log
|   |       |   |   +---[FILE] estimation_results.json | size: 13.80 KB | ext: .json
|   |       |   |   +---[FILE] estimation_summary.txt | size: 488 B | ext: .txt
|   |       |   |   \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       |   +---[DIR] run_2026-01-20_14-29-22/
|   |       |   |   +---[FILE] estimation.log | size: 29.06 KB | ext: .log
|   |       |   |   +---[FILE] estimation_results.json | size: 13.93 KB | ext: .json
|   |       |   |   +---[FILE] estimation_summary.txt | size: 488 B | ext: .txt
|   |       |   |   \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       |   \---[DIR] run_2026-01-20_15-11-40/
|   |       |       +---[FILE] estimation.log | size: 29.36 KB | ext: .log
|   |       |       +---[FILE] estimation_results.json | size: 13.81 KB | ext: .json
|   |       |       +---[FILE] estimation_summary.txt | size: 488 B | ext: .txt
|   |       |       \---[FILE] specification_used.yaml | size: 13.11 KB | ext: .yaml
|   |       +---[DIR] 2016_v2/
|   |       |   +---[FILE] cou_f_contours.png | size: 121.63 KB | ext: .png
|   |       |   +---[FILE] cou_f_mu.png | size: 64.94 KB | ext: .png
|   |       |   +---[FILE] cou_m_contours.png | size: 88.23 KB | ext: .png
|   |       |   +---[FILE] cou_m_mu.png | size: 66.80 KB | ext: .png
|   |       |   +---[FILE] elasticities.csv | size: 465 B | ext: .csv
|   |       |   +---[FILE] estimation.log | size: 28.36 KB | ext: .log
|   |       |   +---[FILE] estimation_results.json | size: 15.54 KB | ext: .json
|   |       |   +---[FILE] estimation_summary.txt | size: 492 B | ext: .txt
|   |       |   +---[FILE] fit_mean_hours.png | size: 30.25 KB | ext: .png
|   |       |   +---[FILE] fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   +---[FILE] muc_comparison.png | size: 74.97 KB | ext: .png
|   |       |   +---[FILE] mul_comparison.png | size: 76.04 KB | ext: .png
|   |       |   +---[FILE] negative_mu_diagnostics.png | size: 38.75 KB | ext: .png
|   |       |   +---[FILE] parameters_with_se.csv | size: 4.06 KB | ext: .csv
|   |       |   +---[FILE] params.csv | size: 2.77 KB | ext: .csv
|   |       |   +---[FILE] post_estimation_report_20260109_092244.html | size: 48.18 KB | ext: .html
|   |       |   +---[FILE] post_estimation_report_20260109_092529.html | size: 48.18 KB | ext: .html
|   |       |   +---[FILE] sf_contours.png | size: 103.17 KB | ext: .png
|   |       |   +---[FILE] sf_mu.png | size: 66.76 KB | ext: .png
|   |       |   +---[FILE] sm_contours.png | size: 99.75 KB | ext: .png
|   |       |   +---[FILE] sm_mu.png | size: 71.33 KB | ext: .png
|   |       |   \---[FILE] specification_used.yaml | size: 10.08 KB | ext: .yaml
|   |       +---[DIR] minimal_spec/
|   |       |   \---[DIR] 2016_gamspy/
|   |       |       \---[DIR] run_2026-01-23_11-01-01/
|   |       |           +---[FILE] estimation.log | size: 22.17 KB | ext: .log
|   |       |           +---[FILE] estimation_results.json | size: 17.87 KB | ext: .json
|   |       |           +---[FILE] estimation_results_couples.csv | size: 628 B | ext: .csv
|   |       |           +---[FILE] estimation_results_singles_female.csv | size: 628 B | ext: .csv
|   |       |           +---[FILE] estimation_results_singles_male.csv | size: 628 B | ext: .csv
|   |       |           +---[FILE] estimation_summary.txt | size: 3.66 KB | ext: .txt
|   |       |           \---[FILE] specification_used.yaml | size: 3.82 KB | ext: .yaml
|   |       +---[DIR] minimal_theta0/
|   |       |   +---[DIR] 2016_gamspy/
|   |       |   |   +---[DIR] run_2026-01-23_14-10-01/
|   |       |   |   |   +---[FILE] estimation.log | size: 22.15 KB | ext: .log
|   |       |   |   |   +---[FILE] estimation_results.json | size: 18.51 KB | ext: .json
|   |       |   |   |   +---[FILE] estimation_results_couples.csv | size: 737 B | ext: .csv
|   |       |   |   |   +---[FILE] estimation_results_singles_female.csv | size: 737 B | ext: .csv
|   |       |   |   |   +---[FILE] estimation_results_singles_male.csv | size: 737 B | ext: .csv
|   |       |   |   |   +---[FILE] estimation_summary.txt | size: 3.67 KB | ext: .txt
|   |       |   |   |   \---[FILE] specification_used.yaml | size: 3.79 KB | ext: .yaml
|   |       |   |   +---[DIR] run_2026-01-23_14-49-16/
|   |       |   |   |   +---[FILE] estimation.log | size: 21.89 KB | ext: .log
|   |       |   |   |   +---[FILE] estimation_results.json | size: 15.07 KB | ext: .json
|   |       |   |   |   +---[FILE] estimation_results_couples.csv | size: 737 B | ext: .csv
|   |       |   |   |   +---[FILE] estimation_results_singles_female.csv | size: 737 B | ext: .csv
|   |       |   |   |   +---[FILE] estimation_results_singles_male.csv | size: 737 B | ext: .csv
|   |       |   |   |   +---[FILE] estimation_summary.txt | size: 3.67 KB | ext: .txt
|   |       |   |   |   \---[FILE] specification_used.yaml | size: 3.79 KB | ext: .yaml
|   |       |   |   \---[DIR] run_2026-01-23_15-41-04/
|   |       |   |       +---[FILE] estimation.log | size: 21.89 KB | ext: .log
|   |       |   |       +---[FILE] estimation_results.json | size: 11.04 KB | ext: .json
|   |       |   |       +---[FILE] estimation_results_couples.csv | size: 737 B | ext: .csv
|   |       |   |       +---[FILE] estimation_results_singles_female.csv | size: 737 B | ext: .csv
|   |       |   |       +---[FILE] estimation_results_singles_male.csv | size: 737 B | ext: .csv
|   |       |   |       +---[FILE] estimation_summary.txt | size: 3.67 KB | ext: .txt
|   |       |   |       +---[FILE] params_with_se.csv | size: 890 B | ext: .csv
|   |       |   |       \---[FILE] specification_used.yaml | size: 3.79 KB | ext: .yaml
|   |       |   \---[DIR] 2016_scipy/
|   |       |       +---[DIR] run_2026-01-23_14-13-07/
|   |       |       |   +---[FILE] estimation.log | size: 16.40 KB | ext: .log
|   |       |       |   +---[FILE] estimation_results.json | size: 8.76 KB | ext: .json
|   |       |       |   +---[FILE] estimation_summary.txt | size: 497 B | ext: .txt
|   |       |       |   \---[FILE] specification_used.yaml | size: 3.79 KB | ext: .yaml
|   |       |       +---[DIR] run_2026-01-23_14-24-06/
|   |       |       |   +---[FILE] estimation.log | size: 16.17 KB | ext: .log
|   |       |       |   +---[FILE] estimation_results.json | size: 8.75 KB | ext: .json
|   |       |       |   +---[FILE] estimation_summary.txt | size: 497 B | ext: .txt
|   |       |       |   \---[FILE] specification_used.yaml | size: 3.79 KB | ext: .yaml
|   |       |       +---[DIR] run_2026-01-23_14-27-28/
|   |       |       |   +---[FILE] estimation.log | size: 14.02 KB | ext: .log
|   |       |       |   +---[FILE] estimation_results.json | size: 8.78 KB | ext: .json
|   |       |       |   +---[FILE] estimation_summary.txt | size: 496 B | ext: .txt
|   |       |       |   \---[FILE] specification_used.yaml | size: 3.79 KB | ext: .yaml
|   |       |       +---[DIR] run_2026-01-23_14-51-29/
|   |       |       |   +---[FILE] estimation.log | size: 13.90 KB | ext: .log
|   |       |       |   +---[FILE] estimation_results.json | size: 7.06 KB | ext: .json
|   |       |       |   +---[FILE] estimation_summary.txt | size: 496 B | ext: .txt
|   |       |       |   \---[FILE] specification_used.yaml | size: 3.79 KB | ext: .yaml
|   |       |       \---[DIR] run_2026-01-23_15-42-32/
|   |       |           +---[FILE] estimation.log | size: 13.90 KB | ext: .log
|   |       |           +---[FILE] estimation_results.json | size: 7.18 KB | ext: .json
|   |       |           +---[FILE] estimation_summary.txt | size: 496 B | ext: .txt
|   |       |           \---[FILE] specification_used.yaml | size: 3.79 KB | ext: .yaml
|   |       +---[DIR] phase2/
|   |       |   +---[DIR] pooled_leisure_gamspy/
|   |       |   |   +---[DIR] run_2026-01-24_12-49-00/
|   |       |   |   |   \---[FILE] estimation.log | size: 11.62 KB | ext: .log
|   |       |   |   +---[DIR] run_2026-01-26_10-20-56/
|   |       |   |   |   \---[FILE] estimation.log | size: 11.03 KB | ext: .log
|   |       |   |   \---[DIR] run_2026-01-26_10-31-10/
|   |       |   |       \---[FILE] estimation.log | size: 20.82 KB | ext: .log
|   |       |   \---[DIR] ultra_minimal_gamspy/
|   |       |       +---[DIR] run_2026-01-24_12-49-00/
|   |       |       |   \---[FILE] estimation.log | size: 11.58 KB | ext: .log
|   |       |       +---[DIR] run_2026-01-26_10-19-18/
|   |       |       |   \---[FILE] estimation.log | size: 10.90 KB | ext: .log
|   |       |       +---[DIR] run_2026-01-26_10-20-56/
|   |       |       |   \---[FILE] estimation.log | size: 11.01 KB | ext: .log
|   |       |       \---[DIR] run_2026-01-26_10-31-10/
|   |       |           \---[FILE] estimation.log | size: 20.31 KB | ext: .log
|   |       +---[DIR] simple_spec/
|   |       |   \---[DIR] 2016_gamspy/
|   |       |       \---[DIR] run_2026-01-22_16-14-53/
|   |       |           +---[FILE] estimation.log | size: 23.61 KB | ext: .log
|   |       |           +---[FILE] estimation_results.json | size: 36.09 KB | ext: .json
|   |       |           +---[FILE] estimation_results_couples.csv | size: 1.10 KB | ext: .csv
|   |       |           +---[FILE] estimation_results_singles_female.csv | size: 1.10 KB | ext: .csv
|   |       |           +---[FILE] estimation_results_singles_male.csv | size: 1.10 KB | ext: .csv
|   |       |           +---[FILE] estimation_summary.txt | size: 5.03 KB | ext: .txt
|   |       |           \---[FILE] specification_used.yaml | size: 5.08 KB | ext: .yaml
|   |       +---[DIR] spec/
|   |       |   +---[DIR] job_choice/
|   |       |   |   \---[DIR] gamspy/
|   |       |   |       +---[DIR] estimation_spec_job_choice_v0_id_enhanced/
|   |       |   |       |   \---[DIR] run_2026-02-05_14-48-48/
|   |       |   |       |       +---[FILE] estimation.log | size: 21.25 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 26.10 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 1.43 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.43 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.43 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 4.60 KB | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 6.93 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_choice_v0_id_strict/
|   |       |   |       |   +---[DIR] run_2026-02-05_11-26-02/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 21.97 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 42.85 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 2.10 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.10 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.10 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 5.63 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 4.26 KB | ext: .yaml
|   |       |   |       |   \---[DIR] run_2026-02-05_11-36-48/
|   |       |   |       |       +---[FILE] estimation.log | size: 21.97 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 42.88 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 1.99 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.99 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.99 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 5.63 KB | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 4.26 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_choice_v0_minimal/
|   |       |   |       |   +---[DIR] run_2026-02-04_21-02-19/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 18.20 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 9.44 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 827 B | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 827 B | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 827 B | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 3.57 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 2.83 KB | ext: .yaml
|   |       |   |       |   \---[DIR] run_2026-02-04_23-33-58/
|   |       |   |       |       +---[FILE] estimation.log | size: 19.69 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 20.44 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 983 B | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 983 B | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 983 B | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 3.57 KB | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 2.84 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_choice_v0_plus/
|   |       |   |       |   +---[DIR] run_2026-02-05_00-01-13/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 23.40 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 46.79 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 2.04 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.04 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.04 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 5.86 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 4.67 KB | ext: .yaml
|   |       |   |       |   \---[DIR] run_2026-02-05_10-48-29/
|   |       |   |       |       +---[FILE] estimation.log | size: 22.27 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 46.85 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 2.11 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 2.11 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 2.11 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 5.86 KB | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 4.67 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_choice_v0_plus_b/
|   |       |   |       |   +---[DIR] run_2026-02-05_00-21-22/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 23.28 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 46.45 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 2.46 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.46 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.46 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 6.21 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 4.66 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-05_00-27-57/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 23.31 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 49.10 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 2.55 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.55 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.55 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 6.21 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 4.67 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-05_00-48-39/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 23.47 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 50.60 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 2.62 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.62 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.62 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 6.21 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 7.88 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-05_11-00-11/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 23.63 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 50.86 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 2.67 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.67 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.67 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 6.21 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 7.88 KB | ext: .yaml
|   |       |   |       |   \---[DIR] run_2026-02-05_11-07-11/
|   |       |   |       |       +---[FILE] estimation.log | size: 23.63 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 51.65 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 2.68 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 2.68 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 2.68 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 6.21 KB | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 7.91 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_choice_v0_plus_c/
|   |       |   |       |   \---[DIR] run_2026-02-05_13-34-18/
|   |       |   |       |       +---[FILE] estimation.log | size: 22.89 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 45.86 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 2.80 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 2.80 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 2.80 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 6.10 KB | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 8.57 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_choice_v1/
|   |       |   |       |   \---[DIR] run_2026-02-04_19-59-42/
|   |       |   |       |       +---[FILE] estimation.log | size: 24.56 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 54.58 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 3.63 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 3.63 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 3.63 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 7.60 KB | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 10.27 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_choice_v1_dummies/
|   |       |   |       |   \---[DIR] run_2026-02-04_16-20-22/
|   |       |   |       |       +---[FILE] estimation.log | size: 26.82 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 65.47 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 5.36 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 5.36 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 5.36 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 9.71 KB | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 13.84 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_M0/
|   |       |   |       |   +---[DIR] run_2026-02-05_15-38-28/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 20.17 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 20.32 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.17 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.17 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.17 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 3.54 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 934 B | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 2.63 KB | ext: .yaml
|   |       |   |       |   \---[DIR] run_2026-02-08_22-27-15/
|   |       |   |       |       +---[FILE] estimation.log | size: 20.08 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 11.87 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 1.18 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.18 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.18 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 3.54 KB | ext: .txt
|   |       |   |       |       +---[FILE] identification_diagnostics.txt | size: 915 B | ext: .txt
|   |       |   |       |       +---[FILE] params_with_se.csv | size: 1.22 KB | ext: .csv
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 2.63 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_M1/
|   |       |   |       |   +---[DIR] run_2026-02-05_16-19-19/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 20.92 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 21.24 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.13 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.13 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.13 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 3.64 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1.02 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 2.78 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-05_16-22-00/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 20.90 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 24.28 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.15 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.15 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.15 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 3.65 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1023 B | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 2.78 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-05_16-42-16/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 21.20 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 23.00 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.13 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.13 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.13 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 3.65 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1.02 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 3.20 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-05_16-44-46/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 21.20 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 23.62 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.13 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.13 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.13 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 3.65 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1.02 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 3.21 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-05_16-47-04/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 21.25 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 23.60 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.13 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.13 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.13 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 3.65 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1.02 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 3.21 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-05_16-50-11/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 21.25 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 23.63 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.14 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.14 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.14 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 3.65 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1.02 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 3.21 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-05_16-59-58/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 21.09 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 21.36 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.13 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.13 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.13 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 3.64 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1.02 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 3.19 KB | ext: .yaml
|   |       |   |       |   \---[DIR] run_2026-02-08_22-39-59/
|   |       |   |       |       +---[FILE] estimation.log | size: 21.09 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 12.32 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 1.14 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.14 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.14 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 3.64 KB | ext: .txt
|   |       |   |       |       +---[FILE] identification_diagnostics.txt | size: 1023 B | ext: .txt
|   |       |   |       |       +---[FILE] params_with_se.csv | size: 1.27 KB | ext: .csv
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 3.19 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_M2/
|   |       |   |       |   +---[DIR] run_2026-02-05_17-06-41/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 22.82 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 28.56 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.64 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.64 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.64 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 4.75 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1.09 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 3.96 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-05_22-46-35/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 21.91 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 27.81 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.65 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.65 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.65 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 4.75 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 996 B | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 3.96 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-08_22-52-23/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 22.68 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 15.34 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.69 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.69 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.69 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 4.74 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1016 B | ext: .txt
|   |       |   |       |   |   +---[FILE] params_with_se.csv | size: 1.76 KB | ext: .csv
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 3.96 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-08_23-28-46/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 22.69 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 29.95 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.69 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.69 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.69 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 4.74 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1.01 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 3.96 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-08_23-40-55/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 22.47 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 15.10 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.62 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.62 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.62 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 4.63 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1.00 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] params_with_se.csv | size: 1.72 KB | ext: .csv
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 5.00 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-08_23-58-54/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 22.18 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 14.77 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.53 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.53 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.53 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 4.50 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1.01 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] params_with_se.csv | size: 1.67 KB | ext: .csv
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 4.82 KB | ext: .yaml
|   |       |   |       |   \---[DIR] run_2026-02-10_10-06-29/
|   |       |   |       |       +---[FILE] estimation.log | size: 27.03 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 16.05 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 1.53 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.53 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.53 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 4.50 KB | ext: .txt
|   |       |   |       |       +---[FILE] identification_diagnostics.txt | size: 914 B | ext: .txt
|   |       |   |       |       +---[FILE] params_with_se.csv | size: 1.95 KB | ext: .csv
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 4.82 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_M2_centered/
|   |       |   |       |   \---[DIR] run_2026-02-05_21-59-58/
|   |       |   |       |       +---[FILE] estimation.log | size: 23.32 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 28.31 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 1.84 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.84 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.84 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 4.81 KB | ext: .txt
|   |       |   |       |       +---[FILE] identification_diagnostics.txt | size: 1.17 KB | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 4.00 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_M2_lite/
|   |       |   |       |   \---[DIR] run_2026-02-05_22-33-18/
|   |       |   |       |       +---[FILE] estimation.log | size: 21.58 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 23.92 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 1.58 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.58 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.58 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 4.20 KB | ext: .txt
|   |       |   |       |       +---[FILE] identification_diagnostics.txt | size: 932 B | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 3.59 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_M2_lite_scaled/
|   |       |   |       |   \---[DIR] run_2026-02-05_23-07-11/
|   |       |   |       |       +---[FILE] estimation.log | size: 21.10 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 23.91 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 800 B | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 800 B | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 800 B | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 4.11 KB | ext: .txt
|   |       |   |       |       +---[FILE] identification_diagnostics.txt | size: 891 B | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 3.65 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_M2_scaled/
|   |       |   |       |   \---[DIR] run_2026-02-05_23-00-19/
|   |       |   |       |       +---[FILE] estimation.log | size: 21.90 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 27.57 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 1014 B | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1014 B | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1014 B | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 4.72 KB | ext: .txt
|   |       |   |       |       +---[FILE] identification_diagnostics.txt | size: 915 B | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 4.01 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_M2b/
|   |       |   |       |   +---[DIR] run_2026-02-11_14-37-13/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 29.10 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 41.85 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.53 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.53 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.53 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 4.78 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 937 B | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 5.78 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-11_14-40-10/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 28.82 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 42.77 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.54 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.54 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.54 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 4.78 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 906 B | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 5.78 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-11_14-46-29/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 28.65 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 40.72 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.48 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.48 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.48 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 4.66 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1023 B | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 5.63 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-11_15-13-14/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 30.15 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 43.78 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.60 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.60 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.60 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 4.89 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 907 B | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 5.67 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-11_15-17-57/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 29.83 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 43.90 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.60 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.60 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.60 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 4.89 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1023 B | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 5.67 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-19_10-20-18/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 29.17 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 42.63 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.54 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.54 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.54 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 4.78 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1023 B | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 5.52 KB | ext: .yaml
|   |       |   |       |   \---[DIR] run_2026-02-19_10-38-45/
|   |       |   |       |       +---[FILE] estimation.log | size: 28.50 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 41.22 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 1.48 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.48 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.48 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 4.66 KB | ext: .txt
|   |       |   |       |       +---[FILE] identification_diagnostics.txt | size: 1023 B | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 5.40 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_M2c/
|   |       |   |       |   +---[DIR] run_2026-02-19_10-48-35/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 31.05 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 55.33 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 2.31 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.31 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.31 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 6.49 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1.00 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 8.26 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-19_11-30-40/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 32.80 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 55.76 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 2.35 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.35 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.35 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 6.49 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 1.00 KB | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 8.26 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-19_11-46-04/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 31.27 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 53.44 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 2.24 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.24 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.24 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 6.27 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 905 B | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 7.92 KB | ext: .yaml
|   |       |   |       |   +---[DIR] run_2026-02-19_13-19-11/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 31.27 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 53.44 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 2.24 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.24 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.24 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 6.27 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 905 B | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 7.92 KB | ext: .yaml
|   |       |   |       |   \---[DIR] run_2026-02-19_13-37-33/
|   |       |   |       |       +---[FILE] estimation.log | size: 31.21 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 53.84 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 2.24 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 2.24 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 2.24 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 6.26 KB | ext: .txt
|   |       |   |       |       +---[FILE] identification_diagnostics.txt | size: 933 B | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 8.05 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_M2d_type/
|   |       |   |       |   +---[DIR] run_2026-02-19_15-10-31/
|   |       |   |       |   |   +---[FILE] estimation.log | size: 28.62 KB | ext: .log
|   |       |   |       |   |   +---[FILE] estimation_results.json | size: 41.17 KB | ext: .json
|   |       |   |       |   |   +---[FILE] estimation_results_couples.csv | size: 1.45 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_female.csv | size: 1.45 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_results_singles_male.csv | size: 1.45 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] estimation_summary.txt | size: 6.09 KB | ext: .txt
|   |       |   |       |   |   +---[FILE] identification_diagnostics.txt | size: 918 B | ext: .txt
|   |       |   |       |   |   \---[FILE] specification_used.yaml | size: 6.24 KB | ext: .yaml
|   |       |   |       |   \---[DIR] run_2026-02-19_16-20-59/
|   |       |   |       |       +---[FILE] estimation.log | size: 27.67 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 39.49 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 1.39 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.39 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.39 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 5.86 KB | ext: .txt
|   |       |   |       |       +---[FILE] identification_diagnostics.txt | size: 915 B | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 5.90 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_M2e_a/
|   |       |   |       |   \---[DIR] run_2026-02-20_10-04-46/
|   |       |   |       |       +---[FILE] estimation.log | size: 32.88 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 47.75 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 1.73 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.73 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.73 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 6.88 KB | ext: .txt
|   |       |   |       |       +---[FILE] identification_diagnostics.txt | size: 968 B | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 8.99 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_M2e_b/
|   |       |   |       |   \---[DIR] run_2026-02-20_11-24-37/
|   |       |   |       |       +---[FILE] estimation.log | size: 32.97 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 45.23 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 1.68 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.68 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.68 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 6.65 KB | ext: .txt
|   |       |   |       |       +---[FILE] identification_diagnostics.txt | size: 915 B | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 8.24 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_M2e_hours/
|   |       |   |       |   \---[DIR] run_2026-02-20_09-28-35/
|   |       |   |       |       +---[FILE] estimation.log | size: 27.90 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 41.41 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 1.45 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.45 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.45 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 6.20 KB | ext: .txt
|   |       |   |       |       +---[FILE] identification_diagnostics.txt | size: 999 B | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 6.88 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_M2f_hybrid/
|   |       |   |       |   \---[DIR] run_2026-02-19_16-55-27/
|   |       |   |       |       +---[FILE] estimation.log | size: 33.56 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 48.71 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 1.74 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.74 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.74 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 6.77 KB | ext: .txt
|   |       |   |       |       +---[FILE] identification_diagnostics.txt | size: 1.01 KB | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 7.31 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_M2g_unified_opportunity/
|   |       |   |       |   \---[DIR] run_2026-02-20_10-18-58/
|   |       |   |       |       +---[FILE] estimation.log | size: 35.62 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 51.99 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 1.86 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.86 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.86 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 7.23 KB | ext: .txt
|   |       |   |       |       +---[FILE] identification_diagnostics.txt | size: 1.14 KB | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 8.35 KB | ext: .yaml
|   |       |   |       +---[DIR] estimation_spec_job_M2h_pruned/
|   |       |   |       |   \---[DIR] run_2026-02-20_11-25-18/
|   |       |   |       |       +---[FILE] estimation.log | size: 33.08 KB | ext: .log
|   |       |   |       |       +---[FILE] estimation_results.json | size: 45.98 KB | ext: .json
|   |       |   |       |       +---[FILE] estimation_results_couples.csv | size: 1.64 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_female.csv | size: 1.64 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_results_singles_male.csv | size: 1.64 KB | ext: .csv
|   |       |   |       |       +---[FILE] estimation_summary.txt | size: 6.54 KB | ext: .txt
|   |       |   |       |       +---[FILE] identification_diagnostics.txt | size: 1.03 KB | ext: .txt
|   |       |   |       |       \---[FILE] specification_used.yaml | size: 6.80 KB | ext: .yaml
|   |       |   |       \---[DIR] unknown_spec/
|   |       |   |           +---[DIR] run_2026-02-04_23-32-08/
|   |       |   |           |   \---[FILE] estimation.log | size: 2.62 KB | ext: .log
|   |       |   |           +---[DIR] run_2026-02-05_21-48-01/
|   |       |   |           |   \---[FILE] estimation.log | size: 19.04 KB | ext: .log
|   |       |   |           +---[DIR] run_2026-02-10_10-05-46/
|   |       |   |           |   \---[FILE] estimation.log | size: 4.50 KB | ext: .log
|   |       |   |           +---[DIR] run_2026-02-10_10-06-07/
|   |       |   |           |   \---[FILE] estimation.log | size: 4.50 KB | ext: .log
|   |       |   |           +---[DIR] run_2026-02-11_15-11-19/
|   |       |   |           |   \---[FILE] estimation.log | size: 8.84 KB | ext: .log
|   |       |   |           \---[DIR] run_2026-02-19_10-47-05/
|   |       |   |               \---[FILE] estimation.log | size: 3.11 KB | ext: .log
|   |       |   +---[DIR] v1/
|   |       |   |   +---[DIR] gamspy/
|   |       |   |   \---[DIR] scipy/
|   |       |   +---[DIR] v2/
|   |       |   |   +---[DIR] gamspy/
|   |       |   |   |   +---[DIR] run_2026-01-27_12-27-02/
|   |       |   |   |   |   +---[FILE] estimation.log | size: 26.70 KB | ext: .log
|   |       |   |   |   |   +---[FILE] estimation_results.json | size: 57.89 KB | ext: .json
|   |       |   |   |   |   +---[FILE] estimation_results_couples.csv | size: 2.28 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.28 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.28 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_summary.txt | size: 7.78 KB | ext: .txt
|   |       |   |   |   |   \---[FILE] specification_used.yaml | size: 10.09 KB | ext: .yaml
|   |       |   |   |   +---[DIR] run_2026-01-28_11-39-59/
|   |       |   |   |   |   +---[FILE] estimation.log | size: 26.53 KB | ext: .log
|   |       |   |   |   |   +---[FILE] estimation_results.json | size: 57.89 KB | ext: .json
|   |       |   |   |   |   +---[FILE] estimation_results_couples.csv | size: 2.28 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.28 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.28 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_summary.txt | size: 7.78 KB | ext: .txt
|   |       |   |   |   |   \---[FILE] specification_used.yaml | size: 10.09 KB | ext: .yaml
|   |       |   |   |   +---[DIR] run_2026-01-28_11-57-43/
|   |       |   |   |   |   +---[FILE] estimation.log | size: 16.73 KB | ext: .log
|   |       |   |   |   |   +---[FILE] estimation_results.json | size: 24.75 KB | ext: .json
|   |       |   |   |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.33 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_summary.txt | size: 2.91 KB | ext: .txt
|   |       |   |   |   |   \---[FILE] specification_used.yaml | size: 10.09 KB | ext: .yaml
|   |       |   |   |   +---[DIR] run_2026-01-28_12-45-18/
|   |       |   |   |   |   +---[FILE] estimation.log | size: 24.42 KB | ext: .log
|   |       |   |   |   |   +---[FILE] estimation_results.json | size: 59.18 KB | ext: .json
|   |       |   |   |   |   +---[FILE] estimation_results_couples.csv | size: 2.29 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.29 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.29 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_summary.txt | size: 7.77 KB | ext: .txt
|   |       |   |   |   |   \---[FILE] specification_used.yaml | size: 10.09 KB | ext: .yaml
|   |       |   |   |   +---[DIR] run_2026-01-28_12-52-23/
|   |       |   |   |   |   +---[FILE] estimation.log | size: 23.89 KB | ext: .log
|   |       |   |   |   |   +---[FILE] estimation_results.json | size: 57.15 KB | ext: .json
|   |       |   |   |   |   +---[FILE] estimation_results_couples.csv | size: 2.29 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.29 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.29 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_summary.txt | size: 7.77 KB | ext: .txt
|   |       |   |   |   |   \---[FILE] specification_used.yaml | size: 10.09 KB | ext: .yaml
|   |       |   |   |   +---[DIR] run_2026-01-28_13-22-08/
|   |       |   |   |   |   +---[FILE] estimation.log | size: 26.25 KB | ext: .log
|   |       |   |   |   |   +---[FILE] estimation_results.json | size: 56.15 KB | ext: .json
|   |       |   |   |   |   +---[FILE] estimation_results_couples.csv | size: 2.25 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.25 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.25 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_summary.txt | size: 7.78 KB | ext: .txt
|   |       |   |   |   |   \---[FILE] specification_used.yaml | size: 10.09 KB | ext: .yaml
|   |       |   |   |   +---[DIR] run_2026-01-28_13-45-56/
|   |       |   |   |   |   +---[FILE] estimation.log | size: 23.90 KB | ext: .log
|   |       |   |   |   |   +---[FILE] estimation_results.json | size: 55.92 KB | ext: .json
|   |       |   |   |   |   +---[FILE] estimation_results_couples.csv | size: 2.30 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.30 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.30 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_summary.txt | size: 7.77 KB | ext: .txt
|   |       |   |   |   |   \---[FILE] specification_used.yaml | size: 10.09 KB | ext: .yaml
|   |       |   |   |   +---[DIR] run_2026-01-28_14-03-24/
|   |       |   |   |   |   +---[FILE] estimation.log | size: 23.90 KB | ext: .log
|   |       |   |   |   |   +---[FILE] estimation_results.json | size: 55.92 KB | ext: .json
|   |       |   |   |   |   +---[FILE] estimation_results_couples.csv | size: 2.30 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.30 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.30 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_summary.txt | size: 7.78 KB | ext: .txt
|   |       |   |   |   |   \---[FILE] specification_used.yaml | size: 10.09 KB | ext: .yaml
|   |       |   |   |   +---[DIR] run_2026-01-28_14-08-57/
|   |       |   |   |   |   +---[FILE] estimation.log | size: 24.26 KB | ext: .log
|   |       |   |   |   |   +---[FILE] estimation_results.json | size: 54.96 KB | ext: .json
|   |       |   |   |   |   +---[FILE] estimation_results_couples.csv | size: 2.31 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.31 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.31 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_summary.txt | size: 7.76 KB | ext: .txt
|   |       |   |   |   |   \---[FILE] specification_used.yaml | size: 10.09 KB | ext: .yaml
|   |       |   |   |   +---[DIR] run_2026-01-28_14-10-55/
|   |       |   |   |   |   +---[FILE] estimation.log | size: 24.43 KB | ext: .log
|   |       |   |   |   |   +---[FILE] estimation_results.json | size: 57.94 KB | ext: .json
|   |       |   |   |   |   +---[FILE] estimation_results_couples.csv | size: 2.30 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.30 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.30 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_summary.txt | size: 7.78 KB | ext: .txt
|   |       |   |   |   |   \---[FILE] specification_used.yaml | size: 10.09 KB | ext: .yaml
|   |       |   |   |   +---[DIR] run_2026-01-29_11-48-10/
|   |       |   |   |   |   +---[FILE] estimation.log | size: 24.43 KB | ext: .log
|   |       |   |   |   |   +---[FILE] estimation_results.json | size: 57.94 KB | ext: .json
|   |       |   |   |   |   +---[FILE] estimation_results_couples.csv | size: 2.30 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_female.csv | size: 2.30 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_results_singles_male.csv | size: 2.30 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] estimation_summary.txt | size: 7.77 KB | ext: .txt
|   |       |   |   |   |   \---[FILE] specification_used.yaml | size: 10.09 KB | ext: .yaml
|   |       |   |   |   \---[DIR] run_2026-02-02_18-05-03/
|   |       |   |   |       +---[FILE] estimation.log | size: 24.43 KB | ext: .log
|   |       |   |   |       +---[FILE] estimation_results.json | size: 57.94 KB | ext: .json
|   |       |   |   |       +---[FILE] estimation_results_couples.csv | size: 2.30 KB | ext: .csv
|   |       |   |   |       +---[FILE] estimation_results_singles_female.csv | size: 2.30 KB | ext: .csv
|   |       |   |   |       +---[FILE] estimation_results_singles_male.csv | size: 2.30 KB | ext: .csv
|   |       |   |   |       +---[FILE] estimation_summary.txt | size: 7.77 KB | ext: .txt
|   |       |   |   |       \---[FILE] specification_used.yaml | size: 10.09 KB | ext: .yaml
|   |       |   |   \---[DIR] scipy/
|   |       |   |       +---[DIR] run_2026-01-27_12-09-18/
|   |       |   |       |   +---[FILE] estimation.log | size: 29.70 KB | ext: .log
|   |       |   |       |   +---[FILE] estimation_results.json | size: 25.96 KB | ext: .json
|   |       |   |       |   +---[FILE] estimation_summary.txt | size: 491 B | ext: .txt
|   |       |   |       |   \---[FILE] specification_used.yaml | size: 10.09 KB | ext: .yaml
|   |       |   |       \---[DIR] run_2026-01-28_13-19-18/
|   |       |   |           +---[FILE] estimation.log | size: 16.08 KB | ext: .log
|   |       |   |           +---[FILE] estimation_results.json | size: 26.08 KB | ext: .json
|   |       |   |           +---[FILE] estimation_summary.txt | size: 489 B | ext: .txt
|   |       |   |           \---[FILE] specification_used.yaml | size: 10.09 KB | ext: .yaml
|   |       |   \---[DIR] v3/
|   |       |       \---[DIR] gamspy/
|   |       |           +---[DIR] run_2026-02-02_18-15-46/
|   |       |           |   +---[FILE] estimation.log | size: 25.18 KB | ext: .log
|   |       |           |   +---[FILE] estimation_results.json | size: 61.92 KB | ext: .json
|   |       |           |   +---[FILE] estimation_results_couples.csv | size: 3.40 KB | ext: .csv
|   |       |           |   +---[FILE] estimation_results_singles_female.csv | size: 3.40 KB | ext: .csv
|   |       |           |   +---[FILE] estimation_results_singles_male.csv | size: 3.40 KB | ext: .csv
|   |       |           |   +---[FILE] estimation_summary.txt | size: 8.26 KB | ext: .txt
|   |       |           |   \---[FILE] specification_used.yaml | size: 10.94 KB | ext: .yaml
|   |       |           +---[DIR] run_2026-02-02_18-52-34/
|   |       |           |   +---[FILE] estimation.log | size: 25.01 KB | ext: .log
|   |       |           |   +---[FILE] estimation_results.json | size: 61.82 KB | ext: .json
|   |       |           |   +---[FILE] estimation_results_couples.csv | size: 3.42 KB | ext: .csv
|   |       |           |   +---[FILE] estimation_results_singles_female.csv | size: 3.42 KB | ext: .csv
|   |       |           |   +---[FILE] estimation_results_singles_male.csv | size: 3.42 KB | ext: .csv
|   |       |           |   +---[FILE] estimation_summary.txt | size: 8.25 KB | ext: .txt
|   |       |           |   \---[FILE] specification_used.yaml | size: 10.94 KB | ext: .yaml
|   |       |           +---[DIR] run_2026-02-02_19-08-45/
|   |       |           |   +---[FILE] estimation.log | size: 25.02 KB | ext: .log
|   |       |           |   +---[FILE] estimation_results.json | size: 62.22 KB | ext: .json
|   |       |           |   +---[FILE] estimation_results_couples.csv | size: 3.35 KB | ext: .csv
|   |       |           |   +---[FILE] estimation_results_singles_female.csv | size: 3.35 KB | ext: .csv
|   |       |           |   +---[FILE] estimation_results_singles_male.csv | size: 3.35 KB | ext: .csv
|   |       |           |   +---[FILE] estimation_summary.txt | size: 8.25 KB | ext: .txt
|   |       |           |   \---[FILE] specification_used.yaml | size: 11.25 KB | ext: .yaml
|   |       |           +---[DIR] run_2026-02-03_00-23-08/
|   |       |           |   \---[FILE] estimation.log | size: 14.13 KB | ext: .log
|   |       |           +---[DIR] run_2026-02-03_00-25-51/
|   |       |           |   +---[FILE] estimation.log | size: 25.18 KB | ext: .log
|   |       |           |   +---[FILE] estimation_results.json | size: 63.96 KB | ext: .json
|   |       |           |   +---[FILE] estimation_results_couples.csv | size: 3.41 KB | ext: .csv
|   |       |           |   +---[FILE] estimation_results_singles_female.csv | size: 3.41 KB | ext: .csv
|   |       |           |   +---[FILE] estimation_results_singles_male.csv | size: 3.41 KB | ext: .csv
|   |       |           |   +---[FILE] estimation_summary.txt | size: 8.25 KB | ext: .txt
|   |       |           |   \---[FILE] specification_used.yaml | size: 14.99 KB | ext: .yaml
|   |       |           +---[DIR] run_2026-02-03_00-52-33/
|   |       |           |   +---[FILE] estimation.log | size: 25.16 KB | ext: .log
|   |       |           |   +---[FILE] estimation_results.json | size: 63.35 KB | ext: .json
|   |       |           |   +---[FILE] estimation_results_couples.csv | size: 3.43 KB | ext: .csv
|   |       |           |   +---[FILE] estimation_results_singles_female.csv | size: 3.43 KB | ext: .csv
|   |       |           |   +---[FILE] estimation_results_singles_male.csv | size: 3.43 KB | ext: .csv
|   |       |           |   +---[FILE] estimation_summary.txt | size: 8.25 KB | ext: .txt
|   |       |           |   \---[FILE] specification_used.yaml | size: 14.99 KB | ext: .yaml
|   |       |           \---[DIR] run_2026-02-05_14-11-43/
|   |       |               +---[FILE] estimation.log | size: 25.45 KB | ext: .log
|   |       |               +---[FILE] estimation_results.json | size: 63.45 KB | ext: .json
|   |       |               +---[FILE] estimation_results_couples.csv | size: 3.48 KB | ext: .csv
|   |       |               +---[FILE] estimation_results_singles_female.csv | size: 3.48 KB | ext: .csv
|   |       |               +---[FILE] estimation_results_singles_male.csv | size: 3.48 KB | ext: .csv
|   |       |               +---[FILE] estimation_summary.txt | size: 8.25 KB | ext: .txt
|   |       |               \---[FILE] specification_used.yaml | size: 14.99 KB | ext: .yaml
|   |       +---[DIR] spec_tests/
|   |       |   +---[DIR] 1_minimal_theta0_scipy/
|   |       |   |   \---[DIR] run_2026-01-24_11-30-21/
|   |       |   |       +---[FILE] estimation.log | size: 13.75 KB | ext: .log
|   |       |   |       +---[FILE] estimation_results.json | size: 7.08 KB | ext: .json
|   |       |   |       +---[FILE] estimation_summary.txt | size: 496 B | ext: .txt
|   |       |   |       \---[FILE] specification_used.yaml | size: 3.79 KB | ext: .yaml
|   |       |   +---[DIR] 2_pooled_consumption_scipy/
|   |       |   |   \---[DIR] run_2026-01-24_12-14-56/
|   |       |   |       +---[FILE] estimation.log | size: 18.55 KB | ext: .log
|   |       |   |       +---[FILE] estimation_results.json | size: 6.76 KB | ext: .json
|   |       |   |       +---[FILE] estimation_summary.txt | size: 499 B | ext: .txt
|   |       |   |       \---[FILE] specification_used.yaml | size: 3.38 KB | ext: .yaml
|   |       |   +---[DIR] 3_pooled_leisure_scipy/
|   |       |   |   \---[DIR] run_2026-01-24_12-18-20/
|   |       |   |       +---[FILE] estimation.log | size: 17.49 KB | ext: .log
|   |       |   |       +---[FILE] estimation_results.json | size: 6.76 KB | ext: .json
|   |       |   |       +---[FILE] estimation_summary.txt | size: 502 B | ext: .txt
|   |       |   |       \---[FILE] specification_used.yaml | size: 3.24 KB | ext: .yaml
|   |       |   \---[DIR] 4_ultra_minimal_scipy/
|   |       |       \---[DIR] run_2026-01-24_12-18-20/
|   |       |           +---[FILE] estimation.log | size: 15.64 KB | ext: .log
|   |       |           +---[FILE] estimation_results.json | size: 5.33 KB | ext: .json
|   |       |           +---[FILE] estimation_summary.txt | size: 498 B | ext: .txt
|   |       |           \---[FILE] specification_used.yaml | size: 3.00 KB | ext: .yaml
|   |       +---[DIR] spec_v2/
|   |       |   +---[DIR] run_2026-01-27_11-39-07/
|   |       |   |   +---[FILE] estimation.log | size: 48.00 KB | ext: .log
|   |       |   |   +---[FILE] estimation_results.json | size: 24.98 KB | ext: .json
|   |       |   |   +---[FILE] estimation_summary.txt | size: 492 B | ext: .txt
|   |       |   |   \---[FILE] specification_used.yaml | size: 10.09 KB | ext: .yaml
|   |       |   \---[DIR] run_2026-01-27_12-09-18/
|   |       |       +---[FILE] estimation.log | size: 29.70 KB | ext: .log
|   |       |       +---[FILE] estimation_results.json | size: 25.96 KB | ext: .json
|   |       |       +---[FILE] estimation_summary.txt | size: 491 B | ext: .txt
|   |       |       \---[FILE] specification_used.yaml | size: 10.09 KB | ext: .yaml
|   |       \---[DIR] V1_gamspy/
|   |           \---[DIR] run_2026-01-27_11-27-43/
|   |               +---[FILE] estimation.log | size: 26.69 KB | ext: .log
|   |               +---[FILE] estimation_results.json | size: 52.94 KB | ext: .json
|   |               +---[FILE] estimation_results_couples.csv | size: 1.93 KB | ext: .csv
|   |               +---[FILE] estimation_results_singles_female.csv | size: 1.93 KB | ext: .csv
|   |               +---[FILE] estimation_results_singles_male.csv | size: 1.93 KB | ext: .csv
|   |               +---[FILE] estimation_summary.txt | size: 7.32 KB | ext: .txt
|   |               \---[FILE] specification_used.yaml | size: 13.07 KB | ext: .yaml
|   +---[DIR] logs/
|   |   +---[FILE] fr_2016_enhanced_pipeline_2026-01-30_17-10-35.txt | size: 8.93 KB | ext: .txt
|   |   +---[FILE] fr_2016_enhanced_pipeline_2026-02-02_16-57-15.txt | size: 2.90 KB | ext: .txt
|   |   +---[FILE] fr_2016_enhanced_pipeline_2026-02-02_17-39-24.txt | size: 170.99 KB | ext: .txt
|   |   +---[FILE] fr_2016_enhanced_pipeline_2026-02-05_13-59-31.txt | size: 37.62 KB | ext: .txt
|   |   \---[FILE] session_2026-02-19_15-02-47.txt | size: 5.30 KB | ext: .txt
|   +---[DIR] post_estimation/
|   |   \---[DIR] fr/
|   |       +---[DIR] 2016/
|   |       |   +---[DIR] joint/
|   |       |   |   +---[FILE] cou_f_mu.png | size: 78.47 KB | ext: .png
|   |       |   |   +---[FILE] cou_m_mu.png | size: 78.95 KB | ext: .png
|   |       |   |   +---[FILE] couples_f_contours.png | size: 120.54 KB | ext: .png
|   |       |   |   +---[FILE] couples_m_contours.png | size: 120.54 KB | ext: .png
|   |       |   |   +---[FILE] elasticities.csv | size: 415 B | ext: .csv
|   |       |   |   +---[FILE] fit_mean_hours.png | size: 28.43 KB | ext: .png
|   |       |   |   +---[FILE] fit_participation.png | size: 29.74 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_joint_diagnostics.html | size: 27.38 KB | ext: .html
|   |       |   |   +---[FILE] muc_comparison.png | size: 66.12 KB | ext: .png
|   |       |   |   +---[FILE] mul_comparison.png | size: 64.06 KB | ext: .png
|   |       |   |   +---[FILE] negative_mu_diagnostics.png | size: 41.43 KB | ext: .png
|   |       |   |   +---[FILE] params.csv | size: 3.61 KB | ext: .csv
|   |       |   |   +---[FILE] post_estimation_report_20260108_183607.html | size: 48.68 KB | ext: .html
|   |       |   |   +---[FILE] sf_mu.png | size: 61.88 KB | ext: .png
|   |       |   |   +---[FILE] singles_female_contours.png | size: 113.02 KB | ext: .png
|   |       |   |   +---[FILE] singles_male_contours.png | size: 90.64 KB | ext: .png
|   |       |   |   +---[FILE] sm_mu.png | size: 65.05 KB | ext: .png
|   |       |   |   +---[FILE] vw_pooled_cou_f_mu.png | size: 76.17 KB | ext: .png
|   |       |   |   +---[FILE] vw_pooled_cou_m_mu.png | size: 75.98 KB | ext: .png
|   |       |   |   +---[FILE] vw_pooled_couples_f_contours.png | size: 101.09 KB | ext: .png
|   |       |   |   +---[FILE] vw_pooled_couples_m_contours.png | size: 101.09 KB | ext: .png
|   |       |   |   +---[FILE] vw_pooled_elasticities.csv | size: 405 B | ext: .csv
|   |       |   |   +---[FILE] vw_pooled_fit_mean_hours.png | size: 34.72 KB | ext: .png
|   |       |   |   +---[FILE] vw_pooled_fit_participation.png | size: 33.49 KB | ext: .png
|   |       |   |   +---[FILE] vw_pooled_muc_comparison.png | size: 62.16 KB | ext: .png
|   |       |   |   +---[FILE] vw_pooled_mul_comparison.png | size: 78.73 KB | ext: .png
|   |       |   |   +---[FILE] vw_pooled_params.csv | size: 3.67 KB | ext: .csv
|   |       |   |   +---[FILE] vw_pooled_post_estimation_report.html | size: 39.51 KB | ext: .html
|   |       |   |   +---[FILE] vw_pooled_post_estimation_report2.html | size: 40.25 KB | ext: .html
|   |       |   |   +---[FILE] vw_pooled_sf_mu.png | size: 72.20 KB | ext: .png
|   |       |   |   +---[FILE] vw_pooled_singles_female_contours.png | size: 106.12 KB | ext: .png
|   |       |   |   +---[FILE] vw_pooled_singles_male_contours.png | size: 99.89 KB | ext: .png
|   |       |   |   \---[FILE] vw_pooled_sm_mu.png | size: 73.70 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug_cou_f_mu.png | size: 76.17 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug_cou_m_mu.png | size: 75.98 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug_couples_f_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug_couples_m_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug_muc_comparison.png | size: 62.16 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug_mul_comparison.png | size: 78.73 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug_sf_mu.png | size: 72.20 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug_singles_female_contours.png | size: 106.12 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug_singles_male_contours.png | size: 99.89 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug_sm_mu.png | size: 73.70 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug2_cou_f_mu.png | size: 76.17 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug2_cou_m_mu.png | size: 75.98 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug2_couples_f_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug2_couples_m_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug2_muc_comparison.png | size: 62.16 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug2_mul_comparison.png | size: 78.73 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug2_sf_mu.png | size: 72.20 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug2_singles_female_contours.png | size: 106.12 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug2_singles_male_contours.png | size: 99.89 KB | ext: .png
|   |       |   +---[FILE] fr_2016_debug2_sm_mu.png | size: 73.70 KB | ext: .png
|   |       |   +---[FILE] fr_2016_final_cou_f_mu.png | size: 79.20 KB | ext: .png
|   |       |   +---[FILE] fr_2016_final_cou_m_mu.png | size: 78.52 KB | ext: .png
|   |       |   +---[FILE] fr_2016_final_couples_f_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_final_couples_m_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_final_elasticities.csv | size: 405 B | ext: .csv
|   |       |   +---[FILE] fr_2016_final_fit_mean_hours.png | size: 34.51 KB | ext: .png
|   |       |   +---[FILE] fr_2016_final_fit_participation.png | size: 33.49 KB | ext: .png
|   |       |   +---[FILE] fr_2016_final_muc_comparison.png | size: 62.16 KB | ext: .png
|   |       |   +---[FILE] fr_2016_final_mul_comparison.png | size: 78.73 KB | ext: .png
|   |       |   +---[FILE] fr_2016_final_params.csv | size: 3.67 KB | ext: .csv
|   |       |   +---[FILE] fr_2016_final_post_estimation_report.html | size: 39.58 KB | ext: .html
|   |       |   +---[FILE] fr_2016_final_sf_mu.png | size: 71.51 KB | ext: .png
|   |       |   +---[FILE] fr_2016_final_singles_female_contours.png | size: 106.12 KB | ext: .png
|   |       |   +---[FILE] fr_2016_final_singles_male_contours.png | size: 99.89 KB | ext: .png
|   |       |   +---[FILE] fr_2016_final_sm_mu.png | size: 72.49 KB | ext: .png
|   |       |   +---[FILE] fr_2016_fixed_cou_f_mu.png | size: 81.24 KB | ext: .png
|   |       |   +---[FILE] fr_2016_fixed_cou_m_mu.png | size: 77.57 KB | ext: .png
|   |       |   +---[FILE] fr_2016_fixed_couples_f_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_fixed_couples_m_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_fixed_elasticities.csv | size: 405 B | ext: .csv
|   |       |   +---[FILE] fr_2016_fixed_fit_mean_hours.png | size: 34.51 KB | ext: .png
|   |       |   +---[FILE] fr_2016_fixed_fit_participation.png | size: 33.49 KB | ext: .png
|   |       |   +---[FILE] fr_2016_fixed_muc_comparison.png | size: 62.16 KB | ext: .png
|   |       |   +---[FILE] fr_2016_fixed_mul_comparison.png | size: 78.73 KB | ext: .png
|   |       |   +---[FILE] fr_2016_fixed_params.csv | size: 3.67 KB | ext: .csv
|   |       |   +---[FILE] fr_2016_fixed_post_estimation_report.html | size: 39.60 KB | ext: .html
|   |       |   +---[FILE] fr_2016_fixed_sf_mu.png | size: 73.44 KB | ext: .png
|   |       |   +---[FILE] fr_2016_fixed_singles_female_contours.png | size: 106.12 KB | ext: .png
|   |       |   +---[FILE] fr_2016_fixed_singles_male_contours.png | size: 99.89 KB | ext: .png
|   |       |   +---[FILE] fr_2016_fixed_sm_mu.png | size: 77.48 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_cou_f_mu.png | size: 81.08 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_cou_m_mu.png | size: 81.01 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_couples_f_contours.png | size: 83.33 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_couples_m_contours.png | size: 83.32 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_elasticities.csv | size: 413 B | ext: .csv
|   |       |   +---[FILE] fr_2016_joint_fit_mean_hours.png | size: 30.07 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_muc_comparison.png | size: 63.38 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_mul_comparison.png | size: 65.33 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_negative_mu_diagnostics.png | size: 39.69 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_params.csv | size: 3.64 KB | ext: .csv
|   |       |   +---[FILE] fr_2016_joint_post_est_contour_couples_f.png | size: 84.72 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_post_est_contour_couples_m.png | size: 85.03 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_post_est_contour_singles_female.png | size: 77.35 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_post_est_contour_singles_male.png | size: 73.28 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_post_est_elasticities.csv | size: 1.13 KB | ext: .csv
|   |       |   +---[FILE] fr_2016_joint_post_est_fit.csv | size: 654 B | ext: .csv
|   |       |   +---[FILE] fr_2016_joint_post_est_fit_comparison.png | size: 66.06 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_post_est_marginal_utilities.csv | size: 517 B | ext: .csv
|   |       |   +---[FILE] fr_2016_joint_post_est_marginal_utilities.png | size: 70.55 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_post_est_params.csv | size: 2.94 KB | ext: .csv
|   |       |   +---[FILE] fr_2016_joint_post_estimation_report.html | size: 39.58 KB | ext: .html
|   |       |   +---[FILE] fr_2016_joint_post_estimation_report_20260109_002221.html | size: 48.42 KB | ext: .html
|   |       |   +---[FILE] fr_2016_joint_sf_mu.png | size: 67.66 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_singles_female_contours.png | size: 111.49 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_singles_male_contours.png | size: 98.71 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_sm_mu.png | size: 65.63 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_test2_cou_f_mu.png | size: 79.20 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_test2_cou_m_mu.png | size: 78.52 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_test2_couples_f_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_test2_couples_m_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_test2_elasticities.csv | size: 405 B | ext: .csv
|   |       |   +---[FILE] fr_2016_joint_test2_fit_mean_hours.png | size: 34.51 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_test2_fit_participation.png | size: 33.49 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_test2_muc_comparison.png | size: 62.16 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_test2_mul_comparison.png | size: 78.73 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_test2_params.csv | size: 3.67 KB | ext: .csv
|   |       |   +---[FILE] fr_2016_joint_test2_post_estimation_report.html | size: 39.63 KB | ext: .html
|   |       |   +---[FILE] fr_2016_joint_test2_sf_mu.png | size: 71.51 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_test2_singles_female_contours.png | size: 106.12 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_test2_singles_male_contours.png | size: 99.89 KB | ext: .png
|   |       |   +---[FILE] fr_2016_joint_test2_sm_mu.png | size: 72.49 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled_cou_f_mu.png | size: 76.17 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled_cou_m_mu.png | size: 75.98 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled_couples_f_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled_couples_m_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled_elasticities.csv | size: 405 B | ext: .csv
|   |       |   +---[FILE] fr_2016_styled_fit_mean_hours.png | size: 34.72 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled_fit_participation.png | size: 33.49 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled_muc_comparison.png | size: 62.16 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled_mul_comparison.png | size: 78.73 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled_params.csv | size: 3.67 KB | ext: .csv
|   |       |   +---[FILE] fr_2016_styled_post_estimation_report.html | size: 40.30 KB | ext: .html
|   |       |   +---[FILE] fr_2016_styled_sf_mu.png | size: 72.20 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled_singles_female_contours.png | size: 106.12 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled_singles_male_contours.png | size: 99.89 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled_sm_mu.png | size: 73.70 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled2_cou_f_mu.png | size: 76.17 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled2_cou_m_mu.png | size: 75.98 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled2_couples_f_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled2_couples_m_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled2_elasticities.csv | size: 405 B | ext: .csv
|   |       |   +---[FILE] fr_2016_styled2_fit_mean_hours.png | size: 34.72 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled2_fit_participation.png | size: 33.49 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled2_muc_comparison.png | size: 62.16 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled2_mul_comparison.png | size: 78.73 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled2_params.csv | size: 3.67 KB | ext: .csv
|   |       |   +---[FILE] fr_2016_styled2_post_estimation_report.html | size: 40.32 KB | ext: .html
|   |       |   +---[FILE] fr_2016_styled2_sf_mu.png | size: 72.20 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled2_singles_female_contours.png | size: 106.12 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled2_singles_male_contours.png | size: 99.89 KB | ext: .png
|   |       |   +---[FILE] fr_2016_styled2_sm_mu.png | size: 73.70 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test_cou_f_mu.png | size: 76.17 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test_cou_m_mu.png | size: 75.98 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test_couples_f_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test_couples_m_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test_elasticities.csv | size: 405 B | ext: .csv
|   |       |   +---[FILE] fr_2016_test_fit_mean_hours.png | size: 34.51 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test_fit_participation.png | size: 33.49 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test_muc_comparison.png | size: 62.16 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test_mul_comparison.png | size: 78.73 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test_params.csv | size: 3.67 KB | ext: .csv
|   |       |   +---[FILE] fr_2016_test_post_estimation_report.html | size: 39.57 KB | ext: .html
|   |       |   +---[FILE] fr_2016_test_sf_mu.png | size: 72.20 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test_singles_female_contours.png | size: 106.12 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test_singles_male_contours.png | size: 99.89 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test_sm_mu.png | size: 73.70 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test3_cou_f_mu.png | size: 76.17 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test3_cou_m_mu.png | size: 75.98 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test3_couples_f_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test3_couples_m_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test3_fit_mean_hours.png | size: 34.72 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test3_fit_participation.png | size: 33.49 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test3_muc_comparison.png | size: 62.16 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test3_mul_comparison.png | size: 78.73 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test3_sf_mu.png | size: 72.20 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test3_singles_female_contours.png | size: 106.12 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test3_singles_male_contours.png | size: 99.89 KB | ext: .png
|   |       |   +---[FILE] fr_2016_test3_sm_mu.png | size: 73.70 KB | ext: .png
|   |       |   +---[FILE] fr_2016_v2_cou_f_mu.png | size: 81.24 KB | ext: .png
|   |       |   +---[FILE] fr_2016_v2_cou_m_mu.png | size: 77.57 KB | ext: .png
|   |       |   +---[FILE] fr_2016_v2_couples_f_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_v2_couples_m_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] fr_2016_v2_elasticities.csv | size: 405 B | ext: .csv
|   |       |   +---[FILE] fr_2016_v2_fit_mean_hours.png | size: 34.51 KB | ext: .png
|   |       |   +---[FILE] fr_2016_v2_fit_participation.png | size: 33.49 KB | ext: .png
|   |       |   +---[FILE] fr_2016_v2_muc_comparison.png | size: 62.16 KB | ext: .png
|   |       |   +---[FILE] fr_2016_v2_mul_comparison.png | size: 78.73 KB | ext: .png
|   |       |   +---[FILE] fr_2016_v2_params.csv | size: 3.67 KB | ext: .csv
|   |       |   +---[FILE] fr_2016_v2_post_estimation_report.html | size: 40.26 KB | ext: .html
|   |       |   +---[FILE] fr_2016_v2_sf_mu.png | size: 73.44 KB | ext: .png
|   |       |   +---[FILE] fr_2016_v2_singles_female_contours.png | size: 106.12 KB | ext: .png
|   |       |   +---[FILE] fr_2016_v2_singles_male_contours.png | size: 99.89 KB | ext: .png
|   |       |   +---[FILE] fr_2016_v2_sm_mu.png | size: 77.48 KB | ext: .png
|   |       |   +---[FILE] test_styled_cou_f_mu.png | size: 76.17 KB | ext: .png
|   |       |   +---[FILE] test_styled_cou_m_mu.png | size: 75.98 KB | ext: .png
|   |       |   +---[FILE] test_styled_couples_f_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] test_styled_couples_m_contours.png | size: 101.09 KB | ext: .png
|   |       |   +---[FILE] test_styled_elasticities.csv | size: 405 B | ext: .csv
|   |       |   +---[FILE] test_styled_fit_mean_hours.png | size: 34.73 KB | ext: .png
|   |       |   +---[FILE] test_styled_fit_participation.png | size: 33.48 KB | ext: .png
|   |       |   +---[FILE] test_styled_muc_comparison.png | size: 62.16 KB | ext: .png
|   |       |   +---[FILE] test_styled_mul_comparison.png | size: 78.73 KB | ext: .png
|   |       |   +---[FILE] test_styled_negative_mu_diagnostics.png | size: 46.08 KB | ext: .png
|   |       |   +---[FILE] test_styled_params.csv | size: 3.67 KB | ext: .csv
|   |       |   +---[FILE] test_styled_post_estimation_report_20260107_173433.html | size: 40.98 KB | ext: .html
|   |       |   +---[FILE] test_styled_sf_mu.png | size: 72.20 KB | ext: .png
|   |       |   +---[FILE] test_styled_singles_female_contours.png | size: 106.12 KB | ext: .png
|   |       |   +---[FILE] test_styled_singles_male_contours.png | size: 99.89 KB | ext: .png
|   |       |   \---[FILE] test_styled_sm_mu.png | size: 73.70 KB | ext: .png
|   |       +---[DIR] 2016_gamspy_styled/
|   |       |   +---[DIR] run_2026-01-20_16-28-04/
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 65.39 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 66.67 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_couples_f_contours.png | size: 93.28 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_couples_m_contours.png | size: 72.41 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 403 B | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.20 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 58.68 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 61.82 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 30.94 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 13.68 KB | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260120_162816.html | size: 83.93 KB | ext: .html
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 59.40 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_singles_female_contours.png | size: 48.33 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_singles_male_contours.png | size: 48.34 KB | ext: .png
|   |       |   |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 59.59 KB | ext: .png
|   |       |   +---[DIR] run_2026-01-20_16-57-54/
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 93.28 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 65.39 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 72.41 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 66.67 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 464 B | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.13 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 80.15 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 88.54 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 4.33 KB | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260120_165805.html | size: 47.74 KB | ext: .html
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 120.49 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 66.88 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 118.68 KB | ext: .png
|   |       |   |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 67.90 KB | ext: .png
|   |       |   +---[DIR] run_2026-01-20_23-09-09/
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 93.28 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 65.39 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 72.41 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 66.67 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 464 B | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.13 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 80.15 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 88.54 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 4.33 KB | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260120_230921.html | size: 56.30 KB | ext: .html
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 120.49 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 66.88 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 118.68 KB | ext: .png
|   |       |   |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 67.90 KB | ext: .png
|   |       |   +---[DIR] run_2026-01-20_23-29-23/
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 93.28 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 65.39 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 72.41 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 66.67 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 403 B | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.13 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 79.19 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 84.97 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 4.33 KB | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260120_232937.html | size: 55.75 KB | ext: .html
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 120.49 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 66.88 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 118.68 KB | ext: .png
|   |       |   |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 67.90 KB | ext: .png
|   |       |   +---[DIR] run_2026-01-20_23-44-28/
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 93.28 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 65.39 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 72.41 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 66.67 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 403 B | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.13 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 79.19 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 84.97 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 4.33 KB | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260120_234441.html | size: 52.43 KB | ext: .html
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 120.49 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 66.88 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 118.68 KB | ext: .png
|   |       |   |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 67.90 KB | ext: .png
|   |       |   +---[DIR] run_2026-01-21_01-36-34/
|   |       |   +---[DIR] run_2026-01-22_01-19-30/
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 93.28 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 65.39 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 72.41 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 66.67 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 403 B | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.13 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 79.19 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 84.97 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 4.33 KB | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260122_011942.html | size: 52.44 KB | ext: .html
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 120.49 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 66.88 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 118.68 KB | ext: .png
|   |       |   |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 67.90 KB | ext: .png
|   |       |   +---[DIR] run_2026-01-22_14-38-30/
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 93.28 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 65.39 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 72.41 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 66.67 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 403 B | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.13 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 79.19 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 84.97 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 4.33 KB | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260122_143839.html | size: 86.76 KB | ext: .html
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 120.49 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 66.88 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 118.68 KB | ext: .png
|   |       |   |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 67.90 KB | ext: .png
|   |       |   +---[DIR] run_2026-01-22_15-52-12/
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 93.28 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 65.39 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 72.41 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 66.67 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 403 B | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.13 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 79.19 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 84.97 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 4.33 KB | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260122_155222.html | size: 86.76 KB | ext: .html
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 120.49 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 66.88 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 118.68 KB | ext: .png
|   |       |   |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 67.90 KB | ext: .png
|   |       |   +---[DIR] run_2026-01-22_15-55-39/
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 88.62 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 65.86 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 74.35 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 68.49 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 403 B | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.16 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 80.51 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 81.18 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 2.47 KB | ext: .csv
|   |       |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260122_155549.html | size: 67.92 KB | ext: .html
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 120.82 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 67.26 KB | ext: .png
|   |       |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 119.90 KB | ext: .png
|   |       |   |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 68.20 KB | ext: .png
|   |       |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 75.61 KB | ext: .png
|   |       |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 77.44 KB | ext: .png
|   |       |   +---[FILE] fr_2016_gamspy_couples_f_contours.png | size: 75.10 KB | ext: .png
|   |       |   +---[FILE] fr_2016_gamspy_couples_m_contours.png | size: 81.31 KB | ext: .png
|   |       |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 412 B | ext: .csv
|   |       |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.19 KB | ext: .png
|   |       |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 60.37 KB | ext: .png
|   |       |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 73.22 KB | ext: .png
|   |       |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 30.94 KB | ext: .png
|   |       |   +---[FILE] fr_2016_gamspy_params.csv | size: 8.30 KB | ext: .csv
|   |       |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260116_203143.html | size: 78.39 KB | ext: .html
|   |       |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260117_200443.html | size: 77.31 KB | ext: .html
|   |       |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 60.56 KB | ext: .png
|   |       |   +---[FILE] fr_2016_gamspy_singles_female_contours.png | size: 48.85 KB | ext: .png
|   |       |   +---[FILE] fr_2016_gamspy_singles_male_contours.png | size: 48.84 KB | ext: .png
|   |       |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 60.75 KB | ext: .png
|   |       +---[DIR] minimal_spec/
|   |       |   +---[DIR] 2016_gamspy_styled/
|   |       |   |   \---[DIR] run_2026-01-23_11-16-24/
|   |       |   |       +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 103.78 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 66.42 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 101.71 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 65.94 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_elasticities.csv | size: 402 B | ext: .csv
|   |       |   |       +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.17 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.46 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 76.79 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 87.66 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_params.csv | size: 1.14 KB | ext: .csv
|   |       |   |       +---[FILE] fr_2016_gamspy_post_estimation_report_20260123_111634.html | size: 49.16 KB | ext: .html
|   |       |   |       +---[FILE] fr_2016_gamspy_sf_contours.png | size: 117.94 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_sf_mu.png | size: 64.99 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_sm_contours.png | size: 116.51 KB | ext: .png
|   |       |   |       \---[FILE] fr_2016_gamspy_sm_mu.png | size: 64.04 KB | ext: .png
|   |       |   \---[DIR] 2016_scipy_styled/
|   |       |       \---[DIR] run_2026-01-23_14-54-28/
|   |       |           +---[FILE] fr_2016_scispy_cou_f_contours.png | size: 107.99 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_cou_f_mu.png | size: 63.52 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_cou_m_contours.png | size: 99.98 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_cou_m_mu.png | size: 63.96 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_elasticities.csv | size: 402 B | ext: .csv
|   |       |           +---[FILE] fr_2016_scispy_fit_mean_hours.png | size: 31.64 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_fit_participation.png | size: 30.13 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_muc_comparison.png | size: 73.18 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_mul_comparison.png | size: 87.41 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_params.csv | size: 1.20 KB | ext: .csv
|   |       |           +---[FILE] fr_2016_scispy_post_estimation_report_20260123_145437.html | size: 47.98 KB | ext: .html
|   |       |           +---[FILE] fr_2016_scispy_sf_contours.png | size: 116.98 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_sf_mu.png | size: 63.03 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_sm_contours.png | size: 115.70 KB | ext: .png
|   |       |           \---[FILE] fr_2016_scispy_sm_mu.png | size: 63.63 KB | ext: .png
|   |       +---[DIR] minimal_theta0/
|   |       |   +---[DIR] 2016_gamspy_styled/
|   |       |   |   +---[DIR] run_2026-01-23_14-32-23/
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 107.99 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 63.52 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 99.98 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 63.96 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 402 B | ext: .csv
|   |       |   |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 31.64 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.13 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 73.18 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 87.41 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 1.16 KB | ext: .csv
|   |       |   |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260123_143232.html | size: 49.48 KB | ext: .html
|   |       |   |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 116.98 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 63.03 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 115.70 KB | ext: .png
|   |       |   |   |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 63.63 KB | ext: .png
|   |       |   |   +---[DIR] run_2026-01-23_15-03-39/
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 107.99 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 63.52 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 99.98 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 63.96 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 402 B | ext: .csv
|   |       |   |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 31.64 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.13 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 73.18 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 87.41 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 1.20 KB | ext: .csv
|   |       |   |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260123_150348.html | size: 46.08 KB | ext: .html
|   |       |   |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 116.98 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 63.03 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 115.70 KB | ext: .png
|   |       |   |   |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 63.63 KB | ext: .png
|   |       |   |   +---[DIR] run_2026-01-23_15-05-04/
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 107.99 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 63.52 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 99.98 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 63.96 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 402 B | ext: .csv
|   |       |   |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 31.64 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.13 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 73.18 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 87.41 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 1.20 KB | ext: .csv
|   |       |   |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260123_150513.html | size: 46.08 KB | ext: .html
|   |       |   |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 116.98 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 63.03 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 115.70 KB | ext: .png
|   |       |   |   |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 63.63 KB | ext: .png
|   |       |   |   +---[DIR] run_2026-01-23_15-57-21/
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 107.99 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 63.52 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 99.98 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 63.96 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 31.64 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.13 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 73.18 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 87.41 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 116.98 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 63.03 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 115.70 KB | ext: .png
|   |       |   |   |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 63.63 KB | ext: .png
|   |       |   |   +---[DIR] run_2026-01-23_16-03-10/
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 107.99 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 63.52 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 99.98 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 63.96 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 402 B | ext: .csv
|   |       |   |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 31.64 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.13 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 73.18 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 87.41 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 1.32 KB | ext: .csv
|   |       |   |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260123_160320.html | size: 38.14 KB | ext: .html
|   |       |   |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 116.98 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 63.03 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 115.70 KB | ext: .png
|   |       |   |   |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 63.63 KB | ext: .png
|   |       |   |   \---[DIR] run_2026-01-23_16-06-17/
|   |       |   |       +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 107.99 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 63.52 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 99.98 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 63.96 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_elasticities.csv | size: 402 B | ext: .csv
|   |       |   |       +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 31.64 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.13 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 73.18 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 87.41 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_params.csv | size: 1.31 KB | ext: .csv
|   |       |   |       +---[FILE] fr_2016_gamspy_post_estimation_report_20260123_160634.html | size: 39.37 KB | ext: .html
|   |       |   |       +---[FILE] fr_2016_gamspy_sf_contours.png | size: 116.98 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_sf_mu.png | size: 63.03 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_gamspy_sm_contours.png | size: 115.70 KB | ext: .png
|   |       |   |       \---[FILE] fr_2016_gamspy_sm_mu.png | size: 63.63 KB | ext: .png
|   |       |   \---[DIR] 2016_scipy_styled/
|   |       |       +---[DIR] run_2026-01-23_15-22-00/
|   |       |       |   +---[FILE] fr_2016_scispy_cou_f_contours.png | size: 107.99 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_scispy_cou_f_mu.png | size: 63.52 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_scispy_cou_m_contours.png | size: 99.98 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_scispy_cou_m_mu.png | size: 63.96 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_scispy_elasticities.csv | size: 402 B | ext: .csv
|   |       |       |   +---[FILE] fr_2016_scispy_fit_mean_hours.png | size: 31.64 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_scispy_fit_participation.png | size: 30.13 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_scispy_muc_comparison.png | size: 73.18 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_scispy_mul_comparison.png | size: 87.41 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_scispy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_scispy_params.csv | size: 1.20 KB | ext: .csv
|   |       |       |   +---[FILE] fr_2016_scispy_post_estimation_report_20260123_152209.html | size: 40.42 KB | ext: .html
|   |       |       |   +---[FILE] fr_2016_scispy_sf_contours.png | size: 116.98 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_scispy_sf_mu.png | size: 63.03 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_scispy_sm_contours.png | size: 115.70 KB | ext: .png
|   |       |       |   \---[FILE] fr_2016_scispy_sm_mu.png | size: 63.63 KB | ext: .png
|   |       |       \---[DIR] run_2026-01-23_15-43-49/
|   |       |           +---[FILE] fr_2016_scispy_cou_f_contours.png | size: 107.99 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_cou_f_mu.png | size: 63.52 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_cou_m_contours.png | size: 99.98 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_cou_m_mu.png | size: 63.96 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_elasticities.csv | size: 402 B | ext: .csv
|   |       |           +---[FILE] fr_2016_scispy_fit_mean_hours.png | size: 31.64 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_fit_participation.png | size: 30.13 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_muc_comparison.png | size: 73.18 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_mul_comparison.png | size: 87.41 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_params.csv | size: 1.32 KB | ext: .csv
|   |       |           +---[FILE] fr_2016_scispy_post_estimation_report_20260123_154358.html | size: 38.13 KB | ext: .html
|   |       |           +---[FILE] fr_2016_scispy_sf_contours.png | size: 116.98 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_sf_mu.png | size: 63.03 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scispy_sm_contours.png | size: 115.70 KB | ext: .png
|   |       |           \---[FILE] fr_2016_scispy_sm_mu.png | size: 63.63 KB | ext: .png
|   |       +---[DIR] simple_spec/
|   |       |   \---[DIR] 2016_gamspy_styled/
|   |       |       +---[DIR] run_2026-01-23_10-16-00/
|   |       |       |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 98.02 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 62.04 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 86.87 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 60.66 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 404 B | ext: .csv
|   |       |       |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.14 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 70.28 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 95.30 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_params.csv | size: 2.31 KB | ext: .csv
|   |       |       |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260123_101610.html | size: 66.07 KB | ext: .html
|   |       |       |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 120.33 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 66.21 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 118.19 KB | ext: .png
|   |       |       |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 66.58 KB | ext: .png
|   |       |       +---[DIR] run_2026-01-23_10-32-02/
|   |       |       |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 98.02 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 62.04 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 86.87 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 60.66 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 404 B | ext: .csv
|   |       |       |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.14 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 70.28 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 95.30 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_params.csv | size: 2.31 KB | ext: .csv
|   |       |       |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260123_103211.html | size: 66.07 KB | ext: .html
|   |       |       |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 120.33 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 66.21 KB | ext: .png
|   |       |       |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 118.19 KB | ext: .png
|   |       |       |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 66.58 KB | ext: .png
|   |       |       \---[DIR] run_2026-01-23_10-46-54/
|   |       |           +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 98.02 KB | ext: .png
|   |       |           +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 62.04 KB | ext: .png
|   |       |           +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 86.87 KB | ext: .png
|   |       |           +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 60.66 KB | ext: .png
|   |       |           +---[FILE] fr_2016_gamspy_elasticities.csv | size: 404 B | ext: .csv
|   |       |           +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.14 KB | ext: .png
|   |       |           +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |           +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 70.28 KB | ext: .png
|   |       |           +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 95.30 KB | ext: .png
|   |       |           +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |           +---[FILE] fr_2016_gamspy_params.csv | size: 2.31 KB | ext: .csv
|   |       |           +---[FILE] fr_2016_gamspy_post_estimation_report_20260123_104704.html | size: 66.46 KB | ext: .html
|   |       |           +---[FILE] fr_2016_gamspy_sf_contours.png | size: 120.33 KB | ext: .png
|   |       |           +---[FILE] fr_2016_gamspy_sf_mu.png | size: 66.21 KB | ext: .png
|   |       |           +---[FILE] fr_2016_gamspy_sm_contours.png | size: 118.19 KB | ext: .png
|   |       |           \---[FILE] fr_2016_gamspy_sm_mu.png | size: 66.58 KB | ext: .png
|   |       +---[DIR] spec/
|   |       |   +---[DIR] job_choice/
|   |       |   |   \---[DIR] gamspy/
|   |       |   |       +---[DIR] estimation_spec_job_choice_v0_id_enhanced/
|   |       |   |       |   \---[DIR] run_2026-02-05_14-54-15/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 70.65 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 68.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 74.28 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 62.13 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 412 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 31.09 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.08 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.58 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.10 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.18 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.05 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 49.58 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 47.95 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 48.58 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 50.48 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 48.27 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.93 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.61 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.66 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 41.55 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.73 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 49.06 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 63.14 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 1.63 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_145437.html | size: 48.82 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 73.15 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 61.83 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 69.51 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 62.61 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 96.45 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 98.15 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 92.67 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 93.05 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 96.00 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_choice_v0_id_strict/
|   |       |   |       |   +---[DIR] run_2026-02-05_11-41-19/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 83.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 62.57 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 79.42 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 65.16 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 31.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 29.98 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.11 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.49 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.14 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.21 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.06 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 45.16 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.39 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 44.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 43.82 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.97 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.61 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.56 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.39 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.66 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 56.87 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 59.95 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 39.93 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 2.77 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_114141.html | size: 53.44 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 81.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 64.39 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 85.71 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 65.42 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 94.49 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 98.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 94.97 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 94.51 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 93.21 KB | ext: .png
|   |       |   |       |   \---[DIR] run_2026-02-05_11-49-04/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 83.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 62.57 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 79.42 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 65.16 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 31.26 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 29.98 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.11 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.49 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.14 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.21 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.06 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 45.16 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.39 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 44.84 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 43.82 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.97 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.61 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.56 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.39 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.66 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 56.87 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 59.95 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 39.93 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 2.77 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_114926.html | size: 53.44 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 81.31 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 64.39 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 85.71 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 65.42 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 94.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 98.44 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 93.85 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 94.72 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 94.97 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_choice_v0_minimal/
|   |       |   |       |   +---[DIR] run_2026-02-04_21-07-58/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_cou_f_contours.png | size: 109.68 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_cou_f_mu.png | size: 63.22 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_cou_m_contours.png | size: 110.08 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_cou_m_mu.png | size: 61.98 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_elasticities.csv | size: 402 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_fit_mean_hours.png | size: 31.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_fit_participation.png | size: 29.89 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_hours_distribution_couples_female.png | size: 59.17 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_hours_distribution_couples_male.png | size: 59.48 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_hours_distribution_singles_female.png | size: 56.64 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_hours_distribution_singles_male.png | size: 56.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_hours_distribution_total.png | size: 54.77 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_muc_comparison.png | size: 65.65 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_mul_comparison.png | size: 80.50 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_params.csv | size: 773 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_post_estimation_report_20260204_210815.html | size: 36.22 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_sf_contours.png | size: 55.99 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_sf_mu.png | size: 64.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_sm_contours.png | size: 56.46 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_sm_mu.png | size: 67.28 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_wage_distribution_couples_female.png | size: 98.50 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_wage_distribution_couples_male.png | size: 106.82 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_wage_distribution_singles_female.png | size: 96.34 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_wage_distribution_singles_male.png | size: 95.52 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_wage_distribution_total.png | size: 99.78 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-04_22-57-46/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_cou_f_contours.png | size: 109.68 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_cou_f_mu.png | size: 63.22 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_cou_m_contours.png | size: 110.08 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_cou_m_mu.png | size: 61.98 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_elasticities.csv | size: 402 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_fit_mean_hours.png | size: 31.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_fit_participation.png | size: 29.89 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_hours_distribution_couples_female.png | size: 57.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_hours_distribution_couples_male.png | size: 57.59 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_hours_distribution_singles_female.png | size: 57.13 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_hours_distribution_singles_male.png | size: 57.20 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_hours_distribution_total.png | size: 56.04 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_job_distribution_couples_female.png | size: 47.40 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_job_distribution_couples_male.png | size: 47.59 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_job_distribution_singles_female.png | size: 48.35 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_job_distribution_singles_male.png | size: 48.75 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_job_distribution_total.png | size: 47.42 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_loc_distribution_couples_female.png | size: 42.06 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_loc_distribution_couples_male.png | size: 36.66 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_loc_distribution_singles_female.png | size: 38.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_loc_distribution_singles_male.png | size: 38.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_loc_distribution_total.png | size: 36.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_muc_comparison.png | size: 65.65 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_mul_comparison.png | size: 80.50 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_params.csv | size: 773 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_post_estimation_report_20260204_225808.html | size: 37.63 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_sf_contours.png | size: 55.99 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_sf_mu.png | size: 64.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_sm_contours.png | size: 56.46 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_sm_mu.png | size: 67.28 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_wage_distribution_couples_female.png | size: 97.32 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_wage_distribution_couples_male.png | size: 98.71 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_wage_distribution_singles_female.png | size: 93.34 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_wage_distribution_singles_male.png | size: 92.92 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_wage_distribution_total.png | size: 96.18 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-04_23-40-16/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 87.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 65.53 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 82.21 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 66.57 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 30.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 30.49 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.12 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.55 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.13 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 44.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.45 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 44.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 43.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.97 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.61 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.53 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.41 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.68 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 60.44 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 61.01 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 1.41 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260204_234038.html | size: 36.12 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 82.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 70.06 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 81.79 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 64.91 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 94.85 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 98.04 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 95.17 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 95.02 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 93.66 KB | ext: .png
|   |       |   |       |   \---[DIR] run_2026-02-04_23-48-59/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 87.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 65.53 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 82.21 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 66.57 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 30.54 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 30.49 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.12 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.55 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.13 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.23 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.05 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 44.96 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.45 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 44.84 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 43.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.97 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.61 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.53 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.41 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.68 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 60.44 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 61.01 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 1.41 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260204_234921.html | size: 36.46 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 82.33 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 70.06 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 81.79 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 64.91 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 95.02 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 96.99 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 95.30 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 96.17 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 95.70 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_choice_v0_plus/
|   |       |   |       |   +---[DIR] run_2026-02-05_00-06-16/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 77.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 64.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 76.36 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 62.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 412 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 31.08 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.11 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.61 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.15 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.16 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.08 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 45.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.71 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 45.35 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 44.11 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.95 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.64 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.57 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.46 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.68 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 48.95 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 66.07 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 3.10 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_000639.html | size: 46.68 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 72.99 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 68.36 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 64.18 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 58.85 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 96.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 98.20 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 93.95 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 94.43 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 94.98 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-05_00-12-33/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 77.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 64.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 76.36 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 62.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 412 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 31.08 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.11 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.61 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.15 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.16 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.08 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 45.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.71 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 45.35 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 44.11 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.95 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.64 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.57 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.46 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.68 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 48.95 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 66.07 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 3.10 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_001255.html | size: 54.84 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 72.99 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 68.36 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 64.18 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 58.85 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 96.88 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 98.40 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 94.51 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 94.71 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 95.92 KB | ext: .png
|   |       |   |       |   \---[DIR] run_2026-02-05_10-53-24/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 77.20 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 66.55 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 76.25 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 71.89 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 412 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 31.06 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.11 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.59 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.14 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.17 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.08 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 44.89 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.70 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 45.55 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 44.99 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 44.13 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.97 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.63 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.57 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.46 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.68 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 54.42 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 66.28 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 3.03 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_105346.html | size: 54.37 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 76.19 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 69.49 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 79.95 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 59.85 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 95.92 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 97.62 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 94.65 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 94.74 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 95.64 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_choice_v0_plus_b/
|   |       |   |       |   +---[DIR] run_2026-02-05_00-34-16/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 76.34 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 67.15 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 70.89 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 65.73 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 413 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 30.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 29.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.08 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.59 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.14 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.20 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.08 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 48.93 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 47.67 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 48.86 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 46.02 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 48.37 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.95 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.63 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.46 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.69 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 48.02 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 69.15 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 35.19 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 3.48 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_003438.html | size: 57.00 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 62.32 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 64.90 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 65.55 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 63.68 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 95.27 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 98.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 93.99 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 95.25 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 94.88 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-05_10-20-34/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 70.21 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 68.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 69.52 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 64.64 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 413 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 30.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 29.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.06 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.57 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.15 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.22 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.06 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 48.21 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 47.65 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 48.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 49.15 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 47.48 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.99 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.66 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 41.55 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.72 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 50.90 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 66.68 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 36.12 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 3.65 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_102057.html | size: 56.34 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 71.55 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 61.91 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 70.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 65.98 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 94.78 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 97.44 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 93.06 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 94.47 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 95.59 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-05_11-11-46/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 72.74 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 65.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 67.82 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 69.77 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 413 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 30.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 29.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.07 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.15 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.21 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.07 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 48.29 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 47.63 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 49.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.50 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 48.38 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.62 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.57 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.69 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 50.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 65.03 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 35.07 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 3.91 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_111209.html | size: 56.14 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 70.78 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 68.64 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 65.34 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 58.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 94.93 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 98.16 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 94.25 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 95.79 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 95.58 KB | ext: .png
|   |       |   |       |   \---[DIR] run_2026-02-05_11-19-32/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 72.74 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 65.60 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 67.82 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 69.77 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 413 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 30.54 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 29.83 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.07 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.58 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.15 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.21 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.07 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 48.29 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 47.63 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 49.31 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.50 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 48.38 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.96 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.62 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.57 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.69 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 50.83 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 65.03 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 35.07 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 3.91 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_111954.html | size: 56.14 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 70.78 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 68.64 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 65.34 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 58.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 94.73 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 98.44 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 93.52 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 95.47 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 95.75 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_choice_v0_plus_c/
|   |       |   |       |   \---[DIR] run_2026-02-05_13-41-16/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 76.84 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 67.35 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 70.33 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 63.11 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 411 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 30.53 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 29.80 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.06 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.57 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.29 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.18 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.06 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 48.43 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 47.59 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 48.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 50.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 48.49 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.97 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.60 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.68 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 41.51 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.70 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 49.65 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 65.22 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 36.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 2.83 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_134138.html | size: 56.69 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 63.62 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 69.91 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 74.74 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 65.22 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 94.91 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 97.86 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 92.23 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 93.93 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 95.06 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_M0/
|   |       |   |       |   +---[DIR] run_2026-02-05_16-05-25/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 86.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 64.79 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 84.09 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 62.78 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 30.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 30.49 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.12 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.55 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.13 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 44.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.45 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 44.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 43.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.97 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.61 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.53 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.42 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.68 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 53.93 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 62.55 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 1.34 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_160547.html | size: 44.12 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 81.27 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 67.25 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 78.69 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 65.72 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 95.77 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 97.56 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 94.70 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 95.53 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 95.72 KB | ext: .png
|   |       |   |       |   \---[DIR] run_2026-02-08_22-32-26/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 88.21 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 64.44 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 87.14 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 64.62 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.28 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.32 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.21 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.36 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 48.54 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.78 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.87 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.59 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.36 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.86 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.28 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.98 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 56.40 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 70.51 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 1.55 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260208_223310.html | size: 43.21 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 88.28 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 62.42 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 83.94 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 67.73 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.35 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 76.87 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.73 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.41 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.84 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_M1/
|   |       |   |       |   +---[DIR] run_2026-02-05_16-26-39/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 85.62 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 65.49 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 78.15 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 63.99 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 411 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 30.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 30.49 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.55 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.12 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 45.16 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.44 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 44.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 43.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.98 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.62 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.52 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.42 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.67 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 56.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 58.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 1.65 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_162702.html | size: 45.06 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 82.78 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 63.64 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 85.44 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 63.95 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 95.91 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 99.22 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 95.04 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 94.59 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 95.26 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-05_16-54-58/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 88.61 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 63.30 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 46.55 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 62.00 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 421 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 30.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 30.49 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.11 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.55 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.11 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 45.16 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 44.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 43.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.98 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.64 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.52 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.42 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.68 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 56.99 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 56.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 1.66 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_165520.html | size: 45.65 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 81.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 65.19 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 83.95 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 65.07 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 93.27 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 98.40 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 95.22 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 95.22 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 96.95 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-05_17-02-30/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 87.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 65.53 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 82.21 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 66.57 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 30.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 30.49 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.12 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.55 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.13 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 44.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.45 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 44.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 43.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.97 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.61 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.53 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.41 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.68 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 60.44 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 61.01 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 1.63 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_170253.html | size: 44.68 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 82.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 70.06 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 81.79 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 64.91 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 93.30 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 98.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 95.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 95.16 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 94.81 KB | ext: .png
|   |       |   |       |   \---[DIR] run_2026-02-08_22-42-37/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 87.98 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 63.52 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 87.48 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 63.39 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.28 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.32 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.21 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.36 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 48.53 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.78 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.13 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.62 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.22 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.36 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.86 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.29 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.97 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 56.35 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 68.27 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 1.83 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260208_224320.html | size: 43.97 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 86.10 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 62.70 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 84.02 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 64.91 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.59 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.22 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.72 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.41 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.77 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_M2/
|   |       |   |       |   +---[DIR] run_2026-02-05_17-10-17/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 85.67 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 62.74 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 81.92 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 65.04 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 30.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 30.49 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.13 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.21 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.06 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 44.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 44.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 43.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.98 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.62 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.53 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.43 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.68 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 55.07 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 56.64 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 2.20 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_171040.html | size: 51.45 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 82.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 63.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 80.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 60.82 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 95.29 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 97.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 94.88 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 95.48 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 93.80 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-05_22-50-01/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 85.67 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 62.74 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 81.92 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 65.04 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 30.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 30.49 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.13 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.21 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.06 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 44.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 44.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 43.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.98 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.62 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.53 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.43 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.68 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 55.07 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 56.64 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 1.99 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_225024.html | size: 51.33 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 82.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 63.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 80.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 60.82 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 95.85 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 98.38 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 95.25 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 95.46 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 94.18 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-08_22-57-17/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 88.95 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 66.46 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 87.71 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 64.97 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.27 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.20 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 47.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 48.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.57 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.64 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.36 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.85 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 60.43 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 68.48 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 2.45 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260208_225809.html | size: 50.55 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 84.04 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 65.86 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 87.74 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 65.16 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.40 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.91 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.39 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.70 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-08_23-32-14/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 88.95 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 66.46 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 87.71 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 64.97 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.27 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.20 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 47.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 48.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.57 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.64 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.36 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.85 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 60.43 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 68.48 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 2.94 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260208_233241.html | size: 49.11 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 84.04 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 65.86 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 87.74 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 65.16 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.51 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.18 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.70 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.62 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.68 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-08_23-40-15/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 88.95 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 66.46 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 87.71 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 64.97 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.27 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.20 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 47.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 48.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.57 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.64 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.36 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.85 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 60.43 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 68.48 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 2.94 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260208_234041.html | size: 49.11 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 84.04 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 65.86 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 87.74 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 65.16 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.36 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.13 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.42 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.48 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.69 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-08_23-51-32/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 88.94 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 66.07 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 87.71 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 65.08 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.27 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.20 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 47.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 48.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.57 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.64 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.36 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.85 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 60.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 68.41 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 2.39 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260208_235225.html | size: 49.83 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 84.37 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 66.22 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 87.52 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 64.75 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.38 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.11 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.72 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.35 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.65 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-09_00-01-19/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 88.94 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 66.07 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 87.71 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 65.08 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.27 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.20 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 47.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 48.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.57 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.64 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.36 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.85 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 60.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 68.41 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 2.32 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260209_000211.html | size: 49.10 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 84.37 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 66.22 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 87.52 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 64.75 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.51 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.01 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.42 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.54 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-10_10-10-21/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 88.94 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 66.07 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 87.71 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 65.08 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.27 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.20 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 47.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 48.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.57 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.64 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.36 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.85 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 60.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 68.41 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 2.78 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260210_101050.html | size: 47.00 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 84.37 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 66.22 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 87.52 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 64.75 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.18 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.34 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.75 KB | ext: .png
|   |       |   |       |   \---[DIR] run_2026-02-11_14-20-50/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 88.94 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 66.07 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 87.71 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 65.08 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.27 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.33 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.20 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 47.58 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 48.10 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.57 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.26 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.64 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.23 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.36 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.85 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.31 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.96 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 60.33 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 68.41 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 2.78 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260211_142155.html | size: 48.37 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 84.37 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 66.22 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 87.52 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 64.75 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.10 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.38 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.49 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.48 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.66 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_M2_centered/
|   |       |   |       |   \---[DIR] run_2026-02-05_22-10-25/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 86.06 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 62.31 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 82.21 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 65.14 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 30.54 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 30.49 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.10 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.55 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.13 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.06 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 44.96 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 44.84 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 43.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.97 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.62 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.53 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.43 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.68 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 54.03 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 57.09 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 2.17 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_221048.html | size: 51.78 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 82.95 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 62.33 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 79.03 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 61.14 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 92.70 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 99.13 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 95.32 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 95.71 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 96.70 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_M2_lite/
|   |       |   |       |   \---[DIR] run_2026-02-05_22-40-14/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 88.08 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 64.20 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 82.88 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 65.79 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 30.54 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 30.49 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.11 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.55 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.12 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.22 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.05 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 44.96 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.45 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 44.84 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 43.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.97 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.61 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.53 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.42 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.68 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 60.13 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 61.51 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 1.68 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_224037.html | size: 47.43 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 81.12 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 68.43 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 82.06 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 65.90 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 95.16 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 99.23 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 95.31 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 95.58 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 95.43 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_M2_lite_scaled/
|   |       |   |       |   \---[DIR] run_2026-02-05_23-11-16/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 88.08 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 64.20 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 82.88 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 65.79 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 30.54 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 30.49 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.11 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.55 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.12 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.22 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.05 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 44.96 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.45 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 44.84 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 43.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.97 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.61 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.53 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.42 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.68 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 60.13 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 61.51 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 1.68 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_231139.html | size: 47.35 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 81.12 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 68.43 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 82.06 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 65.90 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 95.57 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 97.98 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 94.84 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 94.97 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 94.77 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_M2_scaled/
|   |       |   |       |   \---[DIR] run_2026-02-05_23-04-06/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_contours.png | size: 80.60 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_f_mu.png | size: 64.62 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_contours.png | size: 80.63 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_cou_m_mu.png | size: 64.93 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_elasticities.csv | size: 408 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_mean_hours.png | size: 31.06 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_female.png | size: 57.10 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_couples_male.png | size: 57.54 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_female.png | size: 57.13 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_singles_male.png | size: 57.20 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_hours_distribution_total.png | size: 56.05 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_female.png | size: 44.97 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_couples_male.png | size: 44.69 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_female.png | size: 44.84 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_singles_male.png | size: 45.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_job_distribution_total.png | size: 44.19 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_female.png | size: 41.98 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_couples_male.png | size: 36.63 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_female.png | size: 41.54 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_singles_male.png | size: 40.43 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_loc_distribution_total.png | size: 40.66 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_muc_comparison.png | size: 56.32 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_mul_comparison.png | size: 59.62 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_params.csv | size: 1.92 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_post_estimation_report_20260205_230428.html | size: 51.08 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_contours.png | size: 81.16 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sf_mu.png | size: 66.28 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_contours.png | size: 81.65 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_sm_mu.png | size: 63.76 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_female.png | size: 95.64 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_couples_male.png | size: 98.22 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_female.png | size: 95.23 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_singles_male.png | size: 95.11 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gamspy_wage_distribution_total.png | size: 95.97 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_M2b/
|   |       |   |       |   +---[DIR] run_2026-02-11_14-42-34/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 86.37 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 64.29 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 85.66 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 63.88 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 47.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.59 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.63 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.22 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.37 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.86 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.29 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 56.35 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 66.66 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 3.28 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260211_144301.html | size: 53.34 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 86.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 69.85 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 83.28 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 63.46 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 76.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.55 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.58 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.74 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-11_14-52-14/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 86.41 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 64.29 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 85.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 63.89 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 47.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.59 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.63 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.22 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.37 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.86 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.29 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 56.35 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 66.66 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 2.85 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260211_145240.html | size: 52.81 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 86.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 69.20 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 83.27 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 63.39 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.42 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.25 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.69 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.66 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.88 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-11_15-18-11/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 86.15 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 64.36 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 85.52 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 63.44 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 56.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 66.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 3.39 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260211_151813.html | size: 46.71 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 87.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 69.35 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 83.11 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 63.51 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-11_15-18-34/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 86.15 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 64.36 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 85.52 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 63.44 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 47.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.59 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.63 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.22 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.37 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.86 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.29 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 56.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 66.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 3.39 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260211_151901.html | size: 54.01 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 87.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 69.35 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 83.11 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 63.51 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.52 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.98 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.96 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.69 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-11_15-21-00/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 86.15 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 64.36 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 85.52 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 63.44 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 47.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.59 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.63 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.22 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.37 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.86 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.29 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 56.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 66.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 3.39 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260211_152127.html | size: 54.09 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 87.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 69.35 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 83.11 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 63.51 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.82 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.62 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-19_10-24-19/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 86.18 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 64.35 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 85.54 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 63.44 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 47.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.59 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.63 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.22 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.37 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.86 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.29 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 56.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 66.16 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 3.21 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260219_102446.html | size: 53.44 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 86.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 69.30 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 83.08 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 63.39 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.67 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.10 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.63 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.65 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.57 KB | ext: .png
|   |       |   |       |   \---[DIR] run_2026-02-19_10-45-19/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 86.41 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 64.29 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 85.54 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 63.89 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.26 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.31 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.23 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.05 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 47.84 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.59 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.63 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.22 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.37 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.86 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.29 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.96 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 56.35 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 66.66 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 3.01 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260219_104546.html | size: 52.82 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 86.58 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 69.20 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 83.27 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 63.39 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.54 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.26 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.67 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.98 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.68 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_M2b_education/
|   |       |   |       |   \---[DIR] run_2026-02-19_10-16-15/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 86.15 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 64.36 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 85.52 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 63.44 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.26 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.31 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.23 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.05 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 47.84 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.59 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.63 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.22 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.37 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.86 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.29 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.96 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 56.31 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 66.10 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 3.39 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260219_101643.html | size: 54.05 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 87.05 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 69.35 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 83.11 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 63.51 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.51 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.38 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.56 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.71 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_M2c/
|   |       |   |       |   +---[DIR] run_2026-02-19_10-52-04/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 84.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 64.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 84.71 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 64.08 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.21 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.02 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 47.87 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.48 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.37 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.85 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.29 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.97 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 55.02 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 69.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 4.45 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260219_105230.html | size: 59.81 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 83.16 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 67.68 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 83.04 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 65.66 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.37 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.18 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.53 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.68 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.77 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-19_11-34-55/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 83.48 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 63.44 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 84.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 63.42 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.28 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.84 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.22 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.04 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 47.87 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.48 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.56 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.38 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.85 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.29 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.96 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 55.03 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 69.67 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 4.53 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260219_113523.html | size: 59.82 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 83.63 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 67.27 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 83.12 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 65.35 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.77 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.11 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.45 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.39 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.58 KB | ext: .png
|   |       |   |       |   +---[DIR] run_2026-02-19_11-50-03/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 83.30 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 64.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 84.36 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 64.30 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.27 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.31 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.22 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.04 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 47.87 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.48 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.58 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.62 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.38 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.85 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.29 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.97 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 55.26 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 69.43 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 4.09 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260219_115030.html | size: 58.90 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 83.71 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 67.52 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 83.23 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 65.62 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.32 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 76.98 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.77 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.79 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.72 KB | ext: .png
|   |       |   |       |   \---[DIR] run_2026-02-19_13-58-23/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 83.01 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 63.99 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 84.83 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 64.30 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.27 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.31 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.26 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.22 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.04 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 47.87 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.48 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.57 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.62 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.39 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.85 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.29 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.97 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 54.70 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 67.96 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 4.21 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260219_135850.html | size: 59.30 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 83.08 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 67.40 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 83.94 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 62.92 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.72 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 76.96 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.95 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.69 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.73 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_M2d_type/
|   |       |   |       |   +---[DIR] run_2026-02-19_15-58-59/
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 90.13 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 65.73 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 89.44 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 64.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.29 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.82 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.34 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.25 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.21 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.33 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 48.53 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.92 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.62 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.24 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.37 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.85 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.27 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.97 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 56.74 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 70.05 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 4.00 KB | ext: .csv
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260219_160038.html | size: 54.44 KB | ext: .html
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 82.18 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 66.89 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 85.01 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 64.63 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.56 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 76.94 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.88 KB | ext: .png
|   |       |   |       |   |   +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.54 KB | ext: .png
|   |       |   |       |   |   \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.69 KB | ext: .png
|   |       |   |       |   \---[DIR] run_2026-02-19_16-38-46/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 90.13 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 65.73 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 89.44 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 64.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.29 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.82 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.34 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.25 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.21 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.33 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 48.53 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.92 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.62 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.37 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.85 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.27 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.97 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 56.74 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 70.05 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 3.87 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260219_164023.html | size: 53.08 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 82.18 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 66.89 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 85.01 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 64.63 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.44 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.17 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.66 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.51 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.74 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_M2e_a/
|   |       |   |       |   \---[DIR] run_2026-02-20_10-38-44/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 81.77 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 61.77 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 80.51 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 66.31 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 411 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.21 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.30 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.17 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.19 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 47.93 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 47.85 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.28 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.60 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.63 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.36 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.85 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.29 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.95 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 55.76 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 69.63 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 4.81 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260220_104020.html | size: 59.28 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 84.11 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 64.96 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 81.14 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 63.98 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 79.14 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.79 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 78.05 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 75.41 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 81.19 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_M2e_hours/
|   |       |   |       |   \---[DIR] run_2026-02-20_09-47-28/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 88.91 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 71.79 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 88.82 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 68.35 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.22 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.82 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.28 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.16 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.19 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.15 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 48.53 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.90 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.58 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.63 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.22 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.39 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.83 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.31 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.97 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 62.72 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 71.73 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 4.04 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260220_094910.html | size: 55.99 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 81.38 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 66.44 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 85.71 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 69.04 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 79.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.89 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 77.66 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 75.13 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 81.12 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_M2f_hybrid/
|   |       |   |       |   \---[DIR] run_2026-02-20_09-22-50/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 85.05 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 69.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 86.36 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 68.96 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 410 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.27 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.83 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.31 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.27 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.19 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 48.04 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 47.86 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.48 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.57 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.67 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.23 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.38 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.85 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.29 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.97 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 59.58 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 69.10 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 5.30 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260220_092431.html | size: 57.83 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 85.74 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 67.86 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 84.73 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 66.50 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.67 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.17 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 76.77 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.54 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.70 KB | ext: .png
|   |       |   |       +---[DIR] estimation_spec_job_M2g_unified_opportunity/
|   |       |   |       |   \---[DIR] run_2026-02-20_10-57-29/
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_contours.png | size: 85.51 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_f_mu.png | size: 64.55 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_contours.png | size: 84.60 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_cou_m_mu.png | size: 67.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_elasticities.csv | size: 411 B | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_mean_hours.png | size: 31.60 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_fit_participation.png | size: 30.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_female.png | size: 56.24 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_couples_male.png | size: 55.86 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_female.png | size: 56.30 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_singles_male.png | size: 56.20 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_hours_distribution_total.png | size: 55.22 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_female.png | size: 47.99 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_couples_male.png | size: 47.85 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_female.png | size: 47.46 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_singles_male.png | size: 48.61 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_job_distribution_total.png | size: 46.64 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_female.png | size: 36.25 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_couples_male.png | size: 36.38 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_female.png | size: 35.88 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_singles_male.png | size: 41.30 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_loc_distribution_total.png | size: 34.97 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_muc_comparison.png | size: 55.71 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_mul_comparison.png | size: 69.47 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_params.csv | size: 5.56 KB | ext: .csv
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_post_estimation_report_20260220_105905.html | size: 60.34 KB | ext: .html
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_contours.png | size: 83.65 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sf_mu.png | size: 64.73 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_contours.png | size: 81.04 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_sm_mu.png | size: 63.52 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_female.png | size: 78.45 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_couples_male.png | size: 77.14 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_female.png | size: 77.16 KB | ext: .png
|   |       |   |       |       +---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_singles_male.png | size: 74.72 KB | ext: .png
|   |       |   |       |       \---[FILE] fr_2016_jobchoice_gmm_gamspy_wage_distribution_total.png | size: 80.76 KB | ext: .png
|   |       |   |       \---[DIR] unknown_spec/
|   |       |   +---[DIR] v2/
|   |       |   |   +---[DIR] gamspy/
|   |       |   |   |   +---[DIR] run_2026-01-27_13-26-18/
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 89.55 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 57.77 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 93.86 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 58.80 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 411 B | ext: .csv
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.13 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 29.81 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 57.61 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 79.28 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 5.68 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260127_132628.html | size: 61.88 KB | ext: .html
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 87.26 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 63.97 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 93.83 KB | ext: .png
|   |       |   |   |   |   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 63.91 KB | ext: .png
|   |       |   |   |   +---[DIR] run_2026-01-28_17-36-01/
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 104.23 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 67.61 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 98.47 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 67.52 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 409 B | ext: .csv
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.14 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 29.81 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_female.png | size: 58.21 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_male.png | size: 56.94 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_female.png | size: 57.50 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_male.png | size: 57.50 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_total.png | size: 56.43 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 64.90 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 79.93 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 5.64 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260128_173616.html | size: 62.60 KB | ext: .html
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 88.50 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 63.82 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 93.21 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sm_mu.png | size: 65.81 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_female.png | size: 67.29 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_male.png | size: 73.74 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_female.png | size: 66.52 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_male.png | size: 69.86 KB | ext: .png
|   |       |   |   |   |   \---[FILE] fr_2016_gamspy_wage_distribution_total.png | size: 66.18 KB | ext: .png
|   |       |   |   |   +---[DIR] run_2026-01-28_17-42-06/
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 104.23 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 67.61 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 98.47 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 67.52 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 409 B | ext: .csv
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.14 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 29.81 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_female.png | size: 58.21 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_male.png | size: 56.94 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_female.png | size: 57.50 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_male.png | size: 57.50 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_total.png | size: 56.43 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 64.90 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 79.93 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 5.64 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260128_174222.html | size: 62.60 KB | ext: .html
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 88.50 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 63.82 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 93.21 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sm_mu.png | size: 65.81 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_female.png | size: 66.81 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_male.png | size: 73.44 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_female.png | size: 66.02 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_male.png | size: 69.79 KB | ext: .png
|   |       |   |   |   |   \---[FILE] fr_2016_gamspy_wage_distribution_total.png | size: 66.43 KB | ext: .png
|   |       |   |   |   +---[DIR] run_2026-01-28_17-50-40/
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 104.23 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 67.61 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 98.47 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 67.52 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 409 B | ext: .csv
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.14 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 29.81 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_female.png | size: 58.21 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_male.png | size: 56.94 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_female.png | size: 57.50 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_male.png | size: 57.50 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_total.png | size: 56.43 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 64.90 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 79.93 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 5.64 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260128_175056.html | size: 62.58 KB | ext: .html
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 88.50 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 63.82 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 93.21 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sm_mu.png | size: 65.81 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_female.png | size: 66.70 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_male.png | size: 73.67 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_female.png | size: 66.14 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_male.png | size: 69.82 KB | ext: .png
|   |       |   |   |   |   \---[FILE] fr_2016_gamspy_wage_distribution_total.png | size: 66.31 KB | ext: .png
|   |       |   |   |   +---[DIR] run_2026-01-29_11-38-31/
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 104.23 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 67.61 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 98.47 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 67.52 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 409 B | ext: .csv
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.14 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 29.81 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_female.png | size: 58.21 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_male.png | size: 56.94 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_female.png | size: 57.50 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_male.png | size: 57.50 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_hours_distribution_total.png | size: 56.43 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 64.90 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 79.93 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_params.csv | size: 5.64 KB | ext: .csv
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260129_113847.html | size: 62.58 KB | ext: .html
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 88.50 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 63.82 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 93.21 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_sm_mu.png | size: 65.81 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_female.png | size: 66.77 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_male.png | size: 73.25 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_female.png | size: 65.82 KB | ext: .png
|   |       |   |   |   |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_male.png | size: 69.03 KB | ext: .png
|   |       |   |   |   |   \---[FILE] fr_2016_gamspy_wage_distribution_total.png | size: 66.42 KB | ext: .png
|   |       |   |   |   \---[DIR] run_2026-02-02_18-07-45/
|   |       |   |   |       +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 104.23 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 67.61 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 98.47 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 67.52 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_elasticities.csv | size: 409 B | ext: .csv
|   |       |   |   |       +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.14 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_fit_participation.png | size: 29.81 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_hours_distribution_couples_female.png | size: 58.21 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_hours_distribution_couples_male.png | size: 56.94 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_hours_distribution_singles_female.png | size: 57.50 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_hours_distribution_singles_male.png | size: 57.50 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_hours_distribution_total.png | size: 56.43 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 64.90 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 79.93 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_params.csv | size: 5.64 KB | ext: .csv
|   |       |   |   |       +---[FILE] fr_2016_gamspy_post_estimation_report_20260202_180802.html | size: 62.57 KB | ext: .html
|   |       |   |   |       +---[FILE] fr_2016_gamspy_sf_contours.png | size: 88.50 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_sf_mu.png | size: 63.82 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_sm_contours.png | size: 93.21 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_sm_mu.png | size: 65.81 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_wage_distribution_couples_female.png | size: 66.92 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_wage_distribution_couples_male.png | size: 73.65 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_wage_distribution_singles_female.png | size: 66.33 KB | ext: .png
|   |       |   |   |       +---[FILE] fr_2016_gamspy_wage_distribution_singles_male.png | size: 69.30 KB | ext: .png
|   |       |   |   |       \---[FILE] fr_2016_gamspy_wage_distribution_total.png | size: 66.43 KB | ext: .png
|   |       |   |   \---[DIR] scipy/
|   |       |   |       \---[DIR] run_2026-01-27_13-30-20/
|   |       |   |           +---[FILE] fr_2016_scipy_cou_f_contours.png | size: 93.13 KB | ext: .png
|   |       |   |           +---[FILE] fr_2016_scipy_cou_f_mu.png | size: 65.22 KB | ext: .png
|   |       |   |           +---[FILE] fr_2016_scipy_cou_m_contours.png | size: 94.57 KB | ext: .png
|   |       |   |           +---[FILE] fr_2016_scipy_cou_m_mu.png | size: 64.31 KB | ext: .png
|   |       |   |           +---[FILE] fr_2016_scipy_elasticities.csv | size: 411 B | ext: .csv
|   |       |   |           +---[FILE] fr_2016_scipy_fit_mean_hours.png | size: 30.11 KB | ext: .png
|   |       |   |           +---[FILE] fr_2016_scipy_fit_participation.png | size: 29.81 KB | ext: .png
|   |       |   |           +---[FILE] fr_2016_scipy_muc_comparison.png | size: 66.09 KB | ext: .png
|   |       |   |           +---[FILE] fr_2016_scipy_mul_comparison.png | size: 74.52 KB | ext: .png
|   |       |   |           +---[FILE] fr_2016_scipy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |       |   |           +---[FILE] fr_2016_scipy_params.csv | size: 5.79 KB | ext: .csv
|   |       |   |           +---[FILE] fr_2016_scipy_post_estimation_report_20260127_133029.html | size: 61.03 KB | ext: .html
|   |       |   |           +---[FILE] fr_2016_scipy_sf_contours.png | size: 84.58 KB | ext: .png
|   |       |   |           +---[FILE] fr_2016_scipy_sf_mu.png | size: 68.45 KB | ext: .png
|   |       |   |           +---[FILE] fr_2016_scipy_sm_contours.png | size: 90.77 KB | ext: .png
|   |       |   |           \---[FILE] fr_2016_scipy_sm_mu.png | size: 65.37 KB | ext: .png
|   |       |   \---[DIR] v3/
|   |       |       \---[DIR] gamspy/
|   |       |           +---[DIR] run_2026-02-02_18-25-56/
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 110.26 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 58.37 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 98.27 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 55.69 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 412 B | ext: .csv
|   |       |           |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.11 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 29.80 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_female.png | size: 58.20 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_male.png | size: 56.92 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_female.png | size: 57.60 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_male.png | size: 57.56 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_total.png | size: 56.41 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 60.04 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 79.06 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 34.77 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_params.csv | size: 6.21 KB | ext: .csv
|   |       |           |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260202_182612.html | size: 64.64 KB | ext: .html
|   |       |           |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 91.53 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 68.64 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 83.17 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sm_mu.png | size: 68.30 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_female.png | size: 65.02 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_male.png | size: 74.06 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_female.png | size: 67.03 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_male.png | size: 67.38 KB | ext: .png
|   |       |           |   \---[FILE] fr_2016_gamspy_wage_distribution_total.png | size: 66.72 KB | ext: .png
|   |       |           +---[DIR] run_2026-02-02_18-54-20/
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 100.85 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 60.23 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 98.79 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 58.23 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 412 B | ext: .csv
|   |       |           |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.18 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.19 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_female.png | size: 58.21 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_male.png | size: 57.04 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_female.png | size: 57.51 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_male.png | size: 57.51 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_total.png | size: 56.40 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 56.72 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 78.88 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_params.csv | size: 6.21 KB | ext: .csv
|   |       |           |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260202_185435.html | size: 65.44 KB | ext: .html
|   |       |           |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 86.79 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 65.87 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 89.16 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sm_mu.png | size: 72.08 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_female.png | size: 67.58 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_male.png | size: 73.93 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_female.png | size: 66.25 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_male.png | size: 70.09 KB | ext: .png
|   |       |           |   \---[FILE] fr_2016_gamspy_wage_distribution_total.png | size: 67.17 KB | ext: .png
|   |       |           +---[DIR] run_2026-02-02_18-59-11/
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 98.37 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 63.66 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 100.40 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 58.83 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 412 B | ext: .csv
|   |       |           |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.12 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 29.81 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_female.png | size: 58.21 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_male.png | size: 57.84 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_female.png | size: 57.50 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_male.png | size: 57.50 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_total.png | size: 56.38 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 57.36 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 79.88 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_params.csv | size: 6.13 KB | ext: .csv
|   |       |           |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260202_185927.html | size: 65.15 KB | ext: .html
|   |       |           |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 86.58 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 65.54 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 89.07 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sm_mu.png | size: 72.57 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_female.png | size: 67.41 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_male.png | size: 74.52 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_female.png | size: 66.41 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_male.png | size: 70.02 KB | ext: .png
|   |       |           |   \---[FILE] fr_2016_gamspy_wage_distribution_total.png | size: 66.93 KB | ext: .png
|   |       |           +---[DIR] run_2026-02-02_23-42-36/
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 96.11 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 62.97 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 100.91 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 57.96 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 408 B | ext: .csv
|   |       |           |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.12 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 29.82 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_female.png | size: 58.22 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_male.png | size: 56.99 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_female.png | size: 57.50 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_male.png | size: 57.52 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_total.png | size: 56.41 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 60.57 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 83.12 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_params.csv | size: 6.02 KB | ext: .csv
|   |       |           |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260202_234252.html | size: 65.99 KB | ext: .html
|   |       |           |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 80.95 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 62.66 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 84.85 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sm_mu.png | size: 67.82 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_female.png | size: 66.57 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_male.png | size: 73.74 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_female.png | size: 66.46 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_male.png | size: 70.17 KB | ext: .png
|   |       |           |   \---[FILE] fr_2016_gamspy_wage_distribution_total.png | size: 66.71 KB | ext: .png
|   |       |           +---[DIR] run_2026-02-03_00-32-01/
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 95.74 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 64.94 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 102.79 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 60.32 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 408 B | ext: .csv
|   |       |           |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.13 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 29.81 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_female.png | size: 58.21 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_male.png | size: 56.98 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_female.png | size: 57.51 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_male.png | size: 57.53 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_total.png | size: 56.40 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 63.01 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 80.69 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_params.csv | size: 6.38 KB | ext: .csv
|   |       |           |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260203_003217.html | size: 65.39 KB | ext: .html
|   |       |           |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 81.25 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 65.36 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 85.67 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sm_mu.png | size: 69.05 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_female.png | size: 66.93 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_male.png | size: 73.42 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_female.png | size: 66.49 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_male.png | size: 69.89 KB | ext: .png
|   |       |           |   \---[FILE] fr_2016_gamspy_wage_distribution_total.png | size: 66.54 KB | ext: .png
|   |       |           +---[DIR] run_2026-02-03_00-44-19/
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 95.74 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 64.94 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 102.79 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 60.32 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 408 B | ext: .csv
|   |       |           |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.13 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 29.81 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_female.png | size: 58.21 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_male.png | size: 56.98 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_female.png | size: 57.51 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_male.png | size: 57.53 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_total.png | size: 56.40 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 63.01 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 80.69 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_params.csv | size: 6.38 KB | ext: .csv
|   |       |           |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260203_004434.html | size: 65.57 KB | ext: .html
|   |       |           |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 81.25 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 65.36 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 85.67 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sm_mu.png | size: 69.05 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_female.png | size: 66.94 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_male.png | size: 73.58 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_female.png | size: 65.97 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_male.png | size: 70.19 KB | ext: .png
|   |       |           |   \---[FILE] fr_2016_gamspy_wage_distribution_total.png | size: 67.13 KB | ext: .png
|   |       |           +---[DIR] run_2026-02-03_00-58-41/
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 95.45 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 65.37 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 102.43 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 60.44 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 408 B | ext: .csv
|   |       |           |   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.13 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 29.81 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_female.png | size: 58.21 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_couples_male.png | size: 56.98 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_female.png | size: 57.50 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_singles_male.png | size: 57.52 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_hours_distribution_total.png | size: 56.40 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 63.33 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 79.89 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_params.csv | size: 6.18 KB | ext: .csv
|   |       |           |   +---[FILE] fr_2016_gamspy_post_estimation_report_20260203_005857.html | size: 64.80 KB | ext: .html
|   |       |           |   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 81.39 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 63.07 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 85.44 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_sm_mu.png | size: 67.31 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_female.png | size: 67.32 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_couples_male.png | size: 73.71 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_female.png | size: 66.73 KB | ext: .png
|   |       |           |   +---[FILE] fr_2016_gamspy_wage_distribution_singles_male.png | size: 69.69 KB | ext: .png
|   |       |           |   \---[FILE] fr_2016_gamspy_wage_distribution_total.png | size: 66.11 KB | ext: .png
|   |       |           \---[DIR] run_2026-02-05_14-17-19/
|   |       |               +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 95.24 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 65.82 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 101.83 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 60.07 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_elasticities.csv | size: 408 B | ext: .csv
|   |       |               +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.09 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_hours_distribution_couples_female.png | size: 58.21 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_hours_distribution_couples_male.png | size: 56.90 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_hours_distribution_singles_female.png | size: 57.49 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_hours_distribution_singles_male.png | size: 57.52 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_hours_distribution_total.png | size: 56.41 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 63.08 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 80.52 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_params.csv | size: 6.44 KB | ext: .csv
|   |       |               +---[FILE] fr_2016_gamspy_post_estimation_report_20260205_141740.html | size: 65.39 KB | ext: .html
|   |       |               +---[FILE] fr_2016_gamspy_sf_contours.png | size: 81.40 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_sf_mu.png | size: 64.75 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_sm_contours.png | size: 86.78 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_sm_mu.png | size: 69.47 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_wage_distribution_couples_female.png | size: 66.99 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_wage_distribution_couples_male.png | size: 73.04 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_wage_distribution_singles_female.png | size: 66.70 KB | ext: .png
|   |       |               +---[FILE] fr_2016_gamspy_wage_distribution_singles_male.png | size: 70.20 KB | ext: .png
|   |       |               \---[FILE] fr_2016_gamspy_wage_distribution_total.png | size: 66.83 KB | ext: .png
|   |       +---[DIR] spec_tests/
|   |       |   +---[DIR] 1_minimal_theta0_scipy/
|   |       |   |   \---[DIR] run_2026-01-24_12-26-49/
|   |       |   |       +---[FILE] fr_2016_scipy_cou_f_contours.png | size: 107.99 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_cou_f_mu.png | size: 63.52 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_cou_m_contours.png | size: 99.98 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_cou_m_mu.png | size: 63.96 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_elasticities.csv | size: 402 B | ext: .csv
|   |       |   |       +---[FILE] fr_2016_scipy_fit_mean_hours.png | size: 31.64 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_fit_participation.png | size: 30.13 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_muc_comparison.png | size: 73.18 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_mul_comparison.png | size: 87.41 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_params.csv | size: 1.32 KB | ext: .csv
|   |       |   |       +---[FILE] fr_2016_scipy_post_estimation_report_20260124_122659.html | size: 38.13 KB | ext: .html
|   |       |   |       +---[FILE] fr_2016_scipy_sf_contours.png | size: 116.98 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_sf_mu.png | size: 63.03 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_sm_contours.png | size: 115.70 KB | ext: .png
|   |       |   |       \---[FILE] fr_2016_scipy_sm_mu.png | size: 63.63 KB | ext: .png
|   |       |   +---[DIR] 2_pooled_consumption_scipy/
|   |       |   |   +---[DIR] run_2026-01-24_12-27-44/
|   |       |   |   |   +---[FILE] fr_2016_scipy_cou_f_contours.png | size: 114.83 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_cou_f_mu.png | size: 70.10 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_cou_m_contours.png | size: 111.00 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_cou_m_mu.png | size: 69.79 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_fit_mean_hours.png | size: 30.18 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_muc_comparison.png | size: 80.89 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_mul_comparison.png | size: 71.70 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_sf_contours.png | size: 80.83 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_sf_mu.png | size: 70.38 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_sm_contours.png | size: 86.60 KB | ext: .png
|   |       |   |   |   \---[FILE] fr_2016_scipy_sm_mu.png | size: 68.73 KB | ext: .png
|   |       |   |   +---[DIR] run_2026-01-24_12-28-29/
|   |       |   |   |   +---[FILE] fr_2016_scipy_cou_f_contours.png | size: 114.83 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_cou_f_mu.png | size: 70.10 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_cou_m_contours.png | size: 111.00 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_cou_m_mu.png | size: 69.79 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_fit_mean_hours.png | size: 30.18 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_muc_comparison.png | size: 80.89 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_mul_comparison.png | size: 71.70 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_sf_contours.png | size: 80.83 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_sf_mu.png | size: 70.38 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_sm_contours.png | size: 86.60 KB | ext: .png
|   |       |   |   |   \---[FILE] fr_2016_scipy_sm_mu.png | size: 68.73 KB | ext: .png
|   |       |   |   \---[DIR] run_2026-01-24_12-30-16/
|   |       |   |       +---[FILE] fr_2016_scipy_cou_f_contours.png | size: 114.83 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_cou_f_mu.png | size: 70.10 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_cou_m_contours.png | size: 111.00 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_cou_m_mu.png | size: 69.79 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_elasticities.csv | size: 405 B | ext: .csv
|   |       |   |       +---[FILE] fr_2016_scipy_fit_mean_hours.png | size: 30.18 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_muc_comparison.png | size: 80.89 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_mul_comparison.png | size: 71.70 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_params.csv | size: 1.19 KB | ext: .csv
|   |       |   |       +---[FILE] fr_2016_scipy_post_estimation_report_20260124_123026.html | size: 38.32 KB | ext: .html
|   |       |   |       +---[FILE] fr_2016_scipy_sf_contours.png | size: 80.83 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_sf_mu.png | size: 70.38 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_sm_contours.png | size: 86.60 KB | ext: .png
|   |       |   |       \---[FILE] fr_2016_scipy_sm_mu.png | size: 68.73 KB | ext: .png
|   |       |   +---[DIR] 3_pooled_leisure_scipy/
|   |       |   |   +---[DIR] run_2026-01-24_12-28-35/
|   |       |   |   |   +---[FILE] fr_2016_scipy_cou_f_contours.png | size: 114.38 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_cou_f_mu.png | size: 70.10 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_cou_m_contours.png | size: 110.85 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_cou_m_mu.png | size: 69.79 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_fit_mean_hours.png | size: 30.18 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_muc_comparison.png | size: 80.86 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_mul_comparison.png | size: 71.54 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_sf_contours.png | size: 83.99 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_sf_mu.png | size: 69.91 KB | ext: .png
|   |       |   |   |   +---[FILE] fr_2016_scipy_sm_contours.png | size: 86.54 KB | ext: .png
|   |       |   |   |   \---[FILE] fr_2016_scipy_sm_mu.png | size: 68.95 KB | ext: .png
|   |       |   |   \---[DIR] run_2026-01-24_12-31-08/
|   |       |   |       +---[FILE] fr_2016_scipy_cou_f_contours.png | size: 114.38 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_cou_f_mu.png | size: 70.10 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_cou_m_contours.png | size: 110.85 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_cou_m_mu.png | size: 69.79 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_elasticities.csv | size: 405 B | ext: .csv
|   |       |   |       +---[FILE] fr_2016_scipy_fit_mean_hours.png | size: 30.18 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_muc_comparison.png | size: 80.86 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_mul_comparison.png | size: 71.54 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_params.csv | size: 1.19 KB | ext: .csv
|   |       |   |       +---[FILE] fr_2016_scipy_post_estimation_report_20260124_123118.html | size: 38.32 KB | ext: .html
|   |       |   |       +---[FILE] fr_2016_scipy_sf_contours.png | size: 83.99 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_sf_mu.png | size: 69.91 KB | ext: .png
|   |       |   |       +---[FILE] fr_2016_scipy_sm_contours.png | size: 86.54 KB | ext: .png
|   |       |   |       \---[FILE] fr_2016_scipy_sm_mu.png | size: 68.95 KB | ext: .png
|   |       |   \---[DIR] 4_ultra_minimal_scipy/
|   |       |       \---[DIR] run_2026-01-24_12-31-40/
|   |       |           +---[FILE] fr_2016_scipy_cou_f_contours.png | size: 112.95 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scipy_cou_f_mu.png | size: 69.97 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scipy_cou_m_contours.png | size: 109.07 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scipy_cou_m_mu.png | size: 67.90 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scipy_elasticities.csv | size: 402 B | ext: .csv
|   |       |           +---[FILE] fr_2016_scipy_fit_mean_hours.png | size: 30.19 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scipy_fit_participation.png | size: 30.48 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scipy_muc_comparison.png | size: 80.55 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scipy_mul_comparison.png | size: 99.64 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scipy_negative_mu_diagnostics.png | size: 31.81 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scipy_params.csv | size: 938 B | ext: .csv
|   |       |           +---[FILE] fr_2016_scipy_post_estimation_report_20260124_123149.html | size: 36.03 KB | ext: .html
|   |       |           +---[FILE] fr_2016_scipy_sf_contours.png | size: 123.83 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scipy_sf_mu.png | size: 64.71 KB | ext: .png
|   |       |           +---[FILE] fr_2016_scipy_sm_contours.png | size: 121.25 KB | ext: .png
|   |       |           \---[FILE] fr_2016_scipy_sm_mu.png | size: 64.95 KB | ext: .png
|   |       \---[DIR] v1/
|   |           \---[DIR] gamspy/
|   |               \---[DIR] run_2026-01-27_12-00-32/
|   |                   +---[FILE] fr_2016_gamspy_cou_f_contours.png | size: 90.65 KB | ext: .png
|   |                   +---[FILE] fr_2016_gamspy_cou_f_mu.png | size: 57.71 KB | ext: .png
|   |                   +---[FILE] fr_2016_gamspy_cou_m_contours.png | size: 93.14 KB | ext: .png
|   |                   +---[FILE] fr_2016_gamspy_cou_m_mu.png | size: 59.10 KB | ext: .png
|   |                   +---[FILE] fr_2016_gamspy_elasticities.csv | size: 411 B | ext: .csv
|   |                   +---[FILE] fr_2016_gamspy_fit_mean_hours.png | size: 30.13 KB | ext: .png
|   |                   +---[FILE] fr_2016_gamspy_fit_participation.png | size: 29.81 KB | ext: .png
|   |                   +---[FILE] fr_2016_gamspy_muc_comparison.png | size: 59.10 KB | ext: .png
|   |                   +---[FILE] fr_2016_gamspy_mul_comparison.png | size: 77.75 KB | ext: .png
|   |                   +---[FILE] fr_2016_gamspy_negative_mu_diagnostics.png | size: 39.04 KB | ext: .png
|   |                   +---[FILE] fr_2016_gamspy_params.csv | size: 4.74 KB | ext: .csv
|   |                   +---[FILE] fr_2016_gamspy_post_estimation_report_20260127_120044.html | size: 59.44 KB | ext: .html
|   |                   +---[FILE] fr_2016_gamspy_sf_contours.png | size: 89.19 KB | ext: .png
|   |                   +---[FILE] fr_2016_gamspy_sf_mu.png | size: 66.70 KB | ext: .png
|   |                   +---[FILE] fr_2016_gamspy_sm_contours.png | size: 93.79 KB | ext: .png
|   |                   \---[FILE] fr_2016_gamspy_sm_mu.png | size: 62.69 KB | ext: .png
|   \---[FILE] KEEP_RESULTS.md | size: 299 B | ext: .md
+---[DIR] reports/
+---[DIR] scripts/
|   +---[DIR] archive/
|   |   +---[DIR] backups_2025_12/
|   |   |   +---[FILE] estimation_spec.yaml.backup | size: 6.83 KB | ext: .backup
|   |   |   +---[FILE] estimation_spec_loc_empirical.yaml.backup | size: 7.04 KB | ext: .backup
|   |   |   \---[FILE] RURO_estimate_FR.py.backup_20251216_143415 | size: 239.16 KB | ext: .backup_20251216_143415
|   |   +---[DIR] experimental/
|   |   |   +---[FILE] run_draws_euromod_interactive.py | size: 4.46 KB | ext: .py
|   |   |   +---[FILE] run_full_pipeline_interactive.py | size: 16.51 KB | ext: .py
|   |   |   +---[FILE] run_pipeline_explicit.py | size: 29.85 KB | ext: .py
|   |   |   +---[FILE] run_pipeline_memory_only.py | size: 14.71 KB | ext: .py
|   |   |   \---[FILE] simple.py | size: 1.07 KB | ext: .py
|   |   +---[DIR] fixes/
|   |   |   +---[FILE] recompute_se.py | size: 4.06 KB | ext: .py
|   |   |   \---[FILE] rerun_post_estimation.py | size: 3.41 KB | ext: .py
|   |   +---[DIR] old_data_prep/
|   |   |   \---[FILE] data_prep2.py | size: 65.11 KB | ext: .py
|   |   +---[DIR] old_ruro_pre_enhanced/
|   |   |   +---[FILE] full_RURO.py | size: 53.33 KB | ext: .py
|   |   |   +---[FILE] inspect_RURO_fr_2021.py | size: 871 B | ext: .py
|   |   |   +---[FILE] run_fr_2021_prep.py | size: 864 B | ext: .py
|   |   |   +---[FILE] RURO_boxcox_group_opportunities.py | size: 42.60 KB | ext: .py
|   |   |   +---[FILE] RURO_boxcox_mnl.py | size: 25.74 KB | ext: .py
|   |   |   +---[FILE] RURO_gpt.py | size: 38.53 KB | ext: .py
|   |   |   \---[FILE] trim_mnl_dataset.py | size: 3.47 KB | ext: .py
|   |   +---[DIR] rum_approach/
|   |   |   \---[DIR] RUM/
|   |   |       +---[FILE] analyzer_runner.py | size: 1.80 KB | ext: .py
|   |   |       +---[FILE] bio_boxcox.py | size: 20.84 KB | ext: .py
|   |   |       +---[FILE] biotest.py | size: 2.09 KB | ext: .py
|   |   |       +---[FILE] combine_years_for_dcm.py | size: 7.95 KB | ext: .py
|   |   |       +---[FILE] data_prep.py | size: 20.95 KB | ext: .py
|   |   |       +---[FILE] DCM1.py | size: 30.93 KB | ext: .py
|   |   |       +---[FILE] DCM1_boxcox.py | size: 48.18 KB | ext: .py
|   |   |       +---[FILE] DCM1_boxcox_gender_split.py | size: 4.34 KB | ext: .py
|   |   |       +---[FILE] DCM1_gamspy.py | size: 21.50 KB | ext: .py
|   |   |       +---[FILE] DCM2_gamspy.py | size: 58.74 KB | ext: .py
|   |   |       +---[FILE] DCM2_gamspy_gender_split.py | size: 4.18 KB | ext: .py
|   |   |       +---[FILE] MLE_dcm.py | size: 16.85 KB | ext: .py
|   |   |       +---[FILE] old_biogeme.py | size: 19.69 KB | ext: .py
|   |   |       +---[FILE] old_prep.py | size: 30.90 KB | ext: .py
|   |   |       +---[FILE] process2_py.py | size: 17.20 KB | ext: .py
|   |   |       +---[FILE] run_de_multi_year.py | size: 2.85 KB | ext: .py
|   |   |       +---[FILE] run_euromod.py | size: 3.29 KB | ext: .py
|   |   |       +---[FILE] scenarios.py | size: 30.77 KB | ext: .py
|   |   |       +---[FILE] scenarios_de.py | size: 4.94 KB | ext: .py
|   |   |       +---[FILE] set_biogeme_env.py | size: 89 B | ext: .py
|   |   |       \---[FILE] train_mnl.py | size: 1.22 KB | ext: .py
|   |   \---[FILE] README.md | size: 278 B | ext: .md
|   +---[DIR] diagnostics/
|   |   +---[FILE] check_nchildren_simple.py | size: 2.05 KB | ext: .py
|   |   +---[FILE] check_nchildren_variation.py | size: 3.42 KB | ext: .py
|   |   +---[FILE] check_nchildren_variation_v2.py | size: 1.72 KB | ext: .py
|   |   +---[FILE] check_preference_diagnostics.py | size: 6.09 KB | ext: .py
|   |   +---[FILE] check_type_ids.py | size: 3.53 KB | ext: .py
|   |   +---[FILE] compare_scipy_gamspy.py | size: 6.79 KB | ext: .py
|   |   +---[FILE] README.md | size: 463 B | ext: .md
|   |   \---[FILE] test_gamspy_vs_scipy.py | size: 10.56 KB | ext: .py
|   +---[DIR] enhanced/
|   |   +---[FILE] checking.ipynb | size: 138.64 KB | ext: .ipynb
|   |   +---[FILE] compute_standard_errors.py | size: 12.92 KB | ext: .py
|   |   +---[FILE] diagnostic_consumption_variation.py | size: 8.18 KB | ext: .py
|   |   +---[FILE] enh_france_data_prep.py | size: 109.58 KB | ext: .py
|   |   +---[FILE] enh_pipeline.ps1 | size: 19.71 KB | ext: .ps1
|   |   +---[FILE] enh_prepare_FR_gsur.py | size: 24.64 KB | ext: .py
|   |   +---[FILE] enh_RURO_draws.py | size: 63.81 KB | ext: .py
|   |   +---[FILE] enh_RURO_estimate_FR.py | size: 69.63 KB | ext: .py
|   |   +---[FILE] enh_RURO_euromod.py | size: 56.24 KB | ext: .py
|   |   +---[FILE] enh_RURO_post_estimation.py | size: 54.94 KB | ext: .py
|   |   +---[FILE] enh_RURO_prep.py | size: 55.21 KB | ext: .py
|   |   +---[FILE] enh_RURO_prep_mnl_basic.py | size: 88.04 KB | ext: .py
|   |   +---[FILE] estimation_engine.py | size: 81.93 KB | ext: .py
|   |   +---[FILE] estimation_spec.yaml | size: 13.07 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_AC2013.yaml | size: 21.03 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_enhanced_minimal.yaml | size: 8.90 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_enhanced_minimal_v2.yaml | size: 11.02 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_choice_v0_id_enhanced.yaml | size: 6.93 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_choice_v0_id_strict.yaml | size: 4.26 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_choice_v0_minimal.yaml | size: 2.84 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_choice_v0_plus.yaml | size: 4.67 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_choice_v0_plus_b.yaml | size: 7.91 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_choice_v0_plus_c.yaml | size: 8.57 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_choice_v1.yaml | size: 10.27 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_choice_v1_dummies.yaml | size: 13.84 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_choice_v2.yaml | size: 15.96 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M0.yaml | size: 2.63 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M1.yaml | size: 3.19 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M2.yaml | size: 4.82 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M2_centered.yaml | size: 4.00 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M2_lite.yaml | size: 3.59 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M2_lite_scaled.yaml | size: 3.65 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M2_plus.yaml | size: 21.35 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M2_scaled.yaml | size: 4.01 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M2b.yaml | size: 5.40 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M2c.yaml | size: 8.05 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M2d_type.yaml | size: 5.90 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M2e_a.yaml | size: 8.99 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M2e_b.yaml | size: 8.24 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M2e_hours.yaml | size: 6.88 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M2e_type_fit.yaml | size: 6.31 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M2f_hybrid.yaml | size: 7.31 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M2g_unified_opportunity.yaml | size: 8.35 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M2h_pruned.yaml | size: 6.80 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_job_M3.yaml | size: 4.02 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_loc_empirical.yaml | size: 6.05 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_minimal.yaml | size: 3.82 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_minimal_theta0.yaml | size: 3.79 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_occupation_choice.yaml | size: 13.38 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_parser.py | size: 61.71 KB | ext: .py
|   |   +---[FILE] estimation_spec_pooled_consumption.yaml | size: 3.38 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_pooled_leisure.yaml | size: 3.24 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_simple.yaml | size: 5.08 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_ultra_minimal.yaml | size: 3.00 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_v2.yaml | size: 10.29 KB | ext: .yaml
|   |   +---[FILE] estimation_spec_v3.yaml | size: 14.99 KB | ext: .yaml
|   |   +---[FILE] estimation_utils.py | size: 60.94 KB | ext: .py
|   |   +---[FILE] estimation_utils_AC2013.py | size: 24.55 KB | ext: .py
|   |   +---[FILE] expression_constraints.py | size: 25.12 KB | ext: .py
|   |   +---[FILE] fix_spec_initial_values.py | size: 8.50 KB | ext: .py
|   |   +---[FILE] gamspy_estimation.py | size: 95.33 KB | ext: .py
|   |   +---[FILE] gamspy_estimation_vectorized.py | size: 63.30 KB | ext: .py
|   |   +---[FILE] mcfadden_sampler.py | size: 15.80 KB | ext: .py
|   |   +---[FILE] occupation_choice_utils.py | size: 16.81 KB | ext: .py
|   |   +---[FILE] parallel_estimation.py | size: 23.81 KB | ext: .py
|   |   +---[FILE] path_helpers.py | size: 6.73 KB | ext: .py
|   |   +---[FILE] quick_verify.py | size: 6.42 KB | ext: .py
|   |   +---[FILE] README.md | size: 10.27 KB | ext: .md
|   |   +---[FILE] reduce_draws_files.py | size: 14.81 KB | ext: .py
|   |   +---[FILE] reduce_mnl_columns.py | size: 24.37 KB | ext: .py
|   |   +---[FILE] run_diagnostics.ps1 | size: 3.23 KB | ext: .ps1
|   |   +---[FILE] run_enhanced_pipeline.ps1 | size: 36.14 KB | ext: .ps1
|   |   +---[FILE] RURO_post_estimation_styled.py | size: 237.55 KB | ext: .py
|   |   +---[FILE] sanity_checks.py | size: 25.44 KB | ext: .py
|   |   \---[FILE] validate_specs.py | size: 5.67 KB | ext: .py
|   +---[DIR] Job_model/
|   |   +---[FILE] ACCEPTANCE_TESTS.md | size: 15.01 KB | ext: .md
|   |   +---[FILE] Commands_job.txt | size: 3.79 KB | ext: .txt
|   |   +---[FILE] enh_job_draws.py | size: 40.83 KB | ext: .py
|   |   +---[FILE] enh_job_universe.py | size: 54.70 KB | ext: .py
|   |   +---[FILE] New Text Document.txt | size: 6.48 KB | ext: .txt
|   |   +---[FILE] plot_loc_by_dehde.py | size: 5.84 KB | ext: .py
|   |   +---[FILE] README_job_model.md | size: 7.59 KB | ext: .md
|   |   +---[FILE] run_job_ruro_pipeline.py | size: 15.49 KB | ext: .py
|   |   \---[FILE] sanity_checks_job.py | size: 21.12 KB | ext: .py
|   +---[DIR] runners/
|   |   \---[DIR] legacy/
|   |       +---[FILE] cleanup_final.ps1 | size: 6.41 KB | ext: .ps1
|   |       +---[FILE] README.md | size: 382 B | ext: .md
|   |       +---[FILE] run_gamspy_estimation.ps1 | size: 2.71 KB | ext: .ps1
|   |       +---[FILE] RUN_NOW.ps1 | size: 1.10 KB | ext: .ps1
|   |       +---[FILE] RUN_OPTIMIZED_ESTIMATION.ps1 | size: 1.92 KB | ext: .ps1
|   |       +---[FILE] RUN_PIPELINE_WITH_REDUCED_FILES.ps1 | size: 4.87 KB | ext: .ps1
|   |       +---[FILE] RUN_POST_ESTIMATION_STYLED.ps1 | size: 477 B | ext: .ps1
|   |       \---[FILE] RUN_WITH_SCIPY.ps1 | size: 1.92 KB | ext: .ps1
|   +---[FILE] extract_excel_text.py | size: 637 B | ext: .py
|   +---[FILE] france_data_prep.py | size: 67.86 KB | ext: .py
|   +---[FILE] generate_html_report.py | size: 10.95 KB | ext: .py
|   +---[FILE] init_params_singles_template.csv | size: 2.39 KB | ext: .csv
|   +---[FILE] path_helpers.py | size: 6.73 KB | ext: .py
|   +---[FILE] prepare_FR_gsur.py | size: 15.11 KB | ext: .py
|   +---[FILE] run_fr_2016_joint_only.ps1 | size: 28.01 KB | ext: .ps1
|   +---[FILE] run_fr_2016_pipeline.ps1 | size: 21.23 KB | ext: .ps1
|   +---[FILE] run_gamspy.ps1 | size: 1.32 KB | ext: .ps1
|   +---[FILE] run_pipeline_explicit.ipynb | size: 149.33 KB | ext: .ipynb
|   +---[FILE] run_post_estimation.ps1 | size: 5.17 KB | ext: .ps1
|   +---[FILE] run_post_estimation_standalone.py | size: 7.17 KB | ext: .py
|   +---[FILE] RURO_draws.py | size: 39.77 KB | ext: .py
|   +---[FILE] RURO_estimate_FR.py | size: 244.23 KB | ext: .py
|   +---[FILE] RURO_euromod.py | size: 41.31 KB | ext: .py
|   +---[FILE] RURO_post_estimation.py | size: 108.80 KB | ext: .py
|   +---[FILE] RURO_prep.py | size: 27.76 KB | ext: .py
|   +---[FILE] RURO_prep_mnl_basic.py | size: 31.37 KB | ext: .py
|   +---[FILE] seed_boxcox_init.csv | size: 297 B | ext: .csv
|   \---[FILE] tdo.ps1 | size: 2.09 KB | ext: .ps1
+---[DIR] src/
|   +---[DIR] mnl/
|   |   +---[DIR] data/
|   |   |   +---[FILE] __init__.py | size: 170 B | ext: .py
|   |   |   \---[FILE] loaders.py | size: 1.19 KB | ext: .py
|   |   +---[DIR] evaluation/
|   |   |   +---[FILE] __init__.py | size: 165 B | ext: .py
|   |   |   \---[FILE] metrics.py | size: 749 B | ext: .py
|   |   +---[DIR] integration/
|   |   |   +---[FILE] __init__.py | size: 196 B | ext: .py
|   |   |   \---[FILE] euromod.py | size: 5.81 KB | ext: .py
|   |   +---[DIR] models/
|   |   |   +---[FILE] __init__.py | size: 123 B | ext: .py
|   |   |   \---[FILE] mnl.py | size: 1.35 KB | ext: .py
|   |   +---[DIR] pipelines/
|   |   |   +---[FILE] __init__.py | size: 163 B | ext: .py
|   |   |   \---[FILE] estimation.py | size: 1.39 KB | ext: .py
|   |   +---[FILE] __init__.py | size: 298 B | ext: .py
|   |   \---[FILE] config.py | size: 1.38 KB | ext: .py
|   \---[DIR] mnl.egg-info/
|       +---[FILE] dependency_links.txt | size: 1 B | ext: .txt
|       +---[FILE] PKG-INFO | size: 4.79 KB | ext: [no extension]
|       +---[FILE] requires.txt | size: 292 B | ext: .txt
|       +---[FILE] SOURCES.txt | size: 522 B | ext: .txt
|       \---[FILE] top_level.txt | size: 4 B | ext: .txt
+---[DIR] ruro/
|   +---[FILE] Ruro_estimation_H.Rmd | size: 68.69 KB | ext: .Rmd
|   +---[FILE] Ruro_estimation_new.Rmd | size: 93.39 KB | ext: .Rmd
|   +---[FILE] Ruro_functions_EMRWS.R | size: 60.07 KB | ext: .R
|   \---[FILE] Ruro_simulation_H.Rmd | size: 306.23 KB | ext: .Rmd
+---[DIR] tests/
|   \---[FILE] test_imports.py | size: 125 B | ext: .py
+---[FILE] pyproject.toml | size: 1.14 KB | ext: .toml
+---[FILE] README.md | size: 20.38 KB | ext: .md
+---[FILE] requirements.txt | size: 3.70 KB | ext: .txt
\---[FILE] RURO_MNL_project_files_structure.md | size: 220 B | ext: .md
```
