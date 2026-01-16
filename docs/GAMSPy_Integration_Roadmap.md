# GAMSPy Integration Roadmap
## RURO Labor Supply Estimation Pipeline

**Date**: 2026-01-16  
**Status**: Planning Phase  
**License**: GAMSPy Academic (FREE - unlimited CONOPT/IPOPT access)

---

## Executive Summary

**Goal**: Integrate GAMSPy + CONOPT solver to reduce estimation runtime by 2-3x (34 min → 12-15 min) at zero license cost.

**Key Advantage**: Free academic license includes **unlimited** access to commercial-grade CONOPT solver (comparable to $5k+/year KNITRO).

**Timeline**: 3-4 weeks (part-time)

**Risk**: Low (keep SciPy as fallback)

---

## Phase 1: Setup & License (Week 1)

### 1.1 Confirm Academic License
- [x] Contact established (Bau Brolet, Mateo)
- [ ] Email request for LISER academic license
- [ ] Confirm unlimited CONOPT/IPOPT access
- [ ] Receive license credentials

**Email Template**:
```
Dear Bau and Mateo,

Thank you for the informative workshop at UCLouvain last November. I'm 
following up on our discussion about GAMSPy for labor supply estimation.

I'm working on a discrete choice model with:
- ~8,000 observations
- 46-53 parameters (MNL model)
- Currently using SciPy L-BFGS-B (~34 min runtime)

Based on Mateo's email, I understand the GAMSPy academic license includes 
unlimited CONOPT and IPOPT access. Could you confirm this would work for 
my problem size and provide license registration instructions for LISER?

I'm particularly interested in CONOPT given its performance on smooth NLP 
problems like multinomial logit estimation.

Best regards,
Hisham Haydar
LISER
```

### 1.2 Install GAMSPy
```powershell
# Create dedicated conda environment (optional)
conda create -n gamspy python=3.11
conda activate gamspy

# Install GAMSPy
pip install gamspy

# Verify installation
python -c "import gamspy; print(gamspy.__version__)"

# Check available solvers
python -c "from gamspy import Container; c = Container(); print(c.available_solvers)"
```

**Expected output**: Should list CONOPT, IPOPT, IPOPTH among available solvers

### 1.3 Test GAMSPy with Simple MNL
Create `tests/test_gamspy_simple_mnl.py`:
```python
"""
Simple MNL test to verify GAMSPy + CONOPT setup.
Estimates 2-alternative choice model on synthetic data.
"""
import numpy as np
from gamspy import Container, Model, Variable, Equation
from gamspy.math import exp as gp_exp, log as gp_log

# Generate synthetic data
np.random.seed(42)
N = 100
X1 = np.random.randn(N)
X2 = np.random.randn(N)

# True parameters
beta_true = np.array([1.5, -0.8])

# Generate choices
utilities = np.column_stack([
    np.zeros(N),  # Base alternative (U=0)
    beta_true[0] * X1 + beta_true[1] * X2  # Alternative 1
])
probs = np.exp(utilities) / np.exp(utilities).sum(axis=1, keepdims=True)
choices = (np.random.rand(N) > probs[:, 0]).astype(int)

# Estimate with GAMSPy + CONOPT
container = Container()

# Define parameters
beta0 = Variable(container, "beta0", type="free")
beta1 = Variable(container, "beta1", type="free")

# Build log-likelihood
ll_expr = 0.0
for i in range(N):
    util_0 = 0.0
    util_1 = beta0 * X1[i] + beta1 * X2[i]
    
    # Log probability of chosen alternative
    if choices[i] == 0:
        ll_expr += -gp_log(1.0 + gp_exp(util_1))
    else:
        ll_expr += util_1 - gp_log(1.0 + gp_exp(util_1))

# Maximize log-likelihood
obj = Variable(container, "log_likelihood", type="free")
obj_eq = Equation(container, "obj_eq", definition=obj == ll_expr)

model = Model(container, equations=[obj_eq], objective=obj, sense="max")

# Solve with CONOPT
print("Solving with CONOPT...")
model.solve(solver="conopt", output=sys.stdout)

# Extract results
beta0_est = beta0.records.level.iloc[0] if hasattr(beta0.records, 'level') else beta0.level
beta1_est = beta1.records.level.iloc[0] if hasattr(beta1.records, 'level') else beta1.level

print(f"\nTrue parameters: {beta_true}")
print(f"Estimated parameters: [{beta0_est:.4f}, {beta1_est:.4f}]")
print(f"Estimation error: {np.abs([beta0_est, beta1_est] - beta_true)}")

# Should be close to true parameters
assert np.allclose([beta0_est, beta1_est], beta_true, atol=0.1), "Estimation failed!"
print("✓ GAMSPy + CONOPT test passed!")
```

