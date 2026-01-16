# COMPREHENSIVE WORKSPACE CLEANUP
# Cleans root + ALL subfolders (scripts/, scripts/enhanced/, etc.)

Write-Host @"
================================================================================
COMPREHENSIVE WORKSPACE CLEANUP
================================================================================

This script will:
  1. Archive all .md files from root AND subfolders
  2. Remove test/debug .py files (test_*.py, debug_*.py, etc.)
  3. Remove unnecessary .ps1 files
  4. Clean __pycache__ folders
  5. Remove temporary/old files

WARNING: This will REMOVE test files permanently!
         .md files will be ARCHIVED (not deleted)

"@ -ForegroundColor Yellow

$confirm = Read-Host "Continue with cleanup? (y/n)"
if ($confirm -ne 'y') {
    Write-Host "Cleanup cancelled." -ForegroundColor Yellow
    exit
}

# ============================================================================
# 1. CREATE ARCHIVE DIRECTORIES
# ============================================================================
Write-Host "`n[1/6] Creating archive directories..." -ForegroundColor Cyan

$archiveDirs = @(
    "docs/archive/troubleshooting_sessions",
    "docs/archive/logs",
    "docs/archive/old_scripts",
    "docs/archive/test_files",
    "docs/archive/scripts_docs"
)

foreach ($dir in $archiveDirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Write-Host "  ✓ Created: $dir" -ForegroundColor Green
}

# ============================================================================
# 2. ARCHIVE .MD FILES FROM ROOT
# ============================================================================
Write-Host "`n[2/6] Archiving .md files from root..." -ForegroundColor Cyan

$keepInRoot = @("README.md", "CHANGELOG.md", "CONTRIBUTING.md", "LICENSE.md")

$mdPatterns = @(
    "*_FIX*.md", "*_FIXED*.md", "*_COMPLETE*.md", "*_READY*.md", 
    "*_STATUS*.md", "*_SUMMARY*.md", "*_RESULTS*.md", "*_ANALYSIS*.md",
    "*_IMPLEMENTATION*.md", "*_GUIDE*.md", "*_COMMANDS*.md",
    "*SESSION*.md", "*DEBUG*.md", "GAMSPY_*.md", "COLUMN_*.md",
    "POST_ESTIMATION_*.md", "DRAWS_*.md", "ESTIMATION_*.md",
    "COUPLES_*.md", "DEMOGRAPHICS_*.md", "R_vs_PYTHON*.md",
    "RURO_POST*.md", "INDENTATION*.md", "ALL_*.md", "*START_HERE*.md",
    "*QUICK_REF*.md", "FRESH_START*.md", "WORKSPACE_*.md"
)

$movedMD = 0
foreach ($pattern in $mdPatterns) {
    Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue | ForEach-Object {
        if ($keepInRoot -notcontains $_.Name) {
            Move-Item -Path $_.FullName -Destination "docs/archive/troubleshooting_sessions/" -Force
            Write-Host "  MOVED: $($_.Name)" -ForegroundColor Yellow
            $movedMD++
        }
    }
}

Write-Host "  ✓ Moved $movedMD .md files from root" -ForegroundColor Green

# ============================================================================
# 3. ARCHIVE .MD FILES FROM SUBFOLDERS
# ============================================================================
Write-Host "`n[3/6] Archiving .md files from subfolders..." -ForegroundColor Cyan

$scriptsDirs = @("scripts", "scripts/enhanced", "scripts/R")
$movedSubMD = 0

foreach ($dir in $scriptsDirs) {
    if (Test-Path $dir) {
        Get-ChildItem -Path $dir -Filter "*.md" -File -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
            # Keep README.md in each folder
            if ($_.Name -ne "README.md") {
                $destination = "docs/archive/scripts_docs/$($_.Name)"
                Move-Item -Path $_.FullName -Destination $destination -Force
                Write-Host "  MOVED: $($_.DirectoryName)\$($_.Name)" -ForegroundColor Yellow
                $movedSubMD++
            } else {
                Write-Host "  KEEP: $($_.DirectoryName)\$($_.Name)" -ForegroundColor Green
            }
        }
    }
}

Write-Host "  ✓ Moved $movedSubMD .md files from subfolders" -ForegroundColor Green

# ============================================================================
# 4. REMOVE TEST/DEBUG PYTHON FILES
# ============================================================================
Write-Host "`n[4/6] Removing test/debug Python files..." -ForegroundColor Cyan

$testPatterns = @(
    "test_*.py",
    "debug_*.py",
    "diagnose_*.py",
    "analyze_*.py",
    "fix_*.py",
    "compute_*.py",
    "run_gamspy.py",
    "CLEAN_*.py",
    "verify_*.py",
    "check_*.py",
    "*_test.py",
    "*_debug.py"
)

$keepPyFiles = @(
    "test_4group_likelihood.py",  # Might be essential
    "test_joint_likelihood.py"     # Might be essential
)

$removedPy = 0

# Root folder
foreach ($pattern in $testPatterns) {
    Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue | ForEach-Object {
        if ($keepPyFiles -notcontains $_.Name) {
            Remove-Item -Path $_.FullName -Force
            Write-Host "  REMOVED: $($_.Name)" -ForegroundColor Red
            $removedPy++
        } else {
            Write-Host "  KEEP: $($_.Name)" -ForegroundColor Green
        }
    }
}

