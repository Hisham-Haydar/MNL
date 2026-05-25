# RURO GSUR v2 Stage A — Lookup Validation Report v1

Date: 2026-05-17
Lookup file: `Data/external/FR_gsur_ruro_v2_stageA.parquet`
Script: `scripts/enhanced/enh_prepare_FR_gsur_v2.py`
Reference spec: `docs/France_case/RURO_GSUR_rebuild_specification_v2_1.md`

---

## 1. Input files used

| File | Purpose | Rows / Size |
|---|---|---|
| `Data/external/FR_gsur.xlsx` | Eurostat unemployment rates — `lfst_r_lfu3rt__custom_19204794` | 120 sheets; extracted 552 geo × isced × sex × age records for FR metro NUTS-2 |
| `Data/external/fr_drgn1_to_nuts2_crosswalk.csv` | drgn1→NUTS-2 crosswalk (O1) | 22 rows; all verified |
| `Data/external/lfst_r_lfsd2pop_FR_2016.tsv` | D2 population denominators (O2 operational) | 4,057 rows; filtered to 1,584 usable rows (metro NUTS-2 × MF sex × educ3 ISCED) |
| `Data/external/lfst_r_lfp2acedu_FR_2016.tsv` | D1 labour-force denominators (O2 diagnostic only) | 986 rows; filtered to 132 rows (Y15-74, metro NUTS-2 × MF sex × educ3 ISCED) |
| `Data/external/insee_001688526_2016.csv` | National benchmark (O9) | 9.725% annual average 2016 |

---

## 2. Crosswalk rows and support

**Crosswalk file:** `Data/external/fr_drgn1_to_nuts2_crosswalk.csv`

| drgn1 | Label | old NUTS-2 components | new NUTS-2 (2016) components | n |
|---|---|---|---|---|
| 1 | Île-de-France | FR10 | FR10 | 1 |
| 2 | Bassin Parisien | FR21, FR22, FR23, FR24, FR25, FR26 | FRF2, FRE2, FRD2, FRB0, FRD1, FRC1 | 6 |
| 3 | Nord-Pas-de-Calais | FR30 | FRE1 | 1 |
| 4 | Est | FR41, FR42, FR43 | FRF3, FRF1, FRC2 | 3 |
| 5 | Ouest | FR51, FR52, FR53 | FRG0, FRH0, FRI3 | 3 |
| 6 | Sud-Ouest | FR61, FR62, FR63 | FRI1, FRJ2, FRI2 | 3 |
| 7 | Rhône-Alpes / Auvergne | FR71, FR72 | FRK2, FRK1 | 2 |
| 8 | Méditerranée | FR81, FR82, FR83 | FRJ1, FRL0, FRM0 | 3 |
| 9 | DOM (stub) | FR91–94 | — (NaN, O5) | 0 |

All 22 rows: `verified_against_eurostat = YES`.
FR10 (Île-de-France) unchanged under NUTS 2016 reform — absent from
Eurostat NUTS2013-NUTS2016.xlsx correspondence sheet by design (code
unchanged); confirmed as FR10 → FR10.

---

## 3. GSUR workbook sheets, geography, and year support

**Workbook:** `Data/external/FR_gsur.xlsx`  
**Dataset:** `lfst_r_lfu3rt__custom_19204794`  
**Last updated:** 11/09/2025  
**Year used:** 2016

Sheets used for Stage A:

| Sheets | isced11 | sex | age band | Purpose |
|---|---|---|---|---|
| Sheet 45, 55 | ED0-2 | M, F | Y20-64 | Stage A operational |
| Sheet 75, 85 | ED3_4 | M, F | Y20-64 | Stage A operational |
| Sheet 105, 115 | ED5-8 | M, F | Y20-64 | Stage A operational |
| Sheet 43, 53, 73, 83, 103, 113 | ED0-2, ED3_4, ED5-8 | M, F | Y15-74 | D1 vs D2 diagnostic |
| Sheet 5 | TOTAL | T | Y20-64 | Legacy gsur reconstruction |

All 22 metropolitan France NUTS-2 codes present for all required combinations
in the 2016 column (column index 20). Year column confirmed at position 20
across all parsed sheets.

---

## 4. Denominator source used

**Operational:** D2 (`lfst_r_lfsd2pop`) for all Stage A cells.

Rationale (O2 binding decision): D1 (`lfst_r_lfp2acedu`) does not publish
Y20-64 for any EU country at any NUTS level. The complete 2016 SDMX-CSV
download contains zero rows with Y20-64. D1 cannot serve as the Stage A
operational denominator. D2 (population in private households) provides
Y20-64 for all 22 metropolitan NUTS-2 regions with education stratification.
v2.1 §5(D2) authorises population weighting as an acceptable approximation.

