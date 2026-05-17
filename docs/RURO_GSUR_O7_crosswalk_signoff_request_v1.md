# RURO GSUR O7 Crosswalk Sign-off Request v1

Date: 2026-05-17

Reference documents:
- `docs/RURO_GSUR_StageA_authorization_v1.md`
- `docs/RURO_GSUR_rebuild_specification_v2_1.md` §7 (O7)
- `docs/RURO_GSUR_v2_stageA_implementation_report_v1.md`
- `Results/RURO_GSUR_v2_stageA_lookup_validation_report_v1.md`

---

## 1. Purpose

This document requests the O7 crosswalk sign-off required before any write
to the versioned GSURv2 MNL parquet paths. Per the governing specification
`docs/RURO_GSUR_rebuild_specification_v2_1.md` §17(O7) and the open-decisions
resolution memo `docs/RURO_GSUR_v2_1_open_decisions_resolution_v1.md`:

> Once the O1 crosswalk is constructed, the `drgn1`-to-NUTS2 crosswalk
> and the GSUR age-education join key must be reviewed and approved by
> the user before merging into the MNL parquets — that is, before any
> output parquet is written to versioned (`_GSURv2`) paths. The sign-off
> must be recorded as an explicit user approval message referencing the
> crosswalk file and the merge key used.

This request presents all material the user needs to give that approval.
The exact approval text to copy is in §13.

---

## 2. Stage A lookup validation status

The Stage A GSUR lookup validation passed all nine pass/fail checks.

| Check | Result |
|---|---|
| L1 — Unique keys | PASS |
| L2 — Proportion units (all values in [0, 1]) | PASS |
| L3 — drgn1 support (1–9 present) | PASS |
| L4 — Île-de-France source sanity (diff = 0.000) | PASS |
| L5 — National benchmark (9.82% vs 9.725%, Δ = 0.10 ppt) | PASS |
| L7 — Weighting-source documentation | PASS |
| L8 — Approximation flags (0 D3 rows in Stage A) | PASS |
| Missing-value check (0 NaN for drgn1=1..8) | PASS |
| IDF parity check (O8, tolerance 0.001) | PASS |

The correct readiness phrase for this lookup is:

**"Stage A broad-age lookup ready."**

The lookup is ready for the Stage A MNL merge (subject to this O7 sign-off).
It is not ready for Stage B age-specific GSUR work, which remains deferred to
the post-Stage-A review per O6.

---

## 3. Scope limitation: Stage A broad-age lookup only

`Data/external/FR_gsur_ruro_v2_stageA.parquet` is a Stage A broad-age
lookup. It is **not** the final full v2 lookup.

What this file contains:
- One row per `(drgn1, educ3, sex)` for drgn1 ∈ {1..9}
- `gsur`: corrected broad-age unemployment rate at Y20-64 (proportion units)
- `weighting_source`: `'population'` for all rows (D2 operational denominator)
- `gsur_age_band_used`: `'Y20-64'` for drgn1=1..8; DOM stub label for drgn1=9
- `gsur_legacy_misaligned`: reconstructed v1 comparison value (see §8)

What this file does not contain:
- Age-specific GSUR (`gsur_age`): not computed; Stage B only
- Narrow age-band columns (`gsur_y15_24`, `gsur_y25_34`, etc.): not computed; Stage B only
- D3 (approximate_uniform) cells: none in Stage A; the two D3 cells
  (FRM0/F/Y25-34/ED0-2 and FRM0/F/Y15-24/ED5-8) are narrow-band Stage B
  cells and are not present in this file

The full v2 lookup (including Stage B age-specific bands and D3 fallback
cells) will be built separately after the Stage A verdict and O6 resolution.
This sign-off authorises the merge of the Stage A file only.

---

## 4. Approved crosswalk candidate

**File:** `Data/external/fr_drgn1_to_nuts2_crosswalk.csv`

| drgn1 | Label | old NUTS-2 | new NUTS-2 (2016) | n |
|---|---|---|---|---|
| 1 | Île-de-France | FR10 | FR10 | 1 |
| 2 | Bassin Parisien | FR21, FR22, FR23, FR24, FR25, FR26 | FRF2, FRE2, FRD2, FRB0, FRD1, FRC1 | 6 |
| 3 | Nord-Pas-de-Calais | FR30 | FRE1 | 1 |
| 4 | Est | FR41, FR42, FR43 | FRF3, FRF1, FRC2 | 3 |
| 5 | Ouest | FR51, FR52, FR53 | FRG0, FRH0, FRI3 | 3 |
| 6 | Sud-Ouest | FR61, FR62, FR63 | FRI1, FRJ2, FRI2 | 3 |
| 7 | Rhône-Alpes / Auvergne | FR71, FR72 | FRK2, FRK1 | 2 |
| 8 | Méditerranée | FR81, FR82, FR83 | FRJ1, FRL0, FRM0 | 3 |
| 9 | DOM stub (O5) | FR91–94 | — | 0 |

