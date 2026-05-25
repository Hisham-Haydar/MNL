# FR 2016 RURO Pipeline – Function-Level Execution Narrative

## 0. Document Meta

- **Repository commit / timestamp:** `[unknown]` (local working tree snapshot as of 2025-12-14).  
- **Machine assumptions:** Windows 11 workstation, PowerShell shell, Python 3.11 environment reachable via the `python` launcher, EUROMOD installed on a mapped `U:/` share.  
- **Logging & outputs:**  
  - Primary run log: `outputs/logs/fr_2016_joint_only_<timestamp>.md`.  
  - Intermediate datasets: `Data/processed/fr/2016/...` on the shared storage resolved by `path_helpers`.  
  - Estimation outputs: `outputs/estimates/fr/2016/`.  
  - Post-estimation HTML/plots: same `outputs/estimates/...` directory.  
  - Legacy post-est artifacts (if re-enabled): `outputs/post_estimation/fr/2016/`.

---

## 1. End-to-End Overview

### 1.1 RURO within this codebase

The Random Utility–Random Opportunity (RURO) model here unifies a discrete-choice labour supply model with a stochastic opportunity generator. Individuals (single males, single females, and couples) evaluate a finite set of job offers that are partly observed (actual employment) and partly simulated (draws). Utility combines Box–Cox-transformed leisure and consumption, shifted by demographic covariates (age, education, children), and subtracts the log proposal density so the estimated likelihood reflects the structural opportunity density rather than the simulation proposal. Hours and wage opportunities follow parametric densities with their own coefficients (`HoursOppParams`, `WageOppParams`), meaning estimation simultaneously fits preferences and opportunity distributions.

### 1.2 High-level pipeline dataflow

```
raw EU-SILC/EUROMOD text
        │
        ▼
france_data_prep.py  ──►  Data/processed/fr/2016/fr_2016_[singles|couples].parquet
        │
        ▼
RURO_prep.py         ──►  *_RURO_ready.parquet (adds RURO covariates)
        │
        ▼
RURO_draws.py        ──►  *_RURO_ready_RURO_draws.parquet (observed + simulated offers)
        │
        ▼
RURO_euromod.py      ──►  outputs/estimates/fr/2016/combined_draws_em.parquet
        │
        ├── prepare_FR_gsur.py  ──► Data/external/FR_gsur_ruro.parquet
        │
        ▼
RURO_prep_mnl_basic.py ──► Data/processed/fr/2016/fr_2016_RURO_mnl.parquet
        │
        ▼
RURO_estimate_FR.py  ──► outputs/estimates/fr/2016/fr_2016_joint.json
        │
        ▼
RURO_post_estimation.py ──► outputs/estimates/fr/2016/vw_joint_post_estimation_report.html + PNGs
```

### 1.3 Main artifacts per stage

| Stage | Producer script | Outputs | Notes |
| --- | --- | --- | --- |
| Data prep | `france_data_prep.py` | Cleaned singles/couples Parquet files | Contains harmonized IDs, hours, wages, benefits |
| RURO covariates | `RURO_prep.py` | `singles_RURO_ready.parquet`, `couples_RURO_ready.parquet` | Adds experience, education, region dummies, RURO flags |
| Opportunity draws | `RURO_draws.py` | `*_RURO_ready_RURO_draws.parquet` | Observed draw plus `N_DRAWS` simulated offers |
| EUROMOD | `RURO_euromod.py` | `combined_draws_em.parquet` | Disposable income per individual/draw |
| GSUR | `prepare_FR_gsur.py` | `FR_gsur_ruro.parquet` | Group-specific unemployment rates |
| MNL prep | `RURO_prep_mnl_basic.py` | `fr_2016_RURO_mnl.parquet` | Long dataset with normalized consumption/leisure, priors |
| Estimation | `RURO_estimate_FR.py` | `fr_2016_joint.json`, log outputs | Joint parameters, gradients, metadata |
| Post-estimation | `RURO_post_estimation.py` | HTML, PNGs, optional CSV | Diagnostics, fit comparisons, marginal utilities |

---

## 2. Entrypoint: `run_fr_2016_joint_only.ps1`

### 2.1 Execution order (mapped directly from the script)

1. **Environment preparation**
   - Set variables: `$YEAR=2016`, `$SYSTEM_YEAR=2015`, `$N_DRAWS=99`, `$WAGE_SPEC="vw"`, etc.
   - Resolve directories for scripts, data, EUROMOD, GSUR lookup, outputs.
   - Configure threading env vars (`OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `NUMEXPR_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `NUMBA_NUM_THREADS`) based on detected logical cores.
   - Raise log header at `outputs/logs/fr_2016_joint_only_<timestamp>.md`.

2. **Pre-flight checks**
   - Verify raw microdata (`$RAW`) and EUROMOD installation exist.
   - Log configuration summary and create directories.

3. **Conditional data regeneration**
   - If `$SKIP_IF_MNL_EXISTS` is false (default), run Steps 1–6 below; else skip straight to estimation if `fr_2016_RURO_mnl.parquet` already exists.

4. **Step 1 – Data preparation**
   - Command:  
     ```powershell
     python "$SCRIPTS\france_data_prep.py" --year 2016 --raw-dir "U:\EUROMOD-STORAGE\Data\raw" --out-dir "$PROC" --system-year 2015 --export-format parquet
     ```
   - Produces cleaned singles/couples base files.

5. **Step 2 – RURO preparation**
   - Command:  
     ```powershell
     python "$SCRIPTS\RURO_prep.py" --processed-dir "$PROC" --base-year 2016 --export-format parquet
     ```
   - Adds RURO-specific regressors and writes `*_RURO_ready.parquet`.

