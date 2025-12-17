# Couples Utility Specification Fix Plan

**Date:** 2025-12-16
**Issue:** Incorrect couples preference parameters - male shifter incorrectly includes n_children
**Severity:** CRITICAL - affects all couples estimation

---

## Bug Description

**Current (WRONG) Implementation:**
```python
# Male leisure shifters [0:6] - 6 params
beta_lm0, beta_lm_age_norm, beta_lm_age_norm2,
beta_lm_n_children,  # ← SHOULD NOT BE HERE!
beta_lm_educL, beta_lm_educH

# Female leisure shifters [6:12] - 6 params
beta_lf0, beta_lf_age_norm, beta_lf_age_norm2,
beta_lf_n_children,  # ← Correct
beta_lf_educL, beta_lf_educH

# Shared [12:16] - 4 params
beta_c, theta_lm, theta_lf, theta_c
```

**Correct Specification (from user):**
```
B_l_coupM = beta_lm0 + beta_lm_age_norm * age_norm +
            beta_lm_age_norm2 * age_norm2 +
            beta_lm_educL * educL + beta_lm_educH * educH
            # NO n_children term!

B_l_coupF = beta_lf0 + beta_lf_age_norm * age_norm +
            beta_lf_age_norm2 * age_norm2 +
            beta_lf_n_children * n_children +  # ← Only for females!
            beta_lf_educL * educL + beta_lf_educH * educH
```

---

## Corrected Parameter Structure

### Option A: Without Interaction Term (15 total params)
```
[0:5]   Male prefs (5):    beta_lm0, age_norm, age_norm2, educL, educH
[5:11]  Female prefs (6):  beta_lf0, age_norm, age_norm2, n_children, educL, educH
[11:15] Shared (4):        beta_c, theta_lm, theta_lf, theta_c

Total standalone couples: 15 + 14 hopp + 12 wopp = 41 (vw) or 29 (fw)
Total joint: 9 + 9 + 15 + 14 + 12 = 59 (vw) or 47 (fw)
```

### Option B: WITH Interaction Term (16 total params) - RECOMMENDED
```
[0:5]   Male prefs (5):    beta_lm0, age_norm, age_norm2, educL, educH
[5:11]  Female prefs (6):  beta_lf0, age_norm, age_norm2, n_children, educL, educH
[11:16] Shared (5):        beta_c, theta_lm, theta_lf, theta_c, beta_interact

Utility: U = beta_leisure_m * lm_bc + beta_leisure_f * lf_bc +
             beta_c * c_bc + beta_interact * l_m * l_f

Total standalone couples: 16 + 14 hopp + 12 wopp = 42 (vw) or 30 (fw)
Total joint: 9 + 9 + 16 + 14 + 12 = 60 (vw) or 48 (fw)
```

**User confirmed: Add interaction term!**

---

## Required Changes

### Files to Modify:
1. **scripts/RURO_estimate_FR.py** (PRIMARY)
2. Documentation files (parameter counts)

### Specific Changes in RURO_estimate_FR.py:

#### 1. PreferenceParametersCouples dataclass (line ~889)
```python
# REMOVE:
beta_lm_n_children: float = 0.0

# Keep all others
```

#### 2. Parameter unpacking in ALL couples functions:
- `fast_neg_ll_with_grad_couples()` (line ~3503)
- `log_likelihood_couples()` (line ~2830)
- `fast_log_likelihood_couples()` (line ~1605)
- `fast_neg_ll_with_grad_couples_precomputed()` (line ~4797)

**Change from:**
```python
# Male [0:6]
beta_lm0 = theta[0]
beta_lm_age_norm = theta[1]
beta_lm_age_norm2 = theta[2]
beta_lm_n_children = theta[3]  # REMOVE
beta_lm_educL = theta[4]
beta_lm_educH = theta[5]

# Female [6:12]
beta_lf0 = theta[6]
...
```

**Change to:**
```python
# Male [0:5] - NO n_children
beta_lm0 = theta[0]
beta_lm_age_norm = theta[1]
beta_lm_age_norm2 = theta[2]
beta_lm_educL = theta[3]
beta_lm_educH = theta[4]

# Female [5:11] - WITH n_children
beta_lf0 = theta[5]
beta_lf_age_norm = theta[6]
beta_lf_age_norm2 = theta[7]
beta_lf_n_children = theta[8]
beta_lf_educL = theta[9]
beta_lf_educH = theta[10]

# Shared [11:16] - WITH interaction
beta_c = theta[11]
theta_lm = theta[12]
theta_lf = theta[13]
theta_c = theta[14]
beta_interact = theta[15]  # NEW
```

