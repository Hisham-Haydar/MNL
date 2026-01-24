# ==============================================================================
# PHASE 1: SciPy Screening - All 4 Specifications in Parallel
# ==============================================================================
# Run these commands in PowerShell. Each command ends with & to run in background.
# After all 4 are started, run: Wait-Job to see when they complete
#
# Expected total time: 2-3 hours (parallel execution)
# ==============================================================================

# Set working directory
cd "U:\Desktop\Nizam_Hisham\MNL"

# ==============================================================================
# SPEC 1: Current Minimal (Baseline)
# ==============================================================================
Write-Host "Starting SPEC 1: minimal_theta0 with SciPy..." -ForegroundColor Cyan

python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/spec_tests/1_minimal_theta0_scipy" `
  --group joint `
  --solver scipy `
  --method L-BFGS-B `
  --maxiter 2000 `
  --spec-config "scripts/enhanced/estimation_spec_minimal_theta0.yaml" `
  --warm-start "outputs/estimates/fr/minimal_theta0/2016_gamspy/run_2026-01-23_15-41-04/estimation_results.json" `
  --auto-timestamp `
  --verbose &

# ==============================================================================
# SPEC 2: Pooled Consumption
# ==============================================================================
Write-Host "Starting SPEC 2: pooled_consumption with SciPy..." -ForegroundColor Cyan

python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/spec_tests/2_pooled_consumption_scipy" `
  --group joint `
  --solver scipy `
  --method L-BFGS-B `
  --maxiter 2000 `
  --spec-config "scripts/enhanced/estimation_spec_pooled_consumption.yaml" `
  --warm-start "outputs/estimates/fr/minimal_theta0/2016_gamspy/run_2026-01-23_15-41-04/estimation_results.json" `
  --auto-timestamp `
  --verbose &

# ==============================================================================
# SPEC 3: Pooled Leisure by Gender
# ==============================================================================
Write-Host "Starting SPEC 3: pooled_leisure with SciPy..." -ForegroundColor Cyan

python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/spec_tests/3_pooled_leisure_scipy" `
  --group joint `
  --solver scipy `
  --method L-BFGS-B `
  --maxiter 2000 `
  --spec-config "scripts/enhanced/estimation_spec_pooled_leisure.yaml" `
  --warm-start "outputs/estimates/fr/minimal_theta0/2016_gamspy/run_2026-01-23_15-41-04/estimation_results.json" `
  --auto-timestamp `
  --verbose &

# ==============================================================================
# SPEC 4: Ultra Minimal (Log-only, pooled consumption + leisure by gender)
# ==============================================================================
Write-Host "Starting SPEC 4: ultra_minimal with SciPy..." -ForegroundColor Cyan

python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/spec_tests/4_ultra_minimal_scipy" `
  --group joint `
  --solver scipy `
  --method L-BFGS-B `
  --maxiter 2000 `
  --spec-config "scripts/enhanced/estimation_spec_ultra_minimal.yaml" `
  --warm-start "outputs/estimates/fr/minimal_theta0/2016_gamspy/run_2026-01-23_15-41-04/estimation_results.json" `
  --auto-timestamp `
  --verbose &

# ==============================================================================
# WAIT FOR ALL JOBS TO COMPLETE
# ==============================================================================
Write-Host "`nAll 4 SciPy runs started in parallel. Waiting for completion..." -ForegroundColor Yellow
Write-Host "This will take 2-3 hours total." -ForegroundColor Yellow

Get-Job | Wait-Job

Write-Host "`nAll SciPy estimations complete!" -ForegroundColor Green
Write-Host "Results are in: outputs/estimates/fr/spec_tests/" -ForegroundColor Green

# ==============================================================================
# NEXT STEP: ANALYSIS
# ==============================================================================
Write-Host "`n" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PHASE 1 COMPLETE - Next Steps:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Check each estimation_results.json for:" -ForegroundColor Cyan
Write-Host "   - Log-likelihood (LL)" -ForegroundColor Cyan
Write-Host "   - Condition number (in hessian_diagnostics)" -ForegroundColor Cyan
Write-Host "   - Parameter estimates" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host "2. Create comparison table with:" -ForegroundColor Cyan
Write-Host "   | Spec | LL | Cond # | AIC | BIC |" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host "3. Pick best 2-3 specs for Phase 2 (GAMSPy CONOPT validation)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
