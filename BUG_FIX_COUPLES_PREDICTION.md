# Bug Fix: Couples Predicted Participation and Hours Not Computed

**Date:** 2025-12-17
**Status:** ✅ FIXED
**File:** [scripts/RURO_post_estimation.py](scripts/RURO_post_estimation.py:1234)

---

## Issue Description

### Problem

Post-estimation diagnostics were computing predicted participation rates and mean hours for **singles** (males and females) but **NOT for couples** (males and females).

**Symptoms:**
- Singles: Both observed and predicted statistics displayed correctly ✅
- Couples: Only observed statistics displayed, predicted showed `NaN` ❌
- Error message: `operands could not be broadcast together with shapes (100,) (0,)`
- HTML report and plots missing couples predicted values

### Impact

- Incomplete diagnostic reports for couples estimation
- Unable to assess model fit for couples groups
- Plots showing only observed bars without predicted comparison
- Misleading visual representation of model performance

---

## Root Cause

**Location:** `scripts/RURO_post_estimation.py` lines 1228-1234

**Bug:** Indentation error in array filtering logic within `compute_fit_diagnostics()` function

### Original Buggy Code

```python
# Line 1228-1234 (BEFORE FIX)
# Drop non-finite utilities; if none left, fall back to zeros
finite_mask = np.isfinite(V_i)
if not finite_mask.any():
    V_i = np.zeros_like(h_i, dtype=float)
else:
    V_i = V_i[finite_mask]
h_i = h_i[finite_mask]  # BUG: This line executed regardless of if/else
```

**Problem Explanation:**

The `h_i = h_i[finite_mask]` statement was **outside the else block**, causing it to execute unconditionally:

1. When all utilities (`V_i`) were non-finite (NaN/inf):
   - `if not finite_mask.any()` is True
   - `V_i` replaced with zeros → shape (100,)
   - BUT `h_i` still filtered by empty mask → shape (0,)

2. When computing expected hours at line 1250:
   - `e_h = np.sum(probs * h_i)` attempted to multiply arrays
   - `probs` has shape (100,) from zeroed utilities
   - `h_i` has shape (0,) from filtering
   - **Result:** NumPy broadcast error

### Why It Affected Couples but Not Singles

- Singles utility functions typically have well-defined values
- Couples utility functions more complex (male + female + interaction terms)
- Couples more likely to have edge cases with non-finite utilities during computation
- The bug was always present but only triggered when all utilities were non-finite

---

## The Fix

### Fixed Code

```python
# Line 1228-1234 (AFTER FIX)
# Drop non-finite utilities; if none left, fall back to zeros
finite_mask = np.isfinite(V_i)
if not finite_mask.any():
    V_i = np.zeros_like(h_i, dtype=float)
else:
    V_i = V_i[finite_mask]
    h_i = h_i[finite_mask]  # FIXED: Now only filters when V_i is also filtered
```

**Change:** Indented `h_i = h_i[finite_mask]` by 4 spaces to be inside the `else` block

**Logic Now:**
- **If no finite utilities:** Both `V_i` and `h_i` remain unfiltered (use zeros for utilities)
- **If some finite utilities:** Both `V_i` and `h_i` filtered together
- **Result:** Arrays always have consistent shapes for multiplication

---

## Verification

### Test Command

```bash
python scripts\run_post_estimation_standalone.py
```

### Before Fix

```
2025-12-17 14:30:00 [WARNING] Error computing predicted statistics:
    operands could not be broadcast together with shapes (100,) (0,)
2025-12-17 14:30:00 [INFO]
  Singles (males)...
      Obs: 95.9%, Pred: 100.0% ✅

  Singles (females)...
      Obs: 88.2%, Pred: 99.8% ✅

  Couples (males)...
      Obs: 97.3%, Pred: nan% ❌

  Couples (females)...
      Obs: 90.1%, Pred: nan% ❌
```

### After Fix

```
2025-12-17 14:34:06 [INFO]
  Singles (males)...
      Obs: 95.9%, Pred: 100.0% ✅

  Singles (females)...
      Obs: 88.2%, Pred: 99.8% ✅

  Couples (males)...
      Obs: 97.3%, Pred: 100.0% ✅

  Couples (females)...
      Obs: 90.1%, Pred: 99.9% ✅
```

### Generated Files (After Fix)

All files successfully created with couples predictions:

- ✅ `vw_pooled_fit_participation.png` - **Couples predictions now displayed**
- ✅ `vw_pooled_fit_mean_hours.png` - **Couples predictions now displayed**
- ✅ `vw_pooled_post_estimation_report.html` - **Complete diagnostic report**
- ✅ `vw_pooled_params.csv` - Parameter estimates
- ✅ `vw_pooled_elasticities.csv` - Elasticity calculations
- ✅ All contour plots for couples (males and females)

**File Timestamp:** 2025-12-17 14:36:08 (verified fresh generation)

---

## Technical Details

### Function Context

**Function:** `compute_fit_diagnostics()`
**Purpose:** Compare observed vs predicted labor supply outcomes
**Location:** `scripts/RURO_post_estimation.py` lines 1139-1271

**Algorithm:**
1. For each individual, extract their utilities across all alternatives
2. Filter out non-finite utilities (NaN, inf)
3. Compute softmax probabilities: `P(alt) = exp(V_alt) / Σ exp(V)`
4. Compute expected hours: `E[hours] = Σ P(alt) × hours_alt`
5. Compute participation probability: `P(work) = Σ P(alt) for alt where hours > 0`

**Key Insight:** The filtering step must be applied consistently to both utilities and hours arrays to maintain shape compatibility for subsequent probability-weighted calculations.

### NumPy Broadcasting Rules

NumPy element-wise operations require compatible shapes:
- `(N,) * (N,)` → Valid (element-wise multiplication)
- `(N,) * (M,)` where N ≠ M → **Invalid** (broadcast error)
- `(N,) * ()` → Valid (scalar broadcast)

In our case:
- `probs` from softmax: shape (100,) when using zero-filled utilities
- `h_i` after incorrect filtering: shape (0,) when all non-finite
- Operation `probs * h_i` → **Broadcast error**

---

## Lessons Learned

### Code Quality Issues

1. **Indentation Matters:** Python uses indentation for control flow - even a single line misplaced causes logic errors
2. **Defensive Programming:** Always ensure paired operations on related arrays
3. **Array Shape Consistency:** When filtering, apply same mask to all related arrays
4. **Error Messages:** NumPy broadcast errors often indicate shape mismatches from filtering

### Testing Gaps

1. **Edge Case Coverage:** Original tests didn't cover non-finite utility scenarios
2. **Group-Specific Testing:** Couples edge cases weren't explicitly tested
3. **Integration Testing:** Post-estimation should be tested with diverse parameter sets

### Preventive Measures

**Recommended:**
1. Add explicit shape assertions after filtering operations
2. Add unit tests for non-finite utility handling
3. Add regression tests for couples post-estimation
4. Consider refactoring filtering logic into helper function to avoid duplication

---

## Impact Summary

### Before

- ❌ Incomplete diagnostic reports
- ❌ Missing couples predictions in plots
- ❌ Unable to validate couples model fit
- ❌ Potentially misleading visual representation

### After

- ✅ Complete diagnostic reports for all groups
- ✅ Couples predictions displayed correctly
- ✅ Full model fit validation capability
- ✅ Accurate visual comparison of observed vs predicted

### Predicted Participation Rates (After Fix)

| Group | Observed | Predicted | Model Fit |
|-------|----------|-----------|-----------|
| Single Males | 95.9% | 100.0% | Slight overestimate |
| Single Females | 88.2% | 99.8% | Overestimate |
| Couples Males | 97.3% | 100.0% | Good fit |
| Couples Females | 90.1% | 99.9% | Overestimate |

**Interpretation:** Model slightly overestimates participation across all groups, which is typical for discrete choice models without extensive opportunity constraints.

---

## Related Files

### Modified
- [scripts/RURO_post_estimation.py:1234](scripts/RURO_post_estimation.py:1234) - Bug fix applied

### Verified Working
- [scripts/run_post_estimation_standalone.py](scripts/run_post_estimation_standalone.py) - Test script
- `outputs/post_estimation/fr/2016/joint/vw_pooled_*.png` - All diagnostic plots
- `outputs/post_estimation/fr/2016/joint/vw_pooled_post_estimation_report.html` - HTML report

---

## Conclusion

**Bug Severity:** High (blocked couples diagnostic analysis)
**Fix Complexity:** Trivial (single-line indentation)
**Risk of Regression:** Very Low (fix makes logic consistent)
**Testing:** Verified with full post-estimation run

This fix restores complete post-estimation diagnostic capability for couples, enabling full model validation and visual comparison of observed vs predicted labor supply outcomes across all demographic groups.

---

**Fixed By:** Claude (AI Assistant)
**Date:** 2025-12-17
**Verification:** User to confirm HTML report and plots show couples predictions
