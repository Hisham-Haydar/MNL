# JMP GSURv2 Multi-Year Extension — Construction Verdict v1

Date: 2026-05-20

Construction under review: GSURv2 Stage A multi-year lookup
construction for opportunity years 2016, 2015, and 2014, executed
under Option B (y2016 value-identity lock followed by conditional
y2015 and y2014 construction).

Output files under review (all in `Data/external/`):
- `FR_gsur_ruro_v2_stageA_y2016.parquet` + `__sidecar.json`
- `FR_gsur_ruro_v2_stageA_y2015.parquet` + `__sidecar.json`
- `FR_gsur_ruro_v2_stageA_y2014.parquet` + `__sidecar.json`

Primary evidence:
- `Results/JMP_GSURv2_multi_year_extension_validation_report_v1.md`
- `docs/JMP_GSURv2_multi_year_extension_construction_report_v1.md`

Governing documents:
- `docs/JMP_GSURv2_multi_year_extension_construction_authorization_v1.md`
  (the Option B construction authorization)
- `docs/JMP_GSUR_year_alignment_decision_v1.md` (the opportunity-
  year alignment rule and the GSURv2 final-build requirement)
- `docs/JMP_multi_year_stage_M1_P3a_construction_verdict_v1.md`
  (the provisional P3a construction the GSURv2 lookups will
  eventually serve)
- `docs/RURO_occ_M1_clean_verdict_v1.md` (the active single-year
  JMP baseline)

Interpreter of record: `.venv\Scripts\python.exe`
(`U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe`).

Scope of verdict: post-construction quality assessment of the
GSURv2 multi-year lookup construction. The verdict adjudicates
whether the construction followed the Option B authorization,
whether the three lookups are correctly and completely
constructed, whether GSURv2 coverage is now complete for the P3a
opportunity years, and which gate is next. The verdict does not
authorise the MNL-parquet rebuild, the pooled stacking re-run,
pooled estimation, welfare computation, or canonical promotion;
those steps are separately gated.

---

## 1. Verdict

**PASS.**

The GSURv2 multi-year lookup construction is a clean PASS. All
three opportunity-year Stage A lookups were constructed under
Option B; the y2016 value-identity gate passed exactly (maximum
absolute `gsur` difference of 0.0, byte-identical reproduction of
the existing validated lookup); the y2015 and y2014 constructions
followed conditionally and passed all validation checks; all three
sidecars carry the complete 14-field provenance with the expected
year-specific values; and the load-bearing Île-de-France parity
check returned exactly 0.0 for all three years. No halt was
triggered. The construction followed the authorization without
material deviation.

The construction is classified PASS rather than PASS WITH
LIMITATIONS because the GSURv2 lookup data products — the three
opportunity-year lookups — carry no limitations: each lookup has
the correct 54-row schema, the correct cell-level rates, the
correct IDF parity, the correct benchmark provenance, and the
correct NUTS-2016 vintage. The construction-quality criteria are
all met at the data-product level.

Three outstanding items are recorded (§15), but none qualifies the
construction PASS. First, the post-construction cleanup — the
retirement of the existing un-tagged y2016 baseline and the
migration of references from the un-tagged path to the year-tagged
path — was correctly not executed by the construction: post-
construction cleanup, archival of the un-tagged y2016 file, and
reference migration are separately gated (per the construction
authorization §4 and §10 Step 8), and the construction followed
the authorization correctly by not performing them. Second, the six
output files are present on
disk with full sidecar provenance but are not git-committed,
because the `Data/` directory is git-excluded; the provenance is
carried by the sidecars and the construction report, which are
committed. Third, the construction report §9 carries a minor
descriptive label slip (the suppressed NUTS-2 regions FRM0 and
FRI2 are mislabelled), which is a documentation annotation error
that does not affect the construction (the suppression handling
operates on NUTS codes, not labels). These three items are
housekeeping and documentation matters, not limitations of the
GSURv2 lookup data.

**GSURv2 lookup coverage is now complete for the three P3a
opportunity years 2014, 2015, and 2016 at the lookup level.** The
three lookups exist, are validated, and carry consistent
provenance. The MNL-parquet integration of these lookups — the
merge that replaces the v1-fallback rates with GSURv2 rates in the
FR_2015, FR_2016, and FR_2017 MNL parquets — has not been
performed and is the next stage, gated behind the O7 crosswalk
sign-off and a separate MNL-rebuild authorization (§10, §11).

