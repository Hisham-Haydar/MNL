# Couples Data Reshape Fix Plan

**Date:** 2025-12-16
**Issue:** Missing reshape step converts couples data from long to wide format
**Severity:** CRITICAL - prevents opportunity parameters from being estimated

---

## Root Cause Analysis

### Current Data Flow (BROKEN)

**Step 1: RURO_draws.py** ✅ WORKS CORRECTLY
- Creates couples draws in **LONG format**
- Structure: 2 rows per household-draw (one for head, one for partner)
- Columns: `lhw`, `wage`, `hours`, `yem00`, `yemxp`, `deh`, `pexp` (common names)
- Gender identified by `dgn`: 0 = female, 1 = male
- Result: 583,854 rows (2,900 households × 100 draws × 2 persons)

**Step 2: RURO_euromod.py** ✅ WORKS CORRECTLY
- Processes both rows (male + female) through EUROMOD
- Returns disposable income `ils_dispy` for each person
- Stays in LONG format

**Step 3: RURO_prep_mnl_basic.py** ❌ **MISSING RESHAPE STEP**
- **Problem**: Does NOT reshape couples from long to wide
- **Should do**: Pivot to 1 row per household-draw with `_male`/`_female` columns
- **Currently does**: Just passes data through unchanged in long format
- Result: Final MNL dataset has 580,000 rows (should be 290,000)

**Step 4: Estimation code** ❌ EXPECTS WIDE FORMAT
- `precompute_data_couples()` tries to read columns with `_m` and `_f` suffixes
- These columns don't exist → safe_get() returns zeros
- No variation → zero gradients → opportunity parameters can't be estimated

---

## Naming Convention Issue

**Problem**: Using `_f` suffix conflicts with existing FLAG columns
- Existing: `lhw_f` = flag (not "hours worked female")
- Existing: `yem_f` = flag (not "employment income female")

**Solution**: Use **`_male` and `_female`** suffixes (clearest, no conflicts)

---

## Required Changes

### 1. RURO_prep_mnl_basic.py - Add Reshape Function

**Location**: After line 199 (`_build_mnl_block` function)

**New function**: `_reshape_couples_to_wide()`

```python
def _reshape_couples_to_wide(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reshape couples data from long format (2 rows per household-draw) to
    wide format (1 row per household-draw with _male and _female columns).

    Input (LONG):
        idhh    draw    dgn    lhw    wage    yem00    deh    pexp    ...
        1001    0       1      40     15.5    2400     3      5       ... (male)
        1001    0       0      35     12.0    2100     4      3       ... (female)

    Output (WIDE):
        idhh    draw    lhw_male    lhw_female    wage_male    wage_female    ...
        1001    0       40          35            15.5         12.0           ...

    Uses dgn (0=female, 1=male) to identify gender.
    """
    import logging

    if "ruro_group" not in df.columns:
        raise KeyError("Expected 'ruro_group' column for couples identification.")

    # Only reshape couples data (ruro_group == 10)
    is_couple = df["ruro_group"] == 10

    if not is_couple.any():
        logging.info("No couples data to reshape (ruro_group != 10).")
        return df

    df_couples = df[is_couple].copy()
    df_non_couples = df[~is_couple].copy()

    if "dgn" not in df_couples.columns:
        raise KeyError("Couples data must have 'dgn' column for gender identification.")

    if "idhh" not in df_couples.columns:
        raise KeyError("Couples data must have 'idhh' column for household identification.")

    if "draw" not in df_couples.columns:
        raise KeyError("Couples data must have 'draw' column.")

    # Verify we have 2 rows per household-draw
    dgn = pd.to_numeric(df_couples["dgn"], errors="coerce").fillna(-1).astype(int)
    rows_per_hh_draw = df_couples.groupby(["idhh", "draw"]).size()

    if not (rows_per_hh_draw == 2).all():
        n_bad = (rows_per_hh_draw != 2).sum()
        logging.warning(
            f"Expected 2 rows per (idhh, draw) for couples, but {n_bad} "
            f"household-draws have different counts. Proceeding anyway..."
        )

    # Identify male/female rows
    male_mask = dgn == 1
    female_mask = dgn == 0

    df_male = df_couples[male_mask].copy()
    df_female = df_couples[female_mask].copy()

    logging.info(f"Reshaping couples: {len(df_male)} male rows, {len(df_female)} female rows")

    # Columns to reshape (exclude ID columns and flags)
    id_cols = ["idhh", "draw", "idperson", "idorighh", "idorigperson"]
    flag_cols = [c for c in df_couples.columns if c.endswith("_f") or c.endswith("_s") or c.endswith("_a")]

    # Columns to pivot: numeric/categorical data that varies by gender
    pivot_cols = []
    for col in df_couples.columns:
        if col in id_cols or col in flag_cols:
            continue
        if col in ("dgn", "ruro_group", "ruro_decider", "hh_IsHead", "hh_IsPartner"):
            continue  # structural columns
        if col.startswith("tu_") or col.startswith("i_") or col.startswith("il_"):
            continue  # EUROMOD internal variables
        pivot_cols.append(col)

    logging.info(f"Pivoting {len(pivot_cols)} columns to _male/_female format")

    # Suffix male/female columns
    rename_male = {col: f"{col}_male" for col in pivot_cols}
    rename_female = {col: f"{col}_female" for col in pivot_cols}

    df_male_renamed = df_male.rename(columns=rename_male)
    df_female_renamed = df_female.rename(columns=rename_female)

    # Merge on (idhh, draw)
    df_wide = df_male_renamed.merge(
        df_female_renamed,
        on=["idhh", "draw"],
        how="inner",
        suffixes=("", "_DROP")
    )

    # Drop duplicate columns from merge
    drop_cols = [c for c in df_wide.columns if c.endswith("_DROP")]
    df_wide = df_wide.drop(columns=drop_cols)

    # Keep one copy of household-level variables (they're the same for both partners)
    # Remove _male suffix from household-level vars
    household_vars = ["ruro_group", "idhh", "draw"]
    for var in household_vars:
        male_var = f"{var}_male"
        if male_var in df_wide.columns:
            df_wide[var] = df_wide[male_var]
            df_wide = df_wide.drop(columns=[male_var, f"{var}_female"], errors="ignore")

    logging.info(f"Reshaped couples data: {len(df_wide)} rows (was {len(df_couples)})")

    # Combine back with non-couples data if any
    if not df_non_couples.empty:
        # Ensure compatible schemas
        # Non-couples don't have _male/_female columns, so keep them separate
        # or handle appropriately
        logging.info("Returning only reshaped couples data (singles handled separately)")
        return df_wide

    return df_wide
```