6. **Step 3 – Generate draws**
   - Command (couples optional append if file exists):  
     ```powershell
     python "$SCRIPTS\RURO_draws.py" --singles-path "$SINGLES_RURO" --n-draws 99 --wage-spec vw --couples-path "$COUPLES_RURO"
     ```
   - Generates prior-weighted long draw files.

7. **Step 4 – EUROMOD simulation**
   - Command:  
     ```powershell
     python "$SCRIPTS\RURO_euromod.py" --singles-draws "$SINGLES_DRAWS" --microdata-template "$RAW" --euromod-root "$EUROMOD_ROOT" --euromod-system FR_2015 --euromod-dataset FR_2016 --scenario-dir "$SCEN" --couples-draws "$COUPLES_DRAWS"
     ```
   - Produces EUROMOD outputs for each draw.

8. **Step 5 – Prepare GSUR**
   - If `FR_gsur_ruro.parquet` missing, run:  
     ```powershell
     python "$SCRIPTS\prepare_FR_gsur.py" --input "$PROJ_ROOT\Data\external\FR_gsur.xlsx" --output-dir "$PROJ_ROOT\Data\external"
     ```
   - Otherwise skip (file already present).

9. **Step 6 – Build MNL dataset**
   - Command:  
     ```powershell
     python "$SCRIPTS\RURO_prep_mnl_basic.py" --singles-draws "$SINGLES_DRAWS" --euromod-combined "$EM_COMBINED" --out-base "$MNL_BASE" --wage-spec vw --year 2016 --skip-csv --couples-draws "$COUPLES_DRAWS" --gsur-file "$GSUR_FILE"
     ```
   - Writes `fr_2016_RURO_mnl.parquet`.

10. **Step 7 – Joint estimation + post-estimation**
    - Command:  
      ```powershell
      python "$SCRIPTS\RURO_estimate_FR.py" --mnl-file "$MNL_FILE" --joint --wage-spec vw --optimizer L-BFGS-B --maxiter 2000 --use-numba --n-jobs <cores> --post-estimation --out-file "$EST_FILE" --init-params "$INIT_PARAMS_JOINT"
      ```
    - Emits JSON results, triggers `RURO_post_estimation.py` automatically because `--post-estimation` is set.

11. **Summary**
    - Writes successful completion notice with references to output files and runtime.

### 2.2 Failure propagation

Each `Run-PythonScript` call captures stdout/stderr, logs the command, and halts the pipeline with `exit 1` if the exit code is non-zero. Therefore, any downstream step is not attempted if upstream fails, guaranteeing sequential integrity.

---

## 3. Stage A — Data Ingestion and Preparation

### 3.1 Script: `france_data_prep.py`

**Responsibility:** Transform raw EU-SILC/EUROMOD data into cleaned singles/couples Parquet files with harmonized IDs, hours, wages, incomes, and RURO eligibility flags. Pulls helper paths from `path_helpers` (`data_root`, `euromod_root`, `ensure_dir`) with fallback inline implementations, so path resolution is part of the script contract.

#### 3.1.1 `setup_logging(level: str = "INFO")`

- **Called from:** `main()` at startup.
- **Purpose:** Configure Python logging (console + optional file) so each subsequent function logs filtering results.
- **Inputs:** Logging level string; uses module-level `logging` and optionally `scratch.my_functions.setup_logging` if available.
- **Operations (step-by-step):**
  1. Attempt `from scratch.my_functions import setup_logging`; if unavailable, default to `logging.basicConfig`.
  2. Set format to include timestamp, level, module.
  3. Attach stream handler only once (avoids duplicated logs).
- **Outputs:** Global logger configured.
- **Assumptions & invariants:** Logging callable is idempotent.  
- **Common bugs & diagnostics:** Missing `scratch` module triggers INFO log about fallback but is not fatal.
- **Downstream consumer:** Every function emits messages for reproducibility.

#### 3.1.2 `validate_household_integrity(df: pd.DataFrame) -> bool`

- **Called from:** `prepare_one_year` after filters.
- **Purpose:** Ensure each household retains at least one head/partner entry and unique `idperson`.
- **Inputs:** DataFrame with `idhh`, `hh_IsHead`, `hh_IsPartner`.
- **Operations:**
  1. Group by `idhh` counting rows where `hh_IsHead` or `hh_IsPartner` equals 1.
  2. Confirm counts ≥1; collect offenders.
  3. Check for duplicate `idperson`.
- **Outputs:** Boolean flag; logs detail.
- **Assumptions:** ID columns typed as integers.
- **Common bugs:** If earlier renaming failed, `KeyError` surfaces here.
- **Downstream consumer:** Guard before writing singles/couples; failing returns False, prompting `prepare_one_year` to raise.

#### 3.1.3 `check_data_quality(df: pd.DataFrame) -> List[str]`

- **Purpose:** Summarize anomalies (negative wages, hours > 80, etc.).
- **Inputs:** DataFrame with `yem`, `lhw`.
- **Operations:**
  1. Compute share of zero/negative wages.
  2. Inspect distribution tails for hours/wages.
  3. Return list of warnings for log.
- **Outputs:** List of warning strings.
- **Common bugs:** None; used for human review.
- **Downstream consumer:** `prepare_one_year` prints warnings at end.

#### 3.1.4 `create_income_columns(df)`

- **Purpose:** Build RURO-friendly income fields.
- **Inputs:** EUROMOD-coded columns (`yem`, benefit codes, taxes).
- **Operations:**
  1. Sum benefit variables to `benefits_total`.
  2. Compute `labour_income = yem - taxes`.
  3. Derive `other_members_income` per household by subtracting decider contributions.
  4. Normalize to monthly using `WEEKS_PER_MONTH`.
- **Outputs:** DataFrame with new columns.
- **Assumptions:** Monetary columns numeric; missing data filled with 0.
- **Failure modes:** NaNs propagate if EUROMOD data missing; function logs top offending IDs.
- **Downstream consumer:** RURO consumption uses these columns.

