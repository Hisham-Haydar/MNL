# GAMSPy Full Specification Implementation Plan

**Date**: 2026-01-17
**Goal**: Update GAMSPy to match complete SciPy utility specification
**Estimated Time**: 8-12 hours

---

## Current Status

**GAMSPy implements** (INCOMPLETE):
```
V_j = u_j
    = beta_c * BC(C_j, theta_c) + beta_l(demographics) * BC(L_j, theta_l)
```

**SciPy implements** (COMPLETE):
```
V_j = u_j + log_h_j + log_w_j - log(prior_j)

where:
  u_j         = utility from consumption and leisure
  log_h_j     = hours opportunity density (focal points + working costs)
  log_w_j     = wage opportunity density (Mincer equation)
  log(prior_j) = importance sampling correction
```

**Missing in GAMSPy**: `log_h` (10 parameters) + `log_w` (6 parameters) = **16 parameters unused!**

---

## Complete Utility Specification from SciPy

### 1. Utility Component (u)

**Singles**:
```
u_singles = beta_l_coeff * BC(leisure, theta_l) + beta_c * BC(consumption, theta_c)

where beta_l_coeff = beta_l0 + beta_l_age_norm * age_norm
                              + beta_l_age_norm2 * age_norm2
                              + beta_l_educL * educL
                              + beta_l_educH * educH
                              + beta_l_n_children * n_children  [females only]
```

**Couples**:
```
u_couples = beta_l_coeff_male * BC(l_m, theta_l_m)
          + beta_l_coeff_female * BC(l_f, theta_l_f)
          + beta_c * BC(c_household, theta_c)  [household consumption]
          + beta_interact * BC(l_m, theta_l_m) * BC(l_f, theta_l_f)
```

**Status**: ✅ Already implemented in GAMSPy (except beta_interact for couples)

### 2. Hours Opportunity Component (log_h)

**Formula**:
```
log_h = beta_work * I(working)
      + beta_pt1 * I(pt1_focal)       # ~20h focal point
      + beta_pt2 * I(pt2_focal)       # ~30h focal point
      + beta_ft * I(ft_focal)          # ~40h focal point
      + beta_gsur * (gsur * working)
      + beta_work_educL * (educL * working)
      + beta_work_educH * (educH * working)
      + beta_work_female * (female * working)
      + beta_work_couple * (couple * working)
      + beta_work_idf * (idf * working)
```

**What it represents**: Cost/benefit of working at different hours levels
- `beta_work`: Base cost/benefit of working (vs not working)
- `beta_pt1/pt2/ft`: Focal point bonuses (people cluster at standard hours)
- `beta_gsur`: Group-specific unemployment rate effect
- Interaction terms: How education, gender, couple status, region affect work propensity

**Status**: ❌ NOT implemented in GAMSPy

**Parameters needed** (10):
- beta_work, beta_pt1, beta_pt2, beta_ft
- beta_gsur, beta_work_educL, beta_work_educH
- beta_work_female, beta_work_couple, beta_work_idf

### 3. Wage Opportunity Component (log_w)

**Formula** (Variable Wages - "vw" specification):
```
μ(X) = beta_w0 + beta_w_educL * educL
                + beta_w_educH * educH
                + beta_pexp * pexp_years
                + beta_pexp2 * pexp_years²

log_w = -0.5 * [(log(wage) - μ)² / σ²] - log(σ) - 0.5 * log(2π)
```

Applied only for workers (hours > 0), zero otherwise.

**What it represents**: Log-likelihood of observed wage given characteristics
- Mincer equation: log wage = f(education, experience)
- Explains wage variation in data
- Helps identify hours choice from wage effects

**Status**: ❌ NOT implemented in GAMSPy

**Parameters needed** (6):
- beta_w0, beta_w_educL, beta_w_educH
- beta_pexp, beta_pexp2, sigma

### 4. Importance Sampling Correction (log_prior)

**Formula**:
```
log(prior_j) = log(probability that alternative j was drawn in RURO procedure)
```

**Status**: ❓ Need to check if this is in data as a column

---

## Implementation Tasks

