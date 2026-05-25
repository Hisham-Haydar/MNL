# JMP Pooled P3a — Region-Dummy Repair Report v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

Authorization: `docs/JMP_pooled_P3a_region_dummy_repair_authorization_v1.md`  
Diagnostic that mandated this repair: `Results/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v1.md`  
Post-repair diagnostic: `Results/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v2.md`

---

## 1. Repair verdict

**PASS. Both repairs applied. Region dummies are now wired and identifiable on the regenerated data.**

| Repair | Status | Summary |
|--------|--------|---------|
| R1 — couples region-dummy data-build fix | **APPLIED** | `reg_nuts1_2`–`reg_nuts1_8` derived from `drgn1` in couples split; all 0 NaN, binary, non-zero |
| R2 — precompute value-presence guard | **APPLIED** | Direct path now requires non-missing non-degenerate values; `drgn1` fallback reachable; no-source case raises `ValueError` |

Validation results V1–V9: all **PASS** (see §10).  
Post-repair diagnostic: cause-B defect resolved; design rank 9/9, condition 3.195 (see §14).  
No halt conditions H1–H7 fired.

---

## 2. Authorization scope

This repair is authorized by `docs/JMP_pooled_P3a_region_dummy_repair_authorization_v1.md` (A1–A6). Authorized actions:

- **A1** R1: couples region-dummy data-build fix.
- **A2** R2: precompute value-presence guard.
- **A3** Regenerate and validate the estimation-ready split stem.
- **A4** Rerun the read-only region-dummy diagnostic (v2).
- **A5** No preflight rerun needed (column set and schema unchanged; see §15).
- **A6** Write this repair report.

Not authorized (and not performed): solver run, re-estimation, welfare, SA2, canonical promotion, no-region design, specification modification, M1-clean displacement.

---

## 3. Files inspected

| File | Role |
|------|------|
| `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet` | Source unified parquet (read-only) |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet` | Defective couples split (read, then replaced) |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__singles.parquet` | Singles split (read; preserved unchanged) |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json` | Metadata sidecar (replaced with updated version) |
| `scripts/maintenance/prepare_pooled_estimation_ready.py` | Split-stem build script (modified: R1) |
| `scripts/enhanced/estimation_utils.py` | Precompute functions (modified: R2) |
| `docs/JMP_pooled_P3a_region_dummy_repair_authorization_v1.md` | Authorization (read-only reference) |
| `Results/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v1.md` | Prior diagnostic (read-only reference) |

Diagnostic confirmed (read-only): unified parquet couples rows have valid `drgn1` (743,800 non-missing, 8 unique codes) and all-NaN `reg_nuts1_2`–`reg_nuts1_8` — establishing that R1 can derive the correct dummies from `drgn1`.

---

## 4. Files archived

Before regeneration, the existing split-stem files were copied to:

| Archived path | Original path | Notes |
|---|---|---|
| `Data/processed/fr/pooled/archive/fr_p3a_gsurv2_estimation_ready__couples_defective_20260521.parquet` | `.../__couples.parquet` | Defective couples split (all-NaN region dummies) |
| `Data/processed/fr/pooled/archive/fr_p3a_gsurv2_estimation_ready__singles_20260521.parquet` | `.../__singles.parquet` | Pre-repair singles split (unchanged content; archived for full stem provenance) |
| `Data/processed/fr/pooled/archive/fr_p3a_gsurv2_estimation_ready__mnlmeta_20260521.json` | `.../__mnlmeta.json` | Pre-repair metadata sidecar |

File sizes: couples 117 MB, singles 67 MB, meta 1 KB. Archive path: `Data/processed/fr/pooled/archive/`.

---

## 5. Files modified

| File | Change |
|------|--------|
| `scripts/maintenance/prepare_pooled_estimation_ready.py` | Added `derive_couples_region_dummies()` (R1 repair function) and `validate_couples_region_dummies()` (V1/V2 validation); inserted R1 call after year-indicator derivation; inserted V1/V2 check before conservation validation; added `region_dummy_repair` note to `build_mnlmeta()` output |
| `scripts/enhanced/estimation_utils.py` | Replaced schema-presence test (`if "reg_nuts1_2" in df.columns`) with R2 value-presence guard: direct path requires all columns present AND `notna().any()` AND `nunique() > 1` after `fillna(0)`; drgn1 fallback now reachable when direct columns are absent/all-NaN/all-zero; no-source case raises `ValueError` |

---

## 6. Files created

| File | Notes |
|------|-------|
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet` | Regenerated couples split with valid `reg_nuts1_2`–`reg_nuts1_8` (743,800 rows, 148 cols) |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__singles.parquet` | Regenerated singles split (preserved content; 500,700 rows, 148 cols) |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json` | Regenerated metadata with `region_dummy_repair` note |
| `Results/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v2.md` | Post-repair diagnostic |
| `docs/JMP_pooled_P3a_region_dummy_repair_report_v1.md` | This document |

