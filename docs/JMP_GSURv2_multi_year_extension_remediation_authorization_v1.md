# JMP GSURv2 Multi-Year Extension — Remediation Authorization v1

Date: 2026-05-20

Specification class: remediation authorization memo. The memo
authorises the preparatory remediation steps that the
implementation audit established as prerequisites for GSURv2
construction. It is an authorization document for the remediation
only; it does not authorise the GSURv2 construction itself, the
MNL-parquet rebuild, pooled estimation, or any welfare work.

Reference documents:
- `docs/JMP_GSURv2_multi_year_extension_implementation_audit_v1.md`
  (the audit returning NOT READY — CODE CHANGES REQUIRED)
- `docs/JMP_GSURv2_multi_year_extension_implementation_audit_addendum_v1.md`
  (the audit addendum specifying the remediation prerequisites)
- `docs/JMP_GSURv2_multi_year_extension_design_memo_v1.md` (the
  governing design memo defining conditions A1–A6 and changes
  C1–C7)
- `docs/JMP_GSUR_year_alignment_decision_v1.md` (the opportunity-
  year alignment rule and the GSURv2 final-build requirement)
- `docs/RURO_GSUR_rebuild_specification_v2_1.md` (the canonical
  GSURv2 construction methodology — referenced for validation
  checks)
- `docs/RURO_GSUR_v2_stageA_implementation_report_v1.md` (the
  existing 2016 GSURv2 build and the pending O7 sign-off)

Scope of memo: the memo authorises the remediation steps —
resolution of the K2 column-naming and C6 output-naming
decisions, retrieval of the six missing external files,
implementation of the seven script parameterisation changes
C1–C7, preparation of the y2016 provenance and sidecar lock, and
preparation of the O7 crosswalk sign-off request — that the audit
established as prerequisites for GSURv2 construction. The memo
does not authorise the construction of the y2014 and y2015 GSURv2
lookups (the GSURv2 extension proper), the MNL-parquet rebuild,
pooled estimation, welfare implementation, or welfare computation;
those steps are separately gated and require their own
authorizations after the remediation is complete.

---

## 1. Purpose

The purpose of this memo is to authorise the remediation steps
that must be completed before GSURv2 construction can be
authorised, as established by the implementation audit and its
addendum. The audit returned a verdict of NOT READY — CODE
CHANGES REQUIRED, identifying three categories of blocking item:
two unresolved naming decisions (K2 column naming, C6 output
naming), six missing external files, and seven unimplemented
script parameterisation changes (C1–C7), together with two
provenance-lock failures on the existing 2016 GSURv2 lookup (K1
sidecar absent, K3 O7 sign-off pending).

The memo resolves the two naming decisions, authorises the
retrieval of the six missing external files, authorises the
implementation of the seven script parameterisation changes,
authorises the preparation of the y2016 provenance and sidecar
lock, and authorises the preparation of the O7 crosswalk sign-off
request. Each authorisation is bounded: the memo authorises the
preparatory step but not the construction it enables.

The memo's operational deliverable is the exact Claude Code task
(§15) that executes the authorised remediation. The remediation
task produces the remediated inputs and code; a separate
construction authorization (deferred to a subsequent memo, per the
audit addendum §24) authorises the GSURv2 construction once the
remediation is complete and validated.

The memo maintains the established gating discipline: the
remediation is a construction-precondition activity, not a
construction activity. The single-year M1-clean 2016 specification
remains the active JMP baseline throughout (§12), unaffected by
the remediation.

---

## 2. Current audit verdict

The implementation audit returned **NOT READY — CODE CHANGES
REQUIRED**. Table 1 reproduces the six audit-condition statuses
from the audit §3 and the addendum §1.

| Condition | Subject | Status |
|---|---|---|
| A1 | `lfst_r_lfu3rt` unemployment-rate source (`FR_gsur.xlsx`) | PASS |
| A2 | `lfst_r_lfsd2pop` / `lfst_r_lfp2acedu` denominators, y2014 and y2015 | FAIL |
| A3 | INSEE BDM 001688526 benchmark, y2014 and y2015 | FAIL |
| A4 | NUTS-2 vintage compatibility | CONDITIONAL |
| A5/K1 | Existing y2016 sidecar JSON (provenance lock) | FAIL |
| A5/K2 | y2016 output column-name consistency | FLAG |
| A5/K3 | O7 crosswalk sign-off resolution | FAIL |
| A6 | Script parameterisation C1–C7 | FAIL (all seven unimplemented) |

The audit established that one condition passes (A1: the
unemployment-rate workbook `FR_gsur.xlsx` already covers years
2007–2019, so no new unemployment-rate retrieval is required), one
is conditional and expected to pass at retrieval (A4: the NUTS-2
vintage of the retrieved files is expected to match the crosswalk
because Eurostat applies retroactive NUTS revision), and the
remaining conditions fail or carry flags requiring remediation.

The primary blocking gate identified by the audit (§24) is the
absence of the `--opportunity-year` parameterisation: the
construction script cannot be run for any year other than 2016
without the C1–C7 changes. The audit established that the year-
invariant construction logic requires no modification (the
parameterisation is fewer than 30 net lines of change across the
seven items) and that the script is a clean candidate for
parameterisation.

The audit explicitly did not authorise construction, file
retrieval, or script modification. It recommended a remediation
authorization memo (audit §24; addendum §23) that resolves the
naming decisions, authorises file retrieval, and authorises the
script parameterisation. This memo is that remediation
authorization.

---

## 3. Why GSURv2 construction is not authorized yet

