# JMP GSURv2 Multi-Year Extension — Implementation Audit v1

**Document:** `docs/JMP_GSURv2_multi_year_extension_implementation_audit_v1.md`
**Date:** 2026-05-20
**Auditor:** Claude Code Sonnet (local codebase inspection; no construction, estimation, or welfare)
**Governing document:** `docs/JMP_GSURv2_multi_year_extension_design_memo_v1.md`
**Scope:** Readiness assessment for extending the GSURv2 Stage A build to opportunity years 2014 and 2015

---

## 1. Purpose and scope

This audit assesses readiness for the GSURv2 multi-year extension as specified in
`docs/JMP_GSURv2_multi_year_extension_design_memo_v1.md` §19. The six audit conditions
A1–A6 defined in that memo are evaluated in full. No GSURv2 lookup is constructed, no
script is modified, no external data is downloaded, no MNL parquets are rebuilt, no
pooled models are estimated, and no welfare computations are performed.

The audit answers six questions:

- **A1** — Is the lfst_r_lfu3rt unemployment-rate source available for y2014 and y2015?
- **A2** — Are the lfst_r_lfsd2pop (D2) and lfst_r_lfp2acedu (D1) denominator files
  available for y2014 and y2015?
- **A3** — Are the INSEE BDM 001688526 national-benchmark values available for y2014
  and y2015?
- **A4** — Do available extracts use a NUTS-2 vintage compatible with the crosswalk?
- **A5** — Does the existing y2016 GSURv2 lookup satisfy provenance-lock requirements
  K1, K2, and K3 for reuse without a rebuild?
- **A6** — Can `enh_prepare_FR_gsur_v2.py` accommodate the seven parameterisation
  changes C1–C7 without modifying year-invariant logic?

The immediate next operational step after this audit is to resolve all failing
conditions, then issue a separate GSURv2 construction authorisation prompt. This
document does not authorise construction.

---

## 2. Survey-year to opportunity-year alignment

The alignment rule (from `docs/JMP_GSUR_year_alignment_decision_v1.md` and design memo
§3) maps EUROMOD system year to GSUR opportunity year:

| Survey-data year | EUROMOD system year | GSUR opportunity year |
|:---:|:---:|:---:|
| FR_2015 | 2015 | **y2014** |
| FR_2016 | 2016 | **y2015** |
| FR_2017 | 2017 | **y2016** |

Rationale: EUROMOD runs a tax-benefit system calibrated to the year prior to the survey
data year; job opportunities are drawn from that prior year's labour market. The
FR_2016-based MNL estimation (ruro_occ_M1_clean) uses a 2015 opportunity year; a y2016
GSURv2 lookup (already built) covers FR_2017 only.

Current MNL parquets in `Data/processed/fr/` (all `gsur_version: v1_fallback_opportunity_year_aligned`):

| Parquet stem | Survey year | Opportunity year used |
|:---|:---:|:---:|
| `fr_2015_RURO_mnl_v1gsurY2014__` | 2015 | v1 fallback y2014 |
| `fr_2016_RURO_mnl_v1gsurY2015__` | 2016 | v1 fallback y2015 |
| `fr_2017_RURO_mnl_v1gsurY2016__` | 2017 | v1 fallback y2016 |

All three survey years use v1 fallback rates sourced from `FR_gsur_ruro.parquet`, not
from `FR_gsur_ruro_v2_stageA.parquet`. The GSURv2 Stage A lookup has not been integrated
into any MNL parquet.

---

## 3. Audit conditions summary

| Condition | Subject | Status |
|:---|:---|:---:|
| A1 | lfst_r_lfu3rt unemployment-rate source (FR_gsur.xlsx) | **PASS** |
| A2 | lfst_r_lfsd2pop / lfst_r_lfp2acedu denominator files — y2014 and y2015 | **FAIL** |
| A3 | INSEE BDM 001688526 benchmark — y2014 and y2015 | **FAIL** |
| A4 | NUTS-2 vintage compatibility | **CONDITIONAL** |
| A5/K1 | Existing y2016 sidecar JSON (provenance-lock) | **FAIL** |
| A5/K2 | y2016 output column-name consistency | **FLAG** |
| A5/K3 | O7 crosswalk sign-off resolution | **FAIL** |
| A6 | Script parameterisation — C1 through C7 | **FAIL (all 7 unimplemented)** |