The singles split was regenerated from the same unified source as part of the normal build process; its content is identical to the pre-repair version (same source rows, same derivations). Regenerating it together with the couples split ensures the two files derive from the same build run and the metadata row counts are consistent.

---

## 7. R1 couples region-dummy data-build fix

**Derivation rule** (implemented in `derive_couples_region_dummies()` in `prepare_pooled_estimation_ready.py`):

```python
for k in range(2, 9):
    df_couples[f"reg_nuts1_{k}"] = (df_couples["drgn1"] == k).astype(float)
```

Region 1 (Île-de-France) is the omitted reference and receives no dummy.

**Guard**: the function fires only when `reg_nuts1_2` through `reg_nuts1_8` are absent OR all-NaN OR all-zero in the couples split. Specifically:

```python
col_present = all(c in df_couples.columns for c in _reg_cols)
if col_present:
    any_valid = any(df_couples[c].notna().any() for c in _reg_cols)
    any_nondegenerate = any(df_couples[c].fillna(0).nunique() > 1 for c in _reg_cols)
    if any_valid and any_nondegenerate:
        # already valid — skip repair
        return df_couples
```

The guard does not overwrite already-valid columns. If `drgn1` is absent or all-NaN, the function raises `ValueError` (halt condition H1) rather than silently continuing.

**Resulting couples region support** (all 24 region×year cells populated):

| Region | year_tag=1 (2015) | year_tag=2 (2016) | year_tag=3 (2017) | Total rows (×100 alts) |
|--------|---|---|---|---|
| 1 (ref) | 378 | 383 | 336 | 109,700 |
| 2 | 484 | 446 | 419 | 134,900 |
| 3 | 197 | 191 | 172 | 56,000 |
| 4 | 239 | 227 | 197 | 66,300 |
| 5 | 445 | 484 | 420 | 134,900 |
| 6 | 288 | 292 | 248 | 82,800 |
| 7 | 310 | 305 | 272 | 88,700 |
| 8 | 225 | 249 | 231 | 70,500 |

Minimum cell: 172 households (region 3, year 2017). All cells positive.

---

## 8. R2 precompute value-presence guard

**Guard logic** (implemented in `precompute_data_couples` in `estimation_utils.py`, replacing lines 1070–1088):

```python
_reg_direct_cols = [f"reg_nuts1_{k}" for k in range(2, 9)]
_reg_direct_usable = (
    all(c in df.columns for c in _reg_direct_cols)          # all present
    and any(df[c].notna().any() for c in _reg_direct_cols)  # at least one non-NaN
    and any(df[c].fillna(0).nunique() > 1 for c in _reg_direct_cols)  # at least one non-degenerate
)
if _reg_direct_usable:
    # direct reg_nuts1_* path
    reg2 = df["reg_nuts1_2"].fillna(0.0).values
    ...
elif "drgn1" in df.columns:
    # drgn1 fallback — now reachable when direct columns are absent, all-NaN, or all-zero
    reg2 = (drgn1 == 2).astype(float)
    ...
else:
    raise ValueError(
        "precompute_data_couples: no usable region source. "
        "reg_nuts1_2..8 are absent/all-NaN/all-zero AND drgn1 is not available."
    )
```

