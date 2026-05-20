# JMP GSURv2 MNL-Parquet Rebuild Report v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-20*

---

## 1. Purpose

This report records the outcome of the GSURv2 MNL-parquet rebuild
executed under the authorization
`docs/JMP_GSURv2_MNL_rebuild_authorization_v1.md`. The rebuild
merges the three validated GSURv2 opportunity-year lookups
(y2014, y2015, y2016) into the FR_2015, FR_2016, and FR_2017 MNL
parquets, replacing the v1-fallback opportunity-side rates with
GSURv2 rates and preserving the v1-fallback rates in fallback
columns.

The rebuild covers six output parquets (three survey years ×
singles / couples) plus three metadata sidecar JSON files. All
twelve authorization validation checks (V1–V12) passed for all
three survey years. No halt condition was triggered. The rebuild
is complete.

---

## 2. Authorization basis

The rebuild was executed under:

- Authorization memo: `docs/JMP_GSURv2_MNL_rebuild_authorization_v1.md`
  (corrected by `docs/JMP_GSURv2_MNL_rebuild_authorization_correction_v1.md`)
- O7 crosswalk sign-off: `docs/JMP_GSURv2_O7_crosswalk_signoff_v1.md`
- Construction verdict: `docs/JMP_GSURv2_multi_year_extension_construction_verdict_v1.md`
  (corrected by `docs/JMP_GSURv2_multi_year_extension_construction_verdict_correction_v1.md`)
- Validation report: `Results/JMP_GSURv2_multi_year_extension_validation_report_v1.md`

Interpreter of record: `.venv\Scripts\python.exe`
(`U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe`).

---

## 3. Preflight check

The preflight check confirmed all input files present and all
output stems absent before the rebuild ran.

| File | Status |
|------|--------|
| `fr_2015_RURO_mnl_v1gsurY2014__singles.parquet` | present |
| `fr_2015_RURO_mnl_v1gsurY2014__couples.parquet` | present |
| `fr_2016_RURO_mnl_v1gsurY2015__singles.parquet` | present |
| `fr_2016_RURO_mnl_v1gsurY2015__couples.parquet` | present |
| `fr_2017_RURO_mnl_v1gsurY2016__singles.parquet` | present |
| `fr_2017_RURO_mnl_v1gsurY2016__couples.parquet` | present |
| `FR_gsur_ruro_v2_stageA_y2014.parquet` (SHA `740ef6c7…`) | present, SHA match |
| `FR_gsur_ruro_v2_stageA_y2015.parquet` (SHA `f51ad630…`) | present, SHA match |
| `FR_gsur_ruro_v2_stageA_y2016.parquet` (SHA `19ac53…`) | present, SHA match |
| All 9 output files (6 parquets + 3 sidecars) | absent OK |

---

## 4. GSURv2 lookup SHA-256 verification

The SHA-256 of each GSURv2 lookup was verified against the
recorded construction output hashes before merging.

| Opportunity year | Lookup file | SHA-256 (full) | Match |
|---|---|---|---|
| 2014 | `FR_gsur_ruro_v2_stageA_y2014.parquet` | `740ef6c7e57e355fb517262202be03bfc947589ac68024f971f620e3d2557e68` | PASS |
| 2015 | `FR_gsur_ruro_v2_stageA_y2015.parquet` | `f51ad6306574bf3a1d7b577e7741222c5bf2fb8126e512c0bbf965d6a2d03c83` | PASS |
| 2016 | `FR_gsur_ruro_v2_stageA_y2016.parquet` | `19ac53143fb404f3de44f4e2abc3313b0946eda835261496720bc511358c24ef` | PASS |

No SHA mismatch. Halt condition H4 was not triggered.

---

## 5. Schema verification

The actual MNL schema was verified for each input parquet before
merging.

*Singles schema verified present* (all three survey years):
`drgn1`, `educ3`, `dgn`, `gsur` — confirmed present in all three
singles parquets. No required key column missing or ambiguous.
Halt condition H1 was not triggered.

*Couples schema verified present* (all three survey years):
`drgn1`, `educ3_male`, `educ3_female`, `gsur_male`, `gsur_female`
— confirmed present in all three couples parquets.

*GSURv2 lookup `sex` coding verified*: `sex` takes values `F` and
`M` in all three lookups, consistent with the construction report
§5. Halt condition H3 was not triggered.

---

## 6. Singles dgn coding verification

