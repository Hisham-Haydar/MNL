# JMP Pooled P3a — Region-Dummy Non-Identification Diagnostic v2

**Model**: RURO occupation-opportunity P3a, pooled 2015–2017  
**Specification**: `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml`  
**Date**: 2026-05-21  
**Status**: Post-repair read-only diagnostic. No estimation run.  
**Prior diagnostic**: `Results/P3a/pooled_P3a/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v1.md`  
**Repair authorization**: `docs/archive/2026-05-26_round2_chain_compression/replaced_by_clean_corrected/JMP_pooled_P3a_region_dummy_repair_authorization_v1.md`  
**Repair report**: `docs/archive/2026-05-26_round2_chain_compression/replaced_by_clean_corrected/JMP_pooled_P3a_region_dummy_repair_report_v1.md`

---

## 1. Diagnostic verdict

**The cause-B defect has been resolved. Region dummies are now populated, wired, and identifiable on the regenerated data.**

The couples split `reg_nuts1_2`–`reg_nuts1_8` are now valid binary non-NaN columns derived exactly from `drgn1`. The precompute produces non-zero `data.reg2`–`data.reg8` arrays (134,900 / 56,000 / 66,300 / 134,900 / 82,800 / 88,700 / 70,500 non-zero rows respectively). The product `reg_k × (working_male + working_female)` — the contribution of each region dummy to the couples market-opportunity index — is non-zero for 55,437–133,537 rows per region. The joint-LL gradient with respect to `beta_E_drgn_k` (k=2,…,8) is no longer identically zero; these parameters now receive genuine couple-level variation through the market-opportunity channel.

The post-repair couples design matrix (7 region dummies + 2 year indicators, 7,438 household×year rows) has **rank 9/9** and condition number **3.195**, matching the hypothetical design predicted by diagnostic v1. No collinearity was introduced by the repair. The max pairwise correlation between region dummies and year indicators is 0.018; the max cross-correlation between region dummies is 0.22 (mechanically expected for 7 dummies from an 8-category partition).

**Classification change**: the pre-repair cause was **B/DEGENERATE_OR_MISWIRED_COLUMNS** (the couples `reg_nuts1_k` columns were entirely NaN, producing zero arrays via `fillna(0.0)`). This cause has been **removed** by R1 (data-build fix) and R2 (precompute value-presence guard). The post-repair classification is **defect resolved; region dummies identifiable**.

> **Important**: this diagnostic confirms the region dummies are now *identifiable* — i.e., the gradient is non-zero and the design is full-rank. Whether they are statistically significant once re-estimated on the corrected data is a separate, empirical question that this read-only diagnostic does not and cannot answer. Re-estimation is not authorized here and has not been run.

---

## 2. Authorization scope

Read-only diagnostic on the regenerated split stem. No solver run. No re-estimation. No data modification beyond the R1/R2 repair already applied and documented in the repair report. No welfare, no SA2, no canonical promotion, no M1-clean displacement.

---

## 3. Files inspected

