# RURO GSUR — Local O1 Evidence Audit v1

Date: 2026-05-17

Reference documents:
- `docs/France_case/RURO_GSUR_rebuild_specification_v2_1.md`
- `docs/RURO_GSUR_v2_1_open_decisions_resolution_v1.md`
- `docs/RURO_GSUR_external_acquisition_verification_claude_v1.md`

---

## 1. Files inspected

| File | Location | Status |
|------|----------|--------|
| `fr_2016.parquet` | `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/` | Read, 10,873 rows |
| `fr_2016_RURO_mnl__singles.parquet` | same | Read, 167,600 rows / 1,676 hh |
| `fr_2016_RURO_mnl__couples.parquet` | same | Read, 257,700 rows / 2,577 hh |
| `DRD_FR_2016_a3_export.txt` | `docs/France_case/euromod_reference/` | Read |
| `FR_gsur.xlsx` | `Data/external/` | Read — 120 data sheets + Summary + Structure |
| `FR_gsur_full.csv` | `Data/external/` | Read — 90,720 rows |
| `FR_gsur_ruro.csv` | `Data/external/` | Read — 2,160 rows |
| `FR_gsur_simple.parquet` | `Data/external/` | Read — 9,720 rows |
| `FR_gsur_ruro.parquet` | `Data/external/` | Inspected — same schema and drgn1 values as ruro CSV; gsur values differ from CSV by float precision only |

---

## 2. EUROMOD drgn1 definition in local documentation

The DRD (`DRD_FR_2016_a3_export.txt`) documents the derivation explicitly:

```
drgn1 = 1 if drgn2 == 1
drgn1 = 2 if drgn2 in {2,3,4,5,6,7}
drgn1 = 3 if drgn2 == 8
drgn1 = 4 if drgn2 in {9,10,11}
drgn1 = 5 if drgn2 in {12,13,14}
drgn1 = 6 if drgn2 in {15,16,17}
drgn1 = 7 if drgn2 in {18,19}
drgn1 = 8 if drgn2 in {20,21,22}
drgn1 = 9 if drgn2 in {23,24,25,26}
drgn1 = 10 if drgn2 == 27
```

`drgn2` in turn maps `DB040` (the EU-SILC regional variable) to integer codes 1–27,
where 1–22 are metropolitan France, 23–26 are the four DOM (FR91–FR94), and 27 is
`FRZZ` (unknown/missing, recoded to 1).

The full `drgn2`-to-NUTS2 correspondence extracted from the DRD:

| drgn2 | NUTS-2 code | Region name |
|-------|-------------|-------------|
| 1 | FR10 | Île-de-France |
| 2 | FR21 | Champagne-Ardenne |
| 3 | FR22 | Picardie |
| 4 | FR23 | Haute-Normandie |
| 5 | FR24 | Centre |
| 6 | FR25 | Basse-Normandie |
| 7 | FR26 | Bourgogne |
| 8 | FR30 | Nord-Pas-de-Calais |
| 9 | FR41 | Lorraine |
| 10 | FR42 | Alsace |
| 11 | FR43 | Franche-Comté |
| 12 | FR51 | Pays de la Loire |
| 13 | FR52 | Bretagne |
| 14 | FR53 | Poitou-Charentes |
| 15 | FR61 | Aquitaine |
| 16 | FR62 | Midi-Pyrénées |
| 17 | FR63 | Limousin |
| 18 | FR71 | Rhône-Alpes |
| 19 | FR72 | Auvergne |
| 20 | FR81 | Languedoc-Roussillon |
| 21 | FR82 | Provence-Alpes-Côte d'Azur |
| 22 | FR83 | Corse |
| 23 | FR91 | Guadeloupe (DOM) |
| 24 | FR92 | Martinique (DOM) |
| 25 | FR93 | Guyane (DOM) |
| 26 | FR94 | Réunion (DOM) |
| 27 | FRZZ | Unknown (recoded to drgn2=1, drgn1=1) |

These are the **22 former metropolitan régions** (NUTS 2013) plus DOM. The coding is
the pre-2016 NUTS-2 vintage. EUROMOD `drgn1` therefore groups these 22 old régions
into 8 composite categories plus a DOM category (9) and a residual (10). The local
data dictionary fully documents this chain; no external EUROMOD codebook is needed
to establish it.

---

## 3. drgn1 support in France 2016 raw/input data

`fr_2016.parquet` contains both `drgn1` and `drgn2`. Observed value counts by
household (10,873 total rows; each row is one individual but `drgn1/drgn2` are
household-level, so counts below are from `drop_duplicates("idhh")`):

