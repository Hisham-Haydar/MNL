# RURO Preference Estimation Capabilities

Date: May 11, 2026

Scope: detailed explanation of how the current code estimates preferences, parameter by parameter, using the French RURO MNL files and the Python/GAMSPy estimation pipeline.

## Bottom Line

The code estimates preferences through a discrete-choice RURO likelihood. Preferences enter as a Box-Cox utility function of normalized consumption and normalized leisure. The model estimates separate preference parameters for:

- Singles male households.
- Singles female households.
- Male partners in couples.
- Female partners in couples.
- Shared household consumption in couples.

The current best empirical preference estimates are from:

```text
outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2h_pruned/run_2026-02-20_11-25-18/estimation_results.json
```

That run used:

```text
scripts/enhanced/enh_RURO_estimate_FR.py
--group joint
--solver gamspy-conopt
--vectorized
--spec-config scripts/enhanced/estimation_spec_job_M2h_pruned.yaml
```

So the production code path for the current baseline is the vectorized GAMSPy estimator:

```text
scripts/enhanced/gamspy_estimation_vectorized.py
```

The non-vectorized GAMSPy and NumPy/SciPy code implement the same economic structure, but the reviewed French outputs were generated with `--vectorized`.

## 1. Estimation Flow

The preference estimation flow is:

1. Build counterfactual alternatives: hours, wages/jobs, taxes, disposable income, and proposal densities.
2. Convert those alternatives into MNL files.
3. Normalize consumption and leisure.
4. Load the YAML specification.
5. Construct the utility and opportunity index for each household and alternative.
6. Maximize the joint log-likelihood over preference and opportunity parameters.
7. Store final estimates, standard errors, Hessian diagnostics, and metadata in `estimation_results.json`.

Main files:

| File | Role |
| --- | --- |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | Creates consumption, leisure, demographics, normalized variables, and prior/proposal corrections. |
| `scripts/enhanced/estimation_utils.py` | Loads MNL files into precomputed arrays used by estimators. |
| `scripts/enhanced/estimation_spec_parser.py` | Reads YAML specs and creates the parameter list, initial values, and bounds. |
| `scripts/enhanced/gamspy_estimation_vectorized.py` | Production vectorized GAMSPy likelihood used by the current French runs. |
| `scripts/enhanced/gamspy_estimation.py` | Non-vectorized GAMSPy likelihood with the same utility structure. |
| `scripts/enhanced/estimation_engine.py` | NumPy/SciPy likelihood and analytical derivatives. Useful for validation and debugging. |

## 2. Preference Variables

### Consumption

For singles, consumption starts from EUROMOD disposable income:

```text
consumption = max(ils_dispy, 1.0)
```

For couples, household consumption is the sum of partner-level disposable income:

```text
consumption = max(ils_dispy_male, 1.0) + max(ils_dispy_female, 1.0)
```

The estimator uses normalized consumption:

```text
C = c_norm = consumption / c_scale
```

For singles, `c_scale` is the mean consumption across all alternatives. For couples, `c_scale` is the mean household consumption sum across all alternatives.

Important code references:

- `enh_RURO_prep_mnl_basic.py:694-729`: singles disposable income and consumption.
- `enh_RURO_prep_mnl_basic.py:1088-1198`: couples disposable income floor and partner-level consumption.
- `enh_RURO_prep_mnl_basic.py:1223-1259`: singles normalization.
- `enh_RURO_prep_mnl_basic.py:1274-1316`: couples normalization.
- `estimation_utils.py:604-608`: singles estimator arrays use `c_norm`.
- `estimation_utils.py:905-914`: couples estimator arrays use `c_norm`, `l_norm_male`, and `l_norm_female`.

### Leisure

Leisure is constructed from weekly hours:

```text
leisure = max(80.0 - hours, 1.0)
```

For couples:

```text
leisure_male   = max(80.0 - hours_male, 1.0)
leisure_female = max(80.0 - hours_female, 1.0)
```

The estimator uses normalized leisure:

```text
L        = l_norm
L_male   = l_norm_male
L_female = l_norm_female
```

The constant `80.0` is defined in `enh_RURO_prep_mnl_basic.py:52`.

### Demographic Preference Shifters

