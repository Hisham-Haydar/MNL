# =====================================================================
# RURO POST-ESTIMATION ANALYSIS
# =====================================================================
# This script runs comprehensive post-estimation analysis on RURO results
# 
# Features:
#   - Standard errors (Hessian-based)
#   - Model fit statistics (AIC, BIC, pseudo R²)
#   - Marginal utilities (MUC, MUL, MRS)
#   - Elasticities
#   - Plots (MUC/MUL curves, correlation matrices, parameter significance)
#   - HTML report
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\run_post_estimation.ps1
# =====================================================================

# Configuration
$YEAR = 2016
$PROJ_ROOT = "U:\Desktop\Nizam_Hisham\MNL"
$MNL_FILE = "U:\EUROMOD-STORAGE\Data\processed\fr\$YEAR\fr_${YEAR}_RURO_mnl.parquet"

# Resolve outputs root from ~/.mnl/config.yaml
$_mnlConfig = Join-Path $env:USERPROFILE ".mnl\config.yaml"
$_storageRoot = ""; $OUTPUTS_ROOT = ""
if (Test-Path $_mnlConfig) {
    Get-Content $_mnlConfig | ForEach-Object {
        if ($_ -match '^\s*storage_root\s*:\s*(.+)$') { $_storageRoot = $Matches[1].Trim().Replace('/', '\') }
        if ($_ -match '^\s*outputs_root\s*:\s*(.+)$') { $OUTPUTS_ROOT = $Matches[1].Trim().Replace('/', '\') }
    }
}
if (-not $OUTPUTS_ROOT -and $_storageRoot) { $OUTPUTS_ROOT = Join-Path $_storageRoot "outputs" }
if (-not $OUTPUTS_ROOT) { Write-Error "Cannot resolve outputs_root. Set outputs_root or storage_root in $_mnlConfig"; exit 1 }

$RESULTS_DIR = "$OUTPUTS_ROOT\estimates\fr\$YEAR"
$OUTPUT_DIR = "$OUTPUTS_ROOT\post_estimation\fr\$YEAR"

# Python executable (use venv)
$PYTHON = "python"

# Thread settings
$env:OMP_NUM_THREADS = "32"
$env:MKL_NUM_THREADS = "32"
$env:NUMEXPR_NUM_THREADS = "32"
$env:OPENBLAS_NUM_THREADS = "32"
$env:NUMBA_NUM_THREADS = "32"
$env:PYTHONUNBUFFERED = "1"

# Create output directory
New-Item -ItemType Directory -Force -Path $OUTPUT_DIR | Out-Null

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "RURO POST-ESTIMATION ANALYSIS - FRANCE $YEAR" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Check if estimation results exist
$results = @(
    @{Name="Single Males"; File="$RESULTS_DIR\fr_${YEAR}_single_males.json"},
    @{Name="Single Females"; File="$RESULTS_DIR\fr_${YEAR}_single_females.json"},
    @{Name="Couples"; File="$RESULTS_DIR\fr_${YEAR}_couples.json"},
    @{Name="Joint"; File="$RESULTS_DIR\fr_${YEAR}_joint.json"}
)

Write-Host "Checking estimation results..." -ForegroundColor Yellow
foreach ($result in $results) {
    if (Test-Path $result.File) {
        Write-Host "  OK $($result.Name): Found" -ForegroundColor Green
    } else {
        Write-Host "  SKIP $($result.Name): Not found" -ForegroundColor Yellow
    }
}
Write-Host ""

# Function to run post-estimation
function Run-PostEstimation {
    param(
        [string]$Name,
        [string]$EstimationFile,
        [string]$Group,
        [string]$Sex = $null
    )
    
    if (-not (Test-Path $EstimationFile)) {
        Write-Host "Skipping $Name (file not found)" -ForegroundColor Yellow
        return
    }
    
    Write-Host ""
    Write-Host "--- $Name ---" -ForegroundColor Magenta
    
    $outDir = "$OUTPUT_DIR\$($Name.Replace(' ', '_').ToLower())"
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
      $cmd = "$PYTHON `"$PROJ_ROOT\scripts\RURO_post_estimation.py`" --results `"$EstimationFile`" --mnl-file `"$MNL_FILE`" --out-dir `"$outDir`" --wage-spec vw"
    
    if ($Sex) {
        $cmd += " --sex $Sex"
    }
    
    Write-Host "Command: $cmd" -ForegroundColor DarkGray
    Write-Host ""
    
    $startTime = Get-Date
    
    try {
        Invoke-Expression $cmd
        $exitCode = $LASTEXITCODE
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $exitCode = 1
    }
    
    $duration = (Get-Date) - $startTime
      if ($exitCode -eq 0) {
        Write-Host "SUCCESS: $Name" -ForegroundColor Green
        Write-Host "  Duration: $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor Green
        Write-Host "  Output: $outDir" -ForegroundColor Cyan
    } else {
        Write-Host "FAILED: $Name (exit code: $exitCode)" -ForegroundColor Red
        Write-Host "  Duration: $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor Red
    }
}

# Run post-estimation for each result
$pipelineStart = Get-Date

Run-PostEstimation -Name "Single Males" -EstimationFile "$RESULTS_DIR\fr_${YEAR}_single_males.json" -Group "1" -Sex "m"
Run-PostEstimation -Name "Single Females" -EstimationFile "$RESULTS_DIR\fr_${YEAR}_single_females.json" -Group "1" -Sex "f"
Run-PostEstimation -Name "Couples" -EstimationFile "$RESULTS_DIR\fr_${YEAR}_couples.json" -Group "10"
Run-PostEstimation -Name "Joint" -EstimationFile "$RESULTS_DIR\fr_${YEAR}_joint.json" -Group "1"

$pipelineEnd = Get-Date
$totalDuration = $pipelineEnd - $pipelineStart

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "POST-ESTIMATION COMPLETE" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "Total Duration: $($totalDuration.ToString('hh\:mm\:ss'))" -ForegroundColor Cyan
Write-Host "Output Directory: $OUTPUT_DIR" -ForegroundColor Cyan
Write-Host ""
Write-Host "Generated files for each model:" -ForegroundColor White
Write-Host "  - standard_errors.csv (SE, t-values, p-values)" -ForegroundColor White
Write-Host "  - model_fit.json (AIC, BIC, pseudo R²)" -ForegroundColor White
Write-Host "  - elasticities.csv (labor supply elasticities)" -ForegroundColor White
Write-Host "  - plots/ (MUC/MUL, correlation matrix, parameter significance)" -ForegroundColor White
Write-Host "  - report.html (comprehensive HTML report)" -ForegroundColor White
Write-Host ""
Write-Host "Done!" -ForegroundColor Green