**drgn1 (by household):**

| drgn1 | hh count |
|-------|----------|
| 1 | 654 |
| 2 | 715 |
| 3 | 317 |
| 4 | 372 |
| 5 | 781 |
| 6 | 482 |
| 7 | 502 |
| 8 | 430 |

Categories 9 and 10 observe **0 households**. Maximum observed `drgn1` = 8.

**drgn2 (by household):** Values 1–22 observed (all 22 metropolitan NUTS-2 regions).
Maximum observed `drgn2` = 22. No `drgn2 >= 23` rows (DOM absent).

---

## 4. drgn1 support in current MNL parquets

Both canonical MNL parquets carry `drgn1` as a column. Value counts by household:

**Singles (1,676 hh):**

| drgn1 | hh |
|-------|-----|
| 1 | 271 |
| 2 | 269 |
| 3 | 126 |
| 4 | 145 |
| 5 | 297 |
| 6 | 190 |
| 7 | 197 |
| 8 | 181 |

**Couples (2,577 hh):**

| drgn1 | hh |
|-------|-----|
| 1 | 383 |
| 2 | 446 |
| 3 | 191 |
| 4 | 227 |
| 5 | 484 |
| 6 | 292 |
| 7 | 305 |
| 8 | 249 |

All MNL households fall in categories 1–8. No household carries `drgn1` of 9 or 10
in either parquet. The `drgn1` column is present with non-null integer values for all
rows in both parquets.

---

## 5. Whether drgn1 is 10-category, 8-observed-category, NUTS-1, NUTS-2, or another coding

`drgn1` is a **10-category** variable by construction (categories 1–10 in the DRD
derivation), but **only 8 categories are observed** in the France 2016 metropolitan
analytical sample (categories 1–8). Categories 9 (DOM: FR91–FR94) and 10 (FRZZ
residual) are structurally defined but produce zero observations in the sample.

`drgn1` is **neither NUTS-1 nor NUTS-2**. It is a **custom EUROMOD grouping** of
the 22 old NUTS-2 (pre-2016) French régions, where each `drgn1` category aggregates
between 1 and 6 old NUTS-2 units. Specifically:

| drgn1 | NUTS-2 units included | Number |
|-------|----------------------|--------|
| 1 | FR10 | 1 |
| 2 | FR21, FR22, FR23, FR24, FR25, FR26 | 6 |
| 3 | FR30 | 1 |
| 4 | FR41, FR42, FR43 | 3 |
| 5 | FR51, FR52, FR53 | 3 |
| 6 | FR61, FR62, FR63 | 3 |
| 7 | FR71, FR72 | 2 |
| 8 | FR81, FR82, FR83 | 3 |

Under the 2016 NUTS reform, these old NUTS-2 codes are **renamed** (not
reorganised) to new letter codes: e.g., FR10 stays FR10, FR21 → FRF2, FR30 → FRE1,
FR42 → FRF1, FR81 → FRJ1. The underlying 22-region geography is preserved.

---

## 6. Whether DOM / Mayotte appear in the sample

**No DOM households appear in the France 2016 analytical sample.**

- `fr_2016.parquet`: zero rows with `drgn2 >= 23` (which covers FR91–FR94 = Guadeloupe,
  Martinique, Guyane, Réunion). Maximum observed `drgn2` = 22.
- MNL singles: zero households with `drgn1 >= 9`.
- MNL couples: zero households with `drgn1 >= 9`.

Mayotte (drgn2 not defined in the DRD; INSEE code 06, NUTS FRY5) is absent. The
France 2016 EUROMOD input data is metropolitan France only (drgn2 1–22; drgn1 1–8).

---

## 7. Whether the France 2016 analytical sample is metropolitan France or France hors Mayotte

**Metropolitan France only.** The EUROMOD FR_2016 input and all downstream MNL
parquets contain only the 22 former metropolitan NUTS-2 régions (drgn2 1–22,
drgn1 1–8). No DOM respondents appear. The sample is therefore **France
métropolitaine**, not France hors Mayotte.

Benchmark implication: the correct benchmark source is INSEE BDM metropolitan-France
series `001688526`, but the exact 2016 annual value still has to be extracted and
cited before Stage A validation. The 9.7% figure currently documented in
`docs/RURO_GSUR_external_acquisition_verification_claude_v1.md` is Q4 2016, not
yet the confirmed annual average. The Eurostat `FR` value (10.1%) must not be used
against this metropolitan sample as it covers France hors Mayotte.

---

## 8. GSUR workbook sheets and columns

