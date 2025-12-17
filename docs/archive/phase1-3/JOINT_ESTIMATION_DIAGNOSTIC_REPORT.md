# Joint Estimation Diagnostic Report

**Date:** 2025-12-16
**Issue:** Couples and opportunity parameters not being estimated in joint mode
**Status:** ❌ **CRITICAL BUGS IDENTIFIED**

---

## Executive Summary

Joint estimation is **FAILING to estimate 44 out of 60 parameters** (73%). Only singles preference parameters are being optimized; couples and opportunity parameters remain at their initial values despite couples representing 78% of the dataset.

###Root Causes Identified:

1. **Possible Missing Interaction Term** in couples utility (needs verification)
2. **Initial Values Loading Issue** - estimation starts from previous run's values
3. **Gradient Computation Issue** - couples/opportunity gradients may be zero
4. **Standard Errors Not Computed** - Hessian calculation failing

---

## Detailed Findings

### 1. Parameter Movement Analysis

**Parameters that MOVED (estimated successfully):**
- Singles Males [0-8]: ✅ Changed by -2.71 to +6.84
- Singles Females [9-17]: ✅ Changed by -1.76 to +7.70

**Parameters that DID NOT MOVE (not estimated):**
- Couples Preferences [18-33]: ❌ ALL stayed at initial values (16 params)
- Hours Opportunity Male [34-40]: ❌ Near-zero or unchanged (7 params)
- Hours Opportunity Female [41-47]: ❌ Near-zero or unchanged (7 params)
- Wage Opportunity Male [48-53]: ❌ Exact initial values (6 params)
- Wage Opportunity Female [54-59]: ❌ Exact initial values (6 params)

### 2. Data Verification

✅ **Couples data EXISTS and is LOADED:**
- Single Males: 739 households (73,900 rows) - 10%
- Single Females: 882 households (88,200 rows) - 12%
- Couples: 2,900 households (580,000 rows) - **78%** of dataset!

✅ **Joint estimation code structure is CORRECT:**
- Properly sums log-likelihoods from all three groups
- Gradients are mapped correctly to joint parameter vector
- Data filtering logic is correct

### 3. Couples Utility Specification Issue