GSURv2 construction is not authorised by this memo because the
preconditions for construction are not yet met, and because the
remediation that establishes those preconditions has not yet been
executed. The construction is gated behind the remediation, and
the remediation is gated behind this authorization. The memo
authorises the remediation; it does not authorise the construction
that the remediation enables.

Three preconditions for construction remain unmet at the time of
this memo.

First, the external inputs for opportunity years 2014 and 2015 do
not exist locally. The four Eurostat denominator files and the two
INSEE benchmark files are absent (audit §5, §6; addendum §2). The
parameterised script cannot be run for y2014 or y2015 without
these inputs: the D2 and D1 denominator paths (C3, C4) resolve to
non-existent files, and the benchmark value (C5) cannot be read.
Construction for y2014 and y2015 is therefore impossible until the
six files are retrieved.

Second, the construction script is not parameterised. All seven
C1–C7 changes are unimplemented (audit §12; addendum §5). The
script's year is hard-coded at `YEAR = 2016` (line 44), the
denominator paths are hard-coded to the 2016 files (lines 192,
209), the benchmark is hard-coded at `BENCHMARK_PCT = 9.725` (line
45), the output path is hard-coded to the un-tagged 2016 filename
(line 42), and no sidecar is written. The script cannot be run for
any year other than 2016 in its current state, and even for 2016
it writes to the un-tagged path and produces no sidecar.

Third, the two naming decisions (K2 column naming, C6 output
naming) are unresolved. The audit established (R4, R5; addendum
§22) that these decisions must be made before any parquet rebuild,
because the column name propagates to the MNL-merge step and the
deflation-exclusion configuration, and the output naming
determines whether the existing y2016 lookup is overwritten or
preserved. Construction without these decisions resolved would
risk a silent deflation error (R4) or an output-path collision
(R5).

The remediation this memo authorises establishes all three
preconditions: it retrieves the six external files, implements the
seven script changes, and resolves the two naming decisions. Once
the remediation is complete and validated (§14), the construction
becomes authorisable under a separate construction authorization
(§15, deferred). Until then, construction is not authorised, and
this memo does not authorise it.

The deferral is consistent with the established gating discipline.
The audit addendum §24 specifies a construction-authorization
checklist with ten items, the first four of which (the six files
present, C1–C7 implemented and committed, the K2 decision
implemented in script and config, the C6 scheme adopted and
references updated) are the outputs of the remediation this memo
authorises. The construction authorization is issued only after
those four items are confirmed complete.

---

## 4. Required opportunity years

The GSURv2 extension must ultimately cover three opportunity
years, mapped to the three survey years by the alignment rule
(year-alignment decision §2; audit §2). Table 2 reproduces the
mapping and the current GSURv2 status by opportunity year.

| Opportunity year | Required by survey year | GSURv2 status | Remediation relevance |
|---|---|---|---|
| 2014 | FR_2015 | NOT BUILT | external inputs to retrieve; construction deferred |
| 2015 | FR_2016 | NOT BUILT | external inputs to retrieve; construction deferred |
| 2016 | FR_2017 | BUILT (un-tagged, no sidecar) | provenance lock to prepare (K1, K3); year-tag to apply (C6) |

The required opportunity years are 2014, 2015, and 2016. The
remediation prepares all three: it retrieves the external inputs
for opportunity years 2014 and 2015 (the two not yet built), and
it prepares the provenance lock and year-tagging for opportunity
year 2016 (the one already built but lacking a sidecar and a
year-tagged filename).

The remediation does not construct the y2014 and y2015 lookups;
it retrieves and prepares their inputs. The y2016 provenance-lock
preparation (§9) is the one opportunity-year-specific construction-
adjacent activity the remediation authorises, and it is bounded
narrowly: it reproduces an existing validated lookup under the
parameterised script for the purpose of validating the
parameterisation and generating the missing sidecar, not for
constructing a new lookup.

---

## 5. Missing external files

The remediation authorises the retrieval of six missing external
files, identified by the audit §5 and §6 and the addendum §21.
Table 3 specifies the files, their roles, and their sources.

| # | File | Role | Source |
|---|---|---|---|
| 1 | `Data/external/lfst_r_lfsd2pop_FR_2014.tsv` | D2 population denominator, y2014 | Eurostat SDMX-CSV API |
| 2 | `Data/external/lfst_r_lfp2acedu_FR_2014.tsv` | D1 active-population denominator, y2014 | Eurostat SDMX-CSV API |
| 3 | `Data/external/lfst_r_lfsd2pop_FR_2015.tsv` | D2 population denominator, y2015 | Eurostat SDMX-CSV API |
| 4 | `Data/external/lfst_r_lfp2acedu_FR_2015.tsv` | D1 active-population denominator, y2015 | Eurostat SDMX-CSV API |
| 5 | `Data/external/insee_001688526_2014.csv` | National UR benchmark, y2014 | INSEE BDM API |
| 6 | `Data/external/insee_001688526_2015.csv` | National UR benchmark, y2015 | INSEE BDM API |

The four Eurostat denominator files are retrieved from the same
SDMX-CSV endpoint as the existing 2016 files (documented in
`Data/external/gsur_denominator_source.txt`), with the
`startPeriod` and `endPeriod` parameters set to the target year.
The two INSEE benchmark files are retrieved from the INSEE BDM API
(documented in `Data/external/gsur_benchmark_source.txt`); the
annual-average benchmark value for each year is computed as the
mean of the four quarterly values after retrieval.

The retrieval must produce two accompanying provenance updates.
The `gsur_denominator_source.txt` file must be extended with
entries for the y2014 and y2015 denominator files, recording the
API call parameters and the retrieval date. The
`gsur_benchmark_source.txt` file must be extended with entries for
the y2014 and y2015 benchmark files, recording the API call, the
four quarterly values, and the computed annual average. The
computed annual averages become the `BENCHMARK_PCT` values for
y2014 and y2015 in the parameterised script (C5).