**Confirmed behaviour**:
- Direct path taken when `reg_nuts1_*` are valid (post-repair production data). ✓
- drgn1 fallback taken when `reg_nuts1_*` are synthetic all-NaN but drgn1 is present. ✓ (smoke-test confirmed)
- `ValueError` raised when both sources are absent. ✓ (smoke-test confirmed)

**Defence-in-depth**: R2 makes R1 robust. Even if a future build again writes empty `reg_nuts1_*` columns (as occurred in the original P3a build), the precompute will reach the `drgn1` fallback rather than silently zeroing the region block. With R1 applied, the direct path is always valid on the production parquet; R2 is the guard that prevents silent recurrence on any future build that may repeat the original defect.

---

## 9. Singles validation

The singles split was preserved and regenerated from the same source without content change. Post-repair checks:

| Check | Result |
|-------|--------|
| `reg_nuts1_2`–`reg_nuts1_8` non-NaN | PASS (0 missing for all 7 columns) |
| Binary values | PASS (all in {0, 1}) |
| Non-degenerate | PASS (2 unique values per column) |
| Row count | PASS (500,700 rows) |
| Year indicators correct | PASS |
| Cluster key `cluster_id == idorighh` | PASS |
| `ils_dispy_real` present and non-null | PASS |

Singles non-zero counts per region dummy: reg_nuts1_2=81,200; reg_nuts1_3=38,100; reg_nuts1_4=43,000; reg_nuts1_5=87,500; reg_nuts1_6=57,600; reg_nuts1_7=58,700; reg_nuts1_8=52,500.

Note: the `applies_to: "household"` guard in `_compute_market_opportunity_singles` means these valid columns are still correctly skipped for singles. This is by design; region identification enters only through the couples market-opportunity index.

---

## 10. Couples validation

All V1–V9 checks pass on the regenerated couples split.

| Check | Result | Detail |
|-------|--------|--------|
| **V1** Couples reg columns present, zero NaN, binary, non-zero | **PASS** | All 7 columns: 0 missing; values in {0,1}; 56,000–134,900 ones each |
| **V2** `reg_nuts1_k == 1[drgn1==k]` for all k | **PASS** | Zero mismatch rows for all 7 columns; all dummies zero for `drgn1==1` rows |
| **V3** Singles region dummies valid (unchanged) | **PASS** | All 7 columns: 0 missing, 2 unique values |
| **V4** Conservation: rows, HH-years, clusters | **PASS** | singles=500,700; couples=743,800; total=1,244,500; HH-years=12,445; clusters=9,657 |
| **V5** Cluster key and income routing | **PASS** | `cluster_id==idorighh` on both; singles `ils_dispy_real`; couples `ils_dispy_male/female`; couples `c_norm` present and non-null |
| **V6** Year indicators preserved | **PASS** | singles 2015=166,900; 2017=166,200; couples 2015=256,600; 2017=229,500; zero mismatch with `year_tag` |
| **V7** Metadata sidecar present, row counts correct, R1 note present | **PASS** | `region_dummy_repair.repair=R1` recorded |
| **V8** Precompute produces non-zero `data.reg2`–`reg8`; fallback works; no-source errors | **PASS** (3/3 sub-tests) | Direct path: 56,000–134,900 non-zero; drgn1 fallback: same; no-source: ValueError raised |
| **V9** Region support by `year_tag`: all 24 cells populated | **PASS** | Minimum cell: 172 households |

---

## 11. drgn1-to-region-dummy equality check

Exact equality verified row-by-row for the full 743,800-row couples split:

```
reg_nuts1_2 == 1[drgn1==2]:  0 mismatches  PASS
reg_nuts1_3 == 1[drgn1==3]:  0 mismatches  PASS
reg_nuts1_4 == 1[drgn1==4]:  0 mismatches  PASS
reg_nuts1_5 == 1[drgn1==5]:  0 mismatches  PASS
reg_nuts1_6 == 1[drgn1==6]:  0 mismatches  PASS
reg_nuts1_7 == 1[drgn1==7]:  0 mismatches  PASS
reg_nuts1_8 == 1[drgn1==8]:  0 mismatches  PASS
All dummies zero for drgn1==1 rows:  PASS
```

