# ==============================================================================
# Consumption Variation Diagnostics Runner
# ==============================================================================
# Runs the available pre-estimation consumption-variation diagnostic.
#
# Usage from server:
#   cd U:\Desktop\Nizam_Hisham\MNL
#   .\scripts\enhanced\run_diagnostics.ps1
# ==============================================================================

param(
    [string]$Country = "FR",
    [int]$Year = 2016
)

# Paths
$PROJ_ROOT = "U:\Desktop\Nizam_Hisham\MNL"
$PYTHON_EXE = "$PROJ_ROOT\.venv\Scripts\python.exe"
$DIAG_SCRIPT = "$PROJ_ROOT\scripts\enhanced\diagnostic_consumption_variation.py"

$PROC_DIR = "U:\EUROMOD-STORAGE\Data\processed\fr\$Year"
$MNL_BASE = "$PROC_DIR\fr_${Year}_RURO_mnl"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Pre-Estimation Diagnostics - $Country $Year" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Processed dir:    $PROC_DIR"
Write-Host "  MNL base:         $MNL_BASE"
Write-Host ""

# Check if files exist
Write-Host "Checking input files..." -ForegroundColor Yellow
$files = @(
    "${MNL_BASE}__singles.parquet",
    "${MNL_BASE}__couples.parquet"
)

$allExist = $true
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✓ $(Split-Path -Leaf $file)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $(Split-Path -Leaf $file) NOT FOUND" -ForegroundColor Red
        $allExist = $false
    }
}

if (-not $allExist) {
    Write-Host ""
    Write-Host "ERROR: Some required files are missing. Cannot run diagnostics." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Running diagnostics (this may take a few minutes)..." -ForegroundColor Yellow
Write-Host ""

# Run diagnostic script
$args = @(
    $DIAG_SCRIPT,
    "--mnl-base", $MNL_BASE,
    "--household-type", "both"
)

$process = Start-Process -FilePath $PYTHON_EXE -ArgumentList $args -NoNewWindow -Wait -PassThru

Write-Host ""
if ($process.ExitCode -eq 0) {
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host "Diagnostics completed successfully!" -ForegroundColor Green
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Review the diagnostic output above"
    Write-Host "  2. Check for any warnings (⚠️) or errors (❌)"
    Write-Host "  3. If all checks pass, proceed to MNL estimation"
    Write-Host ""
} else {
    Write-Host "================================================================================" -ForegroundColor Red
    Write-Host "Diagnostics failed with exit code: $($process.ExitCode)" -ForegroundColor Red
    Write-Host "================================================================================" -ForegroundColor Red
    exit $process.ExitCode
}
