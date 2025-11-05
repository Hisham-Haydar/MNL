# Code Structure Reference

## Location in File

The explicit estimation code is in `scripts/old_biogeme.py`, starting at **line 145** (after the data loading section).

## Section Breakdown

### Section 1: Imports and Configuration (Lines 145-170)

```python
import biogeme.database as db
import biogeme.biogeme as bio
import biogeme.models as models
from biogeme.expressions import Beta, Variable
from math import log as ln

# Configuration
INCLUDE_ASCS = True
CENTER_LOGS = True
Y_SCALE = 1.0
POOLED = False
```

**Purpose**: Import Biogeme components and set up estimation configuration flags.

### Section 2: Compute Centering Values (Lines 172-193)

```python
def compute_actual_choice_logs(df: pd.DataFrame, labels: Sequence[str]) -> tuple[float, float]:
    """Compute mean logy and logl at actual choice for centering."""
    # ... implementation ...
    return float(mean_logy), float(mean_logl)

mean_logy_actual, mean_logl_actual = compute_actual_choice_logs(df, scenario_labels)
```

**Purpose**: Calculate mean log(consumption) and log(leisure) at each person's actual choice. These values are used to center regressors for numerical stability.

**Output**:
- `mean_logy_actual`: e.g., 10.52
- `mean_logl_actual`: e.g., 3.46

### Section 3: Prepare Biogeme Database (Lines 195-217)

```python
df_bio = df.copy()
alt_ids = {label: idx + 1 for idx, label in enumerate(scenario_labels)}
df_bio["choice_id"] = df_bio["actual_choice"].map(alt_ids)

# Select columns and convert to numeric
numeric_df = df_bio[keep_columns].apply(pd.to_numeric, errors="coerce")

database = db.Database("labour_supply", numeric_df)
```

**Purpose**: Convert the pandas DataFrame into a Biogeme database object.

**Key transformations**:
- Map scenario labels (h0, h1, ..., h6) → choice IDs (1, 2, ..., 7)
- Select only necessary columns (choice_id + regressors + gender)
- Convert all to numeric type
- Create Biogeme database

**Output**: `database` object ready for model specification

### Section 4: Define Beta Parameters (Lines 219-248)

```python
# Main coefficients (9)
alpha_1 = Beta("beta_log_consumption", 0.0, None, None, 0)
alpha_2 = Beta("beta_log_leisure", 0.0, None, None, 0)
# ... (4 more alpha parameters)
beta_1 = Beta("beta_log2_consumption", 0.0, None, None, 0)
beta_2 = Beta("beta_log2_leisure", 0.0, None, None, 0)
gamma = Beta("beta_logy_logl", 0.0, None, None, 0)

# Centering parameters (3, fixed)
C_LOGY = Beta("C_LOGY", mean_logy_actual, None, None, 1)
C_LOGL = Beta("C_LOGL", mean_logl_actual, None, None, 1)
LN_SCALE = Beta("LN_SCALE", 0.0, None, None, 1)

# ASCs (7, one fixed)
if INCLUDE_ASCS:
    for idx, label in enumerate(scenario_labels):
        if idx == 0:
            asc_dict[label] = Beta(f"ASC_{label}", 0.0, None, None, 1)
        else:
            asc_dict[label] = Beta(f"ASC_{label}", 0.0, None, None, 0)
```

**Beta parameters format**: `Beta(name, start_value, lower_bound, upper_bound, fixed_flag)`
- `name`: Parameter name for output
- `start_value`: Starting value for optimization
- `lower_bound`/`upper_bound`: Bounds (None = unbounded)
- `fixed_flag`: 0 = estimate, 1 = fixed

**Total parameters**: 9 estimated + 7 ASCs (6 estimated, 1 fixed) + 3 centering (all fixed) = **19 total**

### Section 5: Create Variables (Lines 250-255)

```python
var_dict = {}
for label in scenario_labels:
    for var_name in SCENARIO_VARIABLES:
        var_dict[f"{var_name}_{label}"] = Variable(f"{var_name}_{label}")
```

**Purpose**: Create Biogeme Variable objects that reference columns in the database.

**Creates**: 9 variables × 7 labels = 63 total variable references

### Section 6: Build Utility Expressions (Lines 257-314)

```python
V = {}
av = {}

for label in scenario_labels:
    alt_id = alt_ids[label]
    
    # Extract variables
    logy_raw = var_dict[f"logy_{label}"]
    logl_raw = var_dict[f"logl_{label}"]
    # ... (5 more variables)
    
    # Apply centering transformation
    logy_centered = logy_raw - (LN_SCALE + C_LOGY)
    logl_centered = logl_raw - C_LOGL
    
    # Compute squares and interaction
    log2y_term = logy_centered * logy_centered
    log2l_term = logl_centered * logl_centered
    logyl_term = logy_centered * logl_centered
    
    # Build utility expression
    utility = (
        alpha_1 * logy_centered
        + alpha_2 * logl_centered
        + alpha_3 * leila
        + alpha_4 * leila2
        + alpha_5 * lochi
        + alpha_6 * logdc
        + beta_1 * log2y_term
        + beta_2 * log2l_term
        + gamma * logyl_term
    )
    
    # Add ASC
    if INCLUDE_ASCS:
        utility = utility + asc_dict[label]
    
    V[alt_id] = utility
    av[alt_id] = 1
```

