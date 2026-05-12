# RURO Job-Choice Model: Full Pipeline Documentation

## 1. What This Project Does

This project estimates a **Random Utility Random Opportunity (RURO) Multinomial Logit (MNL)** labor supply model with discrete **job choice** for France. The model explains how individuals and couples choose among labor market opportunities (combinations of hours, wages, and occupations) given the tax-benefit system, their preferences, and the labor market conditions they face.

The "job-choice" variant extends the standard RURO framework by treating jobs as **discrete bundles** of (hours, wage, occupation) rather than continuous draws from a smooth distribution. This allows the model to capture occupation-specific labor market frictions and education-dependent market access.

**Country**: France
**Data year**: 2016
**Tax-benefit model**: EUROMOD (EU-wide microsimulation)
**Estimation method**: Maximum Likelihood via L-BFGS-B (SciPy) or CONOPT (GAMSPy)

---

## 2. Pipeline Overview

The pipeline runs **8 scripts in sequence**, transforming raw EUROMOD microdata into estimated structural parameters with standard errors and diagnostics:

```
Script 1: enh_france_data_prep.py        Raw EUROMOD filtering
    |
Script 2: enh_RURO_prep.py              Labor supply variable construction
    |
Script 3: enh_job_universe.py           Discrete job universe creation       [JOB-CHOICE SPECIFIC]
    |
Script 4: enh_job_draws.py              Job opportunity sampling             [JOB-CHOICE SPECIFIC]
    |
Script 5: enh_RURO_euromod.py           Tax-benefit simulation (EUROMOD)
    |
Script 6: enh_prepare_FR_gsur.py        Unemployment rate lookup (GSUR)      [Run once]
    |
Script 7: enh_RURO_prep_mnl_basic.py    MNL dataset assembly
    |
Script 8: enh_RURO_estimate_FR.py       MNL estimation
    |
Script 9: RURO_post_estimation_styled.py Post-estimation report
```

Scripts 3-4 replace the continuous-draw script (`enh_RURO_draws.py`) used in the standard RURO model. Script 6 only needs to run once per country/year combination.

---

## 3. Detailed Script-by-Script Guide

### Script 1: `enh_france_data_prep.py` — Raw Data Filtering

**Location**: `scripts/enhanced/enh_france_data_prep.py`

**Purpose**: Filter raw EUROMOD household/person data to the working-age population relevant for labor supply analysis.

**What it does**:
1. Loads raw EUROMOD output (`FR_{year}.txt`) containing all households and persons
2. Filters to working-age adults (18-65) with labor status codes 3, 5, or 7 (employed, self-employed, unemployed)
3. Computes and validates wages (hourly, monthly), removes outliers
4. Constructs household-level decision units (who is a "singles" vs "couples" household)
5. Generates diagnostic plots (wage distributions, hours distributions, education, etc.)

**Inputs**:
- Raw EUROMOD data: `FR_{year}.txt`
- Configuration (age range, wage bounds, hours caps, etc.)

**Outputs**:
- `singles_filtering_final.parquet` — Singles households (one decision-maker)
- `couples_filtering_final.parquet` — Couples households (two decision-makers)

**Key command**:
```powershell
python scripts/enhanced/enh_france_data_prep.py `
  --year 2016 `
  --raw-dir "Z:/path/to/raw" `
  --out-dir "Z:/path/to/processed/fr/2016" `
  --export-format parquet
```

---

### Script 2: `enh_RURO_prep.py` — RURO Variable Construction

**Location**: `scripts/enhanced/enh_RURO_prep.py`

**Purpose**: Build the demographic, labor market, and structural variables needed for RURO estimation from the filtered data.

**What it does**:
1. Loads filtered singles and couples data
2. Creates RURO group flags (`ruro_group`: 1=singles, 10=couples)
3. Identifies decision-makers (`ruro_sample`, `ruro_decider`)
4. Constructs key variables:
   - **Working indicators**: `working`, `working_pt1` (~20h), `working_pt2` (~30h), `working_ft` (~40h)
   - **Experience**: `pexp_years`, `pexp_years2` from work history (`liwwh` priority, then `dew`, then `dey`)
   - **Education dummies**: `educL`, `educM`, `educH` (from `deh` levels)
   - **Age**: `age_norm` (demeaned), `age_norm2` (squared)
   - **Children**: `n_children` (count of dependent children)
   - **Region dummies**: `reg_nuts1_1` through `reg_nuts1_10`
   - **Occupation**: `loc_ruro`, `loc4`, `isco1` (ISCO-08 1-digit)
   - **Baseline values**: `lhw_base`, `yivwg_base` (preserved for draw=0)