Conditions that fail or carry unresolved flags are blocking items (§23).

---

## 4. A1 — Unemployment-rate source (lfst_r_lfu3rt / FR_gsur.xlsx)

**Status: PASS**

`Data/external/FR_gsur.xlsx` is present (1,077,164 bytes). The workbook's `Structure`
sheet declares the time dimension as including all years from 2007 through at least 2019,
explicitly listing:

```
time: 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019 ...
```

The workbook covers **y2014 and y2015** within its existing time dimension. The
construction script uses `_find_year_col(df_raw, YEAR)` (line 165 of
`scripts/enhanced/enh_prepare_FR_gsur_v2.py`) to locate the column for any specified
year. No additional workbook retrieval is required for this input.

The workbook includes the following dimensions relevant to the Stage A build:
- `isced11`: TOTAL, ED0-2, ED3_4, ED5-8
- `sex`: T, M, F
- `age`: Y15-24, Y20-64, Y25-34, Y35-44, Y45-54, Y55-64, Y15-74, and others
- `geo`: all French NUTS-2 codes in NUTS2016 vintage (FR10, FRB0, FRD1, FRD2, FRE1,
  FRE2, FRF1, FRF2, FRF3, FRC1, FRC2, FRG0, FRH0, FRI1, FRI2, FRI3, FRJ1, FRJ2,
  FRK1, FRK2, FRL0, FRM0) plus NUTS-1 aggregates and DOM regions (FRY series)

The Y20-64 age band required by the Stage A broad-age specification (GSUR rebuild spec
v2.1 §6) is present for all years.

**Operational note for C2 (§14):** When the script is parameterised, C2 replaces the
implicit 2016 column selection with a `--opportunity-year`-driven lookup using
`_find_year_col`. No new workbook is needed; the current file already supports this.

---

## 5. A2 — Population-denominator files (lfst_r_lfsd2pop and lfst_r_lfp2acedu)

**Status: FAIL**

The construction script requires two Eurostat population-denominator TSV files per
opportunity year:

| File | Purpose | y2016 status | y2015 status | y2014 status |
|:---|:---|:---:|:---:|:---:|
| `lfst_r_lfsd2pop_FR_{year}.tsv` | D2 denominator: population by NUTS-2 × sex × age × education | PRESENT (357,080 bytes) | **MISSING** | **MISSING** |
| `lfst_r_lfp2acedu_FR_{year}.tsv` | D1 denominator: active population by NUTS-2 × sex × age × education | PRESENT (88,055 bytes) | **MISSING** | **MISSING** |

Full-EU download files present for 2016 only:
- `lfst_r_lfsd2pop_2016_full.csv` (7,214,941 bytes)
- `lfst_r_lfp2acedu_2016_full.csv` (1,732,181 bytes)

There are no multi-year full downloads and no 2014 or 2015 filtered TSV files.

**Operational response:** Four files must be retrieved from the Eurostat SDMX-CSV API
before construction can proceed for y2014 or y2015:
- `lfst_r_lfsd2pop_FR_2014.tsv` — D2 denominator, y2014
- `lfst_r_lfp2acedu_FR_2014.tsv` — D1 denominator, y2014
- `lfst_r_lfsd2pop_FR_2015.tsv` — D2 denominator, y2015
- `lfst_r_lfp2acedu_FR_2015.tsv` — D1 denominator, y2015

Retrieval uses the same Eurostat SDMX-CSV endpoint as the 2016 files (documented in
`Data/external/gsur_denominator_source.txt`), with `startPeriod` and `endPeriod`
changed to the target year. Companion `gsur_denominator_source.txt` entries for
y2014 and y2015 should be added to record provenance.

Note: `gsur_denominator_source.txt` documents a structural limitation — the
`lfst_r_lfp2acedu` table does not publish 10-year age bands at NUTS-2 level (only broad
bands Y15-74, Y25-64, Y_GE15). This limitation is unchanged for 2014 and 2015, as it
reflects the Eurostat publication structure, not a year-specific gap.

