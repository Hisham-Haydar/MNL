# RURO Commands: Job Model vs Continuous Enhanced RURO

Date: 2026-05-12

This note explains how to distinguish commands for:

1. the continuous enhanced RURO pipeline; and
2. the job-choice / job-model RURO pipeline.

The two pipelines share some later scripts, but they differ in how alternatives are generated and in the file names passed into Step 6 estimation preparation.

Related method notes:

- `docs/methods/RURO_JOB_MODEL_GMM_METHOD_NOTE.md`
- `docs/estimation/RURO_GSUR_DATA_AND_MERGE_NOTE.md`

## Quick Rule

If the command uses:

```text
scripts/Job_model/
*_jobdraws.parquet
job_model or job_model_gmm
fr_2016_RURO_mnl_job or fr_2016_RURO_mnl_job_gmm
estimation_spec_job_*.yaml
outputs/estimates/fr/spec/job_choice/
```

then it is a **job-model / job-choice RURO** command.

If the command uses:

```text
scripts/enhanced/enh_RURO_draws.py
*_RURO_draws.parquet
scenarios_2016
fr_2016_RURO_mnl
estimation_spec_v*.yaml or estimation_spec.yaml
outputs/estimates/fr/spec/v*/
```

then it is a **continuous enhanced RURO** command, not the job model.

## Conceptual Difference

### Continuous Enhanced RURO

The continuous branch creates alternatives by drawing hours and wages directly.

Typical generated files:

```text
singles_RURO_ready_RURO_draws.parquet
couples_RURO_ready_RURO_draws.parquet
combined_draws_em.parquet
fr_2016_RURO_mnl__singles.parquet
fr_2016_RURO_mnl__couples.parquet
```

The economic opportunity object is approximately:

```text
non-employment / hours opportunity + wage opportunity
```

### Job-Model / Job-Choice RURO

The job branch first builds a discrete job universe, then draws jobs.

Typical generated files:

```text
job_universe_2016.parquet
job_universe_2016__meta.json
singles_RURO_ready_jobdraws.parquet
couples_RURO_ready_jobdraws.parquet
combined_draws_em.parquet
fr_2016_RURO_mnl_job_gmm__singles.parquet
fr_2016_RURO_mnl_job_gmm__couples.parquet
```

The economic opportunity object is approximately:

```text
job = hours bin + wage bin + occupation / ISCO + optional latent type
```

## Command Families

## A. Continuous Enhanced RURO Commands

These are the non-job-model commands.

### A1. Full Continuous Enhanced Runner

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\enhanced\run_enhanced_pipeline.ps1
```

This runner calls the continuous draw generator:

```text
scripts/enhanced/enh_RURO_draws.py
```

It does not call:

```text
scripts/Job_model/enh_job_universe.py
scripts/Job_model/enh_job_draws.py
```

### A2. Continuous Step 1: France Prep

```powershell
python .\scripts\enhanced\enh_france_data_prep.py `
  --year 2016 `
  --raw-dir "Z:/hisham/EUROMOD-STORAGE/Data/raw" `
  --out-dir "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016" `
  --system-year 2015 `
  --export-format parquet
```

This command is shared. Both the continuous and job-model branches usually start from the same prepared data.

### A3. Continuous Step 2: RURO Prep

```powershell
python .\scripts\enhanced\enh_RURO_prep.py `
  --processed-dir "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016" `
  --base-year 2016 `
  --export-format parquet
```

This command is also shared.

### A4. Continuous Step 3: Draw Hours/Wages Directly

```powershell
python .\scripts\enhanced\enh_RURO_draws.py `
  --singles-path "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --couples-path "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready.parquet" `
  --n-draws 99 `
  --wage-spec vw
```

This is the key continuous-RURO marker.

Outputs:

```text
singles_RURO_ready_RURO_draws.parquet
couples_RURO_ready_RURO_draws.parquet
```

### A5. Continuous Step 4: EUROMOD