**Inputs**:
- `singles_filtering_final.parquet`, `couples_filtering_final.parquet`

**Outputs**:
- `singles_RURO_ready.parquet` — Singles with all RURO variables
- `couples_RURO_ready.parquet` — Couples with all RURO variables
- `*__colgroups.json` — Column metadata sidecar

**Key command**:
```powershell
python scripts/enhanced/enh_RURO_prep.py `
  --processed-dir "Z:/path/to/processed/fr/2016" `
  --base-year 2016 `
  --export-format parquet
```

---

### Script 3: `enh_job_universe.py` — Job Universe Construction (JOB-CHOICE SPECIFIC)

**Location**: `scripts/Job_model/enh_job_universe.py`

**Purpose**: Build a discrete grid of possible jobs from observed labor market outcomes. Each job is a unique (hours_bin, wage_bin, occupation) triple.

**What it does**:
1. Loads RURO-ready data (singles + couples)
2. Defines hours bins (e.g., cutpoints at 5, 16, 31, 43, 71 hours/week)
3. Defines wage bins (data-dependent deciles or fixed cutpoints)
4. Counts observed workers in each (hours_bin, wage_bin, isco1) cell
5. Assigns representative values: `hours_rep`, `wage_rep` (bin means/medians)
6. Computes empirical prior: q_j = cell_count / total_count (with optional Laplace smoothing)
7. Assigns `job_id` to each cell (sequential: 1..N; 0 = non-employment)
8. Optionally prunes rare cells (empirical_pruned mode)

**Universe modes**:
- `empirical_pruned` (default): Drop cells with < 5 observations
- `empirical_all`: Keep all observed cells
- `full_grid`: Complete dense grid, fill empty cells
- `gmm_occ`: Gaussian mixture-based occupation types (advanced)

**Inputs**:
- `singles_RURO_ready.parquet`, `couples_RURO_ready.parquet`

**Outputs**:
- `job_universe_{year}.parquet` — Job grid with columns: `job_id`, `hours_bin`, `wage_bin`, `isco1`, `hours_rep`, `wage_rep`, `yem_rep`, `q_j_prior`
- `job_universe_{year}__meta.json` — Bin definitions and metadata
- `job_universe_{year}__gmm_diagnostics.csv` — GMM fit diagnostics (if gmm mode)

**Key command**:
```powershell
python scripts/Job_model/enh_job_universe.py `
  --singles-path "Z:/path/singles_RURO_ready.parquet" `
  --couples-path "Z:/path/couples_RURO_ready.parquet" `
  --output-dir "Z:/path/to/processed/fr/2016/job_model_gmm" `
  --universe-mode gmm_occ `
  --year 2016
```

---

### Script 4: `enh_job_draws.py` — Job Opportunity Sampling (JOB-CHOICE SPECIFIC)

**Location**: `scripts/Job_model/enh_job_draws.py`

**Purpose**: For each individual/couple, generate a set of K hypothetical job opportunities by sampling from the job universe.

**What it does**:
1. Loads the job universe grid
2. For each decision-maker, creates draw=0 (their observed/baseline job)
   - Maps their actual (hours, wage, occupation) to the nearest `job_id`
3. For draws 1..K, samples hypothetical jobs:
   - With probability pi0 (gender-specific): non-employment (job_id=0, hours=0, wage=0)
   - With probability (1-pi0): sample a `job_id` from the empirical prior q_j
4. Attaches job attributes (hours_rep, wage_rep, isco1) to each draw
5. Computes proposal density components: `log_q_job`, `log_q_state`, `log_q_total`
6. Creates EUROMOD-compatible aliases (`lhw`, `yivwg`, `yem`)
7. Replicates non-deciders (children, other adults) across all draws for EUROMOD

