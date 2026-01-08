# COMPREHENSIVE IMPLEMENTATION PLAN: ADDRESSING HIGH GRADIENT NORMS AT CONVERGENCE

## EXECUTIVE SUMMARY

After thorough inspection of all provided files, I have identified the root causes of high gradient norms and developed a phased implementation plan. The core issues are:

1. **Premature convergence** due to default L-BFGS-B tolerances being too loose
2. **Parameters hitting bounds** (theta_l, theta_c = 0.0) creating non-zero gradients at constraint boundaries
3. **Missing gradient diagnostics** - no KKT-aware convergence checks or component-wise reporting
4. **Lack of gradient verification** - analytical gradients never validated against finite differences

---

## PHASE 0: GRADIENT VERIFICATION (CRITICAL FOUNDATION)

### Objective
Validate analytical gradient correctness using finite-difference checks before any optimization modifications.

### Files to Edit

#### 1. estimation_spec.yaml
**Location:** Top-level, new section after `optimization:`

**Changes:**
```yaml
# Add new section for gradient verification
gradient_verification:
  enabled: false  # Set to true to enable FD checks
  method: "central"  # "forward" or "central" (central is more accurate)
  epsilon: 1.0e-7  # Step size for finite differences
  tolerance: 1.0e-4  # Max acceptable |analytical - numerical| / |analytical|
  check_at_init: true  # Check gradient at initial values
  check_random_points: 0  # Number of random parameter vectors to test (0 = disabled)
  random_seed: 42  # Seed for reproducible random checks
  verbose: true  # Print detailed comparison
```

#### 2. estimation_spec_parser.py
**Location:** `EstimationSpec` dataclass (around line 30)

**Changes:**
Add new fields to dataclass:
```python
@dataclass
class EstimationSpec:
    # ... existing fields ...
    
    # Gradient verification settings
    grad_verify_enabled: bool = False
    grad_verify_method: str = "central"
    grad_verify_epsilon: float = 1e-7
    grad_verify_tolerance: float = 1e-4
    grad_verify_at_init: bool = True
    grad_verify_random_points: int = 0
    grad_verify_seed: int = 42
    grad_verify_verbose: bool = False
```

**Location:** `parse_specification()` function (around line 150)

**Changes:**
Add parsing for gradient_verification section:
```python
def parse_specification(yaml_path: Path) -> EstimationSpec:
    # ... existing code ...
    
    # Parse gradient verification settings
    grad_verify = config.get('gradient_verification', {})
    
    return EstimationSpec(
        # ... existing fields ...
        grad_verify_enabled=grad_verify.get('enabled', False),
        grad_verify_method=grad_verify.get('method', 'central'),
        grad_verify_epsilon=float(grad_verify.get('epsilon', 1e-7)),
        grad_verify_tolerance=float(grad_verify.get('tolerance', 1e-4)),
        grad_verify_at_init=grad_verify.get('check_at_init', True),
        grad_verify_random_points=int(grad_verify.get('check_random_points', 0)),
        grad_verify_seed=int(grad_verify.get('random_seed', 42)),
        grad_verify_verbose=grad_verify.get('verbose', False),
    )
```

#### 3. parallel_estimation.py
**Location:** New function before `estimate_single_group()` (around line 50)