The construction PASS authorises nothing downstream. The MNL-
parquet rebuild, the pooled stacking re-run, pooled estimation,
welfare computation, and canonical promotion all remain
separately gated and unauthorised (§11 through §14). The single-
year M1-clean 2016 specification remains the active JMP baseline
(§15).

---

## 2. Whether construction followed authorization

**The construction followed the Option B authorization. Post-
construction cleanup, archival of the un-tagged y2016 file, and
reference migration were correctly not executed: they are
separately gated per the construction authorization §4 and §10
Step 8, and the construction followed the authorization correctly
by not performing them.**

The construction executed the authorised Option B sequence (§4 of
the authorization). The y2016 run executed first as the provenance
and value-identity lock; the y2016 value-identity check (§6 of the
authorization, conditions G1–G4) was performed key-aligned on
`(year, drgn1, educ3, sex)`; the y2015 run executed conditional on
the y2016 gate passing; and the y2014 run executed conditional on
both the y2016 gate and the y2015 validation passing. The
conditional sequencing was respected: no genuinely new lookup was
constructed until the y2016 value-identity gate confirmed the
parameterised script reproduces the existing validated lookup
exactly.

The construction used the authorised interpreter
(`.venv\Scripts\python.exe`) and the authorised script
(`enh_prepare_FR_gsur_v2.py`, commit `178ca72`, confirmed by the
`script_version` field in all three sidecars). The construction
script was not modified during construction (the no-modification
constraint of the authorization §16 N6 was respected). The pre-run
preflight confirmed all six year-tagged outputs were absent before
construction began (the existing-output guard of the authorization
§11 did not trigger). No halt condition was triggered.

The construction did not perform post-construction cleanup, archival
of the un-tagged y2016 baseline, or reference migration: the
existing un-tagged `FR_gsur_ruro_v2_stageA.parquet` was not retired
to the archive, and the references to the un-tagged path in the
canary and validation scripts were not migrated to the year-tagged
path. This is correct and consistent with the authorization. The
construction authorization §4 states explicitly that "post-
construction cleanup, archival of the un-tagged y2016 file, and
reference migration are separately gated after the construction
report and validation report pass", and §10 Step 8 restricts the
construction to committing the six output files only, with the same
deferred-cleanup language. The construction followed the
authorization correctly.

The six output parquets and sidecars are present on disk but are
not git-committed, because the `Data/` directory is git-excluded
per `.gitignore` (rule `Data/`, line 21). The provenance of all
six output files is carried by the committed sidecars and the
committed construction and validation reports.

---

## 3. y2016 value-identity result

**PASS. Maximum absolute `gsur` difference = 0.0 (exact); byte-
identical reproduction.**

The y2016 value-identity gate is the load-bearing precondition of
Option B: it confirms that the parameterised script reproduces the
existing validated y2016 lookup exactly, validating the
construction logic before any genuinely new lookup is built. The
gate passed on all four conditions and the NaN-alignment check.

| Condition | Requirement | Result |
|---|---|---|
| G1 — row counts | Both files exactly 54 rows | new 54, old 54 — PASS |
| G2 — key match | All `(year, drgn1, educ3, sex)` keys match | All 54 key tuples match — PASS |
| G3 — no duplicates | Zero duplicate keys in either file | new 0, old 0 — PASS |
| G4 — max absolute diff | 0.0, or ≤ 1e-12 if floating precision requires; NaN-aware over 48 active cells | 0.0 exactly — PASS |
| NaN stub alignment | 6 drgn1=9 stub rows NaN in both files | 6 stubs NaN in both — PASS |

The comparison was key-aligned on `(year, drgn1, educ3, sex)`, not
row-order-only, as required by the authorization §6. The maximum
absolute `gsur` difference over the 48 active (non-null) cells was
0.0 exactly, and the 6 drgn1=9 stub rows were NaN-aligned in both
files. The construction report further records that the y2016
year-tagged parquet is byte-identical to the un-tagged baseline:
both carry SHA-256
`19ac53143fb404f3de44f4e2abc3313b0946eda835261496720bc511358c24ef`
and size 7,444 bytes. The byte-identity is a stronger result than
the value-identity the gate required: not only do the `gsur` values
match to within machine precision, the entire parquet is bit-for-
bit identical to the existing validated lookup.

The byte-identity confirms that the C1–C7 parameterisation
preserves the construction logic exactly. The parameterised script,
run with `--opportunity-year 2016`, produces the same lookup as the
original un-parameterised script produced for 2016. This is the
empirical validation of the parameterisation that the Option B
design used the y2016 run to obtain, and it licensed the y2015 and
y2014 construction.

