# Occupation Choice: Country/Year/Specification Agnostic Design

## Design Principles

The occupation choice implementation is **fully agnostic** to:
1. **Country**: Works with any country's occupation classification system
2. **Year**: No hardcoded year-specific constants or assumptions
3. **Specification**: Flexible parameter structure defined entirely in YAML
4. **Normalization**: No assumptions about how variables are scaled or normalized

## How Agnosticism is Achieved

### 1. No Hardcoded Occupation Codes

**BAD (Country-Specific):**
```python
if occupation == "Manager":
    wage_mean = 3.5 + 0.25 * experience
elif occupation == "Professional":
    wage_mean = 3.2 + 0.23 * experience
```

**GOOD (Agnostic):**
```python
for occ_config in spec.occupation_wage_configs:
    occ_var = occ_config["occupation"]  # Read from YAML: could be "loc4_1", "isco_1", "soc_11"
    beta_0 = params[f"{occ_config['intercept']}{gender_suffix}"]
    mu_occ = beta_0 + ...
```

The occupation variables (`loc4_1`, `loc4_2`, etc.) are **not hardcoded** - they're read from the YAML specification. To use this for a different country:
- UK: Change YAML to use `soc_1`, `soc_2`, ... (UK SOC codes)
- France: Change YAML to use `pcs_3`, `pcs_4`, ... (French PCS codes)
- International: Use `isco_1`, `isco_2`, ... (ISCO codes)

### 2. No Hardcoded Variable Names

**BAD (Specification-Specific):**
```python
education_high = data.education_high  # Assumes this variable exists
interaction = alpha_prof_educ * education_high
```

**GOOD (Agnostic):**
```python
for interaction in occ_pref["interactions"]:
    var_name = interaction["variable"]  # Read from YAML
    if var_name in demographic_vars:
        interaction_term = occ_dummy * demographic_vars[var_name]
```

The demographic variables (`education_high`, `age`, etc.) are **dynamically extracted** based on what's specified in the YAML. To use different demographics:
- Add `education_years` instead of `education_high`
- Add `children_under_3` instead of `n_children`
- Add any custom interaction variable

### 3. No Hardcoded Normalization Assumptions

**BAD (Normalization-Specific):**
```python
exp_scaled = (experience - 20) / 10  # Assumes mean=20, scale=10
```

**GOOD (Agnostic):**
```python
exp_scaled = experience / 10.0  # Simple decade scaling, works with any experience range
# OR even better: let data already be scaled
mu_occ = beta_0 + beta_exp * experience  # No rescaling in code
```

The normalization/scaling is **left to the user** in data preparation. The code doesn't assume:
- Mean or standard deviation of any variable
- Units (years, decades, log-scale)
- Range (0-1, -3 to 3, etc.)

### 4. No Hardcoded Parameter Structure

**BAD (Rigid Structure):**
```python
alpha_prof_sm = params["alpha_prof_sm"]  # Assumes this exact parameter exists
```

**GOOD (Flexible Structure):**
```python
alpha_occ_name = f"{occ_pref['coefficient']}{gender_suffix}"  # Constructed from YAML
if alpha_occ_name in params:  # Safe check before access
    u_with_occ += params[alpha_occ_name] * occ_dummy
```

Parameter names are **constructed dynamically** from the YAML specification. To change the parameter structure:
- Use different suffixes (e.g., `_male`, `_female` instead of `_sm`, `_sf`)
- Use different coefficient names (e.g., `pref_prof` instead of `alpha_prof`)
- Add or remove parameters without changing code

### 5. Graceful Degradation with Missing Variables

**BAD (Fails if Variable Missing):**
```python
education = data.education  # Crashes if not present
mu_occ = beta_0 + beta_ed * education
```

**GOOD (Handles Missing Variables):**
```python
if education is not None and beta_ed_name in params:
    mu_occ = mu_occ + params[beta_ed_name] * education
# OR
if var_name in demographic_vars and coef_name in params:
    interaction_term = ...
else:
    logging.warning(f"Variable {var_name} not found in data")
```

The code **logs warnings** instead of crashing when variables are missing. This allows:
- Running without education if not in data
- Running without experience if not relevant
- Skipping interactions that aren't applicable

## Example: Adapting to Different Countries

### Norway (Current Implementation)
```yaml
occupation_preferences:
  - occupation: "loc4_2"  # Norwegian LOC4 code for Professionals
    coefficient: "alpha_prof"
    interactions:
      - variable: "education_high"  # Tertiary education
        coefficient: "alpha_prof_educ"
```

### UK (Using SOC Codes)
```yaml
occupation_preferences:
  - occupation: "soc_2"  # UK SOC code for Professional occupations
    coefficient: "alpha_prof"
    interactions:
      - variable: "degree_level"  # UK degree classification
        coefficient: "alpha_prof_educ"
```

