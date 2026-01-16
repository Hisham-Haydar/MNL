# =====================================================================
# DETAILED ESTIMATION RUN WITH FULL LOGGING
# =====================================================================
# This script runs the estimation with detailed iteration-by-iteration
# output captured to a timestamped log file.
#
# Author: MNL Estimation Team
# Date: 2026-01-08
# =====================================================================

param(
    [string]$Country = "fr",
    [string]$Year = "2016",
    [string]$Group = "joint",
    [int]$MaxIter = 10000
)

# Configuration
$PROJ_ROOT = "U:\Desktop\Nizam_Hisham\MNL"
$PYTHON_EXE = "$PROJ_ROOT\.venv\Scripts\python.exe"
$SCRIPT_PATH = "$PROJ_ROOT\scripts\enhanced\enh_RURO_estimate_FR.py"
$SPEC_PATH = "$PROJ_ROOT\scripts\enhanced\estimation_spec.yaml"
$MNL_BASE = "U:/EUROMOD-STORAGE/Data/processed/$Country/$Year/${Country}_${Year}_RURO_mnl"
$OUTPUT_DIR = "$PROJ_ROOT\outputs\estimates\$Country\$Year"
$LOG_DIR = "$PROJ_ROOT\outputs\logs"

# Create directories
New-Item -ItemType Directory -Force -Path $OUTPUT_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null

# Generate timestamped log filename
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$LOG_FILE = "$LOG_DIR\estimation_${Country}_${Year}_${Group}_${TIMESTAMP}.txt"

# Helper function to write timestamped log entries
function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Write-Host $logEntry -ForegroundColor $Color
    $logEntry | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
}

# Banner
Write-Log "================================================================================" "Cyan"
Write-Log "RURO MNL ESTIMATION - DETAILED RUN" "Cyan"
Write-Log "================================================================================" "Cyan"
Write-Log ""
Write-Log "Configuration:"
Write-Log "  Country: $Country"
Write-Log "  Year: $Year"
Write-Log "  Group: $Group"
Write-Log "  Max Iterations: $MaxIter"
Write-Log ""
Write-Log "Paths:"
Write-Log "  Python: $PYTHON_EXE"
Write-Log "  Script: $SCRIPT_PATH"
Write-Log "  Spec: $SPEC_PATH"
Write-Log "  MNL Base: $MNL_BASE"
Write-Log "  Output: $OUTPUT_DIR"
Write-Log ""
Write-Log "Log File: $LOG_FILE"
Write-Log ""

# Build command
$cmd = "& `"$PYTHON_EXE`" `"$SCRIPT_PATH`" " +
       "--mnl-base `"$MNL_BASE`" " +
       "--output-dir `"$OUTPUT_DIR`" " +
       "--group $Group " +
       "--method L-BFGS-B " +
       "--maxiter $MaxIter " +
       "--spec-config `"$SPEC_PATH`" " +
       "--verbose"

Write-Log "================================================================================" "Cyan"
Write-Log "Starting Estimation" "Cyan"
Write-Log "================================================================================" "Cyan"
Write-Log "Command: $cmd"
Write-Log ""
Write-Log "Started at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "Green"
Write-Log ""

# Capture start time
$startTime = Get-Date

# Run the command and capture all output to log file
try {
    # Use Start-Process with redirection to capture all output
    Invoke-Expression $cmd 2>&1 | ForEach-Object {
        $line = $_.ToString()
        Write-Host $line
        $line | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
    }

    $exitCode = $LASTEXITCODE
} catch {
    $exitCode = 1
    Write-Log ""
    Write-Log "ERROR: $($_.Exception.Message)" "Red"
}

# Capture end time
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Log ""
Write-Log "================================================================================" "Cyan"
if ($exitCode -eq 0) {
    Write-Log "ESTIMATION COMPLETED SUCCESSFULLY" "Green"
} else {
    Write-Log "ESTIMATION FAILED" "Red"
}
Write-Log "================================================================================" "Cyan"
Write-Log "Completed at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Log "Duration: $($duration.ToString('hh\:mm\:ss'))"
Write-Log "Exit Code: $exitCode"
Write-Log ""
Write-Log "Log saved to: $LOG_FILE"
Write-Log "Results saved to: $OUTPUT_DIR"
Write-Log ""

# Display convergence diagnostics if available
$resultsJson = "$OUTPUT_DIR\estimation_results.json"
if (Test-Path $resultsJson) {
    Write-Log "================================================================================" "Cyan"
    Write-Log "CONVERGENCE SUMMARY" "Cyan"
    Write-Log "================================================================================" "Cyan"

    $results = Get-Content $resultsJson | ConvertFrom-Json

    foreach ($grp in @("singles_male", "singles_female", "couples")) {
        if ($results.results.$grp) {
            $r = $results.results.$grp
            Write-Log ""
            Write-Log "Group: $grp" "Yellow"
            Write-Log "  Final Log-Likelihood: $($r.final_ll)"
            Write-Log "  Iterations: $($r.n_iterations)"
            Write-Log "  Function Evaluations: $($r.n_function_evals)"

            if ($r.convergence_diagnostics) {
                $diag = $r.convergence_diagnostics
                Write-Log "  Gradient Norm (Full): $($diag.gradient_norm_full)"
                Write-Log "  Gradient Norm (Projected): $($diag.gradient_norm_projected)"
                Write-Log "  Gradient Inf-Norm (Full): $($diag.gradient_inf_norm_full)"
                Write-Log "  Gradient Inf-Norm (Projected): $($diag.gradient_inf_norm_projected)"
            }
        }
    }
    Write-Log ""
}

exit $exitCode