---

## 6. A3 — National benchmark availability (INSEE BDM 001688526)

**Status: FAIL**

The Stage A benchmark verification (O9 resolution in the GSUR rebuild spec) uses the
INSEE BDM series 001688526 (ILO unemployment rate, SA, Metropolitan France). The
2016 annual average (9.725%) is documented in `Data/external/gsur_benchmark_source.txt`
and stored in `Data/external/insee_001688526_2016.csv`.

| File | y2016 | y2015 | y2014 |
|:---|:---:|:---:|:---:|
| `insee_001688526_{year}.csv` | PRESENT (477 bytes) | **MISSING** | **MISSING** |

Benchmark percentages for y2014 and y2015 are unknown. Annual-average values must be
computed from quarterly data after retrieval.

**Operational response:** Retrieve `insee_001688526_2014.csv` and
`insee_001688526_2015.csv` from the INSEE BDM API (endpoint documented in
`Data/external/gsur_benchmark_source.txt`). Add companion `gsur_benchmark_source.txt`
entries for each year recording the API call, the four quarterly values, and the
computed annual average. The computed annual averages will become the `BENCHMARK_PCT`
values for y2014 and y2015 in the parameterised script (C4, §16).

---

## 7. A4 — NUTS-2 vintage compatibility

**Status: CONDITIONAL**

The `fr_drgn1_to_nuts2_crosswalk.csv` maps `drgn1` (1–8) to NUTS2016 codes (e.g.
FRB0, FRD2, FRE2, FRF1). All 22 rows carry `verified_against_eurostat=YES`. The
crosswalk uses the post-2013 NUTS-2016 vintage exclusively.

For the existing 2016 input files:
- `lfst_r_lfsd2pop_FR_2016.tsv` first-line inspection confirms codes FR10, FRB0 (NUTS2016
  vintage). NUTS-vintage-compatible: **YES**.
- `FR_gsur.xlsx` Structure sheet lists NUTS2016 codes (FRB0, FRD1, FRD2, FRE1, FRE2,
  FRF1, FRF2, FRF3, FRC1, FRC2, FRK1, FRK2, FRL0, FRM0) throughout its full time range
  including 2014 and 2015. Eurostat applies retroactive NUTS revision, so historical
  years in the workbook already use the current NUTS2016 vintage.

For 2014 and 2015 denominator TSV files (currently MISSING): Eurostat SDMX downloads
apply the currently valid NUTS revision to all time periods retroactively. When
`lfst_r_lfsd2pop_FR_2014.tsv` and `lfst_r_lfsd2pop_FR_2015.tsv` are retrieved from the
current Eurostat API, they are expected to carry NUTS2016 codes matching the crosswalk.

**Condition A4 is expected to pass** once the A2 files are retrieved; the NUTS2013-NUTS2016
conversion workbook (`Data/external/NUTS2013-NUTS2016.xlsx`) is available as a fallback
if any vintage mismatch is encountered. Confirmation is deferred until retrieval; this
cannot be verified for files that do not yet exist locally.

The L-vintage check (§10 and §13 of the rebuild spec) must be run on each new TSV file
as part of the construction workflow.

---

## 8. A5 — Existing y2016 provenance-lock (K1, K2, K3 overview)

**Status: FAIL (two of three sub-conditions fail; one flag)**

The design memo §15 defines three requirements that must be satisfied before the
existing y2016 GSURv2 lookup can be reused without a rebuild under the parameterised
script:

| Sub-condition | Description | Status |
|:---|:---|:---:|
| K1 | Sidecar JSON present and parses without error | **FAIL** |
| K2 | Column-name convention consistent with downstream spec | **FLAG** |
| K3 | O7 crosswalk sign-off resolved | **FAIL** |

K1 and K3 fail outright. K2 is flagged for explicit resolution before promotion. Details
in §9–§11 below.

