# Variable Diagnostic Report - Missing Demographic Variables

**Date:** 2025-12-17
**Issue:** 11 preference parameters stuck at initial values
**Root Cause:** Missing `age_norm`, `age_norm2`, and `n_children` variables in MNL dataset

---

## Summary

**Problem:** The estimation code expects demographic variables that the MNL builder is NOT creating:
- `age_norm` / `age_norm_male` / `age_norm_female` - Age centered at mean
- `age_norm2` / `age_norm2_male` / `age_norm2_female` - Squared normalized age
- `n_children` / `n_children_male` / `n_children_female` - Total number of children

**Impact:** 11 parameters cannot be estimated because their covariates are missing:
- Single Males: `beta_l_age_norm`, `beta_l_age_norm2`, `beta_l_n_children`
- Single Females: `beta_l_age_norm`, `beta_l_age_norm2`, `beta_l_n_children`
- Couples: `beta_l_age_norm_m`, `beta_l_age_norm2_m`, `beta_l0_f`, `beta_l_age_norm_f`, `beta_l_age_norm2_f`

---

## Current State of Variables in MNL Dataset

### ✅ Age Variables (RAW - Available)
| Variable | Sample Group | Mean | Std | Available |
|----------|-------------|------|-----|-----------|
| `dag` | Singles | 43.72 | 10.96 | ✅ |
| `dag_male` | Couples | 42.65 | 9.75 | ✅ |
| `dag_female` | Couples | 40.55 | 9.85 | ✅ |

### ❌ Age Variables (NORMALIZED - Missing)
| Variable | Sample Group | Expected | Status |
|----------|-------------|----------|--------|
| `age_norm` | Singles | `dag - mean(dag)` | ❌ NOT CREATED |
| `age_norm2` | Singles | `age_norm^2` | ❌ NOT CREATED |
| `age_norm_male` | Couples | `dag_male - mean(dag_male)` | ❌ NOT CREATED |
| `age_norm2_male` | Couples | `age_norm_male^2` | ❌ NOT CREATED |
| `age_norm_female` | Couples | `dag_female - mean(dag_female)` | ❌ NOT CREATED |
| `age_norm2_female` | Couples | `age_norm_female^2` | ❌ NOT CREATED |

### ✅ Children Variables (TOTAL - Available)
| Variable | Sample Group | Mean | Max | Available |
|----------|-------------|------|-----|-----------|
| `num_children_total` | Singles | 0.381 | 5 | ✅ |
| `num_children_total_male` | Couples | 1.174 | 6 | ✅ |
| `num_children_total_female` | Couples | 1.209 | 6 | ✅ |

### ❌ Children Variables (ALIAS - Missing)
| Variable | Sample Group | Expected | Status |
|----------|-------------|----------|--------|
| `n_children` | Singles | Alias for `num_children_total` | ❌ NOT CREATED |
| `n_children_male` | Couples | Alias for `num_children_total_male` | ❌ NOT CREATED |
| `n_children_female` | Couples | Alias for `num_children_total_female` | ❌ NOT CREATED |

---

## Required Fixes to RURO_prep_mnl_basic.py

### Fix 1: Add Missing Variables to `_build_mnl_block_singles()`

**Location:** After line ~108 (after education variables are created)

**Code to Add:**
```python
# Age normalization (for preference parameters)
if "dag" in df.columns:
    dag_values = pd.to_numeric(df["dag"], errors="coerce")
    dag_mean = dag_values.mean()
    df["age_norm"] = dag_values - dag_mean
    df["age_norm2"] = df["age_norm"] ** 2
    LOGGER.debug(f"Created age_norm (mean=0.00, std={df['age_norm'].std():.2f})")

# Total children count (create alias for compatibility)
if "num_children_total" in df.columns:
    df["n_children"] = pd.to_numeric(df["num_children_total"], errors="coerce").fillna(0)
    LOGGER.debug(f"Created n_children alias (mean={df['n_children'].mean():.2f})")
```

