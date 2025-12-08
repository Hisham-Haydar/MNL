# =====================================================================
# RURO FRANCE 2016 – JOINT ESTIMATION (FULL PIPELINE)
# =====================================================================
# This script runs the COMPLETE pipeline from data prep to joint estimation.
# It regenerates the MNL dataset with the SIMPLIFIED specification:
#   - age_norm = dag - mean(dag) (demeaned, not ratio)
#   - age_norm2 = age_norm²
#   - n_children = sum of all children (collapsed from children0_3, children4_6, children7_9)
#   - No region dummies in preferences/hours opportunity
#   - No year dummies in wage equation
#
# Pipeline steps:
#   1. france_data_prep.py   - Prepare raw EUROMOD data
#   2. RURO_prep.py          - Build RURO-ready datasets (singles/couples)
#   3. RURO_draws.py         - Generate opportunity draws
#   4. RURO_euromod.py       - Run EUROMOD on all draws
#   5. prepare_FR_gsur.py    - Prepare GSUR data (if needed)
#   6. RURO_prep_mnl_basic.py - Build MNL estimation dataset (with new variables)
#   7. RURO_estimate_FR.py   - Joint estimation
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\run_fr_2016_joint_only.ps1
#
# Author: Generated for France 2016 joint estimation
# Date: 2025-12-08
# =====================================================================

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------
$YEAR = 2016
$COUNTRY = "FR"
$SYSTEM_YEAR = 2015  # EUROMOD system year = data year - 1
$N_DRAWS = 99        # Number of counterfactual draws
$WAGE_SPEC = "vw"    # "fw" = fixed wages, "vw" = variable wages
$MAX_ITER = 2000     # Maximum optimizer iterations

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
$EST_FILE = "$RESULTS_DIR\fr_${YEAR}_joint.json"
$POST_EST_DIR = "$PROJ_ROOT\outputs\post_estimation\fr\$YEAR"

# Initial parameter file (optional - set to $null to use defaults)
$INIT_PARAMS_JOINT = $null

# Log file
$LOG_DIR = "$PROJ_ROOT\outputs\logs"
$TIMESTAMP = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LOG_FILE = "$LOG_DIR\fr_${YEAR}_joint_only_$TIMESTAMP.md"

# Skip data regeneration if MNL file exists and is recent?
# Set to $false to ALWAYS regenerate (recommended after code changes)
$SKIP_IF_MNL_EXISTS = $false

# ---------------------------------------------------------------------
# PERFORMANCE OPTIMIZATIONS
# ---------------------------------------------------------------------
# Detect available CPU cores (take first value if multiple processors)
$CPU_CORES_RAW = (Get-WmiObject -Class Win32_Processor).NumberOfLogicalProcessors
if ($CPU_CORES_RAW -is [array]) {
    $CPU_CORES = $CPU_CORES_RAW[0]
} else {
    $CPU_CORES = $CPU_CORES_RAW
}
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
New-Item -ItemType Directory -Force -Path $PROC | Out-Null
New-Item -ItemType Directory -Force -Path $SCEN | Out-Null

$logHeader = @"
# RURO France $YEAR - Joint Estimation (Full Pipeline)

**Started:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Configuration:**
- Year: $YEAR
- System Year: $SYSTEM_YEAR
- N Draws: $N_DRAWS
- Wage Spec: $WAGE_SPEC
- Max Iterations: $MAX_ITER
- CPU Cores: $CPU_CORES

**SIMPLIFIED SPECIFICATION:**
- Age normalization: demeaned (dag - mean_dag) instead of log ratio
- Children: single n_children variable (collapsed)
- No region dummies in preferences/hours opportunity
- No year dummies in wage equation
- Total parameters: 60 (vw) or 48 (fw)

---

"@
$logHeader | Out-File -FilePath $LOG_FILE -Encoding utf8

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
        Write-Host "  MISSING: $Description - $Path" -ForegroundColor Yellow
        return $false
    }
    Write-Host "  OK: $Description exists" -ForegroundColor Green
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
    
    try {
        $output = Invoke-Expression $Command 2>&1
        $exitCode = $LASTEXITCODE
    } catch {
        $output = $_.Exception.Message
        $exitCode = 1
    }
    
    $duration = (Get-Date) - $startTime
    
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
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "RURO FRANCE $YEAR - JOINT ESTIMATION (FULL PIPELINE)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Configuration:" -ForegroundColor White
Write-Host "  Year:           $YEAR"
Write-Host "  System Year:    $SYSTEM_YEAR"
Write-Host "  N Draws:        $N_DRAWS"
Write-Host "  Wage Spec:      $WAGE_SPEC"
Write-Host "  Max Iterations: $MAX_ITER"
Write-Host "  CPU Cores:      $CPU_CORES"
Write-Host ""

