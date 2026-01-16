# 🎯 FINAL FIX: Couples Demographics Pattern

**Date:** January 16, 2026  
**Issue:** `AttributeError: 'EstimationSpec' object has no attribute 'utility_leisure_shifters_female'`  
**Status:** ✅ FIXED

---

## The Problem

Code tried to use:
- `spec.utility_leisure_shifters_female` 
- `spec.utility_leisure_shifters_male`

But `EstimationSpec` only has:
- `spec.utility_leisure_shifters` (single list for all)

---

## The Solution

For **couples**, use the same shifters list but add gender suffixes to coefficient names:

### Pattern for Couples Female
```python
beta_l_f_expr = param_vars['beta_l0_f']
for shifter in spec.utility_leisure_shifters:  # Same list!
    var_name = shifter['variable']             # e.g., 'age_norm'
    base_coef = shifter['coefficient']         # e.g., 'beta_l_age_norm'
    coef_name_f = f"{base_coef}_f"            # e.g., 'beta_l_age_norm_f'
    if coef_name_f in param_vars:
        demo_val = getattr(data, var_name, None)
        beta_l_f_expr += param_vars[coef_name_f] * float(demo_val[idx])
```

### Pattern for Couples Male
```python
beta_l_m_expr = param_vars['beta_l0_m']
for shifter in spec.utility_leisure_shifters:  # Same list!
    var_name = shifter['variable']             # e.g., 'age_norm'
    base_coef = shifter['coefficient']         # e.g., 'beta_l_age_norm'
    coef_name_m = f"{base_coef}_m"            # e.g., 'beta_l_age_norm_m'
    if coef_name_m in param_vars:
        demo_val = getattr(data, var_name, None)
        beta_l_m_expr += param_vars[coef_name_m] * float(demo_val[idx])
```

---

## How It Works

### YAML Spec (Single List)
```yaml
leisure:
  shifters:
    - variable: "age_norm"
      coefficient: "beta_l_age_norm"
    - variable: "educL"
      coefficient: "beta_l_educL"
```

### Parameter Names (Gender-Specific)
```yaml
initial_values:
  # Singles male
  beta_l_age_norm_sm: -0.0076
  beta_l_educL_sm: 0.1389
  
  # Singles female
  beta_l_age_norm_sf: -0.0208
  beta_l_educL_sf: 0.1394
  
  # Couples female
  beta_l_age_norm_f: -0.0334
  beta_l_educL_f: 0.1644
  
  # Couples male
  beta_l_age_norm_m: -0.0031
  beta_l_educL_m: 0.1749
```

**Key Insight:** The **variable names** stay the same (`age_norm`, `educL`), but **coefficient names** get suffixes (`_sm`, `_sf`, `_f`, `_m`).

---

## Files Modified

### 1. `estimate_couples_gamspy()` (lines ~511, ~528)
- Female: Uses `f"{base_coef}_f"`
- Male: Uses `f"{base_coef}_m"`

### 2. `estimate_joint_gamspy()` (lines ~851, ~867)
- Couples female: Uses `f"{base_coef}_f"`
- Couples male: Uses `f"{base_coef}_m"`

**Total:** 4 locations fixed

---

## Compilation Status

```bash
✓ gamspy_estimation.py - NO ERRORS
```

---

## Ready to Run!

```powershell
python run_gamspy.py
```

Or:

```powershell
python scripts/enhanced/enh_RURO_estimate_FR.py --mnl-base U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl --output-dir outputs/estimates/fr/2016_gamspy --group joint --solver gamspy-conopt --spec-config scripts/enhanced/estimation_spec.yaml --auto-timestamp
```

---

## All Bugs Fixed (8 Total)

1. ✅ Syntax error (missing newline)
2. ✅ `group_sizes` → `group_ends`
3. ✅ Missing `actual_choice` field
4. ✅ `demographics_*` → `utility_leisure_shifters` (singles)
5. ✅ Indentation errors
6. ✅ Escape sequence warning
7. ✅ `beta_c_f/m` → `beta_c` (couples consumption)
8. ✅ **Couples demographics pattern** (use `_f`/`_m` suffix) ← THIS FIX

**Status: ALL DONE!** 🎉
