# RURO GSUR External Acquisition — Decision Memo v1

Date: 2026-05-17

Scope: final reconciliation of three external-acquisition diagnostic
documents into a single binding decision memo for the GSUR rebuild's
external assets (O1 crosswalk, O2 denominator, O9 national benchmark).
This memo is the authoritative reference for what is downloaded, what is
cited, what is constructed, and whether Stage A implementation is
authorized.

Inputs reconciled:
- `RURO_GSUR_external_acquisition_report_v1.md` (ChatGPT Deep Research
  acquisition report)
- `RURO_GSUR_external_acquisition_verification_claude_v1.md` (Claude
  adversarial verification of the above)
- `RURO_GSUR_local_O1_evidence_audit_v1.md` (local audit of files
  already in the project — DRD, GSUR workbook, MNL parquets)
- `RURO_GSUR_rebuild_specification_v2_1.md` (spec defining the rebuild
  and the open decisions to be resolved)
- `RURO_GSUR_v2_1_open_decisions_resolution_v1.md` (resolution memo
  recording locally-resolved decisions O3, O4, O5, O7, O8, O10)

Conservative-interpretation rule applied throughout: when the three
diagnostic documents disagree on a substantive point, the position
adopted is the **most documentation-demanding and least assumption-
heavy** of the three.

---

## 1. Final verdict

**Status: acquisition-ready. Implementation NOT authorized.**

The three diagnostic documents collectively establish that the GSUR
rebuild can proceed methodologically. The methodology is now fully
determined — the local DRD documents the `drgn1` → old NUTS-2
derivation explicitly, the GSUR workbook contains NUTS-2 rows for all
22 old metropolitan régions under their NUTS 2016 letter codes, the
sample is confirmed as metropolitan France only, and the correct
external assets have been identified for each of O1, O2, O9.

However, three external assets have not yet been downloaded and
archived:
- The Eurostat `NUTS2013-NUTS2016.xlsx` correspondence workbook
  (documentary source for O1 sign-off).
- The Eurostat `lfst_r_lfp2acedu` France 2016 extract (primary
  denominator source for O2).
- The INSEE BDM série `001688526` exact 2016 annual average (benchmark
  for O9 validation).

Until these three files are committed to `Data/external/` and the
denominator-suppression status is verified, no GSUR rebuild code may
be executed and no v2 MNL parquets may be written.

The readiness ladder (per the requirement of distinguishing six
levels) currently stands at:

| Level | Status |
|---|---|
| acquisition-ready (external sources identified and resolved) | **YES** |
| asset-inventory-ready (external files downloaded and archived) | NO |
| crosswalk-construction-ready (methodology verifiable, files in hand) | NO |
| GSUR-lookup-generation-ready (denominators confirmed available/usable) | NO |
| MNL-rebuild-ready (GSUR lookup validated against benchmarks) | NO |
| estimation-ready (versioned GSURv2 parquets validated) | NO |

The project is at the boundary between *acquisition-ready* and
*asset-inventory-ready*. The next concrete task is asset acquisition,
not implementation.

---

## 2. What the external acquisition report got right

The ChatGPT Deep Research acquisition report (referred to below as
"the acquisition report") correctly identifies the right official
sources at the file level:

(R1) **Eurostat `NUTS2013-NUTS2016.xlsx`** is genuinely the official
correspondence workbook between the two relevant NUTS vintages, hosted
on the Eurostat "History of NUTS" page. This is confirmed by the
Claude verification §2.

(R2) **`lfst_r_lfp2acedu`** is genuinely the right Eurostat table for
labour-force stock by (NUTS-2 × sex × age × ISCED11 education level).
This is confirmed by the Claude verification §2, which adds that the
dataset is "Economically active population by sex, age, educational
attainment level and NUTS 2 regions (1 000)", in thousand persons,
with all four required dimensions.

(R3) **`une_rt_a`** and **`tps00203`** are genuinely the right Eurostat
sources for the national unemployment rate annual series. These are
confirmed by the Claude verification §2.

(R4) **Commission Regulation (EU) 2016/2066** (CELEX 32016R2066) is
genuinely the legal instrument for the NUTS 2016 revision. Confirmed
by Claude verification §2.

(R5) The acquisition report's bottom-line framing — "acquisition-
ready, but not yet execution-ready" — is the correct overall verdict.
This memo preserves that framing.

(R6) The acquisition report correctly recognizes that "no official
source will map directly to EUROMOD `drgn1`" because `drgn1` is an
EUROMOD-specific grouping, not an official Eurostat or INSEE
classification (acquisition report §4 caveat). This framing is
correct and is preserved.

---

## 3. What the Claude verification corrected

The Claude adversarial verification identifies four substantive
corrections to the acquisition report that must be carried forward.
All four are accepted under the conservative-interpretation rule.

