# RURO GSUR v2.1 — Open Decisions Resolution Memo v1

Date: 2026-05-17

Reference specification: `docs/RURO_GSUR_rebuild_specification_v2_1.md`

---

## Purpose

This memo records the resolution status of all ten open decisions (O1–O10)
listed in §17 of `RURO_GSUR_rebuild_specification_v2_1.md`. It is the
authoritative record of which decisions are resolved and which remain
blocked, and must be updated before any GSUR rebuild implementation work
begins.

Decisions resolved here are binding for the implementation. Unresolved
decisions are hard blockers; no code that depends on their outcome may be
merged or promoted to canonical paths until the block is lifted.

---

## Canonical memo

| Item | Status |
|------|--------|
| Reference spec | `docs/RURO_GSUR_rebuild_specification_v2_1.md` |
| Spec version | v2.1 (supersedes v2 in full) |
| This memo | `docs/RURO_GSUR_v2_1_open_decisions_resolution_v1.md` v1 |
| Resolved decisions | O3, O4, O5, O7, O8, O10 |
| Unresolved decisions | O1, O2, O9 |
| Overall readiness for implementation | BLOCKED — see §4 |

---

## Locally resolved decisions

### O3 — Age-65 handling

**Decision: A65-3 (map to broad-age fallback with an explicit flag).**

Individuals aged 65 and over are assigned the Y15-64 broad-age GSUR
(`gsur`) as fallback. The output column `gsur_age_band_used` must carry
the value `"Y15-64_fallback_age65"` for these rows, distinguishing them
from the standard `"Y55-64"` assignment.

**File evidence (confirmed 2026-05-17):**
- Singles: 400 rows with `dag >= 65` out of 335,200 (0.12%).
- Couples: 0 rows with `dag_male >= 65` or `dag_female >= 65` out of
  515,400.
- Sample impact is negligible. The A65-3 fallback introduces no
  identifiable bias risk.

**Why not A65-1 (exclude) or A65-2 (map to Y55-64):**
A65-1 would silently drop 400 singles who are otherwise valid
respondents in the estimation sample. A65-2 would misrepresent the
age-specific unemployment rate since the Y55-64 band excludes those aged
65 and over by Eurostat definition. A65-3 provides honest broad-age
coverage and is self-documenting via the flag column.

---

### O4 — Education alignment (deh → educ3 mapping)

**Decision: deh 0/1/2 → educ3 = 0 (low), deh 3/4 → educ3 = 1 (medium),
deh 5 → educ3 = 2 (high).**

This is the mapping already applied in the upstream MNL parquets. The
GSUR age-education cell lookup must use this three-way education code when
joining GSUR source data to individual respondents.

**File evidence (confirmed 2026-05-17):**

| deh | educ3 | n (singles) |
|-----|-------|-------------|
| 0.0 | 0 | 9,600 |
| 1.0 | 0 | 8,800 |
| 2.0 | 0 | 32,800 |
| 3.0 | 1 | 147,200 |
| 4.0 | 1 | 1,000 |
| 5.0 | 2 | 135,800 |

The crosstab is perfectly monotone — each deh value maps to exactly one
educ3 value with no overlap. The proposed mapping is already encoded in
the data; no transformation ambiguity exists.

Couples use gender-specific variants: `deh_male` → `educ3_male` and
`deh_female` → `educ3_female`, following the same three-way mapping.

---

### O5 — DOM / drgn1 = 9 handling

**Decision: retain drgn1 = 9 in the output schema but leave it empty
(NaN) for the France 2016 metropolitan sample.**

The output schema must include `drgn1 = 9` as a valid category so that
the pipeline remains portable to DOM-inclusive datasets. For France 2016
(metropolitan sample), no respondents carry `drgn1 = 9`; those rows would
receive NaN for all GSUR columns derived from a region lookup. If DOM
respondents ever appear upstream (e.g., from a DOM-inclusive future data
pull), the rebuild pipeline will propagate their regional code correctly
without modification.

No special-casing, exclusion, or warning is required for `drgn1 = 9` in
the current run.

---

### O7 — Crosswalk sign-off

**Decision: mandatory manual sign-off before merge.**

The `drgn1`-to-NUTS2 crosswalk (§4 of the spec) and the GSUR
age-education join key must be reviewed and approved by the user before
any output parquet is written to either versioned (`_GSURv2`) or canonical
paths. The sign-off must be recorded as an explicit user approval message
referencing the crosswalk file and the merge key used.

This requirement applies once, at the end of Stage A verification, before
Stage A promotion.

---

### O8 — Île-de-France parity tolerance

**Decision: absolute tolerance 0.001.**

The Stage A validation check comparing the rebuilt GSUR (broad-age, no
education stratification) against the legacy GSUR for Île-de-France
respondents uses an absolute tolerance of 0.001. Any row-level discrepancy
exceeding this threshold for Île-de-France must be investigated before
Stage A can be signed off.

This tolerance applies to the numerical comparison of `gsur` (broad-age)
values only. It does not apply to `gsur_age` (age-specific) values, which
are new and have no legacy counterpart.