#### 3.1.5 `correct_labor_status(df, config=None)`

- **Purpose:** Harmonize labour status for RURO.
- **Inputs:** DataFrame, optional config specifying valid codes.
- **Operations:**
  1. Map `les` codes into {employed, unemployed, inactive}.
  2. Force `lma=1` for positive observed hours.
  3. For missing statuses, infer from `yem` or benefit receipt.
- **Outputs:** Updated `lma`, `ruro_decider`.
- **Assumptions:** `les` column exists; fallback uses heuristics.
- **Common bugs:** Unexpected codes -> warning plus fallback to inactive.
- **Downstream consumer:** RURO draws rely on accurate `lma` for priors.

#### 3.1.6 `compute_wage_recon(df)`

- **Purpose:** Recreate consistent hourly wages.
- **Inputs:** `yem`, `lhw`, `yemmy`, etc.
- **Operations:**
  1. Convert incomes to monthly (if provided annually).
  2. Compute `wage_em = yem / hours`; clip to `[0, 120]`.
  3. Apply smoothing/log to produce `wage_ruro`.
  4. Fill zero hours with NaN to avoid division by zero.
- **Outputs:** Additional wage columns.
- **Failure modes:** Negative hours -> flagged.
- **Downstream consumer:** RURO_prep_mnl_basic uses `wage` for priors and wage opportunities.

#### 3.1.7 `identify_extreme_households(df, config)`

- **Purpose:** Flag unrealistic households (hours > 80, wages > threshold).
- **Operations:** Create boolean mask; return indices for dropping.
- **Downstream:** `stepwise_filter_households`.

#### 3.1.8 `log_filtering_step(step_name, before, after)`

- Logging helper; ensures each filter step recorded.

#### 3.1.9 `apply_other_members_filter(df, config)`

- **Purpose:** Ensure `other_members_income` defined.
- **Operations:** Drop households lacking non-decider entries or impute zeros per config.
- **Downstream:** Cleaned dataset for RURO_prep.

#### 3.1.10 `stepwise_filter_households(df, config)`

- **Purpose:** Apply all filters sequentially.
- **Operations:**  
  1. Drop extremes (`identify_extreme_households`).  
  2. Enforce decider counts.  
  3. Apply other-members filter.  
  4. Reset index.
- **Failure modes:** Overly strict config -> empty dataset; function raises.

#### 3.1.11 `_write_dataframe(df, base_path, export_format)`

- Writes DataFrame to disk (Parquet by default).  
- Downstream: `export_household_data`.

#### 3.1.12 `export_household_data(df, out_dir, export_format)`

- **Purpose:** Separate singles/couples and write.
- **Operations:**  
  1. `separate_household_types`.  
  2. `_write_dataframe` per subset.  
  3. Return dict with file paths.

#### 3.1.13 `_plot_distribution`, `_generate_group_plots`

- Optional QA plots (histograms of hours/wages).  
- Failure handled gracefully.

#### 3.1.14 `load_fr_txt(raw_path)`

- Reads raw EUROMOD/EU-SILC text into DataFrame.  
- Failure -> pipeline stops before Step 1 completes.

#### 3.1.15 `clean_harmonize_fr(df)`

- **Purpose:** Rename columns, enforce dtypes, create decider flags.
- **Operations:**  
  1. Rename EU-SILC variable codes to descriptive names (dag, deh, etc.).  
  2. Cast IDs to integers, fill missing `dag` using household averages.  
  3. Build `hh_IsHead`, `hh_IsPartner`, `is_child`.

#### 3.1.16 `separate_household_types(df)`

- Splits dataset into singles vs couples using `ruro_group` and `idhh`.

#### 3.1.17 `filter_singles_by_gender(df, gender)`

- Optional debug helper; not used in default run.

#### 3.1.18 `prepare_one_year(...)`

- **Purpose:** Compose steps above for a single year.
- **Inputs:** CLI args (year, raw dir, out dir, system year).
- **Operations:** `load_fr_txt → clean_harmonize_fr → create_income_columns → correct_labor_status → stepwise_filter_households → export_household_data`. Logs QA warnings, ensures integrity.
- **Outputs:** Dict of file paths.

#### 3.1.19 `main()`

- CLI entry; calls `setup_logging`, `prepare_one_year`.

### 3.2 Script: `RURO_prep.py`

**Responsibility:** Consume singles/couples files from Stage 3.1, augment them with RURO-specific covariates (experience, education dummies, hours categories, GSUR placeholders), and write `_RURO_ready` files.

#### 3.2.1 `_maybe_add_column(df, name, values)`

- Adds column only if absent (prevents overwriting user-supplied data).
- Failure: mismatched length → ValueError.

#### 3.2.2 `_resolve_processed_dir(processed_dir, base_year)`

- Resolves working directory by checking CLI override or falling back to `path_helpers.data_root()/processed/fr/<year>`.
- Failure: Directory exists but missing required files -> FileNotFoundError.

#### 3.2.3 `_load_filtered_data(processed_dir)`

- Reads singles/couples Parquet; logs shapes; ensures required columns exist.

#### 3.2.4 `_infer_year_series(df, default_year)`

- Supplies `year` column (existing or default) for later merges.

#### 3.2.5 `_enforce_loc_for_nonworkers(df)`

- Sets `loc=-1` for nonworkers to avoid EUROMOD rejects.

#### 3.2.6 `_add_france_nuts1_region_dummies(df)`

- Uses `scripts/Drd_vars.txt` to map `drgn2` to coarse `reg2` / `reg3` dummies. Leaves NaN if mapping missing; warns analysts to repair mapping file rather than force to base region.

#### 3.2.7 `_add_ruro_variables_basic(df, base_year)`

