# Script Audit and Cleanup Plan

**Date:** December 16, 2025
**Total Scripts:** 56 Python files
**Purpose:** Identify redundant scripts, consolidate code, improve maintainability

---

## Executive Summary

The `scripts/` directory contains **56 Python scripts** across multiple approaches and stages of development. Many are **redundant, deprecated, or superseded** by newer implementations.

**Recommended Action:** Archive 30+ scripts, keep 20-25 core/utility scripts, consolidate documentation.

---

## Script Categories

### 1. Core RURO Pipeline Scripts (KEEP - 9 files)

**Essential scripts for the production RURO pipeline:**

| Script | Purpose | Status | Notes |
|--------|---------|--------|-------|
| **france_data_prep.py** | Step 1: Data preparation | ✅ ACTIVE | **FIXED** - Merge logic corrected |
| **RURO_prep.py** | Step 2: RURO variable creation | ✅ ACTIVE | Used by all pipelines |
| **RURO_draws.py** | Step 3: Generate wage/hours draws | ✅ ACTIVE | Core functionality |
| **RURO_euromod.py** | Step 4: EUROMOD simulation | ✅ ACTIVE | **FIXED** - yem00/yemxp split added |
| **prepare_FR_gsur.py** | Step 5: GSUR probability calculation | ✅ ACTIVE | France-specific |
| **RURO_prep_mnl_basic.py** | Step 6: MNL dataset creation | ✅ ACTIVE | Long format conversion |
| **RURO_estimate_FR.py** | Step 7: Parameter estimation | ✅ ACTIVE | CLI estimator |
| **RURO_post_estimation.py** | Step 8: Post-estimation diagnostics | ✅ ACTIVE | Plots & reports |
| **path_helpers.py** | Utility: Path resolution | ✅ ACTIVE | Used by all scripts |

**Action:** KEEP all 9 scripts - these are the canonical RURO pipeline.

---

### 2. Pipeline Orchestration Scripts (KEEP - 3 files)

**Scripts that run multiple pipeline steps:**

| Script | Purpose | Use Case | Status |
|--------|---------|----------|--------|
| **run_pipeline_explicit.py** | Full pipeline runner (Steps 1-4) | ✅ RECOMMENDED | Interactive Jupyter-style execution |
| **run_full_pipeline_interactive.py** | Alternative pipeline runner | ⚠️ REDUNDANT? | Similar to explicit version |
| **run_pipeline_memory_only.py** | In-memory pipeline (no disk writes) | ✅ SPECIALIZED | Fast prototyping |

**Action:**
- KEEP `run_pipeline_explicit.py` as the **canonical pipeline runner**
- KEEP `run_pipeline_memory_only.py` for **fast prototyping**
- DECIDE: Is `run_full_pipeline_interactive.py` needed, or can it be merged with explicit version?

**Recommendation:** Consolidate the two interactive runners into ONE canonical version.

---

### 3. Utility/Helper Scripts (KEEP - 5 files)

**Useful helper scripts for specific tasks:**

| Script | Purpose | Status | Notes |
|--------|---------|--------|-------|
| **check_draws.py** | Inspect draw distributions | ✅ KEEP | Debugging tool |
| **analyze_identification.py** | Parameter identification analysis | ✅ KEEP | Diagnostic tool |
| **extract_excel_text.py** | Extract text from Excel files | ✅ KEEP | Data processing |
| **simple.py** | Simple test/demo script | ⚠️ UNCLEAR | Check if still needed |
| **data_prep2.py** | Alternative data prep? | ⚠️ REDUNDANT? | Check vs france_data_prep.py |

**Action:**
- KEEP utility scripts if actively used
- ARCHIVE `simple.py` if it's just a test
- INVESTIGATE `data_prep2.py` - likely redundant with `france_data_prep.py`

---

### 4. Fix/Debug Scripts (ARCHIVE - 8 files)

**One-off scripts created to fix specific issues - NOW SUPERSEDED:**

| Script | Purpose | Status | Reason to Archive |
|--------|---------|--------|-------------------|
| **fix_standard_errors.py** | Fix SE computation | ⚠️ ARCHIVE | Issue resolved in main code |
| **fix_beta_leisure.py** | Fix leisure parameter | ⚠️ ARCHIVE | Issue resolved |
| **fix_param_names.py** | Rename parameters | ⚠️ ARCHIVE | One-time fix completed |
| **test_hours_fix.py** | Test hours calculation | ⚠️ ARCHIVE | Test completed |
| **debug_hessian.py** | Debug Hessian computation | ⚠️ ARCHIVE | Issue resolved |
| **recompute_se.py** | Recompute standard errors | ⚠️ ARCHIVE | Superseded by post-estimation |
| **rerun_post_estimation.py** | Rerun post-estimation | ⚠️ REDUNDANT | Use RURO_post_estimation.py |
| **run_draws_euromod_interactive.py** | Interactive draws/EUROMOD | ⚠️ REDUNDANT | Use run_pipeline_explicit.py |