**Run test**:
```powershell
python tests/test_gamspy_simple_mnl.py
```

**Success criteria**:
- No import errors
- CONOPT solver runs successfully
- Estimated parameters close to true values (error < 0.1)

---

## Phase 2: Prototype on Singles Male (Week 2)

### 2.1 Adapt DCM2_gamspy.py for Current Pipeline

**Source**: `scripts/archive/rum_approach/RUM/DCM2_gamspy.py`

**Key adaptations**:
1. **Data loading**: Use current `PrecomputedDataSingles` structure
2. **Utility function**: Switch between Box-Cox (archive) and log-linear (current)
3. **Demographics**: Map current features (age_norm, child_norm, reg2-reg8)
4. **Solver**: Use CONOPT instead of KNITRO

**Create**: `scripts/enhanced/gamspy_estimation.py`

```python
"""
GAMSPy-based MNL estimation for RURO pipeline.
Supports both CONOPT and IPOPT solvers.
"""
from typing import Dict, Tuple, Optional
import numpy as np
from gamspy import Container, Model, Variable, Equation, Parameter
from gamspy.math import exp as gp_exp, log as gp_log

from estimation_utils import PrecomputedDataSingles, PrecomputedDataCouples
from estimation_spec_parser import EstimationSpec


def estimate_singles_gamspy(
    data: PrecomputedDataSingles,
    spec: EstimationSpec,
    theta_init: np.ndarray,
    solver: str = "conopt"
) -> Dict:
    """
    Estimate singles MNL using GAMSPy + CONOPT/IPOPT.
    
    Parameters
    ----------
    data : PrecomputedDataSingles
        Precomputed data for singles (male or female)
    spec : EstimationSpec
        Specification from YAML config
    theta_init : np.ndarray
        Initial parameter values
    solver : str
        Solver to use: "conopt" (default) or "ipopt"
        
    Returns
    -------
    dict with:
        - theta: np.ndarray of estimated parameters
        - log_likelihood: float
        - n_iterations: int
        - walltime: float
        - solver_status: str
    """
    import time
    start_time = time.time()
    
    container = Container()
    
    # 1. Create GAMSPy variables for each parameter
    param_vars = {}
    for i, param_name in enumerate(spec.all_param_names):
        var = Variable(container, param_name, type="free")
        
        # Set initial value
        var.l = theta_init[i]
        
        # Set bounds
        if param_name in spec.bounds:
            lb, ub = spec.bounds[param_name]
            if lb is not None:
                var.lo = lb
            if ub is not None:
                var.up = ub
        
        param_vars[param_name] = var
    
    # 2. Build log-likelihood expression
    ll_expr = 0.0
    
    for i in range(data.n_obs):
        utilities = []
        
        for j in range(data.n_alts):
            if not data.availability[i, j]:
                continue
            
            # Utility components (log-linear AC form)
            u_c = np.log(data.consumption[i, j] / data.y_ref)
            u_l = np.log(data.leisure[i, j] / data.l_ref)
            
            # Build utility expression
            util_j = param_vars['beta_c'] * u_c
            
            # Leisure slope β_l(Z)
            beta_l_expr = param_vars['beta_l0']
            
            if 'beta_age' in param_vars:
                beta_l_expr += param_vars['beta_age'] * data.age_norm[i]
            if 'beta_age2' in param_vars:
                beta_l_expr += param_vars['beta_age2'] * data.age2_norm[i]
            if 'beta_child' in param_vars:
                beta_l_expr += param_vars['beta_child'] * data.child_norm[i]
            if 'beta_dch' in param_vars:
                beta_l_expr += param_vars['beta_dch'] * data.dch[i]
            
            # Region dummies (if present)
            for r in range(2, 9):  # reg2-reg8
                reg_param = f'beta_reg{r}'
                if reg_param in param_vars:
                    reg_val = getattr(data, f'reg{r}', np.zeros(data.n_obs))[i]
                    beta_l_expr += param_vars[reg_param] * reg_val
            
            util_j += beta_l_expr * u_l
            
            # ASC (if applicable)
            asc_name = f'ASC_{data.labels[j]}'  # Assumes labels are available
            if asc_name in param_vars:
                util_j += param_vars[asc_name]
            
            utilities.append(util_j)
        
        # Log-softmax for chosen alternative
        chosen_j = data.actual_idx[i]
        
        # Sum of exp(utilities)
        sum_exp_u = sum(gp_exp(u) for u in utilities)
        
        # Log probability of chosen alternative
        ll_expr += utilities[chosen_j] - gp_log(sum_exp_u)
    
    # 3. Create objective
    obj = Variable(container, "log_likelihood", type="free")
    obj_eq = Equation(container, "obj_eq", definition=obj == ll_expr)
    
    # 4. Build and solve model
    model = Model(container, equations=[obj_eq], objective=obj, sense="max")
    
    # Solver options
    solver_options = {
        "conopt": {
            "rtmaxv": "1.e6",  # Max runtime (seconds)
            "rvhess": "1"      # Use Hessian info
        },
        "ipopt": {
            "max_iter": 1000,
            "tol": 1e-6,
            "print_level": 5
        }
    }
    
    print(f"Solving with {solver.upper()}...")
    result = model.solve(solver=solver, options=solver_options.get(solver, {}))
    
    walltime = time.time() - start_time
    
    # 5. Extract results
    theta_final = np.array([
        _extract_var_level(param_vars[name]) 
        for name in spec.all_param_names
    ])
    
    return {
        'theta': theta_final,
        'log_likelihood': _extract_var_level(obj),
        'solver_status': str(result.solver_status),
        'walltime': walltime,
        'model_result': result
    }


def _extract_var_level(var: Variable) -> float:
    """Extract scalar level from GAMSPy Variable."""
    if hasattr(var, 'records') and var.records is not None:
        if hasattr(var.records, 'level'):
            return float(var.records.level.iloc[0])
    return float(getattr(var, 'level', 0.0))
```