**This replaces** `enh_RURO_draws.py` (continuous sampling) in the job-choice pipeline.

**Key difference from continuous RURO**: Instead of sampling hours ~ Uniform[h_min, h_max] and wage ~ Uniform[w_min, w_max], we sample a discrete `job_id` from the job universe. The hours and wage are then the representative (posted) values for that job.

**Inputs**:
- `singles_RURO_ready.parquet`, `couples_RURO_ready.parquet`
- `job_universe_{year}.parquet`

**Outputs**:
- `singles_RURO_ready_RURO_draws.parquet` — Singles with K+1 rows per person (draw 0..K)
- `couples_RURO_ready_RURO_draws.parquet` — Couples with K+1 rows per household-member (draw 0..K)
- `*__drawsmeta.json` — Draw parameters (pi0, n_draws, h/w bounds, wage_spec)

**Key command**:
```powershell
python scripts/Job_model/enh_job_draws.py `
  --singles-path "Z:/path/singles_RURO_ready.parquet" `
  --couples-path "Z:/path/couples_RURO_ready.parquet" `
  --job-universe "Z:/path/job_universe_2016.parquet" `
  --output-dir "Z:/path/to/draws_output" `
  --n-draws 199 `
  --pi0-m 0.10 --pi0-f 0.10 `
  --wage-spec fw `
  --rng-seed 17
```

---

### Script 5: `enh_RURO_euromod.py` — Tax-Benefit Simulation

**Location**: `scripts/enhanced/enh_RURO_euromod.py`

**Purpose**: Run the EUROMOD tax-benefit microsimulation on ALL draws (observed + hypothetical) to compute disposable income for each possible labor market outcome.

**Why this is needed**: RURO models require knowing the **net income** (after taxes and benefits) for each hypothetical job. EUROMOD computes this by applying the full French tax-benefit system to each scenario.

**What it does**:
1. Loads draws files (singles + couples) and EUROMOD microdata template
2. For each draw: overwrites labor inputs (hours, wages, earnings) in the EUROMOD template
3. Creates draw-specific household/person IDs (idhh * 1000 + draw) for panel structure
4. Handles EUROMOD accounting identities (yem00 for regular hours, yemxp for overtime)
5. For job-choice: applies occupation overrides from job draws (isco1)
6. Replicates non-deciders across all draws (children keep baseline values)
7. Runs EUROMOD **once** on the combined dataset (efficient batch processing)
8. Merges back: carry columns (draw, job_id, log_q_*, demographics)

**Inputs**:
- `singles_RURO_ready_RURO_draws.parquet` (from Script 4)
- `couples_RURO_ready_RURO_draws.parquet` (from Script 4)
- EUROMOD microdata template (baseline household data)
- EUROMOD system + dataset codes

**Outputs**:
- `combined_draws_em.parquet` — EUROMOD output for all draws (disposable income, taxes, benefits for each scenario)
- `*__euromodmeta.json` — EUROMOD run metadata

**Key command**:
```powershell
python scripts/enhanced/enh_RURO_euromod.py `
  --singles-draws "Z:/path/singles_draws.parquet" `
  --couples-draws "Z:/path/couples_draws.parquet" `
  --microdata-template "Z:/path/FR_2016_template.txt" `
  --euromod-system FR_2015 `
  --euromod-dataset FR_2016_c2 `
  --scenario-dir "Z:/path/to/scenarios"
```

---

### Script 6: `enh_prepare_FR_gsur.py` — Unemployment Rate Lookup (Run Once)

**Location**: `scripts/enhanced/enh_prepare_FR_gsur.py`

**Purpose**: Transform Eurostat unemployment rate data into a clean lookup table, capturing regional and education-specific labor market tightness.

**What it does**:
1. Reads Eurostat unemployment data (`FR_gsur.xlsx`, 120 sheets)
2. Parses education × gender × age group combinations
3. Creates lookup keyed on (year, drgn1, dgn, educ3)
4. Maps French NUTS1 regions to drgn1 codes
5. Selects appropriate age group (prefer Y20-64)

