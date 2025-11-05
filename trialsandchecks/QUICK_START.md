# Quick Start Guide: Explicit DCM Estimation

## What was added?

Added a complete, explicit DCM estimation code section to `scripts/old_biogeme.py` (starting after line 145) that:

1. **Loads pre-filtered male singles data** using the existing `load_dataset()` function
2. **Applies centering and scaling** to log(consumption) and log(leisure) around actual choice means
3. **Includes ASCs** (alternative-specific constants) for all scenario alternatives
4. **Estimates all coefficients** on the 9 regressors (logy, logl, Leila, Leila2, lochi, logdc, log2y, log2l, logyl)
5. **Saves results** as CSV files in `reports/biogeme/male_explicit/`

## How to run it

### Option 1: Run in Jupyter/IPython
```python
# In your Jupyter notebook or IPython session:
%run scripts/old_biogeme.py
```

The script will:
- Load data from the parquet file (if it exists)
- Run the full estimation 
- Print results and save CSV files

### Option 2: Run from command line
```powershell
cd \\crc\users\hisham\Desktop\Nizam_Hisham\MNL
python scripts/old_biogeme.py
```

### Option 3: Import and run specific parts
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'scripts'))

from old_biogeme import load_dataset
df, labels, path = load_dataset()

# Now run the estimation cells manually or copy the code
```

## What gets estimated?

| Parameter | Name | Type | Status |
|-----------|------|------|--------|
| α₁ | beta_log_consumption | Coefficient on log(y) | Estimated |
| α₂ | beta_log_leisure | Coefficient on log(l) | Estimated |
| α₃ | beta_leila | Leila interaction | Estimated |
| α₄ | beta_log2_leila | Leila quadratic | Estimated |
| α₅ | beta_log_leisure_children | Children effect | Estimated |
| α₆ | beta_log_leisure_child_lt6 | Young child effect | Estimated |
| β₁ | beta_log2_consumption | Curvature on log(y) | Estimated |
| β₂ | beta_log2_leisure | Curvature on log(l) | Estimated |
| γ | beta_logy_logl | Interaction log(y)×log(l) | Estimated |
| ASC_h0 to ASC_h6 | Alternative-specific constants | Constants per alternative | h0 fixed to 0, others estimated |

## Key features

✓ **Centering**: Regressors normalized around actual choice means for numerical stability
✓ **Scaling**: Support for scaling consumption (currently Y_SCALE=1.0, no scaling)
✓ **ASCs**: Alternative-specific constants included (first alternative normalized to 0)
✓ **Explicit**: Every step is detailed and easy to understand/modify
✓ **Detailed logging**: Progress messages at each estimation stage
✓ **Error handling**: Graceful handling of missing attributes and convergence issues

## Configuration options (modifiable)

Located near the top of the estimation section:

```python
INCLUDE_ASCS = True      # Set to False to remove ASCs
CENTER_LOGS = True       # Set to False to disable centering
Y_SCALE = 1.0           # Change to scale consumption (e.g., 1000 for thousands)
POOLED = False          # Set to True for pooled male/female (requires gender column)
```

## Output files

After estimation completes, you'll find in `reports/biogeme/male_explicit/`:

- `dcm_male_explicit_ascsON_centered_parameters.csv` - All estimated parameters
- Console output - Log-likelihood, ρ², adjusted ρ², convergence info

## Interpreting the results

The `_parameters.csv` file contains:

| Column | Meaning |
|--------|---------|
| Value | Estimated coefficient value |
| Std err | Standard error of the estimate |
| t-stat | t-statistic (Value / Std err) |
| p-value | Statistical significance |
| Rob. Std err | Robust standard error (if available) |
| Rob. t-stat | Robust t-statistic (if available) |
| Rob. p-value | Robust p-value (if available) |

## Differences from DCM1.py

This code is **equivalent to** calling from DCM1.py:
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

But:
- Written **explicitly step-by-step** (like test_biogeme.py)
- All operations are **visible in the code**
- Easier to **debug and modify**
- Includes **detailed logging** at each step

## Troubleshooting

### Issue: "FileNotFoundError: Missing wide DCM dataset"
**Solution**: Run `scripts/scenarios.py` first to generate the parquet dataset

### Issue: "NaN values detected in numeric data"
**Solution**: Check data for missing regressors; the model will drop rows with NaNs

### Issue: Estimation doesn't converge
**Solutions**:
1. Check data quality and outliers
2. Modify starting values for Beta parameters
3. Try different centering/scaling options
4. Reduce the number of parameters

### Issue: "Output directory not set"
**Solution**: The code handles this gracefully; check `reports/biogeme/male_explicit/` for results

## Next steps

After estimation:

1. **Examine results**: Open `_parameters.csv` to review coefficients
2. **Check fit**: Note log-likelihood and ρ² values
3. **Modify model**: Edit the estimation section to try variations
4. **Compare**: Run DCM1.py version and compare results
5. **Analyze**: Use results for policy simulations or elasticity calculations