**Changes:**
Add gradient verification function:
```python
def verify_gradient_finite_difference(
    theta: np.ndarray,
    data,
    spec: EstimationSpec,
    likelihood_fn: Callable,
    gradient_fn: Callable,
) -> Dict[str, Any]:
    """
    Verify analytical gradient using finite differences.
    
    Returns dict with:
        - max_rel_error: Maximum relative error across all parameters
        - max_abs_error: Maximum absolute error
        - param_errors: Array of relative errors per parameter
        - passed: Boolean indicating if verification passed
        - details: Detailed comparison for logging
    """
    logger = logging.getLogger(__name__)
    epsilon = spec.grad_verify_epsilon
    method = spec.grad_verify_method
    tol = spec.grad_verify_tolerance
    
    # Compute analytical gradient
    grad_analytical = gradient_fn(theta, data, spec)
    
    # Compute numerical gradient
    grad_numerical = np.zeros_like(theta)
    n_params = len(theta)
    
    for i in range(n_params):
        theta_plus = theta.copy()
        theta_minus = theta.copy()
        
        if method == 'central':
            theta_plus[i] += epsilon
            theta_minus[i] -= epsilon
            f_plus = likelihood_fn(theta_plus, data, spec)
            f_minus = likelihood_fn(theta_minus, data, spec)
            grad_numerical[i] = (f_plus - f_minus) / (2 * epsilon)
        else:  # forward
            theta_plus[i] += epsilon
            f_plus = likelihood_fn(theta_plus, data, spec)
            f_0 = likelihood_fn(theta, data, spec)
            grad_numerical[i] = (f_plus - f_0) / epsilon
    
    # Compute errors
    abs_errors = np.abs(grad_analytical - grad_numerical)
    rel_errors = abs_errors / (np.abs(grad_analytical) + 1e-12)  # Avoid division by zero
    
    max_abs_error = np.max(abs_errors)
    max_rel_error = np.max(rel_errors)
    
    passed = max_rel_error < tol
    
    # Build detailed comparison
    details = []
    details.append(f"Gradient Verification ({method} differences, ε={epsilon:.2e})")
    details.append("=" * 80)
    details.append(f"{'Parameter':<25} {'Analytical':>15} {'Numerical':>15} {'Abs Error':>15} {'Rel Error':>15}")
    details.append("-" * 80)
    
    for i in range(min(n_params, 50)):  # Limit to first 50 parameters for readability
        param_name = spec.all_param_names[i] if i < len(spec.all_param_names) else f"param_{i}"
        details.append(
            f"{param_name:<25} {grad_analytical[i]:>15.6e} {grad_numerical[i]:>15.6e} "
            f"{abs_errors[i]:>15.6e} {rel_errors[i]:>15.6e}"
        )
    
    if n_params > 50:
        details.append(f"... ({n_params - 50} more parameters)")
    
    details.append("=" * 80)
    details.append(f"Max absolute error: {max_abs_error:.6e}")
    details.append(f"Max relative error: {max_rel_error:.6e}")
    details.append(f"Tolerance: {tol:.6e}")
    details.append(f"Status: {'✓ PASSED' if passed else '✗ FAILED'}")
    
    return {
        'max_rel_error': float(max_rel_error),
        'max_abs_error': float(max_abs_error),
        'param_errors': rel_errors,
        'passed': passed,
        'details': '\n'.join(details)
    }
```

**Location:** `estimate_single_group()` function (around line 80), **before** `scipy.optimize.minimize` call

**Changes:**
Add gradient verification before optimization:
```python
def estimate_single_group(
    group_name: str,
    data,
    spec: EstimationSpec,
    theta_init: np.ndarray,
    use_gradient: bool = True
) -> Tuple[str, scipy.optimize.OptimizeResult, float]:
    
    logger = logging.getLogger(__name__)
    
    # ... existing setup code ...
    
    # ========================================================================
    # GRADIENT VERIFICATION (if enabled)
    # ========================================================================
    if spec.grad_verify_enabled and use_gradient:
        logger.info(f"[{group_name}] Running gradient verification...")
        
        # Determine likelihood and gradient functions
        if isinstance(data, PrecomputedDataSingles):
            from estimation_engine import compute_likelihood_singles, compute_gradient_singles
            likelihood_fn = compute_likelihood_singles
            gradient_fn = compute_gradient_singles
        else:
            from estimation_engine import compute_likelihood_couples, compute_gradient_couples
            likelihood_fn = compute_likelihood_couples
            gradient_fn = compute_gradient_couples
        
        # Check at initial values
        if spec.grad_verify_at_init:
            logger.info(f"[{group_name}] Checking gradient at initial values...")
            verify_result = verify_gradient_finite_difference(
                theta_init, data, spec, likelihood_fn, gradient_fn
            )
            
            if spec.grad_verify_verbose:
                logger.info(f"\n{verify_result['details']}")
            
            if not verify_result['passed']:
                logger.error(
                    f"[{group_name}] Gradient verification FAILED at initial values!\n"
                    f"Max relative error: {verify_result['max_rel_error']:.6e} "
                    f"(tolerance: {spec.grad_verify_tolerance:.6e})\n"
                    f"This indicates a bug in the analytical gradient computation."
                )
                raise ValueError(f"Gradient verification failed for {group_name}")
            else:
                logger.info(
                    f"[{group_name}] ✓ Gradient verification PASSED at initial values "
                    f"(max rel error: {verify_result['max_rel_error']:.6e})"
                )
        
        # Check at random points (if requested)
        if spec.grad_verify_random_points > 0:
            logger.info(
                f"[{group_name}] Checking gradient at {spec.grad_verify_random_points} random points..."
            )
            rng = np.random.default_rng(spec.grad_verify_seed)
            
            for point_idx in range(spec.grad_verify_random_points):
                # Generate random point within parameter bounds
                theta_random = theta_init.copy()
                bounds = spec.get_bounds_tuple()
                
                for i in range(len(theta_random)):
                    lb, ub = bounds[i]
                    if lb is None:
                        lb = theta_init[i] - 1.0
                    if ub is None:
                        ub = theta_init[i] + 1.0
                    theta_random[i] = rng.uniform(lb, ub)
                
                verify_result = verify_gradient_finite_difference(
                    theta_random, data, spec, likelihood_fn, gradient_fn
                )
                
                if not verify_result['passed']:
                    logger.error(
                        f"[{group_name}] Gradient verification FAILED at random point {point_idx + 1}!"
                    )
                    if spec.grad_verify_verbose:
                        logger.error(f"\n{verify_result['details']}")
                    raise ValueError(f"Gradient verification failed for {group_name}")
                else:
                    logger.info(
                        f"[{group_name}] ✓ Random point {point_idx + 1}/{spec.grad_verify_random_points} passed "
                        f"(max rel error: {verify_result['max_rel_error']:.6e})"
                    )
    
    # ... continue with existing optimization code ...
```

