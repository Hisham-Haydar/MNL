# Pipeline Run Analysis - December 14, 2025

**Date:** 2025-12-14 13:44-14:00
**Pipeline:** France 2016 RURO Joint Estimation (Full Run from Scratch)
**Status:** ⚠️ **COMPLETED WITH CRITICAL ISSUES**

---

## Executive Summary

The pipeline ran successfully through all 7 steps and estimation "converged," BUT there are **critical data and identification issues** that make the results invalid:

🔴 **CRITICAL**: Couples consumption data = 0.0 (mean and std both zero)
🔴 **CRITICAL**: Most parameters stuck at initial values (identification failure)
⚠️ **WARNING**: Exit code 1 (likely from `--post-estimation` flag issue)

**Conclusion**: The estimation technically succeeded but the results are NOT usable due to data problems and parameter identification failures.

---

## Pipeline Execution Timeline

### Steps 1-6: Data Preparation ✅ SUCCESS

| Step | Description | Duration | Status |
|------|-------------|----------|--------|
| 1 | Data Preparation | 00:01:08 | ✅ SUCCESS |
| 2 | RURO Preparation | 00:00:18 | ✅ SUCCESS |
| 3 | Generate Draws | 00:00:32 | ✅ SUCCESS |
| 4 | EUROMOD Simulation | 00:03:36 | ✅ SUCCESS |
| 5 | Prepare GSUR | ~0s (cached) | ✅ SUCCESS |
| 6 | Build MNL Dataset | 00:00:46 | ✅ SUCCESS |

**Total preprocessing time:** ~6 minutes 20 seconds

**Data created:**
- Processed data: 11,964 records (4,521 households)
- Singles: 2,310 individuals
- Couples: 9,654 individuals
- MNL dataset: **742,100 rows** (different from expected 449,589!)

### Step 7: Joint Estimation ⚠️ CONVERGED BUT INVALID

**Duration:** 00:00:27 (optimization only, ~32s including pre-computation)
**Optimizer:** L-BFGS-B
**Status:** CONVERGENCE: RELATIVE REDUCTION OF F <= FACTR*EPSMCH
**Exit Code:** 1 (failed - likely post-estimation error)

**Performance:**
- Total optimization time: 26.99s
- Iterations: 35
- Function evaluations: 38
- Avg time per evaluation: 702.53ms

**Log-Likelihood:**
- Initial: -1,273,550.50
- Final: -22,207.35
- **Improvement:** 1,251,343.15 (98.26% reduction!)

---

## Critical Issues Found

### 🔴 ISSUE 1: Couples Consumption Data = ZERO

**From estimation log:**
```
Computed synthetic consumption: mean=2.472, std=1.936    # Single males ✅
Computed synthetic consumption: mean=2.532, std=2.005    # Single females ✅
Computed synthetic couples consumption: mean=0.000, std=0.000  # Couples ❌
```

**Impact:**
- Couples utility function cannot be estimated (consumption term = 0)
- All couples preference parameters stuck at initial values
- Couples contribute nothing meaningful to the likelihood

**Root Cause:** Likely bug in `RURO_prep_mnl_basic.py` when computing couples consumption:
- File: [scripts/RURO_prep_mnl_basic.py](scripts/RURO_prep_mnl_basic.py)
- Lines: ~300-400 (couples consumption extraction)
- The consumption column is either missing, misnamed, or computed incorrectly

### 🔴 ISSUE 2: Parameter Identification Failure

**Parameters that moved (estimated successfully):**
- `sm.pref.beta_l0`: -1.7145
- `sm.pref.beta_l_educL`: 0.8937
- `sm.pref.beta_l_educH`: -0.7411
- `sm.pref.beta_c`: -1.6517
- `sm.pref.theta_l`: 7.3411 (Box-Cox for leisure)
- `sm.pref.theta_c`: 1.5711 (Box-Cox for consumption)
- Similar for single females

**Parameters STUCK at initial values:**

1. **All age/children effects in preferences:** 0.0
   - `beta_l_age_norm`, `beta_l_age_norm2`, `beta_l_n_children` = 0.0

2. **ALL couples parameters:** Stuck at typical initials
   - `cou.pref.beta_l0_m` = 1.0 (initial)
   - `cou.pref.beta_l0_f` = 1.0 (initial)
   - `cou.pref.beta_c` = 1.0 (initial)
   - `cou.pref.theta_l_m` = 0.5 (initial)
   - `cou.pref.theta_l_f` = 0.5 (initial)
   - `cou.pref.theta_c` = 0.5 (initial)
   - All education/age/children effects = 0.0

