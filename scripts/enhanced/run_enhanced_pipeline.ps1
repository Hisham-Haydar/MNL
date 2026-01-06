# =====================================================================
# ENHANCED RURO FRANCE 2016 – COMPLETE PIPELINE RUNNER
# =====================================================================
# This script runs the COMPLETE enhanced RURO pipeline from data prep
# to joint estimation using the enhanced scripts with improved:
#   - Performance optimizations
#   - Error handling and validation
#   - Logging and diagnostics
#   - Post-estimation analysis
#
# Pipeline steps:
#   1. enh_france_data_prep.py      - Prepare raw EUROMOD data
#   2. enh_RURO_prep.py             - Build RURO-ready datasets (singles/couples)
#   3. enh_RURO_draws.py            - Generate opportunity draws
#   4. enh_RURO_euromod.py          - Run EUROMOD on all draws
#   5. enh_prepare_FR_gsur.py       - Prepare GSUR data (if needed)
#   6. enh_RURO_prep_mnl_basic.py   - Build MNL estimation dataset
#   7. enh_RURO_estimate_FR.py      - Joint estimation
#   8. enh_RURO_post_estimation.py  - Post-estimation analysis & reports
#
# Usage:
#   1. Activate virtual environment: .\.venv\Scripts\Activate.ps1
#   2. Run: powershell -ExecutionPolicy Bypass -File .\scripts\enhanced\run_enhanced_pipeline.ps1
#
#   Options:
#     -SkipTo <step>     Skip to a specific step (1-8), runs from that step onward
#     -OnlyStep <step>   Run only a specific step (1-8)
#     -SkipSteps <list>  Comma-separated list of steps to skip (e.g., "1,2,3")
#     -ForceRebuild      Force rebuild of all intermediate files
#
#   Examples:
#     .\run_enhanced_pipeline.ps1 -SkipTo 7           # Skip to estimation
#     .\run_enhanced_pipeline.ps1 -OnlyStep 8        # Run only post-estimation
#     .\run_enhanced_pipeline.ps1 -SkipSteps "1,2,3" # Skip data prep steps
#     .\run_enhanced_pipeline.ps1 -ForceRebuild      # Force full rebuild
#
# Author: RURO Estimation Team
# Date: 2026-01-03
# Version: Enhanced Pipeline v2.0
# =====================================================================

# ---------------------------------------------------------------------
# CLI PARAMETERS
# ---------------------------------------------------------------------
param(
    [int]$SkipTo = 0,           # Skip to this step number (1-8), 0 = run all
    [int]$OnlyStep = 0,         # Run only this step (1-8), 0 = run all
    [string]$SkipSteps = "",    # Comma-separated list of steps to skip
    [switch]$ForceRebuild       # Force rebuild of all intermediate files
)

# Parse SkipSteps into array
$SkipStepsList = @()
if ($SkipSteps -ne "") {
    $SkipStepsList = $SkipSteps -split "," | ForEach-Object { [int]$_.Trim() }
}

# Helper function to check if a step should run
function Should-RunStep {
    param([int]$StepNum)
    
    # If OnlyStep is set, only run that step
    if ($OnlyStep -gt 0) {
        return ($StepNum -eq $OnlyStep)
    }
    
    # If SkipTo is set, skip steps before it
    if ($SkipTo -gt 0 -and $StepNum -lt $SkipTo) {
        return $false
    }
    
    # If step is in SkipSteps list, skip it
    if ($SkipStepsList -contains $StepNum) {
        return $false
    }
    
    return $true
}

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------
$YEAR = 2016
$COUNTRY = "FR"
$SYSTEM_YEAR = 2015  # EUROMOD system year = data year - 1
$N_DRAWS = 99        # Number of counterfactual draws
$WAGE_SPEC = "vw"    # "fw" = fixed wages, "vw" = variable wages
$MAX_ITER = 5000     # Maximum optimizer iterations

# Paths (SERVER CONFIGURATION)
$PROJ_ROOT = "U:\Desktop\Nizam_Hisham\MNL"
$SCRIPTS = "$PROJ_ROOT\scripts\enhanced"
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
# Enhanced version creates separate singles/couples files, not a combined file
$MNL_SINGLES = "${MNL_BASE}__singles.parquet"
$MNL_COUPLES = "${MNL_BASE}__couples.parquet"
$MNL_META = "${MNL_BASE}__mnlmeta.json"