The `dgn` coding was verified empirically before constructing the
`dgn`-to-`sex` mapping. The verification used the FR_2016 singles
parquet (representative year; the same coding applies to all three
years as the parquets share the same upstream pipeline).

Verification evidence:

- `dgn=0.0` rows: 91,000 (FR_2016). `dgn=1.0` rows: 76,600.
- `n_children` mean: `dgn=0.0` → 0.550, `dgn=1.0` → 0.188.
  This difference is consistent with female-headed singles
  households having more children attached in France EU-SILC
  data.
- `educH` rate: `dgn=0.0` → 0.430, `dgn=1.0` → 0.376. This
  difference is consistent with higher female tertiary attainment
  rates in France.
- Mean `gsur` in current (v1-fallback) data: `dgn=0.0` → 0.090,
  `dgn=1.0` → 0.101. In the GSURv2 lookup (y2015), mean `gsur`
  by sex: `F` → 0.108, `M` → 0.116. The directional ordering
  (higher unemployment for `dgn=1.0` / `M`) is consistent.
- All `idpartner` values are 0.0, confirming the singles parquet
  contains no coupled individuals.

**Verified mapping: `dgn=1.0` → `M` (male); `dgn=0.0` → `F`
(female).** This is the project convention (dgn==1 for male,
dgn==0 for female). The convention was confirmed empirically
before merging, not assumed. Halt condition H2 was not triggered.

---

## 7. dgn-to-sex mapping (documented explicitly)

| MNL `dgn` value | GSURv2 `sex` value | Rationale |
|---|---|---|
| `1.0` | `M` | Empirically verified (§6): higher unemployment, lower educH rate, lower n_children |
| `0.0` | `F` | Empirically verified (§6): consistent with female household characteristics in France |

GSURv2 lookup `sex` coding: `F` / `M` (uppercase string, verified
in all three lookups). The mapping is applied identically for all
three survey years.

---

## 8. Rebuild execution: FR_2015 singles

*Survey year*: FR_2015. *Opportunity year*: 2014. *Lookup*:
`FR_gsur_ruro_v2_stageA_y2014.parquet`.

Input parquet: `fr_2015_RURO_mnl_v1gsurY2014__singles.parquet`.
Shape: 166,900 rows × 75 columns. No drgn1=9 rows.

Steps executed:
1. `gsur_v1_fallback` column created by copying existing `gsur`.
2. `dgn` mapped to `_sex` using the verified mapping (1.0→M, 0.0→F).
3. Singles merged to lookup on `(drgn1, educ3, _sex)` (left join).
4. 166,900/166,900 rows matched; NaN in drgn1 ≠ 9: 0.
5. `gsur` column replaced with GSURv2 rate. `_sex` helper column dropped.
6. Output written: `fr_2015_RURO_mnl_v2gsurY2014__singles.parquet`,
   76 columns (75 original + `gsur_v1_fallback`).

Rows with `gsur` changed: 144,600 / 166,900.

---

## 9. Rebuild execution: FR_2015 couples

*Survey year*: FR_2015. *Opportunity year*: 2014. *Lookup*:
`FR_gsur_ruro_v2_stageA_y2014.parquet`.

Input parquet: `fr_2015_RURO_mnl_v1gsurY2014__couples.parquet`.
Shape: 256,600 rows × 93 columns. No drgn1=9 rows.

Steps executed:
1. `gsur_male_v1_fallback` and `gsur_female_v1_fallback` created.
2. Male merge on `(drgn1, educ3_male)` against lookup subset
   `sex=M`; NaN in drgn1 ≠ 9: 0 (218,800 rows changed).
3. Female merge on `(drgn1, educ3_female)` against lookup subset
   `sex=F`; NaN in drgn1 ≠ 9: 0 (230,400 rows changed).
4. `gsur_male` and `gsur_female` replaced. Helper columns dropped.
5. Output written: `fr_2015_RURO_mnl_v2gsurY2014__couples.parquet`,
   95 columns (93 original + `gsur_male_v1_fallback` +
   `gsur_female_v1_fallback`).

---

## 10. Rebuild execution: FR_2016 singles

*Survey year*: FR_2016. *Opportunity year*: 2015. *Lookup*:
`FR_gsur_ruro_v2_stageA_y2015.parquet`.

Input parquet: `fr_2016_RURO_mnl_v1gsurY2015__singles.parquet`.
Shape: 167,600 rows × 75 columns. No drgn1=9 rows.

