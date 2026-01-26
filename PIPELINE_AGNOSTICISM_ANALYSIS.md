# RURO MNL Estimation Pipeline - Agnosticism Analysis

**Date:** 2026-01-26
**Question:** Is the estimation pipeline specification/normalization/country/year agnostic?

## Executive Summary

**YES** - The pipeline is designed to be fully agnostic across all four dimensions:

| Dimension        | Agnostic? | Implementation                                    |
|------------------|-----------|---------------------------------------------------|
| Specification    | ✅ YES    | YAML-based configuration, fully parameterized     |
| Normalization    | ✅ YES    | Read from MNL metadata JSON                       |
| Country          | ✅ YES    | No hardcoded country logic (FR is doc only)       |
| Year             | ✅ YES    | No hardcoded year logic                           |

---

## 1. Specification Agnosticism ✅

### Design
- **YAML-based configuration**: All model specifications defined in external YAML files
- **Command-line argument**: `--spec-config estimation_spec_XXXX.yaml`
- **Parser-driven**: `estimation_spec_parser.py` reads YAML and constructs specification object

### Evidence
```python
# enh_RURO_estimate_FR.py:755
parser.add_argument(
    "--spec-config",
    type=Path,
    default=Path("estimation_spec.yaml"),
    help="Path to YAML specification file"
)

# Line 919
spec = parse_specification(spec_path)
```

### What Can Be Configured
1. **Utility functional form**: `log`, `box_cox`, `linear`
2. **Parameter structure**: Group-specific vs pooled parameters
3. **Shifters**: Leisure utility shifters (demographics)
4. **Hours/wage opportunity**: Flexible specification
5. **Initial values**: Custom starting points
6. **Bounds**: Parameter constraints
7. **Optimization settings**: Solver options

### Examples in Codebase
- `estimation_spec_minimal_theta0.yaml` - 17 parameters with thetas at bounds
- `estimation_spec_pooled_leisure.yaml` - 14 parameters with leisure pooling
- `estimation_spec_ultra_minimal.yaml` - 10 parameters with maximum pooling
- `estimation_spec_loc_empirical.yaml` - LOC wage specification

**Verdict**: FULLY AGNOSTIC - No hardcoded specification logic

---

## 2. Normalization Agnosticism ✅

### Design
- **Metadata-driven**: Normalization constants stored in `*__mnlmeta.json`
- **Validation**: Runtime checks ensure data matches metadata
- **Flexible structure**: Supports both flat and nested metadata formats

### Evidence
```python
# estimation_utils.py:554-562
norm = metadata["normalization"]
if "singles" in norm:
    # Nested structure
    c_scale = norm["singles"]["c_scale"]
    l_scale = norm["singles"]["l_scale"]
else:
    # Flat structure
    c_scale = norm["c_scale"]
    l_scale = norm["l_scale"]
```

### Normalization Constants Used
1. **`c_scale`**: Consumption normalization (e.g., 40000 EUR)
2. **`l_scale`**: Leisure normalization (e.g., 8760 hours/year)
3. **`l_male_scale`**: Male leisure for couples (if different)
4. **`w_scale`**: Wage normalization

### Validation
- Runtime validation checks that `c_norm = consumption / c_scale` matches data
- Warns if normalization differs from expected values

**Verdict**: FULLY AGNOSTIC - Constants read from metadata, no hardcoding

---

## 3. Country Agnosticism ✅

### Design
- **Data-driven**: Country determined by MNL input path
- **No country-specific logic**: All references to "France" are documentation only

### Evidence of France References (Documentation Only)
```python
# enh_RURO_estimate_FR.py:4 (docstring)
"Enhanced RURO MNL Estimation - France"

# Line 711 (argparse description)
description="Enhanced RURO MNL Estimation - France"

# Line 896 (log message)
logger.info("Enhanced RURO MNL Estimation - France")
```

### No Country-Specific Logic Found
Search revealed NO conditional logic based on country (no `if country == "fr"` patterns)

### How to Use for Different Countries
```bash
# Germany
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "path/to/de/2020/de_2020_RURO_mnl" \
  --output-dir "outputs/estimates/de/2020"

# Spain
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "path/to/es/2019/es_2019_RURO_mnl" \
  --output-dir "outputs/estimates/es/2019"
```

**Verdict**: FULLY AGNOSTIC - Only cosmetic "France" references in docs

---

## 4. Year Agnosticism ✅

### Design
- **Data-driven**: Year determined by MNL input path
- **No year-specific logic**: Examples use 2016 but no hardcoding

### Evidence
Search revealed NO conditional logic based on year (no temporal conditions)