The D1 active-population file (`lfst_r_lfp2acedu`) is retrieved
for completeness and diagnostic comparison, but the D2 population
denominator (`lfst_r_lfsd2pop`) remains the operational
denominator per the rebuild specification §5(D2) and the Stage A
implementation report §3 O2: the D1 table does not publish the
Y20-64 age band at NUTS-2 level (audit §5), a structural
limitation of the Eurostat publication that is year-invariant and
applies equally to 2014 and 2015. The D2 file is the operational
input; the D1 file is diagnostic.

The NUTS-2 vintage of the retrieved Eurostat files (condition A4)
is expected to be NUTS2016, matching the crosswalk, because
Eurostat applies the current NUTS revision retroactively to all
time periods (audit §7). The A4 verification is part of the
post-remediation validation (§14): the L-vintage check confirms
the retrieved files use NUTS2016 codes before any construction
proceeds.

The retrieval is authorised. It requires external API access. The
retrieval does not construct any GSURv2 lookup; it acquires the
inputs that a subsequent construction will consume.

---

## 6. K2 column-naming decision

**Decision: the active model/MNL column name remains `gsur`. The
GSURv2 provenance is recorded in the sidecar metadata, not encoded
in the column name. The v1 fallback values are preserved in a
separately named legacy column (`gsur_v1_fallback`) where needed
at MNL-merge time.**

The audit (§10) and the addendum (§22) flagged the K2 column-name
inconsistency: the GSURv2 Stage A lookup parquet stores the rate
in a column named `gsur`, while the multi-year config YAML
(`config/multi_year/fr_p3a_stage_m1.yaml`) lists `gsur_v2` in the
`variables_excluded_from_deflation` list. The mismatch creates a
risk (audit R4) that the GSURv2 `gsur` column would not be matched
by the `gsur_v2` exclusion entry at MNL-merge time and would
escape the deflation-exclusion protection.

The audit offered three resolution options (§10): (a) rename the
Stage A output column from `gsur` to `gsur_v2` in the script;
(b) update the config YAML to list `gsur` instead of `gsur_v2`;
(c) confirm that the prep script renames the column on merge. This
memo adopts option (b): the active column name remains `gsur`, and
the config YAML is updated to list `gsur` in the deflation-
exclusion list.

The decision is justified on three grounds. First, the `gsur`
column name is the name the structural model and the MNL
estimation reference. The RURO estimation specifications (the
M1-clean YAML and its lineage) and the estimator reference the
opportunity-side variable as `gsur`; renaming it to `gsur_v2`
would require propagating the new name through the estimation
specifications, the estimator, the post-estimation diagnostics,
and the precompute logic. Keeping `gsur` confines the GSURv2
change to the data layer (the rates in the column change; the
column name does not), which is the lower-risk choice. Second, the
GSURv2 provenance is more appropriately recorded in the sidecar
metadata than in the column name: the sidecar (C7, §9) records the
GSURv2 version, the opportunity year, the construction inputs, and
the validation outcomes, providing a richer and more auditable
provenance record than a column-name suffix. Third, encoding the
version in the column name would couple the data layer to the
version in a way that complicates future version changes: a GSURv3
would require a further column rename and a further propagation
through the estimation pipeline, whereas the sidecar-provenance
approach records the version without touching the column name.

The decision has two operational consequences for the remediation.
First, the config YAML must be updated to list `gsur` (not
`gsur_v2`) in the `variables_excluded_from_deflation` list, so
that the GSUR proportion is correctly excluded from CPI deflation
(GSUR is a job-acceptance probability, not a monetary value, and
must not be deflated). This config update is authorised as part of
the remediation (§11) and must be made atomically with the script
changes (audit R4 mitigation). Second, the v1 fallback values must
be preserved in a separately named legacy column where needed:
when the MNL-merge step (downstream, not authorised here) replaces
the v1 fallback rates in the `gsur` column with GSURv2 rates, the
prior v1 values are written to a `gsur_v1_fallback` column so that
the v1-versus-GSURv2 comparison remains auditable. This v1-
preservation behaviour is a forward decision recorded now and
implemented at MNL-merge time; it does not affect the GSURv2
lookup parquet (which carries only the GSURv2 `gsur` column) and
is not implemented in the remediation.

The K2 decision is recorded. The active column name is `gsur`; the
GSURv2 provenance is in the sidecar; the v1 fallback is preserved
in `gsur_v1_fallback` at MNL-merge time.

---

## 7. C6 output-naming decision

**Decision: all three opportunity-year GSURv2 lookups use year-
tagged output filenames —
`FR_gsur_ruro_v2_stageA_y2014.parquet`,
`FR_gsur_ruro_v2_stageA_y2015.parquet`, and
`FR_gsur_ruro_v2_stageA_y2016.parquet` — each with a matching
`__sidecar.json` file. The existing un-tagged y2016 lookup is
retired (or renamed) when the year-tagged y2016 lookup is produced.**

The audit (§18) and the addendum (§5, R5) flagged the C6 output-
naming decision: the existing y2016 lookup uses the un-tagged stem
`FR_gsur_ruro_v2_stageA.parquet`, and the parameterised script
must adopt a year-tagged scheme to avoid overwriting the existing
lookup when run for y2014 or y2015. The audit offered two options:
year-tag all three years (rebuilding y2016 under the new name), or
year-tag only the new years (retaining the un-tagged y2016 file).