**Consequence:** The existing `FR_gsur_ruro_v2_stageA.parquet` cannot be reused as the
final y2016 lookup for pooled estimation without resolution of K1 and K3 at a minimum.
It may be rebuilt under the parameterised script once C1–C7 are implemented; rebuilding
would subsume K1 and K3 by construction if the new script writes the sidecar (K1) and
the crosswalk sign-off is confirmed (K3).

---

## 9. K1 — Sidecar JSON parity

**Status: FAIL**

The design memo §14 requires a sidecar file
`Data/external/FR_gsur_ruro_v2_stageA__sidecar.json` recording build provenance,
schema metadata, and validation outcomes.

File inspection result: `FR_gsur_ruro_v2_stageA__sidecar.json` is **absent** from
`Data/external/`. The `RURO_GSUR_v2_stageA_implementation_report_v1.md` does not
mention a sidecar JSON, and the current construction script
(`enh_prepare_FR_gsur_v2.py`) does not write one.

**Operational response:** When the script is parameterised (C1–C7), C7 adds sidecar
writing as a required output step. Alternatively, the sidecar for the existing y2016
lookup could be written post-hoc if a rebuild under the new script is not performed.
Either path satisfies K1; the parameterised-rebuild path is preferred because it also
resolves K3 (§11).

---

## 10. K2 — Column-name consistency

**Status: FLAG**

The Stage A parquet (`FR_gsur_ruro_v2_stageA.parquet`) stores the GSURv2 rate in a
column named **`gsur`** (confirmed by parquet inspection: columns include `year`,
`drgn1`, `educ3`, `sex`, `gsur`, `weighting_source`, `gsur_age_band_used`,
`gsur_legacy_misaligned`, `denom_flag`, `n_components`, `gsur_unreliable`).

The harmonised P3a config (`config/multi_year/fr_p3a_stage_m1.yaml`,
`variables_excluded_from_deflation`, line 91) lists `gsur_v2` as a named column to
exclude from CPI deflation. The current provisional MNL parquets use column `gsur`
(v1 fallback); the config entry for `gsur_v2` is therefore a forward-looking
placeholder.

**Issue:** When the prep script (`enh_RURO_prep_mnl_basic.py`) is updated to merge from
`FR_gsur_ruro_v2_stageA.parquet` instead of `FR_gsur_ruro.parquet`, the resulting MNL
parquet column will be named `gsur` (inherited from the Stage A parquet). The
`variables_excluded_from_deflation` entry `gsur_v2` will not match, so the column would
not be excluded from deflation.

**Required resolution:** One of the following must be adopted and documented before
construction:
- (a) Rename the Stage A output column from `gsur` to `gsur_v2` in the parameterised
  script (consistent with the config YAML forward-reference).
- (b) Update `fr_p3a_stage_m1.yaml` to list `gsur` instead of `gsur_v2` in the
  exclusion list.
- (c) Confirm that the prep script renames the column on merge, and that this rename
  is stable across rebuilds.

The column-name convention must be recorded in the sidecar schema (K1) and the
construction authorisation memo before any rebuild.

---

## 11. K3 — Provenance-discrepancy resolution (O7 crosswalk sign-off)

**Status: FAIL**

The `RURO_GSUR_v2_stageA_implementation_report_v1.md` §O7 records:

> **O7 crosswalk sign-off: PENDING** — MNL merge blocked; no GSUR-to-MNL test
> conducted.

O7 requires that the crosswalk (`fr_drgn1_to_nuts2_crosswalk.csv`) produces correct
`drgn1`-level GSUR assignments when merged with the MNL job-choice data. This check was
deferred at the time of the Stage A build because the MNL parquets had not been
finalised.

**Consequence:** The y2016 GSURv2 lookup cannot be promoted to a final (non-provisional)
status until O7 is signed off. O7 verification requires merging the Stage A parquet
with the MNL draw-expanded parquet and confirming that `gsur` values are non-null and
plausible across all `drgn1` values.

**Operational response for K3:** O7 verification is a merge check, not a data rebuild.
It can be performed as a post-construction validation step on a per-year basis using
`Results/_canary_ruro_occ_M0.py` or an equivalent per-year check. K3 is resolved by
running O7 against the final parameterised output, not against the pre-existing y2016
parquet in isolation.

---

