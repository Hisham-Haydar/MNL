# Phase 5 Bug #6: GAMSPy Shows "Iterations: 0" Despite All Fixes

**Date**: 2026-01-17
**Status**: 🔍 INVESTIGATING
**Impact**: CRITICAL - GAMSPy builds model correctly but CONOPT doesn't optimize

---

## Summary

After fixing 5 critical bugs, GAMSPy estimation still fails with:
- **Iterations: 0** - CONOPT reports no optimization occurred
- **LL = -10408.9232** (should be ~-5148)
- **Parameters unchanged** from initial values
- **Model status: OptimalLocal** (misleading - it's not actually optimal!)

---

## What We Know

### 1. Joint Estimation Function IS Running

From logs (run_2026-01-17_14-53-16):
```
2026-01-17 14:53:25 - Starting GAMSPy JOINT estimation
2026-01-17 14:53:27 - Created 49 shared parameters
2026-01-17 14:53:27 - Building log-likelihood for singles male...
2026-01-17 14:53:52 - Singles male LL expression built (25 seconds)
2026-01-17 14:53:52 - Building log-likelihood for singles female...
2026-01-17 14:54:24 - Singles female LL expression built (32 seconds)
2026-01-17 14:54:24 - Building log-likelihood for couples...
2026-01-17 14:55:46 - Couples LL expression built (82 seconds)
2026-01-17 14:55:46 - Combining into joint log-likelihood...
2026-01-17 14:56:22 - (Combining took 36 seconds!)
2026-01-17 14:56:22 - Solving joint model with CONOPT...
2026-01-17 14:57:55 - JOINT ESTIMATION COMPLETE (93 seconds for "solve")
```

**Total time**: 4.5 minutes

The joint function completes and returns results, but CONOPT did 0 iterations in 93 seconds.

### 2. Expression Building Pattern Matches Working Code

DCM2_gamspy.py (working reference implementation):
```python
objective_expr = 0.0  # Start with Python float
for n_idx in range(N):
    # Build log-likelihood term for observation n
    objective_expr += lognum_expr - gp_log(denom_expr + 1e-60)

model = Model(container, objective=objective_expr, sense="max")
```

Our code (gamspy_estimation.py):
```python
ll_sm = 0.0  # Start with Python float
for g in range(data_singles_male.n_groups):
    # Build log-likelihood term for group g
    ll_sm = ll_sm + log_prob

ll_joint = ll_sm + ll_sf + ll_cou

model = Model(container, objective=ll_joint, sense="max")
```

**Pattern is IDENTICAL** to working code!

### 3. All Previous Bugs Are Fixed

- ✅ Bug #1: Box-Cox POWER function → using exp(θ * log(x))
- ✅ Bug #2: Status from wrong object → using model, not result
- ✅ Bug #3: Wrong attribute names → using solve_status and status
- ✅ Bug #4: Box-Cox scaling → applying to raw values
- ✅ Bug #5: Constraining equations → removed, direct expression maximization

### 4. Results Are Byte-for-Byte Identical Across Runs

```
Run 1: LL = -10408.9232, beta_l0_sm = -0.002855, Iterations: 0
Run 2: LL = -10408.9232, beta_l0_sm = -0.002855, Iterations: 0
Run 3: LL = -10408.9232, beta_l0_sm = -0.002855, Iterations: 0
```

This suggests:
1. CONOPT is evaluating the LL at initial values
2. CONOPT thinks it's "optimal" at those values
3. CONOPT doesn't explore parameter space at all

---

## Hypotheses

### Hypothesis 1: Expression Is a Constant

**Theory**: The `ll_joint` expression might be evaluated to a constant before passing to Model(), so CONOPT sees a constant objective (no variables to optimize).

**Test**: Check `type(ll_joint)` before creating model:
```python
logger.info(f"ll_joint type: {type(ll_joint)}")
# Should be: <class 'gamspy._algebra.expression.Expression'>
# NOT: <class 'float'>
```

**Status**: Testing now with diagnostic logging

### Hypothesis 2: GAMSPy Is Caching The Model

**Theory**: GAMSPy might cache models by name, and we're reusing "ruro_joint_mnl_gamspy" across runs.

**Test**: Try unique model name each run
```python
model_name = f"ruro_joint_mnl_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
model = Model(container, name=model_name, ...)
```

**Status**: Not tested yet

### Hypothesis 3: Parameter Variables Not Linked to Objective

**Theory**: The parameter variables (`param_vars[name]`) might not be properly linked to the objective expression, so CONOPT sees no derivatives.

**Test**: Check container has variables
```python
n_vars = sum(1 for s in container.data.values() if hasattr(s, 'type'))
logger.info(f"Container has {n_vars} variables")
# Should be: 49 variables
```

**Status**: Testing now with diagnostic logging

### Hypothesis 4: Initial Values Are "Locally Optimal"

**Theory**: By pure chance, the initial values might satisfy first-order optimality conditions for the (wrong) LL formulation.

**Evidence against**: SciPy with same initial values takes 200+ iterations and finds much better solution (LL=-5148).

**Status**: Unlikely

### Hypothesis 5: CONOPT Configuration Issue

**Theory**: CONOPT might have a convergence tolerance so loose that it thinks initial values are optimal.

**Test**: Check CONOPT listing file for convergence criteria
```bash
find . -name "*.lst" -type f  # Look for GAMS listing files
grep "ITERATION\|CONVERGENCE" *.lst
```

**Status**: No .lst files found in output directory (need to check temp directory)

---

## Current Investigation

**Running**: GAMSPy estimation with diagnostic logging to check:
1. `type(ll_sm)`, `type(ll_sf)`, `type(ll_cou)`, `type(ll_joint)`
2. Number of symbols in container
3. Number of Variables in container
4. Model problem type and sense

**Expected output**:
```
ll_sm type: <class 'gamspy._algebra.expression.Expression'>
ll_sf type: <class 'gamspy._algebra.expression.Expression'>
ll_cou type: <class 'gamspy._algebra.expression.Expression'>
ll_joint type: <class 'gamspy._algebra.expression.Expression'>
Model problem type: nlp
Model sense: max
Container has 50+ symbols
Number of Variables: 49
```

If all these check out, then the model is built correctly and the issue is with CONOPT itself or how we're calling it.

---

## Next Steps

1. **Check diagnostic output** from current run
2. **If expressions are correct**: Look for GAMS listing files to see what CONOPT is actually doing
3. **If expressions are constants**: Investigate why accumulation pattern breaks (but DCM2 works!)
4. **If variables missing**: Check parameter variable creation logic
5. **Last resort**: Try different solver (IPOPT, KNITRO) to see if it's CONOPT-specific

---

**Investigation Started**: 2026-01-17 15:00
**Estimated Resolution**: 1-2 hours

---
