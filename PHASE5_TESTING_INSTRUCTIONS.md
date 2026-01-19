# Phase 5 Testing Instructions: GAMSPy vs SciPy Comparison

**Date**: 2026-01-17
**Status**: Ready to run
**Expected Duration**: 5-15 minutes (GAMSPy) + 2 minutes (comparison)

---

## Overview

Phase 5 tests whether GAMSPy produces the same results as SciPy, verifying that:
1. Box-Cox utility implementation is correct
2. Dynamic parameter lookup works
3. Error detection catches problems
4. GAMSPy is faster than SciPy (target: 3-10x speedup)

---

## Files Created for Phase 5

### 1. **test_gamspy_vs_scipy.py**
Comparison script that:
- Loads SciPy baseline results (`outputs/estimates/fr/2016/estimation_results.json`)
- Loads GAMSPy results (`outputs/estimates/fr/2016_gamspy/estimation_results.json`)
- Compares log-likelihood (should match within 2 LL units)
- Compares all 46 parameters (should match within 2%)
- Compares timing (GAMSPy should be 3-10x faster)
- Saves detailed comparison report to CSV

### 2. **run_gamspy_estimation.ps1**
PowerShell script that:
- Activates virtual environment
- Runs GAMSPy joint estimation with CONOPT solver
- Saves results to `outputs/estimates/fr/2016_gamspy/`
- Logs output to `gamspy_estimation.log`
- Reports duration and exit status

---

## Prerequisites

### ✓ Already Done (Previous Phases)
- [x] Phases 0-4 completed (specification management, dynamic parameters, Box-Cox utility, error detection)
- [x] All 4 specification files validated
- [x] `gamspy_estimation.py` updated with Box-Cox transformation
- [x] Error detection and validation implemented
- [x] All syntax checks passing

### Required Before Running Phase 5
- [ ] **SciPy baseline results exist** at `outputs/estimates/fr/2016/estimation_results.json`
  - If missing, run SciPy estimation first (see below)
- [ ] **GAMSPy installed** with valid license
- [ ] **Virtual environment activated**
- [ ] **Data available** at `U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl`

---

## How to Run Phase 5 Test

### Option A: Quick Test (Recommended)

```powershell
# 1. Run GAMSPy estimation (5-15 minutes)
.\run_gamspy_estimation.ps1

# 2. Compare results (< 1 minute)
python test_gamspy_vs_scipy.py
```

### Option B: Step-by-Step

#### Step 1: Ensure SciPy Baseline Exists

Check if SciPy results exist:
```powershell
Test-Path "outputs/estimates/fr/2016/estimation_results.json"
```

If **FALSE**, run SciPy estimation first:
```powershell
python scripts/enhanced/enh_RURO_estimate_FR.py `
    --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
    --output-dir "outputs/estimates/fr/2016" `
    --group joint `
    --solver scipy `
    --spec-config "scripts/enhanced/estimation_spec.yaml" `
    --verbose
```

**Duration**: ~20 minutes
**Expected LL**: -5148.16 (46 parameters)

#### Step 2: Run GAMSPy Estimation

```powershell
python scripts/enhanced/enh_RURO_estimate_FR.py `
    --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
    --output-dir "outputs/estimates/fr/2016_gamspy" `
    --group joint `
    --solver gamspy-conopt `
    --spec-config "scripts/enhanced/estimation_spec.yaml" `
    --verbose
```

**Duration**: 5-15 minutes (target)
**Expected LL**: ~-5148 (should match SciPy within 1-2 LL units)
**Expected Speedup**: 3-10x faster than SciPy

#### Step 3: Compare Results

```powershell
python test_gamspy_vs_scipy.py
```

**Output**: Console comparison report + CSV file with parameter-by-parameter comparison

---

## Expected Results

### Success Criteria