## 12. A6 — Script parameterisation readiness

**Status: FAIL (all 7 changes unimplemented)**

`scripts/enhanced/enh_prepare_FR_gsur_v2.py` (782 lines) has no `argparse`
`--opportunity-year` argument and contains seven year-specific hardcoded values
(identified by the design memo §9 as C1–C7). Each is detailed in §13–§19 below.

**Overall finding:** The year-invariant construction logic (NUTS crosswalk merge,
education mapping, D1/D2/D3 denominator hierarchy, age-band selection, drgn1=9 stub
handling, IDF parity check, benchmark validation) is clean and contains no additional
year references beyond C1–C7. The script is a natural candidate for parameterisation:
introducing one `--opportunity-year` argument drives all seven changes without touching
the core logic. No structural rewrite is needed.

The table below previews the status of each change:

| Code | Subject | Status |
|:---|:---|:---:|
| C1 | `YEAR = 2016` hardcoded constant | Unimplemented |
| C2 | Year-specific UR workbook column selection | Unimplemented |
| C3 | Year-specific D2 denominator path | Unimplemented |
| C4 | Year-specific D1 denominator path | Unimplemented |
| C5 | Year-specific benchmark input and value | Unimplemented |
| C6 | Year-tagged output path | Unimplemented |
| C7 | Year recorded in sidecar provenance | Unimplemented |

---

## 13. C1 — Opportunity-year argument

**Status: Unimplemented**

**Current state (line 44):**
```python
YEAR = 2016
```
Hardcoded at module level. No `argparse` parser exists in the script; the module has no
`if __name__ == "__main__":` block using `sys.argv`.

**Required change:** Add `argparse` with `--opportunity-year` (integer, required). Set
`YEAR` from `args.opportunity_year`. All subsequent uses of `YEAR` (lines 44, 165, 310,
334, 364) propagate automatically once the constant is replaced by the argument value.

**Impact scope:** C1 is the root change; C2–C7 are all derived from the same `YEAR`
value once it is an argument. No year-invariant logic is affected.

---

## 14. C2 — Year-specific unemployment-rate input

**Status: Unimplemented**

**Current state:** `load_gsur_workbook()` (line 147) loads `Data/external/FR_gsur.xlsx`
unconditionally. `_find_year_col(df_raw, YEAR)` (line 165) then identifies the year
column within the workbook.

**Assessment:** FR_gsur.xlsx is confirmed to be multi-year (A1, §4). Its Structure sheet
declares year columns from 2007 through at least 2019, including 2014 and 2015. No
workbook path change is needed. The `YEAR` constant (C1) already flows into
`_find_year_col`; once C1 is parameterised, C2 is satisfied without any further edit
to `load_gsur_workbook()`.

**Required change:** Only C1 (add `--opportunity-year` argument). `_find_year_col` will
receive the correct year automatically. No workbook-path logic change needed.

**Impact scope:** Zero additional lines beyond C1.

---

## 15. C3 — Year-specific D2 denominator path

**Status: Unimplemented**

**Current state (line 192 in `load_d2()`):**
```python
path = EXT / f"lfst_r_lfsd2pop_FR_2016.tsv"
```
Hardcoded filename with `2016` literal.

**Required change:** Replace with:
```python
path = EXT / f"lfst_r_lfsd2pop_FR_{YEAR}.tsv"
```
where `YEAR` is the module-level constant set by C1.

**Prerequisite:** `lfst_r_lfsd2pop_FR_2014.tsv` and `lfst_r_lfsd2pop_FR_2015.tsv` must
be present in `Data/external/` (A2, §5) before the parameterised script can be run for
y2014 or y2015. The code change itself is one-line.

---

## 16. C4 — Year-specific D1 denominator path

**Status: Unimplemented**

**Current state (line 209 in `load_d1()`):**
```python
path = EXT / f"lfst_r_lfp2acedu_FR_2016.tsv"
```
Hardcoded filename with `2016` literal.

**Required change:** Replace with:
```python
path = EXT / f"lfst_r_lfp2acedu_FR_{YEAR}.tsv"
```

