# EUROMOD Investigation Summary
**Date:** December 15, 2025
**Issue:** Constant `ils_dispy` (disposable income) despite varying `yem` (employment income)

---

## Problem Statement

During joint estimation (Step 7), we discovered:
- **Log-likelihood**: Improved -1,273,550 → -22,207 (98% reduction)
- **Parameters**: 50/60 stuck at initial values
- **Root cause**: Couples had **constant consumption** across all 200 alternatives
- **Diagnosis**: `ils_dispy` was constant for each person across all 100 draws

---

## Investigation Timeline

### Initial Hypothesis: EUROMOD Merge Logic
**Theory**: `ils_dispy` from draws was overwriting EUROMOD output
**Action**: Enhanced merge logic to prioritize EUROMOD output
**Result**: ✗ Failed - `ils_dispy` still constant

### Second Hypothesis: Column Filtering
**Theory**: Need to filter `ils_*` output columns before EUROMOD
**Action**: Implemented filtering to only send original template columns
**Result**: ✗ Failed - but discovered the REAL issue!

### Key Discovery: Template vs Drawn Values
**Critical Insight** (thanks to user!): `yem = wpm × lhw × yivwg`

**Problem Identified**:
1. `yem`, `lhw`, `yivwg` exist in BOTH template (constant) AND draws (varying)
2. Original fix kept only "template columns" → used template's CONSTANT `yem`
3. EUROMOD received constant `yem` → calculated constant `ils_dispy`

**Fix Attempted**: Filter out only `ils_*` outputs + metadata, keep drawn inputs
**Result**: ✗ Still failed, but for different reason!

### Current Status: The Real Problem

After implementing the fix:
- ✓ Drawn `yem` IS being sent to EUROMOD (std=7730)
- ✓ EUROMOD output HAS varying `yem` (std=8021)
- ✗ BUT `ils_dispy` is STILL constant (std=0) for ~96% of persons!

**Affected Scale**:
- Total persons: 11,964
- Persons with constant `ils_dispy`: 11,503 (96.1%)
- Persons with constant `ils_dispy` + varying `yem`: 6,960 (58.2%)

**BUT**: Some persons DO have varying `ils_dispy`!
- Person 148520001: ils_dispy std=108.63 ✓ WORKS!
- Person 435030001: ils_dispy std=55.70 ✓ WORKS!
- Person 148300001: ils_dispy std=0.00 ✗ BROKEN

---

## Key Findings

### 1. Data Flow is Correct

**RURO_draws.py** (Step 3):
- ✓ Generates varying `lhw` (hours): std=17.79
- ✓ Generates varying `yivwg` (wage): std=38.33
- ✓ Calculates varying `yem`: std=7,215

**RURO_euromod.py** (Step 4):
- ✓ Extracts `yem_draw` from draws (line 478-481)
- ✓ Replaces `merged["yem"]` with drawn value (line 550-552)
- ✓ Sends varying `yem` to EUROMOD (confirmed: std=7730)

**EUROMOD Output**:
- ✓ Contains varying `yem` (std=8021)
- ✗ Contains constant `ils_dispy` (std=0) for most persons

### 2. Not Singles vs Couples

Initially thought problem was couples-specific, but testing shows:
- Singles: 80% have constant `ils_dispy`
- Couples: 80% have constant `ils_dispy`
- **Problem affects BOTH groups similarly**

### 3. EUROMOD CAN Calculate Varying `ils_dispy`

~4% of persons DO have varying `ils_dispy`, proving EUROMOD is capable.

**Question**: What's different about the 4% that work?

---

## Hypotheses for Why `ils_dispy` is Constant

### Hypothesis A: EUROMOD Internal Logic
EUROMOD may use variables OTHER than `yem` for `ils_dispy` calculation:
- Other income sources (benefits, capital income)
- Household-level variables
- Tax/benefit eligibility flags

If these are constant, `ils_dispy` could be constant despite varying `yem`.

### Hypothesis B: ID Transformation Issues
Code transforms IDs for draws (line 415-417):
```python
# ID transformation happens somewhere
# Verification: sim_df_base_ids = sim_df[id_col] // 1000
```

