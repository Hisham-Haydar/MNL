# Aaberge-Colombino (2013) Alignment Implementation Plan

## Executive Summary

This document describes the implementation plan for aligning the RURO France 2016 labor supply model with the specification in **Aaberge & Colombino (2013)** - *"Empirical Optimal Income Taxation: A Microeconometric Application to Norway"*.

The implementation maintains backward compatibility with the existing Stijn Van Houtven specification while adding A-C style features.

---

## 1. Inspection Findings

### 1.1 Current Specification Structure

| Component | Location | Current Implementation |
|-----------|----------|----------------------|
| **Utility function** | `estimation_engine.py:135-210` | Box-Cox with `theta_l`, `theta_c` |
| **Leisure shifters** | `estimation_spec.yaml:leisure_shifters` | Linear age, age², n_children |
| **Hours opportunity** | `estimation_engine.py:220-270` | Discrete logit with focal points |
| **Wage opportunity** | `estimation_engine.py:280-350` | Lognormal with education effects |
| **Couples utility** | `estimation_engine.py:500-650` | Additive male + female |

### 1.2 Variable Names Identified

| Purpose | Variable | Location |
|---------|----------|----------|
| Log consumption | `logy`, `consumption` | estimation_utils.py |
| Log leisure | `logl`, `leisure` | estimation_utils.py |
| Hours | `lhrs`, `hours` | estimation_spec.yaml |
| Log wage | `logw`, `log_wage` | estimation_utils.py |
| Age | `dage`, `age_norm` | estimation_spec.yaml |
| Children | `n_children`, `nch` | estimation_utils.py |
| Education | `educL`, `educM`, `educH` | estimation_spec.yaml |
| Unemployment | `gsur`, `u_rate` | estimation_spec.yaml |

### 1.3 Parameter Structure (4-Group Architecture)

| Group | Suffix | Description |
|-------|--------|-------------|
| Singles Male | `_sm` | Male singles parameters |
| Singles Female | `_sf` | Female singles parameters |
| Couples Male | `_cm` | Male in couples parameters |
| Couples Female | `_cf` | Female in couples parameters |

---

## 2. A-C 2013 vs Current Specification

### 2.1 Summary Comparison Table

| Block | Current (Stijn) | A-C 2013 | Status |
|-------|-----------------|----------|--------|
| **Hours opportunity** | Discrete logits (implicit h=0) | Discrete logits with explicit g₁×g₂ | **Kept** (relabeled) |
| **Wage equation** | μ = β₀ + β_educ | μ = β₀ + β_exp + β_exp² + β_educ | **Extended** |
| **Non-market mass** | Implicit in h=0 category | Explicit (1-p₁ₖ) term | **Clarified** |
| **Sector/occupation** | None | Placeholder for future | **Planned** |
| **Utility - consumption** | β_c * BC(c, θ_c) | Same | **Kept** |
| **Utility - leisure** | β_l * BC(l, θ_l) | Same with age/children shifters | **Extended** |
| **Utility - age terms** | β_age * age + β_age2 * age² | β_age * log(age) + β_age2 * log(age)² | **Changed** |
| **Utility - children** | β_nch * n_children (females) | β_C1*C1 + β_C2*C2 + β_C3*C3 | **Extended** |
| **Couples - joint opp** | Independent | μ₀ correlation parameter | **Added** |
| **Couples - leisure** | Additive U_m + U_f | + α_ll * BC(l_m) * BC(l_f) | **Added** |

### 2.2 Mathematical Specification

#### Singles Utility (A-C Style)

```
U(c, l; X, θ) = β_l(X) * BC(l, θ_l) + β_c * BC(c, θ_c)

Where:
  β_l(X) = β_l0 + β_age * log(age) + β_age2 * log(age)²
                + β_C1 * C1 + β_C2 * C2 + β_C3 * C3
                + β_nch * n_children  (females only, legacy)

  BC(x, θ) = (x^θ - 1) / θ    if |θ| > ε
           = log(x)            if |θ| ≤ ε  (A-C default: θ = 0)

  C1 = number of children aged 0-2
  C2 = number of children aged 3-6
  C3 = number of children aged 7-17
```

#### Wage Equation (A-C Extended)

