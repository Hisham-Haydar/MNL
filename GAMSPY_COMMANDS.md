# GAMSPy Command Reference Card

## Quick Commands

### Test Installation
```powershell
python scripts\enhanced\test_gamspy_benchmark.py
```

### Joint Estimation (ALL GROUPS - RECOMMENDED)
```powershell
python scripts\enhanced\enh_RURO_estimate_FR.py `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimation/FR_2016_gamspy_joint" `
  --group joint `
  --solver gamspy-conopt `
  --spec-config scripts/enhanced/estimation_spec.yaml `
  --auto-timestamp
```
**Runtime:** ~10-16 minutes (vs 30-40 min with SciPy) - **2.5x speedup!**
**Output:** Creates `run_YYYY-MM-DD_HH-MM-SS/` subfolder with all results

### Singles Male (GAMSPy)
```powershell
python scripts\enhanced\enh_RURO_estimate_FR.py `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimation/FR_2016_gamspy_sm" `
  --group singles_male `
  --solver gamspy-conopt `
  --spec-config scripts/enhanced/estimation_spec.yaml
```

### Singles Female (GAMSPy)
```powershell
python scripts\enhanced\enh_RURO_estimate_FR.py `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimation/FR_2016_gamspy_sf" `
  --group singles_female `
  --solver gamspy-conopt `
  --spec-config scripts/enhanced/estimation_spec.yaml
```

### Couples (GAMSPy)
```powershell
python scripts\enhanced\enh_RURO_estimate_FR.py `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimation/FR_2016_gamspy_cou" `
  --group couples `
  --solver gamspy-conopt `
  --spec-config scripts/enhanced/estimation_spec.yaml
```

### Baseline (SciPy for comparison)
```powershell
python scripts\enhanced\enh_RURO_estimate_FR.py `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimation/FR_2016_scipy_sm" `
  --group singles_male `
  --solver scipy `
  --spec-config scripts/enhanced/estimation_spec.yaml
```

## Solver Options
- `--solver scipy` - L-BFGS-B (baseline, slower)
- `--solver gamspy-conopt` - CONOPT (2-3x faster, **recommended**)
- `--solver gamspy-ipopt` - IPOPT (open-source alternative)
- `--solver gamspy-knitro` - KNITRO (if licensed)

## Files to Check
- Estimation log: `{output-dir}/estimation.log`
- Results JSON: `{output-dir}/estimation_results.json`
- Parameters CSV: `{output-dir}/parameters.csv`