**Action:** ARCHIVE all to `scripts/archive/fixes/` - they served their purpose but are no longer needed.

---

### 5. Old/Deprecated RURO Scripts (ARCHIVE - 7 files)

**Scripts in `scripts/Old_Script_ruro(not well)/` - explicitly marked as outdated:**

| Script | Status | Action |
|--------|--------|--------|
| `run_fr_2021_prep.py` | ⚠️ OLD | Archive (replaced by france_data_prep.py) |
| `inspect_RURO_fr_2021.py` | ⚠️ OLD | Archive (inspection complete) |
| `full_RURO.py` | ⚠️ OLD | Archive (replaced by modular pipeline) |
| `RURO_gpt.py` | ⚠️ OLD | Archive (experimental version) |
| `trim_mnl_dataset.py` | ⚠️ OLD | Archive (dataset trimming complete) |
| `RURO_boxcox_mnl.py` | ⚠️ OLD | Archive (boxcox implemented in RURO_estimate_FR.py) |
| `RURO_boxcox_group_opportunities.py` | ⚠️ OLD | Archive (boxcox implemented in RURO_estimate_FR.py) |

**Action:** These are already in `Old_Script_ruro(not well)/`, so they're effectively archived. Consider moving entire directory to `scripts/archive/old_ruro/`.

---

### 6. Alternative RUM Approach (ARCHIVE - 22 files)

**Scripts in `scripts/RUM/` - different methodology (not RURO):**

| Category | Scripts | Status |
|----------|---------|--------|
| **DCM Estimation** | DCM1.py, DCM1_boxcox.py, DCM1_boxcox_gender_split.py, DCM1_gamspy.py, DCM2_gamspy.py, DCM2_gamspy_gender_split.py | ⚠️ DIFFERENT APPROACH |
| **Biogeme** | old_biogeme.py, biotest.py, set_biogeme_env.py, bio_boxcox.py | ⚠️ DIFFERENT APPROACH |
| **MLE/Training** | train_mnl.py, MLE_dcm.py | ⚠️ DIFFERENT APPROACH |
| **Data Prep (RUM)** | data_prep.py, old_prep.py, process2_py.py | ⚠️ DIFFERENT APPROACH |
| **Scenarios** | scenarios.py, scenarios_de.py, run_euromod.py | ⚠️ DIFFERENT APPROACH |
| **Analysis** | analyze_dcm_results.py, analyze_dcm_gender_split.py, analyzer_runner.py | ⚠️ DIFFERENT APPROACH |
| **Multi-year** | run_de_multi_year.py, combine_years_for_dcm.py | ⚠️ DIFFERENT APPROACH |

**Action:** ARCHIVE entire `scripts/RUM/` directory to `scripts/archive/rum_approach/`

**Reason:** These implement a **different methodology** (pure RUM without opportunity structure). They may be useful for comparison but are not part of the active RURO pipeline.

---

## Summary Table

| Category | Count | Action | Location |
|----------|-------|--------|----------|
| **Core RURO Pipeline** | 9 | ✅ KEEP | scripts/ (root) |
| **Pipeline Orchestration** | 3 | ✅ KEEP (consolidate to 2) | scripts/ (root) |
| **Utility Scripts** | 5 | ✅ KEEP (review 2) | scripts/ (root) |
| **Fix/Debug Scripts** | 8 | ⚠️ ARCHIVE | → scripts/archive/fixes/ |
| **Old RURO Scripts** | 7 | ⚠️ ARCHIVE | → scripts/archive/old_ruro/ |
| **RUM Approach Scripts** | 22 | ⚠️ ARCHIVE | → scripts/archive/rum_approach/ |
| **TOTAL** | 54 | **Keep: 20-22, Archive: 32-34** | |

---

## Recommended Directory Structure

### Current Structure
```
scripts/
├── france_data_prep.py
├── RURO_*.py (8 files)
├── run_pipeline_*.py (3 files)
├── fix_*.py (3 files)
├── debug_*.py (1 file)
├── check_*.py (1 file)
├── analyze_*.py (1 file)
├── recompute_*.py (1 file)
├── rerun_*.py (1 file)
├── test_*.py (1 file)
├── simple.py
├── data_prep2.py
├── extract_excel_text.py
├── path_helpers.py
├── prepare_FR_gsur.py
├── RUM/ (22 files)
└── Old_Script_ruro(not well)/ (7 files)
```

### Proposed Structure
```
scripts/
├── Core Pipeline (9 files)
│   ├── france_data_prep.py
│   ├── RURO_prep.py
│   ├── RURO_draws.py
│   ├── RURO_euromod.py
│   ├── prepare_FR_gsur.py
│   ├── RURO_prep_mnl_basic.py
│   ├── RURO_estimate_FR.py
│   ├── RURO_post_estimation.py
│   └── path_helpers.py
│
├── Pipeline Runners (2 files)
│   ├── run_pipeline_canonical.py  (consolidated from explicit + interactive)
│   └── run_pipeline_memory_only.py
│
├── Utilities (3-5 files)
│   ├── check_draws.py
│   ├── analyze_identification.py
│   └── extract_excel_text.py
│
└── archive/
    ├── fixes/
    │   ├── fix_standard_errors.py
    │   ├── fix_beta_leisure.py
    │   ├── fix_param_names.py
    │   ├── test_hours_fix.py
    │   ├── debug_hessian.py
    │   ├── recompute_se.py
    │   ├── rerun_post_estimation.py
    │   └── run_draws_euromod_interactive.py
    │
    ├── old_ruro/
    │   └── [7 files from Old_Script_ruro(not well)/]
    │
    └── rum_approach/
        └── [22 files from RUM/]
```