The partition is exact and exhaustive: every couples row is assigned to exactly one region (region 1 through 8), with region 1 as the omitted reference (all seven dummies zero) and each remaining region coded as a binary indicator.

---

## 12. Precompute smoke test

Three sub-tests run on the post-repair `precompute_data_couples`:

**Sub-test 1 — real repaired data (direct path)**: `precompute_data_couples(df_c, meta)` on the regenerated couples split. Result: `data.reg2`–`data.reg8` all non-zero, consistent with column values.

```
data.reg2: 134,900 / 743,800 non-zero  PASS
data.reg3:  56,000 / 743,800 non-zero  PASS
data.reg4:  66,300 / 743,800 non-zero  PASS
data.reg5: 134,900 / 743,800 non-zero  PASS
data.reg6:  82,800 / 743,800 non-zero  PASS
data.reg7:  88,700 / 743,800 non-zero  PASS
data.reg8:  70,500 / 743,800 non-zero  PASS
```

**Sub-test 2 — synthetic all-NaN `reg_nuts1_*` with valid `drgn1` (fallback)**: Replaced all `reg_nuts1_k` with NaN; kept `drgn1`. Precompute logs warning and falls back to `drgn1`; `data.reg2`–`data.reg8` identical to sub-test 1. PASS.

**Sub-test 3 — all-NaN `reg_nuts1_*` AND `drgn1` removed (error)**: Dropped both sources. Precompute raised `ValueError: precompute_data_couples: no usable region source…`. PASS.

---

## 13. Region-dummy gradient-relevance check

The product `data.reg_k × (data.working_male + data.working_female)` — the quantity that multiplies `beta_E_drgn_k` in the market-opportunity index for couples — is non-zero for the following row counts:

| Parameter | `reg_k × (wm + wf)` non-zero rows | Fraction of 743,800 |
|---|---|---|
| `beta_E_drgn2` | 133,537 | 18.0% |
| `beta_E_drgn3` | 55,437 | 7.5% |
| `beta_E_drgn4` | 65,607 | 8.8% |
| `beta_E_drgn5` | 133,556 | 18.0% |
| `beta_E_drgn6` | 81,997 | 11.0% |
| `beta_E_drgn7` | 87,774 | 11.8% |
| `beta_E_drgn8` | 69,771 | 9.4% |

The non-zero count is slightly less than the non-zero `data.reg_k` count because `working_male + working_female = 0` for alternatives where neither partner is employed; those rows (non-employment alternatives in each choice set) contribute zero regardless of region. This is correct behaviour — region dummies affect market opportunity only for the employed alternatives, exactly as the YAML specification intends.

Pre-repair, all seven of these products were identically zero. Post-repair, each beta_E_drgn_k receives gradient signal from 55,437–133,537 rows per parameter per likelihood evaluation.

---

## 14. Post-repair diagnostic result

The read-only region-dummy diagnostic was rerun on the regenerated stem and saved as `Results/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v2.md`.

**Post-repair classification: defect resolved; region dummies identifiable.**

Key findings from diagnostic v2:

| Metric | Pre-repair (v1) | Post-repair (v2) |
|--------|----------------|-----------------|
| Couples `reg_nuts1_2`–`reg_nuts1_8` NaN status | all-NaN (743,800/743,800) | 0 NaN |
| Precompute path taken | `fillna(0.0)` (direct, degenerate) | direct `reg_nuts1_*` (valid) |
| `data.reg2`–`data.reg8` | all-zero | non-zero (55,437–134,900 rows each) |
| `beta_E_drgn_k × reg_k × (wm+wf)` non-zero rows | 0 | 55,437–133,537 per parameter |
| Couples design rank (reg + year) | 2/10 (8 zero cols) | **9/9** |
| Couples design condition | ∞ | **3.195** |
| Cause classification | B/DEGENERATE_OR_MISWIRED_COLUMNS | **Defect resolved; identifiable** |

