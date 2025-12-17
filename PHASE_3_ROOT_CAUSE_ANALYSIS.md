# Phase 3 Root Cause Analysis: Opportunity Parameters Still Stuck

**Date:** 2025-12-16
**Status:** Problem NOT fully solved - Zero gradients persist

---

## Problem Summary

After completing Phase 1 (reshape) and Phase 2 (column name updates), the test estimation shows:

```
[JOINT] Gradient norms:
  SM Prefs [0:9]:      1913.891274   ← MOVING ✓
  SF Prefs [9:18]:     2354.956150   ← MOVING ✓
  COU Prefs [18:34]:   2099.910196   ← MOVING ✓
  HOPP_M [34:41]:      0.000000      ← STUCK ❌
  HOPP_F [41:48]:      0.000000      ← STUCK ❌
  WOPP_M [48:54]:      0.000000      ← STUCK ❌
  WOPP_F [54:60]:      0.000000      ← STUCK ❌
```

**All 26 opportunity parameters have ZERO gradients.**

---

## Diagnostic Results

### Dataset Stats
- Total rows: 448,900
- Couples rows: 286,800 ✓ (correct wide format)
- Total columns: 1,471

### Missing Columns (CRITICAL)

#### 1. GSUR Variables (Labor Force Participation Probability)
```
[MISSING] gsur_male
[MISSING] gsur_female
```

**Why critical:** Hours opportunity density requires GSUR probability to model employment/non-employment transitions.

#### 2. Log-Wage Variables
```
[MISSING] log_wage_male
[MISSING] log_wage_female
```

**Why critical:** Wage opportunity density uses log-normal distribution requiring log-transformed wages.

#### 3. Experience Squared (Wrong Naming)
```
[EXISTS] pexp_years2_male  (but estimation code looks for pexp2_male)
[EXISTS] pexp_years2_female  (but estimation code looks for pexp2_female)
```

**Why problematic:** Naming mismatch - estimation code cannot find these variables.

### Existing Columns (Good Variation)

#### Hours-Related ✓
```
hours_male:       mean=35.58, std=19.85, n_unique=284,002
hours_female:     mean=35.50, std=19.86, n_unique=283,993
working_male:     mean=0.97, std=0.16, n_unique=2
working_female:   mean=0.90, std=0.30, n_unique=2
working_pt1_male: mean=0.01, std=0.08, n_unique=2
working_ft_male:  mean=0.25, std=0.43, n_unique=2
```

#### Wage-Related ✓
```
wage_male:        mean=59.84, std=34.73, n_unique=283,933
wage_female:      mean=59.96, std=34.65, n_unique=283,933
pexp_male:        mean=12.72, std=20.99, n_unique=1,236
pexp_female:      mean=11.61, std=19.82, n_unique=1,176
pexp_years2_male: mean=602.47, std=2386.14, n_unique=1,236
```

---

## Root Cause: Incomplete MNL Builder

**File:** `scripts/RURO_prep_mnl_basic.py`
**Function:** `_build_mnl_block_couples_wide()` (lines 146-193)

### What It Currently Does ✓
1. Creates `hours_male/female` from `lhw_male/female`
2. Creates `leisure_male/female`
3. Creates education dummies from `deh_male/female`
4. Creates `pexp_years_male/female` and `pexp_years2_male/female`
5. Creates `consumption` from `ils_dispy`

### What It's MISSING ❌
1. **GSUR variables** - Not created or merged
2. **Log-wage transformations** - No `log_wage_male/female`
3. **Alias for pexp2** - Should also create `pexp2_male = pexp_years2_male`
4. **Working status indicators** - Not explicitly created (may rely on reshape)

---

## Why Opportunity Parameters Can't Be Estimated

### Hours Opportunity Density Formula
```python
# Requires:
- working_male, working_female: Employment status
- gsur_male, gsur_female: Predicted employment probability
- hours_male, hours_female: Observed hours

# Without GSUR → Probability density = 0 → Gradient = 0
```

### Wage Opportunity Density Formula
```python
# Requires:
- log_wage_male, log_wage_female: Log-transformed wages
- pexp2_male, pexp2_female: Experience squared for variance function

# Without log_wage → Cannot compute log-normal density → Gradient = 0
```

---

## Required Fixes

