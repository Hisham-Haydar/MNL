# RURO Joint Estimation - Complete Parameter Guide

## Executive Summary

The joint estimation combines **ALL THREE groups** (single males, single females, and couples) into a single model where:
- ✅ **Preferences** are **group-specific** (each group has its own utility function)
- ✅ **Opportunity densities** are **gender-shared** (labor market treats singles and couples the same by gender)

**Total Parameters:**
- **68 parameters** for fixed wages (`fw`)
- **100 parameters** for variable wages (`vw`)

---

## Parameter Structure

### 1. GROUP-SPECIFIC PREFERENCES (50 parameters)

These capture how each group values leisure vs consumption.

#### 1.1 Single Males Preferences (12 parameters)
```
[0]   sm.pref.beta_l0           - Leisure intercept
[1]   sm.pref.beta_l_log_age    - Age effect on leisure (log)
[2]   sm.pref.beta_l_log_age2   - Age² effect on leisure
[3]   sm.pref.beta_l_ch4_6      - Effect of children aged 4-6
[4]   sm.pref.beta_l_ch7_9      - Effect of children aged 7-9
[5]   sm.pref.beta_l_educL      - Low education effect
[6]   sm.pref.beta_l_educH      - High education effect
[7]   sm.pref.beta_l_reg2       - Region 2 effect
[8]   sm.pref.beta_c            - Consumption coefficient
[9]   sm.pref.theta_l           - Box-Cox leisure (curvature)
[10]  sm.pref.theta_c           - Box-Cox consumption (curvature)
[11]  sm.pref.beta_l_ch0_3      - Effect of children aged 0-3
```

#### 1.2 Single Females Preferences (13 parameters)
```
[12]  sf.pref.beta_l0           - Leisure intercept
[13]  sf.pref.beta_l_log_age    - Age effect on leisure (log)
[14]  sf.pref.beta_l_log_age2   - Age² effect on leisure
[15]  sf.pref.beta_l_ch4_6      - Effect of children aged 4-6
[16]  sf.pref.beta_l_ch7_9      - Effect of children aged 7-9
[17]  sf.pref.beta_l_educL      - Low education effect
[18]  sf.pref.beta_l_educH      - High education effect
[19]  sf.pref.beta_l_reg2       - Region 2 effect
[20]  sf.pref.beta_c            - Consumption coefficient
[21]  sf.pref.theta_l           - Box-Cox leisure (curvature)
[22]  sf.pref.theta_c           - Box-Cox consumption (curvature)
[23]  sf.pref.beta_l_ch0_3      - Effect of children aged 0-3
[24]  sf.pref.beta_l_reg3       - Region 3 effect (extra parameter for females)
```

#### 1.3 Couples Preferences (25 parameters)
Couples have separate preferences for male and female partners, plus interaction terms.

**Male Partner Leisure (10):**
```
[25]  cou.pref.beta_l0_m        - Male leisure intercept
[26]  cou.pref.beta_l_log_age_m - Male age effect
[27]  cou.pref.beta_l_log_age2_m- Male age² effect
[28]  cou.pref.beta_l_ch0_3_m   - Children 0-3 effect on male leisure
[29]  cou.pref.beta_l_ch4_6_m   - Children 4-6 effect on male leisure
[30]  cou.pref.beta_l_ch7_9_m   - Children 7-9 effect on male leisure
[31]  cou.pref.beta_l_reg2_m    - Male region 2 effect
[32]  cou.pref.beta_l_reg3_m    - Male region 3 effect
[33]  cou.pref.beta_l_educL_m   - Male low education effect
[34]  cou.pref.beta_l_educH_m   - Male high education effect
```

**Female Partner Leisure (10):**
```
[35]  cou.pref.beta_l0_f        - Female leisure intercept
[36]  cou.pref.beta_l_log_age_f - Female age effect
[37]  cou.pref.beta_l_log_age2_f- Female age² effect
[38]  cou.pref.beta_l_ch0_3_f   - Children 0-3 effect on female leisure
[39]  cou.pref.beta_l_ch4_6_f   - Children 4-6 effect on female leisure
[40]  cou.pref.beta_l_ch7_9_f   - Children 7-9 effect on female leisure
[41]  cou.pref.beta_l_reg2_f    - Female region 2 effect
[42]  cou.pref.beta_l_reg3_f    - Female region 3 effect
[43]  cou.pref.beta_l_educL_f   - Female low education effect
[44]  cou.pref.beta_l_educH_f   - Female high education effect
```

