# Clean Rerun Checklist - Phase 4 with Enhanced Post-Estimation

**Date:** 2025-12-17
**Goal:** Run full pipeline from scratch with proper .venv activation to verify Phase 4 results

---

## Pre-Flight Checks

### 1. Verify Virtual Environment

```powershell
cd U:\Desktop\Nizam_Hisham\MNL
.\.venv\Scripts\Activate.ps1
python -c "import euromod; print('euromod OK')"
python -c "import pandas; print('pandas OK')"
python -c "import numpy; print('numpy OK')"
```

**Expected:** All imports should work without warnings

### 2. Clean Up Old Files

**Files to DELETE:**

```powershell
# Processed data files
Remove-Item "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_processed.parquet" -ErrorAction SilentlyContinue
Remove-Item "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready.parquet" -ErrorAction SilentlyContinue
Remove-Item "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready.parquet" -ErrorAction SilentlyContinue
Remove-Item "U:\EUROMOD-STORAGE\Data\processed\fr\2016\*_RURO_draws.parquet" -ErrorAction SilentlyContinue
Remove-Item "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl.parquet" -ErrorAction SilentlyContinue

# EUROMOD interim results
Remove-Item "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016\*" -Recurse -ErrorAction SilentlyContinue

# Old estimation outputs
Remove-Item "U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\2016\*.json" -ErrorAction SilentlyContinue
Remove-Item "U:\Desktop\Nizam_Hisham\MNL\outputs\post_estimation\fr\2016\*" -Recurse -ErrorAction SilentlyContinue
```

**Files to KEEP:**
- Raw data: `U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt`
- Code: All Python scripts
- Documentation: All .md files

---

## Full Pipeline Run

### Step 1: Activate Environment (CRITICAL!)

```powershell
cd U:\Desktop\Nizam_Hisham\MNL
.\.venv\Scripts\Activate.ps1
```

**Verify activation:**
```powershell
python -c "import sys; print(sys.prefix)"
```

Should show: `U:\Desktop\Nizam_Hisham\MNL\.venv`

### Step 2: Run Full Pipeline

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_fr_2016_pipeline.ps1
```

**Expected duration:** ~14 minutes

**Expected output files:**
1. `fr_2016_processed.parquet` (11,964 records)
2. `singles_RURO_ready.parquet` (2,310 records)
3. `couples_RURO_ready.parquet` (9,654 records)
4. `singles_RURO_ready_RURO_draws.parquet` (99 draws × singles)
5. `couples_RURO_ready_RURO_draws.parquet` (99 draws × couples)
6. `combined_draws_em.parquet` (286,800 rows after EUROMOD)
7. `fr_2016_RURO_mnl.parquet` (448,900 rows - MNL dataset)

### Step 3: Verify MNL Dataset

```powershell
python -c "
import pandas as pd
df = pd.read_parquet('U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl.parquet')
print(f'Rows: {len(df):,}')
print(f'Columns: {len(df.columns)}')
print(f'Has age_norm_female: {\"age_norm_female\" in df.columns}')
print(f'Has age_norm2_female: {\"age_norm2_female\" in df.columns}')
print(f'Has n_children: {\"n_children\" in df.columns}')
"
```

**Expected:**
```
Rows: 448,900
Columns: 1,486
Has age_norm_female: True
Has age_norm2_female: True
Has n_children: True
```

### Step 4: Run Joint Estimation with Post-Estimation

```powershell
python scripts\RURO_estimate_FR.py `
  --mnl-file "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl.parquet" `
  --joint `
  --wage-spec vw `
  --optimizer L-BFGS-B `
  --maxiter 500 `
  --use-numba `
  --n-jobs 32 `
  --post-estimation `
  --out-file "outputs\estimates\fr\2016\fr_2016_joint_CLEAN_RUN.json"
```

**Expected:**
- Convergence: ~52 iterations
- Final LL: ~-15,233
- Time: ~60-90 seconds
- 59/60 parameters should move

### Step 5: Verify Results

```powershell
python -c "
import json
with open('outputs/estimates/fr/2016/fr_2016_joint_CLEAN_RUN.json') as f:
    data = json.load(f)
print(f'Success: {data[\"success\"]}')
print(f'LL: {data[\"log_likelihood\"]:.2f}')
print(f'Iterations: {data[\"n_iterations\"]}')
print(f'Parameters: {len(data[\"theta\"])}')

import numpy as np
theta = np.array(data['theta'])
theta0 = np.array(data['theta0'])
moved = np.sum(np.abs(theta - theta0) > 1e-6)
print(f'Parameters moved: {moved}/{len(theta)} ({100*moved/len(theta):.1f}%)')
"
```