```powershell
python .\scripts\enhanced\enh_RURO_euromod.py `
  --singles-draws "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_RURO_draws.parquet" `
  --couples-draws "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_RURO_draws.parquet" `
  --microdata-template "Z:/hisham/EUROMOD-STORAGE/Data/raw/FR_2016.txt" `
  --euromod-system FR_2015 `
  --euromod-dataset FR_2016 `
  --euromod-root "Z:/hisham/EUROMOD-STORAGE/EUROMOD_RELEASES_J1.0+/EUROMOD_RELEASES_J1.0+" `
  --scenario-dir "Z:/hisham/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016"
```

Continuous marker:

```text
scenarios_2016
*_RURO_draws.parquet
```

### A6. Continuous Step 5: MNL Prep

```powershell
python .\scripts\enhanced\enh_RURO_prep_mnl_basic.py `
  --singles-draws "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_RURO_draws.parquet" `
  --couples-draws "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_RURO_draws.parquet" `
  --euromod-combined "Z:/hisham/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016/combined_draws_em.parquet" `
  --out-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --wage-spec vw `
  --year 2016 `
  --gsur-file "U:/Desktop/Nizam_Hisham/MNL/Data/external/FR_gsur_ruro.parquet"
```

Continuous markers:

```text
--out-base .../fr_2016_RURO_mnl
--wage-spec vw
*_RURO_draws.parquet
```

### A7. Continuous Estimation

Example:

```powershell
python .\scripts\enhanced\enh_RURO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/v3/gamspy" `
  --group joint `
  --solver gamspy-conopt `
  --vectorized `
  --spec-config "scripts/enhanced/estimation_spec_v3.yaml" `
  --warm-start none `
  --auto-timestamp `
  --verbose
```

Continuous markers:

```text
fr_2016_RURO_mnl
estimation_spec_v3.yaml
outputs/estimates/fr/spec/v3/
```

## B. Job-Model / Job-Choice RURO Commands

These are the commands for the job model.

### B1. Job-Model Step 1: France Prep

```powershell
python .\scripts\enhanced\enh_france_data_prep.py `
  --year 2016 `
  --raw-dir "Z:/hisham/EUROMOD-STORAGE/Data/raw" `
  --out-dir "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016" `
  --system-year 2015 `
  --export-format parquet
```

This is shared with continuous RURO.

### B2. Job-Model Step 2: RURO Prep

```powershell
python .\scripts\enhanced\enh_RURO_prep.py `
  --processed-dir "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016" `
  --base-year 2016 `
  --export-format parquet
```

This is shared with continuous RURO.

### B3. Job-Model Step 3: Build Job Universe

```powershell
python .\scripts\Job_model\enh_job_universe.py `
  --singles-path "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --couples-path "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready.parquet" `
  --output-dir "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/job_model_gmm" `
  --year 2016 `
  --universe-mode gmm_occ `
  --gmm-kmax 6 `
  --gmm-min-comp-count 50 `
  --gmm-min-comp-weight 0.03 `
  --gmm-rep-stat mean `
  --gmm-cov-type full `
  --gmm-contract-draws 3 `
  --job-id-mode deterministic `
  --include-isco0 0 `
  --seed 13
```

Job-model markers:

```text
scripts/Job_model/enh_job_universe.py
job_model_gmm
--universe-mode gmm_occ
```

### B4. Job-Model Step 4: Draw Jobs

```powershell
python .\scripts\Job_model\enh_job_draws.py `
  --singles-path "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --couples-path "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready.parquet" `
  --job-universe "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/job_model_gmm/job_universe_2016.parquet" `
  --job-metadata "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/job_model_gmm/job_universe_2016__meta.json" `
  --n-draws 199 `
  --baseline-mode posted `
  --seed 13