### Year Information
- **Stored in metadata**: Year can be included in MNL metadata JSON
- **Output labeling**: Year extracted from path for output filenames
- **No temporal logic**: No "before/after 2015" type conditions

### How to Use for Different Years
```bash
# 2020 data
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "path/to/fr/2020/fr_2020_RURO_mnl" \
  --output-dir "outputs/estimates/fr/2020"

# 2018 data
python scripts/enhanced/enh_RURO_estimate_FR.py \
  --mnl-base "path/to/fr/2018/fr_2018_RURO_mnl" \
  --output-dir "outputs/estimates/fr/2018"
```

**Verdict**: FULLY AGNOSTIC - No year-specific logic

---

## 5. Data Format Requirements

For the pipeline to work with ANY country/year, the MNL data must follow this structure:

### Required Files
1. **`{prefix}_mnl_singles.parquet`** - Singles MNL dataset
2. **`{prefix}_mnl_couples.parquet`** - Couples MNL dataset
3. **`{prefix}__mnlmeta.json`** - Metadata with normalization constants

### Required Columns (Singles)
- `hhid`, `consumption`, `leisure`, `hours`, `wage`, `actual_choice`
- `working`, `working_pt1`, `working_pt2`, `working_ft`
- Demographics: `gsur`, `age_norm`, `n_children`, `educL`, `educM`, `educH`

### Required Columns (Couples)
- `hhid`, `consumption`
- `leisure_male`, `leisure_female`, `hours_male`, `hours_female`
- `wage_male`, `wage_female`, `actual_choice`
- `working_male`, `working_female`, `working_pt1_male`, etc.

### Metadata Structure
```json
{
  "normalization": {
    "c_scale": 40000,
    "l_scale": 8760,
    "w_scale": 20
  },
  "data_characteristics": {
    "country": "fr",
    "year": 2016,
    "n_singles": 1676,
    "n_couples": 2577
  }
}
```

---

## 6. Recommended Best Practices

### For Multi-Country/Year Analysis

1. **Consistent naming convention**:
   ```
   {country}_{year}_RURO_mnl_singles.parquet
   {country}_{year}_RURO_mnl_couples.parquet
   {country}_{year}_RURO_mnl__mnlmeta.json
   ```

2. **Separate output directories**:
   ```
   outputs/estimates/{country}/{year}/{spec_name}
   ```

3. **Version specifications**:
   ```
   specs/{country}/estimation_spec_{spec_name}.yaml
   specs/common/estimation_spec_baseline.yaml  # Shared specs
   ```

4. **Batch processing example**:
   ```bash
   for country in fr de es; do
     for year in 2016 2018 2020; do
       python scripts/enhanced/enh_RURO_estimate_FR.py \
         --mnl-base "data/$country/$year/${country}_${year}_RURO_mnl" \
         --output-dir "outputs/estimates/$country/$year" \
         --spec-config "specs/common/estimation_spec_baseline.yaml"
     done
   done
   ```

---

## 7. Limitations & Caveats

### Assumption: Common Data Structure
- All countries must use SAME column names
- All countries must use SAME variable definitions
- Metadata normalization must be comparable

### Not Yet Agnostic To:
1. **Variable names**: If a country uses `salaire` instead of `wage`, code will fail
2. **Choice set structure**: Assumes 100 alternatives (hours grid)
3. **Demographic coding**: Assumes educL/educM/educH binary indicators

### Future Enhancements
- **Schema validation**: JSON schema for MNL data format
- **Variable mapping**: Config file to map country-specific column names
- **Flexible choice sets**: Support variable numbers of alternatives

---

## 8. Conclusion

**The RURO MNL estimation pipeline IS agnostic across all four dimensions:**

✅ **Specification**: YAML-based, fully parameterized
✅ **Normalization**: Metadata-driven, validated at runtime
✅ **Country**: Data-driven, no country logic (FR is cosmetic)
✅ **Year**: Data-driven, no temporal logic

**To use the pipeline for a new country/year:**
1. Prepare MNL data in required format
2. Create metadata JSON with normalization constants
3. Create/reuse YAML specification
4. Run estimation with appropriate paths

**Script naming is misleading**: Despite being called `enh_RURO_estimate_FR.py`, the script works for ANY country. Consider renaming to `enh_RURO_estimate.py` for clarity.

---

## 9. Testing Recommendation

To verify agnosticism, test with:
- Different countries (DE, ES, IT)
- Different years (2015, 2018, 2020)
- Different normalizations (varying c_scale/l_scale)
- Different specifications (various YAML configs)

All should work without code changes, only data/config modifications.
