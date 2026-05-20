# JMP GSURv2 Multi-Year Extension — Construction Report v1

*France 2014–2015–2016 | v1 | 2026-05-20*

Authorization: `docs/JMP_GSURv2_multi_year_extension_construction_authorization_v1.md`

---

## 1. Construction verdict

**GSURv2 multi-year lookup construction PASSED.**

All three opportunity-year Stage A lookups were constructed successfully
under Option B. The y2016 value-identity gate passed with maximum
absolute `gsur` difference of **0.0** (exact). The y2015 and y2014
constructions followed conditionally and both passed all validation
checks. Six output files were written to `Data/external/`.

| Year | Construction | Value-identity / Validation | Outcome |
|------|-------------|----------------------------|---------|
| 2016 | PASS | G1–G4 all PASS; max diff = 0.0 | **PASS** |
| 2015 | PASS | Y2015-1–Y2015-5 all PASS | **PASS** |
| 2014 | PASS | Y2014-1–Y2014-5 all PASS | **PASS** |

No halt was triggered. No year-tagged output pre-existed. The untagged
baseline `FR_gsur_ruro_v2_stageA.parquet` was not modified, retired,
or moved.

---

## 2. Authorization scope

Construction executed under Option B per the construction authorization
memo §4. Construction scope was Stage A lookup production only:

- Run the parameterised script for all three opportunity years.
- Perform the y2016 key-aligned value-identity check (G1–G4).
- Inspect sidecars and validation outputs for all three years.
- Write the six year-tagged output files to `Data/external/`.

Not executed (separately gated):
- MNL parquet rebuild.
- Pooled stacking re-run.
- Pooled estimation.
- Welfare computation.
- Canonical promotion.
- Retirement or archival of the untagged y2016 file.
- Canary/validation script updates or reference migration.

Construction script: `scripts/enhanced/enh_prepare_FR_gsur_v2.py`,
commit `178ca72` (confirmed by sidecar `script_version` field for all
three years).

Interpreter: `.venv\Scripts\python.exe`
(`U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe`).

---

## 3. Commands run

Commands run in order, each using `.venv\Scripts\python.exe`:

```
Step 1  .venv\Scripts\python.exe scripts\enhanced\enh_prepare_FR_gsur_v2.py --opportunity-year 2016
Step 2  [Key-aligned value-identity check — Python inline]
Step 3  [Sidecar inspection — Python inline]
Step 4  .venv\Scripts\python.exe scripts\enhanced\enh_prepare_FR_gsur_v2.py --opportunity-year 2015
Step 5  [y2015 validation — Python inline]
Step 6  .venv\Scripts\python.exe scripts\enhanced\enh_prepare_FR_gsur_v2.py --opportunity-year 2014
Step 7  [y2014 validation — Python inline]
```

Pre-run preflight confirmed:
- All six year-tagged outputs absent before construction began.
- Existing untagged baseline present with correct SHA-256.
- Construction script present at expected path.

The script reported all nine validation checks PASS (`L1_unique_keys`,
`L2_proportion_units`, `L3_drgn1_support`, `L4_idf_crosswalk_sanity`,
`L5_national_benchmark`, `L7_weighting_source`, `L8_approximation_flags`,
`missing_values`, `IDF_parity`) for every opportunity year. Overall
script verdict: PASS for all three years.

---

## 4. y2016 value-identity gate

**GATE: PASS**

The y2016 year-tagged lookup was compared key-aligned against the
existing untagged baseline `FR_gsur_ruro_v2_stageA.parquet` on keys
`(year, drgn1, educ3, sex)`.

| Condition | Requirement | Result |
|-----------|-------------|--------|
| G1 — row counts | Both files exactly 54 rows | new: 54, old: 54 — **PASS** |
| G2 — key match | All keys match exactly | All 54 key tuples match — **PASS** |
| G3 — no duplicates | Zero duplicate keys in either file | new: 0, old: 0 — **PASS** |
| G4 — max absolute diff | ≤ 1e-12, NaN-aware over 48 active cells | **0.0 exactly — PASS** |
| NaN stub alignment | drgn1=9 rows NaN in both files | 6 stubs NaN in both — **PASS** |

Maximum absolute `gsur` difference over 48 active (non-null) cells: **0.0**

The y2016 year-tagged parquet is byte-identical to the untagged
baseline (both SHA-256 `19ac53143fb404f3de44f4e2abc3313b0946eda835261496720bc511358c24ef`,
7,444 bytes), confirming that the parameterised script reproduces the
existing validated y2016 lookup exactly.