### Testing Commands

```bash
# 1. Enable gradient verification in spec
# Edit estimation_spec.yaml: set gradient_verification.enabled = true

# 2. Run estimation with verification
python enh_RURO_estimate_FR.py \
    --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
    --group singles_male \
    --maxiter 0 \
    --spec-config estimation_spec.yaml \
    --output-dir outputs/gradient_verification \
    --verbose

# Expected output:
# [singles_male] Running gradient verification...
# [singles_male] Checking gradient at initial values...
# [singles_male] ✓ Gradient verification PASSED at initial values (max rel error: 1.23e-05)
```

### Expected Outcomes

1. **If verification passes**: Analytical gradients are correct; proceed to Phase 1
2. **If verification fails**: 
   - **STOP** - fix gradient bugs in estimation_engine.py before proceeding
   - Check chain rule for Box-Cox derivatives
   - Verify sign conventions (negative log-likelihood vs positive)
   - Check array broadcasting issues

---

## PHASE 1: KKT-AWARE CONVERGENCE DIAGNOSTICS

### Objective
Add proper convergence checks that account for bound constraints using KKT (Karush-Kuhn-Tucker) conditions.

### Theoretical Background

For constrained optimization:
- **KKT conditions**: At optimum with active bounds, gradient perpendicular to constraints can be non-zero
- **Projected gradient**: g_proj[i] = 0 if parameter at bound, else g[i]
- **True convergence**: ||g_proj|| should be small, NOT ||g||

### Files to Edit

#### 1. parallel_estimation.py
**Location:** After `scipy.optimize.minimize` call in `estimate_single_group()` (around line 150)

**Changes:**
Add KKT-aware convergence check:
```python
def estimate_single_group(...):
    # ... existing code up to scipy.optimize.minimize ...
    
    result = scipy.optimize.minimize(
        fun=fun,
        x0=theta_init,
        args=(data, spec),
        jac=jac,
        method=spec.opt_method,
        bounds=spec.get_bounds_tuple(),
        options={
            'maxiter': spec.opt_max_iterations,
            'ftol': spec.opt_tolerance,
            'disp': False
        }
    )
    
    walltime = time.time() - start_time
    
    # ========================================================================
    # KKT-AWARE CONVERGENCE DIAGNOSTICS
    # ========================================================================
    if result.success:
        grad = result.jac  # Full gradient
        grad_norm_full = np.linalg.norm(grad)
        
        # Compute projected gradient (accounting for bounds)
        grad_proj = grad.copy()
        bounds = spec.get_bounds_tuple()
        theta_final = result.x
        
        n_at_lower = 0
        n_at_upper = 0
        bound_tol = 1e-8
        
        for i in range(len(theta_final)):
            lb, ub = bounds[i]
            
            # At lower bound: project out positive gradient components
            if lb is not None and abs(theta_final[i] - lb) < bound_tol:
                if grad[i] > 0:  # Gradient pointing into feasible region
                    grad_proj[i] = 0.0
                n_at_lower += 1
            
            # At upper bound: project out negative gradient components
            elif ub is not None and abs(theta_final[i] - ub) < bound_tol:
                if grad[i] < 0:  # Gradient pointing into feasible region
                    grad_proj[i] = 0.0
                n_at_upper += 1
        
        grad_norm_proj = np.linalg.norm(grad_proj)
        
        # Identify parameters with largest gradient components
        grad_abs = np.abs(grad)
        top_indices = np.argsort(grad_abs)[-10:][::-1]  # Top 10 by magnitude
        
        logger.info(f"[{group_name}] Convergence Diagnostics:")
        logger.info(f"  Full gradient norm:       {grad_norm_full:.6e}")
        logger.info(f"  Projected gradient norm:  {grad_norm_proj:.6e}")
        logger.info(f"  Parameters at lower bound: {n_at_lower}")
        logger.info(f"  Parameters at upper bound: {n_at_upper}")
        logger.info(f"  Optimizer message: {result.message}")
        
        # Component-wise gradient report
        logger.info(f"  Top 10 gradient components:")
        for idx in top_indices:
            param_name = spec.all_param_names[idx] if idx < len(spec.all_param_names) else f"param_{idx}"
            at_bound = ""
            if bounds[idx][0] is not None and abs(theta_final[idx] - bounds[idx][0]) < bound_tol:
                at_bound = " (at lower bound)"
            elif bounds[idx][1] is not None and abs(theta_final[idx] - bounds[idx][1]) < bound_tol:
                at_bound = " (at upper bound)"
            
            logger.info(
                f"    {param_name:<25} grad={grad[idx]:>12.6e} "
                f"value={theta_final[idx]:>10.6f}{at_bound}"
            )
        
        # Convergence assessment
        if grad_norm_proj > 10.0:
            logger.warning(
                f"⚠️  [{group_name}] HIGH PROJECTED GRADIENT NORM: {grad_norm_proj:.2f}\n"
                f"    Convergence is questionable even after accounting for bounds.\n"
                f"    Recommendations:\n"
                f"    1. Tighten ftol/gtol in optimization settings\n"
                f"    2. Increase max_iterations to allow more steps\n"
                f"    3. Review bounds on parameters at constraints"
            )
        elif grad_norm_proj > 1.0:
            logger.warning(
                f"⚠️  [{group_name}] Moderate projected gradient norm: {grad_norm_proj:.2f}\n"
                f"    May not be fully converged. Consider tightening tolerances."
            )
        else:
            logger.info(f"✓ [{group_name}] Projected gradient norm acceptable: {grad_norm_proj:.6e}")
    
    # ... rest of function ...
```

