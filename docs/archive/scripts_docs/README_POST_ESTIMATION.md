# Enhanced RURO Post-Estimation - Quick Start Guide

## Overview

The enhanced post-estimation module (`enh_RURO_post_estimation.py`) provides comprehensive post-estimation analysis for RURO labor supply models. It dynamically adapts to any specification and generates professional HTML reports with plots.

---

## Quick Start

### Basic Usage

```bash
python scripts/enhanced/enh_RURO_post_estimation.py \
  --results-json outputs/fr_2016_vw_joint/estimation_results.json \
  --mnl-base data/derived/fr_2016_mnl \
  --output-dir outputs/fr_2016_vw_joint \
  --prefix vw_joint_
```

### Command-Line Arguments

- `--results-json`: Path to `estimation_results.json` from estimation
- `--mnl-base`: Base path for MNL data files (without `__singles.parquet` suffix)
- `--output-dir`: Directory for post-estimation outputs
- `--prefix`: (Optional) Prefix for output files
- `--no-strict-validation`: (Optional) Disable strict metadata validation

---

## Outputs

### HTML Report
- **File**: `{prefix}post_estimation_report.html`
- **Contains**: All tables, plots, and diagnostics in one file
- **Open in browser**: Double-click to view

### CSV Files
1. **`{prefix}post_est_params.csv`** - Parameter estimates
2. **`{prefix}post_est_elasticities.csv`** - Labor supply elasticities
3. **`{prefix}post_est_fit.csv`** - Fit statistics
4. **`{prefix}post_est_marginal_utilities.csv`** - MU diagnostics

### PNG Plots
- **Fit comparison**: Observed vs predicted participation and hours
- **Marginal utilities**: MU means and % negative across groups
- **Utility contours**: One plot per demographic group/gender

---

## Example Workflow

### 1. Run Estimation

```bash
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base data/derived/fr_2016_mnl \
  --spec-config scripts/enhanced/estimation_spec.yaml \
  --output-dir outputs/fr_2016_vw_joint \
  --n-jobs 4
```

This creates:
- `outputs/fr_2016_vw_joint/estimation_results.json`
- `outputs/fr_2016_vw_joint/specification_used.yaml`
- CSV files with parameters

### 2. Run Post-Estimation

```bash
python scripts/enhanced/enh_RURO_post_estimation.py \
  --results-json outputs/fr_2016_vw_joint/estimation_results.json \
  --mnl-base data/derived/fr_2016_mnl \
  --output-dir outputs/fr_2016_vw_joint \
  --prefix vw_joint_
```

This creates:
- `outputs/fr_2016_vw_joint/vw_joint_post_estimation_report.html` ← **Open this!**
- CSV files with elasticities, fit stats, marginal utilities
- PNG plots embedded in HTML

### 3. View Results

Open the HTML report in your browser:
```bash
# Windows
start outputs/fr_2016_vw_joint/vw_joint_post_estimation_report.html

# Linux/Mac
open outputs/fr_2016_vw_joint/vw_joint_post_estimation_report.html
```

---

## What the HTML Report Contains

### Summary Statistics
- Joint log-likelihood
- Total observations and groups
- Estimation time

### Parameter Estimates Table
- All parameters by group (singles_male, singles_female, couples)
- Estimates with full precision

### Labor Supply Elasticities
- Hicksian (compensated) elasticities
- Marshallian (uncompensated) elasticities
- Extensive vs intensive margin decomposition
- Separate for males and females in couples

### Marginal Utility Diagnostics
- Mean and median MUC and MUL
- % of population with negative MU
- Warnings if > 5% negative

### Fit Diagnostics Plot
- Observed vs predicted participation rates (bar chart)
- Observed vs predicted mean hours (bar chart)

### Marginal Utility Plot
- Mean MUC and MUL by group
- % negative MUC and MUL (with 5% threshold line)

### Utility Contour Plots
- 2D utility surface in (consumption, leisure) space
- One plot per demographic group
- For couples: separate plots for males and females

---

## Python API

### From Python Script

```python
from pathlib import Path
from scripts.enhanced.enh_RURO_post_estimation import run_enhanced_post_estimation

results = run_enhanced_post_estimation(
    results_json_path=Path("outputs/fr_2016_vw_joint/estimation_results.json"),
    mnl_base=Path("data/derived/fr_2016_mnl"),
    output_dir=Path("outputs/fr_2016_vw_joint"),
    prefix="vw_joint_",
    strict_validation=True
)

# Access results
print(f"HTML report: {results['html_path']}")
print(f"Elasticities: {results['elasticities']}")
print(f"Marginal utilities: {results['mu_stats']}")
```

### Return Value

The function returns a dictionary with:
```python
{
    'fit_stats': dict,          # Fit diagnostics by group
    'elasticities': dict,       # Elasticity estimates by group
    'mu_stats': dict,           # Marginal utility statistics
    'params': ParsedParameters, # Parsed parameter object
    'html_path': Path,          # Path to HTML report
    'plot_paths': dict,         # Paths to all PNG plots
    'csv_paths': dict           # Paths to all CSV files
}
```

---

## Specifications Supported

The post-estimation system works with **any** YAML specification:

### Variable Wages (VW)
```bash
--spec-config scripts/enhanced/estimation_spec.yaml
```
- Mincer wage equation with education and experience
- 22 parameters for singles, 31 for joint

### Occupation-Based Wages (LOC4)
```bash
--spec-config scripts/enhanced/estimation_spec_loc_empirical.yaml
```
- 4 occupation groups with group-specific means/variances
- 26 parameters for singles, 35 for joint

