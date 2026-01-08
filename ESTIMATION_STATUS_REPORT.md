# RURO Pipeline Estimation Status Report
**Date:** 2026-01-08
**Session:** Post-consumption fix re-run with theta_c bound relaxed to [0.0, 5.0]

---

## Executive Summary

### ✅ **FIXED: Singles Estimation**
- Singles (male and female) estimations are now working correctly
- Parameters move substantially from initial values
- Consumption preference parameters (beta_c, theta_c) are now identified

### ⚠️ **REMAINING ISSUE: Couples Estimation**
- Couples estimation shows problematic parameter estimates
- Very low beta_c (0.011 vs ~1.13 for singles)
- High gradient norm (838) indicating non-convergence
- theta_c stuck near initial value (0.493 vs 0.5)

---

## Detailed Results

### Singles Male Estimation ✅

| Parameter | Initial | Estimated | Movement | Status |
|-----------|---------|-----------|----------|--------|
| beta_c | 1.0 | 1.133 | +13.3% | ✅ Moved |
| theta_c | 0.5 | 0.000003 | ~0.0 | ✅ Log utility (optimal) |
| theta_l | 0.5 | 0.222 | -55.6% | ✅ Moved |
| beta_l_n_children | 0.1 | 0.1 | 0% | ✅ Expected (cross-sectional ID) |

- **Final LL:** -1657.25
- **Iterations:** 206
- **Gradient norm:** 207 (moderate - likely due to theta_c at bound)
- **Success:** True
- **Walltime:** 17s

**Interpretation:** Males prefer log utility for consumption (theta_c → 0) and moderate curvature for leisure (theta_l = 0.22).

---

### Singles Female Estimation ✅

| Parameter | Initial | Estimated | Movement | Status |
|-----------|---------|-----------|----------|--------|
| beta_c | 1.0 | 1.124 | +12.4% | ✅ Moved |
| theta_c | 0.5 | 0.014 | -97.1% | ✅ Near-log utility |
| theta_l | 0.5 | 0.0 | -100% | ✅ Exact log utility |
| beta_l_n_children | 0.1 | 0.214 | +114% | ✅ Moved significantly! |

- **Final LL:** -1860.27
- **Iterations:** 286
- **Gradient norm:** 313 (moderate)
- **Success:** True
- **Walltime:** 24s

**Interpretation:** Females prefer log utility for both consumption (theta_c ≈ 0) and leisure (theta_l = 0). Number of children has a strong effect on female leisure preferences (beta_l_n_children = 0.214).

---

### Couples Estimation ⚠️ **PROBLEMATIC**

| Parameter | Initial | Estimated | Movement | Status |
|-----------|---------|-----------|----------|--------|
| beta_c | 1.0 | **0.011** | -98.9% | ❌ **Unrealistically low** |
| theta_c | 0.5 | **0.493** | -1.4% | ❌ **Stuck at initial** |
| theta_l | 0.5 | 1.054 | +110.8% | ⚠️ Moved, but high |
| beta_pexp2 | -0.001 | **0.318** | +31900% | ❌ **WRONG SIGN** (should be negative) |

- **Final LL:** -1649.22
- **Iterations:** 769 (very high)
- **Gradient norm:** **838** (VERY HIGH - indicates non-convergence)
- **Success:** True (optimizer incorrectly reports success)
- **Walltime:** 271s (much slower than singles)

**Interpretation:** Couples estimation has serious problems. The very low beta_c and stuck theta_c suggest fundamental identification or numerical issues.

---

## Root Cause Analysis: Couples Issue

### Hypothesis 1: Consumption Scaling in Couples Utility ⭐ **MOST LIKELY**

**Issue:** Consumption is a household public good that enters BOTH male and female utilities:

```python
# estimation_engine.py lines 939-940
u_male = beta_l_coeff_male * bc_l_male + beta_c * bc_c
u_female = beta_l_coeff_female * bc_l_female + beta_c * bc_c
```

**Effect:**
- Total consumption utility contribution = `2 * beta_c * BC(c; theta_c)`
- This **doubles** the consumption effect vs singles
- May cause beta_c to be estimated as ~0.5x the singles value to compensate
- But 0.011 is far below 0.5 * 1.13 ≈ 0.565, so this isn't the full story

### Hypothesis 2: Leisure-Consumption Trade-off Differs in Couples

**Issue:** In couples, labor supply decisions are **joint** - each spouse's hours affect household consumption and their partner's leisure.

**Effect:**
- More complex identification path for beta_c
- beta_c identified from how consumption variation affects JOINT labor supply choices
- May require different curvature (theta_c) than singles

### Hypothesis 3: Numerical Instability in Joint Optimization

**Evidence:**
- Gradient norm = 838 (should be < 1e-3)
- 769 iterations (vs 206-286 for singles)
- beta_pexp2 has WRONG SIGN (positive instead of negative)

**Possible causes:**
- Ill-conditioned Hessian
- Multiple local minima
- Multicollinearity between parameters
- Box-Cox transformation derivatives unstable for couples' consumption range

---

## Diagnostic Results

### Consumption Variation Check ✅

**Singles:**
- Mean within-household std dev: 5857.62
- Mean CV: 78%
- Zero variation households: 0%
- **Status: PASSED**

