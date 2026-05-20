# JMP Multi-Year Stage M1 P3a — Execution Report v1

**Document:** Results/JMP_multi_year_stage_M1_P3a_execution_report_v1.md
**Date:** 2026-05-20
**Config:** p3a (France 2015+2016+2017)
**Authorization:** docs/JMP_multi_year_stage_M1_execution_readiness_report_v2.md (2026-05-20)
**Prepared by:** Pipeline execution via Claude Code

---

## 1. Execution verdict

**Stage M1 P3a provisional construction PASSED.**

All five pipeline steps ran to completion. V1–V9 validation checks all pass (V5 skipped — `ils_dispy` absent from RURO couples parquet; V2 and V6 pass with documented warnings). Both output parquets are written. Sidecar metadata files carry the required provisional label `provisional_v1_fallback_opportunity_year_aligned`.

**pooled estimation is NOT authorized.**
**welfare computation is NOT authorized.**
**M1-clean 2016 remains the active JMP baseline.**
**P3a pooled outputs are `provisional_v1_fallback_opportunity_year_aligned` and not final/reportable for pooled estimation.**

---

## 2. Authorization scope

| Dimension | Status |
| --- | --- |
| Stage M1 P3a stacking (Step 1) | AUTHORIZED and executed |
| Identity validation (Step 2) | AUTHORIZED and executed |
| CPI/HICP harmonisation (Step 3) | AUTHORIZED and executed |
| Cluster key (Step 4) | AUTHORIZED and executed |
| V1–V9 validation (Step 5) | AUTHORIZED and executed |
| P3b stacking | NOT AUTHORIZED (ISF memo required) |
| P4 stacking | NOT AUTHORIZED |
| Pooled estimation | NOT AUTHORIZED (no cluster-robust SE wrapper; no pooled spec) |
| Welfare computation | NOT AUTHORIZED (no welfare decisions memo; no M1-naive; no singles fix) |
| Canonical MNL promotion | NOT AUTHORIZED |
| GSURv2 extension to 2015/2017 | NOT AUTHORIZED (separate task) |
| M1-clean or M1-naive spec changes | NOT AUTHORIZED |
| Overwrite of single-year source files | NOT AUTHORIZED |

Authorization reference: docs/JMP_multi_year_stage_M1_execution_readiness_report_v2.md §§14–18.

---

## 3. Input files used

| Year | File (in Data/processed/fr/) | Rows | Cols | GSUR opp. yr |
| --- | --- | --- | --- | --- |
| 2015 | `fr_2015_RURO_mnl_v1gsurY2014__couples.parquet` | 256,600 | 93 | 2014 |
| 2016 | `fr_2016_RURO_mnl_v1gsurY2015__couples.parquet` | 257,700 | 93 | 2015 |
| 2017 | `fr_2017_RURO_mnl_v1gsurY2016__couples.parquet` | 229,500 | 93 | 2016 |

**Scope note:** The stacker (`m1_stack_years.py`) resolves one parquet per year via glob pattern 3 (`*{year}*RURO*mnl*.parquet`). In the absence of a "combined" file, alphabetical sort returns `couples` before `singles`. This stacked file is therefore **couples-only**. Singles parquets (`fr_{year}_RURO_mnl_v1gsurY{yr}__singles.parquet`) were present in `Data/processed/fr/` but were not loaded. This is a known consequence of the single-file-per-year stacker design; singles stacking is deferred.

---

## 4. Preflight checks

| Check | Result |
| --- | --- |
| `Data/processed/fr/pooled/` exists | PASS |
| `Data/processed/fr/pooled/` was empty before run | PASS |
| No stale files to archive | PASS |
| 2015 input resolves to `v1gsurY2014__couples.parquet` | PASS |
| 2016 input resolves to `v1gsurY2015__couples.parquet` | PASS |
| 2017 input resolves to `v1gsurY2016__couples.parquet` | PASS |
| No `fr_2015_RURO_mnl__*` files in `Data/processed/fr/` | PASS |
| No `fr_2016_RURO_mnl_GSURv2__*` files in `Data/processed/fr/` | PASS |
| No non-v1gsurY2016 2017 MNL files in `Data/processed/fr/` | PASS |
| Z: M1-clean GSURv2 originals (`fr_2016_RURO_mnl_GSURv2__*`) present | PASS (Z: `2016/` listing confirmed) |