`FR_gsur.xlsx` contains 122 sheets:
- `Summary`: 134 rows, 7 columns — appears to be a navigation or title sheet; all
  content rows are unlabelled.
- `Structure`: 81 rows — the dimension codelist for the extraction. Key entries:
  - `freq`: Annual [A]
  - `isced11`: TOTAL, ED0-2, ED3_4, ED5-8
  - `sex`: T, M, F
  - `age`: Y15-24, Y15-29, Y15-74, Y_GE15, Y20-64, Y25-34, Y_GE25, Y35-44, Y45-54, Y55-64
  - `unit`: PC (percentage)
  - `geo`: FR, FR1, FR10, FRB, FRB0, FRC, FRC1, FRC2, FRD, FRD1, FRD2, FRE, FRE1,
    FRE2, FRF, FRF1, FRF2, FRF3, FRG, FRG0, FRH, FRH0, FRI, FRI1, FRI2, FRI3,
    FRJ, FRJ1, FRJ2, FRK, FRK1, FRK2, FRL, FRL0, FRM, FRM0, FRY, FRY1, FRY2,
    FRY3, FRY4
- `Sheet 1`–`Sheet 120`: each sheet is a single combination of (isced11 × sex × age),
  with rows = geo codes, columns = years 2007–2024. Dataset identified in each sheet
  header: `lfst_r_lfu3rt__custom_19204794` — Eurostat table
  **"Unemployment rates by educational attainment level and NUTS 2 region"**.

The `FR_gsur_full.csv` is the unpivoted version of all 120 data sheets:
- 90,720 rows × 8 columns: `year`, `region_code`, `region_name`, `gsur`,
  `education`, `sex`, `age_group`, `sheet`.
- `gsur` is a percentage (values range from 1.3 to ~60+ for age-specific bands).
- Contains both NUTS-1 aggregates (FR1, FRB, ..., FRM, FRY) and their NUTS-2
  sub-components (FR10, FRB0, FRC1, FRC2, ...).

The `FR_gsur_ruro.csv` is a processed version that has already mapped NUTS-1
letter codes to a `drgn1` integer key (using 0=France national, 1–13=13 new
régions, 14=FRY/DOM), with additional columns `dgn`, `educ3`, `age_group_used`,
`region_key`. It contains **rates only** (no denominator counts). Shape: 2,160 rows.

The `FR_gsur_simple.parquet` is a further-filtered version retaining only the
broad-age (`Y20-64`, `Y25-34`, `Y_GE25`) rows for the 15 NUTS-1 codes. Shape: 9,720
rows. Values are in percentage points (2.4–~60).

---

## 9. GSUR workbook geography variable(s)

The GSUR workbook (`FR_gsur.xlsx`) uses Eurostat `geo` codes. The Structure sheet
confirms the geography dimension contains:

- `FR` — France national aggregate
- NUTS-1 letter codes: `FR1`, `FRB`, `FRC`, `FRD`, `FRE`, `FRF`, `FRG`, `FRH`,
  `FRI`, `FRJ`, `FRK`, `FRL`, `FRM`, `FRY`
- NUTS-2 letter codes: `FR10`, `FRB0`, `FRC1`, `FRC2`, `FRD1`, `FRD2`, `FRE1`,
  `FRE2`, `FRF1`, `FRF2`, `FRF3`, `FRG0`, `FRH0`, `FRI1`, `FRI2`, `FRI3`, `FRJ1`,
  `FRJ2`, `FRK1`, `FRK2`, `FRL0`, `FRM0`, `FRY1`, `FRY2`, `FRY3`, `FRY4`

These are **NUTS 2016 letter codes**, not the pre-2016 NUTS-2 numeric codes
(FR21, FR30, etc.) nor the pre-reform INSEE two-digit codes. The 22 old NUTS-2
régions appear in the NUTS-2 rows under their new letter names: e.g., FR21
Champagne-Ardenne is now FRF2, FR30 Nord-Pas-de-Calais is FRE1. Each old NUTS-2
region has exactly one new NUTS-2 code.

The `FR_gsur_full.csv` contains `region_code` and `region_name` columns. The
`region_name` column includes both old regional names (Champagne-Ardenne, Alsace,
etc.) at the NUTS-2 level and new merged regional names (Grand Est, Normandie, etc.)
at the NUTS-1 level. This confirms that the workbook contains the full hierarchy.

---

## 10. Whether GSUR workbook geography is NUTS-1, NUTS-2, old INSEE region, modern region, or unclear

**Both NUTS-1 and NUTS-2 (NUTS 2016 vintage) are present.**

