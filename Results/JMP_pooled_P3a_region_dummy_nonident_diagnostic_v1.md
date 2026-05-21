# JMP Pooled P3a — Region-Dummy Non-Identification Diagnostic v1

**Model**: RURO occupation-opportunity P3a, pooled 2015–2017  
**Specification**: `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml`  
**Date**: 2026-05-21  
**Analyst**: read-only diagnostic; no estimation run, no data modification

---

## 1. Diagnostic verdict

**Root cause confirmed: B/DEGENERATE_OR_MISWIRED_COLUMNS.**

The region-dummy columns `reg_nuts1_2`–`reg_nuts1_8` are present in the couples split parquet with all 743,800 values missing (NaN). Because `estimation_utils.py:precompute_data_couples` uses schema-presence (`if "reg_nuts1_2" in df.columns`) rather than value-presence to choose between the direct column path and the `drgn1` fallback, it takes the direct path and calls `fillna(0.0)` — producing seven all-zero arrays. In `_compute_market_opportunity_couples` the region-dummy contribution is `beta_E_drgn_k × 0 × working = 0` for every alternative and every observation. The gradient of the joint log-likelihood with respect to `beta_E_drgn2`–`beta_E_drgn8` is identically zero at all parameter values; the likelihood is exactly flat in these seven directions.

A separate guard in `_compute_market_opportunity_singles` (line 116–117) skips every shifter with `applies_to in {"cm", "cf", "household"}`, so region dummies never enter the singles market-opportunity index either. The two zero-contribution pathways are independent and together guarantee complete non-identification.

The `drgn1` column in the couples parquet is valid (743,800 non-missing rows, 8 unique region codes, all 8×3 region×year cells populated). No structural collinearity exists. The non-identification is entirely a data-build artifact: `reg_nuts1_k` was not populated during the pooled P3a construction step.

---

## 2. Authorization scope

This diagnostic is read-only. Authorized actions are:

- Read parquet data files, specification YAML, precompute source code, engine source code, SE JSON results.
- Run Python scripts that read existing files and compute statistics. No writes to data, no writes to spec, no new estimation calls.

Explicitly out of scope:

- Running the solver or re-estimating any model.
- Modifying data files or specification files.
- Computing welfare effects.
- Issuing an SA2 verdict.
- Promoting any model or output to canonical status.
- Replacing M1-clean 2016 as the active JMP baseline.

---

## 3. Files inspected

| File | Role |
|------|------|
| `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml` | Specification for the P3a pooled run |
| `scripts/enhanced/estimation_engine.py` | Market-opportunity computation for singles and couples |
| `scripts/enhanced/estimation_utils.py` | Precompute functions: `precompute_data_singles`, `precompute_data_couples` |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__singles.parquet` | Singles split data (500,700 rows) |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet` | Couples split data (743,800 rows) |
| `Results/JMP_pooled_P3a_start1_cluster_robust_se.json` | Cluster-robust SE, start 1 |
| `Results/JMP_pooled_P3a_start2_cluster_robust_se.json` | Cluster-robust SE, start 2 |
| `Results/JMP_pooled_P3a_start3_cluster_robust_se.json` | Cluster-robust SE, start 3 |
| `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_1/run_2026-05-21_16-38-29/estimation_results.json` | Estimation results start 1 |
| `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_2/run_2026-05-21_17-10-39/estimation_results.json` | Estimation results start 2 |
| `outputs/estimates/fr/spec/ruro_occ_P3a_pooled/gamspy/start_3/run_2026-05-21_17-42-29/estimation_results.json` | Estimation results start 3 |

Diagnostic Python scripts executed (read-only, no side effects):

- `C:\Users\hisham\AppData\Local\Temp\diag_region_dummy.py` — column integrity, wiring, collinearity, flat-LL check
- `C:\Users\hisham\AppData\Local\Temp\diag_region_dummy2.py` — applies_to guard, gsur pathway, drgn1 fallback trace, year-indicator check, LL parity
- `C:\Users\hisham\AppData\Local\Temp\p3a_diagnostics.py` — parameter comparison across starts, SE analysis, VCV block

---

## 4. Region-dummy columns and variable mapping