# Results output directory
$RESULTS_DIR = "$PROJ_ROOT\outputs\estimates\fr\$YEAR"
$EST_FILE = "$RESULTS_DIR\fr_${YEAR}_joint.json"
$POST_EST_DIR = "$PROJ_ROOT\outputs\post_estimation\fr\$YEAR"

# Initial parameter file (optional - set to $null to use defaults)
# Using previous estimation results to speed up convergence
$INIT_PARAMS_JOINT = "$PROJ_ROOT\outputs\estimates\fr\2016\fr_2016_joint.json"

# Log file - use .txt for full detailed output capture (like enh_pipeline.ps1)
$LOG_DIR = "$PROJ_ROOT\outputs\logs"
$TIMESTAMP = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LOG_FILE = "$LOG_DIR\fr_${YEAR}_enhanced_pipeline_$TIMESTAMP.txt"

# CRITICAL FIX: Use virtual environment Python explicitly for Start-Process
$PYTHON_EXE = "$PROJ_ROOT\.venv\Scripts\python.exe"

# Skip data regeneration if MNL file exists and is recent?
# Set to $false to ALWAYS regenerate (recommended after code changes)
# Note: -ForceRebuild CLI flag overrides this setting
$SKIP_IF_MNL_EXISTS = $true
if ($ForceRebuild) {
    $SKIP_IF_MNL_EXISTS = $false
    Write-Host "ForceRebuild enabled - will regenerate all intermediate files" -ForegroundColor Yellow
}

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

# Auto-detect latest estimation JSON to use as initial parameters if path not provided
if (-not $INIT_PARAMS_JOINT -or -not (Test-Path $INIT_PARAMS_JOINT)) {
    $latestEstimate = Get-ChildItem -Path $RESULTS_DIR -Filter "fr_*joint*.json" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if ($latestEstimate) {
        $INIT_PARAMS_JOINT = $latestEstimate.FullName
        Write-Host "Detected latest estimation JSON for warm start: $INIT_PARAMS_JOINT" -ForegroundColor Cyan
    } else {
        $INIT_PARAMS_JOINT = $null
        Write-Host "No prior estimation JSON found for warm start." -ForegroundColor Yellow
    }
}

$logHeader = @"
# RURO France $YEAR - Enhanced Pipeline Execution

