# RURO GSUR v2 Stage A — Implementation Report v1

Date: 2026-05-17
Script: `scripts/enhanced/enh_prepare_FR_gsur_v2.py`
Output: `Data/external/FR_gsur_ruro_v2_stageA.parquet`
Authorization: `docs/RURO_GSUR_StageA_authorization_v1.md`

---

## 1. Scope

This report documents the Stage A GSUR lookup build as defined in
`docs/RURO_GSUR_rebuild_specification_v2_1.md` §9 and authorized by
`docs/RURO_GSUR_StageA_authorization_v1.md` (2026-05-17).

Stage A scope: corrected broad-age `gsur` using Y20-64, one row per
`(drgn1, educ3, sex)` combination, D2 population denominators (operational),
no MNL parquet writes, no estimation, no canonical-path modification.

---

## 2. Inputs used

| File | Role | Rows / Notes |
|---|---|---|
| `Data/external/FR_gsur.xlsx` | Unemployment rates (lfst_r_lfu3rt) | 120 sheets; dataset `lfst_r_lfu3rt__custom_19204794` |
| `Data/external/fr_drgn1_to_nuts2_crosswalk.csv` | drgn1→NUTS2 mapping (O1) | 22 rows; all `verified_against_eurostat=YES` |
| `Data/external/lfst_r_lfsd2pop_FR_2016.tsv` | D2 population denominators (O2 operational) | 4,057 rows |
| `Data/external/lfst_r_lfp2acedu_FR_2016.tsv` | D1 labour-force denominators (O2 diagnostic only) | 986 rows |
| `Data/external/insee_001688526_2016.csv` | National benchmark (O9) | 9.725% annual average |
| `Data/external/NUTS2013-NUTS2016.xlsx` | NUTS renaming reference (O1 provenance) | Referenced via crosswalk |

---

## 3. Key design decisions implemented

### O1 — Crosswalk

The `drgn1`-to-NUTS2 crosswalk (`fr_drgn1_to_nuts2_crosswalk.csv`) maps
each of the 22 metropolitan France pre-2016 NUTS-2 codes to the post-2016
NUTS-2 codes verified against Eurostat `NUTS2013-NUTS2016.xlsx`. All 22
rows carry `verified_against_eurostat = YES`.

drgn1 compositions (number of NUTS-2 components):

| drgn1 | Label | n components |
|---|---|---|
| 1 | Île-de-France | 1 (FR10) |
| 2 | Bassin Parisien | 6 (FRF2, FRE2, FRD2, FRB0, FRD1, FRC1) |
| 3 | Nord-Pas-de-Calais | 1 (FRE1) |
| 4 | Est | 3 (FRF3, FRF1, FRC2) |
| 5 | Ouest | 3 (FRG0, FRH0, FRI3) |
| 6 | Sud-Ouest | 3 (FRI1, FRJ2, FRI2) |
| 7 | Rhône-Alpes / Auvergne | 2 (FRK2, FRK1) |
| 8 | Méditerranée | 3 (FRJ1, FRL0, FRM0) |
| 9 | DOM stub (O5) | 0 — NaN placeholder |

### O2 — Denominator

D2 (`lfst_r_lfsd2pop`, population in private households) is the operational
denominator for Stage A (Y20-64). D1 (`lfst_r_lfp2acedu`) does not publish
Y20-64 for any EU country and cannot serve as denominator. D1 is used only
as a diagnostic comparison at Y15-74 per v2.1 §5(D2).

For each (drgn1, educ3, sex) cell, the rate is computed as the
population-weighted mean of the contributing NUTS-2 unemployment rates:

```
gsur(drgn1, educ3, sex) = Σ [ur(nuts2, educ3, sex) × pop(nuts2, educ3, sex)]
                           / Σ pop(nuts2, educ3, sex)
```

where the sum runs over the NUTS-2 components of the drgn1 group.

**O2 fallback cells at Y20-64 (Stage A):**