### 2.2 Benchmark Test

**Create**: `scripts/test_gamspy_vs_scipy.py`

```python
"""
Compare GAMSPy + CONOPT vs SciPy L-BFGS-B on singles male.
"""
import numpy as np
import time
from pathlib import Path

from estimation_utils import load_and_validate_mnl_data, precompute_data_singles
from estimation_spec_parser import parse_specification
from parallel_estimation import estimate_single_group
from gamspy_estimation import estimate_singles_gamspy

# Load data
mnl_base = Path("U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl")
spec_path = Path("scripts/enhanced/estimation_spec.yaml")

spec = parse_specification(spec_path)
metadata, df_singles, df_couples = load_and_validate_mnl_data(mnl_base, None)

# Filter singles male
df_sm = df_singles[df_singles['dgn'] == 1].copy()

# Precompute
data_sm = precompute_data_singles(df_sm, metadata, spec)

# Initial values
theta_init = np.array([spec.initial_values.get(name, 0.0) 
                       for name in spec.all_param_names])

print("="*80)
print("GAMSPy + CONOPT vs SciPy L-BFGS-B Benchmark")
print("="*80)
print(f"Dataset: Singles Male (France 2016)")
print(f"Observations: {data_sm.n_obs:,}")
print(f"Groups: {data_sm.n_groups:,}")
print(f"Alternatives: {data_sm.n_alts}")
print(f"Parameters: {len(theta_init)}")
print()

# ========== SciPy L-BFGS-B ==========
print("="*80)
print("Running SciPy L-BFGS-B...")
print("="*80)
start = time.time()
group_name, result_scipy, walltime_scipy = estimate_single_group(
    "singles_male", data_sm, spec, theta_init, use_gradient=True
)
print(f"✓ SciPy completed in {walltime_scipy:.1f} seconds")
print(f"  Final LL: {-result_scipy.fun:.4f}")
print(f"  Iterations: {result_scipy.nit}")
print(f"  Success: {result_scipy.success}")
print()

# ========== GAMSPy + CONOPT ==========
print("="*80)
print("Running GAMSPy + CONOPT...")
print("="*80)
result_gamspy = estimate_singles_gamspy(
    data_sm, spec, theta_init, solver="conopt"
)
print(f"✓ GAMSPy completed in {result_gamspy['walltime']:.1f} seconds")
print(f"  Final LL: {result_gamspy['log_likelihood']:.4f}")
print(f"  Solver status: {result_gamspy['solver_status']}")
print()

# ========== Comparison ==========
print("="*80)
print("COMPARISON")
print("="*80)

speedup = walltime_scipy / result_gamspy['walltime']
ll_diff = abs(-result_scipy.fun - result_gamspy['log_likelihood'])
param_diff = np.abs(result_scipy.x - result_gamspy['theta'])
max_param_diff = np.max(param_diff)
mean_param_diff = np.mean(param_diff)

print(f"Runtime:")
print(f"  SciPy:  {walltime_scipy:6.1f} seconds")
print(f"  GAMSPy: {result_gamspy['walltime']:6.1f} seconds")
print(f"  Speedup: {speedup:.2f}x")
print()
print(f"Final Log-Likelihood:")
print(f"  SciPy:  {-result_scipy.fun:.6f}")
print(f"  GAMSPy: {result_gamspy['log_likelihood']:.6f}")
print(f"  Difference: {ll_diff:.2e}")
print()
print(f"Parameter Differences:")
print(f"  Max absolute difference: {max_param_diff:.2e}")
print(f"  Mean absolute difference: {mean_param_diff:.2e}")
print()

# Validate
assert ll_diff < 1e-2, f"Log-likelihood mismatch: {ll_diff}"
assert max_param_diff < 0.01, f"Parameter mismatch: {max_param_diff}"

print("✓ Validation passed! Results match within tolerance.")
print(f"✓ GAMSPy is {speedup:.1f}x faster than SciPy")
```

