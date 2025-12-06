# RURO_estimate_FR.py - Optimization Recommendations

## Summary

The code is well-optimized with several good practices:
- ✅ Pre-computed data structures to avoid DataFrame overhead
- ✅ Analytical gradients (10-50x faster than numerical)
- ✅ Vectorized NumPy operations
- ✅ Optional Numba JIT compilation
- ✅ Joblib parallelization for joint estimation

However, there are several improvements that can boost **speed** and **accuracy**:

---

## 🚀 SPEED IMPROVEMENTS

### 1. **Optimize the bincount loop in gradient computation** (~2x speedup)

**Problem**: The loop `for k in range(n_params): E_dV_per_group[:, k] = np.bincount(...)` is called every iteration.

**Solution**: Use a single matrix operation with sparse matrices or use `scipy.sparse.csr_matrix` for the group aggregation.

```python
# CURRENT (slow):
E_dV_per_group = np.zeros((data.n_groups, n_params), dtype=np.float64)
for k in range(n_params):
    E_dV_per_group[:, k] = np.bincount(data.group_idx, weights=P_weighted_dV[:, k], minlength=data.n_groups)

# IMPROVED (faster - use numba with prange):
@njit(parallel=True, cache=True, fastmath=True)
def _bincount_matrix_numba(group_idx, P_weighted_dV, n_groups):
    n, n_params = P_weighted_dV.shape
    E_dV = np.zeros((n_groups, n_params), dtype=np.float64)
    for i in prange(n):
        g = group_idx[i]
        for k in range(n_params):
            E_dV[g, k] += P_weighted_dV[i, k]
    return E_dV
```

### 2. **Pre-compute interaction terms** (minor speedup)

**Problem**: Terms like `data.working * data.gsur` are recomputed every iteration.

**Solution**: Pre-compute these in `PrecomputedDataSingles`:
```python
@dataclass
class PrecomputedDataSingles:
    # ... existing fields ...
    working_gsur: np.ndarray      # working * gsur
    working_educL: np.ndarray     # working * educL
    working_educH: np.ndarray     # working * educH
    working_reg2: np.ndarray      # working * reg2
    working_reg3: np.ndarray      # working * reg3
```

### 3. **Use float32 for large datasets** (memory/speed tradeoff)

For very large datasets (>1M rows), consider using `float32`:
```python
# In precompute_data_singles, add option:
dtype = np.float32 if use_float32 else np.float64
```

### 4. **Cache-friendly memory access** (10-20% speedup)

Ensure arrays are accessed in row-major (C) order:
```python
# When building dV_dtheta, ensure contiguous layout
dV_dtheta = np.ascontiguousarray(dV_dtheta)
```

### 5. **Avoid redundant computations in LL + gradient**

**Problem**: `fast_neg_ll_with_grad_singles` calls both functions separately, computing V twice.

**Solution**: Combine them:
```python
def fast_neg_ll_with_grad_combined(theta, data, is_male, wage_spec):
    """Compute LL and gradient in single pass - avoids recomputing V."""
    # Compute V and dV/dtheta once
    V, dV_dtheta = _compute_V_and_derivatives(theta, data, is_male, wage_spec)
    
    # Log-sum-exp for LL
    V_max_per_group = np.maximum.reduceat(V, data.group_starts)
    V_max = V_max_per_group[data.group_idx]
    exp_V_shifted = np.exp(V - V_max)
    sum_exp_per_group = np.bincount(data.group_idx, weights=exp_V_shifted, minlength=data.n_groups)
    
    # LL
    log_sum_exp_per_group = V_max_per_group + np.log(sum_exp_per_group)
    V_obs = V[data.obs_indices]
    ll = np.sum(V_obs - log_sum_exp_per_group)
    
    # Gradient (reuse exp_V_shifted)
    sum_exp = sum_exp_per_group[data.group_idx]
    P = exp_V_shifted / sum_exp
    # ... rest of gradient computation
    
    return -ll, -grad
```

---

## 🎯 ACCURACY IMPROVEMENTS

### 1. **Better parameter bounds for Box-Cox**

**Problem**: Box-Cox exponent `theta_l`, `theta_c` can go negative, causing instability.

**Solution**: Use tighter bounds:
```python
# Current bounds are (0.01, 2.0), consider:
bounds[9] = (0.05, 1.5)   # theta_l - more reasonable range
bounds[10] = (0.05, 1.5)  # theta_c
```

### 2. **Numerical stability in log-sum-exp**

**Problem**: Very large/small V values can cause overflow.

**Solution**: Already using max-subtraction trick, but add additional clipping:
```python
# Add clipping for extreme values
V = np.clip(V, -500, 500)  # exp(-500) ≈ 0, exp(500) would overflow
```

### 3. **Better handling of edge cases in wage equation**

**Problem**: When `sigma` approaches 0, the wage density blows up.

