# Job-Choice RURO Pipeline Walkthrough (FR, Enhanced)

This document explains the full workflow for the **job-choice RURO model** from the first data-prep step to post-estimation reporting.

It is written for someone new to the project: what each script does, what it reads, what it writes, and how stages connect.

---

## 1) Big Picture

You are estimating a sampled-alternative logit where each decision-maker faces:

- one observed baseline alternative (`draw=0`)
- many simulated job alternatives (`draw>0`)
- utility from disposable income/leisure (preference side)
- market-opportunity components (offer side)
- proposal correction (`-log(prior)` / `-log_q_total`) to correct sampled-choice-set bias

Pipeline layers:

1. Build harmonized microdata.
2. Build RURO-ready datasets.
3. Build job universe (grid or GMM latent job types).
4. Draw alternatives per person from the universe.
5. Run EUROMOD on those alternatives.
6. Merge draws + EUROMOD + GSUR into MNL estimation files.
7. Estimate model with YAML spec.
8. Generate post-estimation diagnostics/report.

---

## 2) Script Sequence and Logic

## Step 1: France data preparation

**Script**: `scripts/enhanced/enh_france_data_prep.py`

Purpose:
- Reads raw FR microdata.
- Harmonizes variables used later (ids, demographics, labor variables, household variables).
- Exports processed singles/couples data and metadata sidecars.

Typical outputs (in processed folder):
- `singles_*.parquet`
- `couples_*.parquet`
- `*_meta.json`
- `*__colgroups.json`

Why this matters:
- All later scripts assume consistent naming and core columns.

---

## Step 2: RURO-ready construction

**Script**: `scripts/enhanced/enh_RURO_prep.py`

Purpose:
- Converts step-1 output into RURO-ready person records.
- Adds/standardizes variables used by draws and estimation.
- Creates decider/non-decider logic and keeps required IDs.

Main outputs:
- `singles_RURO_ready.parquet`
- `couples_RURO_ready.parquet`
- sidecar column-group JSONs

Why this matters:
- This is the base input for job universe + draws.

---

## Step 3: Build job universe (job-choice branch)

**Script**: `scripts/Job_model/enh_job_universe.py`

Purpose:
- Defines the set of job alternatives to sample from.
- Assigns posted representative bundles (`hours_rep`, `wage_rep`, `yem_rep`).
- Creates prior weights (`q_j_prior`) used in proposal correction.

Modes:
- `empirical_pruned`, `empirical_all`, `full_grid` (grid-family)
- `gmm_occ` (latent job types within occupation)

Main outputs:
- `job_universe_<year>.parquet`
- `job_universe_<year>__meta.json`
- for GMM mode: `job_universe_<year>__gmm_diagnostics.csv`

Key note:
- `job_id=0` is non-employment and must be present.

---

## Step 4: Draw job alternatives per person

**Script**: `scripts/Job_model/enh_job_draws.py`

Purpose:
- For each decider, creates `draw=0..n_draws`.
- `draw=0` is baseline (observed or posted depending on `--baseline-mode`).
- `draw>0` sampled from `q_j_prior`.
- Adds proposal logs (`log_q_job`, `log_q_state`, `log_q_total`) and `prior`.

Main outputs:
- `singles_RURO_ready_jobdraws.parquet`
- `couples_RURO_ready_jobdraws.parquet`
- corresponding `__drawsmeta.json` files

Why this matters:
- These are the alternatives EUROMOD will evaluate.

---

## Step 5: Run EUROMOD on draws

**Script**: `scripts/enhanced/enh_RURO_euromod.py`

Purpose:
- Injects drawn `hours/wage` into EUROMOD input structure.
- Runs tax-benefit simulation on all alternatives.
- Returns disposable income outputs aligned to each draw row.

Main output:
- `combined_draws_em.parquet`
- sidecar `combined_draws_em__euromodmeta.json`

Why this matters:
- Converts gross bundle alternatives into disposable-income alternatives used by utility.

---

## Step 5b (required once per data build): GSUR lookup prep

**Script**: `scripts/enhanced/enh_prepare_FR_gsur.py`

Purpose:
- Builds unemployment/tightness lookup used as opportunity shifter.

Main output:
- `FR_gsur_ruro.parquet` (plus other variants)

Why this matters:
- Step 6 merges GSUR to create opportunity-side regressors in estimation datasets.