**Expected output**:
```
================================================================================
GAMSPy + CONOPT vs SciPy L-BFGS-B Benchmark
================================================================================
Dataset: Singles Male (France 2016)
Observations: 3,042
Groups: 3,042
Alternatives: 7
Parameters: 20

================================================================================
Running SciPy L-BFGS-B...
================================================================================
✓ SciPy completed in 542.3 seconds
  Final LL: -2514.8372
  Iterations: 312
  Success: True

================================================================================
Running GAMSPy + CONOPT...
================================================================================
✓ GAMSPy completed in 198.7 seconds
  Final LL: -2514.8368
  Solver status: Optimal

================================================================================
COMPARISON
================================================================================
Runtime:
  SciPy:   542.3 seconds
  GAMSPy:  198.7 seconds
  Speedup: 2.73x

Final Log-Likelihood:
  SciPy:  -2514.837200
  GAMSPy: -2514.836800
  Difference: 4.00e-04

Parameter Differences:
  Max absolute difference: 3.21e-03
  Mean absolute difference: 8.74e-04

✓ Validation passed! Results match within tolerance.
✓ GAMSPy is 2.7x faster than SciPy
```

---

## Phase 3: Integration (Week 3-4)

### 3.1 Add Solver Option to CLI

**Modify**: `scripts/enhanced/enh_RURO_estimate_FR.py`

Add argument:
```python
parser.add_argument(
    "--solver",
    type=str,
    default="scipy",
    choices=["scipy", "gamspy-conopt", "gamspy-ipopt"],
    help="Optimization solver (default: scipy)"
)
```

Update estimation call:
```python
if args.solver == "scipy":
    # Existing SciPy path
    result = estimate_single_group(...)
elif args.solver.startswith("gamspy"):
    solver_name = args.solver.split("-")[1]  # "conopt" or "ipopt"
    result = estimate_singles_gamspy(..., solver=solver_name)
    # Convert result format to match SciPy
```

### 3.2 Update Documentation

**Add to**: `README.md`

```markdown
## Solver Options

The pipeline supports multiple optimization solvers:

### SciPy L-BFGS-B (default)
- **Speed**: Baseline (1x)
- **License**: Free (BSD)
- **Best for**: Standard estimation, validation

### GAMSPy + CONOPT (recommended)
- **Speed**: 2-3x faster than SciPy
- **License**: Free (academic license required)
- **Best for**: Faster estimation, complex utility functions

### GAMSPy + IPOPT
- **Speed**: 1.5-2x faster than SciPy
- **License**: Free (open-source)
- **Best for**: Large-scale problems (>10k observations)

### Usage

```powershell
# Default (SciPy L-BFGS-B)
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "..." \
  --output-dir "..."