**Current Implementation ([scripts/RURO_estimate_FR.py:3574](scripts/RURO_estimate_FR.py#L3574)):**
```python
u = beta_leisure_m * lm_bc + beta_leisure_f * lf_bc + beta_c * c_bc
```

**User's Specification:**
```
U_ij = B_C_coup * consumption_bc +
       B_l_coupM * leisure_M_bc +
       B_l_coupF * leisure_F_bc +
       B_interact * leisure_M * leisure_F  # ← MISSING in code?
```

**Analysis:**
- Parameter count in results: 16 couples preferences
- Breakdown: Male (6) + Female (6) + Shared (4) = 16
- Shared params: beta_c, theta_lm, theta_lf, theta_c
- **NO interaction parameter** in the count!

**Question:** Was the interaction term intentionally removed in the "SIMPLIFIED" specification, or is it missing?

### 4. Opportunity Parameters

**Hours Opportunity (hopp):**
- Expected: Coefficients for work status, part-time, full-time, GSUR, education
- Actual: ALL near-zero (~1e-16) or 0.5
- **Issue:** No variation or identification

**Wage Opportunity (wopp):**
- Expected: Log-wage equation coefficients
- Actual: ALL at exact initial values (2.5, -0.1, 0.2, 0.02, -0.001, 0.4)
- **Issue:** Parameters not being updated by optimizer

### 5. Standard Errors

❌ **None computed**
- All `std_error`, `t_value`, `p_value` columns are empty
- Post-estimation attempted but couldn't compute Hessian
- Possible reasons:
  1. Hessian is singular (parameters not identified)
  2. Gradient function not accessible in CLI mode
  3. Numerical issues with Box-Cox parameters

### 6. Negative Marginal Utilities

⚠️ **12.3% of observations** have negative marginal utilities:
- Negative MU of consumption: 1,621 obs (12.3%)
- Negative MU of leisure: 1,615 obs (12.2%)

This is **economically invalid** and indicates:
- Poor parameter values
- Model misspecification
- Or computation errors

---

## Technical Analysis

### Joint Estimation Workflow

**Step 1: Load Data ✅**
```python
# Line 5400-5402
df_sm = df_full[(df_full["ruro_group"] == 1) & (df_full["dgn"] == 1)]  # 739 individuals
df_sf = df_full[(df_full["ruro_group"] == 1) & (df_full["dgn"] == 0)]  # 882 individuals
df_cou = df_full[df_full["ruro_group"] == 10]  # 2,900 households
```

**Step 2: Precompute Data ✅**
```python
# Line 5422-5424
data_sm = precompute_data_singles(df_sm, is_male=True)   ✓
data_sf = precompute_data_singles(df_sf, is_male=False)  ✓
data_cou = precompute_data_couples(df_cou)               ✓
```

**Step 3: Load Initial Parameters ⚠️**
```bash
--init-params "U:\Desktop\Nizam_Hisham\MNL\outputs\estimates\fr\2016\fr_2016_joint.json"
```
**Issue:** Estimation loads from previous run, which had couples/opportunity params at defaults!

**Step 4: Joint Objective Function ✅**
```python
# Line 5057-5160
ll_total -= neg_ll_sm   # Singles males contribution
ll_total -= neg_ll_sf   # Singles females contribution
ll_total -= neg_ll_cou  # Couples contribution ✓
```

**Step 5: Optimization ❓**
```python
# L-BFGS-B optimizer with bounds
# Converged in 35 iterations
# Final LL: -22,207.35
```
**Issue:** Only singles parameters moved!

---

## Probable Root Causes

### Hypothesis 1: Gradient is Zero (MOST LIKELY)

**Evidence:**
- Optimizer converged quickly (35 iterations)
- Only some parameters moved
- Others stayed exactly at initial values

**Possible reasons:**
1. **Data has no variation** in couples/opportunity dimensions
   - Hours opportunity: Maybe all at same category?
   - Wage draws: Maybe not varying enough?
2. **Gradient computation bug** in couples/opportunity functions
3. **Parameters not identifiable** with current model specification

### Hypothesis 2: Initial Values at Local Optimum

**Evidence:**
- Using `--init-params` from previous run
- Previous run had same issue (circular problem!)

**Solution:** Start from DIFFERENT initial values

### Hypothesis 3: Model Misspecification

**Evidence:**
- Missing interaction term in couples utility?
- 12% negative marginal utilities
- Poor parameter interpretability

---

## Recommended Actions

### IMMEDIATE (Priority 1)

**1. Test Singles-Only Estimation First**
```bash
# Test single males only
python scripts/RURO_estimate_FR.py \
  --mnl-file "path/to/fr_2016_RURO_mnl.parquet" \
  --group 1 --sex m \
  --wage-spec vw \
  --optimizer L-BFGS-B \
  --maxiter 500 \
  --use-numba \
  --out-file "outputs/test_sm_only.json"
```
**Purpose:** Verify singles estimation works independently

**2. Run Joint WITHOUT --init-params**
```bash
# Start from default initial values, NOT previous run
python scripts/RURO_estimate_FR.py \
  --mnl-file "path/to/fr_2016_RURO_mnl.parquet" \
  --joint \
  --wage-spec vw \
  --optimizer L-BFGS-B \
  --maxiter 2000 \
  --use-numba \
  --n-jobs 32 \
  --out-file "outputs/joint_fresh_start.json"
  # NOTE: NO --init-params flag!
```

**3. Add Diagnostic Logging**
Add these print statements to `fast_neg_ll_with_grad_joint()` at line 5160:
```python
# Before return statement
print(f"DEBUG: SM LL contribution: {ll_sm if data_sm else 0:.2f}")
print(f"DEBUG: SF LL contribution: {ll_sf if data_sf else 0:.2f}")
print(f"DEBUG: COU LL contribution: {ll_cou if data_cou else 0:.2f}")
print(f"DEBUG: Total LL: {ll_total:.2f}")
print(f"DEBUG: Grad norm SM: {np.linalg.norm(grad[0:9]):.4f}")
print(f"DEBUG: Grad norm SF: {np.linalg.norm(grad[9:18]):.4f}")
print(f"DEBUG: Grad norm COU: {np.linalg.norm(grad[18:34]):.4f}")
print(f"DEBUG: Grad norm HOPP_M: {np.linalg.norm(grad[34:41]):.4f}")
print(f"DEBUG: Grad norm HOPP_F: {np.linalg.norm(grad[41:48]):.4f}")
if wage_spec == "vw":
    print(f"DEBUG: Grad norm WOPP_M: {np.linalg.norm(grad[48:54]):.4f}")
    print(f"DEBUG: Grad norm WOPP_F: {np.linalg.norm(grad[54:60]):.4f}")
```

### SHORT TERM (Priority 2)

**4. Verify Couples Utility Specification**
- Check R reference file `scratch/Ruro_estimation_new.Rmd` for interaction term
- If interaction exists in R but not Python → ADD IT
- If it doesn't exist in R → current implementation is correct

**5. Check Data Variation**
Create diagnostic script to verify:
- Couples consumption varies across alternatives
- Hours vary across draws
- Wages vary across draws (if vw spec)

**6. Inspect Gradient Values**
During first iteration, print:
- Gradient for each parameter group
- Check if couples/opportunity gradients are truly zero

### MEDIUM TERM (Priority 3)

**7. Fix Standard Errors Computation**
- Either integrate Hessian calculation into estimation
- Or use numerical Hessian via `numdifftools`
- Or switch to optimizer that returns Hessian (trust-constr)

**8. Address Negative Marginal Utilities**
- Add constraints to ensure MU > 0
- Or reparameterize utility function
- Or check if data normalization is correct

---

## Success Criteria

Estimation is successful when:
- ✅ All 60 parameters move from initial values (change > 0.01)
- ✅ Couples parameters have reasonable magnitudes (not 0 or 1)
- ✅ Opportunity parameters are non-zero and interpretable
- ✅ Standard errors computed successfully
- ✅ Negative marginal utilities < 5%
- ✅ Log-likelihood improves from initial values
- ✅ Convergence message is NORM_OF_PROJECTED_GRADIENT or REL_REDUCTION

---

## Files to Inspect

1. **[scripts/RURO_estimate_FR.py](scripts/RURO_estimate_FR.py)**
   - Line 5016-5160: `fast_neg_ll_with_grad_joint()` - joint objective
   - Line 3460-3800: `fast_neg_ll_with_grad_couples()` - couples likelihood
   - Line 5400-5404: Data filtering for joint estimation

2. **[scratch/Ruro_estimation_new.Rmd](scratch/Ruro_estimation_new.Rmd)**
   - R reference implementation
   - Check for couples utility specification
   - Verify if interaction term exists

3. **[outputs/estimates/fr/2016/fr_2016_joint.json](outputs/estimates/fr/2016/fr_2016_joint.json)**
   - Current (problematic) results
   - Compare theta0 vs theta to see parameter movement

---

## Contact for Questions

- Utility specification: Verify with user (interaction term?)
- R reference code: Check `scratch/Ruro_estimation_new.Rmd`
- Data issues: Inspect MNL dataset directly

---

**END OF REPORT**