- **Steps:**
  1. Determine year per record via `_infer_year_series`.
  2. Build `pexp_years`, `pexp_years2` from age minus education length.
  3. Create education dummies (`educL`, `educH`, residual `educM`).
  4. Mark `working_pt1`, `working_pt2`, `working_ft` based on hours thresholds (1–20, 21–30, ≥35).
  5. Generate RURO IDs (`ruro_group`, `ruro_sample`), `pi0_m/f` priors, `other_members_income`.
  6. Apply `_enforce_loc_for_nonworkers` and `_add_france_nuts1_region_dummies`.

#### 3.2.8 `_prepare_ruro_basic(...)`

- Calls `_load_filtered_data`, runs `_add_ruro_variables_basic` for singles and couples, ensures directories exist, writes `_RURO_ready` Parquet files.

#### 3.2.9 `_cli_ruro_prep_basic()` / `main()`

- CLI entry hooking args to `_prepare_ruro_basic`.

### 3.3 Script: `prepare_FR_gsur.py`

**Responsibility:** Build GSUR (group-specific unemployment rate) lookup table.

#### 3.3.1 `parse_sheet_metadata(df)`

- Extracts metadata (region code, gender, etc.) from Excel sheet headers.

#### 3.3.2 `parse_sheet_data(df)`

- Melts data rows into long format with `year`, `value`, and metadata columns.

#### 3.3.3 `process_all_sheets(xlsx_path)`

- Iterates over workbook sheets, calling the two parsers, concatenates results.

#### 3.3.4 `create_simplified_gsur(full_df)`

- Maps fine region codes to `reg2/3`, standardizes gender codes, renames `value` → `gsur`.

#### 3.3.5 `create_ruro_gsur_lookup(full_df)`

- Group-by region, gender, year to compute final GSUR values; writes Parquet.

#### 3.3.6 `main()`

- CLI entry; ensures output directory exists, runs pipeline.

### 3.4 Script: `RURO_prep_mnl_basic.py`

**Responsibility:** Combine RURO draws and EUROMOD outputs, normalize consumption/leisure, append GSUR, create new regressors (`age_norm`, `age_norm2`, `n_children`), compute priors, and write MNL-ready dataset.

#### 3.4.1 `_read_df(path)`

- Reads Parquet/CSV/Pickle; ensures DataFrame.

#### 3.4.2 `_write_df(df, base)`

- Writes Parquet (CSV optional); returns dict with final paths.

#### 3.4.3 `_merge_euromod_outputs(long_df, em_df)`

- Merges RURO draws with EUROMOD results on `(idperson, draw)` ensuring `ils_dispy` present; replaces `idhh` with EUROMOD’s `idhh_true`.

#### 3.4.4 `_restrict_to_deciders(df)`

- Drops non-deciders using priority rule: head/partner flags → `ruro_decider` → `lma`. Logs how many rows removed.

#### 3.4.5 `_build_mnl_block(df, sample_group)`

- Computes `hours`, `leisure` (80 – hours), `consumption` (including other members), log transforms, education dummies, adds `sample_group`.

#### 3.4.6 `_build_loc_distribution(df)`

- Optional; calculates empirical occupation distribution for debugging priors.

#### 3.4.7 `_compute_prior(...)`

- Implements RURO prior: zero-hour mass (`pi0_m/f`) plus uniform densities over hours/wages (bounded by CLI options). Stores `log_prior`.

#### 3.4.8 `parse_args()` / `main()`

- Steps:  
  1. Read singles/couples draws, EUROMOD combined file, GSUR file.  
  2. Merge EUROMOD results, restrict to deciders.  
  3. Build MNL blocks (consumption/leisure).  
  4. Vectorized creation of `age_norm = dag - mean(dag)`, `age_norm2`, `n_children` (sum of `ch0_3`, `ch4_6`, `ch7_9`), including `_m/_f` for couples.  
  5. Merge GSUR by region/gender/year (or skip if `--no-gsur`).  
  6. Compute priors, ensure required columns, write output.

---

## 4. Stage B — RURO Draws / Choice-Set Construction

### 4.1 Script: `RURO_draws.py`

**Responsibility:** For every RURO-ready decider, generate `n_draws` synthetic opportunities (hours/wages) plus the observed draw, compute proposal densities (priors), and store in long format.

#### 4.1.1 `_collect_candidates()`, `_resolve_storage_root()`, `_euromod_root()`

- **Called from:** Top-level when resolving default paths.
- **Purpose:** Locate shared storage/EUROMOD installations by scanning environment hints and standard directories.
- **Inputs:** None (reads env vars like `MNL_STORAGE_ROOT`, `MNL_EUROMOD_ROOT`).
- **Outputs:** Path objects for later CLI defaults.
- **Assumptions:** At least one candidate contains `Data` or EUROMOD release tree.
- **Common bugs:** Running offline without mapped `U:/` leads to `FileNotFoundError`; fix by setting env var.
- **Downstream consumer:** CLI defaults when user omits explicit paths.

#### 4.1.2 `_read_microdata_file(path)`

- Reads baseline microdata if needed for verifying column presence; similar to `_read_df`.

#### 4.1.3 `_read_dataframe(path)`

- Shared helper; returns DataFrame and logs shape.

#### 4.1.4 `_write_dataframe(df, base_path, suffix="_draws")`

- Writes draws DataFrame to Parquet; returns dict of output paths for singles/couples.

#### 4.1.5 `_attach_other_members_income(df)`

- Ensures `other_members_income` column exists and is numeric; fills missing with 0.0 to prevent NaNs when computing consumption later.

#### 4.1.6 `_build_loc_distribution(df)`

- Computes empirical distribution of `loc` for working deciders; used for sampling when simulated draws require a plausible occupation.

#### 4.1.7 `_sample_loc`, `_draw_loc`

- Accept a probability dictionary and RNG, draw an occupation code; fallback to observed `loc` or -1 if distribution absent.