---

## Cleanup Actions

### Step 1: Create Archive Directory Structure
```bash
mkdir -p scripts/archive/fixes
mkdir -p scripts/archive/old_ruro
mkdir -p scripts/archive/rum_approach
```

### Step 2: Move Fix/Debug Scripts
```bash
mv scripts/fix_*.py scripts/archive/fixes/
mv scripts/debug_*.py scripts/archive/fixes/
mv scripts/recompute_*.py scripts/archive/fixes/
mv scripts/rerun_*.py scripts/archive/fixes/
mv scripts/test_hours_fix.py scripts/archive/fixes/
mv scripts/run_draws_euromod_interactive.py scripts/archive/fixes/
```

### Step 3: Move Old RURO Scripts
```bash
mv scripts/Old_Script_ruro\(not\ well\)/* scripts/archive/old_ruro/
rmdir scripts/Old_Script_ruro\(not\ well\)
```

### Step 4: Move RUM Approach Scripts
```bash
mv scripts/RUM/* scripts/archive/rum_approach/
rmdir scripts/RUM
```

### Step 5: Consolidate Pipeline Runners

**Option A:** Keep both as-is (if they serve different purposes)

**Option B:** Merge into canonical version
```bash
# Review run_pipeline_explicit.py and run_full_pipeline_interactive.py
# Merge best features into run_pipeline_canonical.py
# Archive the others
```

### Step 6: Review Remaining Utility Scripts
```bash
# Decide on:
# - simple.py (likely archive)
# - data_prep2.py (likely archive if redundant with france_data_prep.py)
```

---

## Benefits of Cleanup

1. **Reduced Confusion:** Clear distinction between active and archived code
2. **Easier Maintenance:** Only maintain scripts that are actively used
3. **Better Documentation:** README can focus on core pipeline
4. **Faster Onboarding:** New users see only relevant scripts
5. **Preserved History:** Archived scripts remain available if needed

---

## Final Script Count (After Cleanup)

| Category | Count |
|----------|-------|
| **Active Core Pipeline** | 9 |
| **Active Orchestration** | 2 |
| **Active Utilities** | 3-5 |
| **TOTAL ACTIVE** | **14-16** |
| **Archived** | 37-39 |

**Result:** ~70% reduction in visible scripts, much cleaner repository!

---

## Next Steps

1. ✅ Document all fixes (COMPLETE - see COMPLETE_FIX_DOCUMENTATION.md)
2. ⏳ Create archive directories
3. ⏳ Move deprecated scripts to archive
4. ⏳ Consolidate pipeline runners
5. ⏳ Update README.md to reflect new structure
6. ⏳ Test that core pipeline still works after cleanup
7. ⏳ Commit cleanup with clear git message

---

## Consolidation Opportunities

### Opportunity 1: Merge Interactive Pipeline Runners

**Files:**
- `run_pipeline_explicit.py` (660 lines)
- `run_full_pipeline_interactive.py` (464 lines)
- `run_pipeline_memory_only.py` (400 lines)

**Approach:**
- Keep `run_pipeline_explicit.py` as the **canonical interactive runner**
- Add `--memory-only` flag to avoid disk writes (merge from memory_only version)
- Archive `run_full_pipeline_interactive.py` if it's redundant
- Result: ONE canonical pipeline runner with options

### Opportunity 2: Consolidate Fix Scripts into Core

**Instead of separate fix_*.py scripts:**
- Fixes should be **integrated into core scripts** (france_data_prep.py, RURO_euromod.py, etc.)
- This has already been done! ✅
- Archive the standalone fix scripts

### Opportunity 3: Create Utility Module

**Instead of scattered utility scripts:**
```python
# scripts/utils/__init__.py
from .check_draws import check_draw_distributions
from .analyze_identification import analyze_parameter_identification
from .extract_excel import extract_excel_text

# Usage:
from utils import check_draw_distributions
```

**Benefits:**
- Cleaner imports
- Better organization
- Easier to find utilities

---

## Conclusion

**Current state:** 54 Python scripts, many redundant or deprecated
**Proposed state:** 14-16 active scripts, 37-39 archived
**Cleanup effort:** ~2 hours (creating structure, moving files, testing, updating docs)
**Maintenance benefit:** Significantly reduced complexity and confusion

**Recommendation:** Proceed with cleanup after testing the current pipeline with all fixes applied.

---

**Status: AUDIT COMPLETE - READY FOR CLEANUP**