This memo adopts the uniform year-tagged scheme for all three
years. The decision is justified on three grounds. First, uniform
year-tagging makes the opportunity-year keying explicit in every
lookup filename, which is the clearer and less error-prone
convention for the multi-year construction: a reader inspecting
`Data/external/` sees three parallel year-tagged lookups rather
than one un-tagged file and two year-tagged files. Second, the
uniform scheme avoids the output-path-collision risk (audit R5):
if the un-tagged y2016 file were retained alongside year-tagged
y2014 and y2015 files, references to the un-tagged path in the
canary and validation scripts would silently continue using the
old file, creating a latent inconsistency. Third, the uniform
scheme aligns the y2016 lookup with the sidecar-provenance
discipline: rebuilding y2016 under the parameterised script
produces the year-tagged y2016 file and its sidecar in one step,
resolving K1 (the missing sidecar) by construction.

The decision has two operational consequences for the remediation.
First, the parameterised script's output path (C6) is year-tagged:
`FR_gsur_ruro_v2_stageA_y{YEAR}.parquet`, with the matching sidecar
`FR_gsur_ruro_v2_stageA_y{YEAR}__sidecar.json`. Second, all
references to the un-tagged path `FR_gsur_ruro_v2_stageA.parquet`
in the canary and validation scripts must be updated to the
year-tagged y2016 path, and the existing un-tagged file must be
retired (archived or deleted, not silently left in place) when the
year-tagged y2016 lookup is produced. The reference updates and
the retirement are authorised as part of the remediation (§11).

The C6 decision is recorded. All three lookups use year-tagged
filenames with matching sidecars; the un-tagged y2016 file is
retired when the year-tagged y2016 lookup is produced.

---

## 8. C1–C7 script parameterisation authorization

The remediation authorises the implementation of the seven script
parameterisation changes C1–C7 in
`scripts/enhanced/enh_prepare_FR_gsur_v2.py`, as specified by the
audit §13–§19 and the addendum §5. Table 4 specifies each change.

| Change | Location | Current | Authorised change |
|---|---|---|---|
| C1 | line 44 | `YEAR = 2016` | Add `argparse` `--opportunity-year` (integer, required); set `YEAR` from the argument |
| C2 | line 165 | `_find_year_col(df_raw, YEAR)` | No additional edit; satisfied by C1 (the workbook is multi-year) |
| C3 | line 192, `load_d2()` | `lfst_r_lfsd2pop_FR_2016.tsv` | Replace `2016` literal with `{YEAR}` f-string |
| C4 | line 209, `load_d1()` | `lfst_r_lfp2acedu_FR_2016.tsv` | Replace `2016` literal with `{YEAR}` f-string |
| C5 | line 45 | `BENCHMARK_PCT = 9.725` | Read from `insee_001688526_{YEAR}.csv`; compute mean of quarterly values |
| C6 | line 42 | `FR_gsur_ruro_v2_stageA.parquet` | Year-tagged path `FR_gsur_ruro_v2_stageA_y{YEAR}.parquet` (per §7) |
| C7 | absent | no sidecar block | Add sidecar JSON write at end of `__main__`; fields per the design memo §14 and the K2 decision (§6) |

The authorisation is bounded by three constraints.

First, the changes are confined to the input-selection and output-
tagging layers of the script. The year-invariant construction
logic — the population-weighted aggregation over NUTS-2 components,
the education alignment (educ3 to ISCED ED0-2 / ED3_4 / ED5-8), the
Y20-64 age-band selection, the drgn1=9 stub handling, the IDF
parity check, the benchmark validation, and the eleven-column
output schema — must remain unchanged (audit §12; design memo §9
C6-preservation). The audit established (§12; addendum §4) that the
construction logic contains no year references beyond the seven
C1–C7 items, so the parameterisation does not require touching the
core logic. No change to the construction methodology is authorised
by this remediation.

Second, the C7 sidecar block must record the GSURv2 column name as
`gsur` (the K2 decision, §6) and must record the full provenance
specified in the design memo §14: the opportunity year, the
benchmark value, the input file paths (D2, D1, unemployment-rate
workbook), the GSUR column name, the NUTS vintage, the build
timestamp, the script version, and the validation outcomes (IDF
parity difference, benchmark difference, row count). The sidecar is
the provenance record that resolves K1 (§9) and that records the
K2 decision (§6).

Third, the C5 benchmark change must read the year-specific INSEE
benchmark from the retrieved CSV (§5) and compute the annual
average; it must not hard-code the benchmark value for any year.
This honours the rebuild specification cleanup edit 2 (the
validation report cites the benchmark rather than hard-coding a
national rate; rebuild specification §13).

The C1–C7 implementation is authorised as a code-change task. The
audit established the total edit scope as fewer than 30 net lines
across all seven changes (audit §24; addendum §5). The
implementation must be committed to the repository as a single
remediation commit, atomically with the config YAML update (the K2
decision, §6), per the audit R4 mitigation.

The authorisation to implement C1–C7 does not authorise running
the parameterised script to construct the y2014 and y2015 lookups.
The implementation produces a parameterised script; the
construction that the parameterised script enables is separately
gated (§12). The one bounded exception is the y2016 reproduction
authorised in §9, which validates the parameterisation and
generates the y2016 provenance lock without constructing a new
lookup.

---

## 9. y2016 provenance and sidecar lock

The remediation authorises the preparation of the y2016 provenance
and sidecar lock, which resolves the K1 failure (the absent y2016
sidecar) and produces the year-tagged y2016 lookup (the C6
decision, §7). The preparation is bounded narrowly: it reproduces
the existing validated y2016 lookup under the parameterised script
for the purpose of validating the parameterisation and generating
the missing sidecar, not for constructing a new lookup.

