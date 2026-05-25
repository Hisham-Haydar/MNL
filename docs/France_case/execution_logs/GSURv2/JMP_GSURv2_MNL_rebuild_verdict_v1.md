# JMP GSURv2 MNL-Parquet Rebuild — Post-Rebuild Verdict v1

Date: 2026-05-20

Rebuild under review: GSURv2 MNL-parquet rebuild for survey years
FR_2015, FR_2016, and FR_2017 — the merge of the three validated
GSURv2 opportunity-year lookups into the survey-year MNL parquets,
replacing the v1-fallback opportunity-side rates with GSURv2 rates.

Output files under review (in `Data/processed/fr/`):
- `fr_2015_RURO_mnl_GSURv2_y2014__{singles,couples}.parquet` + `__mnlmeta.json`
- `fr_2016_RURO_mnl_GSURv2_y2015__{singles,couples}.parquet` + `__mnlmeta.json`
- `fr_2017_RURO_mnl_GSURv2_y2016__{singles,couples}.parquet` + `__mnlmeta.json`

Primary evidence:
- `Results/JMP_GSURv2_MNL_rebuild_report_v2.md` (the rebuild report)
- `Results/JMP_GSURv2_MNL_rebuild_correction_report_v1.md` (the
  stem-and-heading correction report)

Governing documents:
- `docs/JMP_GSURv2_MNL_rebuild_authorization_v1.md` (the rebuild
  authorization, corrected by
  `docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_GSURv2_MNL_rebuild_authorization_correction_v1.md`)
- `docs/JMP_GSURv2_O7_crosswalk_signoff_v1.md` (the O7 sign-off)
- `docs/JMP_GSURv2_multi_year_extension_construction_verdict_v1.md`
  (the GSURv2 lookup construction PASS)
- `docs/RURO_occ_M1_clean_verdict_v1.md` (the active single-year
  JMP baseline)

Interpreter of record: `.venv\Scripts\python.exe`
(`U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe`).

Scope of verdict: post-rebuild quality assessment of the GSURv2
MNL-parquet rebuild. The verdict adjudicates whether the rebuild
followed the authorization, whether the merge was performed
correctly for singles and couples, whether the validation passed,
whether the authorized-stem outputs are byte-identical to the
validated rebuild outputs, whether the rebuilt parquets are valid
GSURv2 inputs for P3a stacking, and which gate is next. The
verdict does not authorise pooled estimation, welfare
implementation, welfare computation, or canonical promotion; those
steps are separately gated.

---

## 1. Verdict

**PASS WITH MINOR DOCUMENTATION CAVEAT.**

The GSURv2 MNL-parquet rebuild is a substantive PASS. All twelve
authorization validation checks (V1–V12) passed for all three
survey years (81 sub-checks, zero failures); no halt condition
(H1–H10) was triggered; the singles `dgn`-to-`sex` mapping was
verified empirically rather than assumed; the couples partner-
specific merges were performed and verified; the v1-fallback GSUR
values were preserved exactly; the row and household counts are
unchanged; the non-GSUR columns are value-identical between input
and output; the active GSUR columns are complete for all active
records; and the input v1-fallback and canonical files are
confirmed unmodified. On the rebuild-correctness criteria, the
rebuild is a clean PASS.

The classification carries the qualifier "WITH MINOR DOCUMENTATION
CAVEAT" for one reason, which is documentation-only and does not
affect the data: the rebuild report v2 §5 (Output stems) lists the
FR_2017 output stem as `fr_2017_RURO_mnl_GSURv2_y2017__`, which is
a typo. The correct opportunity year for FR_2017 is 2016 (the
EUROMOD system year for the FR_2017 survey year, per the alignment
rule). The verdict has verified that the *actual files and
sidecars* carry the correct `GSURv2_y2016` stem, not `y2017`
(§16): the files-created inventory (report v2 §21), the sidecar
inventory (report v2 §13), the survey-year mapping (report v2 §7),
the fallback-preservation table (report v2 §12), and the
correction report's byte-identity table all reference
`fr_2017_RURO_mnl_GSURv2_y2016__`. The `y2017` token appears only
in the §5 output-stems table of report v2 and is a documentation
typo isolated to that one table. Because the actual files,
sidecars, and all other report references are correctly
`GSURv2_y2016`, the `y2017` occurrence is classified as a
documentation typo only, not a data or naming error in the
deliverables.

The rebuild PASSES. The minor documentation caveat (the §5 `y2017`
typo) is recorded for correction in the report (§17) but does not
qualify the data product: the FR_2017 GSURv2-based MNL parquets are
correctly named `GSURv2_y2016`, correctly merged with the
opportunity-year-2016 lookup, and correctly validated.

**The rebuilt MNL parquets are valid GSURv2 inputs for P3a
stacking** (§18). They carry the GSURv2 opportunity-year-aligned
rates for all three survey years, constructed by a single
consistent methodology, and they pass all rebuild validation. They
are the GSURv2-final MNL inputs for the final P3a pooled stacking.

The rebuild PASS advances the pipeline to one immediate next
authorized task and no more: writing the Stage M1 P3a GSURv2
stacking re-run authorization memo (§19, §23). The stacking
execution itself remains separately gated and is not authorized
until that memo exists. Pooled estimation, welfare computation, and
canonical promotion remain separately gated and unauthorised (§20,
§21). The single-year M1-clean 2016 specification remains the active
JMP baseline (§22).