---

## 4. y2014 construction result

**PASS. All validation checks (Y2014-1 through Y2014-5) passed.**

The y2014 lookup was constructed conditional on both the y2016
value-identity gate passing and the y2015 validation passing (the
terminal step of the Option B sequence). It passed all validation
checks.

Output: `FR_gsur_ruro_v2_stageA_y2014.parquet` (SHA-256
`740ef6c7…`, 7,441 bytes, 54 rows, eleven-column schema). The
`gsur` range over the active cells is 0.053647 to 0.261.

| Check | Requirement | Result |
|---|---|---|
| Y2014-1 — row count | 54 (48 active + 6 stubs) | 54 — PASS |
| Y2014-2 — sidecar fields | 14 fields, `opportunity_year=2014`, `benchmark_pct=9.9`, `row_count=54` | all present, values correct — PASS |
| Y2014-3 — IDF parity | `idf_parity_difference` ≈ 0.0 | 0.0 — PASS |
| Y2014-4 — L5 benchmark | benchmark difference recorded | 0.0494 ppt recorded — PASS |
| Y2014-5 — NUTS vintage | NUTS-2016 compatible with crosswalk | `nuts_vintage="NUTS2016"` — PASS |

The IDF parity check returned 0.0, confirming that the population-
weighted aggregation reduces correctly to the single-component FR10
value for the single-component Île-de-France region. The L5
national-benchmark difference of 0.0494 ppt (the constructed
national GSUR aggregate versus the INSEE benchmark of 9.9 per
cent) is recorded as a consistency diagnostic and is the smallest
of the three years' L5 differences. The NUTS-2016 vintage is
confirmed and recorded in the sidecar.

The y2014 lookup is correctly and completely constructed. It is
the genuinely new lookup serving the FR_2015 survey year (the
2014 opportunity year, per the alignment rule), for which no
GSURv2 lookup previously existed.

---

## 5. y2015 construction result

**PASS. All validation checks (Y2015-1 through Y2015-5) passed.**

The y2015 lookup was constructed conditional on the y2016 value-
identity gate passing (the second step of the Option B sequence).
It passed all validation checks.

Output: `FR_gsur_ruro_v2_stageA_y2015.parquet` (SHA-256
`f51ad630…`, 7,433 bytes, 54 rows, eleven-column schema). The
`gsur` range over the active cells is 0.053183 to 0.225.

| Check | Requirement | Result |
|---|---|---|
| Y2015-1 — row count | 54 (48 active + 6 stubs) | 54 — PASS |
| Y2015-2 — sidecar fields | 14 fields, `opportunity_year=2015`, `benchmark_pct=10.025`, `row_count=54` | all present, values correct — PASS |
| Y2015-3 — IDF parity | `idf_parity_difference` ≈ 0.0 | 0.0 — PASS |
| Y2015-4 — L5 benchmark | benchmark difference recorded | 0.0943 ppt recorded — PASS |
| Y2015-5 — NUTS vintage | NUTS-2016 compatible with crosswalk | `nuts_vintage="NUTS2016"` — PASS |

The IDF parity check returned 0.0, confirming the correct single-
component reduction for Île-de-France. The L5 national-benchmark
difference of 0.0943 ppt (versus the INSEE benchmark of 10.025 per
cent) is recorded as a consistency diagnostic. The NUTS-2016
vintage is confirmed and recorded.

The y2015 lookup is correctly and completely constructed. It is the
genuinely new lookup serving the FR_2016 survey year (the 2015
opportunity year), for which no GSURv2 lookup previously existed.
The y2015 validation passing was the precondition that licensed the
y2014 construction.

---

## 6. y2016 provenance lock result

**RESOLVED. The y2016 provenance lock is complete: the year-tagged
y2016 lookup and its sidecar exist, the sidecar carries the full
14-field provenance, and the value-identity against the existing
baseline is confirmed exact.**

The y2016 provenance lock was the purpose of running y2016 first
under Option B. The lock comprises two elements, both resolved.

First, the K1 sidecar resolution. The original y2016 GSURv2 lookup
(the un-tagged `FR_gsur_ruro_v2_stageA.parquet`) lacked a sidecar,
which was the K1 provenance-lock failure in the implementation
audit. The y2016 construction run wrote the year-tagged y2016
sidecar (`FR_gsur_ruro_v2_stageA_y2016__sidecar.json`) via the C7
sidecar block, carrying the 14-field provenance: `opportunity_year=2016`,
`gsur_column_name="gsur"`, the input file paths, `benchmark_pct=9.725`,
`nuts_vintage="NUTS2016"`, `idf_parity_difference=0.0`,
`benchmark_difference_pct=0.1718`, `row_count=54`, the build
timestamp, and the script version `178ca72…`. K1 is resolved: the
y2016 lookup now carries a complete provenance sidecar.