3. **ALL hours opportunity parameters:** Stuck
   - `hopp_m.beta_work` = 0.5 (initial)
   - `hopp_f.beta_work` = 0.5 (initial)
   - All other hopp params ≈ 0.0

4. **ALL wage opportunity parameters:** Stuck
   - `wopp_m.beta0` = 2.5, `wopp_f.beta0` = 2.3 (initials)
   - `wopp_m.sigma` = 0.4, `wopp_f.sigma` = 0.4 (initials)
   - Education/experience effects at typical initials

**Estimated vs. Initial Values:**
```
Out of 60 parameters:
- ~10 parameters moved significantly (singles preferences)
- ~50 parameters stuck at or near initial values (83%)
```

**Why this happened:**
1. **Couples data problem**: Consumption = 0 → couples don't contribute to likelihood
2. **Weak identification**: Opportunity parameters not identifiable from choice data alone
3. **Possible collinearity**: Age/children/education effects might be collinear with intercepts
4. **Bounds too tight?**: Even though we fixed the bounds bug, some parameters might be hitting bounds

### ⚠️ ISSUE 3: Exit Code 1 (Post-Estimation)

The estimation exited with code 1 despite successful convergence.

**Likely cause:** The `--post-estimation` flag is enabled but the post-estimation code is incomplete (documented in [POST_ESTIMATION_STATUS.md](POST_ESTIMATION_STATUS.md)).

**From previous analysis:**
- `RURO_post_estimation.py` has incomplete stub functions
- Will crash when called with incomplete `ParsedParameters` class
- Should remove `--post-estimation` flag from pipeline

**Current PowerShell script (line 416):**
```powershell
"--post-estimation " +   # ← REMOVE THIS LINE
```

---

## Data Quality Analysis

### Row Counts

**Expected vs. Actual:**
- **Expected MNL dataset**: 449,589 rows
- **Actual MNL dataset**: 742,100 rows
- **Difference**: +292,511 rows (+65% larger!)

**This discrepancy needs investigation:**
- Are there duplicate rows?
- Different number of alternatives per individual?
- Different draw structure?

### Group Breakdown

```
Single males:   73,900 rows  (739 individuals × 100 alternatives)
Single females: 88,200 rows  (882 individuals × 100 alternatives)
Couples:       580,000 rows  (2,900 individuals × 200 alternatives)
Total:         742,100 rows
```

**Couples alternatives:** 200 per couple (likely 100 male hours × 2 scenarios, or similar)

### Consumption Statistics

**Singles:**
- Males: mean=2.472, std=1.936 ✅
- Females: mean=2.532, std=2.005 ✅

**Couples:**
- mean=0.000, std=0.000 ❌

**This is the smoking gun** - couples consumption data is completely broken.

---

## Root Cause Investigation Needed

### Priority 1: Fix Couples Consumption Data

**File to investigate:** [scripts/RURO_prep_mnl_basic.py](scripts/RURO_prep_mnl_basic.py)

**What to check:**
1. How couples consumption is extracted from EUROMOD output
2. Column name mapping (might be looking for wrong column)
3. Transformation/normalization logic
4. Whether consumption is household-level or individual-level

**Likely issues:**
```python
# Bad (what might be happening):
df_cou['ruro_consumption'] = 0.0  # Hard-coded zero?
df_cou['ruro_consumption'] = df_cou['consumption'].fillna(0)  # Missing column?

# Good (what should happen):
df_cou['ruro_consumption'] = df_cou['ils_dispy'] / 1000  # Disposable income
```

**Expected consumption values:**
- Should be similar magnitude to singles (~2.5 mean)
- Should have positive standard deviation
- Should correlate with household income

### Priority 2: Check Parameter Bounds

**File to check:** [scripts/RURO_estimate_FR.py](scripts/RURO_estimate_FR.py)

Even though we fixed the unreachable bounds bug (line 5515), we should verify:
1. Are bounds being set correctly now?
2. Are any parameters hitting their bounds?
3. Should we widen bounds further?

**Current bounds (from previous analysis):**
```python
bounds[7] = (-10, 20.0)   # theta_l (Box-Cox leisure)
bounds[8] = (-10, 20.0)   # theta_c (Box-Cox consumption)
bounds[53] = (-10, 50.0)  # sigma_males
bounds[59] = (-10, 50.0)  # sigma_females
```

**Estimated values hitting bounds?**
```
sm.pref.theta_l = 7.3411   # Within (-10, 20) ✅
sm.pref.theta_c = 1.5711   # Within (-10, 20) ✅
sf.pref.theta_l = 8.1951   # Within (-10, 20) ✅
sf.pref.theta_c = 1.6444   # Within (-10, 20) ✅
wopp_m.sigma = 0.4000      # Stuck at initial (should be within -10, 50)
wopp_f.sigma = 0.4000      # Stuck at initial
```