**Prerequisite:** `lfst_r_lfp2acedu_FR_2014.tsv` and `lfst_r_lfp2acedu_FR_2015.tsv`
must be present (A2, §5). The code change itself is one-line.

---

## 17. C5 — Year-specific national-benchmark input and value

**Status: Unimplemented**

**Current state (line 45):**
```python
BENCHMARK_PCT = 9.725
```
Hardcoded 2016 annual-average unemployment rate (metropolitan France, 9.725%,
documented in `Data/external/gsur_benchmark_source.txt`).

**Required change:** Two sub-changes:
1. Read `Data/external/insee_001688526_{YEAR}.csv`, compute the mean of the four
   quarterly values, and assign to `BENCHMARK_PCT` at runtime. Alternatively, use a
   small lookup dict keyed by year.
2. The benchmark CSV path also implies a year reference that follows from C1.

**Prerequisite:** `insee_001688526_2014.csv` and `insee_001688526_2015.csv` must be
present (A3, §6). The annual-average values for y2014 and y2015 are unknown until
retrieval; they must be documented in `gsur_benchmark_source.txt` before construction.

---

## 18. C6 — Year-tagged output path

**Status: Unimplemented**

**Current state (line 42):**
```python
OUT = EXT / "FR_gsur_ruro_v2_stageA.parquet"
```
Hardcoded output filename with no year tag. Running for y2014 or y2015 without changing
`OUT` would overwrite the existing y2016 lookup.

**Required change:**
```python
OUT = EXT / f"FR_gsur_ruro_v2_stageA_y{YEAR}.parquet"
```
or an equivalent scheme that embeds `YEAR` in the filename.

**Naming-convention note:** The existing y2016 file uses the bare stem
`FR_gsur_ruro_v2_stageA.parquet`. For backward compatibility, the y2016 file may retain
its current name and only y2014 and y2015 outputs use the year-tagged stem. Alternatively,
all three outputs adopt the year-tagged scheme and the y2016 file is rebuilt with the new
name. The K2 column-name decision (§10) and the canary/validation scripts that reference
`FR_gsur_ruro_v2_stageA.parquet` by name would need concurrent updates for whichever
scheme is adopted. The choice must be recorded in the construction authorisation memo.

---

## 19. C7 — Provenance recording in sidecar

**Status: Unimplemented**

**Current state:** The script writes only the output parquet. No sidecar JSON is
produced. `FR_gsur_ruro_v2_stageA__sidecar.json` is absent (K1, §9).

**Required change:** At the end of `__main__`, write a sidecar JSON file alongside
`OUT` recording at minimum:
- `opportunity_year`
- `benchmark_pct`
- `d1_path`, `d2_path`, `gsur_workbook_path`
- `gsur_column_name` (resolves K2, §10)
- `nuts_vintage` (confirms A4, §7)
- `build_timestamp`
- `script_version` or commit hash
- Validation outcomes (IDF parity diff, benchmark diff, row count)
- `o7_status` placeholder to be filled at MNL merge check (K3, §11)

The sidecar filename should follow the output stem: for output
`FR_gsur_ruro_v2_stageA_y{YEAR}.parquet`, the sidecar is
`FR_gsur_ruro_v2_stageA_y{YEAR}__sidecar.json`.

---

## 20. Year-invariant assets: confirmed reusable

The following assets require no year-specific replacement and are confirmed present:

| Asset | Path | Status | Notes |
|:---|:---|:---:|:---|
| drgn1–NUTS2 crosswalk | `Data/external/fr_drgn1_to_nuts2_crosswalk.csv` | PRESENT | 22 rows, all `verified_against_eurostat=YES`; NUTS2016 codes |
| NUTS vintage workbook | `Data/external/NUTS2013-NUTS2016.xlsx` | PRESENT | L-vintage fallback if any mismatch found |
| FR unemployment workbook | `Data/external/FR_gsur.xlsx` | PRESENT (multi-year) | Structure sheet confirms 2014–2019 time range; NUTS2016 codes |
| CPI harmonisation file | `Data/external/cpi_hicp_fr_harmonisation.csv` | PRESENT | Three-year deflators φ(2015)=1.0031, φ(2016)=1.0, φ(2017)=0.9886 |

