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
| Deferred decisions | O6 (Stage B necessity — deferred to post-Stage-A review) |
| Unresolved decisions | O1, O2, O9 |
| Overall readiness for implementation | BLOCKED — see §4 |

---

## Locally resolved decisions

### O3 — Age-65 handling

**Decision: A65-3 (map age 65 to Y20-64 broad fallback with explicit flag).**

Individuals aged 65 are assigned the Y20-64 broad working-age GSUR
(`gsur`) as fallback. The output column `gsur_age_band_used` must carry
the value `"Y20-64_fallback_age65"` for these rows, distinguishing them
from the standard `"Y55-64"` assignment. This is the A65-3 option as
defined in §7 of the canonical spec.

**File evidence (confirmed 2026-05-17, canonical MNL parquet):**
- Singles: 200 rows with `dag == 65` out of 167,600 total rows,
  representing 2 households. Couples: 0 rows.
- Sample impact is negligible (2 households, 0.12% of the singles
  estimation sample).

**Why not A65-1 (exclude) or A65-2 (map to Y55-64):**
A65-1 would silently drop 2 valid single-household respondents from the
estimation sample. A65-2 would assign the Y55-64 rate, which by Eurostat
definition covers ages 55 to 64 and does not include age 65; the
resulting rate is a systematic misassignment. A65-3 provides honest
broad working-age coverage and is self-documenting via the flag column.

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
| 0.0 | 0 | 4,800 |
| 1.0 | 0 | 4,400 |
| 2.0 | 0 | 16,400 |
| 3.0 | 1 | 73,600 |
| 4.0 | 1 | 500 |
| 5.0 | 2 | 67,900 |

The crosstab is perfectly monotone — each deh value maps to exactly one
educ3 value with no overlap. The proposed mapping is already encoded in
the data; no transformation ambiguity exists.

Couples use gender-specific variants: `deh_male` → `educ3_male` and
`deh_female` → `educ3_female`, following the same three-way mapping.

---

### O5 — DOM / drgn1 = 9 handling

**Decision: retain drgn1 = 9 in the output schema but leave it empty
(NaN) for the France 2016 metropolitan sample.**

For France 2016 (metropolitan sample), no respondents carry `drgn1 = 9`;
those rows receive NaN for all GSUR columns. The output schema retains
`drgn1 = 9` as a valid category slot so that the lookup table structure
remains portable. If DOM respondents appear in a future data pull, the
lookup must be extended with DOM-specific Eurostat data to populate those
cells; the schema slot alone is not sufficient and would not be populated
automatically.

No special-casing, exclusion, or warning is required for `drgn1 = 9` in
the current run.

---

### O7 — Crosswalk sign-off

**Decision: mandatory manual sign-off before merge.**

Once the O1 crosswalk is constructed, the `drgn1`-to-NUTS2 crosswalk
(§4 of the spec) and the GSUR age-education join key must be reviewed and
approved by the user before merging into the MNL parquets — that is,
before any output parquet is written to versioned (`_GSURv2`) paths. The
sign-off must be recorded as an explicit user approval message referencing
the crosswalk file and the merge key used.

This requirement applies once, at crosswalk-construction time, before
the merge step that produces the GSURv2 versioned parquets.

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

1. Stage A produces a verdict of SA-STANDS or SA-REVISION (per §9.3 of
   the spec); SA-OVERTURNED does not authorise promotion.
2. The user explicitly approves promotion in a recorded approval message
   after the Stage A verdict is issued.

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

The spec requires labour-force denominators by (modern NUTS-2 or NUTS-3
× sex × education × age band) for France 2016, sourced from Eurostat LFS
microdata or published LFS aggregates per §5(D1) of the spec. If
education-stratified denominators are unavailable, population denominators
may be used (§5(D2)); if neither is available, the aggregation must be
flagged as approximate per §5(D3). The current GSUR workbook's denominator
source is not documented in the audit.

**Blocking question:** Are labour-force denominators by (region × sex ×
education × age band) available for France 2016 in Eurostat or INSEE? If
not, are population denominators available at that granularity?

**To resolve:** Identify the specific Eurostat dataset (table code and
reference period), confirm its dimensional coverage (must include education
or document why the D3 fallback applies), download or confirm access, and
record the citation in `Data/external/gsur_denominator_source.txt`.

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
