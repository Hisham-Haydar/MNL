# RURO Project Memory Map

Date: 2026-05-12

Purpose: quick recovery document for remembering what was built, where it is documented, and what is still scattered or stale.

## Short Answer

Most of the important work is documented, but not all in one place. The main topics are covered:

- continuous enhanced RURO pipeline;
- job-choice RURO pipeline;
- GMM occupation/job-type approach;
- GSUR preparation and merge;
- preference estimation;
- opportunity/preference identification status;
- command families;
- R reference comparison and sector-extension plan;
- project cleanup / package direction.

The biggest documentation risk is not absence. It is fragmentation. Some details live in old archived notes, some in command files, and some in script READMEs.

## Start With These Files

| Need | Read this |
| --- | --- |
| Overall project/package orientation | `README.md` |
| Self-contained A-to-Z methods and pipeline guide | `docs/RURO_METHODS_AND_PIPELINE_MANUAL_v1.md` |
| Country/year portability and cleanup policy | `docs/RURO_PACKAGE_PORTABILITY_AND_CLEANUP_POLICY_v1.md` |
| Index of non-`docs/` files mirrored into `docs/` | `docs/MIRRORED_DOCUMENTS_INDEX.md` |
| Active command entrypoints | `docs/PIPELINE_ENTRYPOINTS.md` |
| Practical return guide | `docs/RURO_RETURN_GUIDE_DATA_RESULTS_AND_CLEANUP.md` |
| External storage audit and cleanup plan | `docs/RURO_EXTERNAL_STORAGE_HYGIENE_AUDIT_2026-05-12.md` |
| Job model vs continuous RURO command split | `docs/RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md` |
| Full command inventory | `docs/RURO_ENHANCED_PIPELINE_COMMANDS.md` |
| Current result baselines | `docs/RURO_ACTIVE_RESULTS_REGISTRY.md` |
| Current identification status | `docs/RURO_CURRENT_STATE_AND_IDENTIFICATION.md` |
| Detailed preference estimation explanation | `docs/RURO_PREFERENCE_ESTIMATION_CAPABILITIES.md` |
| R reference comparison and sector plan | `docs/RURO_R_REFERENCE_COMPARISON_SECTOR_OPPORTUNITY_PLAN.md` |
| Job model details | `scripts/Job_model/README_job_model.md` |
| Job model validation / GMM tests | `scripts/Job_model/ACCEPTANCE_TESTS.md` |
| GMM job-model method note | `docs/RURO_JOB_MODEL_GMM_METHOD_NOTE.md` |
| GSUR preparation and merge note | `docs/RURO_GSUR_DATA_AND_MERGE_NOTE.md` |
| Exact GMM job command chain used | `scripts/Job_model/Commands_job.txt` |
| Cleanup decisions | `docs/RURO_PROJECT_HYGIENE_CLEANUP_RECOMMENDATIONS.md` |

## What Was Built

### 1. Continuous Enhanced RURO

Status: implemented and documented.

Main scripts:

- `scripts/enhanced/enh_france_data_prep.py`
- `scripts/enhanced/enh_RURO_prep.py`
- `scripts/enhanced/enh_RURO_draws.py`
- `scripts/enhanced/enh_RURO_euromod.py`
- `scripts/enhanced/enh_prepare_FR_gsur.py`
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py`
- `scripts/enhanced/enh_RURO_estimate_FR.py`
- `scripts/enhanced/RURO_post_estimation_styled.py`

Main docs:

- `scripts/enhanced/README.md`
- `docs/RURO_ENHANCED_PIPELINE_COMMANDS.md`
- `docs/RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md`
- `docs/FR2016_RURO_pipeline_report.md`

Key file markers:

- `singles_RURO_ready_RURO_draws.parquet`
- `couples_RURO_ready_RURO_draws.parquet`
- `fr_2016_RURO_mnl__singles.parquet`
- `fr_2016_RURO_mnl__couples.parquet`

### 2. Job-Choice RURO

Status: implemented and documented.

Main scripts:

- `scripts/Job_model/enh_job_universe.py`
- `scripts/Job_model/enh_job_draws.py`
- `scripts/Job_model/run_job_ruro_pipeline.py`
- shared downstream scripts in `scripts/enhanced/`

Main docs:

- `scripts/Job_model/README_job_model.md`
- `scripts/Job_model/ACCEPTANCE_TESTS.md`
- `docs/RURO_JOB_MODEL_GMM_METHOD_NOTE.md`
- `scripts/Job_model/Commands_job.txt`
- `docs/RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md`
- `docs/RURO_R_REFERENCE_COMPARISON_SECTOR_OPPORTUNITY_PLAN.md`

Key file markers:

- `job_universe_2016.parquet`
- `job_universe_2016__meta.json`
- `singles_RURO_ready_jobdraws.parquet`
- `couples_RURO_ready_jobdraws.parquet`
- `fr_2016_RURO_mnl_job_gmm__singles.parquet`
- `fr_2016_RURO_mnl_job_gmm__couples.parquet`

### 3. GMM Occupation / Latent Job-Type Approach

Status: implemented in current code and documented, but scattered.

Core idea:

```text
Within each occupation / ISCO group, fit latent job types using GMM.
Each latent type has representative hours/wages and optional contract draws.
The resulting job universe is sampled by the job-draw script.
```

Main implementation:

- `scripts/Job_model/enh_job_universe.py`
- `scripts/Job_model/enh_job_draws.py`
- `scripts/Job_model/sanity_checks_job.py`

Important CLI options:

- `--universe-mode gmm_occ`
- `--gmm-kmax`
- `--gmm-min-comp-count`
- `--gmm-min-comp-weight`
- `--gmm-rep-stat`
- `--gmm-trim-q`
- `--gmm-cov-type`
- `--gmm-contract-draws`
- `--job-id-mode deterministic`

Main docs:

- `scripts/Job_model/README_job_model.md`
- `scripts/Job_model/ACCEPTANCE_TESTS.md`
- `scripts/Job_model/Commands_job.txt`
- `docs/RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md`

Important command chain:

```text
scripts/Job_model/Commands_job.txt
```

Known stale note:

```text
scripts/Job_model/New Text Document.txt
```

This file says GMM was not applied. That appears stale relative to the current code, because `enh_job_universe.py` now supports `gmm_occ` and the current docs include GMM commands and acceptance tests. Do not use `New Text Document.txt` as current truth.

### 4. GSUR

Status: implemented and documented.

Core idea:

GSUR is used as an external unemployment/opportunity-rate shifter. The prepared file is:

```text
Data/external/FR_gsur_ruro.parquet
```

Main preparation script:

```text
scripts/enhanced/enh_prepare_FR_gsur.py
```

Typical command:

```powershell
python .\scripts\enhanced\enh_prepare_FR_gsur.py `
  --input "U:/Desktop/Nizam_Hisham/MNL/Data/external/FR_gsur.xlsx" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/Data/external"
```

Where GSUR enters:

- `enh_RURO_prep_mnl_basic.py` merges GSUR into the MNL files through `--gsur-file`.
- Continuous RURO can use GSUR in hours/opportunity terms.
- Job-choice RURO can use GSUR in market-opportunity terms such as `beta_offer_gsur_*`.

Main docs:

- `docs/RURO_GSUR_DATA_AND_MERGE_NOTE.md`
- `scripts/enhanced/README.md`
- `docs/FR2016_RURO_pipeline_report.md`
- `scripts/Job_model/README_job_model.md`
- `docs/RURO_CURRENT_STATE_AND_IDENTIFICATION.md`
- `docs/RURO_R_REFERENCE_COMPARISON_SECTOR_OPPORTUNITY_PLAN.md`

Important implementation note:

The job-model README documents that GSUR merge supports age-group matching and fallback to full-age bracket coverage. The implementation history says the current FR GSUR file effectively uses `Y20-64` fallback coverage.

### 5. Preference Estimation

Status: documented in detail.

Main doc:

```text
docs/RURO_PREFERENCE_ESTIMATION_CAPABILITIES.md
```

Core idea:

Preferences are Box-Cox utility terms in normalized consumption and leisure, with demographic shifters. They are estimated jointly with opportunity terms in the RURO likelihood.