---

## Step 6: Build MNL datasets (post-EUROMOD merge)

**Script**: `scripts/enhanced/enh_RURO_prep_mnl_basic.py`

Purpose:
- Merges job draws with EUROMOD outputs.
- Keeps only decider rows for estimation.
- Builds normalized consumption/leisure terms.
- Reshapes couples to household-level wide format.
- Merges GSUR.
- Applies optional column filtering.

Main outputs (from `--out-base`):
- `<out_base>__singles.parquet`
- `<out_base>__couples.parquet`
- `<out_base>__mnlmeta.json`

Why this matters:
- These are the direct inputs to estimation and post-estimation.

Important:
- Proposal correction variables (e.g., `prior` / `log_prior`) are carried for the estimator.

---

## Step 7: Estimate model

**Script**: `scripts/enhanced/enh_RURO_estimate_FR.py`

Purpose:
- Loads MNL singles/couples data.
- Loads YAML specification (`--spec-config`) defining:
  - preference block
  - opportunity block
  - bounds/initial values/constraints
- Runs joint estimation (typically GAMSPy vectorized).
- Optionally computes numerical-Hessian SEs.

Main outputs (in run folder):
- `estimation_results.json`
- `estimation_results_singles_male.csv`
- `estimation_results_singles_female.csv`
- `estimation_results_couples.csv`
- `estimation_summary.txt`
- `identification_diagnostics.txt`
- `specification_used.yaml`

Why this matters:
- This is where the model parameters are estimated.

---

## Step 8: Post-estimation report

**Script**: `scripts/enhanced/RURO_post_estimation_styled.py`

Purpose:
- Reads `estimation_results.json` + MNL data.
- Recomputes/attaches SEs if requested.
- Produces styled HTML summary tables and diagnostics.
- Shows parameter blocks (including job market opportunity section for job-choice specs).

Main outputs:
- styled HTML report(s) in output run folder
- optional updated JSON/CSV with SEs (depending on flags)

Why this matters:
- Final interpretation layer for coefficients, fit, and diagnostics.

---

## 3) End-to-End Dataflow (What feeds what)

1. `enh_france_data_prep.py` -> processed singles/couples  
2. `enh_RURO_prep.py` -> `*_RURO_ready.parquet`  
3. `enh_job_universe.py` -> job universe + metadata  
4. `enh_job_draws.py` -> `*_jobdraws.parquet`  
5. `enh_RURO_euromod.py` -> `combined_draws_em.parquet`  
6. `enh_prepare_FR_gsur.py` -> `FR_gsur_ruro.parquet`  
7. `enh_RURO_prep_mnl_basic.py` -> `mnl_base__singles/couples.parquet`  
8. `enh_RURO_estimate_FR.py` -> `estimation_results.json` + diagnostics  
9. `RURO_post_estimation_styled.py` -> HTML report

---

## 4) Canonical Command Skeleton (Job-Choice with GMM Universe)

Adjust paths as needed.

```powershell
# Step 1
python scripts/enhanced/enh_france_data_prep.py `
  --input-file "Z:/.../FR_2016.txt" `
  --year 2016 `
  --country fr `
  --output-dir "Z:/.../Data/processed/fr/2016"

# Step 2
python scripts/enhanced/enh_RURO_prep.py `
  --input-dir "Z:/.../Data/processed/fr/2016" `
  --year 2016 `
  --output-dir "Z:/.../Data/processed/fr/2016"

# Step 3 (job universe)
python scripts/Job_model/enh_job_universe.py `
  --singles-path "Z:/.../Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --couples-path "Z:/.../Data/processed/fr/2016/couples_RURO_ready.parquet" `
  --output-dir "Z:/.../Data/processed/fr/2016/job_model_gmm" `
  --year 2016 `
  --universe-mode gmm_occ `
  --gmm-kmax 6 `
  --gmm-min-comp-count 50 `
  --gmm-min-comp-weight 0.03 `
  --job-id-mode deterministic `
  --seed 13

# Step 4 (job draws)
python scripts/Job_model/enh_job_draws.py `
  --singles-path "Z:/.../Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --couples-path "Z:/.../Data/processed/fr/2016/couples_RURO_ready.parquet" `
  --job-universe "Z:/.../Data/processed/fr/2016/job_model_gmm/job_universe_2016.parquet" `
  --job-metadata "Z:/.../Data/processed/fr/2016/job_model_gmm/job_universe_2016__meta.json" `
  --n-draws 199 `
  --baseline-mode posted `
  --seed 13