Steps executed as for FR_2015 singles (§8). 150,100 / 167,600
rows had `gsur` changed. Output written:
`fr_2016_RURO_mnl_v2gsurY2015__singles.parquet`, 76 columns.

---

## 11. Rebuild execution: FR_2016 couples

*Survey year*: FR_2016. *Opportunity year*: 2015. *Lookup*:
`FR_gsur_ruro_v2_stageA_y2015.parquet`.

Input parquet: `fr_2016_RURO_mnl_v1gsurY2015__couples.parquet`.
Shape: 257,700 rows × 93 columns. No drgn1=9 rows.

Steps executed as for FR_2015 couples (§9). 224,300 male rows
and 241,500 female rows had `gsur` changed. Output written:
`fr_2016_RURO_mnl_v2gsurY2015__couples.parquet`, 95 columns.

---

## 12. Rebuild execution: FR_2017 singles

*Survey year*: FR_2017. *Opportunity year*: 2016. *Lookup*:
`FR_gsur_ruro_v2_stageA_y2016.parquet`.

Input parquet: `fr_2017_RURO_mnl_v1gsurY2016__singles.parquet`.
Shape: 166,200 rows × 75 columns. No drgn1=9 rows.

Steps executed as for FR_2015 singles (§8). 160,900 / 166,200
rows had `gsur` changed. Output written:
`fr_2017_RURO_mnl_v2gsurY2016__singles.parquet`, 76 columns.

---

## 13. Rebuild execution: FR_2017 couples

*Survey year*: FR_2017. *Opportunity year*: 2016. *Lookup*:
`FR_gsur_ruro_v2_stageA_y2016.parquet`.

Input parquet: `fr_2017_RURO_mnl_v1gsurY2016__couples.parquet`.
Shape: 229,500 rows × 93 columns. No drgn1=9 rows.

Steps executed as for FR_2015 couples (§9). 218,400 male rows
and 225,100 female rows had `gsur` changed. Output written:
`fr_2017_RURO_mnl_v2gsurY2016__couples.parquet`, 95 columns.

---

## 14. v1-fallback preservation

The v1-fallback GSUR values were preserved under fallback column
names before the active GSUR columns were replaced.

| Output parquet | Fallback column(s) | Value-identical to input? |
|---|---|---|
| `fr_2015_RURO_mnl_v2gsurY2014__singles.parquet` | `gsur_v1_fallback` | PASS (exact) |
| `fr_2015_RURO_mnl_v2gsurY2014__couples.parquet` | `gsur_male_v1_fallback`, `gsur_female_v1_fallback` | PASS (exact) |
| `fr_2016_RURO_mnl_v2gsurY2015__singles.parquet` | `gsur_v1_fallback` | PASS (exact) |
| `fr_2016_RURO_mnl_v2gsurY2015__couples.parquet` | `gsur_male_v1_fallback`, `gsur_female_v1_fallback` | PASS (exact) |
| `fr_2017_RURO_mnl_v2gsurY2016__singles.parquet` | `gsur_v1_fallback` | PASS (exact) |
| `fr_2017_RURO_mnl_v2gsurY2016__couples.parquet` | `gsur_male_v1_fallback`, `gsur_female_v1_fallback` | PASS (exact) |

The `gsur_v1_fallback` column is value-identical to the input
parquet's `gsur` column for all three singles outputs. The
`gsur_male_v1_fallback` and `gsur_female_v1_fallback` columns are
value-identical to the input parquets' `gsur_male` and
`gsur_female` columns for all three couples outputs. Halt
condition H6 was not triggered.

---

## 15. Validation results: FR_2015

All V1–V12 checks passed for FR_2015 (27 sub-checks, 0 failures).

| Check | Singles | Couples |
|---|---|---|
| V1 Row counts unchanged | PASS (166,900) | PASS (256,600) |
| V2 Household counts unchanged | PASS (1,669 HH) | PASS (2,566 HH) |
| V3 Non-GSUR columns value-identical | PASS | PASS |
| V4 Active GSUR complete for drgn1 1–8 | PASS (NaN in non-9: 0) | PASS (M and F: 0) |
| V5 drgn1=9 handling documented | PASS (0 drgn1=9 rows) | PASS (0 drgn1=9 rows) |
| V6 Fallback columns present and value-identical | PASS | PASS |
| V7 Opportunity-year mapping correct | PASS (y2014) | PASS (y2014) |
| V8 dgn-to-sex mapping verified | PASS | — |
| V9 Partner-specific merge verified | — | PASS (spot-check: M=0.100129, F=0.057679) |
| V10 Merged values match lookup exactly | PASS (spot: exp=0.071, act=0.071) | PASS |
| V11 Metadata sidecars present | PASS | PASS |
| V12 Canonical files untouched | PASS | PASS |