Verification status: all 22 rows carry `verified_against_eurostat = YES`.

Provenance chain (three steps, all documented):
1. `drgn1` groupings → `drgn2` values: EUROMOD France 2016 DRD
   (`docs/euromod_reference/DRD_FR_2016_a3_export.txt`)
2. `drgn2` → old NUTS-2 (FR10–FR83): same DRD
3. Old NUTS-2 → new NUTS-2 (NUTS 2016 codes): verified against
   `Data/external/NUTS2013-NUTS2016.xlsx` (Eurostat, downloaded 2026-05-17,
   sheet "Correspondence NUTS-2")

FR10 (Île-de-France) is unchanged under the NUTS 2016 reform and is absent
from the correspondence sheet by design. Its mapping (FR10 → FR10) is
confirmed explicitly. The Île-de-France parity check in the lookup validation
verified this: computed gsur = source workbook FR10 value to 0.000000
absolute difference for all 6 educ3 × sex cells.

---

## 5. Crosswalk file

```
Data/external/fr_drgn1_to_nuts2_crosswalk.csv
```

Schema: `drgn1, old_nuts2_code, region_name, new_nuts2_code_2016, verified_against_eurostat`

Rows: 22 (one per metropolitan France pre-2016 NUTS-2 region).
All rows: `verified_against_eurostat = YES`.

This file is the load-bearing data asset for the merge. It determines which
Eurostat NUTS-2 unemployment rates are aggregated into each EUROMOD drgn1
region. It was constructed via the three-step provenance chain described in §4
and is the crosswalk that O7 requires sign-off on before use in MNL parquets.

---

## 6. Merge key

The approved merge key for joining the Stage A lookup to the MNL parquets is:

```
(drgn1, educ3, sex)
```

The Stage A parquet is already aggregated to drgn1 level (one row per
drgn1 × educ3 × sex). The MNL parquet merge does not require individual
NUTS-2 lookups at merge time; those were resolved at lookup-build time.

The merge procedure for each MNL individual is:

1. Read the individual's `drgn1`, `educ3`, and `sex` from the MNL parquet.
2. Look up the matching row in `FR_gsur_ruro_v2_stageA.parquet` on
   `(drgn1, educ3, sex)`.
3. Assign the `gsur` value (and ancillary columns) to the individual row.
4. For rows with `dag == 65`, overwrite `gsur_age_band_used` with
   `"Y20-64_fallback_age65"` per O3.
5. For rows with `drgn1 == 9`, all GSUR columns remain NaN per O5.

For couples parquets, the merge is applied twice: once for the male partner
using `(drgn1, educ3_male, 'M')` and once for the female partner using
`(drgn1, educ3_female, 'F')`.

The merge key does not require NUTS-2 codes in the MNL parquet. The
crosswalk is used at lookup-build time (already done); the merge itself
operates on the pre-aggregated drgn1-level lookup.

---

## 7. Lookup file to merge

```
Data/external/FR_gsur_ruro_v2_stageA.parquet
```

Rows: 54 (48 active for drgn1=1..8, 6 NaN stubs for drgn1=9)
Key columns: `drgn1`, `educ3`, `sex`
Value column to merge: `gsur` (and ancillary: `weighting_source`,
`gsur_age_band_used`, `gsur_legacy_misaligned`, `denom_flag`,
`gsur_unreliable`)

All 9 pass/fail validation checks passed (§2 above). The file is ready for
the Stage A MNL merge subject to this O7 sign-off.

---

## 8. Legacy GSUR variable note

The `gsur_legacy_misaligned` column in the lookup is a **reconstructed**
legacy comparison variable. It was computed by the build script as the
unweighted mean of the TOTAL-sex / TOTAL-educ3 / Y20-64 values from
`FR_gsur.xlsx` Sheet 5 across the NUTS-2 components of each drgn1 group.

This is not loaded from the actual v1 MNL parquet `gsur` column. It is
an approximation of what v1 stored, constructed for forensic comparison
purposes. The correct forensic record of v1 values will be read directly
from the canonical v1 parquets at MNL merge time and written to
`gsur_legacy_misaligned` from the actual v1 parquet column — overwriting
the reconstructed values in this lookup. The merge script must read the
existing `gsur` column from the canonical parquet and rename it to
`gsur_legacy_misaligned` before writing the new `gsur` from the Stage A
lookup.

If the actual v1 parquet `gsur` column is not available at merge time, the
reconstructed value in the lookup may be used as a fallback, but this must
be flagged in the MNL rebuild validation report.

---

## 9. Expected MNL columns to be added or replaced

