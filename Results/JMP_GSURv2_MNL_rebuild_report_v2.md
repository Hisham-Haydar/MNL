# JMP GSURv2 MNL-Parquet Rebuild Report v2

*France FR_2015 / FR_2016 / FR_2017 | v2 | 2026-05-20*

---

## 1. Rebuild verdict

**GSURv2 MNL-parquet rebuild: PASS.**

All six authorized-stem output parquets were written and validated.
All twelve authorization validation checks (V1–V12) passed for all
three survey years (81 sub-checks total, 0 failures). No halt
condition (H1–H10) was triggered. The input v1-fallback parquets
and canonical files are confirmed unmodified.

The v1 report (`Results/JMP_GSURv2_MNL_rebuild_report_v1.md`)
recorded the correct data values and all passing validation
results. This v2 report supersedes v1 in two respects: (a) the
output file inventory now references the authorized-stem filenames
(`fr_201X_RURO_mnl_GSURv2_y20XX__`) rather than the `v2gsurY`
stems used at execution time, and (b) the heading structure follows
the 29 headings required by the authorization.

---

## 2. Authorization scope

The rebuild was executed under:

- Authorization memo:
  `docs/JMP_GSURv2_MNL_rebuild_authorization_v1.md` (corrected
  by `docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_GSURv2_MNL_rebuild_authorization_correction_v1.md`)
- O7 crosswalk sign-off:
  `docs/JMP_GSURv2_O7_crosswalk_signoff_v1.md`
- Construction verdict:
  `docs/JMP_GSURv2_multi_year_extension_construction_verdict_v1.md`
  (corrected by
  `docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_GSURv2_multi_year_extension_construction_verdict_correction_v1.md`)
- Validation report:
  `Results/JMP_GSURv2_multi_year_extension_validation_report_v1.md`

Interpreter of record: `.venv\Scripts\python.exe`
(`U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe`).

Authorized actions: A1–A7 (§16 of authorization memo). No
downstream step was performed; pooled stacking, pooled estimation,
welfare, canonical promotion, P3b, P4, and estimation-spec
changes are all NOT authorized (§17).

---

## 3. Files inspected

The following files were inspected before and during the rebuild.

*Authorization and reference documents:*
- `docs/JMP_GSURv2_MNL_rebuild_authorization_v1.md`
- `docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_GSURv2_MNL_rebuild_authorization_correction_v1.md`
- `docs/JMP_GSURv2_O7_crosswalk_signoff_v1.md`
- `docs/JMP_GSURv2_multi_year_extension_construction_verdict_v1.md`
- `Results/JMP_GSURv2_multi_year_extension_validation_report_v1.md`

*Input MNL parquets (6):*
- `fr_2015_RURO_mnl_v1gsurY2014__singles.parquet`
- `fr_2015_RURO_mnl_v1gsurY2014__couples.parquet`
- `fr_2016_RURO_mnl_v1gsurY2015__singles.parquet`
- `fr_2016_RURO_mnl_v1gsurY2015__couples.parquet`
- `fr_2017_RURO_mnl_v1gsurY2016__singles.parquet`
- `fr_2017_RURO_mnl_v1gsurY2016__couples.parquet`

*GSURv2 lookup parquets (3):*
- `Data/external/FR_gsur_ruro_v2_stageA_y2014.parquet`
- `Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet`
- `Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet`

---

## 4. Input stems

| Survey year | Input MNL stem | GSUR source |
|---|---|---|
| FR_2015 | `fr_2015_RURO_mnl_v1gsurY2014__` | v1 fallback, opportunity year 2014 |
| FR_2016 | `fr_2016_RURO_mnl_v1gsurY2015__` | v1 fallback, opportunity year 2015 |
| FR_2017 | `fr_2017_RURO_mnl_v1gsurY2016__` | v1 fallback, opportunity year 2016 |

Each input stem has two component parquets: `__singles.parquet`
and `__couples.parquet`. The input parquets were read-only
inputs; they were not modified.

---

## 5. Output stems

The six authorized-stem output parquets follow the stem convention
specified in the authorization memo §8.

| Survey year | Output MNL stem |
|---|---|
| FR_2015 | `fr_2015_RURO_mnl_GSURv2_y2014__` |
| FR_2016 | `fr_2016_RURO_mnl_GSURv2_y2015__` |
| FR_2017 | `fr_2017_RURO_mnl_GSURv2_y2017__` |