#### 4.1.8 `generate_draws_long(df, n_draws, wage_spec, rng_seed, ...)`

- **Called from:** `main()` separately for singles and couples.
- **Purpose:** Core routine building the long dataset.
- **Inputs:**  
  - DataFrame with RURO covariates.  
  - `n_draws` (99).  
  - Wage spec ("vw" = varying wages).  
  - RNG seeds, hours/wage bounds, pi0 parameters.
- **Operations (step-by-step):**
  1. Initialize RNG (`np.random.default_rng(rng_seed)`); shuffle row order to avoid patterns.
  2. For each decider, copy observed row as `draw=0`, `is_chosen=1`.
  3. Loop vectorized: generate `n_draws` arrays of random hours uniform on `[h_min, h_max]`. Optionally enforce focal point probabilities by replacing draws near 20/30/40 hours.
  4. For zero-hours alternatives, set `wage=0`, `loc=-1`, record zero-hour prior mass.
  5. For variable wages, sample uniformly on `[w_min, w_max]`; for fixed wages, reuse observed wage.
  6. Copy static covariates (education, region, GSUR) to every draw.
  7. Compute priors:  
     - `prior_hours = log(1 / (h_max - h_min))` for working draws; zero-hours use `log(pi0_gender)`.  
     - `prior_wage` analogous when `wage_spec="vw"`.  
     - Combine to `log_prior = prior_hours + prior_wage`.
  8. Concatenate observed + simulated rows, sort by `idperson`, assign sequential `draw`.
- **Outputs:** DataFrame with columns `idperson`, `idhh`, `draw`, `hours`, `wage`, `loc`, `is_chosen`, `ruro_group`, `other_members_income`, `log_prior`, `pi0`.
- **Assumptions:** Hours bounds >0; `n_draws` positive.
- **Failure modes:** If input lacks `pi0_m/f`, priors default to 0.1; missing `ruro_group` results in ValueError.
- **Downstream consumer:** EUROMOD simulation and MNL prep.

#### 4.1.9 `parse_args()` / `main()`

- **Operations:**  
  1. Parse CLI options (paths, draws, wage spec, RNG seeds).  
  2. Read singles/couples RURO-ready data.  
  3. `_attach_other_members_income`.  
  4. Run `generate_draws_long` for each cohort, write outputs, log summary stats (per-group counts, mean hours).
- **Failure modes:** Missing input files, invalid `n_draws`.

---

## 5. Stage C — EUROMOD Run & Counterfactual Income Construction

### 5.1 Script: `RURO_euromod.py`

**Responsibility:** Expand households for each draw, run EUROMOD to recalculate disposable income/taxes/benefits, and merge results back with draw identifiers.

#### 5.1.1 `_collect_candidates`, `_resolve_storage_root`, `_euromod_root`

- Same purpose as in the draws script: locate data storage and EUROMOD release directories.

#### 5.1.2 `_read_microdata_file(path)`

- Reads baseline microdata template used to attach non-deciders to each draw.

#### 5.1.3 `EUROMODRunner.__init__(root)`

- Validates EUROMOD installation path, stores references for command-line invocation.

#### 5.1.4 `EUROMODRunner._resolve_system(country, system_code, dataset_name)`

- Constructs scenario path `<root>/<country>/<system>/<dataset>`; ensures necessary XML/config files exist.

#### 5.1.5 `EUROMODRunner.run_on_dataframe(df, *, country, system_code, dataset_name)`

- **Purpose:** Write EUROMOD input file, execute EUROMOD in batch, parse outputs.
- **Operations:**  
  1. Dump DataFrame to CSV/TSV format expected by EUROMOD.  
  2. Prepare command-line invocation referencing scenario.  
  3. Run process with captured stdout/stderr; convert non-zero exit to `RuntimeError`.  
  4. Read EUROMOD output file (per-person results) back into pandas.
- **Outputs:** DataFrame with `ils_dispy`, `taxes`, `benefits`, `idhh_true`, `idperson_true`, etc.
- **Failure modes:** EUROMOD license errors, missing dataset definitions. Logged along with command for reproduction.

#### 5.1.6 `_read_dataframe(path)`

- Helper to load draws files.

#### 5.1.7 `_prepare_euromod_dataset(draws_df, microdata_template)`

- **Purpose:** Expand base microdata so EUROMOD can evaluate each draw.
- **Operations:**  
  1. Merge draws with baseline microdata using `idperson`.  
  2. For non-deciders, replicate rows for each draw belonging to their household (ensures taxes consider other members).  
  3. For deciders, overwrite hours (`lhw`), wages, months worked (`yemmy`, `lunmy`), unemployment benefits (set to zero if working).  
  4. Assign new household ID: `idhh = idhh_true * 1000 + draw`.  
  5. Keep `draw` column for merging outputs later.
- **Outputs:** Expanded DataFrame ready for EUROMODRunner.
- **Failure modes:** Households missing non-deciders -> warnings; rows dropped if merge fails.

#### 5.1.8 `run_euromod_for_draws(...)`

- **Purpose:** Orchestrate EUROMOD run for singles and couples draws.
- **Operations:**  
  1. Read draws file(s).  
  2. Call `_prepare_euromod_dataset`.  
  3. Create scenario directory if needed.  
  4. Run EUROMOD via `EUROMODRunner`.  
  5. Merge EUROMOD outputs with draws via `(idperson_true, draw)`.  
  6. Write `combined_draws_em.parquet`.
- **Failure modes:** Mismatch between `idperson` and EUROMOD IDs → ValueError.
- **Downstream consumer:** `RURO_prep_mnl_basic.py`.

#### 5.1.9 `parse_args()` / `main()`

- Parses CLI arguments, configures scenario directories, runs `run_euromod_for_draws`.

---

## 6. Stage D — Estimation (`RURO_estimate_FR.py`)