### Fix 2: Add Missing Variables to `_build_mnl_block_couples_wide()`

**Location:** After the gender loop that creates `educL_*`, `educM_*`, `educH_*` variables (around line 180)

**Code to Add:**
```python
# After the gender loop, add age normalization and children count
for gender in ["male", "female"]:
    # Age normalization (for preference parameters)
    dag_col = f"dag_{gender}"
    if dag_col in df.columns:
        dag_values = pd.to_numeric(df[dag_col], errors="coerce")
        dag_mean = dag_values.mean()
        df[f"age_norm_{gender}"] = dag_values - dag_mean
        df[f"age_norm2_{gender}"] = df[f"age_norm_{gender}"] ** 2
        LOGGER.debug(f"Created age_norm_{gender} (mean=0.00, std={df[f'age_norm_{gender}'].std():.2f})")

    # Total children count (create alias for compatibility)
    num_children_col = f"num_children_total_{gender}"
    if num_children_col in df.columns:
        df[f"n_children_{gender}"] = pd.to_numeric(df[num_children_col], errors="coerce").fillna(0)
        LOGGER.debug(f"Created n_children_{gender} alias (mean={df[f'n_children_{gender}'].mean():.2f})")
```

---

## Expected Results After Fix

### Singles
- `age_norm`: mean=0.00, std=10.96, fully identified ✓
- `age_norm2`: mean≈120, std varies, fully identified ✓
- `n_children`: mean=0.381, max=5, fully identified ✓

### Couples
- `age_norm_male`: mean=0.00, std=9.75, fully identified ✓
- `age_norm2_male`: mean≈95, std varies, fully identified ✓
- `age_norm_female`: mean=0.00, std=9.85, fully identified ✓
- `age_norm2_female`: mean≈97, std varies, fully identified ✓
- `n_children_male`: mean=1.174, max=6, fully identified ✓
- `n_children_female`: mean=1.209, max=6, fully identified ✓

---

## Parameters That Will Now Be Estimated

Once these variables are created, the following 11 parameters should be able to move from their initial values:

### Single Males (3 parameters)
1. `sm.pref.beta_l_age_norm` - Currently at 0.0
2. `sm.pref.beta_l_age_norm2` - Currently at 0.0
3. `sm.pref.beta_l_n_children` - Currently at 0.0

### Single Females (3 parameters)
1. `sf.pref.beta_l_age_norm` - Currently at 0.0
2. `sf.pref.beta_l_age_norm2` - Currently at 0.0
3. `sf.pref.beta_l_n_children` - Currently at 0.2

### Couples (5 parameters)
1. `cou.pref.beta_l_age_norm_m` - Currently at 0.0
2. `cou.pref.beta_l_age_norm2_m` - Currently at 0.0
3. `cou.pref.beta_l0_f` - Currently at 1.0 (baseline parameter, might be normalization constraint)
4. `cou.pref.beta_l_age_norm_f` - Currently at 0.0
5. `cou.pref.beta_l_age_norm2_f` - Currently at 0.0

---

## Implementation Steps

1. **Add variables to MNL builder** (both singles and couples functions)
2. **Rebuild MNL dataset** using updated builder
3. **Re-run estimation** with full iteration limit
4. **Verify parameters move** from initial values
5. **Check standard errors** (separate issue to investigate)

---

## Notes

**Age Normalization:**
- Subtracting the mean creates a variable with mean=0, which improves numerical stability and interpretation
- Age-squared (`age_norm2`) captures non-linear age effects on leisure preferences

**Children Count:**
- The raw variable `num_children_total` already exists and has good variation
- We just need to create an alias `n_children` for estimation code compatibility
- For couples, both male and female have the same household children count (expected)

**Parameter at Initial Value ≠ Not Working:**
- Some parameters might legitimately stay at zero if they're not significant predictors
- But they can only be determined NOT significant if the covariate exists!
- Currently, the gradients are mathematically zero because the variables don't exist

---

**Status:** Variables identified, fixes ready to implement