- NUTS-1 rows: 14 codes (FR1–FRM + FRY). These are the 13 new metropolitan régions
  plus DOM aggregate. These correspond to EUROMOD `drgn1`-like groupings but use
  a different coding system (13 new regions, not 8 EUROMOD groups).
- NUTS-2 rows: 27 codes (FR10, FRB0, ..., FRM0, FRY1–FRY4). These are the 22 old
  metropolitan régions (renamed but geographically identical) plus 5 DOM NUTS-2 units.

**Neither the old INSEE two-digit regional codes (11, 21, 22, ..., 83, 94) nor the
old NUTS-2 alphanumeric codes (FR10, FR21, ..., FR83) appear as row identifiers.
The workbook uses only NUTS 2016 letter codes.**

However, by region name, the 22 old metropolitan régions are identifiable:
Champagne-Ardenne, Picardie, Haute-Normandie, etc. appear as NUTS-2 row labels
under their new codes (FRF2, FRE2, FRD2, etc.).

---

## 11. Whether GSUR geography can be mapped to drgn1 without many-to-one ambiguity

**Yes, with a NUTS-2-level join. No many-to-one ambiguity at the NUTS-2 level.**

The GSUR workbook contains NUTS-2 rows for all 22 old metropolitan régions under
their NUTS 2016 letter codes (e.g., FR10 for Île-de-France, FRF2 for
Champagne-Ardenne, FRE1 for Nord-Pas-de-Calais). Each new NUTS-2 letter code
corresponds to exactly one old NUTS-2 region — the 2016 reform was a pure
relabelling; the 22-region geography is preserved. A join from EUROMOD `drgn2`
(which maps to old NUTS-2 codes via the DRD) to GSUR NUTS-2 rows (which carry the
new letter codes and the matching old region names) is therefore one-to-one in both
directions.

The mapping is **reconstructible from local evidence** (DRD + GSUR workbook region
names) without any external file. The formal `NUTS2013-NUTS2016.xlsx` source should
still be acquired for documentary purposes (O1 and O7 sign-off), but it does not
reveal any new information: the mapping is fully determined by the region names already
present in the GSUR workbook. No crosswalk enumeration is performed here; that step
belongs to the implementation phase, after O1 is formally resolved.

**`FR_gsur_ruro.csv` uses the wrong regional object.** It has already collapsed the
data to the 13 new NUTS-1 regions under a `drgn1` column that runs 0–14. This is a
different coding from EUROMOD `drgn1` (1–8). The EUROMOD groupings cut across the
new NUTS-1 boundaries, so the ruro CSV cannot be directly joined to EUROMOD `drgn1`
for groups 2–8 without many-to-one ambiguity. The correct source for the GSUR
rebuild is the NUTS-2 rows in `FR_gsur_full.csv`.

---

## 12. Whether the Eurostat NUTS2013-NUTS2016 file is actually needed

**Not strictly needed, but useful for documentation.**

The old→new NUTS-2 renaming is reconstructible from the GSUR workbook region names
alone (the old region names Champagne-Ardenne, Picardie, etc. appear as NUTS-2 row
labels in `FR_gsur.xlsx`), joined to the DRD `drgn2`→old-NUTS-2 table. The
`NUTS2013-NUTS2016.xlsx` provides a canonical official source for the same mapping,
which eliminates any ambiguity from name-based reconstruction (accents, truncation,
ordering). For the crosswalk sign-off required by O7, having the official Eurostat
file as a documentary source is the more defensible choice.

**Bottom line**: the `NUTS2013-NUTS2016.xlsx` is useful for documentation and for
the O7 sign-off, but the crosswalk can be built from local evidence without it.

---

## 13. Whether the official COG/NUTS crosswalk chain is feasible

**Feasible, and simpler than described in the verification document.**

The verification document (`RURO_GSUR_external_acquisition_verification_claude_v1.md`)
described a four-step chain that included step 1 (EUROMOD `drgn1` → INSEE 2-digit
code) as unverified. This step is now fully resolved from local evidence: the DRD
documents the exact derivation of `drgn1` from `drgn2`, and `drgn2` is explicitly
mapped to the old NUTS-2 alphanumeric codes (`FR10`, `FR21`, etc.) in the DRD
`DB040` derivation. The "EUROMOD `drgn1` codebook not publicly documented" concern
in §4 of the verification document does not apply to this project, because the DRD is
available locally and provides the complete derivation chain.

The remaining chain is therefore:

1. **EUROMOD `drgn1` → old NUTS-2 code**: fully documented in the local DRD. Done.
2. **Old NUTS-2 code → new NUTS-2 letter code**: one-to-one renaming. Reconstructible
   from GSUR workbook region names or from `NUTS2013-NUTS2016.xlsx` (to be acquired
   for documentary purposes per O1).
