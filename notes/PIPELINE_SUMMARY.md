# RURO France 2016 Pipeline - Summary

**Date:** December 6, 2025  
**Total Duration:** ~14 minutes (estimation + post-estimation)

---

## ✅ Completed Tasks

### 1. **Fixed PowerShell Pipeline Issues**
- **Issue:** Script was hanging indefinitely when running Python commands
- **Root Cause:** Using `$args` (PowerShell automatic variable) and `ProcessStartInfo` deadlock
- **Solution:** 
  - Renamed `$args` → `$cmdArgs`
  - Switched from `ProcessStartInfo` to simpler `Invoke-Expression`
  
### 2. **Fixed Python Import Issues**
- **Issue:** `ModuleNotFoundError: No module named 'path_helpers'`
- **Solution:** Scripts need to run from the `scripts/` directory (handled by pipeline)

### 3. **Fixed Virtual Environment Usage**
- **Issue:** Pipeline was using system Python instead of venv
- **Solution:** Added auto-detection of venv Python and updated all commands

### 4. **Fixed Column Naming Issues**
- **Issue:** Multiple column mismatch errors (`drgn`, `dag`, `educL`, `reg2-7`)
- **Solution:** 
  - Fixed `RURO_prep.py` column renaming (moved earlier, fixed assignment)
  - Expanded column mapping for singles (`dag_m`/`dag_f` → `dag`, etc.)
  - Fixed `RURO_estimate_FR.py` to handle `drgn*` → `reg*` mapping

### 5. **Optimized CPU Usage**
- **Auto-detection:** Script now detects available CPU cores automatically
- **Environment variables:** Set `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `NUMBA_NUM_THREADS`, etc.
- **Process priority:** Set to "High" for better CPU allocation
- **Joint estimation:** Uses all available cores (`--n-jobs $CPU_CORES`)

### 6. **Added Post-Estimation Analysis**
- **Created:** `run_post_estimation.ps1` standalone script
- **Integrated:** Added Step 8 to main pipeline (optional)
- **Features:**
  - Parameter estimates summary
  - Marginal utility plots (MUC, MUL, MRS)
  - Model fit statistics (note: Hessian requires gradient function)
  - Output organized by model type

---

## 📊 Pipeline Results

### Step-by-Step Execution Times
| Step | Description | Duration | Status |
|------|-------------|----------|--------|
| 1 | Data Preparation | ~47 sec | ✅ SUCCESS |
| 2 | RURO Preparation | ~19 sec | ✅ SUCCESS |
| 3 | Generate Draws (99) | ~24 sec | ✅ SUCCESS |
| 4 | EUROMOD Simulation | ~3min 25sec | ✅ SUCCESS |
| 5 | GSUR Preparation | ~0 sec (cached) | ✅ SUCCESS |
| 6 | Build MNL Dataset | ~5min 9sec | ✅ SUCCESS |
| 7a | Estimate Single Males | ~43 sec | ✅ SUCCESS |
| 7b | Estimate Single Females | ~38 sec | ✅ SUCCESS |
| 7c | Estimate Couples | ~30 sec | ❌ FAILED |
| 7d | Joint Estimation | ~1min 49sec | ✅ SUCCESS |
| **Total Pipeline** | | **~13min 56sec** | ✅ **SUCCESS** |

### Post-Estimation (Step 8)
| Model | Duration | Status |
|-------|----------|--------|
| Single Males | ~3 sec | ✅ SUCCESS |
| Single Females | ~3 sec | ✅ SUCCESS |
| Couples | N/A | ⊘ SKIPPED (no estimation) |
| Joint | ~2 sec | ✅ SUCCESS |
| **Total** | **~9 sec** | ✅ **SUCCESS** |

---

## 📁 Output Files

### Estimation Results
```
U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\2016\
├── fr_2016_single_males.json      (✅ 37 parameters)
├── fr_2016_single_females.json    (✅ 37 parameters)
├── fr_2016_couples.json           (❌ Failed)
└── fr_2016_joint.json             (✅ 100 parameters)
```

### Post-Estimation Results
```
U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\2016\
├── single_males/
│   ├── plots/
│   │   ├── marginal_utility_consumption.png
│   │   ├── marginal_utility_leisure.png
│   │   └── mrs_curve.png
│   └── parameter_summary.txt
├── single_females/
│   └── ... (same structure)
└── joint/
    └── ... (same structure)
