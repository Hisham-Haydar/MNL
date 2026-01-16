# Demographics Fix - Before & After

## The Problem

The GAMSPy estimation code was trying to access attributes that don't exist in `EstimationSpec`:
- `spec.demographics_singles`
- `spec.demographics_couples_female`
- `spec.demographics_couples_male`

## The Root Cause

Looking at `estimation_spec_parser.py`, the actual structure is:

```python
@dataclass
class EstimationSpec:
    utility_leisure_shifters: List[Dict[str, str]]
    utility_leisure_shifters_female: List[Dict[str, str]]
    utility_leisure_shifters_male: List[Dict[str, str]]
```

Each shifter is a dict like:
```python
{
    'variable': 'age',        # The column name in the data
    'coefficient': 'beta_age'  # The parameter name
}
```

## The Fix

### For Singles (1 leisure term)

**BEFORE (BROKEN):**
```python
beta_l_expr = param_vars['beta_l0']
for demo_name in spec.demographics_singles:
    param_name = f'beta_{demo_name}'
    if param_name in param_vars:
        demo_val = getattr(data, demo_name, None)
        if demo_val is not None:
            beta_l_expr = beta_l_expr + param_vars[param_name] * float(demo_val[global_idx])
```

**AFTER (WORKING):**
```python
beta_l_expr = param_vars['beta_l0']
for shifter in spec.utility_leisure_shifters:
    var_name = shifter['variable']
    coef_name = shifter['coefficient']
    if coef_name in param_vars:
        demo_val = getattr(data, var_name, None)
        if demo_val is not None:
            beta_l_expr = beta_l_expr + param_vars[coef_name] * float(demo_val[global_idx])
```

### For Couples (2 leisure terms: female + male)

**BEFORE (BROKEN):**
```python
# Female
beta_l_f_expr = param_vars['beta_l0_f']
for demo_name in spec.demographics_couples_female:
    param_name = f'beta_{demo_name}_f'
    if param_name in param_vars:
        demo_val = getattr(data, demo_name, None)
        if demo_val is not None:
            beta_l_f_expr = beta_l_f_expr + param_vars[param_name] * float(demo_val[global_idx])

# Male
beta_l_m_expr = param_vars['beta_l0_m']
for demo_name in spec.demographics_couples_male:
    param_name = f'beta_{demo_name}_m'
    if param_name in param_vars:
        demo_val = getattr(data, demo_name, None)
        if demo_val is not None:
            beta_l_m_expr = beta_l_m_expr + param_vars[param_name] * float(demo_val[global_idx])
```

**AFTER (WORKING):**
```python
# Female
beta_l_f_expr = param_vars['beta_l0_f']
for shifter in spec.utility_leisure_shifters_female:
    var_name = shifter['variable']
    coef_name = shifter['coefficient']
    if coef_name in param_vars:
        demo_val = getattr(data, var_name, None)
        if demo_val is not None:
            beta_l_f_expr = beta_l_f_expr + param_vars[coef_name] * float(demo_val[global_idx])

# Male
beta_l_m_expr = param_vars['beta_l0_m']
for shifter in spec.utility_leisure_shifters_male:
    var_name = shifter['variable']
    coef_name = shifter['coefficient']
    if coef_name in param_vars:
        demo_val = getattr(data, var_name, None)
        if demo_val is not None:
            beta_l_m_expr = beta_l_m_expr + param_vars[coef_name] * float(demo_val[global_idx])
```

## Files Changed

All instances fixed in `scripts/enhanced/gamspy_estimation.py`:

1. **`estimate_singles_gamspy()`** - Line 258
2. **`estimate_couples_gamspy()`** - Lines 515, 531
3. **`estimate_joint_gamspy()`** - Lines 751, 801, 852, 866

Total: **7 locations fixed** ✅

## Example Spec YAML

```yaml
utility_leisure_shifters:
  - variable: age
    coefficient: beta_age
  - variable: num_children
    coefficient: beta_children
  - variable: region_urban
    coefficient: beta_urban

utility_leisure_shifters_female:
  - variable: age_female
    coefficient: beta_age_f
  - variable: education_female
    coefficient: beta_edu_f

utility_leisure_shifters_male:
  - variable: age_male
    coefficient: beta_age_m
  - variable: education_male
    coefficient: beta_edu_m
```

## Verification

All fixed instances now correctly:
1. ✅ Iterate over the list of shifter dicts
2. ✅ Extract `variable` and `coefficient` from each dict
3. ✅ Use `variable` to get data from the dataset
4. ✅ Use `coefficient` to get the parameter from `param_vars`
5. ✅ Build the leisure utility expression correctly

**Status:** All 7 instances verified and working! 🎉
