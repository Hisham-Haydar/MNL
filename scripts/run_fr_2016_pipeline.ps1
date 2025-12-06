# =====================================================================
# RURO FRANCE 2016 – FULL PIPELINE
# =====================================================================
# This script runs the complete RURO estimation pipeline for France 2016
# 
# Pipeline steps:
#   1. france_data_prep.py   - Prepare raw EUROMOD data
#   2. RURO_prep.py          - Build RURO-ready datasets (singles/couples)
#   3. RURO_draws.py         - Generate opportunity draws
#   4. RURO_euromod.py       - Run EUROMOD on all draws
#   5. prepare_FR_gsur.py    - Prepare GSUR data (if needed)
#   6. RURO_prep_mnl_basic.py - Build MNL estimation dataset
#   7. RURO_estimate_FR.py   - Estimate RURO model
#
# Parallelization:
#   - Steps 1-6: Use NumPy/Pandas vectorization (automatic via MKL/OpenBLAS threads)
#   - Step 7 (Estimation): Full parallelization via Numba + NumPy threading
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\run_fr_2016_pipeline.ps1
#
# Author: Generated for France 2016 pipeline
# Date: 2025-12-05
# =====================================================================

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------
$YEAR = 2016
$COUNTRY = "FR"
$SYSTEM_YEAR = 2015  # EUROMOD system year = data year - 1
$N_DRAWS = 99       # Number of counterfactual draws ()
$WAGE_SPEC = "vw"    # "fw" = fixed wages, "vw" = variable wages

# Paths
$PROJ_ROOT = "U:\Desktop\Nizam_Hisham\MNL"
$SCRIPTS = "$PROJ_ROOT\scripts"
$DATA_ROOT = "U:\EUROMOD-STORAGE\Data"
$PROC = "$DATA_ROOT\processed\fr\$YEAR"
$RAW = "$DATA_ROOT\raw\FR_$YEAR.txt"
$SCEN = "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_$YEAR"
$EUROMOD_ROOT = "U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+"
$GSUR_FILE = "$PROJ_ROOT\Data\external\FR_gsur_ruro.parquet"

# Output files (will be created by pipeline)
$SINGLES_RURO = "$PROC\singles_RURO_ready.parquet"
$COUPLES_RURO = "$PROC\couples_RURO_ready.parquet"
$SINGLES_DRAWS = "$PROC\singles_RURO_ready_RURO_draws.parquet"
$COUPLES_DRAWS = "$PROC\couples_RURO_ready_RURO_draws.parquet"
$EM_COMBINED = "$SCEN\combined_draws_em.parquet"
$MNL_BASE = "$PROC\fr_${YEAR}_RURO_mnl"
$MNL_FILE = "$MNL_BASE.parquet"

# Results output directory
$RESULTS_DIR = "$PROJ_ROOT\outputs\estimates\fr\$YEAR"

# Initial parameter files (optional - set to $null to use defaults)
# These CSV files should have columns: parameter, value
$INIT_PARAMS_SM = "$SCRIPTS\init_params_singles_template.csv"  # Single males
$INIT_PARAMS_SF = $null  # Single females (set path or $null for defaults)
$INIT_PARAMS_COU = $null  # Couples (set path or $null for defaults)
$INIT_PARAMS_JOINT = $null  # Joint estimation (set path or $null for defaults)

# Log file for pipeline output
$LOG_DIR = "$PROJ_ROOT\outputs\logs"
$TIMESTAMP = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LOG_FILE = "$LOG_DIR\fr_${YEAR}_pipeline_$TIMESTAMP.md"

# ---------------------------------------------------------------------
# PERFORMANCE OPTIMIZATIONS
# ---------------------------------------------------------------------
# Detect available CPU cores
$CPU_CORES = (Get-WmiObject -Class Win32_Processor).NumberOfLogicalProcessors
Write-Host "Detected CPU cores: $CPU_CORES" -ForegroundColor Cyan

# Set thread environment variables for optimal NumPy/MKL performance
# These apply to ALL steps (data prep uses vectorized pandas/numpy)
$env:OMP_NUM_THREADS = "$CPU_CORES"
$env:MKL_NUM_THREADS = "$CPU_CORES"
$env:NUMEXPR_NUM_THREADS = "$CPU_CORES"
$env:OPENBLAS_NUM_THREADS = "$CPU_CORES"

