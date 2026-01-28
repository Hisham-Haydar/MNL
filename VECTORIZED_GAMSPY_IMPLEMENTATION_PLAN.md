# Vectorized GAMSPy Implementation Plan

**Date:** 2026-01-28
**Goal:** Optimize GAMSPy estimation for production Python package
**Target:** 3-5x speedup, scalable to occupation choice (400 alternatives)

---

## Current Status

✅ **Created:** `gamspy_estimation_vectorized.py` with basic structure
⚠️ **TODO:** Complete implementation with full utility function and opportunity terms

---

## Architecture Overview

### Current (Line-by-Line) Approach
```python
ll_sm = 0.0
for g in range(n_individuals):  # Python loop
    utilities = []
    for j in range(n_alts):  # Python loop
        util_j = beta_c * bc(c[j], theta_c) + ...  # Create expression node
        utilities.append(util_j)

    ll_sm = ll_sm + log_prob_g  # Accumulate (creates new node each time)
```

**Problems:**
- Creates ~9M expression nodes for 7000 individuals × 100 alts
- Python loop overhead
- Expression tree grows linearly with each `ll = ll + term`

### Vectorized Approach
```python
# Define indexed sets
i_set = Set(container, "individuals", records=range(n_individuals))
j_set = Set(container, "alternatives", records=range(n_alts))

# Define data as 2D Parameters
consumption = Parameter(container, "consumption", domain=[i_set, j_set])
consumption[...] = data.consumption.reshape(n_individuals, n_alts)

# Build utility as INDEXED expression (single expression!)
utility[i, j] = beta_c * box_cox(consumption[i,j], theta_c) + ...

# Vectorized log-likelihood
chosen_util = Sum(j, chosen[i,j] * utility[i,j])
denom = Sum(j, exp(utility[i,j]))
ll = Sum(i, chosen_util - log(denom))
```

**Benefits:**
- Single expression tree (not 9M nodes)
- GAMSPy generates vectorized GAMS code
- GAMS compiles indexed operations efficiently
- Much smaller .gms file (10-50 MB vs 200-500 MB)

---

## Implementation Tasks

### ✅ **Phase 1: Foundation** (DONE)

- [x] Create `gamspy_estimation_vectorized.py`
- [x] Define indexed Sets (i_set, j_set)
- [x] Create 2D Parameters for consumption, leisure, chosen, prior
- [x] Basic utility function (consumption + leisure)
- [x] Vectorized log-likelihood structure
- [x] Parameter variables with bounds
- [x] Model creation and solve

### **Phase 2: Complete Utility Function** (TODO)

**File:** `gamspy_estimation_vectorized.py` (lines 300-350)

#### 2.1 Leisure Shifters

Add support for demographic shifters on leisure:

```python
# Age shifters
if 'beta_l_age_norm' in param_vars:
    age_norm_param = Parameter(container, "age_norm", domain=[i_set])
    age_norm_param[...] = data.age_norm  # Individual-level data

    beta_l_age = param_vars[f'beta_l_age_norm_{gender_suffix}']
    u_leisure = u_leisure + beta_l_age * age_norm_param * box_cox_transform(l_scaled, theta_l)

# Age squared
if 'beta_l_age_norm2' in param_vars:
    age_norm2_param = Parameter(container, "age_norm2", domain=[i_set])
    age_norm2_param[...] = data.age_norm2

    beta_l_age2 = param_vars[f'beta_l_age_norm2_{gender_suffix}']
    u_leisure = u_leisure + beta_l_age2 * age_norm2_param * box_cox_transform(l_scaled, theta_l)

# Number of children (females only)
if gender_suffix == 'sf' and 'beta_l_n_children_sf' in param_vars:
    n_children_param = Parameter(container, "n_children", domain=[i_set])
    n_children_param[...] = data.n_children

    beta_l_nchild = param_vars['beta_l_n_children_sf']
    u_leisure = u_leisure + beta_l_nchild * n_children_param * box_cox_transform(l_scaled, theta_l)

# Education shifters (educL, educH)
for educ_var in ['educL', 'educH']:
    if f'beta_l_{educ_var}_{gender_suffix}' in param_vars:
        educ_param = Parameter(container, f"{educ_var}", domain=[i_set])
        educ_param[...] = getattr(data, educ_var.lower())

        beta_l_educ = param_vars[f'beta_l_{educ_var}_{gender_suffix}']
        u_leisure = u_leisure + beta_l_educ * educ_param * box_cox_transform(l_scaled, theta_l)
```