---

## 2. Whether rebuild followed authorization

**Yes. The rebuild followed the authorization (corrected) for all
authorised actions, with the output-stem naming corrected post-
execution to match the authorization.**

The rebuild executed the authorised actions A1–A7 (authorization
§16): it read the three input v1-fallback MNL parquets and the
three GSURv2 lookups with SHA-256 verification (A1); it verified
the actual MNL schema and the GSURv2 `sex` coding (A2); it verified
the singles `dgn` coding empirically and constructed the
`dgn`-to-`sex` mapping (A3); it performed the singles merge with
v1-fallback preservation (A4); it performed the couples partner-
specific merges with v1-fallback preservation (A5); it wrote the
six output parquets with metadata sidecars (A6); and it ran the
twelve validation checks (A7).

The rebuild respected the authorization boundaries. It did not
stack the parquets, estimate any model, compute welfare, promote
any file to a canonical path, or modify any estimation
specification (authorization §17 N1–N7). The input v1-fallback
parquets and the canonical files were not modified (report v2 §20,
§22).

One execution detail required post-execution correction. The
rebuild execution initially wrote to `v2gsurY` output stems
(`fr_2015_RURO_mnl_v2gsurY2014__`, etc.) derived from the task
prompt preflight, rather than the authorised `GSURv2_y` stems
(authorization §8). The correction report records that the
authorised-stem files were subsequently created by byte-identical
file copy of the validated `v2gsurY` parquets, with the original
`v2gsurY` files preserved. The correction is a filename
normalisation, not a data change: the authorised-stem parquets are
byte-identical to the validated `v2gsurY` outputs (§16). The final
deliverables carry the authorised `GSURv2_y` stems, matching the
authorization.

The rebuild followed the authorization. The output-stem mismatch
at execution time was corrected to the authorised stems by byte-
identical copy, and the final files match the authorization.

---

## 3. Whether O7 was satisfied

**Yes. The O7 crosswalk sign-off was satisfied.**

The O7 sign-off granted the user's explicit approval of the
crosswalk (`fr_drgn1_to_nuts2_crosswalk.csv`), the three GSURv2
lookup files, the conceptual merge key `(drgn1, educ3, sex)`, the
survey-year/opportunity-year mapping, and the merge specifications
(singles `dgn`-to-`sex` mapping after verification; couples
partner-specific merges). The rebuild satisfied each element.

The rebuild used the O7-approved crosswalk and the three O7-
approved GSURv2 lookups, verifying each lookup's SHA-256 against
the recorded construction-output hash before merging (report v2 §6:
all three SHAs verified, halt H4 not triggered). The rebuild
applied the O7-approved conceptual merge key `(drgn1, educ3, sex)`
through the singles merge (keyed on `(drgn1, educ3, mapped-sex)`)
and the couples partner-specific merges. The rebuild applied the
O7-approved survey-year/opportunity-year mapping exactly (§8). The
rebuild performed the O7-required `dgn`-coding verification (S1) and
the O7-required couples partner-specific merges (C3, C4).

The O7 sign-off's prohibitions were respected: the rebuild did not
stack, estimate, compute welfare, promote canonically, perform P3b
or P4, or displace M1-clean. The O7 sign-off was the prerequisite
for the rebuild authorization; the rebuild was executed within the
bounds the O7 sign-off and the rebuild authorization established.

The O7 sign-off was satisfied.

---

## 4. Whether actual MNL schema was handled correctly

**Yes. The actual MNL schema was verified and handled correctly,
with the singles/couples asymmetry treated correctly.**

The rebuild verified the actual MNL schema for each input parquet
before merging (report v2 §8). The singles schema (`drgn1`,
`educ3`, `dgn`, `gsur`) was confirmed present for all three survey
years; the couples schema (`drgn1`, `educ3_male`, `educ3_female`,
`gsur_male`, `gsur_female`) was confirmed present for all three
survey years; no required key column was missing or ambiguous (halt
H1 not triggered). The GSURv2 lookup `sex` coding (`F`/`M`,
uppercase strings) was confirmed in all three lookups (halt H3 not
triggered).

The schema asymmetry between singles and couples was handled
correctly. The singles parquet carries a single `dgn` column and a
single `gsur` column, so the singles merge keyed on `(drgn1,
educ3, mapped-sex)` using the verified `dgn`-to-`sex` mapping and
replaced the single `gsur` column (§9). The couples parquet carries
partner-specific `educ3_male`/`educ3_female` and
`gsur_male`/`gsur_female` columns, so the couples merge performed
two partner-specific merges (male on `(drgn1, educ3_male, sex=M)`,
female on `(drgn1, educ3_female, sex=F)`) and replaced the two
partner-specific GSUR columns (§10). The asymmetric handling is
correct: the singles merge used the single sex indicator, and the
couples merge used the two partner-specific education groups with
the respective sex values.

The actual MNL schema was verified before merging and handled
correctly for both household types.

---

## 5. FR_2015 rebuild result

**PASS. FR_2015 → GSURv2 y2014, all validation checks passed.**

The FR_2015 MNL parquets were merged with the GSURv2 opportunity-
year-2014 lookup (`FR_gsur_ruro_v2_stageA_y2014.parquet`, SHA
`740ef6c7…`, verified), per the alignment mapping (FR_2015 survey
year → EUROMOD system year 2014 → opportunity year 2014).

