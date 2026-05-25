# GAMSPy Integration - Quick Start Guide
## RURO Labor Supply Estimation with CONOPT/IPOPT

**Date**: 2026-01-16  
**Status**: Ready to test  
**License**: GAMSPy Academic (FREE - unlimited CONOPT/IPOPT)

---

## Prerequisites

✅ You already have:
- GAMSPy installed and licensed
- Successfully ran RUM estimations (DCM1_gamspy.py, DCM2_gamspy.py)
- CONOPT/IPOPT working

---

## Quick Test

### Step 1: Verify GAMSPy Installation

```powershell
cd u:\Desktop\Nizam_Hisham\MNL

# Test GAMSPy + CONOPT
python scripts/enhanced/test_gamspy_benchmark.py
```

**Expected output**:
```
================================================================================
TEST 1: GAMSPy Installation & License
================================================================================
[OK] GAMSPy installed (version 1.17.2)
  [i] Solver detection not available, will test CONOPT directly
  [i] GAMSPy installation verified - will test solvers in Test 2

================================================================================
TEST 2: Simple MNL (Synthetic Data)
================================================================================
Generated 200 observations
Choice distribution: [114  86]
...
[OK] Test passed! Max error: 0.1804

================================================================================
TEST SUMMARY
================================================================================
[OK] GAMSPy is ready for RURO pipeline integration!
```

---

## Running RURO Estimation with GAMSPy

### Singles Male Estimation (CONOPT)

```powershell
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/2016_gamspy_conopt_test" `
  --spec-config scripts/enhanced/estimation_spec.yaml `
  --group singles_male `
  --solver gamspy-conopt
```

**Expected runtime**: ~3-7 minutes (vs ~9-12 min with SciPy)

### Singles Female Estimation (IPOPT)

```powershell
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/2016_gamspy_ipopt_test" `
  --spec-config scripts/enhanced/estimation_spec.yaml `
  --group singles_female `
  --solver gamspy-ipopt
```

### Couples Estimation (CONOPT)

```powershell
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/2016_couples_gamspy" `
  --spec-config scripts/enhanced/estimation_spec.yaml `
  --group couples `
  --solver gamspy-conopt
```

---

## Solver Comparison

### Available Solvers

| Solver | Speed vs SciPy | License | Best For |
|--------|----------------|---------|----------|
| `scipy` | 1.0x (baseline) | FREE | Default, validation |
| `gamspy-conopt` | **2-3x faster** | **FREE (academic)** | **Recommended** |
| `gamspy-ipopt` | 1.5-2x faster | FREE (always) | Large-scale problems |
| `gamspy-knitro` | 2.5-3.5x faster | $$$ (commercial) | Not needed (CONOPT is nearly as good) |

### When to Use Each

**Use `gamspy-conopt`** (default recommendation):
- Faster estimation (2-3x speedup)
- Commercial-grade solver at zero cost
- Best for RURO MNL (smooth log-linear utility)

**Use `scipy`** (L-BFGS-B):
- Validation against GAMSPy results
- Debugging (analytical gradient available)
- Joint estimation (not yet implemented in GAMSPy)

**Use `gamspy-ipopt`**:
- If CONOPT license issues
- Very large problems (>10k observations)
- Testing solver sensitivity

---

## Comparing Results

### Run Both Solvers and Compare

```powershell
# SciPy baseline
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/2016_scipy_baseline" `
  --group singles_male `
  --solver scipy

# GAMSPy + CONOPT
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/2016_gamspy_baseline" `
  --group singles_male `
  --solver gamspy-conopt

# Compare results
python scripts/compare_estimation_results.py `
  --result1 outputs/estimates/fr/2016_scipy_baseline/estimation_results.json `
  --result2 outputs/estimates/fr/2016_gamspy_baseline/estimation_results.json
```

**Expected differences**:
- **Runtime**: GAMSPy 2-3x faster
- **Final LL**: Should match within 0.01% (< 1e-2)
- **Parameters**: Should match within 1% (< 0.01)

---

## Current Limitations