The P3a pooled specification defines seven region-dummy market-opportunity shifters, excluding region 1 (Île-de-France) as the reference:

| YAML variable | Parquet column | GAMS/engine attribute | Coefficient |
|---------------|----------------|-----------------------|-------------|
| `reg_nuts1_2` | `reg_nuts1_2` | `data.reg2` | `beta_E_drgn2` |
| `reg_nuts1_3` | `reg_nuts1_3` | `data.reg3` | `beta_E_drgn3` |
| `reg_nuts1_4` | `reg_nuts1_4` | `data.reg4` | `beta_E_drgn4` |
| `reg_nuts1_5` | `reg_nuts1_5` | `data.reg5` | `beta_E_drgn5` |
| `reg_nuts1_6` | `reg_nuts1_6` | `data.reg6` | `beta_E_drgn6` |
| `reg_nuts1_7` | `reg_nuts1_7` | `data.reg7` | `beta_E_drgn7` |
| `reg_nuts1_8` | `reg_nuts1_8` | `data.reg8` | `beta_E_drgn8` |

Each shifter is specified with `applies_to: "household"` and `interaction: ["working"]`. Region 1 (Île-de-France) is the omitted category and enters via the baseline intercept. The specification also includes year-indicator shifters (`year_2015_indicator`, `year_2017_indicator`) with the same `applies_to: "household"` and `interaction: ["working"]` structure; year 2016 is the reference year.

---

## 5. Column integrity in singles split file

**File**: `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__singles.parquet`  
**Rows**: 500,700 · **Columns**: 148 · **Unique singles households × year-tags**: 5,007

| Column | Missing | Non-null unique | Assessment |
|--------|---------|-----------------|------------|
| `reg_nuts1_2` | 0 / 500,700 | 2 (0, 1) | PASS — valid binary dummy |
| `reg_nuts1_3` | 0 / 500,700 | 2 (0, 1) | PASS |
| `reg_nuts1_4` | 0 / 500,700 | 2 (0, 1) | PASS |
| `reg_nuts1_5` | 0 / 500,700 | 2 (0, 1) | PASS |
| `reg_nuts1_6` | 0 / 500,700 | 2 (0, 1) | PASS |
| `reg_nuts1_7` | 0 / 500,700 | 2 (0, 1) | PASS |
| `reg_nuts1_8` | 0 / 500,700 | 2 (0, 1) | PASS |

Singles region distribution (households; region 1 = baseline, 653 households):

| Region | Households |
|--------|-----------|
| 1 (Île-de-France) | 653 |
| 2 | 623 |
| 3 | 287 |
| 4 | 335 |
| 5 | 673 |
| 6 | 456 |
| 7 | 471 |
| 8 | 404 |

All region dummies are correctly populated in the singles split. However, this fact is structurally irrelevant to identification because region dummies are skipped for singles by the `applies_to: "household"` guard (see Section 12).

---

## 6. Column integrity in couples split file

**File**: `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet`  
**Rows**: 743,800 · **Columns**: 148 · **Unique couples households × year-tags**: 7,438

| Column | Missing | Non-null unique | Assessment |
|--------|---------|-----------------|------------|
| `reg_nuts1_2` | 743,800 / 743,800 | 0 | **FAIL — entirely NaN** |
| `reg_nuts1_3` | 743,800 / 743,800 | 0 | **FAIL — entirely NaN** |
| `reg_nuts1_4` | 743,800 / 743,800 | 0 | **FAIL — entirely NaN** |
| `reg_nuts1_5` | 743,800 / 743,800 | 0 | **FAIL — entirely NaN** |
| `reg_nuts1_6` | 743,800 / 743,800 | 0 | **FAIL — entirely NaN** |
| `reg_nuts1_7` | 743,800 / 743,800 | 0 | **FAIL — entirely NaN** |
| `reg_nuts1_8` | 743,800 / 743,800 | 0 | **FAIL — entirely NaN** |
| `drgn1` | 0 / 743,800 | 8 (1–8) | PASS — valid fallback column |

The `drgn1` column is fully populated in the couples split. Confirmation:

```
After fillna(0.0): reg_nuts1_2 -> unique=[0.0]  sum=0.0
```

