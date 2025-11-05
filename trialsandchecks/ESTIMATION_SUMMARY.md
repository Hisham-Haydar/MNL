# Explicit DCM Estimation for Male Singles

## Overview
Added explicit DCM (Discrete Choice Model) estimation code to `scripts/old_biogeme.py` for male singles with:
- **Centering**: Regressors centered around actual choice means
- **Scaling**: Support for consumption scaling (y_scale parameter)
- **ASCs**: Alternative-specific constants included
- **Detailed specification**: Written explicitly step-by-step, similar to `test_biogeme.py`

## Configuration
```python
INCLUDE_ASCS = True      # Alternative-specific constants enabled
CENTER_LOGS = True       # Centering around actual choice means enabled
Y_SCALE = 1.0           # No consumption scaling (1.0 = no rescaling)
POOLED = False          # Single gender estimation (not pooled)
```

## Model Specification

### Parameters (13 total)

**Main Utility Coefficients (6):**
- `alpha_1` (beta_log_consumption): Coefficient on log(consumption)
- `alpha_2` (beta_log_leisure): Coefficient on log(leisure)
- `alpha_3` (beta_leila): Coefficient on Leila interaction (log(l) × log(age))
- `alpha_4` (beta_log2_leila): Quadratic in Leila
- `alpha_5` (beta_log_leisure_children_total): Effect of total children on leisure
- `alpha_6` (beta_log_leisure_child_lt6_dummy): Effect of young child (<6) dummy on leisure

**Quadratic and Interaction Coefficients (3):**
- `beta_1` (beta_log2_consumption): Curvature on log(consumption)
- `beta_2` (beta_log2_leisure): Curvature on log(leisure)
- `gamma` (beta_logy_logl): Interaction between consumption and leisure

**Centering and Scaling Parameters (3, fixed):**
- `C_LOGY`: Centers log(consumption) around actual choice mean (fixed = 1)
- `C_LOGL`: Centers log(leisure) around actual choice mean (fixed = 1)
- `LN_SCALE`: Scaling factor for consumption (fixed = 1, no scaling)

**Alternative-Specific Constants (n alternatives):**
- `ASC_h0`, `ASC_h1`, ..., `ASC_h6`: One per scenario label
  - First alternative (h0) normalized to 0 (fixed)
  - Others estimated freely (fixed = 0)

### Utility Specification

For each alternative k:

```
V_k = ASC_k 
    + α₁ × logy*_k + α₂ × logl*_k + α₃ × Leila_k + α₄ × Leila2_k 
    + α₅ × lochi_k + α₆ × logdc_k
    + β₁ × (logy*_k)² + β₂ × (logl*_k)² + γ × (logy*_k × logl*_k)

where:
  logy*_k = logy_k - ln(y_scale) - C_LOGY
  logl*_k = logl_k - C_LOGL
```

### Centering Transformation

The model applies transformations to inputs:
1. **Log consumption**: `logy_centered = logy_raw - LN_SCALE - C_LOGY`
2. **Log leisure**: `logl_centered = logl_raw - C_LOGL`
3. **Squared and interaction terms**: Computed from centered variables

This centering helps with numerical stability and interpretation.

## Implementation Steps

The code follows these steps:

1. **Load Data**: Uses `load_dataset()` to get male singles data with all regressors
2. **Compute Centering Values**: Calculate mean logy and logl at actual choice
3. **Prepare Database**: Convert DataFrame to Biogeme database format with:
   - Choice identifier (`choice_id`)
   - All scenario variables (logy, logl, Leila, Leila2, lochi, logdc, log2y, log2l, logyl)
   - Gender column (dgn)
4. **Define Parameters**: Create Beta objects with:
   - Reasonable starting values (0.0)
   - No bounds (None for lower/upper)
   - Fixed status (0=estimated, 1=fixed)
5. **Build Utilities**: Construct utility expressions for each alternative
6. **Specify Model**: Create multinomial logit model
7. **Estimate**: Run Biogeme estimation
8. **Extract Results**: 
   - Estimated parameters (CSV)
   - Fit statistics (log-likelihood, ρ², adjusted ρ²)
   - Variance-covariance matrices (if available)

## Output

The estimation produces:
- **Location**: `reports/biogeme/male_explicit/`
- **Files**:
  - `dcm_male_explicit_ascsON_centered_parameters.csv` - Estimated parameters
  - Console output - Summary statistics and convergence info

## Code Structure

The code is organized into 8 main sections in `old_biogeme.py`:

```python
# Section 1: Configuration
INCLUDE_ASCS = True
CENTER_LOGS = True
# ...

# Section 2: Compute actual choice values
mean_logy_actual, mean_logl_actual = compute_actual_choice_logs(df, scenario_labels)

# Section 3: Prepare database
database = db.Database("labour_supply", numeric_df)

# Section 4: Define Beta parameters
alpha_1 = Beta("beta_log_consumption", 0.0, None, None, 0)
# ...

# Section 5: Build utility expressions
for label in scenario_labels:
    V[alt_id] = utility + asc_dict[label]

# Section 6: Create logit model
logprob = models.loglogit(V, av, choice)

# Section 7: Estimate
results = biogeme_model.estimate()

# Section 8: Extract results
params_df = results.getEstimatedParameters()
```

## Usage

To run the estimation, execute the cell or run:

```python
# After loading data:
df, scenario_labels, dataset_path = load_dataset()

# Then run the explicit estimation section:
# The section will automatically execute when the cell is run
```

## Comparison with DCM1.py

This explicit implementation matches `DCM1.py` when called with:
```python
estimate_model(
    gender="male",
    df=df,
    labels=scenario_labels,
    output_dir=Path("reports/biogeme"),
    include_ascs=True,
    center_logs=True,
    y_scale=1.0,
    pooled=False
)
```

But written in detail with all steps explicit, making it:
- **Easier to understand** the exact specification
- **Easier to modify** for variations or debugging
- **Similar to** `test_biogeme.py` style (explicit and detailed)

## Notes

- All parameters are estimated freely except ASCs and centering/scaling fixed terms
- The first alternative (h0) serves as the base category for ASCs
- Quadratic terms and interactions are computed from centered variables
- Model uses multinomial logit (MNL) specification
- Estimation uses Biogeme's built-in optimization