```

Job-model markers:

```text
scripts/Job_model/enh_job_draws.py
job_universe_2016.parquet
job_universe_2016__meta.json
```

Outputs:

```text
singles_RURO_ready_jobdraws.parquet
couples_RURO_ready_jobdraws.parquet
```

### B5. Job-Model Step 5: EUROMOD On Job Draws

```powershell
python .\scripts\enhanced\enh_RURO_euromod.py `
  --singles-draws "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_jobdraws.parquet" `
  --couples-draws "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_jobdraws.parquet" `
  --microdata-template "Z:/hisham/EUROMOD-STORAGE/Data/raw/FR_2016.txt" `
  --euromod-system FR_2015 `
  --euromod-dataset FR_2016 `
  --euromod-root "Z:/hisham/EUROMOD-STORAGE/EUROMOD_RELEASES_J1.0+/EUROMOD_RELEASES_J1.0+" `
  --scenario-dir "Z:/hisham/EUROMOD-STORAGE/interim/ruro/fr/2016/job_model_gmm/scenarios"
```

This uses the shared EUROMOD script, but the inputs make it a job-model command.

Job-model markers:

```text
*_jobdraws.parquet
job_model_gmm/scenarios
```

### B6. Job-Model Step 6: MNL Prep

This is the command you identified.

```powershell
python .\scripts\enhanced\enh_RURO_prep_mnl_basic.py `
  --singles-draws "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_jobdraws.parquet" `
  --couples-draws "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_jobdraws.parquet" `
  --euromod-combined "Z:/hisham/EUROMOD-STORAGE/interim/ruro/fr/2016/job_model_gmm/scenarios/combined_draws_em.parquet" `
  --out-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_job_gmm" `
  --wage-spec fw `
  --year 2016 `
  --gsur-file "U:/Desktop/Nizam_Hisham/MNL/Data/external/FR_gsur_ruro.parquet" `
  --no-column-filter
```

Job-model markers:

```text
*_jobdraws.parquet
job_model_gmm/scenarios
fr_2016_RURO_mnl_job_gmm
--wage-spec fw
--no-column-filter
```

### B7. Job-Model Estimation

Example from the recorded job commands:

```powershell
python .\scripts\enhanced\enh_RURO_estimate_FR.py `
  --mnl-base "\\aff300msh.cifs.myliser.lu\ComputeShare\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/job_choice/gamspy" `
  --group joint `
  --solver gamspy-conopt `
  --vectorized `
  --spec-config "scripts/enhanced/estimation_spec_job_M2c.yaml" `
  --warm-start none `
  --auto-timestamp `
  --verbose
```

Job-model markers:

```text
fr_2016_RURO_mnl_job_gmm
outputs/estimates/fr/spec/job_choice/gamspy
estimation_spec_job_*.yaml
```

Current stronger job-choice candidates use specs such as:

```text
scripts/enhanced/estimation_spec_job_M2h_pruned.yaml
scripts/enhanced/estimation_spec_job_M2e_a.yaml
```

### B8. Job-Model Post-Estimation

```powershell
python scripts/enhanced/RURO_post_estimation_styled.py `
  --results-json "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/job_choice/gamspy/run_2026-02-19_13-37-33/estimation_results.json" `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_job_gmm" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/post_estimation/fr/spec/job_choice/gamspy" `
  --prefix "fr_2016_jobchoice_gmm_gamspy_" `
  --compute-se `
  --spec-config "scripts/enhanced/estimation_spec_job_M2c.yaml" `
  --auto-timestamp
```

Job-model markers:

```text
jobchoice
job_gmm
estimation_spec_job_*.yaml
```

## Shared Commands

These commands are shared and are not enough by themselves to identify the branch:

```text
enh_france_data_prep.py
enh_RURO_prep.py
enh_RURO_euromod.py
enh_RURO_prep_mnl_basic.py
enh_RURO_estimate_FR.py
RURO_post_estimation_styled.py
```

The branch is identified by the inputs and outputs:

| Shared script | Continuous inputs | Job-model inputs |
| --- | --- | --- |
| `enh_RURO_euromod.py` | `*_RURO_draws.parquet` | `*_jobdraws.parquet` |
| `enh_RURO_prep_mnl_basic.py` | `fr_2016_RURO_mnl` | `fr_2016_RURO_mnl_job_gmm` |
| `enh_RURO_estimate_FR.py` | `estimation_spec_v*.yaml` | `estimation_spec_job_*.yaml` |
| `RURO_post_estimation_styled.py` | `fr_2016_gamspy_` prefix | `fr_2016_jobchoice_gmm_gamspy_` prefix |
