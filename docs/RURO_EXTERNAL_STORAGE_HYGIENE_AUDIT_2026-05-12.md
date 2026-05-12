# RURO External Storage Hygiene Audit

Date: 2026-05-12

Scope:

- `U:\EUROMOD-STORAGE`
- `Z:\Hisham\EUROMOD-STORAGE`
- `Z:\Hisham\EUROMOD-STORAGE_1`
- repository `outputs/`

This audit is non-destructive. No external data were deleted or moved. The only files moved were generated inventory CSVs inside this repository, into `docs/archive/inventories/external_storage_2026-05-12/`.

## Short Answer

Use this as the current rule:

```text
Canonical active external data root:
Z:\Hisham\EUROMOD-STORAGE

Equivalent command-style path seen in metadata:
\\aff300msh.cifs.myliser.lu\ComputeShare\Hisham\EUROMOD-STORAGE
```

The most important current job-GMM data are only complete under:

```text
Z:\Hisham\EUROMOD-STORAGE
```

`U:\EUROMOD-STORAGE` is useful but should be treated as a partial/older mirror for the current job-GMM branch because it does not contain the final `fr_2016_RURO_mnl_job_gmm` MNL files or the job-GMM EUROMOD combined file.

`Z:\Hisham\EUROMOD-STORAGE_1` is an older snapshot. It should be treated as archive-only and is a candidate for removal once you have confirmed that `Z:\Hisham\EUROMOD-STORAGE` and repository documentation are sufficient.

## Inventory Artifacts

Generated inventories are stored here:

```text
docs/archive/inventories/external_storage_2026-05-12/
```

Files:

- `external_storage_top_level_inventory_2026-05-12.csv`
- `external_storage_full_file_inventory_2026-05-12.csv`
- `external_storage_cross_root_differences_2026-05-12.csv`
- `external_storage_ruro_file_inventory_2026-05-12.csv`
- `external_storage_ruro_directory_inventory_2026-05-12.csv`
- `external_storage_reports_results_inventory_2026-05-12.csv`
- `external_storage_key_metadata_summary_2026-05-12.csv`
- `external_storage_ruro1_topfolders_2026-05-12.csv`
- `external_storage_reports_topfolders_2026-05-12.csv`
- `external_storage_report_files_2026-05-12.csv`
- `repo_outputs_file_inventory_2026-05-12.csv`
- `repo_estimation_runs_inventory_2026-05-12.csv`
- `repo_estimation_results_summary_2026-05-12.csv`

Use the Markdown docs for decisions. Use the CSVs when you need exact file-level detail.

## Top-Level Storage Summary

### `U:\EUROMOD-STORAGE`

Approximate top-level contents:

| Folder | Files | Size | Interpretation |
| --- | ---: | ---: | --- |
| `Data` | 146 | 2.46 GB | useful processed/raw data, but not complete for current job-GMM final MNL |
| `interim` | 5 | 725.60 MB | continuous and non-GMM job EUROMOD combined files |
| `RURO1` | 750 | 6.22 GB | legacy experimental work, mostly old 2021/early RURO tries |
| `old_Data_results` | 914 | 401.82 MB | historical data/results, archive-only |
| `reports` | 317 | 7.48 MB | older DCM/Box-Cox reports, archive-only |
| `gamspy` | 70 | 1.45 MB | older Box-Cox/GAMSPy report artifacts, archive-only |
| `old rep` | 185 | 2.67 MB | old Biogeme/DCM reports, archive-only |
| `EUROMOD_RELEASES_J1.0+` | 213 | 1.89 GB | EUROMOD installation/reference, keep if scripts use it |

### `Z:\Hisham\EUROMOD-STORAGE`

Approximate top-level contents:

| Folder | Files | Size | Interpretation |
| --- | ---: | ---: | --- |
| `Data` | 149 | 2.77 GB | current best external data root |
| `interim` | 7 | 1.13 GB | includes current job-GMM EUROMOD combined file |
| `RURO1` | 750 | 6.22 GB | legacy experimental work copied from older storage |
| `old_Data_results` | 914 | 401.82 MB | historical data/results, archive-only |
| `reports` | 317 | 7.48 MB | older DCM/Box-Cox reports, archive-only |
| `gamspy` | 70 | 1.45 MB | older Box-Cox/GAMSPy report artifacts, archive-only |
| `old rep` | 185 | 2.67 MB | old Biogeme/DCM reports, archive-only |
| `EUROMOD_RELEASES_J1.0+` | 213 | 1.89 GB | EUROMOD installation/reference, keep if scripts use it |

