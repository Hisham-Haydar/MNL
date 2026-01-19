# Ready to Implement: GAMSPy Full Specification

**Date**: 2026-01-17
**Status**: ✅ READY - All prerequisites complete
**Next**: Start implementation

---

## Summary of Work Completed

### Bugs Fixed (6 total)
1. ✅ Box-Cox POWER function → Use exp(θ * log(x))
2. ✅ Status from wrong object → Use model, not result
3. ✅ Wrong attribute names → Use solve_status and status
4. ✅ Box-Cox scaling → Apply to raw values, not scaled
5. ✅ Optimization not running → Remove constraining equations
6. ✅ SciPy joint estimation result saving bug

### Root Cause Identified
**GAMSPy utility is incomplete** - only implements consumption + leisure, missing:
- Hours opportunity (log_h): 10 parameters
- Wage opportunity (log_w): 6 parameters
- Interaction term (beta_interact): 1 parameter
- **Total**: 17 parameters unused → Singular Hessian → "Iterations: 0"

### Complete Utility Specification Extracted
Using Explore agent, extracted full formula from SciPy:
```
V = u + log_h + log_w - log(prior)

where:
  u       = beta_l(Z) * BC(L, theta_l) + beta_c * BC(C, theta_c) [+ interact for couples]
  log_h   = beta_work * working + beta_pt1/pt2/ft * focal_points + interactions
  log_w   = Mincer equation log-likelihood (VW specification)
  prior   = importance sampling correction
```

### Data Variables Verified
All required variables exist in datasets:
- ✅ `hours`, `wage`, `working`, `working_pt1/pt2/ft`
- ✅ `educL`, `educH`, `gsur`, `drgn1`, `pexp_years`
- ✅ `prior` (importance sampling weights)
- ✅ All gender-specific versions for couples

---

## Implementation Plan

### Task 1: Implement log_h for Singles (2-3 hours)

**File**: `scripts/enhanced/gamspy_estimation.py`
**Functions**: `estimate_singles_gamspy()`, `estimate_joint_gamspy()` (singles sections)

**What to add**:
```python
# After computing utility u_j, add hours opportunity log_h_j
hours = data.hours[global_idx]
working = float(data.working[global_idx])  # Pre-computed!
pt1_focal = float(data.working_pt1[global_idx])  # Pre-computed!
pt2_focal = float(data.working_pt2[global_idx])  # Pre-computed!
ft_focal = float(data.working_ft[global_idx])  # Pre-computed!

educL = float(getattr(data, 'educL', np.zeros(1))[global_idx])
educH = float(getattr(data, 'educH', np.zeros(1))[global_idx])
gsur_val = float(data.gsur[global_idx])
female = 1.0 if group == 'singles_female' else 0.0
couple = 0.0  # Singles
idf = float(data.drgn1[global_idx])  # Île-de-France

log_h = (param_vars['beta_work'] * working
       + param_vars['beta_pt1'] * pt1_focal
       + param_vars['beta_pt2'] * pt2_focal
       + param_vars['beta_ft'] * ft_focal
       + param_vars['beta_gsur'] * (gsur_val * working)
       + param_vars['beta_work_educL'] * (educL * working)
       + param_vars['beta_work_educH'] * (educH * working)
       + param_vars['beta_work_female'] * (female * working)
       + param_vars['beta_work_couple'] * (couple * working)
       + param_vars['beta_work_idf'] * (idf * working))

util_j = util_j + log_h
```

### Task 2: Implement log_w for Singles (2-3 hours)

**What to add**:
```python
# After adding log_h, add wage opportunity for workers
if working > 0.5:
    wage_obs = float(data.wage[global_idx])
    pexp = float(data.pexp_years[global_idx])
    pexp2 = pexp * pexp

    # Mincer equation
    mu_wage = (param_vars['beta_w0']
             + param_vars['beta_w_educL'] * educL
             + param_vars['beta_w_educH'] * educH
             + param_vars['beta_pexp'] * pexp
             + param_vars['beta_pexp2'] * pexp2)

    # Log-likelihood of observed wage
    log_wage_obs = gp_log(wage_obs + LOG_EPS)
    residual = log_wage_obs - mu_wage
    sigma_param = param_vars['sigma']

    log_w = -0.5 * (residual * residual) / (sigma_param * sigma_param + LOG_EPS) \
            - gp_log(sigma_param + LOG_EPS) \
            - 0.5 * gp_log(2.0 * math.pi)

    util_j = util_j + log_w
```