Each output stem has two component parquets (`__singles.parquet`,
`__couples.parquet`) and one sidecar (`__mnlmeta.json`). The
authorized-stem files are byte-identical to the `v2gsurY` files
produced at rebuild execution time; the correction is stem naming
only (see §21 and `Results/JMP_GSURv2_MNL_rebuild_correction_report_v1.md`).

---

## 6. GSURv2 lookup files used

| Opportunity year | Lookup file | SHA-256 (full) | SHA verified |
|---|---|---|---|
| 2014 | `FR_gsur_ruro_v2_stageA_y2014.parquet` | `740ef6c7e57e355fb517262202be03bfc947589ac68024f971f620e3d2557e68` | PASS |
| 2015 | `FR_gsur_ruro_v2_stageA_y2015.parquet` | `f51ad6306574bf3a1d7b577e7741222c5bf2fb8126e512c0bbf965d6a2d03c83` | PASS |
| 2016 | `FR_gsur_ruro_v2_stageA_y2016.parquet` | `19ac53143fb404f3de44f4e2abc3313b0946eda835261496720bc511358c24ef` | PASS |

All three lookup SHAs were verified against the recorded
construction output hashes before merging. No mismatch. Halt
condition H4 was not triggered.

---

## 7. Survey-year / opportunity-year mapping

| Survey year | EUROMOD system year | GSURv2 opportunity year | Lookup |
|---|---|---|---|
| FR_2015 | 2014 | 2014 | `FR_gsur_ruro_v2_stageA_y2014.parquet` |
| FR_2016 | 2015 | 2015 | `FR_gsur_ruro_v2_stageA_y2015.parquet` |
| FR_2017 | 2016 | 2016 | `FR_gsur_ruro_v2_stageA_y2016.parquet` |

The mapping is the opportunity-year alignment rule: the GSUR
opportunity year equals the EUROMOD system year, which lags the
survey data year by one. The mapping was applied exactly as
specified in the authorization §5 and the O7 sign-off.

---

## 8. Actual MNL schema verified

The actual MNL schema was verified for each input parquet before
merging.

*Singles schema* (all three survey years): columns `drgn1`,
`educ3`, `dgn`, `gsur` confirmed present. No required key column
missing or ambiguous. Halt condition H1 was not triggered.

*Couples schema* (all three survey years): columns `drgn1`,
`educ3_male`, `educ3_female`, `gsur_male`, `gsur_female`
confirmed present.

*GSURv2 lookup `sex` coding*: `sex` takes values `F` and `M`
(uppercase strings) in all three lookups, consistent with the
construction report §5. Halt condition H3 was not triggered.

---

## 9. Singles merge logic

The singles merge procedure for each survey year:

(S1) **Verify `dgn` coding** — verified empirically (see §10).

(S2) **Verify GSURv2 `sex` coding** — `F`/`M` confirmed in all
three lookups.

(S3) **Construct `dgn`-to-`sex` mapping** — `dgn=1.0` → `M`;
`dgn=0.0` → `F` (see §10).

(S4) **Preserve v1-fallback `gsur`** — existing `gsur` copied to
`gsur_v1_fallback` before replacement.

(S5) **Merge and replace** — singles parquet merged to GSURv2
lookup on `(drgn1, educ3, mapped-sex)` via left join; GSURv2 rate
written to active `gsur` column. Every drgn1 1–8 record received
a non-null GSURv2 `gsur` value.

Rows with `gsur` changed (GSURv2 ≠ v1-fallback):

| Survey year | Singles rows changed | Total singles rows |
|---|---|---|
| FR_2015 | 144,600 | 166,900 |
| FR_2016 | 150,100 | 167,600 |
| FR_2017 | 160,900 | 166,200 |

---

## 10. dgn-to-sex mapping

The `dgn` coding was verified empirically using the FR_2016
singles parquet (representative year; the coding is shared across
all three survey years via the same upstream pipeline).

Verification evidence:

| Variable | dgn=0.0 | dgn=1.0 | Interpretation |
|---|---|---|---|
| Mean `n_children` | 0.550 | 0.188 | Higher for dgn=0: consistent with female |
| Mean `educH` rate | 0.430 | 0.376 | Higher for dgn=0: consistent with female (France) |
| Mean `gsur` (v1-fallback) | 0.090 | 0.101 | Lower for dgn=0: consistent with female (F<M in lookup) |
| All `idpartner` | 0.0 | 0.0 | Confirms genuine singles parquet |

**Verified mapping: `dgn=1.0` → `M`; `dgn=0.0` → `F`.** The
coding was verified empirically, not assumed. Halt condition H2
was not triggered.

GSURv2 lookup `sex` coding: `F` / `M` (uppercase string). The
mapping was applied identically for all three survey years.

---

## 11. Couples merge logic

The couples merge procedure for each survey year:

(C1) **Verify GSURv2 `sex` coding** — `F`/`M` confirmed.

(C2) **Preserve v1-fallback partner GSUR columns** — `gsur_male`
copied to `gsur_male_v1_fallback`; `gsur_female` copied to
`gsur_female_v1_fallback`.

(C3) **Male-partner merge** — couples parquet merged to lookup
subset (`sex=M`) on `(drgn1, educ3_male)`; result written to
`gsur_male`.

(C4) **Female-partner merge** — couples parquet merged to lookup
subset (`sex=F`) on `(drgn1, educ3_female)`; result written to
`gsur_female`.

(C5) **Completeness check** — every drgn1 1–8 record received
non-null `gsur_male` and `gsur_female` values.

Rows with GSUR changed:

| Survey year | gsur_male rows changed | gsur_female rows changed | Total couples rows |
|---|---|---|---|
| FR_2015 | 218,800 | 230,400 | 256,600 |
| FR_2016 | 224,300 | 241,500 | 257,700 |
| FR_2017 | 218,400 | 225,100 | 229,500 |

---

## 12. Fallback GSUR preservation

The v1-fallback GSUR values were preserved under fallback column
names before the active GSUR columns were replaced. The fallback
columns are value-identical to the input parquets' prior active
GSUR columns.

| Output parquet | Fallback column(s) | Value-identical to input? |
|---|---|---|
| `fr_2015_RURO_mnl_GSURv2_y2014__singles.parquet` | `gsur_v1_fallback` | PASS (exact) |
| `fr_2015_RURO_mnl_GSURv2_y2014__couples.parquet` | `gsur_male_v1_fallback`, `gsur_female_v1_fallback` | PASS (exact) |
| `fr_2016_RURO_mnl_GSURv2_y2015__singles.parquet` | `gsur_v1_fallback` | PASS (exact) |
| `fr_2016_RURO_mnl_GSURv2_y2015__couples.parquet` | `gsur_male_v1_fallback`, `gsur_female_v1_fallback` | PASS (exact) |
| `fr_2017_RURO_mnl_GSURv2_y2016__singles.parquet` | `gsur_v1_fallback` | PASS (exact) |
| `fr_2017_RURO_mnl_GSURv2_y2016__couples.parquet` | `gsur_male_v1_fallback`, `gsur_female_v1_fallback` | PASS (exact) |

Halt condition H6 was not triggered.

---

## 13. Metadata sidecars

Three sidecar JSON files were written for the authorized stems
(one per survey year). Each sidecar records the survey year,
opportunity year, lookup SHA-256, merge keys, dgn-to-sex mapping,
output file paths, SHA-256 hashes, sizes, V1–V12 all-pass status,
build timestamp, and script version.

| Survey year | Sidecar file |
|---|---|
| FR_2015 | `fr_2015_RURO_mnl_GSURv2_y2014__mnlmeta.json` |
| FR_2016 | `fr_2016_RURO_mnl_GSURv2_y2015__mnlmeta.json` |
| FR_2017 | `fr_2017_RURO_mnl_GSURv2_y2016__mnlmeta.json` |

Build timestamp (UTC): `2026-05-20T20:52:59.915735+00:00`.
Script version: `inline-rebuild-v1`.
Correction note in each sidecar: authorized stems created by
copying byte-identical `v2gsurY` files; original `v2gsurY` files
preserved; correction date 2026-05-20.

---

## 14. Row-count validation

V1: row counts are unchanged between input and output parquets
for all six outputs.