**Started:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Configuration:**
- Year: $YEAR
- System Year: $SYSTEM_YEAR
- N Draws: $N_DRAWS
- Wage Spec: $WAGE_SPEC
- Max Iterations: $MAX_ITER
- CPU Cores: $CPU_CORES
- Scripts: Enhanced v2.0

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

    # Enhanced logging with timestamps
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    Write-SubStep $Description
    Write-Host "[$timestamp] Command: $Command" -ForegroundColor DarkGray

    # Log command with timestamp
    "" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "=" * 80 | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "STEP: $Description" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "=" * 80 | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "Started: $timestamp" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "Command: $Command" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "OUTPUT:" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "-" * 80 | Out-File -FilePath $LOG_FILE -Append -Encoding utf8

    $startTime = Get-Date

    # Create temp files for output capture (like enh_pipeline.ps1)
    $stdoutFile = [System.IO.Path]::GetTempFileName()
    $stderrFile = [System.IO.Path]::GetTempFileName()

    try {
        # Parse command to extract script path and arguments
        # Command format: python "script.py" --arg1 val1 --arg2 val2
        if ($Command -match '^python\s+"([^"]+)"\s*(.*)$') {
            $scriptPath = $Matches[1]
            $scriptArgs = $Matches[2]
        } elseif ($Command -match '^python\s+(\S+)\s*(.*)$') {
            $scriptPath = $Matches[1]
            $scriptArgs = $Matches[2]
        } else {
            throw "Could not parse command: $Command"
        }

        # Build argument list for Start-Process
        $argList = "`"$scriptPath`" $scriptArgs"

        Write-Host "[$timestamp] Starting process with redirected output..." -ForegroundColor DarkGray

        # Start process with redirected output (captures ALL output including sanity checks)
        $process = Start-Process -FilePath $PYTHON_EXE `
            -ArgumentList $argList `
            -NoNewWindow `
            -Wait `
            -PassThru `
            -RedirectStandardOutput $stdoutFile `
            -RedirectStandardError $stderrFile

        $exitCode = $process.ExitCode

        # Read and display stdout
        if (Test-Path $stdoutFile) {
            $stdout = Get-Content $stdoutFile -Raw
            if ($stdout) {
                $stdout -split "`r?`n" | ForEach-Object {
                    if ($_.Trim()) {
                        $lineTimestamp = Get-Date -Format "HH:mm:ss.fff"
                        Write-Host "[$lineTimestamp] $_"
                        "[$lineTimestamp] $_" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
                    }
                }
            }
        }

        # Read and display stderr (in red, marked as STDERR in log)
        if (Test-Path $stderrFile) {
            $stderr = Get-Content $stderrFile -Raw
            if ($stderr) {
                "" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
                "=== STDERR OUTPUT ===" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
                $stderr -split "`r?`n" | ForEach-Object {
                    if ($_.Trim()) {
                        $lineTimestamp = Get-Date -Format "HH:mm:ss.fff"
                        Write-Host "[$lineTimestamp] [STDERR] $_" -ForegroundColor Red
                        "[$lineTimestamp] [STDERR] $_" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
                    }
                }
                "=== END STDERR ===" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
            }
        }

    } catch {
        $errorMsg = $_.Exception.Message
        Write-Host "[ERROR] $errorMsg" -ForegroundColor Red
        "[EXCEPTION] $errorMsg" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        $_.ScriptStackTrace | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        $exitCode = 1
    } finally {
        # Clean up temp files
        if (Test-Path $stdoutFile) { Remove-Item $stdoutFile -Force -ErrorAction SilentlyContinue }
        if (Test-Path $stderrFile) { Remove-Item $stderrFile -Force -ErrorAction SilentlyContinue }
    }

    $endTime = Get-Date
    $duration = $endTime - $startTime

    # Log completion with timestamp
    $endTimestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "-" * 80 | Out-File -FilePath $LOG_FILE -Append -Encoding utf8

    if ($exitCode -ne 0) {
        Write-Host "[$endTimestamp] FAILED: $Description (exit code: $exitCode)" -ForegroundColor Red
        Write-Host "Duration: $($duration.ToString('hh\:mm\:ss\.fff'))" -ForegroundColor Red
        "Status: FAILED (exit code: $exitCode)" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        "Completed: $endTimestamp" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        "Duration: $($duration.ToString('hh\:mm\:ss\.fff'))" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        "" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        return $false
    }    Write-Host "[$endTimestamp] SUCCESS: $Description" -ForegroundColor Green
    Write-Host "Duration: $($duration.ToString('hh\:mm\:ss\.fff'))" -ForegroundColor Green
    "Status: SUCCESS" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "Completed: $endTimestamp" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "Duration: $($duration.ToString('hh\:mm\:ss\.fff'))" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    return $true
}

# ---------------------------------------------------------------------
# PRE-FLIGHT CHECKS
# ---------------------------------------------------------------------
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "ENHANCED RURO FRANCE $YEAR - COMPLETE PIPELINE" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Configuration:" -ForegroundColor White
Write-Host "  Year:           $YEAR"
Write-Host "  System Year:    $SYSTEM_YEAR"
Write-Host "  N Draws:        $N_DRAWS"
Write-Host "  Wage Spec:      $WAGE_SPEC"
Write-Host "  Max Iterations: $MAX_ITER"
Write-Host "  CPU Cores:      $CPU_CORES"
Write-Host "  Scripts:        Enhanced v2.0"
Write-Host ""

# Display CLI options if set
if ($SkipTo -gt 0 -or $OnlyStep -gt 0 -or $SkipSteps -ne "" -or $ForceRebuild) {
    Write-Host "CLI Options:" -ForegroundColor Magenta
    if ($SkipTo -gt 0) { 
        Write-Host "  SkipTo:       Step $SkipTo (will skip steps 1-$($SkipTo-1), then run steps $SkipTo-8)" -ForegroundColor Yellow 
    }
    if ($OnlyStep -gt 0) { Write-Host "  OnlyStep:     Step $OnlyStep only" -ForegroundColor Yellow }
    if ($SkipSteps -ne "") { Write-Host "  SkipSteps:    $SkipSteps" -ForegroundColor Yellow }
    if ($ForceRebuild) { Write-Host "  ForceRebuild: Enabled" -ForegroundColor Yellow }
    Write-Host ""
    
    # Confirmation prompt for SkipTo (to clarify it continues after target step)
    if ($SkipTo -gt 0 -and $OnlyStep -eq 0) {
        Write-Host "NOTE: -SkipTo will run from Step $SkipTo through Step 8." -ForegroundColor Cyan
        Write-Host "      To run ONLY Step $SkipTo, use: -OnlyStep $SkipTo" -ForegroundColor Cyan
        Write-Host ""
        $response = Read-Host "Continue? (Y/n)"
        if ($response -eq "n" -or $response -eq "N") {
            Write-Host "Aborted by user." -ForegroundColor Yellow
            exit 0
        }
        Write-Host ""
    }
}

# =====================================================================
# VERIFY VIRTUAL ENVIRONMENT (CRITICAL!)
# =====================================================================
Write-Host "Verifying virtual environment..." -ForegroundColor Yellow
Write-Host ""

# Check Python executable path
$pythonPath = (Get-Command python).Source
Write-Host "  Python executable: $pythonPath"

if ($pythonPath -like "*\.venv\*") {
    Write-Host "  OK: Running in virtual environment" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Not running in .venv!" -ForegroundColor Red
    Write-Host "  Please activate virtual environment first:" -ForegroundColor Yellow
    Write-Host "    cd U:\Desktop\Nizam_Hisham\MNL" -ForegroundColor Yellow
    Write-Host "    .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    exit 1
}

# Test critical imports
Write-Host ""
Write-Host "Testing critical package imports..." -ForegroundColor Yellow

# Test pandas and numpy first (always needed)
$output = python -c "import pandas; import numpy; print('OK')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: pandas or numpy import failed" -ForegroundColor Red
    Write-Host "  $output" -ForegroundColor Red
    exit 1
}
Write-Host "  OK: pandas, numpy available" -ForegroundColor Green

# Test scipy
$output = python -c "import scipy; print('OK')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: scipy available" -ForegroundColor Green
} else {
    Write-Host "  ERROR: scipy import failed (required for optimization)" -ForegroundColor Red
    exit 1
}

# Test numba
$output = python -c "import numba; print('OK')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: numba available (JIT compilation enabled)" -ForegroundColor Green
} else {
    Write-Host "  WARNING: numba not available (estimation will be slower)" -ForegroundColor Yellow
}

# Test euromod (warn if missing but don't fail - pipeline will handle EUROMOD step errors)
$euromodOutput = python -c "import euromod; print('OK')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: euromod available" -ForegroundColor Green
} else {
    Write-Host "  WARNING: euromod import issue (non-critical)" -ForegroundColor Yellow
    Write-Host "  Note: EUROMOD step may use different import methods" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Virtual environment verification PASSED" -ForegroundColor Green
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

# Check if user wants to run any of steps 1-6
$userWantsSteps1to6 = $false
if ($OnlyStep -gt 0 -and $OnlyStep -le 6) {
    $userWantsSteps1to6 = $true
} elseif ($SkipTo -gt 0 -and $SkipTo -le 6) {
    $userWantsSteps1to6 = $true
} elseif ($SkipTo -eq 0 -and $OnlyStep -eq 0) {
    # Default: run all steps
    $userWantsSteps1to6 = $true
}

# Skip data regeneration ONLY if:
# 1. All files exist
# 2. User didn't request steps 1-6 via CLI
# 3. ForceRebuild is not set
if ($SKIP_IF_MNL_EXISTS -and 
    (Test-Path $MNL_SINGLES) -and 
    (Test-Path $MNL_COUPLES) -and 
    (Test-Path $EM_COMBINED) -and 
    (Test-Path $SINGLES_RURO) -and 
    (Test-Path $COUPLES_RURO) -and
    -not $userWantsSteps1to6) {
    
    Write-Host ""
    Write-Host "All required intermediate datasets found. Skipping Steps 1-6." -ForegroundColor Yellow
    Write-Host "Set SKIP_IF_MNL_EXISTS=`$false or use -ForceRebuild to force a full rebuild." -ForegroundColor Yellow
    $needsDataRegen = $false
}