### Testing Commands

```bash
# Run estimation with new diagnostics (gradient verification disabled)
python enh_RURO_estimate_FR.py \
    --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
    --group joint \
    --maxiter 5000 \
    --spec-config estimation_spec.yaml \
    --output-dir outputs/test_diagnostics \
    --verbose

# Check log for convergence diagnostics section
grep -A 20 "Convergence Diagnostics" outputs/test_diagnostics/estimation.log
```

### Expected Output

```
[singles_male] Convergence Diagnostics:
  Full gradient norm:       843.24
  Projected gradient norm:  12.35
  Parameters at lower bound: 2
  Parameters at upper bound: 0
  Optimizer message: CONVERGENCE: RELATIVE REDUCTION OF F <= FACTR*EPSMCH
  Top 10 gradient components:
    theta_l                   grad= 8.234e+02  value=  0.000000 (at lower bound)
    theta_c                   grad= 3.156e+02  value=  0.000000 (at lower bound)
    beta_l0                   grad= 4.521e+00  value= -0.245502
    ...
⚠️  [singles_male] Moderate projected gradient norm: 12.35
    May not be fully converged. Consider tightening tolerances.
```

**Interpretation:**
- Full gradient norm (843.24) is misleadingly high due to `theta_l` and `theta_c` at bounds
- Projected gradient norm (12.35) shows actual non-convergence after removing bound effects
- Action required: Tighten tolerances or relax bounds

---

## PHASE 2: TIGHTER CONVERGENCE CONTROLS

### Objective
Fix premature convergence by tightening L-BFGS-B tolerances.

### Critical Discovery

**Location:** parallel_estimation.py, line ~140

```python
result = scipy.optimize.minimize(
    # ...
    method=spec.opt_method,
    bounds=spec.get_bounds_tuple(),
    options={
        'maxiter': spec.opt_max_iterations,
        'ftol': spec.opt_tolerance,  # ← Currently 1e-7 from YAML
        'disp': False
    }
)
```

**Issue:** Missing `gtol` parameter! L-BFGS-B defaults to `gtol=1e-5`, but we need tighter control.

**Also missing:** scipy's L-BFGS-B uses `ftol` for **function** tolerance, NOT the old `factr` parameter. The old scipy used `factr`, but modern scipy.optimize.minimize translates this internally. We should set both `ftol` and `gtol` explicitly.

### Files to Edit

#### 1. estimation_spec.yaml
**Location:** `optimization:` section (around line 170)

**Changes:**
```yaml
optimization:
  method: "L-BFGS-B"
  analytical_gradient: true
  max_iterations: 10000  # Increased from 5000
  
  # CRITICAL: L-BFGS-B convergence tolerances
  # ftol: relative change in f(x) must be > ftol * |f(x)| to continue
  # gtol: norm of projected gradient must be > gtol to continue
  tolerance: 1.0e-9      # ftol (function value relative change)
  gradient_tolerance: 1.0e-6  # gtol (projected gradient norm) - NEW!
  
  # Display settings
  disp: true
  iprint: 1  # Print iteration info every iteration
```

#### 2. estimation_spec_parser.py
**Location:** `EstimationSpec` dataclass (around line 45)

**Changes:**
```python
@dataclass
class EstimationSpec:
    # ... existing fields ...
    
    opt_method: str = "L-BFGS-B"
    opt_analytical_gradient: bool = True
    opt_max_iterations: int = 10000
    opt_tolerance: float = 1e-6  # ftol
    opt_gradient_tolerance: float = 1e-6  # gtol - NEW!
    opt_display_convergence: bool = False
```

**Location:** `parse_specification()` function (around line 200)