(C1) **NUTS-2 was NOT realigned to the 13 new métropolitaine régions
in NUTS 2021** (acquisition report claim, Claude verification §3).
The NUTS-2 level still reflects the 22 former régions in NUTS 2016,
NUTS 2021, and NUTS 2024. Only NUTS-1 hosts the 13 new régions
(replacing the ZEAT). The NUTS-2 codes are renamed under the new
letter scheme (FR21 → FRF2, FR42 → FRF1, FR43 → FRC2, etc.) but the
underlying 22-region geography is preserved.

Implication: the GSUR rebuild's crosswalk is a pure renaming at the
NUTS-2 level. The 22 old metropolitan régions are still individually
identifiable in the GSUR workbook, just under new letter codes.

(C2) **`lfst_r_lfu3pers` does NOT have a duration dimension** (claim
in acquisition report §13, corrected in Claude verification §3).
Duration of unemployment at NUTS-2 level sits in `lfst_r_lfu2ltu`.
This correction matters for any sensitivity analyses but not for the
primary denominator path (which uses `lfst_r_lfp2acedu`).

(C3) **Eurostat `geo = FR` includes the four DOM** (Guadeloupe,
Martinique, Guyane, Réunion) for reference year 2016 (Claude
verification §3 and §10). It is *France hors Mayotte*, not France
métropolitaine. Mayotte was added only from 2024.

Implication for O9: using the Eurostat `FR` benchmark (10.1%)
against a metropolitan-France-only sample would overstate the
benchmark by approximately 0.4 percentage points because DOM regions
have systematically higher unemployment rates than métropole. The
correct benchmark for a métropole sample is INSEE BDM série
`001688526`, not Eurostat `une_rt_a`.

(C4) **The EUROMOD `drgn1` codebook is NOT publicly documented in
the EUROMOD France country report** (Claude verification §3). The
publicly available country report (Bouvard & Trannoy, AMSE) does
not contain the variable codebook; it documents policies, not
variable definitions.

This concern is addressed by the local O1 audit (see §4 below): the
EUROMOD France 2016 **local DRD** does contain the full `drgn1`
derivation explicitly, so step 1 of Claude's four-step chain is
locally resolved without requiring the public country report.

Additionally, two minor corrections are noted:
- The author attribution for the FR_2016/FR_2017 country report is
  Bouvard & Trannoy, not De Agostini (acquisition report §3 vs Claude
  verification §3 end).
- The dataset gloss for `lfst_r_lfp2acedu` is "p2 = NUTS-2", not
  "p2 = participation" (Claude verification §15).

---

## 4. What the local O1 audit resolved

The local audit (`RURO_GSUR_local_O1_evidence_audit_v1.md`) is the
strongest of the three diagnostic documents because it inspects the
actual files in the project. It resolves the four most pessimistic
claims in the Claude verification:

(A1) **The EUROMOD `drgn1` derivation is fully documented in the
local DRD.** The DRD `DRD_FR_2016_a3_export.txt` contains the exact
Stata derivation from `drgn2`, and `drgn2` is explicitly mapped to old
NUTS-2 alphanumeric codes (`FR10`, `FR21`, ..., `FR83`) in the same
file. This collapses Claude's four-step chain to a three-step chain
where the first step is fully resolved locally:

| step | content | source |
|---|---|---|
| 1 | EUROMOD `drgn1` → old NUTS-2 code | local DRD (resolved) |
| 2 | old NUTS-2 code → new NUTS 2016 letter code | `NUTS2013-NUTS2016.xlsx` (needs acquisition) |
| 3 | new NUTS 2016 letter code → GSUR row | direct lookup in `FR_gsur_full.csv` (resolved) |

The COG 2015/2016 INSEE files and step 4 (new NUTS-2 → NUTS-1) from
the Claude verification are **not needed** for this project. The
project joins at NUTS-2 granularity; the 13 new NUTS-1 régions are
irrelevant to the EUROMOD `drgn1` grouping.

(A2) **The GSUR workbook contains NUTS-2 rows for all 22 old
metropolitan régions** under their new letter codes. The Structure
sheet (audit §8) shows the `geo` dimension includes both NUTS-1 codes
(14: FR1, FRB–FRM, FRY) and NUTS-2 codes (27: FR10, FRB0, FRC1, ...,
FRM0, FRY1–FRY4). Each old metropolitan NUTS-2 region has exactly one
new NUTS-2 letter code; the mapping is one-to-one and the workbook
preserves the full hierarchy.

(A3) **The analytical sample is metropolitan France only.** The raw
input `fr_2016.parquet` and both MNL parquets contain zero
households with `drgn2 ≥ 23` (DOM) or `drgn1 ≥ 9`. The sample is
strictly metropolitan France (`drgn2` 1–22, `drgn1` 1–8). Mayotte is
absent.

This resolves the perimeter ambiguity that the Claude verification
flagged as unresolved (§11 of the verification): the benchmark must
be INSEE BDM `001688526` (France métropolitaine), not Eurostat
`une_rt_a` (France hors Mayotte).