The y2016 value-identity gate licensed the y2015 and y2014
construction per §6 of the authorization memo.

---

## 5. y2016 output and sidecar

**VALIDATION: PASS**

Output file: `Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet`
- SHA-256: `19ac53143fb404f3de44f4e2abc3313b0946eda835261496720bc511358c24ef`
- Size: 7,444 bytes
- Rows: 54 (48 active drgn1 1–8, 6 stubs drgn1=9)
- Columns: `year`, `drgn1`, `educ3`, `sex`, `gsur`, `weighting_source`,
  `gsur_age_band_used`, `gsur_legacy_misaligned`, `denom_flag`,
  `n_components`, `gsur_unreliable`
- `gsur` range (active cells): 0.047036 to 0.234
- drgn1 values: 1–9 (8 active + 1 stub)
- educ3 values: 0, 1, 2
- sex values: F, M

Sidecar: `Data/external/FR_gsur_ruro_v2_stageA_y2016__sidecar.json`

| Field | Value |
|-------|-------|
| `opportunity_year` | 2016 |
| `gsur_column_name` | `"gsur"` |
| `output_path` | `Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet` |
| `input_d2` | `Data/external/lfst_r_lfsd2pop_FR_2016.tsv` |
| `input_d1` | `Data/external/lfst_r_lfp2acedu_FR_2016.tsv` |
| `input_unemployment_workbook` | `Data/external/FR_gsur.xlsx` |
| `input_benchmark_csv` | `Data/external/insee_001688526_2016.csv` |
| `benchmark_pct` | 9.725 |
| `nuts_vintage` | `"NUTS2016"` |
| `idf_parity_difference` | 0.0 |
| `benchmark_difference_pct` | 0.1718 |
| `row_count` | 54 |
| `build_timestamp` | `2026-05-20T19:06:59.392956+00:00` |
| `script_version` | `178ca72bcb40b829a41648a470cb4c31aee9605b` |

All 14 sidecar fields present. IDF parity: 0.0 (PASS). L5 benchmark
difference: 0.1718 ppt (recorded; diagnostic only, construction-level
validation check L5 PASS).

---

## 6. y2015 output and sidecar

**VALIDATION: PASS**

Output file: `Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet`
- SHA-256: `f51ad6306574bf3a1d7b577e7741222c5bf2fb8126e512c0bbf965d6a2d03c83`
- Size: 7,433 bytes
- Rows: 54 (48 active drgn1 1–8, 6 stubs drgn1=9)
- Columns: same 11-column schema as y2016
- `gsur` range (active cells): 0.053183 to 0.225
- drgn1 values: 1–9; educ3 values: 0, 1, 2; sex values: F, M

Sidecar: `Data/external/FR_gsur_ruro_v2_stageA_y2015__sidecar.json`

| Field | Value |
|-------|-------|
| `opportunity_year` | 2015 |
| `gsur_column_name` | `"gsur"` |
| `output_path` | `Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet` |
| `input_d2` | `Data/external/lfst_r_lfsd2pop_FR_2015.tsv` |
| `input_d1` | `Data/external/lfst_r_lfp2acedu_FR_2015.tsv` |
| `input_unemployment_workbook` | `Data/external/FR_gsur.xlsx` |
| `input_benchmark_csv` | `Data/external/insee_001688526_2015.csv` |
| `benchmark_pct` | 10.025 |
| `nuts_vintage` | `"NUTS2016"` |
| `idf_parity_difference` | 0.0 |
| `benchmark_difference_pct` | 0.0943 |
| `row_count` | 54 |
| `build_timestamp` | `2026-05-20T19:08:21.653726+00:00` |
| `script_version` | `178ca72bcb40b829a41648a470cb4c31aee9605b` |

All 14 sidecar fields present. IDF parity: 0.0 (PASS). L5 benchmark
difference: 0.0943 ppt (recorded; diagnostic only).

---

## 7. y2014 output and sidecar

**VALIDATION: PASS**

Output file: `Data/external/FR_gsur_ruro_v2_stageA_y2014.parquet`
- SHA-256: `740ef6c7e57e355fb517262202be03bfc947589ac68024f971f620e3d2557e68`
- Size: 7,441 bytes
- Rows: 54 (48 active drgn1 1–8, 6 stubs drgn1=9)
- Columns: same 11-column schema as y2016 and y2015
- `gsur` range (active cells): 0.053647 to 0.261
- drgn1 values: 1–9; educ3 values: 0, 1, 2; sex values: F, M

Sidecar: `Data/external/FR_gsur_ruro_v2_stageA_y2014__sidecar.json`