**Changes:**
```python
def parse_specification(yaml_path: Path) -> EstimationSpec:
    # ... existing code ...
    
    opt_config = config.get("optimization", {})
    opt_method = opt_config.get("method", "L-BFGS-B")
    opt_analytical_gradient = opt_config.get("analytical_gradient", True)
    opt_max_iterations = opt_config.get("max_iterations", 10000)
    opt_tolerance = float(opt_config.get("tolerance", 1e-6))
    opt_gradient_tolerance = float(opt_config.get("gradient_tolerance", 1e-6))  # NEW!
    opt_display = opt_config.get("disp", False)
    
    return EstimationSpec(
        # ... existing fields ...
        opt_method=opt_method,
        opt_analytical_gradient=opt_analytical_gradient,
        opt_max_iterations=opt_max_iterations,
        opt_tolerance=opt_tolerance,
        opt_gradient_tolerance=opt_gradient_tolerance,  # NEW!
        opt_display_convergence=opt_display,
    )
```

#### 3. parallel_estimation.py
**Location:** `estimate_single_group()`, `scipy.optimize.minimize` call (around line 140)

**Changes:**
```python
def estimate_single_group(...):
    # ... existing setup ...
    
    # Build options dict with EXPLICIT tolerances
    options = {
        'maxiter': spec.opt_max_iterations,
        'ftol': spec.opt_tolerance,           # Function value tolerance
        'gtol': spec.opt_gradient_tolerance,  # Gradient norm tolerance - NEW!
        'disp': spec.opt_display_convergence,
        'maxfun': 15000,  # Explicit max function evaluations
    }
    
    # L-BFGS-B specific: control iteration printing
    if spec.opt_method == 'L-BFGS-B':
        options['iprint'] = 1 if spec.opt_display_convergence else -1
    
    logger.info(f"[{group_name}] Optimizer settings:")
    logger.info(f"  method: {spec.opt_method}")
    logger.info(f"  ftol: {options['ftol']:.2e}")
    logger.info(f"  gtol: {options['gtol']:.2e}")
    logger.info(f"  maxiter: {options['maxiter']}")
    
    result = scipy.optimize.minimize(
        fun=fun,
        x0=theta_init,
        args=(data, spec),
        jac=jac,
        method=spec.opt_method,
        bounds=spec.get_bounds_tuple(),
        options=options
    )
    
    # ... rest of function ...
```

### Testing Commands

```bash
# 1. Update estimation_spec.yaml with tighter tolerances
# Set: tolerance: 1.0e-9, gradient_tolerance: 1.0e-6

# 2. Run estimation
python enh_RURO_estimate_FR.py \
    --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
    --group singles_male \
    --maxiter 10000 \
    --spec-config estimation_spec.yaml \
    --output-dir outputs/tight_tolerances \
    --verbose

# 3. Check convergence
python -c "
import json
with open('outputs/tight_tolerances/estimation_results.json') as f:
    r = json.load(f)
    for g in ['singles_male', 'singles_female', 'couples']:
        if g in r['results']:
            print(f'{g}: grad_norm={r[\"results\"][g][\"gradient_norm\"]:.2e}, iters={r[\"results\"][g][\"n_iterations\"]}')
"
```

### Expected Outcomes

- **Before:** gradient_norm ~843 (singles_male), ~316 (singles_female)
- **After:** gradient_norm < 10 for all groups (with projected norm < 1.0)
- **Iterations:** May increase from 123 → 300-500 due to tighter criteria
- **Final LL:** Should be slightly better (more optimal)

---

## PHASE 3: BOUND RELAXATION (IF NEEDED)

### Objective
If Phase 2 still shows high projected gradients, relax bounds on theta parameters.

### Diagnostic Check

After Phase 2, check Phase 1 diagnostics:
```
Parameters at lower bound: 2  ← theta_l, theta_c
Top gradient component: theta_l grad=8.234e+02 (at lower bound)
```

**If still seeing this:** theta parameters are stuck at 0.0 because optimizer wants negative values.

### Files to Edit

#### 1. estimation_spec.yaml
**Location:** `optimization.bounds:` section (around line 185)

**Current:**
```yaml
bounds:
  theta_l: [0.0, 5.0]  # Hitting lower bound!
  theta_c: [0.0, 5.0]  # Hitting lower bound!
```

**Option A: Small positive lower bound**
```yaml
bounds:
  theta_l: [0.001, 10.0]  # Allow near-zero but not exactly zero
  theta_c: [0.001, 10.0]  # Wider upper bound for flexibility
```

**Option B: Allow negative (if theoretically justified)**
```yaml
bounds:
  theta_l: [-2.0, 10.0]  # Allow negative curvature
  theta_c: [-2.0, 10.0]  # Requires careful economic interpretation
```

**Recommendation:** Start with Option A. Only use Option B if:
1. Economic theory allows negative theta (non-standard utility)
2. Option A still shows binding constraints

### Testing Commands

```bash
# After updating bounds in YAML
python enh_RURO_estimate_FR.py \
    --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
    --group joint \
    --maxiter 10000 \
    --spec-config estimation_spec.yaml \
    --output-dir outputs/relaxed_bounds \
    --verbose

# Check if parameters still at bounds
grep "at.*bound" outputs/relaxed_bounds/estimation.log
```

