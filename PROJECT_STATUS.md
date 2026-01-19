# RURO MNL Estimation Project - Current Status

**Last Updated**: 2026-01-17
**Current Phase**: Phase 1 COMPLETED, Ready for Phase 2
**Project Goal**: Fix GAMSPy estimation to match SciPy results and provide 10x speedup

---

## Quick Summary

### The Problem
GAMSPy estimation produces terrible results (LL = -15053.63) compared to SciPy (LL = -5148.16). Investigation revealed two root causes:

1. **Parameter Naming Issue** (FIXED in Phase 1 ✓)
   - GAMSPy used hardcoded `beta_c`, `beta_l0` that don't exist in 4-group spec
   - Should use `beta_c_sm`, `beta_l0_sm` for singles male, etc.

2. **Utility Function Issue** (Phase 2 - TODO)
   - GAMSPy uses log-linear: `U = β*log(C) + β*log(L)`
   - SciPy uses Box-Cox: `U = β*BC(C,θ) + β*BC(L,θ)`
   - These are fundamentally different models!

### What Works Now

✓ All 4 specification files parse correctly (Phase 0)
✓ GAMSPy reads parameters dynamically from any spec (Phase 1)
✓ No more hardcoded parameter names (Phase 1)
✓ Proper 4-group architecture support (Phase 1)

### What's Next

- [ ] **Phase 2**: Implement Box-Cox utility in GAMSPy (3-4 hours)
- [ ] **Phase 4**: Add error detection and logging (1 hour)
- [ ] **Phase 5**: Test GAMSPy vs SciPy baseline (2 hours)
- [ ] **Phase 6**: Extract Hessian for standard errors (1 hour)
- [ ] **Phase 7**: Test all 4 specifications (2 hours)

**Estimated time to completion**: ~10 hours

---

## File Structure

### Specification Files (scripts/enhanced/)

| File | Parameters | Status | Notes |
|------|------------|--------|-------|
| estimation_spec.yaml | 49 | ✓ Working | Base 4-group architecture |
| estimation_spec_AC2013.yaml | 68 | ✓ Working | Aaberge-Colombino 2013 style |
| estimation_spec_v2.yaml | 53 | ✓ Working | Extended with region interactions |
| estimation_spec_loc_empirical.yaml | 52 | ✓ Working | Location empirical (fixed in Phase 0) |

### Code Files

| File | Purpose | Status |
|------|---------|--------|
| gamspy_estimation.py | GAMSPy estimation functions | Phase 1 DONE |
| estimation_engine.py | SciPy estimation (Box-Cox) | Working (baseline) |
| estimation_spec_parser.py | YAML parsing | Working |
| validate_specs.py | Spec validation tool | Created Phase 0 |
| fix_spec_initial_values.py | Spec repair tool | Created Phase 0 |

### Documentation Files

| File | Purpose |
|------|---------|
| PHASE1_ANALYSIS.md | Phase 1 problem analysis |
| PHASE1_COMPLETED.md | Phase 1 completion report |
| PROJECT_STATUS.md | This file - current status |
| witty-growing-hearth.md | Original implementation plan |

### Result Files

| Path | Description | Quality |
|------|-------------|---------|
| outputs/estimates/fr/2016/estimation_results.json | Current SciPy (46 params) | LL=-5148.16 ✓ |
| outputs/estimates/fr/2016_legacy/estimation_results.json | Legacy SciPy (49 params) | LL=-5045.61 ✓✓ (BEST) |
| outputs/estimates/fr/2016_gamspy/.../estimation_results.json | Broken GAMSPy | LL=-15053.63 ✗ |

---

## Parameter Architecture

### 4-Group Structure (46 parameters)

**Singles Male (_sm)**:
- beta_c_sm, theta_c_sm (consumption)
- beta_l0_sm, theta_l_sm (leisure)
- beta_l_age_norm_sm, beta_l_age_norm2_sm
- beta_l_educL_sm, beta_l_educH_sm

**Singles Female (_sf)**:
- beta_c_sf, theta_c_sf (consumption)
- beta_l0_sf, theta_l_sf (leisure)
- beta_l_age_norm_sf, beta_l_age_norm2_sf
- beta_l_n_children_sf (children effect)
- beta_l_educL_sf, beta_l_educH_sf

**Couples Male (_m)**:
- beta_l0_m, theta_l_m (leisure only)
- beta_l_age_norm_m, beta_l_age_norm2_m
- beta_l_educL_m, beta_l_educH_m

**Couples Female (_f)**:
- beta_l0_f, theta_l_f (leisure only)
- beta_l_age_norm_f, beta_l_age_norm2_f
- beta_l_n_children_f (children effect)
- beta_l_educL_f, beta_l_educH_f

**Couples Household (shared)**:
- beta_c, theta_c (consumption - shared between partners)

**Opportunity & Wage Parameters** (shared across all groups):
- beta_work, beta_pt1, beta_pt2, beta_ft (hours opportunity)
- beta_work_educL, beta_work_educH (education effects on work)
- beta_w0, beta_w_educL, beta_w_educH (wage equation)
- beta_pexp, beta_pexp2 (potential experience)
- sigma (wage variance)

**Couples Interaction**:
- beta_interact (cross-leisure effect)

---

## Key Technical Concepts

### Box-Cox Transformation

**Formula**:
```
BC(x, θ) = (x^θ - 1) / θ    if |θ| > ε
BC(x, θ) = log(x)            if |θ| ≤ ε
```

**Purpose**: Flexible utility curvature
- θ = 0 → logarithmic utility (standard)
- θ = 1 → linear utility
- θ ∈ (0,1) → intermediate concavity

