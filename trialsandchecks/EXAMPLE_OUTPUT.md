# Example Output and Expected Results

## What you'll see when running the estimation

### Console Output

```
Mean logy at actual choice: 10.523456
Mean logl at actual choice: 3.456789
Preparing Biogeme database for 5234 observations
Database created: 5234 observations
Defining Beta parameters for utility specification
Parameters defined: alpha_1-6, beta_1-2, gamma, centering/scaling terms
ASCs included for all 7 alternatives
Creating Variable expressions for all regressors
Building utility functions for 7 alternatives
Alternative h0 (id=1): utility function with 9 regressors + ASC
Alternative h1 (id=2): utility function with 9 regressors + ASC
Alternative h2 (id=3): utility function with 9 regressors + ASC
Alternative h3 (id=4): utility function with 9 regressors + ASC
Alternative h4 (id=5): utility function with 9 regressors + ASC
Alternative h5 (id=6): utility function with 9 regressors + ASC
Alternative h6 (id=7): utility function with 9 regressors + ASC
Creating logit model specification
Initializing Biogeme model
Running estimation with model name: dcm_male_explicit_ascsON_centered
Output directory: \\crc\users\hisham\Desktop\Nizam_Hisham\MNL\reports\biogeme\male_explicit
Estimation started with 5234 heads.

[Biogeme runs optimization...]

Estimation completed
Optimized log-likelihood: -8234.567
Null log-likelihood: -9123.456
Rho-squared: 0.097342
Adjusted Rho-squared: 0.094892

=== ESTIMATED PARAMETERS ===
                                    Value    Std err   t-stat   p-value
beta_log_consumption              0.8934     0.0234   38.18   <0.0001
beta_log_leisure                  1.2456     0.0456   27.31   <0.0001
beta_leila                        -0.1234     0.0189   -6.53   <0.0001
beta_log2_leila                   0.0456     0.0078    5.85   <0.0001
beta_log_leisure_children_total   -0.2345     0.0234   -10.02  <0.0001
beta_log_leisure_child_lt6_dummy  -0.3456     0.0345   -10.02  <0.0001
beta_log2_consumption             -0.0345     0.0089   -3.88   0.0001
beta_log2_leisure                 -0.0678     0.0145   -4.68   <0.0001
beta_logy_logl                     0.0234     0.0067    3.49   0.0005
ASC_h0                            0.0000     Fixed    -      -
ASC_h1                           -0.5234     0.1234   -4.24   <0.0001
ASC_h2                           -1.2345     0.1456   -8.48   <0.0001
ASC_h3                           -0.8765     0.1123   -7.81   <0.0001
ASC_h4                           -1.5678     0.1678   -9.34   <0.0001
ASC_h5                           -2.3456     0.2145  -10.94   <0.0001
ASC_h6                           -1.9876     0.1897  -10.47   <0.0001
C_LOGY                           10.523456   Fixed    -      -
C_LOGL                            3.456789   Fixed    -      -
LN_SCALE                          0.0000     Fixed    -      -

Parameters saved to: \\crc\users\hisham\Desktop\Nizam_Hisham\MNL\reports\biogeme\male_explicit\dcm_male_explicit_ascsON_centered_parameters.csv
Estimation and results extraction complete
```

## Output Files

### 1. Parameters CSV
`reports/biogeme/male_explicit/dcm_male_explicit_ascsON_centered_parameters.csv`

```csv
,Value,Std err,t-stat,p-value
beta_log_consumption,0.893399,0.023412,38.18,0.0000
beta_log_leisure,1.245563,0.045623,27.31,0.0000
beta_leila,-0.123412,0.018923,-6.53,0.0000
beta_log2_leila,0.045623,0.007812,5.85,0.0000
beta_log_leisure_children_total,-0.234512,0.023456,-10.02,0.0000
beta_log_leisure_child_lt6_dummy,-0.345612,0.034512,-10.02,0.0000
beta_log2_consumption,-0.034512,0.008912,-3.88,0.0001
beta_log2_leisure,-0.067834,0.014512,-4.68,0.0000
beta_logy_logl,0.023456,0.006712,3.49,0.0005
ASC_h0,0.000000,
ASC_h1,-0.523412,0.123412,-4.24,0.0000
ASC_h2,-1.234512,0.145623,-8.48,0.0000
ASC_h3,-0.876534,0.112345,-7.81,0.0000
ASC_h4,-1.567834,0.167834,-9.34,0.0000
ASC_h5,-2.345612,0.214561,-10.94,0.0000
ASC_h6,-1.987643,0.189734,-10.47,0.0000
C_LOGY,10.523456,
C_LOGL,3.456789,
LN_SCALE,0.000000,
```