All 54 output rows carry `weighting_source = 'population'`.
No `labour_force` rows appear in the Stage A lookup.
No `approximate_uniform` (D3) rows appear in the Stage A lookup.
(The two D3 cells — FRM0/F/Y25-34/ED0-2 and FRM0/F/Y15-24/ED5-8 — are
narrow-band Stage B cells and do not affect Y20-64 Stage A.)

---

## 5. Denominator suppression and fallback flags

**Y20-64 D2 coverage by region:**

All 22 metropolitan NUTS-2 regions have `OBS_VALUE` present for Y20-64.
Six cells flagged `u` (unreliable): all within FRM0 (Corse), all sex × ISCED
combinations. These cells carry OBS_VALUE and are used per O2 resolution
("use D2; flag in validation report").

**denom_flag summary in output:**

| denom_flag | n rows | Meaning |
|---|---|---|
| (empty) | 18 | No suppression in any contributing D2 cell; UR source also clean |
| `u` | 24 | At least one contributing cell has OBS_FLAG=u in D2 or UR source |
| `u_u` | 6 | Both UR source and D2 cells carry OBS_FLAG=u (drgn1=8, Méditerranée, which includes FRM0) |
| `drgn1_9_dom_absent_fr2016` | 6 | O5 stub; drgn1=9 absent from FR 2016 metropolitan sample |

**gsur_unreliable summary:**

| gsur_unreliable | n rows |
|---|---|
| False | 18 (drgn1=1,2(educ3=1),3,4(M,educ3=1),5(M/F,educ3=1),+singles) |
| True | 36 |

**FRM0 note (drgn1=8):** FRM0 Y20-64 cells are flagged `u` in D2. Values
are present and used. The `denom_flag = 'u_u'` flag on all 6 drgn1=8 rows
indicates both the D2 population and the UR source carry the `u` flag.
This affects the Corse component of drgn1=8; the other two components
(FRJ1 Languedoc-Roussillon, FRL0 PACA) are clean. The weighted aggregation
uses all three components; the Corse contribution is small given its
population weight relative to FRL0 and FRJ1.

**FRI2 note (drgn1=6):** FRI2 (Limousin) appears in drgn1=6 (Sud-Ouest)
alongside FRI1 (Aquitaine) and FRJ2 (Midi-Pyrénées). Some FRI2 Y20-64
cells carry `u` flag in the UR source. These are used with D2; flagged.

---

## 6. Percent-to-proportion conversion check (L2)

All unemployment rate values from `FR_gsur.xlsx` are in percentage units
(e.g., 16.4 for 16.4%). The script divides by 100 at point of ingestion.

**Verification:**

- All non-NaN `gsur` values in the output lie in [0.00, 1.00]. **PASS**
- Minimum non-NaN `gsur`: 0.047036 (drgn1=5, educ3=2, M = 4.7%)
- Maximum non-NaN `gsur`: 0.234000 (drgn1=3, educ3=0, M = 23.4%)
- Both values are plausible French regional unemployment rates for 2016

Cross-check: FR (national, TOTAL/T/Y20-64) from Sheet 5 = 9.8%. Our
population-weighted national aggregate (section 11) = 9.82%, consistent.

---

## 7. Unique-key check (L1)

**Key columns:** `(drgn1, educ3, sex)`

- Total rows: 54
- Duplicate rows: 0
- Expected drgn1 range 1–9: all present
- Expected educ3 values {0, 1, 2}: all present for each drgn1
- Expected sex values {M, F}: both present for each (drgn1, educ3)

**Result: PASS**

---

## 8. Missing-value check

- `gsur` NaN for drgn1 ∈ {1..8}: **0** — no missing values. **PASS**
- `gsur` NaN for drgn1 = 9: **6** — expected (O5 DOM stub). **PASS**

No cell in drgn1=1..8 has a missing gsur value. The D2 Y20-64 coverage for
all 22 metro NUTS-2 regions is complete (including the FRM0 flagged-u cells
which have OBS_VALUE present).

---

## 9. Old vs corrected GSUR comparison (L10-diag)

The `gsur_legacy_misaligned` column reconstructs what v1 stored: TOTAL-sex /
TOTAL-educ3 / Y20-64 unweighted mean across drgn1 NUTS-2 components.

| Metric | Value |
|---|---|
| Comparable rows (both non-NaN) | 48 |
| Mean \|gsur − gsur_legacy_misaligned\| | 3.64 ppt |
| Max \|gsur − gsur_legacy_misaligned\| | 8.12 ppt |