The seven all-NaN columns are present in the parquet schema (column names exist) even though all values are missing. This schema presence — not value presence — is what triggers the wrong branch in `precompute_data_couples` (see Section 11).

---

## 7. Region support by year_tag and household type

**Couples** (7,438 household × year-tag observations, derived from `drgn1`):

| Region | year_tag=1 (2015) | year_tag=2 (2016) | year_tag=3 (2017) | Total |
|--------|-------------------|--------------------|-------------------|-------|
| 1 | 378 | 383 | 336 | 1,097 |
| 2 | 484 | 446 | 419 | 1,349 |
| 3 | 197 | 191 | 172 | 560 |
| 4 | 239 | 227 | 197 | 663 |
| 5 | 445 | 484 | 420 | 1,349 |
| 6 | 288 | 292 | 248 | 828 |
| 7 | 310 | 305 | 272 | 887 |
| 8 | 225 | 249 | 231 | 705 |

All 24 region×year cells are populated (minimum cell: 172 households for region 3, year 2017). No structural sparsity.

**Singles** (5,007 household × year-tag observations, derived from `reg_nuts1_k`):

| Region | year_tag=1 (2015) | year_tag=2 (2016) | year_tag=3 (2017) | Total |
|--------|-------------------|--------------------|-------------------|-------|
| 1 | 281 | 271 | 269 | 821 |
| 2 | 258 | 269 | 285 | 812 |
| 3 | 119 | 126 | 136 | 381 |
| 4 | 151 | 145 | 134 | 430 |
| 5 | 284 | 297 | 294 | 875 |
| 6 | 209 | 190 | 177 | 576 |
| 7 | 203 | 197 | 187 | 587 |
| 8 | 164 | 181 | 180 | 525 |

All 24 cells populated. The data has sufficient region support for identification under a correctly wired model.

---

## 8. Region-dummy variation by working / non-working alternatives

Region dummies are specified with `applies_to: "household"` — they are household-level attributes that do not vary across the 100 alternatives in a choice set. Their contribution to the market-opportunity index enters as `beta_E_drgn_k × reg_k × working_i`, where `working_i` is an alternative-specific binary indicator (0 or 1 for the employment state of that alternative). Under a correctly wired model, the household-level dummy `reg_k` is constant across all alternatives, but the product with `working_i` introduces alternative-level variation (distinction between employed and non-employed alternatives).

In the current estimation:

- **Couples**: `reg_k = 0` for all observations (NaN → fillna(0.0)). The product is zero regardless of `working_i`. No variation reaches the market-opportunity index.
- **Singles**: Region dummies are skipped by the `applies_to: "household"` guard before any variable access. The `working` interaction is never computed.

The `gsur` shifter (also present in the specification) is specified with `offer_only_vars: ["gsur"]` and no `applies_to` (defaults to `"both"`). In singles, `gsur` varies across the 100 alternatives within each choice set (1,105 of the 5,007 singles choice-sets show within-group variation), providing identification from the singles submodel. This confirms that the singles market-opportunity gradient computation is functioning correctly for non-`household` shifters.

---

## 9. Region-dummy wiring in pooled YAML

Excerpt from `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml` (region dummy block, representative for all seven):

```yaml
market_opportunity_shifters:
  - coef_name: beta_E_drgn2
    variable: reg_nuts1_2
    interaction: [working]
    applies_to: household

  - coef_name: beta_E_drgn3
    variable: reg_nuts1_3
    interaction: [working]
    applies_to: household

  # ... (reg_nuts1_4 through reg_nuts1_8 follow identical pattern)

  - coef_name: beta_E_y2015
    variable: year_2015_indicator
    interaction: [working]
    applies_to: household

  - coef_name: beta_E_y2017
    variable: year_2017_indicator
    interaction: [working]
    applies_to: household
```

The YAML wiring is correct in intent. The `applies_to: household` attribute is appropriate for household-level dummies that should shift the market-opportunity index uniformly across all employment alternatives. The variable names match the expected parquet column names. The wiring failure is not in the YAML.

---

## 10. Region-dummy wiring in parser output

The specification parser (`estimation_spec_parser.py`) reads the YAML and produces a list of market-opportunity shifter objects. For each shifter the parser extracts:

- `coef_name` — matched against the parameter vector
- `variable` — the attribute name expected on the precomputed data object (e.g., `reg2` after the precompute maps `reg_nuts1_2 → data.reg2`)
- `interaction` — list of interaction variable names (`["working"]`)
- `applies_to` — the routing tag (`"household"`)

The parser output is structurally correct. The `applies_to: "household"` tag reaches the engine as intended. The engine's routing logic for singles (`continue` at line 116–117 of `estimation_engine.py`) then correctly implements the YAML semantics: region dummies are not supposed to enter the singles market-opportunity index, and they do not. The routing for couples is also correct: `applies_to == "household"` directs the engine to use `data.working_male + data.working_female` as the interaction term (line 208). The wiring failure is not in the parser output.

---

## 11. Region-dummy wiring in extra_vars / precompute path

The `precompute_data_couples` function in `estimation_utils.py` contains the following branch at lines 1070–1088:

```python
# Create region dummies (region 1 = Île-de-France is reference) - household level
if "reg_nuts1_2" in df.columns:
    reg2 = df["reg_nuts1_2"].fillna(0.0).values
    reg3 = df["reg_nuts1_3"].fillna(0.0).values
    reg4 = df["reg_nuts1_4"].fillna(0.0).values
    reg5 = df["reg_nuts1_5"].fillna(0.0).values
    reg6 = df["reg_nuts1_6"].fillna(0.0).values
    reg7 = df["reg_nuts1_7"].fillna(0.0).values
    reg8 = df["reg_nuts1_8"].fillna(0.0).values
elif "drgn1" in df.columns:
    # Create dummies from drgn1 code
    reg2 = (drgn1 == 2).astype(float)
    reg3 = (drgn1 == 3).astype(float)
    reg4 = (drgn1 == 4).astype(float)
    reg5 = (drgn1 == 5).astype(float)
    reg6 = (drgn1 == 6).astype(float)
    reg7 = (drgn1 == 7).astype(float)
    reg8 = (drgn1 == 8).astype(float)
else:
    reg2 = reg3 = reg4 = reg5 = reg6 = reg7 = reg8 = np.zeros(n_obs)
```

The condition `"reg_nuts1_2" in df.columns` tests column-name membership in the DataFrame schema, which returns `True` for any column that was included in the schema at parquet creation time, regardless of whether the column contains any non-null values.

In the couples parquet, `reg_nuts1_2` is in the schema (the column exists) but has 743,800 / 743,800 values missing. Therefore:

1. `"reg_nuts1_2" in df.columns` evaluates to `True`.
2. The `if` branch is taken: `reg2 = df["reg_nuts1_2"].fillna(0.0).values`.
3. Since all values are NaN, `fillna(0.0)` produces an array of 743,800 zeros.
4. The `elif "drgn1" in df.columns` fallback at line 1078 is never reached.
5. `data.reg2` through `data.reg8` are set to all-zero arrays on the precomputed data object.

**This is the proximate cause of non-identification.**

The fix is to use value-presence rather than schema-presence in the guard condition. The corrected logic would be:

```python
if "reg_nuts1_2" in df.columns and df["reg_nuts1_2"].notna().any():
    # direct column path
elif "drgn1" in df.columns:
    # drgn1 fallback
```

or equivalently, to populate `reg_nuts1_k` from `drgn1` during the pooled P3a data-build step.

---

## 12. Whether region dummies reach the market-opportunity index

**Singles submodel** — region dummies do NOT reach the market-opportunity index.

`_compute_market_opportunity_singles` in `estimation_engine.py` iterates over YAML market-opportunity shifters. For each shifter, the routing guard at lines 116–117 is:

```python
if applies_to in {"cm", "cf", "household"}:
    continue
```

All seven region-dummy shifters have `applies_to = "household"`, so all seven are skipped with `continue`. The singles market-opportunity gradient is zero with respect to `beta_E_drgn2`–`beta_E_drgn8` for all parameter values.

This is correct YAML semantics: region dummies are household-level attributes and should not enter the singles market-opportunity index in the intended model. The guard is functioning as designed.