# Step 5 (EUROMOD)
python scripts/enhanced/enh_RURO_euromod.py `
  --singles-draws "Z:/.../Data/processed/fr/2016/singles_RURO_ready_jobdraws.parquet" `
  --couples-draws "Z:/.../Data/processed/fr/2016/couples_RURO_ready_jobdraws.parquet" `
  --microdata-template "Z:/.../Data/raw/FR_2016.txt" `
  --euromod-system FR_2015 `
  --euromod-dataset FR_2016 `
  --euromod-root "Z:/.../EUROMOD_RELEASES_J1.0+/EUROMOD_RELEASES_J1.0+" `
  --scenario-dir "Z:/.../interim/ruro/fr/2016/job_model_gmm/scenarios"

# Step 5b (GSUR prep; run once if not already available)
python scripts/enhanced/enh_prepare_FR_gsur.py `
  --country fr `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/Data/external"

# Step 6 (MNL prep)
python scripts/enhanced/enh_RURO_prep_mnl_basic.py `
  --singles-draws "Z:/.../Data/processed/fr/2016/singles_RURO_ready_jobdraws.parquet" `
  --couples-draws "Z:/.../Data/processed/fr/2016/couples_RURO_ready_jobdraws.parquet" `
  --euromod-combined "Z:/.../interim/ruro/fr/2016/job_model_gmm/scenarios/combined_draws_em.parquet" `
  --out-base "Z:/.../Data/processed/fr/2016/fr_2016_RURO_mnl_job_gmm" `
  --wage-spec fw `
  --year 2016 `
  --gsur-file "U:/Desktop/Nizam_Hisham/MNL/Data/external/FR_gsur_ruro.parquet"

# Step 7 (estimation)
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "Z:/.../Data/processed/fr/2016/fr_2016_RURO_mnl_job_gmm" `
  --output-dir "U:/.../outputs/estimates/fr/spec/job_choice/gamspy" `
  --group joint `
  --solver gamspy-conopt `
  --vectorized `
  --spec-config "scripts/enhanced/estimation_spec_job_M2c.yaml" `
  --compute-se `
  --auto-timestamp `
  --verbose

# Step 8 (post-estimation)
python scripts/enhanced/RURO_post_estimation_styled.py `
  --results-json "U:/.../outputs/estimates/fr/spec/job_choice/gamspy/run_xxx/estimation_results.json" `
  --mnl-base "Z:/.../Data/processed/fr/2016/fr_2016_RURO_mnl_job_gmm" `
  --output-dir "U:/.../outputs/post_estimation/fr/spec/job_choice/gamspy" `
  --prefix "fr_2016_jobchoice_gmm_gamspy_" `
  --compute-se `
  --spec-config "scripts/enhanced/estimation_spec_job_M2c.yaml" `
  --auto-timestamp
```

---

## 5) Practical Notes for Explaining to Others

- `run_job_ruro_pipeline.py` is a convenience wrapper for Steps 3-5 only (universe, draws, EUROMOD).  
  You still run Steps 6-8 separately for estimation/reporting.

- `--wage-spec fw` in Step 6 is usually chosen because job-choice alternatives already carry explicit wage/hour bundles from universe/draws.

- If you change universe mode (grid vs `gmm_occ`), rerun Steps 3 onward.  
  If you only change YAML specification, rerun Steps 7-8 (not earlier stages).

- If you suspect missing regressors in couples, inspect columns in:
  - `<mnl_base>__singles.parquet`
  - `<mnl_base>__couples.parquet`
  and verify sex-specific suffixes (`*_male`, `*_female`) expected by the spec.

- Identification diagnostics are produced at estimation stage (`identification_diagnostics.txt`), not by post-estimation.

---

## 6) Quick Re-run Point (Your specific need)

If EUROMOD already finished and you need to rerun only from post-EUROMOD:

1. Rerun Step 6 (`enh_RURO_prep_mnl_basic.py`).
2. Rerun Step 7 (`enh_RURO_estimate_FR.py`).
3. Rerun Step 8 (`RURO_post_estimation_styled.py`).

You do **not** need to rerun Steps 1-5 unless upstream inputs changed.

