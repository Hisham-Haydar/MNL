# RUN ESTIMATION - var_data None check fixed!
# This should now complete with parameter report

Write-Host "="*80 -ForegroundColor Green
Write-Host "RUNNING ESTIMATION WITH var_data FIX" -ForegroundColor Yellow  
Write-Host "="*80 -ForegroundColor Green
Write-Host ""
Write-Host "Fixed: Added None checks for var_data in estimation_engine.py" -ForegroundColor Cyan
Write-Host "       This fixes the standard error computation error" -ForegroundColor Cyan
Write-Host ""
Write-Host "Expected:" -ForegroundColor Yellow
Write-Host "  ✅ GAMSPY estimation completes (~1.6 min)" -ForegroundColor White
Write-Host "  ✅ Standard errors computed successfully" -ForegroundColor White
Write-Host "  ✅ Parameter report generated" -ForegroundColor White
Write-Host "  ✅ Results saved to JSON and CSV" -ForegroundColor White
Write-Host ""

python scripts\enhanced\enh_RURO_estimate_FR.py `
    --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
    --output-dir outputs\estimates\fr\2016_gamspy `
    --group joint `
    --solver gamspy-conopt `
    --spec-config scripts\enhanced\estimation_spec.yaml `
    --auto-timestamp

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "="*80 -ForegroundColor Green
    Write-Host "SUCCESS! Check results in latest run folder" -ForegroundColor Green
    Write-Host "="*80 -ForegroundColor Green
    
    # Show latest results folder
    $latest = Get-ChildItem "outputs\estimates\fr\2016_gamspy" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    Write-Host ""
    Write-Host "Results location:" -ForegroundColor Yellow
    Write-Host "  $($latest.FullName)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Files:" -ForegroundColor Yellow
    Get-ChildItem $latest.FullName | Select-Object Name, Length | Format-Table -AutoSize
}