### Task 3: Implement log_h for Couples (1-2 hours)

**What to add**:
```python
# Male hours opportunity
hours_m = data.hours_male[global_idx]
working_m = float(data.working_male[global_idx])
# ... same formula as singles, using male demographics

# Female hours opportunity
hours_f = data.hours_female[global_idx]
working_f = float(data.working_female[global_idx])
# ... same formula as singles, using female demographics, with female=1.0

util_j = util_j + log_h_m + log_h_f
```

### Task 4: Implement log_w for Couples (1-2 hours)

**What to add**:
```python
# Male wage opportunity (if working)
if working_m > 0.5:
    wage_male = data.wage_male[global_idx]
    # ... Mincer equation using male characteristics

# Female wage opportunity (if working)
if working_f > 0.5:
    wage_female = data.wage_female[global_idx]
    # ... Mincer equation using female characteristics

util_j = util_j + log_w_m + log_w_f
```

### Task 5: Add Interaction Term for Couples (30 min)

**What to add**:
```python
# After computing BC(l_m) and BC(l_f)
interact_term = param_vars['beta_interact'] * bc_l_m * bc_l_f
util_j = util_j + interact_term
```

### Task 6: Add Importance Sampling Correction (30 min)

**What to add**:
```python
# After all components, subtract log(prior)
prior_j = float(data.prior[global_idx])
log_prior = gp_log(prior_j + LOG_EPS)
util_j = util_j - log_prior
```

---

## Testing Strategy

### Incremental Approach
1. **Baseline**: Current GAMSPy → LL = -10408, Iterations: 0
2. **+log_h**: Expect LL improvement, parameters move
3. **+log_w**: Expect further improvement
4. **+interact+prior**: Expect LL ≈ -5148 (match SciPy!)

### Success Criteria
- ✅ LL ≈ -5148 (within 1 LL unit of SciPy)
- ✅ All 49 parameters within 1% of SciPy
- ✅ Iterations > 0 (optimizer actually runs!)
- ✅ Hessian invertible (model identified)
- ✅ Walltime < 15 min (vs 20 min for SciPy)

---

## Key Implementation Details

### Use Pre-Computed Variables
The data already has:
- `working`, `working_pt1`, `working_pt2`, `working_ft`
- No need to compute focal point indicators!

### Handle Zero Division
```python
# Always add small epsilon to avoid division by zero
sigma_param = param_vars['sigma']
... / (sigma_param * sigma_param + LOG_EPS)
```

### Conditional Logic for Workers
```python
# Only compute log_w for workers (hours > 0)
if working > 0.5:  # Use 0.5 threshold since working is float
    log_w = ...
    util_j = util_j + log_w
```

### Group Indicators
```python
female = 1.0 if group == 'singles_female' else 0.0
couple = 0.0  # For singles
couple = 1.0  # For couples
```

---

## Files to Modify

1. **scripts/enhanced/gamspy_estimation.py**:
   - Lines ~1080-1120: Singles male utility (add log_h, log_w)
   - Lines ~1148-1180: Singles female utility (add log_h, log_w)
   - Lines ~1213-1270: Couples utility (add log_h×2, log_w×2, interact)

2. **Test after each modification**:
   - Run GAMSPy estimation
   - Check LL improves
   - Check parameters move from initial values

---

## Expected Outcomes

### Before (Current)
```
LL: -10408.9232
Iterations: 0
Parameters: 19 unused, rest at suboptimal values
Hessian: Singular
Walltime: 4.5 minutes (but wrong!)
```

### After (Full Specification)
```
LL: ~-5148 (matches SciPy!)
Iterations: 50-200
Parameters: All 49 used and optimized
Hessian: Invertible
Walltime: 5-15 minutes (10x faster than SciPy!)
```

**LL improvement**: ~5260 log-likelihood units!

---

## User's Future Goals

After GAMSPy works with current specification:

1. **Occupation-specific wage/hours distributions**
   - Multiple wage equations by occupation
   - Joint modeling of occupation + hours choice

2. **Hours peaks from data** (match Stijn's specification)
   - Empirical focal points from hours distribution
   - More flexible than fixed pt1/pt2/ft

3. **Multiple specifications**
   - Test AC2013, v2, loc_empirical YAMLs
   - Compare model fit across specifications

---

**Created**: 2026-01-17 15:50
**Status**: ✅ READY TO IMPLEMENT
**Estimated Time**: 8-10 hours total
**Next Action**: Start with Task 1 (log_h for singles)

---
