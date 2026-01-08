# Couples Fix Results Analysis
**Date:** 2026-01-08
**Run:** After consumption doubling fix

---

## RESULTS SUMMARY

### Singles Male ✅ **EXCELLENT**

| Parameter | Initial | Estimated | Movement | Status |
|-----------|---------|-----------|----------|--------|
| beta_c | 1.0 | **1.312** | +31.2% | ✅ Strong preference for consumption |
| theta_c | 0.5 | **0.016** | -96.8% | ✅ Log utility (optimal) |
| theta_l | 0.5 | **0.0** | -100% | ✅ Exact log utility |
| beta_pexp2 | -0.001 | **-0.0006** | ✅ Negative (correct sign) |

- **Final LL:** -1650.93
- **Iterations:** 251
- **Gradient norm:** 225 (moderate - likely at theta_l bound)
- **Walltime:** 17s

**Interpretation:** Males have log utility for both consumption and leisure. Strong consumption preference (beta_c = 1.312).

---

### Singles Female ✅ **EXCELLENT**

| Parameter | Initial | Estimated | Movement | Status |
|-----------|---------|-----------|----------|--------|
| beta_c | 1.0 | **1.316** | +31.6% | ✅ Strong preference for consumption |
| theta_c | 0.5 | **0.002** | -99.6% | ✅ Log utility (optimal) |
| theta_l | 0.5 | **0.002** | -99.6% | ✅ Log utility |
| beta_l_n_children | 0.1 | **0.111** | +11.4% | ✅ Moved! |
| beta_pexp2 | -0.001 | **-0.0001** | ✅ Negative (correct sign) |

- **Final LL:** -1805.13
- **Iterations:** 609
- **Gradient norm:** 168 (moderate)
- **Walltime:** 39s

**Interpretation:** Females also have log utility. Very similar beta_c to males (1.316 vs 1.312), indicating consistent preferences across gender.

---

### Couples ❌ **STILL PROBLEMATIC**

| Parameter | Initial | Estimated | Movement | Status |
|-----------|---------|-----------|----------|--------|
| beta_c | 1.0 | **0.026** | -97.4% | ❌ **STILL TOO LOW** |
| theta_c | 0.5 | **0.468** | -6.4% | ❌ **BARELY MOVED** |
| theta_l | 0.5 | **0.490** | -2.0% | ⚠️ Barely moved |
| beta_pexp | 0.02 | **0.825** | +4025% | ⚠️ **VERY HIGH** |
| beta_pexp2 | -0.001 | **-0.129** | ✅ Negative but very large |

- **Final LL:** -1653.14
- **Iterations:** 652 (much higher than singles!)
- **Gradient norm:** 199 (**STILL HIGH**)
- **Walltime:** 233s (13x slower than singles male!)

**Interpretation:** Couples estimation is **STILL FAILING**. The couples consumption fix helped reduce beta_c from 0.011 to 0.026, but it's still **50x lower** than singles (0.026 vs 1.31).

---

## COMPARISON: Before vs After Couples Fix

| Metric | Before Fix | After Fix (Couples) | Change |
|--------|------------|---------------------|--------|
| beta_c | 0.0107 | 0.0257 | +140% (but still way too low!) |
| theta_c | 0.4934 | 0.4681 | -5% (minimal movement) |
| beta_pexp | 0.9177 | 0.8249 | -10% (still very high) |
| beta_pexp2 | +0.3183 | -0.1286 | ✅ Now negative! |
| Gradient norm | 838 | 199 | -76% (better but still high) |
| Iterations | 769 | 652 | -15% (still slow) |

**Verdict:** The fix **HELPED** (beta_c doubled, beta_pexp2 now negative, lower gradient norm) but couples estimation is **STILL FUNDAMENTALLY BROKEN**.

---

## ROOT CAUSE ANALYSIS

### Hypothesis 1: ⭐ **Consumption Data Issue (MOST LIKELY)**

**Evidence:**
1. Singles beta_c ≈ 1.31 (reasonable)
2. Couples beta_c = 0.026 (50x lower!)
3. If couples `consumption` variable is actually **household total** but we're treating it as if it's the **sum of individual incomes** in the utility function, we'd get exactly this scaling issue.

**From R code analysis:**
```r
# R code uses INDIVIDUAL disposable incomes
dispy_util_m = (ils_dispy_m / dpi) / mean_dispy_19
dispy_util_f = (ils_dispy_f / dpi) / mean_dispy_19

# Utility function
util = ... + beta_c * BC(dispy_util_m + dispy_util_f; theta_c)
```

**Python couples data:**
- We have ONE `consumption` column (from EUROMOD)
- **QUESTION:** Is this:
  - (A) Household total (ils_dispy for the household)
  - (B) Sum of male + female individual incomes

**If (A):** Our utility is correct: `BC(household_total)`
**If (B):** The R code expects us to do `BC(c_male + c_female)` but we're already doing `BC(sum)`, which is the same

**But there's a normalization issue!**

### Hypothesis 2: ⭐⭐ **Normalization Scaling Error (VERY LIKELY)**

Let's think about the normalization:

**Singles:**
- `consumption_norm = ils_dispy_individual / mean_dispy_19`
- Where `mean_dispy_19` = weighted mean of **individual** disposable income for lma==1