### 6.1 Model definition

- **Utility (singles):**
  \[
  U_{ij} = (\beta_{l0} + \beta_{l,age} \cdot age\_norm_{ij} + \beta_{l,age2} \cdot age\_norm2_{ij} + \beta_{l,nch} \cdot n\_children_{ij} + \beta_{l,educL} \cdot educL_i + \beta_{l,educH} \cdot educH_i) \cdot BC(l_{ij}; \theta_l) + \beta_c \cdot BC(c_{ij}; \theta_c) + \log h(h_{ij}; \psi_h) + \log w(w_{ij}; \psi_w) - \log prior_{ij}
  \]
- **Couples:** Add male and female leisure blocks (own parameters) and a shared consumption function with `beta_c` and `theta_c`.
- **Opportunity terms:** Hours density parameters determine relative mass at zero hours, part-time focal points, and full-time work; wage density follows log-normal with mean determined by education and potential experience, plus region/year dummies.

### 6.2 Parameter blocks & constraints

| Block | Parameters (vw spec) | Notes |
| --- | --- | --- |
| Single male prefs | 9 | intercept, age_norm, age_norm2, n_children, educL, educH, `beta_c`, `theta_l`, `theta_c` |
| Single female prefs | 9 | same structure |
| Couples prefs | 16 | male+female leisure (6 each) + shared Box–Cox exponents/consumption (4) |
| Hours opp male | 7 | `beta_work`, `beta_pt1`, `beta_pt2`, `beta_ft`, `beta_gsur`, `beta_work_educL`, `beta_work_educH` (reg dummies removed in simplified spec) |
| Hours opp female | 7 | analogous |
| Wage opp male | 6 | intercept, educ dummies, pexp, pexp², sigma |
| Wage opp female | 6 | same |

Box–Cox exponents constrained positive via `theta = 0.01 + softplus(raw)` (current code uses direct values but clipped). Wage sigma enforced positive: `sigma = abs(raw_sigma) + 1e-6`.

### 6.3 Likelihood construction

1. Load `fr_2016_RURO_mnl.parquet`, split into single male/female and couples groups.
2. `precompute_data_*` converts pandas columns into contiguous NumPy arrays and records per-person draw boundaries.
3. For each θ vector, compute deterministic utilities \(V_{ij}\) = preference component + hours opportunity log density + wage opportunity log density – `log_prior`.
4. Compute logit probabilities using log-sum-exp per person; LL equals sum of log probabilities for observed draws.
5. Analytic gradients derived via expectation of derivatives minus derivative at chosen alternative.
6. Joint LL is sum over groups; gradients mapped into shared θ layout.

### 6.4 Optimizer

- `scipy.optimize.minimize(method="L-BFGS-B", jac=True)` with `maxiter` from CLI.
- Optional Numba acceleration for gradient aggregator loops (`--use-numba`).
- `--validate-gradient` (debug) compares analytic and numerical gradients for sanity.

### 6.5 Numerical stability

- Box–Cox inputs clipped at 1e-6 before transforming.
- Wage sigma uses epsilon to avoid divide-by-zero.
- Softmax computed via log-sum-exp to avoid overflow.
- `log_prior` ensures importance sampling correction is inside utility, preventing subtraction on probability scale.
- Bounded parameter initialization prevents exploring extreme values initially.

### 6.6 Function Execution Trace (key functions)

Given the file’s size, this trace focuses on the functions that directly affect data, utilities, or likelihoods.

#### 6.6.1 `precompute_data_singles(df, is_male=True)`

- **Called from:** `main()` after reading dataset.
- **Purpose:** Convert pandas columns to NumPy arrays stored in `PrecomputedDataSingles`.
- **Inputs:** DataFrame subset, flag for gender.
- **Operations:**  
  1. Extract arrays for `consumption`, `leisure`, `age_norm`, `age_norm2`, `n_children`, `educL`, `educH`, `reg2`, `reg3`, `gsur`, `pexp`, `pexp2`, `log_wage`, `hours`, `log_prior`.  
  2. Build `group_idx` referencing each individual’s row slice, using `idperson` factorization.  
  3. Store `is_chosen` vector (1 for observed draw).  
  4. Return dataclass for downstream functions.
- **Outputs:** `PrecomputedDataSingles`.
- **Failure modes:** Missing columns -> `KeyError`; NaNs propagate (logged).
- **Downstream consumer:** `ff_calc_util_singles`, gradient functions.

#### 6.6.2 `precompute_data_couples(df)`

- Similar to singles but handles male/female-specific columns (`leisure_m`, `leisure_f`, `age_norm_m/f`), plus shared consumption.

#### 6.6.3 `pack_theta_singles`, `unpack_theta_singles`

- Map between structured dataclasses and flat vector.  
- Important for ensuring joint parameter ordering remains consistent across runs.  
- Failure: mismatched length triggers ValueError, halting optimizer early.

#### 6.6.4 `get_initial_theta_*`

- Provide starting values; either defaults embedded in code or read from JSON via `--init-params`.

#### 6.6.5 `boxcox_transform`, `d_boxcox_dtheta`, `d_boxcox_dx`

- Evaluate Box–Cox transform and derivatives with safeguards for θ→0.

#### 6.6.6 `ff_calc_util_singles(data, pref, hopp, wopp)`

- **Purpose:** Build deterministic utility vector.  
- **Operations:**  
  1. Compute preference linear index \(X\beta\).  
  2. Multiply by `boxcox_transform(leisure, theta_l)`.  
  3. Add consumption term `beta_c * boxcox_transform(consumption, theta_c)`.  
  4. Add `ff_calc_hopp` output and `ff_calc_wopp` output.  
  5. Subtract `log_prior`.
- **Outputs:** Utility array.

#### 6.6.7 `ff_calc_util_couples`

- Same idea with male/female components and shared consumption.

