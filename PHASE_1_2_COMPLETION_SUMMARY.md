# Phase 1 & 2 Completion Summary

**Date:** 2025-12-16
**Issue Fixed:** Missing reshape step in couples data pipeline
**Root Cause:** Couples data remained in LONG format but estimation code expected WIDE format

---

## Phase 1: Data Preparation (COMPLETED ✓)

### Changes Made to `scripts/RURO_prep_mnl_basic.py`

#### 1. Added Reshape Function (lines 201-368)
```python
def _reshape_couples_to_wide(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reshape couples data from long format (2 rows per household-draw) to
    wide format (1 row per household-draw with _male and _female columns).

    Input (LONG):
        idhh  draw  dgn  lhw  wage  ...
        1001  0     1    40   15.5  ... (male)
        1001  0     0    35   12.0  ... (female)

    Output (WIDE):
        idhh  draw  lhw_male  lhw_female  wage_male  wage_female  ...
        1001  0     40        35          15.5       12.0         ...
    """
```

**Key features:**
- Uses `dgn` column (0=female, 1=male) to identify gender
- Excludes flag columns ending in `_f`, `_s`, `_a`, `_o` from pivoting
- Preserves household-level variables (one copy, no suffix)
- Adds extensive error checking and logging

#### 2. Created Couples-Specific MNL Builder (lines 146-193)
```python
def _build_mnl_block_couples_wide(df: pd.DataFrame) -> pd.DataFrame:
    """Build MNL dataset block for couples in WIDE format."""
```

**Creates derived variables:**
- Education dummies from `deh_male`, `deh_female`
- Experience variables from `pexp_male`, `pexp_female`
- Working status from `hours_male`, `hours_female`
- Age-squared terms
- All with `_male`/`_female` suffixes

#### 3. Integrated Reshape into Pipeline (lines 517-578)
```python
def main() -> None:
    # ... existing code ...

    if args.couples_draws:
        couples_long = _read_df(couples_path)
        couples_long = _merge_euromod_outputs(couples_long, em_df)
        couples_long = _restrict_to_deciders(couples_long)

        # NEW: Reshape couples from long to wide format
        couples_wide = _reshape_couples_to_wide(couples_long)

        # Use couples-specific MNL builder
        couples_mnl = _build_mnl_block_couples_wide(couples_wide)
        frames.append(couples_mnl)
```

### Results

**Before reshape:**
- Couples: 580,000 rows (2 rows per household-draw)
- Missing `_male`/`_female` columns → opportunity parameters stuck at zero

**After reshape:**
- Couples: 286,800 rows (1 row per household-draw)
- Singles: 162,100 rows (unchanged)
- **Total: 448,900 rows** in final MNL dataset
- All gender-specific columns created: 684 `_male`/`_female` columns

**Output file:** `U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_RESHAPED.parquet`

---

## Phase 2: Estimation Code Updates (COMPLETED ✓)

### Changes Made to `scripts/RURO_estimate_FR.py`

**Automated replacement script created:** `apply_phase2_renames.py`
**Total replacements:** 670

### Replacement Categories

#### 1. String Literals (Column Names) - 120 replacements
```python
"leisure_m" → "leisure_male"
"leisure_f" → "leisure_female"
"hours_m" → "hours_male"
"hours_f" → "hours_female"
"age_norm_m" → "age_norm_male"
"age_norm_f" → "age_norm_female"
"educL_m" → "educL_male"
"educL_f" → "educL_female"
"educH_m" → "educH_male"
"educH_f" → "educH_female"
"pexp_m" → "pexp_male"
"pexp_f" → "pexp_female"
"working_m" → "working_male"
"working_f" → "working_female"
"working_pt1_m" → "working_pt1_male"
"working_pt1_f" → "working_pt1_female"
"working_pt2_m" → "working_pt2_male"
"working_pt2_f" → "working_pt2_female"
"working_ft_m" → "working_ft_male"
"working_ft_f" → "working_ft_female"
"gsur_m" → "gsur_male"
"gsur_f" → "gsur_female"
```

#### 2. Variable Names (with word boundaries) - 550 replacements
```python
\bl_m\b → l_male (38 occurrences)
\bl_f\b → l_female (38 occurrences)
\bhours_m\b → hours_male (26 occurrences)
\bhours_f\b → hours_female (25 occurrences)
\bage_norm_m\b → age_norm_male (15 occurrences)
\bage_norm_f\b → age_norm_female (14 occurrences)
\bage_norm2_m\b → age_norm2_male (14 occurrences)
\bage_norm2_f\b → age_norm2_female (14 occurrences)
\beducL_m\b → educL_male (27 occurrences)
\beducL_f\b → educL_female (26 occurrences)
\beducH_m\b → educH_male (26 occurrences)
\beducH_f\b → educH_female (25 occurrences)
\bpexp_m\b → pexp_male (19 occurrences)
\bpexp_f\b → pexp_female (19 occurrences)
\bpexp2_m\b → pexp2_male (7 occurrences) ← Added in second pass
\bpexp2_f\b → pexp2_female (7 occurrences) ← Added in second pass
\bworking_m\b → working_male (47 occurrences)
\bworking_f\b → working_female (47 occurrences)
\bworking_pt1_m\b → working_pt1_male (14 occurrences)
\bworking_pt1_f\b → working_pt1_female (14 occurrences)
\bworking_pt2_m\b → working_pt2_male (13 occurrences)
\bworking_pt2_f\b → working_pt2_female (13 occurrences)
\bworking_ft_m\b → working_ft_male (13 occurrences)
\bworking_ft_f\b → working_ft_female (13 occurrences)
\bgsur_m\b → gsur_male (16 occurrences)
\bgsur_f\b → gsur_female (16 occurrences)
```