(A4) **The current `FR_gsur_ruro.csv` and `FR_gsur_ruro.parquet`
files use the wrong regional object.** They have already been
collapsed to 13 new NUTS-1 régions under a `drgn1` column that runs
0–14 (where 0 is the national aggregate, 1–13 are the 13 new
régions, and 14 is the DOM aggregate). This is a different coding
from EUROMOD `drgn1` (1–8). The current ruro CSV/parquet **cannot be
directly joined** to EUROMOD `drgn1` for groups 2–8 because the new
NUTS-1 régions cut across the old EUROMOD groupings (e.g., modern
Grand Est FRF contains old FR21 in `drgn1=2` and old FR41/FR42 in
`drgn1=4`).

The correct source for the GSUR rebuild is the **NUTS-2 rows in
`FR_gsur_full.csv`** (or equivalently in the original `FR_gsur.xlsx`
data sheets), joined via the renamed NUTS-2 codes.

Additionally:
- Age 65 in singles: 200 rows = 2 households (audit confirms O3
  decision: A65-3 Y20-64 fallback is appropriate; sample impact is
  0.12%).
- Age 65 in couples: 0 rows.
- The INSEE 9.7% figure in the Claude verification is the Q4 2016
  value, not the annual average. The exact 2016 annual average must
  be extracted from INSEE BDM série `001688526` before use.

---

## 5. O1 crosswalk decision

**Decision: build the `drgn1` → NUTS-2 crosswalk locally from the
DRD, then verify against the Eurostat `NUTS2013-NUTS2016.xlsx` file
acquired as documentary source.**

The crosswalk methodology is:

(S1) Use the DRD's documented `drgn1` → `drgn2` rule (locally
available in `DRD_FR_2016_a3_export.txt`) to build a 1-to-many
mapping from EUROMOD `drgn1` (categories 1–8) to old NUTS-2 codes
(FR10, FR21, ..., FR83). This is fully determined by the DRD:

```
drgn1 = 1  →  {FR10}
drgn1 = 2  →  {FR21, FR22, FR23, FR24, FR25, FR26}
drgn1 = 3  →  {FR30}
drgn1 = 4  →  {FR41, FR42, FR43}
drgn1 = 5  →  {FR51, FR52, FR53}
drgn1 = 6  →  {FR61, FR62, FR63}
drgn1 = 7  →  {FR71, FR72}
drgn1 = 8  →  {FR81, FR82, FR83}
```

(S2) Apply the old NUTS-2 → new NUTS 2016 letter-code renaming
verified against the Eurostat `NUTS2013-NUTS2016.xlsx` workbook
(acquired as documentary source). The expected renaming (per local
audit and Claude verification §3):

```
FR10 → FR10  (Île-de-France unchanged)
FR21 → FRF2  (Champagne-Ardenne)
FR22 → FRE2  (Picardie)
FR23 → FRD2  (Haute-Normandie)
FR24 → FRB0  (Centre-Val de Loire)
FR25 → FRD1  (Basse-Normandie)
FR26 → FRC1  (Bourgogne)
FR30 → FRE1  (Nord-Pas-de-Calais)
FR41 → FRF3  (Lorraine)
FR42 → FRF1  (Alsace)
FR43 → FRC2  (Franche-Comté)
FR51 → FRG0  (Pays de la Loire)
FR52 → FRH0  (Bretagne)
FR53 → FRI3  (Poitou-Charentes)
FR61 → FRI1  (Aquitaine)
FR62 → FRJ2  (Midi-Pyrénées)
FR63 → FRI2  (Limousin)
FR71 → FRK2  (Rhône-Alpes)
FR72 → FRK1  (Auvergne)
FR81 → FRJ1  (Languedoc-Roussillon)
FR82 → FRL0  (Provence-Alpes-Côte d'Azur)
FR83 → FRM0  (Corse)
```

This mapping is what the audit (§5) calls "reconstructible from
local evidence" — the GSUR workbook contains region names under both
old and new codes, and the renaming is verifiable cell-by-cell.
However, the conservative interpretation requires that this be
verified against the Eurostat documentary source, not just inferred
from region names (which can have accent/truncation/spelling
variants).

(S3) Join each new NUTS-2 letter code to the corresponding GSUR row
in `FR_gsur_full.csv` (or the source workbook). The join is direct
because the GSUR workbook indexes rows by the new NUTS-2 letter
codes per the audit §9.

The output is a verified crosswalk file:
`Data/external/fr_drgn1_to_nuts2_crosswalk.csv`

with columns:
- `drgn1` (1–8)
- `old_nuts2_code` (FR10, FR21, ..., FR83)
- `region_name` (Île-de-France, Champagne-Ardenne, ...)
- `new_nuts2_code_2016` (FR10, FRF2, ..., FRM0)
- `verified_against_eurostat` (boolean, must be True for all rows
  before sign-off)

The implementation crosswalk file must be cited and signed off per
O7 (mandatory manual sign-off before merge).

---