---

### O10 — Promotion rule

**Decision: versioned-path-first; canonical promotion only after Stage A
verdict and explicit user approval.**

The v2 MNL parquets enriched with GSUR columns are written exclusively to
versioned paths:
- `fr_2016_RURO_mnl_GSURv2__singles.parquet`
- `fr_2016_RURO_mnl_GSURv2__couples.parquet`

The canonical paths (`fr_2016_RURO_mnl__singles.parquet`,
`fr_2016_RURO_mnl__couples.parquet`) are not touched until:
1. Stage A verification passes all checks in §14 of the spec.
2. The user explicitly approves promotion in a recorded approval message.

Scripts and specifications must reference the versioned paths during
Stage A. Any script that writes to or reads from canonical paths during
Stage A is in violation of this rule.

---

## Decisions requiring external acquisition

The following three decisions cannot be resolved from files currently in
the repository. They are hard blockers for implementation. No GSUR rebuild
code may be executed until each is resolved.

### O1 — Crosswalk source requirement

**Status: UNRESOLVED.**

The spec requires a documented NUTS2-to-drgn1 crosswalk that is traceable
to an official Eurostat or INSEE source. The audit identified that the
current `FR_gsur.xlsx` source workbook uses a region coding that does not
unambiguously map to `drgn1` categories 1–8 as derived from `drgn2`.

**Blocking question:** Which authoritative crosswalk document maps the
GSUR workbook's regional dimension to the `drgn1` codes used in the
EUROMOD France 2016 data?

**To resolve:** Acquire and commit the crosswalk document (or a
reproducible extract of it) to `Data/external/` and record the source URL
and date of access.

---

### O2 — Denominator data requirement

**Status: UNRESOLVED.**

The spec requires a denominator (labour force count by region × age ×
sex) sourced from Eurostat Labour Force Survey microdata or published LFS
aggregates. The current GSUR workbook provides unemployment counts but the
denominator source is not documented in the audit.

**Blocking question:** Which Eurostat LFS table or microdata file provides
the labour-force denominator used to compute unemployment rates by region,
age band, and sex for France 2016?

**To resolve:** Identify the specific Eurostat dataset (table code and
reference period), download or confirm access, and record the citation in
`Data/external/gsur_denominator_source.txt`.

---

### O9 — National benchmark requirement

**Status: UNRESOLVED.**

§14 of the spec requires a national-level unemployment rate benchmark
for France 2016 (aggregate, age-specific, and sex-specific) against which
the rebuilt GSUR regional rates can be validated. The benchmark source
must be cited in the validation report; it cannot be hard-coded.

**Blocking question:** Which published Eurostat or OECD table provides the
national unemployment rate for France 2016 by age band and sex, at the
level of granularity required by the validation checks in §14?

**To resolve:** Identify the specific table (dataset code, filter
parameters, and reference period), confirm the values, and record the
citation.

---

## Files to acquire

The following files must be obtained before implementation can proceed:

| File | Purpose | Decision |
|------|---------|---------|
| NUTS2-to-drgn1 crosswalk (official source) | Regional join key for GSUR merge | O1 |
| LFS denominator table for France 2016 by region × age × sex | Unemployment rate computation | O2 |
| National unemployment rate benchmark for France 2016 by age × sex | Stage A validation reference | O9 |

Target location for all acquired files: `Data/external/`.

---

## Sources to cite

Once the external files are acquired, each must be cited with:
- Dataset or document name
- Publisher (Eurostat, INSEE, OECD, or other)
- Reference period (France 2016 or closest available)
- Date of access
- URL or DOI if publicly available

The citations must appear in:
1. The validation report produced at Stage A (`Results/RURO_GSUR_v2_stage_A_validation_report_v1.md`).
2. The crosswalk documentation file (`Data/external/gsur_crosswalk_source.txt`).
3. The denominator source file (`Data/external/gsur_denominator_source.txt`).

---

## Blocking status

| Decision | Status | Blocking? |
|----------|--------|-----------|
| O1 | UNRESOLVED — crosswalk source not acquired | YES |
| O2 | UNRESOLVED — denominator source not acquired | YES |
| O3 | RESOLVED — A65-3 broad-age fallback with flag | no |
| O4 | RESOLVED — deh 0/1/2→0, 3/4→1, 5→2 | no |
| O5 | RESOLVED — drgn1=9 in schema, NaN for FR 2016 metropolitan | no |
| O6 | DEFERRED — Stage B necessity; deferred to post-Stage-A review | no |
| O7 | RESOLVED — mandatory manual sign-off before merge | no |
| O8 | RESOLVED — Île-de-France parity tolerance 0.001 | no |
| O9 | UNRESOLVED — national benchmark source not acquired | YES |
| O10 | RESOLVED — versioned-first; canonical after Stage A + user approval | no |

**Overall status: BLOCKED on O1, O2, O9.**

No GSUR rebuild code may be executed, and no output parquets may be
written, until O1, O2, and O9 are resolved and the required files are
committed to `Data/external/`.