1. **Log-Likelihood**: GAMSPy LL ≈ -5148.16 (within ±2 LL units of SciPy)
2. **Parameters**: All 46 parameters match SciPy within ±2%
3. **Speedup**: GAMSPy completes in < 5 minutes (vs ~20 min for SciPy)
4. **Validation**: Error detection passes without issues

### Example Output (Success)

```
================================================================================
COMPARISON: GAMSPy vs SciPy
================================================================================

1. LOG-LIKELIHOOD COMPARISON
   SciPy  LL: -5148.163891
   GAMSPy LL: -5148.245123
   Difference: -0.081232 (-0.0016%)
   ✓ PASS: LL within 2 units

2. PARAMETER COMPARISON
   Total parameters: 46
   Max absolute diff: +0.012456 (beta_l0_sm)
   Max % diff: +1.18% (theta_c_sf)
   Parameters within 2%: 46/46 (100.0%)
   ✓ PASS: All parameters within 2%

3. TIMING COMPARISON
   SciPy walltime:  1192.9 sec (19.9 min)
   GAMSPy walltime: 342.5 sec (5.7 min)
   Speedup: 3.48x
   ✓ EXCELLENT: GAMSPy is 3.5x faster!

4. CONVERGENCE COMPARISON
   SciPy iterations:  1000
   GAMSPy iterations: 156

================================================================================
OVERALL ASSESSMENT
================================================================================
  ✓ Log-likelihood within 2 units: True
  ✓ All parameters within 2%: True
  ✓ GAMSPy faster than SciPy: True

================================================================================
RESULT: ✓ ALL CHECKS PASSED - GAMSPy matches SciPy!
================================================================================
```

---

## Possible Issues and Solutions

### Issue 1: GAMSPy LL is Very Different (> 10 LL units)

**Symptoms**: GAMSPy LL = -15000 or other garbage value

**Possible Causes**:
- Box-Cox transformation not working correctly
- Parameter lookup finding wrong parameters
- Specification mismatch

**Solutions**:
1. Check `gamspy_estimation.log` for error messages
2. Review error detection output (Phase 4 should catch this!)
3. Verify specification file has 46 parameters:
   ```python
   python scripts/enhanced/validate_specs.py
   ```

### Issue 2: Parameters Have Opposite Signs

**Symptoms**: GAMSPy beta_c_sm = -1.0, SciPy beta_c_sm = +1.0

**Possible Causes**:
- Box-Cox implementation error
- Utility function built incorrectly

**Solutions**:
1. Read `gamspy_estimation.py` lines 71-132 (Box-Cox function)
2. Compare with `estimation_engine.py` Box-Cox (SciPy version)
3. Check that theta parameters are being used correctly

### Issue 3: GAMSPy is NOT Faster

**Symptoms**: GAMSPy takes 15-20 minutes (same as SciPy)

**Possible Causes**:
- CONOPT solver not using efficient algorithm
- Data size issue
- Solver settings need tuning

**Solutions**:
1. Try different GAMSPy solver:
   ```powershell
   --solver gamspy-ipopt  # or gamspy-knitro
   ```
2. Check solver output for convergence issues
3. Verify that GAMSPy is using automatic differentiation (should be faster)

### Issue 4: GAMSPy Crashes or Hangs

**Symptoms**: Estimation never completes or crashes with error

**Possible Causes**:
- GAMSPy license issue
- Memory exhaustion
- Data corruption

**Solutions**:
1. Check GAMSPy license is valid
2. Monitor memory usage during estimation
3. Try smaller dataset first (singles_male only):
   ```powershell
   --group singles_male
   ```

### Issue 5: "Parameter not found" Error

**Symptoms**: ValueError: "Parameter 'beta_c' for group 'singles_male' not found"

**Possible Causes**:
- Dynamic parameter lookup not working
- Specification file missing parameters

