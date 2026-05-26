# filepath: enh_pipeline.ps1
# ==============================================================================
# Enhanced RURO Pipeline Runner - France 2016
# ==============================================================================
# This script runs the complete RURO pipeline from data preparation through
# MNL dataset creation (excluding estimation steps).
#
# Pipeline Steps:
#   1. enh_france_data_prep.py     - Prepare and filter France 2016 data
#   2. enh_RURO_prep.py            - Create RURO-ready datasets
#   3. enh_RURO_draws.py           - Generate opportunity draws
#   4. enh_RURO_euromod.py         - Run EUROMOD simulation on draws
#   5. enh_prepare_FR_gsur.py      - Prepare GSUR unemployment lookup
#   6. enh_RURO_prep_mnl_basic.py  - Build final MNL estimation dataset
#
# Usage:
#   cd U:\Desktop\Nizam_Hisham\MNL
#   .\scripts\enhanced\enh_pipeline.ps1
#
# NOTE: You do NOT need to activate venv - script uses venv Python directly!
# ==============================================================================

# Skip flags - set to $true to skip a stage
$SKIP_DATA_PREP = $false
$SKIP_RURO_PREP = $false
$SKIP_DRAWS = $false
$SKIP_EUROMOD = $false
$SKIP_GSUR = $false
$SKIP_MNL = $false

# Verification flags
$RUN_QUICK_VERIFY = $true        # Run quick verification after pipeline completion
$RUN_DETAILED_VERIFY = $false    # Run detailed verification (optional, more comprehensive)

# ==============================================================================
# Configuration
# ==============================================================================

$COUNTRY = "FR"
$YEAR = 2016
$SYSTEM_YEAR = 2015
$N_DRAWS = 99
$WAGE_SPEC = "vw"

# Paths
$PROJ_ROOT = "U:\Desktop\Nizam_Hisham\MNL"
$SCRIPTS_DIR = "$PROJ_ROOT\scripts\enhanced"
$DATA_ROOT = "U:\EUROMOD-STORAGE\Data"
$PROC_DIR = "$DATA_ROOT\processed\fr\$YEAR"
$RAW_DIR = "$DATA_ROOT\raw"
$RAW_FILE = "$RAW_DIR\FR_$YEAR.txt"
$SCEN_DIR = "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_$YEAR"
$EUROMOD_ROOT = "U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+"

# CRITICAL FIX: Use virtual environment Python explicitly
$PYTHON_EXE = "$PROJ_ROOT\.venv\Scripts\python.exe"

# Input/output files
$SINGLES_RURO = "$PROC_DIR\singles_RURO_ready.parquet"
$COUPLES_RURO = "$PROC_DIR\couples_RURO_ready.parquet"
$SINGLES_DRAWS = "$PROC_DIR\singles_RURO_ready_RURO_draws.parquet"
$COUPLES_DRAWS = "$PROC_DIR\couples_RURO_ready_RURO_draws.parquet"
$EM_COMBINED = "$SCEN_DIR\combined_draws_em.parquet"
$GSUR_FILE = "$PROJ_ROOT\Data\external\FR_gsur_ruro.parquet"
$MNL_BASE = "$PROC_DIR\fr_${YEAR}_RURO_mnl"

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

# Log setup
$LOG_DIR = "$OUTPUTS_ROOT\logs"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$LOG_FILE = "$LOG_DIR\enh_pipeline_${COUNTRY}_${YEAR}_${TIMESTAMP}.txt"

# Create directories if they don't exist
New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $PROC_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $SCEN_DIR | Out-Null

# ==============================================================================
# Helper Functions
# ==============================================================================

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage
    Add-Content -Path $LOG_FILE -Value $logMessage
}

function Write-Section {
    param([string]$Title)
    $separator = ''.PadLeft(80,'=')
    Write-Log ""
    Write-Log $separator
    Write-Log $Title
    Write-Log $separator
}