**Expected:**
```
Success: True
LL: -15233.14
Iterations: 52
Parameters: 60
Parameters moved: 59/60 (98.3%)
```

### Step 6: Check HTML Report

```powershell
# Find HTML files
Get-ChildItem -Path "outputs" -Filter "*post_estimation*.html" -Recurse
```

**Expected:** HTML report with:
- ✅ Rho-squared (our enhancement)
- ✅ Null log-likelihood
- ✅ AIC/BIC
- ✅ Parameter estimates
- ✅ Diagnostic plots

---

## Expected Results Summary

### Model Fit (should match Phase 4):
- **Log-likelihood:** -15,233.14
- **Null LL:** -20,672.61
- **Rho-squared:** 0.2631 (EXCELLENT)
- **AIC:** 30,586.27
- **BIC:** 31,247.15

### Parameter Success:
- **Moved:** 59/60 (98.3%)
- **Stuck:** 1/60 (1.7%)
  - Only `cou.pref.beta_l_age_norm2_f` at 0.0

### Standard Errors:
- **Status:** May fail with singular Hessian
- **Reason:** Numerical precision issue with 60 parameters
- **Impact:** Parameter estimates still valid

---

## Troubleshooting

### Issue: "euromod package not found"

**Cause:** Virtual environment not activated

**Fix:**
```powershell
.\.venv\Scripts\Activate.ps1
python -c "import euromod"
```

### Issue: Pipeline stops at Step 1

**Cause:** Missing raw data file

**Check:**
```powershell
Test-Path "U:\EUROMOD-STORAGE\Data\raw\FR_2016.txt"
```

### Issue: Estimation converges to wrong LL

**Cause:** Old MNL dataset without demographic variables

**Fix:** Delete `fr_2016_RURO_mnl.parquet` and rebuild from Step 6

### Issue: Couples parameters stuck at initial

**Cause:** Missing `age_norm_female`, `age_norm2_female` in MNL dataset

**Fix:**
1. Check [scripts/RURO_prep_mnl_basic.py:273-284](scripts/RURO_prep_mnl_basic.py:273-284)
2. Verify couples section has:
   ```python
   age_norm_female = dag_female - mean(dag_female)
   age_norm2_female = age_norm_female²
   n_children_female = num_children_total_female
   ```

---

## Post-Run Verification

### 1. Check Fit Statistics

```powershell
python compute_fit_statistics.py `
  outputs\estimates\fr\2016\fr_2016_joint_CLEAN_RUN.json `
  U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl.parquet
```

### 2. Compare with Phase 4

```powershell
python -c "
import json
import numpy as np

# Load both results
with open('outputs/estimates/fr/2016/fr_2016_joint_PHASE4.json') as f:
    phase4 = json.load(f)
with open('outputs/estimates/fr/2016/fr_2016_joint_CLEAN_RUN.json') as f:
    clean = json.load(f)

print('Comparison:')
print(f'Phase 4 LL: {phase4[\"log_likelihood\"]:.2f}')
print(f'Clean LL:   {clean[\"log_likelihood\"]:.2f}')
print(f'Difference: {abs(phase4[\"log_likelihood\"] - clean[\"log_likelihood\"]):.2f}')

# Should be identical or very close (< 0.01)
"
```

---

## Success Criteria

✅ **Pipeline completes all 7 steps**
✅ **Estimation converges in ~52 iterations**
✅ **Final LL ≈ -15,233**
✅ **59/60 parameters moved**
✅ **Rho-squared ≈ 0.263**
✅ **HTML report generated with rho-squared**
✅ **No "euromod package not found" warnings**

---

## Files Created

After successful run, you should have:

**Estimation:**
- `outputs/estimates/fr/2016/fr_2016_joint_CLEAN_RUN.json`
- `outputs/estimates/fr/2016/fr_2016_joint_CLEAN_RUN_with_fit_stats.json` (from compute_fit_statistics.py)

**Post-Estimation:**
- `outputs/estimates/fr/2016/vw_joint_post_estimation_report.html`
- `outputs/estimates/fr/2016/vw_joint_params.csv`
- `outputs/estimates/fr/2016/vw_joint_elasticities.csv`
- `outputs/estimates/fr/2016/vw_joint_*.png` (contour plots)

---

**Ready to run:** All scripts are in place, enhancements are complete
**Next step:** Delete old files and run full pipeline from scratch
**Expected time:** ~15 minutes total