The code can use these demographic variables to shift the leisure coefficient:

| Variable | Construction | Role in preference utility |
| --- | --- | --- |
| `age_norm` | Age minus sample mean. For couples, partner-specific `age_norm_male` and `age_norm_female`. | Shifts the marginal utility of leisure. |
| `age_norm2` | Squared centered age. For couples, partner-specific squared terms. | Allows a quadratic age profile in leisure preferences. |
| `n_children` | Household number of children. Males are skipped when the spec marks this as gender-specific. | Shifts female leisure preferences. |
| `educL` | Low education dummy. | Shifts leisure preference relative to the omitted education group. |
| `educH` | High education dummy. | Shifts leisure preference relative to the omitted education group. |
| `educM` | Middle education dummy. | Usually omitted/reference category. |

In the current job-choice M2h pruned spec, only `age_norm`, `age_norm2`, `n_children`, and `educH` enter preferences. In the continuous v3 spec, both `educL` and `educH` enter.

## 3. Box-Cox Utility Transform

The economic utility uses a Box-Cox transform:

```text
BC(x, theta) = (x^theta - 1) / theta     if theta != 0
BC(x, 0)     = log(x)
```

Interpretation:

- `theta = 1` gives approximately linear utility in `x - 1`.
- `theta = 0` gives log utility.
- `theta < 1` implies diminishing marginal utility.
- More negative `theta` means stronger curvature near low values of consumption or leisure.

The NumPy/SciPy helper implements this directly in `estimation_utils.py:1249-1272`.

The vectorized GAMSPy helper uses a Taylor expansion around `theta = 0` in `gamspy_estimation_vectorized.py:185-203`. This gives a smooth expression for the nonlinear solver. This is an implementation detail worth validating because some current estimates, especially in the job-choice model, have `theta` values below `-2`, outside the range where a low-order Taylor approximation is naturally most accurate.

## 4. Preference Utility Formulas

The full choice index is:

```text
V_hj = U_hj(preferences)
     + H_hj(hours opportunity)
     + W_hj(wage opportunity)
     + M_hj(market opportunity, if present)
     - log(prior_hj)
```

The preference part is `U_hj`.

### Singles

For a single person in group `g`, where `g` is `sm` for singles male or `sf` for singles female:

```text
U_g =
    beta_c_g * BC(C, theta_c_g)
  + beta_l_g(Z) * BC(L, theta_l_g)
  + beta_cl_g * BC(C, theta_c_g) * BC(L, theta_l_g)   [only if spec includes beta_cl]
```

The leisure coefficient is:

```text
beta_l_g(Z) =
    beta_l0_g
  + beta_l_age_g * age_norm
  + beta_l_age2_g * age_norm2
  + beta_l_nkids_g * n_children       [female only in M2h]
  + beta_l_educH_g * educH
```

For continuous v3, the names are slightly different:

```text
beta_l_g(Z) =
    beta_l0_g
  + beta_l_age_norm_g * age_norm
  + beta_l_age_norm2_g * age_norm2
  + beta_l_n_children_g * n_children  [female only]
  + beta_l_educL_g * educL
  + beta_l_educH_g * educH
```

Production vectorized code references:

- `gamspy_estimation_vectorized.py:347-350`: creates consumption, leisure, chosen, and prior arrays.
- `gamspy_estimation_vectorized.py:377-388`: consumption utility.
- `gamspy_estimation_vectorized.py:390-416`: leisure utility and demographic shifters.
- `gamspy_estimation_vectorized.py:418-427`: optional consumption-leisure interaction.
- `gamspy_estimation_vectorized.py:590-610`: adds opportunity and prior correction, then forms log-likelihood.

### Couples

For couples, consumption is a household public-good term and is added once, not once per partner:

```text
U_couple =
    beta_c * BC(C, theta_c)
  + beta_l_m(Z_m) * BC(L_m, theta_l_m)
  + beta_l_f(Z_f) * BC(L_f, theta_l_f)
  + beta_cl_m * BC(C, theta_c) * BC(L_m, theta_l_m)   [only if spec includes beta_cl]
  + beta_cl_f * BC(C, theta_c) * BC(L_f, theta_l_f)   [only if spec includes beta_cl]
  + beta_interact * BC(L_m, theta_l_m) * BC(L_f, theta_l_f)   [only if spec includes beta_interact]
```