**Couples submodel** — region dummies are passed to the computation but contribute zero due to the NaN bug.

`_compute_market_opportunity_couples` reaches the `applies_to == "household"` branch for each region dummy. The contribution is:

```python
var_param = getattr(data, "reg2")          # = all-zeros array (743,800 × 1)
var_param = var_param * (data.working_male + data.working_female)  # 0 × anything = 0
log_market += theta["beta_E_drgn2"] * var_param                    # = 0 exactly
```

The `working_male + working_female` interaction is non-zero for many alternatives (employment states), but multiplying by the all-zero `data.reg2` makes every term exactly zero. The market-opportunity index receives zero contribution from all seven region dummies, regardless of parameter values.

**Joint LL gradient** — identically zero w.r.t. beta_E_drgn2–drgn8.

The gradient of the couples log-likelihood is `∂LL/∂beta_E_drgn_k = Σ_i (chosen_i − P_i) × reg_k × working_i`. Since `reg_k = 0` everywhere, this gradient is identically zero at all parameter values. Combined with the singles exclusion, the joint gradient is:

```
∂LL_joint / ∂ beta_E_drgn_k = 0   (k = 2, ..., 8)   for all theta
```

---

## 13. Whether beta_E_drgn2 through beta_E_drgn8 enter the gradient

**Result: No.** The joint gradient is identically zero for all seven region-dummy coefficients (see Section 12).

Confirmation from the solver: the Hessian diagonal entries for `beta_E_drgn2`–`beta_E_drgn8` are at machine-epsilon scale in all three starts:

| Parameter | start_1 se_hessian | start_2 se_hessian | start_3 se_hessian |
|-----------|--------------------|--------------------|---------------------|
| `beta_E_drgn2` | 3.239e-15 | 1.166e-15 | 1.845e-15 |
| `beta_E_drgn3` | 2.388e-15 | 7.201e-15 | 2.733e-15 |
| `beta_E_drgn4` | 4.853e-15 | 3.452e-15 | 1.478e-15 |
| `beta_E_drgn5` | 3.417e-16 | 3.177e-15 | 1.253e-15 |
| `beta_E_drgn6` | 5.946e-15 | 1.440e-15 | 2.406e-15 |
| `beta_E_drgn7` | 2.403e-15 | 8.511e-16 | 4.244e-15 |
| `beta_E_drgn8` | 1.983e-15 | 9.488e-16 | 1.589e-15 |

These values (≈ 10⁻¹⁵) are at double-precision machine epsilon for the Hessian — consistent with numerical noise around zero second derivatives. The Hessian-based SE values similarly reflect near-zero curvature. Region dummy parameters appear in the free_mask (`free=True`) because the machine-epsilon entries are strictly positive and pass the `≤ 0` threshold test, but they are not genuinely identified.

The Hessian condition number (PE6) across starts confirms near-singularity of the full Hessian due to these seven flat directions:

| Start | PE6 condition number |
|-------|---------------------|
| start_1 | 5.178e+24 |
| start_2 | 1.131e+25 |
| start_3 | 2.826e+25 |

These are 12–13 orders of magnitude above the near-singular threshold of 10¹².

---

## 14. Collinearity diagnostics

The design matrix analysed here is defined at the household×year_tag level (one row per unique choice situation), consisting of the market-opportunity shifters that would be active in the gradient if the data were correctly wired: region dummies (7), year indicators (2), and gsur (1) — 10 columns total.

**Couples design matrix (actual — as estimated)**:

The seven `reg_nuts1_k` columns are all-zero (NaN fillna) and `gsur` is also all-NaN in couples (fillna → 0). Only `year_2015_indicator` and `year_2017_indicator` are non-zero.

```
Shape: (7,438, 10)
Rank:  2 / 10
Singular values: [50.66, 47.91, 0., 0., 0., 0., 0., 0., 0., 0.]
Condition number: inf (8 of 10 singular values are zero)
```

The rank-2 actual design is not a collinearity result — it reflects degenerate (all-zero) inputs for eight of the ten columns. The two non-zero singular values correspond to the two year indicators that are properly populated.

**Couples design matrix (hypothetical — using drgn1 fallback as intended)**:

```
Shape: (7,438, 9)  [7 region dummies + 2 year indicators]
Rank:  9 / 9
Singular values: [56.12, 49.00, 36.72, 33.25, 29.31, 27.59, 26.10, 24.24, 17.57]
Condition number: 3.195
```

Full rank, well-conditioned. No structural collinearity between region dummies and year indicators.

**Singles design matrix (actual — as used)**:

```
Shape: (5,007, 10)  [7 region dummies + 2 year indicators + gsur]
Rank:  10 / 10
Condition number: 14.0
```

The singles data is fully ranked. Region dummies are non-zero and linearly independent of year indicators and gsur.

**Conclusion**: non-identification is entirely attributable to degenerate (all-zero) inputs in the couples precompute, not to structural collinearity.

---

## 15. Rank of region-plus-related design block

| Design matrix | Shape | Rank | Notes |
|---------------|-------|------|-------|
| Couples actual (reg_nuts1_k + year + gsur) | (7,438, 10) | **2 / 10** | 8 zero columns |
| Couples hypothetical (drgn1 dummies + year) | (7,438, 9) | **9 / 9** | Full rank |
| Singles actual (reg_nuts1_k + year + gsur) | (5,007, 10) | **10 / 10** | Full rank |

The VCV block restricted to the seven region-dummy parameters confirms the degenerate Hessian:

```
VCV drgn block eigenvalues (start_1):
  min = -1.734e-28
  max =  5.938e-28
```

These eigenvalues are at the scale of double-precision rounding error (≈ 10⁻²⁸), not at the scale of a genuine variance. The negative eigenvalue is floating-point noise around zero.

---

## 16. Condition number of region-plus-related design block

| Design | Condition number | Interpretation |
|--------|-----------------|----------------|
| Couples actual | ∞ (zero singular values) | Degenerate — zero columns |
| Couples hypothetical (drgn1) | **3.195** | Well-conditioned |
| Singles actual | **14.0** | Well-conditioned |

If the couples data were correctly populated from `drgn1`, the hypothetical condition number of 3.195 is far below any threshold of concern (typically 10³–10⁶ for near-collinearity). The region and year variables would be orthogonally identified.

The 3.195 figure arises because the 8-region NUTS-1 partition and the 3-year panel are both balanced and broadly uncorrelated at the household level: no region is exclusively observed in one year.

---

## 17. Correlation with GSUR

`gsur` enters the market-opportunity index for singles with `applies_to` defaulting to `"both"` (not `"household"`), so it is not skipped. In the singles submodel, `gsur` varies across alternatives within each choice set (1,105 of 5,007 singles choice-sets show within-group variation) and contributes genuine curvature to the singles LL. Its identification comes entirely from the singles submodel; couples `gsur` is all-NaN (fillna → 0) and contributes nothing.

In the singles submodel, region dummies are skipped by the `applies_to: "household"` guard and are not in the active gradient space. Therefore, the in-model correlation between `gsur` and region dummies in the singles likelihood is undefined (region dummies contribute zero gradient). In the hypothetical full-design matrix for singles (region + year + gsur), the design is full rank with condition number 14.0, indicating no problematic correlation.

`gsur` is identified: identical across all three starts to full precision (`beta_E_gsur = −1.198054`, `se_robust = 1.788e−01`, `t = −6.70`). Its identification is unaffected by the region-dummy bug.

---

## 18. Correlation with year indicators

Year indicators (`year_2015_indicator`, `year_2017_indicator`) are in the same structural category as region dummies: `applies_to: "household"`, `interaction: ["working"]`. They are skipped for singles by the same `applies_to: "household"` guard. In couples, their parquet columns are correctly populated (0 missing values), so `fillna(0.0)` does nothing — they survive as valid non-zero arrays and contribute genuine curvature to the couples LL.

**Year indicators are identified** despite sharing the `applies_to: "household"` guard for singles. Confirmation across all three starts:

| Start | `beta_E_y2015` | se_robust | `beta_E_y2017` | se_robust |
|-------|---------------|-----------|---------------|-----------|
| start_1 | 0.109717 | 2.532e-01 | 0.325530 | 2.773e-01 |
| start_2 | 0.109717 | 2.532e-01 | 0.325530 | 2.773e-01 |
| start_3 | 0.109717 | 2.532e-01 | 0.325530 | 2.773e-01 |