**Shared Parameters (5):**
```
[45]  cou.pref.theta_l_m        - Box-Cox male leisure
[46]  cou.pref.theta_l_f        - Box-Cox female leisure
[47]  cou.pref.theta_c          - Box-Cox household consumption
[48]  cou.pref.beta_c           - Household consumption coefficient
[49]  cou.pref.beta_interaction - Interaction: male leisure × female leisure
```

---

### 2. GENDER-SHARED OPPORTUNITY PARAMETERS

These capture labor market constraints - **SAME for singles and couples by gender**.

#### 2.1 Hours Opportunity - Males (9 parameters)
Used by both single males AND male partners in couples.

```
[50]  hopp_m.beta_work          - Working probability intercept
[51]  hopp_m.beta_pt1           - Part-time 1 (1-15h) indicator
[52]  hopp_m.beta_pt2           - Part-time 2 (16-30h) indicator
[53]  hopp_m.beta_ft            - Full-time (31-40h) indicator
[54]  hopp_m.beta_gsur          - GSUR probability effect
[55]  hopp_m.beta_work_educL    - Work × low education interaction
[56]  hopp_m.beta_work_educH    - Work × high education interaction
[57]  hopp_m.beta_work_reg2     - Work × region 2 interaction
[58]  hopp_m.beta_work_reg3     - Work × region 3 interaction
```

#### 2.2 Hours Opportunity - Females (9 parameters)
Used by both single females AND female partners in couples.

```
[59]  hopp_f.beta_work          - Working probability intercept
[60]  hopp_f.beta_pt1           - Part-time 1 (1-15h) indicator
[61]  hopp_f.beta_pt2           - Part-time 2 (16-30h) indicator
[62]  hopp_f.beta_ft            - Full-time (31-40h) indicator
[63]  hopp_f.beta_gsur          - GSUR probability effect
[64]  hopp_f.beta_work_educL    - Work × low education interaction
[65]  hopp_f.beta_work_educH    - Work × high education interaction
[66]  hopp_f.beta_work_reg2     - Work × region 2 interaction
[67]  hopp_f.beta_work_reg3     - Work × region 3 interaction
```

#### 2.3 Wage Opportunity - Males (16 parameters, `vw` only)
Wage equation for males (both singles and partners).

```
[68]  wopp_m.beta0              - Wage intercept
[69]  wopp_m.beta_educL         - Low education wage effect
[70]  wopp_m.beta_educH         - High education wage effect
[71]  wopp_m.beta_pexp          - Potential experience (linear)
[72]  wopp_m.beta_pexp2         - Potential experience (quadratic)
[73]  wopp_m.beta_reg2          - Region 2 wage effect (Bassin Parisien)
[74]  wopp_m.beta_reg3          - Region 3 wage effect (Nord-Pas-de-Calais)
[75]  wopp_m.beta_reg4          - Region 4 wage effect (Est)
[76]  wopp_m.beta_reg5          - Region 5 wage effect (Ouest)
[77]  wopp_m.beta_reg6          - Region 6 wage effect (Sud-Ouest)
[78]  wopp_m.beta_reg7          - Region 7 wage effect (Centre-Est)
[79]  wopp_m.beta_reg8          - Region 8 wage effect (Méditerranée)
[80]  wopp_m.beta_reg9          - Region 9 wage effect (DOM)
[81]  wopp_m.beta_yd1           - Year dummy 1
[82]  wopp_m.beta_yd2           - Year dummy 2
[83]  wopp_m.sigma              - Wage variance (log-normal)
```

#### 2.4 Wage Opportunity - Females (16 parameters, `vw` only)
Wage equation for females (both singles and partners).