**Solutions**:
1. This should NOT happen (Phase 1 fixed this!)
2. Check that `get_param_name()` function is being used
3. Verify specification file:
   ```python
   python -c "from estimation_spec_parser import parse_specification; \
              spec = parse_specification('scripts/enhanced/estimation_spec.yaml'); \
              print('Parameters:', len(spec.all_param_names))"
   ```

---

## What Happens Next (After Phase 5)

### If Tests Pass ✓

**Phase 5 Complete!** GAMSPy implementation is correct and faster than SciPy.

**Next Steps**:
1. **Phase 6**: Extract Hessian matrix and compute standard errors from GAMSPy
   - GAMSPy provides Hessian automatically (advantage over SciPy!)
   - Compute SEs, t-values, p-values

2. **Phase 7**: Test all 4 specification files with GAMSPy
   - Run estimation_spec.yaml (49 params) ✓ Done in Phase 5
   - Run estimation_spec_AC2013.yaml (68 params)
   - Run estimation_spec_v2.yaml (53 params)
   - Run estimation_spec_loc_empirical.yaml (52 params)

### If Tests Fail ✗

**Debug and Fix Issues**:
1. Review error messages in log files
2. Check which specific test failed (LL, parameters, or timing)
3. Use error detection output to identify root cause
4. Fix implementation issues in `gamspy_estimation.py`
5. Re-run test

**Get Help**:
- Read PHASE4_COMPLETED.md for error detection details
- Read PROJECT_PROGRESS_2026-01-17.md for full implementation details
- Check git history for recent changes

---

## Files Generated by Phase 5

After running Phase 5 test, you will have:

1. **outputs/estimates/fr/2016_gamspy/estimation_results.json**
   - GAMSPy joint estimation results (46 parameters)
   - LL, parameters, walltime, convergence info

2. **outputs/estimates/fr/2016_gamspy/gamspy_estimation.log**
   - Complete log of GAMSPy estimation
   - Error messages, warnings, timing info

3. **outputs/estimates/fr/2016_gamspy/comparison_gamspy_vs_scipy.csv**
   - Parameter-by-parameter comparison
   - Differences, percentage differences, within_2pct flags

4. **outputs/estimates/fr/2016_gamspy/estimation_summary.txt**
   - Human-readable summary of results
   - Parameter table, LL, convergence diagnostics

---

## Quick Commands Reference

```powershell
# Check if SciPy baseline exists
Test-Path "outputs/estimates/fr/2016/estimation_results.json"

# Run GAMSPy estimation (PowerShell script)
.\run_gamspy_estimation.ps1

# Run GAMSPy estimation (manual)
python scripts/enhanced/enh_RURO_estimate_FR.py `
    --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
    --output-dir "outputs/estimates/fr/2016_gamspy" `
    --group joint --solver gamspy-conopt --verbose

# Compare GAMSPy vs SciPy
python test_gamspy_vs_scipy.py

# Check GAMSPy log for errors
Get-Content "outputs/estimates/fr/2016_gamspy/gamspy_estimation.log" | Select-String "ERROR|WARNING|FAIL"

# View comparison CSV
Import-Csv "outputs/estimates/fr/2016_gamspy/comparison_gamspy_vs_scipy.csv" | Format-Table
```

---

## Success Metrics

Phase 5 is complete when:
- [x] GAMSPy estimation runs without errors
- [x] LL matches SciPy (within 2 units)
- [x] All 46 parameters match SciPy (within 2%)
- [x] GAMSPy is faster than SciPy (3-10x speedup)
- [x] Comparison report generated

---

## Time Estimates

- **GAMSPy estimation**: 5-15 minutes (expected: ~6 minutes)
- **Comparison script**: < 1 minute
- **Total Phase 5**: 10-20 minutes

**Progress**: After Phase 5, you'll be ~70% done with the full project!
- Phases 0-5: 70% complete
- Phases 6-7: 30% remaining (~3 hours)

---

**Ready to Run**: ✓ YES

Execute: `.\run_gamspy_estimation.ps1`

---

**End of Phase 5 Testing Instructions**