### Safety Verification

**Native EUROMOD columns PRESERVED (NOT renamed):**
```python
# These remained unchanged:
"wage_f" in df.columns  # Flag or native wage column
"yivwg_f" in df.columns  # Alternative wage column
"lhw_f"  # Hours worked flag column
"yem_f"  # Employment income flag column
```

**Verification steps:**
1. ✓ Python syntax compiles successfully
2. ✓ Native column checks intact (grepped for `"wage_f"`, `"yivwg_f"`)
3. ✓ No flag columns accidentally renamed
4. ✓ Word boundaries prevented partial matches

### Functions Updated

All functions that handle couples data were updated:

1. **`CouplesData` dataclass** (lines 238-285)
   - Updated field names: `l_male`, `l_female`, `age_norm_male`, etc.

2. **`precompute_data_couples()`** (lines 555-800)
   - Updated column name lookups
   - Updated dataclass field assignments

3. **`fast_neg_ll_with_grad_couples()`** (lines 3463-3800)
   - Updated variable references throughout

4. **`fast_log_likelihood_couples()`** (lines 2750-2900)
   - Updated variable references

5. **`ff_calc_util_couples()`** (lines 1501-1642)
   - Updated variable references

6. **All opportunity density functions**
   - Hours opportunity: Updated `_m`/`_f` → `_male`/`_female`
   - Wage opportunity: Updated `_m`/`_f` → `_male`/`_female`

---

## Naming Convention Decision

**Chosen:** `_male` and `_female` suffixes

**Rationale:**
- ✓ Clear and explicit (no ambiguity)
- ✓ No conflicts with flag columns (which end in `_f`, `_s`, `_a`, `_o`)
- ✓ Consistent with modern coding conventions
- ✓ Self-documenting code

**Rejected alternatives:**
- `_m` and `_f`: ❌ Conflicts with flag columns (e.g., `lhw_f` = "hours worked flag")
- `_ma` and `_fe`: ⚠️ Less clear
- `_M` and `_F`: ⚠️ Case-sensitive, less readable

---

## Files Modified

### Core Files
1. `scripts/RURO_prep_mnl_basic.py`
   - Added `_reshape_couples_to_wide()` (~168 lines)
   - Added `_build_mnl_block_couples_wide()` (~48 lines)
   - Modified `main()` to call reshape (~5 lines)
   - **Total additions:** ~220 lines

2. `scripts/RURO_estimate_FR.py`
   - 670 automated replacements
   - **Total changes:** 670 lines modified

### Temporary Files (CLEANED UP ✓)
- `apply_phase2_renames.py` - Deleted after use
- `scripts/RURO_estimate_FR.py.backup_phase2` - Deleted after verification

### Documentation
- `COUPLES_DATA_RESHAPE_FIX_PLAN.md` - Complete implementation plan
- `PHASE_1_2_COMPLETION_SUMMARY.md` - This file

---

## Expected Outcomes (To Be Verified in Phase 3)

After fixes:
- ✅ Couples MNL data: 286,800 rows (1 per household-draw)
- ✅ Columns exist: `lhw_male`, `lhw_female`, `wage_male`, `wage_female`, etc.
- ⏳ Opportunity variables have variation (not constant/missing)
- ⏳ Gradients non-zero for all parameter groups
- ⏳ All 60 parameters estimated (not just 18)
- ⏳ No conflicts with flag columns

---

## Next Steps (Phase 3)

1. ⏳ Test estimation with reshaped dataset
2. ⏳ Verify all columns are found
3. ⏳ Check parameter gradients are non-zero
4. ⏳ Confirm all 60 parameters move during optimization
5. ⏳ Compare results to pre-fix baseline

---

## Key Lessons Learned

1. **Always check data format assumptions** - The estimation code assumed wide format but data prep created long format
2. **Naming matters** - Flag columns ending in `_f` required careful suffix choice
3. **Automate carefully** - Word boundary regex essential to avoid partial matches
4. **Verify native columns** - Must not rename EUROMOD native columns
5. **Clean up temporary files** - Remove diagnostic scripts after use

---

**Status:** Phase 1 ✓ | Phase 2 ✓ | Phase 3 ⏳ (In Progress)