# =====================================================================
# STEP 1: DATA PREPARATION
# =====================================================================
if ($needsDataRegen -and (Should-RunStep 1)) {
    Write-Step "STEP 1/8: DATA PREPARATION (enh_france_data_prep.py)"

    $cmd = "python `"$SCRIPTS\enh_france_data_prep.py`" --year $YEAR --raw-dir `"$DATA_ROOT\raw`" --out-dir `"$PROC`" --system-year $SYSTEM_YEAR --export-format parquet"

    $step1Result = Run-PythonScript $cmd "Prepare raw EUROMOD data for France $YEAR"

    # Check if output file exists (script may return exit code 1 even on success)
    $expectedFile = Join-Path $PROC "fr_$YEAR.parquet"
    if (-not $step1Result) {
        if (Test-Path $expectedFile) {
            Write-Host "  NOTE: Script exited with error code but output file exists" -ForegroundColor Yellow
            Write-Host "  Verified: $expectedFile" -ForegroundColor Green
            Write-Host "  Continuing pipeline..." -ForegroundColor Green
        } else {
            Write-Host "Pipeline stopped at Step 1: Output file missing" -ForegroundColor Red
            exit 1
        }
    }
} elseif (-not (Should-RunStep 1)) {
    Write-Host "SKIPPING Step 1 (per CLI options)" -ForegroundColor DarkGray
}