## Model Statistics Summary

```
Total observations: 5,234
Estimated parameters: 16
  - Utility coefficients: 9
  - ASCs: 7 (1 fixed, 6 estimated)
  - Centering parameters: 3 (all fixed)

Log-Likelihood:
  - Optimized (at convergence): -8,234.57
  - Null (all parameters = 0): -9,123.46
  - Change: 888.89

Goodness of Fit:
  - McFadden's ρ² = (LL_opt - LL_null) / LL_null
    = (-8234.57 - (-9123.46)) / (-9123.46)
    = 888.89 / 9123.46
    = 0.0973 (9.73%)
  
  - Adjusted ρ² = 1 - (LL_opt - K) / LL_null
    = 1 - (-8234.57 - 6) / (-9123.46)
    = 1 - (-8240.57) / (-9123.46)
    = 1 - 0.9032
    = 0.0949 (9.49%)

Information Criteria:
  - AIC = 2K - 2*LL_opt = 2(16) - 2*(-8234.57) = 32 + 16,469.14 = 16,501.14
  - BIC = K*ln(n) - 2*LL_opt = 16*ln(5234) - 2*(-8234.57)
        = 16*8.562 - (-16469.14) = 136.99 + 16,469.14 = 16,606.13
```

## Interpretation Guide

### Coefficient Signs and Magnitudes

**Positive coefficients** (e.g., β_log_consumption = 0.894):
- Increasing consumption *increases* utility
- This is expected; higher consumption makes alternatives more attractive

**Negative coefficients** (e.g., β_log_leisure_children = -0.235):
- Increasing this variable *decreases* utility
- More children reduces utility (higher time cost for leisure)

**Quadratic terms** (e.g., β_log2_consumption = -0.035):
- Negative → diminishing marginal utility (standard assumption)
- Positive → increasing marginal utility (unusual, suggests possible model misspecification)

**ASCs** (e.g., ASC_h1 = -0.523):
- Negative ASCs indicate alternatives h1-h6 are less preferred than h0 (base)
- ASC_h0 = 0 by normalization (base category)
- The more negative an ASC, the less preferred that alternative

### Statistical Significance

Using **p-values**:
- p < 0.001: Highly significant (marked as `<0.0001`)
- p < 0.01: Very significant
- p < 0.05: Significant
- p > 0.05: Not significantly different from 0

In example output, most parameters are highly significant (p < 0.0001).

### Model Fit

**ρ² = 0.0973 (9.73%)**
- Interpretation: The model explains about 9.73% of the variation in choices
- Typical range for choice models: 0.20-0.40 is considered "good"
- This value is reasonable for labor supply models with aggregate data

## Comparing with DCM1.py

When you run the same specification with DCM1.py:
```bash
python scripts/DCM1.py --genders male --include-ascs --center-logs
```

The parameters in the CSV should match exactly (within numerical precision).

If you see differences:
1. Check that both are using the same data (same `load_dataset()` output)
2. Check scenario labels match (both using h0-h6)
3. Check centering/scaling values match
4. Verify BIOGEME version is the same

## Next Steps with Results

1. **Check coefficient signs**: Do they make economic sense?
2. **Review p-values**: Are important coefficients significant?
3. **Compare models**: Run variations (e.g., without ASCs, with different scaling)
4. **Calculate elasticities**: How do policy changes affect predicted choices?
5. **Simulate scenarios**: Use the estimated parameters for predictions
6. **Generate plots**: Visualize preference patterns
7. **Document findings**: Write up the labor supply model results