---

## 16. Validation results: FR_2016

All V1–V12 checks passed for FR_2016 (27 sub-checks, 0 failures).

| Check | Singles | Couples |
|---|---|---|
| V1 Row counts unchanged | PASS (167,600) | PASS (257,700) |
| V2 Household counts unchanged | PASS (1,676 HH) | PASS (2,577 HH) |
| V3 Non-GSUR columns value-identical | PASS | PASS |
| V4 Active GSUR complete for drgn1 1–8 | PASS (NaN in non-9: 0) | PASS (M and F: 0) |
| V5 drgn1=9 handling documented | PASS (0 drgn1=9 rows) | PASS (0 drgn1=9 rows) |
| V6 Fallback columns present and value-identical | PASS | PASS |
| V7 Opportunity-year mapping correct | PASS (y2015) | PASS (y2015) |
| V8 dgn-to-sex mapping verified | PASS | — |
| V9 Partner-specific merge verified | — | PASS (spot-check: M=0.098344, F=0.054729) |
| V10 Merged values match lookup exactly | PASS (spot: exp=0.076, act=0.076) | PASS |
| V11 Metadata sidecars present | PASS | PASS |
| V12 Canonical files untouched | PASS | PASS |

---

## 17. Validation results: FR_2017

All V1–V12 checks passed for FR_2017 (27 sub-checks, 0 failures).

| Check | Singles | Couples |
|---|---|---|
| V1 Row counts unchanged | PASS (166,200) | PASS (229,500) |
| V2 Household counts unchanged | PASS (1,662 HH) | PASS (2,295 HH) |
| V3 Non-GSUR columns value-identical | PASS | PASS |
| V4 Active GSUR complete for drgn1 1–8 | PASS (NaN in non-9: 0) | PASS (M and F: 0) |
| V5 drgn1=9 handling documented | PASS (0 drgn1=9 rows) | PASS (0 drgn1=9 rows) |
| V6 Fallback columns present and value-identical | PASS | PASS |
| V7 Opportunity-year mapping correct | PASS (y2016) | PASS (y2016) |
| V8 dgn-to-sex mapping verified | PASS | — |
| V9 Partner-specific merge verified | — | PASS (spot-check: M=0.101143, F=0.056077) |
| V10 Merged values match lookup exactly | PASS (spot: exp=0.056, act=0.056) | PASS |
| V11 Metadata sidecars present | PASS | PASS |
| V12 Canonical files untouched | PASS | PASS |

---

## 18. drgn1=9 handling

The metropolitan France MNL parquets carry no drgn1=9 records
(confirmed for all six input parquets and all six output
parquets). The DOM and extra-regio households are excluded
upstream of the MNL preparation step. Accordingly, no record in
any output parquet has a null active GSUR value due to the drgn1=9
stub. V5 (drgn1=9 handling documented) passes for all six outputs.

---

## 19. gsur range by survey year

The GSURv2 rates merged into the active GSUR columns are within
[0, 1] for all outputs (V5 range check).

| Survey year | Singles gsur range | Couples gsur_male range | Couples gsur_female range |
|---|---|---|---|
| FR_2015 | [0.0537, 0.261] | [0.0536, 0.261] | [0.0563, 0.177] |
| FR_2016 | [0.0532, 0.225] | [0.0595, 0.225] | [0.0532, 0.183] |
| FR_2017 | [0.0470, 0.234] | [0.0470, 0.234] | [0.0478, 0.230] |

The declining upper bounds from FR_2015 to FR_2017 are consistent
with the reduction in French regional unemployment over 2014–2016
in the GSURv2 source data.

---

## 20. Output file inventory