# Scripts folders
foreach ($dir in $scriptsDirs) {
    if (Test-Path $dir) {
        foreach ($pattern in $testPatterns) {
            Get-ChildItem -Path $dir -Filter $pattern -File -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
                Remove-Item -Path $_.FullName -Force
                Write-Host "  REMOVED: $($_.DirectoryName)\$($_.Name)" -ForegroundColor Red
                $removedPy++
            }
        }
    }
}

Write-Host "  ✓ Removed $removedPy test/debug Python files" -ForegroundColor Green

# ============================================================================
# 5. REMOVE UNNECESSARY POWERSHELL FILES
# ============================================================================
Write-Host "`n[5/6] Removing unnecessary PowerShell files..." -ForegroundColor Cyan

$keepPS1 = @(
    "RUN_PIPELINE_WITH_REDUCED_FILES.ps1",
    "cleanup_workspace.ps1",
    "cleanup_repo.ps1"
)

$oldPS1 = @(
    "FRESH_START_MENU.ps1",
    "RUN_COLUMN_REDUCTION.ps1",
    "run_estimation_detailed_log.ps1",
    "run_estimation_verbose.ps1",
    "run_gamspy_joint.ps1",
    "test_column_reduction_dry_run.ps1",
    "run_gamspy.ps1"
)

$removedPS1 = 0

# Root folder
foreach ($script in $oldPS1) {
    if (Test-Path $script) {
        Remove-Item -Path $script -Force
        Write-Host "  REMOVED: $script" -ForegroundColor Red
        $removedPS1++
    }
}

# Scripts folder
Get-ChildItem -Path "scripts" -Filter "*.ps1" -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    $keep = $false
    foreach ($keepFile in $keepPS1) {
        if ($_.Name -eq $keepFile) {
            $keep = $true
            break
        }
    }
    
    if (-not $keep) {
        Remove-Item -Path $_.FullName -Force
        Write-Host "  REMOVED: $($_.DirectoryName)\$($_.Name)" -ForegroundColor Red
        $removedPS1++
    }
}

Write-Host "  ✓ Removed $removedPS1 unnecessary PowerShell files" -ForegroundColor Green

# ============================================================================
# 6. CLEAN TEMPORARY FILES & __pycache__
# ============================================================================
Write-Host "`n[6/6] Cleaning temporary files and __pycache__..." -ForegroundColor Cyan

$removedTemp = 0

# Remove __pycache__ directories
Get-ChildItem -Path . -Directory -Filter "__pycache__" -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -Path $_.FullName -Recurse -Force
    Write-Host "  REMOVED: $($_.FullName)" -ForegroundColor Red
    $removedTemp++
}

# Remove .pyc files
Get-ChildItem -Path . -Filter "*.pyc" -File -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -Path $_.FullName -Force
    $removedTemp++
}

# Remove log files from root
Get-ChildItem -Path . -Filter "*.log" -File -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "docs/archive/logs/" -Force
    Write-Host "  MOVED: $($_.Name)" -ForegroundColor Yellow
    $removedTemp++
}

# Remove text output files
$txtPatterns = @("*_output.txt", "*_columns.txt", "*_analysis.txt", "dry_run*.txt")
foreach ($pattern in $txtPatterns) {
    Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue | ForEach-Object {
        Move-Item -Path $_.FullName -Destination "docs/archive/logs/" -Force
        Write-Host "  MOVED: $($_.Name)" -ForegroundColor Yellow
        $removedTemp++
    }
}

Write-Host "  ✓ Cleaned $removedTemp temporary files" -ForegroundColor Green

# ============================================================================
# SUMMARY
# ============================================================================
Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Cyan

Write-Host "`nSummary:"
Write-Host "  ✓ .md files moved to archive (root): $movedMD" -ForegroundColor Yellow
Write-Host "  ✓ .md files moved to archive (subfolders): $movedSubMD" -ForegroundColor Yellow
Write-Host "  ✓ Test/debug .py files removed: $removedPy" -ForegroundColor Red
Write-Host "  ✓ Unnecessary .ps1 files removed: $removedPS1" -ForegroundColor Red
Write-Host "  ✓ Temporary files cleaned: $removedTemp" -ForegroundColor Yellow

Write-Host "`nArchive locations:"
Write-Host "  📁 Troubleshooting docs: docs/archive/troubleshooting_sessions/" -ForegroundColor Cyan
Write-Host "  📁 Scripts docs: docs/archive/scripts_docs/" -ForegroundColor Cyan
Write-Host "  📁 Logs: docs/archive/logs/" -ForegroundColor Cyan
Write-Host "  📁 Test files: docs/archive/test_files/" -ForegroundColor Cyan

Write-Host "`n✅ Workspace is now clean!" -ForegroundColor Green

Write-Host "`nRemaining files in root:" -ForegroundColor Cyan
Write-Host "  .md files:" -ForegroundColor Yellow
Get-ChildItem -Path . -Filter "*.md" -File | ForEach-Object { Write-Host "    - $($_.Name)" }
Write-Host "  .ps1 files:" -ForegroundColor Yellow
Get-ChildItem -Path . -Filter "*.ps1" -File | ForEach-Object { Write-Host "    - $($_.Name)" }
Write-Host "  .py files:" -ForegroundColor Yellow
Get-ChildItem -Path . -Filter "*.py" -File | ForEach-Object { Write-Host "    - $($_.Name)" }

Write-Host "`nRemaining .md files in scripts/:" -ForegroundColor Cyan
Get-ChildItem -Path "scripts" -Filter "*.md" -File -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "    - $($_.DirectoryName)\$($_.Name)"
}

Write-Host "`n"