**Effort:** 1-2 hours
**Testing:** Verify LL matches line-by-line approach

#### 2.2 Hours Opportunity Density

Add hours opportunity terms (working, pt1, pt2, ft, gsur):

```python
# Create indicator Parameters for hours
working_param = Parameter(container, "working", domain=[i_set, j_set])
working_param[...] = data.working.reshape(n_groups, n_alts)

pt1_param = Parameter(container, "working_pt1", domain=[i_set, j_set])
pt1_param[...] = data.working_pt1.reshape(n_groups, n_alts)

pt2_param = Parameter(container, "working_pt2", domain=[i_set, j_set])
pt2_param[...] = data.working_pt2.reshape(n_groups, n_alts)

ft_param = Parameter(container, "working_ft", domain=[i_set, j_set])
ft_param[...] = data.working_ft.reshape(n_groups, n_alts)

# Build hours opportunity
beta_work = param_vars['beta_work']
beta_pt1 = param_vars['beta_pt1']
beta_pt2 = param_vars['beta_pt2']
beta_ft = param_vars['beta_ft']

u_hours = (beta_work * working_param
           + beta_pt1 * pt1_param
           + beta_pt2 * pt2_param
           + beta_ft * ft_param)

# GSUR interaction (if present)
if 'beta_gsur' in param_vars and data.gsur is not None:
    gsur_param = Parameter(container, "gsur", domain=[i_set, j_set])
    gsur_param[...] = data.gsur.reshape(n_groups, n_alts)

    beta_gsur = param_vars['beta_gsur']
    u_hours = u_hours + beta_gsur * gsur_param * working_param

# Education × working interactions
for educ_var in ['educL', 'educH']:
    param_name = f'beta_work_{educ_var.lower()}'
    if param_name in param_vars:
        # Need individual-level educ expanded to all alternatives
        educ_indiv = getattr(data, educ_var.lower() + '_indiv')  # Individual level
        educ_expanded = np.repeat(educ_indiv, n_alts).reshape(n_groups, n_alts)

        educ_work_param = Parameter(container, f"{educ_var}_working", domain=[i_set, j_set])
        educ_work_param[...] = educ_expanded

        beta = param_vars[param_name]
        u_hours = u_hours + beta * educ_work_param * working_param

# Add to utility
utility = utility + u_hours
```

**Effort:** 2-3 hours
**Testing:** Check hours opportunity contributions

#### 2.3 Wage Opportunity Density

Add wage log-normal density for working alternatives:

```python
# Only for working alternatives (h > 0)
if data.log_wage is not None:
    log_wage_param = Parameter(container, "log_wage", domain=[i_set, j_set])
    log_wage_param[...] = data.log_wage.reshape(n_groups, n_alts)

    # Build wage mean: mu = beta_w0 + beta_w_educL*educL + beta_w_educH*educH + beta_pexp*exp + beta_pexp2*exp²
    beta_w0 = param_vars['beta_w0']
    mu_wage = beta_w0

    # Education effects
    for educ_var in ['educL', 'educH']:
        if f'beta_w_{educ_var.lower()}' in param_vars:
            educ_indiv = getattr(data, educ_var.lower() + '_indiv')
            educ_expanded = np.repeat(educ_indiv, n_alts).reshape(n_groups, n_alts)

            educ_param = Parameter(container, f"wage_{educ_var}", domain=[i_set, j_set])
            educ_param[...] = educ_expanded

            beta_w_educ = param_vars[f'beta_w_{educ_var.lower()}']
            mu_wage = mu_wage + beta_w_educ * educ_param

    # Experience effects
    if 'beta_pexp' in param_vars and data.pexp_years is not None:
        pexp_param = Parameter(container, "pexp_years", domain=[i_set])
        pexp_param[...] = data.pexp_years_indiv  # Individual level

        # Expand to alternatives
        pexp_expanded = np.repeat(data.pexp_years_indiv, n_alts).reshape(n_groups, n_alts)
        pexp_2d_param = Parameter(container, "pexp_expanded", domain=[i_set, j_set])
        pexp_2d_param[...] = pexp_expanded

        beta_pexp = param_vars['beta_pexp']
        mu_wage = mu_wage + beta_pexp * pexp_2d_param

        # Experience squared
        if 'beta_pexp2' in param_vars:
            pexp2_expanded = np.repeat(data.pexp_years2_indiv, n_alts).reshape(n_groups, n_alts)
            pexp2_param = Parameter(container, "pexp2_expanded", domain=[i_set, j_set])
            pexp2_param[...] = pexp2_expanded

            beta_pexp2 = param_vars['beta_pexp2']
            mu_wage = mu_wage + beta_pexp2 * pexp2_param

    # Log-normal density: log p(w) = -0.5 * [(log w - mu) / sigma]² - log(sigma) - 0.5*log(2π)
    sigma = param_vars['sigma']
    residual = log_wage_param - mu_wage

    log_wage_density = (-0.5 * (residual ** 2) / ((sigma ** 2) + LOG_EPS)
                        - gp_log(sigma + LOG_EPS)
                        - 0.5 * gp_log(2.0 * np.pi))

    # Multiply by working indicator (only contributes when h > 0)
    u_wage = log_wage_density * working_param

    # Add to utility
    utility = utility + u_wage
```