**Solution**: Use softplus transformation:
```python
# Instead of: sigma = abs(theta[36]) + 1e-6
# Use softplus for smoother optimization:
def softplus(x, beta=1.0):
    return np.log(1 + np.exp(beta * x)) / beta

sigma = softplus(theta[36]) + 0.1  # Ensures sigma >= 0.1
```

### 4. **Regularization for stability**

Add optional L2 regularization to prevent extreme parameter values:
```python
def fast_log_likelihood_singles(..., regularization=0.0):
    ll = ...  # normal LL
    if regularization > 0:
        ll -= 0.5 * regularization * np.sum(theta ** 2)
    return ll
```

### 5. **Gradient validation flag**

Add a debug mode to verify gradients:
```python
if validate_gradient:
    numerical_grad = numerical_gradient(lambda t: fast_log_likelihood_singles(t, data), theta)
    grad_error = np.max(np.abs(grad - numerical_grad))
    if grad_error > 1e-4:
        LOGGER.warning(f"Gradient error: {grad_error:.6f}")
```

---

## 🔧 CODE QUALITY IMPROVEMENTS

### 1. **Reduce code duplication**

The same theta unpacking code appears in multiple functions. Create a helper:
```python
def _unpack_theta_singles_fast(theta):
    """Unpack theta into named components for fast functions."""
    return {
        'beta_l0': theta[0], 'beta_l_log_age': theta[1], ...
    }
```

### 2. **Add type hints for clarity**

```python
from typing import NamedTuple

class SinglesParams(NamedTuple):
    pref: np.ndarray      # [0:12]
    hopp: np.ndarray      # [12:21]
    wopp: np.ndarray      # [21:37] or None
```

### 3. **Document parameter indices clearly**

Create constants:
```python
# Parameter indices for singles
IDX_PREF_START, IDX_PREF_END = 0, 12
IDX_HOPP_START, IDX_HOPP_END = 12, 21
IDX_WOPP_START, IDX_WOPP_END = 21, 37
```

---

## 📊 IMPLEMENTATION PRIORITY

| Priority | Improvement | Expected Speedup | Effort |
|----------|-------------|------------------|--------|
| HIGH | Combined LL+grad function | 30-50% | Medium |
| HIGH | Numba bincount matrix | 20-40% | Low |
| MEDIUM | Pre-compute interactions | 5-10% | Low |
| MEDIUM | Better Box-Cox bounds | N/A (accuracy) | Low |
| LOW | Float32 option | Memory savings | Low |

---

## Quick Win: Fast Combined Function

Here's the most impactful change - a combined LL+gradient function:

```python
def fast_neg_ll_with_grad_combined(
    theta: np.ndarray,
    data: PrecomputedDataSingles,
    is_male: bool = True,
    wage_spec: str = "fw",
) -> Tuple[float, np.ndarray]:
    """
    OPTIMIZED: Compute LL and gradient in single pass.
    Avoids recomputing V, Box-Cox, and softmax probabilities.
    ~30-50% faster than calling LL and grad separately.
    """
    n = len(data.c)
    n_params = 37 if wage_spec == "vw" else 21
    
    # Unpack theta once
    beta_l0, beta_l_log_age, beta_l_log_age2 = theta[0], theta[1], theta[2]
    # ... rest of unpacking ...
    
    # Box-Cox (computed once, used for both LL and grad)
    l_bc = _fast_boxcox(data.l, theta_l)
    c_bc = _fast_boxcox(data.c, theta_c)
    dl_bc_dtheta_l = _fast_d_boxcox_dtheta(data.l, theta_l)
    dc_bc_dtheta_c = _fast_d_boxcox_dtheta(data.c, theta_c)
    
    # Build V and dV_dtheta together
    # ... utility computation ...
    
    # Softmax (computed once, used for both)
    V_max_per_group = np.maximum.reduceat(V, data.group_starts)
    V_max = V_max_per_group[data.group_idx]
    exp_V_shifted = np.exp(V - V_max)
    sum_exp_per_group = np.bincount(data.group_idx, weights=exp_V_shifted, minlength=data.n_groups)
    
    # LL computation
    log_sum_exp_per_group = V_max_per_group + np.log(sum_exp_per_group)
    V_obs = V[data.obs_indices]
    ll = np.sum(V_obs - log_sum_exp_per_group)
    
    # Gradient computation (reuses exp_V_shifted and sum_exp_per_group)
    sum_exp = sum_exp_per_group[data.group_idx]
    P = exp_V_shifted / sum_exp
    P_weighted_dV = P[:, None] * dV_dtheta
    
    # Bincount for E[dV]
    E_dV_per_group = np.zeros((data.n_groups, n_params), dtype=np.float64)
    for k in range(n_params):
        E_dV_per_group[:, k] = np.bincount(data.group_idx, weights=P_weighted_dV[:, k], minlength=data.n_groups)
    E_dV = E_dV_per_group[data.group_idx, :]
    
    grad = (dV_dtheta[data.is_obs, :] - E_dV[data.is_obs, :]).sum(axis=0)
    
    return -ll, -grad
```