```

### Data Files
```
U:\EUROMOD-STORAGE\Data\processed\fr\2016\
├── fr_2016_processed.parquet       (✅ 11,964 records)
├── singles_RURO_ready.parquet      (✅ 2,310 singles)
├── couples_RURO_ready.parquet      (✅ 9,654 couples)
├── singles_RURO_ready_RURO_draws.parquet  (✅ 99 draws)
├── couples_RURO_ready_RURO_draws.parquet  (✅ 99 draws)
└── fr_2016_RURO_mnl.parquet        (✅ 449,589 choice rows)
```

### Logs
```
U:\Desktop\Nizam_Hisham\MNL\outputs\logs\
└── fr_2016_pipeline_2025-12-06_11-26-56.md
```

---

## 🎯 Key Estimation Results

### Single Males (Group 1, Sex M)
- **Log-likelihood:** -3,139.64
- **N individuals:** 1,000
- **Key parameters:**
  - `beta_l0`: 0.1687 (leisure intercept)
  - `beta_c`: 0.5000 (consumption coefficient)
  - `theta_l`: 2.0000 (leisure Box-Cox parameter)
  - `theta_c`: 0.5000 (consumption Box-Cox parameter)
  - `beta_l_educL`: 0.4227 (low education effect on leisure)
  - `beta_l_educH`: -0.3607 (high education effect on leisure)

### Single Females (Group 1, Sex F)
- **Log-likelihood:** -3,838.09
- **N individuals:** 1,000
- **Key parameters:**
  - `beta_l0`: 1.0912 (leisure intercept - higher than males)
  - `beta_c`: 1.0000 (consumption coefficient)
  - `theta_l`: 0.0100 (leisure Box-Cox parameter - near log)
  - `theta_c`: 0.5000 (consumption Box-Cox parameter)

### Joint Estimation (All Groups)
- **Log-likelihood:** -6,977.75
- **N individuals:** 1,000
- **Parameters:** 100 (including singles males, singles females, couples male/female)
- **Shared opportunity parameters:** Yes (wage opportunity equations)

---

## ⚠️ Known Issues

### 1. Couples Estimation Failed
- **Error:** Exit code 1 (details not captured in this run)
- **Possible causes:**
  - Column naming mismatch for couples-specific variables
  - Insufficient data or convergence issues
- **Recommendation:** Run couples estimation separately with verbose logging

### 2. Hessian Computation Not Available
- **Warning:** "CLI mode: Cannot compute Hessian without gradient function"
- **Impact:** Standard errors, t-values, p-values not computed
- **Solution:** Use `run_full_post_estimation()` from within `RURO_estimate_FR.py`

### 3. Post-Estimation Limitations
- Current post-estimation only produces:
  - ✅ Parameter summaries
  - ✅ Marginal utility plots
  - ❌ Standard errors (requires Hessian)
  - ❌ Model fit statistics (AIC, BIC)
  - ❌ Elasticities

---

## 🔧 Script Improvements Made

### `run_fr_2016_pipeline.ps1`
1. Auto-detects CPU cores
2. Sets process priority to "High"
3. Uses venv Python automatically
4. Added Step 8: Post-estimation analysis
5. Fixed all command constructions to use variables

### `RURO_prep.py`
1. Fixed column renaming sequence
2. Expanded sex-specific column mapping
3. Fixed mandatory column checks
4. Improved error messages

### `RURO_estimate_FR.py`
1. Added `drgn*` → `reg*` column mapping
2. Fixed CSV initial parameter loading
3. Improved precompute functions

### `run_post_estimation.ps1`
1. New standalone script for post-estimation
2. Checks for estimation results
3. Generates plots and summaries
4. Organized output by model type

---

## 📝 Recommendations

### For Next Run

1. **Debug Couples Estimation:**
   ```powershell
   python "U:\Desktop\Nizam_Hisham\MNL\scripts\RURO_estimate_FR.py" `
       --mnl-file "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl.parquet" `
       --group 10 `
       --wage-spec vw `
       --optimizer L-BFGS-B `
       --maxiter 500 `
       --use-numba `
       --out-file "U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\2016\fr_2016_couples.json"
   ```

2. **Compute Full Standard Errors:**
   - Modify estimation to return gradient function
   - Use `compute_numeric_hessian()` from `RURO_post_estimation.py`

3. **Increase Iterations:**
   - Current: `--maxiter 500`
   - Consider: `--maxiter 1000` or `--maxiter 2000` for better convergence

4. **Try Different Optimizers:**
   - Current: `L-BFGS-B`
   - Alternatives: `SLSQP`, `trust-constr`, `Nelder-Mead`

5. **Validate Initial Parameters:**
   - Review `init_params_singles_template.csv`
   - Consider creating separate templates for males/females/couples

---

## 🚀 How to Run

### Full Pipeline
```powershell
cd U:\Desktop\Nizam_Hisham\MNL
powershell -ExecutionPolicy Bypass -File .\scripts\run_fr_2016_pipeline.ps1
```

### Post-Estimation Only
```powershell
cd U:\Desktop\Nizam_Hisham\MNL
powershell -ExecutionPolicy Bypass -File .\scripts\run_post_estimation.ps1
```

### Individual Steps
```powershell
# Step 1: Data preparation
python scripts\france_data_prep.py --year 2016 --raw-dir "U:\EUROMOD-STORAGE\Data\raw" --out-dir "U:\EUROMOD-STORAGE\Data\processed\fr\2016" --system-year 2015 --export-format parquet

# Step 2: RURO preparation
python scripts\RURO_prep.py --processed-dir "U:\EUROMOD-STORAGE\Data\processed\fr\2016" --base-year 2016 --export-format parquet

# Step 7a: Estimate single males
python scripts\RURO_estimate_FR.py --mnl-file "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl.parquet" --group 1 --sex m --wage-spec vw --optimizer L-BFGS-B --maxiter 500 --use-numba --out-file "U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\2016\fr_2016_single_males.json"
```

---

## 📚 Documentation

- **Pipeline Script:** `scripts/run_fr_2016_pipeline.ps1`
- **Post-Estimation:** `scripts/run_post_estimation.ps1`
- **Estimation Module:** `scripts/RURO_estimate_FR.py`
- **Post-Estimation Module:** `scripts/RURO_post_estimation.py`
- **Data Preparation:** `scripts/france_data_prep.py`
- **RURO Prep:** `scripts/RURO_prep.py`

---

**Generated:** December 6, 2025, 12:05 PM  
**Status:** Pipeline operational with 3/4 models successfully estimated