### Fix 1: Add GSUR Variables to Couples Data

**Option A:** Merge GSUR from singles model estimates (if available)
**Option B:** Compute GSUR during MNL building using employment status
**Option C:** Set GSUR = employment rate as approximation

**Recommended:** Option C (quickest) - Use actual employment rate as GSUR proxy:
```python
# In _build_mnl_block_couples_wide():
for gender in ["male", "female"]:
    working_col = f"working_{gender}"
    if working_col in df.columns:
        # Use employment rate as GSUR approximation
        emp_rate = df[working_col].mean()
        df[f"gsur_{gender}"] = emp_rate
        # Or use actual working status as probability:
        df[f"gsur_{gender}"] = df[working_col].astype(float)
```

### Fix 2: Add Log-Wage Transformations

```python
# In _build_mnl_block_couples_wide():
for gender in ["male", "female"]:
    wage_col = f"wage_{gender}"
    if wage_col in df.columns:
        wage = pd.to_numeric(df[wage_col], errors="coerce").fillna(1.0)
        wage = wage.clip(lower=1e-6)  # Avoid log(0)
        df[f"log_wage_{gender}"] = np.log(wage)
```

### Fix 3: Create pexp2 Alias

```python
# In _build_mnl_block_couples_wide():
for gender in ["male", "female"]:
    pexp2_col = f"pexp_years2_{gender}"
    if pexp2_col in df.columns:
        # Create alias for estimation code compatibility
        df[f"pexp2_{gender}"] = df[pexp2_col]
```

### Fix 4: Ensure Working Status Indicators Exist

```python
# In _build_mnl_block_couples_wide():
for gender in ["male", "female"]:
    hours_col = f"hours_{gender}"
    if hours_col in df.columns:
        hours = pd.to_numeric(df[hours_col], errors="coerce").fillna(0.0)

        # Working status
        df[f"working_{gender}"] = (hours > 0).astype(int)
        df[f"working_pt1_{gender}"] = ((hours > 0) & (hours < 20)).astype(int)
        df[f"working_pt2_{gender}"] = ((hours >= 20) & (hours < 35)).astype(int)
        df[f"working_ft_{gender}"] = (hours >= 35).astype(int)
```

---

## Implementation Priority

**HIGH PRIORITY (Critical for opportunity parameters):**
1. ✅ Add `log_wage_male/female` transformations
2. ✅ Add `pexp2_male/female` aliases
3. ✅ Add `gsur_male/female` (use employment rate)

**MEDIUM PRIORITY (Defensive):**
4. ⚠️ Verify `working_*_male/female` indicators exist (check diagnostic)

---

## Expected Outcomes After Fixes

### Before Fixes (Current State)
```
[JOINT] Gradient norms:
  HOPP_M [34:41]:      0.000000  ← No hours opportunity variables
  HOPP_F [41:48]:      0.000000
  WOPP_M [48:54]:      0.000000  ← No wage opportunity variables
  WOPP_F [54:60]:      0.000000
```

### After Fixes (Expected)
```
[JOINT] Gradient norms:
  HOPP_M [34:41]:      XXX.XXXX  ← Non-zero gradients
  HOPP_F [41:48]:      XXX.XXXX
  WOPP_M [48:54]:      XXX.XXXX
  WOPP_F [54:60]:      XXX.XXXX
  Total gradient norm: YYYY.YYYY
```

---

## Test Plan

1. Update `_build_mnl_block_couples_wide()` with missing derived variables
2. Rebuild MNL dataset: `python scripts/RURO_prep_mnl_basic.py ...`
3. Run diagnostic again to verify columns exist
4. Run test estimation (50 iterations)
5. Verify opportunity parameter gradients are non-zero
6. Run full estimation (500 iterations) if test passes
7. Verify all 60 parameters converge

---

## Related Files

- `scripts/RURO_prep_mnl_basic.py` - MNL dataset builder (needs fixes)
- `scripts/RURO_estimate_FR.py` - Estimation code (already updated in Phase 2)
- `COUPLES_DATA_RESHAPE_FIX_PLAN.md` - Original plan (incomplete)
- `PHASE_1_2_COMPLETION_SUMMARY.md` - Phase 1 & 2 summary

---

**Status:** Analysis complete, fixes identified, ready for implementation.
