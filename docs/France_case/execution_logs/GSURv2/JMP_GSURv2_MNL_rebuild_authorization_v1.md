# JMP GSURv2 MNL-Parquet Rebuild — Authorization v1

Date: 2026-05-20

Specification class: rebuild authorization memo. The memo
authorises the GSURv2 MNL-parquet rebuild — the merge of the three
validated GSURv2 opportunity-year lookups into the FR_2015,
FR_2016, and FR_2017 MNL parquets, replacing the v1-fallback
opportunity-side rates with GSURv2 rates — following the O7
crosswalk sign-off. It is an authorization document for the MNL-
parquet rebuild only; it does not authorise the pooled stacking
re-run, pooled estimation, welfare computation, canonical
promotion, P3b, or P4.

Reference documents:
- `docs/JMP_GSURv2_O7_crosswalk_signoff_v1.md` (the O7 sign-off
  granting the crosswalk and merge key)
- `docs/JMP_GSURv2_multi_year_extension_construction_verdict_v1.md`
  (the construction verdict classifying the lookup construction
  PASS, with correction
  `docs/JMP_GSURv2_multi_year_extension_construction_verdict_correction_v1.md`)
- `Results/JMP_GSURv2_multi_year_extension_validation_report_v1.md`
  (the validation report corroborating the construction PASS)
- `docs/JMP_GSURv2_multi_year_extension_construction_report_v1.md`
  (the construction report with the lookup provenance)
- `docs/France_case/JMP_GSUR_year_alignment_decision_v1.md` (the opportunity-
  year alignment rule)

Interpreter of record: `.venv\Scripts\python.exe`
(`U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe`).

Scope of memo: the memo authorises the GSURv2 MNL-parquet rebuild
for the three survey years, specifying the input stems, the GSURv2
lookup inputs, the output stems, the actual MNL schema, the merge
logic for singles and couples, the v1-fallback preservation rule,
the active GSUR variable naming rule, the metadata requirements,
the validation checks, the halt conditions, and the rebuild report.
The memo does not authorise the pooled stacking re-run, pooled
estimation, welfare computation, canonical promotion, P3b, P4, or
any change to the M1-clean or M1-naive estimation specifications;
those steps are separately gated.

---

## 1. Purpose

The purpose of this memo is to authorise the GSURv2 MNL-parquet
rebuild: the merge of the three validated GSURv2 opportunity-year
lookups (y2014, y2015, y2016) into the FR_2015, FR_2016, and
FR_2017 MNL parquets, producing GSURv2-based MNL parquets in which
the opportunity-side GSUR variable carries the GSURv2 education-
and sex-stratified rates rather than the v1-fallback rates.

The rebuild is authorised because two preconditions are now met.
First, the GSURv2 lookup construction PASSED (the construction
verdict and the validation report both classify the construction
PASS, with all three lookups validated). Second, the O7 crosswalk
sign-off has been granted (the user's explicit approval of the
crosswalk and the merge key for the MNL merge). The MNL-parquet
rebuild was the next authorization candidate after the O7 sign-off
(construction verdict §11); the O7 sign-off being granted, the
rebuild is now authorised.

The memo specifies the rebuild precisely: the survey-year-to-
opportunity-year mapping (§5), the input and output MNL stems (§6,
§8), the GSURv2 lookup inputs (§7), the actual MNL schema (§9), the
merge logic for singles and couples (§10, §11), the v1-fallback
preservation rule (§12), the active GSUR variable naming rule
(§13), the metadata requirements (§14), the validation checks
(§15), the halt conditions (§18), and the rebuild report (§19). The
memo's operational deliverable is the exact Claude Code task (§20).

The rebuild produces GSURv2-based MNL parquets. It does not stack
them, estimate from them, or compute welfare from them; those steps
are separately gated (§17). The single-year M1-clean 2016
specification remains the active JMP baseline throughout (§17).

---

## 2. Current status

The current status of the multi-year extension is that the GSURv2
lookup construction is complete and validated, the O7 sign-off is
granted, and the MNL-parquet rebuild is the next authorised step.

The GSURv2 lookup construction PASSED. The construction verdict
classifies the construction PASS, confirming that all three
opportunity-year lookups (y2014, y2015, y2016) were constructed
under Option B, the y2016 value-identity gate passed exactly
(maximum absolute `gsur` difference 0.0, byte-identical to the
existing baseline), and the y2015 and y2014 constructions passed
all validation. The validation report corroborates: all validation
checks pass for all three years, with the IDF parity check at 0.0
for every year and the L5 benchmark differences small and recorded.

The three GSURv2 lookups exist in `Data/external/` with confirmed
SHA-256 hashes: `FR_gsur_ruro_v2_stageA_y2016.parquet` (`19ac53…`,
7,444 bytes, byte-identical to the existing baseline),
`FR_gsur_ruro_v2_stageA_y2015.parquet` (`f51ad630…`, 7,433 bytes),
and `FR_gsur_ruro_v2_stageA_y2014.parquet` (`740ef6c7…`, 7,441
bytes). Each carries a complete 14-field provenance sidecar.

The MNL parquets currently carry the v1-fallback opportunity-side
rates. The provisional P3a pooled dataset is labelled
`provisional_v1_fallback_opportunity_year_aligned` because the
GSURv2 lookups have not yet been merged into the MNL parquets. The
MNL-parquet rebuild this memo authorises performs that merge,
producing GSURv2-based MNL parquets that replace the v1-fallback
rates with GSURv2 rates.

The O7 crosswalk sign-off is granted (§4). The MNL-parquet rebuild
is the next authorised step, and this memo authorises it.

---

## 3. Evidence from GSURv2 construction