Second, the value-identity confirmation. The y2016 provenance lock
required that the year-tagged y2016 lookup be value-identical to
the existing un-tagged baseline, so that the year-tagged lookup is
established as the authoritative y2016 lookup without altering the
validated rates. The value-identity gate (§3) confirmed this
exactly (byte-identical, SHA-256 match). The year-tagged y2016
lookup is therefore the existing validated y2016 lookup under a
year-tagged name with a complete provenance sidecar.

The provenance lock is complete in the sense the lock plan
specified: the y2016 lookup is now year-tagged, sidecar-documented,
and value-identity-confirmed against the existing baseline. The one
element of the lock plan not executed is the retirement of the
existing un-tagged baseline (lock plan Step 7), which was deferred
to the separate cleanup gate (§2, §15). The deferral does not
affect the provenance lock's substantive completion: the year-
tagged y2016 lookup and its sidecar exist and are value-identity-
confirmed; the retirement of the now-redundant un-tagged baseline
is a housekeeping step. The K3 element of the provenance lock (the
O7 crosswalk sign-off) is a separate gate that the construction
did not and could not resolve (§10); it gates the MNL-parquet
merge, not the lookup construction.

---

## 7. Sidecar metadata status

**COMPLETE AND CONSISTENT. All three sidecars carry the full 14-
field provenance with the correct year-specific values and
consistent year-invariant values.**

The three sidecars were inspected against the 14-field schema
specified in the construction authorization §12. Table 1
summarises the inspection.

| Field | y2016 | y2015 | y2014 | Status |
|---|---|---|---|---|
| `opportunity_year` | 2016 | 2015 | 2014 | year-specific, correct |
| `gsur_column_name` | `"gsur"` | `"gsur"` | `"gsur"` | consistent (K2 decision) |
| `output_path` | `…_y2016.parquet` | `…_y2015.parquet` | `…_y2014.parquet` | year-tagged, correct |
| `input_d2` | `…_2016.tsv` | `…_2015.tsv` | `…_2014.tsv` | year-specific, correct |
| `input_d1` | `…_2016.tsv` | `…_2015.tsv` | `…_2014.tsv` | year-specific, correct |
| `input_unemployment_workbook` | `FR_gsur.xlsx` | `FR_gsur.xlsx` | `FR_gsur.xlsx` | consistent (shared) |
| `input_benchmark_csv` | `…_2016.csv` | `…_2015.csv` | `…_2014.csv` | year-specific, correct |
| `benchmark_pct` | 9.725 | 10.025 | 9.9 | year-specific, correct |
| `nuts_vintage` | `"NUTS2016"` | `"NUTS2016"` | `"NUTS2016"` | consistent, correct |
| `idf_parity_difference` | 0.0 | 0.0 | 0.0 | all exact zero |
| `benchmark_difference_pct` | 0.1718 | 0.0943 | 0.0494 | recorded (diagnostic) |
| `row_count` | 54 | 54 | 54 | consistent, correct |
| `build_timestamp` | 19:06:59Z | 19:08:21Z | 19:09:10Z | year-ordered, UTC |
| `script_version` | `178ca72…` | `178ca72…` | `178ca72…` | consistent (single version) |

The sidecar inspection confirms three substantive properties.
First, the `gsur_column_name` field records `"gsur"` for all three
years, making the K2 decision (the active column name remains
`gsur`) explicit and auditable per build. Second, the
`script_version` field records the identical git SHA
(`178ca72bcb40b829a41648a470cb4c31aee9605b`) for all three years,
confirming that a single script version was used throughout the
construction — there was no mid-construction script modification.
Third, the `idf_parity_difference` field records exactly 0.0 for
all three years, confirming the construction-correctness of the
population-weighted aggregation for the single-component Île-de-
France region in every year.

The build timestamps are year-ordered (y2016 at 19:06:59, y2015 at
19:08:21, y2014 at 19:09:10), consistent with the Option B
construction sequence (y2016 first, then y2015, then y2014), and
are timezone-aware UTC.

The sidecar metadata is complete and consistent. No field is
missing; no value is incorrect; the year-invariant values are
consistent across the three years; the year-specific values are
correct for each year.

