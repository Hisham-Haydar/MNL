# =====================================================================
# CLEANUP SCRIPT - MNL Repository
# =====================================================================
# This script removes temporary files and archives debugging docs
# Run from project root: powershell -ExecutionPolicy Bypass -File cleanup_repo.ps1
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
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review CLEANUP_ACTION_PLAN.md for details" -ForegroundColor White
Write-Host "  2. Delete intermediate data files (optional - for fresh test)" -ForegroundColor White
Write-Host "  3. Run pipeline: powershell -ExecutionPolicy Bypass -File .\scripts\run_fr_2016_joint_only.ps1" -ForegroundColor White
Write-Host ""