The MNL-parquet rebuild rests on the GSURv2 construction evidence,
which establishes that the three lookups are correctly constructed
and ready for merge.

The construction PASS is established by the construction verdict
and the validation report. Three pieces of construction evidence
are load-bearing for the rebuild.

First, the IDF parity check returned exactly 0.0 for all three
years (construction report §5–§7; validation report §10). The IDF
parity check confirms that the crosswalk-weighted aggregation
reduces correctly to the single-component FR10 value for the
single-component Île-de-France region. Because the rebuild merges
the crosswalk-derived drgn1-level GSUR assignments into the MNL
records, the IDF parity at 0.0 confirms that the crosswalk
application in the lookup construction is correct, which is the
foundation for the merge.

Second, the lookup schema is the eleven-column Stage A schema
(construction report §5), of which the merge consumes the keys
`(drgn1, educ3, sex)` and the value `gsur`. The validation report
§4 confirms the keys `(drgn1, educ3, sex)` are unique within each
year-tagged lookup (no duplicate keys), which is the precondition
for an unambiguous merge: each `(drgn1, educ3, sex)` cell maps to
exactly one GSURv2 rate.

Third, the lookups cover all 48 active cells (drgn1 ∈ {1, …, 8} ×
educ3 ∈ {0, 1, 2} × sex ∈ {F, M}) with non-null `gsur`, and the 6
drgn1=9 stub cells carry NaN (validation report §7). The complete
coverage of the 48 active cells ensures that the merge populates a
GSURv2 rate for every active MNL record; the drgn1=9 NaN handling
must be documented in the rebuild (§15), but no France metropolitan
MNL record carries drgn1=9 (the DOM and extra-regio households are
excluded upstream), so the drgn1=9 stubs do not affect the active
sample.

The construction evidence establishes that the three GSURv2
lookups are correctly constructed, uniquely keyed, and completely
covering the active cells. The lookups are ready for the merge.

---

## 4. O7 crosswalk sign-off status

**The O7 crosswalk sign-off is GRANTED.**

The O7 sign-off (`docs/JMP_GSURv2_O7_crosswalk_signoff_v1.md`)
grants the user's explicit approval of the crosswalk and the merge
key for the GSURv2 MNL-parquet rebuild. The sign-off approves:

The crosswalk: `Data/external/fr_drgn1_to_nuts2_crosswalk.csv`.

The GSURv2 lookup files:
`Data/external/FR_gsur_ruro_v2_stageA_y2014.parquet`,
`Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet`, and
`Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet`.

The conceptual merge key: `(drgn1, educ3, sex)`.

The survey-year / opportunity-year mapping: FR_2015 uses GSURv2
opportunity year 2014; FR_2016 uses GSURv2 opportunity year 2015;
FR_2017 uses GSURv2 opportunity year 2016.

The merge specifications: for singles, the rebuild must map GSURv2
`sex` to the observed MNL `dgn` coding after verifying the coding
convention; for couples, the rebuild must use partner-specific
merges (male partner `(drgn1, educ3_male, sex = male)`, female
partner `(drgn1, educ3_female, sex = female)`).

The O7 sign-off explicitly does not authorise the MNL-parquet
rebuild by itself, the pooled Stage M1 stacking re-run, pooled
estimation, welfare implementation or computation, canonical
promotion, P3b or P4, or the replacement of M1-clean 2016 as the
active JMP baseline. The O7 sign-off is the crosswalk-and-merge-key
approval that is the prerequisite for the MNL-parquet rebuild
authorization; this memo is that rebuild authorization, and it
authorises the rebuild within the bounds the O7 sign-off and this
memo establish.

The O7 sign-off being granted, the MNL-parquet rebuild precondition
is met. The rebuild is authorised by this memo.

---

## 5. Survey-year / opportunity-year mapping

The rebuild merges each survey year's MNL parquet with the GSURv2
lookup for the correct opportunity year, per the alignment rule
(year-alignment decision §2) and the O7 sign-off. Table 1
specifies the mapping.

| Survey year | EUROMOD system year | GSURv2 opportunity year | GSURv2 lookup |
|---|---|---|---|
| FR_2015 | 2014 | 2014 | `FR_gsur_ruro_v2_stageA_y2014.parquet` |
| FR_2016 | 2015 | 2015 | `FR_gsur_ruro_v2_stageA_y2015.parquet` |
| FR_2017 | 2016 | 2016 | `FR_gsur_ruro_v2_stageA_y2016.parquet` |

The required decisions are confirmed: FR_2015 must use GSURv2
y2014; FR_2016 must use GSURv2 y2015; FR_2017 must use GSURv2
y2016. The mapping is the opportunity-year alignment that the
year-alignment decision established and the O7 sign-off approved:
the GSUR opportunity year equals the EUROMOD system year, which
lags the survey data year by one.

The mapping is the load-bearing rebuild constraint. A merge that
keyed a survey year's MNL parquet to the wrong opportunity year's
GSURv2 lookup (for instance, FR_2016 to y2016 rather than y2015)
would reintroduce the one-year-lag error that the year-alignment
decision corrected. The rebuild must apply the mapping exactly: the
y2014 lookup to FR_2015, the y2015 lookup to FR_2016, the y2016
lookup to FR_2017. The validation (§15) confirms the mapping is
applied correctly.

---

## 6. Input MNL stems

The rebuild reads the three survey-year MNL parquets currently
carrying the v1-fallback opportunity-side rates. Table 2 specifies
the input stems.

