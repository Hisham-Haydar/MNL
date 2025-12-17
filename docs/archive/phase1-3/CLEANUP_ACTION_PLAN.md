# Cleanup Action Plan - MNL Repository

**Date:** December 16, 2025
**Purpose:** Clean up temporary files, redundant documentation, and prepare for production pipeline run

---

## ✅ Pipeline Verification (run_fr_2016_joint_only.ps1)

### Scripts Used by Pipeline - All Fixed!

| Step | Script | Status | Fixes Applied |
|------|--------|--------|---------------|
| **Step 1** | france_data_prep.py | ✅ FIXED | Merge logic prioritizes EUROMOD outputs |
| **Step 2** | RURO_prep.py | ✅ OK | No fixes needed |
| **Step 3** | RURO_draws.py | ✅ OK | No fixes needed |
| **Step 4** | RURO_euromod.py | ✅ FIXED | yem00/yemxp split + column filtering |
| **Step 5** | prepare_FR_gsur.py | ✅ OK | No fixes needed |
| **Step 6** | RURO_prep_mnl_basic.py | ✅ OK | No fixes needed |
| **Step 7** | RURO_estimate_FR.py | ✅ OK | No fixes needed |

**VERDICT:** ✅ **Pipeline is READY TO RUN with all critical fixes applied!**

---

## 🗑️ Files to Delete (14 files)

### Temporary Python Scripts (9 files)
**Purpose:** These were created during debugging and are no longer needed

```powershell
Remove-Item U:\Desktop\Nizam_Hisham\MNL\temp_check_columns.py
Remove-Item U:\Desktop\Nizam_Hisham\MNL\temp_check_consumption.py
Remove-Item U:\Desktop\Nizam_Hisham\MNL\temp_check_euromod_output.py
Remove-Item U:\Desktop\Nizam_Hisham\MNL\temp_check_original.py
Remove-Item U:\Desktop\Nizam_Hisham\MNL\temp_check_ruro_ready.py
Remove-Item U:\Desktop\Nizam_Hisham\MNL\temp_check_singles_vs_couples.py
Remove-Item U:\Desktop\Nizam_Hisham\MNL\temp_check_structure.py
Remove-Item U:\Desktop\Nizam_Hisham\MNL\temp_check_yem_calculation.py
Remove-Item U:\Desktop\Nizam_Hisham\MNL\temp_count_constant_ils_dispy.py
```

### Temporary Files (3 files)
```powershell
Remove-Item U:\Desktop\Nizam_Hisham\MNL\check_gamspy.py
Remove-Item U:\Desktop\Nizam_Hisham\MNL\temp_freeze.txt
Remove-Item U:\Desktop\Nizam_Hisham\MNL\euromod_debug.log
```

### Empty Config Files (1 file)
```powershell
Remove-Item U:\Desktop\Nizam_Hisham\MNL\.editorconfig  # 0 bytes
```

**Total to delete:** 13 files

---

## 📁 Documentation to Archive (Move to docs/archive/)

### Debugging Documentation (Archive - Keep for Reference)
**These documents were valuable during debugging but are superseded by final documentation**

```powershell
# Create archive directory
New-Item -ItemType Directory -Force -Path U:\Desktop\Nizam_Hisham\MNL\docs\archive

# Move debugging docs
Move-Item U:\Desktop\Nizam_Hisham\MNL\BREAKTHROUGH_FINDINGS_2025-12-15.md docs\archive\
Move-Item U:\Desktop\Nizam_Hisham\MNL\BUG_REPORT_2025-12-08.md docs\archive\
Move-Item U:\Desktop\Nizam_Hisham\MNL\CONVERSATION_SUMMARY_2025-12-14.md docs\archive\
Move-Item U:\Desktop\Nizam_Hisham\MNL\COUPLES_CONSUMPTION_BUG_ANALYSIS.md docs\archive\
Move-Item U:\Desktop\Nizam_Hisham\MNL\DATA_QUALITY_ISSUES_2025-12-15.md docs\archive\
Move-Item U:\Desktop\Nizam_Hisham\MNL\EUROMOD_FIX_SUMMARY_2025-12-14.md docs\archive\
Move-Item U:\Desktop\Nizam_Hisham\MNL\EUROMOD_INVESTIGATION_SUMMARY_2025-12-15.md docs\archive\
Move-Item U:\Desktop\Nizam_Hisham\MNL\LOGGING_ENHANCEMENTS_2025-12-14.md docs\archive\
Move-Item U:\Desktop\Nizam_Hisham\MNL\PIPELINE_RUN_ANALYSIS_2025-12-14.md docs\archive\
Move-Item U:\Desktop\Nizam_Hisham\MNL\POST_ESTIMATION_STATUS.md docs\archive\
```