The male leisure coefficient is:

```text
beta_l_m(Z_m) =
    beta_l0_m
  + beta_l_age_m * age_norm_male
  + beta_l_age2_m * age_norm2_male
  + beta_l_educH_m * educH_male
```

The female leisure coefficient is:

```text
beta_l_f(Z_f) =
    beta_l0_f
  + beta_l_age_f * age_norm_female
  + beta_l_age2_f * age_norm2_female
  + beta_l_nkids_f * n_children
  + beta_l_educH_f * educH_female
```

For continuous v3, the corresponding names are `beta_l_age_norm_m`, `beta_l_age_norm2_m`, `beta_l_educL_m`, `beta_l_educH_m`, and similarly for `_f`.

Production vectorized code references:

- `gamspy_estimation_vectorized.py:645-649`: creates couples consumption, leisure, chosen, and prior arrays.
- `gamspy_estimation_vectorized.py:659-689`: resolves partner-specific variable names such as `age_norm_male` and `age_norm_female`.
- `gamspy_estimation_vectorized.py:697-708`: household consumption utility.
- `gamspy_estimation_vectorized.py:710-735`: male leisure utility.
- `gamspy_estimation_vectorized.py:737-763`: female leisure utility.
- `gamspy_estimation_vectorized.py:765-787`: optional consumption-leisure and male-female leisure interactions.
- `gamspy_estimation_vectorized.py:1023-1034`: adds opportunity and prior correction, then forms couples log-likelihood.

## 5. Parameter Naming Rules

The vectorized GAMSPy code uses this suffix convention:

| Group | Suffix | Example |
| --- | --- | --- |
| Singles male | `_sm` | `beta_c_sm`, `theta_l_sm` |
| Singles female | `_sf` | `beta_c_sf`, `theta_l_sf` |
| Couples male | `_m` | `beta_l0_m`, `theta_l_m` |
| Couples female | `_f` | `beta_l0_f`, `theta_l_f` |
| Couples household consumption | no suffix | `beta_c`, `theta_c` |

This is implemented in `gamspy_estimation_vectorized.py:59-86`. The function first tries the group-specific suffix and then falls back to a generic parameter if one exists.

## 6. What Each Preference Parameter Means

| Parameter family | Meaning | Where it enters |
| --- | --- | --- |
| `beta_c_sm`, `beta_c_sf` | Consumption utility scale for singles male/female. Positive values mean higher normalized consumption raises utility, conditional on curvature. | `beta_c_g * BC(C, theta_c_g)` |
| `beta_c` | Shared household consumption utility scale for couples. Consumption is added once for the household. | `beta_c * BC(C, theta_c)` |
| `theta_c_sm`, `theta_c_sf`, `theta_c` | Consumption curvature. Lower values imply stronger diminishing marginal utility. | Inside `BC(C, theta_c)` |
| `beta_l0_sm`, `beta_l0_sf`, `beta_l0_m`, `beta_l0_f` | Baseline leisure utility coefficient for each demographic group. | Multiplies `BC(L, theta_l)` |
| `beta_l_age_*` or `beta_l_age_norm_*` | Linear age effect on the leisure coefficient. | Adds to `beta_l(Z)` |
| `beta_l_age2_*` or `beta_l_age_norm2_*` | Quadratic age effect on the leisure coefficient. | Adds to `beta_l(Z)` |
| `beta_l_nkids_sf`, `beta_l_nkids_f` | Children effect on female leisure coefficient in job-choice specs. | Adds to female `beta_l(Z)` |
| `beta_l_n_children_sf`, `beta_l_n_children_f` | Same concept in continuous v3 naming. | Adds to female `beta_l(Z)` |
| `beta_l_educL_*` | Low education effect on leisure coefficient, relative to omitted education category. Used in continuous v3. | Adds to `beta_l(Z)` |
| `beta_l_educH_*` | High education effect on leisure coefficient, relative to omitted category. | Adds to `beta_l(Z)` |
| `theta_l_sm`, `theta_l_sf`, `theta_l_m`, `theta_l_f` | Leisure curvature for each group. Lower values imply stronger curvature in leisure utility. | Inside `BC(L, theta_l)` |
| `beta_cl_sm`, `beta_cl_sf`, `beta_cl_m`, `beta_cl_f` | Consumption-leisure interaction. Positive or negative values alter the local complementarity/substitutability between consumption and leisure. Used in continuous v3, not M2h pruned. | `beta_cl * BC(C) * BC(L)` |
| `beta_interact` | Male-female leisure interaction in couples. Used in continuous v3, not M2h pruned. | `beta_interact * BC(L_m) * BC(L_f)` |