**Why GSUR matters**: The unemployment rate (`gsur`) captures how tight the labor market is for each demographic group. It enters the market opportunity function, allowing the model to distinguish between "this person doesn't work because they don't want to" vs "this person doesn't work because the labor market is bad for their group."

**Inputs**:
- `FR_gsur.xlsx` (Eurostat unemployment data)

**Outputs**:
- `FR_gsur_ruro.parquet` — Lookup table: (year, drgn1, dgn, educ3) -> gsur
- `FR_gsur_ruro.csv` — Same, for inspection

**Key command** (run once):
```powershell
python scripts/enhanced/enh_prepare_FR_gsur.py `
  --input "Data/external/FR_gsur.xlsx" `
  --output-dir "Data/external"
```

---

### Script 7: `enh_RURO_prep_mnl_basic.py` — MNL Dataset Assembly

**Location**: `scripts/enhanced/enh_RURO_prep_mnl_basic.py`

**Purpose**: Assemble the final estimation-ready MNL dataset by combining EUROMOD outputs with GSUR, computing consumption/leisure, normalizing variables, computing prior probabilities, and reshaping couples to wide format.

**What it does**:
1. **Load and merge**: Join EUROMOD output (disposable income per draw) with draws data (demographics, job attributes)
2. **Restrict to deciders**: Keep only heads/partners (exclude children, other adults)
3. **Merge GSUR**: Match unemployment rates by (year, region, gender, education)
4. **Compute consumption**: From EUROMOD disposable income (ils_dispy)
5. **Compute leisure**: leisure = total_time - hours_worked (capped, floored)
6. **Normalize**: c_norm = c / c_scale, l_norm = l / l_scale (scales from observed choices)
7. **Compute prior**: log_prior = log(q_hours) + log(q_wage) + log(q_occupation) (importance sampling correction)
8. **Reshape couples**: Long format (one row per person) -> Wide format (one row per household with `_male`/`_female` suffixed columns)
9. **Create derived variables**: `n_children` for household (couples), education dummies, age variables
10. **Column filtering**: Reduce from 900+ columns to ~100 essential ones (85-90% size reduction)
11. **Sanity checks**: Validate structure, no NaN in key variables, couples balance

**Inputs**:
- `combined_draws_em.parquet` (from Script 5)
- `singles_RURO_ready_RURO_draws.parquet`, `couples_RURO_ready_RURO_draws.parquet` (from Script 4)
- `FR_gsur_ruro.parquet` (from Script 6)
- `*__drawsmeta.json` (draw parameters)

**Outputs**:
- `fr_2016_RURO_mnl_job_gmm__singles.parquet` — Singles MNL dataset (~335K rows: 1,676 persons x 200 alternatives)
- `fr_2016_RURO_mnl_job_gmm__couples.parquet` — Couples MNL dataset (~515K rows: 2,577 households x 200 alternatives)
- `fr_2016_RURO_mnl_job_gmm__mnlmeta.json` — Metadata (normalization scales, sample sizes, columns)

**Key command**:
```powershell
python scripts/enhanced/enh_RURO_prep_mnl_basic.py `
  --singles-draws "Z:/path/singles_draws.parquet" `
  --couples-draws "Z:/path/couples_draws.parquet" `
  --euromod-combined "Z:/path/combined_draws_em.parquet" `
  --gsur-file "Data/external/FR_gsur_ruro.parquet" `
  --drawsmeta "Z:/path/drawsmeta.json" `
  --out-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_job_gmm" `
  --wage-spec fw `
  --year 2016 `
  --verbose