| File | Role |
|------|------|
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet` | Regenerated couples split (post-repair) |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__singles.parquet` | Singles split (preserved, unchanged) |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json` | Regenerated metadata sidecar |
| `scripts/enhanced/estimation_utils.py` | Precompute with R2 value-presence guard applied |
| `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml` | Pooled P3a specification (unchanged) |
| `Data/processed/fr/pooled/archive/fr_p3a_gsurv2_estimation_ready__couples_defective_20260521.parquet` | Archived defective couples split |

---

## 4. Region-dummy column status: post-repair couples split

| Column | Missing / Total | Non-null unique | Non-zero rows | Pre-repair status |
|--------|----------------|-----------------|---------------|-------------------|
| `reg_nuts1_2` | 0 / 743,800 | 2 | 134,900 | all-NaN |
| `reg_nuts1_3` | 0 / 743,800 | 2 | 56,000 | all-NaN |
| `reg_nuts1_4` | 0 / 743,800 | 2 | 66,300 | all-NaN |
| `reg_nuts1_5` | 0 / 743,800 | 2 | 134,900 | all-NaN |
| `reg_nuts1_6` | 0 / 743,800 | 2 | 82,800 | all-NaN |
| `reg_nuts1_7` | 0 / 743,800 | 2 | 88,700 | all-NaN |
| `reg_nuts1_8` | 0 / 743,800 | 2 | 70,500 | all-NaN |
| `drgn1` | 0 / 743,800 | 8 | — | valid (unchanged) |

All seven region-dummy columns are now valid binary float64 arrays. `reg_nuts1_k == 1[drgn1 == k]` exactly for all rows. Region 1 (Île-de-France) remains the omitted reference (all seven dummies are 0 for `drgn1 == 1` rows).

---

## 5. Region-dummy column status: singles split (unchanged)

| Column | Missing / Total | Non-zero rows |
|--------|----------------|---------------|
| `reg_nuts1_2` | 0 / 500,700 | 81,200 |
| `reg_nuts1_3` | 0 / 500,700 | 38,100 |
| `reg_nuts1_4` | 0 / 500,700 | 43,000 |
| `reg_nuts1_5` | 0 / 500,700 | 87,500 |
| `reg_nuts1_6` | 0 / 500,700 | 57,600 |
| `reg_nuts1_7` | 0 / 500,700 | 58,700 |
| `reg_nuts1_8` | 0 / 500,700 | 52,500 |

Singles region dummies were valid in the pre-repair split and remain valid and unchanged. Note: the singles `applies_to: "household"` guard in `_compute_market_opportunity_singles` means these columns still do not enter the singles likelihood; region identification continues to come through the couples submodel only. This is correct by design.

---

## 6. Region support by year_tag: post-repair

**Couples** (7,438 household × year-tag observations):

| Region | year_tag=1 (2015) | year_tag=2 (2016) | year_tag=3 (2017) | Total |
|--------|-------------------|--------------------|-------------------|-------|
| 1 (ref) | 378 | 383 | 336 | 1,097 |
| 2 | 484 | 446 | 419 | 1,349 |
| 3 | 197 | 191 | 172 | 560 |
| 4 | 239 | 227 | 197 | 663 |
| 5 | 445 | 484 | 420 | 1,349 |
| 6 | 288 | 292 | 248 | 828 |
| 7 | 310 | 305 | 272 | 887 |
| 8 | 225 | 249 | 231 | 705 |

All 24 region×year cells populated. Minimum cell: 172 (region 3, year 2017). The repair preserved the support structure exactly as `drgn1` defined it — identical to the hypothetical design reported in diagnostic v1.

---

## 7. Wiring verification: region dummies in precompute

`precompute_data_couples` now correctly takes the **direct `reg_nuts1_*` path** on the regenerated split (R2 value-presence guard: all columns present, non-missing, non-degenerate). Arrays are set to the column values directly:

```
data.reg2: 134,900 / 743,800 non-zero
data.reg3:  56,000 / 743,800 non-zero
data.reg4:  66,300 / 743,800 non-zero
data.reg5: 134,900 / 743,800 non-zero
data.reg6:  82,800 / 743,800 non-zero
data.reg7:  88,700 / 743,800 non-zero
data.reg8:  70,500 / 743,800 non-zero
```

---

## 8. Market-opportunity index contribution: post-repair

In `_compute_market_opportunity_couples`, the region-dummy contribution is `beta_E_drgn_k × data.reg_k × (data.working_male + data.working_female)`. Post-repair, the product `reg_k × (working_male + working_female)` is non-zero for:

| Region dummy | Non-zero `reg_k × (wm+wf)` rows | Fraction of 743,800 |
|---|---|---|
| `reg2` | 133,537 | 18.0% |
| `reg3` | 55,437 | 7.5% |
| `reg4` | 65,607 | 8.8% |
| `reg5` | 133,556 | 18.0% |
| `reg6` | 81,997 | 11.0% |
| `reg7` | 87,774 | 11.8% |
| `reg8` | 69,771 | 9.4% |

These are the rows at which `beta_E_drgn_k` will receive a non-zero score contribution and appear in the gradient. The likelihood is no longer flat in these directions. The gradient `∂LL_couples / ∂ beta_E_drgn_k` is now non-zero at generic parameter values.

---

## 9. Design rank and condition: post-repair

| Design matrix | Shape | Rank | Condition | Notes |
|---|---|---|---|---|
| Couples actual, post-repair (reg + year) | (7,438, 9) | **9 / 9** | **3.195** | Full rank |
| Couples actual, post-repair (reg + year + gsur) | — | — | — | gsur is all-NaN in couples; excluded |
| Couples actual, pre-repair (reg + year + gsur) | (7,438, 10) | 2 / 10 | ∞ | 8 zero columns |
| Singles actual (reg + year + gsur) | (5,007, 10) | 10 / 10 | 14.01 | Unchanged |

The post-repair couples design is full rank with condition number 3.195 — the well-conditioned structure predicted by diagnostic v1 for the correct `drgn1`-derived design. The singular values are:

```
[56.12, 49.00, 36.72, 33.25, 29.31, 27.59, 26.10, 24.24, 17.57]
```

All positive and of similar magnitude. No near-zero singular values; no structural degeneracy.

---

## 10. No new collinearity introduced

Pairwise correlations between region dummies and year indicators (couples, post-repair):

| | year_2015 | year_2017 |
|---|---|---|
| reg_nuts1_2 | 0.0137 | 0.0021 |
| reg_nuts1_3 | 0.0041 | −0.0009 |
| reg_nuts1_4 | 0.0102 | −0.0077 |
| reg_nuts1_5 | −0.0150 | 0.0028 |
| reg_nuts1_6 | 0.0021 | −0.0069 |
| reg_nuts1_7 | 0.0035 | −0.0015 |
| reg_nuts1_8 | −0.0176 | 0.0134 |

Maximum |correlation| between any region dummy and any year indicator: **0.018**.  
Maximum |correlation| between any two region dummies: **0.22** (expected for orthogonal dummies from an 8-category partition; the omitted reference causes small mechanically-induced negative correlations).

No collinearity problem. H6 (new collinearity introduced) did not fire.

---

## 11. Cause classification: post-repair

**Pre-repair**: **B/DEGENERATE_OR_MISWIRED_COLUMNS** — couples `reg_nuts1_k` columns present in schema but entirely NaN; precompute took `fillna(0.0)` branch; seven all-zero arrays; gradient identically zero; flat LL.

**Post-repair**: **Defect resolved. Region dummies are now wired and identifiable.**

The two-link cause has been repaired:
- **Link 1 (data build)**: `reg_nuts1_2`–`reg_nuts1_8` now derived from `drgn1` in the couples split when the existing columns are absent or all-NaN (R1 repair in `prepare_pooled_estimation_ready.py`).
- **Link 2 (precompute guard)**: `precompute_data_couples` now uses a value-presence test (`notna().any()` and `nunique() > 1` after `fillna(0)`) before taking the direct `reg_nuts1_*` path; falls back to `drgn1` if the direct columns are degenerate; raises `ValueError` if neither source is usable (R2 repair in `estimation_utils.py`).

The post-repair design is full-rank (9/9) and well-conditioned (κ = 3.195). The gradient will be non-zero with respect to `beta_E_drgn2`–`beta_E_drgn8` at generic parameter values. The identifiability condition is satisfied by the data.

---

## 12. What this diagnostic does and does not establish

**Established** (no estimation required):
- The seven region-dummy columns in the couples split are now valid, binary, and non-degenerate.
- The precompute produces non-zero `data.reg2`–`data.reg8` arrays.
- The `beta_E_drgn_k × reg_k × (wm+wf)` contributions are non-zero for 7.5%–18% of couples rows per region.
- The couples design matrix is full-rank (9/9) and well-conditioned (κ = 3.195) with no collinearity between region and year effects.
- The original cause-B defect — zero gradient from all-NaN input columns — has been removed.

**Not established** (requires re-estimation, which is not authorized here):
- Whether `beta_E_drgn2`–`beta_E_drgn8` will be statistically significant in the corrected model.
- Whether the region opportunity dimension will be jointly identified in the Hessian sense (non-singular VCV sub-block) at the new optimum.
- Whether the corrected model will satisfy the SA2 region criteria (S4, S5).
- Whether the corrected estimates will be numerically stable across multiple starts.

These are empirical questions for a future re-estimation that requires its own authorization. The present diagnostic confirms that the data infrastructure now supports identification; it does not pre-judge the estimation outcome.

---

## 13. Required final statements

No solver was run. No re-estimation was performed. No welfare was computed. No SA2 verdict was issued. No canonical promotion was performed. M1-clean 2016 remains the active JMP baseline.

The region-dummy cause-B defect has been resolved on the regenerated data. The region dummies are now identifiable. Whether they are statistically significant requires re-estimation, which is a separate gate not authorized by this diagnostic.