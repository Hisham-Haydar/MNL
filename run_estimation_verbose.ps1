# =====================================================================
# VERBOSE ESTIMATION RUNNER - Shows Real-Time Iteration Output
# =====================================================================
# This script runs estimation with FULL real-time output visible
# in the terminal, including iteration-by-iteration progress.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\run_estimation_verbose.ps1
#
# Author: RURO Estimation Team
# Date: 2026-01-09
# =====================================================================

param(
    [string]$Country = "fr",
    [string]$Year = "2016",
    [string]$Group = "joint",
    [int]$MaxIter = 10000,
    [int]$NCores = 32
)

# Configuration
$PROJ_ROOT = "U:\Desktop\Nizam_Hisham\MNL"
$PYTHON_EXE = "$PROJ_ROOT\.venv\Scripts\python.exe"
$SCRIPT_PATH = "$PROJ_ROOT\scripts\enhanced\enh_RURO_estimate_FR.py"
$SPEC_PATH = "$PROJ_ROOT\scripts\enhanced\estimation_spec.yaml"
$MNL_BASE = "U:/EUROMOD-STORAGE/Data/processed/$Country/$Year/${Country}_${Year}_RURO_mnl"
$OUTPUT_DIR = "$PROJ_ROOT\outputs\estimates\$Country\$Year"
$INIT_PARAMS = "$OUTPUT_DIR\estimation_results.json"

# Create output directory
New-Item -ItemType Directory -Force -Path $OUTPUT_DIR | Out-Null

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "VERBOSE ESTIMATION RUN - Real-Time Iteration Output" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration:" -ForegroundColor White
Write-Host "  Country:       $Country"
Write-Host "  Year:          $Year"
Write-Host "  Group:         $Group"
Write-Host "  Max Iterations: $MaxIter"
Write-Host "  CPU Cores:     $NCores"
Write-Host ""
Write-Host "Paths:" -ForegroundColor White
Write-Host "  Python:        $PYTHON_EXE"
Write-Host "  Script:        $SCRIPT_PATH"
Write-Host "  Spec:          $SPEC_PATH"
Write-Host "  MNL Base:      $MNL_BASE"
Write-Host "  Output:        $OUTPUT_DIR"
Write-Host ""

if (Test-Path $INIT_PARAMS) {
    Write-Host "Initial Parameters: $INIT_PARAMS" -ForegroundColor Cyan
} else {
    Write-Host "Initial Parameters: Using defaults (no init file found)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "Starting Estimation - Iteration Output Will Appear Below" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Build command
$cmd = @(
    "`"$PYTHON_EXE`""
    "`"$SCRIPT_PATH`""
    "--mnl-base `"$MNL_BASE`""
    "--output-dir `"$OUTPUT_DIR`""
    "--group $Group"
    "--method L-BFGS-B"
    "--maxiter $MaxIter"
    "--spec-config `"$SPEC_PATH`""
    "--n-jobs $NCores"
)

if (Test-Path $INIT_PARAMS) {
    $cmd += "--init-params `"$INIT_PARAMS`""
}

$fullCmd = $cmd -join " "

Write-Host "Command:" -ForegroundColor DarkGray
Write-Host $fullCmd -ForegroundColor DarkGray
Write-Host ""
Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host ""

# Run command with DIRECT output (no redirection)
$startTime = Get-Date

# Use Invoke-Expression for real-time output
Invoke-Expression $fullCmd

$exitCode = $LASTEXITCODE
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "ESTIMATION COMPLETED SUCCESSFULLY" -ForegroundColor Green
} else {
    Write-Host "ESTIMATION FAILED" -ForegroundColor Red
}
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Duration:  $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor White
Write-Host "Exit Code: $exitCode"
Write-Host ""
Write-Host "Results saved to: $OUTPUT_DIR" -ForegroundColor Cyan
Write-Host ""

exit $exitCode
