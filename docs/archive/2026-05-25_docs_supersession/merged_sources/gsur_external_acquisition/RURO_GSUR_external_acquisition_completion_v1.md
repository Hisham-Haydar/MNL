> Merged into `docs/France_case/consolidated/RURO_GSUR_external_acquisition_consolidated_v1.md` on 2026-05-25. See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-25.md`.

# RURO GSUR External Acquisition — Completion Memo v1

Date: 2026-05-17
Prepared by: Claude Code (claude-sonnet-4-6)
Reference: docs/RURO_GSUR_external_acquisition_decision_v2.md (governing
decision memo); docs/RURO_GSUR_rebuild_specification_v2_1.md (governing spec)

This memo records the outcome of the GSUR external asset acquisition
task specified in the decision memo §16. It documents the three
required downloads, the crosswalk construction, the suppression
inventory, the benchmark extraction, and the updated readiness verdict.
No GSUR rebuild code has been run; no MNL parquets have been written.

---

## 1. Acquisition verdict

**PARTIAL ACQUISITION SUCCESS. O1 and O9 resolved. O2 remains
unresolved. Stage A implementation is NOT authorized.**

Summary of blocker status:

| Blocker | Decision | Status |
|---|---|---|
| Blocker 1 — NUTS2013-NUTS2016.xlsx | O1 | RESOLVED |
| Blocker 2 — lfst_r_lfp2acedu denominator | O2 | UNRESOLVED — dimensional mismatch |
| Blocker 3 — INSEE BDM 001688526 benchmark | O9 | RESOLVED |

O2 is unresolved because the acquired labour-force denominator
(`lfst_r_lfp2acedu`) does not provide the narrow age-band structure
(Y15-24, Y25-34, Y35-44, Y45-54, Y55-64) that the v2.1 specification
§6 requires for source-aligned age binning. This is a structural
limitation of the Eurostat publication — the table is not published at
narrow age bands for France NUTS-2 at any level. A denominator-
resolution decision is required before implementation can proceed.

O1 and O9 are fully resolved and their evidence is archived.

---

## 2. Files downloaded

All three required downloads were successful:

| File | Source | Size | Date |
|---|---|---|---|
| `Data/external/NUTS2013-NUTS2016.xlsx` | Eurostat History of NUTS | 373,947 bytes | 2026-05-17 |
| `Data/external/lfst_r_lfp2acedu_2016_full.csv` | Eurostat SDMX-CSV API | 1,732,181 bytes | 2026-05-17 |
| `Data/external/lfst_r_lfsd2pop_2016_full.csv` | Eurostat SDMX-CSV API | 7,214,941 bytes | 2026-05-17 |
| `Data/external/insee_001688526_raw` | INSEE BDM API (values captured) | n/a | 2026-05-17 |

The population fallback (`lfst_r_lfsd2pop`) was downloaded because
denominator suppression in `lfst_r_lfp2acedu` was confirmed non-trivial
(Corse FRM0 suppressed), per the decision memo §15 instruction.

---

## 3. Files created manually

| File | Purpose | Status |
|---|---|---|
| `Data/external/fr_drgn1_to_nuts2_crosswalk.csv` | O1 verified crosswalk | created |
| `Data/external/lfst_r_lfp2acedu_FR_2016.tsv` | O2 filtered primary extract | created |
| `Data/external/lfst_r_lfsd2pop_FR_2016.tsv` | O2 filtered population fallback | created |
| `Data/external/insee_001688526_2016.csv` | O9 benchmark quarterly + annual | created |
| `Data/external/gsur_crosswalk_source.txt` | O1 provenance | created |
| `Data/external/gsur_denominator_source.txt` | O2 provenance + suppression | created |
| `Data/external/gsur_benchmark_source.txt` | O9 provenance | created |

Schema of `fr_drgn1_to_nuts2_crosswalk.csv`:
`drgn1, old_nuts2_code, region_name, new_nuts2_code_2016, verified_against_eurostat`
(22 rows; all `verified_against_eurostat = YES`).

---

## 4. O1 — NUTS-2 crosswalk resolution

**O1: RESOLVED.**

`NUTS2013-NUTS2016.xlsx` downloaded from:
`https://ec.europa.eu/eurostat/documents/345175/629341/NUTS2013-NUTS2016.xlsx`

Verification used the "Correspondence NUTS-2" sheet. 26 France rows
were found (22 metropolitan + 4 DOM + Mayotte). The 22 metropolitan
rows were extracted. FR10 (Île-de-France) was not listed because
its code was unchanged; it was added with `verified_against_eurostat=YES`
and `change=unchanged`.