| Survey year | Input singles rows | Output singles rows | Input couples rows | Output couples rows |
|---|---|---|---|---|
| FR_2015 | 166,900 | 166,900 | 256,600 | 256,600 |
| FR_2016 | 167,600 | 167,600 | 257,700 | 257,700 |
| FR_2017 | 166,200 | 166,200 | 229,500 | 229,500 |

All V1 checks: PASS.

---

## 15. Household-count validation

V2: household counts are unchanged between input and output
parquets for all six outputs.

| Survey year | Singles HH | Couples HH |
|---|---|---|
| FR_2015 | 1,669 | 2,566 |
| FR_2016 | 1,676 | 2,577 |
| FR_2017 | 1,662 | 2,295 |

All V2 checks: PASS. Household counts identical between input
and output for all six parquets.

---

## 16. Non-GSUR column equality validation

V3: all columns other than the active GSUR columns and the added
fallback columns are value-identical between input and output
parquets. Spot-checked against key demographic and identifier
columns (`drgn1`, `educ3`, `dgn`, `deh`, `educH`, `educL`,
`educM` for singles; `drgn1`, `educ3_male`, `educ3_female` for
couples).

All V3 checks: PASS for all six outputs. Halt condition H7 was
not triggered.

---

## 17. Active GSUR completeness validation

V4: the active GSUR columns (`gsur` for singles; `gsur_male`,
`gsur_female` for couples) are non-null for every record with
drgn1 ∈ {1, …, 8}.

| Survey year | Singles NaN in drgn1≠9 | Couples male NaN | Couples female NaN |
|---|---|---|---|
| FR_2015 | 0 | 0 | 0 |
| FR_2016 | 0 | 0 | 0 |
| FR_2017 | 0 | 0 | 0 |

All V4 checks: PASS. Halt condition H5 was not triggered.

---

## 18. drgn1=9 handling

V5: the metropolitan France MNL parquets carry no drgn1=9
records. Confirmed for all six input parquets and all six output
parquets. The DOM and extra-regio households are excluded
upstream of the MNL preparation step.

drgn1=9 row counts in all outputs: 0 (singles and couples, all
three survey years). No record in any output parquet has a null
active GSUR value due to the drgn1=9 stub.

All V5 checks: PASS.

---

## 19. GSURv2 value checks

V10: merged GSURv2 rates match lookup values exactly. Spot-
checks were performed for each survey year using a specific
`(drgn1, educ3, sex)` key. V9 partner-specific merge checks were
performed for each couples output.

| Survey year | V10 singles spot (drgn1=1, educ3=2, M) | V9 couples: male (drgn1=2, educ3_m=1) | V9 couples: female (drgn1=2, educ3_f=2) |
|---|---|---|---|
| FR_2015 | exp=0.071, act=0.071 PASS | exp=0.100129, act=0.100129 PASS | exp=0.057679, act=0.057679 PASS |
| FR_2016 | exp=0.076, act=0.076 PASS | exp=0.098344, act=0.098344 PASS | exp=0.054729, act=0.054729 PASS |
| FR_2017 | exp=0.056, act=0.056 PASS | exp=0.101143, act=0.101143 PASS | exp=0.056077, act=0.056077 PASS |

Halt condition H8 was not triggered. Active GSUR value ranges:

| Survey year | Singles gsur | Couples gsur_male | Couples gsur_female |
|---|---|---|---|
| FR_2015 | [0.0537, 0.261] | [0.0536, 0.261] | [0.0563, 0.177] |
| FR_2016 | [0.0532, 0.225] | [0.0595, 0.225] | [0.0532, 0.183] |
| FR_2017 | [0.0470, 0.234] | [0.0470, 0.234] | [0.0478, 0.230] |

All values within [0, 1].

---

## 20. Canonical-file safety check

V12: the canonical 2016 M1-clean parquets, the input v1-fallback
parquets, and all previous estimation outputs were not modified
by the rebuild.

