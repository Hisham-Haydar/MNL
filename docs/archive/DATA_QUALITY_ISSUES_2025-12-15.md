# Critical Data Quality Issues - December 15, 2025

**Discovery Method:** Interactive inspection using [run_draws_euromod_interactive.py](scripts/run_draws_euromod_interactive.py) and VS Code Data Wrangler

**Impact:** These early-stage data preparation issues may explain the downstream EUROMOD ils_dispy calculation problems.

---

## Summary of Critical Issues

Inspection of the RURO_ready datasets (output of Step 2: RURO_prep.py) revealed **fundamental data integrity problems** that exist from the very beginning of the pipeline:

### 1. **Duplicate `lhw` Column**
- **Problem:** Two identical columns named "lhw" exist in the dataset
- **Impact:** Data integrity violation, potential confusion in downstream analysis
- **Severity:** HIGH
- **Source:** Unknown - needs investigation in france_data_prep.py

### 2. **Redundant `ruro_sample` and `ruro_decider` Columns**
- **Problem:** Both columns contain identical 0/1 values (perfect clones)
- **Impact:** Unnecessary duplication, one can be safely dropped
- **Severity:** LOW (cosmetic, but indicates redundant logic)
- **Source:** RURO_prep.py line 480

### 3. **Labor Market Activity (`lma`) Always Zero**
- **Problem:** `lma` (labor market activity) = 0 for ALL persons
- **Expected:** `lma = 1` for anyone with `ruro_decider = 1` and working
- **Impact:** **CRITICAL** - `lma` is used to identify workers in RURO_prep.py (line 582)
- **Severity:** CRITICAL
- **Source:** france_data_prep.py does NOT extract or create `lma` from EUROMOD output

### 4. **Labor Market Inactive (`lun`) Always Zero**
- **Problem:** `lun` = 0 for ALL persons
- **Expected:** Should show variation between active/inactive labor market participants
- **Impact:** HIGH - Missing critical labor market status information
- **Severity:** HIGH
- **Source:** france_data_prep.py does NOT extract `lun` from EUROMOD output

### 5. **Labor Market Constrained (`lmc`) Always Zero**
- **Problem:** `lmc` = 0 for ALL persons
- **Expected:** Should identify persons facing labor market constraints
- **Impact:** MODERATE - Missing constraint information
- **Severity:** MODERATE
- **Source:** france_data_prep.py does NOT extract `lmc` from EUROMOD output

### 6. **All `lhw_*` Variant Columns Always Zero**
- **Problem:** Four lhw-related columns are ALL zero:
  - `lhw_a1` = 0
  - `lhw_a_9` = 0
  - `lhw_a_20` = 0
  - `lhw_a` = 0
- **Impact:** Unknown purpose, but all being zero suggests they're not being populated
- **Severity:** UNKNOWN - need to determine if these are required
- **Source:** Unclear what these variables represent

### 7. **`lunmy` Has Some Variation (Good!)**
- **Status:** This variable DOES show variation
- **Note:** This proves EUROMOD labor market variables CAN vary when properly extracted

---

## Root Cause Analysis

### Missing EUROMOD Output Extraction

**Critical Finding:** [france_data_prep.py](scripts/france_data_prep.py:1-1500) does NOT extract EUROMOD labor market output variables!

**Evidence:**
```bash
# Search results in france_data_prep.py
grep "lma.*=" france_data_prep.py    # NO MATCHES
grep "lun.*=" france_data_prep.py    # NO MATCHES
grep "lmc.*=" france_data_prep.py    # NO MATCHES
grep "lhw_a" france_data_prep.py     # NO MATCHES
```

**What's happening:**
1. france_data_prep.py runs EUROMOD simulation (line 867)
2. Gets EUROMOD output as `df_sim` (line 868)
3. BUT: Never extracts the labor market status variables (`lma`, `lun`, `lmc`, `lhw_*`)
4. These variables should be in EUROMOD output but are not being copied to final dataset

**RURO_prep.py Logic Depends on `lma`:**
```python
# scripts/RURO_prep.py lines 576-585
lma = None
if "lma" in df.columns:
    lma = cast(pd.Series, pd.to_numeric(df["lma"], errors="coerce"))

if lma is not None:
    is_worker_bool = (lma == 1) & (lhw > 0.0)  # Uses lma to identify workers!
else:
    is_worker_bool = les.eq(3) & (lhw > 0.0)   # Fallback to les
```