#### 6.6.8 `ff_calc_hopp`, `ff_calc_hopp_couples`

- Evaluate log hours density by applying linear predictors to hours features (work vs non-work indicator, part-time dummies, GSUR, education interactions).

#### 6.6.9 `ff_calc_wopp`, `ff_calc_wopp_couples`

- Evaluate log wage density assuming log-normal distribution; includes education and experience effects plus optional region/year dummies.

#### 6.6.10 `fast_log_likelihood_singles`, `fast_log_likelihood_couples`

- Compose utilities with log-sum-exp per person to compute LL.  
- Use vectorized `np.bincount` to accumulate per-individual normalization constants.

#### 6.6.11 `fast_neg_ll_with_grad_singles`, `fast_neg_ll_with_grad_couples`

- Return negative LL plus gradient by combining derivatives of preference, hours, wage components.  
- Implementation avoids loops by stacking derivative arrays and using `P_weighted_dV = P * dV`.

#### 6.6.12 `_compute_utility_derivatives_singles`, `_compute_hopp_derivatives`, `_compute_wopp_derivatives`

- Provide derivative arrays for each parameter with respect to leisure/consumption/hours/wage components.  
- Used both by “fast” gradient functions and fallback slower versions.

#### 6.6.13 `fast_neg_ll_with_grad_joint`

- Combines single male, single female, and couples contributions into a single LL/gradient pair, ensuring shared opportunity parameters accumulate gradient contributions appropriately.

#### 6.6.14 `neg_log_likelihood_with_grad_joint`

- Wrapper deciding whether to call fast NumPy/Numba implementation; used by optimizer as `fun`.

#### 6.6.15 `_load_init_params_from_csv(path)`

- Allows warm-start from CSV (name,value). Aligns names with current order; warns about missing names.

#### 6.6.16 `parse_args()` / `main()`

- Steps:  
  1. Parse CLI options.  
  2. Read dataset, precompute arrays.  
  3. Load initial θ (default or from file).  
  4. Run `minimize`.  
  5. Serialize results to JSON (parameter values, names, gradient norms, runtime).  
  6. If `--post-estimation`, call `run_post_estimation`.

---

## 7. Stage E — Post-Estimation (`RURO_post_estimation.py`)

### 7.1 Outputs

- HTML report `vw_joint_post_estimation_report.html` summarizing estimation, diagnostics, and plots.
- PNG plots: marginal utilities, hours fit, MU diagnostics, contour charts, MRS curves.
- Optional CSV/Excel tables (if CLI flags set) listing parameter estimates, SEs, diagnostics.

### 7.2 Function Execution Trace (selected)

#### 7.2.1 `ParsedParameters` (`__post_init__`, `_parse_parameters`, `_identify_model_structure`)

- **Purpose:** Convert JSON results into structured dictionaries keyed by group.
- **Inputs:** JSON dictionary from estimation (`params`, `param_names`, metadata).
- **Operations:**  
  1. Zip names/values into dict.  
  2. Determine wage spec, whether joint estimation run, and lengths of each block.  
  3. Provide helper accessors (`get_param`, `get_leisure_coef_params`, etc.).
- **Failure modes:** Missing parameter names -> ValueError; script halts with message so JSON must match specification.
- **Downstream consumer:** All diagnostics rely on `ParsedParameters`.

#### 7.2.2 `compute_standard_errors(parsed_params, jacobian=None, hessian=None)`

- **Purpose:** Estimate covariance matrix.  
- **Operations:**  
  1. If Hessian provided (rare), invert it with damping.  
  2. Otherwise compute numerical Hessian using central differences (expensive).  
  3. Return SEs and t-stats in DataFrame.
- **Failure modes:** Singular Hessian -> warnings, NaN SE.
- **Downstream consumer:** Parameter tables in HTML.

#### 7.2.3 `compute_marginal_utility_consumption`, `compute_marginal_utility_leisure`

- Evaluate MU for each observation using Box–Cox derivatives; clip inputs to avoid negative values.

#### 7.2.4 `compute_mrs`

- Ratio of MU_l to MU_c at given shifters; used for elasticity calculations.

#### 7.2.5 `compute_beta_l_at_median`, `get_default_median_shifters`, `compute_median_shifters_from_data`

- Provide representative shifters (median age, education, children) for plotting MU surfaces.

#### 7.2.6 `compute_negative_mu_diagnostics`, `compute_all_mu_diagnostics`

- Summaries of how often MU_c or MU_l falls below zero; helps detect implausible parameter combinations.

#### 7.2.7 `compute_fit_diagnostics`

- **Purpose:** Compare observed vs predicted hours outcomes, compute LL statistics.
- **Inputs:** Dataset, parsed parameters.
- **Operations:**  
  1. Recompute utilities/probabilities.  
  2. Aggregate predicted shares over hours bins, zero hours, part-time.  
  3. Calculate LL_start (from initial θ if stored) and LL_end; compute pseudo-R².
- **Outputs:** Dictionary consumed by HTML report.

#### 7.2.8 Plotting functions (`plot_fit_comparison`, `plot_marginal_utilities`, `plot_mu_diagnostics`, `plot_mu_comparison`, `plot_utility_contours_all_groups`)

- Generate PNG images saved next to HTML. Each function documents axes, titles, and file names for reproducibility.

#### 7.2.9 `compute_structural_elasticities`, `analyze_muc_behavior`

- Optional advanced diagnostics triggered by CLI flags; compute wage elasticities or analyze marginal utility curvature.

#### 7.2.10 `generate_html_report(parsed_params, diagnostics, plot_info, output_path)`

- Compose final HTML with sections for overview, parameter tables, diagnostics, and embedded plots.

#### 7.2.11 `run_post_estimation(args)`

- CLI entry called from estimation stage; orchestrates operations above and logs success/failure.

---

