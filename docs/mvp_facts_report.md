# MVP Facts Report: RURO Estimation Toolkit

**Purpose:** Technical documentation for packaging the RURO (Random Utility Random Opportunity) estimation toolkit as a minimal Python distribution.

**Date:** December 13, 2025
**Scope:** SciPy-based estimation engines (RURO + baseline MNL models)
**Exclusions:** Biogeme and GAMSPy backends (documented but not in MVP)

---

## Table of Contents

1. [Current Run Commands](#1-current-run-commands)
2. [Optimizer Stack](#2-optimizer-stack)
3. [Data Schema](#3-data-schema)
4. [Outputs](#4-outputs)
5. [Dependencies](#5-dependencies)
6. [Numba Usage](#6-numba-usage)
7. [Entry Points](#7-entry-points)
8. [What's Missing for Packaging](#8-whats-missing-for-packaging)

---

## 1. Current Run Commands

### 1.1 RURO Estimation (Main Model)

**File:** `scripts/RURO_estimate_FR.py`

#### Single Group Estimation
```bash
# Single males with variable wages
python scripts/RURO_estimate_FR.py \
  --mnl-file path/to/fr_2016_RURO_mnl.parquet \
  --group 1 --sex m --wage-spec vw \
  --optimizer L-BFGS-B --maxiter 2000 \
  --use-numba --n-jobs 64 \
  --out-file outputs/estimates/fr/2016/fr_2016_single_m_vw.json

# Single females with fixed wages
python scripts/RURO_estimate_FR.py \
  --mnl-file path/to/fr_2016_RURO_mnl.parquet \
  --group 1 --sex f --wage-spec fw \
  --optimizer L-BFGS-B --maxiter 2000 \
  --out-file outputs/estimates/fr/2016/fr_2016_single_f_fw.json

# Couples
python scripts/RURO_estimate_FR.py \
  --mnl-file path/to/fr_2016_RURO_mnl.parquet \
  --group 10 --wage-spec vw \
  --optimizer L-BFGS-B --maxiter 2000 \
  --use-numba --n-jobs 64 \
  --out-file outputs/estimates/fr/2016/fr_2016_couples_vw.json
```

**Reference:** Lines 69-83 (usage examples in docstring)

#### Joint Estimation (All Groups Simultaneously)
```bash
python scripts/RURO_estimate_FR.py \
  --mnl-file path/to/fr_2016_RURO_mnl.parquet \
  --joint --wage-spec vw \
  --optimizer L-BFGS-B --maxiter 2000 \
  --use-numba --n-jobs 64 \
  --post-estimation \
  --out-file outputs/estimates/fr/2016/fr_2016_joint.json
```

**Reference:** `scripts/run_fr_2016_joint_only.ps1:382-391` (PowerShell wrapper)

**Key Parameters:**
- `--group`: 1 (singles) or 10 (couples)
- `--sex`: m (male), f (female), or pooled (default for singles)
- `--wage-spec`: fw (fixed wages, fewer params) or vw (variable wages, wage opportunity model)
- `--optimizer`: L-BFGS-B (default), BFGS, trust-constr, SLSQP, Nelder-Mead
- `--maxiter`: Maximum iterations (500-2000, default 500)
- `--use-numba`: Enable Numba JIT compilation (30x speedup for log-likelihood)
- `--n-jobs`: Number of parallel jobs for joint estimation
- `--post-estimation`: Run post-estimation diagnostics after convergence
- `--init-params`: Path to JSON file with initial parameter values

### 1.2 Baseline MNL: Translog Utility (SciPy)

**File:** `scripts/RUM/MLE_dcm.py`

```bash
# Male estimation
python scripts/RUM/MLE_dcm.py --gender male --include-ascs --robust-se

# Female estimation
python scripts/RUM/MLE_dcm.py --gender female --include-ascs --robust-se

# With centering and scaling
python scripts/RUM/MLE_dcm.py --gender male \
  --center-logs --y-scale 1000.0 \
  --include-ascs --robust-se
```

**Reference:** Lines 300-308 (CLI argument parser)

**Key Parameters:**
- `--gender`: male or female (required)
- `--labels`: Scenario labels (default: h0, h1, ..., h6)
- `--include-ascs`: Include alternative-specific constants (ASCs)
- `--center-logs`: Center log(y) and log(l) at sample mean
- `--y-scale`: Scaling factor for consumption (default: 1.0)
- `--robust-se`: Compute sandwich standard errors (slow, optional)

**Output Location:** `reports/mle_dcm/{gender}_{variant}/`

### 1.3 Baseline MNL: Box-Cox Utility (SciPy)

**File:** `scripts/RUM/DCM1_boxcox.py`

```bash
# Gender-specific estimation
python scripts/RUM/DCM1_boxcox.py --genders male --include-ascs
python scripts/RUM/DCM1_boxcox.py --genders female --include-ascs

# Pooled estimation with gender shifters
python scripts/RUM/DCM1_boxcox.py --pooled --include-ascs

# Pooled with gender-split parameters
python scripts/RUM/DCM1_boxcox.py --pooled --gender-split --include-ascs

# Advanced: gender-split parameters + gender-specific Z shifters
python scripts/RUM/DCM1_boxcox.py --pooled --gender-split --z-by-gender --include-ascs

# Custom consumption scale quantile
python scripts/RUM/DCM1_boxcox.py --pooled --c-scale-quantile 0.95
```

**Reference:** Lines 1191-1220 (CLI argument parser)

**Key Parameters:**
- `--genders`: male, female, or both (default: both)
- `--pooled`: Estimate pooled model with gender indicator
- `--gender-split`: Use gender-specific Box-Cox parameters (alpha/beta)
- `--z-by-gender`: Also split Z shifters (delta_*) by gender
- `--include-ascs`: Include alternative-specific constants
- `--c-scale-quantile`: Quantile for consumption normalization (default: 0.99)
- `--gender-column`: Column name for gender indicator (default: dgn)
- `--data-dir`: Input directory (default: Data/processed/scenarios/)
- `--output-dir`: Output directory (default: reports/mle_dcm/boxcox/)

**Output Location:** `reports/mle_dcm/boxcox/{gender}_{variant}/`

### 1.4 Baseline MNL: Biogeme Backend (Optional)

**File:** `scripts/RUM/DCM1.py`

```bash
# Estimate both genders with Biogeme
python scripts/RUM/DCM1.py

# Male only
python scripts/RUM/DCM1.py --genders male

# Custom output directory
python scripts/RUM/DCM1.py --output-dir reports/custom_biogeme
```

**Reference:** Lines 56-66 (usage examples in docstring)

**Note:** Requires `biogeme>=3.2` (optional dependency in `pyproject.toml:36`)

### 1.5 Baseline MNL: GAMSPy Backend (Optional)

**File:** `scripts/RUM/DCM2_gamspy.py`

**Note:** Uses GAMSPy library with external solvers (knitro, ipopth, conopt). Not currently in `pyproject.toml`. Reference: Lines 33-34, 49-53.

### 1.6 Pipeline Orchestration (PowerShell)

**File:** `scripts/run_fr_2016_joint_only.ps1`

```powershell
# Run full pipeline (data prep + estimation)
powershell -ExecutionPolicy Bypass -File .\scripts\run_fr_2016_joint_only.ps1
```

**What it does:**
1. Data preparation (`france_data_prep.py`)
2. RURO preparation (`RURO_prep.py`)
3. Generate counterfactual draws (`RURO_draws.py`)
4. EUROMOD simulation (`RURO_euromod.py`)
5. Prepare GSUR data (`prepare_FR_gsur.py`)
6. Build MNL dataset (`RURO_prep_mnl_basic.py`)
7. Joint estimation (`RURO_estimate_FR.py --joint`)

**Reference:** Lines 22-26, 262-436

**Duration:** ~14 minutes (full pipeline) or ~2-3 minutes (joint estimation only if data exists)

---

## 2. Optimizer Stack

### 2.1 SciPy Backend (MVP Scope)

All three estimation approaches (RURO, translog MNL, Box-Cox MNL) use **SciPy's `minimize` function**.

#### A. RURO Estimation (`RURO_estimate_FR.py`)

**Optimizer Call:**
```python
from scipy.optimize import minimize

result = minimize(
    objective_and_grad,
    theta0,
    method="L-BFGS-B",
    jac=True,  # CRITICAL: analytical gradient provided
    bounds=bounds,
    options={"disp": True, "maxiter": args.maxiter, "ftol": 1e-9, "gtol": 1e-5},
)
```

**Reference:** Lines 5544-5550 (joint estimation), 5938-5944 (singles), 5967-5973 (couples)

**Gradient:**
- **Analytical gradient** computed explicitly (not numerical approximation)
- Returned as second element of tuple from `objective_and_grad` function
- Uses pre-computed gradients via helper functions
- **10-50x faster** than numerical differentiation

**Bounds:**
- Most parameters: unbounded (`(None, None)`)
- Box-Cox powers (theta_c, theta_l): `(0.01, 2.0)` (strictly positive, bounded curvature)
- Wage variance (sigma, sigma_m, sigma_f): `(-10, 30.0)` (practical range for log-normal SD)
- Reference: Lines 5929-5936 (singles), 5957-5964 (couples), 5531-5542 (joint)

**Options:**
- `maxiter`: 500-2000 (default: 500, PowerShell scripts use 2000)
- `ftol`: 1e-9 (function tolerance)
- `gtol`: 1e-5 (gradient tolerance)
- `disp`: True (print iteration updates)

#### B. Baseline MNL: Box-Cox (`DCM1_boxcox.py`)

**Optimizer Call:**
```python
result = minimize(
    negative_log_likelihood,
    theta0,
    args=(data, structure),
    method="L-BFGS-B",
    jac=grad_negative_log_likelihood,  # Analytical gradient function
    bounds=bounds,
    options={"maxiter": 2000, "disp": log_level <= logging.DEBUG},
)
```

**Reference:** Lines 946-954

**Gradient:**
- **Analytical gradient** via `grad_negative_log_likelihood` function
- Computes score matrix (gradients per observation) and sums
- Reference: Lines 861-863 (gradient function definition)

**Bounds:**
- All parameters: unbounded (`(None, None)`)
- Reference: Line 941 (bounds construction)

**Options:**
- `maxiter`: 2000 (hardcoded)
- `disp`: Controlled by log level

#### C. Baseline MNL: Translog (`MLE_dcm.py`)

**Optimizer Call:**
```python
res = minimize(
    fun=lambda th: total_nll(df, spec, th),
    x0=theta0,
    method="L-BFGS-B",
    options=dict(maxiter=1000, disp=True),
)
```

**Reference:** Lines 238-243

**Gradient:**
- **NO explicit gradient** (SciPy uses numerical approximation)
- Slower convergence than RURO/Box-Cox

**Bounds:**
- None specified (unconstrained optimization)

**Options:**
- `maxiter`: 1000 (hardcoded)
- `disp`: True

### 2.2 Biogeme Backend (Optional/Advanced)

**File:** `scripts/RUM/DCM1.py`

**Library:** `biogeme.biogeme` (version >=3.2)

```python
import biogeme.biogeme as bio
import biogeme.models as models
from biogeme.expressions import Beta, Variable

# Build Biogeme database and model
database = db.Database("DCM", df)
prob_model = models.logit(V, avail_dict, chosen)
biogeme_obj = bio.BIOGEME(database, prob_model)
biogeme_obj.modelName = model_name

# Estimate
results = biogeme_obj.estimate()
```

**Reference:** Lines 47-51 (imports)

**Features:**
- Automatic gradient computation
- Built-in robust standard error calculation
- Different parameter and diagnostic reporting
- Requires installation: `pip install biogeme>=3.2`

**In `pyproject.toml`:** Optional dependency under `advanced` extras (line 36)

### 2.3 GAMSPy Backend (Optional/Advanced)

**File:** `scripts/RUM/DCM2_gamspy.py`

**Library:** `gamspy` (not in `pyproject.toml`)

```python
from gamspy import Container, Model, Variable
from gamspy.math import exp as gp_exp, log as gp_log

# Build GAMSPy model
model = Model(
    container,
    name="boxcox_mnl",
    equations=[ll_def],
    problem="NLP",
    sense="max",
    objective=ll_sum,
)

# Solve with external solver
model.solve(solver=solver)  # solver in ['knitro', 'ipopth', 'conopt']
```

**Reference:** Lines 33-34 (imports), 1099-1121 (model construction and solve)

**Solvers:**
- knitro
- ipopth (IPOPT)
- conopt

**Reference:** Lines 49-53 (solver mapping)

**Note:** Requires commercial solver licenses (knitro, conopt) or open-source IPOPT. Not suitable for MVP.

### 2.4 Comparison Summary

| Feature | RURO (SciPy) | Box-Cox MNL (SciPy) | Translog MNL (SciPy) | Biogeme | GAMSPy |
|---------|-------------|-------------------|-------------------|---------|--------|
| **Gradient** | Analytical ✓ | Analytical ✓ | Numerical only | Auto ✓ | Declarative |
| **Bounds** | Selective | Unbounded | Unbounded | Flexible | Flexible |
| **SE Computation** | Post-hoc | Post-hoc | Post-hoc | Built-in | - |
| **Parallelization** | Joblib (joint) | Single-threaded | Single-threaded | Single-threaded | Depends on solver |
| **JIT Acceleration** | Numba (optional) | No | No | No | No |
| **MVP Inclusion** | **YES** | **YES** | **YES** | No (optional) | No (optional) |

---

## 3. Data Schema

### 3.1 RURO MNL Dataset (Long Format)

**File:** Output of `RURO_prep_mnl_basic.py`
**Format:** Parquet (`.parquet`)
**Structure:** One row per (individual, alternative) pair

**Example:** 449,589 rows for France 2016 (11,964 individuals × ~38 alternatives/person on average)

#### Core Identification Columns

| Column | Type | Description | Reference |
|--------|------|-------------|-----------|
| `ruro_id` | string | Individual identifier (unique per person) | Line 525-527 |
| `ruro_group` | int | 1 = singles, 10 = couples | Line 443-455 |
| `alt_id` | int | Alternative identifier (hours category) | - |
| `chosen` | int | 1 if observed choice, 0 otherwise | Line 525-527 |
| `draws` | int | Draw number (0 = observed, 1-99 = counterfactuals) | Line 525-527 |

#### Utility Components

| Column | Type | Description | Reference |
|--------|------|-------------|-----------|
| `ruro_consumption` | float | Net disposable income (from EUROMOD) | Line 184 |
| `ruro_leisure_m` | float | Male leisure hours (T_HOURS - lhw_m) | Line 185 |
| `ruro_leisure_f` | float | Female leisure hours (couples only) | Line 268 |

#### Demographics (Individual-Level)

**Singles:**

| Column | Type | Description | Reference |
|--------|------|-------------|-----------|
| `dag` | float | Age in years | Line 186-188 |
| `age_norm` | float | Demeaned age: dag - mean(dag) | Line 186-188 |
| `age_norm2` | float | Squared demeaned age | Line 188 |
| `n_children` | float | Total number of children | Line 190 |
| `educL` | float | Low education dummy | Line 192 |
| `educH` | float | High education dummy | Line 193 |
| `dgn` | float | Gender: 0 = male, 1 = female | - |

**Couples (additional columns with _m and _f suffixes):**

| Column | Type | Description | Reference |
|--------|------|-------------|-----------|
| `dag_m`, `dag_f` | float | Male/female age | - |
| `age_norm_m`, `age_norm_f` | float | Demeaned age by gender | - |
| `age_norm2_m`, `age_norm2_f` | float | Squared demeaned age | - |
| `educL_m`, `educH_m` | float | Male education dummies | Line 706-707 |
| `educL_f`, `educH_f` | float | Female education dummies | Line 723-724 |
| `n_children` | float | Total children (household level) | - |

#### Hours Indicators (Alternative-Level)

| Column | Type | Description | Reference |
|--------|------|-------------|-----------|
| `working` | float | 1{hours > 0} (binary) | Line 196 |
| `working_pt1` | float | 1{hours ≈ 20} (part-time 1) | Line 197 |
| `working_pt2` | float | 1{hours ≈ 30} (part-time 2) | Line 198 |
| `working_ft` | float | 1{hours ≈ 40} (full-time) | Line 199 |

**Couples:** Same columns with `_m` and `_f` suffixes (Lines 695-703, 711-719)

#### Wage Variables (if wage_spec="vw")

| Column | Type | Description | Reference |
|--------|------|-------------|-----------|
| `log_wage` | float | Log of hourly wage draw | Line 200 |
| `pexp` | float | Potential experience (age - education - 6) | Line 201 |
| `pexp2` | float | Potential experience squared | Line 202 |

**Couples:** `log_wage_m`, `log_wage_f`, `pexp_m`, `pexp_f`, `pexp2_m`, `pexp2_f`

#### Opportunity Variables

| Column | Type | Description | Reference |
|--------|------|-------------|-----------|
| `gsur` | float | Group-specific unemployment rate | Line 201, 468 |
| `log_prior` | float | Log of proposal density (for importance sampling) | - |

**Couples:** `gsur_m`, `gsur_f` (Lines 714-716, 731-733)

#### Normalization Constants

Referenced in code but used for normalization, not estimation:

| Constant | Value | Description | Reference |
|----------|-------|-------------|-----------|
| `TOTAL_LEISURE_HOURS` | 80.0 | Total available weekly hours | Line 156 |
| `MEAN_DISPY_NORM` | 2500.0 | Consumption normalization | Line 157 |
| `MEAN_LHW_NORM` | 35.0 | Leisure normalization | Line 158 |

**Reference:** `scripts/RURO_estimate_FR.py`, lines 156-158

### 3.2 Baseline MNL Dataset (Wide Format)

**Files:**
- `Data/processed/scenarios/heads_wide_single_male_dcm.parquet`
- `Data/processed/scenarios/heads_wide_single_female_dcm.parquet`

**Format:** Wide format - one row per individual, columns for each alternative

#### Core Columns

| Column | Type | Description | Reference (MLE_dcm) | Reference (DCM1_boxcox) |
|--------|------|-------------|-------------------|----------------------|
| `actual_choice` | string | Observed scenario (h0, h1, ..., h6) | Line 80-86 | Line 194-196 |
| `dag` | float | Age in years | - | Line 219 |
| `num_children_total` | float | Total children | - | Line 222-226 |
| `DCH` | float | Childcare demand dummy | - | Line 227 |
| `dgn` | float | Gender (for pooled models) | - | Line 229-235 |

#### Alternative-Specific Variables (per scenario label)

For each label `{lab}` in (h0, h1, h2, h3, h4, h5, h6):

**Translog Model (MLE_dcm.py):**

| Column Pattern | Type | Description | Reference |
|---------------|------|-------------|-----------|
| `logy_{lab}` | float | Log(consumption) | Line 73-86 |
| `logl_{lab}` | float | Log(leisure) | Line 73-86 |
| `log2y_{lab}` or `logy2_{lab}` | float | (log y)² | Line 92-97 |
| `log2l_{lab}` or `logl2_{lab}` | float | (log l)² | Line 92-97 |
| `logyl_{lab}` | float | log y × log l | Line 100 |
| `Leila_{lab}` | float | log l × log age | Line 100 |
| `Leila2_{lab}` | float | (log l × log age)² | Line 100 |
| `lochi_{lab}` | float | Log(childcare cost) or related | Line 100 |
| `logdc_{lab}` | float | Log(disutility cost) or travel cost | Line 100 |
| `avail_{lab}` | float | Availability (1=available, 0=not) | Line 204-208 |

**Box-Cox Model (DCM1_boxcox.py):**

| Column Pattern | Type | Description | Reference |
|---------------|------|-------------|-----------|
| `consumption_{lab}` | float | Net income (raw, not logged) | Line 199-200 |
| `lhw_{lab}` | float | Labor hours worked | Line 201 |
| `avail_{lab}` | float | Availability | Line 203-209 |

**Note:** Box-Cox model computes normalized consumption/leisure internally:
- `C_norm = clip(consumption / y_ref, eps, 1.0)` where `y_ref` is 99th percentile (default)
- `L_norm = clip((T_HOURS - lhw) / T_HOURS, eps, 1.0)` where `T_HOURS = 80.0`

**Reference:** Lines 214-217 (normalization)

### 3.3 Column Presence by Model

| Model | Format | Key Columns | Notes |
|-------|--------|-------------|-------|
| RURO | Long | ruro_id, ruro_consumption, ruro_leisure_*, age_norm, n_children, educL/H, working*, gsur, log_wage (if vw) | Must include ALL alternatives per individual |
| Translog MNL | Wide | actual_choice, logy_*, logl_*, log2y_*, log2l_*, logyl_*, Leila_*, avail_* | Pre-computed logs and interactions |
| Box-Cox MNL | Wide | actual_choice, consumption_*, lhw_*, avail_*, dag, num_children_total, DCH | Raw values (Box-Cox transform applied in code) |

---

## 4. Outputs

### 4.1 Estimation Results (JSON)

**Primary Output:** JSON file with parameter estimates and diagnostics

**Written by:**
- RURO: `scripts/RURO_estimate_FR.py`, lines 5634, 5694, 6097 (`json.dump`)
- Box-Cox MNL: `scripts/RUM/DCM1_boxcox.py`, line 1173 (`write_parameter_metadata`)
- Translog MNL: `scripts/RUM/MLE_dcm.py`, line 415 (`meta_path.write_text`)

#### Structure (RURO Example)

```json
{
  "model_type": "ruro_joint",
  "wage_spec": "vw",
  "group_config": {...},
  "param_names": ["SM.pref.beta_l0", "SM.pref.beta_c", ...],
  "theta": [0.123, 1.456, ...],
  "std_errors": [0.012, 0.045, ...],
  "varcov": [[...], [...], ...],
  "log_likelihood": -123456.78,
  "convergence": {
    "success": true,
    "message": "Optimization terminated successfully",
    "nit": 143,
    "nfev": 156
  },
  "diagnostics": {
    "aic": 247153.56,
    "bic": 248012.34,
    "n_params": 60,
    "n_obs": 449589
  },
  "estimation_time_seconds": 127.45,
  "timestamp": "2025-12-13T14:32:11"
}
```

**Location:**
- RURO: `outputs/estimates/{country}/{year}/{prefix}.json`
- Baseline MNL: `reports/mle_dcm/{model}/{gender}_{variant}/{model_name}_meta.json`

### 4.2 Parameter Tables (CSV)

**Written by:**
- Box-Cox MNL: Line 1178 (`param_df.to_csv`)
- Translog MNL: Line 402 (`pd.DataFrame(rows).to_csv`)

**Structure:**

| Name | Value | StdErr | t | p | RobustSE | Robust t | Robust p |
|------|-------|--------|---|---|----------|----------|----------|
| beta_l0 | 0.123 | 0.012 | 10.25 | 0.000 | 0.015 | 8.20 | 0.000 |
| beta_c | 1.456 | 0.045 | 32.36 | 0.000 | 0.052 | 28.00 | 0.000 |
| ... | ... | ... | ... | ... | ... | ... | ... |

**Location:**
- RURO: Not generated (JSON only)
- Box-Cox MNL: `reports/mle_dcm/boxcox/{gender}_{variant}/{model_name}_parameters.csv`
- Translog MNL: `reports/mle_dcm/{gender}_{variant}/{base_name}_parameters.csv`

### 4.3 Confusion Matrices (CSV)

**Written by:** Box-Cox MNL only

```csv
predicted,h0,h1,h2,h3,h4,h5,h6
h0,1234,45,12,3,0,0,0
h1,67,2345,123,45,12,0,0
...
```

**Reference:** `scripts/RUM/DCM1_boxcox.py:1176` (`cm.to_csv`)

**Location:** `reports/mle_dcm/boxcox/{gender}_{variant}/{model_name}_confusion.csv`

### 4.4 Post-Estimation Diagnostics

**Generated by:**
- RURO: `scripts/RURO_post_estimation.py` (if `--post-estimation` flag used)
- Box-Cox MNL: Built-in (always generated)

#### Diagnostic Plots (PNG)

**RURO Outputs (if `--post-estimation`):**
- `{wage_spec}_{sex}_muc.png` - Marginal Utility of Consumption
- `{wage_spec}_{sex}_mul.png` - Marginal Utility of Leisure
- `{wage_spec}_{sex}_mrs.png` - Marginal Rate of Substitution
- `{wage_spec}_{sex}_param_significance.png` - Parameter visualization

**Location:** `outputs/post_estimation/{country}/{year}/{group}/`

**Box-Cox MNL:**
- Generates MUC/MUL draws CSV: `{model_name}_mucmul_draws.csv` (Line 1179)
- Generates MUC/MUL summary JSON: `{model_name}_mucmul_summary.json` (Line 1182)

**Reference:** Lines 1178-1182 (Box-Cox), post-estimation script for RURO

#### HTML Reports (RURO only)

If post-estimation enabled:
- `{wage_spec}_{sex}_post_estimation_report.html` - Comprehensive diagnostic report

**Note:** HTML generation requires matplotlib (optional dependency)

### 4.5 Metadata Files (JSON)

#### Parameter Labels

```json
{
  "beta_l0": "Baseline leisure coefficient",
  "beta_c": "Consumption coefficient",
  "theta_l": "Box-Cox power (leisure)",
  ...
}
```

**Written by:** Box-Cox MNL (Line 1185), Translog MNL (Line 420)

**Location:** `{output_dir}/{model_name}_param_labels.json`

#### Parameter Descriptions

```json
{
  "beta_l0": "Baseline leisure slope before shifters.",
  "beta_c": "Marginal utility level for consumption.",
  ...
}
```

**Written by:** Box-Cox MNL (Line 1186), Translog MNL (Line 421-428)

**Location:** `{output_dir}/{model_name}_param_descriptions.json`

### 4.6 Log Files (PowerShell Pipeline)

**Generated by:** `scripts/run_fr_2016_joint_only.ps1`

**Format:** Markdown (`.md`)

**Location:** `outputs/logs/fr_{year}_joint_only_{timestamp}.md`

**Contents:**
- Configuration summary
- Execution timestamps and durations for each step
- Command outputs (stdout/stderr)
- Success/failure status

**Reference:** Lines 66-69, 110-132 (log setup)

### 4.7 Output Directory Structure

```
outputs/
├── estimates/
│   └── fr/
│       └── 2016/
│           ├── fr_2016_single_m_vw.json
│           ├── fr_2016_single_f_vw.json
│           ├── fr_2016_couples_vw.json
│           └── fr_2016_joint.json
│
├── post_estimation/
│   └── fr/
│       └── 2016/
│           ├── single_m/
│           │   ├── vw_m_muc.png
│           │   ├── vw_m_mul.png
│           │   ├── vw_m_mrs.png
│           │   └── vw_m_post_estimation_report.html
│           └── joint/
│               └── ...
│
└── logs/
    └── fr_2016_joint_only_2025-12-13_14-32-11.md

reports/
└── mle_dcm/
    ├── boxcox/
    │   ├── male_ascsOFF_q99/
    │   │   ├── boxcox_male_ascsOFF_q99_parameters.csv
    │   │   ├── boxcox_male_ascsOFF_q99_confusion.csv
    │   │   ├── boxcox_male_ascsOFF_q99_meta.json
    │   │   ├── boxcox_male_ascsOFF_q99_mucmul_draws.csv
    │   │   └── boxcox_male_ascsOFF_q99_mucmul_summary.json
    │   └── pooled_genderSplit/
    │       └── ...
    └── male_ascsOFF/
        ├── mle_male_ascsOFF_parameters.csv
        ├── mle_male_ascsOFF_transform_meta.json
        ├── mle_male_ascsOFF_param_labels.json
        └── mle_male_ascsOFF_param_descriptions.json
```

---

## 5. Dependencies

### 5.1 Core Dependencies (Required)

From `pyproject.toml:12-21`:

```toml
[project]
dependencies = [
    "numpy>=1.24",
    "pandas>=2.0",
    "pyarrow>=14.0",
    "scikit-learn>=1.4",
    "statsmodels>=0.14",
    "pylogit>=0.2.6",
    "pyyaml>=6.0",
    "tqdm>=4.65",
]
```

**Runtime Imports:**

| Package | Used In | Purpose | Import Location |
|---------|---------|---------|----------------|
| `numpy` | All | Array operations, numerical computing | RURO:128, MLE_dcm:27, DCM1_boxcox:28 |
| `pandas` | All | Data manipulation, I/O | RURO:129, MLE_dcm:28, DCM1_boxcox:29 |
| `scipy` | All | `minimize` optimizer, `logsumexp` | RURO:130, MLE_dcm:29-30, DCM1_boxcox:30-31 |
| `pyarrow` | Data prep | Parquet file I/O (via pandas) | Implicit (pandas backend) |
| `pyyaml` | Config | YAML config parsing (if used) | Not in examined scripts |
| `tqdm` | Pipeline | Progress bars | Not in examined scripts |

**Notes:**
- `scipy` not explicitly listed in `pyproject.toml` but **required** (implied by statsmodels dependency)
- `statsmodels` and `pylogit` not imported in examined scripts (may be used elsewhere)
- `scikit-learn` not imported in examined scripts

### 5.2 Optional Dependencies

#### Development Tools

From `pyproject.toml:24-30`:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "ruff>=0.5",
    "ipykernel>=6.29",
    "mypy>=1.10",
    "pre-commit>=3.7",
]
```

#### Notebooks

From `pyproject.toml:31-34`:

```toml
notebook = [
    "jupyterlab>=4.2",
    "jupyter-book>=0.15",
]
```

#### Advanced Estimators

From `pyproject.toml:35-38`:

```toml
advanced = [
    "biogeme>=3.2",
    "pyblp>=0.12",
]
```

**Used In:** `scripts/RUM/DCM1.py` (Biogeme backend)

#### EUROMOD Integration

From `pyproject.toml:39-41`:

```toml
euromod = [
    "euromod>=0.2",
]
```

**Used In:** Data preparation pipeline (not in estimation scripts)

#### Performance (Undocumented in pyproject.toml)

| Package | Version | Used In | Purpose | Import Location |
|---------|---------|---------|---------|----------------|
| `numba` | Any | RURO (optional) | JIT compilation (30x speedup) | RURO:139-143 |
| `joblib` | Any | RURO (optional) | Parallel gradient computation | RURO:133-137 |
| `matplotlib` | Any | Post-estimation | Plotting diagnostics | RURO_post_estimation:27-32, DCM1_boxcox:Implicit |

**Installation:**
```bash
pip install numba joblib matplotlib
```

**Availability Checks:**

```python
# RURO_estimate_FR.py
try:
    from joblib import Parallel, delayed
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

try:
    from numba import njit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
```

**Reference:** Lines 133-143

**Graceful Degradation:**
- If `numba` not available: Uses pure NumPy (slower but works)
- If `joblib` not available: Sequential gradient computation (slower for joint estimation)
- If `matplotlib` not available: Skips plots, still saves numerical results

### 5.3 Version Constraints

**Verified Constraints:**

| Package | Constraint | Reason | Reference |
|---------|-----------|--------|-----------|
| `numpy` | >=1.24 | Modern array API | pyproject.toml:13 |
| `pandas` | >=2.0 | Pyarrow backend, modern API | pyproject.toml:14 |
| `pyarrow` | >=14.0 | Parquet format compatibility | pyproject.toml:15 |
| `python` | >=3.10 | Type hints (PEP 604: `X \| Y`) | pyproject.toml:11 |

**Implied Constraints:**

| Package | Constraint | Source |
|---------|-----------|--------|
| `scipy` | >=1.11 (estimated) | Uses `minimize` with modern options |
| `numba` | >=0.56 (estimated) | Uses `cache=True, fastmath=True` |

### 5.4 Installation Commands

**Minimal (SciPy backend only):**
```bash
pip install -e .
pip install scipy  # Not in pyproject.toml but required
```

**With performance optimizations:**
```bash
pip install -e .
pip install scipy numba joblib matplotlib
```

**With all optional features:**
```bash
pip install -e ".[dev,notebook,advanced,euromod]"
pip install scipy numba joblib matplotlib
```

---

## 6. Numba Usage

### 6.1 JIT-Compiled Functions

**File:** `scripts/RURO_estimate_FR.py`

Four functions use **Numba's `@njit` decorator** with aggressive optimization flags:

#### Function 1: Box-Cox Transformation

```python
@njit(cache=True, fastmath=True)
def _boxcox_transform_numba(x: np.ndarray, theta: float) -> np.ndarray:
    """Numba-accelerated Box-Cox transformation."""
    n = x.shape[0]
    result = np.empty(n, dtype=np.float64)

    if abs(theta) < 1e-6:  # theta ≈ 0 → log transform
        for i in range(n):
            result[i] = np.log(max(x[i], 1e-8))
    else:
        alpha_inv = 1.0 / theta
        for i in range(n):
            x_clipped = max(x[i], 1e-8)
            result[i] = (x_clipped ** theta - 1.0) * alpha_inv

    return result
```

**Reference:** Lines 1253-1268

**Purpose:** Transform consumption and leisure for utility computation
**Speedup:** ~10x faster than NumPy version for large arrays

#### Function 2: Box-Cox Derivative (w.r.t. theta)

```python
@njit(cache=True, fastmath=True)
def _d_boxcox_dtheta_numba(x: np.ndarray, theta: float) -> np.ndarray:
    """Numba-accelerated derivative of Box-Cox w.r.t. theta."""
    n = x.shape[0]
    result = np.empty(n, dtype=np.float64)

    if abs(theta) < 1e-6:
        for i in range(n):
            ln_x = np.log(max(x[i], 1e-8))
            result[i] = 0.5 * ln_x * ln_x
    else:
        alpha_inv_sq = 1.0 / (theta * theta)
        for i in range(n):
            x_clipped = max(x[i], 1e-8)
            x_alpha = x_clipped ** theta
            ln_x = np.log(x_clipped)
            numerator = theta * x_alpha * ln_x - (x_alpha - 1.0)
            result[i] = numerator * alpha_inv_sq

    return result
```

**Reference:** Lines 1270-1288

**Purpose:** Gradient computation for Box-Cox power parameters (theta_c, theta_l)

#### Function 3: Log-Likelihood Computation

```python
@njit(cache=True, fastmath=True)
def _compute_log_likelihood_numba(
    V: np.ndarray,      # (n_rows,) - deterministic utilities
    is_obs: np.ndarray, # (n_rows,) - bool mask for observed vs draws
) -> float:
    """
    Numba-accelerated log-likelihood computation.

    For each individual i, we have:
      - 1 observed alternative (is_obs=True)
      - K counterfactual draws (is_obs=False)

    We compute:
      LL = Σ_i [V_i,obs - log(Σ_j exp(V_i,j))]

    where j sums over observed + all draws.
    """
    n = V.shape[0]
    ll = 0.0
    i = 0

    while i < n:
        # Find observed choice for this individual
        if not is_obs[i]:
            i += 1
            continue

        v_obs = V[i]

        # Collect all alternatives for this individual (obs + draws)
        max_v = v_obs
        j = i + 1
        while j < n and not is_obs[j]:
            if V[j] > max_v:
                max_v = V[j]
            j += 1

        # Compute log-sum-exp with numerical stability
        sum_exp = 0.0
        sum_exp += np.exp(v_obs - max_v)
        for k in range(i + 1, j):
            sum_exp += np.exp(V[k] - max_v)

        # Add contribution to log-likelihood
        ll += v_obs - (max_v + np.log(sum_exp))

        # Move to next individual
        i = j

    return ll
```

**Reference:** Lines 1345-1390 (simplified here for clarity)

**Purpose:** Compute total log-likelihood across all individuals
**Speedup:** **~30x faster** than pure NumPy version

**Why faster?**
- Explicit loop with minimal overhead
- In-place computation without temporary arrays
- Compiler optimizations (`fastmath=True`)

#### Function 4: Gradient Computation

```python
@njit(cache=True, fastmath=True)
def _compute_softmax_gradient_numba(
    V: np.ndarray,        # (n_rows,) - utilities
    is_obs: np.ndarray,   # (n_rows,) - observation mask
    dV_dtheta: np.ndarray # (n_rows, n_params) - partial derivatives
) -> np.ndarray:
    """
    Numba-accelerated gradient of log-likelihood.

    Returns: (n_params,) - gradient vector
    """
    n_rows, n_params = dV_dtheta.shape
    grad = np.zeros(n_params, dtype=np.float64)

    i = 0
    while i < n_rows:
        if not is_obs[i]:
            i += 1
            continue

        v_obs = V[i]

        # Find all alternatives for this individual
        j = i + 1
        while j < n_rows and not is_obs[j]:
            j += 1

        # Compute softmax probabilities
        max_v = v_obs
        for k in range(i, j):
            if V[k] > max_v:
                max_v = V[k]

        sum_exp = 0.0
        for k in range(i, j):
            sum_exp += np.exp(V[k] - max_v)

        probs = np.empty(j - i, dtype=np.float64)
        for k in range(i, j):
            probs[k - i] = np.exp(V[k] - max_v) / sum_exp

        # Compute gradient contribution
        for p in range(n_params):
            contrib = dV_dtheta[i, p]  # Observed derivative

            # Subtract weighted average of derivatives
            expected = 0.0
            for k in range(i, j):
                expected += probs[k - i] * dV_dtheta[k, p]

            contrib -= expected
            grad[p] += contrib

        i = j

    return grad
```

**Reference:** Lines 1290-1343 (simplified)

**Purpose:** Compute gradient vector for optimizer
**Note:** NOT actually used in final version (NumPy gradient is faster for matrix operations)

### 6.2 Numba Compilation Flags

#### `cache=True`

**Purpose:** Cache compiled machine code to disk for faster subsequent runs

**Cache Location:**
- Linux/Mac: `~/.cache/numba/`
- Windows: `%LOCALAPPDATA%\Numba\numba_cache\`

**Pitfall (Windows UNC Paths):**
If running from network drive (e.g., `\\server\share\project`), Numba may fail to create cache directory.

**Workaround:**
```python
import os
os.environ['NUMBA_CACHE_DIR'] = 'C:/temp/numba_cache'
```

**Or disable caching:**
```python
@njit(fastmath=True)  # Remove cache=True
def my_function(...):
    ...
```

#### `fastmath=True`

**Purpose:** Enable aggressive floating-point optimizations

**Relaxations:**
- Assumes no NaN/Inf values (finite arithmetic only)
- Allows reordering of operations (breaks strict IEEE 754)
- Enables fused multiply-add (FMA) instructions

**Risk:** Slight numerical differences (~1e-12) compared to strict mode

**Safe in this context:** Economic parameters and log-likelihoods are finite and well-behaved

### 6.3 Performance Impact

**Benchmark (RURO estimation, France 2016, 449k rows, 60 params):**

| Configuration | Log-Likelihood Time | Gradient Time | Total Iter Time |
|--------------|-------------------|---------------|----------------|
| Pure NumPy | ~2.5 sec | ~1.2 sec | ~3.7 sec |
| Numba LL only | ~0.08 sec | ~1.2 sec | ~1.3 sec |
| Numba LL + Grad | ~0.08 sec | ~1.5 sec | ~1.6 sec |

**Conclusion:** Use Numba for log-likelihood only (30x speedup). Keep gradient in NumPy (matrix ops are faster).

**Reference:** Lines 86-107 (performance optimization notes in docstring)

### 6.4 Numba Availability Checks

```python
try:
    from numba import njit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

# Later in code:
if NUMBA_AVAILABLE and args.use_numba:
    ll_func = _compute_log_likelihood_numba
else:
    ll_func = _compute_log_likelihood_numpy
```

**Reference:** Lines 139-143, usage throughout estimation functions

**Graceful Degradation:** If Numba not installed, falls back to NumPy (works but slower)

### 6.5 Known Issues

#### Issue 1: First-Run Compilation Delay

**Symptom:** First call to JIT function takes 5-30 seconds

**Cause:** Numba compiles function to machine code on first execution

**Mitigation:** Subsequent calls are instant (cached)

#### Issue 2: UNC Path Cache Failure (Windows)

**Symptom:** `RuntimeError: Cannot create cache directory on network drive`

**Workaround:** Set `NUMBA_CACHE_DIR` to local path or disable caching

**Reference:** Known Numba limitation with Windows network shares

#### Issue 3: Import-Time Overhead

**Symptom:** Slow imports when Numba installed

**Impact:** +1-2 seconds on script startup

**Not an issue:** One-time cost per script execution

---

## 7. Entry Points

### 7.1 Current CLI Entry Points

Currently, all estimators are standalone scripts with `argparse` CLIs:

| Script | Description | Arguments | Entry Pattern |
|--------|-------------|-----------|--------------|
| `RURO_estimate_FR.py` | RURO estimation | 30+ flags | `if __name__ == "__main__": main()` |
| `MLE_dcm.py` | Translog MNL | ~10 flags | `if __name__ == "__main__": main()` |
| `DCM1_boxcox.py` | Box-Cox MNL | ~15 flags | `if __name__ == "__main__": main()` |
| `DCM1.py` | Biogeme MNL | ~5 flags | (Not in MVP) |
| `DCM2_gamspy.py` | GAMSPy MNL | ~10 flags | (Not in MVP) |

**Reference:**
- RURO: Line 6168 (`if __name__ == "__main__"`)
- MLE_dcm: Line 450 (`if __name__ == "__main__"`)
- DCM1_boxcox: Line 1292 (`if __name__ == "__main__"`)

### 7.2 Proposed MVP Entry Points

#### Strategy: Thin Wrappers

Create lightweight wrapper functions that:
1. Accept standardized `config` dict
2. Call existing estimation logic
3. Write outputs to specified directory
4. **Do NOT change numerical behavior**

#### A. RURO Entry Point

```python
# src/mnl/ruro/api.py

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class RUROConfig:
    """Configuration for RURO estimation."""
    mnl_file: Path
    group: int = 1  # 1=singles, 10=couples
    sex: str = "pooled"  # m, f, or pooled
    wage_spec: str = "vw"  # fw or vw
    optimizer: str = "L-BFGS-B"
    maxiter: int = 500
    use_numba: bool = True
    n_jobs: int = 1
    post_estimation: bool = False
    init_params: Optional[Path] = None
    verbose: bool = True

def fit(config: RUROConfig, out_dir: Path) -> dict:
    """
    Estimate RURO model.

    Args:
        config: RURO configuration
        out_dir: Output directory for results

    Returns:
        Dictionary with:
            - theta: Parameter estimates (np.ndarray)
            - param_names: Parameter names (list)
            - std_errors: Standard errors (np.ndarray)
            - varcov: Variance-covariance matrix (np.ndarray)
            - log_likelihood: Final log-likelihood (float)
            - convergence: Convergence info (dict)
            - file_path: Path to JSON output (Path)
    """
    # Import existing estimation logic
    from scripts.RURO_estimate_FR import run_estimation

    # Call with config
    results = run_estimation(
        mnl_file=config.mnl_file,
        group=config.group,
        sex=config.sex,
        wage_spec=config.wage_spec,
        optimizer=config.optimizer,
        maxiter=config.maxiter,
        use_numba=config.use_numba,
        n_jobs=config.n_jobs,
        out_dir=out_dir,
    )

    return results
```

**Location:** `src/mnl/ruro/api.py`

**Refactoring Required:**
- Extract estimation logic from `main()` into `run_estimation()` function
- Keep all numerical code unchanged
- Add `out_dir` parameter to control output location

#### B. Baseline MNL Entry Points

```python
# src/mnl/baseline/translog.py

@dataclass
class TranslogConfig:
    """Configuration for translog MNL estimation."""
    data_file: Path
    gender: str  # "male" or "female"
    labels: Optional[list[str]] = None
    include_ascs: bool = False
    center_logs: bool = False
    y_scale: float = 1.0
    robust_se: bool = False
    maxiter: int = 1000

def fit(config: TranslogConfig, out_dir: Path) -> dict:
    """Estimate translog MNL model."""
    from scripts.RUM.MLE_dcm import estimate_dcm
    # ... call existing logic ...


# src/mnl/baseline/boxcox.py

@dataclass
class BoxCoxConfig:
    """Configuration for Box-Cox MNL estimation."""
    data_file: Path
    gender: str  # "male", "female", or "pooled"
    labels: Optional[list[str]] = None
    include_ascs: bool = False
    gender_split: bool = False
    z_by_gender: bool = False
    c_scale_quantile: float = 0.99
    maxiter: int = 2000

def fit(config: BoxCoxConfig, out_dir: Path) -> dict:
    """Estimate Box-Cox MNL model."""
    from scripts.RUM.DCM1_boxcox import estimate
    # ... call existing logic ...
```

### 7.3 Console Script Entry Points

Add to `pyproject.toml`:

```toml
[project.scripts]
ruro-estimate = "mnl.ruro.cli:main"
mnl-translog = "mnl.baseline.translog_cli:main"
mnl-boxcox = "mnl.baseline.boxcox_cli:main"
```

**Implementation:**

```python
# src/mnl/ruro/cli.py

import argparse
from pathlib import Path
from mnl.ruro.api import RUROConfig, fit

def main():
    parser = argparse.ArgumentParser(description="RURO estimation CLI")
    parser.add_argument("--mnl-file", type=Path, required=True)
    parser.add_argument("--group", type=int, default=1)
    parser.add_argument("--sex", default="pooled")
    parser.add_argument("--wage-spec", default="vw")
    parser.add_argument("--out-dir", type=Path, default=Path("outputs/estimates"))
    # ... other arguments ...

    args = parser.parse_args()

    config = RUROConfig(
        mnl_file=args.mnl_file,
        group=args.group,
        sex=args.sex,
        wage_spec=args.wage_spec,
        # ...
    )

    results = fit(config, args.out_dir)
    print(f"Estimation complete: {results['file_path']}")
    print(f"Log-likelihood: {results['log_likelihood']:.2f}")

if __name__ == "__main__":
    main()
```

### 7.4 Minimal Refactoring Strategy

**Goal:** Create package-ready entry points without changing numerical code

**Steps:**

1. **Extract main logic from scripts:**
   - Move core estimation code from `main()` to reusable functions
   - Keep `main()` as thin CLI wrapper
   - No changes to numerical algorithms

2. **Create API modules:**
   - `src/mnl/ruro/api.py` - RURO wrapper
   - `src/mnl/baseline/translog.py` - Translog MNL wrapper
   - `src/mnl/baseline/boxcox.py` - Box-Cox MNL wrapper

3. **Add console scripts:**
   - Reuse existing CLI argument parsing
   - Thin wrappers that call API functions

4. **Keep scripts/ folder:**
   - Original scripts remain functional
   - Can gradually deprecate in favor of package API

**Testing Strategy:**

```python
# tests/test_api.py

def test_ruro_single_male():
    config = RUROConfig(
        mnl_file=Path("tests/fixtures/test_mnl.parquet"),
        group=1,
        sex="m",
        wage_spec="fw",
        maxiter=10,  # Quick test
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        results = fit(config, Path(tmpdir))

        assert results["convergence"]["success"]
        assert len(results["theta"]) > 0
        assert (Path(tmpdir) / "test_result.json").exists()
```

---

## 8. What's Missing for Packaging

### 8.1 Repository Structure

#### Current State

```
MNL/
├── src/
│   └── mnl/          # Partially implemented
│       ├── __init__.py
│       ├── config.py
│       ├── data/
│       ├── models/
│       ├── pipelines/
│       └── evaluation/
│
├── scripts/          # Standalone scripts (not in package)
│   ├── RURO_estimate_FR.py
│   ├── RURO_post_estimation.py
│   └── RUM/
│       ├── MLE_dcm.py
│       ├── DCM1_boxcox.py
│       └── DCM1.py
│
├── tests/
│   └── test_imports.py  # Minimal
│
├── pyproject.toml    # Exists but incomplete
├── README.md
└── docs/             # This file!
```

#### Target State (MVP)

```
MNL/
├── src/
│   └── mnl/
│       ├── __init__.py
│       ├── ruro/              # NEW
│       │   ├── __init__.py
│       │   ├── api.py         # fit(config, out_dir)
│       │   ├── cli.py         # Console script wrapper
│       │   ├── estimation.py  # Core estimation logic (refactored from scripts)
│       │   └── gradient.py    # Gradient computation
│       │
│       ├── baseline/          # NEW
│       │   ├── __init__.py
│       │   ├── translog.py    # Translog MNL API
│       │   ├── boxcox.py      # Box-Cox MNL API
│       │   ├── translog_cli.py
│       │   └── boxcox_cli.py
│       │
│       ├── data/
│       │   ├── __init__.py
│       │   └── loaders.py     # Parquet/CSV loading utilities
│       │
│       └── utils/
│           ├── __init__.py
│           └── numba_funcs.py # Shared Numba functions
│
├── scripts/          # Keep for backward compatibility
│   └── (unchanged)
│
├── tests/
│   ├── test_imports.py
│   ├── test_ruro_api.py       # NEW
│   ├── test_translog_api.py   # NEW
│   ├── test_boxcox_api.py     # NEW
│   └── fixtures/
│       └── test_data.parquet  # Small test dataset
│
├── .github/
│   └── workflows/
│       └── ci.yml             # NEW - GitHub Actions CI
│
├── pyproject.toml    # UPDATED
├── requirements.txt  # NEW - Frozen dependencies
├── README.md         # UPDATED
└── docs/
    ├── mvp_facts_report.md    # This file
    ├── api.md                 # NEW - API documentation
    └── migration_guide.md     # NEW - Scripts → API migration
```

### 8.2 Packaging Configuration

#### pyproject.toml Additions

**Missing:**

```toml
[project.scripts]
ruro-estimate = "mnl.ruro.cli:main"
mnl-translog = "mnl.baseline.translog_cli:main"
mnl-boxcox = "mnl.baseline.boxcox_cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
mnl = ["py.typed"]
```

**Add scipy to dependencies:**

```toml
[project]
dependencies = [
    "numpy>=1.24",
    "pandas>=2.0",
    "scipy>=1.11",     # ADD THIS
    "pyarrow>=14.0",
    # ... existing ...
]
```

**Document performance extras:**

```toml
[project.optional-dependencies]
performance = [
    "numba>=0.56",
    "joblib>=1.3",
    "matplotlib>=3.7",
]

# Update existing:
dev = [
    "pytest>=7.4",
    "pytest-cov>=4.1",  # ADD
    "ruff>=0.5",
    "ipykernel>=6.29",
    "mypy>=1.10",
    "pre-commit>=3.7",
]
```

### 8.3 Testing Infrastructure

#### Smoke Tests (Required)

```python
# tests/test_smoke.py

def test_import_ruro():
    """Verify RURO module imports without error."""
    from mnl.ruro import api
    assert hasattr(api, 'fit')
    assert hasattr(api, 'RUROConfig')

def test_import_baseline():
    """Verify baseline modules import."""
    from mnl.baseline import translog, boxcox
    assert hasattr(translog, 'fit')
    assert hasattr(boxcox, 'fit')

def test_scipy_available():
    """Verify scipy is installed."""
    import scipy.optimize
    assert hasattr(scipy.optimize, 'minimize')

def test_numba_optional():
    """Numba should be optional (graceful degradation)."""
    try:
        import numba
        assert hasattr(numba, 'njit')
    except ImportError:
        pass  # OK if not installed
```

#### Functional Tests (Recommended)

```python
# tests/test_ruro_fit.py

import tempfile
from pathlib import Path
import pytest
from mnl.ruro.api import RUROConfig, fit

@pytest.fixture
def test_data():
    """Load small test dataset."""
    return Path(__file__).parent / "fixtures" / "test_mnl.parquet"

def test_ruro_fit_basic(test_data):
    """Test basic RURO estimation runs without error."""
    config = RUROConfig(
        mnl_file=test_data,
        group=1,
        sex="m",
        wage_spec="fw",
        maxiter=5,  # Very short for testing
        use_numba=False,  # Avoid JIT compilation overhead
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        results = fit(config, Path(tmpdir))

        # Check structure
        assert "theta" in results
        assert "param_names" in results
        assert "log_likelihood" in results
        assert len(results["theta"]) > 0

def test_ruro_output_files(test_data):
    """Test that output files are created."""
    config = RUROConfig(mnl_file=test_data, maxiter=5)

    with tempfile.TemporaryDirectory() as tmpdir:
        results = fit(config, Path(tmpdir))

        assert results["file_path"].exists()
        assert results["file_path"].suffix == ".json"
```

### 8.4 CI/CD Pipeline

#### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml

name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
          pip install scipy

      - name: Run tests
        run: pytest --cov=src/mnl --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.10'

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install ruff mypy

      - name: Lint with ruff
        run: ruff check src tests

      - name: Type check with mypy
        run: mypy src --ignore-missing-imports
```

### 8.5 Dependency Management

#### requirements.txt (Frozen Versions)

**Generate:**
```bash
pip freeze > requirements.txt
```

**Example:**
```
numpy==1.26.2
pandas==2.1.4
scipy==1.11.4
pyarrow==14.0.1
scikit-learn==1.4.0
statsmodels==0.14.1
pyyaml==6.0.1
tqdm==4.66.1
numba==0.58.1
joblib==1.3.2
matplotlib==3.8.2
```

**Usage:**
```bash
# Reproducible install
pip install -r requirements.txt
```

### 8.6 Documentation

#### Missing Docs

1. **API Reference (`docs/api.md`):**
   - Document `RUROConfig`, `TranslogConfig`, `BoxCoxConfig`
   - Document `fit()` functions for each model
   - Include examples

2. **Migration Guide (`docs/migration_guide.md`):**
   - How to convert scripts/X.py calls to API calls
   - Side-by-side comparison:
     ```bash
     # Old
     python scripts/RURO_estimate_FR.py --mnl-file data.parquet --group 1 --sex m

     # New (CLI)
     ruro-estimate --mnl-file data.parquet --group 1 --sex m

     # New (Python API)
     from mnl.ruro.api import RUROConfig, fit
     config = RUROConfig(mnl_file="data.parquet", group=1, sex="m")
     results = fit(config, out_dir="outputs")
     ```

3. **Installation Guide (`docs/installation.md`):**
   - Minimal install
   - With performance extras
   - With all optional features
   - Troubleshooting (Numba, Windows UNC paths)

### 8.7 Packaging Checklist

- [ ] **Restructure src/ layout**
  - [ ] Create `src/mnl/ruro/` module
  - [ ] Create `src/mnl/baseline/` module
  - [ ] Move numba functions to `src/mnl/utils/numba_funcs.py`

- [ ] **Refactor estimation logic**
  - [ ] Extract `RURO_estimate_FR.main()` → `mnl.ruro.estimation.run_estimation()`
  - [ ] Extract `MLE_dcm.main()` → `mnl.baseline.translog.run_estimation()`
  - [ ] Extract `DCM1_boxcox.main()` → `mnl.baseline.boxcox.run_estimation()`
  - [ ] Verify numerical results unchanged (bit-for-bit comparison)

- [ ] **Create API wrappers**
  - [ ] `src/mnl/ruro/api.py` with `RUROConfig` and `fit()`
  - [ ] `src/mnl/baseline/translog.py` with `TranslogConfig` and `fit()`
  - [ ] `src/mnl/baseline/boxcox.py` with `BoxCoxConfig` and `fit()`

- [ ] **Create CLI wrappers**
  - [ ] `src/mnl/ruro/cli.py`
  - [ ] `src/mnl/baseline/translog_cli.py`
  - [ ] `src/mnl/baseline/boxcox_cli.py`

- [ ] **Update pyproject.toml**
  - [ ] Add `scipy>=1.11` to dependencies
  - [ ] Add `[project.scripts]` console entry points
  - [ ] Add `performance` optional extras (numba, joblib, matplotlib)
  - [ ] Add `pytest-cov` to dev extras

- [ ] **Create tests**
  - [ ] `tests/test_smoke.py` - Import checks
  - [ ] `tests/test_ruro_api.py` - RURO API functionality
  - [ ] `tests/test_translog_api.py` - Translog API functionality
  - [ ] `tests/test_boxcox_api.py` - Box-Cox API functionality
  - [ ] `tests/fixtures/test_data.parquet` - Minimal test dataset

- [ ] **Set up CI/CD**
  - [ ] Create `.github/workflows/ci.yml`
  - [ ] Configure pytest with coverage
  - [ ] Add ruff linting
  - [ ] Add mypy type checking
  - [ ] Test on Linux + Windows, Python 3.10-3.12

- [ ] **Freeze dependencies**
  - [ ] Generate `requirements.txt` with `pip freeze`
  - [ ] Document version constraints

- [ ] **Write documentation**
  - [ ] `docs/api.md` - API reference with examples
  - [ ] `docs/migration_guide.md` - Scripts → API migration
  - [ ] `docs/installation.md` - Installation instructions
  - [ ] Update `README.md` with quickstart

- [ ] **Validation**
  - [ ] Run old scripts, save outputs
  - [ ] Run new API, save outputs
  - [ ] Verify numerical equivalence (max diff < 1e-10)

- [ ] **Release preparation**
  - [ ] Tag version 0.1.0
  - [ ] Write CHANGELOG.md
  - [ ] Test install from tarball: `pip install dist/mnl-0.1.0.tar.gz`

---

## Summary

This report documents all technical facts needed to package the RURO estimation toolkit as a minimal Python distribution. The MVP focuses on the **SciPy backend** (RURO + baseline MNL models) with graceful degradation for optional dependencies.

**Key Findings:**

1. **Three estimation approaches** use SciPy's L-BFGS-B optimizer
2. **Analytical gradients** in RURO and Box-Cox MNL (10-50x faster convergence)
3. **Numba JIT** provides 30x speedup for log-likelihood (optional)
4. **Long vs wide format** data schemas for RURO vs baseline MNL
5. **JSON outputs** with standardized structure
6. **scipy missing** from pyproject.toml (critical dependency)
7. **Minimal refactoring** needed - extract logic from scripts without changing numerical code

**Next Steps:**

1. Create `src/mnl/ruro/` and `src/mnl/baseline/` modules
2. Add API wrappers with standardized `fit(config, out_dir)` interface
3. Add console script entry points
4. Create smoke tests and functional tests
5. Set up CI/CD pipeline
6. Validate numerical equivalence with original scripts

**Timeline Estimate:**

- API wrappers: 2-3 days
- Testing: 1-2 days
- CI/CD setup: 1 day
- Documentation: 1-2 days
- **Total: ~1 week for MVP**

---

**End of Report**
