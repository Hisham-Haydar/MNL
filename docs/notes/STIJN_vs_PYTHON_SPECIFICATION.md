# the R reference's R Implementation vs Python Implementation Comparison

**Date:** 2025-12-16
**Purpose:** Verify Python implementation matches the R reference's R specification

---

## Wage Opportunity Specification (from the R reference's R code)

### Formula (Log-Normal PDF)
```r
wopp = ifelse(working==0, 0, -0.5*((log(wage)-lw)/sigma)^2 - log(sigma*wage*sqrt(2*pi)))
```

Where:
- `lw` = mean of log(wage), depends on characteristics
- `sigma` = standard deviation of log(wage)
- Applied ONLY when `working > 0` (zero if not working)

### Parameters

**Male Wage Opportunity** (params 69-73, 79, 81-82):
```r
lw_male = param[69]               # intercept
        + param[70] * educL       # low education
        + param[71] * educH       # high education
        + param[72] * pexp        # experience
        + param[73] * pexp^2      # experience squared
        + param[81] * yd1         # year dummy 1 (SHARED)
        + param[82] * yd2         # year dummy 2 (SHARED)

sigma_male = param[79]            # std deviation
```

**Female Wage Opportunity** (params 74-78, 80, 81-82):
```r
lw_female = param[74]             # intercept
          + param[75] * educL     # low education
          + param[76] * educH     # high education
          + param[77] * pexp      # experience
          + param[78] * pexp^2    # experience squared
          + param[81] * yd1       # year dummy 1 (SHARED)
          + param[82] * yd2       # year dummy 2 (SHARED)

sigma_female = param[80]          # std deviation
```

### Key Features:
1. ✅ **Gender-specific**: Separate parameters for male/female
2. ✅ **Group-shared**: Same params for singles males & couples males
3. ✅ **Year dummies SHARED**: param[81], param[82] used by both genders
4. ✅ **Zero if not working**: `ifelse(working==0, 0, ...)`
5. ✅ **Log-normal distribution**: Uses `log(wage)` as dependent variable

---

## Hours Opportunity Specification (from the R reference's R code)

### Formula
```r
hopp = sum of linear terms in working status indicators and interactions
```

**Male Hours Opportunity** (params 51-59):
```r
hopp_male = param[51] * working           # working indicator
          + param[52] * working_pt1       # part-time 1 (<20 hours)
          + param[53] * working_pt2       # part-time 2 (20-35 hours)
          + param[54] * working_ft        # full-time (>=35 hours)
          + param[55] * working * gsur    # working * GSUR interaction ← GSUR HERE!
          + param[56] * working * regW    # working * region W
          + param[57] * working * regB    # working * region B
          + param[58] * working * educL   # working * low education
          + param[59] * working * educH   # working * high education
```

**Female Hours Opportunity** (params 60-68):
```r
hopp_female = param[60] * working         # working indicator
            + param[61] * working_pt1     # part-time 1
            + param[62] * working_pt2     # part-time 2
            + param[63] * working_ft      # full-time
            + param[64] * working * gsur  # working * GSUR interaction ← GSUR HERE!
            + param[65] * working * regW  # working * region W
            + param[66] * working * regB  # working * region B
            + param[67] * working * educL # working * low education
            + param[68] * working * educH # working * high education
```

### Key Features:
1. ✅ **GSUR used in HOURS opportunity**, NOT wage opportunity
2. ✅ **Interactions with working status**: `working * gsur`, `working * regW`, etc.
3. ✅ **Gender-specific and group-shared**: Same as wage opportunity

---

## Python Implementation Check

### Current Python Implementation (RURO_estimate_FR.py)

Let me check what the Python code is actually doing...

**Expected Python equivalent:**

```python
# Wage opportunity for males (singles + couples)
mean_logw_m = (w_intercept_m
             + w_educL_m * educL_male
             + w_educH_m * educH_male
             + w_pexp_m * pexp_male
             + w_pexp2_m * (pexp_male ** 2)
             + w_yd1 * yd1          # SHARED year dummy
             + w_yd2 * yd2)         # SHARED year dummy

sigma_m = exp(w_log_sigma_m)  # or just w_sigma_m depending on parameterization

# Only for working individuals
w_opp_m = np.where(
    working_male > 0,
    -0.5 * ((np.log(wage_male) - mean_logw_m) / sigma_m)**2 - np.log(sigma_m * wage_male * np.sqrt(2*np.pi)),
    0.0
)

# Similar for females...
```