The audit (§9) established that the y2016 sidecar JSON
(`FR_gsur_ruro_v2_stageA__sidecar.json`) is absent and that the
existing construction script does not write one. The audit offered
two resolution paths (§9): write the sidecar post-hoc for the
existing lookup, or rebuild y2016 under the parameterised script
(which writes the sidecar via C7). This memo adopts the rebuild-
reproduction path, for two reasons. First, the rebuild
reproduction simultaneously validates the parameterisation (by
confirming the parameterised script reproduces the existing y2016
lookup value-identically) and generates the missing sidecar (via
C7), accomplishing both the K1 resolution and the parameterisation
regression check in one step. Second, the rebuild reproduction
produces the year-tagged y2016 lookup
(`FR_gsur_ruro_v2_stageA_y2016.parquet`) required by the C6
decision (§7), aligning the y2016 lookup with the year-tagged
naming of the y2014 and y2015 lookups.

The y2016 reproduction is bounded by three constraints that
distinguish it from construction.

First, it reproduces an existing validated lookup. The y2016
inputs all exist locally (the unemployment-rate workbook, the 2016
D2 and D1 denominators, the 2016 INSEE benchmark). Running the
parameterised script with `--opportunity-year 2016` reproduces the
y2016 lookup from the same inputs that produced the existing
lookup. The reproduction is not a new construction; it regenerates
an existing validated data product under the parameterised script.

Second, it is subject to a value-identity regression check
(§14). The reproduced y2016 lookup must be compared value-
identically (under schema-aligned column-wise comparison, per the
rebuild specification cleanup edit 7) against the existing y2016
lookup (`FR_gsur_ruro_v2_stageA.parquet`). If the reproduced
lookup matches the existing lookup value-identically, the
parameterisation is validated (the C1–C7 changes preserve the
construction logic) and the reproduction is accepted. If the
reproduced lookup differs from the existing lookup, the
parameterisation has altered the construction logic — a remediation
failure that must be diagnosed before any further work. The value-
identity check is the load-bearing validation of the
parameterisation.

Third, it generates the y2016 provenance lock. The C7 sidecar
block writes the y2016 sidecar
(`FR_gsur_ruro_v2_stageA_y2016__sidecar.json`), resolving K1. The
sidecar records the y2016 provenance (the inputs, the GSUR column
name `gsur` per the K2 decision, the NUTS vintage, the IDF parity
difference, the benchmark difference, the row count). The existing
un-tagged y2016 lookup is retired when the year-tagged y2016
lookup and its sidecar are accepted (the C6 decision, §7).

The K3 provenance-lock requirement (the O7 crosswalk sign-off)
is not resolved by the y2016 reproduction. K3 requires an MNL-
merge check (§10) that is downstream of the lookup construction
and is not authorised here. The y2016 reproduction resolves K1
(the sidecar) and applies C6 (the year-tag); K3 is prepared (§10)
but not resolved in the remediation.

The y2016 provenance-lock preparation is authorised as a bounded
reproduction-and-sidecar step. It is the one construction-adjacent
activity the remediation authorises, and it is bounded to the
reproduction of an existing validated lookup under value-identity
control. It does not authorise the construction of the y2014 and
y2015 lookups.

---

## 10. O7 crosswalk sign-off preparation

The remediation authorises the preparation of the O7 crosswalk
sign-off request, which addresses the K3 provenance-lock failure.
The preparation is bounded: it assembles the sign-off request
documentation for the user's decision, but it does not resolve the
sign-off (a user decision) and does not run the MNL-merge check
that validates it (a downstream step, not authorised here).

The audit (§11) established that the O7 crosswalk sign-off is
pending: the Stage A implementation report records O7 as PENDING,
with the MNL-merge check deferred at the time of the Stage A build
because the MNL parquets had not been finalised. The O7 sign-off
requires the user to approve the crosswalk
(`fr_drgn1_to_nuts2_crosswalk.csv`) and the merge key
(`(drgn1, educ3, sex)`), and the sign-off is validated by an MNL-
merge check confirming that the GSUR values are non-null and
plausible across all drgn1 values when the lookup is merged with
the MNL data.

The remediation prepares the O7 sign-off request by assembling the
documentation the user needs to make the sign-off decision: the
crosswalk file (`fr_drgn1_to_nuts2_crosswalk.csv`, 22 rows, all
carrying `verified_against_eurostat = YES`), the merge key
(`(drgn1, educ3, sex)`, confirmed in the Stage A implementation
report §8), the drgn1 compositions (the NUTS-2 components of each
drgn1 group, per the rebuild specification §3 and the Stage A
implementation report §3 O1), and the merge procedure (the per-
individual join for singles, the per-partner double join for
couples, per the Stage A implementation report §8). The assembled
documentation is presented as an O7 sign-off request for the
user's explicit approval.

The preparation is bounded by two constraints.

First, the O7 sign-off itself is a user decision, not a remediation
output. The remediation assembles the request; the user makes the
sign-off. The remediation does not pre-empt or substitute for the
user's sign-off decision.

Second, the O7 merge-check validation is downstream and is not
authorised here. The O7 check confirms the crosswalk produces
correct drgn1-level GSUR assignments when the lookup is merged with
the MNL data; this merge is the MNL-parquet rebuild, which is
explicitly not authorised by this remediation (§12). The K3
resolution — running the O7 merge check against each new lookup —
is part of the construction-and-merge workflow, sequenced after the
construction authorization (audit addendum §24 item 8). The
remediation prepares the O7 sign-off request; it does not run the
O7 merge check.