```
[84]  wopp_f.beta0              - Wage intercept
[85]  wopp_f.beta_educL         - Low education wage effect
[86]  wopp_f.beta_educH         - High education wage effect
[87]  wopp_f.beta_pexp          - Potential experience (linear)
[88]  wopp_f.beta_pexp2         - Potential experience (quadratic)
[89]  wopp_f.beta_reg2          - Region 2 wage effect
[90]  wopp_f.beta_reg3          - Region 3 wage effect
[91]  wopp_f.beta_reg4          - Region 4 wage effect
[92]  wopp_f.beta_reg5          - Region 5 wage effect
[93]  wopp_f.beta_reg6          - Region 6 wage effect
[94]  wopp_f.beta_reg7          - Region 7 wage effect
[95]  wopp_f.beta_reg8          - Region 8 wage effect
[96]  wopp_f.beta_reg9          - Region 9 wage effect
[97]  wopp_f.beta_yd1           - Year dummy 1
[98]  wopp_f.beta_yd2           - Year dummy 2
[99]  wopp_f.sigma              - Wage variance (log-normal)
```

---

## Bounds Analysis

### Current Bounds (in code)

```python
# Box-Cox parameters (indices 9, 10, 21, 22, 45, 46, 47)
bounds[9] = (0.01, 2.0)    # sm.pref.theta_l
bounds[10] = (0.01, 2.0)   # sm.pref.theta_c
bounds[21] = (0.01, 2.0)   # sf.pref.theta_l
bounds[22] = (0.01, 2.0)   # sf.pref.theta_c
bounds[45] = (0.01, 2.0)   # cou.pref.theta_l_m
bounds[46] = (0.01, 2.0)   # cou.pref.theta_l_f
bounds[47] = (0.01, 2.0)   # cou.pref.theta_c

# Wage variance (vw only, indices 83, 99)
bounds[83] = (0.01, 2.0)   # wopp_m.sigma
bounds[99] = (0.01, 2.0)   # wopp_f.sigma
```

### Why Bounds Exist

1. **Box-Cox Curvature (`theta_l`, `theta_c`):**
   - Theory: Should be in (0, 1] for concave utility
   - Bounds (0.01, 2.0) allow slight convexity for numerical exploration
   - **Recommendation:** Keep bounds for numerical stability
   - **Alternative:** Use log-barrier penalty instead of hard bounds

2. **Wage Variance (`sigma`):**
   - Must be positive for log-normal distribution
   - Bounds (0.01, 2.0) prevent numerical issues
   - **Recommendation:** Keep bounds (variance cannot be negative)

3. **All Other Parameters:**
   - No theoretical bounds needed
   - Already unbounded in code

### Removing Bounds (If Desired)

To remove ALL bounds and let optimizer explore freely:

```python
# In joint estimation section, replace:
bounds = [(None, None)] * len(theta0)
# Remove all bounds[...] = (...) assignments
```

**⚠️ Warning:** Removing Box-Cox bounds may cause:
- Negative theta values → division by zero
- Very large theta values → numerical overflow
- Optimizer convergence issues

---

## Post-Estimation Diagnostics Available

### 1. From CLI Mode (Current Implementation)
When you run `RURO_post_estimation.py` with `--results`:

✅ **Available:**
- Parameter estimates (all 100 parameters with names)
- Log-likelihood value
- Model fit statistics:
  - AIC (Akaike Information Criterion)
  - BIC (Bayesian Information Criterion)
  - McFadden's Pseudo R²
  - Adjusted Pseudo R²
  - LL per observation
- Marginal utility plots:
  - MUC (Marginal Utility of Consumption)
  - MUL (Marginal Utility of Leisure)
  - MRS (Marginal Rate of Substitution)
  - Combined visualization
- Parameter significance visualization
- Comprehensive HTML report

⚠️ **Limited:**
- Standard errors: Cannot compute Hessian without gradient function
- t-values: Not available in CLI mode
- p-values: Not available in CLI mode
- Correlation matrix: Not available
- Elasticities: Framework only, not computed

### 2. From Full Post-Estimation (Requires Integration)
To get full diagnostics, need to call `run_post_estimation()` from within estimation script with gradient function:

✅ **Would Add:**
- Standard errors (via Jacobian and numeric Hessian)
- t-values and p-values for all parameters
- Parameter correlation matrix
- Hessian eigenvalues (positive-definiteness check)
- Gradient accuracy check
- Labor supply elasticities
- Excel export with all results

---

## How to Run

### Option 1: Quick Joint Estimation (Recommended)
```powershell
cd U:\Desktop\Nizam_Hisham\MNL
powershell -ExecutionPolicy Bypass -File .\scripts\run_fr_2016_joint_only.ps1
```

This script:
- Runs joint estimation only (assumes steps 1-6 complete)
- Generates post-estimation analysis automatically
- Creates detailed log file
- Outputs HTML report with all available diagnostics