After the Stage A MNL merge, the versioned GSURv2 parquets will contain the
following GSUR-related columns, per spec §8.1 (singles) and §8.2 (couples):

**Singles parquet — columns added or replaced:**

| Column | Action | Source |
|---|---|---|
| `gsur` | **replace** existing v1 `gsur` | Stage A lookup `gsur` column |
| `gsur_legacy_misaligned` | **add new** | v1 canonical parquet's `gsur` column (read before overwrite) |
| `gsur_age_band_used` | **add new** | Stage A lookup `gsur_age_band_used`; O3 override for dag=65 |
| `gsur_weighting_source` | **add new** | Stage A lookup `weighting_source` |

The age-specific columns (`gsur_age`, `gsur_y15_24`, `gsur_y25_34`,
`gsur_y35_44`, `gsur_y45_54`, `gsur_y55_64`) are Stage B columns and are
**not** added in the Stage A merge.

**Couples parquet:** all of the above with `_male` and `_female` suffixes,
looked up independently per partner using `(drgn1, educ3_male/female, 'M'/'F')`.

All non-GSUR columns are value-identical to the v1 canonical parquets under
schema-aligned comparison (spec §14 M1). The MNL rebuild validation (§14
checks M1–M10) must confirm this before Stage A re-estimation may proceed.

---

## 10. Versioned output parquets that would be written after approval

After O7 sign-off is granted, the merge step is authorized to write exactly
these two files:

```
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2__singles.parquet
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2__couples.parquet
```

These are the versioned GSURv2 paths defined in spec §12(F6). They are
distinct from the canonical paths and do not overwrite them.

The canonical paths remain untouched at v1 content:
```
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet
```

Canonical promotion is a separate step requiring SA-STANDS or SA-REVISION
verdict and a separate explicit user approval per O10. It is not part of
this sign-off.

---

## 11. What approval authorizes

Granting O7 sign-off authorizes exactly the following:

1. **Writing** `fr_2016_RURO_mnl_GSURv2__singles.parquet` to the versioned
   path `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/`.
2. **Writing** `fr_2016_RURO_mnl_GSURv2__couples.parquet` to the same
   versioned path.
3. **Using** `Data/external/fr_drgn1_to_nuts2_crosswalk.csv` as the
   authoritative drgn1→NUTS2 mapping for the Stage A MNL merge.
4. **Using** `Data/external/FR_gsur_ruro_v2_stageA.parquet` with merge key
   `(drgn1, educ3, sex)` as the source of corrected `gsur` values.
5. **Running** the MNL rebuild validation (spec §14 checks M1–M10) on the
   versioned parquets after they are written.

---

## 12. What approval does not authorize

This O7 sign-off does not authorize:

1. **Overwriting canonical MNL parquets.** The canonical paths
   (`fr_2016_RURO_mnl__singles.parquet`, `fr_2016_RURO_mnl__couples.parquet`)
   must not be touched. Canonical promotion requires a separate approval after
   the Stage A verdict per O10.

2. **Stage A re-estimation.** Estimation against the versioned GSURv2 parquets
   is not authorized by this sign-off. Estimation requires the MNL rebuild
   validation (spec §14 M1–M10) to pass first.

3. **Age-specific GSUR Stage B.** The narrow age-band columns (`gsur_age`,
   `gsur_y*`) are not part of the Stage A merge. Stage B is deferred to
   post-Stage-A review per O6.

4. **Welfare computation.** Not authorized at any point in Stage A.

5. **Using the Stage A lookup as the final full v2 lookup.** This lookup
   covers Y20-64 broad-age only. Stage B will require a separate lookup build
   after O6 is resolved.

6. **Applying the D3 reviewer sign-off.** The two D3 cells
   (FRM0/F/Y25-34/ED0-2 and FRM0/F/Y15-24/ED5-8) are Stage B cells; their
   sign-off is deferred and is not part of this O7 sign-off.

---

## 13. Exact approval text for the user to copy

To grant O7 crosswalk sign-off, copy and send the following text verbatim
as a reply message. Do not paraphrase or abbreviate it; the sign-off must
reference the specific files and merge key to be recorded.

---

I approve O7 crosswalk sign-off for Stage A versioned GSURv2 MNL rebuild.

The approved crosswalk is:
Data/external/fr_drgn1_to_nuts2_crosswalk.csv

The approved lookup file is:
Data/external/FR_gsur_ruro_v2_stageA.parquet

The approved merge key is:
(drgn1, educ3, sex)

This approval is only for writing versioned GSURv2 MNL parquets.
It does not authorize overwriting canonical MNL files.
It does not authorize estimation until the MNL rebuild validation passes.
It does not authorize age-specific GSUR Stage B.
It does not authorize welfare computation.