#### 3. Utility calculation (add interaction)
```python
# Current:
u = beta_leisure_m * lm_bc + beta_leisure_f * lf_bc + beta_c * c_bc

# Change to:
u = (beta_leisure_m * lm_bc +
     beta_leisure_f * lf_bc +
     beta_c * c_bc +
     beta_interact * data.l_m * data.l_f)  # NEW: interaction term
```

#### 4. Beta leisure computation (remove n_children from male)
```python
# Current:
beta_leisure_m = (
    beta_lm0
    + beta_lm_age_norm * data.age_norm_m
    + beta_lm_age_norm2 * data.age_norm2_m
    + beta_lm_n_children * data.n_children  # REMOVE THIS LINE
    + beta_lm_educL * data.educL_m
    + beta_lm_educH * data.educH_m
)

# Change to:
beta_leisure_m = (
    beta_lm0
    + beta_lm_age_norm * data.age_norm_m
    + beta_lm_age_norm2 * data.age_norm2_m
    + beta_lm_educL * data.educL_m
    + beta_lm_educH * data.educH_m
)
```

#### 5. Gradient computation (ALL couples gradient functions)
Update gradient arrays from 16 to 16 params (same size but different structure):

```python
# Update preference gradient size and indexing
du_dtheta = np.empty((n, 16), dtype=np.float64)

# Male params [0:5]
du_dtheta[:, 0] = lm_bc
du_dtheta[:, 1] = data.age_norm_m * lm_bc
du_dtheta[:, 2] = data.age_norm2_m * lm_bc
du_dtheta[:, 3] = data.educL_m * lm_bc
du_dtheta[:, 4] = data.educH_m * lm_bc

# Female params [5:11]
du_dtheta[:, 5] = lf_bc
du_dtheta[:, 6] = data.age_norm_f * lf_bc
du_dtheta[:, 7] = data.age_norm2_f * lf_bc
du_dtheta[:, 8] = data.n_children * lf_bc       # n_children only for female
du_dtheta[:, 9] = data.educL_f * lf_bc
du_dtheta[:, 10] = data.educH_f * lf_bc

# Shared params [11:16]
du_dtheta[:, 11] = c_bc
du_dtheta[:, 12] = beta_leisure_m * dlm_bc_dtheta
du_dtheta[:, 13] = beta_leisure_f * dlf_bc_dtheta
du_dtheta[:, 14] = beta_c * dc_bc_dtheta
du_dtheta[:, 15] = data.l_m * data.l_f  # NEW: interaction gradient
```

#### 6. Parameter names (line ~3083)
```python
names += [
    "cou.pref.beta_lm0",
    "cou.pref.beta_lm_age_norm",
    "cou.pref.beta_lm_age_norm2",
    # REMOVE: "cou.pref.beta_lm_n_children",
    "cou.pref.beta_lm_educL",
    "cou.pref.beta_lm_educH",

    "cou.pref.beta_lf0",
    "cou.pref.beta_lf_age_norm",
    "cou.pref.beta_lf_age_norm2",
    "cou.pref.beta_lf_n_children",  # Keep for female
    "cou.pref.beta_lf_educL",
    "cou.pref.beta_lf_educH",

    "cou.pref.beta_c",
    "cou.pref.theta_lm",
    "cou.pref.theta_lf",
    "cou.pref.theta_c",
    "cou.pref.beta_interact",  # NEW
]
```

#### 7. Initial values (line ~3007)
```python
# Remove n_children initial value for males
# Add interaction initial value (start at 0.0)
```

#### 8. get_n_params_joint() function
Update to reflect new counts (should stay 60 for vw).

---

## Testing Plan

1. **Verify parameter counts:**
   - Standalone couples: 16 + 14 + 12 = 42 (vw)
   - Joint: 9 + 9 + 16 + 14 + 12 = 60 (vw)

2. **Test singles-only first** (unchanged)

3. **Test couples-only** with new specification

4. **Test joint estimation** with corrected structure

5. **Verify gradient computations** numerically

---

## Implementation Priority

**CRITICAL - Must fix before any estimation runs!**

The current results are INVALID because the model specification is wrong.

---

**Next Steps:**
1. Apply all fixes systematically
2. Add diagnostic logging
3. Delete broken JSON file with wrong parameter structure
4. Rerun estimation from scratch with correct specification
