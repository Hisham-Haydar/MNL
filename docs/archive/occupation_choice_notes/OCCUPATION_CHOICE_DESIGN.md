# Occupation Choice Model Design Document

## Overview

This document describes the implementation of occupation choice in the RURO MNL labor supply model, based on the Aaberge & Colombino (2011) framework for sector choice.

## Conceptual Framework

### Traditional Approach (What We Had)
```
Choice set: 100 alternatives (hours only)
Utility: U(consumption, leisure | occupation_dummy)
         ↑ occupation is just a covariate/shifter
```

### New Approach (Occupation as Choice)
```
Choice set: 400 alternatives (100 hours × 4 occupations)
Utility: U(consumption, leisure, occupation)
Wages: w ~ f(w | occupation, education, experience)
Hours: h ~ g(h | occupation)
         ↑ occupation is a CHOICE with its own opportunity distribution
```

## Mathematical Specification

### Utility Function

The utility for individual i choosing alternative j with (h, w, occ) is:

```
U_ij = v(c_ij, L_ij, occ_j) · ε_ij

where:
  c_ij = disposable income (after tax)
  L_ij = leisure = 8736 - h_j
  occ_j ∈ {loc4_1, loc4_2, loc4_3, loc4_4}
  ε_ij ~ Type I Extreme Value
```

The systematic component v() is:

```
log v(c, L, occ) = α1 · [c^α2 - 1]/α2
                   + α3 · [L^α4 - 1]/α4
                   + β_l_occ · L  (occupation-specific leisure preference)
                   + α_occ + Σ α_occ_k · Z_k  (occupation preference + interactions)
```

**Occupation preference components:**

1. **Occupation-specific leisure preferences:** Some occupations may allow more flexible hours or better work-life balance
   - β_l_prof, β_l_tech, β_l_service (relative to managers)

2. **Direct occupation preferences:** Intrinsic attractiveness of occupation
   - α_prof, α_tech, α_service (relative to managers)

3. **Occupation-demographic interactions:** How occupation attractiveness varies with characteristics
   - α_prof_educ: Professionals more attractive for highly educated
   - α_tech_educ: Technicians more attractive for medium educated
   - α_service_age: Service jobs attractiveness by age

### Opportunity Set Structure

Following Aaberge & Colombino (2011), the opportunity density is:

```
p(h, w, occ) = p1k · g1_occ(h) · g2_occ(w) · g3(occ)  if h > 0
             = p0k = 1 - p1k                          if h = 0
```

Where:
- `p1k` = proportion of market opportunities
- `g1_occ(h)` = **occupation-specific hours density**
- `g2_occ(w)` = **occupation-specific wage density**
- `g3(occ)` = occupation availability probability

**Key insight:** Hours and wages are **independently distributed** within each occupation, but the distributions **differ across occupations**.

### Occupation-Specific Wage Equations

Each occupation has its own Mincer equation:

```
log(w_occ) = β0_occ + β1_occ · Exp + β2_occ · Exp² + β3_occ · Ed + σ_occ · η

where η ~ N(0, 1)
```

**Expected pattern:**
- **Managers (loc4_1):** Highest β0 (intercept), steepest β3 (education returns)
- **Professionals (loc4_2):** High β0, high β3
- **Technicians (loc4_3):** Medium β0, moderate β3
- **Service (loc4_4):** Lower β0, low β3

### Occupation-Specific Hour Densities

Each occupation has different clustering of hours:

```
g1_occ(h) = γ_occ                           if h ∈ [52, 910]
          = γ_occ · exp(π_pt_occ · s_pt)    if h ∈ (910, 1066]  (part-time peak)
          = γ_occ                           if h ∈ (1066, 1898]
          = γ_occ · exp(π_ft_occ · s_ft)    if h ∈ (1898, 2106]  (full-time peak)
          = γ_occ                           if h ∈ (2106, 3640]
```

**Expected pattern:**
- **Managers:** Strong full-time clustering, weak part-time
- **Professionals:** Strong full-time, moderate part-time
- **Technicians:** Moderate both
- **Service:** Moderate full-time, strong part-time

### Occupation Availability

The probability that occupation occ is available:

```
g3(occ) = exp(μ_occ) / Σ_k exp(μ_k)

where:
  μ_mgr < μ_prof < μ_tech < μ_service = 0  (reference)
```

This captures that managerial positions are rarer than service positions.

## Implementation Strategy

### Approach: McFadden Sampling with Occupation Stratification

We do **NOT** need to re-run the entire MNL generation pipeline (Steps 3/4/6)!

Instead, we **expand the choice set during estimation** using McFadden's (1978) procedure:

#### For each individual i:

1. **Observe:** (h_obs, w_obs, occ_obs) from data

2. **Sample alternatives:**
   - **Observed occupation:** Sample 99 alternatives from p(h, w | occ_obs, X_i)
   - **Occupation 2:** Sample 100 alternatives from p(h, w | occ_2, X_i)
   - **Occupation 3:** Sample 100 alternatives from p(h, w | occ_3, X_i)
   - **Occupation 4:** Sample 100 alternatives from p(h, w | occ_4, X_i)