### Expected Outcomes

- **theta_l, theta_c** no longer at exactly 0.0
- **Projected gradient norm** drops below 1.0
- **Economic interpretation:** Check if estimated theta values make sense

---

## PHASE 4: PARAMETER SCALING (OPTIONAL - ONLY IF PHASES 0-3 INSUFFICIENT)

### Objective
If gradient norms remain high after Phases 0-3, implement parameter scaling for better numerical conditioning.

### Decision Criteria

**Implement scaling ONLY if:**
1. Phases 0-3 completed successfully
2. Projected gradient norm still > 1.0 after 10,000+ iterations
3. Hessian condition number estimated > 10^6 (very ill-conditioned)

### Implementation Strategy

**DO NOT** modify estimation_engine.py (too risky for core likelihood code). Instead, use **wrapper approach** in parallel_estimation.py.

### Files to Edit

#### 1. estimation_spec.yaml
**Location:** New top-level section

**Changes:**
```yaml
# Parameter scaling for numerical conditioning
parameter_scaling:
  enabled: false  # Set true to enable
  method: "typical_value"  # Scale by typical magnitude
  
  # Typical values for scaling (param_scaled = param_raw / scale)
  scales:
    # Preference parameters
    beta_l0: 1.0
    beta_l_age_norm: 0.1
    beta_l_age_norm2: 0.01
    beta_l_n_children: 1.0
    beta_l_educL: 1.0
    beta_l_educH: 1.0
    beta_c: 1.0
    theta_l: 1.0
    theta_c: 1.0
    
    # Hours opportunity
    beta_work: 1.0
    beta_pt1: 1.0
    beta_pt2: 1.0
    beta_ft: 1.0
    beta_gsur: 1.0
    beta_work_educL: 1.0
    beta_work_educH: 1.0
    
    # Wage equation (different magnitudes!)
    beta_w0: 1.0
    beta_w_educL: 1.0
    beta_w_educH: 1.0
    beta_pexp: 0.1
    beta_pexp2: 0.001  # Quadratic term is tiny - needs scaling!
    sigma: 1.0
    
    # Interaction
    beta_interact: 0.01
```

#### 2. estimation_spec_parser.py
**Location:** `EstimationSpec` dataclass

**Changes:**
```python
@dataclass
class EstimationSpec:
    # ... existing fields ...
    
    # Scaling configuration
    scaling_enabled: bool = False
    scaling_method: str = "typical_value"
    scaling_scales: Dict[str, float] = field(default_factory=dict)
    
    def scale_params(self, theta_raw: np.ndarray) -> np.ndarray:
        """Convert raw → scaled: theta_scaled = theta_raw / scale"""
        if not self.scaling_enabled:
            return theta_raw
        
        theta_scaled = theta_raw.copy()
        for i, param_name in enumerate(self.all_param_names):
            scale = self.scaling_scales.get(param_name, 1.0)
            theta_scaled[i] = theta_raw[i] / scale
        
        return theta_scaled
    
    def unscale_params(self, theta_scaled: np.ndarray) -> np.ndarray:
        """Convert scaled → raw: theta_raw = theta_scaled * scale"""
        if not self.scaling_enabled:
            return theta_scaled
        
        theta_raw = theta_scaled.copy()
        for i, param_name in enumerate(self.all_param_names):
            scale = self.scaling_scales.get(param_name, 1.0)
            theta_raw[i] = theta_scaled[i] * scale
        
        return theta_raw
    
    def scale_gradient(self, grad_raw: np.ndarray) -> np.ndarray:
        """Apply chain rule: ∂L/∂θ_scaled = (∂L/∂θ_raw) * scale"""
        if not self.scaling_enabled:
            return grad_raw
        
        grad_scaled = grad_raw.copy()
        for i, param_name in enumerate(self.all_param_names):
            scale = self.scaling_scales.get(param_name, 1.0)
            grad_scaled[i] = grad_raw[i] * scale  # Chain rule!
        
        return grad_scaled
    
    def scale_bounds(self) -> List[Tuple[Optional[float], Optional[float]]]:
        """Scale bounds: bound_scaled = bound_raw / scale"""
        if not self.scaling_enabled:
            return self.get_bounds_tuple()
        
        bounds_scaled = []
        raw_bounds = self.get_bounds_tuple()
        
        for i, param_name in enumerate(self.all_param_names):
            scale = self.scaling_scales.get(param_name, 1.0)
            lb_raw, ub_raw = raw_bounds[i]
            
            lb_scaled = lb_raw / scale if lb_raw is not None else None
            ub_scaled = ub_raw / scale if ub_raw is not None else None
            
            bounds_scaled.append((lb_scaled, ub_scaled))
        
        return bounds_scaled
```

**Location:** `parse_specification()` function