| Survey year | Input MNL stem | GSUR source (current) |
|---|---|---|
| FR_2015 | `fr_2015_RURO_mnl_v1gsurY2014__` | v1 fallback, opportunity year 2014 |
| FR_2016 | `fr_2016_RURO_mnl_v1gsurY2015__` | v1 fallback, opportunity year 2015 |
| FR_2017 | `fr_2017_RURO_mnl_v1gsurY2016__` | v1 fallback, opportunity year 2016 |

Each input stem has two component parquets (singles and couples),
following the `__singles.parquet` / `__couples.parquet` convention.
The input parquets carry the v1-fallback opportunity-year-aligned
GSUR rates: the GSUR opportunity year is already correctly aligned
(y2014 for FR_2015, y2015 for FR_2016, y2016 for FR_2017), but the
rates are v1-fallback rather than GSURv2.

The rebuild reads the input parquets, preserves the v1-fallback
GSUR values under fallback column names (§12), and replaces the
active GSUR columns with the GSURv2 rates merged from the lookups
(§10, §11). The input parquets are read-only inputs; the rebuild
does not modify them in place (§8 specifies separate output stems).

---

## 7. GSURv2 lookup inputs

The rebuild merges from the three GSURv2 opportunity-year lookups
validated by the construction. Table 3 specifies the lookup inputs.

| Opportunity year | Lookup file | SHA-256 | Rows |
|---|---|---|---|
| 2014 | `Data/external/FR_gsur_ruro_v2_stageA_y2014.parquet` | `740ef6c7…` | 54 |
| 2015 | `Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet` | `f51ad630…` | 54 |
| 2016 | `Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet` | `19ac53…` | 54 |

Each lookup carries the eleven-column Stage A schema. The merge
consumes the key columns `(drgn1, educ3, sex)` and the value column
`gsur`. The 54 rows comprise 48 active cells (drgn1 ∈ {1, …, 8} ×
educ3 ∈ {0, 1, 2} × sex ∈ {M, F}) with non-null `gsur` and 6
drgn1=9 stub cells with NaN `gsur`.

The rebuild must verify each lookup's SHA-256 against the recorded
value (Table 3) before merging, to confirm the lookup is the
validated construction output and has not been modified. A SHA-256
mismatch halts the rebuild (§18).

The lookups are the approved GSURv2 lookup files named in the O7
sign-off. No other GSUR source (the v1 fallback, the un-tagged
y2016 baseline) is used as a merge input; the v1-fallback rates are
read from the input MNL parquets only for preservation (§12), not
as a merge source.

---

## 8. Output MNL stems

The rebuild writes three GSURv2-based MNL parquet stems, year-
tagged to encode the GSURv2 source and the opportunity year. Table
4 specifies the output stems.

| Survey year | Output MNL stem |
|---|---|
| FR_2015 | `fr_2015_RURO_mnl_GSURv2_y2014__` |
| FR_2016 | `fr_2016_RURO_mnl_GSURv2_y2015__` |
| FR_2017 | `fr_2017_RURO_mnl_GSURv2_y2016__` |

Each output stem has two component parquets (singles and couples),
following the `__singles.parquet` / `__couples.parquet`
convention. The output stems encode the GSURv2 source
(`GSURv2`) and the opportunity year (`y2014`, `y2015`, `y2016`),
distinguishing them from the v1-fallback input stems
(`v1gsurY2014`, etc.).

The output stems are new files. The rebuild does not overwrite the
input v1-fallback parquets, the canonical 2016 M1-clean parquets,
or any previous estimation output. The no-overwrite constraint is a
rebuild requirement (§16, §18): the rebuild writes to the new
GSURv2-based output stems, preserving the input and canonical files
intact. If an output stem already exists (for instance, from an
aborted prior rebuild), the rebuild must not overwrite it silently:
the existing file is archived or the rebuild halts and documents
the existing file (§18).

---

## 9. Actual MNL schema

The rebuild operates on the actual MNL schema, which differs
between singles and couples and which the O7 sign-off documented.
The rebuild must use the actual schema, not an assumed schema.

*Singles MNL schema.* The singles parquets carry the opportunity-
side and demographic columns:
- `drgn1` (the EUROMOD region code)
- `educ3` (the education group, 0/1/2)
- `dgn` (the sex/gender indicator)
- `gsur` (the active opportunity-side GSUR variable)

