#Requires -Version 5.1
<#
.SYNOPSIS
    Sync local EUROMOD-STORAGE data to the UNC backup share.

.DESCRIPTION
    Mirrors the canonical local store (C:\Users\hisham\MNL\EUROMOD-STORAGE) to
    \\crc\users\hisham\MNL_backup\EUROMOD-STORAGE using robocopy. The default job
    set covers the DATA only: Data\ (processed/pooled, raw, FR, DE, interim,
    inspecting), new_data\ (bpool), outputs\, reports\. robocopy copies only
    changed files, so repeat syncs are fast.

    NOT backed up: the EUROMOD system itself (Euromod_model\, currently
    EUROMOD_RELEASES_J2.0+) - it is re-downloadable software, not data. Use -All
    to include everything under EUROMOD-STORAGE if you want a full mirror.

    - Called automatically at the end of estimation runs (enh_RURO_estimate_FR.py)
    - Can also be run manually from the project root:
          .\scripts\sync_backup.ps1
    - Source and destination are read from ~/.mnl/config.yaml if pyyaml is available,
      otherwise fall back to hardcoded defaults below.

.PARAMETER DryRun
    Print what would be synced without copying anything.

.PARAMETER All
    Sync everything under EUROMOD-STORAGE (not just Data/). Useful for a full backup.

.EXAMPLE
    .\scripts\sync_backup.ps1
    .\scripts\sync_backup.ps1 -DryRun
    .\scripts\sync_backup.ps1 -All
#>
param(
    [switch]$DryRun,
    [switch]$All
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Resolve paths from ~/.mnl/config.yaml or defaults
# ---------------------------------------------------------------------------
$configPath = Join-Path $env:USERPROFILE ".mnl\config.yaml"
$localRoot  = ""
$backupRoot = ""

if (Test-Path $configPath) {
    $lines = Get-Content $configPath
    foreach ($line in $lines) {
        if ($line -match '^\s*storage_root\s*:\s*(.+)$') {
            $localRoot = $Matches[1].Trim().Replace('/', '\')
        }
        if ($line -match '^\s*backup_root\s*:\s*(.+)$') {
            $raw = $Matches[1].Trim().Replace('/', '\')
            $backupRoot = Join-Path $raw "EUROMOD-STORAGE"
        }
    }
}

if (-not $localRoot) {
    Write-Error "storage_root not set. Add 'storage_root: /path/to/EUROMOD-STORAGE' to $configPath"
    exit 1
}
if (-not $backupRoot) {
    Write-Error "backup_root not set. Add 'backup_root: //server/share/MNL_backup' to $configPath"
    exit 1
}

Write-Host ""
Write-Host "=== RURO MNL - Backup Sync ===" -ForegroundColor Cyan
Write-Host "  Source : $localRoot"
Write-Host "  Dest   : $backupRoot"
if ($DryRun) { Write-Host "  Mode   : DRY RUN (no files will be copied)" -ForegroundColor Yellow }
Write-Host ""

# ---------------------------------------------------------------------------
# Check backup destination is reachable
# ---------------------------------------------------------------------------
$backupParent = Split-Path $backupRoot -Parent     # ...\MNL_backup
$shareRoot    = Split-Path $backupParent -Parent   # ...\hisham (the reachable network share)
if (-not (Test-Path $shareRoot -ErrorAction SilentlyContinue)) {
    Write-Warning "Backup share not reachable: $shareRoot"
    Write-Warning "Skipping backup sync. Connect to the CRC network and retry."
    exit 0
}
if (-not (Test-Path $backupParent)) {
    New-Item -ItemType Directory -Path $backupParent -Force | Out-Null
    Write-Host "Created backup root: $backupParent" -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# Determine what to sync
# ---------------------------------------------------------------------------
$robocopyFlags = @("/E", "/COPY:DAT", "/R:3", "/W:5", "/NP", "/NDL")
if ($DryRun) { $robocopyFlags += "/L" }

if ($All) {
    $syncJobs = @(
        @{src = $localRoot; dst = $backupRoot; label = "Full EUROMOD-STORAGE"}
    )
} else {
    $syncJobs = @(
        @{src = "$localRoot\Data";     dst = "$backupRoot\Data";     label = "Data (processed/pooled, raw, FR, DE, interim, inspecting)"},
        @{src = "$localRoot\new_data"; dst = "$backupRoot\new_data"; label = "new_data (bpool)"},
        @{src = "$localRoot\outputs";  dst = "$backupRoot\outputs";  label = "outputs"},
        @{src = "$localRoot\reports";  dst = "$backupRoot\reports";  label = "reports"}
    )
}

# ---------------------------------------------------------------------------
# Run sync jobs
# ---------------------------------------------------------------------------
$totalCopied = 0
$startTime   = Get-Date

foreach ($job in $syncJobs) {
    if (-not (Test-Path $job.src)) {
        Write-Host "  [SKIP] $($job.label) - source does not exist: $($job.src)" -ForegroundColor DarkGray
        continue
    }
    Write-Host "  [SYNC] $($job.label) ..." -NoNewline

    $logFile = Join-Path $env:TEMP "mnl_sync_$($job.label -replace '[/\\: ]','_').log"
    $result  = robocopy $job.src $job.dst @robocopyFlags /LOG:$logFile 2>&1

    # robocopy exit codes: 0=nothing to do, 1=copied, 2=extra in dest, 3=both, >=8=error
    if ($LASTEXITCODE -ge 8) {
        Write-Host " ERROR (exit $LASTEXITCODE)" -ForegroundColor Red
        Write-Host "    Log: $logFile"
    } else {
        # Parse file count from log
        $logContent = Get-Content $logFile -ErrorAction SilentlyContinue
        # robocopy summary line: "   Files :  <Total>  <Copied>  <Skipped> ..."  -> capture 2nd column
        $filesLine  = $logContent | Select-String '^\s*Files :' | Select-Object -Last 1
        $copiedNum  = if ($filesLine -and $filesLine.Line -match 'Files :\s+\d+\s+(\d+)') { [int]$Matches[1] } else { 0 }
        $totalCopied += $copiedNum
        Write-Host " done ($copiedNum files)" -ForegroundColor Green
    }
}

$elapsed = (Get-Date) - $startTime
Write-Host ""
Write-Host "Sync complete - $totalCopied files copied in $([math]::Round($elapsed.TotalSeconds,1))s" -ForegroundColor Cyan
if ($DryRun) { Write-Host "(Dry run - no files were actually copied)" -ForegroundColor Yellow }
