# CLAUDE.md - AI Assistant Guide for MNL Repository

**Last Updated:** December 7, 2025
**Repository:** Structural Discrete-Choice Modelling Toolkit (MNL)
**Purpose:** Labor supply estimation using the RURO (Random Utility Random Opportunity) framework

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Technology Stack](#technology-stack)
4. [Development Workflows](#development-workflows)
5. [Common Tasks](#common-tasks)
6. [Code Conventions](#code-conventions)
7. [Data Management](#data-management)
8. [Configuration System](#configuration-system)
9. [Testing & Quality](#testing--quality)
10. [Troubleshooting](#troubleshooting)
11. [Key Files Reference](#key-files-reference)

---

## Project Overview

### What This Project Does

This is a **structural labor supply estimation toolkit** for economic research. It estimates how individuals and households make labor supply decisions (hours worked) by:

- Modeling discrete choices using multinomial logit and extensions
- Integrating tax-benefit microsimulation via EUROMOD
- Estimating utility function parameters from microdata
- Computing labor supply elasticities and policy responses

### Primary Framework: RURO

**RURO** (Random Utility Random Opportunity) models labor supply with:
- **Preferences:** How people value consumption vs. leisure
- **Opportunities:** Labor market constraints (job availability, wages)
- **Tax-Benefit System:** Net income calculations via EUROMOD

### Current Focus

- **Country:** France
- **Years:** 2016 (operational), expanding to multi-year
- **Groups:** Single males, single females, couples
- **Parameters:** Up to 100 in joint estimation (variable wages)

---

## Repository Structure

```
/home/user/MNL/
├── src/mnl/                    # Main Python package (reusable modules)
│   ├── data/                   # Data loading and preprocessing
│   │   └── loaders.py         # CSV/TSV readers, panel data prep
│   ├── models/                 # Estimation models
│   │   └── mnl.py             # MultinomialLogit wrapper
│   ├── pipelines/              # Orchestration logic
│   │   └── estimation.py      # run_estimation_pipeline()
│   ├── evaluation/             # Metrics and diagnostics
│   │   └── metrics.py         # log_likelihood, accuracy
│   ├── integration/            # External tool connectors
│   │   └── euromod.py         # EuromodConnector class
│   └── config.py              # Configuration dataclasses
│
├── scripts/                    # CLI entry points (49 Python, 5 PowerShell)
│   ├── RURO_*.py              # RURO pipeline components
│   ├── france_data_prep.py    # Country-specific data prep
│   ├── path_helpers.py        # Path resolution utilities
│   ├── run_fr_2016_pipeline.ps1    # Full pipeline automation
│   ├── run_fr_2016_joint_only.ps1  # Quick joint estimation
│   └── RUM/                   # Alternative estimation approaches
│
├── configs/                    # YAML configuration files
│   └── default.yaml           # Template estimation config
│
├── tests/                      # Pytest test suite
│   └── test_imports.py        # Basic import validation
│
├── notebooks/                  # Jupyter notebooks (exploratory)
│
├── docs/                       # Technical documentation
│   ├── architecture.md        # System design
│   ├── data_catalog.md        # Data provenance tracker
│   └── environment_setup.md   # Installation guide
│
├── EUROMOD/                    # EUROMOD configuration files
│   └── EM3Translation/        # XML parameter files
│
├── RURO/                       # RURO-specific utilities
│   └── scripts/               # Helper scripts
│
├── scratch/                    # Development utilities
│   ├── my_functions.py        # Shared helper functions
│   └── Ruro_estimation_new.Rmd # R reference implementation
│
└── [Documentation Files]       # Root-level markdown guides
    ├── README.md              # Quick start guide
    ├── PIPELINE_SUMMARY.md    # Execution results & timing
    ├── JOINT_ESTIMATION_GUIDE.md  # Parameter reference
    ├── FINAL_STATUS_REPORT.md # Implementation status
    ├── FIXES_SUMMARY.md       # Recent fixes log
    └── QUICK_REFERENCE.md     # Command cheat sheet
```

### External Data Structure (NOT in repository)

```
U:/EUROMOD-STORAGE/Data/
├── raw/                        # Immutable source data
│   └── FR_2016.txt            # EUROMOD microdata
├── interim/                    # Intermediate outputs
│   └── ruro/fr/scenarios_*/   # EUROMOD simulation results
└── processed/                  # Analysis-ready datasets
    └── fr/2016/
        ├── fr_2016_processed.parquet       (11,964 records)
        ├── singles_RURO_ready.parquet      (2,310 singles)
        ├── couples_RURO_ready.parquet      (9,654 couples)
        └── fr_2016_RURO_mnl.parquet        (449,589 choice rows)

outputs/
├── estimates/fr/2016/          # JSON estimation results
├── post_estimation/fr/2016/    # Diagnostic plots and HTML reports
└── logs/                       # Pipeline execution logs
```

---

## Technology Stack

### Core Python

- **Version:** 3.10+ (required for modern type hints)
- **Build:** setuptools + pip editable install (`pip install -e .`)
- **Package Name:** `mnl` (version 0.1.0)

### Data Processing

- **pandas:** 2.0+ (primary data manipulation)
- **numpy:** 1.24+ (numerical computations)
- **pyarrow:** 14.0+ (Parquet file I/O)
- **polars:** 1.34.0 (high-performance alternative)

### Econometric Libraries

- **statsmodels:** 0.14+ (basic MNL estimation)
- **pylogit:** 1.0.1 (discrete choice models)
- **scipy:** 1.16+ (optimization, numerical methods)
- **scikit-learn:** 1.7+ (ML utilities)
- **biogeme:** 3.3.1 (advanced discrete choice - optional)
- **pyblp:** 1.1.2 (BLP estimator - optional)

### Microsimulation

- **euromod:** 0.2.17 (EUROMOD Python bindings)
- **pythonnet:** 3.0.5 (CLR/.NET integration)

### Development Tools

- **pytest:** 8.4+ (testing)
- **ruff:** 0.14 (linting and formatting - replaces flake8, black, isort)
- **mypy:** 1.18 (type checking)
- **pre-commit:** 4.3.0 (automated quality checks)

### Visualization

- **matplotlib:** 3.10+ (plotting)
- **jupyterlab:** 4.4+ (interactive analysis)
- **jupyter-book:** 1.0+ (documentation publishing)

### Configuration

- **PyYAML:** 6.0+ (YAML config files)
- **tqdm:** 4.67+ (progress bars)
- **click:** 8.3+ (CLI building)

---

## Development Workflows

### Initial Setup

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\Activate.ps1  # Windows

# 2. Install package in editable mode
pip install --upgrade pip
pip install -e ".[dev,notebook,advanced,euromod]"

# 3. Install pre-commit hooks
pre-commit install

# 4. Register Jupyter kernel (optional)
python -m ipykernel install --user --name mnl --display-name "MNL"
```

### Running Estimations

#### Option 1: Full Pipeline (from scratch)
```powershell
cd /home/user/MNL
powershell -ExecutionPolicy Bypass -File ./scripts/run_fr_2016_pipeline.ps1
```
- **Duration:** ~14 minutes
- **Runs:** All 7 steps + post-estimation
- **Use when:** Starting from raw data or full rerun needed

#### Option 2: Joint Estimation Only (recommended)
```powershell
powershell -ExecutionPolicy Bypass -File ./scripts/run_fr_2016_joint_only.ps1
```
- **Duration:** ~2-3 minutes
- **Assumes:** MNL dataset already exists
- **Use when:** Tweaking estimation parameters only

#### Option 3: Individual Python Scripts
```bash
# Single group estimation
python scripts/RURO_estimate_FR.py \
  --mnl-file path/to/fr_2016_RURO_mnl.parquet \
  --group 1 --sex m \
  --wage-spec vw \
  --optimizer L-BFGS-B \
  --maxiter 500 \
  --use-numba \
  --out-file outputs/estimates/result.json

# Joint estimation (all groups)
python scripts/RURO_estimate_FR.py \
  --mnl-file path/to/fr_2016_RURO_mnl.parquet \
  --joint \
  --wage-spec vw \
  --optimizer L-BFGS-B \
  --maxiter 500 \
  --use-numba \
  --n-jobs 64 \
  --out-file outputs/estimates/joint.json

# Post-estimation diagnostics
python scripts/RURO_post_estimation.py \
  --results outputs/estimates/result.json \
  --mnl-file path/to/fr_2016_RURO_mnl.parquet \
  --out-dir outputs/post_estimation \
  --wage-spec vw --sex m
```

### Testing & Quality Checks

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/mnl

# Type checking
mypy src

# Linting
ruff check src tests

# Auto-fix linting issues
ruff check src tests --fix

# Format code
ruff format src tests

# Run all pre-commit hooks manually
pre-commit run --all-files
```

---

## Common Tasks

### Task 1: Add a New Feature to Estimation Model

1. **Create module in `src/mnl/models/`**
   ```python
   # src/mnl/models/mixed_logit.py
   from __future__ import annotations

   import pandas as pd
   from typing import Any

   class MixedLogit:
       def __init__(self, data: pd.DataFrame, **kwargs):
           ...

       def fit(self) -> dict[str, Any]:
           ...
   ```

2. **Update `src/mnl/models/__init__.py`**
   ```python
   from .mnl import MultinomialLogit
   from .mixed_logit import MixedLogit

   __all__ = ["MultinomialLogit", "MixedLogit"]
   ```

3. **Add tests in `tests/`**
   ```python
   # tests/test_mixed_logit.py
   from mnl.models import MixedLogit

   def test_mixed_logit_import():
       assert MixedLogit is not None
   ```

4. **Update documentation** in `docs/architecture.md`

### Task 2: Prepare Data for a New Country/Year

```bash
# Step 1: Data preparation
python scripts/france_data_prep.py \
  --year 2021 \
  --raw-dir path/to/raw \
  --out-dir path/to/processed/fr/2021 \
  --system-year 2020 \
  --export-format parquet

# Step 2: RURO preparation
python scripts/RURO_prep.py \
  --processed-dir path/to/processed/fr/2021 \
  --base-year 2021 \
  --export-format parquet

# Step 3-7: Follow pipeline steps (see PIPELINE_SUMMARY.md)
```

### Task 3: Debug Estimation Convergence Issues

1. **Increase verbosity:**
   ```bash
   python scripts/RURO_estimate_FR.py ... --verbose
   ```

2. **Try different optimizers:**
   - Current: `L-BFGS-B` (default, uses analytical gradient)
   - Alternatives: `SLSQP`, `trust-constr`, `Nelder-Mead`, `BFGS`

3. **Adjust iteration limits:**
   ```bash
   --maxiter 1000  # Increase from default 500
   ```

4. **Check initial parameters:**
   - Review `init_params_singles_template.csv`
   - Ensure they're in feasible region

5. **Examine bounds:**
   - Box-Cox parameters: (0.01, 2.0)
   - Wage variance: (0.01, 2.0)
   - Others: unbounded

### Task 4: Generate Post-Estimation Diagnostics

```bash
# After estimation completes
python scripts/RURO_post_estimation.py \
  --results outputs/estimates/fr/2016/fr_2016_joint.json \
  --mnl-file path/to/fr_2016_RURO_mnl.parquet \
  --out-dir outputs/post_estimation/fr/2016/joint \
  --wage-spec vw \
  --sex pooled
```

**Outputs created:**
- `vw_pooled_muc.png` - Marginal Utility of Consumption
- `vw_pooled_mul.png` - Marginal Utility of Leisure
- `vw_pooled_mrs.png` - Marginal Rate of Substitution
- `vw_pooled_param_significance.png` - Parameter visualization
- `vw_pooled_post_estimation_report.html` - Comprehensive HTML report

### Task 5: Add Environment Variables for Path Resolution

Edit your shell profile or set in PowerShell:

```bash
# Linux/Mac (.bashrc or .zshrc)
export MNL_STORAGE_ROOT="/path/to/EUROMOD-STORAGE"
export MNL_DATA_ROOT="/path/to/EUROMOD-STORAGE/Data"
export MNL_EUROMOD_ROOT="/path/to/EUROMOD"

# Windows (PowerShell profile or session)
$env:MNL_STORAGE_ROOT = "U:\EUROMOD-STORAGE"
$env:MNL_DATA_ROOT = "U:\EUROMOD-STORAGE\Data"
```

**Path Resolution Hierarchy** (from `scripts/path_helpers.py`):
1. Environment variables (highest priority)
2. Hardcoded locations (`U:/EUROMOD-STORAGE`)
3. Repository-adjacent (fallback)

---

## Code Conventions

### Python Style (Enforced by Ruff)

- **Line length:** 100 characters
- **Quotes:** Double quotes (`"string"`)
- **Import order:** stdlib → third-party → local
- **Type hints:** Required for public APIs (Python 3.10+ style)
- **Docstrings:** Google style

### Naming Conventions

- **Classes:** `PascalCase` (e.g., `MultinomialLogit`, `EuromodConnector`)
- **Functions/methods:** `snake_case` (e.g., `load_raw_choice_data()`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `DEFAULT_YEAR`, `MAX_ITERATIONS`)
- **Private:** Leading underscore `_internal_function()`

### File Naming

**Python Modules:**
- `snake_case.py` (e.g., `france_data_prep.py`)
- Prefix `RURO_*` for RURO-specific scripts
- Prefix `_*` for internal/helper scripts (e.g., `_cell_sanity.py`)

**Data Files:**
- Pattern: `{country}_{year}_{stage}.{format}`
- Examples: `fr_2016_processed.parquet`, `fr_2016_RURO_mnl.parquet`
- Stages: `raw`, `processed`, `RURO_ready`, `RURO_draws`
- Formats: `.parquet` (preferred), `.csv`, `.txt`

**Output Files:**
- Estimates: `{country}_{year}_{model_type}.json`
- Plots: `{wage_spec}_{sex}_{plot_type}.png`

**Documentation:**
- UPPERCASE for major docs: `README.md`, `PIPELINE_SUMMARY.md`
- lowercase for technical docs: `architecture.md`, `data_catalog.md`

### Type Annotations Example

```python
from __future__ import annotations  # Enable modern type hints

from pathlib import Path
from typing import Any

def load_config(path: str | Path) -> EstimationConfig:
    """Load configuration from YAML file.

    Args:
        path: Path to YAML configuration file.

    Returns:
        Parsed configuration object.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If config format is invalid.
    """
    ...
```

### Docstring Format (Google Style)

```python
def run_estimation_pipeline(
    *,
    config: EstimationConfig,
    save_probabilities_to: Path | None = None
) -> dict[str, float]:
    """Execute the default estimation pipeline end-to-end.

    This function orchestrates data loading, preprocessing, model estimation,
    and evaluation. It follows the pattern:
    load → prepare → estimate → evaluate → save.

    Args:
        config: Typed configuration with data paths and model specs.
        save_probabilities_to: Optional path to save predicted probabilities.
            If None, probabilities are not saved.

    Returns:
        Dictionary of evaluation metrics:
            - log_likelihood: Final log-likelihood value
            - accuracy: Prediction accuracy (0-1)
            - n_observations: Number of observations

    Raises:
        FileNotFoundError: If data file specified in config doesn't exist.
        ValueError: If configuration is invalid or incomplete.

    Example:
        >>> config = EstimationConfig(
        ...     data_path=Path("data/processed/panel.csv"),
        ...     features=["price", "time"],
        ... )
        >>> metrics = run_estimation_pipeline(config=config)
        >>> print(f"Log-likelihood: {metrics['log_likelihood']}")
    """
    ...
```

### Error Handling

**Prefer specific exceptions:**
```python
# Good
if not data_path.exists():
    raise FileNotFoundError(f"Data file not found: {data_path}")

# Bad
if not data_path.exists():
    raise Exception("File not found")
```

**Use custom exceptions for domain errors:**
```python
# In src/mnl/integration/euromod.py
class EuromodConnectorError(Exception):
    """Base exception for EUROMOD connector errors."""
    pass
```

---

## Data Management

### Data Location Principles

1. **NEVER commit data files to Git**
   - `.gitignore` excludes: `.parquet`, `.csv`, `.xlsx`, `.dta`, etc.
   - Only commit: schemas, documentation, summary statistics

2. **External storage structure:**
   - Raw data: `U:/EUROMOD-STORAGE/Data/raw/`
   - Interim: `U:/EUROMOD-STORAGE/Data/interim/`
   - Processed: `U:/EUROMOD-STORAGE/Data/processed/{country}/{year}/`
   - Outputs: `outputs/` in project root (also gitignored)

3. **Document data provenance:**
   - Update `docs/data_catalog.md` for all datasets
   - Include: source, date acquired, processing steps, column definitions

### Data Files in RURO Pipeline

| File | Stage | Records | Purpose |
|------|-------|---------|---------|
| `FR_2016.txt` | Raw | Variable | EUROMOD microdata (source) |
| `fr_2016_processed.parquet` | 1 | 11,964 | Cleaned household data |
| `singles_RURO_ready.parquet` | 2 | 2,310 | Singles with RURO variables |
| `couples_RURO_ready.parquet` | 2 | 9,654 | Couples with RURO variables |
| `*_RURO_draws.parquet` | 3 | × 99 | Monte Carlo wage draws |
| `combined_draws_em.parquet` | 4 | 286,800 | After EUROMOD simulation |
| `fr_2016_RURO_mnl.parquet` | 6 | 449,589 | Final MNL dataset (long format) |

### MNL Dataset Structure

**Long format:** One row per (individual, alternative)

**Key columns:**
- `ruro_id`: Individual identifier (string)
- `ruro_group`: 1 = singles, 10 = couples
- `alt_id`: Alternative identifier (hours category)
- `chosen`: 1 if observed choice, 0 otherwise
- Utility components:
  - `ruro_consumption`: Net disposable income
  - `ruro_leisure_m`, `ruro_leisure_f`: Hours of leisure
- Covariates:
  - Demographics: `dag` (age), `educL`, `educM`, `educH`
  - Region: `reg2`, `reg3`, ..., `reg9`
  - Children: `ch0_3`, `ch4_6`, `ch7_9`
- Opportunity variables:
  - `gsur_probability`: Labor force participation prob
  - Wage draws: `wage_draw_m`, `wage_draw_f`

---

## Configuration System

### YAML Configuration (Template)

Location: `configs/default.yaml`

```yaml
data:
  preprocessed_path: Data/processed/choice_panel.csv

model:
  choice_column: choice
  individual_id_column: individual_id
  alternative_id_column: alternative_id
  weights_column: null
  features:
    - price
    - time
    - distance

output:
  probabilities_path: outputs/probabilities.csv
  model_summary_path: outputs/model_summary.txt
```

### Environment Variables

Set these to customize path resolution:

| Variable | Purpose | Example |
|----------|---------|---------|
| `MNL_STORAGE_ROOT` | Base data/outputs directory | `U:/EUROMOD-STORAGE` |
| `MNL_DATA_ROOT` | Data directory override | `U:/EUROMOD-STORAGE/Data` |
| `MNL_EUROMOD_ROOT` | EUROMOD installation | `C:/EUROMOD` |
| `EUROMOD_RAW` | Raw data directory | `U:/EUROMOD-STORAGE/Data/raw` |
| `MNL_LOCAL_WORKDIR` | Local workspace (UNC workaround) | `C:/temp/mnl` |

### Script-Level Arguments

Most scripts accept command-line arguments via `argparse`:

```bash
python scripts/RURO_estimate_FR.py --help
```

**Common arguments:**
- `--mnl-file`: Path to MNL dataset
- `--group`: 1 (singles) or 10 (couples)
- `--sex`: m (male), f (female), or pooled
- `--wage-spec`: fw (fixed wages) or vw (variable wages)
- `--optimizer`: L-BFGS-B, SLSQP, trust-constr, etc.
- `--maxiter`: Maximum iterations
- `--use-numba`: Enable Numba JIT compilation
- `--n-jobs`: Number of parallel jobs
- `--out-file`: Output JSON file path

---

## Testing & Quality

### Test Structure

```
tests/
├── test_imports.py      # Verify package imports work
├── test_loaders.py      # Test data loading functions
├── test_models.py       # Test estimation models
└── test_pipelines.py    # Test end-to-end pipelines
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_imports.py

# With coverage report
pytest --cov=src/mnl --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Pre-commit Hooks

Configured in `.pre-commit-config.yaml`:

```bash
# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run
```

**Hooks enforce:**
1. Code formatting (ruff)
2. Import sorting (ruff)
3. Type checking (mypy)
4. Test execution (pytest)

### Code Quality Checks

```bash
# Linting
ruff check src tests

# Auto-fix
ruff check src tests --fix

# Format
ruff format src tests

# Type checking
mypy src

# Combined workflow
ruff check src tests --fix && \
ruff format src tests && \
mypy src && \
pytest
```

---

## Troubleshooting

### Issue: Import Errors (`ModuleNotFoundError: No module named 'path_helpers'`)

**Cause:** Scripts run from wrong directory

**Solution:** Scripts must run from `scripts/` directory or use absolute imports

```bash
# Good (from project root)
python scripts/france_data_prep.py ...

# Good (from scripts directory)
cd scripts
python france_data_prep.py ...
```

### Issue: EUROMOD Connection Failed

**Symptoms:** `EuromodConnectorError` or .NET errors

**Solutions:**
1. Check EUROMOD installation exists
2. Verify environment variable: `MNL_EUROMOD_ROOT`
3. Ensure `pythonnet` package installed: `pip install pythonnet`
4. Check EUROMOD version compatibility (tested with 0.2.17)

### Issue: Optimization Not Converging

**Symptoms:** "Maximum iterations reached" or poor log-likelihood

**Solutions:**
1. **Increase iterations:**
   ```bash
   --maxiter 1000  # or 2000
   ```

2. **Try different optimizer:**
   ```bash
   --optimizer BFGS  # or SLSQP, trust-constr
   ```

3. **Check initial parameters:**
   - Review `init_params_singles_template.csv`
   - Ensure they're reasonable starting values

4. **Examine gradient:**
   - Enable verbose output: `--verbose`
   - Check gradient norms in output

5. **Simplify model:**
   - Start with fewer parameters (fixed wages: `--wage-spec fw`)
   - Estimate single groups before joint

### Issue: Memory Errors with Large Datasets

**Solutions:**
1. **Use Polars instead of Pandas:**
   ```python
   import polars as pl
   df = pl.read_parquet("data.parquet")
   ```

2. **Process in chunks:**
   ```python
   for chunk in pd.read_csv("data.csv", chunksize=10000):
       process(chunk)
   ```

3. **Increase swap space** (Linux)

4. **Use 64-bit Python** (Windows)

### Issue: Path Resolution Fails (UNC Paths)

**Symptoms:** "Cannot access UNC path" on Windows

**Solution:** Use `ensure_local_workdir()` from `path_helpers.py`

```python
from path_helpers import ensure_local_workdir

# Creates local copy if on UNC path
local_path = ensure_local_workdir()
```

### Issue: Standard Errors Not Computed

**Symptoms:** "Cannot compute Hessian without gradient function"

**Explanation:** CLI mode post-estimation cannot access gradient function

**Solutions:**
1. **Accept limitation:** Use parameter estimates without SE
2. **Integrate post-estimation:** Call `run_full_post_estimation()` from within estimation script (requires code modification)
3. **Use Biogeme:** Switch to Biogeme estimator which computes SE automatically

### Issue: Git Shows Large Diffs for Data Files

**Cause:** Data files committed by mistake

**Solution:**
```bash
# Remove from Git but keep local
git rm --cached outputs/data.parquet

# Verify .gitignore includes pattern
echo "*.parquet" >> .gitignore

# Commit removal
git add .gitignore
git commit -m "Remove data files from Git tracking"
```

---

## Key Files Reference

### Documentation Files (Root)

| File | Purpose | When to Update |
|------|---------|----------------|
| `README.md` | Quick start guide | Setup changes, major features |
| `PIPELINE_SUMMARY.md` | Execution results & timing | After pipeline runs |
| `JOINT_ESTIMATION_GUIDE.md` | Parameter reference (100 params) | Model changes, new parameters |
| `FINAL_STATUS_REPORT.md` | Implementation status | Major milestones |
| `FIXES_SUMMARY.md` | Recent bug fixes log | After fixing bugs |
| `QUICK_REFERENCE.md` | Command cheat sheet | New commands added |
| `CLAUDE.md` | This file - AI assistant guide | Structure/convention changes |

### Core Python Modules

| File | Purpose | Key Functions/Classes |
|------|---------|----------------------|
| `src/mnl/config.py` | Configuration management | `EstimationConfig` |
| `src/mnl/data/loaders.py` | Data loading | `load_raw_choice_data()`, `prepare_panel_data()` |
| `src/mnl/models/mnl.py` | MNL estimation | `MultinomialLogit` |
| `src/mnl/pipelines/estimation.py` | Pipeline orchestration | `run_estimation_pipeline()` |
| `src/mnl/evaluation/metrics.py` | Metrics | `log_likelihood()`, `prediction_accuracy()` |
| `src/mnl/integration/euromod.py` | EUROMOD connector | `EuromodConnector` |

### Critical Scripts

| File | Purpose | Duration | Use When |
|------|---------|----------|----------|
| `scripts/run_fr_2016_pipeline.ps1` | Full pipeline | ~14 min | Full rerun needed |
| `scripts/run_fr_2016_joint_only.ps1` | Joint estimation only | ~2-3 min | Parameter tuning |
| `scripts/RURO_estimate_FR.py` | Estimation CLI | Varies | Custom estimation |
| `scripts/RURO_post_estimation.py` | Diagnostics | ~3 sec | After estimation |
| `scripts/france_data_prep.py` | Data preparation | ~47 sec | New data |
| `scripts/RURO_prep.py` | RURO preparation | ~19 sec | New RURO dataset |
| `scripts/RURO_draws.py` | Generate draws | ~24 sec | New wage draws |
| `scripts/RURO_euromod.py` | EUROMOD simulation | ~3.5 min | Simulate net income |
| `scripts/RURO_prep_mnl_basic.py` | Build MNL dataset | ~5 min | Create choice dataset |
| `scripts/path_helpers.py` | Path utilities | N/A | Import in other scripts |

### Configuration Files

| File | Purpose | Format |
|------|---------|--------|
| `configs/default.yaml` | Template config | YAML |
| `pyproject.toml` | Python package config | TOML |
| `requirements.txt` | Frozen dependencies | Text |
| `.gitignore` | Git exclusions | Text |
| `.pre-commit-config.yaml` | Pre-commit hooks | YAML |

### Data Files (External - Not in Git)

| File | Records | Purpose |
|------|---------|---------|
| `fr_2016_processed.parquet` | 11,964 | Cleaned household data |
| `singles_RURO_ready.parquet` | 2,310 | Singles with RURO vars |
| `couples_RURO_ready.parquet` | 9,654 | Couples with RURO vars |
| `fr_2016_RURO_mnl.parquet` | 449,589 | Final MNL dataset |

---

## RURO Pipeline Overview

### 7-Step Pipeline

```
Step 1: Data Preparation (france_data_prep.py)           → ~47 sec
  ├─ Input:  FR_2016.txt (raw EUROMOD data)
  └─ Output: fr_2016_processed.parquet (11,964 records)

Step 2: RURO Preparation (RURO_prep.py)                  → ~19 sec
  ├─ Input:  fr_2016_processed.parquet
  └─ Output: singles_RURO_ready.parquet (2,310)
             couples_RURO_ready.parquet (9,654)

Step 3: Generate Draws (RURO_draws.py)                   → ~24 sec
  ├─ Input:  *_RURO_ready.parquet
  └─ Output: *_RURO_draws.parquet (99 draws each)

Step 4: EUROMOD Simulation (RURO_euromod.py)             → ~3.5 min
  ├─ Input:  *_RURO_draws.parquet
  └─ Output: combined_draws_em.parquet (286,800 rows)

Step 5: GSUR Preparation (prepare_FR_gsur.py)            → ~0 sec (cached)
  ├─ Input:  External labor market data
  └─ Output: GSUR probability estimates

Step 6: Build MNL Dataset (RURO_prep_mnl_basic.py)       → ~5 min
  ├─ Input:  combined_draws_em + GSUR + RURO_ready
  └─ Output: fr_2016_RURO_mnl.parquet (449,589 rows)

Step 7: Estimation (RURO_estimate_FR.py)                 → 30s-2min
  ├─ Input:  fr_2016_RURO_mnl.parquet
  └─ Output: JSON parameter estimates
      ├─ 7a: Single Males (--group 1 --sex m)    → 12-37 params
      ├─ 7b: Single Females (--group 1 --sex f)  → 13-37 params
      ├─ 7c: Couples (--group 10)                → 25-76 params
      └─ 7d: Joint (--joint)                     → 68-100 params

Step 8: Post-Estimation (RURO_post_estimation.py)        → ~3 sec
  ├─ Input:  JSON estimates + MNL dataset
  └─ Output: Plots, HTML reports, diagnostics
```

**Total Pipeline Duration:** ~14 minutes

---

## Parameter Structure (Joint Estimation)

### Total Parameters: 100 (variable wages) or 68 (fixed wages)

**Breakdown:**
1. **Group-Specific Preferences** (50 params)
   - Single Males: 12 preference parameters
   - Single Females: 13 preference parameters
   - Couples: 25 preference parameters (male + female + interaction)

2. **Gender-Shared Opportunities** (50 params, vw only)
   - Hours Opportunity Males: 9 parameters
   - Hours Opportunity Females: 9 parameters
   - Wage Opportunity Males: 16 parameters (vw only)
   - Wage Opportunity Females: 16 parameters (vw only)

**See `JOINT_ESTIMATION_GUIDE.md` for complete parameter list and descriptions.**

---

## Best Practices for AI Assistants

### When Working with This Codebase

1. **Read before modifying:** Always read files before editing
2. **Use existing patterns:** Follow established conventions
3. **Update documentation:** Keep markdown docs synchronized
4. **Test changes:** Run pytest after modifications
5. **Check paths:** Use `path_helpers.py` for cross-platform compatibility
6. **Preserve data separation:** Never commit data files
7. **Document decisions:** Update relevant .md files

### Communication Style

- Be concise and technical
- Reference file paths with line numbers: `src/mnl/config.py:42`
- Provide runnable commands in code blocks
- Link to relevant documentation files
- Explain "why" not just "what"

### Preferred Tool Usage

- **File search:** Use Glob tool, not `find`
- **Content search:** Use Grep tool, not `grep` command
- **Read files:** Use Read tool, not `cat`
- **Edit files:** Use Edit tool, not `sed`
- **Run commands:** Use Bash tool for git, npm, python, etc.

### Code Quality Expectations

- Type hints on all public functions
- Google-style docstrings
- Error handling with specific exceptions
- No print statements (use logging)
- Ruff-compliant formatting
- Mypy type checking passes

---

## Additional Resources

### Internal Documentation

- Architecture: `docs/architecture.md`
- Data Catalog: `docs/data_catalog.md`
- Environment Setup: `docs/environment_setup.md`
- Pipeline Summary: `PIPELINE_SUMMARY.md`
- Joint Estimation: `JOINT_ESTIMATION_GUIDE.md`

### External Resources

- EUROMOD: https://euromod-web.jrc.ec.europa.eu/
- Ruff: https://docs.astral.sh/ruff/
- Pytest: https://docs.pytest.org/
- Statsmodels MNL: https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.MNLogit.html

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-07 | 1.0.0 | Initial comprehensive CLAUDE.md created |

---

**For questions or clarifications, consult:**
- README.md for quick start
- QUICK_REFERENCE.md for command reference
- PIPELINE_SUMMARY.md for execution details
- JOINT_ESTIMATION_GUIDE.md for parameter details
