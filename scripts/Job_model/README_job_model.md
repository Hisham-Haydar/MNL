# Job-Choice RURO Branch

This folder contains the discrete **job-choice RURO** pipeline:

1. build a job universe (`enh_job_universe.py`)
2. generate person-level job draws (`enh_job_draws.py`)
3. run EUROMOD on those draws (`scripts/enhanced/enh_RURO_euromod.py`)

Last validated run: **2026-02-04** (FR 2016, full grid with ISCO0, 199 simulated draws).

---

## What Is Implemented

### 1) Job universe construction
- `--universe-mode`: `empirical_pruned`, `empirical_all`, `full_grid`
- `--rep-fill-mode`: `bin_means`, `bin_midpoints`
- `--hours-rep-stat` and `--wage-rep-stat` when `bin_means`: `mean`, `median`, `mode`
- `--job-id-mode`: `deterministic` (stable IDs) or `sequential`
- `--include-isco0` and `--isco-codes` support

With `full_grid`, total jobs are:
- `n_isco * n_hours_bins * n_wage_bins` working jobs
- plus one non-employment job (`job_id=0`)

Example: ISCO codes `0..9` with 4 hour bins and 10 wage bins gives `400 + 1 = 401` total jobs.

### 2) Draw generation
- Baseline mode:
  - `cell_rep` (default): draw 0 also uses job-cell representative values
  - `observed`: draw 0 uses observed baseline values
- Vectorized simulation for deciders
- Proposal density columns available (`prior`, `log_prior`, `log_q_*`)
- `job_id`, `hours_bin`, `wage_bin`, `isco1` carried with each draw

### 3) EUROMOD compatibility
- Job draws are shaped to be compatible with `enh_RURO_euromod.py`
- Carry-through identifiers/features are preserved for estimation prep

### 4) Step 6 integration (`enh_RURO_prep_mnl_basic.py`)
- Job-model priors are now used automatically when available:
  - singles: `log_q_total`
  - couples: `log_q_total_male + log_q_total_female`
- Job columns are kept in the essential column set (after filtering)
- Couples reshape remains strict with sanity checks
- GSUR merge supports age-group matching and full-age fallback

---

## Recommended End-to-End Command

```powershell
python scripts/Job_model/run_job_ruro_pipeline.py `
  --singles-path "U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --couples-path "U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready.parquet" `
  --microdata-template "U:/EUROMOD-STORAGE/Data/raw/FR_2016.txt" `
  --year 2016 `
  --universe-mode full_grid `
  --rep-fill-mode bin_means `
  --hours-rep-stat mode `
  --wage-rep-stat median `
  --job-id-mode deterministic `
  --baseline-mode cell_rep `
  --n-draws 199 `
  --include-isco0 `
  --euromod-system FR_2015 `
  --euromod-dataset FR_2016 `
  --euromod-root "U:/EUROMOD-STORAGE/EUROMOD_RELEASES_J1.0+/EUROMOD_RELEASES_J1.0+" `
  --scenario-dir "U:/EUROMOD-STORAGE/interim/ruro/fr/2016/job_model/scenarios" `
  --seed 13
```

---

## Outputs

### Universe step
- `job_universe_{year}.parquet`
- `job_universe_{year}__meta.json`

### Draw step
- `singles_RURO_ready_jobdraws.parquet`
- `couples_RURO_ready_jobdraws.parquet`
- `*_jobdraws__drawsmeta.json`

### EUROMOD step
- `combined_draws_em.parquet` in scenario directory

### Step 6 (MNL prep) from job draws
Suggested command:

```powershell
python scripts/enhanced/enh_RURO_prep_mnl_basic.py `
  --singles-draws "U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_jobdraws.parquet" `
  --couples-draws "U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_jobdraws.parquet" `
  --euromod-combined "U:/EUROMOD-STORAGE/interim/ruro/fr/2016/job_model/scenarios/combined_draws_em.parquet" `
  --out-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_job" `
  --wage-spec fw `
  --year 2016 `
  --gsur-file "U:/Desktop/Nizam_Hisham/MNL/Data/external/FR_gsur_ruro.parquet"
```

### Step 7 (new): Job-choice preference estimation
Use the regular estimator entrypoint with the job-ready MNL base and the job-choice spec:

```powershell
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_job" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/job_choice/gamspy" `
  --group joint `
  --solver gamspy-conopt `
  --vectorized `
  --spec-config "U:/Desktop/Nizam_Hisham/MNL/scripts/enhanced/estimation_spec_job_choice_v1.yaml" `
  --warm-start "none" `
  --auto-timestamp `
  --verbose
```

Notes:
- `market_opportunity.shifters` in the spec are now parsed and estimated in vectorized GAMSPy.
- Job fields (`job_id`, `hours_bin`, `wage_bin`, `isco1`) are preserved in filtered MNL outputs.
- For clean preference/opportunity separation, keep labor-demand shifters in `market_opportunity` only.

### Step 8 (new): Job-choice post-estimation report
Use the same styled report script; it now renders model-aware metadata for job-choice runs.

```powershell
python scripts/enhanced/RURO_post_estimation_styled.py `
  --results-json "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/job_choice/gamspy/run_xxx/estimation_results.json" `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_job" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/post_estimation/fr/spec/job_choice/gamspy" `
  --prefix "fr_2016_jobchoice_gamspy_" `
  --compute-se `
  --spec-config "scripts/enhanced/estimation_spec_job_choice_v0_plus_b.yaml" `
  --auto-timestamp
```

Report additions for job-choice runs:
- Estimation configuration block (spec, model family, opportunity tier, proposal correction, centering)
- Embedded `identification_diagnostics.txt` (if produced at estimation step)
- Opportunity parameter table and job/LOC fit plots when those columns are present

---

## Expected Logs and Interpretation

- `Baseline job assignment used fallback ...`  
  Normal for some rows when exact observed baseline cell is unavailable.

- `GSUR merge (...): filled ... using fallback age_group=Y20-64`  
  Expected if GSUR file only contains full-age bracket rows.

- `rows have ils_dispy=0` warning in EUROMOD step  
  Not automatically fatal; inspect composition by draw/group before deciding.

---

## Known Scope and Limits

- Discrete job offers are currently based on `(hours_bin, wage_bin, isco1)`.
- Couples draws are independent across partners at draw generation stage.
- Downstream utility/estimation specification is still controlled in `scripts/enhanced`.

---

## Related Docs

- `scripts/Job_model/ACCEPTANCE_TESTS.md`
- `scripts/enhanced/README.md`
- `DONE.md`
- `TODO.md`
