> Merged into `docs/France_case/consolidated/RURO_GSUR_rebuild_consolidated_v1.md` on 2026-05-25. See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-25.md`.

# RURO GSUR O2 Denominator Resolution Memo v1

Date: 2026-05-17
Prepared by: Claude Code (claude-sonnet-4-6)
Reference:
  docs/RURO_GSUR_rebuild_specification_v2_1.md §5 (weighting principle)
  docs/RURO_GSUR_external_acquisition_decision_v2.md §7–§8 (O2 decision)
  docs/RURO_GSUR_external_acquisition_completion_v1.md §5, §9 (acquisition outcome)

This memo resolves the three O2 denominator questions left open by the
acquisition completion memo. It answers them with precise data evidence,
states a binding denominator-source decision, and specifies the amendment
required in the open-decisions resolution memo before implementation can
proceed.

---

## 1. The three questions

Per the acquisition completion memo §9 and the user's review finding,
three questions must be answered explicitly:

(Q1) Since D1 (labour force, `lfst_r_lfp2acedu`) lacks Y20-64 and all
narrow source-aligned bands, should the rebuild use D2 (population,
`lfst_r_lfsd2pop`) for both Stage A and Stage B?

(Q2) Is there any alternative official labour-force denominator source
with the exact required age bands and education dimension?

(Q3) If not, should v2.1 be amended to make D2 the operational
denominator source, with D1 used only as a diagnostic comparison where
overlapping bands exist?

---

## 2. Evidence: what D1 actually provides

`lfst_r_lfp2acedu` (Eurostat, "Economically active population by sex,
age, educational attainment level and NUTS 2 regions"):

**Age bands present in the full downloaded dataset (all EU countries,
2016):** Y15-74, Y25-64, Y_GE15.

**Y20-64 rows in the full dataset: zero.** Y20-64 is absent for every
country, not just France. This is confirmed by inspecting the full 2016
SDMX-CSV download (`lfst_r_lfp2acedu_2016_full.csv`, 1.7 MB, all EU).

**Narrow bands (Y15-24, Y25-34, Y35-44, Y45-54, Y55-64) rows: zero.**
Same finding — absent for all countries.

`lfst_r_lfp2acedu` cannot provide:
- Y20-64 (Stage A broad-age GSUR, v2.1 §9)
- Any narrow source-aligned band (Stage B age-specific GSUR, v2.1 §6)

This rules it out as the operational denominator source for both stages.

---

## 3. Evidence: what D2 actually provides

`lfst_r_lfsd2pop` (Eurostat, "Population in private households by
educational attainment level and NUTS 2 region"):

**Age bands present for France NUTS-2 (22 regions):** Y15-24, Y15-64,
Y15-74, Y20-64, Y25-34, Y25-64, Y35-44, Y45-54, Y55-64, Y_GE15,
Y_GE25, Y_GE65.

**Y20-64 coverage (Stage A denominator):**
- 132 cells: 22 regions × 2 sex (M/F) × 3 ISCED (ED0-2, ED3_4, ED5-8)
- All 22 regions present; no missing OBS_VALUE
- 6 cells flagged `u` (unreliable): FRM0 (Corse), all sex×ISCED combos
- OBS_VALUE present in all 6 flagged cells
- **Effective coverage: 126/132 cells fully clean; 6/132 flagged-but-valued**

**Narrow-band coverage (Stage B denominators):**
- 660 cells: 22 regions × 5 bands × 2 sex × 3 ISCED
- 2 cells with missing OBS_VALUE: FRM0/F/Y25-34/ED0-2 and
  FRM0/F/Y15-24/ED5-8
- 56 cells flagged `u`: concentrated in smaller regions (FRC2, FRD1,
  FRE2, FRF2, FRI2 all-bands, FRI3, FRK1, FRM0 all-bands)
- **Effective coverage: 602/660 clean; 56/660 flagged-but-valued;
  2/660 missing value**

D2 provides every age band required by v2.1 for both Stage A and Stage B,
at all 22 France metropolitan NUTS-2 regions.

---

## 4. Evidence: alternative D1 sources

The Eurostat dataflow catalogue was checked for any regional (NUTS-2)
table providing labour-force or economically-active-population by
(sex × education × Y20-64) for France 2016.

**Finding: no such table exists in the Eurostat NUTS-2 catalogue.**
Y20-64 is absent from `lfst_r_lfp2acedu` for all countries — it is not
a published age band in this table at any NUTS level. The related
tables checked (`lfst_r_lfe2eedu`, `lfst_r_lfu3pers`) do not provide
the required (education × Y20-64 × NUTS-2) combination.

The only Eurostat NUTS-2 source with both Y20-64 and education is
`lfst_r_lfsd2pop` (population, not labour force).

A France-specific source (French LFS microdata, Eurostat NUTS-2
microdata replication) could theoretically provide labour-force counts
at narrower disaggregation, but: (a) it would not be a publicly
downloadable Eurostat table, (b) it is not currently available in
the project, and (c) acquiring it would be a new external acquisition
task outside the scope of the current GSUR rebuild. It is not a
viable path for the v2.1 implementation.

**Answer to Q2: No. No alternative D1 source exists within the scope
of this rebuild.**

---

## 5. Binding denominator-source decision

**Decision: adopt D2 (`lfst_r_lfsd2pop`, population in private
households) as the operational denominator source for both Stage A
(Y20-64) and Stage B (narrow age bands). D1 (`lfst_r_lfp2acedu`,
labour force) is retained as a diagnostic comparison source only,
restricted to the overlapping broad bands (Y15-74, Y25-64) where
both D1 and D2 are available.**

Rationale:
- D1 cannot provide Y20-64 or any narrow band at any NUTS level.
  There is no way to use D1 as the primary source for the cells
  the rebuild actually needs.
- D2 provides complete coverage for all required cells.
- v2.1 §5(D2) explicitly states that population weighting is an
  acceptable approximation: "total-population weighting is an
  acceptable approximation. Population weighting is an approximation
  to labour-force weighting and the approximation error depends on how
  labour-force participation rates vary across the contributing cells."
- v2.1 §5(D2) also specifies the documentation requirement: identify
  any subset where both sources are available, compute rates under
  both, and report differences. Under this decision, D1 is used
  exclusively for that diagnostic — not as an operational denominator.

**Answer to Q1: Yes. D2 (population) is used for both Stage A and
Stage B. This is not a concession or a partial fix — D1 cannot serve
the purpose and D2 is the specified acceptable fallback.**

---

## 6. v2.1 amendment required

**Answer to Q3: Yes. v2.1 §5 must be amended to reflect that D1 is
structurally unavailable from Eurostat for France NUTS-2 at the
required age bands, and that D2 is the operational denominator for
this rebuild.**

The amendment is a clarification note, not a specification revision.
The substance of v2.1 §5(D2) already authorises population weighting
as an acceptable approximation; what is missing is an explicit
acknowledgement that the D1 preference cannot be operationalised for
France NUTS-2 at the age-education granularity required.

The amendment text to add to
`docs/RURO_GSUR_v2_1_open_decisions_resolution_v1.md` as a new
resolved item (O2 addendum) is specified in §7 below.

The governing specification `RURO_GSUR_rebuild_specification_v2_1.md`
does not need to be revised. Its §5 already contains the D2 fallback
path and documentation requirements. The addendum in the open-decisions
memo is sufficient to authorise the decision.

---

## 7. O2 addendum for open-decisions resolution memo

The following decision block must be added to
`docs/RURO_GSUR_v2_1_open_decisions_resolution_v1.md` as an amendment
to O2's entry, before implementation may proceed.

---

**O2 addendum — denominator-source resolution (2026-05-17)**

**Evidence established during acquisition:**

(E1) `lfst_r_lfp2acedu` (labour force, D1 in §5) does not publish
Y20-64 or any narrow 10-year band for France or any EU country at
any NUTS level. The full 2016 SDMX-CSV download contains zero rows
with these age values. D1 is structurally unavailable for any cell
the v2.1 rebuild requires.

(E2) `lfst_r_lfsd2pop` (population in private households, D2 in §5)
provides Y20-64 and all five narrow bands for all 22 France
metropolitan NUTS-2 regions with education disaggregation. Y20-64
is clean for 21/22 regions; FRM0 cells are flagged `u` but valued.
No alternative Eurostat NUTS-2 labour-force source with the required
age-education grid exists.

**Decision:**

D2 (`lfst_r_lfsd2pop`) is the operational denominator for both
Stage A (Y20-64) and Stage B (narrow age bands). All cells in
the v2.1 GSUR lookup use `weighting_source = 'population'`.

D1 (`lfst_r_lfp2acedu`, Y15-74 only) is used exclusively as a
diagnostic comparison: at Y15-74, compute the aggregated GSUR rate
under D1 and D2 weighting, and report the difference in the Stage A
validation report. This satisfies v2.1 §5(D2)'s documentation
requirement.

**Fallback cells (D2 suppressed or missing):**

FRI2 (Limousin) narrow bands: all five flagged `u`, OBS_VALUE present.
Use these values; flag as `weighting_source = 'population'`; note
reliability caveat in the validation report.

FRM0 (Corse) narrow bands: all five flagged `u`; 2 cells (F/Y25-34/ED0-2
and F/Y15-24/ED5-8) have missing OBS_VALUE. For the 2 missing cells,
apply D3 (approximate_uniform): set weight equal to 1/N where N is the
number of NUTS-2 components of drgn1=8 (N=3: FRJ1, FRL0, FRM0); flag
as `weighting_source = 'approximate_uniform'`. This requires reviewer
sign-off per v2.1 §5(D3)(b). All other FRM0 cells use D2 with
`weighting_source = 'population'`.

FRM0 Y20-64: 6 cells flagged `u` (all sex×ISCED); OBS_VALUE present.
Use D2; flag as `weighting_source = 'population'`; note reliability
caveat.

**Schema impact:**

The v2.1 `weighting_source` column schema is unchanged:
`labour_force`, `population`, `approximate_uniform`. Under this
decision, `labour_force` will not appear in the operational lookup
because D1 cannot provide the required age bands. It would appear
if the D1 diagnostic comparison produces a separate output, but that
output is not part of the MNL parquet.

---

## 8. Suppression and fallback summary table

For implementation reference:

| Stage | Age band | Denominator | Regions clean | Regions flagged-u | Missing cells | Action |
|---|---|---|---|---|---|---|
| A | Y20-64 | D2 (lfst_r_lfsd2pop) | 21/22 | FRM0 (6 cells) | 0 | use D2; flag FRM0 |
| B | Y15-24 | D2 (lfst_r_lfsd2pop) | 19/22 | FRC2,FRD1,FRE2,FRF2,FRI3,FRK1,FRM0 | 1 (FRM0/F) | use D2; D3 for missing |
| B | Y25-34 | D2 (lfst_r_lfsd2pop) | 19/22 | FRC1,FRC2,FRD1,FRI2,FRK1,FRM0 | 1 (FRM0/F) | use D2; D3 for missing |
| B | Y35-44 | D2 (lfst_r_lfsd2pop) | 20/22 | FRI2,FRK1,FRM0 | 0 | use D2; flag noted |
| B | Y45-54 | D2 (lfst_r_lfsd2pop) | 20/22 | FRI2,FRM0 | 0 | use D2; flag noted |
| B | Y55-64 | D2 (lfst_r_lfsd2pop) | 19/22 | FRC2,FRD1,FRF2,FRI2,FRM0 | 0 | use D2; flag noted |
| Diagnostic | Y15-74 | D1 (lfst_r_lfp2acedu) | 21/22 | FRM0 | 0 | compare D1 vs D2 rate |

---

## 9. Implementation authorization after this decision

If the O2 addendum in §7 is recorded in the open-decisions memo as a
binding resolution, then:

- O1: RESOLVED (crosswalk verified and constructed)
- O2: RESOLVED (denominator source decision recorded; D2 operational)
- O9: RESOLVED (benchmark 9.725%)

**Stage A implementation becomes authorized, subject to O7 crosswalk
sign-off before merge into MNL parquets.**

The 2 missing FRM0 cells require D3 (approximate_uniform) with
reviewer sign-off per v2.1 §5(D3)(b). This sign-off can occur during
the implementation step when those cells are first encountered; it does
not block the implementation prompt from being written.

No new downloads are required. All denominator data is in:
- `Data/external/lfst_r_lfsd2pop_FR_2016.tsv` (operational)
- `Data/external/lfst_r_lfp2acedu_FR_2016.tsv` (diagnostic only)