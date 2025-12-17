# Couples Consumption Bug - Root Cause Analysis
**Date:** 2025-12-14
**Status:** 🔴 CRITICAL BUG IDENTIFIED

---

## Executive Summary

**Problem**: Couples consumption is constant across all choice alternatives, making couples parameters unidentifiable.

**Root Cause**: EUROMOD output has constant `ils_dispy` (disposable income) for each person across all draws, even though hours and earnings vary.

**Impact**:
- 100% of couples (2,900 households) have constant consumption
- Couples contribute nothing to estimation likelihood
- All couples parameters stuck at initial values
- Estimation "succeeds" but results are invalid

---

## Bug Timeline

1. **MNL Dataset Created**: [RURO_prep_mnl_basic.py](scripts/RURO_prep_mnl_basic.py) correctly sums `ils_dispy` across household members
2. **Consumption is Constant**: All 2,900 couples have identical consumption across 200 alternatives
3. **Estimation Detects Problem**: [RURO_estimate_FR.py:608-610](scripts/RURO_estimate_FR.py#L608-L610) detects consumption doesn't vary
4. **Tries to Fix Synthetically**: Looks for `yem_m`, `yem_f`, `ils_dispy_m`, `ils_dispy_f` columns (don't exist)
5. **Returns Zero Consumption**: `safe_get` returns zeros → synthetic computation returns zeros
6. **Optimizer Ignores Couples**: Couples have zero consumption → zero contribution to likelihood

---

## Data Structure Analysis

### Expected Structure (User Specification)

For couples:
- Draws happen at **individual level** (male and female separately)
- Each person has 100 draws (varying hours/wages)
- MNL dataset combines draws: each (male draw i, female draw j) = one alternative
- 100 male draws × 100 female draws = 10,000 alternatives per couple (but we see 200?)
- Consumption for alternative (i,j) = male's ils_dispy(draw i) + female's ils_dispy(draw j)

### Actual Structure Found

**MNL Dataset (`fr_2016_RURO_mnl.parquet`)**:
```
Household 1483000:
- Total rows: 200
- Unique persons: 2
- Unique draws: 100 (0-99)
- Structure: 2 persons × 100 draws = 200 rows

Draw 0:
  Person 148300001 (male):   lhw=15.00,  ils_dispy=491.50
  Person 148300002 (female): lhw=42.00,  ils_dispy=2455.22
  → Consumption = 491.50 + 2455.22 = 2946.72

Draw 1:
  Person 148300001 (male):   lhw=2.37,   ils_dispy=491.50  ← SAME!
  Person 148300002 (female): lhw=28.71,  ils_dispy=2455.22 ← SAME!
  → Consumption = 491.50 + 2455.22 = 2946.72  ← CONSTANT!
```

**EUROMOD Output (`combined_draws_em.parquet`)**:
```
Person 148300000001, Draw 0:
  Row 0: lhw=15.00,  yem=631.67,   ils_dispy=491.50
  Row 1: lhw=42.00,  yem=2989.17,  ils_dispy=2515.86
  Row 2-3: (non-deciders with zeros)

Person 148300000001, Draw 1:
  Row 0: lhw=2.37,   yem=370.87,   ils_dispy=491.50  ← SAME AS DRAW 0!
  Row 1: lhw=28.71,  yem=926.37,   ils_dispy=2515.86 ← SAME AS DRAW 0!
```

**Key Finding**:
- Hours (`lhw`) vary correctly across draws ✅
- Earnings (`yem`) vary correctly across draws ✅
- **Disposable income (`ils_dispy`) is CONSTANT** ❌

---

## Root Cause: EUROMOD Issue

EUROMOD is being called correctly and **does compute varying earnings** (`yem`), but **`ils_dispy` doesn't change**.

### Hypothesis 1: EUROMOD Not Recalculating Taxes/Benefits

`ils_dispy` = earnings + benefits - taxes

If EUROMOD recalculates earnings but uses **cached/baseline values** for benefits and taxes, then `ils_dispy` would be constant even though `yem` varies.

**Evidence**:
- `yem` varies: 631.67 → 370.87 → 940.12 (changes with hours)
- `ils_dispy` constant: 491.50 → 491.50 → 491.50 (doesn't change)

This suggests EUROMOD is:
1. ✅ Correctly updating labor hours (`lhw`) for each draw
2. ✅ Correctly computing earnings (`yem`) from updated hours
3. ❌ **NOT recalculating** taxes/benefits based on new earnings
4. ❌ Using **baseline `ils_dispy`** from observed draw (draw=0)

### Hypothesis 2: EUROMOD Configuration Issue

The EUROMOD scenario might be configured to:
- Update earnings variables
- NOT recalculate tax-benefit system
- Output baseline disposable income for all draws

**Files to investigate**:
- [scripts/RURO_euromod.py](scripts/RURO_euromod.py) - EUROMOD invocation
- EUROMOD scenario XMLs in `U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016/`

### Hypothesis 3: Merge Issue

The `combined_draws_em.parquet` might have incorrect merge logic where:
- EUROMOD outputs are correct
- But merge keeps baseline `ils_dispy` instead of draw-specific values

**Evidence against this**: `yem` varies correctly, so the merge is working for some variables

---

## Impact on Estimation

### What Estimation Code Expected

[RURO_estimate_FR.py:573-650](scripts/RURO_estimate_FR.py#L573-L650):

1. Check if `c_norm` column exists (NO - not in dataset)
2. Check if `consumption` exists and varies within households (YES exists, NO doesn't vary)
3. Try to compute synthetic consumption from:
   - `ils_dispy_m`, `ils_dispy_f` (don't exist - no `_m/_f` suffixes)
   - `yem_m`, `yem_f` (don't exist - no `_m/_f` suffixes)
4. `safe_get` returns zeros for missing columns
5. Synthetic computation: `c = base_non_labor + NET_OF_TAX * (yem_m + yem_f)`
6. With all inputs = 0: `c = 0 + 0.6 * (0 + 0) = 0`
7. Log message: "Computed synthetic couples consumption: mean=0.000, std=0.000"

### Workaround Attempted by Estimation Code

The code tries to fix constant consumption by computing it synthetically, but fails because:
1. Column names don't match (no `_m/_f` suffixes in couples data)
2. Even if columns existed, they'd still be constant (root EUROMOD issue)

---

## Why Singles Work But Couples Don't

**Singles**:
- Each row = one person with one draw
- EUROMOD recalculates `ils_dispy` for each draw (or consumption already varies?)
- Estimation log: "Computed synthetic consumption: mean=2.472, std=1.936" ✅

**Couples**:
- Each row = one person in couple with one draw
- EUROMOD outputs constant `ils_dispy` per person
- Summing constant values → constant household consumption
- Estimation detects non-varying consumption → tries synthetic approach → fails

---

## Fixes Required

### Fix 1: Diagnose EUROMOD Issue (Priority 1)

**Investigate**:
1. Check EUROMOD scenario configuration for France 2016
2. Verify EUROMOD is being called with correct flags to recalculate full tax-benefit system
3. Check if `ils_dispy_em` column (EUROMOD output) exists and varies
4. Compare `ils_dispy` vs `ils_dispy_em` in combined_draws_em.parquet

**Script to check**: [scripts/RURO_euromod.py](scripts/RURO_euromod.py)

**Likely issue**: Line ~200-300 where EUROMOD runner is invoked - might need additional flags/parameters

### Fix 2: Verify Couples Draw Structure (Priority 1)

**Questions**:
1. Should couples have 100 draws (synchronized) or 10,000 draws (full combinations)?
2. Current structure: 2 persons × 100 draws = 200 rows
3. Expected structure: ?

**If 100 synchronized draws**:
- Male draw i pairs with female draw i only
- 100 alternatives per couple
- Consumption[i] = male_ils_dispy[i] + female_ils_dispy[i]

**If 10,000 full combinations**:
- Male draw i pairs with female draw j for all i,j
- 10,000 alternatives per couple
- Consumption[i,j] = male_ils_dispy[i] + female_ils_dispy[j]

Current data suggests synchronized draws (100, not 10,000).

### Fix 3: Update Estimation Code (Priority 2)

Once EUROMOD issue is fixed, the estimation code will still try synthetic computation because it checks if consumption varies.

**Options**:
A) Fix EUROMOD → consumption will vary → estimation will use it directly
B) Add fallback: if consumption exists but doesn't vary, use `ils_dispy` directly anyway
C) Remove the "consumption must vary" check for couples

**Recommendation**: Fix EUROMOD first (root cause), then reassess if estimation changes needed

---

## Immediate Action Plan

1. **Verify EUROMOD output** ⏳ IN PROGRESS
   ```python
   # Check if ils_dispy_em (EUROMOD-calculated) exists and varies
   em = pd.read_parquet('.../combined_draws_em.parquet')
   # Compare ils_dispy vs ils_dispy_em
   ```

2. **Check EUROMOD invocation** in [RURO_euromod.py](scripts/RURO_euromod.py)
   - Line ~150-250: `EUROMODRunner.run_on_dataframe`
   - Check command-line arguments passed to EUROMOD
   - Verify scenario XML configuration

3. **Test EUROMOD manually**
   - Run EUROMOD on sample household with varying hours
   - Verify output has varying `ils_dispy`
   - Compare to current pipeline output

4. **Temporary workaround** (if EUROMOD fix takes time)
   - Compute consumption synthetically using `yem` and tax approximation
   - Would require adding `_m/_f` columns during MNL prep

5. **Long-term fix**
   - Fix EUROMOD configuration/invocation
   - Re-run pipeline from Step 4 (EUROMOD simulation)
   - Verify consumption varies before estimation

---

## Expected vs Actual Outcomes

| Aspect | Expected | Actual | Status |
|--------|----------|--------|--------|
| Singles consumption | Varies within individuals | Varies (mean=2.47, std=1.94) | ✅ OK |
| Couples consumption | Varies within households | Constant (std=0 for all HHs) | ❌ BUG |
| EUROMOD `lhw` | Varies across draws | Varies correctly | ✅ OK |
| EUROMOD `yem` | Varies across draws | Varies correctly | ✅ OK |
| EUROMOD `ils_dispy` | **Varies across draws** | **CONSTANT!** | ❌ BUG |
| Couples parameters | Estimated from data | Stuck at initials | ❌ CONSEQUENCE |
| Final log-likelihood | ~-90K to -100K (typical) | -22,207 (singles only) | ⚠️ INVALID |

---

## Files to Investigate Next

1. [scripts/RURO_euromod.py](scripts/RURO_euromod.py) - EUROMOD invocation
2. `U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016/*.xml` - EUROMOD config
3. [scripts/RURO_prep_mnl_basic.py:171-177](scripts/RURO_prep_mnl_basic.py#L171-L177) - Consumption aggregation
4. EUROMOD documentation for batch mode and variable recalculation

---

## Questions for User

1. **Is consumption supposed to vary for couples?** (Yes, obviously!)
2. **Should couples have 100 or 10,000 alternatives?** (Synchronized draws vs full combinations)
3. **Does EUROMOD need specific flags** to recalculate full tax-benefit system?
4. **Has this pipeline ever worked** with varying couples consumption?

---

**Next Step**: Investigate [RURO_euromod.py](scripts/RURO_euromod.py) to see how EUROMOD is being invoked and why `ils_dispy` isn't being recalculated.