Identical to 6 decimal places. Year indicators are identified because their couples data column is valid; region dummies are not identified because their couples data column is all-NaN.

The hypothetical couples design (7 region dummies + 2 year indicators, derived from `drgn1`) has rank 9/9 and condition number 3.195, confirming no collinearity between region and year effects.

---

## 19. Correlation with occupation variables

Occupation dummies (`beta_occ_2_cm`, `beta_occ_3_cm`, `beta_occ_4_cm`, and singles equivalents) are specified as alternative-level characteristics that shift log-probability directly, not through the market-opportunity index. They do not interact with household-level region dummies in the likelihood gradient.

The occupation dummies are identified: across all three starts they are identical to 6 decimal places (consistent with all genuinely identified parameters). No collinearity concern between occupation and region variables exists because they operate in structurally separate parts of the likelihood.

Under a correctly wired model, the region-dummy contribution (`beta_E_drgn_k × reg_k × working`) affects all employment alternatives uniformly for a household in region k, while occupation dummies select among employment alternatives for a given household. These are orthogonal identification channels.

---

## 20. Flat-likelihood confirmation from existing starts

Three solver runs were completed from independent starting points. The joint log-likelihoods are:

| Start | LL singles male | LL singles female | LL couples | LL joint |
|-------|----------------|-------------------|------------|----------|
| start_1 | −19,093.5404 | −19,093.5404 | −19,093.5404 | **−57,280.6213** |
| start_2 | −19,093.5404 | −19,093.5404 | −19,093.5404 | **−57,280.6213** |
| start_3 | −19,093.5404 | −19,093.5404 | −19,093.5404 | **−57,280.6213** |

The joint LL is identical across all three starts to four decimal places. The solver has found the same optimum three times, as expected when the LL is flat in some directions. The convergence is genuine — not a premature termination.

The identifying parameters are identical to 6 decimal places across starts:

| Parameter | start_1 | start_2 | start_3 |
|-----------|---------|---------|---------|
| `beta_E_gsur` | −1.198054 | −1.198054 | −1.198054 |
| `beta_E_y2015` | 0.109717 | 0.109717 | 0.109717 |
| `beta_E_y2017` | 0.325530 | 0.325530 | 0.325530 |

The non-identified region dummies converge to arbitrary values depending on initialisation:

| Parameter | start_1 | start_2 | start_3 |
|-----------|---------|---------|---------|
| `beta_E_drgn2` | +0.801342 | +0.000000 | +0.710103 |
| `beta_E_drgn3` | +0.656401 | +0.000000 | +0.587259 |
| `beta_E_drgn4` | +1.562552 | +0.000000 | +1.599162 |
| `beta_E_drgn5` | +0.772496 | +0.000000 | +0.821448 |
| `beta_E_drgn6` | +0.766517 | +0.000000 | +0.860019 |
| `beta_E_drgn7` | +0.640451 | +0.000000 | +0.605616 |
| `beta_E_drgn8` | +0.463141 | +0.000000 | +0.437233 |

Start 2 initialised region dummies at zero and the solver left them there. Starts 1 and 3 initialised at different values and converged to different non-zero points, all with the same LL. This is the canonical signature of exact non-identification: any value in the direction of zero gradient achieves the same likelihood.

---

## 21. Direct LL-invariance check, if possible without re-estimation

A direct LL-invariance check (evaluating the likelihood at deliberately different `beta_E_drgn_k` values and confirming LL does not change) was not run as a standalone computation because the three-start experiment already provides conclusive evidence: starts 1 and 3 converged to substantially different region-dummy parameters (+0.80 vs +0.71 for drgn2, for example) while producing identical joint LL values (−57,280.6213). This constitutes an empirical LL-invariance demonstration without requiring additional solver calls.

The algebraic proof of invariance follows directly from the gradient calculation in Section 12: if the gradient ∂LL/∂beta_E_drgn_k = 0 for all theta, then LL(theta + Δ × e_k) = LL(theta) for any scalar Δ, where e_k is the k-th unit vector. The zero gradient is not a local property — it holds everywhere in parameter space because `data.reg_k = 0` everywhere.