**Effort:** 2-3 hours
**Testing:** Compare wage contributions with line-by-line

---

### **Phase 3: Couples Estimation** (TODO)

**File:** `gamspy_estimation_vectorized.py` (new function)

Implement `_build_couples_utility_vectorized()`:

```python
def _build_couples_utility_vectorized(container, data_couples, param_vars, spec):
    """
    Build vectorized utility for couples.

    Requires:
    - Separate male and female utilities
    - Leisure interaction: beta_interact * BC(L_m) * BC(L_f)
    - Shared consumption utility
    """
    n_groups = data_couples.n_groups
    n_alts = data_couples.n_alts

    # Sets
    i_set = Set(container, "couples", records=[str(i) for i in range(n_groups)])
    j_set = Set(container, "alternatives", records=[str(j) for j in range(n_alts)])

    # Male data
    c_male = Parameter(container, "c_male", domain=[i_set, j_set])
    c_male[...] = data_couples.consumption_male.reshape(n_groups, n_alts)

    l_male = Parameter(container, "l_male", domain=[i_set, j_set])
    l_male[...] = data_couples.leisure_male.reshape(n_groups, n_alts)

    # Female data
    c_female = Parameter(container, "c_female", domain=[i_set, j_set])
    c_female[...] = data_couples.consumption_female.reshape(n_groups, n_alts)

    l_female = Parameter(container, "l_female", domain=[i_set, j_set])
    l_female[...] = data_couples.leisure_female.reshape(n_groups, n_alts)

    # Build male utility
    u_male = _build_individual_utility(c_male, l_male, param_vars, spec, gender='m')

    # Build female utility
    u_female = _build_individual_utility(c_female, l_female, param_vars, spec, gender='f')

    # Leisure interaction
    beta_interact = param_vars['beta_interact']

    l_scale = float(data_couples.l_scale)
    theta_l_m = param_vars.get('theta_l_m', 0.0)
    theta_l_f = param_vars.get('theta_l_f', 0.0)

    bc_l_male = box_cox_transform(l_male / l_scale, theta_l_m)
    bc_l_female = box_cox_transform(l_female / l_scale, theta_l_f)

    u_interact = beta_interact * bc_l_male * bc_l_female

    # Total utility
    utility = u_male + u_female + u_interact

    # Subtract prior
    prior = Parameter(container, "prior_cou", domain=[i_set, j_set])
    prior[...] = data_couples.prior.reshape(n_groups, n_alts)

    utility = utility - gp_log(prior + LOG_EPS)

    return utility
```

**Effort:** 3-4 hours
**Testing:** Compare couples LL with line-by-line

---

### **Phase 4: Joint Estimation** (TODO)

**File:** `gamspy_estimation_vectorized.py` (lines 450-600)

Complete `estimate_joint_vectorized_gamspy()`:

```python
def estimate_joint_vectorized_gamspy(...):
    # Create container
    container = Container()

    # Build singles male
    i_sm = Set(container, "individuals_sm", records=...)
    j_sm = Set(container, "alternatives_sm", records=...)
    utility_sm = _build_singles_utility_vectorized(container, data_sm, param_vars, spec, 'sm')
    ll_sm = _build_ll_vectorized(i_sm, j_sm, utility_sm, chosen_sm)

    # Build singles female
    i_sf = Set(container, "individuals_sf", records=...)
    j_sf = Set(container, "alternatives_sf", records=...)
    utility_sf = _build_singles_utility_vectorized(container, data_sf, param_vars, spec, 'sf')
    ll_sf = _build_ll_vectorized(i_sf, j_sf, utility_sf, chosen_sf)

    # Build couples
    i_cou = Set(container, "couples", records=...)
    j_cou = Set(container, "alternatives_cou", records=...)
    utility_cou = _build_couples_utility_vectorized(container, data_couples, param_vars, spec)
    ll_cou = _build_ll_vectorized(i_cou, j_cou, utility_cou, chosen_cou)

    # Combine
    ll_joint = ll_sm + ll_sf + ll_cou

    # Create model
    model = Model(container, "joint_mnl", problem="nlp", sense="max", objective=ll_joint)

    # Solve
    result = model.solve(solver=solver_name, solver_options=solver_options)

    return extract_results(result, param_vars, spec)
```

**Effort:** 2-3 hours
**Testing:** Compare with `gamspy_estimation.estimate_joint_gamspy()`

---

### **Phase 5: Occupation Choice Support** (TODO - Future)

**File:** `gamspy_estimation_vectorized.py` (new module)

Add occupation dimension to indexed structure:

```python
# 3D structure: individuals × alternatives × occupations
i_set = Set(container, "individuals", records=...)
j_set = Set(container, "hours_alts", records=range(100))  # Hours alternatives
k_set = Set(container, "occupations", records=range(4))    # Occupations

# 3D Parameters
consumption = Parameter(container, "consumption", domain=[i_set, j_set, k_set])
utility[i, j, k] = ...  # Occupation-specific utility

# Log-likelihood over 400 alternatives (100 hours × 4 occupations)
ll = Sum(i, chosen_util[i] - log(Sum([j,k], exp(utility[i,j,k]))))
```

**Effort:** 1-2 days
**Testing:** Verify with occupation choice data

---

## Testing Strategy

### Unit Tests

Create `test_gamspy_vectorized.py`:

```python
import pytest
from gamspy_estimation import estimate_singles_gamspy
from gamspy_estimation_vectorized import estimate_singles_vectorized_gamspy

def test_singles_male_equivalence(test_data_sm, test_spec, theta_init):
    """Verify vectorized gives same LL as line-by-line."""
    result_old = estimate_singles_gamspy(test_data_sm, test_spec, theta_init, solver="conopt")
    result_new = estimate_singles_vectorized_gamspy(test_data_sm, test_spec, theta_init, solver="conopt")

    assert abs(result_old['ll'] - result_new['ll']) < 1e-4, "LL mismatch!"
    assert np.allclose(result_old['theta'], result_new['theta'], atol=1e-3), "Parameter mismatch!"

def test_performance_improvement(test_data_sm, test_spec, theta_init):
    """Verify vectorized is faster."""
    from gamspy_estimation_vectorized import compare_performance

    results = compare_performance(test_data_sm, test_spec, theta_init, solver="conopt")

    assert results['speedup'] > 2.0, f"Expected >2x speedup, got {results['speedup']:.2f}x"
    assert results['ll_diff'] < 1e-4, f"LL difference too large: {results['ll_diff']}"
```

### Integration Tests

```python
def test_full_pipeline_france_2016():
    """Test full estimation pipeline on France 2016 data."""
    # Load data
    data_sm = load_france_2016_singles_male()
    data_sf = load_france_2016_singles_female()
    data_cou = load_france_2016_couples()

    # Load spec
    spec = parse_yaml("estimation_spec.yaml")

    # Get warm-start
    theta_init = load_warm_start("previous_run.pkl")

    # Run vectorized joint estimation
    result = estimate_joint_vectorized_gamspy(
        data_sm, data_sf, data_cou, spec, theta_init,
        solver="conopt"
    )

    # Check convergence
    assert result['status'] == 'Optimal'
    assert result['walltime'] < 300  # Should be < 5 minutes with warm-start
```

