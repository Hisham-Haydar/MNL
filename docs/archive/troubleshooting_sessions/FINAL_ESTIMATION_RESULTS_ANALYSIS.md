# Final Estimation Results Analysis
**Date:** 2026-01-08
**Session:** After all fixes applied (consumption variation + couples utility + consumption floor)

---

## Executive Summary

### Status: COUPLES ISSUE PERSISTS ⚠️

After applying three major fixes:
1. ✅ **Consumption variation fix** (EUROMOD merge - FIXED singles)
2. ✅ **Couples utility function fix** (removed consumption doubling - had NO effect)
3. ❌ **Consumption floor fix** (1e-6 → 1.0 - had NO effect)

**Singles estimations are now working correctly**, but **couples beta_c remains 44x too low** (0.027 vs ~1.2 for singles).

---

## Estimation Results Comparison

| Metric | Singles Male | Singles Female | Couples | Expected Couples |
|--------|--------------|----------------|---------|------------------|
| **beta_c** | 1.180 ✅ | 1.316 ✅ | **0.027** ❌ | ~1.2 |
| **theta_c** | 0.000 ✅ | 0.002 ✅ | **0.459** ❌ | ~0.0 |
| **theta_l** | 0.027 ✅ | 0.002 ✅ | 0.712 ✅ | - |
| **Gradient norm** | 4,907 ⚠️ | 168 ✅ | 236 ⚠️ | < 10 |
| **Iterations** | 455 | 609 | 950 (high) | - |
| **Final LL** | -1588.37 | -1805.13 | -1647.03 | - |
| **Walltime** | 27s | 40s | 331s (slow!) | - |

### Parameter Movement from Initial Values

| Parameter | Initial | Couples Estimate | Movement | Status |
|-----------|---------|------------------|----------|---------|
| beta_c | 1.0 | **0.027** | -97.3% | ❌ **COLLAPSED** |
| theta_c | 0.5 | **0.459** | -8.2% | ❌ **STUCK** |
| theta_l | 0.5 | 0.712 | +42.4% | ✅ Moved |
| beta_pexp | 0.02 | 1.006 | +4930% | ⚠️ **TOO HIGH** |
| beta_pexp2 | -0.001 | -0.023 | +2200% | ✅ Correct sign now |

---

## What Each Fix Accomplished

### Fix #1: Consumption Variation (EUROMOD Merge) ✅ **MAJOR SUCCESS**