### Fixed Wages (FW)
```yaml
specification:
  wage_spec: "fw"
```
- No wage opportunity parameters
- Simpler parameter set

### Custom Specifications
The system adapts to:
- Different leisure shifters (age, education, children, etc.)
- Different hours opportunity shifters
- Custom wage specifications
- Any parameter naming convention from YAML

---

## Interpreting Results

### Elasticities

**Hicksian (Compensated) Elasticity**: ε_h ≈ 1 - θ_l
- Measures labor supply response to wage changes holding utility constant
- Typical values: 0.2 to 0.8

**Marshallian (Uncompensated) Elasticity**: ε_m ≈ ε_h + income_effect
- Measures total labor supply response to wage changes
- Includes income effect (typically negative)
- Typical values: 0.1 to 0.7

**Extensive Margin** (30% of total): Participation decision (work vs not work)
**Intensive Margin** (70% of total): Hours conditional on working

### Marginal Utilities

**MUC (Marginal Utility of Consumption)**: ∂U/∂c = β_c × c^(θ_c - 1)
- Should be positive (more consumption is better)
- Should be diminishing (θ_c < 1 for concave utility)

**MUL (Marginal Utility of Leisure)**: ∂U/∂l = β_l(X) × l^(θ_l - 1)
- Should be positive (more leisure is better)
- Should be diminishing (θ_l < 1 for concave utility)

**Warning Signs**:
- > 5% negative MUC: Check β_c sign and θ_c value
- > 5% negative MUL: Check β_l0 sign and leisure shifters

### Fit Diagnostics

**Participation Rate**: Fraction working (h > 0)
- Compare observed vs predicted
- Good fit: < 5 percentage point difference

**Mean Hours (Workers)**: Average hours for those working
- Compare observed vs predicted
- Good fit: < 2 hour difference

---

## Troubleshooting

### Common Issues

**Issue**: Module not found
```
ImportError: No module named 'estimation_utils'
```
**Solution**: Run from project root or add to PYTHONPATH:
```bash
cd c:\Users\hisham\Desktop\Nizam_Hisham\MNL
python scripts/enhanced/enh_RURO_post_estimation.py ...
```

**Issue**: Matplotlib not available
```
WARNING: Matplotlib not available, skipping plot
```
**Solution**: Install matplotlib:
```bash
pip install matplotlib
```
Post-estimation will still work, but plots won't be generated.

**Issue**: Specification file not found
```
FileNotFoundError: Could not find specification file
```
**Solution**: Ensure `specification_used.yaml` is in the same directory as `estimation_results.json`, or specify with `--spec-config`.

**Issue**: Data file not found
```
FileNotFoundError: [path]__singles.parquet not found
```
**Solution**: Ensure `--mnl-base` points to the base path (without `__singles.parquet` suffix).

---

## Advanced Usage

### Multiple Specifications Comparison

```bash
# Run VW post-estimation
python scripts/enhanced/enh_RURO_post_estimation.py \
  --results-json outputs/fr_2016_vw_joint/estimation_results.json \
  --mnl-base data/derived/fr_2016_mnl \
  --output-dir outputs/fr_2016_vw_joint \
  --prefix vw_

# Run LOC4 post-estimation
python scripts/enhanced/enh_RURO_post_estimation.py \
  --results-json outputs/fr_2016_loc_joint/estimation_results.json \
  --mnl-base data/derived/fr_2016_mnl \
  --output-dir outputs/fr_2016_loc_joint \
  --prefix loc_

# Compare elasticities
diff outputs/fr_2016_vw_joint/vw_post_est_elasticities.csv \
     outputs/fr_2016_loc_joint/loc_post_est_elasticities.csv
```

### Automated Pipeline

Create a PowerShell script to run estimation + post-estimation:

```powershell
# run_full_pipeline.ps1

$MNL_BASE = "data\derived\fr_2016_mnl"
$SPEC = "scripts\enhanced\estimation_spec.yaml"
$OUTPUT = "outputs\fr_2016_vw_joint"

Write-Host "Step 1: Running Estimation..."
python scripts\enhanced\enh_RURO_estimate_FR.py `
  --mnl-base $MNL_BASE `
  --spec-config $SPEC `
  --output-dir $OUTPUT `
  --n-jobs 4

Write-Host "Step 2: Running Post-Estimation..."
python scripts\enhanced\enh_RURO_post_estimation.py `
  --results-json "$OUTPUT\estimation_results.json" `
  --mnl-base $MNL_BASE `
  --output-dir $OUTPUT `
  --prefix vw_joint_

Write-Host "Done! Opening report..."
start "$OUTPUT\vw_joint_post_estimation_report.html"
```

---

## Files Overview

### Input Files (Required)
1. **`estimation_results.json`** - From `enh_RURO_estimate_FR.py`
2. **`{mnl_base}__singles.parquet`** - Singles MNL data
3. **`{mnl_base}__couples.parquet`** - Couples MNL data (if joint estimation)
4. **`{mnl_base}__mnlmeta.json`** - Metadata with normalization constants
5. **`specification_used.yaml`** - YAML specification (auto-located)

### Output Files (Generated)
1. **HTML**: `{prefix}post_estimation_report.html`
2. **CSVs**: `{prefix}post_est_*.csv` (params, elasticities, fit, MU)
3. **PNGs**: `{prefix}post_est_*.png` (fit, MU, contours)

---

## Support

For issues or questions:
1. Check this README
2. Review [POST_ESTIMATION_COMPLETE.md](../../POST_ESTIMATION_COMPLETE.md) for technical details
3. Examine the module docstrings in `enh_RURO_post_estimation.py`
4. Check estimation logs in `estimation.log`

---

**Happy analyzing!** 📊