**Interpretation:** Large differences are expected and correct. The corrected
`gsur` is sex- and education-stratified; `gsur_legacy_misaligned` is not. The
dominant source of difference is education stratification: low-education (ED0-2)
rates are roughly 2× to 4× higher than high-education (ED5-8) rates within the
same region and sex. The v1 TOTAL/TOTAL value represents an average across
education groups that masks this heterogeneity.

The magnitude of the correction is substantively meaningful and consistent with
the v2 specification's motivation. This is a diagnostic finding, not a failure.

---

## 10. Île-de-France parity check (O8, spec §13 L4)

**Tolerance:** 0.001 absolute (O8 resolution).

drgn1=1 (Île-de-France) is the single unambiguous case: it maps to exactly
one NUTS-2 code (FR10), so the computed `gsur` must equal the FR10 source
workbook value exactly.

| educ3 | sex | source workbook FR10 (%) | computed gsur | diff | pass |
|---|---|---|---|---|---|
| 0 (ED0-2) | F | 15.30% | 0.153000 | 0.000000 | PASS |
| 0 (ED0-2) | M | 16.40% | 0.164000 | 0.000000 | PASS |
| 1 (ED3_4) | F | 10.30% | 0.103000 | 0.000000 | PASS |
| 1 (ED3_4) | M | 11.00% | 0.110000 | 0.000000 | PASS |
| 2 (ED5-8) | F | 5.80% | 0.058000 | 0.000000 | PASS |
| 2 (ED5-8) | M | 5.60% | 0.056000 | 0.000000 | PASS |

**All 6 cells: diff = 0.000000 ≤ tolerance 0.001. PASS.**

Note on legacy comparison: `gsur_legacy_misaligned` for drgn1=1 = 0.091
(9.1%, the FR10 TOTAL/T/Y20-64 value from Sheet 5). The diff between
`gsur` and `gsur_legacy_misaligned` for drgn1=1 ranges from 0.033 to
0.073. This is expected — it shows that v1 correctly used FR10 but did not
stratify by education or sex. The corrected v2 rates are internally consistent
and match the source.

---

## 11. National benchmark comparison (L5, O9)

**Benchmark:** INSEE BDM série 001688526, 2016 annual average = **9.725%**
(proportion: 0.09725). Source: `Data/external/insee_001688526_2016.csv`.
REF_AREA: FM (metropolitan France only — correct perimeter for this sample).

**Tolerance:** ±1.0 ppt (spec §13 L5 recommended tolerance).

**Computation:** Population-weighted aggregate across all 22 metropolitan
NUTS-2 regions, all educ3 × sex cells:

```
national_rate = Σ(ur_nuts2_educ3_sex × pop_nuts2_educ3_sex)
               / Σ pop_nuts2_educ3_sex
```

using D2 population denominators and FR_gsur.xlsx Y20-64 UR values directly
(not from the aggregated lookup).

**Result:**

| Metric | Value |
|---|---|
| Computed national rate | 9.82% |
| INSEE benchmark (O9) | 9.725% |
| Difference | +0.10 ppt |
| Tolerance | ±1.0 ppt |

**PASS** (diff = 0.10 ppt, well within ±1.0 ppt tolerance).

The computed 9.82% also aligns with the FR TOTAL/T/Y20-64 direct value from
Sheet 5 of FR_gsur.xlsx (9.8%), confirming internal consistency.

---

## 12. D1 vs D2 diagnostic comparison (L11-diag, v2.1 §5 D2)

**Purpose:** Document the empirical magnitude of the population-weighting
approximation by comparing the aggregated GSUR rate at Y15-74 under D1
(labour-force) and D2 (population) weighting. Required by v2.1 §5(D2).

**Scope:** Y15-74 is the only age band available in both D1 and D2 for
France metropolitan NUTS-2 at the required educ3 × sex disaggregation.

**Results:**

| Statistic | Value |
|---|---|
| Mean \|D2 − D1\| across all (drgn1, educ3, sex) | 0.027 ppt |
| Max \|D2 − D1\| across all (drgn1, educ3, sex) | 0.327 ppt |

The maximum difference (0.327 ppt at drgn1=4, educ3=0, F) is well below
0.5 ppt. The mean difference (0.027 ppt) is negligible. Population weighting
(D2) is an excellent approximation to labour-force weighting (D1) at the
France NUTS-2 level for 2016.

**Selected row-level comparison:**

