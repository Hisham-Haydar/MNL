# ==============================================================================
# PHASE 2: GAMSPy CONOPT Validation - Run AFTER Phase 1 Complete
# ==============================================================================
# Use these commands AFTER analyzing Phase 1 results.
# Pick your best 2-3 specs and run them with GAMSPy CONOPT to validate
# that solvers agree on the results.
#
# Expected total time: 2-3 hours (parallel execution)
# ==============================================================================

# Set working directory
cd "U:\Desktop\Nizam_Hisham\MNL"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PHASE 2: GAMSPy CONOPT Solver Validation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host "Run these commands IF Phase 1 SciPy completed." -ForegroundColor Yellow
Write-Host "Edit/remove commands for specs that didn't look promising." -ForegroundColor Yellow
Write-Host "" -ForegroundColor Cyan

# ==============================================================================
# OPTION A: Run ultra_minimal (likely to be best)
# ==============================================================================
Write-Host "Starting SPEC 4: ultra_minimal with GAMSPy CONOPT..." -ForegroundColor Cyan

python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/spec_tests/4_ultra_minimal_gamspy" `
  --group joint `
  --solver gamspy-conopt `
  --spec-config "scripts/enhanced/estimation_spec_ultra_minimal.yaml" `
  --warm-start "outputs/estimates/fr/minimal_theta0/2016_gamspy/run_2026-01-23_15-41-04/estimation_results.json" `
  --auto-timestamp `
  --verbose &

# ==============================================================================
# OPTION B: Run pooled_consumption (also strong candidate)
# ==============================================================================
Write-Host "Starting SPEC 2: pooled_consumption with GAMSPy CONOPT..." -ForegroundColor Cyan

python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/spec_tests/2_pooled_consumption_gamspy" `
  --group joint `
  --solver gamspy-conopt `
  --spec-config "scripts/enhanced/estimation_spec_pooled_consumption.yaml" `
  --warm-start "outputs/estimates/fr/minimal_theta0/2016_gamspy/run_2026-01-23_15-41-04/estimation_results.json" `
  --auto-timestamp `
  --verbose &

# ==============================================================================
# OPTION C: Run pooled_leisure (if you want to test this too)
# ==============================================================================
Write-Host "Starting SPEC 3: pooled_leisure with GAMSPy CONOPT..." -ForegroundColor Cyan

python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/spec_tests/3_pooled_leisure_gamspy" `
  --group joint `
  --solver gamspy-conopt `
  --spec-config "scripts/enhanced/estimation_spec_pooled_leisure.yaml" `
  --warm-start "outputs/estimates/fr/minimal_theta0/2016_gamspy/run_2026-01-23_15-41-04/estimation_results.json" `
  --auto-timestamp `
  --verbose &

# ==============================================================================
# OPTIONAL: Run baseline minimal_theta0 with CONOPT (for comparison to your existing run)
# ==============================================================================
# Uncomment below if you want to compare GAMSPy results on the baseline
# Write-Host "Starting SPEC 1: minimal_theta0 with GAMSPy CONOPT..." -ForegroundColor Cyan
#
# python scripts/enhanced/enh_RURO_estimate_FR.py `
#   --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
#   --output-dir "outputs/estimates/fr/spec_tests/1_minimal_theta0_gamspy" `
#   --group joint `
#   --solver gamspy-conopt `
#   --spec-config "scripts/enhanced/estimation_spec_minimal_theta0.yaml" `
#   --warm-start "outputs/estimates/fr/minimal_theta0/2016_gamspy/run_2026-01-23_15-41-04/estimation_results.json" `
#   --auto-timestamp `
#   --verbose &

# ==============================================================================
# WAIT FOR ALL JOBS TO COMPLETE
# ==============================================================================
Write-Host "`nGAMSPy CONOPT runs started in parallel. Waiting for completion..." -ForegroundColor Yellow
Write-Host "This will take 2-3 hours total." -ForegroundColor Yellow

Get-Job | Wait-Job

Write-Host "`nAll GAMSPy CONOPT estimations complete!" -ForegroundColor Green
Write-Host "Results are in: outputs/estimates/fr/spec_tests/" -ForegroundColor Green

# ==============================================================================
# COMPARISON ANALYSIS
# ==============================================================================
Write-Host "`n" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PHASE 2 COMPLETE - Comparison Analysis:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host "For each spec, compare SciPy vs GAMSPy:" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host "SciPy result:" -ForegroundColor Cyan
Write-Host "  outputs/estimates/fr/spec_tests/N_SPEC_scipy/run_*/estimation_results.json" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host "GAMSPy result:" -ForegroundColor Cyan
Write-Host "  outputs/estimates/fr/spec_tests/N_SPEC_gamspy/run_*/estimation_results.json" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host "Extract and compare:" -ForegroundColor Cyan
Write-Host "  1. Log-likelihood (should differ < 0.1%)" -ForegroundColor Cyan
Write-Host "  2. Condition number (exact Hessian from CONOPT)" -ForegroundColor Cyan
Write-Host "  3. Standard errors (CONOPT more reliable)" -ForegroundColor Cyan
Write-Host "  4. Parameter estimates (should be very similar)" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NEXT: Generate final report with best spec" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