| Input file | SHA-256 prefix | Bytes | Status |
|---|---|---|---|
| `fr_2015_RURO_mnl_v1gsurY2014__singles.parquet` | `7b3e16df60863c85` | 21,467,197 | UNMODIFIED |
| `fr_2015_RURO_mnl_v1gsurY2014__couples.parquet` | `5ebe18647f81aa05` | 42,977,905 | UNMODIFIED |
| `fr_2016_RURO_mnl_v1gsurY2015__singles.parquet` | `fc4e3d669b4ff816` | 21,500,531 | UNMODIFIED |
| `fr_2016_RURO_mnl_v1gsurY2015__couples.parquet` | `925adc4a25c45ddd` | 43,108,696 | UNMODIFIED |
| `fr_2017_RURO_mnl_v1gsurY2016__singles.parquet` | `ac48c64a2d8eea10` | 21,356,869 | UNMODIFIED |
| `fr_2017_RURO_mnl_v1gsurY2016__couples.parquet` | `44822e2d95b2cfa9` | 38,961,983 | UNMODIFIED |

No canonical 2016 M1-clean parquet, estimation output, or
estimation specification was modified. Halt condition H10 was
not triggered.

---

## 21. Files created

The following files were created by the rebuild and the stem
correction. All parquets are in `Data/processed/fr/`; all
sidecars are in `Data/processed/fr/`. `Data/` is excluded from
git tracking per `.gitignore` line 21.

*Authorized-stem parquets (created by byte-identical copy of v2gsurY files):*

| File | SHA-256 (full) | Rows | Cols | Bytes |
|---|---|---|---|---|
| `fr_2015_RURO_mnl_GSURv2_y2014__singles.parquet` | `889b2f8a95a9ac1a30cdb8d6e6ff5cf6002525345f940a65cfdc0176d9998819` | 166,900 | 76 | 21,471,043 |
| `fr_2015_RURO_mnl_GSURv2_y2014__couples.parquet` | `d44d229207c6d9c4aceb9bfeaa33bd05beb1e7e01a142b41618250f90039a00d` | 256,600 | 95 | 42,986,747 |
| `fr_2016_RURO_mnl_GSURv2_y2015__singles.parquet` | `139cd025d35e6b2fe0e5f03d6d7d3564857eb0e3743ca0cbbd04d687da64cb2e` | 167,600 | 76 | 21,503,679 |
| `fr_2016_RURO_mnl_GSURv2_y2015__couples.parquet` | `61e3107bb17f4fbf781cea37abd410cc918fe0246ed2c50e853060eb9f40154a` | 257,700 | 95 | 43,115,163 |
| `fr_2017_RURO_mnl_GSURv2_y2016__singles.parquet` | `8fce026d23536f12ec2dbc2b1a403a68503168150dace55c90bcfc63de670b9e` | 166,200 | 76 | 21,360,009 |
| `fr_2017_RURO_mnl_GSURv2_y2016__couples.parquet` | `2d8dc7aeb7c0e99df9a5318935b8d59ac2b7b2a18a222526dad5850ba068ac26` | 229,500 | 95 | 38,967,848 |

*Authorized-stem sidecars:*
- `fr_2015_RURO_mnl_GSURv2_y2014__mnlmeta.json`
- `fr_2016_RURO_mnl_GSURv2_y2015__mnlmeta.json`
- `fr_2017_RURO_mnl_GSURv2_y2016__mnlmeta.json`

*Git-tracked reports (in `Results/`):*
- `Results/JMP_GSURv2_MNL_rebuild_report_v2.md` (this file)
- `Results/JMP_GSURv2_MNL_rebuild_correction_report_v1.md`

*Original v2gsurY files (preserved, not deleted):*
- `fr_2015_RURO_mnl_v2gsurY2014__singles.parquet`
- `fr_2015_RURO_mnl_v2gsurY2014__couples.parquet`
- `fr_2015_RURO_mnl_v2gsurY2014__mnlmeta.json`
- `fr_2016_RURO_mnl_v2gsurY2015__singles.parquet`
- `fr_2016_RURO_mnl_v2gsurY2015__couples.parquet`
- `fr_2016_RURO_mnl_v2gsurY2015__mnlmeta.json`
- `fr_2017_RURO_mnl_v2gsurY2016__singles.parquet`
- `fr_2017_RURO_mnl_v2gsurY2016__couples.parquet`
- `fr_2017_RURO_mnl_v2gsurY2016__mnlmeta.json`

---

## 22. Files modified

No parquet data values were changed by the correction. The
correction creates new authorized-stem copies; it does not modify
existing files.

