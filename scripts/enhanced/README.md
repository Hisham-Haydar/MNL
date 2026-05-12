# Enhanced RURO Pipeline - France 2016

This directory contains the complete enhanced RURO (Random Utility Random Opportunity) pipeline for estimating labor supply models using French 2016 data.

## 📁 Directory Contents

### Pipeline Scripts (7 Steps)

1. **[enh_france_data_prep.py](enh_france_data_prep.py)** - Step 1: Data Preparation
   - Converts raw EUROMOD data to analysis-ready format
   - Splits into singles/couples datasets
   - Harmonizes variable names and creates baseline demographics

2. **[enh_RURO_prep.py](enh_RURO_prep.py)** - Step 2: RURO Preparation
   - Creates RURO-ready datasets with baseline variables
   - Generates education, region, and work status variables
   - Computes wages and potential experience

3. **[enh_RURO_draws.py](enh_RURO_draws.py)** - Step 3: Opportunity Draws Generation
   - Generates 99 counterfactual + 1 observed opportunity per person
   - Fully vectorized NumPy implementation
   - Gender-specific parameters (π₀, hours range, wages)

4. **[enh_RURO_euromod.py](enh_RURO_euromod.py)** - Step 4: EUROMOD Simulation
   - Runs EUROMOD tax-benefit microsimulation on all draws
   - Single combined run (all draws at once)
   - Computes household disposable income

5. **[enh_prepare_FR_gsur.py](enh_prepare_FR_gsur.py)** - Step 5: GSUR Data Preparation
   - Processes Eurostat unemployment rates
   - Maps NUTS1 regions to analysis codes
   - Creates lookup table for opportunity constraints

6. **[enh_RURO_prep_mnl_basic.py](enh_RURO_prep_mnl_basic.py)** - Step 6: MNL Dataset Creation
   - Merges draws + EUROMOD results + GSUR data
   - Restricts to deciders (heads/partners)
   - Computes consumption/leisure normalization
   - Creates estimation variables (age_norm, n_children, etc.)
   - Supports both continuous RURO draws and job-choice draws (including `job_id` / `log_q_*` priors)

7. **[enh_RURO_estimate_FR.py](enh_RURO_estimate_FR.py)** - Step 7: Joint Estimation
   - YAML-based model specification
   - Parallel MNL estimation (singles/couples)
   - Post-estimation diagnostics
   - Results export (JSON/CSV/HTML)

### Automation & Runners

- **[run_enhanced_pipeline.ps1](run_enhanced_pipeline.ps1)** - **Main Pipeline Runner**
  - Executes all 7 steps sequentially
  - Automatic CPU core detection
  - Enhanced logging with timestamps
  - Pre-flight checks (venv, imports, files)
  - Smart skip logic for intermediate files
  - Warm start from previous estimation

- **[run_diagnostics.ps1](run_diagnostics.ps1)** - Pre-Estimation Diagnostics
  - Validates data quality before estimation
  - Checks for NaN/inf values
  - Verifies variable distributions

### Estimation Components

- **[estimation_engine.py](estimation_engine.py)** - Core Optimization Engine
  - Log-likelihood computation
  - Gradient calculations
  - Numba JIT compilation for performance

- **[estimation_utils.py](estimation_utils.py)** - Utility Functions
  - Parameter initialization
  - Results formatting
  - Convergence checks

- **[parallel_estimation.py](parallel_estimation.py)** - Parallel Processing
  - Multi-threaded estimation
  - Group-wise parallelization

- **[estimation_spec_parser.py](estimation_spec_parser.py)** - YAML Parser
  - Reads model specifications
  - Validates parameter structure

- **[estimation_spec.yaml](estimation_spec.yaml)** - Model Specification (Variable Wages)
  - Defines preferences structure
  - Specifies opportunity equations
  - 60 parameters total (vw)

- **[estimation_spec_loc_empirical.yaml](estimation_spec_loc_empirical.yaml)** - Alternative Spec
  - Location-empirical wage specification
  - Different wage equation structure

### Post-Estimation Analysis

- **[RURO_post_estimation_styled.py](RURO_post_estimation_styled.py)** - Styled Report Generator (recommended)
  - Model-aware output (regular RURO vs job-choice RURO)
  - Shows estimation source and run configuration metadata
  - Includes identification diagnostics file (`identification_diagnostics.txt`) when present
  - Flags degenerate/near-zero standard errors in parameter tables

- **[enh_RURO_post_estimation.py](enh_RURO_post_estimation.py)** - Post-Estimation Diagnostics
  - Computes elasticities (own-wage, cross-wage, income)
  - Calculates wage gradients
  - Generates predicted probabilities
  - Creates interactive HTML report

- **[diagnostic_consumption_variation.py](diagnostic_consumption_variation.py)** - Consumption-variation identification check
  - Data quality validation
  - Descriptive statistics
  - Variable distribution checks

### Documentation

- **[README.md](README.md)** - This file (directory overview)
- **[../../docs/PIPELINE_ENTRYPOINTS.md](../../docs/PIPELINE_ENTRYPOINTS.md)** - Active entrypoints and canonical commands
  - Full step-by-step guide
  - Prerequisites and setup
  - Detailed command-line syntax
  - Troubleshooting guide
  - Advanced configuration

- **[../../README.md](../../README.md)** - Project quick start
  - Fast setup instructions
  - Common commands
  - Quick troubleshooting

- **[../../docs/RURO_ACTIVE_RESULTS_REGISTRY.md](../../docs/RURO_ACTIVE_RESULTS_REGISTRY.md)** - Current baseline output runs
  - How to interpret results
  - Diagnostics explanation
  - Elasticity calculations

## 🚀 Getting Started

### Quick Start (Recommended)