Output: `fr_2015_RURO_mnl_GSURv2_y2014__singles.parquet` (SHA
`889b2f8a…`, 166,900 rows, 76 columns) and
`fr_2015_RURO_mnl_GSURv2_y2014__couples.parquet` (SHA `d44d2292…`,
256,600 rows, 95 columns).

Merge results: the singles merge changed 144,600 of 166,900 GSUR
values (the remainder being cells where the GSURv2 rate coincides
with the v1-fallback rate); the couples merge changed 218,800
`gsur_male` and 230,400 `gsur_female` values. The row counts are
unchanged (singles 166,900, couples 256,600); the household counts
are unchanged (singles 1,669, couples 2,566). The active GSUR
columns are complete for all active records (zero NaN in drgn1 ∈
{1, …, 8}). The fallback columns are present and value-identical to
the input parquet's prior active GSUR values. The active GSUR
ranges are within [0, 1] (singles [0.0537, 0.261], couples male
[0.0536, 0.261], couples female [0.0563, 0.177]).

The FR_2015 rebuild passed all validation checks.

---

## 6. FR_2016 rebuild result

**PASS. FR_2016 → GSURv2 y2015, all validation checks passed.**

The FR_2016 MNL parquets were merged with the GSURv2 opportunity-
year-2015 lookup (`FR_gsur_ruro_v2_stageA_y2015.parquet`, SHA
`f51ad630…`, verified), per the alignment mapping (FR_2016 survey
year → EUROMOD system year 2015 → opportunity year 2015).

Output: `fr_2016_RURO_mnl_GSURv2_y2015__singles.parquet` (SHA
`139cd025…`, 167,600 rows, 76 columns) and
`fr_2016_RURO_mnl_GSURv2_y2015__couples.parquet` (SHA `61e3107b…`,
257,700 rows, 95 columns).

Merge results: the singles merge changed 150,100 of 167,600 GSUR
values; the couples merge changed 224,300 `gsur_male` and 241,500
`gsur_female` values. The row counts are unchanged (singles
167,600, couples 257,700); the household counts are unchanged
(singles 1,676, couples 2,577). The active GSUR columns are
complete for all active records. The fallback columns are present
and value-identical. The active GSUR ranges are within [0, 1]
(singles [0.0532, 0.225], couples male [0.0595, 0.225], couples
female [0.0532, 0.183]).

The FR_2016 household count of 4,253 (1,676 singles + 2,577
couples) matches the established single-year M1-clean 2016 sample
size exactly, confirming that the FR_2016 component of the rebuild
operates on the same sample as the accepted single-year baseline.

The FR_2016 rebuild passed all validation checks.

---

## 7. FR_2017 rebuild result

**PASS. FR_2017 → GSURv2 y2016, all validation checks passed. The
actual output stem is `GSURv2_y2016` (correct); the `y2017` token
in report v2 §5 is a documentation typo only (§16).**

The FR_2017 MNL parquets were merged with the GSURv2 opportunity-
year-2016 lookup (`FR_gsur_ruro_v2_stageA_y2016.parquet`, SHA
`19ac53…`, verified), per the alignment mapping (FR_2017 survey
year → EUROMOD system year 2016 → opportunity year 2016).

Output: `fr_2017_RURO_mnl_GSURv2_y2016__singles.parquet` (SHA
`8fce026d…`, 166,200 rows, 76 columns) and
`fr_2017_RURO_mnl_GSURv2_y2016__couples.parquet` (SHA `2d8dc7ae…`,
229,500 rows, 95 columns).

The output stem is `GSURv2_y2016`, the correct opportunity year for
the FR_2017 survey year. The verdict has verified this against the
files-created inventory (report v2 §21), the sidecar inventory
(report v2 §13), the survey-year mapping (report v2 §7), the
fallback-preservation table (report v2 §12), and the correction
report's byte-identity table — all of which reference
`fr_2017_RURO_mnl_GSURv2_y2016__`. The single `y2017` occurrence in
report v2 §5 (the output-stems table) is a documentation typo
isolated to that table; it is addressed in §16 of this verdict and
recorded for correction in §17.

Merge results: the singles merge changed 160,900 of 166,200 GSUR
values; the couples merge changed 218,400 `gsur_male` and 225,100
`gsur_female` values. The row counts are unchanged (singles
166,200, couples 229,500); the household counts are unchanged
(singles 1,662, couples 2,295). The active GSUR columns are
complete for all active records. The fallback columns are present
and value-identical. The active GSUR ranges are within [0, 1]
(singles [0.0470, 0.234], couples male [0.0470, 0.234], couples
female [0.0478, 0.230]).

The FR_2017 rebuild passed all validation checks. The output files
carry the correct `GSURv2_y2016` stem.

---

## 8. Survey-year / opportunity-year mapping

**CORRECT. The mapping was applied exactly: FR_2015 → y2014,
FR_2016 → y2015, FR_2017 → y2016.**

The rebuild applied the opportunity-year alignment mapping (report
v2 §7) exactly as specified in the authorization §5 and the O7
sign-off. Table 1 reproduces the mapping and the lookup merged for
each survey year.

| Survey year | EUROMOD system year | Opportunity year | Lookup merged | Lookup SHA verified |
|---|---|---|---|---|
| FR_2015 | 2014 | 2014 | `FR_gsur_ruro_v2_stageA_y2014.parquet` | `740ef6c7…` PASS |
| FR_2016 | 2015 | 2015 | `FR_gsur_ruro_v2_stageA_y2015.parquet` | `f51ad630…` PASS |
| FR_2017 | 2016 | 2016 | `FR_gsur_ruro_v2_stageA_y2016.parquet` | `19ac53…` PASS |