---

## 8. Validation status by year

**ALL THREE YEARS PASS. The script-level validation battery passed
on all nine checks for every opportunity year, and the per-year
authorization-level validation passed for all three years.**

The construction script reported all nine validation checks PASS
for every opportunity year (construction report §3): `L1_unique_keys`,
`L2_proportion_units`, `L3_drgn1_support`, `L4_idf_crosswalk_sanity`,
`L5_national_benchmark`, `L7_weighting_source`, `L8_approximation_flags`,
`missing_values`, and `IDF_parity`. The overall script verdict was
PASS for all three years. The separate validation report
(`Results/JMP_GSURv2_multi_year_extension_validation_report_v1.md`)
corroborates the construction report's validation summary.

Table 2 summarises the per-year validation status against the
authorization-level checks (§13 of the authorization).

| Check | y2016 | y2015 | y2014 |
|---|---|---|---|
| Row count = 54 | PASS | PASS | PASS |
| Value-identity vs baseline (key-aligned, G1–G4) | PASS (gate) | n/a | n/a |
| Sidecar 14 fields present | PASS | PASS | PASS |
| `opportunity_year` correct | PASS | PASS | PASS |
| `gsur_column_name = "gsur"` | PASS | PASS | PASS |
| `benchmark_pct` correct | PASS | PASS | PASS |
| IDF parity ≈ 0.0 | PASS (0.0) | PASS (0.0) | PASS (0.0) |
| L5 benchmark difference recorded | PASS (0.1718) | PASS (0.0943) | PASS (0.0494) |
| NUTS-2016 vintage | PASS | PASS | PASS |
| No silent overwrite | PASS | PASS | PASS |

Two validation observations warrant note. First, the IDF parity
check — the load-bearing construction-correctness check — returned
exactly 0.0 for all three years, confirming that the crosswalk-
weighted aggregation reduces correctly to the single-component FR10
value for Île-de-France in every year. Second, the L5 national-
benchmark differences (0.1718, 0.0943, 0.0494 ppt for 2016, 2015,
2014 respectively) are all within the expected range for a
population-weighted NUTS-2-to-national aggregation versus a direct
national survey figure; the L5 check is a consistency diagnostic,
not a construction gate, and the recorded deviations do not
invalidate the cell-level rates.

The denominator and crosswalk logic were applied consistently
across the three years: the D2 population denominator at Y20-64 was
the operational denominator (the D1 denominator being diagnostic
only, owing to the year-invariant Eurostat limitation that D1 does
not publish Y20-64 at NUTS-2 level), the shared 22-row crosswalk
was applied to all three years, and the year-invariant suppression
pattern for the two suppressed NUTS-2 regions was handled by the
`approximate_uniform` fallback with the L8 approximation-flags
check passing for all years.

The validation status is PASS for all three years.

---

## 9. Whether GSURv2 coverage is now complete for P3a

**Yes, at the lookup level. GSURv2 lookup coverage is now complete
for the three P3a opportunity years 2014, 2015, and 2016. The MNL-
parquet integration of these lookups is the next stage and has not
been performed.**

The P3a pooled sample requires GSURv2 opportunity-year coverage for
three opportunity years: 2014 (serving the FR_2015 survey year),
2015 (serving FR_2016), and 2016 (serving FR_2017), per the
alignment rule (year-alignment decision §2). Prior to this
construction, GSURv2 existed only for opportunity year 2016 (the
un-tagged Stage A lookup built for the single-year M1-clean
baseline); opportunity years 2014 and 2015 had no GSURv2 lookup.

The construction produced GSURv2 lookups for all three opportunity
years: the year-tagged y2016 lookup (value-identical to the
existing baseline), the new y2015 lookup, and the new y2014 lookup.
All three are validated, carry consistent provenance, and use the
identical construction methodology (the same script version, the
same shared crosswalk, the same D2 denominator method, the same
Y20-64 age band). The GSURv2 lookup coverage for the three P3a
opportunity years is therefore complete: a GSURv2 lookup exists,
validated and provenance-documented, for each of the three years.

The completeness is at the lookup level, not the MNL-parquet level.
The three GSURv2 lookups exist as standalone lookup parquets in
`Data/external/`. They have not been merged into the FR_2015,
FR_2016, and FR_2017 MNL parquets: those MNL parquets still carry
the v1-fallback opportunity-side rates (the P3a construction
verdict §13 documented the provisional v1-fallback status). The
P3a pooled dataset
(`fr_p3a_harmonised.parquet`) consequently remains labelled
`provisional_v1_fallback_opportunity_year_aligned` until the MNL-
parquet rebuild merges the GSURv2 lookups.