### Task 1: Add Hours Opportunity to Singles (2-3 hours)

**File**: `scripts/enhanced/gamspy_estimation.py`

**Function**: `estimate_singles_gamspy()` and `estimate_joint_gamspy()` (singles sections)

**Implementation**:
```python
# After computing utility u_j, add log_h_j
for global_idx in range(start_idx, end_idx):
    # ... existing utility computation ...

    # Hours opportunity density
    hours = data.hours[global_idx]  # Actual hours worked
    working = float(hours > 0)  # 0/1 indicator

    # Focal point indicators
    pt1_focal = float(15 <= hours < 25)  # Part-time 1 ~20h
    pt2_focal = float(25 <= hours < 35)  # Part-time 2 ~30h
    ft_focal = float(hours >= 35)        # Full-time ~40h

    # Get demographic variables
    educL = float(getattr(data, 'educL', None)[global_idx]) if hasattr(data, 'educL') else 0.0
    educH = float(getattr(data, 'educH', None)[global_idx]) if hasattr(data, 'educH') else 0.0
    gsur_val = float(getattr(data, 'gsur', None)[global_idx]) if hasattr(data, 'gsur') else 0.0
    female = 1.0 if group == 'singles_female' else 0.0
    couple = 0.0  # Singles
    idf = float(getattr(data, 'drgn1', None)[global_idx]) if hasattr(data, 'drgn1') else 0.0

    # Build log_h expression
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

    # Add to utility
    util_j = util_j + log_h
```

**Challenges**:
- Need to check if data has `drgn1` (Île-de-France indicator) or similar location variable
- Focal point thresholds might need adjustment based on French labor market

### Task 2: Add Wage Opportunity to Singles (2-3 hours)

**Implementation**:
```python
# After adding log_h, add log_w for workers
if working > 0.5:  # If working
    wage_obs = float(data.wage[global_idx])

    # Get experience (or proxy from age)
    pexp = float(getattr(data, 'pexp_years', None)[global_idx]) if hasattr(data, 'pexp_years') else 0.0
    pexp2 = pexp * pexp

    # Mincer equation for predicted log wage
    mu_wage = (param_vars['beta_w0']
             + param_vars['beta_w_educL'] * educL
             + param_vars['beta_w_educH'] * educH
             + param_vars['beta_pexp'] * pexp
             + param_vars['beta_pexp2'] * pexp2)

    # Log-likelihood of observed wage
    from gamspy.math import log as gp_log
    log_wage_obs = gp_log(wage_obs + LOG_EPS)
    residual = log_wage_obs - mu_wage
    sigma_param = param_vars['sigma']

    log_w = -0.5 * (residual * residual) / (sigma_param * sigma_param + LOG_EPS) \
            - gp_log(sigma_param + LOG_EPS) \
            - 0.5 * gp_log(2.0 * math.pi)

    util_j = util_j + log_w
```

**Challenges**:
- Need to check if data has `wage` column (it does based on validation output)
- Need to check if data has `pexp_years` or compute from age
- Division by sigma requires careful handling to avoid zero

### Task 3: Add Importance Sampling Correction (1 hour)

**Implementation**:
```python
# After adding log_w, subtract log_prior
if hasattr(data, 'prior') or hasattr(data, 'draw_prob'):
    prior_j = float(getattr(data, 'prior', getattr(data, 'draw_prob', 1.0))[global_idx])
    log_prior = gp_log(prior_j + LOG_EPS)
    util_j = util_j - log_prior
```

### Task 4: Add Hours Opportunity to Couples (1-2 hours)

**Implementation**:
```python
# Compute log_h separately for male and female
hours_male = data.hours_male[global_idx]
hours_female = data.hours_female[global_idx]

# Male hours opportunity
working_m = float(hours_male > 0)
log_h_m = ... # Same formula as singles, using male demographics

# Female hours opportunity
working_f = float(hours_female > 0)
log_h_f = ... # Same formula as singles, using female demographics

util_j = util_j + log_h_m + log_h_f
```

### Task 5: Add Wage Opportunity to Couples (1-2 hours)

