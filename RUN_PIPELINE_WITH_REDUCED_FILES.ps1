# RUN THIS - Simple Commands to Continue
# (Ignore the 27 orphaned Python processes - they won't interfere)

Write-Host @"

================================================================================
OPTIMIZED PIPELINE - READY TO RUN! ✅
================================================================================

Optimizations enabled:
  ✅ Reduced EUROMOD file (63.4 MB instead of 465.2 MB - 86% savings!)
  ✅ Column filtering in Step 6 (~100 essential columns instead of 641)
  ✅ Expected MNL dataset size: ~90 MB (instead of ~700 MB)
  ✅ Expected speedup: 2-3x faster overall!

Output will be:
  - Singles MNL: ~40 MB, ~100 columns (instead of 300 MB, 641 columns)
  - Couples MNL: ~50 MB, ~100 columns (instead of 400 MB, 650 columns)
  - Total storage savings: ~85-90%!

================================================================================
NEXT STEP: Choose what to run
================================================================================

"@ -ForegroundColor Cyan

$choice = Read-Host @"

Choose an option:
  1) Run Step 6 (MNL dataset creation) with REDUCED EUROMOD file
  2) Run full pipeline (Step 6 + Step 7 estimation)
  3) Just show me the commands (don't run anything)
  4) Exit

Enter choice (1-4)
"@

switch ($choice) {
    "1" {
        Write-Host "`n=== Running Step 6 with REDUCED EUROMOD file ===" -ForegroundColor Green
        Write-Host "Expected: 2-3x faster than with full EUROMOD file!`n" -ForegroundColor Yellow
        
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
        Write-Host "`n=== Running FULL PIPELINE (Step 6 + Step 7) ===" -ForegroundColor Green
        Write-Host "Step 6: MNL dataset creation (with REDUCED EUROMOD)" -ForegroundColor Yellow
        Write-Host "Step 7: Joint estimation (singles + couples)`n" -ForegroundColor Yellow
        
        # Step 6
        python scripts\enhanced\enh_RURO_prep_mnl_basic.py `
            --singles-draws U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_RURO_draws.parquet `
            --euromod-combined U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016_reduced/combined_draws_em.parquet `
            --out-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
            --wage-spec vw `
            --year 2016 `
            --couples-draws U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_RURO_draws.parquet `
            --gsur-file U:/Desktop/Nizam_Hisham/MNL/Data/external/FR_gsur_ruro.parquet
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✓ Step 6 complete! Starting Step 7...`n" -ForegroundColor Green
            
            # Step 7
            python scripts\enhanced\enh_RURO_estimate_FR.py `
                --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
                --output-dir outputs/estimation/FR_2016 `
                --group joint `
                --n-jobs 4
        } else {
            Write-Host "`n✗ Step 6 failed - not running Step 7`n" -ForegroundColor Red
        }
    }
    
    "3" {
        Write-Host "`n=== COMMANDS TO RUN ===" -ForegroundColor Cyan
        Write-Host @"

# Step 6: Create MNL dataset (with REDUCED EUROMOD file)
python scripts\enhanced\enh_RURO_prep_mnl_basic.py ``
    --singles-draws U:/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_RURO_draws.parquet ``
    --euromod-combined U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016_reduced/combined_draws_em.parquet ``
    --out-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl ``
    --wage-spec vw ``
    --year 2016 ``
    --couples-draws U:/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready_RURO_draws.parquet ``
    --gsur-file U:/Desktop/Nizam_Hisham/MNL/Data/external/FR_gsur_ruro.parquet

# Step 7: Joint estimation
python scripts\enhanced\enh_RURO_estimate_FR.py ``
    --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl ``
    --output-dir outputs/estimation/FR_2016 ``
    --group joint ``
    --n-jobs 4

"@ -ForegroundColor White
    }
    
    "4" {
        Write-Host "`nExiting...`n" -ForegroundColor Yellow
        exit
    }
    
    default {
        Write-Host "`nInvalid choice. Exiting.`n" -ForegroundColor Red
    }
}

Write-Host "`nDone!`n" -ForegroundColor Green