### France (Using PCS Codes)
```yaml
occupation_preferences:
  - occupation: "pcs_3"  # French PCS code for Cadres (managers/professionals)
    coefficient: "alpha_prof"
    interactions:
      - variable: "bac_plus_5"  # French higher education (5+ years post-bac)
        coefficient: "alpha_prof_educ"
```

**No code changes needed** - just update the YAML and ensure the data has the corresponding occupation dummy variables.

## Example: Adapting to Different Years

The implementation has **no year-specific logic**. Time-varying factors are captured through:

1. **Parameters**: Estimated separately for each year
   - Wage levels change → β0 changes
   - Returns to education change → β_ed changes
   - Occupation preferences change → α_occ changes

2. **Data**: Different distributions for each year
   - 1995 data: Lower wages, different occupation distribution
   - 2025 data: Higher wages, different occupation distribution
   - Code works identically for both

3. **No temporal assumptions**:
   - No "Year 2000 baseline" assumptions
   - No "CPI adjustment to 2015 prices" in code
   - No "experience must be < 40" constraints

## Example: Adapting to Different Specifications

### Minimal Specification (4 Occupations, No Interactions)
```yaml
occupation_preferences:
  - occupation: "occ_1"
    coefficient: "alpha_occ1"
  - occupation: "occ_2"
    coefficient: "alpha_occ2"
  # Only base preferences, no interactions
```
**Code behavior**: Skips interaction loop, only adds direct preferences

### Rich Specification (Multiple Interactions)
```yaml
occupation_preferences:
  - occupation: "occ_2"
    coefficient: "alpha_prof"
    interactions:
      - variable: "education"
        coefficient: "alpha_prof_educ"
      - variable: "age"
        coefficient: "alpha_prof_age"
      - variable: "urban"
        coefficient: "alpha_prof_urban"
      - variable: "immigrant"
        coefficient: "alpha_prof_immigrant"
```
**Code behavior**: Loops through all interactions, adds each one

### Alternative Parameterization (Linear Experience)
```yaml
wage_opportunity:
  occupations:
    - occupation: "occ_1"
      intercept: "beta_w0_occ1"
      experience: "beta_w_exp_occ1"
      # No experience_squared - just omit it
      education: "beta_w_ed_occ1"
```
**Code behavior**: Checks for experience_squared, skips if not present

## Modular Integration

The occupation choice utilities are **completely modular**:

```python
# In estimation_engine.py - existing code
u = _compute_utility_singles(params, data, spec)
log_h = _compute_hours_opportunity_singles(params, data, spec, is_male)
log_w = _compute_wage_opportunity_vw_singles(params, data, spec)

# ADD occupation choice (only if spec.occupation_choice == True)
if spec.occupation_choice:
    from occupation_choice_utils import (
        add_occupation_preferences_to_utility,
        compute_occupation_specific_wage_density,
        compute_occupation_specific_hours_density,
        extract_occupation_dummies_from_data,
        extract_demographic_vars_from_data
    )

    # Extract occupation data
    occ_dummies = extract_occupation_dummies_from_data(data, spec)
    demo_vars = extract_demographic_vars_from_data(data, spec)

    # Add occupation components
    u = add_occupation_preferences_to_utility(u, params, spec, occ_dummies, demo_vars, gender_suffix)
    log_h = log_h + compute_occupation_specific_hours_density(hours, occ_dummies, working, params, spec)
    log_w = compute_occupation_specific_wage_density(log_wage, occ_dummies, experience, education, working, params, spec, gender_suffix)
    log_g3 = compute_occupation_availability(occ_dummies, params, spec, gender_suffix)

    # Total composite value
    V = u + log_h + log_w + log_g3 - log_prior
else:
    # Original logic (no occupation choice)
    V = u + log_h + log_w - log_prior
```

## Benefits of This Design

1. **Reusability**: Same code works for Norway, Sweden, UK, France, etc.
2. **Maintainability**: Updates in one place apply to all countries
3. **Testability**: Can test with synthetic data without country-specific setup
4. **Extensibility**: Easy to add new interactions or occupation types
5. **Clarity**: YAML specification documents the model structure
6. **Backward Compatibility**: Non-occupation models work unchanged

## What Users Need to Do

To use occupation choice with their data:

1. **Data Preparation**: Ensure occupation dummies are in the dataset
   - Example: `loc4_1`, `loc4_2`, `loc4_3`, `loc4_4` (4 dummy variables summing to 1)

2. **YAML Specification**: Define occupation structure
   - List occupations used
   - Specify which interactions to include
   - Set initial parameter values

3. **Run Estimation**: Same command as before
   ```bash
   python estimate.py --spec estimation_spec_occupation_choice.yaml --data data.parquet
   ```

**No code changes needed** - everything is configuration-driven!

---

**Last updated:** 2026-01-27