**Changes:**
```python
def parse_specification(yaml_path: Path) -> EstimationSpec:
    # ... existing code ...
    
    # Parse scaling
    scaling_config = config.get('parameter_scaling', {})
    scaling_enabled = scaling_config.get('enabled', False)
    scaling_method = scaling_config.get('method', 'typical_value')
    scaling_scales = scaling_config.get('scales', {})
    
    return EstimationSpec(
        # ... existing fields ...
        scaling_enabled=scaling_enabled,
        scaling_method=scaling_method,
        scaling_scales=scaling_scales,
    )
```

#### 3. parallel_estimation.py
**Location:** `estimate_single_group()` function, **wrap** objective and gradient

**Changes:**
```python
def estimate_single_group(...):
    # ... existing setup ...
    
    # Determine base likelihood and gradient functions
    if isinstance(data, PrecomputedDataSingles):
        from estimation_engine import compute_likelihood_singles, compute_gradient_singles
        base_fun = compute_likelihood_singles
        base_jac = compute_gradient_singles
    else:
        from estimation_engine import compute_likelihood_couples, compute_gradient_couples
        base_fun = compute_likelihood_couples
        base_jac = compute_gradient_couples
    
    # ========================================================================
    # PARAMETER SCALING WRAPPERS (if enabled)
    # ========================================================================
    if spec.scaling_enabled:
        logger.info(f"[{group_name}] Parameter scaling ENABLED")
        
        def fun(theta_scaled, data, spec):
            """Wrapper: scaled → raw → likelihood"""
            theta_raw = spec.unscale_params(theta_scaled)
            return base_fun(theta_raw, data, spec)
        
        def jac(theta_scaled, data, spec):
            """Wrapper: scaled → raw → gradient → scaled gradient"""
            theta_raw = spec.unscale_params(theta_scaled)
            grad_raw = base_jac(theta_raw, data, spec)
            grad_scaled = spec.scale_gradient(grad_raw)
            return grad_scaled
        
        # Scale initial values and bounds
        theta_init_scaled = spec.scale_params(theta_init)
        bounds_scaled = spec.scale_bounds()
        
        logger.info(f"  Initial params (scaled): {theta_init_scaled[:5]}...")  # Show first 5
    else:
        # No scaling - use base functions directly
        fun = base_fun
        jac = base_jac if use_gradient else None
        theta_init_scaled = theta_init
        bounds_scaled = spec.get_bounds_tuple()
    
    # Run optimization (now in scaled space if enabled)
    result = scipy.optimize.minimize(
        fun=fun,
        x0=theta_init_scaled,
        args=(data, spec),
        jac=jac,
        method=spec.opt_method,
        bounds=bounds_scaled,
        options={
            'maxiter': spec.opt_max_iterations,
            'ftol': spec.opt_tolerance,
            'gtol': spec.opt_gradient_tolerance,
            'disp': spec.opt_display_convergence,
        }
    )
    
    # ========================================================================
    # UNSCALE RESULTS (if scaling was used)
    # ========================================================================
    if spec.scaling_enabled:
        # Convert final parameters back to raw scale
        result.x = spec.unscale_params(result.x)
        
        # Convert gradient back to raw scale (for diagnostics)
        if hasattr(result, 'jac') and result.jac is not None:
            # Inverse chain rule: grad_raw = grad_scaled / scale
            grad_raw = result.jac.copy()
            for i, param_name in enumerate(spec.all_param_names):
                scale = spec.scaling_scales.get(param_name, 1.0)
                grad_raw[i] = result.jac[i] / scale
            result.jac = grad_raw
        
        logger.info(f"[{group_name}] Unscaled final parameters to raw values")
    
    # ... continue with existing convergence diagnostics (Phase 1) ...
```

### Testing Commands

```bash
# 1. Enable scaling in YAML
# Set: parameter_scaling.enabled = true

# 2. Run estimation
python enh_RURO_estimate_FR.py \
    --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
    --group singles_male \
    --maxiter 10000 \
    --spec-config estimation_spec.yaml \
    --output-dir outputs/with_scaling \
    --verbose

# 3. Compare gradient norms with/without scaling
diff <(grep "gradient norm" outputs/tight_tolerances/estimation.log) \
     <(grep "gradient norm" outputs/with_scaling/estimation.log)
```

### Expected Outcomes

- **Gradient norm** should drop by factor of 10-100 due to better conditioning
- **Iterations** may decrease (optimizer converges faster)
- **Final parameters** should be identical to unscaled run (within numerical precision)

---

## MINIMAL VIABLE PATCH SET

The **smallest** set of changes to get correct convergence + diagnostics:

### Must-Have Changes (Complete in Order)

1. **Phase 0 - Gradient Verification** (1-2 hours)
   - estimation_spec.yaml: Add `gradient_verification` section
   - estimation_spec_parser.py: Add 8 fields to `EstimationSpec`, parse YAML
   - parallel_estimation.py: Add `verify_gradient_finite_difference()` function (60 lines)
   - parallel_estimation.py: Add verification call in `estimate_single_group()` (40 lines)
   - **Test immediately** - if gradient verification fails, STOP and fix bugs first