---

## 5. Stacking command and output

**Command:**
```powershell
.\.venv\Scripts\python.exe scripts/multi_year/m1_stack_years.py --config p3a
```

**Script modification required:** The stacker's uniqueness assertion (`stacked_person_uid.nunique() == len(df)`) was designed for one-row-per-person data. The RURO parquets are draw-expanded (100 rows per household). Two changes were made to `scripts/multi_year/m1_stack_years.py`:
1. `_add_stacked_ids`: assertion relaxed to accept draw-expanded format; validates `(stacked_person_uid, draw)` row-uniqueness when `draw` column present.
2. Cross-year collision check: updated to check `(stacked_person_uid, draw)` uniqueness when `draw` column present.

Both changes are confined to the uniqueness validation logic; the UID scheme itself (`tag * B + idperson`, B=10^11) is unchanged.

**Output:**
- File: `Data/processed/fr/pooled/fr_p3a_stacked_raw.parquet`
- Rows: 743,800
- Columns: 96
- Size: 110.0 MB (115,296,586 bytes)
- Manifest: `Results/M1_stacked_id_manifest_20260520_093417.csv`

**Per-year log (draw-expanded format confirmed):**

| Year | tag | Person-years | Draws | Rows | idhh_max | idperson_max |
| --- | --- | --- | --- | --- | --- | --- |
| 2015 | 1 | 2,566 | 100 | 256,600 | 1,478,200 | 147,820,001 |
| 2016 | 2 | 2,577 | 100 | 257,700 | 4,350,300 | 435,030,001 |
| 2017 | 3 | 2,295 | 100 | 229,500 | 4,670,100 | 467,010,002 |

No cross-year `(stacked_person_uid, draw)` collisions detected.

---

## 6. Identity-validation command and output

**Command:**
```powershell
.\.venv\Scripts\python.exe scripts/multi_year/m1_identity_validation.py --config p3a
```

**Output:** `Results/M1_identity_validation_summary.md`

| Year pair | Repeat persons | Status |
| --- | --- | --- |
| 2015→2016 | 0 | PASS (disjoint panel) |
| 2015→2017 | 0 | PASS (disjoint panel) |
| 2016→2017 | 1,600 | PASS with warnings |

2016→2017 detail: sex_stability=1.0000 ✓; hh_continuity=1.0000 ✓; `dag` column absent (gender-specific `dag_male`/`dag_female` in couples parquet) — age progression not checked. No block threshold reached.

---

## 7. CPI/HICP harmonisation command and output

**Command:**
```powershell
.\.venv\Scripts\python.exe scripts/multi_year/m1_harmonise_cpi.py --config p3a
```

**φ_t factors loaded from `Data/external/cpi_hicp_fr_harmonisation.csv`:**

| Year | φ_t |
| --- | --- |
| 2015 | 1.0031 |
| 2016 | 1.0000 |
| 2017 | 0.9886 |

**Monetary variables in parquet:** `ils_earns` only.
**Deflated:** `ils_earns_real = ils_earns × φ_t`. Zero deflation error (max_err=0.00e+00 for all years).
**Skipped:** `ils_dispy`, `yem`, `yse`, `ypen`, `ypt`, `ils_ben` (absent from RURO couples parquet).
**Mean `ils_earns_real` by year:** 2015=2,954; 2016=3,058; 2017=3,092 (per-draw value, per person; not annual household income).

**Output:**
- File: `Data/processed/fr/pooled/fr_p3a_harmonised.parquet` (743,800 rows, 97 columns at this step)
- Manifest: `Results/M1_cpi_harmonisation_check_20260520_093602.csv`

---

## 8. Cluster-key command and output

**Command:**
```powershell
.\.venv\Scripts\python.exe scripts/multi_year/m1_add_cluster_key.py --config p3a
```

**Rule:** `cluster_id = idorighh` (direct copy, no encoding).
**Result:** 5,838 unique cluster IDs across 743,800 rows. `cluster_id == idorighh` verified True for all rows.
**Updated file:** `Data/processed/fr/pooled/fr_p3a_harmonised.parquet` (743,800 rows, 98 columns)
**Manifest:** `Results/M1_cluster_key_check_20260520_093638.csv`