Important interpretation point: leisure shifter parameters do not add utility directly. They change the coefficient on transformed leisure. For example, `beta_l_educH_f` changes how much female leisure matters for high-education women in couples.

## 7. Current Baseline Preference Specification: Job-Choice M2h Pruned

Specification:

```text
scripts/enhanced/estimation_spec_job_M2h_pruned.yaml
```

This is the current best empirical baseline because it has better convergence and Hessian diagnostics than the continuous French specs.

Preference block in this spec:

```text
utility:
  consumption:
    coefficient: beta_c
    box_cox_exponent: theta_c

  leisure:
    intercept: beta_l0
    box_cox_exponent: theta_l
    shifters:
      age_norm   -> beta_l_age
      age_norm2  -> beta_l_age2
      n_children -> beta_l_nkids, female only
      educH      -> beta_l_educH
```

This spec does not include:

- `beta_cl_*` consumption-leisure interaction terms.
- `beta_interact` male-female leisure interaction.
- `educL` preference shifters.

### Current M2h Pruned Preference Estimates

Output:

```text
outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2h_pruned/run_2026-02-20_11-25-18/estimation_results.json
```

Sample:

- 4,253 households.
- 850,600 household-alternative rows.
- 200 alternatives per household.
- Joint log-likelihood: `-22203.6096`.
- Hessian condition number: about `1.28e6`.
- Negative Hessian eigenvalues: `0`.

| Parameter | Estimate | Std. error | Interpretation |
| --- | ---: | ---: | --- |
| `beta_l0_sm` | 5.1782 | 0.9690 | Baseline leisure utility coefficient for single men. |
| `beta_l_age_sm` | 0.0982 | 0.0556 | Age shifts single-male leisure preference upward as age rises above the mean. |
| `beta_l_age2_sm` | 0.0054 | 0.0043 | Quadratic age shift for single-male leisure preference. |
| `beta_l_educH_sm` | -1.7053 | 0.9971 | High education lowers the single-male leisure coefficient relative to non-high education in this spec. |
| `beta_c_sm` | 0.7769 | 0.1117 | Consumption utility scale for single men. |
| `theta_l_sm` | -2.6696 | 0.5720 | Leisure curvature for single men. Strong diminishing marginal utility shape. |
| `theta_c_sm` | -1.5255 | NA | Consumption curvature for single men. This parameter is tightly fixed by bounds in M2h, so it is not freely estimated. |
| `beta_l0_sf` | 8.2219 | 1.3470 | Baseline leisure utility coefficient for single women. |
| `beta_l_age_sf` | -0.0175 | 0.0438 | Age shift for single-female leisure preference. Small and statistically weak in this run. |
| `beta_l_age2_sf` | 0.0028 | 0.0039 | Quadratic age shift for single-female leisure preference. |
| `beta_l_nkids_sf` | -0.2785 | 0.5133 | Children shift the leisure coefficient for single women. Statistically weak in this run. |
| `beta_l_educH_sf` | -4.5347 | 1.0338 | High education lowers the single-female leisure coefficient relative to non-high education. |
| `beta_c_sf` | 0.7324 | 0.1764 | Consumption utility scale for single women. |
| `theta_l_sf` | -2.1746 | 0.3245 | Leisure curvature for single women. |
| `theta_c_sf` | -1.5960 | 0.2621 | Consumption curvature for single women. |
| `beta_l0_m` | 3.9594 | 0.4836 | Baseline leisure utility coefficient for male partners in couples. |
| `beta_l_age_m` | -0.0379 | 0.0206 | Age shift for male-partner leisure preference. |
| `beta_l_age2_m` | 0.0032 | 0.0020 | Quadratic age shift for male-partner leisure preference. |
| `beta_l_educH_m` | -2.1277 | 0.4166 | High education lowers male-partner leisure coefficient relative to non-high education. |
| `theta_l_m` | -2.1822 | 0.2160 | Leisure curvature for male partners. |
| `beta_l0_f` | 6.8841 | 0.8438 | Baseline leisure utility coefficient for female partners in couples. |
| `beta_l_age_f` | -0.0526 | 0.0239 | Age shift for female-partner leisure preference. |
| `beta_l_age2_f` | 0.0002 | 0.0026 | Quadratic age shift for female-partner leisure preference. |
| `beta_l_nkids_f` | -0.1976 | 0.2502 | Children shift female-partner leisure coefficient. Statistically weak in this run. |
| `beta_l_educH_f` | -3.1981 | 0.5340 | High education lowers female-partner leisure coefficient relative to non-high education. |
| `theta_l_f` | -1.9073 | 0.1751 | Leisure curvature for female partners. |
| `beta_c` | 1.0262 | 0.1100 | Shared household consumption utility scale for couples. |
| `theta_c` | -2.8833 | 0.2082 | Shared household consumption curvature for couples. |