The mapping is the load-bearing rebuild constraint: each survey
year's MNL parquet was merged with the GSURv2 lookup for the
correct opportunity year (the EUROMOD system year, which lags the
survey data year by one). A misapplication — for instance, merging
FR_2016 with the y2016 lookup rather than the y2015 lookup — would
reintroduce the one-year-lag error that the year-alignment decision
corrected. The rebuild applied the mapping exactly, and the
validation (V7) confirmed the opportunity-year mapping is correct
for each output (report v2, validation summary).

The mapping is correct. The `y2017` typo in report v2 §5 (§16)
does not reflect a mapping error: the FR_2017 parquet was merged
with the y2016 lookup (the correct opportunity year), as confirmed
by the lookup-used record (report v2 §6, §7) and the actual output
filenames (report v2 §21).

---

## 9. Singles merge validation

**PASS. The singles merge was performed correctly, with the `dgn`-
to-`sex` mapping verified empirically.**

The singles merge keyed the singles MNL parquet to the GSURv2
lookup on `(drgn1, educ3, mapped-sex)`, where the mapped sex is
derived from the verified `dgn`-to-`sex` mapping.

The `dgn` coding was verified empirically, not assumed (report v2
§10), satisfying the O7 sign-off's requirement and the
authorization's S1 step (halt H2 not triggered). The verification
used the FR_2016 singles parquet and four corroborating signals:
the mean number of children is higher for `dgn=0.0` (0.550) than
for `dgn=1.0` (0.188), consistent with `dgn=0` being female; the
mean high-education rate is higher for `dgn=0.0` (0.430) than for
`dgn=1.0` (0.376), consistent with the French female education
pattern; the mean v1-fallback GSUR is lower for `dgn=0.0` (0.090)
than for `dgn=1.0` (0.101), consistent with the female-below-male
pattern in the lookup; and all `idpartner` values are 0.0,
confirming a genuine singles parquet. The four signals jointly
establish the mapping `dgn=1.0` → `M`, `dgn=0.0` → `F`.

The verified mapping is the project-convention mapping (the sample
documentation records `dgn==1` for male, `dgn==0` for female), but
the rebuild confirmed it empirically rather than assuming it, which
is the discipline the O7 sign-off and the authorization required.
The empirical verification is the protection against a silent sex-
inversion error: had the `dgn` coding been the reverse, every
singles GSUR rate would have been merged from the wrong sex cell,
a plausible-looking but incorrect result. The empirical
verification rules this out.

The singles merge replaced the active `gsur` column with the GSURv2
rate keyed on the verified mapping, populated the active `gsur`
column completely for the active sample (zero NaN in drgn1 ∈ {1,
…, 8}, V4 PASS), and the V10 spot-check confirmed a merged GSURv2
rate matches the lookup value exactly for a sampled `(drgn1, educ3,
sex)` key. The singles merge is validated.

---

## 10. Couples merge validation

**PASS. The couples partner-specific merges were performed and
verified.**

The couples merge performed two partner-specific merges (report v2
§11), keying the couples MNL parquet to the GSURv2 lookup once for
each partner. The male-partner merge keyed on `(drgn1, educ3_male,
sex=M)` and wrote the result to the active `gsur_male` column; the
female-partner merge keyed on `(drgn1, educ3_female, sex=F)` and
wrote the result to the active `gsur_female` column. The merges
used the GSURv2 lookup subset for the respective sex (`sex=M` for
the male merge, `sex=F` for the female merge), keyed on the partner-
specific education group.

The completeness check (C5) confirmed that every couples record
with drgn1 ∈ {1, …, 8} received non-null `gsur_male` and
`gsur_female` values (V4 PASS: zero NaN in the active partner-
specific GSUR columns for all three survey years). The V9 partner-
specific merge check confirmed the merges are correct: the report
records the spot-checks for the male merge (a couple's `gsur_male`
matching the lookup value for `(drgn1, educ3_male, M)`) and the
female merge (a couple's `gsur_female` matching the lookup value
for `(drgn1, educ3_female, F)`) for each couples output, with the
expected and actual values matching exactly (report v2 §19: the
per-survey-year V9 checks all PASS, e.g. FR_2017 male
`(drgn1=2, educ3_m=1)` expected 0.101143, actual 0.101143).

The partner-specific merge is the central couples complexity, and
it was performed correctly: the same lookup was merged twice, once
per partner, using the partner-specific education group and the
partner's sex. The couples merge is validated.

---

## 11. Fallback GSUR preservation

**PASS. The v1-fallback GSUR values were preserved exactly under
fallback column names.**

The rebuild preserved the v1-fallback GSUR values before replacing
the active GSUR columns (report v2 §12), satisfying the
authorization's preservation rule (§12) and the validation V6.

For the singles outputs, the existing (v1-fallback) `gsur` values
were copied to a `gsur_v1_fallback` column before the active `gsur`
column was replaced with the GSURv2 rate. For the couples outputs,
the existing `gsur_male` values were copied to a
`gsur_male_v1_fallback` column and the existing `gsur_female`
values to a `gsur_female_v1_fallback` column before the active
partner-specific columns were replaced.