```

**Output structure** (each row is one alternative for one person/household in one draw):

| Column | Description |
|--------|-------------|
| `idhh`, `idperson`, `draw` | Identifiers |
| `is_chosen` | 1 if this is the observed choice, 0 otherwise |
| `job_id` / `job_id_male` / `job_id_female` | Discrete job identifier |
| `hours`, `wage`, `isco1` | Job attributes |
| `consumption`, `leisure` | Utility arguments (from EUROMOD) |
| `c_norm`, `l_norm` | Normalized consumption and leisure |
| `prior`, `log_prior` | Prior probability (importance weight) |
| `gsur` / `gsur_male` / `gsur_female` | Unemployment rate for individual's group |
| `age_norm`, `age_norm2` | Demeaned age and age-squared |
| `n_children` | Number of dependent children |
| `educL`, `educM`, `educH` | Education dummies |
| `working` | 1 if hours > 0 |

---

### Script 8: `enh_RURO_estimate_FR.py` — MNL Estimation

**Location**: `scripts/enhanced/enh_RURO_estimate_FR.py`

**Purpose**: Estimate the structural parameters of the RURO MNL model by maximizing the log-likelihood.

**What it does**:
1. **Parse specification**: Load the YAML specification file defining the model structure (which parameters, which shifters, bounds, initial values)
2. **Load data**: Read MNL parquet files + metadata JSON
3. **Validate**: Check data-specification compatibility
4. **Filter by group**: Select singles_male, singles_female, couples, or joint (all together)
5. **Precompute**: Extract and organize data arrays for fast likelihood evaluation
   - Consumption/leisure grids per individual
   - Choice indicators
   - Demographic covariates (age, education, children)
   - Market opportunity shifter variables (isco1 dummies, gsur, interactions)
   - Leisure shifter variables (age_norm, age_norm2, n_children, educH)
   - Prior probabilities (importance sampling correction)
6. **Validate precomputed data**: Verify all specification-required variables are present
7. **Warm-start**: Load initial parameter values from previous estimation (if available)
8. **Estimate**: Maximize joint log-likelihood using solver:
   - **SciPy L-BFGS-B**: Bounded optimization with analytical gradients
   - **GAMSPy CONOPT**: Vectorized model with automatic differentiation (2-3x faster)
9. **Compute standard errors**: Numerical Hessian (central finite differences), invert for var-cov matrix
10. **Identification diagnostics**: Hessian condition number, eigenvalue analysis, bound hits
11. **Save results**: JSON, CSV, summary text, log, spec copy

**The Model**:

For each individual *i* choosing alternative *j* from choice set *Q_i*:

```
P(j | Q_i, X_i; theta) = exp(V_ij + log lambda_ij) / sum_k exp(V_ik + log lambda_ik)
```

Where:
- **V_ij** = Utility of alternative j for individual i:
  ```
  V_ij = [beta_l0 + beta_l_age * age_i + beta_l_age2 * age_i^2
          + beta_l_nkids * nkids_i + beta_l_educH * educH_i] * BC(leisure_ij; theta_l)
        + beta_c * BC(consumption_ij; theta_c)
  ```
  BC(x; theta) = (x^theta - 1) / theta  (Box-Cox transformation)

- **log lambda_ij** = Market opportunity (log probability of being offered job j):
  ```
  log lambda_ij = log prior_ij + sum_k beta_offer_isco1_k * isco1_k_j * working_j
                + beta_offer_gsur_educM * gsur_i * working_j * educM_i
                + beta_offer_gsur_educH * gsur_i * working_j * educH_i
  ```

- **log prior_ij** = Proposal density correction (importance sampling weight from draw generation)

**Inputs**:
- `fr_2016_RURO_mnl_job_gmm__singles.parquet` (from Script 7)
- `fr_2016_RURO_mnl_job_gmm__couples.parquet` (from Script 7)
- `fr_2016_RURO_mnl_job_gmm__mnlmeta.json` (from Script 7)
- `estimation_spec_job_M2c.yaml` (model specification)

**Outputs** (in timestamped subfolder):
- `estimation_results.json` — Full results (parameters, SEs, diagnostics, metadata)
- `estimation_results_singles_male.csv` / `_singles_female.csv` / `_couples.csv` — Parameter tables
- `estimation_summary.txt` — Human-readable summary
- `identification_diagnostics.txt` — Hessian condition number, eigenvalue analysis
- `specification_used.yaml` — Copy of spec used
- `estimation.log` — Full execution log

**Key command**:
```powershell
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_job_gmm" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/job_choice/gamspy" `
  --group joint `
  --solver gamspy-conopt --vectorized `
  --spec-config scripts/enhanced/estimation_spec_job_M2c.yaml `
  --auto-timestamp --verbose