The O7 crosswalk sign-off preparation is authorised as a
documentation-assembly step. It produces the sign-off request for
the user's decision; it does not resolve the sign-off and does not
run the merge check.

---

## 11. What is authorized

The remediation authorises the following steps. Each is a
construction-precondition activity bounded as specified in the
preceding sections.

(A1) **K2 column-naming decision implemented.** The active model/
MNL column name remains `gsur` (§6). The config YAML
(`config/multi_year/fr_p3a_stage_m1.yaml`) is updated to list
`gsur` (not `gsur_v2`) in the `variables_excluded_from_deflation`
list, atomically with the script changes. The v1-fallback-
preservation behaviour (`gsur_v1_fallback` at MNL-merge time) is
recorded as a forward decision.

(A2) **C6 output-naming decision implemented.** All three
opportunity-year lookups use year-tagged filenames
(`_y2014`, `_y2015`, `_y2016`) with matching `__sidecar.json`
files (§7). References to the un-tagged y2016 path in the canary
and validation scripts are updated; the un-tagged y2016 file is
retired when the year-tagged y2016 lookup is produced.

(A3) **Retrieval of the six missing external files.** The four
Eurostat denominator files and the two INSEE benchmark files (§5)
are retrieved from the Eurostat SDMX-CSV API and the INSEE BDM
API, with provenance entries added to `gsur_denominator_source.txt`
and `gsur_benchmark_source.txt`. The y2014 and y2015 annual-average
benchmark values are computed and recorded.

(A4) **Implementation of C1–C7 in the construction script.** The
seven parameterisation changes (§8) are implemented in
`scripts/enhanced/enh_prepare_FR_gsur_v2.py`, confined to the
input-selection and output-tagging layers, with the year-invariant
construction logic preserved unchanged. The implementation is
committed atomically with the config YAML update (A1).

(A5) **Preparation of the y2016 provenance and sidecar lock.** The
parameterised script is run with `--opportunity-year 2016` to
reproduce the existing y2016 lookup, subject to the value-identity
regression check (§9, §14), generating the year-tagged y2016
lookup and its sidecar (resolving K1). This is a bounded
reproduction of an existing validated lookup, not a new
construction.

(A6) **Preparation of the O7 crosswalk sign-off request.** The
O7 sign-off documentation (the crosswalk, the merge key, the
drgn1 compositions, the merge procedure) is assembled and
presented as a sign-off request for the user's decision (§10).
The O7 sign-off itself and the O7 merge check are not part of this
authorisation.

(A7) **Post-remediation validation.** The validation checks
specified in §14 are run to confirm the remediation is complete
and correct.

The authorised steps are the remediation. They establish the
preconditions for GSURv2 construction without performing the
construction.

---

## 12. What is not authorized

The remediation does not authorise the following. Each is
separately gated and requires its own authorization after the
remediation is complete.

(N1) **GSURv2 construction of the y2014 and y2015 lookups.** The
construction of the new opportunity-year lookups — running the
parameterised script with `--opportunity-year 2014` and
`--opportunity-year 2015` to build the y2014 and y2015 GSURv2
lookups — is not authorised. It requires the separate construction
authorization specified in the audit addendum §24, issued after the
remediation is complete and validated. The y2016 reproduction (A5)
is the one bounded exception, and it reproduces an existing
validated lookup rather than constructing a new one.

(N2) **MNL-parquet rebuilding.** The merge of the GSURv2 lookups
into the FR_2015, FR_2016, and FR_2017 MNL parquets — the step that
replaces the v1 fallback rates with GSURv2 rates in the MNL data —
is not authorised. It is downstream of the lookup construction and
requires its own authorization. The v1-fallback-preservation
behaviour (`gsur_v1_fallback`) is implemented at this step, not in
the remediation.

(N3) **The O7 merge check.** The MNL-merge check that validates the
O7 crosswalk sign-off (resolving K3) is not authorised. The
remediation prepares the O7 sign-off request (A6); the merge check
runs at MNL-merge time, downstream of the construction.

(N4) **Pooled estimation, provisional or final.** No pooled
estimation is authorised. The final pooled estimation remains
gated behind the complete GSURv2 coverage (year-alignment decision
§6) and the cluster-robust SE wrapper and pooled specification (P3a
construction verdict §17). The provisional v1-fallback dry-run
remains a separately authorised activity (year-alignment decision
§5), not authorised here.

(N5) **Welfare implementation and welfare computation.** No welfare
work is authorised. The welfare design memos are complete (P3a
construction verdict §19), but welfare implementation and
computation require their own authorizations and an accepted
empirical baseline, neither of which is provided here.

(N6) **Canonical MNL promotion.** No canonical promotion of any
GSURv2-based data product is authorised. The versioned-path-first
discipline (rebuild specification cleanup edit 4) holds: GSURv2
outputs are written to versioned paths, and canonical promotion
requires explicit approval after a Stage A verdict.

(N7) **Displacement of the M1-clean baseline.** The single-year
M1-clean 2016 specification remains the active JMP baseline (§13
of the P3a construction verdict; audit §21). The remediation does
not displace it. M1-clean remains active until a future SA2
verdict on a final (GSURv2-based) pooled specification determines
otherwise.

The not-authorised steps are the construction and everything
downstream of it. The remediation prepares the construction; it
does not perform it or anything beyond it.

---

## 13. Required remediation outputs

The remediation must produce the following outputs. Each is a
verifiable artefact confirming a remediation step is complete.

(O1) **The six retrieved external files**, present in
`Data/external/`: `lfst_r_lfsd2pop_FR_2014.tsv`,
`lfst_r_lfp2acedu_FR_2014.tsv`, `lfst_r_lfsd2pop_FR_2015.tsv`,
`lfst_r_lfp2acedu_FR_2015.tsv`, `insee_001688526_2014.csv`,
`insee_001688526_2015.csv`.

