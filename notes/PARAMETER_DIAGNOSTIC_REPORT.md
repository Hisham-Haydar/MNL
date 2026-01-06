# Parameter Estimation Diagnostic Report
**Date:** 2025-12-17
**Estimation:** France 2016 Joint (vw specification)
**File:** `outputs/estimates/fr/2016/fr_2016_joint.json`

---

## Summary

**Total Parameters:** 60
**Log-Likelihood:** -10,240.94
**Converged:** YES
**Iterations:** 151
**Standard Errors:** AVAILABLE ✓

---

## Key Findings

### ✅ **GOOD NEWS: All Opportunity Parameters ARE Working!**

- **HOPP_M (Hours Opportunity Male):** 7/7 parameters moved, 0 at zero
- **HOPP_F (Hours Opportunity Female):** 7/7 parameters moved, 0 at zero
- **WOPP_M (Wage Opportunity Male):** 6/6 parameters moved, 0 at zero
- **WOPP_F (Wage Opportunity Female):** 6/6 parameters moved, 0 at zero

**Phase 3 fixes were SUCCESSFUL** - all 26 opportunity parameters are now being estimated!

---

## ⚠️ Parameters NOT Estimated (11 total)

These are **preference parameters** that didn't move from their initial values:

### Single Males (3 parameters)
1. `sm.pref.beta_l_age_norm` - init=0.0, final=0.0
2. `sm.pref.beta_l_age_norm2` - init=0.0, final=0.0
3. `sm.pref.beta_l_n_children` - init=0.0, final=0.0

### Single Females (3 parameters)
10. `sf.pref.beta_l_age_norm` - init=0.0, final=0.0
11. `sf.pref.beta_l_age_norm2` - init=0.0, final=0.0
12. `sf.pref.beta_l_n_children` - init=0.2, final=0.2

### Couples (5 parameters)
19. `cou.pref.beta_l_age_norm_m` - init=0.0, final=0.0
20. `cou.pref.beta_l_age_norm2_m` - init=0.0, final=0.0
24. `cou.pref.beta_l0_f` - init=1.0, final=1.0
25. `cou.pref.beta_l_age_norm_f` - init=0.0, final=0.0
26. `cou.pref.beta_l_age_norm2_f` - init=0.0, final=0.0

---

## Parameter Groups Breakdown

| Group | Index Range | Total Params | Moved | At Zero | Status |
|-------|-------------|--------------|-------|---------|--------|
| SM Prefs | [0:9] | 9 | 6 | 3 | ⚠️ Some not moving |
| SF Prefs | [9:18] | 9 | 6 | 2 | ⚠️ Some not moving |
| COU Prefs | [18:34] | 16 | 11 | 4 | ⚠️ Some not moving |
| **HOPP_M** | [34:41] | 7 | 7 | 0 | ✅ **ALL WORKING** |
| **HOPP_F** | [41:48] | 7 | 7 | 0 | ✅ **ALL WORKING** |
| **WOPP_M** | [48:54] | 6 | 6 | 0 | ✅ **ALL WORKING** |
| **WOPP_F** | [54:60] | 6 | 6 | 0 | ✅ **ALL WORKING** |

---

## Why Some Preference Parameters Didn't Move

### Possible Explanations:

1. **Age Variables Have Little Variation**
   - After normalization (`age_norm = dag - mean(dag)`), age might have limited variation
   - Age-squared (`age_norm2`) depends on age variation
   - These might not be significant predictors in this dataset

2. **Number of Children Not Significant**
   - For singles, `n_children` might not vary much or might not affect leisure preferences
   - Parameter stays at initial value (0.0) because gradient is small

3. **Identification Issues**
   - Some parameters might be at corners of their identified set
   - Baseline parameters (like `cou.pref.beta_l0_f = 1.0`) might be normalization constraints

4. **Model Specification**
   - These parameters might not be in the utility function for this specification
   - They might be fixed at their initial values by design

---

## Standard Errors Status

✅ **Standard errors ARE available** (unlike the limitation mentioned earlier)

The estimation code successfully computed:
- Parameter estimates (`theta`)
- Standard errors (`std_errors`)
- T-statistics (`t_values`)

This means we can conduct proper statistical inference!

---

## Comparison with Stijn's R Implementation

According to [STIJN_vs_PYTHON_SPECIFICATION.md](STIJN_vs_PYTHON_SPECIFICATION.md):

- Stijn's R code has **82 parameters** total
- Our Python code has **60 parameters** total

**Difference:** Stijn likely includes more demographic interactions or year dummies in preferences.

Our implementation appears to use a **simplified preference specification** while keeping the full opportunity specification.

---

## Recommendations

### 1. **Investigate Age Variable Variation**
Check if `age_norm` and `age_norm2` have sufficient variation in the dataset:

```python
import pandas as df
mnl = pd.read_parquet('U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl.parquet')
print(mnl['age_norm'].describe())
print(mnl['age_norm2'].describe())
```

### 2. **Check if Parameters Should Be Fixed**
Review the utility function specification to confirm if these parameters are:
- Part of the model specification
- Meant to be estimated or fixed at zero/initial values

### 3. **Compare with Stijn's Parameter Count**
If we should have 82 parameters like Stijn's R code, we need to investigate what's missing.

### 4. **Standard Errors for Non-Moving Parameters**
Check the standard errors for parameters that didn't move - they might be:
- Very large (parameter not identified)
- Very small (parameter at boundary)
- NULL (parameter fixed)

### 5. **Consider Alternative Initial Values**
For parameters stuck at initial values, try different starting points to see if they move.

---

## Next Steps for Investigation

1. **Check variable variation** in MNL dataset for age and children variables
2. **Review utility function specification** in `RURO_estimate_FR.py`
3. **Compare parameter counts** with Stijn's R implementation
4. **Examine standard errors** for non-moving parameters
5. **Verify if this is expected behavior** for this simplified specification

---

**Status:** Pipeline is WORKING, but some preference parameters may need further investigation to determine if they should be estimated or are correctly fixed at their initial values.