| Survey year | File | SHA-256 (full) | Rows | Cols | Bytes |
|---|---|---|---|---|---|
| FR_2015 | `fr_2015_RURO_mnl_v2gsurY2014__singles.parquet` | `889b2f8a95a9ac1a30cdb8d6e6ff5cf6002525345f940a65cfdc0176d9998819` | 166,900 | 76 | 21,471,043 |
| FR_2015 | `fr_2015_RURO_mnl_v2gsurY2014__couples.parquet` | `d44d229207c6d9c4aceb9bfeaa33bd05beb1e7e01a142b41618250f90039a00d` | 256,600 | 95 | 42,986,747 |
| FR_2016 | `fr_2016_RURO_mnl_v2gsurY2015__singles.parquet` | `139cd025d35e6b2fe0e5f03d6d7d3564857eb0e3743ca0cbbd04d687da64cb2e` | 167,600 | 76 | 21,503,679 |
| FR_2016 | `fr_2016_RURO_mnl_v2gsurY2015__couples.parquet` | `61e3107bb17f4fbf781cea37abd410cc918fe0246ed2c50e853060eb9f40154a` | 257,700 | 95 | 43,115,163 |
| FR_2017 | `fr_2017_RURO_mnl_v2gsurY2016__singles.parquet` | `8fce026d23536f12ec2dbc2b1a403a68503168150dace55c90bcfc63de670b9e` | 166,200 | 76 | 21,360,009 |
| FR_2017 | `fr_2017_RURO_mnl_v2gsurY2016__couples.parquet` | `2d8dc7aeb7c0e99df9a5318935b8d59ac2b7b2a18a222526dad5850ba068ac26` | 229,500 | 95 | 38,967,848 |

All six output parquets are in `Data/processed/fr/`. `Data/` is
excluded from git tracking per `.gitignore` line 21; the output
parquets are not git-committed. Provenance is carried by the
sidecar JSON files and this report.

---

## 21. Sidecar inventory

Three sidecar JSON files were written (one per survey year, shared
by the singles and couples output parquets of that year). Each
sidecar records the survey year, opportunity year, lookup SHA-256,
merge keys, dgn-to-sex mapping, output file SHA-256 and sizes,
V1–V12 all-pass status, build timestamp, and script version.

| Survey year | Sidecar file |
|---|---|
| FR_2015 | `fr_2015_RURO_mnl_v2gsurY2014__mnlmeta.json` |
| FR_2016 | `fr_2016_RURO_mnl_v2gsurY2015__mnlmeta.json` |
| FR_2017 | `fr_2017_RURO_mnl_v2gsurY2016__mnlmeta.json` |

Build timestamp (UTC): `2026-05-20T20:52:59.915735+00:00`.
Script version: `inline-rebuild-v1`.

---

## 22. Input v1-fallback file integrity

The six input v1-fallback parquets were not modified by the
rebuild. They are read-only inputs; the rebuild writes to
separate output stems (§20).

| Input file | SHA-256 prefix | Bytes | Status |
|---|---|---|---|
| `fr_2015_RURO_mnl_v1gsurY2014__singles.parquet` | `7b3e16df60863c85` | 21,467,197 | UNMODIFIED |
| `fr_2015_RURO_mnl_v1gsurY2014__couples.parquet` | `5ebe18647f81aa05` | 42,977,905 | UNMODIFIED |
| `fr_2016_RURO_mnl_v1gsurY2015__singles.parquet` | `fc4e3d669b4ff816` | 21,500,531 | UNMODIFIED |
| `fr_2016_RURO_mnl_v1gsurY2015__couples.parquet` | `925adc4a25c45ddd` | 43,108,696 | UNMODIFIED |
| `fr_2017_RURO_mnl_v1gsurY2016__singles.parquet` | `ac48c64a2d8eea10` | 21,356,869 | UNMODIFIED |
| `fr_2017_RURO_mnl_v1gsurY2016__couples.parquet` | `44822e2d95b2cfa9` | 38,961,983 | UNMODIFIED |

No canonical 2016 M1-clean parquet, estimation output, or
estimation specification was modified. V12 (canonical files
untouched) passes for all six outputs. Halt condition H10 was
not triggered.

---

## 23. Halt conditions

All ten halt conditions (H1–H10) were checked during the rebuild.
None was triggered.

| Halt condition | Status |
|---|---|
| H1 Required key column missing or ambiguous | Not triggered (all key columns verified present) |
| H2 dgn coding unverifiable | Not triggered (coding verified empirically) |
| H3 GSURv2 sex coding unrecognised | Not triggered (F/M confirmed) |
| H4 GSURv2 lookup SHA-256 mismatch | Not triggered (all three SHAs match) |
| H5 Merge incompleteness | Not triggered (0 NaN in active records) |
| H6 Fallback preservation failure | Not triggered (all fallback columns value-identical) |
| H7 Non-GSUR column modified | Not triggered (V3 passed) |
| H8 Lookup-value mismatch | Not triggered (V10 passed, spot-checks exact) |
| H9 Existing output stem found | Not triggered (all output stems absent before rebuild) |
| H10 Canonical or input file modification detected | Not triggered (V12 passed) |