**Consequence:**
- Since `lma` is missing (or all zeros), the fallback `les == 3` logic is used
- This may incorrectly identify workers
- Worker identification errors propagate to:
  - `is_worker` flag
  - `wage_ruro` calculation
  - All wage-related analysis

---

## Impact on Downstream Analysis

### Immediate Impact (Step 2: RURO_prep)
- ✗ Worker identification may be incorrect (using fallback `les` instead of `lma`)
- ✗ `is_worker` flag may be wrong for some persons
- ✗ `wage_ruro` may be incorrectly set to 0 for workers or non-zero for non-workers

### Step 3: RURO_draws
- ✗ Wage draws generated for wrong set of persons
- ✗ Hours draws may not match actual labor market status

### Step 4: EUROMOD Simulation
- ✗ Input data has incorrect labor market status
- ✗ EUROMOD may calculate disposable income based on wrong employment status
- ✗ **This could explain why `ils_dispy` is constant for 96% of persons!**

### Step 7: Estimation
- ✗ Parameter identification fails
- ✗ 50/60 parameters stuck at initial values
- ✗ Model cannot estimate because data lacks variation

---

## Verification Steps Needed

### 1. Check Raw EUROMOD Output
```python
# After france_data_prep.py runs EUROMOD (line 867)
df_sim = sim.outputs[0]

# Check if these columns exist in EUROMOD output
labor_cols = ['lma', 'lun', 'lmc', 'lhw_a1', 'lhw_a_9', 'lhw_a_20', 'lhw_a']
for col in labor_cols:
    if col in df_sim.columns:
        print(f"{col}: exists, std={df_sim[col].std():.4f}")
    else:
        print(f"{col}: MISSING from EUROMOD output")
```

### 2. Check FR_2016.txt Raw Input
- Verify if `lma`, `lun`, `lmc` exist in raw EUROMOD microdata
- If they exist: Extract them in france_data_prep.py
- If they don't exist: They may be EUROMOD-calculated outputs that need extraction

### 3. EUROMOD Documentation
- Consult EUROMOD FR_2015 policy documentation
- Identify which variables are outputs vs inputs
- Determine correct extraction logic

---

## Proposed Fixes

### Fix 1: Extract EUROMOD Labor Market Variables

**Location:** [france_data_prep.py](scripts/france_data_prep.py:867-900)

**After EUROMOD simulation (line 867-868), add:**
```python
# Extract EUROMOD labor market status outputs
labor_market_vars = ['lma', 'lun', 'lmc', 'lhw_a1', 'lhw_a', 'lhw_a_9', 'lhw_a_20']

for var in labor_market_vars:
    if var in df_sim.columns:
        logging.info(f"Extracting EUROMOD output: {var} (std={df_sim[var].std():.4f})")
    else:
        logging.warning(f"EUROMOD output missing expected variable: {var}")
        df_sim[var] = 0  # Create as zero if missing
```

### Fix 2: Remove Duplicate `lhw` Column

**Location:** [france_data_prep.py](scripts/france_data_prep.py) or [RURO_prep.py](scripts/RURO_prep.py)

**Need to identify:**
- Where is the duplicate created?
- Which `lhw` is correct? (probably the one from EUROMOD input/output)
- Add explicit de-duplication:
```python
# Remove duplicate columns (keep first occurrence)
df = df.loc[:, ~df.columns.duplicated()]
```

### Fix 3: Consolidate `ruro_sample` and `ruro_decider`

**Location:** [RURO_prep.py](scripts/RURO_prep.py:480)

**Current logic creates both:**
```python
# Line 489: ruro_sample = 1{ruro_decider == 1 AND dag >= 18}
_maybe_add_column(df, "ruro_sample", ruro_sample_flag)
```

**Decision needed:**
- Are they intentionally different? (ruro_decider = head+partner, ruro_sample = adults only?)
- If so, keep both but document the difference clearly
- If not, remove redundant one

### Fix 4: Validate Worker Identification Logic