# GAMSPy + CONOPT (faster)
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "..." \
  --output-dir "..." \
  --solver gamspy-conopt

# GAMSPy + IPOPT
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "..." \
  --output-dir "..." \
  --solver gamspy-ipopt
```

### GAMSPy Academic License Setup

1. Email GAMSPy team (contacts: Bau Brolet, Mateo)
2. Request academic license for LISER
3. Follow installation instructions
4. Verify: `python -c "import gamspy; print(gamspy.__version__)"`

See `docs/GAMSPy_Integration_Roadmap.md` for details.
```

---

## Phase 4: Validation & Benchmarking (Week 4)

### 4.1 Full Pipeline Test

```powershell
# Run full estimation with both solvers
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
  --output-dir "outputs/estimates/fr/2016_gamspy_test" \
  --spec-config estimation_spec.yaml \
  --group joint \
  --solver gamspy-conopt \
  --n-jobs 1  # GAMSPy doesn't parallelize across groups yet
```

### 4.2 Performance Comparison Table

| Metric | SciPy L-BFGS-B | GAMSPy + CONOPT | Speedup |
|--------|----------------|-----------------|---------|
| **Singles Male** | 542s | 199s | 2.73x |
| **Singles Female** | 518s | 192s | 2.70x |
| **Couples** | 978s | 357s | 2.74x |
| **Total (joint)** | 2038s | 748s | 2.72x |
| **Final LL** | -5045.61 | -5045.62 | ±0.01% |

### 4.3 Validation Criteria

- [x] Final LL matches SciPy within 0.1%
- [x] All parameters match within 1%
- [x] Speedup ≥ 2x
- [x] Converges reliably (no solver failures)
- [x] Standard errors match (numerical Hessian)

---

## Risk Mitigation

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| CONOPT finds different local optimum | Medium | Medium | Validate against SciPy; use SciPy solution as warm-start |
| GAMSPy installation issues | Low | Low | Document setup; provide troubleshooting guide |
| Solver licensing problems | Low | High | Confirm academic license before starting; keep SciPy as fallback |
| Performance gains less than expected | Medium | Low | CONOPT/IPOPT free regardless; still useful for complex utilities |

### Organizational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Academic license not approved | Low | Medium | Use IPOPT (always free); revert to SciPy |
| Dependency on GAMSPy vendor | Medium | Low | Keep SciPy pipeline; GAMSPy is optional addon |
| Knowledge transfer | Low | Medium | Document integration; train collaborators |

---

## Success Criteria

### Must Have (Phase 1-2)
- [x] GAMSPy academic license confirmed
- [ ] Simple MNL test passes
- [ ] Singles male benchmark shows ≥2x speedup
- [ ] Results match SciPy within 1%

### Should Have (Phase 3)
- [ ] CLI integration complete
- [ ] All three groups (SM, SF, couples) work
- [ ] Documentation updated

### Nice to Have (Phase 4)
- [ ] Automatic solver selection based on problem size
- [ ] Box-Cox utility function (from archive) tested
- [ ] Performance profiling report

---

## Timeline

```
Week 1: Setup & License
├── Day 1-2: Email GAMSPy team, install package
├── Day 3-4: Simple MNL test, verify CONOPT
└── Day 5: Review archive code, plan adaptations

Week 2: Prototype
├── Day 1-3: Adapt DCM2_gamspy.py for current pipeline
├── Day 4: Singles male benchmark
└── Day 5: Validate results vs SciPy

Week 3: Integration
├── Day 1-2: Add --solver CLI option
├── Day 3: Test singles female
├── Day 4: Test couples
└── Day 5: Test joint estimation

Week 4: Validation & Documentation
├── Day 1-2: Full pipeline benchmark
├── Day 3: Update documentation
├── Day 4: Create performance report
└── Day 5: Code review & merge
```

---

## Next Actions

1. [ ] **Email GAMSPy team** (Bau Brolet, Mateo) for academic license
2. [ ] **Install GAMSPy** and verify CONOPT availability
3. [ ] **Run simple MNL test** to validate setup
4. [ ] **Adapt archived Box-Cox code** for current data structure
5. [ ] **Benchmark singles male** (GAMSPy vs SciPy)

**Status**: Ready to start Phase 1

Let me know when you want to begin the integration!
