# EUROMOD Couples Consumption Fix - Summary

**Date:** 2025-12-14
**Issue:** Couples consumption constant across all draws → parameters unidentifiable
**Status:** 🔄 Fix implemented, testing in progress

---

## Problem Identification

### Symptoms
- 100% of couples (2,900 households) had constant consumption across all 200 alternatives
- Couples parameters stuck at initial values during estimation
- Estimation "succeeded" but couples contributed nothing to likelihood
- Final LL = -22,207 (singles only, should be ~-90K to -100K with couples)

### Root Cause
**EUROMOD output had constant `ils_dispy` (disposable income) for each person across all draws**, even though:
- Hours (`lhw`) varied correctly ✅
- Earnings (`yem`) varied correctly ✅
- Disposable income (`ils_dispy`) was CONSTANT ❌

Example for Person 148300001:
```
Draw 0: hours=15.00, earnings=631.67, disp_income=491.50
Draw 1: hours=2.37,  earnings=370.87, disp_income=491.50 ← SAME!
Draw 2: hours=40.92, earnings=940.12, disp_income=491.50 ← SAME!
```

---

## Investigation Process

### Step 1: Confirmed Data Issue
Checked MNL dataset (`fr_2016_RURO_mnl.parquet`):
- Couples consumption exists with valid mean (4,235) and std (2,072)
- BUT: std=0 within every household across all alternatives
- Consumption = sum of male + female `ils_dispy`, which are both constant

### Step 2: Traced to EUROMOD Output
Checked EUROMOD output (`combined_draws_em.parquet`):
- EUROMOD receives varying `yem` (earnings) as input
- EUROMOD produces varying `yem` in output
- BUT: `ils_dispy` in output is constant per person

### Step 3: Identified Merge Issue
Code analysis of [RURO_euromod.py](scripts/RURO_euromod.py):
- Line 371: Merges EUROMOD template (with baseline `ils_dispy`) with draws
- Line 614: Calls EUROMOD with merged data containing baseline `ils_dispy`
- Line 625-628: Reattaches draw/ID columns to EUROMOD output

**Hypothesis**: Either:
1. EUROMOD doesn't recalculate fields that already exist in input, OR
2. The merge logic inadvertently keeps pre-EUROMOD `ils_dispy` instead of post-EUROMOD

---

## Solution Implemented

### Changes to [RURO_euromod.py](scripts/RURO_euromod.py)

#### 1. Enhanced DEBUG Logging (Lines 622-638)
Added detailed logging to track `ils_dispy` through the pipeline:
```python
# DEBUG: Verify ils_dispy values after EUROMOD
if "ils_dispy" in sim_df.columns:
    logging.info(f"RURO_euromod DEBUG: ils_dispy after EUROMOD - "
                f"min={sim_df['ils_dispy'].min():.2f}, "
                f"max={sim_df['ils_dispy'].max():.2f}, "
                f"mean={sim_df['ils_dispy'].mean():.2f}, "
                f"nunique={sim_df['ils_dispy'].nunique()}")

    # Sample one person to verify varying ils_dispy
    sample_person = merged[f"{id_col}_true"].iloc[0]
    sim_df_base_ids = sim_df[id_col] // 1000
    sample_mask = (sim_df_base_ids == sample_person)
    sample_data = sim_df[sample_mask][['ils_dispy']].head(5)
    logging.info(f"RURO_euromod DEBUG: Sample person {sample_person} "
                f"ils_dispy values from EUROMOD:\n{sample_data.to_string()}")
```

#### 2. Improved Merge Strategy (Lines 640-680)
Explicitly prioritize EUROMOD-calculated values:

```python
# Step 1: Identify columns to keep from pre-EUROMOD data
cols_to_reattach = ["draw", "idhh_true", f"{id_col}_true"]

# Step 2: Add these columns to EUROMOD output
for col in cols_to_reattach:
    sim_df[col] = merged[col].values

# Step 3: Add columns that exist ONLY in pre-EUROMOD data
pre_euromod_only_cols = set(merged.columns) - set(sim_df.columns)
logging.info(f"RURO_euromod: Adding {len(pre_euromod_only_cols)} columns "
            f"from pre-EUROMOD data that are not in EUROMOD output")

for col in pre_euromod_only_cols:
    sim_df[col] = merged[col].values

# Step 4: Verify EUROMOD-calculated ils_dispy was used
if "ils_dispy" in sim_df.columns and f"{id_col}_true" in sim_df.columns:
    sample_person = sim_df[f"{id_col}_true"].iloc[0]
    person_data = sim_df[sim_df[f"{id_col}_true"] == sample_person].head(5)
    ils_std = person_data["ils_dispy"].std()
    logging.info(f"RURO_euromod VERIFICATION: Sample person {sample_person} "
                f"ils_dispy std={ils_std:.6f} (should be > 0 if EUROMOD recalculated)")

    if ils_std < 1e-6:
        logging.warning(f"RURO_euromod WARNING: ils_dispy appears constant! "
                       f"EUROMOD may not have recalculated disposable income.")
```