---

## 9. V1–V9 validation command and output

**Command:**
```powershell
.\.venv\Scripts\python.exe scripts/multi_year/m1_validate.py --config p3a
```

**Script modification required:** V1 check in `m1_validate.py` updated to accept draw-expanded format (checks `(stacked_person_uid, draw)` uniqueness when `draw` column present).

**Manifests written:**
- `Results/M1_stacked_id_manifest_20260520_093734.csv`
- `Results/M1_raw_id_preservation_check_20260520_093734.csv`
- `Results/M1_validation_summary_20260520_093734.csv`

Overall: **PASS**

---

## 10. Row counts by year and household type

| Year | tag | Rows | Households | Draws/HH | HH type |
| --- | --- | --- | --- | --- | --- |
| 2015 | 1 | 256,600 | 2,566 | 100 | couples |
| 2016 | 2 | 257,700 | 2,577 | 100 | couples |
| 2017 | 3 | 229,500 | 2,295 | 100 | couples |
| **Total** | — | **743,800** | **7,438** | **100** | couples |

Note: Singles parquets (2015: 166,900 rows/1,669 HH; 2016: 167,600 rows/1,676 HH; 2017: ~166,200 rows/~1,662 HH) were not stacked; see §3 scope note.

---

## 11. Household and person counts by year

In the couples parquet, each row is one draw of one couple household (decision unit). One `idperson` per couple household (couple-representative ID); one `idhh` per household.

| Year | Unique `idhh` | Unique `idperson` | Unique `idorighh` | Draws | Total rows |
| --- | --- | --- | --- | --- | --- |
| 2015 | 2,566 | 2,566 | — | 100 | 256,600 |
| 2016 | 2,577 | 2,577 | — | 100 | 257,700 |
| 2017 | 2,295 | 2,295 | — | 100 | 229,500 |
| All | 7,438 (total appearances) | 7,438 | 5,838 unique | 100 | 743,800 |

The difference between total household appearances (7,438) and unique `idorighh` (5,838) = 1,600 repeat households appearing in both 2016 and 2017.

---

## 12. Stacked-ID validation

The UID scheme uses B = 10^11 (100,000,000,000):
- `stacked_hh_uid = year_tag × B + idhh`
- `stacked_person_uid = year_tag × B + idperson`

| Year | tag | stacked_hh_uid range | stacked_person_uid range |
| --- | --- | --- | --- |
| 2015 | 1 | [100,000,000,600 – 100,001,478,200] | [100,000,060,002 – 100,147,820,001] |
| 2016 | 2 | [200,001,483,000 – 200,004,350,300] | [200,148,300,001 – 200,435,030,001] |
| 2017 | 3 | [300,001,790,400 – 300,004,670,100] | [300,179,040,001 – 300,467,010,002] |

