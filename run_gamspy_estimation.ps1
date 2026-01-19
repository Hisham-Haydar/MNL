#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run GAMSPy joint estimation for Phase 5 testing

.DESCRIPTION
    This script runs GAMSPy estimation with CONOPT solver and saves results
    to outputs/estimates/fr/2016_gamspy/ for comparison with SciPy baseline.

.NOTES
    Author: Phase 5 Testing
    Created: 2026-01-17
#>

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\.venv\Scripts\Activate.ps1"

# Set paths
$MNL_BASE = "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl"
$OUTPUT_DIR = "outputs/estimates/fr/2016_gamspy"
$SPEC_CONFIG = "scripts/enhanced/estimation_spec.yaml"

# Create output directory
New-Item -ItemType Directory -Force -Path $OUTPUT_DIR | Out-Null

Write-Host "`n================================================================================" -ForegroundColor Green
Write-Host "PHASE 5 TEST: GAMSPy Estimation" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "Data: $MNL_BASE"
Write-Host "Output: $OUTPUT_DIR"
Write-Host "Specification: $SPEC_CONFIG"
Write-Host "Solver: CONOPT (GAMSPy)"
Write-Host "Expected runtime: 5-15 minutes"
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""

# Run GAMSPy estimation
Write-Host "Starting GAMSPy estimation..." -ForegroundColor Yellow

$ErrorActionPreference = "Continue"
$StartTime = Get-Date

python scripts/enhanced/enh_RURO_estimate_FR.py `
    --mnl-base $MNL_BASE `
    --output-dir $OUTPUT_DIR `
    --group joint `
    --solver gamspy-conopt `
    --spec-config $SPEC_CONFIG `
    --verbose 2>&1 | Tee-Object -FilePath "$OUTPUT_DIR/gamspy_estimation.log"

$ExitCode = $LASTEXITCODE
$EndTime = Get-Date
$Duration = $EndTime - $StartTime

Write-Host "`n================================================================================" -ForegroundColor Green
if ($ExitCode -eq 0) {
    Write-Host "GAMSPy Estimation COMPLETED" -ForegroundColor Green
} else {
    Write-Host "GAMSPy Estimation FAILED (Exit code: $ExitCode)" -ForegroundColor Red
}
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "Duration: $($Duration.ToString('hh\:mm\:ss'))"
Write-Host "Log saved to: $OUTPUT_DIR/gamspy_estimation.log"
Write-Host "Results saved to: $OUTPUT_DIR/estimation_results.json"
Write-Host ""

if ($ExitCode -eq 0) {
    Write-Host "Next step: Run comparison test" -ForegroundColor Cyan
    Write-Host "  python test_gamspy_vs_scipy.py" -ForegroundColor White
} else {
    Write-Host "Check log file for errors: $OUTPUT_DIR/gamspy_estimation.log" -ForegroundColor Yellow
}

exit $ExitCode