The crosswalk, NUTS workbook, and FR_gsur.xlsx are shared across all three opportunity
years and do not need per-year copies.

---

## 21. Active MNL parquets and provisional P3a status

**Active single-year baseline:** ruro_occ_M1_clean (FR_2016). This baseline is not
displaced by the GSURv2 extension audit and remains the active JMP single-year baseline.

**Provisional P3a harmonised parquet:**
- Path: `Data/processed/fr/pooled/fr_p3a_harmonised.parquet`
- Rows: 1,244,500 (V1–V9 PASS)
- Provisioning label: `provisional_v1_fallback_opportunity_year_aligned`
- GSUR source: `FR_gsur_ruro.parquet` (v1 fallback), applied via `enh_RURO_prep_mnl_basic.py`
- Opportunity-year alignment: correct (y2014 for FR_2015, y2015 for FR_2016, y2016 for FR_2017)
- GSURv2 integration: **none** — the Stage A lookup has not been merged into any parquet

The `fr_p3a_harmonised.parquet` is mechanically correct under the v1 fallback but
carries the provisional label explicitly because GSURv2 rates have not replaced the
fallback rates. It is not suitable for final pooled estimation until the GSURv2 rebuild
is complete and all three opportunity-year lookups are integrated.

**GSUR column provenance per survey year (meta JSON confirmed):**

| MNL parquet stem | `gsur_version` | `gsur_opportunity_year` | GSUR source file |
|:---|:---|:---:|:---|
| `fr_2015_RURO_mnl_v1gsurY2014__` | v1_fallback_opportunity_year_aligned | 2014 | `FR_gsur_ruro.parquet` |
| `fr_2016_RURO_mnl_v1gsurY2015__` | v1_fallback_opportunity_year_aligned | 2015 | `FR_gsur_ruro.parquet` |
| `fr_2017_RURO_mnl_v1gsurY2016__` | v1_fallback_opportunity_year_aligned | 2016 | `FR_gsur_ruro.parquet` |

Note: `fr_2017` uses the v1 fallback for y2016 even though a GSURv2 Stage A lookup
exists for y2016 (`FR_gsur_ruro_v2_stageA.parquet`). The Stage A lookup has not been
integrated into any prep-script run. All three survey years must be rebuilt with the
corresponding GSURv2 lookups after construction is complete.

---

## 22. Open decisions carried forward

The following open decisions from earlier GSURv2 work remain unresolved and affect
the construction:

| Decision | Source | Status | Impact |
|:---|:---|:---:|:---|
| O7 — crosswalk sign-off | GSUR Stage A implementation report | PENDING | K3 fail; y2016 cannot be promoted; must be run for each new year at construction time |
| K2 — GSURv2 column name convention | This audit (§10) | UNRESOLVED | Column naming (`gsur` vs `gsur_v2`) must be decided before any parquet rebuild |
| C6 — output naming scheme | This audit (§18) | UNRESOLVED | Year-tagged vs. bare stem; backward-compat with existing y2016 file |
| A4 — NUTS vintage for 2014/2015 extracts | This audit (§7) | CONDITIONAL | Expected PASS; must be confirmed at retrieval |
| Benchmark values for y2014, y2015 | This audit (§6) | UNKNOWN | Annual-average unemployment rates must be sourced and documented before C5 can be implemented |

These decisions do not require data downloads or code changes within this audit scope.
They must be resolved in the construction authorisation memo before the parameterised
script is implemented.

---

## 23. Blocking issues summary

All items below must be resolved before GSURv2 construction for y2014 or y2015 can
proceed. Items are grouped by resolution category.

### 23a. External data retrieval (A2, A3)

Four Eurostat denominator TSV files are missing:

1. `Data/external/lfst_r_lfsd2pop_FR_2014.tsv` — D2 denominator, y2014
2. `Data/external/lfst_r_lfp2acedu_FR_2014.tsv` — D1 denominator, y2014
3. `Data/external/lfst_r_lfsd2pop_FR_2015.tsv` — D2 denominator, y2015
4. `Data/external/lfst_r_lfp2acedu_FR_2015.tsv` — D1 denominator, y2015