Box-Cox parameters moved, so bounds are working. But sigma parameters stuck at initial values suggests identification issue, not bounds issue.

### Priority 3: Check for Collinearity

**Variables to check:**
- Age (dag) vs. age_norm vs. age_norm2
- Education dummies (educL, educH) vs. reference category
- Children effects (n_children) vs. family structure
- Regional effects (if any)

**Diagnosis:**
```python
import pandas as pd
df = pd.read_parquet("U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl.parquet")

# Correlation matrix
covariates = ['age_norm', 'age_norm2', 'n_children', 'educL', 'educH']
print(df[covariates].corr())

# Variance inflation factors (VIF)
from statsmodels.stats.outliers_influence import variance_inflation_factor
vif = pd.DataFrame()
vif["Variable"] = covariates
vif["VIF"] = [variance_inflation_factor(df[covariates].values, i) for i in range(len(covariates))]
print(vif)
```

If VIF > 10, there's multicollinearity.

### Priority 4: Check Initial Parameters

**File to check:** [init_params_singles_template.csv](init_params_singles_template.csv) (or similar)

**Questions:**
1. Are initial values too far from true values?
2. Are some parameters initialized at boundary values?
3. Should we use estimates from individual group estimation as initials for joint?

**Current initials (from output):**
- Most couples/opportunity params at "round numbers" (0.0, 0.5, 1.0, 2.5)
- Suggests generic initialization, not data-driven

**Better approach:**
1. Estimate singles males separately → get theta_l, theta_c
2. Estimate singles females separately → get theta_l, theta_c
3. Estimate couples separately (once data fixed) → get couples params
4. Use those as initials for joint estimation

---

## Convergence Behavior Analysis

### Good News ✅

1. **Convergence achieved:** L-BFGS-B declared convergence after 35 iterations
2. **Fast convergence:** ~27 seconds, ~703ms per evaluation
3. **Massive likelihood improvement:** From -1.27M to -22K (98% reduction)
4. **No Numba errors:** JIT compilation worked
5. **No parallelization issues:** 32 jobs ran successfully

### Bad News ❌

1. **No iteration output:** The optimization ran silently without printing iteration progress
   - Issue: `disp` parameter is deprecated in SciPy 1.18
   - Need to implement custom callback for progress monitoring

2. **Parameters didn't move:** Most parameters stuck at initials despite "convergence"
   - Optimizer found "local optimum" where most parameters don't affect likelihood
   - This is a **data/identification problem**, not optimizer problem

3. **Suspiciously low final LL:** -22,207 seems too good compared to initial -1.27M
   - With 742K rows, LL per observation = -0.0299
   - This is actually very good fit (close to perfect)
   - **BUT**: With couples consumption = 0, couples aren't contributing
   - Actual LL might be from singles only

**Singles-only LL check:**
```
Singles rows: 73,900 + 88,200 = 162,100
LL per row: -22,207 / 162,100 = -0.137

This is plausible for well-fitting MNL model.
```

So the optimizer **correctly ignored couples** because they have zero consumption (contribute nothing to likelihood).

---

## Recommendations

### Immediate Actions (< 30 minutes)

