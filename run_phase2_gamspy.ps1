# Phase 2: GAMSPy CONOPT validation on top 2 specifications
# Run these commands to get exact Hessian diagnostics

# Specification 1: ultra_minimal (10 params, most parsimonious)
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/phase2/ultra_minimal_gamspy" `
  --group joint `
  --solver gamspy-conopt `
  --spec-config "scripts/enhanced/estimation_spec_ultra_minimal.yaml" `
  --warm-start "none" `
  --auto-timestamp `
  --verbose

# Specification 2: pooled_leisure (14 params, best BIC)
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/phase2/pooled_leisure_gamspy" `
  --group joint `
  --solver gamspy-conopt `
  --spec-config "scripts/enhanced/estimation_spec_pooled_leisure.yaml" `
  --warm-start "none" `
  --auto-timestamp `
  --verbose
