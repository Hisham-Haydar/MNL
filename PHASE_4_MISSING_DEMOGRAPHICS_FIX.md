# Phase 4: Missing Demographic Variables Fix

**Date:** 2025-12-17
**Issue:** 11 preference parameters stuck at initial values due to missing demographic variables
**Status:** ✅ FIXED - Ready to rebuild and test

---

## Problem Summary

After Phase 3 successfully fixed opportunity parameters, discovered that 11 preference parameters could not be estimated because their required demographic variables were missing from the MNL dataset:

- `age_norm`, `age_norm2`, `n_children` (singles)
- `age_norm_male`, `age_norm2_male`, `n_children_male` (couples)
- `age_norm_female`, `age_norm2_female`, `n_children_female` (couples)

---

## Root Cause

The MNL builder functions (`_build_mnl_block` for singles and `_build_mnl_block_couples_wide` for couples) were NOT creating these derived demographic variables that the estimation code expects.

**Available raw variables:**
- ✅ `dag`, `dag_male`, `dag_female` - Raw age (exists)
- ✅ `num_children_total`, `num_children_total_male`, `num_children_total_female` - Total children (exists)

**Missing derived variables:**
- ❌ `age_norm` - Age centered at mean (NOT created)
- ❌ `age_norm2` - Squared normalized age (NOT created)
- ❌ `n_children` - Alias for total children (NOT created)

---

## Fixes Implemented

### Fix 1: Singles Function (`_build_mnl_block`)

**File:** [scripts/RURO_prep_mnl_basic.py](scripts/RURO_prep_mnl_basic.py:273-284)
**Location:** After education variables (line 273)

**Added:**
```python
# Age normalization (for preference parameters)
if "dag" in df.columns:
    dag_values = pd.to_numeric(df["dag"], errors="coerce")
    dag_mean = dag_values.mean()
    df["age_norm"] = dag_values - dag_mean
    df["age_norm2"] = df["age_norm"] ** 2
    logging.debug(f"Created age_norm (mean=0.00, std={df['age_norm'].std():.2f})")

# Total children count (create alias for compatibility)
if "num_children_total" in df.columns:
    df["n_children"] = pd.to_numeric(df["num_children_total"], errors="coerce").fillna(0)
    logging.debug(f"Created n_children alias (mean={df['n_children'].mean():.2f})")
```

### Fix 2: Couples Function (`_build_mnl_block_couples_wide`)

**File:** [scripts/RURO_prep_mnl_basic.py](scripts/RURO_prep_mnl_basic.py:212-225)
**Location:** Inside gender loop, after experience variables (line 212)

**Added:**
```python
# Age normalization (for preference parameters)
dag_col = f"dag_{gender}"
if dag_col in df.columns:
    dag_values = pd.to_numeric(df[dag_col], errors="coerce")
    dag_mean = dag_values.mean()
    df[f"age_norm_{gender}"] = dag_values - dag_mean
    df[f"age_norm2_{gender}"] = df[f"age_norm_{gender}"] ** 2
    logging.debug(f"Created age_norm_{gender} (mean=0.00, std={df[f'age_norm_{gender}'].std():.2f})")

# Total children count (create alias for compatibility)
num_children_col = f"num_children_total_{gender}"
if num_children_col in df.columns:
    df[f"n_children_{gender}"] = pd.to_numeric(df[num_children_col], errors="coerce").fillna(0)
    logging.debug(f"Created n_children_{gender} alias (mean={df[f'n_children_{gender}'].mean():.2f})")
```

---

## Expected Results After Fix

### Variables Created - Singles
| Variable | Formula | Expected Stats |
|----------|---------|----------------|
| `age_norm` | `dag - mean(dag)` | mean=0.00, std≈10.96 |
| `age_norm2` | `age_norm^2` | mean≈120, std varies |
| `n_children` | Alias of `num_children_total` | mean≈0.38, max=5 |

### Variables Created - Couples
| Variable | Formula | Expected Stats |
|----------|---------|----------------|
| `age_norm_male` | `dag_male - mean(dag_male)` | mean=0.00, std≈9.75 |
| `age_norm2_male` | `age_norm_male^2` | mean≈95, std varies |
| `n_children_male` | Alias of `num_children_total_male` | mean≈1.17, max=6 |
| `age_norm_female` | `dag_female - mean(dag_female)` | mean=0.00, std≈9.85 |
| `age_norm2_female` | `age_norm_female^2` | mean≈97, std varies |
| `n_children_female` | Alias of `num_children_total_female` | mean≈1.21, max=6 |