FRM0 (Corse) Y20-64: all 6 sex × ISCED cells are flagged `u` (unreliable)
in `lfst_r_lfsd2pop` but carry OBS_VALUE. Used with `weighting_source =
'population'`; flagged in `denom_flag` as `u_u` (UR source also flagged).
Noted in the validation report.

FRI2 (Limousin): present in drgn1=6 (Sud-Ouest). For Y20-64 at least one
cell is flagged `u`; OBS_VALUE present. Used with D2; flagged.

The two D3 cells (FRM0/F/Y25-34/ED0-2 and FRM0/F/Y15-24/ED5-8) are
**narrow-band Stage B cells only** and do not affect Stage A (Y20-64).
No D3 cells appear in the Stage A lookup.

### O3 — Age-65 handling

The lookup provides `gsur_age_band_used = "Y20-64"` for all drgn1=1..8
rows. When the MNL parquets are merged (pending O7 sign-off), rows with
`dag == 65` are assigned `gsur_age_band_used = "Y20-64_fallback_age65"`
at merge time. This flag is documented in the merge spec; the lookup itself
does not embed per-age rows.

### O4 — Education alignment

educ3 ∈ {0, 1, 2} maps to ISCED codes:

| educ3 | ISCED code | ISCED label |
|---|---|---|
| 0 | ED0-2 | Less than primary, primary, lower secondary (levels 0–2) |
| 1 | ED3_4 | Upper secondary and post-secondary non-tertiary (levels 3–4) |
| 2 | ED5-8 | Tertiary (levels 5–8) |

The join key for the MNL merge is `(drgn1, educ3, sex)`. The Stage A lookup
parquet is already aggregated to drgn1 level; the crosswalk was consumed
during lookup construction and is not re-applied at merge time. No NUTS-2
codes are required in the MNL parquet at merge time.
This mapping is already applied in the upstream MNL parquets (O4 confirmed).

Note: an earlier draft of this report incorrectly stated the merge key as
`(new_nuts2_code_2016, sex, educ3)`. That has been corrected here. The
authoritative merge key is `(drgn1, educ3, sex)` as confirmed in
`docs/RURO_GSUR_O7_crosswalk_signoff_request_v1.md` §6.

### O5 — drgn1 = 9 stub

Six rows for drgn1=9 are present in the output with `gsur = NaN` and
`gsur_age_band_used = "Y20-64_fallback_dom_absent"`. No France 2016
metropolitan sample respondents carry drgn1=9. The schema slot is retained
for portability.

### O7 — Crosswalk sign-off (pending)

The O7 crosswalk sign-off has not been obtained. The lookup parquet has been
written to the authorized intermediate path (`Data/external/`). No MNL
parquet has been written. The merge step that produces
`fr_2016_RURO_mnl_GSURv2__singles.parquet` and
`fr_2016_RURO_mnl_GSURv2__couples.parquet` is blocked until explicit user
approval referencing `fr_drgn1_to_nuts2_crosswalk.csv` and the merge key is
recorded.

---

## 4. Output schema

File: `Data/external/FR_gsur_ruro_v2_stageA.parquet`
Rows: 54 (48 active drgn1=1..8 + 6 drgn1=9 stubs)
Columns: 11

| Column | Type | Description |
|---|---|---|
| `year` | int64 | Reference year (2016) |
| `drgn1` | int64 | EUROMOD region code (1–9) |
| `educ3` | int64 | Education group (0=low, 1=med, 2=high) |
| `sex` | object | Sex (M/F) |
| `gsur` | float64 | Corrected broad-age GSUR (proportion, Y20-64) |
| `weighting_source` | object | Denominator type: `population` (all Stage A rows) |
| `gsur_age_band_used` | object | Age band used: `Y20-64` (or fallback label for drgn1=9) |
| `gsur_legacy_misaligned` | float64 | Reconstructed v1 GSUR (TOTAL/T/Y20-64 unweighted mean) |
| `denom_flag` | object | Suppression/reliability flag for contributing D2 cells |
| `n_components` | int64 | Number of NUTS-2 components in the drgn1 group |
| `gsur_unreliable` | bool | True if any contributing cell carried OBS_FLAG=u |