*Couples MNL schema.* The couples parquets carry partner-specific
columns:
- `drgn1` (the household region code)
- `educ3_male` (the male partner's education group)
- `educ3_female` (the female partner's education group)
- `gsur_male` (the active male-partner GSUR variable)
- `gsur_female` (the active female-partner GSUR variable)

*GSURv2 lookup schema.* The lookup carries:
- `drgn1` (the region code)
- `educ3` (the education group)
- `sex` (the sex, in the lookup's coding)
- `gsur` (the GSURv2 rate)

The schema asymmetry is the central rebuild complexity. The singles
parquet carries a single `dgn` column and a single `gsur` column,
so the singles merge keys on `(drgn1, educ3, dgn↔sex)` and replaces
the single `gsur` column (§10). The couples parquet carries
partner-specific `educ3_male`/`educ3_female` and
`gsur_male`/`gsur_female` columns, so the couples merge performs two
partner-specific merges and replaces the two partner-specific GSUR
columns (§11).

The rebuild must verify the actual schema of each input parquet
before merging: it must confirm that the singles parquet carries
`drgn1`, `educ3`, `dgn`, `gsur`, and that the couples parquet
carries `drgn1`, `educ3_male`, `educ3_female`, `gsur_male`,
`gsur_female`. If a required key column is missing or ambiguous,
the rebuild halts and reports (§18).

---

## 10. Merge logic for singles

The singles merge keys the singles MNL parquet to the GSURv2 lookup
on `(drgn1, educ3, sex)`, after mapping the MNL `dgn` column to the
GSURv2 `sex` column. The merge replaces the active `gsur` column
with the GSURv2 rate.

The merge procedure is:

(S1) **Verify the `dgn` coding.** The rebuild must verify the MNL
`dgn` coding convention before merging — it must not assume the
coding silently. The project convention (established in the sample
documentation) is `dgn==1` for male and `dgn==0` for female, but
the rebuild must confirm this empirically against the singles
parquet (for instance, by cross-tabulating `dgn` against a known
sex-correlated variable, or by confirming the coding against the
EUROMOD variable documentation) before constructing the
`dgn`-to-`sex` mapping. The verified mapping is recorded in the
rebuild report (§19).

(S2) **Verify the GSURv2 `sex` coding.** The rebuild must confirm
the GSURv2 lookup's `sex` coding (whether `M`/`F`, `male`/`female`,
or another coding) before constructing the mapping. The lookup
schema (construction report §5) records `sex` values `F` and `M`.
The rebuild confirms this and documents the mapping explicitly.

(S3) **Construct the `dgn`-to-`sex` mapping.** Using the verified
`dgn` coding (S1) and the verified GSURv2 `sex` coding (S2), the
rebuild constructs the mapping from the MNL `dgn` value to the
GSURv2 `sex` value (for instance, `dgn==1` → `sex=="M"`, `dgn==0`
→ `sex=="F"`, subject to the verified coding). The mapping is
documented explicitly in the rebuild report.

(S4) **Preserve the v1-fallback `gsur`.** Before replacing the
active `gsur` column, the rebuild copies the existing `gsur` values
to a `gsur_v1_fallback` column (§12).

(S5) **Merge and replace.** The rebuild merges the singles parquet
to the GSURv2 lookup on `(drgn1, educ3, mapped-sex)` and writes the
merged GSURv2 rate to the active `gsur` column. Every singles MNL
record with drgn1 ∈ {1, …, 8} receives a non-null GSURv2 `gsur`
value; the merge must populate the active `gsur` column completely
for the active sample.

The singles merge replaces the single `gsur` column with the
GSURv2 rate, keyed on the verified `dgn`-to-`sex` mapping. The
active GSUR variable for singles remains `gsur` (§13). The v1-
fallback values are preserved in `gsur_v1_fallback` (§12).

---

## 11. Merge logic for couples

The couples merge performs two partner-specific merges, keying the
couples MNL parquet to the GSURv2 lookup once for the male partner
and once for the female partner, and replaces the two partner-
specific GSUR columns.

The merge procedure is:

(C1) **Verify the GSURv2 `sex` coding.** As for singles (S2), the
rebuild confirms the GSURv2 lookup's `sex` coding (`F`/`M` per the
lookup schema) before constructing the partner-specific merges.

(C2) **Preserve the v1-fallback partner GSUR columns.** Before
replacing the active partner-specific GSUR columns, the rebuild
copies the existing `gsur_male` values to a `gsur_male_v1_fallback`
column and the existing `gsur_female` values to a
`gsur_female_v1_fallback` column (§12).

(C3) **Male-partner merge.** The rebuild merges the couples parquet
to the GSURv2 lookup on `(drgn1, educ3_male, sex = male)` and writes
the merged GSURv2 rate to the active `gsur_male` column. The male-
partner merge keys on the male partner's education group
(`educ3_male`) and the male sex value.

(C4) **Female-partner merge.** The rebuild merges the couples
parquet to the GSURv2 lookup on `(drgn1, educ3_female, sex = female)`
and writes the merged GSURv2 rate to the active `gsur_female`
column. The female-partner merge keys on the female partner's
education group (`educ3_female`) and the female sex value.

(C5) **Completeness check.** Every couples MNL record with drgn1 ∈
{1, …, 8} receives non-null GSURv2 `gsur_male` and `gsur_female`
values; the two partner-specific merges must populate the active
partner-specific GSUR columns completely for the active sample.

The couples merge replaces the two partner-specific GSUR columns
with the GSURv2 rates, keyed on the partner-specific education
groups and the respective sex values. The active GSUR variables for
couples remain `gsur_male` and `gsur_female` (§13). The v1-fallback
values are preserved in `gsur_male_v1_fallback` and
`gsur_female_v1_fallback` (§12).

The partner-specific merge is the central couples complexity: the
same GSURv2 lookup is merged twice, once per partner, using the
partner-specific education group and the partner's sex. The male
partner's GSUR is keyed on `(drgn1, educ3_male, male)`; the female
partner's GSUR is keyed on `(drgn1, educ3_female, female)`. The two
merges are independent and must both succeed for the couples
rebuild to be complete.

---

## 12. v1 fallback preservation rule

The rebuild preserves the v1-fallback GSUR values under fallback
column names before replacing the active GSUR columns with the
GSURv2 rates. The preservation makes the v1-versus-GSURv2
comparison auditable and ensures the v1-fallback rates are not lost.

*Singles preservation.* Before replacing the active `gsur` column,
the rebuild copies the existing (v1-fallback) `gsur` values to a
`gsur_v1_fallback` column. After the merge, the singles parquet
carries both `gsur` (the GSURv2 rate) and `gsur_v1_fallback` (the
preserved v1 rate).

*Couples preservation.* Before replacing the active `gsur_male` and
`gsur_female` columns, the rebuild copies the existing (v1-fallback)
`gsur_male` values to a `gsur_male_v1_fallback` column and the
existing `gsur_female` values to a `gsur_female_v1_fallback` column.
After the merge, the couples parquet carries both `gsur_male` and
`gsur_male_v1_fallback`, and both `gsur_female` and
`gsur_female_v1_fallback`.

The preservation rule is a rebuild requirement. The validation
(§15) confirms that the fallback columns are present and value-
identical to the prior active GSUR values: the `gsur_v1_fallback`
column must equal the input parquet's `gsur` column exactly, the
`gsur_male_v1_fallback` column must equal the input parquet's
`gsur_male` column exactly, and the `gsur_female_v1_fallback`
column must equal the input parquet's `gsur_female` column exactly.
A mismatch indicates the preservation was not performed correctly
and halts the rebuild (§18).

The preservation rule serves two purposes. First, it preserves the
v1-fallback rates for audit and for the v1-versus-GSURv2 comparison
that may inform a future robustness exposure. Second, it ensures
that the rebuild is reversible: the v1-fallback rates are recoverable
from the fallback columns if the GSURv2 rebuild needs to be revisited.

---

## 13. Active GSUR variable naming rule

The active GSUR variable names are unchanged by the rebuild. The
rebuild replaces the rates in the active columns; it does not rename
the active columns.

*Singles.* The active GSUR variable remains `gsur`. The GSURv2 rate
is written to the `gsur` column, replacing the v1-fallback rate
(which is preserved in `gsur_v1_fallback`). The active column name
`gsur` is the name the structural model and the MNL estimation
reference (the K2 decision from the GSURv2 extension: the active
column name remains `gsur`).

*Couples.* The active GSUR variables remain `gsur_male` and
`gsur_female`. The GSURv2 rates are written to the `gsur_male` and
`gsur_female` columns, replacing the v1-fallback rates (which are
preserved in `gsur_male_v1_fallback` and `gsur_female_v1_fallback`).

The active GSUR naming rule is the K2 decision applied at the MNL-
parquet level: the active column names are unchanged so that the
downstream estimation pipeline (the RURO estimator, the
specification YAMLs) references the same column names regardless of
whether the rates are v1-fallback or GSURv2. The GSURv2 provenance
is recorded in the rebuild sidecar (§14), not encoded in the column
name. The required decisions are confirmed: for singles, the active
GSUR variable remains `gsur`; for couples, the active GSUR variables
remain `gsur_male` and `gsur_female`.

---

## 14. Metadata and sidecar requirements

Each GSURv2-based MNL parquet carries a metadata sidecar recording
the rebuild provenance. The sidecar makes the rebuild auditable and
records the GSURv2 source, the opportunity-year mapping, the merge
logic, and the validation outcomes.

The required sidecar fields are:

`gsur_version` — set to `"GSURv2_opportunity_year_aligned"`
(distinguishing the rebuild from the v1-fallback source).

`gsur_opportunity_year` — the opportunity year merged into the
parquet (2014 for FR_2015, 2015 for FR_2016, 2016 for FR_2017).

`gsur_lookup_file` — the path and SHA-256 of the GSURv2 lookup
merged into the parquet.

`gsur_column_name` — the active GSUR column name(s): `"gsur"` for
singles; `"gsur_male"` and `"gsur_female"` for couples.

`gsur_v1_fallback_preserved` — `true`, with the fallback column
name(s): `"gsur_v1_fallback"` for singles;
`"gsur_male_v1_fallback"` and `"gsur_female_v1_fallback"` for
couples.

`dgn_to_sex_mapping` (singles) — the verified `dgn`-to-`sex`
mapping (S1, S3), recorded explicitly (for instance, `{"1": "M",
"0": "F"}`).

`sex_coding` — the GSURv2 lookup's `sex` coding (`"F"`/`"M"`).

`merge_key_singles` — `(drgn1, educ3, sex)` with the `dgn`-to-`sex`
mapping.

`merge_key_couples` — the two partner-specific keys: male
`(drgn1, educ3_male, male)`, female `(drgn1, educ3_female,
female)`.

`crosswalk_file` — the O7-approved crosswalk
(`fr_drgn1_to_nuts2_crosswalk.csv`) and its O7 sign-off reference.

`o7_signoff_reference` — the O7 sign-off document
(`docs/JMP_GSURv2_O7_crosswalk_signoff_v1.md`).

`row_count`, `household_count` — the row and household counts (which
must be unchanged from the input parquet, §15).

`drgn1_9_handling` — the documentation of how drgn1=9 records (if
any) are handled (§15); for the metropolitan France sample, no
record carries drgn1=9, which must be confirmed and recorded.

`build_timestamp`, `script_version` — the rebuild timestamp and the
rebuild script version.

`validation_results` — the per-parquet validation outcomes (§15).

The sidecar is written for each of the six output parquets (three
survey years × singles/couples). The sidecar inspection is part of
the validation (§15): the rebuild confirms each sidecar is present
and carries the required fields with the expected values.

---

## 15. Required validation checks

The rebuild is validated by the following checks, applied per
output parquet. The validation confirms the rebuild merged the
GSURv2 rates correctly and preserved the input data intact.

(V1) **Row counts unchanged.** The output parquet's row count
equals the input parquet's row count. The merge does not add or
drop rows.

(V2) **Household counts unchanged.** The output parquet's household
count equals the input parquet's household count. The merge does
not add or drop households.

(V3) **Non-GSUR columns value-identical.** All columns other than
the active GSUR columns and the added fallback columns are value-
identical between the input and output parquets. The merge changes
only the active GSUR columns (replaced with GSURv2 rates) and adds
the fallback columns (the preserved v1 rates); all other columns —
the demographic columns, the income columns, the hours columns, the
occupation columns, the identifiers — are unchanged.

(V4) **Active GSUR columns complete for drgn1 1–8.** The active
GSUR columns (`gsur` for singles; `gsur_male`, `gsur_female` for
couples) are non-null for every record with drgn1 ∈ {1, …, 8}. The
merge populates a GSURv2 rate for every active record.

(V5) **drgn1=9 handling documented.** The handling of drgn1=9
records is documented. For the metropolitan France sample, no
record carries drgn1=9 (the DOM and extra-regio households are
excluded upstream); the rebuild confirms this and records it in the
sidecar. If any drgn1=9 record were present, its GSUR would be NaN
(the lookup stub), and the handling would be documented.

(V6) **Fallback GSUR columns present and value-identical to prior
active GSUR.** The fallback columns (`gsur_v1_fallback` for singles;
`gsur_male_v1_fallback`, `gsur_female_v1_fallback` for couples) are
present and value-identical to the input parquet's active GSUR
columns. The preservation (§12) is confirmed exact.

(V7) **Survey-year / opportunity-year mapping correct.** The output
parquet's `gsur_opportunity_year` sidecar field matches the
required mapping (2014 for FR_2015, 2015 for FR_2016, 2016 for
FR_2017), and the GSURv2 lookup merged is the lookup for that
opportunity year.

(V8) **Singles `dgn`-to-GSURv2-`sex` mapping verified.** The `dgn`
coding was verified empirically (S1), the GSURv2 `sex` coding was
verified (S2), and the mapping is recorded in the sidecar. The
validation confirms the mapping was verified, not assumed.

(V9) **Couples partner-specific GSUR merge verified.** The male-
partner merge keyed on `(drgn1, educ3_male, male)` and the female-
partner merge keyed on `(drgn1, educ3_female, female)` were
performed correctly, populating the respective active columns. The
validation confirms the partner-specific merges are correct (for
instance, by spot-checking that a couple's `gsur_male` matches the
lookup value for `(drgn1, educ3_male, M)` and `gsur_female` matches
the lookup value for `(drgn1, educ3_female, F)`).

(V10) **GSURv2 merged values match lookup values exactly.** For
sampled and/or full key checks, the merged GSURv2 rates in the
active GSUR columns match the GSURv2 lookup values exactly for the
corresponding `(drgn1, educ3, sex)` keys. The merge is a lookup
join, so the merged value must equal the lookup value for the
matched key; any discrepancy indicates a merge error.

(V11) **Metadata sidecars present.** Each output parquet has a
metadata sidecar (§14) present and carrying the required fields.

(V12) **Canonical files untouched.** The canonical 2016 M1-clean
parquets, the input v1-fallback parquets, and any previous
estimation output are unchanged. The rebuild confirms (for instance,
by SHA-256) that these files were not modified.

All twelve validation checks must pass for the rebuild to be
accepted. A failure of any check halts the rebuild (§18) and is
recorded in the rebuild report (§19).

---

## 16. What is authorized

The rebuild authorises the following, and only the following.

(A1) **Reading the three input v1-fallback MNL parquets** (§6) and
the three GSURv2 lookups (§7), with SHA-256 verification of the
lookups.

(A2) **Verifying the actual MNL schema** (§9) of each input parquet
and the GSURv2 lookup `sex` coding.

(A3) **Verifying the singles `dgn` coding** (S1) and constructing
the `dgn`-to-`sex` mapping (S3).

(A4) **Performing the singles merge** (§10): preserving the v1-
fallback `gsur` as `gsur_v1_fallback`, merging on `(drgn1, educ3,
mapped-sex)`, and replacing the active `gsur` column with the
GSURv2 rate.

(A5) **Performing the couples merge** (§11): preserving the v1-
fallback `gsur_male` and `gsur_female` as the respective fallback
columns, performing the two partner-specific merges, and replacing
the active `gsur_male` and `gsur_female` columns with the GSURv2
rates.

(A6) **Writing the six GSURv2-based MNL output parquets** (§8) to
the year-tagged output stems, with the metadata sidecars (§14).

(A7) **Running the twelve validation checks** (§15) and producing
the rebuild report (§19).

The authorised steps are the GSURv2 MNL-parquet rebuild for the
three survey years. They do not extend to any downstream step.

---

## 17. What is not authorized

The rebuild does not authorise the following. Each is separately
gated.

(N1) **Pooled stacking.** The Stage M1 pooled stacking re-run
against the GSURv2-based MNL parquets is NOT authorised. It is
downstream of the rebuild and requires its own authorization.

(N2) **Pooled estimation.** No pooled estimation, provisional or
final, is authorised. The final pooled estimation remains gated
behind the pooled stacking re-run, the cluster-robust SE wrapper,
and the pooled specification.

(N3) **Welfare computation.** No welfare implementation or
computation is authorised. Welfare work requires its own
authorization and an accepted empirical baseline.

(N4) **Canonical promotion.** No canonical promotion of any GSURv2-
based MNL parquet is authorised. The GSURv2-based parquets are
written to versioned year-tagged stems; canonical promotion
requires explicit approval after a downstream verdict.

(N5) **P3b or P4.** The P3b configuration (blocked by the ISF
comparability gate) and the P4 configuration are NOT authorised.

(N6) **Changes to the M1-clean or M1-naive estimation specs.** The
M1-clean and M1-naive estimation specifications are unchanged by
the rebuild. The rebuild produces data parquets; it does not modify
any estimation specification.

(N7) **Promotion of the pooled route over M1-clean.** The GSURv2-
based MNL parquets are the data foundation for a future pooled
estimation; producing them does not promote the pooled route over
the single-year M1-clean baseline. M1-clean 2016 remains the active
JMP baseline (per the O7 sign-off and the construction verdict),
displaced only by a future SA2 verdict on a final pooled
specification.

The not-authorised steps are everything downstream of the rebuild.
The rebuild produces the GSURv2-based MNL parquets; it does not
stack, estimate, or compute welfare from them.

---

## 18. Halt conditions

The rebuild halts under the following conditions. Each halt
preserves the inputs and any partial outputs and requires diagnosis
before the rebuild proceeds.

(H1) **Required key column missing or ambiguous.** If a required
key column (`drgn1`, `educ3`, `dgn` for singles; `drgn1`,
`educ3_male`, `educ3_female` for couples) is missing from an input
parquet or is ambiguous, the rebuild halts and reports (§9).

(H2) **`dgn` coding unverifiable.** If the singles `dgn` coding
cannot be verified empirically (S1) — for instance, if the coding
is ambiguous or inconsistent with the EUROMOD documentation — the
rebuild halts. The rebuild must not assume the `dgn` coding
silently.

(H3) **GSURv2 `sex` coding unrecognised.** If the GSURv2 lookup's
`sex` coding is not the expected `F`/`M` and the mapping cannot be
constructed unambiguously, the rebuild halts and documents the
coding.

(H4) **GSURv2 lookup SHA-256 mismatch.** If a GSURv2 lookup's SHA-
256 does not match the recorded value (Table 3), the rebuild halts:
the lookup is not the validated construction output or has been
modified.

(H5) **Merge incompleteness.** If the merge leaves any active record
(drgn1 ∈ {1, …, 8}) with a null active GSUR value, the rebuild halts:
the merge did not populate the active GSUR column completely (V4).

(H6) **Fallback preservation failure.** If a fallback column is not
value-identical to the input parquet's prior active GSUR column
(V6), the rebuild halts: the preservation was not performed
correctly.

(H7) **Non-GSUR column modified.** If any non-GSUR column differs
between the input and output parquets (V3), the rebuild halts: the
merge altered a column it should not have.

(H8) **Lookup-value mismatch.** If a merged GSURv2 rate does not
match the lookup value for its key (V10), the rebuild halts: the
merge join is incorrect.

(H9) **Existing output stem found.** If an output stem already
exists before its rebuild (§8), the rebuild halts before
overwriting it. The existing file is archived or documented before
the rebuild proceeds. Silent overwriting is not authorised.

(H10) **Canonical or input file modification detected.** If the
rebuild would modify a canonical 2016 M1-clean parquet, an input
v1-fallback parquet, or a previous estimation output, the rebuild
halts: the no-overwrite constraint (§8, §16) is violated.

The halt conditions are protective: they stop the rebuild at the
first sign of a merge error, a verification failure, or a no-
overwrite violation, preserving the inputs and the canonical files.
The most consequential halts are H2 (`dgn` coding unverifiable) and
H8 (lookup-value mismatch), which indicate that the merge key
mapping or the merge join is incorrect — errors that would
propagate a wrong opportunity-side rate into the GSURv2-based MNL
parquets.

---

## 19. Required rebuild report

The rebuild produces a rebuild report
(`Results/JMP_GSURv2_MNL_rebuild_report_v1.md` or equivalent)
recording the rebuild outcome for each survey year and each
component (singles, couples). The report is the deliverable that
confirms the rebuild outcome and informs the next gating decision.

The report must record:

(R1) **The rebuild sequence and outcomes.** For each survey year
and component, whether the rebuild executed, whether the validation
passed, and the halt point if the rebuild halted.

(R2) **The verified `dgn`-to-`sex` mapping.** The empirically
verified singles `dgn` coding (S1), the GSURv2 `sex` coding (S2),
and the constructed mapping (S3), recorded explicitly.

(R3) **The merge results.** For singles, the merge on `(drgn1,
educ3, mapped-sex)` and the active `gsur` replacement. For couples,
the two partner-specific merges and the active `gsur_male` /
`gsur_female` replacements.

(R4) **The v1-fallback preservation.** Confirmation that the
fallback columns are present and value-identical to the prior
active GSUR values (V6).

(R5) **The twelve validation results** (§15) for each output
parquet: row counts (V1), household counts (V2), non-GSUR column
identity (V3), active GSUR completeness (V4), drgn1=9 handling (V5),
fallback preservation (V6), opportunity-year mapping (V7), `dgn`-to-
`sex` mapping verification (V8), partner-specific merge verification
(V9), lookup-value match (V10), sidecar presence (V11), canonical-
file integrity (V12).

(R6) **The output file inventory.** The six GSURv2-based MNL output
parquets, their SHA-256 hashes, their row and household counts, and
their sidecars.

(R7) **The halt and diagnosis record, if applicable.** If the
rebuild halted, the halt condition, the diagnosis, and the
recommended remediation.

(R8) **The readiness of the next gate.** A statement that the next
gate is a strict post-rebuild verdict; if that verdict passes, it
may authorize pooled stacking re-run as the following step.
Confirmation that the rebuild did not perform any downstream step.

The rebuild report is returned to the project chat for the next
gating decision. If the rebuild passes, the next gate is a strict
post-rebuild verdict; if that verdict passes, it may authorize
pooled stacking re-run as the following step. If the rebuild halts,
the report informs the diagnosis and the re-authorisation.

---

## 20. Exact next Claude Code task

The following prompt initiates the GSURv2 MNL-parquet rebuild task
in Claude Code Sonnet. The prompt executes the authorised rebuild
(§16) under the halt conditions (§18) and produces the rebuild
report (§19). It does not stack the parquets, estimate from them,
or compute welfare from them.

Tool path: Claude Code Sonnet (local codebase, MNL-parquet rebuild).

Interpreter: `.venv\Scripts\python.exe`.

Files to confirm present: the three input v1-fallback MNL parquet
stems (§6); the three GSURv2 lookups (§7) with their recorded SHA-
256 hashes; the O7-approved crosswalk
(`fr_drgn1_to_nuts2_crosswalk.csv`); the O7 sign-off
(`docs/JMP_GSURv2_O7_crosswalk_signoff_v1.md`); and this rebuild
authorization.

Prompt to use:

> Execute the GSURv2 MNL-parquet rebuild per
> `docs/JMP_GSURv2_MNL_rebuild_authorization_v1.md`. Use the
> interpreter `.venv\Scripts\python.exe`. Do NOT stack the parquets.
> Do NOT estimate any model. Do NOT compute welfare. Do NOT promote
> any file to a canonical path. Do NOT modify any canonical 2016
> M1-clean parquet, any input v1-fallback parquet, any previous
> estimation output, or any estimation specification.
>
> For each survey year (FR_2015 → y2014, FR_2016 → y2015, FR_2017 →
> y2016):
>
> 1. Verify the GSURv2 lookup SHA-256 against the recorded value
>    (y2014 `740ef6c7…`, y2015 `f51ad630…`, y2016 `19ac53…`). If
>    mismatch: HALT.
>
> 2. Verify the actual MNL schema: singles carry `drgn1`, `educ3`,
>    `dgn`, `gsur`; couples carry `drgn1`, `educ3_male`,
>    `educ3_female`, `gsur_male`, `gsur_female`. If a required key
>    column is missing or ambiguous: HALT and report.
>
> 3. Verify the singles `dgn` coding EMPIRICALLY — do not assume it.
>    Confirm the `dgn`-to-sex convention and the GSURv2 lookup `sex`
>    coding (`F`/`M`). Construct and document the `dgn`-to-`sex`
>    mapping explicitly. If the coding cannot be verified: HALT.
>
> 4. Singles: copy the existing `gsur` to `gsur_v1_fallback`; merge
>    the GSURv2 lookup on `(drgn1, educ3, mapped-sex)`; write the
>    GSURv2 rate to the active `gsur` column. Confirm every drgn1
>    1–8 record has a non-null `gsur`.
>
> 5. Couples: copy `gsur_male` to `gsur_male_v1_fallback` and
>    `gsur_female` to `gsur_female_v1_fallback`; perform two
>    partner-specific merges — male `(drgn1, educ3_male, sex=male)`
>    → `gsur_male`, female `(drgn1, educ3_female, sex=female)` →
>    `gsur_female`. Confirm every drgn1 1–8 record has non-null
>    `gsur_male` and `gsur_female`.
>
> 6. Write the GSURv2-based output parquets to the year-tagged
>    stems: `fr_2015_RURO_mnl_GSURv2_y2014__`,
>    `fr_2016_RURO_mnl_GSURv2_y2015__`,
>    `fr_2017_RURO_mnl_GSURv2_y2016__` (each with `__singles.parquet`
>    and `__couples.parquet`). If an output stem already exists:
>    archive it or HALT (do not overwrite silently). Write a
>    metadata sidecar for each output parquet per the authorization
>    §14.
>
> 7. Run the twelve validation checks per the authorization §15:
>    row counts unchanged; household counts unchanged; non-GSUR
>    columns value-identical; active GSUR complete for drgn1 1–8;
>    drgn1=9 handling documented; fallback columns present and
>    value-identical to prior active GSUR; opportunity-year mapping
>    correct; `dgn`-to-`sex` mapping verified; partner-specific
>    merge verified; merged GSURv2 values match lookup values
>    exactly; sidecars present; canonical files untouched. If any
>    check FAILS: HALT and report.
>
> Save the rebuild report as
> `Results/JMP_GSURv2_MNL_rebuild_report_v1.md`, recording the
> verified `dgn`-to-`sex` mapping, the merge results, the v1-
> fallback preservation, the twelve validation results per output
> parquet, the output file inventory with SHA-256 hashes, any halt
> and diagnosis, and the readiness of the next gate. Do NOT stack
> the parquets. Do NOT run pooled estimation. Do NOT compute
> welfare.

Output to save: the rebuild report at
`Results/JMP_GSURv2_MNL_rebuild_report_v1.md`, together with the
six GSURv2-based MNL output parquets and their sidecars.

What to do next: return the rebuild report to the project chat for
the next gating decision. If the rebuild passes, the next gate is
a strict post-rebuild verdict; if that verdict passes, it may
authorize pooled stacking re-run as the following step. Pooled
stacking re-run is separately gated and not authorised by this
rebuild. If the rebuild halts — particularly on H2 (`dgn` coding
unverifiable) or H8 (lookup-value mismatch) — the report informs
the diagnosis and the re-authorisation.

---

**Required final statements**

The following statements are made explicitly, as required.

- **GSURv2 MNL-parquet rebuild is authorized only after O7 sign-
  off.** The O7 crosswalk sign-off is granted
  (`docs/JMP_GSURv2_O7_crosswalk_signoff_v1.md`), satisfying the
  prerequisite for the rebuild. This memo authorises the GSURv2
  MNL-parquet rebuild for the three survey years within the bounds
  specified.

- **Pooled stacking is NOT authorized.** The Stage M1 pooled
  stacking re-run against the GSURv2-based MNL parquets is downstream
  of the rebuild and requires its own authorization.

- **Pooled estimation is NOT authorized.** No pooled estimation,
  provisional or final, is authorised by this rebuild.

- **Welfare computation is NOT authorized.** No welfare
  implementation or computation is authorised by this rebuild.

- **M1-clean 2016 remains the active JMP baseline.** The GSURv2
  MNL-parquet rebuild produces opportunity-side data parquets; it
  produces no estimation result and does not displace the M1-clean
  baseline. M1-clean 2016 remains the active JMP baseline until a
  later SA2 verdict explicitly promotes a final pooled
  specification.