```
log(w) ~ N(μ_w, σ²_w)

μ_w = β_w0 + β_exp * experience + β_exp2 * experience²
           + β_educL * educL + β_educH * educH
```

#### Couples Utility (A-C Style)

```
U_couple = U_m(c, l_m; X_m, θ_m) + U_f(c, l_f; X_f, θ_f) 
         + α_ll * BC(l_m, θ_lm) * BC(l_f, θ_lf)

Where:
  α_ll = cross-leisure interaction (complementarity if > 0)
```

#### Couples Joint Opportunity (A-C's μ₀)

```
log f_opp(h_m, h_f, w_m, w_f | X) = log f_h(h_m) + log f_h(h_f)
                                  + log f_w(w_m | h_m > 0) + log f_w(w_f | h_f > 0)
                                  + log(μ_0) * I(h_m > 0, h_f > 0)

Where:
  μ_0 > 1: positive assortative matching (both working more likely)
  μ_0 < 1: negative assortative matching
  μ_0 = 1: independent (no joint effect)
```

---

## 3. Implementation Plan

### 3.1 Files Created

| File | Purpose | Status |
|------|---------|--------|
| `estimation_spec_AC2013.yaml` | A-C style YAML specification | ✅ Created |
| `estimation_utils_AC2013.py` | A-C utility and opportunity functions | ✅ Created |
| `AC_alignment_plan.md` | This implementation plan | ✅ Created |

### 3.2 Files to Modify

| File | Changes Required | Priority |
|------|------------------|----------|
| `estimation_spec_parser.py` | Add AC2013 model version handling | High |
| `estimation_engine.py` | Integrate AC2013 utility functions | High |
| `parallel_estimation.py` | Add μ₀ and α_ll handling for couples | High |
| `estimation_utils.py` | Add experience term preprocessing | Medium |
| `enh_RURO_prep_mnl_basic.py` | Add child-age-group variables | Medium |
| `RURO_post_estimation_styled.py` | Add AC2013 diagnostics | Low |

### 3.3 Step-by-Step Implementation

#### Step 1: Update `estimation_spec_parser.py`

```python
# Add model version detection
def parse_specification(spec_path: Path) -> EstimationSpec:
    with open(spec_path, 'r') as f:
        config = yaml.safe_load(f)
    
    spec = EstimationSpec()
    spec.model_version = config.get('model_version', 'legacy')
    
    if spec.model_version == 'AC2013':
        # Parse AC2013-specific parameters
        _parse_ac2013_params(config, spec)
    else:
        # Existing legacy parsing
        _parse_legacy_params(config, spec)
    
    return spec
```

#### Step 2: Update `estimation_engine.py`

```python
# In _compute_utility_singles():
def _compute_utility_singles(params, data, spec):
    if spec.model_version == 'AC2013':
        from estimation_utils_AC2013 import compute_leisure_shifter_AC2013
        
        # Use log-age shifters
        beta_l = compute_leisure_shifter_AC2013(
            params, data.__dict__, gender_suffix
        )
    else:
        # Existing linear age shifters
        beta_l = compute_leisure_shifter_legacy(params, data, spec)
    
    # Rest of utility computation...
```

#### Step 3: Update `parallel_estimation.py`

```python
# In compute_likelihood_couples():
def compute_likelihood_couples(theta, data, spec):
    # ... existing code ...
    
    if spec.model_version == 'AC2013':
        from estimation_utils_AC2013 import (
            compute_cross_leisure_utility,
            compute_joint_market_availability
        )
        
        # Add cross-leisure interaction
        if 'alpha_ll' in params:
            U_cross = compute_cross_leisure_utility(
                data.leisure_male, data.leisure_female,
                params['theta_l_cm'], params['theta_l_cf'],
                params['alpha_ll']
            )
            u = u + U_cross
        
        # Add joint market availability
        if 'mu_0' in params:
            log_f_joint = compute_joint_market_availability(
                data.working_male, data.working_female,
                params['mu_0']
            )
            log_opp = log_opp + log_f_joint
    
    # ... rest of likelihood ...
```

#### Step 4: Update Data Preparation

In `enh_RURO_prep_mnl_basic.py`, ensure child-age-group variables are created:

```python
def prepare_children_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Add child-age-group variables if not present."""
    
    # Check for age-specific children counts
    if 'nch02' not in df.columns:
        # Try to derive from age-specific columns if available
        # Otherwise set to zero with warning
        df['nch02'] = 0
        df['nch36'] = 0
        df['nch717'] = 0
        logger.warning("Child-age-group variables not found, using zeros")
    
    return df
```

---

## 4. Testing Plan

### 4.1 Unit Tests

```python
# Test log-age transformation
def test_log_age_terms():
    ages = np.array([25, 35, 45, 55, 65])
    log_age, log_age_sq = compute_log_age_terms(ages)
    assert np.allclose(log_age, np.log(ages))
    assert np.allclose(log_age_sq, np.log(ages)**2)

# Test wage equation
def test_wage_mean_AC2013():
    params = {'beta_w0': 2.5, 'beta_exp': 0.03, 'beta_exp2': -0.0005}
    data = {'exp': np.array([10]), 'exp2': np.array([100])}
    mu_w = compute_wage_mean_AC2013(params, data)
    expected = 2.5 + 0.03 * 10 - 0.0005 * 100
    assert np.allclose(mu_w, expected)

# Test joint market availability
def test_joint_market_availability():
    w_m = np.array([1, 1, 0])
    w_f = np.array([1, 0, 1])
    log_f = compute_joint_market_availability(w_m, w_f, mu_0=1.5)
    assert log_f[0] == np.log(1.5)  # Both work
    assert log_f[1] == 0.0          # Only male works
    assert log_f[2] == 0.0          # Only female works
```

### 4.2 Integration Tests

```bash
# Small-sample test (sanity check)
python enh_RURO_estimate_FR.py \
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
  --spec-config estimation_spec_AC2013.yaml \
  --group singles_male \
  --output-dir outputs/AC_test_sm \
  --maxiter 100 \
  --verbose

# Compare legacy vs AC2013
python enh_RURO_estimate_FR.py \
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" \
  --spec-config estimation_spec.yaml \
  --group joint \
  --output-dir outputs/legacy_comparison \
  --verbose
```

### 4.3 Validation Checks

1. **Gradient finite check**: Ensure no NaN/Inf in gradients
2. **Log-likelihood improvement**: LL should increase during optimization
3. **Parameter bounds**: All estimates within specified bounds
4. **Convergence**: Gradient norm below tolerance at solution

---

## 5. Backward Compatibility

The implementation uses a **model version flag** in the YAML specification:

```yaml
model_version: "AC2013"  # or "legacy"
```

- `legacy`: Uses existing Stijn Van Houtven specification
- `AC2013`: Uses Aaberge-Colombino (2013) extensions

The estimation engine dispatches to the appropriate functions based on this flag.

---

## 6. Future Extensions

### 6.1 Sector/Occupation Effects

The A-C specification includes sector interactions. Placeholders are included:

```yaml
sector_shifters:
  enabled: false
  # Uncomment when sector data available:
  # beta_sector_public: {...}
  # beta_sector_service: {...}
```

### 6.2 LOC (Local Occupation Categories)

The existing LOC empirical specification can be extended with A-C features.

---

## 7. References

1. Aaberge, R., & Colombino, U. (2013). Using a microeconometric model of household labour supply to design optimal income tax. *Scandinavian Journal of Economics*, 115(2), 449-475.

2. Van Houtven, S. (RURO original implementation)

3. Bargain, O., et al. (EUROMOD microsimulation)

---

## 8. Changelog

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-09 | RURO Pipeline | Initial A-C alignment plan |
| 2026-01-09 | RURO Pipeline | Created estimation_spec_AC2013.yaml |
| 2026-01-09 | RURO Pipeline | Created estimation_utils_AC2013.py |

---

## 9. Quick Start

To use the A-C 2013 specification:

```powershell
# 1. Run estimation with AC2013 spec
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --spec-config "scripts/enhanced/estimation_spec_AC2013.yaml" `
  --group joint `
  --output-dir "outputs/estimates/fr/2016_AC2013" `
  --method L-BFGS-B `
  --maxiter 10000 `
  --verbose

# 2. Run post-estimation
python scripts/enhanced/RURO_post_estimation_styled.py `
  --results-json "outputs/estimates/fr/2016_AC2013/estimation_results.json" `
  --mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "outputs/estimates/fr/2016_AC2013"
```