The completion of the GSURv2 lookup coverage satisfies the
empirical prerequisite that the year-alignment decision §6
established for final pooled estimation: GSURv2 rebuilt for each
opportunity year (2014, 2015, 2016). The lookups now exist. The
remaining work to reach a final pooled estimation — the MNL-parquet
rebuild merging the lookups, the pooled stacking re-run, the
cluster-robust inference, the pooled specification, and the pooled
estimation — is downstream and separately gated (§11 through §13).

The GSURv2 coverage for the three P3a opportunity years is complete
at the lookup level. The MNL integration is the next stage.

---

## 10. Whether O7 sign-off is now needed

**Yes. The O7 crosswalk sign-off is now the next required gate
before the GSURv2 MNL-parquet rebuild.**

The O7 crosswalk sign-off is the user's explicit approval of the
NUTS-2-to-drgn1 crosswalk (`fr_drgn1_to_nuts2_crosswalk.csv`, 22
rows, all `verified_against_eurostat=YES`) and the merge key
`(drgn1, educ3, sex)` for the MNL-parquet merge. The sign-off has
been pending since the original Stage A build (the K3 provenance-
lock item); the sign-off request document is assembled and ready
for the user's decision (construction report §20).

The O7 sign-off gates the MNL-parquet merge, not the lookup
construction. The lookup construction is complete (§1, §9): the
three GSURv2 lookups exist, validated, and the IDF parity check
(which confirms the crosswalk-weighted aggregation reduces
correctly for the single-component region) passed at 0.0 for all
three years. The crosswalk has therefore been used correctly in the
lookup construction. The O7 sign-off concerns the next stage: when
the lookups are merged into the MNL parquets, the merge applies the
crosswalk-derived drgn1-level GSUR assignments to the individual
MNL records, and the O7 sign-off confirms that the crosswalk and
the merge key are accepted for that merge.

The O7 sign-off is now the next required gate because the lookup
construction is complete and the next stage is the MNL-parquet
rebuild, which requires the O7 sign-off. The sign-off is a user
decision, not a Claude Code execution task. Until the O7 sign-off
is granted, the MNL-parquet rebuild is not authorised (§11).

The O7 sign-off being needed does not reopen any construction
question. The lookups are correctly constructed using the
crosswalk; the IDF parity confirms the crosswalk application. The
O7 sign-off is the governance approval that the crosswalk is
accepted for the downstream MNL merge, which is the gate between
the completed lookup construction and the MNL-parquet rebuild.

---

## 11. Whether MNL parquet rebuild is now authorized

**No. The MNL-parquet rebuild is NOT authorized. The O7 crosswalk
sign-off is not yet complete; the O7 sign-off is the prerequisite,
and the MNL-parquet rebuild is the next authorization candidate
after O7.**

The MNL-parquet rebuild — the merge of the three GSURv2 lookups
into the FR_2015, FR_2016, and FR_2017 MNL parquets, replacing the
v1-fallback opportunity-side rates with GSURv2 rates — is not
authorised by this construction verdict. Two distinct gates are
unmet.

First, the O7 crosswalk sign-off is not complete (§10). The O7
sign-off is the prerequisite governance approval for the MNL merge;
it is a pending user decision. The construction authorization §16
N1 established that the MNL-parquet rebuild "additionally requires
the O7 crosswalk sign-off, which is pending the user's decision."
The sign-off has not been granted.

Second, even with the O7 sign-off granted, the MNL-parquet rebuild
requires its own authorization. The MNL rebuild is a distinct
construction step with its own merge logic (the per-individual join
for singles, the per-partner double join for couples), its own
validation (the M1–M10 MNL-rebuild checks of the rebuild
specification), and its own provenance requirements (the v1-
fallback preservation in a `gsur_v1_fallback` column, per the K2
decision). The MNL rebuild is not authorised by this lookup-
construction verdict; it requires a separate MNL-rebuild
authorization memo.

The MNL-parquet rebuild is therefore NOT authorized yet, because
the O7 sign-off is not complete. If the O7 sign-off had already
been explicitly granted, the MNL-parquet rebuild would still
require its own authorization memo, but the O7 prerequisite would
be cleared. As the O7 sign-off is pending, the MNL-parquet rebuild
is the next authorization candidate after O7: once the O7 sign-off
is granted, the MNL-rebuild authorization memo is the next
governance document.