**After fixes, verify:**
```python
# Check consistency of worker definitions
df['worker_from_lma'] = (df['lma'] == 1) & (df['lhw'] > 0)
df['worker_from_les'] = (df['les'] == 3) & (df['lhw'] > 0)
df['worker_mismatch'] = df['worker_from_lma'] != df['worker_from_les']

print(f"Workers identified by lma: {df['worker_from_lma'].sum()}")
print(f"Workers identified by les: {df['worker_from_les'].sum()}")
print(f"Mismatches: {df['worker_mismatch'].sum()}")
```

---

## Testing Plan

### Phase 1: Diagnostic Run
1. Add logging to france_data_prep.py to show EUROMOD output columns
2. Run Step 1 only
3. Inspect what columns EUROMOD actually produces
4. Verify if `lma`, `lun`, `lmc` exist

### Phase 2: Fix Implementation
1. Implement Fix 1: Extract EUROMOD labor market variables
2. Implement Fix 2: Remove duplicate `lhw`
3. Run Steps 1-2 and inspect RURO_ready output

### Phase 3: Validation
1. Check that `lma` now varies (not all zeros)
2. Check that `lun`, `lmc` have expected values
3. Verify no duplicate columns remain
4. Check worker identification matches expectations

### Phase 4: Full Pipeline
1. Delete all intermediate files
2. Set fixed random seed in RURO_draws.py
3. Run full pipeline Steps 1-7
4. Verify `ils_dispy` now varies for >96% of persons
5. Check estimation convergence

---

## Questions to Answer

1. **What labor market variables does EUROMOD FR_2015 produce?**
   - Need to check EUROMOD documentation or output inspection

2. **Are `lhw_*` variants required for analysis?**
   - What do these represent? (activity levels? alternative specifications?)
   - Are they used anywhere in the pipeline?

3. **Is the duplicate `lhw` a pandas merge artifact?**
   - Check for merge operations that might create duplicates
   - Review column selection logic

4. **Should `lunmy` (months unemployed) be used instead of `lun`?**
   - `lunmy` DOES vary, suggesting it's correctly extracted
   - Is this the variable we should be using?

5. **Does fixing `lma` solve the `ils_dispy` problem?**
   - Hypothesis: Wrong worker identification → wrong EUROMOD inputs → constant outputs
   - Test by re-running full pipeline after fixes

---

## Priority Ranking

1. **CRITICAL:** Fix 1 - Extract EUROMOD labor market variables (`lma`, `lun`, `lmc`)
2. **HIGH:** Validate worker identification logic after Fix 1
3. **MODERATE:** Fix 2 - Remove duplicate `lhw` column
4. **LOW:** Fix 3 - Clarify `ruro_sample` vs `ruro_decider` difference
5. **UNKNOWN:** Fix 4 - Investigate `lhw_*` variants (need to determine if required)

---

## Related Files

- [france_data_prep.py](scripts/france_data_prep.py) - Where EUROMOD extraction should happen
- [RURO_prep.py](scripts/RURO_prep.py) - Where `lma` is expected to exist
- [run_draws_euromod_interactive.py](scripts/run_draws_euromod_interactive.py) - Interactive inspection tool
- [EUROMOD_INVESTIGATION_SUMMARY_2025-12-15.md](EUROMOD_INVESTIGATION_SUMMARY_2025-12-15.md) - Previous investigation

---

## Connection to Previous Issues

This discovery provides a **missing link** in our investigation:

**Previous finding:** 96% of persons have constant `ils_dispy` despite varying `yem`

**New insight:** If worker identification is wrong from Step 1, then:
1. Wrong persons are treated as workers in RURO_ready
2. Wage draws created for wrong persons in Step 3
3. EUROMOD receives incorrect employment status in Step 4
4. EUROMOD calculates `ils_dispy` based on wrong labor market status
5. Result: Constant `ils_dispy` because EUROMOD sees constant employment status!

**Hypothesis:** Fixing labor market variable extraction in france_data_prep.py will fix the entire pipeline.

**Test:** Re-run full pipeline after implementing Fix 1 and verify `ils_dispy` variation.

---

**Next Step:** Implement Fix 1 (Extract EUROMOD labor market variables) and test.