# For Numba parallelization (used in estimation step)
$env:NUMBA_NUM_THREADS = "$CPU_CORES"

# Set process priority to high for better CPU allocation
$process = Get-Process -Id $PID
$process.PriorityClass = "High"

# Disable Python output buffering for real-time logging
$env:PYTHONUNBUFFERED = "1"

# ---------------------------------------------------------------------
# LOGGING SETUP
# ---------------------------------------------------------------------
# Create log directory if it doesn't exist
New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null

# Initialize log file with header
$logHeader = @"
# RURO France $YEAR Pipeline Log

**Started:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Configuration:**
- Year: $YEAR
- System Year: $SYSTEM_YEAR
- N Draws: $N_DRAWS
- Wage Spec: $WAGE_SPEC
- Threads: $env:OMP_NUM_THREADS

---

"@
$logHeader | Out-File -FilePath $LOG_FILE -Encoding utf8

# Function to log to both console and file
function Write-Log {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
    $Message | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
}

# ---------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------
function Write-Step {
    param([string]$Message)
    $line = "=" * 70
    Write-Host ""
    Write-Host $line -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host $line -ForegroundColor Cyan
    Write-Host ""
    # Log to file
    "" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "## $Message" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
}

function Write-SubStep {
    param([string]$Message)
    Write-Host ">>> $Message" -ForegroundColor Yellow
    "### $Message" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
}

function Test-FileExists {
    param([string]$Path, [string]$Description)
    if (-not (Test-Path $Path)) {
        Write-Host "ERROR: $Description not found: $Path" -ForegroundColor Red
        "- ❌ ERROR: $Description not found: ``$Path``" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        return $false
    }
    Write-Host "  OK: $Description exists" -ForegroundColor Green
    "- ✅ $Description exists" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    return $true
}

function Run-PythonScript {
    param([string]$Command, [string]$Description)
    
    Write-SubStep $Description
    Write-Host "Command: $Command" -ForegroundColor DarkGray
    "``````bash" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    $Command | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "``````" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    
    $startTime = Get-Date
    
    # Use Invoke-Expression which is simpler and more reliable
    try {
        $output = Invoke-Expression $Command 2>&1
        $exitCode = $LASTEXITCODE
    } catch {
        $output = $_.Exception.Message
        $exitCode = 1
    }
    
    $duration = (Get-Date) - $startTime
    
    # Display and log output
    if ($output) {
        $outputStr = $output | Out-String
        Write-Host $outputStr
        "``````" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        $outputStr | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        "``````" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    }
    
    "" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    
    if ($exitCode -ne 0) {
        Write-Host "FAILED: $Description (exit code: $exitCode)" -ForegroundColor Red
        Write-Host "Duration: $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor Red
        "**FAILED:** $Description (exit code: $exitCode)" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        "Duration: $($duration.ToString('hh\:mm\:ss'))" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        return $false
    }
    
    Write-Host "SUCCESS: $Description" -ForegroundColor Green
    Write-Host "Duration: $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor Green
    "**SUCCESS:** $Description" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "Duration: ``$($duration.ToString('hh\:mm\:ss'))``" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    return $true
}

# ---------------------------------------------------------------------
# PRE-FLIGHT CHECKS
# ---------------------------------------------------------------------
Write-Step "PRE-FLIGHT CHECKS - FRANCE $YEAR PIPELINE"

Write-Host "Configuration:" -ForegroundColor White
Write-Host "  Year:         $YEAR"
Write-Host "  System Year:  $SYSTEM_YEAR"
Write-Host "  N Draws:      $N_DRAWS"
Write-Host "  Wage Spec:    $WAGE_SPEC"
Write-Host "  Threads:      $env:OMP_NUM_THREADS"
Write-Host ""

# Check required files exist
$preflightOK = $true

if (-not (Test-FileExists $RAW "Raw EUROMOD data")) { $preflightOK = $false }
if (-not (Test-FileExists $EUROMOD_ROOT "EUROMOD installation")) { $preflightOK = $false }
if (-not (Test-FileExists $GSUR_FILE "GSUR lookup table")) { 
    Write-Host "  WARNING: GSUR file not found - will skip GSUR merge" -ForegroundColor Yellow
}

