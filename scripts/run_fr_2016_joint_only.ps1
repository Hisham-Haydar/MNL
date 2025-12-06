# =====================================================================
# RURO FRANCE 2016 – JOINT ESTIMATION ONLY
# =====================================================================
# This script runs ONLY the joint estimation (Step 7d) with full
# post-estimation diagnostics.
#
# Prerequisites:
#   - Steps 1-6 must have been completed (MNL dataset exists)
#   - MNL file: U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl.parquet
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\run_fr_2016_joint_only.ps1
#
# Author: Generated for France 2016 joint estimation
# Date: 2025-12-06
# =====================================================================

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------
$YEAR = 2016
$COUNTRY = "FR"
$WAGE_SPEC = "vw"    # "fw" = fixed wages, "vw" = variable wages
$MAX_ITER = 500      # Maximum optimizer iterations

# Paths
$PROJ_ROOT = "U:\Desktop\Nizam_Hisham\MNL"
$SCRIPTS = "$PROJ_ROOT\scripts"
$DATA_ROOT = "U:\EUROMOD-STORAGE\Data"
$PROC = "$DATA_ROOT\processed\fr\$YEAR"
$MNL_FILE = "$PROC\fr_${YEAR}_RURO_mnl.parquet"

# Results output directory
$RESULTS_DIR = "$PROJ_ROOT\outputs\estimates\fr\$YEAR"
$POST_EST_DIR = "$PROJ_ROOT\outputs\post_estimation\fr\$YEAR"

# Initial parameter file (optional - set to $null to use defaults)
$INIT_PARAMS_JOINT = $null

# Log file
$LOG_DIR = "$PROJ_ROOT\outputs\logs"
$TIMESTAMP = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LOG_FILE = "$LOG_DIR\fr_${YEAR}_joint_only_$TIMESTAMP.md"

# ---------------------------------------------------------------------
# PERFORMANCE OPTIMIZATIONS
# ---------------------------------------------------------------------
# Detect available CPU cores
$CPU_CORES = (Get-WmiObject -Class Win32_Processor).NumberOfLogicalProcessors
Write-Host "Detected CPU cores: $CPU_CORES" -ForegroundColor Cyan

# Set thread environment variables for optimal performance
$env:OMP_NUM_THREADS = "$CPU_CORES"
$env:MKL_NUM_THREADS = "$CPU_CORES"
$env:NUMEXPR_NUM_THREADS = "$CPU_CORES"
$env:OPENBLAS_NUM_THREADS = "$CPU_CORES"
$env:NUMBA_NUM_THREADS = "$CPU_CORES"

# Set process priority to high
$process = Get-Process -Id $PID
$process.PriorityClass = "High"

# Disable Python output buffering
$env:PYTHONUNBUFFERED = "1"

# ---------------------------------------------------------------------
# LOGGING SETUP
# ---------------------------------------------------------------------
New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $RESULTS_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $POST_EST_DIR | Out-Null

$logHeader = @"
# RURO France $YEAR - Joint Estimation Only

**Started:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Configuration:**
- Year: $YEAR
- Wage Spec: $WAGE_SPEC
- Max Iterations: $MAX_ITER
- CPU Cores: $CPU_CORES

---

"@
$logHeader | Out-File -FilePath $LOG_FILE -Encoding utf8

# ---------------------------------------------------------------------
# PRE-FLIGHT CHECKS
# ---------------------------------------------------------------------
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "RURO FRANCE $YEAR - JOINT ESTIMATION ONLY" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Configuration:" -ForegroundColor White
Write-Host "  Year:           $YEAR"
Write-Host "  Wage Spec:      $WAGE_SPEC"
Write-Host "  Max Iterations: $MAX_ITER"
Write-Host "  CPU Cores:      $CPU_CORES"
Write-Host ""

# Check MNL file exists
if (-not (Test-Path $MNL_FILE)) {
    Write-Host "ERROR: MNL dataset not found: $MNL_FILE" -ForegroundColor Red
    Write-Host "Please run steps 1-6 of the pipeline first." -ForegroundColor Red
    exit 1
}
Write-Host "  OK: MNL dataset found" -ForegroundColor Green
Write-Host ""