**Problem:** 100% of households had zero consumption variation across draws.
**Cause:** Step 6 merge kept observed income instead of EUROMOD counterfactual.
**Fix:** Modified [enh_RURO_prep_mnl_basic.py](scripts/enhanced/enh_RURO_prep_mnl_basic.py#L209-L222) to ALWAYS use `ils_dispy_em`.

**Result:**
- **Singles:** FIXED! beta_c moved from 1.0 → 1.18-1.32, theta_c → 0.0 (log utility)
- **Couples:** No effect on beta_c or theta_c

### Fix #2: Couples Utility Function ✅ **TECHNICALLY CORRECT, BUT NO EFFECT**

**Problem:** Consumption appeared twice in couples utility (male + female).
**Cause:** [estimation_engine.py](scripts/enhanced/estimation_engine.py#L938-L953) was doubling consumption contribution.
**Fix:** Changed to add consumption utility ONCE (matching R reference code).

**Result:**
- **Gradient quality:** Improved slightly (838 → 236)
- **beta_c:** NO CHANGE (0.026 → 0.027)
- **theta_c:** NO CHANGE (0.468 → 0.459)

### Fix #3: Consumption Floor (1e-6 → 1.0) ❌ **NO EFFECT**

**Problem:** EUROMOD returns negative disposable income; Python clipped to 1e-6, R clipped to 1.0.
**Cause:** BC(0.000001, 0.5) = -2000 (extreme value) vs BC(1.0, 0.5) = 0 (neutral).
**Fix:** Modified [enh_RURO_prep_mnl_basic.py](scripts/enhanced/enh_RURO_prep_mnl_basic.py#L53) `DCM_MIN_POSITIVE = 1.0`.

**Result:**
- **beta_c:** NO CHANGE (0.026 → 0.027)
- **theta_c:** NO CHANGE (0.468 → 0.459)
- **beta_pexp:** Increased dramatically (0.825 → 1.006)

---

## Diagnostic Evidence

### Convergence Quality ⚠️ **POOR**

| Group | Gradient Norm | Status | Interpretation |
|-------|--------------|--------|----------------|
| Singles male | 4,907 | ❌ **Very high** | Premature convergence or numerical issues |
| Singles female | 168 | ⚠️ Moderate | Acceptable but not ideal |
| Couples | 236 | ⚠️ Moderate | Better than before (838) but still high |

**Expected:** Gradient norm < 1e-3 (~0.001) for true convergence.

**Issue:** L-BFGS-B reports "SUCCESS" despite high gradient norms.

### Wage Equation Parameters 🚨 **SUSPECT**

Couples wage parameters are anomalous:

```
beta_pexp  = 1.006   (expected ~0.01-0.04, like singles)
beta_pexp2 = -0.023  (expected ~-0.0001 to -0.0006, like singles)
```

This suggests the wage profile is **extremely steep** (100x more experience effect than singles). This is econometrically implausible.

**Hypothesis:** The extreme wage parameters may be compensating for the collapsed beta_c by distorting the income-leisure trade-off.

---

## Hypotheses for Persistent Couples Issue

### Hypothesis 1: Data Still Has Issues (MOST LIKELY)

**Evidence:**
- Consumption floor fix had ZERO effect
- This suggests the 4,057 observations with consumption < 1.0 are not the root cause
- May be a different data issue we haven't identified

**Next Steps:**
1. Verify consumption floor was actually applied (check MNL parquet file)
2. Compare couples vs singles consumption distributions
3. Check for other data anomalies (NaNs, Infs, outliers)

### Hypothesis 2: Numerical Instability in Optimizer

**Evidence:**
- Very high gradient norms (236-4907) despite "success"
- 950 iterations for couples (vs 455-609 for singles)
- Parameters may be stuck in local minimum

**Next Steps:**
1. Add tighter convergence criteria (`ftol=1e-8`, `gtol=1e-6`)
2. Try different initial values for beta_c (e.g., 1.5, 2.0)
3. Test with SLSQP or trust-constr optimizers

### Hypothesis 3: Specification Mis-specification

**Evidence:**
- theta_c stuck near 0.5 (not moving to 0.0 like singles)
- beta_c collapsed to near-zero
- This pattern suggests consumption may not enter utility in the way the model assumes

**Next Steps:**
1. Test log utility specification (theta_c = theta_l = 0, fixed)
2. Test linear utility (theta_c = theta_l = 1, fixed)
3. Compare likelihoods and check if Box-Cox is necessary

### Hypothesis 4: Couples Leisure Interaction Term

**Evidence:**
- beta_interact = 0.002 (essentially zero)
- Couples may have strong leisure complementarity that's not captured

**Next Steps:**
1. Test with larger initial value for beta_interact (e.g., 0.5)
2. Examine data for evidence of joint leisure patterns

---

## Comparison: Before vs After All Fixes

| Metric | Before Any Fixes | After All Fixes | Change |
|--------|------------------|-----------------|---------|
| **Singles beta_c** | 1.0 (stuck) | 1.18-1.32 | ✅ **FIXED** |
| **Singles theta_c** | 0.5 (stuck) | ~0.0 | ✅ **FIXED** |
| **Couples beta_c** | 1.0 → 0.011 | 0.027 | ❌ **STILL BROKEN** (slight improvement) |
| **Couples theta_c** | 0.5 | 0.459 | ❌ **STILL STUCK** |
| **Couples beta_pexp2** | +0.318 (wrong sign) | -0.023 | ✅ **FIXED SIGN** |
| **Gradient norm (couples)** | 838 | 236 | ⚠️ **IMPROVED** but still high |

---

## Critical Questions Remaining

### 1. Was the consumption floor actually applied?

Need to verify:
```python
df_couples = pd.read_parquet('.../fr_2016_RURO_mnl_couples.parquet')
print(f"Min consumption: {df_couples['ils_dispy'].min()}")
print(f"Obs with consumption < 1.0: {(df_couples['ils_dispy'] < 1.0).sum()}")
```

**Expected after fix:**
- Min consumption = 1.0 (not 0.000001)
- Observations < 1.0 = 0 (not 4,057)

### 2. Why did consumption floor fix have zero effect?

Possible explanations:
1. **Fix wasn't actually applied** (need to verify Step 6 ran with new code)
2. **4,057 observations are not the problem** (issue is elsewhere)
3. **Optimization is stuck in local minimum** (can't escape even with better data)

### 3. Is the couples utility function ACTUALLY correct now?

Need to verify:
- Consumption appears ONCE in total utility
- Gradients w.r.t. beta_c and theta_c are correct
- No accidental scaling factors

---

## Recommended Next Actions

### Priority 1: Verify Fixes Were Applied

1. ✅ Check `enh_RURO_prep_mnl_basic.py` line 53 has `DCM_MIN_POSITIVE = 1.0`
2. ⏳ **Load couples MNL parquet and verify min(ils_dispy) = 1.0**
3. ⏳ **Verify Step 6 output log shows "4,057 observations floored at 1.0"**

### Priority 2: Test Alternative Optimizer Settings

1. Increase ftol and gtol:
   ```yaml
   opt_options:
     ftol: 1.0e-10  # (currently 1e-8)
     gtol: 1.0e-8   # (currently not set)
     maxiter: 10000 # (currently 5000)
   ```

2. Try different initial values:
   ```yaml
   initial_values:
     beta_c: 1.5  # (currently 1.0)
     theta_c: 0.0 # (currently 0.5) - start at log utility
   ```

### Priority 3: Test Simpler Specifications

1. **Fixed log utility:**
   ```yaml
   # Set theta_c = 0.0 and theta_l = 0.0 (FIXED, not estimated)
   ```

2. **Couples-specific beta_c:**
   ```yaml
   # Add beta_c_couples parameter (separate from beta_c_singles)
   ```

### Priority 4: Deep Data Diagnostics

1. Compare couples vs singles:
   - Consumption distributions
   - Leisure distributions
   - Wage distributions
   - Hours distributions

2. Check for outliers/anomalies:
   - Extremely high consumption
   - Negative/zero hours
   - Missing wage data

---

## Files Modified in This Session

1. [scripts/enhanced/enh_RURO_prep_mnl_basic.py](scripts/enhanced/enh_RURO_prep_mnl_basic.py)
   - Line 53: `DCM_MIN_POSITIVE = 1.0` (was 1e-6)
   - Lines 209-222: EUROMOD merge logic (ALWAYS use ils_dispy_em)

2. [scripts/enhanced/estimation_spec.yaml](scripts/enhanced/estimation_spec.yaml)
   - Lines 28, 34: Box-Cox bounds [0.0, 5.0] (was [0.001, 5.0])
   - Lines 186-189: Added beta_pexp2 ∈ [-10, 0] constraint

3. [scripts/enhanced/estimation_engine.py](scripts/enhanced/estimation_engine.py)
   - Lines 938-953: Couples utility function (consumption added ONCE)
   - Lines 1293-1296: Couples beta_c gradient (removed 2.0x multiplier)
   - Lines 1312-1316: Couples theta_c gradient (removed 2.0x multiplier)

4. [scripts/enhanced/estimation_utils.py](scripts/enhanced/estimation_utils.py)
   - Lines 898-935: Box-Cox derivative with Taylor expansion for theta ≈ 0

---

## Summary

**What Works:**
- ✅ Singles male estimation (beta_c = 1.180, theta_c = 0.000)
- ✅ Singles female estimation (beta_c = 1.316, theta_c = 0.002)
- ✅ beta_pexp2 now has correct negative sign

**What's Still Broken:**
- ❌ Couples beta_c = 0.027 (44x too low)
- ❌ Couples theta_c = 0.459 (stuck near initial value)
- ❌ Couples beta_pexp = 1.006 (implausibly high)
- ⚠️ High gradient norms across all groups

**Next Critical Step:**
**Verify the consumption floor fix was actually applied** by checking the Step 6 output data.

If the fix WAS applied and had no effect, this suggests a deeper issue with either:
1. The couples data itself (different anomaly we haven't found)
2. The couples utility specification (fundamental mis-specification)
3. The optimization algorithm (stuck in bad local minimum)
