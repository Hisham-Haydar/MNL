# JMP GSURv2 MNL-Parquet Rebuild — Correction Report v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-20*

---

## 1. Purpose

This document records two narrow corrections applied to the GSURv2
MNL-parquet rebuild package after the rebuild completed and was
validated. No parquet data values were changed. No merge was
rerun. No downstream step was performed.

| # | Issue | Action |
|---|-------|--------|
| C1 | Output parquets written to `v2gsurY` stems rather than the authorized `GSURv2_y` stems (authorization §8) | Created authorized-stem copies by byte-identical file copy; original `v2gsurY` files preserved |
| C2 | Rebuild report v1 (29 headings) did not use the heading structure required by the authorization; output file inventory referenced `v2gsurY` filenames | Created rebuild report v2 with the 29 required headings and the authorized-stem filenames |

The rebuild data quality is unchanged. All V1–V12 validation checks
that passed in v1 still pass in v2. The authorized-stem parquets
are byte-identical to the `v2gsurY` parquets.

---

## 2. Issues corrected

### C1 — Output stem mismatch

The authorization memo §8 specifies three output stems:

```
fr_2015_RURO_mnl_GSURv2_y2014__
fr_2016_RURO_mnl_GSURv2_y2015__
fr_2017_RURO_mnl_GSURv2_y2016__
```

The rebuild execution wrote to stems derived from the T6 task
prompt preflight:

```
fr_2015_RURO_mnl_v2gsurY2014__
fr_2016_RURO_mnl_v2gsurY2015__
fr_2017_RURO_mnl_v2gsurY2016__
```

The `v2gsurY` stems encode the same semantic content as the
authorized `GSURv2_y` stems (GSURv2 source + opportunity year),
but the filenames do not match the authorization. The correction
creates the authorized-stem files.

### C2 — Report heading structure

The rebuild report v1 used 29 headings but not the specific
heading labels required by the authorization. The v1 report also
referenced `v2gsurY` filenames in the output inventory. The
correction creates rebuild report v2 with the exact 29 required
headings and with all file references updated to the authorized
stems.

---

## 3. Output-stem correction

The authorized-stem parquets were created by byte-identical file
copy of the validated `v2gsurY` parquets. No merge was rerun.

| Source (`v2gsurY`) | Authorized copy (`GSURv2_y`) | Byte-identical |
|---|---|---|
| `fr_2015_RURO_mnl_v2gsurY2014__singles.parquet` | `fr_2015_RURO_mnl_GSURv2_y2014__singles.parquet` | Yes (SHA `889b2f8a…`) |
| `fr_2015_RURO_mnl_v2gsurY2014__couples.parquet` | `fr_2015_RURO_mnl_GSURv2_y2014__couples.parquet` | Yes (SHA `d44d2292…`) |
| `fr_2016_RURO_mnl_v2gsurY2015__singles.parquet` | `fr_2016_RURO_mnl_GSURv2_y2015__singles.parquet` | Yes (SHA `139cd025…`) |
| `fr_2016_RURO_mnl_v2gsurY2015__couples.parquet` | `fr_2016_RURO_mnl_GSURv2_y2015__couples.parquet` | Yes (SHA `61e3107b…`) |
| `fr_2017_RURO_mnl_v2gsurY2016__singles.parquet` | `fr_2017_RURO_mnl_GSURv2_y2016__singles.parquet` | Yes (SHA `8fce026d…`) |
| `fr_2017_RURO_mnl_v2gsurY2016__couples.parquet` | `fr_2017_RURO_mnl_GSURv2_y2016__couples.parquet` | Yes (SHA `2d8dc7ae…`) |

Byte-identity was verified for all six copies (SHA-256 of source
equals SHA-256 of destination). The original `v2gsurY` files are
preserved and were not deleted or modified.

---

## 4. Sidecar correction

The three `v2gsurY` sidecars were used as templates for three new
authorized-stem sidecars. All data fields (survey year, opportunity
year, lookup SHA-256, merge keys, dgn-to-sex mapping, row counts,
column counts, V1–V12 all-pass status, build timestamp, script
version) are carried over unchanged. Only the output path fields
were updated.

| Field | v2gsurY sidecar value | GSURv2_y sidecar value |
|---|---|---|
| `output_singles_parquet` | `fr_201X_RURO_mnl_v2gsurY20XX__singles.parquet` | `fr_201X_RURO_mnl_GSURv2_y20XX__singles.parquet` |
| `output_couples_parquet` | `fr_201X_RURO_mnl_v2gsurY20XX__couples.parquet` | `fr_201X_RURO_mnl_GSURv2_y20XX__couples.parquet` |
| `output_singles_sha256` | unchanged (byte-identical) | unchanged (byte-identical) |
| `output_couples_sha256` | unchanged (byte-identical) | unchanged (byte-identical) |
| `output_singles_bytes` | unchanged | unchanged |
| `output_couples_bytes` | unchanged | unchanged |
| `stem_correction_note` | (absent) | Added: authorized stems created by byte-identical copy of v2gsurY files; original v2gsurY files preserved; correction 2026-05-20 |

Authorized-stem sidecars written:
- `fr_2015_RURO_mnl_GSURv2_y2014__mnlmeta.json`
- `fr_2016_RURO_mnl_GSURv2_y2015__mnlmeta.json`
- `fr_2017_RURO_mnl_GSURv2_y2016__mnlmeta.json`

---

## 5. Report-heading correction

