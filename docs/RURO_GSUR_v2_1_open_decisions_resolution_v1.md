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
| Resolved decisions | O1, O2, O3, O4, O5, O7, O8, O9, O10 |
| Deferred decisions | O6 (Stage B necessity — deferred to post-Stage-A review) |
| Unresolved decisions | none |
| Overall readiness for implementation | AUTHORIZED — pending O7 crosswalk sign-off before merge |

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

## Decisions resolved by external acquisition

The following three decisions were unresolved at initial memo writing
and have since been resolved by the external acquisition task completed
2026-05-17. Evidence and source files are in `Data/external/`.

### O1 — Crosswalk source requirement

**Status: RESOLVED (2026-05-17).**

The `drgn1`-to-NUTS2 crosswalk is constructed and verified. The
three-step chain is fully documented:

1. `drgn1` groupings → `drgn2` values: from EUROMOD France 2016 DRD
   (`docs/euromod_reference/DRD_FR_2016_a3_export.txt`)
2. `drgn2` → old NUTS-2 (FR10–FR83): from the same DRD
3. Old NUTS-2 → new NUTS-2 (NUTS 2016 codes): verified against
   `Data/external/NUTS2013-NUTS2016.xlsx` (Eurostat, downloaded
   2026-05-17, sheet "Correspondence NUTS-2")

All 22 metropolitan NUTS-2 codes resolved without ambiguity. FR10
(Île-de-France) is unchanged; all others recoded 1:1.

**Deliverable:** `Data/external/fr_drgn1_to_nuts2_crosswalk.csv`
Schema: `drgn1, old_nuts2_code, region_name, new_nuts2_code_2016,
verified_against_eurostat`. All 22 rows have
`verified_against_eurostat = YES`.

Provenance: `Data/external/gsur_crosswalk_source.txt`.

O7 sign-off (mandatory before merge into MNL parquets) remains a
separate procedural step at crosswalk-construction time.

---

### O2 — Denominator data requirement

**Status: RESOLVED (2026-05-17) — see addendum below.**

**Initial question:** Are labour-force or population denominators
available at (NUTS-2 × sex × education × age band) granularity for
France 2016?

**Finding from acquisition (2026-05-17):**

The preferred D1 source (`lfst_r_lfp2acedu`, Eurostat labour-force
by NUTS-2 × sex × age × education) does not publish Y20-64 or any
narrow 10-year age band for France or any EU country. The full 2016
SDMX-CSV download contains zero rows with Y20-64, Y15-24, Y25-34,
Y35-44, Y45-54, or Y55-64. D1 cannot serve as the operational
denominator for either Stage A (Y20-64) or Stage B (narrow bands).

The D2 source (`lfst_r_lfsd2pop`, Eurostat population in private
households by NUTS-2 × sex × age × education) provides all required
age bands including Y20-64 and all five narrow bands, for all 22
France metropolitan NUTS-2 regions. No alternative D1 source at the
required age-education granularity exists in the Eurostat NUTS-2
catalogue.

Full analysis: `docs/RURO_GSUR_O2_denominator_resolution_v1.md`.

**O2 addendum — denominator-source binding decision:**

D2 (`lfst_r_lfsd2pop`, population in private households) is the
operational denominator source for both Stage A (Y20-64) and Stage B
(narrow age bands). All cells in the v2.1 GSUR lookup carry
`weighting_source = 'population'`. This is authorised by v2.1 §5(D2),
which states that population weighting is an acceptable approximation
when labour-force denominators at the required disaggregation are
unavailable.

D1 (`lfst_r_lfp2acedu`, Y15-74 only) is used exclusively as a
diagnostic comparison: at Y15-74, compute the aggregated GSUR rate
under D1 and D2 weighting and report the difference in the Stage A
validation report, satisfying v2.1 §5(D2)'s documentation requirement.
D1 does not appear in the operational lookup or in the MNL parquets.

**Fallback cells:**

FRI2 (Limousin) narrow bands: all five age-band cells flagged `u`
(unreliable) in `lfst_r_lfsd2pop`; OBS_VALUE present. Use these
values; flag as `weighting_source = 'population'`; note reliability
caveat in the validation report.

FRM0 (Corse) narrow bands: all five age-band cells flagged `u`; 2
cells have missing OBS_VALUE (F/Y25-34/ED0-2 and F/Y15-24/ED5-8).
For the 2 missing cells, apply D3 (approximate_uniform) with reviewer
sign-off per v2.1 §5(D3)(b): set weight = 1/3 (drgn1=8 has three
NUTS-2 components: FRJ1, FRL0, FRM0). Flag as
`weighting_source = 'approximate_uniform'`. All other FRM0 cells use
D2 with `weighting_source = 'population'`.

FRM0 Y20-64 (Stage A): 6 cells flagged `u`; OBS_VALUE present. Use
D2; flag in validation report.