3. **New NUTS-2 letter code → GSUR row**: direct lookup in `FR_gsur_full.csv`.
   Done.

Step 4 from the verification document (new NUTS-2 → NUTS-1 for the 13 new régions)
is not needed for this project because the project joins at NUTS-2 granularity.

The COG 2015 file (INSEE old-region geography) is not needed. The old-region-to-NUTS
join is already given by the DRD's `drgn2`-to-NUTS2 table combined with the GSUR
workbook's region names.

---

## 14. Benchmark implication

**Use the INSEE metropolitan France benchmark.**

The France 2016 EUROMOD input and all MNL parquets contain only metropolitan France
respondents (drgn1 1–8; drgn2 1–22; no DOM rows). The analytical sample is
France métropolitaine.

The correct 2016 national unemployment rate benchmark is the **INSEE BDM metropolitan
France series `001688526`** (*Taux de chômage au sens du BIT — Ensemble — France
métropolitaine — CVS*). The 9.7% figure cited in
`docs/RURO_GSUR_external_acquisition_verification_claude_v1.md` is the Q4 2016
value, not a confirmed annual average. The exact annual average for 2016 must be
extracted directly from the series before use in Stage A validation and cited with
the extraction date. The series URL is:
`https://www.insee.fr/fr/statistiques/serie/001688526`.

The Eurostat `tps00203`/`une_rt_a` `geo=FR` value (10.1% for 2016) covers France
hors Mayotte (métropole + 4 DOM) and must not be used as the validation reference
for this metropolitan sample.

---

## 15. Implementation readiness verdict

**NOT READY for implementation.**

Local evidence substantially advances the O1 position: the EUROMOD `drgn1`
derivation is fully documented in the local DRD, the GSUR workbook contains the
required NUTS-2 rows for all 22 old metropolitan régions, the sample is confirmed as
metropolitan France only, and the correct benchmark series has been identified.
These findings correct the most pessimistic claims in
`docs/RURO_GSUR_external_acquisition_verification_claude_v1.md`.

However, implementation remains unauthorized per §18 of the v2.1 specification
until all open decisions with hard-blocker status are closed. O1, O2, and O9
remain open. The local evidence audit does not itself constitute resolution of those
decisions; it establishes that resolution is achievable without additional
fundamental data-architecture work.

---

## 16. Exact blocker(s) remaining

Three blockers remain open. All are external-acquisition steps, not
data-architecture problems.

**O1 — formal crosswalk source not acquired.** The old-NUTS-2-to-new-NUTS-2
renaming is reconstructible from local evidence (DRD + GSUR region names), but the
O7 mandatory sign-off before merge requires a citable official source. Acquire
`NUTS2013-NUTS2016.xlsx` from the Eurostat NUTS history page and verify it cell by
cell against the GSUR region-name labels. This is an administrative step; the
underlying mapping is already fully determined locally.

**O2 — denominator data not downloaded.** `lfst_r_lfp2acedu` (Eurostat, labour-force
stock by NUTS-2 × sex × age × ISCED11) has been identified as the correct primary
source, but the France 2016 extract has not been downloaded and cell-level
suppression flags (`:`, `c`, `u`, `e`) for smaller French NUTS-2 units have not
been checked. Suppression at the four-dimensional cross-tab is common for Corse
(FRM0) and may affect other small units. Until this check is complete, it is
unknown whether the denominator is usable at full detail or requires a fallback per
§5(D2)–(D3) of the spec.

**O9 — benchmark not cited with exact annual value.** INSEE BDM series `001688526`
(France métropolitaine) has been identified as the correct source. The 9.7% figure
in the verification document is Q4 2016, not an annual average. The exact 2016
annual average must be extracted from the series, confirmed, and cited with an
extraction date before it can be used in Stage A validation.

**Previously unresolved questions now closed by this audit:**

| Question | Prior status | Audit finding |
|----------|-------------|---------------|
| EUROMOD drgn1 codebook | Unknown external | Fully documented in local DRD |
| GSUR workbook regional granularity | Unknown | NUTS-2 rows present for all 22 old régions |
| Can GSUR join to drgn1 without ambiguity | Unknown | Yes, at NUTS-2 level; ruro CSV is at wrong level |
| DOM in analytical sample | Unknown | Zero — metropolitan France only |
| Sample perimeter | Unknown | Metropolitan France (drgn2 ≤ 22; drgn1 1–8) |
| Correct benchmark series | Unknown | INSEE `001688526`; exact annual value still needed |