## 6. O1 remaining risk

Three residual risks at the crosswalk stage:

(K1) **Edge cases in the old → new NUTS-2 renaming**. The mapping in
§5(S2) is the canonical Eurostat renaming, but cell-by-cell
verification against `NUTS2013-NUTS2016.xlsx` is required for sign-
off. Specifically: confirm that each of the 22 old codes appears in
the Eurostat file with the expected new letter code, and that no
old code is split across multiple new codes (no NUTS reform splits
at NUTS-2 level — geography is preserved — but documentary
verification is required).

(K2) **Spelling/accent variants in region names across files**. The
GSUR workbook may use slightly different region names than the
Eurostat file (Île-de-France vs Ile de France; Provence-Alpes-Côte
d'Azur vs Provence-Alpes-Côte-d'Azur). Verification should join by
NUTS-2 code (the safe key), not by region name (the unsafe key).
The crosswalk file must be coded by NUTS-2 letter code, not by
region name string.

(K3) **The `FR_gsur_ruro.csv` file currently in `Data/external/` is
at the wrong granularity** (13 new NUTS-1 régions, not 22 NUTS-2 old
régions per the audit §11). This file must not be used in the
rebuild. The implementation must read from `FR_gsur_full.csv` or
`FR_gsur.xlsx` directly at NUTS-2 level. The misaligned ruro CSV
should be archived with a clear note, not deleted.

These risks are documentary/operational, not methodological. They
are resolved during implementation, not during acquisition.

---

## 7. O2 denominator decision

**Decision: primary denominator is Eurostat `lfst_r_lfp2acedu`
(labour-force stock by NUTS-2 × sex × age × ISCED11 educational
attainment, France 2016 extract). Fallback hierarchy per §8.**

The Eurostat dataset:
- **Name**: "Economically active population by sex, age, educational
  attainment level and NUTS 2 regions (1 000)"
- **Code**: `lfst_r_lfp2acedu`
- **Unit**: thousand persons (stock, not rate)
- **Dimensions**: NUTS-2 × sex × age × ISCED11 education × year
- **Reference period**: 2016 (annual)
- **URL**: `https://ec.europa.eu/eurostat/databrowser/view/lfst_r_lfp2acedu/default/table`

Why this dataset is correct:
- Same four dimensions as the GSUR unemployment cell (NUTS-2, sex,
  age, education).
- Labour-force concept (not population) matches the unemployment
  rate's denominator definition (rate = unemployed / labour force).
- Same vintage source (EU-LFS, EU-LFS-derived data published with
  consistent ISCED11 categories).

Two operational checks must be done before this dataset is committed
as the primary denominator:

(P1) **Cell-suppression check**. Small NUTS-2 units (Corse FRM0,
Limousin FRI2) may have suppressed cells at the four-dimensional
crosstab. Eurostat marks suppressed cells with `:`, `c`, `u`, or `e`
flags. The extract must be downloaded and the suppression status
must be inventoried per cell before the lookup is built.

(P2) **ISCED11 ↔ MNL `educ3` alignment**. The Eurostat dataset uses
ISCED11 categories (typically ED0-2, ED3_4, ED5-8 in `lfst_r_lfp2acedu`).
The MNL `educ3` uses three values (0/1/2). The audit §2 confirms the
mapping (deh 0/1/2 → educ3=0; deh 3/4 → educ3=1; deh 5 → educ3=2)
which corresponds to ISCED 0-2 → 0, ISCED 3-4 → 1, ISCED 5-8 → 2.
This must be verified against the actual Eurostat dataset column
labels.

---

## 8. O2 fallback hierarchy

For cells where the primary denominator is unavailable or suppressed:

(F1) **Primary (D1 in v2.1 spec §5)**: labour-force from
`lfst_r_lfp2acedu`. Use when the cell value is present and
unsuppressed.

(F2) **Fallback A (D2 in v2.1 spec §5)**: population from
`lfst_r_lfsd2pop` (or equivalent population-by-NUTS-2-sex-age table).
Use when labour-force is suppressed but population is available.
Cell-level `weighting_source = 'population'` flag must be set.

Note that `lfst_r_lfsd2pop` does NOT include the education dimension,
so it is a strictly coarser fallback. If education-stratified
population is unavailable, the cell may need to use the
population-without-education denominator combined with an education-
share assumption — but this introduces additional approximation
error that must be documented.

(F3) **Fallback B (D3 in v2.1 spec §5)**: approximate-uniform
aggregation across modern NUTS components. Use only as a last
resort, only with explicit reviewer sign-off, and only with cell-
level `weighting_source = 'approximate_uniform'` flag.

(F4) **Unaggregatable**: cell uses the broad-age national value as
final fallback per §5(D3)(a), with `weighting_source =
'national_fallback'` flag.

The validation report must list every cell that uses Fallback A, B,
or the unaggregatable path, and quantify what fraction of the v2
GSUR lookup values are non-primary.

