# RURO Return Guide: Data, Results, Commands, And Cleanup

Date: 2026-05-12

Purpose: this is the practical guide to use when returning to the project after time away. It tells you which storage root to use, what each pipeline step does, where outputs go, and what is safe or unsafe to clean.

## Start Here

Read these first:

1. `README.md`
2. `docs/RURO_PROJECT_MEMORY_MAP.md`
3. `docs/RURO_EXTERNAL_STORAGE_HYGIENE_AUDIT_2026-05-12.md`
4. `docs/RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md`
5. `docs/RURO_ACTIVE_RESULTS_REGISTRY.md`

## Current Canonical Roots

### Repository Root

```text
\\crc\users\hisham\Desktop\Nizam_Hisham\MNL
```

Equivalent local-style path seen in the IDE:

```text
H:\Desktop\Nizam_Hisham\MNL
```

This contains:

- source code;
- scripts;
- documentation;
- specs;
- repository-level estimation outputs and post-estimation reports.

### Active External Data Root

Use:

```text
Z:\Hisham\EUROMOD-STORAGE
```

The same storage appears in metadata as:

```text
\\aff300msh.cifs.myliser.lu\ComputeShare\Hisham\EUROMOD-STORAGE
```

This contains the current job-GMM data and EUROMOD combined files.

### Secondary / Older External Root

```text
U:\EUROMOD-STORAGE
```

Treat this as secondary. It does not contain the final current job-GMM MNL files.

### Old Snapshot

```text
Z:\Hisham\EUROMOD-STORAGE_1
```

Treat this as archive-only.

## What To Do Depending On Your Goal

## Goal A: Run Or Reproduce Current Job-GMM RURO

Use this branch when you want the most developed current preference/opportunity work.

Read:

- `docs/RURO_JOB_MODEL_GMM_METHOD_NOTE.md`
- `docs/RURO_GSUR_DATA_AND_MERGE_NOTE.md`
- `scripts/Job_model/Commands_job.txt`

Canonical data base:

```text
Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016
```

Canonical MNL base:

```text
Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm
```

Equivalent UNC MNL base used in result metadata:

```text
\\aff300msh.cifs.myliser.lu\ComputeShare\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm
```

### Job-GMM Step Map

| Step | Script | Main inputs | Main outputs | What happens |
| --- | --- | --- | --- | --- |
| 1 | `enh_france_data_prep.py` | raw FR data | `fr_2016*.parquet` | builds cleaned base FR 2016 files |
| 2 | `enh_RURO_prep.py` | processed FR data | `singles_RURO_ready.parquet`, `couples_RURO_ready.parquet` | builds RURO baseline files |
| 3 | `enh_job_universe.py` | RURO-ready files | `job_model_gmm\job_universe_2016.*` | fits GMM latent job types within ISCO |
| 4 | `enh_job_draws.py` | job universe, RURO-ready files | `*_jobdraws.parquet` | samples job alternatives |
| 5 | `enh_RURO_euromod.py` | `*_jobdraws.parquet` | `interim\ruro\fr\2016\job_model_gmm\scenarios\combined_draws_em.parquet` | runs EUROMOD on job alternatives |
| 6 | `enh_RURO_prep_mnl_basic.py` | jobdraws, EUROMOD combined, GSUR | `fr_2016_RURO_mnl_job_gmm__*.parquet` | builds estimation-ready MNL files |
| 7 | `enh_RURO_estimate_FR.py` | MNL base, YAML spec | timestamped run under `outputs\estimates` | estimates preferences and opportunities |
| 8 | `RURO_post_estimation_styled.py` | `estimation_results.json`, MNL base | timestamped reports under `outputs\post_estimation` | creates HTML diagnostics/reports |

### What Running Each Step Overwrites

Be careful with Steps 1-6 because they write deterministic filenames.

| Step | Overwrite risk |
| --- | --- |
| Step 1 | can replace `fr_2016*.parquet` in `Data\processed\fr\2016` |
| Step 2 | can replace `singles_RURO_ready.parquet` and `couples_RURO_ready.parquet` |
| Step 3 | can replace `job_model_gmm\job_universe_2016.*` |
| Step 4 | can replace `singles_RURO_ready_jobdraws.parquet` and `couples_RURO_ready_jobdraws.parquet` |
| Step 5 | can replace `job_model_gmm\scenarios\combined_draws_em.parquet` |
| Step 6 | can replace `fr_2016_RURO_mnl_job_gmm__*.parquet` |
| Step 7 | normally creates a new timestamped run if `--auto-timestamp` is used |
| Step 8 | normally creates a new timestamped report folder if `--auto-timestamp` is used |

