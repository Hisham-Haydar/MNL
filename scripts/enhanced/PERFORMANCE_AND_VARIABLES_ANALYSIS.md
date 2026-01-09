# Performance and Variables Analysis Report

## 1. Variable Availability Summary

### Data Location
- **Singles MNL**: `U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl__singles.parquet`
- **Couples MNL**: `U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl__couples.parquet`

### Legacy Specification Variables

| Expected Variable | Available Column | Status |
|-------------------|------------------|--------|
| `logy` | `log_c` | ✅ Available |
| `logl` | `log_l` | ✅ Available |
| `lhrs` | `hours` | ✅ Available |
| `logw` | `wage` (need `np.log()`) | ✅ Available |
| `dage` | `dag` | ✅ Available |
| `dage2` | Compute from `dag**2` | ⚠️ Derive |
| `pexp` | `pexp` or `pexp_years` | ✅ Available |
| `pexp2` | `pexp_years2` | ✅ Available |
| `age_norm` | `age_norm` | ✅ Available |
| `age_norm2` | `age_norm2` | ✅ Available |
| `educL` | `educL` | ✅ Available |
| `educH` | `educH` | ✅ Available |
| `n_children` | `n_children` | ✅ Available |
| `working` | `working` | ✅ Available |
| `pt1` | `working_pt1` | ✅ Available |
| `pt2` | `working_pt2` | ✅ Available |
| `ft` | `working_ft` | ✅ Available |
| `gsur` | ❌ Not found | ❌ **MISSING** |

### AC2013 Specification Variables (Additional)

| Expected Variable | Available Column | Status |
|-------------------|------------------|--------|
| `nch02` (children 0-2) | `num_children_0_3` | ⚠️ Close match |
| `nch36` (children 3-6) | `num_children_3_6` | ✅ Available |
| `nch717` (children 7-17) | `num_children_6_11` + `num_children_11_17` | ⚠️ Combine |

### Key Findings

1. **GSUR (Regional Unemployment Rate)** is missing from the data
   - The YAML spec includes it but the data doesn't have it
   - **Solution**: Either add GSUR to data preprocessing, or remove from YAML spec

2. **Age groups for children** need minor adjustments:
   - Data has: `num_children_0_3, num_children_3_6, num_children_6_11, num_children_11_17`
   - AC2013 expects: `nch02, nch36, nch717`

---

## 2. Memory and Loading Performance

### Current State (Loading ALL 954 Columns)
```
Shape: 167,600 rows × 954 columns
Memory: 1,213 MB (1.2 GB)
Load time: 2.14 seconds
```

### Optimized State (Loading Only Needed ~26 Columns)
```
Shape: 167,600 rows × 26 columns  
Memory: 33 MB
Load time: 0.05 seconds
```

### Impact
| Metric | Improvement |
|--------|-------------|
| Memory | **97.3% reduction** (1.2 GB → 33 MB) |
| Load time | **97.6% reduction** (2.1s → 0.05s) |

### Recommendation
**Add column filtering to data loading in `estimation_utils.py`:**
```python
# Instead of:
df = pd.read_parquet(path)

# Use:
needed_cols = ['log_c', 'log_l', 'hours', 'wage', 'dag', 'pexp', ...]
df = pd.read_parquet(path, columns=needed_cols)
```

---

## 3. Vectorization Analysis

### Current Code Status: **Partially Vectorized**

#### ✅ Well Vectorized (NumPy operations):
- Box-Cox transformations: `box_cox_transform()` uses pure NumPy
- Utility computation: Most operations are vectorized array operations
- Wage likelihood: Uses vectorized normal PDF computation
- Gradient computation: Uses vectorized operations

#### ⚠️ Bottleneck: `compute_log_sum_exp_by_group()`
```python
def compute_log_sum_exp_by_group(V, group_starts, group_ends):
    n_groups = len(group_starts)
    lse = np.zeros(n_groups)
    
    for i in range(n_groups):  # ← PYTHON LOOP over 4,253 groups!
        start, end = group_starts[i], group_ends[i]
        V_group = V[start:end]
        max_V = V_group.max()
        lse[i] = max_V + np.log(np.sum(np.exp(V_group - max_V)))
    
    return lse
```