## 8. Complete Artifact Inventory

```
Data/
 └─ processed/fr/2016/
      ├─ fr_2016_singles.parquet
      ├─ fr_2016_couples.parquet
      ├─ singles_RURO_ready.parquet
      ├─ couples_RURO_ready.parquet
      ├─ singles_RURO_ready_RURO_draws.parquet
      ├─ couples_RURO_ready_RURO_draws.parquet
      └─ fr_2016_RURO_mnl.parquet
Data/external/
 └─ FR_gsur_ruro.parquet
outputs/
 ├─ estimates/fr/2016/
 │    ├─ combined_draws_em.parquet
 │    ├─ fr_2016_joint.json
 │    ├─ vw_joint_post_estimation_report.html
 │    └─ *.png diagnostics
 └─ logs/
      └─ fr_2016_joint_only_<timestamp>.md
```

| Artifact | Producer | Format | Contents | Downstream usage |
| --- | --- | --- | --- | --- |
| `fr_2016_singles.parquet`, `fr_2016_couples.parquet` | `france_data_prep.py` | Parquet | Cleaned EUROMOD microdata for deciders | Input to `RURO_prep.py` |
| `*_RURO_ready.parquet` | `RURO_prep.py` | Parquet | Adds experience, education, RURO flags, pi0 | Input to `RURO_draws.py` |
| `*_RURO_ready_RURO_draws.parquet` | `RURO_draws.py` | Parquet | Observed + simulated opportunities, priors | Input to `RURO_euromod.py` & `RURO_prep_mnl_basic.py` |
| `combined_draws_em.parquet` | `RURO_euromod.py` | Parquet | Disposable income, taxes, benefits per draw | Input to `RURO_prep_mnl_basic.py` |
| `FR_gsur_ruro.parquet` | `prepare_FR_gsur.py` | Parquet | Region×gender×year GSUR values | Merged into MNL dataset |
| `fr_2016_RURO_mnl.parquet` | `RURO_prep_mnl_basic.py` | Parquet | Final long MNL dataset with normalized consumption/leisure, priors | Input to `RURO_estimate_FR.py` |
| `fr_2016_joint.json` | `RURO_estimate_FR.py` | JSON | Parameter estimates, optimizer metadata, gradients | Input to `RURO_post_estimation.py` |
| `vw_joint_post_estimation_report.html`, PNGs | `RURO_post_estimation.py` | HTML/PNG | Diagnostics, plots, parameter tables | Analyst consumption |
| `fr_2016_joint_only_<timestamp>.md` | PowerShell script | Markdown log | Commands executed, durations, success/failure | Audit trail |

---

## 9. Reproducibility Contract

1. **Seed policy:**  
   - RURO draws: pass explicit `--rng-seed` (and `--couples-rng-seed`) to `RURO_draws.py` for deterministic opportunity sets.  
   - EUROMOD deterministic given identical inputs; no random seed needed.

2. **Configuration capture:**  
   - `run_fr_2016_joint_only.ps1` logs CLI commands, environment variables, and timestamps. Retain log files alongside outputs for provenance.

3. **How to rerun from scratch:**  
   - Delete or rename `Data/processed/fr/2016/fr_2016_RURO_mnl.parquet` to force Steps 1–6.  
   - Execute  
     ```powershell
     powershell -ExecutionPolicy Bypass -File scripts/run_fr_2016_joint_only.ps1
     ```  
   - Verify outputs match checklist (MNL dataset, JSON, HTML, log).

4. **Comparison policy:**  
   - Use `jq` or Python to compare `fr_2016_joint.json` parameter arrays between runs.  
   - Differences should be ≤ optimizer tolerance if seeds unchanged. Larger shifts indicate upstream data differences.

5. **Stability assumptions:**  
   - EUROMOD and pandas versions should remain constant; major upgrades can change rounding, requiring re-validation.

6. **External dependencies:**  
   - Path resolution relies on mapped network drives (`U:/`). If running elsewhere, set env vars `MNL_STORAGE_ROOT`, `MNL_EUROMOD_ROOT`.  
   - EUROMOD license must remain valid; failing license check halts pipeline at Step 4.

---

## 10. Known Limitations / Technical Debt

1. **Over-parameterized preferences:** Legacy child age-band coefficients still exist; even though new data provides `n_children`, parameters remain in vector (some fixed later). Leads to weak identification and NaN SEs.
2. **Wage opportunity complexity:** Region and year dummies inflate dimensionality and yield extreme t-values; plan to align with literature by keeping only education and experience effects.
3. **Loose bounds:** Box–Cox exponents, `beta_c`, and wage `sigma` currently have wide or implicit bounds; risk of optimizer exploring unstable regions.
4. **Path dependencies:** Hard-coded `U:/` paths remain in scripts; analysts working offline must override manually.
5. **EUROMOD fragility:** If EUROMOD input schema changes, `_prepare_euromod_dataset` must be updated; errors manifest only during runtime with cryptic EUROMOD logs.
6. **No automated regression tests:** Multi-step transformations rely on manual inspection; a future test suite should validate key invariants (e.g., priors sum to 1, consumption positive).
7. **Monolithic estimation script:** `RURO_estimate_FR.py` exceeds 5k lines; refactoring into modules (data prep, utilities, optimizer) would improve maintainability.
8. **Legacy post-estimation references:** PowerShell script still comments out an older post-est step; ensure documentation stays aligned with actual outputs to avoid confusion.
9. **GSUR merge assumptions:** Script forward-fills missing GSUR entries quietly; adds risk if new regions appear. Deserves stronger validation warnings.
10. **Importance sampling alignment:** RURO draws and estimation must agree on priors. No automatic check prevents users from modifying draws without updating `_compute_prior`, so documentation must emphasize keeping them in sync.

---

*End of report – update whenever pipeline ordering, function responsibilities, or outputs change.*