---

## 12. Whether pooled stacking re-run is now authorized

**No. The pooled stacking re-run is NOT authorized.**

The pooled stacking re-run — the re-execution of the Stage M1
pooled stacking against GSURv2-based MNL parquets to produce a
final (non-provisional) pooled dataset — is not authorised by this
construction verdict. The pooled stacking re-run is downstream of
the MNL-parquet rebuild: it requires the GSURv2-based MNL parquets
as its inputs, and those parquets do not exist until the MNL-
parquet rebuild is performed (which is itself not authorised, §11).

The pooled stacking re-run is gated behind the MNL-parquet rebuild,
which is gated behind the O7 sign-off. The pooled stacking re-run
is not authorised, and it is not the next gate; the O7 sign-off and
the MNL-parquet rebuild are prior.

---

## 13. Whether pooled estimation is authorized

**No. Pooled estimation is NOT authorized.**

Pooled estimation — provisional or final — is not authorised by
this construction verdict. The final pooled estimation remains
gated behind several prerequisites that are not met: the GSURv2-
based MNL parquets do not exist (the MNL rebuild is not authorised,
§11); the final pooled dataset does not exist (the pooled stacking
re-run is not authorised, §12); no cluster-robust standard-error
wrapper exists for the RURO estimator (P3a construction verdict
§17); and no pooled estimation specification exists (P3a
construction verdict §17).

The completion of the GSURv2 lookup coverage (§9) advances the
empirical prerequisite chain toward final pooled estimation, but it
does not authorise the estimation. Pooled estimation is several
gates distant and is not authorised.

---

## 14. Whether welfare computation is authorized

**No. Welfare computation is NOT authorized.**

Welfare implementation and welfare computation are not authorised
by this construction verdict. Welfare computation requires a
welfare scaffolding implementation, an accepted empirical baseline,
and the welfare-measurement decisions; none of these is provided or
advanced by the GSURv2 lookup construction. The GSURv2 construction
is a data-construction step on the opportunity-side input; it does
not produce any estimation result or welfare quantity.

Welfare computation remains gated behind the pooled-estimation path
(or the single-year M1-clean baseline, whichever becomes the
operative welfare baseline) and behind the welfare scaffolding
implementation. It is not authorised.

---

## 15. Remaining blockers

No blocker remains for the GSURv2 lookup construction itself — it
is complete and PASSED (§1). The remaining items are of two kinds:
downstream gates and post-construction housekeeping.

*Downstream gates.* Table 3 lists the gates between the completed
lookup construction and the eventual final pooled estimation.

| Downstream step | Gating condition |
|---|---|
| MNL-parquet rebuild | O7 crosswalk sign-off (pending user decision) + separate MNL-rebuild authorization |
| Pooled stacking re-run | MNL-parquet rebuild complete |
| Pooled estimation | Pooled dataset + cluster-robust SE wrapper + pooled specification |
| Welfare computation | Accepted empirical baseline + welfare scaffolding implementation |

The immediate downstream gate is the O7 crosswalk sign-off, which
is the prerequisite for the MNL-parquet rebuild (§10, §11).

*Post-construction cleanup (separately gated).* Three items are
separately gated per the construction authorization and are not
outstanding failures of the construction. None blocks the lookup
construction PASS or the downstream gates; all are recorded for a
separate narrow cleanup authorization per the authorization §4 and
§10 Step 8.

(H1) The existing un-tagged y2016 baseline
`FR_gsur_ruro_v2_stageA.parquet` remains on disk alongside the
byte-identical year-tagged y2016 lookup. Retirement (archival via
`git mv`, or equivalent) is separately gated after the construction
report and validation report pass, per the authorization. Because
the two files are byte-identical, their coexistence does not create
a data inconsistency, but the un-tagged file should be retired
under the cleanup gate to avoid future ambiguity.

(H2) The references to the un-tagged path in the canary and
validation scripts were not migrated to the year-tagged y2016 path.
The migration is separately gated per the authorization, to be
performed under the same cleanup authorization as H1. Until
migrated, the canary and validation scripts continue to reference
the un-tagged file, which is byte-identical to the year-tagged
file, so the references remain functionally correct.

(H3) The construction report §9 carries a minor descriptive label
slip: the two suppressed NUTS-2 regions are mislabelled (FRM0 and
FRI2 are annotated with incorrect region names). The suppression
handling operated correctly on the NUTS codes; the slip is a
documentation annotation error in the report prose, not a
construction error. A one-line correction to the construction
report is recommended for the record.