---

## 5. Selected lookup values (all 48 active rows)

| drgn1 | educ3 | sex | gsur | weighting_source | denom_flag | gsur_unreliable |
|---|---|---|---|---|---|---|
| 1 | 0 | F | 0.153000 | population | | False |
| 1 | 0 | M | 0.164000 | population | | False |
| 1 | 1 | F | 0.103000 | population | | False |
| 1 | 1 | M | 0.110000 | population | | False |
| 1 | 2 | F | 0.058000 | population | | False |
| 1 | 2 | M | 0.056000 | population | | False |
| 2 | 0 | F | 0.148696 | population | u | True |
| 2 | 0 | M | 0.168041 | population | u | True |
| 2 | 1 | F | 0.110746 | population | | False |
| 2 | 1 | M | 0.101143 | population | | False |
| 2 | 2 | F | 0.056077 | population | u | True |
| 2 | 2 | M | 0.056530 | population | u | True |
| 3 | 0 | F | 0.230000 | population | | False |
| 3 | 0 | M | 0.234000 | population | | False |
| 3 | 1 | F | 0.133000 | population | | False |
| 3 | 1 | M | 0.135000 | population | | False |
| 3 | 2 | F | 0.070000 | population | | False |
| 3 | 2 | M | 0.067000 | population | | False |
| 4 | 0 | F | 0.182887 | population | u | True |
| 4 | 0 | M | 0.198251 | population | u | True |
| 4 | 1 | F | 0.089803 | population | u | True |
| 4 | 1 | M | 0.116210 | population | | False |
| 4 | 2 | F | 0.062167 | population | u | True |
| 4 | 2 | M | 0.055147 | population | u | True |
| 5 | 0 | F | 0.163606 | population | u | True |
| 5 | 0 | M | 0.184225 | population | | False |
| 5 | 1 | F | 0.090638 | population | | False |
| 5 | 1 | M | 0.076066 | population | | False |
| 5 | 2 | F | 0.057353 | population | u | True |
| 5 | 2 | M | 0.047036 | population | u | True |
| 6 | 0 | F | 0.164661 | population | u | True |
| 6 | 0 | M | 0.160378 | population | u | True |
| 6 | 1 | F | 0.089144 | population | u | True |
| 6 | 1 | M | 0.086287 | population | u | True |
| 6 | 2 | F | 0.061818 | population | u | True |
| 6 | 2 | M | 0.060187 | population | u | True |
| 7 | 0 | F | 0.139336 | population | u | True |
| 7 | 0 | M | 0.150738 | population | u | True |
| 7 | 1 | F | 0.081668 | population | u | True |
| 7 | 1 | M | 0.068956 | population | u | True |
| 7 | 2 | F | 0.047759 | population | u | True |
| 7 | 2 | M | 0.051752 | population | u | True |
| 8 | 0 | F | 0.157024 | population | u_u | True |
| 8 | 0 | M | 0.171326 | population | u_u | True |
| 8 | 1 | F | 0.128038 | population | u_u | True |
| 8 | 1 | M | 0.113038 | population | u_u | True |
| 8 | 2 | F | 0.062628 | population | u_u | True |
| 8 | 2 | M | 0.061042 | population | u_u | True |

drgn1=9 rows: all gsur = NaN, weighting_source = population,
gsur_age_band_used = Y20-64_fallback_dom_absent.

---

## 6. Legacy vs corrected comparison (gsur_legacy_misaligned)

The `gsur_legacy_misaligned` column is a reconstruction of what v1 stored:
TOTAL-sex / TOTAL-educ3 / Y20-64 unweighted mean across NUTS-2 components of
the drgn1 group. It is not education- or sex-stratified.

The corrected `gsur` is education- and sex-stratified. Large differences
between `gsur` and `gsur_legacy_misaligned` are expected because:

1. v1 used no education stratification (collapsed to TOTAL).
2. v1 used an incorrect v1 crosswalk with misaligned region codes.
3. The corrected gsur uses the proper NUTS-2 post-2016 codes.

The IDF parity check (spec §13 L4, §14 M4) confirms that drgn1=1 (Île-de-
France, single-component group FR10) matches the FR10 source workbook values
exactly (diff = 0.000000 for all 6 educ3 × sex cells). The large numeric
difference between `gsur` and `gsur_legacy_misaligned` for drgn1=1 is a
consequence of v1 not stratifying by education, not a computation error.

---

## 7. What this script does NOT do

Per authorization memo §8 and task restrictions:

- Does NOT write `fr_2016_RURO_mnl_GSURv2__singles.parquet`
- Does NOT write `fr_2016_RURO_mnl_GSURv2__couples.parquet`
- Does NOT write to any canonical MNL parquet path
- Does NOT estimate any RURO model
- Does NOT activate age-specific `gsur_age` (Stage B)
- Does NOT run welfare computation

---

## 8. O7 crosswalk sign-off — pending action

Before the MNL merge step can proceed, the following must be obtained as
an explicit user approval message:

**Crosswalk reviewed:** `Data/external/fr_drgn1_to_nuts2_crosswalk.csv`

**Merge key to be used:**
```
(drgn1, educ3, sex)
```

The Stage A lookup parquet is already aggregated to drgn1 level. The
crosswalk (`fr_drgn1_to_nuts2_crosswalk.csv`) was consumed during lookup
construction; it is not re-applied at merge time. The merge procedure is:

1. For each MNL individual, read `drgn1`, `educ3`, and `sex`.
2. Join to `FR_gsur_ruro_v2_stageA.parquet` on `(drgn1, educ3, sex)`.
3. Assign `gsur` (and ancillary columns) to the individual row.
4. For `dag == 65`, overwrite `gsur_age_band_used` with
   `"Y20-64_fallback_age65"` (O3).
5. For `drgn1 == 9`, all GSUR columns remain NaN (O5).

For couples, apply the join twice: `(drgn1, educ3_male, 'M')` for the male
partner and `(drgn1, educ3_female, 'F')` for the female partner.

**`gsur_legacy_misaligned` at merge time:**
Before writing the new `gsur` to the versioned parquets, the merge script
must read the existing `gsur` column from the canonical v1 parquet and
write it to `gsur_legacy_misaligned`. The `gsur_legacy_misaligned` column
currently present in the lookup parquet is a reconstruction (TOTAL-sex /
TOTAL-educ3 unweighted mean from FR_gsur.xlsx Sheet 5) and is not the
actual v1 parquet value. The merge script overwrites it with the true v1
value read from the canonical path. If the v1 parquet `gsur` column is
unavailable at merge time, the reconstructed value may be used as a fallback
and must be flagged in the MNL rebuild validation report.

This merge procedure supersedes the earlier incorrect description in this
section. The authoritative merge specification is
`docs/RURO_GSUR_O7_crosswalk_signoff_request_v1.md` §6 and §8.

The sign-off message must reference `fr_drgn1_to_nuts2_crosswalk.csv` and
this merge key explicitly.

---

## 9. Next steps (implementation sequence)

1. **O7 sign-off** — obtain explicit user approval message for crosswalk and
   merge key before any MNL parquet write.
2. **Modify `enh_RURO_prep_mnl_basic.py`** — add GSUR v2 merge logic per
   v2.1 §12(F5), writing versioned GSURv2 parquets per §12(F6).
3. **MNL rebuild validation** — run v2.1 §14 checks (M1–M10) on versioned
   parquets.
4. **Stage A re-estimation** — run M0c_b2 against versioned GSURv2 parquets
   per v2.1 §15(R1).
5. **Stage A verdict** — apply decision rule §9.3 (SA-STANDS / SA-REVISION /
   SA-OVERTURNED).
6. **Canonical promotion (conditional)** — only after SA-STANDS or
   SA-REVISION verdict and explicit user approval per O10.