The validation confirmed the fallback columns are value-identical
to the input parquets' prior active GSUR values for all six outputs
(report v2 §12: all PASS exact; halt H6 not triggered). The
preservation is exact: the `gsur_v1_fallback` column equals the
input singles `gsur` column exactly, the `gsur_male_v1_fallback`
column equals the input couples `gsur_male` column exactly, and the
`gsur_female_v1_fallback` column equals the input couples
`gsur_female` column exactly.

The fallback preservation serves the audit and reversibility
purposes the authorization specified: the v1-fallback rates are
recoverable from the fallback columns, and the v1-versus-GSURv2
comparison (which may inform a future robustness exposure) is
available within each GSURv2-based parquet. The preservation is
validated.

---

## 12. Metadata sidecar status

**PASS. Three authorized-stem sidecars are present, each recording
the full rebuild provenance.**

The rebuild wrote three metadata sidecars for the authorized stems
(one per survey year; report v2 §13):
`fr_2015_RURO_mnl_GSURv2_y2014__mnlmeta.json`,
`fr_2016_RURO_mnl_GSURv2_y2015__mnlmeta.json`, and
`fr_2017_RURO_mnl_GSURv2_y2016__mnlmeta.json`. The FR_2017 sidecar
is correctly named `GSURv2_y2016` (not `y2017`), consistent with
the actual output files (§16).

Each sidecar records the survey year, the opportunity year, the
lookup SHA-256, the merge keys, the `dgn`-to-`sex` mapping, the
output file paths and SHA-256 hashes and sizes, the V1–V12 all-pass
status, the build timestamp (`2026-05-20T20:52:59Z`), and the
script version (`inline-rebuild-v1`). Each sidecar carries the
correction note recording that the authorized-stem files were
created by byte-identical copy of the `v2gsurY` files with the
originals preserved.

One sidecar-provenance observation warrants note for the record:
the `script_version` field records `inline-rebuild-v1` (an inline-
script identifier) rather than a git commit hash. This is a
provenance-granularity matter, not a defect: the rebuild was
executed inline, and the merge logic is fully documented in the
rebuild report (§9, §10, §11) and reproducible from the recorded
inputs (the input parquets, the verified lookups, and the verified
`dgn`-to-`sex` mapping). The inline-script identifier is acceptable
for the rebuild provenance given the full documentation, but a
future canonical promotion (separately gated) would benefit from a
committed rebuild script with a git-hash provenance.

The metadata sidecars are present and complete.

---

## 13. Row and household counts

**PASS. Row and household counts are unchanged between input and
output for all six parquets.**

The validation confirmed that the merge added or dropped no rows
and no households (report v2 §14, §15; V1, V2). Table 2 reproduces
the counts.

| Survey year | Singles rows | Singles HH | Couples rows | Couples HH |
|---|---|---|---|---|
| FR_2015 | 166,900 | 1,669 | 256,600 | 2,566 |
| FR_2016 | 167,600 | 1,676 | 257,700 | 2,577 |
| FR_2017 | 166,200 | 1,662 | 229,500 | 2,295 |

The output row counts equal the input row counts exactly for all
six parquets (V1 PASS), and the output household counts equal the
input household counts exactly for all six parquets (V2 PASS). The
merge is a left join that populates GSUR values without altering
the row or household structure: it does not add rows (no key
duplication in the lookup, confirmed by the lookup's unique-key
property), and it does not drop rows (every active record matches a
lookup cell, confirmed by the active-GSUR completeness, §15).

The row and household counts are unchanged. The counts also
reconcile with the P3a construction: the per-component row and
household counts here match the per-component counts recorded in
the P3a construction verdict (e.g., FR_2016 singles 1,676,
FR_2016 couples 2,577), confirming the rebuilt parquets carry the
same sample as the provisional P3a inputs.

---

## 14. Non-GSUR column preservation

**PASS. All non-GSUR columns are value-identical between input and
output.**

The validation confirmed that all columns other than the active
GSUR columns and the added fallback columns are value-identical
between the input and output parquets (report v2 §16; V3; halt H7
not triggered). The merge changed only the active GSUR columns
(replaced with GSURv2 rates) and added the fallback columns (the
preserved v1 rates); all other columns — the demographic columns
(`drgn1`, `educ3`, `dgn`, `deh`, `educH`, `educL`, `educM` for
singles; `drgn1`, `educ3_male`, `educ3_female` for couples), the
income columns, the hours columns, the occupation columns, the
identifiers — are unchanged.

The V3 check spot-checked the key demographic and identifier
columns and confirmed value-identity for all six outputs. The non-
GSUR column preservation is the property that ensures the GSURv2-
based parquets differ from the v1-fallback inputs only in the
opportunity-side GSUR variable: every other modelling input (the
consumption, leisure, wage, occupation, and demographic variables)
is unchanged, so the GSURv2-based parquets are a clean opportunity-
side replacement.

The non-GSUR columns are preserved exactly. The column-count
increase (from the v1-fallback inputs to the 76-column singles and
95-column couples outputs) is accounted for by the added fallback
columns, not by any alteration of the existing columns.

---

## 15. Active GSUR completeness

**PASS. The active GSUR columns are complete for all active
records.**

The validation confirmed that the active GSUR columns are non-null
for every record with drgn1 ∈ {1, …, 8} (report v2 §17; V4; halt
H5 not triggered). For all three survey years, the singles `gsur`
column has zero NaN in the active range, and the couples
`gsur_male` and `gsur_female` columns each have zero NaN in the
active range.