```

---

### Script 9: `RURO_post_estimation_styled.py` — Post-Estimation Report

**Location**: `scripts/enhanced/RURO_post_estimation_styled.py`

**Purpose**: Generate an interactive HTML report with parameter tables, diagnostics, and model fit analysis.

**What it does**:
1. **Load results**: Parse estimation_results.json
2. **Compute statistics**: t-values, p-values, confidence intervals for all parameters
3. **Compute SEs** (if not in results): Re-load data, build numerical Hessian, invert
4. **Generate HTML report** with sections:
   - **Parameter estimates table**: Estimate, SE, t-stat, p-value, bounds, significance stars
   - **Model diagnostics**: Log-likelihood, AIC, BIC, gradient norms, convergence status
   - **Marginal utility analysis**: MUC (marginal utility of consumption) and MUL (marginal utility of leisure) checks — verifies economic theory (MUC > 0, MUL > 0)
   - **Bounds monitoring**: Identifies parameters at their bounds (potential identification issues)
   - **Utility decomposition**: Breaks down utility into preference + opportunity + prior components
   - **Hours distribution**: Predicted vs observed hours allocation across focal points (0h, PT1, PT2, FT)
   - **Identification diagnostics**: Hessian condition number, eigenvalues, stability relative to previous run
5. **Export CSV**: Parameter table for further analysis

**Inputs**:
- `estimation_results.json` (from Script 8)
- MNL data files (optional, enables richer diagnostics)
- Specification YAML (optional, for SE recomputation)

**Outputs** (in timestamped subfolder):
- `fr_2016_jobchoice_gmm_gamspy_params.csv` — Parameter table (estimate, SE, t, p, bounds)
- `fr_2016_jobchoice_gmm_gamspy_report.html` — Interactive HTML report
- `identification_diagnostics.txt` — Detailed identification analysis

**Key command**:
```powershell
python scripts/enhanced/RURO_post_estimation_styled.py `
  --results-json "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/job_choice/gamspy/run_YYYY-MM-DD_HH-MM-SS/estimation_results.json" `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_job_gmm" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/post_estimation/fr/spec/job_choice/gamspy" `
  --prefix "fr_2016_jobchoice_gmm_gamspy_" `
  --compute-se `
  --spec-config scripts/enhanced/estimation_spec_job_M2c.yaml `
  --auto-timestamp