---

## Parameters That Should Now Be Estimated

Once MNL dataset is rebuilt, these 11 parameters should be able to move from their initial values:

### Single Males (3 parameters)
- `sm.pref.beta_l_age_norm` - Effect of normalized age on leisure
- `sm.pref.beta_l_age_norm2` - Effect of age-squared on leisure
- `sm.pref.beta_l_n_children` - Effect of number of children on leisure

### Single Females (3 parameters)
- `sf.pref.beta_l_age_norm` - Effect of normalized age on leisure
- `sf.pref.beta_l_age_norm2` - Effect of age-squared on leisure
- `sf.pref.beta_l_n_children` - Effect of number of children on leisure

### Couples (5 parameters)
- `cou.pref.beta_l_age_norm_m` - Effect of male age on male leisure
- `cou.pref.beta_l_age_norm2_m` - Effect of male age-squared on male leisure
- `cou.pref.beta_l0_f` - Female baseline leisure (might be normalization constraint)
- `cou.pref.beta_l_age_norm_f` - Effect of female age on female leisure
- `cou.pref.beta_l_age_norm2_f` - Effect of female age-squared on female leisure

---

## Next Steps

1. **Rebuild MNL Dataset** using updated builder
   ```bash
   python scripts/RURO_prep_mnl_basic.py \
     --singles-draws U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_RURO_draws.parquet \
     --couples-draws U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_RURO_draws.parquet \
     --euromod-combined U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016/combined_draws_em.parquet \
     --out-base U:/EUROMOD-STORAGE/Data/processed/fr/2016 \
     --year 2016
   ```

2. **Verify New Variables** exist in rebuilt dataset

3. **Re-run Joint Estimation** with full iteration limit
   ```bash
   python scripts/RURO_estimate_FR.py \
     --mnl-file U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl.parquet \
     --joint --wage-spec vw \
     --optimizer L-BFGS-B --maxiter 500 \
     --use-numba --n-jobs 32 \
     --out-file outputs/estimates/fr/2016/fr_2016_joint.json
   ```

4. **Check Parameter Movement** - Verify 11 parameters now estimate

5. **Investigate Standard Errors** - Separate issue to address

---

## Technical Notes

### Why Age Normalization?
- Centering age at its mean (age_norm = dag - mean(dag)) creates a variable with mean=0
- Improves numerical stability in optimization
- Makes parameter interpretation clearer (effect at mean age)
- Age-squared captures non-linear age effects

### Why Children Alias?
- Raw variable `num_children_total` already exists with correct data
- Estimation code expects variable named `n_children`
- Creating alias maintains compatibility without data duplication

### Variable Naming Consistency
- Singles: `age_norm`, `age_norm2`, `n_children`
- Couples: `age_norm_male/female`, `age_norm2_male/female`, `n_children_male/female`
- Follows same pattern as other gender-specific variables (`hours_male`, `wage_male`, etc.)

---

## Outstanding Issues

### 1. Standard Errors All NaN
- **Status:** Not addressed in this phase
- **Issue:** All 60 standard errors are NaN in estimation output
- **Likely Cause:** Hessian computation failing or not being computed
- **Next Action:** Investigate numerical Hessian approximation in estimation code

### 2. Parameter Count Discrepancy
- **Status:** Documented but not investigated
- **Stijn's R Code:** 82 parameters
- **Our Python Code:** 60 parameters
- **Difference:** 22 parameters (likely year dummies, regional interactions, or alternative specifications)
- **Next Action:** Compare parameter lists to understand differences

---

## Summary

**Phase 4 Successfully Addresses:**
✅ Missing `age_norm`, `age_norm2`, `n_children` variables
✅ Added to both singles and couples builder functions
✅ Maintains naming consistency with existing variables
✅ Includes debugging logging for verification

**Next Phase Requirements:**
- Rebuild MNL dataset with updated builder
- Re-run estimation to verify parameters now estimate
- Address standard errors NaN issue (separate investigation)

---

**Status:** ✅ **PHASE 4 COMPLETE** - Code changes implemented, ready for testing