2. **Phase 1 - KKT Diagnostics** (1 hour)
   - parallel_estimation.py: Add post-optimization diagnostics in `estimate_single_group()` (60 lines)
   - Compute projected gradient norm, report top components, warn if high
   - **Test** - confirms whether issue is truly non-convergence or just bound effects

3. **Phase 2 - Tighter Tolerances** (30 minutes)
   - estimation_spec.yaml: Add `gradient_tolerance: 1.0e-6`, set `tolerance: 1.0e-9`
   - estimation_spec_parser.py: Add `opt_gradient_tolerance` field
   - parallel_estimation.py: Add `gtol` to optimizer options dict
   - **Test** - should reduce projected gradient norm to < 1.0

### Optional Changes (Only If Needed)

4. **Phase 3 - Bound Relaxation** (15 minutes)
   - estimation_spec.yaml: Change `theta_l/theta_c` bounds from `[0.0, 5.0]` to `[0.001, 10.0]`
   - Only needed if Phase 2 shows parameters stuck at bounds

5. **Phase 4 - Parameter Scaling** (3-4 hours)
   - Complex implementation - only if Phases 1-3 fail
   - Not recommended unless Hessian severely ill-conditioned

### Total Effort Estimate

- **Minimum (Phases 0-2)**: 2.5-3.5 hours implementation + 1 hour testing = **4.5 hours**
- **With bound relaxation**: +0.5 hours = **5 hours**
- **With scaling**: +4 hours = **9 hours** (but likely unnecessary)

---

## FILES MODIFIED SUMMARY

### Core Changes (Phases 0-2)
1. estimation_spec.yaml - 25 new lines
2. estimation_spec_parser.py - 15 new lines + 1 new method
3. parallel_estimation.py - 160 new lines (1 new function, modifications to 1 existing)

### Optional Changes (Phase 3)
4. estimation_spec.yaml - 2 line edits

### Advanced Changes (Phase 4)
5. estimation_spec.yaml - 35 new lines
6. estimation_spec_parser.py - 80 new lines + 4 new methods
7. parallel_estimation.py - 40 line modifications

### Total Lines of Code
- **Minimum patch**: ~200 LOC
- **Full implementation**: ~400 LOC

---

## VALIDATION CHECKLIST

After implementing each phase, verify:

### Phase 0
- [ ] Gradient verification passes at initial values (max rel error < 1e-4)
- [ ] If random checks enabled, all pass
- [ ] Verification can be disabled via YAML flag

### Phase 1
- [ ] Log shows "Convergence Diagnostics" section after each group
- [ ] Projected gradient norm reported separately from full norm
- [ ] Top 10 gradient components listed with bound status
- [ ] Warning issued if projected norm > 1.0

### Phase 2
- [ ] Log shows `gtol` and `ftol` values before optimization
- [ ] Projected gradient norm < 1.0 for all groups
- [ ] Iterations may increase but final LL improves
- [ ] No warnings about questionable convergence

### Phase 3 (if needed)
- [ ] Parameters no longer at bounds
- [ ] Projected gradient norm < 1.0
- [ ] Estimated theta values economically interpretable

### Phase 4 (if needed)
- [ ] Final parameters identical to unscaled run (within 1e-6)
- [ ] Gradient verification still passes with scaling enabled
- [ ] Iterations decrease compared to unscaled

---

## RISK MITIGATION

### High-Risk Areas

1. **Gradient verification** - If this fails, entire estimation is suspect
   - Mitigation: Implement first, fix bugs before proceeding
   
2. **Chain rule in scaling** - Easy to get sign wrong
   - Mitigation: Re-run gradient verification with scaling enabled

3. **Bound scaling** - Can create infeasible regions
   - Mitigation: Log scaled bounds, verify manually

### Rollback Plan

Each phase is independent - can disable via YAML flags:
```yaml
gradient_verification:
  enabled: false  # Disable Phase 0

parameter_scaling:
  enabled: false  # Disable Phase 4
```

Phases 1-3 cannot be disabled but are non-breaking (only add diagnostics/tighten tolerances).

---

## CONCLUSION

This plan provides a **systematic, testable, and minimal** approach to fixing the high gradient norm issue:

1. **Phase 0** validates correctness
2. **Phase 1** diagnoses the real problem
3. **Phase 2** fixes the most likely cause (loose tolerances)
4. **Phase 3** addresses bound constraints if needed
5. **Phase 4** is a fallback for extreme cases

**Recommended sequence:** Implement Phases 0-2 (4.5 hours), test thoroughly, then decide if Phase 3 is needed. Phase 4 should only be considered if all else fails.

The projected gradient norm diagnostic (Phase 1) is the **key innovation** - it separates real non-convergence from bound effects, which was the root cause of the confusion in the original results.