| drgn1 | educ3 | sex | D2 rate (Y15-74) | D1 rate (Y15-74) | diff (D2−D1) |
|---|---|---|---|---|---|
| 1 | 0 | M | 16.80% | 16.80% | 0.000 ppt |
| 1 | 0 | F | 15.40% | 15.40% | 0.000 ppt |
| 2 | 0 | M | 17.34% | 17.42% | −0.082 ppt |
| 4 | 0 | F | 19.05% | 18.72% | +0.327 ppt |
| 8 | 0 | M | 17.80% | 17.94% | −0.140 ppt |

drgn1=1 (single-component, FR10): diff = 0.000 for all cells, as expected.

**Conclusion:** The D2 population-weighting approximation introduces at most
0.33 ppt of error relative to D1 labour-force weighting. This is acceptable
under v2.1 §5(D2). The approximation error is documented and does not affect
the Stage A lookup quality.

---

## 13. D3 fallback rows

**D3 rows in Stage A lookup:** 0

No `approximate_uniform` (D3) cells appear in the Stage A (Y20-64) output.
The two D3 cells identified in the O2 resolution memo
(FRM0/F/Y25-34/ED0-2 and FRM0/F/Y15-24/ED5-8) are narrow-band Stage B
cells and do not affect the Y20-64 Stage A band.

The D3 reviewer sign-off requirement per v2.1 §5(D3)(b) applies to Stage B
implementation and is deferred to the Stage B implementation phase.

---

## 14. Final PASS / FAIL for lookup readiness

| Check | Reference | Result |
|---|---|---|
| L1 — Unique keys | spec §13.1 | **PASS** — 0 duplicates, 54 rows |
| L2 — Proportion units | spec §13.1 | **PASS** — all values in [0, 1] |
| L3 — drgn1 support | spec §13.1 | **PASS** — drgn1 1–9 all present |
| L4 — IDF crosswalk sanity (source comparison) | spec §13.1 | **PASS** — diff = 0.000 all cells |
| L5 — National benchmark (O9) | spec §13.1 | **PASS** — 9.82% vs 9.725%, diff = 0.10 ppt |
| L7 — Weighting-source documentation | spec §13.1 | **PASS** — all rows flagged `population` |
| L8 — Approximation flags | spec §13.1 | **PASS** — 0 D3 rows in Stage A |
| Missing-value check | spec §13.1 | **PASS** — 0 NaN for drgn1=1..8 |
| IDF parity check (source workbook) | O8 / spec §14 M4 | **PASS** — 0.000 absolute diff |
| L10-diag — Old vs corrected comparison | spec §13.2 | DIAGNOSTIC — mean 3.64 ppt, expected |
| L11-diag — D1 vs D2 diagnostic | spec §13.2 | DIAGNOSTIC — max 0.327 ppt, acceptable |
| L13 — D3 fallback rows | O2 resolution | NONE — 0 D3 rows in Stage A |

**Overall verdict: LOOKUP READY — all pass/fail checks passed.**

The lookup file `Data/external/FR_gsur_ruro_v2_stageA.parquet` is ready for
the MNL merge step, subject to O7 crosswalk sign-off before any write to
versioned GSURv2 MNL parquet paths.

---

## Sources cited

| Source | File | Date accessed |
|---|---|---|
| Eurostat `lfst_r_lfu3rt` (unemployment rates by NUTS-2 × sex × education × age) | `Data/external/FR_gsur.xlsx` | 2025-12-04 (workbook extraction date) |
| Eurostat `NUTS2013-NUTS2016.xlsx` (NUTS renaming correspondence) | `Data/external/NUTS2013-NUTS2016.xlsx` | 2026-05-17 |
| Eurostat `lfst_r_lfsd2pop` (population in private households, D2 operational) | `Data/external/lfst_r_lfsd2pop_FR_2016.tsv` | 2026-05-17; URL: `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/lfst_r_lfsd2pop?format=SDMX-CSV&startPeriod=2016&endPeriod=2016` |
| Eurostat `lfst_r_lfp2acedu` (labour force, D1 diagnostic) | `Data/external/lfst_r_lfp2acedu_FR_2016.tsv` | 2026-05-17; URL: `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/lfst_r_lfp2acedu?format=SDMX-CSV&startPeriod=2016&endPeriod=2016` |
| INSEE BDM série 001688526 (ILO unemployment rate, Metropolitan France, SA) | `Data/external/insee_001688526_2016.csv` | 2026-05-17; URL: `https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688526` |
| EUROMOD FR 2016 DRD (`DRD_FR_2016_a3_export.txt`) | `docs/France_case/euromod_reference/DRD_FR_2016_a3_export.txt` | In-repository |