**In MNL Context**:
```
U = β_c * BC(C/c_scale, θ_c) + β_l * BC(L/l_scale, θ_l) + opportunity terms
```

### Log-Linear Utility (What GAMSPy Currently Uses)

**Formula**:
```
U = β_c * log(C/c_scale) + β_l * log(L/l_scale) + opportunity terms
```

**Problem**: This is equivalent to Box-Cox with θ=0 (forced), but our specifications have θ as estimated parameters!

### Why Results Differ

**SciPy estimates** (Box-Cox):
```
beta_c_sm = 1.04   (positive, because θ_c_sm = 0.26 allows flexibility)
theta_c_sm = 0.26  (non-zero curvature)
```

**GAMSPy would estimate** (log-linear):
```
beta_c_sm = negative?  (compensating for forced θ=0)
theta_c_sm = not used  (hardcoded to 0 implicitly)
```

---

## How to Continue This Project

### Starting a New Session

1. **Read this file** (PROJECT_STATUS.md) for current status
2. **Read PHASE1_COMPLETED.md** for what was just finished
3. **Check the todo list** for next tasks
4. **Review the plan** in witty-growing-hearth.md for overall strategy

### Key Files to Understand

**Before modifying code, read**:
1. scripts/enhanced/estimation_spec_parser.py (understand spec structure)
2. scripts/enhanced/estimation_engine.py (SciPy baseline - Box-Cox implementation)
3. scripts/enhanced/gamspy_estimation.py (GAMSPy implementation - just updated)

### Testing Strategy

**Quick syntax check**:
```bash
python -m py_compile scripts/enhanced/gamspy_estimation.py
```

**Validate specs**:
```bash
python scripts/enhanced/validate_specs.py
```

**Run SciPy estimation** (baseline):
```bash
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
  --output-dir "outputs/estimates/fr/2016" \
  --group joint \
  --method L-BFGS-B \
  --maxiter 5000
```

**Run GAMSPy estimation** (once Phase 2 done):
```bash
# Same command with --use-gamspy flag (to be added)
```

---

## Common Pitfalls

### 1. Don't Mix Phase 1 and Phase 2 Changes

**Phase 1**: Parameter naming (DONE)
**Phase 2**: Utility function form (TODO)

These are separate concerns - don't try to fix both at once!

### 2. Test with SMALL Dataset First

Before running full estimation (4253 groups, 425k observations):
- Create a test with 10-20 groups
- Verify utility expressions build correctly
- Check parameter names resolve correctly

### 3. Remember: GAMSPy Uses Different Math Library

**NumPy**: `np.log()`, `np.power()`, `np.exp()`
**GAMSPy**: `gp_log()`, `gp_power()`, `gp_exp()`

Import correctly:
```python
from gamspy.math import exp as gp_exp, log as gp_log, power as gp_power
```

### 4. GAMS Doesn't Like UNC Paths

Always call `ensure_local_workdir()` before creating GAMSPy Container.

---

## Success Criteria

### Phase 2 Success (Box-Cox Implementation)

✓ GAMSPy estimation uses Box-Cox utility
✓ Syntax check passes
✓ Test run completes without errors
✓ Parameter estimates have correct signs (beta_c_sm > 0, not negative)

### Final Success (All Phases)

✓ GAMSPy LL ≈ SciPy LL (within 1-2 LL units)
✓ Parameter estimates match (within 1-2%)
✓ GAMSPy completes in < 5 minutes (vs 20 min for SciPy)
✓ Standard errors and t-values available
✓ All 4 specifications work with both SciPy and GAMSPy

---

## Contact Points / Key Decisions

### Specification Choices

**User prefers**: 4-group 46-parameter architecture (estimation_spec.yaml)
**Why**: Gender-specific parameters, modern specification

**But**: Legacy 49-param spec gave better fit (LL=-5045 vs -5148)
**Reason**: Had extra parameters (beta_work_female, beta_work_couple, beta_work_idf)

**Decision**: Continue with 46-param 4-group spec, possibly revisit if needed

### Solver Choices

**GAMSPy solvers**:
- CONOPT (default): Good for smooth NLP
- IPOPT: Interior-point, handles bounds well
- KNITRO: Commercial, very fast (if available)

**Current default**: CONOPT

---

## Quick Command Reference

### Python Environment

```bash
# Activate venv
U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\activate

# Check Python
python --version

# Install GAMSPy (if needed)
pip install gamspy
```

### File Operations

```bash
# Syntax check all Python files
python -m py_compile scripts/enhanced/*.py

# Validate all specs
python scripts/enhanced/validate_specs.py

# Fix missing initial values
python scripts/enhanced/fix_spec_initial_values.py
```

### Git Operations

```bash
# Check status
git status

# See what changed
git diff scripts/enhanced/gamspy_estimation.py

# Commit Phase 1
git add scripts/enhanced/gamspy_estimation.py PHASE1_*.md PROJECT_STATUS.md
git commit -m "feat: Phase 1 - Make GAMSPy specification-agnostic with dynamic parameter lookup"
```

---

## End of Project Status Document

**Next Step**: Implement Phase 2 (Box-Cox Utility Transformation in GAMSPy)

**Estimated Completion**: Phase 2 can be completed in one 3-4 hour session

**User's Instruction**: "proceed please ! ( alwasy keep documentation of what is happening so whenver I continue or start a new chat I need to know where  I am ) you whole purpose is to help me in this project only nothing else !"

**Documentation**: ✓ COMPLETE - All phases documented for continuity