### Key Improvements

1. **Explicit Merge Priority**: EUROMOD output (`sim_df`) is the base; pre-EUROMOD columns only added if missing
2. **Verification Check**: Automatically detects if `ils_dispy` is still constant and warns
3. **Detailed Logging**: Tracks `ils_dispy` variation at each step for debugging
4. **Transparent Logic**: Clear documentation of what columns come from where

---

## Expected Outcomes

### If Fix Works ✅

**EUROMOD Output**:
- `ils_dispy` varies across draws for each person
- std > 0 for verification check

**MNL Dataset**:
- Couples consumption varies within households
- std > 1e-6 for each household

**Estimation**:
- Couples contribute to likelihood
- Couples parameters move from initial values
- Final LL improves to ~-90K to -100K range
- Parameter identification successful

### If Fix Doesn't Work ❌

**Possible Causes**:
1. EUROMOD Python package doesn't recalculate pre-existing fields
   - **Solution**: Drop `ils_dispy` from input before calling EUROMOD

2. EUROMOD configuration issue
   - **Solution**: Check EUROMOD scenario XML settings

3. EUROMOD needs specific flags to recalculate full tax-benefit system
   - **Solution**: Review EUROMOD API documentation, add required parameters

---

## Testing Plan

### Phase 1: EUROMOD Output Verification ⏳ IN PROGRESS
```bash
# Re-run EUROMOD step
python scripts/RURO_euromod.py \
  --singles-draws singles_RURO_ready_RURO_draws.parquet \
  --couples-draws couples_RURO_ready_RURO_draws.parquet \
  --microdata-template FR_2016.txt \
  --euromod-system FR_2015 --euromod-dataset FR_2016
```

**Check**:
1. Look for DEBUG log: "ils_dispy after EUROMOD - nunique=X" (should be > 100)
2. Look for VERIFICATION log: "ils_dispy std=X" (should be > 0)
3. If WARNING appears: "ils_dispy appears constant" → fix didn't work

### Phase 2: MNL Dataset Verification
```python
# Check if consumption now varies
df = pd.read_parquet('fr_2016_RURO_mnl.parquet')
cou = df[df['ruro_group'] == 10]

# Should show varying=2900, constant=0
varying = (cou.groupby('idhh')['consumption'].std() > 1e-6).sum()
constant = (cou.groupby('idhh')['consumption'].std() <= 1e-6).sum()
print(f'Varying: {varying}, Constant: {constant}')
```

### Phase 3: Re-run Estimation
```bash
# Re-run Steps 6-7
python scripts/RURO_prep_mnl_basic.py ...
python scripts/RURO_estimate_FR.py --joint ...
```

**Expected**:
- Couples parameters move from initials
- Final LL < -50,000 (couples contributing)
- Estimation time longer (~5-10 min vs ~30s)

---

## Fallback Plan

If EUROMOD still doesn't recalculate `ils_dispy`:

### Option A: Drop ils_dispy Before EUROMOD
```python
# In RURO_euromod.py, before line 614:
if 'ils_dispy' in merged.columns:
    merged = merged.drop(columns=['ils_dispy'])
    logging.info("RURO_euromod: Dropped pre-EUROMOD ils_dispy to force recalculation")
```

### Option B: Compute Synthetic Consumption
```python
# In RURO_prep_mnl_basic.py or estimation code:
# consumption = base_non_labor_income + (1 - tax_rate) * earnings
# Where tax_rate ≈ 0.4 for France
cons = base_dispy - base_yem + 0.6 * yem
```

### Option C: Check EUROMOD API
```python
# Verify EUROMOD Python package version and API
import euromod
print(euromod.__version__)
# Check if there's a parameter to force recalculation
```

---

## Timeline

- **13:44**: Pipeline run started, identified constant consumption
- **14:00**: Root cause found (constant `ils_dispy` from EUROMOD)
- **14:15**: Fix implemented in RURO_euromod.py
- **14:20**: EUROMOD re-run started
- **14:24**: ⏳ Waiting for EUROMOD completion (~3-4 min total)
- **14:25**: Verify fix worked
- **14:30**: Re-run MNL prep + estimation if successful

---

## Files Modified

1. [scripts/RURO_euromod.py:614-680](scripts/RURO_euromod.py#L614-L680)
   - Enhanced merge logic
   - Added DEBUG logging
   - Added verification checks

---

## Documentation Created

1. [COUPLES_CONSUMPTION_BUG_ANALYSIS.md](COUPLES_CONSUMPTION_BUG_ANALYSIS.md) - Detailed root cause analysis
2. [PIPELINE_RUN_ANALYSIS_2025-12-14.md](PIPELINE_RUN_ANALYSIS_2025-12-14.md) - Full pipeline run diagnostics
3. This file - Fix summary and testing plan

---

**Status**: Fix deployed, EUROMOD running, awaiting verification results.