If IDs are incorrectly transformed, EUROMOD might group all draws together.

### Hypothesis C: Draw Replication Logic
For non-deciders, code replicates baseline (lines 385-398).
If decider logic is broken, everyone might be treated as non-decider.

### Hypothesis D: EUROMOD Caching/Configuration
EUROMOD might have internal caching or configuration preventing recalculation.

---

## Code Changes Made

### File: `scripts/RURO_euromod.py`

**Lines 631-676**: Column filtering logic
```python
# Filter out ils_* outputs and draw metadata
ils_output_cols = [c for c in merged.columns if c.startswith('ils_') and c != 'ils_earns']
draw_metadata_cols = [c for c in merged.columns if c not in original_template_cols and not c.startswith('ils_')]
cols_to_filter = set(ils_output_cols) | set(draw_metadata_cols)
cols_to_send = [c for c in merged.columns if c not in cols_to_filter]
```

**Lines 711-718**: Updated merge logic
```python
unique_draw_cols = cols_to_filter - euromod_output_cols
# Only add back columns unique to draws, not in EUROMOD output
```

**Result**: Varying `yem` reaches EUROMOD, but `ils_dispy` still constant.

---

## Next Steps

### Option 1: Fresh Pipeline Run with Seed (RECOMMENDED)
1. Delete all intermediate files from Step 2 onwards
2. Set fixed random seed in `RURO_draws.py` for reproducibility
3. Re-run Steps 2-6 with clean data flow
4. Carefully inspect at each step:
   - Step 3: Verify draws vary correctly
   - Step 4: Verify EUROMOD receives/outputs varying data
   - Step 6: Verify MNL dataset has varying consumption

### Option 2: Manual `ils_dispy` Calculation
Calculate `ils_dispy` post-EUROMOD ourselves:
```python
ils_dispy_recalc = yem + other_income + benefits - taxes
```

Use EUROMOD's tax/benefit outputs but recalculate final `ils_dispy`.

### Option 3: Investigate the 4% That Work
Compare persons with varying vs constant `ils_dispy`:
- What variables differ?
- What characteristics make EUROMOD recalculate?
- Can we replicate those conditions?

### Option 4: EUROMOD Expert Consultation
Contact EUROMOD developers about why recalculation isn't happening.

---

## Questions to Answer

1. **ID Transformation**: Are `idperson` and `idhh` being modified for draws?
2. **Seed Consistency**: Is there a random seed set in `RURO_draws.py`?
3. **Decider Logic**: Are all persons being correctly identified as deciders?
4. **Working Status**: Does `working_mask` logic affect EUROMOD calculations?
5. **Household Dependencies**: Does EUROMOD calculate household-level variables that prevent variation?

---

## Files Modified

1. `scripts/run_fr_2016_joint_only.ps1` - Enhanced logging
2. `scripts/RURO_euromod.py` - Column filtering and merge logic

## Files to Check

1. `scripts/RURO_draws.py` - Random seed setting
2. `scripts/RURO_prep.py` - Initial data preparation
3. `scripts/france_data_prep.py` - Raw data processing

---

## Reproduction Steps

To reproduce the current state:
```bash
# From project root
powershell -ExecutionPolicy Bypass -File ./scripts/run_fr_2016_joint_only.ps1
```

To check results:
```python
import pandas as pd

# Load EUROMOD output
df = pd.read_parquet('U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016/combined_draws_em.parquet')

# Check one person
person = df[df['idperson_true'] == 148300001]
print(f"yem std: {person['yem'].std():.2f}")
print(f"ils_dispy std: {person['ils_dispy'].std():.2f}")
```

---

## Recommendation

**Proceed with Option 1**: Fresh pipeline run from Step 2/3 with:
1. Fixed random seed for reproducibility
2. Enhanced validation at each step
3. Interactive Jupyter notebook for inspection
4. Systematic comparison of working vs non-working persons

This will either:
- Reveal a data flow issue we missed
- Confirm the problem is in EUROMOD's internal logic
- Identify specific conditions that enable varying `ils_dispy`

---

**End of Summary**