**This loop runs 4,253 times per likelihood evaluation!**
- With L-BFGS-B doing ~100s of iterations
- Each iteration needs 1 likelihood + 1 gradient (with n_params finite differences internally)
- **Total: potentially 100,000s of calls to this function**

### Optimization Options

#### Option 1: Numba JIT Compilation
```python
from numba import jit, prange

@jit(nopython=True, parallel=True)
def compute_log_sum_exp_by_group_numba(V, group_starts, group_ends):
    n_groups = len(group_starts)
    lse = np.zeros(n_groups)
    
    for i in prange(n_groups):  # Parallel loop!
        start, end = group_starts[i], group_ends[i]
        V_group = V[start:end]
        max_V = V_group.max()
        lse[i] = max_V + np.log(np.sum(np.exp(V_group - max_V)))
    
    return lse
```
**Expected speedup: 10-50x**

#### Option 2: scipy.special.logsumexp with segments
```python
from scipy.ndimage import maximum_filter1d
from scipy.special import logsumexp

# Pre-compute segment indices
def compute_lse_vectorized(V, group_starts, group_ends):
    # Use np.add.reduceat for segment operations
    ...
```

---

## 4. Why is Estimation Taking So Long?

### Estimation Parameters
- **4,253 household groups** (766 male singles + 910 female singles + 2,577 couples)
- **425,300 total observations** (100 alternatives per group)
- **46 parameters** to estimate
- **L-BFGS-B optimizer** with analytical gradients

### Time Breakdown (Estimated)

| Component | Per Iteration | Iterations | Total |
|-----------|---------------|------------|-------|
| Likelihood eval | ~0.1-0.5s | ~500-1000 | ~50-500s |
| Gradient eval | ~0.1-0.5s | ~500-1000 | ~50-500s |
| Optimizer overhead | negligible | - | - |
| **Total** | | | **~2-15 minutes** |

### Why Longer Than Expected?

1. **Python loops** in `compute_log_sum_exp_by_group()` - called thousands of times
2. **Large memory footprint** - loading unnecessary columns slows down cache performance
3. **Couples have 100×100 = 10,000 alternatives** per household - very large choice sets

---

## 5. Recommended Optimizations

### Immediate (Easy, High Impact)
1. ✅ **Filter columns on load** - 97% memory reduction
2. ✅ **Add Numba JIT to log-sum-exp loop** - 10-50x speedup

### Medium-term
3. **Reduce couples alternatives** - Consider 20×20 = 400 instead of 100×100 = 10,000
4. **Use multiprocessing for gradient** - Parallelize parameter gradient computation

### Long-term
5. **GPU acceleration** - JAX or PyTorch for very large datasets
6. **Compiled estimation** - Cython or C++ for core likelihood

---

## 6. Quick Fix Script

To immediately improve performance, add this to `estimation_utils.py`:

```python
# At top of file
try:
    from numba import jit, prange
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

# Replace compute_log_sum_exp_by_group with:
if HAS_NUMBA:
    @jit(nopython=True, parallel=True)
    def _compute_lse_numba(V, group_starts, group_ends):
        n_groups = len(group_starts)
        lse = np.zeros(n_groups)
        for i in prange(n_groups):
            start, end = group_starts[i], group_ends[i]
            max_V = -1e300
            for j in range(start, end):
                if V[j] > max_V:
                    max_V = V[j]
            sum_exp = 0.0
            for j in range(start, end):
                sum_exp += np.exp(V[j] - max_V)
            lse[i] = max_V + np.log(sum_exp)
        return lse
    
    compute_log_sum_exp_by_group = _compute_lse_numba
```

---

## Summary

| Issue | Impact | Fix Difficulty |
|-------|--------|----------------|
| Loading 954 columns | High memory, slow | Easy |
| Python loop in LSE | Major bottleneck | Medium (Numba) |
| Missing GSUR variable | Estimation may fail | Check YAML |
| Large couples choice sets | Slow likelihood | Design decision |