# Check required files
$preflightOK = $true
if (-not (Test-FileExists $RAW "Raw EUROMOD data")) { $preflightOK = $false }
if (-not (Test-FileExists $EUROMOD_ROOT "EUROMOD installation")) { $preflightOK = $false }
Test-FileExists $GSUR_FILE "GSUR lookup table" | Out-Null  # Warning only

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
# CHECK IF DATA REGENERATION IS NEEDED
# =====================================================================
$needsDataRegen = $true

if ($SKIP_IF_MNL_EXISTS -and (Test-Path $MNL_FILE)) {
    Write-Host ""
    Write-Host "MNL file exists: $MNL_FILE" -ForegroundColor Yellow
    Write-Host "Skipping data regeneration (set SKIP_IF_MNL_EXISTS=`$false to force)" -ForegroundColor Yellow
    $needsDataRegen = $false
}

if ($needsDataRegen) {
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

    # =====================================================================
    # STEP 3: GENERATE DRAWS
    # =====================================================================
    Write-Step "STEP 3/7: GENERATE DRAWS (RURO_draws.py)"

    $cmd = "python `"$SCRIPTS\RURO_draws.py`" --singles-path `"$SINGLES_RURO`" --n-draws $N_DRAWS --wage-spec $WAGE_SPEC"
    if (Test-Path $COUPLES_RURO) {
        $cmd += " --couples-path `"$COUPLES_RURO`""
    }

    if (-not (Run-PythonScript $cmd "Generate $N_DRAWS counterfactual draws")) {
        Write-Host "Pipeline stopped at Step 3" -ForegroundColor Red
        exit 1
    }

    # =====================================================================
    # STEP 4: EUROMOD SIMULATION
    # =====================================================================
    Write-Step "STEP 4/7: EUROMOD SIMULATION (RURO_euromod.py)"

    $EUROMOD_SYSTEM = "${COUNTRY}_$SYSTEM_YEAR"
    $EUROMOD_DATASET = "${COUNTRY}_$YEAR"

    $cmd = "python `"$SCRIPTS\RURO_euromod.py`" --singles-draws `"$SINGLES_DRAWS`" --microdata-template `"$RAW`" --euromod-root `"$EUROMOD_ROOT`" --euromod-system $EUROMOD_SYSTEM --euromod-dataset $EUROMOD_DATASET --scenario-dir `"$SCEN`""
    if (Test-Path $COUPLES_DRAWS) {
        $cmd += " --couples-draws `"$COUPLES_DRAWS`""
    }

    if (-not (Run-PythonScript $cmd "Run EUROMOD on all draws")) {
        Write-Host "Pipeline stopped at Step 4" -ForegroundColor Red
        exit 1
    }

    # =====================================================================
    # STEP 5: PREPARE GSUR (if needed)
    # =====================================================================
    Write-Step "STEP 5/7: PREPARE GSUR (prepare_FR_gsur.py)"

    if (-not (Test-Path $GSUR_FILE)) {
        $GSUR_INPUT = "$PROJ_ROOT\Data\external\FR_gsur.xlsx"
        if (Test-Path $GSUR_INPUT) {
            $cmd = "python `"$SCRIPTS\prepare_FR_gsur.py`" --input `"$GSUR_INPUT`" --output-dir `"$PROJ_ROOT\Data\external`""
            Run-PythonScript $cmd "Prepare GSUR lookup table" | Out-Null
        } else {
            Write-Host "GSUR input file not found - skipping GSUR preparation" -ForegroundColor Yellow
        }
    } else {
        Write-Host "GSUR file already exists: $GSUR_FILE" -ForegroundColor Green
    }

    # =====================================================================
    # STEP 6: BUILD MNL DATASET (with new variables)
    # =====================================================================
    Write-Step "STEP 6/7: BUILD MNL DATASET (RURO_prep_mnl_basic.py)"

    Write-Host "NOTE: This creates the SIMPLIFIED variables:" -ForegroundColor Cyan
    Write-Host "  - age_norm = dag - mean(dag)  (demeaned)" -ForegroundColor Cyan
    Write-Host "  - age_norm2 = age_norm^2" -ForegroundColor Cyan
    Write-Host "  - n_children (collapsed from children0_3, children4_6, children7_9)" -ForegroundColor Cyan
    Write-Host ""

    $cmd = "python `"$SCRIPTS\RURO_prep_mnl_basic.py`" --singles-draws `"$SINGLES_DRAWS`" --euromod-combined `"$EM_COMBINED`" --out-base `"$MNL_BASE`" --wage-spec $WAGE_SPEC --year $YEAR --skip-csv"

    if (Test-Path $COUPLES_DRAWS) {
        $cmd += " --couples-draws `"$COUPLES_DRAWS`""
    }

    if (Test-Path $GSUR_FILE) {
        $cmd += " --gsur-file `"$GSUR_FILE`""
    } else {
        $cmd += " --no-gsur"
    }

    if (-not (Run-PythonScript $cmd "Build MNL estimation dataset with simplified variables")) {
        Write-Host "Pipeline stopped at Step 6" -ForegroundColor Red
        exit 1
    }

    # Verify output
    if (-not (Test-Path $MNL_FILE)) {
        Write-Host "ERROR: MNL file not created: $MNL_FILE" -ForegroundColor Red
        exit 1
    }
}

# =====================================================================
# STEP 7: JOINT ESTIMATION
# =====================================================================
Write-Step "STEP 7/7: JOINT ESTIMATION (RURO_estimate_FR.py)"

Write-Host "SIMPLIFIED PARAMETER STRUCTURE:" -ForegroundColor Magenta
Write-Host "  Singles: 22 params (vw) = 9 prefs + 7 hopp + 6 wopp" -ForegroundColor White
Write-Host "  Couples: 42 params (vw) = 16 prefs + 14 hopp + 12 wopp" -ForegroundColor White
Write-Host "  Joint:   60 params (vw) = 34 prefs + 14 hopp + 12 wopp" -ForegroundColor White
Write-Host ""

$cmd = "python `"$SCRIPTS\RURO_estimate_FR.py`" " +
       "--mnl-file `"$MNL_FILE`" " +
       "--joint " +
       "--wage-spec $WAGE_SPEC " +
       "--optimizer L-BFGS-B " +
       "--maxiter $MAX_ITER " +
       "--use-numba " +
       "--n-jobs $CPU_CORES " +
       "--post-estimation " +
       "--out-file `"$EST_FILE`""

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
Write-Host "  MNL Dataset:    $MNL_FILE"
Write-Host "  Estimation:     $EST_FILE"
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
- Estimation: ``$EST_FILE``
- Log File: ``$LOG_FILE``

### SIMPLIFIED Parameters Estimated (Total: 60 for vw, 48 for fw)

#### Group-Specific Preferences (34 parameters)

**Single Males (9):** 
- beta_l0, beta_l_age_norm, beta_l_age_norm2, beta_l_n_children
- beta_l_educL, beta_l_educH, beta_c, theta_l, theta_c

**Single Females (9):** 
- beta_l0, beta_l_age_norm, beta_l_age_norm2, beta_l_n_children
- beta_l_educL, beta_l_educH, beta_c, theta_l, theta_c

**Couples (16):**
- Male leisure (6): beta_l0_m, beta_l_age_norm_m, beta_l_age_norm2_m, beta_l_n_children_m, beta_l_educL_m, beta_l_educH_m
- Female leisure (6): beta_l0_f, beta_l_age_norm_f, beta_l_age_norm2_f, beta_l_n_children_f, beta_l_educL_f, beta_l_educH_f
- Shared (4): theta_l_m, theta_l_f, theta_c, beta_c

#### Gender-Shared Opportunity Parameters (26 parameters for vw, 14 for fw)

**Hours Opportunity - Males (7):** 
- beta_work, beta_pt1, beta_pt2, beta_ft, beta_gsur, beta_work_educL, beta_work_educH

**Hours Opportunity - Females (7):** 
- beta_work, beta_pt1, beta_pt2, beta_ft, beta_gsur, beta_work_educL, beta_work_educH

**Wage Opportunity - Males (6, vw only):** 
- beta0, beta_educL, beta_educH, beta_pexp, beta_pexp2, sigma

**Wage Opportunity - Females (6, vw only):** 
- beta0, beta_educL, beta_educH, beta_pexp, beta_pexp2, sigma

### Key Simplifications from Original Model
1. **Age**: Demeaned (dag - mean_dag) instead of log ratio → better numerical stability
2. **Children**: Single n_children variable instead of three separate age groups
3. **Region dummies**: REMOVED from preferences and hours opportunity
4. **Year dummies**: REMOVED from wage equation
5. **Total reduction**: From 100 to 60 parameters (40% reduction)

"@ | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
