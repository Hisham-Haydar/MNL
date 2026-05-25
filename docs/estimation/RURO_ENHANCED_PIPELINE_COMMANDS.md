# RURO Enhanced Pipeline Commands

Date: 2026-05-12

This document lists the commands found in the active enhanced pipeline scripts and archived command logs.

For a cleaner split between the job-model commands and the continuous enhanced RURO commands, see:

- `docs/methods/RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md`
- `docs/methods/RURO_JOB_MODEL_GMM_METHOD_NOTE.md`
- `docs/estimation/RURO_GSUR_DATA_AND_MERGE_NOTE.md`

Sources inspected:

- `scripts/enhanced/run_enhanced_pipeline.ps1`
- `scripts/enhanced/enh_pipeline.ps1`
- `scripts/enhanced/run_diagnostics.ps1`
- `scripts/Job_model/Commands_job.txt`
- `docs/archive/commands/commands_legacy.txt`
- `docs/archive/commands/commands_20260122_143200.txt`

## 1. Main Enhanced Pipeline Runner

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run the active full enhanced pipeline:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\enhanced\run_enhanced_pipeline.ps1
```

Runner options documented in the script:

```powershell
.\scripts\enhanced\run_enhanced_pipeline.ps1 -SkipTo 7
.\scripts\enhanced\run_enhanced_pipeline.ps1 -OnlyStep 8
.\scripts\enhanced\run_enhanced_pipeline.ps1 -SkipSteps "1,2,3"
.\scripts\enhanced\run_enhanced_pipeline.ps1 -ForceRebuild
```

## 2. User-Confirmed Job-Choice GMM Command Chain

This is the command chain recorded in `scripts/Job_model/Commands_job.txt`. It matches the command you identified for the MNL preparation step using `fr_2016_RURO_mnl_job_gmm`.

### Step 1: France Preparation

```powershell
python .\scripts\enhanced\enh_france_data_prep.py `
  --year 2016 `
  --raw-dir "Z:/hisham/EUROMOD-STORAGE/Data/raw" `
  --out-dir "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016" `
  --system-year 2015 `
  --export-format parquet
```

### Step 2: RURO Preparation

```powershell
python .\scripts\enhanced\enh_RURO_prep.py `
  --processed-dir "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016" `
  --base-year 2016 `
  --export-format parquet
```

### Step 3: GMM Job Universe

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

### Step 4: GMM Job Draws

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

### Step 5: EUROMOD On GMM Job Draws

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

### Step 6: MNL Preparation For GMM Job Choice

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

### Step 7: GMM Job-Choice Estimation

This recorded command estimates from `fr_2016_RURO_mnl_job_gmm` using `estimation_spec_job_M2c.yaml`.

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

### Step 8: GMM Job-Choice Post-Estimation Report

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

## 3. Commands Generated By `run_enhanced_pipeline.ps1`

The active runner uses these default settings:

```text
YEAR = 2016
SYSTEM_YEAR = 2015
N_DRAWS = 99
WAGE_SPEC = vw
MAX_ITER = 5000
PROJECT_ROOT = U:\Desktop\Nizam_Hisham\MNL
DATA_ROOT = U:\EUROMOD-STORAGE\Data
SCENARIO_DIR = U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016
EUROMOD_ROOT = U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+
```

### Step 1: Data Preparation

```powershell
python "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_france_data_prep.py" `
  --year 2016 `
  --raw-dir "U:\EUROMOD-STORAGE\Data\raw" `
  --out-dir "U:\EUROMOD-STORAGE\Data\processed\fr\2016" `
  --system-year 2015 `
  --export-format parquet
```

### Step 2: RURO Preparation

```powershell
python "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_prep.py" `
  --processed-dir "U:\EUROMOD-STORAGE\Data\processed\fr\2016" `
  --base-year 2016 `
  --export-format parquet
```

### Step 3: Continuous Opportunity Draws

```powershell
python "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_draws.py" `
  --singles-path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready.parquet" `
  --n-draws 99 `
  --wage-spec vw `
  --couples-path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready.parquet"
```

### Step 4: EUROMOD Simulation

```powershell
python "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_euromod.py" `
  --singles-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready_RURO_draws.parquet" `
  --microdata-template "U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt" `
  --euromod-root "U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+" `
  --euromod-system FR_2015 `
  --euromod-dataset FR_2016 `
  --scenario-dir "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016" `
  --couples-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet"
```

### Step 5: GSUR Preparation

Only run if `Data\external\FR_gsur_ruro.parquet` is missing and `Data\external\FR_gsur.xlsx` exists:

```powershell
python "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_prepare_FR_gsur.py" `
  --input "U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur.xlsx" `
  --output-dir "U:\Desktop\Nizam_Hisham\MNL\Data\external"
```

### Step 6: MNL Dataset Creation

```powershell
python "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_prep_mnl_basic.py" `
  --singles-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready_RURO_draws.parquet" `
  --euromod-combined "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016\combined_draws_em.parquet" `
  --out-base "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl" `
  --wage-spec vw `
  --year 2016 `
  --couples-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet" `
  --gsur-file "U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur_ruro.parquet"
```

### Step 7: Joint Estimation From The Runner

The runner builds a SciPy-style joint estimation command:

```powershell
python "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_estimate_FR.py" `
  --mnl-base "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl" `
  --output-dir "U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\2016" `
  --group joint `
  --method L-BFGS-B `
  --maxiter 5000 `
  --n-jobs <detected CPU cores>