**Reason:** These documents capture the debugging journey but are now superseded by:
- `COMPLETE_FIX_DOCUMENTATION.md` (comprehensive fix reference)
- `FIXES_APPLIED_SUMMARY.md` (session summary)
- `CRITICAL_FIX_yem00_discovery.md` (critical discovery - KEEP in root)

---

## 📚 Documentation to KEEP (Root Directory)

### Essential Current Documentation (11 files)

| File | Purpose | Keep? |
|------|---------|-------|
| **COMPLETE_FIX_DOCUMENTATION.md** | ✅ KEEP | Comprehensive reference for all fixes |
| **FIXES_APPLIED_SUMMARY.md** | ✅ KEEP | Session summary (just created) |
| **SCRIPT_AUDIT_CLEANUP_PLAN.md** | ✅ KEEP | Script cleanup plan |
| **CRITICAL_FIX_yem00_discovery.md** | ✅ KEEP | Critical discovery documentation |
| **VARIABLE_MAPPING_ANALYSIS.md** | ✅ KEEP | Variable reference |
| **EUROMO_sys_france_2015.md** | ✅ KEEP | French EUROMOD system reference |
| **CLAUDE.md** | ✅ KEEP | AI assistant guide |
| **JOINT_ESTIMATION_GUIDE.md** | ✅ KEEP | Parameter guide |
| **PIPELINE_SUMMARY.md** | ✅ KEEP | Pipeline execution reference |
| **QUICK_REFERENCE.md** | ✅ KEEP | Command cheat sheet |
| **QUICK_START.md** | ✅ KEEP | Quick start guide |
| **READY_TO_RUN.md** | ✅ KEEP | Pipeline readiness check |
| **README.md** | ✅ KEEP | Project overview |

### Configuration Files (3 files)
| File | Purpose | Keep? |
|------|---------|-------|
| **pyproject.toml** | ✅ KEEP | Python package config |
| **requirements.txt** | ✅ KEEP | Dependencies |
| **.gitignore** | ✅ KEEP | Git exclusions |

---

## 🧹 Cleanup Script

### PowerShell Script to Execute Cleanup

```powershell
# =====================================================================
# CLEANUP SCRIPT - MNL Repository
# =====================================================================
# This script removes temporary files and archives debugging docs
# Run from project root: U:\Desktop\Nizam_Hisham\MNL
# =====================================================================

Write-Host "Starting MNL Repository Cleanup..." -ForegroundColor Cyan
Write-Host ""

# Set project root
$PROJ_ROOT = "U:\Desktop\Nizam_Hisham\MNL"
Set-Location $PROJ_ROOT

# =====================================================================
# STEP 1: Delete Temporary Files
# =====================================================================
Write-Host "STEP 1: Deleting temporary files..." -ForegroundColor Yellow

$tempFiles = @(
    "temp_check_columns.py",
    "temp_check_consumption.py",
    "temp_check_euromod_output.py",
    "temp_check_original.py",
    "temp_check_ruro_ready.py",
    "temp_check_singles_vs_couples.py",
    "temp_check_structure.py",
    "temp_check_yem_calculation.py",
    "temp_count_constant_ils_dispy.py",
    "check_gamspy.py",
    "temp_freeze.txt",
    "euromod_debug.log",
    ".editorconfig"
)

$deletedCount = 0
foreach ($file in $tempFiles) {
    $fullPath = Join-Path $PROJ_ROOT $file
    if (Test-Path $fullPath) {
        Remove-Item $fullPath -Force
        Write-Host "  ✅ Deleted: $file" -ForegroundColor Green
        $deletedCount++
    } else {
        Write-Host "  ⚠️  Not found: $file" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Deleted $deletedCount temporary files" -ForegroundColor Cyan
Write-Host ""

# =====================================================================
# STEP 2: Archive Debugging Documentation
# =====================================================================
Write-Host "STEP 2: Archiving debugging documentation..." -ForegroundColor Yellow

# Create archive directory
$archiveDir = Join-Path $PROJ_ROOT "docs\archive"
if (-not (Test-Path $archiveDir)) {
    New-Item -ItemType Directory -Force -Path $archiveDir | Out-Null
    Write-Host "  Created archive directory: docs\archive" -ForegroundColor Green
}

$debugDocs = @(
    "BREAKTHROUGH_FINDINGS_2025-12-15.md",
    "BUG_REPORT_2025-12-08.md",
    "CONVERSATION_SUMMARY_2025-12-14.md",
    "COUPLES_CONSUMPTION_BUG_ANALYSIS.md",
    "DATA_QUALITY_ISSUES_2025-12-15.md",
    "EUROMOD_FIX_SUMMARY_2025-12-14.md",
    "EUROMOD_INVESTIGATION_SUMMARY_2025-12-15.md",
    "LOGGING_ENHANCEMENTS_2025-12-14.md",
    "PIPELINE_RUN_ANALYSIS_2025-12-14.md",
    "POST_ESTIMATION_STATUS.md"
)

$archivedCount = 0
foreach ($doc in $debugDocs) {
    $sourcePath = Join-Path $PROJ_ROOT $doc
    $destPath = Join-Path $archiveDir $doc
    if (Test-Path $sourcePath) {
        Move-Item $sourcePath $destPath -Force
        Write-Host "  ✅ Archived: $doc" -ForegroundColor Green
        $archivedCount++
    } else {
        Write-Host "  ⚠️  Not found: $doc" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Archived $archivedCount debugging documents" -ForegroundColor Cyan
Write-Host ""

# =====================================================================
# STEP 3: Summary
# =====================================================================
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "CLEANUP COMPLETE" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor White
Write-Host "  Deleted files:    $deletedCount" -ForegroundColor Green
Write-Host "  Archived docs:    $archivedCount" -ForegroundColor Green
Write-Host "  Archive location: docs\archive\" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your repository is now clean and ready for production pipeline run!" -ForegroundColor Green
Write-Host ""

# =====================================================================
# STEP 4: Verify Essential Files
# =====================================================================
Write-Host "Verifying essential files still present..." -ForegroundColor Yellow

$essentialFiles = @(
    "COMPLETE_FIX_DOCUMENTATION.md",
    "FIXES_APPLIED_SUMMARY.md",
    "SCRIPT_AUDIT_CLEANUP_PLAN.md",
    "CRITICAL_FIX_yem00_discovery.md",
    "VARIABLE_MAPPING_ANALYSIS.md",
    "EUROMO_sys_france_2015.md",
    "CLAUDE.md",
    "README.md"
)

$allPresent = $true
foreach ($file in $essentialFiles) {
    $fullPath = Join-Path $PROJ_ROOT $file
    if (Test-Path $fullPath) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ MISSING: $file" -ForegroundColor Red
        $allPresent = $false
    }
}

Write-Host ""
if ($allPresent) {
    Write-Host "All essential files present ✅" -ForegroundColor Green
} else {
    Write-Host "Some essential files are missing ❌" -ForegroundColor Red
}

Write-Host ""
Write-Host "Done! You can now run the pipeline." -ForegroundColor Green
```

