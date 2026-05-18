# Quick Run - Fixed Indentation Error
# Run this to start the estimation

Write-Host "=" * 80 -ForegroundColor Green
Write-Host "INDENTATION ERROR FIXED - RUNNING ESTIMATION" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Green
Write-Host ""
Write-Host "Fixed: Line 893 indentation error in gamspy_estimation.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting estimation..." -ForegroundColor Yellow
Write-Host ""

python scripts\enhanced\enh_RURO_estimate_FR.py `
    --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl `
    --output-dir outputs\estimates\fr\2016_gamspy `
    --group joint `
    --solver gamspy-conopt `
    --spec-config scripts\enhanced\specifications\estimation_spec.yaml `
    --auto-timestamp

Write-Host ""
if ($LASTEXITCODE -eq 0) {
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "=" * 80 -ForegroundColor Green
} else {
    Write-Host "=" * 80 -ForegroundColor Red
    Write-Host "FAILED - Check error above" -ForegroundColor Red
    Write-Host "=" * 80 -ForegroundColor Red
}
