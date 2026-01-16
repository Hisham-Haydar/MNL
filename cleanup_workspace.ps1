# Cleanup Script - Organize Documentation
# Moves all session/debug .md files to a docs/archive folder

Write-Host @"
================================================================================
WORKSPACE CLEANUP - DOCUMENTATION ORGANIZER
================================================================================

This script will:
  1. Find all troubleshooting/session .md files
  2. Move them to docs/archive/ folder
  3. Keep only essential documentation in root
  4. Clean up scripts/ folder

"@ -ForegroundColor Cyan

$confirm = Read-Host "Continue with cleanup? (y/n)"
if ($confirm -ne 'y') {
    Write-Host "Cleanup cancelled." -ForegroundColor Yellow
    exit
}

# Create archive directory
$archiveDir = "docs/archive/troubleshooting_sessions"
New-Item -ItemType Directory -Force -Path $archiveDir | Out-Null
Write-Host "✓ Created archive directory: $archiveDir" -ForegroundColor Green

# Define patterns for files to archive (troubleshooting/session files)
$archivePatterns = @(
    "*_FIX*.md",
    "*_FIXED*.md",
    "*_COMPLETE*.md",
    "*_READY*.md",
    "*_STATUS*.md",
    "*_SUMMARY*.md",
    "*_RESULTS*.md",
    "*_ANALYSIS*.md",
    "*_IMPLEMENTATION*.md",
    "*_GUIDE*.md",
    "*_COMMANDS*.md",
    "*SESSION*.md",
    "*DEBUG*.md",
    "*FRESH_START*.md",
    "*QUICK_REF*.md",
    "*START_HERE*.md",
    "GAMSPY_*.md",
    "COLUMN_*.md",
    "POST_ESTIMATION_*.md",
    "DRAWS_*.md",
    "ESTIMATION_*.md",
    "COUPLES_*.md",
    "DEMOGRAPHICS_*.md",
    "R_vs_PYTHON*.md",
    "RURO_POST*.md",
    "INDENTATION*.md",
    "ALL_*.md"
)

# Files to KEEP in root (essential docs only)
$keepInRoot = @(
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE.md"
)

Write-Host "`nScanning for files to archive..." -ForegroundColor Cyan

$movedCount = 0
$keptCount = 0

foreach ($pattern in $archivePatterns) {
    $files = Get-ChildItem -Path . -Filter $pattern -File
    
    foreach ($file in $files) {
        # Skip if in keep list
        if ($keepInRoot -contains $file.Name) {
            Write-Host "  KEEP: $($file.Name)" -ForegroundColor Green
            $keptCount++
            continue
        }
        
        # Move to archive
        $destination = Join-Path $archiveDir $file.Name
        Move-Item -Path $file.FullName -Destination $destination -Force
        Write-Host "  MOVED: $($file.Name)" -ForegroundColor Yellow
        $movedCount++
    }
}

# Also clean up log files
Write-Host "`nCleaning up log files..." -ForegroundColor Cyan
$logArchive = "docs/archive/logs"
New-Item -ItemType Directory -Force -Path $logArchive | Out-Null

$logPatterns = @("*.log", "*_debug.py", "diagnose_*.py", "debug_*.py", "analyze_*.py")
foreach ($pattern in $logPatterns) {
    $logs = Get-ChildItem -Path . -Filter $pattern -File
    foreach ($log in $logs) {
        $destination = Join-Path $logArchive $log.Name
        Move-Item -Path $log.FullName -Destination $destination -Force
        Write-Host "  MOVED: $($log.Name)" -ForegroundColor Yellow
        $movedCount++
    }
}

# Clean up text output files
Write-Host "`nCleaning up text output files..." -ForegroundColor Cyan
$txtPatterns = @("*_output.txt", "*_columns.txt", "*_analysis.txt")
foreach ($pattern in $txtPatterns) {
    $txts = Get-ChildItem -Path . -Filter $pattern -File
    foreach ($txt in $txts) {
        $destination = Join-Path $logArchive $txt.Name
        Move-Item -Path $txt.FullName -Destination $destination -Force
        Write-Host "  MOVED: $($txt.Name)" -ForegroundColor Yellow
        $movedCount++
    }
}

# Clean up old PowerShell scripts (keep main ones)
Write-Host "`nCleaning up old PowerShell scripts..." -ForegroundColor Cyan
$psArchive = "docs/archive/old_scripts"
New-Item -ItemType Directory -Force -Path $psArchive | Out-Null

$keepPS1 = @(
    "RUN_PIPELINE_WITH_REDUCED_FILES.ps1",
    "cleanup_repo.ps1"
)

$oldPS1 = @(
    "FRESH_START_MENU.ps1",
    "RUN_COLUMN_REDUCTION.ps1",
    "run_estimation_detailed_log.ps1",
    "run_estimation_verbose.ps1",
    "run_gamspy_joint.ps1"
)

foreach ($script in $oldPS1) {
    if (Test-Path $script) {
        $destination = Join-Path $psArchive $script
        Move-Item -Path $script -Destination $destination -Force
        Write-Host "  MOVED: $script" -ForegroundColor Yellow
        $movedCount++
    }
}

# Summary
Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "`nSummary:"
Write-Host "  Files moved to archive: $movedCount" -ForegroundColor Yellow
Write-Host "  Files kept in root: $keptCount" -ForegroundColor Green
Write-Host "`nArchive locations:"
Write-Host "  Documentation: $archiveDir" -ForegroundColor Cyan
Write-Host "  Logs: $logArchive" -ForegroundColor Cyan
Write-Host "  Scripts: $psArchive" -ForegroundColor Cyan

Write-Host "`n✓ Workspace is now clean!" -ForegroundColor Green
Write-Host "`nEssential files in root:" -ForegroundColor Cyan
Get-ChildItem -Path . -Filter "*.md" -File | ForEach-Object { Write-Host "  - $($_.Name)" }
Get-ChildItem -Path . -Filter "*.ps1" -File | ForEach-Object { Write-Host "  - $($_.Name)" }

Write-Host "`n"