1. **Activate virtual environment**:
   ```powershell
   cd U:\Desktop\Nizam_Hisham\MNL
   .\.venv\Scripts\Activate.ps1
   ```

2. **Run the complete pipeline**:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\enhanced\run_enhanced_pipeline.ps1
   ```

3. **View results**:
   ```powershell
   Invoke-Item "outputs\post_estimation\fr\2016\fr_2016_joint_post_estimation.html"
   ```

### Detailed Guide

For canonical active commands, see **[../../docs/PIPELINE_ENTRYPOINTS.md](../../docs/PIPELINE_ENTRYPOINTS.md)**.

## 📊 Pipeline Flow

```
Raw Data (FR_2016.txt)
    ↓
[Step 1] enh_france_data_prep.py
    ↓
RURO-ready datasets (singles/couples)
    ↓
[Step 2] enh_RURO_prep.py
    ↓
Baseline variables (wages, education, region)
    ↓
[Step 3] enh_RURO_draws.py
    ↓
Opportunity draws (99 + 1 observed)
    ↓
[Step 4] enh_RURO_euromod.py
    ↓
Disposable income (EUROMOD simulation)
    ↓
[Step 5] enh_prepare_FR_gsur.py (optional)
    ↓
GSUR unemployment rates
    ↓
[Step 6] enh_RURO_prep_mnl_basic.py
    ↓
MNL estimation dataset
    ↓
[Step 7] enh_RURO_estimate_FR.py
    ↓
Estimated parameters + diagnostics
```

## 🎯 Key Features

✅ **Enhanced Performance**
- Fully vectorized NumPy operations
- Numba JIT compilation (10x speedup)
- Parallel processing (automatic CPU detection)
- Single EUROMOD run (all draws combined)

✅ **Robust Error Handling**
- Pre-flight checks (venv, imports, files)
- Automatic validation at each step
- Detailed error messages
- Smart recovery (EUROMOD exit code handling)

✅ **Enhanced Logging**
- Timestamped execution logs
- Real-time progress updates
- Markdown-formatted reports
- Success/failure tracking

✅ **Flexible Configuration**
- YAML-based model specifications
- Multiple wage specs (fw/vw)
- Group-specific estimation
- Warm start support

✅ **Comprehensive Diagnostics**
- Post-estimation HTML reports
- Elasticity calculations
- Wage gradient analysis
- Predicted vs observed comparisons

## 📦 Output Structure

```
outputs\
├── estimates\fr\2016\
│   ├── fr_2016_joint.json           # Estimation results
│   └── fr_2016_joint_params.csv     # Parameter table
├── post_estimation\fr\2016\
│   └── fr_2016_joint_post_estimation.html  # Diagnostics report
└── logs\
    └── fr_2016_enhanced_pipeline_[timestamp].md  # Execution log
```

## 🔧 Configuration

### Server Paths (in run_enhanced_pipeline.ps1)
```powershell
$PROJ_ROOT = "U:\Desktop\Nizam_Hisham\MNL"
$DATA_ROOT = "U:\EUROMOD-STORAGE\Data"
$EUROMOD_ROOT = "U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+"
```

### Model Parameters
```powershell
$YEAR = 2016              # Data year
$N_DRAWS = 99             # Counterfactual draws
$WAGE_SPEC = "vw"         # vw = variable wages, fw = fixed wages
$MAX_ITER = 5000          # Optimizer max iterations
```

## 📖 Documentation Hierarchy

1. **Start here**: [../../README.md](../../README.md) - Project quick start
2. **Active commands**: [../../docs/PIPELINE_ENTRYPOINTS.md](../../docs/PIPELINE_ENTRYPOINTS.md) - Canonical entrypoints
3. **After estimation**: [../../docs/RURO_ACTIVE_RESULTS_REGISTRY.md](../../docs/RURO_ACTIVE_RESULTS_REGISTRY.md) - Baseline result registry
4. **This file**: [README.md](README.md) - Directory overview

## 🆘 Troubleshooting

### Common Issues

1. **Not in virtual environment**: Run `.\.venv\Scripts\Activate.ps1`
2. **EUROMOD exit code 1**: Usually false alarm, check if output file exists
3. **Estimation not converging**: Use warm start (automatic in pipeline script)

For cleanup and current project structure, see [../../docs/RURO_PROJECT_HYGIENE_CLEANUP_RECOMMENDATIONS.md](../../docs/RURO_PROJECT_HYGIENE_CLEANUP_RECOMMENDATIONS.md).

## 🔬 Model Specification

### Total Parameters

- **Variable Wages (vw)**: 60 parameters
  - Preferences: 34 (singles male/female + couples)
  - Hours opportunity: 14 (gender-specific)
  - Wage opportunity: 12 (gender-specific)

- **Fixed Wages (fw)**: 48 parameters
  - Preferences: 34 (same as vw)
  - Hours opportunity: 14 (same as vw)
  - No wage equation

### Estimation Groups

1. **Single Males**: 9 preference + 7 hours + 6 wage = 22 params (vw)
2. **Single Females**: 9 preference + 7 hours + 6 wage = 22 params (vw)
3. **Couples**: 16 preference shared = 16 params (vw)
4. **Joint**: All groups simultaneously = 60 params (vw)

## 📚 References

- Aaberge, R., & Colombino, U. (1998). *Designing Optimal Taxes with a Microeconometric Model of Household Labour Supply*. University of Oslo.
- EUROMOD: https://euromod-web.jrc.ec.europa.eu/

## 📝 Version History

- **v2.0** (2026-01-03): Enhanced pipeline with improved performance and diagnostics
- **v1.0** (2025-12): Initial implementation

---

**For questions or issues**, consult the documentation or check execution logs in `outputs\logs\`

**Version**: Enhanced Pipeline v2.0
**Last Updated**: 2026-01-03