Two INSEE benchmark files are missing:

5. `Data/external/insee_001688526_2014.csv` — national UR benchmark, y2014
6. `Data/external/insee_001688526_2015.csv` — national UR benchmark, y2015

Accompanying provenance entries must be added to `Data/external/gsur_denominator_source.txt`
and `Data/external/gsur_benchmark_source.txt`.

### 23b. Script code changes (A6: C1–C7)

Seven hardcoded year-specific values in `scripts/enhanced/enh_prepare_FR_gsur_v2.py`
must be replaced by argument-driven logic:

7. **C1** — `YEAR = 2016` (line 44) → `--opportunity-year` argument
8. **C2** — `_find_year_col(df_raw, YEAR)` (line 165) → driven by C1; no additional change
9. **C3** — `lfst_r_lfsd2pop_FR_2016.tsv` (line 192 in `load_d2()`) → f-string with `YEAR`
10. **C4** — `lfst_r_lfp2acedu_FR_2016.tsv` (line 209 in `load_d1()`) → f-string with `YEAR`
11. **C5** — `BENCHMARK_PCT = 9.725` (line 45) → read from year-specific INSEE CSV
12. **C6** — `FR_gsur_ruro_v2_stageA.parquet` (line 42 in `OUT` assignment) → year-tagged filename
13. **C7** — sidecar JSON writing (absent) → add sidecar output block

Note: C2 requires no additional edit beyond C1 (§14); total distinct edit points are
6 (lines 44–45 for C1/C5, line 42 for C6, line 192 for C3, line 209 for C4, plus new
sidecar block for C7).

### 23c. Provenance-lock items for y2016 (A5)

14. **K1** — Sidecar JSON absent: `FR_gsur_ruro_v2_stageA__sidecar.json` must be created
    (resolved by C7 if y2016 is rebuilt under the parameterised script)
15. **K3** — O7 crosswalk sign-off pending: MNL-merge check must be run for y2016 output

### 23d. Naming-convention decisions (K2)

16. **K2** — GSURv2 column name (`gsur` vs `gsur_v2`) must be decided and recorded in
    the construction authorisation memo

---

## 24. Final verdict

**NOT READY — CODE CHANGES REQUIRED**

The primary blocking gate is the absence of the `--opportunity-year` parameterisation
(A6 fail). The construction script `enh_prepare_FR_gsur_v2.py` cannot be run for any
year other than 2016 without the C1–C7 changes. Implementing C1 (adding
`--opportunity-year`) resolves C2 automatically and requires only minor targeted edits
for C3, C4, C5, C6, and C7 (fewer than 30 net lines of change across all seven items).
The year-invariant construction logic requires no modification.

Concurrent prerequisites that must be resolved alongside the code changes:

- **External retrieval (A2, A3):** Four Eurostat TSV files and two INSEE benchmark CSVs
  must be downloaded before the parameterised script can be run for y2014 and y2015.
  These files are absent; retrieval requires external API access.
- **Provenance-lock (A5/K1, K3):** The sidecar JSON for y2016 is absent (K1);
  the crosswalk sign-off (O7/K3) is pending. Both are resolved by rebuilding y2016 under
  the parameterised script after C1–C7 are implemented.
- **Naming convention (K2):** The `gsur` vs `gsur_v2` column-name question must be
  settled before any parquet rebuild.

**What passes:**
- A1 (FR_gsur.xlsx multi-year confirmed): PASS
- Year-invariant assets (crosswalk, NUTS workbook, CPI file): all present
- P3a provisional construction V1–V9: PASS
- Opportunity-year alignment rule: correctly documented and applied

**Immediate next step:** Issue a GSURv2 construction authorisation memo that (a) resolves
K2 and C6 naming decisions, (b) authorises retrieval of the six missing external files,
and (c) authorises implementation of C1–C7 in `enh_prepare_FR_gsur_v2.py`. The
construction itself is sequenced after the authorisation memo is in place. This audit
does not authorise construction.

---

*Audit generated by Claude Code Sonnet, 2026-05-20. No scripts modified, no data
modified, no external APIs called, no models estimated.*