---

## 22. Cause classification

**Classification: B/DEGENERATE_OR_MISWIRED_COLUMNS**

The non-identification of `beta_E_drgn2`–`beta_E_drgn8` is caused by **degenerate input columns** in the couples split file. The specific failure chain is:

1. The pooled P3a data-build step did not populate `reg_nuts1_2`–`reg_nuts1_8` in the couples parquet. These columns exist in the schema but contain 743,800 / 743,800 NaN values.

2. `estimation_utils.py:precompute_data_couples` (line 1070) tests `"reg_nuts1_2" in df.columns` — a schema-presence test, not a value-presence test. The condition is `True` despite all values being NaN.

3. The `fillna(0.0)` branch is taken. Arrays `data.reg2` through `data.reg8` are set to all zeros.

4. The `elif "drgn1"` fallback (line 1078) is never reached, despite `drgn1` being a valid column with 8 unique non-null region codes.

5. In `_compute_market_opportunity_couples`, the contribution is `beta_E_drgn_k × 0 × working = 0` exactly. The gradient is zero.

6. In `_compute_market_opportunity_singles`, a separate `applies_to: "household"` guard (lines 116–117) skips region dummies entirely. No backup identification pathway exists through the singles submodel.

7. The joint LL is exactly flat in the seven region-dummy directions.

This classification excludes:

- **A/INTACT_AND_WIRED_BUT_COLLINEAR_OR_REDUNDANT**: excluded because the hypothetical design (using `drgn1`) has rank 9/9 and condition number 3.195 — no structural collinearity. The problem is upstream of the estimation: zero columns enter the likelihood.
- **C/INCONCLUSIVE**: excluded because the data and code inspection is definitive. The failure mode is unambiguous and fully traceable.

---

## 23. Recommended next gate

**Gate: Pooled data-build fix — populate `reg_nuts1_k` in couples split from `drgn1`.**

The minimum fix is to modify the pooled P3a data-build script to populate `reg_nuts1_2`–`reg_nuts1_8` in the couples parquet from the `drgn1` column. The `drgn1` column is present and valid (743,800 non-missing values, 8 unique region codes, all 8×3 region×year cells occupied). The conversion is:

```python
for k in range(2, 9):
    df_couples[f"reg_nuts1_{k}"] = (df_couples["drgn1"] == k).astype(float)
```

An alternative fix — adding a value-presence guard in `estimation_utils.py:precompute_data_couples` — would also work:

```python
if "reg_nuts1_2" in df.columns and df["reg_nuts1_2"].notna().any():
    # direct column path
elif "drgn1" in df.columns:
    # drgn1 fallback (currently unreachable)
```

The data-build fix is preferred because it makes the data self-describing, removes the dependency on fallback logic, and allows the parquet files to be used by any downstream tool without the wiring subtlety.

**Re-estimation is required after the fix.** The current P3a results contain seven non-identified region dummy parameters. They must not be reported or used for inference. M1-clean 2016 remains the active JMP baseline; this diagnostic pertains to P3a pooled only.

No SA2 should be issued until re-estimation is complete and multi-start convergence is confirmed for the corrected model.

---

## 24. What was not executed

The following actions were explicitly NOT taken during this diagnostic:

- **No solver run**: The GAMS/CONOPT solver was not called. No `gamspy_estimation_vectorized.py` or `enh_RURO_estimate_FR.py` invocations were made.
- **No re-estimation**: No new estimation results were generated.
- **No data modification**: The parquet files were read-only. No columns were added, modified, or filled.
- **No specification modification**: The YAML file was read-only. No parameter definitions or bounds were changed.
- **No welfare computation**: No household utility or welfare calculations were performed.
- **No SA2 verdict**: No formal sufficiency assessment was issued.
- **No canonical promotion**: No model or output set was promoted to canonical or baseline status.
- **No M1-clean substitution**: M1-clean 2016 was not referenced or modified. It remains the active baseline.

---

## 25. Required final statements

No solver was run. No re-estimation was performed. No welfare was computed. No SA2 verdict was issued. No canonical promotion was performed. M1-clean 2016 remains the active JMP baseline.