**Until the cell-suppression check (P1) is complete, it is unknown
which cells will use which fallback. This is a hard blocker for
implementation.**

---

## 9. O9 benchmark decision

**Decision: use INSEE BDM série `001688526` ("Taux de chômage au
sens du BIT — Ensemble — France métropolitaine — CVS"). The
extracted 2016 annual average value (not yet known) is the
validation benchmark.**

Rationale:
- The analytical sample is metropolitan France only (audit §6, §7;
  resolves Claude verification §11 ambiguity).
- Eurostat `geo = FR` covers France hors Mayotte (métropole + 4 DOM),
  not metropolitan France alone (Claude verification §10).
- Using Eurostat `FR` (10.1%) against a metropolitan sample would
  overstate the benchmark by ~0.4 percentage points due to higher
  DOM unemployment.
- INSEE BDM `001688526` is the French national-statistics-office
  series for metropolitan France, BIT-concept unemployment rate,
  seasonally adjusted, annual frequency available.

Two operational steps before this can be used:

(B1) **Extract the exact 2016 annual average from the series**. The
9.7% figure cited in the Claude verification §11 is the Q4 2016
value, not the annual average. The annual average for 2016 must be
extracted from `https://www.insee.fr/fr/statistiques/serie/001688526`
and confirmed via the INSEE downloadable CSV.

(B2) **Verify the series field**. The series description must be
checked against the audit §14 reading ("Taux de chômage au sens du
BIT — Ensemble — France métropolitaine — CVS"). The series should be
quarterly (CVS = seasonally adjusted), with an annual average column
or computable from the four 2016 quarters.

The validation report must cite:
- Series code: INSEE BDM `001688526`
- Series title: as published by INSEE
- URL: `https://www.insee.fr/fr/statistiques/serie/001688526`
- Date of extraction
- Exact 2016 annual average value
- Concept: BIT (ILO definition), metropolitan France, age 15+,
  seasonally adjusted (CVS), annual average of 4 quarterly values

The Eurostat `tps00203` value (10.1%) and INSEE BDM `001688527`
(France hors Mayotte) are **not** the validation benchmark for this
project. They may be cited as alternative perimeters for
comparison purposes only.

---

## 10. Sample perimeter decision

**Decision: metropolitan France only.**

This decision is grounded in three independent confirmations:

(M1) **MNL parquet evidence**. The local audit §4 inspects both
canonical MNL parquets and finds zero households with `drgn1 ≥ 9`.
All 1,676 singles households and 2,577 couples households are in
metropolitan France (`drgn1` 1–8).

(M2) **Raw EUROMOD input evidence**. The audit §3 inspects
`fr_2016.parquet` (the raw EUROMOD input file) and finds zero rows
with `drgn2 ≥ 23` (the DOM range). The sample upstream is metropolitan
France.

(M3) **DRD-documented derivation**. The DRD explicitly defines `drgn2
= 27 → FRZZ → drgn1 = 10 → recoded to drgn1 = 1` (FRZZ residual
collapsed to Île-de-France). No DOM-recoding logic; the DOM
categories `drgn1` 9 are simply absent from the metropolitan-France
file.

This decision is binding for:
- Benchmark choice (§9: INSEE `001688526`, not Eurostat `FR`).
- Schema retention (§5.O5 resolution: `drgn1 = 9` retained in schema
  for portability but NaN for this sample).
- M1-clean specifications (if region dummies are added, the partition
  is `drgn1 ∈ {1, ..., 8}`, not including 9).

The decision resolves the perimeter question that the Claude
verification §11 flagged as the binding ambiguity for O9.

---

## 11. Files to download

The minimum acquisition package is three files. Optional supplementary
files are listed at the end.

### 11.1 Required (hard blockers for implementation)

(D1) **Eurostat NUTS correspondence workbook**
- Filename: `NUTS2013-NUTS2016.xlsx`
- URL: `https://ec.europa.eu/eurostat/documents/345175/629341/NUTS2013-NUTS2016.xlsx`
- Source: Eurostat, "History of NUTS" page
- Purpose: documentary verification of the §5(S2) old → new NUTS-2
  renaming for O1 sign-off
- Archive location: `Data/external/NUTS2013-NUTS2016.xlsx`
- Resolves: O1 documentary requirement

(D2) **Eurostat labour-force regional extract**
- Filename: download as `lfst_r_lfp2acedu_FR_2016.tsv` (or .xlsx)
- URL: `https://ec.europa.eu/eurostat/databrowser/view/lfst_r_lfp2acedu/default/table`
- Source: Eurostat databrowser
- Extract parameters:
  - `geo`: all FR NUTS-2 codes (FR10, FRB0, FRC1, FRC2, FRD1, FRD2,
    FRE1, FRE2, FRF1, FRF2, FRF3, FRG0, FRH0, FRI1, FRI2, FRI3,
    FRJ1, FRJ2, FRK1, FRK2, FRL0, FRM0 — the 22 metropolitan
    NUTS-2 regions; DOM codes FRY1–FRY4 may be excluded since the
    sample doesn't include them)
  - `sex`: M, F (not T — denominators are sex-specific)
  - `age`: Y15-24, Y25-34, Y35-44, Y45-54, Y55-64, and Y20-64 (the
    Eurostat age bands matching the GSUR workbook per audit §8)
  - `isced11`: ED0-2, ED3_4, ED5-8 (the three matching education
    levels)
  - `time`: 2016
  - `unit`: THS_PER (thousand persons)
- Purpose: primary denominator for §7 GSUR cell construction
- Archive location: `Data/external/lfst_r_lfp2acedu_FR_2016.tsv`
- Resolves: O2 primary denominator requirement
- **Mandatory verification post-download**: inventory cell suppression
  per §8 (P1).

(D3) **INSEE national benchmark series**
- Series: `001688526`
- Title: "Taux de chômage au sens du BIT — Ensemble — France
  métropolitaine — CVS"
- URL: `https://www.insee.fr/fr/statistiques/serie/001688526`
- Source: INSEE Banque de Données Macroéconomiques (BDM)
- Format: CSV (downloadable from the BDM page)
- Purpose: validation benchmark for §9 Stage A rebuilt national rate
- Archive location: `Data/external/insee_001688526_2016.csv`
- Resolves: O9 benchmark requirement
- **Mandatory verification post-download**: extract exact 2016 annual
  average value (audit §14 corrects the 9.7% Q4 figure).

### 11.2 Optional supplementary downloads

These are useful for documentation traceability but not required for
implementation.

(D4) **Population denominator fallback** (only if (D2) has substantial
suppression):
- Filename: `lfst_r_lfsd2pop_FR_2016.tsv`
- URL: `https://ec.europa.eu/eurostat/databrowser/view/lfst_r_lfsd2pop/default/table`
- Purpose: O2 Fallback A per §8(F2)

(D5) **EU-LFS metadata page** (for ESMS citation):
- URL: `https://ec.europa.eu/eurostat/cache/metadata/en/lfst_r_esms.htm`
- Format: HTML, archive as PDF
- Purpose: documentation of EU-LFS methodology cited in validation

(D6) **Commission Regulation 2016/2066** (legal documentation):
- URL: `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R2066`
- Purpose: legal traceability of NUTS 2016 vintage

(D7) **INSEE NUTS metadata definition** (concept documentation):
- URL: `https://www.insee.fr/fr/metadonnees/definition/c2112`
- Purpose: definition of French NUTS structure post-reform

(D8) **Loi n° 2015-29 du 16 janvier 2015** (legal documentation):
- URL: `https://www.legifrance.gouv.fr/loda/id/JORFTEXT000030109622`
- Purpose: legal traceability of the 22 → 13 region reform

These are documentation, not data inputs. The validation report
should reference (D5) and (D6) for citations; (D7) and (D8) only if
the paper discusses the territorial reform.

---

## 12. Files to create manually

(M1) **Crosswalk file**:
- Path: `Data/external/fr_drgn1_to_nuts2_crosswalk.csv`
- Schema: per §5 of this memo (`drgn1`, `old_nuts2_code`,
  `region_name`, `new_nuts2_code_2016`, `verified_against_eurostat`)
- Construction: from local DRD `drgn1` derivation, joined to the
  Eurostat `NUTS2013-NUTS2016.xlsx` renaming for verification
- Sign-off: required (O7), recorded as an explicit user approval
  message before merge into MNL parquets

(M2) **Crosswalk source documentation**:
- Path: `Data/external/gsur_crosswalk_source.txt`
- Content: citations for all sources used in (M1), including DRD
  local path and Eurostat URL, with date of access
- Constructed at acquisition completion, before implementation

(M3) **Denominator source documentation**:
- Path: `Data/external/gsur_denominator_source.txt`
- Content: citation for Eurostat `lfst_r_lfp2acedu`, extraction date,
  extract parameters used, cell-level suppression inventory result
- Constructed after (D2) download and verification

(M4) **Benchmark source documentation**:
- Path: `Data/external/gsur_benchmark_source.txt`
- Content: INSEE BDM `001688526` citation, extraction date, exact
  2016 annual average value, concept description
- Constructed after (D3) download and verification

These four manual files are companions to the three downloaded files
(D1, D2, D3) and form the complete external asset package.

---

## 13. Citations to record

The Stage A validation report
(`Results/RURO_GSUR_v2_stage_A_validation_report_v1.md`) must record
the following citations in a structured form:

### For O1 crosswalk

| Item | Reference |
|---|---|
| Local derivation source | EUROMOD France 2016 DRD, `DRD_FR_2016_a3_export.txt`, local file, accessed [date] |
| Official documentary source | Eurostat, "History of NUTS — NUTS 2013–NUTS 2016 correspondence", `NUTS2013-NUTS2016.xlsx`, downloaded [date], URL: `https://ec.europa.eu/eurostat/documents/345175/629341/NUTS2013-NUTS2016.xlsx` |
| Legal underpinning (NUTS 2016 revision) | Commission Regulation (EU) 2016/2066 of 21 November 2016 amending Regulation (EC) No 1059/2003, CELEX 32016R2066, URL: `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R2066` |
| Legal underpinning (French regional reform) | Loi n° 2015-29 du 16 janvier 2015 relative à la délimitation des régions, JORF TEXT000030109622, URL: `https://www.legifrance.gouv.fr/loda/id/JORFTEXT000030109622` |
| Conceptual reference | INSEE, NUTS metadata definition c2112, URL: `https://www.insee.fr/fr/metadonnees/definition/c2112` |

### For O2 denominator

| Item | Reference |
|---|---|
| Primary source | Eurostat, "Economically active population by sex, age, educational attainment level and NUTS 2 regions (1 000)", `lfst_r_lfp2acedu`, year 2016 extract, downloaded [date], URL: `https://ec.europa.eu/eurostat/databrowser/view/lfst_r_lfp2acedu/default/table` |
| Methodology | Eurostat EU-LFS ESMS metadata, URL: `https://ec.europa.eu/eurostat/cache/metadata/en/lfst_r_esms.htm` |
| Cell-suppression inventory | `Data/external/gsur_denominator_source.txt` (project-internal file documenting suppression status by cell) |

If population fallback (D2) is used, additionally cite:
- Eurostat `lfst_r_lfsd2pop` with the same format.

### For O9 benchmark

| Item | Reference |
|---|---|
| Primary benchmark | INSEE Banque de Données Macroéconomiques, série `001688526`, "Taux de chômage au sens du BIT — Ensemble — France métropolitaine — CVS", 2016 annual average value = [TBD after extraction], downloaded [date], URL: `https://www.insee.fr/fr/statistiques/serie/001688526` |
| Sample perimeter confirmation | This decision memo §10 |

The Eurostat `une_rt_a` value (10.1%) and INSEE BDM `001688527`
(France hors Mayotte) may be cited as alternative-perimeter
references in a sensitivity-analysis row, but are **not** the primary
benchmark.

---

## 14. Whether Stage A implementation is authorized

**Stage A implementation is NOT authorized.**

The methodology is determined, the external sources are identified,
the sample perimeter is confirmed, and six of ten open decisions are
resolved. But three of the ten open decisions remain unresolved
because the corresponding files have not yet been downloaded and
verified:

| Decision | Status | Asset required |
|---|---|---|
| O1 | resolution defined, asset not acquired | `NUTS2013-NUTS2016.xlsx` |
| O2 | resolution defined, asset not acquired, suppression unknown | `lfst_r_lfp2acedu` 2016 extract |
| O9 | resolution defined, exact value not extracted | INSEE BDM `001688526` |
| O3 | RESOLVED | (locally resolved) |
| O4 | RESOLVED | (locally resolved) |
| O5 | RESOLVED | (locally resolved) |
| O6 | DEFERRED (Stage B necessity, decided post-Stage-A) | n/a |
| O7 | RESOLVED (sign-off required at crosswalk-construction step) | (procedural) |
| O8 | RESOLVED (tolerance 0.001) | (locally resolved) |
| O10 | RESOLVED (versioned-first promotion rule) | (locally resolved) |

Per the v2.1 specification §18, implementation requires that all hard-
blocker open decisions be resolved AND the corresponding external
assets be available. The hard-blocker status of O1, O2, and O9 is
preserved.

The current readiness level is **acquisition-ready**: the next steps
are well-defined and the diagnostic work to identify them is
complete. Implementation work (code, MNL parquet writes, estimation)
is not authorized.

---

## 15. If not authorized, exact remaining blockers

Three concrete acquisition tasks must be completed in order for
implementation to be authorized:

**Blocker 1: download `NUTS2013-NUTS2016.xlsx` from Eurostat, archive
in `Data/external/`, and verify cell-by-cell against the §5(S2)
expected renaming.**

The §5(S2) mapping is the canonical Eurostat renaming and is
expected to verify cleanly. If any old NUTS-2 code maps unexpectedly
or is missing from the workbook, that is a flag for investigation
before implementation. Verification produces a confirmation note in
the crosswalk source documentation (M2).

**Blocker 2: download `lfst_r_lfp2acedu` France 2016 extract from
Eurostat databrowser, archive in `Data/external/`, and inventory
cell-level suppression flags.**

The extract parameters are specified in §11(D2). After download, run
a cell-suppression audit:
- Count cells with valid numeric values (primary denominator
  available, weighting_source = `labour_force`).
- Count cells with suppression flags (`:`, `c`, `u`, `e`), broken
  down by which dimension causes the suppression.
- For each suppressed cell, determine the fallback path per §8:
  population (F2), approximate-uniform (F3), or national fallback
  (F4).

If suppression affects more than ~10% of cells or any large
metropolitan region (Île-de-France, Hauts-de-France/Nord), this is a
flag for revisiting the v2.1 specification — possibly requiring a v3
specification documenting the limitation.

**Blocker 3: extract INSEE BDM série `001688526` exact 2016 annual
average from the INSEE BDM page.**

The series should be quarterly seasonally adjusted; the annual
average is computed as the mean of the four 2016 quarterly values.
Record the four quarterly values and the computed annual average in
`Data/external/gsur_benchmark_source.txt`.

**After all three blockers are cleared**, this decision memo is
updated to v2 (or a separate `v1_post_acquisition` memo is
produced) recording the resolved values, and a Claude Code
implementation prompt for the v2.1 rebuild can be written.

---

## 16. Exact next Claude Code task

The next concrete task is **acquisition**, not implementation. Below
is the structured Claude Code task that should follow this memo:

```text
Work locally in my RURO/MNL codebase.

This task is the GSUR external asset acquisition. It is not
implementation; no GSUR rebuild code may be run.

Read:
- docs/RURO_GSUR_external_acquisition_decision_v1.md (this memo)
- docs/RURO_GSUR_rebuild_specification_v2_1.md (the spec)
- docs/RURO_GSUR_v2_1_open_decisions_resolution_v1.md (resolved
  decisions; do not duplicate)

Task: acquire and archive the three external assets required for
GSUR rebuild authorization, and produce a post-acquisition verdict
memo.

Step 1 — Download Eurostat NUTS2013-NUTS2016.xlsx.
URL: https://ec.europa.eu/eurostat/documents/345175/629341/NUTS2013-NUTS2016.xlsx
Save to: Data/external/NUTS2013-NUTS2016.xlsx

Step 2 — Verify the §5(S2) old → new NUTS-2 renaming cell-by-cell
against the downloaded workbook. Create:
- Data/external/fr_drgn1_to_nuts2_crosswalk.csv (the verified
  crosswalk)
- Data/external/gsur_crosswalk_source.txt (citations + verification
  notes)

Step 3 — Download Eurostat lfst_r_lfp2acedu France 2016 extract.
URL: https://ec.europa.eu/eurostat/databrowser/view/lfst_r_lfp2acedu/default/table
Extract parameters: per §11(D2) of the decision memo.
Save to: Data/external/lfst_r_lfp2acedu_FR_2016.tsv

Step 4 — Inventory cell-level suppression in lfst_r_lfp2acedu.
Produce: Data/external/gsur_denominator_source.txt with:
- Citation
- Extraction parameters
- Per-cell suppression inventory (which cells have `:`, `c`, `u`,
  `e` flags; which dimensions cause suppression)
- Recommended fallback path per suppressed cell per §8 of the
  decision memo

Step 5 — Extract INSEE BDM 001688526 exact 2016 annual average.
URL: https://www.insee.fr/fr/statistiques/serie/001688526
Save to: Data/external/insee_001688526_2016.csv
Compute the 2016 annual average from the four quarterly values.
Produce: Data/external/gsur_benchmark_source.txt with citation,
extraction date, four quarterly values, computed annual average,
and concept description.

Step 6 — Write the post-acquisition verdict memo:
docs/RURO_GSUR_external_acquisition_completion_v1.md

The verdict memo must state:
- Whether each of O1, O2, O9 is now resolved (yes/no per blocker)
- Whether implementation is now authorized (yes / partial / no)
- If partial: which cells require fallback paths, and whether v3
  specification is needed
- If no: which acquisition step failed and why

Do not run GSUR rebuild code. Do not write to MNL parquets. This
task is acquisition only.

Tools allowed: web_fetch, file write to Data/external/ and docs/.
```

If this acquisition completes cleanly (all three downloads succeed,
suppression is acceptable, benchmark extraction succeeds), the
project moves to **asset-inventory-ready** and the next task is the
GSUR rebuild implementation prompt per v2.1 §15.

If suppression in `lfst_r_lfp2acedu` is severe (e.g., > 30% of cells
affected, or full suppression for any large region), the project may
need a v3 specification documenting an approximate-implementation
path. In that case, the post-acquisition verdict memo should
explicitly flag this as a v3-trigger and recommend writing the v3
spec before any implementation work.

---

## 17. Suggested filename and supersession

Save this memo as:
`docs/RURO_GSUR_external_acquisition_decision_v1.md`
(category: decision memo / acquisition).

This memo supersedes the conclusions of:
- the ChatGPT Deep Research acquisition report (the report's
  identifications are accepted with the Claude verification's four
  corrections);
- the Claude verification report (its conclusions are accepted with
  the local audit's resolution of step 1 of the four-step chain);
- the local O1 evidence audit (its conclusions are accepted and
  formalized into binding decisions).

This memo and the v2.1 specification together define the rebuild's
external-data requirements and the acquisition path. The post-
acquisition verdict memo (to be produced by the next Claude Code
task) will determine whether implementation is authorized or whether
a v3 specification is required.
