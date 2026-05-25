# Launches bpool EUROMOD chunk jobs one file at a time with concurrency limit.
# Each EUROMOD chunk peaks around 7-10 GB RAM during .NET+pandas pipeline,
# so we gate to 2 concurrent per file to stay well under the 199 GB free.
$py     = "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe"
$script = "U:\Desktop\Nizam_Hisham\MNL\scripts\bpool\run_bpool_euromod_chunk.py"
$logdir = "U:\EUROMOD-STORAGE\new_data\chunks"
$maxConcurrent = 2

# Build couples bands (6 chunks, draws 0..899 in bands of 150)
function Make-CouplesBands {
    $bands = [System.Collections.ArrayList]@()
    for ($i = 0; $i -lt 6; $i++) {
        $null = $bands.Add(@{ lo = $i * 150; hi = ($i + 1) * 150; ci = $i })
    }
    return ,$bands
}
$couplesBands = Make-CouplesBands

$files = @(
    @{ year=2015; mode="singles"; chunks=@(@{lo=0;hi=101;ci=0}) },
    @{ year=2015; mode="couples"; chunks=$couplesBands },
    @{ year=2016; mode="couples"; chunks=$couplesBands },
    @{ year=2017; mode="couples"; chunks=$couplesBands }
)

foreach ($f in $files) {
    $year = $f.year; $mode = $f.mode
    Write-Host ""
    Write-Host "===== $year $mode ====="

    # Check if all chunks already done
    $allDone = $true
    foreach ($c in $f.chunks) {
        $ci = $c.ci
        $out = "$logdir\fr_p3a_bpool_priced__${year}__${mode}__c${ci}.parquet"
        if (-not (Test-Path $out)) { $allDone = $false; break }
    }
    if ($allDone) {
        Write-Host "  All chunks already done - skipping."
        continue
    }

    # Launch chunks with concurrency limit
    $pending = @()
    foreach ($c in $f.chunks) {
        $ci = $c.ci
        $out = "$logdir\fr_p3a_bpool_priced__${year}__${mode}__c${ci}.parquet"
        if (Test-Path $out) {
            Write-Host "  chunk $ci already done - skip"
            continue
        }
        $pending += ,$c
    }

    if ($pending.Count -eq 0) {
        Write-Host "  No new chunks to launch."
        continue
    }

    Write-Host "  Running $($pending.Count) chunk(s), max $maxConcurrent concurrent..."
    $active = @()
    $pendingIdx = 0
    while ($pendingIdx -lt $pending.Count -or $active.Count -gt 0) {
        # Launch until we hit the concurrency cap
        while ($active.Count -lt $maxConcurrent -and $pendingIdx -lt $pending.Count) {
            $c = $pending[$pendingIdx]
            $lo = $c.lo; $hi = $c.hi; $ci = $c.ci
            $logfile = "$logdir\log_${year}_${mode}_c${ci}.txt"
            $errfile = "$logdir\err_${year}_${mode}_c${ci}.txt"
            Set-Content $logfile ""
            Set-Content $errfile ""

            $argList = "`"$script`" --year $year --mode $mode --draw-lo $lo --draw-hi $hi --chunk-id $ci"
            $p = Start-Process -FilePath $py -ArgumentList $argList `
                -RedirectStandardOutput $logfile `
                -RedirectStandardError  $errfile `
                -WindowStyle Hidden -PassThru
            $active += $p
            Write-Host "  LAUNCHED chunk $ci  draw=[$lo,$hi)  PID=$($p.Id)  (active=$($active.Count))"
            $pendingIdx++
        }

        # Poll every 10 sec for any active process to finish
        if ($active.Count -gt 0) {
            Start-Sleep -Seconds 10
            $stillActive = @()
            foreach ($p in $active) {
                if ($p.HasExited) {
                    $mins = [math]::Round(($p.ExitTime - $p.StartTime).TotalMinutes, 1)
                    Write-Host "  EXITED PID=$($p.Id) after $mins min"
                } else {
                    $stillActive += $p
                }
            }
            $active = $stillActive
        }
    }

    # Success = output parquet exists. ExitCode is unreliable with -WindowStyle Hidden.
    $anyFail = $false
    foreach ($c in $f.chunks) {
        $ci = $c.ci
        $out = "$logdir\fr_p3a_bpool_priced__${year}__${mode}__c${ci}.parquet"
        if (Test-Path $out) {
            $sz = [math]::Round((Get-Item $out).Length / 1MB, 1)
            Write-Host "  chunk $ci -> OK (${sz} MB)"
        } else {
            Write-Host "  chunk $ci -> FAIL (no output parquet)"
            $anyFail = $true
        }
    }

    if ($anyFail) {
        Write-Host "  ERRORS in $year $mode - check err_*.txt files. Stopping."
        exit 1
    }
    Write-Host "  $year $mode DONE."
}

Write-Host ""
Write-Host "All files processed. Run assemble_bpool_priced.py to assemble final parquets."