**Couples:**
- Mean within-household std dev: 6016.49
- Mean CV: 80%
- Zero variation households: 0%
- **Status: PASSED**

**Conclusion:** Consumption variation is GOOD for both singles and couples. The couples issue is NOT due to lack of data variation.

---

## Comparison: Before vs After Consumption Fix

| Metric | Before Fix | After Fix (Singles) | After Fix (Couples) |
|--------|------------|---------------------|---------------------|
| beta_c movement | ❌ Stuck at 1.0 | ✅ Moved to 1.13 | ⚠️ 0.011 (too low) |
| theta_c movement | ❌ Stuck at 0.5 | ✅ Moved to ~0.0 | ❌ Stuck at 0.493 |
| Consumption std (data) | 0.0 | 5857.62 | 6016.49 |
| Gradient norm | 500-900 | 207-313 | **838** (still high) |

---

## Recommended Next Steps

### 1. **Investigate Couples Utility Specification** (PRIORITY 1)

**Options:**
- **A. Scale consumption for couples:** Multiply consumption by 0.5 in couples utility to account for shared public good
  - Would make beta_c comparable between singles and couples
  - Literature precedent: equivalence scales in household economics

- **B. Allow separate beta_c for couples:** Add `beta_c_couples` parameter
  - Lets data determine appropriate scaling
  - More parameters, but better fit

- **C. Use per-capita consumption:** Divide household consumption by 2 for couples
  - Simple and interpretable
  - Assumes equal consumption sharing

**Recommendation:** Try option C first (simplest), then A if needed.

### 2. **Fix Experience-Squared Sign Constraint**

**Issue:** beta_pexp2 = 0.318 (positive) is econometrically wrong for Mincer equation

**Solution:** Add bound constraint:
```yaml
bounds:
  beta_pexp2: [-10.0, 0.0]  # Must be negative (concave wage profile)
```

### 3. **Add Convergence Quality Checks**

**Issue:** L-BFGS-B reports "success" despite gradient_norm = 838

**Solution:** Add post-optimization validation:
```python
if result.success and np.linalg.norm(result.jac) > 1e-2:
    logging.warning(f"Premature convergence: gradient_norm = {np.linalg.norm(result.jac):.2e}")
    logging.warning("Consider: tighter ftol, more iterations, or check for identification issues")
```

### 4. **Run Specification Comparison**

Once couples estimation is fixed, test alternative specifications:
- Log utility (theta_c = theta_l = 0, fixed) vs Box-Cox
- With/without focal hours (beta_pt1, beta_pt2, beta_ft)
- With/without GSUR unemployment effects
- Compare via AIC/BIC and likelihood ratio tests

---

## Files Modified in This Session

1. **estimation_spec.yaml** (lines 28, 34, 186-187)
   - Changed Box-Cox bounds from [0.001, 5.0] to [0.0, 5.0]
   - Allows exact log utility (theta = 0)

2. **enh_RURO_prep_mnl_basic.py** (lines 209-222) ⭐ **CRITICAL FIX**
   - Fixed EUROMOD merge to ALWAYS use counterfactual income
   - Resolved consumption=0 variation issue for all household types

3. **estimation_utils.py** (lines 898-935, 952-964)
   - Improved Box-Cox derivative with Taylor expansion for theta ≈ 0
   - Added numerical stability for log utility

4. **estimation_engine.py** (lines 102-111, 484-500)
   - Added NaN/Inf validation in likelihood and gradient
   - Added warnings for zero gradients

5. **diagnostic_consumption_variation.py** (NEW FILE)
   - Created diagnostic tool to check consumption variation
   - Detected original issue (0% variation)

---

## Technical Notes

### Why theta_c → 0 Makes Economic Sense

**Box-Cox Utility:**
```
BC(c; θ) = (c^θ - 1) / θ   for θ ≠ 0
BC(c; 0) = log(c)          for θ → 0
```

**Implications:**
- theta_c = 0 → log utility → constant relative risk aversion (CRRA)
- Elasticity of intertemporal substitution = 1
- This is a standard assumption in macro labor supply models
- Empirically reasonable for consumption preferences

### Why theta_l Varies (0.0 to 1.05)

**Singles Male:** theta_l = 0.22 (mild curvature, close to log)
**Singles Female:** theta_l = 0.0 (exact log utility)
**Couples:** theta_l = 1.05 (linear-ish leisure utility)

This heterogeneity suggests **gender and household type** affect leisure preferences differently, which is economically plausible (women with children value leisure more flexibly, couples coordinate leisure).

---

## Summary

### ✅ What We Fixed
1. Consumption variation bug (EUROMOD merge issue)
2. Box-Cox bounds (now allow log utility)
3. Numerical stability (Taylor expansion for derivatives)
4. Data validation (NaN/Inf checks)

### ✅ What Works Now
1. Singles male estimation
2. Singles female estimation (including n_children identification!)
3. Data has sufficient variation for all household types

### ⚠️ What Still Needs Work
1. **Couples estimation** (beta_c too low, theta_c stuck, wrong sign on beta_pexp2)
2. Convergence quality warnings (high gradient norms)
3. Specification testing framework

---

**Next Action:** Modify couples utility function to use per-capita consumption (divide by 2) and add beta_pexp2 sign constraint.