3. **Total choice set:** 400 alternatives (1 observed + 399 sampled)

4. **For each alternative j:**
   - Sample ε_j ~ Type I Extreme Value
   - Compute utility U_ij = v(c_ij, L_ij, occ_j) · ε_j
   - If needed, run EUROMOD or use tax approximation to get c_ij

5. **Chosen alternative:** j* = argmax_j U_ij

#### McFadden Consistency

McFadden (1978) showed that sampling from the true opportunity distribution gives **consistent parameter estimates**, even though we don't enumerate all possible alternatives.

The key is that the sampling distribution q(h, w | occ) must match the opportunity distribution p(h, w | occ).

### Estimation Procedure

The likelihood contribution for individual i is:

```
L_i = Pr(choose observed alternative | X_i, parameters)

    = v(c_obs, L_obs, occ_obs) · p(h_obs, w_obs, occ_obs)
      ────────────────────────────────────────────────────
      Σ_j v(c_j, L_j, occ_j) · p(h_j, w_j, occ_j)
```

Where the sum is over the sampled choice set of 400 alternatives.

## Parameter Groups

### 1. Utility Parameters (78 parameters)
- Consumption curvature: α1, α2 (2 params)
- Leisure curvature: α3, α4 (2 params)
- Consumption preferences: β_c_{sm,sf,m,f} (4 params)
- Leisure intercepts: β_l0_{sm,sf,m,f} (4 params)
- **Occupation-specific leisure:** β_l_{occ}_{gender} (12 params: 3 occ × 4 gender)
- **Occupation preferences:** α_{occ}_{gender} (12 params: 3 occ × 4 gender)
- **Occupation interactions:** α_{occ}_{var}_{gender} (24 params: 3 occ × 2 vars × 4 gender)
- Leisure interaction (couples): α_leisure_interact (1 param)
- **Total utility params:** ~61 params

### 2. Wage Opportunity Parameters (40 parameters)
- Per occupation-gender: 5 params (β0, β_exp, β_exp2, β_ed, σ)
- 4 occupations × 2 genders × 5 params = **40 params**

### 3. Hours Opportunity Parameters (17 parameters)
- Part-time clustering: π_pt_{occ} (4 params)
- Full-time clustering: π_ft_{occ} (4 params)
- Focal point amplitudes: π2, π4 (2 params)
- Base density normalization: γ_{occ} (4 params)
- Working indicator: β_work (1 param)
- **Total hours params:** ~15 params

### 4. Market Opportunity Parameters (6 parameters)
- Occupation availability: μ_{occ}_{gender} (6 params: 3 occ × 2 gender)
- Note: Service (loc4_4) is reference, so μ_service = 0

### **TOTAL PARAMETERS: ~122 parameters**

(vs. 78 parameters in the original model without occupation choice)

## Data Requirements

### Existing Variables (from your MNL data)
✅ Hours: `hours_year`
✅ Wages: `wage_hourly`
✅ Occupation: `loc4_1`, `loc4_2`, `loc4_3`, `loc4_4` (dummies)
✅ Demographics: `age`, `education`, `experience`
✅ Income: `gross_income`, `disposable_income`

### Derived Variables (create during estimation)
- `education_high`: 1 if tertiary education
- `education_medium`: 1 if secondary education
- `education_low`: 1 if primary education only
- `experience`: age - education_years - 5
- `experience_squared`: experience²

## Estimation Steps

### Phase 1: Estimate Occupation-Specific Wage Equations
Before full model estimation, estimate wage equations separately for each occupation-gender group:

```python
for occupation in [loc4_1, loc4_2, loc4_3, loc4_4]:
    for gender in [male, female]:
        model = OLS(log_wage ~ experience + experience² + education)
        β0_occ_g, β_exp_occ_g, β_exp2_occ_g, β_ed_occ_g, σ_occ_g = model.fit()
```

Use these as **fixed initial values** for the full MNL estimation.

### Phase 2: Estimate Occupation-Specific Hour Densities
Estimate the clustering parameters from observed hour distributions:

```python
for occupation in [loc4_1, loc4_2, loc4_3, loc4_4]:
    hist_h = histogram(hours | occupation == occ)
    π_pt_occ = fit_parttime_peak(hist_h)
    π_ft_occ = fit_fulltime_peak(hist_h)
```

### Phase 3: Full MNL Estimation with Occupation Choice
Use the wage and hour estimates from Phases 1-2 as initial values, then estimate the full model with all parameters jointly.

## Implementation Files to Modify

### 1. Specification Parser (`estimation_spec_parser.py`)
**New sections to parse:**
- `occupation_preferences`
- `occupation_specific: true` in hours_opportunity
- `occupation_specific_log_normal` in wage_opportunity
- `occupation_availability` in market_opportunity

