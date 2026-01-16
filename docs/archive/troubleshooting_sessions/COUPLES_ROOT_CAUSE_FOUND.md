# COUPLES ESTIMATION ROOT CAUSE - FOUND!
**Date:** 2026-01-08
**Status:** ⭐ **CRITICAL BUG IDENTIFIED**

---

## EXECUTIVE SUMMARY

**Root Cause:** Negative EUROMOD disposable income clipped to 1e-6 instead of floored at 1.0, causing extreme Box-Cox values that break couples estimation.

**Impact:** 4,057 observations (1.57% of couples data) have consumption < 1, creating Box-Cox values around -2000, forcing optimizer to set beta_c ≈ 0.026 (50x too low).

**Fix:** Change consumption floor from `1e-6` to `1.0` to match R code.

---

## THE SMOKING GUN

### Data Evidence

**Couples with consumption < 1:**
- Count: 4,057 / 257,700 (1.57%)
- Pattern: Male hours = 0, female may or may not work
- EUROMOD `ils_dispy_em`: **NEGATIVE** (-405, -44, -13, etc.)
- Python `consumption`: **0.000001** (clipped!)

**Singles with consumption < 1:**
- Count: 41 / 167,600 (0.02%)
- **38x FEWER problematic observations!**

### Box-Cox Transformation Impact

```python
# With current floor (1e-6):
BC(0.000001, theta=0.5) = (0.000001^0.5 - 1) / 0.5 = -1999.998

# With proper floor (1.0):
BC(1.0, theta=0.5) = (1.0^0.5 - 1) / 0.5 = 0.0
```

**Effect on optimization:**
- Extreme negative BC values dominate the likelihood
- Optimizer reduces beta_c to minimize impact of these outliers
- Result: beta_c = 0.026 (couples) vs 1.31 (singles) - **50x difference!**

---

## CODE COMPARISON

### Python (WRONG - Line 688)
```python
cons = pd.to_numeric(df["ils_dispy"], errors="coerce").clip(lower=DCM_MIN_POSITIVE)
# DCM_MIN_POSITIVE = 1e-6
```

### R Reference (CORRECT - Line 619)
```r
ils_dispy = pmax(1, ils_dispy)  # Floor at 1.0
```

---

## WHY NEGATIVE EUROMOD OUTPUT?

When counterfactual hours are zero or very low, EUROMOD calculates:
```
Disposable income = Earnings + Benefits - Taxes - Contributions
```

For some draws:
- Earnings = 0 (male not working)
- Benefits = small (or zero with "lim" OLI spec)
- Taxes = 0
- Contributions = fixed minimum (health insurance, etc.)
- **Result:** Negative disposable income

**This is REALISTIC** - households with no earnings and minimum contributions can have negative "disposable" income (they need savings/debt/transfers to survive).

---

## PATTERN ANALYSIS

### By Work Pattern (Couples)

| Pattern | Count | Mean Consumption | Consumption < 1 | % |
|---------|-------|------------------|-----------------|---|
| Both zero hours | 2,618 | 823.78 | 164 | 6.26% |
| Very low hours | 13,180 | 2,079.84 | 905 | 6.87% |
| Part-time | 33,683 | 4,015.59 | 1,170 | 3.47% |
| Full-time | 208,219 | 8,541.57 | 1,818 | **0.87%** |

### Male Zero Hours (Female Works)

- Count: 23,435 observations
- Mean consumption: **292.06** (very low!)
- Consumption < 1: **3,777** (16.1% of this subset!)

This pattern is the **PRIMARY SOURCE** of the problem.

---

## OBSERVED VS COUNTERFACTUAL

**Observed (draw=0):**
- Consumption < 1: 14 / 2,577 (**0.54%**)
- Both hours = 0: 14

**Counterfactual (draw>0):**
- Consumption < 1: 4,043 / 255,123 (**1.58%**)
- Both hours = 0: 2,604

**Conclusion:** The problem is in **COUNTERFACTUAL draws**, not observed data. This makes sense - in reality, households adjust their behavior to avoid zero income, but in simulated counterfactuals, we force zero hours and get unrealistic negative incomes.

---

## THE FIX

### Option A: Match R Code ⭐ **RECOMMENDED**

```python
# Change line 53
DCM_MIN_POSITIVE = 1.0  # Was: 1e-6

# OR change line 688 specifically for consumption
cons = pd.to_numeric(df["ils_dispy"], errors="coerce").clip(lower=1.0)
```

**Pros:**
- Matches R reference code
- BC(1.0, theta) = 0 for any theta > 0
- No extreme values

**Cons:**
- Still arbitrary floor (why 1.0?)
- Doesn't address root cause (negative EUROMOD output)

---

### Option B: Handle Negative Income Properly

```python
# Convert negative/zero income to small positive value
cons = pd.to_numeric(df["ils_dispy"], errors="coerce")
cons = np.where(cons <= 0, 1.0, cons)  # Or use consumption floor
df["consumption"] = cons
```

**Pros:**
- Explicit handling of negative values
- Clear intent

**Cons:**
- Same as Option A (arbitrary floor)

---

### Option C: Equivalence Scale Adjustment (Best Long-term)

```python
# For couples, apply equivalence scale
# Modified OECD scale: 1.0 + 0.5 = 1.5 for couple without children
if household_type == "couples":
    equiv_scale = 1.5  # Or calculate from n_children
    cons_per_capita = cons / equiv_scale
    cons_per_capita = cons_per_capita.clip(lower=1.0)
```

**Pros:**
- Economically meaningful
- Makes couples consumption comparable to singles
- May help with beta_c convergence

**Cons:**
- Requires additional implementation
- Not in R code (different approach)

---

## IMMEDIATE ACTION: OPTION A

Apply the simple fix now, test results:

```python
# enh_RURO_prep_mnl_basic.py, line 53
DCM_MIN_POSITIVE = 1.0  # Changed from 1e-6
```

**Expected results after fix:**
- Couples beta_c: 0.026 → ~1.3 (match singles)
- Couples theta_c: 0.468 → ~0.0 (log utility)
- Gradient norm: 199 → < 10
- Convergence: Much faster

---

## VERIFICATION

### Before Fix
- Couples beta_c = 0.0257
- Couples theta_c = 0.4681
- Couples gradient norm = 199
- Consumption < 1: 4,057 observations

### After Fix (Expected)
- Couples beta_c ≈ 1.3
- Couples theta_c ≈ 0.0
- Couples gradient norm < 10
- Consumption < 1: 0 observations (all floored to 1.0)

---

## CONCLUSION

This is a **DATA PREPARATION BUG**, not a model specification issue. The fix is simple and should completely resolve couples estimation.

**Status:** Ready to implement fix and re-run estimation.