Current best empirical baseline for preferences:

```text
outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2h_pruned/run_2026-02-20_11-25-18/
```

### 6. Preference vs Opportunity Identification

Status: documented.

Main docs:

- `docs/RURO_CURRENT_STATE_AND_IDENTIFICATION.md`
- `docs/RURO_R_REFERENCE_COMPARISON_AND_ACTION_PLAN.md`
- `docs/RURO_R_REFERENCE_COMPARISON_SECTOR_OPPORTUNITY_PLAN.md`

Current safe claim:

```text
The code can estimate separate preference and opportunity blocks.
The job-choice branch is the strongest empirical candidate.
The continuous French branch should not yet be described as fully separately identified.
```

### 7. Sector / Occupation Extension

Status: planned, not implemented as a clean sector layer.

Main doc:

```text
docs/RURO_R_REFERENCE_COMPARISON_SECTOR_OPPORTUNITY_PLAN.md
```

Current state:

- Job-choice RURO already has occupation/job availability through `isco1`, `job_id`, and market opportunity terms.
- This is not the same as a clean NACE/industry-sector opportunity layer.
- ISCO is occupation, not industry sector.
- A true sector extension should carry NACE/industry through data prep, draw generation, MNL prep, specification parsing, estimation, and reporting.

### 8. Results and Baselines

Status: documented.

Main doc:

```text
docs/RURO_ACTIVE_RESULTS_REGISTRY.md
```

Important runs:

```text
outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2h_pruned/run_2026-02-20_11-25-18/
outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2e_a/run_2026-02-20_10-04-46/
outputs/estimates/fr/spec/v3/gamspy/run_2026-02-05_14-11-43/
```

## What Is Still Not Perfectly Documented

### 1. GMM narrative was scattered

There is now a standalone GMM method note:

```text
docs/RURO_JOB_MODEL_GMM_METHOD_NOTE.md
```

The older details still also live across:

- `scripts/Job_model/README_job_model.md`
- `scripts/Job_model/ACCEPTANCE_TESTS.md`
- `scripts/Job_model/Commands_job.txt`
- `docs/RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md`

### 2. GSUR method note now exists

There is now a standalone GSUR note:

```text
docs/RURO_GSUR_DATA_AND_MERGE_NOTE.md
```

It explains:

- source file;
- output file;
- merge keys;
- age-group fallback;
- where GSUR enters opportunity equations;
- what `beta_gsur` / `beta_offer_gsur_*` mean.

### 3. Some old docs are now historical only

Archived docs are useful, but they may describe earlier project states. For current truth, prefer:

- `README.md`
- `docs/PIPELINE_ENTRYPOINTS.md`
- `docs/RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md`
- `docs/RURO_ACTIVE_RESULTS_REGISTRY.md`
- `docs/RURO_CURRENT_STATE_AND_IDENTIFICATION.md`

## Things To Ignore Or Treat Carefully

| File | Issue |
| --- | --- |
| `scripts/Job_model/New Text Document.txt` | Stale note saying GMM was not implemented; current code has `gmm_occ`. |
| `docs/archive/**` | Historical; useful for provenance but not always current. |
| `scripts/runners/legacy/**` | Old root runners; not current entrypoints. |
| many old `outputs/` folders | Do not infer current baseline from timestamp alone. Use `docs/RURO_ACTIVE_RESULTS_REGISTRY.md`. |

## If You Forget Everything Again

Read in this order:

1. `README.md`
2. `docs/RURO_PROJECT_MEMORY_MAP.md`
3. `docs/RURO_RETURN_GUIDE_DATA_RESULTS_AND_CLEANUP.md`
4. `docs/RURO_EXTERNAL_STORAGE_HYGIENE_AUDIT_2026-05-12.md`
5. `docs/RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md`
6. `docs/RURO_JOB_MODEL_GMM_METHOD_NOTE.md`
7. `docs/RURO_GSUR_DATA_AND_MERGE_NOTE.md`
8. `scripts/Job_model/Commands_job.txt`
9. `docs/RURO_ACTIVE_RESULTS_REGISTRY.md`
10. `docs/RURO_CURRENT_STATE_AND_IDENTIFICATION.md`