---

## Critical Issues to Verify in Python Code

### Issue 1: Are Year Dummies Shared?
**the R reference's R**: param[81] and param[82] appear in BOTH male and female equations
**Python**: Need to verify if year dummies are shared or separate

### Issue 2: Is GSUR in Wage Opportunity?
**the R reference's R**: GSUR is ONLY in hours opportunity (`hopp`), NOT in wage opportunity (`wopp`)
**Python**: Need to verify GSUR is not incorrectly included in wage opportunity

### Issue 3: Are Variables Named Correctly After Reshape?
**Required variables for wage opportunity**:
- `wage_male`, `wage_female` (or `yivwg_male`, `yivwg_female`)
- `log(wage_male)`, `log(wage_female)` - WE JUST ADDED THESE ✓
- `educL_male`, `educH_male`, `educL_female`, `educH_female` - Created by reshape ✓
- `pexp_male`, `pexp_female` - Created by reshape ✓
- `pexp2_male`, `pexp2_female` - WE JUST ADDED ALIASES ✓
- `working_male`, `working_female` - WE JUST ADDED THESE ✓
- `yd1`, `yd2` (year dummies - should be household-level, NOT gendered)

**Required variables for hours opportunity**:
- `working_male`, `working_female` - WE JUST ADDED THESE ✓
- `working_pt1_male`, `working_pt2_male`, `working_ft_male` - WE JUST ADDED THESE ✓
- `working_pt1_female`, `working_pt2_female`, `working_ft_female` - WE JUST ADDED THESE ✓
- `gsur_male`, `gsur_female` - WE JUST ADDED THESE ✓
- `educL_male`, `educH_male`, `educL_female`, `educH_female` - Created by reshape ✓
- Regional dummies: `regW`, `regB` (should be household-level, NOT gendered)

---

## Parameter Count Verification

### the R reference's R Implementation (variable wages, "vw"):

**Total: 82 parameters**

Breakdown:
1. **Single Males Utility**: 12 params (indices 1-12)
2. **Single Females Utility**: 13 params (indices 13-25)
3. **Couples Utility**: 26 params (indices 26-50, including interaction)
4. **Hours Opportunity Males**: 9 params (indices 51-59)
5. **Hours Opportunity Females**: 9 params (indices 60-68)
6. **Wage Opportunity Males Mean**: 5 params (indices 69-73: intercept, educL, educH, pexp, pexp2)
7. **Wage Opportunity Females Mean**: 5 params (indices 74-78: intercept, educL, educH, pexp, pexp2)
8. **Wage Opportunity Males Sigma**: 1 param (index 79)
9. **Wage Opportunity Females Sigma**: 1 param (index 80)
10. **Year Dummies (SHARED)**: 2 params (indices 81-82)

**Note**: In the R reference's code, param indices start at 1 (R convention)

### Python Implementation (RURO_estimate_FR.py)

**Expected: 60-62 parameters** (depending on year dummies)

Wait - this is DIFFERENT from the R reference's 82 parameters! Let me check what's different...

**Possible explanations:**
1. Python code might not include year dummies?
2. Python couples utility might have fewer parameters?
3. Python might parameterize differently?

---

## Next Steps

1. ✅ **Verify our MNL builder creates ALL required variables**
   - We just added: `log_wage_male/female`, `pexp2_male/female`, `gsur_male/female`, `working_*_male/female`

2. ⏳ **Check Python estimation code parameterization**
   - Verify parameter count matches or understand differences
   - Check if year dummies are included
   - Verify GSUR is in hours opportunity, NOT wage opportunity

3. ⏳ **Test with rebuilt dataset**
   - Dataset rebuild is running now
   - Will verify all columns exist
   - Run test estimation to see if gradients are non-zero

---

## Summary

**the R reference's Specification is:**
- ✅ Gender-specific wage opportunity (male/female separate)
- ✅ Group-shared opportunity parameters (singles & couples use same)
- ✅ GSUR in HOURS opportunity only (interaction with working status)
- ✅ Log-normal wage opportunity (uses log(wage))
- ✅ Year dummies SHARED between male and female
- ✅ Zero wage opportunity if not working

**Our Python implementation should match this exactly!**

The missing variables we just added to `_build_mnl_block_couples_wide()` are critical for this specification to work.

---

**Status:** Understanding the R reference's specification complete. Need to verify Python implementation matches.