### ~~Joint Estimation~~ ✅ NOW IMPLEMENTED!
GAMSPy now supports joint estimation with the `--group joint` flag:
- ✅ `--group singles_male`
- ✅ `--group singles_female`  
- ✅ `--group couples`
- ✅ `--group joint` **NEW: Fully implemented!**

**Joint estimation with GAMSPy:**
```powershell
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/2016_gamspy_joint" `
  --group joint `
  --solver gamspy-conopt `
  --spec-config scripts/enhanced/estimation_spec.yaml
```

**Expected runtime:** 10-16 minutes (vs 30-40 min with SciPy) - **2.5x speedup!**

### Standard Errors
GAMSPy doesn't return gradient → numerical Hessian required (same as SciPy)

Use `--compute-se` flag after estimation (same as before):
```powershell
python scripts/enhanced/RURO_post_estimation_styled.py `
  --results-json outputs/estimates/fr/2016_gamspy_baseline/estimation_results.json `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --spec-config scripts/enhanced/estimation_spec.yaml `
  --compute-se
```

---

## Troubleshooting

### Error: "GAMSPy not installed"
```powershell
pip install gamspy
```

### Error: "CONOPT solver not available"
Check license:
```python
from gamspy import Container
c = Container()
print(c.available_solvers)  # Should include 'CONOPT' or 'conopt'
```

If CONOPT missing:
1. Check GAMSPy license status
2. Contact Bau Brolet / Mateo (GAMSPy team)
3. Use `--solver gamspy-ipopt` as fallback

### Error: "UNC path not supported"
GAMSPy changed working directory to local temp (automatic)
Check log for: "Changed to local working directory: ..."

### Convergence Issues
If GAMSPy finds different local optimum than SciPy:
1. Use SciPy solution as warm-start:
   ```powershell
   --warm-start outputs/estimates/fr/2016_scipy_baseline/estimation_results.json
   ```
2. Compare final LL values (should be close)
3. Report if systematic differences

### Slow Performance
If GAMSPy is NOT 2-3x faster:
1. Check solver actually used (look for "Solving with CONOPT..." in log)
2. Verify problem size (should be ~3k-8k observations)
3. Try different solver (`--solver gamspy-ipopt`)
4. Report issue with benchmark results

---

## Next Steps

### 1. Test Installation (5 minutes)
```powershell
python scripts/enhanced/test_gamspy_benchmark.py
```

### 2. Quick Benchmark (10-15 minutes)
```powershell
# Singles male with CONOPT
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/2016_gamspy_test" `
  --group singles_male `
  --solver gamspy-conopt
```

### 3. Compare with SciPy (20-30 minutes)
Run same estimation with `--solver scipy` and compare results

### 4. Full Pipeline (if successful)
- Run all three groups (SM, SF, couples) with GAMSPy
- Compare with SciPy joint estimation
- Document performance gains
- Update README with solver recommendations

---

## Expected Performance

Based on RUM archive scripts and solver characteristics:

| Group | Observations | SciPy Time | GAMSPy (CONOPT) | Speedup |
|-------|--------------|------------|-----------------|---------|
| Singles Male | ~3,000 | 9-12 min | 3-5 min | 2.4-3.0x |
| Singles Female | ~3,000 | 9-12 min | 3-5 min | 2.4-3.0x |
| Couples | ~2,000 | 12-16 min | 4-6 min | 2.7-3.0x |
| **Total** | ~8,000 | **30-40 min** | **10-16 min** | **~2.5x** |

---

## Support

**GAMSPy Issues**:
- Bau Brolet: bbrolet@gams.com
- Mateo (Academic Coordinator)

**RURO Pipeline Issues**:
- Check `docs/estimation/GAMSPy_Integration_Roadmap.md`
- Review `docs/estimation/GAMSPy_vs_SciPy_Architecture_Comparison.md`

---

## Success Criteria

✅ Test 1 passes (GAMSPy installation OK)  
✅ Test 2 passes (simple MNL works)  
✅ Singles male estimation completes  
✅ Final LL matches SciPy within 0.01%  
✅ Parameters match SciPy within 1%  
✅ Runtime is 2-3x faster than SciPy  

If all criteria met → **Ready for production use!**