**Integration**: Modify `main()` function (line 517-574)

```python
def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = parse_args()

    # ... existing code to load data ...

    # Build MNL blocks
    singles_mnl = _build_mnl_block(singles_long, sample_group="singles")

    if args.couples_draws:
        couples_path = Path(args.couples_draws).resolve()
        if not couples_path.exists():
            raise FileNotFoundError(f"Couples draws file not found: {couples_path}")
        couples_long = _read_df(couples_path)
        couples_long = _merge_euromod_outputs(couples_long, em_df)
        couples_long = _restrict_to_deciders(couples_long)

        # NEW: Reshape couples from long to wide format
        couples_wide = _reshape_couples_to_wide(couples_long)

        couples_mnl = _build_mnl_block(couples_wide, sample_group="couples")
        frames.append(couples_mnl)

    # ... rest of main() ...
```

---

### 2. RURO_estimate_FR.py - Update Column Names

**All functions that reference `_m` and `_f` columns:**

**Current naming:**
```python
l_m, l_f, age_norm_m, age_norm_f, educL_m, educH_m, educL_f, educH_f, pexp_m, pexp_f
```

**New naming:**
```python
l_male, l_female, age_norm_male, age_norm_female, educL_male, educH_male,
educL_female, educH_female, pexp_male, pexp_female
```

**Functions to update:**
1. `precompute_data_couples()` (line 555-659)
2. `fast_neg_ll_with_grad_couples()` (line 3463-3800)
3. `fast_log_likelihood_couples()` (line 2750-2900)
4. `ff_calc_util_couples()` (line 1501-1642)
5. All opportunity density functions for couples

**Example change** (precompute_data_couples):
```python
# OLD:
l_m = safe_get("l_m", 0.0)
l_f = safe_get("l_f", 0.0)

# NEW:
l_male = safe_get("l_male", 0.0)  # or "ruro_leisure_m" -> "leisure_male"
l_female = safe_get("l_female", 0.0)  # or "ruro_leisure_f" -> "leisure_female"
```

---

### 3. Update MNL Dataset Column Names

After reshape, the MNL dataset should have:

**Couples-specific columns** (wide format, 1 row per household-draw):
```
# Leisure
leisure_male, leisure_female  (or l_male, l_female)

# Hours worked
lhw_male, lhw_female
hours_male, hours_female

# Wages
wage_male, wage_female
yem00_male, yem00_female  (labour income)
yemxp_male, yemxp_female  (extra work income)

# Working status indicators
working_male, working_female
working_pt1_male, working_pt1_female
working_pt2_male, working_pt2_female
working_ft_male, working_ft_female

# Education (derived from deh)
educL_male, educH_male, educM_male
educL_female, educH_female, educM_female

# Experience
pexp_male, pexp_female
pexp_years_male, pexp_years_female

# Demographics
age_male, age_female
dag_male, dag_female  (if needed)

# GSUR (if implemented)
gsur_male, gsur_female
gsur_probability_male, gsur_probability_female

# Household-level (no gender suffix)
idhh, draw, chosen, ruro_group
consumption  (household aggregate from ils_dispy)
```

---

## Implementation Steps

### Phase 1: Data Preparation (RURO_prep_mnl_basic.py)

1. ✅ Add `_reshape_couples_to_wide()` function
2. ✅ Integrate into `main()` function
3. ✅ Create derived variables in wide format:
   - Education dummies from `deh_male`, `deh_female`
   - Experience squared from `pexp_male`, `pexp_female`
   - Working status from `hours_male`, `hours_female`
4. ✅ Test reshape logic with diagnostic script

### Phase 2: Estimation Code (RURO_estimate_FR.py)

1. ✅ Update `CouplesData` dataclass (if exists) with new column names
2. ✅ Update `precompute_data_couples()` - ALL column references
3. ✅ Update ALL couples likelihood functions:
   - `fast_neg_ll_with_grad_couples()`
   - `fast_log_likelihood_couples()`
   - `ff_calc_util_couples()`
   - `fast_neg_ll_with_grad_couples_precomputed()`
4. ✅ Update opportunity density functions:
   - Hours opportunity: `_m` → `_male`, `_f` → `_female`
   - Wage opportunity: `_m` → `_male`, `_f` → `_female`
5. ✅ Update parameter names if needed

### Phase 3: Testing

1. ✅ Run RURO_prep_mnl_basic.py with new reshape logic
2. ✅ Verify output MNL dataset structure:
   - Couples: 290,000 rows (was 580,000)
   - Columns: `*_male` and `*_female` exist and vary
3. ✅ Run estimation with updated code
4. ✅ Verify gradients are non-zero for opportunity parameters
5. ✅ Verify all 60 parameters move during optimization

---

## Expected Outcomes

After fixes:
- ✅ Couples MNL data: 290,000 rows (1 per household-draw, not 2)
- ✅ Columns exist: `lhw_male`, `lhw_female`, `wage_male`, `wage_female`, etc.
- ✅ Opportunity variables have variation (not constant or missing)
- ✅ Gradients non-zero for all parameter groups
- ✅ All 60 parameters estimated (not just 18)
- ✅ No conflicts with flag columns (lhw_f, yem_f remain as flags)

---

## Naming Convention Summary

**RECOMMENDED**: `_male` and `_female`
- Pros: Clear, explicit, no ambiguity, no conflicts
- Cons: Slightly longer

**Alternatives considered**:
- `_m` and `_f`: ❌ Conflicts with flag columns
- `_ma` and `_fe`: ⚠️ Less clear, but shorter
- `_M` and `_F`: ⚠️ Case-sensitive, less readable

**Decision**: Use `_male` and `_female` for maximum clarity and compatibility.

---

## Files to Modify

1. **scripts/RURO_prep_mnl_basic.py**
   - Add `_reshape_couples_to_wide()` function (~100 lines)
   - Modify `main()` to call reshape (2 lines)
   - Update `_build_mnl_block()` to create derived vars in wide format (optional)

2. **scripts/RURO_estimate_FR.py**
   - Update `precompute_data_couples()` (~20 column name changes)
   - Update all couples likelihood functions (~50 variable name changes)
   - Update opportunity functions (~30 variable name changes)
   - Estimated: ~100 lines to change

3. **Test/diagnostic scripts**
   - Update diagnostic scripts to check `_male`/`_female` columns
   - Verify reshape logic correctness

---

## Risk Assessment

**Low risk**:
- Name change is mechanical (search-replace)
- Reshape logic is standard pandas pivot operation
- Existing singles code unaffected

**Medium risk**:
- Need to ensure all column references updated
- Need comprehensive testing

**Mitigation**:
- Create backup before changes
- Test singles-only first (should be unaffected)
- Test couples-only before joint
- Add extensive logging to reshape function

---

**END OF PLAN**