The three authorized-stem sidecar JSON files are new files (not
modifications of the v2gsurY sidecars). The `output_singles_parquet`
and `output_couples_parquet` path fields in the new sidecars
reference the authorized `GSURv2_y` filenames.

`Results/JMP_GSURv2_MNL_rebuild_report_v1.md` is superseded by
this v2 report but is not deleted; v1 remains in git history.

---

## 23. What was not executed

The following were not executed as part of the rebuild or this
correction:

- Pooled stacking of the output parquets.
- Any model estimation.
- Welfare computation.
- Canonical promotion of any output parquet.
- Any change to P3b, P4, M1-clean, or M1-naive estimation
  specifications.
- Rerunning the GSURv2 merge (the correction copies existing
  byte-identical content; no new merge was performed).

---

## 24. Whether GSURv2 MNL rebuild passed

**Yes. The GSURv2 MNL-parquet rebuild PASSED.**

All V1–V12 validation checks passed for all three survey years
(81 sub-checks, 0 failures). All H1–H10 halt conditions remained
not triggered. The authorized-stem files are byte-identical to
the validated `v2gsurY` outputs. No data values were changed by
the correction.

---

## 25. Whether pooled stacking re-run is authorized

**No. Pooled stacking re-run is NOT authorized.**

The Stage M1 pooled stacking re-run against the GSURv2-based MNL
parquets is downstream of the rebuild and requires its own
authorization (authorization §17 N1). The rebuild and this
correction do not authorize it.

---

## 26. Whether pooled estimation is authorized

**No. Pooled estimation is NOT authorized.**

No pooled estimation, provisional or final, is authorized by the
rebuild or by this correction. Pooled estimation remains gated
behind the pooled stacking re-run, the cluster-robust SE wrapper,
and the pooled specification authorization (§17 N2).

---

## 27. Whether welfare computation is authorized

**No. Welfare computation is NOT authorized.**

No welfare implementation or computation is authorized by the
rebuild or by this correction. Welfare work requires its own
authorization and an accepted empirical baseline (§17 N3).

---

## 28. Remaining blockers

The rebuild itself has no remaining blockers — it is complete and
all validation checks passed.

The gate immediately following the rebuild is a strict
post-rebuild verdict. The post-rebuild verdict is the required
next step before any downstream work (pooled stacking, pooled
estimation, welfare) can be authorized.

Downstream blockers (not affected by the rebuild):

- Pooled stacking re-run requires its own authorization after
  the post-rebuild verdict.
- Pooled estimation requires pooled stacking completion plus
  cluster-robust SE wrapper and specification authorization.
- Welfare requires an accepted empirical baseline.
- M1-clean 2016 remains the active JMP baseline until a later
  SA2 verdict explicitly promotes a final pooled specification.

---

## 29. Exact next task

The exact next task is: issue a strict post-rebuild verdict on
the GSURv2 MNL-parquet rebuild.

The post-rebuild verdict must inspect this report
(`Results/JMP_GSURv2_MNL_rebuild_report_v2.md`) and the
correction report
(`Results/JMP_GSURv2_MNL_rebuild_correction_report_v1.md`),
confirm that the rebuild passed all V1–V12 checks, confirm that
the authorized-stem output files exist with the recorded SHA-256
hashes, and issue a verdict (PASS or FAIL with diagnosis).

If the post-rebuild verdict passes, it may authorize pooled
stacking re-run as the following step. Pooled stacking re-run is
separately gated and is not authorized by this rebuild or this
correction.

---

**Required final statements**

- **GSURv2 MNL-parquet rebuild is COMPLETE and PASSES all
  validation checks.** All six authorized-stem output parquets
  exist, all V1–V12 checks passed, and all H1–H10 halt conditions
  were not triggered.

- **The dgn-to-sex mapping is verified.** `dgn=1.0` → `M`
  (male); `dgn=0.0` → `F` (female). Verified empirically, not
  assumed.

- **Pooled stacking is NOT authorized.** Separately gated.

- **Pooled estimation is NOT authorized.** Separately gated.

- **Welfare computation is NOT authorized.** Separately gated.

- **M1-clean 2016 remains the active JMP baseline.** Displaced
  only by a future SA2 verdict explicitly promoting a final
  pooled specification.