```

---

## 4. Supporting Files

### Specification YAML (`estimation_spec_job_M2c.yaml`)

The YAML specification file defines the entire model structure. It is read by the estimation script and controls:

- **Utility function**: Box-Cox form, consumption/leisure coefficients, Box-Cox exponents
- **Leisure shifters**: Which demographic variables shift leisure preferences (age, children, education)
- **Market opportunity shifters**: Which variables shift job offer probabilities (occupation dummies, gsur × education)
- **Initial values**: Starting point for optimization (warm-started from previous spec)
- **Bounds**: Parameter bounds for constrained optimization
- **Expression constraints**: Soft penalties ensuring marginal utility positivity
- **Optimization settings**: Method, tolerance, max iterations

### Parser (`estimation_spec_parser.py`)

Parses the YAML spec into an `EstimationSpec` dataclass. Handles:
- Parameter name generation (gender-specific suffixes: `_sm`, `_sf`, `_m`, `_f`)
- Automatic parameter ordering (preference -> opportunity)
- Warm-start value loading from previous results
- Validation of specification consistency

### Estimation Engine (`estimation_engine.py`)

Core likelihood computation with analytical gradients (NumPy):
- `compute_likelihood_singles()` / `compute_likelihood_couples()`
- `compute_gradient_singles()` / `compute_gradient_couples()`
- `compute_gradient_joint()` — Stacks all groups for joint estimation
- Box-Cox transforms and their derivatives

### GAMSPy Vectorized Engine (`gamspy_estimation_vectorized.py`)

Alternative solver using GAMSPy algebraic modeling:
- Builds the optimization problem using indexed GAMS variables
- Uses automatic differentiation (no hand-coded gradients)
- Supports CONOPT, IPOPT, KNITRO solvers
- 2-3x faster than SciPy for this model

### Utilities (`estimation_utils.py`)

Data loading, validation, and precomputation:
- `load_and_validate_mnl_data()` — Load + validate MNL datasets
- `precompute_data_singles()` / `precompute_data_couples()` — Build arrays
- `PrecomputedDataSingles` / `PrecomputedDataCouples` — Dataclass structures
- `_extract_or_derive_single()` — Extract variables from parquet or derive from existing columns

---

## 5. Data Flow Diagram

```
                    RAW EUROMOD DATA
                    (FR_2016.txt)
                          |
                    [Script 1: enh_france_data_prep.py]
                    Filter: age 18-65, les in {3,5,7}
                    Compute: wages, hours, income
                          |
              +-----------+-----------+
              |                       |
    singles_filtering        couples_filtering
       _final.parquet           _final.parquet
              |                       |
              +-----------+-----------+
                          |
                    [Script 2: enh_RURO_prep.py]
                    Create: working flags, education dummies,
                    age_norm, n_children, pexp_years,
                    region dummies, occupation codes
                          |
              +-----------+-----------+
              |                       |
    singles_RURO              couples_RURO
     _ready.parquet            _ready.parquet
              |                       |
              +-----------+-----------+
                          |
                    [Script 3: enh_job_universe.py]
                    Build discrete job grid:
                    (hours_bin x wage_bin x isco1) -> job_id
                          |
                   job_universe_2016.parquet
                    (200 discrete jobs)
                          |
              +-----------+-----------+
              |                       |
    singles_RURO_ready       couples_RURO_ready
              |                       |
              +-----------+-----------+
                          |
                    [Script 4: enh_job_draws.py]
                    For each person: sample 199 jobs
                    from universe + 1 observed job
                    Compute proposal density q(j)
                          |
              +-----------+-----------+
              |                       |
    singles_draws.parquet    couples_draws.parquet
    (335K rows: 1,676        (515K rows: 2,577
     persons x 200 alts)      hh x 200 alts)
              |                       |
              +-----------+-----------+
                          |
                    [Script 5: enh_RURO_euromod.py]
                    Run EUROMOD on all 850K scenarios
                    Compute: ils_dispy (disposable income),
                    taxes, benefits for each (person, job)
                          |
                combined_draws_em.parquet
                    (all scenarios with income)
                          |
              +-----------+-----------+
              |                       |
    combined_draws_em        FR_gsur_ruro.parquet
                             (unemployment rates)
                             [Script 6: run once]
              |                       |
              +-----------+-----------+
                          |
                    [Script 7: enh_RURO_prep_mnl_basic.py]
                    Merge EUROMOD output + GSUR
                    Compute: consumption, leisure, normalize
                    Reshape couples to wide format
                    Compute prior probabilities
                    Filter to essential columns
                          |
              +-----------+-----------+
              |           |           |
    __singles.parquet  __couples.parquet  __mnlmeta.json
      (335K rows)       (515K rows)       (metadata)
              |           |           |
              +-----------+-----------+
                          |
                    [Script 8: enh_RURO_estimate_FR.py]
                    + estimation_spec_job_M2c.yaml
                    |
                    Parse spec -> Load data -> Precompute
                    -> Optimize LL -> Compute SEs
                    -> Save results
                          |
              +-----------+-----------+
              |           |           |
    estimation_    estimation_    identification_
    results.json   summary.txt   diagnostics.txt
              |
              |
                    [Script 9: RURO_post_estimation_styled.py]
                    Generate HTML report with:
                    - Parameter tables (estimate, SE, t, p)
                    - Model diagnostics (LL, AIC, BIC)
                    - Marginal utility checks
                    - Hours distribution fit
                    - Identification analysis
                          |
              +-----------+-----------+
              |                       |
    params.csv              report.html