The completeness confirms the merge populated a GSURv2 rate for
every active record: every singles record's `(drgn1, educ3,
mapped-sex)` key matched a lookup cell, and every couples record's
two partner-specific keys matched lookup cells. The complete
coverage follows from the GSURv2 lookups covering all 48 active
cells (drgn1 ∈ {1, …, 8} × educ3 ∈ {0, 1, 2} × sex ∈ {M, F}) with
non-null rates, and from the MNL records' keys falling within those
48 active cells.

The drgn1=9 handling is documented (report v2 §18; V5): the
metropolitan France MNL parquets carry no drgn1=9 records (the DOM
and extra-regio households are excluded upstream), so the drgn1=9
lookup stubs (NaN) do not affect any active record. The verdict
confirms zero drgn1=9 records in all six input and output parquets,
so the active GSUR completeness is not compromised by any drgn1=9
NaN.

The active GSUR columns are complete.

---

## 16. Authorized-stem correction

**VERIFIED. The authorized-stem parquets are byte-identical to the
validated rebuild outputs. The FR_2017 stem is correctly
`GSURv2_y2016` in the actual files; the `y2017` token in report v2
§5 is a documentation typo only.**

The rebuild execution initially wrote to `v2gsurY` output stems
(`fr_2015_RURO_mnl_v2gsurY2014__`, etc.) rather than the authorised
`GSURv2_y` stems. The correction report records that the
authorised-stem files were created by byte-identical file copy of
the validated `v2gsurY` parquets, with the originals preserved. The
verdict confirms the byte-identity from the correction report's
SHA-256 table: each authorised-stem parquet's full SHA-256 equals
its `v2gsurY` source's SHA-256 (e.g.,
`fr_2015_RURO_mnl_GSURv2_y2014__singles.parquet` SHA `889b2f8a…`
matches the source). All six byte-identity checks PASS. The
correction is a filename normalisation; no data value was changed.

The FR_2017 output-stem issue is resolved as a documentation typo,
per the verdict requirement. The verdict examined every reference
to the FR_2017 output stem across the rebuild report v2 and the
correction report:

| Location | FR_2017 stem reference | Correct (`y2016`)? |
|---|---|---|
| Report v2 §5 (Output stems table) | `fr_2017_RURO_mnl_GSURv2_y2017__` | NO — typo |
| Report v2 §7 (mapping; lookup `y2016`) | opportunity year 2016 | YES |
| Report v2 §12 (fallback table) | `fr_2017_RURO_mnl_GSURv2_y2016__` | YES |
| Report v2 §13 (sidecar inventory) | `fr_2017_RURO_mnl_GSURv2_y2016__mnlmeta.json` | YES |
| Report v2 §21 (files created) | `fr_2017_RURO_mnl_GSURv2_y2016__{singles,couples}.parquet` | YES |
| Correction report §3 (byte-identity) | `fr_2017_RURO_mnl_GSURv2_y2016__{singles,couples}.parquet` | YES |
| Correction report §6 (data integrity) | `fr_2017_RURO_mnl_GSURv2_y2016__{singles,couples}.parquet` (SHA `8fce026d…`, `2d8dc7ae…`) | YES |

The `y2017` token appears in exactly one location — the report v2
§5 output-stems table — and is contradicted by every other
reference, including the actual files-created inventory and the
sidecar inventory. The verdict therefore classifies the `y2017`
occurrence as a documentation typo isolated to report v2 §5, not a
data or naming error in the deliverables. The actual FR_2017 output
files and sidecar are `fr_2017_RURO_mnl_GSURv2_y2016__`, the
correct opportunity year. This satisfies the verdict requirement:
the `y2017` is a documentation typo only, because the actual files
and sidecars are `GSURv2_y2016`.

The authorized-stem correction is verified: the files are byte-
identical to the validated outputs, and the FR_2017 stem is
correctly `GSURv2_y2016` in the deliverables.

---

## 17. Documentation issues or remaining report-cleanup items

Two documentation items are recorded for cleanup. Neither affects
the data or the rebuild PASS.

(D1) **Report v2 §5 FR_2017 stem typo.** The output-stems table in
report v2 §5 lists the FR_2017 output stem as
`fr_2017_RURO_mnl_GSURv2_y2017__`. The correct stem is
`fr_2017_RURO_mnl_GSURv2_y2016__` (§16). A one-line correction to
report v2 §5 is recommended, replacing `y2017` with `y2016`, so
that the §5 table is consistent with §7, §12, §13, §21, and the
actual files. This is a documentation typo correction; the actual
files are already correctly named.

(D2) **Sidecar `script_version` granularity.** The sidecar
`script_version` field records `inline-rebuild-v1` rather than a
git commit hash (§12). This is acceptable for the rebuild
provenance given the full documentation of the merge logic in the
rebuild report, but a future canonical promotion (separately gated)
would benefit from a committed rebuild script with a git-hash
provenance. This is a provenance-granularity note for the
canonical-promotion stage, not a rebuild defect.

Both items are documentation-level. D1 is a one-line typo
correction to the report; D2 is a provenance-granularity note for a
future stage. Neither blocks the rebuild PASS, the validity of the
GSURv2-based parquets as P3a inputs (§18), or the next gate (§19).

The git-tracking status (the six output parquets are present on
disk but not git-committed, owing to the `Data/` git-exclusion) is
noted but is not a documentation issue: the provenance is carried by
the committed reports and the sidecars, and the file SHA-256 hashes
recorded in the report provide attestation.

---

## 18. Whether rebuilt MNL parquets are now GSURv2-final for P3a stacking

**Yes. The rebuilt MNL parquets are valid GSURv2-final inputs for
the final P3a pooled stacking.**

The rebuilt MNL parquets satisfy the conditions for GSURv2-final
P3a stacking inputs. Each of the three survey-year MNL parquet pairs
(singles, couples) carries the GSURv2 opportunity-year-aligned rates
in the active GSUR columns (`gsur` for singles; `gsur_male`,
`gsur_female` for couples), merged from the correct opportunity-year
lookup (y2014 for FR_2015, y2015 for FR_2016, y2016 for FR_2017).
The opportunity-side variable is now constructed by a single
consistent GSURv2 methodology across all three survey years, which
is the condition the year-alignment decision §6 established for a
final pooled build: GSURv2 rebuilt for each opportunity year before
any year's parquet is promoted to final status.

The rebuilt parquets pass all rebuild validation (§1, all V1–V12
PASS), preserve the sample structure (row and household counts
unchanged, §13), preserve the non-GSUR modelling inputs (value-
identical, §14), and carry complete active GSUR coverage (§15).
They are a clean opportunity-side replacement of the v1-fallback
inputs: identical in every modelling variable except the
opportunity-side GSUR, which now carries the GSURv2 rates.

The rebuilt parquets are therefore the GSURv2-final MNL inputs for
the final P3a pooled stacking. The provisional P3a pooled dataset
(`fr_p3a_harmonised.parquet`, labelled
`provisional_v1_fallback_opportunity_year_aligned`) was constructed
from the v1-fallback MNL parquets; a final P3a pooled stacking re-
run against the GSURv2-based MNL parquets would produce a final
(non-provisional) pooled dataset whose opportunity-side variable
carries the GSURv2 rates, dropping the `v1_fallback` qualifier from
the provisioning label.

The rebuilt MNL parquets are GSURv2-final for P3a stacking. The
final P3a stacking re-run is the next gate (§19).

---

## 19. Whether Stage M1 P3a GSURv2 stacking re-run is authorized

**The immediate next authorized task is to write the Stage M1 P3a
GSURv2 stacking re-run authorization memo. The stacking execution
itself remains separately gated and is not authorized until that
memo exists.**

The rebuild PASS establishes that the GSURv2-based MNL parquets are
valid GSURv2-final inputs for P3a stacking (§18). The next gate in
the multi-year pipeline is the Stage M1 P3a GSURv2 pooled stacking
re-run: the re-execution of the Stage M1 pooled stacking pipeline
against the GSURv2-based MNL parquets, producing a final (non-
provisional) pooled dataset.

This verdict advances the pipeline to the stacking authorization
memo as the immediate next task, and only that. The stacking re-run
does not execute on the basis of this verdict alone: a separate
stacking authorization memo must first be written, specifying the
stacking scope (the inputs — the six GSURv2-based MNL parquets; the
CPI harmonisation; the stacked-ID engineering; the cluster-key
annotation; the V1–V9 stacking validation; the output naming
dropping the `v1_fallback` qualifier). The stacking re-run executes
the same Stage M1 pipeline that produced the provisional P3a
dataset, with the GSURv2-based MNL parquets replacing the v1-
fallback MNL parquets as inputs, but only once that authorization
memo exists and authorizes execution.

The stacking re-run is the next gate because it is the immediate
downstream step that consumes the GSURv2-based MNL parquets, and
because it is the step that produces the final (non-provisional)
pooled dataset required for any final pooled estimation. The
stacking re-run does not estimate any model or compute any welfare;
it produces the final pooled dataset. But the execution of the
stacking re-run is gated on its own authorization memo; this verdict
does not authorize that execution.

No step beyond the stacking authorization memo is authorised by this
verdict. The stacking re-run's own verdict (a strict post-stacking
construction verdict, paralleling the provisional P3a construction
verdict) will adjudicate whether the final pooled dataset is
correctly constructed, and only then will the subsequent gates
(the cluster-robust SE wrapper, the pooled specification, the
pooled estimation) be considered.

---

## 20. Whether pooled estimation is authorized

**No. Pooled estimation is NOT authorized.**

Pooled estimation — provisional or final — is not authorised by
this post-rebuild verdict. The final pooled estimation remains
gated behind several prerequisites that are not met: the final
(non-provisional) pooled dataset does not exist (the Stage M1 P3a
GSURv2 stacking re-run authorization memo has not yet been written
(§19); no cluster-robust standard-error wrapper
exists for the RURO estimator (P3a construction verdict §17); and
no pooled estimation specification exists (P3a construction verdict
§17).

The rebuild PASS advances the empirical prerequisite chain toward
final pooled estimation — it produces the GSURv2-final MNL inputs —
but it does not authorise the estimation. Pooled estimation is
several gates distant (stacking re-run → stacking verdict →
cluster-robust SE wrapper → pooled specification → pooled
estimation → SA2 verdict) and is not authorised.

---

## 21. Whether welfare computation is authorized

**No. Welfare computation is NOT authorized.**

Welfare implementation and welfare computation are not authorised
by this post-rebuild verdict. Welfare computation requires a
welfare scaffolding implementation, an accepted empirical baseline,
and the welfare-measurement decisions; none of these is provided or
advanced by the GSURv2 MNL-parquet rebuild. The rebuild is a data-
construction step on the opportunity-side input; it produces no
estimation result and no welfare quantity.

Welfare computation remains gated behind the pooled-estimation path
(or the single-year M1-clean baseline, whichever becomes the
operative welfare baseline) and behind the welfare scaffolding
implementation. It is not authorised.

---

## 22. Remaining blockers

The rebuild itself has no remaining blockers — it is complete and
PASSED (§1).

*Downstream gates.* Table 3 lists the gates between the completed
rebuild and the eventual final pooled estimation and welfare
computation.

| Downstream step | Gating condition |
|---|---|
| Stage M1 P3a GSURv2 stacking re-run authorization memo | Immediate next authorized task (§19, §23); writing the memo is the gate before stacking execution |
| Stage M1 P3a GSURv2 stacking re-run execution | Not authorized until the stacking authorization memo exists |
| Stacking re-run verdict | Stacking re-run complete |
| Pooled estimation | Final pooled dataset + cluster-robust SE wrapper + pooled specification |
| Welfare computation | Accepted empirical baseline + welfare scaffolding implementation |

*Documentation cleanup (non-blocking).* Two documentation items
(§17) are recorded for cleanup: the report v2 §5 FR_2017 stem typo
(D1, a one-line correction) and the sidecar `script_version`
granularity (D2, a provenance note for the canonical-promotion
stage). Neither blocks the next gate; both may be addressed at any
time.

The immediate next authorized task is writing the Stage M1 P3a
GSURv2 stacking re-run authorization memo (§19, §23). The stacking
execution itself is not authorized until that memo exists.

M1-clean 2016 remains the active JMP baseline (per the O7 sign-off,
the construction verdict, and the rebuild authorization), displaced
only by a future SA2 verdict on a final pooled specification.

---

## 23. Immediate next task

**The immediate next authorized task is to write the Stage M1 P3a
GSURv2 stacking re-run authorization memo. The stacking execution
itself remains separately gated and is not authorized until that
memo exists.**

The immediate next task is to write the stacking re-run authorization
memo (a Claude Project chat document), which specifies the stacking
re-run scope: the six GSURv2-based MNL parquets as inputs (replacing
the v1-fallback inputs); the CPI harmonisation (base year 2016, the
same INSEE factors as the provisional P3a build); the stacked-ID
engineering (the numeric int64 UID scheme); the cluster-key
annotation (`idorighh` at the raw household level); the V1–V9
stacking validation; and the output naming (dropping the
`v1_fallback` qualifier, producing a final non-provisional pooled
dataset, e.g., `fr_p3a_GSURv2_final_harmonised.parquet`). The
stacking execution itself is not authorized by this verdict and may
not proceed until that authorization memo exists.

The sequencing from the current point is:

1. *Stage M1 P3a GSURv2 stacking re-run authorization memo* (Claude
   Project chat). The authorization specifying the stacking re-run
   scope. This is the immediate next authorized task.

2. *Stage M1 P3a GSURv2 stacking re-run* (Claude Code Sonnet),
   conditional on the authorization memo existing and authorizing
   execution. The re-execution of the Stage M1 pipeline against the
   GSURv2-based MNL parquets, producing the final pooled dataset.

3. *Stage M1 P3a GSURv2 stacking construction verdict* (Claude
   Project chat), conditional on the stacking re-run. A strict
   construction verdict on the final pooled dataset, paralleling the
   provisional P3a construction verdict.

4. *Pooled estimation gates* (cluster-robust SE wrapper, pooled
   specification, pooled estimation, SA2 verdict), each separately
   gated and not authorised until the final pooled dataset is
   constructed and verdicted.

A parallel, non-blocking task is the documentation cleanup (§17 D1,
D2), which may be addressed at any time independently of the
stacking re-run.

Tasks explicitly not authorised by this verdict, and not the
immediate next task: pooled estimation (§20), welfare computation
(§21), canonical promotion, P3b, P4, changes to the M1-clean or
M1-naive estimation specifications, and the displacement of the
M1-clean 2016 baseline (§22).

---

**Required final statements**

- **The GSURv2 MNL-parquet rebuild PASSES** (with the minor
  documentation caveat of the report v2 §5 `y2017` typo, which is a
  documentation-only matter; the actual FR_2017 files and sidecars
  are correctly `GSURv2_y2016`). All V1–V12 checks passed for all
  three survey years, and the authorized-stem parquets are byte-
  identical to the validated rebuild outputs.

- **The rebuilt MNL parquets are valid GSURv2-final inputs for P3a
  stacking.** The opportunity-side GSUR variable carries the GSURv2
  opportunity-year-aligned rates across all three survey years.

- **The immediate next authorized task is to write the Stage M1 P3a
  GSURv2 stacking re-run authorization memo. The stacking execution
  itself remains separately gated and is not authorized until that
  memo exists.**

- **Pooled estimation is NOT authorized.** Separately gated behind
  the stacking re-run, the stacking verdict, the cluster-robust SE
  wrapper, and the pooled specification.

- **Welfare implementation and welfare computation are NOT
  authorized.** Separately gated behind an accepted empirical
  baseline and the welfare scaffolding implementation.

- **M1-clean 2016 remains the active JMP baseline.** Displaced only
  by a later SA2 verdict explicitly promoting a final pooled
  specification.