# Create output directories
Write-Host ""
Write-Host "Creating output directories..." -ForegroundColor White
New-Item -ItemType Directory -Force -Path $PROC | Out-Null
New-Item -ItemType Directory -Force -Path $SCEN | Out-Null
New-Item -ItemType Directory -Force -Path $RESULTS_DIR | Out-Null
Write-Host "  OK: Directories created" -ForegroundColor Green

if (-not $preflightOK) {
    Write-Host ""
    Write-Host "Pre-flight checks FAILED. Please fix issues above." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Pre-flight checks PASSED" -ForegroundColor Green

# Record start time
$pipelineStart = Get-Date

# =====================================================================
# STEP 1: DATA PREPARATION
# =====================================================================
Write-Step "STEP 1/7: DATA PREPARATION (france_data_prep.py)"

$cmd = "python `"$SCRIPTS\france_data_prep.py`" --year $YEAR --raw-dir `"$DATA_ROOT\raw`" --out-dir `"$PROC`" --system-year $SYSTEM_YEAR --export-format parquet"

if (-not (Run-PythonScript $cmd "Prepare raw EUROMOD data for France $YEAR")) {
    Write-Host "Pipeline stopped at Step 1" -ForegroundColor Red
    exit 1
}

# =====================================================================
# STEP 2: RURO PREPARATION
# =====================================================================
Write-Step "STEP 2/7: RURO PREPARATION (RURO_prep.py)"

$cmd = "python `"$SCRIPTS\RURO_prep.py`" --processed-dir `"$PROC`" --base-year $YEAR --export-format parquet"

if (-not (Run-PythonScript $cmd "Build RURO-ready datasets (singles/couples)")) {
    Write-Host "Pipeline stopped at Step 2" -ForegroundColor Red
    exit 1
}

# Verify outputs
if (-not (Test-FileExists $SINGLES_RURO "Singles RURO-ready")) { exit 1 }

# =====================================================================
# STEP 3: GENERATE DRAWS
# =====================================================================
Write-Step "STEP 3/7: GENERATE DRAWS (RURO_draws.py)"

# Build command with optional couples path
$cmd = "python `"$SCRIPTS\RURO_draws.py`" --singles-path `"$SINGLES_RURO`" --n-draws $N_DRAWS --wage-spec $WAGE_SPEC"
if (Test-Path $COUPLES_RURO) {
    $cmd += " --couples-path `"$COUPLES_RURO`""
}

if (-not (Run-PythonScript $cmd "Generate $N_DRAWS counterfactual draws")) {
    Write-Host "Pipeline stopped at Step 3" -ForegroundColor Red
    exit 1
}

# Verify outputs
if (-not (Test-FileExists $SINGLES_DRAWS "Singles draws")) { exit 1 }

# =====================================================================
# STEP 4: EUROMOD SIMULATION
# =====================================================================
Write-Step "STEP 4/7: EUROMOD SIMULATION (RURO_euromod.py)"

$EUROMOD_SYSTEM = "${COUNTRY}_$SYSTEM_YEAR"
$EUROMOD_DATASET = "${COUNTRY}_$YEAR"

# Build command
$cmd = "python `"$SCRIPTS\RURO_euromod.py`" --singles-draws `"$SINGLES_DRAWS`" --microdata-template `"$RAW`" --euromod-root `"$EUROMOD_ROOT`" --euromod-system $EUROMOD_SYSTEM --euromod-dataset $EUROMOD_DATASET --scenario-dir `"$SCEN`""
if (Test-Path "$PROC\couples_RURO_ready_RURO_draws.parquet") {
    $cmd += " --couples-draws `"$COUPLES_DRAWS`""
}

if (-not (Run-PythonScript $cmd "Run EUROMOD on all draws")) {
    Write-Host "Pipeline stopped at Step 4" -ForegroundColor Red
    exit 1
}

# Verify outputs
if (-not (Test-FileExists $EM_COMBINED "EUROMOD combined output")) { exit 1 }

# =====================================================================
# STEP 5: PREPARE GSUR (if needed)
# =====================================================================
Write-Step "STEP 5/7: PREPARE GSUR (prepare_FR_gsur.py)"

if (-not (Test-Path $GSUR_FILE)) {
    $GSUR_INPUT = "$PROJ_ROOT\Data\external\FR_gsur.xlsx"
    if (Test-Path $GSUR_INPUT) {
        $cmd = "python `"$SCRIPTS\prepare_FR_gsur.py`" --input `"$GSUR_INPUT`" --output-dir `"$PROJ_ROOT\Data\external`""
        if (-not (Run-PythonScript $cmd "Prepare GSUR lookup table")) {
            Write-Host "WARNING: GSUR preparation failed - will skip GSUR in MNL" -ForegroundColor Yellow
        }
    } else {
        Write-Host "GSUR input file not found - skipping GSUR preparation" -ForegroundColor Yellow
    }
} else {
    Write-Host "GSUR file already exists: $GSUR_FILE" -ForegroundColor Green
}

# =====================================================================
# STEP 6: BUILD MNL DATASET
# =====================================================================
Write-Step "STEP 6/7: BUILD MNL DATASET (RURO_prep_mnl_basic.py)"

# Build command
$cmd = "python `"$SCRIPTS\RURO_prep_mnl_basic.py`" --singles-draws `"$SINGLES_DRAWS`" --euromod-combined `"$EM_COMBINED`" --out-base `"$MNL_BASE`" --wage-spec $WAGE_SPEC --year $YEAR"

if (Test-Path $COUPLES_DRAWS) {
    $cmd += " --couples-draws `"$COUPLES_DRAWS`""
}

if (Test-Path $GSUR_FILE) {
    $cmd += " --gsur-file `"$GSUR_FILE`""
} else {
    $cmd += " --no-gsur"
}

if (-not (Run-PythonScript $cmd "Build MNL estimation dataset")) {
    Write-Host "Pipeline stopped at Step 6" -ForegroundColor Red
    exit 1
}

# Verify outputs
if (-not (Test-FileExists $MNL_FILE "MNL dataset")) { exit 1 }

# =====================================================================
# STEP 7: RURO ESTIMATION
# =====================================================================
Write-Step "STEP 7/7: RURO ESTIMATION (RURO_estimate_FR.py)"

# 7a. Estimate SINGLE MALES
Write-Host ""
Write-Host "--- 7a. Single Males ---" -ForegroundColor Magenta
$cmd = "python `"$SCRIPTS\RURO_estimate_FR.py`" --mnl-file `"$MNL_FILE`" --group 1 --sex m --wage-spec $WAGE_SPEC --optimizer L-BFGS-B --maxiter 500 --use-numba --out-file `"$RESULTS_DIR\fr_${YEAR}_single_males.json`""
if ($INIT_PARAMS_SM -and (Test-Path $INIT_PARAMS_SM)) {
    $cmd += " --init-params `"$INIT_PARAMS_SM`""
    Write-Host "  Using initial params: $INIT_PARAMS_SM" -ForegroundColor Cyan
}

if (-not (Run-PythonScript $cmd "Estimate single males")) {
    Write-Host "WARNING: Single males estimation failed" -ForegroundColor Yellow
}

# 7b. Estimate SINGLE FEMALES
Write-Host ""
Write-Host "--- 7b. Single Females ---" -ForegroundColor Magenta
$cmd = "python `"$SCRIPTS\RURO_estimate_FR.py`" --mnl-file `"$MNL_FILE`" --group 1 --sex f --wage-spec $WAGE_SPEC --optimizer L-BFGS-B --maxiter 500 --use-numba --out-file `"$RESULTS_DIR\fr_${YEAR}_single_females.json`""
if ($INIT_PARAMS_SF -and (Test-Path $INIT_PARAMS_SF)) {
    $cmd += " --init-params `"$INIT_PARAMS_SF`""
    Write-Host "  Using initial params: $INIT_PARAMS_SF" -ForegroundColor Cyan
}

if (-not (Run-PythonScript $cmd "Estimate single females")) {
    Write-Host "WARNING: Single females estimation failed" -ForegroundColor Yellow
}

# 7c. Estimate COUPLES (if data exists)
Write-Host ""
Write-Host "--- 7c. Couples ---" -ForegroundColor Magenta
$cmd = "python `"$SCRIPTS\RURO_estimate_FR.py`" --mnl-file `"$MNL_FILE`" --group 10 --wage-spec $WAGE_SPEC --optimizer L-BFGS-B --maxiter 500 --use-numba --out-file `"$RESULTS_DIR\fr_${YEAR}_couples.json`""
if ($INIT_PARAMS_COU -and (Test-Path $INIT_PARAMS_COU)) {
    $cmd += " --init-params `"$INIT_PARAMS_COU`""
    Write-Host "  Using initial params: $INIT_PARAMS_COU" -ForegroundColor Cyan
}

if (-not (Run-PythonScript $cmd "Estimate couples")) {
    Write-Host "WARNING: Couples estimation failed (may not have couple data)" -ForegroundColor Yellow
}

# 7d. JOINT ESTIMATION (all groups with shared opportunity parameters)
Write-Host ""
Write-Host "--- 7d. Joint Estimation (all groups) ---" -ForegroundColor Magenta
$cmd = "python `"$SCRIPTS\RURO_estimate_FR.py`" --mnl-file `"$MNL_FILE`" --joint --wage-spec $WAGE_SPEC --optimizer L-BFGS-B --maxiter 500 --use-numba --n-jobs $CPU_CORES --out-file `"$RESULTS_DIR\fr_${YEAR}_joint.json`""
if ($INIT_PARAMS_JOINT -and (Test-Path $INIT_PARAMS_JOINT)) {
    $cmd += " --init-params `"$INIT_PARAMS_JOINT`""
    Write-Host "  Using initial params: $INIT_PARAMS_JOINT" -ForegroundColor Cyan
}

if (-not (Run-PythonScript $cmd "Joint estimation (shared opportunity parameters)")) {
    Write-Host "WARNING: Joint estimation failed" -ForegroundColor Yellow
}

# =====================================================================
# STEP 8: POST-ESTIMATION ANALYSIS (OPTIONAL)
# =====================================================================
Write-Step "STEP 8/8: POST-ESTIMATION ANALYSIS (RURO_post_estimation.py)"

$POST_EST_DIR = "$PROJ_ROOT\outputs\post_estimation\fr\$YEAR"
New-Item -ItemType Directory -Force -Path $POST_EST_DIR | Out-Null

# Helper function for post-estimation
function Run-PostEstimation {
    param([string]$Name, [string]$EstFile, [string]$Group, [string]$Sex = "")
    
    if (-not (Test-Path $EstFile)) {
        Write-Host "Skipping $Name (estimation file not found)" -ForegroundColor Yellow
        return
    }
    
    Write-Host ""
    Write-Host "--- Post-Estimation: $Name ---" -ForegroundColor Magenta
    
    $outDir = "$POST_EST_DIR\$($Name.Replace(' ', '_').ToLower())"
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
      $cmd = "python `"$SCRIPTS\RURO_post_estimation.py`" --results `"$EstFile`" --mnl-file `"$MNL_FILE`" --out-dir `"$outDir`" --wage-spec $WAGE_SPEC"
    if ($Sex) { $cmd += " --sex $Sex" }
    
    Run-PythonScript $cmd "Post-estimation analysis for $Name"
}

# Run post-estimation for each successful estimation
Run-PostEstimation -Name "Single Males" -EstFile "$RESULTS_DIR\fr_${YEAR}_single_males.json" -Group "1" -Sex "m"
Run-PostEstimation -Name "Single Females" -EstFile "$RESULTS_DIR\fr_${YEAR}_single_females.json" -Group "1" -Sex "f"
Run-PostEstimation -Name "Couples" -EstFile "$RESULTS_DIR\fr_${YEAR}_couples.json" -Group "10"
Run-PostEstimation -Name "Joint" -EstFile "$RESULTS_DIR\fr_${YEAR}_joint.json" -Group "1"

# =====================================================================
# PIPELINE COMPLETE
# =====================================================================
$pipelineEnd = Get-Date
$totalDuration = $pipelineEnd - $pipelineStart

Write-Step "PIPELINE COMPLETE - FRANCE $YEAR"

Write-Host "Summary:" -ForegroundColor White
Write-Host "  Data Year:      $YEAR"
Write-Host "  System Year:    $SYSTEM_YEAR"
Write-Host "  N Draws:        $N_DRAWS"
Write-Host "  Wage Spec:      $WAGE_SPEC"
Write-Host ""
Write-Host "Output Files:" -ForegroundColor White
Write-Host "  MNL Dataset:    $MNL_FILE"
Write-Host "  Results Dir:    $RESULTS_DIR"
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
- MNL Dataset: ``$MNL_FILE``
- Results Dir: ``$RESULTS_DIR``

"@ | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