```

---

## 6. Model Specification Evolution

| Spec | Parameters | Key Features | Status |
|------|-----------|--------------|--------|
| **M2** | 23 | Base: occupation_base=1 (drop isco1_1), 3-way isco1 interactions (isco1 x gsur x working) | Baseline |
| **M2b** | 26 | occupation_base=0 (all 9 isco1), 2-way isco1 (isco1 x working), + gsur x educM/H interactions | Improved |
| **M2c** | 36 | M2b + leisure shifters (age, age^2, n_children, educH). 25 preference + 11 market opportunity | Current |

### M2c Parameter Breakdown

**Preference Parameters (25 total)**:

| Parameter | SM | SF | CM | CF | Description |
|-----------|:--:|:--:|:--:|:--:|-------------|
| beta_l0   | x  | x  | x  | x  | Leisure intercept |
| beta_l_age | x | x  | x  | x  | Age -> leisure preference |
| beta_l_age2 | x | x | x  | x  | Age^2 -> leisure preference |
| beta_l_nkids | - | x | -  | x  | Children -> leisure preference (females only) |
| beta_l_educH | x | x | x  | x  | High education -> leisure preference |
| beta_c    | x  | x  | shared | shared | Consumption coefficient |
| theta_l   | x  | x  | x  | x  | Box-Cox exponent (leisure) |
| theta_c   | x  | x  | shared | shared | Box-Cox exponent (consumption) |

SM = Singles Male, SF = Singles Female, CM = Couples Male, CF = Couples Female

**Market Opportunity Parameters (11 total)**:

| Parameter | Description |
|-----------|-------------|
| beta_offer_isco1_1..9 | Occupation-specific employment shift (isco1_k x working) |
| beta_offer_gsur_educM | Education-gsur interaction (medium education) |
| beta_offer_gsur_educH | Education-gsur interaction (high education) |

---

## 7. Key Concepts

### RURO Framework
The Random Utility Random Opportunity model separates labor supply into:
- **Preferences** (utility): How much the individual values leisure vs consumption
- **Opportunities** (market access): What jobs are available to the individual

This separation is crucial for policy analysis: a tax reform changes the budget constraint (consumption), while a training program changes market access (opportunities).

### Job-Choice Extension
Instead of continuous (hours, wage) draws, jobs are discrete bundles. This:
- Captures occupation-specific labor market frictions
- Allows education-dependent market access (gsur interactions)
- Makes the model more realistic (people choose "jobs", not continuous hours)

### Importance Sampling Correction
Since draws are sampled from a proposal distribution q(j), not the true distribution, we correct with:
```
P(chosen | data) = sum_j [exp(V_j) / q(j)] * [1 / sum_k exp(V_k) / q(k)]
```
In log-space: log_prior = -log(q_j) enters the utility as an offset.

### Box-Cox Utility
The Box-Cox transform BC(x; theta) = (x^theta - 1) / theta generalizes:
- theta = 1: linear utility
- theta -> 0: log utility
- theta < 0: concave utility (diminishing marginal returns)

The theta parameters are estimated, allowing the data to determine the curvature of preferences.

### Identification
The model is identified through:
1. **Exclusion restrictions**: Variables in opportunity but not preference (isco1 dummies), and vice versa (age, children in leisure)
2. **Functional form**: Box-Cox nonlinearity in preferences vs log-linear opportunity
3. **Tax-benefit variation**: EUROMOD provides exogenous variation in consumption across jobs
4. **Proposal correction**: The prior/importance weight separates sampling artifacts from economic content

---

## 8. Orchestrator Script

For running Steps 3-5 together, there is an orchestrator:

**Location**: `scripts/Job_model/run_job_ruro_pipeline.py`

This script chains: job universe -> job draws -> EUROMOD in a single command, passing outputs from each stage to the next automatically. It is the recommended way to run the job-choice data preparation pipeline.

---

## 9. File Locations

| Type | Path |
|------|------|
| Scripts (enhanced) | `scripts/enhanced/` |
| Scripts (job-choice) | `scripts/Job_model/` |
| Spec files | `scripts/enhanced/estimation_spec_job_M2*.yaml` |
| Source MNL data | `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_job_gmm` |
| Estimation outputs | `U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/job_choice/gamspy/` |
| Post-estimation outputs | `U:/Desktop/Nizam_Hisham/MNL/outputs/post_estimation/fr/spec/job_choice/gamspy/` |
| GSUR data | `Data/external/FR_gsur_ruro.parquet` |
| Python environment | `.venv/` (use `.venv/Scripts/python.exe`) |