---

## Performance Benchmarks

### Expected Timings (France 2016, 100 alts, 7000 individuals)

| Stage | Line-by-Line | Vectorized | Speedup |
|-------|--------------|------------|---------|
| **A: Data loading** | <1s | <1s | 1x |
| **A→B: Expression building** | 30-60s | 5-10s | **5-6x** |
| **B: GAMS generation** | 1-3 min | 15-30s | **3-6x** |
| **B: GAMS compilation** | 30-120s | 10-20s | **3-6x** |
| **B→C: Data transfer** | 20-40s | 5-10s | **3-4x** |
| **C: CONOPT init** | 30-60s | 15-30s | **2x** |
| **C→D: Optimization** | 10-60s | 10-60s | 1x (same) |
| **TOTAL** | **5-8 min** | **1-3 min** | **3-5x** |

### Expected Timings (Occupation Choice, 400 alts)

| Stage | Line-by-Line | Vectorized | Speedup |
|-------|--------------|------------|---------|
| **A→B: Expression** | 2-4 min | 20-40s | **6x** |
| **B→C: Compilation** | 10-20 min | 2-4 min | **5x** |
| **C→D: Optimization** | 30-120s | 30-120s | 1x |
| **TOTAL** | **15-30 min** | **3-7 min** | **4-5x** |

---

## File Structure for Package

```
ruro_estimation/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── data_structures.py      # PrecomputedData classes
│   ├── spec_parser.py          # YAML parsing
│   └── box_cox.py              # Box-Cox utilities
├── estimation/
│   ├── __init__.py
│   ├── scipy_estimation.py     # SciPy L-BFGS-B (existing)
│   ├── gamspy_estimation.py    # GAMSPy line-by-line (legacy)
│   └── gamspy_vectorized.py    # GAMSPy vectorized (NEW, recommended)
├── tests/
│   ├── test_scipy.py
│   ├── test_gamspy_vectorized.py
│   └── fixtures/
│       └── test_data_small.pkl
└── docs/
    ├── api_reference.md
    ├── performance_guide.md
    └── examples/
```

---

## Timeline

### Week 1: Core Implementation
- **Day 1:** Complete Phase 2.1-2.2 (leisure shifters, hours opportunity)
- **Day 2:** Complete Phase 2.3 (wage opportunity)
- **Day 3:** Testing and debugging singles estimation

### Week 2: Couples and Joint
- **Day 4:** Phase 3 (couples utility)
- **Day 5:** Phase 4 (joint estimation)
- **Day 6-7:** Testing, benchmarking, documentation

### Week 3: Polish and Package
- **Day 8-9:** Refine API, add docstrings
- **Day 10:** Write comprehensive tests
- **Day 11:** Performance profiling and optimization
- **Day 12-13:** Documentation and examples
- **Day 14:** Package setup (setup.py, PyPI)

---

## API Design for Package

```python
# Simple API for end users
from ruro_estimation import estimate

# Automatic method selection
result = estimate(
    data=prepared_data,
    spec_file="estimation_spec.yaml",
    method="auto",  # Chooses best method automatically
    solver="conopt",
    warm_start="previous_run.pkl"
)

# Explicit method selection
result = estimate(
    data=prepared_data,
    spec_file="estimation_spec.yaml",
    method="gamspy-vectorized",  # Use optimized GAMSPy
    solver="conopt"
)

# Advanced: Direct access to vectorized estimator
from ruro_estimation.estimation import estimate_joint_vectorized

result = estimate_joint_vectorized(
    data_sm=data_singles_male,
    data_sf=data_singles_female,
    data_couples=data_couples,
    spec=spec_object,
    theta_init=theta_init,
    solver="conopt",
    solver_options={"rtmaxv": "1.e-3"}
)
```

---

## Next Steps

1. **IMMEDIATE:** Complete Phase 2 (utility function components)
2. **THIS WEEK:** Implement and test singles estimation
3. **NEXT WEEK:** Extend to joint estimation
4. **WEEK 3:** Package setup and documentation

Would you like me to:
- Start implementing Phase 2.1 (leisure shifters)?
- Create the test suite structure?
- Design the package API in more detail?