**New parameter creation logic:**
- Create occupation-specific leisure shifters: `beta_l_{occ}_{gender}`
- Create occupation preference params: `alpha_{occ}_{gender}`
- Create occupation interaction params: `alpha_{occ}_{var}_{gender}`
- Create wage params by occupation: `beta_w0_{occ}_{gender}`, etc.
- Create hour params by occupation: `pi_pt_{occ}`, `pi_ft_{occ}`

### 2. Estimation Engine (`estimation_engine.py`)
**New utility computation:**
```python
def _compute_utility_with_occupation(data, params, spec):
    # Base utility from consumption and leisure
    util = _compute_base_utility(data.consumption, data.leisure, params, spec)

    # Add occupation-specific leisure preference
    for occ in ['loc4_2', 'loc4_3', 'loc4_4']:
        beta_l_occ = params[f'beta_l_{occ}_{gender}']
        util += beta_l_occ * data.leisure * data[occ]

    # Add direct occupation preference
    for occ in ['loc4_2', 'loc4_3', 'loc4_4']:
        alpha_occ = params[f'alpha_{occ}_{gender}']
        util += alpha_occ * data[occ]

        # Add interactions
        for var in ['educ', 'age']:
            alpha_occ_var = params[f'alpha_{occ}_{var}_{gender}']
            util += alpha_occ_var * data[occ] * data[var]

    return util
```

**New opportunity density:**
```python
def _compute_opportunity_density_occupation(h, w, occ, params, spec):
    # Hours density (occupation-specific)
    g_h = _compute_hours_density(h, occ, params, spec)

    # Wage density (occupation-specific)
    g_w = _compute_wage_density(w, occ, experience, education, params, spec)

    # Occupation availability
    g_occ = _compute_occupation_availability(occ, params, spec)

    # Market opportunity proportion
    p1k = _compute_market_proportion(params, spec)

    return p1k * g_h * g_w * g_occ
```

### 3. McFadden Sampling (`mcfadden_sampler.py` - NEW FILE)
Create a new module for occupation-stratified sampling:

```python
def sample_occupation_alternatives(individual, spec, n_per_occ=100):
    """
    Sample 400 alternatives: 100 per occupation

    Returns:
        alternatives: DataFrame with columns [hours, wage, loc4_1, loc4_2, loc4_3, loc4_4]
    """
    alternatives = []

    for occ in ['loc4_1', 'loc4_2', 'loc4_3', 'loc4_4']:
        # Sample hours from occupation-specific distribution
        hours = sample_hours(n_per_occ, occupation=occ, spec=spec)

        # Sample wages from occupation-specific Mincer equation
        wages = sample_wages(n_per_occ, occupation=occ,
                            experience=individual.experience,
                            education=individual.education,
                            spec=spec)

        # Create occupation dummies
        occ_dummies = create_occupation_dummies(occ)

        alternatives.append(pd.DataFrame({
            'hours': hours,
            'wage': wages,
            **occ_dummies
        }))

    return pd.concat(alternatives, ignore_index=True)
```

## Testing Strategy

### Unit Tests
1. **Wage equation sampling:** Verify that sampled wages match occupation-specific distributions
2. **Hours density sampling:** Verify that sampled hours match occupation-specific clustering
3. **Utility computation:** Verify that occupation preferences are correctly added to utility
4. **Choice probability:** Verify that choice probabilities sum to 1

### Integration Test
1. Create a **small synthetic dataset** (100 individuals)
2. Run estimation with occupation choice
3. Verify that:
   - All parameters are estimated
   - Log-likelihood improves over iterations
   - Choice probabilities are reasonable
   - Occupation switching patterns make sense

### Validation Test
1. **Compare to observed occupation distribution**
2. **Cross-elasticities:** Does higher wage in occupation A increase its choice probability?
3. **Sorting patterns:** Do highly educated choose professional occupations?

## Expected Results

### Occupation Preference Patterns
- **α_prof_educ > 0:** Highly educated prefer professional jobs
- **α_tech_educ > 0:** Medium educated prefer technician jobs
- **α_service < 0:** Service jobs less attractive ceteris paribus

### Wage Gradient
- **β_w_ed:** Managers > Professionals > Technicians > Service
- **σ:** Wage variance differs across occupations

### Hour Patterns
- **π_ft:** Managers and Professionals have strong full-time clustering
- **π_pt:** Service workers have strong part-time clustering

### Elasticities
- **Wage elasticity:** Larger for occupations with flatter wage profiles
- **Occupation switching:** Education is a key determinant
- **Cross-occupation effects:** Tax changes may induce occupation switching

## References

- Aaberge, R., & Colombino, U. (2011). Empirical Optimal Income Taxation: A Microeconometric Application to Norway. *Working Papers ChilD n. 16/2011*.

- McFadden, D. (1978). Modeling the Choice of Residential Location. In *Spatial Interaction Theory and Planning Models*, ed. by A. Karlqvist et al., North Holland, 75–96.

- Dagsvik, J.K. (1994). Discrete and Continuous Choice, Max-Stable Processes and Independence from Irrelevant Attributes. *Econometrica*, 62, 1179-1205.