Before rerunning Steps 3-6, copy or archive the existing outputs if you need the old state.

### Current Job-GMM External State

The current external files indicate:

```text
GMM universe timestamp: 2026-02-08T20:43:18Z
GMM universe mode: gmm_occ
GMM contract draws: 3
GMM jobs: 88 working jobs plus non-employment

Job draws:
singles timestamp: 2026-02-08T20:53:51Z
couples timestamp: 2026-02-08T20:54:14Z
n_draws: 199 simulated + baseline = 200 alternatives

EUROMOD combined:
timestamp: 2026-02-08T20:59:18Z
n_rows: 2,174,600
n_draws: 200

MNL job-GMM:
timestamp: 2026-02-19T13:38:15Z
wage_spec: fw
singles_total_rows: 335,200
couples_total_rows: 515,400
```

This is the external dataset behind the current job-choice runs.

## Goal B: Run Continuous Enhanced RURO

Use this branch when comparing with the R reference's original continuous hours/wage approach.

Read:

- `docs/RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md`
- `docs/RURO_ENHANCED_PIPELINE_COMMANDS.md`
- `scripts/enhanced/README.md`

Canonical data base:

```text
Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl
```

Important external files:

```text
Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready_RURO_draws.parquet
Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet
Z:\Hisham\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016\combined_draws_em.parquet
Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl__singles.parquet
Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl__couples.parquet
```

Continuous branch markers:

```text
enh_RURO_draws.py
*_RURO_draws.parquet
scenarios_2016
fr_2016_RURO_mnl
estimation_spec_v*.yaml
```

## Goal C: Inspect Results

Use:

```text
docs/RURO_ACTIVE_RESULTS_REGISTRY.md
```

Then inspect:

```text
outputs\estimates
outputs\post_estimation
```

The repository currently has many historical runs:

```text
estimation run directories: 168
runs with estimation_results.json: 115
```

Do not browse by timestamp alone. Use the active registry and the result summary CSV:

```text
docs/archive/inventories/external_storage_2026-05-12/repo_estimation_results_summary_2026-05-12.csv
```

Important known runs:

| Role | Path |
| --- | --- |
| current pruned candidate | `outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2h_pruned/run_2026-02-20_11-25-18` |
| parent/comparison candidate | `outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2e_a/run_2026-02-20_10-04-46` |
| later candidate to review | `outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2e_b/run_2026-02-20_11-24-37` |
| continuous v3 reference | `outputs/estimates/fr/spec/v3/gamspy/run_2026-02-05_14-11-43` |

### What A Run Folder Should Contain

A complete estimation run normally has:

```text
estimation_results.json
estimation_summary.txt
identification_diagnostics.txt
specification_used.yaml
```

Some older runs do not have `identification_diagnostics.txt`. Treat them as older-generation output.

### What Post-Estimation Reports Need

Post-estimation reports need:

- `estimation_results.json`;
- matching MNL base;
- matching spec YAML;
- same branch family, continuous vs job-choice.

If the report was generated from a job-GMM run, use:

```text
Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm
```

## Goal D: Clean Or Archive

Do not delete first. Classify first.

Use:

```text
docs/RURO_EXTERNAL_STORAGE_HYGIENE_AUDIT_2026-05-12.md
```

## Active Keep List

Keep these as active:

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

## Archive-Only List

Treat these as historical:

```text
Z:\Hisham\EUROMOD-STORAGE_1
Z:\Hisham\EUROMOD-STORAGE\RURO1
Z:\Hisham\EUROMOD-STORAGE\old_Data_results
Z:\Hisham\EUROMOD-STORAGE\old rep
Z:\Hisham\EUROMOD-STORAGE\reports
Z:\Hisham\EUROMOD-STORAGE\gamspy
Z:\Hisham\EUROMOD-STORAGE\male_ascsON_q99
U:\EUROMOD-STORAGE\RURO1
U:\EUROMOD-STORAGE\old_Data_results
U:\EUROMOD-STORAGE\old rep
U:\EUROMOD-STORAGE\reports
U:\EUROMOD-STORAGE\gamspy
```

## Suggested Archive Folder

Use:

```text
Z:\Hisham\EUROMOD-STORAGE\_archive\2026-05-12
```

Suggested move plan:

```text
RURO1 -> _archive\2026-05-12\RURO1
old_Data_results -> _archive\2026-05-12\old_Data_results
old rep -> _archive\2026-05-12\old rep
reports -> _archive\2026-05-12\reports_boxcox_dcm
gamspy -> _archive\2026-05-12\gamspy_boxcox_dcm
male_ascsON_q99 -> _archive\2026-05-12\male_ascsON_q99
```