(O2) **The updated provenance text files**:
`gsur_denominator_source.txt` extended with the y2014 and y2015
denominator entries; `gsur_benchmark_source.txt` extended with the
y2014 and y2015 benchmark entries (including the four quarterly
values and the computed annual average for each year).

(O3) **The parameterised construction script**:
`scripts/enhanced/enh_prepare_FR_gsur_v2.py` with C1–C7
implemented and committed, the year-invariant logic preserved
unchanged.

(O4) **The updated config YAML**:
`config/multi_year/fr_p3a_stage_m1.yaml` with `gsur` (not
`gsur_v2`) in the `variables_excluded_from_deflation` list,
committed atomically with the script changes.

(O5) **The year-tagged y2016 lookup and its sidecar**:
`FR_gsur_ruro_v2_stageA_y2016.parquet` and
`FR_gsur_ruro_v2_stageA_y2016__sidecar.json`, produced by the
y2016 reproduction (A5), with the existing un-tagged y2016 file
retired.

(O6) **The O7 crosswalk sign-off request document**, assembling
the crosswalk, the merge key, the drgn1 compositions, and the
merge procedure for the user's sign-off decision.

(O7) **A remediation completion report**
(`Results/JMP_GSURv2_multi_year_extension_remediation_report_v1.md`
or equivalent) recording the status of each remediation step, the
post-remediation validation results (§14), and the readiness of
the construction preconditions.

The remediation completion report (O7) is the deliverable that
the subsequent construction authorization references to confirm
the construction preconditions are met (audit addendum §24 items
1–4).

---

## 14. Validation required after remediation

The remediation must be validated by the following checks before
the construction authorization is issued. The validations confirm
the remediation is complete and correct without constructing the
y2014 and y2015 lookups.

(V1) **File-presence and parse check.** Confirm the six retrieved
external files (O1) are present in `Data/external/` and parse
without error. Confirm the file structures match the 2016
reference files (the D2 and D1 TSV column structures, the INSEE
CSV quarterly-value structure).

(V2) **NUTS-vintage check (A4 / L-vintage).** Confirm the
retrieved y2014 and y2015 D2 denominator files use the NUTS2016
vintage compatible with the crosswalk (the codes FR10, FRB0, etc.).
If either file uses a different vintage, the L-vintage check fails
and the `NUTS2013-NUTS2016.xlsx` fallback conversion is required
before construction. The A4 condition, conditional in the audit, is
resolved by this check.

(V3) **Benchmark documentation check.** Confirm the y2014 and y2015
annual-average benchmark values are computed from the retrieved
INSEE CSVs and recorded in `gsur_benchmark_source.txt` (O2). The
values become the C5 benchmark inputs for the eventual y2014 and
y2015 construction.

(V4) **Parameterisation regression check (y2016 value-identity).**
Run the parameterised script with `--opportunity-year 2016` and
confirm the reproduced y2016 lookup matches the existing y2016
lookup (`FR_gsur_ruro_v2_stageA.parquet`) value-identically under
schema-aligned column-wise comparison. A value-identical match
confirms the C1–C7 parameterisation preserves the construction
logic. A mismatch indicates the parameterisation altered the logic
and must be diagnosed before any further work. This is the load-
bearing validation of the parameterisation.

(V5) **y2016 sidecar parse check (K1).** Confirm the y2016 sidecar
(`FR_gsur_ruro_v2_stageA_y2016__sidecar.json`) is written, parses
without error, and records the GSUR column name as `gsur` (the K2
decision), the opportunity year 2016, the inputs, the NUTS vintage,
the IDF parity difference, the benchmark difference, and the row
count. The K1 provenance-lock requirement is resolved by this
check.

(V6) **Config-consistency check (K2).** Confirm the config YAML
(O4) lists `gsur` in the `variables_excluded_from_deflation` list
and that this matches the active GSUR column name. The K2 mismatch
flagged in the audit is resolved by this check.

(V7) **Script-logic-preservation check.** Confirm that the C1–C7
changes are confined to the input-selection and output-tagging
layers and that the year-invariant construction logic (the
aggregation, education alignment, age-band selection, drgn1=9 stub
handling, IDF parity check, benchmark validation, output schema) is
unchanged. The V4 value-identity check provides the empirical
confirmation; this check provides the code-inspection confirmation.

The seven validations confirm the remediation outputs are complete
and correct. If all seven pass, the construction preconditions are
met and the construction authorization may be issued. If any
validation fails — particularly V2 (NUTS vintage), V4
(parameterisation regression), or V5 (sidecar) — the failing
remediation step must be diagnosed and corrected before the
construction authorization is issued.

The validations do not construct the y2014 and y2015 lookups. V4
reproduces the existing y2016 lookup under value-identity control;
it does not build a new lookup. The y2014 and y2015 construction is
deferred to the separate construction authorization.

---

## 15. Exact next Claude Code task

The following prompt initiates the remediation task in Claude Code
Sonnet. The prompt executes the authorised remediation steps
(A1–A7) and produces the remediation outputs (O1–O7) under the
validation checks (V1–V7). It does not construct the y2014 and
y2015 lookups, does not rebuild any MNL parquet, does not estimate
any model, and does not compute welfare.

Tool path: Claude Code Sonnet (local codebase, external-data
retrieval, code changes).