```

If an initial-parameter JSON exists, the runner appends:

```powershell
--init-params "U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\2016\fr_2016_joint.json"
```

### Step 8: Post-Estimation From The Runner

The runner selects the most recent `estimation_results*.json` in `outputs\estimates\fr\2016` and runs:

```powershell
python "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\RURO_post_estimation_styled.py" `
  --results-json "<latest estimation_results*.json>" `
  --mnl-base "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl" `
  --output-dir "U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\2016" `
  --prefix "fr_2016_joint_"
```

## 4. Older `enh_pipeline.ps1` Commands

The older runner covers Steps 1-6 only. Its Step 3 and Step 6 differ from the active runner.

Older Step 3 included explicit draw bounds:

```powershell
python "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_draws.py" `
  --singles-path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready.parquet" `
  --n-draws 99 `
  --wage-spec vw `
  --occ-spec fixed `
  --h-min 10 `
  --h-max 70 `
  --w-min 2 `
  --w-max 170 `
  --rng-seed 17 `
  --couples-path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready.parquet"
```

Older Step 6 wrote a combined MNL file as well:

```powershell
python "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_prep_mnl_basic.py" `
  --singles-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready_RURO_draws.parquet" `
  --euromod-combined "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016\combined_draws_em.parquet" `
  --out-base "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl" `
  --wage-spec vw `
  --year 2016 `
  --write-combined `
  --couples-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet" `
  --gsur-file "U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur_ruro.parquet"
```

## 5. Diagnostics Command

Current diagnostics runner:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\enhanced\run_diagnostics.ps1
```

It runs:

```powershell
python "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\diagnostic_consumption_variation.py" `
  --mnl-base "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl" `
  --household-type both
```

## 6. Manual Estimation And Reporting Commands Found In Archive

These were found in `docs/archive/commands/commands_legacy.txt`.

### Post-estimation report for a GAMSPy run

```powershell
python scripts/enhanced/RURO_post_estimation_styled.py `
  --results-json outputs/estimates/fr/2016_gamspy/run_2026-01-17_19-42-09/estimation_results.json `
  --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
  --output-dir outputs/post_estimation/fr/2016_gamspy_styled `
  --prefix fr_2016_gamspy_ `
  --compute-se
```

### GAMSPy estimation with default enhanced spec and warm start

```powershell
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/MNL/outputs/estimates/fr/2016_gamspy_styled" `
  --group joint `
  --solver gamspy-conopt `
  --spec-config "U:/Desktop/Nizam_Hisham/MNL/scripts/enhanced/estimation_spec.yaml" `
  --warm-start "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/2016_gamspy/run_2026-01-22_15-32-40/estimation_results.json" `
  --auto-timestamp `
  --verbose
```

### Post-estimation report for 2026-01-20 GAMSPy run

```powershell
python .\scripts\enhanced\RURO_post_estimation_styled.py `
  --results-json "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/2016_gamspy/run_2026-01-20_15-30-09/estimation_results.json" `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/post_estimation/fr/2016_gamspy_styled" `
  --prefix "fr_2016_gamspy_" `
  --compute-se `
  --auto-timestamp `
  --verbose
```

### Post-estimation report for ultra-minimal SciPy spec test

```powershell
python .\scripts\enhanced\RURO_post_estimation_styled.py `
  --results-json "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec_tests/4_ultra_minimal_scipy/run_2026-01-24_12-18-20/estimation_results.json" `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/post_estimation/fr/spec_tests/4_ultra_minimal_scipy" `
  --prefix "fr_2016_scipy_" `
  --compute-se `
  --auto-timestamp
```

### GAMSPy incremental v1 enhanced-minimal run

```powershell
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/incremental/v1_enhanced_minimal" `
  --group joint `
  --solver gamspy-conopt `
  --spec-config "U:/Desktop/Nizam_Hisham/MNL/scripts/enhanced/estimation_spec_minimal_theta0.yaml" `
  --warm-start "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/minimal_theta0/2016_gamspy/run_2026-01-23_14-10-01/estimation_results.json" `
  --auto-timestamp
```

### SciPy enhanced-minimal run

```powershell
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/incremental/v1_enhanced_minimal" `
  --group joint `
  --solver scipy `
  --spec-config "scripts/enhanced/estimation_spec_enhanced_minimal.yaml" `
  --warm-start "none" `
  --auto-timestamp `
  --verbose
```

### SciPy spec v2 command with typo in script name

The archived command contains a typo: `enh_RUscRO_estimate_FR.py`. The intended script is almost certainly `enh_RURO_estimate_FR.py`.

```powershell
python scripts/enhanced/enh_RUscRO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/spec_v2" `
  --group joint `
  --solver scipy `
  --method L-BFGS-B `
  --maxiter 2000 `
  --spec-config "scripts/enhanced/estimation_spec_v2.yaml" `
  --warm-start "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/minimal_theta0/2016_gamspy/run_2026-01-23_14-10-01/estimation_results.json" `
  --auto-timestamp
```

## 7. Shell / Report-Opening Commands Found In Archive

These were found in `docs/archive/commands/commands_20260122_143200.txt`.

```powershell
& //crc/users/hisham/Desktop/Nizam_Hisham/MNL/.venv/Scripts/Activate.ps1
```

```powershell
$run = Get-ChildItem -Directory "U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\2016_gamspy_styled" |
  Sort-Object LastWriteTime -Descending | Select-Object -First 1
Start-Process (Get-ChildItem $run.FullName -Filter *.html | Select-Object -First 1).FullName
```

```powershell
New-Item -ItemType Directory -Force "U:\Desktop\Nizam_Hisham\MNL\logs" | Out-Null
Get-History | Select-Object -ExpandProperty CommandLine |
  Set-Content "U:\Desktop\Nizam_Hisham\MNL\logs\commands_$(Get-Date -Format yyyyMMdd_HHmmss).txt"
```