The diagnostic v2 explicitly notes that whether the region dummies will be statistically significant in the re-estimated model is a separate, empirical question that requires re-estimation (not authorized by this repair).

---

## 15. Preflight result, if rerun

A full preflight rerun was **not required**. The column set of the regenerated couples split is unchanged from the defective split (148 columns; the `reg_nuts1_2`–`reg_nuts1_8` columns existed in the schema before; only their values changed from NaN to valid binary floats). No new columns were added; no columns were removed; no schema incompatibility was introduced.

A targeted load/precompute confirmation (V7, V8 above) was run instead, per the authorization (A5):
- V7: loader accepted the regenerated stem.
- V8: `precompute_data_couples` produces non-zero region arrays on the real data.

This constitutes the preflight equivalence check for the changed component. No estimator CLI or smoke-test interface was called against the GAMS/GAMSPy solver.

---

## 16. What was not executed

| Action | Status |
|--------|--------|
| Solver run | NOT executed |
| Re-estimation of pooled P3a | NOT executed |
| Welfare computation | NOT executed |
| SA2 verdict | NOT issued |
| Canonical promotion of any output | NOT performed |
| No-region design adopted or designed | NOT performed |
| Specification (YAML) modification | NOT performed |
| M1-clean 2016 displacement | NOT performed |
| Any modification beyond R1, R2, and stem regeneration | NOT performed |

---

## 17. Whether re-estimation is now ready for authorization

The corrected data is ready. The pre-conditions for a re-estimation authorization are met:
- The couples `reg_nuts1_2`–`reg_nuts1_8` columns are now valid, binary, and wired into the couples market-opportunity index.
- The precompute produces non-zero region arrays (V8 confirmed).
- The design is full-rank with condition 3.195 (no structural identification problem).
- V1–V9 all pass.
- The diagnostic v2 confirms cause-B defect resolved.

**However, re-estimation is NOT authorized by this memo.** A separate re-estimation authorization is required before any solver is run. That authorization is the next gate.

---

## 18. Whether welfare computation is authorized

**No.** Welfare computation is not authorized. It remains gated behind an accepted SA2 verdict on a re-estimated, corrected pooled P3a model.

---

## 19. Whether M1-clean remains active

**Yes.** M1-clean 2016 remains the active JMP baseline, displaced only by a future SA2 verdict explicitly promoting an identified pooled specification. The present repair does not change this.

---

## 20. Immediate next task

The immediate next task is a **re-estimation authorization memo** for the corrected pooled P3a specification:

- A separate authorization memo gates re-estimation of `ruro_occ_P3a_pooled` against the regenerated split stem.
- After re-estimation with a multi-start protocol, a fresh strict post-estimation review adjudicates whether the region block is now identified (S4, S5), whether the preference-block comparison (S6) passes, and whether the SA2 criteria are met.
- If the region block proves genuinely redundant or insignificant on the corrected data, the no-region design option becomes a legitimately evidenced choice at that review gate — not before.

Welfare, SA2, canonical promotion, and M1-clean displacement remain gated and are not authorized here.

---

## Required final statements

**R1 (couples region-dummy data-build fix) and R2 (precompute value-presence guard) are applied; the region dummies are now wired and identifiable on the regenerated data.** All 13 validation requirements pass. The cause-B defect that produced the flat-LL ridge in `beta_E_drgn2`–`beta_E_drgn8` has been removed.

**The original flat-region cause has been removed.** The pre-repair cause (B/DEGENERATE_OR_MISWIRED_COLUMNS — all-NaN input columns zeroed by `fillna(0.0)`) no longer applies on the regenerated data. The couples design matrix is now full-rank (9/9) and well-conditioned (κ = 3.195). The gradient is non-zero with respect to all seven region-dummy parameters.

**No solver was run.**

**No welfare was computed.**

**No SA2 verdict was issued.**

**M1-clean 2016 remains the active baseline.**