| Field | Value |
|-------|-------|
| `opportunity_year` | 2014 |
| `gsur_column_name` | `"gsur"` |
| `output_path` | `Data/external/FR_gsur_ruro_v2_stageA_y2014.parquet` |
| `input_d2` | `Data/external/lfst_r_lfsd2pop_FR_2014.tsv` |
| `input_d1` | `Data/external/lfst_r_lfp2acedu_FR_2014.tsv` |
| `input_unemployment_workbook` | `Data/external/FR_gsur.xlsx` |
| `input_benchmark_csv` | `Data/external/insee_001688526_2014.csv` |
| `benchmark_pct` | 9.9 |
| `nuts_vintage` | `"NUTS2016"` |
| `idf_parity_difference` | 0.0 |
| `benchmark_difference_pct` | 0.0494 |
| `row_count` | 54 |
| `build_timestamp` | `2026-05-20T19:09:10.891357+00:00` |
| `script_version` | `178ca72bcb40b829a41648a470cb4c31aee9605b` |

All 14 sidecar fields present. IDF parity: 0.0 (PASS). L5 benchmark
difference: 0.0494 ppt (recorded; diagnostic only).

---

## 8. Source files used

All twelve external input files confirmed present at construction time.
All files used as specified by the construction authorization §9.

| File | Role | Used for |
|------|------|---------|
| `Data/external/FR_gsur.xlsx` | Unemployment rates 2007–2019 | y2016, y2015, y2014 (shared) |
| `Data/external/fr_drgn1_to_nuts2_crosswalk.csv` | drgn1 → NUTS-2 mapping | y2016, y2015, y2014 (shared) |
| `Data/external/lfst_r_lfsd2pop_FR_2016.tsv` | D2 denominator | y2016 |
| `Data/external/lfst_r_lfp2acedu_FR_2016.tsv` | D1 denominator (diagnostic) | y2016 |
| `Data/external/insee_001688526_2016.csv` | INSEE benchmark CSV | y2016 (9.725%) |
| `Data/external/lfst_r_lfsd2pop_FR_2015.tsv` | D2 denominator | y2015 |
| `Data/external/lfst_r_lfp2acedu_FR_2015.tsv` | D1 denominator (diagnostic) | y2015 |
| `Data/external/insee_001688526_2015.csv` | INSEE benchmark CSV | y2015 (10.025%) |
| `Data/external/lfst_r_lfsd2pop_FR_2014.tsv` | D2 denominator | y2014 |
| `Data/external/lfst_r_lfp2acedu_FR_2014.tsv` | D1 denominator (diagnostic) | y2014 |
| `Data/external/insee_001688526_2014.csv` | INSEE benchmark CSV | y2014 (9.9%) |
| `Data/external/FR_gsur_ruro_v2_stageA.parquet` | Value-identity baseline | y2016 gate only |

No input file was missing. No file retrieval was performed.

D2 row counts read: 1,584 (y2016), 1,583 (y2015), 1,584 (y2014) —
consistent with the year-specific Eurostat denominator files.

---

## 9. Crosswalk logic

The crosswalk `fr_drgn1_to_nuts2_crosswalk.csv` contains 22 NUTS-2 rows
mapping to drgn1 values 1–8. All three opportunity-year constructions
loaded the same shared crosswalk (22 rows, drgn1 range 1–8). The
construction applied population-weighted aggregation from NUTS-2 to
drgn1 using the crosswalk.

The IDF parity check (drgn1=1 = single-component FR10) passed at 0.0
for all three years, confirming the crosswalk-weighted aggregation
reduces correctly to the single-component value for Île-de-France.

FRM0 (Mayotte) and FRI2 (Corsica) suppression is year-invariant: the
same `approximate_uniform` fallback pattern applies across 2014, 2015,
and 2016 where denominator data is suppressed. This is reflected in the
`denom_flag` and `gsur_unreliable` columns of each output parquet, and
confirmed by the L8 (approximation flags) check passing for all years.

NUTS vintage: all three constructions used NUTS-2016 (confirmed at
retrieval, re-audit §3; recorded in sidecar `nuts_vintage` field).

---

## 10. Denominator logic

D2 (`lfst_r_lfsd2pop_FR_{YEAR}.tsv`) is the operative denominator for
the Y20-64 age-band aggregation at NUTS-2 level. D1
(`lfst_r_lfp2acedu_FR_{YEAR}.tsv`) is diagnostic only: the Eurostat D1
table does not publish the Y20-64 age band at NUTS-2 level, a year-
invariant limitation. The D1 vs D2 diagnostic was computed for the
Y15-74 age band and recorded in each construction run:

| Year | Mean |D2-D1| (ppt) | Max |D2-D1| (ppt) |
|------|------------------|-----------------|
| 2016 | 0.027 | 0.327 |
| 2015 | 0.022 | 0.190 |
| 2014 | 0.017 | 0.148 |

The D1 vs D2 differences are at the Y15-74 age band (diagnostic
comparison band, not the construction band). The construction uses D2
at Y20-64 exclusively; D1 differences at Y15-74 are recorded for
audit purposes and do not affect the constructed cell-level rates.

The `L7_weighting_source` check passed for all three years, confirming
the weighting source was applied correctly.

---

## 11. Benchmark logic

Benchmark values are read from year-specific INSEE BDM 001688526 CSVs
(C5 parameterisation). Each CSV contains the four quarterly observations
for that year; the script reads the annual-average row (`period` =
year) from each file.

| Year | Benchmark (%) | Source row | L5 benchmark difference (ppt) |
|------|--------------|------------|-------------------------------|
| 2016 | 9.725 | `insee_001688526_2016.csv`, period=2016 | 0.1718 |
| 2015 | 10.025 | `insee_001688526_2015.csv`, period=2015 | 0.0943 |
| 2014 | 9.9 | `insee_001688526_2014.csv`, period=2014 | 0.0494 |

The L5 national-benchmark check passed for all three years. The L5
check compares the constructed national GSUR aggregate against the
INSEE annual benchmark; a deviation is a consistency diagnostic, not
a construction gate. The deviations recorded (0.05–0.17 ppt) are
within the expected range for a population-weighted NUTS-2 → national
aggregation versus a direct national survey figure.

---

## 12. Sidecar metadata

All three sidecars contain exactly 14 fields as specified in §12 of the
construction authorization. Fields are identical across years except for
the year-specific values:

| Field | y2016 | y2015 | y2014 |
|-------|-------|-------|-------|
| `opportunity_year` | 2016 | 2015 | 2014 |
| `gsur_column_name` | `"gsur"` | `"gsur"` | `"gsur"` |
| `output_path` | `…_y2016.parquet` | `…_y2015.parquet` | `…_y2014.parquet` |
| `input_d2` | `…_2016.tsv` | `…_2015.tsv` | `…_2014.tsv` |
| `input_d1` | `…_2016.tsv` | `…_2015.tsv` | `…_2014.tsv` |
| `input_unemployment_workbook` | `FR_gsur.xlsx` | `FR_gsur.xlsx` | `FR_gsur.xlsx` |
| `input_benchmark_csv` | `…_2016.csv` | `…_2015.csv` | `…_2014.csv` |
| `benchmark_pct` | 9.725 | 10.025 | 9.9 |
| `nuts_vintage` | `"NUTS2016"` | `"NUTS2016"` | `"NUTS2016"` |
| `idf_parity_difference` | 0.0 | 0.0 | 0.0 |
| `benchmark_difference_pct` | 0.1718 | 0.0943 | 0.0494 |
| `row_count` | 54 | 54 | 54 |
| `build_timestamp` | `2026-05-20T19:06:59Z` | `2026-05-20T19:08:21Z` | `2026-05-20T19:09:10Z` |
| `script_version` | `178ca72bcb…` | `178ca72bcb…` | `178ca72bcb…` |

`script_version` is the full git SHA of `enh_prepare_FR_gsur_v2.py`:
`178ca72bcb40b829a41648a470cb4c31aee9605b` — consistent across all
three years, confirming a single script version was used throughout
construction.

---

## 13. Files created

Six files were created in `Data/external/`:

| File | SHA-256 | Size (bytes) | Rows |
|------|---------|-------------|------|
| `FR_gsur_ruro_v2_stageA_y2016.parquet` | `19ac53143fb404f3de44f4e2abc3313b0946eda835261496720bc511358c24ef` | 7,444 | 54 |
| `FR_gsur_ruro_v2_stageA_y2016__sidecar.json` | (JSON) | — | — |
| `FR_gsur_ruro_v2_stageA_y2015.parquet` | `f51ad6306574bf3a1d7b577e7741222c5bf2fb8126e512c0bbf965d6a2d03c83` | 7,433 | 54 |
| `FR_gsur_ruro_v2_stageA_y2015__sidecar.json` | (JSON) | — | — |
| `FR_gsur_ruro_v2_stageA_y2014.parquet` | `740ef6c7e57e355fb517262202be03bfc947589ac68024f971f620e3d2557e68` | 7,441 | 54 |
| `FR_gsur_ruro_v2_stageA_y2014__sidecar.json` | (JSON) | — | — |