---

## 📊 Before/After Comparison

### Before Cleanup (Root Directory)

```
Total files: 41
- Documentation: 28 markdown files
- Config: 3 files (.editorconfig, pyproject.toml, requirements.txt, .gitignore)
- Temporary: 13 files (temp_*.py, check_gamspy.py, temp_freeze.txt, etc.)
```

### After Cleanup (Root Directory)

```
Total files: 17
- Documentation: 14 markdown files (essential only)
- Config: 3 files (pyproject.toml, requirements.txt, .gitignore)
- Archived: 10 markdown files moved to docs/archive/
- Deleted: 13 temporary files removed
```

**Result:** 58% reduction in root directory files (41 → 17)

---

## 🚀 Next Steps After Cleanup

### 1. Run Cleanup Script
```powershell
# Save the cleanup script above to: cleanup_repo.ps1
# Then run:
powershell -ExecutionPolicy Bypass -File cleanup_repo.ps1
```

### 2. Verify Pipeline is Ready
```powershell
# Check that all pipeline scripts exist and have fixes
Get-ChildItem -Path scripts -Filter "RURO_*.py" | Select-Object Name
Get-ChildItem -Path scripts -Filter "france_*.py" | Select-Object Name
Get-ChildItem -Path scripts -Filter "run_*.ps1" | Select-Object Name
```

### 3. Delete Intermediate Data Files (Fresh Start)
```powershell
# Delete Step 2-4 outputs to test from scratch
Remove-Item U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready.parquet
Remove-Item U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready.parquet
Remove-Item U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready_RURO_draws.parquet
Remove-Item U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet
Remove-Item U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016\combined_draws_em.parquet

# Keep Step 1 output (if it's recent and has the merge fix)
# Otherwise delete:
# Remove-Item U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_processed.parquet
```

### 4. Run Full Pipeline
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_fr_2016_joint_only.ps1
```

---

## ✅ Verification Checklist

Before running the pipeline, verify:

- [ ] All temporary files deleted
- [ ] Debugging docs archived to docs/archive/
- [ ] Essential documentation still in root
- [ ] Pipeline script exists: `scripts/run_fr_2016_joint_only.ps1`
- [ ] Core scripts have fixes:
  - [ ] `scripts/france_data_prep.py` has merge fix
  - [ ] `scripts/RURO_euromod.py` has yem00/yemxp split fix
- [ ] Intermediate data files deleted for fresh test
- [ ] Python environment activated
- [ ] Ready to run pipeline!

---

**Status: CLEANUP PLAN READY - EXECUTE TO CLEAN REPOSITORY**