Rebuild report v1 (`Results/JMP_GSURv2_MNL_rebuild_report_v1.md`)
used these headings (§1–§29):

1. Purpose — 2. Authorization basis — 3. Preflight check —
4. GSURv2 lookup SHA-256 verification — 5. Schema verification —
6. Singles dgn coding verification — 7. dgn-to-sex mapping —
8–13. Rebuild execution (FR_2015 singles/couples, FR_2016, FR_2017) —
14. v1-fallback preservation — 15–17. Validation results (per year) —
18. drgn1=9 handling — 19. gsur range by survey year —
20. Output file inventory — 21. Sidecar inventory —
22. Input v1-fallback file integrity — 23. Halt conditions —
24. Output stem naming note — 25. Survey-year totals —
26. What was not done — 27. Overall rebuild verdict —
28. git note — 29. Readiness of next gate

Rebuild report v2 (`Results/P3a/gsurv2/JMP_GSURv2_MNL_rebuild_report_v2.md`)
uses the 29 required headings:

1. Rebuild verdict — 2. Authorization scope — 3. Files inspected —
4. Input stems — 5. Output stems — 6. GSURv2 lookup files used —
7. Survey-year / opportunity-year mapping —
8. Actual MNL schema verified — 9. Singles merge logic —
10. dgn-to-sex mapping — 11. Couples merge logic —
12. Fallback GSUR preservation — 13. Metadata sidecars —
14. Row-count validation — 15. Household-count validation —
16. Non-GSUR column equality validation —
17. Active GSUR completeness validation —
18. drgn1=9 handling — 19. GSURv2 value checks —
20. Canonical-file safety check — 21. Files created —
22. Files modified — 23. What was not executed —
24. Whether GSURv2 MNL rebuild passed —
25. Whether pooled stacking re-run is authorized —
26. Whether pooled estimation is authorized —
27. Whether welfare computation is authorized —
28. Remaining blockers — 29. Exact next task

Report v1 is superseded by v2 but is preserved in git history.
No data values reported in v1 were incorrect; only the heading
structure and file references were corrected.

---

## 6. Data integrity checks

To confirm the correction introduced no data changes, the
authorized-stem parquets were verified byte-identical to the
`v2gsurY` parquets immediately after copying.

| Authorized-stem file | SHA-256 (full) | Matches v2gsurY source SHA |
|---|---|---|
| `fr_2015_RURO_mnl_GSURv2_y2014__singles.parquet` | `889b2f8a95a9ac1a30cdb8d6e6ff5cf6002525345f940a65cfdc0176d9998819` | Yes |
| `fr_2015_RURO_mnl_GSURv2_y2014__couples.parquet` | `d44d229207c6d9c4aceb9bfeaa33bd05beb1e7e01a142b41618250f90039a00d` | Yes |
| `fr_2016_RURO_mnl_GSURv2_y2015__singles.parquet` | `139cd025d35e6b2fe0e5f03d6d7d3564857eb0e3743ca0cbbd04d687da64cb2e` | Yes |
| `fr_2016_RURO_mnl_GSURv2_y2015__couples.parquet` | `61e3107bb17f4fbf781cea37abd410cc918fe0246ed2c50e853060eb9f40154a` | Yes |
| `fr_2017_RURO_mnl_GSURv2_y2016__singles.parquet` | `8fce026d23536f12ec2dbc2b1a403a68503168150dace55c90bcfc63de670b9e` | Yes |
| `fr_2017_RURO_mnl_GSURv2_y2016__couples.parquet` | `2d8dc7aeb7c0e99df9a5318935b8d59ac2b7b2a18a222526dad5850ba068ac26` | Yes |

All six byte-identity checks PASS. No data was altered by the
correction.

The V1–V12 validation checks recorded in the v1 report remain
valid for the authorized-stem parquets: the authorized-stem
parquets carry exactly the same data as the `v2gsurY` parquets
that were validated.

---

## 7. What was not changed

The following are confirmed unchanged by this correction:

- All parquet data values (GSUR rates, fallback rates, all other
  columns).
- The V1–V12 validation results (all PASS, unchanged).
- The H1–H10 halt conditions (all not triggered, unchanged).
- The GSURv2 lookup SHA-256 hashes and provenance.
- The dgn-to-sex mapping (`dgn=1.0` → `M`; `dgn=0.0` → `F`).
- The merge logic (singles: S1–S5; couples: C1–C5).
- The v1-fallback preservation (fallback columns value-identical
  to input parquets' prior active GSUR columns).
- The input v1-fallback parquets (all six confirmed unmodified).
- The GSURv2 lookup parquets.
- Any estimation specification or canonical file.
- The `v2gsurY` files (preserved, not deleted).

No merge was rerun. No model was estimated. No welfare was
computed. No canonical promotion was performed.

---

## 8. Final verdict

**GSURv2 MNL-parquet rebuild remains PASS.**

The two corrections (output-stem normalization and report-heading
correction) are documentation and filename corrections only. All
data integrity checks pass. The authorized-stem parquets are
byte-identical to the validated `v2gsurY` outputs. No data value
was changed. The rebuild data quality is unchanged from the v1
report.

**Pooled stacking re-run is NOT authorized.** The rebuild and
this correction do not authorize pooled stacking re-run. It is
separately gated after the post-rebuild verdict.

**Pooled estimation is NOT authorized.** Separately gated.

**Welfare computation is NOT authorized.** Separately gated.

**M1-clean 2016 remains the active JMP baseline.** Displaced
only by a future SA2 verdict explicitly promoting a final pooled
specification.