### How To Read The M2h Estimates

The positive `beta_c_*` and `beta_c` estimates mean that higher normalized consumption raises utility. The negative `theta_c` estimates mean that the utility gain is highly concave: additional consumption matters more at low normalized consumption than at high normalized consumption.

The positive `beta_l0_*` estimates mean baseline leisure has positive marginal utility for all groups. The negative `theta_l_*` estimates imply a concave transformed leisure shape.

The negative `beta_l_educH_*` estimates mean high education reduces the leisure coefficient relative to the omitted education category in this specification. Economically, after controlling for consumption, opportunities, market access, and demographics, high education is associated with a stronger relative tendency toward work or lower utility weight on leisure.

The children parameters are negative in M2h for single women and female partners, but they are statistically weak in this run. They should not be over-interpreted.

## 8. Richer Continuous V3 Preference Capability

Specification:

```text
scripts/enhanced/estimation_spec_v3.yaml
```

This spec supports a richer preference model than M2h:

- `educL` and `educH` leisure shifters.
- Consumption-leisure interactions `beta_cl_sm`, `beta_cl_sf`, `beta_cl_m`, `beta_cl_f`.
- Couple leisure interaction `beta_interact`.

However, the current continuous v3 French run is not reliable for final inference:

- Joint log-likelihood: `-6608.5910`.
- Hessian condition number: about `2.45e27`.
- Negative Hessian eigenvalues: `3`.

That means v3 demonstrates code capability, but not yet credible final empirical identification.

### Continuous V3 Preference Estimates, Exploratory Only

Output:

```text
outputs/estimates/fr/spec/v3/gamspy/run_2026-02-05_14-11-43/estimation_results.json
```

