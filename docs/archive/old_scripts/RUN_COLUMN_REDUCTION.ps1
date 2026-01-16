# RUN_COLUMN_REDUCTION.ps1
# Execute column reduction on EUROMOD output
# Run this AFTER Step 4 (EUROMOD) and BEFORE Step 6 (MNL dataset creation)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Column Reduction Script" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will reduce EUROMOD output from 342 columns to 25 columns" -ForegroundColor Yellow
Write-Host "Expected: 465 MB → 34 MB (92.7% reduction)" -ForegroundColor Yellow
Write-Host ""

# Run the column reduction
python scripts\enhanced\reduce_mnl_columns.py `
    --input-dir U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Column Reduction Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Output saved to:" -ForegroundColor Cyan
Write-Host "  U:/EUROMOD-STORAGE/interim/ruro/fr/scenarios_2016_reduced/combined_draws_em.parquet" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Update run_enhanced_pipeline.ps1 line 102:" -ForegroundColor White
Write-Host '     $EM_COMBINED = "$SCEN_reduced\combined_draws_em.parquet"' -ForegroundColor Yellow
Write-Host ""
Write-Host "  2. Re-run Step 6 (should be 2-3x faster!):" -ForegroundColor White
Write-Host "     python scripts\enhanced\enh_RURO_prep_mnl_basic.py ..." -ForegroundColor Yellow
Write-Host ""