**Implementation**:
```python
# Compute log_w separately for male and female
if working_m > 0.5:
    wage_male = data.wage_male[global_idx]
    log_w_m = ... # Same formula as singles

if working_f > 0.5:
    wage_female = data.wage_female[global_idx]
    log_w_f = ... # Same formula as singles

util_j = util_j + log_w_m + log_w_f
```

### Task 6: Add Interaction Term to Couples (30 min)

**Implementation**:
```python
# After computing BC(l_m, theta_l_m) and BC(l_f, theta_l_f)
bc_l_m = boxcox_gamspy(l_m_val, param_vars[theta_l_m_param])
bc_l_f = boxcox_gamspy(l_f_val, param_vars[theta_l_f_param])

# Add interaction term
interact_term = param_vars['beta_interact'] * bc_l_m * bc_l_f
util_j = util_j + interact_term
```

**Status**: Currently missing from couples utility

---

## Testing Strategy

### Phase 1: Incremental Testing
1. **Baseline**: Run current GAMSPy (LL = -10408)
2. **+log_h**: Add hours opportunity only → expect LL to improve
3. **+log_w**: Add wage opportunity → expect LL to improve further
4. **+interact**: Add interaction term → expect LL ≈ -5148

### Phase 2: Parameter Validation
For each phase, check:
- Do the new parameters move from initial values?
- Are they within reasonable bounds?
- Do signs make sense? (e.g., beta_work < 0 = working is costly)

### Phase 3: Full Comparison with SciPy
- LL difference < 1 unit
- All 49 parameters within 1% of SciPy
- Convergence diagnostics match

---

## Data Requirements

Need to verify these columns exist in MNL datasets:
- ✅ `hours` (or `hours_male`, `hours_female` for couples)
- ✅ `wage` (or `wage_male`, `wage_female` for couples)
- ✅ `educL`, `educH` (validated in logs)
- ✅ `gsur` (validated in logs)
- ❓ `drgn1` or `loc4` (location variable)
- ❓ `pexp_years` (experience) - may need to compute from age
- ❓ `prior` or `draw_prob` (importance sampling weights)

**Action**: Check data structure in `estimation_utils.py` to confirm variable names

---

## Expected Outcomes

### Before (Current GAMSPy)
```
LL: -10408.9232
Iterations: 0 (local optimum with incomplete utility)
19 parameters unused (beta_work, beta_w0, etc.)
Hessian: Singular
```

### After (Full Specification)
```
LL: ~-5148 (matching SciPy!)
Iterations: 50-200
All 49 parameters used
Hessian: Invertible
Walltime: 5-15 minutes (vs 20 min for SciPy)
```

**LL improvement**: ~5260 log-likelihood units!

---

## Implementation Order

1. ✅ Fix SciPy joint estimation bug (DONE)
2. ✅ Understand complete utility specification (DONE)
3. ⏳ Implement log_h for singles
4. ⏳ Implement log_w for singles
5. ⏳ Test singles utility (should match SciPy singles results)
6. ⏳ Implement log_h for couples
7. ⏳ Implement log_w for couples
8. ⏳ Implement beta_interact for couples
9. ⏳ Test joint utility (should match SciPy joint results)
10. ⏳ Document and finalize

**Estimated total time**: 8-12 hours

---

## Future Extensions (User's Goals)

After getting GAMSPy working with current specification:

### 1. Occupation-Specific Wage/Hours Distributions
- Add occupation indicators to data
- Estimate separate wage equations by occupation
- Model occupation choice jointly with hours

### 2. Hours Peaks (Stijn's specification)
- Add explicit focal point parameters for observed hours clusters
- Identify empirical peaks in data (e.g., 20h, 35h, 39h, 40h)
- More flexible than fixed pt1/pt2/ft categories

### 3. Multiple Specifications
- Test `estimation_spec_AC2013.yaml` (Aaberge-Colombino 2013)
- Test `estimation_spec_v2.yaml` (regional interactions)
- Test `estimation_spec_loc_empirical.yaml` (location-specific)

---

**Plan Created**: 2026-01-17 15:35
**Ready to implement**: ✅ YES
**First task**: Implement log_h for singles

---
