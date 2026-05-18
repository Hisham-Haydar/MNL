# RUN WITH SCIPY - Traditional Estimator
# This should work as before (just slower than GAMSPY)

Write-Host "="*80 -ForegroundColor Cyan
Write-Host "RUNNING WITH SCIPY (Traditional Estimator)" -ForegroundColor Yellow
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""
Write-Host "Using:" -ForegroundColor Yellow
Write-Host "  • Solver: SciPy L-BFGS-B (traditional)" -ForegroundColor White
Write-Host "  • Column filtering: Active (~100 cols vs 641/650)" -ForegroundColor White
Write-Host "  • EUROMOD: Reduced (63 MB vs 465 MB)" -ForegroundColor White
Write-Host "  • var_data fix: Active (for standard errors)" -ForegroundColor White
Write-Host ""
Write-Host "Expected runtime: 10-15 minutes (vs 30-40 min before optimizations)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Starting SciPy estimation..." -ForegroundColor Cyan
Write-Host ""

python scripts\enhanced\enh_RURO_estimate_FR.py `
    --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
    --output-dir outputs\estimates\fr\2016_scipy `
    --group joint `
    --solver scipy `
    --spec-config scripts\enhanced\specifications\estimation_spec.yaml `
    --auto-timestamp

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "="*80 -ForegroundColor Green
    Write-Host "SCIPY ESTIMATION COMPLETE!" -ForegroundColor Green
    Write-Host "="*80 -ForegroundColor Green
    
    $latest = Get-ChildItem "outputs\estimates\fr\2016_scipy" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    Write-Host ""
    Write-Host "Results: $($latest.FullName)" -ForegroundColor Cyan
    Write-Host ""
    Get-ChildItem $latest.FullName | Select-Object Name, @{Name="Size(KB)";Expression={[math]::Round($_.Length/1KB,1)}} | Format-Table -AutoSize
} else {
    Write-Host ""
    Write-Host "="*80 -ForegroundColor Red
    Write-Host "SCIPY ESTIMATION FAILED" -ForegroundColor Red
    Write-Host "="*80 -ForegroundColor Red
}
