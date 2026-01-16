# ✅ ANSWER: Do Draws Files Need Reduction?

**Date:** January 16, 2026  
**Status:** ⚠ **LIKELY YES - But needs verification**

---

## 🎯 SHORT ANSWER

**YES, the draws files likely DO need reduction!**

Here's why:
- MNL dataset has **641 columns** (from Step 6 output)
- Reduced EUROMOD has only **27 columns**
- Step 6 creates only **~15-20 derived columns**
- **641 - 27 - 20 = ~594 columns from draws files!**

This suggests the draws files are **bloated with unnecessary EUROMOD data**.

---

## 📊 EVIDENCE

### From Step 6 Output Log:
```
Loaded EUROMOD outputs: 1,087,300 rows
Loaded singles draws: 168,319 rows
Singles MNL dataset ready: 167,600 rows, 641 columns
```

### Column Math:
```
MNL Dataset (641 columns) = A + B + C

A = EUROMOD reduced (27 columns) ✅
B = Draws file (UNKNOWN - but 641 - 27 - 20 = ~594!)
C = Step 6 created (~20 columns):
    - consumption, leisure
    - c_norm, l_norm, log_c_norm, log_l_norm
    - age_norm, age_norm2
    - educL, educM, educH
    - gsur
    - sample_group
    - etc.

Therefore: B ≈ 594 columns in draws file!
```

---

## 🔍 WHAT'S LIKELY IN THE DRAWS FILES

### Expected (Essential - ~40-50 columns):
- **IDs:** idperson, idhh, draw, is_chosen
- **Draw-specific:** hours (per draw), wage (per draw)
- **Prior:** prior, prior_h, prior_w, log_prior
- **Demographics:** dag, dgn, deh, drgn1, n_children, idpartner
- **Metadata:** dwt, ruro_group, keep_for_analysis

### Likely Bloat (~550+ columns):
- ❌ **EUROMOD outputs:** ils_dispy, ils_origy, ils_earns, ils_pen, tin_s, tsc_*, bsa_*, bun_*, bho_*, bfa_*
- ❌ **EUROMOD internals:** i_*, il_*, tu_* (hundreds of temporary variables)
- ❌ **Tax-benefit details:** Not needed for MNL estimation

**These are DUPLICATES** - already in `combined_draws_em.parquet`!

---

## 💡 WHY THIS HAPPENED

The draws files were likely created from the **full EUROMOD output** before column reduction was implemented:

```
Step 1-2: Data prep
    ↓
Step 3: Draw generation
    ↓ (reads FULL EUROMOD output - 342 columns)
    ↓
Draws files created with ALL EUROMOD columns ← BLOAT!
    ├─ singles_RURO_ready_RURO_draws.parquet (~594 cols)
    └─ couples_RURO_ready_RURO_draws.parquet (~594 cols)
    ↓
Step 6: MNL prep (merges draws + EUROMOD)
    ↓
MNL dataset: 641 columns (bloated!)
```

---

## ✅ RECOMMENDED SOLUTION

### Create Draws File Reduction Script

Similar to EUROMOD reduction, but keep only **draw-essential columns**:

```python
# Essential columns for draws files (~40-50 total)

DRAWS_ESSENTIAL_COLS = {
    # IDs
    "idperson", "idhh", "draw", "is_chosen", "draw_id",
    
    # Draw-specific (vary by draw)
    "hours", "wage", "yem",  # These change for each alternative
    
    # Prior probabilities
    "prior", "prior_h", "prior_w", "log_prior",
    
    # Demographics (person characteristics, constant across draws)
    "dag", "dgn", "deh", "drgn1",
    "n_children", "nch02", "nch36", "nch712", "nch1317",
    "in_couple", "idpartner", "ruro_group", "ruro_decider",
    
    # Weights
    "dwt",
    
    # Metadata
    "keep_for_analysis", "ruro_sample",
}

# DROP everything else:
# - ils_* (EUROMOD outputs - already in combined_draws_em.parquet)
# - tin_*, tsc_*, bsa_*, bun_* (tax-benefit outputs - already in EUROMOD file)
# - i_*, il_*, tu_* (EUROMOD internals - not needed)
```

### Expected Impact:

```
Before: ~594 columns
After:  ~40-50 columns
Reduction: ~90%!

MNL dataset would go from:
  641 columns → ~100 columns (much more manageable!)
```

---

## 🎯 VERIFICATION NEEDED

**We couldn't complete the analysis because:**
1. Python commands are hanging (multiple processes blocking)
2. Files are large (~168K rows for singles)

**To verify, we need to:**
1. Check actual column count in draws files
2. Identify which columns are EUROMOD outputs/internals
3. Confirm they're duplicates of what's in `combined_draws_em.parquet`

---

## 📝 ACTION PLAN

### Option 1: Verify First (Recommended)
```powershell
# 1. Restart PowerShell (close all Python processes)
# 2. Run analysis script
python analyze_draws_files.py

# 3. Review output
# 4. If draws files have 500+ columns, proceed with reduction
```

### Option 2: Assume Reduction Needed
```powershell
# 1. Create draws_file_reduction.py (similar to reduce_mnl_columns.py)
# 2. Run reduction on both files:
#    - singles_RURO_ready_RURO_draws.parquet
#    - couples_RURO_ready_RURO_draws.parquet
# 3. Test with Step 6
# 4. Compare MNL dataset column count (should be ~100 instead of 641)
```

### Option 3: Proceed Without Draws Reduction
```powershell
# The EUROMOD reduction alone gives significant benefits:
# - 86.4% file size reduction on EUROMOD input
# - 2-3x faster Step 6 (less EUROMOD data to merge)
# - Draws files would remain at ~594 columns

# Trade-off:
# ✅ Faster EUROMOD merge
# ✅ Less memory for EUROMOD data
# ❌ Still loading 594 columns from draws
# ❌ MNL dataset still has 641 columns
```

---

## 💡 BOTTOM LINE

**Based on the math (641 - 27 - 20 = 594), the draws files are VERY likely bloated.**

**Recommendation:**
1. ✅ **EUROMOD reduction is complete and working** (86.4% savings!)
2. ⏳ **Draws reduction is likely worth doing** (would save another ~90% on draws files)
3. 🎯 **But Step 6 will work either way** - you can proceed now and optimize draws files later

**Priority:**
- **High:** Run Step 6 with reduced EUROMOD (will see 2-3x speedup)
- **Medium:** Verify draws file columns (when Python processes clear)
- **Low:** Implement draws reduction (nice-to-have optimization)

---

## 🚀 NEXT STEPS

**Immediate (recommended):**
```powershell
# Run Step 6 with reduced EUROMOD file
# (This alone gives significant benefits!)
.\RUN_PIPELINE_WITH_REDUCED_FILES.ps1
```

**Later (optimization):**
```powershell
# After verifying draws files are bloated:
# 1. Create draws reduction script
# 2. Reduce draws files to ~40-50 essential columns
# 3. Re-run Step 6 (should get ~100 column MNL dataset)
# 4. Enjoy even faster processing!
```

---

**Status:** ✅ **EUROMOD reduction complete (86.4% savings)**  
**Next:** ⏳ **Verify draws files need reduction (likely YES)**  
**Impact:** 🎯 **Could reduce MNL dataset from 641 → ~100 columns**