### `Z:\Hisham\EUROMOD-STORAGE_1`

Approximate top-level contents:

| Folder | Files | Size | Interpretation |
| --- | ---: | ---: | --- |
| `Data` | 108 | 2.20 GB | older data snapshot, missing current job-GMM final outputs |
| `interim` | 3 | 528.67 MB | older continuous scenario only |
| `RURO1` | 750 | 6.22 GB | duplicate legacy experimental work |
| `old_Data_results` | 914 | 401.82 MB | duplicate archive copy |
| `reports` | 317 | 7.48 MB | duplicate archive copy |
| `gamspy` | 70 | 1.45 MB | duplicate archive copy |

Recommendation:

```text
Treat Z:\Hisham\EUROMOD-STORAGE_1 as archive-only.
Do not use it for new work.
Delete only after a deliberate backup decision.
```

## Current Active Data Lineage

The current job-GMM branch is recoverable from `Z:\Hisham\EUROMOD-STORAGE`.

### Step 1/2: Prepared FR 2016 Base Data

Path:

```text
Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016
```

Important files:

| File | Role |
| --- | --- |
| `fr_2016.parquet` | processed full FR 2016 base data |
| `fr_2016_singles.parquet` | processed singles |
| `fr_2016_singles_male.parquet` | processed male singles |
| `fr_2016_singles_female.parquet` | processed female singles |
| `fr_2016_couples.parquet` | processed couples |
| `singles_RURO_ready.parquet` | baseline singles ready for RURO draws |
| `couples_RURO_ready.parquet` | baseline couples ready for RURO draws |

### Continuous RURO Draws And MNL Files

Path:

```text
Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016
```

Important files:

| File | Role |
| --- | --- |
| `singles_RURO_ready_RURO_draws.parquet` | continuous singles alternatives |
| `couples_RURO_ready_RURO_draws.parquet` | continuous couples alternatives |
| `fr_2016_RURO_mnl__singles.parquet` | continuous MNL singles |
| `fr_2016_RURO_mnl__couples.parquet` | continuous MNL couples |
| `fr_2016_RURO_mnl__mnlmeta.json` | metadata for continuous MNL build |

Corresponding EUROMOD combined file:

```text
Z:\Hisham\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016\combined_draws_em.parquet
```

Metadata summary:

```text
script: enh_RURO_prep_mnl_basic.py
timestamp: 2026-02-05T13:09:06Z
wage_spec: vw
n_draws: 100
singles_deciders: 1676
couples_deciders: 2577
singles_total_rows: 167600
couples_total_rows: 257700
prior source: job_draw_log_q_total / job_draw_log_q_total_joint
```

Note: the metadata says `job_draw_log_q_total` even for the continuous branch because the MNL prep script uses a common prior field naming pattern. Interpret the branch by filenames and paths, not only that label.

### Non-GMM Job Model Files

Path:

```text
Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016
```

Important files:

| File | Role |
| --- | --- |
| `job_model\job_universe_2016.parquet` | non-GMM job universe |
| `job_model\job_universe_2016__meta.json` | non-GMM universe metadata |
| `singles_RURO_ready_jobdraws.parquet` | job draws; current copy differs from `U:` |
| `couples_RURO_ready_jobdraws.parquet` | job draws; current copy differs from `U:` |
| `fr_2016_RURO_mnl_job__singles.parquet` | non-GMM job MNL singles |
| `fr_2016_RURO_mnl_job__couples.parquet` | non-GMM job MNL couples |
| `fr_2016_RURO_mnl_job__mnlmeta.json` | non-GMM job MNL metadata |

Corresponding EUROMOD combined file:

```text
Z:\Hisham\EUROMOD-STORAGE\interim\ruro\fr\2016\job_model\scenarios\combined_draws_em.parquet
```

Metadata summary for non-GMM MNL:

```text
script: enh_RURO_prep_mnl_basic.py
timestamp: 2026-02-05T12:31:33Z
wage_spec: fw
n_draws: 100
singles_deciders: 1676
couples_deciders: 2577
```

### Current GMM Job Model Files

This is the most important current external data family.

Path:

```text
Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016
```

Important files:

| File | Role |
| --- | --- |
| `job_model_gmm\job_universe_2016.parquet` | GMM latent job-type universe |
| `job_model_gmm\job_universe_2016__meta.json` | GMM universe metadata |
| `job_model_gmm\job_universe_2016__gmm_diagnostics.csv` | per-occupation GMM diagnostics |
| `singles_RURO_ready_jobdraws.parquet` | GMM job draws for singles |
| `singles_RURO_ready_jobdraws__drawsmeta.json` | singles draw metadata |
| `couples_RURO_ready_jobdraws.parquet` | GMM job draws for couples |
| `couples_RURO_ready_jobdraws__drawsmeta.json` | couples draw metadata |
| `fr_2016_RURO_mnl_job_gmm__singles.parquet` | final GMM job-choice MNL singles |
| `fr_2016_RURO_mnl_job_gmm__couples.parquet` | final GMM job-choice MNL couples |
| `fr_2016_RURO_mnl_job_gmm__mnlmeta.json` | final GMM job-choice MNL metadata |

Corresponding EUROMOD combined file:

```text
Z:\Hisham\EUROMOD-STORAGE\interim\ruro\fr\2016\job_model_gmm\scenarios\combined_draws_em.parquet
```

Metadata summary:

```text
job universe script: enh_job_universe.py
job universe timestamp: 2026-02-08T20:43:18Z
universe_mode: gmm_occ
gmm_kmax: 6
gmm_contract_draws: 3
n_jobs: 88
n_cells_total: 89
n_working_deciders: 6561

job draws script: enh_job_draws.py
singles draw timestamp: 2026-02-08T20:53:51Z
couples draw timestamp: 2026-02-08T20:54:14Z
n_draws: 199
baseline_mode: posted

EUROMOD script: enh_RURO_euromod.py
EUROMOD timestamp: 2026-02-08T20:59:18Z
n_rows: 2174600
n_draws: 200

MNL script: enh_RURO_prep_mnl_basic.py
MNL timestamp: 2026-02-19T13:38:15Z
wage_spec: fw
n_draws: 200
singles_deciders: 1676
couples_deciders: 2577
singles_total_rows: 335200
couples_total_rows: 515400
gsur file: U:/Desktop/Nizam_Hisham/MNL/Data/external/FR_gsur_ruro.parquet
```

Interpretation:

```text
This is the external data family that supports the current job-choice/GMM estimation runs in repository outputs.
```

## Important Cross-Root Differences

The three roots are not interchangeable.

### Current job-GMM final files only exist on `Z:\Hisham\EUROMOD-STORAGE`

These were not found in `U:\EUROMOD-STORAGE` or `Z:\Hisham\EUROMOD-STORAGE_1`:

```text
Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__singles.parquet
Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__couples.parquet
Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__mnlmeta.json
interim\ruro\fr\2016\job_model_gmm\scenarios\combined_draws_em.parquet
interim\ruro\fr\2016\job_model_gmm\scenarios\combined_draws_em__euromodmeta.json
```

### `U:` has older jobdraws than `Z:`

Examples:

| Relative path | `U:` size/time | `Z:` size/time | Interpretation |
| --- | --- | --- | --- |
| `singles_RURO_ready_jobdraws.parquet` | 5.81 MB, 2026-02-04 | 8.63 MB, 2026-02-08 | `Z:` is newer GMM jobdraws |
| `couples_RURO_ready_jobdraws.parquet` | 16.54 MB, 2026-02-04 | 25.07 MB, 2026-02-08 | `Z:` is newer GMM jobdraws |
| `fr_2016_RURO_mnl_job__singles.parquet` | 8.87 MB, 2026-02-04 | 5.38 MB, 2026-02-05 | different non-GMM job MNL builds |
| `fr_2016_RURO_mnl_job__couples.parquet` | 29.39 MB, 2026-02-04 | 16.16 MB, 2026-02-05 | different non-GMM job MNL builds |

