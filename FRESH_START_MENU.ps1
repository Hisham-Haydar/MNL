# ==========================================
# FRESH START - Quick Command Reference
# ==========================================

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "FRESH START - Ready to Run" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "Column Reduction Status:" -ForegroundColor Yellow
Write-Host "  ✓ EUROMOD reduced: 465.2 MB → 63.4 MB (86.4% savings)" -ForegroundColor Green
Write-Host "  ✓ Columns reduced: 342 → 27 (92.1% reduction)" -ForegroundColor Green
Write-Host "  ✓ File location: U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016_reduced/`n" -ForegroundColor Green

Write-Host "Choose your action:`n" -ForegroundColor Yellow

Write-Host "[1] Run Step 6 (MNL Dataset Creation) with REDUCED files" -ForegroundColor White
Write-Host "    Fast: Uses 63.4 MB file instead of 465.2 MB`n" -ForegroundColor Gray

Write-Host "[2] Analyze draws files (check if they need reduction too)" -ForegroundColor White
Write-Host "    Optional: See what's in the draws files`n" -ForegroundColor Gray

Write-Host "[3] Run Step 6 + Step 7 (Complete pipeline)" -ForegroundColor White
Write-Host "    Full run: MNL dataset creation → Estimation`n" -ForegroundColor Gray

Write-Host "[4] Check file sizes and verify setup" -ForegroundColor White
Write-Host "    Verification: Confirm all files are ready`n" -ForegroundColor Gray

$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`n=== Running Step 6 with REDUCED EUROMOD file ===" -ForegroundColor Cyan
        python scripts\enhanced\enh_RURO_prep_mnl_basic.py `
            --singles-draws U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_RURO_draws.parquet `
            --euromod-combined U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016_reduced/combined_draws_em.parquet `
            --out-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
            --wage-spec vw `
            --year 2016 `
            --couples-draws U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_RURO_draws.parquet `
            --gsur-file U:/Desktop/Nizam_Hisham/MNL/Data/external/FR_gsur_ruro.parquet
    }
    
    "2" {
        Write-Host "`n=== Analyzing Draws Files ===" -ForegroundColor Cyan
        python analyze_draws_files.py
    }
    
    "3" {
        Write-Host "`n=== Running Complete Pipeline ===" -ForegroundColor Cyan
        Write-Host "Step 6: MNL Dataset Creation..." -ForegroundColor Yellow
        python scripts\enhanced\enh_RURO_prep_mnl_basic.py `
            --singles-draws U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_RURO_draws.parquet `
            --euromod-combined U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016_reduced/combined_draws_em.parquet `
            --out-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
            --wage-spec vw `
            --year 2016 `
            --couples-draws U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_RURO_draws.parquet `
            --gsur-file U:/Desktop/Nizam_Hisham/MNL/Data/external/FR_gsur_ruro.parquet
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`nStep 7: Running Estimation..." -ForegroundColor Yellow
            python scripts\enhanced\enh_RURO_estimate_FR.py `
                --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
                --output-dir outputs/estimation/FR_2016 `
                --group joint `
                --n-jobs 4
        } else {
            Write-Host "`n✗ Step 6 failed. Not running Step 7." -ForegroundColor Red
        }
    }
    
    "4" {
        Write-Host "`n=== Verifying Setup ===" -ForegroundColor Cyan
        
        Write-Host "`nEUROMOD Files:" -ForegroundColor Yellow
        $original = "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016\combined_draws_em.parquet"
        $reduced = "U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016_reduced\combined_draws_em.parquet"
        
        if (Test-Path $original) {
            $size = (Get-Item $original).Length / 1MB
            Write-Host "  ✓ Original: $([math]::Round($size,1)) MB" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Original: NOT FOUND" -ForegroundColor Red
        }
        
        if (Test-Path $reduced) {
            $size = (Get-Item $reduced).Length / 1MB
            Write-Host "  ✓ Reduced: $([math]::Round($size,1)) MB" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Reduced: NOT FOUND" -ForegroundColor Red
        }
        
        Write-Host "`nDraws Files:" -ForegroundColor Yellow
        $singles = "U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready_RURO_draws.parquet"
        $couples = "U:\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet"
        
        if (Test-Path $singles) {
            $size = (Get-Item $singles).Length / 1MB
            Write-Host "  ✓ Singles: $([math]::Round($size,1)) MB" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Singles: NOT FOUND" -ForegroundColor Red
        }
        
        if (Test-Path $couples) {
            $size = (Get-Item $couples).Length / 1MB
            Write-Host "  ✓ Couples: $([math]::Round($size,1)) MB" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Couples: NOT FOUND" -ForegroundColor Red
        }
        
        Write-Host "`nGSUR File:" -ForegroundColor Yellow
        $gsur = "U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur_ruro.parquet"
        if (Test-Path $gsur) {
            $size = (Get-Item $gsur).Length / 1KB
            Write-Host "  ✓ GSUR: $([math]::Round($size,1)) KB" -ForegroundColor Green
        } else {
            Write-Host "  ✗ GSUR: NOT FOUND" -ForegroundColor Red
        }
        
        Write-Host "`nPython Processes:" -ForegroundColor Yellow
        $pythonProcs = Get-Process python -ErrorAction SilentlyContinue
        if ($pythonProcs) {
            Write-Host "  ⚠ $($pythonProcs.Count) Python process(es) running" -ForegroundColor Yellow
        } else {
            Write-Host "  ✓ No Python processes running" -ForegroundColor Green
        }
    }
    
    default {
        Write-Host "`n✗ Invalid choice. Please run again and choose 1-4." -ForegroundColor Red
    }
}

Write-Host "`n============================================" -ForegroundColor Cyan