**Deliverables:**
- `Data/external/lfst_r_lfsd2pop_FR_2016.tsv` (operational: 4,057 rows)
- `Data/external/lfst_r_lfp2acedu_FR_2016.tsv` (diagnostic only: 986 rows)
- `Data/external/gsur_denominator_source.txt`

---

### O9 — National benchmark requirement

**Status: RESOLVED (2026-05-17).**

The correct benchmark is INSEE BDM série `001688526`:
- Title: "Taux de chômage au sens du BIT — Ensemble — France
  métropolitaine — CVS" (ILO unemployment rate, Metropolitan France,
  seasonally adjusted)
- REF_AREA: FM (metropolitan France only — correct for this sample,
  which excludes DOM)
- URL: `https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688526`
- Extraction date: 2026-05-17

Why not Eurostat `une_rt_a` / `geo=FR` (10.1%): that figure covers
France hors Mayotte (métropole + 4 DOM). The MNL sample is
metropolitan France only (drgn1=1–8). INSEE REF_AREA=FM is the
correct perimeter.

**2016 annual average: 9.725%**
Quarterly values: Q1=9.9%, Q2=9.7%, Q3=9.6%, Q4=9.7%.
Annual average = simple mean of four quarters.

Tolerance for Stage A validation: 0.001 absolute (per O8 resolution).

**Deliverables:**
- `Data/external/insee_001688526_2016.csv`
- `Data/external/gsur_benchmark_source.txt`

---

## Files acquired (2026-05-17)

All external files required for O1, O2, and O9 are now committed to
`Data/external/`. No further downloads are required.

| File | Purpose | Decision |
|------|---------|---------|
| `NUTS2013-NUTS2016.xlsx` | Official NUTS renaming correspondence | O1 |
| `fr_drgn1_to_nuts2_crosswalk.csv` | Verified drgn1→NUTS2 crosswalk | O1 |
| `gsur_crosswalk_source.txt` | O1 provenance | O1 |
| `lfst_r_lfsd2pop_FR_2016.tsv` | Population denominators (operational) | O2 |
| `lfst_r_lfp2acedu_FR_2016.tsv` | Labour-force denominators (diagnostic only) | O2 |
| `gsur_denominator_source.txt` | O2 provenance + suppression inventory | O2 |
| `insee_001688526_2016.csv` | National benchmark (9.725% annual 2016) | O9 |
| `gsur_benchmark_source.txt` | O9 provenance | O9 |

---

## Sources to cite

External sources are acquired and documented. Citations are already
recorded in the three provenance files. The Stage A validation report
must copy citations from these sources:

| Source | Provenance file |
|---|---|
| Eurostat NUTS2013-NUTS2016.xlsx (O1) | `Data/external/gsur_crosswalk_source.txt` |
| Eurostat lfst_r_lfsd2pop (O2 operational) | `Data/external/gsur_denominator_source.txt` |
| Eurostat lfst_r_lfp2acedu (O2 diagnostic) | `Data/external/gsur_denominator_source.txt` |
| INSEE BDM 001688526 (O9) | `Data/external/gsur_benchmark_source.txt` |

The validation report (`Results/RURO_GSUR_v2_stage_A_validation_report_v1.md`)
must reproduce these citations in full, with date of access and URL.

---

## Blocking status

| Decision | Status | Blocking? |
|----------|--------|-----------|
| O1 | RESOLVED — crosswalk verified; fr_drgn1_to_nuts2_crosswalk.csv created | no — O7 sign-off pending |
| O2 | RESOLVED — D2 (population) operational; D1 diagnostic; 2 FRM0 cells → D3 with sign-off | no — D3 sign-off at implementation |
| O3 | RESOLVED — A65-3 broad-age fallback with flag | no |
| O4 | RESOLVED — deh 0/1/2→0, 3/4→1, 5→2 | no |
| O5 | RESOLVED — drgn1=9 in schema, NaN for FR 2016 metropolitan | no |
| O6 | DEFERRED — Stage B necessity; deferred to post-Stage-A review | no |
| O7 | RESOLVED — mandatory manual sign-off before merge | PENDING (sign-off required before merge step) |
| O8 | RESOLVED — Île-de-France parity tolerance 0.001 | no |
| O9 | RESOLVED — INSEE BDM 001688526; 2016 annual average = 9.725% | no |
| O10 | RESOLVED — versioned-first; canonical after Stage A + user approval | no |

**Overall status: AUTHORIZED for implementation.**

All hard-blocker decisions (O1, O2, O9) are resolved. Stage A
implementation may proceed. The remaining procedural requirement is
O7 crosswalk sign-off, which must be obtained as an explicit user
approval message before the merge step that writes to versioned
GSURv2 parquet paths. It does not block writing the implementation
prompt or running the pre-merge build steps.

The 2 FRM0 D3 cells (approximate_uniform) require reviewer sign-off
per v2.1 §5(D3)(b) at the point those cells are first encountered
in the implementation. This does not block the implementation prompt.
