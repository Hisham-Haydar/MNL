# FINAL WORKSPACE CLEANUP - Simple and Robust
# Archives .md files and removes test files

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "WORKSPACE CLEANUP" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will:" -ForegroundColor Yellow
Write-Host "  1. Archive all .md files (except README.md)" -ForegroundColor White
Write-Host "  2. Remove test/debug Python files" -ForegroundColor White
Write-Host "  3. Remove old PowerShell scripts" -ForegroundColor White
Write-Host "  4. Clean __pycache__ folders (project directories only, excluding .venv)" -ForegroundColor White
Write-Host ""
Write-Host "Starting cleanup in 2 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# Create archive directories
Write-Host ""
Write-Host "[1/5] Creating archive directories..." -ForegroundColor Cyan
$archiveDirs = @(
    "docs\archive\troubleshooting_sessions",
    "docs\archive\scripts_docs",
    "docs\archive\logs"
)

foreach ($dir in $archiveDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    }
}

# Archive root .md files
Write-Host ""
Write-Host "[2/5] Archiving root .md files..." -ForegroundColor Cyan
$movedMD = 0
$keepInRoot = @("README.md", "CHANGELOG.md", "CONTRIBUTING.md", "LICENSE.md")

Get-ChildItem -Path . -Filter "*.md" -File | ForEach-Object {
    if ($keepInRoot -notcontains $_.Name) {
        $dest = "docs\archive\troubleshooting_sessions\$($_.Name)"
        Move-Item -Path $_.FullName -Destination $dest -Force
        Write-Host "  Moved: $($_.Name)" -ForegroundColor Yellow
        $movedMD++
    } else {
        Write-Host "  Kept: $($_.Name)" -ForegroundColor Green
    }
}
Write-Host "  Total: $movedMD files moved" -ForegroundColor Green

# Archive scripts/ .md files
Write-Host ""
Write-Host "[3/5] Archiving scripts/ .md files..." -ForegroundColor Cyan
$movedScriptsMD = 0

if (Test-Path "scripts") {
    Get-ChildItem -Path "scripts" -Filter "*.md" -File -Recurse | ForEach-Object {
        if ($_.Name -ne "README.md") {
            $dest = "docs\archive\scripts_docs\$($_.Name)"
            Move-Item -Path $_.FullName -Destination $dest -Force
            Write-Host "  Moved: $($_.FullName)" -ForegroundColor Yellow
            $movedScriptsMD++
        }
    }
}
Write-Host "  Total: $movedScriptsMD files moved" -ForegroundColor Green

# Remove test Python files
Write-Host ""
Write-Host "[4/5] Removing test Python files..." -ForegroundColor Cyan
$removedPy = 0

$testPatterns = @(
    "test_*.py",
    "debug_*.py",
    "diagnose_*.py",
    "analyze_*.py",
    "fix_*.py",
    "verify_*.py",
    "check_*.py"
)

foreach ($pattern in $testPatterns) {
    Get-ChildItem -Path . -Filter $pattern -File | ForEach-Object {
        Remove-Item -Path $_.FullName -Force
        Write-Host "  Removed: $($_.Name)" -ForegroundColor Red
        $removedPy++
    }
    
    if (Test-Path "scripts") {
        Get-ChildItem -Path "scripts" -Filter $pattern -File -Recurse | ForEach-Object {
            Remove-Item -Path $_.FullName -Force
            Write-Host "  Removed: $($_.FullName)" -ForegroundColor Red
            $removedPy++
        }
    }
}
Write-Host "  Total: $removedPy files removed" -ForegroundColor Green

# Clean temporary files
Write-Host ""
Write-Host "[5/5] Cleaning temporary files..." -ForegroundColor Cyan
$removedTemp = 0

# Directories to exclude from __pycache__ cleanup (virtual environments)
$excludeDirs = @(".venv", "venv", ".env", "env", "node_modules")

# Remove __pycache__ (but NOT from virtual environments)
Get-ChildItem -Path . -Directory -Filter "__pycache__" -Recurse | ForEach-Object {
    $shouldRemove = $true
    $path = $_.FullName
    
    # Check if path contains any excluded directory
    foreach ($excludeDir in $excludeDirs) {
        if ($path -like "*\$excludeDir\*") {
            $shouldRemove = $false
            Write-Host "  Skipped (venv): $path" -ForegroundColor DarkGray
            break
        }
    }
    
    if ($shouldRemove) {
        Remove-Item -Path $_.FullName -Recurse -Force
        Write-Host "  Removed: $path" -ForegroundColor Red
        $removedTemp++
    }
}

# Remove .pyc (but NOT from virtual environments)
Get-ChildItem -Path . -Filter "*.pyc" -File -Recurse | ForEach-Object {
    $shouldRemove = $true
    $path = $_.FullName
    
    # Check if path contains any excluded directory
    foreach ($excludeDir in $excludeDirs) {
        if ($path -like "*\$excludeDir\*") {
            $shouldRemove = $false
            break
        }
    }
    
    if ($shouldRemove) {
        Remove-Item -Path $_.FullName -Force
        $removedTemp++
    }
}

# Move logs
Get-ChildItem -Path . -Filter "*.log" -File | ForEach-Object {
    $dest = "docs\archive\logs\$($_.Name)"
    Move-Item -Path $_.FullName -Destination $dest -Force
    Write-Host "  Moved: $($_.Name)" -ForegroundColor Yellow
    $removedTemp++
}

Write-Host "  Total: $removedTemp items cleaned" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  Root .md files moved: $movedMD" -ForegroundColor White
Write-Host "  Scripts .md files moved: $movedScriptsMD" -ForegroundColor White
Write-Host "  Test Python files removed: $removedPy" -ForegroundColor White
Write-Host "  Temporary files cleaned: $removedTemp" -ForegroundColor White
Write-Host ""
Write-Host "Archive location:" -ForegroundColor Yellow
Write-Host "  docs\archive\" -ForegroundColor Cyan
Write-Host ""
Write-Host "Remaining root files:" -ForegroundColor Yellow

Write-Host "  .md files:" -ForegroundColor Cyan
Get-ChildItem -Path . -Filter "*.md" -File | ForEach-Object { 
    Write-Host "    - $($_.Name)" -ForegroundColor White
}

Write-Host "  .ps1 files:" -ForegroundColor Cyan
Get-ChildItem -Path . -Filter "*.ps1" -File | ForEach-Object { 
    Write-Host "    - $($_.Name)" -ForegroundColor White
}

Write-Host "  .py files:" -ForegroundColor Cyan
Get-ChildItem -Path . -Filter "*.py" -File | ForEach-Object { 
    Write-Host "    - $($_.Name)" -ForegroundColor White
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