Note on git tracking: the `Data/` directory is excluded from git
tracking by `.gitignore` (rule `Data/`, line 21). The six output files
are present on disk and fully attested by their sidecar provenance
records. They are not git-committed; their provenance is carried by the
sidecars and by this construction report.

This construction report and the validation report are committed to git.

---

## 14. Files modified

No files were modified by this construction. The construction script
`scripts/enhanced/enh_prepare_FR_gsur_v2.py` was not modified (read-
only use). The existing untagged baseline
`Data/external/FR_gsur_ruro_v2_stageA.parquet` was not modified,
retired, or moved. Its SHA-256 remains
`19ac53143fb404f3de44f4e2abc3313b0946eda835261496720bc511358c24ef`
and size 7,444 bytes, unchanged from the pre-construction state.

No MNL parquets were modified. No config files were modified. No canary
or validation scripts were modified.

---

## 15. What was not executed

The following were not executed, consistent with the authorization
boundary (authorization memo §16):

- MNL parquet rebuild (no `FR_2016_*.parquet`, `FR_2015_*.parquet`,
  or `FR_2017_*.parquet` was written or modified).
- Stage M1 pooled stacking re-run.
- Pooled estimation of any kind.
- Welfare implementation or computation.
- Canonical promotion of any file.
- Retirement, archival, deletion, or movement of the untagged y2016
  baseline (`FR_gsur_ruro_v2_stageA.parquet`).
- `git mv` of any file.
- Modification of canary scripts or validation scripts.
- Reference migration from untagged to year-tagged paths.

Post-construction cleanup and reference migration are separately gated
after the construction report and validation report pass.

---

## 16. Whether MNL parquet rebuild is authorized

**MNL parquet rebuild is NOT authorized.**

The merge of the GSURv2 lookups into the FR_2015, FR_2016, and FR_2017
MNL parquets is downstream of the lookup construction, requires its own
authorization, and additionally requires the O7 crosswalk sign-off
(authorization memo §16 N1), which is pending the user's decision.

---

## 17. Whether pooled estimation is authorized

**Pooled estimation is NOT authorized.**

No pooled estimation, provisional or final, is authorized by this
construction (authorization memo §16 N3). The final pooled estimation
remains gated behind the complete GSURv2-based MNL rebuild, the
cluster-robust SE wrapper, and the pooled specification.

---

## 18. Whether welfare computation is authorized

**Welfare computation is NOT authorized.**

No welfare implementation or computation is authorized by this
construction (authorization memo §16 N4). Welfare work requires its own
authorization and an accepted empirical baseline.

---

## 19. Remaining blockers

No blockers remain for the lookup construction itself — it is complete.

Blockers for downstream steps:

| Downstream step | Blocker |
|----------------|---------|
| MNL parquet rebuild | O7 crosswalk sign-off (user decision, pending); separate MNL rebuild authorization |
| Pooled stacking re-run | MNL parquet rebuild not yet complete |
| Pooled estimation | MNL parquet rebuild not yet complete; cluster-robust SE wrapper; pooled specification |
| Welfare computation | Accepted empirical baseline not yet established |
| Post-construction cleanup (untagged file archival, reference migration) | Separately gated after this construction report and validation report pass |

---

## 20. Exact next task

**The next gate is the O7 crosswalk sign-off (a user decision).**

The O7 sign-off determines whether the NUTS-2 → drgn1 crosswalk used
in the GSURv2 construction is accepted as the crosswalk for the MNL-
parquet merge. It is a user decision, not a Claude Code execution task.
The O7 sign-off request document is present (re-audit §10); the user
reviews it and issues the decision.

If the O7 sign-off is granted, the next Claude Code task is the MNL-
parquet rebuild authorization — a separate authorization memo that
gates the merge of the GSURv2 lookups into the FR_2015, FR_2016, and
FR_2017 MNL parquets.

If the O7 sign-off is deferred, no further data construction is
authorized until the sign-off is resolved.

In parallel (not blocking), post-construction cleanup — archival of the
untagged y2016 file and reference migration in canary/validation scripts
— may be authorized in a separate, narrow cleanup authorization after
the construction report and validation report are accepted.

M1-clean 2016 remains the active JMP baseline.

---

*Construction completed: 2026-05-20.*
*Authorization reference: `docs/JMP_GSURv2_multi_year_extension_construction_authorization_v1.md`*