### Option 2: Manual Joint Estimation
```powershell
cd U:\Desktop\Nizam_Hisham\MNL

# Estimation
.venv\Scripts\python.exe scripts\RURO_estimate_FR.py `
  --mnl-file "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl.parquet" `
  --joint `
  --wage-spec vw `
  --optimizer L-BFGS-B `
  --maxiter 500 `
  --use-numba `
  --n-jobs 64 `
  --out-file "outputs\estimates\fr\2016\fr_2016_joint.json"

# Post-Estimation
.venv\Scripts\python.exe scripts\RURO_post_estimation.py `
  --results "outputs\estimates\fr\2016\fr_2016_joint.json" `
  --mnl-file "U:\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl.parquet" `
  --out-dir "outputs\post_estimation\fr\2016\joint" `
  --wage-spec vw `
  --sex pooled
```

### Option 3: Full Pipeline (Steps 1-8)
```powershell
cd U:\Desktop\Nizam_Hisham\MNL
powershell -ExecutionPolicy Bypass -File .\scripts\run_fr_2016_pipeline.ps1
```

---

## Expected Output

### Files Created
```
outputs/
  estimates/
    fr/
      2016/
        fr_2016_joint.json              # Estimation results
  
  post_estimation/
    fr/
      2016/
        joint/
          vw_pooled_muc.png             # MUC plot
          vw_pooled_mul.png             # MUL plot
          vw_pooled_mu_combined.png     # Combined MU plot
          vw_pooled_mrs.png             # MRS plot
          vw_pooled_param_significance.png  # Parameter plot
          vw_pooled_post_estimation_report.html  # Full HTML report
  
  logs/
    fr_2016_joint_only_YYYY-MM-DD_HH-mm-ss.md  # Execution log
```

### Estimation Performance (Expected)
- **Time:** ~3-5 minutes with analytical gradient
- **Iterations:** ~50-150 iterations to convergence
- **Function evaluations:** ~50-150 (with analytical gradient)
- **Log-likelihood:** ~-7,000 to -10,000 (depends on data fit)

---

## Interpretation Guide

### Preference Parameters
- **`beta_l0` > 0:** Base preference for leisure
- **`beta_l_log_age` < 0:** Leisure preference decreases with age
- **`beta_l_educH` < 0:** High education → less leisure (work more)
- **`beta_c` > 0:** Positive valuation of consumption
- **`theta_l`, `theta_c` ∈ (0,1):** Concave utility (risk aversion)
- **`beta_interaction` > 0:** Complementarity (partners enjoy leisure together)

### Opportunity Parameters
- **`beta_work` < 0:** Work has disutility (reduces choice probability)
- **`beta_gsur` > 0:** Higher GSUR probability → more hours available
- **`beta_educH` (wage)` > 0:** High education → higher wages
- **`sigma` > 0:** Wage dispersion (larger = more wage variation)

### Model Fit
- **Pseudo R²** > 0.2: Good fit
- **AIC/BIC:** Lower is better (compare across specifications)
- **LL per observation:** Closer to 0 is better

---

## Troubleshooting

### Issue: "Cannot compute Hessian without gradient function"
**Solution:** This is expected in CLI mode. To get full SE, need to integrate post-estimation into estimation script.

### Issue: Optimization not converging
**Solutions:**
- Increase `--maxiter 500` → `--maxiter 1000`
- Try different optimizer: `--optimizer BFGS`
- Provide better initial values via `--init-params`

### Issue: Parameter hitting bounds
**Solution:** If Box-Cox parameters hit 0.01 or 2.0, may need to:
- Adjust bounds
- Check data normalization
- Use log-barrier penalty instead

---

## Summary

| Aspect | Details |
|--------|---------|
| **Total Parameters** | 100 (vw) or 68 (fw) |
| **Group-Specific** | 50 preference parameters |
| **Gender-Shared** | 18 hours + 32 wage opportunity |
| **Bounds** | 9 bounded (Box-Cox + sigma), rest unbounded |
| **Estimation Time** | ~3-5 minutes with analytical gradient |
| **Post-Est Available** | Plots, fit stats, HTML report |
| **Post-Est Limited** | Standard errors (need gradient integration) |
| **Recommended Run** | Use `run_fr_2016_joint_only.ps1` |