1. **Remove `--post-estimation` flag** from [scripts/run_fr_2016_joint_only.ps1:416](scripts/run_fr_2016_joint_only.ps1#L416)
   ```powershell
   # DELETE THIS LINE:
   "--post-estimation " +
   ```

2. **Investigate couples consumption bug** in [scripts/RURO_prep_mnl_basic.py](scripts/RURO_prep_mnl_basic.py)
   - Read the file, find couples consumption computation
   - Check if column name is correct
   - Check if transformation is correct
   - Fix the bug

3. **Re-run just Step 6 and 7** after fixing consumption bug
   ```powershell
   # After fixing RURO_prep_mnl_basic.py:
   python scripts/RURO_prep_mnl_basic.py --singles-draws ... --couples-draws ...
   python scripts/RURO_estimate_FR.py --mnl-file ... --joint ...
   ```

### Short-term Actions (1-2 hours)

4. **Add progress callback** to optimizer in [scripts/RURO_estimate_FR.py:5544](scripts/RURO_estimate_FR.py#L5544)
   ```python
   def callback(xk):
       """Print iteration progress"""
       iter_num = callback.counter
       if iter_num % 5 == 0:  # Every 5 iterations
           fval = objective_func(xk)
           print(f"Iteration {iter_num}: LL={-fval:.2f}")
       callback.counter += 1

   callback.counter = 0

   result = minimize(
       ...,
       callback=callback,  # Add this
   )
   ```

5. **Check parameter bounds** are being applied correctly
   - Add print statements to confirm bounds are set
   - Check if any parameters hit bounds during optimization

6. **Run collinearity diagnostics** on MNL dataset
   - Check VIF for age, education, children variables
   - Consider dropping collinear variables

### Medium-term Actions (1 day)

7. **Estimate groups separately** before joint estimation
   ```bash
   # Get good initial parameters
   python scripts/RURO_estimate_FR.py --mnl-file ... --group 1 --sex m --wage-spec vw
   python scripts/RURO_estimate_FR.py --mnl-file ... --group 1 --sex f --wage-spec vw
   python scripts/RURO_estimate_FR.py --mnl-file ... --group 10 --wage-spec vw

   # Use those results as initials for joint
   python scripts/RURO_estimate_FR.py --mnl-file ... --joint --init-params joint_initials.csv
   ```

8. **Implement identification tests**
   - Check if Hessian is positive definite
   - Check condition number of Hessian
   - Check if parameters are identifiable

9. **Fix or complete post-estimation code**
   - Option A: Complete the stub functions in `RURO_post_estimation.py`
   - Option B: Use backup version if available
   - Option C: Rewrite with working diagnostics

---

## Files to Investigate

### Priority 1: Data Bug
- [scripts/RURO_prep_mnl_basic.py](scripts/RURO_prep_mnl_basic.py) - Line ~300-400 (couples consumption)
- Check column names: `ils_dispy`, `consumption`, `ruro_consumption`
- Check for nulls, zeros, missing data

### Priority 2: Estimation Setup
- [scripts/RURO_estimate_FR.py](scripts/RURO_estimate_FR.py) - Line 5544 (optimizer call)
- Line 5515 (bounds setup - already fixed)
- Add progress callback
- Verify bounds are applied

### Priority 3: Initial Parameters
- Check if initial parameter file exists
- Compare initials to estimated values
- Consider using single-group estimates as initials

### Priority 4: Post-Estimation
- [scripts/run_fr_2016_joint_only.ps1:416](scripts/run_fr_2016_joint_only.ps1#L416) - Remove flag
- [scripts/RURO_post_estimation.py](scripts/RURO_post_estimation.py) - Fix or disable

---

## Logging Enhancement Status

✅ **SUCCESS**: Enhanced logging worked perfectly for Steps 1-6

**What worked:**
- Millisecond timestamps on every line
- Real-time streaming output
- Structured markdown log format
- Clear status markers (SUCCESS/FAILED)
- Duration tracking

**What needs improvement:**
- Step 7 (estimation) ran silently without iteration progress
- Need to add custom callback for optimizer progress
- Need to capture Python output better (currently going to stderr)

**Log file created:**
- [outputs/logs/fr_2016_joint_only_2025-12-14_13-44-41.md](outputs/logs/fr_2016_joint_only_2025-12-14_13-44-41.md)
- Contains full output from Steps 1-6
- Step 7 has no output (ran silently)

---

## Summary Table

| Component | Status | Issue | Priority |
|-----------|--------|-------|----------|
| Steps 1-6 | ✅ SUCCESS | None | - |
| Estimation convergence | ✅ CONVERGED | - | - |
| Couples data | 🔴 BROKEN | Consumption = 0 | **P0** |
| Parameter identification | 🔴 FAILED | 50/60 params stuck | **P1** |
| Post-estimation | 🔴 CRASHED | Incomplete code | **P2** |
| Logging | ✅ WORKING | No iter progress | **P3** |
| Bounds fix | ✅ FIXED | - | - |

---

## Next Steps

1. ✅ Enhanced logging (DONE)
2. ✅ Ran pipeline from scratch (DONE)
3. ✅ Identified critical issues (DONE)
4. ⏳ **FIX COUPLES CONSUMPTION BUG** (URGENT)
5. ⏳ Remove post-estimation flag
6. ⏳ Re-run estimation with fixed data
7. ⏳ Analyze convergence behavior with proper output
8. ⏳ Check identification with properly estimated model

---

**Session Time:** 16 minutes
**Status:** Analysis complete, ready to fix data bugs

**Files Created:**
- [outputs/logs/fr_2016_joint_only_2025-12-14_13-44-41.md](outputs/logs/fr_2016_joint_only_2025-12-14_13-44-41.md)
- [outputs/estimates/fr/2016/fr_2016_joint.json](outputs/estimates/fr/2016/fr_2016_joint.json)
- This report: [PIPELINE_RUN_ANALYSIS_2025-12-14.md](PIPELINE_RUN_ANALYSIS_2025-12-14.md)