**Purpose**: Define the utility function for each alternative.

**Key operations**:
1. Extract raw variables from database
2. Apply centering transformation
3. Compute derived terms (squares, interactions)
4. Build linear combination with coefficients
5. Add alternative-specific constant
6. Store in utility dictionary

**Utility formula for alternative k**:
```
V_k = [ASC_k +] α₁·logy* + α₂·logl* + α₃·Leila + α₄·Leila2 
      + α₅·lochi + α₆·logdc + β₁·(logy*)² + β₂·(logl*)² + γ·(logy*·logl*)

where:
  logy* = logy - LN_SCALE - C_LOGY
  logl* = logl - C_LOGL
```

**Output**:
- `V`: Dictionary mapping alternative IDs to utility expressions
- `av`: Dictionary mapping alternative IDs to availability (all = 1)

### Section 7: Specify and Estimate Model (Lines 316-345)

```python
# Create log-likelihood
choice = Variable("choice_id")
logprob = models.loglogit(V, av, choice)

# Create Biogeme model
model_name = "dcm_male_explicit_ascsON_centered"
output_dir = PROJECT_ROOT / "reports" / "biogeme" / "male_explicit"
output_dir.mkdir(parents=True, exist_ok=True)

biogeme_model = bio.BIOGEME(database, logprob)
# ... set model name and output directory ...

# Estimate
results = biogeme_model.estimate()
```

**Purpose**: Package the utilities into a logit model and run estimation.

**Steps**:
1. Define choice variable (`choice_id`)
2. Create multinomial logit log-likelihood using utilities, availability, and choice
3. Create Biogeme model object
4. Set model name and output directory
5. Call `estimate()` to run optimization

**Output**: `results` object containing estimated parameters and statistics

### Section 8: Extract and Display Results (Lines 347-394)

```python
# Get parameters
try:
    if hasattr(results, "get_pandas_estimated_parameters"):
        params_df = results.get_pandas_estimated_parameters()
    else:
        params_df = results.getEstimatedParameters()
except Exception as e:
    params_df = None

if params_df is not None:
    print(params_df)
    params_path = output_dir / f"{model_name}_parameters.csv"
    params_df.to_csv(params_path)

# Get fit statistics
try:
    opt_ll = results.getLogLikelihood()
    null_ll = results.getLLNull()
    rho2 = results.getRho2()
    rho2_adj = results.getRho2Adjusted()
except Exception as e:
    pass
```

**Purpose**: Extract and save results.

**Extracts**:
- Estimated parameters with standard errors and t-stats
- Log-likelihood (optimized and null)
- McFadden's ρ² and adjusted ρ²
- Variance-covariance matrices (if available)

**Saves**:
- Parameters to CSV file in output directory
- Prints summary to console

## Data Flow Diagram

```
┌─────────────────────────────┐
│  load_dataset()             │
│  (male singles, all labels) │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Section 2: Compute centering values │
│ mean_logy_actual, mean_logl_actual  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Section 3: Prepare database         │
│ Convert to numeric, map choices     │
└──────────────┬──────────────────────┘
               │
               ▼
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌────────────┐     ┌──────────────┐
│ Section 4: │     │ Section 5:   │
│ Betas      │     │ Variables    │
│ (9 main +  │     │ (63 var      │
│  3 center+ │     │  references) │
│  7 ASCs)   │     │              │
└────────────┘     └──────────────┘
    │                     │
    └──────────┬──────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Section 6: Build utilities          │
│ V[alt_id] for each alternative      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Section 7: Create model & estimate  │
│ Biogeme multinomial logit model     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ results object                      │
│ (parameters, statistics)            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Section 8: Extract results          │
│ Save CSV, print summaries           │
└─────────────────────────────────────┘
```

## Key Variables and Objects

| Variable | Type | Purpose |
|----------|------|---------|
| `df` | DataFrame | Loaded male singles data |
| `scenario_labels` | tuple | Alternative labels (h0-h6) |
| `database` | db.Database | Biogeme database object |
| `alpha_1`, ... `gamma` | Beta | Estimated coefficients |
| `C_LOGY`, `C_LOGL`, `LN_SCALE` | Beta | Fixed centering/scaling params |
| `asc_dict` | dict | Alternative-specific constants |
| `var_dict` | dict | Variable references to database |
| `V` | dict | Utility functions for each alt |
| `av` | dict | Availability flags |
| `logprob` | expression | Log-likelihood formula |
| `biogeme_model` | BIOGEME | Estimation object |
| `results` | Results | Optimization results |
| `params_df` | DataFrame | Estimated parameters with stats |

## Configuration Variations

To run different model specifications, modify the configuration section:

```python
# Specification 1: No ASCs
INCLUDE_ASCS = False
# ... rest is same

# Specification 2: No centering
CENTER_LOGS = False
# C_LOGY = Beta("C_LOGY", 0.0, ...)
# ... modify accordingly

# Specification 3: With scaling (e.g., thousands)
Y_SCALE = 1000.0
# LN_SCALE = Beta("LN_SCALE", ln(1000), ...)

# Specification 4: Different starting values
alpha_1 = Beta("beta_log_consumption", 0.5, None, None, 0)  # Changed from 0.0
```

Then re-run the entire section to estimate the new specification.