All 22 old NUTS-2 codes resolved to new codes without ambiguity.
The change type is `recoded` for all 21 codes that changed (pure
letter-code renaming; no boundary changes at NUTS-2 level). FR10
is `unchanged`. This confirms the decision memo §3(C1) finding.

drgn1 → new NUTS-2 constituent codes:

| drgn1 | new NUTS-2 codes (NUTS 2016) |
|---|---|
| 1 | FR10 |
| 2 | FRF2, FRE2, FRD2, FRB0, FRD1, FRC1 |
| 3 | FRE1 |
| 4 | FRF3, FRF1, FRC2 |
| 5 | FRG0, FRH0, FRI3 |
| 6 | FRI1, FRJ2, FRI2 |
| 7 | FRK2, FRK1 |
| 8 | FRJ1, FRL0, FRM0 |

O7 sign-off (per O7 resolution): crosswalk sign-off is required before
merging into MNL parquets, not at this acquisition step.

---

## 5. O2 — denominator acquisition and dimensional mismatch

**O2: UNRESOLVED — dimensional mismatch on age bands.**

### 5.1 What was acquired

`lfst_r_lfp2acedu` (labour-force, primary denominator D1) was
downloaded as a full 2016 SDMX-CSV (all EU countries) and filtered to
the 22 France metropolitan NUTS-2 codes. The filtered extract
(`lfst_r_lfp2acedu_FR_2016.tsv`) has 986 rows.

`lfst_r_lfsd2pop` (population, fallback denominator D2) was likewise
downloaded and filtered (`lfst_r_lfsd2pop_FR_2016.tsv`, 4,057 rows).

### 5.2 Dimensional mismatch

The v2.1 specification §9 requires the Stage A `gsur` column to use
the Y20-64 broad-age cell. The v2.1 specification §6 additionally
requires Stage B denominators at narrow 10-year bands (Y15-24,
Y25-34, Y35-44, Y45-54, Y55-64).

**`lfst_r_lfp2acedu` does not provide Y20-64, nor any narrow age
band.** The full downloaded dataset — covering all EU countries and
all NUTS levels — contains zero rows with Y20-64, Y15-24, Y25-34,
Y35-44, Y45-54, or Y55-64. The age dimension is limited to Y15-74,
Y25-64, and Y_GE15 only. This is a structural publication limitation
of the table, not a France-specific suppression issue.

Implication: `lfst_r_lfp2acedu` cannot serve as D1 denominator for
Stage A (Y20-64 absent) or for any Stage B narrow-age cell. The v2.1
§5(D1) preference for labour-force weighting cannot be operationalised
for any cell the rebuild requires.

### 5.3 Population fallback availability

`lfst_r_lfsd2pop` **does** provide the narrow age bands for France
NUTS-2. Confirmed coverage: 660 cells (22 regions × 5 age bands × 2
sex × 3 ISCED = 660), with the following caveat:

- 56 cells carry OBS_FLAG=`u` (unreliable): concentrated in smaller
  regions (FRC2, FRD1, FRE2, FRF2, FRI2, FRI3, FRK1, FRM0) and the
  Y15-24 / Y25-34 bands where sample sizes are small
- 2 of the 660 cells have missing OBS_VALUE: FRM0/F/Y25-34/ED0-2 and
  FRM0/F/Y15-24/ED5-8
- The remaining cells (600+ of 660) are populated

Suppressed narrow-band cells by region and age band:

| region | suppressed age bands |
|---|---|
| FRC1 | Y25-34 |
| FRC2 | Y15-24, Y25-34, Y55-64 |
| FRD1 | Y15-24, Y25-34 |
| FRE2 | Y15-24 |
| FRF2 | Y15-24, Y55-64 |
| FRI2 | all five bands |
| FRI3 | Y15-24 |
| FRK1 | Y15-24, Y25-34, Y35-44 |
| FRM0 | all five bands |

FRI2 (Limousin) and FRM0 (Corse) have all narrow bands suppressed or
flagged unreliable in the population fallback.

### 5.4 Decision required

Using `lfst_r_lfsd2pop` as the narrow-age denominator changes the
weighting method from D1 (labour-force) to D2 (population) for
**all** age-disaggregated cells, not just Corse. Per v2.1 §5(D2),
population weighting is an acceptable approximation, but:
- It must be documented empirically where possible
- All cells using population weighting must be flagged
  `weighting_source = 'population'`
- The approximation error (D1 vs D2) must be estimated wherever
  both sources are available