Recommendation:

```text
For future job-GMM work, use Z:\Hisham\EUROMOD-STORAGE or the equivalent UNC path.
Do not mix U: jobdraws with Z: job-GMM MNL files.
```

### `Z:\Hisham\EUROMOD-STORAGE_1` is older

It has older continuous MNL files and no current job-GMM final MNL files. It should not be used for future estimation unless you are deliberately reproducing an old January 2026 state.

## Repository Results And Reports

The active estimation results are not mainly in `U:\EUROMOD-STORAGE` or `Z:\Hisham\EUROMOD-STORAGE`. They are in the repository:

```text
outputs\estimates
outputs\post_estimation
```

Generated inventory:

```text
docs/archive/inventories/external_storage_2026-05-12/repo_estimation_results_summary_2026-05-12.csv
```

Observed result counts:

```text
estimation run directories: 168
runs with estimation_results.json summarized: 115
incomplete/diagnostic run folders: about 53
```

Current active registry:

```text
docs/RURO_ACTIVE_RESULTS_REGISTRY.md
```

Important registered runs:

| Role | Path | LL |
| --- | --- | ---: |
| current pruned candidate | `outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2h_pruned/run_2026-02-20_11-25-18` | -22203.61 |
| parent/comparison candidate | `outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2e_a/run_2026-02-20_10-04-46` | -21717.82 |
| continuous v3 exploratory baseline | `outputs/estimates/fr/spec/v3/gamspy/run_2026-02-05_14-11-43` | see summary CSV |

Additional later run found:

```text
outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2e_b/run_2026-02-20_11-24-37
```

Summary:

```text
timestamp: 2026-02-20T11:51:26
LL: -22161.05
spec: scripts/enhanced/estimation_spec_job_M2e_b.yaml
```

This run is newer than the active registry's M2h pruned run. It is not automatically promoted here because the active registry likely reflects a model-selection judgment, not only final log-likelihood. Do not delete this run before deciding whether it should be promoted, archived as comparison, or marked superseded.

## Legacy External Result Families

### `RURO1`

`RURO1` is a legacy experimental tree copied across all three storage roots.

Top-level folders:

| Folder | Size | Interpretation |
| --- | ---: | --- |
| `try1` | 899.57 MB | old 2021-style attempt |
| `try2` | 758.09 MB | old 2021-style attempt |
| `try3` | 3.45 GB | old 2021-style attempt; contains very large CSV exports |
| `try4` | 238.30 MB | later 2021-style attempt, smaller than `try3` |
| `2021` | 906.04 MB | old 2021-style attempt |
| `2016` | 31.72 MB | old 2016 attempt |
| `enhanced_results1` | 3.75 MB | old post-estimation/log results |
| `_bestwithses1`, `best_by_far`, `actua_1` | under 1 MB each | old selected report/result snapshots |
| `bad_results` | 15.84 KB | explicitly bad/failed results |
| `perpartion_2016` | 1.66 MB | likely old preparation diagnostics |

Recommendation:

```text
Archive RURO1 as historical.
Do not use RURO1 for current job-GMM or current continuous FR 2016 work.
```

Deletion candidates after archive:

- duplicate CSV exports in `try2`/`try3` when Parquet versions exist;
- `bad_results`;
- duplicate copies of `RURO1` in `U:` and `Z:\Hisham\EUROMOD-STORAGE_1`.

Do not delete until a backup/archive decision is made.

### `reports`, `gamspy`, `old rep`

These are older DCM/Box-Cox/Biogeme report families, mainly for older DE/panel/Box-Cox experiments. They are small and useful only for provenance.

Recommendation:

```text
Archive under historical DCM/Box-Cox material.
Do not treat as current RURO FR 2016 estimation output.
```

### `old_Data_results`

This is historical data/results from earlier work. It includes older data, outputs, scenarios, and Biogeme reports.

Recommendation:

```text
Archive only.
Keep temporarily until the current docs fully capture any useful provenance.
```

## Hygiene Classification

### Keep Active

Keep these for active work:

```text
Z:\Hisham\EUROMOD-STORAGE\Data\raw
Z:\Hisham\EUROMOD-STORAGE\Data\FR
Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016
Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\job_model_gmm
Z:\Hisham\EUROMOD-STORAGE\interim\ruro\fr\2016\job_model_gmm\scenarios
Z:\Hisham\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016
U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur_ruro.parquet
outputs\estimates\fr\spec\job_choice\gamspy
outputs\post_estimation\fr\spec\job_choice\gamspy
```

### Keep As Secondary / Do Not Use As Canonical

```text
U:\EUROMOD-STORAGE
```

Reason:

- useful mirror;
- contains current continuous MNL files;
- lacks current job-GMM final MNL files and job-GMM combined EUROMOD output;
- may cause mistakes if mixed with `Z:` current GMM files.

### Archive Candidates

```text
Z:\Hisham\EUROMOD-STORAGE_1
Z:\Hisham\EUROMOD-STORAGE\RURO1
Z:\Hisham\EUROMOD-STORAGE\old_Data_results
Z:\Hisham\EUROMOD-STORAGE\old rep
Z:\Hisham\EUROMOD-STORAGE\reports
Z:\Hisham\EUROMOD-STORAGE\gamspy
Z:\Hisham\EUROMOD-STORAGE\male_ascsON_q99
```

### Delete Candidates Only After Review

These can probably be deleted after archive verification:

- `Z:\Hisham\EUROMOD-STORAGE_1` as a whole, if it is confirmed to be a complete older duplicate and not needed for provenance;
- duplicate `RURO1` copies in `U:` and `Z:\Hisham\EUROMOD-STORAGE_1`;
- `RURO1\bad_results`;
- huge CSV versions in `RURO1\try2` and `RURO1\try3` when equivalent Parquet files exist;
- temporary `Thumbs.db` files;
- incomplete repository run folders that do not contain `estimation_results.json`, after the run inventory is reviewed.

## Proposed Archive Layout

Use one archive root per storage root:

```text
Z:\Hisham\EUROMOD-STORAGE\_archive\2026-05-12\
```

Suggested moves:

```text
RURO1 -> _archive\2026-05-12\RURO1
old_Data_results -> _archive\2026-05-12\old_Data_results
old rep -> _archive\2026-05-12\old rep
reports -> _archive\2026-05-12\reports_boxcox_dcm
gamspy -> _archive\2026-05-12\gamspy_boxcox_dcm
male_ascsON_q99 -> _archive\2026-05-12\male_ascsON_q99
```

For `Z:\Hisham\EUROMOD-STORAGE_1`, decide whether it should be:

1. renamed to `Z:\Hisham\EUROMOD-STORAGE_1_ARCHIVE_2026-01-19`; or
2. deleted after one final copy of this audit is kept.

Because this is external data storage, do not run recursive deletes until a reviewed delete manifest is created.

## Cleanup Manifest Needed Before Deletion

Before deleting anything, create:

```text
docs/RURO_EXTERNAL_STORAGE_DELETE_MANIFEST_YYYY-MM-DD.md
```

For every deletion candidate, record:

- full path;
- size;
- reason for deletion;
- replacement path or reason it is no longer needed;
- whether the file is already in an archive;
- whether any command or metadata file still references it.

Minimum rule:

```text
Never delete a file that appears in:
- an active command file;
- an active result metadata file;
- docs/RURO_ACTIVE_RESULTS_REGISTRY.md;
- docs/RURO_RETURN_GUIDE_DATA_RESULTS_AND_CLEANUP.md.
```

## Practical Rule For Future Work

When returning to the project:

1. Read `docs/RURO_RETURN_GUIDE_DATA_RESULTS_AND_CLEANUP.md`.
2. Use `Z:\Hisham\EUROMOD-STORAGE` for active external data.
3. Use repository `outputs/` for estimation and post-estimation reports.
4. Use `docs/RURO_ACTIVE_RESULTS_REGISTRY.md` to decide which result runs matter.
5. Treat `RURO1`, `old_Data_results`, `old rep`, old `reports`, and `Z:\Hisham\EUROMOD-STORAGE_1` as historical archive material.
6. Do not mix `U:` and `Z:` artifacts within one pipeline run unless you know they are the same file version.