Files to place in the workspace or confirm present: the
construction script
(`scripts/enhanced/enh_prepare_FR_gsur_v2.py`); the config YAML
(`config/multi_year/fr_p3a_stage_m1.yaml`); the existing y2016
lookup (`Data/external/FR_gsur_ruro_v2_stageA.parquet`); the
provenance text files (`Data/external/gsur_denominator_source.txt`,
`Data/external/gsur_benchmark_source.txt`); the crosswalk
(`Data/external/fr_drgn1_to_nuts2_crosswalk.csv`); the NUTS
reference (`Data/external/NUTS2013-NUTS2016.xlsx`); the audit and
addendum; and this remediation authorization.

Prompt to use:

> Execute the GSURv2 multi-year extension remediation per
> `docs/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md`.
> Do NOT construct the y2014 or y2015 GSURv2 lookups. Do NOT
> rebuild any MNL parquet. Do NOT estimate any model. Do NOT
> compute welfare. Do NOT promote any file to a canonical path.
>
> Execute the following remediation steps:
>
> 1. Retrieve the six missing external files into `Data/external/`:
>    `lfst_r_lfsd2pop_FR_2014.tsv`, `lfst_r_lfp2acedu_FR_2014.tsv`,
>    `lfst_r_lfsd2pop_FR_2015.tsv`, `lfst_r_lfp2acedu_FR_2015.tsv`
>    (Eurostat SDMX-CSV API, same endpoint as the 2016 files with
>    startPeriod/endPeriod set to the target year), and
>    `insee_001688526_2014.csv`, `insee_001688526_2015.csv` (INSEE
>    BDM API). Add provenance entries to
>    `gsur_denominator_source.txt` and `gsur_benchmark_source.txt`,
>    recording the API calls and, for the benchmark files, the four
>    quarterly values and the computed annual average per year.
>
> 2. Confirm the retrieved y2014 and y2015 D2 denominator files use
>    the NUTS2016 vintage compatible with
>    `fr_drgn1_to_nuts2_crosswalk.csv` (L-vintage check). Flag any
>    mismatch; do not proceed past this check if a mismatch is
>    found.
>
> 3. Implement C1–C7 in
>    `scripts/enhanced/enh_prepare_FR_gsur_v2.py` per the
>    authorization §8: C1 add `--opportunity-year` argument
>    (integer, required) and set `YEAR` from it; C2 no additional
>    edit; C3 year-parameterise the D2 path; C4 year-parameterise
>    the D1 path; C5 read the year-specific INSEE benchmark and
>    compute the annual average; C6 year-tag the output path
>    (`FR_gsur_ruro_v2_stageA_y{YEAR}.parquet`); C7 write a sidecar
>    JSON recording the GSUR column name `gsur`, the opportunity
>    year, the inputs, the NUTS vintage, the IDF parity difference,
>    the benchmark difference, and the row count. Keep the year-
>    invariant construction logic unchanged.
>
> 4. Update `config/multi_year/fr_p3a_stage_m1.yaml` to list `gsur`
>    (not `gsur_v2`) in `variables_excluded_from_deflation`. Commit
>    this atomically with the script changes.
>
> 5. Run the parameterised script with `--opportunity-year 2016` to
>    reproduce the y2016 lookup. Compare the reproduced
>    `FR_gsur_ruro_v2_stageA_y2016.parquet` value-identically
>    (schema-aligned column-wise) against the existing
>    `FR_gsur_ruro_v2_stageA.parquet`. If value-identical, accept
>    the year-tagged y2016 lookup and its sidecar, and retire the
>    existing un-tagged y2016 file (archive, do not silently
>    delete). If not value-identical, stop and report the
>    discrepancy; do not proceed.
>
> 6. Update all references to the un-tagged path
>    `FR_gsur_ruro_v2_stageA.parquet` in the canary and validation
>    scripts to the year-tagged y2016 path.
>
> 7. Assemble the O7 crosswalk sign-off request: the crosswalk
>    (`fr_drgn1_to_nuts2_crosswalk.csv`), the merge key
>    `(drgn1, educ3, sex)`, the drgn1 compositions, and the merge
>    procedure. Present it as a sign-off request for the user's
>    decision. Do NOT run the O7 MNL-merge check.
>
> 8. Run the post-remediation validation checks V1–V7 per the
>    authorization §14.
>
> Save the remediation completion report as
> `Results/JMP_GSURv2_multi_year_extension_remediation_report_v1.md`,
> recording the status of each step, the validation results, and
> the readiness of the construction preconditions. Do NOT construct
> the y2014 or y2015 lookups; the construction is authorised
> separately after this remediation is complete and validated.

Output to save: the remediation completion report at
`Results/JMP_GSURv2_multi_year_extension_remediation_report_v1.md`,
together with the remediation outputs O1–O6.

What to do next: return the remediation completion report to this
chat for a construction-authorization decision. If all seven
validations pass, the next step is the GSURv2 construction
authorization memo (per the audit addendum §24), which authorises
running the parameterised script with `--opportunity-year 2014`
and `--opportunity-year 2015` to construct the new lookups. If any
validation fails — particularly V2 (NUTS vintage), V4
(parameterisation regression), or V5 (sidecar) — the remediation
report identifies the failing step, and the construction
authorization is deferred until the failing step is corrected.

The remediation task is the immediate next operational step. It
does not authorise GSURv2 construction, MNL-parquet rebuilding,
pooled estimation, welfare implementation, or welfare computation;
it establishes and validates the preconditions so that the
subsequent construction authorization can proceed against confirmed
inputs, a parameterised script, resolved naming decisions, and a
locked y2016 provenance.

The single-year M1-clean 2016 specification remains the active JMP
baseline throughout the remediation and until a future SA2 verdict
on a final pooled specification determines otherwise.