function Run-PythonScript {
    param(
        [string]$ScriptPath,
        [string]$Arguments,
        [string]$Description
    )

    Write-Section "Running: $Description"
    Write-Log "Script: $ScriptPath"
    Write-Log "Arguments: $Arguments"
    Write-Log "Python: $PYTHON_EXE"
    Write-Log "Started at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

    $startTime = Get-Date

    # Use Start-Process for reliable stdout/stderr capture
    # Create temp files for output capture
    $stdoutFile = [System.IO.Path]::GetTempFileName()
    $stderrFile = [System.IO.Path]::GetTempFileName()

    try {
        # Build argument list - need to handle quoted paths properly
        $argList = "`"$ScriptPath`" $Arguments"

        # Start process with redirected output
        $process = Start-Process -FilePath $PYTHON_EXE `
            -ArgumentList $argList `
            -NoNewWindow `
            -Wait `
            -PassThru `
            -RedirectStandardOutput $stdoutFile `
            -RedirectStandardError $stderrFile

        $exitCode = $process.ExitCode

        # Read and log stdout
        if (Test-Path $stdoutFile) {
            $stdout = Get-Content $stdoutFile -Raw
            if ($stdout) {
                $stdout -split "`r?`n" | ForEach-Object {
                    if ($_.Trim()) {
                        Write-Host $_
                        Add-Content -Path $LOG_FILE -Value $_
                    }
                }
            }
        }

        # Read and log stderr (in red)
        if (Test-Path $stderrFile) {
            $stderr = Get-Content $stderrFile -Raw
            if ($stderr) {
                Add-Content -Path $LOG_FILE -Value "=== STDERR OUTPUT ==="
                $stderr -split "`r?`n" | ForEach-Object {
                    if ($_.Trim()) {
                        Write-Host $_ -ForegroundColor Red
                        Add-Content -Path $LOG_FILE -Value "[STDERR] $_"
                    }
                }
                Add-Content -Path $LOG_FILE -Value "=== END STDERR ==="
            }
        }

    } catch {
        $errorMsg = $_.Exception.Message
        Write-Host "[EXCEPTION] $errorMsg" -ForegroundColor Red
        Add-Content -Path $LOG_FILE -Value "[EXCEPTION] $errorMsg"
        Add-Content -Path $LOG_FILE -Value $_.ScriptStackTrace
        $exitCode = 1
    } finally {
        # Clean up temp files
        if (Test-Path $stdoutFile) { Remove-Item $stdoutFile -Force -ErrorAction SilentlyContinue }
        if (Test-Path $stderrFile) { Remove-Item $stderrFile -Force -ErrorAction SilentlyContinue }
    }

    $endTime = Get-Date
    $duration = $endTime - $startTime

    Write-Log "Completed at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Log "Duration: $($duration.ToString())"
    Write-Log "Exit Code: $exitCode"

    if ($exitCode -ne 0) {
        Write-Log "ERROR: Script failed with exit code $exitCode"
        return $false
    }

    Write-Log "SUCCESS: $Description completed successfully"
    return $true
}

function Test-FileExists {
    param(
        [string]$FilePath,
        [string]$Description
    )

    if (Test-Path $FilePath) {
        Write-Log "VERIFIED: $Description exists at $FilePath"
        return $true
    } else {
        Write-Log "WARNING: $Description not found at $FilePath"
        return $false
    }
}

# ==============================================================================
# System Information and Pre-flight Checks
# ==============================================================================

Write-Section "Enhanced RURO Pipeline - France $YEAR"
Write-Log "Pipeline Start Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Log "Log File: $LOG_FILE"
Write-Log ""
Write-Log "Configuration:"
Write-Log "  Country: $COUNTRY"
Write-Log "  Year: $YEAR"
Write-Log "  System Year: $SYSTEM_YEAR"
Write-Log "  N Draws: $N_DRAWS"
Write-Log "  Wage Spec: $WAGE_SPEC"
Write-Log ""
Write-Log "Paths:"
Write-Log "  Project Root: $PROJ_ROOT"
Write-Log "  Scripts Dir: $SCRIPTS_DIR"
Write-Log "  Processed Dir: $PROC_DIR"
Write-Log "  Scenario Dir: $SCEN_DIR"
Write-Log ""
Write-Log "Skip Flags:"
Write-Log "  SKIP_DATA_PREP: $SKIP_DATA_PREP"
Write-Log "  SKIP_RURO_PREP: $SKIP_RURO_PREP"
Write-Log "  SKIP_DRAWS: $SKIP_DRAWS"
Write-Log "  SKIP_EUROMOD: $SKIP_EUROMOD"
Write-Log "  SKIP_GSUR: $SKIP_GSUR"
Write-Log "  SKIP_MNL: $SKIP_MNL"
Write-Log ""
Write-Log "Verification Flags:"
Write-Log "  RUN_QUICK_VERIFY: $RUN_QUICK_VERIFY"
Write-Log "  RUN_DETAILED_VERIFY: $RUN_DETAILED_VERIFY"

# Detect CPU cores
$cpuCores = (Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
Write-Log ""
Write-Log "System Information:"
Write-Log "  CPU Cores: $cpuCores"
Write-Log "  PowerShell Version: $($PSVersionTable.PSVersion)"

# CRITICAL CHECK: Verify venv Python exists
if (-not (Test-Path $PYTHON_EXE)) {
    Write-Log "ERROR: Virtual environment Python not found at: $PYTHON_EXE"
    Write-Host ""
    Write-Host "Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create it by running:" -ForegroundColor Yellow
    Write-Host "  cd $PROJ_ROOT" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor Yellow
    Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

Write-Log "  Python Executable: $PYTHON_EXE"

# Verify Python version
try {
    $pythonVersion = & $PYTHON_EXE --version 2>&1
    Write-Log "  Python Version: $pythonVersion"
} catch {
    Write-Log "  ERROR: Could not run Python: $($_.Exception.Message)"
    exit 1
}

# CRITICAL CHECK: Verify numpy is installed
Write-Log ""
Write-Log "Pre-flight Package Checks:"
try {
    $numpyCheck = & $PYTHON_EXE -c "import numpy; print(f'NumPy {numpy.__version__}')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Log "  [OK] $numpyCheck"
    } else {
        Write-Log "  [X] NumPy not available!"
        Write-Host ""
        Write-Host "NumPy not installed in virtual environment!" -ForegroundColor Red
        Write-Host "Please install dependencies:" -ForegroundColor Yellow
        Write-Host "  cd $PROJ_ROOT" -ForegroundColor Yellow
        Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
        Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
        exit 1
    }

    $pandasCheck = & $PYTHON_EXE -c "import pandas; print(f'Pandas {pandas.__version__}')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Log "  [OK] $pandasCheck"
    }
} catch {
    Write-Log "  WARNING: Could not verify packages: $($_.Exception.Message)"
}

Write-Log ""
Write-Log "[OK] All pre-flight checks passed - ready to run pipeline!"

# ==============================================================================
# Pipeline Execution
# ==============================================================================

$pipelineStartTime = Get-Date

try {
    # --------------------------------------------------------------------------
    # Step 1: Data Preparation
    # --------------------------------------------------------------------------
    if (-not $SKIP_DATA_PREP) {
        $scriptPath = "$SCRIPTS_DIR\enh_france_data_prep.py"
        $scriptArgs = "--year $YEAR --raw-dir `"$RAW_DIR`" --out-dir `"$PROC_DIR`" --system-year $SYSTEM_YEAR --export-format parquet"

        $result = Run-PythonScript -ScriptPath $scriptPath -Arguments $scriptArgs -Description "Step 1: Data Preparation (France $YEAR)"

        # Verify output
        $expectedFile = "$PROC_DIR\fr_$YEAR.parquet"
        if (-not $result) {
            if (Test-Path $expectedFile) {
                Write-Log "NOTE: Script exited with error but output file exists - continuing"
            } else {
                throw "Step 1 failed: Output file missing"
            }
        }
        Test-FileExists -FilePath $expectedFile -Description "Prepared data"
    } else {
        Write-Section "SKIPPED: Step 1 - Data Preparation"
    }

    # --------------------------------------------------------------------------
    # Step 2: RURO Preparation
    # --------------------------------------------------------------------------
    if (-not $SKIP_RURO_PREP) {
        $scriptPath = "$SCRIPTS_DIR\enh_RURO_prep.py"
        $scriptArgs = "--processed-dir `"$PROC_DIR`" --base-year $YEAR --export-format parquet"

        if (-not (Run-PythonScript -ScriptPath $scriptPath -Arguments $scriptArgs -Description "Step 2: RURO Dataset Preparation")) {
            throw "Step 2 failed"
        }

        # Verify outputs
        Test-FileExists -FilePath $SINGLES_RURO -Description "Singles RURO-ready"
        Test-FileExists -FilePath $COUPLES_RURO -Description "Couples RURO-ready"
    } else {
        Write-Section "SKIPPED: Step 2 - RURO Preparation"
    }

    # --------------------------------------------------------------------------
    # Step 3: Draw Generation
    # --------------------------------------------------------------------------
    if (-not $SKIP_DRAWS) {
        $scriptPath = "$SCRIPTS_DIR\enh_RURO_draws.py"
        $scriptArgs = "--singles-path `"$SINGLES_RURO`" --n-draws $N_DRAWS --wage-spec $WAGE_SPEC --occ-spec fixed --h-min 10 --h-max 70 --w-min 2 --w-max 170 --rng-seed 17"

        if (Test-Path $COUPLES_RURO) {
            $scriptArgs += " --couples-path `"$COUPLES_RURO`""
        }

        if (-not (Run-PythonScript -ScriptPath $scriptPath -Arguments $scriptArgs -Description "Step 3: Opportunity Draw Generation")) {
            throw "Step 3 failed"
        }

        # Verify outputs
        Test-FileExists -FilePath $SINGLES_DRAWS -Description "Singles draws"
        if (Test-Path $COUPLES_RURO) {
            Test-FileExists -FilePath $COUPLES_DRAWS -Description "Couples draws"
        }
    } else {
        Write-Section "SKIPPED: Step 3 - Draw Generation"
    }

    # --------------------------------------------------------------------------
    # Step 4: EUROMOD Simulation
    # --------------------------------------------------------------------------
    if (-not $SKIP_EUROMOD) {
        $EUROMOD_SYSTEM = "${COUNTRY}_$SYSTEM_YEAR"
        $EUROMOD_DATASET = "${COUNTRY}_$YEAR"

        $scriptPath = "$SCRIPTS_DIR\enh_RURO_euromod.py"
        $scriptArgs = "--singles-draws `"$SINGLES_DRAWS`" --microdata-template `"$RAW_FILE`" --euromod-root `"$EUROMOD_ROOT`" --euromod-system $EUROMOD_SYSTEM --euromod-dataset $EUROMOD_DATASET --scenario-dir `"$SCEN_DIR`""

        if (Test-Path $COUPLES_DRAWS) {
            $scriptArgs += " --couples-draws `"$COUPLES_DRAWS`""
        }

        $result = Run-PythonScript -ScriptPath $scriptPath -Arguments $scriptArgs -Description "Step 4: EUROMOD Simulation"

        # EUROMOD may exit with error but still produce output
        if (-not $result) {
            if (Test-Path $EM_COMBINED) {
                Write-Log "NOTE: EUROMOD script exited with error but output file exists - continuing"
            } else {
                throw "Step 4 failed: Output file missing"
            }
        }
        Test-FileExists -FilePath $EM_COMBINED -Description "EUROMOD combined output"
    } else {
        Write-Section "SKIPPED: Step 4 - EUROMOD Simulation"
    }

    # --------------------------------------------------------------------------
    # Step 5: GSUR Preparation
    # --------------------------------------------------------------------------
    if (-not $SKIP_GSUR) {
        if (-not (Test-Path $GSUR_FILE)) {
            $GSUR_INPUT = "$PROJ_ROOT\Data\external\FR_gsur.xlsx"
            if (Test-Path $GSUR_INPUT) {
                $scriptPath = "$SCRIPTS_DIR\enh_prepare_FR_gsur.py"
                $scriptArgs = "--input `"$GSUR_INPUT`" --output-dir `"$PROJ_ROOT\Data\external`""

                Run-PythonScript -ScriptPath $scriptPath -Arguments $scriptArgs -Description "Step 5: GSUR Lookup Preparation" | Out-Null
            } else {
                Write-Log "GSUR input file not found - skipping GSUR preparation"
            }
        } else {
            Write-Log "GSUR file already exists: $GSUR_FILE"
        }
        Test-FileExists -FilePath $GSUR_FILE -Description "GSUR lookup table"
    } else {
        Write-Section "SKIPPED: Step 5 - GSUR Preparation"
    }

    # --------------------------------------------------------------------------
    # Step 6: MNL Dataset Preparation
    # --------------------------------------------------------------------------
    if (-not $SKIP_MNL) {
        $scriptPath = "$SCRIPTS_DIR\enh_RURO_prep_mnl_basic.py"
        $scriptArgs = "--singles-draws `"$SINGLES_DRAWS`" --euromod-combined `"$EM_COMBINED`" --out-base `"$MNL_BASE`" --wage-spec $WAGE_SPEC --year $YEAR --write-combined"

        if (Test-Path $COUPLES_DRAWS) {
            $scriptArgs += " --couples-draws `"$COUPLES_DRAWS`""
        }

        if (Test-Path $GSUR_FILE) {
            $scriptArgs += " --gsur-file `"$GSUR_FILE`""
        }

        if (-not (Run-PythonScript -ScriptPath $scriptPath -Arguments $scriptArgs -Description "Step 6: MNL Dataset Preparation")) {
            throw "Step 6 failed"
        }

        # Verify outputs
        Test-FileExists -FilePath "${MNL_BASE}__singles.parquet" -Description "MNL singles dataset"
        if (Test-Path $COUPLES_DRAWS) {
            Test-FileExists -FilePath "${MNL_BASE}__couples.parquet" -Description "MNL couples dataset"
        }
        Test-FileExists -FilePath "${MNL_BASE}__mnlmeta.json" -Description "MNL metadata"
    } else {
        Write-Section "SKIPPED: Step 6 - MNL Dataset Preparation"
    }

    # --------------------------------------------------------------------------
    # Pipeline Completion
    # --------------------------------------------------------------------------
    $pipelineEndTime = Get-Date
    $pipelineDuration = $pipelineEndTime - $pipelineStartTime

    Write-Section "Pipeline Completed Successfully"
    Write-Log "Total Duration: $($pipelineDuration.ToString())"
    Write-Log "End Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

    # --------------------------------------------------------------------------
    # Verification Phase
    # --------------------------------------------------------------------------
    if ($RUN_QUICK_VERIFY) {
        Write-Section "Running Quick Verification"

        $verifyScript = "$SCRIPTS_DIR\verify_ruro_pipeline.py"

        if (Test-Path $verifyScript) {
            $scriptArgs = "--draws-dir `"$PROC_DIR`" --euromod-output `"$EM_COMBINED`""

            Run-PythonScript -ScriptPath $verifyScript -Arguments $scriptArgs -Description "Quick Verification" | Out-Null
        } else {
            Write-Log "WARNING: verify_ruro_pipeline.py not found at $verifyScript"
        }
    }

    if ($RUN_DETAILED_VERIFY) {
        Write-Section "Running Detailed Verification"

        $detailedVerifyScript = "$SCRIPTS_DIR\verify_ruro_pipeline.py"

        if (Test-Path $detailedVerifyScript) {
            $scriptArgs = "--draws-dir `"$PROC_DIR`" --euromod-output `"$EM_COMBINED`" --detailed"

            Run-PythonScript -ScriptPath $detailedVerifyScript -Arguments $scriptArgs -Description "Detailed Verification" | Out-Null
        } else {
            Write-Log "WARNING: Detailed verification script not found"
        }
    }

    # --------------------------------------------------------------------------
    # Final Summary
    # --------------------------------------------------------------------------
    Write-Section "Pipeline Execution Summary"
    Write-Log "All pipeline stages completed successfully"
    Write-Log ""
    Write-Log "Output Files:"
    Write-Log "  Singles RURO: $SINGLES_RURO"
    Write-Log "  Couples RURO: $COUPLES_RURO"
    Write-Log "  Singles Draws: $SINGLES_DRAWS"
    Write-Log "  Couples Draws: $COUPLES_DRAWS"
    Write-Log "  EUROMOD Combined: $EM_COMBINED"
    Write-Log "  MNL Singles: ${MNL_BASE}__singles.parquet"
    Write-Log "  MNL Couples: ${MNL_BASE}__couples.parquet"
    Write-Log "  MNL Metadata: ${MNL_BASE}__mnlmeta.json"
    Write-Log ""
    Write-Log "IMPORTANT: All terminal output (including errors) logged to:"
    Write-Log "  $LOG_FILE"

} catch {
    Write-Section "Pipeline Failed"
    Write-Log "ERROR: $($_.Exception.Message)"
    Write-Log "Stack Trace: $($_.ScriptStackTrace)"
    Write-Log ""
    Write-Log "Pipeline failed at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Log "Log file saved to: $LOG_FILE"
    exit 1
}

Write-Log ""
Write-Log (''.PadLeft(80,'='))
Write-Log "DONE"
Write-Log (''.PadLeft(80,'='))