Do not move `Data`, `interim`, or `EUROMOD_RELEASES_J1.0+` during ordinary cleanup.

## Delete Rules

Only delete when all conditions are true:

1. The file/folder is listed in a reviewed delete manifest.
2. A replacement or archive path is documented.
3. No active command references it.
4. No active result metadata references it.
5. It is not part of the active keep list.

Create this before deleting:

```text
docs/RURO_EXTERNAL_STORAGE_DELETE_MANIFEST_YYYY-MM-DD.md
```

## What Each Major Folder Means

### `Data\raw`

Raw EUROMOD text and DRD files. Keep.

### `Data\FR`

Country raw/reference files. Keep.

### `Data\processed\fr\2016`

Main processed FR 2016 data and generated estimation data. Keep active.

### `interim\ruro`

EUROMOD scenario outputs. Keep current scenario folders:

```text
interim\ruro\fr\scenarios_2016
interim\ruro\fr\2016\job_model\scenarios
interim\ruro\fr\2016\job_model_gmm\scenarios
```

### `outputs` inside external storage

Mostly preparation plots and older exported files. It is not the active estimation output root. Current estimation outputs are in repository `outputs`.

### repository `outputs`

Current estimation and post-estimation run folders. Keep active runs; archive or remove incomplete runs only after reviewing the run inventory.

### `RURO1`

Old experimental tree. Useful for history, not current work.

### `old_Data_results`, `old rep`, old `reports`, old `gamspy`

Historical DCM/Box-Cox/Biogeme outputs. Archive-only.

## Safe Workflow For A New Experiment

1. Choose the branch:

```text
continuous RURO
job-choice RURO
job-choice GMM RURO
```

2. Create or choose a new spec YAML under:

```text
scripts\enhanced
```

3. Do not rerun Steps 1-6 unless the data-generating process changed.

For many experiments, you can start at estimation:

```powershell
python .\scripts\enhanced\enh_RURO_estimate_FR.py `
  --mnl-base "\\aff300msh.cifs.myliser.lu\ComputeShare\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/job_choice/gamspy" `
  --group joint `
  --solver gamspy-conopt `
  --vectorized `
  --spec-config "scripts/enhanced/YOUR_SPEC.yaml" `
  --warm-start none `
  --auto-timestamp `
  --verbose
```

4. After estimation, generate a report:

```powershell
python .\scripts\enhanced\RURO_post_estimation_styled.py `
  --results-json "outputs/estimates/fr/spec/job_choice/gamspy/YOUR_SPEC/run_YYYY-MM-DD_HH-MM-SS/estimation_results.json" `
  --mnl-base "Z:/Hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_job_gmm" `
  --output-dir "outputs/post_estimation/fr/spec/job_choice/gamspy" `
  --prefix "fr_2016_jobchoice_gmm_" `
  --compute-se `
  --spec-config "scripts/enhanced/YOUR_SPEC.yaml" `
  --auto-timestamp
```

5. Promote or archive the run:

- update `docs/RURO_ACTIVE_RESULTS_REGISTRY.md` if it becomes an active baseline;
- otherwise leave it as historical run output;
- do not delete it until a cleanup pass has recorded it.

## Common Mistakes To Avoid

### Mixing `U:` and `Z:` inputs

Do not use `U:` jobdraws with `Z:` MNL outputs. The current job-GMM data are complete on `Z:`.

### Rerunning Step 6 with the wrong branch

If `--singles-draws` points to `*_RURO_draws.parquet`, you are building continuous RURO MNL.

If `--singles-draws` points to `*_jobdraws.parquet`, you are building job-choice MNL.

### Using old `RURO1` files as if they are current

`RURO1` is historical. It includes useful early experiments but is not the active branch.

### Treating log-likelihood alone as model selection

A newer run such as `M2e_b` may have a different LL than the registered baseline. Promotion should also consider identification diagnostics, bounds, Hessian, interpretability, and the research question.

### Deleting old runs before recording why

Before deleting, create a manifest. The point is reproducibility, not only disk space.

## If You Forget Again

Use this order:

1. `docs/RURO_PROJECT_MEMORY_MAP.md`
2. `docs/RURO_RETURN_GUIDE_DATA_RESULTS_AND_CLEANUP.md`
3. `docs/RURO_EXTERNAL_STORAGE_HYGIENE_AUDIT_2026-05-12.md`
4. `docs/RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md`
5. `scripts/Job_model/Commands_job.txt`
6. `docs/RURO_ACTIVE_RESULTS_REGISTRY.md`