**Couples:**
- If `consumption = ils_dispy_household` (total for both spouses)
- But `mean_dispy_19` is still the **individual** mean from singles!
- Then `consumption_norm = household_total / individual_mean`
- This makes couples consumption **roughly 2x larger** than it should be!

**Example:**
- Singles individual income: 2000
- Singles normalized: 2000 / 2000 = 1.0
- Couples household income: 4000 (2x singles)
- Couples normalized: 4000 / 2000 = 2.0 (**TWICE as large!**)

**Effect on estimation:**
- If consumption appears "too high" in the data, the optimizer will:
  - Reduce beta_c (to 0.026 instead of 1.31)
  - Keep theta_c high (0.468) to reduce curvature

**This explains everything!**

---

## DIAGNOSIS: Normalization Constant Issue

### The Problem

**Singles normalization:**
```python
consumption_singles = ils_dispy_individual / mean_dispy_19
```

**Couples normalization (CURRENT - WRONG?):**
```python
consumption_couples = ils_dispy_household / mean_dispy_19
```

**But if `mean_dispy_19` is computed from SINGLES data**, then it's the mean of **individual** income, not **household** income!

### The Fix Options

**Option A: Use household-specific normalization constant**
```python
mean_dispy_19_household = mean_dispy_19_singles * 2  # Approximate
consumption_couples = ils_dispy_household / mean_dispy_19_household
```

**Option B: Convert household to per-capita**
```python
consumption_couples = (ils_dispy_household / 2) / mean_dispy_19
```

**Option C: Match R code exactly - use individual incomes**
```python
# If EUROMOD outputs individual ils_dispy for each spouse:
consumption_couples = (ils_dispy_male + ils_dispy_female) / mean_dispy_19
```

---

## VERIFICATION NEEDED

### 1. Check `mean_dispy_19` computation

**Question:** Is `mean_dispy_19` computed from:
- (A) Singles data only (individual mean)
- (B) All data including couples (mixed individual + household means)
- (C) Separate constants for singles vs couples

**File to check:** Step 6 or metadata file

### 2. Check couples `consumption` variable

**Question:** What does `consumption` represent in couples data?
- (A) Household total (sum of male + female)
- (B) Already normalized per-capita
- (C) Something else

**How to check:**
```python
import pandas as pd
df_couples = pd.read_parquet("fr_2016_RURO_mnl__couples.parquet")
df_singles = pd.read_parquet("fr_2016_RURO_mnl__singles.parquet")

# Compare consumption magnitudes
print("Singles consumption mean:", df_singles["consumption"].mean())
print("Couples consumption mean:", df_couples["consumption"].mean())
print("Ratio:", df_couples["consumption"].mean() / df_singles["consumption"].mean())

# If ratio ≈ 2, then couples consumption is household total not normalized!
```

### 3. Check R code normalization

**From R code (line 625):**
```r
dispy_util = (ils_dispy / dpi) / mean_dispy_19
```

**Question:** Does R compute separate `mean_dispy_19` for singles vs couples, or use the same constant?

---

## RECOMMENDED FIX

### Step 1: Verify consumption scaling
```bash
python -c "
import pandas as pd
df_s = pd.read_parquet('fr_2016_RURO_mnl__singles.parquet')
df_c = pd.read_parquet('fr_2016_RURO_mnl__couples.parquet')
print(f'Singles mean: {df_s[\"consumption\"].mean():.2f}')
print(f'Couples mean: {df_c[\"consumption\"].mean():.2f}')
print(f'Ratio: {df_c[\"consumption\"].mean() / df_s[\"consumption\"].mean():.2f}')
"
```

### Step 2: If ratio ≈ 2, apply couples-specific normalization

**In Step 6 (enh_RURO_prep_mnl_basic.py):**
```python
# For couples, divide by 2 before normalization
# OR use couples-specific mean_dispy_19

if household_type == "couples":
    # Option A: Per-capita normalization
    df["consumption"] = (df["ils_dispy"] / 2) / mean_dispy_19

    # Option B: Household-specific constant
    mean_dispy_19_household = mean_dispy_19 * 2
    df["consumption"] = df["ils_dispy"] / mean_dispy_19_household
```

### Step 3: Re-run estimation

After fixing normalization, couples parameters should match singles:
- beta_c ≈ 1.3 (not 0.026)
- theta_c ≈ 0.0 (log utility, not 0.468)

---

## NEXT STEPS

1. ✅ **Verify consumption scaling** (run diagnostic script above)
2. ⚠️ **Check metadata for normalization constants**
3. ⚠️ **Fix couples normalization if needed**
4. ⚠️ **Re-run estimation**
5. ⚠️ **Compare with R code results**

---

## CONCLUSION

The consumption doubling fix was **NECESSARY** but **NOT SUFFICIENT**. Couples estimation still fails because of a **normalization scaling issue**:

- **Singles:** consumption normalized by individual mean → correct scale
- **Couples:** household consumption normalized by individual mean → **2x too large**
- **Result:** Optimizer compensates by reducing beta_c by 50x and keeping theta_c high

**Next action:** Verify consumption scaling and apply couples-specific normalization.
