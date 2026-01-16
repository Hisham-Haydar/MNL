# RURO Pipeline Complete Guide
## Random Utility Random Opportunity Labor Supply Model - France 2016

**Version:** Enhanced Pipeline
**Last Updated:** 2026-01-03
**Author:** RURO Estimation Team

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Directory Structure](#directory-structure)
4. [Pipeline Steps](#pipeline-steps)
5. [Running the Pipeline](#running-the-pipeline)
6. [Verifying Success](#verifying-success)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)

---

## Overview

This pipeline implements the **RURO (Random Utility Random Opportunity) labor supply model** for France 2016 data. The RURO model (Aaberge & Colombino 1998) is a structural discrete choice model that estimates labor supply behavior by:

1. **Random Utility**: Individuals maximize utility over consumption and leisure
2. **Random Opportunity**: Job opportunities are constrained by a stochastic opportunity set (hours, wages)

### Pipeline Architecture

The complete pipeline consists of **7 sequential steps**:

```
Step 1: france_data_prep.py       → Prepare raw EUROMOD data
Step 2: RURO_prep.py              → Build RURO-ready datasets
Step 3: RURO_draws.py             → Generate opportunity draws
Step 4: RURO_euromod.py           → Run EUROMOD simulation
Step 5: prepare_FR_gsur.py        → Prepare unemployment data
Step 6: RURO_prep_mnl_basic.py    → Build MNL estimation dataset
Step 7: RURO_estimate_FR.py       → Joint estimation (MNL)
```

### Key Features

- **Joint estimation** of singles (male/female) and couples
- **99 counterfactual draws** + 1 observed opportunity per individual
- **EUROMOD integration** for tax-benefit calculations
- **Multiple wage specifications**: Fixed wages (fw) or variable wages (vw)
- **GSUR unemployment rates** by region/gender/education
- **Parallel processing** with automatic CPU core detection
- **Enhanced logging** with timestamps and diagnostics

---

## Prerequisites

### 1. Software Requirements

- **Python 3.8+** with virtual environment (`.venv`)
- **PowerShell 5.1+** (Windows)
- **EUROMOD J1.0+** installation

### 2. Required Python Packages

```bash
pandas>=1.5.0
numpy>=1.23.0
scipy>=1.9.0
numba>=0.56.0
pyarrow>=10.0.0  # For parquet I/O
pyyaml>=6.0      # For estimation specs
```

**EUROMOD-specific:**
```bash
pythonnet  # For EUROMOD C# interop (if needed)
```

### 3. Data Requirements

#### Raw Data (Input)
- **EUROMOD microdata**: `FR_2016.txt`
  - Location: `U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt`
  - Source: EUROMOD standard format (SILC-based)

#### External Data (Optional)
- **GSUR unemployment rates**: `FR_gsur.xlsx`
  - Location: `U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur.xlsx`
  - Source: Eurostat NUTS1-level unemployment by gender/education

### 4. EUROMOD Configuration

- **Installation**: `U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+`
- **System**: `FR_2015` (system year = data year - 1)
- **Dataset**: `FR_2016`
- **Required policies**: Baseline system (no specific policy scenarios)

---

## Directory Structure

### Server Paths (Production)

```
U:\EUROMOD-STORAGE\
├── Data\
│   ├── raw\
│   │   └── FR_2016.txt                    # Input: Raw EUROMOD data
│   └── processed\fr\2016\
│       ├── fr_2016.parquet                # Output: Step 1
│       ├── singles_RURO_ready.parquet     # Output: Step 2
│       ├── couples_RURO_ready.parquet     # Output: Step 2
│       ├── singles_RURO_ready_RURO_draws.parquet  # Output: Step 3
│       ├── couples_RURO_ready_RURO_draws.parquet  # Output: Step 3
│       ├── fr_2016_RURO_mnl.parquet       # Output: Step 6
│       └── fr_2016_RURO_mnl__mnlmeta.json # Metadata: Step 6
├── interim\ruro\fr\scenarios_2016\
│   └── combined_draws_em.parquet          # Output: Step 4 (EUROMOD)
└── EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+\
    └── [EUROMOD installation files]

U:\Desktop\Nizam_Hisham\MNL\
├── scripts\enhanced\                       # All pipeline scripts
│   ├── enh_france_data_prep.py
│   ├── enh_RURO_prep.py
│   ├── enh_RURO_draws.py
│   ├── enh_RURO_euromod.py
│   ├── enh_prepare_FR_gsur.py
│   ├── enh_RURO_prep_mnl_basic.py
│   ├── enh_RURO_estimate_FR.py
│   ├── run_enhanced_pipeline.ps1          # PowerShell runner
│   ├── PIPELINE_GUIDE.md                  # This file
│   └── estimation_spec.yaml               # Estimation configuration
├── Data\external\
│   ├── FR_gsur.xlsx                       # Input: Unemployment data
│   └── FR_gsur_ruro.parquet               # Output: Step 5
└── outputs\
    ├── estimates\fr\2016\
    │   └── fr_2016_joint.json             # Output: Step 7 (results)
    ├── post_estimation\fr\2016\
    │   └── fr_2016_joint_post_estimation.html  # Diagnostics
    └── logs\
        └── fr_2016_joint_only_[timestamp].md   # Execution log
```

---

## Pipeline Steps

### Step 1: Data Preparation (`enh_france_data_prep.py`)

**Purpose**: Convert raw EUROMOD text file to analysis-ready format

**Inputs**:
- `U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt` (EUROMOD microdata)

**Outputs**:
- `fr_2016.parquet` - Full France dataset
- `fr_2016_singles.parquet` - Singles (male/female heads)
- `fr_2016_couples.parquet` - Couples (married/cohabiting)

**Key Operations**:
- Filter to France (country == "FR")
- Harmonize variable names (EUROMOD → analysis format)
- Split into singles/couples based on household structure
- Create baseline demographics (age, gender, education, region)

**Command**:
```powershell
python "enh_france_data_prep.py" `
  --year 2016 `
  --raw-dir "U:\EUROMOD-STORAGE\Data\raw" `
  --out-dir "U:\EUROMOD-STORAGE\Data\processed\fr\2016" `
  --system-year 2015 `
  --export-format parquet
```

**Expected Runtime**: 2-5 minutes
**Success Indicator**: Files created in `processed\fr\2016\`

---

### Step 2: RURO Preparation (`enh_RURO_prep.py`)

**Purpose**: Create RURO-ready datasets with baseline variables for opportunity generation

**Inputs**:
- `fr_2016_singles.parquet`
- `fr_2016_couples.parquet`

**Outputs**:
- `singles_RURO_ready.parquet`
- `couples_RURO_ready.parquet`

**Key Variables Created**:
- `ruro_group`: Estimation group (single_male, single_female, couple)
- `is_worker`: Employment status (hours > 0)
- `wage_ruro`: Hourly wage (earnings / hours)
- `pexp_years`: Potential experience (age - education - 6)
- `educ3`: Education level (Low/Medium/High)
- `drgn1`: NUTS1 region code (1-10)
- Region dummies: `reg_2`, `reg_3`, ..., `reg_10`
- Education dummies: `educL`, `educH`

**Command**:
```powershell
python "enh_RURO_prep.py" `
  --processed-dir "U:\EUROMOD-STORAGE\Data\processed\fr\2016" `
  --base-year 2016 `
  --export-format parquet
```

**Expected Runtime**: 1-3 minutes
**Success Indicator**: `singles_RURO_ready.parquet` and `couples_RURO_ready.parquet` created

---

### Step 3: Generate Opportunity Draws (`enh_RURO_draws.py`)

**Purpose**: Generate counterfactual job opportunities (hours, wages) for each individual

**Inputs**:
- `singles_RURO_ready.parquet`
- `couples_RURO_ready.parquet`

**Outputs**:
- `singles_RURO_ready_RURO_draws.parquet` (N_singles × 100 rows)
- `couples_RURO_ready_RURO_draws.parquet` (N_couples × 200 rows)

**Key Features**:
- **99 counterfactual draws** + 1 observed opportunity per person
- **Gender-specific parameters**:
  - π₀ (mass at zero hours): Different for males/females
  - Hours range: [h_min, h_max] uniform distribution
  - Wage specification: Fixed (fw) or variable (vw)
- **Couples**: 2 deciders × 100 draws each = 200 rows per couple
- **Proposal densities**: `log_q_h`, `log_q_w` for importance sampling correction

**Command**:
```powershell
python "enh_RURO_draws.py" `
  --singles-path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready.parquet" `
  --couples-path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready.parquet" `
  --n-draws 99 `
  --wage-spec vw
```

**Parameters**:
- `--wage-spec vw`: Variable wages (default)
- `--wage-spec fw`: Fixed wages (use observed wage for all draws)

**Expected Runtime**: 3-7 minutes
**Success Indicator**: Draw files created with correct row counts

---

### Step 4: EUROMOD Simulation (`enh_RURO_euromod.py`)

**Purpose**: Calculate disposable income for all opportunity draws using EUROMOD

**Inputs**:
- `singles_RURO_ready_RURO_draws.parquet`
- `couples_RURO_ready_RURO_draws.parquet`
- `FR_2016.txt` (microdata template for EUROMOD)

**Outputs**:
- `combined_draws_em.parquet` - All draws with disposable income (`ils_dispy`)

**Key Operations**:
1. **Combine singles + couples** into single dataset
2. **Mutate decider variables** (hours, wages) for each draw
3. **Assign unique IDs**: `id_new = id_original × 1000 + draw_id`
4. **Run EUROMOD once** (all draws simultaneously)
5. **Extract disposable income** at household level
6. **Merge back** to draw-level dataset

**Command**:
```powershell
python "enh_RURO_euromod.py" `
  --singles-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready_RURO_draws.parquet" `
  --couples-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet" `
  --microdata-template "U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt" `
  --euromod-root "U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+" `
  --euromod-system FR_2015 `
  --euromod-dataset FR_2016 `
  --scenario-dir "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016"
```

**Expected Runtime**: 15-45 minutes (EUROMOD is slow)
**Success Indicator**: `combined_draws_em.parquet` exists with `ils_dispy` column

**IMPORTANT**: This step may exit with code 1 but still succeed. Check for output file existence.

---

### Step 5: Prepare GSUR Data (`enh_prepare_FR_gsur.py`)

**Purpose**: Process Eurostat unemployment rates for opportunity constraints

**Inputs**:
- `FR_gsur.xlsx` - Raw Eurostat data (NUTS1 × year × gender × education)

**Outputs**:
- `FR_gsur_ruro.parquet` - Lookup table with merge keys

**Key Variables**:
- `year`: Calendar year
- `drgn1`: NUTS1 region code (1-10)
- `dgn`: Gender (1=male, 2=female)
- `educ3`: Education level (1=low, 2=medium, 3=high)
- `gsur`: Unemployment rate (0-1)

**Command**:
```powershell
python "enh_prepare_FR_gsur.py" `
  --input "U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur.xlsx" `
  --output-dir "U:\Desktop\Nizam_Hisham\MNL\Data\external"
```

**Expected Runtime**: < 1 minute
**Success Indicator**: `FR_gsur_ruro.parquet` created

**Note**: This step is **optional**. Use `--no-gsur` in Step 6 if GSUR file is unavailable.

---

### Step 6: Build MNL Dataset (`enh_RURO_prep_mnl_basic.py`)

**Purpose**: Create final estimation dataset by merging draws + EUROMOD + GSUR

**Inputs**:
- `singles_RURO_ready_RURO_draws.parquet`
- `couples_RURO_ready_RURO_draws.parquet`
- `combined_draws_em.parquet` (from EUROMOD)
- `FR_gsur_ruro.parquet` (optional)

**Outputs**:
- `fr_2016_RURO_mnl.parquet` - Main estimation dataset
- `fr_2016_RURO_mnl__singles.parquet` - Singles subset
- `fr_2016_RURO_mnl__couples.parquet` - Couples subset
- `fr_2016_RURO_mnl__mnlmeta.json` - Metadata (normalization constants, counts)

**Key Operations**:
1. **Merge EUROMOD results** with draws
2. **Restrict to deciders** (heads/partners, exclude children/dependents)
3. **Merge GSUR unemployment** rates by (year, region, gender, education)
4. **Compute consumption**:
   - `cons = ils_dispy / hh_size` (household disposable income per capita)
   - `cons_norm = cons / mean_cons_all` (normalized)
5. **Compute leisure**:
   - `leis = max_hours - hours_ruro` (available leisure time)
   - `leis_norm = leis / max_hours` (normalized to [0,1])
6. **Create estimation variables**:
   - `age_norm = dag - mean(dag)` (demeaned age)
   - `age_norm2 = age_norm²`
   - `n_children = children0_3 + children4_6 + children7_9`
7. **Compute RURO prior density** (log_dens_prior)
8. **Add choice indicator**: `chosen = 1` if draw_id == 0, else 0

**Command**:
```powershell
python "enh_RURO_prep_mnl_basic.py" `
  --singles-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready_RURO_draws.parquet" `
  --couples-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet" `
  --euromod-combined "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016\combined_draws_em.parquet" `
  --gsur-file "U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur_ruro.parquet" `
  --out-base "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl" `
  --wage-spec vw `
  --year 2016 `
  --skip-csv
```

**Parameters**:
- `--skip-csv`: Don't export CSV (parquet only, faster)
- `--no-gsur`: Skip GSUR merge if file unavailable

**Expected Runtime**: 5-10 minutes
**Success Indicator**: Parquet files + JSON metadata created

---

### Step 7: Joint Estimation (`enh_RURO_estimate_FR.py`)

**Purpose**: Estimate RURO model parameters via maximum likelihood (MNL)

**Inputs**:
- `fr_2016_RURO_mnl.parquet` - Estimation dataset
- `estimation_spec.yaml` - Model specification (optional)
- `fr_2016_joint.json` - Initial parameters for warm start (optional)

**Outputs**:
- `fr_2016_joint.json` - Estimated parameters + metadata
- `fr_2016_joint_params.csv` - Parameter table
- `fr_2016_joint_post_estimation.html` - Diagnostics report

**Model Structure** (Variable Wages):

**Total Parameters: 60**

1. **Group-Specific Preferences (34 params)**:
   - Single males (9): β_l0, β_l_age_norm, β_l_age_norm2, β_l_n_children, β_l_educL, β_l_educH, β_c, θ_l, θ_c
   - Single females (9): Same structure
   - Couples (16): Male leisure (6) + Female leisure (6) + Shared (4)

2. **Gender-Shared Opportunity (26 params)**:
   - **Hours opportunity** (14 params):
     - Males (7): β_work, β_pt1, β_pt2, β_ft, β_gsur, β_work_educL, β_work_educH
     - Females (7): Same structure
   - **Wage opportunity** (12 params, vw only):
     - Males (6): β0, β_educL, β_educH, β_pexp, β_pexp2, σ
     - Females (6): Same structure

**Command**:
```powershell
python "enh_RURO_estimate_FR.py" `
  --mnl-file "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl.parquet" `
  --joint `
  --wage-spec vw `
  --optimizer L-BFGS-B `
  --maxiter 5000 `
  --use-numba `
  --n-jobs 8 `
  --post-estimation `
  --out-file "U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\2016\fr_2016_joint.json" `
  --init-params "U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\2016\fr_2016_joint.json"
```

**Parameters**:
- `--joint`: Joint estimation (singles + couples simultaneously)
- `--wage-spec vw`: Variable wages (use `fw` for fixed wages)
- `--optimizer L-BFGS-B`: Quasi-Newton method (recommended)
- `--maxiter 5000`: Maximum iterations (typically converges < 100)
- `--use-numba`: JIT compilation (10x speedup)
- `--n-jobs 8`: Parallel workers (set to CPU core count)
- `--post-estimation`: Generate diagnostics report
- `--init-params`: Warm start from previous estimation (optional)

**Expected Runtime**: 5-20 minutes (with warm start: 1-5 minutes)
**Success Indicator**: JSON file created with `"converged": true`

**Convergence Criteria**:
- Gradient norm < 1e-5
- Function change < 1e-9
- Typical iterations: 50-100 (with warm start: 10-30)

---

## Running the Pipeline

### Method 1: Automated PowerShell Script (Recommended)

The PowerShell runner script executes all 7 steps sequentially with:
- Automatic CPU core detection
- Enhanced logging with timestamps
- Pre-flight checks (virtual environment, imports, file existence)
- Smart skip logic (if intermediate files exist)
- Warm start from previous estimation

**Steps**:

1. **Activate virtual environment**:
   ```powershell
   cd U:\Desktop\Nizam_Hisham\MNL
   .\.venv\Scripts\Activate.ps1
   ```

2. **Run the pipeline**:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\enhanced\run_enhanced_pipeline.ps1
   ```

3. **Monitor progress**:
   - Real-time output with timestamps in console
   - Detailed log saved to `outputs\logs\fr_2016_joint_only_[timestamp].md`

4. **Check results**:
   - Estimation: `outputs\estimates\fr\2016\fr_2016_joint.json`
   - Diagnostics: `outputs\post_estimation\fr\2016\fr_2016_joint_post_estimation.html`

**Configuration** (edit script header):
```powershell
$YEAR = 2016
$N_DRAWS = 99
$WAGE_SPEC = "vw"  # or "fw"
$MAX_ITER = 5000
$SKIP_IF_MNL_EXISTS = $true  # Set to $false to force rebuild
```

---

### Method 2: Manual Step-by-Step Execution

For debugging or partial runs, execute each step manually:

**Activate environment**:
```powershell
cd U:\Desktop\Nizam_Hisham\MNL
.\.venv\Scripts\Activate.ps1
```

**Step 1: Data Prep**
```powershell
python "scripts\enhanced\enh_france_data_prep.py" `
  --year 2016 `
  --raw-dir "U:\EUROMOD-STORAGE\Data\raw" `
  --out-dir "U:\EUROMOD-STORAGE\Data\processed\fr\2016" `
  --system-year 2015 `
  --export-format parquet
```

**Step 2: RURO Prep**
```powershell
python "scripts\enhanced\enh_RURO_prep.py" `
  --processed-dir "U:\EUROMOD-STORAGE\Data\processed\fr\2016" `
  --base-year 2016 `
  --export-format parquet
```

**Step 3: Draws**
```powershell
python "scripts\enhanced\enh_RURO_draws.py" `
  --singles-path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready.parquet" `
  --couples-path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready.parquet" `
  --n-draws 99 `
  --wage-spec vw
```

**Step 4: EUROMOD**
```powershell
python "scripts\enhanced\enh_RURO_euromod.py" `
  --singles-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready_RURO_draws.parquet" `
  --couples-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet" `
  --microdata-template "U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt" `
  --euromod-root "U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+" `
  --euromod-system FR_2015 `
  --euromod-dataset FR_2016 `
  --scenario-dir "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016"
```

**Step 5: GSUR (optional)**
```powershell
python "scripts\enhanced\enh_prepare_FR_gsur.py" `
  --input "Data\external\FR_gsur.xlsx" `
  --output-dir "Data\external"
```

**Step 6: MNL Dataset**
```powershell
python "scripts\enhanced\enh_RURO_prep_mnl_basic.py" `
  --singles-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready_RURO_draws.parquet" `
  --couples-draws "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet" `
  --euromod-combined "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016\combined_draws_em.parquet" `
  --gsur-file "Data\external\FR_gsur_ruro.parquet" `
  --out-base "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl" `
  --wage-spec vw `
  --year 2016 `
  --skip-csv
```

**Step 7: Estimation**
```powershell
python "scripts\enhanced\enh_RURO_estimate_FR.py" `
  --mnl-file "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl.parquet" `
  --joint `
  --wage-spec vw `
  --optimizer L-BFGS-B `
  --maxiter 5000 `
  --use-numba `
  --n-jobs 8 `
  --post-estimation `
  --out-file "outputs\estimates\fr\2016\fr_2016_joint.json"
```

---

## Verifying Success

### Check 1: File Existence

After each step, verify output files exist:

```powershell
# Step 1
Test-Path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016.parquet"

# Step 2
Test-Path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready.parquet"
Test-Path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready.parquet"

# Step 3
Test-Path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready_RURO_draws.parquet"
Test-Path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet"

# Step 4
Test-Path "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016\combined_draws_em.parquet"

# Step 5
Test-Path "U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur_ruro.parquet"

# Step 6
Test-Path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl.parquet"
Test-Path "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl__mnlmeta.json"

# Step 7
Test-Path "U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\2016\fr_2016_joint.json"
```

### Check 2: Row Counts

Verify data integrity with expected row counts:

```python
import pandas as pd

# Step 3: Draws should be N × 100 (singles) or N × 200 (couples)
df_singles = pd.read_parquet("singles_RURO_ready.parquet")
df_singles_draws = pd.read_parquet("singles_RURO_ready_RURO_draws.parquet")
assert len(df_singles_draws) == len(df_singles) * 100

df_couples = pd.read_parquet("couples_RURO_ready.parquet")
df_couples_draws = pd.read_parquet("couples_RURO_ready_RURO_draws.parquet")
assert len(df_couples_draws) == len(df_couples) * 200

# Step 6: MNL dataset should only contain deciders
df_mnl = pd.read_parquet("fr_2016_RURO_mnl.parquet")
assert df_mnl['is_decider'].all()  # All rows are deciders
```

### Check 3: Estimation Convergence

Verify successful optimization:

```python
import json

with open("fr_2016_joint.json", "r") as f:
    results = json.load(f)

# Check convergence
assert results["converged"] == True
assert results["n_iter"] < 5000  # Should converge well before max iterations

# Check log-likelihood
print(f"Log-Likelihood: {results['log_likelihood']}")
print(f"AIC: {results['aic']}")
print(f"BIC: {results['bic']}")

# Check parameter estimates
params = results["parameters"]
print(f"Total parameters: {len(params)}")
```

### Check 4: Diagnostics Report

Open the HTML diagnostics report:

```powershell
# Automatically open in browser
Invoke-Item "U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\2016\fr_2016_joint_post_estimation.html"
```

**Key Metrics to Check**:
- **Convergence status**: Should be "CONVERGED"
- **Gradient norm**: < 1e-5
- **Parameter significance**: Most t-stats > 2
- **Elasticities**: Reasonable magnitudes (0.1 - 1.5 typical)
- **Wage gradients**: Positive for education, concave for experience

---

## Troubleshooting

### Issue 1: Virtual Environment Not Activated

**Symptom**:
```
ERROR: Not running in .venv!
```

**Solution**:
```powershell
cd U:\Desktop\Nizam_Hisham\MNL
.\.venv\Scripts\Activate.ps1
```

If activation fails:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

---

### Issue 2: Missing Raw Data

**Symptom**:
```
MISSING: Raw EUROMOD data - U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt
```

**Solution**:
- Verify EUROMOD data is installed
- Check file path and permissions
- Ensure network drive is mounted (if U:\ is network)

---

### Issue 3: EUROMOD Import Error

**Symptom**:
```
ImportError: No module named 'clr'
```

**Solution**:
```powershell
pip install pythonnet
```

Or if using alternative import method:
```python
# This is handled internally by enh_RURO_euromod.py
# No action needed - script will adapt
```

---

### Issue 4: EUROMOD Step Returns Exit Code 1

**Symptom**:
```
FAILED: Run EUROMOD on all draws (exit code: 1)
```

**Solution**:
This is **often a false alarm**. Check if output file exists:
```powershell
Test-Path "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016\combined_draws_em.parquet"
```

If file exists, the step succeeded despite exit code. The PowerShell script handles this automatically.

---

### Issue 5: Estimation Not Converging

**Symptom**:
```
"converged": false
"n_iter": 5000
```

**Solutions**:

1. **Increase iterations**:
   ```powershell
   --maxiter 10000
   ```

2. **Try different optimizer**:
   ```powershell
   --optimizer BFGS  # Instead of L-BFGS-B
   ```

3. **Use warm start** from previous run:
   ```powershell
   --init-params "outputs\estimates\fr\2016\fr_2016_joint.json"
   ```

4. **Check data quality**:
   ```python
   # Look for NaN or inf values
   import pandas as pd
   df = pd.read_parquet("fr_2016_RURO_mnl.parquet")
   print(df.isna().sum())
   print((df == float('inf')).sum())
   ```

---

### Issue 6: Memory Errors

**Symptom**:
```
MemoryError: Unable to allocate array
```

**Solutions**:

1. **Reduce draws** (if testing):
   ```powershell
   --n-draws 49  # Half the draws
   ```

2. **Use chunked processing** (edit script to process in batches)

3. **Increase virtual memory** (Windows page file)

4. **Use 64-bit Python** (verify with `python -c "import sys; print(sys.maxsize)"`)

---

### Issue 7: Slow Performance

**Solutions**:

1. **Verify Numba is enabled**:
   ```powershell
   --use-numba  # Should be default
   ```

2. **Set parallel workers to CPU count**:
   ```powershell
   --n-jobs 8  # Adjust to your CPU cores
   ```

3. **Disable logging verbosity** (edit scripts to reduce print statements)

4. **Use parquet instead of CSV**:
   ```powershell
   --skip-csv
   ```

---

### Issue 8: GSUR File Missing

**Symptom**:
```
WARNING: GSUR file not found
```

**Solution**:
This is **non-critical**. Use `--no-gsur` flag in Step 6:
```powershell
--no-gsur
```

The model will run without unemployment rate constraints.

---

## Advanced Configuration

### Customizing Model Specification

Edit [`estimation_spec.yaml`](estimation_spec.yaml:1) to modify model structure:

```yaml
model:
  preferences:
    singles_male:
      leisure:
        - "age_norm"      # Add/remove variables
        - "age_norm2"
        - "n_children"
        - "educL"
        - "educH"
      consumption: []

  opportunity:
    hours:
      males:
        - "pt1"           # Part-time categories
        - "pt2"
        - "ft"
        - "gsur"          # Unemployment rate
        - "work_educL"
        - "work_educH"

    wage:
      males:
        - "educL"
        - "educH"
        - "pexp"
        - "pexp2"
```

### Separate Estimation (Non-Joint)

To estimate singles and couples separately:

```powershell
# Single males only
python enh_RURO_estimate_FR.py `
  --mnl-file "fr_2016_RURO_mnl.parquet" `
  --group single_male `
  --wage-spec vw `
  --out-file "fr_2016_single_male.json"

# Single females only
python enh_RURO_estimate_FR.py `
  --mnl-file "fr_2016_RURO_mnl.parquet" `
  --group single_female `
  --wage-spec vw `
  --out-file "fr_2016_single_female.json"

# Couples only
python enh_RURO_estimate_FR.py `
  --mnl-file "fr_2016_RURO_mnl.parquet" `
  --group couple `
  --wage-spec vw `
  --out-file "fr_2016_couple.json"
```

### Fixed vs Variable Wages

**Fixed Wages (fw)**:
- Uses observed wage for all draws
- Faster estimation (fewer parameters)
- Total parameters: 48 (instead of 60)

**Variable Wages (vw)**:
- Estimates wage equation (human capital model)
- More realistic (wages vary with education/experience)
- Total parameters: 60

To switch:
```powershell
--wage-spec fw  # Fixed wages
```

---

## Post-Estimation Analysis

After successful estimation, use the post-estimation script:

```powershell
python "scripts\enhanced\enh_RURO_post_estimation.py" `
  --estimation-file "outputs\estimates\fr\2016\fr_2016_joint.json" `
  --mnl-file "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl.parquet" `
  --output-dir "outputs\post_estimation\fr\2016"
```

**Outputs**:
- `fr_2016_joint_post_estimation.html` - Interactive diagnostics
- `fr_2016_joint_elasticities.csv` - Labor supply elasticities
- `fr_2016_joint_wage_gradients.csv` - Wage equation derivatives
- `fr_2016_joint_predicted_probs.parquet` - Choice probabilities

**Key Diagnostics**:
1. **Parameter estimates**: Values, standard errors, t-statistics
2. **Elasticities**: Own-wage, cross-wage, income elasticities
3. **Wage gradients**: Returns to education, experience
4. **Predicted vs observed**: Choice probability comparisons
5. **Goodness of fit**: Log-likelihood, AIC, BIC, pseudo-R²

---

## References

### Methodology
- Aaberge, R., & Colombino, U. (1998). *Designing Optimal Taxes with a Microeconometric Model of Household Labour Supply*. Memorandum No. 06/1998, Department of Economics, University of Oslo.

### EUROMOD
- Sutherland, H., & Figari, F. (2013). *EUROMOD: The European Union tax-benefit microsimulation model*. International Journal of Microsimulation, 6(1), 4-26.

### Software
- Python: https://www.python.org/
- NumPy: https://numpy.org/
- Pandas: https://pandas.pydata.org/
- SciPy: https://scipy.org/
- Numba: https://numba.pydata.org/

---

## Support

For issues or questions:

1. **Check log file**: `outputs\logs\fr_2016_joint_only_[timestamp].md`
2. **Review diagnostics**: `outputs\post_estimation\fr\2016\fr_2016_joint_post_estimation.html`
3. **Consult troubleshooting** section above
4. **Contact**: [Your contact information]

---

**Last Updated**: 2026-01-03
**Version**: Enhanced Pipeline v2.0
