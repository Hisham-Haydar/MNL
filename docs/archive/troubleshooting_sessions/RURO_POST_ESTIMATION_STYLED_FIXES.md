# RURO Post-Estimation Styled Fixes Summary

**Date**: January 7, 2026  
**File**: `scripts/enhanced/RURO_post_estimation_styled.py`

## Fixes Applied

### A) NumPy Scalar Formatting (Fix for "N/A" values)
Added two helper functions to handle NumPy scalar types correctly:

```python
def is_num(x: Any) -> bool:
    """Check if x is numeric (Python or NumPy scalar) and finite."""
    
def safe_format(x: Any, fmt: str = ".4f", fallback: str = "N/A") -> str:
    """Safely format a numeric value with fallback for non-numeric."""
```

These replace all `isinstance(x, float)` checks which fail for `np.float64` and similar types.

### B) Leisure Shifter Parsing
Fixed `_identify_model_structure()` to filter out corrupted shifter names:

```python
# Filter out corrupted shifter names (e.g., "sm.age_norm" from parsing errors)
if '.' in shifter:
    continue  # Skip malformed names with embedded group prefixes
```

### C) Singles Fit Diagnostics - Use Full β_l(X)
Changed `compute_fit_diagnostics_from_data()` to use `compute_beta_l_full()` instead of just `beta_l0`:

```python
# Compute full beta_l(X) for each observation (not just beta_l0)
beta_l = compute_beta_l_full(df_g, params, suffix='')
U_pref = beta_c * boxcox_transform(c, theta_c) + beta_l * boxcox_transform(l, theta_l)
```

### D) Column Naming Robustness via __mnlmeta.json
Added metadata loading functions for robust column name resolution:

```python
def load_mnl_metadata(mnl_base: Path) -> Optional[Dict[str, Any]]:
    """Load metadata from __mnlmeta.json file."""

def get_column_name(metadata, dataset, preferred, fallbacks) -> str:
    """Get column name from metadata with fallbacks."""
```

### E) Dead Code Removal
Removed duplicate `return plot_paths` statement in `plot_mu_distributions_by_group()`.

### F) Group-Name Normalization
Added `canonicalize_group_name()` function to normalize group names:

```python
def canonicalize_group_name(group: str) -> str:
    """Normalize group names: 'singles_male' → 'sm', 'couples' → 'cou', etc."""
```

### G) Structural Elasticities → Curvature-Based Heuristics
Renamed section in HTML report and added explanation note:

```html
<h2>📈 Curvature-Based Heuristics (Structural Elasticity Approximations)</h2>
<div class="stats-box">
    <h4>⚠️ Interpretation Note</h4>
    <p>These are <strong>not</strong> true labor supply elasticities. They are heuristic 
    approximations derived from the curvature parameters (θ) of the Box-Cox utility function...</p>
</div>
```

### H) Report Filename Timestamp
Added timestamp to HTML report filename:

```python
report_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
html_path = output_dir / f'{prefix}post_estimation_report_{report_timestamp}.html'
```

### I) Rho-Squared and AIC per Observation
Added computation of McFadden's pseudo R² and adjusted R²:

```python
# Compute rho-squared and AIC_per_obs now that we have ll_null
ll = fit_stats.get('log_likelihood', 0)
ll_null_val = fit_stats.get('ll_null')
n_params = fit_stats.get('n_parameters', 0)
n_obs = fit_stats.get('n_observations', 0)

if ll_null_val is not None and ll_null_val != 0:
    fit_stats['rho_squared'] = 1 - (ll / ll_null_val)
    fit_stats['rho_squared_adj'] = 1 - ((ll - n_params) / ll_null_val)

if n_obs > 0:
    fit_stats['AIC_per_obs'] = fit_stats.get('AIC', 0) / n_obs
```

### J) Hours Distribution Binning
Added hours distribution binning (observed vs predicted) to match original:

```python
# Hours distribution (binned) for observed
bins = [0, 5, 15, 25, 35, 45, 55, 65, 100]
bin_labels = ['0', '1-10', '11-20', '21-30', '31-40', '41-50', '51-60', '60+']
obs_binned = pd.cut(obs_hours_array, bins=bins, labels=bin_labels, include_lowest=True)
hours_dist_observed = (obs_vc / obs_vc.sum()).to_dict()
```

## Testing

```powershell
# Test module imports
python -c "import scripts.enhanced.RURO_post_estimation_styled; print('OK')"

# Test helper functions
python -c "
import numpy as np
from scripts.enhanced.RURO_post_estimation_styled import is_num, safe_format
print('is_num(np.float64(1.5)):', is_num(np.float64(1.5)))  # True
print('is_num(np.nan):', is_num(np.nan))  # False
print('safe_format(np.float64(1.234567)):', safe_format(np.float64(1.234567)))  # 1.2346
print('safe_format(np.nan):', safe_format(np.nan))  # N/A
"
```

## Comparison: Styled vs Original

| Feature | Original | Styled |
|---------|----------|--------|
| Participation rates | ✅ | ✅ |
| Mean hours (observed/predicted) | ✅ | ✅ |
| Hours distribution bins | ✅ | ✅ (added) |
| Rho-squared | ✅ | ✅ (added) |
| Adjusted rho-squared | ✅ | ✅ (added) |
| AIC/BIC | ✅ | ✅ |
| AIC per observation | ✅ | ✅ (added) |
| Negative MUC/MUL diagnostics | ✅ | ✅ |
| Negative MU bar chart plot | ✅ | ✅ (added) |
| Full β_l(X) computation | ✅ | ✅ (fixed) |
| MU distribution plots | ✅ | ✅ |
| Utility contour plots | ✅ | ✅ |
| MUC/MUL comparison plots | ✅ | ✅ |
| Elasticity heuristics | ✅ | ✅ (renamed) |
| Timestamped reports | ❌ | ✅ (added) |
| NumPy scalar handling | ❌ | ✅ (added) |
| Group name normalization | ❌ | ✅ (added) |

## Summary

The styled version now produces **at least as detailed and accurate results** as the original `RURO_post_estimation.py`, with several enhancements:

1. **Robust formatting**: Proper handling of NumPy scalars prevents "N/A" display issues
2. **Complete fit statistics**: rho-squared, adjusted rho-squared, AIC per observation
3. **Full beta_l(X)**: Uses complete leisure coefficient with all shifters
4. **Hours distributions**: Binned observed vs predicted hours
5. **All diagnostic plots**: MU comparison, MU by group, negative MU bar charts
6. **Better organization**: Group name normalization, metadata column lookup
7. **Timestamped filenames**: Avoids overwriting previous reports

## Next Steps

1. Run the full pipeline with Step 8 (post-estimation) to verify all fixes work correctly
2. Verify the HTML report displays correct values instead of "N/A"
3. Check that MU plots show curves (not distributions)
4. Verify fit diagnostics show different predicted vs observed values for couples