# Record start time
$pipelineStart = Get-Date

# =====================================================================
# JOINT ESTIMATION
# =====================================================================
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Magenta
Write-Host "JOINT ESTIMATION (all groups with shared opportunity parameters)" -ForegroundColor Magenta
Write-Host "======================================================================" -ForegroundColor Magenta
Write-Host ""

$cmd = "python `"$SCRIPTS\RURO_estimate_FR.py`" " +
       "--mnl-file `"$MNL_FILE`" " +
       "--joint " +
       "--wage-spec $WAGE_SPEC " +
       "--optimizer L-BFGS-B " +
       "--maxiter $MAX_ITER " +
       "--use-numba " +
       "--n-jobs $CPU_CORES " +
       "--out-file `"$RESULTS_DIR\fr_${YEAR}_joint.json`""

if ($INIT_PARAMS_JOINT -and (Test-Path $INIT_PARAMS_JOINT)) {
    $cmd += " --init-params `"$INIT_PARAMS_JOINT`""
    Write-Host "  Using initial params: $INIT_PARAMS_JOINT" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "Command:" -ForegroundColor Yellow
Write-Host $cmd -ForegroundColor DarkGray
Write-Host ""

"## Joint Estimation" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
"``````bash" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
$cmd | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
"``````" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
"" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8

$startTime = Get-Date
$output = Invoke-Expression $cmd 2>&1
$exitCode = $LASTEXITCODE
$duration = (Get-Date) - $startTime

# Display output
if ($output) {
    $outputStr = $output | Out-String
    Write-Host $outputStr
    "``````" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    $outputStr | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "``````" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
}

Write-Host ""
if ($exitCode -ne 0) {
    Write-Host "FAILED: Joint estimation (exit code: $exitCode)" -ForegroundColor Red
    Write-Host "Duration: $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor Red
    "**FAILED:** Joint estimation (exit code: $exitCode)" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    exit 1
}

Write-Host "SUCCESS: Joint estimation" -ForegroundColor Green
Write-Host "Duration: $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor Green
"**SUCCESS:** Joint estimation" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
"Duration: ``$($duration.ToString('hh\:mm\:ss'))``" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
"" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8

# =====================================================================
# POST-ESTIMATION ANALYSIS
# =====================================================================
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Magenta
Write-Host "POST-ESTIMATION ANALYSIS" -ForegroundColor Magenta
Write-Host "======================================================================" -ForegroundColor Magenta
Write-Host ""

$EST_FILE = "$RESULTS_DIR\fr_${YEAR}_joint.json"
if (-not (Test-Path $EST_FILE)) {
    Write-Host "WARNING: Estimation file not found, skipping post-estimation" -ForegroundColor Yellow
} else {
    $outDir = "$POST_EST_DIR\joint"
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    
    # NOTE: Post-estimation for joint model runs in CLI mode
    # This generates:
    # - Parameter estimates table
    # - Model fit statistics (AIC, BIC, pseudo R²)
    # - Marginal utility plots (MUC, MUL, MRS)
    # - Parameter significance plot
    # - HTML report with all diagnostics
    #
    # Full standard errors require running from within estimation script
    # because gradient function is needed for Hessian computation
    
    $cmd = "python `"$SCRIPTS\RURO_post_estimation.py`" " +
           "--results `"$EST_FILE`" " +
           "--mnl-file `"$MNL_FILE`" " +
           "--out-dir `"$outDir`" " +
           "--wage-spec $WAGE_SPEC " +
           "--sex pooled"
    
    Write-Host "Command:" -ForegroundColor Yellow
    Write-Host $cmd -ForegroundColor DarkGray
    Write-Host ""
    
    "## Post-Estimation Analysis" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "``````bash" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    $cmd | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "``````" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    
    $startTime = Get-Date
    $output = Invoke-Expression $cmd 2>&1
    $exitCode = $LASTEXITCODE
    $duration = (Get-Date) - $startTime
    
    if ($output) {
        $outputStr = $output | Out-String
        Write-Host $outputStr
        "``````" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        $outputStr | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        "``````" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    }
    
    Write-Host ""
    if ($exitCode -ne 0) {
        Write-Host "WARNING: Post-estimation had errors (exit code: $exitCode)" -ForegroundColor Yellow
    } else {
        Write-Host "SUCCESS: Post-estimation analysis" -ForegroundColor Green
    }
    Write-Host "Duration: $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor Green
    "Duration: ``$($duration.ToString('hh\:mm\:ss'))``" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
}