| Parameter | Estimate | Std. error | Interpretation |
| --- | ---: | ---: | --- |
| `beta_l0_sm` | 6.7600 | 0.2026 | Baseline leisure coefficient for single men. |
| `beta_l_age_norm_sm` | 0.0038 | 0.0236 | Linear age shift for single-male leisure coefficient. |
| `beta_l_age_norm2_sm` | 0.0013 | 0.0020 | Quadratic age shift for single-male leisure coefficient. |
| `beta_l_educL_sm` | 2.2484 | 0.0979 | Low education shift for single-male leisure coefficient. |
| `beta_l_educH_sm` | -1.2057 | 0.4732 | High education shift for single-male leisure coefficient. |
| `beta_c_sm` | 0.0543 | 0.2877 | Consumption scale for single men. Weak in v3. |
| `theta_l_sm` | -0.6070 | 0.1058 | Leisure curvature for single men. |
| `theta_c_sm` | -0.2114 | 0.1268 | Consumption curvature for single men. |
| `beta_cl_sm` | 1.9420 | 0.3940 | Consumption-leisure interaction for single men. |
| `beta_l0_sf` | 7.3799 | 0.1325 | Baseline leisure coefficient for single women. |
| `beta_l_age_norm_sf` | -0.0347 | 0.0241 | Linear age shift for single-female leisure coefficient. |
| `beta_l_age_norm2_sf` | 0.0028 | 0.0024 | Quadratic age shift for single-female leisure coefficient. |
| `beta_l_n_children_sf` | -0.2652 | 0.3176 | Children shift for single-female leisure coefficient. |
| `beta_l_educL_sf` | 0.8385 | 0.1057 | Low education shift for single-female leisure coefficient. |
| `beta_l_educH_sf` | -2.1331 | 0.3688 | High education shift for single-female leisure coefficient. |
| `beta_c_sf` | 0.0336 | 0.2774 | Consumption scale for single women. Weak in v3. |
| `theta_l_sf` | -0.6096 | 0.1092 | Leisure curvature for single women. |
| `theta_c_sf` | -0.5602 | 0.1275 | Consumption curvature for single women. |
| `beta_cl_sf` | 1.0887 | 0.3299 | Consumption-leisure interaction for single women. |
| `beta_l0_m` | 0.0483 | 0.4629 | Baseline leisure coefficient for male partners. Weak in v3. |
| `beta_l_age_norm_m` | -0.0052 | 0.0142 | Linear age shift for male partners. |
| `beta_l_age_norm2_m` | -0.0010 | 0.0013 | Quadratic age shift for male partners. |
| `beta_l_educL_m` | 0.4121 | 0.4412 | Low education shift for male partners. |
| `beta_l_educH_m` | -1.1042 | 0.2901 | High education shift for male partners. |
| `theta_l_m` | -0.6026 | NA | Leisure curvature for male partners. SE unavailable in this output. |
| `beta_cl_m` | 4.5449 | 0.3553 | Consumption-leisure interaction for male partners. |
| `beta_l0_f` | 5.2876 | 0.2083 | Baseline leisure coefficient for female partners. |
| `beta_l_age_norm_f` | -0.0636 | 0.0206 | Linear age shift for female partners. |
| `beta_l_age_norm2_f` | -0.0006 | 0.0019 | Quadratic age shift for female partners. |
| `beta_l_n_children_f` | 0.1000 | NA | Children shift for female partners. Appears fixed or not assigned an SE in this output. |
| `beta_l_educL_f` | -0.5174 | 0.6179 | Low education shift for female partners. |
| `beta_l_educH_f` | -1.5718 | 0.3025 | High education shift for female partners. |
| `theta_l_f` | -0.6607 | NA | Leisure curvature for female partners. SE unavailable in this output. |
| `beta_cl_f` | 7.6958 | 0.2737 | Consumption-leisure interaction for female partners. |
| `beta_c` | 1.0738 | 0.0299 | Shared household consumption scale for couples. |
| `theta_c` | 0.9823 | NA | Shared household consumption curvature for couples. SE unavailable in this output. |
| `beta_interact` | 6.5165 | NA | Male-female leisure interaction. SE unavailable in this output. |

Because the v3 Hessian is indefinite, these estimates should be treated as evidence that the code can estimate this richer preference structure, not as final preference estimates.

## 9. How The Likelihood Estimates These Parameters

For each household `h`, the data contain alternatives `j = 1, ..., J`. Exactly one alternative is observed/chosen.

The model computes:

```text
P(choice = j | h) = exp(V_hj) / sum_k exp(V_hk)
```

For the chosen alternative:

```text
log likelihood contribution = V_h,chosen - log(sum_k exp(V_hk))
```

The joint objective is:

```text
LL_joint = LL_singles_male + LL_singles_female + LL_couples
```

The vectorized code implements this at:

- `gamspy_estimation_vectorized.py:608-610` for singles.
- `gamspy_estimation_vectorized.py:1032-1034` for couples.
- `gamspy_estimation_vectorized.py:1591-1631` for the joint model.

Preference parameters are therefore estimated from within-household tradeoffs across alternatives. For example:

- If observed choices often select higher consumption alternatives despite lower leisure, the likelihood pushes up consumption utility or changes consumption curvature.
- If observed choices often select more leisure despite lower consumption, the likelihood pushes up leisure utility or changes leisure curvature.
- If this pattern differs by age, education, or children, the likelihood moves the leisure shifter parameters.
- If consumption and leisure tradeoffs vary jointly, the richer v3 model can move `beta_cl_*`.
- In couples, if male and female leisure choices are correlated beyond separate leisure terms, v3 can move `beta_interact`.

