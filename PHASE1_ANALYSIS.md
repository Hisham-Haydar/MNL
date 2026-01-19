# Phase 1 Analysis: Making GAMSPy Specification-Agnostic

**Date**: 2026-01-17
**Status**: In Progress
**Goal**: Remove hardcoded parameter references and make GAMSPy read everything dynamically from specification files

---

## Current Issues Identified

### Issue 1: Singles Estimation Uses Wrong Parameters (CRITICAL!)

**File**: [scripts/enhanced/gamspy_estimation.py:247-273](scripts/enhanced/gamspy_estimation.py#L247-L273)

**Problem**: The `estimate_singles_gamspy()` function uses generic `beta_c` and `beta_l0` instead of gender-specific parameters:

```python
# Line 247: WRONG - uses generic beta_c
util_j = param_vars['beta_c'] * log_c_term

# Line 255: WRONG - uses generic beta_l0
beta_l_expr = param_vars['beta_l0']

# Line 270: WRONG - uses generic coefficient without suffix
beta_l_expr = beta_l_expr + param_vars[coef_name] * float(demo_val[global_idx])
```

**Why this is critical**:
- This function is called for BOTH singles male AND singles female
- But it always uses the same parameters (beta_c, beta_l0)
- In the 4-group architecture, singles male should use beta_c_sm, beta_l0_sm
- Singles female should use beta_c_sf, beta_l0_sf
- This causes estimation to fail because beta_c and beta_l0 DON'T EXIST in the 46-parameter specification!

**Evidence from specification**:
```yaml
# estimation_spec.yaml has:
- beta_c_sm
- beta_c_sf
- beta_l0_sm
- beta_l0_sf
- beta_c (couples household consumption)

# But NOT:
- beta_c (for singles) ❌
- beta_l0 (generic) ❌
```

### Issue 2: Joint Estimation Hardcodes Correct Parameters (GOOD!)

**File**: [scripts/enhanced/gamspy_estimation.py:720-821](scripts/enhanced/gamspy_estimation.py#L720-L821)

**Status**: The `estimate_joint_gamspy()` function CORRECTLY hardcodes:
- Singles male: `beta_c_sm`, `beta_l0_sm` (line 720, 724) ✓
- Singles female: `beta_c_sf`, `beta_l0_sf` (line 771, 775) ✓
- Couples: `beta_c` (household), `beta_l0_m`, `beta_l0_f` (line 821, 825, 841) ✓

**But**: This is still hardcoded! Won't work with different specification structures (e.g., AC2013 spec with _cm/_cf suffixes).

### Issue 3: Couples Estimation Also Hardcodes (MOSTLY CORRECT)

**File**: [scripts/enhanced/gamspy_estimation.py:487-520](scripts/enhanced/gamspy_estimation.py#L487-L520)

**Status**: The `estimate_couples_gamspy()` function correctly uses:
- `beta_c` for household consumption (line 487) ✓
- `beta_l0_f` for female leisure (line 491) ✓
- `beta_l0_m` for male leisure (line 508) ✓

**But**: Still hardcoded and won't adapt to different specs.

---

## Solution Strategy

### Step 1: Detect Group Context
Add a parameter to specify which group is being estimated:

```python
def estimate_singles_gamspy(
    data: PrecomputedDataSingles,
    spec: EstimationSpec,
    theta_init: np.ndarray,
    group: str = "singles_male",  # NEW: "singles_male" or "singles_female"
    solver: str = "conopt",
    verbose: bool = True
) -> Dict[str, Any]:
```

### Step 2: Determine Parameter Suffix Dynamically
Based on group, determine which parameter suffix to use:

```python
# Map group to parameter suffix
SUFFIX_MAP = {
    "singles_male": "_sm",
    "singles_female": "_sf",
    "couples_male": "_m",
    "couples_female": "_f",
    "couples_household": "",  # No suffix for household params
}

def get_param_name(base_name: str, group: str, param_vars: dict) -> str:
    """
    Get actual parameter name for a group-specific context.

    Tries in order:
    1. group-specific parameter (e.g., beta_c_sm)
    2. generic parameter (e.g., beta_c)
    3. raises error if not found
    """
    suffix = SUFFIX_MAP.get(group, "")

    # Try with suffix first
    if suffix:
        param_with_suffix = f"{base_name}{suffix}"
        if param_with_suffix in param_vars:
            return param_with_suffix

    # Try generic parameter
    if base_name in param_vars:
        return base_name

    # Not found
    raise ValueError(
        f"Parameter '{base_name}' with group '{group}' not found. "
        f"Tried: {base_name}{suffix}, {base_name}"
    )
```

### Step 3: Update Utility Building Logic
Replace all hardcoded parameter references with dynamic lookups:

```python
# OLD (line 247):
util_j = param_vars['beta_c'] * log_c_term

# NEW:
beta_c_param = get_param_name('beta_c', group, param_vars)
util_j = param_vars[beta_c_param] * log_c_term

# OLD (line 255):
beta_l_expr = param_vars['beta_l0']

# NEW:
beta_l0_param = get_param_name('beta_l0', group, param_vars)
beta_l_expr = param_vars[beta_l0_param]

# OLD (line 270):
beta_l_expr = beta_l_expr + param_vars[coef_name] * float(demo_val[global_idx])

# NEW:
coef_param = get_param_name(coef_name, group, param_vars)
beta_l_expr = beta_l_expr + param_vars[coef_param] * float(demo_val[global_idx])
```

### Step 4: Update Couples Estimation
Apply the same dynamic parameter lookup to couples estimation:

```python
# Consumption: Always household-level, use "couples_household" group
beta_c_param = get_param_name('beta_c', 'couples_household', param_vars)
util_j = param_vars[beta_c_param] * log_c_term

# Female leisure: Use "couples_female" group
beta_l0_f_param = get_param_name('beta_l0', 'couples_female', param_vars)
beta_l_f_expr = param_vars[beta_l0_f_param]

# Male leisure: Use "couples_male" group
beta_l0_m_param = get_param_name('beta_l0', 'couples_male', param_vars)
beta_l_m_expr = param_vars[beta_l0_m_param]
```

---

## Implementation Steps

1. ✓ **Analyze current code** - COMPLETED
2. **Add helper function `get_param_name()`** at top of gamspy_estimation.py
3. **Update `estimate_singles_gamspy()`**:
   - Add `group` parameter
   - Replace hardcoded `beta_c` with dynamic lookup
   - Replace hardcoded `beta_l0` with dynamic lookup
   - Fix leisure shifter coefficient lookups
4. **Update `estimate_couples_gamspy()`**:
   - Use dynamic lookup for all parameters
   - Specify correct group context (household/male/female)
5. **Update `estimate_joint_gamspy()`**:
   - Use dynamic lookup for singles male section
   - Use dynamic lookup for singles female section
   - Use dynamic lookup for couples section
6. **Test with all 4 specifications**:
   - estimation_spec.yaml (49 params)
   - estimation_spec_AC2013.yaml (68 params, uses _cm/_cf)
   - estimation_spec_v2.yaml (53 params)
   - estimation_spec_loc_empirical.yaml (52 params)

---

## Expected Outcomes

After Phase 1 completion:

1. **No more hardcoded parameter names** - All parameters read dynamically from spec
2. **Works with any specification structure** - Adapts to _sm/_sf, _cm/_cf, or no suffixes
3. **Proper error messages** - Clear errors when parameters are missing
4. **Still uses log-linear utility** - Box-Cox implementation comes in Phase 2
5. **All 4 specs parse correctly** - Already validated in Phase 0

---

## Next Phase Preview

**Phase 2** will replace the log-linear utility (`U = β*log(C)`) with Box-Cox utility (`U = β*BC(C,θ)`). This is a separate concern from parameter naming and should be done AFTER Phase 1.

**Separation of concerns**:
- Phase 1: Parameter naming and dynamic specification
- Phase 2: Utility function mathematical form
- Phase 3: Already covered by Phase 1 (4-group architecture through dynamic naming)