# =====================================================================
# SUMMARY
# =====================================================================
$pipelineEnd = Get-Date
$totalDuration = $pipelineEnd - $pipelineStart

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "COMPLETE" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output Files:" -ForegroundColor White
Write-Host "  Estimation:     $EST_FILE"
Write-Host "  Post-Est Dir:   $outDir"
Write-Host "  Log File:       $LOG_FILE"
Write-Host ""
Write-Host "Total Duration:   $($totalDuration.ToString('hh\:mm\:ss'))" -ForegroundColor Cyan
Write-Host ""
Write-Host "Done!" -ForegroundColor Green

# Final log entry
@"

---

## Summary

**Completed:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Total Duration:** $($totalDuration.ToString('hh\:mm\:ss'))

### Output Files
- Estimation: ``$EST_FILE``
- Post-Estimation: ``$outDir``
- HTML Report: ``$outDir\${WAGE_SPEC}_pooled_post_estimation_report.html``

### Parameters Estimated (Total: 100 for vw, 68 for fw)

#### Group-Specific Preferences (50 parameters)
**Single Males (12):** beta_l0, beta_l_log_age, beta_l_log_age2, beta_l_ch4_6, beta_l_ch7_9, beta_l_educL, beta_l_educH, beta_l_reg2, beta_c, theta_l, theta_c, beta_l_ch0_3

**Single Females (13):** beta_l0, beta_l_log_age, beta_l_log_age2, beta_l_ch4_6, beta_l_ch7_9, beta_l_educL, beta_l_educH, beta_l_reg2, beta_c, theta_l, theta_c, beta_l_ch0_3, beta_l_reg3

**Couples (25):**
- Male leisure (10): beta_l0_m, beta_l_log_age_m, beta_l_log_age2_m, beta_l_ch0_3_m, beta_l_ch4_6_m, beta_l_ch7_9_m, beta_l_reg2_m, beta_l_reg3_m, beta_l_educL_m, beta_l_educH_m
- Female leisure (10): beta_l0_f, beta_l_log_age_f, beta_l_log_age2_f, beta_l_ch0_3_f, beta_l_ch4_6_f, beta_l_ch7_9_f, beta_l_reg2_f, beta_l_reg3_f, beta_l_educL_f, beta_l_educH_f
- Shared (5): theta_l_m, theta_l_f, theta_c, beta_c, beta_interaction

#### Gender-Shared Opportunity Parameters

**Hours Opportunity - Males (9):** beta_work, beta_pt1, beta_pt2, beta_ft, beta_gsur, beta_work_educL, beta_work_educH, beta_work_reg2, beta_work_reg3

**Hours Opportunity - Females (9):** beta_work, beta_pt1, beta_pt2, beta_ft, beta_gsur, beta_work_educL, beta_work_educH, beta_work_reg2, beta_work_reg3

**Wage Opportunity - Males (16, vw only):** beta0, beta_educL, beta_educH, beta_pexp, beta_pexp2, beta_reg2-9, beta_yd1, beta_yd2, sigma

**Wage Opportunity - Females (16, vw only):** beta0, beta_educL, beta_educH, beta_pexp, beta_pexp2, beta_reg2-9, beta_yd1, beta_yd2, sigma

### Post-Estimation Diagnostics Available
- ✅ Parameter estimates with names
- ✅ Log-likelihood and model fit (AIC, BIC, pseudo R²)
- ✅ Marginal utility plots (MUC, MUL)
- ✅ Marginal rate of substitution (MRS)
- ✅ Combined visualization plots
- ✅ Parameter significance visualization
- ✅ HTML report with all results
- ⚠️  Standard errors: Limited in CLI mode (requires full post-estimation from estimation script)

### Bounds Removed
The Box-Cox parameter bounds have been kept (0.01, 2.0) for numerical stability.
Sigma bounds have been kept (0.01, 2.0) for positive variance.
All other parameters are unbounded.

"@ | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