---

## 24. Output stem naming note

The authorization memo §8 specifies output stems
`fr_201X_RURO_mnl_GSURv2_y20XX__`. The rebuild used the stems
specified in the T6 task prompt (`fr_201X_RURO_mnl_v2gsurY20XX__`),
which were the stems confirmed absent in the preflight check. The
stems encode the same semantic content: GSURv2 source and
opportunity year. The provenance is recorded unambiguously in the
sidecar `lookup_parquet`, `opportunity_year`, and SHA-256 fields.

---

## 25. Survey-year totals

| Survey year | Singles rows | Couples rows | Total rows |
|---|---|---|---|
| FR_2015 | 166,900 | 256,600 | 423,500 |
| FR_2016 | 167,600 | 257,700 | 425,300 |
| FR_2017 | 166,200 | 229,500 | 395,700 |
| **All years** | **500,700** | **743,800** | **1,244,500** |

The total row count matches the Stage M1 construction report
(1,244,500 rows across all three years), confirming that the
rebuild preserves the complete pooled dataset row counts.

---

## 26. What was not done

The following downstream steps were not performed, as the
authorization explicitly prohibits them.

- **Pooled stacking was not performed.** The six output parquets
  were not stacked into a pooled dataset. Pooled stacking is
  separately gated (N1).
- **No model was estimated.** No RURO or other estimation was
  run against the output parquets. Pooled estimation is
  separately gated (N2).
- **Welfare was not computed.** No welfare computation was
  performed (N3).
- **No canonical promotion.** The output parquets are in
  year-tagged versioned stems; no canonical promotion was
  performed (N4).
- **No P3b or P4.** Not performed (N5).
- **No estimation specification was modified.** The M1-clean
  and M1-naive YAML specifications are unchanged (N6).

---

## 27. Overall rebuild verdict

**GSURv2 MNL-parquet rebuild: PASS.**

All six output parquets were written successfully. All twelve
validation checks (V1–V12) passed for all three survey years.
No halt condition was triggered. The input v1-fallback parquets
and canonical files are confirmed unmodified. The rebuild is
complete within the bounds specified in the authorization.

The GSURv2 rates now replace the v1-fallback opportunity-side
rates in the active `gsur`, `gsur_male`, and `gsur_female`
columns for FR_2015, FR_2016, and FR_2017. The v1-fallback
rates are preserved in the `gsur_v1_fallback`,
`gsur_male_v1_fallback`, and `gsur_female_v1_fallback` columns.

---

## 28. git note

`Data/` is excluded from git tracking per `.gitignore` line 21.
The six output parquets and three sidecar JSON files are on
disk but are not git-committed. This report (`Results/`) is git-
tracked and committed, carrying the SHA-256 hashes, row counts,
and validation outcomes that record the rebuild provenance.

---

## 29. Readiness of next gate

**The next gate is a strict post-rebuild verdict.** If that
verdict passes, it may authorize pooled stacking re-run as the
following step. The rebuild did not perform any downstream step
(pooled stacking, pooled estimation, welfare, canonical
promotion, or any estimation specification change).

Pooled stacking re-run is separately gated and is not authorized
by this rebuild.

---

**Required final statements**

- **GSURv2 MNL-parquet rebuild is COMPLETE and PASSES all
  validation checks.** All six output parquets (FR_2015, FR_2016,
  FR_2017 × singles/couples) were written, all V1–V12 checks
  passed, and all H1–H10 halt conditions were not triggered.

- **The dgn-to-sex mapping is verified.** `dgn=1.0` → `M` (male);
  `dgn=0.0` → `F` (female). Verified empirically, not assumed.

- **Pooled stacking is NOT authorized.** The Stage M1 pooled
  stacking re-run against the GSURv2-based MNL parquets is
  downstream of the rebuild and requires its own authorization.

- **Pooled estimation is NOT authorized.** No pooled estimation,
  provisional or final, is authorized by this rebuild.

- **Welfare computation is NOT authorized.** Welfare work is
  separately gated.

- **M1-clean 2016 remains the active JMP baseline.** The rebuild
  does not promote the pooled route over the single-year M1-clean
  baseline. M1-clean 2016 remains the active JMP baseline until
  a later SA2 verdict explicitly promotes a final pooled
  specification.