Additionally, for FRI2 and FRM0 cells where the population fallback
is itself suppressed/unreliable, D3 (approximate_uniform) or D1/D2
at broad age band would be the only remaining option — requiring an
explicit decision per v2.1 §5(D3).

**The denominator-resolution decision for O2 is: accept D2
(population, `lfst_r_lfsd2pop`) as the narrow-age denominator for
all cells, with D1 (labour-force, broad age only) used where an
explicit broad-age rate is needed; document the D1-vs-D2 comparison
at Y15-74 level. This requires a v2.1 §5 clarification note
(or a v2.2 addendum) acknowledging that D1 at narrow age bands is
structurally unavailable from Eurostat for France NUTS-2.**

Until this decision is recorded as a binding resolution (analogous
to O3–O10 in the open-decisions memo), O2 remains unresolved.

---

## 6. O2 — suppression inventory summary

This section documents the cell-level suppression in `lfst_r_lfp2acedu`
(the acquired primary extract) for implementation reference.

**Primary extract (`lfst_r_lfp2acedu`, labour force):**
- Total cells: 986
- Suppressed (OBS_FLAG=`u`): 220 (22.3%)
- Pattern A — NRP isced category: 219 cells, all regions. NRP is not
  a usable education category; excluded regardless.
- Pattern B — FRM0 (Corse): all 45 cells flagged `u`, including the
  3 usable isced categories. OBS_VALUE present but unreliable.
- Among usable education cells (ED0-2, ED3_4, ED5-8; sex M/F):
  18 cells suppressed, all in FRM0.
- 21 of 22 regions: zero suppressed usable cells.

**Narrow-age population fallback (`lfst_r_lfsd2pop`):**
- 660 narrow-band education cells for 22 regions
- 56 cells with OBS_FLAG=`u` (8.5%)
- Concentrated in FRI2 (Limousin) and FRM0 (Corse): fully suppressed
- 7 additional regions with partial suppression on Y15-24/Y25-34

**Broad-age coverage (`lfst_r_lfp2acedu`, Y15-74, Y25-64):**
- All 22 regions, 21 clean; FRM0 flagged `u` but OBS_VALUE present
- Usable as broad-age fallback for cells where narrow-age fails

---

## 7. O9 — benchmark extraction

**O9: RESOLVED.**

- Series: INSEE BDM `001688526`
- Title: "Taux de chômage au sens du BIT — Ensemble — France
  métropolitaine — CVS" (ILO unemployment rate, Metropolitan France,
  seasonally adjusted)
- REF_AREA: FM (metropolitan France only — correct for this sample)
- URL: `https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688526`
- Extraction date: 2026-05-17
- Archive: `Data/external/insee_001688526_2016.csv`

**2016 quarterly values:**

| Quarter | Rate (%) |
|---|---|
| Q1 2016 | 9.9 |
| Q2 2016 | 9.7 |
| Q3 2016 | 9.6 |
| Q4 2016 | 9.7 |

**2016 annual average (simple mean of four quarters): 9.725%**

Why INSEE `001688526` not Eurostat `FR`: Eurostat `geo=FR` gives
10.1% (France hors Mayotte, includes DOM). The MNL sample is
metropolitan France only (drgn1=1–8). INSEE REF_AREA=FM is the
correct benchmark.

---

## 8. Updated readiness ladder

| Level | Pre-acquisition | Post-acquisition |
|---|---|---|
| acquisition-ready | YES | YES |
| asset-inventory-ready | NO | YES |
| crosswalk-construction-ready | NO | YES (O1 resolved) |
| GSUR-lookup-generation-ready | NO | NO (O2 denominator decision pending) |
| MNL-rebuild-ready | NO | NO |
| estimation-ready | NO | NO |

The project has moved from acquisition-ready to crosswalk-construction-
ready / asset-inventory-ready. GSUR-lookup-generation-ready requires O2
to be resolved first.

---

## 9. Remaining blocker: O2 denominator-resolution decision

One concrete decision is needed before implementation can proceed:

**O2 denominator-resolution decision**: The v2.1 spec §5(D1) preference
for labour-force denominators cannot be satisfied at narrow age-band
granularity for France NUTS-2. Eurostat does not publish
`lfst_r_lfp2acedu` (or any labour-force table with education) at
narrow age bands below Y15-74 for NUTS-2 regions. The population
fallback `lfst_r_lfsd2pop` does provide narrow age bands and is fully
downloaded.

The resolution options are:

**(R1) Accept D2 (population) as the operational denominator for both
Stage A (Y20-64) and Stage B (narrow bands).**
Use `lfst_r_lfsd2pop` for all cells. Set `weighting_source = 'population'`
throughout. D1 (`lfst_r_lfp2acedu`, Y15-74 only) is used exclusively
as a diagnostic comparison at Y15-74 to estimate the D1-vs-D2
approximation error, as required by v2.1 §5(D2). D1 does not appear
in the operational lookup. For FRI2 and FRM0 cells where D2 is also
suppressed or missing, apply D3 (approximate_uniform) with reviewer
sign-off per v2.1 §5(D3)(b).
Record this as an addendum to the open-decisions resolution memo.
See docs/RURO_GSUR_O2_denominator_resolution_v1.md for full analysis.

**(R2) Drop age disaggregation; use only Y15-74 broad-age GSUR rates.**
This reverses the v2.1 key improvement over v1. Not recommended.

**(R3) Issue v2.2 specification** clarifying that narrow-age
denominators use D2 (population) as primary in lieu of the
structurally unavailable D1. Formalises R1 in the governing document.

R1 (with a binding O2 addendum in the open-decisions memo) or R3 are
the viable paths. Either requires an explicit user decision before the
implementation prompt is written.

---

## 10. Implementation authorization

**Stage A implementation is NOT authorized.**

O2 remains unresolved. The dimensional mismatch on the denominator
age structure must be resolved — either by accepting D2 (population)
as the narrow-age denominator (R1/R3 above) or by revising the spec.

O1 and O9 are fully resolved. The crosswalk is constructed and
verified. The benchmark annual average is confirmed at 9.725%.

The denominator files are all downloaded and available:
- `lfst_r_lfp2acedu_FR_2016.tsv`: usable for broad-age cells (Y15-74)
- `lfst_r_lfsd2pop_FR_2016.tsv`: usable for narrow-age cells (D2)

Implementation can proceed immediately once O2 is resolved.

---

## 11. Corrections to prior outputs

This section records corrections to deliverables that were wrong in
the first draft of this memo.

**(E1) Crosswalk schema**: the first draft used column names `drgn2,
old_nuts2, new_nuts2, region_label, nuts2013_to_2016_change`.
The required schema is `drgn1, old_nuts2_code, region_name,
new_nuts2_code_2016, verified_against_eurostat`. The file has been
rebuilt with the correct schema. `drgn2` (the intermediate step) is
not included in the deliverable file; it is documented in
`gsur_crosswalk_source.txt`.

**(E2) lfst_r_lfsd2pop_FR_2016.tsv missing**: the first draft
created only the full download (`lfst_r_lfsd2pop_2016_full.csv`)
without creating the filtered FR extract. The filtered extract has
been created.

**(E3) gsur_denominator_source.txt schema drift**: the first draft
wrote `F4=national` as a fourth weighting-source value. The v2.1
spec allows only `labour_force`, `population`, `approximate_uniform`.
The file has been corrected.

**(E4) Overstatement of FRM0 fallback**: the first draft said FRM0
was "cleanly resolved" by the population fallback. In fact, the
population fallback cells for FRM0 also carry OBS_FLAG=`u`. The
values are present but flagged unreliable — this is an approximation
decision, not a clean resolution.

**(E5) O2 verdict**: the first draft declared O2 resolved and
implementation authorized. The correct verdict is O2 unresolved
because the primary denominator lacks the required narrow age-band
dimension. Implementation is not authorized.

---

## 12. Exact next step

The next task is a narrow **O2 denominator-resolution decision**,
not the GSUR rebuild implementation.

The decision must record: whether R1 (accept D2 population for
narrow-age cells), R2 (drop age disaggregation), or R3 (issue v2.2
spec) is the binding path; and how FRI2 / FRM0 fully-suppressed cells
are handled (D3 approximate_uniform with sign-off, or D1 broad-age
fallback per v2.1 §5(D3)).

Once that decision is recorded as an O2 addendum in
`docs/RURO_GSUR_v2_1_open_decisions_resolution_v1.md`, the
implementation prompt for the GSUR v2.1 rebuild (per decision memo
§16 final paragraph and v2.1 spec §15) can be written.

**Files ready for implementation** (no further download needed):
- `Data/external/fr_drgn1_to_nuts2_crosswalk.csv`
- `Data/external/lfst_r_lfp2acedu_FR_2016.tsv` (broad-age D1)
- `Data/external/lfst_r_lfsd2pop_FR_2016.tsv` (narrow-age D2)
- `Data/external/insee_001688526_2016.csv` (O9 benchmark)
- `Data/external/FR_gsur_full.csv` or `FR_gsur.xlsx` (GSUR source,
  at NUTS-2 level; NOT `FR_gsur_ruro.csv` which is at wrong granularity)