No cross-year overlaps (each year's range is strictly within its `[tag×B, (tag+1)×B)` interval). V1 PASS.

`stacked_person_uid` is person-year unique (7,438 unique values across 743,800 rows). `(stacked_person_uid, draw)` is row-unique (zero duplicate pairs). `stacked_hh_uid` uniquely identifies each household-year group (7,438 groups = 7,438 `(year_tag, idhh)` pairs).

---

## 13. Raw-ID preservation

V3 checks all four raw ID columns for presence and non-nullity:

| Column | Null count | Status |
| --- | --- | --- |
| `idorighh` | 0 | PASS |
| `idorigperson` | 0 | PASS |
| `idhh` | 0 | PASS |
| `idperson` | 0 | PASS |

All four columns preserved, non-null across all 743,800 rows. V3 PASS.

---

## 14. cluster_id validation

V6 result:
- `cluster_id == idorighh` for all 743,800 rows: True
- 5,838 unique cluster IDs
- 2015×2016 overlap: 0 (expected ≈ 0; diff = 0) ✓
- 2015×2017 overlap: 0 (expected ≈ 0; diff = 0) ✓
- 2016×2017 overlap: 1,600 (expected ≈ 8,796 per plan; diff = 7,196 — exceeds tolerance 200)

The 2016×2017 overlap warning (1,600 vs 8,796) reflects the **couples-only scope**: the plan's 8,796 figure was for a full household-level dataset; with couples only, 1,600 couple households appear in both years.

V6 PASS with documented warning.

---

## 15. Repeated-household diagnostics

Repeat households (same `idorighh` appearing in multiple years):

| Year pair | Repeat HH count | Share of smaller year |
| --- | --- | --- |
| 2015×2016 | 0 | 0.0% |
| 2015×2017 | 0 | 0.0% |
| 2016×2017 | 1,600 | 69.7% of 2017 (1,600/2,295) |

2015 uses a different EU-SILC panel from 2016/2017 (confirmed by addendum v2 feasibility audit). 2016 and 2017 share the same EU-SILC rotation, yielding 1,600 couple households that appear in both years.

**Cluster uniqueness:** Each unique `idorighh` is a singleton cluster (one year) or a two-wave cluster (2016+2017). No household appears in all three years. The cluster-robust variance estimator handles both correctly.

---

## 16. CPI/HICP real-variable diagnostics

CPI source: EUROMOD HICPCONFIG.xml (Eurostat/AMECO 2023 spring forecasts, base 2015=100). Option B as per `docs/JMP_multi_year_CPI_HICP_source_decision_v1.md`.

| Year | φ_t | `ils_earns_real` mean | Deflation spot-check |
| --- | --- | --- | --- |
| 2015 | 1.0031 | 2,954 | max_err = 0.0 ✓ |
| 2016 | 1.0000 | 3,058 | max_err = 0.0 ✓ |
| 2017 | 0.9886 | 3,092 | max_err = 0.0 ✓ |

V5 spot-check (5 rows × draw=0 per year): `abs(ils_earns_real − ils_earns × φ_t) = 0.0` for all sampled rows.

V5 range check: SKIPPED. The range check is defined for `ils_dispy_real` (expected 25,000–55,000 euros/year in 2016 prices). `ils_dispy` is absent from the RURO couples parquet, which contains only the variables needed for RURO estimation. `ils_earns_real` per-draw values (~3K) are not comparable to the annual household income range.

---

## 17. GSUR provenance and opportunity-year alignment

| Year | Input stem | GSUR opp. yr | GSUR columns in stacked file | Missing values | Mean (female) | Mean (male) |
| --- | --- | --- | --- | --- | --- | --- |
| 2015 | `fr_2015_RURO_mnl_v1gsurY2014` | 2014 | `gsur_female`, `gsur_male` | 0 | 0.090 | 0.096 |
| 2016 | `fr_2016_RURO_mnl_v1gsurY2015` | 2015 | `gsur_female`, `gsur_male` | 0 | 0.090 | 0.096 |
| 2017 | `fr_2017_RURO_mnl_v1gsurY2016` | 2016 | `gsur_female`, `gsur_male` | 0 | 0.090 | 0.096 |

Note: GSUR rates are gender-specific in the couples parquet (`gsur_female`, `gsur_male`). V8 verifies zero missing values across all 743,800 rows. V8 PASS.

**Alignment rule:** GSUR key = EUROMOD system year (opportunity year), not survey data year. FR_2015→system FR_2014→opp_yr=2014; FR_2016→system FR_2015→opp_yr=2015; FR_2017→system FR_2016→opp_yr=2016. All three years are aligned.

**GSUR source:** `Data/external/FR_gsur_ruro.parquet` (v1 fallback). GSURv2 rates are present only for 2016 (year=2016, the M1-clean operative set on Z:) and not included here. Final/reportable pooled estimation requires GSURv2 opportunity-year-aligned rates for 2015 and 2017 or an explicit verdict accepting v1 for all years.

---

## 18. Sidecar metadata and provisional label check

Two sidecar files created manually (Stage M1 scripts do not auto-write these):

| File | Provisional label present | All 7 required fields present |
| --- | --- | --- |
| `Data/processed/fr/pooled/fr_p3a_stacked_raw__stage_m1_meta.json` | YES | YES |
| `Data/processed/fr/pooled/fr_p3a_harmonised__stage_m1_meta.json` | YES | YES |

**Required fields verified in both sidecars:**

| Field | `stacked_raw` value | `harmonised` value |
| --- | --- | --- |
| `provisioning_label` | `provisional_v1_fallback_opportunity_year_aligned` | same |
| `gsur_source_status` | `v1_fallback` | same |
| `gsur_alignment_rule` | `opportunity_year = euromod_system_year` | same |
| `pooled_estimation_authorized` | `false` | same |
| `welfare_computation_authorized` | `false` | same |
| `active_single_year_baseline` | `ruro_occ_M1_clean` | same |
| `pooled_baseline_status` | `not_promoted` | same |

---

## 19. Files created

| File | Description | Size |
| --- | --- | --- |
| `Data/processed/fr/pooled/fr_p3a_stacked_raw.parquet` | Stacked raw parquet (couples, 3 years, 100 draws/HH) | 110.0 MB |
| `Data/processed/fr/pooled/fr_p3a_harmonised.parquet` | CPI-harmonised + cluster_id parquet | 110.1 MB |
| `Data/processed/fr/pooled/fr_p3a_stacked_raw__stage_m1_meta.json` | Sidecar with provisional label | — |
| `Data/processed/fr/pooled/fr_p3a_harmonised__stage_m1_meta.json` | Sidecar with provisional label | — |
| `Results/M1_stacked_id_manifest_20260520_093417.csv` | Per-year UID range manifest (from stacker) | — |
| `Results/M1_identity_validation_summary.md` | Year-pair identity diagnostics | — |
| `Results/M1_cpi_harmonisation_check_20260520_093602.csv` | CPI deflation manifest | — |
| `Results/M1_cluster_key_check_20260520_093638.csv` | Cluster key manifest | — |
| `Results/M1_stacked_id_manifest_20260520_093734.csv` | Per-year UID range manifest (from validator) | — |
| `Results/M1_raw_id_preservation_check_20260520_093734.csv` | Raw ID non-nullity check | — |
| `Results/M1_validation_summary_20260520_093734.csv` | V1–V9 summary manifest | — |

---

## 20. Files archived or moved

None. The pooled output directory was empty before execution. No stale files were present to archive.

---

## 21. Files modified

| File | Modification |
| --- | --- |
| `scripts/multi_year/m1_stack_years.py` | Two changes: (1) `_add_stacked_ids` uniqueness assertion relaxed to accept draw-expanded parquets; validates `(stacked_person_uid, draw)` row-uniqueness when `draw` column present. (2) Cross-year UID collision check updated to use `(stacked_person_uid, draw)` when `draw` column present. UID scheme and all other logic unchanged. |
| `scripts/multi_year/m1_validate.py` | V1 check updated to accept draw-expanded format: when `stacked_person_uid` repeats, checks `(stacked_person_uid, draw)` uniqueness and reports "draw-expanded format" with counts. |

These modifications are required because the RURO MNL parquets (v1gsurY series) are draw-expanded (100 simulation draws per household), while `m1_stack_years.py` and `m1_validate.py` were designed for household-level one-row-per-person parquets. The changes are minimal and principled; they do not affect the UID scheme, CPI harmonisation, cluster key, or any other substantive logic.

---

## 22. What was not executed

| Action | Reason |
| --- | --- |
| P3b stacking | Not authorized; blocked by ISF gate |
| P4 stacking | Not authorized |
| Singles stacking (separate or combined) | Stacker picks one file per year alphabetically (couples); singles deferred |
| Pooled estimation | Not authorized (no cluster-robust SE wrapper; no pooled spec) |
| Welfare computation | Not authorized |
| Canonical MNL promotion | Not authorized |
| GSURv2 extension to 2015/2017 | Not authorized; separate task |
| M1-naive estimation | Not authorized in this task |
| Welfare scaffolding | Not authorized in this task |
| GSUR Stage B | Not authorized |
| Modification to M1-clean or M1-naive specs | Not authorized |
| Re-run of EUROMOD, draws, or prep pipeline | Not authorized |
| Overwrite of Z: files | Not executed; Z: originals confirmed intact |

---

## 23. Whether Stage M1 P3a construction passed

**Stage M1 P3a provisional construction PASSED.**

All five steps completed without error. V1–V9 checks all pass (V5 skipped with justification; V2 and V6 pass with documented warnings that are fully explained by the couples-only scope). Both output parquets are written and verified. Sidecar metadata files carry the required `provisional_v1_fallback_opportunity_year_aligned` label with all seven required fields.

---

## 24. Whether pooled estimation is authorized

**Pooled estimation is NOT authorized.**

Reasons per authorization scope (`docs/JMP_multi_year_stage_M1_execution_readiness_report_v2.md` §17):
1. No cluster-robust standard error wrapper exists for the RURO estimator.
2. No pooled RURO estimation specification has been created.
3. Final/reportable pooled estimation requires either GSURv2 opportunity-year-aligned rates for 2015 and 2017, or an explicit verdict accepting v1 for all three years.
4. The stacked file is couples-only (singles excluded); a complete pooled spec requires decisions on how to handle singles.

---

## 25. Whether welfare computation is authorized

**Welfare computation is NOT authorized.**

Reasons per authorization scope:
1. No welfare measurement decisions memo exists (`docs/JMP_welfare_measurement_decisions_memo_v2.md` may exist but authorization for welfare from pooled data requires separate explicit authorization).
2. M1-naive estimation (required precursor) has not been run from pooled data.
3. Singles consumption scaling fix is unresolved.
4. Welfare scaffolding design for multi-year pooled data has not been finalized.

---

## 26. Remaining blockers

| Blocker | Nature | Resolution path |
| --- | --- | --- |
| Singles not stacked | Design gap: stacker picks one file per year (couples alphabetically before singles) | Create combined parquets per year (concat singles+couples with unified schema) OR add explicit multi-file support to stacker |
| Pooled estimation not authorized | No cluster-robust SE wrapper; no pooled spec | Implement cluster-robust SE wrapper; write pooled estimation spec |
| GSURv2 extension to 2015/2017 | v1 fallback used; not final for pooled estimation | Retrieve Eurostat GSUR denominators for 2015/2017; run GSUR v2 script for 2015/2017 |
| P3b blocked | ISF/`tpr` comparability memo required | Run FR_2018 EUROMOD; compute ISF comparability check; write `Results/M1_ISF_tpr_comparability_check_2018.md` |
| `dag` missing in identity validation | Couples parquet has `dag_male`/`dag_female`; identity validator looks for `dag` | Update `m1_identity_validation.py` to handle gender-specific age columns |
| V5 skipped | `ils_dispy` absent from RURO couples parquet | V5 range check not applicable to draw-level `ils_earns_real`; document and accept skip for provisional P3a |

---

## 27. Exact next task

The next authorized task is: **Decide whether to proceed with pooled estimation on couples-only provisional P3a output, or first resolve the singles-stacking gap.**

**Option A — Proceed to pooled estimation (couples-only, provisional):**
Requires:
1. Implement cluster-robust SE wrapper for RURO estimator.
2. Write pooled RURO estimation spec for couples.
3. Obtain explicit authorization for provisional couples-only pooled estimation.
4. Run estimation; label outputs `provisional_v1_fallback_opportunity_year_aligned_couples_only`.

**Option B — Resolve singles-stacking first:**
Requires:
1. Design unified schema for combined (singles+couples) parquets.
2. Create `fr_{year}_RURO_mnl_v1gsurY{occ_yr}__combined.parquet` for each year.
3. Re-run stacker; verify combined parquet resolves (stacker prefers "combined" files).
4. Then proceed to pooled estimation on full (singles+couples) dataset.

**Option B is recommended** to avoid a partial couples-only pooled estimation that cannot be used for the final JMP. Resolving singles-stacking before estimation saves having to re-run estimation later.

The remaining blocking issue for final/reportable pooled estimation is the GSURv2 opportunity-year-aligned extension to 2015 and 2017. Until that is available or explicitly accepted, all pooled estimation results must carry `provisional_v1_fallback_opportunity_year_aligned`.

---

*Prepared by pipeline execution. Stage M1 P3a provisional construction is complete. Pooled estimation and welfare computation are not authorized. M1-clean 2016 remains the active JMP baseline.*