The post-construction housekeeping items (H1, H2, H3) are not
blockers for the downstream gates: the O7 sign-off and the MNL-
parquet rebuild do not depend on the retirement of the un-tagged
baseline or the reference migration. They are recorded for a
separate narrow cleanup authorization, which may proceed in
parallel with the O7 sign-off.

The git-tracking status (the six output files are present on disk
but not git-committed, owing to the `Data/` git-exclusion) is noted
but is not a blocker: the provenance is carried by the committed
sidecars and the committed construction and validation reports. If
git-tracked provenance of the output files is desired, the file
hashes recorded in the construction report and sidecars provide the
attestation; the files themselves are reproducible from the
committed script and the committed external inputs.

---

## 16. Immediate next task

**The immediate next task is the O7 crosswalk sign-off, a user
decision.**

The O7 crosswalk sign-off is the next required gate before the MNL-
parquet rebuild (§10). It is the user's explicit approval of the
crosswalk (`fr_drgn1_to_nuts2_crosswalk.csv`) and the merge key
`(drgn1, educ3, sex)` for the MNL-parquet merge. The O7 sign-off
request document is assembled and ready for the user's review. The
sign-off is a governance decision, not a Claude Code execution
task.

The sequencing from the current point is:

1. *O7 crosswalk sign-off* (user decision). The user reviews the
   O7 sign-off request and issues the decision. This is the
   immediate next task.

2. *MNL-parquet rebuild authorization* (Claude Project chat),
   conditional on the O7 sign-off being granted. A separate
   authorization memo that gates the merge of the three GSURv2
   lookups into the FR_2015, FR_2016, and FR_2017 MNL parquets,
   specifying the merge logic, the M1–M10 validation, and the v1-
   fallback preservation in a `gsur_v1_fallback` column per the K2
   decision.

3. *MNL-parquet rebuild* (Claude Code Sonnet), conditional on the
   MNL-rebuild authorization. The merge that produces the GSURv2-
   based MNL parquets.

4. *Final P3a pooled stacking re-run* (Claude Code Sonnet),
   conditional on the MNL rebuild. The re-execution of the Stage M1
   pipeline against the GSURv2-based MNL parquets, producing a
   final (non-provisional) pooled dataset.

5. *Pooled estimation and SA2 verdict*, conditional on the final
   pooled dataset, the cluster-robust SE wrapper, and the pooled
   specification.

A parallel, non-blocking task is the post-construction cleanup
authorization (the retirement of the un-tagged y2016 baseline, the
reference migration, and the construction-report label correction;
§15 H1, H2, H3), which may be issued at any time after this
verdict, independently of the O7 sign-off.

If the O7 sign-off is deferred, no further data construction is
authorised: the MNL-parquet rebuild and everything downstream
remain gated. The post-construction cleanup may still proceed under
its separate cleanup authorization.

---

**Required final statements**

The following statements are made explicitly, as required, and are
supported by the construction report and the validation report.

- **GSURv2 multi-year lookup construction PASSED.** All three
  opportunity-year lookups (2014, 2015, 2016) were constructed under
  Option B, the y2016 value-identity gate passed exactly (maximum
  absolute `gsur` difference 0.0, byte-identical), and the y2015 and
  y2014 constructions passed all validation checks.

- **GSURv2 coverage for P3a opportunity years 2014, 2015, and 2016
  is complete.** A validated, provenance-documented GSURv2 lookup
  exists for each of the three opportunity years at the lookup
  level. The MNL-parquet integration of these lookups is the next
  stage.

- **O7 crosswalk sign-off is now required before GSURv2 MNL parquet
  rebuild.** The O7 sign-off is the next required gate; it is a
  pending user decision.

- **MNL parquet rebuild is NOT authorized yet.** The O7 crosswalk
  sign-off has not been explicitly signed off; the MNL-parquet
  rebuild is not authorised until the O7 sign-off is complete, and
  even then requires its own authorization memo. The MNL-parquet
  rebuild is the next authorization candidate after O7.

- **Pooled stacking re-run is NOT authorized.**

- **Pooled estimation is NOT authorized.**

- **Welfare computation is NOT authorized.**

- **M1-clean 2016 remains the active JMP baseline.** The GSURv2
  lookup construction produces opportunity-side lookups; it produces
  no estimation result and does not displace the M1-clean baseline.
  M1-clean remains active until explicitly superseded by a later
  SA2 verdict on a final pooled specification.