These parameters are estimated jointly with opportunity parameters. The model does not first estimate preferences in isolation and then estimate opportunity. The opportunity blocks are in the same likelihood, so a preference estimate should always be read conditional on the opportunity specification.

## 10. Bounds And Shape Restrictions

The YAML spec controls starting values and bounds.

In M2h pruned:

- `beta_c_sm`, `beta_c_sf`, and `beta_c` are bounded below at `0.05`.
- `beta_l0_sm`, `beta_l0_sf`, `beta_l0_m`, and `beta_l0_f` are bounded below at `0.05`.
- `theta_l_*` and most `theta_c_*` parameters are bounded between `-8.0` and `0.95`.
- `theta_c_sm` is tightly fixed at `[-1.525496001, -1.525495999]`.

This means `theta_c_sm` in M2h is not identified by the current run. It is imposed from the warm start / previous model.

The specs also support expression constraints such as:

- Marginal utility of consumption positive.
- Marginal utility of leisure positive.
- Decreasing marginal utility.

In M2h, expression constraints are enabled with soft penalties. The active M2h constraints shown in the YAML focus on positive leisure marginal utility for couples.

## 11. Capabilities

The current code can estimate:

- Group-specific consumption preference scales for singles.
- Shared household consumption preference scale for couples.
- Group-specific consumption curvature for singles.
- Shared household consumption curvature for couples.
- Group-specific leisure preference intercepts.
- Age and age-squared shifts in leisure preferences.
- Children shifts in female leisure preferences.
- Education shifts in leisure preferences.
- Group-specific leisure curvature.
- Optional consumption-leisure interactions.
- Optional male-female leisure interaction in couples.
- Joint preference and opportunity parameters in one likelihood.
- Standard errors, t-values, p-values, and Hessian diagnostics when the Hessian is usable.

## 12. Current Limitations

The code does not currently estimate:

- Random coefficients or continuous unobserved preference heterogeneity.
- A full distribution of preferences beyond observed group and demographic interactions.
- Separate individual consumption coefficients inside couples; couples use one shared household consumption coefficient.
- A final validated continuous RURO preference model for France. The continuous v3 capability exists, but the current v3 diagnostics are too weak for final claims.

Implementation issues to keep in mind:

1. The current best job-choice model fixes `theta_c_sm`, so single-male consumption curvature is imposed rather than estimated.
2. The vectorized GAMSPy Box-Cox transform uses a fourth-order Taylor approximation. Current `theta` estimates can be far from zero, so exact-vs-approximate utility checks are advisable.
3. Preference and opportunity are estimated jointly, so preference interpretation depends on the opportunity specification.
4. The richer continuous v3 model has an indefinite Hessian and should not be used as the final source of preference estimates.
5. Some v3 standard errors are unavailable, another reason to avoid strong inference from v3.

## 13. Practical Reporting Language

A precise way to describe the current code capability is:

> The code estimates a Box-Cox preference utility with group-specific consumption and leisure curvature, demographic shifts in the marginal utility of leisure, and optional consumption-leisure and within-couple leisure interactions. These preference parameters are estimated jointly with RURO opportunity terms in a multinomial logit likelihood using simulated alternatives and a proposal-density correction. The current best empirical preference estimates come from the job-choice M2h pruned model; the richer continuous v3 preference specification is implemented but not yet reliable for final inference because of weak Hessian diagnostics.

## 14. Recommended Next Improvements For Preference Estimation

1. Replace or validate the vectorized GAMSPy Box-Cox Taylor approximation against the exact NumPy formula at the estimated `theta` values.
2. Unfix `theta_c_sm` only after the model is stable enough to estimate it.
3. Add a preference-only diagnostic run with opportunity parameters fixed, then an opportunity-only run with preferences fixed.
4. Run a simulation recovery test where true preference parameters are known.
5. Add model cards for each preference spec showing which variables enter preferences and which enter opportunities.
6. Keep M2h pruned as the empirical baseline until a continuous RURO spec has stable Hessian diagnostics.