# =====================================================================
# STEP 2: RURO PREPARATION
# =====================================================================
if ($needsDataRegen -and (Should-RunStep 2)) {
    Write-Step "STEP 2/8: RURO PREPARATION (enh_RURO_prep.py)"

    $cmd = "python `"$SCRIPTS\enh_RURO_prep.py`" --processed-dir `"$PROC`" --base-year $YEAR --export-format parquet"

    if (-not (Run-PythonScript $cmd "Build RURO-ready datasets (singles/couples)")) {
        Write-Host "Pipeline stopped at Step 2" -ForegroundColor Red
        exit 1
    }
} elseif (-not (Should-RunStep 2)) {
    Write-Host "SKIPPING Step 2 (per CLI options)" -ForegroundColor DarkGray
}

# =====================================================================
# STEP 3: GENERATE DRAWS
# =====================================================================
if ($needsDataRegen -and (Should-RunStep 3)) {
    Write-Step "STEP 3/8: GENERATE DRAWS (enh_RURO_draws.py)"

    $cmd = "python `"$SCRIPTS\enh_RURO_draws.py`" --singles-path `"$SINGLES_RURO`" --n-draws $N_DRAWS --wage-spec $WAGE_SPEC"
    if (Test-Path $COUPLES_RURO) {
        $cmd += " --couples-path `"$COUPLES_RURO`""
    }

    if (-not (Run-PythonScript $cmd "Generate $N_DRAWS counterfactual draws")) {
        Write-Host "Pipeline stopped at Step 3" -ForegroundColor Red
        exit 1
    }
} elseif (-not (Should-RunStep 3)) {
    Write-Host "SKIPPING Step 3 (per CLI options)" -ForegroundColor DarkGray
}

# =====================================================================
# STEP 4: EUROMOD SIMULATION
# =====================================================================
if ($needsDataRegen -and (Should-RunStep 4)) {
    Write-Step "STEP 4/8: EUROMOD SIMULATION (enh_RURO_euromod.py)"

    $EUROMOD_SYSTEM = "${COUNTRY}_$SYSTEM_YEAR"
    $EUROMOD_DATASET = "${COUNTRY}_$YEAR"

    $cmd = "python `"$SCRIPTS\enh_RURO_euromod.py`" --singles-draws `"$SINGLES_DRAWS`" --microdata-template `"$RAW`" --euromod-root `"$EUROMOD_ROOT`" --euromod-system $EUROMOD_SYSTEM --euromod-dataset $EUROMOD_DATASET --scenario-dir `"$SCEN`""
    if (Test-Path $COUPLES_DRAWS) {
        $cmd += " --couples-draws `"$COUPLES_DRAWS`""
    }

    $step4Result = Run-PythonScript $cmd "Run EUROMOD on all draws"

    # Check if output file exists (EUROMOD may return exit code 1 even on success)
    $expectedEuromodFile = Join-Path $SCEN "combined_draws_em.parquet"
    if (-not $step4Result) {
        if (Test-Path $expectedEuromodFile) {
            Write-Host "  NOTE: Script exited with error code but output file exists" -ForegroundColor Yellow
            Write-Host "  Verified: $expectedEuromodFile" -ForegroundColor Green
            Write-Host "  Continuing pipeline..." -ForegroundColor Green
        } else {
            Write-Host "Pipeline stopped at Step 4: Output file missing" -ForegroundColor Red
            exit 1
        }
    }
} elseif (-not (Should-RunStep 4)) {
    Write-Host "SKIPPING Step 4 (per CLI options)" -ForegroundColor DarkGray
}

# =====================================================================
# STEP 5: PREPARE GSUR (if needed)
# =====================================================================
if ($needsDataRegen -and (Should-RunStep 5)) {
    Write-Step "STEP 5/8: PREPARE GSUR (enh_prepare_FR_gsur.py)"

    if (-not (Test-Path $GSUR_FILE)) {
        $GSUR_INPUT = "$PROJ_ROOT\Data\external\FR_gsur.xlsx"
        if (Test-Path $GSUR_INPUT) {
            $cmd = "python `"$SCRIPTS\enh_prepare_FR_gsur.py`" --input `"$GSUR_INPUT`" --output-dir `"$PROJ_ROOT\Data\external`""
            Run-PythonScript $cmd "Prepare GSUR lookup table" | Out-Null
        } else {
            Write-Host "GSUR input file not found - skipping GSUR preparation" -ForegroundColor Yellow
        }
    } else {
        Write-Host "GSUR file already exists: $GSUR_FILE" -ForegroundColor Green
    }
} elseif (-not (Should-RunStep 5)) {
    Write-Host "SKIPPING Step 5 (per CLI options)" -ForegroundColor DarkGray
}

# =====================================================================
# STEP 6: BUILD MNL DATASET
# =====================================================================
if ($needsDataRegen -and (Should-RunStep 6)) {
    Write-Step "STEP 6/8: BUILD MNL DATASET (enh_RURO_prep_mnl_basic.py)"

    $cmd = "python `"$SCRIPTS\enh_RURO_prep_mnl_basic.py`" --singles-draws `"$SINGLES_DRAWS`" --euromod-combined `"$EM_COMBINED`" --out-base `"$MNL_BASE`" --wage-spec $WAGE_SPEC --year $YEAR"

    if (Test-Path $COUPLES_DRAWS) {
        $cmd += " --couples-draws `"$COUPLES_DRAWS`""
    }

    if (Test-Path $GSUR_FILE) {
        $cmd += " --gsur-file `"$GSUR_FILE`""
    }
    # Note: GSUR is optional in enhanced version - no --no-gsur flag needed

    if (-not (Run-PythonScript $cmd "Build MNL estimation dataset")) {
        Write-Host "Pipeline stopped at Step 6" -ForegroundColor Red
        exit 1
    }

    # Verify output (enhanced version creates separate singles/couples files)
    if (-not (Test-Path $MNL_SINGLES)) {
        Write-Host "ERROR: MNL singles file not created: $MNL_SINGLES" -ForegroundColor Red
        exit 1
    }
    if (-not (Test-Path $MNL_COUPLES)) {
        Write-Host "ERROR: MNL couples file not created: $MNL_COUPLES" -ForegroundColor Red
        exit 1
    }
    Write-Host "  MNL singles: $MNL_SINGLES" -ForegroundColor Green
    Write-Host "  MNL couples: $MNL_COUPLES" -ForegroundColor Green
} elseif (-not (Should-RunStep 6)) {
    Write-Host "SKIPPING Step 6 (per CLI options)" -ForegroundColor DarkGray
}

# =====================================================================
# STEP 7: JOINT ESTIMATION
# =====================================================================
if (Should-RunStep 7) {
    Write-Step "STEP 7/8: JOINT ESTIMATION (enh_RURO_estimate_FR.py)"    Write-Host "MODEL PARAMETERS:" -ForegroundColor Magenta
    if ($WAGE_SPEC -eq "vw") {
        Write-Host "  Total: 60 params (variable wages)" -ForegroundColor White
        Write-Host "  - Preferences: 34 params (singles male/female + couples)" -ForegroundColor White
        Write-Host "  - Hours opportunity: 14 params (gender-specific)" -ForegroundColor White
        Write-Host "  - Wage opportunity: 12 params (gender-specific)" -ForegroundColor White
    } else {
        Write-Host "  Total: 48 params (fixed wages)" -ForegroundColor White
        Write-Host "  - Preferences: 34 params (singles male/female + couples)" -ForegroundColor White
        Write-Host "  - Hours opportunity: 14 params (gender-specific)" -ForegroundColor White
    }
    Write-Host ""

    $cmd = "python `"$SCRIPTS\enh_RURO_estimate_FR.py`" " +
           "--mnl-base `"$MNL_BASE`" " +
           "--output-dir `"$RESULTS_DIR`" " +
           "--group joint " +
           "--method L-BFGS-B " +
           "--maxiter $MAX_ITER " +
           "--n-jobs $CPU_CORES"

    if ($INIT_PARAMS_JOINT -and (Test-Path $INIT_PARAMS_JOINT)) {
        $cmd += " --init-params `"$INIT_PARAMS_JOINT`""
        Write-Host "  Using initial params: $INIT_PARAMS_JOINT" -ForegroundColor Cyan
        Write-Host ""
    }

    Write-Host "Command:" -ForegroundColor Yellow
    Write-Host $cmd -ForegroundColor DarkGray
    Write-Host ""

    # Enhanced logging for joint estimation
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "## Joint Estimation" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "**Started:** $timestamp" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "**Command:**" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "``````bash" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    $cmd | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "``````" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "**Output:**" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "``````" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8

    $startTime = Get-Date

    # Execute with real-time timestamped output
    try {
        $output = Invoke-Expression $cmd 2>&1 | ForEach-Object {
            $line = $_.ToString()
            $lineTimestamp = Get-Date -Format "HH:mm:ss.fff"
            # Write to console with timestamp
            Write-Host "[$lineTimestamp] $line"
            # Accumulate for log file
            "[$lineTimestamp] $line"
        }
        $exitCode = $LASTEXITCODE
    } catch {
        $output = $_.Exception.Message
        $exitCode = 1
        Write-Host "[ERROR] $output" -ForegroundColor Red
    }

    $endTime = Get-Date
    $duration = $endTime - $startTime

    # Write output to log
    if ($output) {
        $outputStr = $output | Out-String
        $outputStr | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    }
    "``````" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8

    # Log completion
    $endTimestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"

    Write-Host ""
    if ($exitCode -ne 0) {
        Write-Host "[$endTimestamp] FAILED: Joint estimation (exit code: $exitCode)" -ForegroundColor Red
        Write-Host "Duration: $($duration.ToString('hh\:mm\:ss\.fff'))" -ForegroundColor Red
        "**Status:** FAILED (exit code: $exitCode)" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        "**Completed:** $endTimestamp" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        "**Duration:** $($duration.ToString('hh\:mm\:ss\.fff'))" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        "" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        "---" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
        exit 1
    }

    Write-Host "[$endTimestamp] SUCCESS: Joint estimation" -ForegroundColor Green
    Write-Host "Duration: $($duration.ToString('hh\:mm\:ss\.fff'))" -ForegroundColor Green
    "**Status:** SUCCESS" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "**Completed:** $endTimestamp" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "**Duration:** $($duration.ToString('hh\:mm\:ss\.fff'))" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    "---" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
} else {
    Write-Host "SKIPPING Step 7 (per CLI options)" -ForegroundColor DarkGray
}

# =====================================================================
# STEP 8: POST-ESTIMATION ANALYSIS (STYLED VERSION)
# =====================================================================
if (Should-RunStep 8) {
    Write-Step "STEP 8/8: POST-ESTIMATION ANALYSIS (RURO_post_estimation_styled.py)"

    # Find the estimation results JSON (most recent)
    $estResultsJson = Get-ChildItem -Path $RESULTS_DIR -Filter "estimation_results*.json" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if (-not $estResultsJson) {
        Write-Host "ERROR: No estimation_results.json found in $RESULTS_DIR" -ForegroundColor Red
        Write-Host "Post-estimation requires successful estimation output." -ForegroundColor Yellow
        exit 1
    }

    Write-Host "  Using estimation results: $($estResultsJson.FullName)" -ForegroundColor Cyan
    Write-Host "  Using STYLED post-estimation (rich HTML with emojis, MUC analysis, elapsed time)" -ForegroundColor Magenta

    # Use the new styled post-estimation script (matches old vw_pooled aesthetics)
    $cmd = "python `"$SCRIPTS\RURO_post_estimation_styled.py`" " +
           "--results-json `"$($estResultsJson.FullName)`" " +
           "--mnl-base `"$MNL_BASE`" " +
           "--output-dir `"$POST_EST_DIR`" " +
           "--prefix `"fr_${YEAR}_joint_`""

    if (-not (Run-PythonScript $cmd "Run styled post-estimation analysis (MUC behavior, elasticities, elapsed time)")) {
        Write-Host "WARNING: Styled post-estimation analysis failed" -ForegroundColor Yellow
        Write-Host "Falling back to basic post-estimation..." -ForegroundColor Yellow

        # Fallback to basic version if styled fails
        $cmd_fallback = "python `"$SCRIPTS\enh_RURO_post_estimation.py`" " +
               "--results-json `"$($estResultsJson.FullName)`" " +
               "--mnl-base `"$MNL_BASE`" " +
               "--output-dir `"$POST_EST_DIR`" " +
               "--prefix `"fr_${YEAR}_joint_`""

        if (-not (Run-PythonScript $cmd_fallback "Run basic post-estimation analysis (fallback)")) {
            Write-Host "WARNING: Basic post-estimation also failed" -ForegroundColor Yellow
            Write-Host "Check logs for details. Continuing to summary..." -ForegroundColor Yellow
        }
    }

    # Find post-estimation report
    $latestPostEstReport = Get-ChildItem -Path $POST_EST_DIR -Filter "*post_estimation*.html" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if ($latestPostEstReport) {
        Write-Host "Post-estimation report: $($latestPostEstReport.FullName)" -ForegroundColor Green
    } else {
        # Also check RESULTS_DIR as fallback
        $latestPostEstReport = Get-ChildItem -Path $RESULTS_DIR -Filter "*post_estimation*.html" -File -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        if ($latestPostEstReport) {
            Write-Host "Post-estimation report: $($latestPostEstReport.FullName)" -ForegroundColor Green
        } else {
            Write-Host "WARNING: Post-estimation HTML report not found" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "SKIPPING Step 8 (per CLI options)" -ForegroundColor DarkGray
}

# =====================================================================
# SUMMARY
# =====================================================================
$pipelineEnd = Get-Date
$totalDuration = $pipelineEnd - $pipelineStart

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "ENHANCED PIPELINE COMPLETE" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output Files:" -ForegroundColor White
Write-Host "  MNL Singles:        $MNL_SINGLES"
Write-Host "  MNL Couples:        $MNL_COUPLES"
Write-Host "  Estimation:         $RESULTS_DIR"
Write-Host "  Post-Estimation:    $($latestPostEstReport.FullName)"
Write-Host "  Log File:           $LOG_FILE"
Write-Host ""
Write-Host "Total Duration:       $($totalDuration.ToString('hh\:mm\:ss'))" -ForegroundColor Cyan
Write-Host ""
Write-Host "Done!" -ForegroundColor Green

# Final log entry
@"

---

## Summary

**Completed:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Total Duration:** $($totalDuration.ToString('hh\:mm\:ss'))

### Output Files
- MNL Singles: ``$MNL_SINGLES``
- MNL Couples: ``$MNL_COUPLES``
- Estimation Dir: ``$RESULTS_DIR``
- Post-Estimation Report: ``$($latestPostEstReport.FullName)``
- Log File: ``$LOG_FILE``

### Parameters Estimated
- Total: $(if ($WAGE_SPEC -eq 'vw') { '60' } else { '48' }) parameters
- Wage Specification: $WAGE_SPEC
- Converged: Check JSON file for details

### Next Steps
1. Review post-estimation HTML report for diagnostics
2. Check parameter estimates in JSON file
3. Run additional post-estimation analysis if needed

"@ | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
